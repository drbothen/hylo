---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T23:45:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.009.md, prd-supplements/nfr-catalog.md]
input-hash: "5241649"
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
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fix — removed the BC-1.06.002 partial-coverage claim (A2-04); that property is VP-018's, and this VP's fakes do not exercise the slash-sid fault site", "1.3 2026-11-18T23:45:00Z: ADV-P5 fix (B01 sibling) — OrderTable scope widened past the CP-S/CP-N triggers: the O-site rows join the sequence table (CP-O06..O08 skip-and-turn-drop per OD-167, CP-O09, the OD-166 record skip at 7c, CP-O10/O11 conversion degrades at 7d), matching the corrected ARCH-03 step table and the error taxonomy"]
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
- **Partial coverage:** none beyond the primary BC. (BC-1.06.002's failed-replace
  property — persists nothing — is verified by VP-018; the ordered script is what
  makes that property observable per step, motivating AD-03, but this VP's recording
  fakes do not exercise the slash-sid fault site, so no coverage is claimed here.)
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
    for _, tc := range OrderTable { // happy + degrade-at-k for k in 0..8 (CP-S/CP-N)
        // + the O-site rows: CP-O06..O08 SKIP the line write and DROP the in-flight
        // turn (OD-167) — the recording env asserts the skip+drop sequence, not a
        // degrade; CP-O09 the extended-D4-EX-2 no-write row; OD-166 the 7c record
        // skip; CP-O10/O11 the 7d conversion degrades (BC-1.05.007). Sibling of
        // ADV-P5-B01: the step table outdates these sites no longer.
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
