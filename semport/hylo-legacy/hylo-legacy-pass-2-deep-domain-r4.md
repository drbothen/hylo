# Pass 2 Deepening — Round 4: Domain Model (connection lifecycle, protocol re-checks, consolidated catalogue, ledger schema, owner decisions) — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Re-read this round: `dgx_proxy.py:50-66,96-190,209-336,525-540`,
  `dgx_ledger_exporter.py:1-60,110-215`, `claude-dgx:70-80`, `deploy/io.hylo.ledger-tunnel.plist` (full).
- Authorized extra source: **mitmproxy 12.3.1** (`version.py:5`), read only, never imported or executed. Modules read: `proxy/layers/http/__init__`,
  `proxy/layers/http/_http1`, `proxy/layers/http/_http2`, `proxy/layers/http/_events`, `proxy/layers/tls`, `proxy/server`, `proxy/mode_servers`,
  `proxy/mode_specs`, `addons/proxyserver`, `addons/script`, `addons/errorcheck`, `addons/block`, `addons/dumper`, `addons/next_layer`, `addonmanager`,
  `master`, `options`, and `h11/_readers` (a mitmproxy dependency in the same venv, only to locate one error string). Cited as "mitmproxy 12.3.1 `<module>:<line>`".
- Inputs read: every file in this directory (broad passes, extraction validation, pass-2 r1-r3, pass-3 broad, r1, r2), `docs/PLAN.md` phases and D13-D16.
  **Pass-3 round 3 (`…-pass-3-deep-behavioral-contracts-r3.md`) did not exist when this file was written** (checked twice, last at 06:41Z), so there was
  nothing to reconcile with it. Where this round touches pass-3 r2 claims, the reconciliation is stated inline.
- Method: static reading only. No scratch execution was needed this round (`scratchpad/p2r4/` created, left empty). Nothing legacy, networked or
  proxy-related was run. `CLAUDE.local.md` was not read.
- A bare `:N` means `dgx_proxy.py` unless the section says otherwise.

---

## 0. Orchestrator evidence recorded, audit, retractions

### 0.1 Evidence received this round (orchestrator, local, 2026-11-14) and the gaps it closes

| Gap (r3 list) | Evidence | Verdict |
|---|---|---|
| **2** upstream-error causes | `dgx_upstream_error`: 18 connect-refused, 4 `Client disconnected.`, 1 `server closed connection` (= 23, matches the r3 census). `anthropic_upstream_error`: 20 `Client disconnected.`, 1 `HTTP/1 protocol error: peer closed connection without sending complete message body` (= 21; r3's census said 20, the ledger is live, so the two snapshots differ and r3's `anth_request − anth_reply` arithmetic is not recomputed here). 38 mitmdump logs in `$TMPDIR`: exactly 1 `Addon error`, a `NameError` (`_account_hint` not defined) raised in `DGXRouter.response` during a live reload while `dgx_proxy.py` was mid-edit | **Closed.** (a) r3 §1.5 (client cancel → `*_upstream_error`) is **production-confirmed**, upgraded MEDIUM → HIGH: 4 of 23 DGX error events (17 %) are user cancels, and each one adds 1 to `dgx_llm_request_errors_total` (`dgx_ledger_exporter.py:208-210`). (b) Each message maps to one mitmproxy source line (§1.4). (c) The `NameError` is a **response-hook exception in a successfully imported module** (P-S class: the reply was already sent, the ledger lines after the raise were lost). It proves that live-reload edits reach running proxies and that P-S-type ledger losses happen. It does **not** measure the import-failure ("plain pass-through") mode: that mode logs `error in script <path>`, not `Addon error` (§2.2) |
| **3** 36 DGX requests with neither reply nor error | the ledger has no request/flow ID; pairing is heuristic only (session + timestamp order). 61 `dgx_request` lines lack `req_bytes`, 4570 lack `path` (older proxy versions) | **Closed as a recorded domain limitation** (no pairing attempted). Refinement from source (§3.3): the reply and error events copy the request's attribution, including `req_bytes`, so a composite near-key exists. It is ambiguous exactly for Claude Code retries (identical bodies) |
| **5** deploy facts | installed exporter and tunnel LaunchAgents: `KeepAlive=true`, `RunAtLoad=true`, matching `legacy/deploy/io.hylo.ledger-exporter.plist`; the exporter runs `/usr/bin/python3` with the exporter script | **Closed.** The exporter **crash loop on one bad ledger line is CONFIRMED for production** (r2 §5.2 startup amplification + r3 E-3). vmalert vs Prometheus as rule evaluator: **unknown, low impact**, recorded as a P6 backend-documentation note. The `lsof` COMMAND name for the venv `mitmdump` (unwired coordinator only): **unknown, low impact** |

### 0.2 Retractions and corrections (this round)

CONV-ABS numbers used so far: pass 2 used 1-6, pass 3 r2 used 6 and 7 (a numbering collision, see §0.3). The parallel pass-3 round 3 may claim
the next free numbers, so this round starts at **12**, leaving 8-11 for that round.

| Marker | Prior claim (file) | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-12** | r3 §1.6 row 3: "a bad `DGX_UPSTREAM` port gives the same plain-proxy state **from launch** … reachable only with `DGX_SKIP_PREFLIGHT=1` or through a later reload" | **At launch the plain-proxy state is not reachable.** mitmdump installs an `ErrorCheck` log handler that records every ERROR-level record during startup. `master.run` calls `shutdown_if_errored()` before servers start, after servers start, and after the `running` hook, and only then uninstalls it. `shutdown_if_errored` prints `Error(s) logged during startup, exiting...` and calls `sys.exit(1)`. A script import failure is logged at ERROR (`error in script <path>`). So with `DGX_SKIP_PREFLIGHT=1` and a bad port, mitmdump **exits 1 during startup**; the launcher's readiness loop then prints `invisible proxy failed to start; see $MLOG` and exits 1 (`claude-dgx:77-78`). The plain-proxy state exists **only after a reload in an already-running proxy** (the handler is gone by then). Caveat, MEDIUM: the first script load runs from the watcher task after one `sleep(0)`, so it must land before the last startup check. It does with at least two checks after real socket awaits, but this is task-order reasoning, not a run. A theoretical micro-window remains where the launcher's `nc -z` sees the listener just before the exit | mitmproxy 12.3.1 `addons/errorcheck:10-55`, `master:54-94`, `addons/script:23-71,93-98,113-152` |
| Refinement (r3 §1.4) | "Offline local-only use is impossible, and an Anthropic outage at connect time also takes the DGX lane down" | **Confirmed, with its scope.** (a) What gates is the **TCP connect** to `api.anthropic.com:443` at CONNECT time (DNS failure, refusal, unreachable, or the OS connect timeout, since mitmproxy sets no connect timeout of its own). (b) An upstream **TLS** failure does not gate: the client TLS handshake proceeds anyway ("Trying to establish TLS with client anyway"). (c) The coupling applies **per new client connection**. Tunnels that are already open keep serving DGX-lane flows if Anthropic later becomes unreachable. Claude Code opens new connections whenever its pool needs one, so an Anthropic outage degrades the DGX lane progressively, not instantly | `proxy/layers/http/__init__:786-800`; `proxy/layers/tls:606-616,627-635`; `proxy/server:206-229` |
| Refinement (r3 §2.2) | "Sonnet on the Anthropic lane is priced at $0 by the external spend rules" | **Legacy side confirmed; wording refined; rule side not re-read.** The exporter carries **no lane label** on any Anthropic family. `anth_req` is keyed by `(project, user, model_req, account)` and `anth_in` by `(project, user, model, account)` (`dgx_ledger_exporter.py:160-167`). So external rules can price only by **model**, and server-tool Sonnet requests can be told apart from other Anthropic-lane Sonnet traffic only via the ledger. The correct wording is "**unpriced** (absent from the spend sums, so $0 in them, and counted as unpriced requests)". `deploy/recording.yml` was not authorized this round, so r3's citation (recording.yml:100-113,154-156) is carried, not re-verified. In legacy, Sonnet reaches the Anthropic lane only through R4 (server tools), P-R1..R3 fail-open, and the reload pass-through state | as cited |
| Confirmed (r3 §3.3) | launcher port race: "the second mitmdump fails to bind and exits" | **Confirmed from source.** A bind failure raises `OSError("… failed to listen on *:<port> with …")`, `ServerManager.update` logs it at ERROR, and `ErrorCheck` exits 1 during startup. The rest of the race holds as stated (MEDIUM, static) | `proxy/mode_servers:252-266`; `addons/proxyserver:93-96`; `addons/errorcheck:28-46` |

### 0.3 CONV-ABS crosswalk (the numbering collided across passes)

| Number | Pass 2 meaning | Pass 3 meaning |
|---|---|---|
| CONV-ABS-1..4 | r1: 9999 default ts; char units; `LC_ALL=C` unsafe; `json.loads(bytes)` acceptance | — |
| CONV-ABS-5 | r2: CP-25 not an independent trigger | (cited, not re-used) |
| CONV-ABS-6 | r3: `rotate` crashes only while mitmdump runs | r2: CP-T predicates too broad |
| CONV-ABS-7 | — | r2: `rotate` does not always touch `args.force` (same subject as pass-2 CONV-ABS-6; consistent) |
| CONV-ABS-12 | r4: startup vs reload plain-proxy state (this file) | — |

Recommendation for the final synthesis: cite these as `P2-CONV-ABS-6` / `P3-CONV-ABS-6` to disambiguate.

Hallucination-class audit of r3: no phantom entities, no over-extrapolated lists. One over-reach (CONV-ABS-12). Metrics recounted from the
orchestrator's evidence (23 DGX errors: matches; Anthropic errors 20 → 21: live ledger, not an error).

---

## 1. Target A — mitmproxy 12.3.1 upstream-connection lifecycle (closes r3 gap 4)

### 1.1 Where server connections live

| Fact | Source |
|---|---|
| After `CONNECT api.anthropic.com:443`, the regular-mode `HttpLayer` hands the tunnel to `NextLayer`, which (after client TLS) stacks a **new `HttpLayer(HTTPMode.transparent)`** for the tunnel's traffic | `proxy/layers/http/__init__:786-800,806-826`; `addons/next_layer:170,196` |
| Each `HttpLayer` owns `connections: dict[Connection, Layer]` (client connection + every server connection it opened) and `waiting_for_establishment`. **Scope = one client connection (one tunnel).** There is no pool shared across client connections | `__init__:930-946,962` |
| Entries are **only ever added** to `connections` (`:962`, `:1010`, `:1055`, `:1156`). No line in the module removes one. Closed and failed server connections stay in the dict for the life of the client connection | grep of `__init__` for `connections` |
| A flow's server connection is chosen **after the `request` hook**, from `(flow.request.host, flow.request.port, scheme == "https", server_conn.via, transport)`. The legacy rewrite (`:161-163`) therefore selects the DGX per flow. The tunnel's own `context.server` (the eager Anthropic connection) is untouched and keeps serving Anthropic-lane flows | `__init__:757-771`; spec match `:116-122` |
| `ConnectionHandler.max_conns`: at most **5** concurrent server connections per address per client connection. The semaphore is held for the connection's whole lifetime (open + handle) | `proxy/server:109,206-268` |

### 1.2 `get_connection` decision order (per request)

For each existing connection whose spec matches, in insertion order (`__init__:1068-1098`):

1. still being established → queue this request on it (no second connect);
2. **`connection.error` set → fail this request at once with that error, no new connect attempt** (`:1078-1084`);
3. connected → reuse it (unless an h2 client is talking to an h1 server, see §1.3);
4. otherwise (half-closed, no error) → skip it and open a new connection.

`connection.error` is set **only** when the TCP connect fails (`proxy/server:221-229`, the `OSError` text) or the upstream TLS handshake fails
(`proxy/layers/tls:401`). A connection that the server closes after establishment (idle keep-alive timeout, backend restart) has no `error`. It
falls into case 4 and is replaced on the next request.

### 1.3 Answer to gap 4: is a failed DGX connection cached, and are later requests failed without a retry?

**In the source: yes. In effect: it depends on the client's HTTP version.**

| Client ↔ proxy protocol | What happens after a DGX connect failure | Source |
|---|---|---|
| **HTTP/1.1** | The flow gets `ResponseProtocolError(CONNECT_FAILED)` → `error` hook → the client receives a mitmproxy **502** with `Connection: close`, and the proxy **closes the client connection** (`CloseConnection`). The tunnel and its `HttpLayer` end, so the cached error can never serve a second request. Claude Code's next request opens a new tunnel (new eager Anthropic connect, then a fresh DGX connect). **Every DGX-lane request gets its own connect attempt.** | `__init__:723-771`; `_http1:269-277` (Http1Server), `:483-496` |
| **HTTP/2** | The error is sent **per stream** (502 headers on that stream). The client connection stays open. The failed `Server` with `error` stays first in `connections`, so **every later DGX-lane request on that client connection fails immediately with the identical error text, without a connect attempt, even after the DGX recovers**, until the client closes that connection. Each failure still fires the `error` hook, so each writes its own `dgx_upstream_error` | `_http2:139-150`; `__init__:1072-1084` |
| Either | A reused DGX connection that the server closed just as a request was sent → `server closed connection` (`GENERIC_SERVER_ERROR`) → 502, **no retry**. This matches the 1 observed DGX event (a stale keep-alive race or a backend crash mid-request; the ledger cannot tell them apart) | `_http1:436-458` |

Which row applies in production is **UNVERIFIED**: it depends on the ALPN that Claude Code negotiates with the proxy (mitmproxy mirrors the upstream
ALPN under `eager`). Cheap local check: at `flow_detail=1` the dumper appends ` HTTP/2.0` to the request line when the client spoke HTTP/2,
and hides the version for h1 ↔ h1 (`addons/dumper:184-193`). So `grep -c ' HTTP/2.0$'` over `$TMPDIR/dgx-mitm.*.log` settles it (Remaining
gap 2). In the h2 case the 18 connect-refused events may include cached repeats of one failure.

Other connection facts that matter for parity and for hylo's design:
- **Reuse across flows:** a DGX connection is reused by later DGX-lane flows of the **same** client connection (HTTP/1 upstream, sequential).
  It is never shared across Claude Code connections.
- **h2 client → h1 DGX:** concurrent DGX flows on one h2 client connection each open their own DGX connection (`__init__:1086-1096,1176-1188`).
  Those `Server` objects accumulate in `connections` until the client connection closes, capped at 5 open per address by `max_conns`.
- **Error strings** (exact source; the `error` field of `*_upstream_error` is `str(flow.error)[:300]`, `:320-322`):

| Ledger `error` text | Raised at | Meaning |
|---|---|---|
| `Client disconnected.` | `_http1:132-145` (Http1Server `wait`) | client FIN while the response was in flight (user cancel) |
| `server closed connection` | `_http1:452-458` (Http1Client) | server closed before any response bytes |
| `unexpected server response: b'…'` | `_http1:443-450` | server closed with unparsed bytes buffered |
| `HTTP/1 protocol error: <h11 message>` | `_http1:97-106` | h11 `ProtocolError` while reading a body. `peer closed connection without sending complete message body` is h11's text for an EOF inside a content-length or chunked body (`h11/_readers:138,208`). The text alone does not say which side (client request body vs upstream response body); an event with empty attribution would mean the client side (the `request` hook never ran) |
| `<OSError text>` (e.g. `[Errno 61] …`) | `proxy/server:221-229` | TCP connect failure, the 18 connect-refused events. The exact wording depends on the OS and Python version |
| `Connection killed: <err>` | `proxy/server:197-204` | not reachable in legacy (no addon kills server connections) |

### 1.4 Domain consequences

- **Failure-mode parity is out of reach and should be out of scope.** Legacy's behavior under DGX or Anthropic outages depends on mitmproxy
  internals (eager CONNECT, per-tunnel pools, the h2-only sticky error, no retries). hylo's Go proxy will manage connections differently. That is a
  failure-mode-only deviation, merged into OD-17.
- **`dgx_llm_request_errors_total` mixes four causes**: backend down (connect failures, possibly multiplied under h2), user cancels, stale
  keep-alive races, and `dgx_reply` status ≥ 400. D7 freezes the metric. A post-cutover `reason` field is OD-16/OD-25.

---

## 2. Target D — protocol re-checks of r3's riskiest claims

### 2.1 Verdicts

| # | r3 claim | Verdict | Evidence |
|---|---|---|---|
| D-1 | **Eager CONNECT**: the DGX lane fails when Anthropic is unreachable | **CONFIRMED**, scope refined (§0.2): it gates per new client connection, on TCP connect only (not TLS). The launcher passes only `--set flow_detail=1 --listen-port … -s …` (`claude-dgx:75`), so `connection_strategy` keeps its default `eager` (`addons/proxyserver:154-163`). On failure the CONNECT gets a 502 whose body names the fix ("consider setting `connection_strategy` to `lazy`"). The addon has no `http_connect*` hook, so the ledger records nothing | `proxy/layers/http/__init__:786-800`; `tls:606-616` |
| D-2 | **Live-reload pass-through** failure mode | **CONFIRMED for reloads; RETRACTED for launch (CONV-ABS-12).** The reload path: `loadscript` removes the old addon, `load_script` returns `None` on any exception (logged `error in script <path>`), and nothing is registered, so the running proxy forwards everything untouched. **Log-grammar detail (new):** `register(None)` is still called inside `safecall`. The first time it registers a lookup entry named `nonetype`, and every later failed reload in the same process logs `Addon error: An addon called 'nonetype' already exists.` So the right way to measure this mode in the mitmdump logs is `error in script`, and `Addon error: An addon called 'nonetype'` marks repeat occurrences. The production `NameError` is a different failure (§0.1 (c)) | `addons/script:23-71,113-131`; `addonmanager:20-21,158-196,40-58` |
| D-3 | **Sonnet-on-Anthropic priced $0** | **CONFIRMED IN PART** (legacy side), wording refined to "unpriced", rule text carried from r3 (§0.2) | `dgx_ledger_exporter.py:160-167` |
| D-4 | **Launcher port-pick race** | **CONFIRMED** (§0.2). Realism is a judgment call: it needs two launches within mitmdump's startup time (Python import plus bind, typically about a second). A terminal multiplexer restoring several windows at once is the plausible trigger | `claude-dgx:72-78`; `proxy/mode_servers:252-266`; `addons/errorcheck:28-46` |

### 2.2 New: the legacy proxy listens on **all interfaces** and serves LAN clients

| Fact | Source |
|---|---|
| `listen_host` defaults to `""`, which `mode_specs.listen_host` passes through as "listen on all hosts" (IPv4 and IPv6). The launcher sets only `--listen-port` | mitmproxy 12.3.1 `options:94-99`; `proxy/mode_specs:138-149`; `proxy/mode_servers:252-258`; `claude-dgx:75` |
| Client admission: `block_global=True` (public source IPs refused), **`block_private=False`** (RFC 1918 / ULA LAN clients **accepted**), loopback always accepted. No `proxyauth` is configured | `addons/block:8-50` |
| The launcher's free-port probe and `HTTPS_PROXY` both use `127.0.0.1` only | `claude-dgx:73,77,79` |

**Domain consequence (HIGH from source; reachability depends on the host firewall, which is outside the repo):** while a `claude-dgx` window
runs, any host on the same private network can use its port 8090-8143 as an unauthenticated forward proxy. In particular, a Sonnet
`/v1/messages` request sent through it is routed to the backend **with the owner's backend key injected** (`:164`), attributed with
whatever `X-DGX-*` headers the sender chooses, and written to the owner's ledger. The 54-port range is easy to scan. This matches the
exporter's `0.0.0.0:9210` exposure already in pass 4, but is worse (credential use, not just label disclosure). D16 already requires the UI to
bind to localhost. The proxy listener needs the same rule (OD-24). Note also that the ledger tunnel forwards **remote loopback to local loopback**
(`127.0.0.1:9210:127.0.0.1:9210`, `deploy/io.hylo.ledger-tunnel.plist:7`), so the exporter's `0.0.0.0` bind is not needed by the deployed
scrape path either (OD-27).

---

## 3. Target B — Canonical domain model (merges broad pass 2, r1-r3 and r4; one place for Phase 1)

Source-round codes: **B** = broad pass 2, **r1**..**r4** = deepening rounds, **P3r1/P3r2** = pass-3 deep rounds (cited, never edited).
Each row gives the entity's form and its essential invariants or hazards, then points to the round that holds the detail.

### 3.1 Entity catalogue (deduplicated, by bounded context)

**Routing & capture (proxy, P3)**

| Entity | Form / key | Writer → reader | Key invariants and hazards | Detail in |
|---|---|---|---|---|
| **Lane** | proxy: `anthropic` / `anthropic-server-tools` / DGX (implicit: no `lane` key, `dgx_*` event names); status line: `dgx`/`anth`/None from stdin `model.id`; backfill: the lane with the most output tokens (tie → `dgx`) | proxy, status line, backfill | Three vocabularies: always qualify the term. Prefix match is case-sensitive `startswith` | B, r1 §8, r2 §7 |
| **Request (consumed body)** | JSON object: `model`, `metadata.user_id`, `tools[].{type,name,input_schema}`, `messages[].content[].type` | Claude Code → `request` hook | Non-object or unparseable body → untouched to Anthropic. Mistyped fields → P-R1..R3 | r2 §4.1 |
| **Routing decision** | R0 bridge WS, R1 not intercepted, R2 unparseable, R3 Anthropic, R4 server tools, R5 DGX (every `/v1/messages*` path, **including `count_tokens`**, live: 5/5 answered 200) | `request` hook | Only `api.anthropic.com` + `/v1/messages*` is ever rerouted | r2 §4.2, r3 §4.3 |
| **Tool set / normalization** | rebuilt **only when `changed`**: nameless and non-dict tools dropped, duplicates collapse (last definition, first slot), `tool_addition`/`tool_removal` applied, non-six-type blocks dropped, an emptied message → `(tools updated)` | `normalize_for_dgx` | Silently removes `document` and similar blocks on the DGX lane (OD-09). Re-serialization uses Python `json.dumps` byte rules | r2 §4.3, P3r2 B4 |
| **Flow attribution** | `_attrib {project, user, session, meta_user_id, model_req, req_bytes, path [, lane]}`; `_dgx` = copy + `model_served` (+ `in_tok`, `out_tok`, `stream_stop_reason` added in `response`); `_t0`, `_dgx_t0`, `_sse_tap` | `request`/`responseheaders` → `response`/`error` | `req_bytes` is **characters**. `model_served` is the **requested** model, not the served alias (a naming trap). `_bridge_dur` and `_ws_started` are never set | B, r2 §4.5 |
| **SSE tap** | `_SSETap`: tail `buf` ≤ 64,000 B, `usage (in,out)` only from a **top-level** `usage` holding `input_tokens`, cache maxima from both levels, `stop_reason` from `delta` | `responseheaders` → `response` | A malformed event aborts the rest of its chunk, so results depend on chunk boundaries for malformed streams | B, r1 I2, P3r2 B3 |
| **Usage / cache fields** | `cache_read_tok`, `cache_write_tok`, `cache_write_5m_tok` (= write − 1h), `cache_write_1h_tok` (clamped to write) | proxy | `in_tok` = **uncached input** on the Anthropic lane, the **whole prompt** on the DGX lane | B |
| **Account / device hint** | 8-char prefix of `account_uuid` / `device_id` from `metadata.user_id` (a JSON string) | proxy `_account_hint`; exporter `_account_device` | The two implementations differ on non-object JSON and on object values (I6). A list-valued `account_uuid` writes a list into the ledger (P-S2 → E-06) | B, r1 I6, r2 §4.6 |
| **Rate-limit header set** | `{suffix_lowercased: value}` for `anthropic-ratelimit-unified-*`, in **wire first-occurrence order**, repeated names folded with `", "` | `responseheaders` → `anth_ratelimit` | Logged when the sorted-JSON changes, per session, per proxy process. Reset by a reload | B, r3 §1.3 |
| **Proxy process state** | `_router._key_cache` (retried until a read succeeds), `_router._last_rl` (unbounded per session), `_logged_unknown` | module | All reset by a live reload | r2 §4.5 |
| **Addon generation** | the currently registered module. States: *loaded* / *raising in a hook* (P-R, P-S) / *absent after a failed reload* (plain pass-through) / *removed permanently* (file vanished at a poll) | mitmproxy script watcher (1 s mtime poll) | A failed load **at startup** exits mitmdump (CONV-ABS-12). The *absent* state is reachable only by a reload | r3 §1.6, **r4 §0.2, §2.1** |
| **Client connection (tunnel)** | one Claude Code TCP connection = one CONNECT to `api.anthropic.com` (eager upstream connect) + one transparent `HttpLayer` | mitmproxy | Owns its own server-connection pool. Ends on HTTP/1 connect errors (502 + close) | **r4 §1.1** |
| **Upstream connection** | `Server(address, tls, via, transport)`; Anthropic = eager tunnel peer; DGX = lazy, per tunnel, reused sequentially | mitmproxy | A failed connect is cached for the tunnel's life (sticky only for h2 clients). No retries. ≤ 5 per address per tunnel | r3 §1.4, **r4 §1.2-1.3** |
| **Proxy listener** | one mitmdump per window, port 8090-8143, **all interfaces**, LAN clients accepted, no auth | launcher | Port race between simultaneous launches. LAN reachability (OD-24) | r3 §3.3, **r4 §2.2** |
| **Decision log** | `time.strftime("%Y-%m-%d %H:%M:%S ") + msg` lines | proxy `note` | Not a ledger; no consumer. Holds `anth tap: buf=… usage=… ct=…` lines | B, r3 §4.3 |
| **Failed-request capture** | `~/dgx-llm-obs/failed-req-<ms>.json`, request **body only**, newest 20 kept, bodies ≥ 50,000,000 chars skipped | DGX `response`, status ≥ 400 | Lost on P-S4 | B, r2 §4.6, r3 §1.1 |
| **Ledger event** | §3.2 | proxy → exporter | Append-only, multi-writer, D7-frozen | §3.2 |

**Observability export (exporter, P2)**

| Entity | Form / key | Key invariants and hazards | Detail in |
|---|---|---|---|
| **Rebuild state** | 15 keyed accumulators (`req_totals`, `est_prompt`, `tok_in/out`, `dgx_cr`, `dgx_in_cap`, `dur_*`, `errors`, `anth_*`, `passthrough`, `last_*_ts`, `sess_meta`, `sess_stats`, `fakestop`, `processed_size`) | The `tok_in` and `anth_in` key sets drive whole families. `sess_stats` is never cleared. `anth_ds/dc` stay 0 (no current event carries `duration_s` on `anth_usage`). The exposition is a pure function of (ledger bytes, hook-log bytes, TZ, `DGX_SESSION_LIMIT`) | r2 §5.1 |
| **Exposition** | 27 metric families, `text/plain; version=0.0.4`, `0.0.0.0:9210`, `/metrics` only | Irregular HELP/TYPE layout is part of the bytes (D7) | pass 1 §4.7, P3r2 BC-EX-018 |
| **Fake-stop tallies** | substring match over the whole hook-log line in fixed pattern order; `p_done_latest` = first match on the last line that has one | Model text in `tail` can inject tags and values (OD-23) | B, r2 §5.1, P3r2 C2 |
| **Process lifecycle** | rebuild **before** bind; launchd `KeepAlive` + `RunAtLoad` | One bad ledger line → crash loop, `:9210` never served: **production-confirmed config** | r2 §5.2, r3 E-3, **r4 §0.1** |

**Session cockpit (status line, P1)**

| Entity | Form / key | Key invariants and hazards | Detail in |
|---|---|---|---|
| **Status-line input (stdin)** | Claude Code JSON. 24 paths consumed; truthiness fallbacks; `bool` passes number checks | Strict stdio, Python 3.11.7 oracle, `COLUMNS` numeric in production (owner rulings and capture) | r1 §1, r3 §0.1 |
| **Transcript record** | JSONL `{type, subtype, timestamp, message{id, usage, content[]}}`; blocks `text/thinking/tool_use/tool_result/image` | 512 KB window; bytes `splitlines`; `json.loads(bytes)` acceptance (CONV-ABS-4); dedup memory of 256 ids | r1 §2 |
| **Session cache** `statusline-<sid>.json` | keys `rl, rl_ts, fetch_ts, up, ts, sample, hist, proc_start` (+ preserved unknown keys) | Three separate atomic writes per refresh; `NaN`/`Infinity` tokens allowed | r1 §3.2, r2 §0 |
| **Mix cache** `statusline-mix-<key>.json` | 16 keys in a fixed order, `mixv6` marker | Full rewrite; reset rules; sticky transcript crashes replaced by D4-EX-2 | r1 §3.3, P3r2 A6 |
| **Git cache** `statusline-git-<sha1[:16]>.json` | `{ts, branch}` | Keyed by the raw project-dir string | r1 §3.4 |
| **Cost history** `cost-history.json` | `sessions[sid] = {lane, usd, api_ms, ts, src}` | No pruning; a parse failure wipes all history on the next write | r1 §3.5, r2 §7 |
| **TelemetrySample / HistoryPoint / health verdict** | `{name or up:<job>: float}`; point `{t, v, k, f[, v], p}`; fresh/stale/dead + serving-down | First value per key wins. NaN: CP-N01/N02 (VictoriaMetrics documents dropping NaN; Inf open) | r1 §4, r3 §2 |
| **Recording-rule series** | 18 queried series with definitions, units, absent/NaN behavior | External (dgx-llm); P6 backend contract | r3 §2 |
| **Turn / Composition / Rebuild / Plan-window states / Cost thresholds** | as defined | Character units; compaction resets composition and `pp` only | B, r1 §2.3, §8 |

**Turn quality (Stop hook, P4)**

| Entity | Form | Key invariants and hazards | Detail in |
|---|---|---|---|
| **Hook input** | Claude Code `Stop` JSON: `last_assistant_message`, `stop_hook_active`, `transcript_path`, `session_id` | Any truthy `stop_hook_active` allows the stop. An empty message still calls Kev | r2 §6.1 |
| **Kev exchange / verdict** | `POST {url}` `{model, state, questions.turn_complete}` → `answers.turn_complete.noul`; median of up to 3 calls | H-04 crash (a last attempt failing after a success) | r2 §6.2-6.3, P3r2 C1 |
| **Hook stdout / hook log line** | `hookSpecificOutput.additionalContext`; log grammar with Python `repr` | Go needs a Python-`repr` encoder | r2 §6.4-6.5 |

**Trust & environment (launcher, CA, preflight; P4)**

| Entity | Form | Key invariants and hazards | Detail in |
|---|---|---|---|
| **CA store / trust state / keychain entry / fingerprint / backups** | `~/.mitmproxy/*`, `~/.dgx/trust-state.json`, a login-keychain `trustRoot` | Regeneration keys on `-ca.pem`, the CLI checks `-ca-cert.pem`. Conflicts with D13 (hylo replaces it) | r3 §3.1 |
| **Preflight probe** | TCP connect, 4 s, four error classes | Port defaults to 80 whatever the scheme | r3 §3.2 |
| **Coordinator state** (unwired) | `.proxy-state/{port,pid,lock}` | Dead path; `flock` is missing on macOS | r3 §3.3 |
| **Launcher outputs** | `--settings` JSON bytes, child environment, argv | String-built JSON; `<HERE>` inserted unescaped | r2 §6.6-6.7 |
| **Env inputs (42) and env-bool grammar** | 27 Python + 21 launcher − 6 overlap; per-variable `== "1"` vs `!= "0"` | `DGX_STATUSLINE=true` disables the status line | r1 §6.1, r2 §0/§6.8, r3 E-5 |
| **CONFIG (D15)** | env rows mapped to keys; about 55 status-line literal keys; named-constant classes | Defaults equal legacy values until cutover | r1 §6 |
| **Backfill message / price table** | per-id first-line usage and model; family by substring; 3-family price table | Haiku read 0.005 error (shared with the external rules); unknown families skipped | r2 §7, r3 E-4 |

**Crash catalogues (index; canonical IDs):** status line CP-S/T/N/C/X/A = **43** (P3r2 table, canonical over r1's 31-ID numbering; crosswalk r2 §0.1);
proxy P-R1..R4, P-S1..P-S4 (r2 §4.6, r3 §1.1); exporter E-01..E-09, E-20, E-21 (r2 §5.2, P3r2 BC-EX-021); hook H-01..H-08 (r2 §6.3);
backfill B-01..B-08 (r2 §7). **P-S class production-confirmed** this round (§0.1).

### 3.2 LEDGER SCHEMA (canonical; D7-frozen until cutover)

**Writer contract** (`:56-62`): `open(LEDGER, "a")`, one `f.write(json.dumps({"t": …, "event": …, **fields}) + "\n")`, `OSError` swallowed.
`t` = `time.strftime("%Y-%m-%dT%H:%M:%S")`: **local wall time, 1-second resolution, no offset**, taken at **write** time (request events at
`request`-hook time, replies at response end). Python `json.dumps` defaults: `", "`/`": "`, `ensure_ascii` (the file is ASCII), insertion order,
float `repr`. **Multi-writer:** one mitmdump per window, all appending to one file. Line integrity relies on each line being one `write()` on an
`O_APPEND` descriptor (static reasoning, MEDIUM; lines are far below the 8 KiB buffer). The global line order is write order across processes,
not flow order (§3.3).

**Field types:** `S?` = string or null (from a header); `J` = any JSON (Claude Code sends a string); `I` = int; `F` = float.

| # | Event | Emitter | Trigger | Fields after `t, event`, in order | Optional / variant / historical | Legacy consumers | Ledger count (orchestrator) | Rounds |
|---|---|---|---|---|---|---|---|---|
| 1 | `dgx_request` | `:154` | R5 | `project S?, user S?, session S?, meta_user_id J, model_req S, req_bytes I (chars), path S (query stripped), model_served S (= model_req)` | **61 lines lack `req_bytes`**, **4570 lack `path`** (`path` added 2026-11-12; older proxy builds). No legacy consumer reads `path` or `model_served` | exporter: `req_totals` (project, user, model_req, account, device from `meta_user_id`), `est_prompt` (`req_bytes/4` iff numeric > 0), `sess_meta`/`sess_stats.reqs`, `last_dgx_ts`, `last_ts` | 4755 | B, r3 §4, r4 |
| 2 | `dgx_reply` | `:272` | `response`, host == DGX host, `/v1/messages*`, any status | `status I, duration_s F (3 dp)`, then the `_dgx` fields of #1, then `[in_tok I (whole prompt), out_tok I]` iff tap usage, `[stream_stop_reason S]` iff tap stop | `_dgx` absent (a DGX-host flow not routed by this addon) → only `status, duration_s` (≈ 0.0). Never written for flows that took the `error` hook | exporter: `dur_*` (numeric `duration_s`), `errors` and `sess_stats.errors` iff `status ≥ 400` (a non-numeric status crashes, E-07), `sess_meta` | 4696 | B, r2 §4.5 |
| 3 | `dgx_usage` | `:276` | after #2 when `in_tok` is set (SSE only) | `project S?, user S?, session S?, account S (8-char / "unknown"; a list in the P-S2 edge), in_tok I, out_tok I, stop_reason S?` `[, cache_read_tok I]` | `cache_read_tok` only with vLLM `--enable-prompt-tokens-details` (since 2026-11-12). Lost on P-S3 | exporter: `tok_in`/`tok_out`, `dgx_cr`/`dgx_in_cap` (iff the key is present), `sess_stats.in/out` | 4564 | B, r2 §5.1 |
| 4 | `dgx_upstream_error` | `:322` | `error` hook, `/v1/messages*`, request host == DGX host | `error S (≤ 300)`, then the `_dgx` fields of #1 (minus any `error` key) | Causes in production: **18 connect failures, 4 `Client disconnected.`, 1 `server closed connection`** (§1.3 table) | exporter: `errors[(project, user)] += 1`; **not** in `sess_stats.errors` | 23 | B, r3 §1.5, **r4** |
| 5 | `anth_request` | `:134`, `:139` | R3 / R4 | `project, user, session, meta_user_id, model_req, req_bytes, path` (as #1), `lane S ("anthropic" or "anthropic-server-tools")` | `path` absent on older lines (r3: 3562 Anthropic lines in all). Not written for R2 or P-R1..R3 | exporter: `anth_req` (account is always `"unknown"`: no `account` field), `last_anth_ts` | 6210 | B, r3 |
| 6 | `anth_reply` | `:245` | `response`, host `api.anthropic.com`, `/v1/messages*` (incl. `count_tokens`) | the `_attrib` fields (#5 order, incl. `lane` when set), `status I, duration_s F`, then iff usage: `in_tok I (uncached), out_tok I, stop_reason S?`, then iff cache keys: `cache_read_tok, cache_write_tok, cache_write_5m_tok, cache_write_1h_tok` | `_attrib` absent (R2) → no attribution, `duration_s ≈ 0.0`. `lane` absent on P-R1..R3 flows. Lost on P-S1 | exporter: `passthrough` iff `status == 200` (int or `200.0`) | 6189 | B, r2 §4.6 |
| 7 | `anth_usage` | `:247` | after #6 when usage was found | `lane S (default "anthropic"), project, user, session, account S, model S (= model_req), in_tok I, out_tok I, stop_reason S?` `[, 4 cache fields]` | **`cache_write_5m_tok` is wrong (= total) on streamed replies from the proxy builds of 2026-11-12**; consumers must derive 5m = write − min(1h, write) (`dgx_ledger_exporter.py:173-178`). Cache fields absent before the 2026-11-12 cache capture. No `duration_s` in the current writer. Lost on P-S1/P-S2 | exporter: `anth_in/out`, cache families (coverage counted iff a cache key is present), `arq`; `ads/adc` read `duration_s` (never present) | 5984 | B, r2 §5.1, r4 |
| 8 | `anthropic_upstream_error` | `:322` | `error` hook, `/v1/messages*`, request host ≠ DGX host | `error S`, then `_attrib` (incl. `lane`), or nothing when the `request` hook never ran | Production: **20 `Client disconnected.`, 1 `HTTP/1 protocol error: peer closed …`** | **none** (the exporter ignores it) | 21 (r3: 20) | B, r3 §0.3, **r4** |
| 9 | `anth_ratelimit` | `:188` | `responseheaders`, `api.anthropic.com`, any `anthropic-ratelimit-unified-*` header, changed since the last one for this session in this process | `session S?, headers {suffix: S}` (wire order, folded duplicates) | Re-logged after every reload | **none** (the status line uses stdin) | 261 | B, r3 §1.3 |
| 10 | `bridge_ws_connect` | `:101` | request to `bridge.claudeusercontent.com` with `Upgrade: websocket` | `host S` | — | `t` → `last_ts` only | not reported | B |
| 11 | `bridge_ws_close` | `:213` | `response` for the bridge host, i.e. at the **101 upgrade response**, not at close | `duration_s F` (**always 0.0**) | Misleading name | `t` → `last_ts` only | not reported | B |
| 12 | `ws_closed` | `:536` | never (guard on an attribute that is never set) | `duration_s F` | dead | — | 0 expected | B, r2 §4.5 |
| 13 | `anthropic_reply` | none now (historical name before 2026-11-10) | — | unknown (only `status` and `t` are read) | historical alias of `anth_reply` | exporter: `passthrough` iff `status == 200`, `t` | 258 | B, r3 §4.1 |

**Every** event with a parseable `t` advances `dgx_llm_last_request_timestamp_seconds`, and every event with a truthy `session` and `project`
feeds the dead `sess_proj`. The status line, Stop hook and backfill **never read the ledger** (r3 §4.1).

**Requirements for any new reader** (P3 replay, P4 D16 UI history, P6 `hylo top`, P7): treat `path`, `req_bytes`, cache fields, `lane`, and attribution as
optional; alias `anthropic_reply` → `anth_reply`; derive 5m cache writes; treat `anthropic_upstream_error` as current; interpret `t` as naive local
time (DST-ambiguous for one hour each autumn, P3r2 BC-EX-020); never assume a request has a reply, usage or error event.

### 3.3 Correlation: no flow ID (domain limitation, recorded; no pairing attempted)

| Fact | Evidence |
|---|---|
| No event carries a request or flow identifier. `t` has 1-second resolution and no offset, and several proxies interleave lines | `:56-62` |
| `dgx_reply` and `dgx_upstream_error` copy the **whole** request attribution, including `req_bytes`, `path`, `model_req`, `session`. So `(session, path, model_req, req_bytes)` plus `reply.t − duration_s ≈ request.t` (±1 s) is a **composite near-key** for request → reply/error | `:256,272-274,318-323` |
| `dgx_usage` / `anth_usage` carry **no** `req_bytes`. They pair with their reply through equal `(session, in_tok, out_tok)` and the same or next second (both are written in the same hook call) | `:245-253,272-282` |
| The near-key is ambiguous exactly where it matters: **Claude Code retries resend an identical body** (same `req_bytes`), so a retry and its original are indistinguishable. Two lines carrying the same `t` and the same session, one per lane (e.g. Haiku background calls), are told apart only by `model_req` | static reasoning |
| Consequences | P3 replay must pair heuristically and report ambiguous pairs. The 36 unpaired DGX requests stay unexplained. D16's flow view is fed by the internal event stream (PLAN D16), so the **live** UI is unaffected, but any **ledger-backed** history view inherits the limitation. P7 input: add a `flow_id` (and a UTC offset on `t`) to the redesigned schema |

---

## 4. Target C — Consolidated owner decisions (deduplicated; rulings excluded)

Excluded as already ruled: strict stdio and the Python 3.11.7 oracle; degraded output byte-for-byte for catalogued crash paths; CP-C01..C10 out of
parity scope (with the Go writer producing legacy's cache format); D4-EX-1; D4-EX-2; D13; D14; D15; D16. Phase codes follow `docs/PLAN.md` (P1 status
line, P2 exporter, P3 proxy, P4 run/hook/ca/ui, P5 cutover, P6 generalize, P7 ledger redesign).

| ID | Decision | Component | Bites | Origin | Recommendation (one line) |
|---|---|---|---|---|---|
| OD-01 | CONFIG key naming and the `HYLO_*` derivation rule | config | P1 | r1 #1 | Derive mechanically: `HYLO_` + upper-snake of the dotted key. |
| OD-02 | Status line glyphs as config | status line | P1 | r1 #2 | Yes: `statusline.glyphs.*` with legacy defaults (D15 lists presentation values). |
| OD-03 | Windows sanitizing of session ids in cache file names (I8) | status line | P1 | r1 #3 | Sanitize on Windows only; byte-identical names elsewhere. |
| OD-04 | One `paths.hook_log` key for the hook (writer) and the exporter (reader) | hook, exporter | P2, P4 | r1 #4 | One key, defaulting to the legacy path. |
| OD-05 | Env-bool grammar for the `DGX_*` aliases (`DGX_STATUSLINE=true` disables) | config, launcher | P1, P4, P6 | r2 #5 | Keep the per-variable legacy string rules for `DGX_*`; typed booleans for `HYLO_*` only. |
| OD-06 | **P-R4**: unreadable backend key → Claude Code's credentials sent to the backend (cleartext under `http`) | proxy | P3 | r2 #6, r3 E-1 | Approved deviation: fail closed (local 502 + error event), never contact the backend. |
| OD-07 | `x-api-key`/`Authorization`/cookies forwarded on every DGX-lane request | proxy | P3 | pass 4, r3 #7 | Approved deviation: strip client credentials before adding the backend key (consistent with D16's guardrail). |
| OD-08 | P-R1..R3: a request-hook exception silently re-lanes a would-be DGX request to Anthropic | proxy | P3 | r2 #7 | Reproduce in the replay; hylo additionally logs a visible routing-error event. |
| OD-09 | `document` and other non-six-type blocks dropped on the DGX lane | proxy | P3, P6 | r2 #8 | Parity now; after cutover, a config routing rule sending such requests to Anthropic. |
| OD-10 | `count_tokens` for local models goes to the backend (live) vs D13's "`POST /v1/messages` only" | proxy | P3 | r2 #9, r3 §4.3 | Keep the behavior; amend D13 to name `/v1/messages/count_tokens`. |
| OD-11 | Exporter poison-line behavior: crash loop under KeepAlive (**production config confirmed**) | exporter | P2 | r2 #10, r4 §0.1 | Approved deviation: skip and count bad lines (a `…_ledger_bad_lines_total` metric), mirroring D4-EX-2. |
| OD-12 | Hook H-04: `(p, None)` crash, exit 1, no log | hook | P4 | r2 #11 | Fix: use the last successful call's time; document as a deviation. |
| OD-13 | Price tables (Haiku read 0.005 in backfill and external rules; no Haiku > 100K tier; no Fable/Mythos; Sonnet on Anthropic unpriced) | backfill, P6 cost | P6 | r2 #12, r3 | Prices in config: legacy values for parity, documented prices as post-cutover defaults. |
| OD-14 | `subagentStatusLine` emission (removed in Claude Code ≥ 2.1.323) and `--subagent` (CP-A01..A03) in Go scope | launcher, status line | P1, P4 | r2 #14, P3r2 | Toggle `run.subagent_statusline` (default on for parity); `--subagent` in scope only if the toggle stays. |
| OD-15 | Exporter parity oracle: `/usr/bin/python3` 3.9.6, empty launchd environment | exporter | P2 | r2 #13 | Pin 3.9.6 with an empty env for P2 goldens. |
| OD-16 | **Client cancels counted as DGX errors** (**production-confirmed: 4 of 23**) | proxy, exporter | P2, P3 | r3 #16, P3r2 #2 | Reproduce through cutover (D7); afterwards add a `reason` field, metric unchanged. |
| OD-17 | **Upstream connection management out of parity scope**: eager CONNECT couples the DGX lane to Anthropic reachability; h2-only sticky cached connect failures; no retry on a stale keep-alive | proxy | P3 | r3 #17, **r4 §1** | Approved failure-mode deviation: lazy upstream connects, per-request reconnect or backoff, never couple the lanes. |
| OD-18 | Response-hook crash paths P-S1..P-S4 (ledger lines lost, client unaffected; **P-S class seen in production**) | proxy | P3 | r2, r3 #18, P3r2 #3 | Reproduce the ledger effects of P-S1..S3 in the replay; P-S4 (LOW) may be an approved deviation (Go keeps the capture). |
| OD-19 | Launcher port race and the unwired coordinator | launcher | P4 | r3 #19 | Out of parity scope: hylo binds its own listener (port 0 or a lock) and drops the coordinator. |
| OD-20 | P6 telemetry backend contract (MetricsQL query, job names, recorded series, constants as config); evaluator unknown | status line, P6 | P6 | r3 #20, r4 §0.1 | Accept r3 §2.3 as the documented requirement; the evaluator (vmalert or Prometheus) becomes a documentation note. |
| OD-21 | CP-T05 detection point in the D4-EX-2 Go contract | status line | P1 | P3r2 #1 | Confirm pass 3's choice (skip the opening line) unless the owner prefers turn-only skipping. |
| OD-22 | Exporter DST false idle (naive local `t`, `fold=0`) | exporter, status line | P2, P7 | P3r2 #4 | Accept through cutover (D7); record an offset in the P7 schema. |
| OD-23 | Exporter tally misattribution (tags and `p_done=` inside `tail` are counted) | exporter | P2, P7 | P3r2 #5 | Reproduce in P2 (D7); fix with a structured hook log in P7. |
| **OD-24** | **Proxy listens on all interfaces and serves LAN clients; LAN senders get the backend key injected** | proxy | P3 | **r4 §2.2** | Approved deviation: bind loopback only (like D16's UI), with config for anything wider. |
| **OD-25** | **No correlation key in the ledger** (replay pairing heuristic; retries ambiguous) | proxy, ledger | P3, P7 | **r4 §3.3** | Keep the format through cutover (D7); the P3 replay uses the composite near-key and reports ambiguities; P7 adds `flow_id` and a UTC offset. |
| **OD-26** | **Config reload semantics** (legacy's failed reload silently turns proxies into plain pass-through) | proxy, config | P3, P6 | **r4 §2.1** | hylo keeps the last good config on a bad reload, emits an error event, and never degrades to pass-through. |
| **OD-27** | Exporter binds `0.0.0.0:9210` unauthenticated, though the deployed tunnel needs only loopback | exporter | P2 | pass 4, **r4 §2.2** | Default `exporter.bind = 127.0.0.1` as an approved deviation (the scrape path is `ssh -R` loopback-to-loopback). |

**Count: 27 pending decisions** (r3's 20 + pass-3 r2's 3 non-duplicate items (CP-T05, DST, tally) + 4 new this round (OD-24..27). Merged: P3r2 #2 →
OD-16, P3r2 #3 → OD-18, P3r2 `--subagent` scope → OD-14, the h2 sticky cache → OD-17).

**Top 8 by risk:** OD-06 (credentials to the backend), OD-24 (LAN clients use the backend key), OD-07 (client auth headers forwarded), OD-11
(exporter crash loop, production config), OD-16 (user cancels inflate the error metric, production-confirmed), OD-17 (lane coupling and
connection failure modes), OD-10 (`count_tokens` vs D13), OD-25 (no correlation key: P3 replay design).

---

## Delta Summary

| Target | New items | Refined / confirmed |
|---|---|---|
| Evidence (gaps 2, 3, 5) | 3 gap closures recorded; production confirmation of r3 §1.5 (17 % of DGX error events are user cancels) and of the exporter crash-loop config | r3 §1.5 MEDIUM → HIGH; the `NameError` classified as P-S (not import failure) |
| A connection lifecycle | 5 facts (pool scope per tunnel, add-only `connections`, decision order, error cached only on connect/TLS failure, `max_conns` 5); **gap-4 answer** (cached in source; never re-served for HTTP/1 clients because the tunnel closes; **sticky for HTTP/2 clients**); 6-row error-string table mapped to source lines; h2→h1 per-flow connections | r3 §1.4 reuse claim confirmed |
| D re-checks | **CONV-ABS-12** (startup ErrorCheck: no plain-proxy state at launch); **new: proxy listens on all interfaces, admits LAN clients, injects the backend key** (§2.2); `nonetype` log-grammar detail for repeated failed reloads | eager CONNECT confirmed with scope (TCP only, per new connection); "$0" → "unpriced" (legacy side confirmed, rule side carried); port race confirmed from source |
| B consolidation | one canonical catalogue (6 contexts, about 50 entities, each with a source round), 13-event ledger schema with emitters, consumers, variants and counts; **new schema facts:** multi-writer append contract, `t` taken at write time, the 2026-11-12 `cache_write_5m_tok` defect variant, 61/4570 missing-field counts, `anthropic_upstream_error` with empty attribution; composite near-key for correlation | r1-r3 entity rows merged and deduplicated; CONV-ABS crosswalk (collision across passes) |
| C owner decisions | 27 items with ID, component, phase and recommendation; 4 new (OD-24..27) | 20 + 5 merged, 3 duplicates folded |

Existing items refined: 7 (r3 §1.4, §1.5, §1.6, §2.2, §3.3; r2 §5.2; P3r2 B2).

## Remaining Gaps (verbatim-carryable)

1. Owner capture, VictoriaMetrics (unchanged): one `/api/v1/query` response for the exact `QUERY` (`dgx_statusline.py:102-123`) on an idle box, under light load, and with fewer than 20 TTFT samples, after the DGX soak is scored. Look for `"NaN"`/`"+Inf"`/`"-Inf"` in `value[1]` per `__name__`. MetricsQL documents dropping NaN, so expect `dgx_ttft:p95_30m` to be absent at idle; the capture confirms this and settles Inf.
2. Owner local check (cheap, decides which row of r4 §1.3 applies): count ` HTTP/2.0` request lines in `$TMPDIR/dgx-mitm.*.log` (`grep -c ' HTTP/2.0$'`; mitmdump hides the version for h1 ↔ h1). Zero → HTTP/1 everywhere, so cached connect failures are never re-served. Non-zero → the sticky failure mode is live, and the 18 connect-refused events may include cached repeats (check for identical `error` text within one session in the same second).
3. Owner local check: count `error in script` lines (import failures, the plain pass-through mode) and `Addon error: An addon called 'nonetype'` lines (repeated failed reloads) in the same logs. `Addon error` alone measures hook exceptions (P-R/P-S), not pass-through.
4. Owner local check (optional, LOW): whether the 1 `anthropic_upstream_error` with `HTTP/1 protocol error: peer closed …` carries attribution fields (present → upstream response body cut; absent → client request body cut, the `request` hook never ran).
5. Not determinable from authorized sources (LOW, carried): vmalert vs Prometheus as the evaluator of `deploy/recording.yml` (P6 documentation note); the `lsof` COMMAND name of the venv `mitmdump` (unwired coordinator); whether the host firewall blocks inbound connections to the proxy ports (decides the practical reach of OD-24, not its fix).
6. Owner decisions OD-01..OD-27 (§4).

## Novelty Assessment

Novelty: SUBSTANTIVE

Most of this round is consolidation (the catalogue, the schema and the decision list) and would count as NITPICK alone. Three findings change the
spec and are not refinements:
- **The proxy listener is LAN-reachable and injects the backend key for any private-network sender** (§2.2). No prior pass recorded the proxy's bind
  address or admission policy. It adds a P3 deviation (OD-24) next to the two credential items.
- **CONV-ABS-12**: a bad script or config at launch makes mitmdump exit (startup `ErrorCheck`), not run as a plain proxy. This changes the launcher and
  proxy failure model in r3 §1.6, and with it what the "plain pass-through" mode means for hylo's reload design (OD-26).
- **Gap-4 answer**: a failed upstream connection is cached per tunnel with no retry. It is harmless for HTTP/1 clients (the tunnel closes) and a sticky
  outage amplifier for HTTP/2 clients. This also explains how `dgx_llm_request_errors_total` can be multiplied, and it defines what OD-17 must
  deviate from.
Smaller but real: the multi-writer and write-time `t` contract, the composite near-key for replay pairing, the `cache_write_5m_tok` defect variant, and
the production confirmation that 17 % of DGX error events are user cancels.

## Convergence Declaration

Another round needed. Substantive items surfaced this round (§2.2 LAN exposure, CONV-ABS-12, the connection-cache semantics). The entity model
itself was stable this round: no new domain entity outside the transport layer appeared. What remains is owner checks 2-4 (one grep each), the VM
capture, and the 27 decisions.

## State Checkpoint

```yaml
pass: 2
round: 4
status: complete
files_scanned: 3 legacy files in part (dgx_proxy.py, dgx_ledger_exporter.py, claude-dgx) + deploy/io.hylo.ledger-tunnel.plist + 17 mitmproxy 12.3.1 modules + h11/_readers (one string)
timestamp: 2026-11-14T06:45:00Z
novelty: SUBSTANTIVE
retractions: [CONV-ABS-12]
owner_decisions: 27 (OD-01..OD-27)
pass3_r3_reconciled: not present at write time
next: pass 2 round 5 (targets = Remaining Gaps 1-6 verbatim)
```
