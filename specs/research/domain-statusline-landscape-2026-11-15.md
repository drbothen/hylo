# Domain research: Claude Code status line peer landscape + freshness delta (market-intelligence L3)

- **Type:** domain (market-intelligence-assessment, Step 2, depth L3: risk check + competitive summary)
- **Date:** 2026-11-15 (UTC; all sources accessed 2026-11-15 unless noted)
- **Project:** hylo (public)
- **Scope:** (A) the gap left by yesterday's research: the community status line tools for Claude Code; (B) freshness delta since 2026-11-14 on the statusLine contract, Claude Code versions, rate-limit headers, policy, new hybrid routers; (C) risk signals specific to P1 (`hylo statusline`).
- **Builds on (not repeated here):** `domain-hybrid-routing-claude-code-2026-11-14.md` (landscape §1, statusLine contract §2.2, policy §4.1, churn §4.3), `peer-tool-lessons-2026-11-14.md`, and `docs/STATUSLINE-WIDGETS.md`.
- **Claim tags:** **[documented]** = official vendor docs, changelog or registry; **[verified]** = read directly on the repo or registry page today; **[community-observed]** = third-party README, issue or press, not independently checked; **[inferred]** = this report's reasoning.
- **Scope is fixed by parity (D4).** Feature ideas below are backlog input for after cutover, not P1 changes.

---

## Executive summary

1. **The status line space is crowded and mature.** Five tools dominate: claude-hud (~28.9k stars), ccusage (~19.4k; its `statusline` is one command of a usage analyzer), ccstatusline (~13.6k), CCometixLine (~3.5k) and claude-powerline (~1.2k), plus a long tail of a dozen or more smaller ones. All five ship cost, context %, git, model and 5h/7d plan windows, and most also show prompt-cache state. [verified stars; community-observed widgets]
2. **No surveyed tool reports per-request lane, local-backend health or GPU telemetry.** Provider *detection* exists: claude-hud names Bedrock/Vertex/MiniMax; cc-usage-bar and claude-mini-hud recognize GLM/Kimi/DeepSeek base URLs; CCometixLine has custom model rules. None reads a Prometheus-compatible store, and none shows vLLM/LMCache/GPU state. [community-observed]
3. **The one real lane-aware peer is the model-relay plus coralline pair.** model-relay writes a per-session status file (`claude` / `pinned` / `failover` / `limit` / `offline` / `direct`), and coralline's `relay` segment displays it (`↪ glm-5.3 · failover`). The indicator is window-level, as hylo's pill is, and it covers no backend telemetry or owned-hardware cost. **hylo should not claim to be "the only lane-aware status line".** [community-observed]
4. **Things hylo does that no peer was found doing:** a backend telemetry row (health, queue, KV, host-tier hit share, TTFT p95, power, ¢/h, idle); owned-hardware `⛏` cost; **per-lane** p75/p95 cost colors computed from the user's own 30-day history; the composition split `▤❙◈`; the `↻` rebuild counter derived from the transcript; and the window age `⌂`. Pace-projected plan-limit coloring is **not** unique (claude-powerline, CCometixLine and ccstatusline all ship pace/forecast). [inferred from the README surveys]
5. **No Claude Code release after 2.1.325.** npm `latest` is still 2.1.325, and the GitHub release (2026-11-13 20:40) is still marked Latest. The statusLine stdin field list on the docs page matches yesterday's §2.2. The **2.1.323 removal of `subagentStatusLine` is confirmed** by the changelog line quoted in issue #109446, and the regression report #109494 was closed as a duplicate. [documented / verified]
6. **Stdin facts yesterday's report missed** (they bear on parity, and none is new since 11-14 as far as can be told):
   - `cost.total_cost_usd` uses a **managed-only** `modelPricing` table when one is in effect (since 2.1.242). This can shift `$` and the cost-history percentiles for enterprise users.
   - `cost.total_duration_ms` "accumulates across resumes and doesn't include time while the session isn't running".
   - `output_style.name` and `pr.kind` exist.
   - The repo object is `workspace.repo.*`, not a top-level `repo.*`.
   [documented]
7. **No change to rate-limit headers or Anthropic's policy text was found.** The legal page's "intermediate … session tokens" clause is unchanged as of today. One refinement: a community README reports that `7d_oi` is the **Fable-only** weekly allowance, sent only on Fable responses. [documented / community-observed, single source]
8. **New hybrid routers seen this week are all base-URL tools, so they lose Remote Control:** claude-spillway (quota spillover to Ollama Cloud), wend-router, leitum, Toy Models Gate, plus llm-router and routecall (hook/plugin based). None is endpoint-preserving, and none has a lane-aware status line. [community-observed]
9. **P1 platform risk is moderate and manageable.** The `statusLine` command stays documented and keeps gaining fields additively. The removed surface was `subagentStatusLine`, not `statusLine`. Claude Code "mods" (since 2.1.287, `ui.render` sites including a per-mod status line) are a faster-churning sibling surface: watch it, don't adopt it. [documented / inferred]
10. **Policy and trademark posture for P1 is better than most peers'.** hylo's status line reads only stdin, transcript, caches and its own metrics store. Several peers instead read the Claude.ai OAuth token from the keychain to call `/api/oauth/usage` (ccstatusline, claudeline, leeguooooo's usage bar, claude-spillway), which sits closer to the "collect … intermediate credentials" clause. Most peers use "claude" in their names. hylo does not, which is the conservative pattern. [community-observed / inferred]

---

## A. Claude Code status line peer landscape

### A.1 Major tools (verified against repo pages, 2026-11-15)

| Tool | Language / distribution | Stars (2026-11-15) | Latest release | Widgets (documented, incl. optional) | Data sources | Cross-platform | Alt-backend / lane awareness |
|---|---|---|---|---|---|---|---|
| **jarrodwatts/claude-hud** | TypeScript on Node 18+/Bun; Claude Code plugin marketplace | **28.9k** [verified] | v0.15.0, 2026-11-02 [verified] | model/provider, git, context, token breakdown, cost, prompt-cache status, 5h/7d + reset; tools/agents/todos activity lines; optional output speed | stdin, transcript JSONL, config, git; says no undocumented API calls | macOS/Linux/Windows (Windows needs Node) [verified] | Detects Bedrock, Vertex, MiniMax (provider label); no per-request lane [community-observed] |
| **ccusage/ccusage** (`ccusage statusline`; formerly ryoppippi/ccusage) | v20 is **Rust** (release notes mention a Rust 1.100 bump), shipped through npm/npx/bunx as platform binaries; Nix flake | **19.4k** [verified] | **v20.0.51, 2026-11-14** [verified] | model + effort, session/today cost, 5h **block** cost + time left (reconstructed locally), burn rate $/h, context tokens/% | stdin + local transcript JSONL; LiteLLM pricing snapshot, offline by default; `--cost-source cc/ccusage/both` | npm platform binaries (macOS/Linux/Windows) [community-observed] | `modelLabelAliases` maps any model id to a display label; multi-agent-CLI reports (Codex, Kimi, …); no lane split [verified docs] |
| **sirmalloc/ccstatusline** | TypeScript; npm/npx, bunx; Ink TUI configurator; powerline themes | **13.6k** [verified] | v2.2.34 (Perplexity dates it 2026-11-06; the release page extract showed no date) | model, git (+insertions/deletions/root), session cost, tokens and speed, context %, cache timer/hit/miss, block/weekly usage + per-model weekly (Sonnet/Opus/Fable), extra usage, spend limit, reset timers and forecasts, memory, session name, OSC 8 link, custom-command widgets | stdin (context, cache, cost, spend limit); transcript (block timer, tokens/speed, compaction counter); **Anthropic `/api/oauth/usage` using OAuth credentials read from the macOS Keychain or the credentials file** (block/weekly/extra usage) [verified via Context7 docs] | macOS/Linux/Windows (docs/WINDOWS.md) [verified] | None found; custom command widgets could show anything [verified README] |
| **Haleclipse/CCometixLine** | Rust; npm `@cometix/ccline`, GitHub binaries (Linux x64/arm64 incl. static, macOS x64/arm64, Windows x64), source build | **3.5k** [verified] | v2.0.1, 2026-10-24 [verified] | presets: model, dir, git, context + trend, cache, cost, 5h pace, code activity; dashboard (3 lines) | stdin; optional companion mod for live activity/timing | macOS/Linux/Windows binaries [verified] | `models.toml` custom model rules (e.g. Kimi, custom context limit); no lane split. **README still documents `subagentStatusLine`** (inert since 2.1.323). v1 shipped a "Claude Code patcher" and, in v1.0.9, "Claude in Chrome subscription bypass patches"; v2 removed the patcher [verified] |
| **Owloops/claude-powerline** | TypeScript; npm `@owloops/claude-powerline`; Claude plugin; TUI grid layout | **1.2k** [verified] | v1.32.8, 2026-11-06 [verified] | model, git, session/today/month cost and tokens, context %, prompt-cache timer, native 5h/7d + reset/pace | stdin (quota segments need `rate_limits`), transcript JSONL | Node (three OSes not confirmed from README) | Fallback context limit for unknown models; no backend detection [community-observed] |

### A.2 Long tail (Perplexity survey; stars and versions **not** re-verified on repo pages)

| Tool | Lang | Stars (date as reported) | Notable widgets / sources | Alt-backend awareness |
|---|---|---|---|---|
| rz1989s/claude-code-statusline | Bash, Homebrew tap | 480 (11-12) | cost (session/daily/weekly), block timer, cache efficiency, burn rate, MCP status; reads `~/.claude/projects` JSONL; Windows only through WSL | none found |
| chongdashu/cc-statusline | TS generator → Bash | 646 (11-11) | context, cost, reset timer, tokens, burn rate; can call ccusage | none found |
| leeguooooo/claude-code-usage-bar (`claude-statusbar`, PyPI 3.52.3) | Python + binaries | 393 (11-15) | 5h/7d + projections, cache age, relay balance; **Anthropic OAuth usage API** for model-scoped limits | relay/Bedrock/Vertex "no-quota" mode; no local engine |
| ersinkoc/claude-statusline (PyPI 1.9.9) | Python | 78 | JSONL → local DB/daemon; cost, tokens, cache, CPU/mem | explicitly Claude-only |
| hagan/claudia-statusline | Rust | 37 | context, cost/$h, cache hit, compaction/subagent tracking; SQLite + optional Turso cloud sync | adaptive context learning only |
| fredrikaverpil/claudeline | **Go** (`go install`, binaries, plugin) | 55 | 5h/7d + scoped quota bars, cache miss/expiry, service status; **Anthropic OAuth usage API** | identifies Bedrock/Vertex/Foundry/API/OAuth modes |
| felipeelias/claude-statusline | **Go**, Homebrew | n/a | Starship-style format string: dir, branch, model, cost (fixed $1/$5 thresholds), context, timer, lines | none [community-observed blog, 2026-03-17] |
| TuYv/cc-usage-bar | Node add-on | 4 | provider quota/balance; stdin `rate_limits`, then cache, then provider HTTP (Anthropic fallback uses OAuth) | detects `ANTHROPIC_BASE_URL` for Kimi, GLM, MiniMax, DeepSeek, StepFun, SiliconFlow, OpenRouter, Novita |
| zander-zyx/claude-mini-hud | TS | 10 | context, cache, cost, 5h/7d or provider balance, token speed | detects many base-URL providers |
| orassayag/super-status | Bash | 8 | cache ratio/expiry, 5h/7d pace, OpenRouter credits, Anthropic Admin cost API | detects OpenRouter, z.ai, Bedrock, Vertex, custom base-URL host |
| **Nanako0129/coralline** | Bash (+ wizard) | n/a | p10k-style; `relay` segment; cache hit + expiry countdown; tok/s | **reads model-relay's per-session status file: the only lane-aware segment found** [community-observed README] |
| awesomezun/claude-statusline ("Awesome Statusline") | Bash + PowerShell | n/a | model, effort, context, cache, limits; also installs as a Claude Code **mod** (band above the prompt) | none |

### A.3 Lane / backend awareness: the precise answer

- **Provider detection (static, per session):** claude-hud, claudeline, super-status, cc-usage-bar, claude-mini-hud, CCometixLine (model rules), ccusage (`modelLabelAliases`). They label *where the base URL points* or *what the model id is*. [community-observed]
- **Window-level routing state:** **model-relay + coralline** (`↪ claude`, `↪ glm-5.3`, `· failover`, `· limit`, `offline`, `direct`). This is the nearest peer to hylo's lane pill. It is a status *file* written by the router, not inferred from the model id. [community-observed: model-relay README and release notes, coralline README]
- **Per-request lane split of tokens or cost inside one session:** none found, in any tool. hylo does not do it either: its pill follows the session's **main** model (STATUSLINE-WIDGETS row 1). The proxy ledger has per-request lanes; the status line does not show a per-lane split. [inferred]
- **Backend telemetry from a Prometheus-compatible store (vLLM/LMCache/GPU):** none found. The closest is ccstatusline's system-memory widget. [community-observed]

### A.4 What hylo's status line does that none of the surveyed tools do

[inferred from A.1–A.3; "none" means not found in the READMEs and docs checked]

| hylo widget (STATUSLINE-WIDGETS) | Nearest peer equivalent | Unique? |
|---|---|---|
| Row 2 backend strip: health dot (vLLM/LMCache down), queue `r·q`, KV gauge + `↺host`, `»mine`/`▣box` throughput, sparkline, TTFT p95, power/temp/¢/h, idle | none | **Yes** |
| `⛏` owned-hardware cash cost | none (peers show list-price or provider balance) | **Yes** |
| `$`/`$/h` colors at **personal p75/p95 per lane**, 30-day history | fixed thresholds (claude-statusline $1/$5; ccstatusline/ccusage burn-rate visuals) | **Yes** (percentile-from-history not found anywhere) |
| Composition `▤❙◈` by bytes since the last compact boundary | none found (claude-hud shows tools/agents activity, not composition) | **Yes** |
| `↻n` cache-rebuild counter (transcript, >20K excess-write threshold) | `prompt_cache.misses` / `miss_causes` shown by ccstatusline, CCometixLine, claudeline | Partly (different derivation; Claude Code now gives misses natively) |
| `⌂` Claude Code window age (survives `/clear`) | none found | **Yes** |
| Lane pill | coralline `relay` segment (via model-relay) | **No** (window-level peer exists) |
| Pace-projected plan-limit color | claude-powerline "pace", CCometixLine "5h pace/ETA", ccstatusline "forecast" | **No** |
| Context, cost, lines, timers, git, model, `♻` hit ratio | everywhere | No |

**Positioning line for the README (owner's call)** [inferred]: hylo's status line is "the one that knows your own hardware": lane, backend health and owned-hardware cost next to the Anthropic numbers. It is not "the first lane-aware status line".

### A.5 Ideas peers have that hylo lacks (backlog only; scope is fixed by parity)

[community-observed features; relevance is inferred]

1. **Warm-cache countdown** (`prompt_cache.expires_at`): ccstatusline, claude-powerline, coralline, leeguooooo. Claude Code already re-runs the line at `expires_at`. This is a cheap, high-value P7 widget for the 1-hour TTL.
2. **`prompt_cache.last_miss_cause` / `miss_causes`** (`tools_changed`, `system_prompt_changed`, `ttl_expired_5m`, `likely_server_side`): native data that could replace or complement the transcript-derived `↻` heuristic after cutover.
3. **Model label aliases** (ccusage `modelLabelAliases`): a config-driven version of backlog #29 (show the real served model on the local lane). This fits D15.
4. **`spend_limit` display** (gateway users) and **effort level** (`effort.level`): peers show both, and hylo ignores both today.
5. **A drop-in segment folder** (statusline-pro: `~/.claude/status-segments/*.json`) or **custom-command widgets** (ccstatusline): an extensibility hook in place of hard-coded widgets.
6. **Interactive configurator / presets / powerline themes** (ccstatusline TUI, claude-powerline grid, CCometixLine presets): useful once hylo has a web UI/TUI (D16).
7. **Plugin-marketplace install** (claude-hud, claude-powerline, model-relay): a common distribution channel. Mind the plugin-name rule in C.3.
8. **Per-model weekly windows (Fable/`7d_oi`) via the OAuth usage API:** **do not adopt.** It requires reading the user's Claude.ai token (see C.2). The stdin-plus-ledger approach is the safer equivalent.

---

## B. Freshness delta since 2026-11-14

| Item | What was checked (2026-11-15) | Result |
|---|---|---|
| Claude Code version | npm registry `@anthropic-ai/claude-code/latest`; GitHub releases page; unofficial changelog mirror | **No change: 2.1.325 is still latest** (GitHub release 2026-11-13 20:40, "30 commits to main since"). Nothing after 2.1.325 exists yet. [verified] |
| statusLine stdin contract | Full docs page fetched and compared field by field with yesterday's §2.2 | **No new or removed fields detected.** The docs page carries no change date, so "unchanged since 11-14" means "matches yesterday's extraction". Corrections and additions to yesterday's list follow this table. [documented] |
| statusLine settings | Same page | `type`, `command`, `padding`, `refreshInterval` (min 1), `hideVimModeIndicator`: unchanged. New-to-us: `footerLinksRegexes` (footer link badges without a script; not a statusLine key). `allowManagedHooksOnly` hides non-managed status lines silently. [documented] |
| `subagentStatusLine` | Issues #109446 and #109494 | **Removal confirmed and intentional:** the 2.1.323 changelog reads "Removed the subagentStatusLine setting: subagent rows always use the default look, and settings files that still hold the key load as before". #109494 (regression report) is labeled duplicate. #109446 asks for it back and proposes mods render sites (#105919); no maintainer reversal seen. [documented via issue quote] |
| Rate-limit headers | Perplexity search (week), CLIProxyAPI #7417 and commit cb70eac, claude-spillway README | **No header change found.** Refinements: (a) community report that `anthropic-ratelimit-unified-7d_oi-*` is the **Fable-only weekly allowance**, sent only on Fable responses (single source, claude-spillway); (b) Claude Code honors unified headers from a *gateway* only when the auth token is a JWT with `aud: claude-gateway` (CLIProxyAPI #7417). Neither affects invisible mode, where the real Anthropic headers arrive; (c) 2.1.323 reworded the `seven_day_overage_included` limit messages to point to `/usage-credits` (unofficial changelog). [community-observed] |
| Anthropic terms / policy | Legal-and-compliance page re-extracted; Perplexity search (week) | **Legal page text unchanged** ("may not collect, store, or intermediate Claude.ai credentials or session tokens"; "The Claude Code binary must not be modified"). AUP (eff. 11-12) already covered yesterday. New this week: press coverage of the **Supported Regions Policy** (dated 11-12; not design-relevant) and commentary ("Claude is coming for reverse proxies"). **No enforcement against user-run local proxies found.** [documented / community-observed] |
| New hybrid-routing tools | Perplexity search (week), Tavily | claude-spillway (PyPI 0.10.0; base URL; spills `/v1/messages` to **Ollama Cloud** when quota is low; reads the OAuth usage endpoint; multi-account launcher); wend-router 0.2.0 (base URL, free models, MIT); leitum (launcher for base-URL providers incl. local); Toy Models Gate (VS Code extension gateway, base URL); llm-router 16.0.0 (hooks/MCP, not a proxy); routecall (plugin, Zenodo). **All base-URL or hook-based, so none keeps Remote Control.** No new endpoint-preserving interceptor found beyond yesterday's list. [community-observed] |
| Peer releases | model-relay releases page | model-relay ≥0.7.0 writes `~/.claude/model-relay-status/<session id>` for status lines (A.3). This existed before 11-14 but was not called out yesterday. [community-observed] |

**Stdin facts not in yesterday's §2.2** [documented: statusline and settings-reference docs]. These are pre-existing as far as can be told and are listed for parity awareness.

- `cost.total_cost_usd` is "computed client-side at list price **unless a `modelPricing` table is in effect**". `modelPricing` is **managed-scope only** (ignored in user/project/local settings and in `--settings`), requires 2.1.242+, and supports `multiplier` (0–10; >1 needs 2.1.271+) and per-model `overrides`. Effect on hylo: for users under managed pricing, `$`, `$/h` and the cost-history percentiles reflect contracted rates rather than list price. hylo cannot set this from its launcher (managed only).
- `cost.total_duration_ms` "accumulates across resumes and doesn't include time while the session isn't running". STATUSLINE-WIDGETS says "wall clock since the session started, idle included". Both can be true (idle while running counts; time with the process stopped does not), but the `⏱` doc wording should mention resumes when docs are next touched.
- `output_style.name`, `pr.kind` (`mr` for GitLab), `pr.review_state`, `workspace.git_worktree`; the repo object is **`workspace.repo.{host,owner,name}`** (yesterday's report wrote `repo.*`).
- `context_window.total_input_tokens` / `total_output_tokens` are documented as "from the most recent API response", not session totals.
- `prompt_cache` does not count subagent requests (consistent with `♻` being main-conversation only).

---

## C. Risk signals specific to P1

### C.1 Platform risk (statusLine contract churn): **moderate, manageable**

- **Additive churn is the norm.** Fields arrive version-gated (2.1.80 `rate_limits`; 2.1.234 `pr.kind`; 2.1.251 `prompt_cache`/`spend_limit`; 2.1.260 `last_miss_cause`, `workspace.repo` for nested GitLab; 2.1.284 `spend_limit` dollars; 2.1.295 behavior change under `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`). hylo's defensive parsing (every object optional) is the right mitigation. [documented]
- **Removal precedent exists, but for the sibling surface.** `subagentStatusLine` went from documented to inert in one release (2.1.323), with no startup warning, and peers (CCometixLine) still document it. A removal of `statusLine` itself is **not** signalled: it is documented, still gaining fields, and has `/statusline` as a first-class command. [documented / inferred]
- **Mods are the surface to watch.** Since 2.1.287, mods can draw at `ui.render` sites, including "a status line under the prompt" (one per mod, capped at 200 chars or two rows), a band above the prompt, panes and toasts. The mods API churns fast: 2.1.319 removed `$.ui.backdrop`, and 2.1.323 changed band composition and `$.theme.set` arguments. If Anthropic ever moves rich footer UI to mods, hylo would need a mod adapter. **Recommendation:** stay on `statusLine` for P1, and add "mods status line" as a P7 watch item. [documented / inferred]
- **Historic breakage of status line data:** `current_usage` zeros in 2.1.8–2.1.14 (yesterday §4.3). Mitigation already planned: golden tests covering absent/null objects.
- **Mitigations for P1** [inferred]: (1) a golden stdin corpus per tested Claude Code version (with and without `prompt_cache`, `rate_limits.spend_limit`, `output_style`, `pr.kind`); (2) record stdin `version` in the cache files for diagnosis; (3) never exit nonzero (already a parity rule); (4) a per-release changelog review step for `area:statusline` (P5 checklist).

### C.2 Competitive replication risk: **low for the differentiators, high for the commodity widgets**

- **Commodity widgets** (context, cost, git, model, 5h/7d, cache hit) are offered by five tools with 1k–29k stars and fast release cadence (ccusage released 2026-11-14; ccstatusline and claude-powerline weekly). Competing on them is pointless. [verified / inferred]
- **The differentiators depend on infrastructure peers don't have:** a proxy ledger (per-request lane truth), a metrics store with vLLM/LMCache/DCGM series, and owned-hardware cost rules. A peer could add a "Prometheus query" custom widget (ccstatusline custom commands, CCometixLine mods), but reproducing the health semantics (LMCache-connector detection, preemption coloring, TTFT sample-size dimming) requires the backend. Replication risk is low unless model-relay or claude-code-router grows a telemetry story. [inferred]
- **Most likely convergence:** model-relay plus coralline already pairs a router with a status line segment. If model-relay adds an HTTPS-proxy-mode ledger and a metrics strip, it would be the closest overlap. **Watch model-relay releases.** [inferred]
- **Go peers exist** (claudeline, felipeelias/claude-statusline), so "single static Go binary" is not unique for the status line by itself. It is unique only combined with the proxy and exporter. [community-observed]

### C.3 Trademark and naming

- **Peers' naming is mostly non-compliant with the conservative reading**: claude-hud, claude-powerline, claude-statusline (several), claudeline and claudia-statusline use "claude" in the product name. No rename request to a status line tool was found; a 2026-10 survey by another project reached the same conclusion ("tolerance, not permission"). Known enforcement: Clawdbot → Moltbot → OpenClaw (2026-01), and Anthropic's own plugin rename on legal advice (ralph-wiggum → ralph-loop, 2026-01-06). [community-observed]
- **The plugin manifest validator reserves names**: a third-party plugin name "cannot start with `claude-`, `anthropic-`, `anthropics-`, or `cc-plugin-`, be `claude`, `anthropic`, `anthropics`, `claude-code`, or `claude-mods`, or put `official` beside `claude` or `anthropic`" (validator text quoted in trailofbits/skills#353, 2026-10). If hylo ever ships a plugin (A.5 idea 7), name it `hylo`. [community-observed]
- **hylo's position is already the conservative one** (no "Claude" in names, "for Claude Code" descriptive use, disclaimer; yesterday §4.2). No new action needed for P1. Keep status line glyphs and colors original (no Anthropic orange or logo). [inferred]
- **Adjacent compliance signal:** the legal page says "The Claude Code binary must not be modified". CCometixLine v1's patcher and "subscription bypass patches" are the anti-pattern. hylo never patches the binary (consistent with D6's "unmodified client"). [documented / verified]
- **Credential handling contrast (useful in the README):** hylo's status line never reads the Claude.ai OAuth token. Several popular peers do, to call `/api/oauth/usage`. hylo also never sends its status line traffic through the proxy (OD-2: `Proxy: nil`). [verified via Context7 for ccstatusline; community-observed for the others]

---

## Implications for P1

1. **No change to P1 scope or the parity target.** Nothing in B invalidates a legacy behavior. Claude Code is still 2.1.325, and the stdin fields hylo reads are unchanged. [documented]
2. **Golden stdin corpus:** add fixtures that carry `output_style`, `pr.kind`, `workspace.repo`, `prompt_cache.last_miss_cause`, and `rate_limits.spend_limit` (with and without the dollar fields) to prove additive fields do not perturb byte-parity output. All synthetic (public-repo hygiene).
3. **Do not port `--subagent`** (confirmed removal). Do not copy CCometixLine's still-documented `subagentStatusLine` example.
4. **Cost semantics note for docs (D15 rationale):** `$` is list price **unless managed `modelPricing` applies**. The p75/p95 history then mixes bases if a user's org changes pricing. Document it, but don't change behavior pre-cutover.
5. **`⏱` doc wording:** add "accumulates across resumes; excludes time the session isn't running" (official semantics) to the widget doc when it is next edited. Not a behavior change.
6. **README positioning:** say "lane-aware with backend telemetry and owned-hardware cost". Do not say "first/only lane-aware status line"; credit model-relay plus coralline in an "Alternatives" list (yesterday's open question 6).
7. **Backlog after cutover (P7):** warm-cache countdown, `last_miss_cause`, config-driven model label aliases (#29), effort, spend limit, drop-in segments. **Explicitly reject** OAuth-usage-API widgets (credential handling).
8. **Watch list:** model-relay releases (convergence risk), Claude Code mods status line render sites (platform risk), #109446 (any `subagentStatusLine` replacement), and the `7d_oi` = Fable-only claim (verify against the ledger's `anth_ratelimit` captures when a Fable request occurs; local verification only).

---

## Sources (accessed 2026-11-15)

**Anthropic / Claude Code (official)**
- https://code.claude.com/docs/en/statusline (stdin fields, settings, triggers; fetched in full)
- https://code.claude.com/docs/en/settings-reference (`modelPricing` scope/version/schema)
- https://code.claude.com/docs/en/legal-and-compliance (credential and binary-modification clauses; extracted)
- https://code.claude.com/docs/en/plugins/mods/interface (render sites, mod status lines, version gates)
- https://code.claude.com/docs/en/plugins/mods (mods since 2.1.287; via perplexity_ask)
- https://registry.npmjs.org/@anthropic-ai/claude-code/latest (2.1.325; extracted)
- https://github.com/anthropics/claude-code/releases (v2.1.325 Latest, 2026-11-13; extracted)
- https://github.com/anthropics/claude-code/releases/tag/v2.1.325
- https://github.com/anthropics/claude-code/issues/109446 (changelog quote on the removal; extracted)
- https://github.com/anthropics/claude-code/issues/109494 (labeled duplicate; extracted)
- https://github.com/anthropics/claude-code/issues/108569 (usage-credits statusLine feature request)

**Status line peers**
- https://github.com/jarrodwatts/claude-hud, https://github.com/jarrodwatts/claude-hud/releases (extracted)
- https://github.com/ccusage/ccusage, https://github.com/ccusage/ccusage/releases, https://github.com/ccusage/ccusage/blob/main/docs/guide/statusline.md (extracted)
- https://github.com/sirmalloc/ccstatusline (WebFetch), https://github.com/sirmalloc/ccstatusline/releases (extracted); Context7 `/sirmalloc/ccstatusline` (docs/DEVELOPMENT.md, docs/USAGE.md)
- https://github.com/Haleclipse/CCometixLine, https://github.com/Haleclipse/CCometixLine/releases (extracted)
- https://github.com/Owloops/claude-powerline, https://github.com/Owloops/claude-powerline/releases (extracted)
- https://github.com/Nanako0129/coralline (Tavily snippet)
- https://github.com/cablate/model-relay, https://github.com/cablate/model-relay/releases (extracted / snippet)
- https://github.com/rz1989s/claude-code-statusline, https://github.com/chongdashu/cc-statusline, https://github.com/hagan/claudia-statusline, https://github.com/ersinkoc/claude-statusline, https://github.com/TuYv/cc-usage-bar, https://github.com/leeguooooo/claude-code-usage-bar, https://github.com/zander-zyx (claude-mini-hud), https://github.com/orassayag/super-status, https://github.com/fredrikaverpil/claudeline (Perplexity survey; not re-verified)
- https://felipeelias.github.io/2026/03/17/claude-statusline.html (Go status line)
- https://github.com/awesomezun/claude-statusline, https://github.com/cell-observatory/claude-statusline
- https://alexcloudstar.com/blog/claude-code-status-line-guide-2026 (statusline-pro drop-in folder)

**Freshness / policy / routers**
- https://changelogs.core-directive.com/ (unofficial Claude Code changelog mirror; 2.1.323 limit-message entry)
- https://github.com/router-for-me/CLIProxyAPI/issues/7417, https://github.com/router-for-me/CLIProxyAPI/commit/cb70eacfa533d44efb1eec5007098321e396fc3c
- https://pypi.org/project/claude-spillway/0.10.0/ (search snippet; direct page fetch failed)
- https://klymentiev.com/blog/claude-code-free (wend-router), https://pypi.org/project/leitum/, https://pypi.org/project/llm-routing/16.0.0/, https://marketplace.visualstudio.com/items?itemName=medevorg.toy-models-gate, https://zenodo.org/records/24113029 (routecall)
- https://pivotnews.ai/build/anthropic-documents-claude-code-proxy-and-certificate (network docs coverage, 2026-11-15)
- https://dev.to/haoyi/claude-is-coming-for-reverse-proxies-53ad, https://agihunt.info/en/p/1a1c828b0547126170734a66c25 (AUP / regions commentary)

**Trademark**
- https://github.com/Jbmanllr/accroster/issues/27 (naming-rules survey, 2026-10-24)
- https://github.com/anthropics/claude-plugins-official/pull/142 (rename on legal advice)
- https://github.com/trailofbits/skills/issues/353 (reserved plugin-name validator text)
- https://openclawhq.io/blog/why-was-clawdbot-renamed-to-moltbot

---

## Research Methods

| Tool | Queries | Purpose |
|---|---|---|
| **Perplexity perplexity_research (PRIMARY)** | 1 | Track A: full status line peer survey (14 tools: language, distribution, stars, releases, widgets, sources, OS, backend awareness) |
| Perplexity perplexity_reason | 0 | not needed |
| Perplexity perplexity_search | 6 | Track B: Claude Code versions after 2.1.325; policy news (week); rate-limit header changes (week); new hybrid routers (week); statusLine issues (week). Track C: trademark/rename signals |
| Perplexity perplexity_ask | 2 | `modelPricing` scope/version; Claude Code mods vs statusLine |
| Context7 | 2 (resolve + query) | ccstatusline usage-widget data sources (OAuth usage API, Keychain credential read) |
| Tavily tavily_search | 3 | claude-spillway; lane-aware status line search; coralline/model-relay status segment |
| Tavily tavily_research | 0 | not needed |
| Tavily tavily_extract | 9 calls (17 URLs) | npm `latest`; statusline docs; GitHub releases (claude-code, ccusage, claude-powerline, claude-hud, ccstatusline, CCometixLine, model-relay); peer repo pages (stars); issues #109446/#109494; legal page; ccusage statusline doc |
| Tavily tavily_crawl / tavily_map | 0 | not needed |
| WebFetch | 5 | statusline docs (full field table); settings-reference (`modelPricing`); ccstatusline repo; mods interface doc; PyPI claude-spillway (failed: JS-only page) |
| WebSearch | 0 | not needed |
| Training data | 1 area | only general framing (what a powerline/p10k style is). Every star count, version, date, field and quote comes from tool output |

**Total MCP tool calls:** 23 (1 perplexity_research, 6 perplexity_search, 2 perplexity_ask, 2 Context7, 3 tavily_search, 9 tavily_extract), plus 5 WebFetch.
**Training data reliance:** low.

**Why only one perplexity_research call:** track A is the only multi-source synthesis question in this delta. B and C are freshness checks, which the brief assigned to perplexity_search/ask and which were answered by direct extraction of registries, docs and issues.

**Inconclusive or unverified (flagged):**
- Star counts and versions for the A.2 long tail come from the Perplexity survey and were not re-read on repo pages. coralline, felipeelias/claude-statusline and awesomezun have no star figure.
- The ccstatusline v2.2.34 release date: Perplexity says 2026-11-06, but the release page extract showed no date.
- ccusage's statusline cache widgets and its OS matrix were not confirmed; claude-powerline's Windows support was not confirmed.
- Whether any status line fields were added *between* 2026-11-14 and today: the docs page carries no change history, so "unchanged" means "matches yesterday's extraction".
- `7d_oi` = Fable-only allowance: single community source (claude-spillway README); verify locally against ledger captures.
- claude-spillway details: the PyPI page could not be fetched (JS-only); facts come from search snippets.
- Whether "mods status line" render sites will ever supersede `statusLine`: no signal either way; treated as a watch item.
