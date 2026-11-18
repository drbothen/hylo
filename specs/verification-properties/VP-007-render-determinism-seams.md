---
document_type: verification-property
level: L4
version: "1.6"
status: draft
producer: architect
timestamp: 2026-11-21T12:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.009.md, behavioral-contracts/ss-05/BC-5.04.003.md, domain-spec/invariants.md]
input-hash: "db3b121"
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
modified: ["1.1 2026-11-18T14:35:00Z: ADV-P4 fix (A2-10) — semantic re-anchor (P4): source_bc moved from BC-1.01.009 to BC-5.04.003, the contract whose VP table cites this VP (TimeFloat value discipline + one-read-per-render); BC-1.01.009 had explicitly dropped the citation (its :149-150 note: determinism, not effect order — ADV-P1-B11), so BC-1.01.009 is removed from bcs: and the VP-INDEX map is reconciled", "1.2 2026-11-18T23:45:00Z: ADV-P5 fix (A2-31) — the NowReads assert is stated against the cumulative counter: capture the count after the first Render and assert the per-render DELTA (exactly 1, IM-14), so a correct implementation reporting 2 after two renders on the same env passes", "1.3 2026-11-19T18:00:00Z: pass-7 fix (A2-10) — the second render runs on a FRESH COPY of the recorded Env: the property claims render determinism, not effect-script idempotence at a fixed clock (legacy's first-run writes — rl_ts, fetch_ts, hist, mix offsets, proc_start, cost history — are effect-order concerns, BC-1.01.009/VP-008); the sketch no longer reuses the mutated env", "1.4 2026-11-20T08:00:00Z: pass-8 fix (A2-11) — the IM-14 clock-count checks now observe a render each: the first render's exactly-once assert reads the recording copy's counter after Render returns, and the replay's counter is read on the SAME fresh copy the second render ran on (the former sketch counted a throwaway FreshCopy that never rendered, subtracting a pre-render baseline — no render could ever be observed); the Method bullet states the per-render norm for both renders", "1.5 2026-11-21T00:00:00Z: pass-9 fix (ADV-P9-A2-16) — the DI-007 corollary now copies the invariant's full scope: the environment seams (git state, process table, clock, env; AD-03) join stdin, transcript, metrics store and own caches", "1.6 2026-11-21T12:00:00Z: pass-12 fix (A2-05) — the 'none is read behind Render's back' clause given an oracle that can fail: a static AST lint leg (TestRender_SeamClosednessLint, go/parser over internal/statusline — Render's intra-module call closure, the same offline mechanism as VP-006's call-site lint and VP-022's leg (c)) asserts no direct time.Now/time.Since/os.Getenv/os.LookupEnv/exec.Command outside the Env seam implementation, with a POL-11 positive-coverage assertion (a planted mutant fixture is flagged exactly; the scanned-function count is fatal-nonzero); the recording fakes remain the runtime observable"]
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
sources are `Env` members; none is read behind `Render`'s back — a clause with an
oracle (A2-05): a static AST lint over `internal/statusline` (Render's intra-module
call closure) asserts no direct `time.Now`/`time.Since`/`os.Getenv`/`os.LookupEnv`/
`exec.Command` call outside the Env seam implementation, planted-mutant-flagged
(POL-11), so the double replay plus the lint can fail on a bypassing read. The repetition is
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
  ran on (IM-14; A2-11); plus the seam-closedness AST lint (skeleton below): no
  direct clock/env/exec read outside the Env seam implementation, planted-mutant
  positive coverage, scanned-function count fatal-nonzero (A2-05).
- **Honesty:** testable-only. The random-sample property asserts replay determinism
  as its own oracle: a randomly recorded `Env` replayed twice (reads shuffle-safe)
  must yield byte-identical output — no live oracle exists or is needed. Runtime
  seam-closedness is asserted by the recording fakes noticing reads; the static leg
  (no direct clock/env/exec read behind the seam) is the AST lint with planted-mutant
  coverage — the mechanism VP-022's leg (c) uses for file opens and ledger names,
  extended to the nondeterminism sources this VP owns.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Property replay | Go test + generator | yes — recording fakes | random Env recordings, double replay |
| Counting seams | Go test | exact | one `Now` read per render |
| Seam-closedness lint (AST) | Go test, go/parser over internal/statusline | yes — intra-module call closure | no direct clock/env/exec read outside the Env seam; planted mutant flagged, scanned-function count fatal-nonzero (A2-05) |

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

func TestRender_SeamClosednessLint(t *testing.T) { // A2-05: the clause gets an oracle.
    // Static AST lint (go/parser) over internal/statusline — Render's intra-module
    // call closure — same mechanism as VP-006's call-site lint and VP-022's leg (c).
    flagged := SeamBypassSites() // direct time.Now / time.Since / os.Getenv /
    // os.LookupEnv / exec.Command outside the Env seam implementation
    if len(flagged) != 0 {
        t.Fatalf("%d seam bypasses: %v", len(flagged), flagged)
    }
    if n := FunctionsScanned(); n == 0 { // POL-11: a mis-pathed scan checks nothing
        t.Fatal("lint scanned zero functions — mis-pathed AST scan passes inert")
    }
    if got := len(SeamBypassSites(plantedMutantFixture())); got != 1 { // POL-11: the
        t.Fatalf("planted bypass mutant flagged %d times, want exactly 1", got) // lint bites
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
