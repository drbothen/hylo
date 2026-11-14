# Pass 4 Deepening — Round 4: audit of round 3, systematic mitmproxy numeric-limit sweep — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/`, read-only and static. Nothing in `legacy/` was imported, executed or modified. No proxy, nothing
  networked, no socket binds, no DNS lookups. CLAUDE.local.md was not read.
- Authorized read-only references: mitmproxy 12.3.1 (`m/` = the venv's `site-packages/mitmproxy/`; `version.py` "12.3.1"), and for adjacent
  libraries on the same path the venv's `h2/`, `h11/` (read only to confirm what mitmproxy does and does not use); local man pages `zshmisc(1)`,
  `zshoptions(1)`, `termios(4)`, `intro(2)`, `_exit(2)`; CPython stdlib 3.11 (`py311/` = `/opt/homebrew/anaconda3/lib/python3.11`). The production
  interpreter is CPython 3.12.10 (P2r7). Its stdlib is not an authorized source, so every asyncio or shutil value below is the **3.11** value and
  is labeled as such.
- Scratch (all in `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r4/`): `sweep.py` parses every
  `.py` file of the mitmproxy package with `ast.parse` on the file text (run with Homebrew `python3.12 -I`, because the package uses 3.12 syntax;
  **nothing from mitmproxy is imported**). It writes `out/all.tsv` (every int/float literal), `out/inscope.tsv`, `out/nontrivial.tsv`,
  `out/consts.tsv` (module- and class-level numeric assignments) and `out/summary.txt`. `classify.py` labels the non-trivial in-scope rows and
  writes `out/classified.tsv` and `classify.out`. Man-page text dumps: `zshmisc.txt`, `zshoptions.txt`, `termios.txt`, `intro2.txt`, `exit2.txt`.
- Inputs read: pass-4 deep r3 (§C catalogue, §E NFRs) and r2 (headings, T-122..T-133 provenance). Pass-5 r3 does **not exist** at the time of
  writing (`ls` of the semport directory), so it was neither read nor edited. Cross-checked against P2r4/P2r5 (h2 not live: 0 ` HTTP/2.0` lines in
  38 logs), P2r6 (no `~/.mitmproxy/config.yaml`), P2r7 §1.4 T-6 (no header-size cap), P3r3/P3r4/P3r8 (BC-PX-040/045 feed boundaries), and pass-1 r2
  row 7l (a vanished script file removes the script).
- Numbering: retractions **CONV-ABS-81, 82** (83, 84 unused). **No new owner items** (OD-90..OD-93 unused). Sibling files were not edited.

Abbreviations and rationale codes as in round 3 (`SL`, `PX`, `HK`, `L`, …; **M**, **DOC**, **J**, **C**, **Dv**, **Dv†**, **OWNER**, **N/A**,
**EXT**; classes CFG, NC, DROP, OOS, EXT, NEW-H, N/A per r3 §C.1).

---

## A. Independent audit of round 3's new items (fresh evidence)

### A.1 Verification table

| # | Round-3 item | Fresh evidence (this round) | Verdict |
|---|---|---|---|
| 1 | **T-136** leaf cache: 100 leaves, FIFO, no expiry re-check | `m/certs.py:541` `STORE_CAP = 100`. `expire()` at `:576-580` appends every new entry to `expire_queue` and, past 100, pops the **oldest inserted** entry and drops it from `certs`. `get_cert` (`:771-821`) builds candidate keys (asterisk forms of the CN and each SAN, then `"*"`, then `(commonname, sans)`), returns the first one present in `self.certs`, and **never looks at the cached certificate's validity dates**. A miss mints with `dummy_cert(self.default_privatekey, …)` and stores under `(commonname, sans)` (`:802-819`). **Refinements:** (a) a cache hit does not move the entry, so eviction is by insertion order, not LRU. (b) The key is not the host name: `sans` comes from `tlsconfig.get_cert` (`m/addons/tlsconfig.py:634-674`) and holds the upstream certificate's CN and SANs, the client SNI, **and the upstream address** (`:670-672`). One host reached at several resolved IPs therefore produces several keys. (c) The CRL distribution point is fixed when the leaf is first minted; it is not part of the key | **confirmed + refinements**; the round-3 basis for "not binding" is replaced (CONV-ABS-81) |
| 2 | **T-137** 5 upstream connections per address per client connection | `m/proxy/server.py:109` `self.max_conns = collections.defaultdict(lambda: asyncio.Semaphore(5))`, created in `ConnectionHandler.__init__` (`:105`), so there is one map per client connection. `:206` `async with self.max_conns[command.connection.address]:`. **Refinement:** the `async with` block spans the connect **and** `await self.handle_connection(command.connection)` (`:259-260`). The permit is held for the upstream connection's whole life. This caps **simultaneously open** connections per address, not concurrent connect attempts. A sixth one waits until one of the five closes | **confirmed + refinement** |
| 3 | **T-138** 1 s live-reload poll | `m/addons/script.py:74` `ReloadInterval = 1`; `watcher()` (`:133-152`): `last_mtime = 0.0`, then loop `os.stat(...).st_mtime`; `if mtime > last_mtime: self.loadscript()`; `await asyncio.sleep(ReloadInterval)`. **Refinements:** the trigger is a strict mtime increase (`:147`); the first pass loads the script (mtime > 0.0); a `FileNotFoundError` removes the script from `options.scripts` for good (`:141-146`), which pass-1 r2 row 7l already records. "Within about 1 s" means one poll interval plus import time | **confirmed + refinement** |
| 4 | **R-12** terminal close kills mitmdump without draining | **Handler set:** a package-wide search finds only `m/tools/main.py:128-129` (`loop.add_signal_handler` SIGINT/SIGTERM), `:132-133` (Windows fallback), `:138` (SIGPIPE → `SIG_IGN`), and `m/utils/debug.py:130-131` (SIGUSR1/2). There are **0** `SIGHUP` references in `mitmproxy/`. In the venv, `SIGHUP` occurs only under `urwid/` (console UI, not loaded by mitmdump). Launcher trap: `L:97` `trap '…' EXIT INT TERM`. **Delivery, now documented from authorized man pages (r3 rated it MEDIUM for lack of a source):** (a) `termios(4)` "Modem Disconnect": on hangup "the SIGHUP signal is sent to the controlling process" (the user's interactive shell, the session leader per `intro(2)` "Controlling process"); (b) `zshoptions(1)` `HUP <Z>` (on by default): "Send the HUP signal to running jobs when the shell exits", and `zshmisc(1)` JOBS: "running jobs will be sent a SIGHUP signal, if the HUP option is set"; (c) independently of (b), `_exit(2)`: "If the process is a controlling process …, the SIGHUP signal is sent to the foreground process group of the controlling terminal". **Why mitmdump is in that group:** the launcher is a non-interactive script (`L:1` `#!/bin/zsh`), and `zshoptions(1)` `MONITOR` is "Set by default in interactive shells" only. With job control off, the `&` child at `L:75` stays in the script's process group, which is the foreground job. **Why SIGHUP keeps its default action:** `zshmisc(1)` SIGNALS: "The INT and QUIT signals for an invoked command are ignored if the command is followed by `&` and the MONITOR option is not active". Only INT and QUIT change; HUP is inherited as default, and mitmproxy installs no SIGHUP handler | **confirmed; delivery upgraded MEDIUM → HIGH (documented, not exercised)**. r3's "no authorized source covers" is retracted (CONV-ABS-82) |
| 5 | **CONV-ABS-73** (a failed Kev call costs from milliseconds to 2.5 s; no "typical" figure) | `py311/socket.py:827-846`: per address, `settimeout(timeout)` then `sock.connect(sa)`. A refused connect raises at once and is caught. A black-holed connect blocks until the 2.5 s timeout. `HK:113` `urlopen(req, timeout=KEV_TIMEOUT)`; `HK:120-121` catches `OSError`/`URLError` and returns `(None, None)` | **confirmed** |
| 6 | **CONV-ABS-74** (anchors `SL:118`, `SL:121`, `SL:136`) | Printed this round: `SL:102` `QUERY = (`; `SL:103` the first selector line (no window); `SL:118` contains `[1m]`; `SL:121` contains `[30m]`; `SL:135` is blank; `SL:136` `SPARK = "▁▂▃▄▅▆▇█"` | **confirmed** |
| 7 | (found while auditing R-12) **R-10** "Ctrl-C orphans only before `m/tools/main.py:128`" | r2/r3 stated this without a source for *why* mitmdump survives an early Ctrl-C. `zshmisc(1)` SIGNALS (row 4) supplies it: mitmdump starts with SIGINT **ignored**. If Ctrl-C comes before `main.py:128` replaces that disposition, the launcher dies (its trap is not armed until `L:97`) while mitmdump ignores the signal, so mitmdump is orphaned. After `:128`, SIGINT runs `master.shutdown` (DumpMaster has no `prompt_for_exit`; that method exists only in `m/tools/console/master.py:80`, and `main.py:119` falls back to `shutdown`). **New corollary:** SIGQUIT stays ignored for the life of the process (no handler anywhere), so Ctrl-\ never stops mitmdump | **confirmed, now grounded; one corollary** |

### A.2 Retractions this round

| Marker | Claim | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-81** | r3 §B.1 T-136 "not binding: 85 upstream hosts observed across all windows" | Hosts are not cache keys. A key is `(CN, SANs)`, where the SANs include the upstream address, so one host can occupy several slots. No authorized source counts distinct keys per process. **What stands, on a different basis:** eviction cannot change behavior, because a re-mint reuses the CA key (no key generation, `certs.py:427`) and only re-signs. A full cache costs CPU, not correctness. The "no expiry re-check" half of T-136 is unaffected | `m/certs.py:576-580,771-819`; `m/addons/tlsconfig.py:634-674` |
| **CONV-ABS-82** | r3 §B.2 R-12 "Delivery of SIGHUP … MEDIUM, because it rests on tty/shell hangup semantics that no authorized source covers" | `termios(4)`, `intro(2)`, `_exit(2)`, `zshoptions(1)` (`HUP`, `MONITOR`) and `zshmisc(1)` (JOBS, SIGNALS) document the whole chain (row 4). Confidence becomes **HIGH (documented, not exercised)**. The remaining assumption is that the window's interactive shell is a session leader holding the terminal, which is the standard terminal-emulator setup | §A.1 row 4 |

Neither retraction changes a value, class, key or owner item.

---

## B. Systematic mitmproxy 12.3.1 numeric-limit sweep

### B.1 Method and scope

1. **Mechanical enumeration.** `sweep.py` walks all 254 `.py` files under `m/`, parses each with `ast.parse`, and records every `int`/`float`
   constant (bools excluded, unary minus folded) with file, line, parent-node kind and source line. Separately, it records every module-level and
   class-level assignment whose value contains a numeric literal.
2. **Scope = files on the legacy production path.** The launcher runs `mitmdump --set flow_detail=1 --listen-port N -s dgx_proxy.py` (`L:75`).
   `tools/dump.py:19-26` loads `addons.default_addons()` (`m/addons/__init__.py:34-67`, 31 addons) plus `Dumper`, `KeepServing`,
   `ReadFileStdin`, `ErrorCheck`; the master adds `TermLog`. P2r6 found no `config.yaml`. The legacy addon sets no mitmproxy option (no `ctx.options`
   writes in `dgx_proxy.py`; its hooks are `request`, `responseheaders`, `response`, `error`, `websocket_start`, `websocket_end`,
   `PX:524-548`). **In scope:** every module of the core, proxy, net/http, TLS, WebSocket and certificate code, plus all loaded addons, including
   addons that are loaded but inert. **Out of scope (not reachable in regular mode with these options):** `tools/console/`, `tools/web/`,
   `contentviews/` (used only at `flow_detail >= 3`, `m/addons/dumper.py:118-124`), QUIC/HTTP3/DNS/UDP layers and addons, `platform/`
   (transparent mode), `io/` (no `rfile`/`save_stream_file`), `test/`, `utils/pyinstaller|emoji|magisk`, and the non-TLS `contrib/` parsers.
   `out/all.tsv` keeps the out-of-scope rows too.
3. **Mechanical trivial filter.** Values 0, 1, 2, −1, 0.0, 1.0 and every literal used as an index or slice bound. The trivial rows in
   call/keyword/assignment contexts were still listed and read (`stacklevel=2`, `sys.exit(1)`, `pop(0)`, enum members, …). Two of them are
   operative: `ReloadInterval = 1` (T-138) and `enable_push = 0` (h2 only, folded into T-124 below).
4. **Manual review** of all 333 non-trivial in-scope rows and all 120 in-scope named numeric assignments. Each one was classified as
   **operative** (buffer or frame size, header or body limit, cache size, timeout, retry count, queue or concurrency length), **protocol**
   (status codes, ports, RFC or record-format constants, version gates), or **incidental** (formatting, indentation, display, debug-only).
   Operative rows were then traced to whether the legacy configuration activates them.
5. **Adjacent defaults on the same path** that are not literals in the mitmproxy package (asyncio stream and server defaults, h2/h11
   library defaults) were checked where mitmproxy relies on them (§B.4).

### B.2 Counts

| Measure | Count |
|---|---|
| `.py` files parsed (whole package) | 254 (176 contain numeric literals) |
| Numeric literals, whole package | **3,417** |
| Named numeric assignments, whole package | 827 |
| Literals in in-scope files (87 files) | **972** |
| …trivial (mechanical filter) | 639 |
| …non-trivial, reviewed one by one | **333** |
| Named numeric assignments in scope, reviewed | 120 |
| Classification of the 333 | **protocol 214** (64 of them in `net/http/status_codes.py`) · **incidental 82** · **operative 37 literals at 35 distinct sites** |
| Operative sites by status | **already catalogued 10** (9 sites, plus `ReloadInterval` from the trivial bucket) · **active, not catalogued 8** · **HTTP/2-only 5** · **inactive under legacy options 14** |

### B.3 Operative sites (complete list)

**Already catalogued (confirmed unchanged):** `certs.py:40,41,44,328` and `options.py:9` → T-125; `certs.py:541` → T-136; `options.py:140` →
T-124; `options.py:243` → T-122; `proxy/server.py:109` → T-137; `addons/script.py:74` → T-138.

**Active, not catalogued (8 sites, 5 limits):**

| Site | Value | Effect in legacy | Bears on legacy behavior? | Disposition |
|---|---|---|---|---|
| `proxy/server.py:285` `reader.read(65535)`; `proxy/layers/tls.py:288` `bio_read(65535)`, `:416` `tls.recv(65535)` in a loop that drains every decrypted record before handing data on | 65,535 B per read | sets the size of the pieces fed to `response.stream` callables, which is the SSE tap's `feed()` granularity | Only through the feed boundaries, which are already a modelled behavior: P3r3 cites `server:285` for BC-PX-040, and BC-PX-045 states the chunk-independent contract that the parity harness tests. Not a limit any client can observe | **no new row**: cross-reference on **T-065** (§C.1) |
| `net/tls.py:194`, `:243` `@lru_cache(256)` on `create_proxy_server_context` / `create_client_proxy_context` | 256 SSL contexts each | contexts keyed by the TLS option tuple; legacy options never change, so only a handful exist per process | No: a miss rebuilds a context (CPU only). Never approached | no row (incidental cache) |
| `certs.py:42` `CRL_EXPIRY = 7 d` with `:512-514` (last update now − 2 d, next update now − 2 d + 7 d) | dummy CRL valid **5 days forward**, built once per cert store (`certs.py:630`, regenerated at `tlsconfig.py:532` on CA option change) | When an upstream leaf has a CRL distribution point and `upstream_cert` is on (default), the minted leaf points to `<upstream CRL scheme+host>/mitmproxy-<CA serial>.crl` (`tlsconfig.py:653-663`), and the `request` hook answers that path with the dummy CRL (`:676-684`) | No observed effect: a client must fetch and check CRLs, and no legacy client is known to. Not verified from an authorized source for Node. The launcher exports only `HTTPS_PROXY` (`L:79`), so an `http://` CRL fetch would bypass the proxy and get the real issuer's CRL anyway | no row; **T-125** note (§C.1) and S-4 |
| `addons/dumper.py:179` `max(shutil.get_terminal_size()[0] - 25, 50)` at `flow_detail == 1` | URL clipped to (columns − 25), at least 50 | stdout is redirected to `$MLOG` (`L:75`), so the size falls back to `COLUMNS` or `(80, 24)` (py311 `shutil.py:1398-1437`) → URLs over 55 chars are clipped with `…` in the per-window log | No: the mitmdump log is diagnostic, not a D4/D7 surface. The ` HTTP/2.0` suffix that P2r5 counted is appended after the clipped URL (`dumper.py:184-193`), so that check is unaffected | no row (log formatting) |

**HTTP/2-only (5 sites): not live in production.** P2r5 found 0 ` HTTP/2.0` request lines in 38 logs. `proxy/layers/http/_http_h2.py:53-55,66`
(local `initial_window_size` and connection window 2³¹ − 1, `max_frame_size` and `max_inbound_frame_size` 2¹⁷ = 131,072 B);
`proxy/layers/http/_http2.py:489` (`provisional_max_concurrency = 10` streams until the server's first SETTINGS), `:498` (`enable_push = 0`).
The h2 library defaults that mitmproxy does not override are `h2/connection.py:320,335,358-360` (max header list 65,536 B, local
`MAX_CONCURRENT_STREAMS` 100) and `:323` (closed-stream memory 65,536). All of these are folded into **T-124** as one "h2 parameters" row (§C.1).
That is the same disposition r1 gave the 58 s ping: NC only if hylo ever speaks h2 upstream, which HY-PROTO-1 excludes.

**Inactive under the legacy options (14 sites):** `proxy/layers/websocket.py:243` `FRAGMENT_SIZE = 4000` (used only when a message's length
changes, `:256-272`; legacy registers no `websocket_message` hook, so the original framing is always reused); `proxy/server.py:47`
`UDP_TIMEOUT = 20` (UDP only, `:116-119`); `addons/keepserving.py:39` (only with `rfile`/replay, `:43-54`); `addons/command_history.py:11`
(console history, nothing appended in mitmdump); `addons/eventstore.py:13` (instantiated only by `tools/console/master.py:42` and
`tools/web/master.py:36`); `command.py:195`; `options.py:8` `content_view_lines_cutoff` 512 (`flow_detail >= 3`); `proxy/layer.py:31,109`
(`proxy_debug` only); `net/free_port.py:10` (only for port 0, `mode_servers.py:293-295`); `net/tls.py:89` (TLS-version probe);
`addons/core.py:19`, `proxy/mode_specs.py:90`, `addons/browser.py:170` (8080 defaults, overridden by `--listen-port`).

**Protocol constants of note (no row; recorded for `hylo ca`):** `certs.py:434` a leaf gets a CN only if it is shorter than 64 characters
(RFC 5280 upper bound on common names); SANs carry the identity either way. `certs.py:646` writes CA files with umask `0o77` (owner-only).

### B.4 Adjacent defaults on the path (not mitmproxy literals)

| Default | Value (py311; runtime 3.12 not read) | Where mitmproxy relies on it | Bears on legacy? | Disposition |
|---|---|---|---|---|
| Proxy listener backlog | 100 (`py311/asyncio/base_events.py:1436`) | `m/proxy/mode_servers.py:307` `asyncio.start_server(self.handle_stream, host, port)` with no `backlog` | No: one Claude Code window per proxy. Failure mode only, the same kind as T-129 for the exporter | no row; noted under O-1's proxy counterpart |
| StreamReader limit | 64 KiB; reading pauses above 2 × limit (`py311/asyncio/streams.py:23,505`) | `asyncio.open_connection` / `start_server` with no `limit` (`m/proxy/server.py:212`, `mode_servers.py:307`) | No: mitmproxy calls `read(65535)`, never `readline` | no row |
| Write high-water mark and backpressure | 64 KiB (`py311/asyncio/transports.py:314-317`) | `m/proxy/server.py:297,330-339`: after every read, `drain_writers()` awaits `drain()` on **every** transport of the client connection before reading again | Shapes memory only: a streamed (pass-through) flow holds about 64 KiB of write buffer plus about 128 KiB of read buffer per connection, and a slow client throttles reads from the upstream. Buffered bodies (T-127) are unaffected | no row; **P-3** refinement (§D) |
| HTTP/1 head size | **no limit**: mitmproxy uses h11's `ReceiveBuffer.maybe_extract_lines()` (`m/proxy/layers/http/_http1.py:9,285,408`) but not `h11.Connection`, whose 16 KiB cap (`h11/_connection.py:69,485`) therefore never applies | every request and response head | Not observably (P2r7 T-6: Claude Code heads are small) | **T-139**, a catalogue entry for P2r7 T-6 (§C.1). Same family as T-126/T-127 (absent limits); not new to the model |

### B.5 Sweep result

No operative limit that bears on legacy behavior is missing from the catalogue. Of the 35 operative sites, 10 were already catalogued. The other
25 are h2-only and not live (5), inactive under the legacy options (14), or active but behavior-neutral (8 sites, 5 limits). Of those 5 limits,
the read size is already modelled as BC-PX-040/045, and the CRL, SSL-context cache and log-width limits have no observable legacy effect. The
only catalogue addition is **T-139**. It records the absent HTTP/1 head limit that P2r7 found, so that the hylo named constant has a catalogue
row like T-126/T-127. Three existing rows get notes: T-065, T-124, T-125.

---

## C. Catalogue update (delta to r3 §C; r3 §C stays authoritative for every row not shown)

### C.1 Changed and new rows

| T | Value (op) | Site | Class | Rat. | Rationale | Key / NC reason | Last |
|---|---|---|---|---|---|---|---|
| 065 | 64,000 B (`>`) | PX:368,408 | CFG | OWNER-C | purpose "runaway line guard", value not. **Note R4:** feed pieces are at most 65,535 B per socket read (m/proxy/server.py:285; TLS m/proxy/layers/tls.py:416); boundary behavior is BC-PX-040/045 | `proxy.sse_tap.max_line_bytes` (OD-35) | **R4** |
| 124 | h2 parameters: 58 s ping; local window 2³¹−1 (stream and connection); max frame 2¹⁷; provisional 10 streams before SETTINGS; push off; h2-lib max header list 65,536 B, local max streams 100 | m/options.py:137-140; m/proxy/layers/http/_http_h2.py:53-55,66; m/proxy/layers/http/_http2.py:489,498; h2/connection.py:320,335,358-360 | NC | C | tool and library defaults; h2 not live (P2r5) | NC, only if hylo speaks h2 upstream (HY-PROTO-1 excludes it) | **R4** |
| 125 | RSA 2048 (e = 65537); CA 3,650 d; leaf 199 d span, back-dated 2 d (197 d forward); leaf reuses the CA key; SHA-256; CN only if < 64 chars; dummy CRL next update +5 d, served at `/mitmproxy-<serial>.crl` on the upstream CRL host | m/options.py:9,226-233; m/certs.py:40-44,328,340-341,427-434,493,512-514,803-811; m/addons/tlsconfig.py:631-684 | NC | C | tool default | NC in `hylo ca` with comments; whether hylo leaves carry a CRL distribution point is a P4 design choice (no legacy client checks CRLs) | **R4** |
| 136 | 100 leaves, FIFO by insertion (hits do not refresh), key = (CN, SANs incl. SNI and upstream IP), no expiry re-check | m/certs.py:541,576-580,771-819; m/addons/tlsconfig.py:634-674 | NC | C | tool default; eviction only re-signs (CPU), so never a behavior change (CONV-ABS-81) | NC in `internal/ca`; re-mint before `not_after` for a long-lived proxy (OD-50) | **R4** |
| 137 | 5 open upstream connections per address per client connection (permit held for the connection's life) | m/proxy/server.py:105-109,206-262 | N/A | C | tool default | N/A: Go transport limits (HY-PROTO-1) | **R4** |
| 138 | 1 s mtime poll; strict `mtime >`; vanished file removes the script | m/addons/script.py:74,133-152 | DROP | C | tool default | — (OD-26; compiled binary) | **R4** |
| **139** | no HTTP/1 head size limit (h11 `ReceiveBuffer` without `h11.Connection`'s 16 KiB cap) | m/proxy/layers/http/_http1.py:9,58,285,408; h11/_connection.py:69,485 (unused) | NC | N/A | absent limit; unobservable for Claude Code traffic (P2r7 T-6) | NC in `internal/proxy` with a comment: hylo's listener will have a finite head limit (Go `http.Server.MaxHeaderBytes` defaults to 1 MiB), a deviation that applies only to heads no legacy client sends | **R4** |

### C.2 Totals

| Measure | r3 | **r4** |
|---|---|---|
| Thresholds | 138 | **139** (broad 105 + r1 30 + r3 3 + r4 1) |
| By class | CFG 96 · NC 28 · DROP 7 · OOS 2 · EXT 2 · NEW-H 2 · N/A 1 | **CFG 96 · NC 29 · DROP 7 · OOS 2 · EXT 2 · NEW-H 2 · N/A 1** |
| By rationale | OWNER 27 · Dv† 18 · N/A 7 · EXT 2 · resolved 84 | **OWNER 27 · Dv† 18 · N/A 8 · EXT 2 · resolved 84** |
| Rationale resolved | 111 of 138 | **112 of 139** (94 final + 18 awaiting one bulk "yes") |
| Owner must supply | 27 in 7 groups | **27 in 7 groups** (unchanged) |
| Last changed in R4 | — | 7 rows: T-065, T-124, T-125, T-136, T-137, T-138, T-139 |

### C.3 OD-57 lists

**Unchanged.** Bulk confirmation (18 rows, Dv†): T-003, T-005, T-007, T-008, T-009, T-022, T-025, T-038 (covers T-039), T-050, T-060, T-061,
T-064, T-076, T-081, T-088, T-094, T-101, T-119. Owner supplies a rationale (27 rows in groups A–G): exactly as r3 §C.6. T-139's rationale is
N/A (an absent limit), and the round-4 notes on T-065/T-124/T-125/T-136..T-138 do not change any rationale status.

---

## D. NFR catalogue changes (delta to r3 §E)

| NFR | Change | Evidence |
|---|---|---|
| P-3 Streaming latency (refined) | Pass-through flows are backpressured: after each read, mitmproxy drains every writer of the client connection (64 KiB high-water mark, asyncio default), so a streamed flow's proxy memory is bounded at about 64 KiB written plus about 128 KiB read per connection. Feed pieces are at most 65,535 B (BC-PX-040/045) | §B.3, §B.4; T-065 |
| P-7 mitmproxy internal caps (refined) | T-136 is keyed by (CN, SANs incl. IP), so it is not a host count; eviction costs only a re-sign. T-137 caps open connections, with the permit held for each connection's life | §A.1 rows 1-2 |
| R-10 Pre-trap orphan window (grounded) | mitmdump starts with SIGINT and SIGQUIT ignored (`&` without MONITOR, `zshmisc(1)` SIGNALS). An early Ctrl-C therefore orphans it until `m/tools/main.py:128` installs its handler. SIGQUIT stays ignored for the process's whole life | §A.1 row 7 |
| R-12 Terminal close (confidence) | SIGHUP delivery is now **HIGH, documented**: `termios(4)`, `_exit(2)`, `zshoptions(1)` HUP/MONITOR, `zshmisc(1)` JOBS/SIGNALS. hylo implication unchanged: detached shared proxy (OD-66 (a)), drain (OD-38), stop (OD-50), and SIGHUP given an explicit meaning | §A.1 row 4; CONV-ABS-82 |
| S-4 CA (refined) | adds: CN only when shorter than 64 chars; minted leaves copy the upstream's CRL distribution point host with a local path, answered by a dummy CRL valid 5 days forward from process start; CA files written owner-only | T-125 |
| O-1 (note) | proxy listener backlog 100 (asyncio default, py311) — failure mode only, the counterpart of the exporter's 5 (T-129) | §B.4 |

Missing-NFR list (r3 §E.6): unchanged.

---

## Delta Summary

- **Audit (target A):** 7 rows checked with fresh evidence. T-136, T-137, T-138, R-12, CONV-ABS-73 and CONV-ABS-74 are all **confirmed**. R-10 is
  **grounded** (and one corollary added). Refinements: T-136 (insertion-order eviction; key includes SNI and upstream IP; CRL point fixed at first
  mint), T-137 (permit held for the connection's life), T-138 (strict-mtime trigger; vanished file), R-12 (delivery documented → HIGH).
  **2 narrow retractions:** CONV-ABS-81 (T-136's "85 hosts" basis) and CONV-ABS-82 (R-12's "no authorized source"). Neither changes a value,
  class, key or owner item.
- **Sweep (target B):** 3,417 literals in 254 files enumerated mechanically; 972 in scope (87 files); 639 trivial filtered; 333 non-trivial and
  120 named constants reviewed by hand → protocol 214, incidental 82, operative 37 literals at 35 sites (10 catalogued, 8 active and
  behavior-neutral, 5 h2-only and not live, 14 inactive). Adjacent asyncio/h11/h2 defaults checked (§B.4). **0 missing operative limits that bear
  on legacy behavior.**
- **Catalogue (target C):** 1 row added as a catalogue entry for an already-modelled absent limit (T-139 ← P2r7 T-6); 6 rows annotated (T-065,
  T-124, T-125, T-136, T-137, T-138). Totals 139; resolved 112 of 139; OD-57 lists unchanged (18 bulk / 27 owner).
- NFR refinements: P-3 (backpressure bound), P-7, R-10, R-12, S-4, O-1 note.
- Owner items: none new (OD-90..OD-93 unused). Retraction markers used: CONV-ABS-81, -82 (83, 84 unused).

## Remaining Gaps (verbatim-carryable)

1. Owner answers for OD-57: bulk confirmation of 18 Dv† rows and 27 owner rationales in 7 groups (r3 §C.6, unchanged).
2. T-078's Prometheus port-allocation source is still unverified (no network). It is a rationale label only.
3. Pass 5 (sibling, r3 not yet written): confirm in its register unbounded DNS (status line, hook, preflight), the `subprocess.run` total deadline,
   the strict operators of H-5/H-6, and the T-139 named constant if pass 5 lists `internal/proxy` constants.
4. asyncio values in §B.4 are CPython 3.11's. The production interpreter is 3.12.10, whose stdlib is not an authorized source. These values are
   behavior-neutral at legacy scale either way.
5. P1/P3 test-plan notes: boundary table tests for the `SL:674` clamp, the `cols > 0` trim, and T-090..T-092's strict operators. The BC-PX-045
   chunk-independence property already covers T-065's interaction with the 65,535 B reads.

## Novelty Assessment

Novelty: NITPICK — findings are refinements, not gaps.

Removing this round's findings would not change how the system is specified. The mandated systematic sweep found no operative mitmproxy limit
that bears on legacy behavior and is missing from the catalogue. Every operative site is already catalogued, is on the h2 path (which is not live),
is inactive under the legacy options, or has no observable effect. The one item not already in the model elsewhere is the read size, and it is
already the basis of BC-PX-040/045. T-139 adds a P2r7 finding to the catalogue; it is not a discovery. The round-3 items all survived an
independent audit. The two retractions replace a basis and a confidence label, and change no value, class, key, rationale status or owner item.
The man-page evidence raises R-12's confidence but leaves its hylo implication unchanged.

## Convergence Declaration

Pass 4 has converged — findings are nitpicks, not gaps.

## State Checkpoint

```yaml
pass: 4
round: 4
status: complete
timestamp: 2026-11-14T11:40:00Z
novelty: NITPICK
files_scanned: mitmproxy 12.3.1 whole package (254 .py files, AST sweep) with manual reads of certs.py, addons/tlsconfig.py, addons/script.py, addons/dumper.py, addons/keepserving.py, addons/command_history.py, addons/__init__.py, tools/dump.py, tools/main.py, proxy/server.py, proxy/mode_servers.py, proxy/utils.py, proxy/layers/tls.py, proxy/layers/websocket.py, proxy/layers/http/{__init__,_http1,_http2,_http_h2}.py, net/tls.py, options.py; h2/connection.py, h11/_connection.py, h11/_receivebuffer.py (adjacent-default checks); py311 socket.py, shutil.py, asyncio/{streams,base_events,transports,selector_events}.py; man zshmisc, zshoptions, termios, intro(2), _exit(2); legacy L:1,60-104, PX:98-170,362-412,524-548, SL:102-136, HK:108-122
sweep: {files_parsed: 254, literals_total: 3417, literals_in_scope: 972, trivial_filtered: 639, nontrivial_reviewed: 333, named_constants_in_scope_reviewed: 120, protocol: 214, incidental: 82, operative_literals: 37, operative_sites: 35, operative_catalogued: 10, operative_active_uncatalogued: 8, operative_h2_only: 5, operative_inactive: 14, missing_behavior_bearing_limits: 0}
thresholds: {total: 139, new_this_round: 1, by_class: {CFG: 96, NC: 29, DROP: 7, OOS: 2, EXT: 2, NEW-H: 2, NA: 1}, rationale: {owner: 27, bulk_confirm: 18, na: 8, ext: 2, resolved_other: 84}, resolved: 112}
verification: {confirmed: 4, confirmed_with_refinement: 3, retracted_basis_or_label: 2}
retractions: [CONV-ABS-81, CONV-ABS-82]
conv_abs_unused: [83, 84]
new_owner_items: []
od_unused: [OD-90, OD-91, OD-92, OD-93]
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r4/
next: none for pass 4 (orchestrator applies strict-binary rule)
```
