# Pass 2 Deepening — Round 6: Domain Model (proxy shutdown and inactivity paths, re-verification of r5, mechanical completeness diff, canonical pointer) — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Re-read this round: `dgx_proxy.py:1-560`, `claude-dgx:15-30,60-185`,
  `dgx_ledger_exporter.py:20-30,200-290,398-414`, `dgx-proxy-coordinator.sh:1-50`, `dgx_statusline.py:85-90,640-652`, `ROLLBACK.md`,
  `tools/backfill_cost_history.py:30-35,80`.
- Authorized extra sources (read only, never imported or executed): **mitmproxy 12.3.1** `tools/main`, `tools/dump`, `master`,
  `addons/__init__`, `addons/script`, `addons/proxyserver`, `addonmanager`, `utils/asyncio_utils`, `options`, `proxy/server`,
  `proxy/mode_servers`, `proxy/layers/http/__init__`, `proxy/layers/http/_http1`, `proxy/layers/tls`. **Python 3.9 stdlib** (CommandLineTools
  framework, the exporter's interpreter, OD-15) `socketserver.py`, `http/server.py`, for the exporter claim only.
- Inputs read: pass-2 r4 (catalogue, schema) and r5 (corrections, OD-01..OD-34), pass-6 synthesis, extraction validation, and the earlier pass-2
  rounds' section headings (for §4). **Pass-3 round 4 (`…-pass-3-deep-behavioral-contracts-r4.md`) did not exist at write time** (checked at
  start and at 07:06Z). Nothing to reconcile, nothing edited.
- Method: static reading only. Nothing from legacy ran, no proxy, nothing networked. `CLAUDE.local.md` was not read. One scratch script
  (`scratchpad/p2r6/enum.py`, run with `/usr/bin/python3 -I`) parsed the legacy files as **text/AST data** for target C. It imports nothing from
  legacy. Its output is in `scratchpad/p2r6/diff.json` and `crosspass.txt`.
- Notation: a bare `:N` means `dgx_proxy.py`; `EX:N` = `dgx_ledger_exporter.py`; `L:N` = `claude-dgx`; mitmproxy as "mitmproxy 12.3.1 `<module>:<line>`";
  `py39 <module>:<line>` = the Python 3.9 stdlib. Addresses in examples are RFC 5737.
- Retraction numbering: pass 2 has used 1-6 and 12-14; pass 3 has used 6-8 and holds 9-11. Pass-3 round 4 runs in parallel and may claim
  numbers from 15 up, so this round uses **CONV-ABS-20** (15-19 left free for it).

---

## 0. Orchestrator settlements recorded and items closed

| Settlement (orchestrator, 2026-11-14) | Items closed | Consequence |
|---|---|---|
| `~/.mitmproxy/config.yaml` does **not** exist (the directory holds only CA files). mitmproxy runs on its defaults | r5 Remaining Gap 3; pass-3 r3 gap 1 (shared) | mitmproxy reads `config.yaml`/`config.yml` from `confdir` at startup (mitmproxy 12.3.1 `tools/main:86-90`). Absent file → every option not passed by the launcher keeps its default. Now **verified, not just consistent:** `listen_host=""` (all interfaces), `block_private=False`, **no `proxyauth`** (the r5 §1.1 row "unauthenticated … not separately verified" is now verified), `connection_strategy=eager`, default body-size options (P-S4 holds as written), and `tcp_timeout=600` (new consequence, §1.3) |
| OD-27, hylo side: the hylo exporter binds loopback by default; a wider bind is opt-in config (D15) with a warning, under the HY-BIND rules. The legacy-side live risk stays accepted by the owner | r5 Remaining Gap 2; the "(exporter default: confirm)" qualifier on OD-27 | **OD-27 is fully ruled.** HY-BIND-5 loses its "for owner confirmation" marker and becomes a default like HY-BIND-1..3 (§3) |

---

## 1. Target A — what mitmproxy 12.3.1 does with in-flight flows at shutdown, and the 36 unpaired DGX requests

### 1.1 Signals: which ones mitmdump handles

| Fact | Source |
|---|---|
| mitmdump installs handlers for **SIGINT and SIGTERM only** (`loop.add_signal_handler`). SIGTERM → `master.shutdown`; SIGINT → `prompt_for_exit` if the master has one, else `shutdown`. `DumpMaster` has none, so SIGINT = SIGTERM | mitmproxy 12.3.1 `tools/main:117-133`; `tools/dump:10-26` |
| SIGPIPE is set to ignored. **No other signal is touched**: a search of the whole package finds no `SIGHUP` | `tools/main:137-138`; package-wide search |
| So **SIGHUP and SIGKILL kill mitmdump at once with the default disposition**: no hook, no `done`, no ledger line | consequence (Python installs no SIGHUP handler of its own) |
| The launcher's trap is `EXIT INT TERM`, **not HUP**. It sends a plain `kill` (SIGTERM) to the mitmdump PID. `claude` is not `exec`'d, so the EXIT trap runs after Claude Code exits | `L:97,185` |

### 1.2 The SIGTERM path, step by step (static)

1. `shutdown()` sets `should_exit`; `run()` leaves `await self.should_exit.wait()` and, in its `finally`, awaits `done()` → **`DoneHook`** to all addons
   (`master:90-101,106-107`).
2. No addon closes connections at `done`: the script addon only cancels its reload watcher and **stays registered** (`addons/script:105-107`);
   `addons/proxyserver` has no `done` hook (no `def done` in the module). Client and server connection tasks are still alive when `run()` returns.
3. `run()` returns; the eager task factory is restored to the previous one on the way out (`utils/asyncio_utils:90-100`); `asyncio.run(main())`
   ends (`tools/main:140-143`). CPython's `asyncio.run` then **cancels every remaining task and runs the loop until they finish**, then shuts down
   async generators and the default executor. *This step is CPython `asyncio.runners` behavior, not re-read this round (the 3.12 stdlib is outside the
   authorized sources). It is the documented contract of `asyncio.run`.*
4. A cancelled connection task does **not** die silently. `handle_connection` catches `CancelledError`, marks the connection `CLOSED`, and still
   calls `server_event(ConnectionClosed(connection))` before re-raising (`proxy/server:283-308,327-328`).
5. That event reaches the HTTP layer:
   - client side (through TLS, `proxy/layers/tls:440-450`): the client-facing `Http1Server` is in `wait` once the request is complete
     (`_http1:331-336`), and `ConnectionClosed` there yields **`Client disconnected.`** (`_http1:125-145`);
   - server side: before response headers → **`server closed connection`** (`_http1:436-458`); inside a chunked SSE body → h11 EOF error →
     **`HTTP/1 protocol error: peer closed connection without sending complete message body`** (`_http1:88-107`).
   Whichever arrives first, `handle_protocol_error` sets `flow.error` and yields **`HttpErrorHook`** unless the response is already done
   (`proxy/layers/http/__init__:723-744`). The second close finds the flow errored and adds no second hook.
6. `server_event` turns the hook into a **new task** (`proxy/server:425-431`, `hook_task` `:356-359`). That task did not exist when `asyncio.run`
   collected the tasks to cancel, so it is not cancelled. Its first step runs before the loop stops: it is queued while a cancelled task is still
   running, ahead of the completion callbacks that stop the loop. In that one step it runs `handle_hook` → `handle_lifecycle` →
   `trigger_event` → `invoke_addon`, all synchronous for this chain (`proxy/mode_servers:69-75`; `addonmanager:232-241,264-272,285-292`). No
   default addon ahead of `ScriptLoader` defines an async `error` hook (`addons/__init__:34-67`; the only `error` hooks are in `save`,
   `savehar`, `dumper`, `view`, all synchronous). So **the legacy `error()` runs and writes `dgx_upstream_error`** (`:311-323`).

**Verdict (MEDIUM, static; the one unread link is step 3):** on **SIGTERM/SIGINT**, in-flight `/v1/messages` flows **do** get the `error` hook. They
are **not** orphaned. They are logged as `*_upstream_error` with the same three texts that ordinary cancels and backend drops produce, so in the
ledger they **cannot be told apart from user cancels** (OD-16). The response hook is not called for them.

### 1.3 New failure mode F-2: mitmproxy's 600 s inactivity timeout cuts silent flows

| Fact | Source |
|---|---|
| Option `tcp_timeout`, default **600** s: "Connections will be closed after this period of inactivity". The launcher does not set it and there is no `config.yaml` (§0), so 600 s is in effect | mitmproxy 12.3.1 `options:240-246`; `L:75` |
| One `TimeoutWatchdog` per **client** connection handler. Activity is registered on **every** `server_event` of that handler, i.e. any bytes from Claude Code **or from the upstream server** on that tunnel. The watchdog is paused only while a hook runs | `proxy/server:50-88,116-120,387`; `proxy/mode_servers:70` |
| On expiry: `on_timeout` cancels the client connection task ("Closing connection due to inactivity") | `proxy/server:344-354` |
| The cancelled task then goes through §1.2 step 4-5 **while the loop is running**. The flow gets **`Client disconnected.`**, the `error` hook runs normally, and legacy writes `dgx_upstream_error` (or `anthropic_upstream_error`) with that text | as §1.2 |

**Consequence.** Any flow whose tunnel carries **no bytes in either direction for 600 s** is cut by the proxy, and the cut is logged and counted
(`dgx_llm_request_errors_total`, `EX:208-210`) as **a client cancel**. Candidates on the DGX lane:
- a **non-streaming** DGX request (buffered JSON, `:200-206`) whose generation takes more than 10 minutes. The backend sends nothing until the reply
  is complete;
- a streaming request that sits in the backend's queue or prefill for more than 10 minutes before its first event. Whether vLLM sends any byte before
  the first token is **unverified**.

The launcher raises Claude Code's own API timeout to **30 minutes** because "local 753B model is slow; allow long responses"
(`API_TIMEOUT_MS=1800000`, `L:104`). The proxy's ceiling is therefore **3x lower than the client's**. This applies to every DGX-lane request,
and nothing in the legacy tree mentions it. On the Anthropic lane, streamed replies carry periodic events, so the cut is unlikely there (judgment).
No prior pass records `tcp_timeout`: a search of every pass file finds no `tcp_timeout`, "inactivity" or 600 s idle limit.

Identification in the existing ledger (cheap owner check, no networking): an error event carries no `duration_s`, but the r4 §3.3 / r5 C-6 near-key
pairs it with its request. A `Client disconnected.` event whose `t` is about **600 s** after its request's `t` is an inactivity cut, not a user cancel.

**hylo requirement (HY-TIMEOUT-1, proposed):** the proxy's in-flight timeout must be at least the client's API timeout (configurable per D15, default
derived from the launcher's `API_TIMEOUT_MS`). The HY-BIND-6 read-header and idle timeouts apply to **idle client connections between requests**,
never to a request waiting on its upstream. Owner item **OD-35**.

### 1.4 Settling the "36 unpaired DGX requests" explanation

The 36 comes from counts: `dgx_request` 4755 − `dgx_reply` 4696 − `dgx_upstream_error` 23 = **36** (r4 §3.2 ledger counts). It is a lower bound on
requests without a terminal event, because a `dgx_reply` with no `_dgx` (a DGX-host flow the addon did not route, r4 #2) adds to the reply count
without pairing any request.

r5 §2.5's hypothesis was "flows cut off by proxy shutdown (the launcher's trap and kill)". **Split verdict:**

| Shutdown path | In-flight flow outcome | Orphan? | Basis |
|---|---|---|---|
| Trap `kill` = **SIGTERM** (and SIGINT) | `error` hook runs → `*_upstream_error` | **No** (CONV-ABS-20) | §1.2 |
| **SIGHUP**: terminal window, tab or tmux pane closed while a request is in flight | process dies at once, no hook | **Yes** | §1.1. *Delivery is judgment, OS-level, not source-read:* the launcher runs mitmdump with `&` in a non-interactive zsh (`L:75`), so it stays in the launcher's process group, and a hangup reaches that group directly or via the parent shell's job SIGHUP. Either route reaches mitmdump, and it has no handler |
| **SIGKILL**, crash, forced logout/reboot after the grace period | no hook | **Yes** | default dispositions |
| Normal quit of Claude Code | Claude Code's sockets close first → `Client disconnected.` → `error` hook, **then** the trap's SIGTERM | No | judgment (order of events at exit) |

**Other possible causes (all static; none measured):**

| # | Cause | Orphan mechanism | How to tell (owner check on the ledger, local) | Likelihood |
|---|---|---|---|---|
| O-1 | **Before the `error` hook existed.** The hook was added in response to the 2026-11-11 incident (exact build date not in the repo), when "a dead or unreachable DGX left no trace" (a terminal without Local Network permission got `No route to host` on every Sonnet request, silently) | every upstream failure or cancel before that build wrote only `dgx_request` | do the 36 cluster on or before 2026-11-11? | **High**: the docstring records exactly this blind spot (`:312-315`) |
| O-2 | Window closed (SIGHUP) or SIGKILL with a request in flight | §1.1 | is the orphan the **last** `dgx_request` of its session (no later line from that session)? | Medium |
| O-3 | Failed live reload (plain pass-through, r4 §2.1) between a request and its reply | the reply arrives while no addon is registered | do orphans sit next to `addon module loaded (PID …)` lines in the decision log (`:518`)? | Low (0 `error in script` in retained logs, r5 §0.1) |
| O-4 | Response-hook exception **before** `:272` in an older or mid-edit build (the 1 observed `NameError` was at `:250`/`:277`, after the write) | P-S class, earlier in the hook | timing against known edits; the current code has no raise path before `:272` (re-checked: `:254-274`) | Low |
| O-5 | Ledger append failed (`OSError` swallowed, `:61-62`) | reply line lost | not detectable | Very low |
| O-6 | Pairing artifacts (only if the 36 came from heuristic pairing rather than the count difference) | 61 lines lack `req_bytes`, 4570 lack `path`; null sessions collapse | recount by session | n/a for the count figure |

F-2 (inactivity cut) is **not** an orphan cause: it writes an error event. It is a misclassification cause (OD-16).

The schema does not change. Reader rule (r4 §3.2, r5 C-6) stands: **never assume a request has a reply or an error.**

---

## 2. Target B — re-verification of round 5's three SUBSTANTIVE findings

| r5 finding | Verdict | Evidence re-read this round |
|---|---|---|
| **F-1** exporter stalls on one idle connection | **CONFIRMED, with 3 refinements** | `EX:414` `HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()`. `HTTPServer` is a plain `TCPServer` subclass; only `ThreadingHTTPServer` mixes in threads (py39 `http/server:132,144-145`). `serve_forever` "Handle one request at a time" → `_handle_request_noblock` → `process_request` → `finish_request` inline (py39 `socketserver:215-237,303-320,341-360`). `StreamRequestHandler.timeout = None`, so `setup` never calls `settimeout` (py39 `socketserver:784,790-793`). `handle_one_request` blocks in `self.rfile.readline(65537)` (py39 `http/server:393-402`). An immediate close returns an empty line and ends the connection, so port scanners do not stall it (r5's claim holds). **Refinements:** (a) the stall also happens on a **partial header block**, since `parse_headers(self.rfile)` blocks too (py39 `http/server:344`); (b) keep-alive **cannot** cause it: `protocol_version = "HTTP/1.0"` (py39 `http/server:623`) and the exporter does not override it, so every connection closes after one response. Only an idle or slow-sending client stalls the server; (c) while stalled, new connections wait in the listen backlog (`request_queue_size = 5`, py39 `socketserver:441`) and are refused beyond that. The module-level `state_lock = threading.Lock()` (`EX:27`, used `EX:239,288`) is **vestigial**: there is only one thread. It corroborates that a threaded server was intended but never wired |
| **CONV-ABS-14** `anthropic_upstream_error` = "any non-DGX host"; empty attribution does not identify the side | **CONFIRMED, plus one symmetric refinement** | `error()` filters only on `flow.request.path.startswith("/v1/messages")` (`:316`), picks `lane = "dgx" if flow.request.host == self.dgx_host else "anthropic"` (`:319`), and takes `_dgx` or `_attrib` or `{}` (`:318`). `_attrib` is set only after the host check, the parse and the dict check (`:103-117`). **Refinement:** the mirror case exists for the DGX name. A flow addressed **directly** to the backend's host (for example an absolute-form `POST http://192.0.2.10:8080/v1/messages` through the proxy) never passes the `api.anthropic.com` gate. On failure it writes `dgx_upstream_error` with **no attribution**, and the exporter counts it under `("unknown", "unknown")` (`EX:208-210`). Claude Code never does this; a local process or (legacy) LAN client can. So **neither error event name identifies the lane by itself**: `dgx_*` means "host equals the configured backend host", `anthropic_*` means "any other host" |
| **L1** plain-HTTP absolute-form use of the backend key, no TLS, no CA | **CONFIRMED** | In regular mode a non-CONNECT HTTP/1 request with an absolute-form target already carries its host, so the host-header branch is skipped (mitmproxy 12.3.1 `proxy/layers/http/__init__:224-254`). The target is then rewritten to origin form (`:256-261`). The `request` hook sees `host == "api.anthropic.com"` and a `/v1/messages` path. **No scheme check exists** (`:103`), so R5 applies: scheme, host and port switch to the backend and `Authorization: Bearer <key>` is set (`:161-164`). Admission rule unchanged (r5 §1.1). With no `config.yaml` (§0) there is no `proxyauth`. Legacy risk stays owner-accepted (OD-24) |

No retraction of any r5 finding. CONV-ABS-20 retracts only the trap-SIGTERM half of r5 §2.5's **hypothesis** (§1.4), which r5 had labeled
unverified.

### 2.1 Retraction (this round)

| Marker | Prior claim (file) | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-20** | r5 §2.5: the launcher's `kill` on `EXIT INT TERM` ending mitmdump mid-flow "writes neither `dgx_reply` nor `dgx_upstream_error`" (hypothesis, MEDIUM-LOW) | On SIGTERM/SIGINT, mitmproxy cancels connection tasks; each cancel still produces `ConnectionClosed` → `HttpErrorHook` → legacy `error()` → `*_upstream_error`. Only **SIGHUP** (not trapped by the launcher, not handled by mitmdump) and SIGKILL leave a request without a terminal event. Pre-hook-era requests (O-1) are the other strong candidate | §1.1-1.4 |

---

## 3. Owner-decision list delta (base: r5 §3.2, OD-01..OD-34)

| ID | Change | Status |
|---|---|---|
| OD-27 | Hylo exporter default confirmed: loopback, wider bind opt-in with warning (HY-BIND-5 now a default) | **R** (fully) |
| OD-16 | Rationale widened. `Client disconnected.` covers four causes: user cancel, proxy inactivity cut at 600 s (F-2), proxy SIGTERM shutdown mid-flow (§1.2), and the client side of any cut. The recommendation is unchanged (reproduce through cutover; `reason` field after) | P |
| OD-28 | Note: the shutdown and inactivity cuts produce the same fixed mitmproxy strings, so "emit mitmproxy's fixed strings for deterministic causes" covers them | P |
| **OD-35** (new) | **Proxy inactivity ceiling.** Legacy cuts any flow silent for 600 s (F-2), below the launcher's 30-minute client timeout. Decide: reproduce 600 s for parity, or approved failure-mode deviation | P. Recommendation: deviation. HY-TIMEOUT-1: in-flight timeout ≥ client API timeout, configurable (D15); idle-between-requests timeouts (HY-BIND-6) kept separate. Parity replay is unaffected (no recorded input reaches 600 s of silence unless captured; flag any that do) |
| **OD-36** (new) | **In-flight flows at proxy exit.** Legacy records them on SIGTERM (as cancels) but not on SIGHUP or SIGKILL (orphans). Decide hylo's exit semantics | P. Recommendation: handle SIGHUP like SIGTERM (Windows: console close / CTRL_CLOSE, via `internal/platform`), drain for a bounded deadline, then write one error event per remaining flow. The text is out of byte parity (OD-28); the event name is unchanged (D7) |

**Count: 36 items (OD-01..OD-36): 34 pending, 2 ruled (OD-24 legacy side + hylo default; OD-27 legacy side + hylo default).**
Risk ranking (r5 §3.3) unchanged except that **OD-35 joins the top set next to OD-17**. Both are connection-management deviations, and OD-35 can
silently fail long local generations.

---

## 4. Target C — mechanical completeness diff of the pass-2 domain model

### 4.1 Method

`enum.py` (scratch) walks every file under `legacy/`. Python files: AST top-level `def`/`class` names, top-level assignments, class methods and
class attributes, `if __name__` block names, every `os.environ.get`/`os.getenv`/`os.environ[...]` key, every `ledger(...)` first argument, and
string constants that look like paths or files. Shell and plist files: `$VAR`/`${VAR}` names, path-like tokens, plist `<string>` values. Each unique
token was then searched literally in the six pass-2 files (broad, r1-r5). Tokens absent from all of them were then searched in every other pass file,
and finally checked **by concept** (a different spelling or a description) in pass 2.

| Token class | Unique tokens | Absent from pass-2 text by literal name |
|---|---|---|
| `ledger()` call sites | 11 distinct first arguments at **12 call sites** | 1 (the f-string `f'{lane}_upstream_error'`) |
| Env vars (Python: **27**, matching r1's 27; shell `$VAR`s) | 61 | 3 |
| Module-level names, methods, class attributes, `__main__` names | 202 | 74 |
| Path-like literals, plist strings | 85 | 28 |
| **Total** | **359** | **106** |

### 4.2 Disposition of the 106

| Group | Tokens | Disposition |
|---|---|---|
| Ledger | `f'{lane}_upstream_error'` (`:322`) | **Covered.** It is schema rows #4 and #8. All 12 call sites map one-to-one onto r4 §3.2 rows #1-#12 (`:154` #1, `:272` #2, `:276` #3, `:322` #4/#8, `:134`+`:139` #5, `:245` #6, `:247` #7, `:188` #9, `:101` #10, `:213` #11, `:536` #12). **Ledger diff: 0** |
| Env | `START_RANGE`, `END_RANGE`, `LOCK` | **Not env vars.** Local shell variables of the unwired coordinator (`dgx-proxy-coordinator.sh:9-10`). Its range 8090-8143 and lock file are in r3 §3.3. **Env diff: 0** (all 27 Python env reads and every launcher knob are in pass 2) |
| Covered under another name | `_SSETap.KEEP`/`__init__`/`_scan`/`_absorb_cache`/`cache` (SSE tap entity, r4 §3.1, r5 #29); `RL_PREFIX` (rate-limit header set); `DGX_BLOCK_TYPES` ("six-type" normalization); `DECISION_LOG` (decision log, `DGX_PROXY_DECISIONS`); `_MIX_CACHE`, `statusline-mix-%s.json` (mix cache); `COST_HIST` (`cost-history.json`); `PRICES`, `session_cost` (backfill price table); `_STOP_REASON_ALIASES`, `extract_stop_reason` (`finish_reason` aliasing); `PILL_*` (lane pill); `_SUB_GLYPH`, `main_subagent`, `render_subagent_rows` (subagent rows, OD-14); `MITMPROXY_DIR`, `STATE_PATH`, `TRUST_CERT_NAME`, `BACKUPS_TO_KEEP`, `_read_state`, `_write_state`, `_file_fingerprint`, `_login_keychain`, `cmd_trust_*`, `_build_parser`, `.mitmproxy.bak-*`, `~/.mitmproxy/mitmproxy-ca-cert.pem` and the trust CLI's help and message strings (CA store / trust state / keychain / fingerprint / backups entity, r3 §3.1); `$HOME/.config/dgx-llm/profile.env` (launcher env, r2 §6.7); `${TMPDIR}/dgx-mitm.$$.$PORT.log` (per-window mitmdump log, r4/r5); `websocket_start`/`websocket_end` (`ws_closed` dead path, r2 §4.5); `cache_fields`, `_current_size`, `Handler.log_message`, `_ANSI`, `truecolor`, `_fmt_tokens`, `_norm_pt`, `mix_labels`, `mix_segment`, `render_telemetry*`, `non_english`, `opus_verdict`, `ANNOUNCE` (functions or regexes of entities already catalogued; their behavior is pass-3 material) | **Covered.** No new entity |
| Thresholds and named constants | `COST_*`, `GIT_TTL`, `HIST`, `HIST_MIN_GAP`, `HTTP_TIMEOUT`, `IDLE_AFTER`, `NARROW_COLS`, `REBUILD_EXCESS`, `RL_KEEP`, `SPARK_*`, `STALE_OK`, `TURN_*`, `MIN_USD`, `MIN_BACKFILL_API_MS` (backfill 30-minute floor = BC-BF-010's 1,800,000), `TRACE_KEYS`/`_SPARK_FIXED`/`_SPARK_FLOOR` (sparkline trace map for `DGX_SL_TRACE`, which is in pass 2) | **Covered by value** in pass 4 / pass 3 and the r1 §6.2-6.3 CONFIG map. Configuration, not entities |
| Files genuinely absent from pass 2 | `${TMPDIR}/dgx-shared-mitm.<port>.log` (coordinator, **unwired**); `${TMPDIR}/opus-router.<pid>.log` (visible mode, whose `opus_router.py` is **absent** from `legacy/`, pass 0 and r2 env table); `/tmp/dgx-ledger-tunnel.log` and the tunnel's `ServerAlive*`/`ExitOnForwardFailure` options (in pass 3, a log with no consumer); `/Library/Keychains/System.keychain` (only printed as a hint, never touched, `:698-699`); `ROLLBACK.md`'s DGX-side scripts (documentation, DGX side, out of hylo scope); `/bin/zsh` (shebang) | **NITPICK.** Write-only logs of dead or external paths, or strings never acted on. None is read by any component, none is a D7 surface |
| Vestigial state | `state_lock` (`EX:27`) | **NITPICK** (§2, F-1 corroboration) |
| Launcher oddity | not a token miss, found while reading `L:15-30`: the visible-mode router port probe (4141-4199, `nc -z` loop) runs **even in invisible mode**, and its `PORT` is then unused | **NITPICK.** Harmless startup cost; noted for P4 (hylo has no router) |

**Diff result: 0 new entities, 0 new ledger events, 0 new env inputs, 0 schema errors.** The only files missing from pass 2 are write-only logs of
unwired or absent paths. One non-mechanical finding came from target A instead: the **mitmproxy option** `tcp_timeout` (F-2), a runtime default,
not a legacy token, so no source enumeration could have found it.

---

## 5. Target D — Pass 2 canonical pointer (authoritative location per topic, for Phase 1)

Read the base location first, then apply the listed amendments in order. Later rounds amend; they never restate whole tables.

| Topic | Authoritative base | Amendments (apply in order) |
|---|---|---|
| **Entity catalogue** (all bounded contexts) | r4 §3.1 (`…-pass-2-deep-domain-r4.md`) | r5 §2.2 CONV-ABS-13 (exporter state = 19 accumulators + 3 dict states + 5 scalars); r5 C-5 (28 metric names); r5 C-7/C-8 and §1.1 (proxy listener and exporter admission); r5 §2.4 F-1 and r6 §2 (exporter process lifecycle); r6 §1.1-1.3 (proxy process: signals, F-2 inactivity cut) |
| **Ledger schema** (13 events, writer contract, field order, consumers) | r4 §3.2 | r5 C-1 (`anth_reply` carries the defective `cache_write_5m_tok` too), C-2 (defect window and exact derivation), C-3 (`bridge_ws_close` = every bridge response), C-4 (`anth_ratelimit` on every Anthropic response, `session: null` shared slot), CONV-ABS-14 and r6 §2 (error event names identify the host, not the lane; both can carry empty attribution) |
| **Correlation / pairing** | r4 §3.3 | r5 C-6 (near-key works on the Anthropic lane; replies without requests exist); r6 §1.4 (the 36: count-derived lower bound; causes O-1..O-6; SIGHUP/SIGKILL vs SIGTERM) |
| **Error-text table** (`*_upstream_error.error`) | r4 §1.3 table | r5 CONV-ABS-14 (empty attribution not diagnostic); r6 §1.2-1.3 (shutdown and inactivity cuts emit the same texts) |
| **Routing decisions, request body, normalization, flow attributes** | r2 §4.1-4.5 | r3 §4.3 (`count_tokens`, live); r4 §3.1 rows *Routing decision*, *Tool set*, *Flow attribution* |
| **Upstream connection model** (mitmproxy) | r4 §1.1-1.3 | r5 §0.1 / C-10 (HTTP/1.1 observed: h2 sticky mode not live); r6 §1.3 (600 s inactivity) |
| **Cache wire formats** (session, mix, git, cost history) | r1 §3.1-3.6 (`…-pass-2-deep-domain.md`) | r2 §0 (`NaN`/`Infinity` tokens); r4 §3.1 *Session cockpit* rows; r5 §2.1 row 32 (keys re-verified) |
| **Status line stdin schema** | r1 §1.1-1.3 | r3 §0.1 (owner capture: strict stdio, Python 3.11.7 oracle, numeric `COLUMNS`) |
| **Transcript schema and incremental parser** | r1 §2.1-2.5 | r4 §3.1 *Transcript record* (CONV-ABS-4 acceptance) |
| **Telemetry (VictoriaMetrics) response and recording rules** | r1 §4.1-4.3 | r3 §2.1-2.3 (per-series table, P6 backend requirements); r5 C-9 (exact-label pricing) |
| **Hook stdin, Kev wire format, hook stdout and log grammar** | r2 §6.1-6.5 | — |
| **Launcher `--settings`, child env, env-bool grammar** | r2 §6.6-6.8 | r3 E-5 |
| **CONFIG map (D15)** | r1 §6.1-6.3 | r2 §0 and §6.8 (env-bool grammar); OD-01/OD-05 |
| **Trust, CA, preflight, coordinator** | r3 §3.1-3.3 | r4 §0.2 (port race confirmed); r6 §4.2 (coordinator log, unwired) |
| **Backfill** | r2 §7 | r3 E-4; OD-13, OD-31 |
| **Crash catalogues** | index in r4 §3.1 (closing paragraph) | status line: pass-3 r2 table (43 IDs, canonical over r1's numbering; crosswalk r2 §0.1); proxy P-R1..R4 / P-S1..S4: r2 §4.6 + r3 §1.1 (P-S production-confirmed r4 §0.1); exporter E-01..E-09, E-20, E-21: r2 §5.2 + pass-3 r2 BC-EX-021; hook H-01..H-08: r2 §6.3; backfill B-01..B-08: r2 §7. Failure modes outside crash catalogues: **F-1** (r5 §2.4, r6 §2), **F-2** (r6 §1.3) |
| **Owner-decision list** | r5 §3.2 (OD-01..OD-34) | r6 §3 (OD-27 fully ruled; OD-16/OD-28 notes; OD-35, OD-36 new). Pass-3 r4's canonical BC index and OD mapping, when it lands, must be read alongside |
| **LAN exposure and bind requirements** | r5 §1.1-1.4 (admission, L1-L7, N1-N5, HY-BIND-1..6) | r6 §0 (no `config.yaml`: unauthenticated verified; HY-BIND-5 now a default); r6 §2 (L1 re-confirmed); r6 §1.3 (HY-TIMEOUT-1 next to HY-BIND-6) |
| **Retractions** (CONV-ABS crosswalk) | r5 §0.3 table | r6: **CONV-ABS-20** (trap-SIGTERM orphans). Cite as `P2-CONV-ABS-n` / `P3-CONV-ABS-n` (r4 §0.3 recommendation) |

Superseded and not to be used for Phase 1 without the amendments: broad pass 2's ledger schema (11 events; r4 has 13 with variants) and r4's
"15 keyed accumulators" and "27 metric families" figures.

---

## Delta Summary

| Target | New | Refined / confirmed |
|---|---|---|
| Settlements | 2 recorded; r5 gaps 2 and 3 and pass-3 r3 gap 1 closed; "unauthenticated" now verified; OD-27 fully ruled | — |
| A shutdown | **F-2: 600 s inactivity cut** (mitmproxy `tcp_timeout`, never configured, below the launcher's 30-minute client timeout; logged as `Client disconnected.`); SIGHUP/SIGKILL = orphan path (no handler, not trapped); 6 alternative orphan causes with owner checks, O-1 (pre-hook era) the strongest | SIGTERM path traced end to end: the `error` hook fires (CONV-ABS-20 retracts the trap-SIGTERM half of r5 §2.5); "36" re-derived as a count difference and lower bound |
| B re-verification | — | F-1 confirmed + 3 refinements (partial headers, HTTP/1.0 rules out keep-alive, backlog 5) + vestigial `state_lock`; CONV-ABS-14 confirmed + mirror case (`dgx_upstream_error` with empty attribution for direct-to-backend flows); L1 confirmed |
| C completeness | 0 entities, 0 events, 0 env inputs, 0 schema errors | 359 tokens enumerated, 106 absent by name, all dispositioned (covered, constants, or write-only logs of dead paths) |
| D pointer | canonical pointer table (20 topics) | — |
| Decisions | OD-35 (inactivity ceiling), OD-36 (exit semantics) | OD-16, OD-28 notes; OD-27 ruled |

Existing items refined: 7 (F-1 ×3, CONV-ABS-14 mirror, OD-16, OD-28, OD-27).

## Remaining Gaps (verbatim-carryable)

1. Owner capture, VictoriaMetrics (unchanged): one `/api/v1/query` response for the exact `QUERY` (`dgx_statusline.py:102-123`) on an idle box,
   under light load, and with fewer than 20 TTFT samples, after the DGX soak is scored. Look for `"NaN"`/`"+Inf"`/`"-Inf"` in `value[1]` per `__name__`.
2. Owner local ledger check (cheap, no networking), for the 36 orphans: (a) how many have `t` on or before 2026-11-11 (O-1, pre-`error`-hook era);
   (b) how many are the last `dgx_request` of their session (O-2, window closed).
3. Owner local ledger check (cheap): for the 4 DGX and 20 Anthropic `Client disconnected.` events, pair each with its request by the near-key and
   report `t(error) − t(request)`. Values near 600 s are F-2 inactivity cuts, not user cancels (decides how much of OD-16 is F-2).
4. Not determinable from authorized sources (LOW): whether vLLM's streaming endpoint sends any byte before the first token (decides whether F-2 can
   hit streamed DGX requests or only non-streaming ones), and whether Claude Code sends non-streaming Sonnet `/v1/messages` requests. Also the
   CPython 3.12 `asyncio.run` cancel step (§1.2 step 3) was not source-read. It is the documented contract.
5. Owner decisions: 34 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-36).

## Novelty Assessment

Novelty: SUBSTANTIVE

Most of this round is confirmation, closure and pointers, and on its own would be NITPICK: the three r5 findings were re-verified with no retraction,
the mechanical diff found **no** missing entity, event, env input or schema error, the settlements closed two gaps, and §5 is a pointer table. The
SIGTERM/SIGHUP analysis settles a known hypothesis and corrects one of its halves (CONV-ABS-20). That is a refinement: the reader rule "never assume
a request has a reply" already covered it.

One finding meets the stated bar of a **new failure mode**: **F-2, the 600 s inactivity cut** (mitmproxy `tcp_timeout` default, in effect because
neither the launcher nor a `config.yaml` sets it). No prior pass of either kind recorded it. It silently fails any DGX-lane request that is silent
for 10 minutes, below the 30-minute client timeout the launcher deliberately sets, and it logs those failures as user cancels. Removing it would
change the spec: it adds HY-TIMEOUT-1 and owner item OD-35, and it changes how OD-16's cancel count must be read. It is a single item. Under the
protocol's binary rule a new failure mode is SUBSTANTIVE, so the round is SUBSTANTIVE. The entity model, the ledger schema and the
token-level completeness diff are now stable. Round 7 should target only Remaining Gaps 2-4 and a check that no other mitmproxy **default option**
(the class F-2 came from) shapes legacy behavior unrecorded.

## Convergence Declaration

Another round needed — F-2 (mitmproxy's unconfigured 600 s inactivity timeout) is a new failure mode surfaced this round. The suggested next scope is
a sweep of mitmproxy 12.3.1's default options (`options.py` and the addon `load()` option declarations) for any other default that shapes legacy
behavior, plus owner checks 2-3.

## State Checkpoint

```yaml
pass: 2
round: 6
status: complete
files_scanned: dgx_proxy.py (1-560), claude-dgx (15-30, 60-185), dgx_ledger_exporter.py (20-30, 200-290, 398-414), dgx-proxy-coordinator.sh (1-50), dgx_statusline.py (85-90, 640-652), ROLLBACK.md, tools/backfill_cost_history.py (30-35, 80); all legacy files AST/text-enumerated for target C; mitmproxy 12.3.1 (tools/main, tools/dump, master, addons/__init__, addons/script, addons/proxyserver, addonmanager, utils/asyncio_utils, options, proxy/server, proxy/mode_servers, proxy/layers/http/__init__, proxy/layers/http/_http1, proxy/layers/tls); Python 3.9 socketserver, http/server
timestamp: 2026-11-14T07:10:00Z
novelty: SUBSTANTIVE
retractions: [CONV-ABS-20]
new_failure_modes: [F-2 mitmproxy 600 s inactivity cut logged as client cancel]
target_c_diff: 359 tokens, 106 absent by name, 0 new entities/events/env inputs/schema errors
owner_decisions: 36 (OD-01..OD-36; 34 pending, 2 ruled: OD-24, OD-27)
pass3_r4_reconciled: not present at write time
next: pass 2 round 7 (targets = Remaining Gaps 2-4 + mitmproxy default-option sweep)
```
