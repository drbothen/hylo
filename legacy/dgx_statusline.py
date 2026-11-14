#!/usr/bin/env python3
"""claude-dgx status line — the cockpit view (workstream 1, 2026-11-11; reviewed v2).

Wired by the `claude-dgx` launcher through `--settings '{"statusLine":{"type":"command",
...}}'`, so it exists ONLY in DGX sessions (nothing written to ~/.claude/settings.json).
Claude Code pipes session JSON to stdin on each refresh (after every assistant message
+ every refreshInterval tick); we print up to two rows:

    ◨ DGX · Sonnet 5.5 · ⎇ main · home-lab · ▰▰▰▰▱▱▱▱▱▱ 43%/1.0M · ▤30% ❙68% ◈ 2% · ♻ 94% · ▲31/▼4
      · ⏱ 7h25m·1h52m ⌂1d07h · ↑88.0M[in500 ✍970k ⟳88.0M] ↓298k ↻1 · $32.62 $17.5/h ⛏n/a
    ◉ r3·q0 · KV▰▰▰▰ 92% · »113t/s · ▣204t/s ▅▆▇█ · ◔4.2s · ⚡1059W·1400W 66° 34¢/h · ☾ idle 2m

Row-1 legend (the long tail): `⏱ elapsed·model-time ⌂window-age` (elapsed resets on /clear,
⌂ does not); tokens `↑all-sent[in ✍write ⟳read] ↓out ↻rebuilds` (session totals, in+✍+⟳ = ↑);
`$ $/h` colored by your own same-lane p75/p95 over 30 days (cost-history.json).

Row-2 legend: `»113t/s` = THIS session's last completed API call (transcript, both
lanes, prefill included; dimmed when the reply was < 200 tokens); `▣204t/s` = the DGX box,
all clients, 1-minute vLLM generation rate — a different quantity, not a ratio; the
sparkline after it plots that box rate, zero-anchored (≤ 12 pts, ~48 s). `⚡GPU·wall` — the wall estimate carries the color. Full reference and the
2026-11-13 review: docs/STATUSLINE-WIDGETS.md, docs/STATUSLINE-REVIEW-2026-11-13.md.

Row 1 is the session: lane badge (DGX-served Flash = cyan ◨ DGX, Anthropic Opus/Haiku
passthrough = magenta ◨ ANTH, unknown env = grey), model, git branch, project, a
green→red truecolor context thermometer, prompt-cache hit ratio, lines added/removed,
session wall time and (subscription accounts) the 5h rate-limit gauge. Lane flips live
on a mid-session `/model opus` — it compares stdin's model.id against the launcher's
LOCAL_MODEL_PREFIXES.

Row 2 is the GB300 telemetry strip, ONE VictoriaMetrics round trip per refresh (~25 ms
LAN, disk-cached DGX_SL_TTL seconds keyed by session_id, atomic writes). Throughput
history feeds a fading sparkline persisted in that same cache. Degradation ladder:
fresh → green ◉; vLLM or (in-use) LMCache scrape down → red ◉ vLLM down / LMCache down;
VM briefly unreachable → yellow ◉ with last-known numbers + (~Ns) age; >KEEP_DEAD or
never seen → red ◌ DGX ?. Never an error, never blank (blank = nonzero exit), every
path ends in output + exit 0.

Contract notes (verified against code.claude.com docs, 2026-11-11):
  - stdout = one line per row; ANSI + truecolor OK; exit 0 required for display;
    stderr is invisible (logged only under `claude --debug`).
  - Refresh triggers: each assistant message, refreshInterval tick, /compact, mode
    changes; debounced 300 ms; in-flight runs are cancelled by newer triggers.
  - context_window.used_percentage is null before the first API call — guard it.
  - COLUMNS/LINES env hold the terminal size; COLUMNS may be absent/non-numeric.
  - Cache MUST key on session_id (stable per session), never pid (changes per run).
Env knobs (all optional):
    DGX_SL_VM_URL   VictoriaMetrics base (default http://192.0.2.10:8428)
    DGX_SL_TTL      cache/fetch TTL seconds (default 4, match refreshInterval)
    DGX_SL_ROWS     1 lane only / 2 both (default 2; also auto-drops row 2 <72 cols)
    DGX_SL_SPARK    0 disables the throughput sparkline (default on)
    DGX_SL_GIT      0 disables the git branch lookup (default on)
v2 fixes vs v1: visible-width (not byte) narrowing, stale-last-known actually renders,
proxy env bypassed for the VM call, empty model id → "?" lane (not false ANTH), no /0K
denominator, COLUMNS parse hardened, single cache read (no _HIST global), flatline
sparkline centered. Adds: git, timer, ±lines, rate-limit, idle marker, ¢/h.
"""

import colorsys
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.request

# ---------------------------------------------------------------- tunables --------------
VM_URL = os.environ.get("DGX_SL_VM_URL", "http://192.0.2.10:8428").rstrip("/")
TTL = float(os.environ.get("DGX_SL_TTL", "4"))
ROWS = int(os.environ.get("DGX_SL_ROWS", "2"))
SPARK_ON = os.environ.get("DGX_SL_SPARK", "1") != "0"
GIT_ON = os.environ.get("DGX_SL_GIT", "1") != "0"
CACHE_DIR = os.path.expanduser("~/.cache/dgx-llm")
STALE_OK = 15.0        # green dot while last good sample is younger than this (s)
KEEP_DEAD = 300.0      # last-known sample stays advertised (stale-flagged) this long (s)
HTTP_TIMEOUT = 1.5     # s; LAN round trip measured ~25 ms
SPARK_PTS = 12         # sparkline width (kept short: long flats read as blobs)
SPARK_MAX_AGE = 90.0   # s of history kept for the sparkline
HIST_MIN_GAP = 2.0     # s between sparkline samples
RL_KEEP = 1800.0       # s to keep displaying plan limits last reported by CC (no blinking)
# Which signal the sparkline plots: rate (box tok/s) | kv (GPU KV%) | ttft | mine.
# Rate is flat when the box is healthy — kv (pressure, predictive) and ttft (spiky)
# tend to carry more information; mine moves per turn.
TRACE = os.environ.get("DGX_SL_TRACE", "rate")
# show '☾ idle' when the DGX lane last got a request longer ago than this (s). 5 min is a
# judgment call: longer than a normal think/tool gap between turns of an active session, so
# it means "nobody is actively using the DGX lane" (review #20.2).
IDLE_AFTER = 300.0
# ⛏ guard: the cash basis is monthly cost / (trailing-24h DGX-lane tokens x month). Below
# 1M DGX-lane tokens in 24 h (= 30.4 MTok/month, roughly one modest session a day) there is
# no representative utilization to divide by — on 2026-11-13 a quiet day drove the basis to
# $3.47M/MTok. Below the floor ⛏ shows 'n/a' instead of a number (review #11.1).
MIN_BASIS_MTOK_MONTH = 30.4
GIT_TTL = 5.0          # s between real .git/HEAD reads (docs' example pattern)
NARROW_COLS = 72       # below this, auto-drop row 2 unless DGX_SL_ROWS forces it

QUERY = (
    '{__name__=~"vllm:num_requests_running|vllm:num_requests_waiting|'
    "vllm:kv_cache_usage_perc|dgx_kv:host_hit_share|"
    "dgx_tokens:gen_rate5m|dgx_ttft:p95_30m|dgx_preempt:rate5m|"
    "dgx_llm_last_dgx_request_timestamp_seconds|dgx_power:est_wall_watts|"
    "dgx_power:rate_usd_per_kwh|"
    "dgx_cost:dgx_usd_per_mtok|dgx_tokens:rate_mtok_month|"
    "vllm:lmcache_mp_lookup_duration_seconds_count|"
    'DCGM_FI_DEV_POWER_USAGE|DCGM_FI_DEV_GPU_TEMP"}'
    # Serving health (review 2026-11-13, #13): scrape health of vLLM and the LMCache server,
    # same round trip. Stored per job as "up:<job>" (see fetch_sample).
    ' or up{job=~"vllm|lmcache"}'
    # Sparkline 'rate' trace (review #17 A+): box tok/s over 1 MINUTE, so the ~48 s sparkline
    # moves on its own timescale (the 5-min average barely moved). The extra label is
    # REQUIRED: PromQL `or` matches label sets ignoring names, and an unlabeled series would
    # collide with dgx_tokens:gen_rate5m and be dropped.
    ' or label_set(alias(sum(rate(vllm:generation_tokens_total[1m])), "dgx_sl:gen_rate1m"),'
    ' "sl", "1m")'
    # TTFT sample size behind dgx_ttft:p95_30m (review #18): requests in the same 30-min window.
    ' or label_set(alias(sum(increase(vllm:time_to_first_token_seconds_count[30m])),'
    ' "dgx_sl:ttft_n30m"), "sl", "n30m")'
)
TTFT_MIN_N = 20        # below 20 samples the 95th percentile IS the maximum (1/20 = 5%)

# ---------------------------------------------------------------- primitives ------------
RESET, DIM, BOLD = "\033[0m", "\033[2m", "\033[1m"
SEP = f"{DIM} · {RESET}"
# Lane badge = inverted pill: bright bg + black bold text reads as a printed chip.
PILL_DGX, PILL_ANTH, PILL_NONE = "\033[106;30;1m", "\033[105;30;1m", "\033[100;37;1m"
WHITE, CYAN, GREEN, YELLOW, RED, GREY = (
    "\033[97m", "\033[36m", "\033[32m", "\033[33m", "\033[31m", "\033[90m")
MAGENTA = "\033[35m"
BOLDRED = "\033[1;91m"

SPARK = "▁▂▃▄▅▆▇█"
_ANSI = re.compile(r"\033\[[0-9;]*m")


def truecolor(rgb):
    return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"


def heat(pct):
    """0..100 -> green→amber→red truecolor for gauges and bars."""
    h = (1.0 - min(max(pct, 0.0), 100.0) / 100.0) * 0.22   # hue 0(red)..0.22(green)
    r, g, b = colorsys.hsv_to_rgb(h, 0.85, 0.80)
    return (int(r * 255), int(g * 255), int(b * 255))


def visible(text):
    """Display width of a decorated string: ANSI escape runs are zero-width."""
    return len(_ANSI.sub("", text))


# ---------------------------------------------------------------- VM fetch + cache -------

def fetch_sample(sid8=None):
    """One VictoriaMetrics instant query covering every series.

    -> ({metric_name: float} or None, {session_label: output-token counter}).
    The per-name first-wins rule must NOT swallow the labelled session series, so those
    are bucketed separately, keyed by their `session` label.
    """
    url = f"{VM_URL}/api/v1/query?query={urllib.parse.quote(QUERY, safe='')}"
    # Bypass HTTP(S)_PROXY env (the launcher exports HTTPS_PROXY pointing at the local
    # mitmproxy!). Talking metrics directly keeps the ledger clean and survives proxy death.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(url, timeout=HTTP_TIMEOUT) as resp:
            payload = json.loads(resp.read())
        if payload.get("status") != "success":
            return None
        out = {}
        for s in payload["data"]["result"]:
            name = s["metric"].get("__name__", "")
            try:
                val = float(s["value"][1])
            except (KeyError, ValueError, IndexError):
                continue
            if name == "up":                          # one per job: keep them apart
                name = "up:" + s["metric"].get("job", "")
            if name and name not in out:  # single-GPU/single-instance: first wins
                out[name] = val
        return out or None
    except Exception:
        return None


def load_cache(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_cache(path, data):
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=CACHE_DIR, prefix=os.path.basename(path) + ".")
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh)
        os.replace(tmp, path)  # atomic: readers never see a torn file
    except Exception:
        pass  # cache loss is cosmetic; the next refresh rewrites it


# ---- dynamic cost colors (review #11 revisit, owner design 2026-11-14) -------------------
# $ and $/h are colored against YOUR OWN past sessions on the same lane over the last 30
# days: yellow >= p75, red >= p95. History = ~/.cache/dgx-llm/cost-history.json, seeded by
# tools/backfill_cost_history.py and kept current by record_cost() with Claude Code's exact
# figures. Only sessions >= $1 count (below that: short checks, not work sessions). A
# backfilled burn rate counts only with >= 30 min of model time (approximate spans); an
# exact one from 5 min (same as the display). < 10 qualifying sessions in the lane -> cold
# start: $ yellow at a fixed $25, $/h uncolored.
COST_HIST = os.path.join(CACHE_DIR, "cost-history.json")
COST_WINDOW_S = 30 * 86400
COST_MIN_USD = 1.0
COST_MIN_N = 10
COST_FALLBACK_YELLOW = 25.0


def record_cost(sid, lane, usd, api_ms):
    """Store this session's exact cost (src 'cc'); throttled to one write per minute."""
    if not sid or lane not in ("dgx", "anth") or not isinstance(usd, (int, float)):
        return
    h = load_cache(COST_HIST)
    s = h.setdefault("sessions", {})
    e = s.get(sid) or {}
    now = time.time()
    if e.get("src") == "cc" and now - e.get("ts", 0) < 60:
        return                                     # throttle: one write per session-minute
    s[sid] = {"lane": lane, "usd": round(usd, 4),
              "api_ms": api_ms if isinstance(api_ms, (int, float)) else None,
              "ts": now, "src": "cc"}
    save_cache(COST_HIST, h)


def cost_thresholds(lane, sid):
    """-> ((usd_p75, usd_p95) | None, (rate_p75, rate_p95) | None) for this lane, excluding
    the current session. None = fewer than COST_MIN_N qualifying sessions (cold start)."""
    now = time.time()
    tot, rate = [], []
    for k, e in (load_cache(COST_HIST).get("sessions") or {}).items():
        if k == sid or e.get("lane") != lane or now - e.get("ts", 0) > COST_WINDOW_S:
            continue
        usd = e.get("usd")
        if not isinstance(usd, (int, float)) or usd < COST_MIN_USD:
            continue
        tot.append(usd)
        api = e.get("api_ms")
        need = 300000 if e.get("src") == "cc" else 1800000
        if isinstance(api, (int, float)) and api >= need:
            rate.append(usd / (api / 3.6e6))

    def pct(v):
        if len(v) < COST_MIN_N:
            return None
        v = sorted(v)
        return v[int(0.75 * (len(v) - 1))], v[int(0.95 * (len(v) - 1))]
    return pct(tot), pct(rate)


def claude_window_start(cache_path):
    """Unix start time of the Claude Code process running this status line, or None.

    Claude Code's stdin restarts every clock on /clear (a new session), so "how long has
    this window been open" must come from the process itself (owner request 2026-11-14):
    walk up from our parent (a per-refresh shell) to the ancestor whose command is
    `claude` and read its start time. Cached in the session file -> one ps walk per
    session, none on normal refreshes."""
    c = load_cache(cache_path)
    if isinstance(c.get("proc_start"), (int, float)):
        return c["proc_start"]
    try:
        import subprocess
        pid = os.getppid()
        for _ in range(6):
            out = subprocess.run(["ps", "-o", "ppid=,comm=,lstart=", "-p", str(pid)],
                                 capture_output=True, text=True, timeout=1).stdout.strip()
            if not out:
                return None
            ppid, comm, *rest = out.split(None, 2)
            if os.path.basename(comm) == "claude" and rest:
                start = time.mktime(time.strptime(rest[0].strip(), "%a %b %d %H:%M:%S %Y"))
                c["proc_start"] = start
                save_cache(cache_path, c)
                return start
            pid = int(ppid)
            if pid <= 1:
                return None
    except Exception:
        return None
    return None


def effective_rl(cache_path, rl_stdin):
    """Smoothed plan limits: CC sends rate_limits only on subscription accounts and
    possibly not on every refresh — so remember the last-seen value (RL_KEEP s) and
    keep displaying it, or the widget blinks/never-shows-stable. Policy: SHOW unless
    never seen (API-key session) or stale beyond RL_KEEP; the 'rerouting everything'
    case is handled separately via a bare-'claude' prefix (render_lane)."""
    now = time.time()
    if isinstance(rl_stdin, dict) and rl_stdin:
        c = load_cache(cache_path)
        c["rl"], c["rl_ts"] = rl_stdin, now
        save_cache(cache_path, c)
        return rl_stdin
    c = load_cache(cache_path)
    rl, ts = c.get("rl"), c.get("rl_ts", 0)
    return rl if (isinstance(rl, dict) and now - ts < RL_KEEP) else None


def get_sample(cache_path):
    """TTL'd fetch w/ stale fallback -> (sample|None, age_s, up_bool, spark_hist).

    (The per-session rate used to come from here — the delta of the ledger exporter's
    per-session output counter. It is now the transcript's last-turn rate, see _mix_counts;
    review 2026-11-13 #16.)
    """
    now = time.time()
    c = load_cache(cache_path)
    if c.get("fetch_ts", 0) > now - TTL:                       # fresh verdict, reuse it
        return c.get("sample"), now - c.get("ts", 9999), bool(c.get("up")), c.get("hist", [])
    sample = fetch_sample()
    entry = dict(c)                                            # preserves hist on failure
    entry.pop("sess_state", None)                              # retired (#16)
    if sample:
        # History for the sparkline: one dict per observation holding EVERY plottable
        # signal, so DGX_SL_TRACE can pick retroactively. A missing series simply omits
        # its key — never a fabricated 0 (that once drew fake cliffs to the floor).
        # Point format: {"t": unix, "v": box tok/s, "k": gpu-kv fraction,
        #                "f": ttft p95 s, "p": 1 when preemptions active}
        hist = [_norm_pt(p) for p in c.get("hist", [])]
        hist = [p for p in hist if now - p.get("t", 0) < SPARK_MAX_AGE]
        if not hist or now - hist[-1]["t"] >= HIST_MIN_GAP:
            pt = {"t": now}
            for key, series in (("v", "dgx_sl:gen_rate1m"),
                                ("k", "vllm:kv_cache_usage_perc"),
                                ("f", "dgx_ttft:p95_30m")):
                if series in sample:
                    pt[key] = sample[series]
            if "v" not in pt and "dgx_tokens:gen_rate5m" in sample:
                pt["v"] = sample["dgx_tokens:gen_rate5m"]        # fallback: 5-min average
            if sample.get("dgx_preempt:rate5m", 0) > 0:          # same rule as the queue (#17.3)
                pt["p"] = 1
            hist.append(pt)
        entry.update({"fetch_ts": now, "up": True, "ts": now, "sample": sample,
                      "hist": hist[-32:]})
        save_cache(cache_path, entry)
        return sample, 0.0, True, hist
    entry["fetch_ts"] = now                                    # remember we tried
    entry["up"] = False
    save_cache(cache_path, entry)
    age = now - c.get("ts", 0)
    if c.get("sample") and age < KEEP_DEAD:
        return c["sample"], age, False, c.get("hist", [])     # last-known, stale-flagged
    return None, age, False, []


# ---------------------------------------------------------------- git (cached) -----------

def git_branch(directory):
    """Branch name (or short sha) for the first repo found upward; '' when none/error.

    Anchored on the directory passed in (render_lane passes workspace.project_dir — the
    directory Claude Code was started in, by design; a non-repo start dir shows no branch).
    A directory counts as a repo only when its .git (directory, or worktree/submodule
    pointer file) holds a HEAD — a stray plain file named HEAD no longer ends the walk
    (review 2026-11-13, #3.2). Walks up to the filesystem root (#3.3); cached by caller."""
    try:
        d = os.path.abspath(directory or os.getcwd())
        while True:
            dotgit = os.path.join(d, ".git")
            gitdir = None
            if os.path.isdir(dotgit):
                gitdir = dotgit
            elif os.path.isfile(dotgit):                       # worktree: .git is a pointer file
                with open(dotgit) as fh:
                    first = fh.readline().strip()
                if first.startswith("gitdir:"):
                    gitdir = os.path.normpath(os.path.join(d, first[len("gitdir:"):].strip()))
            if gitdir and os.path.isfile(os.path.join(gitdir, "HEAD")):
                with open(os.path.join(gitdir, "HEAD")) as fh:
                    ref = fh.read().strip()
                if ref.startswith("ref: refs/heads/"):
                    return ref[len("ref: refs/heads/"):]
                return ref[:7]                                 # detached HEAD -> short sha
            parent = os.path.dirname(d)
            if parent == d:
                return ""
            d = parent
    except Exception:
        pass
    return ""


def git_segment(directory):
    if not GIT_ON:
        return None
    # Stable filename from a digest of the FULL path (NOT hash(): str hashes are salted per
    # process, so every invocation minted a new cache file). The previous key, the last 40
    # chars of the path, let two dirs with the same tail share an entry (review #3.4).
    key = hashlib.sha1(directory.encode("utf-8", "replace")).hexdigest()[:16]
    cache_path = os.path.join(CACHE_DIR, f"statusline-git-{key}.json")
    c = load_cache(cache_path)
    now = time.time()
    if now - c.get("ts", 0) > GIT_TTL or "branch" not in c:
        c = {"ts": now, "branch": git_branch(directory)}
        save_cache(cache_path, c)
    b = c.get("branch", "")
    return f"{GREY}⎇ {b}{RESET}" if b else None


# ---------------------------------------------------------------- row 1: session ---------

def fmt_ctx(cw):
    pct = cw.get("used_percentage")
    if not isinstance(pct, (int, float)):
        return None
    pct = min(max(pct, 0.0), 100.0)
    total = cw.get("context_window_size") or 0
    # Round half UP: round() is half-to-even, which gave 45% -> 4 cells but 55% -> 6
    # (review 2026-11-13, #5.2).
    filled = min(int(pct / 10 + 0.5), 10)
    bar = "".join(
        f"{truecolor(heat((i + 0.5) * 10))}▰" if i < filled else f"{GREY}▱"
        for i in range(10)) + RESET
    # Thresholds: plain <= 50% (no action needed); heat color above 50% (past halfway);
    # bold red from 85%. CC auto-compacts a native-1M model at ~967K (~96.7%), so 85% leaves
    # ~117K tokens (~12 points, roughly 10 heavy turns) of runway — time to /compact or wrap
    # on your own terms. Review 2026-11-13, #5.1.
    col = BOLDRED if pct >= 85 else (truecolor(heat(pct)) if pct > 50 else "")
    denom = f"{DIM}/{total / 1e6:.1f}M{RESET}" if total >= 1e6 else \
            (f"{DIM}/{total / 1000:.0f}K{RESET}" if total > 0 else "")
    return f"{bar} {col}{pct:.0f}%{RESET}{denom}"


def render_lane(d, mix=None, dgx_mtok=None, dgx_rate=None, win_start=None):
    model = d.get("model") or {}
    model_name = model.get("display_name") or model.get("id") or "?"
    model_id = model.get("id") or ""
    prefixes = [p.strip() for p in os.environ.get("LOCAL_MODEL_PREFIXES", "").split(",")
                if p.strip()]
    on_dgx = any(model_id.startswith(p) for p in prefixes) if (prefixes and model_id) else None
    badge = (PILL_DGX + " ◨ DGX " if on_dgx else
             PILL_ANTH + " ◨ ANTH " if on_dgx is False and model_id else
             PILL_NONE + " ◨ ? ") + RESET                   # no id yet -> ?, never a lie

    ws = d.get("workspace") or {}
    proj_dir = ws.get("project_dir") or ws.get("current_dir") or d.get("cwd") or ""
    parts = [badge, f"{WHITE}{model_name}{RESET}"]
    if proj_dir:
        g = git_segment(proj_dir)
        if g:
            parts.append(g)
        # normpath drops a trailing slash ("/x/p/" -> "p"); the root keeps "/" instead of
        # an empty segment between two separators (review 2026-11-13, #4.1).
        pname = os.path.basename(os.path.normpath(proj_dir)) or os.path.normpath(proj_dir)
        if pname:
            parts.append(f"{GREY}{pname}{RESET}")
    bar = fmt_ctx(d.get("context_window") or {})
    if bar:
        parts.append(bar)
    mb = mix_segment(mix) if mix else None                 # context CONTENT micro-bar
    if mb:
        parts.append(mb)

    # Cache hit = CC's prompt_cache.hit_ratio on BOTH lanes: this session's cache-read
    # tokens / all input tokens (docs). Honest on the DGX lane since vLLM runs with
    # --enable-prompt-tokens-details: its per-request cache_read_input_tokens =
    # num_local_cached + num_external_cached (vLLM PrefillStats), i.e. GPU prefix-cache
    # AND LMCache/host-tier hits. Until 2026-11-13 the DGX lane showed vLLM's box-wide
    # prefix_cache_hits/queries instead — GPU-only, so ~0% under LMCache while ~96% of
    # prompt tokens came from cache (review #7). Only whole 8,576-token blocks hit on DGX.
    hr = (d.get("prompt_cache") or {}).get("hit_ratio")
    if isinstance(hr, (int, float)):
        parts.append(f"{CYAN}♻{RESET} {min(max(hr, 0.0), 1.0) * 100:.0f}%")

    # Plan limits (subscription accounts; API-key sessions omit the whole block).
    # Labels are PLAIN TEXT ('5h'/'7d') on purpose: emoji codepoints (⛽🗓️) render as
    # huge colored glyphs in some terminals and wreck legibility (seen in the field).
    # Hidden ONLY when the plan can't be in play: never reported by CC (API account)
    # or stale beyond RL_KEEP — or when we reroute ALL Claude models to the DGX
    # (LOCAL_MODEL_PREFIXES containing bare 'claude'), leaving nothing to burn the plan.
    reroute_all = any(p.rstrip("*") in ("claude", "claude-")
                      for p in prefixes)
    rl = {} if reroute_all else (d.get("rate_limits") or {})
    shown = []
    now_rl = time.time()
    for label, key in (("5h", "five_hour"), ("7d", "seven_day")):
        w = rl.get(key) or {}
        pct = w.get("used_percentage")
        reset = w.get("resets_at")
        # CC drops a window once resets_at passes; the 30-min smoothing must too, or a
        # refilled window kept showing e.g. a red 5h95% (review 2026-11-13, #12.1).
        if isinstance(reset, (int, float)) and reset <= now_rl:
            continue
        if isinstance(pct, (int, float)):
            shown.append((label, min(max(pct, 0.0), 100.0), reset))
    if shown:
        binding = max(shown, key=lambda t: t[1])[0]
        bits = []
        for label, pct, reset in shown:
            # Bands: > 70% = pace yourself / plan around the reset; > 90% = throttling imminent.
            col = RED if pct > 90 else YELLOW if pct > 70 else GREY
            seg = f"{col}{label}{pct:.0f}%{RESET}"
            if label == binding and pct > 70 and isinstance(reset, (int, float)):
                rem = reset - now_rl
                if 0 < rem <= 8 * 86400:                       # 7d window max + slack
                    if rem >= 86400:                           # binding 7d: day-level (#12.2)
                        cd = f"{int(rem // 86400)}d{int((rem % 86400) // 3600):02d}h"
                    elif rem >= 3600:
                        cd = f"{int(rem // 3600)}h{int((rem % 3600) // 60):02d}m"
                    else:
                        cd = f"{int(rem // 60)}m"
                    seg += f" {col}->{cd}{RESET}"
            bits.append(seg)
        parts.append(" ".join(bits))

    cost = d.get("cost") or {}
    la, lr = cost.get("total_lines_added") or 0, cost.get("total_lines_removed") or 0
    if la or lr:
        parts.append(f"{GREEN}▲{_fmt_lines(la)}{RESET}{DIM}/{RESET}{RED}▼{_fmt_lines(lr)}{RESET}")

    dur = cost.get("total_duration_ms")
    if isinstance(dur, (int, float)) and dur > 60000:          # show timer after 1 minute
        # "⏱ <elapsed>·<api>": elapsed = wall clock since THIS session started (CC resets it
        # on /clear, which starts a new session — not since the window opened); api = time
        # spent waiting on the model (cost.total_api_duration_ms), dimmed. Review #9 follow-up
        # 2026-11-14: elapsed alone could not tell a long working session from an idle one.
        def _hm(ms):
            mins = int(ms // 60000)
            # % 60, not % 100: 75 min rendered "1h75m" until review 2026-11-13 (#9.1)
            return f"{mins // 60}h{mins % 60:02d}m" if mins >= 60 else f"{mins}m"
        seg = f"{GREY}⏱ {_hm(dur)}{RESET}"
        api = cost.get("total_api_duration_ms")
        if isinstance(api, (int, float)) and api >= 60000:
            # not capped at elapsed: concurrent (subagent) API calls can sum past wall time
            seg += f"{DIM}·{_hm(api)}{RESET}"
        # ⌂ = how long this Claude Code window has been open (process age, survives /clear);
        # shown only when it exceeds the session's elapsed time by >= 5 min, i.e. after a
        # /clear or resume — otherwise it would repeat the elapsed figure.
        if isinstance(win_start, (int, float)):
            win_ms = (time.time() - win_start) * 1000
            if win_ms - dur >= 300000:
                wm = int(win_ms // 60000)
                wtxt = f"{wm // 1440}d{(wm % 1440) // 60:02d}h" if wm >= 1440 else _hm(win_ms)
                seg += f"{GREY} ⌂{wtxt}{RESET}"
        parts.append(seg)

    # Session token totals + cost. Totals prefer CC's own stdin figures and fall back to
    # our transcript accumulation; cost is CC's list-price computation — on the DGX lane
    # we add the electricity-equivalent for the same tokens (dgx_cost:dgx_usd_per_mtok),
    # because $0.09-at-cost vs $X-at-list IS the displacement story this rig exists for.
    # SESSION totals come only from our transcript parse (each API message id counted once).
    # CC's context_window.total_input/output_tokens are the LAST API response (current
    # context: 353,850 = that call's input+cache_creation+cache_read), not the session —
    # verified on live stdin, review 2026-11-13 #10.1. Main-session transcript only:
    # subagents write their own files, so their tokens are not in these totals.
    tin = tout = c_wr = c_rd = c_in = rb = None
    if mix and len(mix) >= 7:
        tin, tout, c_wr, c_rd = mix[3], mix[4], mix[5], mix[6]
    if mix and len(mix) >= 10:
        c_in, rb = mix[8], mix[9]
    # Owner-approved layout (review #10 revisit, 2026-11-14): "↑total[in ✍ ⟳] ↓out ↻n".
    #   ↑  all prompt tokens sent (the context re-sent on every call)  = in + ✍ + ⟳ exactly
    #   in fresh uncached input  ($4/MTok Opus 5.5)     ✍ cache writes ($8/MTok, 1-h TTL)
    #   ⟳  cache reads ($0.20/MTok)                     ↓ output ($20/MTok)
    #   ↻  cache rebuilds (REBUILD_EXCESS rule), hidden when 0
    # The bracketed parts are non-overlapping price classes; zero parts are omitted.
    have_t = isinstance(tin, (int, float)) or isinstance(tout, (int, float))
    if have_t and ((tin or 0) > 0 or (tout or 0) > 0):
        seg = f"{GREY}↑{RESET}{WHITE}{_fmt_tok_c(tin or 0)}{RESET}"
        inner = []
        if isinstance(c_in, (int, float)) and c_in > 0:
            inner.append(f"{WHITE}in{_fmt_tok_c(c_in)}{RESET}")
        if isinstance(c_wr, (int, float)) and c_wr > 0:
            inner.append(f"{YELLOW}✍{_fmt_tok_c(c_wr)}{RESET}")
        if isinstance(c_rd, (int, float)) and c_rd > 0:
            inner.append(f"{CYAN}⟳{_fmt_tok_c(c_rd)}{RESET}")
        if len(inner) >= 2:                  # one part alone always equals ↑: no brackets
            seg += f"{DIM}[{RESET}" + " ".join(inner) + f"{DIM}]{RESET}"
        seg += f"{GREY} ↓{RESET}{WHITE}{_fmt_tok_c(tout or 0)}{RESET}"
        if isinstance(rb, (int, float)) and rb > 0:
            seg += f" {DIM}{YELLOW}↻{rb:.0f}{RESET}"
        parts.append(seg)
    usd = cost.get("total_cost_usd")
    if isinstance(usd, (int, float)) and usd > 0:
        api_ms = cost.get("total_api_duration_ms")
        lane = "dgx" if on_dgx else ("anth" if on_dgx is False else None)
        sid = d.get("session_id")
        record_cost(sid, lane, usd, api_ms)
        th_usd, th_rate = cost_thresholds(lane, sid) if lane else (None, None)
        # $ color: grey < $1 (a short check); then YOUR p75/p95 on this lane (yellow/red);
        # cold start (< 10 sessions) -> yellow at a fixed $25.
        if usd < COST_MIN_USD:
            col = GREY
        elif th_usd:
            col = RED if usd >= th_usd[1] else YELLOW if usd >= th_usd[0] else WHITE
        else:
            col = YELLOW if usd >= COST_FALLBACK_YELLOW else WHITE
        cseg = f"{col}${usd:.2f}{RESET}"
        # Burn rate (review #11 revisit, owner 2026-11-14): $ per hour of MODEL work =
        # total_cost_usd / total_api_duration_ms — "is this session expensive per unit of
        # work", not just big. From 5 min of API time (below that the ratio is noise). Same
        # caveat as $: list price, incl. subagents/background; counterfactual on the DGX lane.
        # Colored by YOUR $/h p75/p95 on this lane; uncolored at cold start.
        if isinstance(api_ms, (int, float)) and api_ms >= 300000:
            r = usd / (api_ms / 3.6e6)
            rc = (RED if r >= th_rate[1] else YELLOW if r >= th_rate[0] else GREY) if th_rate else GREY
            cseg += f"{rc} ${r:.1f}/h{RESET}"
        tot = (tin or 0) + (tout or 0)
        if on_dgx and tot > 0:
            basis_ok = (isinstance(dgx_rate, (int, float)) and dgx_rate >= MIN_BASIS_MTOK_MONTH
                        and isinstance(dgx_mtok, (int, float)) and dgx_mtok > 0)
            if not basis_ok:
                cseg += f"{GREY} ⛏n/a{RESET}"                 # no representative utilization
            else:
                eq = tot * dgx_mtok / 1e6
                if eq >= 0.005:                                # skip sub-half-cent noise
                    cseg += f"{GREY} ⛏{eq:.2f}{RESET}"
        parts.append(cseg)
    return parts


# ---------------------------------------------------------------- row 2: DGX telemetry ---

# 'mine' retired 2026-11-13 (#17.4: its per-refresh counter source was removed in #16);
# an unknown/retired name falls back to 'rate'.
TRACE_KEYS = {"rate": "v", "kv": "k", "ttft": "f"}
# Zero-anchored scale ceilings (review #17.1): bar height = value / max(window max, floor).
# kv is a fraction with a FIXED 0-1 scale; the floors keep an idle box at the lowest bar
# instead of magnifying noise (1 tok/s, 0.1 s).
_SPARK_FIXED = {"k": 1.0}
_SPARK_FLOOR = {"v": 1.0, "f": 0.1}


def _norm_pt(p):
    """History point normalizer: legacy [ts, rate] lists -> dict form."""
    if isinstance(p, list):
        return {"t": p[0], "v": p[1]}
    return p if isinstance(p, dict) else {}


def sparkline(hist):
    """Plots the TRACE-selected signal from history with headroom padding so flat-ish
    data stays legible. Cells sample-marked with p=1 (preemptions active) flash amber."""
    key = TRACE_KEYS.get(TRACE, "v")
    pts = [(_np.get("t"), _np.get(key), _np.get("p"))
           for _np in (_norm_pt(p) for p in hist[-SPARK_PTS:])
           if _np.get(key) is not None]
    if len(pts) < 2:
        return ""
    vals = [v for _, v, _ in pts]
    # Zero-anchored: height is proportional to the value, so a 0.3% drift stays flat and a
    # doubling looks like one. The old min-max autoscale (+15% pad) drew both identically.
    top = _SPARK_FIXED.get(key) or max(max(vals), _SPARK_FLOOR.get(key, 1e-9))

    def idx(v):
        j = max(v, 0.0) / top * (len(SPARK) - 1)
        return int(min(j, len(SPARK) - 1) + 0.5)

    out = []
    for i, (_, v, pre) in enumerate(pts[:-1]):     # trail: muted, fades toward the left
        if pre:
            r, g, b = 220, 170, 60                 # preemption burst: amber, unfaded
        else:
            fade = 0.55 + 0.45 * i / max(len(pts) - 2, 1)
            r, g, b = (int(c * fade) for c in (70, 170, 190))
        out.append(f"\033[38;2;{r};{g};{b}m{SPARK[idx(v)]}")
    _, v_last, pre_last = pts[-1]
    if pre_last:
        out.append(f"{YELLOW}{SPARK[idx(v_last)]}")    # head flashes amber too
    else:
        out.append(f"{truecolor((140, 235, 255))}{SPARK[idx(v_last)]}")  # brightest
    return "".join(out) + RESET


def render_telemetry(sample, age, up, hist, sess_rate=None):
    """Degradation ladder: red '?' when nothing known; stale-known keeps fields + age."""
    if not sample:
        return [f"{RED}◌ DGX ?{RESET}"]
    if not up or age > STALE_OK:
        parts = render_telemetry_fields(sample, stale=True, hist=hist, sess_rate=sess_rate)
        if age > 0:
            parts.append(f"{DIM}(~{age:.0f}s old){RESET}")
        return parts
    return render_telemetry_fields(sample, stale=False, hist=hist, sess_rate=sess_rate)


def serving_state(m):
    """-> None (serving OK / unknown) | 'vLLM down' | 'LMCache down'.

    The dot used to mean only "VictoriaMetrics answered", so a dead vLLM showed a green dot
    over an idle-looking strip (review 2026-11-13, #13.1).
      vLLM down    = its scrape reports up=0, or the up series is absent AND no vllm:* series
                     came back (job missing entirely).
      LMCache down = vLLM is running with the LMCache connector (only then does vLLM export
                     vllm:lmcache_mp_lookup_duration_seconds) AND the lmcache scrape is up=0.
                     Under native offload the lmcache job is permanently down by design, so
                     it only counts when the connector is in use (#13 A+)."""
    up_v = m.get("up:vllm")
    has_vllm = any(k.startswith("vllm:") for k in m)
    if up_v == 0 or (up_v is None and not has_vllm):
        return "vLLM down"
    if "vllm:lmcache_mp_lookup_duration_seconds_count" in m and m.get("up:lmcache") == 0:
        return "LMCache down"
    return None


def render_telemetry_fields(m, stale, hist, sess_rate=None):
    dot = YELLOW if stale else GREEN
    down = serving_state(m)
    # Red text, not just a red dot: either failure stalls or fails DGX-lane requests
    # (the LMCache connector waits on server lookups), so it must not read as "idle".
    parts = [f"{RED}◉ {down}{RESET}" if down else f"{dot}◉{RESET}"]

    r = m.get("vllm:num_requests_running")
    if r is not None:
        q = m.get("vllm:num_requests_waiting", 0)
        # Yellow when ANYTHING waits (incl. r0·q>0 = stalled scheduler; was green until
        # review 2026-11-13 #14.1, condition was `r and q`) or when ANY preemption happened
        # in the last 5 min — the capacity contract's own failure signal (zero preemptions
        # to pass; C2 failed on one). Was > 0.01/s = 3+ per 5 min (#14.2). Yellow, not red:
        # "waiting" also holds requests briefly waiting for an LMCache load at admission.
        busy = q > 0 or m.get("dgx_preempt:rate5m", 0) > 0
        parts.append(f"{YELLOW if busy else GREEN}r{r:.0f}·q{q:.0f}{RESET}")

    # KV gauge = blocks held by RUNNING requests (not occupancy; reads 85-96% in healthy
    # 12-agent operation). The overflow signal is the host-tier share of reused history
    # (dgx_kv:host_hit_share): 0% while every agent's history fits on the GPU, 80% at 13 agents,
    # 100% at 14+. Yellow when > 5% (THRESHOLDS.md §8). Until 2026-11-12 this went yellow on
    # gauge > 80% and showed "+host" from kv_offload_cpu_cache_usage_perc, which is memory
    # pinned by in-flight transfers, not host-tier fill — both inconsistent with the dashboards.
    # Review 2026-11-13 #15: hide when the series is missing (vLLM down/restarting used to
    # render an invented "KV 0%"); 4 cells by CEILING quarters — 0% empty, 1-25 one cell,
    # 26-50 two, 51-75 three, 76-100 four — so healthy busy operation (85-96%) is a steady
    # full bar instead of flickering at a rounding boundary. "↺host" = native host offload
    # OR LMCache L1 (vLLM credits both as external hits).
    kv_raw = m.get("vllm:kv_cache_usage_perc")
    hs_raw = m.get("dgx_kv:host_hit_share")
    host_share = hs_raw * 100 if isinstance(hs_raw, (int, float)) else None
    if isinstance(kv_raw, (int, float)):
        kv = min(max(kv_raw * 100, 0.0), 100.0)
        n = min(math.ceil(kv / 25), 4)
        warn = host_share is not None and host_share > 5
        parts.append(f"{YELLOW if warn else CYAN}KV{'▰' * n}{'▱' * (4 - n)} {kv:.0f}%{RESET}"
                     + (f" {DIM}↺host {host_share:.0f}%{RESET}"
                        if host_share is not None and host_share > 0.5 else ""))

    # Two SEPARATE segments (owner decision 2026-11-14, review #16 follow-up): they measure
    # different things in different units, so "mine/box" invited a false comparison.
    #   »mine t/s  THIS session's last completed API call, output tokens / (trigger -> last
    #              line), from the transcript — both lanes, prefill included; dimmed when the
    #              reply was < 200 tokens (review #16).
    #   ▣box t/s   the DGX box: every client's vLLM output tok/s over 1 MINUTE (same series the
    #              sparkline beside it plots); 5-min rate only as a fallback.
    rate = m.get("dgx_sl:gen_rate1m", m.get("dgx_tokens:gen_rate5m"))
    # sess_rate = [rate, dim]; dim (reply < TURN_DIM_OUT tokens) renders grey: shown, but
    # flagged as latency-dominated rather than throughput.
    mine = ""
    if isinstance(sess_rate, (list, tuple)) and sess_rate and isinstance(sess_rate[0], (int, float)):
        dim = len(sess_rate) > 1 and bool(sess_rate[1])
        mine = (f"{GREY}{sess_rate[0]:.0f}{RESET}" if dim
                else f"{BOLD}{WHITE}{sess_rate[0]:.0f}{RESET}")
    if mine:
        parts.append(f"{GREY}»{RESET}{mine}{GREY}t/s{RESET}")
    if rate is not None:
        box = f"{GREY}▣{RESET}{GREY if stale else WHITE}{rate:.0f}{RESET}{GREY}t/s{RESET}"
        sp = "" if stale or not SPARK_ON else sparkline(hist)
        parts.append((box + f" {sp}").rstrip())

    # TTFT p95 over 30 min, box-wide (every DGX client incl. benchmarks and synthetic probes).
    # Review #18: with < TTFT_MIN_N requests in the window the "p95" is the slowest request,
    # so it renders dimmed as "max" and never triggers the yellow (> 8 s, THRESHOLDS §8b).
    # Integer seconds from 10 s: buckets there are 20/40/80/160/640/2560 s, so decimals were
    # interpolation, not precision. NaN (no data) hides the segment.
    ttft = m.get("dgx_ttft:p95_30m")
    if isinstance(ttft, (int, float)) and not math.isnan(ttft):
        n = m.get("dgx_sl:ttft_n30m")
        val = f"{ttft:.0f}s" if ttft >= 10 else f"{ttft:.1f}s"
        if isinstance(n, (int, float)) and n < TTFT_MIN_N:
            parts.append(f"{GREY}◔max {val}{RESET}")
        else:
            parts.append(f"{YELLOW if ttft > 8 else GREY}◔{val}{RESET}")

    w = m.get("DCGM_FI_DEV_POWER_USAGE")
    if w is not None:
        t = m.get("DCGM_FI_DEV_GPU_TEMP")
        wall, rate_c = m.get("dgx_power:est_wall_watts"), m.get("dgx_power:rate_usd_per_kwh")
        # Color = whole-box wall estimate vs the 1,600 W system rating (80% / 95%, THRESHOLDS.md
        # §8); the number shown stays GPU watts. Until 2026-11-12 the 1,200/1,500 W cut-offs were
        # applied to GPU-only watts, the wrong quantity for a system rating.
        # Review 2026-11-13 #19 (A+): "⚡<GPU>W·<wall>W" — the GPU number stays neutral and
        # the whole-box wall estimate is shown next to it and carries the color, so the
        # color is attached to the quantity it judges (a red ⚡900W used to mean the BOX,
        # not the GPU, was over 1,520 W).
        wc = (RED if wall > 1520 else YELLOW if wall > 1280 else WHITE) if wall else WHITE
        txt = f"{WHITE}⚡{w:.0f}W{RESET}"
        if wall:
            txt += f"{GREY}·{RESET}{wc}{wall:.0f}W{RESET}"
        txt += (f"{GREY} {t:.0f}°{RESET}" if t is not None else "")
        if wall and rate_c:                                    # whole-box estimate × tariff
            cents = wall / 1000 * rate_c * 100
            txt += f"{GREY} {cents:.0f}¢/h{RESET}"
        parts.append(txt)

    # DGX-lane recency only: Opus/Haiku passthrough also writes ledger events, and
    # the any-event timestamp let Anthropic traffic mask a genuinely idle DGX.
    last = m.get("dgx_llm_last_dgx_request_timestamp_seconds")
    if last and last > 0 and time.time() - last > IDLE_AFTER and (m.get("vllm:num_requests_running") or 0) < 1:
        idle_min = int((time.time() - last) // 60)
        # 6m / 18h20m / 3d04h — minutes-only read "1100m" after a quiet day (review #20.1)
        if idle_min >= 1440:
            age = f"{idle_min // 1440}d{(idle_min % 1440) // 60:02d}h"
        elif idle_min >= 60:
            age = f"{idle_min // 60}h{idle_min % 60:02d}m"
        else:
            age = f"{idle_min}m"
        parts.append(f"{CYAN}☾ idle {age}{RESET}")
    return parts

# ------------------------------------------------------------- subagent panel row --------
# Claude Code's `subagentStatusLine` setting replaces the row BODY of each subagent in
# the agent panel (what you see when you expand an agent). Different contract from the
# main line: stdin holds {"columns": N, "tasks": [{id, name, agentType, status,
# description, label, startTime(ms), model, tokenCount, ...}]} for ALL visible rows and
# we emit one JSON line per row: {"id": "<task id>", "content": "<rendered row>"}.
# Omitted rows keep CC's default body; empty content hides the row.

_SUB_GLYPH = {"running": ("»", YELLOW), "completed": ("✔", GREEN),
              "failed": ("✘", RED), "killed": ("◍", GREY)}


def _fmt_lines(n):
    """Line counts: exact below 10,000; whole thousands up to 1M ('184k'); then 1 decimal
    ('1.2M'). Keeps row 1 narrow on big refactors (review 2026-11-13, #8.1)."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "?"
    if n >= 1_000_000:
        return f"{n / 1e6:.1f}M"
    if n >= 10_000:
        return f"{n // 1000}k"
    return str(n)


def _fmt_tok_c(n):
    """Compact tokens for the row-1 token segment: 500, 970k, 88.0M (approved mockup)."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "?"
    if n >= 1e6:
        return f"{n / 1e6:.1f}M"
    if n >= 1000:
        return f"{n / 1000:.0f}k"
    return f"{n:.0f}"


def _fmt_tokens(n):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "?"
    if n >= 1e6:
        return f"{n / 1e6:.2f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return f"{n:.0f}"


def render_subagent_rows(d):
    now_ms = time.time() * 1000
    out = []
    for task in d.get("tasks") or []:
        if not isinstance(task, dict) or "id" not in task:
            continue
        glyph, col = _SUB_GLYPH.get(task.get("status"), ("◍", GREY))
        name = task.get("name") or task.get("label") or task.get("description") or task.get("agentType") or "?"
        bits = [f"{col}{glyph} {name}{RESET}"]

        model = task.get("model")
        if model:
            # Lane tag (review 2026-11-13 #21.4): same prefix rule as the main lane pill, so a
            # Haiku subagent inside a DGX session shows it is served by Anthropic.
            prefixes = [p.strip() for p in os.environ.get("LOCAL_MODEL_PREFIXES", "").split(",")
                        if p.strip()]
            lane = ""
            if prefixes:
                lane = (f"{CYAN}◨DGX{RESET} " if any(model.startswith(p) for p in prefixes)
                        else f"{MAGENTA}◨ANTH{RESET} ")
            bits.append(f"{lane}{GREY}{model}{RESET}")
        tok = task.get("tokenCount")
        if isinstance(tok, (int, float)) and tok > 0:
            bits.append(f"{CYAN}{_fmt_tokens(tok)} tok{RESET}")
        st = task.get("status")
        start = task.get("startTime")
        # Elapsed clock ONLY while running: CC keeps finished rows in the panel and its
        # contract (2.1.322) carries no end time, so a completed/failed row's clock used to
        # keep counting up (review #21.2). (Dead contextUsedPercentage / unused
        # contextWindowSize branches removed — neither is usable as sent, #21.3.)
        if st == "running" and isinstance(start, (int, float)) and start > 0:
            secs = max(now_ms - start, 0) / 1000
            bits.append(f"{GREY}{int(secs // 60):02d}:{int(secs % 60):02d}{RESET}")
        if st and st != "running":
            bits.append(f"{GREY}{st}{RESET}")

        out.append(json.dumps({"id": task["id"], "content": " · ".join(bits)}))
    return out


def main_subagent():
    try:
        d = json.load(sys.stdin)
    except Exception:
        d = {}
    rows = render_subagent_rows(d if isinstance(d, dict) else {})
    if rows:
        print("\n".join(rows))
    return 0

# ------------------------------------------------------- context composition (mix) -------
# WHAT'S IN the context, not just how full it is: a proportional bar over the three
# movable buckets, parsed from the session transcript (stdin transcript_path):
#   ▤ tool results (file reads, command output — usually the whale)
#   ❙ conversation (user text + assistant text + tool_use payloads)
#   ◈ thinking
# Byte-proportional (≈tokens/4, the same heuristic the ledger exporter uses). The
# system prompt/tool definitions are NOT in the transcript file, so they are out of
# scope by construction; the bar shows the share of what the session can influence.
# Parsing is incremental: the cache remembers the byte offset, only NEW complete
# lines are parsed per refresh, capped per refresh; a shrunk transcript (new session
# file / compaction) resets the accumulator.

_MIX_CACHE = "statusline-mix-%s.json"
_READ_CAP = 524288          # max bytes of transcript parsed per refresh

# Last-turn delivered rate (review 2026-11-13 #16), from the transcript, so it works on BOTH
# lanes: output tokens of one API message / (its triggering user line -> its last line).
# Includes prefill (the wait you actually experience). Replay 2026-11-13 (456 DGX-lane and
# 193 Anthropic-lane messages; medians 81 / 85 tok/s):
#   TURN_DIM_OUT 200 tokens: replies shorter than this are SHOWN but DIMMED — their time is
#                mostly prefill/latency, not throughput. (They used to be skipped, which
#                biased the shown value up 1.5-3% and left an older, faster turn on screen;
#                owner decision 2026-11-13.)
#   stale span:  span > TURN_STALE x out / TURN_FLOOR_TPS (effective < 3.75 tok/s) means the
#                "trigger" line is not the real request (user stepped away, an approval prompt
#                waited) — a measurement error, not slow service; skipped. 15 tok/s = the
#                harness's per-agent decode floor, 4x = margin for slow prefill. Known edge: a
#                very long prefill with a short reply (~85 s, 300 tokens) is skipped too.
TURN_DIM_OUT = 200
# Cache rebuild detector (review #10 revisit, 2026-11-14): a call whose cache WRITE exceeds its
# context GROWTH by more than this re-wrote already-cached context. Validated on 9,650 calls in
# 120 transcripts: normal calls max 4,145 excess (99.9% under 577); smallest rebuild 61,901 —
# 20K sits ~5x above the worst normal call and ~3x below the smallest rebuild.
REBUILD_EXCESS = 20000
TURN_FLOOR_TPS = 15.0
TURN_STALE = 4.0


def _iso_ts(s):
    """Transcript timestamp ('2026-11-13T20:18:04.123Z') -> unix seconds, or None."""
    if not isinstance(s, str):
        return None
    try:
        import datetime
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _finish_turn(cur, lr):
    """Close the current API message; return the new last-turn [rate, dim] (or keep lr).
    dim = True when the reply was shorter than TURN_DIM_OUT (latency-dominated)."""
    if not cur or cur.get("t0") is None:
        return lr
    out, span = cur.get("out") or 0, (cur.get("t1") or 0) - cur["t0"]
    if out <= 0 or span <= 0 or span > TURN_STALE * out / TURN_FLOOR_TPS:
        return lr
    return [out / span, out < TURN_DIM_OUT]


def _mix_counts(d):
    """Incrementally parse the transcript.

    -> (res, conv, think, tin, tout, c_wr, c_rd): composition byte counts PLUS cumu-
    lative session usage: tin = input + cache-creation + cache-read (billed-equivalent
    input), tout = output, c_wr = cache-write tokens (1.25x priced), c_rd = cache-read
    tokens (0.1x priced). None when no transcript exists. Introducing a missing key
    (token fields added later, or usage split added later) triggers one honest full
    re-parse via the offset reset.
    """
    path = d.get("transcript_path")
    if not path or not os.path.isfile(path):
        return None
    try:
        size = os.stat(path).st_size
    except OSError:
        return None
    sid = d.get("session_id") or "nosession"
    mcache = os.path.join(CACHE_DIR, _MIX_CACHE % re.sub(r"[^A-Za-z0-9_-]", "_", sid)[:40])
    c = load_cache(mcache)
    off = c.get("size", 0)
    res, conv, think = c.get("res", 0), c.get("conv", 0), c.get("think", 0)
    tin, tout = c.get("tin", 0), c.get("tout", 0)
    c_wr, c_rd = c.get("c_wr", 0), c.get("c_rd", 0)
    lr, lu, cur = c.get("lr"), c.get("lu"), c.get("cur")   # last-turn rate state (#16)
    c_in, rb, pp = c.get("c_in", 0), c.get("rb", 0), c.get("pp")  # fresh input, rebuilds (#10)
    need_reset = False
    for key in ("tin", "c_wr", "mixv6"):           # fields/semantics introduced post-launch
        if key not in c and off > 0:               # (mixv6: compaction reset, usage dedup,
            need_reset = True                      #  last-turn rate, fresh input + rebuilds)
    # Usage dedup: CC writes ONE transcript line per content block of an API message and
    # repeats the message's full usage on every line (93/106 messages split), so summing
    # per line overcounted x2.91 (review #10.2). Count each message id once; ids of the
    # same message are adjacent, a short memory of recent ids covers refresh boundaries.
    recent_ids = list(c.get("ids", [])) if not (need_reset or size < off) else []
    seen_ids = set(recent_ids)
    if need_reset or size < off:
        off, res, conv, think, tin, tout, c_wr, c_rd = 0, 0, 0, 0, 0, 0, 0, 0
        lr = lu = cur = pp = None
        c_in = rb = 0
    if size == off:
        return res, conv, think, tin, tout, c_wr, c_rd, lr, c_in, rb
    try:
        with open(path, "rb") as fh:
            fh.seek(off)
            blob = fh.read(min(size - off, _READ_CAP))
            # A single line longer than the cap (big tool results reach 1.36 MB; 28 of 200
            # recent transcripts) used to yield no newline -> offset never advanced -> the
            # parse froze for the rest of the session. Finish the line instead (review #6.5).
            while b"\n" not in blob and off + len(blob) < size:
                more = fh.read(_READ_CAP)
                if not more:
                    break
                blob += more
    except OSError:
        return res, conv, think, tin, tout, c_wr, c_rd, lr, c_in, rb
    cut = blob.rfind(b"\n")                                    # complete lines only
    if cut < 0:
        return res, conv, think, tin, tout, c_wr, c_rd, lr, c_in, rb
    off += cut + 1
    for line in blob[:cut].splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue                                           # torn/partial line: skip
        # Last-turn rate. A message's lines can be INTERLEAVED with tool_result user lines
        # (CC runs a tool, then writes the message's next block), so turns are keyed on the
        # message id: start = user line before its FIRST line, end = its LAST line. Close it
        # on a newer message id, a system line (turn_duration / stop_hook_summary / compact)
        # or a real user prompt — never on an interleaved tool_result.
        typ, t_line = e.get("type"), _iso_ts(e.get("timestamp"))
        if t_line is not None:
            m_ = e.get("message") or {}
            mid_ = m_.get("id")
            if typ == "assistant" and mid_:
                if cur and cur.get("id") == mid_:
                    cur["t1"] = t_line
                else:
                    lr = _finish_turn(cur, lr)
                    cur = {"id": mid_, "t0": lu, "t1": t_line,
                           "out": (m_.get("usage") or {}).get("output_tokens") or 0}
            elif typ == "user":
                cont = m_.get("content")
                if not (isinstance(cont, list) and any(
                        isinstance(b, dict) and b.get("type") == "tool_result" for b in cont)):
                    lr, cur = _finish_turn(cur, lr), None
                lu = t_line
            elif typ == "system":
                lr, cur = _finish_turn(cur, lr), None
        if e.get("type") == "system" and e.get("subtype") == "compact_boundary":
            # Compaction APPENDS a boundary + summary; the file never shrinks. Everything
            # before it left the context, so the composition buckets restart here. Session
            # usage totals (tin/tout/c_wr/c_rd) are cumulative and deliberately NOT reset.
            # (review 2026-11-13, #6.1: whole-file ▤17% ❙65% ◈18% vs real ▤4% ❙95% ◈1%)
            res = conv = think = 0
            pp = None              # new context: the next call's write is not a rebuild
            continue
        msg = e.get("message") or {}
        u = msg.get("usage")
        mid = msg.get("id")
        if isinstance(u, dict) and mid and mid in seen_ids:
            u = None                                           # same API call, already counted
        elif isinstance(u, dict) and mid:
            seen_ids.add(mid)
            recent_ids.append(mid)
        if isinstance(u, dict):                                # true per-call usage
            _i = u.get("input_tokens") or 0
            _w = u.get("cache_creation_input_tokens") or 0
            _r = u.get("cache_read_input_tokens") or 0
            tin += _i + _w + _r
            c_in += _i
            c_wr += _w
            c_rd += _r
            tout += u.get("output_tokens") or 0
            # Rebuild = this call wrote more than its context grew, by > REBUILD_EXCESS: it
            # re-wrote context that was already cached (expired after > 1 h idle, or the
            # cached prefix changed — tool list / system prompt / model).
            prompt = _i + _w + _r
            if pp is not None and _w - max(0, prompt - pp) > REBUILD_EXCESS:
                rb += 1
            pp = prompt
        content = msg.get("content")
        if isinstance(content, str):
            conv += len(content)
            continue
        if not isinstance(content, list):
            continue
        for blk in content:
            if not isinstance(blk, dict):
                continue
            bt = blk.get("type")
            if bt == "tool_result":
                inner = blk.get("content")
                if isinstance(inner, str):
                    n = len(inner)
                elif isinstance(inner, list):
                    # nested images (e.g. browser screenshots) count like top-level ones,
                    # not as hundreds of KB of base64 JSON (review #6.3)
                    n = sum(2000 if isinstance(it, dict) and it.get("type") == "image"
                            else len(json.dumps(it)) for it in inner)
                else:
                    n = len(json.dumps(inner)) if inner is not None else 0
                res += n
            elif bt == "text":
                conv += len(blk.get("text") or "")
            elif bt == "thinking":
                think += len(blk.get("thinking") or "")
            elif bt == "tool_use":
                conv += len(json.dumps(blk.get("input") or ""))   # call args ≈ conv
            elif bt == "image":
                res += 2000                                       # base64 estimate/blk
    save_cache(mcache, {"size": off, "res": res, "conv": conv, "think": think,
                        "tin": tin, "tout": tout, "c_wr": c_wr, "c_rd": c_rd, "mixv6": 1,
                        "c_in": c_in, "rb": rb, "pp": pp,
                        "ids": recent_ids[-256:], "lr": lr, "lu": lu, "cur": cur})
    return res, conv, think, tin, tout, c_wr, c_rd, lr, c_in, rb


def mix_labels(counts):
    """Fixed-width glyph-tagged percentages ('▤30% ❙50% ◈20%').
    Counts may be the 5-tuple (res, conv, think, tin, tout) — ONLY the first three
    (byte buckets) participate: summing all five mixed units (bytes vs token totals)
    and diluted the percentages (regression caught live after the token-total_add).
    Zero-content buckets render blank; 1-digit values padded so widths don't jitter."""
    counts = counts[:3] if counts else None
    if not counts or sum(counts) <= 0:
        return None
    total = sum(counts)
    order = ((CYAN, "▤", counts[0]), (GREEN, "❙", counts[1]), (MAGENTA, "◈", counts[2]))
    bits = []
    for col, glyph, n in order:
        if n > 0:
            pct = round(n / total * 100)
            body = f"{pct:>2d}%" if pct > 0 else " <1%"   # present but tiny
            bits.append(f"{col}{glyph}{body}{RESET}")
    return " ".join(bits) if bits else None


def mix_segment(counts):
    """Context-composition segment: glyph-tagged percentages only (▤30% ❙50% ◈20%).
    The proportional bar was dropped — the fixed-width tagged percents carry the same
    information more precisely. Glyphs keep the color/mapping discoverable."""
    if not counts or sum(counts[:3]) <= 0:
        return None
    return mix_labels(counts)

def term_cols():
    raw = os.environ.get("COLUMNS", "0")
    try:
        return int(raw)
    except (ValueError, TypeError):
        return 0


def trim_to_fit(row, cols):
    """Drop trailing segments until the VISIBLE width fits (escape bytes don't count)."""
    while visible(row) > cols and SEP in row:
        row = row.rsplit(SEP, 1)[0] + RESET
    return row


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        d = {}
    if not isinstance(d, dict):
        d = {}

    rows_env = ROWS
    cols = term_cols()
    rows = []
    cols = term_cols()
    dgx_mtok = dgx_rate = None
    mix = _mix_counts(d)               # context composition (cheap incremental parse)
    sid = d.get("session_id") or "nosession"
    cache_path = os.path.join(CACHE_DIR, f"statusline-{sid}.json")
    d["rate_limits"] = effective_rl(cache_path, d.get("rate_limits"))  # smoothed plan state
    if rows_env >= 2:
        sample, age, up, hist = get_sample(cache_path)
        if isinstance(sample, dict):
            dgx_mtok = sample.get("dgx_cost:dgx_usd_per_mtok")   # blended $/MTok at cost
            if not isinstance(dgx_mtok, (int, float)) or dgx_mtok <= 0:
                dgx_mtok = None
            dgx_rate = sample.get("dgx_tokens:rate_mtok_month")  # basis guard input
        if (rows_env > 2 or cols == 0 or cols >= NARROW_COLS):  # responsive: known-tight terminals drop row 2
            last_turn = mix[7] if mix and len(mix) >= 8 else None   # transcript, both lanes
            rows.append(SEP.join(
                render_telemetry(sample, age, up, hist if SPARK_ON else [], last_turn)))

    win_start = claude_window_start(cache_path) if d.get("session_id") else None
    rows.insert(0, SEP.join(render_lane(d, mix, dgx_mtok, dgx_rate, win_start)))

    if cols > 0:
        rows = [trim_to_fit(r, cols) for r in rows]
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    try:
        if "--subagent" in sys.argv[1:]:
            sys.exit(main_subagent())
        sys.exit(main())
    except Exception:
        print(f"{GREY}statusline degraded{RESET}")   # never blank, never nonzero
        sys.exit(0)
