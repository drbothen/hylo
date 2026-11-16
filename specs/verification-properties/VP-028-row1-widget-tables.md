---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.02.001.md, behavioral-contracts/ss-01/BC-1.02.007.md, behavioral-contracts/ss-01/BC-1.02.013.md, behavioral-contracts/ss-01/BC-1.02.020.md, behavioral-contracts/ss-01/BC-1.02.030.md, prd-supplements/test-vectors.md]
input-hash: "8bffcb0"
traces_to: prd.md
source_bc: BC-1.02.001
bcs: [BC-1.02.001, BC-1.02.002, BC-1.02.003, BC-1.02.004, BC-1.02.005, BC-1.02.006, BC-1.02.007, BC-1.02.008, BC-1.02.009, BC-1.02.010, BC-1.02.011, BC-1.02.012, BC-1.02.013, BC-1.02.014, BC-1.02.015, BC-1.02.016, BC-1.02.017, BC-1.02.018, BC-1.02.019, BC-1.02.020, BC-1.02.021, BC-1.02.022, BC-1.02.023, BC-1.02.024, BC-1.02.025, BC-1.02.026, BC-1.02.027, BC-1.02.028, BC-1.02.029, BC-1.02.030]
module: internal/statusline (row-1 file families)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: []
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

Every row-1 widget behaves per the oracle-pinned tables: lane-pill prefix match; model
label display_name→id→"?"; project basename(normpath(cwd)); branch walk and 5 s TTL
cache; context thermometer including the /0K, /1000K, NaN quirks; composition
percentage half-even rounding; cache-hit segment incl. NaN/inf; limits hidden on
reroute-all prefixes; expired window unreported; pace/absolute colour bands with the
rem = 0.9 × length boundary; countdown 1.15 gate; rate-limit smoothing over 1800 s and
sticky CP-S09; _fmt_lines/_hm/_fmt_tok_c formats incl. their typed OverflowError /
ValueError degrade sites; API-time suffix; ⌂ visibility gate and duration format; heat()
HSV cells; str()-of-non-str model label; POSIX normpath keeps //; no-unit-promotion
token format; pick eq threshold 0.005; effective_rl sequence with sticky CP-S09.

## Source Contract

- **Primary BC:** BC-1.02.001 — Lane pill derives from model-prefix startswith match.
- **Partial coverage:** BC-1.02.002..030 (all thirty S1.02 contracts; per-widget homes
  in BC-COMPONENT-MAP.md).
- **Invariant verified:** OD-135 CRITICAL tier (S1 >= 95% mutation kill target);
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
| Widget tables | Go test, per-widget canonical tables | yes — authored corners | all 30 S1.02 contracts |
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
| Input space size | 30 widgets x corners | bounded tables |
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
