# Domain research: hybrid local + cloud routing for Claude Code

- **Type:** domain
- **Date:** 2026-11-14 (UTC; sources accessed 2026-11-13/14)
- **Project:** hylo (public, `drbothen/hylo`)
- **Scope:** landscape, Claude Code configuration surfaces, Anthropic Messages API facts, policy/brand risks, OpenAI-compat translation
- **Claim tags:** **[documented]** = official vendor docs/changelog/registry; **[community-observed]** = GitHub issues, third-party READMEs, user reports; **[inferred]** = this report's reasoning, not directly sourced.
- **Settled decisions:** D1-D12 in `docs/PLAN.md` are not reopened here. Items that bear on them appear as **"risk for owner awareness"**.

---

## Executive summary

1. **hylo is not the first endpoint-preserving (TLS-interception) router.** At least six projects now intercept `api.anthropic.com` through `HTTPS_PROXY` + `NODE_EXTRA_CA_CERTS` while leaving the base URL alone; the closest is **cablate/model-relay** (MIT, v0.7.5, 2026-10-24), which says it keeps Remote Control working. **KarpelesLab/teamclaude** (MIT, v1.1.29) publishes the most detailed list of Remote Control paths to pass through untouched. [community-observed]
2. **What sets hylo apart is the full package, not the routing trick:** one static cross-platform Go binary, an append-only usage ledger, a Prometheus exporter, a two-row status line that knows which lane served the session (with backend GPU telemetry and owned-hardware cost), and the parity-tested move from a prototype in daily use. None of the surveyed tools combines all of these. [inferred]
3. **Remote Control requires `api.anthropic.com`.** Since Claude Code **2.1.196**, an `ANTHROPIC_BASE_URL` pointing at any other host (including a localhost proxy) disables it, and so does an API key or auth-token override. This confirms D6. [documented]
4. **Since 2.1.287, `claude remote-control` sends its bridge traffic through `HTTPS_PROXY`** (`/v1/code/`, `/v1/environments/`, `/v1/sessions/`, `/v2/session_ingress/`, `/v2/ccr-sessions/`, plus `/v1/oauth/token`). hylo must pass these through byte-for-byte. [community-observed: teamclaude docs]
5. **Every local server hylo plans to support now serves `/v1/messages` natively,** with SSE and tool use: vLLM ≥0.11.1, llama.cpp ≥b7187, Ollama ≥0.14.0, LM Studio ≥0.4.1, SGLang ≥0.5.9. The OpenAI-translation part of P6 is therefore much less important for Ollama and LM Studio than PLAN.md assumes. [documented]
6. **Invisible mode turns off Claude Code's gateway-compatibility fallbacks.** Claude Code believes it is talking to Anthropic, so it sends every first-party feature (tool search `defer_loading`/`tool_reference`, `context_management`, the advisor tool, new `anthropic-beta` values, server tools) to whatever answers. The retry-without-tool-search fallback (2.1.305) and the gateway caveats are tied to a custom base URL. hylo's request normalization is the only defense on the local lane. [inferred from documented changelog]
7. **Latest Claude Code is 2.1.325** (npm, 2026-11-13). **2.1.323 removed `subagentStatusLine`.** The `statusLine` stdin now includes `version`, `rate_limits.{five_hour,seven_day,spend_limit}` (since 2.1.80) and a rich `prompt_cache` object. [documented]
8. **The `anthropic-ratelimit-unified-*` headers are undocumented.** The community observes utilization as a 0-1 fraction, reset as Unix epoch seconds, a `representative-claim`, overage headers, and a model-scoped `7d_oi` window. Claude Code's documented `rate_limits` stdin is the stable interface. [community-observed / documented]
9. **Biggest policy risk (owner awareness, bears on D6).** The Claude Code legal page says third-party developers may not "collect, store, or **intermediate** Claude.ai credentials or session tokens", and the Usage Policy (effective 2026-11-12) bans services that "proxy … through unauthorized means, including services that route requests through consumer subscriptions". Anthropic also documents TLS-inspection proxies, and hylo is a user-run local proxy in front of the unmodified client, so the rule's application to hylo is ambiguous, not settled. [documented + inferred]
10. **Claude Code version churn regularly breaks tools like hylo:** new body fields and beta headers rejected by compatible servers, the `system` role inside `messages[]` (2.1.154), tool search on by default (2.1.304), the `\p{}` regex in a tool schema (2.1.265), the advisor-tool tag (2.1.275), `NO_PROXY` ignored (2.1.83-2.1.116). Pinning a tested range plus a fail-open passthrough is necessary. [documented / community-observed]

---

## 1. Landscape: tools that route Claude Code to local or alternative models

### 1.1 Base-URL gateways (`ANTHROPIC_BASE_URL`): all lose Remote Control

| Tool | Approach | Per-request lane switching | RC | Status line | Cost/usage | License | Latest (date) | Activity |
|---|---|---|---|---|---|---|---|---|
| **musistudio/claude-code-router** | Local gateway, base URL | Yes: v3 header/body conditions, rewrites, fallbacks. Older docs had `background`/`think`/`longContext`/`webSearch` keys | No | `ccr statusline` in older versions; current v3 support unclear | Request logs, routes, tokens, latency, estimated cost | MIT | v3.1.3 (2026-10-09) | ~38k stars, active |
| **LiteLLM proxy** | Base URL. Unified `/v1/messages` routes and translates; `/anthropic/v1/messages` is native passthrough | Yes on the unified endpoint (e.g. Haiku → Ollama, Sonnet → Anthropic) | No | none of its own | Spend logs, budgets; subscription traffic valued at list price | MIT (enterprise dir separate) | v1.109.1 (2026-11-12) | ~63k stars, very active |
| **1rgs/claude-code-proxy** | Base URL, LiteLLM translation | Haiku/Sonnet → small/big model; no documented mixed local+Anthropic mode | No | none | Logging only | **No license file found** | no GitHub release | ~3.8k stars, last push 2026-06 |
| **fuergaosi233/claude-code-proxy** | Base URL → one OpenAI-compatible upstream | Alias → small/middle/big; no Anthropic passthrough | No | none | none | MIT | no releases | ~2.8k stars, last commit 2026-03 |
| **luohy15/y-router** | Cloudflare Worker / Docker → OpenRouter or OpenAI-compatible | Model selection by env; no direct-Anthropic passthrough | No | none | none | MIT | none | **archived 2026-01-11** |

All rows [community-observed] (project READMEs, release pages), except the RC column, which follows from the documented 2.1.196 rule [documented].

### 1.2 Endpoint-preserving interceptors (`HTTPS_PROXY` + local CA): hylo's actual peer group

| Tool | Approach | Lane switching | RC | Status line / usage | License | Latest | Notes |
|---|---|---|---|---|---|---|---|
| **cablate/model-relay** | Base URL by default; `/provider rc on` switches to HTTPS-proxy mode with local CA via `NODE_EXTRA_CA_CERTS` | Yes: model aliases (incl. Haiku/background) to other providers; per-window pinning; 429 failover chain. Backends must speak Anthropic Messages | **Project says yes** in proxy mode: "token refresh and Remote Control traffic included, passes to Anthropic unchanged" | Per-session relay-state file, optional status bar plugin; request logs, no spend accounting | MIT | v0.7.5 (2026-10-24) | **Closest to hylo.** Warns that `HTTPS_PROXY` in settings `env` also applies to `git`/`curl`/`gh` (blind tunnels, which fail if the router is down) |
| **KarpelesLab/teamclaude** | MITM by default (real HTTP/2 server on the intercepted host, HTTP/1.1 also handled); optional base URL | Account rotation and quota failover; not a local-model router | Yes: lists the RC paths it passes through with the client's own credential; Desktop may need `mitm.http1Only` | `/teamclaude/quota` endpoint for status lines | MIT | v1.1.29 (2026-11-10) | Account rotation is the kind of use the Usage Policy targets; **do not copy that pattern** |
| **peter-wagstaff/claude-hybrid-router** | `HTTPS_PROXY` + local CA | A marker in a subagent's system prompt sends it to Ollama/OpenAI-compatible; otherwise Anthropic | Not verified | none | MIT | no releases | 3 stars; marker-based rather than model-prefix |
| **Screddyice/backdoor** | Base URL or `HTTPS_PROXY` interception | Explicit local routes; opt-in cloud→Ollama failover on transport outage | Project says yes in forward-proxy mode | Transcript-based "savings" report | MIT | none | 0 stars |
| **aeroxy/claude-proxy** (Rust) | Base URL or MITM | Provider-prefixed models → Gemini; Claude passes through | Not verified | none | MIT | v1.6.0 (2026-11-12) | Cloud alternatives, not local |
| **CLIProxyAPI + community mitmproxy sidecar** | Separate mitmproxy addon in front of the base-URL gateway | Model name selects the reroute | **User-reported working** (`/rc` + mobile); maintainers closed in-core MITM as "not planned" | Built-in usage stats removed in v6.10.0 | MIT (core) | v8.0.69 (2026-11-12) | issue #7111 |

All rows [community-observed]. RC claims are project self-reports, not independently verified.

### 1.3 Differentiation and verdict

- **Is anyone doing invisible per-request hybrid routing?** **Yes**: model-relay (proxy mode), claude-hybrid-router, backdoor and the CLIProxyAPI sidecar all do per-request routing behind an unchanged `api.anthropic.com`. hylo should not claim to be first. [community-observed]
- **What no surveyed tool combines** [inferred]:
  - a single static Go binary for macOS, Linux and Windows with per-OS service units (D5, D12);
  - an append-only **JSONL ledger** that records Anthropic plan-limit headers (`anth_ratelimit`) as well as per-lane usage, plus a **Prometheus exporter** for existing Grafana boards (D7);
  - a **lane-aware status line**: lane pill, served-model honesty, per-lane dynamic cost percentiles, owned-hardware `⛏` cost, backend GPU telemetry;
  - a **parity-tested** port of a prototype in daily use, with explained thresholds;
  - a **Stop hook** for "fake stops" by local models.
- **Peers to study before P3** [inferred]: model-relay (RC path handling, child-process `HTTPS_PROXY` side effects) and teamclaude's `docs/proxy-modes.md` (HTTP/2 MITM server, RC path list, refusing to proxy through itself).

---

## 2. Claude Code configuration surfaces relevant to hylo

**Current version:** npm `@anthropic-ai/claude-code@2.1.325` (`engines.node >=22`; the `claude` binary is a native executable with per-platform optional packages). [documented: npm registry] The 2.1.3xx line began with 2.1.300 on 2026-10-14. [documented: GitHub releases]

### 2.1 Environment and flags

| Surface | Facts | Tag |
|---|---|---|
| `ANTHROPIC_BASE_URL` | Changes the endpoint, not the model. Any non-`api.anthropic.com` host disables RC (2.1.196+). Anthropic "does not support routing Claude Code to non-Claude models through any gateway" | [documented] |
| Model aliases | `ANTHROPIC_MODEL`; `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU}_MODEL` (Haiku also = background model; Sonnet/Opus also drive `opusplan` phases); `ANTHROPIC_SMALL_FAST_MODEL` deprecated; `CLAUDE_CODE_SUBAGENT_MODEL` (+ `_FORCE`) | [documented] |
| Credentials | `ANTHROPIC_AUTH_TOKEN` (Bearer) and `ANTHROPIC_API_KEY` (`x-api-key`) override the subscription login **and disable RC** (since 2.1.139) | [documented] / [community-observed #59062] |
| `HTTPS_PROXY` / `HTTP_PROXY` / `NO_PROXY` | Upper- and lower-case supported. Precedence `https_proxy`, `HTTPS_PROXY`, `http_proxy`, `HTTP_PROXY`. `NO_PROXY` takes comma/space lists and `*`. **SOCKS not supported** | [documented] |
| `NODE_EXTRA_CA_CERTS` | Documented for the native install as well. `CLAUDE_CODE_CERT_STORE=bundled,system` (default) also reads the OS store (npm installs need Node ≥22.15) | [documented] |
| mTLS | `CLAUDE_CODE_CLIENT_CERT`, `_KEY`, `_KEY_PASSPHRASE` | [documented] |
| Paths that ignored the CA | MCP OAuth initiation ignored `NODE_EXTRA_CA_CERTS` until 2.1.133; the voice-dictation WebSocket failed with a corporate CA (2026-10) | [community-observed #55760, #102747] |
| `--settings <file-or-json>` | File (≤2 MiB) or inline JSON; per session; above user/project/local settings, below managed; omitted keys keep file values | [documented] |
| RC kill switches | `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` and `CLAUDE_CODE_DISABLE_FEATURE_FLAGS` make RC unavailable | [documented] |
| Beta/tool-search switches | `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`, `ENABLE_TOOL_SEARCH=0/false` | [documented / community-observed] |

### 2.2 `statusLine` contract

[documented: code.claude.com/docs/en/statusline]

- **Config:** `{"type":"command","command":…,"padding":N,"refreshInterval":S,"hideVimModeIndicator":bool}`. `refreshInterval` is in seconds, minimum 1; unset means event-driven only. `padding` (default 0) adds to the built-in spacing.
- **Triggers:**
  - session start/resume, new assistant message, `/compact` done, permission-mode change, vim toggle;
  - `command` change (runs immediately);
  - refresh timer;
  - **a rate-limit window reaching `resets_at`**, and **a warm prompt cache reaching `expires_at`**.
  - Debounced 300 ms; a new run cancels the one in flight.
- **Output rules:** shown only on **exit 0** with stdout; nonzero exit or empty output leaves the line blank. Multiple lines become multiple rows. ANSI colors and OSC 8 links work. `COLUMNS`/`LINES` are passed in the environment.
- **Requirements:** workspace trust is required; managed-hook policy can block non-managed commands.
- **Stdin fields** (the ones hylo uses are in bold):
  - session: **`session_id`**, `session_name`, `prompt_id`, **`transcript_path`**, **`version`**, **`model.{id,display_name}`**, `cwd`, **`workspace.{current_dir,project_dir}`**, `added_dirs`, `git_worktree`, `repo.{host,owner,name}`;
  - cost: **`cost.{total_cost_usd,total_duration_ms,total_api_duration_ms,total_lines_added,total_lines_removed}`**;
  - context: **`context_window.{context_window_size,used_percentage,remaining_percentage,total_input_tokens,total_output_tokens,current_usage.{input,output,cache_creation_input,cache_read_input}_tokens}`**, `exceeds_200k_tokens`;
  - modes: `fast_mode`, `effort.level`, `thinking.enabled`;
  - limits: **`rate_limits.{five_hour,seven_day}.{used_percentage,resets_at}`** (epoch **seconds**), `rate_limits.spend_limit.{used_percentage,resets_at,used_usd,limit_usd,period}`;
  - cache: **`prompt_cache.{warm,caching_observed,ttl,expires_at,requests,misses,expected_rebuilds,hit_ratio,cache_write_tokens,miss_recache_tokens,last_miss_at,last_miss_cause,miss_causes,recache_tokens_if_cold}`**;
  - other: `vim.mode`, `agent.name`, `pr.*`, `worktree.*`.
- **Conditionality:**
  - `rate_limits` appears only for Pro/Max/Ultra (or a gateway with a spend limit), after the first response. Each window can be absent on its own and is dropped after its reset. Added in **2.1.80**; spend-limit fields 2.1.251/2.1.284.
  - `used_percentage` = input + cache_creation + cache_read, output excluded.
  - `current_usage` is null before the first call and right after compaction.
- **`subagentStatusLine`:** existed by 2.1.105 at the latest (first version not confirmed); payload extended in 2.1.214 (effort) and 2.1.293 (`agentType`); **removed in 2.1.323** (old settings still load, but the command is ignored). Issue #109446 asks for it back. Consistent with PLAN.md §3. [documented]

### 2.3 Stop hook contract

[documented: code.claude.com/docs/en/hooks]

- **When it fires:** when the main agent finishes responding; not on user interrupt. API errors fire `StopFailure` instead.
- **Input:** `session_id`, `transcript_path` (written asynchronously, may lag), `cwd`, `permission_mode`, `hook_event_name:"Stop"`, `prompt_id`, `scratchpad_dir`, `effort`, **`stop_hook_active`**, **`last_assistant_message`** (preferred over reading the possibly lagging transcript), `background_tasks`, `session_crons`.
- **Output:**
  - `{"decision":"block","reason":"…"}` keeps Claude working and gives it the reason; omit `decision` to allow the stop.
  - `{"continue":false,"stopReason":…}` halts everything (it does **not** mean "keep working").
  - `hookSpecificOutput.additionalContext` adds non-error feedback.
  - Print JSON and exit 0; exit 2 also blocks, using stderr as the reason.
  - **Loop cap:** at most eight consecutive continuations, reset by a tool call.

### 2.4 What Remote Control requires, and why a base URL breaks it

- **Requirements** [documented]:
  - an eligible claude.ai login (Pro/Max/Ultra/Team/Enterprise) through `/login`;
  - no API key or `CLAUDE_CODE_OAUTH_TOKEN` (setup-token lacks the full scope);
  - the endpoint is `api.anthropic.com`: not Bedrock/Vertex/Foundry, not a custom `ANTHROPIC_BASE_URL`, not an enterprise apps gateway;
  - org policy enabled; not ZDR or HIPAA.
- **The cause is a deliberate client-side check, not a protocol limit** [documented]: the error names the variable responsible ("Remote Control is only available when using Claude via api.anthropic.com"). Issue #76653 asked for a localhost exception; none has been granted. [community-observed]
- **Bridge traffic goes through the proxy** [community-observed: teamclaude]: since 2.1.287 the RC bridge (`/v1/environments/`, `/v1/sessions/`, `/v2/session_ingress/`, `/v2/ccr-sessions/`, `/v1/code/`) is sent through `HTTPS_PROXY`. These requests are bound to the paired identity and fail if credentials are altered. PLAN.md §9 mentions a "WebSocket bridge"; whether these paths use WebSocket upgrades, long-poll or SSE was **not confirmed** in this research. **Inconclusive.**

---

## 3. Anthropic Messages API facts the proxy and status line depend on

### 3.1 SSE event sequence

[documented: platform.claude.com/docs/en/build-with-claude/streaming]

- **Order:** `message_start` (message with empty `content`; initial `message.usage`), then per block `content_block_start`, `content_block_delta`×N, `content_block_stop`, then one or more `message_delta` (`stop_reason`, `usage`), then `message_stop`.
  - `ping` can appear anywhere. `error` events can appear mid-stream (e.g. `overloaded_error`, which would be HTTP 529 outside a stream).
  - **Unknown event types must be tolerated.**
- **Delta types:** `text_delta`, `input_json_delta` (`partial_json`; concatenate and parse at stop), `thinking_delta` (may be empty when display is omitted), `signature_delta` (sent just before the thinking block's stop). Server-tool result blocks arrive whole, with no deltas.
- **Usage semantics:** `message_delta.usage` counts are **cumulative**. A delta may carry only `output_tokens`, or also `input_tokens`, cache counts and `server_tool_use` (server-tool cases update input too). **Merge the fields that are present; never sum snapshots; never treat an absent field as zero.** [documented] This is exactly what the prototype's SSE usage tap must keep doing (parity item).

### 3.2 Usage object

[documented]

- `input_tokens`: uncached input after the last breakpoint.
- `output_tokens`: inclusive of `output_tokens_details.thinking_tokens`.
- `cache_creation_input_tokens`, `cache_read_input_tokens`.
- `cache_creation.{ephemeral_5m_input_tokens,ephemeral_1h_input_tokens}`: a breakdown of `cache_creation_input_tokens`, **not** additional tokens.
- Also: `server_tool_use.{web_search_requests,web_fetch_requests}`, `service_tier` (`standard|priority|batch|null`), `inference_geo`, `speed` (`standard|fast`).
- **Total input** = `input + cache_creation + cache_read`. This matches the status line's ↑ = in + ✍ + ⟳.

### 3.3 Rate-limit headers

- **Documented (API key):** `anthropic-ratelimit-{requests,tokens,input-tokens,output-tokens}-{limit,remaining,reset}`; `anthropic-priority-{input,output}-tokens-*`; `anthropic-fast-{input,output}-tokens-*`; `retry-after` (not on every 429, never on spend-cap 429s).
  - `reset` values are RFC 3339; token `remaining` is rounded to the thousand.
  - Input-token limits count uncached input + cache writes, not reads.
  - [documented: platform.claude.com/docs/en/api/rate-limits]
- **Undocumented subscription headers**, prefix `anthropic-ratelimit-unified-` [community-observed: claude-code #12829, #20636, #77846; CLIProxyAPI `claude_ratelimit.go`; mtrojnar/pi-usage; ArkNill analysis]:

| Suffix | Observed meaning |
|---|---|
| `status` | `allowed` / `allowed_warning` / `rejected` |
| `5h-utilization`, `7d-utilization` | **fraction 0-1** (e.g. `0.34` = 34%) |
| `5h-reset`, `7d-reset`, `reset` | Unix epoch **seconds** |
| `5h-status`, `7d-status` | per-window status |
| `5h-surpassed-threshold`, `7d-surpassed-threshold` | threshold signal |
| `representative-claim` | `five_hour` / `seven_day`: which window binds |
| `fallback`, `fallback-percentage` | observed values 0.2, 0.5; **semantics unknown** |
| `overage-status`, `-utilization`, `-reset`, `-disabled-reason` | extra-usage state (e.g. `org_level_disabled`) |
| `7d_oi-utilization`, `-reset`, `-status` | an additional **model-scoped** 7-day window |

- **Implication** [inferred]: the owner's observation that only `7d-*` arrives for one account fits the community reports that headers vary by account and plan. The status line should keep reading Claude Code's documented `rate_limits` stdin and use the ledger `anth_ratelimit` capture only for diagnostics and metrics. The exporter (P2) should tolerate new suffixes such as `7d_oi` without crashing.

### 3.4 Prompt caching

[documented: prompt-caching and pricing pages]

- **TTLs:** 5 min (default) and 1 h (`ttl:"1h"`). Writes cost **1.25×** and **2×** base input respectively.
- **Reads/refreshes are not universally 0.1×:**
  - Opus 5.5 and Sonnet 5.5: 0.05×
  - Fable/Mythos 5.2: 0.025×
  - all other models: 0.1×
- A hit refreshes the TTL at no extra charge (the read is still billed). The lifetime runs from the **start** of the request. Longer TTL breakpoints must precede shorter ones.

### 3.5 List prices (USD per MTok, standard tier, verified 2026-11-14 on the pricing page)

[documented]

| Model | Input | Output | 5m write | 1h write | Cache read |
|---|---:|---:|---:|---:|---:|
| Opus 5.5 (`claude-opus-5-5`) | 4.00 | 20.00 | 5.00 | 8.00 | 0.20 |
| Sonnet 5.5 (`claude-sonnet-5-5`) | 2.00 | 10.00 | 2.50 | 4.00 | 0.10 |
| Haiku 5.5, prompt ≤100K | 0.10 | 0.50 | 0.125 | 0.20 | 0.01 |
| Haiku 5.5, prompt >100K | 0.50 | 2.50 | 0.625 | 1.00 | 0.05 |
| Fable 5.2 / Mythos 5.2 | 8.00 | 40.00 | 10.00 | 16.00 | 0.20 |

- Opus/Sonnet 5.5 have 1M context at standard prices (no long-context premium). The Haiku 5.5 >100K threshold counts cache reads and writes.
- Batch is 50% off. Fast mode, data residency and server tools are priced separately.
- **The status line doc's figures ($4 / $8 1h-write / $0.20 / $20 for Opus 5.5) match.** [documented]

---

## 4. Risks

### 4.1 Terms and policy: proxying a subscription session and mixing in non-Anthropic models

| Source | Text (verbatim where quoted) | Tag |
|---|---|---|
| Claude Code legal page | "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, Max, or Ultra plan credentials on behalf of their users. Moreover, developers may not collect, store, or **intermediate** Claude.ai credentials or session tokens — sign-in to a Claude account must complete through Anthropic's own flow." | [documented, extracted 2026-11-14] |
| Same page | "Advertised usage limits for Pro, Max, and Ultra plans assume ordinary, individual usage of Claude Code" | [documented] |
| Usage Policy (effective 2026-11-12) | Prohibits: "Resell, proxy, or otherwise provide access to Claude through unauthorized means, including services that route requests through consumer subscriptions or misrepresent the product or client being used"; and "Intentionally bypass or interfere with capabilities, restrictions, or guardrails … without prior authorization" | [documented, extracted 2026-11-14] |
| Consumer Terms (eff. 2025-10-08) | §3.7: no automated access except via API key or where Anthropic explicitly permits; §3: no reverse engineering or bypassing protective measures | [documented via secondary sources] |
| Gateway / network docs | Anthropic itself documents TLS-inspection proxies with custom CAs, and gateways that forward the signed-in user's OAuth `Authorization` | [documented] |
| Gateway docs | "doesn't support routing Claude Code to non-Claude models through any gateway" ("unsupported", which is not the same as "prohibited") | [documented] |
| Enforcement history | 2026-01-09: subscription OAuth tokens used by OpenCode/Clawdbot were rejected (harness-spoofing safeguards). 2026-02-19/20: legal page clarified; OpenCode removed its Anthropic OAuth plugin. 2026-04-04: OpenClaw usage moved to extra-usage billing; partly paused 2026-06-15 | [community-observed: press, GitHub] |

**Assessment** [inferred, not legal advice]:

- **Lower-risk facts about hylo:** the user runs the **genuine, unmodified Claude Code client** with their own login. hylo does not obtain, store or reuse the token for its own requests, does not misrepresent the client to Anthropic, passes Anthropic-bound requests **untouched**, and runs locally for one user. The enforcement so far has targeted **separate harnesses reusing the token** and **resale/rotation services**, not local proxies in front of Claude Code.
- **Higher-risk facts about hylo:** TLS termination means hylo **does intermediate** the session token in a literal sense. hylo is a distributed developer tool, not the user's own corporate proxy. "Proxy … through unauthorized means" is broad. Sending some turns of a subscription session to a non-Claude model is explicitly "unsupported".
- **Risk for owner awareness (D6):** invisible mode is the design point most exposed to a stricter reading. The worst plausible outcome is account-level action against *users*, without notice. Mitigations hylo can adopt without reopening D6:
  1. never log, persist or forward the `Authorization` header or OAuth tokens (redact them in the ledger and debug output, and test for it);
  2. never send Anthropic credentials to a local backend (already rewritten; make it a test);
  3. no modification of Anthropic-bound requests or headers, and no account pooling or rotation;
  4. a README "use at your own risk / check Anthropic's terms" notice, plus an API-key profile as a documented alternative (RC is lost with an API key);
  5. consider asking Anthropic for written clarification.

### 4.2 Trademark and brand

- **Product names:** the Claude Code legal page says Claude Code/Anthropic names and logos cannot be part of a developer's product, feature, company name or logo. Accurate plain-text descriptive statements are allowed. The general trademark guidelines (eff. 2024-08-01) require permission for any implied endorsement. [documented]
- **Disclaimers:** a "not affiliated" disclaimer helps but does not cure a bad name or logo. [documented]
- **Precedents:** Clawdbot → Moltbot → OpenClaw after an Anthropic trademark request (2026-01-27/30) [community-observed: press]. The Claude Code SDK became the Claude Agent SDK (2025-09-29); the stated reason was scope, not trademark. [documented]
- **hylo's position** [inferred]: the name contains no "Claude", and the README already says "for Claude Code … Not affiliated with Anthropic. 'Claude' is a trademark of Anthropic." That is the conservative pattern. Remaining caution: do not use Anthropic or Claude Code visual styling or logos in the status line, docs or release assets; keep binary, service and LaunchAgent names `hylo`/`io.hylo.*`; consider "independent tool for Claude Code" wording.
- **Served-model honesty** [inferred]: serving a non-Claude model under a `claude-sonnet-*` alias makes Claude Code display "Sonnet 5.5". The status line review already flags this. Showing the real served model on the local lane (backlog #29) also lowers misrepresentation risk.

### 4.3 How Claude Code churn has broken similar tools (selected)

| Date | Version | Breakage | Tag |
|---|---|---|---|
| 2026-01-21 | 2.1.8-2.1.14 | `context_window.current_usage` reported zeros in status line stdin | [community-observed #19724] |
| 2026-01-28 | — | Ollama 404 on `count_tokens?beta=true`, followed by hangs | [community-observed ollama#13949] |
| 2026-01-29 | 2.1.22 | `context_management` body field → 400 "Extra inputs are not permitted" on gateways | [community-observed #21612] |
| 2026-02-13 | — | New `anthropic-beta` values → "invalid beta flag" (LiteLLM incident) | [community-observed] |
| 2026-03-27 | 2.1.83 → fixed 2.1.117 | `NO_PROXY` ignored; streaming 502s through the forward proxy | [community-observed #39862] |
| 2026-05-29 | 2.1.154+ | `system` role inside `messages[]` rejected by older vLLM Anthropic validation | [community-observed vllm#44000] |
| 2026-06-29 | 2.1.196 | RC disabled with a non-Anthropic base URL (intentional) | [documented] |
| 2026-07-15 | — | vLLM template failures replaying `tool_reference` blocks | [community-observed #77928] |
| 2026-08-05 | 2.1.221 | Streaming `ECONNRESET` (transport change plus a Windows LSP conflict) | [community-observed #84194] |
| 2026-09-09 | 2.1.265-266 | Tool schema regex with `\p{…}` → 400 on strict validators; fixed 2.1.268 | [community-observed #92964] |
| 2026-09-18 | 2.1.275 | `advisor_20260301` tool tag broke every request behind affected proxies; fixed 2.1.276 | [documented] |
| 2026-10-09 | ~2.1.280 | Subagent transcripts missing final usage (transcript-based token counters undercount); fixed 2.1.307 | [community-observed #100830 / documented] |
| 2026-10-19/20 | 2.1.304/305 | Tool search on by default behind custom base URLs; retry without it on rejection | [documented] |
| 2026-11-12 | 2.1.323 | `subagentStatusLine` removed | [documented] |

**Key inference for hylo:** the fixes in 2.1.304/305 are scoped to **custom base URLs**. In invisible mode Claude Code sees `api.anthropic.com`, so it will **always** send the Anthropic-first-party feature set. A local backend that rejects a new field produces a 400 that Claude Code may not retry around. hylo's normalizer must therefore (a) strip or translate unknown fields for the local lane, (b) filter `anthropic-beta` values to an allow-list per backend, and (c) log unknown fields and betas to the ledger so new ones surface quickly. [inferred]

**On certificate pinning** [community-observed / documented]: no evidence that Claude Code pins certificates for `api.anthropic.com`; a desktop report that suspected pinning was retracted. The native (Bun) build honors `NODE_EXTRA_CA_CERTS` for normal API traffic.

---

## 5. OpenAI-compatible backends: Anthropic ↔ Chat Completions translation (P6)

### 5.1 Do we even need it?

Native `/v1/messages` support as of 2026-11-14 [documented unless noted]:

| Server | Since | Latest | Streaming + tools | Thinking | Images | Cache usage reporting | `count_tokens` |
|---|---|---|---|---|---|---|---|
| vLLM | 0.11.1 (2025-11-18) | 0.33.0 (2026-11-02) | yes (needs tool parser + `--enable-auto-tool-choice`) | yes (parser) | base64 + URL | cache read/creation with `--enable-prompt-tokens-details` | yes |
| SGLang | 0.5.9 (2026-02-24) | 0.5.23 (2026-11-02) | yes (`--tool-call-parser`) | yes; `budget_tokens` not enforced | base64 + URL | `cache_read_input_tokens` with `--enable-cache-report` | yes |
| llama.cpp `llama-server` | b7187 (2025-11-28) | 1.0.0 (2026-11-13) | yes (Jinja template) | yes; signatures empty | multimodal models | `cache_read_input_tokens`; **subtracts cached from input** (Anthropic semantics) | yes |
| Ollama | 0.14.0 (2026-01-10) | 0.40.16 (2026-11-09) | yes | yes; budget not enforced | base64 only (no URL) | docs say no; **0.40.3 observed `cache_read_input_tokens`** (conflict) | **no** |
| LM Studio | 0.4.1 (2026-01-30) | 0.4.28 (2026-10-31) | yes | observed | tool-result images from 0.4.22 | observed; **bug report: `input_tokens` includes cached → double count** [community-observed lmstudio-bug-tracker#2535] | not documented |

**Conclusion** [inferred]: for P6, "Anthropic-compatible backend" covers all five planned servers. Translation to Chat Completions matters only for genuinely OpenAI-only endpoints (older versions, hosted OpenAI-compatible APIs, some proxies). Two things are required regardless:

- **Per-backend usage normalization:** LM Studio's input double-count, llama.cpp's subtraction, and Ollama's undocumented cache fields would all distort the ledger and the `♻`/`↑` widgets.
- **A `count_tokens` strategy for backends without the endpoint:** route it to Anthropic? estimate locally? return 404? The CC Switch report (#5376) shows a missing route can turn into many tiny billable requests. Owner decision.

### 5.2 What translation requires (if built)

[documented: OpenAI and Anthropic API references; community-observed pitfalls]

- **Requests:**
  - `system` (string or blocks) → `role:"system"` message(s); drop `cache_control`.
  - Tools: `input_schema` → `function.parameters` (as an object, not a string).
  - `tool_use{id,name,input}` ↔ `tool_calls[{id,function{name,arguments:<JSON string>}}]`; `tool_result{tool_use_id,content,is_error}` → `role:"tool"` messages (`is_error` has no equivalent).
  - `tool_choice` `auto|any|none|{tool}` → `auto|required|none|{function}`; `disable_parallel_tool_use` → `parallel_tool_calls:false`.
  - Base64 images → `data:` URIs.
  - Thinking → provider `reasoning_content` (lossy; **never fabricate signatures**).
- **Stop reasons:** `tool_calls`→`tool_use`, `length`→`max_tokens`, `stop`→`end_turn` (stop-sequence identity lost), `content_filter`→`refusal` (a policy mapping).
- **Streaming:** synthesize `message_start`; keep per-`tool_calls[].index` state; open a `tool_use` block once id and name are known; emit `input_json_delta` per fragment; **never mix fragments across indexes**; close blocks; `message_delta` + `message_stop`. Request `stream_options.include_usage` and wait for the final `choices:[]` usage chunk, but do not treat usage as end-of-stream (some servers send it on every chunk).
- **Usage:** `cache_read = prompt_tokens_details.cached_tokens`; `input = prompt_tokens − cached`; `output = completion_tokens`; never invent cache writes.
- **Known pitfalls** [community-observed]:
  - parallel calls merged into one block with invalid JSON (LiteLLM #44029);
  - per-chunk usage closing tool blocks early (CLIProxyAPI #5419);
  - dropped closing braces;
  - duplicate `call_0` ids collapsing results;
  - double-subtracted cache tokens;
  - local models that simply cannot run a multi-turn tool loop.

### 5.3 Existing libraries (license compatibility with Apache-2.0 noted)

| Library | Lang | Direction | License | Version | Fit for hylo |
|---|---|---|---|---|---|
| `github.com/elkpi/oxa-protocol/go/v3` | Go | Bidirectional via an IR, streaming, records fidelity loss | Apache-2.0 | v3.3.0 | **Best library candidate**, in-process; needs a vetting review |
| `github.com/maximhq/bifrost` | Go | Anthropic SDK in → OpenAI/Ollama out | Apache-2.0 | transports v2.5.1 | Full gateway; too heavy as a dependency; good reference |
| `router-for-me/CLIProxyAPI` | Go | Claude clients → OpenAI-compatible upstreams | MIT | v8.0.69 | Reference implementation (stream state machine, `claude_ratelimit.go`) |
| `hy-shine/claude-proxy-go` | Go | Anthropic → OpenAI upstream | MIT | v0.2.0 | Converters are `internal/`; reference only |
| `kyungw00k/anthropic-openai-proxy-go` | Go | Anthropic → OpenAI | README says MIT; pkg.go.dev detects none | pseudo-version 2026-09 | Verify license first |
| `lrbmike/omniai-go`, `LingByte/ling-base/relayconvert` | Go | both | MIT | v0.0.1 / v0.1.0 | Immature |
| `QuantumNous/new-api` | Go | multi | **AGPL-3.0** | v1.0.0-rc.51 | **Avoid** (license) |
| LiteLLM | Python | multi | MIT | v1.109.1 | Behavioral reference |
| claude-code-router transformers | TS | multi | MIT | v3.1.3 | Behavioral reference |

[community-observed: pkg.go.dev, GitHub releases; versions not re-verified individually against each registry beyond the research tool's retrieval]

Given "standard library first", a small hand-written translator (roughly the size of one SSE state machine) informed by oxa-protocol and CLIProxyAPI is likely preferable to a dependency. That is a judgment call for the owner. [inferred]

---

## Implications for hylo (mapped to phases)

**P1: `hylo statusline`**
- Parse stdin defensively: every object is optional; `rate_limits` windows can be absent on their own; `current_usage` is null after compaction; `used_percentage` can be null. [documented]
- Do **not** port a `--subagent` mode (removed in 2.1.323; consistent with PLAN §3).
- Read stdin `version`. A golden test should cover stdin with and without `prompt_cache` and `rate_limits.spend_limit` (additive fields must not break parity output).
- Claude Code reruns the line on `resets_at` and `expires_at` events. The prototype's 30-minute smoothing and the "drop window past resets_at" rule keep working; no change needed (parity first).
- Cost basis: keep using `cost.total_cost_usd` for `$`. If hylo ever reprices transcripts (`cost backfill`), use the per-model cache-read multipliers (0.05× for Opus/Sonnet 5.5, not 0.1×) and the Haiku 5.5 100K tier.

**P2: `hylo exporter`**
- Tolerate unknown `anthropic-ratelimit-unified-*` suffixes (`7d_oi-*`, `overage-*`, `fallback-percentage`) without failing. Metric names stay unchanged (D7); new suffixes wait for P7.

**P3: `hylo proxy` (highest-risk phase)**
- **RC passthrough allow-list**, byte-for-byte with the client's own credential: `/v1/oauth/token`, `/v1/code/`, `/v1/environments/`, `/v1/sessions/`, `/v2/session_ingress/`, `/v2/ccr-sessions/`, `/api/oauth/files/`, `/api/oauth/file_upload`, `/v1/mcp_servers`. Better: route **only** `/v1/messages` and `/v1/messages/count_tokens` for local-prefixed models and pass **everything else** through untouched. Add replay tests for each path. [community-observed teamclaude]
- **HTTP/2 + HTTP/1.1 on the intercepted listener:** Go `net/http` serves h2 with a `tls.Config.GetCertificate` per-host leaf when ALPN negotiates `h2` [community-observed via perplexity_ask; single source]. teamclaude reports Desktop needing an HTTP/1.1-only fallback, so make ALPN configurable.
- **Blind-tunnel every non-intercepted host** (CONNECT without TLS termination). Commands Claude Code runs inherit `HTTPS_PROXY` and fail if the proxy is down (model-relay warning). Document `NO_PROXY` and consider failing open.
- **Never proxy through yourself:** drop an upstream `HTTPS_PROXY` that points at hylo's own listener (teamclaude pattern).
- **Normalizer for the local lane:** an allow-list of `anthropic-beta` values per backend; strip or translate unknown top-level body fields (`context_management`, tool search `defer_loading`/`tool_reference`, advisor tools); handle the `system` role in `messages[]`; ledger-log anything stripped. **Server-tool requests must go to Anthropic** (the prototype already does this).
- **SSE tap:** merge cumulative usage fields; tolerate unknown event types and mid-stream `error` events.
- **Security tests:** `Authorization`/`x-api-key`/OAuth values never appear in the ledger, logs or local-backend requests.

**P4: `hylo run`, `hook stop`, `doctor`, `ca`**
- `hylo run` must **not** set `ANTHROPIC_BASE_URL`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` or `CLAUDE_CODE_DISABLE_FEATURE_FLAGS` (each kills RC). `hylo doctor` should check for them in the environment and in settings `env`.
- `hylo doctor` should report the Claude Code version (stdin `version` or `claude --version`) against the tested range, and warn on SOCKS proxies (unsupported).
- Stop hook: prefer `last_assistant_message` over transcript reads (the transcript lags); respect `stop_hook_active` and the 8-continuation cap.
- CA: `NODE_EXTRA_CA_CERTS` works for the native build too. Known exceptions are MCP OAuth (fixed 2.1.133) and the voice WebSocket; document them.

**P5: cutover**
- Pin and document the tested Claude Code range. The 2.1.32x line already removed one feature hylo used; review the changelog per release as a cutover checklist item.

**P6: generalize**
- Reorder: **Anthropic-native backends first** (all five servers qualify). OpenAI translation becomes an optional adapter.
- Add per-backend **usage normalizers** (LM Studio input double-count, llama.cpp subtraction, Ollama's undocumented cache fields) and a **`count_tokens` policy** per backend.
- Per-backend minimum versions: vLLM ≥0.11.1, SGLang ≥0.5.9, llama.cpp ≥b7187, Ollama ≥0.14.0, LM Studio ≥0.4.1.
- If translation is built: hand-written, informed by oxa-protocol (Apache-2.0) and CLIProxyAPI (MIT); avoid AGPL code.

**P7: redesign**
- The ledger could add `cache_creation.ephemeral_{5m,1h}`, `service_tier`, `speed`, `inference_geo`, `thinking_tokens`, the unified `7d_oi`/overage headers, and fields stripped by the normalizer.

**Cross-cutting**
- Public README: add a short "Terms and risk" section (user-run, unmodified client, no token storage, check Anthropic's terms) and an "Alternatives" section naming model-relay and claude-code-router.

---

## Open questions for the owner

1. **Policy posture:** should hylo ask Anthropic for written clarification of "intermediate … session tokens" as it applies to a user-run local proxy, and/or ship an API-key profile (no RC) as the documented "conservative" mode?
2. **`count_tokens` on the local lane:** route to the backend when supported, to Anthropic otherwise, or estimate locally?
3. **Unknown fields and betas on the local lane:** strip silently, strip and ledger-log, or fail the request loudly? (This decides how visible Claude Code churn is.)
4. **RC traffic transport:** do you have a capture showing whether the bridge paths use WebSocket upgrades (PLAN §9 says "WebSocket bridge")? This research could not confirm it.
5. **P6 scope:** given native `/v1/messages` everywhere, drop OpenAI translation from the P6 exit criterion (Ollama via `/v1/messages` would satisfy "works end to end with only config")?
6. **Peers:** acknowledge model-relay and others in the README (an honest landscape), or stay silent?
7. **Served-model display:** prioritize backlog #29 (show the real local model) earlier, as a misrepresentation-risk reducer?

---

## Sources (accessed 2026-11-13/14)

**Anthropic / Claude Code (official)**
- https://code.claude.com/docs/en/remote-control (Remote Control requirements and error causes; extracted)
- https://code.claude.com/docs/en/legal-and-compliance (credential use, "intermediate" clause; extracted)
- https://code.claude.com/docs/en/statusline (statusLine contract and stdin fields; extracted)
- https://code.claude.com/docs/en/hooks (Stop hook input/output)
- https://code.claude.com/docs/en/network-config (proxy, CA, mTLS env vars)
- https://code.claude.com/docs/en/env-vars (model and auth env vars)
- https://code.claude.com/docs/en/model-config (alias env vars)
- https://code.claude.com/docs/en/llm-gateway, https://code.claude.com/docs/en/llm-gateway-protocol (gateway requirements; "non-Claude models not supported")
- https://code.claude.com/docs/en/cli-reference (`--settings`)
- https://github.com/anthropics/claude-code/releases (2.1.80, 2.1.196, 2.1.214, 2.1.276, 2.1.293, 2.1.304, 2.1.305, 2.1.307, 2.1.323, 2.1.325)
- https://registry.npmjs.org/@anthropic-ai/claude-code/latest (2.1.325; extracted)
- https://platform.claude.com/docs/en/build-with-claude/streaming (SSE events)
- https://platform.claude.com/docs/en/api/messages (usage object)
- https://platform.claude.com/docs/en/api/rate-limits (documented headers)
- https://platform.claude.com/docs/en/build-with-claude/prompt-caching (TTLs)
- https://platform.claude.com/docs/en/about-claude/pricing (list prices, cache multipliers; extracted)
- https://www.anthropic.com/legal/aup (Usage Policy, eff. 2026-11-12; extracted)
- https://www.anthropic.com/legal/consumer-terms (Consumer Terms, eff. 2025-10-08)

**Claude Code issues**
- https://github.com/anthropics/claude-code/issues/72382 (RC + base URL), /76653 (localhost exception request), /72749, /59062 (API key disables RC)
- /109446 (subagentStatusLine removal), /19724 (status line usage zeros), /21612 (context_management), /22893, /31936, /77928, /104309 (tool search), /39862 (NO_PROXY), /55760 (MCP OAuth CA), /102747 (voice WebSocket CA), /84194 (ECONNRESET), /92964 (`\p{}` regex), /100830 (subagent usage)
- /12829, /20636, /77846 (unified rate-limit headers)

**Landscape**
- https://github.com/musistudio/claude-code-router (v3.1.3)
- https://docs.litellm.ai/docs/proxy/client_setup/claude_code, https://github.com/BerriAI/litellm/releases (v1.109.1), https://docs.litellm.ai/blog/claude-code-beta-headers-incident
- https://github.com/1rgs/claude-code-proxy, https://github.com/fuergaosi233/claude-code-proxy, https://github.com/luohy15/y-router
- https://github.com/cablate/model-relay (extracted)
- https://github.com/KarpelesLab/teamclaude/blob/master/docs/proxy-modes.md (extracted)
- https://github.com/peter-wagstaff/claude-hybrid-router, https://github.com/Screddyice/backdoor, https://github.com/aeroxy/claude-proxy
- https://github.com/router-for-me/CLIProxyAPI/issues/7111, https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.61/internal/runtime/executor/helps/claude_ratelimit.go
- https://github.com/mtrojnar/pi-usage, https://github.com/ArkNill/claude-code-hidden-problem-analysis/blob/main/02_RATELIMIT-HEADERS.md

**Local servers**
- https://docs.ollama.com/api/anthropic-compatibility, https://github.com/ollama/ollama/releases/tag/v0.14.0, https://github.com/ollama/ollama/issues/13949
- https://docs.vllm.ai/en/stable/serving/online_serving/, https://github.com/vllm-project/vllm/releases/tag/v0.11.1, https://github.com/vllm-project/vllm/issues/44000
- https://docs.sglang.io/docs/basic_usage/anthropic_api, https://github.com/sgl-project/sglang/releases/tag/v0.5.9
- https://github.com/ggml-org/llama.cpp/tree/master/tools/server, https://github.com/ggml-org/llama.cpp/releases/tag/b7187, https://huggingface.co/blog/ggml-org/anthropic-messages-api-in-llamacpp
- https://lmstudio.ai/docs/developer/anthropic-compat/messages, https://lmstudio.ai/changelog/lmstudio/lmstudio-v0.4.1, https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/2535
- https://github.com/farion1231/cc-switch/issues/5376 (missing count_tokens fallback)

**Translation**
- https://developers.openai.com/api/reference/resources/chat (Chat Completions reference)
- https://pkg.go.dev/github.com/elkpi/oxa-protocol/go/v3, https://github.com/maximhq/bifrost, https://pkg.go.dev/github.com/hy-shine/claude-proxy-go@v0.2.0, https://github.com/QuantumNous/new-api
- https://github.com/BerriAI/litellm/issues/44029, https://github.com/router-for-me/CLIProxyAPI/issues/5419

**Policy/brand press**
- https://www.theregister.com/software/2026/02/20/anthropic-clarifies-ban-on-third-party-tool-access-to-claude/5014546
- https://techcrunch.com/2026/04/04/anthropic-says-claude-code-subscribers-will-need-to-pay-extra-for-openclaw-support/
- https://github.com/anomalyco/opencode/issues/7410
- https://laravel-news.com/clawdbot-rebrands-to-moltbot-after-trademark-request-from-anthropic
- https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan

---

## Research Methods

| Tool | Queries | Purpose |
|---|---|---|
| **Perplexity perplexity_research (PRIMARY)** | 9 | Landscape of routers; native `/v1/messages` in local servers; statusLine/Stop hook/`--settings`/subagentStatusLine; network/model env vars and RC requirements; Messages API SSE, usage, rate-limit headers, caching, prices; terms/trademark risks; Anthropic↔OpenAI translation and Go libraries; Claude Code churn breakages |
| Perplexity perplexity_reason | 0 | not needed (synthesis done in-report) |
| Perplexity perplexity_search | 0 | — |
| Perplexity perplexity_ask | 1 | Latest Go release / net/http h2 with GetCertificate (single-source; flagged) |
| Context7 | 0 | Not used: the questions were about product policy, docs and the landscape rather than library APIs; official docs were extracted directly instead |
| Tavily tavily_search | 0 | — |
| Tavily tavily_research | 0 | — |
| Tavily tavily_extract | 7 URLs (5 calls) | Cross-validation of load-bearing claims: RC docs, legal-and-compliance, pricing page, Usage Policy, statusline docs, model-relay README, teamclaude proxy-modes, npm registry `latest` |
| Tavily tavily_crawl / tavily_map | 0 | — |
| WebFetch / WebSearch | 0 | — |
| Training data | 2 areas | Only general protocol background (SSE framing, MITM CONNECT mechanics) and judgment on library fit. Every version, date, price and policy quote comes from tool output |

**Total MCP tool calls:** 15 (9 perplexity_research, 1 perplexity_ask, 5 tavily_extract)
**Training data reliance:** low. Versions are registry- or release-page-sourced (Claude Code 2.1.325 verified directly on npm). Prices, RC rules, the legal-page clause and the AUP clause were verified verbatim by extraction.

**Inconclusive or single-source items (flagged):**
- whether the RC bridge uses WebSocket;
- the first version with `subagentStatusLine`;
- the semantics of `unified-fallback-percentage`;
- Ollama cache-usage reporting (docs and observation conflict);
- the Go 1.27.5 latest-release claim (one source; irrelevant to the Go ≥1.26 floor);
- independent verification of the peer tools' RC claims;
- per-library Go module versions, which came from the research tool's pkg.go.dev retrieval and were not each re-fetched.
