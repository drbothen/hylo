---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.04.002.md, behavioral-contracts/ss-01/BC-1.04.004.md, behavioral-contracts/ss-01/BC-1.04.009.md, behavioral-contracts/ss-01/BC-1.04.014.md, behavioral-contracts/ss-01/BC-1.04.020.md, prd-supplements/test-vectors.md]
input-hash: "4bd1594"
traces_to: prd.md
source_bc: BC-1.04.002
bcs: [BC-1.04.001, BC-1.04.002, BC-1.04.003, BC-1.04.004, BC-1.04.005, BC-1.04.006, BC-1.04.007, BC-1.04.008, BC-1.04.009, BC-1.04.010, BC-1.04.011, BC-1.04.012, BC-1.04.013, BC-1.04.014, BC-1.04.015, BC-1.04.016, BC-1.04.017, BC-1.04.018, BC-1.04.019, BC-1.04.020, BC-1.04.021]
module: internal/statusline (sample.go, row2.go, sparkline.go, telemetry.go)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-030: Row-2 telemetry family — TTL machine, freshness ladder, NaN crash paths

## Property Statement

Row-2 telemetry matches the oracle-pinned tables: fetch_sample (query, 1.5 s timeout,
first-wins), get_sample TTL / KEEP_DEAD state machine and pinned 11-step sequence with
cache key order, history point rules (90 s cap, 2 s gap) with `_norm_pt`, freshness
ladder + stale suffix, health dot (green-while-success rule), queue/KV/throughput/
sparkline/TTFT/power/idle segments incl. format boundaries, mine segment, VM fetch
whenever ROWS >= 2, and the NaN/+Inf crash paths (CP-N01/N02) with wall-colour
mismatch quirk.

## Source Contract

- **Primary BC:** BC-1.04.002 — get_sample TTL / KEEP_DEAD state machine.
- **Partial coverage:** BC-1.04.001..021 (all twenty-one S1.04 contracts; NaN crash
  paths also ride VP-001).
- **Invariant verified:** NFR-005 (32-point metric histories — joint with VP-031);
  OD-130 (±Inf treated as unknown, defensive parse).


## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — the 11-step get_sample sequence table, TTL/KEEP_DEAD
  transition matrices, freshness-ladder rows, sparkline glyph/color/scale tables, NaN/inf
  fault rows.
- **Honesty:** testable-only; the 1.5 s timeout and first-wins semantics are
  fake-server integration rows.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Sequence table | Go test, 11 canonical steps | yes | get_sample pinned sequence |
| Segment tables | Go test | yes | all row-2 segments x freshness states |
| Fault rows | Go test (httptest fake) | yes | down/500/garbage/±Inf metrics |

## Proof Harness Skeleton

```go
func TestGetSample_Pinned11StepSequence(t *testing.T) {
    for _, s := range SampleSequence11 {
        got := advanceSample(newFakeMetrics(), s.Steps...)
        if got != s.Want { t.Fatalf("step %d: %+v", s.ID, got) }
    }
}
```

## Named Tests (OD-145 table where applicable)

`row2` parity family (ARCH-07 case-id grammar) + the metrics-mode rows
(down/500/garbage) of the ARCH-07 case model; in-tree
`TestGetSample_Pinned11StepSequence`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Sequence + segment tables | bounded |
| Proof complexity | N/A | |
| Tool support | Full | httptest fake |
| Estimated proof time | Weeks | segment volume |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
