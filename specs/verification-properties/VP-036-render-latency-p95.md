---
document_type: verification-property
level: L4
version: "1.8"
status: draft
producer: architect
timestamp: 2026-11-22T02:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-08-build-ci-release.md, behavioral-contracts/ss-06/BC-6.04.002.md, prd-supplements/nfr-catalog.md, owner-decisions-log-2026-11-14.md]
input-hash: "8c5c4a7"
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
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fix — sampling aligned to NFR-001: 20 runs per case, p95 = 19th sorted, binds per case, no pooling (A2-27)", "1.3 2026-11-18T09:20:00Z: ADV-P3 fixes (A2-09) — skeleton drops Go-named arguments (positional call with comments); gate computation excludes the >512 KB oversize fixture, which is timed and reported but exempt from the gate", "1.4 2026-11-18T15:02:00Z: ADV-P4 fix (A2-19) — the >512 KB fixture exemption made conditional per product-brief: the exception applies only when the fixture misses the p95 target; if it meets the budget it is gated like every case", "1.5 2026-11-19T12:00:00Z: pass-6 fixes (OD-187, A2-21: the >512 KB exemption is conditional (fires only on a miss, reported); the gate fails on zero measured cases)", "1.6 2026-11-19T18:00:00Z: pass-7 fix (A2-18/OD-191) — the exempt >512 KB fixture gets a CEILING: exempt from the 25 ms target but the gate fails if its p95 exceeds 100 ms (labeled judgment call: 4x the target, well under the refresh interval), so the leg can no longer never fail; fixture identification by validated case flag timing_exempt: large-transcript (exactly one case, transcript > 512 KB) named beside the exemption", "1.7 2026-11-21T18:30:00Z: pass-12 fixes (A2-11, A2-10 sibling) — Source Contract quotes the current BC-6.04.002 title with the '(large-transcript exemption: 100 ms ceiling)' suffix (BC-INDEX S6.04 row); the oversize-fixture shorthand '>512 KB-line' respelled to the pinned byte threshold (transcript exceeding 524,288 bytes = 512 KiB, however many lines) in statement, flag condition and sketch", "1.8 2026-11-22T02:00:00Z: pass-13 fixes (ADV-P13-A2-02/A2-08, orchestrator call 10) — sampling unit restated to the canonical pass-12 call-4 form: per (case, step), one timed sample = one hylo invocation (one render), cold-start replay from committed seeds with caches and seeds reset before every replay, warm-up included; 'steady-state' removed and 'binds per case' respelled 'binds per (case, step)', no pooling across cases or steps, no summing over steps; large-transcript ceiling breach pinned to p95 > 100.0 ms (exactly 100.0 ms passes, 0.1 ms resolution); the zero-measured-cases failure made UNCONDITIONAL — it runs armed or unarmed, before the arming check (ADV-P13-A2-08)"]
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

Render latency on the owner's Mac (darwin/arm64) over the synthetic
fixture corpus, with metrics HTTP wait excluded per the case model, achieves p95 <=
25 ms (OD-117, labeled judgment call ≈3× over the measured 84.5 ms legacy median).
Sampling discipline is per **(case, step)** (NFR-001): one timed SAMPLE is one
invocation of hylo — one render; a multi-step case is replayed from its committed
seeds 1 warm-up + 20 times and EACH STEP is timed on its own, giving a 20-sample
series per (case, step); caches and seeds are reset to the case's declared state
before every replay, warm-up included — cold-start discipline, so the 20 samples of
a (case, step) series measure one identical workload and no run inherits a
predecessor's warm caches. The samples of each (case, step) series are sorted and
the nearest-rank p95 is the 19th of the 20 sorted samples; the gate **binds per
(case, step)** — every (case, step) p95 must meet the budget, with no pooling across
cases or steps and no summing over steps (a multi-step wall-clock total is never
compared against the per-render target; pooling would hide a slow pair behind fast
ones). One STATED,
CONDITIONAL exception (the brief's speed judgment call, OD-187): the large-transcript
fixture — the one corpus case whose transcript exceeds 524,288 bytes (512 KiB),
however many lines it holds — is exempt from the binding gate ONLY WHEN that fixture
misses the 25 ms
target — if it meets the budget it is gated like every case — and its exemption is
REPORTED in the gate output when it fires. The exempt fixture is NOT unbounded
(OD-191): it is identified by a validated case flag (`timing_exempt:
large-transcript` — exactly one case, and its transcript must exceed 524,288
bytes), and
the gate FAILS if its p95 > 100.0 ms (labeled judgment call: 4x the target,
well under the refresh interval; at the 0.1 ms report resolution a p95 of exactly
100.0 ms passes the ceiling). The exemption is
authored as an exception, not implied by a conditional that could never fire
(ADV-P5-A2-13). Budget failures bind only with `HYLO_TIMING_GATE=1` — the gate arms
on the owner's Mac target; CI legs print the report and pass regardless. ONE failure
is UNCONDITIONAL (ADV-P13-A2-08): the zero-measured-cases check (A2-21) runs armed
or unarmed — a run that measures nothing passes nothing, so a broken corpus load
fails every leg (the sketch runs it before the arming check).

## Source Contract

- **Primary BC:** BC-6.04.002 — Per-OS timing report; p95 <= 25 ms binds on the
  owner's Mac target (large-transcript exemption: 100 ms ceiling).
- **Partial coverage:** NFR-001 (measurement method + baseline provenance 2026-11-15).
- **Invariant verified:** none (performance budget, not a logical property); the
  off-hot-path placement of the metrics fetch is enforced by the BC-6.02.003 case
  model, and the ancestor probe's microsecond cost claim (AD-07) rides this measurement.

## Property Class and Verification Method

- **Class:** performance.
- **Method:** measured property — the per-OS timing report; explicitly not a proof and
  not machine-independent: budget failures bind only where the gate is armed
  (`HYLO_TIMING_GATE=1` on the owner's Mac); the zero-measured-cases totality check
  is unconditional (ADV-P13-A2-08).
- **Honesty:** statistical measurement with named variance sources (loaded machine,
  corpus fixture); the weakest claim class in the index, by design.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Timing report | CI leg + local gate script | per (case, step): cold-start replay from committed seeds — 1 warm-up + 20 timed runs, each step timed on its own; nearest-rank p95 = 19th sorted sample; binds per (case, step), no pooling across cases or steps, no summing over steps | corpus (case, step) pairs |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestTimingReport_PerOS(t *testing.T) {
    // A2-09: positional call — Go has no named arguments. Per (case, step): cold-start
    // replay from committed seeds — caches and seeds reset before every replay, warm-up
    // included — 1 warm-up + 20 timed runs, each step timed on its own; nearest-rank
    // p95 = 19th sorted sample, binds per (case, step), no pooling across cases or
    // steps, no summing over steps.
    rep := MeasureCorpus(1, 20, fakeVMHandling)
    PrintReport(rep) // every leg prints
    if rep.caseCount() == 0 { // A2-21 (P11), ADV-P13-A2-08: runs ARMED OR UNARMED —
        // the totality check precedes the arming check; zero measured cases pass nothing
        t.Fatal("timing gate measured 0 cases — corpus load broken")
    }
    if gatingEnabled() {
        // OD-187/OD-191: the oversize fixture is identified by a validated case
        // flag (timing_exempt: large-transcript — exactly one case, transcript
        // > 524,288 bytes). Its exemption is CONDITIONAL — it fires only when the
        // fixture MISSES the 25 ms target, and its use is reported — and it has
        // a CEILING breached only when p95 > 100.0 ms (judgment call: 4x the
        // target, well under the refresh interval; exactly 100.0 ms passes), so
        // this leg can fail.
        if ov := rep.caseP95(oversizeFixture); ov > 100*time.Millisecond {
            t.Fatalf("oversize fixture p95 = %v > 100 ms ceiling (OD-191)", ov)
        } else if ov > 25*time.Millisecond {
            PrintGateExemption(oversizeFixture, ov) // reported, not silently dropped
        }
        if rep.worstGatePairP95() > 25*time.Millisecond { // every (case, step) p95 binds
            t.Fatalf("worst (case, step) p95 = %v > 25 ms", rep.worstGatePairP95())
        }
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
