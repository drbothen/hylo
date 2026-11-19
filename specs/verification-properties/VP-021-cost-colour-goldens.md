---
document_type: verification-property
level: L4
version: "1.8"
status: draft
producer: architect
timestamp: 2026-11-25T09:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.05.001.md, behavioral-contracts/ss-01/BC-1.05.002.md, behavioral-contracts/ss-01/BC-1.05.003.md, behavioral-contracts/ss-01/BC-1.05.005.md, behavioral-contracts/ss-01/BC-1.05.007.md, behavioral-contracts/ss-01/BC-1.05.008.md]
input-hash: "ab6bf0f"
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
modified: ["1.1 2026-11-18T09:18:00Z: ADV-P3 fixes — the legs the BC VP-tables route here now exist in this document: testing/quick for-all legs (BC-1.05.001/002/003/005 threshold/percentile invariants) and a Tier C differential formatting-fuzz row (BC-1.05.007) (C2-08); OD-135 invariant claim recast per OD-158, mutation non-gating in P1 (A2-23)", "1.2 2026-11-18T14:18:00Z: ADV-P4 fixes — seeded-session count corrected to 21 (12 s + 8 g + sess-self, BC-1.05.008; A09/C2-04), fixture slice renamed SeededSessions21; quick.Values filler rewritten to the assigning form args[i] = reflect.ValueOf(x) (A2-05)", "1.3 2026-11-19T12:00:00Z: pass-6 fixes (A2-12: the quick-leg oracle respelled as the harness re-derivation of the BC-1.05.005 rule; the generator derives th from rates (no unconstrained th))", "1.4 2026-11-19T18:00:00Z: pass-7 fix (A2-14) — the quick leg's quantifier is the filtered population (SL:240-262): recorded sid/lane, 30-day window, rates length >= COST_MIN_N (= 10), $1 gate on the goldens side; the COST_MIN_N cold-start case (no threshold, no colour) is pinned as a table leg, so a correct implementation no longer false-fails on arbitrary-length rates", "1.5 2026-11-20T18:00:00Z: pass-11 fix (A2-03, orchestrator call 10) — the percentile property derived from BC-1.05.005 exactly: the quantifier runs over qualified HISTORY ENTRIES building TWO lists (dollar list per PC1/PC2 — the $ colour thresholds come from THIS list, not the rate list; rate list further gated by PC3's per-src api_ms need, cc 300000 vs other 1800000); PC1's self-exclusion (k == sid skipped) replaces the 'single recorded sid' misstatement; the NaN finite restriction (EC-009, Python sorted with a NaN is non-monotone) carried normatively in the Method, not only a sketch comment; skeleton generator rewritten to entries → two lists", "1.6 2026-11-21T09:00:00Z: pass-11 residual — the Method paragraph's corrupted glyph line (a stray wrench emoji) repaired to its clause text '⛏ basis and $/h'; no other change", "1.7 2026-11-21T22:30:00Z: pass-12 fix (A2-19, sketch only) — the quick.Values filler assigns each argument its SIGNATURE type: args[0]/[2] take assembled thresholds structs, args[1]/[3] take the underlying []float64 lists (a scalar percentile float was assigned to the []float64 parameters)", "1.8 2026-11-25T09:00:00Z: pass-14 fix (ADV-P14-A2-02) — the COST_MIN_N cold-start parenthetical no longer says 'no colour': with no threshold pair the $ amount takes the fallback ladder (grey below min_usd $1, yellow at or above cold_yellow_usd fallback 25, else white; BC-1.05.001 PC-1, SL:610-615) and $/h is grey (BC-1.05.002 PC-2, SL:624), matching legacy and the owning BCs"]
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
for-all percentile leg is derived from BC-1.05.005 exactly (PC1-PC4, SL:240-262;
A2-14, A2-03). The quantifier runs over HISTORY ENTRIES, not bare rate lists, and
cost_thresholds builds TWO lists qualified independently (A2-03): the DOLLAR list —
the $ colour thresholds come from this list, not from the rate list — and the RATE
list, a further subset of it. An entry `(k, e)` qualifies for the dollar list iff
(PC1) it is not self-excluded — a stored key `k == sid` is SKIPPED (self-exclusion
of the current sid, not "a single recorded sid") — and `e.lane == lane`, and it is
within the strict 30-day window (`now - ts > window_s` excludes; exactly 30 d
counts, EC-004), and (PC2) `e.usd` is a number (bool counts) with `usd >= min_usd`
($1). It additionally qualifies for the rate list iff (PC3) `e.api_ms` is a number
and `api_ms >= need`, the PER-SRC gate: `need = rate_min_api_ms.cc` = 300000 when
`e.src == "cc"`, `rate_min_api_ms.other` = 1800000 for every other src (absent
included); the rate value is `usd / (api_ms / 3.6e6)`. Each list independently
returns None below COST_MIN_N (= 10; the cold-start case — no threshold, but NOT
no colour: the $ amount still takes the fallback ladder, grey below `min_usd`
($1), yellow at or above `cold_yellow_usd` (fallback 25), else white
(BC-1.05.001 PC-1, SL:610-615), and the $/h segment is grey (BC-1.05.002 PC-2,
SL:624) — pinned as a table leg, not a quick leg); else sort ascending and
floor-index (PC4). NaN-bearing histories are LEGAL inputs (EC-009, OD-138: pinned
byte-for-byte per exact file order); a NaN can land on a picked index (Python
`sorted` with a NaN is non-monotone), so the ordering corollary is stated only
over NaN-free populations — the finite restriction is carried in the Method, not
just a sketch comment.

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
  percentile thresholds; p75 ≤ p95 only for NAN-FREE populations — the finite restriction is normative
  here, because EC-009's legal NaN histories can put a NaN on a picked index and
  return an unordered pair (Python `sorted` with a NaN is non-monotone, A2-03);
  ⛏ basis and $/h
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
        // A2-12: the thresholds ARE the percentiles (BC-1.05.005), derived in the
        // harness — an independent th would be unconstrained.
        // A2-14/A2-03: the quantifier is the QUALIFIED-HISTORY population of
        // BC-1.05.005 PC1-PC4 — entries, not bare rate lists. The harness
        // re-derives BOTH lists: usdList (PC1: k == sid SELF-EXCLUDED, lane
        // match, strict 30-d window; PC2: numeric usd, usd >= min_usd) and
        // rateList (further subset by PC3: numeric api_ms >= PER-SRC need —
        // cc 300000, other 1800000 — value usd/(api_ms/3.6e6)). The $ colour
        // thresholds derive from usdList, the ⛏/$/h bands from rateList; each
        // list independently returns None below COST_MIN_N (= 10). FINITE
        // (NaN-free) populations only for the ordering corollary; EC-009
        // NaN-bearing histories are pinned table legs ordered per exact file
        // order (OD-138).
        h := genQualifiedHistories(r, costMinN)
        // A2-19: each arg's TYPE must match the property signature — a scalar
        // percentile float does not fit a []float64 (or thresholds) parameter.
        usdPair := thresholds{p75: derivePercentile(h.Usd, 0.75), p95: derivePercentile(h.Usd, 0.95)}  // usd pair
        ratePair := thresholds{p75: derivePercentile(h.Rate, 0.75), p95: derivePercentile(h.Rate, 0.95)} // rate pair
        args[0] = reflect.ValueOf(usdPair)
        args[1] = reflect.ValueOf(h.Usd)   // the []float64 the percentiles derive from
        args[2] = reflect.ValueOf(ratePair)
        args[3] = reflect.ValueOf(h.Rate)
        args[4] = reflect.ValueOf(h)
    }}
    if err := quick.Check(func(usTh thresholds, usd []float64, rateTh thresholds, rate []float64, h histories) bool {
        c := costColor(usTh, rateTh, h)
        // A2-08: the oracle RE-DERIVES the percentiles from the BC-1.05.005 rule
        // (sort the finite inputs, pinned indices) — the check CAN fail; the bare
        // p75 ≤ p95 tautology is kept only as a corollary over NaN-free lists.
        return c.usdPair == usTh && c.ratePair == rateTh &&
            usTh.p75 <= usTh.p95 && rateTh.p75 <= rateTh.p95 &&
            coloringIsPure(usTh, rateTh, h)
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
