---
document_type: verification-property
level: L4
version: "1.22"
status: draft
producer: architect
timestamp: 2026-11-20T12:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.03.004.md, behavioral-contracts/ss-06/BC-6.03.003.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "859167e"
traces_to: prd.md
source_bc: BC-6.03.004
bcs: [BC-6.03.004, BC-6.03.003, BC-1.06.002, BC-3.02.001, BC-3.02.002, BC-1.03.018, BC-1.03.019, BC-1.03.020, BC-1.03.006, BC-1.03.007, BC-1.03.010, BC-1.03.002, BC-1.03.005, BC-1.03.014, BC-1.03.016, BC-2.02.001, BC-2.02.002, BC-2.02.003, BC-2.02.004, BC-2.02.005, BC-2.02.006, BC-1.01.001, BC-1.02.004, BC-1.03.015, BC-1.05.004, BC-1.04.003, BC-1.04.002, BC-1.04.001, BC-1.05.005, BC-1.05.006, BC-1.05.009, BC-1.06.001, BC-1.02.017, BC-1.04.018]
module: internal/parity
proof_method: mutation-test (fail-closed catalogue)
feasibility: feasible
verification_lock: false
proof_file_hash: null

lifecycle_status: active
introduced: "1.0"
modified:
  - "1.1 2026-11-17: ADV-P1 pass-1 fixes"
  - "1.2 2026-11-17: ADV-P2 pass-2 fixes \u2014 exclusion ids respelled to the BC form (OD-30, OD-76) and closed set extended to ten elements with OD-159/OD-160/OD-161 (A2-02); method recatalogued honestly: mutation generator drives the production harness's fail-closed rejections (A2-09); proof_file_hash field added (A2-29)"
  - "1.3 2026-11-18T09:04:00Z: ADV-P3 fixes \u2014 riders + named table tests completed for all ten closed-set ids: OD-30 (BC-1.05.006), cp-x03 (BC-1.01.001), OD-159 (BC-1.02.004, the deviation's defining UTF-8-read contract), OD-160 (BC-1.05.004), OD-161 (BC-1.03.015) (A2-17); ClosedSet skeleton asserts a non-zero computed count and logs \u201CN entries validated\u201D (POL-11, A2-06); test-registry correspondence recast as `go test -list` / AST scan \u2014 Go has no live reflection over the test registry (A2-24)"
  - "1.4 2026-11-18T10:00:00Z: ADV-P3 sync \u2014 rider test names aligned to the rider BCs' own traceability names: OD-30 rider respelled to TestCostHistory_OD30_NumericSidStringKey (BC-1.05.006 Canonical Test Vectors); D4-EX-1 rider attributed to BC-3.02.001 with TestWindowAge_D4EX1_Windows*; OD-76 split from temp-file (BC-3.02.002, TestWindowStart_OD76_*); D4-EX-2 rider spelled TestMixCache_OD32_* (stamp re-dated ascending 2026-11-19, SC-27)"
  - "1.5 2026-11-18T14:45:00Z: ADV-P4 fixes \u2014 OD-169: the cost-history record-guard divergence gets its own exclusion id OD-166; closed set becomes ELEVEN ids with scope 'cost-history bytes written after a refresh whose usd or api_ms could not convert to float; nothing else'; closure row added (riding table test TestCostHistory_OD166_RecordGuard, defined in VP-020) and every 'rides D4-EX-2' / 'named deviation under OD-156' wording for this case removed; canonical concrete test names per rider replace family globs (A2-14): TestMixCache_OD32_WrongShapeTables (VP-013), TestCPX03_WriteFailureExit0 (VP-003), TestD4EX3_{Number,Boolean,URL,Enum} per owner design call 13 \u2014 no Theme member (theme settings are rejected by the corpus validator)"
  - "1.6 2026-11-18: ADV-P4 pass-4 fix \u2014 skeleton LoadExclusions path aligned with the relocated exclusions file internal/parity/testdata/exclusions.json (BC-6.03.004 PC-1, beside the corpus root)"
  - "1.7 2026-11-18T22:00:00Z: pass-4 correction (item 10) \u2014 skeleton LoadExclusions path aligned with the OD-148 exclusions file internal/statusline/testdata/parity/exclusions.json, beside the OD-148 corpus root (fixtures stay with the subject package)"
  - "1.8 2026-11-18T23:45:00Z: ADV-P5 fixes (A2-17, A2-36) \u2014 closure check now rejects glob references in table_test too (only e.Case was covered); OD-76's family abbreviation fixed to the concrete member TestWindowStart_OD76_NativeProbeDiffTable (fixed here per BC-3.02.002's delegation); temp-file spelled as two entries with one concrete test each; frontmatter proof_method relabelled mutation-test (fail-closed catalogue) \u2014 it was never testing/quick (COSMETIC A2-36). OD-30/OD-166 rider names already carry plan call 15's canon (TestCostHistory_OD30_NumericSidStringKey, TestCostHistory_OD166_RecordGuard)"
  - "1.9 2026-11-18T23:45:00Z: ADV-P5 fix (A2-03 rider) \u2014 the D4-EX-3 riding-name set gains the OD-178 Text member: TestD4EX3_{Number,Boolean,URL,Enum,Text}"
  - "1.10 2026-11-19T01:00:00Z: SC-14 reciprocity (sync-check-adv-p5) \u2014 bcs: gains BC-1.04.003 and BC-1.05.005, the two OD-160-carrying contracts whose Verification Properties tables cite this VP's closure check (ADV-P5-C2-17 closure citations); Source Contract Partial-coverage bullet names both rows; no closed-set membership or test-name change"
  - "1.11 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) \u2014 modified history re-ordered chronologically; no behavioral change"
  - "1.12 2026-11-19T03:00:00Z: ADV-P5 residual fix \u2014 the Source Contract partial-coverage bullet's D4-EX-3 rider set respelled from the four-name family to the five canonical names TestD4EX3_{Boolean,Enum,URL,Number,Text} (Text per OD-178, 2026-11-18); body now matches the 1.9 history entry, whose respell had not reached this bullet"
  - "1.13 2026-11-19T12:00:00Z: pass-6 fixes (OD-181, A2-10, A2-22, C06: closed set becomes TWELVE ids with OD-181 (metrics transport beyond plain http) and its closure row; LoadExclusions resolves from the module root; the D4-EX-1 family glob respelled to the concrete member per delegation; history reordered ascending; the D4-EX-2 rider attribution names the CP-O06..O08 vector carriers)"
  - "1.14 2026-11-19T14:00:00Z: pass-6 residual sweep — bcs: gains BC-1.03.006/.007/.010, whose owned CP-O06..O08 vector rows state they ride this closure check (reciprocity preferred over exception-listing, SC-13/SC-14 convention; ADV-P6-C06 reciprocal)"
  - "1.15 2026-11-19T16:00:00Z: sync-check adv-p6 closure (SC-21) — bcs: gains BC-1.06.001, whose PC-1 note states the exclusion entry and its riding table test are validated by this closure check; Source Contract names the row; the dipping 1.4 stamp re-dated ascending (SC-27); no closed-set membership or test-name change"
  - "1.16 2026-11-19T18:00:00Z: pass-7 fixes (A2-02/A2-03/A2-04 + C2-03/C05 reciprocity, orchestrator call 10) — rider attributions copied EXACTLY from the BC-6.03.004 register: OD-159 rider respelled to BC-1.03.001 PC-3 (directional test), OD-160 riders respelled to BC-1.02.017 EC-010 and BC-1.01.008 EC-011 (directional tests; BC-1.05.004 keeps the dedicated test), OD-30 gains BC-1.05.009, temp-file returns to the register's single riding test TestCacheStore_TempFile_CleanupOnFailedReplace (BC-1.06.002's OD-110 test remains that contract's own product test, not a second rider); cp-x03's OD-145 provisional name settled here as TestCPX03_WriteFailureExit0; closure check additionally verifies a rider test exists for EVERY closed id independent of entries (OD-181; TestD4EX3_Text) and guards a non-empty mutant catalogue; bcs: gains BC-1.04.001 (OD-181 rider carrier) and BC-1.04.002 (OD-160-tagged EC-008 citation carrier), map rows reciprocated in VP-INDEX"
  - "1.17 2026-11-19T19:00:00Z: pass-7 residual remediation — OD-159 register-rider citation corrected to its real home BC-1.02.004 TestGitTextReads_OD159_StrictUTF8 in the map row and mutant-catalogue note (the formerly cited BC-1.03.001 PC-3 is the stat-race postcondition and never mentions OD-159; BC-6.03.004 register corrected to match); cp-x03 provisional-note sync recorded as done; no behavioural change"
  - "1.18 2026-11-19T20:00:00Z: sync-check adv-p7 closure (SC-29) — bcs: gains BC-1.02.017, whose Inv 3 names this VP's concrete D4-EX-1 rider test TestWindowAge_D4EX1_Windows_AncestorFound (ADV-P7-B15; reciprocity preferred over exception-listing, SC-13/SC-14 convention); no closed-set membership or test-name change"
  - "1.19 2026-11-20T08:00:00Z: pass-8 fixes (A2-05, A2-06, C03) — OD-160 register riders corrected to BC-1.02.017 EC-004..006 (hand-edited proc_start shapes) and BC-1.01.008 PC3 (cached-branch lone surrogate), in both the Source Contract and the Named Tests note (EC-010 is the CP-O05 overflow; BC-1.01.008 has no EC-011); TestWindowAge_D4EX1_Windows_AncestorFound labelled the D4-EX-1 rider, never an OD-160 rider (1.18 entry label corrected in place); D4-EX-2 attribution gains the hylo-only vector carriers BC-1.03.014 and BC-1.03.016; OD-160 citation carriers gain BC-1.03.002 (EC-008/009) and BC-1.03.005 (PC5); bcs: gains those four contracts"
  - "1.20 2026-11-20T12:00:00Z: pass-9 fix (C2-04) — bcs: gains BC-1.05.009 (second OD-30 register contract beside BC-1.05.006; its body register row and Named Tests entry already named it — the frontmatter map row was the missing reciprocity); VP-INDEX coverage map synced in the same burst by the index owner; the 1.19 entry's lost closing quote restored (call 5 YAML repair)"
  - "1.21 2026-11-18T17:50:00Z: pass-10 fixes (A2-06, A2-10) — scope review stated honestly as a MANUAL obligation: the closure check verifies id membership, uniqueness, test existence and expected-file match, not that each entry's case lies inside its id's declared scope (OD-166 'and nothing else' / OD-181 transport are predicated by the rulings and BC bodies, not by an oracle; no structure mutant can attach a valid id to an out-of-scope case) — property statement and Honesty bullet state it (A2-06); the rider-existence leg additionally asserts RiderRegister()'s keys equal the twelve-element closed set (length + per-id presence — a register missing an id would silently skip that id's check) (A2-10)"
  - "1.22 2026-11-21T09:00:00Z: pass-11 residual — bcs: gains BC-1.04.018 (its VP-table row routes the OD-160 exclusion to this closure check, citation carrier only, no riding test of its own; ADV-P11-C2-02), the Source Contract citation-carriers sentence names it; VP-INDEX map and recount synced in the same burst"
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
OD-166, OD-181};
every entry carries one
specific case and its own table test plus an expected-output file; the Go output of an
excluded case must match its own expected file; no glob or wildcard entry exists; and
the harness FAILs with a named reason on any violation (missing table test, mismatched
expected file, glob entry, empty or duplicate case-id, or foreign id). Corpus case-ids
are non-empty and unique. Any id outside the twelve-element closed set requires an
owner decision — the machinery cannot admit one silently. OD-166's scope (OD-169) is
exactly the cost-history bytes written after a refresh whose `usd` or `api_ms` could
not convert to float — hylo's record guard skips the record where legacy persisted the
raw int — and nothing else. OD-181's scope (2026-11-18) is metrics transport beyond
plain http: non-http(s) redirect targets (hylo serves no sample) and TLS trust-store
differences for https (hylo uses the OS trust store); parity cases use plain http
only, and table tests pin hylo's transport behaviour (BC-1.04.001). Scope
review is the complement of membership and is MANUAL (pass-10 A2-06): the closure
check verifies id membership, case-id uniqueness, test existence and the
expected-file match — not that each entry's case lies inside its id's declared
scope. OD-166's "and nothing else" and OD-181's transport scope are predicated by
the rulings and the BC bodies, not by an oracle; no mutant can attach a valid id to
an out-of-scope case, because scope is a predicate over the case's semantics, not
its parsed structure — a valid id on an out-of-scope case passes the machinery and
is caught only by review against the OD-169/OD-181 declarations. The closure
check is rider-complete (against a register whose keys are asserted equal to the
twelve-element closed set — A2-10: a register missing an id would silently skip
that id's existence check): besides walking the entries, it verifies that EVERY
closed-set id's canonical rider test exists in its declared package — whether or
not any parity case currently carries that id — so deleting
`TestMetricsClient_OD181_TransportTable` (OD-181, whose parity cases are plain
http only) or `TestD4EX3_Text` (D4-EX-3's Go-table-test-only member, which backs
no parity entry) reds the check. The mutation leg guards a NON-EMPTY mutant
catalogue: an empty catalogue fails the leg instead of passing while checking
nothing.

## Source Contract

- **Primary BC:** BC-6.03.004 — Exclusion-list machinery: per-case entries, expected
  files, table tests, no globs.
- **Partial coverage:** BC-6.03.003 (temp-file carve-out from cache comparison only),
  and the exclusion-riding contracts — rider attributions COPIED EXACTLY from the
  BC-6.03.004 register (Preconditions 3; authoritative per orchestrator call 10):
  BC-3.02.001 (D4-EX-1; register family `TestWindowAge_D4EX1_Windows*` — the concrete
  member is fixed here per that contract's delegation:
  `TestWindowAge_D4EX1_Windows_AncestorFound`), BC-1.03.018/.019/.020 (D4-EX-2; 21
  BC-SL-099 rows + BC-SL-100/103 rows; concrete member `TestMixCache_OD32_WrongShapeTables`
  in VP-013, whose CP-O06..O08 vector rows live in BC-1.03.006/.007/.010, and whose
  dedicated hylo-only vector carriers BC-1.03.014 (single-line CP-T06 rows with
  expected all-zero BASE caches `"size"` 70/81) and BC-1.03.016 (row T15) ride the
  same entry — ADV-P8-C03), BC-2.02.001..006
  (D4-EX-3, `TestD4EX3_{Number,Boolean,URL,Enum,Text}` + `config validate`; no Theme
  member — theme settings are rejected by the corpus validator; by the same
  no-legacy-equivalent rule `TestD4EX3_Text` is a GO TABLE TEST ONLY backing no parity
  entry, ADV-P6-D14), BC-1.05.006 and BC-1.05.009 (OD-30,
  `TestCostHistory_OD30_NumericSidStringKey`), BC-3.02.002 (OD-76,
  `TestWindowStart_OD76_NativeProbeDiffTable`), BC-6.03.003 (temp-file,
  `TestCacheStore_TempFile_CleanupOnFailedReplace` — the register's ONE riding test;
  BC-1.06.002's `TestCacheStore_OD110_TempCleanup` remains that contract's own OD-110
  product test and its citation of this check, not a second rider), BC-1.01.001 EC-005
  (cp-x03, dedicated table test; the OD-145 provisional name is settled here, in VP-003
  and BC-1.01.001's VP row as `TestCPX03_WriteFailureExit0` — the register's "name
  provisional" note synced pass-7 residual), the stories owning the file-reading verbs
  (OD-159; register rider: BC-1.02.004 riding table test
  `TestGitTextReads_OD159_StrictUTF8` — the deviation's defining UTF-8-read contract;
  pass-7 residual correction — the formerly cited BC-1.03.001 PC-3 is the stat-race
  postcondition and never mentions OD-159), the
  stories owning the cache-store verbs (OD-160; register riders: BC-1.02.017 EC-004..006
  — the hand-edited `proc_start` shapes NaN / +Infinity / -Infinity — and BC-1.01.008
  PC3, the cached-`branch` lone-surrogate clause; directional tests; dedicated test
  `TestForeignCacheShape_OD160_Vectors`
  in BC-1.05.004), the stories owning the stdin path-field verbs (OD-161; register
  rider: BC-1.03.015 PC-3 directional test, `TestTranscriptPath_OD161_IntMeansNoTranscript`),
  BC-1.05.004 (OD-166, `TestCostHistory_OD166_RecordGuard`, defined in VP-020), and
  BC-1.04.001 (OD-181, dedicated table tests → `TestMetricsClient_OD181_TransportTable`,
  defined in VP-030). Citation carriers (their Verification Properties tables cite this
  closure check; no riding test of their own): BC-1.04.003 and BC-1.05.005 (OD-160-tagged
  foreign-cache/history crash-shape error columns, ADV-P5-C2-17), BC-1.03.002 (OD-160
  foreign-cache shapes on EC-008/EC-009, the float/negative cached `size` paths) and
  BC-1.03.005 (OD-160 foreign cached `ids` shapes, PC5 — ADV-P8-C03 reciprocity, the
  siblings BC-1.03.015/BC-1.06.001 already carried their citations), BC-1.04.002 (OD-160 tag
  on EC-008), and BC-1.06.001 (temp-file-parity carrier; its PC-1 note states the
  exclusion entry and its riding table test are validated by this closure check — SC-21),
  BC-1.04.018 (OD-160 tag on the PC-1 foreign exact-giant-int `lr[0]` mix-cache shape;
  citation carrier only, no riding test of its own — the entry is validated by the
  closure check's existing OD-160 member and the riding test
  `TestForeignCacheShape_OD160_Vectors`; ADV-P11-C2-02, pass-11 residual).
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
  The oracle is the finite mutant structure itself: membership in the closed twelve-id
  set, case-id non-emptiness and uniqueness, and one-table-test
  correspondence per entry plus rider completeness for every closed id (entries or
  none) — no live oracle call exists or is needed. What the machinery does NOT
  encode is per-id scope (pass-10 A2-06): no mutant attaches a valid id to an
  out-of-scope case, and none can — scope is a predicate over the case's semantics,
  not its parsed structure; scope review is therefore a manual obligation against
  the OD-169/OD-181 declarations, stated here rather than claimed.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Closure test over the committed file | `go test ./internal/parity -run TestParityExclusions_ClosedSet` | yes — finite parsed structure | every entry + every closed id's rider test |
| Mutation property test | `go test ./internal/parity -run TestParityExclusions_MutationFailClosed` | yes — finite mutant catalogue | every violation mode driven through the production checker |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestParityExclusions_ClosedSet(t *testing.T) {
    ids := map[string]bool{"D4-EX-1": true, "D4-EX-2": true, "D4-EX-3": true,
        "OD-30": true, "OD-76": true, "temp-file": true, "cp-x03": true,
        "OD-159": true, "OD-160": true, "OD-161": true, "OD-166": true, // A2-02/OD-169
        "OD-181": true} // OD-181: metrics transport beyond plain http — TWELVE ids
    seen := map[string]bool{}
    for _, e := range LoadExclusions(filepath.Join(ModuleRoot(), // A2-10: module-root
        "internal/statusline/testdata/parity/exclusions.json")) { // resolution, as VP-009/VP-010

        if !ids[e.ID] { t.Fatalf("foreign exclusion id %q", e.ID) }
        if e.Case == "" { t.Fatalf("entry %s: empty case-id", e.ID) }
        if seen[e.Case] { t.Fatalf("duplicate case-id %q", e.Case) }
        seen[e.Case] = true
        if strings.ContainsAny(e.Case, "*?[") { t.Fatal("glob entry — blanket exclusions banned") }
        if strings.ContainsAny(e.TableTest, "*?[") { // A2-17: the check covered only
            t.Fatal("glob table-test reference — one concrete name per entry") // e.Case
        }
        if !TableTestExists(e.TableTest) { t.Fatalf("entry %s: missing table test", e.ID) }
        if !GoOutputMatchesExpected(e) { t.Fatalf("entry %s: Go output ≠ own expected file", e.ID) }
    }
    if len(seen) == 0 { // POL-11 (A2-06): an empty/mis-pathed load must not pass green
        t.Fatal("zero exclusion entries loaded — mis-pathed corpus passes nothing")
    }
    // A2-04 (call 10): rider existence for EVERY closed id, independent of the
    // entries — the register's (id → package, table_test) mapping from
    // BC-6.03.004 Preconditions 3. Deleting a riding test reds the check even
    // with zero entries for that id (OD-181's TestMetricsClient_OD181_
    // TransportTable; D4-EX-3's TestD4EX3_Text, which backs no parity entry).
    // pass-10 A2-10: rider EXISTENCE for every closed id presupposes that the
    // register itself covers the closed set — a register missing an id would
    // silently skip that id's existence check. Assert the keys equal the ids.
    if reg := RiderRegister(); len(reg) != len(ids) {
        t.Fatalf("rider register has %d keys, want %d (the closed set)", len(reg), len(ids))
    }
    for id := range ids {
        if _, ok := RiderRegister()[id]; !ok {
            t.Fatalf("rider register missing closed id %s", id)
        }
    }
    for id, rider := range RiderRegister() { // from the BC-6.03.004 register
        if !TableTestExistsIn(rider.Package, rider.Test) {
            t.Fatalf("closed id %s: rider test %s missing from %s", id, rider.Test, rider.Package)
        }
    }
    t.Logf("%d exclusion entries validated, %d rider tests present", len(seen), len(RiderRegister()))
}

func TestParityExclusions_MutationFailClosed(t *testing.T) { // A2-09
    mutants := MutateExclusionsFile(validExclusionsFixture())
    if len(mutants) == 0 { // A2-04: an empty catalogue checks nothing — fail, not pass
        t.Fatal("empty mutant catalogue — mutation leg validates nothing")
    }
    for _, m := range mutants {
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
closed-set id, A2-14; names COPIED from the BC-6.03.004 register — authoritative
per orchestrator call 10 — which spells a family abbreviation (`*`) for D4-EX-1
and delegates a provisional name (OD-145) for cp-x03; the concrete members are
fixed here or in the defining VP):
`TestWindowAge_D4EX1_Windows_AncestorFound` (BC-3.02.001 — the concrete member of
the register's `TestWindowAge_D4EX1_Windows*` family, fixed here per that
contract's delegation; the fake `ProcStarter` returns a start so `⌂` can show,
EC-008; the BC-body glob respelling is owed there), `TestMixCache_OD32_WrongShapeTables`
(BC-1.03.018/019/020; defined in VP-013), `TestD4EX3_{Number,Boolean,URL,Enum,Text}`
(BC-2.02.001..006 + the OD-178 Text class member; the pass-4 no-Theme-member note
stands for theme settings, which the corpus validator rejects),
`TestWindowStart_OD76_NativeProbeDiffTable` (BC-3.02.002 — the concrete member of
the formerly abbreviated family, fixed here per that contract's delegation;
ADV-P5-A2-17),
`TestCostHistory_OD30_NumericSidStringKey` (register contracts BC-1.05.006 and
BC-1.05.009);
temp-file carries the register's ONE riding test, BC-6.03.003's
`TestCacheStore_TempFile_CleanupOnFailedReplace` (BC-1.06.002's
`TestCacheStore_OD110_TempCleanup` remains that contract's own OD-110 product
test and its citation of this check, not a second rider — register copied
exactly, A2-03),
`TestCPX03_WriteFailureExit0`
(BC-1.01.001 EC-005; defined in VP-003 — the OD-145 provisional name settled
here, in VP-003 and the BC's VP row; the register and EC-005 "provisional"
notes synced pass-7 residual), `TestGitTextReads_OD159_StrictUTF8` (BC-1.02.004, the
defining UTF-8-read contract and the register's OD-159 rider — pass-7 residual
correction; the formerly cited BC-1.03.001 PC-3 is the stat-race postcondition
and never mentions OD-159),
`TestForeignCacheShape_OD160_Vectors` (BC-1.05.004, dedicated test; the
register's OD-160 riders are BC-1.02.017 EC-004..006 and BC-1.01.008 PC3's
directional tests — corrected anchors, ADV-P8-A2-05; EC-010 is the CP-O05
overflow and BC-1.01.008 has no EC-011),
`TestCostHistory_OD166_RecordGuard` (BC-1.05.004; defined in VP-020),
`TestTranscriptPath_OD161_IntMeansNoTranscript` (BC-1.03.015),
`TestMetricsClient_OD181_TransportTable` (BC-1.04.001; defined in VP-030 — the plain-http
transport rows of the metrics client: header spellings, empty-`Location` urljoin rule,
visited-cap worst case, and the OD-181 table rows that pin hylo's non-http/https
behaviour).

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
