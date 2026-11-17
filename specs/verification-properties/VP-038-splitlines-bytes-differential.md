---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-01/BC-1.03.004.md, domain-spec/invariants.md, prd-supplements/nfr-catalog.md, owner-decisions-log-2026-11-14.md]
input-hash: "6bd15f4"
traces_to: prd.md
source_bc: BC-1.03.004
bcs: [BC-1.03.004]
module: internal/statusline (transcript*.go)
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.1"
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

# VP-038: SplitLinesBytes equals CPython bytes.splitlines — differential

## Property Statement

`SplitLinesBytes` — the byte-level splitter the transcript parser (`_mix_counts`
consumption, BC-1.03.004) feeds each record from — splits on `\n`, `\r\n` and `\r`
exactly as CPython 3.11 `bytes.splitlines()` does: same split points, ends-retained
pieces, and the losslessness the call site relies on (joining the pieces with their
original terminators reconstructs the input byte-for-byte). Equivalence is pinned by
committed oracle-generated corner tables (OD-142 regime); random sampling asserts the
self-consistency invariants that make divergence visible; end-to-end divergence
hunting on random transcripts rides Tier C (VP-011).

## Source Contract

- **Primary BC:** BC-1.03.004 — record splitting + per-line json.loads consumption
  (the BC's VP row marks this property "no VP yet"; minted as VP-038 by this pass).
- **Partial coverage:** none — VP-006 is the pyfmt JSON depth budget, not this (the
  BC row says so explicitly).
- **Invariant verified:** NFR-003 substrate (the splitter is on the protocol input
  path; any split-point drift changes `size`/offset bookkeeping).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** fuzz differential — `go test -fuzz` over arbitrary byte strings
  (primitives only), plus the committed corner table (lone `\r`, `\r\n` adjacency,
  trailing terminator, empty input, 8-bit bytes with high bits set).
- **Honesty (iron law):** testable-only. The fuzz oracle is twofold: (a) lossless
  reconstruction — `join(pieces, their terminators) == input`; (b) no piece contains
  an embedded terminator — both self-oracles; live CPython fidelity is established
  only by the committed corner table (the oracle process is not callable from unit
  tests).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Corner table | Go test, oracle-generated goldens | yes | split-point semantics |
| Fuzz | `go test -fuzz` | budget-bounded | losslessness + terminator freedom |
| Corpus parity | Tier C (VP-011) | corpus-bounded | end-to-end divergence hunt |

## Proof Harness Skeleton

```go
func FuzzSplitLinesBytes(f *testing.F) {
    f.Fuzz(func(t *testing.T, b []byte) {
        pieces := SplitLinesBytes(b)
        var recon []byte
        for i, p := range pieces {
            term, has := terminatorOf(b, p, i) // the piece's original terminator
            if has { recon = append(recon, p...) ; recon = append(recon, term...) } else { recon = append(recon, p...) }
            if !has && i < len(pieces)-1 { t.Fatal("interior piece lost its terminator") }
            if bytes.ContainsAny(p, "\n\r") { t.Fatal("piece embeds a terminator") }
        }
        if !bytes.Equal(recon, b) { t.Fatal("split is lossy (call site relies on reconstruction)") }
    })
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table (transcript-parser scope); in-tree fuzz target
`FuzzSplitLinesBytes` + corner goldens under `internal/statusline/testdata/`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Infinite (fuzz) + corner table | |
| Proof complexity | Low | pure byte function |
| Tool support | Full | stdlib fuzzing |
| Estimated proof time | Hours | corner authoring dominates |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-17 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
