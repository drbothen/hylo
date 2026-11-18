---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-20T08:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-01/BC-1.03.018.md, behavioral-contracts/ss-01/BC-1.03.019.md, behavioral-contracts/ss-01/BC-1.03.020.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "d87c668"
traces_to: prd.md
source_bc: BC-1.03.019
bcs: [BC-1.03.018, BC-1.03.019, BC-1.03.020, BC-1.03.006, BC-1.03.007, BC-1.03.010, BC-1.03.014, BC-1.03.016]
module: internal/statusline (transcript parser)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-18T14:15:00Z: ADV-P4 fixes — W-predicate sharpened per OD-167: a numeric-overflow skip (CP-O06..O08) also drops the in-flight turn (cur → null); the ruled drop is part of the expected post-skip state, not a mutation-on-skip violation (A2-03); skeleton test renamed to the canonical rider name TestMixCache_OD32_WrongShapeTables (BC-1.03.020 register, A2-14)", "1.2 2026-11-19T12:00:00Z: pass-6 fixes (A2-07, C06: the OD-32 reader rule stated with BOTH conditions (numeric t0 AND non-numeric out); bcs: gains BC-1.03.006/.007/.010)", "1.3 2026-11-20T08:00:00Z: pass-8 fixes (A2-10, A2-07, C03) — the table composition stated precisely: the canonical 21 BC-1.03.019 rows (predate OD-156/OD-167, no CP-O rows) PLUS the dedicated CP-O06..O08 vector/turn-drop legs owned by BC-1.03.006/.007/.010, each row's oracle its owning contract's pin; the two BC-1.03.018 for-all rows gained matching property legs (generated-W-line bit-identical state preservation, testing/quick; delete-the-line equivalence fuzz with the PC4(b) cur-null adjustment); Partial coverage and bcs: gain the hylo-only D4-EX-2 vector carriers BC-1.03.014 (single-line CP-T06, BASE size 70/81) and BC-1.03.016 (T15)"]
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

For every row of the harness's wrong-shape table — the canonical 21 rows of
BC-1.03.019 (which predate OD-156/OD-167 and contain no CP-O rows) PLUS the
dedicated CP-O06..O08 vector and turn-drop legs owned by BC-1.03.006/.007/.010,
each row's oracle being the exact expected values pinned in its owning contract
(A2-10) — a transcript line with the ruled wrong
shape is skipped by the W-predicate (no partial mutation of committed parser state;
for the numeric-overflow rows CP-O06..O08 the ruled consequence of the skip is that the
in-flight turn is dropped — `cur` ends null, OD-167), the resulting
caches match the exact expected values of that row, and the poisoned-`cur.out` reader
rule (OD-32) treats `cur` as absent — no open turn — iff `cur` is an object whose
`t0` is a number (int, float or bool) AND whose `out` is not a number, and keeps a
raw value when `t0` is null. Legacy's sticky-crash behavior (BC-SL-068) is intentionally replaced by these
contracts — a replacement, not a gap. Two for-all legs own the rows BC-1.03.018
routes here (ADV-P8-A2-07): for EVERY generated W-line (per CP), parser state after
the line equals state before, bit-identical (Go property test, testing/quick); and
on random transcripts with injected W-lines, DELETE-THE-LINE EQUIVALENCE holds —
the post-skip state equals the oracle run on the transcript with the W-line
deleted, adjusted per PC4(b): at each overflow skip the post-skip state
additionally includes `cur` → null (the open turn discarded, never finished).

## Source Contract

- **Primary BC:** BC-1.03.019 — D4-EX-2 table tests (21 rows, exact expected caches).
- **Partial coverage:** BC-1.03.018 (W-predicates: skip, no partial mutation),
  BC-1.03.020 (legacy-poisoned cur.out reader rule, OD-32), BC-1.03.006, BC-1.03.007,
  BC-1.03.010 (the CP-O06..O08 vector rows of the canonical table — the D4-EX-2
  skip-plus-turn-drop deviations those contracts own are delivered by this VP's
  21-row table; C06; reciprocal BC-body VP rows are the BC owners' fixes),
  BC-1.03.014 (single-line CP-T06 rows with hylo-only expected all-zero BASE caches
  `"size"` 70/81) and BC-1.03.016 (row T15, hylo-only D4-EX-2 expectation) —
  dedicated D4-EX-2 vector carriers that ride the same exclusion entry
  (ADV-P8-C03).
- **Invariant verified:** DI-012 (D4-EX-2 rides the exclusion list with dedicated
  tables per OD-105/OD-110); replaces BC-SL-068 per BC-ALLOCATION edge case 2.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — the canonical 21-row table with exact expected cache
  values; W-predicate rows assert skip + state intact; plus the two for-all legs:
  a testing/quick property over generated W-lines per CP (state after = state
  before, bit-identical) and a fuzz leg for delete-the-line equivalence with the
  PC4(b) `cur`-null adjustment (ADV-P8-A2-07).
- **Honesty:** testable-only; the table is the specification (T13 row oracle-confirmed,
  OD-143 refers to the turn table — D4-EX-2's 21 rows are the ruled expectation).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test | Go test, `internal/statusline` | yes — 21 canonical rows + the owned CP-O06..O08 vector legs | every wrong-shape class + poisoned-cache rule |
| Generated-W-line property | Go property test (testing/quick) | generated W-lines per CP | state-after = state-before, bit-identical |
| Delete-the-line equivalence fuzz | `go test -fuzz` | random transcripts, injected W-lines | post-skip state = deletion oracle, adjusted per PC4(b) |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestMixCache_OD32_WrongShapeTables(t *testing.T) { // canonical rider name, BC-1.03.020 (A2-14)
    for _, r := range WrongShapeTable21 {
        st := newParserState(r.Seed)
        st.ApplyLine(r.Line)
        // Ruled skip rule (OD-167 sharpening, A2-03): no partial mutation of
        // committed state AND the in-flight turn dropped (cur -> null). The null
        // cur is the ruled post-skip state — not a "mutation on skip" violation.
        if !r.SkipRuleHolds(st) { t.Fatalf("row %d: skip rule violated", r.ID) }
        assertCachesEqual(t, r.ExpectedCaches, st.Caches())
    }
}

func TestWrongShape_StatePreservation_Quick(t *testing.T) { // BC-1.03.018 for-all row (A2-07):
    // for every generated W-line (per CP), parser state after = state before, bit-identical.
    err := quick.Check(func(seed ParserState, wline WLine) bool { // wline generated holding some W-predicate
        st := seed.Clone()
        st.ApplyLine(wline)
        return st.BitIdenticalTo(seed)
    }, nil)
    if err != nil { t.Fatalf("W-line state preservation violated: %v", err) }
}

func FuzzWrongShape_DeleteLineEquivalence(f *testing.F) { // BC-1.03.018 for-all row (A2-07):
    // random transcripts with injected W-lines: post-skip state = oracle on the transcript
    // with the W deleted, adjusted per PC4(b) — at each overflow skip the state additionally
    // includes cur -> null (the open turn discarded, OD-167).
    f.Fuzz(func(t *testing.T, transcript []byte) {
        got := ParseWithWPPredicates(transcript)
        want := ParseWithWPPredicates(DeleteWLines(transcript)) // deletion oracle, state-adjusted
        if !CachesEqualModuloPC4b(got, want) {
            t.Fatal("delete-the-line equivalence violated (modulo the OD-167 cur-null adjustment)")
        }
    })
}
```

## Named Tests (OD-145 table where applicable)

Rides exclusion id `D4-EX-2`; parity case family `transcript`; the corresponding
exclusion entry is verified admissible by `TestParityExclusions_ClosedSet` (VP-012).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | 21 canonical rows + the owned CP-O06..O08 vector legs, plus generated W-lines | canonical table + for-all legs |
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
