# Peer-tool lessons and owner decisions OD-1 / OD-2

- **Type:** general (follow-up to `domain-hybrid-routing-claude-code-2026-11-14.md` §1.2/§4.3)
- **Date:** 2026-11-14 (sources accessed 2026-11-13/14; Claude Code current = 2.1.325)
- **Claim tags:** **[documented]** official docs, changelog or registry · **[community-observed]** issues, third-party READMEs · **[inferred]** this report's reasoning
- **Legacy references** were checked with grep on `legacy/` on 2026-11-14. They are cited by symbol (function or class) per the stable-anchor rule TD-VSDD-091; the coordinator's line numbers map onto these symbols.
- **Status of OD-1 / OD-2:** decided by the owner on 2026-11-14 and recorded verbatim below. They are **pending addition to `docs/PLAN.md` as D13/D14**; whether to add them is the owner's call.

## Summary

- Five peer lessons are **already covered by legacy**. Seven are new: L1 became OD-2, L2 is rejected by OD-1, and L3-L7 land in P3, P6 or nowhere. One pattern must **not** be copied: teamclaude's account rotation.
- **OD-1 (intercept everything)** supersedes the name-constrained-CA recommendation in `general-go-tls-intercepting-proxy-2026-11-14.md` (summary item 6, open question 1). The CA must mint leaves for any host, so the protection shifts to compensating controls (§2.2). A defined failure behavior is needed for hosts that cannot be intercepted (§2.4).
- **OD-2 (no proxy leakage to children):** Claude Code has **no** non-environment proxy setting. Its own subprocess scrub **explicitly keeps** `HTTP_PROXY`/`HTTPS_PROXY`. The only documented lever that reaches Bash commands is `CLAUDE_ENV_FILE`. **Recommendation:** combine (f) a launcher shim with (a) a SessionStart hook that writes `unset …` lines, and (b) make hylo-owned commands ignore proxy environment. Residual leaks are reported by `hylo doctor`: user hooks, MCP stdio servers, the PowerShell tool, and sandbox chaining.

---

## 1. Lessons from peer tools

**Already covered by legacy (no action beyond parity):**
- every non-`/v1/messages` request is passed through (`legacy/dgx_proxy.py` module docstring);
- the WebSocket bridge lifecycle is logged for `bridge.claudeusercontent.com`: module docstring; `bridge_ws_connect` emitted in `DGXRouter.request`; `bridge_ws_close` emitted in `DGXRouter.response`; hooks `websocket_start`/`websocket_end`;
- `anthropic-beta` is stripped on the local lane (`DGXRouter.request`, the `headers.pop("anthropic-beta")` line);
- unknown content block types are dropped and logged once (`normalize_for_dgx`);
- `count_tokens` is classified separately in the ledger (`DGXRouter.request`, endpoint classification).

| # | Lesson | Source tool | Why it matters | Deviates from legacy? (policy 13) | Disposition |
|---|---|---|---|---|---|
| L1 | Don't leak proxy env to child processes | cablate/model-relay README (`HTTPS_PROXY` in settings `env` also hits `git`/`curl`/`gh`, which fail while the router is down) [community-observed] | Children are routed through a TLS-terminating proxy they never asked for, and they break when it dies | **Yes**: the legacy launcher `claude-dgx` exports `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` | **→ OD-2** (§3) |
| L2 | Selective interception (intercept only the API host, blind-tunnel the rest) | KarpelesLab/teamclaude `docs/proxy-modes.md` [community-observed] | Smaller attack surface; would allow a name-constrained CA | Yes (legacy intercepts everything) | **Rejected by OD-1** |
| L3 | Serve HTTP/2 on intercepted connections, with an HTTP/1.1-only switch | teamclaude (real h2 server; Desktop needs `mitm.http1Only`) [community-observed] | Bun/undici negotiate h2 via ALPN; some clients need 1.1 | Parity-neutral (mitmproxy also speaks h2) | **P3** |
| L4 | Refuse to proxy through yourself (loop detection) | teamclaude (drops an upstream proxy whose address is its own listener) [community-observed] | A `hylo` started from a shell that inherited `HTTPS_PROXY` would recurse into itself | Parity-neutral | **P3** |
| L5 | Per-backend allow-list of request fields and `anthropic-beta` values, plus surfacing unknown fields | Lesson from the 2026 breakage table (domain report §4.3: `context_management` 2.1.22, `system` role in `messages[]` 2.1.154, tool search `tool_reference` 2.1.304, advisor tag 2.1.275, `\p{}` schema 2.1.265) [documented/community-observed] | Invisible mode means Claude Code believes it is talking to Anthropic, so its base-URL fallbacks (2.1.304/305 retries) never trigger. hylo is the only defense on the local lane [inferred] | Surfacing: parity-neutral if **debug log only** (ledger frozen per D7 / policy 17). Allow-list: a behavior change | **P3** debug-log surfacing; **P6** allow-list |
| L6 | Opt-in failover to Anthropic when the local backend is unreachable | Screddyice/backdoor (opt-in cloud↔local failover on transport outage), model-relay (`failover.chain`) [community-observed] | Keeps a session alive when the GPU box is down, **but bills the subscription**, so it must be opt-in and visible on the status line | **Yes**: legacy logs `<lane>_upstream_error` and fails (`DGXRouter.error`) | **P6**, opt-in, status-line indicator |
| L7 | Per-window lane state file | model-relay (per-session relay-state file for status bars) [community-observed] | Lets the status line show the lane | No | **Covered**: hylo's status line already derives the lane (pill) |
| ✗ | **Do NOT copy:** account rotation / quota pooling | teamclaude | The Usage Policy (eff. 2026-11-12) bans "services that route requests through consumer subscriptions"; pooling accounts is the clearest match [documented: anthropic.com/legal/aup] | — | Never |

**Open gap:** no peer's Remote Control claim has been independently verified: model-relay and backdoor self-report, and the CLIProxyAPI sidecar is one user's report. **The P3 shadow week must test Remote Control explicitly:** pair from mobile or the web, send a prompt, see it stream, disconnect and reconnect, run a long idle period. Bridge WebSocket connect/close events should appear in the ledger as they do in legacy. [inferred]

---

## 2. OD-1 (proposed D13): intercept all Claude Code traffic

> **Decided (owner, 2026-11-14):** ALL traffic from the Claude Code process goes through the intercept. TLS is terminated for every host Claude Code contacts, as legacy does today (mitmproxy default, no `ignore_hosts`/`allow_hosts`; the `HTTPS_PROXY` export in `claude-dgx`). Only `POST /v1/messages` on `api.anthropic.com` is ever rewritten; every other host and path is forwarded unmodified.

*Pending addition to docs/PLAN.md as D13.*

### 2.1 Consequences

- **Supersedes** the recommendation in `general-go-tls-intercepting-proxy-2026-11-14.md`: its summary item 6 (a critical Name Constraints extension permitting only intercepted DNS names), its "name-constrained CA rejected" risk row, and its open question 1 (allow-list interception). The CA must be able to mint a leaf for **any** DNS name Claude Code contacts: `api.anthropic.com`, `bridge.claudeusercontent.com`, `claude.ai`, remote MCP servers, WebFetch targets, telemetry and update hosts. [inferred]
- **Scope note:** legacy exports only `HTTPS_PROXY`, not `HTTP_PROXY`, so plain-HTTP requests from Claude Code bypass the proxy today. "All traffic" in practice means all HTTPS/CONNECT traffic. Parity (D4) says keep it that way; the owner may confirm. [documented: legacy `claude-dgx`]

### 2.2 Compensating controls (the CA is now unconstrained by design)

| Control | Detail | Tag |
|---|---|---|
| **Trust scope** | The CA is trusted **only** through `NODE_EXTRA_CA_CERTS` for the Claude process, and **never** installed in an OS trust store. Combined with OD-2's `unset NODE_EXTRA_CA_CERTS` for Bash children, only the `claude` process trusts it | [inferred] |
| **Flag: legacy keychain install** | Legacy's `trust install` (`cmd_trust_install` in `legacy/dgx_proxy.py`) adds the CA to the **macOS login keychain**. It even prints that keychain trust covers "Apple-native, Go, curl, .NET stacks". With an unconstrained CA, that is machine-wide impersonation capability for any process of the user. **Recommend `hylo ca` does not port `trust install`** (Claude Code does not need it), or keeps it behind an explicit `--os-trust` flag with a warning. `hylo doctor` should detect a leftover keychain entry (legacy's `cmd_trust_status`/`cmd_trust_remove` already show how). **Owner decision.** | [documented: legacy] / [inferred] |
| **CA key protection** | Unix: directory `0700`, key `0600`, owned by the user. Windows: an explicit NTFS DACL (`icacls /inheritance:r`, then remove other explicit grants; owner and SYSTEM only). Optionally encrypt with **user-scoped** DPAPI (not `CRYPTPROTECT_LOCAL_MACHINE`). Mode bits do nothing on Windows. Neither protects against compromise of the running account | [documented: Microsoft icacls/DPAPI docs; Red Hat] |
| **Short-lived leaves** | Generate in memory. Validity of a few days to 30 days with automatic regeneration; mitmproxy uses 199 days total (2 days backdated + 197). The TLS report's 30-day judgment call still stands; short validity is nearly free with an in-memory cache. Limits a stolen *leaf* key, not a stolen CA key | [documented: mitmproxy 12.3.0 `certs.py`] |
| **Strict upstream verification** | Verify every upstream against the system roots (plus an explicit corporate CA if configured). **Never `InsecureSkipVerify`.** On a verification failure, fail the client connection; never downgrade | [inferred; standard practice] |
| **CA rotation** | `hylo ca rotate` (legacy has `cmd_trust_rotate`) creates a new key and CA, `NODE_EXTRA_CA_CERTS` is updated on the next `hylo run`, and the old CA is deleted | [inferred] |
| **Exclusion-only name constraint** (optional) | Go can emit one: empty `PermittedDNSDomains`, `ExcludedDNSDomains: ["local"]`, `ExcludedIPRanges: 0.0.0.0/0, ::/0`, `PermittedDNSDomainsCritical: true`. Benefit: a stolen key cannot impersonate IP-literal hosts or mDNS `.local` names (typical LAN targets) to the trusting process. Limits: it does not block `localhost`, private DNS zones, or public names resolving to private IPs; wildcard handling varies. **Bun caveat:** Bun 1.4.4 rejected IP-SAN leaves under IP-constrained CAs with `UNSUPPORTED_CONSTRAINT_TYPE`; a fix was proposed (oven-sh/bun PR #46522). Behavior varies by version and must be tested against Claude Code's embedded Bun. **Consequence under OD-1:** hylo could not intercept an IP-literal host, so such hosts would need blind-tunnelling, a narrow exception to "TLS terminated for every host". **Assessment:** modest value, since the trust scope is already one process. Worth it only if the owner accepts the IP-literal exception | [documented: pkg.go.dev crypto/x509, RFC 5280] / [community-observed: Bun] / [inferred] |

### 2.3 What the proxy must handle for arbitrary hosts (P3)

- **Per-host ALPN:** offer `h2,http/1.1` to the client and negotiate upstream separately. Do not assume the upstream speaks h2 just because the client does (L3). A config switch forces HTTP/1.1. [inferred]
- **WebSocket upgrades:** pass them through on any host. That covers Remote Control on `api.anthropic.com` (bridge paths `/v1/environments/`, `/v1/sessions/`, `/v2/session_ingress/`, `/v2/ccr-sessions/`, `/v1/code/`) and on `bridge.claudeusercontent.com`. Keep legacy's lifecycle events (D7). Over h2, WebSocket uses extended CONNECT (RFC 8441); forcing 1.1 for upgrade requests is a fallback. [community-observed: teamclaude; legacy `websocket_start`/`websocket_end`]
- **SSE:** flush per event, never buffer or compress-transform. **No idle or write timeouts on intercepted streams:** long thinking pauses and RC sessions idle for hours. Only header-read timeouts on the client side. [inferred; matches the TLS report]
- **Unmodified forwarding:** headers, bodies and paths for every host and path except `POST api.anthropic.com/v1/messages`. Hop-by-hop headers are handled per RFC 9110. [inferred]

### 2.4 Hosts that cannot be intercepted: proposed failure behavior (owner decides)

**Background:** mitmproxy has no automatic fallback by default. Its `tls_passthrough.py` is an optional example that passes **subsequent** connections through after a *client-side* handshake failure; the first connection still fails. [documented: mitmproxy docs/examples]

**Proposal:**

1. **Static list:** `proxy.passthrough_hosts` in config (host:port regex) means a blind CONNECT tunnel. The client sees the real certificate, so end-to-end mTLS and pinning work. **`api.anthropic.com` cannot be listed** (routing would be impossible), so config validation rejects it.
2. **Client rejects hylo's leaf** (pinning, or a runtime ignoring `NODE_EXTRA_CA_CERTS`, e.g. the voice WebSocket in claude-code#102747): log `tls_client_reject host=…` to the debug log, add host:port to an in-memory passthrough set for the proxy's lifetime, and blind-tunnel subsequent CONNECTs. The first attempt fails; Claude Code's own retry usually succeeds.
3. **Upstream requests a client certificate:** if `CLAUDE_CODE_CLIENT_CERT`/`_KEY` are configured (Claude Code's documented mTLS settings [documented: network-config]), hylo presents the same cert upstream. Otherwise fail the connection with a clear error and add the host to the passthrough set (same as 2).
4. **`api.anthropic.com` itself cannot be intercepted:** **fail closed** with a loud error (stderr from `hylo run`, debug log, `hylo doctor`). Silently tunnelling would send local-lane requests to Anthropic and bill the subscription.

Learned passthroughs are **not** persisted across restarts by default (so a fixed CA problem is not hidden). `hylo doctor` lists them. [inferred]

---

## 3. OD-2 (proposed D14): proxy configuration must not leak to Claude Code's children

> **Decided (owner, 2026-11-14):** proxy configuration must NOT leak to Claude Code's child processes: Bash tool commands, git/gh/curl, hooks, the status line command, MCP stdio servers. This is an owner-approved deviation from legacy (the `claude-dgx` launcher exports `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` into the whole environment).

*Pending addition to docs/PLAN.md as D14.*

### 3.1 Facts from current Claude Code docs (2.1.325)

- **Inheritance:** children inherit Claude Code's environment by default. The settings `env` block is applied to the session environment and inherited by subprocesses. Setting a variable to `""` passes an empty value, not an absent one. [documented: settings-reference, env-vars]
- **`CLAUDE_ENV_FILE`:** "a shell script whose contents Claude Code runs before each Bash command in the same shell process". It is populated by **SessionStart, Setup, CwdChanged and FileChanged** hooks. It is **not** available to hooks running in PowerShell. PowerShell *tool* commands import only plain assignments from it (2.1.296+), so an `unset` line prevents the import, and PowerShell never executes the file as code. [documented: hooks, env-vars, extracted 2026-11-14]
- **`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`:** strips credentials from Bash, hook and stdio-MCP environments, but **"leaves … proxy settings in place"** (`HTTP_PROXY`, `HTTPS_PROXY`, "including a username and password in the URL"). [documented: env-vars, extracted]
- **No proxy setting outside the environment** for Claude Code's own traffic: only `HTTPS_PROXY`/`HTTP_PROXY`/`NO_PROXY` via the launch env or settings `env`. `sandbox.network.httpProxyPort`/`socksProxyPort` redirect **sandboxed commands** to a custom proxy, not Claude's own traffic. [documented: network-config, settings-reference, sandboxing]
- **Sandbox chaining:** for sandboxed commands, Claude Code injects its own `HTTP(S)_PROXY`/`ALL_PROXY` pointing at its sandbox proxy, which **tunnels allowed connections through the upstream proxy from the parent environment**. So with sandboxing on, child traffic reaches hylo even if the Bash shell unsets the variables. [documented: sandboxing]
- **MCP stdio servers:** per-server `env` **merges** over the inherited environment. `CLAUDE_CODE_MCP_ALLOWLIST_ENV=1` replaces the inherited base with a "safe baseline" plus the configured `env`. Whether that baseline includes proxy variables is **not stated: inconclusive**. [documented / inconclusive]
- **Subagents and `CLAUDE_ENV_FILE`:** reports conflict. One macOS report says subagents got separate empty files; a later Windows report on 2.1.299/2.1.304 says they shared the session file. **Must be tested** on the pinned version. [community-observed: #46696, #103861]

### 3.2 Mechanism comparison

| Mech. | What it covers | Gaps | Effort / risk | Tag |
|---|---|---|---|---|
| **(a)** SessionStart hook → `CLAUDE_ENV_FILE` with `unset HTTPS_PROXY https_proxy HTTP_PROXY http_proxy ALL_PROXY all_proxy NODE_EXTRA_CA_CERTS` | Every **Bash tool** command, foreground and background (the file runs before each command) | Not hooks, status line or MCP stdio. **Not the PowerShell tool** (an `unset` line is ignored/blocks the import), which matters on Windows without Git Bash. Subagents: test. **Sandboxed commands still reach hylo** via sandbox chaining. Lines added by `CwdChanged` are cleared on the next cwd change; SessionStart lines persist | Low: documented, injected via hylo's `--settings` (hook arrays from multiple settings sources combine [inferred; test]) | [documented] |
| **(b)** hylo-owned wrappers that scrub the environment | `hylo statusline` and `hylo hook stop`: hylo controls these binaries, so it can ignore proxy env internally (legacy's status line already bypasses the proxy for metrics in `fetch_sample` of `legacy/dgx_statusline.py`). User hooks and MCP servers could be wrapped by rewriting their commands into `hylo exec --clean-env -- <cmd>` | Wrapping *user* commands means editing user settings or `.mcp.json`, which is invasive and fragile. Plugin-provided hooks and MCP servers can't be rewritten cleanly | Low for hylo-owned commands; high for user commands | [inferred] |
| **(c)** A non-environment proxy setting | — | **Does not exist** for Claude's own traffic | n/a | [documented] |
| **(d)** Per-MCP `env` overrides (`"HTTPS_PROXY": ""`, …) | A specific stdio MCP server | Sets an *empty* value, not an unset one. Most stacks treat empty as "no proxy" (Go `net/http`, curl, undici) [inferred; per-tool]. Per-server config edits; `NODE_EXTRA_CA_CERTS=""` behavior is runtime-specific. `CLAUDE_CODE_MCP_ALLOWLIST_ENV=1` might cover all servers at once **if** its baseline omits proxy vars (inconclusive) | Medium; user-config edits | [documented] / [inferred] |
| **(e)** Claude Code strips proxy vars itself | — | **No**: the scrub keeps them explicitly. No documented env-scrub option for proxies | n/a | [documented] |
| **(f)** `hylo run` shim sets the variables only on the `claude` process | Keeps them out of the user's shell and the rest of the desktop (legacy is effectively this already: the export happens inside the `claude-dgx` script) | Children of `claude` still inherit. Needs (a)/(b) | Trivial; `os/exec` with `cmd.Env` on all three OSes | [inferred] |

### 3.3 Recommendation (not decided)

**(f) + (a) + (b, hylo-owned only)**, plus `hylo doctor` reporting the residual surfaces:

1. `hylo run` launches `claude` with `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` in **that process's** env only (f). It never writes them to settings `env`, which would reach every child and every session.
2. Through `--settings`, `hylo run` adds a **SessionStart** hook, `hylo hook session-start`, that appends the `unset …` line to `$CLAUDE_ENV_FILE` (a). Re-asserting the same line from a `CwdChanged` hook is unnecessary, because SessionStart lines persist.
3. `hylo statusline` and `hylo hook stop` construct their HTTP clients with `Proxy: nil` and system roots only (b). This is parity-compatible: the status line already bypasses the proxy.
4. **Residual leaks, documented and detected:**
   - user/plugin hooks and MCP stdio servers (pending the owner question below);
   - the **PowerShell tool** on Windows (`hylo doctor` warns when Git Bash is absent);
   - **sandbox mode** (sandboxed child traffic chains through hylo. Since hylo tunnels it unmodified under OD-1, this is a routing leak, not a rewrite; detecting it would need a `hylo doctor` check for `sandbox.enabled`);
   - subagent Bash, if the version test shows a separate env file.
5. **Test in P4 on each OS:** in a hylo session, `env | grep -i proxy` through the Bash tool should be empty, including from a subagent and a background task. Check the status line and Stop hook process env.

**Why not (b) for everything:** rewriting user hook and MCP commands changes user-owned config. It conflicts with "never touch `~/.claude/settings.json`", which is the launcher's existing principle (STATUSLINE-WIDGETS "How it runs"). [inferred]

### 3.4 Side questions

- **Does leaking `NODE_EXTRA_CA_CERTS` alone matter?** It routes nothing: a child Node/Bun process only *trusts* the hylo CA. Under OD-1 that CA is unconstrained, so a leaked trust means any child JS process would accept certificates from anyone who obtains the CA key. Exposure is low as long as the key is protected (§2.2), but unsetting it costs nothing. **Unset it too.** [inferred]
- **Does `hylo run` restarting a dead proxy reduce blast radius?** It reduces the **availability** blast radius (children routed through a dead proxy fail; Claude itself fails until restart). It does nothing for the routing/interception leak, which is what OD-2 addresses. With OD-2 in place, a dead proxy affects only Claude's own requests, and the restart covers that. [inferred]
- **Remote MCP servers (HTTP/SSE)** that Claude Code connects to itself are Claude traffic under OD-1: intercepted and forwarded unmodified. [owner decision restated]

---

## Phase mapping

| Item | P3 | P4 | P6 |
|---|---|---|---|
| L3 h2 + HTTP/1.1 switch; L4 self-loop refusal | ✔ | | |
| L5 unknown fields/betas → debug log (ledger unchanged, D7) | ✔ | | |
| L5 per-backend allow-list | | | ✔ |
| L6 opt-in failover + status-line indicator | | | ✔ |
| OD-1 arbitrary-host intercept, WebSocket passthrough, SSE flush, no stream idle timeouts, strict upstream verify | ✔ | | |
| OD-1 failure behavior (passthrough list, learned passthrough, fail-closed for api.anthropic.com, mTLS cert reuse) | ✔ | | |
| OD-1 CA controls (key ACLs/DPAPI, short leaves, rotate; no OS-trust install by default; optional exclusion constraint) | ✔ (leaf mint) | ✔ (`hylo ca`, `hylo doctor` keychain check) | |
| OD-2 (f) shim env + (a) SessionStart unset hook + (b) hylo-owned commands without proxy | | ✔ | |
| OD-2 residual-leak checks in `hylo doctor` (PowerShell, sandbox, subagents) | | ✔ | |
| Remote Control explicit test plan | ✔ (shadow week) | ✔ (exit criterion) | |

**Parity note (D4):** OD-1 is parity-preserving. OD-2 and the keychain change are owner-approved deviations. During the P3 shadow week, the shadow window should use OD-2 behavior while Python windows keep legacy env; the ledger diff is unaffected because children's traffic never touched `/v1/messages`. [inferred]

---

## Open questions for the owner

1. **Should MCP stdio servers and user/plugin hooks count as "Claude traffic" (proxied) or as children (not proxied)?** Recommendation: children, not proxied, and documented as a residual leak unless the owner opts into per-server `env` overrides (d).
2. **Uninterceptable hosts:** approve the proposed behavior (§2.4): static passthrough list, learned in-memory passthrough after client reject or upstream client-cert request, reuse of `CLAUDE_CODE_CLIENT_CERT` upstream, fail-closed for `api.anthropic.com`?
3. **Legacy keychain install:** drop `trust install` in `hylo ca`, or keep it behind `--os-trust` with a warning? Also, should `hylo doctor` offer to remove a leftover legacy keychain entry?
4. **Exclusion-only name constraint** (no IPs, no `.local`): worth adopting, given it forces blind-tunnelling of IP-literal hosts (a narrow OD-1 exception) and needs a Bun compatibility test?
5. **Sandbox mode:** with Claude Code's sandbox on, child traffic chains through hylo regardless of OD-2. Accept and document it, or have `hylo run` refuse or warn when sandboxing is enabled? (Legacy's `claude-dgx` has safe/sandbox modes. Check how they interact.)
6. **`HTTP_PROXY`:** keep legacy's HTTPS-only export (parity), confirming "all traffic" means all HTTPS?
7. **Add OD-1/OD-2 to PLAN.md as D13/D14?**

---

## Sources (accessed 2026-11-13/14)

- Claude Code hooks reference (`CLAUDE_ENV_FILE`, events, PowerShell): https://code.claude.com/docs/en/hooks (extracted)
- Claude Code env vars (`CLAUDE_ENV_FILE`, `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` table, `CLAUDE_CODE_MCP_ALLOWLIST_ENV`): https://code.claude.com/docs/en/env-vars (extracted)
- Network config (proxy vars, mTLS, CA): https://code.claude.com/docs/en/network-config
- Settings reference (`env` block, sandbox proxy ports): https://code.claude.com/docs/en/settings-reference
- Sandboxing (injected proxy, upstream chaining): https://code.claude.com/docs/en/sandboxing
- MCP (stdio `env` merge): https://code.claude.com/docs/en/mcp
- Claude Code releases 2.1.296 (PowerShell env file), 2.1.251 (scrub), 2.1.325: https://github.com/anthropics/claude-code/releases
- Subagent env-file reports: https://github.com/anthropics/claude-code/issues/46696, https://github.com/anthropics/claude-code/issues/103861
- Voice WebSocket CA failure: https://github.com/anthropics/claude-code/issues/102747
- Usage Policy (account pooling / consumer-subscription routing): https://www.anthropic.com/legal/aup (extracted)
- cablate/model-relay README: https://github.com/cablate/model-relay (extracted)
- teamclaude proxy modes: https://github.com/KarpelesLab/teamclaude/blob/master/docs/proxy-modes.md (extracted)
- Screddyice/backdoor: https://github.com/Screddyice/backdoor
- Go crypto/x509 name constraints: https://pkg.go.dev/crypto/x509 · RFC 5280: https://www.rfc-editor.org/rfc/rfc5280.html
- Bun IP name-constraint handling: https://github.com/oven-sh/bun/issues/45055, https://github.com/oven-sh/bun/pull/46522
- mitmproxy certificates / ignore hosts / tls_passthrough: https://docs.mitmproxy.org/stable/concepts-certificates/, https://docs.mitmproxy.org/stable/howto/ignore-domains/, https://github.com/mitmproxy/mitmproxy/blob/main/examples/contrib/tls_passthrough.py, https://github.com/mitmproxy/mitmproxy/blob/v12.3.0/mitmproxy/certs.py
- Windows ACL / DPAPI: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls, https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata
- Internal (symbol anchors):
  - `legacy/claude-dgx` (the `HTTPS_PROXY` / `NODE_EXTRA_CA_CERTS` exports);
  - `legacy/dgx_proxy.py`: module docstring, `DGXRouter.request`, `DGXRouter.response`, `DGXRouter.error`, `normalize_for_dgx`, `websocket_start`, `websocket_end`, `cmd_trust_install`, `cmd_trust_status`, `cmd_trust_remove`, `cmd_trust_rotate`;
  - `legacy/dgx_statusline.py`: `fetch_sample`;
  - `general-go-tls-intercepting-proxy-2026-11-14.md`; `domain-hybrid-routing-claude-code-2026-11-14.md`.

## Research Methods

| Tool | Queries | Purpose |
|---|---|---|
| **Perplexity perplexity_research (PRIMARY)** | 2 | Claude Code env propagation to children (`CLAUDE_ENV_FILE`, scrub, sandbox proxy, MCP env, hooks/status line); private-CA practice (name constraints in Node/Bun/Go, leaf lifetime, Windows key ACL/DPAPI, uninterceptable-host handling) |
| Tavily tavily_extract | 1 call (2 URLs) | Verbatim verification of hooks and env-vars docs (`CLAUDE_ENV_FILE` semantics; scrub keeps proxy vars) |
| Grep (local, public `legacy/` and prior research) | 4 | Verify legacy references and map them to symbols; locate the superseded name-constraint recommendation |
| Context7 / WebFetch / WebSearch | 0 | Not needed: official docs were extracted directly |
| Training data | 1 area | Protocol background (RFC 8441 extended CONNECT, hop-by-hop headers, empty-proxy-var behavior in Go/curl/undici): flagged [inferred] |

**Total MCP tool calls:** 3 (2 perplexity_research, 1 tavily_extract). Prior-report MCP evidence (15 calls) is reused for L1-L7.
**Training data reliance:** low-medium. The OD-2 mechanism facts are verbatim-verified. Empty-value proxy semantics per tool and hook-array merging across `--settings` are inferred and need P4 tests.
**Inconclusive:** whether the `CLAUDE_CODE_MCP_ALLOWLIST_ENV` baseline includes proxy variables; `CLAUDE_ENV_FILE` propagation to subagents (conflicting reports); Bun IP-constraint behavior in Claude Code's embedded runtime.
