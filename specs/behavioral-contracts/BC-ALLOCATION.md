---
artifact_type: bc-allocation
document_type: bc-allocation
level: L3
version: "0.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T16:00:00Z
phase: 1a
stage: "1 of 3 (allocation only — individual BC files are created in stage 2 by the writer groups)"
origin: greenfield
subsystem: register
capability: register
lifecycle_status: active
introduced: "0.1"
modified: "0.1"
extracted_from: "statusline-target-design.md §8 + hylo-legacy-pass-3-deep-behavioral-contracts-r4.md §7.3"
deprecated: "n.a."
deprecated_by: "n.a."
replacement: "n.a."
retired: "n.a."
removal_reason: "n.a."
removed: "n.a."
inputs:
  - prd.md
  - ./domain-spec/capabilities.md
  - ./domain-spec/invariants.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - owner-decisions-log-2026-11-14.md
input-hash: "fc86b6b"
traces_to: ../prd.md
---

# BC Allocation: hylo P1 (authoritative)

> **Purpose.** One row per new behavioral contract for the P1 status line. Stage 2
> writer groups create one file per row at
> `behavioral-contracts/ss-NN/BC-S.SS.NNN.md` (shard by subsystem), using the title
> below as the file's H1 and `BC-ALLOCATION.md` as the mapping authority. Individual
> BC files must not be invented or renumbered outside this table.
>
> **Sources.** Legacy column refers to BC-SL-nnn in
> `../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md` (§7.3,
> amended r5-r8); "Primary source" cites the legacy source lines (SL:n) via the
> translation design §2.2/§2.3/§8 (`../semport/hylo-legacy/statusline-target-design.md`)
> or the governing owner decision (OD-n). Conf = translation confidence from design §8
> (H = mechanical given pinned oracle tables; M = sizeable Python-semantics surface);
> "—" for new contracts with no legacy counterpart.
>
> **Approval.** Subsystem breakdown approved by the owner 2026-11-15; to be recorded
> as OD-131 (pending). Parity classes after owner rulings OD-107..OD-114.

## Mapping rules applied

1. **Exactly-one mapping.** Every legacy BC-SL-001..103 maps to exactly one new BC id,
   except BC-SL-097 (out of scope, OD-14) and BC-SL-068 (accounted as replaced by the
   BC-SL-098 mapping, D4-EX-2) — see the "Out of scope / replaced" table.
2. **Helper-home rule.** A legacy contract whose primary Go home is `internal/pyfmt`
   (design §8 "Go home" prefixed `py/`) allocates into S5: BC-SL-067 → S5.02,
   BC-SL-069 → S5.04, BC-SL-071/096 → S5.02. Widget behavior stays in S1.
3. **Cost family cohesion.** All cost-widget and cost-history contracts
   (BC-SL-025/026/027/028/029/079/082/101/102) allocate into S1.05 ("cost history +
   dynamic colors") even where the design's translation step was S3.
4. **Probe/render split.** Window-age rendering and its gate (BC-SL-022, BC-SL-081)
   stay in S1.02 row-1 widgets; acquisition semantics (BC-SL-023, BC-SL-080: native
   per-OS probe, D4-EX-1, OD-76 edge differences) allocate into S3.02.
5. **Golden machinery.** BC-SL-089 (row goldens A/B/C) allocates into S6.03 — the
   Tier B committed-golden comparison is harness machinery; the golden *content* is
   status-line output.
6. **One behavior per BC.** New S2 contracts split the OD-114 D4-EX-3 error classes
   (number-range, number-grammar, enum, URL) into one contract each; the S5 helper
   bundles split by pyfmt file (num/json/str/time).
7. **Numbering.** NNN restarts at 001 within each subsection (template §2 pattern);
   shard directories `ss-NN` are keyed by subsystem (S1 → ss-01, ... S6 → ss-06).

## Writer groups (stage 2)

| Group | Scope | BCs |
|-------|-------|-----|
| A | S1.01 | 10 |
| B1 | S1.02 .001-.015 | 15 |
| B2 | S1.02 .016-.030 | 15 |
| C | S1.03 | 21 |
| D | S1.04 | 21 |
| E | S1.05 + S1.06 | 11 |
| F | S2 + S4 | 15 |
| G | S3 + S5 | 16 |
| H | S6 | 14 |
| **Total** | | **138** |

## Allocation table

Legend, parity class: `byte-exact` = reproduce legacy bytes; `D4-EX-1/2/3` = named
deviation classes; `OD-30` / `OD-76` = owner-ruled known differences; `temp-file` =
mkstemp temp handling difference (OD-110); `n.a.` = not ported.

### S1.01 — Input/output contract (writer A)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-1.01.001 | Guard prints the 29-byte degraded line and exits 0 | BC-SL-001 | byte-exact | SL:1238-1245 | H | A |
| BC-1.01.002 | Non-JSON or non-object stdin decodes to an empty object | BC-SL-002 | byte-exact | SL:1201-1206 | H | A |
| BC-1.01.003 | Rows join with LF; row 2 shown only when width permits | BC-SL-003 | byte-exact | SL:1224-1234 | H | A |
| BC-1.01.004 | Visible width counts code points after stripping SGR | BC-SL-004 | byte-exact | SL:151-153 | H | A |
| BC-1.01.005 | COLUMNS parses with the Python int grammar, else 0 | BC-SL-005 | byte-exact | SL:1185-1190 | H | A |
| BC-1.01.006 | trim_to_fit double-resets; single reset on the recycle row | BC-SL-054 | byte-exact | SL:1193-1197 | H | A |
| BC-1.01.007 | Negative COLUMNS disables trim and hides row 2 | BC-SL-055 | byte-exact | SL:1188-1190 | H | A |
| BC-1.01.008 | Strict UTF-8 stdio; invalid stdin UTF-8 renders from {} | BC-SL-076 | byte-exact | SL:1201-1206, 1234 | H | A |
| BC-1.01.009 | Side effects run in legacy order; a degrade keeps earlier writes | BC-SL-077 | byte-exact | SL:1200-1235 | M | A |
| BC-1.01.010 | Trim breakpoint matrix across widths | BC-SL-090 | byte-exact | SL:1193-1197 | H | A |

### S1.02 — Row-1 widgets (writers B1/B2)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-1.02.001 | Lane pill derives from model-prefix startswith match | BC-SL-006 | byte-exact | SL:441-462 | H | B1 |
| BC-1.02.002 | Model label falls back display_name → id → "?" | BC-SL-007 | byte-exact | SL:441-462 | H | B1 |
| BC-1.02.003 | Project label is basename(normpath(cwd)) | BC-SL-008 | byte-exact | SL:441-462 | H | B1 |
| BC-1.02.004 | Branch walk reads .git dir or file and HEAD | BC-SL-009 | byte-exact | SL:372-396 | H | B1 |
| BC-1.02.005 | Branch segment cached with a 5 s TTL | BC-SL-010 | byte-exact | SL:405-411 | H | B1 |
| BC-1.02.006 | Context thermometer and its denominator | BC-SL-011 | byte-exact | SL:418-437 | H | B1 |
| BC-1.02.007 | Composition percentage rounds half-even | BC-SL-012 | byte-exact | SL:1171 | H | B1 |
| BC-1.02.008 | Cache-hit segment | BC-SL-013 | byte-exact | SL:477-479 | H | B1 |
| BC-1.02.009 | Limits segment hidden on reroute-all prefixes | BC-SL-014 | byte-exact | SL:444, 487-532 | H | B1 |
| BC-1.02.010 | Expired rate-limit window is unreported | BC-SL-015 | byte-exact | SL:487-532 | H | B1 |
| BC-1.02.011 | Pace and absolute colour bands | BC-SL-016 | byte-exact | SL:506-532 | H | B1 |
| BC-1.02.012 | Countdown format and the 1.15 gate | BC-SL-017 | byte-exact | SL:487-532 | M | B1 |
| BC-1.02.013 | Rate-limit smoothing over 1800 s | BC-SL-018 | byte-exact | SL:304-308 | H | B1 |
| BC-1.02.014 | Lines segment formats via _fmt_lines | BC-SL-019 | byte-exact | SL:849-860 | H | B1 |
| BC-1.02.015 | Timer segment formats via _hm | BC-SL-020 | byte-exact | SL:534-563 | H | B1 |
| BC-1.02.016 | API-time suffix | BC-SL-021 | byte-exact | SL:534-563 | H | B2 |
| BC-1.02.017 | Window-age suffix (⌂) with its visibility gate | BC-SL-022 | byte-exact | SL:554-563 | M | B2 |
| BC-1.02.018 | Token segment formats via _fmt_tok_c | BC-SL-024 | byte-exact | SL:565-600, 863-873 | H | B2 |
| BC-1.02.019 | heat() HSV cell colours | BC-SL-056 | byte-exact | SL:140-148 | H | B2 |
| BC-1.02.020 | Thermometer quirks (/0K, /1000K, NaN crash) | BC-SL-057 | byte-exact | SL:418-437 | H | B2 |
| BC-1.02.021 | Model label str() of a non-str value | BC-SL-058 | byte-exact | SL:442, 453 | M | B2 |
| BC-1.02.022 | POSIX normpath keeps // | BC-SL-059 | byte-exact | SL:460 | M | B2 |
| BC-1.02.023 | Cache-hit NaN/inf rendering | BC-SL-060 | byte-exact | SL:477-479 | H | B2 |
| BC-1.02.024 | Pace band boundary at rem = 0.9 × length | BC-SL-061 | byte-exact | SL:487-532 | H | B2 |
| BC-1.02.025 | _fmt_tok_c performs no unit promotion | BC-SL-062 | byte-exact | SL:863-873 | H | B2 |
| BC-1.02.026 | _fmt_lines OverflowError on inf degrades (CP-S11) | BC-SL-063 | byte-exact | SL:849-860 | H | B2 |
| BC-1.02.027 | _hm ValueError on inf degrades (CP-S12/S13) | BC-SL-064 | byte-exact | SL:534-563 | H | B2 |
| BC-1.02.028 | Window-age duration format | BC-SL-081 | byte-exact | SL:554-563 | H | B2 |
| BC-1.02.029 | Pick eq threshold 0.005 | BC-SL-083 | byte-exact | SL:636 | H | B2 |
| BC-1.02.030 | effective_rl sequence with sticky CP-S09 | BC-SL-093 | byte-exact | SL:298-312 | H | B2 |

### S1.03 — Transcript parsing (writer C)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-1.03.001 | No transcript path yields no transcript state | BC-SL-030 | byte-exact | SL:1010-1015 | H | C |
| BC-1.03.002 | Mix cache name and mixv6 reset rules | BC-SL-031 | byte-exact | SL:1016-1038 | H | C |
| BC-1.03.003 | 512 KB read step with long-line completion | BC-SL-032 | byte-exact | SL:1041-1052 | H | C |
| BC-1.03.004 | bytes.splitlines + per-line json.loads | BC-SL-033 | byte-exact | SL:1059-1063 | M | C |
| BC-1.03.005 | Usage dedup per message id (memory 256) | BC-SL-034 | byte-exact | SL:1064-1119 | H | C |
| BC-1.03.006 | Usage accumulation across int/float/big-int | BC-SL-035 | byte-exact | SL:1064-1119 | M | C |
| BC-1.03.007 | Rebuild rule at 20,000 excess input tokens | BC-SL-036 | byte-exact | SL:1088-1119 | H | C |
| BC-1.03.008 | compact_boundary resets composition and pp | BC-SL-037 | byte-exact | SL:999-1119 | H | C |
| BC-1.03.009 | Composition per block from json.dumps lengths | BC-SL-038 | byte-exact | SL:1120-1149 | M | C |
| BC-1.03.010 | Last-turn rate machine | BC-SL-039 | byte-exact | SL:977-996, 1064-1087 | H | C |
| BC-1.03.011 | First line of a message supplies its usage | BC-SL-065 | byte-exact | SL:1064-1119 | H | C |
| BC-1.03.012 | Short + long line completes over two refreshes | BC-SL-066 | byte-exact | SL:1041-1052 | H | C |
| BC-1.03.013 | Mix cache sid sanitized per code point | BC-SL-070 | byte-exact | SL:1017 | H | C |
| BC-1.03.014 | text/thinking block value types | BC-SL-072 | byte-exact | SL:1120-1149 | H | C |
| BC-1.03.015 | transcript_path type semantics (int = fd) | BC-SL-088 | byte-exact | SL:1010-1015 | M | C |
| BC-1.03.016 | Turn-machine exhaustive table (20 rows) | BC-SL-094 | byte-exact | SL:1064-1087 | H | C |
| BC-1.03.017 | Turn identity ignores seen_ids | BC-SL-095 | byte-exact | SL:1064-1087 | H | C |
| BC-1.03.018 | D4-EX-2 wrong-shape line W-predicates (skip, no partial mutation) | BC-SL-098 | D4-EX-2 | D4-EX-2; SL:1060-1063 | M | C |
| BC-1.03.019 | D4-EX-2 table tests (21 rows, exact expected caches) | BC-SL-099 | D4-EX-2 | D4-EX-2; Q-c ruling | H | C |
| BC-1.03.020 | Legacy-poisoned cur.out reader rule (OD-32) | BC-SL-100 | D4-EX-2 | D4-EX-2; OD-32 | M | C |
| BC-1.03.021 | cur with t0 null and non-numeric out kept verbatim | BC-SL-103 | byte-exact | SL:988-996; P3r4 §1.2 | H | C |

### S1.04 — Row-2 telemetry, metrics client, freshness (writer D)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-1.04.001 | fetch_sample: query, 1.5 s timeout, first-wins | BC-SL-040 | byte-exact | SL:102-123, 158-187 | M | D |
| BC-1.04.002 | get_sample TTL / KEEP_DEAD state machine | BC-SL-041 | byte-exact | SL:315-359 | H | D |
| BC-1.04.003 | History point rules (90 s cap, 2 s gap) | BC-SL-042 | byte-exact | SL:315-359 | H | D |
| BC-1.04.004 | Freshness ladder + stale suffix | BC-SL-043 | byte-exact | SL:693-835 | H | D |
| BC-1.04.005 | Health dot | BC-SL-044 | byte-exact | SL:693-835 | H | D |
| BC-1.04.006 | Queue segment | BC-SL-045 | byte-exact | SL:693-835 | H | D |
| BC-1.04.007 | KV segment | BC-SL-046 | byte-exact | SL:693-835 | H | D |
| BC-1.04.008 | Throughput segments | BC-SL-047 | byte-exact | SL:693-835 | H | D |
| BC-1.04.009 | Sparkline glyphs, scale and colors | BC-SL-048 | byte-exact | SL:659-690, 644-649 | H | D |
| BC-1.04.010 | TTFT segment | BC-SL-049 | byte-exact | SL:693-835 | H | D |
| BC-1.04.011 | Power segment | BC-SL-050 | byte-exact | SL:693-835 | H | D |
| BC-1.04.012 | Idle segment | BC-SL-051 | byte-exact | SL:693-835 | H | D |
| BC-1.04.013 | VM fetch whenever ROWS >= 2 | BC-SL-053 | byte-exact | SL:1217-1218 | H | D |
| BC-1.04.014 | Sparkline NaN/+Inf crash path (CP-N02) | BC-SL-073 | byte-exact | SL:659-690 | H | D |
| BC-1.04.015 | KV NaN crash path (CP-N01) and cell math | BC-SL-074 | byte-exact | SL:693-835 | H | D |
| BC-1.04.016 | Row-2 NaN/inf rendering; wall-colour mismatch | BC-SL-075 | byte-exact | SL:693-835 | H | D |
| BC-1.04.017 | Idle strict > 300 and age format | BC-SL-084 | byte-exact | SL:693-835 | H | D |
| BC-1.04.018 | Mine (last-turn) segment | BC-SL-085 | byte-exact | SL:693-835 | H | D |
| BC-1.04.019 | TTFT format boundaries | BC-SL-086 | byte-exact | SL:693-835 | H | D |
| BC-1.04.020 | get_sample pinned sequence and cache key order | BC-SL-091 | byte-exact | SL:315-359 | M | D |
| BC-1.04.021 | HIST_MIN_GAP reachability (seeded) | BC-SL-092 | byte-exact | SL:315-359 | H | D |

### S1.05 — Cost history + dynamic colors (writer E)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-1.05.001 | $ colours from lane percentile thresholds | BC-SL-025 | byte-exact | SL:601-625 | H | E |
| BC-1.05.002 | $/h segment with threshold colouring | BC-SL-026 | byte-exact | SL:601-625 | H | E |
| BC-1.05.003 | ⛏ pick inside the $ block (basis threshold) | BC-SL-027 | byte-exact | SL:601-636 | H | E |
| BC-1.05.004 | record_cost throttled write | BC-SL-028 | byte-exact | SL:224-237 | H | E |
| BC-1.05.005 | cost_thresholds p75/p95 percentiles | BC-SL-029 | byte-exact | SL:240-262 | H | E |
| BC-1.05.006 | Numeric sid: throttle and self-exclusion fail (single string-form key) | BC-SL-079 | OD-30 | OD-30; SL:224-262 | H | E |
| BC-1.05.007 | $ and $/h number formatting | BC-SL-082 | byte-exact | SL:601-636 | H | E |
| BC-1.05.008 | Cost colouring goldens (20 seeded sessions) | BC-SL-101 | byte-exact | SL:601-625; P3r4 §1.1 | H | E |
| BC-1.05.009 | record_cost write contract (exact JSON format) | BC-SL-102 | OD-30 | OD-30; SL:224-237, 245-246 | H | E |

### S1.06 — Session caches (writer E)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-1.06.001 | Cache load/save: never-raise, raw sid in file names | BC-SL-052 | byte-exact | SL:190-206; OD-03 | H | E |
| BC-1.06.002 | Sid with / : failed replace persists nothing; temp handling | BC-SL-078 | temp-file | SL:198-206; OD-110 | M | E |

### S2.01 — Schema + resolution (writer F)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-2.01.001 | P1 resolution: HYLO_* env over built-in defaults; no file layer; DGX_* never read | new | n.a. | OD-107, OD-05 | — | F |
| BC-2.01.002 | backends array: exactly one entry validated until P6; backends[0].metrics_url / backends[0].model_prefixes; default prefixes claude-sonnet | new | n.a. | OD-123, OD-111 | — | F |
| BC-2.01.003 | statusline.theme.* keys for SGR palette, pill codes and separator, legacy defaults | new | n.a. | OD-113 | — | F |
| BC-2.01.004 | Key registry: every key declares type, range/operator, default and rationale | new | n.a. | D15, OD-57, OD-114 | — | F |
| BC-2.01.005 | HYLO_* value grammars: typed bool, comma lists, ~ path expansion; COLUMNS excluded as protocol input | new | n.a. | OD-05, OD-74, OD-61 | — | F |

### S2.02 — Validation + config-error line (writer F)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-2.02.001 | D4-EX-3 config-error line: exact format, exit 0, stderr detail, no cache writes | BC-SL-087 | D4-EX-3 | OD-102, OD-114; SL:73-100 | H | F |
| BC-2.02.002 | Number-range class: non-finite/negative durations are config errors; TTL 0 stays valid | new | D4-EX-3 | OD-114 (T10) | — | F |
| BC-2.02.003 | Number-grammar class: underscore and Unicode-digit numerals are config errors | new | D4-EX-3 | OD-114 (T10) | — | F |
| BC-2.02.004 | Enum class: unknown sparkline trace value is a config error | new | D4-EX-3 | OD-114 (T10) | — | F |
| BC-2.02.005 | URL class: non-http(s) metrics URL is a config error | new | D4-EX-3 | OD-114 (T10) | — | F |
| BC-2.02.006 | Boolean class: a non-typed-boolean value is a config error (true\|false\|1\|0\|yes\|no) | new | D4-EX-3 | OD-140, OD-05 | — | F |

### S2.03 — Config subcommands (writer F)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|-------------|---|
| BC-2.03.001 | hylo config validate exits non-zero on the same errors as D4-EX-3 | new | n.a. | OD-102, OD-107 | — | F |
| BC-2.03.002 | hylo config path prints the per-OS config file path | new | n.a. | OD-95 | — | F |

### S3.01 — Per-OS paths (writer G)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-3.01.001 | Per-OS cache/config/state dirs; hylo cache dir from P1 (XDG/hylo, LOCALAPPDATA) | new | n.a. | OD-95, OD-101 | — | G |

### S3.02 — Process start / window age (writer G)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-3.02.001 | Window start via native per-OS ancestor probe; whole-second truncation; proc_start key first | BC-SL-023 | D4-EX-1 | D4-EX-1; SL:276-294 | M | G |
| BC-3.02.002 | ps-parse replacement: named per-OS edge differences (macOS/Linux) | BC-SL-080 | OD-76 | OD-76, D4-EX-1; SL:276-294 | M | G |

### S4.01 — Subcommand dispatch (writer F)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-4.01.001 | Dispatch statusline / version / config; statusline exits 0 for any argv | new | n.a. | design §2.1; RESUME step 1 | — | F |
| BC-4.01.002 | Unknown flag renders one-line error, exit 0, never blank (incl. leftover --subagent) | new | n.a. | OD-112 | — | F |
| BC-4.01.003 | hylo version prints the version string | new | n.a. | RESUME step 1 | — | F |

### S5.01 — Numbers/rounding (writer G)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-5.01.001 | Round/RoundN/F: half-even, decimal re-round, 'f' format incl. -0; nan/inf/-inf spellings | new | n.a. | OD-103; design IM-05/06 | — | G |
| BC-5.01.002 | ParseInt/ParseFloat Python grammar: underscores, Unicode digits, signs, 4,300-digit limit, nan/inf/1e400 | new | n.a. | OD-103; design IM-12 | — | G |
| BC-5.01.003 | CPython float divmod/mod; Int/Ceil typed NaN/Overflow errors; Max/Min NaN argument order | new | n.a. | OD-103; design IM-07/08/09 | — | G |
| BC-5.01.004 | pyfmt.D: {:d} decimal formatting with width and zero-pad | new | n.a. | OD-141; design IM-05 | — | G |
| BC-5.01.005 | pyfmt.Repr: CPython float repr (shortest round-trip, .0 suffix, inf/nan spellings) | new | n.a. | OD-141; design IM-03/05, PR-07/08 | — | G |
| BC-5.01.006 | pyfmt.MaxSeq: Python max() over a sequence with first-maximal-wins NaN order | new | n.a. | OD-141; design IM-09, PR-04 | — | G |

### S5.02 — JSON byte semantics (writer G)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-5.02.001 | json.dumps length rules (escaping, float repr, inner-null 0) | BC-SL-071 | byte-exact | SL:1120-1149; design IM-04 | H | G |
| BC-5.02.002 | json.dumps length oracle (63 cases) | BC-SL-096 | byte-exact | design §8 (63 rows); P3r2 §A5 | H | G |
| BC-5.02.003 | json.loads(bytes) acceptance set: BOM/UTF-16/32, invalid UTF-8, depth, NaN, duplicates | BC-SL-067 | byte-exact | SL:1059-1063; design IM-01 | M | G |
| BC-5.02.004 | Ordered object Value: insertion order, last-wins keeps position, Delete; WTF-8 strings | new | n.a. | design IM-01/03 | — | G |
| BC-5.02.005 | pyfmt.Str: Python str() of values (str unchanged, non-str via repr) | new | n.a. | OD-141; design IM-05 | — | G |
| BC-5.02.006 | pyfmt.Dumps: json.dump cache-file bytes (separators, ensure_ascii, float repr, order) | new | n.a. | OD-141; design IM-03 | — | G |

### S5.03 — Code-point string ops (writer G)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-5.03.001 | Len/Truncate/HasSurrogate: code points, surrogate = 1, not terminal cells | new | n.a. | OD-103; design IM-11 | — | G |
| BC-5.03.002 | Strip/RStrip/RSplit1/SplitLinesBytes: Python whitespace; \n \r\n \r only | new | n.a. | OD-103; design IM-11 | — | G |
| BC-5.03.003 | SubNonWord per code point before truncation; EncodeUTF8Replace lone surrogate → ? | new | n.a. | OD-103; design IM-11, IM-20 | — | G |
| BC-5.03.004 | PosixNormpath/NtNormpath/Basename per-OS selection (ntpath on Windows) | new | n.a. | OD-103; design IM-11 | — | G |

### S5.04 — Time semantics (writer G)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-5.04.001 | FromISOFormat: 3.11 grammar, naive = local, fraction truncation beyond µs | BC-SL-069 | byte-exact | SL:983; design IM-13 | M | G |
| BC-5.04.002 | LocalToUnix: CPython _mktime port, gap/overlap semantics, TZ injection, embedded tzdata | new | n.a. | OD-103; design IM-13, PR-14 | — | G |
| BC-5.04.003 | pyfmt.TimeFloat: Python time.time() value discipline (ns→s float, once per render) | new | n.a. | OD-141; design IM-14 | — | G |

### S6.01 — Oracle execution (writer H)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-6.01.001 | Oracle runs via explicit absolute CPython 3.11.x path, never PATH; invoked with -s, never -I/-E | new | n.a. | OD-104, OD-108, OD-109 | — | H |
| BC-6.01.002 | Child environment constructed from scratch: no *_proxy, fixed HOME/TMPDIR/locale | new | n.a. | OD-109 (DET-43) | — | H |
| BC-6.01.003 | Clock shim freezes time functions from HYLO_TEST_NOW, stepped per refresh; canary fails if shim absent | new | n.a. | OD-58, OD-109 | — | H |

### S6.02 — Fixture corpus (writer H)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-6.02.001 | Committed corpus synthetic-only; owner real inputs replayed from git-ignored captures/ | new | n.a. | OD-107; D2 hygiene | — | H |
| BC-6.02.002 | stdin-sequence replay of captured sessions: ordered snapshots, clock advanced per step | new | n.a. | OD-107 | — | H |
| BC-6.02.003 | Case model: stdin template + translated settings + metrics mode + seeds + steps | new | n.a. | design §5.2 | — | H |
| BC-6.02.004 | Cache-swap coverage: Python-writes/Go-reads and reverse, all four caches | new | n.a. | design §5.2 (ruling Q-b) | — | H |

### S6.03 — Comparison + exclusions (writer H)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-6.03.001 | Row goldens A/B/C (Tier B, Python-written, OS-specific variants) | BC-SL-089 | byte-exact | design §8 (S8 goldens) | H | H |
| BC-6.03.002 | Comparison = stdout bytes + exit code per step; named caches byte-for-byte by file name; stderr never compared | new | n.a. | OD-107; design §5.3 | — | H |
| BC-6.03.003 | mkstemp temp names excluded from comparison; Go temp-cleanup difference covered | new | temp-file | OD-110; design §5.3 | — | H |
| BC-6.03.004 | Exclusion-list machinery: per-case entries, expected files, table tests, no globs | new | n.a. | OD-105, OD-110 | — | H |

### S6.04 — CI matrix + timing (writer H)

| New BC ID | Title | Legacy | Parity class | Primary source | Conf | Writer |
|---|---|---|---|---|---|---|
| BC-6.04.001 | CI matrix: ubuntu-24.04 / macos-15 arm64 / windows-2025; Go 1.26.x leg; -race; gitleaks | new | n.a. | design §5.5; CLAUDE.md | — | H |
| BC-6.04.002 | Per-OS timing report; p95 <= 25 ms binds on the owner's Mac target | new | n.a. | OD-117 | — | H |
| BC-6.04.003 | Tier C differential fuzz: nightly Linux, non-gating, random valid inputs to both sides | new | n.a. | design §5.1; O5 | — | H |

## Out of scope / replaced (legacy accounting exceptions)

| Legacy ID | Disposition | Reason |
|---|---|---|
| BC-SL-097 | Out of scope — not ported | `--subagent` entry point; OD-14 rules --subagent / agent-panel rows out of hylo (CC 2.1.323 removed subagentStatusLine). The never-blank/exit-0 rule for a leftover `--subagent` argument is covered by BC-4.01.002 (OD-112). |
| BC-SL-068 | Replaced — no new BC of its own | Sticky transcript crash (legacy-only behavior). Superseded by the D4-EX-2 Go contract: the BC-SL-098 mapping (BC-1.03.018) plus BC-1.03.019/020 carry the corrected behavior (Q-c = D4-EX-2; design §8 "068 replaced"). |

## Summary counts

Per subsystem / section:

| Section | Writer | BCs | Mapped from legacy | New |
|---|---|---|---|---|
| S1.01 input/output | A | 10 | 10 | 0 |
| S1.02 row-1 widgets | B1+B2 | 30 | 30 | 0 |
| S1.03 transcript parsing | C | 21 | 21 | 0 |
| S1.04 row-2 telemetry | D | 21 | 21 | 0 |
| S1.05 cost history + colors | E | 9 | 9 | 0 |
| S1.06 session caches | E | 2 | 2 | 0 |
| S2.01 schema + resolution | F | 5 | 0 | 5 |
| S2.02 validation + error line | F | 6 | 1 (BC-SL-087) | 5 |
| S2.03 config subcommands | F | 2 | 0 | 2 |
| S3.01 per-OS paths | G | 1 | 0 | 1 |
| S3.02 process start | G | 2 | 2 | 0 |
| S4.01 dispatch | F | 3 | 0 | 3 |
| S5.01 numbers/rounding | G | 6 | 0 | 6 |
| S5.02 JSON byte semantics | G | 6 | 3 (071, 096, 067) | 3 |
| S5.03 code-point string ops | G | 4 | 0 | 4 |
| S5.04 time semantics | G | 3 | 1 (069) | 2 |
| S6.01 oracle execution | H | 3 | 0 | 3 |
| S6.02 fixture corpus | H | 4 | 0 | 4 |
| S6.03 comparison + exclusions | H | 4 | 1 (089) | 3 |
| S6.04 CI matrix + timing | H | 3 | 0 | 3 |
| **Total** | | **145** | **101** | **44** |

Per writer group: A 10 · B1 15 · B2 15 · C 21 · D 21 · E 11 · F 16 · G 22 · H 14 = **145**
(after the OD-141/OD-140 additions of 2026-11-15; stage-2 baseline was F 15 · G 16 · H 14
= **138**).

### Legacy accounting check

- Legacy population: BC-SL-001..103 = **103** contracts.
- Mapped to exactly one new BC id: **101** (rows marked with a BC-SL-nnn legacy id above).
- Out of scope: **1** (BC-SL-097, OD-14).
- Accounted as replaced: **1** (BC-SL-068, superseded by the BC-SL-098 mapping per D4-EX-2).
- 101 + 1 + 1 = **103 — fully accounted.**
- Every new BC id is unique; NNN restarts per subsection; shard = subsystem (ss-01..ss-06).

## Description

This register is the authoritative allocation of the hylo P1 behavioral contracts: it
maps all 103 legacy status-line contracts (BC-SL-001..103) to new hierarchical ids
BC-S.SS.NNN under the owner-approved subsystem breakdown (S1-S6 with BCs this cycle;
S7-S12 reserved), assigns parity classes after owner rulings OD-107..OD-114, translation
confidence from the translation design §8, and stage-2 writer groups. It is consumed by
the stage-2 writer agents and by the consistency-validator; the PRD index (prd.md
Section 2) mirrors it and must not drift.

## Preconditions

1. The L2 domain spec (domain-spec/) is product-level and stable; OD-118..OD-130
   resolved all formerly proposed elements.
2. The semport target design (statusline-target-design.md) maps all 103 legacy
   contracts (§8) with parity classes and confidence; owner rulings OD-107..OD-114 are
   appended and govern.
3. The owner approved the subsystem breakdown 2026-11-15 (to be recorded as OD-131).
4. prd.md Section 2 mirrors this register; any BC id, title, or count change here must
   be propagated there in the same burst.

## Postconditions

1. Every row in the allocation table corresponds to exactly one future BC file at
   `behavioral-contracts/ss-NN/BC-S.SS.NNN.md`, created in stage 2.
2. After stage 2, every legacy contract BC-SL-001..103 is either represented by a new
   BC file (101), listed out-of-scope (BC-SL-097, OD-14), or listed replaced
   (BC-SL-068 → the BC-SL-098 mapping).
3. Writer groups A-H can be dispatched in parallel without id collisions; each group
   has at most 21 contracts and a single subsystem-section scope (B split B1/B2).
4. prd.md frontmatter `supplements:` remain STAGE 3 placeholders until stage 3
   populates `prd-supplements/`.

## Invariants

1. **Exactly-one mapping**: each legacy id occurs at most once in the allocation
   table; 101 mapped + BC-SL-097 OOS + BC-SL-068 replaced = 103.
2. **Append-only ids**: new BC ids are never reused or renumbered; retirement follows
   the BC deprecation protocol (DF-030), never deletion.
3. **Shard layout**: BC file path = `behavioral-contracts/ss-NN/BC-S.SS.NNN.md` with
   ss-NN keyed by subsystem number; NNN restarts per subsection.
4. **Title authority**: the allocation title is the intended BC file H1; if a stage-2
   writer enriches a title, the change must land in the BC file H1 and in prd.md
   Section 2 in the same commit (bc_h1_is_title_source_of_truth).
5. **Parity classes are closed**: only byte-exact, D4-EX-1/2/3, OD-30, OD-76,
   temp-file, and n.a. occur; introducing a new class requires an owner decision.

## Edge Cases

1. **BC-SL-097** (`--subagent`, out of scope, OD-14): the never-blank/exit-0 behavior
   for a leftover `--subagent` argv is contracted by BC-4.01.002 (OD-112), so no
   parity hole remains despite the OOS disposition.
2. **BC-SL-068**: legacy sticky-crash behavior is intentionally not ported; its Go
   replacement is the D4-EX-2 W-predicate contract (BC-1.03.018) verified by
   BC-1.03.019/020 — a replacement, not a gap.
3. **Dual-home contracts** (BC-SL-067/069/071/096, helper home in `internal/pyfmt`):
   allocated to S5 per the helper-home rule; their consuming S1 behavior contracts
   (e.g. BC-1.03.004) reference the helper contracts rather than duplicating tables.
4. **BC-SL-102** tagged OD-30 rather than byte-exact: its numeric-sid write path is
   the OD-30 sub-case called out in design §8; stage-2 writer E must scope the
   contract to the ruled single-string-key behavior.

## Canonical Test Vectors

Register-level vectors are out of scope here; canonical golden tables are named in
prd.md Section 5b (STAGE 3) and specified per contract in stage 2 from the pinned
sources: turn machine (20 rows, BC-SL-094), D4-EX-2 table (21 rows, BC-SL-099),
json.dumps length oracle (63 cases, BC-SL-096), get_sample 11-step sequence (BC-SL-091),
cost colouring (20 sessions, BC-SL-101), CPython-generated pyfmt expectation tables
(design §2.6).

## Verification Properties

VP elaboration is a stage-3/verification-architecture deliverable. Obligations noted
at allocation: D4-EX-1 (BC-3.02.001/002) and D4-EX-2 (BC-1.03.018/019/020) require
dedicated exclusion table tests (OD-110); D4-EX-3 requires one test per key class
(BC-2.02.001..005); the harness must fail on a missing table test, on a mismatched
expected file, or on glob entries (BC-6.03.004). The orchestrator must dispatch the
architect afterward so VP-INDEX propagates (vp_index_is_vp_catalog_source_of_truth).

## Traceability

- PRD index mirror: `../prd.md` Section 2 (must match this register).
- Legacy source register: `../../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md` §7.3.
- Translation mapping: `../../semport/hylo-legacy/statusline-target-design.md` §8
  (parity class, confidence, Go home) and §2 (package layout, primary sources).
- Owner decisions: `../owner-decisions-log-2026-11-14.md` (OD-102, OD-104..114, OD-117,
  OD-123, OD-131 pending); docs/PLAN.md D1-D16.
- L2 anchors: `../domain-spec/capabilities.md` (CAP-009/010/011, CAP-015),
  `../domain-spec/invariants.md` (DI-007, DI-008, DI-010, DI-012).

## Stage 3 change log (integration, 2026-11-15)

Applied at stage 3 during cross-group reconciliation. No id was renumbered and no row
was added or removed; the table above remains the stage-1 allocation record. All 138
BC files were verified against this register (ids, titles, frontmatter legacy_id /
parity_class / confidence).

Citation corrections (allocation primary source too narrow or off by a line; the BC
file cites the corrected range):

| New BC ID | Allocated source | Cited in BC file | Reason |
|---|---|---|---|
| BC-1.02.029 | SL:636 | SL:633-635 (inside SL:626-636) | SL:636 is `parts.append(cseg)`; the 0.005 check is SL:634, `eq` computed SL:633, format SL:635 |
| BC-1.01.007 | SL:1188-1190 | + SL:1224, SL:1232 | Allocated range is the COLUMNS parse only; row-2-hidden and trim-skip behavior live at the named sites |
| BC-1.02.005 | SL:405-411 | SL:399-413 (+ SL:99, SL:77) | Adds the git-enabled check and segment rendering |
| BC-1.02.007 | SL:1171 | SL:1157-1183 (+ call site SL:466-468) | Allocated line is the rounding line only |
| BC-1.02.013 | SL:304-308 | SL:298-312 | Adds the cached-read path, function header and call site |
| BC-1.03.002 | SL:1016-1038 | SL:1016-1040 | Size-equals-offset return is SL:1039-1040 |
| BC-1.03.003 | SL:1041-1052 | SL:1041-1058 | Cut and offset logic is SL:1053-1058 |
| BC-1.04.003, BC-1.04.020 | SL:315-359 | + `_norm_pt` SL:652-656 | History rules depend on the normalizer |
| BC-1.04.013 | SL:1217-1218 | SL:1217-1227 | Row-2 render inputs are SL:1224-1227 |
| BC-2.02.005 | (draft) SL:185-186 | SL:186-187 | fetch_sample catch-all one line off in the draft; fixed by writer F |
| BC-2.02.004 | (draft) SL:641-642 | SL:642-643 | "mine retired" comment one line off in the draft; fixed by writer F |

Confidence disagreements (allocation value used; noted in the BC files): BC-1.04.013 and
BC-1.02.009 are H here and in design §8 but M in the P3r4 index; BC-1.02.012 is M here
(float floor-division/modulo translation risk) though the behavior itself is high
confidence.

Cross-group normalizations decided at integration (BC files edited):

- `statusline.telemetry.ttl_s` (BC-2.01.004 registry / design §2.4 spelling) replaces
  the illustrative `statusline.ttl_s` in BC-6.02.003's exclusions vector.
- Exclusion entry id `temp-file` (lowercase, per the closed set in BC-6.03.004)
  replaces BC-1.06.002's draft `TEMP-FILE`; that case keeps its own table test
  (`TestCacheStore_OD110_TempCleanup`), distinct from BC-6.03.003's
  `TestCacheStore_TempFile_CleanupOnFailedReplace`.
- Literal invisible characters in test vectors (U+200B in BC-5.01.002, BC-5.03.002)
  rewritten as visible `\u200B` escapes; all BC files scanned clean of
  U+200B-U+200F, U+202A-U+202E, U+2066-U+2069, U+FEFF.
- JSON decode recursion budgets restated per call site: stdin text mode 993 accepted /
  994 rejected (BC-1.01.002), transcript bytes mode 995 accepted / 1,000 rejected
  (BC-5.02.003, consumed by BC-1.03.004); `Decode` takes the budget per call site.
- Negative `COLUMNS` beyond int64 restated identically in BC-1.01.005 PC-4 and
  BC-5.01.002 PC-3: an overflowing negative stays negative (row 2 hidden); only the
  over-4,300-digit error path maps to 0.

## Stage 3 revision — owner rulings OD-132..OD-145 (2026-11-15)

Seven rows added at the owner's rulings on PRD OQ-1..OQ-14 (2026-11-15); no existing id
was renumbered, retitled or removed, and the 138 stage-2 rows stand as allocated.

- **Added BC-2.02.006** (OD-140): dedicated boolean-parsing contract in S2.02; one
  behavior — typed booleans `true|false|1|0|yes|no` per OD-05, anything else is a
  boolean-class config error.
- **Added BC-5.01.004, BC-5.01.005, BC-5.01.006, BC-5.02.005, BC-5.02.006, BC-5.04.003**
  (OD-141): helper-level contracts for the six pyfmt helpers `D`, `Repr`, `Str`, `Dumps`,
  `MaxSeq`, `TimeFloat` in their design §2.6 homes (num / json / time); S5 coverage
  rises to 19. Cycle total: **145 BCs** (101 mapped from legacy + 44 new).
- **OD-135** (no row change): S1 and S5 are module-critical (coverage >= 95%) per
  `prd-supplements/module-criticality.md`; prd.md §1.6 amended accordingly (amends the
  OD-131 priority labels).
- **Dispositions recorded in BC files:** BC-2.03.002 prints all three paths (OD-132);
  `statusline.window_age.process_name` registered (OD-133); theme reason string is the
  named "not an SGR parameter list" class (OD-134); `cp-x03` joins the closed exclusion
  set above (OD-136, scope table row in BC-6.03.004); `math/big` at the two
  duration-format sites (OD-137); NaN-usd outcome pinned from the oracle (OD-138);
  symlinked-binary case deferred to the per-OS probe test (OD-139); json.dumps oracle
  table regenerated by script, row 53 = 38 (OD-142); T13 confirmed by oracle, row kept
  (OD-143); Windows cache/state subdirectories + XDG ignore ruling (OD-144); harness
  flag/test/seed names marked provisional for the architect (OD-145).
