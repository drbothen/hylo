---
document_type: verification-property
level: L4
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-19T18:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.05.001.md, behavioral-contracts/ss-01/BC-1.05.002.md, behavioral-contracts/ss-01/BC-1.05.003.md, behavioral-contracts/ss-01/BC-1.05.005.md, behavioral-contracts/ss-01/BC-1.05.007.md, behavioral-contracts/ss-01/BC-1.05.008.md]
input-hash: "0ead974"
traces_to: prd.md
source_bc: BC-1.05.008
bcs: [BC-1.05.001, BC-1.05.002, BC-1.05.003, BC-1.05.005, BC-1.05.007, BC-1.05.008]
module: internal/statusline (cost.go), internal/cost
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-18T09:18:00Z: ADV-P3 fixes — the legs the BC VP-tables route here now exist in this document: testing/quick for-all legs (BC-1.05.001/002/003/005 threshold/percentile invariants) and a Tier C differential formatting-fuzz row (BC-1.05.007) (C2-08); OD-135 invariant claim recast per OD-158, mutation non-gating in P1 (A2-23)", "1.2 2026-11-18T14:18:00Z: ADV-P4 fixes — seeded-session count corrected to 21 (12 s + 8 g + sess-self, BC-1.05.008; A09/C2-04), fixture slice renamed SeededSessions21; quick.Values filler rewritten to the assigning form args[i] = reflect.ValueOf(x) (A2-05)", "1.3 2026-11-19T12:00:00Z: pass-6 fixes (A2-12: the quick-leg oracle respelled as the harness re-derivation of the BC-1.05.005 rule; the generator derives th from rates (no unconstrained th))", "1.4 2026-11-19T18:00:00Z: pass-7 fix (A2-14) — the quick leg's quantifier is the filtered population (SL:240-262): recorded sid/lane, 30-day window, rates length >= COST_MIN_N (= 10), $1 gate on the goldens side; the COST_MIN_N cold-start case (no threshold, no colour) is pinned as a table leg, so a correct implementation no longer false-fails on arbitrary-length rates"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-021: Dynamic dollar colours and percentile goldens over 21 seeded sessions

## Property Statement

Across the 21 canonical seeded sessions (12 s-seeded + 8 g-seeded + `sess-self`,
per BC-1.05.008): the $ colour derives from the lane percentile
thresholds exactly (p75/p95 percentiles per the cost_thresholds math), $/h threshold
colouring, the ⛏ pick inside the $ block, and the $ / $/h number formatting match the
oracle-pinned goldens byte-for-byte, including colour-band boundary rows. The
for-all percentile leg is quantified over the population cost_thresholds actually
filters (SL:240-262, A2-14): a single recorded sid and lane, the 30-day window,
rates of length >= COST_MIN_N (= 10; shorter histories are the cold-start case
returning no threshold — no colour — pinned as a table leg, not a quick leg), and
the $1 session-minimum gate honoured on the goldens side.

## Source Contract

- **Primary BC:** BC-1.05.008 — Cost colouring goldens (21 seeded sessions).
- **Partial coverage:** BC-1.05.001 ($ colours from lane percentile thresholds),
  BC-1.05.002 ($/h segment threshold colouring), BC-1.05.003 (⛏ basis threshold),
  BC-1.05.005 (cost_thresholds p75/p95 percentiles), BC-1.05.007 ($ and $/h number
  formatting).
- **Invariant verified:** NFR-003 (byte parity on the colouring path); OD-135 CRITICAL
  tier (S1 coverage >= 95%; the mutation kill-rate target is a Phase 6 objective and
  does not gate P1 — OD-158).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** golden/parity tier — seeded-session goldens crossing threshold boundaries
  (band edges, basis crossings), plus percentile math tables; PLUS the legs the BC
  VP-tables route here (C2-08): testing/quick for-all legs for the invariants marked
  "property proof" in BC-1.05.001/002/003/005 (colour is a pure function of the lane
  percentile thresholds; p75 ≤ p95 whenever a pair is returned; ⛏ basis and $/h
  banding are pure threshold functions — the quick-leg oracle INDEPENDENTLY RE-DERIVES
  the BC-1.05.005 rule in the harness; a canonical table cannot oracle randomly
  generated inputs, the VP-041 A2-08 lesson), and a Tier C differential formatting-fuzz
  row for the surface
  marked "fuzz" in BC-1.05.007 ($ and $/h spellings), budgeted by
  `HYLO_PARITY_FUZZSECONDS`.
- **Honesty:** testable-only; boundaries pinned, continuity between them rides corpus
  breadth and Tier C.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Golden sessions | Go test, seeded cost histories | yes — 21 sessions | threshold bands, ⛏ basis, formatting |
| Property legs | `testing/quick`, *quick.Config with Values | sized | BC-1.05.001/002/003/005 for-all rows |
| Differential fuzz | parity harness, `HYLO_PARITY_FUZZSECONDS` | budget-bounded | BC-1.05.007 formatting |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestCostColouring_SeededSessions(t *testing.T) {
    for _, s := range SeededSessions21 { // 12 s + 8 g + sess-self (BC-1.05.008)
        frame := renderCostBlock(s.History(), s.USD, s.HourRate)
        assertGoldenBytes(t, s.CostGolden, frame)
    }
}

func TestCostProps_QuickLeg(t *testing.T) { // C2-08: for-all rows routed here by the BCs
    cfg := &quick.Config{MaxCount: 500, Values: func(args []reflect.Value, r *rand.Rand) {
        // A2-05: a Values filler must ASSIGN each arg (args[i] = reflect.ValueOf(x));
        // args arrives filled with zero reflect.Values — Elem().Set panics.
        // A2-12: the thresholds ARE the percentiles of the rates (BC-1.05.005), so
        // the generator produces rates and derives th from them — an independent th
        // would be unconstrained by the percentile assertions.
        // A2-14: the for-all quantifier is the FILTERED population — recorded sid
        // and lane, 30-day window, rates length >= COST_MIN_N (= 10); the
        // cold-start case (len < COST_MIN_N → no threshold, no colour) is a
        // pinned table leg, not a quick leg, so a correct implementation no
        // longer false-fails on arbitrary-length rates.
        rates := genFiniteRatesMinN(r, costMinN) // FINITE only and len >= 10 (BC-1.05.005 qualifier; OD-138 NaN usd rows are pinned table legs)
        args[0] = reflect.ValueOf(derivePercentile(rates, 0.75))
        args[1] = reflect.ValueOf(rates)
    }}
    if err := quick.Check(func(th thresholds, rates []float64) bool {
        c := costColor(th, rates)
        // A2-08: the oracle RE-DERIVES the percentiles from the BC-1.05.005 rule
        // (sort the finite inputs, pinned indices) — the check CAN fail; the bare
        // p75 ≤ p95 tautology is kept only as a corollary.
        return c.p75 == derivePercentile(rates, 0.75) &&
            c.p95 == derivePercentile(rates, 0.95) &&
            c.p75 <= c.p95 && coloringIsPure(th, rates)
    }, cfg); err != nil {
        t.Fatalf("cost invariant violated: %v", err)
    }
}
// BC-1.05.007 formatting fuzz rides TestParityTierC_DiffFuzz under internal/parity
// (HYLO_PARITY_FUZZSECONDS budget, VP-011 oracle discipline).
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestCostColouring_SeededSessions`; the
canonical vector register is BC-ALLOCATION "Canonical Test Vectors" (21 sessions,
BC-SL-101).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | 21 sessions + boundary rows | bounded |
| Proof complexity | N/A | |
| Tool support | Full | golden files |
| Estimated proof time | Days | seeding is the cost |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
