---
document_type: verification-property
level: L4
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-18T15:02:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-08-build-ci-release.md, behavioral-contracts/ss-06/BC-6.04.002.md, prd-supplements/nfr-catalog.md, owner-decisions-log-2026-11-14.md]
input-hash: "2321059"
traces_to: prd.md
source_bc: BC-6.04.002
bcs: [BC-6.04.002]
module: internal/statusline (hot path), CI timing report
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fix — sampling aligned to NFR-001: 20 runs per case, p95 = 19th sorted, binds per case, no pooling (A2-27)", "1.3 2026-11-18T09:20:00Z: ADV-P3 fixes (A2-09) — skeleton drops Go-named arguments (positional call with comments); gate computation excludes the >512 KB oversize fixture, which is timed and reported but exempt from the gate", "1.4 2026-11-18T15:02:00Z: ADV-P4 fix (A2-19) — the >512 KB fixture exemption made conditional per product-brief: the exception applies only when the fixture misses the p95 target; if it meets the budget it is gated like every case"]
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
Sampling discipline is per **case** (NFR-001): each case gets 1 warm-up + 20 timed
runs; the case's 20 samples are sorted and the nearest-rank p95 is the 19th sample;
the gate **binds per case** — every case's p95 must meet the budget, with no pooling
across the corpus (pooling would hide a slow case behind fast ones). One STATED,
UNCONDITIONAL exception (the brief's speed judgment call): the >512 KB-line fixture is
exempt from the binding gate — its samples are still collected, reported and ranked in
the gate output like every case's, but it never fails the build. The exemption is
authored as an exception, not implied by a conditional that could never fire
(ADV-P5-A2-13). The gate fails the build only with `HYLO_TIMING_GATE=1` — it binds on
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
| Timing report | CI leg + local gate script | per case: 1 warm-up + 20 timed runs, nearest-rank p95 = 19th sorted sample; binds per case, no pooling | steady-state corpus cases |

## Proof Harness Skeleton

```go
func TestTimingReport_PerOS(t *testing.T) {
    // A2-09: positional call — Go has no named arguments. Per case: 1 warm-up + 20
    // timed runs, nearest-rank p95 = 19th sorted sample, binds per case, no pooling.
    rep := MeasureCorpus(1, 20, fakeVMHandling)
    PrintReport(rep) // every leg prints
    // The >512 KB-line fixture is timed and REPORTED but exempt from the gate
    // (the stated exception), so it must not enter the worst-case computation:
    if gatingEnabled() && rep.worstGateCaseP95() > 25*time.Millisecond { // gate-exempt cases excluded
        t.Fatalf("worst-case p95 = %v > 25 ms", rep.worstGateCaseP95())
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
