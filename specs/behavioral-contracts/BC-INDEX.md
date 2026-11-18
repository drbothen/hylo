---
artifact_type: bc-index
document_type: bc-index
level: L3
version: "0.2.9"
status: draft
producer: product-owner
timestamp: 2026-11-19T14:00:00Z
phase: 1a
stage: "3 of 3 (integration)"
origin: greenfield
capability: register
lifecycle_status: active
introduced: "0.1"
modified: "0.2.9"
extracted_from: "behavioral-contracts/ss-01..ss-06 frontmatter and H1 headings (generated; do not hand-edit rows)"
deprecated: "n.a."
deprecated_by: "n.a."
replacement: "n.a."
retired: "n.a."
removed: "n.a."
removal_reason: "n.a."
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
input-hash: "c5a28b3"
traces_to: ../prd.md

---

# BC-INDEX: hylo P1 behavioral contracts (all 154, stage 3)

> **Generated index.** One row per behavioral-contract file, built from each file's
> frontmatter and H1 heading (bc_h1_is_title_source_of_truth: the title column is the
> file's H1 verbatim). Links are relative to this directory. The authoritative mapping
> (including writer groups and primary sources) is `BC-ALLOCATION.md`; per-contract
> detail is in the linked file. All rows are status draft at stage 3.
>
> **Totals.** 154 contracts: 101 in S1, 13 in S2, 3 in S3, 3 in S4, 20 in S5, 14 in S6.
> 108 mapped from legacy BC-SL-001..103 (incl. the BC-SL-097 fan-out), 46 new; the two
> accounting exceptions are in the table below.
>
> Revision note (2026-11-15, OD-132..OD-145): +7 contracts (BC-2.02.006 boolean class;
+6 pyfmt helper contracts per OD-141); titles are the file H1s verbatim.
>
> Revision note (2026-11-17, OD-155): +8 contracts, new group S1.07 (subagent panel
> rows; BC-SL-097 restored to scope from OD-14 OOS); titles are the file H1s verbatim.
>
> Revision note (2026-11-18, pass-3 remediation sync): +1 contract, BC-5.01.007
> (ADV-P3-D08); titles are the file H1s verbatim.
>
> Revision note (2026-11-17, pass-4 remediation sync): BC-1.02.003 title enriched to the
> postcondition's selection order (pass-4 B17, ruled text; BC file H1 to be synced by the
> BC agent in the same burst); BC-1.03.015 parity column corrected to `OD-161` (pass-4
> C10 — frontmatter and traceability already said OD-161). Titles are the file H1s
> verbatim modulo table pipe escaping.
>
> Revision note (2026-11-18, pass-5 remediation sync): parity columns corrected to the
> frontmatter state — BC-1.05.004 → `OD-166`, BC-1.05.009 → `OD-30, OD-166` (pass-5
> C2-07); BC-1.07.002 → `byte-exact` with the disabled (OD-155 off-switch) half described
> in the new Parity-class notes section (pass-5 C16). Titles are the file H1s verbatim
> modulo table pipe escaping.

### S1.01 — Input/output contract

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-1.01.001 | Guard prints the 29-byte degraded line and exits 0 | S1.01 | BC-SL-001 | byte-exact | H | draft | [BC-1.01.001](ss-01/BC-1.01.001.md) |
| BC-1.01.002 | Non-JSON or non-object stdin decodes to an empty object | S1.01 | BC-SL-002 | byte-exact | H | draft | [BC-1.01.002](ss-01/BC-1.01.002.md) |
| BC-1.01.003 | Rows join with LF; width hides row 2 only when rows == 2 | S1.01 | BC-SL-003 | byte-exact | H | draft | [BC-1.01.003](ss-01/BC-1.01.003.md) |
| BC-1.01.004 | Visible width counts code points after stripping SGR | S1.01 | BC-SL-004 | byte-exact | H | draft | [BC-1.01.004](ss-01/BC-1.01.004.md) |
| BC-1.01.005 | COLUMNS parses with the Python int grammar, else 0 | S1.01 | BC-SL-005 | byte-exact | H | draft | [BC-1.01.005](ss-01/BC-1.01.005.md) |
| BC-1.01.006 | trim_to_fit double-resets; single reset on the recycle row | S1.01 | BC-SL-054 | byte-exact | H | draft | [BC-1.01.006](ss-01/BC-1.01.006.md) |
| BC-1.01.007 | Negative COLUMNS disables trim and hides row 2 only when rows == 2 | S1.01 | BC-SL-055 | byte-exact | H | draft | [BC-1.01.007](ss-01/BC-1.01.007.md) |
| BC-1.01.008 | Strict UTF-8 stdio; invalid stdin UTF-8 renders from {} | S1.01 | BC-SL-076 | byte-exact | H | draft | [BC-1.01.008](ss-01/BC-1.01.008.md) |
| BC-1.01.009 | Side effects run in legacy order; a degrade keeps earlier writes | S1.01 | BC-SL-077 | byte-exact | M | draft | [BC-1.01.009](ss-01/BC-1.01.009.md) |
| BC-1.01.010 | Trim breakpoint matrix across widths | S1.01 | BC-SL-090 | byte-exact | H | draft | [BC-1.01.010](ss-01/BC-1.01.010.md) |

### S1.02 — Row-1 widgets

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-1.02.001 | Lane pill derives from model-prefix startswith match | S1.02 | BC-SL-006 | byte-exact | H | draft | [BC-1.02.001](ss-01/BC-1.02.001.md) |
| BC-1.02.002 | Model label falls back display_name → id → "?" | S1.02 | BC-SL-007 | byte-exact | H | draft | [BC-1.02.002](ss-01/BC-1.02.002.md) |
| BC-1.02.003 | Project label: basename(normpath(project_dir \| current_dir \| cwd)) | S1.02 | BC-SL-008 | byte-exact | H | draft | [BC-1.02.003](ss-01/BC-1.02.003.md) |
| BC-1.02.004 | Branch walk reads .git dir or file and HEAD | S1.02 | BC-SL-009 | byte-exact | H | draft | [BC-1.02.004](ss-01/BC-1.02.004.md) |
| BC-1.02.005 | Branch segment cached with a 5 s TTL | S1.02 | BC-SL-010 | byte-exact | H | draft | [BC-1.02.005](ss-01/BC-1.02.005.md) |
| BC-1.02.006 | Context thermometer and its denominator | S1.02 | BC-SL-011 | byte-exact | H | draft | [BC-1.02.006](ss-01/BC-1.02.006.md) |
| BC-1.02.007 | Composition percentage rounds half-even | S1.02 | BC-SL-012 | byte-exact | H | draft | [BC-1.02.007](ss-01/BC-1.02.007.md) |
| BC-1.02.008 | Cache-hit segment | S1.02 | BC-SL-013 | byte-exact | H | draft | [BC-1.02.008](ss-01/BC-1.02.008.md) |
| BC-1.02.009 | Limits segment hidden on reroute-all prefixes | S1.02 | BC-SL-014 | byte-exact | H | draft | [BC-1.02.009](ss-01/BC-1.02.009.md) |
| BC-1.02.010 | Expired rate-limit window is unreported | S1.02 | BC-SL-015 | byte-exact | H | draft | [BC-1.02.010](ss-01/BC-1.02.010.md) |
| BC-1.02.011 | Pace and absolute colour bands | S1.02 | BC-SL-016 | byte-exact | H | draft | [BC-1.02.011](ss-01/BC-1.02.011.md) |
| BC-1.02.012 | Countdown format and the 1.15 gate | S1.02 | BC-SL-017 | byte-exact | M | draft | [BC-1.02.012](ss-01/BC-1.02.012.md) |
| BC-1.02.013 | Rate-limit smoothing over 1800 s | S1.02 | BC-SL-018 | byte-exact | H | draft | [BC-1.02.013](ss-01/BC-1.02.013.md) |
| BC-1.02.014 | Lines segment formats via _fmt_lines | S1.02 | BC-SL-019 | byte-exact | H | draft | [BC-1.02.014](ss-01/BC-1.02.014.md) |
| BC-1.02.015 | Timer segment formats via _hm | S1.02 | BC-SL-020 | byte-exact | H | draft | [BC-1.02.015](ss-01/BC-1.02.015.md) |
| BC-1.02.016 | API-time suffix | S1.02 | BC-SL-021 | byte-exact | H | draft | [BC-1.02.016](ss-01/BC-1.02.016.md) |
| BC-1.02.017 | Window-age suffix (⌂) with its visibility gate | S1.02 | BC-SL-022 | byte-exact | M | draft | [BC-1.02.017](ss-01/BC-1.02.017.md) |
| BC-1.02.018 | Token segment formats via _fmt_tok_c | S1.02 | BC-SL-024 | byte-exact | H | draft | [BC-1.02.018](ss-01/BC-1.02.018.md) |
| BC-1.02.019 | heat() HSV cell colours | S1.02 | BC-SL-056 | byte-exact | H | draft | [BC-1.02.019](ss-01/BC-1.02.019.md) |
| BC-1.02.020 | Thermometer quirks (/0K, /1000K, NaN crash) | S1.02 | BC-SL-057 | byte-exact | H | draft | [BC-1.02.020](ss-01/BC-1.02.020.md) |
| BC-1.02.021 | Model label str() of a non-str value | S1.02 | BC-SL-058 | byte-exact | M | draft | [BC-1.02.021](ss-01/BC-1.02.021.md) |
| BC-1.02.022 | POSIX normpath keeps // | S1.02 | BC-SL-059 | byte-exact | M | draft | [BC-1.02.022](ss-01/BC-1.02.022.md) |
| BC-1.02.023 | Cache-hit NaN/inf rendering | S1.02 | BC-SL-060 | byte-exact | H | draft | [BC-1.02.023](ss-01/BC-1.02.023.md) |
| BC-1.02.024 | Pace band boundary at rem = 0.9 × length | S1.02 | BC-SL-061 | byte-exact | H | draft | [BC-1.02.024](ss-01/BC-1.02.024.md) |
| BC-1.02.025 | _fmt_tok_c performs no unit promotion | S1.02 | BC-SL-062 | byte-exact | H | draft | [BC-1.02.025](ss-01/BC-1.02.025.md) |
| BC-1.02.026 | _fmt_lines OverflowError on inf degrades (CP-S11) | S1.02 | BC-SL-063 | byte-exact | H | draft | [BC-1.02.026](ss-01/BC-1.02.026.md) |
| BC-1.02.027 | _hm ValueError on inf degrades (CP-S12/S13) | S1.02 | BC-SL-064 | byte-exact | H | draft | [BC-1.02.027](ss-01/BC-1.02.027.md) |
| BC-1.02.028 | Window-age duration format | S1.02 | BC-SL-081 | byte-exact | H | draft | [BC-1.02.028](ss-01/BC-1.02.028.md) |
| BC-1.02.029 | Pick eq threshold 0.005 | S1.02 | BC-SL-083 | byte-exact | H | draft | [BC-1.02.029](ss-01/BC-1.02.029.md) |
| BC-1.02.030 | effective_rl sequence with sticky CP-S09 | S1.02 | BC-SL-093 | byte-exact | H | draft | [BC-1.02.030](ss-01/BC-1.02.030.md) |

### S1.03 — Transcript parsing

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-1.03.001 | No transcript path yields no transcript state | S1.03 | BC-SL-030 | byte-exact | H | draft | [BC-1.03.001](ss-01/BC-1.03.001.md) |
| BC-1.03.002 | Mix cache name and mixv6 reset rules | S1.03 | BC-SL-031 | byte-exact | H | draft | [BC-1.03.002](ss-01/BC-1.03.002.md) |
| BC-1.03.003 | 512 KB read step with long-line completion | S1.03 | BC-SL-032 | byte-exact | H | draft | [BC-1.03.003](ss-01/BC-1.03.003.md) |
| BC-1.03.004 | bytes.splitlines + per-line json.loads | S1.03 | BC-SL-033 | byte-exact | M | draft | [BC-1.03.004](ss-01/BC-1.03.004.md) |
| BC-1.03.005 | Usage dedup per message id (memory 256) | S1.03 | BC-SL-034 | byte-exact | H | draft | [BC-1.03.005](ss-01/BC-1.03.005.md) |
| BC-1.03.006 | Usage accumulation across int/float/big-int | S1.03 | BC-SL-035 | byte-exact | M | draft | [BC-1.03.006](ss-01/BC-1.03.006.md) |
| BC-1.03.007 | Rebuild rule at 20,000 excess input tokens | S1.03 | BC-SL-036 | byte-exact | H | draft | [BC-1.03.007](ss-01/BC-1.03.007.md) |
| BC-1.03.008 | compact_boundary resets composition and pp | S1.03 | BC-SL-037 | byte-exact | H | draft | [BC-1.03.008](ss-01/BC-1.03.008.md) |
| BC-1.03.009 | Composition per block from json.dumps lengths | S1.03 | BC-SL-038 | byte-exact | M | draft | [BC-1.03.009](ss-01/BC-1.03.009.md) |
| BC-1.03.010 | Last-turn rate machine | S1.03 | BC-SL-039 | byte-exact | H | draft | [BC-1.03.010](ss-01/BC-1.03.010.md) |
| BC-1.03.011 | First line of a message supplies its usage | S1.03 | BC-SL-065 | byte-exact | H | draft | [BC-1.03.011](ss-01/BC-1.03.011.md) |
| BC-1.03.012 | Short + long line completes over two refreshes | S1.03 | BC-SL-066 | byte-exact | H | draft | [BC-1.03.012](ss-01/BC-1.03.012.md) |
| BC-1.03.013 | Mix cache sid sanitized per code point | S1.03 | BC-SL-070 | byte-exact | H | draft | [BC-1.03.013](ss-01/BC-1.03.013.md) |
| BC-1.03.014 | text/thinking block value types | S1.03 | BC-SL-072 | byte-exact | H | draft | [BC-1.03.014](ss-01/BC-1.03.014.md) |
| BC-1.03.015 | transcript_path type semantics (truthy int → no transcript, no descriptor I/O) | S1.03 | BC-SL-088 | OD-161 | M | draft | [BC-1.03.015](ss-01/BC-1.03.015.md) |
| BC-1.03.016 | Turn-machine exhaustive table (20 rows) | S1.03 | BC-SL-094 | byte-exact | H | draft | [BC-1.03.016](ss-01/BC-1.03.016.md) |
| BC-1.03.017 | Turn identity ignores seen_ids | S1.03 | BC-SL-095 | byte-exact | H | draft | [BC-1.03.017](ss-01/BC-1.03.017.md) |
| BC-1.03.018 | D4-EX-2 wrong-shape line W-predicates (skip, no partial mutation) | S1.03 | BC-SL-098 | D4-EX-2 | M | draft | [BC-1.03.018](ss-01/BC-1.03.018.md) |
| BC-1.03.019 | D4-EX-2 table tests (21 rows, exact expected caches) | S1.03 | BC-SL-099 | D4-EX-2 | H | draft | [BC-1.03.019](ss-01/BC-1.03.019.md) |
| BC-1.03.020 | Legacy-poisoned cur.out reader rule (OD-32) | S1.03 | BC-SL-100 | D4-EX-2 | M | draft | [BC-1.03.020](ss-01/BC-1.03.020.md) |
| BC-1.03.021 | cur with t0 null and non-numeric out kept verbatim | S1.03 | BC-SL-103 | byte-exact | H | draft | [BC-1.03.021](ss-01/BC-1.03.021.md) |

### S1.04 — Row-2 telemetry, metrics client, freshness

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-1.04.001 | fetch_sample: query, 1.5 s timeout, first-wins | S1.04 | BC-SL-040 | byte-exact | M | draft | [BC-1.04.001](ss-01/BC-1.04.001.md) |
| BC-1.04.002 | get_sample TTL / KEEP_DEAD state machine | S1.04 | BC-SL-041 | byte-exact | H | draft | [BC-1.04.002](ss-01/BC-1.04.002.md) |
| BC-1.04.003 | History point rules (90 s cap, 2 s gap) | S1.04 | BC-SL-042 | byte-exact | H | draft | [BC-1.04.003](ss-01/BC-1.04.003.md) |
| BC-1.04.004 | Freshness ladder + stale suffix | S1.04 | BC-SL-043 | byte-exact | H | draft | [BC-1.04.004](ss-01/BC-1.04.004.md) |
| BC-1.04.005 | Health dot | S1.04 | BC-SL-044 | byte-exact | H | draft | [BC-1.04.005](ss-01/BC-1.04.005.md) |
| BC-1.04.006 | Queue segment | S1.04 | BC-SL-045 | byte-exact | H | draft | [BC-1.04.006](ss-01/BC-1.04.006.md) |
| BC-1.04.007 | KV segment | S1.04 | BC-SL-046 | byte-exact | H | draft | [BC-1.04.007](ss-01/BC-1.04.007.md) |
| BC-1.04.008 | Throughput segments | S1.04 | BC-SL-047 | byte-exact | H | draft | [BC-1.04.008](ss-01/BC-1.04.008.md) |
| BC-1.04.009 | Sparkline glyphs, scale and colors | S1.04 | BC-SL-048 | byte-exact | H | draft | [BC-1.04.009](ss-01/BC-1.04.009.md) |
| BC-1.04.010 | TTFT segment | S1.04 | BC-SL-049 | byte-exact | H | draft | [BC-1.04.010](ss-01/BC-1.04.010.md) |
| BC-1.04.011 | Power segment | S1.04 | BC-SL-050 | byte-exact | H | draft | [BC-1.04.011](ss-01/BC-1.04.011.md) |
| BC-1.04.012 | Idle segment | S1.04 | BC-SL-051 | byte-exact | H | draft | [BC-1.04.012](ss-01/BC-1.04.012.md) |
| BC-1.04.013 | VM fetch whenever ROWS >= 2 | S1.04 | BC-SL-053 | byte-exact | H | draft | [BC-1.04.013](ss-01/BC-1.04.013.md) |
| BC-1.04.014 | Sparkline NaN/+Inf crash path (CP-N02) | S1.04 | BC-SL-073 | byte-exact | H | draft | [BC-1.04.014](ss-01/BC-1.04.014.md) |
| BC-1.04.015 | KV NaN crash path (CP-N01) and cell math | S1.04 | BC-SL-074 | byte-exact | H | draft | [BC-1.04.015](ss-01/BC-1.04.015.md) |
| BC-1.04.016 | Row-2 NaN/inf rendering; wall-colour mismatch | S1.04 | BC-SL-075 | byte-exact | H | draft | [BC-1.04.016](ss-01/BC-1.04.016.md) |
| BC-1.04.017 | Idle strict > 300 and age format | S1.04 | BC-SL-084 | byte-exact | H | draft | [BC-1.04.017](ss-01/BC-1.04.017.md) |
| BC-1.04.018 | Mine (last-turn) segment | S1.04 | BC-SL-085 | byte-exact | H | draft | [BC-1.04.018](ss-01/BC-1.04.018.md) |
| BC-1.04.019 | TTFT format boundaries | S1.04 | BC-SL-086 | byte-exact | H | draft | [BC-1.04.019](ss-01/BC-1.04.019.md) |
| BC-1.04.020 | get_sample pinned sequence and cache key order | S1.04 | BC-SL-091 | byte-exact | M | draft | [BC-1.04.020](ss-01/BC-1.04.020.md) |
| BC-1.04.021 | HIST_MIN_GAP reachability (seeded) | S1.04 | BC-SL-092 | byte-exact | H | draft | [BC-1.04.021](ss-01/BC-1.04.021.md) |

### S1.05 — Cost history + dynamic colors

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-1.05.001 | $ colours from lane percentile thresholds | S1.05 | BC-SL-025 | byte-exact | H | draft | [BC-1.05.001](ss-01/BC-1.05.001.md) |
| BC-1.05.002 | $/h segment with threshold colouring | S1.05 | BC-SL-026 | byte-exact | H | draft | [BC-1.05.002](ss-01/BC-1.05.002.md) |
| BC-1.05.003 | ⛏ pick inside the $ block (basis threshold) | S1.05 | BC-SL-027 | byte-exact | H | draft | [BC-1.05.003](ss-01/BC-1.05.003.md) |
| BC-1.05.004 | record_cost throttled write | S1.05 | BC-SL-028 | OD-166 | H | draft | [BC-1.05.004](ss-01/BC-1.05.004.md) |
| BC-1.05.005 | cost_thresholds p75/p95 percentiles | S1.05 | BC-SL-029 | byte-exact | H | draft | [BC-1.05.005](ss-01/BC-1.05.005.md) |
| BC-1.05.006 | Numeric sid keyed by string form — throttle and self-exclusion hold | S1.05 | BC-SL-079 | OD-30 | H | draft | [BC-1.05.006](ss-01/BC-1.05.006.md) |
| BC-1.05.007 | $, $/h and ⛏ number formatting | S1.05 | BC-SL-082 | byte-exact | H | draft | [BC-1.05.007](ss-01/BC-1.05.007.md) |
| BC-1.05.008 | Cost colouring goldens (21 seeded sessions) | S1.05 | BC-SL-101 | byte-exact | H | draft | [BC-1.05.008](ss-01/BC-1.05.008.md) |
| BC-1.05.009 | record_cost write contract (exact JSON format) | S1.05 | BC-SL-102 | OD-30, OD-166 | H | draft | [BC-1.05.009](ss-01/BC-1.05.009.md) |

### S1.06 — Session caches

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-1.06.001 | Cache load/save: never-raise, raw sid in file names | S1.06 | BC-SL-052 | temp-file | H | draft | [BC-1.06.001](ss-01/BC-1.06.001.md) |
| BC-1.06.002 | Sid with / : failed replace persists nothing; temp handling | S1.06 | BC-SL-078 | temp-file | M | draft | [BC-1.06.002](ss-01/BC-1.06.002.md) |

### S1.07 — Subagent panel rows (OD-155 revision, 2026-11-17)

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-1.07.001 | `--subagent` in argv selects the subagent renderer before main | S1.07 | BC-SL-097 | byte-exact | H | draft | [BC-1.07.001](ss-01/BC-1.07.001.md) |
| BC-1.07.002 | `statusline.subagent.enabled` off switch (default true = legacy) | S1.07 | new (OD-155) | byte-exact | H | draft | [BC-1.07.002](ss-01/BC-1.07.002.md) |
| BC-1.07.003 | Subagent stdin is total — unparseable or non-object input renders zero rows | S1.07 | BC-SL-097 | byte-exact | H | draft | [BC-1.07.003](ss-01/BC-1.07.003.md) |
| BC-1.07.004 | One default-JSON line per eligible task; zero bytes for zero rows | S1.07 | BC-SL-097 | byte-exact | H | draft | [BC-1.07.004](ss-01/BC-1.07.004.md) |
| BC-1.07.005 | Status glyph, name-fallback chain, and settled-status suffix | S1.07 | BC-SL-097 | byte-exact | H | draft | [BC-1.07.005](ss-01/BC-1.07.005.md) |
| BC-1.07.006 | Model segment carries the model-prefix lane tag | S1.07 | BC-SL-097 | byte-exact | H | draft | [BC-1.07.006](ss-01/BC-1.07.006.md) |
| BC-1.07.007 | Token segment (_fmt_tokens) and running-only elapsed clock | S1.07 | BC-SL-097 | byte-exact | H | draft | [BC-1.07.007](ss-01/BC-1.07.007.md) |
| BC-1.07.008 | CP-A01..A05 degrade to the 29-byte line, exit 0 | S1.07 | BC-SL-097 | byte-exact | H | draft | [BC-1.07.008](ss-01/BC-1.07.008.md) |

### S2.01 — Schema + resolution

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-2.01.001 | P1 resolution: HYLO_* env over built-in defaults; no file layer; DGX_* never read | S2.01 | new | n.a. | — | draft | [BC-2.01.001](ss-02/BC-2.01.001.md) |
| BC-2.01.002 | backends array: exactly one entry validated until P6; backends[0].metrics_url / backends[0].model_prefixes; default prefixes claude-sonnet | S2.01 | new | n.a. | — | draft | [BC-2.01.002](ss-02/BC-2.01.002.md) |
| BC-2.01.003 | statusline.theme.* keys for SGR palette, pill codes and separator, legacy defaults | S2.01 | new | n.a. | — | draft | [BC-2.01.003](ss-02/BC-2.01.003.md) |
| BC-2.01.004 | Key registry: every key declares type, range/operator, default and rationale | S2.01 | new | n.a. | — | draft | [BC-2.01.004](ss-02/BC-2.01.004.md) |
| BC-2.01.005 | HYLO_* value grammars: typed bool, comma lists, ~ path expansion; COLUMNS excluded as protocol input | S2.01 | new | n.a. | — | draft | [BC-2.01.005](ss-02/BC-2.01.005.md) |

### S2.02 — Validation + config-error line

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-2.02.001 | D4-EX-3 config-error line: exact format, exit 0, stderr detail, no cache writes | S2.02 | BC-SL-087 | D4-EX-3 | H | draft | [BC-2.02.001](ss-02/BC-2.02.001.md) |
| BC-2.02.002 | Number-range class: non-finite/negative durations are config errors, except the git.ttl_s negative exception; TTL 0 stays valid | S2.02 | new | D4-EX-3 | — | draft | [BC-2.02.002](ss-02/BC-2.02.002.md) |
| BC-2.02.003 | Number-grammar class: underscore and Unicode-digit numerals are config errors | S2.02 | new | D4-EX-3 | — | draft | [BC-2.02.003](ss-02/BC-2.02.003.md) |
| BC-2.02.004 | Enum class: unknown sparkline trace value is a config error | S2.02 | new | D4-EX-3 | — | draft | [BC-2.02.004](ss-02/BC-2.02.004.md) |
| BC-2.02.005 | URL class: non-http(s) metrics URL is a config error | S2.02 | new | D4-EX-3 | — | draft | [BC-2.02.005](ss-02/BC-2.02.005.md) |
| BC-2.02.006 | Boolean class: a non-typed-boolean value is a config error (true\|false\|1\|0\|yes\|no) | S2.02 | new | D4-EX-3 | — | draft | [BC-2.02.006](ss-02/BC-2.02.006.md) |

### S2.03 — Config subcommands

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-2.03.001 | hylo config validate exits non-zero on the same errors as D4-EX-3 | S2.03 | new | n.a. | — | draft | [BC-2.03.001](ss-02/BC-2.03.001.md) |
| BC-2.03.002 | hylo config path prints the config, cache and state paths (OD-132) | S2.03 | new | n.a. | — | draft | [BC-2.03.002](ss-02/BC-2.03.002.md) |

### S3.01 — Per-OS paths

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-3.01.001 | Per-OS cache/config/state dirs (XDG/hylo, LOCALAPPDATA); LocalZone TZ resolution (OS zone, UTC on empty/unparseable) | S3.01 | new | n.a. | — | draft | [BC-3.01.001](ss-03/BC-3.01.001.md) |

### S3.02 — Process start / window age

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-3.02.001 | Window start via native per-OS ancestor probe; whole-second truncation; proc_start key first | S3.02 | BC-SL-023 | D4-EX-1 | M | draft | [BC-3.02.001](ss-03/BC-3.02.001.md) |
| BC-3.02.002 | ps-parse replacement: named per-OS edge differences (macOS/Linux) | S3.02 | BC-SL-080 | OD-76 | M | draft | [BC-3.02.002](ss-03/BC-3.02.002.md) |

### S4.01 — Subcommand dispatch

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-4.01.001 | Dispatch statusline / version / config; statusline exits 0 for any argv | S4.01 | new | n.a. | — | draft | [BC-4.01.001](ss-04/BC-4.01.001.md) |
| BC-4.01.002 | Unknown flag renders one-line error, exit 0, never blank | S4.01 | new | n.a. | — | draft | [BC-4.01.002](ss-04/BC-4.01.002.md) |
| BC-4.01.003 | hylo version prints the version string | S4.01 | new | n.a. | — | draft | [BC-4.01.003](ss-04/BC-4.01.003.md) |

### S5.01 — Numbers/rounding

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-5.01.001 | Round/RoundN/F: half-even, decimal re-round, 'f' format incl. -0; nan/inf/-inf spellings | S5.01 | new | n.a. | — | draft | [BC-5.01.001](ss-05/BC-5.01.001.md) |
| BC-5.01.002 | ParseInt/ParseFloat Python grammar: underscores, Unicode digits, signs, 4,300-digit limit, nan/inf/1e400 | S5.01 | new | n.a. | — | draft | [BC-5.01.002](ss-05/BC-5.01.002.md) |
| BC-5.01.003 | CPython float divmod/mod; Int/Ceil typed NaN/Overflow errors; Max/Min NaN argument order | S5.01 | new | n.a. | — | draft | [BC-5.01.003](ss-05/BC-5.01.003.md) |
| BC-5.01.004 | pyfmt.D: {:d} decimal formatting with width and zero-pad | S5.01 | new | n.a. | — | draft | [BC-5.01.004](ss-05/BC-5.01.004.md) |
| BC-5.01.005 | pyfmt.Repr: CPython float repr (shortest round-trip, .0 suffix, inf/nan spellings) | S5.01 | new | n.a. | — | draft | [BC-5.01.005](ss-05/BC-5.01.005.md) |
| BC-5.01.006 | pyfmt.MaxSeq: Python max() over a sequence with first-maximal-wins NaN order | S5.01 | new | n.a. | — | draft | [BC-5.01.006](ss-05/BC-5.01.006.md) |
| BC-5.01.007 | Mixed int/float Num semantics: float(int) ErrOverflow bound, true division, exact comparison, Max/Min exact ties | S5.01 | new | n.a. | — | draft | [BC-5.01.007](ss-05/BC-5.01.007.md) |

### S5.02 — JSON byte semantics

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-5.02.001 | json.dumps length rules (escaping, float repr, inner-null 0) | S5.02 | BC-SL-071 | byte-exact | H | draft | [BC-5.02.001](ss-05/BC-5.02.001.md) |
| BC-5.02.002 | json.dumps length oracle (63 cases) | S5.02 | BC-SL-096 | byte-exact | H | draft | [BC-5.02.002](ss-05/BC-5.02.002.md) |
| BC-5.02.003 | json.loads(bytes) acceptance set: BOM/UTF-16/32, invalid UTF-8, depth, NaN, duplicates | S5.02 | BC-SL-067 | byte-exact | M | draft | [BC-5.02.003](ss-05/BC-5.02.003.md) |
| BC-5.02.004 | Ordered object Value: insertion order, last-wins keeps position, Delete; WTF-8 strings | S5.02 | new | n.a. | — | draft | [BC-5.02.004](ss-05/BC-5.02.004.md) |
| BC-5.02.005 | pyfmt.Str: Python str() of values (str unchanged, non-str via repr) | S5.02 | new | n.a. | — | draft | [BC-5.02.005](ss-05/BC-5.02.005.md) |
| BC-5.02.006 | pyfmt.Dumps: json.dump cache-file bytes (separators, ensure_ascii, float repr, order) | S5.02 | new | n.a. | — | draft | [BC-5.02.006](ss-05/BC-5.02.006.md) |

### S5.03 — Code-point string ops

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-5.03.001 | Len/Truncate/HasSurrogate: code points, surrogate = 1, not terminal cells | S5.03 | new | n.a. | — | draft | [BC-5.03.001](ss-05/BC-5.03.001.md) |
| BC-5.03.002 | Strip/RStrip/RSplit1/SplitLinesBytes: Python whitespace; \n \r\n \r only | S5.03 | new | n.a. | — | draft | [BC-5.03.002](ss-05/BC-5.03.002.md) |
| BC-5.03.003 | SubNonWord per code point before truncation; EncodeUTF8Replace lone surrogate → ? | S5.03 | new | n.a. | — | draft | [BC-5.03.003](ss-05/BC-5.03.003.md) |
| BC-5.03.004 | PosixNormpath/NtNormpath/Basename per-OS selection (ntpath on Windows) | S5.03 | new | n.a. | — | draft | [BC-5.03.004](ss-05/BC-5.03.004.md) |

### S5.04 — Time semantics

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-5.04.001 | FromISOFormat: 3.11 grammar, naive = local, fraction truncation beyond µs | S5.04 | BC-SL-069 | byte-exact | M | draft | [BC-5.04.001](ss-05/BC-5.04.001.md) |
| BC-5.04.002 | LocalToUnix: CPython _mktime port, gap/overlap semantics, TZ injection, embedded tzdata | S5.04 | new | n.a. | — | draft | [BC-5.04.002](ss-05/BC-5.04.002.md) |
| BC-5.04.003 | pyfmt.TimeFloat: Python time.time() value discipline (ns→s float, once per render) | S5.04 | new | n.a. | — | draft | [BC-5.04.003](ss-05/BC-5.04.003.md) |

### S6.01 — Oracle execution

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-6.01.001 | Oracle runs via explicit absolute CPython 3.11.x path, never PATH; invoked with -s, never -I/-E | S6.01 | new | n.a. | — | draft | [BC-6.01.001](ss-06/BC-6.01.001.md) |
| BC-6.01.002 | Child environment constructed from scratch: no *_proxy, fixed HOME/TMPDIR/locale | S6.01 | new | n.a. | — | draft | [BC-6.01.002](ss-06/BC-6.01.002.md) |
| BC-6.01.003 | Clock shim freezes time functions from HYLO_TEST_NOW, stepped per refresh; canary fails if shim absent | S6.01 | new | n.a. | — | draft | [BC-6.01.003](ss-06/BC-6.01.003.md) |

### S6.02 — Fixture corpus

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-6.02.001 | Committed corpus synthetic-only; owner real inputs replayed from git-ignored captures/ | S6.02 | new | n.a. | — | draft | [BC-6.02.001](ss-06/BC-6.02.001.md) |
| BC-6.02.002 | stdin-sequence replay of captured sessions: ordered snapshots, clock advanced per step | S6.02 | new | n.a. | — | draft | [BC-6.02.002](ss-06/BC-6.02.002.md) |
| BC-6.02.003 | Case model: stdin template + translated settings + metrics mode + seeds + steps | S6.02 | new | n.a. | — | draft | [BC-6.02.003](ss-06/BC-6.02.003.md) |
| BC-6.02.004 | Cache-swap coverage: Python-writes/Go-reads and reverse, all four caches | S6.02 | new | n.a. | — | draft | [BC-6.02.004](ss-06/BC-6.02.004.md) |

### S6.03 — Comparison + exclusions

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-6.03.001 | Row goldens A/B/C (Tier B, Python-written, OS-specific variants) | S6.03 | BC-SL-089 | byte-exact | H | draft | [BC-6.03.001](ss-06/BC-6.03.001.md) |
| BC-6.03.002 | Comparison = stdout bytes + exit code per step; named caches byte-for-byte by file name; stderr never compared | S6.03 | new | n.a. | — | draft | [BC-6.03.002](ss-06/BC-6.03.002.md) |
| BC-6.03.003 | mkstemp temp names excluded from comparison; Go temp-cleanup difference covered | S6.03 | new | temp-file | — | draft | [BC-6.03.003](ss-06/BC-6.03.003.md) |
| BC-6.03.004 | Exclusion-list machinery: per-case entries, expected files, table tests, no globs | S6.03 | new | n.a. | — | draft | [BC-6.03.004](ss-06/BC-6.03.004.md) |

### S6.04 — CI matrix + timing

| BC ID | Title | Subsystem / section | Legacy | Parity class | Conf | Status | File |
|---|---|---|---|---|---|---|---|
| BC-6.04.001 | CI matrix: ubuntu-24.04 / macos-15 arm64 / windows-2025; Go 1.26.x leg; -race; gitleaks | S6.04 | new | n.a. | — | draft | [BC-6.04.001](ss-06/BC-6.04.001.md) |
| BC-6.04.002 | Per-OS timing report; p95 <= 25 ms binds on the owner's Mac target | S6.04 | new | n.a. | — | draft | [BC-6.04.002](ss-06/BC-6.04.002.md) |
| BC-6.04.003 | Tier C differential fuzz: nightly all three OSes, one clean run, non-gating, random valid inputs | S6.04 | new | n.a. | — | draft | [BC-6.04.003](ss-06/BC-6.04.003.md) |

## Accounting exceptions

- BC-SL-097: out of scope (OD-14), no new BC.
- BC-SL-068: accounted as replaced by the BC-SL-098 mapping (D4-EX-2).

## Parity-class notes (prose carve-outs)

- BC-1.07.002: the `byte-exact` parity class covers the ENABLED half (default true =
  legacy rows); the disabled half (`statusline.subagent.enabled=false`) is the OD-155 off
  switch — new behavior contracted by BC-1.07.002 itself, not a parity class. The former
  index value `OD-155 off switch` was not a closed-set id (pass-5 C16; the BC file's
  frontmatter is to be synced by the BC agent).

