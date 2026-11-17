---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.03.004.md, behavioral-contracts/ss-06/BC-6.03.003.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "0185d9e"
traces_to: prd.md
source_bc: BC-6.03.004
bcs: [BC-6.03.004, BC-6.03.003, BC-1.06.002, BC-3.02.001, BC-3.02.002, BC-1.03.018, BC-1.03.019, BC-1.03.020, BC-2.02.001, BC-2.02.002, BC-2.02.003, BC-2.02.004, BC-2.02.005, BC-2.02.006]
module: internal/parity
proof_method: property-test (testing/quick)
feasibility: feasible
verification_lock: false
proof_file_hash: null

lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — exclusion ids respelled to the BC form (OD-30, OD-76) and closed set extended to ten elements with OD-159/OD-160/OD-161 (A2-02); method recatalogued honestly: mutation generator drives the production harness's fail-closed rejections (A2-09); proof_file_hash field added (A2-29)"]
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
{D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161};
every entry carries one
specific case and its own table test plus an expected-output file; the Go output of an
excluded case must match its own expected file; no glob or wildcard entry exists; and
the harness FAILs with a named reason on any violation (missing table test, mismatched
expected file, glob entry, empty or duplicate case-id, or foreign id). Corpus case-ids
are non-empty and unique. Any id outside the ten-element closed set requires an
owner decision — the machinery cannot admit one silently.

## Source Contract

- **Primary BC:** BC-6.03.004 — Exclusion-list machinery: per-case entries, expected
  files, table tests, no globs.
- **Partial coverage:** BC-6.03.003 (temp-file carve-out from cache comparison only),
  and the exclusion-riding contracts: BC-1.06.002/BC-3.02.001/BC-3.02.002
  (D4-EX-1/OD-76/temp-file), BC-1.03.018/.019/.020 (D4-EX-2), BC-2.02.001..006
  (D4-EX-3).
- **Invariant verified:** DI-012 (no blanket exclusions; every exclusion carries its
  own table tests); OD-105/OD-110; AD-09 (machinery fails closed).

## Property Class and Verification Method

- **Class:** invariant (the closure itself is a proof-obligation over a finite
  structure — the "provably-closable" disposition in ARCH-07).
- **Method:** mutation property test — a generator produces mutated exclusion files
  (drop a table-test reference, respell an id, insert a glob/wildcard case, duplicate a
  case-id, empty a case-id, point at a missing expected file) and each mutant is fed
  through the production harness's own exclusion checker (the same loader/validator
  the Tier A run uses, not a test-local reimplementation), asserting the run FAILs
  closed with the matching named reason; plus the committed file's closure test as the
  happy-path instance (id membership, uniqueness, expected-file existence and match,
  one-test-per-entry, no globs).
- **Honesty:** the strongest close-to-proof property in the harness, but still
  empirical (parsed-structure assertions over mutants), not a theorem-prover artifact.
  The oracle is the finite mutant structure itself: membership in the closed ten-id
  set, case-id non-emptiness and uniqueness, and one-table-test
  correspondence per entry — no live oracle call exists or is needed.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Closure test over the committed file | `go test ./internal/parity -run TestParityExclusions_ClosedSet` | yes — finite parsed structure | every entry, happy path |
| Mutation property test | `go test ./internal/parity -run TestParityExclusions_MutationFailClosed` | yes — finite mutant catalogue | every violation mode driven through the production checker |

## Proof Harness Skeleton

```go
func TestParityExclusions_ClosedSet(t *testing.T) {
    ids := map[string]bool{"D4-EX-1": true, "D4-EX-2": true, "D4-EX-3": true,
        "OD-30": true, "OD-76": true, "temp-file": true, "cp-x03": true,
        "OD-159": true, "OD-160": true, "OD-161": true} // A2-02: BC-spelled ids
    seen := map[string]bool{}
    for _, e := range LoadExclusions("internal/statusline/testdata/parity/exclusions.json") {
        if !ids[e.ID] { t.Fatalf("foreign exclusion id %q", e.ID) }
        if e.Case == "" { t.Fatalf("entry %s: empty case-id", e.ID) }
        if seen[e.Case] { t.Fatalf("duplicate case-id %q", e.Case) }
        seen[e.Case] = true
        if strings.ContainsAny(e.Case, "*?[") { t.Fatal("glob entry — blanket exclusions banned") }
        if !TableTestExists(e.TableTest) { t.Fatalf("entry %s: missing table test", e.ID) }
        if !GoOutputMatchesExpected(e) { t.Fatalf("entry %s: Go output ≠ own expected file", e.ID) }
    }
}

func TestParityExclusions_MutationFailClosed(t *testing.T) { // A2-09
    for _, m := range MutateExclusionsFile(validExclusionsFixture()) {
        // m is a mutated exclusion file; the production checker (not a
        // test-local copy) must reject it with the matching named reason.
        err := ProductionExclusionChecker(m.File) // same path Tier A uses
        if err == nil {
            t.Fatalf("%s: harness accepted a mutant that validates nothing", m.Kind)
        }
        if !matchesNamedReason(m.Kind, err) {
            t.Fatalf("%s: wrong rejection reason %q", m.Kind, err)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestParityExclusions_ClosedSet` and `TestParityExclusions_MutationFailClosed`
(ARCH-07). Riding table tests named by ruling:
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
