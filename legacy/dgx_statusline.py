#!/usr/bin/env python3
"""claude-dgx status line — the cockpit view (workstream 1, 2026-11-11; reviewed v2).

Wired by the `claude-dgx` launcher through `--settings '{"statusLine":{"type":"command",
...}}'`, so it exists ONLY in DGX sessions (nothing written to ~/.claude/settings.json).
Claude Code pipes session JSON to stdin on each refresh (after every assistant message
+ every refreshInterval tick); we print up to two rows:

    ◨ DGX · Sonnet 5.5 · ⎇ main · home-lab · ▰▰▰▱▱ 43%/1.0M · ♻ 94% · ▲31 ▼4 · ⏱ 12m
    ◉ r3·q0 · KV▰▱▱ 6% · »38/204t/s ▁▂▃▅▇ · ◔4.2s · ⚡1059W 66° 34¢/h · ☾ idle 2m

Row-2 legend: `»38/204t/s` = THIS session's delivered-token rate / box-wide 5-min
average (vLLM generation tokens summed over all sessions); the sparkline plots that
box-wide rate (≤16 pts, ≤90 s of history, persisted per session). The session figure
counts tokens when a stream closes, so it can legitimately read 0 mid-long-generation.

Row 1 is the session: lane badge (DGX-served Flash = cyan ◨ DGX, Anthropic Opus/Haiku
passthrough = magenta ◨ ANTH, unknown env = grey), model, git branch, project, a
green→red truecolor context thermometer, prompt-cache hit ratio, lines added/removed,
session wall time and (subscription accounts) the 5h rate-limit gauge. Lane flips live
on a mid-session `/model opus` — it compares stdin's model.id against the launcher's
LOCAL_MODEL_PREFIXES.

Row 2 is the GB300 telemetry strip, ONE VictoriaMetrics round trip per refresh (~25 ms
LAN, disk-cached DGX_SL_TTL seconds keyed by session_id, atomic writes). Throughput
history feeds a fading sparkline persisted in that same cache. Degradation ladder:
fresh → green ◉; VM briefly unreachable → yellow ◉ with last-known numbers + (~Ns) age;
>KEEP_DEAD or never seen → red ◌ DGX ?. Never an error, never blank (blank = nonzero
exit), every path ends in output + exit 0.

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
import json
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
IDLE_MINE = 15.0       # s without counter movement -> session rate is ZERO (not EMA ghost)
RL_KEEP = 1800.0       # s to keep displaying plan limits last reported by CC (no blinking)
# Which signal the sparkline plots: rate (box tok/s) | kv (GPU KV%) | ttft | mine.
# Rate is flat when the box is healthy — kv (pressure, predictive) and ttft (spiky)
# tend to carry more information; mine moves per turn.
TRACE = os.environ.get("DGX_SL_TRACE", "rate")
IDLE_AFTER = 300.0     # show '☾ idle' when DGX last got a request longer ago than this (s)
GIT_TTL = 5.0          # s between real .git/HEAD reads (docs' example pattern)
NARROW_COLS = 72       # below this, auto-drop row 2 unless DGX_SL_ROWS forces it

QUERY = (
    '{__name__=~"vllm:num_requests_running|vllm:num_requests_waiting|'
    "vllm:kv_cache_usage_perc|vllm:kv_offload_cpu_cache_usage_perc|"
    "dgx_tokens:gen_rate5m|dgx_ttft:p95_30m|dgx_preempt:rate5m|"
    "dgx_llm_last_dgx_request_timestamp_seconds|dgx_power:est_wall_watts|"
    "dgx_power:rate_usd_per_kwh|dgx_llm_session_tokens_out|"
    "dgx_cost:dgx_usd_per_mtok|"
    "vllm:prefix_cache_hits_total|vllm:prefix_cache_queries_total|"
    'DCGM_FI_DEV_POWER_USAGE|DCGM_FI_DEV_GPU_TEMP"}'
)

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
            return None, {}
        out, sess = {}, {}
        for s in payload["data"]["result"]:
            name = s["metric"].get("__name__", "")
            try:
                val = float(s["value"][1])
            except (KeyError, ValueError, IndexError):
                continue
            if name == "dgx_llm_session_tokens_out":
                lbl = s["metric"].get("session", "")
                if lbl and lbl not in sess:
                    sess[lbl] = val
                continue
            if name and name not in out:  # single-GPU/single-instance: first wins
                out[name] = val
        return (out or None), sess
    except Exception:
        return None, {}


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


def _sess_rate_from_state(st, now):
    """Displayed session rate from stored state, WITHOUT a fetch (TTL-hit / stale paths).

    Same idleness rule as the fetch path: counter stationary longer than IDLE_MINE ->
    exactly 0 (no EMA ghosts), otherwise the stored EMA. None when never measured.
    (st may be from an older cache without 'moved' -> falls back to 'ts'.)"""
    if st.get("ema") is None:
        return None
    moved = st.get("moved", st.get("ts", 0))
    return 0.0 if (now - moved) > IDLE_MINE else st["ema"]


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


def get_sample(cache_path, sid8=None):
    """TTL'd fetch w/ stale fallback.

    -> (sample|None, age_s, up_bool, spark_hist, sess_rate|None)
    sess_rate = THIS session's delivered-token rate (delta of the exporter's per-session
    output-token counter, EMA-smoothed while moving; a hard 0 once the counter has been
    stationary for IDLE_MINE seconds — no zombie EMA leftovers while the session idles;
    None when unmeasurable this refresh).
    """
    now = time.time()
    c = load_cache(cache_path)
    if c.get("fetch_ts", 0) > now - TTL:                       # fresh verdict, reuse it
        return (c.get("sample"), now - c.get("ts", 9999), bool(c.get("up")),
                c.get("hist", []), _sess_rate_from_state(c.get("sess_state") or {}, now))
    sample, sess = fetch_sample()
    entry = dict(c)                                            # preserves hist on failure
    if sample:
        # History for the sparkline: one dict per observation holding EVERY plottable
        # signal, so DGX_SL_TRACE can pick retroactively. A missing series simply omits
        # its key — never a fabricated 0 (that once drew fake cliffs to the floor).
        # Point format: {"t": unix, "v": box tok/s, "k": gpu-kv fraction,
        #                "f": ttft p95 s, "m": session delivered tok/s (instant),
        #                "p": 1 when preemptions active}
        hist = [_norm_pt(p) for p in c.get("hist", [])]
        hist = [p for p in hist if now - p.get("t", 0) < SPARK_MAX_AGE]
        if not hist or now - hist[-1]["t"] >= HIST_MIN_GAP:
            pt = {"t": now}
            for key, series in (("v", "dgx_tokens:gen_rate5m"),
                                ("k", "vllm:kv_cache_usage_perc"),
                                ("f", "dgx_ttft:p95_30m")):
                if series in sample:
                    pt[key] = sample[series]
            if sample.get("dgx_preempt:rate5m", 0) > 0.01:
                pt["p"] = 1
            hist.append(pt)

        # Per-session delivered rate from the exporter's monotonic counter. Exporter
        # restarts shrink the counter -> reset the state instead of emitting nonsense.
        # Idleness is FIRST-CLASS: 'moved' = last time the counter increased; when it
        # has been stationary > IDLE_MINE, the rate is exactly 0 — the EMA never
        # outlives real movement (fixes ghost tok/s while the session idles).
        sess_rate = None
        st = c.get("sess_state") or {}
        cur = sess.get(sid8) if (sid8 and sess) else None
        if cur is not None:
            prev = st.get("c")
            gap = now - st.get("ts", 0)
            moved = st.get("moved", st.get("ts", 0))
            if prev is None or cur < prev:
                sess_rate = None                               # first sight or restart
                moved = now
            elif cur > prev:
                if gap >= 1.0:
                    inst = (cur - prev) / gap
                    prev_ema = st.get("ema")
                    sess_rate = inst if prev_ema is None else 0.5 * inst + 0.5 * prev_ema
                    if hist and hist[-1].get("t") == now:
                        hist[-1]["m"] = inst                   # instantaneous, not EMA
                else:
                    sess_rate = st.get("ema")                  # sample gap too small
                moved = now
            else:                                              # cur == prev: no delivery
                sess_rate = st.get("ema")
            if sess_rate is not None and (now - moved) > IDLE_MINE:
                sess_rate = 0.0                                # stationary: hard zero
            entry["sess_state"] = {"c": cur, "ts": now, "ema": sess_rate, "moved": moved}
        else:
            entry["sess_state"] = None

        entry.update({"fetch_ts": now, "up": True, "ts": now, "sample": sample,
                      "hist": hist[-32:]})
        save_cache(cache_path, entry)
        return sample, 0.0, True, hist, sess_rate
    entry["fetch_ts"] = now                                    # remember we tried
    entry["up"] = False
    save_cache(cache_path, entry)
    age = now - c.get("ts", 0)
    if c.get("sample") and age < KEEP_DEAD:
        # last-known sample, stale-flagged; session rate via the same no-ghost rule
        return c["sample"], age, False, c.get("hist", []), \
            _sess_rate_from_state(c.get("sess_state") or {}, now)
    return None, age, False, [], None


# ---------------------------------------------------------------- git (cached) -----------

def git_branch(directory):
    """Branch name (or short sha) for the first .git found upward; '' when none/error."""
    try:
        d = os.path.abspath(directory or os.getcwd())
        for _ in range(6):                                     # walk up a few levels max
            head = os.path.join(d, ".git")
            if os.path.isfile(head):                           # worktree: .git is a pointer file
                with open(head) as fh:
                    first = fh.readline().strip()
                if first.startswith("gitdir:"):
                    head = os.path.normpath(os.path.join(d, first[len("gitdir:"):].strip()))
            if os.path.isfile(os.path.join(head if os.path.isdir(head) else d, "HEAD")) or \
               os.path.isfile(os.path.join(head, "HEAD")):
                with open(os.path.join(head, "HEAD")) as fh:
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
    # Stable filename (path-derived, NOT hash(): str hashes are salted per process, which
    # made every invocation mint a new cache file and the cache never hit).
    key = re.sub(r"[^A-Za-z0-9_.-]", "_", directory)[-40:] or "root"
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
    filled = int(round(pct / 100 * 10))
    bar = "".join(
        f"{truecolor(heat((i + 0.5) * 10))}▰" if i < filled else f"{GREY}▱"
        for i in range(10)) + RESET
    col = BOLDRED if pct >= 85 else (truecolor(heat(pct)) if pct > 50 else "")
    denom = f"{DIM}/{total / 1e6:.1f}M{RESET}" if total >= 1e6 else \
            (f"{DIM}/{total / 1000:.0f}K{RESET}" if total > 0 else "")
    return f"{bar} {col}{pct:.0f}%{RESET}{denom}"


def render_lane(d, vm_cache=None, mix=None, dgx_mtok=None):
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
        parts.append(f"{GREY}{os.path.basename(proj_dir)}{RESET}")
    bar = fmt_ctx(d.get("context_window") or {})
    if bar:
        parts.append(bar)
    mb = mix_segment(mix) if mix else None                 # context CONTENT micro-bar
    if mb:
        parts.append(mb)

    # Cache hit: BOTH lanes serve from a cache, but only Anthropic echoes it back in the
    # usage block CC's prompt_cache reads. vLLM reports zeros there (real DGX-lane
    # transcripts show cache_* = 0), which would render a lying "♻ 0%". So on the DGX
    # lane we show vLLM's OWN prefix-cache hit ratio (VM counters) instead, and reserve
    # CC's prompt_cache figure for the Anthropic lane where it is measured honestly.
    if on_dgx:
        if isinstance(vm_cache, (int, float)) and vm_cache >= 0:
            parts.append(f"{CYAN}♻{RESET} {vm_cache * 100:.0f}%")
    else:
        hr = (d.get("prompt_cache") or {}).get("hit_ratio")
        if isinstance(hr, (int, float)):
            parts.append(f"{CYAN}♻{RESET} {hr * 100:.0f}%")

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
    for label, key in (("5h", "five_hour"), ("7d", "seven_day")):
        w = rl.get(key) or {}
        pct = w.get("used_percentage")
        if isinstance(pct, (int, float)):
            shown.append((label, min(max(pct, 0.0), 100.0), w.get("resets_at")))
    if shown:
        binding = max(shown, key=lambda t: t[1])[0]
        bits = []
        for label, pct, reset in shown:
            col = RED if pct > 90 else YELLOW if pct > 70 else GREY
            seg = f"{col}{label}{pct:.0f}%{RESET}"
            if label == binding and pct > 70 and isinstance(reset, (int, float)):
                rem = reset - time.time()
                if 0 < rem < 86400:                            # sane window: countdown useful
                    seg += (" " + (f"{col}->{int(rem // 3600)}h{int((rem % 3600) // 60):02d}m{RESET}"
                                   if rem >= 3600 else f"{col}->{int(rem // 60)}m{RESET}"))
            bits.append(seg)
        parts.append(" ".join(bits))

    cost = d.get("cost") or {}
    la, lr = cost.get("total_lines_added") or 0, cost.get("total_lines_removed") or 0
    if la or lr:
        parts.append(f"{GREEN}▲{la}{RESET}{DIM}/{RESET}{RED}▼{lr}{RESET}")

    dur = cost.get("total_duration_ms")
    if isinstance(dur, (int, float)) and dur > 60000:          # show timer after 1 minute
        mins = int(dur // 60000)
        parts.append(f"{GREY}⏱ {mins // 60}h{mins % 100:02d}m{RESET}" if mins >= 60
                     else f"{GREY}⏱ {mins}m{RESET}")

    # Session token totals + cost. Totals prefer CC's own stdin figures and fall back to
    # our transcript accumulation; cost is CC's list-price computation — on the DGX lane
    # we add the electricity-equivalent for the same tokens (dgx_cost:dgx_usd_per_mtok),
    # because $0.09-at-cost vs $X-at-list IS the displacement story this rig exists for.
    cw2 = d.get("context_window") or {}
    tin = cw2.get("total_input_tokens")
    tout = cw2.get("total_output_tokens")
    c_wr = c_rd = None
    if mix and len(mix) >= 7:                                  # usage split (transcript)
        c_wr, c_rd = mix[5], mix[6]
        if not (isinstance(tin, (int, float)) and isinstance(tout, (int, float))):
            tin, tout = mix[3], mix[4]                         # transcript-derived fallback
    have_t = isinstance(tin, (int, float)) or isinstance(tout, (int, float))
    if have_t and ((tin or 0) > 0 or (tout or 0) > 0):
        parts.append(f"{GREY}↑{RESET}{WHITE}{_fmt_tokens(tin or 0)}{RESET}"
                     f"{GREY} ↓{RESET}{WHITE}{_fmt_tokens(tout or 0)}{RESET}")
    # Usage split: ⟳ cache-read volume (cheap, 0.1x) and ✍ cache-write volume (premium,
    # 1.25x). Only meaningful where the lane reports the split (Anthropic does; vLLM's
    # zeros hide them automatically on the DGX lane).
    if isinstance(c_rd, (int, float)) and c_rd > 0:
        parts.append(f"{CYAN}⟳{_fmt_tokens(c_rd)}{RESET}")
    if isinstance(c_wr, (int, float)) and c_wr > 0:
        parts.append(f"{YELLOW}✍{_fmt_tokens(c_wr)}{RESET}")
    usd = cost.get("total_cost_usd")
    if isinstance(usd, (int, float)) and usd > 0:
        col = YELLOW if usd >= 5 else WHITE if usd >= 1 else GREY
        cseg = f"{col}${usd:.2f}{RESET}"
        tot = (tin or 0) + (tout or 0)
        if on_dgx and isinstance(dgx_mtok, (int, float)) and dgx_mtok > 0 and tot > 0:
            eq = tot * dgx_mtok / 1e6
            if eq >= 0.005:                                    # skip sub-half-cent noise
                cseg += f"{GREY} ⛏{eq:.2f}{RESET}"
        parts.append(cseg)
    return parts


# ---------------------------------------------------------------- row 2: DGX telemetry ---

TRACE_KEYS = {"rate": "v", "kv": "k", "ttft": "f", "mine": "m"}


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
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.15 or abs(hi) * 0.15 or 1.0   # never peg bars to top/bottom
    lo, hi = lo - pad, hi + pad
    span = hi - lo

    def idx(v):
        j = (v - lo) / span * (len(SPARK) - 1)     # span>0 by construction
        return int(min(max(j, 0.0), len(SPARK) - 1) + 0.5)

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


def render_telemetry_fields(m, stale, hist, sess_rate=None):
    dot = YELLOW if stale else GREEN
    parts = [f"{dot}◉{RESET}"]

    r = m.get("vllm:num_requests_running")
    if r is not None:
        q = m.get("vllm:num_requests_waiting", 0)
        busy = (r and q) or m.get("dgx_preempt:rate5m", 0) > 0.01
        parts.append(f"{YELLOW if busy else GREEN}r{r:.0f}·q{q:.0f}{RESET}")

    kv = m.get("vllm:kv_cache_usage_perc", 0) * 100
    kv_host = m.get("vllm:kv_offload_cpu_cache_usage_perc", 0) * 100
    n = max(min(int(kv / 20), 3), 0)
    parts.append(f"{YELLOW if kv > 80 else CYAN}KV{'▰' * n}{'▱' * (3 - n)} {kv:.0f}%{RESET}"
                 + (f"{DIM}+host {kv_host:.0f}%{RESET}" if kv_host > 0.5 else ""))

    rate = m.get("dgx_tokens:gen_rate5m")
    if rate is not None:
        # »mine/box t/s: this session's delivered-token rate over the box-wide 5-min
        # average. Mine is delivered tokens (the exporter counts on stream close), so it
        # can legitimately read 0 during one long uninterrupted generation.
        if stale:
            body = f"{GREY}»{rate:>3.0f}t/s{RESET}"
        elif sess_rate is not None:
            body = f"{BOLD}{WHITE}{sess_rate:>3.0f}{RESET}{GREY}/{rate:>3.0f}t/s{RESET}"
        else:
            body = f"{WHITE}»{rate:>3.0f}t/s{RESET}"
        sp = "" if stale or not SPARK_ON else sparkline(hist)
        parts.append((body + f" {sp}").rstrip())

    ttft = m.get("dgx_ttft:p95_30m")
    if ttft is not None:
        parts.append(f"{YELLOW if ttft > 8 else GREY}◔{ttft:.1f}s{RESET}")

    w = m.get("DCGM_FI_DEV_POWER_USAGE")
    if w is not None:
        t = m.get("DCGM_FI_DEV_GPU_TEMP")
        wc = RED if w > 1500 else YELLOW if w > 1200 else WHITE
        txt = f"{wc}⚡{w:.0f}W{RESET}" + (f"{GREY} {t:.0f}°{RESET}" if t is not None else "")
        wall, rate_c = m.get("dgx_power:est_wall_watts"), m.get("dgx_power:rate_usd_per_kwh")
        if wall and rate_c:                                    # whole-box estimate × tariff
            cents = wall / 1000 * rate_c * 100
            txt += f"{GREY} {cents:.0f}¢/h{RESET}"
        parts.append(txt)

    # DGX-lane recency only: Opus/Haiku passthrough also writes ledger events, and
    # the any-event timestamp let Anthropic traffic mask a genuinely idle DGX.
    last = m.get("dgx_llm_last_dgx_request_timestamp_seconds")
    if last and last > 0 and time.time() - last > IDLE_AFTER and (m.get("vllm:num_requests_running") or 0) < 1:
        idle_min = int((time.time() - last) // 60)
        parts.append(f"{CYAN}☾ idle {idle_min}m{RESET}")
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
            bits.append(f"{GREY}{model}{RESET}")
        tok = task.get("tokenCount")
        if isinstance(tok, (int, float)) and tok > 0:
            bits.append(f"{CYAN}{_fmt_tokens(tok)} tok{RESET}")
        # Context window of the subagent, as %, when CC reports both sizes.
        cw = task.get("contextWindowSize")
        start = task.get("startTime")
        if isinstance(start, (int, float)) and start > 0:
            secs = max(now_ms - start, 0) / 1000
            bits.append(f"{GREY}{int(secs // 60):02d}:{int(secs % 60):02d}{RESET}")
        ctxp = task.get("contextUsedPercentage")            # not in docs today; future-proof
        if isinstance(ctxp, (int, float)):
            bits.append(f"{truecolor(heat(ctxp))}◍{ctxp:.0f}%{RESET}")
        st = task.get("status")
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
    need_reset = False
    for key in ("tin", "c_wr"):                    # fields introduced post-launch
        if key not in c and off > 0:
            need_reset = True
    if need_reset or size < off:
        off, res, conv, think, tin, tout, c_wr, c_rd = 0, 0, 0, 0, 0, 0, 0, 0
    if size == off:
        return res, conv, think, tin, tout, c_wr, c_rd
    try:
        with open(path, "rb") as fh:
            fh.seek(off)
            blob = fh.read(min(size - off, _READ_CAP))
    except OSError:
        return res, conv, think, tin, tout, c_wr, c_rd
    cut = blob.rfind(b"\n")                                    # complete lines only
    if cut < 0:
        return res, conv, think, tin, tout, c_wr, c_rd
    off += cut + 1
    for line in blob[:cut].splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue                                           # torn/partial line: skip
        msg = e.get("message") or {}
        u = msg.get("usage")
        if isinstance(u, dict):                                # true per-call usage
            _i = u.get("input_tokens") or 0
            _w = u.get("cache_creation_input_tokens") or 0
            _r = u.get("cache_read_input_tokens") or 0
            tin += _i + _w + _r
            c_wr += _w
            c_rd += _r
            tout += u.get("output_tokens") or 0
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
                n = len(inner) if isinstance(inner, str) else \
                    len(json.dumps(inner)) if inner is not None else 0
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
                        "tin": tin, "tout": tout, "c_wr": c_wr, "c_rd": c_rd})
    return res, conv, think, tin, tout, c_wr, c_rd


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
    vm_cache = None
    dgx_mtok = None
    mix = _mix_counts(d)               # context composition (cheap incremental parse)
    sid = d.get("session_id") or "nosession"
    cache_path = os.path.join(CACHE_DIR, f"statusline-{sid}.json")
    d["rate_limits"] = effective_rl(cache_path, d.get("rate_limits"))  # smoothed plan state
    if rows_env >= 2:
        sample, age, up, hist, sess_rate = get_sample(cache_path, sid[:8])
        if isinstance(sample, dict):
            h, q = (sample.get("vllm:prefix_cache_hits_total"),
                    sample.get("vllm:prefix_cache_queries_total"))
            if isinstance(h, (int, float)) and isinstance(q, (int, float)) and q > 0:
                vm_cache = h / q
            dgx_mtok = sample.get("dgx_cost:dgx_usd_per_mtok")   # blended $/MTok at cost
            if not isinstance(dgx_mtok, (int, float)) or dgx_mtok <= 0:
                dgx_mtok = None
        if (rows_env > 2 or cols == 0 or cols >= NARROW_COLS):  # responsive: known-tight terminals drop row 2
            rows.append(SEP.join(
                render_telemetry(sample, age, up, hist if SPARK_ON else [], sess_rate)))

    rows.insert(0, SEP.join(render_lane(d, vm_cache, mix, dgx_mtok)))

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
