---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.009.md, behavioral-contracts/ss-05/BC-5.04.003.md, domain-spec/invariants.md]
input-hash: "4a8972b"
traces_to: prd.md
source_bc: BC-1.01.009
bcs: [BC-1.01.009, BC-5.04.003]
module: internal/statusline (Render, Env)
proof_method: proptest
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

# VP-007: Render is deterministic under injected seams

## Property Statement

For a fixed `Env` (recorded seam values: clock value, seam-returned files, cache
contents, metrics response, config), `Render(stdin, env)` produces byte-identical
output on repeated invocation, and the clock seam is read exactly once per render
(IM-14 — a live-clock minute-straddle mid-render cannot occur). All nondeterminism
sources are `Env` members; none is read behind `Render`'s back.

## Source Contract

- **Primary BC:** BC-1.01.009 — Side effects run in legacy order; a degrade keeps
  earlier writes (order totality implies seam-closedness).
- **Partial coverage:** BC-5.04.003 (TimeFloat: ns→s float, once per render).
- **Invariant verified:** DI-007 corollary (inputs are only stdin, transcript, metrics
  store, own caches — structurally, via Env); AD-03/AD-10 seam discipline.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** property-based test — a generator produces random `Env` recordings;
  each `Env` is replayed twice (and shuffled-order read-checked) asserting identical
  output bytes; a counting `Now` asserts exactly-one clock read.
- **Honesty:** testable-only. Seam-closedness (no hidden global reads) is asserted by
  the recording fakes noticing reads, not proven; a static lint on `Env` scope is a
  code-review obligation, mirroring VP-022.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Property replay | Go test + generator | yes — recording fakes | random Env recordings, double replay |
| Counting seams | Go test | exact | one `Now` read per render |

## Proof Harness Skeleton

```go
func TestRender_DeterministicUnderSeams(t *testing.T) {
    for _, env := range generatedEnvs(200) {
        a, _ := statusline.Render(stdin, env.Record())
        b, _ := statusline.Render(stdin, env.Record())
        if !bytes.Equal(a, b) { t.Fatal("nondeterministic render") }
        if env.NowReads() != 1 { t.Fatalf("clock read %d times", env.NowReads()) }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestRender_DeterministicUnderSeams`; the
seam recordings double as ARCH-07 harness hooks (AD-10).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Large but generatable | Env recordings |
| Proof complexity | Low-medium | determinism is structural |
| Tool support | Full | plain Go |
| Estimated proof time | Days | generator breadth is the cost |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
