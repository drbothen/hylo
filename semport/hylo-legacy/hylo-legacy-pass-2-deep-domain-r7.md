# Pass 2 Deepening — Round 7: Domain Model (mitmproxy 12.3.1 option-default audit, asyncio.run cancellation link, final sweep, canonical pointer amendments) — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Re-read this round: `claude-dgx:15-30,60-110` (launcher env, mitmdump command line,
  trap), `dgx_proxy.py:79-83,120-135,161-166`, `dgx_preflight.py:1-40`.
- Authorized extra sources (read only, never imported or executed):
  - **mitmproxy 12.3.1** (`version:5`): `options`, every `addons/*.py` `load()` declaration, `addons/__init__`, `tools/dump`, `tools/main`, `master`,
    `addons/tlsconfig`, `addons/proxyserver`, `addons/next_layer`, `addons/dumper`, `addons/onboarding`, `addons/update_alt_svc`,
    `addons/command_history`, `net/tls`, `proxy/layers/tls`, `proxy/layers/http/__init__`, `proxy/layers/websocket`, `proxy/server`,
    `proxy/commands`, `utils/asyncio_utils`. Bundled dependency versions from their `dist-info` directories: certifi 2026.10.23, pyOpenSSL 26.4.0,
    cryptography 50.0.2, h11 0.16.0, h2 4.4.1, wsproto 1.3.2.
  - **CPython 3.12.10**, the venv's base interpreter (`.mitmenv/pyvenv.cfg` `home` → the uv `cpython-3.12` symlink → `cpython-3.12.10`;
    `include/python3.12/patchlevel.h:26`): `asyncio/runners`, `asyncio/tasks`, `asyncio/futures`, `asyncio/base_events`, `asyncio/locks`. Read
    for the asyncio.run cancellation link only.
- Inputs read: pass-2 r4 (§1 connection model, §2.2 bind), r5 (section map), r6 (complete; §5 is the canonical pointer table), pass-3 r4 (header,
  §0, §3 V-1..V-3, §4-§7.1, carried checks, Delta, Gaps). **Pass-3 round 5 (`…-pass-3-deep-behavioral-contracts-r5.md`) did not exist at write
  time** (checked at start and at 07:19Z). Nothing to reconcile, nothing edited.
- Method: static reading only. Nothing from legacy ran, no proxy, nothing networked. `CLAUDE.local.md` was not read. One scratch script
  (`scratchpad/p2r7/opts.py`, run with `/usr/bin/python3 -I`) parses mitmproxy's source files as **AST data** (it imports nothing from mitmproxy)
  and lists every `add_option(...)` call, positional or keyword form. Output: `scratchpad/p2r7/opts.tsv` (112 calls), `loaded_opts.tsv` (the 93
  options a mitmdump process registers).
- Notation: a bare `:N` means `dgx_proxy.py`; `L:N` = `claude-dgx`; mitmproxy as "mitmproxy 12.3.1 `<module>:<line>`" (abbreviated `m/<module>:<line>`
  inside tables); `cpy <module>:<line>` = CPython 3.12.10 stdlib. Addresses in examples are RFC 5737.
- Numbering: owner items follow the orchestrator's settlements (OD-01..OD-38, then pass-3 r5's OD-39 and OD-40, final) and continue at **OD-41**.
  Retractions would start at **CONV-ABS-25** (pass-3 r5 issued none; 21 and up are free). **None was needed this round** (§5).

---

## 0. Orchestrator settlements recorded and items closed

| Settlement (orchestrator, 2026-11-14) | Items closed | Consequence |
|---|---|---|
| **OD numbering.** Pass-3 r4's OD-35 (Go tap lines over 64,000 bytes) and OD-36 (backfill has no phase or package in `docs/PLAN.md`) keep their numbers. Pass-2 r6's items are renumbered: r6 "OD-35" tcp_timeout / HY-TIMEOUT-1 → **OD-37**; r6 "OD-36" in-flight behavior at hylo exit → **OD-38** | the r6/P3r4 OD-35/OD-36 collision | Wherever r6 says OD-35 read **OD-37**; wherever r6 says OD-36 read **OD-38**. Base list after the settlement: OD-01..OD-38, 36 pending, 2 ruled (OD-24, OD-27). This round adds OD-41 and OD-42 (§3) |
| **Pass-3 r5 owner items (final numbers).** **OD-39**: exporter rebuild trigger and missed appends. It rebuilds only when the ledger size changes, so changes to the hook log alone and lines appended during a read are skipped (BC-EX-027). Recommendation: approved deviation, Go tracks the consumed byte offset and watches both files. **OD-40**: confirm that the P3 exit criterion's "identical routing decisions" means the per-request lane choice, not the text of the routing-decisions log | numbering collision with this round's first draft | List before this round: **OD-01..OD-40, 38 pending, 2 ruled**. This round's items are **OD-41** (upstream TLS policy) and **OD-42** (connect timeout). No pass-2 content changes: OD-39 is pass-3/exporter material, and OD-40 is consistent with pass-3 r4's note that decision-log text is OOS (no consumer reads it) |
| **The 36 unpaired DGX requests are all dated 2026-11-11.** Request vs reply+error per day: 11-10 282/282, 11-11 4265/4229, 11-12 85/85, 11-13 108/108, 11-14 15/15 | r6 Remaining Gap 2 (a) and (b) | **O-1 confirmed** (r6 §1.4): the orphans predate the `error` hook, which was added after that day's incident (`:311-315` docstring). Proxy shutdown (SIGTERM, SIGHUP or SIGKILL) is **ruled out as the cause in the retained ledger**: every day after 11-11 pairs exactly. O-2..O-6 stay theoretical. OD-38 (exit semantics) keeps its design rationale (§2 below makes the SIGTERM half HIGH confidence), but no production orphan supports it |
| **F-2 not observed.** The 4 `Client disconnected.` DGX errors came 0, 342, 0 and 181 s after the session's latest request. None is near 600 s | r6 Remaining Gap 3 | The 600 s inactivity cut (r6 §1.3) has **not happened in production**. It stays a **latent** failure mode, and OD-37 stays pending. OD-16's cancel count is, as far as the retained ledger shows, all real cancels (or backend drops), not F-2 |

Owner rulings applied (not pending): strict stdio and the Python 3.11.7 oracle; degraded output byte for byte; CP-C01..C10 out of scope; D4-EX-1;
D4-EX-2; D13-D16; the hylo proxy, UI and exporter bind to loopback by default (legacy LAN risk accepted). Owner check after the soak, carried: the
VictoriaMetrics NaN capture.

---

## 1. Target A — every mitmproxy 12.3.1 option default the launcher does not override

### 1.1 Scope and count

- **What a mitmdump process registers.** `DumpMaster` adds `default_addons()` plus `Dumper`, `KeepServing`, `ReadFileStdin` and `ErrorCheck`
  (m/`tools/dump:19-26`); `Master` adds `TermLog` (m/`master:37-39`); `Options()` declares the core set (m/`options:15-247`). The 31 default addons are
  listed at m/`addons/__init__:34-67`. `intercept` and `view` declare options but **are not loaded by mitmdump**, and the `tools/web` and
  `tools/console` options belong to the other front ends. The three `add_option` calls at m/`proxy/server:508-521` sit under
  `if __name__ == "__main__"` (a test stub), and one in `addonmanager:99` is the generic method. **Result: 93 options.** No option is declared twice
  among them.
- **What the launcher sets.** `mitmdump --set flow_detail=1 --listen-port "$MITM_PORT" -s "$HERE/dgx_proxy.py"` (`L:75`). That covers
  `listen_port`, `scripts` and `flow_detail`. **`flow_detail` defaults to 1** (m/`addons/dumper:55`), so the `--set` is a no-op restatement. No
  `config.yaml` exists (r6 §0), and mitmdump reads no `MITMPROXY_*` option environment. **90 options run at their defaults.**
- **Environment the proxy process does read** (not an option, same class): `MITMPROXY_SSLKEYLOGFILE` or `SSLKEYLOGFILE`, read once at import
  (m/`net/tls:147-149`). The launcher neither sets nor clears it (`L:75` inherits the shell's environment). See §1.4 T-3.

### 1.2 Result by class

| Class | Count | Options |
|---|---|---|
| Set by the launcher | 3 | `listen_port`, `scripts`, `flow_detail` (= default) |
| Already recorded by earlier rounds, re-confirmed at the cited default | 12 | `listen_host` `""`, `block_global` True, `block_private` False, `proxyauth` None (r4 §2.2, r5 §1.1, r6 §0); `connection_strategy` eager (r4 D-1); `stream_large_bodies` None, `body_size_limit` None, `store_streamed_bodies` False, `validate_inbound_headers` True (P3r3, P3r4 §0, BC-PX-037); `tcp_timeout` 600 (r6 §1.3, OD-37); `confdir` `~/.mitmproxy` (r3 §3.1); `mode` regular |
| **Shape legacy behavior, not recorded before** | **11** | `ssl_insecure` False, `ssl_verify_upstream_trusted_ca` None, `ssl_verify_upstream_trusted_confdir` None (§1.3 T-1); `tls_version_client_min`/`_max`, `tls_version_server_min`/`_max`, `ciphers_client`, `ciphers_server` (§1.3 T-2); `http2` True (§1.3 P-1, ALPN mirroring); `websocket` True (§1.3 W-1) |
| Recorded now; **inert in production** but each needs a hylo constant or a P6 key | 22 | `http2_ping_keepalive` 58, `normalize_outbound_headers` True, `upstream_cert` True, `key_size` 2048, `certs` [], `cert_passphrase` None, `client_certs` None, `request_client_cert` False, `add_upstream_certs_to_client_chain` False, `tls_ecdh_curve_client`/`_server` None, `ignore_hosts` [], `allow_hosts` [], `tcp_hosts` [], `rawtcp` True, `anticomp` False, `connect_addr` None, `termlog_verbosity` info, `dumper_filter` None, `showhost` False, `onboarding` True, `onboarding_host` `mitm.it` (§1.5) |
| Inert: feature off, another proxy mode, or display only | 45 | `server` True (structural), `anticache`, `block_list`, `client_replay`, `client_replay_concurrency`, `command_history`, `dumper_default_contentview`, `export_preserve_original_ip`, `keepserving`, `map_local`, `map_remote`, `modify_body`, `modify_headers`, `keep_host_header`, `proxy_debug`, `rfile`, `readfile_filter`, `save_stream_file`, `save_stream_filter`, `hardump`, the 12 `server_replay*` options, `stickyauth`, `stickycookie`, `strip_ech`, `emudhra`, `emudhra_old`, `keep_alt_svc_header`, `upstream_auth`, `show_ignored_hosts`, `http3`, `http_connect_send_host_header`, `udp_hosts`, `content_view_lines_cutoff`, `protobuf_definitions` (§1.6) |
| **Total** | **93** | |

### 1.3 The options that shape legacy behavior (new)

#### T-1. Upstream certificate verification: on, against **certifi's bundle only** (the D13 question)

| Fact | Source |
|---|---|
| `ssl_insecure` defaults to **False**, so every upstream TLS connection uses `VERIFY_PEER` | m/`options:173-181`; m/`addons/tlsconfig:314-317` |
| The trust anchor: with `ssl_verify_upstream_trusted_ca` and `_confdir` both None (their defaults), mitmproxy loads **`certifi.where()`** and nothing else. It never calls `set_default_verify_paths`, so the **OS trust store, the macOS keychains and `SSL_CERT_FILE` are all ignored**. The bundle is certifi **2026.10.23** (the venv's `certifi-2026.10.23.dist-info`) | m/`net/tls:215-224`; m/`options:182-196` |
| **Hostname check** on top of the chain check: SNI is set and `X509_VERIFY_PARAM_set1_host` (or `_set1_ip` for an IP literal) is enabled, with `NO_PARTIAL_WILDCARDS` and `NEVER_CHECK_SUBJECT` (SAN only, no CN fallback) | m/`addons/tlsconfig:96-99,375-401` |
| SNI per leg: the eager Anthropic connection uses the client's SNI (`api.anthropic.com`). A rerouted flow's new server connection uses **`event.address[0]`, the backend host after the rewrite** (not the client's SNI), so an `https` backend is verified against its own name or IP | m/`addons/tlsconfig:319-320`; m/`proxy/layers/http/__init__:1130-1144` |
| A failed upstream handshake sets `conn.error` to a fixed text: **`Certificate verify failed: <OpenSSL X509 reason>`**; or the server's alert text (`tlsv1 alert unknown ca`, `sslv3 alert bad certificate`, `ssl/tls alert bad certificate`); **`The remote server does not speak TLS.`**; **`The remote server and mitmproxy cannot agree on a TLS version to use. You may need to adjust mitmproxy's tls_version_server_min option.`**; else `OpenSSL <repr>` | m/`proxy/layers/tls:305-354,400-401` |
| **Per-lane outcome under `eager`.** An upstream TLS failure on the CONNECT's own server does **not** kill the tunnel. mitmproxy logs `Unable to establish TLS connection with server (<err>). Trying to establish TLS with client anyway. …` (INFO, in the per-window log) and finishes the client handshake. Then every Anthropic-lane flow on that tunnel fails at once with that `error` (no new connect attempt), while DGX-lane flows on the same tunnel open their own backend connection and **succeed** | m/`proxy/layers/tls:606-619`; m/`proxy/layers/http/__init__:1101-1114`; r4 §1.2 |

**Domain consequences.**

1. **Legacy verifies strictly.** No legacy path disables upstream verification. That matches the orchestrator's reading of D13 ("strict
   verification required"). *Recorded as verified:* `docs/PLAN.md:165` (D13) does not itself mention upstream verification. It covers
   interception scope and CA trust. The requirement should be written down (HY-TLS-1).
2. **The trust anchor is a pinned snapshot of the Mozilla roots, not the OS.** Two observable cases differ from what an OS-store client would do:
   - A network with **TLS inspection** (a corporate root that exists only in the OS store) breaks the Anthropic lane only. Every Anthropic-lane
     request fails with `Certificate verify failed: unable to get local issuer certificate` (the OpenSSL reason string; the exact wording comes
     from OpenSSL and was not source-read), logged as `anthropic_upstream_error` **with attribution**, because the `request` hook runs before the
     connection is chosen (r4 §1.1). The DGX lane keeps working.
   - An **`https` backend with a private or self-signed CA** cannot be used at all. Legacy has no option to add a CA. Every routed flow fails
     with `Certificate verify failed: …`, logged as `dgx_upstream_error`. The same applies to `DGX_UPSTREAM=https://…` pointing at a plain-HTTP
     port: `The remote server does not speak TLS.` on every routed flow. Today `DGX_UPSTREAM` defaults to `http://` (`:79-81`), so neither
     happens in production.
3. **Interaction with the legacy CA install (r3 §3.1, conflict with D13).** Legacy installs the mitmproxy CA as `trustRoot` in the login keychain.
   That has **no effect on legacy's own upstream verification** (certifi only). A Go proxy that uses the OS verifier on macOS **would** trust that
   keychain root for upstream connections. On a machine migrating from legacy, hylo would then accept upstream certificates minted by the old
   mitmproxy CA. This is a cutover hygiene item for `hylo ca` / `hylo doctor` (detect and offer removal), not a parity item.

**hylo requirements and decision.**
- **HY-TLS-1 (default, consistent with D13 as the orchestrator reads it):** upstream verification is always on: chain plus hostname (SAN only, no
  CN fallback). There is **no** "skip verification" key. D15 is satisfied by a per-backend `tls.ca_file` (extra trust, P6) and, for mTLS
  backends, `tls.client_cert` (legacy cannot do either; §1.5).
- **OD-41 (new, pending): the upstream trust anchor.** (a) the OS store (Go `crypto/x509` system roots: the platform verifier on macOS and Windows,
  the system bundle on Linux); (b) an embedded Mozilla root snapshot, which is what legacy uses (via certifi); (c) the OS store plus per-backend
  `ca_file`. The choice changes behavior only in the two cases above (TLS inspection, private-CA backends), plus the keychain case in point 3.
  *Recommendation:* (c), as an approved failure-mode deviation. It fixes the TLS-inspection case and needs no new dependency. The error texts
  (`Certificate verify failed: …`) fall under OD-28 (text parity for upstream errors). The event name is unchanged (D7).

#### T-2. TLS versions and cipher suites, both legs

| Fact | Source |
|---|---|
| `tls_version_{client,server}_min` default **TLS 1.2**; `_max` default **UNBOUNDED** (TLS 1.3 when OpenSSL has it). TLS 1.1 and below need an explicit option | m/`addons/tlsconfig:157-186`; m/`net/tls:47-70` |
| `ciphers_{client,server}` None → mitmproxy's TLS 1.2 list `_DEFAULT_CIPHERS`, which includes CBC-SHA suites, static-RSA suites and **`DES-CBC3-SHA`** (3DES). TLS 1.3 suites are OpenSSL's defaults and cannot be configured (m/`tlsconfig:140`) | m/`addons/tlsconfig:34-61,82-92,250-255,341-346` |
| Every context sets `OP_CIPHER_SERVER_PREFERENCE` and `OP_NO_COMPRESSION`. `tls_ecdh_curve_*` None → OpenSSL's default groups | m/`net/tls:71,170-178` |

**Consequence.** Against `api.anthropic.com` (TLS 1.3) and a plain-HTTP backend, none of this is observable. It matters only for a TLS 1.2-only
`https` backend. **hylo:** the minimum is a named constant **TLS 1.2**, equal to legacy. Cipher suites are Go's defaults, which drop 3DES and the
static-RSA suites. That is an unobservable deviation for every peer legacy actually talks to. It is folded into OD-41 as sub-item (d) so that the owner
sees all TLS policy in one place. *Recommendation:* Go defaults, no cipher configuration key (a protocol/security constant under D15's exception
clause, with a comment).

#### P-1. `http2` True: the upstream leg **mirrors the client's protocol**

| Fact | Source |
|---|---|
| With `http2` True, the upstream connection offers **exactly the client's ALPN list** ("we want to keep things on the same protocol version … header capitalization"). If the client sent no ALPN, the upstream gets none | m/`addons/tlsconfig:322-339` |
| The client is answered with the protocol the upstream chose | m/`addons/tlsconfig:108-130` |
| Production: 0 ` HTTP/2.0` lines in 38 retained logs (P3r4 §0). Since the client is offered whatever Anthropic chose from the **client's own** offer, this means **both legs are HTTP/1.1** (either the client never offers `h2`, or the upstream declined it) | P3r4 §0; r4 §1.3 |

**Consequence.** Legacy never speaks HTTP/2 to Anthropic in production. h1 preserves header-name case on the wire; h2 lowercases it. Go's
`net/http` negotiates h2 automatically when its TLS config offers it (`http.DefaultTransport` sets `ForceAttemptHTTP2`; Go-side fact, not
source-read here). **HY-PROTO-1 (parity default, attached to OD-17):** the upstream leg uses the client's HTTP version (h1 ↔ h1). hylo must not
upgrade the Anthropic leg to h2 on its own. The `h2`-only knobs (`http2_ping_keepalive` 58 s, `normalize_outbound_headers`) are then inert, as in
legacy (§1.5).

#### W-1. `websocket` True: every Remote Control message is **kept in memory** and **logged**

| Fact | Source |
|---|---|
| A 101 response with `Upgrade: websocket` and a matching `Sec-WebSocket-Version` becomes a WebSocket flow **because `websocket` is True** | m/`proxy/layers/http/__init__:499-509` |
| Every complete message is appended to `flow.websocket.messages` and kept for the life of the connection. **Nothing in the package prunes it** (the only reassignment is `eventsequence:24-28`, used to iterate replays) | m/`proxy/layers/websocket:178-187`; package search |
| At the default `flow_detail` 1, the dumper prints **one line per message** (`… -> WebSocket text message -> …`) to the per-window log; message bodies only at ≥ 3. Pings and pongs are logged at INFO (`Received WebSocket ping from …`), which `termlog_verbosity` info prints | m/`addons/dumper:301-313`; m/`proxy/layers/websocket:196-200`; m/`proxy/commands:143-146` |
| The legacy addon's WebSocket hooks never log (dead path, r2 §4.5, BC-PX-027), so none of this reaches the ledger | r2 §4.5 |

**New failure mode F-3 (latent; magnitude unmeasured):** a long session with Remote Control (the bridge to `bridge.claudeusercontent.com`) grows
mitmdump's memory by the size of **every bridge message in both directions**, with no cap, until that WebSocket closes. The per-window log
(`${TMPDIR}/dgx-mitm.<pid>.<port>.log`, never deleted by the launcher: the trap at `L:97` only kills processes) grows by one line per message and
per ping. Neither is a D7 surface, and neither is a parity surface.

The bridge WebSocket is also subject to F-2: it is cut after 600 s with no frame in either direction. Pings count as activity (r6 §1.3: activity is
any `server_event`). Whether the bridge pings more often than every 600 s is **unknown** (owner check 2 below).

**hylo:** D16 already requires bounded in-memory buffers, so **HY-WS-1 is a default, not a new OD:** WebSocket messages are relayed without
retention beyond D16's bounded buffer. No per-message log line. The bridge idle limit is not tied to OD-37's request timeout: it is the
idle-connection rule HY-BIND-6, with a default that must exceed the bridge's ping interval (unknown; owner check 2).

### 1.4 Adjacent hard-coded behavior found during the audit (not options)

| ID | Behavior | Source | hylo |
|---|---|---|---|
| **T-3** | **TLS key logging from the environment.** If `MITMPROXY_SSLKEYLOGFILE` or `SSLKEYLOGFILE` is set when mitmdump starts, it appends the session secrets of **every** TLS connection, on both legs, to that file (creating parent directories). Anyone holding that file and a capture can decrypt the traffic, including `Authorization`/`x-api-key`. The launcher inherits the variable from the user's shell (`L:75`) and never mentions it. It is not in the r3 E-5 env count (42 names), which counts only names the legacy files read | m/`net/tls:118-149,187-189` | **HY-TLS-3 (default):** hylo never reads `SSLKEYLOGFILE` implicitly (Go `crypto/tls` writes key logs only when the program sets `KeyLogWriter`). If a debug key is ever offered, it is explicit config (D15) and `hylo doctor` warns while it is set. Not a parity surface |
| **T-4** | **No upstream connect timeout.** Server connections use `asyncio.open_connection(host, port)` with **no timeout** and no option for one. A refused or unreachable backend fails at once (`[Errno 61]`, `[Errno 65]`). A **silent** one (powered off, packets dropped) waits for the **OS TCP connect timeout**, and the client waits with it. The OS value was not source-read (judgment: tens of seconds to about two minutes, depending on OS and settings). The 600 s watchdog is far above it, and the launcher's 4 s limit applies only to the pre-launch check (`dgx_preflight.py:23`, pass-4 T-100) | m/`proxy/server:206-235` | **OD-42 (new, pending):** parity (D4/D15) means default = no proxy-side limit (OS behavior). *Recommendation:* config key `backend.connect_timeout`, default equal to legacy (OS) until cutover, then a finite value as a labeled judgment call. The resulting error text falls under OD-28 |
| T-5 | A connect cancelled mid-attempt (for example by SIGTERM) gives the error text **`connection cancelled`** (`str(CancelledError())` is empty) | m/`proxy/server:223-227` | Adds one row to the r4 §1.3 error-text table (§4) |
| T-6 | No HTTP header-size option exists, and a search of `proxy/layers/http` and `net/http` found no header-size cap (MEDIUM, search-based). Go's `http.Server` defaults `MaxHeaderBytes` to 1 MB | search | Named constant in hylo with a comment. Unobservable for Claude Code traffic (NITPICK) |

### 1.5 Inert in production; recorded with the hylo disposition (22)

| Option (default) | Why inert in legacy | hylo |
|---|---|---|
| `http2_ping_keepalive` 58, `normalize_outbound_headers` True | h2 only; both legs are h1 (P-1). m/`proxy/layers/http/_http2:378,399,544-567` | named constants if hylo ever speaks h2 |
| `upstream_cert` True, `add_upstream_certs_to_client_chain` False, `certs` [], `cert_passphrase` None, `key_size` 2048 | Leaf certificates are minted by the mitmproxy CA with the upstream's details (eager), RSA 2048 (m/`options:9,124-129,226-233`; m/`tlsconfig:644`) | `hylo ca` constants (key type and size, leaf validity), P4 |
| `client_certs` None, `request_client_cert` False | No mTLS on either leg (m/`tlsconfig:201-206,348-357`) | P6 per-backend `tls.client_cert` (HY-TLS-1) |
| `tls_ecdh_curve_client`/`_server` None | OpenSSL default groups | Go defaults |
| `ignore_hosts` [], `allow_hosts` [], `tcp_hosts` [] | **Every** CONNECT host is TLS-intercepted (m/`addons/next_layer:212-213`). This is the behavior D13 keeps | D13 (ruled); no change |
| `rawtcp` True | Non-HTTP bytes inside a tunnel pass as raw TCP (m/`next_layer:193`; m/`proxy/layers/http/__init__:545`) | hylo forwards non-HTTP tunnels unchanged (D13 "every other host … forwarded unchanged") |
| `anticomp` False | The client's `Accept-Encoding` passes through, except that legacy itself forces `identity` on routed and Anthropic-lane `/v1/messages` (`:131,:166`) | parity: same rule (BC-PX already) |
| `connect_addr` None | OS chooses the source address | none |
| `termlog_verbosity` info, `dumper_filter` None, `showhost` False | Per-window log content: one line per flow; the request line shows the **post-rewrite** URL (`flow.request.url`), truncated to `max(columns − 25, 50)` characters, where columns falls back to 80 when stdout is a file (so 55); connection, TLS, inactivity and WebSocket lines at INFO (m/`addons/dumper:163-193`) | no equivalent file in hylo (D16 event API replaces it) |
| `onboarding` True, `onboarding_host` `mitm.it` | The proxy answers requests for host `mitm.it` itself with the CA download app (m/`addons/onboarding:8-34`). Only reachable by asking for that host. The CA certificate is public | none (`hylo ca` replaces it) |

### 1.6 Inert (45), with the reason

- **Feature off by default:** `anticache`, `block_list`, `client_replay`, `client_replay_concurrency`, `map_local`, `map_remote`, `modify_body`,
  `modify_headers`, `save_stream_file`, `save_stream_filter`, `hardump`, `rfile`, `readfile_filter`, `keepserving`, the 12 `server_replay*` options,
  `stickyauth`, `stickycookie`, `upstream_auth`, `proxy_debug`, `export_preserve_original_ip`, `emudhra`, `emudhra_old`, `show_ignored_hosts`,
  `protobuf_definitions`.
- **Other proxy modes only:** `keep_host_header` (reverse mode, m/`proxy/layers/http/__init__:264-273`), `keep_alt_svc_header` (reverse mode,
  m/`addons/update_alt_svc:24-33`), `http_connect_send_host_header` (upstream-proxy mode, m/`proxy/layers/http/_upstream_proxy:66`), `http3` and
  `udp_hosts` (QUIC/UDP modes, m/`proxy/layers/quic/_stream_layers:440`), `strip_ech` (DNS flows only, m/`addons/strip_dns_https_records:15`).
- **Display or front-end only:** `dumper_default_contentview`, `content_view_lines_cutoff` (512; flow_detail ≥ 3 only).
- `command_history` True: reads `~/.mitmproxy/command_history` if present and writes it at `done` only once 2 × `VACUUM_SIZE` commands exist.
  mitmdump has no command input (m/`addons/command_history:18-45`).
- `server` True: structural (it starts the listener).

**Audit verdict.** Of 90 defaults, 12 were already recorded and 45 are inert. The rest split into **11 that shape behavior** (T-1 upstream trust, T-2
TLS policy, P-1 protocol mirroring, W-1 WebSocket retention) and 22 inert ones that each get a hylo disposition. The environment input T-3 and the
missing connect timeout T-4 are the non-option members of the same class. **No other default changes routing, buffering, body size or header
handling** beyond what BC-PX-037 and r4/r6 already record.

---

## 2. Target B — the CPython `asyncio.run` cancellation link (r6 §1.2 step 3), now source-read

| Step | Fact | Source |
|---|---|---|
| 1 | mitmdump's entry point ends with `return asyncio.run(main())`; `main()` awaits `master.run()` | m/`tools/main:139-143` |
| 2 | `asyncio.run` = `with Runner(...) as runner: return runner.run(main)`. Leaving the `with` calls `Runner.close()` | cpy `asyncio/runners:160-195,61-62` |
| 3 | `close()` runs `_cancel_all_tasks(loop)`, then `run_until_complete(loop.shutdown_asyncgens())`, then `run_until_complete(loop.shutdown_default_executor(...))`, and only then `loop.close()` | cpy `asyncio/runners:64-79` |
| 4 | `_cancel_all_tasks` snapshots `all_tasks(loop)` (pending tasks only), calls `.cancel()` on each, then `run_until_complete(gather(*to_cancel, return_exceptions=True))`. Exceptions other than cancellation are reported through the loop's exception handler | cpy `asyncio/runners:198-216`; `asyncio/tasks:43-67` |
| 5 | A cancelled connection task catches `CancelledError` in its read loop, marks the connection `CLOSED`, and **awaits `server_event(ConnectionClosed)` before re-raising** | m/`proxy/server:282-328` (catch `:290-292`, event `:308`, re-raise `:327-328`) |
| 6 | Inside `server_event`, the lock is uncontended (the code under it has no `await`, m/`server:384-386`), and `asyncio.Lock.acquire` returns without suspending when unlocked. The `HttpErrorHook` becomes `asyncio.create_task(hook_task(...))` | cpy `asyncio/locks:92-101`; m/`proxy/server:426-431`; m/`utils/asyncio_utils:14-35` |
| 7 | By then `master.run()` has returned and restored the previous task factory (m/`utils/asyncio_utils:89-100`), so the default factory makes a plain `Task`, whose constructor queues its first step with `call_soon` | cpy `asyncio/base_events:456-465`; `asyncio/tasks:139` |
| 8 | Ordering: that `call_soon` happens **during** the cancelled task's step. The cancelled task finishes later in the same step, and only then are its done-callbacks (gather's) queued, also with `call_soon` (cpy `asyncio/futures:161-173`). Each loop iteration runs only the callbacks that were ready at its start (cpy `asyncio/base_events:1922,1982`). When gather's outer future completes, `_run_until_complete_cb` calls `loop.stop()` (cpy `base_events:181-188`, registered `:676`), and `run_forever` exits only after the iteration in which `_stopping` became true (cpy `base_events:645-646`). The hook task's first step therefore always runs before the loop stops | as cited |
| 9 | **More margin than r6 claimed.** The hook task was created after the snapshot, so it is not cancelled. Even if its chain had awaited something, it would get further steps during the two later `run_until_complete` calls in `close()` (step 3). Only a task still pending at `loop.close()` is dropped | cpy `asyncio/runners:70-77` |

**Verdict: HIGH (static, every link read).** On SIGTERM or SIGINT, an in-flight `/v1/messages` flow gets the `error` hook, and legacy writes
`*_upstream_error` with `Client disconnected.`, `server closed connection` or the h11 EOF text (r6 §1.2 step 5). r6's "MEDIUM, one unread link" is
upgraded. Pass-3 r4's **V-3** (does mitmproxy's shutdown fire `error` for in-flight flows) is answered statically. A replay-rig run would only
confirm it. The production question behind V-3 is closed independently by the settlement (§0: no orphans after 2026-11-11).

---

## 3. Owner-decision list delta (base: the settled OD-01..OD-38)

| ID | Change | Status |
|---|---|---|
| OD-37 (was r6 "OD-35") | Renumbered. Note: **not observed in production** (§0: 0, 342, 0, 181 s). Remains a latent failure mode. Also applies to the Remote Control WebSocket (§1.3 W-1), where the relevant hylo rule is HY-BIND-6 rather than HY-TIMEOUT-1 | P |
| OD-38 (was r6 "OD-36") | Renumbered. The SIGTERM half is now HIGH (§2). The retained ledger has **no** shutdown orphans (§0); the SIGHUP/SIGKILL half stays a design argument, not an observed defect | P |
| OD-17 | Note: **HY-PROTO-1**: the upstream leg mirrors the client's HTTP version (both legs h1 in production). Go must not upgrade the Anthropic leg to h2 on its own (§1.3 P-1) | P |
| OD-28 | Scope widened: the upstream TLS failure texts (`Certificate verify failed: …`, `The remote server does not speak TLS.`, the TLS-version text, alert texts, `OpenSSL …`) and `connection cancelled` are further fixed mitmproxy strings | P |
| **OD-41** (new) | **Upstream TLS policy.** (a) trust anchor: OS store, embedded Mozilla snapshot (legacy = certifi 2026.10.23), or OS store plus per-backend `ca_file`; (b) per-backend `ca_file` and `client_cert` keys (P6; legacy has neither); (c) cleanup of the legacy login-keychain `trustRoot` at cutover, since a Go OS-store verifier would trust it upstream; (d) cipher suites | P. Recommendation: (a) OS store plus per-backend `ca_file` (approved failure-mode deviation: only TLS-inspection networks and private-CA backends behave differently); (b) yes, P6; (c) `hylo doctor` detects and `hylo ca` offers removal; (d) Go defaults, TLS 1.2 minimum as a named constant. Verification itself is **not** optional (HY-TLS-1) |
| **OD-42** (new) | **Upstream connect timeout.** Legacy has none (OS TCP connect timeout, §1.4 T-4) | P. Recommendation: config key `backend.connect_timeout`, default = legacy (none) until cutover, then a finite labeled judgment value |

**Count: 42 items (OD-01..OD-42): 40 pending, 2 ruled (OD-24, OD-27).** (OD-39 and OD-40 are pass-3 r5's, §0.)
Defaults introduced without an OD (they follow from rulings): HY-TLS-1 (verification always on; orchestrator's D13 reading), HY-TLS-3 (no implicit
key log), HY-WS-1 (D16 bounded buffers), HY-PROTO-1 (D4 parity).

---

## 4. Target C — final pass-2 sweep and the amended canonical pointer

### 4.1 What is still open in the pass-2 domain model

| Item | State after r7 |
|---|---|
| Entities, ledger schema, env inputs | Stable since r6's mechanical diff (0 new). One new **process input** outside legacy's own code: `SSLKEYLOGFILE` / `MITMPROXY_SSLKEYLOGFILE` (T-3) |
| The 36 unpaired DGX requests | **Closed** (§0: all 2026-11-11, O-1) |
| F-2 frequency | **Closed for the retained ledger** (§0: not observed) |
| asyncio.run link | **Closed** (§2) |
| mitmproxy runtime configuration | **Closed** by the 93-option audit (§1) |
| Owner capture: VictoriaMetrics NaN | open (after the soak), carried |
| New cheap owner checks, local and read-only, on the 38 retained `${TMPDIR}/dgx-mitm.*.log` files (none networked) | (1) count `Closing connection due to inactivity` lines (m/`proxy/server:352`, INFO): idle tunnels between requests are expected; any line whose client had a flow in progress is an F-2 cut; (2) for the bridge: count `WebSocket … message` lines per log (F-3 volume) and the spacing of `Received WebSocket ping` lines (is it below 600 s?); (3) count `Unable to establish TLS connection with server` lines (T-1 in production; expected 0) |
| Not determinable from authorized sources (LOW) | whether vLLM sends any byte before the first token, and whether Claude Code sends non-streaming Sonnet requests (both only change how likely the latent F-2 is); the OS connect-timeout value (T-4) |

Apart from the owner captures and checks, **no domain-model gap remains open in pass 2.**

### 4.2 Error-text table additions (r4 §1.3; apply after r5 CONV-ABS-14 and r6 §1.2-1.3)

| Ledger `error` text | Raised at | Meaning |
|---|---|---|
| `Certificate verify failed: <reason>` | m/`proxy/layers/tls:319-322` | upstream chain or hostname check failed (T-1) |
| `tlsv1 alert unknown ca` / `sslv3 alert bad certificate` / `ssl/tls alert bad certificate` | m/`tls:323-332` | the upstream rejected the handshake with that alert |
| `The remote server does not speak TLS.` | m/`tls:333-343` | `https` backend URL pointing at a plain-HTTP port |
| `The remote server and mitmproxy cannot agree on a TLS version to use. You may need to adjust mitmproxy's tls_version_server_min option.` | m/`tls:344-351` | upstream supports only TLS < 1.2 (T-2) |
| `OpenSSL <repr>` | m/`tls:352-354` | any other handshake error |
| `connection cancelled` | m/`proxy/server:223-227` | connect attempt cancelled (e.g. SIGTERM during connect) |

### 4.3 Canonical pointer (r6 §5) — r7 amendments

Apply r6 §5 as written, then these amendments. Rows not listed are unchanged.

| Topic | Authoritative base (unchanged) | r7 amendment (apply after r6's) |
|---|---|---|
| **Entity catalogue** | r4 §3.1 | r7 §1.3 W-1 (proxy process state: unbounded per-WebSocket message list, F-3); r7 §1.4 T-3 (process env input `SSLKEYLOGFILE`) |
| **Correlation / pairing** | r4 §3.3 | r7 §0 (the 36 are all 2026-11-11: O-1 confirmed, shutdown ruled out for the retained ledger) |
| **Error-text table** | r4 §1.3 | r7 §4.2 (6 rows: upstream TLS failures and `connection cancelled`) |
| **Upstream connection model** (mitmproxy) | r4 §1.1-1.3 | r7 §1.3 T-1 (certifi-only verification; on TLS failure the tunnel survives and only the Anthropic lane fails), P-1 (ALPN mirroring, h1 both legs), §1.4 T-4 (no connect timeout) |
| **mitmproxy runtime configuration** (new row) | **r7 §1** (93 options: 3 set, 12 recorded, 11 behavior-shaping, 22 inert with disposition, 45 inert) | — |
| **Proxy shutdown semantics** | r6 §1.1-1.2 | r7 §2 (asyncio.run link read; verdict HIGH; V-3 answered statically) |
| **Crash catalogues / failure modes** | as r6 | add **F-3** (r7 §1.3 W-1); F-2 status "latent, not observed" (r7 §0) |
| **Owner-decision list** | r5 §3.2 (OD-01..OD-34) | r6 §3 **with the r7 §0 renumbering (r6 OD-35 → OD-37, r6 OD-36 → OD-38)**; P3r4 §5 (OD-35 tap lines, OD-36 backfill); P3r5 (OD-39 exporter rebuild trigger, OD-40 meaning of "identical routing decisions"); r7 §3 (OD-41, OD-42; notes on OD-17, OD-28, OD-37, OD-38) |
| **LAN exposure and bind requirements** | r5 §1.1-1.4 | r7 §1.3 W-1 (bridge WebSocket idle limit belongs under HY-BIND-6, not HY-TIMEOUT-1) |
| **TLS requirements** (new row) | **r7 §1.3 T-1/T-2, §1.4 T-3** (HY-TLS-1, HY-TLS-3, OD-41) | — |
| **Retractions** | r5 §0.3; P3r4 §6 crosswalk | r6 CONV-ABS-20; r7: none (CONV-ABS-25 not issued) |

---

## 5. Retraction audit (this round)

Claims re-checked against source this round, with no retraction needed:
- r6 §1.2 step 3 ("documented contract, not re-read"): confirmed from the CPython 3.12.10 source (§2). Step 6 ("first step runs before the loop
  stops") is confirmed, with more margin than stated (§2 step 9).
- r4 §1.2 / §1.3 ("`connection.error` set only on TCP connect failure or upstream TLS handshake failure") and r4 D-1 ("gates on TCP connect only,
  not TLS"): consistent with T-1's per-lane outcome. The new detail is the error texts (§4.2).
- r4 §1.3 "mitmproxy mirrors the upstream ALPN under eager": the wording is loose but the substance holds. Precisely: the upstream is offered the
  **client's** ALPN list, and the client gets the protocol the upstream chose (P-1). Refinement, not a retraction.
- Pass-1/pass-4 references to "`flow_detail=1`" as a setting are not wrong. The value equals the default (§1.1).
- r6 §1.3 F-2 mechanism: unchanged. Its production frequency is now known to be zero in the retained ledger (§0).

**No CONV-ABS issued this round** (CONV-ABS-25 left unused).

---

## Delta Summary

| Target | New | Refined / confirmed |
|---|---|---|
| Settlements | 3 recorded; OD renumbering applied (r6 OD-35 → OD-37, OD-36 → OD-38); r6 gaps 2 and 3 closed | O-1 confirmed; F-2 latent, not observed |
| A option audit | 93 options enumerated from source (AST); **T-1** certifi-only upstream verification with hostname check and its per-lane failure outcome; **T-2** TLS 1.2 floor and legacy cipher list; **P-1** ALPN mirroring → h1 both legs, HY-PROTO-1; **W-1 / F-3** unbounded WebSocket message retention plus per-message log lines; **T-3** `SSLKEYLOGFILE` env input; **T-4** no upstream connect timeout; HY-TLS-1, HY-TLS-3, HY-WS-1 | 12 previously recorded defaults re-confirmed; `flow_detail=1` is a no-op; 22 inert options dispositioned; 45 inert with reasons |
| B asyncio link | — | r6 §1.2 upgraded MEDIUM → **HIGH** with every CPython 3.12.10 link cited; extra margin from `Runner.close()`; P3r4 V-3 answered statically |
| C sweep | error-text table +6 rows; pointer table: 2 new rows (runtime configuration, TLS requirements), 9 amended rows | no pass-2 domain gap open except owner captures and checks |
| Decisions | **OD-41** (upstream TLS policy), **OD-42** (connect timeout) | OD-17, OD-28, OD-37, OD-38 notes |

New items: 6 (T-1, T-2, P-1, W-1/F-3, T-3, T-4) plus 2 ODs and 4 HY defaults. Existing items refined: 8 (asyncio verdict, V-3, OD-17, OD-28, OD-37, OD-38,
error table, r4 ALPN wording).

## Remaining Gaps (verbatim-carryable)

1. Owner capture, VictoriaMetrics (unchanged): one `/api/v1/query` response for the exact `QUERY` (`dgx_statusline.py:102-123`) on an idle box, under
   light load, and with fewer than 20 TTFT samples, after the DGX soak is scored. Look for `"NaN"`/`"+Inf"`/`"-Inf"` in `value[1]` per `__name__`.
2. Owner local log checks (cheap, read-only, no networking) on the retained `${TMPDIR}/dgx-mitm.*.log` files: (a) `Closing connection due to
   inactivity` lines, and whether any coincides with a flow in progress (F-2); (b) per-log count of `WebSocket … message` lines and the spacing of
   `Received WebSocket ping` lines on the bridge (F-3 volume; is the ping interval below 600 s?); (c) `Unable to establish TLS connection with server`
   lines (T-1 in production; expected 0).
3. Not determinable from authorized sources (LOW): whether vLLM's streaming endpoint sends any byte before the first token, and whether Claude Code
   sends non-streaming Sonnet requests (likelihood of the latent F-2); the OS TCP connect timeout value behind T-4.
4. Owner decisions: 40 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-42).

## Novelty Assessment

Novelty: SUBSTANTIVE

Half of this round is NITPICK by the stated rule: the settlements and renumbering, the asyncio.run link (a confirmation that upgrades r6's
confidence), the 57 options that were already recorded or are inert, the error-table rows, and the pointer amendments.

The option audit, the target taken from the class F-2 came from, found defaults that shape legacy behavior and that **no prior pass of either kind
recorded** (searches for `certifi`, `ssl_insecure`, `VERIFY_PEER`, `SSLKEYLOGFILE`, `websocket.messages` and a connect timeout found nothing):

- **T-1:** every upstream TLS connection is verified against **certifi's bundle only** (OS store ignored), and an upstream verification failure
  kills only the Anthropic lane while the DGX lane keeps working. This produces OD-41 and HY-TLS-1 and changes the hylo TLS spec (trust anchor,
  per-backend CA, keychain cleanup).
- **P-1:** the upstream leg mirrors the client's protocol, so production is h1 on both legs. Go's default would silently move the Anthropic leg to h2.
  This is a new parity requirement (HY-PROTO-1).
- **W-1 / F-3:** unbounded per-WebSocket message retention and per-message logging on the Remote Control bridge. A new resource failure mode.
- **T-3 / T-4:** an undocumented environment input that writes TLS secrets, and the absence of any upstream connect timeout (OD-42).

Removing these findings would change how the proxy is specified: its TLS policy, its upstream protocol choice, its WebSocket handling and its
connect-timeout configuration. Under the binary rule that is SUBSTANTIVE. The entity model, the ledger schema and the runtime-configuration surface
are now fully enumerated. A round 8 should be able to restrict itself to re-verifying T-1, P-1, W-1, T-3 and T-4 and to whatever pass-3 r5 hands off.

## Convergence Declaration

Another round needed: the mitmproxy option audit surfaced unrecorded behavior-shaping defaults (certifi-only upstream verification and its
lane-asymmetric failure, client-mirrored upstream HTTP version, unbounded WebSocket retention), an implicit `SSLKEYLOGFILE` input and the missing
connect timeout. The suggested scope for round 8: re-verify those five items against source, reconcile with pass-3 r5 when it lands, and carry the
owner checks.

## State Checkpoint

```yaml
pass: 2
round: 7
status: complete
files_scanned: claude-dgx (15-30, 60-110), dgx_proxy.py (79-83, 120-135, 161-166), dgx_preflight.py (1-40); mitmproxy 12.3.1 (options, all addons/*.py load() declarations via AST, addons/__init__, tools/dump, tools/main, master, addons/tlsconfig, addons/proxyserver, addons/next_layer, addons/dumper, addons/onboarding, addons/update_alt_svc, addons/command_history, net/tls, proxy/layers/tls, proxy/layers/http/__init__, proxy/layers/websocket, proxy/server, proxy/commands, utils/asyncio_utils); CPython 3.12.10 asyncio (runners, tasks, futures, base_events, locks)
timestamp: 2026-11-14T07:30:00Z
novelty: SUBSTANTIVE
retractions: []
conv_abs_next_free: 25
option_audit: {registered_in_mitmdump: 93, set_by_launcher: 3, previously_recorded: 12, behavior_shaping_new: 11, inert_with_disposition: 22, inert: 45}
new_findings: [T-1 certifi-only upstream verification + lane-asymmetric failure, T-2 TLS floor/ciphers, P-1 ALPN mirroring (h1 both legs), W-1/F-3 unbounded WebSocket retention, T-3 SSLKEYLOGFILE env input, T-4 no upstream connect timeout]
asyncio_link: closed (HIGH)
owner_decisions: 42 (OD-01..OD-42; 40 pending, 2 ruled: OD-24, OD-27; OD-39/OD-40 from pass-3 r5; OD-41/OD-42 this round)
pass3_r5_reconciled: not present at write time
next: pass 2 round 8 (re-verify T-1, P-1, W-1, T-3, T-4; reconcile pass-3 r5; owner checks)
```
