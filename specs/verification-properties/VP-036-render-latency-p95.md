---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-08-build-ci-release.md, behavioral-contracts/ss-06/BC-6.04.002.md, prd-supplements/nfr-catalog.md, owner-decisions-log-2026-11-14.md]
input-hash: "dc56a43"
traces_to: prd.md
source_bc: BC-6.04.002
module: internal/statusline (hot path), CI timing report
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

# VP-036: Render latency p95 <= 25 ms on the owner's Mac target (measured)

## Property Statement

Steady-state render latency on the owner's Mac (darwin/arm64) over the synthetic
fixture corpus, with metrics HTTP wait excluded per the case model, achieves p95 <=
25 ms (OD-117, labeled judgment call ≈3× over the measured 84.5 ms legacy median).
Measurement discipline: 1 warm-up + 5 timed runs, nearest-rank p95, fake-VM handling
time subtracted. The gate fails the build only with `HYLO_TIMING_GATE=1` — it binds on
the owner's Mac target; CI legs print the report and pass regardless.

## Source Contract

- **Primary BC:** BC-6.04.002 — Per-OS timing report; p95 <= 25 ms binds on the
  owner's Mac target.
- **Partial coverage:** NFR-001 (measurement method + baseline provenance 2026-11-15).
- **Invariant verified:** none (performance budget, not a logical property); the
  off-hot-path placement of the metrics fetch is enforced by the BC-6.02.003 case
  model, and the ancestor probe's microsecond cost claim (AD-07) rides this measurement.

## Property Class and Verification Method

- **Class:** performance.
- **Method:** measured property — the per-OS timing report; explicitly not a proof and
  not machine-independent: the number binds only where the gate is armed
  (`HYLO_TIMING_GATE=1` on the owner's Mac).
- **Honesty:** statistical measurement with named variance sources (loaded machine,
  corpus fixture); the weakest claim class in the index, by design.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Timing report | CI leg + local gate script | 6 runs, nearest-rank p95 | steady-state corpus refreshes |

## Proof Harness Skeleton

```go
func TestTimingReport_PerOS(t *testing.T) {
    rep := MeasureCorpus(warmup: 1, timed: 5, subtract: fakeVMHandling)
    PrintReport(rep) // every leg prints
    if gatingEnabled() && rep.p95 > 25*time.Millisecond {
        t.Fatalf("p95 = %v > 25 ms", rep.p95)
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; the timing report printer is table-tested per
ARCH-08; the gate arms only under `HYLO_TIMING_GATE=1`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Corpus refreshes | bounded |
| Proof complexity | Statistical | variance, not proof |
| Tool support | Full | in-tree report |
| Estimated proof time | Hours per leg | gate binding is local |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
