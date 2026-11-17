---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.009.md, prd-supplements/nfr-catalog.md]
input-hash: "77638f1"
traces_to: prd.md
source_bc: BC-1.01.009
bcs: [BC-1.01.009]
module: internal/statusline (Render orchestrator)
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

# VP-008: Effect order is exactly legacy's; a crash at step k keeps writes 1..k-1

## Property Statement

`Render` executes the ARCH-03 effect-step script (steps 0-8) in exactly legacy's order:
a crash or typed degrade at step k leaves all writes of steps 1..k-1 persisted and
suppresses all later writes; identical cache states after happy and degraded runs are
therefore observable. No step reordering, buffering, or post-error commit exists.

## Source Contract

- **Primary BC:** BC-1.01.009 — Side effects run in legacy order; a degrade keeps
  earlier writes.
- **Partial coverage:** BC-1.06.002 (failed replace persists nothing — the in-memory
  overlay would get this wrong, motivating AD-03).
- **Invariant verified:** NFR-002 consequence (write ordering preserved, BC-1.01.009);
  AD-03 (pure widgets + ordered effect script).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — order-recording fakes behind every `Env` seam assert
  the exact step sequence for happy paths and one degrade-at-step-k row per step; the
  resulting cache-dir states are byte-compared against legacy-run seeds.
- **Honesty:** testable-only. Order is an observational property of the orchestrator;
  it is pinned by recording fakes and by parity (VP-009), not proven.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Recording fakes | Go test | yes — 9 steps x happy/degrade | full script, per-step degrade rows |

## Proof Harness Skeleton

```go
func TestEffectOrder_LegacySequence(t *testing.T) {
    for _, tc := range OrderTable { // happy + degrade-at-k for k in 0..8
        rec := newRecordingEnv(tc.DegradeAt)
        _, err := statusline.Render(tc.Stdin, rec)
        if got := rec.Log(); got != tc.WantSequence {
            t.Fatalf("%s: sequence %s", tc.Name, got)
        }
        rec.AssertCacheStatesMatchLegacySeeds(t)
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestEffectOrder_LegacySequence`; cache
states after degraded runs additionally pinned by the `swap` parity family
(`TestParityCacheSwap_FourCaches`, VP-019).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Small | 9 steps, 2 outcomes each |
| Proof complexity | N/A | observational pinning |
| Tool support | Full | recording fakes |
| Estimated proof time | Days | per-step seed states are the cost |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
