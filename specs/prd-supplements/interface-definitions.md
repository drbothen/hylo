---
document_type: prd-supplement-interface-definitions
level: L3
version: "1.7"
status: draft
producer: product-owner
timestamp: 2026-11-18T12:00:00Z
phase: 1a
stage: "3 of 3 (integration)"
inputs: [prd.md]
input-hash: "035b9a1"
traces_to: prd.md
---

# Interface Definitions: hylo P1 statusline

> PRD supplement — extracted from PRD Section 3.
> Referenced by: implementer, test-writer, devops-engineer.
> Every entry traces to a behavioral contract; the contract wins on any conflict.

## CLI Interface

```
hylo statusline                     # render 1-2 lines from the statusLine stdin payload
hylo version                        # print "hylo <version>"
hylo config validate                # exit 0 + "hylo: config ok", or exit 1 + plain reasons
hylo config path [--config <path>]  # print config, cache and state paths, one per line (OD-132)
```

- Global flag: `--config <path>` is accepted by `config path` only (override; `~` expanded,
  OD-61/OD-101). `hylo statusline` otherwise takes no flags in P1: any argument starting
  with `-` is an unknown-flag error (OD-112), except a bare `-` (positional) and a bare
  `--`, which ends the flag scan (trailing arguments ignored by the SCAN only).
  `--subagent` is a ported P1 flag (OD-155, superseding OD-14): the exact argv element,
  matched ANYWHERE in the statusline argument slice — at any index, including after a
  bare `--` (pass-3 A01: `hylo statusline -- --subagent` routes to the panel) — selects
  the subagent panel renderer before any flag scan or config processing, gated by
  `statusline.subagent.enabled` (default true; BC-1.07.001..008). On the subagent path
  config IS resolved (OD-168): a config error there emits ZERO bytes on stdout and the
  error line on stderr, exit 0 (pass-3 A02; entry point and owner per ARCH-01
  `runStatuslineSubagent`).
- Dispatch contract: BC-4.01.001; version fallback chain: BC-4.01.003; config path
  resolution order (--config, then `HYLO_CONFIG`, then per-OS default): BC-2.03.002.

## Exit Code Semantics

| Code | Meaning | When | Contract |
|---|---|---|---|
| 0 | Success / degraded-success | every `statusline` render (including degraded ladder, config-error line, unknown-flag line); `version`; `config path`; `config validate` when valid | BC-1.01.001, DI-008 |
| 1 | Validation failure | `config validate` on an invalid configuration | BC-2.03.001 |
| 2 | Usage error | bad arguments/flags on `version`/`config validate`/`config path`; golden text `cmd/hylo/testdata/usage.golden` | BC-4.01.001, BC-2.03.001 |
| non-zero | Harness only | parity-harness integrity failures (canary, missing table test, bad exclusion id) — never in `hylo` itself | BC-6.01.003, BC-6.03.004 |

## stdin JSON Contract (statusline)

- One JSON object, text-mode `json.load` semantics (BC-1.01.002): leading/trailing
  whitespace allowed; BOM or invalid UTF-8 -> decoded as `{}` and the render continues
  (BC-1.01.008); `NaN`/`Infinity`/`-Infinity` tokens accepted (ModeText values, BC-5.02.003
  invariant 3); trailing data -> `{}`; non-object top level -> `{}`.
- Recursion budget is per call site, governed by **limit = 999 − (Python frames from
  `<module>` down to `json`'s raw_decode)**, measured end to end on the real legacy
  program with isolated HOME (orchestrator, 2026-11-17; supersedes the earlier
  frame-local 989/990 probe, which does not transfer across invocation depths).
  Measured: stdin (main → json.load, 6 frames) 993 accepted / 994 rejected;
  transcript lines (main → _mix_counts → json.loads, 6 frames) 993/994; session cache
  (main → effective_rl → load_cache, 8 frames) 991/992; git cache (main → render_lane →
  git_segment → load_cache, 9 frames) 990/991. Derived from equal chain depth: the
  get_sample, claude_window_start and mix-cache loaders (8 frames) 991/992; the
  cost-history loaders record_cost and cost_thresholds, called from render_lane
  (9 frames) 990/991. Boundaries are call-context dependent (ADV-P1-B17) and pinned by
  the recorded measurement recipes; there is no single budget and no per-mode budget
  (full table and recipes: VP-006; ADV-P2-A07 closed).
- Objects read: `model` (`.id`, `.display_name`), `workspace` (`.current_dir`, `.repo.*`),
  `transcript_path`, `session_id`, `cost` (`total_duration_ms`), `rate_limits`
  (`.windows`, `.spend_limit` with and without dollar fields), `version`, plus the newer
  optional fields `output_style.name`, `pr.kind`, `prompt_cache.last_miss_cause`/`miss_causes`
  (market-intel §6.1). Any field may be absent or null; wrong inner types degrade per the
  CP-S01..S17 register, never fail (BC-1.02.x, BC-1.03.015).

## Output Byte Contract (statusline stdout)

- Happy path: exactly 1 or 2 lines joined with `\n` and terminated by `\n` (BC-1.01.003);
  visible width from code points after SGR stripping (BC-1.01.004); trim per
  BC-1.01.006/.010.
- Degraded: exactly `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 (BC-1.01.001).
  The grey/reset SGR pair is the built-in named constant `\e[90m` / `\e[0m`, independent
  of `statusline.theme.*` (OD-113; BC-2.02.001 invariant 2), because the theme itself may
  be the invalid value on a config-error run.
- Config error: `\e[90mhylo: config error: <key>=<value> (<reason>)\e[0m\n`, exit 0;
  stderr carries `hylo: config error: <key>=<value> (<reason>) [from <ENVNAME>]` per
  error in registry order (BC-2.02.001). No cache writes on a config-error run.
- Unknown flag: `\e[90mhylo: unknown flag <flag>\e[0m\n` (first flag); stderr
  `hylo: unknown flag <flag> (hylo statusline takes no flags)` per flag; checked before
  config resolution (BC-4.01.002).
- Side-effect order on a degrade: legacy order preserved; earlier writes kept (BC-1.01.009).

## HYLO_* Key Schema (P1 subset)

Naming (BC-2.01.004): dotted lower-snake key names matching
`^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*|\[[0-9]+\])*$`; `EnvName(key)` = `HYLO_` + upper snake
with every `.`, `[`, `]` run collapsed to one `_`. Grammar per type: typed bool
(case-sensitive `true|false|1|0|yes|no`), comma lists (OD-74), `~` expansion in paths
(OD-61, `~user` left as written), COLUMNS excluded as protocol input (BC-2.01.005).
Full registry (every key: type, range, default, unit, op, rationale, rationale code):
BC-2.01.004 + golden `internal/config/testdata/legacy_defaults.golden`.

Representative keys (families enumerated in design §2.4; amended by OD-113, OD-123):

| Key | Type | Default | Range / op | Rationale (code) | Contract |
|---|---|---|---|---|---|
| `statusline.rows` | Int | 2 | any int64 (legacy semantics for negative and large values); row 2 shown when `rows >= 2` | DOC | BC-1.01.003, BC-1.04.013, BC-2.02.003 |
| `statusline.narrow_cols` | Int | 72 | any Int (comparison-total `cols >= narrow_cols` gate — non-negative and negative gate values both gate total, pass-3 B08) | J (T-014) | BC-1.01.003 |
| `statusline.git.enabled` | Bool | true | on/off segment gate | DOC | BC-1.02.005 |
| `statusline.git.ttl_s` | Seconds | 5 | any finite number; `< 0` (and any negative) means "never fresh": the git cache is always recomputed — behavior legacy defines (SL:99-100), so negatives are admitted (pass-3 B08) | C (T-013) | BC-1.02.005 |
| `statusline.telemetry.ttl_s` | Seconds | 4 | finite, `>= 0`, `<= 9223372036.854775`; strict `fetch_ts > now - ttl` | DOC (T-001) | BC-1.04.002, BC-2.02.002 |
| `backends[0].metrics_url` | URL | `http://192.0.2.10:8428` | scheme http(s), host present | OWNER (OD-123) | BC-2.01.002, BC-2.02.005 |
| `backends[0].model_prefixes` | List | `claude-sonnet` | comma list; startswith match | OWNER (OD-111/123) | BC-2.01.002, BC-1.02.001 |
| `paths.cache_dir` | Path | per-OS hylo cache dir | not the legacy literal (exception) | OWNER (OD-101) | BC-3.01.001 |
| `statusline.theme.reset` | SGR | `0` | SGR parameter list (non-list = config error, BC-2.01.003) | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.dim` | SGR | `2` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.bold` | SGR | `1` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.white` | SGR | `97` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.cyan` | SGR | `36` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.green` | SGR | `32` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.yellow` | SGR | `33` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.red` | SGR | `31` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.grey` | SGR | `90` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.magenta` | SGR | `35` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.boldred` | SGR | `1;91` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.pill_local` | SGR | `106;30;1` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.pill_cloud` | SGR | `105;30;1` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.pill_unknown` | SGR | `100;37;1` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.separator` | Text | ` · ` (U+00B7) | free text, no control bytes (control byte = config error, BC-2.01.003 PC-3) | DOC (OD-113) | BC-2.01.003 |
| `statusline.window_age.process_name` | Text | `claude` | non-empty, no control bytes; exact basename match (Windows `.exe` stripped) | OWNER (OD-133) | BC-3.02.001/.002 |
| `statusline.sparkline.trace` | Enum | `rate` | `rate\|kv\|ttft` (legacy `mine` retired) | DOC | BC-2.02.004 |
| `statusline.context.cells` | Int | 10 | `>= 1` (BC-1.02.006 PC3-PC5 define the widget for any cell count — `d=100/n`, `min(…,n)`, a loop over n cells — so non-default values are definable; pass-3 B07) | J (T-027..T-029) | BC-1.02.006 |
| `statusline.context.plain_max` | Int | 50 | any Int (comparison-total `min(…,n)` gate; BC-1.02.006 PC3-PC5; pass-3 B07) | DOC | BC-1.02.006 |
| `statusline.context.red_from` | Int | 85 | any Int (band threshold; BC-1.02.006 PC3-PC5; pass-3 B07) | DOC | BC-1.02.006 |
| `statusline.units.context` | Text | `K` | default-only: range = {`K`}; registered semantics `1e6` → `M`, else `K` | DOC | BC-1.02.006 |
| `statusline.units.lines` | Text | `k`/`M` | default-only: range = {`k`/`M`}; thresholds 10,000 (`>=` → k), 1,000,000 (`>=` → M) | DOC | BC-1.02.014 |
| `statusline.units.tokens` | Text | `k`/`M` | default-only: range = {`k`/`M`}; thresholds 1,000 (`>=` → k), 1e6 (`>=` → M) | DOC (T-042) | BC-1.02.025 |
| `statusline.theme.heat` | Text | 0.22/0.85/0.80 | three finite Floats, hue span `> 0`, saturation/value in `[0, 1]` (BC-1.02.019 PC defines the HSV gradient for non-default triples; pass-3 B07) | DOC (T-030) | BC-1.02.019 |
| `statusline.transcript.read_cap_bytes` | Int (bytes) | 524288 | `>= 1` | J (T-054) | BC-1.03.003 |
| `statusline.transcript.dedup_memory` | Int | 256 | `>= 1` | Dv (T-060) | BC-1.03.005 |
| `statusline.transcript.rebuild_excess` | Int | 20000 | `>= 0` | M (T-056) | BC-1.03.007 |
| `statusline.composition.image_chars` | Int | 2000 | `>= 0` | J (T-059) | BC-1.03.009 |
| `statusline.turn.dim_below_out` | Int | 200 | `>= 0`; dim gate compares the last turn's output **token count** (`out < TURN_DIM_OUT`), not a rate | DOC (T-055) | BC-1.03.010 |
| `statusline.turn.floor_tps` | Float | 15.0 | `> 0` (finite) | DOC (T-057) | BC-1.03.010 |
| `statusline.turn.stale_factor` | Float | 4.0 | `> 0` (finite) | J (T-058) | BC-1.03.010 |
| `statusline.kv.cells` | Int | 4 | `1..100` — upper bound 100 is a labeled judgment call (J): caps the O(cells) render work and visible-width blowup far beyond any terminal used with the status line, keeping the 25 ms p95 budget; the T-codes justify the DEFAULT, not the bound (pass-3 A27; cell formula defined for C ≥ 1; non-default behavior defined in BC-1.04.007) | Dv (T-048) | BC-1.04.007 |
| `statusline.queue.yellow` | Bool | true | both booleans defined: `true` = rule `q > 0 or preempt > 0`, `false` = never yellow (BC-1.04.006) | Dv (T-047) | BC-1.04.006 |
| `statusline.sparkline.points` | Int | 12 | `1..100` — upper bound 100 is a labeled judgment call (J), same rationale as `kv.cells`: caps O(points) render work and segment width within the 25 ms p95 budget; the T-code justifies the default, not the bound (pass-3 A27) | J (T-006) | BC-1.04.009 |
| `statusline.sparkline.history_cap` | Int | 32 | `>= 1` | Dv (T-009) | BC-1.04.003/.009 |
| `statusline.sparkline.scale` | Float (triple) | k-top 1.0; v-floor 1.0, f-floor 0.1; other 1e-9 | each value finite `> 0` | Dv (T-045) | BC-1.04.009 |
| `statusline.cost.min_sessions` | Int | 10 | `>= 1` (0 raises IndexError on an empty list in legacy, SL:261) | OWNER (T-020) | BC-1.05.005 |
| `statusline.cost.percentiles` | Float pair | (0.75, 0.95) | each a finite Float in `[0, 1]`, ASCENDING pair: `p75 <= p95` is ratified — a descending pair is a number-range config error (pass-3 C2-07; ratified in
BC-1.05.005 on its own grounds — index overflow and negative wrap — not mirrored
from the limits bands, whose chained red-first comparison is comparison-total for
any finite pair, so no ordering constraint is ratified there) | OWNER (T-024) | BC-1.05.005 |
| `statusline.cost.min_usd` | Float | 1.0 | finite `>= 0` (grey test strict `<`) | Dv (T-019) | BC-1.05.001 |
| `statusline.cost.cold_yellow_usd` | Float | 25.0 | finite `>= 0` (cold test inclusive `>=`) | OWNER (T-021) | BC-1.05.001 |
| `statusline.idle.running_below` | Float | 1 | finite `>= 0`, NaN rejected | DOC (T-108) | BC-1.04.012 |
| `statusline.subagent.enabled` | Bool | true | on/off panel gate, default = legacy (OD-155) | OWNER (OD-155) | BC-1.07.002 |
| `statusline.subagent.glyphs.running` | Text | `\u00bb` (U+00BB) | non-empty, no control bytes (one-line output invariant; mirrors BC-2.01.003 PC-3) | J (OD-02; SL:845-846) | BC-1.07.005 |
| `statusline.subagent.glyphs.completed` | Text | `\u2714` (U+2714) | non-empty, no control bytes (as above) | J (OD-02; SL:845-846) | BC-1.07.005 |
| `statusline.subagent.glyphs.failed` | Text | `\u2718` (U+2718) | non-empty, no control bytes (as above) | J (OD-02; SL:845-846) | BC-1.07.005 |
| `statusline.subagent.glyphs.killed` | Text | `\u25cd` (U+25CD) | non-empty, no control bytes (as above) | J (OD-02; SL:845-846) | BC-1.07.005 |
| `statusline.subagent.colors.running` | SGR | `33` (= `statusline.theme.yellow`) | SGR parameter list (class per BC-2.01.003; legacy YELLOW) | J (OD-02; SL:131-132, 845-846) | BC-1.07.005 |
| `statusline.subagent.colors.completed` | SGR | `32` (= `statusline.theme.green`; legacy GREEN) | SGR parameter list (as above) | J (OD-02; SL:131-132, 845-846) | BC-1.07.005 |
| `statusline.subagent.colors.failed` | SGR | `31` (= `statusline.theme.red`; legacy RED) | SGR parameter list (as above) | J (OD-02; SL:131-132, 845-846) | BC-1.07.005 |
| `statusline.subagent.colors.killed` | SGR | `90` (= `statusline.theme.grey`; legacy GREY) | SGR parameter list (as above) | J (OD-02; SL:131-132, 845-846) | BC-1.07.005 |
| `statusline.subagent.joiner` | Text | `\u0020\u00b7\u0020` (space, U+00B7, space) | free text, no control bytes (control byte = config error, BC-2.01.003 PC-3) | DOC (SL:924) | BC-1.07.004 |
| `statusline.subagent.tokens.k_from` | Float | 1000 | finite `> 0`; ascending pair `k_from <= m_from` (OD-162 every-key-has-a-range; pass-3 A14/C05) | DOC (T-042) | BC-1.07.007 |
| `statusline.subagent.tokens.m_from` | Float | 1000000 | finite `> 0`; ascending pair `k_from <= m_from` (as above) | DOC (T-042) | BC-1.07.007 |
| `statusline.limits.keep_s` | Seconds | 1800 | finite `> 0` (`<` age gate, comparison-total in legacy; pass-3 A05) | J (T-010, owner group A) | BC-1.02.013, BC-1.02.030 |
| `statusline.limits.windows` | List | `5h/7d` | default-only: range = {`5h/7d`} (window lengths 18000 s / 604800 s; non-default selectors undefined) | DOC (T-031, Anthropic convention) | BC-1.02.010, BC-1.02.024 |
| `statusline.limits.countdown_max_factor` | Float | 1.15 | any finite number (multiplier in the `<=` countdown gate) | DOC | BC-1.02.012 |
| `statusline.limits.projection_min_elapsed` | Float | 0.10 | any finite number (`>=` elapsed-fraction gate) | DOC (T-032) | BC-1.02.011, BC-1.02.024 |
| `statusline.limits.projected_bands` | Float pair | red > 100, yellow >= 80 | each a finite Float (band comparison) | DOC (T-033) | BC-1.02.011, BC-1.02.024 |
| `statusline.limits.absolute_bands` | Float pair | red > 90, yellow > 70 | each a finite Float (band comparison) | DOC (T-034) | BC-1.02.011, BC-1.02.024 |
| `statusline.timer.min_ms` | Int | 60000 | any Int (comparison-total display gate, operator `>`) | DOC (T-038) | BC-1.02.015 |
| `statusline.timer.api_min_ms` | Int | 60000 | any Int (operator `>=`) | DOC (T-039) | BC-1.02.016, BC-1.02.027 |
| `statusline.cost.window_s` | Seconds | 2592000 (30 d) | finite `> 0` (history filter; pass-3 A05) | OWNER (T-018) | BC-1.05.005 |
| `statusline.cost.record_throttle_s` | Seconds | 60 | finite `> 0` (strict `<` throttle; pass-3 A05) | Dv (T-022) | BC-1.05.004 |
| `statusline.cost.rate_min_api_ms` | Int map | `{cc: 300000, other: 1800000}` | each value any Int (ratio gate) | Dv (T-023) | BC-1.05.005 |
| `statusline.cost.burn_min_api_ms` | Int | 300000 | any Int (ratio gate) | Dv (T-043) | BC-1.05.002 |
| `statusline.cost.basis_min_shown_usd` | Float | 0.005 | finite Float (operator `>=`) | Dv (T-044) | BC-1.02.029 |
| `statusline.cost.basis_min_mtok_month` | Float | 30.4 | finite Float (operator `>=`) | Dv (T-012) | BC-1.02.029, BC-1.05.003 |
| `statusline.telemetry.query` | Text | legacy `QUERY` literal (SL:102-123, byte-pinned golden) | any text (percent-encoded into the URL; upstream errors degrade per the CP-S register) | DOC | BC-1.04.001 |
| `statusline.telemetry.timeout_s` | Seconds | 1.5 | finite Float > 0 (HTTP client timeout; <= 0 not legacy-covered) | J (T-005) | BC-1.04.001 |
| `statusline.telemetry.fresh_s` | Seconds | 15 | finite `> 0` (freshness comparison; pass-3 A05) | Dv (T-003) | BC-1.04.004 |
| `statusline.telemetry.keep_dead_s` | Seconds | 300 | finite `> 0` (retention comparison; pass-3 A05) | J (T-004) | BC-1.04.002 |
| `statusline.ttft.min_samples` | Int | 20 | any Int (sample-count gate; below it p95 = max) | Dv (T-015) | BC-1.04.010 |
| `statusline.ttft.integer_from_s` | Seconds | 10 | finite `> 0` (histogram-bucket threshold; pass-3 A05) | Dv (T-051) | BC-1.04.010 |
| `statusline.ttft.yellow_s` | Seconds | 8 | finite `> 0` (colour-band threshold; pass-3 A05) | M (T-052) | BC-1.04.010 |
| `statusline.idle.after_s` | Seconds | 300 | finite `> 0` (idle comparison; pass-3 A05) | J (T-011) | BC-1.04.012 |
| `statusline.power.wall_red_w` | Watts (Int) | 1520 | any Int (band comparison) | Dv (T-053) | BC-1.04.011 |
| `statusline.power.wall_yellow_w` | Watts (Int) | 1280 | any Int (band comparison) | Dv (T-053) | BC-1.04.011 |
| `statusline.window_age.min_margin_ms` | Milliseconds (Int) | 300000 | any Int (margin comparison) | OWNER (T-040, owner request) | BC-1.02.017 |
| `statusline.window_age.max_depth` | Int | 6 | any Int (ancestor-walk cap) | DOC (T-025) | BC-3.02.001 |
| `statusline.kv.host_shown_pct` | Float | 0.5 | finite Float (display gate) | Dv (T-050) | BC-1.04.007 |
| `statusline.kv.host_yellow_pct` | Float | 5 | finite Float (band threshold, THRESHOLDS §8 SL:746) | M (T-049) | BC-1.04.007 |
| `statusline.sparkline.enabled` | Bool | true | both booleans defined: `false` hides the sparkline (legacy `DGX_SL_SPARK != "0"`) | DOC | BC-1.04.008, BC-2.01.005 |
| `statusline.sparkline.max_age_s` | Seconds | 90 | finite `> 0` (gap-pruning comparison; pass-3 A05) | Dv (T-007) | BC-1.04.003 |
| `statusline.sparkline.min_gap_s` | Seconds | 2 | finite `> 0` (gap guard; pass-3 A05) | Dv (T-008) | BC-1.04.003 |
| `statusline.sparkline.colors` | RGB triples + Float | trail (70,170,190), fade 0.55..1.0, amber (220,170,60), head (140,235,255) | components any Int, fade finite (presentation formatter plugs them in) | J (T-046, presentation) | BC-1.04.009 |
| `statusline.glyphs.*` (family) | Text | legacy glyph set (OD-02) | non-empty, no control bytes (one-line output invariant; mirrors BC-2.01.003 PC-3); members per BC-2.01.004 registry | J (OD-02) | BC-1.02.007/.014/.015/.017/.018/.023/.028 |

Default-only parameters (the owning BC hard-codes the formula and leaves non-default
values undefined — non-default behavior: see the BC; per OD-162 such a key's valid range
is its default value only, any other value being a number-range config error):
`statusline.units.context` (BC-1.02.006 hard-codes `pct/10`, `min(…,10)`, `range(10)`);
`statusline.units.lines` (BC-1.02.014), `statusline.units.tokens` (BC-1.02.025),
`statusline.limits.windows` (BC-1.02.010).
`statusline.context.cells`, `statusline.context.plain_max`, `statusline.context.red_from`
and `statusline.theme.heat` are NOT default-only any more: BC-1.02.006/.019 PC3-PC5 now
define non-default behavior, and their ranges are registered in the table above
(pass-3 B07). Likewise `statusline.kv.cells` (BC-1.04.007) and
`statusline.queue.yellow` (BC-1.04.006) are NOT default-only any more: both BCs now
define non-default behavior, and their ranges are registered in the table above
(pass-2 C2-04). Pass-3 A14/C05 registration: the subagent panel keys
(`statusline.subagent.glyphs.*`, `colors.*`, `joiner`, `tokens.*`) now carry registry
rows — superseding BC-1.07.005's "pin `_SUB_GLYPH` as a Go map literal" wording and
sourcing the panel's glyphs/colors/joiner/token thresholds from config (D15); the
sibling BC amendment lands with the product-owner.

OD-162 registration sweep (adv-p2 sync SC-09, 2026-11-18T05:30:00Z): every dotted key
named in a BC body now carries a row above — 48 rows added in this burst (15
`statusline.theme.*` members replacing the former family row, 32 individual tail keys,
1 `statusline.glyphs.*` family row; members of `statusline.glyphs.*` are never named
individually in BC bodies, so the family row stands). Deliberately NOT registry keys
(setting them yields only the unknown-setting warning, BC-2.01.002 PC-7, OD-123):
`statusline.telemetry.url` and `routing.local_model_prefixes`. The inert key
`statusline.window_age.ps_timeout_s` was removed by OD-147 (BC-3.02.001) and is likewise
not registered. Judgment-label calls worth owner eyes: `statusline.telemetry.timeout_s`
(finite Float > 0 — a <= 0 timeout has no legacy-covered behavior) and
`statusline.sparkline.colors` (component/float domain judged from the presentation
formatter).

Label reconciliation for `statusline.telemetry.ttl_s` (ADV-P1-A2-16 family, A2-26 audit):
the table carries **DOC (T-001)** because the governing contract's golden row
(BC-2.01.004 PC-table) pins `RationaleCode=DOC, Rationale="match refreshInterval
(legacy SL:50; T-001)"`. The pass-4 catalogue row T-001 supports "documented": its basis
is the harness's own documented `statusLine.refreshInterval` (domain research §"statusLine
settings"), i.e. an alignment with a documented constant — not a measurement (M), a
derivation (Dv) or a judgment call (J), and this supplement defers to the contract on
any conflict.

Documented default exceptions to "defaults equal legacy until cutover": the two OWNER
exceptions of BC-2.01.004 PC-4 — `paths.cache_dir` (OD-101) and `backends[0].model_prefixes`
(OD-111/OD-123); the `backends[0].metrics_url` default is not an exception (it spells the
same URL legacy serves, with the RFC 5737 placeholder). Unknown `HYLO_*` variables warn on stderr
(`hylo: warning: unknown setting <NAME> (ignored)`) and never change exit status
(BC-2.01.001).

Per-OS directories (BC-3.01.001, OD-144): relative or empty `XDG_*` values are ignored
(XDG spec); on Windows the cache and state directories are separate subdirectories
`%LOCALAPPDATA%\hylo\cache` and `%LOCALAPPDATA%\hylo\state`. `hylo config path` prints
all three resolved paths, one per line, labels and order fixed (`config:`, `cache:`,
`state:`; OD-132, BC-2.03.002) — the **effective** paths (OD-165): exactly the values
the running binary resolves, overrides honored the same way the status line honors them.

## Flag Interactions

| Flag A | Flag B | Interaction | Resolution |
|---|---|---|---|
| unknown flag | config error | unknown flag wins | flag check precedes `config.Load` (BC-4.01.002) |
| `--config <path>` | `HYLO_CONFIG` | flag overrides env | BC-2.03.002 |
| `HYLO_*` env | built-in default | env overrides default; file layer absent in P1 (OD-107) | BC-2.01.001 |
| first unknown flag | later unknown flags | first is rendered; all go to stderr | BC-4.01.002 |
| first config error | later config errors | first in registry order is rendered; all to stderr | BC-2.02.001 |
