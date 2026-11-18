---
document_type: verification-property
level: L4
version: "1.5"
status: draft
producer: architect
timestamp: 2026-11-21T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.009.md, behavioral-contracts/ss-05/BC-5.04.003.md, domain-spec/invariants.md]
input-hash: "bcb7faf"
traces_to: prd.md
source_bc: BC-5.04.003
bcs: [BC-5.04.003]
module: internal/statusline (Render, Env)
proof_method: property-test (testing/quick)
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-18T14:35:00Z: ADV-P4 fix (A2-10) — semantic re-anchor (P4): source_bc moved from BC-1.01.009 to BC-5.04.003, the contract whose VP table cites this VP (TimeFloat value discipline + one-read-per-render); BC-1.01.009 had explicitly dropped the citation (its :149-150 note: determinism, not effect order — ADV-P1-B11), so BC-1.01.009 is removed from bcs: and the VP-INDEX map is reconciled", "1.2 2026-11-18T23:45:00Z: ADV-P5 fix (A2-31) — the NowReads assert is stated against the cumulative counter: capture the count after the first Render and assert the per-render DELTA (exactly 1, IM-14), so a correct implementation reporting 2 after two renders on the same env passes", "1.3 2026-11-19T18:00:00Z: pass-7 fix (A2-10) — the second render runs on a FRESH COPY of the recorded Env: the property claims render determinism, not effect-script idempotence at a fixed clock (legacy's first-run writes — rl_ts, fetch_ts, hist, mix offsets, proc_start, cost history — are effect-order concerns, BC-1.01.009/VP-008); the sketch no longer reuses the mutated env", "1.4 2026-11-20T08:00:00Z: pass-8 fix (A2-11) — the IM-14 clock-count checks now observe a render each: the first render's exactly-once assert reads the recording copy's counter after Render returns, and the replay's counter is read on the SAME fresh copy the second render ran on (the former sketch counted a throwaway FreshCopy that never rendered, subtracting a pre-render baseline — no render could ever be observed); the Method bullet states the per-render norm for both renders", "1.5 2026-11-21T00:00:00Z: pass-9 fix (ADV-P9-A2-16) — the DI-007 corollary now copies the invariant's full scope: the environment seams (git state, process table, clock, env; AD-03) join stdin, transcript, metrics store and own caches"]
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
sources are `Env` members; none is read behind `Render`'s back. The repetition is
defined (A2-10): the second render runs on a FRESH COPY of the recorded `Env` —
the first render's cache writes are invisible to it. The property claims render
determinism, NOT effect-script idempotence at a fixed clock: legacy's first-run
writes (`rl_ts`, `fetch_ts`, `hist`, the mix offsets, `proc_start`, cost history)
happen once and are effect-order concerns (BC-1.01.009, VP-008), and no BC states
that re-running the effect script at a fixed clock is a no-op.

## Source Contract

- **Primary BC:** BC-5.04.003 — TimeFloat: ns→s float, once per render (its VP table
  carries this VP for the value discipline and the one-read-per-render rows; A2-10).
  Determinism is the property; effect ORDER is BC-1.01.009's concern (VP-008), which
  explicitly declines this citation (ADV-P1-B11).
- **Partial coverage:** none (standalone determinism property; the replay generator
  reuses the AD-10 seam recordings).
- **Invariant verified:** IM-14 (one clock read per render); DI-007 corollary (inputs
  are only stdin, the transcript, the metrics store, its own caches, and the
  environment seams — git state, process table, clock, env (AD-03) — structurally,
  via Env; ADV-P9-A2-16); AD-03/AD-10 seam discipline.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** property-based test — a generator produces random `Env` recordings;
  each `Env` is replayed twice, the SECOND replay on a fresh copy of the recording
  (first-render cache writes invisible, A2-10), asserting identical
  output bytes; a counting `Now` asserts EACH render reads the clock exactly once —
  the first render on the recording copy, the replay on the fresh copy it actually
  ran on (IM-14; A2-11).
- **Honesty:** testable-only. The random-sample property asserts replay determinism
  as its own oracle: a randomly recorded `Env` replayed twice (reads shuffle-safe)
  must yield byte-identical output — no live oracle exists or is needed. Seam-
  closedness (no hidden global reads) is asserted by
  the recording fakes noticing reads, not proven; a static lint on `Env` scope is a
  code-review obligation, mirroring VP-022.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Property replay | Go test + generator | yes — recording fakes | random Env recordings, double replay |
| Counting seams | Go test | exact | one `Now` read per render |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestRender_DeterministicUnderSeams(t *testing.T) {
    for _, env := range generatedEnvs(200) {
        e := env.Record()
        a, _ := statusline.Render(stdin, e)
        if first := e.NowReads(); first != 1 { // A2-11: the FIRST render is observed too —
            t.Fatalf("first render read the clock %d times, want 1", first) // exactly one read (IM-14)
        }
        // A2-10: the second render sees a FRESH COPY of the recording — the first
        // render's cache writes are invisible to it (render determinism, not
        // effect-script idempotence; no BC claims the latter).
        replay := e.FreshCopy() // the copy the SECOND render runs on: its NowReads
        b, _ := statusline.Render(stdin, replay) // counter is what the replay observable is
        if !bytes.Equal(a, b) { t.Fatal("nondeterministic render") }
        if d := replay.NowReads(); d != 1 { // A2-11: counted on the copy that rendered,
            t.Fatalf("clock read %d times in the second render", d) // not on a throwaway fresh copy
        }
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
