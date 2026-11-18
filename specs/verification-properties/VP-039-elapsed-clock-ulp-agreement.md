---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-18T14:32:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.07.007.md, owner-decisions-log-2026-11-14.md]
input-hash: "c16bf76"
traces_to: prd.md
source_bc: BC-1.07.007
bcs: [BC-1.07.007]
module: internal/statusline (subagent elapsed clock)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-18T09:01:00Z: ADV-P3 fixes (A2-03) — computation restated to legacy exactly: elapsed = max(now_ms - start, 0)/1000 with now_ms = time.time()*1000 (SL:889, 919; the 0.001-multiply form was wrong); fusion site named as time*1000 - start; oracle corrected from test-local helper agreement to bit-exact comparison against CPython-derived goldens, with the explicit float64() conversion the BC requires forbidding FMA contraction on EVERY arm64 target (darwin, linux, windows — not only darwin/arm64)", "1.2 2026-11-18T14:32:00Z: ADV-P4 fix (A2-09) — build constraint split and made valid: the golden-parity test carries NO build tag (pure float64 comparison, runs on every CI leg including amd64); only the fusion-regime detector is `//go:build arm64` with the comment on its own line; the grid now draws (start, now) pairs at wall-clock epoch-ms magnitude (~1.7e12) with deltas in the ulp neighbourhoods of MM:SS boundaries — the regime the FMA guard protects"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-039: Elapsed-clock float computations agree at ulp level across fusion regimes

## Property Statement

Legacy computes the elapsed clock as `now_ms = time.time() * 1000`, then
`elapsed = max(now_ms - start, 0) / 1000` (SL:889, 919; BC-1.07.007). The fusion
hazard is the `time*1000 - start` shape: on every arm64 target (darwin/arm64,
linux/arm64, windows/arm64) the Go compiler may contract a multiply–subtract pair
into FMA, contracting the product back into the subtraction and shifting results by
ulps. The BC therefore requires an **explicit `float64()` conversion** of the product
before the subtraction, which forbids contraction by construction on every arm64
target. Parity is not a tolerance claim: the production value is compared **bit-exactly
against CPython-derived goldens** (the unfused evaluation is the definition — CPython
performs each op separately, no fusion), and the rendered `MM:SS` is byte-identical
across regimes. The rendered value is a function of the input pair alone; no
elapsed-clock rendering may flicker between `MM:SS` values because of compiler
fusion. A build-tagged arm64 detector (any arm64 OS; compiled and run on the
darwin/arm64 CI leg) asserts the compiler would contract an unconstrained
multiply–subtract probe pair — the regime the conversion guards against is real —
and that the production function agrees with the unfused reference bit-exactly.
The golden-parity comparison itself is architecture-independent pure float64
evaluation against committed goldens and runs on every CI leg, amd64 included;
only the detector is arm64-tagged.

## Source Contract

- **Primary BC:** BC-1.07.007 — Token segment (_fmt_tokens) and running-only elapsed
  clock; PR-15: the explicit float64() conversion forbids fusion; unfused =
  CPython-exact.
- **Partial coverage:** none (standalone convolution property; the `_fmt_tokens`
  dense-grid leg of BC-1.07.007 rides the Tier A T-family tables, VP-009).
- **Invariant verified:** CONV-ABS-77 (arithmetic-convention abs fixtures: floating
  fusion must not change rendered output).

## Property Class and Verification Method

- **Class:** invariant (rendered-output equivalence across evaluation regimes).
- **Method:** unit/property test — a dense grid over elapsed-ms deltas around
  minute/second boundaries plus a seeded random sample; each input's production
  elapsed value (carrying the explicit `float64()` conversion) is compared bit-exactly
  against the CPython-derived golden for the same input (unfused reference); a
  build-tagged arm64 detector asserts the contraction regime is real via a
  known-contraction probe pair and fails loudly if it changed.
- **Honesty:** testable-only; the golden comparison is sampled, not deduced — the
  grid covers the rounding-boundary neighbourhoods where an FMA contraction could
  flip the rendered minute or second. Helper-vs-helper ulp tolerance inside the test
  is instrumentation, not the parity claim.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Golden-parity grid + sample | Go test, `internal/statusline` (no build tag) | yes — dense boundary grid, seeded sample | elapsed-clock input space at MM:SS precision, bit-exact vs CPython-derived goldens |
| Fusion-regime detector | Probe-pair test, arm64 | yes | compiler contraction regime change |

## Proof Harness Skeleton

```go
// TestElapsedClock_UnfusedGoldenParity has NO build tag (A2-09): comparing float64
// evaluations against committed CPython-derived goldens is architecture-independent,
// so the parity claim holds on every CI leg, amd64 included.
func TestElapsedClock_UnfusedGoldenParity(t *testing.T) { // PR-15, CONV-ABS-77
    for _, p := range ElapsedWallClockGrid() { // (start, now) pairs at wall-clock
        // epoch-ms magnitude (~1.7e12 ms), deltas in the ulp neighbourhoods of
        // MM:SS rounding boundaries — at 1.7e12 the product time*1000 has an ulp
        // of ~2^-12 ms, exactly where FMA contraction can flip a rendered second.
        // CPython-derived golden: unfused max((time*1000 as float64) - start, 0)/1000
        want := mmss(GoldenElapsed(p.Start, p.Now))
        if got := mmss(ProductionElapsed(p.Start, p.Now)); got != want { // explicit float64() conversion
            t.Fatalf("start=%d now=%d: rendered %s, CPython golden %s", p.Start, p.Now, got, want)
        }
    }
}

// every arm64 target contracts; darwin/arm64 runs the detector in CI
//
//go:build arm64

func TestElapsedClock_FusionRegimeDetector(t *testing.T) { // A2-09: tag on the detector only
    if !contractFMA(probePair()) { // detector: the fused regime is real on arm64
        t.Fatal("arm64 no longer contracts FMA; revisit the float64() fusion guard")
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestElapsedClock_UnfusedGoldenParity`
(no build tag — runs on every CI leg, amd64 included; the amd64 legs pin the
definitional unfused evaluation) plus `TestElapsedClock_FusionRegimeDetector`
(`//go:build arm64` only; the CI matrix discloses the split in the VP-037 OS matrix).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Small, boundary-dense | ms deltas at MM:SS precision |
| Proof complexity | N/A | sampled equivalence + detector |
| Tool support | Full | math bits, overflow-free ulp compare on float64 |
| Estimated proof time | Hours | grid authoring dominates |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-18 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
