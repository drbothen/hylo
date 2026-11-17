---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-18T01:30:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.07.007.md, owner-decisions-log-2026-11-14.md]
input-hash: "7fc5393"
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

# VP-039: Elapsed-clock float computations agree at ulp level across fusion regimes

## Property Statement

For every plausible elapsed-clock input pair (now_ms − start_ms at MM:SS rendering
precision), the fused computation `float64(ms) * 0.001` evaluated under arm64 FMA
contraction and the unfused two-step evaluation (divide, then minute/second split)
agree to within 1 ulp, and the rendered `MM:SS` string is byte-identical across the
two regimes. No elapsed-clock rendering may flicker between `MM:SS` values because of
compiler fusion: the rendered value is a function of the input pair alone. The
detector test is compiled and run only on darwin/arm64 (build-tagged), where the Go
compiler contracts FMA (CONV-ABS-77, PR-15); on all other OSes the same source path
compiles without contraction, so the unfused evaluation is the definition and the
rendered string is pinned by the BC-1.07.007 tables.

## Source Contract

- **Primary BC:** BC-1.07.007 — Token segment (_fmt_tokens) and running-only elapsed
  clock; PR-15: fused vs unfused elapsed-clock floats agree at ulp level on arm64.
- **Partial coverage:** none (standalone convolution property; the `_fmt_tokens`
  dense-grid leg of BC-1.07.007 rides the Tier A T-family tables, VP-009).
- **Invariant verified:** CONV-ABS-77 (arithmetic-convention abs fixtures: floating
  fusion must not change rendered output).

## Property Class and Verification Method

- **Class:** invariant (rendered-output equivalence across evaluation regimes).
- **Method:** unit/property test — a dense grid over elapsed-ms deltas around
  minute/second boundaries plus a seeded random sample; each input is evaluated fused
  and unfused, asserting ≤ 1 ulp difference on the float and byte-identical `MM:SS`
  output; a build-tagged darwin/arm64 detector asserts the fused path is actually
  exercised (the detector reads the compiler's contraction behaviour via a
  known-contraction probe pair and fails loudly if the regime changed).
- **Honesty:** testable-only; equivalence is sampled, not deduced — the grid covers
  the rounding-boundary neighbourhoods where a 1-ulp difference could flip the
  rendered minute or second.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Ulp-equivalence grid + sample | Go test, `internal/statusline` (build tag `darwin && arm64`) | yes — dense boundary grid, seeded sample | elapsed-clock input space at MM:SS precision |
| Fusion-regime detector | Probe-pair test, darwin/arm64 only | yes | compiler contraction regime change |

## Proof Harness Skeleton

```go
//go:build darwin && arm64

func TestElapsedClock_UlpAgreement(t *testing.T) { // PR-15, CONV-ABS-77
    for _, ms := range ElapsedBoundaryGrid() { // minute/second rounding neighbourhoods
        fused, unfused := EvalFused(ms), EvalUnfused(ms)
        if ulpDiff(fused, unfused) > 1 {
            t.Fatalf("ms=%d: %v vs %v exceeds 1 ulp", ms, fused, unfused)
        }
        if mmss(fused) != mmss(unfused) {
            t.Fatalf("ms=%d: rendered MM:SS flickers across fusion regimes", ms)
        }
    }
    if !contractFMA(probePair()) { // detector: the fused regime is real
        t.Fatal("arm64 no longer contracts FMA; revisit the ulp-equivalence claim")
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestElapsedClock_UlpAgreement`
(darwin/arm64 build tag; skipped as not-applicable on the Linux/Windows CI legs,
where the unfused evaluation is definitional — the CI matrix pins this in the
VP-037 OS matrix disclosure).

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
