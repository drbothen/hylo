# Pass 3 deepening, round 7: behavioral contracts (hylo-legacy), verification round

- **Scope:** `legacy/` is unchanged: 11 files, 3,181 lines (recounted with `wc -l`). Re-read this round: `dgx_statusline.py:436-470,560-640,1155-1245`;
  `dgx_ledger_exporter.py` in full; `dgx_proxy.py:40-340,339-460,465-522`; `auto_continue.py:190-275`. Read-only, for citations only: mitmproxy
  12.3.1 `http:39-45,426-441`, `addonmanager:44-59,264-300`, `options:240-246`, `proxy/server:50-75,110-120,378-392` (from the per-window venv's
  site-packages; nothing was imported or executed from there).
- **Inputs read:** pass-3 r6 (in full), r5 (in full), r4 (§0, §3, §4, §6, §7 canonical index); pass-3 broad, r1, r2, r3 (grep for Target B);
  pass-2 r8 (§0-§2, §5-§6, Delta, Gaps); **pass-2 r9** (`…-pass-2-deep-domain-r9.md`, present from 01:45 local; read only, not edited), and pass-2
  r2 §6 (hook catalogue), r4 §1.3 (HTTP/2 row).
- **Orchestrator messages applied (2026-11-14):** (1) the ledger holds 0 lone-surrogate escapes and 0 non-ASCII `project` values, so E-22 and
  BC-PX-048's crash rows are **latent**. (2) Pass 2 converged at r9 (NITPICK). CONV-ABS-27/28 are taken. OD-44 is unused. 0 `bridge_ws_*` events
  2026-11-09..14 (OD-43 confirmed). The 2 rerouted h2 `/v1/messages` are `dgx_request` lines with empty session/meta_user_id/project and a
  `claude-sonnet*` model. Of the 241 `/v1/code/sessions` GETs, 216-217 streamed. **Add a BC for legacy's pass-through duration behavior plus the
  HY-PASS-1 requirement** (done: BC-PX-049, §4). (3) **The VictoriaMetrics capture is done** (§5): CP-N01/CP-N02 (pass-2 CP-40/CP-41) are latent.
- **Method:** fresh scripts (none reuses a round-6 script or fixture) in
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r7/`. Each one execs a **text copy** of the
  legacy file in a fresh namespace, redirects `HOME`, the ledger, the hook log and the decision log into the scratchpad, and asserts the cited source
  lines before it runs. Scripts and outputs: `sl_tick.py` → `sl_tick_out.txt`; `ex_e22.py` → `ex_e22_out.txt` (3.11.7; 3.9.6 with `LANG=en_US.UTF-8`;
  3.9.6 with an empty environment, as under launchd); `px_abort.py` → `px_abort_out.txt` (twice: `LANG=en_US.UTF-8` strict, and `LC_ALL=C`, which
  turns on UTF-8 mode); `hk_log.py` → `hk_log_out.txt`; `region_stmts.py` → `region_stmts_out.txt`. Interpreters: `/opt/homebrew/anaconda3/bin/python3
  -I` (3.11.7) and `/usr/bin/python3 -I` (3.9.6). No legacy main() or server ran. No socket was bound (the exporter handler is driven in memory). No
  proxy ran and nothing was networked. `CLAUDE.local.md` was not read. No git commit.
- **Notation:** `\e` is ESC (U+001B). `\udcXX` inside a JSON string is the 6-character ASCII escape. A raw lone surrogate code point is written
  U+DCXX. A bare `:N` means the file named in the section heading. **P2rN**/**P3rN** = pass-2/pass-3 round N.
- **IDs (append-only):** new **BC-PX-049** (carried from P2r8 §1.2-1.3 / P2r9 gap 3). New hook crash row **H-09**. Retraction **CONV-ABS-22** (from
  the 22-24 range; 23 and 24 unused). **No new OD** (OD-44 stays unused; the next new OD would be OD-46).

---

## 1. Target A: round 6's three unstated effects, re-verified from scratch

### 1.1 Verification table

| r6 item | Verdict | New evidence (this round) |
|---|---|---|
| **R1-1 / BC-SL-027 amendment:** ⛏ is part of the `$` segment, so it needs `cost.total_cost_usd` numeric and `> 0` | **CONFIRMED** | AST: the ⛏ `If` at `:627` is a descendant of the `If` at `:602` (`isinstance(usd, (int, float)) and usd > 0`), whose body ends at `:636` (`parts.append(cseg)`). Execution with new fixtures (tin 3.4M, tout 120k, `dgx_mtok` 0.07, `dgx_rate` 31.0, which is ≥ 30.4, so the basis is ok): `total_cost_usd` absent, `0`, `0.0`, NaN, `-0.5`, `"1.5"` (str), `None` and `False` give **no ⛏**, and the token segment is the last row-1 segment (4 parts). `True` gives `\e[97m$1.00\e[0m\e[90m ⛏0.25\e[0m` (a bool is an int; BC-SL-082 already lists `True→$1.00`). `0.004` gives `\e[90m$0.00\e[0m\e[90m ⛏0.25\e[0m`. `2.5` with `api_ms` 600000 gives `\e[97m$2.50\e[0m\e[90m $15.0/h\e[0m\e[90m ⛏0.25\e[0m`. With the basis not ok: no cost gives no `⛏n/a`, `2.5` gives `\e[97m$2.50\e[0m\e[90m ⛏n/a\e[0m`. The ANTH lane never shows ⛏ |
| **R2-1 / E-22:** a lone surrogate in a label value makes `.encode()` at `:399` raise on every scrape. The process stays up | **CONFIRMED, trigger list refined** | The handler runs in memory (`object.__new__(Handler)`, `wfile` = BytesIO). Ledger lines come from `json.dumps` defaults on a header value decoded as mitmproxy does it (`b"caf\xe9".decode("utf-8", "surrogateescape")`). The result is **identical** on 3.11.7, on 3.9.6 with `LANG`, and on 3.9.6 with an empty environment. For each trigger: startup `rebuild()` is ok; scrape 1 raises `UnicodeEncodeError` with **0 bytes written** (no status line); `processed_size` equals the file size; scrape 2 raises; `?rebuild=1` raises; a later valid append still raises (the full rescan re-reads the poisoned line). Triggers pinned: `project` through `dgx_request`, through `anth_request` alone, and through `dgx_upstream_error` alone; `user` through a `dgx_reply` with status 500; `account` through `dgx_usage`; `device` through a `meta_user_id` JSON string; `session` with the surrogate at index 3. **Not** triggers (200): the UTF-8 control `café`; `session` with the surrogate at index 9 (cut by `[:8]`); `project` only on an `anth_reply` line (not a label source) |
| **R3-1 / BC-PX-048:** `note()` lets `UnicodeEncodeError` (a `ValueError`) escape. The calling hook stops | **CONFIRMED in both locale modes** | Locale encoding is `UTF-8`/utf8_mode 0 with `LANG`, and `utf-8`/utf8_mode 1 with `LC_ALL=C`. `open()` is strict in both, so the results are the same. Rows below |
| P-E1 (`:321` before `:322`) | **CONFIRMED** | Project header bytes `caf\xe9`: `error()` raises and the ledger stays `[]` on **both** lanes (backend host → no `dgx_upstream_error`; `api.anthropic.com` → no `anthropic_upstream_error`). UTF-8 bytes `caf\xc3\xa9` give `['dgx_upstream_error']` / `['anthropic_upstream_error']` |
| P-S5 (`:286` before the capture `:288-299`) | **CONFIRMED** | DGX 422 with body bytes `…bad \xff input…`: the decode goes through the `strict=False` fallback (mitmproxy `http:438-441`) → raise. The ledger has `['dgx_reply']` and **0** `failed-req-*.json`. The ASCII body control gives `['dgx_reply']` and 1 capture |
| **P-S6** (`:240` before `:245,247`) | **CONFIRMED, now pinned by execution (MEDIUM → HIGH)** | The full chain runs on a stub flow: `responseheaders()` installs the copied `_SSETap` (because `"text/event-stream" in ctype`), the SSE bytes are fed in 37-byte chunks plus `b""` (usage `(21, 34)`), then `response()`. With a `content-type` value holding a raw `0xE9` byte (decoded with surrogateescape), it raises at `:240` and the ledger stays `[]`: **neither `anth_reply` nor `anth_usage`**. The ASCII `content-type` control gives `['anth_reply', 'anth_usage']`. Reachability: Anthropic would have to send non-UTF-8 bytes in `Content-Type` (judgment: not realistic) |
| P-R5 (`:510` after `_logged_unknown.add` at `:509`) | **CONFIRMED** | Unknown block type `"zz\udce9"` (a JSON escape in an ASCII body). Attempt 1 raises: host stays `api.anthropic.com`, the body is not rewritten, the ledger stays `[]`. Attempt 2 (same proxy generation) is ok: host `192.0.2.77`, body rewritten, `['dgx_request']`. Control `"zzé"` (a valid code point): routed on the first attempt, and the decision log holds `zzé` |

Supporting source checks, re-read this round:

- mitmproxy 12.3.1 `http:40-41` decodes headers with `x.decode("utf-8", "surrogateescape")`. `http:426-441`: `get_text(strict=False)` falls back to
  `content.decode("utf8", "surrogateescape")`.
- `addonmanager:44-59`: `safecall` logs `Addon error: <value>` and swallows everything except `AddonHalt`/`OptionsError`. So the flow continues
  with the state the hook had already applied.
- Production corroboration that no note-abort has happened: P2r9 A9 counts exactly **1** `Addon error` line in the 40 retained logs, and it is the
  known mid-edit-reload `NameError` (P2r5). A note-abort would log `Addon error: 'utf-8' codec can't encode character … surrogates not allowed`.

### 1.2 Reachability, set by the orchestrator's ledger evidence

The ledger has **0** lines with a lone-surrogate escape and **0** non-ASCII `project` values. The one plausible production vector, a non-ASCII
working-directory basename sent as Latin-1 bytes through `X-DGX-Project` (`claude-dgx:44`), **has not occurred**. Marked:

| Item | Reachability (final) |
|---|---|
| E-22 | **latent**: only with a non-ASCII project name or label value whose bytes are not UTF-8 |
| P-E1 | **latent**: same vector as E-22 |
| P-S5 | **latent**: needs non-UTF-8 bytes in a backend error body |
| P-S6 | **latent**: needs non-UTF-8 bytes in Anthropic's `Content-Type` (judgment: not realistic) |
| P-R5 | **latent**: needs a hand-crafted request (a lone-surrogate escape in a block type) |

All five stay in the crash catalogues with this reachability. Their contracts and Go treatment are unchanged (E-22 → OD-11; P-* → OD-45). Owner check 3
from r6 is **closed**.

### 1.3 Class sweep: the same mechanism at every other text-mode write in `legacy/` (new)

Round 6's three findings share one mechanism: a str holding a lone surrogate reaches a **strict UTF-8 text write** that does not catch
`UnicodeEncodeError`. This round checked every text-mode write site in the six Python files (AST and grep list: `open(…,"a"/"w")`, `fdopen`,
`write_text`, `print`, `json.dump`, `.encode()`):

| Site | Can a lone surrogate reach it? | Outcome | Covered by |
|---|---|---|---|
| proxy `note()` `:65-74` | yes (headers, error bodies, body JSON escapes) | the hook aborts | BC-PX-048 (r6), confirmed §1.1 |
| proxy `ledger()` `:56-62` | yes, but `json.dumps` escapes it to ASCII | written | BC-PX-048 item 4 |
| proxy capture `write_text` `:296` | no: `get_text()` is strict, so the str is valid | — | BC-PX-021 |
| exporter body `.encode()` `:399` | yes (labels) | the scrape fails | E-22 (r6), confirmed §1.1 |
| exporter startup `print` `:413` | no (env and path text) | — | BC-EX-001 |
| status line `print` `:1234`, `:935` | yes (display name, id, project label) | degraded line | **CP-S17** (pass-3 broad §B, strict column of BC-SL-076) |
| status line cache writes (`json.dump`, `:202-203`) | escaped by `ensure_ascii` | written | BC-SL-052/070 |
| backfill `json.dump` `:115`, `print` `:110,117` | escaped / numeric and path text | — | BC-BF-012 |
| preflight `print` `:27-40` | no (host, port, OS error text) | — | BC-PF-002 |
| **hook `_log` `:193-201`** | **yes**: `session={data.get('session_id')}` and `stop_hook_active={…}` are rendered with `str()`, **not** `repr()` | **the hook crashes: exit 1, no stdout, no log** | **not stated anywhere** → **H-09** (§2) |
| hook `emit` `print(json.dumps(…))` `:206` | escaped by `ensure_ascii` | — | BC-HK-021 |

The `tail` field is safe because it is rendered with `{tail!r}`, and `repr()` escapes a lone surrogate as `\udce9`.

---

## 2. H-09 (new hook crash row) and CONV-ABS-22

**Pinned** (`hk_log.py`, colon-fake path, so no Kev and no network; 3.11.7, because the hook does not import on 3.9, H-08):

| Stdin (JSON text) | Result | Stdout | Hook-log lines |
|---|---|---|---|
| `"session_id":"s-1"`, message ending in `:` | ok | 313 B (`hookSpecificOutput` JSON) | 1 |
| `"session_id":"s-\udce9"`, same message | **`UnicodeEncodeError`** | **0** | **0** |
| `"session_id":"s-2"`, message containing `caf\udce9` | ok (the tail is `repr`-escaped) | 313 B | 1 |

**H-09** (add to P2r2 §6.3 as the next hook crash ID): *a lone-surrogate escape in `session_id` (or in a truthy string `stop_hook_active` on the
non-English path, which logs before the `stop_hook_active` check) makes `_log` raise `UnicodeEncodeError`, which is not caught (`:200` catches only
`OSError`). The hook exits 1 with no stdout and no log line.* Because `emit` logs **before** it prints (BC-HK-013/021), the crash also suppresses a
continue decision (non-English, colon-fake, Kev or heuristic), so the stop is allowed. A `kev-allow` loses its calibration line.

- **Reachability: latent.** Claude Code's `session_id` is a UUID and `stop_hook_active` is a boolean (P2r2 §6.1). No real input carries a lone
  surrogate.
- **Contract owner:** BC-HK-019 ("no top-level guard: crash → exit 1, no stdout") already states the outcome. H-09 adds a trigger, not a new outcome.
- **Go:** Go's `encoding/json` turns a lone-surrogate escape into U+FFFD (pinned in r6 with go1.26.5), so a Go hook would log and emit. Parity
  treatment: the same choice as **OD-45**, whose recommendation (a diagnostic-log write never changes a routing or ledger outcome) carries over
  to "a hook-log write never changes the hook's decision". Recommend that the owner rules OD-45 for **both** logs. No new OD.

**CONV-ABS-22 (retraction):** P3r6 §1.5 and §1.6, "A4 Stop hook main flow (105 statements) … **No unstated effect**", is wrong for `_log`
(`auto_continue.py:196-198`). That `_log` raises on a lone surrogate in `session_id` was unstated. Ground truth: H-09. P3r6 §1.6's total of "3"
unstated effects becomes **4** (the fourth latent). RET crosswalk: **RET-15 = CONV-ABS-22**.

---

## 3. Target B: propagation of the orchestrator's correction (CONV-ABS-25 / CONV-ABS-26)

Grep over the broad pass-3 file and r1-r6 for `HTTP/2`, `HTTP/1.1`, `HTTP/1 `, `h2`, `bridge`, `Remote Control`, `websocket`, then each hit read in
context:

| # | File, place | Statement | Rests on the retracted fact? | Amended in r6? | Amended wording (apply) |
|---|---|---|---|---|---|
| PR-1 | P3r4 §0, "mitmdump logs" row | "38 retained logs: **0** ` HTTP/2.0` lines … consequence 2 is **observed** … error-cause table applies in its HTTP/1 form only" | yes (the 0-line count) | **yes** (r6 §6 RET note, BC-PX-044 flag) | — |
| PR-2 | P3r3 §2.3 consequence 2 (BC-PX-044) | "the `Client disconnected.` wording is the HTTP/1 server layer's … So in production **Claude Code talks HTTP/1.1** to the proxy" | **no**: this rests on the error text, not on the count, and it is about Claude Code. Still true | yes (BC-PX-044 flag) | Optional sharpening: "…so **Claude Code's** `/v1/messages` flows are HTTP/1.1 (confirmed by P2r8 attribution). Other clients reach the proxy over h2 (CONV-ABS-25); for them a user cancel would read `stream reset by client (…)`" |
| PR-3 | P3r3 Delta Summary, P3 bullet | "the client talks HTTP/1.1" | partly (generic "the client") | not explicitly | "**Claude Code** talks HTTP/1.1; h2 clients exist (child tools, CONV-ABS-25)" |
| PR-4 | P3r3 §2.4 (BC-PX-043) | "the request line stays in origin form, because the client used CONNECT plus TLS (HTTP/1, §2.3)" | partly | yes (BC-PX-043 flag: V-1 needs an h2 case) | — (flag suffices) |
| PR-5 | P3r4 §3, **V-1** | "Request line in origin form (client used CONNECT + TLS over HTTP/1.1)" | partly | **only through the BC-PX-043 flag**; r6 gap 2 restates V-1 without the h2 case | "…(Claude Code uses CONNECT + TLS over HTTP/1.1). **Add one h2 case:** an h2 client's rerouted request carries `:authority`, updated the same way (P3r3 §2.4)" |
| PR-6 | P3r4 §3, **V-2** | "HTTP/1.1: the 502 is sent and the client connection closes (P2r4 §1.3, HTTP/1 row; **production is HTTP/1.1**)" | **yes** | **no** | "HTTP/1.1 (Claude Code): the 502 is sent and the client connection closes (P2r4 §1.3, HTTP/1 row). **HTTP/2 (non-Claude-Code clients, observed in production, CONV-ABS-25):** the 502 goes out on the stream, the connection stays open, and later DGX-lane requests on it fail at once with the cached error (P2r4 §1.3 HTTP/2 row). Reachable in legacy only by child tools; D14 removes them in hylo. Record both client-side byte sequences" |
| PR-7 | broad BC-PX-001 / BC-PX-026; P3r4 §4 C-3 row; P3r4 §7.3 rows | `bridge.claudeusercontent.com` upgrade / response rules | as **code**, correct; as "Remote Control", retracted | yes (r6 flags "never fires in production", OD-43) | Add to both flags: "0 `bridge_ws_*` events in the ledger 2026-11-09..14 (P2r9, OD-43 premise confirmed)" |
| PR-8 | P3r6 header and §5 (Remote Control channels) | "long-lived streaming GETs on `/v1/code/sessions/…`" | no (the count qualifier is CONV-ABS-28's) | — | Optional precision: "241 GETs, of which 216-217 streamed and 24 buffered (P2r9 CONV-ABS-28)" |
| PR-9 | P3r6 §5, BC-LN-004 flag | "2 `/v1/messages` from a non-Claude-Code h2 child rerouted to the DGX" | no | — | Add "ledger-corroborated: written as `dgx_request` with empty `session`/`meta_user_id`/`project` and a `claude-sonnet*` model (P2r9 §2.2)" |
| PR-10 | P3r3 §2.3 Conf line; P3r2 C-table; P3r6 §5 row "HTTP/1.1 persistence is mitmproxy's default" | neutral mentions of h1/h2 layers | no | — | — |

**Result:** one statement still rests on the retracted fact without an amendment (**PR-6**, V-2's "production is HTTP/1.1"). Two more need a wording
fix so that "the client" reads "Claude Code" (**PR-3**, **PR-5**). Every bridge statement is code-accurate and already flagged. No BC's contract text
changes. Nothing in pass 3 still names `bridge.claudeusercontent.com` as the Remote Control host.

---

## 4. BC-PX-049 (new; carries P2r8 §1.2-1.3 and P2r9 gap 3): pass-through flows have no total-duration limit, only a 600 s inactivity cut

**Source:** `dgx_proxy.py:99-104` (request: every non-`/v1/messages` path and every other host returns untouched), `:175-206` (responseheaders:
`anth_ratelimit` capture for `api.anthropic.com`, SSE → tap + stream, other non-`/v1/messages` responses are left on mitmproxy's default),
`:211-216,250-251` (`response` writes nothing for non-`/v1/messages` paths), `:316-317` (`error` returns for non-`/v1/messages` paths); `claude-dgx:75`
(no `tcp_timeout` override; P3r4 §0: no `config.yaml`). mitmproxy 12.3.1: `options:240-246` (`tcp_timeout` int 600, "closed after this period of
inactivity"); `proxy/server:50-75` (`TimeoutWatchdog`), `:116-120` (one watchdog per client connection with `tcp_timeout`), `:387`
(`register_activity()` on **every** server event, from either side); `proxy/layers/websocket:196-201` (pings and pongs relayed end to end).

**Contract (legacy).**

1. A pass-through flow (any host other than the routed `api.anthropic.com/v1/messages*`, or any other path on `api.anthropic.com`, including the
   `/api/frame/sync` WebSocket and the `/v1/code/sessions/…` GETs) has **no total-duration limit** in the addon or in mitmproxy's defaults.
2. The only proxy-side cut is the **inactivity** watchdog: a client connection on which **no event in either direction** occurs for 600 s is closed
   ("Closing connection due to inactivity"). Any byte, message or WebSocket ping/pong resets it.
3. Ledger effect of a pass-through flow: **none**, whether it ends normally, by server EOF, or by the inactivity cut. Exceptions: `anth_ratelimit`
   when an `api.anthropic.com` response carries changed `anthropic-ratelimit-unified-*` headers (BC-PX-013), and an `_SSETap` on SSE responses whose
   result is never written (BC-PX-014, no `/v1/messages` path).
4. Streaming: SSE responses are streamed on any host (BC-PX-014/037). Other pass-through responses are **buffered** in full (mitmproxy default;
   BC-PX-037). The 24 buffered `/v1/code/sessions` GETs are this case.

**Production evidence (P2r8 §1.1-§2.2, re-derived in P2r9):** 8 `/api/frame/sync` WebSockets lasted 763-13,860 s with server pings every 20 s (median
20.0 s), and **none was cut**. Of the 216-217 streamed `/v1/code/sessions` GETs, the longest was 3,599 s (the **server's** cap) and 148 lasted ≥ 600 s,
**none cut**. Endings: 129 normal, 80 server EOF, 32 `Client disconnected.`. The watchdog fired 57 times in 40 logs: 56 idle npm keep-alives (benign)
and **1 in-flight cut** of an MCP SSE stream (`mcp.atlassian.com`) that was silent for ≥ 600 s. That cut left no ledger trace (contract 3).

**Go contract (P4 run / P3 proxy), linked to D13 and D6.** D13: "every other host and path is forwarded unchanged". D6: Remote Control must keep
working. **HY-PASS-1:** a pass-through flow has no total-duration limit and is relayed as it arrives. hylo's routed-lane timeout (HY-TIMEOUT-1, at
least the client's `API_TIMEOUT_MS` = 30 min, BC-PX-046) **must never apply** to pass-through flows: it would cut the WebSocket (observed up to 3 h
51 min) and the 1-hour session streams. Inactivity cut on pass-through: per **OD-37** as amended in P2r8 (recommend: no idle cut while a response is
streaming; idle cut only on connections with no flow in progress; the WebSocket idle limit must exceed the 20 s ping interval with margin,
HY-BIND-6). Legacy's in-flight cut of a silent stream after 600 s is the behavior OD-37 recommends **not** reproducing. Table tests: a 2 h
WebSocket with 20 s pings survives; a 3,600 s SSE GET survives; a silent streaming response is not cut while in flight (per the OD-37 ruling); a
routed `/v1/messages` flow still hits HY-TIMEOUT-1.

Index row: `BC-PX-049 | Pass-through flows: no total-duration limit; 600 s inactivity cut only; no ledger trace | internal/proxy | P3 | OD-37 | D13, D6, HY-PASS-1, HY-BIND-6 | H | r7 | new r7, carried from P2r8 §1.2-1.3 / P2r9`.
Related flags: BC-PX-002 ("duration semantics in BC-PX-049"); BC-PX-046 ("row 1 is the routed-lane case of BC-PX-049 contract 2").

---

## 5. VictoriaMetrics capture recorded (owner capture closed; orchestrator, 2026-11-14, read-only)

| Capture | Result |
|---|---|
| One instant query with the exact legacy `QUERY` (`dgx_statusline.py:102-123`, URL built as in `fetch_sample`) | `status: success`, **19 series, all finite** (no NaN, no ±Inf). Light load: `dgx_sl:ttft_n30m` = 6 (< 20, so the p95 is the max), `dgx_ttft:p95_30m` = 0.059, `gen_rate1m` = 0, both `up{job}` = 1 |
| 24 h `query_range`, 60 s step | `sum(increase(vllm:time_to_first_token_seconds_count[30m]))`: 1,441 points, **2 zero points** (truly idle 30-min windows occurred). `dgx_ttft:p95_30m`: 1,439 points, **0 non-finite**, one 3-minute gap. So in idle windows the p95 series is **absent**, not NaN (MetricsQL drops NaN from query output) |

**Consequence:** **CP-N01** (KV NaN, `:759`; pass-2 CP-40) and **CP-N02** (sparkline NaN/+Inf, `:675`; pass-2 CP-41) are **not reachable in
production through these series**. Marked **latent** (reachable only with a backend or TSDB that emits NaN). The realistic case in CP-N02's
catalogue text ("`DGX_SL_TRACE=ttft` on a quiet box") does not occur with VictoriaMetrics, because an absent series is not stored as NaN. BC-SL-073,
074 and 075 keep their contracts: the Go port handles NaN defensively and byte for byte, per the owner ruling on catalogued crash paths. The
absent-series path is the one the fresh path takes (missing key → the existing `None` handling in BC-SL-043..051). No contract change.

---

## 6. Target C: final completeness statement for pass 3

Evidence combined:

| Round | Method | Covered | Uncovered found → disposition |
|---|---|---|---|
| r5 | mechanical diff: every function, effect site and exception handler (Python AST) plus shell branches | **283 items** (257 Python, 26 shell) | 2 items plus 1 cited-region gap → BC-EX-027. 5 shell items out of scope (D6) |
| r6 | statement-by-statement re-read against the citing BCs | **903 statements** in five regions (status line rows 1-2, exporter, proxy hooks, hook main flow) | 3 unstated effects → BC-SL-027 amended, E-22, BC-PX-048 (+4 crash rows) |
| r7 | fresh re-execution of r6's three, plus a **class sweep** of r6's mechanism over every text-mode write in all six Python files | 3 of 3 confirmed; 11 write sites | 1 unstated trigger → H-09 (latent), under an existing contract (BC-HK-019) |
| r7 | pass-2 hand-off (P2r9 gap 3) | pass-through duration | BC-PX-049 (a mitmproxy-default behavior around legacy code already covered by BC-PX-002/013/014/037) |

Statement accounting (`region_stmts.py`, AST `stmt` nodes): the six Python files hold **1,809** statements (status line 742, proxy 500, exporter 316,
hook 146, backfill 86, preflight 19). The 903 read line by line in r6 are half of them. The regions r6 listed as not read statement by statement
(`get_sample`…`claude_window_start` `:158-362` 138, `render_subagent_rows`/`main_subagent` `:888-975` 42, `_mix_counts` `:999-1154` 116, proxy tap
and helpers `:339-456` 71, backfill 86; 453 together) are each pinned by **exhaustive** tables from r1-r4: BC-SL-091/093 (sample and rate-limit
sequences), BC-SL-094/095/098/099 (turn machine, D4-EX-2 table), BC-SL-097 (`--subagent`, OD-14), BC-PX-045 (tap theorem plus a 300-trial property
test and an executable reference model), and BC-BF-006..013. The trust CLI (`dgx_proxy.py:550-764`) is OOS (BC-PX-031, D13).

**Statement:** **No behavior-bearing code in `legacy/` is without a BC**, apart from the explicit out-of-scope set: the trust CLI (BC-PX-031, OOS,
replaced by `hylo ca`); the D6 visible-mode launcher branches (5 shell items, including the router port probe); the unwired coordinator (BC-CO-001/002,
OOS); decision-log **text** (BC-PX-022/029, OOS pending OD-40); `--subagent` (BC-SL-097, OD-14); the deploy plists (BC-SV-001/002, OOS); CP-C01..C10
(owner-ruled OOS); `ROLLBACK.md` (documentation). Every function, effect site and handler is cited by a BC or an OOS ruling (r5). Every unstated
effect found by reading (r5: 1, r6: 3, r7: 1) now has a contract or a catalogue row.

**Residual risk, stated plainly:** the 453 statements listed above were verified against exhaustive pinned tables, not re-read line by line for
side effects outside those tables. The only class of unstated effect that line-by-line reading has found (rounds 5-7) is "an exception class that
a guard does not catch, at a write". This round swept that class over every write site in all files. A further line-by-line reading of the 453 is
possible, but nothing points to an open gap there.

---

## 7. Target D: canonical index after r5-r7

Base: P3r4 §7.3 (227 rows), amended by P3r5 §6 (+2 → 229), P3r6 §6 (+2 → 231) and this round (+1 → **232**).

### 7.1 Totals

| Component | BCs | BX | JE | OOS | Approved deviation | Pending OD (primary) |
|---|---|---|---|---|---|---|
| Status line (SL) | 103 | 97 | 0 | 0 | 4 | 2 (OD-14, OD-30) |
| Proxy (PX) | 49 | 37 | 0 | 3 | 1 | 8 (OD-07, OD-16, OD-26, OD-28, OD-37 ×2, OD-41, OD-45) |
| Exporter (EX) | 27 | 0 | 16 | 1 | 0 | 10 (OD-11 ×2, OD-22, OD-23 ×2, OD-29 ×3, OD-33, OD-39) |
| Stop hook (HK) | 23 | 3 | 18 | 0 | 0 | 2 (OD-12 ×2) |
| Launcher (LN) | 11 | 0 | 8 | 2 | 1 | 0 |
| Coordinator (CO) | 2 | 0 | 0 | 2 | 0 | 0 |
| Preflight (PF) | 2 | 0 | 2 | 0 | 0 | 0 |
| Backfill (BF) | 13 | 0 | 0 | 0 | 0 | 13 (OD-36) |
| Services (SV) | 2 | 0 | 0 | 2 | 0 | 0 |
| **Total** | **232** | **137** | **44** | **10** | **6** | **35** |

- By phase: P1 103, P2 29, P3 48, P4 39, unscheduled 13 (= 232).
- By last round: B 79, r1 84, r2 24, r3 19, r4 11, r5 3, r6 10, **r7 2** (= 232).
- Crash catalogues: status line 43 (CP-N01/N02 now **latent**); proxy P-R1..R5, P-S1..S6, P-E1 (P-R5, P-S5, P-S6, P-E1 **latent**); exporter
  E-01..E-09, E-20..E-22 (E-22 **latent**); hook **H-01..H-09** (H-09 new, latent); backfill B-01..B-08.
- Owner items: OD-01..OD-43 and OD-45 (44 items; **OD-44 unused**). Ruled: OD-24, OD-27. **Pending 42.** New this round: none (the next number
  is OD-46).
- Retractions: pass-3 adds **CONV-ABS-22** (RET-15). 23-24 unused. Pass 2 holds 25-28. The next free number is 29.

### 7.2 Changed rows only (r7)

| ID | Change |
|---|---|
| **BC-PX-049** | **new** (§4): `Pass-through flows: no total-duration limit; 600 s inactivity cut only; no ledger trace` · `internal/proxy` · P3 · OD-37 · Also D13, D6, HY-PASS-1, HY-BIND-6 · H · r7 |
| BC-HK-019 | Last r1 → **r7**; flag "H-09: a lone surrogate in `session_id` (or a truthy string `stop_hook_active`) crashes `_log`, exit 1, no stdout, no log; latent; Go per OD-45 (CONV-ABS-22)" |
| BC-SL-027 | flag "r7: re-verified (AST + 12 cost values)" (Last stays r6) |
| BC-SL-073, BC-SL-074, BC-SL-075 | flag "latent in production: VictoriaMetrics returns absent series, not NaN (capture 2026-11-14, §5)" (Last unchanged) |
| BC-EX-021 | flag "E-22 latent (0 surrogate escapes in the ledger); trigger list refined (§1.1)" (Last stays r6) |
| BC-PX-024 | flag "P-E1 latent" (Last stays r6) |
| BC-PX-048 | Conf H unchanged; flags "all four rows re-pinned r7; P-S6 pinned by execution (was MEDIUM static); all four latent" (Last stays r6) |
| BC-PX-002 | flag "duration semantics of pass-through flows in BC-PX-049" |
| BC-PX-046 | flag "row 1 is the routed-lane case of BC-PX-049 contract 2" |
| BC-PX-001, BC-PX-026 | flag += "0 `bridge_ws_*` events in the ledger 2026-11-09..14 (P2r9; OD-43 premise confirmed)" |
| BC-PX-043 | flag += "V-1 text: add the h2 `:authority` case (PR-5)" |
| BC-PX-044 | flag += "V-2 text amended for h2 clients (PR-6)" |
| BC-LN-004 | flag += "ledger-corroborated: the 2 rerouted h2 requests are `dgx_request` lines with empty session/meta_user_id/project (P2r9)" |

---

## Owner checks (carried, optional)

1. Optional: the Grafana per-session panel with at least 2 recent sessions (BC-EX-025).
2. Optional: `promtool check metrics` offline on one saved scrape body.
3. ~~VictoriaMetrics NaN capture~~: **done** (§5). ~~Ledger surrogate count~~: **done** (§1.2).

## Delta Summary

- **Target A:** all three of r6's unstated effects **re-verified from scratch** with new scripts and fixtures. BC-SL-027's amendment holds (AST
  nesting plus 12 cost values). E-22 holds on 3.11.7 and 3.9.6, including an empty launchd-like environment. Its trigger list is refined: `session`
  only within `[:8]`; `anth_reply` is not a source; `?rebuild=1` and later appends do not recover. BC-PX-048 holds in both locale modes on all four
  rows, and **P-S6 is now pinned by execution** through `responseheaders` → `_SSETap.feed` → `response`. All five rows (E-22, P-E1, P-S5, P-S6, P-R5)
  are **latent** per the ledger evidence.
- **Class sweep (new):** r6's mechanism checked at all 11 text-write sites. One more trigger: **H-09** (hook `_log` renders `session_id` with
  `str()`), latent, under BC-HK-019's existing contract. **CONV-ABS-22** retracts r6's "hook: no unstated effect".
- **Target B:** 10 statements checked. One rests on the retracted fact and was not amended (PR-6, V-2); two need "Claude Code" wording (PR-3, PR-5);
  the bridge statements are code-accurate and already flagged. No BC contract text changes.
- **Pass-2 hand-off:** **BC-PX-049** (pass-through duration: no total limit, 600 s inactivity only, no ledger trace, HY-PASS-1 as a D13/D6-linked
  requirement).
- **VictoriaMetrics capture:** recorded. CP-N01/N02 are latent. The last required owner capture is closed.
- **Target C:** no behavior-bearing code without a BC outside the explicit out-of-scope set. The residual risk is stated.
- **Counts:** new BCs 1 (BC-PX-049, carried). Re-dated 1 (BC-HK-019). Flag-only 14. Index 232. Crash rows +1 (H-09). Retractions 1 (CONV-ABS-22). New
  ODs 0.

## Remaining Gaps (verbatim-carryable)

1. Optional owner checks: the Grafana per-session panel with at least 2 sessions; `promtool check metrics` offline on a saved scrape.
2. P3 replay verification items, stub-backend rig only: V-1 (Host header bytes, **plus one h2 `:authority` case**), V-2 (mitmproxy 502 bytes on
   connect failure and `server closed connection`, **h1 and h2 variants**), V-3 optional confirmation. One rig case per BC-PX-048 row is optional now
   that all four are pinned in isolation and latent.
3. Owner decisions: 42 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-43, OD-45). Suggest that OD-45's ruling covers both diagnostic logs (proxy
   decision log and hook log, H-09). OD-37's ruling also settles BC-PX-049's inactivity rule.
4. Apply the PR-3/PR-5/PR-6 wording fixes when the Phase-1 spec copies V-1/V-2 and BC-PX-044 (no contract changes).
5. Not determinable from authorized sources (LOW, no spec impact): how Claude Code encodes non-ASCII custom header values (now moot for parity,
   since all dependent rows are latent); whether Claude Code can report `total_cost_usd` ≤ 0 while the transcript holds tokens (BC-SL-027
   reachability); which duplicate session sample VictoriaMetrics keeps (BC-EX-025).

## Novelty Assessment

Novelty: NITPICK — findings are refinements, not gaps.

What this round did: it re-verified r6's three unstated effects from scratch (all confirmed, none retracted), pinned P-S6 by execution, recorded the
ledger and VictoriaMetrics evidence that makes E-22, the four P-rows and CP-N01/N02 latent, found that propagation needs only wording fixes (one
unamended V-2 sentence, two "the client" → "Claude Code" edits), and found no uncovered code. By the orchestrator's stated criterion, that is a
NITPICK round.

Two items need an honest justification:

- **BC-PX-049** is a new index row, but it carries a pass-2 entity (P2r8 HY-PASS-1, the pass-through stream class) into the BC catalogue. It
  describes mitmproxy defaults around addon code already covered by BC-PX-002/013/014/037, and its Go rule is governed by the existing OD-37 and D13.
  Rounds 4-6 classified their carried rows (BC-EX-026, BC-PX-046, BC-PX-047) as refinements, and this round follows that precedent. The orchestrator
  asked for this BC as gap-filling. It fills a **catalogue** gap, not a gap in the model.
- **H-09 / CONV-ABS-22** is an unstated trigger inside a region that r6 called clean. It is a new **trigger** for an outcome BC-HK-019 already states
  (exit 1, no stdout), produced by a mechanism already in the model (BC-PX-048), unreachable with Claude Code's input types, and its Go treatment fits
  inside OD-45 with no new decision. Removing it would not change how the hook is specified, only one catalogue row. If the orchestrator counts any
  retraction as SUBSTANTIVE, this is the one item that would make the round so. I judge it a refinement and say so here rather than hide it.

Fewer than three substantive items were found (by the judgment above, none). Per the honest-convergence rule, pass 3 is declared converged.

## Convergence Declaration

Pass 3 has converged — findings are nitpicks, not gaps.

## State Checkpoint

```yaml
pass: 3
round: 7
status: complete
files_scanned: dgx_statusline.py (:436-470, :560-640, :1155-1245; AST of render_lane), dgx_ledger_exporter.py (all; exec'd as text copy, handler in memory), dgx_proxy.py (:40-522; :1-549 exec'd as text copy), auto_continue.py (:190-275; exec'd as text copy), statement counts for all 6 .py files; pass-3 B, r1-r6 (grep + context), r4-r6 in full; pass-2 r2 §6, r4 §1.3, r8, r9; mitmproxy 12.3.1 http, addonmanager, options, proxy/server, proxy/layers/websocket (citations only)
timestamp: 2026-11-14T07:49:49Z
novelty: NITPICK
reverified: {BC-SL-027_amendment: confirmed, E-22: confirmed (trigger list refined; 3.11.7, 3.9.6, 3.9.6 empty env), BC-PX-048: confirmed (P-E1, P-S5, P-S6 pinned by execution, P-R5; both locale modes)}
reachability: {E-22: latent, P-E1: latent, P-S5: latent, P-S6: latent, P-R5: latent, CP-N01: latent, CP-N02: latent, H-09: latent}
new_bcs: {PX: 1 (BC-PX-049, carried from P2r8/P2r9)}
redated_bcs: [BC-HK-019]
crash_rows_added: [H-09]
retractions: [CONV-ABS-22 (P3r6 §1.5 'hook: no unstated effect')]
propagation: {checked: 10, unamended_resting_on_retracted_fact: 1 (PR-6 V-2), wording_fixes: 2 (PR-3, PR-5), bc_text_changes: 0}
completeness: {diff_items_r5: 283, statements_reread_r6: 903, python_statements_total: 1809, write_sites_swept_r7: 11, uncovered_behavior_bearing_code: 0 (excl. OOS set)}
bc_index_total: 232
bc_index_by_parity: {BX: 137, JE: 44, OOS: 10, approved_deviation: 6, pending_OD: 35}
owner_decisions: 44 (OD-01..OD-43, OD-45; 42 pending, 2 ruled; OD-44 unused; next new OD-46)
owner_captures: {vm_nan: done (19 series finite; absent-not-NaN when idle), ledger_surrogates: done (0)}
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r7/
next: pass 3 converged; carry Remaining Gaps to Phase 1 / the final synthesis
```
