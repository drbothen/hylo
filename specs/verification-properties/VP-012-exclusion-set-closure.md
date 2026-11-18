---
document_type: verification-property
level: L4
version: "1.7"
status: draft
producer: architect
timestamp: 2026-11-18T14:45:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.03.004.md, behavioral-contracts/ss-06/BC-6.03.003.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "dca8232"
traces_to: prd.md
source_bc: BC-6.03.004
bcs: [BC-6.03.004, BC-6.03.003, BC-1.06.002, BC-3.02.001, BC-3.02.002, BC-1.03.018, BC-1.03.019, BC-1.03.020, BC-2.02.001, BC-2.02.002, BC-2.02.003, BC-2.02.004, BC-2.02.005, BC-2.02.006, BC-1.01.001, BC-1.02.004, BC-1.03.015, BC-1.05.004, BC-1.05.006]
module: internal/parity
proof_method: property-test (testing/quick)
feasibility: feasible
verification_lock: false
proof_file_hash: null

lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — exclusion ids respelled to the BC form (OD-30, OD-76) and closed set extended to ten elements with OD-159/OD-160/OD-161 (A2-02); method recatalogued honestly: mutation generator drives the production harness's fail-closed rejections (A2-09); proof_file_hash field added (A2-29)", "1.3 2026-11-18T09:04:00Z: ADV-P3 fixes — riders + named table tests completed for all ten closed-set ids: OD-30 (BC-1.05.006), cp-x03 (BC-1.01.001), OD-159 (BC-1.02.004, the deviation's defining UTF-8-read contract), OD-160 (BC-1.05.004), OD-161 (BC-1.03.015) (A2-17); ClosedSet skeleton asserts a non-zero computed count and logs “N entries validated” (POL-11, A2-06); test-registry correspondence recast as `go test -list` / AST scan — Go has no live reflection over the test registry (A2-24)", "1.4 2026-11-18T02:24:00Z: ADV-P3 sync — rider test names aligned to the rider BCs' own traceability names: OD-30 rider respelled to TestCostHistory_OD30_NumericSidStringKey (BC-1.05.006 Canonical Test Vectors); D4-EX-1 rider attributed to BC-3.02.001 with TestWindowAge_D4EX1_Windows*; OD-76 split from temp-file (BC-3.02.002, TestWindowStart_OD76_*); D4-EX-2 rider spelled TestMixCache_OD32_*", "1.5 2026-11-18T14:45:00Z: ADV-P4 fixes — OD-169: the cost-history record-guard divergence gets its own exclusion id OD-166; closed set becomes ELEVEN ids with scope 'cost-history bytes written after a refresh whose usd or api_ms could not convert to float; nothing else'; closure row added (riding table test TestCostHistory_OD166_RecordGuard, defined in VP-020) and every 'rides D4-EX-2' / 'named deviation under OD-156' wording for this case removed; canonical concrete test names per rider replace family globs (A2-14): TestMixCache_OD32_WrongShapeTables (VP-013), TestCPX03_WriteFailureExit0 (VP-003), TestD4EX3_{Number,Boolean,URL,Enum} per owner design call 13 — no Theme member (theme settings are rejected by the corpus validator)", "1.6 2026-11-18: ADV-P4 pass-4 fix — skeleton LoadExclusions path aligned with the relocated exclusions file internal/parity/testdata/exclusions.json (BC-6.03.004 PC-1, beside the corpus root)", "1.7 2026-11-18T22:00:00Z: pass-4 correction (item 10) — skeleton LoadExclusions path aligned with the OD-148 exclusions file internal/statusline/testdata/parity/exclusions.json, beside the OD-148 corpus root (fixtures stay with the subject package)"]
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
{D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161,
OD-166};
every entry carries one
specific case and its own table test plus an expected-output file; the Go output of an
excluded case must match its own expected file; no glob or wildcard entry exists; and
the harness FAILs with a named reason on any violation (missing table test, mismatched
expected file, glob entry, empty or duplicate case-id, or foreign id). Corpus case-ids
are non-empty and unique. Any id outside the eleven-element closed set requires an
owner decision — the machinery cannot admit one silently. OD-166's scope (OD-169) is
exactly the cost-history bytes written after a refresh whose `usd` or `api_ms` could
not convert to float — hylo's record guard skips the record where legacy persisted the
raw int — and nothing else.

## Source Contract

- **Primary BC:** BC-6.03.004 — Exclusion-list machinery: per-case entries, expected
  files, table tests, no globs.
- **Partial coverage:** BC-6.03.003 (temp-file carve-out from cache comparison only),
  and the exclusion-riding contracts — one named table test per closed-set id:
  BC-3.02.001 (D4-EX-1, `TestWindowAge_D4EX1_Windows*`), BC-1.03.018/.019/.020
  (D4-EX-2, concrete member `TestMixCache_OD32_WrongShapeTables` in VP-013), BC-2.02.001..006 (D4-EX-3,
  `TestD4EX3_{Number,Boolean,URL,Enum}` — no Theme member: theme settings are rejected
  by the corpus validator, owner design call 13),
  BC-3.02.002 (OD-76, `TestWindowStart_OD76_*`), BC-1.06.002 (temp-file, distinct
  case: `TestCacheStore_OD110_TempCleanup`), BC-1.05.006 (OD-30,
  `TestCostHistory_OD30_NumericSidStringKey`), BC-1.01.001 (cp-x03,
  `TestCPX03_WriteFailureExit0`, cf. VP-003), BC-1.02.004 (OD-159 — Go reads files as
  UTF-8 on all OSes; the defining contract for the deviation,
  `TestGitTextReads_OD159_StrictUTF8`), BC-1.05.004 (OD-160 foreign-cache shapes,
  `TestForeignCacheShape_OD160_Vectors`; OD-166 record guard,
  `TestCostHistory_OD166_RecordGuard`, defined in VP-020), BC-1.03.015 (OD-161, `TestTranscriptPath_OD161_IntMeansNoTranscript`).
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
  The oracle is the finite mutant structure itself: membership in the closed eleven-id
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
        "OD-159": true, "OD-160": true, "OD-161": true, "OD-166": true} // A2-02/OD-169: eleven ids
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
    if len(seen) == 0 { // POL-11 (A2-06): an empty/mis-pathed load must not pass green
        t.Fatal("zero exclusion entries loaded — mis-pathed corpus passes nothing")
    }
    t.Logf("%d exclusion entries validated", len(seen))
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
(ARCH-07). Riding table tests named by ruling (one canonical concrete name per
closed-set id, A2-14; names as fixed by the rider BCs and the BC-6.03.004 register —
where a register spells a family abbreviation (`*`), the concrete member is fixed
here or in the defining VP):
`TestWindowAge_D4EX1_Windows*` (BC-3.02.001), `TestMixCache_OD32_WrongShapeTables`
(BC-1.03.018/019/020; defined in VP-013), `TestD4EX3_{Number,Boolean,URL,Enum}`
(BC-2.02.001..006; call-13 canonical set — no Theme member, theme settings are
rejected by the corpus validator), `TestWindowStart_OD76_*` (BC-3.02.002),
`TestCostHistory_OD30_NumericSidStringKey` (BC-1.05.006),
`TestCacheStore_TempFile_CleanupOnFailedReplace` (BC-6.03.003),
`TestCacheStore_OD110_TempCleanup` (BC-1.06.002), `TestCPX03_WriteFailureExit0`
(BC-1.01.001; defined in VP-003), `TestGitTextReads_OD159_StrictUTF8` (BC-1.02.004),
`TestForeignCacheShape_OD160_Vectors` (BC-1.05.004),
`TestCostHistory_OD166_RecordGuard` (BC-1.05.004; defined in VP-020),
`TestTranscriptPath_OD161_IntMeansNoTranscript` (BC-1.03.015).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Finite, tiny | the parsed exclusions file |
| Proof complexity | Low | structural assertions |
| Tool support | Full | Go tables; test-registry correspondence via `go test -list` / AST scan (Go has no live reflection over the test registry, A2-24) |
| Estimated proof time | Days | test-registry correspondence is the cost |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
