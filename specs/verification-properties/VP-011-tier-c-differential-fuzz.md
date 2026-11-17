---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-18T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.04.003.md, owner-decisions-log-2026-11-14.md]
input-hash: "a90484b"
traces_to: prd.md
source_bc: BC-6.04.003
bcs: [BC-6.04.003]
module: internal/parity
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: SC-07 — Primary-BC line synced to BC-6.04.003 H1 (OD-149 all-OS wording)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-011: Tier C differential fuzz hunts hidden divergence paths

## Property Statement

A nightly, non-gating differential fuzz drives random valid inputs (stdin
templates, settings, metrics modes, clock steps) to both the oracle and the Go port and
compares stepwise stdout bytes and exit codes; over the fuzz budget no divergence is
found that is not covered by the closed exclusion set. Budget 0 skips (PR legs); the
nightly workflow sets `HYLO_PARITY_FUZZSECONDS=1800` (30 minutes per OS, OD-149).

## Source Contract

- **Primary BC:** BC-6.04.003 — Tier C differential fuzz: nightly all three OSes, one
  clean run, non-gating, random valid inputs.
- **Disposition (OD-149, owner 2026-11-16):** the nightly run extends to all three OSes
  with a 30-minute budget per OS (`HYLO_PARITY_FUZZSECONDS=1800`); the P1 Tier C exit
  condition is ONE clean nightly run on all three OSes (owner judgment call).
- **Partial coverage:** RK-2 disposition (hunting P27-class hidden exception paths the
  43-path catalogue may have missed).
- **Invariant verified:** DI-012 extension — any fuzz-found diff must resolve to an
  explained deviation or a defect; it can never silently broaden the exclusion list
  (glob-free machinery, VP-012).

## Property Class and Verification Method

- **Class:** liveness (a continuous hunt: every night either confirms agreement or
  surfaces a divergence for triage).
- **Method:** property-based/fuzz test — `TestParityTierC_DiffFuzz` with random valid
  input generation to both sides; non-gating by ruling.
- **Honesty:** testable-only; statistical, not exhaustive — budget-bounded.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Differential fuzz | `go test ./internal/parity -run TestParityTierC_DiffFuzz`, env `HYLO_PARITY_FUZZSECONDS` | no (random), budget-bounded | random valid input space, nightly |

## Proof Harness Skeleton

```go
func TestParityTierC_DiffFuzz(t *testing.T) {
    if fuzzSeconds() == 0 { t.Skip("budget 0: skip on PR legs") }
    gen := RandomValidCaseGenerator()
    for run := 0; run < budgetRuns(); run++ {
        cs := gen.Next()
        if diverged(RunOracle(cs), RunGoPort(cs)) && !isClosedExclusion(cs) {
            t.Fatalf("unexplained divergence in %s", cs.ID)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestParityTierC_DiffFuzz`, budget env `HYLO_PARITY_FUZZSECONDS` (0 = skip; nightly
sets 1800 = 30 min per OS), per ARCH-07 (OD-149).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Infinite | statistically sampled |
| Proof complexity | N/A | hunting, not proving |
| Tool support | Full | stdlib + generator |
| Estimated proof time | Nights | P1 exit = ONE clean nightly run on all 3 OSes (OD-149) |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
