#!/usr/bin/env python3
"""Prometheus exporter for the dgx-llm observability ledger.

Tails ~/dgx-llm-obs.jsonl (written by dgx_proxy.py) and exposes, on :9210/metrics:
  dgx_llm_requests_total{project,user,model}        — DGX-bound requests
  dgx_llm_request_duration_seconds_sum/count{...}   — round-trip latency (anthropic-lane excl.)
  dgx_llm_request_errors_total{project,user}        — DGX replies with status >= 400
  dgx_llm_anthropic_passthrough_total               — requests routed to real Anthropic
  dgx_llm_last_request_timestamp_seconds            — freshness gauge

State is rebuilt from the full file on start (ledger is small; a few MB at most).
Counters are monotonic per process lifetime; exporter restart resets them, which
is acceptable for rates/ratios (label	vm: a restart shows as a dip, not data loss).
"""
import json
import os
import time
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

LEDGER = os.environ.get("DGX_OBS_LEDGER", os.path.expanduser("~/dgx-llm-obs.jsonl"))
PORT = int(os.environ.get("DGX_LEDGER_EXPORTER_PORT", "9210"))

state_lock = __import__("threading").Lock()
req_totals = defaultdict(int)          # (project,user,model,acct,dev) -> n
est_prompt = defaultdict(float)        # (project,user,acct) -> est. prompt tokens
dur_sum = defaultdict(float)           # (project,user) -> seconds
dur_count = defaultdict(int)
errors = defaultdict(int)              # (project,user) -> n
tok_in = defaultdict(int)              # (project,user,acct) -> TRUE input tokens (SSE usage)
tok_out = defaultdict(int)             # (project,user,acct) -> TRUE output tokens
anth_req = defaultdict(int)            # (project,user,model,acct) -> n (passthrough)
anth_in = defaultdict(int)             # passthrough TRUE input tokens
anth_out = defaultdict(int)            # passthrough TRUE output tokens
anth_ds = defaultdict(float)           # passthrough latency sum
anth_dc = defaultdict(int)             # passthrough latency count
anth_rqs = defaultdict(int)            # passthrough usage events (= completed requests)
passthrough = 0
last_ts = 0.0


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def _account_device(meta_user_id):
    """Split CC's metadata.user_id (stringified JSON {device_id, account_uuid, session_id})
    into short stable labels; falls back to (raw-if-short, 'unknown')."""
    acct = dev = "unknown"
    if meta_user_id:
        if isinstance(meta_user_id, str):
            try:
                m = json.loads(meta_user_id)
                if isinstance(m, dict):
                    acct = (m.get("account_uuid") or "unknown")[:8]
                    dev = (m.get("device_id") or "unknown")[:8]
            except ValueError:
                acct, dev = (meta_user_id[:8], "unknown") if len(meta_user_id) > 8 else (meta_user_id, "unknown")
        elif isinstance(meta_user_id, dict):
            acct = (meta_user_id.get("account_uuid") or "unknown")[:8]
            dev = (meta_user_id.get("device_id") or "unknown")[:8]
    return acct, dev


def rebuild() -> None:
    global passthrough, last_ts
    rt, ds, dc, er, et, tin, tout = (defaultdict(int), defaultdict(float), defaultdict(int),
                                     defaultdict(int), defaultdict(float),
                                     defaultdict(int), defaultdict(int))
    ara, ain, aout, ads, adc, arq = (defaultdict(int), defaultdict(int), defaultdict(int),
                                     defaultdict(float), defaultdict(int), defaultdict(int))
    pt = 0
    last = 0.0
    try:
        with open(LEDGER) as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                t = ev.get("t")
                if t:
                    try:
                        import datetime
                        ts = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S").timestamp()
                        last = max(last, ts)
                    except ValueError:
                        pass
                if ev.get("event") == "dgx_usage":
                    key_u = (ev.get("project") or "unknown", ev.get("user") or "unknown",
                             ev.get("account") or "unknown")
                    tin[key_u] += int(ev.get("in_tok") or 0)
                    tout[key_u] += int(ev.get("out_tok") or 0)
                elif ev.get("event") == "anth_request":
                    key_a = (ev.get("project") or "unknown", ev.get("user") or "unknown",
                             ev.get("model_req") or "?", ev.get("account") or "unknown")
                    ara[key_a] += 1
                elif ev.get("event") == "anth_usage":
                    key_a = (ev.get("project") or "unknown", ev.get("user") or "unknown",
                             ev.get("model") or "?", ev.get("account") or "unknown")
                    ain[key_a] += int(ev.get("in_tok") or 0)
                    aout[key_a] += int(ev.get("out_tok") or 0)
                    d = ev.get("duration_s")
                    if isinstance(d, (int, float)):
                        ads[key_a] += d
                        adc[key_a] += 1
                    arq[key_a] += 1
                elif ev.get("event") == "dgx_request":
                    acct, dev = _account_device(ev.get("meta_user_id"))
                    key = (ev.get("project") or "unknown", ev.get("user") or "unknown", ev.get("model_req") or "?", acct, dev)
                    rt[key] += 1
                    nbytes = ev.get("req_bytes")
                    if isinstance(nbytes, (int, float)) and nbytes > 0:
                        # rough prompt-token estimate: ~4 chars per token for mixed code/prose
                        et[(key[0], key[1], acct)] += nbytes / 4.0
                elif ev.get("event") == "dgx_reply":
                    key = (ev.get("project") or "unknown", ev.get("user") or "unknown")
                    d = ev.get("duration_s")
                    if isinstance(d, (int, float)):
                        ds[key] += d
                        dc[key] += 1
                    if ev.get("status", 0) >= 400:
                        er[key] += 1
                elif ev.get("event") == "anthropic_reply" and ev.get("status") == 200:
                    pt += 1
    except FileNotFoundError:
        pass
    with state_lock:
        req_totals.clear(); req_totals.update(rt)
        dur_sum.clear(); dur_sum.update(ds)
        dur_count.clear(); dur_count.update(dc)
        errors.clear(); errors.update(er)
        est_prompt.clear(); est_prompt.update(et)
        tok_in.clear(); tok_in.update(tin)
        tok_out.clear(); tok_out.update(tout)
        anth_req.clear(); anth_req.update(ara)
        anth_in.clear(); anth_in.update(ain)
        anth_out.clear(); anth_out.update(aout)
        anth_ds.clear(); anth_ds.update(ads)
        anth_dc.clear(); anth_dc.update(adc)
        anth_rqs.clear(); anth_rqs.update(arq)
        passthrough = pt
        globals()["last_ts"] = last


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path, _, qs = self.path.partition("?")
        if path != "/metrics":
            self.send_response(404); self.end_headers(); return
        params = parse_qs(qs)
        if params.get("rebuild"):  # ?rebuild=1 forces a re-scan
            rebuild()
        with state_lock:
            lines = [
                "# HELP dgx_llm_requests_total DGX-bound requests",
                "# TYPE dgx_llm_requests_total counter",
            ]
            for (proj, user, model, acct, dev), n in sorted(req_totals.items()):
                lines.append(f'dgx_llm_requests_total{{project="{esc(proj)}",user="{esc(user)}",model="{esc(model)}",account="{esc(acct)}",device="{esc(dev)}"}} {n}')
            lines += ["# HELP dgx_llm_est_prompt_tokens_total estimated prompt tokens (bytes/4 heuristic)",
                      "# TYPE dgx_llm_est_prompt_tokens_total counter"]
            for (proj, user, acct), v in sorted(est_prompt.items()):
                lines.append(f'dgx_llm_est_prompt_tokens_total{{project="{esc(proj)}",user="{esc(user)}",account="{esc(acct)}"}} {v:.0f}')
            lines += ["# HELP dgx_llm_tokens_input_total true input tokens (SSE usage, vLLM-reported)",
                      "# TYPE dgx_llm_tokens_input_total counter",
                      "# HELP dgx_llm_tokens_output_total true output tokens (SSE usage, vLLM-reported)",
                      "# TYPE dgx_llm_tokens_output_total counter"]
            for (proj, user, acct), v in sorted(tok_in.items()):
                lines.append(f'dgx_llm_tokens_input_total{{project="{esc(proj)}",user="{esc(user)}",account="{esc(acct)}"}} {v}')
            for (proj, user, acct), v in sorted(tok_out.items()):
                lines.append(f'dgx_llm_tokens_output_total{{project="{esc(proj)}",user="{esc(user)}",account="{esc(acct)}"}} {v}')
            lines += ["# HELP dgx_llm_anthropic_requests_total passthrough (Opus/Haiku) requests",
                      "# TYPE dgx_llm_anthropic_requests_total counter"]
            for (proj, user, model, acct), n in sorted(anth_req.items()):
                lines.append(f'dgx_llm_anthropic_requests_total{{project="{esc(proj)}",user="{esc(user)}",model="{esc(model)}",account="{esc(acct)}"}} {n}')
            lines += ["# HELP dgx_llm_anthropic_tokens_input_total passthrough true input tokens",
                      "# TYPE dgx_llm_anthropic_tokens_input_total counter",
                      "# HELP dgx_llm_anthropic_tokens_output_total passthrough true output tokens",
                      "# TYPE dgx_llm_anthropic_tokens_output_total counter",
                      "# HELP dgx_llm_anthropic_request_duration_seconds_sum passthrough latency",
                      "# TYPE dgx_llm_anthropic_request_duration_seconds_sum counter",
                      "# TYPE dgx_llm_anthropic_request_duration_seconds_count counter"]
            for (proj, user, model, acct), v in sorted(anth_in.items()):
                lbl = f'project="{esc(proj)}",user="{esc(user)}",model="{esc(model)}",account="{esc(acct)}"'
                lines.append(f'dgx_llm_anthropic_tokens_input_total{{{lbl}}} {v}')
                lines.append(f'dgx_llm_anthropic_tokens_output_total{{{lbl}}} {anth_out[(proj, user, model, acct)]}')
                s = anth_ds[(proj, user, model, acct)]
                c = anth_dc[(proj, user, model, acct)]
                lines.append(f'dgx_llm_anthropic_request_duration_seconds_sum{{{lbl}}} {s:.3f}')
                lines.append(f'dgx_llm_anthropic_request_duration_seconds_count{{{lbl}}} {c}')
            lines += ["# HELP dgx_llm_request_duration_seconds_sum cumulative request seconds",
                      "# TYPE dgx_llm_request_duration_seconds_sum counter",
                      "# TYPE dgx_llm_request_duration_seconds_count counter"]
            for (proj, user), s in sorted(dur_sum.items()):
                lbl = f'project="{esc(proj)}",user="{esc(user)}"'
                lines.append(f'dgx_llm_request_duration_seconds_sum{{{lbl}}} {s:.3f}')
                lines.append(f'dgx_llm_request_duration_seconds_count{{{lbl}}} {dur_count[(proj, user)]}')
            lines += ["# HELP dgx_llm_request_errors_total DGX replies with status>=400",
                      "# TYPE dgx_llm_request_errors_total counter"]
            for (proj, user), n in sorted(errors.items()):
                lines.append(f'dgx_llm_request_errors_total{{project="{esc(proj)}",user="{esc(user)}"}} {n}')
            lines += ["# HELP dgx_llm_anthropic_passthrough_total requests passed to real Anthropic",
                      "# TYPE dgx_llm_anthropic_passthrough_total counter",
                      f"dgx_llm_anthropic_passthrough_total {passthrough}",
                      "# HELP dgx_llm_last_request_timestamp_seconds newest ledger event (unix)",
                      "# TYPE dgx_llm_last_request_timestamp_seconds gauge",
                      f"dgx_llm_last_request_timestamp_seconds {last_ts:.0f}"]
        body = ("\n".join(lines) + "\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_a):  # silence request spam
        pass


if __name__ == "__main__":
    rebuild()
    print(f"dgx-ledger-exporter: serving :{PORT}, tailing {LEDGER}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
