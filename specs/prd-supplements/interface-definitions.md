---
document_type: prd-supplement-interface-definitions
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T23:59:00Z
phase: 1a
stage: "3 of 3 (integration)"
inputs: [prd.md]
input-hash: "c5b34f4"
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
  OD-61/OD-101). `hylo statusline` takes no flags in P1: any argument starting with `-` is
  an unknown-flag error (OD-112), except a bare `--` after which arguments are ignored
  (BC-4.01.002 EC-004). `--subagent` has no special handling (OD-14).
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
- Recursion budget is per call site: 993 accepted / 994 rejected at stdin (BC-1.01.002);
  989 accepted / 990 rejected on transcript lines at the `_mix_counts` site (BC-5.02.003).
  The boundaries are call-context dependent (Python-frame depth at the call site, ADV-P1-B17)
  and are pinned by the recorded measurement recipes; there is no single budget and no
  per-mode budget.
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
| `statusline.narrow_cols` | Int | 72 | row 2 kept when `cols >= narrow_cols` | J (T-014) | BC-1.01.003 |
| `statusline.git.enabled` | Bool | true | on/off segment gate | DOC | BC-1.02.005 |
| `statusline.git.ttl_s` | Seconds | 5 | `>= 0` cache TTL | C (T-013) | BC-1.02.005 |
| `statusline.telemetry.ttl_s` | Seconds | 4 | finite, `>= 0`, `<= 9223372036.854775`; strict `fetch_ts > now - ttl` | DOC (T-001) | BC-1.04.002, BC-2.02.002 |
| `backends[0].metrics_url` | URL | `http://192.0.2.10:8428` | scheme http(s), host present | OWNER (OD-123) | BC-2.01.002, BC-2.02.005 |
| `backends[0].model_prefixes` | List | `claude-sonnet` | comma list; startswith match | OWNER (OD-111/123) | BC-2.01.002, BC-1.02.001 |
| `paths.cache_dir` | Path | per-OS hylo cache dir | not the legacy literal (exception) | OWNER (OD-101) | BC-3.01.001 |
| `statusline.theme.*` (15 keys) | SGR/Text | legacy palette, pills, separator | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.window_age.process_name` | Text | `claude` | non-empty, no control bytes; exact basename match (Windows `.exe` stripped) | OWNER (OD-133) | BC-3.02.001/.002 |
| `statusline.sparkline.trace` | Enum | `rate` | `rate\|kv\|ttft` (legacy `mine` retired) | DOC | BC-2.02.004 |
| `statusline.context.cells` | Int | 10 | thermometer cell count | J (T-027..T-029) | BC-1.02.006 |
| `statusline.units.context` | Text | `K` | denominator unit: `1e6` → `M`, else `K` | DOC | BC-1.02.006 |
| `statusline.units.lines` | Text | `k`/`M` | thresholds 10,000 (`>=` → k), 1,000,000 (`>=` → M) | DOC | BC-1.02.014 |
| `statusline.units.tokens` | Text | `k`/`M` | thresholds 1,000 (`>=` → k), 1e6 (`>=` → M) | DOC (T-042) | BC-1.02.025 |
| `statusline.transcript.read_cap_bytes` | Int (bytes) | 524288 | per-refresh transcript read step | J (T-054) | BC-1.03.003 |
| `statusline.transcript.dedup_memory` | Int | 256 | usage-dedup list length | Dv (T-060) | BC-1.03.005 |
| `statusline.transcript.rebuild_excess` | Int | 20000 | rebuild threshold (excess input tokens) | M (T-056) | BC-1.03.007 |
| `statusline.composition.image_chars` | Int | 2000 | chars counted per image block | J (T-059) | BC-1.03.009 |
| `statusline.turn.dim_below_out` | Int | 200 | dim the last-turn segment below this out-rate | DOC (T-055) | BC-1.03.010 |
| `statusline.turn.floor_tps` | Float | 15.0 | per-agent decode TPS floor | DOC (T-057) | BC-1.03.010 |
| `statusline.turn.stale_factor` | Float | 4.0 | stale-rate multiplier | J (T-058) | BC-1.03.010 |
| `statusline.kv.cells` | Int | 4 | KV segment cell count | Dv (T-048) | BC-1.04.007 |
| `statusline.queue.yellow` | Bool | true | yellow rule: `q > 0 or preempt > 0` | Dv (T-047) | BC-1.04.006 |

Default-only parameters (the owning BC hard-codes the formula and leaves non-default
values undefined — non-default behavior: see the BC): `statusline.context.cells`,
`statusline.units.context` (BC-1.02.006 hard-codes `pct/10`, `min(…,10)`, `range(10)`);
`statusline.kv.cells` (BC-1.04.007 hard-codes `/25`, `4`, `4-n`); `statusline.queue.yellow`
(rule shape unstated beyond the default rule).

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
`state:`; OD-132, BC-2.03.002).

## Flag Interactions

| Flag A | Flag B | Interaction | Resolution |
|---|---|---|---|
| unknown flag | config error | unknown flag wins | flag check precedes `config.Load` (BC-4.01.002) |
| `--config <path>` | `HYLO_CONFIG` | flag overrides env | BC-2.03.002 |
| `HYLO_*` env | built-in default | env overrides default; file layer absent in P1 (OD-107) | BC-2.01.001 |
| first unknown flag | later unknown flags | first is rendered; all go to stderr | BC-4.01.002 |
| first config error | later config errors | first in registry order is rendered; all to stderr | BC-2.02.001 |
