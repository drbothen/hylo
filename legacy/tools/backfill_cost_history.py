#!/usr/bin/env python3
"""Seed the status line's per-session cost history from Claude Code transcripts (one-off).

The status line colors the session $ and $/h by YOUR OWN past sessions (same lane, last 30
days: yellow >= p75, red >= p95; status line review #11, 2026-11-14). Going forward it
records Claude Code's exact cost per session itself; this script backfills the history so
the percentiles work from day one. Recorded ("cc") entries are never overwritten here.

Backfill is approximate by construction (documented):
  - $ = the MAIN transcript repriced at list price (subagents/background calls are in their
    own files, so backfilled $ runs a little low vs Claude Code's total);
  - model time = summed per-message spans (triggering line -> last line, stale spans
    skipped), kept only when >= 30 min — shorter backfilled spans give noisy $/h;
  - sessions under $1 are skipped (short checks/probes, not work sessions).
Lane = where most of the session's output tokens came from: a model id starting with one
of LOCAL_MODEL_PREFIXES (default claude-sonnet) is the DGX lane, anything else Anthropic.

usage: python3 tools/backfill_cost_history.py [--days 30] [--dry-run]
"""
import argparse
import datetime
import glob
import json
import os
import tempfile
import time

# List prices per MTok (input, output, cache write 5m, cache write 1h, cache read), from the
# claude-api reference (cached 2026-11-03) — used ONLY by this one-off backfill.
PRICES = {"opus": (4.0, 20.0, 5.0, 8.0, 0.20),
          "sonnet": (2.0, 10.0, 2.5, 4.0, 0.10),
          "haiku": (0.10, 0.50, 0.125, 0.20, 0.005)}
HIST = os.path.expanduser("~/.cache/dgx-llm/cost-history.json")
MIN_USD = 1.0
MIN_BACKFILL_API_MS = 30 * 60 * 1000


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def session_cost(path, prefixes):
    msgs, order, lu, last = {}, [], None, None
    for line in open(path, errors="replace"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        t = e.get("timestamp")
        if not t:
            continue
        last = ts(t)
        m = e.get("message") or {}
        if e.get("type") == "user":
            lu = last
        elif e.get("type") == "assistant" and m.get("id") and isinstance(m.get("usage"), dict):
            i = m["id"]
            if i not in msgs:
                msgs[i] = {"t0": lu, "t1": last, "u": m["usage"], "model": m.get("model") or ""}
                order.append(i)
            else:
                msgs[i]["t1"] = last
    usd, span_s, out = 0.0, 0.0, {"dgx": 0, "anth": 0}
    for i in order:
        x = msgs[i]
        fam = next((k for k in PRICES if k in x["model"]), None)
        if not fam:
            continue
        u = x["u"]
        pi, po, p5, p1, pr = PRICES[fam]
        cc = u.get("cache_creation") or {}
        w1 = cc.get("ephemeral_1h_input_tokens") or 0
        w5 = cc.get("ephemeral_5m_input_tokens") or (0 if cc else (u.get("cache_creation_input_tokens") or 0))
        o = u.get("output_tokens") or 0
        usd += ((u.get("input_tokens") or 0) * pi + o * po + w5 * p5 + w1 * p1
                + (u.get("cache_read_input_tokens") or 0) * pr) / 1e6
        out["dgx" if any(x["model"].startswith(p) for p in prefixes) else "anth"] += o
        if x["t0"] is not None and 0 < x["t1"] - x["t0"] <= 4 * max(o, 1) / 15:
            span_s += x["t1"] - x["t0"]
    api_ms = span_s * 1000 if span_s * 1000 >= MIN_BACKFILL_API_MS else None
    return usd, api_ms, max(out, key=out.get), last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    prefixes = [p.strip() for p in os.environ.get("LOCAL_MODEL_PREFIXES", "claude-sonnet").split(",") if p.strip()]
    try:
        hist = json.load(open(HIST))
    except (OSError, ValueError):
        hist = {}
    sessions = hist.setdefault("sessions", {})
    cut = time.time() - a.days * 86400
    added = skipped_cc = skipped_small = 0
    for path in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
        if os.path.getmtime(path) < cut:
            continue
        sid = os.path.basename(path)[:-len(".jsonl")]
        if sessions.get(sid, {}).get("src") == "cc":
            skipped_cc += 1
            continue
        usd, api_ms, lane, last = session_cost(path, prefixes)
        if usd < MIN_USD or last is None:
            skipped_small += 1
            continue
        sessions[sid] = {"lane": lane, "usd": round(usd, 4), "api_ms": api_ms, "ts": last, "src": "backfill"}
        added += 1
    print(f"backfilled {added} sessions (skipped: {skipped_small} under ${MIN_USD:.0f}, {skipped_cc} already recorded exactly)")
    if not a.dry_run:
        os.makedirs(os.path.dirname(HIST), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(HIST), prefix="cost-history.")
        with os.fdopen(fd, "w") as fh:
            json.dump(hist, fh)
        os.replace(tmp, HIST)
        print(f"wrote {HIST}")


if __name__ == "__main__":
    main()
