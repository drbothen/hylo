# Pass 2 Deepening — Round 8: Domain Model (production evidence from the retained mitmdump logs, re-verification of r7's riskiest claims, consolidated pointer table) — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Re-read this round: `dgx_proxy.py:10-25,92-120,168-214,362-407,520-540`,
  `claude-dgx:79-80`; `docs/PLAN.md:37,114-115,165-166` (D6, D13, D14).
- Authorized extra sources (read only):
  - **The retained mitmdump logs**: `$TMPDIR/dgx-mitm.<pid>.<port>.log`, **40 files, 184,943 lines, about 13 MB** at read time. Several are still
    being appended by live proxies, so every count below is a snapshot taken at about 07:35Z. Reported here as **counts and categories only**. IPs
    appear as `<ip>`, ports as `<port>`, home paths as `$HOME`. No request body, header, prompt text, session ID or URL query value is quoted.
  - **mitmproxy 12.3.1**, cited as "mitmproxy 12.3.1 `<module>:<line>`" (shortened to m/`<module>:<line>` in tables).
- Inputs read: pass-2 r7 (complete), r6 (§1.3-§5), r5 (§0.1, C-3, C-10, OD-17 row), r4 (§1.3 HTTP/2 row, §3.2 rows 10-11), pass-3 r4 (§0 log row,
  BC-PX-001/026 rows). **Pass-3 round 6 (`…-pass-3-deep-behavioral-contracts-r6.md`) did not exist at write time** (checked at start and at
  07:33Z). Nothing to reconcile, nothing edited.
- Method: nothing from legacy ran, no proxy, nothing networked. `CLAUDE.local.md` was not read. Four scratch scripts in
  `scratchpad/p2r8/` (`inact.py`, `tlsfail.py`, `ws.py`, `errs.py`), run with `/usr/bin/python3 -I`, read the logs as text and print aggregates
  only. Shell `grep`/`awk` counts are cross-checks. Shell environment check: no variable name containing `SSLKEYLOG` in the session environment, and
  none in `~/.zshrc`, `~/.zshenv`, `~/.zprofile`, `~/.zlogin` (names searched, values never printed). This agrees with the orchestrator's finding.
- Log line grammar (how lines were attributed): bracketed lines are `[HH:MM:SS.mmm][<client ip>:<client port>] <event>` (connection and TLS
  events). Flow lines are `<client>: <METHOD> <post-rewrite URL>[ HTTP/2.0]` followed by `<< <status>` and, for a failed flow, `<< <error>`.
  The dumper prints a flow when it **ends** (response done or error) (m/`addons/dumper:163-193,233-253`). A WebSocket message line is
  `<client> -> | <- WebSocket text message -> | <- <host:port><path>` (m/`addons/dumper:301-311`). Correlation is by client address within one log
  file, because one client address is one TCP connection.
- Numbering: owner items continue at **OD-43** (pass-3 r6 may take OD-45 and up; this round uses only OD-43). Retractions start at **CONV-ABS-25**.
  This round issues **CONV-ABS-25** and **CONV-ABS-26** (§5).

---

## 0. Inventory of the log evidence (counts, categories)

| Category | Count | Notes |
|---|---|---|
| Client connections | 17,156, **all from loopback** | No LAN client in 40 logs. The LAN exposure of r5 §1.1 (L1-L7) stays theoretical in this evidence |
| Upstream `server connect` | 18,486 to 85 distinct hosts | Top: `api.anthropic.com` 5,398; `http-intake.logs.us5.datadoghq.com` 5,165; `api.github.com` 3,413; private IP (the backend) 1,565; `github.com` 1,262; `downloads.claude.ai` 745; MCP servers (`api.perplexity.ai`, `mcp.context7.com`, `mcp.tavily.com`, `mcp.atlassian.com`, `mcp.exa.ai`, `mcp-proxy.anthropic.com`) 469 together; `registry.npmjs.org` 88; `analytics.brew.sh` 51; `pypi.org` 34; `proxy.golang.org` 16; and about 60 documentation and package hosts with fewer than 30 each |
| `api.anthropic.com` flows by path class | `/v1/code/…` 11,464; `/v1/messages` 7,252 (Anthropic lane; the DGX lane prints the rewritten backend URL); `/api/event_logging` 5,940; `/api/oauth` 533; `/api/eval` 129; `/mcp-registry/v0` 116; others under 100 | `/v1/code/…` and `/api/frame/sync` are recorded by **no** prior pass (§2) |
| `Closing connection due to inactivity` | 57 (56 `tls`, 1 `alpn=http/1.1`) in 23 logs | §1.1 |
| `Client TLS handshake failed. The client does not trust the proxy's certificate for …` | 75, 16 hosts, 16 logs | §3 |
| `Server TLS handshake failed.` | 119 (112 `connection closed`, 7 `Certificate verify failed: self-signed certificate in certificate chain`), each paired with one `Unable to establish TLS connection with server (…)` line | §4 |
| WebSocket | 4,202 message lines (2,086 client→server, 2,116 server→client), 2,400 server pings, 2,400 client pongs, 8 connections, **1 log** | §2.2 |
| Flow lines with ` HTTP/2.0` | **7,566 in 25 of 40 logs** | §5, CONV-ABS-25 |
| Lines naming `bridge.claudeusercontent.com` | **0** | §2.1, CONV-ABS-26 |

---

## 1. Target A — the inactivity closes, F-2 and F-3 with production numbers

### 1.1 The 57 inactivity closes: 56 idle, 1 in-flight cut

Method: for each close, the script gathered every earlier line for the same client address in the same log (bracketed events, flow lines, WebSocket
lines), took the latest timestamped activity, and checked the next five lines for that client for an error flow.

| Group | Count | Upstream | Last flow before the close | Gap from last activity to close | After the close |
|---|---|---|---|---|---|
| **Idle keep-alive** | **56** (all `Client(…, state=open, tls)`) | `registry.npmjs.org`, every one | completed: 53 × `304 Not Modified`, 3 × `200 OK` (package metadata and tarballs) | **600 s** in all 56 (to the second) | `client disconnect` only; **no error flow**, no `Client disconnected.` |
| **In-flight cut** | **1** (`Client(…, state=open, alpn=http/1.1)`) | `mcp.atlassian.com` | a `GET …/v1/mcp` whose response had started (`200 OK (content missing)` = streamed; a `Streaming response from mcp.atlassian.com.` line about 2 h 31 min earlier) | at least 600 s with no byte (the watchdog fired) | the GET flow is printed **after** the close with `<< Client disconnected.`, then `server disconnect`, `client disconnect` |

**Verdict.**
- The 56 are **benign**. They are npm's (or npx's) keep-alive connections, opened when MCP servers are launched through `npx` (the package names are
  MCP servers and their dependencies) and left idle after a completed response. `Client(…, tls)` with no ALPN fits Node's `https` agent, which sends
  no ALPN (m/`connection:196-205`: `tls` is printed only when TLS is up and no ALPN was negotiated). Cutting an idle keep-alive is the intended
  `tcp_timeout` behavior.
- The 1 is a **real F-2 cut**: an MCP Streamable-HTTP server-to-client event stream (a long-poll `GET`) that was silent for at least 600 s, closed by
  the proxy as "inactivity", with the flow ending in `Client disconnected.`. Its client offered ALPN `http/1.1`, which fits Claude Code's own MCP HTTP
  client (judgment: Node `undici` offers `http/1.1`). The path is not `/v1/messages`, so legacy's `error()` hook filters it out (`:316`) and **the
  ledger has no trace of it**. That is why r7 §0 ("F-2 not observed", from the ledger) could not see it.
- **None of the 57 involves `api.anthropic.com`, the DGX lane, or the WebSocket.**

**F-2 status, amended:** latent on the routed lanes (r7 §0 stands: 0 cuts in the ledger), and **observed once in production on a pass-through
stream** (MCP SSE). This widens F-2's scope from "a silent `/v1/messages` flow" to **any streamed response on any intercepted host**, which matters
because D13 intercepts every host (§1.3).

### 1.2 Long-lived streams on `api.anthropic.com` that F-2 did **not** cut

| Stream | Count | Duration (from the `Streaming response` line to the flow's end) | Ending | Cut by F-2? |
|---|---|---|---|---|
| `GET /v1/code/sessions/…` (SSE) | 240 GETs (231 matched to a stream start: 216 with a duration) in 10 logs | min 0 s, median **1,442 s**, p90 3,565 s, **max 3,600 s**; 148 of 216 lasted ≥ 600 s | 128 ended normally, 80 by server EOF (`HTTP/1 protocol error: peer closed connection without sending complete message body`), 32 by `Client disconnected.` | **No.** None of the 57 inactivity lines is on these clients |
| `/api/frame/sync` WebSocket | 8 connections, 1 log | 773 s to **13,862 s** (3 h 51 min) | 4 `ABNORMAL_CLOSURE`, 2 close code `4503` (`reason: cap_expired`), 2 without an end line | **No.** Server pings every **20 s** (§2.2) |

Consequences: the server keeps both channels active more often than every 600 s (the WebSocket provably every 20 s; the SSE stream by inference,
since 148 streams outlived 600 s without a cut). The `max 3,600 s` cap on the SSE streams is the **server's**, not the proxy's (the proxy has no
total-duration limit, r6 §1.3). The 80 server-EOF endings are logged at the flow level only. They are not `/v1/messages`, so no ledger event is
written.

### 1.3 hylo requirement from §1.1-§1.2 (default, no new OD)

**HY-PASS-1 (default; follows from D13 "forwarded unchanged" and D6 "Remote Control works"):** a pass-through flow has **no total-duration limit**,
and its response is relayed as it arrives (no buffering of `text/event-stream`; legacy does this through the "stream any SSE" rule,
`dgx_proxy.py:189-196`). The routed-lane limit HY-TIMEOUT-1 (≥ the client API timeout, 30 min by default) **must not** be applied to pass-through
flows: 1-hour Remote Control streams (§1.2) would be cut at 30 min. Idle cuts on pass-through flows fall under OD-37 (amended in §6), where the one
observed MCP cut is the evidence for a deviation.

### 1.4 F-3 (WebSocket retention) with production numbers

- Retention mechanism re-read (§5, B-3): confirmed.
- Production volume: **8** WebSocket connections in 40 logs, all on `api.anthropic.com/api/frame/sync`, all in **one** proxy log (one window that ran
  across 2026-11-10 and 2026-11-11). Messages per connection: 65, 176, 194, 346, 558, 610, 1,102, 1,151 (sum 4,202). The largest connection held
  **1,151 messages for 3 h 51 min**.
- **Bytes cannot be estimated from these logs.** At `flow_detail` 1 the dumper prints neither message size nor content (m/`addons/dumper:301-313`).
  F-3's magnitude is therefore "≤ 1,151 messages per connection, size unknown". Judgment: unless the messages are large, this is kilobytes to a
  few megabytes. F-3 stays a latent resource failure mode with a **bounded observed message count**, not an observed incident. After a flow ends,
  mitmdump keeps no reference to it (no `view` addon in mitmdump, r7 §1.1), so retention is per live connection, not cumulative.
- Log growth (the other half of F-3): 4,202 message lines plus 4,800 ping and pong lines in one log, about 9,000 of that log's lines.

---

## 2. Target A — what Remote Control actually uses (authoritative answer to the earlier open question)

### 2.1 Legacy's bridge rule keys on a host that never appears

| Fact | Source |
|---|---|
| Legacy's docstring and R0 rule assume the bridge is `bridge.claudeusercontent.com`: `request` writes `bridge_ws_connect` for an upgrade to that host; `response` writes `bridge_ws_close` for **every** response from it | `dgx_proxy.py:17-19,99-102,211-214`; r4 §3.2 rows 10-11; r5 C-3 |
| **0 lines** mention `bridge.claudeusercontent.com` in the 40 logs (no `server connect`, no flow, no handshake failure) | log count |
| The only WebSocket in the logs is on **`api.anthropic.com:<port>/api/frame/sync`** (8 `GET` upgrade flows, 4,202 messages) | log count |
| `api.anthropic.com` also carries **`/v1/code/sessions/…`**: 10,399 `POST`, 825 `PUT`, 240 streamed `GET` (11,464 flows in 10 logs) | log count |

**Domain consequences.**
1. **R0, `bridge_ws_connect` (row 10) and `bridge_ws_close` (row 11) are dead in production** for the period these logs cover (2026-11-10 to
   2026-11-14). The mechanism recorded in r4/r5 is correct as code. Its live frequency is zero by this evidence (owner check G-2 confirms it in the
   ledger). This joins the other dead legacy paths (`ws_closed`, r2 §4.5, BC-PX-027).
2. **Remote Control traffic is `api.anthropic.com` traffic.** It takes the same CONNECT tunnel, eager server connection and certificate as the
   routed `/v1/messages` lane. Legacy's `request` hook returns early for every non-`/v1/messages` path on that host (`:103-104`), so these flows pass
   through untouched. `responseheaders` still runs the rate-limit capture on them (`:175-187`; they carry no `anthropic-ratelimit-unified-*` headers
   unless the server sends them, and a change is logged only when it does). The SSE ones also get an `_SSETap` (`:192-195`), which is bounded at
   64,000 bytes (`:368`) and harmless.
3. **Which channel is "Remote Control"** is an inference (MEDIUM). `/v1/code/sessions/…` (Claude Code session objects, with long-poll streams) is
   present in 10 logs. `/api/frame/sync` (WebSocket, a `slug` query) appears in one window. The logs show the transport, not the feature name. Either
   way, **both are pass-through on `api.anthropic.com` and both must survive the proxy** for D6.
4. The legacy docstring's other claim, "payloads are never touched or buffered", holds for both channels: the WebSocket is relayed message by
   message, pings and pongs end to end (m/`proxy/layers/websocket:196-201`), and SSE is streamed.

**hylo.** The P4 exit check "Remote Control works" (`docs/PLAN.md:128`) should be tested against **these** two channels: a long-lived WebSocket
upgrade on `api.anthropic.com` (with 20 s server pings relayed end to end, never answered locally), and `/v1/code/sessions/…` long-poll SSE up to
3,600 s. The legacy `bridge_ws_*` ledger events are a D7 surface. Their fate goes to the owner as **OD-43** (§6).

### 2.2 WebSocket facts (production)

| Fact | Value |
|---|---|
| Host and path | `api.anthropic.com:<port>/api/frame/sync?slug=<value>` |
| Connections | 8, sequential in one log |
| Server ping interval | median **20 s**, max 21 s (2,400 pings; every ping answered by a client pong, 2,400) |
| Messages | 2,086 client→server, 2,116 server→client; all `text`; 65-1,151 per connection |
| Endings | 4 × `WebSocket Error: ABNORMAL_CLOSURE`, 2 × `UNKNOWN_ERROR=4503 (reason: cap_expired)` (a server close code in the private 4000-4999 range), 2 with no end line |
| Owner check 2 from r7 ("is the ping interval below 600 s?") | **Answered: yes, 20 s.** F-2 cannot cut this WebSocket. HY-BIND-6's idle default for WebSockets needs only to exceed 20 s plus margin. Recommendation: keep it well above that (judgment), since a different server may ping less often |

---

## 3. Target A — D14 evidence: child processes inherit the proxy and break, or get intercepted

**Legacy mechanism (re-read):** the launcher exports `HTTPS_PROXY=http://127.0.0.1:$MITM_PORT` and `NODE_EXTRA_CA_CERTS` (`claude-dgx:79-80`) to the
whole Claude Code process tree. There is no `NO_PROXY`, so local and private-network HTTPS also goes through the proxy. `NODE_EXTRA_CA_CERTS` only
affects Node. Separately, the trust CLI installs the mitmproxy CA as `trustRoot` in the login keychain (r3 §3.1), which macOS-native verifiers honor.

### 3.1 Harm 1: tools that trust neither break (75 handshake failures)

| Host the child tried | Failures | Logs | Likely client class (judgment from the host) |
|---|---|---|---|
| `pypi.org` | 25 | 13 (two per log) | Python packaging (`pip`/`uv` checks during MCP server or tool start) |
| `api.anthropic.com` | 8 | 1 (one burst within 1 s) | a non-Node API client with its own CA bundle, retrying |
| `raw.githubusercontent.com` | 8 | 1 | a script or installer download |
| private IP (`<ip>:<port>`) | 7 | 1 | a client of a private HTTPS service. Paired with the 7 upstream self-signed failures (§4); this client rejected the minted certificate with `tls alert bad certificate` |
| `dl-cdn.alpinelinux.org` | 5 | | container build tooling |
| `github.com` | 4 | | a git or curl build without keychain trust |
| `registry-1.docker.io` 3, `docs.nvidia.com` 3, `www.apple.com` 2, `nvcr.io` 2, `hub.docker.com` 2, `api.github.com` 2, `www.githubstatus.com` 1, `grafana.com` 1, `code.claude.com` 1, `auth.docker.io` 1 | 18 | | container tooling, documentation fetchers |
| **Total** | **75** across **16** hosts in **16** of 40 logs | | |

Each failure is the client aborting the handshake with `tlsv1 alert unknown ca` (or `bad certificate`) after the proxy presented a certificate minted
by the mitmproxy CA. The command fails at the network layer **while the proxy is up**. D14's stated rationale (`docs/PLAN.md:166`: children "keep
working when the proxy is down") is therefore **understated**: under legacy, tools with their own trust store fail **all the time**, proxy up or down.

### 3.2 Harm 2: tools that do trust are intercepted, and can be rerouted

| Evidence | Count |
|---|---|
| Flows printed with ` HTTP/2.0` (the client negotiated h2 through the proxy, so it accepted the minted certificate) | **7,566** in 25 logs: `api.github.com` 4,165, `github.com` 3,274, `analytics.brew.sh` 51, `ghcr.io` 36, `pkg-containers.githubusercontent.com` 17, `pypi.org` 10, others ≤ 4 |
| … of which on `api.anthropic.com`, rerouted by legacy to the DGX backend | **2** `POST /v1/messages`, each on its own short connection: the client spoke HTTP/2 to the proxy and the plain-HTTP backend answered HTTP/1.1 (`200`, 391 and 444 bytes, non-streaming) |
| Claude Code's own traffic in h2 | **0**. Its MCP client offered `alpn=http/1.1` (§1.1), and no `api.anthropic.com` flow other than those 2 is h2 |

Interpretation (MEDIUM): an h2-capable client that trusts the login keychain fits the Go-based `gh` CLI and macOS-native git/curl, which use the
platform verifier. These flows are decrypted, re-encrypted and visible to the proxy. The two `/v1/messages` POSTs came from a **non-Claude-Code**
client (Claude Code does not negotiate h2) that asked for a model matching `LOCAL_MODEL_PREFIXES`. **Legacy silently routed a child process's API
call to the local backend.** That is behavior D14 removes, and it shows that the legacy leak changes routing as well as breaking tools.

**Recorded as D14 production evidence** (D14 is ruled; no new OD): 75 broken TLS handshakes from 16 hosts, 7,566 intercepted h2 flows from trusting
tools, and 2 non-Claude-Code `/v1/messages` requests rerouted to the DGX. For the hylo test plan, the D14 mechanism (P4) should be checked against
all three: a child `pip`, a child `gh`, and a child API client.

---

## 4. Target A — upstream TLS failures (OD-41 and D13 evidence)

Method: each `Server TLS handshake failed` line was attributed to the latest `server connect <host>` of the same client in the same log, and the
following lines were checked for the failed flow.

| Upstream host | Error | Count | Logs | What the client saw |
|---|---|---|---|---|
| `http-intake.logs.us5.datadoghq.com` | `connection closed` | 63 | 5 | client TLS completed (eager: `Trying to establish TLS with client anyway`), then the one flow failed with `<< connection closed` (63 error flows) |
| `downloads.claude.ai` | `connection closed` | 48 | 5 | same; the failed flow is `GET …/claude-code-releases/latest` (48 error flows) |
| `browser-intake-us5-datadoghq.com` | `connection closed` | 1 | 1 | same (1 error flow) |
| private IP | `Certificate verify failed: self-signed certificate in certificate chain` | 7 | 1 | the client then rejected the minted certificate (§3.1 row 4); no flow |
| **`api.anthropic.com`** | — | **0** | | — |
| **DGX backend** (plain HTTP) | — | **0** (no TLS on that leg) | | — |

Findings:
1. **T-1's per-lane mechanism is confirmed in production.** An upstream handshake failure leaves the tunnel up, finishes the client handshake, and
   fails the flow with the server connection's error text (112 of 112 "connection closed" failures have exactly one `<< connection closed` flow).
   r7 §1.3 T-1 row 6 predicted this.
2. **Strict verification is observable in production.** The 7 self-signed failures show legacy refusing an upstream certificate that is not
   anchored in certifi. This is the private-CA case of r7 T-1 point 2, hit by a child process (not by a routed backend). Evidence for HY-TLS-1 and
   OD-41 (c) (per-backend `ca_file`): an `https` backend on that kind of host would fail the same way.
3. **No upstream TLS failure ever touched Claude Code's API host or the routed lanes.** All 112 `connection closed` failures are on two hosts that
   Claude Code itself contacts (judgment: telemetry intake and the release check), and both hosts also succeed in the same logs (5,165 and 745
   connects overall), so the failures are intermittent (about 1.9 % of connects to those hosts). They cluster in a window of roughly 2 hours at the
   same time of day in each of the 5 affected logs (on 2026-11-10, 11-11 and 11-14). The cause (the server closing during the handshake) is
   **not determinable from the logs**. It does not change any spec: under D13 hylo forwards these hosts unchanged, and the failure text falls under
   OD-28.
4. "Unable to establish TLS connection with server" is **119**, not 7: every `Server TLS handshake failed` line (112 + 7) has its companion line
   (m/`proxy/layers/tls:606-619`).

---

## 5. Target B — re-verification of r7's riskiest claims

| r7 claim | Verdict | Evidence |
|---|---|---|
| **B-1. Certifi-only upstream trust store** (T-1) | **CONFIRMED** | `create_proxy_server_context`: `if ca_path is None and ca_pemfile is None: ca_pemfile = certifi.where()`, then `load_verify_locations(ca_pemfile, ca_path)`, nothing else (mitmproxy 12.3.1 `net/tls:216-224`). `ca_path`/`ca_pemfile` come from `ssl_verify_upstream_trusted_confdir`/`_ca` (m/`addons/tlsconfig:359-371`). A package-wide search finds **no** `set_default_verify_paths` call, and `certifi` is imported only in `net/tls:13`. `ssl_insecure` False selects `VERIFY_PEER` (m/`addons/tlsconfig:314-317`). Production corroboration: §4 finding 2 |
| **B-2. `http2` True: "offer what the client offered"** (P-1) | **CONFIRMED as source behavior; r7's production inference partly RETRACTED (CONV-ABS-25)** | m/`addons/tlsconfig:322-339`: with `http2` True, `server.alpn_offers = tuple(client.alpn_offers)`; a TLS client without ALPN gets `[]` upstream. Production now shows both sides of the rule: Claude Code offers `http/1.1` only, so its Anthropic leg is h1 (r7's conclusion for **Claude Code** holds); h2-capable clients get h2 on both legs (7,566 flows), and **`api.anthropic.com` accepts h2 when it is offered** (2 flows). That resolves r7's "either the client never offers `h2`, or the upstream declined it": it is the former. What is retracted: "0 ` HTTP/2.0` lines in 38 logs" and its consequences (§5.1) |
| **B-3. WebSocket messages retained in memory for the connection's life** (W-1) | **CONFIRMED** | Each finished message is appended to `self.flow.websocket.messages` (m/`proxy/layers/websocket:177-187`), and frame fragments are joined into `content` first (`:170-181`). The only reassignment in the package is the replay iterator (m/`eventsequence:25`); `tcp.py:56`/`udp.py:53` are other flow types. No size cap exists on a message or on the list. Pings and pongs are relayed (`:196-201`), not stored. Production volume: §1.4 |
| r7 W-1 "Remote Control (the bridge to `bridge.claudeusercontent.com`)" | **RETRACTED (CONV-ABS-26)** | §2.1 |
| r7 §1.3 W-1 "whether the bridge pings more often than every 600 s is unknown" | **Answered** | 20 s (§2.2) |
| r7 §1.4 T-3 (`SSLKEYLOGFILE` read at import) | **Unchanged; not set in production** | m/`net/tls:147-149` re-read; variable absent from the environment and the zsh rc files (header). T-3 stays a latent hazard, and HY-TLS-3 stays a default |
| r7 §0 settlement "O-1 confirmed" for the 36 unpaired DGX requests | **CONFIRMED with a mechanism** | One log, which started and ended on 2026-11-11, has **36** `<< [Errno 65] No route to host` flows on the DGX lane (`/v1/messages`); a log spanning 2026-11-10 to 11-11 has 2 more. This matches the 36 unpaired requests dated 2026-11-11 and the docstring's incident ("a terminal without Local Network permission got `No route to host` on every Sonnet request", `:311-315`). The 18 later `[Errno 61] Connect call failed` flows (a log from 2026-11-12 on) match the ledger's 18 connect-refused events (r4) |

### 5.1 Retractions

| Marker | Prior claim (file) | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-25** | P2r5 §0.1 row 2 and P3r4 §0: "38 mitmdump logs: **0** lines containing ` HTTP/2.0`". Consequences recorded from it: P2r5 C-10 and the OD-17 row ("h2 sticky cache … **not live**, HTTP/1.1 observed"); P2r5 §0.1 "The HTTP/2 sticky-failure mode is not live in production"; P2r7 §1.3 P-1 "both legs are HTTP/1.1"; P2r7 §1.5 row 1 (`http2_ping_keepalive`, `normalize_outbound_headers` "inert … both legs are h1") | **7,566** ` HTTP/2.0` flow lines in 25 of 40 logs, including logs that were closed before r5 was written (for example one closed on 2026-11-10 with 73, one closed on 2026-11-11 with 3,795). What survives: **Claude Code's own traffic is HTTP/1.1** (0 h2 flows on its hosts except 2 non-Claude-Code ones; its MCP client offers `http/1.1`). Corrections: (a) h2 is live in the legacy proxy for **child-process tools** (Harm 2, §3.2); (b) r4 §1.3's HTTP/2 sticky-failure row is **reachable** for an h2 client of `/v1/messages` (2 such flows, both successful, so the sticky failure itself was never observed); (c) the h2 knobs are active for those flows, not inert. **Spec impact: none for hylo's routed lanes**, because Claude Code is h1 and D14 removes the child traffic. OD-17's recommendation is unchanged; its rationale should read "sticky h2 failure reachable only by non-Claude-Code clients, removed by D14" instead of "not live" | §0, §3.2, §5 B-2 |
| **CONV-ABS-26** | P2r7 §1.3 W-1 and F-3: "a long session with Remote Control (the bridge to `bridge.claudeusercontent.com`)"; P2r7 §1.3 "the bridge WebSocket is also subject to F-2"; implicitly every pass that equates legacy's R0 / `bridge_ws_*` with Remote Control (r2 §4.2 R0 description, r4 §3.1 *Routing decision* R0 "bridge WS") | `bridge.claudeusercontent.com` appears **0** times in 40 logs. The observed long-lived channels are on `api.anthropic.com`: the `/api/frame/sync` WebSocket (8 connections) and `/v1/code/sessions/…` long-poll SSE (240 GETs). F-3 applies to the `/api/frame/sync` WebSocket. F-2 cannot cut it (20 s pings). The R0 **code** description stays correct (it is what `:100-102` does); only its identification with live Remote Control traffic is retracted | §2 |

---

## 6. Owner-decision list delta (base: OD-01..OD-42 after r7)

| ID | Change | Status |
|---|---|---|
| OD-17 | Rationale corrected per CONV-ABS-25: the h2 sticky failure is reachable in legacy only by non-Claude-Code h2 clients (2 flows observed, none failed); D14 removes them. Recommendation unchanged | P |
| OD-37 | **Scope widened and first production evidence.** Legacy's 600 s idle cut applies to **every** intercepted flow, and it fired once in production on an in-flight MCP SSE stream (`mcp.atlassian.com`), with no ledger trace (§1.1). 56 other cuts were idle npm keep-alives (benign). It never cut a Remote Control channel (§1.2). Recommendation, amended: deviation. Routed lanes: HY-TIMEOUT-1. Pass-through flows: HY-PASS-1 (no total-duration cap) and **no idle cut while a response is being streamed**; idle cut only for connections with no flow in progress (HY-BIND-6) | P |
| OD-41 | Production evidence added: strict verification observed (7 self-signed rejections on a private-IP host); no upstream TLS failure on `api.anthropic.com` in 40 logs; 112 intermittent `connection closed` handshake failures on two Claude Code hosts (cause not determinable, about 1.9 % of their connects). Recommendation unchanged | P |
| **OD-43** (new) | **Legacy bridge instrumentation and the real Remote Control channels.** `bridge_ws_connect` and `bridge_ws_close` (ledger rows 10-11, D7 surface) key on `bridge.claudeusercontent.com`, which never appears in production; the live channels are `api.anthropic.com` `/api/frame/sync` (WebSocket) and `/v1/code/sessions/…` (SSE). Decide: (a) reproduce the dead rule byte for byte through cutover (D4/D7), (b) also or instead emit life-cycle events for the observed channels after cutover, or (c) drop both after cutover | P. Recommendation: (a) through cutover, because it is cheap and keeps the ledger format unchanged (D7); then (b) as a post-cutover change with a new event name, so that the status line and Remote Control debugging can see these channels. The D7 freeze forbids changing the existing event names before cutover, not adding new ones afterwards |

**Count: 43 items (OD-01..OD-43): 41 pending, 2 ruled (OD-24, OD-27).**
Defaults introduced without an OD: **HY-PASS-1** (pass-through: no total-duration cap, relay as it arrives; from D13 and D6). Updated default:
HY-BIND-6 WebSocket idle limit must exceed the observed 20 s ping interval, with margin (judgment).

---

## 7. Target C — consolidated pass-2 canonical pointer (supersedes r6 §5 and r7 §4.3; read only this table)

Read the base location first, then the amendments in order. Pass-2 files are `…-pass-2-deep-domain-rN.md` (r1 = `…-pass-2-deep-domain.md`).
P3rN = `…-pass-3-deep-behavioral-contracts-rN.md`.

| Topic | Authoritative base | Amendments (apply in order) |
|---|---|---|
| **Entity catalogue** (all bounded contexts) | r4 §3.1 | r5 §2.2 CONV-ABS-13 (exporter state: 19 accumulators + 3 dict states + 5 scalars); r5 C-5 (28 metric names); r5 C-7/C-8, §1.1 (proxy listener, exporter admission); r5 §2.4 F-1 and r6 §2 (exporter process lifecycle); r6 §1.1-1.3 (proxy process: signals, F-2); r7 §1.3 W-1 (per-WebSocket message list, F-3); r7 §1.4 T-3 (process env input `SSLKEYLOGFILE`); **r8 §2 (Remote Control channels = `api.anthropic.com` `/api/frame/sync` WebSocket and `/v1/code/sessions/…` SSE; R0 / `bridge_ws_*` dead in production, CONV-ABS-26)** |
| **Ledger schema** (13 events, writer contract, field order, consumers) | r4 §3.2 | r5 C-1, C-2, C-3, C-4; CONV-ABS-14 and r6 §2 (error event names identify the host, not the lane); **r8 §2.1 (rows 10-11 never fire in the logged period; OD-43)** |
| **Correlation / pairing** | r4 §3.3 | r5 C-6; r6 §1.4 (the 36: causes O-1..O-6); r7 §0 (all 2026-11-11: O-1); **r8 §5 (mechanism: 36 `No route to host` flows in one 2026-11-11 log)** |
| **Error-text table** (`*_upstream_error.error`) | r4 §1.3 | r5 CONV-ABS-14; r6 §1.2-1.3 (shutdown and inactivity cuts emit the same texts); r7 §4.2 (+6 rows: upstream TLS failures, `connection cancelled`); **r8 §4 (`connection closed` observed as the flow error after an upstream handshake close; non-`/v1/messages`, so never in the ledger)** |
| **Routing decisions, request body, normalization, flow attributes** | r2 §4.1-4.5 | r3 §4.3 (`count_tokens` live); r4 §3.1 rows *Routing decision*, *Tool set*, *Flow attribution*; **r8 §2.1 (R0 never matches in production)**; **r8 §3.2 (non-Claude-Code clients' `/v1/messages` are routed too: 2 observed)** |
| **Upstream connection model** (mitmproxy) | r4 §1.1-1.3 | r5 §0.1/C-10 **as corrected by r8 CONV-ABS-25** (Claude Code is h1; h2 is live for child tools; the h2 sticky row is reachable only by non-Claude-Code clients); r6 §1.3 (600 s inactivity); r7 §1.3 T-1, P-1, §1.4 T-4; **r8 §4 (T-1 per-lane mechanism production-confirmed), §5 B-2 (Anthropic accepts h2 when offered)** |
| **Long-lived pass-through streams** (new row) | **r8 §1.2, §2.2** (SSE up to 3,600 s; WebSocket up to 3 h 51 min, 20 s pings) | — |
| **mitmproxy runtime configuration** | r7 §1 (93 options) | **r8 CONV-ABS-25** (h2 knobs active for child h2 flows, not inert) |
| **TLS requirements** | r7 §1.3 T-1/T-2, §1.4 T-3 (HY-TLS-1, HY-TLS-3, OD-41) | **r8 §4, §5 B-1** (certifi-only re-confirmed; production evidence) |
| **Proxy shutdown semantics** | r6 §1.1-1.2 | r7 §2 (asyncio.run link read; HIGH) |
| **Cache wire formats** (session, mix, git, cost history) | r1 §3.1-3.6 | r2 §0; r4 §3.1 *Session cockpit* rows; r5 §2.1 row 32 |
| **Status line stdin schema** | r1 §1.1-1.3 | r3 §0.1 |
| **Transcript schema and incremental parser** | r1 §2.1-2.5 | r4 §3.1 *Transcript record* (CONV-ABS-4) |
| **Telemetry (VictoriaMetrics) response and recording rules** | r1 §4.1-4.3 | r3 §2.1-2.3; r5 C-9 |
| **Hook stdin, Kev wire format, hook stdout and log grammar** | r2 §6.1-6.5 | — |
| **Launcher `--settings`, child env, env-bool grammar** | r2 §6.6-6.8 | r3 E-5; **r8 §3 (production effect of the exported `HTTPS_PROXY`/`NODE_EXTRA_CA_CERTS`: 75 broken child handshakes, 7,566 intercepted child h2 flows; D14 evidence)** |
| **CONFIG map (D15)** | r1 §6.1-6.3 | r2 §0, §6.8; OD-01/OD-05 |
| **Trust, CA, preflight, coordinator** | r3 §3.1-3.3 | r4 §0.2; r6 §4.2; r7 §1.3 T-1 point 3 (keychain root vs a Go OS-store verifier); **r8 §3.2 (the keychain root is what lets macOS-native child tools accept the proxy)** |
| **Backfill** | r2 §7 | r3 E-4; OD-13, OD-31 |
| **Crash catalogues / failure modes** | index in r4 §3.1 (closing paragraph) | status line: P3r2 table (43 IDs); proxy P-R1..R4 / P-S1..S4: r2 §4.6 + r3 §1.1 (P-S production-confirmed r4 §0.1); exporter E-01..E-09, E-20, E-21: r2 §5.2 + P3r2 BC-EX-021; hook H-01..H-08: r2 §6.3; backfill B-01..B-08: r2 §7. Failure modes outside the catalogues: **F-1** (r5 §2.4, r6 §2); **F-2** (r6 §1.3; r7 §0 latent on routed lanes; **r8 §1.1: observed once on a pass-through MCP stream**); **F-3** (r7 §1.3; **r8 §1.4: ≤ 1,151 messages per connection observed, bytes unknown**) |
| **Owner-decision list** | r5 §3.2 (OD-01..OD-34) | r6 §3 with r7 §0 renumbering (r6 OD-35 → OD-37, OD-36 → OD-38); P3r4 §5 (OD-35, OD-36); P3r5 (OD-39, OD-40); r7 §3 (OD-41, OD-42; notes on OD-17, OD-28, OD-37, OD-38); **r8 §6 (OD-43; notes on OD-17, OD-37, OD-41)**; pass-3 r6 (OD-45 and up, if issued) |
| **LAN exposure and bind requirements** | r5 §1.1-1.4 (HY-BIND-1..6) | r6 §0, §2, §1.3; r7 §1.3 W-1; **r8 §0 (all 17,156 client connections loopback: no LAN client observed); r8 §2.2 (WebSocket idle limit > 20 s ping); r8 §1.3 HY-PASS-1** |
| **Retractions** | r5 §0.3 table | r6 CONV-ABS-20; r7 none; **r8 CONV-ABS-25 (h2 "0 lines"), CONV-ABS-26 (bridge host = Remote Control)** |

Superseded and not to be used for Phase 1 without the amendments: broad pass 2's ledger schema (11 events; r4 has 13 with variants), r4's
"15 keyed accumulators" and "27 metric families" figures, r6 §5 and r7 §4.3 (folded into this table).

---

## 8. Is anything in the pass-2 domain model still open?

| Item | State after r8 |
|---|---|
| Entities, ledger schema, env inputs, runtime configuration | Closed. This round adds no legacy entity. It corrects the identification of the Remote Control channels (§2) and records the pass-through stream class (§1.2) |
| F-2 frequency | Closed: 0 on routed lanes (ledger), 1 on pass-through streams (logs), 56 benign idle cuts |
| F-3 volume | Closed as far as the logs allow (message counts). **Message sizes are not determinable** from `flow_detail` 1 logs (LOW; no spec impact, because HY-WS-1 already bounds memory) |
| Upstream TLS failures in production | Closed (§4). Cause of the 112 intermittent `connection closed` handshakes: not determinable, no spec impact |
| D14 leak | Closed with production counts (§3) |
| Owner capture: VictoriaMetrics NaN | **Open** (after the soak), carried |
| Owner ledger check (new, local, read-only) G-2 | Count `bridge_ws_connect` and `bridge_ws_close` lines in the ledger (expected 0 for the logged period). Confirms OD-43's premise; not needed for the spec |
| Not determinable from authorized sources (LOW) | whether vLLM sends a byte before the first token; whether Claude Code sends non-streaming Sonnet requests (likelihood of F-2 on the routed lane); the OS TCP connect timeout behind T-4; which of the two `api.anthropic.com` channels is branded "Remote Control" (both must pass, so no spec impact) |

**Plain answer:** apart from the owner captures (VictoriaMetrics NaN, and the optional ledger count G-2), **nothing in the pass-2 domain model is
open.** The remaining unknowns are labeled LOW and none of them changes an entity, a schema or a hylo requirement.

---

## Delta Summary

| Target | New | Refined / confirmed |
|---|---|---|
| A inactivity | verdict: 56 idle npm keep-alives (benign, exactly 600 s after a completed response), **1 in-flight F-2 cut** of an MCP SSE stream with no ledger trace; HY-PASS-1 | F-2 latent on routed lanes (r7 §0) stands; OD-37 scope widened |
| A Remote Control | **live channels identified**: `api.anthropic.com` `/api/frame/sync` WebSocket (8 connections, 20 s pings, ≤ 3 h 51 min) and `/v1/code/sessions/…` SSE (240 streams, ≤ 3,600 s) plus 11,224 POST/PUT; legacy R0/`bridge_ws_*` dead in production; OD-43 | r7 owner check 2 answered; F-3 volume bounded by message count |
| A D14 | 75 child handshake failures (16 hosts); 7,566 intercepted child h2 flows; **2 non-Claude-Code `/v1/messages` rerouted to the DGX** | D14 rationale understated (children break with the proxy up) |
| A TLS | upstream failures attributed: 63 + 1 telemetry, 48 release check, 7 private self-signed; 0 on `api.anthropic.com` or the routed lanes | T-1 per-lane mechanism production-confirmed; OD-41 evidence |
| B re-verification | — | certifi-only CONFIRMED; ALPN mirroring CONFIRMED (Anthropic accepts h2 when offered); WebSocket retention CONFIRMED; O-1 confirmed with mechanism (36 `No route to host` flows on 2026-11-11) |
| Retractions | **CONV-ABS-25** (h2 "0 lines" and its consequences), **CONV-ABS-26** (bridge host = Remote Control) | — |
| C pointer | consolidated table (supersedes r6 §5 + r7 §4.3), 1 new row (long-lived pass-through streams), 14 rows amended | pass-2 open items: owner captures only |

New items: 4 (Remote Control channel identification, pass-through stream class with HY-PASS-1, the in-flight F-2 cut on pass-through, child
`/v1/messages` rerouting) plus OD-43. Corrected: 2 recorded claims (CONV-ABS-25, CONV-ABS-26). Refined: 6 (OD-17, OD-37, OD-41, F-3 volume, O-1
mechanism, D14 evidence).

## Remaining Gaps (verbatim-carryable)

1. Owner capture, VictoriaMetrics (unchanged): one `/api/v1/query` response for the exact `QUERY` (`dgx_statusline.py:102-123`) on an idle box,
   under light load, and with fewer than 20 TTFT samples, after the DGX soak is scored. Look for `"NaN"`/`"+Inf"`/`"-Inf"` in `value[1]` per
   `__name__`.
2. Owner ledger check G-2 (local, read-only, optional): count `bridge_ws_connect` and `bridge_ws_close` events in the ledger; expected 0 for
   2026-11-10..14. Confirms OD-43's premise.
3. Not determinable from authorized sources (LOW, no spec impact): WebSocket message sizes (F-3 bytes); the cause of the 112 intermittent upstream
   `connection closed` handshakes on the telemetry and release-check hosts; whether vLLM sends a byte before the first token and whether Claude Code
   sends non-streaming Sonnet requests (routed-lane F-2 likelihood); the OS TCP connect timeout behind T-4; which `api.anthropic.com` channel is
   branded "Remote Control".
4. Owner decisions: 41 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-43).
5. Downstream note for pass 3 (not a pass-2 gap): BC-PX-001 and BC-PX-026 should carry "never observed in production (CONV-ABS-26)"; the P3r4 §0
   log row needs CONV-ABS-25's correction; a BC for HY-PASS-1 (pass-through streams have no total-duration cap) does not exist yet.

## Novelty Assessment

Novelty: SUBSTANTIVE

Much of this round is confirmation and therefore NITPICK by the stated rule: the three re-verified mitmproxy claims, the 56 benign inactivity cuts,
the production counts for T-1 and the D14 leak (D14 is already ruled), the O-1 mechanism, and the consolidated pointer table.

Three findings change the model, and two of them are wrong recorded claims:
- **CONV-ABS-25:** the recorded "0 ` HTTP/2.0` lines" is false (7,566). The fact that survives (Claude Code is h1) is narrower, and the HTTP/2
  sticky-failure path recorded as "not live" is reachable by non-Claude-Code clients. Two of those clients' `/v1/messages` were actually rerouted to
  the DGX.
- **CONV-ABS-26 plus the new channel entity:** Remote Control traffic is on `api.anthropic.com` (`/api/frame/sync` WebSocket and
  `/v1/code/sessions/…` long-poll SSE). `bridge.claudeusercontent.com`, which legacy, r7's F-3 and several earlier rows assume, never appears. This
  changes the D6 test target, produces OD-43 for the dead `bridge_ws_*` events, and turns long-lived pass-through streams into a recorded class.
- **F-2 on pass-through streams:** the 600 s cut has fired in production, on an MCP SSE stream that the ledger cannot see. This, together with the
  1-hour SSE streams, gives the new default HY-PASS-1: hylo's routed-lane timeout must not be applied to pass-through flows.

Removing these would change how the proxy's timeouts, its D6 acceptance test and the D7 handling of `bridge_ws_*` are specified. Under the binary
rule that is SUBSTANTIVE.

## Convergence Declaration

Another round needed: this round retracted two recorded claims (CONV-ABS-25, CONV-ABS-26) and added the Remote Control channel entity and the
pass-through stream class. A round 9 should re-check those two corrections and HY-PASS-1 against source, reconcile with pass-3 r6 (BC-PX-001/026,
the P3r4 §0 log row, OD numbering), and carry the owner capture.

## State Checkpoint

```yaml
pass: 2
round: 8
status: complete
files_scanned: dgx_proxy.py (10-25, 92-120, 168-214, 362-407, 520-540); claude-dgx (79-80); docs/PLAN.md (37, 114-115, 128, 165-166); mitmproxy 12.3.1 (net/tls, addons/tlsconfig, addons/dumper, proxy/layers/websocket, proxy/server, connection, eventsequence; package search for set_default_verify_paths/certifi/messages reassignment); 40 mitmdump logs (184,943 lines, counts only)
timestamp: 2026-11-14T07:50:00Z
novelty: SUBSTANTIVE
retractions: [CONV-ABS-25 (h2 "0 lines" and consequences), CONV-ABS-26 (bridge.claudeusercontent.com = Remote Control)]
conv_abs_next_free: 27
inactivity_closes: {total: 57, idle_keepalive_npm: 56, inflight_cut: 1 (mcp.atlassian.com SSE, no ledger trace), on_anthropic_or_dgx: 0}
client_trust_failures: {total: 75, hosts: 16, logs: 16, top: [pypi.org 25, raw.githubusercontent.com 8, api.anthropic.com 8, private-ip 7]}
upstream_tls_failures: {total: 119, connection_closed: 112 (datadog intake 63+1, downloads.claude.ai 48), self_signed_private_ip: 7, api_anthropic: 0, dgx_lane: 0}
websocket: {host_path: api.anthropic.com /api/frame/sync, connections: 8, logs: 1, messages: 4202, pings: 2400, ping_interval_s: 20, max_duration_s: 13862, max_messages_per_conn: 1151}
remote_control_sse: {path: api.anthropic.com /v1/code/sessions/, get_streams: 240, max_duration_s: 3600, median_s: 1442, post: 10399, put: 825}
http2_flows: 7566 (Claude Code: 0; non-CC /v1/messages rerouted to DGX: 2)
owner_decisions: 43 (OD-01..OD-43; 41 pending, 2 ruled: OD-24, OD-27)
pass3_r6_reconciled: not present at write time
next: pass 2 round 9 (re-verify CONV-ABS-25/26 and HY-PASS-1; reconcile pass-3 r6; owner capture)
```
