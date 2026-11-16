---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-01/BC-1.03.018.md, behavioral-contracts/ss-01/BC-1.03.019.md, behavioral-contracts/ss-01/BC-1.03.020.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "d74dfe3"
traces_to: prd.md
source_bc: BC-1.03.019
bcs: [BC-1.03.018, BC-1.03.019, BC-1.03.020]
module: internal/statusline (transcript parser)
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

# VP-013: D4-EX-2 wrong-shape transcript lines — W-predicates and exact expected caches

## Property Statement

For every row of the 21-row wrong-shape table: a transcript line with the ruled wrong
shape is skipped by the W-predicate (no partial mutation of parser state), the resulting
caches match the exact expected values of that row, and the poisoned-`cur.out` reader
rule (OD-32) treats a numeric `cur.t0` as no-open-turn and keeps a raw value when `t0`
is null. Legacy's sticky-crash behavior (BC-SL-068) is intentionally replaced by these
contracts — a replacement, not a gap.

## Source Contract

- **Primary BC:** BC-1.03.019 — D4-EX-2 table tests (21 rows, exact expected caches).
- **Partial coverage:** BC-1.03.018 (W-predicates: skip, no partial mutation),
  BC-1.03.020 (legacy-poisoned cur.out reader rule, OD-32).
- **Invariant verified:** DI-012 (D4-EX-2 rides the exclusion list with dedicated
  tables per OD-105/OD-110); replaces BC-SL-068 per BC-ALLOCATION edge case 2.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — the canonical 21-row table with exact expected cache
  values; W-predicate rows assert skip + state intact.
- **Honesty:** testable-only; the table is the specification (T13 row oracle-confirmed,
  OD-143 refers to the turn table — D4-EX-2's 21 rows are the ruled expectation).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test | Go test, `internal/statusline` | yes — 21 ruled rows | every wrong-shape class + poisoned-cache rule |

## Proof Harness Skeleton

```go
func TestD4EX2_WrongShapeTables(t *testing.T) {
    for _, r := range WrongShapeTable21 {
        st := newParserState(r.Seed)
        st.ApplyLine(r.Line)
        if !r.WPredicateHolds(st) { t.Fatalf("row %d: mutated on skip", r.ID) }
        assertCachesEqual(t, r.ExpectedCaches, st.Caches())
    }
}
```

## Named Tests (OD-145 table where applicable)

Rides exclusion id `D4-EX-2`; parity case family `transcript`; the corresponding
exclusion entry is verified admissible by `TestParityExclusions_ClosedSet` (VP-012).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | 21 ruled rows | canonical table |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | exact expected cache values per row |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
