# Pass 3 deepening, round 3: behavioral contracts (hylo-legacy)

- **Scope:** `legacy/` (unchanged since round 1: 11 files, 3,181 lines). Re-read this round: `dgx_proxy.py` (whole file),
  `dgx_ledger_exporter.py` (whole file), `tools/backfill_cost_history.py` (whole file), `dgx_statusline.py:195-265`,
  `:425-640`, `:822-836`, `:975-1160`, `claude-dgx:70-80`, `dgx-proxy-coordinator.sh:26-38`.
- **Inputs read:** every file in `.factory/semport/hylo-legacy/`, including pass-3 r1 and r2 and **pass-2 r3**
  (`…-pass-2-deep-domain-r3.md`, written in parallel; read, not edited, reconciled in §1.3 and §2).
- **Extra read-only source (orchestrator-authorized): mitmproxy 12.3.1**, the version in the prototype's venv
  (`mitmproxy/version.py:5`). Modules read: `http`, `addonmanager`, `addons/proxyserver`, `proxy/server`,
  `proxy/layers/http/{__init__,_http1,_http2,_events}`, `net/http/headers`, `net/http/url`. Never imported or executed.
  The venv interpreter is CPython 3.12 (`pyvenv.cfg`, also recorded by pass-2 r3 §0.3).
- **Method:** static reading plus pinning scripts in
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r3/`, run with the
  oracle `/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7). As in round 2, `loader.py` execs a **copy** of a
  legacy file's text in a fresh namespace, with `HOME`, the ledger, the hook log and the decision log redirected to the
  scratchpad. The clock is a frozen shim where noted. Nothing legacy ran in place, nothing was networked, no proxy ran.
  Scripts: `d4ex2.py`, `excl.py`, `cost.py`, `cost2.py`, `backfill.py`, `backfill2.py`, `expo.py`. Round-2 scripts
  `p3r2/tap.py` and `p3r2/dst.py` were re-run unchanged. One third-party library ran offline on synthetic data:
  `prometheus_client` 0.23.1's text parser, used as a reference parser for target 6.
- **Notation:** `\e` is ESC (0x1B). Code points are written `U+XXXX`. "Pinned" means a copied expression produced the
  output shown. A bare `:N` means the file named in the section heading.
- **IDs (append-only):** new BC-SL-099…102, BC-PX-043…044, BC-EX-024…025, BC-BF-006…013. Retraction **CONV-ABS-8**.
  Pass-2 r3 used CONV-ABS-6 for a retraction that pass-3 r2 had already filed as CONV-ABS-7 (§1.3), so this file
  continues at 8.

---

## 0. Owner rulings applied (not pending)

| Ruling | Where it shows here |
|---|---|
| Strict stdio; CPython 3.11.7 is the oracle for the status line and hook (confirmed by owner capture) | every status line and backfill pin ran on 3.11.7 |
| Degraded output byte-for-byte for catalogued crash paths | §7 |
| CP-C01…C10 out of parity scope; the Go writer writes legacy's exact cache format | §3.3, §4 (BC-SL-102 raises one conflict with this ruling, owner item 8) |
| D4-EX-1 (⌂ on Windows), D4-EX-2 (skip wrong-shape transcript lines) | §3 derives the D4-EX-2 table tests |
| D13–D16 | D16 consumers in BC-EX-024; D13 in owner item 6 |

---

## 1. Audit: round 2's riskiest claims re-checked against the source

### 1.1 Verdicts

| Round-2 claim | Verdict | Evidence |
|---|---|---|
| **SSE tap chunk-boundary dependence** (BC-PX-040) | **CONFIRMED and grounded in mitmproxy.** Re-run of `p3r2/tap.py` reproduces both outcomes: one chunk → `usage=None`; split before the good event → `usage=(11, 12)`, `stop=max_tokens`. The feed boundaries are real network framing. The HTTP/1 body reader turns each TCP read (`reader.read(65535)`, mitmproxy 12.3.1 `proxy/server:285`) into one `ResponseData` per available piece of the body (`proxy/layers/http/_http1:88-114`). With chunked transfer encoding that means one piece per HTTP chunk, or part of one. Each piece is one `feed` call (`__init__:446-456`). mitmproxy's own docstring warns that "packet boundaries generally should not be relied upon" (`http:256`). | as cited |
| **Exporter DST false idle** (BC-EX-020) | **CONFIRMED.** Re-run of `p3r2/dst.py` under `TZ=America/Chicago`: 1793514600 and 1793518200 both serialize to `2026-11-01T01:30:00` and both parse back to 1793514600.0 (error −3600 s for the second). The status line's idle test (`dgx_statusline.py:824-825`: `time.time() - last > 300` and running < 1) uses a true epoch for "now", so during the repeated hour it sees the DGX as at least 300 s idle whenever no request is running. | `dgx_proxy.py:60`; exporter `:125`; status line `:824-834` |
| **Tally misattribution** (BC-EX-019) | **CONFIRMED by source.** Each line is checked by `in` substring on the whole line, in the order kev-continue, kev-allow, kev+opus, colon, heuristic (exporter `:217-226`). `p_done_latest` is `re.search` (first match) on every line containing `p_done=`, and later lines overwrite it (`:227-234`). | exporter `:214-236` |
| **P-S4** (`None[:600]` on an SSE error reply) | **CONFIRMED for mitmproxy 12.3.1 with default options.** A streamed response is never stored: `store_streamed_bodies` defaults to False (`addons/proxyserver:147-153`), the body content is assigned only when that option is on (`__init__:473-475`), and the response object is created with `content=None` (`net/http/http1/read:299-305`). `get_text` returns None when `raw_content` is None (`http:390-391,432-434`). The exception is swallowed by `safecall` and logged as `Addon error: 'NoneType' object is not subscriptable` (`addonmanager:45-59`), and the response still reaches the client (`__init__:511-535`). **Two exceptions** (refinement): (a) an SSE error reply whose headers already end the message (`Content-Length: 0`) is not streamed (`__init__:427-430`). Its body is buffered as `b""`, `get_text` returns `""` and nothing raises. (b) A user-level `~/.mitmproxy/config.yaml` setting `store_streamed_bodies: true` would avoid the crash; that file is outside the repo (owner check, LOW). | as cited |
| **CP-T05 W-predicate** (BC-SL-098) | **CONFIRMED by pins** (§3: T05+, T05-lu-none). Two refinements. (1) The clause "the line's usage is … absent" can never hold together with a bad `output_tokens`: absent usage gives `out = 0` (`(None or {}).get(…)`). The working condition is therefore "a usage object whose id is already in `seen_ids`". (2) Round 2's parenthetical "legacy then never crashes" is **wrong**: see CONV-ABS-8. | `dgx_statusline.py:1073-1079,988-994`; `d4ex2.py`, `excl.py` |

### 1.2 Retraction

- **CONV-ABS-8** (pass-3 r2 §A6, CP-T05 row: "It differs from legacy's lazy crash only when the session ends with that
  turn still open (legacy then never crashes)"). Pinned (`excl.py`): when the opening line with the bad `out` is the last
  line parsed, legacy **writes it to the mix cache**:
  `"cur": {"id": "msg_A", "t0": 1794650400.0, "t1": 1794650408.0, "out": "abc"}`. Legacy then crashes at `:994` on the
  **first later refresh** whose new lines close that turn (a newer id, a real user prompt, a timed system line). From
  then on the crash is sticky, because the cache is never saved again. "Never crashes" holds only if the transcript gets
  no closer at all. The corrected contract is BC-SL-100.

No other round-2 claim failed the audit. Hallucination classes: no invented token lists or names. Metrics re-derived:
the round-2 crash total of 43 stands, and no new status line crash path was found this round.

### 1.3 Premise corrections and cross-file reconciliation

| Item | Ruling |
|---|---|
| Orchestrator premise "current code emits `anth_*`; the `anthropic_*` names are historical" | **Partly wrong.** `anthropic_upstream_error` is the **current** name: `lane = "dgx" if flow.request.host == self.dgx_host else "anthropic"` and `ledger(f"{lane}_upstream_error", …)` (`dgx_proxy.py:319-322`). Only `anthropic_reply` is historical (renamed to `anth_reply` on 2026-11-10, exporter comment `:204-205`). Pass-2 r3 §0.3 reached the same conclusion independently. BC-EX-024 records how each consumer treats both |
| Count of `anthropic_upstream_error` | The orchestrator's ledger data given to this round: **21** (20 `Client disconnected.`, 1 `HTTP/1 protocol error: peer closed connection without sending complete message body`). Pass-2 r3 §4.1 lists 20. This file uses 21. Note that 21 equals `anth_request − anth_reply` (pass-2 r3 §4.1), so every unanswered Anthropic request then has an error event. To be reconciled in pass-2 round 4 |
| CONV-ABS ID collision | pass-3 r2 **CONV-ABS-6** = round 1's CP-T predicates were too broad. pass-3 r2 **CONV-ABS-7** = `rotate` touches `args.force` only while mitmdump runs. pass-2 r3 files the same `rotate` retraction as "CONV-ABS-6". Recommendation to the orchestrator: treat pass-2 r3's CONV-ABS-6 as an alias of CONV-ABS-7. The content of both is consistent (pass-2 r3 adds the post-move exit-1 detail) |
| mitmproxy semantics (pass-2 r3 §1, domain side) | Agreed on every point checked: exception semantics, `get_text`, header folding, eager CONNECT, cancel → `error` hook. This file adds the contract-level items pass-2 r3 does not have: the error-cause table with exact texts and client-visible results (BC-PX-044), the Host-header rewrite (BC-PX-043), the end-of-message `stream(b"")` call, the empty-body SSE exception to P-S4, and production confirmation of the cancel path |

---

## 2. Target 1: the six mitmproxy assumptions, verified against 12.3.1

### 2.1 Verdict per assumption

| # | Round-2 assumption | Verdict | mitmproxy 12.3.1 source |
|---|---|---|---|
| 1 | Response created with `content=None`; buffered end-of-message sets the content; streamed content stays None | **CONFIRMED** (default options) | `net/http/http1/read:299-305` (h1), `proxy/layers/http/_http2:458,600` (h2); buffered `__init__:488-492`; streamed `__init__:473-475` only with `store_streamed_bodies` (default False, `addons/proxyserver:147-153`) |
| 2 | `get_text(strict=False)` returns None when `raw_content is None` | **CONFIRMED** | `http:385-391,427-434` |
| 3 | Callable stream: each chunk replaced by `stream(chunk)`; possibly `stream(b"")` at end of message | **CONFIRMED, and 12.3.1 does call `stream(b"")` at end of message.** A `b""` result forwards nothing. The tap's `feed(b"")` returns `b""`, and after any earlier `feed`, `buf` holds no `\n`, so it scans nothing. **A trailing unterminated line is never flushed** | `__init__:446-456` (per chunk), `:460-472` (EOM call, `chunks == b""` → `[]`); tap `dgx_proxy.py:398-410` |
| 4 | `response` hook fires after end of message for streamed flows | **CONFIRMED** | `__init__:476` → `send_response(already_streamed=True)` → `HttpResponseHook` `:511` |
| 5 | An addon exception is logged and the flow continues | **CONFIRMED.** `safecall` logs `Addon error: <exc>` at ERROR (mitmdump's stdout, which is the per-window log) and swallows everything except `AddonHalt`/`OptionsError`. The next addon runs, and the flow resumes with whatever the hook had already applied | `addonmanager:45-59,285-295`. The `stream` callable is **not** wrapped by `safecall`: it runs inside the layer, and an exception there would reach `server_event`'s catch-all `mitmproxy has crashed!` (`proxy/server:436-437`). The tap cannot raise (its `_scan` is fully guarded), so this is moot for legacy, but it constrains any Go "tap" design |
| 6 | Connection drop mid-body → `error` hook **instead of** `response` | **CONFIRMED, and production-confirmed (§2.3).** `handle_protocol_error` fires `HttpErrorHook` iff the client side is not errored and the server side is neither done nor errored. Source comment: "We don't want to trigger both a response hook and an error hook" | `__init__:723-755` |

Also verified: **`Content-Length` after `set_text`** is rewritten to the new byte length, unless the request carries
`Transfer-Encoding` (`http:378-383`). `set_text` encodes with the content-type charset, and JSON content types default
to UTF-8 (`net/http/headers:62-63`). The `json.dumps` output is ASCII, so the bytes are identical under any
ASCII-compatible charset.

### 2.2 BC updates that depend on these assumptions

| BC / crash path | Update |
|---|---|
| **BC-PX-034** path (b) (r1) and **BC-PX-038** (r2) | Pinned to 12.3.1. For a tapped Anthropic flow without a qualifying event, `json.loads(None)` raises **`TypeError`** (not ValueError), caught at `:234`. No token fields, no `anth_usage`. Conf HIGH |
| **BC-PX-037** (stream decision table) | Confirmed. Row 4 ("other paths, non-SSE: mitmproxy default, buffered") holds because `stream` defaults to False (`http:247`) and `stream_large_bodies`/`body_size_limit` default to None (`addons/proxyserver:164-182`). The launcher passes only `--set flow_detail=1` (`claude-dgx:75`; coordinator `:31` likewise). **New row:** any response whose headers already end the message (`Content-Length: 0`, or a 204/304) is buffered even when `stream` was set (`__init__:427-430`). The tap object exists but is never fed, so `tap.usage` is None |
| **BC-PX-039** (interrupted streams) | **CONFIRMED in production** (§2.3). Was "assumption-dependent, MEDIUM-LOW"; now HIGH |
| **BC-PX-040** (chunk dependence) | Confirmed. Chunk sources are pinned above (§1.1). P3 replay rule unchanged: replay recorded `feed` boundaries (HTTP chunk and TCP-read splits), or restrict the corpus to well-formed streams with lines under 64,000 bytes |
| **BC-PX-041** (re-serialization) | `Content-Length` rewrite confirmed (above). The "verify in P3" note is closed |
| **BC-PX-042** / P-R2 | The P-R2 outcome (fail open to Anthropic) is confirmed by assumption 5: the flow continues unrouted. Pass-2 r3 §1.1 gives the full P-R*/P-S* outcome table |
| **P-S4** | Confirmed with two exceptions (§1.1). Only DGX-lane flows are affected: the Anthropic branch reads the body only when status < 400 (`:225`), and a non-SSE DGX error is buffered (`:205-206`) |
| Client-disconnect path | BC-PX-044 |

### 2.3 BC-PX-044 (new): the `error` hook — causes, exact texts, client-visible results

The legacy `error` hook (`dgx_proxy.py:311-323`) records `str(flow.error)[:300]` and does not look at the cause. In
12.3.1 the possible causes for a routed `/v1/messages*` flow are:

| Cause | `error` text (exact) | Hooks fired | Client receives | Source |
|---|---|---|---|---|
| Upstream TCP connect fails | `str(OSError)` from asyncio, e.g. `[Errno 61] Connect call failed ('<host>', <port>)` (61 = ECONNREFUSED on macOS; the number and wording are OS-specific) | `error` only | **502** HTML page from mitmproxy (`CONNECT_FAILED` → 502) | `proxy/server:212-230`; `__init__:757-771`; `_events:111-117`; `_http1:269-277,483-496` |
| **Client closes while the flow is in flight** (Esc during prefill or streaming) | `Client disconnected.` | `error` only (also when the cancel arrives during the `request` hook, via `check_killed(True)`) | nothing (it is gone). mitmproxy also **closes the upstream connection** (`__init__:736-738` → `_http1:350-352`), so the backend sees a disconnect (vLLM aborts the request; backend behavior is external) | `_http1:125-145`; `__init__:696-721,723-755` |
| Upstream closes before any response byte | `server closed connection` | `error` only | 502 | `_http1:436-458` |
| Upstream breaks the HTTP/1 framing (e.g. EOF inside a chunked body) | `HTTP/1 protocol error: <h11 message>`, e.g. `… peer closed connection without sending complete message body…` | `error` only | 502 if no response headers were sent yet; otherwise the connection is closed mid-body | `_http1:88-107,269-277` |
| Client closes after the response completed | (none) | `response` only | — | `need_error_hook` false once the server side is done (`__init__:731-734`) |

**Production evidence (orchestrator, from the private ledger; recorded, not re-derived):** 23 `dgx_upstream_error`
events: 18 `[Errno 61] Connect call failed (<backend>, 8080)`, **4 `Client disconnected.`**, 1 `server closed
connection`. And 21 `anthropic_upstream_error` events: **20 `Client disconnected.`**, 1 `HTTP/1 protocol error: peer
closed connection without sending complete message body`. Consequences:

1. **A user interrupt (Esc) mid-generation is logged as `<lane>_upstream_error` and, on the DGX lane, counts in
   `dgx_llm_request_errors_total{project,user}`** (exporter `:208-210`). Its tap usage is discarded, because `response`
   never runs. Status: **confirmed in production** (4 of 23 DGX error events, 17 %).
2. The `Client disconnected.` wording is the **HTTP/1** server layer's (`_http1:142`). The HTTP/2 layer would report
   `stream reset by client (…)` (`_http2:266-268`). So in production **Claude Code talks HTTP/1.1 to the proxy**. That is a
   P3 harness fact.
3. The error texts are mitmproxy's and the OS's. Go (`net/http`) produces different texts. The exporter never reads
   `error`, so no metric depends on it. Whether Go mimics the texts is owner item 6.

Conf: HIGH (source plus production). Gap: how the `server closed connection` case arises in production (likely a
reused keep-alive connection closed by the backend) is not determinable here and does not change the contract.

### 2.4 BC-PX-043 (new): Host header after the switch to the DGX

`flow.request.scheme/host/port = …` (`dgx_proxy.py:161-163`). In 12.3.1 the `host` and `port` setters call
`_update_host_and_authority` (`http:719-722,759-775`). If a `Host` header is present it is set to
`url.hostport(scheme, host, port)`, and the port is omitted when it is the scheme's default (`net/http/url:143-153`).
An HTTP/2 `:authority` is updated the same way. The three assignments run in order (scheme, then host with the old port,
then port), so the final value is `hostport(new scheme, new host, new port)`. Default upstream: `Host: 192.0.2.10:8080`.
With `DGX_UPSTREAM=http://h` (port defaults to 80, `:83`): `Host: h`. The request line stays in origin form, because the
client used CONNECT plus TLS (HTTP/1, §2.3). **Go contract (P3):** the backend request carries
`Host: <host>[:<port>]`, with the port omitted iff it is the default for the backend scheme. Conf HIGH (source), not
pinned (requires executing mitmproxy).

---

## 3. Target 3: D4-EX-2 table tests derived from legacy runs

### 3.1 BC-SL-099 (new): the table

**Method** (`d4ex2.py`, TZ=UTC, sid `d4ex2`, empty mix cache before each run). For each positive case: (a) legacy
`_mix_counts` on the full transcript must raise, and must leave **no** mix cache (verified: `cache_written_on_raise`
False for all 11 positive rows). (b) Legacy runs on the transcript with the W-line deleted, and the **Go expectation** is
that cache with `size` increased by the deleted line's bytes plus 1 for its `\n`. For each negative look-alike, legacy
must not raise, and the expectation is legacy's own cache. Every transcript line is followed by `\n`.

Base lines (`B`), byte-exact, in this order:

```text
U0  {"type": "user", "timestamp": "2026-11-14T10:00:00Z", "message": {"role": "user", "content": "hello there"}}
A2  {"type": "assistant", "message": {"id": "msg_A", "content": [{"type": "text", "text": "Hi."}], "usage": {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 0, "output_tokens": 30}}, "timestamp": "2026-11-14T10:00:02Z"}
S20 {"type": "system", "subtype": "turn_duration", "timestamp": "2026-11-14T10:00:20Z"}
```

Unless stated otherwise a case is `U0, A2, W, S20`, where W is the case line:

| Case | W line (byte-exact) | Legacy full run | Expected Go mix cache (legacy writer format) |
|---|---|---|---|
| T01+ | `[1, 2]` | AttributeError `:1069` | `{"size": 451, "res": 0, "conv": 14, "think": 0, "tin": 110, "tout": 30, "c_wr": 100, "c_rd": 0, "mixv6": 1, "c_in": 10, "rb": 0, "pp": 110, "ids": ["msg_A"], "lr": [15.0, true], "lu": 1794650400.0, "cur": null}` |
| T01− | `{}` | OK | as T01+ with `"size": 447` |
| T02+ timed | `{"type": "user", "timestamp": "2026-11-14T10:00:05Z", "message": "oops"}` | AttributeError `:1072` | as T01+ with `"size": 517` |
| T02+ untimed | `{"type": "assistant", "message": "oops"}` | AttributeError `:1097` | as T01+ with `"size": 485` |
| T02− untimed cb | `{"type": "system", "subtype": "compact_boundary", "message": "oops"}` | OK | `size 513`, **`conv 0`, `pp null`** (the boundary resets composition), rest as T01+ |
| T03+ | `{"type": "assistant", "timestamp": "2026-11-14T10:00:05Z", "message": {"id": "msg_B", "usage": [1], "content": []}}` | AttributeError `:1079` | as T01+ with `"size": 560` (msg_A's turn stays closed by S20: `lr [15.0, true]`) |
| T03− continuation | same with `"id": "msg_A"` | OK | `size 560`, **`lr [6.0, true]`** (t1 moved to :05), rest as T01+ |
| T03− untimed | `{"type": "assistant", "message": {"id": "msg_B", "usage": [1], "content": []}}` | OK | as T01+ with `"size": 523` |
| T04+ in | `{"type": "assistant", "message": {"id": "msg_B", "content": [{"type": "text", "text": "Hi."}], "usage": {"input_tokens": "5"}}, "timestamp": "2026-11-14T10:00:05Z"}` | TypeError `:1108` | as T01+ with `"size": 609` |
| T04+ out-only | same with `"usage": {"input_tokens": 5, "output_tokens": "x"}` | TypeError `:1112` | as T01+ with `"size": 629` (the `tin`/`c_in` increments legacy made before raising are **not** applied) |
| T04− seen id | T04+ in with `"id": "msg_A"` | OK | `size 609`, **`conv 17`, `lr [6.0, true]`** (usage ignored, text counted, turn extended) |
| T04− cb | `{"type": "system", "subtype": "compact_boundary", "timestamp": "2026-11-14T10:00:05Z", "message": {"id": "msg_B", "usage": {"input_tokens": "5"}}}` | OK | `size 591`, `conv 0`, `pp null`, rest as T01+ |
| T05+ | transcript `U0, A2′(out 10), B5(msg_B, out 5), W, U9`; W = `{"type": "assistant", "message": {"id": "msg_A", "content": [{"type": "text", "text": "Hi."}], "usage": {"output_tokens": "abc"}}, "timestamp": "2026-11-14T10:00:08Z"}`; U9 = U0 with timestamp `…10:00:09Z` | TypeError `:994` (on U9, when the turn opened by W closes) | `{"size": 887, "res": 0, "conv": 28, "think": 0, "tin": 220, "tout": 15, "c_wr": 200, "c_rd": 0, "mixv6": 1, "c_in": 20, "rb": 0, "pp": 110, "ids": ["msg_A", "msg_B"], "lr": [5.0, true], "lu": 1794650409.0, "cur": null}` |
| T05− lu none | T05+ without U0 | OK | `{"size": 778, …, "conv": 20, …, "tin": 220, "tout": 15, …, "lr": null, "lu": 1794650409.0, "cur": null}` |
| T05~ open at end (**excluded from the diff**) | T05+ without U9 | legacy OK **but writes `"cur": {"id": "msg_A", "t0": 1794650400.0, "t1": 1794650408.0, "out": "abc"}`** (BC-SL-100) | Go: `{"size": 778, "res": 0, "conv": 17, …, "lr": [5.0, true], "lu": 1794650400.0, "cur": {"id": "msg_B", "t0": 1794650400.0, "t1": 1794650405.0, "out": 5}}` |
| T06+ text | `{"type": "assistant", "message": {"id": "msg_B", "content": [{"type": "text", "text": 5}], "usage": {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 0, "output_tokens": 30}}, "timestamp": "2026-11-14T10:00:05Z"}` | TypeError `:1143` | as T01+ with `"size": 691` (msg_B's usage, id and turn are **not** applied) |
| T06+ thinking | `{"type": "assistant", "timestamp": "2026-11-14T10:00:05Z", "message": {"id": "msg_B", "content": [{"type": "thinking", "thinking": true}]}}` | TypeError `:1145` | as T01+ with `"size": 584` |
| T06− cb | `{"type": "system", "subtype": "compact_boundary", "timestamp": "2026-11-14T10:00:05Z", "message": {"content": [{"type": "text", "text": 5}]}}` | OK | `size 586`, `conv 0`, `pp null`, rest as T01+ |
| T06− list | T06+ text with `"text": [1, 2, 3]` | OK | `size 699`, `conv 17`, `tin 220`, `tout 60`, `c_wr 200`, `c_in 20`, `ids ["msg_A", "msg_B"]`, `lr [6.0, true]` |
| T07+ | `{"type": "assistant", "timestamp": "2026-11-14T10:00:05Z", "message": {"id": ["x"], "usage": {}, "content": []}}` | TypeError `:1099` | as T01+ with `"size": 557` |
| T07− no usage | same without `"usage": {}` | OK | as T01+ with `"size": 544` |

Pinned facts this table adds to BC-SL-098:

- Raise sites are exactly `:1069` (T01), `:1072` / `:1097` (T02 timed / untimed), `:1079` (T03), `:1108` / `:1112`
  (T04 input / output), `:994` (T05), `:1143` / `:1145` (T06 text / thinking), `:1099` (T07).
- A positive row's expected cache is byte-identical to T01+'s except for `size`, whenever the W-line comes after a closed
  turn. This is the clearest check that Go applied **no** partial mutation.
- Full per-case JSON: `scratchpad/p3r3/d4ex2_out.json`; exact lines: `d4ex2_lines.json` (both reproducible with
  `d4ex2.py`).

### 3.2 BC-SL-100 (new): legacy persists a poisoned `cur.out` (deferred CP-T05)

When the CP-T05 opening line is the last line of a parse window, legacy saves `cur.out` as the raw non-numeric value
(pinned `"out": "abc"`; any JSON string, list or object behaves the same at `:994`). The next refresh whose new lines
close that turn raises at `:994` before `save_cache`, so the offset never moves past the closer. The crash is then
sticky (CP-T05 in its "foreign cache" form, but written by legacy itself). Consequences:

- **Diff harness:** a T05~ fixture diverges only until a closer arrives. A two-refresh fixture (T05~, then append U9)
  shows legacy degraded and Go rendering normally. That is inside D4-EX-2's intent; mark it excluded.
- **Shadow week / cache swap:** a Go reader can meet a **legacy-written** mix cache with a non-numeric `cur.out`.
  Ruling (b) covers Go writing caches, not Go reading this. Proposed Go reader rule (owner item 10): treat such a `cur`
  as absent (`cur = null`, `lr` unchanged), which is what Go would hold had it parsed the same lines under D4-EX-2.

---

## 4. Target 4: cost-history coloring goldens (BC-SL-101, BC-SL-102)

### 4.1 BC-SL-101 (new): goldens with 20 seeded sessions

`cost.py`/`cost2.py`: frozen `time.time() = 1794615009.0`, `LOCAL_MODEL_PREFIXES=claude-sonnet`, model
`claude-opus-5-5` (lane `anth`), `render_lane` called with only `session_id`, `model`, `cost`. The value shown is the
last part (the cost segment). Seeded `cost-history.json` (`BASE`; `ts = NOW − 3600` unless noted):

| Key | Entry | Counts in $ | Counts in $/h | Why |
|---|---|---|---|---|
| `s01…s12` | backfill, usd 2, 4, …, 24, `api_ms` 3,600,000 | yes | yes (rate = usd) | 1 h of model time ≥ 1,800,000 |
| `g13-cc-short` | **cc**, usd 30, `api_ms` 400,000 | yes | **yes** (270 $/h) | cc gate is 300,000 |
| `g14-bf-short` | backfill, usd 30, `api_ms` 1,000,000 | yes | **no** | backfill gate 1,800,000 |
| `g15-small` | usd 0.99 | no | no | < `COST_MIN_USD` |
| `g16-dgx` | lane dgx, usd 100 | no | no | other lane |
| `g17-old` | usd 50, `ts = NOW − 2,592,000.001` | no | no | `now − ts > 30 d` |
| `g18-edge` | usd 26, `ts = NOW − 2,592,000` exactly | **yes** | yes | the window test is strict `>` |
| `g19-str` | usd `"5"` (string) | no | no | not int/float |
| `g20-noapi` | usd 28, `api_ms` null | yes | no | no model time |
| `sess-self` | cc, usd 500, `ts = NOW − 10` | **no** | no | `k == sid` (self-exclusion); also throttles its own write |

Pinned thresholds: `cost_thresholds("anth", "sess-self") = ((24.0, 30.0), (20.0, 26.0))`. That is 16 dollar values
(p75 index `int(0.75·15) = 11` → 24, p95 index 14 → 30) and 14 rates (index 9 → 20, index 12 → 26). The dgx lane has no
qualifying entries → `(None, None)`.

Cost segment goldens (`sess-self`, colors `\e[90m` grey, `\e[97m` white, `\e[33m` yellow, `\e[31m` red):

| usd | `api_ms` | Segment |
|---|---|---|
| 0.5 | 600,000 | `\e[90m$0.50\e[0m\e[90m $3.0/h\e[0m` (grey $ below $1; the rate is still shown, colored by percentile, 3 < 20 → grey) |
| 1.0 | 100,000 | `\e[97m$1.00\e[0m` (`1.0 < 1` is false → percentile colors; no rate below 300,000 ms) |
| 13.99 | 600,000 | `\e[97m$13.99\e[0m\e[31m $83.9/h\e[0m` |
| 19.99 | 3,600,000 | `\e[97m$19.99\e[0m\e[90m $20.0/h\e[0m` (**color/number mismatch**: 19.99 < p75 20 → grey, but `.1f` shows 20.0) |
| 20.0 | 3,600,000 | `\e[97m$20.00\e[0m\e[33m $20.0/h\e[0m` (rate at exactly p75 → yellow, `>=`) |
| 23.99 | 3,600,000 | `\e[97m$23.99\e[0m\e[33m $24.0/h\e[0m` |
| 24.0 | 3,600,000 | `\e[33m$24.00\e[0m\e[33m $24.0/h\e[0m` ($ at exactly p75 → yellow) |
| 25.99 | 3,600,000 | `\e[33m$25.99\e[0m\e[33m $26.0/h\e[0m` (mismatch: shows 26.0 but 25.99 < p95 26 → yellow, not red) |
| 26.0 | 299,999 | `\e[33m$26.00\e[0m` (no rate: `api_ms < 300000`) |
| 29.99 | 3,600,000 | `\e[33m$29.99\e[0m\e[31m $30.0/h\e[0m` |
| 30.0 | 3,600,000 | `\e[31m$30.00\e[0m\e[31m $30.0/h\e[0m` ($ at exactly p95 → red) |
| 40.0 | 360,000 | `\e[31m$40.00\e[0m\e[31m $400.0/h\e[0m` |

More pins:

| Scenario | Result |
|---|---|
| 9 qualifying sessions (usd 10…18) | `(None, None)` → cold start. A new sid `x` at usd 25 → `\e[33m$25.00\e[0m\e[90m $25.0/h\e[0m` (fixed $25 yellow; rate grey). `record_cost` writes `x` **before** `cost_thresholds` runs, so for any **other** sid the lane now has 10 → `((16.0, 18.0), (16.0, 18.0))` |
| exactly 10 qualifying | thresholds present (`COST_MIN_N = 10` is inclusive) |
| 12 dollar entries but no rate entries | `((18.0, 20.0), None)`. usd 21 at 1 h → `\e[31m$21.00\e[0m\e[90m $21.0/h\e[0m` ($ colored, rate grey) |
| dgx lane, 10 entries (usd 5…50, `api_ms` 1,800,000+i) | thresholds `((35.0, 45.0), (69.99976666744445, 89.99960000177776))`. usd 45 at 30 min → `\e[31m$45.00\e[0m\e[31m $90.0/h\e[0m` |
| `LOCAL_MODEL_PREFIXES` empty | lane None: **no** `record_cost` write, cold-start colors. usd 26 at 1 h → `\e[33m$26.00\e[0m\e[90m $26.0/h\e[0m` |

### 4.2 BC-SL-102 (new): `record_cost` write contract

| Rule | Pin |
|---|---|
| Throttle: no write while the existing entry is `src == "cc"` and `now − ts < 60` (strict) | +59.999 s → unchanged (usd 2.0); +60.000 s → written (usd 4.0, `ts 1794615069.0`) |
| Format (legacy writer, default separators, no trailing newline) | `{"sessions": {"fmt": {"lane": "anth", "usd": 12.3457, "api_ms": 654321.5, "ts": 1794615009.0, "src": "cc"}}}`. `api_ms` is stored as given (int stays int, float stays float); a non-numeric `api_ms` → `null`. `usd` → `round(usd, 4)` (`1.00001` → `1.0`) |
| Self-exclusion with a **numeric** sid (`session_id: 123`, refines BC-SL-079) | refresh 1: written under int key 123, serialized `"123"`. `cost_thresholds` compares `"123" == 123` → false, so **the session's own cost counts in its own percentiles** (`(17.0, 19.0)` instead of `(16.0, 18.0)`). Refresh 2: the loaded dict holds `"123"`, and `s.get(123)` misses. The throttle never applies, and the dict gets **both** `"123"` (old) and `123` (new). `json.dump` writes **two `"123"` keys** in one object; `json.load` keeps the last. The file stays at 2 duplicates on every refresh. Not a production shape (Claude Code session ids are strings); see owner item 8 |

---

## 5. Target 5: backfill function-level BCs (`tools/backfill_cost_history.py`)

Pins from `backfill.py`/`backfill2.py` (copy exec'd, `HOME` in scratch, TZ=UTC, synthetic transcripts). The broad
sweep's BC-BF-001…005 stand. These BCs refine them, line by line.

| ID | Contract | Pinned examples | Lines |
|---|---|---|---|
| **BC-BF-006** line filter and clock | Each line goes through `json.loads`; ValueError → skip. A line whose `timestamp` is falsy is **skipped entirely** (usage, user tracking and `last` included). Otherwise `last = ts(timestamp)` for **every** timestamped line of any type. `ts` = `fromisoformat(s.replace("Z", "+00:00")).timestamp()` with the 3.11 grammar; a naive value is local time | `last` taken from a timestamped `summary` line (P23: 1794650499.0); an untimestamped assistant with 1M input → usd 0.0 (P18); `ts("2026-11-14T10:00:00")` = `ts("…Z")` = 1794650400.0 under TZ=UTC (P25) | `:38-52` |
| **BC-BF-007** message entity | `lu` = ts of the last `type == "user"` line (any content, tool_result included). On an assistant line with a truthy `message.id` and a **dict** `usage`: the first occurrence creates `{t0: lu, t1: last, u: usage, model: model or ""}`; later occurrences set **only** `t1`. Assistant lines with a non-dict usage are ignored entirely | first line wins usage and model even when later lines say haiku with huge usage (P9: 0.007); `usage: [1]` → message ignored (P19); a reappearing id after another message stretches `t1` (0 → 400 s) and fails the stale test, while the intervening message's span still counts (P20) | `:53-62` |
| **BC-BF-008** pricing | family = first of `opus`, `sonnet`, `haiku` contained in `model` (dict order, substring, case-sensitive); none → message skipped for **all** of usd, lane and span. `w1 = cache_creation.ephemeral_1h or 0`; `w5 = ephemeral_5m or (0 if cache_creation else cache_creation_input_tokens or 0)` where `cache_creation = u.cache_creation or {}`. `usd += (in·pi + out·po + w5·p5 + w1·p1 + read·pr)/1e6` | opus 1M in → 4.0 (P1); opus 1M out → 20.0 (P2); sonnet 1000/2000/3000 write/4000 read → 0.0299 (P3); split 60/40 → 0.00062 (P4); split 0/0 with total 100 → **0.0** (P5); `cache_creation: {}` → total at 5m, 0.0005 (P6); haiku 1M read → **0.005** (P7, the documented price is 0.01, pass-2 r3 E-4); fable → 0.0 (P8); `sonnet-opus-mix` → opus price (P24) | `:30-32,64-76` |
| **BC-BF-009** lane | per priced message, `out` goes to `dgx` if `model` starts with any prefix, else `anth`; lane = `max(out, key=out.get)`, so a **tie (including 0/0) → `dgx`**. Prefixes come from `LOCAL_MODEL_PREFIXES` (default `claude-sonnet` only when the variable is **unset**; set-but-empty → no prefixes → every message `anth`). `output_tokens: true` adds 1 | input-only opus session → **`dgx`** (P10, tie 0/0); dgx 100 vs anth 101 → `anth` (P11); `LOCAL_MODEL_PREFIXES=""` with sonnet out 10 → `anth` (M11b), unset → `dgx` (M12b) | `:77,81,89` |
| **BC-BF-010** model time | a message's span counts iff `t0 is not None` and `0 < t1 − t0 ≤ 4·max(out, 1)/15`; `api_ms = Σspan·1000` iff ≥ 1,800,000, else None | out absent, span 0.25 s → counted (limit 0.2667 s, P13); out 450, span exactly 120 s → counted (P16); span exactly 1,800 s with out 10,000 → `api_ms 1800000.0` (P14); 1,799 s → None (P15); assistant before any user line → no span (P17) | `:78-80` |
| **BC-BF-011** session selection | glob `~/.claude/projects/*/*.jsonl` (one level, unsorted); skip if `getmtime < now − days·86400` (counted nowhere); skip if the existing entry has `src == "cc"` (`skipped_cc`); skip if `usd < 1.0` or no timestamped line (`skipped_small`); otherwise **replace** the entry (an older `backfill` entry is overwritten). `--days` is argparse `int` | M1/M2: 5 files → `backfilled 2 sessions (skipped: 1 under $1, 1 already recorded exactly)` (the 31-day-old file is in neither count); `--days 0` and `--days -1` → 0 sessions, **file still rewritten**; `--days 1.5` → argparse usage error on stderr, exit 2, nothing written; the same sid in two project dirs → the later one in glob order wins (M9: 4.0 over 2.0) | `:86-109` |
| **BC-BF-012** history I/O | read `json.load(open(HIST))`; OSError/ValueError → `{}` (the write then **replaces** all history, other top-level keys included). Unless `--dry-run`: `mkstemp(prefix="cost-history.")` in the cache dir (**mode 0600**), `json.dump` (default separators, `allow_nan`, no trailing newline), `os.replace`. Unknown top-level keys survive a normal run. Stdout: the summary line, then `wrote <path>` | M2 output `{"keep": 1, "sessions": {"sid-cc": {…unchanged…}, "sid-bf": {"lane": "dgx", "usd": 2.0, "api_ms": null, "ts": 1794650410.0, "src": "backfill"}, "sid-new": {…}}}`; rerun byte-identical (M3); corrupt file → `keep` lost and the former cc entry recomputed as backfill (M5); **NaN token → `"usd": NaN` written** (M13: `NaN < 1.0` is false), which then poisons the status line's percentile sort | `:90-94,108,110-117` |
| **BC-BF-013** abort contract | any uncaught exception aborts **before** the single write, so nothing is written and the traceback exits 1. One bad line in **any** in-window transcript aborts the whole run | M10: `ValueError: Invalid isoformat string: 'nope'`, no file. Crash triggers (pass-2 r2 B-01…B-08), pinned: unparseable timestamp → ValueError `:39`; non-str timestamp → AttributeError `:39`; non-object line → `:49`; non-dict `message` → `:56`; int `model` → TypeError `:66`; list `cache_creation` → `:72`; string token → TypeError `:75`; unhashable id → `:58`; history top level a list → AttributeError `:94`. Non-crashes: NaN token (usd NaN), `model: null` (→ `""`, unpriced) | `:38-117` |

---

## 6. Exporter (P2): event names and exposition conformance

### 6.1 BC-EX-024 (new): how each consumer treats current and historical event names

| Event name | Writer today | Exporter (`dgx_ledger_exporter.py`) | Status line |
|---|---|---|---|
| `anth_reply` | yes (`dgx_proxy.py:245`) | `passthrough += 1` iff `status == 200` (`:206-207`) | never reads the ledger |
| **`anthropic_reply`** (historical, before 2026-11-10) | no | **same branch** as `anth_reply` (`:206`) | — |
| `dgx_upstream_error` | yes (`:322`) | `errors[(project, user)] += 1` (`:208-210`). Does **not** create a session (`:138` lists only `dgx_request/reply/usage`), does not add session errors, does not move `last_dgx_ts` | — |
| **`anthropic_upstream_error`** (current, §1.3) | yes (`:322`) | **no branch** | — |
| any other name (`anth_ratelimit`, `bridge_*`, a hypothetical older `anthropic_request`/`anthropic_usage`) | — | only `last_ts` (any event with a parseable `t`, `:121-126`) and the dead `sess_proj` (`:136-137`) | — |
| `dgx_request` (name unchanged across versions) | yes | `last_dgx_ts`, totals, sessions | sees it only as VictoriaMetrics' `dgx_llm_last_dgx_request_timestamp_seconds` (`dgx_statusline.py:824`), the only exporter series the status line queries (`:106`) |

Consequences: in production, the 21 `anthropic_upstream_error` events reach no metric except freshness, and the 23
`dgx_upstream_error` events add 23 to `dgx_llm_request_errors_total`. Of those 23, 4 are user cancels (BC-PX-044), and 18
are connection-refused (backend down or unreachable). Historical names cannot change any status line output. Go parity
(D7): keep the `anthropic_reply` alias and the ignore-rule for `anthropic_upstream_error`. D16 consumers follow pass-2
r3 §4.2.

### 6.2 BC-EX-025 (new): exposition vs the text format (gap 6)

`expo.py` built a body from the exporter copy (synthetic ledger, 2 sessions sharing their first 8 characters) and
checked it against the text-format 0.0.4 rules. Findings, all legacy behavior to reproduce under D7:

| Property | Legacy output | Rule in the 0.0.4 text format |
|---|---|---|
| Interleaved metadata | 9 families have another family's `# TYPE` between their own `# TYPE` and first sample (input/output tokens, cache read/captured, the four Anthropic token/duration families, the request-duration pair, `session_requests` / `session_tokens`) | HELP/TYPE should directly precede the family's samples (a convention; lenient parsers do not enforce it) |
| **Non-contiguous families** (new) | the session block emits `requests, tokens_in, tokens_out, errors` **per session** (`:380-387`), so with ≥ 2 sessions every `dgx_llm_session_*` family is split into one fragment per session. Production runs up to `DGX_SESSION_LIMIT = 50` sessions | "all lines for a given metric must be provided as one single group" |
| Untyped families | `dgx_llm_session_tokens_in`, `…_tokens_out`, `…_errors` | allowed (untyped) |
| TYPE without samples | `dgx_llm_session_tokens` (gauge) | allowed (an empty family) |
| TYPE without HELP | the two `…_duration_seconds_count` families, `dgx_llm_fakestop_p_done_latest` | allowed |
| **Possible duplicate series** (new) | the session label is `s_id[:8]` (`:382`). Two sessions with the same first 8 characters, project and user give **identical series** in one scrape (pinned with `sess-aaaaaaaa-1/-2`). With Claude Code's UUID session ids the chance is about 3·10⁻⁷ for 50 sessions; reachable only with crafted ids | a duplicate series is an error for strict consumers |

Parser acceptance:

| Parser | Result | Basis |
|---|---|---|
| `prometheus_client` 0.23.1 text parser (reference, offline) | **accepts** all 84 lines (47 families). Metadata detaches: the interleaved TYPE lines become empty typed families, and the samples land in `unknown`-type families. Every sample value is kept | pinned, `expo.py` |
| **VictoriaMetrics** (production) | **accepts in practice**: production has scraped this exporter through the ledger tunnel for days, and the dashboards work (orchestrator). The status line's `☾ idle` reads `dgx_llm_last_dgx_request_timestamp_seconds`, which is emitted **after** the first interleaved block (`:367-370`), so the scrape is parsed at least that far. VictoriaMetrics parses each sample line independently and does not apply type metadata to storage (product behavior from documentation knowledge, **not verified against VictoriaMetrics source** here) | production evidence plus the format rules |
| Prometheus server / Go `expfmt` (client_golang, promtool) | **not verified.** Prometheus' scrape parser is lenient on ordering; duplicate series would surface as scrape warnings. A Go client library **producing** this output would refuse: client_golang's registry rejects duplicate series and groups families with HELP, so the bytes would change (D7) | knowledge, LOW |

Contract for the Go exporter during parity: a **hand-written** writer that reproduces these bytes, not a client library
(owner item 7). Owner check after the soak: confirm that the per-session panels show all sessions. That would prove
VictoriaMetrics ingests the non-contiguous fragments; any dashboard that is empty for a recent session points to a
parser problem.

---

## 7. Crash catalogue status (deltas only)

| Class | Change this round |
|---|---|
| Status line (43 paths) | unchanged count. CP-T05 gains a **legacy-written cache trigger** (BC-SL-100); D4-EX-2 rows now have derived expectations (BC-SL-099) |
| Proxy P-S4 | confirmed for 12.3.1 defaults, with the empty-body and user-config exceptions (§1.1) |
| Proxy P-R1…R4, P-S1…S3 | outcomes source-confirmed (assumption 5; pass-2 r3 §1.1) |
| Backfill B-01…B-08 | pinned with raise lines (BC-BF-013), plus a history-shape trigger (`:94`). Non-crash NaN path (BC-BF-012) |
| Exporter E-* | unchanged |

---

## Owner decisions pending

Carried from round 2 (one-line recommendation each):

1. **CP-T05 detection point** (BC-SL-098): skip the opening line vs skip only the turn. *Recommend: confirm the
   opening-line skip. It also prevents legacy's poisoned-cache form (BC-SL-100), and the table in §3 already encodes it.*
2. **Interrupted generations counted as DGX errors** (BC-PX-039/044, now **production-confirmed**: 4 of 23). *Recommend:
   reproduce through P2/P3 parity (D7); after cutover add a `reason` field and a separate cancel counter, and leave
   `…_errors_total` unchanged.* (Same as pass-2 r3 #16.)
3. **P-S4** (no error-body note or `failed-req` capture for an SSE error reply). *Recommend: an approved deviation. Go
   writes the note and capture. Only the decision log and capture files differ; the ledger and metrics do not.*
4. **Exporter DST false idle** (BC-EX-020, confirmed). *Recommend: accept through cutover (D7); afterwards add an epoch
   field (e.g. `ts`) next to `t` and have the exporter prefer it.*
5. **Exporter tally misattribution** (BC-EX-019, confirmed). *Recommend: reproduce during P2 parity; after cutover
   match the bracketed kind token only at its fixed position and read `p_done=` only from the `kev=` field.*

New this round:

6. **Upstream-error text in the Go proxy** (BC-PX-044). *Recommend: emit mitmproxy's fixed strings for the three
   deterministic causes (`Client disconnected.`, `server closed connection`, `HTTP/1 protocol error: …`) and
   `Connect call failed ('<host>', <port>)` with the platform's errno prefix. Declare `error` text out of byte-parity
   scope, since no metric reads it.*
7. **Exporter writer**: hand-written byte-identical vs client library (BC-EX-025). *Recommend: hand-written during
   parity. A client library changes the bytes and fails the scrape on a duplicate session series.*
8. **Numeric-sid duplicate keys in `cost-history.json`** (BC-SL-102) vs ruling (b)'s "exact format". *Recommend: out of
   byte-parity scope as a known difference (non-production stdin shape); Go writes one key per sid.*
9. **Backfill NaN and history shape** (BC-BF-012/013). *Recommend: keep legacy behavior for the one-off tool; any
   `hylo cost backfill` port skips non-finite usd (documented deviation).*
10. **Go reader of a legacy-written poisoned mix cache** (BC-SL-100). *Recommend: treat a non-numeric `cur.out` as no
    open turn (`cur = null`), consistent with D4-EX-2.*

Also open in pass-2 r3 §5 (not duplicated here): items 6 (P-R4 credentials), 7 (`x-api-key` forwarding), 10
(`count_tokens` vs D13), 11 (exporter poison lines), 17 (eager CONNECT).

---

## Delta Summary

- **New BCs (11 + 8 backfill = 19):** status line 4 (BC-SL-099 D4-EX-2 table, 100 poisoned `cur.out`, 101 cost goldens,
  102 `record_cost` write contract). Proxy 2 (BC-PX-043 Host header, 044 error-cause table). Exporter 2 (BC-EX-024 event
  names, 025 exposition conformance). Backfill 8 (BC-BF-006…013).
- **Refined (12):** BC-PX-034 (b) and 038 (TypeError, version-pinned), 037 (empty-body row), 039 (production-confirmed,
  HIGH), 040 (chunk sources), 041 (Content-Length closed), 042 (P-R2 outcome), P-S4 (confirmed, two exceptions), BC-SL-098
  (CP-T05 clause tightened; raise lines pinned), BC-SL-079 (numeric sid self-inclusion and duplicate keys), BC-EX-018
  (non-contiguous session families), BC-BF-001…005 (superseded in detail by 006…013).
- **Confirmed:** all six mitmproxy assumptions; the chunk dependence, DST false idle, tally misattribution, P-S4 and
  CP-T05 claims from round 2.
- **Retraction:** CONV-ABS-8 (the "legacy never crashes" parenthetical in the CP-T05 row).
- **Premise corrections:** `anthropic_upstream_error` is current; event count 21 vs pass-2 r3's 20; CONV-ABS-6 ID
  collision.
- **Evidence recorded:** orchestrator ledger counts (23/21 upstream errors by text) close round-2 gap 2.

## Remaining Gaps (verbatim-carryable)

1. Owner check (after the soak, LOW): whether `~/.mitmproxy/config.yaml` on the prototype machine sets any option that
   changes the defaults used here (`store_streamed_bodies`, `stream_large_bodies`, `body_size_limit`,
   `connection_strategy`, `validate_inbound_headers`). If none is set, P-S4 and the BC-PX-037 table hold as written.
2. Owner check (after the soak): open a per-session Grafana panel fed by `dgx_llm_session_*` with ≥ 2 recent sessions
   and confirm every session appears. That proves VictoriaMetrics ingests non-contiguous family fragments (BC-EX-025).
   Optionally run `promtool check metrics` on one saved scrape body, offline, to record a strict parser's verdict.
3. Reconcile the `anthropic_upstream_error` count (21 here, 20 in pass-2 r3 §4.1) in pass-2 round 4.
4. P3 harness design input: capture real `feed` boundaries (HTTP chunk plus TCP read) for the replay corpus, or prove the
   corpus is boundary-insensitive (well-formed, lines < 64,000 bytes) (BC-PX-040).
5. Not pinned by execution (needs mitmproxy to run): the Host header value (BC-PX-043) and the 502 page bytes mitmproxy
   sends on connect failure. Source-level HIGH; a P3 replay against a stub backend settles both.
6. Owner decisions 1–10 above.

## Novelty Assessment

Novelty: SUBSTANTIVE

Removing this round would change how P1, P2, P3 and the backfill port are specified:

- P1: D4-EX-2 now has a concrete 21-row Go table-test set with byte-exact inputs and expected caches. A legacy-written
  poisoned cache state (BC-SL-100) was unknown and needs a Go reader rule. Round 2's "legacy never crashes" claim was
  retracted.
- P1: the cost-coloring contract has goldens for every gate (cc vs backfill rate gate, window edge, self-exclusion,
  cold start at 9/10, rate-less thresholds) and two color/number mismatches. Numeric sids create duplicate JSON keys,
  which conflicts with ruling (b).
- P3: the mitmproxy model is verified, not assumed. Production data confirms that user cancels are logged as upstream
  errors and that the client talks HTTP/1.1. New contracts: the error-cause table and the Host-header rewrite.
- P2: the exposition has non-contiguous families and possible duplicate series, which rules out a client library during
  parity. The event-name table settles how historical and current names are treated.
- Backfill: eight function-level BCs with pinned examples, including the input-only session whose lane is `dgx` (0/0
  tie), set-but-empty prefixes, and NaN usd written to history.

## Convergence Declaration

Another round is needed. The new items change the model (a legacy-written crash state, a new error contract,
exposition conformance, eight backfill BCs). What remains is mostly owner checks and decisions (gaps 1–3, 6) plus two
harness inputs (gaps 4–5).

## State Checkpoint

```yaml
pass: 3
round: 3
status: complete
files_scanned: 4 legacy files in full (dgx_proxy.py, dgx_ledger_exporter.py, tools/backfill_cost_history.py) + dgx_statusline.py in part + 10 mitmproxy 12.3.1 modules
timestamp: 2026-11-14T06:43:05Z
novelty: SUBSTANTIVE
new_bcs: {SL: 4, PX: 2, EX: 2, BF: 8}
refined_bcs: 12
retractions: [CONV-ABS-8]
premise_corrections: [anthropic_upstream_error-is-current, count-21-vs-20, CONV-ABS-6-alias-of-7]
status_line_crash_total: 43
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r3/
next: pass 3 round 4 (carry "Remaining Gaps" verbatim)
```
