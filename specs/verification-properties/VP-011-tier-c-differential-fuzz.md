---
document_type: verification-property
level: L4
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-18T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.04.003.md, owner-decisions-log-2026-11-14.md]
input-hash: "0477f88"
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
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: SC-07 — Primary-BC line synced to BC-6.04.003 H1 (OD-149 all-OS wording)", "1.3 2026-11-17: ADV-P2 pass-2 fixes — property reclassified from liveness to safety (bounded-budget observation: every observed divergence carries a closed-set exclusion id); BC-6.04.003:65-67 domain filter (seeded proc_start, no numeric sids) enforced in the generator; the generator seed is logged for reproduction (A2-26)", "1.4 2026-11-18: ADV-P4 pass-4 fix — RK-2 disposition recounted from the taxonomy's declared ranges: 47 catalogued crash paths (CP-X01..X04, CP-S01..S17, CP-T01..T07, CP-N01..N03, CP-O01..O11, CP-A01..A05 = 4+17+7+3+11+5), agreeing with gene-transfusion-assessment.md; foreign-cache shapes are OD-160, not a CP family"]
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
compares stepwise stdout bytes and exit codes; within the fuzz budget every observed
divergence carries an id from the closed exclusion set. Budget 0 skips (PR legs); the
nightly workflow sets `HYLO_PARITY_FUZZSECONDS=1800` (30 minutes per OS, OD-149).

## Source Contract

- **Primary BC:** BC-6.04.003 — Tier C differential fuzz: nightly all three OSes, one
  clean run, non-gating, random valid inputs.
- **Disposition (OD-149, owner 2026-11-16):** the nightly run extends to all three OSes
  with a 30-minute budget per OS (`HYLO_PARITY_FUZZSECONDS=1800`); the P1 Tier C exit
  condition is ONE clean nightly run on all three OSes (owner judgment call).
- **Partial coverage:** RK-2 disposition (hunting P27-class hidden exception paths the
  47-path catalogue may have missed — error-taxonomy.md as of pass 4: CP-X01..X04,
  CP-S01..S17, CP-T01..T07, CP-N01..N03, CP-O01..O11, CP-A01..A05; the foreign-cache
  shapes ride exclusion id OD-160 and are not a CP family in the register).
- **Invariant verified:** DI-012 extension — any fuzz-found diff must resolve to an
  explained deviation or a defect; it can never silently broaden the exclusion list
  (glob-free machinery, VP-012).

## Property Class and Verification Method

- **Class:** safety, not liveness (A2-26): the observation is bounded — within a
  budgeted run, every divergence must carry a closed-set exclusion id, and any
  unexplained divergence fails the run. The nightly cadence is process discipline
  (OD-149's exit gate), not a liveness property of the code.
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
    seed := time.Now().UnixNano()
    t.Logf("tier C fuzz seed: %d (log with every divergence report)", seed) // A2-26
    gen := RandomValidCaseGenerator(seed)
    for run := 0; run < budgetRuns(); run++ {
        cs := gen.Next()
        if !inTierCDomain(cs) { // BC-6.04.003:65-67: seeded proc_start, no numeric sids
            continue
        }
        if diverged(RunOracle(cs), RunGoPort(cs)) && !isClosedExclusion(cs) {
            t.Fatalf("unexplained divergence in %s (seed %d)", cs.ID, seed)
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
