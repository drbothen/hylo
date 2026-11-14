# Pass 2 Deepening — Round 3: Domain Model (mitmproxy semantics, telemetry rules, trust/coordinator/preflight, ledger history, re-checks) — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Re-read in full this round: `dgx_proxy.py` (764), `dgx_ledger_exporter.py` (414),
  `claude-dgx` (185), `dgx-proxy-coordinator.sh` (50), `dgx_preflight.py` (41), `deploy/*.plist`; in part: `auto_continue.py:1-40,90-140,190-275`,
  `dgx_statusline.py:95-190,1180-1195`, `tools/backfill_cost_history.py:25-35`.
- Extra read-only sources authorized by the orchestrator for this round (private, cited by repo-relative name only):
  **mitmproxy 12.3.1** (the prototype venv's version; `version.py:5`), modules `addonmanager`, `addons/script`, `addons/proxyserver`, `http`,
  `coretypes/multidict`, `net/http/headers`, `net/http/http1/read`, `proxy/mode_servers`, `proxy/layers/http/{__init__,_http1,_events,_hooks}`,
  `certs`, `options`. Never imported or executed. **dgx-llm deploy/recording.yml** (375 lines) and `deploy/alerts.yml:65` (the one line that names a
  statusline series).
- Inputs read: every file in this directory (broad passes, extraction validation, pass-2 r1 and r2, pass-3 broad and deep r1; pass-3 files read only,
  not edited), `docs/PLAN.md` D13-D16, `.factory/specs/research/domain-hybrid-routing-claude-code-2026-11-14.md` §3.4-3.5.
- One public documentation page was consulted (MetricsQL reference on docs.victoriametrics.com) for VictoriaMetrics NaN semantics; no project data was sent.
- Method: static reading. Two scratch runs (Python language semantics only, `-I`, files in `scratchpad/p2r3/`): PEP 604 annotation on 3.9.6 vs 3.11.7,
  and `urllib.parse` port semantics on 3.11.7. Marked **[scratch-verified]**. Nothing legacy, networked or proxy-related was run. `CLAUDE.local.md` was not read.
- Line numbers are those of the named file. A bare `:N` means `dgx_proxy.py` unless the section says otherwise.

---

## 0. Owner capture received this round, protocol re-checks (target E), and retractions

### 0.1 Owner capture: status line environment (closes round-2 gap 1)

Method (reported by the orchestrator, 2026-11-14): the r2 §1.3 probe ran as the `statusLine` command of an interactive `claude --settings …` session.
Plain `claude` was used instead of the launcher. This is equivalent for these facts because `claude-dgx` exports no `LANG`/`LC_*`/`PYTHON*`/`PATH`
variable (r2 §1.1, grep-verified again this round). The session ran in a tmux pane.

| Captured fact | Value | Consequence |
|---|---|---|
| `LANG` | `en_US.UTF-8` | — |
| `LC_ALL`, `LC_CTYPE`, `LC_MESSAGES`, `PYTHONUTF8`, `PYTHONIOENCODING`, `PYTHONPATH` | all unset | — |
| interpreter | Anaconda python3 on PATH, **3.11.7** | The status line **and** Stop-hook oracle is Python 3.11.7 (same `python3` on the same PATH, `claude-dgx:161,176`). It satisfies the hook's ≥ 3.10 requirement (`auto_continue.py:94`, §0.2 E-6) |
| `sys.flags.utf8_mode` | `0` | — |
| stdin / stdout | `utf-8` / `strict` both | **Harness stdio = STRICT is CONFIRMED** (was "probable" in r2 §1). Matches the owner ruling. CONV-ABS-3 stands |
| preferred / filesystem encoding | `UTF-8` / `utf-8` | — |
| `COLUMNS` | `80` (Claude Code sets it to the terminal width) | `COLUMNS` is **present and numeric in production**. The absent/non-numeric branch of `term_cols()` (`dgx_statusline.py:1185-1190`) is a robustness path, not a production one |
| `TERM` | `tmux-256color` (pane-specific; `xterm-256color` in iTerm2) | **Legacy does not consume `TERM`.** Grep over all legacy sources: the only `TERM` token is the signal name in the launcher's `trap … EXIT INT TERM` (`claude-dgx:97`). No harness pin needed |
| `PATH` | captured, deliberately **not recorded** (private) | — |

Harness parameters now settled for the status line and hook: `LANG=en_US.UTF-8`, the other locale/Python variables unset, Python 3.11.7, `COLUMNS` numeric.
This matches the owner's CI ruling (status line 3.11).

### 0.2 Re-check of round 2's riskiest claims against the source

| # | Round-2 claim | Verdict | Evidence |
|---|---|---|---|
| E-1 | **P-R4**: if the key file is unreadable, the request still goes to the DGX with Claude Code's own `Authorization` | **CONFIRMED, upgraded from LOW to HIGH.** The ordering is static: host/scheme/port switch (`:161-163`), then `self._key()` evaluated on the right-hand side of `:164` raises before the header assignment. mitmproxy 12.3.1 then continues the flow (§1.1): `safecall` logs `Addon error: …` and swallows the exception (`addonmanager:45-58`, `trigger_event:285-295`). The HTTP layer, after `HttpRequestHook` returns, checks only `check_killed` and `flow.response`, then calls `make_server_connection` to `(flow.request.host, flow.request.port)`, i.e. the DGX (`proxy/layers/http/__init__:376-410,757-771`). Refinements: (a) the backend scheme defaults to `http`, so the OAuth bearer crosses the LAN **in cleartext**; (b) `anthropic-beta` is not popped (`:165` not reached); (c) `_key_cache` stays `None`, so every DGX-lane request repeats it until the file is readable (`:91-95`); (d) the `failed-req-*.json` capture saves only the **body**, not headers (`:294-296`), so the exposure leaves no on-disk header copy. Separately, an `x-api-key` header is forwarded on **every** DGX-lane request even when the key file is fine (known: pass 4, extraction validation row 70); now in the owner list as item 7 | as cited |
| E-2 | **H-04**: `kev_pdone_median` returns `(p, None)` when the last attempt fails after a success, and the `{secs:.2f}` format then raises (exit 1, no stdout, no log) | **CONFIRMED.** `t` is reassigned on every attempt (`auto_continue.py:130`), the early stop needs `t is not None` (`:133`), the return is `ps[len(ps)//2], t` (`:138`), and the format is `f"…({secs:.2f}s)"` (`:250`). The `_log`/`emit` calls come after `:250`, so nothing is logged. Sequences (ok,ok,fail), (ok,fail,fail), (fail,ok,fail) all reach it | `auto_continue.py:124-138,246-252` |
| E-3 | **Exporter crash loop** on one bad ledger line under launchd `KeepAlive` | **CONFIRMED, refined.** `__main__` calls `rebuild()` before binding (`dgx_ledger_exporter.py:410-414`). Inside `rebuild` only `ValueError` from `json.loads` (`:117-120`) and `FileNotFoundError` around the file (`:211`) are caught, so E-01 (`ev.get` on a non-object, `:121`) and E-02 (`strptime` on a non-str `t`, `:125`, which raises `TypeError`, not `ValueError`) end the process. `KeepAlive` true (`plist:10`) restarts it into the same crash. Refinements: (a) the restart cadence is launchd's respawn throttle (documented default 10 s; not verified here), so this is a slow loop, not a busy loop; (b) the committed plist names its script as `~/hylo/legacy/…` (`plist:7`), which launchd does not expand (BC-SV-001): the scrubbed artifact as committed cannot start at all, and the claim concerns the real (absolute-path) agent | as cited |
| E-4 | **Backfill prices** differ from the documented prices (Haiku read 0.005 vs 0.01; no Haiku > 100K tier; no Fable/Mythos) | **CONFIRMED** (`tools/backfill_cost_history.py:28-32` vs research §3.5). New: the **same** 0.005 appears in the external recording rules (`dgx_price:haiku_cache_hit_usd_per_mtok`, dgx-llm deploy/recording.yml:85-86), whose comment says the Haiku cache prices were "derived from the documented 1.25x/2x/0.05x pattern" (:63-65). The research doc says the 0.05× read multiplier applies to Opus/Sonnet 5.5 only, other models 0.1× (§3.4). So 0.005 is one derivation error copied into two places, not two independent errors | as cited |
| E-5 | **Env count 42** (adds `HOME`, `PWD`) | **CONFIRMED by recount.** Python sources reference 27 distinct names via `os.environ`. The launcher reads 21 external names (`ANTHROPIC_CUSTOM_HEADERS`, 15 `DGX_*`, `HOME`, `PWD`, `ROUTER_PORT`, `TMPDIR`) plus 14 internal shell variables (`ARGS`, `HERE`, `LOG`, `MITM_PID`, `MITM_PORT`, `MLOG`, `PF_MSG`, `PF_PY`, `PORT`, `PROFILE`, `ROUTER_PID`, `DGX_PROJECT_HEADER`, `DGX_USER_HEADER`, `DGX_USER_LABEL`). The overlap is 6 (`DGX_AUTOCONTINUE`, `DGX_ENGLISH`, `DGX_KEV_MODEL`, `DGX_KEV_THRESHOLD`, `DGX_KEV_URL`, `DGX_UPSTREAM`). 27 + 21 − 6 = **42**. The coordinator adds only `TMPDIR` (already counted). **Implicit** inputs (not counted in the 42, but harness parameters): `TZ` (local-time `t` and log stamps), `LANG`/`LC_*` (§0.1), `PATH` (which `python3`, `claude`, `security`), `HOME` via `expanduser`, and `HTTPS_PROXY`/`HTTP_PROXY`/`NO_PROXY`, which urllib honors in the hook's Kev call (the status line opts out with `ProxyHandler({})`, `dgx_statusline.py:166-168`). `TERM` is **not** an input (§0.1) | shell recount this round |
| E-6 | **Stop hook fails to import on Python 3.9** | **CONFIRMED** **[scratch-verified]**: `def kev_pdone(state: str, question: dict \| None = None)` raises `TypeError: unsupported operand type(s) for \|: 'type' and 'NoneType'` at definition on 3.9.6 (exit 1), and defines fine on 3.11.7. No `from __future__ import annotations` in `auto_continue.py` (the only PEP 604 use in the non-proxy sources; `dgx_statusline.py:241` has the pattern inside a docstring only). Moot for production now: the captured oracle is 3.11.7 (§0.1) | `auto_continue.py:94`; scratch `p2r3/pep604.py` |

### 0.3 Retractions and corrections

| Marker | Prior claim (file) | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-6** | Pass 6 synthesis line 43 "trust CLI's `remove`/`rotate` **always** crash", and extraction validation row 67 "`rotate` touches `args.force` **unconditionally** (:703)" | `rotate` touches `args` only through `_mitmdump_running() and not args.force` (`:703`). The `and` short-circuits, so **`rotate` crashes (AttributeError on `None.force`) only when `pgrep -f mitmdump` finds a process.** With no proxy running, `rotate` runs: it archives `~/.mitmproxy` to `~/.mitmproxy.bak-<stamp>` (`:709-713`), prunes backups to 3 (`:715-717`), runs `DGX_PROXY_RESTART_CMD` if set (`:719-725`), and otherwise exits 1 with "Fresh CA not found — start the proxy yourself, then re-run `trust install`." (`:726-727`), **after** having moved the CA away. `remove` crashes iff a keychain entry exists (it reaches `args.yes` at `:687` on every such path; `args.force` at `:684` only on a fingerprint mismatch). Pass-3 BC-PX-031 ("remove/rotate crash") holds only with these conditions | `dgx_proxy.py:676-735,759-761` |
| Correction (orchestrator premise, not a pass claim) | "`anthropic_upstream_error` is an event name absent from the pass-2 ledger schema; probably historical" | **It is current.** The `error` hook writes `ledger(f"{lane}_upstream_error", …)` with `lane = "dgx" if host == dgx_host else "anthropic"` (`:319-323`), so `anthropic_upstream_error` is emitted today for every Anthropic-lane `/v1/messages*` flow that errors. The broad pass-2 schema lists it (row 9, `hylo-legacy-pass-2-domain-model.md:69`). Only `anthropic_reply` is historical (§4) | `dgx_proxy.py:311-323` |

Hallucination-class audit of round 2: no phantom entities, no over-extrapolated token lists. One metric re-derived (env 42, confirmed). Round 2's
"Proxy: venv, version not pinned" is superseded: the venv is CPython **3.12** with **mitmproxy 12.3.1** (site-packages path and `version.py:5`), which
matches the owner's CI ruling (proxy 3.12).

---

## 1. Target A — mitmproxy 12.3.1 semantics that decide legacy proxy behavior

### 1.1 Addon exceptions: logged, swallowed, flow continues

| Fact | Source (mitmproxy 12.3.1) |
|---|---|
| Every hook is dispatched by `trigger_event`, which wraps **each addon** in `safecall()` | `addonmanager:285-295` |
| `safecall` re-raises only `AddonHalt`/`OptionsError`. Any other exception is logged at ERROR as `Addon error: <exc>` with a trimmed traceback and **swallowed** | `addonmanager:44-58` |
| The proxy server awaits `handle_lifecycle(hook)` and then the flow's resume. There is no kill-on-error path | `proxy/mode_servers:69-74` |
| After `HttpRequestHook`: if killed → error; elif `flow.response` set → reply locally; **else open/reuse an upstream connection to `(request.host, request.port)` with TLS iff `request.scheme == "https"`** and send the request as it now stands | `proxy/layers/http/__init__:376-410,757-771` |
| After `HttpResponseHeadersHook`: stream iff `flow.response.stream` is truthy, else buffer | `__init__:423-430` |
| After `HttpResponseHook`: unless killed, the (buffered) response is **sent to the client** | `__init__:494-535` |

Resolution of the round-2 proxy crash catalogue (r2 §4.6), outcome column now source-backed:

| ID | Outcome (HIGH unless noted) |
|---|---|
| P-R1, P-R2 | `Addon error` logged to mitmdump's stdout, i.e. the per-window log `$TMPDIR/dgx-mitm.<pid>.<port>.log` (`claude-dgx:74-75`). The flow goes to **api.anthropic.com unchanged** except `Accept-Encoding: identity` (`:131`). No `anth_request`. On reply: `anth_reply` without `lane` (`_attrib` exists), and `anth_usage` with the default lane `anthropic` (`:247`). A would-be DGX request is silently served by Anthropic (plan usage) |
| P-R3 | Same as P-R1. Normalization runs before the host switch and before `set_text` (`:145-150`), so the **original** body bytes go to Anthropic; `_dgx` unset; no `dgx_request` |
| P-R4 | See §0.2 E-1: request **sent to the DGX** with the client's credentials. `dgx_request` already written (`:154`). The reply (likely 401 from an auth-enforcing backend; backend behavior is external) is logged as `dgx_reply` (status ≥ 400 → error metric, failed-req capture) |
| P-S1 | Response hook raises before any ledger write: no `anth_reply`, no `anth_usage`. **The client still receives the response** (it is sent after the hook) |
| P-S2, P-S3 | `*_reply` written, `*_usage` lost; client receives the response |
| **P-S4 (new)** | DGX lane, status ≥ 400 **and** `content-type` containing `text/event-stream`. `responseheaders` tests SSE first (`:196`), so the error body is **streamed** (tapped), and a streamed body is never stored (`store_streamed_bodies` default False; the response is created with `content=None`, `net/http/http1/read:299-305`; `__init__:473-475`). `get_text(strict=False)` then returns `None` (`http:427-432`), and `None[:600]` at `:287` raises `TypeError` (not `OSError`). Already written: `dgx_reply` (and `dgx_usage` if the tap saw usage). Lost: the error-body note and the `failed-req-*.json` capture. Realism LOW (vLLM reports in-stream errors with status 200); listed for catalogue completeness |

### 1.2 `get_text` / `get_content` on streamed and buffered flows (resolves BC-PX-034 path (b))

| Case | Return value | Legacy consequence |
|---|---|---|
| Streamed response (`stream=True` or a callable tap) | `raw_content is None` → `get_content` → `None` → `get_text` → `None` (`http:385-388,427-430`) | `json.loads(None)` raises **`TypeError`**, caught at `:234`/`:307`. **BC-PX-034 path (b) in the tapped-but-no-usage case yields no usage, via `TypeError`.** No `anth_usage` |
| Buffered, valid encoding | decoded `str` | normal |
| Bad `content-encoding`, `strict=True` (request side, `:106`) | `ValueError` | caught at `:107` → note `unparseable /v1/messages body…` → passthrough |
| Bad `content-encoding`, `strict=False` (response side) | raw (still-compressed) bytes, then decoded as below | `json.loads` fails → caught |
| Charset inference | BOM first; then `charset=` param; then `"json" in content-type` → UTF-8; …; fallback **latin-1** (`net/http/headers:39-112`) | Claude Code's `application/json` request bodies decode as UTF-8, so `req_bytes` (`:123`) is a **code-point** count (CONV-ABS-2 / I11 hold). A request without a JSON content type would be decoded as latin-1 (one char per byte) |
| Undecodable text, `strict=True` | `ValueError` | request side: "unparseable" passthrough |
| Undecodable text, `strict=False` | UTF-8 with `surrogateescape` | response-side notes may contain lone surrogates. Harmless, since the decision log is opened in the default locale encoding; the error-body note is ASCII in practice |
| `set_text(json.dumps(req))` (`:150`) | encodes with the content-type charset (UTF-8 for JSON) and **rewrites `content-length`** unless `transfer-encoding` is present (`http:363-383,407-425`) | the DGX request has a correct length. Its bytes are ASCII (`ensure_ascii`) |

### 1.3 Headers: repeated names, folding and iteration order (affects `_attrib` and `anth_ratelimit`)

| Operation | Semantics (`http:49-175`, `coretypes/multidict:46-136`) | Legacy consequence |
|---|---|---|
| `headers.get(name)` / `headers[name]` | case-insensitive; **all values for the name folded with `", "`** | `X-DGX-Project`, `X-DGX-User`, `X-Claude-Code-Session-Id` (`:118-120`) become `"a, b"` if the header repeats. Whether Claude Code ever sends a duplicate (e.g. a nested `claude-dgx` appending a second pair to an inherited `ANTHROPIC_CUSTOM_HEADERS`, `claude-dgx:46-49`) depends on how Claude Code parses that variable: **UNVERIFIED** |
| `headers.items()` (multi=False) | one pair per distinct lower-cased name, **in first-occurrence wire order**, keeping the first occurrence's casing; the value is the folded join | the `anth_ratelimit` `headers` object (`:178-188`) has keys in **Anthropic's wire order** (suffixes lower-cased), **not sorted**. Change detection uses `sort_keys=True` (`:185`), so a pure order change writes nothing. Go must keep first-occurrence order and the `", "` folding to reproduce the ledger bytes |
| `headers[name] = v` | `set_all`: replaces the **first** occurrence in place (position kept), drops later duplicates, appends if absent | `Authorization` (`:164`), `Accept-Encoding` (`:131,166`), `X-DGX-*` (`:156-159`) keep their original positions when present |
| `headers.pop(name, None)` | removes every occurrence | `anthropic-beta` (`:165`) |
| non-UTF-8 header bytes | decoded `utf-8` + `surrogateescape` (`http:40-41`) | a session id with such bytes would reach `json.dumps` as lone surrogates, which are escaped as `\udcXX` (ASCII). Not reachable with Claude Code's UUIDs |

### 1.4 Upstream connection timing

| Fact | Source |
|---|---|
| `connection_strategy` defaults to **`eager`**. The launcher does not override it (`claude-dgx:75`) | `addons/proxyserver:154-162` |
| In regular (explicit-proxy) mode, on `CONNECT api.anthropic.com:443` with `eager`, mitmproxy **opens the upstream connection at CONNECT time**. On failure the client receives **502** `Cannot connect to …` for the CONNECT itself. The legacy addon has no `http_connect_error` hook, so **nothing is logged to the ledger** | `__init__:773-834` |
| Each request then asks for a connection to `(request.host, request.port, tls)`. The eager Anthropic connection is reused for Anthropic-lane requests. A **DGX-lane request opens (lazily, after the `request` hook) a separate connection** to the DGX, reused for later requests on the same client connection | `__init__:1067-1159,105-123` |
| Upstream connect failure for a request → `ResponseProtocolError(CONNECT_FAILED)` → `error` hook → client receives **502 Bad Gateway** | `__init__:723-771`; `_events:100-117`; `_http1:269-277` |

**Domain consequence (new, HIGH from source):** in legacy, **the local lane depends on Anthropic being reachable.** Each Claude Code connection
starts with `CONNECT api.anthropic.com`, and with `eager` that CONNECT fails (502) if Anthropic cannot be reached, before any `/v1/messages`
request exists to route. Offline local-only use is impossible, and an Anthropic outage at connect time also takes the DGX lane down. hylo's Go
proxy is free to connect lazily. That is a behavior change visible only in failure modes, listed as owner decision 17.

### 1.5 The `error` hook also fires on client cancellation (new)

The HTTP/1 server layer turns a client FIN while the flow is in flight into `RequestProtocolError("Client disconnected.", CLIENT_DISCONNECTED)`
(`_http1:124-145`). `handle_protocol_error` sets `flow.error` and fires `HttpErrorHook` whenever the server side is not done (`__init__:723-746`).
The legacy `error` hook (`:311-323`) does not inspect the cause, so **a user cancelling a streaming reply (Esc) writes `dgx_upstream_error` /
`anthropic_upstream_error` with `error: "Client disconnected."`**. The exporter counts every `dgx_upstream_error` in `dgx_llm_request_errors_total`
(`dgx_ledger_exporter.py:208-210`). So the "DGX errors" metric includes user cancels. The code path is traced (MEDIUM: it assumes Claude Code
closes the socket on abort, which is undici behavior, not verified here). The production share is an owner local check (gap 2).

### 1.6 Script loading and live reload (process-state entity "addon generation")

| Fact | Source | Legacy consequence |
|---|---|---|
| `-s` scripts are always loaded with `reload=True` (1 s mtime poll) | `addons/script:214-218,133-152` | editing `dgx_proxy.py` reloads every running proxy (the private notes say so; confirmed in source) |
| A reload **first unregisters the old module**, then imports the new one. If the import fails, the error is logged and **no addon is registered** | `addons/script:113-131,23-57` | a syntax error or module-level exception during a reload turns every running proxy into a **plain pass-through proxy** until the file is fixed: Sonnet requests go **to Anthropic untouched** (plan usage), no ledger, no `Accept-Encoding` change. The launcher cannot detect this |
| Module-level code runs at import: `_router = DGXRouter()` (`:521`) parses `DGX_UPSTREAM` with `urlparse(...).port`, which raises `ValueError` for a non-numeric or out-of-range port **[scratch-verified]** | `:79-83` | a bad `DGX_UPSTREAM` port gives the same plain-proxy state from launch. The preflight (`dgx_preflight.py:19-20`) parses the same URL at module level and dies with a traceback, so the launcher aborts first (`claude-dgx:63-67`). The plain-proxy state is reachable only with `DGX_SKIP_PREFLIGHT=1` or through a later reload |
| If the script file **disappears** at a poll, the watcher removes it from `options.scripts` **permanently** for that process | `addons/script:136-146` | a non-atomic replace of `dgx_proxy.py` (delete, then write) can permanently de-route every running proxy, even after the file is back |
| A reload resets module state: `_logged_unknown`, `_router._key_cache`, `_router._last_rl` (r2 §4.5) | — | after a reload the first rate-limit headers per session are re-logged |
| URL without a scheme, e.g. `DGX_UPSTREAM=h:8080` → `scheme='h'`, `hostname=None`, `port=None` **[scratch-verified]** | `:80-83` | the proxy uses scheme `h`, host `192.0.2.10` (default), port 80. Port default is **80 regardless of scheme**, so `https://host` without a port connects TLS to :80 (`:83`; preflight `:20`) |

---

## 2. Target B — Recording rules behind the status line's telemetry (dgx-llm deploy/recording.yml)

All rules are in one group with `interval: 60s` (recording.yml:1-4). The evaluator (vmalert or Prometheus) is not stated in the authorized files.
The status line's query uses MetricsQL-only functions (`alias`, `label_set`; pass 1 §4.6), so the read side is VictoriaMetrics.

### 2.1 Per-series table (every series in `QUERY`, `dgx_statusline.py:102-123`)

| Series | Kind | Exact definition / source | Unit | Absent when | NaN/Inf possible? | Statusline use |
|---|---|---|---|---|---|---|
| `vllm:num_requests_running`, `vllm:num_requests_waiting` | raw (vLLM) | — | requests | vLLM not scraped | no (gauges) | queue/busy (`:732-740`), idle (`:825`) |
| `vllm:kv_cache_usage_perc` | raw (vLLM) | — | **fraction 0..1** (blocks held by running requests only; recording.yml:322-327) | vLLM not scraped | not expected | KV gauge (`:754`), sparkline `k` (`:340`) |
| `dgx_kv:host_hit_share` | recorded | `dgx_kv:host_hit_tokens_per_s / clamp_min(dgx_kv:gpu_hit_tokens_per_s + dgx_kv:host_hit_tokens_per_s, 1e-9)` (:333-336), with `gpu_hit = sum(rate(vllm:prefix_cache_hits_total[5m])) or vector(0)` (:329-330) and `host_hit = sum(rate(vllm:external_prefix_cache_hits_total[5m])) or vector(0)` (:331-332) | fraction 0..1 | **never** while rules evaluate: `or vector(0)` keeps both inputs present, so with vLLM down it reads **0** (not absent) | no: `clamp_min` prevents 0/0 | KV host share (`:755`) |
| `dgx_tokens:gen_rate5m` | recorded | `sum(rate(vllm:generation_tokens_total[5m]))` (:16-17) | tokens/s | no source sample in 5 m | no | box rate fallback (`:772`), sparkline fallback (`:344-345`) |
| `dgx_ttft:p95_30m` | recorded | `histogram_quantile(0.95, sum(rate(vllm:time_to_first_token_seconds_bucket[30m])) by (le))` (:8-9) | seconds | no bucket series | **PromQL: NaN when there are zero observations in 30 m (idle box).** MetricsQL "removes all the NaN values from the output" (VictoriaMetrics docs), so via VM the series is **absent** instead, and a NaN-valued record is not produced through a MetricsQL evaluator. A quantile landing in the `+Inf` bucket: not settled by the docs (owner capture) | TTFT widget (`:792-797`), sparkline `f` (`:341`); also `alerts.yml:65` `dgx_ttft:p95_30m > 2` |
| `dgx_preempt:rate5m` | recorded | `sum(rate(vllm:num_preemptions_total[5m]))` (:18-19) | preemptions/s | no source | no | busy rule (`:740`), sparkline `p` (`:346`) |
| `dgx_llm_last_dgx_request_timestamp_seconds` | raw (**hylo exporter**) | exporter gauge, emitted only after the first `dgx_request` (`dgx_ledger_exporter.py:367-370`) | unix s (local wall time parsed naive; TZ-sensitive, r2 §5.1) | no DGX request ever, or the exporter is down or crash-looping (E-*) | no | idle `☾` (`:824-825`) |
| `dgx_power:est_wall_watts` | recorded | `dgx_power:total_known_watts * 1.25` (:36-37), `total_known = sum(DCGM_FI_DEV_POWER_USAGE) + (max(dgx_power_socket_watts{socket="grace"}) or vector(0))` (:34-35). 1.25 is a labeled fill factor for unmeasured fans/NVMe/BMC (:30-32) | W | no DCGM series | no | power widget (`:804`) |
| `dgx_power:rate_usd_per_kwh` | recorded | `0.12 + 0.02 * (month() >= bool 6) * (month() <= bool 9)` (:40-41): an owner-specific seasonal tariff; `month()` is evaluated in UTC | USD/kWh | never | no | power cost (`:804`) |
| `dgx_cost:dgx_usd_per_mtok` | recorded | `dgx_cost:dgx_monthly_total / clamp_min(dgx_tokens:rate_mtok_month, 0.001)` (:204-207). `monthly_total = capex_monthly + dgx_power:usd_per_month_operating` (:202-203). `capex_monthly = capex constant / 36` (:164-172). `usd_per_month_operating = dgx_power:usd_24h / 24 * 730` (:196-197). `usd_24h = avg_over_time(est_wall_watts[24h:1m]) * 24/1000 * rate_usd_per_kwh` (:48-49) | USD per MTok (cash basis) | the exporter token series or the power series are absent (exporter E-* crash loop → `⛏` absent) | no NaN (`clamp_min`), but **huge** values on low volume (0.001 floor). The status line's `MIN_BASIS_MTOK_MONTH = 30.4` exists for this reason (`dgx_statusline.py:95-98`) | `⛏` basis (`:1220`) |
| `dgx_tokens:rate_mtok_month` | recorded | `(sum(rate(dgx_llm_tokens_input_total[24h])) + sum(rate(dgx_llm_tokens_output_total[24h]))) * 730 * 3600 / 1e6` (:198-201) | MTok/month (730 h) | the exporter series are absent for 24 h | no | `⛏` volume guard (`:1223`) |
| `vllm:lmcache_mp_lookup_duration_seconds_count` | raw (LMCache) | — | count | LMCache not scraped | no | "LMCache down" test (`:713-720`) |
| `DCGM_FI_DEV_POWER_USAGE`, `DCGM_FI_DEV_GPU_TEMP` | raw (DCGM) | — | W, °C | no DCGM | no | power/temp (`:801-803`). Several GPUs → first in result order wins (`:183`) |
| `up{job=~"vllm\|lmcache"}` | raw | — | 0/1 | job not configured | no | serving health (`:716-720`) |
| `dgx_sl:gen_rate1m` | inline | `sum(rate(vllm:generation_tokens_total[1m]))` renamed + labeled `sl="1m"` | tokens/s | no source | no | box rate, sparkline `v` |
| `dgx_sl:ttft_n30m` | inline | `sum(increase(vllm:time_to_first_token_seconds_count[30m]))` + `sl="n30m"` | requests | no source | no (0 on idle) | TTFT sample size (`:794`, `TTFT_MIN_N = 20`) |

### 2.2 What this settles and what it does not

- **NaN via VictoriaMetrics (documented):** MetricsQL drops NaN from query output. A series whose instant value would be NaN is absent from the
  response rather than carrying `"NaN"`. The status line already handles absent keys. So **CP-N01/N02 via `"NaN"` are unreachable through a
  VictoriaMetrics source per its documentation**. `+Inf`/`-Inf` are not covered by that statement. The owner capture stays open unchanged
  (owner ruling): it confirms the documented behavior on the real build and settles Inf.
- Only one queried recorded series has a natural NaN source: `dgx_ttft:p95_30m`, at idle (histogram with zero observations). All divisions are
  guarded by `clamp_min`, and `host_hit_share`'s inputs are `or vector(0)`.
- **Coupling to the hylo exporter:** `dgx_cost:dgx_usd_per_mtok`, `dgx_tokens:rate_mtok_month` and the idle gauge depend on the exporter's
  `dgx_llm_tokens_{input,output}_total` and `dgx_llm_last_dgx_request_timestamp_seconds`. An exporter crash loop (r2 E-01..E-09, §0.2 E-3) shows up
  in the status line as `⛏ n/a`/absent and a missing `☾`, not as an error.
- **Sonnet on the Anthropic lane is priced at $0** by the external spend rules. `dgx_cost:anth_*_usd_rate5m` exist only for `claude-opus-5-5`
  and `claude-haiku-5-5` (:100-113). The `anthropic-server-tools` lane (Sonnet requests that declare a server tool, r2 §4.2 R4) falls into
  `dgx_cost:anth_unpriced_requests_24h` (:154-156). This does not affect the status line, whose `$` is Claude Code's `total_cost_usd`. It matters for P6
  cost config.

### 2.3 Backend requirements hylo must document for P6 (pluggable telemetry)

| Requirement | Why | Evidence |
|---|---|---|
| A **MetricsQL**-capable instant-query API (VictoriaMetrics) for the default query, or a per-source query in config | `alias`/`label_set` are not PromQL | `dgx_statusline.py:118-122` |
| vLLM metrics: `num_requests_running`, `num_requests_waiting`, `kv_cache_usage_perc`, `generation_tokens_total`, `time_to_first_token_seconds_{bucket,count}`, `num_preemptions_total`, `prefix_cache_hits_total`, `external_prefix_cache_hits_total` | status line widgets | §2.1 |
| Scrape jobs named `vllm` and `lmcache` (the `up` filter is name-bound) | serving-health widget | `dgx_statusline.py:111-113` |
| DCGM exporter (`DCGM_FI_DEV_POWER_USAGE`, `DCGM_FI_DEV_GPU_TEMP`); optional `dgx_power_socket_watts{socket="grace"}` | power widget | recording.yml:34-35 |
| The six recorded series of §2.1 (or their expressions inlined into the query), with the constants (fill factor 1.25, tariff, capex, 36-month amortization, 730 h/month) as **config** (D15) | `⛏`, power cost, KV share, TTFT | recording.yml:16-19,30-59,164-207,329-336 |
| hylo's exporter scraped by the same VictoriaMetrics, so that `dgx_llm_tokens_*` and the last-request gauge exist | `⛏`, idle | §2.2 |
| LMCache MP metrics (`vllm:lmcache_mp_lookup_duration_seconds_count`) only if LMCache is used | LMCache-down test | `dgx_statusline.py:713-720` |

---

## 3. Target C — Coordinator, preflight and trust-state entities

### 3.1 Trust state and CA material (C3, `hylo ca` target)

| Entity | Wire format / location | Writer | Reader | Failure modes |
|---|---|---|---|---|
| **CA store** `~/.mitmproxy/` | Created by mitmproxy at first start **iff `mitmproxy-ca.pem` is missing** (`certs:607-618`). Files: `mitmproxy-ca.pem` (key + cert, written under a `0o77` umask, i.e. owner-only), `mitmproxy-ca.p12`, then `mitmproxy-ca-cert.pem`, `-ca-cert.cer`, `-ca-cert.p12`, `mitmproxy-dhparam.pem` (`certs:653-705`). CN = O = `mitmproxy`, RSA **2048** (`options:7,9`), CA validity **10 years** (`certs:40`), leaf certs **199 days** (`certs:41`) | mitmdump (each proxy, at startup) | launcher (`NODE_EXTRA_CA_CERTS=…/mitmproxy-ca-cert.pem`, `claude-dgx:80`); trust CLI (`CA_PEM`, `:560-561`) | Regeneration keys on **`-ca.pem`**, the trust CLI checks **`-ca-cert.pem`**. Deleting only `-ca.pem` makes the next proxy mint a new CA while the trust state still describes the old one (the `status` DRIFT row catches it only when keychain and file differ). Running proxies keep the CA they loaded, which is why `rotate` refuses while mitmdump runs |
| **Trust state** `~/.dgx/trust-state.json` (`DGX_TRUST_STATE`) | `json.dump(state, indent=2, sort_keys=True)` + `"\n"`; keys `installed_at` (local `%Y-%m-%dT%H:%M:%S`, no TZ), `installed_sha256` (lower-case hex without colons, **or `null`** when `openssl` failed), `keychain` (path string). Written via `mkstemp(dir=parent, prefix=".trust-state.")` (mode 0600) + `os.replace` (`:616-622,631-632`) | `trust install` (both the "already trusted" and the "added" paths, `:633-642`) | `status` (`installed_at` only, `:658,666`), `remove` (`installed_sha256`, `:683`). `rotate` does not read it | parse error or missing → `{}` (`:609-613`). `remove` with no keychain entry deletes the state file (`:681`) |
| **Keychain entry** (login keychain) | `security add-trusted-cert -r trustRoot -k <login keychain> <CA_PEM>` (`:638-639`). Keychain path from `security login-keychain` stripped of whitespace and quotes, else `~/Library/Keychains/login.keychain-db` (`:567-572`) | `trust install` | `_keychain_fingerprint`: `security find-certificate -Z -c mitmproxy <kc>` → the first output line containing "hash" with a 64-character token (the SHA-256 line), lower-cased (`:589-602`). Without `-a` only the **first** certificate whose name matches is examined | `-c` matches by name, so a different CA named "mitmproxy" (e.g. user-imported) is indistinguishable except by fingerprint. `remove` deletes up to 10 matching entries in a loop (`:691-695`) |
| **Fingerprint** | `openssl x509 -noout -fingerprint -sha256` → text after `=`, colons removed, lower-cased (`:575-586`) | — | install/status/rotate | `openssl` missing → `None`; `status` then shows "one side missing" or "cannot verify" |
| **Backups** `~/.mitmproxy.bak-<YYYYmmdd-HHMMSS>` | `shutil.move` of the whole dir; the 3 newest kept (lexical sort = chronological) (`:709-717`) | `rotate` | — | two rotations within the same second: `shutil.move` into an **existing** directory nests the old dir inside it. `rotate` without `DGX_PROXY_RESTART_CMD` and with no proxy running ends with exit 1 after the move (CONV-ABS-6), by design a two-step flow |

CLI surface and exit codes: `claude-dgx trust …` → `exec python3 dgx_proxy.py trust "$@"` (`claude-dgx:11-14`), with the PATH `python3` (Anaconda 3.11.7,
§0.1). `mitmproxy` is not importable there, which is tolerated (`:42-46`). `sys.exit("<msg>")` → message on stderr, exit 1. A missing or unknown subcommand
→ argparse exit 2. Any non-`trust` first argument → usage on stderr, exit 2 (`:759-764`). macOS-only: on other OSes the `security` binary is missing and
`subprocess.run` raises `FileNotFoundError` uncaught (traceback, exit 1).

**Conflict with D13 (no action, recorded):** legacy installs the CA as a `trustRoot` in the **login keychain**. D13 says hylo's CA is "never added to an
OS trust store" and is trusted only through `NODE_EXTRA_CA_CERTS`. So `hylo ca` replaces the install/remove/rotate semantics instead of porting
them. Parity (D4) has nothing to reproduce here beyond the CA file location contract.

### 3.2 Preflight (C7)

| Aspect | Rule | Line |
|---|---|---|
| Invocation | the launcher runs it unless `DGX_SKIP_PREFLIGHT == "1"`, with `.mitmenv/bin/python` (invisible mode; Local Network permission is per app and inherited) or `python3` (visible mode). Argument `${DGX_UPSTREAM:-http://192.0.2.10:8080}`. stdout and stderr are captured together (`2>&1`) | `claude-dgx:60-67` |
| Probe | `socket.create_connection((host, port), timeout=4)`, connect only, no TLS, no HTTP; `host = hostname or 192.0.2.10`, `port = port or 80` (scheme ignored) | `dgx_preflight.py:18-24` |
| Error classes (first match wins) | `EHOSTUNREACH` → Local Network permission text; `socket.timeout` (= `TimeoutError` on 3.10+) or `ETIMEDOUT`/`EHOSTDOWN` → "timed out / host down"; `ECONNREFUSED` → "vLLM is not listening"; any other `OSError` (incl. DNS `gaierror`) → generic `cannot reach …: <e>`. All exit 1 | `:25-41` |
| Non-OSError failures | an invalid port in the URL raises `ValueError` at module level → traceback, exit 1 → the launcher prints `claude-dgx: preflight failed: <traceback>` and exits 1 | `:19-20` **[scratch-verified]** port semantics |
| Launcher contract | failure → two stderr lines plus exit 1, Claude Code not started. Success → silent | `claude-dgx:63-67` |

### 3.3 Coordinator (C8, unwired) and the launcher's real port allocation

The coordinator is **not referenced** by the launcher or any other legacy file (grep this round; pass 1 C8 "unwired" confirmed). Its entity model is still recorded,
because the intent ("one shared proxy") is a live design question for hylo:

| Entity | Form | Line |
|---|---|---|
| State dir | `<script dir>/.proxy-state/` holding `port` (decimal + newline), `pid` (decimal + newline), `lock` (flock target) | `dgx-proxy-coordinator.sh:7-9,37` |
| Validity | `port` non-empty **and** `lsof -iTCP:<port> -sTCP:LISTEN` output contains `mitmdump` **and** `kill -0 <pid>` succeeds | `:14-24` |
| Allocation | first port in 8090..8143 with no listener (any process), start mitmdump with the addon, poll LISTEN ≤ 40 × 0.25 s, write state | `:26-38` |
| Lock | `flock 9` on `lock` in a subshell | `:40-47` |
| Dead code | `STALE_SEC=120` never used | `:11` |
| Hazards (static) | `flock` is not part of base macOS. Without it the command fails (127), `set -e` is off, so the script **runs unlocked**. A venv console script is exec'd through its Python interpreter, so `lsof`'s COMMAND column may not read `mitmdump` (**UNVERIFIED**; the shebang is outside the authorized sources). If it does not, validity never holds and `start_new` always fails after starting a proxy. The started proxy is never stopped by anyone | `:15,28,43` |

**The launcher's own allocation (production path), with a race (new):** `claude-dgx` picks the first port in 8090..8143 that `nc -z` finds closed,
starts mitmdump in the background, and declares success as soon as `nc -z` sees a listener on that port (`claude-dgx:72-78`). Two windows launched
within the bind window both choose the same port. The second mitmdump fails to bind and exits, but the second launcher's readiness probe succeeds
against the **first** window's proxy. The second window then runs against the first window's proxy, with the first window's environment (upstream,
prefixes), and loses it when the first window exits (its `trap` kills that proxy, `claude-dgx:97`): every API call fails for the rest of the session.
Attribution stays correct, since the headers come from each Claude Code process. Static analysis, MEDIUM. Also: in invisible mode the launcher still
probes the router ports 4141..4199 and exits 1 if all are busy (`claude-dgx:17-22`), though no router is used.

---

## 4. Target D — Historical ledger event names and lines without `path`

### 4.1 Event-name census (orchestrator ledger totals) vs current writers

| Event | Ledger total | Current writer? | Consumers and handling |
|---|---|---|---|
| `anth_request` / `anth_reply` / `anth_usage` | 6210 / 6189 / 5984 | yes (`:134,139,245,247`) | exporter (r2 §5.1) |
| `dgx_request` / `dgx_reply` / `dgx_usage` | 4755 / 4696 / 4564 | yes (`:154,272,276`) | exporter |
| `anth_ratelimit` | 261 | yes (`:188`) | **no legacy consumer** (exporter ignores it; the status line uses stdin `rate_limits`) |
| `dgx_upstream_error` | 23 | yes (`:322`) | exporter: `errors[(project,user)] += 1` (`dgx_ledger_exporter.py:208-210`); not in session errors |
| `anthropic_upstream_error` | 20 | **yes, current** (`:322`, §0.3) | exporter: **ignored** (no branch). No other consumer |
| `anthropic_reply` | 258 | **no**: historical name, renamed to `anth_reply` on 2026-11-10 (`dgx_ledger_exporter.py:204-205`; broad pass 2 row "—") | exporter: counted in `dgx_llm_anthropic_passthrough_total` iff `status == 200` (`:206-207`), and its `t` feeds `last_ts`. Not counted in `anth_req`/`anth_in` (different names). The exporter's own comment explains why the old name stays: counting only it "froze this counter at 257" |
| `bridge_ws_connect`, `bridge_ws_close`, `ws_closed` | not reported | `bridge_*` current (`:101,213`); `ws_closed` dead (`:536`) | exporter: ignored except `t` → `last_ts` |

Every event, whatever its name, advances `dgx_llm_last_request_timestamp_seconds` if its `t` parses (`:121-126`). The status line, Stop hook and backfill
**never read the ledger** (grep: no ledger path or event name in `dgx_statusline.py`, `auto_continue.py`, `tools/backfill_cost_history.py`). The status
line sees the ledger only through VictoriaMetrics scraping the exporter.

**Arithmetic that the census supports** (evidence; hypotheses labeled):
- `anth_request − anth_reply = 21`, `anthropic_upstream_error = 20`. Nearly every unanswered Anthropic request has an error event. The remaining 1 fits
  a flow cut by proxy shutdown, or P-S1 (which also suppresses `anth_reply`).
- `dgx_request − dgx_reply = 59`, `dgx_upstream_error = 23`. **36 DGX requests have neither a reply nor an error event.** Hypothesis (not verified):
  proxies killed with flows in flight (the launcher's `trap` kills mitmdump when a window exits, `claude-dgx:97`, so neither hook fires).
- `anth_reply − anth_usage = 205`: count_tokens (31, no `usage`), status ≥ 400 buffered bodies, JSON replies without `usage`. With 5,820 tapped
  Anthropic flows and no `usage=None`, every tapped stream yielded usage (gap 3 closed below).
- `dgx_reply − dgx_usage = 132`: the 5 count_tokens replies (JSON, never tapped, BC-PX-020), status ≥ 400 replies, non-SSE replies.

### 4.2 Lines without `path` (older lines: 4631 dgx, 3562 anth)

`path` was added on 2026-11-12 (`:124-126`). **No legacy consumer reads `path`.** The exporter's only `path` is the HTTP handler's `self.path`
(`dgx_ledger_exporter.py:271`). So absence changes no exposition byte. Consequences for meaning: before 2026-11-12, `count_tokens` calls cannot be told
apart from billed calls. On the DGX lane they count in `dgx_llm_requests_total`, `dgx_llm_est_prompt_tokens_total` and the duration families, but never
in token counters (no tap). On the Anthropic lane they count in `dgx_llm_anthropic_requests_total` and passthrough. **Requirement for new hylo consumers
(D16 event API, web UI, `hylo top`, any ledger replay):** treat `path` as optional, `anthropic_reply` as an alias of `anth_reply`, and
`anthropic_upstream_error` as a current event. Never assume every request has a matching reply or error (§4.1).

### 4.3 Gaps 3 and 5 closed with the orchestrator's local evidence

- **Gap 3 (SSE usage) closed.** 5,820 `anth tap:` decision-log lines, none with `usage=None` (the line format is `:240-241`). In production every tapped
  Anthropic stream carried a top-level `usage` with `input_tokens`, so `anth_usage` was written. The DGX lane: `dgx_reply − dgx_usage = 132` is
  explained by untapped flows (§4.1). The legacy code path (BC-PX-034) is unchanged and remains the parity definition. "Docs permit streams without top-level
  `input_tokens`" stays a theoretical Go robustness case, not a production one.
- **Gap 5 (count_tokens) closed.** Claude Code sends `POST /v1/messages/count_tokens` for Sonnet models, the proxy routes them to the DGX (r2 §4.2 R5),
  and the backend answered all 5 with 200. So **the backend serves the endpoint**, and legacy's DGX routing of `count_tokens` is live behavior.
  Also 31 on the Anthropic lane. D13's wording ("only `POST /v1/messages` … is ever rewritten") does not cover this. Owner decision 10.

---

## 5. Consolidated owner decisions pending (rounds 1-3, deduplicated; rulings removed)

Already ruled, so not listed: CI Python 3.11 (status line) / 3.12 (proxy); harness stdio STRICT (now also capture-confirmed, §0.1); degraded output byte-for-byte
for catalogued crash paths; foreign-cache paths CP-C01..C10 out of parity scope, with the Go writer producing legacy's exact cache format; D4-EX-1 `⌂` on Windows;
D4-EX-2 skip wrong-shape transcript lines (fixes the sticky crash); D13 intercept all hosts; D14 no proxy env in children; D15 config over code; D16 web UI + TUI
on a live event API. The status-line/hook interpreter question (r2 #13) is resolved by the ruling plus §0.1. Only the exporter part remains (item 15).

| # | Decision | Origin | Recommendation (one line) |
|---|---|---|---|
| 1 | CONFIG key naming and the `HYLO_*` derivation rule | r1 #1 | Derive mechanically: `HYLO_` + upper-snake of the dotted key, no hand-picked names. |
| 2 | Whether status line glyphs are config | r1 #2 | Yes, `statusline.glyphs.*` with legacy defaults (D15 says presentation values are config). |
| 3 | Windows sid sanitizing for cache file names (I8) | r1 #3 | Sanitize only on Windows (replace characters invalid in filenames), byte-identical names elsewhere. |
| 4 | One `paths.hook_log` key for writer and reader | r1 #4 | One key, defaulting to the legacy path, so writer and reader cannot diverge. |
| 5 | Env-bool grammar for `DGX_*` aliases (`DGX_STATUSLINE=true` disables) | r2 #5 | Keep the per-variable legacy string rules for `DGX_*`; typed booleans for `HYLO_*` only. |
| 6 | **P-R4**: backend key unreadable → client credentials sent to the backend (now HIGH, §0.2 E-1) | r2 #6 | Approve a deviation: fail closed with a local 502 and an error ledger event, never contact the backend. |
| 7 | **`x-api-key` and other Anthropic auth headers forwarded** on every DGX-lane request | pass 4 gap, r3 | Approve a deviation: strip `x-api-key`/`Authorization`/cookies before adding the backend key (matches D16's "never forwarded"). |
| 8 | P-R1..R3: a request-hook exception silently re-lanes a would-be DGX request to Anthropic | r2 #7 | Reproduce in the P3 replay (parity), but make hylo log a visible routing-error event. |
| 9 | `document` and other non-six-type blocks dropped on the DGX lane | r2 #8 | Parity now; after cutover, a config routing rule that sends such requests to Anthropic. |
| 10 | `count_tokens` for local models goes to the backend (live, 5/5 answered 200) vs D13's "`POST /v1/messages` only" wording | r2 #9, r3 §4.3 | Keep legacy behavior and amend D13's wording to "`/v1/messages` and `/v1/messages/count_tokens`". |
| 11 | Exporter poison-line behavior (E-01..E-21, startup crash loop) | r2 #10 | Skip and count bad lines (e.g. a `…_ledger_bad_lines_total` metric) as a documented deviation, mirroring D4-EX-2. |
| 12 | Hook H-04 (`(p, None)` crash, exit 1 with no log) | r2 #11 | Fix: report the elapsed time of the last successful call; document it as a deviation (calibration data otherwise lost). |
| 13 | Price tables: backfill and external rules share the Haiku read 0.005 error; no Haiku > 100K tier; no Fable/Mythos; Sonnet on the Anthropic lane unpriced in the VM rules | r2 #12, r3 §0.2 E-4, §2.2 | Prices become config (D15): legacy defaults for parity runs, documented prices as the post-cutover defaults. |
| 14 | `subagentStatusLine` still emitted for Claude Code ≥ 2.1.323 (key removed upstream) | r2 #14 | Config toggle `run.subagent_statusline`, default on for parity, documented as ignored by newer Claude Code. |
| 15 | Exporter parity oracle: launchd `/usr/bin/python3` 3.9.6, empty environment (UTF-8 mode on) | r2 #13 remainder | Pin 3.9.6 with an empty env for exporter parity, since E-09 decoding and the int-digit limit are version-sensitive. |
| 16 | **Client cancels counted as DGX errors**: the `error` hook fires on "Client disconnected." (§1.5) | r3 | Reproduce for parity (D7 freezes the metric); after cutover, a `reason` field on the event, metric unchanged. |
| 17 | **Eager CONNECT**: Anthropic unreachable at connect time → the DGX lane fails too (§1.4) | r3 | Go proxy connects upstream lazily (an approved deviation in failure modes only), so local-only use works. |
| 18 | Proxy response-hook crash paths P-S1..P-S4 (ledger events lost, client unaffected) | r2 §4.6, r3 §1.1 | Reproduce the ledger effects in the P3 replay; they are corruption-only except P-S4, which is LOW. |
| 19 | Launcher port race (two windows can share one proxy, §3.3) and the unwired coordinator | r3 | Out of parity scope: hylo binds its own listener (port 0 or a lock) and drops the coordinator. |
| 20 | P6 telemetry backend contract (§2.3): MetricsQL query, job names, recorded series, constants as config | r3 | Accept §2.3 as the documented backend requirement, with the query and every constant in config. |

**Top 5 by risk:** 6 (P-R4 credentials), 7 (`x-api-key` forwarding), 11 (exporter crash loop), 17 (eager CONNECT couples the lanes), 10 (count_tokens vs D13).

---

## Delta Summary

| Target | New items | Highlights |
|---|---|---|
| Owner capture | 1 evidence table (9 rows) | STRICT stdio confirmed; oracle Python 3.11.7; `COLUMNS` supplied by Claude Code; `TERM` not consumed |
| E re-checks | 6 verdicts: 6 confirmed (P-R4 upgraded LOW → HIGH with 4 refinements; H-04; crash loop + throttle/plist refinements; prices + shared-origin finding; env 42 + implicit-input list; 3.9 import) | the Haiku 0.005 error exists in two places from one derivation |
| Retractions | **CONV-ABS-6** (rotate crashes only while mitmdump runs; it otherwise archives the CA and exits 1) + 1 premise correction (`anthropic_upstream_error` is current) | — |
| A mitmproxy | 6 subsections: exception semantics (6 facts) and outcomes for P-R1..R4, P-S1..S3; **new P-S4**; `get_text` table (7 rows); header table (5 rows); connection timing (4 facts); **error hook on client cancel**; script-reload entity (6 rows) | **eager CONNECT couples the DGX lane to Anthropic reachability**; user cancels inflate `dgx_llm_request_errors_total`; a failed reload or vanished script de-routes every live proxy to a plain pass-through; `anth_ratelimit` key order = wire order; BC-PX-034 (b) resolved (`TypeError` on `None`) |
| B recording rules | 18-row series table (definition, sources, unit, absent/NaN behavior, use); 7-row backend requirement table | via VictoriaMetrics, NaN is documented as dropped (CP-N01/N02 NaN unreachable per docs; Inf open); only `dgx_ttft:p95_30m` has a natural NaN source; Sonnet-on-Anthropic unpriced in the spend rules; exporter outage → `⛏`/`☾` absent |
| C trust/preflight/coordinator | 5-row CA/trust entity table + CLI exit codes; 5-row preflight table; 6-row coordinator table + **launcher port race** | regeneration keyed on `-ca.pem` vs the CLI checking `-ca-cert.pem`; legacy keychain install conflicts with D13; port race leaves a window proxy-less |
| D ledger history | 7-row event census with consumers; arithmetic (36 DGX requests with neither reply nor error); `path` absence (no consumer reads it) | requirement for D16 consumers; gaps 3 and 5 closed with the orchestrator's evidence |
| Owner decisions | consolidated list of 20 (from 4 + 14 + 6 new, minus rulings, plus split/merge) | — |

Existing items refined: r2 §4.6 (outcomes now source-backed), r2 §1 (verdict confirmed), r2 §1.4 (proxy interpreter now known: 3.12/mitmproxy 12.3.1),
r2 §2 (documented NaN semantics), r2 §3 and §4.2 (closed), pass-3 BC-PX-010/031/034 (cited, not edited), extraction validation row 67 (CONV-ABS-6).

## Remaining Gaps (verbatim-carryable)

1. Owner capture, VictoriaMetrics (unchanged): one `/api/v1/query` response for the exact `QUERY` (`dgx_statusline.py:102-123`) on an idle box, under light load, and with fewer than 20 TTFT samples, after the DGX soak is scored. Look for `"NaN"`/`"+Inf"`/`"-Inf"` in `value[1]` per `__name__`. Round 3 adds documented context: MetricsQL drops NaN from query output, so expect `dgx_ttft:p95_30m` to be **absent** (not NaN) at idle. The capture confirms this on the real build and settles Inf.
2. Owner local check, upstream-error causes: `jq -r 'select(.event|endswith("_upstream_error"))|.error' ledger | sort | uniq -c`. The share of `"Client disconnected."` tells how much of `dgx_llm_request_errors_total` is user cancels (r3 §1.5). Also count `Addon error` lines in the per-window mitmdump logs (`$TMPDIR/dgx-mitm.*.log`) to measure how often P-R*/P-S* fire in production.
3. Owner local check, the 36 DGX requests with neither `dgx_reply` nor `dgx_upstream_error` (r3 §4.1): correlate their `t` with window exits or proxy restarts (decision-log `addon module loaded` lines) to confirm or reject the "killed in flight" hypothesis.
4. mitmproxy detail not settled: whether a DGX connection that failed stays cached with `connection.error` in the client connection's `HttpLayer.connections` and fails later same-address requests without a retry (`proxy/layers/http/__init__:1071-1084`). Needs a reading of connection teardown in `proxy/server.py`. Affects only failure-mode parity.
5. Not determinable from authorized sources: which evaluator runs `deploy/recording.yml` (vmalert vs Prometheus), and so whether chained rules lag by one interval. The real launchd plist (absolute paths, throttle) is outside the repo. The `lsof` COMMAND name for the venv `mitmdump` (coordinator only, unwired). All LOW.
6. Owner decisions §5 items 1-20.

## Novelty Assessment

Novelty: SUBSTANTIVE
Removing this round would change how P3, P2/P6 and P4 are specified:
- P3 proxy: the failure model is now source-backed. P-R4 sends credentials to the backend (HIGH, was LOW), and a new **architectural coupling** appears: with eager CONNECT the DGX lane fails whenever Anthropic is unreachable at connect time. The `error` hook records **user cancels** as upstream errors (this changes what `dgx_llm_request_errors_total` means). Live reload can silently turn every running proxy into a plain pass-through. There is a new crash path (P-S4). Header folding and wire-order rules fix the `anth_ratelimit` ledger bytes.
- P6 telemetry: the recording-rule model (definitions, units, absent/NaN behavior, exporter coupling) and a concrete backend requirement list. Spend rules leave Sonnet on the Anthropic lane unpriced.
- P4 / `hylo ca`: the trust/CA entity model and its conflict with D13. The launcher port race, plus a retraction (CONV-ABS-6) of a claim that pass 6 had elevated to a top finding.
- Ledger consumers: `anthropic_upstream_error` is current, not historical. Three gaps closed with evidence (status line env, SSE usage, count_tokens).

## Convergence Declaration

Another round needed. Substantive items surfaced this round. The open questions are now narrow (gaps 2-5 are local checks or LOW-impact source readings),
and the owner decision list (20 items) is the main blocker for spec crystallization.

## State Checkpoint

```yaml
pass: 2
round: 3
status: complete
files_scanned: 8 legacy files (dgx_proxy.py, dgx_ledger_exporter.py, claude-dgx, dgx-proxy-coordinator.sh, dgx_preflight.py, 2 plists in full; auto_continue.py, dgx_statusline.py, backfill in part) + 14 mitmproxy 12.3.1 modules + dgx-llm deploy/recording.yml (full) and alerts.yml:65
timestamp: 2026-11-14T09:40:00Z
novelty: SUBSTANTIVE
retractions: [CONV-ABS-6]
next: pass 2 round 4 (targets = Remaining Gaps 1-6 verbatim)
```
