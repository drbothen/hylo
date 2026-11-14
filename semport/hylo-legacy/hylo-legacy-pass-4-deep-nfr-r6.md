# Pass 4 Deepening — Round 6: verification of round 5's HTTP/2 items; Go net/http h2 facts for OD-94 — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/`, read-only and static. Nothing in `legacy/` was imported, executed or modified. No proxy, nothing
  networked, no socket binds, no DNS lookups. CLAUDE.local.md was not read. No git commit.
- Authorized read-only references, all read fresh this round:
  - `m/` = mitmproxy 12.3.1 (`m/version.py:5` `VERSION = "12.3.1"`) under `$PROTOTYPE/.mitmenv/lib/python3.12/site-packages/`.
  - `h2/` 4.4.1 and `hpack/` 4.2.0, in the same venv (versions from their `dist-info/METADATA`).
  - **New this round:** `go/` = the Go 1.26.5 standard library (`go env GOROOT` = `/opt/homebrew/Cellar/go/1.26.5/libexec`, `VERSION` "go1.26.5").
    Files read: `src/net/http/{server,transport,http,h2_bundle,omithttp2}.go`, `src/crypto/tls/{handshake_server,handshake_server_tls13,common}.go`
    and `src/internal/godebugs/table.go`. Nothing was compiled or run.
- Inputs read: pass-4 deep r5 (complete), r4 (complete) and r3 (§C catalogue, §C.5 totals, §C.6 OD-57). Legacy `dgx_proxy.py` (`PX`) l.100-163
  was grepped to check whether the addon ever rewrites `http_version` (it does not; it rewrites only `scheme`, `host` and `port`, at `PX:161-163`).
  **Pass-5 deep r4 did not exist** when this round ran (`ls` of the semport directory), so it was neither read nor edited.
- Scratch directory `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r6/` was created. It is
  empty: every value below comes from direct reads, and no generated artifact is needed.
- Numbering: retractions **CONV-ABS-93, CONV-ABS-94** (95 and 96 unused). **No new owner items** (OD-102..OD-105 unused). OD-94 gets a facts
  annex (§B), not a new number. Sibling files were not edited.

Abbreviations, rationale codes and D15 classes are the same as in r3 §C.1 and r5.

---

## A. Target A: independent re-verification of round 5

### A.1 Verification table

| # | Round-5 item | Fresh evidence (this round) | Verdict |
|---|---|---|---|
| 1 | **T-124** (rewritten): 58 s h2 PING, upstream `Http2Client` only | `m/options.py:137-146` (`http2_ping_keepalive`, int, 58; "Set to 0 to disable"). `m/proxy/layers/http/_http2.py:539-562`: on `Wakeup`, a PING is sent when `time.time() - last_activity + 1 > 58`, i.e. after about 57 s idle. The next wakeup is always requested for `58 - (now - last_activity)` (`:558-561`). `:564` sets `last_activity` on every non-Wakeup event; `:565-567` arms the first wakeup at Start only if the option is `> 0`. Only `Http2Client` (`:474`) has this code. `Http2Server` (`:406-471`) has none | **confirmed**. Precision: the ping fires after about 57 s of idleness, so "every ≤ 58 s" is correct |
| 2 | **T-140** local initial stream window 2³¹ − 1 | `m/proxy/layers/http/_http_h2.py:53` (set), `:57` (`local_settings.acknowledge()`). Immediate acknowledgement of received data: `_http2.py:238-240` | **confirmed** |
| 3 | **T-141** connection window 2³¹ − 1 | `_http_h2.py:61-67`: `initiate_connection` adds `2**31 - 1 - inbound_flow_control_window`. `initiate_connection` runs at `Start` for both subclasses (`_http2.py:124-126`) | **confirmed** |
| 4 | **T-142** max frame size 2¹⁷, advertised and enforced inbound; parenthetical "h2 library default inbound cap would be 2²⁴ (`h2/connection.py:311`, default not used)" | Value: `_http_h2.py:54` (advertised), `:55` (`max_inbound_frame_size = 2**17`). Enforcement: `h2/connection.py:1516` copies `max_inbound_frame_size` into `incoming_buffer.max_frame_size` on every `receive_data`; `h2/frame_buffer.py:70-72` raises `FrameTooLargeError`. **Parenthetical is wrong:** `DEFAULT_MAX_INBOUND_FRAME_SIZE = 2**24` (`h2/connection.py:311`) is defined but **never referenced**; the only uses of the name are its definition. The library's real default is `max_inbound_frame_size = local_settings.max_frame_size` (`:377`), which is the RFC 7540 default of 16,384 B, updated on SETTINGS ACK (`:2003-2005`). mitmproxy raises it to 2¹⁷ from both directions | **value confirmed; parenthetical retracted (CONV-ABS-94)** |
| 5 | **T-143** 10 provisional upstream streams until the server's first SETTINGS; unbounded FIFO queue | `_http2.py:487-490` (`stream_queue` defaultdict(list); `provisional_max_concurrency = 10`); `:511-518` (queue when `open_outbound_streams >= 10 or remote max`); `:529-537` (resume FIFO, comment "popitem would be LIFO, but we want FIFO"); `:631-634` (`RemoteSettingsChanged` sets it to `None`). **Refinement:** if the server's SETTINGS omit `MAX_CONCURRENT_STREAMS`, the remote value is `2**32+1` (`h2/settings.py:226-231`), so after the first SETTINGS the cap is effectively unbounded | **confirmed + refinement** |
| 6 | **T-144** push disabled on the upstream leg | `_http2.py:496-500` (`enable_push = 0`, then acknowledge); `:297-301` logs a push promise at ERROR | **confirmed** |
| 7 | **T-145** local `MAX_CONCURRENT_STREAMS` 100 | `h2/connection.py:344-362` (initial value 100, with the comment explaining why); `:1599-1606` raises `TooManyStreamsError` when `open_inbound_streams + 1 > 100`; `h2/exceptions.py:47` (subclass of `ProtocolError`, code `PROTOCOL_ERROR`) | **confirmed** |
| 8 | **T-146** max decoded header list 65,536 B | `h2/connection.py:319-320`, `:335`, `:359-360`; ACK path `:1999-2001`; `hpack/hpack.py:34` (`DEFAULT_MAX_HEADER_LIST_SIZE = 2 ** 16`), `:499` (`inflated_size = 0`), `:543-547` (adds `table_entry_size`, raises `OversizedHeaderListError` when the total is `>` the limit); `h2/connection.py:2104-2111` turns that into `DenialOfServiceError` | **confirmed** (strict `>`: exactly 65,536 B is accepted) |
| 9 | **T-147** closed-stream memory 65,536 | `h2/connection.py:322-323`, `:395-397` (`SizeLimitDict(size_limit=MAX_CLOSED_STREAMS)`), `:2033-2034` | **confirmed** |
| 10 | r5 §A.2 item 4: every `ProtocolError` "is turned into a GOAWAY `PROTOCOL_ERROR`" and fails every stream | `h2/connection.py:1525-1531`: before re-raising, h2 itself calls `_terminate_connection(e.error_code)` (`:1584-1593`), which queues a GOAWAY carrying **the exception's own code**: `FRAME_SIZE_ERROR` (`h2/exceptions.py:27-33`), `ENHANCE_YOUR_CALM` for `DenialOfServiceError` (`:182-195`), `PROTOCOL_ERROR` for `TooManyStreamsError`. mitmproxy then calls `protocol_error` (`_http2.py:205-206, 275-277, 314-322`), which queues a **second** GOAWAY with `PROTOCOL_ERROR` (`CLOSED + SEND_GOAWAY` is a legal transition, `h2/connection.py:244`) and fails every tracked stream (`:324-333`) | **confirmed (connection-fatal) + precision**: two GOAWAY frames, the first with the specific code. No parity surface (D14) |
| 11 | **T-137 reachability**: an h2 client rerouted to an h1 upstream gets one upstream connection per flow; a 6th concurrent stream "waits, and keeps waiting until the backend closes an idle keep-alive" | One connection per flow: **confirmed** (`m/proxy/layers/http/__init__.py:1087-1097` refuses reuse when `client.alpn == b"h2"` and the connection is not h2; `:1178-1188` gives each queued waiter its own connection). Permit for the connection's life: **confirmed** (`m/proxy/server.py:109, 206, 258-265`). **The wait duration is wrong.** mitmproxy closes the h1 upstream connection itself after one flow when the request is HTTP/2: `m/proxy/layers/http/_http1.py:200-209` (`connection_done` includes `request.is_http2 and isinstance(self, Http1Client)`, with the comment "we can rely on the proxyserver's max-connection-per-server throttling"). `Http1Client` keeps the original request object (`_http1.py:357`; the HTTP/1.1 copy at `:362-370` is used only to build the head), `is_http2` is `http_version == b"HTTP/2.0"` (`m/http.py:284-285`), and legacy never rewrites `http_version` (`PX:161-163`). So a 6th concurrent rewritten stream waits until one of the 5 in-flight flows **completes**, not until the backend closes an idle keep-alive. T-137 is in fact the throttle mitmproxy's authors rely on for h2 → h1 | **reachability confirmed; wait-duration claim retracted (CONV-ABS-93)**. r5 Remaining Gap 4 (backend keep-alive timing) is closed: it does not matter |
| 12 | **T-122 exception**: ping wakeups reset the 600 s watchdog, so an h2 client connection is never idle-cut while its upstream h2 connection is open | Watchdog: `m/proxy/server.py:50-76` (fires only if `last_activity + timeout < now`, `:72`), one per client connection (`:116-120`, `tcp_timeout` 600, `m/options.py:240-247`). `server_event` calls `register_activity()` before handling **any** event (`:387`). Wakeups: `RequestWakeup` → task (`:402-410`) → `wakeup()` → `server_event(events.Wakeup(...))` (`:267-272`). `Wakeup` is a `CommandCompleted` (`m/proxy/events.py:133-138`), routed back to the requesting layer (`__init__.py:968-970`), so `Http2Client` re-arms after every wakeup (`_http2.py:558-561`). After `close_connection` the layer becomes `done`, which swallows the `Wakeup` without re-arming (`_http2.py:324-337`). **Scope refinement:** r5 §A.5 said every h2 client connection has an h2 upstream. That holds when the eager upstream TLS succeeds (`m/addons/tlsconfig.py:232-236` sets `establish_server_tls_first`; `alpn_select_callback` returns `server_alpn`, `:118-119`). If upstream TLS fails, mitmproxy proceeds with the client anyway (`m/proxy/layers/tls.py:606-619`), `server_alpn` is `None`, and the callback picks from the client's own offer (`tlsconfig.py:124-128`). Such an h2 client connection has no `Http2Client` until a later flow opens one, and the 600 s cut applies meanwhile. (If the TCP connect fails, the CONNECT gets a 502 and no TLS follows, `__init__.py:786-798`) | **confirmed + scope refinement** (edge case; no value or class change) |
| 13 | **CONV-ABS-85**: every corrected "no HTTP/2" statement (r5 §A.4) | Each row of r5 §A.4 re-checked against the r1-r4 lines it cites: r4 l.16-17, 89, 105, 110, 134-135, 149, 179, 222-223 and 241 do rest on "h2 not live" (re-read in r4 this round), and r3 l.215 (T-124 row "NC, only if hylo speaks h2 upstream") is the source of the HY-PROTO-1 wording issue. The h2 sites are reachable from source alone: ALPN mirroring (`tlsconfig.py:322-328`), `Http2Server` and `Http2Client` selection (`__init__.py:956-957, 1004-1007, 1204-1205`) | **confirmed**. Production counts (7,566 flows) were not re-counted; logs are not an authorized source here |
| 14 | **CONV-ABS-86**: T-136 key = CN/SANs plus the CONNECT authority, not the resolved IP | `__init__.py:779` sets `server.address = (flow.request.host, flow.request.port)` (CONNECT authority); `server.py:212-215` resolves it inside `asyncio.open_connection`, and the resolved IP goes only to `peername` (`:241`); `tlsconfig.py:671-672` appends `server.address[0]`; `:675` deduplicates; `m/certs.py:788-798, 815` stores under `(commonname, sans)` only. **Refinement:** `organization` and `crl_url` are passed to `dummy_cert` (`certs.py:803-810`) but are **not** part of the key, so the first leaf minted for a given CN/SAN set is reused even if a later upstream certificate has a different organization or CRL point | **confirmed + refinement** |
| 15 | **CONV-ABS-87**: no end-to-end h2 backpressure; unbounded per-stream queue | `_http_h2.py:48, 58` (`defaultdict(collections.deque)`, no `maxlen`); `:92-105` (append when the stream already has buffered data or the window is short). Queued data is not on the transport, so `drain_writers` (`server.py:296-297, 330-342`) does not wait for it. Receive side: immediate `acknowledge_received_data` (`_http2.py:238-240`) with 2³¹ − 1 windows (T-140, T-141) | **confirmed** |
| 16 | r5 §A.3 `dumper.py:184-193` wording: the ` HTTP/2.0` suffix "is also printed when request and response versions differ, which is why the 2 h2 → h1 rerouted flows show it" | `m/addons/dumper.py:184-191`: the suffix is printed if the request is **not** HTTP/1.0 or 1.1, **or** if request and response versions differ. A rerouted h2 flow meets the first condition by itself (its request stays `HTTP/2.0`) | **wording precision**: they show it because the request is h2; the version-mismatch clause is not needed |

### A.2 Retractions this round

| Marker | Claim | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-93** | pass-4 r5 §A.3 T-137 row and §C.1 T-137: a 6th concurrent rewritten h2 stream "waits, and keeps waiting until the backend closes an idle keep-alive. That backend timing was not verified"; r5 Remaining Gap 4 | mitmproxy closes each h1 upstream connection after one h2-originated flow (`_http1.py:200-209`). A permit is therefore released when its flow completes. The 6th stream waits for the first of the 5 in-flight rewritten flows to finish. Backend keep-alive timing plays no part. The row's class (N/A), value (5) and hylo disposition are unchanged | §A.1 row 11 |
| **CONV-ABS-94** | pass-4 r5 §A.3 T-142 row: "h2 library default inbound cap would be 2²⁴ (`h2/connection.py:311`, default not used)" | `DEFAULT_MAX_INBOUND_FRAME_SIZE` is dead (defined, never used). The h2 library's effective inbound default is 16,384 B (`local_settings.max_frame_size`, `h2/connection.py:377`). T-142's operative value, 2¹⁷, is unchanged | §A.1 row 4 |

Neither retraction changes a threshold value, class, key, rationale status or owner item. Both correct a stated fact inside an existing row.

---

## B. Target B: Go `net/http` HTTP/2 negotiation facts for OD-94 (Go 1.26.5 source)

### B.1 What decides the protocol on hylo's client-facing leg

hylo's listener is an HTTP CONNECT proxy that terminates TLS itself on each tunnelled connection (the mitmproxy pattern). On that leg, the
negotiated protocol is set by the `tls.Config.NextProtos` that hylo passes to `tls.Server`, and by `crypto/tls`:

| Fact | Go source |
|---|---|
| ALPN picks the **server's** preference order: the first server protocol that the client also offers | `go/src/crypto/tls/handshake_server.go:342-347` |
| A client that offers `http/1.1` (and not `h2`) against a server list holding only `h2` connects with **no** protocol (special case, Issue 46310) | `handshake_server.go:348-358` |
| No overlap otherwise → handshake fails with alert `no_application_protocol` | `handshake_server.go:269-272, 360`; TLS 1.3 `handshake_server_tls13.go:260-263` |
| An empty server or client list → success with an empty `NegotiatedProtocol` | `handshake_server.go:335-341`; doc `common.go:684-690` |

**Legacy contrast (parity note):** mitmproxy does not pick from its own list. It offers the client's list upstream and then gives the client
whatever the upstream server chose (`tlsconfig.py:108-123, 322-328`). Go picks server-first. For Claude Code, which offers only `http/1.1`, the
result is the same (`http/1.1`) under either option.

### B.2 `http.Server`: when h2 is automatic, and how to turn it off

| Fact | Go source |
|---|---|
| `Server.protocols()`: if `Server.Protocols` is non-nil, it is used as is. Otherwise HTTP/1 is always on, and HTTP/2 is on **unless** `TLSNextProto` is a non-nil map without an `"h2"` key, or `GODEBUG=http2server=0` and there is no `"h2"` key | `go/src/net/http/server.go:3506-3529` |
| Field docs: `Protocols` "If Protocols is nil, the default is usually HTTP/1 and HTTP/2. If TLSNextProto is non-nil and does not contain an "h2" entry, the default is HTTP/1 only"; `TLSNextProto` "If TLSNextProto is not nil, HTTP/2 support is not enabled automatically … The Server.Protocols field now provides a simpler way" | `server.go:3066-3075`; `server.go:3024-3036` |
| `ServeTLS` / `ListenAndServeTLS` **always** run the HTTP/2 setup, then rewrite a **clone** of `TLSConfig.NextProtos` to match `protocols()` (`adjustNextProtos` adds `h2`, then `http/1.1`, or removes them) | `server.go:3482-3503, 3703-3720, 3725-3727, 3533-3563` |
| `Serve(l)` (the call used when hylo hands in its own `*tls.Conn`s) sets up HTTP/2 only if `s.TLSConfig == nil`, or `UnencryptedHTTP2` is enabled, or `s.TLSConfig.NextProtos` contains `"h2"` | `server.go:3404-3415, 3738-3740, 3743-3747, 3367-3388`; doc `:3398-3400` |
| Setup itself (`onceSetNextProtoDefaults`) does nothing if `protocols()` has no HTTP/2, if `GODEBUG=http2server=0`, or if `TLSNextProto["h2"]` already exists; otherwise it installs the bundled h2 server. The bundled `ConfigureServer` appends `h2` and `http/1.1` to `s.TLSConfig.NextProtos` and creates `TLSNextProto` | `server.go:3754-3774`; `h2_bundle.go:4274-4285` |
| **Dispatch trap:** on a `*tls.Conn`, after the handshake, any negotiated protocol other than `""`, `http/1.1`, `http/1.0` is handed to `TLSNextProto[proto]`. If no handler exists, the connection is **closed** (`return`) with **no** fallback to HTTP/1 | `server.go:1924, 1951-1963`; `validNextProto` `:1813-1822` |
| Build tag `nethttpomithttp2` removes the bundled h2 entirely | `omithttp2.go:5, 16`; checked at `server.go:3755`, `transport.go:431` |
| `GODEBUG` names `http2server` and `http2client` have no version-gated default (no `Changed:` field), so the `go` line in `go.mod` does not change them | `go/src/internal/godebugs/table.go:44, 46` |
| Default request-head limit `DefaultMaxHeaderBytes = 1 << 20` (1 MiB) when `MaxHeaderBytes` is 0 | `server.go:892-902, 3017-3022` |

### B.3 `http.Transport`: when h2 is automatic, and how to turn it off

| Fact | Go source |
|---|---|
| `Transport.protocols()`: `Protocols` non-nil → used. Else HTTP/1 on, and HTTP/2 on **only if**: `TLSNextProto` is non-nil **and** holds an `"h2"` entry; or `TLSNextProto` is nil, and (`ForceAttemptHTTP2` is true **or** none of `TLSClientConfig`, `Dial`, `DialContext`, `DialTLS`, `DialTLSContext` is set), and `GODEBUG=http2client` is not `0` | `go/src/net/http/transport.go:464-489`, `hasCustomTLSDialer` `:393-395` |
| Consequence: a zero-value `&http.Transport{}` **does** negotiate h2 (switch default, `:485-486`), although the field doc says "If Protocols is nil, the default is usually HTTP/1 only" (`:309-311`). Setting `TLSClientConfig` or a custom dialer (common in a MITM proxy) turns h2 off unless `ForceAttemptHTTP2` is set | `transport.go:477-486` vs doc `:304-312` |
| `DefaultTransport` has `ForceAttemptHTTP2: true` → h2 with any HTTPS upstream that offers it. `Clone()` first runs the h2 setup on the source and copies `ForceAttemptHTTP2` | `transport.go:46-57, 337-358` |
| Setup (`onceSetNextProtoDefaults`) returns at once under `GODEBUG=http2client=0`, **even when `Protocols` asks for HTTP/2** (`:403-406` is checked before `protocols()` at `:427`). It also returns if `TLSNextProto["h2"]` exists or `protocols()` has no HTTP/2; otherwise it installs the bundled h2 transport and adjusts `TLSClientConfig.NextProtos` | `transport.go:401-462` |
| h2 is negotiated only over TLS. An `http://` upstream (legacy's DGX backend lane is plain HTTP) uses HTTP/1.1 unless `Protocols` holds `UnencryptedHTTP2` **and not** HTTP1 | `transport.go:304-308`; `http.go:19-38` |
| Default response-head limit 10 MiB when `MaxResponseHeaderBytes` is 0 | `transport.go:329-334` |

### B.4 What this means for each OD-94 option

**Option (a): HTTP/1.1 only (the recommendation).** It needs settings on **both** legs. Neither leg gets them from defaults:
1. **Listener:** hylo's per-tunnel `tls.Config.NextProtos = []string{"http/1.1"}`. Effect: a client that offers `h2,http/1.1` gets `http/1.1`; a
   client that offers only `h2` gets `no_application_protocol` (B.1). Also set `Server.Protocols` to HTTP1 only (or `TLSNextProto` to an empty
   non-nil map). The `tls.Config` alone decides ALPN, but this keeps a stray `h2` from being accepted if someone later adds it to `NextProtos`.
   Without a handler, an `h2` negotiation is a silent close (`server.go:1953-1963`); with one, it is served as h2.
2. **Upstream Anthropic leg:** set `Transport.Protocols` to HTTP1 only. **New fact this round:** if hylo builds its transport from
   `http.DefaultTransport.Clone()`, or uses a bare `&http.Transport{}`, Go negotiates **h2 with `api.anthropic.com`** even though Claude Code
   speaks h1. That breaks HY-PROTO-1's mirroring (legacy upstream = h1 for Claude Code, because the upstream offer is the client's offer). Legacy
   parity therefore requires an explicit HTTP/1-only transport even under option (a).
3. **Backend leg (plain `http://`):** HTTP/1.1 by default (B.3). No action needed beyond not enabling `UnencryptedHTTP2`.
4. A process-wide `GODEBUG=http2server=0,http2client=0` (env or `//go:debug` directive) also works, but it is global and invisible in the code.
   The explicit `Protocols` fields are the clearer choice. `Server.Protocols` and `Transport.Protocols` both exist in Go 1.26.5 (`server.go:3075`,
   `transport.go:312`), which is within hylo's Go ≥ 1.26 floor.
5. Test: assert `ConnectionState().NegotiatedProtocol` on both legs (`http/1.1` for a Claude Code-like ClientHello offering `http/1.1`; handshake
   failure for an `h2`-only offer).

**Option (b): mirror h2 as legacy does.** Go does not mirror; the listener picks server-first (B.1). To mirror, hylo would have to look at the
ClientHello (`tls.Config.GetConfigForClient`), connect upstream first with the client's offer, and then build a per-connection `NextProtos` from
the upstream's choice, the way mitmproxy does. The bundled h2 server's defaults then differ from every legacy h2 row, so each one needs an
explicit setting to reach parity:

| Legacy row | Legacy value | Go bundled h2 default | Go source |
|---|---|---|---|
| T-145 max concurrent streams (client leg) | 100 | 250 | `h2_bundle.go:4042, 1120` |
| T-142 max frame size | 2¹⁷ | 1 MiB (`MaxReadFrameSize`) | `h2_bundle.go:3531, 1133` |
| T-140/T-141 receive windows | 2³¹ − 1 | server 1 MiB per connection and per stream; transport 1 GiB / 4 MiB | `h2_bundle.go:1123-1132, 7334, 7339` |
| T-124 keep-alive PING | 58 s idle (upstream only) | none unless `ReadIdleTimeout` (`SendPingTimeout`) is set; ping-ack timeout 15 s | `h2_bundle.go:1074, 1093, 1134, 4953-4955` |
| T-146 max header list | 65,536 B | `MaxHeaderBytes` + 320 (10 headers × 32) on the server | `h2_bundle.go:1139-1145, 4640` |
| T-143 provisional streams | 10 | transport `initialMaxConcurrentStreams` 100 | `h2_bundle.go:7346` |

So (b) is not "free parity". It means a mirroring handshake plus about six explicit h2 settings, and the idle-timer change of r5 §A.5. This
supports the existing recommendation (a). OD-94's question and options are unchanged; this annex replaces r5's "Not verified (Go stdlib is not
an authorized source)" note.

**Also settled:** r4's T-139 note "Go `http.Server.MaxHeaderBytes` defaults to 1 MiB" is now verified (`server.go:892-902`).

---

## C. Target C: catalogue totals

No threshold row was added, removed or reclassified. Two rows change text only:

| T | Change | Last |
|---|---|---|
| 137 | wait-duration text: "a 6th concurrent rewritten stream waits until one of the 5 in-flight rewritten flows completes (mitmproxy closes each h1 upstream connection after one h2-originated flow, `m/proxy/layers/http/_http1.py:200-209`)". Site adds `_http1.py:200-209`. Class N/A, value 5, key unchanged | **R6** |
| 142 | drop the "2²⁴" parenthetical; the library default is 16,384 B (`h2/connection.py:377, 1516`); `:311` is a dead constant. Value 2¹⁷, class NC unchanged | **R6** |

Text-only refinements (no row edit needed): T-122 scope (an h2 client connection with no h2 upstream after an upstream TLS failure is still
idle-cut), T-136 (organization and CRL URL are not part of the key), T-143 (effectively unbounded after SETTINGS without
`MAX_CONCURRENT_STREAMS`), and the two-GOAWAY precision for the connection-fatal h2 errors.

**Final totals (unchanged from r5):**

| Measure | r5 | **r6** |
|---|---|---|
| Thresholds | 147 | **147** (broad 105 + r1 30 + r3 3 + r4 1 + r5 8) |
| By class | CFG 96 · NC 37 · DROP 7 · OOS 2 · EXT 2 · NEW-H 2 · N/A 1 | **unchanged** |
| By rationale | OWNER 27 · Dv† 18 · N/A 8 · EXT 2 · resolved 92 | **unchanged** |
| Rationale resolved | 120 of 147 | **120 of 147** (102 final + 18 awaiting one bulk "yes") |
| Owner must supply | 27 in 7 groups | **unchanged** |
| OD-94 sensitivity | (a): T-124, T-140..T-147 → N/A (NC 28 · N/A 10); (b): T-124 → CFG (CFG 97 · NC 36) | **unchanged** |
| Last changed in R6 | — | 2 rows (T-137, T-142), text only |

OD-57 lists (r3 §C.6): unchanged.

NFR catalogue (r3 §E, r4 §D, r5 §D): P-7 adds "T-137 permits are released per completed flow for h2 → h1". The missing-NFR entry "hylo listener
protocol posture" (r5 §D) adds: Go defaults would negotiate h2 on the upstream Anthropic leg with `DefaultTransport`, so the posture must be set
on **both** legs (§B.4). No other change.

---

## Delta Summary

- **Target A:** 16 items re-verified from fresh reads of mitmproxy, h2 and hpack. **Confirmed:** T-124, T-140, T-141, T-143, T-144, T-145,
  T-146, T-147, T-122's ping exception, CONV-ABS-85, CONV-ABS-86 and CONV-ABS-87. **Retracted, 2:** CONV-ABS-93 (T-137's "waits until the
  backend closes an idle keep-alive": mitmproxy closes each h2-originated h1 upstream connection itself after one flow) and CONV-ABS-94 (T-142's
  "library default 2²⁴": that constant is dead; the real default is 16,384 B). **Refined, 5:** T-122 scope (upstream-TLS-failure edge), T-136
  (organization and CRL point not in the key), T-143 (unbounded after SETTINGS without a stream cap), the two-GOAWAY precision, and the dumper
  wording.
- **Target B:** the Go 1.26.5 facts for OD-94, with file:line, for the server, the transport, crypto/tls ALPN, GODEBUG and the build tag. The new
  decision-relevant fact: `DefaultTransport`, its clones and a bare `Transport{}` negotiate h2 upstream. Option (a) therefore needs an explicit
  HTTP/1-only setting on the **upstream** leg too, not only on the listener, or the Anthropic leg breaks HY-PROTO-1's h1 ↔ h1. Option (b) needs a
  mirroring handshake and about six explicit h2 settings (§B.4 table). r4's 1 MiB `MaxHeaderBytes` note is now verified.
- **Target C:** totals unchanged: 147 rows, CFG 96 · NC 37, resolved 120 of 147. 2 rows changed text only.
- New items: 0 threshold rows, 0 owner items (OD-102..OD-105 unused). Retractions: CONV-ABS-93, -94 (95, 96 unused).

## Remaining Gaps (verbatim-carryable)

1. Owner answers for OD-57 (18 bulk Dv† rows; 27 owner rationales in 7 groups, r3 §C.6) and for **OD-94** (h1-only versus h2 mirroring). §B.4
   gives the Go facts for both options.
2. The Go facts are from source reading only. Nothing was compiled or run. P1/P3 should pin them with a test that asserts the negotiated ALPN
   on the listener and on the upstream transport.
3. The pseudo-terminal-close-as-hangup step of R-12 is still the one link that the authorized man pages do not state (r5 §B.2).
4. The P2r8 counts (57 idle closes and their ALPN split; 7,566 h2 flows) were not re-counted. Logs are not an authorized source for this pass.
5. Carried: the T-078 port-allocation source is unverified; the asyncio values in r4 §B.4 are CPython 3.11's; P1/P3 boundary table tests
   (`SL:674`, `cols > 0`, T-090..T-092).
6. Closed this round: r5 gap 2 (Go stdlib, §B) and r5 gap 4 (backend keep-alive timing; irrelevant after CONV-ABS-93).

## Novelty Assessment

Novelty: SUBSTANTIVE

Most of this round is confirmation: 13 of the 16 items checked survive fresh reads (9 unchanged, 4 with refinements), and the Go facts inform OD-94 without changing legacy
behavior. Under the strict rule, though, any retraction is substantive, and this round makes two. CONV-ABS-93 corrects how long a T-137 waiter
waits (until a flow completes, not until the backend drops an idle connection) and removes a stated open gap. CONV-ABS-94 corrects a stated
library value (16,384 B, not 2²⁴). Neither changes a threshold's value, class or key, and the totals are unchanged, so the model is close to
converged. One Go fact also matters for the spec: option (a) needs an HTTP/1-only upstream transport as well as an HTTP/1-only listener. That
informs the decision and changes no legacy fact.

## Convergence Declaration

Another round needed: two retractions (CONV-ABS-93, -94) under the strict-binary rule. They are narrow: text in T-137 and T-142, no value,
class, key or total changes. A round 7 that re-reads `_http1.py:171-215` and `h2/connection.py:305-397, 1505-1533` and finds nothing new should
close pass 4 as NITPICK.

## State Checkpoint

```yaml
pass: 4
round: 6
status: complete
timestamp: 2026-11-14T13:30:00Z
novelty: SUBSTANTIVE
files_scanned: mitmproxy 12.3.1 options.py, http.py, certs.py, addons/{tlsconfig,dumper,proxyserver}.py, proxy/{server,events,commands}.py, proxy/layers/tls.py, proxy/layers/http/{__init__,_http1,_http2,_http_h2}.py, net/http/http1/read.py; h2 4.4.1 connection.py, exceptions.py, settings.py, frame_buffer.py; hpack 4.2.0 hpack.py; Go 1.26.5 src/net/http/{server,transport,http,h2_bundle,omithttp2}.go, src/crypto/tls/{handshake_server,handshake_server_tls13,common}.go, src/internal/godebugs/table.go; legacy PX:100-163 (grep); pass-4 deep r3 (C), r4, r5
verification: {items: 16, confirmed: 9, confirmed_with_refinement_or_precision: 4, retracted: 2 (CONV-ABS-93 T-137 wait duration, CONV-ABS-94 T-142 h2 default), wording: 1}
go_h2_facts: {server_auto_h2: "Protocols nil and TLSNextProto nil and GODEBUG http2server!=0; ServeTLS always, Serve only if TLSConfig nil or NextProtos has h2", server_disable: [Server.Protocols HTTP1-only, TLSNextProto empty non-nil map, GODEBUG http2server=0, tag nethttpomithttp2], server_trap: "negotiated h2 without TLSNextProto handler closes the conn", transport_auto_h2: "Protocols nil: TLSNextProto has h2, or (ForceAttemptHTTP2 or no custom TLSClientConfig/dialer) and http2client!=0; DefaultTransport ForceAttemptHTTP2=true", transport_disable: [Transport.Protocols HTTP1-only, TLSNextProto empty non-nil map, custom TLSClientConfig/dialer without ForceAttemptHTTP2, GODEBUG http2client=0], alpn: "server preference; h2-only client vs http/1.1-only server -> no_application_protocol"}
thresholds: {total: 147, new_this_round: 0, text_changed: [T-137, T-142], by_class: {CFG: 96, NC: 37, DROP: 7, OOS: 2, EXT: 2, NEW-H: 2, NA: 1}, resolved: 120}
retractions: [CONV-ABS-93, CONV-ABS-94]
conv_abs_unused: [95, 96]
new_owner_items: []
od_unused: [OD-102, OD-103, OD-104, OD-105]
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r6/ (empty; all evidence is direct reads)
next: pass 4 round 7 (confirm CONV-ABS-93/94 sites; expect NITPICK)
```
