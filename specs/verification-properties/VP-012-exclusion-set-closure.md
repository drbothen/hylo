---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.03.004.md, behavioral-contracts/ss-06/BC-6.03.003.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "194b59d"
traces_to: prd.md
source_bc: BC-6.03.004
bcs: [BC-6.03.004, BC-6.03.003, BC-1.06.002, BC-3.02.001, BC-3.02.002, BC-1.03.018, BC-1.03.019, BC-1.03.020, BC-2.02.001, BC-2.02.002, BC-2.02.003, BC-2.02.004, BC-2.02.005, BC-2.02.006]
module: internal/parity
proof_method: proptest
feasibility: feasible
verification_lock: false

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
proof_completed_date: null
---

# VP-012: Exclusion machinery is closed, glob-free, and fails closed

## Property Statement

The parity exclusion list admits only entries whose id is in the closed set
{D4-EX-1, D4-EX-2, D4-EX-3, od30, od76, temp-file, cp-x03}; every entry carries one
specific case and its own table test plus an expected-output file; the Go output of an
excluded case must match its own expected file; no glob or wildcard entry exists; and
the harness FAILs with a named reason on any violation (missing table test, mismatched
expected file, glob entry, or foreign id). Corpus case-ids are unique. A seventh
exclusion class requires an owner decision — the machinery cannot admit one silently.

## Source Contract

- **Primary BC:** BC-6.03.004 — Exclusion-list machinery: per-case entries, expected
  files, table tests, no globs.
- **Partial coverage:** BC-6.03.003 (temp-file carve-out from cache comparison only),
  and the exclusion-riding contracts: BC-1.06.002/BC-3.02.001/BC-3.02.002
  (D4-EX-1/od76/temp-file), BC-1.03.018/.019/.020 (D4-EX-2), BC-2.02.001..006
  (D4-EX-3).
- **Invariant verified:** DI-012 (no blanket exclusions; every exclusion carries its
  own table tests); OD-105/OD-110; AD-09 (machinery fails closed).

## Property Class and Verification Method

- **Class:** invariant (the closure itself is a proof-obligation over a finite
  structure — the "provably-closable" disposition in ARCH-07).
- **Method:** property-based test over the parsed exclusions file plus its table-test
  correspondence: id membership, uniqueness, expected-file existence and match,
  one-test-per-entry, no globs.
- **Honesty:** the strongest close-to-proof property in the harness, but still
  empirical (parsed-structure assertions), not a theorem-prover artifact.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Closure property test | `go test ./internal/parity -run TestParityExclusions_ClosedSet` | yes — finite parsed structure | every entry, every violation mode |

## Proof Harness Skeleton

```go
func TestParityExclusions_ClosedSet(t *testing.T) {
    ids := map[string]bool{"D4-EX-1": true, "D4-EX-2": true, "D4-EX-3": true,
        "od30": true, "od76": true, "temp-file": true, "cp-x03": true}
    seen := map[string]bool{}
    for _, e := range LoadExclusions("internal/statusline/testdata/parity/exclusions.json") {
        if !ids[e.ID] { t.Fatalf("foreign exclusion id %q", e.ID) }
        if seen[e.ID] && e.Case == "" { t.Fatalf("duplicate non-specific id %q", e.ID) }
        seen[e.ID] = true
        if strings.ContainsAny(e.Case, "*?[") { t.Fatal("glob entry — blanket exclusions banned") }
        if !TableTestExists(e.TableTest) { t.Fatalf("entry %s: missing table test", e.ID) }
        if !GoOutputMatchesExpected(e) { t.Fatalf("entry %s: Go output ≠ own expected file", e.ID) }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestParityExclusions_ClosedSet` (ARCH-07). Riding table tests named by ruling:
`TestConfigError_D4EX3_{Number,Boolean,URL,Enum,Theme}`, `TestWindowAge_D4EX1_Windows`,
`TestCacheStore_OD110_TempCleanup`, `TestCacheStore_TempFile_CleanupOnFailedReplace`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Finite, tiny | the parsed exclusions file |
| Proof complexity | Low | structural assertions |
| Tool support | Full | Go tables + reflection over test registry |
| Estimated proof time | Days | test-registry correspondence is the cost |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
