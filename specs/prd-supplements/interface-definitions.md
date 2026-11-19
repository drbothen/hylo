---
document_type: prd-supplement-interface-definitions
level: L3
version: "1.21"
status: draft
producer: product-owner
timestamp: 2026-11-24T14:10:00Z
phase: 1a
stage: "3 of 3 (integration)"
inputs: [prd.md]
input-hash: "006ef5f"
modified:
  - "1.11 2026-11-19T02:00:00Z: pass-5 remediation A03 correction — sparkline.colors fade elements renamed [lo, hi] → [base, span] and law restated as base + span·i/max(n-2, 1) per legacy SL:683 (a base and a span, not a range)"
  - "1.12 2026-11-19T06:00:00Z: pass-6 remediation — glyph width rule restated in legacy's render width (code points; OD-184); `statusline.cache.rename_retry_delay_ms` registered (OD-186); default-only keys given exact env spellings (A13); Text-class reason strings for List-entry violations and non-theme control bytes (A14); subagent token ascending-pair check fire-at and D4-EX-3 naming rule (A19); rationale codes aligned to the owning BCs (B07); stale glyphs-never-named sentence fixed (B15); metrics_url row notes the OD-181 plain-http parity scope"
  - "1.13 2026-11-19T12:00:00Z: pass-7 remediation — unit-selector defaults resolved to their single accepted spellings with the legacy-letter rationale (A04/A05/D01, orchestrator call 5); `git.ttl_s` mirrored floor pinned in the Seconds-class note and the row (A06); `statusline.telemetry.timeout_s` validation ceiling labeled (A21); `Float quad` type named for `sparkline.scale` (D09); `statusline.cache.rename_retry_limit` registered (OD-188); dead-backend labels `statusline.labels.vllm_down`/`lmcache_down` and `statusline.subagent.name_fallback` registered (OD-189); registry back-references completed for `units.tokens`/`limits.windows`/`timer.min_ms` (B10) and the S1.07 consumers (C10)"
  - "1.14 2026-11-19T22:00:00Z: pass-8 remediation — context-denominator rationale cites BC-1.02.006 (the existing contract), not the nonexistent BC-2.01.006 (A01); `Float triple` shape name `array of 3 numbers` added to the Composite-Type grammar for `statusline.theme.heat` (A12); Default/Range cells of `theme.heat` and `limits.windows` re-spelled to the env spellings `[0.22,0.85,0.80]` / `5h,7d` (D06/call 11); `cost.percentiles` ascending check clarified as an intra-key member-pair check whose D4-EX-3 line names the whole key with its full JSON env value (A11)"
  - "1.15 2026-11-20T18:00:00Z: pass-9 remediation — subagent stdin payload section and NDJSON stdout row schema added (zero-byte cases included), copied from BC-1.07.001/.003/.004 (A01); `depthMetricsReply` 992/993 added to the Measured site list (A10); `paths.cache_dir` Range cell re-spelled ABSOLUTE-required with reason `not an absolute path` (A11/call 13); registry back-references completed for `sparkline.trace`/`cost.min_usd`/`cost.display_floor_usd` (C2-10)"
  - "1.16 2026-11-21T00:30:00Z: pass-10 remediation — `--config` no longer called a Global flag (config path is the only accepting verb; A17); stale not-yet-on-disk note dropped from the `paths.cache_dir` row, the error-taxonomy mirror having landed (A15); consumer columns completed: `statusline.pill.label_local` gains BC-1.04.004 (Precondition 3), `statusline.labels.vllm_down`/`lmcache_down` rescoped to the direct consumer BC-1.04.005, glyph-family consumer column gains BC-1.04.018 (sess_rate) and BC-1.04.019 (ttft) (C2-07)"
  - "1.17 2026-11-21T02:00:00Z: pass-10 residual sweep — `statusline.rows` Range cell states the BC-1.01.005 PC-4 rule (the row-2 comparison is exact, not clamped; a negative COLUMNS overflow clamped to math.MinInt64 is NOT output-equivalent, counter-case narrow_cols = MinInt64 — B04 sibling sweep); a BC-amendment citation respelled from a line pointer to the entry id (BC-1.07.005's modified 1.1.2 entry, C02)"
  - "1.18 2026-11-21T03:00:00Z: pass-11 remediation — stdin objects-read list rebuilt from every `.get(` on the stdin document and its sub-objects in legacy (fields legacy never reads removed: `rate_limits.windows`/`.spend_limit`, `workspace.repo.*`, `version`, `output_style.name`, `pr.kind`, `prompt_cache.last_miss_cause`/`miss_causes`; reads legacy makes added: `workspace.project_dir`, `prompt_cache.hit_ratio`, `rate_limits.five_hour`/`seven_day`, `cost.total_lines_added`/`removed`, `total_api_duration_ms`, `total_cost_usd` — A01/call 5); Default cells of `reroute_all_prefixes`, `cost.percentiles`, `limits.projected_bands`/`absolute_bands`, `cost.rate_min_api_ms` re-spelled to the env spellings `claude,claude-` / `[0.75,0.95]` / `[80,100]` / `[70,90]` / `{\"cc\":300000,\"other\":1800000}` (A09/call 4); `absolute_bands` cite corrected SL:520 → SL:521 (D17); `theme.separator` Range cell gains the measured built-in-literal collision caveat (`/`, `[`, `]`; SL:537/596, SL:1195-1196 — B05, with BC-1.01.006 Inv 1 widened the same pass); nine OD-194 label keys `statusline.labels.old/rate/queue/kv/host/tps/max/idle/na` registered with env names per `EnvName` and consumer BCs"
  - "1.19 2026-11-21T14:30:00Z: pass-12 remediation — `--subagent` output-contract applicability corrected: the CP-A01..A05 degrade ladder DOES apply in subagent mode (29-byte line; legacy `main_subagent` catches only stdin faults) while the happy path and the stdout config-error line do not (C01); `statusline.window_age.max_depth` Range cell gains the `0..1000` validation bound (A11/call 3); `statusline.theme.separator` collision caveat enumeration completed with the four built-in DIM-wrapped runs (B05); no behavioral change"
  - "1.20 2026-11-24T14:10:00Z: pass-13 remediation - both --subagent selection cells drop the false 'before any config processing' wording: the subagent path resolves config itself (OD-168; pass-12 A10) - the renderer is selected before the statusline flag scan (pass-3 A01), config after (A06); rename-retry registry ranges re-justified: delay ceiling 1000 -> 100 so that limit x delay is at most 1000 ms per Save, rationale a labeled judgment call, superseding the 'inside the refresh budget' arithmetic (A10, orchestrator call 15); no behavioral change"
  - "1.21 2026-11-18: pass-14 remediation - the exit-1 row gains the EC-012 cite (a relative HYLO_PATHS_CACHE_DIR also exits 1; A10); the statusline.glyphs.* family row's Contract column gains BC-1.02.008 (the member text already credited cache_hit to it; B08); the 1.20 entry re-slotted ascending (oldest-first standing rule); no behavioral change"
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

- `--config` flag: accepted by `config path` only — not a global flag; no other verb takes
  it (override; `~` expanded,
  OD-61/OD-101). `hylo statusline` otherwise takes no flags in P1: any argument starting
  with `-` is an unknown-flag error (OD-112), except a bare `-` (positional) and a bare
  `--`, which ends the flag scan (trailing arguments ignored by the SCAN only).
  `--subagent` is a ported P1 flag (OD-155, superseding OD-14): the exact argv element,
  matched ANYWHERE in the statusline argument slice — at any index, including after a
  bare `--` (pass-3 A01: `hylo statusline -- --subagent` routes to the panel) — selects
  the subagent panel renderer before the statusline flag scan, gated by
  `statusline.subagent.enabled` (default true; BC-1.07.001..008); the subagent path then
  resolves config itself (OD-168; pass-12 A10 — "before any config processing" is false). On the subagent path
  config IS resolved (OD-168): a config error there emits ZERO bytes on stdout and all
  reason lines (the full list, registry order) on stderr, exit 0 (pass-3 A02; singular
  "error line" wording corrected pass-5 A08; entry point and owner per ARCH-01
  `runStatuslineSubagent`).
- Dispatch contract: BC-4.01.001; version fallback chain: BC-4.01.003; config path
  resolution order (--config, then `HYLO_CONFIG`, then per-OS default): BC-2.03.002.

## Exit Code Semantics

| Code | Meaning | When | Contract |
|---|---|---|---|
| 0 | Success / degraded-success | every `statusline` render (including degraded ladder, config-error line, unknown-flag line); `version`; `config path` when all directories resolve; `config validate` when valid | BC-1.01.001, DI-008 |
| 1 | Validation failure | `config validate` on an invalid configuration; `config path` when a directory cannot be determined (BC-2.03.002 EC-008/010/011/012 — EC-012: a relative `HYLO_PATHS_CACHE_DIR` also exits 1; pass-5 A01, pass-14 A10) | BC-2.03.001, BC-2.03.002 |
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
  git_segment → load_cache, 9 frames) 990/991; metrics reply (main → get_sample →
  fetch_sample → json.loads(resp.read()), 7 frames) 992/993, MEASURED end to end
  against a localhost HTTP reply (pass-5 ADV-P5-A2-05; ARCH-06 `depthMetricsReply`;
  supplement site list completed pass-9 A10). Derived from equal chain depth: the
  get_sample, claude_window_start and mix-cache loaders (8 frames) 991/992; the
  cost-history loaders record_cost and cost_thresholds, called from render_lane
  (9 frames) 990/991. Boundaries are call-context dependent (ADV-P1-B17) and pinned by
  the recorded measurement recipes; there is no single budget and no per-mode budget
  (full table and recipes: VP-006; ADV-P2-A07 closed).
- Objects read (binding list, pass-11 A01/call 5 — exactly the fields legacy reads, derived
  from every `.get(` on the stdin document and its sub-objects in legacy/dgx_statusline.py):
  `model` (`.id`, `.display_name`; SL:441-443; BC-1.02.001/.002), `workspace`
  (`.project_dir`, `.current_dir`; SL:452; BC-1.02.003), `cwd` (SL:452; BC-1.02.003),
  `context_window` (`.used_percentage` SL:419, `.context_window_size` SL:423; entered at
  SL:463; BC-1.02.006/.020), `transcript_path` (SL:1009; BC-1.03.001/.015), `session_id`
  (SL:605, 1016, 1214, 1229), `prompt_cache` (`.hit_ratio`; SL:477; BC-1.02.008),
  `cost` (`total_duration_ms` SL:539, `total_lines_added`/`total_lines_removed` SL:535,
  `total_api_duration_ms` SL:550/603, `total_cost_usd` SL:601; BC-1.02.014/.016/.017/.018,
  BC-1.05.007), `rate_limits` (`.five_hour`, `.seven_day` — iterated at SL:499-504 — each
  window `.used_percentage`, `.resets_at`; BC-1.02.010/.011/.013). Fields legacy never
  reads, removed from the former list (pass-11 A01; the "newer optional fields" of
  market-intel §6.1 are tolerated absent like any other field but are not contract
  inputs): `rate_limits.windows`, `rate_limits.spend_limit`, `workspace.repo.*`,
  `version`, `output_style.name`, `pr.kind`,
  `prompt_cache.last_miss_cause`/`miss_causes`. Any field may be absent or null; wrong
  inner types degrade per the CP-S01..S17 register, never fail (BC-1.02.x, BC-1.03.015).

### Subagent stdin payload (--subagent)

Distinct from the MAIN contract above (BC-1.07.001 Pre-1/Pre-2): one NDJSON-style single
JSON object, assumed `{"columns": N, "tasks": [...]}` with per-task fields `id`, `name`,
`agentType`, `status`, `description`, `label`, `startTime` (ms), `model`, `tokenCount`
(ASSUMP-107-1: the Claude Code 2.1.326 `subagentStatusLine` payload is assumed compatible
with the 2.1.322 contract legacy parsed; verified by a capture before Phase 2 writes the
S1.07 stories, OD-192). Ingestion is TOTAL (BC-1.07.003): unparseable stdin, a non-object
top level, non-UTF-8 bytes, a BOM, trailing data, or falsy `tasks` absorbs to
`{}`/zero rows — zero bytes on stdout, exit 0, never the 29-byte line from the parse
path; the site runs on the same 6-frame chain depth as MAIN stdin (993 accepted / 994
rejected, VP-006). `columns` is carried but never trims subagent rows (BC-1.07.004 EC-007).

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
  `hylo: unknown flag <flag> (--subagent is the only P1 flag)` per flag; checked before
  config resolution (BC-4.01.002 PC-3; pass-4 A11 — the former "takes no flags" text is
  false since OD-155).
- Subagent mode (`--subagent`): zero or more LF-terminated NDJSON rows, one default-JSON
  object per eligible task — `{"id": <decoded task id re-serialized>, "content":
  <rendered row>}` — with CPython default separators (`, ` and `: `) and
  `ensure_ascii=True` (pure ASCII wire; every non-ASCII character as a `\uXXXX` escape);
  zero eligible tasks → zero bytes, exit 0; a subagent-mode config error → zero stdout
  bytes with ALL reason lines on stderr (OD-168). Applicability of the MAIN-mode outcomes
  above in this mode (corrected pass-12 C01): the typed crash-path degrade ladder DOES
  apply — a CP-A01..A05 renderer fault reaches the guard and the whole stdout is exactly
  the 29-byte degraded line (legacy `main_subagent` catches only stdin faults, SL:929-932,
  and the guard prints at SL:1243-1244; BC-1.07.008 PC1-PC6, error-taxonomy Surface 3) —
  while the 1-2 line happy path does not (NDJSON rows instead) and a config error emits
  zero stdout bytes (above). Stdin read/decode faults are caught inside `main_subagent`
  itself and absorbed to `{}` (BC-1.07.002/.003/.004; row schema and zero-byte cases:
  BC-1.07.004; pass-9 A01).
- Side-effect order on a degrade: legacy order preserved; earlier writes kept (BC-1.01.009).

## HYLO_* Key Schema (P1 subset)

Naming (BC-2.01.004): dotted lower-snake key names matching
`^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*|\[[0-9]+\])*$`; `EnvName(key)` = `HYLO_` + upper snake
with every `.`, `[`, `]` run collapsed to one `_`. Grammar per type: typed bool
(case-sensitive `true|false|1|0|yes|no`), comma lists (OD-74), `~` expansion in paths
(OD-61, `~user` left as written), COLUMNS excluded as protocol input (BC-2.01.005),
composite types as strict JSON of the declared shape (below). Full registry (every key:
type, range, default, unit, op, rationale, rationale code): BC-2.01.004 + golden
`internal/config/testdata/legacy_defaults.golden`.

### Composite-Type Env Grammar (Float pair / Float triple / Float quad / Int map / RGB triples + Float)

A key whose registry type is composite — `Float pair`, `Float triple`, `Float quad`,
`Int map`, `RGB triples + Float`, or any list of numbers — takes its env value as **strict JSON of
the declared shape** (pass-4 design call; ADV-P4-A04/D19). Parsing is shape-first, then
range:

1. The value must parse as strict JSON (no `NaN`/`Infinity` tokens, no trailing data)
   with exactly the declared shape. Shape names: `array of 2 numbers` (Float pair),
   `array of 3 numbers` (Float triple — `statusline.theme.heat`),
   `array of 4 numbers` (Float quad — `statusline.sparkline.scale`; the type name "Float
   triple" was wrong for this key; pass-5 A03, type named pass-7 D09),
   `object {cc,other} of integers` (Int map),
   `object {trail,fade,amber,head}` (RGB triples + Float).
2. Range checks apply after the shape check, member by member: a member outside its
   range is the number-range error with the existing vocabulary; a default-only
   composite's range is its default value (OD-162): an env value equal to the default is
   accepted, any other value is a number-range config error (pass-5 call 3).
3. Reason string for a shape failure: `<key>=<value> (expected JSON <shape>)`, where
   `<shape>` is e.g. `array of 2 numbers` or `object {cc,other} of integers`. Shape
   errors belong to the seventh D4-EX-3 class **Text** (OD-178; see the error taxonomy).
   Examples: `HYLO_STATUSLINE_COST_PERCENTILES='[0.5,0.9]'` (valid shape; the descending
   pair `'[0.95,0.75]'` passes the shape check and fails the ASCENDING range check —
   number-range error, pass-3 C2-07); `HYLO_STATUSLINE_COST_RATE_MIN_API_MS='{"cc":1,"other":2}'`.
4. Per-key shapes (binding, pass-5 call 3 — each key's declared shape must hold its
   default):
   - `statusline.sparkline.scale` = array of 4 finite numbers `[k_top, v_floor, f_floor,
     other]`, default `[1.0, 1.0, 0.1, 1e-9]`, each member finite `> 0`.
   - `statusline.sparkline.colors` = object with exactly the members `{"trail":[r,g,b],
     "fade":[base,span],"amber":[r,g,b],"head":[r,g,b]}` — trail/amber/head arrays of 3
     integers, fade an array of 2 finite numbers `[base, span]` (the trail fade factor is
     `base + span·i/max(n-2, 1)`: default `[0.55, 0.45]` = base 0.55, span 0.45, matching
     legacy `fade = 0.55 + 0.45 * i / max(len(pts) - 2, 1)`, SL:683, and BC-2.01.005
     PC-5). The former one-number fade spelling cannot
     express the span (pass-5 A03).
   - Int map = object with exactly the keys `cc` and `other`, each a JSON integer (no
     fraction, no exponent) within int64, no extra keys, duplicate keys rejected
     (pass-5 D13).
   - Float pairs name each element: `statusline.limits.projected_bands` =
     `[yellow, red]` — legacy compares red FIRST (`RED if proj > red else YELLOW if
     proj >= yellow`, red strict `>`, yellow inclusive `>=`; SL:519);
     `statusline.limits.absolute_bands` = `[yellow, red]` — red first, both comparisons
     strict `>` (SL:520). The chain is comparison-total, so no ordering constraint
     between the elements is ratified; the POSITION fixes the meaning (pass-5 A15).

The composite type names join the BC-2.01.004 `Type` enum (BC-2.01.004 amended in the
same burst; pass-4 design call 1).

Representative keys (families enumerated in design §2.4; amended by OD-113, OD-123):

| Key | Type | Default | Range / op | Rationale (code) | Contract |
|---|---|---|---|---|---|
| `statusline.rows` | Int | 2 | any int64 (legacy semantics for negative and large values — and the row-2 comparison is exact, not clamped: a negative COLUMNS overflow clamped to `math.MinInt64` is NOT output-equivalent, the counter-case being `narrow_cols = MinInt64`, BC-1.01.005 PC-4); row 2 shown when `rows >= 2` and (`rows > 2` or `cols == 0` or `cols >= narrow_cols`) — the width rule hides row 2 only when `rows == 2` (BC-1.01.003; pass-4 B22; pass-7 B01) | C (T-002, convention; BC-1.01.003) | BC-1.01.003, BC-1.04.013, BC-2.02.003 |
| `statusline.narrow_cols` | Int | 72 | any Int (comparison-total `cols >= narrow_cols` gate — non-negative and negative gate values both gate total, pass-3 B08) | OWNER (T-014, group B; OD-57 E-B; BC-1.01.003) | BC-1.01.003 |
| `statusline.git.enabled` | Bool | true | on/off segment gate | DOC | BC-1.02.005 |
| `statusline.git.ttl_s` | Seconds | 5 | any finite number in `[-9223372036.854775, 9223372036.854775]` (the ceiling mirrored by an explicit floor; a value below the floor is `out of range`, BC-2.02.002 — pass-7 A06); negative = "never fresh" for ordinary timestamps — the gate `now - ts > ttl` (SL:409) is comparison-total, so a `ts` more than \|ttl\| in the future still counts as fresh (BC-1.02.005 EC-007; pass-5 B11); the Duration ceiling still applies (Seconds-class note below), the negative admission is an exception to the `>= 0` floor only (pass-5 A14). Behavior legacy defines (SL:99), so negatives are admitted (pass-3 B08). Explicit per-key exception to the BC-2.02.002 Seconds class (BC-2.02.002 carries the exception list; pass-4 A03) | C (T-013) | BC-1.02.005 |
| `statusline.telemetry.ttl_s` | Seconds | 4 | finite, `>= 0`, `<= 9223372036.854775`; strict `fetch_ts > now - ttl` | DOC (T-001) | BC-1.04.002, BC-2.02.002 |
| `backends[0].metrics_url` | URL | `http://192.0.2.10:8428` | scheme http(s), host present; a URL with userinfo (`http://u:p@host:8428`) loads and then reproduces legacy: no sample (the dead rung) — no exclusion id (OD-180, pass-5 C2-03). Parity metrics cases use plain http only (OD-181 closed-set id: non-http(s) redirect targets → hylo no sample; https verifies against the OS trust store — table-tested, out of byte-parity scope) | OWNER (OD-123) | BC-2.01.002, BC-2.02.005 |
| `backends[0].model_prefixes` | List | `claude-sonnet` | comma list; startswith match | OWNER (OD-111/123) | BC-2.01.002, BC-1.02.001, BC-1.07.006, BC-1.07.008 |
| `statusline.lane.reroute_all_prefixes` | List | `claude,claude-` (legacy display form `["claude", "claude-"]`; Default re-spelled to the env spelling pass-11 A09/call 4) | comma list; every entry non-empty, no control bytes (OD-179, pass-5 B09: the reroute-all markers become config, sourcing the hard-coded "named constant" in BC-1.02.009); entry violation reason `expected non-empty control-free text in every entry`, Text class (OD-178; pass-6 A14) | OWNER (OD-179) | BC-1.02.009 |
| `paths.cache_dir` | Path | per-OS hylo cache dir | ABSOLUTE path required (env `HYLO_PATHS_CACHE_DIR`; `~` expansion per OD-61): a relative value resolves against the per-project cwd and splits caches and cost history, so it is a config error with reason `not an absolute path` (path-grammar family — BC-2.01.005 grammar, riding E-CFG-001 without a dedicated class per the Reason-Vocabulary note in BC-2.02.006; exact string minted pass-9 A11/call 13, mirrored in error-taxonomy) — closing the P20/OD-162 range gap of the former "not the legacy literal (exception)" cell; still not the legacy literal (exception, OD-101) | OWNER (OD-101) | BC-3.01.001 |
| `statusline.cache.rename_retry_delay_ms` | Int | 10 | `1..100` — both bounds labeled judgment call (J): long enough to clear a Windows sharing violation, and set WITH `rename_retry_limit`'s 0..10 ceiling so that limit x delay is at most 1000 ms per Save (labeled judgment call, ADV-P13-A10 / orchestrator call 15 — supersedes the former "inside the refresh budget" arithmetic, which the 10 x 1000 ms product contradicted; OD-186, pass-6 A09: the retry delay was a timing value outside the registry) | J (OD-186) | BC-1.06.001 |
| `statusline.cache.rename_retry_limit` | Int | 2 | `0..10` — both bounds labeled judgment call (J); TOTAL attempts = 1 + limit (limit 0 = the initial replace only, no retry); the 10 ceiling jointly bounds limit x delay at 1000 ms per Save (ADV-P13-A10 / orchestrator call 15). Beside its sibling `rename_retry_delay_ms`; supersedes the `renameRetryLimit = 2` code constant (OD-188, pass-7 A19/A2-07: the knob decides whether a Windows cache write persists, which is parity-visible via the `temp-file` exclusion, so the "no parity-visible behavior" reason for keeping it a constant no longer holds) | J (OD-188) | BC-1.06.001 |
| `statusline.theme.reset` | SGR | `0` | SGR parameter list (non-list = config error, BC-2.01.003) | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.dim` | SGR | `2` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.bold` | SGR | `1` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.white` | SGR | `97` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.cyan` | SGR | `36` | SGR parameter list | DOC (OD-113) | BC-2.01.003, BC-1.07.006, BC-1.07.007 |
| `statusline.theme.green` | SGR | `32` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.yellow` | SGR | `33` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.red` | SGR | `31` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.grey` | SGR | `90` | SGR parameter list | DOC (OD-113) | BC-2.01.003, BC-1.07.006, BC-1.07.007 |
| `statusline.theme.magenta` | SGR | `35` | SGR parameter list | DOC (OD-113) | BC-2.01.003, BC-1.07.006 |
| `statusline.theme.boldred` | SGR | `1;91` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.pill_local` | SGR | `106;30;1` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.pill_cloud` | SGR | `105;30;1` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.theme.pill_unknown` | SGR | `100;37;1` | SGR parameter list | DOC (OD-113) | BC-2.01.003 |
| `statusline.pill.label_local` | Text | `DGX` | non-empty, no control bytes, display width 1..16 (judgment call: keeps the pill short; OD-173); the marker word of the dead-backend rung `◌ <label_local> ?` too (OD-189, pass-7 C2-07) | OWNER (OD-173) | BC-1.02.001, BC-1.04.004 (Precondition 3, dead-marker word), BC-1.07.006 |
| `statusline.pill.label_cloud` | Text | `ANTH` | non-empty, no control bytes, display width 1..16 (as above; OD-173) | OWNER (OD-173) | BC-1.02.001, BC-1.07.006 |
| `statusline.pill.label_unknown` | Text | `?` | non-empty, no control bytes, display width 1..16 (as above; OD-173) | OWNER (OD-173) | BC-1.02.001 |
| `statusline.theme.separator` | Text | ` · ` (U+00B7) | free text, no control bytes (control byte = config error, BC-2.01.003 PC-3). MEASURED collision caveat (pass-11 B05; enumeration completed pass-12 B05): a value whose wrapped bytes `DIM + value + RESET` occur inside a built-in segment — measured built-in exact literals: `/` (lines segment, SL:537), `[` and `]` (token brackets, SL:596) — or inside any built-in DIM-wrapped run: the denominator `{DIM}/…M{RESET}` (SL:435-436, e.g. `/1.0M`, `/200K`), the API-duration suffix `·1m` (SL:553), the window-age suffix `(~5s old)` (SL:700), the telemetry run `↺host 30%` (SL:762) — makes trim_to_fit's `SEP in row` test (SL:1195) true at that inner position, so the rsplit cut (SL:1196) lands inside the built-in segment; admissible, the rendered outcome pinned by the BC-1.01.006 PC1/Inv 1 caveat (widened the same pass) | DOC (OD-113) | BC-2.01.003 |
| `statusline.window_age.process_name` | Text | `claude` | non-empty, no control bytes; exact basename match (Windows `.exe` stripped) | OWNER (OD-133) | BC-3.02.001/.002 |
| `statusline.sparkline.trace` | Enum | `rate` | `rate\|kv\|ttft` (legacy `mine` retired) | DOC | BC-2.02.004, BC-1.04.009 (consumer; pass-9 C2-10) |
| `statusline.context.cells` | Int | 10 | `1..100` — upper bound 100 is a labeled judgment call (J), same rationale as `kv.cells`: caps O(cells) render work and visible-width blowup within the 25 ms p95 budget; the T-codes justify the DEFAULT, not the bound (BC-1.02.006 PC3-PC5 define the widget for any cell count; pass-4 B09 aligns the bound with `kv.cells`). An out-of-range value is a config error, never a clamp (pass-5 B15/call 16) | J (T-027..T-029) | BC-1.02.006 |
| `statusline.context.plain_max` | Float | 50 | any finite number (comparison-total `pct > plain_max` colour gate — plain percentage vs heat-coloured number; not the `min(…,n)` cells formula; BC-1.02.006 PC3-PC5; type aligned to the BC's "any finite JSON number", pass-4 B08) | DOC | BC-1.02.006 |
| `statusline.context.red_from` | Float | 85 | any finite number (band threshold, operator `>=`; BC-1.02.006 PC3-PC5; type aligned to the BC, pass-4 B08) | DOC | BC-1.02.006 |
| `statusline.units.context` | Text | `K` | default-only: range = {`K`}; registered semantics `1e6` → `M`, else `K` — default-only because the M/K divisors are fixed format constants that define the unit spellings, not because the widget formula is hard-coded (pass-4 B10) | DOC | BC-1.02.006 |
| `statusline.units.lines` | Text | `k` | default-only: range = {`k`}; registered render semantics: thresholds 10,000 (`>=` → k), 1,000,000 (`>=` → M) | DOC | BC-1.02.014 |
| `statusline.units.tokens` | Text | `M` | default-only: range = {`M`}; registered render semantics: thresholds 1,000 (`>=` → k), 1e6 (`>=` → M) | DOC (T-042) | BC-1.02.025, BC-1.02.018 |
| `statusline.theme.heat` | Float (triple) | `[0.22,0.85,0.80]` | default-only: range = {`[0.22,0.85,0.80]`} — BC-1.02.019's HSV gradient is defined only for the default triple (PC2 covers sectors i ∈ {0,1}, hue span ≥ 1/3), so any other triple is a number-range config error (OD-162); the Default/Range cells carry the env spelling, the strict-JSON array (pass-6 A13/call 8; cells re-spelled from the display form pass-8 D06/call 11); pass-4 B01/design call 6 | DOC (T-030) | BC-1.02.019 |
| `statusline.transcript.read_cap_bytes` | Int (bytes) | 524288 | `1..67108864` (upper bound 64 MiB, labeled judgment call (J): caps per-refresh read buffering far beyond any real transcript step; pass-5 A13/call 16) | J (T-054) | BC-1.03.003 |
| `statusline.transcript.dedup_memory` | Int | 256 | `1..65536` (upper bound labeled judgment call (J), pass-5 A13/call 16) | Dv (T-060) | BC-1.03.005 |
| `statusline.transcript.rebuild_excess` | Int | 20000 | `>= 0` | M (T-056) | BC-1.03.007 |
| `statusline.composition.image_chars` | Int | 2000 | `>= 0` | J (T-059) | BC-1.03.009 |
| `statusline.turn.dim_below_out` | Int | 200 | `>= 0`; dim gate compares the last turn's output **token count** (`out < TURN_DIM_OUT`), not a rate | DOC (T-055) | BC-1.03.010 |
| `statusline.turn.floor_tps` | Float | 15.0 | `> 0` (finite) | DOC (T-057) | BC-1.03.010 |
| `statusline.turn.stale_factor` | Float | 4.0 | `> 0` (finite) | J (T-058) | BC-1.03.010 |
| `statusline.kv.cells` | Int | 4 | `1..100` — upper bound 100 is a labeled judgment call (J): caps the O(cells) render work and visible-width blowup far beyond any terminal used with the status line, keeping the 25 ms p95 budget; the T-codes justify the DEFAULT, not the bound (pass-3 A27; cell formula defined for C ≥ 1; non-default behavior defined in BC-1.04.007) | Dv (T-048) | BC-1.04.007 |
| `statusline.queue.yellow` | Bool | true | both booleans defined: `true` = rule `q > 0 or preempt > 0`, `false` = never yellow (BC-1.04.006; ratified as a P1 Bool key by OD-175, pass-4 D26) | Dv (T-047) | BC-1.04.006 |
| `statusline.sparkline.points` | Int | 12 | `1..100` — upper bound 100 is a labeled judgment call (J), same rationale as `kv.cells`: caps O(points) render work and segment width within the 25 ms p95 budget; the T-code justifies the default, not the bound (pass-3 A27) | J (T-006) | BC-1.04.009 |
| `statusline.sparkline.history_cap` | Int | 32 | `1..1000` (upper bound labeled judgment call (J), same render-budget rationale as `kv.cells`; pass-5 A13/call 16) | Dv (T-009) | BC-1.04.003/.009 |
| `statusline.sparkline.scale` | Float quad (composite) | `[1.0, 1.0, 0.1, 1e-9]` = `[k_top, v_floor, f_floor, other]` | array of 4 finite numbers (`array of 4 numbers`), each `> 0` (strict JSON env grammar, per-key shape in Composite-Type Env Grammar; pass-5 A03/call 3; `Float quad` joins the BC-2.01.004 `Type` enum — pass-7 D09) | Dv (T-045) | BC-1.04.009 |
| `statusline.cost.min_sessions` | Int | 10 | `>= 1` (0 raises IndexError on an empty list in legacy, SL:261) | OWNER (T-020) | BC-1.05.005 |
| `statusline.cost.percentiles` | Float pair | `[0.75,0.95]` (env spelling, pass-11 A09/call 4) | each a finite Float in `[0, 1]`, ASCENDING pair: `p75 <= p95` is ratified — a descending pair is a number-range config error (strict JSON env grammar, see Composite-Type Env Grammar; pass-3 C2-07; ratified in BC-1.05.005 on its own grounds — index overflow and negative wrap — not mirrored from the limits bands, whose chained red-first comparison is comparison-total for any finite pair, so no ordering constraint is ratified there); when the ascending check fails, the D4-EX-3 line names the WHOLE key `statusline.cost.percentiles` with its full JSON env value (intra-key member-pair check — both members live in the one key's JSON value, no per-member env spelling; cf. the two-key `subagent.tokens` pair, which names the second key; pass-8 A11) | OWNER (T-024) | BC-1.05.005 |
| `statusline.cost.min_usd` | Float | 1.0 | finite `>= 0` (grey test strict `<`) | Dv (T-019) | BC-1.05.001, BC-1.05.005 (PC2 skip gate; pass-9 C2-10) |
| `statusline.cost.cold_yellow_usd` | Float | 25.0 | finite `>= 0` (cold test inclusive `>=`) | OWNER (T-021) | BC-1.05.001 |
| `statusline.idle.running_below` | Float | 1 | finite `>= 0`, NaN rejected | DOC (T-108) | BC-1.04.012 |
| `statusline.subagent.enabled` | Bool | true | on/off panel gate, default = legacy (OD-155) | OWNER (OD-155) | BC-1.07.002 |
| `statusline.subagent.glyphs.running` | Text | `\u00bb` (U+00BB) | exactly 1 code point in legacy's render width (code points; OD-184), non-empty, no control bytes (one-line output invariant; mirrors BC-2.01.003 PC-3) | J (OD-02; SL:845-846) | BC-1.07.005 |
| `statusline.subagent.glyphs.completed` | Text | `\u2714` (U+2714) | exactly 1 code point in legacy's render width (code points; OD-184), non-empty, no control bytes (as above) | J (OD-02; SL:845-846) | BC-1.07.005 |
| `statusline.subagent.glyphs.failed` | Text | `\u2718` (U+2718) | exactly 1 code point in legacy's render width (code points; OD-184), non-empty, no control bytes (as above) | J (OD-02; SL:845-846) | BC-1.07.005 |
| `statusline.subagent.glyphs.killed` | Text | `\u25cd` (U+25CD) | exactly 1 code point in legacy's render width (code points; OD-184), non-empty, no control bytes (as above) | J (OD-02; SL:845-846) | BC-1.07.005 |
| `statusline.subagent.glyphs.unknown` | Text | `\u25cd` (U+25CD) | exactly 1 code point in legacy's render width (code points; OD-184), non-empty, no control bytes; rendered in `statusline.theme.grey`; it does NOT follow `glyphs.killed` (independent key, pass-4 C07/design call 4; SL:894) | J (OD-02; SL:894) | BC-1.07.005 |
| `statusline.subagent.colors.running` | SGR | `33` | SGR parameter list (class per BC-2.01.003; legacy YELLOW). The default coincides with the `statusline.theme.yellow` default but the two are independent values: changing the theme key does not change this key (J, pass-4 A21 \u2014 each key's range is its own, OD-162) | J (OD-02; SL:131-132, 845-846) | BC-1.07.005 |
| `statusline.subagent.colors.completed` | SGR | `32` (legacy GREEN) | SGR parameter list (as above; independence from `statusline.theme.green`, pass-4 A21) | J (OD-02; SL:131-132, 845-846) | BC-1.07.005 |
| `statusline.subagent.colors.failed` | SGR | `31` (legacy RED) | SGR parameter list (as above; independence from `statusline.theme.red`, pass-4 A21) | J (OD-02; SL:131-132, 845-846) | BC-1.07.005 |
| `statusline.subagent.colors.killed` | SGR | `90` (legacy GREY) | SGR parameter list (as above; independence from `statusline.theme.grey`, pass-4 A21) | J (OD-02; SL:131-132, 845-846) | BC-1.07.005 |
| `statusline.subagent.joiner` | Text | `\u0020\u00b7\u0020` (space, U+00B7, space) | free text, no control bytes (control byte = config error, Text class per OD-178, raised by BC-2.01.005; pass-6 A14) | DOC (SL:924) | BC-1.07.004 |
| `statusline.subagent.name_fallback` | Text | `?` | non-empty, no control bytes (fallback for a row with no usable name; OD-189 sources the hard-coded literal — pass-7 C11/C2-07: the equivalent `?` in the lane pill is a key, so this one is too) | OWNER (OD-189) | BC-1.07.005 |
| `statusline.subagent.tokens.k_from` | Float | 1000 | finite `> 0`; ascending pair `k_from <= m_from` (OD-162 every-key-has-a-range; pass-3 A14/C05) | DOC (T-042) | BC-1.07.007 |
| `statusline.subagent.tokens.m_from` | Float | 1000000 | finite `> 0`; ascending pair `k_from <= m_from` (as above). Pair-fire rule (pass-6 A19): the ascending-pair check runs at `m_from`'s own validation, after both keys pass their single-key range checks; when it fails, the D4-EX-3 line names `statusline.subagent.tokens.m_from` with its own value, reason `ascending pair violated (k_from <= m_from)` (number-range class) | DOC (T-042) | BC-1.07.007 |
| `statusline.subagent.tokens.suffix` | Text | ` tok` (U+0020 + `tok`) | non-empty, no control bytes (mirrors BC-2.01.003 PC-3); the `k_from`/`m_from` values are display thresholds only — the divisors 1e3/1e6 are format constants that define the K/M units, not config (why-not-config comment required at the call site; pass-4 C05/design call 3) | DOC (T-042) | BC-1.07.007 |
| `statusline.limits.keep_s` | Seconds | 1800 | finite `> 0` (`<` age gate, comparison-total in legacy; pass-3 A05) | J (T-010, owner group A) | BC-1.02.013, BC-1.02.030 |
| `statusline.limits.windows` | List | `5h,7d` | default-only: range = {`5h,7d`} (comma-list env grammar, OD-74; window lengths 18000 s / 604800 s; non-default selectors undefined; Default/Range cells re-spelled from the display form pass-8 D06/call 11) | DOC (T-031, Anthropic convention) | BC-1.02.010, BC-1.02.011, BC-1.02.024 |
| `statusline.limits.countdown_max_factor` | Float | 1.15 | any finite number (multiplier in the `<=` countdown gate) | J (T-035, owner judgment; OD-57 E-A; BC-1.02.012) | BC-1.02.012 |
| `statusline.limits.projection_min_elapsed` | Float | 0.10 | any finite number (`>=` elapsed-fraction gate) | DOC (T-032) | BC-1.02.011, BC-1.02.024 |
| `statusline.limits.projected_bands` | Float pair | `[80,100]` (env spelling, pass-11 A09/call 4; position 0 = yellow, position 1 = red) | each a finite Float; ELEMENTS NAMED: position 0 is the yellow threshold (compared `>=`, inclusive), position 1 the red threshold (compared `>`, strict), red checked first in legacy's chained comparison (SL:519); strict JSON env grammar, see Composite-Type Env Grammar (pass-5 A15/call 3) | DOC (T-033) | BC-1.02.011, BC-1.02.024 |
| `statusline.limits.absolute_bands` | Float pair | `[70,90]` (env spelling, pass-11 A09/call 4; position 0 = yellow, position 1 = red) | each a finite Float; ELEMENTS NAMED: position 0 yellow, position 1 red, both compared `>`, red checked first (SL:521 — comparison site corrected from the `else:` line 520, pass-11 D17; BC-2.01.005 PC-5 agrees); strict JSON env grammar, see Composite-Type Env Grammar (pass-5 A15/call 3) | DOC (T-034) | BC-1.02.011, BC-1.02.024 |
| `statusline.timer.min_ms` | Int | 60000 | any Int (comparison-total display gate, operator `>`) | Dv (T-038, derived; BC-1.02.015) | BC-1.02.015, BC-1.02.016, BC-1.02.027 |
| `statusline.timer.api_min_ms` | Int | 60000 | any Int (operator `>=`) | Dv (T-039, derived; BC-1.02.016) | BC-1.02.016, BC-1.02.027 |
| `statusline.cost.window_s` | Seconds | 2592000 (30 d) | finite `> 0` (history filter; pass-3 A05) | OWNER (T-018) | BC-1.05.005 |
| `statusline.cost.record_throttle_s` | Seconds | 60 | finite `> 0` (strict `<` throttle; pass-3 A05) | Dv (T-022) | BC-1.05.004 |
| `statusline.cost.rate_min_api_ms` | Int map | `{"cc":300000,"other":1800000}` (strict-JSON env spelling, pass-11 A09/call 4) | each value an Int `> 0` (ratio gate; strict JSON env grammar, see Composite-Type Env Grammar; `<= 0` would let `api_ms` = 0 pass the gate and Python raises ZeroDivisionError at the render SL:623 or in `cost_thresholds` SL:255, which Go floats would silently not reproduce — restricted pass-5 C2-08/call 16). The `_ms` values are millisecond denominations: the BC-2.01.004 PC-3(e) millisecond-type rule applies to the VALUE denomination for map-valued keys (pass-5 D14) | Dv (T-023) | BC-1.05.005 |
| `statusline.cost.burn_min_api_ms` | Int | 300000 | Int `> 0` (ratio gate; ZeroDivisionError guard as above, pass-5 C2-08/call 16) | Dv (T-043) | BC-1.05.002 |
| `statusline.cost.display_floor_usd` | Float | 0.005 | finite Float (operator `>=`); renamed from `cost.basis_min_shown_usd` by OD-174 (pass-4 B21: the key is a display floor for the `⛏` pick, not a basis minimum; not yet shipped, so the rename is free of compatibility debt) | Dv (T-044) | BC-1.02.029, BC-1.05.003 (PC3 pick gate; pass-9 C2-10) |
| `statusline.cost.basis_min_mtok_month` | Float | 30.4 | finite Float (operator `>=`) | Dv (T-012) | BC-1.02.029, BC-1.05.003 |
| `statusline.telemetry.query` | Text | legacy `QUERY` literal (SL:102-123, byte-pinned golden) | any text (percent-encoded into the URL; upstream errors give no sample — the dead rung of the freshness ladder, never a CP-S degrade: BC-1.04.001 PC3/PC5; disposition corrected pass-5 C2-16) | DOC | BC-1.04.001 |
| `statusline.telemetry.timeout_s` | Seconds | 1.5 | finite Float > 0, validation ceiling `<= 25` (HTTP client timeout; <= 0 not legacy-covered). Ceiling rationale (J, pass-7 A21): ~16x the 1.5 s default and an order of magnitude under the 300 s `keep_dead_s` retention horizon — OD-56 makes the fetch a synchronous total deadline inside the render, so an unbounded accepted value could stall the line for its whole duration; the numeric ceiling is a labeled judgment call, not a measured bound | J (T-005) | BC-1.04.001 |
| `statusline.telemetry.fresh_s` | Seconds | 15 | finite `> 0` (freshness comparison; pass-3 A05) | Dv (T-003) | BC-1.04.004 |
| `statusline.telemetry.keep_dead_s` | Seconds | 300 | finite `> 0` (retention comparison; pass-3 A05) | J (T-004) | BC-1.04.002 |
| `statusline.ttft.min_samples` | Int | 20 | any Int (sample-count gate; below it p95 = max) | Dv (T-015) | BC-1.04.010 |
| `statusline.ttft.integer_from_s` | Seconds | 10 | finite `> 0` (histogram-bucket threshold; pass-3 A05) | Dv (T-051) | BC-1.04.010 |
| `statusline.ttft.yellow_s` | Seconds | 8 | finite `> 0` (colour-band threshold; pass-3 A05) | M (T-052) | BC-1.04.010 |
| `statusline.idle.after_s` | Seconds | 300 | finite `> 0` (idle comparison; pass-3 A05) | J (T-011) | BC-1.04.012 |
| `statusline.power.wall_red_w` | Watts (Int) | 1520 | any Int (band comparison) | Dv (T-053) | BC-1.04.011 |
| `statusline.power.wall_yellow_w` | Watts (Int) | 1280 | any Int (band comparison) | Dv (T-053) | BC-1.04.011 |
| `statusline.window_age.min_margin_ms` | Milliseconds (Int) | 300000 | any Int (margin comparison) | OWNER (T-040, owner request) | BC-1.02.017 |
| `statusline.window_age.max_depth` | Int | 6 | `0..1000` (ancestor-walk cap; 0 = no ancestor walk — `FindAncestor` makes zero probes and returns not-found; upper bound 1000 mirrors `statusline.sparkline.history_cap`'s validation bound, labeled judgment call; range added pass-12 A11/call 3) | DOC (T-025) | BC-3.02.001 |
| `statusline.kv.host_shown_pct` | Float | 0.5 | finite Float (display gate) | Dv (T-050) | BC-1.04.007 |
| `statusline.kv.host_yellow_pct` | Float | 5 | finite Float (band threshold, THRESHOLDS §8 SL:746) | M (T-049) | BC-1.04.007 |
| `statusline.sparkline.enabled` | Bool | true | both booleans defined: `false` hides the sparkline (legacy `DGX_SL_SPARK != "0"`) | DOC | BC-1.04.008, BC-2.01.005 |
| `statusline.sparkline.max_age_s` | Seconds | 90 | finite `> 0` (gap-pruning comparison; pass-3 A05) | Dv (T-007) | BC-1.04.003 |
| `statusline.sparkline.min_gap_s` | Seconds | 2 | finite `> 0` (gap guard; pass-3 A05) | Dv (T-008) | BC-1.04.003 |
| `statusline.sparkline.preempt_marker_above` | Float | 0 | `>= 0` (finite); the history `p` marker shows when preempt > value; independent of `statusline.queue.yellow` (pass-4 C2-13/design call 5; type Int → Float pass-5 C2-11/call 16 — `dgx_preempt:rate5m` is a per-second rate, so an Int could not express the historical > 0.01/s rule, SL:737-738) | Dv (T-107) | BC-1.04.003 |
| `statusline.sparkline.colors` | RGB triples + Float | `{"trail":[70,170,190],"fade":[0.55,0.45],"amber":[220,170,60],"head":[140,235,255]}` | object with exactly the members `trail`/`amber`/`head` (arrays of 3 integers) and `fade` (array of 2 finite numbers `[base, span]` — the trail fade factor is `base + span·i/max(n-2, 1)`, per BC-2.01.005 PC-5); components any Int, fade finite (presentation formatter plugs them in; strict JSON env grammar, per-key shape in Composite-Type Env Grammar; pass-5 A03/call 3) | J (T-046, presentation) | BC-1.04.009 |
| `statusline.labels.input` | Text | `in` | non-empty, no control bytes; a two-character LABEL, not a glyph (member ranges per family rule; OD-02's 1-code-point rule does not apply to labels; pass-4 A05/B15 design call 2) | DOC (OD-02) | BC-1.02.018 |
| `statusline.labels.vllm_down` | Text | `vLLM down` | non-empty, no control bytes (dead-backend marker label, OD-189: the `up:vllm` dead-backend word is config, not a constant — pass-7 C2-07) | OWNER (OD-189) | BC-1.04.005 (direct consumer; BC-1.04.004 consumes only via BC-1.04.005) |
| `statusline.labels.lmcache_down` | Text | `LMCache down` | non-empty, no control bytes (as above; OD-189) | OWNER (OD-189) | BC-1.04.005 (direct consumer; BC-1.04.004 consumes only via BC-1.04.005) |
| `statusline.labels.old` | Text | `old` | non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-194 label rule; the 1..16 bound is the OD-173 judgment call); env `HYLO_STATUSLINE_LABELS_OLD`; the word of the stale suffix `(~Ns old)` (SL:700) | OWNER (OD-194) | BC-1.04.004 |
| `statusline.labels.rate` | Text | `r` | non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-194 label rule; OD-173 bound); env `HYLO_STATUSLINE_LABELS_RATE`; the running word of `r<n>·q<m>` (SL:741) | OWNER (OD-194) | BC-1.04.006 |
| `statusline.labels.queue` | Text | `q` | non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-194 label rule; OD-173 bound); env `HYLO_STATUSLINE_LABELS_QUEUE`; the waiting word of `r<n>·q<m>` (SL:741) | OWNER (OD-194) | BC-1.04.006 |
| `statusline.labels.kv` | Text | `KV` | non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-194 label rule; OD-173 bound); env `HYLO_STATUSLINE_LABELS_KV`; the KV gauge word (SL:761) | OWNER (OD-194) | BC-1.04.007 |
| `statusline.labels.host` | Text | `host` | non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-194 label rule; OD-173 bound); env `HYLO_STATUSLINE_LABELS_HOST`; the host-share rung word `↺host <n>%` (SL:762-763) | OWNER (OD-194) | BC-1.04.007 |
| `statusline.labels.tps` | Text | `t/s` | non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-194 label rule; OD-173 bound); env `HYLO_STATUSLINE_LABELS_TPS`; the throughput unit word of both segments (SL:781 mine, SL:783 box rate) | OWNER (OD-194) | BC-1.04.008, BC-1.04.018 |
| `statusline.labels.max` | Text | `max` | non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-194 label rule; OD-173 bound); env `HYLO_STATUSLINE_LABELS_MAX`; the under-min-samples TTFT rung word `◔max <v>` (SL:797) | OWNER (OD-194) | BC-1.04.010 |
| `statusline.labels.idle` | Text | `idle` | non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-194 label rule; OD-173 bound); env `HYLO_STATUSLINE_LABELS_IDLE`; the idle segment word `☾ idle <age>` (SL:834) | OWNER (OD-194) | BC-1.04.012, BC-1.04.017 |
| `statusline.labels.na` | Text | `n/a` | non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-194 label rule; OD-173 bound); env `HYLO_STATUSLINE_LABELS_NA`; the ⛏ rung word `⛏n/a` (SL:631) | OWNER (OD-194) | BC-1.05.003 |
| `statusline.glyphs.*` (family, 27 members) | Text | legacy glyph set (OD-02) | exactly 1 code point, measured in legacy's render width (code points — the count legacy's layout uses; OD-184, pass-6 A04), non-empty, no control bytes (one-line output invariant; mirrors BC-2.01.003 PC-3); sole exception `sparkline` = exactly 8 ordered code points (OD-02, OD-184). The East-Asian-Width validation width (OD-170 tables) applies only to the pill-label 1..16 bound (OD-173), not to glyphs — so `watts` U+26A1 (East-Asian-Width W) is 1 column under the glyph rule. COMPLETE MEMBER LIST (with env names via PC-2 `EnvName`; defaults verified against legacy, pass-5 A18/calls 1-2; order, names and consumer cites unified verbatim with BC-2.01.004 PC-6, pass-5 residual sweep): `tools` U+25A4 (SL:1167; BC-1.02.007), `conversation` U+2759 (SL:1167; BC-1.02.007), `thinking` U+25C8 (SL:1167; BC-1.02.007), `lines_up` U+25B2 (SL:537; BC-1.02.014), `lines_down` U+25BC (SL:537; BC-1.02.014), `timer` U+23F1 (SL:549; BC-1.02.015, BC-1.02.028), `window_age` U+2302 (SL:562; BC-1.02.017, BC-1.02.028), `tokens_up` U+2191 (SL:587; BC-1.02.018), `write` U+270D (SL:592; BC-1.02.018), `cache_read` U+27F3 (SL:594; renamed from `reroute` — not shipped, no alias; pass-5 call 2; BC-1.02.018), `tokens_down` U+2193 (SL:597; BC-1.02.018), `cache_rebuild` U+21BB (SL:598-599; renamed from `stale`, as above; BC-1.02.018), `cache_hit` U+267B (SL:479; BC-1.02.008, BC-1.02.023), `lane` U+25E8 (SL:447-449 main pill AND SL:906-907 subagent tag; BC-1.02.001, BC-1.07.006), `git` U+2387 (SL:413; BC-1.02.005), `cell_on` U+25B0 (SL:428 thermometer, SL:761 KV; BC-1.02.006, BC-1.04.007, BC-1.04.015), `cell_off` U+25B1 (as above), `cost_pick` U+26CF (SL:631/635; BC-1.02.029, BC-1.05.003), `telemetry_dot` U+25C9 (SL:730; BC-1.04.005 — dot colour coupled to BC-1.04.004), `degraded` U+25CC (SL:696; BC-1.04.004), `ttft` U+25D4 (SL:797/799; BC-1.04.010, BC-1.04.019), `watts` U+26A1 (SL:813; BC-1.04.011), `idle` U+263E (SL:834; BC-1.04.012, BC-1.04.017), `box_rate` U+25A3 (SL:783; BC-1.04.008), `sess_rate` U+00BB (SL:781; BC-1.04.018 — value from BC-1.03.010; shared default with `subagent.glyphs.running`, independent key), `host` U+21BA (SL:762; BC-1.04.007), `sparkline` U+2581..U+2588 ramp (SL:136; BC-1.04.009). The subagent lane-tag WORDS come from the OD-173 keys `statusline.pill.label_local`/`label_cloud` (BC-1.07.006 joins BC-1.02.001 as a consumer); the subagent token colour is `statusline.theme.cyan` and the model/clock colour `statusline.theme.grey` (pass-5 C03 product-owner part) | J (OD-02) | BC-1.02.001/.005/.006/.007/.008/.014/.015/.017/.018/.023/.028/.029, BC-1.04.004/.005/.007/.008/.009/.010/.011/.012/.015/.017/.018/.019, BC-1.05.003, BC-1.07.006 |

Seconds-class note (pass-5 A14): the Duration ceiling `<= 9223372036.854775` (int64
nanoseconds; OD-164 number-range case) applies to EVERY `Seconds`-type row in the table
above — `telemetry.ttl_s`, `git.ttl_s`, `limits.keep_s`, `cost.window_s`,
`cost.record_throttle_s`, `telemetry.timeout_s`, `fresh_s`, `keep_dead_s`,
`ttft.integer_from_s`, `ttft.yellow_s`, `idle.after_s`, `sparkline.max_age_s`,
`sparkline.min_gap_s` — in addition to any per-key range (BC-2.02.002 is authoritative).
The `git.ttl_s` exception (pass-3 B08) waives the `>= 0` floor only, not the ceiling; its
ceiling is mirrored by a floor of `-9223372036.854775` (the Duration ceiling's magnitude,
negated): a value below the floor is rejected as `out of range`, so the conversion
well-definedness invariant holds for the exception too (BC-2.02.002 check 3 mirror,
ADV-P5-D11; pass-7 A06).

Default-only parameters (the owning BC hard-codes the formula and leaves non-default
values undefined — non-default behavior: see the BC; per OD-162 such a key's valid range
is its default value only, any other value being a number-range config error):
`statusline.units.context` (default-only because the fixed M/K divisors are format
constants that define the unit spellings — the widget formula itself is now parameterized
on `cells`; pass-4 B10), `statusline.theme.heat` (BC-1.02.019's HSV gradient is defined
only for the default triple; pass-4 B01),
`statusline.units.lines` (BC-1.02.014), `statusline.units.tokens` (BC-1.02.025),
`statusline.limits.windows` (BC-1.02.010).

Exact env spellings of the default-only defaults (binding, pass-6 A13/call 8): a
default-only key compares the PARSED env value to the default, and the env spellings are
`HYLO_STATUSLINE_UNITS_CONTEXT=K`;
`HYLO_STATUSLINE_THEME_HEAT=[0.22,0.85,0.80]` (strict-JSON array of 3 numbers — the
Default table cell above carries this env spelling, pass-8 D06/call 11);
`HYLO_STATUSLINE_UNITS_LINES=k`; `HYLO_STATUSLINE_UNITS_TOKENS=M`;
`HYLO_STATUSLINE_LIMITS_WINDOWS=5h,7d` (comma-list grammar, OD-74). Any other parse that
differs from the default after parsing is a number-range config error (OD-162).

Unit-selector default spellings resolved (pass-7 A04/A05/D01, orchestrator call 5): each
unit-selector key's Default cell is the SINGLE code point the parsed env value is compared
to — this is the cell that lands in `legacy_defaults.golden` — while the k/M pair in each
row's Range cell is the key's registered RENDER semantics (the suffixes the widget paints),
unchanged. The three siblings pick different letters, derived from the bytes legacy
renders: `units.lines` = `k` — the compact tier of `_fmt_lines` paints lowercase `k`
(SL:858, `n // 1000` + `k`); `units.tokens` = `M` — the token formatter's million tier
paints uppercase `M` (SL:870, `f"{n / 1e6:.1f}M"`, the approved-mockup docstring's own
example "88.0M"); `units.context` = `K` — the context denominator below 1e6 paints
uppercase `K` (SL:436; BC-1.02.006 "else `K`"). Case follows the rendered byte per
formatter (lowercase `k` in the line/token formatters, uppercase `K` in the context
denominator); which of a widget's two rendered suffixes NAMES the key default is a
convention ratified by the orchestrator call (lines named by its lower tier, tokens by its
million tier, so the two sibling selectors' golden cells stay distinct).
`statusline.context.cells`, `statusline.context.plain_max`, `statusline.context.red_from`
are NOT default-only any more: BC-1.02.006 PC3-PC5 now
define non-default behavior, and their ranges are registered in the table above
(pass-3 B07; heat rejoined the default-only list above — pass-4 B01). Likewise
`statusline.kv.cells` (BC-1.04.007) and
`statusline.queue.yellow` (BC-1.04.006; OD-175) are NOT default-only any more: both BCs now
define non-default behavior, and their ranges are registered in the table above
(pass-2 C2-04). Pass-3 A14/C05 registration: the subagent panel keys
(`statusline.subagent.glyphs.*`, `colors.*`, `joiner`, `tokens.*`) now carry registry
rows — superseding BC-1.07.005's "pin `_SUB_GLYPH` as a Go map literal" wording and
sourcing the panel's glyphs/colors/joiner/token thresholds from config (D15); the
sibling BC amendments have landed (BC-1.07.005's modified 1.1.2 entry "... sourced from
statusline.subagent.* config keys"; pass-4 A18).

OD-162 registration sweep (adv-p2 sync SC-09, 2026-11-18T05:30:00Z): every dotted key
named in a BC body now carries a row above — 48 rows added in that burst (15
`statusline.theme.*` members replacing the former family row, 32 individual tail keys,
1 `statusline.glyphs.*` family row; the family row stands for the familywide rule —
individual members ARE named in BC bodies where their widgets consume them
(e.g. BC-1.02.001/.005/.006/.008/.018/.023; pass-6 B15). Pass-4 registration addendum
(ADV-P4-A05/B15/C05/C07, rulings OD-173/OD-174): `statusline.labels.input`,
`statusline.pill.label_local`/`label_cloud`/`label_unknown`,
`statusline.sparkline.preempt_marker_above`, `statusline.subagent.glyphs.unknown`,
`statusline.subagent.tokens.suffix` added; `statusline.cost.basis_min_shown_usd`
renamed to `statusline.cost.display_floor_usd`; BC-2.01.004 enumerates every
`statusline.glyphs.*` and `statusline.subagent.glyphs.*` member with env names in the
same burst. Pass-5 registration addendum (ADV-P5-A18/B03, orchestrator calls 1-2; ruling
OD-179): `statusline.lane.reroute_all_prefixes` added; the glyph family grows from 13 to
27 members (adds `lane`, `git`, `cell_on`, `cell_off`, `cost_pick`, `sparkline`,
`telemetry_dot`, `degraded`, `host`, `sess_rate`, `box_rate`, `ttft`, `watts`,
`idle`) and renames `reroute` → `cache_read`, `stale` → `cache_rebuild` (not shipped, no
alias); BC-2.01.004 PC-6 and this row were unified name-for-name in the pass-5 residual
sweep (2026-11-19). Pass-7 registration addendum (OD-188/OD-189):
`statusline.cache.rename_retry_limit`, `statusline.labels.vllm_down`,
`statusline.labels.lmcache_down`, `statusline.subagent.name_fallback` added.
Pass-11 registration addendum (OD-194, ADV-P11-C2-03): the nine readable label words
became Text keys `statusline.labels.old` / `rate` / `queue` / `kv` / `host` / `tps` /
`max` / `idle` / `na` (defaults = the exact legacy words; range = the OD-194 label rule);
a sweep of the legacy render region (SL:415-850) found no further unkeyed readable word —
the remaining painted alphanumerics are unit and punctuation marks (`->`, `·`, `/`, `[`,
`]`, `?`, the dead-rung ` ?`, ` <1%`, `W`, `s`, `m`, `h`, `d`, `%`, `K`/`k`/`M`) and stay
named format constants with why-not-config notes per OD-194.
Deliberately NOT registry keys
(setting them yields only the unknown-setting warning, BC-2.01.002 PC-7, OD-123):
`statusline.telemetry.url` and `routing.local_model_prefixes`. The inert key
`statusline.window_age.ps_timeout_s` was removed by OD-147 (BC-3.02.001) and is likewise
not registered. Judgment-label calls worth owner eyes: `statusline.telemetry.timeout_s`
(finite Float > 0, validation ceiling `<= 25` — a <= 0 timeout has no legacy-covered
behavior; the ceiling is the pass-7 A21 judgment call) and
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
(OD-111/OD-123); the `backends[0].metrics_url` default is not an exception (legacy's own
default at SL:73 is the identical address `http://192.0.2.10:8428` — the RFC 5737
placeholder is legacy behavior, not a hylo divergence; pass-5 A25 verified). Unknown `HYLO_*` variables warn on stderr
(`hylo: warning: unknown setting <NAME> (ignored)`) and never change exit status
(BC-2.01.001).

Per-OS directories (BC-3.01.001, OD-144): relative or empty `XDG_*` values are ignored
(XDG spec); on Windows the cache and state directories are separate subdirectories
`%LOCALAPPDATA%\hylo\cache` and `%LOCALAPPDATA%\hylo\state`. `hylo config path` prints
all three resolved paths, one per line, labels and order fixed (`config:`, `cache:`,
`state:`; OD-132, BC-2.03.002) — the **effective** paths (OD-165): exactly the values
the running binary resolves, overrides honored the same way the status line honors them.

## JSON Output Schema

MAIN-mode statusline emits no JSON on stdout: every MAIN statusline outcome is the byte
contract above (happy path, degraded ladder, config-error line, unknown-flag line), and
`config validate` / `config path` emit plain text lines. The one JSON emitter in P1 is
the `--subagent` panel: NDJSON stdout rows `{"id": <task id>, "content": <rendered row>}`
— property order id-then-content, CPython default separators (`, ` and `: `),
`ensure_ascii=True`, one LF-terminated line per eligible task in input order, zero-byte
outcomes legitimate (renderer off, zero eligible rows, config error per OD-168,
unparseable/non-object stdin absorbed per BC-1.07.003) (BC-1.07.004; pass-9 A01). The
only JSON INPUT surfaces in P1 are the stdin payloads (MAIN contract:
`## stdin JSON Contract (statusline)` above; subagent payload: the subsection above).
When the config-file layer arrives in P4 (OD-107), its parse errors surface as D4-EX-3
config errors and this section will document the file-parse output schema.

## Config File Schema

None in P1: configuration is `HYLO_*` env over built-in defaults; the file layer and its
YAML dependency arrive in P4 (OD-107). The key universe, types, ranges, defaults and
rationales that the P4 file layer must mirror key-for-key are the `HYLO_*` Key Schema
above (registry: BC-2.01.004 + golden `internal/config/testdata/legacy_defaults.golden`);
comma-list encoding for list values in env is OD-74.

## Flag Interactions

| Flag A | Flag B | Interaction | Resolution |
|---|---|---|---|
| unknown flag | config error | unknown flag wins | flag check precedes `config.Load` (BC-4.01.002) |
| `--config <path>` | `HYLO_CONFIG` | flag overrides env | BC-2.03.002 |
| `HYLO_*` env | built-in default | env overrides default; file layer absent in P1 (OD-107) | BC-2.01.001 |
| first unknown flag | later unknown flags | first is rendered; all go to stderr | BC-4.01.002 |
| first config error | later config errors | first in registry order is rendered; all to stderr | BC-2.02.001 |
| `--subagent` (anywhere in argv, incl. after a bare `--`) | unknown flag | `--subagent` wins: the renderer is selected before the statusline flag scan (pass-3 A01); the subagent path resolves config itself (OD-168, pass-12 A10) | BC-1.07.001, BC-4.01.002 |
| `--subagent` | config error | zero stdout bytes; ALL reason lines (the full list) on stderr, exit 0 | OD-168, BC-1.07.002 |
| `--subagent` | `statusline.subagent.enabled=false` | panel gated off by the off switch (BC-1.07.002 contracts the outcome) | BC-1.07.002 |
| `--subagent` | stdin render | subagent-mode config error vs row rendering: zero-byte and NDJSON row outputs are both legitimate stdout outcomes | BC-1.07.002/.003/.004 |
