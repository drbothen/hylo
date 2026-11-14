# Pass 4 Deepening — Round 5: HTTP/2 re-classification, re-verification of CONV-ABS-81/82 — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/`, read-only and static. Nothing in `legacy/` was imported, executed or modified. No proxy, nothing
  networked, no socket binds, no DNS lookups. CLAUDE.local.md was not read. No git commit.
- Authorized read-only references: mitmproxy 12.3.1 (`m/` = `$PROTOTYPE/.mitmenv/lib/python3.12/site-packages/mitmproxy/`).
  As in round 4, the adjacent libraries on the same venv path (`h2/` 4.4.1, `hpack/`) were read only to confirm what mitmproxy relies on. Local man
  pages `termios(4)`, `_exit(2)`, `intro(2)`, `zshoptions(1)`, `zshmisc(1)`, freshly dumped this round. Round-4 scratch outputs (`p4r4/out/inscope.tsv`,
  `classified.tsv`, `classify.out`) were re-read, not re-generated.
- Scratch: `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r5/` holds fresh man-page text dumps
  (`termios.txt`, `exit2.txt`, `intro2.txt`, `zshoptions.txt`, `zshmisc.txt`).
- Inputs read: pass-4 deep r4 (complete), r3 (§C catalogue, §C.5 totals, §C.6 OD-57, §E NFRs), and r1/r2 (grep for HTTP/2 statements, §A.3). Pass-2 deep
  r8 (§0, §1.1, §3.2, §5 B-2, CONV-ABS-25) and r9 (§1 A4/A4a, §2.2) for the production HTTP/2 facts. Pass-2 r7 (HY-PROTO-1 wording). Pass-5 deep r3
  **exists** and was read, not edited. It has no HTTP/2 statement that this round changes (its only HTTP/2 mention is GP-2 `GODEBUG`, l.220).
  Pass-1 r3 C2a and the `http2` option row (l.64, l.126) already say "Claude Code h1, some children h2", so they agree with this round.
- Numbering: retractions **CONV-ABS-85, 86, 87** (88 unused). New owner item **OD-94** (OD-95..OD-97 unused). New threshold rows **T-140..T-147**.
  Sibling files were not edited.

Abbreviations, rationale codes and D15 classes as in r3 §C.1 (`PX`, `L`; **C** convention or tool default; CFG, NC, DROP, OOS, EXT, NEW-H, N/A).
Production counts quoted from pass-2 (P2r8 / P2r9) were not re-counted this round, because the logs are not an authorized source here.

---

## A. Target A: re-classifying the HTTP/2 sites

### A.1 The production fact that changes (from P2r8 §3.2, re-verified in P2r9 §1)

- About **7,566 HTTP/2 flows in 25 logs** (7,575 at P2r9's later read), from child tools that trust the CA: `api.github.com` 4,165, `github.com`
  3,274, `analytics.brew.sh` 51, `ghcr.io` 36, and others.
- **2 h2 `POST /v1/messages`** from a non-Claude-Code client were rewritten to the DGX. Each went to the plain-HTTP backend over HTTP/1.1, and both
  were written to the ledger as `dgx_request` with empty `session`/`project` (P2r9 §2.2).
- Claude Code's own traffic is HTTP/1.1: its MCP client offers `alpn=http/1.1`, and no other `api.anthropic.com` flow is h2.
- Round 4 classified the h2 sites as "not live (0 ` HTTP/2.0` lines in 38 logs)". That basis was retracted as CONV-ABS-25. The sites are live in
  legacy for child traffic. CONV-ABS-85 (§A.4) records this.

### A.2 How h2 is reached in legacy (fresh source reads)

1. **ALPN mirroring.** With `http2` True (`m/options.py:131-136`), the upstream offer is the client's own offer (`m/addons/tlsconfig.py:322-328`).
   The eager upstream handshake runs first, and `alpn_select_callback` then gives the client the protocol the server picked
   (`m/addons/tlsconfig.py:108-123`). So an h2 client connection always has an h2 upstream connection, at least the eager one to the CONNECT target.
2. **Layer selection.** h2 on the client leg starts `Http2Server` (`m/proxy/layers/http/__init__.py:956-957`). h2 on the upstream leg starts
   `Http2Client`, either for a flow (`:1204-1205`) or as soon as the upstream sends data, which h2 servers do at once with their SETTINGS frame
   (`:1000-1012`, comment at `:1002`). Both classes are subclasses of `Http2Connection` (`m/proxy/layers/http/_http2.py:65`) and build a
   `BufferedH2Connection` (`:92`). The `_http_h2.py` settings therefore apply to **both legs**.
3. **h2 to h1 (the 2 rerouted flows).** When the client is h2 and the chosen upstream is not, mitmproxy never reuses a connection: it opens a
   **new upstream connection per flow** (`m/proxy/layers/http/__init__.py:1087-1091` on reuse, `:1178-1188` for queued requests; the comment cites
   "read-until-EOF semantics"). That matches P2r8's "each on its own short connection".
4. **Errors are connection-wide.** Any `h2.exceptions.ProtocolError`, including `TooManyStreamsError`, `FrameTooLargeError` and
   `DenialOfServiceError` for an oversized header block, is turned into a GOAWAY `PROTOCOL_ERROR`. Every open stream on that connection then fails
   (`m/proxy/layers/http/_http2.py:194-207, 275-277, 314-333`; `h2/exceptions.py:27,47,182`; `h2/connection.py:2104-2111`).

### A.3 Per-site T-rows (replacing round 4's single folded T-124)

Legend for "hylo disposition": **D14** means that under D14 child processes no longer use the proxy, so this legacy effect goes away. **OD-94 (a)**
is the recommendation: hylo's listener negotiates HTTP/1.1 only, so these rows are N/A by construction. **OD-94 (b)** means hylo accepts h2 when
a client offers it (full ALPN parity, HY-PROTO-1), and each row then needs the named constant or key shown.

| T | Value | mitmproxy site | Effect on legacy h2 child traffic | hylo disposition |
|---|---|---|---|---|
| **124** (rewritten) | 58 s h2 PING keep-alive on **upstream** h2 connections (`Http2Client` only) | `m/options.py:137-146`; `m/proxy/layers/http/_http2.py:539-567` | Keeps idle upstream h2 connections (GitHub, brew, ghcr; the eager `api.anthropic.com` leg of the 2 rerouted flows) alive with a PING every ≤ 58 s. **New interaction (§A.5):** each ping timer event resets the client connection's 600 s inactivity watchdog, so **an h2 client connection is never idle-cut while its upstream is open** | D14 removes it. (a): N/A. (b): CFG `proxy.http2.ping_keepalive_s` = 58 (a timeout, so D15 makes it config), and the idle timer must count bytes rather than timer events (OD-94) |
| **140** | local `SETTINGS_INITIAL_WINDOW_SIZE` 2³¹ − 1 (per stream) | `m/proxy/layers/http/_http_h2.py:53,57` | The proxy advertises the maximum window to both peers, so a sender is never throttled by the proxy. Received data is acknowledged as soon as it is parsed, whether or not it has been forwarded (`_http2.py:238-240`), so **there is no end-to-end flow control through the proxy on h2** (CONV-ABS-87) | D14. (a): N/A. (b): NC (protocol parameter), with a bounded per-stream send buffer as a hylo deviation (OD-94, D16-style bound) |
| **141** | connection window raised to 2³¹ − 1 | `m/proxy/layers/http/_http_h2.py:61-67` | Same as T-140 at connection level: a GitHub or brew download is never paced by the proxy | D14. (a): N/A. (b): NC |
| **142** | local `SETTINGS_MAX_FRAME_SIZE` and inbound frame cap 2¹⁷ = 131,072 B (h2 library default inbound cap would be 2²⁴) | `m/proxy/layers/http/_http_h2.py:54-55`; `h2/connection.py:311` (default not used) | A peer frame over 128 KiB kills the whole connection (`FrameTooLargeError` → GOAWAY). Compliant peers respect the advertised setting, and no such failure is recorded | D14. (a): N/A. (b): NC |
| **143** | 10 provisional concurrent upstream streams until the server's first SETTINGS, then the server's `MAX_CONCURRENT_STREAMS` | `m/proxy/layers/http/_http2.py:487-490, 511-518, 529-537, 631-634` | Child streams above the cap wait in an **unbounded FIFO** (`stream_queue`). It binds only during the first round trip of a new upstream h2 connection, which is normally already past because of the eager connect | D14. (a): N/A. (b): NC |
| **144** | server push disabled (`SETTINGS_ENABLE_PUSH` = 0) on the upstream leg | `m/proxy/layers/http/_http2.py:496-500`; push promises still received are logged as errors (`:297-300`) | Upstreams never push to children through the proxy | D14. (a): N/A. (b): NC (protocol choice) |
| **145** | local `SETTINGS_MAX_CONCURRENT_STREAMS` 100 (h2 library default, not overridden) | `h2/connection.py:344-362`; enforced at `:1599-1606` | Limits a child client (for example `gh`) to 100 concurrent streams per connection to the proxy. A 101st stream kills the connection (`TooManyStreamsError` → GOAWAY, §A.2 item 4). No such failure is recorded | D14. (a): N/A. (b): NC |
| **146** | max decoded header list 65,536 B (`SETTINGS_MAX_HEADER_LIST_SIZE`, h2/hpack default) | `h2/connection.py:319-320, 335, 359-360, 1999-2001`; `hpack/hpack.py:34, 499, 543-546`; `h2/connection.py:2104-2111` | A header block over 64 KiB, counted as name + value + 32 per entry, kills the h2 connection. **Asymmetry with T-139:** h1 heads have **no** limit. Not observable for the recorded children | D14. (a): N/A (and T-139's finite Go head limit applies). (b): NC, with a comment on the h1/h2 asymmetry |
| **147** | closed-stream memory 65,536 entries | `h2/connection.py:322-323, 395-396, 2033-2034` | Bookkeeping only: frames for streams older than the last 65,536 closed ones are treated as unknown. Behavior-neutral at child volumes | D14. (a): N/A. (b): NC (library internal) |

**Other sites round 4 dismissed or understated on the "no HTTP/2" basis:**

| T | Correction | Evidence | hylo disposition |
|---|---|---|---|
| **137** | **Reachable in legacy.** An h2 client whose flows are rewritten to an h1 upstream (the DGX) gets one upstream connection per flow (§A.2 item 3). Each connection holds one of the 5 permits per address for its **whole life** (r4 §A.1 row 2). So a 6th concurrent rewritten stream from one h2 client connection **waits**, and keeps waiting until the backend closes an idle keep-alive. That backend timing was not verified. Observed: 2 such flows, never concurrent, so the limit never bound. h2 → h2 flows multiplex onto one upstream connection and meet T-143 instead | `m/proxy/server.py:105-109, 206, 259-260`; `m/proxy/layers/http/__init__.py:1087-1091, 1178-1188` | N/A unchanged (Go transport; D14 removes the h2 child clients). Recorded so the parity harness does not expect queueing |
| **122** | Not a fixed 600 s cut for h2 client connections (§A.5) | `m/proxy/server.py:64-76, 267-272, 387, 402-410`; `_http2.py:558-567` | `proxy.idle_timeout_s` (OD-37) unchanged for Claude Code (h1). Note for OD-94 (b) |
| **139** | Adds the asymmetry: h1 has no head limit, h2 has a 64 KiB header-list cap (T-146) | as T-146 | unchanged |
| P-3 (r4 §D) | The r4 bound "about 64 KiB written + 128 KiB read per connection" holds only for **h1 client legs**. That covers all Claude Code traffic. It does not hold on h2 client legs (CONV-ABS-87) | §A.6 | NFR text corrected (§D) |
| `dumper.py:184-193` (r4 §B.3) | Wording: the ` HTTP/2.0` suffix "that P2r5 counted" → "that P2r8/P2r9 counted (7,566)". The suffix is also printed when request and response versions differ (`:185-191`), which is why the 2 h2 → h1 rerouted flows show it | `m/addons/dumper.py:177-193` | — |

### A.4 Every pass-4 statement resting on "no HTTP/2 in production" (grep of r1-r4)

| File:line | Statement | Status |
|---|---|---|
| deep r1 l.123 (T-124) | "active only for child-tool h2 flows (7,566, CONV-ABS-25); Claude Code is h1" | **already correct** (r1 was written after P2r8) |
| deep r1 l.306; r3 l.65, l.221 | "HY-PROTO-1 keeps h1↔h1" | **wording**: HY-PROTO-1 (P2r7 l.136, l.233) says that the upstream leg **mirrors the client's version**. It is h1 ↔ h1 **for Claude Code**, not by rule |
| deep r2 l.97; r3 l.215 | "58 s h2 ping … confirmed / NC" | neutral (no liveness claim) |
| deep r4 l.16-17 | cross-checked against "P2r4/P2r5 (h2 not live: 0 ` HTTP/2.0` lines in 38 logs)" | **retracted** (CONV-ABS-85) |
| deep r4 l.89, l.105, l.134-135 | "HTTP/2-only 5 … not live in production"; "h2-only and not live (5)" | **retracted**: live for child traffic; the sites are re-rowed in §A.3 |
| deep r4 l.110, l.149 | T-124 "h2 not live (P2r5)"; "NC, only if hylo speaks h2 upstream (HY-PROTO-1 excludes it)" | **retracted**: HY-PROTO-1 does not exclude h2, it mirrors the client. Whether hylo ever speaks h2 is OD-94 |
| deep r4 l.103 | ` HTTP/2.0` suffix "that P2r5 counted" | wording (§A.3) |
| deep r4 l.179 (P-3) | bound per connection, stated without a protocol qualifier | **retracted in part** (CONV-ABS-87) |
| deep r4 l.222-223 (Novelty) | "on the h2 path (which is not live)" | **retracted** (CONV-ABS-85); the r4 NITPICK verdict rested on it |
| deep r4 l.241 (checkpoint) | `operative_h2_only: 5` under a "not live" reading | label kept; reading corrected |
| pass-4 broad catalogue | no HTTP/2 statement | — |

### A.5 New interaction: the h2 ping defeats the 600 s inactivity watchdog (T-122 × T-124)

- **The watchdog** is one `TimeoutWatchdog` per client connection (`m/proxy/server.py:116-120`). It fires only if `last_activity + timeout <
  now` (`:72`). `server_event` calls `register_activity()` for **every** event it handles (`:387`).
- **The ping timer is an event.** `Http2Client` asks for a wakeup at Start (`_http2.py:566-567`) and again after **every** wakeup (`:558-561`),
  whether or not it sent a PING. The server delivers each one through `server_event(events.Wakeup(...))` (`m/proxy/server.py:267-272`, scheduled
  at `:402-410`). The PING's ACK from the upstream also arrives as `DataReceived`.
- **Consequence.** While an upstream h2 connection is open, the client connection registers activity at least every 58 s, so the 600 s cut
  **cannot fire**. The cycle stops only when the upstream h2 connection closes (`close_connection` → `self.done`, which swallows `Wakeup` without
  asking again, `_http2.py:324-336`), or when either peer closes.
- **Scope.** Because ALPN is mirrored after an eager connect (§A.2 item 1), every h2 client connection in legacy has an h2 upstream with an
  `Http2Client`. In legacy, therefore, the inactivity cut applies **only to h1 and no-ALPN client connections**.
- **Production consistency (not proof):** P2r8 §1.1 records 57 inactivity closes, split 56 `tls` (no ALPN) + 1 `alpn=http/1.1`. That is **0 on h2
  client connections** across 7,566 h2 flows in 25 logs. This round did not read the logs.
- **hylo:** no effect on Claude Code (h1). If hylo ever serves h2 (OD-94 (b)), the idle timer must be driven by bytes moved, not by internal timer
  events. Otherwise the D15 key `proxy.idle_timeout_s` silently stops meaning anything for h2.

### A.6 New qualification: no end-to-end h2 backpressure (corrects r4 P-3)

- `BufferedH2Connection.send_data` queues anything that exceeds the receiving peer's window in a per-stream `collections.deque` that has **no size
  bound** (`m/proxy/layers/http/_http_h2.py:48, 58, 92-105`). Queued data is not on the transport, so r4's `drain_writers()` backpressure
  (`m/proxy/server.py:297, 330-339`) does not engage.
- On the receiving side, mitmproxy acknowledges every DATA frame as soon as it is parsed (`_http2.py:238-240`), with windows of 2³¹ − 1 (T-140,
  T-141). Its sender therefore keeps sending.
- **Effect:** for a **streamed** flow with an h2 client leg, proxy memory per stream is bounded only by the sender (in principle up to about 2 GiB
  per stream window), not by about 192 KiB. In legacy, only SSE responses and non-JSON `/v1/messages` replies are streamed (`PX:193-208`). The child
  h2 traffic on record is GitHub, brew and registry JSON or blobs (buffered whole, T-127) plus the 2 rerouted non-streaming JSON replies. So this
  case was **reachable but not observed**. Buffered flows already hold the whole body (T-127).

### A.7 OD-94 (new owner item)

| OD | Question | Options | Recommendation |
|---|---|---|---|
| **OD-94** | **hylo listener HTTP/2 posture.** Legacy accepts h2 from any client that offers it (ALPN mirroring). Under D14, the only client is Claude Code, which offers `http/1.1` (P2r8). Should hylo's listener (a) negotiate **HTTP/1.1 only**, or (b) mirror h2 as legacy does? | **(a)** Offer only `http/1.1` on the listener. A client that offers `h2,http/1.1` falls back to h1. A client that offers only `h2` fails the handshake (`no_application_protocol`). T-124 and T-140..T-147 become N/A, and T-122 keeps one meaning. This deviates from legacy only for h2-offering clients, and D14 removes them all. **(b)** Full parity: accept and mirror h2. T-124 becomes CFG `proxy.http2.ping_keepalive_s`; T-140..T-147 become NC with comments; the idle timer counts bytes, not timers (§A.5); and the per-stream h2 send buffer gets a bound (a hylo deviation, §A.6) | **(a)**, recorded as an approved deviation that Claude Code cannot see, with a `hylo doctor` or log warning if a client ever offers `h2`. It keeps HY-PROTO-1 trivially satisfied (h1 ↔ h1), removes 9 rows of h2 tuning from the parity surface, and avoids the T-122 × T-124 and unbounded-buffer behaviors. Revisit if a future Claude Code build offers `h2`. **Not verified (Go stdlib is not an authorized source this round):** Go's `net/http` server and transport negotiate h2 automatically in common configurations. Either option therefore needs explicit listener and transport protocol settings in `internal/proxy`, and a test that asserts the negotiated ALPN on both legs |

---

## B. Target B: re-verification of CONV-ABS-81 and CONV-ABS-82

### B.1 CONV-ABS-81 (T-136 leaf cache): **partly confirmed, partly retracted (CONV-ABS-86)**

| Sub-claim | Fresh evidence | Verdict |
|---|---|---|
| Hosts are not cache keys; the key is `(CN, SANs)` | `m/certs.py:788-798`: candidate keys are the asterisk forms of the CN and each SAN, then `"*"`, then `(commonname, sans)`. A miss stores **only** under `(commonname, sans)` (`:815`). In the mint path, `get_cert` never stores the string forms. `cn` = the first altname (`m/addons/tlsconfig.py:679`) | **confirmed** |
| The SANs include the client SNI | `tlsconfig.py:665-668` (SNI, or the proxy's own socket IP if there is no SNI) | **confirmed** |
| The SANs include "the **upstream address**", so "one host reached at several **resolved IPs** produces several keys" | `tlsconfig.py:671-672` appends `conn_context.server.address[0]`. In regular mode, `server.address` is set from the CONNECT request: `(self.flow.request.host, self.flow.request.port)` (`m/proxy/layers/http/__init__.py:779`), which is the **authority the client wrote**, normally a host name. `asyncio.open_connection(*address)` resolves it (`m/proxy/server.py:212-215`), and the resolved IP goes only to `peername` (`:241`). The authority SAN usually equals the SNI and is removed as a duplicate (`tlsconfig.py:674-675`) | **retracted (CONV-ABS-86)**. Resolved IPs never enter the key. Several keys per host arise from: different upstream certificates for the same host (the CN, SAN list and organization come from the upstream leaf, `:644-650`), a client without SNI, or a CONNECT authority that is an IP literal |
| Eviction is by insertion order; hits do not refresh | `certs.py:576-580` (append, then `pop(0)` past `STORE_CAP = 100` at `:541`, then drop every key that maps to the evicted entry); a hit (`:798-800`) does not call `expire` | **confirmed** |
| The cost of eviction is CPU only | A re-mint calls `dummy_cert(self.default_privatekey, …)` with `builder.public_key(cacert.public_key())` (`certs.py:427, 803-811`). No key is generated, only a SHA-256 re-signature. The new leaf differs only in serial and validity dates | **confirmed** |
| No expiry re-check on a hit | `certs.py:798-800` returns the cached entry without reading `not_valid_after` | **confirmed** |

### B.2 CONV-ABS-82 (R-12 SIGHUP delivery documented): **confirmed, with one precision**

| Link | Fresh evidence (p4r5 dumps) | Verdict |
|---|---|---|
| Hangup → SIGHUP to the controlling process | `termios(4)` "Modem Disconnect" (dump l.380-386): "the SIGHUP signal is sent to the controlling process associated with the terminal. Unless other arrangements have been made, this causes the controlling process to terminate." `intro(2)` (l.417-419): "A session leader with a controlling terminal is a controlling process." | **confirmed**. **Precision:** `termios(4)` states this for a detected modem disconnect when CLOCAL is clear. That closing a terminal window counts as such a hangup on its pseudo-terminal is **not stated** in the authorized pages, and remains the single assumption (r4 already named the "standard terminal-emulator setup") |
| The controlling process's exit → SIGHUP to the foreground process group | `_exit(2)` (l.36-38): "If the process is a controlling process …, the SIGHUP signal is sent to the foreground process group of the controlling terminal." | **confirmed** |
| zsh sends HUP to its running jobs on exit | `zshoptions(1)` `HUP <Z>` (l.909-910): "Send the HUP signal to running jobs when the shell exits." `zshmisc(1)` JOBS (l.1390-1395). **Precision:** the JOBS sentence is in the context of exiting with jobs still running after a warning. `zshoptions(1)` HUP is the general statement | **confirmed** |
| mitmdump stays in the launcher's (foreground) process group | `L:1` `#!/bin/zsh` (non-interactive); `zshoptions(1)` `MONITOR` (l.915-916): "Set by default in interactive shells"; `L:75` `… mitmdump … &` | **confirmed** |
| SIGHUP keeps its default action in mitmdump | `zshmisc(1)` SIGNALS (l.1401-1405): only INT and QUIT are ignored for `&` commands without MONITOR. A recursive count of `SIGHUP` in `m/` gives 0 files. `m/tools/main.py:128-129, 132-133, 137-138` handle SIGINT, SIGTERM and SIGPIPE only. `L:97` traps EXIT INT TERM, not HUP | **confirmed** |

CONV-ABS-82 stands: SIGHUP delivery is **HIGH (documented, not exercised)**, with the one assumption stated. Neither precision changes R-12 or its
hylo implication.

### B.3 Retractions this round

| Marker | Claim | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-85** | pass-4 r4: the 5 h2 operative sites (plus `enable_push` and the h2 library defaults) are "not live in production", folded into T-124 with the key "only if hylo speaks h2 upstream (HY-PROTO-1 excludes it)"; r4's NITPICK verdict cited this | h2 is live in legacy for child tools (about 7,566 flows) and for 2 rerouted `/v1/messages` (P2r8 CONV-ABS-25, P2r9 A4/A4a). HY-PROTO-1 mirrors the client's version; it does not exclude h2. The sites now have their own rows T-124, T-140..T-147 (§A.3), and hylo's h2 exposure is OD-94 | §A.1-§A.4 |
| **CONV-ABS-86** | pass-4 r4 §A.1 row 1 (b) and CONV-ABS-81: the T-136 key includes "the upstream address", so "one host reached at several resolved IPs produces several keys"; r4 C.1 T-136 "key = (CN, SANs incl. SNI and upstream IP)" | The appended SAN is the CONNECT authority (`http/__init__.py:779`), not the resolved IP (`server.py:241`), and it is usually removed as a duplicate of the SNI. CONV-ABS-81's other parts stand (§B.1) | §B.1 |
| **CONV-ABS-87** | pass-4 r4 §D P-3: "a streamed flow's proxy memory is bounded at about 64 KiB written plus about 128 KiB read per connection" | True only for h1 client legs (all Claude Code traffic). On an h2 client leg, unsendable data is queued in an unbounded per-stream deque and the sender is never throttled (windows 2³¹ − 1, immediate acknowledgement) | §A.6 |

---

## C. Catalogue update (delta to r4 §C, which is a delta to r3 §C)

### C.1 Changed and new rows

| T | Value (op) | Site | Class | Rat. | Rationale | Key / NC reason | Last |
|---|---|---|---|---|---|---|---|
| 122 | 600 s inactivity; **reset by every event, including h2 ping wakeups, so it never fires on an h2 client connection while its upstream is open** | m/options.py:240-247; m/proxy/server.py:64-76,116-120,267-272,344-354,387,402-410; m/proxy/mode_servers.py:70 | CFG | C | tool default; fired 57 times in production, 0 on h2 client connections (P2r8 §1.1) | `proxy.idle_timeout_s` (OD-37); under OD-94 (b), activity = bytes moved | **R5** |
| 124 | 58 s h2 PING on upstream h2 connections | m/options.py:137-146; m/proxy/layers/http/_http2.py:539-567 | NC | C | tool default; **live for child h2 traffic** (CONV-ABS-85) | OD-94 (a): N/A. (b): CFG `proxy.http2.ping_keepalive_s` | **R5** |
| 136 | 100 leaves, FIFO by insertion (hits do not refresh), key = (CN, SANs = upstream leaf CN/SANs + SNI or local IP + CONNECT authority, deduplicated), no expiry re-check | m/certs.py:541,576-580,788-818; m/addons/tlsconfig.py:634-682; m/proxy/layers/http/__init__.py:779 | NC | C | tool default; eviction only re-signs (CPU) | NC in `internal/ca`; re-mint before `not_after` for a long-lived proxy (OD-50) | **R5** |
| 137 | 5 open upstream connections per address per client connection (permit held for the connection's life); **reachable for h2 → h1 rewritten flows (one connection per flow)** | m/proxy/server.py:105-109,206-262; m/proxy/layers/http/__init__.py:1087-1091,1178-1188 | N/A | C | tool default; never bound (2 rewritten h2 flows, not concurrent) | N/A: Go transport limits; D14 removes h2 children | **R5** |
| 139 | no HTTP/1 head size limit; **h2 has a 64 KiB header-list cap (T-146)** | m/proxy/layers/http/_http1.py:9,58,285,408; h11/_connection.py:69,485 (unused) | NC | N/A | absent limit | as r4, plus an asymmetry comment | **R5** |
| **140** | h2 local initial stream window 2³¹ − 1 | m/proxy/layers/http/_http_h2.py:53,57 | NC | C | tool setting; live for children; no proxy pacing | OD-94 (a): N/A; (b): NC | **R5** |
| **141** | h2 connection window 2³¹ − 1 | m/proxy/layers/http/_http_h2.py:61-67 | NC | C | tool setting; live for children | as T-140 | **R5** |
| **142** | h2 max frame size 2¹⁷ B (advertised and enforced inbound) | m/proxy/layers/http/_http_h2.py:54-55 | NC | C | tool setting; an oversize frame kills the connection | as T-140 | **R5** |
| **143** | 10 provisional upstream h2 streams before the server's SETTINGS; excess queued unbounded FIFO | m/proxy/layers/http/_http2.py:487-490,511-537,631-634 | NC | C | tool setting; normally inert (eager connect) | as T-140 | **R5** |
| **144** | upstream h2 push disabled (`ENABLE_PUSH` = 0) | m/proxy/layers/http/_http2.py:496-500,297-300 | NC | C | tool choice | as T-140 | **R5** |
| **145** | h2 local `MAX_CONCURRENT_STREAMS` 100 (client leg) | h2/connection.py:344-362,1599-1606 | NC | C | library default; the 101st stream kills the connection | as T-140 | **R5** |
| **146** | h2 max decoded header list 65,536 B | h2/connection.py:319-320,335,359-360,1999-2001,2104-2111; hpack/hpack.py:34,499,543-546 | NC | C | library default; asymmetric with T-139 | as T-140 | **R5** |
| **147** | h2 closed-stream memory 65,536 | h2/connection.py:322-323,395-396,2033-2034 | NC | C | library internal; behavior-neutral | as T-140 | **R5** |

### C.2 Totals (changed)

| Measure | r4 | **r5** |
|---|---|---|
| Thresholds | 139 | **147** (broad 105 + r1 30 + r3 3 + r4 1 + r5 8) |
| By class | CFG 96 · NC 29 · DROP 7 · OOS 2 · EXT 2 · NEW-H 2 · N/A 1 | **CFG 96 · NC 37 · DROP 7 · OOS 2 · EXT 2 · NEW-H 2 · N/A 1** |
| By rationale | OWNER 27 · Dv† 18 · N/A 8 · EXT 2 · resolved 84 | **OWNER 27 · Dv† 18 · N/A 8 · EXT 2 · resolved 92** |
| Rationale resolved | 112 of 139 | **120 of 147** (102 final + 18 awaiting one bulk "yes") |
| Owner must supply | 27 in 7 groups | 27 in 7 groups (unchanged) |
| Last changed in R5 | — | 13 rows: T-122, T-124, T-136, T-137, T-139, T-140..T-147 |

If the owner rules OD-94 (a), T-124 and T-140..T-147 move from NC to N/A (NC 28 · N/A 10). If the owner rules (b), T-124 moves to CFG (CFG 97 · NC 36).
No rationale status changes either way.

### C.3 OD-57 lists

**Unchanged.** Bulk confirmation: the same 18 Dv† rows. Owner supplies a rationale: the same 27 rows in groups A–G (r3 §C.6). The new rows carry
rationale **C** (tool or library default), which is resolved.

---

## D. NFR catalogue changes (delta to r4 §D / r3 §E)

| NFR | Change | Evidence |
|---|---|---|
| P-3 Streaming latency (corrected) | The r4 bound of about 64 KiB written + 128 KiB read applies to **h1 client legs** (all Claude Code traffic). On **h2 client legs** there is no end-to-end backpressure: an unbounded per-stream send queue, windows 2³¹ − 1, immediate acknowledgement. Reachable in legacy for streamed child h2 flows; not observed | §A.6; CONV-ABS-87; T-140, T-141 |
| P-4 Long routed responses (refined) | "proxy idle cut 600 s … reset by any event" now includes the h2 ping timer, so **h2 client connections are never idle-cut while their upstream is open** | §A.5; T-122, T-124 |
| P-7 mitmproxy internal caps (refined) | T-136's key is (upstream leaf CN/SANs + SNI + CONNECT authority), with **no resolved IP**. T-137 is reachable for h2 → h1 rewritten flows. The h2 caps (T-142, T-145, T-146) are **connection-fatal** when exceeded | §B.1; §A.2 item 4; §A.3 |
| D14 evidence (note, no NFR ID) | The child h2 traffic that these rows govern is the D14 evidence of P2r8 §3.2. None of it reaches hylo's proxy after D14 | P2r8 §3.2 |
| Missing NFR (added to r3 §E.6) | **hylo listener protocol posture** is unspecified (h1-only versus h2 mirroring), and Go's defaults may negotiate h2 implicitly (unverified) → OD-94 | §A.7 |

R-12 (SIGHUP) unchanged in substance; the evidence column adds the two precisions from §B.2.

---

## Delta Summary

- **Target A (HTTP/2 re-classification):** round 4 folded the h2 sites into T-124 as "not live", but they are live for child tools. Round 4's
  5 operative sites, `enable_push`, and 3 h2 library defaults are now **8 new rows (T-140..T-147)** plus a rewritten T-124. Each row gives the
  value, site, legacy child-traffic effect and hylo disposition. Three existing rows were corrected or extended for h2: T-137 (reachable via
  h2 → h1 one-connection-per-flow), T-122 and T-139. **Two new behaviors found from source:** (1) h2 ping wakeups reset the 600 s inactivity watchdog,
  so h2 client connections are never idle-cut while their upstream is open; this is consistent with 0 of 57 production idle closes being h2. (2) h2 has
  no end-to-end backpressure through the proxy. Every pass-4 statement resting on "no h2" was listed and corrected (§A.4). New owner item
  **OD-94** (listener h2 posture; recommendation: HTTP/1.1 only).
- **Target B:** CONV-ABS-81 is **partly retracted** (CONV-ABS-86: the key holds the CONNECT authority, not the resolved IP). Its other sub-claims
  (not host-keyed, insertion-order eviction, CPU-only cost, no expiry re-check) are confirmed. CONV-ABS-82 is **confirmed**, with two precisions:
  the pty-close-as-hangup step is the one undocumented assumption, and zsh `HUP` is the general statement while the JOBS sentence is contextual.
- **Target C:** totals changed: 147 rows, NC 37, resolved 120 of 147. OD-57 lists unchanged.
- Retractions: **CONV-ABS-85, -86, -87** (88 unused). Owner items: **OD-94** (OD-95..OD-97 unused).
- New items: 8 threshold rows, 2 behavioral interactions, 1 owner item, 1 missing NFR. Refined: T-122, T-124, T-136, T-137, T-139, P-3, P-4, P-7,
  R-12 evidence.

## Remaining Gaps (verbatim-carryable)

1. Owner answers for OD-57 (18 bulk Dv† rows; 27 owner rationales in 7 groups, r3 §C.6) and for **OD-94** (h1-only listener versus h2 mirroring).
   OD-94's outcome changes the class of T-124 and T-140..T-147 (§C.2).
2. Go stdlib behavior (whether `net/http` server and transport negotiate h2 implicitly; `MaxHeaderBytes` default) is unverified, because it is not an
   authorized source. P1/P4 should verify it with a test that asserts the negotiated ALPN on both legs.
3. The pseudo-terminal-close-as-hangup step of R-12 is the one link not stated by the authorized man pages (§B.2).
4. The backend's idle keep-alive close timing, which decides how long a T-137 waiter would wait, is unverified (no network).
5. The P2r8 counts used here (57 idle closes with ALPN split, 7,566 h2 flows) were not re-counted this round.
6. Carried: T-078 port-allocation source unverified; asyncio values in r4 §B.4 are CPython 3.11's; P1/P3 boundary table tests (`SL:674`, `cols > 0`,
   T-090..T-092).

## Novelty Assessment

Novelty: SUBSTANTIVE

This round adds 8 threshold rows (T-140..T-147) by re-classifying sites that round 4 dismissed on a retracted basis. It also finds two behaviors
from source that change the model: the h2 ping timer keeps the 600 s inactivity cut from ever firing on h2 client connections, and h2 legs have no
end-to-end backpressure. It issues three retractions (CONV-ABS-85, -86, -87) and one new owner item (OD-94) that decides how hylo's listener
handles HTTP/2. Under the strict rule, new rows and retractions are each substantive. Removing these findings would change the spec: the
`internal/proxy` protocol posture, the meaning of `proxy.idle_timeout_s`, and the T-136 cache-key description.

## Convergence Declaration

Another round needed: this round made three retractions and added 8 rows. The next round should audit §A.3/§A.5/§A.6 against source independently,
and fold in OD-94's ruling if one has been made.

## State Checkpoint

```yaml
pass: 4
round: 5
status: complete
timestamp: 2026-11-14T12:30:00Z
novelty: SUBSTANTIVE
files_scanned: mitmproxy 12.3.1 proxy/layers/http/{_http_h2,_http2,__init__}.py, proxy/server.py, addons/tlsconfig.py, addons/dumper.py, certs.py, options.py, tools/main.py, recursive SIGHUP count over m/; h2/connection.py, h2/exceptions.py, hpack/hpack.py (adjacent, read-only); man termios(4), _exit(2), intro(2), zshoptions(1), zshmisc(1) (fresh dumps); legacy L:1,75,97, PX:170-208; p4r4 scratch inscope.tsv, classified.tsv, classify.out; pass-4 deep r1-r4, pass-2 deep r7-r9, pass-5 deep r3, pass-1 deep r3
h2_reclassification: {rows_new: 8 (T-140..T-147), rows_rewritten: [T-124], rows_extended: [T-122, T-137, T-139], interactions_new: [T-122xT-124 idle cut defeated on h2, no end-to-end h2 backpressure]}
verification: {CONV-ABS-81: partly retracted (CONV-ABS-86), CONV-ABS-82: confirmed with 2 precisions}
thresholds: {total: 147, new_this_round: 8, by_class: {CFG: 96, NC: 37, DROP: 7, OOS: 2, EXT: 2, NEW-H: 2, NA: 1}, rationale: {owner: 27, bulk_confirm: 18, na: 8, ext: 2, resolved_other: 92}, resolved: 120}
retractions: [CONV-ABS-85, CONV-ABS-86, CONV-ABS-87]
conv_abs_unused: [88]
new_owner_items: [OD-94]
od_unused: [OD-95, OD-96, OD-97]
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r5/
next: pass 4 round 6 (independent audit of r5 §A.3, §A.5, §A.6, §B.1)
```
