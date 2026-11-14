# Pass 3: Behavioral Contracts — hylo-legacy

There are **no test files** in `legacy/`. Confidence scale used here:
- **HIGH-R** — read in code AND the review doc records the rule as verified with cases (`docs/STATUSLINE-REVIEW-2026-11-13.md`, "N/N pass"). Not an in-tree test; the Go port must turn each into a table test.
- **MEDIUM** — read directly in code, no recorded verification.
- **LOW** — inferred (behavior depends on an external system or on code paths not observable statically).

Policy: every BC cites legacy `file:line`; parity (D4) means the Go port reproduces these, quirks included,
until a deliberate post-parity change. Quirks that look like bugs are flagged **[QUIRK]** — preserve for parity,
list for the owner. Format below: one row per BC: contract (pre -> post), edges/errors, evidence, confidence.

Out of scope (one line each): `--subagent` panel rows (`dgx_statusline.py:837-936,1240-1241`) — removed in Claude Code 2.1.323; `opus_router.py` visible mode (`claude-dgx:85-96,102`) — D6.

ANSI constants used in outputs (`dgx_statusline.py:127-134`): `RESET \033[0m`, `DIM \033[2m`, `BOLD \033[1m`, `SEP = DIM+" · "+RESET`, pills `\033[106;30;1m` (DGX) / `\033[105;30;1m` (ANTH) / `\033[100;37;1m` (none), `WHITE 97`, `CYAN 36`, `GREEN 32`, `YELLOW 33`, `RED 31`, `GREY 90`, `MAGENTA 35`, `BOLDRED 1;91`.

---

## A. Status line (`dgx_statusline.py`) — 53 BCs

### A1. Process contract

| ID | Contract | Edges / errors | Evidence | Conf |
|---|---|---|---|---|
| BC-SL-001 | Any exception raised inside `main()` prints exactly `GREY+"statusline degraded"+RESET` and exits 0 | **[QUIRK]** exceptions at **import time** are NOT covered: non-numeric `DGX_SL_TTL` (`float`) or `DGX_SL_ROWS` (`int`) raise before the guard -> traceback, exit 1, blank line | `:1238-1245`, `:74-75` | MEDIUM |
| BC-SL-002 | stdin not JSON, or JSON not an object -> treated as `{}` (still renders row 1 `◨ ?` + `?` model) | type confusion inside fields (e.g. `model` is a string) raises -> BC-SL-001 | `:1201-1206`, `:441` | MEDIUM |
| BC-SL-003 | Output = rows joined by `\n`, printed with trailing newline; row 1 always first | row 2 present iff `DGX_SL_ROWS >= 2` AND (`ROWS > 2` OR `cols == 0` OR `cols >= 72`) | `:1217-1234` | HIGH-R |
| BC-SL-004 | When `cols > 0`, each row is trimmed by dropping trailing `SEP`-delimited segments until visible width ≤ cols, appending `RESET` after each cut | visible width = **code-point count** after stripping `\033\[[0-9;]*m` (wide glyphs count 1); a single over-wide segment is left as is | `:151-153,1193-1197,1232-1233` | MEDIUM |
| BC-SL-005 | `cols` = `int(COLUMNS)`; absent or non-int -> 0 (no trimming, row 2 shown) | `" 80"` parses (Python `int` strips whitespace) | `:1185-1190` | MEDIUM |
| BC-SL-053 | The VM fetch (and its cache update) happens whenever `ROWS >= 2`, even if row 2 is then hidden for width; it feeds `⛏` | `dgx_mtok` <= 0 or non-number -> None | `:1217-1224` | MEDIUM |

### A2. Row 1 widgets (order: pill, model, branch, project, thermometer, composition, ♻, limits, lines, timer, tokens, cost — `:453-636`)

| ID | Contract | Edges / errors | Evidence | Conf |
|---|---|---|---|---|
| BC-SL-006 | Lane pill: prefixes = comma-split, stripped, non-empty `LOCAL_MODEL_PREFIXES` (**default empty**); `on_dgx` = any `model.id.startswith(p)` when prefixes and id non-empty else None. DGX -> `PILL_DGX+" ◨ DGX "+RESET`; `on_dgx is False` and id -> `PILL_ANTH+" ◨ ANTH "`; else `PILL_NONE+" ◨ ? "` | case-sensitive; server-tool override of the proxy not reflected | `:444-449` | HIGH-R (#1, 10 cases) |
| BC-SL-007 | Model label = `WHITE + (display_name or id or "?") + RESET` | empty strings fall through | `:442,453` | HIGH-R (#2) |
| BC-SL-008 | Project dir = `workspace.project_dir` or `workspace.current_dir` or `cwd` or `""`; label = `basename(normpath(dir))` or `normpath(dir)` (root -> `/`), GREY; omitted when dir empty | trailing slash ignored | `:452,458-462` | HIGH-R (#4, 7 cases) |
| BC-SL-009 | Branch: from `abspath(dir)` walk to filesystem root; a dir counts only if `.git` is a dir, or a file whose first line starts `gitdir:` (relative path joined + normpath), AND that gitdir has a `HEAD` file; `ref: refs/heads/X` -> `X`; else first 7 chars of HEAD content; none -> `""` | any exception -> `""`; stray plain `HEAD` does not stop the walk | `:364-396` | HIGH-R (#3, 10 layouts) |
| BC-SL-010 | Branch segment: disabled when `DGX_SL_GIT == "0"`; cache `statusline-git-<sha1(dir utf-8,replace)[:16]>.json`; recompute when `now - ts > 5` or no `branch`; render `GREY+"⎇ "+b+RESET`, omitted when empty | branch emitted before project label | `:399-413,455-457` | HIGH-R (#3.4) |
| BC-SL-011 | Thermometer: only when `used_percentage` is int/float; clamp 0..100; `filled = min(int(pct/10+0.5),10)`; cell i filled = `truecolor(heat((i+0.5)*10))+"▰"` else `GREY+"▱"`, then RESET; number color BOLDRED if pct ≥ 85, `truecolor(heat(pct))` if > 50, else none; text `f"{pct:.0f}%"`; denominator `DIM+"/"+f"{total/1e6:.1f}M"` if total ≥ 1e6, `f"/{total/1000:.0f}K"` if > 0, else none | null before first call -> segment omitted; `heat` = HSV(h=(1-p/100)*0.22, s .85, v .80) -> `int(c*255)` | `:144-148,418-437` | HIGH-R (#5) |
| BC-SL-012 | Composition: only when mix present and `sum(res,conv,think) > 0`; per bucket with n>0: `pct = round(n/total*100)` (**banker's rounding**), body `f"{pct:>2d}%"` or `" <1%"` when pct==0; glyphs CYAN `▤`, GREEN `❙`, MAGENTA `◈`; joined by one space | zero buckets omitted | `:1157-1183,466-468` | HIGH-R (#6) |
| BC-SL-013 | Cache hit: when `prompt_cache.hit_ratio` is a number -> `CYAN+"♻"+RESET+" "+f"{clamp(hr,0,1)*100:.0f}%"` | both lanes | `:477-479` | HIGH-R (#7) |
| BC-SL-014 | Limits hidden entirely when any prefix with `rstrip("*")` in {`claude`, `claude-`} (reroute-all) | — | `:487-489` | MEDIUM |
| BC-SL-015 | A window with numeric `resets_at <= now` is treated as unreported | applies to smoothed values too | `:505-507` | HIGH-R (#12.1) |
| BC-SL-016 | Window color: `elapsed = 1 - rem/length`; if `0.10 <= elapsed <= 1.0`: `proj = pct/elapsed`, RED if proj > 100, YELLOW if proj ≥ 80, else GREY; otherwise absolute: RED if pct > 90, YELLOW if pct > 70, else GREY; text `f"{label}{pct:.0f}%"` (labels `5h`, `7d`), pct clamped 0..100 | no `resets_at` -> absolute bands; windows joined by two spaces; unreported windows omitted | `:501-522,532` | HIGH-R (#12 revisit, 7 cases) |
| BC-SL-017 | Countdown appended `" "+col+"->"+cd` when `0 < rem <= length*1.15`: rem ≥ 86400 -> `f"{d}d{h:02d}h"`; ≥ 3600 -> `f"{h}h{m:02d}m"`; else `f"{m}m"` (floor divisions) | `->0m` possible for rem < 60 | `:523-530` | HIGH-R |
| BC-SL-018 | Smoothing: non-empty dict `rate_limits` on stdin is stored (`rl`, `rl_ts=now`) and used; otherwise cached `rl` is used if `now - rl_ts < 1800`, else None | stdin `{}` counts as absent | `:298-312,1216` | HIGH-R |
| BC-SL-019 | Lines: shown when added or removed truthy: `GREEN+"▲"+fmt(la)+RESET+DIM+"/"+RESET+RED+"▼"+fmt(lr)+RESET`; `fmt`: `int(n)`; ≥ 1,000,000 -> `f"{n/1e6:.1f}M"`; ≥ 10,000 -> `f"{n//1000}k"`; else `str(n)`; non-int-able -> `"?"` | 0/0 hidden | `:534-537,849-860` | HIGH-R (#8, 6 cases) |
| BC-SL-020 | Timer: when `total_duration_ms > 60000`: `GREY+"⏱ "+hm(dur)+RESET`; `hm`: `mins=int(ms//60000)`; ≥ 60 -> `f"{mins//60}h{mins%60:02d}m"` else `f"{mins}m"` | hours unbounded (`25h00m`) | `:539-549` | HIGH-R (#9, 12 cases) |
| BC-SL-021 | API time appended `DIM+"·"+hm(api)+RESET` when `total_api_duration_ms >= 60000`; not capped at elapsed | — | `:550-553` | HIGH-R (6 cases) |
| BC-SL-022 | `⌂` appended when `win_start` numeric and `(now-win_start)*1000 - dur >= 300000`: wm ≥ 1440 -> `f"{wm//1440}d{(wm%1440)//60:02d}h"` else `hm(win_ms)`; text `GREY+" ⌂"+txt+RESET` | only inside the timer segment (needs dur > 60 s) | `:557-562` | HIGH-R |
| BC-SL-023 | Window start: cached `proc_start` reused; else walk ≤ 6 ancestors from `getppid()` with `ps -o ppid=,comm=,lstart= -p PID` (timeout 1 s); first whose `basename(comm) == "claude"` -> `time.mktime(strptime(lstart, "%a %b %d %H:%M:%S %Y"))`, cached; pid ≤ 1 or empty output -> None | only attempted when `session_id` present; failures not cached (re-walk next refresh); comm with spaces breaks `split(None,2)`; local TZ + C-locale month names | `:265-295,1229` | HIGH-R (owner verified) / LOW on non-macOS |
| BC-SL-024 | Tokens: shown when `tin` or `tout` numeric and either > 0: `GREY+"↑"+RESET+WHITE+c(tin)+RESET`; inner parts (only > 0): `WHITE in<c>`, `YELLOW ✍<c>`, `CYAN ⟳<c>`; brackets `DIM[`…`DIM]` only when ≥ 2 parts; then `GREY+" ↓"+RESET+WHITE+c(tout)`; then `" "+DIM+YELLOW+"↻"+f"{rb:.0f}"` when rb > 0. `c()`: ≥ 1e6 -> `.1f`+`M`; ≥ 1000 -> `.0f`+`k`; else `.0f` | values from transcript, never stdin | `:574-600,863-873` | HIGH-R (#10 revisit) |
| BC-SL-025 | `$`: when `total_cost_usd` > 0: color GREY if < 1; else with thresholds RED ≥ p95, YELLOW ≥ p75, else WHITE; cold start YELLOW ≥ 25 else WHITE; text `f"${usd:.2f}"` | lane None (no prefixes / no id) -> no record, cold-start colors | `:601-616` | HIGH-R (6 color cases) |
| BC-SL-026 | `$/h` appended when api ≥ 300000 ms: `r = usd/(api/3.6e6)`, color RED ≥ p95 / YELLOW ≥ p75 / GREY, GREY at cold start; text `f" ${r:.1f}/h"` | — | `:622-625` | HIGH-R |
| BC-SL-027 | `⛏` (DGX lane only, `tin+tout > 0`): basis ok iff `dgx_tokens:rate_mtok_month >= 30.4` and `dgx_cost:dgx_usd_per_mtok > 0`; not ok -> `GREY+" ⛏n/a"`; ok -> `eq = tot*mtok/1e6`, shown `f" ⛏{eq:.2f}"` only if eq ≥ 0.005 | ROWS=1 -> no sample -> always `n/a` | `:626-635` | HIGH-R (#11, 6 cases) |
| BC-SL-028 | `record_cost(sid, lane, usd, api_ms)`: requires sid, lane in {dgx, anth}, numeric usd; skip if existing entry `src=="cc"` and `now-ts < 60`; else write `{lane, usd: round(usd,4), api_ms or None, ts: now, src: "cc"}` atomically | concurrent sessions may lose an update (repaired next minute) | `:224-237` | MEDIUM |
| BC-SL-029 | `cost_thresholds(lane, sid)`: over entries ≠ sid, same lane, `now - ts <= 30 d`, numeric usd ≥ 1: collect usd; collect rate `usd/(api/3.6e6)` when api ≥ 300000 (src cc) or ≥ 1800000 (else); each list: < 10 -> None, else sorted `v[int(0.75*(n-1))], v[int(0.95*(n-1))]` | index-floor percentile (no interpolation) | `:240-262` | HIGH-R |

### A3. Transcript parser (`_mix_counts`, `:999-1154`)

| ID | Contract | Edges / errors | Evidence | Conf |
|---|---|---|---|---|
| BC-SL-030 | No `transcript_path`, not a file, or stat error -> None (composition, tokens, »mine all absent) | — | `:1009-1015` | MEDIUM |
| BC-SL-031 | Cache `statusline-mix-<re.sub([^A-Za-z0-9_-],"_",sid)[:40]>.json`; reset all accumulators and the id memory when file shrank (`size < off`) or any of `tin`, `c_wr`, `mixv6` missing with off > 0; return cached tuple untouched when `size == off` | reset happens before the size check | `:1016-1040` | HIGH-R |
| BC-SL-032 | Read from `off` up to 524,288 bytes; while the blob has no `\n` and EOF not reached, keep reading 524,288-byte chunks (finish one long line); parse only up to the last `\n`; advance `off` past it; no `\n` at all -> return cached values (offset unchanged) | read OSError -> cached values | `:1041-1058` | HIGH-R (#6.5) |
| BC-SL-033 | Lines split with `bytes.splitlines()` (`\n`, `\r\n`, `\r`); each `json.loads`; failure -> line skipped | invalid UTF-8 raises in `json.loads(bytes)` -> skipped | `:1059-1063` | MEDIUM |
| BC-SL-034 | Usage counted once per `message.id`: ids remembered in a list carried across refreshes (last 256 saved) plus a set; a repeated id's usage ignored; usage without id always counted | id memory cleared on reset | `:1033-1034,1096-1103,1153` | HIGH-R (#10.2) |
| BC-SL-035 | Per counted usage: `tin += in+w+r; c_in += in; c_wr += w; c_rd += r; tout += out` (missing/None -> 0) | totals NOT reset at compaction | `:1104-1112` | HIGH-R (in+✍+⟳ = ↑ on 3 transcripts) |
| BC-SL-036 | Rebuild: `prompt = in+w+r`; if `pp` not None and `w - max(0, prompt-pp) > 20000` -> `rb += 1`; `pp = prompt` | `pp=None` after compaction/reset (first call never a rebuild) | `:1116-1119,1094` | HIGH-R (#10 revisit) |
| BC-SL-037 | `type=="system"` and `subtype=="compact_boundary"`: `res=conv=think=0`, `pp=None`, rest of the line skipped (the turn machine already ran for this line) | — | `:1088-1095` | HIGH-R (#6.1) |
| BC-SL-038 | Composition per line: content str -> `conv += len(str)` (code points); list blocks: `tool_result` str -> `len`; list -> sum(2000 for `type=="image"` dict items else `len(json.dumps(item))`); other non-None -> `len(json.dumps(x))`; `text` -> conv += len(text); `thinking` -> think += len(thinking); `tool_use` -> conv += `len(json.dumps(input or ""))`; `image` -> res += 2000 | `json.dumps` = Python defaults (ASCII-escaped, `", "`/`": "` separators) — **byte-parity hazard**; empty `input {}` counts `len('""')` = 2 | `:1120-1149` | HIGH-R (#6.3) |
| BC-SL-039 | Last-turn rate: for lines with parseable `timestamp`: assistant+id same as `cur` -> `t1 = ts`; assistant+new id -> finish `cur`, start `{id, t0: lu, t1: ts, out: usage.output_tokens or 0}`; user -> if content is not a list containing a `tool_result` block: finish + `cur=None`; always `lu = ts`; system -> finish + `cur=None`. Finish: keep previous `lr` unless `t0` set, `out>0`, `0 < span <= 4*out/15`; then `lr = [out/span, out < 200]` | `out` is taken from the FIRST line of the message; an unfinished `cur` at parse end is persisted, not finished; timestamps without offset are parsed as local time | `:988-996,1064-1087` | HIGH-R (#16, replay) |

### A4. Row 2 telemetry (`:315-359,640-835`)

| ID | Contract | Edges / errors | Evidence | Conf |
|---|---|---|---|---|
| BC-SL-040 | `fetch_sample`: GET `VM_URL/api/v1/query?query=quote(QUERY, safe='')` without env proxies, timeout 1.5 s; non-`success` -> None; map `__name__` -> float(value[1]) first-wins; `up` -> `up:<job>`; empty -> None; any exception -> None | `float("NaN")` accepted | `:158-187` | HIGH-R (#13) |
| BC-SL-041 | `get_sample`: if `fetch_ts > now - TTL` return cached `(sample, now - ts (default 9999), bool(up), hist)`; else fetch: success -> append point, save `{fetch_ts, up:True, ts, sample, hist[-32:]}`, return age 0; failure -> save `fetch_ts=now, up=False` (old sample kept in file), return last sample with age if `age < 300`, else `(None, age, False, [])` | **[QUIRK]** the cached branch does not apply KEEP_DEAD: within TTL after a failed fetch an over-300 s sample is rendered stale instead of `◌ DGX ?` | `:315-359` | MEDIUM |
| BC-SL-042 | History point: drop points older than 90 s; append only if empty or last point ≥ 2 s old; keys `v` (gen_rate1m, fallback gen_rate5m), `k`, `f`, `p:1` if preempt rate > 0 | legacy list points normalized | `:335-350` | HIGH-R (#17) |
| BC-SL-043 | Ladder: no sample -> `[RED+"◌ DGX ?"+RESET]`; not up or age > 15 -> fields(stale) + `DIM+f"(~{age:.0f}s old)"` if age > 0; else fields(fresh) | — | `:693-702` | HIGH-R |
| BC-SL-044 | Health dot: `vLLM down` if `up:vllm == 0` or (no `up:vllm` and no `vllm:*` key); else `LMCache down` if `vllm:lmcache_mp_lookup_duration_seconds_count` present and `up:lmcache == 0`; down -> `RED+"◉ "+state`; else YELLOW (stale) / GREEN `◉` | — | `:705-730` | HIGH-R (#13, 6 cases) |
| BC-SL-045 | Queue: when `num_requests_running` present: `q` default 0; YELLOW if q > 0 or preempt rate5m > 0 else GREEN; `f"r{r:.0f}·q{q:.0f}"` | — | `:732-741` | HIGH-R (#14) |
| BC-SL-046 | KV: when `kv_cache_usage_perc` numeric: kv = clamp(x*100); `n = min(ceil(kv/25),4)`; YELLOW if host share > 5 else CYAN; `"KV"+"▰"*n+"▱"*(4-n)+f" {kv:.0f}%"`; plus `DIM+f" ↺host {hs:.0f}%"` when host share > 0.5 | hidden when series missing | `:754-763` | HIGH-R (#15, 11 cases) |
| BC-SL-047 | Throughput: `»` segment when last-turn rate numeric: dim -> GREY value, else BOLD+WHITE, `f"{rate:.0f}"`, `GREY»`…`GREYt/s`; `▣` segment when box rate present: value GREY if stale else WHITE, then `" "+sparkline` unless stale or spark off, right-stripped | — | `:772-785` | HIGH-R (#16, 6 cases) |
| BC-SL-048 | Sparkline: trace key from `DGX_SL_TRACE` (unknown -> `v`); last 12 points with the key; < 2 -> `""`; `top` = 1.0 for `k` else `max(max(vals), floor)` (floors v 1.0, f 0.1, else 1e-9); `idx = int(min(max(v,0)/top*7, 7)+0.5)`; trail cells amber `(220,170,60)` if `p` else `(70,170,190)*fade`, `fade = 0.55+0.45*i/max(n-2,1)` with `int()` per channel; head YELLOW if `p` else truecolor `(140,235,255)`; ends RESET | glyphs `▁▂▃▄▅▆▇█` | `:644-690` | HIGH-R |
| BC-SL-049 | TTFT: numeric and not NaN: `val = f"{t:.0f}s"` if t ≥ 10 else `f"{t:.1f}s"`; if `ttft_n30m` numeric < 20 -> `GREY+"◔max "+val`; else YELLOW if t > 8 else GREY `◔`+val | — | `:792-799` | HIGH-R (#18, 8 cases) |
| BC-SL-050 | Power: when GPU watts present: `WHITE+f"⚡{w:.0f}W"`; if wall truthy: `GREY·` + (RED > 1520, YELLOW > 1280, else WHITE) `f"{wall:.0f}W"`; temp `GREY+f" {t:.0f}°"` if present; if wall and rate truthy: `GREY+f" {wall/1000*rate*100:.0f}¢/h"` | wall 0 treated as absent | `:801-820` | HIGH-R (#19) |
| BC-SL-051 | Idle: when `last_dgx_request_ts` truthy > 0, `now - last > 300`, and running (default 0) < 1: `idle_min = int((now-last)//60)` -> `d..h` ≥ 1440, `h..m` ≥ 60, else `m`; `CYAN+"☾ idle "+age` | — | `:824-834` | HIGH-R (#20, 7 cases) |
| BC-SL-052 | Cache I/O: `load_cache` -> `{}` on any error; `save_cache` -> mkdir, `mkstemp` in CACHE_DIR with prefix `<basename>.`, `json.dump`, `os.replace`; all errors swallowed | session cache filename uses the **raw** `session_id` (no sanitizing, `:1215`) unlike the mix cache | `:190-206` | MEDIUM |

---

## B. Proxy (`dgx_proxy.py`) — 31 BCs

| ID | Contract | Edges / errors | Evidence | Conf |
|---|---|---|---|---|
| BC-PX-001 | Request to host `bridge.claudeusercontent.com` with `upgrade: websocket` (case-insensitive value) -> ledger `bridge_ws_connect{host}`; flow untouched | — | `:100-102` | MEDIUM |
| BC-PX-002 | Any request whose host is not `api.anthropic.com` or whose path does not start with `/v1/messages` passes through untouched (no ledger) | prefix match: `/v1/messages/count_tokens` and `/v1/messages?…` are in scope | `:103-104` | MEDIUM |
| BC-PX-003 | Body not JSON -> decision note `unparseable /v1/messages body, passing through to anthropic`, passthrough; JSON non-object -> silent passthrough | no ledger event for the request; reply still logged as `anth_reply` with empty attribution | `:105-111` | MEDIUM |
| BC-PX-004 | Attribution stash built for both lanes from headers `X-DGX-Project`, `X-DGX-User`, `X-Claude-Code-Session-Id`, body `metadata.user_id`, `model` (`""` default), `req_bytes=len(text)`, `path` sans query; `_t0 = now` | — | `:112-128` | MEDIUM |
| BC-PX-005 | `Accept-Encoding: identity` forced on **both** lanes (so the SSE tap sees plain text) | modifies Anthropic-lane requests despite "untouched" docstring | `:131,166` | MEDIUM |
| BC-PX-006 | Model not starting with any prefix (proxy default prefix `claude-sonnet`) -> `lane="anthropic"`, ledger `anth_request`, note `-> anthropic (<model>)`, passthrough | empty model -> Anthropic | `:132-136,85-87` | HIGH-R (9,927 requests consistent, #1) |
| BC-PX-007 | Prefix model whose `tools[].type` starts with `web_search_`, `web_fetch_` or `code_execution_` -> `lane="anthropic-server-tools"`, ledger `anth_request`, note `-> anthropic (<model> declares a server tool)` | `type` coerced with `str()` | `:137-141,459-464` | MEDIUM |
| BC-PX-008 | DGX route: `attrib = copy(_attrib) + model_served=req.model` (pre-rewrite); `normalize_for_dgx`; set `model = DGX_SERVED_MODEL` if non-empty and different; re-serialize with `json.dumps(req)` only if anything changed | re-serialization changes bytes (Python separators, ASCII escaping) | `:143-150` | MEDIUM |
| BC-PX-009 | DGX route: ledger `dgx_request`; headers `X-DGX-Project = project or "unknown"`, `X-DGX-User = user or "unknown"`, `X-DGX-Session` only if session | — | `:152-159` | MEDIUM |
| BC-PX-010 | DGX route: scheme/host/port from `DGX_UPSTREAM` (port default 80), `Authorization: Bearer <first read of key file, stripped, cached for process>`, `anthropic-beta` removed, note `-> DGX (<model>)` | missing key file raises inside the hook (mitmproxy-level error; outcome LOW); `x-api-key` and other `anthropic-*` headers are forwarded to the backend | `:79-95,161-167` | MEDIUM |
| BC-PX-011 | Normalization: every dict tool without `input_schema` gets `{"type":"object","properties":{}}` (marks changed) | — | `:480-485` | MEDIUM |
| BC-PX-012 | Normalization: per message with list content, keep blocks whose type is in the DGX set or has no type; `tool_addition` with name+definition -> add/replace in `by_name` (new names appended to order); `tool_removal` -> remove name; others -> drop, note once per type per process `dropping unknown content block type for DGX: <t> keys=[…]`; emptied content -> `[{"type":"text","text":"(tools updated)"}]`; if changed: `tools = [by_name[n] for n in unique(order) if n in by_name]` | name lookup order: `tool.definition.name`, `tool.name`, `block.name`, `block.tool_name`; tools without a name are **dropped** on rebuild **[QUIRK]**; non-dict messages raise | `:467-515` | MEDIUM |
| BC-PX-013 | `responseheaders`, host api.anthropic.com: collect `anthropic-ratelimit-unified-*` headers (suffix lowercased); if non-empty and `json.dumps(sorted)` differs from last for this session -> ledger `anth_ratelimit{session, headers}` | memory per proxy process (restart re-logs); any exception swallowed | `:176-190` | HIGH-R (#12 revisit) |
| BC-PX-014 | Any response with `text/event-stream` content type (any host, any lane) -> SSE tap installed as `response.stream` | — | `:195-199` | MEDIUM |
| BC-PX-015 | Else for `/v1/messages*`: buffer (`stream=False`) when content type has `application/json` or status ≥ 400, otherwise stream | other paths untouched | `:200-208` | MEDIUM |
| BC-PX-016 | Tap `feed(chunk)` returns the chunk unchanged; parses complete lines (up to the last `\n`), keeps the tail; tail capped to last 64,000 bytes | an exception in `_scan` aborts the rest of that block only | `:398-410` | MEDIUM |
| BC-PX-017 | Tap `_scan`: regex `rb"data: ({.*})"` per line; top-level `usage` containing `input_tokens` sets `usage=(in,out)` (last wins); cache maxima absorbed from top-level `usage` and `message.usage`; `delta.stop_reason` truthy -> stop_reason | `message_start` usage (under `message`) does not set `usage` — only events with top-level `usage.input_tokens` do; non-dict `delta` raises -> rest of block skipped | `:412-427` | MEDIUM |
| BC-PX-018 | `cache_fields(u)`: `{}` unless `cache_read_input_tokens` or `cache_creation_input_tokens` key present; else read, write, `w1h = min(ephemeral_1h, write)`, `w5m = write - w1h`. Tap version uses maxima with the 1h split only from events that carry `cache_creation` | — | `:339-359,380-396` | MEDIUM (fix history 2026-11-12) |
| BC-PX-019 | `response`, Anthropic `/v1/messages*`: usage from tap if any, else (status < 400) from JSON body `usage` + `extract_stop_reason`; ledger `anth_reply` always; `anth_usage` only when `in_tok` found; note `   anth tap: buf=… usage=… ct=…` when a tap exists | in_tok/out_tok `int(x or 0)` | `:215-253` | MEDIUM |
| BC-PX-020 | `response`, DGX `/v1/messages*`: with tap usage -> `in_tok = in + cache_read + cache_write`, `out_tok`; tap stop reason -> `stream_stop_reason`; ledger `dgx_reply` always; `dgx_usage` when in_tok set (with `cache_read_tok` only if tap saw cache fields) | non-streaming DGX JSON replies never yield usage **[QUIRK]** | `:254-282` | MEDIUM |
| BC-PX-021 | DGX status ≥ 400: note error body (first 600 chars); keep ≤ 19 old `~/dgx-llm-obs/failed-req-*.json` then write the request body (if < 50,000,000 chars) as `failed-req-<ms>.json`; note saved size; return | OSError swallowed | `:283-300` | MEDIUM |
| BC-PX-022 | DGX success: note `   DGX reply: http=<s> stop_reason=<x>` with `(streamed)` for streamed/SSE, else parsed stop reason or `unknown` | — | `:301-309` | MEDIUM |
| BC-PX-023 | `extract_stop_reason`: top-level `stop_reason`, else `choices[0].finish_reason`; non-str -> None; aliased via map; unknown values verbatim | — | `:430-456` | MEDIUM |
| BC-PX-024 | `error` hook on `/v1/messages*`: lane `dgx` if host == DGX host else `anthropic`; note `   <LANE> UPSTREAM ERROR (project=…): <msg>`; ledger `<lane>_upstream_error{error[:300], attrib…}` | `str(flow.error)` or `unknown error` | `:311-323` | MEDIUM |
| BC-PX-025 | `_account_hint`: str -> JSON dict -> `account_uuid[:8]` or `unknown`; JSON non-dict or invalid -> raw `[:8]`; non-str -> `unknown` | differs from exporter `_account_device` for JSON non-dict | `:326-336` | MEDIUM |
| BC-PX-026 | Bridge `response` -> ledger `bridge_ws_close{duration_s: 0.0}` at the upgrade response **[QUIRK]** | — | `:211-214` | MEDIUM |
| BC-PX-027 | `websocket_start`/`websocket_end` never log (`_ws_started` never set) **[QUIRK/dead]** | — | `:528-536` | MEDIUM |
| BC-PX-028 | `ledger()` format per Pass 2; never raises on OSError | other exceptions (non-serializable values) would raise | `:56-62` | MEDIUM |
| BC-PX-029 | `note()` appends `YYYY-mm-dd HH:MM:SS <msg>\n` local time; %-format errors leave msg raw; OSError swallowed; module load writes `addon module loaded (PID n)` | — | `:65-74,518` | MEDIUM |
| BC-PX-030 | Config read once at module import (`DGX_UPSTREAM`, `DGX_SERVED_MODEL`, `LOCAL_MODEL_PREFIXES` default `claude-sonnet`, `DGX_KEY_FILE`, ledger/decision paths) | mitmdump live reload re-imports | `:53-54,77-89,521` | MEDIUM |
| BC-PX-031 | Trust CLI (`hylo ca` target): `install` idempotent (fingerprint match -> state only), else `security add-trusted-cert -r trustRoot -k <login keychain>`; `status` prints a 7-row aligned table + DRIFT advice | **[QUIRK/bug]** `parse_args(...).func(None)` passes None, so `remove`/`rotate` crash on `args.force`/`args.yes` (AttributeError) | `:625-673,759-761` | MEDIUM |

---

## C. Ledger exporter (`dgx_ledger_exporter.py`) — 17 BCs

| ID | Contract | Edges / errors | Evidence | Conf |
|---|---|---|---|---|
| BC-EX-001 | Start: rebuild, record size, print `dgx-ledger-exporter: serving :<PORT>, tailing <LEDGER>`, serve forever on `0.0.0.0:PORT` (default 9210) | — | `:410-414` | MEDIUM |
| BC-EX-002 | GET path (before `?`) ≠ `/metrics` -> 404 empty | other methods: http.server default 501 | `:270-273` | MEDIUM |
| BC-EX-003 | Rebuild before rendering when `?rebuild` present or ledger size ≠ last processed size | stat error -> no rebuild | `:280-287` | MEDIUM (fix e7f9f2a) |
| BC-EX-004 | Rebuild is a full rescan; malformed lines skipped; missing ledger -> empty state | a `status: null` on a reply line raises TypeError (`None >= 400`) and aborts the scrape **[QUIRK]** | `:94-120,200,211` | MEDIUM |
| BC-EX-005 | `t` parsed with naive `strptime("%Y-%m-%dT%H:%M:%S").timestamp()` (local TZ); `last_ts` = max all; `last_dgx_ts` from `dgx_request`, `last_anth_ts` from `anth_request` | — | `:121-134` | MEDIUM |
| BC-EX-006 | Session funnel: sessions with `dgx_request/reply/usage`; meta from first event; `last` = max t; trimmed to 50 newest by `last` | stats only counted once the session is known | `:135-148,238` | MEDIUM |
| BC-EX-007 | `dgx_usage`: key (project, user, account) defaults `unknown`; `tok_in += in_tok`, `tok_out += out_tok`; if `cache_read_tok` key: `dgx_cr += cache_read`, `dgx_in_cap += in_tok`; session in/out | — | `:149-159` | MEDIUM |
| BC-EX-008 | `anth_request`: key (project, user, `model_req` or `?`, `account`) += 1 — event has no `account` so label is always `unknown` **[QUIRK]** | — | `:160-163` | MEDIUM |
| BC-EX-009 | `anth_usage`: key (project, user, `model` or `?`, account): in/out; if any cache key: coverage +1, read += , `c1 = min(1h, write)`, `cw1 += c1`, `cw5 += write - c1`; duration sum/count from `duration_s` (never present -> 0) **[QUIRK]**; `anth_rqs += 1` (not exported) | — | `:164-183` | MEDIUM |
| BC-EX-010 | `dgx_request`: key (project, user, model_req or `?`, acct, dev) via `_account_device(meta_user_id)`; session reqs; `est_prompt[(p,u,acct)] += req_bytes/4` when > 0 | — | `:184-193` | MEDIUM |
| BC-EX-011 | `dgx_reply`: duration sum/count per (project, user); status ≥ 400 -> errors and session errors | — | `:194-203` | MEDIUM |
| BC-EX-012 | `anth_reply` or `anthropic_reply` with `status == 200` -> passthrough += 1 | — | `:204-207` | MEDIUM |
| BC-EX-013 | `dgx_upstream_error` -> errors += 1 for (project, user) | `anthropic_upstream_error` ignored | `:208-210` | MEDIUM |
| BC-EX-014 | Hook log tallies by substring (if/elif order): ` [kev-continue]`, ` [kev-allow]`, ` [kev+opus-continue]`, ` [colon-fake]`, ` [heuristic-continue]`; `p_done=([0-9.]+)` last match -> `p_done_latest` | substrings inside the user-content `tail` can be miscounted **[QUIRK]** | `:213-236` | MEDIUM |
| BC-EX-015 | Exposition order and lines exactly as `:289-398` (families in fixed order; series sorted by label tuple; sessions by `-last`); joined by `\n` + trailing `\n`; headers `Content-Type: text/plain; version=0.0.4`, `Content-Length` | label values escaped by `esc`: `\` -> `\\`, `"` -> `\"`, newline -> space | `:71-72,288-404` | MEDIUM |
| BC-EX-016 | `dgx_llm_last_dgx_request_timestamp_seconds` / `..._anthropic_...` emitted only when > 0; `dgx_llm_fakestop_p_done_latest` only when seen | — | `:365-374,396-398` | MEDIUM |
| BC-EX-017 | `_account_device`: JSON str dict -> (`account_uuid[:8]`, `device_id[:8]`); invalid JSON -> (raw[:8] if len > 8 else raw, `unknown`); dict input same as JSON; JSON non-dict -> (`unknown`,`unknown`) | — | `:75-91` | MEDIUM |

---

## D. Stop hook (`auto_continue.py`) — 13 BCs

| ID | Contract | Edges / errors | Evidence | Conf |
|---|---|---|---|---|
| BC-HK-001 | stdin invalid JSON -> no output, exit 0 | JSON non-object -> AttributeError, exit 1 | `:210-213` | MEDIUM |
| BC-HK-002 | `tail = msg.strip()[-160:].replace("\n"," ")` | code-point slicing | `:214-215` | MEDIUM |
| BC-HK-003 | Non-English first (unless `DGX_ENGLISH=="0"`): CJK count `n` over ranges `぀-ヿ 㐀-䶿 一-鿿 가-힯 豈-﫿`; non-English iff `n >= 12` or (`n >= 4` and `n/max(1,len(msg)) > 0.02`) -> emit `non-english` with the LANGUAGE ERROR text | runs even when `stop_hook_active` | `:184-190,217-224` | MEDIUM |
| BC-HK-004 | `stop_hook_active` truthy -> allow (no output) | — | `:226-227` | MEDIUM |
| BC-HK-005 | `DGX_AUTOCONTINUE == "0"` -> allow | — | `:228-229` | MEDIUM |
| BC-HK-006 | Stripped message ending `?` -> allow | — | `:230-231` | MEDIUM |
| BC-HK-007 | Colon fake: `re.search(r":\s*$", stripped)` and len > 20 -> emit `colon-fake` (fixed text) before Kev | — | `:236-242` | MEDIUM |
| BC-HK-008 | `kev_state`: for each transcript line: `msg = entry.message or entry`; role = `msg.role` or `entry.type` or `?`; list content -> text blocks' text, other blocks `f"[{type}: {name}]".strip("]")`, joined with spaces after filtering empty and those ending `": ]"` (never true after strip **[QUIRK]**); non-empty -> `f"{role}: {content.strip()[:400]}"`; append `"assistant (final, ending): …"+last[-800:]`; join `\n`, keep last 6000 chars; empty -> `"assistant (final, ending): …"+msg[:800]` | reads the whole transcript every time; OSError -> only the final line | `:64-91` | MEDIUM |
| BC-HK-009 | `kev_pdone`: POST `{"model": KEV_MODEL, "state": …, "questions": {"turn_complete": DONE_QUESTION}}`, `Content-Type: application/json`, Bearer from env or key file if any; timeout 2.5 s; numeric `answers.turn_complete.noul` -> `(float, elapsed)`; else `(None, None)` | — | `:94-121` | LOW (external) |
| BC-HK-010 | Median: up to 3 calls; stop early after ≥ 2 successes when the last elapsed > 1.25 s; none -> None; else `sorted[len//2]` (upper median for 2) | — | `:124-138` | MEDIUM |
| BC-HK-011 | Kev present: `fake = p < 0.40`; not fake -> log `kev-allow` with `p_done=%.3f fake=False (%.2fs)`, no output; fake -> emit `kev-continue` with `p(done)=%.2f` text | — | `:244-261` | MEDIUM |
| BC-HK-012 | Kev absent: `should_continue(msg)`: empty -> False; ends `?` -> False; ends `:`, `…`, `...` -> True; `last` = last sentence of the last line (split on whitespace after `.`/`!`, lookbehind); True iff (ANNOUNCE matches and last does not end `.`/`!`) or (ANNOUNCE and `\b(now\|next\|first)\b` and len < 200 and not `\b(done\|complete\|finished\|ready for you)\b`), case-insensitive -> emit `heuristic-continue` with `tail[-100:]` | Python Unicode `\b` and lookbehind (RE2 lacks lookbehind) | `:24-28,169-181,263-270` | MEDIUM |
| BC-HK-013 | `emit` = log line + print one JSON line `{"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": …}}` (Python json.dumps, ASCII-escaped); log line `"%Y-%m-%d %H:%M:%S [kind] kev=<v> session=<sid> stop_hook_active=<v> tail=<repr>"`; `opus_verdict` never called (dead) | log OSError swallowed | `:141-166,193-206` | MEDIUM |

---

## E. Launcher (`claude-dgx`) — 11 BCs

| ID | Contract | Edges / errors | Evidence | Conf |
|---|---|---|---|---|
| BC-LN-001 | `claude-dgx trust …` -> `exec python3 dgx_proxy.py trust …` (no session) | — | `:11-14` | MEDIUM |
| BC-LN-002 | Exports (unconditionally overriding) `LOCAL_MODEL_PREFIXES=claude-sonnet`, `DGX_SERVED_MODEL=claude-sonnet-5-5`; appends `X-DGX-Project: <basename $PWD>` and `X-DGX-User: <DGX_USER or whoami>` lines to `ANTHROPIC_CUSTOM_HEADERS` | — | `:38-54` | MEDIUM |
| BC-LN-003 | Preflight unless `DGX_SKIP_PREFLIGHT=1`: runs `.mitmenv/bin/python` (invisible) or `python3` with `dgx_preflight.py <DGX_UPSTREAM>`; failure -> two stderr lines, exit 1 | — | `:60-68` | MEDIUM |
| BC-LN-004 | Invisible mode (default): unset `ANTHROPIC_BASE_URL`; first free port 8090..8143 by `nc -z`; start `mitmdump --set flow_detail=1 --listen-port P -s dgx_proxy.py` (log `$TMPDIR/dgx-mitm.<pid>.<P>.log`); wait ≤ 40×0.25 s; export `HTTPS_PROXY=http://127.0.0.1:P`, `NODE_EXTRA_CA_CERTS=$HOME/.mitmproxy/mitmproxy-ca-cert.pem`; print `invisible proxy: …` | no free port / no listen -> stderr, exit 1 | `:70-82` | MEDIUM |
| BC-LN-005 | Exports `API_TIMEOUT_MS=1800000`, `CLAUDE_CODE_AUTO_MODE_SERVER=0` | — | `:104-109` | MEDIUM |
| BC-LN-006 | Sources `DGX_PROFILE` (default `~/.config/dgx-llm/profile.env`) with `set -a` **after** the proxy started -> profile values reach Claude Code, statusline and hook but **not** the running proxy **[QUIRK]** | — | `:114-115` | MEDIUM |
| BC-LN-007 | Args: `--model opus` iff `DGX_MAIN_MODEL=opus` else `--model sonnet`; `--remote-control` iff `DGX_REMOTE=1`; `--append-system-prompt <LANGUAGE RULE>` unless `DGX_ENGLISH=0`; `--dangerously-skip-permissions` unless `DGX_SAFE=1` | — | `:128-139` | MEDIUM |
| BC-LN-008 | Exports `DGX_ENGLISH`, `DGX_AUTOCONTINUE` (default 1), `DGX_KEV_THRESHOLD` (0.40), `DGX_KEV_URL`, `DGX_KEV_MODEL` (launcher default differs from hook default) | — | `:148-155` | MEDIUM |
| BC-LN-009 | `--settings` JSON = `{` comma-joined parts `}`: `hooks` (UserPromptSubmit echo reminder timeout 5 when English; Stop `python3 '<HERE>/auto_continue.py'` timeout 30 when English or autocontinue), `sandbox {enabled:true, allowUnsandboxedCommands:false}` iff `DGX_SANDBOX=1`, `statusLine {type command, command python3 '<HERE>/dgx_statusline.py', padding 0, refreshInterval 4}` + `subagentStatusLine` unless `DGX_STATUSLINE` ≠ 1 | `HERE` containing quotes breaks the JSON | `:156-181` | MEDIUM |
| BC-LN-010 | `DGX_PRINT_ARGS=1` prints `claude` and each arg on its own line, exit 0 (dry run — the proxy has already been started and is killed by the trap) | — | `:182-184` | MEDIUM |
| BC-LN-011 | Runs `claude ARGS "$@"` as a child; trap on EXIT/INT/TERM kills mitmdump | — | `:97,185` | MEDIUM |

## F. Coordinator (2), Preflight (2), Backfill (5), Services (2)

| ID | Contract | Edges / errors | Evidence | Conf |
|---|---|---|---|---|
| BC-CO-001 | Under `flock` on `.proxy-state/lock`: if port file non-empty, a mitmdump LISTENs there (lsof) and pid alive -> reuse; print `PORT=<p>` | **unwired**; `flock` is not a stock macOS binary | `dgx-proxy-coordinator.sh:14-24,40-50` | LOW |
| BC-CO-002 | Else pick first port 8090..8143 with no listener, start mitmdump, wait ≤ 10 s, write port/pid | failure -> stderr, exit 1 | `:26-38` | LOW |
| BC-PF-001 | TCP connect to host:port of argv[1] (default `http://192.0.2.10:8080`, port 80 if absent) with 4 s timeout; success -> silent exit 0 | — | `dgx_preflight.py:18-24` | MEDIUM |
| BC-PF-002 | Failure -> stdout message by class: EHOSTUNREACH (Local Network advice), timeout/ETIMEDOUT/EHOSTDOWN, ECONNREFUSED, else generic; exit 1 | — | `:25-41` | MEDIUM |
| BC-BF-001 | Per transcript: messages keyed by id with `t0` = last user-line ts, `t1` = last line ts, first usage and model; family = first of `opus`, `sonnet`, `haiku` substring; `usd += (in*pi + out*po + w5*p5 + w1*p1 + read*pr)/1e6`, `w5 = ephemeral_5m or (0 if cache_creation else cache_creation_input_tokens)` | unknown family skipped | `tools/backfill_cost_history.py:42-76` | MEDIUM |
| BC-BF-002 | Lane = lane with max output tokens (tie or zero -> `dgx`) | — | `:77,81` | MEDIUM |
| BC-BF-003 | `api_ms = sum of spans with 0 < span <= 4*max(out,1)/15` ×1000, kept only if ≥ 30 min, else None | differs from statusline (`out>0` required there) | `:78-80` | MEDIUM |
| BC-BF-004 | Files modified within `--days` (30); skip sid with existing `src=="cc"`; skip usd < 1 or no timestamps; write `{lane, usd round 4, api_ms, ts: last, src: "backfill"}` | glob order filesystem-dependent | `:95-109` | MEDIUM |
| BC-BF-005 | Print summary; unless `--dry-run`, atomic write of the whole history | — | `:110-117` | MEDIUM |
| BC-SV-001 | Exporter agent: `/usr/bin/python3 ~/hylo/legacy/dgx_ledger_exporter.py`, RunAtLoad, KeepAlive, logs `/tmp/dgx-ledger-exporter.log` | `~` in ProgramArguments is not shell-expanded by launchd (scrubbed path; real one is absolute) | `deploy/io.hylo.ledger-exporter.plist:4-12` | LOW |
| BC-SV-002 | Tunnel agent: `ssh -N -R 127.0.0.1:9210:127.0.0.1:9210 -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes dgx`, KeepAlive | — | `deploy/io.hylo.ledger-tunnel.plist:4-17` | MEDIUM |

## BC counts

| Component | BCs |
|---|---|
| Status line | 53 |
| Proxy (incl. trust CLI) | 31 |
| Exporter | 17 |
| Stop hook | 13 |
| Launcher | 11 |
| Coordinator / Preflight / Backfill / Services | 2 / 2 / 5 / 2 |
| **Total** | **136** |

## Gaps (no verification evidence anywhere)

- Proxy, exporter, hook, launcher: zero recorded test cases; all MEDIUM at best. P3 replay corpus must create them.
- SSE tap behavior on real vLLM vs Anthropic event shapes (BC-PX-017) depends on upstream payloads not in the repo.
- Stop-hook output schema acceptance by Claude Code (BC-HK-013) — external, unverified.
- `ps` parsing on Linux/Windows (BC-SL-023) — macOS-only today.

## State Checkpoint
```yaml
pass: 3
status: complete
files_scanned: 11
timestamp: 2026-11-14T05:09:24Z
next_pass: 4
```
