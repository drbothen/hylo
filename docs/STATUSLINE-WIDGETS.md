# dgx_statusline.py — widget reference

What every segment of the `claude-dgx` status line shows, where the number comes from,
and how each behaves on the two serving lanes (DGX Flash vs Anthropic passthrough).
Companion to the header comment in `../dgx_statusline.py`; this document is the long form.
Every widget was re-reviewed on 2026-11-13 (findings, decisions and verification:
`docs/STATUSLINE-REVIEW-2026-11-13.md`).

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
- The script is stateless between runs; continuity lives in per-session cache files under
  `~/.cache/dgx-llm/`: `statusline-<session_id>.json` (telemetry sample, sparkline history,
  smoothed plan limits), `statusline-mix-<session_id>.json` (incremental transcript parse:
  composition, session token totals, last-turn rate) and `statusline-git-<hash>.json`
  (branch lookups, 5 s TTL, keyed by a digest of the full path). Writes are atomic
  (`mkstemp` + `rename`).
- DGX-side numbers come from **one** VictoriaMetrics instant query per refresh (~25 ms on
  the LAN), reused from cache for `DGX_SL_TTL` (4 s). The query is a `{__name__=~"…"}`
  selector joined with `or` to `up{job=~"vllm|lmcache"}` and two inline series
  (`dgx_sl:gen_rate1m`, `dgx_sl:ttft_n30m`). Inline series carry an extra `sl` label because
  PromQL `or` matches label sets ignoring metric names — an unlabeled series would collide
  with an unlabeled recording rule and be dropped. The query bypasses HTTP(S)_PROXY on
  purpose: the launcher exports `HTTPS_PROXY` pointing at the local mitmproxy.
- Session-scoped numbers (tokens, composition, last-turn rate) come from Claude Code's own
  transcript (`transcript_path`), so they work identically on both lanes. Parsing is
  incremental (only new complete lines; 512 KB per refresh, but a single longer line is
  always finished — lines reach 1.36 MB), deduplicated by API message id (Claude Code
  writes one line per content block and repeats the message's `usage` on every line).

## Row 1 — session & lane

| Widget | Example | Measures | Source / rule | DGX lane | ANTH lane |
|---|---|---|---|---|---|
| Lane pill | `◨ DGX` / `◨ ANTH` / `◨ ?` | Which backend serves this session's **main** model | stdin `model.id` starts with one of the launcher's `LOCAL_MODEL_PREFIXES` (same env, parsing and case-sensitive rule as `dgx_proxy.py`). Grey `?` before the first API call or when the env is unset. Exception: the proxy also sends a Sonnet request that declares an Anthropic server tool (web search/fetch, code execution) to Anthropic — the pill does not see that (0 occurrences in 9,927 requests, Nov 10–13). Background Haiku calls always go to Anthropic regardless | cyan | magenta |
| Model | `Sonnet 5.5` | Claude Code's display name for the session model | stdin `model.display_name` → `model.id`. **On the DGX lane this is the alias Claude Code believes in, not the served model:** vLLM serves GLM-5.3 Flash (dealigned; experts NVFP4, rest BF16, KV FP8) as `claude-sonnet-5-5` (backlog RESUME TODO #29) | alias | accurate |
| Branch | `⎇ main` | Git branch (short SHA when detached) | Walks up from `workspace.project_dir` — the directory Claude Code was **started** in, by design (a non-repo start dir such as `home-lab` shows no branch) — to the filesystem root; a directory counts only if its `.git` (dir or worktree pointer) holds `HEAD`. Cached 5 s | same | same |
| Project | `home-lab` | Basename of the start directory | `project_dir` → `current_dir` → `cwd`, normalized (trailing slash ignored; root shows `/`). Equals the ledger/Grafana `project` label (launcher `basename "$PWD"`); a symlinked start dir may differ | same | same |
| Context thermometer | `▰▰▰▰▱▱▱▱▱▱ 43%/1.0M` | How full Claude Code believes the context window is | stdin `context_window.used_percentage` verbatim (= (input + cache_creation + cache_read) ÷ window, output excluded — official docs) and `context_window_size`. 10 cells, halves round up. Number plain ≤ 50%, heat-colored above, **bold red from 85%**: Claude Code auto-compacts a native-1M model at ~967K (~96.7%), so 85% leaves ~117K tokens (~10 heavy turns) to compact or wrap deliberately | served-model tokens | Anthropic tokens |
| Composition `▤❙◈` | `▤30% ❙50% ◈20%` | What the current context is made of, by bytes | Transcript: ▤ tool results, ❙ conversation (text + tool-call arguments), ◈ thinking text **as stored** (often empty — signature only — so ◈ is understated). **Restarts at every `compact_boundary`** (compaction appends; the file never shrinks). Images count 2,000 bytes, also inside tool results. System prompt and tool definitions are not in the transcript | same | same |
| Cache hit `♻` | `♻ 96%` | Share of this session's input tokens served from cache | Claude Code's `prompt_cache.hit_ratio` on **both** lanes. On the DGX lane vLLM (`--enable-prompt-tokens-details`) reports per-request `cache_read_input_tokens` = GPU prefix-cache hits **+** LMCache/host-tier hits (`PrefillStats`), so this is the DGX's cache rate for your requests; only whole 8,576-token blocks hit. A session that switches lanes blends both. (Until 2026-11-13 the DGX lane showed vLLM's box-wide GPU-only ratio — ~0% under LMCache.) Box-wide view: Grafana vLLM panel 10 | DGX cache, this session | Anthropic cache |
| Lines `▲▼` | `▲870/▼351`, `▲184k/▼97k` | Lines added/removed this session | stdin `cost.total_lines_added/removed`; exact below 10,000, then `k`, then `M` | same | same |
| Timer `⏱` | `⏱ 33m`, `⏱ 1h15m` | Wall-clock age of the session, idle included | stdin `cost.total_duration_ms`; shown after 1 min | same | same |
| Tokens | `↑33.2M ↓156k ⟳32.9M ✍308k` | **Session totals** of the main transcript | Each API message counted once: ↑ input + cache-creation + cache-read, ↓ output, ⟳ cache reads, ✍ cache writes. ✍ equals Claude Code's own `prompt_cache.cache_write_tokens` exactly (cross-check). Subagents write their own transcripts and are not included. (Claude Code's `context_window.total_*_tokens` are the **last** API response, not the session — not used here) | yes | yes |
| Cost `$ ⛏` | `$2.10 ⛏0.09`, `$13.78 ⛏n/a` | `$` = Claude Code's list-price session cost; `⛏` (DGX lane only) = the same session tokens at the owned-hardware **cash** basis | `$`: stdin `cost.total_cost_usd` (client-side list price; includes subagents and background calls). Bands: grey < $1 (a short session), white $1–5, yellow ≥ $5 (about a long Opus session). `⛏` = (↑ + ↓) × `dgx_cost:dgx_usd_per_mtok` ÷ 1M, where the basis = monthly capital + power ÷ trailing-24 h DGX-lane token rate. **`⛏n/a` below 30.4 MTok/month** (1M DGX-lane tokens in 24 h): there is no representative utilization to divide by (a quiet day drove the basis to $3.47M/MTok; backlog TODO #30). At low utilization ⛏ ≫ $ is real: Anthropic bills cache reads at $0.10–0.20/MTok, the DGX's cash cost spreads over every processed token | `$` + `⛏` | `$` only |
| Limits | `5h78% ->1h23m 7d12%`, `7d85% ->3d04h` | Anthropic plan windows (5-hour, 7-day) | stdin `rate_limits.{five_hour,seven_day}`; last-seen values kept 30 min so they don't blink, but a window whose `resets_at` has passed is dropped (as Claude Code does). Grey ≤ 70%, yellow > 70% (pace yourself / plan around the reset), red > 90% (throttling imminent). The binding window gets a countdown past 70%: `->Nm`, `->HhMMm`, or `->DdHHh` beyond a day. Hidden for API-key sessions or when all Claude models are rerouted (bare `claude` prefix) | yes | yes |

## Row 2 — GB300 telemetry strip

The whole box (every client, incl. benchmarks), except `»mine`. Identical on both lanes —
while you work on `◨ ANTH`, the strip keeps showing what the Flash box is doing.

| Widget | Example | Measures | Source / rule |
|---|---|---|---|
| Health dot | `◉` / `◉ vLLM down` / `◉ LMCache down` / `◌ DGX ?` | Metrics fresh **and** serving up | Green: VM sample < 15 s old and serving healthy. Yellow `◉ … (~Ns old)`: last-known values up to 5 min. **Red `◉ vLLM down`**: `up{job="vllm"}` = 0, or no vLLM series at all. **Red `◉ LMCache down`**: vLLM runs the LMCache connector (`vllm:lmcache_mp_lookup_duration_seconds` present) and `up{job="lmcache"}` = 0 — not raised under native offload, where that job is down by design. Red `◌ DGX ?`: nothing known for > 5 min |
| Queue | `r2·q0` | vLLM requests running · waiting | Yellow when **anything waits** (`q > 0`, incl. `r0·q>0` = stalled scheduler) or **any** preemption in the last 5 min (`dgx_preempt:rate5m > 0`) — the capacity contract fails on a single preemption. Yellow, not red: "waiting" also holds requests briefly loading from LMCache at admission |
| KV gauge | `KV▰▰▰▰ 92% ↺host 80%` | GPU KV blocks held by **running** requests (not occupancy) and, when > 0.5%, the share of reused history served from the host tier | `vllm:kv_cache_usage_perc` — **hidden when missing** (no invented 0%). 4 cells by ceiling quarters: 0% empty, 1–25 / 26–50 / 51–75 / 76–100 → 1–4 cells (healthy busy operation, 85–96%, is a steady full bar). `↺host` = `dgx_kv:host_hit_share` (host tier = native offload **or** LMCache L1; vLLM credits both as external hits). Yellow when host share > 5% (THRESHOLDS §8b: measured cliff 0% ≤ 12 agents, 80% at 13; measured under native offload — re-validate from C4) |
| Throughput | `»113t/s` · `▣120t/s` | Two separate numbers (owner decision 2026-11-14): **»** = your speed, **▣** = the DGX box | **»mine** = this session's **last completed API call**, output tokens ÷ (triggering line → its last line), from the transcript — **both lanes**, prefill included. Replies < 200 tokens are shown **dimmed** (latency-dominated). Spans longer than 4 × out/15 (effective < 3.75 tok/s) are skipped as measurement errors (the trigger line is not the real request); the previous value stays. Known edge: a very long prefill with a short reply is skipped too. Replay 2026-11-13: DGX median 81 / p95 114, Anthropic median 85 / p95 115 tok/s. **▣box** = every DGX client's vLLM output tok/s over **1 minute** (`sum(rate(vllm:generation_tokens_total[1m]))`, the series the sparkline plots; 5-min `dgx_tokens:gen_rate5m` as fallback), benchmarks and probes included. They are **not comparable**: one stream vs the sum of all streams — `»121` beside `▣12` (fast stream, idle box) and `»27` beside `▣350` (13 busy agents) are both normal; on the Anthropic lane they are unrelated |
| Sparkline | `▅▅▆▆▇▇██` (after `▣`) | History of one DGX box signal (both lanes) | `DGX_SL_TRACE`: `rate` (default, box tok/s over **1 minute**), `kv` (GPU KV fraction, fixed 0–100% scale), `ttft` (p95). **Zero-anchored**: height ∝ value ÷ window max (floors 1 tok/s, 0.1 s), so a 0.3% drift stays flat and a doubling looks like one. Last ≤ 12 samples ≥ 2 s apart — about 48 s at the 4 s fetch. Amber cells = any preemption in the last 5 min. Real observations only; hidden on the stale path. A session-following `turns` trace is backlog TODO #31 |
| Latency | `◔2.2s`, `◔116s`, `◔max 0.1s` | TTFT p95 over 30 min, all requests (incl. benchmarks and synthetic probes) | `dgx_ttft:p95_30m`. With **fewer than 20 requests** in the window the "p95" is the slowest request, so it shows dimmed as `◔max …` and never turns yellow. Yellow > 8 s otherwise (THRESHOLDS §8b). Integer seconds from 10 s (buckets there are 20/40/80/160/640/2560 s). NaN hides it |
| Power | `⚡207W·349W 36° 4¢/h` | GPU watts · whole-box wall estimate · GPU temperature · cost per hour | `⚡207W` = GB300 (`DCGM_FI_DEV_POWER_USAGE`, neutral). `·349W` = `dgx_power:est_wall_watts` = (GB300 + Grace socket) × 1.25 fill factor (fans/NVMe/BMC unmeasured; CPU and SysIO are sub-rails of Grace, not added) — **this number carries the color**: yellow > 1,280 W, red > 1,520 W (80% / 95% of the 1,600 W rating, THRESHOLDS §8b). `36°` = `DCGM_FI_DEV_GPU_TEMP` (no threshold: DCGM exports no slowdown limit). `¢/h` = wall ÷ 1000 × `dgx_power:rate_usd_per_kwh` (local utility $0.12, $0.14 Jun–Sep; ECONOMICS-BRIEF) |
| Idle | `☾ idle 6m`, `☾ idle 18h20m`, `☾ idle 3d04h` | Time since any Claude Code session last sent a request to the DGX lane | `now − dgx_llm_last_dgx_request_timestamp_seconds`; shown when > 5 min (longer than a normal think/tool gap — a judgment call meaning "nobody is actively using the DGX lane") **and** nothing runs on vLLM. Benchmarks bypass the proxy, so they don't reset it |

## Agent-panel subagent rows (`--subagent`)

The launcher also passes `subagentStatusLine` (same script, `--subagent`), which rewrites
the row bodies in Claude Code's agent panel.

**Version note:** this works in Claude Code **≤ 2.1.322** (all sessions running on
2026-11-14). **2.1.323 removed it** — its schema reads "Deprecated: no longer has any
effect. Subagent rows always use the default look", and the runtime caller is gone. Sessions
started on 2.1.323 show default rows; the setting is then inert (RESUME TODO #32). The
contract is not in the public docs; it was read from the 2.1.322 bundle.

Contract (2.1.322): stdin = session fields + `columns` + `tasks[]`, each with `id, name, type,
agentType, status, description, label` (live progress summary, else description), `startTime`
(ms), `model, effort, contextWindowSize, tokenCount, tokenSamples` (last 16) and `cwd`. No end
time; finished rows stay in the panel for a while. Output = one `{"id": …, "content": …}` JSON
line per row; omitted rows keep the default body; 5 s timeout; a non-zero exit drops all
custom rows; skipped before workspace trust.

| Element | Example | Source |
|---|---|---|
| Status glyph + name | `» fix-auth` | `status` (`»` running, `✔` completed, `✘` failed, `◍` other) and `name` → `label` → `description` → `agentType` |
| Lane + model | `◨DGX claude-sonnet-5-5` | `model`, tagged with the same prefix rule as the main lane pill |
| Tokens | `12.4k tok` | `tokenCount` |
| Elapsed | `02:11` | `now − startTime`, **running rows only** (no end time is sent) |
| Status text | `completed` | non-running rows |

## Both-lane support matrix

| Concern | DGX lane | ANTH lane |
|---|---|---|
| Context numerator | served-model tokens from vLLM usage | Anthropic usage |
| `♻` cache ratio | CC `prompt_cache` (vLLM GPU + LMCache hits) | CC `prompt_cache` |
| Tokens, composition, last-turn rate | transcript | transcript |
| `⛏` owned-hardware cost | yes (n/a below the utilization floor) | — |
| Telemetry strip | live DGX | live DGX (unchanged) |

## Tunables

| Env | Default | Meaning |
|---|---|---|
| `DGX_SL_VM_URL` | `http://192.0.2.10:8428` | VictoriaMetrics base URL |
| `DGX_SL_TTL` | `4` | Seconds between real VM fetches (match refreshInterval) |
| `DGX_SL_ROWS` | `2` | 1 = row 1 only; > 2 = force row 2 even on narrow terminals (< 72 cols drops it) |
| `DGX_SL_SPARK` | `1` | `0` disables the sparkline |
| `DGX_SL_TRACE` | `rate` | Sparkline signal: `rate`, `kv`, `ttft` (`mine` retired → `rate`) |
| `DGX_SL_GIT` | `1` | `0` disables the git branch segment |

Launcher side: `DGX_STATUSLINE=0` omits both settings entirely.

## Troubleshooting

- **Blank status line:** the command exited nonzero or printed nothing. Run
  `claude --debug` in a session — stderr from the status line is logged there.
- **Nothing until trust:** the workspace-trust dialog must be accepted first; CC
  skips the status line before that (`Status line command skipped: workspace trust
  not accepted` under --debug).
- **`◌ DGX ?` for a while:** the DGX or its VM is unreachable from the laptop. Check
  `curl --noproxy '*' http://192.0.2.10:8428/api/v1/query?query=up`.
- **`◉ vLLM down` / `◉ LMCache down`:** the named scrape target is down — check
  `sudo docker ps` on the DGX before assuming the status line is wrong.
- **`☾ idle` stuck on / absurd age:** the ledger exporter froze or its `ssh -R` tunnel is
  down. Check `launchctl list | grep dgx`; restart with
  `launchctl kickstart -k gui/$(id -u)/io.hylo.ledger-exporter`.
- **Agent-panel rows look default:** the session runs Claude Code ≥ 2.1.323 (see the
  version note above).
- **Reset per-session state:** delete `~/.cache/dgx-llm/statusline-*<session_id prefix>*.json`.
