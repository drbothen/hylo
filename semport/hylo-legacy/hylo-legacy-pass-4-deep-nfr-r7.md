# Pass 4 Deepening — Round 7: verification of round 6; FINAL consolidated pass-4 catalogue — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/`, read-only and static. Nothing in `legacy/` was imported, executed or modified. No proxy, nothing
  networked, no socket binds, no DNS lookups. CLAUDE.local.md was not read. No git commit.
- `legacy/` is unchanged since every pass-4 round: its last commit is `220e96c` (2026-11-13 22:18 -0600, removal of the visible-mode router), and
  `git status` shows no local edits under `legacy/`. Ten legacy anchors were re-printed this round as a drift check (SL:74-85, 99-100, 350, 1153;
  PX:287, 291-295, 322, 368, 408, 564, 692; HK:33-36, 133, 179, 190, 236; EX:24-25; PF:23; L:20-21, 104, 158, 161, 176). All match the catalogue.
- Authorized read-only references, all read fresh this round:
  - `m/` = mitmproxy 12.3.1 (`m/version.py:5` `VERSION = "12.3.1"`), `h2/` 4.4.1, `hpack/` 4.2.0 (`h2-4.4.1.dist-info`, `hpack-4.2.0.dist-info`)
    under `$PROTOTYPE/.mitmenv/lib/python3.12/site-packages/`.
  - `go/` = Go 1.26.5 stdlib (`go env GOROOT` = `/opt/homebrew/Cellar/go/1.26.5/libexec`, `VERSION` "go1.26.5"). Nothing compiled or run.
- Inputs read: pass-4 deep r6 (complete), r5 (complete), r4 (complete), r3 (complete, including §C catalogue, §C.6 OD-57, §D, §E NFRs).
  **Pass-5 deep r5 does not exist** at the time of writing (`ls` of the semport directory shows pass-5 deep r1-r4 only), so it was neither read nor
  edited. No sibling file was edited.
- Scratch directory `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r7/` was created and is
  empty: every fact below comes from a direct read.
- Numbering: **no retraction** this round (CONV-ABS-101..104 unused). **No new owner item** (OD-110..OD-113 unused). No new threshold row.

Abbreviations: `SL` status line (`dgx_statusline.py`), `PX` proxy addon (`dgx_proxy.py`), `EX` exporter (`dgx_ledger_exporter.py`), `HK` hook
(`auto_continue.py`), `PF` preflight (`dgx_preflight.py`), `BF` backfill (`tools/backfill_cost_history.py`), `L` launcher (`claude-dgx`), `CO`
coordinator (`dgx-proxy-coordinator.sh`), `pl-ex` / `pl-tu` exporter / tunnel plists (`deploy/`). Rationale codes: **M** measured, **DOC**
written in source or docs, **J** labeled judgment call, **C** convention or tool default, **Dv** derived (structural, no sign-off needed),
**Dv†** derived by these passes (owner bulk-confirms), **OWNER-x** owner supplies (group x of §B.4), **N/A** dead, dropped or an absent limit,
**EXT** a Claude Code constant.

---

## A. Target A: independent re-verification of round 6 (fresh reads)

### A.1 Verification table

| # | Round-6 item | Fresh evidence (this round) | Verdict |
|---|---|---|---|
| 1 | **CONV-ABS-93** (T-137): when an h2 client is rerouted to an HTTP/1.1 upstream, mitmproxy closes each upstream connection after one flow, so a 6th concurrent rewritten stream waits for one of the 5 in-flight flows to **complete** | `m/proxy/layers/http/_http1.py:200-209`: comment "If we proxy HTTP/2 to HTTP/1, we only use upstream connections for one request … we can rely on the proxyserver's max-connection-per-server throttling" (`:200-202`); `connection_done` includes `(self.request.is_http2 or self.request.is_http3) and isinstance(self, Http1Client)` (`:203-206`); then `CloseConnection(self.conn)` and `state = done` (`:208-210`). This runs in `mark_done` only once **both** request and response are done (`:178`). `self.request` is the original request object (`:357`); the HTTP/1.1 copy at `:362-370` is a local used for the head. `is_http2` = `http_version == b"HTTP/2.0"` (`m/http.py:284-285`). Legacy never writes `http_version`: 0 matches in `PX`; the reroute writes only `scheme`, `host`, `port` (`PX:161-163`). Permit side: `m/proxy/server.py:109` (Semaphore(5) per client connection), `:206` `async with` spans the connect and `await self.handle_connection(...)` (`:258-259`) and its `finally` (`:260-265`), so the permit is freed when the closed upstream connection's handler returns. One connection per flow: `m/proxy/layers/http/__init__.py:1087-1097` (no reuse when `client.alpn == b"h2"` and the upstream is not h2) and `:1178-1188` (each queued waiter gets its own connection) | **confirmed**. Precision (no row change): the condition also covers `is_http3`; the permit is released after the `server_disconnected` hook, which legacy does not register (`PX:524-548` hook list) |
| 2 | **CONV-ABS-94** (T-142): `DEFAULT_MAX_INBOUND_FRAME_SIZE` is unused; the h2 library's effective default is 16,384 B | Recursive search of the **whole** venv `site-packages` for `DEFAULT_MAX_INBOUND_FRAME_SIZE`: one hit, its definition `h2/connection.py:311`. `max_inbound_frame_size` occurs only at `h2/connection.py:377` (initialised from `local_settings.max_frame_size`), `:1516` (copied into `incoming_buffer.max_frame_size` on every `receive_data`), `:2005` (updated on SETTINGS ACK), and `m/proxy/layers/http/_http_h2.py:55` (mitmproxy sets 2¹⁷). Library default `MAX_FRAME_SIZE` = 16384: `h2/settings.py:141`. `FrameBuffer` starts at 0 (`h2/frame_buffer.py:39`) but `:1516` overwrites it before any frame is parsed; the check is `length > max_frame_size` → `FrameTooLargeError` (`frame_buffer.py:70-72`). mitmproxy also sets the advertised value and acknowledges at once (`_http_h2.py:54, 57`) | **confirmed** |
| 3 | **T-143 refinement**: after the server's first SETTINGS, a SETTINGS frame without `MAX_CONCURRENT_STREAMS` leaves the cap at 2³² + 1 (effectively unbounded) | `h2/settings.py:226-231` returns `self.get(MAX_CONCURRENT_STREAMS, 2**32+1)`. `m/proxy/layers/http/_http2.py:512-515` compares `open_outbound_streams >=` (`provisional_max_concurrency or remote_settings.max_concurrent_streams`); `:631-634` sets the provisional value to `None` on `RemoteSettingsChanged`; the provisional value is 10 (`:489`) | **confirmed** |
| 4 | **T-122 edge case**: if the eager upstream TLS handshake fails, an h2 client connection has no upstream `Http2Client`, so the 600 s idle cut applies until a flow opens one | Eager upstream TLS first: `m/addons/tlsconfig.py:232-236`. On failure mitmproxy logs "Trying to establish … with client anyway" and proceeds (`m/proxy/layers/tls.py:606-619`). `server.alpn` is assigned only after a successful handshake (`tls.py:380`), so `server_alpn` in the app data is `None` (`tlsconfig.py:296`); `client_alpn` is `client.alpn` (None) for a CONNECT tunnel (`:285-291`; the forced `http/1.1` applies only to TLS-to-the-proxy, `len(layers) == 2`). `alpn_select_callback` then skips `:113-123` and picks the first offer in `HTTP_ALPNS` (`:124-128`), which includes `h2` when the `http2` option is on (`tls.py:161, 164`). Without an `Http2Client` no ping wakeups are scheduled (`_http2.py:565-567` runs only in `Http2Client`), so the watchdog (`m/proxy/server.py:50-76`, `register_activity` per event at `:387`, `tcp_timeout` 600 at `m/options.py:240-247`) can fire | **confirmed** |
| 5 | **Double GOAWAY** on connection-fatal h2 errors: h2 queues a GOAWAY with the exception's own code, then mitmproxy queues a second with `PROTOCOL_ERROR` | `h2/connection.py:1525-1531` catches `ProtocolError` and calls `_terminate_connection(e.error_code)` (`:1584-1593`: `GoAwayFrame`, `SEND_GOAWAY`, `_prepare_for_sending`). Codes: `FRAME_SIZE_ERROR` (`h2/exceptions.py:27-33`), `ENHANCE_YOUR_CALM` for `DenialOfServiceError` (`:182-194`), `PROTOCOL_ERROR` for `TooManyStreamsError` (inherits `:24`; class at `:47`). `TooManyStreamsError` (`h2/connection.py:1601-1606`) is not caught by `_receive_frame` (`:1535-1580` catches only `StreamClosedError` and `StreamIDTooLowError`), so it reaches `:1525`. mitmproxy: `_http2.py:205-206` turns the exception into an event; `:275-277` → `protocol_error` (`:314-322`), which calls h2's `close_connection(PROTOCOL_ERROR)` (`h2/connection.py:1078-1110`, `SEND_GOAWAY` at `:1097`, legal from `CLOSED` per `:244`) and flushes **both** queued frames with one `data_to_send()` (`_http2.py:321`), then fails every tracked stream (`:324-333`) | **confirmed** |
| 6 | Go `server.go:3506-3529` (`Server.protocols()`) | Read: `Protocols` non-nil → used (`:3507-3508`); `TLSNextProto` non-nil without `"h2"` disables h2 (`:3513-3514`); `GODEBUG http2server=0` without `"h2"` disables it (`:3519-3521`); HTTP/1 always on (`:3524`) | **confirmed** |
| 7 | Go `server.go:1951-1963` (dispatch trap) | `NegotiatedProtocol` passes `validNextProto` (`:1816-1821`: everything except `""`, `http/1.1`, `http/1.0`) → `TLSNextProto[proto]` called if present (`:1954-1961`); `return` at `:1962` either way, i.e. a negotiated `h2` with no handler closes the connection | **confirmed** |
| 8 | Go `transport.go:464-489` (`Transport.protocols()`) | `Protocols` non-nil → used; `TLSNextProto` non-nil → h2 only with an `"h2"` entry (`:471-476`); no h2 if `!ForceAttemptHTTP2` and any of `TLSClientConfig`, `Dial`, `DialContext`, custom TLS dialer is set (`:477-483`); none under `http2client=0` (`:484`); otherwise h2 (`:485-486`). Field doc "usually HTTP/1 only" at `:309-311`. `DefaultTransport` sets `DialContext` **and** `ForceAttemptHTTP2: true` (`:46-57`) | **confirmed** |
| 9 | Go `transport.go:403-406` (GODEBUG checked before `protocols()`) | `onceSetNextProtoDefaults` returns at `:403-406` under `http2client=0`; `protocols()` is consulted later at `:427` | **confirmed** |
| 10 | Go `h2_bundle.go` defaults: max concurrent streams 250 | `:4042` `http2defaultMaxStreams = 250`; applied by `http2setConfigDefaults` `:1120` | **confirmed** |
| 11 | Go `h2_bundle.go` defaults: max read frame 1 MiB | `:3531` `http2defaultMaxReadFrameSize = 1 << 20`; applied `:1133` | **confirmed** |
| 12 | Go `h2_bundle.go` defaults: windows, ping, header list, provisional streams (extra spot checks) | Server windows 1 MiB per connection and per stream (`:1123-1132`); transport `1 << 30` / `4 << 20` (`:7334`, `:7339`); `PingTimeout` 15 s (`:1134`); `SendPingTimeout` from `ReadIdleTimeout` (`:1074`, `:1093`), timer armed only if `> 0` (`:4953-4955`); header list = `MaxHeaderBytes` + 10 × 32 (`:1139-1145`, `:4640`); transport `initialMaxConcurrentStreams = 100` (`:7346`). Also `Serve(l)` runs h2 setup only via `shouldConfigureHTTP2ForServe` (`server.go:3413, 3738-3746`) | **confirmed** |

Every round-6 claim survives. Twelve items checked: 12 confirmed, 0 retracted, 2 precisions (row 1) that change no row.

### A.2 Retractions this round

None. CONV-ABS-101..104 unused.

---

## B. Target B: FINAL consolidated pass-4 catalogue (self-contained; supersedes r3 §C, r3 §E and the r4-r6 deltas)

### B.1 Conventions

- **Class (D15):** **CFG** config key, default = legacy value; **NC** named constant (D15 exception; reason in the Key column); **DROP** not
  carried into hylo; **OOS** legacy deployment, not a hylo key; **EXT** Claude Code constant; **NEW-H** hylo key with no legacy value (deviation
  approved elsewhere); **N/A** absent from hylo by construction. Rows that split into a CFG part and an NC part are counted once as CFG.
- **Op:** the comparison exactly as the source writes it. Parity (D4) keeps it unchanged and each key's comment states it.
- **Key naming:** `HYLO_` + upper snake case of the key for the env form (pending OD-01; table approval under pass-5 OD-74). Units use the legacy
  unit (`_s`, `_ms`, `_bytes`, `_chars`, `_pct`, `_w`).
- **Last:** the round whose finding last changed the row's content: B (broad), R1..R6. R7 changed no row. Where r6 recorded a refinement as a
  note "without a row edit" (T-122, T-136, T-143), this catalogue folds the note into the row and marks it **R6**, because the content is r6's.

### B.2 Threshold table (147 rows)

#### B.2.1 Status line (`internal/statusline`, P1) — 79 rows

| T | Value (op) | Site | Class | Rat. | Rationale | Key / NC reason | Last |
|---|---|---|---|---|---|---|---|
| 001 | 4 s (reuse while `fetch_ts > now−TTL`) | SL:74,324 | CFG | DOC | "match refreshInterval" (SL:50; WIDGETS Tunables) | `statusline.telemetry.ttl_s` | B |
| 002 | 2 | SL:75 | CFG | C | two-row design | `statusline.rows` | B |
| 003 | 15 s (`age > STALE_OK` → stale) | SL:79,697 | CFG | Dv† | one VM scrape interval (review #16.1); effective only when `ttl_s > 15` (F-1, OD-55) | `statusline.telemetry.fresh_s` | R1 |
| 004 | 300 s (`age < KEEP_DEAD`) | SL:80,357 | CFG | OWNER-A | ladder stated (SL:34-38), value not | `statusline.telemetry.keep_dead_s` | R1 |
| 005 | 1.5 s per socket op | SL:81,170 | CFG | Dv† | ≈ 60 × the measured ~25 ms RTT (SL:81); no-dribble bound 3 s < 4 s tick | `statusline.telemetry.timeout_s` (semantics OD-56) | R2 |
| 006 | 12 points | SL:82,664 | CFG | J | "kept short: long flats read as blobs" | `statusline.sparkline.points` | B |
| 007 | 90 s (`<`) | SL:83,336 | CFG | Dv† | gap pruning (F-4); review #17.2 "~48 s (doc said 90 s)" | `statusline.sparkline.max_age_s` | R2 |
| 008 | 2 s (`>=`) | SL:84,337 | CFG | Dv† | inert at TTL ≥ 2 (F-2) | `statusline.sparkline.min_gap_s` | R1 |
| 009 | 32 | SL:350 | CFG | Dv† | bounds the cache file; inert unless TTL < 2.8125 s (F-3) | `statusline.sparkline.history_cap` | R3 |
| 010 | 1800 s | SL:85 | CFG | OWNER-A | purpose "no blinking", value not | `statusline.limits.keep_s` | R1 |
| 011 | 300 s (`>`) | SL:93,825 | CFG | J | labeled (SL:90-92; review #20.2) | `statusline.idle.after_s` | B |
| 012 | 30.4 MTok/month | SL:98 | CFG | DOC | 1M DGX tokens / 24 h (SL:94-97; review #11.1) | `statusline.cost.basis_min_mtok_month` | B |
| 013 | 5 s | SL:99 | CFG | C | "docs' example pattern" | `statusline.git.ttl_s` | B |
| 014 | 72 cols (`>=` keeps row 2) | SL:100,1224 | CFG | OWNER-B | none | `statusline.narrow_cols` | R1 |
| 015 | 20 | SL:124 | CFG | DOC | below 20 samples p95 = max (SL:124) | `statusline.ttft.min_samples` | B |
| 016 | `[1m]` | SL:118 | CFG | DOC | review #17 A+ (sparkline timescale) | inside `statusline.telemetry.query` (byte-identical default) | R3 |
| 017 | `[30m]` | SL:121 | CFG | DOC | matches `dgx_ttft:p95_30m` (review #18) | inside `statusline.telemetry.query` | R3 |
| 018 | 30 d | SL:218 | CFG | DOC | owner design (review #11 revisit) | `statusline.cost.window_s` | B |
| 019 | $1 (`>=`) | SL:219 | CFG | DOC | DGX p75 $0.13 from probes; "short checks, not work sessions" (SL:213) | `statusline.cost.min_usd` | B |
| 020 | 10 | SL:220 | CFG | DOC | owner decision (review #11 revisit) | `statusline.cost.min_sessions` | B |
| 021 | $25 | SL:221 | CFG | DOC | owner decision (review #11 revisit) | `statusline.cost.cold_yellow_usd` | B |
| 022 | 60 s (`<` skips) | SL:232 | CFG | Dv† | 1 write per 15 refreshes; WIDGETS "repaired by the next minute's write" | `statusline.cost.record_throttle_s` | R1 |
| 023 | 300,000 / 1,800,000 ms | SL:253 | CFG | DOC | "same as the display" / "approximate spans" (SL:214-215) | `statusline.cost.rate_min_api_ms` = `{cc, other}` (H-2) | R2 |
| 024 | p75/p95; index `int(q·(n−1))` | SL:261 | CFG+NC | DOC+C | owner design; "lower" nearest rank, no interpolation | `statusline.cost.percentiles`; index method NC (parity) | R1 |
| 025 | 6 levels | SL:279 | CFG | Dv† | expected depth 2 (SL:269-270) plus margin | `statusline.window_age.max_depth` | R1 |
| 026 | 1 s per `ps` call (total deadline) | SL:281 | CFG | OWNER-G | walk uncached on failure; ≤ 6 s per refresh (CONV-ABS-62) | `statusline.window_age.ps_timeout_s` | R3 |
| 027 | 10 cells, half-up | SL:426 | CFG+NC | DOC | review #5.2 | `statusline.context.cells`; rounding NC | B |
| 028 | 50 (`>`) / 85 (`>=`) | SL:434 | CFG | DOC | review #5.1; SL:430-433 | `statusline.context.plain_max` / `red_from` | B |
| 029 | 1e6 (`>=`) else K | SL:435-436 | CFG | C | SI units | `statusline.units.context` | B |
| 030 | hue 0.22, s 0.85, v 0.80 | SL:146-147 | CFG | OWNER-B | aesthetic | `statusline.theme.heat` | R1 |
| 031 | 5 h / 7 d | SL:501 | CFG | C | Anthropic window definitions | `statusline.limits.windows` | B |
| 032 | `0.10 <= elapsed <= 1.0` | SL:517 | CFG | DOC | "projection is noise" early (review #12 revisit) | `statusline.limits.projection_min_elapsed` | B |
| 033 | `>100` red, `>=80` yellow | SL:519 | CFG | DOC | review #12 revisit | `statusline.limits.projected_bands` | B |
| 034 | `>90` red, `>70` yellow | SL:521 | CFG | DOC | 70 = pace, 90 = throttling imminent (review #12.3) | `statusline.limits.absolute_bands` | B |
| 035 | `rem <= 1.15 × window` | SL:523 | CFG | OWNER-A | none | `statusline.limits.countdown_max_factor` | R1 |
| 036 | 86400 / 3600 / 60 s | SL:524-529 | NC | C | calendar units | NC: a day is a day | B |
| 037 | 10,000 / 1e6 (`>=`) | SL:856-859 | CFG | DOC | keep row 1 narrow (review #8.1) | `statusline.units.lines` | B |
| 038 | `> 60000` ms | SL:540 | CFG | Dv† | `_hm` has minute granularity (SL:546) | `statusline.timer.min_ms` | R1 |
| 039 | `>= 60000` ms | SL:551 | CFG | Dv | as T-038; `>=` observable at `api == 60000`, keep it (D4) | `statusline.timer.api_min_ms` | R2 |
| 040 | `>= 300000` ms | SL:559 | CFG | DOC | owner request (review row 9 revisit; WIDGETS Timer) | `statusline.window_age.min_margin_ms` | R3 |
| 041 | 1440 min (`>=`) | SL:561,828 | NC | C | calendar | NC | B |
| 042 | 1000 / 1e6 (`>=`) | SL:869-873 | CFG | DOC | approved mockup (review #10 revisit) | `statusline.units.tokens` | B |
| 043 | `>= 300000` ms | SL:622 | CFG | DOC | "below that the ratio is noise" | `statusline.cost.burn_min_api_ms` | B |
| 044 | `>= 0.005` | SL:634 | CFG | DOC | "skip sub-half-cent noise" | `statusline.cost.basis_min_shown_usd` | B |
| 045 | k fixed 1.0; floors v 1.0, f 0.1 | SL:648-649 | CFG | DOC | review #17.1 | `statusline.sparkline.scale` (1e-9 fallback = T-114) | R1 |
| 046 | fade 0.55→1.0; RGB (70,170,190), (220,170,60), (140,235,255) | SL:680-689 | CFG | OWNER-B | aesthetic | `statusline.sparkline.colors` | R1 |
| 047 | `q > 0` or preempt `> 0` | SL:740 | CFG | DOC | review #14 | `statusline.queue.yellow` = `{waiting_gt: 0, preempt_rate_gt: 0}` (H-1) | R2 |
| 048 | `ceil(kv/25)`, 4 cells | SL:759 | CFG+NC | DOC | review #15 | `statusline.kv.cells`; ceiling rule NC | B |
| 049 | `> 5` % | SL:760 | CFG | DOC (M, external) | THRESHOLDS §8b; re-validate under LMCache (review #15.3) | `statusline.kv.host_yellow_pct` | B |
| 050 | `> 0.5` % | SL:763 | CFG | Dv† | the share prints `.0f`, so ≤ 0.5 would print 0% | `statusline.kv.host_shown_pct` | R1 |
| 051 | `>= 10` s | SL:795 | CFG | DOC | buckets 20/40/80 (review #18.2) | `statusline.ttft.integer_from_s` | B |
| 052 | `> 8` s | SL:799 | CFG | DOC (M, external) | THRESHOLDS §8b | `statusline.ttft.yellow_s` | B |
| 053 | `> 1520` / `> 1280` W | SL:812 | CFG | DOC | 95 % / 80 % of the 1,600 W rating | `statusline.power.wall_red_w` / `wall_yellow_w` (keep literals) | B |
| 054 | 524,288 B read **step** | SL:952,1044-1052 | CFG | OWNER-C | a step, not a cap (CONV-ABS-43) | `statusline.transcript.read_cap_bytes` | R1 |
| 055 | 200 tokens | SL:967 | CFG | DOC | owner decision 2026-11-13, replay (SL:955-961) | `statusline.turn.dim_below_out` | B |
| 056 | 20,000 | SL:972 | CFG | M | 9,650 calls / 120 transcripts (SL:968-971) | `statusline.tokens.rebuild_excess` | B |
| 057 | 15 tok/s | SL:973 | CFG | DOC | harness per-agent decode floor (SL:964-965) | `statusline.turn.floor_tps` | B |
| 058 | 4× | SL:974 | CFG | J | "margin for slow prefill" (SL:965) | `statusline.turn.stale_factor` | B |
| 059 | 2,000 chars per image | SL:1137,1149 | CFG | OWNER-C | review #6.3 records the decision, not the derivation | `statusline.composition.image_chars` | R1 |
| 060 | 256 ids | SL:1153 | CFG | Dv† | adjacency comment (SL:1029-1032) | `statusline.transcript.dedup_memory` | R1 |
| 061 | 40 chars | SL:1017 | NC | Dv† | ≥ 36 = a session UUID | NC: cache file-name format shared during shadow (P2r1 §6.3) | R1 |
| 062 | sha1 `[:16]` | SL:405 | NC | C | cache key | NC: file-name format | B |
| 063 | 7 chars | SL:389 | NC | C | git short sha | NC: git format | B |
| 064 | 9999 | SL:325 | NC | Dv† | sentinel (F-5) | NC: explicit "unknown age" in Go | R1 |
| 106 | `len(pts) < 2` → none | SL:666 | NC | Dv | a trend needs two samples | NC: structural | R1 |
| 107 | preempt `> 0` | SL:346 | CFG | DOC | "same rule as the queue (#17.3)" | `statusline.queue.yellow.preempt_rate_gt` (H-1) | R2 |
| 108 | running `< 1` | SL:825 | CFG | DOC | review #20; WIDGETS Idle | `statusline.idle.running_below` | R1 |
| 109 | `round()` half-even; `" <1%"`; width 2 | SL:1171-1172 | NC | DOC | SL:1162,1172 | NC: display format (parity BX) | R1 |
| 110 | `>= 2` parts | SL:595 | NC | DOC | SL:595 comment | NC: structural | R1 |
| 111 | `> 0` zero-suppression group | SL:536-537,586-598,602,627,629,1170,1221 | NC | DOC | WIDGETS Tokens; review #8 | NC: structural | R1 |
| 112 | `(i + 0.5) × 10` | SL:428 | NC | Dv | the cell's midpoint | NC: mathematical | R1 |
| 113 | 8 levels, half-up | SL:136,673-675 | NC | C+Dv | U+2581–U+2588 offer 8 heights | NC rule over the glyph string (OD-02) | R3 |
| 114 | 1e-9 | SL:671 | NC | Dv | division guard | NC | R1 |
| 115 | percent clamps | SL:146,422,479,508,517,674,758 | NC | Dv | percent domain; negatives plot as 0 (SL:674) | NC | R2 |
| 116 | ROWS `>= 2` / `> 2`; COLUMNS 0 = unknown ⇒ wide; trim only if `cols > 0` | SL:1217,1224,1232 | CFG+NC | DOC | WIDGETS Tunables; SL:50 | semantics of `statusline.rows` + `narrow_cols` | R2 |
| 117 | `--subagent` `.2fM`/`.1fk`, `mm:ss` | SL:876-885,919-920 | CFG (if OD-14 keeps it) | OWNER-B | none | `statusline.subagent.units` | R1 |
| 133 | 4,300 digits | CPython 3.11 `default_max_str_digits` (executed r2, synthetic) | NC | C | runtime default | NC parity constant in the transcript decoder | R2 |
| 134 | 300 ms debounce; cancel in-flight | SL:43-44; WIDGETS | EXT | EXT | Claude Code scheduler | — | R1 |
| 135 | 5 s subagent timeout | WIDGETS subagent contract | EXT | EXT | Claude Code | — | R1 |

#### B.2.2 Proxy, CA, ledger (`internal/proxy`, `internal/ledger`, P3; `internal/ca`, P4) — 31 rows

| T | Value (op) | Site | Class | Rat. | Rationale | Key / NC reason | Last |
|---|---|---|---|---|---|---|---|
| 065 | 64,000 B (`>`) | PX:368,408 | CFG | OWNER-C | purpose "runaway line guard" (PX:408), value not. Feed pieces are ≤ 65,535 B per socket read (m/proxy/server.py:285; TLS m/proxy/layers/tls.py:416); boundary behavior is BC-PX-040/045 | `proxy.sse_tap.max_line_bytes` (OD-35) | R4 |
| 066 | keep 19 + new = ≤ 20 files | PX:291-292 | CFG | OWNER-E | purpose (PX:284-285), count not | `proxy.failed_capture.keep` (location `paths.failed_capture_dir`, pass-5 r2 K-3) | R3 |
| 067 | `< 50,000,000` chars | PX:295 | CFG | OWNER-C | none | `proxy.failed_capture.max_chars` | R1 |
| 068 | `[:600]` | PX:287 | CFG | OWNER-D | none | `proxy.decision_log.error_body_chars` | R1 |
| 069 | `[:300]` | PX:322 | CFG | OWNER-D | D7 field value; 300 through cutover | `ledger.upstream_error.max_chars` | R1 |
| 070 | round 3 dp / 1 dp | PX:213,238,273,536 | NC | C | ledger number format | NC: D7 | B |
| 071 | `[:8]` | PX:332,335 | NC | C | UUID first group | NC: D7 value format | R1 |
| 072 | 80 | PX:83 | NC | C | HTTP default port | NC: URL semantics | B |
| 073 | `>= 400` | PX:205,283 | NC | C | HTTP error class | NC: protocol | B |
| 074 | 3 backups | PX:564 | CFG | OWNER-E | none | `ca.backups_keep` | R1 |
| 075 | 30 s / 0.5 s | PX:723-725 | CFG (DROP with `ca.restart_command`) | OWNER-G | none | `ca.regen_wait_s` / `ca.regen_poll_s` (rule-5 form if kept: `ca.restart.{command, wait_s, poll_s}`) | R1 |
| 076 | `removed < 10` | PX:692 | CFG | Dv† | bounds a loop whose delete is `check=False` | `ca.keychain_delete_max` (darwin) | R1 |
| 122 | 600 s inactivity per client connection; reset by **every** event, including h2 ping wakeups, so it never fires on an h2 client connection while its upstream `Http2Client` is open. Edge: if the eager upstream TLS fails, the h2 client connection has no `Http2Client` until a flow opens one, and the 600 s cut applies meanwhile. Disarmed during hooks | m/options.py:240-247; m/proxy/server.py:50-76,116-120,267-272,387,402-410; m/proxy/mode_servers.py:70; m/proxy/layers/tls.py:606-619; m/addons/tlsconfig.py:118-128,232-236 | CFG | C | tool default; fired 57 times in production, 0 on h2 client connections (P2r8 §1.1; not re-counted) | `proxy.idle_timeout_s` (OD-37); under OD-94 (b), activity must mean bytes moved | R6 |
| 123 | TLS ≥ 1.2, max unbounded | m/net/tls.py:69-70 | NC | C | tool default | NC: security floor | R1 |
| 124 | 58 s h2 PING keep-alive on **upstream** h2 connections (`Http2Client` only); fires after about 57 s idle (`+ 1` slack); 0 disables | m/options.py:137-146; m/proxy/layers/http/_http2.py:539-567 | NC | C | tool default; live for child h2 traffic (CONV-ABS-85) | OD-94 (a): N/A. (b): CFG `proxy.http2.ping_keepalive_s` = 58 (a timeout, so D15 makes it config) | R5 |
| 125 | RSA 2048 (e = 65537); CA 3,650 d; leaf 199 d span, back-dated 2 d (197 d forward); leaf reuses the CA key; SHA-256; CN only if < 64 chars; dummy CRL next update +5 d, served at `/mitmproxy-<serial>.crl` on the upstream CRL host | m/options.py:9,226-233; m/certs.py:40-44,328,340-341,427-434,493,512-514,803-811; m/addons/tlsconfig.py:631-684 | NC | C | tool default | NC in `hylo ca` with comments; whether hylo leaves carry a CRL point is a P4 design choice (no legacy client checks CRLs) | R4 |
| 126 | no connect timeout (OS) | m/proxy/server.py:212 (`asyncio.open_connection`, no `wait_for`) | CFG | N/A | absent limit | `backend.connect_timeout_s` (OD-42) | R1 |
| 127 | unbounded buffered body | PX:195-208; m/addons/proxyserver.py:164-183 | CFG | C | tool default | `proxy.max_buffered_body_bytes` (OD-54) | R1 |
| 128 | unbounded WebSocket retention | m/proxy/layers/websocket.py:186 | NEW-H | C | tool default | D16 bounded buffer (HY-WS-1) | R1 |
| 136 | 100 leaves, FIFO by insertion (hits do not refresh); key = (CN, SANs = upstream leaf CN/SANs + SNI or local IP + CONNECT authority, deduplicated); organization and CRL point are minted from the first upstream cert but are **not** in the key; no expiry re-check on a hit | m/certs.py:541,576-580,788-818; m/addons/tlsconfig.py:634-682; m/proxy/layers/http/__init__.py:779 | NC | C | tool default; eviction only re-signs (CPU), never a behavior change (CONV-ABS-81, -86) | NC in `internal/ca`; re-mint before `not_after` for a long-lived proxy (OD-50) | R6 |
| 137 | 5 open upstream connections per address per client connection; permit held for the connection's life. Reachable for h2 → h1 rewritten flows: mitmproxy opens one upstream connection per flow and closes it when the flow completes, so a 6th concurrent rewritten stream waits until one of the 5 in-flight flows completes | m/proxy/server.py:105-109,206-265; m/proxy/layers/http/__init__.py:1087-1097,1178-1188; m/proxy/layers/http/_http1.py:200-209 | N/A | C | tool default; never bound (2 rewritten h2 flows, not concurrent; P2r9) | N/A: Go transport limits; D14 removes h2 child clients. Recorded so the parity harness does not expect queueing | R6 |
| 138 | 1 s mtime poll; strict `mtime >`; vanished file removes the script | m/addons/script.py:74,133-152 | DROP | C | tool default | — (OD-26; compiled binary) | R4 |
| 139 | no HTTP/1 head size limit (h11 `ReceiveBuffer` without `h11.Connection`'s 16 KiB cap); asymmetric with h2's 64 KiB header-list cap (T-146) | m/proxy/layers/http/_http1.py:9,58,285,408; h11/_connection.py:69,485 (unused) | NC | N/A | absent limit; unobservable for Claude Code traffic (P2r7 T-6) | NC in `internal/proxy` with a comment: hylo's listener has a finite head limit (Go `DefaultMaxHeaderBytes` 1 MiB, go/src/net/http/server.go:892-902), a deviation only for heads no legacy client sends | R5 |
| 140 | h2 local `SETTINGS_INITIAL_WINDOW_SIZE` 2³¹ − 1 (per stream); received data acknowledged on parse | m/proxy/layers/http/_http_h2.py:53,57; m/proxy/layers/http/_http2.py:238-240 | NC | C | tool setting; live for children; no proxy pacing, no end-to-end h2 backpressure (CONV-ABS-87) | OD-94 (a): N/A. (b): NC, plus a bounded per-stream send buffer (hylo deviation) | R5 |
| 141 | h2 connection window raised to 2³¹ − 1 | m/proxy/layers/http/_http_h2.py:61-67; m/proxy/layers/http/_http2.py:124-126 | NC | C | tool setting; live for children | as T-140 | R5 |
| 142 | h2 max frame size 2¹⁷ = 131,072 B, advertised and enforced inbound (the h2 library's own default is 16,384 B; `DEFAULT_MAX_INBOUND_FRAME_SIZE` 2²⁴ is a dead constant) | m/proxy/layers/http/_http_h2.py:54-55,57; h2/connection.py:377,1516,2003-2005; h2/settings.py:141; h2/frame_buffer.py:70-72 | NC | C | tool setting; an oversize frame kills the connection (GOAWAY `FRAME_SIZE_ERROR`, then `PROTOCOL_ERROR`) | as T-140 | R6 |
| 143 | 10 provisional upstream h2 streams before the server's first SETTINGS, then the server's `MAX_CONCURRENT_STREAMS` (2³² + 1, i.e. unbounded, if the SETTINGS omit it); excess queued in an unbounded FIFO | m/proxy/layers/http/_http2.py:487-490,511-537,631-634; h2/settings.py:226-231 | NC | C | tool setting; normally inert (eager connect) | as T-140 | R6 |
| 144 | upstream h2 push disabled (`ENABLE_PUSH` = 0); a received push promise is logged at ERROR | m/proxy/layers/http/_http2.py:496-500,297-301 | NC | C | tool choice | as T-140 | R5 |
| 145 | h2 local `MAX_CONCURRENT_STREAMS` 100 (client leg); the 101st stream kills the connection (`TooManyStreamsError`) | h2/connection.py:344-362,1601-1606 | NC | C | library default | as T-140 | R5 |
| 146 | h2 max decoded header list 65,536 B (name + value + 32 per entry, strict `>`); oversize → `DenialOfServiceError` (GOAWAY `ENHANCE_YOUR_CALM`) | h2/connection.py:319-320,335,359-360,1999-2001,2104-2111; hpack/hpack.py:34,499,543-547 | NC | C | library default; asymmetric with T-139 | as T-140, with a comment on the h1/h2 asymmetry | R5 |
| 147 | h2 closed-stream memory 65,536 entries | h2/connection.py:322-323,395-397,2030-2034 | NC | C | library internal; behavior-neutral | as T-140 | R5 |

#### B.2.3 Exporter, hook, launcher, preflight, backfill, services — 37 rows

| T | Value (op) | Site | Class | Rat. | Rationale | Key / NC reason | Last |
|---|---|---|---|---|---|---|---|
| 077 | 50 sessions | EX:24 | CFG | OWNER-E | purpose "most-recent sessions tracked", value not | `exporter.session_limit` | R1 |
| 078 | 9210 | EX:25 | CFG | C (unverified) | Prometheus "default port allocations" wiki (exporters from 9100); the number is arbitrary | `exporter.port` (+ `exporter.bind`, HY-BIND-5) | R3 |
| 079 | bytes / 4.0 | EX:192-193 | CFG | C | "~4 chars per token" (EX:192) | `exporter.est_chars_per_token` | B |
| 080 | `[:8]` | EX:382 | NC | C | UUID group | NC: D7 label value | R1 |
| 081 | `status == 200` | EX:206 | NC | Dv† | success is 200 | NC: D7 metric semantics | R1 |
| 129 | backlog 5 | py39 socketserver.py:441 (py311 :443) | NC | C | library default | NC (failure mode only) | R1 |
| 130 | no socket timeout | py39 socketserver.py:784 (py311 :792) | NEW-H | C | library default | `exporter.read_header_timeout_s` / `idle_timeout_s` (HY-BIND-6, OD-33) | R1 |
| 131 | request line 65,537 B; header line 65,536 B, 100 headers; HTTP/1.0 | py39 http/server.py:402,623; http/client.py:109-110,212-217 | NC | C | library default | NC | R2 |
| 082 | 0.40 (`p < thr` = fake) | HK:33,249; L:150-152 | CFG | M | tuned 2026-11-10 after a 0.487 fake stop (L:150-151) | `hook.kev.threshold` | B |
| 083 | 2.5 s per socket op | HK:34,113 | CFG | OWNER-G | basis Kev-0.8B (HK:125-127); deployed kev-4b unmeasured; bound 15 s no-dribble, unbounded with dribbling | `hook.kev.timeout_s` (OD-56) | R3 |
| 084 | 14 | HK:35 | DROP | N/A | dead (still `int()`-parsed at import) | — (pass-5 ENV-23: accepted and ignored during shadow) | R1 |
| 085 | `[-6000:]` | HK:36,90 | CFG | OWNER-C | none | `hook.kev.state_chars` | R1 |
| 086 | `[:400]`; `[-800:]`; head `[:800]` | HK:83,89,91 | CFG | OWNER-D | purpose (HK:87-88), values not | `hook.kev.line_chars` / `final_tail_chars` | R1 |
| 087 | 3 tries, median | HK:124,129 | CFG | M | ±0.09 single-draw noise (HK:125-127) | `hook.kev.tries` | B |
| 088 | `t > KEV_TIMEOUT / 2` | HK:133 | CFG | Dv† (J weak) | "slow endpoint: stop early" (HK:134) explains the stop, not the half | `hook.kev.early_stop_fraction` | R3 |
| 118 | `len(ps) >= 2`, last call succeeded | HK:133 | CFG | J+Dv | HK:134; a median needs > 1 value | `hook.kev.early_stop_min_scores` | R2 |
| 119 | `ps[len(ps)//2]` (upper median) | HK:137-138 | NC | Dv† | leans toward allowing the stop | NC: median definition (parity) | R1 |
| 089 | `[-160:]` / `[-100:]` | HK:215,268 | CFG | OWNER-D | none | `hook.log.tail_chars` / `hook.autocontinue.quote_chars` (H-5) | R2 |
| 090 | `len > 20` | HK:236 | CFG | OWNER-F | none | `hook.autocontinue.colon_min_chars` (op `>`, stated in the comment; boundary test 20/21) | R3 |
| 091 | `len < 200` | HK:179 | CFG | OWNER-F | none | `hook.autocontinue.max_sentence_chars` (op `<`; boundary test 199/200) | R3 |
| 092 | `n >= 12` or (`n >= 4` and ratio `> 0.02`) | HK:190 | CFG | J+OWNER-F | purpose labeled (HK:188), numbers not | `hook.english.cjk_min_count` / `cjk_ratio_min_count` / `cjk_min_ratio` (op `>`) | R3 |
| 093 | 20 s | HK:141 | DROP | N/A | dead | — | R1 |
| 094 | 30 s / 5 s | L:161,158 | CFG | Dv† | 30 s ≥ the 15 s no-dribble Kev bound and is the only hard limit; 5 s for an `echo` | `run.hooks.stop_timeout_s` / `prompt_timeout_s` | R2 |
| 095 | 8090-8143 | L:72-73; CO:10 | DROP | N/A | hylo binds its own listener (OD-19) | — | R1 |
| 096 | 40 × 0.25 s | L:77; CO:35 | DROP | N/A | in-process listener | — | R1 |
| 097 | 1,800,000 ms | L:104 | CFG | DOC | "local … model is slow; allow long responses" | `run.api_timeout_ms` | B |
| 098 | refreshInterval 4 s, padding 0 | L:176 | CFG | OWNER-G | role stated (L:170-171), value not | `run.statusline.refresh_interval_s` / `run.statusline.padding` | R1 |
| 099 | 120 s | CO:11 | DROP | N/A | coordinator unwired | — | R1 |
| 100 | 4 s connect | PF:23 | CFG | OWNER-G | none; DNS outside it, N × 4 s for N addresses | `run.preflight.timeout_s` (`HYLO_RUN_PREFLIGHT_TIMEOUT_S`; toggle `run.preflight.enabled`, pass-5 r2 K-1) | R3 |
| 101 | 30 s × 3 | pl-tu:9-10 | OOS | Dv† | ≈ 90 s dead-peer detection (man ssh_config) | — (BC-SV-002) | R1 |
| 120 | `127.0.0.1:9210:127.0.0.1:9210` | pl-tu:8 | OOS | Dv | mirrors T-078 | — | R1 |
| 121 | 4141-4199 scan (live); `curl -m 2`, 40 × 0.25 s (dead) | L:20-21,85,94 | DROP | N/A | D6 invisible only | — (R-11 parity-era note) | R2 |
| 132 | 10 s minimum spawn interval | man launchd.plist ThrottleInterval; not set in pl-ex/pl-tu | CFG | C | platform default (documented) | `service.restart_throttle_s` (H-4) | R2 |
| 102 | list prices opus/sonnet/haiku | BF:28-32 | CFG | DOC | claude-api reference, cached 2026-11-03 | `prices.<family>` (OD-13) | B |
| 103 | $1 / 30 min | BF:34-35 | CFG | DOC | BF:12-14 docstring | `cost.backfill.min_usd`; minimum API time reads `statusline.cost.rate_min_api_ms.other` (H-2) | R2 |
| 104 | 30 days | BF:86 | CFG | DOC | matches `COST_WINDOW_S` | `cost.backfill.days` | B |
| 105 | `0 < span <= 4·max(o,1)/15` | BF:78 | CFG+NC | DOC | same rule as T-057/T-058 | shares the turn keys; `max(o,1)` and `<=` variant NC (P2r1 §7 I7) | B |

#### B.2.4 Totals (recounted row by row this round from B.2.1-B.2.3)

| Measure | Count |
|---|---|
| Thresholds | **147** = status line 79 + proxy/CA/ledger 31 + exporter/hook/launcher/services 37 (provenance: broad 105 + r1 30 + r3 3 + r4 1 + r5 8) |
| By class | **CFG 96 · NC 37 · DROP 7 · OOS 2 · EXT 2 · NEW-H 2 · N/A 1** (status line CFG 62, NC 15, EXT 2; proxy CFG 11, NC 17, NEW-H 1, N/A 1, DROP 1; others CFG 23, NC 5, DROP 6, OOS 2, NEW-H 1) |
| By rationale | **OWNER 27 · Dv† 18 · N/A 8 · EXT 2 · resolved DOC/J/M/C/Dv 92** |
| Rationale resolved | **120 of 147** (102 final + 18 awaiting one bulk "yes") |
| Owner must supply | **27 rows in 7 groups** (§B.4) |
| OD-94 sensitivity | (a) h1-only: T-124 and T-140..T-147 move NC → N/A, giving **NC 28 · N/A 10**. (b) mirror h2: T-124 moves NC → CFG, giving **CFG 97 · NC 36**. No rationale status changes either way |
| Rows by last change | **B 45 · R1 56 · R2 16 · R3 14 · R4 3 · R5 8 · R6 5 · R7 0** = 147 (per-row lists in §B.2.5) |

#### B.2.5 "Last changed" tally, per row

Counted from the Last column of B.2.1-B.2.3:

- **B (45):** 001, 002, 006, 011, 012, 013, 015, 018, 019, 020, 021, 027, 028, 029, 031, 032, 033, 034, 036, 037, 041, 042, 043, 044, 048, 049,
  051, 052, 053, 055, 056, 057, 058, 062, 063, 070, 072, 073, 079, 082, 087, 097, 102, 104, 105.
- **R1 (56):** 003, 004, 008, 010, 014, 022, 024, 025, 030, 035, 038, 045, 046, 050, 054, 059, 060, 061, 064, 106, 108, 109, 110, 111, 112, 114,
  117, 134, 135, 067, 068, 069, 071, 074, 075, 076, 123, 126, 127, 128, 077, 080, 081, 129, 130, 084, 085, 086, 119, 093, 095, 096, 098, 099,
  101, 120.
- **R2 (16):** 005, 007, 023, 039, 047, 107, 115, 116, 133, 131, 118, 089, 094, 121, 132, 103.
- **R3 (14):** 009, 016, 017, 026, 040, 113, 066, 078, 083, 088, 090, 091, 092, 100.
- **R4 (3):** 065, 125, 138.
- **R5 (8):** 124, 139, 140, 141, 144, 145, 146, 147.
- **R6 (5):** 122, 136, 137, 142, 143.
- **R7 (0).**

Sum: 45 + 56 + 16 + 14 + 3 + 8 + 5 = **147**. These differ from r3 §C.5's "last changed in R3: 18 rows" only because T-125, T-136, T-137 and
T-138 were changed again in R4-R6.

### B.3 NFR catalogue by category (final; merges r3 §E with r4 §D, r5 §D and r6 §C)

#### B.3.1 Performance

| NFR | Legacy behavior and numbers | BC / OD / T |
|---|---|---|
| P-1 One status line run fits Claude Code's scheduler | Triggers: assistant messages, `/compact`, mode changes, 4 s tick; 300 ms debounce; a newer trigger cancels the running one. Per run: at most one VM fetch (only once the TTL has passed; TTL = refresh ⇒ every tick fetches), 1.5 s per socket operation, ≤ 3 s without dribbling, DNS unbounded for host names. The fetch also runs when the narrow test hides row 2 (`SL:1217-1224`). Git cached 5 s. `ps` walk: once per session when it succeeds, otherwise repeated every refresh, ≤ 6 × 1 s. Cost-history write ≤ once per minute | BC-SL-010, -023, -040, -041, -053; T-001, T-005, T-013, T-022, T-025, T-026, T-098, T-134; OD-56 |
| P-2 Parse bounds | Transcript read incremental, ≥ 512 KiB per run, extended to the next newline with no upper bound (CONV-ABS-43); dedup memory 256; a `mixv6` marker change forces a full re-parse. VM body read whole. Hook reads the whole transcript on every Stop | BC-SL-032, -068/098, BC-HK-008; T-054, T-060 |
| P-3 Streaming latency and memory | SSE relayed chunk by chunk, tap tail ≤ 64,000 B, feed pieces ≤ 65,535 B; `/v1/messages*` JSON or ≥ 400 buffered for the addon; every other non-SSE response buffered in full, no cap (CONV-ABS-44); WebSocket messages retained. **h1 client legs** (all Claude Code traffic): pass-through flows are backpressured, about 64 KiB written + 128 KiB read per connection (asyncio defaults, py311). **h2 client legs:** no end-to-end backpressure (unbounded per-stream send deque, 2³¹ − 1 windows, immediate acknowledgement); reachable for streamed child h2 flows, not observed (CONV-ABS-87) | BC-PX-014, -016, -037, -040, -045; T-065, T-127, T-128, T-140, T-141; OD-54 |
| P-4 Long routed responses | client timeout 30 min; proxy idle cut 600 s per client connection, reset by any event, disarmed during hooks; on h2 client connections the upstream ping wakeups keep it from firing while the upstream h2 connection is open, except after a failed eager upstream TLS handshake; no total cap; pass-through SSE up to 3,600 s and WebSockets 3 h 51 min observed | BC-LN-005, BC-PX-049; T-097, T-122, T-124; OD-37; HY-TIMEOUT-1, HY-PASS-1 |
| P-5 Exporter scrape cost | full ledger rescan after growth, single-threaded, HTTP/1.0, one request per connection | BC-EX-003, -022, -026, -027; T-131; OD-39 |
| P-6 Stop-hook latency | Kev 13 ms/pass measured for Kev-0.8B only; ≤ 3 calls; a failed call costs milliseconds (refused) to 2.5 s (unanswered connect) (CONV-ABS-73); strict bound 15 s without dribbling, unbounded with it; early stop only after a slow successful call with ≥ 2 scores; Claude Code kills at 30 s. A final failed call after a success crashes the hook (H-04) | BC-HK-010, -022; T-083, T-087, T-088, T-094, T-118; OD-12, OD-56 |
| P-7 mitmproxy internal caps | Leaf cache 100, keyed by (upstream leaf CN/SANs + SNI + CONNECT authority), no resolved IP; eviction only re-signs. 5 open upstream connections per address per client connection; reachable for h2 → h1 rewritten flows, where each permit is released when its flow completes. h2 caps (T-142, T-145, T-146) are connection-fatal: two GOAWAY frames (the exception's code, then `PROTOCOL_ERROR`) and every open stream fails | T-136, T-137, T-142, T-145, T-146; OD-50 |

#### B.3.2 Reliability

| NFR | Legacy behavior | BC / OD / T |
|---|---|---|
| R-1 Status line exits 0 except documented crash paths | guard prints the 29-byte degraded line; exceptions CP-X01/X02 (import-time env parse), CP-X03 (guard's own `print`), CP-X04 (signals) | BC-SL-001, -087; CONV-ABS-41 |
| R-2 Telemetry ladder | green while the latest fetch succeeded; yellow from the first failed fetch; last-known ≤ 300 s on fetch runs, any age on in-TTL runs; `◌ DGX ?` without a sample | BC-SL-041, -043, -091; T-003, T-004; CONV-ABS-42; OD-55 |
| R-3 No fabricated zeros | missing series omit segments | BC-SL-074 |
| R-4 Cache durability | `mkstemp` + `os.replace`; a lost cost-history update is repaired within a minute (accepted) | BC-SL-052; T-022 |
| R-5 Proxy never breaks traffic on observability failures | appends swallow `OSError`; exceptions OD-45, OD-18, OD-08 | BC-PX-028, -048 |
| R-6 Upstream failures | no retry or backoff, no connect timeout, eager connect | BC-PX-024, -047; T-126; OD-17, OD-42 |
| R-7 Stop hook | no top-level guard; H-01..H-09, H-04 production-reachable | BC-HK-019, -022; OD-12 |
| R-8 Exporter crash loop | a poison line crashes `rebuild()`; launchd spawns at most once every 10 s (documented) | BC-EX-021; T-132; OD-11 |
| R-9 Supervision | launchd `KeepAlive` for exporter and tunnel; tunnel dead-peer ≈ 90 s; `ExitOnForwardFailure=yes` (`pl-tu:11`) | BC-SV-001/002 (OOS); T-101, T-132 |
| R-10 Pre-trap orphan window | mitmdump started at `L:75`, trap at `L:97`; readiness failure `exit 1` (`L:78`) orphans it. mitmdump starts with SIGINT and SIGQUIT ignored (`&` without MONITOR, `zshmisc(1)` SIGNALS), so an early Ctrl-C orphans it until `m/tools/main.py:128` installs its handler; SIGQUIT stays ignored for life | pass-1 r3 §B.2; OD-50, OD-66 |
| R-11 Busy router range aborts invisible launches | 59 `nc` probes then `exit 1` (`L:17-22`) | CONV-ABS-61; OD-19 (hylo drops it) |
| R-12 Terminal close kills the proxy without draining | SIGHUP not trapped (`L:97`), no handler in mitmproxy (`m/tools/main.py:128-129` SIGINT/SIGTERM only; 0 `SIGHUP` references in `m/`) → immediate death, no `error` hook, no ledger lines for in-flight flows. Delivery HIGH (documented, not exercised: `termios(4)`, `_exit(2)`, `intro(2)`, `zshoptions(1)` HUP/MONITOR, `zshmisc(1)` JOBS/SIGNALS), with one unstated link: that closing a terminal window is a hangup on its pseudo-terminal. hylo: detached shared proxy (OD-66 (a)), drain (OD-38), stop (OD-50), SIGHUP given an explicit meaning | pass-1 r3 I-23; CONV-ABS-82; OD-38, OD-50, OD-66 |

#### B.3.3 Security

| NFR | Legacy behavior | BC / OD / T |
|---|---|---|
| S-1 Network exposure | proxy on all interfaces, RFC 1918 clients admitted; exporter `0.0.0.0:9210` unauthenticated (both accepted for legacy) | OD-24, OD-27, OD-34; HY-BIND-1..6; BC-EX-001 |
| S-2 Credentials | key file cached per process; unreadable key ⇒ client credentials forwarded (P-R4); only `Authorization` replaced; Kev key as env value; backend plain HTTP | OD-06, OD-07; D16 |
| S-3 Upstream TLS | verification on, certifi only, TLS ≥ 1.2; `SSLKEYLOGFILE` inherited | BC-PX-047; T-123; OD-41; HY-TLS-1/3 |
| S-4 CA | RSA 2048; CA 3,650 d and leaves 199 d, both back-dated 2 d; leaves reuse the CA key pair, SHA-256; CN only when < 64 chars; minted leaves copy the upstream CRL host with a local path answered by a dummy CRL valid 5 days forward; CA files written owner-only (umask `0o77`); cached leaves never re-validated, and organization/CRL point are not part of the cache key | T-125, T-136 |
| S-5 Data at rest | failed bodies ≤ 50 M chars × ≤ 20 files; ledger unrotated; caches `0600` | BC-PX-021; T-066, T-067 |
| S-6 Command execution | `DGX_PROXY_RESTART_CMD` `shell=True`; trust-CLI subprocesses with no timeout (`PX:568,578,590,606,638,693`) | — |
| S-7 Owner choices | permission prompts skipped, sandbox off by default | BC-LN rows; P2r2 §6.8 |

#### B.3.4 Operability

| NFR | Legacy behavior | BC / OD / T |
|---|---|---|
| O-1 Exporter stall | no socket timeout, one thread, backlog 5, HTTP/1.0; header limits 100 × 65,536 B (431). Proxy counterpart: listener backlog 100 (asyncio default, py311), failure mode only | BC-EX-026; T-129..T-131; OD-33 |
| O-2 Crash loop | one start about every 10 s, zero bytes, no alert | BC-EX-021; T-132; OD-11 |
| O-3 Silent failures | 600 s idle cut on pass-through leaves no ledger trace; SIGHUP death leaves none (R-12) | BC-PX-024, -049; OD-37, OD-38 |
| O-4 Logs and growth | per-window mitmdump logs never deleted; ledger and hook log never rotated; captures ≤ 20 | T-066 |
| O-5 Health | no exporter or proxy health endpoint; preflight 4 s → `hylo doctor` | BC-PF-001/002; T-100 |
| O-6 Config validation | malformed numeric env crashes at import; per-variable boolean predicates | BC-SL-087; OD-05 |
| O-7 Live reload | an edit to the addon reaches every window within about 1 s (one poll plus import) | T-138; OD-26 |

#### B.3.5 Portability (D5)

Process ancestry (`ps` + C-locale `strptime`, depth 6, 1 s per call) → `internal/platform` with a Windows fallback (D4-EX-1). Cache names →
OD-03. Supervision: launchd (10 s minimum spawn interval) → `service.restart_throttle_s` with an approximate per-OS mapping. Proxy launch (`zsh`,
`nc`, `lsof`, `flock`) → one in-process listener (OD-19). CA trust (`security`, `openssl`) → `hylo ca` per OS. Interpreter-dependent parsing (3.11
vs 3.9.6, T-133) → O1/OD-15. Time zones → OD-22. Paths → `paths.*`.

#### B.3.6 Missing NFRs (expected, not found in legacy)

Ledger rotation; health endpoints; upstream retry/backoff and connect timeout; a body-size cap (T-127); bounded WebSocket retention (T-128); a
total deadline on network calls with DNS covered (status line, hook, preflight); trust-CLI subprocess timeouts; config validation at load; ledger
time zones; launcher cleanup before the first child starts (R-10); a SIGHUP policy and drain on window close (R-12); leaf re-mint before expiry in
a long-lived proxy (T-136); automated tests; **hylo listener protocol posture** (OD-94), which must be set on **both** legs because Go's
`DefaultTransport` negotiates h2 upstream by default (§B.5).

### B.4 OD-57 owner lists (final; unchanged since r3 §C.6)

**Bulk confirmation (18 rows, Dv†, one answer: "accept as derived").** T-003, T-005, T-007, T-008, T-009, T-022, T-025, T-038 (covers T-039),
T-050, T-060, T-061, T-064, T-076, T-081, T-088 ("half the per-call timeout counts as slow; judgment"), T-094, T-101, T-119.

**Owner supplies a rationale (27 rows in 7 groups, one line per group).** "Labeled judgment call" is an acceptable answer (policy 16).

| Group | Rows | Suggested wording if no measurement exists |
|---|---|---|
| A. Retention and staleness windows (3) | T-004 300 s, T-010 1800 s, T-035 1.15 × window | "judgment: 5 min of last-known telemetry; 30 min of plan limits between Claude Code reports; 15 % slack before a reset time counts as bogus" |
| B. Layout and aesthetics (4) | T-014 72 cols, T-030 heat HSV, T-046 sparkline colors, T-117 subagent formats (if OD-14 keeps the path) | "judgment (presentation)" |
| C. Byte and size budgets (5) | T-054 512 KiB step, T-059 2,000 chars/image, T-065 64,000 B, T-067 50 M chars, T-085 6,000 chars | "judgment: parse step / image estimate / runaway-line guard / disk guard / Kev context budget" |
| D. Diagnostic text clips (4) | T-068 600, T-069 300, T-086 400/800, T-089 160/100 | "judgment: log readability" |
| E. Retention counts (3) | T-066 20 files, T-074 3 backups, T-077 50 sessions | "judgment: bounded disk / label cardinality" |
| F. Hook heuristic tuning (3) | T-090 > 20, T-091 < 200, T-092 12 / 4 and 2 % | "judgment, tuned on observed fake stops" |
| G. Timeouts and cadence (5) | T-098 4 s refresh (with T-001), T-100 4 s preflight, T-075 30 s / 0.5 s, T-026 1 s per `ps` call (walk uncached on failure, ≤ 6 s per refresh), T-083 2.5 s per socket operation (basis Kev-0.8B; kev-4b unmeasured) | "judgment", or a kev-4b latency figure for T-083 if one exists |

3 + 4 + 5 + 4 + 3 + 3 + 5 = 27. No r4-r7 row entered or left either list: T-122..T-147 carry rationale C or N/A, both resolved.

### B.5 OD-94 fact sheet (hylo listener HTTP/2 posture)

**Question.** Legacy accepts h2 from any client that offers it, by ALPN mirroring (upstream offer = client's offer, `m/addons/tlsconfig.py:322-328`;
the client gets the upstream's choice, `:108-123`). Under D14 the only client is Claude Code, which offers `http/1.1` (P2r8). Should hylo's
listener (a) negotiate HTTP/1.1 only, or (b) mirror h2 as legacy does? Recommendation on record (r5): **(a)**.

**Legacy facts both options must respect.** Claude Code traffic is h1 ↔ h1 because the upstream offer is the client's offer (HY-PROTO-1 mirrors,
it does not exclude h2). Child tools produced about 7,566 h2 flows and 2 rerouted h2 `/v1/messages` (P2r8/P2r9, not re-counted); D14 removes
them. The h2 rows are T-124, T-140..T-147; related rows T-122, T-137, T-139.

**Go 1.26.5 facts (source reading only; verified in §A rows 6-12 and r6 §B).**

| Topic | Fact | Go source |
|---|---|---|
| ALPN choice | server preference order; `http/1.1`-only client vs an `h2`-only server list connects with no protocol; no overlap otherwise → `no_application_protocol` | `crypto/tls/handshake_server.go:342-358, 269-272, 360`; TLS 1.3 `handshake_server_tls13.go:260-263` |
| Server h2 default | `Server.protocols()`: HTTP/1 always; HTTP/2 unless `TLSNextProto` is non-nil without `"h2"` or `GODEBUG=http2server=0` | `net/http/server.go:3506-3529` |
| Server setup | `ServeTLS` always sets h2 up and rewrites a clone of `NextProtos`; `Serve(l)` only via `shouldConfigureHTTP2ForServe` (TLSConfig nil, or `NextProtos` has `h2`, or unencrypted h2) | `server.go:3482-3503, 3404-3415, 3738-3747, 3367-3388` |
| Dispatch trap | negotiated protocol other than `""`/`http/1.1`/`http/1.0` goes to `TLSNextProto[proto]`; no handler → connection closed, no HTTP/1 fallback | `server.go:1951-1963, 1816-1821` |
| Transport h2 default | `Protocols` nil: h2 if `TLSNextProto` has `"h2"`, or (`ForceAttemptHTTP2` or no custom `TLSClientConfig`/dialer) and `http2client != 0`; a zero `&http.Transport{}` negotiates h2 despite the "usually HTTP/1 only" doc; `DefaultTransport` has `ForceAttemptHTTP2: true` | `transport.go:464-489, 309-311, 46-57` |
| GODEBUG precedence | `http2client=0` returns from setup before `protocols()` is read, even when `Protocols` asks for h2 | `transport.go:403-406, 427` |
| Plain `http://` upstream | h1 unless `Protocols` has `UnencryptedHTTP2` and not HTTP1 | `transport.go:304-308` |
| Head limits | server `DefaultMaxHeaderBytes` 1 MiB; transport response head 10 MiB | `server.go:892-902`; `transport.go:329-334` |
| Build tag | `nethttpomithttp2` removes the bundled h2 | `omithttp2.go:5, 16` |

**Option (a): HTTP/1.1 only (recommended).** Needs explicit settings on both legs:
1. Listener: per-tunnel `tls.Config.NextProtos = []string{"http/1.1"}`, and `Server.Protocols` HTTP1-only (or an empty non-nil `TLSNextProto`).
   `h2,http/1.1` offer → `http/1.1`; `h2`-only offer → handshake failure.
2. Upstream Anthropic leg: `Transport.Protocols` HTTP1-only. Without it, a transport built from `http.DefaultTransport.Clone()` or a bare
   `&http.Transport{}` negotiates **h2 with `api.anthropic.com`**, breaking the legacy h1 ↔ h1 for Claude Code.
3. Backend leg (`http://`): h1 by default; do not enable `UnencryptedHTTP2`.
4. `GODEBUG=http2server=0,http2client=0` also works but is process-wide and invisible in code; the `Protocols` fields are clearer and exist in Go
   1.26.5 (`server.go:3075`, `transport.go:312`).
5. Test: assert `ConnectionState().NegotiatedProtocol` on both legs.
6. Effect on the catalogue: T-124, T-140..T-147 → N/A (NC 28 · N/A 10); T-122 keeps one meaning. Deviation from legacy only for h2-offering
   clients, which D14 removes; log or `hylo doctor` warning if a client ever offers `h2`.

**Option (b): mirror h2.** Go does not mirror (server-first ALPN), so hylo would need `GetConfigForClient`, an upstream-first connect with the
client's offer, and a per-connection `NextProtos` from the upstream's choice. Every legacy h2 row then needs an explicit setting:

| Legacy row | Legacy value | Go bundled h2 default | Go source |
|---|---|---|---|
| T-145 max concurrent streams (client leg) | 100 | 250 | `h2_bundle.go:4042, 1120` |
| T-142 max frame size | 2¹⁷ | 1 MiB | `h2_bundle.go:3531, 1133` |
| T-140/T-141 receive windows | 2³¹ − 1 | server 1 MiB per connection and per stream; transport 1 GiB / 4 MiB | `h2_bundle.go:1123-1132, 7334, 7339` |
| T-124 keep-alive PING | 58 s idle (upstream only) | none unless `ReadIdleTimeout` is set; ping-ack timeout 15 s | `h2_bundle.go:1074, 1093, 1134, 4953-4955` |
| T-146 max header list | 65,536 B | `MaxHeaderBytes` + 320 on the server | `h2_bundle.go:1139-1145, 4640` |
| T-143 provisional streams | 10 | transport 100 | `h2_bundle.go:7346` |

Plus: the idle timer must count bytes moved, not internal timer events (T-122 × T-124), and the per-stream h2 send buffer needs a bound (T-140,
P-3). Effect on the catalogue: T-124 → CFG `proxy.http2.ping_keepalive_s` (CFG 97 · NC 36); T-140..T-147 NC with comments.

---

## C. Target C: is anything in pass 4 still open beyond owner decisions?

**No analysis item is open.** Every threshold has a value, an operator, a source anchor, a class, a key or named-constant reason and a rationale
status, and this round re-confirmed every round-6 claim against source. What remains falls into three kinds, none of which can change a row's
value or class:

1. **Owner decisions:** OD-57 (18 bulk confirmations; 27 rationales in 7 groups) and OD-94 (h1-only vs h2 mirroring). OD-94 changes the class of
   9 rows (§B.2.4), which is already tabulated for both outcomes.
2. **Design-phase verification, not legacy analysis:** the Go facts are from source reading; P1/P3 must pin them with a negotiated-ALPN test on
   both legs. The test-plan notes for boundary table tests (`SL:674` clamp, `cols > 0` trim, T-090..T-092 strict operators) belong to P1/P3.
3. **Labels and confidence notes with no effect on behavior:** T-078's port-allocation source is unverified (no network; rationale label only);
   the asyncio values in P-3 and O-1 are CPython 3.11's (production is 3.12.10, not an authorized source; behavior-neutral at legacy scale); R-12's
   pty-close-as-hangup step is the one link the authorized man pages do not state; the P2r8/P2r9 production counts are pass-2's and were not
   re-counted here (logs are not an authorized source for this pass).

---

## Delta Summary

- **Target A:** 12 items re-verified from fresh reads: CONV-ABS-93's site (`_http1.py:200-209` plus the permit lifetime in `server.py:206-265`),
  CONV-ABS-94's site (dead constant confirmed by a venv-wide search; library default 16,384 B at `h2/settings.py:141`), the T-143 2³² + 1
  refinement, the T-122 TLS-failure edge case, the double GOAWAY, and 7 Go citations (`server.go:3506-3529`, `1951-1963`; `transport.go:464-489`,
  `403-406`; `h2_bundle.go` max streams, frame size, windows/ping/header list/provisional streams). **12 confirmed, 0 retracted.** Two precisions on
  T-137 (the `is_http3` arm; the permit is freed after a `server_disconnected` hook that legacy does not register) change no row.
- **Target B:** the final self-contained catalogue: 147 threshold rows with value, operator, site, class, rationale, key or NC reason and last
  round; class totals recounted row by row (CFG 96 · NC 37 · DROP 7 · OOS 2 · EXT 2 · NEW-H 2 · N/A 1); NFR catalogue P-1..P-7, R-1..R-12,
  S-1..S-7, O-1..O-7, portability, missing NFRs; OD-57 lists (18 / 27 in 7 groups); OD-94 fact sheet for both options. r6's text-only notes on
  T-122, T-136 and T-143 are folded into their rows (marked R6).
- **Target C:** nothing open beyond owner decisions, design-phase tests and behavior-neutral labels (§C).
- New items added: 0 threshold rows, 0 NFRs, 0 owner items (OD-110..OD-113 unused). Retractions: 0 (CONV-ABS-101..104 unused). Existing items
  refined: 0 values or classes; 3 rows absorb r6 notes; 2 precisions (T-137). Last-changed tally: B 45 · R1 56 · R2 16 · R3 14 · R4 3 · R5 8 ·
  R6 5 · R7 0 = 147.

## Remaining Gaps (verbatim-carryable)

1. Owner answers for OD-57 (18 bulk Dv† rows; 27 owner rationales in 7 groups, §B.4) and OD-94 (h1-only versus h2 mirroring; §B.5 facts).
2. P1/P3: a test asserting the negotiated ALPN on the listener and the upstream transport (Go facts are source-read only); boundary table tests for
   `SL:674`, `cols > 0`, T-090..T-092.
3. Behavior-neutral labels: T-078 port-allocation source unverified; asyncio values are CPython 3.11's; R-12's pty-close-as-hangup link
   undocumented; P2r8/P2r9 counts not re-counted in pass 4.

## Novelty Assessment

Novelty: NITPICK — findings are refinements, not gaps.

This round re-read both round-6 retraction sites and every round-6 refinement independently and found them correct. It re-checked seven Go
citations behind the OD-94 fact sheet and found them correct. Ten legacy anchors re-printed unchanged. It added no threshold, changed no value,
operator, class, key or rationale status, raised no owner item and retracted nothing. The consolidation and the folding of r6's notes into rows are
bookkeeping, and the two T-137 precisions are wording. Removing this round would not change how the system is specified.

## Convergence Declaration

Pass 4 has converged — findings are nitpicks, not gaps.

## State Checkpoint

```yaml
pass: 4
round: 7
status: complete
timestamp: 2026-11-14T14:10:00Z
novelty: NITPICK
files_scanned: mitmproxy 12.3.1 proxy/layers/http/{_http1,_http2,_http_h2,__init__}.py, proxy/server.py, proxy/events.py, proxy/layers/tls.py, addons/tlsconfig.py, options.py, http.py, version.py; h2 4.4.1 connection.py, settings.py, frame_buffer.py, exceptions.py; hpack 4.2.0 hpack.py; venv-wide search for DEFAULT_MAX_INBOUND_FRAME_SIZE; Go 1.26.5 src/net/http/{server,transport,h2_bundle}.go; legacy SL/PX/HK/EX/PF/L anchor re-prints, PX:150-166, PX:362-412, git log/status of legacy/; pass-4 deep r3, r4, r5, r6
verification: {items: 12, confirmed: 12, retracted: 0, precisions: 2 (T-137)}
thresholds: {total: 147, new_this_round: 0, changed_this_round: 0, by_class: {CFG: 96, NC: 37, DROP: 7, OOS: 2, EXT: 2, NEW-H: 2, NA: 1}, rationale: {owner: 27, bulk_confirm: 18, na: 8, ext: 2, resolved_other: 92}, resolved: 120, last_changed: {B: 45, R1: 56, R2: 16, R3: 14, R4: 3, R5: 8, R6: 5, R7: 0}}
od94_sensitivity: {a: {NC: 28, NA: 10}, b: {CFG: 97, NC: 36}}
retractions: []
conv_abs_unused: [101, 102, 103, 104]
new_owner_items: []
od_unused: [OD-110, OD-111, OD-112, OD-113]
pass5_r5: absent at time of writing (not read, not edited)
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r7/ (empty; all evidence is direct reads)
next: none for pass 4 (orchestrator applies the strict-binary rule)
```
