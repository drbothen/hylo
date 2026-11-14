# Pass 3 deepening, round 8: behavioral contracts (hylo-legacy), statement partition and re-verification

- **Scope:** `legacy/` is unchanged: 11 files, 3,181 lines (recounted with `wc -l`). This round reads, statement by statement, every Python
  statement that was neither re-read in r6, nor inside a region r7 named as pinned by an exhaustive table, nor out of scope (§1). It also re-reads
  `auto_continue.py:193-270`, `dgx_proxy.py:98-106,170-216,248-256,311-323,516-564`, `dgx_preflight.py` in full, and `dgx_statusline.py:56-157,
  362-398,640-651,838-998,1183-1245`. Read-only, for citations only: mitmproxy 12.3.1 `options:241-247`, `proxy/server:45-125,274-310,340-395`,
  `proxy/mode_servers:60-75`, `proxy/layers/websocket:185-200` (read as text from the per-window venv's site-packages; nothing imported from there).
- **Inputs read:** pass-3 r7 (in full), r6 (§0-§5), r5 (§2.3-§2.4, index), r4 (canonical index §7.3, §3 V-1/V-2, RET table); pass-3 broad and r1
  (§A0-§A9, §D literal table) for the BCs cited by the category (iv) statements; pass-3 r2 §B1 (BC-PX-037 table), r3 (grep for Target C); pass-2 r3
  §1.6 and §3.2, r2 H-catalogue line, r4 CONV-ABS-12, r6 CONV-ABS-14 (read only; pass 2 is converged at r9 and was not edited).
- **Method:** fresh scripts (none reuses an r6 or r7 script or fixture) in
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r8/`: `partition.py` → `partition_out.txt`,
  `iv_detail.txt` (run on 3.11.7 and 3.9.6, identical totals); `ii_detail.py` → `ii_detail_out.txt`; `hk09.py` → `hk09_out.txt`; `px049.py` →
  `px049_out.txt`; `iso_probe.py` → `iso_probe_out.txt`. Every script that runs legacy code execs or runs a **text copy** and asserts the cited source
  lines first. Interpreters: `/opt/homebrew/anaconda3/bin/python3 -I` (3.11.7) and `/usr/bin/python3 -I` (3.9.6). No legacy main() with side effects,
  no server, no proxy, no socket, nothing networked (the hook copy ran as a child process with `HOME` in the scratchpad on two paths that return
  before Kev; the proxy copy ran with stub flows and the mitmproxy import absent). `CLAUDE.local.md` was not read. No git commit.
- **Notation:** `\e` is ESC (U+001B). `\udcXX` inside a JSON string is the 6-character ASCII escape; a raw lone surrogate code point is written
  U+DCXX. A bare `:N` means the file named in the section heading. **P2rN**/**P3rN** = pass-2/pass-3 round N.
- **IDs:** no new BC, no new crash row, no new OD, **no retraction** (CONV-ABS-23/24 stay unused; the next free number is 29). One scope amendment
  of an r7 BC (**AM-1**, BC-PX-049 contracts 3-4), one count correction of an r7 statement (**CC-1**), and four refinements (§2.3).

---

## 1. Target A: exact partition of the 1,809 Python statements

### 1.1 Rules (precedence i > ii > iii > iv, so each `ast.stmt` node lands in exactly one category)

| Category | Rule (as coded in `partition.py`) |
|---|---|
| (i) re-read line by line in r6 | Exactly the nodes r6's `stmt_count.py` counted: every statement nested in the 45 functions r6 named (status line 16, exporter 6 plus the `__main__` block, proxy 9, hook 8). The `def` line itself is **not** counted, as in r6. Reproduces r6's 217 + 100 + 270 + 211 + 105 = **903** |
| (ii) pinned by a named exhaustive table | Statements inside the line ranges r7 §6 named (`dgx_statusline.py:158-362, 888-975, 999-1154`, `dgx_proxy.py:339-456`, all of `tools/backfill_cost_history.py`) that are not already (i) |
| (iii) explicitly out of scope | `dgx_proxy.py` trust CLI: statements at line ≥ 550 **nested inside** a function or the `__main__` body. Scope rule: BC-PX-031 (OOS, replaced by `hylo ca`, D13). The 17 **top-level** statements there (5 assignments `:560-564`, 11 `def`s, the `if __name__` test) run when mitmdump loads the addon, so they go to (iv) and were read |
| (iv) none of these | Everything else |

### 1.2 Partition counts

| File | Total | (i) r6 | (ii) table | (iii) OOS | (iv) read now |
|---|---|---|---|---|---|
| `dgx_statusline.py` | 742 | 317 | 265 | 0 | 160 |
| `dgx_proxy.py` | 500 | 211 | 71 | 133 | 85 |
| `dgx_ledger_exporter.py` | 316 | 270 | 0 | 0 | 46 |
| `auto_continue.py` | 146 | 105 | 0 | 0 | 41 |
| `dgx_preflight.py` | 19 | 0 | 0 | 0 | 19 |
| `tools/backfill_cost_history.py` | 86 | 0 | 86 | 0 | 0 |
| **Total** | **1,809** | **903** | **422** | **133** | **351** |

**CC-1 (count correction of P3r7 §6, wording only):** r7 says the not-re-read regions hold "**453**" statements. Its ranges counted by line number,
so `:158-362` also counted `record_cost` (11 nested statements) and `cost_thresholds` (20), which r6 had already re-read. Exact category (ii) is
**422** (453 − 31). r7's sentence "the 903 … are half of them" stands. The 1,809 total is confirmed on both interpreters.

### 1.3 Category (ii): the named table per function

| File, function (statements) | Exhaustive pinned table (BC) |
|---|---|
| status line `fetch_sample` (21) | BC-SL-040 (fetch, first-wins, `except Exception`), BC-SL-091 (pinned sequence) |
| `load_cache` (5), `save_cache` (8) | BC-SL-052, BC-SL-078 (sid with `/`), BC-SL-041 (NaN tokens in cache) |
| `COST_*` assignments `:217-221` (5); `def record_cost`, `def cost_thresholds` (2) | BC-SL-101, BC-SL-102; r1 §D literal row 025/026/028/029/082 |
| `claude_window_start` (23) | BC-SL-023 (D4-EX-1), BC-SL-080 |
| `effective_rl` (11) | BC-SL-018, BC-SL-093 |
| `get_sample` (32) | BC-SL-041, BC-SL-042, BC-SL-091, BC-SL-092 |
| `render_subagent_rows` (28), `main_subagent` (8) | BC-SL-097 (`--subagent`, CP-A01..A03, OD-14) |
| `_READ_CAP`, `_MIX_CACHE`, `TURN_*`, `REBUILD_EXCESS` `:951-974` (6) | BC-SL-032/066, BC-SL-070, BC-SL-039, BC-SL-036 (r1 §D) |
| `_mix_counts` (116) | BC-SL-030..039, 065..072, BC-SL-094/095 (turn machine), BC-SL-096 (63-case `json.dumps` oracle), BC-SL-098/099 (D4-EX-2, 21 rows), BC-SL-100, 103 |
| proxy `cache_fields` (12) | BC-PX-018 |
| `_SSETap` (46) | BC-PX-016, BC-PX-040, BC-PX-045 (theorem, 300-trial property test, reference model) |
| `_STOP_REASON_ALIASES` (1), `extract_stop_reason` (12) | BC-PX-023 |
| backfill, all 86 | BC-BF-006..013 (BC-BF-001..005 superseded in detail) |

### 1.4 Category (iii)

133 statements: the bodies of `_login_keychain`, `_file_fingerprint`, `_keychain_fingerprint`, `_mitmdump_running`, `_read_state`, `_write_state`,
`cmd_trust_install/status/remove/rotate`, `_build_parser` and the `__main__` body (`dgx_proxy.py:567-764`). Rule: BC-PX-031 (OOS, D13). They run
only as `python3 dgx_proxy.py trust …` (`claude-dgx:11-14`), never inside mitmdump.

### 1.5 Category (iv): all 351 statements read against the BCs

Every statement was read in order. "Stated by" names the BC, catalogue row or pass-2 row that predicts its effect (output, file write, ledger line,
exit or crash).

**Status line (160).**

| Statements | Count | Stated by |
|---|---|---|
| docstring `:2`; imports `:60-70` | 12 | no effect beyond binding (all stdlib) |
| tunables and literals `:73-137` (incl. `TTL`/`ROWS` env parse, `VM_URL.rstrip("/")`, `CACHE_DIR`, `QUERY`, colours, `SEP`, pills, `SPARK`, `_ANSI`) and `:644,648,649,845` (`TRACE_KEYS`, `_SPARK_FIXED`, `_SPARK_FLOOR`, `_SUB_GLYPH`) | 32 | r1 §A0 (env reads), BC-SL-087 + CP-X01/X02 (import-time crash outside the guard), r1 §D literal table (every number), P2r1 config row 9 (trailing `/` stripped), BC-SL-048/073 (retired `mine` → `rate`), BC-SL-097 (`_SUB_GLYPH`) |
| the 14 `def` lines of r6's functions | 14 | name binding; defaults are `None` literals (`render_lane`, `render_telemetry`, `render_telemetry_fields`); no annotation is evaluated that can fail |
| `visible` `:151-153` | 3 | BC-SL-004 |
| `git_branch` `:364-396` | 26 | BC-SL-009 (walk, `gitdir:` pointer, HEAD, `ref[:7]`), BC-SL-009/010 r1 (fully guarded, locale text mode) |
| `_fmt_tokens` `:876-885` | 9 | BC-SL-097 (only `render_subagent_rows` calls it) |
| `_iso_ts` `:977-985` | 8 | BC-SL-069. Probed this round for an exception other than `ValueError` (which would escape and hit BC-SL-068): 16 extreme values × 5 time zones, **none** (§2.3 R-3) |
| `_finish_turn` `:988-996` | 8 | BC-SL-039, BC-SL-094 (turn machine table) |
| `term_cols` `:1185-1190` | 5 | BC-SL-005/055 |
| `trim_to_fit` `:1193-1197` | 5 | BC-SL-054, BC-SL-090 |
| `main` `:1200-1235` | 31 | BC-SL-002/076 (stdin), BC-SL-003/055 (cols read twice, width rule), BC-SL-077 (order and writes), BC-SL-052 (`nosession`, raw sid), BC-SL-018/093, BC-SL-053 (`dgx_mtok` ≤ 0 or non-number → None; `dgx_rate` raw), BC-SL-039/085 (`mix[7]`), `SPARK_ON` (r1 §A0 sparkline row), BC-SL-023 (window start only with a truthy `session_id`), BC-SL-054 |
| `if __name__` `:1238-1245` | 7 | BC-SL-001 (guard), BC-SL-097 (`--subagent` anywhere in argv), CP-X03 (the guard's own print fails) |

**Exporter (46).**

| Statements | Count | Stated by |
|---|---|---|
| docstring, 6 imports | 7 | no effect |
| `LEDGER`, `FAKESTOP_LOG`, `SESSION_LIMIT`, `PORT` `:22-25` | 4 | BC-EX-001 (paths, port 9210); P3r5 §2.4 (`int()` failure → startup crash, BC-EX-021 crash loop) |
| `state_lock` and the 27 accumulators `:27-61` | 28 | P2r2 §5.1 entity table (initial state, `processed_size = -1`); P3r5 (lock vestigial, single-threaded `HTTPServer`) |
| `def` lines (`_current_size`, `esc`, `_account_device`, `rebuild`), `class Handler`, `def do_GET`, `def log_message` | 7 | name binding; annotations are builtins; `BaseHTTPRequestHandler` default HTTP/1.0 (P3r5 §2.4, BC-EX-026) |

**Proxy (85).**

| Statements | Count | Stated by |
|---|---|---|
| docstring, `from __future__ import annotations`, 13 imports | 15 | no effect; `__future__` keeps the `mitmproxy.http.HTTPFlow` and `str \| None` annotations unevaluated |
| `try: import mitmproxy.http / from mitmproxy import ctx / except ImportError: pass` | 4 | CLI mode (BC-PX-031); `ctx` and `log` are unused (no effect) |
| `RL_PREFIX`, `DGX_BLOCK_TYPES`, `_logged_unknown`, `log`, `DECISION_LOG`, `LEDGER` `:48-54` | 6 | BC-PX-013, BC-PX-011/012, P-R5 + P2r3 §1.6 (reset on reload), BC-PX-028/029/030 |
| `def ledger`, `def note`, `class DGXRouter` + 6 method `def`s, `def normalize_for_dgx` | 10 | name binding |
| `_account_hint` `:326-336` | 10 | BC-PX-025; P2r1 I6 (incl. the proxy-only crash on a truthy non-str `account_uuid`, and list values → P-S2/E-06) |
| `uses_server_tool` `:459-464` | 6 | BC-PX-042; P-R2 |
| `note("addon module loaded …")` `:518` | 1 | BC-PX-029; cannot raise (constant text, int PID; r6 §1.4) |
| `_router = DGXRouter()` `:521` | 1 | BC-PX-030; P2r3 §1.6 (bad `DGX_UPSTREAM` port → `ValueError` at import), CONV-ABS-12/RET-09 (at launch mitmdump exits 1) |
| module hooks `request`, `responseheaders`, `response`, `error` (delegators) | 8 | forward to the r6-read methods |
| `websocket_start`, `websocket_end` | 7 | BC-PX-027 (dead: `_ws_started` is never set) |
| trust-CLI top level `:560-564`, 11 `def`s, `if __name__` test | 17 | Executed at addon load. The `def`s bind names (no defaults; annotations unevaluated). The `if` test is false under mitmdump. The 5 assignments call `Path.home()` twice and read `DGX_TRUST_STATE`. Only failure: `Path.home()` raises `RuntimeError` when no home directory can be resolved (`HOME` unset **and** no passwd entry for the uid; CPython 3.11 `pathlib.expanduser`, read this round). Not reachable for a logged-in macOS user, whose passwd entry always resolves. If it were, the outcome is the stated module-level-exception class (CONV-ABS-12 / RET-09 at launch; P2r3 §1.6 pass-through after a reload). No effect beyond binding otherwise |

**Hook (41).**

| Statements | Count | Stated by |
|---|---|---|
| docstring, 8 imports | 9 | no effect |
| `ANNOUNCE` `:24`, `CJK` `:184` | 2 | BC-HK should-continue / non-English contracts (P2r2 §6) |
| `KEV_URL`, `KEV_MODEL`, `KEV_THRESHOLD`, `KEV_TIMEOUT`, `KEV_MESSAGES`, `KEV_CHARS` `:31-36` | 6 | Kev wire table (P2r2 T6); H-07 / P3r5 §2.4 (import-time `float()`/`int()` crash) |
| `DONE_QUESTION` `:38-61` | 1 | Kev wire table (request payload) |
| 8 `def` lines | 8 | name binding; **`def kev_pdone(state: str, question: dict \| None = None)` `:94` is H-08** (annotation evaluated at definition, `TypeError` on Python < 3.10) |
| `opus_verdict` `:141-166` | 13 | dead, never called (P3r5 §2.4, BC-HK-013) |
| `if __name__: main()` | 2 | BC-HK-019 (no guard; return value ignored, exit 0 unless an exception escapes) |

**Preflight (19).**

| Statements | Count | Stated by |
|---|---|---|
| docstring, 4 imports | 5 | no effect |
| `url`, `u`, `host, port` `:18-20` | 3 | BC-PF-001; P2r3 §3.2 (port 80 whatever the scheme; invalid port → `ValueError` traceback, exit 1) |
| `try` / `create_connection` / four `print` branches / `sys.exit(1)` `:22-41` | 11 | BC-PF-001/002; P2r3 §3.2 error-class table (incl. `gaierror` → generic) and its non-`OSError` row (§2.3 R-4) |

**Result for category (iv): 351 statements read, 0 unstated effects.** Every effect, crash and exit in the 351 is predicted by a BC, a catalogue row
(CP-X01..X03, H-07, H-08, P-R2, P-S2, E-06) or a pass-2 row. The one failure not previously written down (`Path.home()` at addon load) cannot
occur on the target platform and falls under the stated module-level-exception outcome.

---

## 2. Target B: r7's new items re-verified with fresh scripts

### 2.1 H-09: **CONFIRMED**

`hk09.py` (3.11.7, child process on a text copy, `HOME` in the scratchpad, Kev URL set to an unusable scheme; both paths return before Kev):

| Case (stdin is ASCII JSON text) | Exit | Stdout | Log file | Log lines | stderr, last line |
|---|---|---|---|---|---|
| c1 colon-fake, `session_id` `"s-ok"` | 0 | 313 B | created | 1 | — |
| c2 colon-fake, `"s-\udc80"` | **1** | **0** | created, empty | **0** | `UnicodeEncodeError: … '\udc80' in position 49: surrogates not allowed` |
| c3 colon-fake, lone high `"s-\ud83d"` | **1** | **0** | created, empty | **0** | same, `'\ud83d'` |
| c4 colon-fake, valid pair `"s-😀"` | 0 | 313 B | created | 1 | — |
| c5 as c2 under `LC_ALL=C` (UTF-8 mode) | **1** | **0** | created, empty | **0** | same as c2 |
| c6 non-English, `stop_hook_active` `"y\udcff"` | **1** | **0** | created, empty | **0** | same, `'\udcff'` in position 71 |
| c7 non-English, `stop_hook_active` `true` | 0 | 350 B | created | 1 | — |
| c8 colon-fake, surrogate only in the message (tail is `repr`-escaped) | 0 | 313 B | created | 1 | — |
| c9 colon-fake, integer `session_id` | 0 | 313 B | created | 1 | — |

H-09 stands as r7 wrote it: trigger, exit 1, no stdout, no log line, in both locale modes, for low and high lone surrogates, and through
`stop_hook_active` on the non-English path. Refinement R-1 (§2.3): the log file (and its directory) is **created** before the write raises.

### 2.2 BC-PX-049: **CONFIRMED** (duration contract), with scope amendment AM-1 (contracts 3-4)

`px049.py`, three parts:

| Part | Evidence | Result |
|---|---|---|
| A. mitmproxy 12.3.1 sources (text assertions) | `options:241-247` `tcp_timeout` int 600 and the only `timeout` option; `proxy/server:116-120` one `TimeoutWatchdog` per client connection; `:385-387` `register_activity()` at the top of every `server_event`; `:274-294` `handle_connection` serves **both** legs and feeds each read to `server_event(DataReceived)`; `:352` "Closing connection due to inactivity"; `proxy/layers/websocket:196-200` pings/pongs relayed end to end | contract items 1-2 confirmed |
| B. `TimeoutWatchdog` text copy under asyncio, timeout 0.3 s | activity every 0.1 s for 2.0 s → fires once at **2.31 s** (0.3 s after the last activity); no activity → fires at **0.30 s** | no total-duration limit; only inactivity; any activity resets |
| C. legacy addon (`:1-549` text copy) on stub pass-through flows | WS upgrade `api.anthropic.com/api/frame/sync` → `[]`; SSE `…/v1/code/sessions/x/events` → tap, `[]`; JSON `…/v1/code/sessions/x` → buffered, `[]`; SSE on another host, then an error (inactivity cut) → tap, `[]`; failure on `api.anthropic.com/api/oauth/profile` → `[]` | contract item 3 confirmed for these flows |

Refinement R-2: `proxy/mode_servers:68-74` wraps every addon hook in `timeout_watchdog.disarm()`, so time inside a hook does not count and the
watchdog re-arms with fresh activity when the hook returns. No pass-through effect (the addon's pass-through hooks return at once).

**AM-1 (scope amendment of BC-PX-049 contracts 3 and 4; r7's duration claims are not withdrawn).** r7's contract 1 defines a pass-through flow as
"any host other than the routed `api.anthropic.com/v1/messages*`". Two hooks are gated on the **path** alone, so for pass-through flows on another
host whose path starts with `/v1/messages`, contracts 3 and 4 as worded are too broad. Part C pins both:

| Case | Legacy behavior | Already stated by |
|---|---|---|
| another host, `/v1/messages`, failure | ledger **`anthropic_upstream_error`** and a decision-log line `ANTHROPIC UPSTREAM ERROR (project=None): …` (`:316-323`) | **CONV-ABS-14** (P2r5/P3r4): `error()` fires for any host; BC-PX-024 index wording "lane = non-DGX host" |
| another host, `/v1/messages`, `text/plain` 200 | `response.stream = True` (streamed, not buffered), no ledger line (`:200-208`) | **BC-PX-037** table rows 2-3 (no host condition, P3r2 §B1) |
| the backend host, `/v1/messages` (mirror case) | `dgx_reply` on success, `dgx_upstream_error` on failure | BC-PX-020/024 (P3r5 §2.4, P2r6 mirror) |

Final wording for BC-PX-049:

- **Contract 3:** "Ledger effect of a pass-through flow: none, whether it ends normally, by server EOF or by the inactivity cut. Exceptions:
  `anth_ratelimit` (BC-PX-013); an `_SSETap` whose result is never written (BC-PX-014); and, for a path starting with `/v1/messages` on any host,
  `anthropic_upstream_error` on failure (BC-PX-024, CONV-ABS-14), or `dgx_reply`/`dgx_upstream_error` when the host is the backend (BC-PX-020/024
  mirror)."
- **Contract 4:** "SSE responses are streamed on any host (BC-PX-014/037). A non-SSE response on a `/v1/messages*` path follows BC-PX-037 on any
  host (JSON or status ≥ 400 → buffered, otherwise streamed). All other pass-through responses are buffered in full (mitmproxy default)."

Each added clause repeats a contract that the index already holds. No new effect. HY-PASS-1, the Go contract and the table tests are unchanged.

### 2.3 Refinements found this round (no new BC, no new effect)

| # | Item | Evidence | Where it belongs |
|---|---|---|---|
| R-1 | H-09: `open(…, "a")` creates `~/.cache/dgx-llm/auto-continue.log` (and `makedirs` its directory) before the encode raises, so a first-ever crash leaves an **empty** log file | `hk09.py` c2/c3/c5/c6 | BC-HK-019 flag (H-09 row). The exporter reads an empty log as zero tallies (BC-EX-014) |
| R-2 | Hooks disarm the inactivity watchdog | mitmproxy `proxy/mode_servers:68-74`, `proxy/server:78-89` | BC-PX-049 contract 2 note |
| R-3 | `_iso_ts` raises nothing but `ValueError` on 16 extreme timestamps × 5 zones (UTC, America/Chicago, Pacific/Kiritimati, Pacific/Pago_Pago, Asia/Tokyo). Naive `9999-12-31T23:59:59` and `…T12:00:00` give `None` under UTC+14 but a float under UTC; naive year-1 values give `None` everywhere except from `0001-01-02` | `iso_probe.py` | BC-SL-069 (TZ-dependent `None` near the range ends) |
| R-4 | Preflight: an over-long DNS label in the upstream URL raises `UnicodeError` (a `ValueError`, not an `OSError`) from the IDNA codec before any lookup → traceback, exit 1 | codec check only (`('a'*64+'.example').encode('idna')`); nothing networked | P2r3 §3.2 "Non-OSError failures" row gains this trigger; outcome unchanged |

---

## 3. Target C: propagation fixes as final wording; no other statement rests on the retracted facts

### 3.1 Corrections table (apply when the Phase-1 spec copies these texts)

| ID | Place | Current text | Final wording |
|---|---|---|---|
| **PR-3** | P3r3 Delta Summary, P3 bullet (`…-r3.md:438-439`) | "Production data confirms that user cancels are logged as upstream errors and that the client talks HTTP/1.1." | "Production data confirms that user cancels are logged as upstream errors and that **Claude Code** talks HTTP/1.1 to the proxy. Other clients that trust the CA (child tools) also use HTTP/2 (CONV-ABS-25)." |
| **PR-5** | P3r4 §3 **V-1**, expected column (`…-r4.md:160`) | "…Request line in origin form (client used CONNECT + TLS over HTTP/1.1)" | "…Request line in origin form (**Claude Code** uses CONNECT + TLS over HTTP/1.1). **Plus one HTTP/2 case:** an h2 client's rerouted request carries `:authority`, updated the same way as `Host` (P3r3 §2.4)." |
| **PR-6** | P3r4 §3 **V-2**, expected column (`…-r4.md:161`) | "HTTP/1.1: the 502 is sent and the client connection closes (P2r4 §1.3, HTTP/1 row; production is HTTP/1.1)" | "**HTTP/1.1 (Claude Code):** the 502 is sent and the client connection closes (P2r4 §1.3, HTTP/1 row). **HTTP/2 (other clients, observed in production, CONV-ABS-25):** the 502 goes out on the stream, the connection stays open, and later DGX-lane requests on that connection fail at once with the cached error (P2r4 §1.3, HTTP/2 row). In legacy only child tools reach this; D14 removes them in hylo. Record both client-side byte sequences." |

### 3.2 Fresh sweep for other dependents

Grep over the broad pass-3 file and r1-r7 for `HTTP/2`, `HTTP/1`, `h1`, `h2`, `claudeusercontent`, `bridge`, `Remote Control` (68 hits). Each hit
was read in context and matched against r7's PR-1..PR-10. Hits r7 did not list:

| # | Place | Statement | Rests on a retracted fact? |
|---|---|---|---|
| PR-11 | P3r3 §1 row "SSE tap chunk-boundary dependence" (BC-PX-040) | "The HTTP/1 body reader turns each TCP read … into one `ResponseData`" | **No.** It describes how the boundaries arise for an h1 flow (Claude Code's). BC-PX-040/045 hold for **any** boundaries (theorem plus property test), so they cover h2 DATA frames too. Optional: add "(h2: one piece per DATA frame; BC-PX-045 is framing-agnostic)" |
| PR-12 | P3r3 §2.2 error-cause rows (`HTTP/1 protocol error: …`), §3 census lines 70, 122, 378 | observed error texts | No: quoted ledger text |
| PR-13 | P3r2 §B1 item 1, P3r3 §2.1 row 1 ("http1/h2 layers create the `Response` with `content=None`") | both layers cited | No: neutral |
| PR-14 | P3r3 §4 exporter event table (`bridge_*` → only `last_ts`) | code behavior | No: code-accurate. `bridge_*` never occurs in production (OD-43), which leaves the row's effect at zero |

**Result:** after PR-3, PR-5 and PR-6, **no pass-3 statement rests on** the retracted "0 HTTP/2 lines" count (CONV-ABS-25) or on
`bridge.claudeusercontent.com` as the Remote Control host (CONV-ABS-26). BC-PX-001/026 stay as code contracts with the "never fires in production"
flag. No BC contract text changes.

---

## 4. Target D: index totals

**Unchanged:** 232 BCs (BX 137, JE 44, OOS 10, approved deviation 6, pending-OD primary 35); crash catalogues as in P3r7 §7.1 (hook H-01..H-09);
owner items OD-01..OD-43 and OD-45 (42 pending, 2 ruled; OD-44 unused; next new OD-46); retractions unchanged (pass 3: CONV-ABS-21, 22; 23-24
unused; next free 29). By last round: no BC is re-dated this round (r8 = 0).

Flag-only changes (Last unchanged):

| ID | Flag |
|---|---|
| BC-PX-049 | "contracts 3-4 re-scoped (AM-1, r8): `/v1/messages*` paths on any host follow BC-PX-024/037; backend host = mirror case; R-2 hooks disarm the watchdog" |
| BC-HK-019 | += "H-09 re-pinned r8 (low and high surrogates, both locale modes); the empty log file is created (R-1)" |
| BC-SL-069 | += "TZ-dependent `None` near the range ends; no exception other than `ValueError` (R-3)" |
| BC-PF-002 | += "IDNA `UnicodeError` → traceback, exit 1 (R-4; P2r3 §3.2 non-OSError row)" |
| BC-PX-043, BC-PX-044 | += "final V-1/V-2 wording: P3r8 §3.1 (PR-5, PR-6)" |
| BC-PX-040 | += "h2 boundaries are DATA frames; BC-PX-045 covers them (PR-11)" |

---

## Owner checks (carried, optional)

1. Optional: the Grafana per-session panel with at least 2 recent sessions (BC-EX-025).
2. Optional: `promtool check metrics` offline on one saved scrape body.

## Delta Summary

- **Target A:** exact AST partition of all 1,809 statements: (i) 903, (ii) 422, (iii) 133, (iv) 351. Every one of the 351 category (iv) statements
  was read against the BCs: **0 unstated effects**. r7's "453" corrected to 422 (CC-1, double count of 31 r6 statements). The 17 top-level
  trust-CLI statements moved from "OOS" to "read", because they run at addon load. Their only failure (`Path.home()` with no resolvable home)
  cannot occur on macOS and falls under the stated module-level-exception outcome.
- **Target B:** H-09 **confirmed** (9 fresh cases, both locale modes, low and high surrogates, both trigger fields). BC-PX-049 **confirmed** for
  duration (source assertions, watchdog copy run under asyncio, addon stub flows). Contracts 3-4 re-scoped (AM-1) to repeat CONV-ABS-14/BC-PX-024
  and BC-PX-037 for `/v1/messages*` paths on other hosts. No new effect.
- **Target C:** PR-3, PR-5, PR-6 given final wording. A fresh sweep found 4 more mentions (PR-11..PR-14), none resting on a retracted fact.
- **Target D:** totals unchanged (232).
- **Counts:** new BCs 0; new crash rows 0; new ODs 0; retractions 0; scope amendments 1 (AM-1); count corrections 1 (CC-1); refinements 4 (R-1..R-4);
  flag-only rows 7.

## Remaining Gaps

1. Optional owner checks: the Grafana per-session panel with at least 2 sessions; `promtool check metrics` offline on a saved scrape.
2. P3 replay verification items, stub-backend rig only: V-1 (Host header bytes plus one h2 `:authority` case, PR-5), V-2 (mitmproxy 502 bytes, h1
   and h2 variants, PR-6), V-3 optional confirmation.
3. Owner decisions: 42 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-43, OD-45). Suggested: OD-45's ruling covers both diagnostic logs (proxy
   decision log and hook log, H-09); OD-37's ruling settles BC-PX-049's inactivity rule.
4. Apply the §3.1 wording and the AM-1 contract text when the Phase-1 spec copies V-1/V-2, BC-PX-044 and BC-PX-049.
5. Not determinable from authorized sources (LOW, no spec impact): how Claude Code encodes non-ASCII custom header values (moot, since all
   dependent rows are latent); whether Claude Code can report `total_cost_usd` ≤ 0 while the transcript holds tokens (BC-SL-027 reachability); which
   duplicate session sample VictoriaMetrics keeps (BC-EX-025).

## Novelty Assessment

NITPICK

Category (iv) is effect-free: 351 statements read, 0 unstated effects. Both r7 items are confirmed, and neither is retracted. Everything else is a
wording fix or a confirmation. CC-1 corrects a count. AM-1 brings BC-PX-049's legacy description in line with contracts the index already states
(CONV-ABS-14/BC-PX-024, BC-PX-037, the BC-PX-020 mirror case); no duration claim is withdrawn and the Go contract does not change. PR-3/5/6 are final
wording. R-1..R-4 refine existing rows without a new outcome. The `Path.home()` failure cannot occur on the target platform. Removing this round's
findings would not change how the system is specified.

## Convergence Declaration

Pass 3 has converged — findings are nitpicks, not gaps.

## State Checkpoint

```yaml
pass: 3
round: 8
status: complete
files_scanned: all 6 .py files (AST partition); category (iv) read in full (dgx_statusline.py :2-153, :364-396, :640-651, :845, :876-885, :951-998 defs, :1185-1245; dgx_ledger_exporter.py :2-61, def/class lines; dgx_proxy.py :1-54, :326-336, :459-464, :516-564, def/class lines; auto_continue.py :2-61, :141-191, def lines, :274-275; dgx_preflight.py all); re-read auto_continue.py :193-270, dgx_proxy.py :98-106, :170-216, :248-256, :311-323; claude-dgx :1-82; pass-3 B, r1-r7 (grep + context), r4-r7 index/sections; pass-2 r2, r3 §1.6/§3.2, r4, r6 (read only); mitmproxy 12.3.1 options, proxy/server, proxy/mode_servers, proxy/layers/websocket (citations only)
timestamp: 2026-11-14T08:06:30Z
novelty: NITPICK
partition: {total: 1809, i_r6: 903, ii_tables: 422, iii_oos: 133, iv_read_r8: 351}
partition_by_file:
  dgx_statusline.py: {total: 742, i: 317, ii: 265, iii: 0, iv: 160}
  dgx_proxy.py: {total: 500, i: 211, ii: 71, iii: 133, iv: 85}
  dgx_ledger_exporter.py: {total: 316, i: 270, ii: 0, iii: 0, iv: 46}
  auto_continue.py: {total: 146, i: 105, ii: 0, iii: 0, iv: 41}
  dgx_preflight.py: {total: 19, i: 0, ii: 0, iii: 0, iv: 19}
  tools/backfill_cost_history.py: {total: 86, i: 0, ii: 86, iii: 0, iv: 0}
unstated_effects_category_iv: 0
reverified: {H-09: confirmed (9 cases, both locale modes), BC-PX-049: confirmed (duration); contracts 3-4 re-scoped AM-1 (no new effect)}
corrections: {CC-1: r7 '453' -> 422, PR-3/PR-5/PR-6: final wording, PR-11..PR-14: checked, none dependent}
refinements: [R-1 H-09 empty log file created, R-2 hooks disarm watchdog, R-3 _iso_ts TZ-dependent None, R-4 preflight IDNA UnicodeError]
new_bcs: 0
new_crash_rows: 0
retractions: 0
new_ods: 0
bc_index_total: 232
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r8/
next: pass 3 converged; carry Remaining Gaps to Phase 1 / the final synthesis
```
