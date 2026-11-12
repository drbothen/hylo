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
FAKESTOP_LOG = os.environ.get("DGX_FAKESTOP_LOG", os.path.expanduser("~/.cache/dgx-llm/auto-continue.log"))
SESSION_LIMIT = int(os.environ.get("DGX_SESSION_LIMIT", "50"))  # most-recent sessions tracked
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
# Prompt-cache tokens (backlog item 4, 2026-11-12). Present only on anth_usage events written
# by dgx_proxy.py after the cache-capture change; older events lack the fields, so
# anth_cache_cov counts usage events that DID carry them (coverage, for honest panels).
anth_cr = defaultdict(int)             # passthrough cache-read tokens
anth_cw5 = defaultdict(int)            # passthrough cache-write tokens, 5-minute TTL
anth_cw1 = defaultdict(int)            # passthrough cache-write tokens, 1-hour TTL
anth_cache_cov = defaultdict(int)      # usage events carrying cache fields
# DGX-lane prefix-cache hits (2026-11-12, needs vLLM --enable-prompt-tokens-details). in_tok on
# dgx_usage is always the whole prompt; cache_read_tok is present only once the flag is on.
# dgx_in_cap = prompt tokens of the requests that carried cache_read_tok, so
# hit ratio = dgx_cr / dgx_in_cap is not diluted by older, uncaptured requests.
dgx_cr = defaultdict(int)              # (project,user,acct) -> DGX cache-read (prefix-hit) tokens
dgx_in_cap = defaultdict(int)          # (project,user,acct) -> prompt tokens of captured requests
sess_meta = {}                         # session_id -> {project,user,last}  (recent N)
sess_stats = {}                        # session_id -> {reqs,in,out,errors}
fakestop = {}                          # tallies from auto-continue.log
passthrough = 0
last_ts = 0.0              # newest ledger event of ANY type (pipeline freshness)
last_dgx_ts = 0.0          # newest DGX-lane request (dgx_request)
last_anth_ts = 0.0         # newest Anthropic-passthrough request (anth_request)
processed_size = -1        # ledger size covered by the in-memory state (-1 = none yet)


def _current_size() -> int:
    try:
        return os.stat(LEDGER).st_size
    except OSError:
        return 0


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
    global passthrough, last_ts, sess_meta, sess_stats
    dcr, dcap = defaultdict(int), defaultdict(int)
    rt, ds, dc, er, et, tin, tout = (defaultdict(int), defaultdict(float), defaultdict(int),
                                     defaultdict(int), defaultdict(float),
                                     defaultdict(int), defaultdict(int))
    ara, ain, aout, ads, adc, arq = (defaultdict(int), defaultdict(int), defaultdict(int),
                                     defaultdict(float), defaultdict(int), defaultdict(int))
    acr, acw5, acw1, acov = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
    # session funnel: most recent SESSION_LIMIT sessions with any event
    smeta = {}     # session_id -> {"project":..., "user":..., "last": epoch}
    sstats = defaultdict(lambda: {"reqs": 0, "in": 0, "out": 0, "errors": 0})
    # fake-stop log tallies
    fs = {"caught": 0, "colon": 0, "heuristic": 0, "opus": 0, "allowed": 0,
          "p_done_latest": None}
    sess_proj = {}  # session uuid -> project (from ledger events)
    pt = 0
    last = 0.0
    last_dgx = 0.0
    last_anth = 0.0
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
                        # Lane-specific: "the DGX is idle" must not be masked by
                        # Opus/Haiku passthrough traffic (which also lands here).
                        if ev.get("event") == "dgx_request":
                            last_dgx = max(last_dgx, ts)
                        elif ev.get("event") == "anth_request":
                            last_anth = max(last_anth, ts)
                    except ValueError:
                        pass
                s_id = ev.get("session")
                if s_id and ev.get("project"):
                    sess_proj[s_id] = (ev["project"], ev.get("user") or "unknown")
                if s_id and ev.get("event") in ("dgx_request", "dgx_reply", "dgx_usage"):
                    sm = smeta.setdefault(s_id, {"project": ev.get("project") or "unknown",
                                                 "user": ev.get("user") or "unknown",
                                                 "last": 0.0})
                    if t:
                        try:
                            import datetime
                            sm["last"] = max(sm["last"], datetime.datetime.strptime(
                                t, "%Y-%m-%dT%H:%M:%S").timestamp())
                        except ValueError:
                            pass
                if ev.get("event") == "dgx_usage":
                    key_u = (ev.get("project") or "unknown", ev.get("user") or "unknown",
                             ev.get("account") or "unknown")
                    tin[key_u] += int(ev.get("in_tok") or 0)
                    if "cache_read_tok" in ev:
                        dcr[key_u] += int(ev.get("cache_read_tok") or 0)
                        dcap[key_u] += int(ev.get("in_tok") or 0)
                    tout[key_u] += int(ev.get("out_tok") or 0)
                    if s_id and s_id in smeta:
                        sstats[s_id]["in"] += int(ev.get("in_tok") or 0)
                        sstats[s_id]["out"] += int(ev.get("out_tok") or 0)
                elif ev.get("event") == "anth_request":
                    key_a = (ev.get("project") or "unknown", ev.get("user") or "unknown",
                             ev.get("model_req") or "?", ev.get("account") or "unknown")
                    ara[key_a] += 1
                elif ev.get("event") == "anth_usage":
                    key_a = (ev.get("project") or "unknown", ev.get("user") or "unknown",
                             ev.get("model") or "?", ev.get("account") or "unknown")
                    ain[key_a] += int(ev.get("in_tok") or 0)
                    aout[key_a] += int(ev.get("out_tok") or 0)
                    if "cache_read_tok" in ev or "cache_write_tok" in ev:
                        acov[key_a] += 1
                        acr[key_a] += int(ev.get("cache_read_tok") or 0)
                        # 5m is DERIVED (write total - 1h), never read from the event: proxy
                        # builds deployed 13:31:52-fix on 2026-11-12 wrote 5m = total on
                        # streamed replies (double count). Deriving keeps old events correct.
                        cw = int(ev.get("cache_write_tok") or 0)
                        c1 = min(int(ev.get("cache_write_1h_tok") or 0), cw)
                        acw1[key_a] += c1
                        acw5[key_a] += cw - c1
                    d = ev.get("duration_s")
                    if isinstance(d, (int, float)):
                        ads[key_a] += d
                        adc[key_a] += 1
                    arq[key_a] += 1
                elif ev.get("event") == "dgx_request":
                    acct, dev = _account_device(ev.get("meta_user_id"))
                    key = (ev.get("project") or "unknown", ev.get("user") or "unknown", ev.get("model_req") or "?", acct, dev)
                    rt[key] += 1
                    if s_id and s_id in smeta:
                        sstats[s_id]["reqs"] += 1
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
                    if s_id and s_id in smeta and ev.get("status", 0) >= 400:
                        sstats[s_id]["errors"] += 1
                # "anth_reply" since 2026-11-10 (proxy rename); "anthropic_reply" before. Counting
                # only the legacy name froze this counter at 257 (found in the Grafana audit).
                elif ev.get("event") in ("anth_reply", "anthropic_reply") and ev.get("status") == 200:
                    pt += 1
                elif ev.get("event") == "dgx_upstream_error":
                    # DGX unreachable (connection refused / no route): count as an error
                    er[(ev.get("project") or "unknown", ev.get("user") or "unknown")] += 1
    except FileNotFoundError:
        pass
    # ------- fake-stop hook log -------
    try:
        with open(FAKESTOP_LOG) as f:
            for line in f:
                if " [kev-continue]" in line:
                    fs["caught"] += 1
                elif " [kev-allow]" in line:
                    fs["allowed"] += 1
                elif " [kev+opus-continue]" in line:
                    fs["opus"] += 1
                elif " [colon-fake]" in line:
                    fs["colon"] += 1
                elif " [heuristic-continue]" in line:
                    fs["heuristic"] += 1
                if "p_done=" in line:
                    try:
                        import re as _re
                        m = _re.search(r"p_done=([0-9.]+)", line)
                        if m:
                            fs["p_done_latest"] = float(m.group(1))
                    except Exception:
                        pass
    except FileNotFoundError:
        pass
    # trim sessions to most recent N
    recent = dict(sorted(smeta.items(), key=lambda kv: kv[1]["last"], reverse=True)[:SESSION_LIMIT])
    with state_lock:
        req_totals.clear(); req_totals.update(rt)
        dur_sum.clear(); dur_sum.update(ds)
        dur_count.clear(); dur_count.update(dc)
        errors.clear(); errors.update(er)
        est_prompt.clear(); est_prompt.update(et)
        tok_in.clear(); tok_in.update(tin)
        tok_out.clear(); tok_out.update(tout)
        dgx_cr.clear(); dgx_cr.update(dcr)
        dgx_in_cap.clear(); dgx_in_cap.update(dcap)
        anth_req.clear(); anth_req.update(ara)
        anth_in.clear(); anth_in.update(ain)
        anth_out.clear(); anth_out.update(aout)
        anth_ds.clear(); anth_ds.update(ads)
        anth_dc.clear(); anth_dc.update(adc)
        anth_rqs.clear(); anth_rqs.update(arq)
        anth_cr.clear(); anth_cr.update(acr)
        anth_cw5.clear(); anth_cw5.update(acw5)
        anth_cw1.clear(); anth_cw1.update(acw1)
        anth_cache_cov.clear(); anth_cache_cov.update(acov)
        sess_meta.clear(); sess_meta.update(recent)
        for s_id in recent:
            sess_stats[s_id] = dict(sstats.get(s_id, {"reqs": 0, "in": 0, "out": 0, "errors": 0}))
        fakestop.clear(); fakestop.update(fs)
        passthrough = pt
        globals()["last_ts"] = last
        globals()["last_dgx_ts"] = last_dgx
        globals()["last_anth_ts"] = last_anth


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path, _, qs = self.path.partition("?")
        if path != "/metrics":
            self.send_response(404); self.end_headers(); return
        params = parse_qs(qs)
        # Rescan when the ledger grew since the last scrape. Without this the gauges
        # (incl. dgx_llm_last_request_timestamp_seconds -> the statusline's "idle" meter)
        # froze at process-boot state forever, because only an explicit ?rebuild=1
        # triggered rebuild(). Cost: one stat() per scrape; the docstring already promises
        # the ledger stays small (a few MB), so a full rescan on change is plenty cheap.
        global processed_size
        try:
            grew = os.stat(LEDGER).st_size != processed_size
        except OSError:
            grew = False
        if params.get("rebuild") or grew:
            rebuild()
            processed_size = _current_size()
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
            lines += ["# HELP dgx_llm_tokens_cache_read_total DGX-lane prompt tokens served from vLLM's prefix cache (needs --enable-prompt-tokens-details)",
                      "# TYPE dgx_llm_tokens_cache_read_total counter",
                      "# HELP dgx_llm_tokens_input_captured_total prompt tokens of DGX requests that reported cache_read_tok (hit-ratio denominator)",
                      "# TYPE dgx_llm_tokens_input_captured_total counter"]
            for (proj, user, acct) in sorted(tok_in):
                k = (proj, user, acct)
                lbl = f'project="{esc(proj)}",user="{esc(user)}",account="{esc(acct)}"'
                lines.append(f'dgx_llm_tokens_cache_read_total{{{lbl}}} {dgx_cr[k]}')
                lines.append(f'dgx_llm_tokens_input_captured_total{{{lbl}}} {dgx_in_cap[k]}')
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
            lines += ["# HELP dgx_llm_anthropic_tokens_cache_read_total passthrough prompt-cache read tokens (usage.cache_read_input_tokens)",
                      "# TYPE dgx_llm_anthropic_tokens_cache_read_total counter",
                      "# HELP dgx_llm_anthropic_tokens_cache_write_total passthrough prompt-cache write tokens by TTL (usage.cache_creation)",
                      "# TYPE dgx_llm_anthropic_tokens_cache_write_total counter",
                      "# HELP dgx_llm_anthropic_usage_cache_captured_total passthrough usage events that carried cache fields (capture coverage)",
                      "# TYPE dgx_llm_anthropic_usage_cache_captured_total counter"]
            for (proj, user, model, acct) in sorted(anth_in):
                k = (proj, user, model, acct)
                lbl = f'project="{esc(proj)}",user="{esc(user)}",model="{esc(model)}",account="{esc(acct)}"'
                lines.append(f'dgx_llm_anthropic_tokens_cache_read_total{{{lbl}}} {anth_cr[k]}')
                lines.append(f'dgx_llm_anthropic_tokens_cache_write_total{{{lbl},ttl="5m"}} {anth_cw5[k]}')
                lines.append(f'dgx_llm_anthropic_tokens_cache_write_total{{{lbl},ttl="1h"}} {anth_cw1[k]}')
                lines.append(f'dgx_llm_anthropic_usage_cache_captured_total{{{lbl}}} {anth_cache_cov[k]}')
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
                      "# HELP dgx_llm_last_request_timestamp_seconds newest ledger event of any type (unix; pipeline freshness)",
                      "# TYPE dgx_llm_last_request_timestamp_seconds gauge",
                      f"dgx_llm_last_request_timestamp_seconds {last_ts:.0f}"]
            # Lane-specific recency. Emitted only once seen, so "never" is absent,
            # not a misleading 1970 timestamp.
            if last_dgx_ts > 0:
                lines += ["# HELP dgx_llm_last_dgx_request_timestamp_seconds newest DGX-lane request (unix)",
                          "# TYPE dgx_llm_last_dgx_request_timestamp_seconds gauge",
                          f"dgx_llm_last_dgx_request_timestamp_seconds {last_dgx_ts:.0f}"]
            if last_anth_ts > 0:
                lines += ["# HELP dgx_llm_last_anthropic_request_timestamp_seconds newest Anthropic-passthrough request (unix)",
                          "# TYPE dgx_llm_last_anthropic_request_timestamp_seconds gauge",
                          f"dgx_llm_last_anthropic_request_timestamp_seconds {last_anth_ts:.0f}"]
            # session funnel (most recent N sessions)
            lines += ["# HELP dgx_llm_session_requests requests belonging to a session (recent)",
                      "# TYPE dgx_llm_session_requests gauge",
                      "# HELP dgx_llm_session_tokens tokens belonging to a session (recent)",
                      "# TYPE dgx_llm_session_tokens gauge"]
            for s_id, meta in sorted(sess_meta.items(), key=lambda kv: -kv[1]["last"]):
                st = sess_stats.get(s_id, {})
                lbl = (f'session="{esc(s_id[:8])}",'
                       f'project="{esc(meta["project"])}",user="{esc(meta["user"])}"')
                lines.append(f'dgx_llm_session_requests{{{lbl}}} {st.get("reqs", 0)}')
                lines.append(f'dgx_llm_session_tokens_in{{{lbl}}} {st.get("in", 0)}')
                lines.append(f'dgx_llm_session_tokens_out{{{lbl}}} {st.get("out", 0)}')
                lines.append(f'dgx_llm_session_errors{{{lbl}}} {st.get("errors", 0)}')
            # fake-stop oracle (auto-continue.log)
            lines += ["# HELP dgx_llm_fakestop_events fake-stop oracle hook tallies",
                      "# TYPE dgx_llm_fakestop_events counter",
                      f'dgx_llm_fakestop_events{{kind="kev_caught"}} {fakestop.get("caught", 0)}',
                      f'dgx_llm_fakestop_events{{kind="colon_caught"}} {fakestop.get("colon", 0)}',
                      f'dgx_llm_fakestop_events{{kind="heuristic"}} {fakestop.get("heuristic", 0)}',
                      f'dgx_llm_fakestop_events{{kind="kev_plus_opus"}} {fakestop.get("opus", 0)}',
                      f'dgx_llm_fakestop_events{{kind="allowed"}} {fakestop.get("allowed", 0)}']
            if fakestop.get("p_done_latest") is not None:
                lines.append("# TYPE dgx_llm_fakestop_p_done_latest gauge")
                lines.append(f'dgx_llm_fakestop_p_done_latest {fakestop["p_done_latest"]:.3f}')
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
    processed_size = _current_size()
    print(f"dgx-ledger-exporter: serving :{PORT}, tailing {LEDGER}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
