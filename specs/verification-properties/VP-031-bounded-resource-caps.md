---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.03.003.md, behavioral-contracts/ss-01/BC-1.03.005.md, behavioral-contracts/ss-01/BC-1.04.003.md, prd-supplements/nfr-catalog.md]
input-hash: "9e17709"
traces_to: prd.md
source_bc: BC-1.03.005
bcs: [BC-1.03.003, BC-1.03.005, BC-1.04.003]
module: internal/statusline (store caps)
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

# VP-031: Bounded per-refresh state — legacy-identical caps

## Property Statement

Per-refresh state is capped exactly as legacy capped it: 256-entry usage dedup,
32-point metric histories, 1,000-line turn identity window, 512 KB transcript read
steps, memory-256 mix cache. Each cap value is a named constant or registry key with
rationale (D15) — the caps legacy fixed are named constants (T-061/062 class), the
tunable ones are registry keys — and exceeding a cap evicts per legacy's discipline
(FIFO/oldest-first as the owning BC rules).

## Source Contract

- **Primary BC:** BC-1.03.005 — Usage dedup per message id (memory 256).
- **Partial coverage:** BC-1.03.003 (512 KB read steps), BC-1.04.003 (90 s cap, 2 s
  gap — 32-point histories).
- **Invariant verified:** NFR-005 (table-verified caps identical to legacy).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — cap±1 boundary rows per cap; eviction-order rows.
- **Honesty:** testable-only; boundary tables, plus a static check that cap constants
  match the registry/constant register (no silent retuning).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Cap boundary tables | Go test | yes — cap±1 per cap | all five caps + eviction rows |
| Constant pin | registry golden | yes | cap provenance (D15) |

## Proof Harness Skeleton

```go
func TestCaps_LegacyIdentical(t *testing.T) {
    if usageDedupCap() != 256 { t.Fatal("dedup cap drifted") }
    if metricHistoryCap() != 32 { t.Fatal("history cap drifted") }
    if turnIdentityWindow() != 1000 { t.Fatal("identity window drifted") }
    if transcriptStepBytes() != 512*1024 { t.Fatal("step bytes drifted") }
    if mixCacheMemory() != 256 { t.Fatal("mix cache memory drifted") }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestCaps_LegacyIdentical` + boundary
matrices per cap.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Five caps x ±1 | tiny |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Hours | |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
