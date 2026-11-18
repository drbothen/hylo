---
document_type: verification-property
level: L4
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-18T14:55:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.02.001.md, behavioral-contracts/ss-01/BC-1.02.007.md, behavioral-contracts/ss-01/BC-1.02.013.md, behavioral-contracts/ss-01/BC-1.02.020.md, behavioral-contracts/ss-01/BC-1.02.030.md, behavioral-contracts/ss-01/BC-1.07.006.md, prd-supplements/test-vectors.md]
input-hash: "1c1a6c0"
traces_to: prd.md
source_bc: BC-1.02.001
bcs: [BC-1.02.001, BC-1.02.002, BC-1.02.003, BC-1.02.004, BC-1.02.005, BC-1.02.006, BC-1.02.007, BC-1.02.008, BC-1.02.009, BC-1.02.010, BC-1.02.011, BC-1.02.012, BC-1.02.013, BC-1.02.014, BC-1.02.015, BC-1.02.016, BC-1.02.017, BC-1.02.018, BC-1.02.019, BC-1.02.020, BC-1.02.021, BC-1.02.022, BC-1.02.023, BC-1.02.024, BC-1.02.025, BC-1.02.026, BC-1.02.027, BC-1.02.028, BC-1.02.029, BC-1.02.030, BC-1.07.006]
module: internal/statusline (row-1 file families)
proof_method: golden
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-18T05:30:00Z: subagent lane-pill startswith leg added — BC-1.07.006 rides the shared prefix rule (adv-p2 sync SC-07)", "1.2 2026-11-18T09:15:00Z: ADV-P3 fix (A2-23) — invariant-verified claim recast per OD-158: mutation kill rate is a Phase 6 objective, non-gating in P1", "1.3 2026-11-18T14:55:00Z: ADV-P4 fixes — B02: the empty-prefix-list row corrected per BC-1.02.001 PC3/EC-001 — the MAIN lane pill is NEVER omitted; an empty prefix list renders the unknown pill `\e[100;37;1m ◨ ? \e[0m` with defaults); only in the subagent model segment (BC-1.07.006, legacy SL:905-907) does the tag disappear; B03: the for-all/quantified legs (testing/quick, fuzz-vs-oracle, lint, fake-filesystem syscalls) split out to the new VP-041 — this VP keeps the bounded golden tables; frontmatter proof_method synced to golden", "1.4 2026-11-18: ADV-P4 pass-4 fix — project-label fact aligned with the BC-1.02.003 fallback chain, basename(normpath(project_dir | current_dir | cwd))"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-028: Row-1 widget family — oracle-pinned tables across all thirty contracts

## Property Statement

Every row-1 widget behaves per the oracle-pinned tables: lane-pill prefix match
(case-sensitive startswith, first matching entry wins; an empty prefix list renders
the UNKNOWN pill `\e[100;37;1m ◨ ? \e[0m` with defaults — the main pill is never
omitted, BC-1.02.001 PC3/EC-001, legacy SL:446-449; only the subagent model segment
drops its tag when no prefix matches, BC-1.07.006, legacy SL:905-907); model
label display_name→id→"?"; project basename(normpath(project_dir | current_dir | cwd));
branch walk and 5 s TTL
cache; context thermometer including the /0K, /1000K, NaN quirks; composition
percentage half-even rounding; cache-hit segment incl. NaN/inf; limits hidden on
reroute-all prefixes; expired window unreported; pace/absolute colour bands with the
rem = 0.9 × length boundary; countdown 1.15 gate; rate-limit smoothing over 1800 s and
sticky CP-S09; _fmt_lines/_hm/_fmt_tok_c formats incl. their typed OverflowError /
ValueError degrade sites; API-time suffix; ⌂ visibility gate and duration format; heat()
HSV cells; str()-of-non-str model label; POSIX normpath keeps //; no-unit-promotion
token format; pick eq threshold 0.005; effective_rl sequence with sticky CP-S09.

Quantified for-all legs — the testing/quick, fuzz-vs-oracle, lint and
fake-filesystem syscall rows the S1.02 VP tables mark "property proof" / "fuzz" /
"lint" — are delivered by VP-041 (pass-4 split, as VP-040 was split from VP-027);
this VP delivers the bounded golden tables ("testable-only; authored corners").

## Source Contract

- **Primary BC:** BC-1.02.001 — Lane pill derives from model-prefix startswith match.
- **Partial coverage:** BC-1.02.002..030 (all thirty S1.02 contracts; per-widget homes
  in BC-COMPONENT-MAP.md); plus BC-1.07.006 — the subagent model segment's lane pill
  applies the identical startswith prefix rule against `backends[0].model_prefixes`
  (v1.1, adv-p2 sync SC-07).
- **Invariant verified:** OD-135 CRITICAL tier (S1 coverage >= 95%; the mutation
  kill-rate target is a Phase 6 objective and does not gate P1 — OD-158);
  NFR-003 byte parity on the whole row-1 surface.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** golden/parity tier — per-widget canonical tables from the pinned sources
  (translation design §8 sources; test-vectors.md) riding the corpus families; the
  sticky/quirk rows (NaN quirks, sticky CP-S09) get dedicated table rows; the
  OverflowError/ValueError degrade sites also ride VP-001's ladder table.
- **Honesty:** testable-only; corpus + tier C extend beyond authored corners.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Widget tables | Go test, per-widget canonical tables | yes — authored corners | all 30 S1.02 contracts + BC-1.07.006 model-segment pill |
| Corpus parity | VP-009 tiers | corpus-bounded | end-to-end bytes |

## Proof Harness Skeleton

```go
func TestRow1_WidgetTables(t *testing.T) {
    for _, w := range Row1WidgetTables {
        got := w.Render(w.Env())
        assertGoldenBytes(t, w.Golden, got)
    }
}
```

## Named Tests (OD-145 table where applicable)

Widget rows ride the `row1`/`transcript`/`cost` parity families (ARCH-07 case
grammar); in-tree umbrella `TestRow1_WidgetTables`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | 30 widgets + 1 subagent model segment x corners | bounded tables |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Weeks | sheer table volume; parallelizable per file family |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
