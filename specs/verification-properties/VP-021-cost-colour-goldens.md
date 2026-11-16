---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.05.001.md, behavioral-contracts/ss-01/BC-1.05.002.md, behavioral-contracts/ss-01/BC-1.05.003.md, behavioral-contracts/ss-01/BC-1.05.005.md, behavioral-contracts/ss-01/BC-1.05.007.md, behavioral-contracts/ss-01/BC-1.05.008.md]
input-hash: "ac182a9"
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

# VP-021: Dynamic dollar colours and percentile goldens over 20 seeded sessions

## Property Statement

Across the 20 canonical seeded sessions: the $ colour derives from the lane percentile
thresholds exactly (p75/p95 percentiles per the cost_thresholds math), $/h threshold
colouring, the ⛏ pick inside the $ block, and the $ / $/h number formatting match the
oracle-pinned goldens byte-for-byte, including colour-band boundary rows.

## Source Contract

- **Primary BC:** BC-1.05.008 — Cost colouring goldens (20 seeded sessions).
- **Partial coverage:** BC-1.05.001 ($ colours from lane percentile thresholds),
  BC-1.05.002 ($/h segment threshold colouring), BC-1.05.003 (⛏ basis threshold),
  BC-1.05.005 (cost_thresholds p75/p95 percentiles), BC-1.05.007 ($ and $/h number
  formatting).
- **Invariant verified:** NFR-003 (byte parity on the colouring path); OD-135 CRITICAL
  tier (S1 coverage >= 95%).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** golden/parity tier — seeded-session goldens crossing threshold boundaries
  (band edges, basis crossings), plus percentile math tables.
- **Honesty:** testable-only; boundaries pinned, continuity between them rides corpus
  breadth and Tier C.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Golden sessions | Go test, seeded cost histories | yes — 20 sessions | threshold bands, ⛏ basis, formatting |

## Proof Harness Skeleton

```go
func TestCostColouring_SeededSessions(t *testing.T) {
    for _, s := range SeededSessions20 {
        frame := renderCostBlock(s.History(), s.USD, s.HourRate)
        assertGoldenBytes(t, s.CostGolden, frame)
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestCostColouring_SeededSessions`; the
canonical vector register is BC-ALLOCATION "Canonical Test Vectors" (20 sessions,
BC-SL-101).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | 20 sessions + boundary rows | bounded |
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
