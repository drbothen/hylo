# General research: a Go TLS-intercepting proxy for hylo (P3)

- **Type:** general (technology)
- **Date:** 2026-11-14 (web findings checked 2026-11-13/14)
- **Feeds:** `docs/PLAN.md` §6 (architecture), §7 P3/P4, §9 risks; packages `internal/proxy`, `internal/ca`
- **Inputs read:** `docs/PLAN.md` §2, §6–§10; `legacy/dgx_proxy.py` (the addon, all of it); `legacy/claude-dgx` (launcher)
- **Tags:** **[documented]** = official docs or source; **[community-observed]** = issue reports, user captures, third-party analysis; **[inferred]** = my own reasoning from the evidence, or from training-data knowledge of Go internals that I did not re-verify this session

---

## Executive summary

1. **Q1 recommendation: build it on the standard library** (CONNECT hijack, then `crypto/tls` `tls.Server` with an in-memory leaf from `internal/ca`, then a shared `http.Server` whose handler is `httputil.ReverseProxy` with `Rewrite`). hylo intercepts **one host** and the client speaks **HTTP/1.1**. `ReverseProxy` already provides SSE auto-flush, WebSocket upgrade relay and context cancellation. A library would add surface area without removing the hard parts (routing, the tap, parity). **Runner-up:** `elazarl/goproxy` v1.9.4 (2026-11-12, active). **Rejected:** `google/martian` (archived 2026-02-20) and `lqqyt2423/go-mitmproxy` (buffers bodies up to 5 MiB by default and keeps SSE events in a per-flow slice).
2. **The legacy setup intercepts every CONNECT host**, not just `api.anthropic.com`. The launcher passes no `ignore_hosts`/`allow_hosts`, and mitmproxy intercepts everything by default. hylo should intercept an allowlist (default: `api.anthropic.com`) and blind-tunnel everything else. That is a deliberate change from parity, and it needs owner sign-off (open question 1).
3. **Remote Control traffic is mostly on `api.anthropic.com`**: work polling, an SSE worker stream, and in some versions a `wss://` session-ingress socket [community-observed]. So it goes **through** the interception path, not around it. The non-negotiables are: flush every `text/event-stream` immediately (legacy already does), relay HTTP/1.1 WebSocket upgrades, and set no idle/read timeouts on intercepted connections.
4. **Claude Code's native binary is a Bun executable** [documented by Bun and Claude Code]. Bun's `fetch` honors `HTTPS_PROXY`/`NO_PROXY` and tunnels HTTPS with CONNECT. It speaks **HTTP/1.1**: Bun's experimental HTTP/2 client does not support CONNECT tunnels. So hylo can offer ALPN `http/1.1` only on the client side, which also matches what mitmproxy ends up negotiating today.
5. **Trust works today through `NODE_EXTRA_CA_CERTS`**, which Bun has supported since 1.1.22. It is read once at process start, so it must be in the environment before launch; issue reports show it was ignored when set only in `settings.json`. The file can hold several PEM certificates, which allows overlap during CA rotation.
6. **CA:** use ECDSA P-256 for the CA and the leaves, with a **critical Name Constraints** extension: permit only the intercepted DNS names and exclude all IPv4/IPv6. OpenSSL (Node), BoringSSL's verifier (Bun) and Go all enforce constraints on trust anchors [documented]. A stolen hylo CA key then cannot impersonate other sites to Claude Code. On Windows, file mode `0600` does **nothing**; you need an explicit DACL.
7. **Parity traps** that would fail a byte-level diff, all in the legacy code itself:
   - Python `json.dumps` defaults: `", "`/`": "` separators, `ensure_ascii`, insertion order.
   - `req_bytes` counts **characters**, not bytes.
   - The ledger `t` field is local time with no zone.
   - Legacy WebSocket ledger events are partly dead code: `ws_closed` never fires, and `bridge_ws_close` fires at handshake time with `duration_s=0.0`.
8. **mitmproxy behaviors to reproduce or consciously drop:**
   - `responseheaders` decides between streaming and buffering before the body arrives.
   - It re-frames streamed bodies.
   - It forces `Accept-Encoding: identity` on `/v1/messages`.
   - It answers upstream failures with its own 502 and fires the `error` hook.
   - Its **eager** connection strategy dials `api.anthropic.com` at CONNECT time, even for requests that end up going to the local backend.
9. **Parity recording:** use a custom JSONL capture (request plus timestamped response chunks, secrets stripped), not HAR or `.mitm` flows. mitmproxy does not keep streamed bodies unless you are on 12.0+ with `store_streamed_bodies=True`.
10. **Testing is all in-process with the standard library:**
    - `httptest` TLS fake upstreams with a test CA that issues `api.anthropic.com` certificates.
    - An injectable upstream dialer.
    - Raw-socket CONNECT tests: single-write `200`, ClientHello arriving in the same packet as CONNECT, half-close.
    - A hand-rolled 101 echo for WebSockets.
    - `go test -fuzz` on the SSE tap, with "the result does not depend on how the stream is chunked" as the property.

---

## Q1. Build vs buy

### Library status (verified on pkg.go.dev / GitHub, 2026-11-13)

| Option | Latest version (date) | Maintenance | HTTP/2 client side | Streaming / SSE | WebSocket in MITM | Selective MITM | Notes |
|---|---|---|---|---|---|---|---|
| **Stdlib** (`net/http`, `crypto/tls`, `httputil`) | Go **1.27.4** / **1.26.11** (2026-11-10) | Go team | Possible: hand the `*tls.Conn` to an `http.Server` and advertise `h2` [inferred] | `ReverseProxy` flushes immediately for `text/event-stream` and for `ContentLength == -1` [documented, source] | HTTP/1.1 Upgrade/101 relay built in since Go 1.12 [documented] | You write it (about 20 lines) | `Director` is **deprecated in Go 1.26**; use `Rewrite` [documented]. Open issue golang/go#80875 (reported against 1.26.5): leaks/early-byte loss on the upgrade error paths [community-observed] |
| **elazarl/goproxy** | **v1.9.4** (2026-11-12); v1.9.3 (11-07), v1.9.2 (09-27) | Active | Opt-in `AllowHTTP2` (full h2 MITM since v1.9.0), via `golang.org/x/net/http2` [documented] | Streams; an SSE regression in v1.8.5 (4 KiB stranding) was fixed in v1.8.6 [documented] | Yes, HTTP/1.1; early-frame fix in v1.9.2 [documented] | `HandleConnectFunc` returns `MitmConnect` or `OkConnect` per host [documented, Context7] | **Default transport skips upstream TLS verification**, so it must be replaced. Runs its own HTTP/1 read loop rather than `http.Server`. Open PRs #806 (nil response-filter panic under h2) and #815 [community-observed] |
| **google/martian** | v3.3.3 (tag 2022-08-16) | **Archived 2026-02-20** (read-only) [documented] | Separate, opt-in h2 path | HTTP/1 path writes through a `bufio.Writer` and flushes after `Response.Write`, so SSE can stall | No (issue #31) | No per-host MITM switch | Not a candidate |
| **lqqyt2423/go-mitmproxy** | **v1.9.5** (2026-11-12); v1.9.4 (10-15) | Active | Only on the upstream-first path | SSE detected and flushed, but ordinary bodies are buffered up to `StreamLargeBodies` (5 MiB) by default, and **parsed SSE events pile up in a per-flow slice** [documented, source] | Yes (hooks) | `SetShouldInterceptRule` | Brings a web UI and an addon framework hylo doesn't need. Issue #81: "ignore_hosts not working" [community-observed] |

### Recommendation: stdlib

Reasons, in priority order:

1. **The hard parts are hylo-specific whichever way you go.** Routing, request normalization, the SSE usage tap, the ledger and parity all have to be written by hand regardless. A MITM library only saves the CONNECT and leaf-certificate plumbing. With stdlib that is roughly 150–250 lines; `internal/ca` exists in the plan anyway (PLAN §6).
2. **The scope is narrow.** One intercepted host; client side HTTP/1.1 only (Q3/Q4); upstream to Anthropic plus one local backend. The features that justify goproxy (h2 MITM, an h2c preface sniffer, generic filters) are not needed.
3. **`ReverseProxy` already covers the protocol checklist from PLAN §9:**
   - SSE auto-flush, plus `FlushInterval: -1` for the other streamed bodies.
   - 101 upgrade relay with hijack and bidirectional copy.
   - Request-context cancellation propagated to the upstream.
   - Hop-by-hop header stripping (with `Rewrite`, done before the hook runs).
4. **Dependency policy (CLAUDE.md):** goproxy pulls in `golang.org/x/net`, and its insecure default transport has to be overridden, which is exactly the kind of footgun that "every dependency needs a reason" exists to avoid.
5. **Security review is easier.** One code path terminates TLS, and it lives in the repo.

**When to switch to goproxy:** only if P3 shows that writing the CONNECT layer is turning into a time sink, for example Windows-specific hijack/half-close bugs. Even then, wrap goproxy behind the same `internal/proxy` interfaces so the routing and tap code does not change.

---

## Q2. Selective interception

### What legacy does

- The launcher (`legacy/claude-dgx` line 75) runs `mitmdump --set flow_detail=1 --listen-port N -s dgx_proxy.py` with **no** `ignore_hosts`, `allow_hosts` or `tcp_hosts`. In mitmproxy's regular mode all three default to empty, so **every CONNECT is TLS-intercepted** [documented, mitmproxy options]. That includes `claude.ai`, `platform.claude.com`, Datadog intake, GitHub, npm, and `bridge.claudeusercontent.com`.
- The addon itself only **rewrites** `api.anthropic.com` `/v1/messages*`. It **observes** `bridge.claudeusercontent.com` WebSocket upgrades (`bridge_ws_connect`, `bridge_ws_close`) and the `anthropic-ratelimit-unified-*` headers on `api.anthropic.com`. Everything else passes through untouched, but still decrypted and re-encrypted.
- Legacy quirks a parity harness has to account for:
  - `websocket_start` only sets `_ws_started` when the attribute already exists. It never does, so **`ws_closed` is never logged**.
  - For an upgraded flow, mitmproxy's `response` hook fires on the 101 handshake. That logs **`bridge_ws_close` at connect time, with `duration_s=0.0`**, because `_bridge_dur` is never set.

  The docstring says "CONNECT/tls-establish/close with durations and byte counts". The code does not do that.

### Recommendation: allowlist interception

- **Intercept:** an exact-match host allowlist on port 443, defaulting to `["api.anthropic.com"]`. Match case-insensitively, on the CONNECT authority with the port stripped.
- **Blind-tunnel everything else:** `net.Dial` to the CONNECT target, then a bidirectional `io.Copy` with `CloseWrite` half-close. No timeouts other than TCP keepalive.
- **Tunnel lifecycle events:** emit them for `bridge.claudeusercontent.com` (and optionally every tunnel) from the CONNECT layer: connect, close, duration, bytes each way. That is what the legacy docstring intended, and it is *more* accurate than the legacy events. It is **not** byte-identical, so the owner decides whether the parity harness compares these events or excludes them (open question 2).
- **Remote Control implications** [community-observed; endpoints are private and change between versions]:
  - Control-plane and worker traffic goes to `api.anthropic.com`: `POST /v1/environments/bridge`, `GET /v1/environments/{id}/work/poll`, `POST /v1/code/sessions/{id}/worker/register`, `GET …/worker/events/stream` (**SSE**, named `SSETransport` in CLI debug logs), and in some paths `wss://api.anthropic.com/v1/session_ingress/ws/...`.
  - These requests are on the intercepted host, so hylo must: (a) stream every `text/event-stream` response with no buffering, which legacy does unconditionally (lines 193–199); (b) relay WebSocket upgrades on `api.anthropic.com`; (c) leave non-`/v1/messages` paths byte-for-byte alone (legacy line 103).
  - Remote Control is **disabled when `ANTHROPIC_BASE_URL` points anywhere but `api.anthropic.com`** [documented, code.claude.com/docs/en/remote-control]. This is why D6 (invisible mode) exists.
  - `bridge.claudeusercontent.com` is **documented as the Claude-in-Chrome WebSocket bridge**, and has also been seen as a Desktop device bridge. It is *not* shown to be the CLI Remote Control transport, so blind-tunneling it carries little risk.
  - Antivirus TLS scanning has been reported to leave Remote Control looking "active" while inbound messages are silently lost (issue #76642). The failure mode for a buffering interceptor is silent, so test **bidirectional** Remote Control (P4 exit criterion).
- **Telemetry and other Anthropic hosts:** `api.anthropic.com` also carries feature flags, telemetry and WebFetch domain-safety checks [documented, network-config]. Those pass through untouched, just as in legacy. Datadog intake hosts, `claude.ai` and `platform.claude.com` (OAuth) are tunneled. That removes a whole class of breakage risk (OAuth refresh, certificate pinning, a client that ignores the extra CA on some path).
- **Loop prevention:** the `hylo proxy` process must not pick up `HTTPS_PROXY` from its own environment. Set `Transport.Proxy = nil` explicitly, because `hylo run` exports `HTTPS_PROXY` and may spawn the proxy as a child process [inferred].
- **Absolute-form requests:** Claude Code 2.1.282–2.1.283 sent Remote Control bridge registration to the proxy as an absolute `https://` URI instead of a CONNECT (issue #97352; fixed in 2.1.287). Handle absolute-form `https://api.anthropic.com/...` requests by putting them through the same intercept handler. Tunneling or rejecting them would break that path [inferred].

---

## Q3. Protocol details

### ALPN / HTTP/2

- **Client side:** Bun `fetch` is HTTP/1.1 by default. Its experimental HTTP/2 client (1.3.14+) **explicitly does not support HTTP proxies or CONNECT** [documented, Bun 1.3.14 notes]. A Windows mitmproxy capture of Claude Code 2.1.228 showed HTTP/1.1 (#85979) [community-observed]. The older Node/undici path defaults to `allowH2=false` in undici 7 and `true` in undici 8 [documented]. **Advertise `NextProtos: ["http/1.1"]`.** This matches what mitmproxy negotiates today: in eager mode it mirrors ALPN, and the client only offers h1 [inferred]. Adding `h2` later means serving the conn with `http.Server`/`x/net/http2` and dropping the `Hijacker`-based WebSocket path, because h2 `ResponseWriter`s do not implement `Hijacker` [documented].
- **Upstream to Anthropic:** Go's `Transport` negotiates h2 with `api.anthropic.com` by default when using the default TLS settings; a custom `TLSClientConfig` needs `ForceAttemptHTTP2` or `Protocols` (Go 1.24+) [documented]. h2 upstream would multiplex every window over one connection, which is good for the one-proxy-per-user model. For **parity, start with HTTP/1.1 upstream** (`Protocols` set to HTTP1 only), because that is what mitmproxy does when the client offered h1 [inferred]. Make h2 a later switch (judgment call; open question 4).
- **Upstream to the local backend:** plain `http://` HTTP/1.1, the same as legacy (`DGX_UPSTREAM`, scheme `http`).
- **WebSocket upgrades** must go upstream over HTTP/1.1. Go's transport forces h1 for `Connection: Upgrade` requests [inferred from transport source, not re-verified]. To be safe, use a dedicated h1-only transport for requests carrying an `Upgrade` header.

### SSE streaming and the tap

- `ReverseProxy.flushInterval()` returns `-1` (flush after every write) when `Content-Type` parses to `text/event-stream`, or when `ContentLength == -1`. Otherwise it uses `FlushInterval` [documented, `reverseproxy.go`]. **Set `FlushInterval: -1` anyway**, because legacy streams every non-JSON `/v1/messages` body (line 208), not only SSE.
- **The tap:** in `ModifyResponse`, replace `resp.Body` with a wrapper whose `Read(p)` calls the inner `Read`, then feeds `p[:n]` to the line scanner **synchronously**, then returns. Do not use a goroutine or a pipe. That adds no latency beyond the scan itself, which is microseconds for a 1–4 KiB chunk.
- **Tap safety rules:**
  - The tap must never return an error or block. It recovers panics internally and stops parsing, the same as legacy's `try/except: pass`.
  - It reproduces the `KEEP = 64_000` tail guard and the complete-lines-only rule exactly. Those affect results on pathological input, so parity depends on them.
  - It finalizes on EOF or `Close`. Ledger writes happen in `Close()`, the equivalent of mitmproxy's `response` hook. `Close` also runs on client disconnect, which legacy logs through `error` instead (see Q6).
- **Avoid wrappers that hide `Flush`:** golang/go#64045 is a wrapper hiding flush capability; `http.TimeoutHandler` buffers [documented]. Any middleware on the MITM server must implement `Unwrap()` so that `http.ResponseController` works.
- **Buffered cases** (legacy buffers JSON and `>=400` on `/v1/messages`): the client sees no difference whether hylo buffers or streams. To keep the ledger identical, the Go tap **captures** the body as it streams, capped at about 1 MiB for usage JSON and the full body for errors, then parses it in `Close()`. That is the same data with lower latency [inferred]. The legacy `failed-req-*.json` save (request body, capped at 50 MB, newest 20 kept) needs the request body kept until the response finishes. hylo already holds it, because it parsed it.

### Content-Encoding

- Legacy forces `Accept-Encoding: identity` on **both** lanes for `/v1/messages` (lines 131, 166). Do the same. Then the tap never sees gzip, br or zstd.
- Set `Transport.DisableCompression = true` on both transports. Otherwise Go adds `Accept-Encoding: gzip` when the client sent none, transparently decompresses, and **strips `Content-Encoding`/`Content-Length`** [documented]. That would change the bytes on pass-through paths.
- If a `/v1/messages` response arrives with a non-identity `Content-Encoding` anyway, pass it through untouched and record `tap_skipped=encoding` in the decision log. Do not decode: the stdlib has gzip but no public brotli or zstd decoder, and decoding would cost a dependency [inferred].

### Request body rewriting

- Read the whole body (it has to be parsed anyway). Use `http.MaxBytesReader` with a generous cap; legacy has none, and Claude Code bodies reach many MB. 64 MiB is a judgment call and has to be documented in the code (CLAUDE.md threshold rule).
- On rewrite, set all of these: `Out.Body`, `Out.ContentLength = len(new)`, `Out.Header.Del("Content-Length")` (the transport writes it from `ContentLength`), and `Out.GetBody` returning a fresh reader so retries are safe [documented]. On pass-through, restore the original bytes the same way.

### Keep-alive, cancellation, errors

- **Client to hylo:** one `http.Server` serves every intercepted conn, with HTTP/1.1 keep-alive. Set **no** `ReadTimeout`/`WriteTimeout`, because SSE and long generations run for minutes. A `ReadHeaderTimeout` of about 30 s on the *outer* CONNECT listener is fine (judgment call).
- **Upstream:** pooled `Transport` per lane. `MaxIdleConnsPerHost` of about 16, sized for 8+ windows (judgment call). No `ResponseHeaderTimeout` on the local lane, because time-to-first-token on large prompts can be long.
- **Cancellation:** `ReverseProxy` clones the inbound request context into the outbound request, so a client disconnect cancels the upstream request [documented]. For upgrades, cancelling the context closes the backend connection [documented, source].
- **Errors:** `ReverseProxy.ErrorHandler` writes a 502 and emits `{lane}_upstream_error`, the parity counterpart of the legacy `error()` hook. The body text will not match mitmproxy's; compare ledger lines only.

---

## Q4. How Claude Code honors proxies and CAs

| Topic | Finding | Tag |
|---|---|---|
| Runtime | The native installer (and, today, the npm package) ships a **Bun single-file executable**; Node is not used at runtime | [documented] bun.com, code.claude.com install docs |
| HTTP client | The Anthropic TS SDK uses global `fetch`, which is Bun's `fetch` in the native binary. OAuth has been reported to use axios | [documented] SDK / [community-observed] #14165 |
| Proxy env | Claude Code checks `https_proxy`, then `HTTPS_PROXY`, `http_proxy`, `HTTP_PROXY`. It supports `NO_PROXY` (comma- or space-separated). No SOCKS. Basic auth works in the URL | [documented] code.claude.com/docs/en/network-config |
| Bun fetch | Honors `HTTP(S)_PROXY`, `NO_PROXY` (suffix, `*`, IP, CIDR, host:port) and `ALL_PROXY` (1.4.3+). HTTPS goes through CONNECT | [documented] bun.sh docs |
| Bun WebSocket | A bare `new WebSocket()` does **not** read proxy env; the app has to pass `{proxy}` (supported since 1.3.6). Claude Code's own WebSocket proxy behavior is application logic | [documented] Bun 1.3.6 / 1.3.9 notes |
| Node (npm/legacy installs) | Env proxying is opt-in: `NODE_USE_ENV_PROXY=1` (22.21+/24.5+). undici `EnvHttpProxyAgent` semantics differ from Node core for `NO_PROXY` | [documented] nodejs.org |
| `NODE_EXTRA_CA_CERTS` | One or more PEM certificates, **appended** to the bundled roots, **read once at startup**. Ignored when setuid or when file capabilities are set. Works on Windows; it is a separate mechanism from the OS store. Bun supports it from 1.1.22 (full bundles from 1.2.3) | [documented] Node CLI docs, Bun 1.1.22 / 1.2.3 |
| System CA | Node `--use-system-ca` (22.15+, 23.8+) and `NODE_USE_SYSTEM_CA=1` (22.19+, 24.6+); Bun `NODE_USE_SYSTEM_CA` 1.2.23+. Claude Code itself defaults to `CLAUDE_CODE_CERT_STORE=bundled,system` (system store trusted since 2.1.101) | [documented] |
| Pitfalls | `HTTPS_PROXY` / `NODE_EXTRA_CA_CERTS` set only in `settings.json` `env` did not reach the API path in 2.0.x (#11660, #10458). A CONNECT response split across reads made native fetch hang (#50252, 2.1.113–119; workaround: proxy writes the response in one go). Voice-dictation WebSocket on Windows ignored the extra CA (#102747). `proxyAuthHelper` was not applied to bootstrap CONNECTs (#99296) | [community-observed] |

**Implications for hylo:**

- `hylo run` must export `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` into the child process environment, not settings. This is what legacy does today (lines 79–80).
- Write `"HTTP/1.1 200 Connection established\r\n\r\n"` in a **single `Write`** (#50252).
- `hylo doctor` should warn when `NO_PROXY`/`no_proxy` matches `api.anthropic.com` or `anthropic.com`. Also warn when `CLAUDE_CODE_CERT_STORE` excludes `bundled`. I could not confirm whether the extra CA is applied under `system`-only; open question.
- The system trust store is not needed (PLAN §6 stands). Because Claude Code also trusts the OS store, the legacy `trust install` into the keychain is redundant for Claude Code. hylo should not install into OS stores by default.

---

## Q5. Local CA security

| Decision | Recommendation | Basis |
|---|---|---|
| Key type | **ECDSA P-256** for the CA and leaves | Supported by Node/OpenSSL 3 and BoringSSL (Bun) [documented]. **Avoid Ed25519**: Bun clients failed Ed25519 handshakes before 1.4.4 [documented, Bun 1.4.4]. RSA-2048 is the fallback; mitmproxy's default is RSA-2048 |
| Leaf keys | One P-256 leaf key generated at proxy start and kept in memory; leaves signed per host and cached in memory | mitmproxy reuses the **CA's own key pair** for every leaf [documented, `certs.py`]. A separate leaf key keeps the CA private key out of the TLS handshake path [inferred] |
| Name Constraints | **Critical** extension: `permittedDNSDomains = [intercept hosts]` (default `api.anthropic.com`); `excludedIPRanges = 0.0.0.0/0, ::/0` | OpenSSL enforces constraints from the trust anchor (in source since 1.0.x), BoringSSL's `X509_verify_cert` (Bun) includes the anchor, and Go enforces on roots [documented]. DNS constraints do not cover IP SANs, hence the IP exclusion. Watch the CN-fallback bypass (OpenSSL issue #30346): always put a DNS SAN on leaves. Go's `x509.Certificate` exposes `PermittedDNSDomainsCritical`, `PermittedDNSDomains` and `ExcludedIPRanges` (stdlib only) |
| Constraint consequence | Adding an intercept host later means **issuing a new CA** (constraints are fixed at signing) | That is the point: widening interception becomes an explicit, visible act (`hylo ca rotate`) [inferred] |
| CA validity | 5 years (judgment call; mitmproxy uses 10). Backdate `NotBefore` by 48 h, as mitmproxy does, to tolerate clock skew | CA/B Forum and Apple 398-day rules apply to publicly trusted or Apple-verified leaves, not to private roots [documented]. The Apple 825-day rule covers leaves under user roots when Apple's verifier is used, which Bun/OpenSSL are not |
| Leaf validity | 30 days, regenerated in memory on start and when within 7 days of expiry; capped at the CA's `NotAfter` | Judgment call; mitmproxy uses 199 days total. The in-memory cache makes short validity free |
| Leaf cache | `sync.Map` keyed by host, holding `*tls.Certificate` with expiry checked on lookup | mitmproxy's 100-entry LRU does no expiry check [documented] |
| Key file permissions | Unix: dir `0700`, key `0600`, write-temp-then-rename. **Windows: mode bits are ignored** apart from the read-only flag. Set a protected DACL (current user + SYSTEM; Administrators optional) with `golang.org/x/sys/windows` `SetNamedSecurityInfo`, or rely on the inherited `%APPDATA%` ACL and **verify it in `hylo doctor`** | [documented] pkg.go.dev/os. `x/sys` is a justified dependency (owned by the Go team), confined to `internal/platform` |
| Files | `ca-cert.pem` (public, what `NODE_EXTRA_CA_CERTS` points at), `ca-key.pem` (secret, PKCS#8), `trust-bundle.pem` (current cert plus any still-valid previous cert) | Never put cert and key in one file the way `mitmproxy-ca.pem` does; that makes it easy to distribute the key by mistake |
| Rotation | `hylo ca rotate` creates a new CA, writes `trust-bundle.pem = new + old`, and switches signing to the new CA **for new proxy starts only**. Running Claude Code processes trust whatever was in the bundle when they launched, so remove the old certificate only after sessions restart | `NODE_EXTRA_CA_CERTS` is read once at start and accepts several PEMs [documented] |

Prior art from mitmproxy:
- Files live in `~/.mitmproxy`: `mitmproxy-ca.pem` (key + cert, unencrypted), `-ca-cert.pem/.cer/.p12`, `mitmproxy-dhparam.pem`.
- Leaves are generated on demand with upstream-certificate sniffing (copies CN and SANs from the real server). hylo does **not** need sniffing, because it has a fixed host list.

---

## Q6. mitmproxy behaviors to reproduce, and parity recording

### Behavior checklist

| mitmproxy behavior | Legacy reliance | hylo action |
|---|---|---|
| `responseheaders` fires before the body; streaming vs buffering decided there | Lines 170–208 | `ModifyResponse` decides tap-and-capture vs tap-only; client-visible behavior is streaming either way |
| `stream = callable` gets body chunks with no chunk framing; boundaries are arbitrary; a final `b""` call | `_SSETap.feed` | Tap on `Read`; property tests prove chunking-independence |
| Streamed HTTP/1 responses are re-framed (new chunked encoding); `Content-Length` kept when present | Implicit | Go's `http.Server` does the same: chunked when the length is unknown, `Content-Length` passed through when known [inferred] |
| `set_text()` recomputes `Content-Length` (unless chunked) | Line 150 | Explicit `ContentLength` + `GetBody` (Q3) |
| Header case and order preserved for HTTP/1 | Not relied on (lookups are case-insensitive) | Go canonicalizes names and writes headers in **sorted** order. Not ledger-visible. Accepted divergence; document it |
| `anth_ratelimit` header keys | `k.lower()` | Lowercase Go's canonical keys before stripping the prefix |
| Proxy-generated 502 + `error` hook on connect/protocol failure | `error()` → `*_upstream_error` | `ErrorHandler`. Note: mitmproxy's `error` also fires on client disconnect mid-stream [inferred]. Decide whether hylo emits an event for client aborts (open question 3) |
| **Eager** strategy: upstream `api.anthropic.com` dialed at CONNECT; failure → 502 on the CONNECT itself | Implicit: if Anthropic is unreachable, even local-lane requests fail | hylo is lazy: it dials per request after routing, so the local lane works offline. **Behavior improvement; flag it as a deliberate divergence** |
| Upstream connection reuse is per client connection, not a global pool; h2→h1 translation closes upstream connections | Implicit | Go uses a global per-lane pool. Not ledger-visible |
| WebSocket messages reassembled and buffered per message; history kept | Bridge flows (now tunneled) | Byte-level relay (no message buffering): better for realtime, and no memory growth |
| `Accept-Encoding: identity` on `/v1/messages` | Lines 131, 166 | Same |
| Request mutations on the local lane: scheme/host/port switch, `Authorization: Bearer <key>`, drop `anthropic-beta`, add `X-DGX-Project/User/Session` | Lines 155–166 | Same, in a pure `route` package. Keep the `X-DGX-*` names (D7) |

### Byte-level parity traps (from reading `dgx_proxy.py`)

1. **Rewritten bodies** use `json.dumps(req)` with Python defaults: `", "` and `": "` separators, `ensure_ascii=True` (non-ASCII becomes `\uXXXX`, astral characters become surrogate pairs), Python float repr, and **insertion-ordered keys**. Go's `map[string]any` loses key order, and `json.Marshal` writes compact output with HTML escaping. Options:
   - (a) A small ordered-JSON model built on `json.Decoder.Token()` (v1, Go 1.26-compatible), plus a Python-compatible encoder. Roughly 200 lines plus fuzzing against a corpus.
   - (b) Define the P3 parity criterion for rewritten bodies as **canonical JSON equality** (the backend parses JSON; bytes do not matter to it).

   Recommendation: (b) for routing parity, plus (a) only if the owner wants a byte-exact diff. `encoding/json/v2` and `jsontext` (which can preserve order) are **GA in Go 1.27** but still `GOEXPERIMENT` in 1.26 [documented] — open question 5.
2. **`req_bytes`** is `len(flow.request.get_text())`: **code points of the decoded text**, not bytes. Go must use `utf8.RuneCount`.
3. **Ledger lines** come from `json.dumps({...})`: same separators and `ensure_ascii`, key order `t`, `event`, then the call-site order of the fields. `t` is **local time, `%Y-%m-%dT%H:%M:%S`, no zone, second resolution**. D7 keeps the format, so the ledger writer needs an ordered field list and a Python-compatible encoder, or else consumers (status line, exporter) must be confirmed to parse JSON rather than match bytes. Field order is observable either way.
4. **`duration_s`** is `round(x, 3)`. Python rounds half-to-even on the binary value, and its float repr differs from Go's `strconv` in corner cases. Exclude timing fields from the diff.
5. **The DGX lane's `in_tok` rebuild** (prompt = input + cache read + cache write) and the cache-split invariant (`w5m + w1h == write`) have to be ported verbatim. These are pure functions, so table-test them.
6. **The local-lane decision note** for a streamed response is `(streamed)` (line 303). The decision log is a separate file; decide whether it is in parity scope (open question 3).

### Recording and replay for the parity harness

- **Do not use** mitmproxy `.mitm` flows or HAR. Streamed bodies are not kept unless you run mitmproxy ≥ 12.0 with `store_streamed_bodies=True` [documented]. HAR has no chunk timing, base64-encodes binary data, and holds every flow in memory until exit.
- **Recommended: a custom JSONL capture**, one exchange per line:
  - `{id, client:{method, path, headers(redacted), body_b64}, upstream_lane, upstream_request:{…}, response:{status, headers, chunks:[{dt_ms, b64}]}, error?}`
  - Capture it with a tiny extra mitmproxy addon (`stream = callable` recording chunks), loaded *after* `dgx_proxy.py` on the live prototype, and only after the soak (CLAUDE.local constraints).
  - Scrub with a committed, reviewed script (CLAUDE.md rule). Real captures go to `captures/` (git-ignored). Synthetic ones go to `testdata/`.
- **Replay design:** one fake upstream server replays recorded responses. Match on lane + path + canonical body hash, the same idea as mitmproxy's server-replay matcher (scheme/method/path/host/port/query/body).
  - Run **both** implementations against it.
  - The Python side needs its Anthropic upstream redirected to the fake. Use a harness-only second addon that rewrites `flow.request.host/port` after `dgx_proxy.py`'s `request` hook (addon order = `-s` order), with `DGX_UPSTREAM` pointing at the fake local backend.
  - The Go side gets the same redirect through a test-only upstream override (see the P3 design section).
  - Diff: routing lane, upstream request (canonical JSON + headers minus volatile ones), client-visible response bytes, ledger lines (minus `t`, `duration_s`).

---

## Q7. Testing

- **Fake Anthropic upstream:**
  - Build it with `httptest.NewUnstartedServer(h)`, set `srv.TLS` to a certificate for `api.anthropic.com` issued by a **test CA** (made in `TestMain` with the same `internal/ca` code), then `StartTLS()`. Set `srv.EnableHTTP2 = true` for an h2 variant.
  - The handler writes SSE events (`message_start` with `usage`, `content_block_delta` ×N, `message_delta` with cumulative usage and `stop_reason`, `message_stop`), calls `http.NewResponseController(w).Flush()` after each, and sleeps between events.
  - Assertions: (a) the client receives event *k* before the server sends *k+1*, which proves there is no buffering; (b) the ledger has the right usage and cache split.
- **Fake local backend:** a plain `httptest.NewServer` that asserts the rewritten model, the `Authorization` header, a missing `anthropic-beta`, and the `X-DGX-*` headers, then replays SSE in vLLM's Anthropic dialect: `input_tokens` excluding cache, which tests the `in_tok` rebuild. An OpenAI-dialect variant (`finish_reason`) waits for P6.
- **Injectable upstream:** the proxy takes an `Upstreams{AnthropicDial func(ctx, network, addr) (net.Conn, error); AnthropicRootCAs *x509.CertPool; Local *url.URL}`. Tests point `api.anthropic.com:443` at the httptest listener without touching DNS.
- **In-process CONNECT tests:**
  - High level: an `http.Client` with `Transport{Proxy: http.ProxyURL(proxyURL), TLSClientConfig: {RootCAs: hyloTestCA}}`, so the client verifies hylo's leaf exactly as Bun would, including name constraints. Add a negative test: a CONNECT to a non-allowlisted host gets tunneled, and the client sees the *origin's* certificate.
  - Raw `net.Conn` tests:
    - The `200` arrives in one TCP read.
    - CONNECT and ClientHello arrive in one write; bytes buffered in the hijacked `bufio.Reader` must be replayed (goproxy fixed exactly this bug).
    - Half-close on tunnels.
    - Absolute-form `https://` requests.
    - Client disconnect mid-stream: the upstream handler observes `r.Context().Done()`.
- **WebSocket without dependencies:** the fake upstream handles `Upgrade: websocket` by hijacking, writing a `101`, then echoing raw bytes. The test client writes a hand-built upgrade request through the proxy and checks that bytes go both ways, plus closure propagation and early bytes sent before the 101 is read (golang/go#80875).
- **Fuzzing (`go test -fuzz`, native since Go 1.18):**
  - `FuzzSSETap(f, stream []byte, cuts []byte)`: split `stream` at the positions from `cuts` and assert that the usage, cache and stop-reason results equal a single-chunk feed whenever no line exceeds `KEEP`. The tap must never panic.
  - `FuzzNormalize` for `normalize_for_dgx` (idempotence; output is valid JSON).
  - `FuzzPyJSON` if option (a) is chosen.
  - Seed corpora from scrubbed captures.
- **Deterministic time:** inject a clock into the ledger and the tap. `testing/synctest` (GA in Go 1.25 [inferred, training data]) can make timeout and keep-alive tests deterministic.
- **CI:** the whole suite is loopback-only, with no OS trust changes, so it runs the same on all three OSes (PLAN §8). Add a Windows-only ACL test for the CA key file.

---

## Implications for hylo P3 design

**Package layout** (refines PLAN §6):

```
internal/ca/            CA create/load/rotate (ECDSA P-256, critical name constraints),
                        LeafIssuer.GetCertificate(*tls.ClientHelloInfo) with in-memory cache,
                        trust-bundle writer. No network code. File I/O through internal/platform
                        (Unix modes / Windows DACL).
internal/proxy/
  listener.go           outer http.Server: CONNECT + absolute-form dispatch, single-write 200,
                        hijack with buffered-byte replay, no proxy env (Transport.Proxy=nil)
  policy.go             InterceptPolicy: exact host allowlist (default api.anthropic.com:443)
  tunnel.go             blind TCP relay with half-close, lifecycle events (bytes, duration)
  mitm.go               tls.Server(NextProtos=["http/1.1"], GetCertificate=ca) → one-conn
                        net.Listener → shared inner http.Server (no Read/WriteTimeout)
  forward.go            httputil.ReverseProxy{Rewrite, FlushInterval:-1, ModifyResponse,
                        ErrorHandler}; transports: anthropic (h1 for parity, DisableCompression,
                        system roots or injected), local (plain h1), upgrade (h1-only)
  route/                PURE: Decide(path, headers, body) → {Lane, NewBody, HeaderEdits, Attrib};
                        ports uses_server_tool, normalize_for_dgx, prefix match. Table + fuzz tests;
                        main parity surface
  ssetap/               PURE: Tap (Write/Feed + Result) reproducing _SSETap incl. KEEP=64_000
                        and cache-max semantics; body wrapper lives in forward.go
  usage/                PURE: cache_fields, extract_stop_reason (+ aliases), account hint,
                        DGX in_tok rebuild
  ratelimit.go          per-session change detection for anth_ratelimit (lowercased keys)
internal/ledger/        single writer (mutex, O_APPEND), ordered fields, Python-compatible
                        encoding if byte parity is required (D7)
internal/pyjson/        (only if option (a)) ordered JSON value + json.dumps-compatible encoder
```

**Key rules for the implementation:**

- Every request on an intercepted host goes through `forward.go`. Only `/v1/messages*` reaches `route.Decide`; everything else is forwarded unchanged (Remote Control, telemetry).
- Every `text/event-stream` response is tapped *only* on `/v1/messages*`. All other SSE (Remote Control) is forwarded with flush-per-write and **no tap**.
- The tap and the ledger can never fail a response. Every observer is guarded, the same as legacy.
- The upstream addresses (Anthropic URL/dialer/RootCAs, local URL, key file) come from `internal/config`, with test-only overrides. That gives the parity harness and unit tests their seam.
- The CA private key is never inside the proxy's TLS handshake path. Leaves have their own key.
- Thresholds that need a documented rationale in code and docs (CLAUDE.md): `KEEP=64_000` (inherited, parity), body cap (judgment), leaf validity / renew window (judgment), CA validity (judgment), backdate of 48 h (mitmproxy convention), idle pool size (judgment), outer `ReadHeaderTimeout` (judgment).

---

## Risks

| Risk | Likelihood / impact | Mitigation |
|---|---|---|
| A Remote Control channel (SSE or WebSocket on `api.anthropic.com`) gets buffered or times out, and it fails silently | Medium / high | Flush-per-write for all SSE; no server timeouts; explicit bidirectional RC test in P4; shadow week |
| Claude Code changes transport (HTTP/2 through CONNECT once Bun supports it; new WebSocket paths) | Medium / medium | `hylo doctor` reports the negotiated ALPN; an h2 server path is feasible later; pin the tested Claude Code range (PLAN §9) |
| Allowlist interception drops ledger events that legacy emitted from decrypted non-API hosts (bridge) | High / low | Tunnel lifecycle events; owner decision on parity scope (open question 2) |
| Byte-parity failures from Python JSON formatting, code-point `req_bytes`, local-time `t` | High (if byte diff) / low | Canonical-JSON parity criterion, or `pyjson`; port the formulas exactly |
| Name-constrained CA rejected by some Claude Code path (e.g. a WebSocket client that ignores the extra CA, #102747) | Low–medium / medium | Only `api.anthropic.com` is intercepted; test API, Remote Control and WebFetch paths in P4; fallback flag `ca.name_constraints=false` |
| golang/go#80875 (ReverseProxy upgrade error paths) | Low / medium | Early-bytes test; pin the Go patch release; fall back to a custom 101 relay |
| Windows CA key readable by other local users | Low / high | DACL via `x/sys/windows`; `hylo doctor` check |
| Shared single proxy is a single point of failure for every window (it was per-window before) | Medium / high | `hylo run` health-checks and restarts the proxy; panic recovery per connection; ledger writer isolated |
| Eager → lazy divergence changes failure modes (local lane works when Anthropic is unreachable) | Certain / low (improvement) | Document as an intentional divergence in parity notes |

---

## Open questions for the owner

1. **Interception scope:** approve allowlist interception (`api.anthropic.com` only) instead of legacy's intercept-everything? It is safer, and it makes Name Constraints possible, but it is a behavior change before parity (D4).
2. **Bridge/WebSocket ledger events:** reproduce the legacy quirks (`bridge_ws_close` at handshake with 0.0 s; no `ws_closed`) for the parity diff, or replace them with correct tunnel-lifecycle events and exclude them from the diff?
3. **Parity scope:** is the decision log (`dgx-llm-routing-decisions.log`) in scope, or only the ledger? Should client aborts mid-stream produce a ledger event, as mitmproxy's `error` hook may today?
4. **Upstream HTTP/2 to Anthropic:** start with h1 for parity, then switch on h2 after cutover?
5. **Byte-exact rewritten bodies and ledger lines,** or canonical-JSON equality? Byte-exact pushes toward a `pyjson` encoder; `jsontext` would justify raising the floor to Go 1.27 (GA there, experimental in 1.26).
6. **Shadow week CA:** run hylo with its own name-constrained CA (the shadow window gets a different `NODE_EXTRA_CA_CERTS`) or reuse the existing mitmproxy CA (no new trust, but RSA and unconstrained)? I recommend its own CA.
7. **Windows DACL:** accept `golang.org/x/sys` as a dependency (it is Go-team-owned, and probably needed anyway for process ancestry in `internal/platform`)?

## Inconclusive or unverified

- Whether Go's transport forces HTTP/1.1 on a *new* TLS dial for `Upgrade` requests (`onlyH1`). This is from memory of `transport.go`; I did not re-read it. The design uses a dedicated h1 transport regardless.
- Whether serving a pre-handshaken `*tls.Conn` through `http.Server.Serve` on a one-conn listener needs `Handshake` again. I believe it is a no-op, and that the `TLSNextProto` defaults are set up in `Serve`. **Verify in a P3 spike.**
- Exactly which Remote Control transport (SSE vs WebSocket) the owner's Claude Code version (2.1.322/323) uses. The evidence is user reverse engineering across versions. **Capture it in P4.**
- Whether `NODE_EXTRA_CA_CERTS` applies when `CLAUDE_CODE_CERT_STORE=system` only. Not found.
- The status of goproxy open PRs #806/#815 against v1.9.4. Not verified (and irrelevant if stdlib is chosen).
- Whether mitmproxy's `error` hook fires on a client abort mid-stream. Inferred from its documented error semantics, not tested.

---

## Sources

**Go**
- Go release history (1.26.11, 1.27.4 on 2026-11-10): https://go.dev/doc/devel/release
- `ReverseProxy` source (flushInterval, Director deprecation, upgrade, context): https://go.dev/src/net/http/httputil/reverseproxy.go
- httputil docs: https://pkg.go.dev/net/http/httputil
- net/http (Transport compression, `Protocols`, `ResponseController`): https://pkg.go.dev/net/http
- Go 1.12 (WebSocket in ReverseProxy): https://go.dev/doc/go1.12
- Go 1.20 (Rewrite, ResponseController): https://go.dev/doc/go1.20
- Go 1.24 (Protocols, unencrypted HTTP/2): https://go.dev/doc/go1.24
- Go 1.26: https://go.dev/doc/go1.26
- Go issues: SSE latency https://github.com/golang/go/issues/27816 · charset https://github.com/golang/go/issues/47359 · flush wrapper https://github.com/golang/go/issues/64045 · upgrade leaks https://github.com/golang/go/issues/80875 · httptest h2 https://github.com/golang/go/issues/34939
- crypto/x509 name constraints: https://pkg.go.dev/crypto/x509 · https://go.dev/src/crypto/x509/name_constraints_test.go
- `os` on Windows (mode bits): https://pkg.go.dev/os
- encoding/json/v2 and jsontext: https://go.dev/blog/jsonv2 · https://pkg.go.dev/encoding/json/jsontext

**Libraries**
- goproxy: https://pkg.go.dev/github.com/elazarl/goproxy?tab=versions · https://github.com/elazarl/goproxy · v1.9.0 https://github.com/elazarl/goproxy/releases/tag/v1.9.0 · v1.8.6 https://github.com/elazarl/goproxy/releases/tag/v1.8.6 · https.go https://github.com/elazarl/goproxy/blob/master/https.go
- martian (archived): https://github.com/google/martian · issue #31 https://github.com/google/martian/issues/31
- go-mitmproxy: https://pkg.go.dev/github.com/lqqyt2423/go-mitmproxy?tab=versions · https://github.com/lqqyt2423/go-mitmproxy · issues https://github.com/lqqyt2423/go-mitmproxy/issues

**mitmproxy**
- Options (ignore_hosts/allow_hosts, http2, connection_strategy, store_streamed_bodies): https://docs.mitmproxy.org/stable/concepts/options/
- Event hooks: https://docs.mitmproxy.org/stable/api/events.html
- HTTP API (stream, set_text): https://docs.mitmproxy.org/stable/api/mitmproxy/http.html · source https://github.com/mitmproxy/mitmproxy/blob/main/mitmproxy/http.py
- Protocols: https://docs.mitmproxy.org/stable/concepts/protocols/
- Certificates: https://docs.mitmproxy.org/stable/concepts/certificates/ · https://docs.mitmproxy.org/stable/api/mitmproxy/certs.html
- Ignore domains: https://docs.mitmproxy.org/stable/howto/ignore-domains/
- HAR support: https://www.mitmproxy.org/posts/har-support/
- Server replay: https://github.com/mitmproxy/mitmproxy/blob/main/mitmproxy/addons/serverplayback.py

**Node / Bun / Claude Code**
- Node enterprise network config: https://nodejs.org/learn/http/enterprise-network-configuration
- Node CLI (`NODE_EXTRA_CA_CERTS`, `--use-system-ca`): https://nodejs.org/docs/latest/api/cli.html
- Node http (env proxy): https://nodejs.org/api/http.html
- undici EnvHttpProxyAgent: https://undici.nodejs.org/api/EnvHttpProxyAgent
- undici v7→v8 (`allowH2`): https://github.com/nodejs/undici/blob/v8.11.0/docs/docs/best-practices/migrating-from-v7-to-v8.md
- Bun proxy guide: https://bun.sh/guides/http/proxy
- Bun fetch: https://bun.sh/docs/runtime/networking/fetch
- Bun release notes: 1.1.22 (extra CA) https://bun.com/blog/bun-v1.1.22 · 1.2.23 (system CA) https://bun.com/blog/bun-v1.2.23 · 1.3.6 (WebSocket proxy) https://bun.com/blog/release-notes/bun-v1.3.6 · 1.3.14 (experimental h2, no CONNECT) https://bun.com/blog/release-notes/bun-v1.3.14 · 1.4.4 (Ed25519) https://bun.com/blog/bun-v1.4.4
- Claude Code network config: https://code.claude.com/docs/en/network-config
- Remote Control: https://code.claude.com/docs/en/remote-control
- Claude Code issues: https://github.com/anthropics/claude-code/issues/11660 · /10458 · /14165 · /50252 · /85979 · /97352 · /99296 · /102747 · /76642 · /72749 · /100377 · /31853 · /20194

**PKI**
- RFC 5280: https://www.rfc-editor.org/rfc/rfc5280.html
- OpenSSL `x509_vfy.c`: https://github.com/openssl/openssl/blob/master/crypto/x509/x509_vfy.c
- `NAME_CONSTRAINTS_check`: https://docs.openssl.org/master/man3/NAME_CONSTRAINTS_check/
- OpenSSL CN-fallback issue: https://github.com/openssl/openssl/issues/30346
- BoringSSL `verify_certificate_chain.h`: https://boringssl.googlesource.com/boringssl/+/master/pki/verify_certificate_chain.h
- Apple certificate requirements: https://support.apple.com/en-us/103769 · https://support.apple.com/en-us/102028
- CA/B Forum SC081v3: https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/
- smallstep templates (constrained intermediates): https://smallstep.com/docs/step-ca/templates/
- mkcert name-constraints discussion: https://github.com/FiloSottile/mkcert/issues/131

---

## Research Methods

| Tool | Queries | Purpose |
|---|---|---|
| **Perplexity perplexity_research (PRIMARY)** | 7 | Go MITM library landscape; Node/undici proxy + CA semantics and Claude Code network docs; ReverseProxy streaming/upgrade/compression behavior; Bun runtime + Claude Code proxy issues; name constraints, key types, validity, mitmproxy CA; mitmproxy internals (h2, stream, headers, hosts, reuse, errors, recording); Remote Control network behavior |
| Perplexity perplexity_reason | 0 | — |
| Perplexity perplexity_search | 0 | — |
| Perplexity perplexity_ask | 2 | encoding/json/v2 status (1.26 vs 1.27); Windows file mode vs ACLs in Go |
| Context7 | 2 | resolve + query `/elazarl/goproxy` (per-host MITM API, AllowHTTP2, MITM loop and handshake code) |
| Tavily tavily_search | 1 | Prior art for in-process CONNECT/MITM proxy tests with httptest |
| Tavily tavily_research / extract / crawl / map | 0 | — |
| WebFetch | 5 | pkg.go.dev versions (goproxy, go-mitmproxy); go.dev release history; `reverseproxy.go` source; google/martian archive status |
| WebSearch | 0 | — |
| Repository reads | 3 files | `docs/PLAN.md`, `legacy/dgx_proxy.py`, `legacy/claude-dgx` (behavior inventory, parity traps) |
| Training data | 4 areas | Go `transport.go` `onlyH1` for upgrades; `http.Server.Serve` with a pre-handshaken `*tls.Conn`; `testing/synctest` GA version; Python `json.dumps` defaults and float repr. All flagged [inferred] |

**Total MCP tool calls:** 12 (7 perplexity_research, 2 perplexity_ask, 2 Context7, 1 Tavily), plus 5 WebFetch.
**Training data reliance:** low–medium. Library versions, maintenance status, Go/Bun/Node/Claude Code behaviors and mitmproxy semantics are web-sourced (several from source code). A few Go-internals and Python-encoding details come from model knowledge; they are tagged [inferred] and listed under "Inconclusive or unverified" for a P3 spike.
