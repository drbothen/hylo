---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-01/BC-1.03.004.md, domain-spec/invariants.md, prd-supplements/nfr-catalog.md, owner-decisions-log-2026-11-14.md]
input-hash: "7708547"
traces_to: prd.md
source_bc: BC-1.03.004
bcs: [BC-1.03.004, BC-5.03.002]
module: internal/pyfmt (str.go)
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.1"
modified: ["1.2 2026-11-17: ADV-P2 fixes — legacy calls blob[:cut].splitlines() (keepends=False): pieces have no terminators; oracle rebuilt; re-homed to internal/pyfmt/str.go per BC-5.03.002/ARCH-06 (A2-05, D13)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-038: SplitLinesBytes equals CPython bytes.splitlines (keepends=False) — corner-table pinned, fuzz self-oracle

## Property Statement

`SplitLinesBytes` — the byte-level splitter the transcript parser (`_mix_counts`
consumption, BC-1.03.004) feeds each record from, ported in `internal/pyfmt/str.go`
per BC-5.03.002 and ARCH-06 — splits on `\n`, `\r\n` and `\r`
exactly as CPython 3.11 `bytes.splitlines()` does with its default `keepends=False`:
same split points, and the pieces carry **no terminators** (legacy calls
`blob[:cut].splitlines()` at SL:1059 — ends are dropped, so no reconstruction-with-
terminators property exists). Equivalence is pinned by committed oracle-generated
corner tables (OD-142 regime); random sampling asserts the
self-consistency invariants below; end-to-end divergence
hunting on random transcripts rides Tier C (VP-011). The title is deliberate: there
is **no live differential** — the oracle process is not callable from unit tests, so
CPython equivalence rests entirely on the committed corner tables.

## Source Contract

- **Primary BC:** BC-1.03.004 — record splitting + per-line json.loads consumption
  (the BC's VP row marks this property "no VP yet"; minted as VP-038 by this pass).
- **Partial coverage:** BC-5.03.002 — the `SplitLinesBytes` str.go port contract
  (its VP row currently cites VP-025 for the byte-split property; that citation
  belongs here).
- **Invariant verified:** NFR-003 substrate (the splitter is on the protocol input
  path; any split-point drift changes `size`/offset bookkeeping).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** fuzz — `go test -fuzz` over arbitrary byte strings
  (primitives only), plus the committed corner table (lone `\r`, `\r\n` adjacency,
  trailing terminator, empty input, 8-bit bytes with high bits set, `\v`/`\f`/`\x85`
  staying inside pieces — bytes split only on `\n`/`\r`).
- **Honesty (iron law):** testable-only. Because the pieces carry no terminators, the
  fuzz oracle is twofold, and both halves are self-oracles: (a) terminator freedom —
  no piece contains `\r` or `\n`; (b) stripped-losslessness — the concatenation of the
  pieces equals the input with every `\r`/`\n` byte removed (byte accounting: no
  non-terminator byte lost or reordered). Whether `\r\n` counts as one boundary is
  pinned only by the committed corner table, not by the fuzz oracle.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Corner table | Go test, oracle-generated goldens | yes | split-point + `\r\n`-grouping semantics |
| Fuzz | `go test -fuzz` | budget-bounded | terminator freedom + stripped-losslessness |
| Corpus parity | Tier C (VP-011) | corpus-bounded | end-to-end divergence hunt |

## Proof Harness Skeleton

```go
func FuzzSplitLinesBytes(f *testing.F) {
    f.Fuzz(func(t *testing.T, b []byte) {
        pieces := pyfmt.SplitLinesBytes(b)
        var concat []byte
        for _, p := range pieces {
            if bytes.IndexAny(p, "\r\n") >= 0 { t.Fatal("piece embeds a terminator (keepends=False)") }
            concat = append(concat, p...)
        }
        if !bytes.Equal(concat, stripTerminators(b)) { // b minus every \r and \n byte
            t.Fatal("split lost or reordered non-terminator bytes")
        }
        // \r\n-as-one-boundary is NOT derivable here; it is pinned by the corner
        // goldens (internal/pyfmt/testdata), e.g. b"a\r\nb" -> [a b], b"a\r\rb" -> [a "" b].
    })
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table (transcript-parser scope); in-tree fuzz target
`FuzzSplitLinesBytes` + corner goldens under `internal/pyfmt/testdata/`.

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
