# dgx_statusline.py — widget reference

What every segment of the `claude-dgx` status line shows, where the number comes from,
and how each behaves on the two serving lanes (DGX Flash vs Anthropic passthrough).
Companion to the header comment in `../dgx_statusline.py`; this document is the long form.

## How it runs

- The `claude-dgx` launcher passes a `statusLine` block in its `--settings` JSON
  (`type: command`, `refreshInterval: 4`), so the line exists **only in claude-dgx
  sessions** — `~/.claude/settings.json` is never touched. Opt out per session with
  `DGX_STATUSLINE=0 claude-dgx`.
- Claude Code launches `python3 .../dgx_statusline.py` and pipes one JSON blob of
  session state to stdin on every refresh (after each assistant message, after
  /compact, on mode changes, plus every 4 s tick; debounced 300 ms, in-flight runs
  cancelled). We print up to two rows. Display requires exit 0 with stdout; stderr is
  invisible unless `claude --debug`. Every code path ends in output + exit 0.
- The script is stateless between runs; all continuity lives in per-session cache
  files `~/.cache/dgx-llm/statusline-<session_id>.json` (telemetry, sparkline history,
  session-rate state) and `statusline-git-<dir>.json` (branch lookups, 5 s TTL).
  Cache writes are atomic (`mkstemp` + `rename`).
- DGX-side numbers come from **one** VictoriaMetrics instant query per refresh
  (~25 ms on the LAN) spanning ~14 series; results older than `DGX_SL_TTL` (4 s) are
  reused from cache instead of re-fetched. The query bypasses HTTP(S)_PROXY on
  purpose: the launcher exports `HTTPS_PROXY` pointing at the local mitmproxy, and
  metrics traffic must not traverse it.

## Row 1 — session & lane

Rendered purely from Claude Code's stdin JSON (plus git).

| Widget | Example | Measures | Source | DGX lane | ANTH lane |
|---|---|---|---|---|---|
| Lane pill | `(details in table below)` | Which backend is serving this session's main model | stdin `model.id` compared against the launcher's `LOCAL_MODEL_PREFIXES` | Cyan pill `◨ DGX` | Magenta pill `◨ ANTH` |
| Model | `Sonnet 5.5` | Display name of the session model | stdin `model.display_name` (falls back to `model.id`) | same | same |
| Branch | `main` | Git branch of the workspace (short SHA when detached) | `.git/HEAD` walk-up, cached 5 s | same | same |
| Project | `dgx-llm` | Basename of the project dir | stdin `workspace.project_dir` → `current_dir` → `cwd` | same | same |
| Context thermometer | `▰▰▰▱▱▱▱▱▱▱ 43%/1.0M` | How full Claude Code believes the context window is | stdin `context_window.used_percentage` / `context_window_size` (see math below) | yes | yes |
| Composition `▤❙◈` | `▤30% ❙50% ◈20%` | What the context is MADE OF, byte-proportional over the three movable buckets: **▤ tool results** (file reads, command output — usually the whale), **❙ conversation** (user + assistant text + tool-call payloads), **◈ thinking**. Glyph-tagged fixed-width percents, `<1%` for present-but-tiny buckets, zero-content buckets omitted. A proportional bar variant preceded this and was removed — percents alone are cleaner. | Incremental parse of the session transcript (stdin `transcript_path`); ~tokens/4 byte heuristic, the same one the ledger exporter uses. System prompt / tool definitions are not in the transcript file and are out of scope by construction. Byte-offset is cached, so each refresh parses only NEW complete lines (capped 512 KB/refresh — on very large transcripts the bar converges within ~5 refreshes; a transcript reset/shrink re-bases automatically). Colors: cyan / green / magenta. Identical on both lanes (it reads the local transcript either way) | yes | yes |
| Cache hit `♻` | `♻ 93%` | Share of prompt tokens served from cache | **Lane-aware** (below) | vLLM prefix-cache ratio from VictoriaMetrics | stdin `prompt_cache.hit_ratio` |
| Lines `▲▼` | `▲870/▼351` | Cumulative lines added/removed this session | stdin `cost.total_lines_added` / `total_lines_removed` | same | same |
| Timer `⏱` | `⏱ 33m` | Wall-clock age of the session (shown after 1 min) | stdin `cost.total_duration_ms` | same | same |
| Tokens `↑↓` | `↑1.4M ↓53k ⟳1.1M ✍906k` | Cumulative session usage. ↑ = input incl. cache-creation + cache-read (each turn re-sends the growing context — real billed-equivalent volume); ↓ = output. **⟳** = cache-READ tokens (0.1x priced — the cheap bulk), **✍** = cache-WRITE tokens (1.25x premium). Split renders only when the lane reports it (Anthropic does; vLLM's zero cache fields auto-hide it) | stdin `context_window.total_*_tokens` for ↑↓; split + fallback from our incremental transcript usage parse. Also feeds the ⛏ equivalence | yes | yes || Cumulative tokens this session: ↑ = input incl. cache-creation and cache-read (each turn re-sends the growing context, so ↑ grows super-linearly — that is real billed-equivalent volume); ↓ = output | stdin `context_window.total_input_tokens` / `total_output_tokens`; fallback = our incremental transcript parse (usage blocks). Also feeds the DGX ⛏ equivalence | yes | yes |
| Cost `$` | `$2.10 ⛏0.09` | Session cost at Anthropic LIST prices (⚠ on the DGX lane this is what the same tokens would have cost at Anthropic, not what they cost here), plus **⛏** = owned-hardware cost of the same tokens on the **cash** basis (capital $123,108.28 over 36 months + power, ÷ measured MTok): `(↑+↓) × dgx_cost:dgx_usd_per_mtok / 1M`. The economic basis (15% cost of capital, `dgx_cost:dgx_usd_per_mtok_economic`, ~25% higher) is on Grafana. Color bands: grey < $1, white $1–5, yellow ≥ $5. Equivalence only on the DGX lane, sub-half-cent suppressed | stdin `cost.total_cost_usd`; ⛏ rate from VictoriaMetrics `dgx_cost:dgx_usd_per_mtok` (capex amortization + measured wall power ÷ measured MTok) | ⛪ shows ⛏ | $ only |
| Limits `⛽🗓` | `5h78% ->1h23m 7d12%` | Consumption of the Anthropic PLAN windows: **5h** five-hour rolling, **7d** seven-day weekly. Plain-text labels deliberately (emoji ⛽🗓 render as huge colored glyphs in some terminals). Color bands: grey <70%, yellow 70–90, >90 red. Binding window (higher %) gets a `->MM:SS` refill countdown past 70%. Hidden when never reported (API-key sessions), stale >30 min, or rerouting ALL Claude models (bare 'claude' prefix) | stdin `rate_limits.five_hour` / `.seven_day` (`used_percentage`, `resets_at`), cached 30 min | yes | yes || Consumption of the Anthropic PLAN windows: ⛽ five-hour rolling, 🗺 seven-day weekly. Color bands per window: grey <70%, yellow 70–90, >90 red. The BINDING window (higher %) gains a live refill countdown past 70%. POLICY: shown on BOTH lanes (plan state, not lane state) and SMOOTHED —last-seen values persist 30 min so CC's intermittent reporting can't blink it. Hidden only when never reported (API-key/pay-per-token sessions), stale >30 min, or rerouting ALL Claude models to the DGX (LOCAL_MODEL_PREFIXES contains bare 'claude')| stdin `rate_limits.five_hour` / `.seven_day` (`used_percentage`, `resets_at`), cached 30 min | yes | yes || stdin `rate_limits.five_hour` / `.seven_day` (`used_percentage`, `resets_at`) | yes | yes |

Lane-pill edge cases: empty `model.id` (before the first API call) renders a neutral
grey `◨ ?` rather than guessing; an unknown env setup (no `LOCAL_MODEL_PREFIXES`)
does the same. Badges flip live mid-session if you `/model opus` → `◨ ANTH`.

### Context math, both lanes

Claude Code computes `used_percentage` itself and we display it verbatim — we never
recompute. Its numerator is input-only: `input_tokens + cache_creation_input_tokens +
cache_read_input_tokens`; output tokens are excluded. Denominator is the model's
declared window. Verified on both lanes:

- **DGX lane:** since 2026-11-12 vLLM runs with `--enable-prompt-tokens-details`, so it
  splits usage like Anthropic: `input_tokens` = uncached remainder, plus
  `cache_read_input_tokens` / `cache_creation_input_tokens` (probe: one 25,018-token prompt
  reported 7,866 + 17,152 written, then 7,866 + 17,152 read). The three-way sum still equals
  true occupancy, and the `⟳ ✍` split now renders on the DGX lane too. (Before the flag: whole
  prompt in `input_tokens`, cache fields absent — 3-pass probe 2632/2632/2632.) Note: vLLM
  caches only whole 8,576-token blocks, so prompts under one block never show a hit. vLLM's
  `--max-model-len 1048576` sits ~4.6% above Claude Code's 1M belief, so the estimate
  errs slightly conservative — never a premature auto-compact.
- **ANTH lane:** Anthropic splits usage (`input 2 + cache_creation 798 + cache_read
  873548` on a real Opus turn); the three-way sum equals occupancy the same way.
- Current Anthropic lineup is 1M-window across the board (Opus 5.5, Sonnet 5.5,
  Fable 5.2, Haiku 5.5); only older Haiku 4.5 is 200K. The denominator shown
  (`/1.0M`, `/200K`) mirrors whatever Claude Code reports, so nothing is hard-coded.
- `used_percentage` is `null` before the session's first API response — the whole
  thermometer is suppressed then, no `/0` / `nan` leaks.

### Cache-hit ratio, why it is lane-aware

CC's `prompt_cache.hit_ratio` is derived from the Anthropic usage fields. vLLM does
not populate them (zeros), so on the DGX lane that figure would be a lying `♻ 0%`.
Instead the DGX lane shows **vLLM's own** prefix-cache effectiveness:
`vllm:prefix_cache_hits_total / vllm:prefix_cache_queries_total` (population across
all requests; live at the time of writing: 50.5M/54.2M ≈ 93%). On the ANTH lane
CC's figure is honest and used directly. Unknown lane → whichever data exists.

## Row 2 — GB300 telemetry strip

All values from the single VictoriaMetrics query against the DGX (`192.0.2.10`),
via recording rules maintained by vmalert, the vLLM exporter, DCGM and the ledger
exporter. Numbers describe the whole box (every session), except the session rate.

| Widget | Example | Measures | Underlying series / derivation |
|---|---|---|---|
| Health dot | `◉` green / yellow / `◌` red | Freshness of DGX data; degradation ladder | Green: last good sample < 15 s old. Yellow: showing last-known values, tagged `(~Ns old)`. Red `◌ DGX ?`: nothing known for > 300 s or ever |
| Queue | `r2·q0` | Requests running on vLLM · queued waiting | `vllm:num_requests_running`, `vllm:num_requests_waiting`; turns yellow when queue > 0 or `dgx_preempt:rate5m` > 0.01 (preemption thrash) |
| KV gauge | `KV▰▰▱ 92% ↺host 80%` | GPU KV blocks held by **running** requests (not occupancy) and, when nonzero, the **share of reused history served from the host tier** | `vllm:kv_cache_usage_perc`; `dgx_kv:host_hit_share`. **Yellow when host share > 5%** = agents' history no longer fits on the GPU (0% ≤ 12 agents, 80% at 13). *Changed 2026-11-12:* was yellow at gauge > 80% (reads 85–96% in healthy operation) and showed `+host` from `kv_offload_cpu_cache_usage_perc`, which is transfer-pinned memory, not host-tier fill — both inconsistent with the dashboards |
| Throughput | `»174/116t/s` + sparkline | **Mine / box** tokens-per-second | Mine: per-session delta of the exporter's `dgx_llm_session_tokens_out` counter, EMA(α=0.5) between refreshes; **hard 0 once the counter has been stationary > 15 s** (idleness is tracked directly, so no EMA ghosts linger while the session idles — across sleep/wake, TTL hits and VM outages alike); counted when a stream CLOSES, so it can read 0 mid-generation. Box: `dgx_tokens:gen_rate5m` = `sum(rate(vllm:generation_tokens_total[5m]))`, all sessions, 5-min rolling — stays nonzero while OTHER sessions generate, by design |
| Sparkline | `▂▃▅▇` | Selected trace history | Default `rate` (box tok/s). **Multi-trace**: `DGX_SL_TRACE` picks the signal — `rate` box tok/s, `kv` GPU KV fraction (pressure trend, predictive), `ttft` latency p95, `mine` this session's delivered rate. Every signal is recorded per sample regardless of which is displayed, so you can switch traces without losing history. Cells sampled while preemptions were active flash amber in any trace. Last ≤12 samples ≤ 90 s old (≥ 2 s apart), 15% range padding so flat periods stay legible; trail fades left, head brightest. History persists in the session cache and only appends REAL observations — a missing series never fabricates a 0 |
| Latency | `◔2.2s` | TTFT p95 over 30 min, all requests | `dgx_ttft:p95_30m` = `histogram_quantile(0.95, sum(rate(vllm:time_to_first_token_seconds_bucket[30m])))`; yellow > 8 s |
| Power | `⚡627W 52° 34¢/h` | GB300 GPU power draw, temperature, and electricity cost | `DCGM_FI_DEV_POWER_USAGE`, `DCGM_FI_DEV_GPU_TEMP`; ¢/h = whole-box wall estimate (`dgx_power:est_wall_watts` /1000 × `dgx_power:rate_usd_per_kWh` × 100). Color = whole-box wall estimate vs the 1,600 W system rating: yellow > 80% (1,280 W), red > 95% (1,520 W); the number shown stays GPU watts (*changed 2026-11-12* from 1,200/1,500 W applied to GPU-only watts) |
| Idle | `☾ idle 12m` | Minutes since any Claude Code session last sent a request to the DGX lane | `now − dgx_llm_last_dgx_request_timestamp_seconds` (newest `dgx_request` ledger event, all sessions); shown when > 5 min AND `num_requests_running` < 1. Lane-specific since 2026-11-11: the previous any-event timestamp counted Opus/Haiku passthrough too, so Anthropic traffic hid a truly idle DGX. Traffic that bypasses the proxy (benchmarks, synthetic probes) is not in the ledger; the running<1 gate keeps the marker off while it runs |

### Lane behavior on row 2

Identical data on both lanes — it is DGX telemetry either way, and that's the point:
while you work in an `◨ ANTH` stretch (Opus subagents etc.), the strip keeps telling
you what the Flash box is doing for your other sessions. Differences are minor: the
session-rate figure (`mine`) can only match on the DGX lane if the session_id matches
an exporter-tracked session (it normally does for claude-dgx sessions); on unknown
IDs only the box rate renders. On the stale path the sparkline is dropped and the
rate renders grey.

## Agent-panel subagent rows (--subagent)

The launcher also passes a `subagentStatusLine` (same script, `--subagent`), which
rewrites the row bodies in Claude Code's **agent panel** — the rows you see while
Agent/Task subagents run. Contract (docs, 2026-11-11): stdin = one JSON with `columns`
and a `tasks[]` array covering every visible row; output = one JSON line per row,
`{"id": "<task id>", "content": "<body>"}`; a row we skip keeps CC's default body
(`name · description · tokens`).

Each rendered row:

| Element | Example | Source |
|---|---|---|
| Status glyph | `»` running (yellow) · `✔` completed (green) · `✘` failed (red) · `◍` killed/unknown (grey) | `tasks[].status` |
| Name | `fix-auth-bug` | `name` → `label` → `description` → `agentType` fallback chain |
| Model | `Sonnet 5.5` | `tasks[].model` (when CC reports it) |
| Tokens | `12.4k tok` | `tasks[].tokenCount` |
| Wall clock | `02:11` | `now − startTime` (mm:ss, running) |
| Status text | `failed` | shown only for non-running rows |

Rows for which CC supplies no id (shouldn't happen) are skipped defensively; malformed
stdin emits nothing rather than crashing (same exit-0 discipline as the main line).
Note: the main line's `agent.name` stdin field is *not* set by Agent/Task subagent
runs — it is only for `--agent` sessions — which is why subagent awareness lives in
this separate setting rather than in row 1.

## Both-lane support matrix

| Concern | DGX lane | ANTH lane |
|---|---|---|
| Numerator correctness | ✅ full prompt in `input_tokens` (probe-verified) | ✅ split-fields sum |
| Denominator | CC's 1M belief (vLLM allows 4.6% more) | CC's 1M (200K for Haiku 4.5) |
| `♻` cache ratio source | vLLM counters (VM) | CC `prompt_cache` |
| Fires ⛽ rate-limit gauge | only if stdin includes it | same |
| Session rate `»mine` | ✅ when session tracked by ledger | usually absent (not DGX-bound) |
| Telemetry strip | live DGX | live DGX (unchanged) |

## Tunables

| Env | Default | Meaning |
|---|---|---|
| `DGX_SL_VM_URL` | `http://192.0.2.10:8428` | VictoriaMetrics base URL |
| `DGX_SL_TTL` | `4` | Seconds between real VM fetches (match refreshInterval) |
| `DGX_SL_ROWS` | `2` | 1 = lane row only; >2 = force row 2 even on narrow terminals |
| `DGX_SL_SPARK` | `1` | `0` disables the throughput sparkline |
| `DGX_SL_GIT` | `1` | `0` disables the git branch segment |

Launcher side: `DGX_STATUSLINE=0` omits the statusLine setting entirely.

## Troubleshooting

- **Blank status line:** the command exited nonzero or printed nothing. Run
  `claude --debug` in a session — stderr from the status line is logged there.
- **Nothing until trust:** the workspace-trust dialog must be accepted first; CC
  skips the status line before that (`Status line command skipped: workspace trust
  not accepted` under --debug).
- **`◌ DGX ?` for a while:** the DGX or its VM is unreachable from the laptop, or the
  `ssh -R` tunnel for the ledger exporter is down. Check `launchctl list | grep dgx`
  and `curl http://192.0.2.10:8428/api/v1/query?query=up` from the laptop.
- **`💤` stuck on / absurd age:** the ledger exporter froze — pre-2026-11-11 builds
  only rebuilt on `?rebuild=1`; current code rescans when the ledger grows. Restart
  with `launchctl kickstart -k gui/$(id -u)/io.hylo.ledger-exporter`.
- **Reset per-session telemetry (sparkline/rates):** delete
  `~/.cache/dgx-llm/statusline-<session_id prefix>*.json`.
