---
document_type: adversarial-review
phase: 1d
pass: 14
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CLEAN
novelty: MEDIUM
findings: 65
---

# Adversarial Spec Review — Phase 1d, Pass 14

Pass 14 ran as six fresh-context perimeters, the same split as passes 1-13. Each section is the verbatim final report of one perimeter, unedited except for this framing. NOT_CLEAN under OD-195 (65 findings: HIGH 3 / MEDIUM 25 / LOW 33 / COSMETIC 4; pass 13 had 72 with 11 HIGH). The orchestrator confirmed A2-01 on disk (`.factory/` is git-ignored on main, so a Go test cannot read BC-6.03.004), checked A2-02 against legacy SL:610-615 (cold start: grey below $1, yellow from $25, else white; `$/h` grey), and measured on CPython 3.11.7: `math.isnan(10**400)` raises OverflowError, `min(10**400, 100.0)` is 100.0, `int('1_0')` is 10, and `9007199254740995 >= 9007199254740996.0` is False while the float64 conversion gives True (C2-07's own example does not show the gap; this one does).

## Perimeter A (PRD, supplements, architecture, CI)

Findings: 14 (high 1, medium 7, low 5, cosmetic 1).

## ADV-P14 Perimeter A: PRD, supplements, architecture, CI

### 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P14-A01 | HIGH | Interface cannot express a BC; P20 config over code | specs/architecture/ARCH-03-statusline.md:401, :378-384, :392-393 | `RecordCost(history, sess, now)` takes no config, and `CostConfig` has no field for `statusline.cost.record_throttle_s`. The throttle rule the doc comment describes (`now - ts < record_throttle_s`) therefore cannot get its value through the declared pure API. BC-1.05.004 makes it config (Precondition 2, BC-1.05.004.md:63; registry row at interface-definitions.md:295). An implementer copying the signature has to hard-code 60 or add a hidden global. | architect |
| ADV-P14-A02 | MEDIUM | Interface type loses parity exactness (P13) | ARCH-03-statusline.md:413 | `CostThresholds` returns `usdPair *[2]float64`. Under BC-1.05.005 PC3/PC4 (BC-1.05.005.md:90, :95-99) the dollar list holds the raw history `usd`, and that value can be an exact int: hylo's own writer keeps ints as ints (BC-1.05.009 PC-3, ARCH-06-pyfmt.md:155). Python compares int thresholds exactly (BC-5.01.007; `NumCmp`, ARCH-06:170). float64 rounds ints above 2^53, so the `$` colour can flip. The return type should be `pyfmt.Num`/`Value`. | architect |
| ADV-P14-A03 | MEDIUM | CI census contradicts a BC (P11) | ARCH-08-build-ci-release.md:248-252; cicd-setup.md:81 vs BC-6.03.001.md:163-168, :150-155 | The Tier B census on the Windows leg counts only `*.windows.golden`. BC-6.03.001 PC-8 compares Windows against the `.windows.golden` when one exists and otherwise against the default golden (A/B/C have no Windows variant). So the Windows leg's "goldens compared" count can never equal the windows-only file census: the job is either always red, or it drops the fallback goldens from the census. PC-6 also mentions "macOS variants" that no census or naming rule defines. | architect |
| ADV-P14-A04 | MEDIUM | Positive-coverage granularity weaker than the gate unit (P11; partial-fix sibling) | cicd-setup.md:80, :87; ARCH-08:225, :302 | The Tier A census counts cases (`N cases compared`) and the timing census counts cases (`timing: N cases timed`). But comparison is per step (BC-6.03.002) and timing gates per (case, step) (BC-6.04.002.md:75-79; VP-036 uses "(case, step) pairs"). A harness that compares or times only the first step of each multi-step case would still pass both censuses. The pass-12/13 per-(case, step) unit change did not reach the census lines. | architect |
| ADV-P14-A05 | MEDIUM | Contradiction: required-check list vs activation rule (P19) | cicd-setup.md:327-336 (line 334), :52; ARCH-08:55, :344-347 vs ARCH-08:34-41 | The branch-protection list requires `govulncheck (required)` unconditionally now. ARCH-08's ORDERING rule says govulncheck becomes required only in the same change that adds go.mod's `toolchain` line, and never on the no-patch 1.26.0 toolchain, which is the current state (ARCH-08:24-26). Applying the list as written does exactly what the rule forbids. | architect |
| ADV-P14-A06 | MEDIUM | NFR target omits catalogued degrade triggers (pending intent verification) | prd.md:500, :518; nfr-catalog.md:25; error-taxonomy.md:57, :276-277, :303-324 | The NFR-002 target and the E-REN-002 carrier derivation list only the X/S/T/N/O/A families. All 32 CP-C rows declare a "typed 29-byte degrade, Go table test" outcome, and NFR-002's requirement text names "cache faults". So no never-blank target binds CP-C01..C32, and their owner BCs (e.g. BC-1.04.002/.006/.009/.011/.012) are not carriers. CP-O06..O09 are also missing from the NFR-002 list. | product-owner |
| ADV-P14-A07 | MEDIUM | Partial-fix sibling: self-contradictory requirement | nfr-catalog.md:24 vs prd.md:499, :30 | The NFR-001 requirement cell still says "Steady-state render latency", while the same cell's sampling rule is cold-start (caches reset before every replay). The PRD title was respelled to "cold-start" in 0.2.25, but this sibling cell was not updated. A performance-test writer could build warm-cache sampling from it. | product-owner |
| ADV-P14-A08 | MEDIUM | Positive-coverage count not derived from the tool's inputs (P11) | cicd-setup.md:84; ARCH-08:260-265 | The govulncheck job's only coverage line is `go: K files scanned`, a repo file count. Nothing in it comes from what govulncheck actually analyzed, so a narrowed package pattern still prints a healthy K. The paired `go test: N tests run` rule applies to test jobs only, and the lint and govulncheck jobs have run no tests since the pass-13 split. | architect |
| ADV-P14-A09 | LOW | Count propagation after the R-009 mint | prd.md:677; assumptions-register.md:22; ARCH-INDEX.md:44; risk-register.md:16-20, :43-46 | All four still say "R-001..R-008". The risk-register gate note maps NFRs for R-001..R-008 but says nothing about R-009, which links to NFR-003 (a parity NFR) for a security risk. | product-owner / architect |
| ADV-P14-A10 | LOW | Incomplete exit-1 cites | interface-definitions.md:64; ARCH-01-binary-cli.md:101, :133 vs prd.md:526, error-taxonomy.md:65, BC-2.03.002.md:153 | These cite EC-008/010/011 only. EC-012 (a relative `HYLO_PATHS_CACHE_DIR` makes `config path` exit 1) is missing. | architect / product-owner |
| ADV-P14-A11 | LOW | Mis-anchored line pointer (P4) | ARCH-00-overview.md:21 | Cites the seam set as "prd.md:70". Line 70 is the §1.1 heading; the AD-10 seam text is at prd.md:77. | architect |
| ADV-P14-A12 | LOW | Timeout formula misses a term (P11 item 5) | ARCH-08:193; cicd-setup.md:57 | The timing timeout counts 21 hylo runs per (case, step). BC-6.04.002 PC-2 (BC-6.04.002.md:103) also measures the CPython oracle median "the same way", which is about four times slower per run. Only a vague "oracle-spawn overhead" term covers it. `N_cases × S_steps` is also undefined when step counts differ per case. | architect |
| ADV-P14-A13 | LOW | Literal command contradicts its own cell | cicd-setup.md:59 | The coverage job's literal `go test -count=1 -coverpkg=./internal/... -coverprofile=cover.out ./internal/...` omits `-skip $ORACLE_TESTS`, which the prose in the same cell requires. Copied as-is, it trips BC-6.01.001's fail-closed interpreter rule. | architect |
| ADV-P14-A14 | COSMETIC | Severity model drift | prd.md:528-534 vs error-taxonomy.md:60-65 | The PRD defines `broken` as E-REN-001/002 only. The taxonomy also rates E-CLI-002, E-VAL-001, E-HAR-001 and E-CLI-003 as broken. | product-owner |

### 2. Policy compliance
- P1 append_only_numbering: PASS (CP-T08 retired and not reused; R-009 appended).
- P2 lift_invariants_to_bcs: PASS within this perimeter.
- P4 semantic_anchoring_integrity: FINDING A11.
- P5 creators_justify_anchors: PASS.
- P6 subsystem names: PASS (PRD §1.6 and module-criticality match the ARCH-INDEX registry).
- P7 BC H1 is the title source: PASS (about 90 H1s across ss-01..06 spot-checked against PRD §2 rows, no drift).
- P9 VP-INDEX source of truth: PASS. 41 VPs; classes 33/7/1; methods 20/13/3/2/1/1/1; the ARCH-INDEX home map and module-criticality counts recomputed and they match.
- P11 ci_positive_coverage_assertion: FINDINGS A03, A04, A08, A12, A13.
- P12 settled_decisions_are_constraints: PASS.
- P13 parity_before_behavior_change: FINDING A02.
- P14 public_repo_hygiene: PASS (only RFC 5737 addresses seen).
- P16 thresholds_are_explained: PASS (A12 is a timeout-derivation gap, not an unexplained threshold).
- P17 ledger_format_frozen: PASS.
- P18 cross_platform: PASS.
- P19 go_hardening_toolchain: FINDING A05 (A08 related).
- P20 config_over_code: FINDING A01.
- P21 public_artifact_hygiene: PASS.

### 3. Files not fully read
All perimeter files were read in full. For cross-reference checks I also opened parts of BC-1.05.005, BC-1.05.004, BC-2.03.002, BC-2.01.001, BC-6.04.002 and BC-6.03.001, plus VP-INDEX.

### 4. Verdict
Novelty: MEDIUM. A01, A02, A03, A04 and A05 are new defects in interfaces and CI. A06 and A07 are propagation gaps left by the pass-12/13 changes.

**NOT_CLEAN**: 1 HIGH and 7 MEDIUM findings.

## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 11 (high 1, medium 2, low 6, cosmetic 2).

## 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P14-A2-01 | HIGH | Oracle that cannot be built; positive coverage is illusory (P11) | VP-012-exclusion-set-closure.md:87-100, 181-182, 188-190, 243-263 | VP-012 says the test parses the per-id (package, test) rider pairs from BC-6.03.004 Preconditions 3. That cannot work, for two reasons. (a) The BC file lives on the factory-artifacts orphan branch, and `.factory/` is git-ignored on main (`.gitignore:29-30`), so a Go test on main or in CI has nothing to parse. (b) The register table (BC-6.03.004:97-110) has no package column. D4-EX-1 is given only as a glob family, which VP-012 itself bans. The OD-30, OD-76, OD-160, OD-161, OD-166, OD-181 and D4-EX-2 rows name no concrete test. So the parsed rider sets come out empty or glob-valued, the leg cannot go red, and the promise that "deleting `TestMetricsClient_OD181_TransportTable` reds the check" (:97-100) is false. Either commit a machine-readable register inside the code tree, or drop the parse claim. | architect |
| ADV-P14-A2-02 | MEDIUM | VP statement contradicts BC and legacy | VP-021-cost-colour-goldens.md:55-56 | The cold-start case is pinned as "no threshold, no colour". BC-1.05.001:73 and legacy SL:614-615 say the `$` amount still gets colour at cold start: yellow if usd >= cold_yellow_usd (25), else white. The `$/h` segment is grey (SL:624). A table leg written from VP-021 would fail a correct port. | architect |
| ADV-P14-A2-03 | MEDIUM | Wrong module anchor (P4); partial-fix sibling | VP-020:14, :100 (Proof Method "Go test, temp dirs"), :111-113; VP-018:14; VP-INDEX.md:99, :101 | VP-020 places the file-I/O property (poisoned-file load, regenerated file) in `internal/cost`, and VP-018 lists `internal/cost` for atomic cache writes. Pass 13 ruled `internal/cost` pure core with no I/O, and `internal/statusline` loads and saves cost history through its `CacheStore` (ARCH-00:88, ARCH-03:343, architecture-feasibility-report:82). Following these VPs, an implementer would put file I/O and temp-dir tests in the pure package. | architect |
| ADV-P14-A2-04 | LOW | Contradiction inside one document | VP-004-closed-exit-code-surface.md:88-89 | The "Invariant verified" line still says non-zero exits happen only in validate, usage and harness contexts. The same file's statement (:46-49) and prd.md:511 add E-CLI-003 (`config path` exit 1). The line was missed by the pass-13 residual. | architect |
| ADV-P14-A2-05 | LOW | Partial fix not propagated | VP-016-config-error-classes-line.md:104-105, :121 | The Method bullet and the Proof Method row still use the tautological "stdout is the config-error line or not" wording. Pass-12 A2-17 removed it from the statement and the sketch. | architect |
| ADV-P14-A2-06 | LOW | Ambiguous oracle wording; sibling of a pass-12 fix | VP-029-transcript-parse-tables.md:62-63 | The delete-the-line oracle is hylo's own parser (:67-68), but the size rule reads "hylo's `size` equals legacy's plus …". VP-013:60-61 was respelled to "the deletion oracle's" in pass-12 A2-16; VP-029 was not. | architect |
| ADV-P14-A2-07 | LOW | Stale enforcer counts (P2) | domain-spec/invariants.md:46 (and the :31, :35 cells) | The file claims DI-008 = 90 and DI-012 = 79 citing BCs. Re-grepping with its own stated method over `ss-0*/` finds 92 files citing DI-008 and 83 citing DI-012. DI-007 = 38 still holds. | business-analyst |
| ADV-P14-A2-08 | LOW | Derived prose lags the catalog (P9) | VP-INDEX.md:41; VP-INDEX.md:341-366 | The 1.27 entry says the VP-014 → BC-1.02.017 reciprocal row is still owed. BC-1.02.017 already delivers it (its :31 v1.3.8 history entry and :160). The "Uncovered BCs" prose stops at the pass-12 count of 289 edges and never records the pass-13 count of 297. | architect |
| ADV-P14-A2-09 | LOW | Assessment pin no longer holds | architecture-feasibility-report.md:13, :19, :22 | The report pins `prd_version` 0.2.22 and OD-115..OD-194 as settled. prd.md:4 is now 0.2.25, and OD-195 exists. | architect |
| ADV-P14-A2-10 | COSMETIC | Sketch contradicts statement | VP-034-oracle-isolation.md:150-151 | The Go-allowlist sketch comment says "the case wins". The statement (:60-63, pass-11 residual) says the case value is used on both sides. | architect |
| ADV-P14-A2-11 | COSMETIC | Sketch incomplete | VP-014-d4ex1-windows-window-age.md:101-109; VP-001:160-162 | The VP-014 sketch checks only the upper bound on probes. The zero-probe cache-first row and the `.0` pin that the statement requires have no sketch leg. VP-001's Proof Method table leaves out `FuzzDegradedLadder`. | architect |

## 2. Policy compliance

- P1 append_only_numbering: PASS
- P2 lift_invariants_to_bcs: PASS on coverage (every DI is either enforced or explicitly deferred under OD-115); counts are stale, see A2-07
- P4 semantic_anchoring_integrity: FINDING A2-03
- P5 creators_justify_anchors: PASS
- P6 subsystem names: PASS (VP module names match the ARCH package table)
- P9 vp_index_is_vp_catalog_source_of_truth: FINDING A2-08. Catalog cells, totals and the `bcs:` map were checked against all 41 frontmatters and are consistent.
- P11 ci_positive_coverage_assertion: FINDING A2-01
- P12 settled_decisions_are_constraints: PASS
- P13 parity_before_behavior_change: PASS
- P14 public_repo_hygiene: PASS
- P16 thresholds_are_explained: PASS
- P17 ledger_format_frozen: PASS
- P18 cross_platform_from_day_one: PASS
- P19 go_hardening_toolchain: PASS
- P20 config_over_code: PASS
- P21 public_artifact_hygiene: PASS (nothing flagged is quoted here)

## 3. Files not fully read

All files in the perimeter were read in body. For VP-005 through VP-041, the first 20-30 frontmatter lines were skipped in the Read, and their `bcs:`, `module` and `source_bc` values were checked by grep instead. VP-012 lines 1-19 were skipped; its `bcs:` line is long and was not inspected directly.

## 4. Novelty

Novelty: MEDIUM. A2-01 is a new class: an oracle that depends on an artifact which never exists in the code tree. A2-02 and A2-03 are new semantic defects. The rest are propagation residue.

**NOT_CLEAN** (1 HIGH, 2 MEDIUM).

## Perimeter B (BC-1.01, BC-1.02)

Findings: 9 (high 0, medium 1, low 7, cosmetic 1).

## ADV-P14 Perimeter B (BC-1.01.\*, BC-1.02.\*): Pass 14 findings

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P14-B01 | MEDIUM | Semantic anchoring / VP reciprocity (P4/P5) | BC-1.01.008 VP table (only VP-005) and PC3; BC-1.02.017 VP table and VP Anchors (VP-028, VP-001, VP-014 only); VP-012:13 `bcs:` and VP-012:135-138 | VP-012 names two OD-160 "register riders" with directional tests: BC-1.02.017 EC-004..006 and BC-1.01.008 PC3 (the cached-`branch` lone surrogate). The links only go one way. BC-1.01.008 is missing from VP-012 `bcs:` and does not cite VP-012. BC-1.02.017 is in VP-012 `bcs:` (pass-7 SC-29, "reciprocity preferred"), but its own VP table has no VP-012 row. The sibling carriers BC-1.01.001 (`cp-x03`) and BC-1.02.004 (OD-159) both have explicit VP-012 rows. Effect: a story built from BC-1.01.008 would not learn that it owes the VP-012 rider test, and the closure check would fail. | product-owner (BC rows); architect (VP-012 `bcs:`) |
| ADV-P14-B02 | LOW | Anchor completeness (pending intent verification) | VP-001:37, 82-99 (Source Contract); BC-1.02.001 EC-007, BC-1.02.003 EC-006, BC-1.02.006 EC-008, BC-1.02.008 EC-006, BC-1.02.010 EC-009, BC-1.02.014 EC-010, BC-1.02.030 PC4 | VP-001 has fault rows cps01..cps17 (VP-001:284). Its partial-coverage list names the CP-S06/07/11/12/13 owners (BC-1.02.020/026/027), and those BCs cite VP-001. The owners of CP-S02..S05, S08, S09 and S10 (error-taxonomy:343-352) are not listed, and their CP-S EC rows do not cite VP-001. BC-1.02.006 and BC-1.02.014 cite VP-001 only for their CP-O rows. The pass-10 B03 sweep covered CP-O only, and pass-11 B01 minted the CP-S owner rows afterwards without adding VP-001. No effect on what gets built, because VP-001 already enumerates the cps rows. | product-owner; architect |
| ADV-P14-B03 | LOW | Unreachable degrade site | BC-1.01.009 PC1 step 6 row ("foreign-cache CP-C01 only (non-dict cache at SL:273-275)"); error-taxonomy:293 | `effective_rl` always runs at step 3. On any non-object session cache it faults first: item assignment raises TypeError at SL:307, and `.get` raises AttributeError at SL:311. Step 4 also faults at SL:324. So CP-C01 can never raise at step 6 (SL:274). The taxonomy row's "the consult yields None" never happens either, because no JSON non-object has `.get`. Out of parity scope (OD-160), but the per-step attribution is wrong. | product-owner; architect (taxonomy row) |
| ADV-P14-B04 | LOW | Missing edge case | BC-1.02.013 PC1 ("missing/corrupt → `{}`") and its EC table | A session cache that parses as a JSON non-object (e.g. `[]`) is neither missing nor corrupt. Legacy faults at SL:307 (stdin `rl` present) or SL:311 (absent). This is CP-C01, OD-160. The contract that owns `effective_rl` does not list it. The sibling BC-1.02.005 EC-010 does list the analogous array-cache case (CP-C08). | product-owner |
| ADV-P14-B05 | LOW | Ambiguous vector setup | BC-1.02.029 CP-O12 seed (`"transcript_path":"<T>"` and `"workspace":{"project_dir":"<T>"}`) | One placeholder `<T>` names both the transcript, which must be a regular file (SL:1010 `os.path.isfile`), and the project directory. BC-1.02.004 uses `<T>` for a temp-root directory. If `<T>` is read as a directory, `_mix_counts` returns None, `tot` is never formed, and the vector does not degrade. | product-owner |
| ADV-P14-B06 | LOW | D15 named-constant declaration gap [process-gap] | BC-1.02.011 PC5 (two-space window joiner, SL:532); BC-1.02.007 PC3 and BC-1.02.018 PC2.3 (single-space joins, SL:1174, SL:596) | Passes 8 and 11 declared intra-segment markup as named format constants one finding at a time (`->`, `·`, `/`, brackets, `?`, ` <1%`). The visible inter-window joiner `"  "` (and the sibling space joins) carry no constant-or-config declaration. These were pinned one at a time, never swept. | product-owner |
| ADV-P14-B07 | LOW | Wording gap vs. a sibling contract | BC-1.01.001 PC3 | "Cache writes performed by steps that completed before the fault persist" does not cover within-step writes. The history-borne CP-O10/O11 raise and the CP-C10 `cost_thresholds` raise both happen inside step 7c, after that step's own `record_cost` write. BC-1.01.001 PC3 lists those as guarded sites; only BC-1.01.009 PC2 states that the write persists. | product-owner |
| ADV-P14-B08 | LOW | Stale anchor label | interface-definitions:331 (Contract column of the `statusline.glyphs.*` family row) | The member text credits `cache_hit` to BC-1.02.008 and BC-1.02.023, but the Contract column lists `.023` and omits `.008`. BC-1.02.008's Config-keys row does name the key. | architect |
| ADV-P14-B09 | COSMETIC | Stale count | BC-1.02.004 VP-028 row ("the 10-layout table") | The contract's own vector table now has 14 rows (rows 11-14 added in passes 9 and 11). | product-owner |

All other postconditions and vectors in the perimeter checked out against the legacy lines. Re-derived independently and matching:
- the 29/45/64-byte frames;
- all trim staircases from the segment widths;
- all ten heat channels plus `heat(0/true/50.4/51/84.5/100)`;
- the half-even cases (12.5, 62.5, 99.5, 1.5, 2.5, 999.5);
- the countdown floor-divisions, including the 1.15·length products, which round exactly to 695520/20700;
- the 0.9·length band boundary;
- `_hm`/window-age big-integer values (`1e24` → `277777777777777766h24m`, `5e23` → `…883h12m`);
- `win_start=true` → `20770d19h`;
- the BC-1.02.030 sequence;
- the CP-O12 overflow mechanics.

### 2. Policy compliance

- **P1** append_only_numbering: PASS
- **P2** lift_invariants_to_bcs: PASS (DI-007/008/012 cited where enforced)
- **P4** semantic_anchoring_integrity: FINDING B01, B02, B08
- **P5** creators_justify_anchors: FINDING B01
- **P6** subsystem name: PASS (all 40 are `SS-01`)
- **P7** H1 = BC-INDEX = PRD: PASS (all 40 titles identical; confidence column matches frontmatter)
- **P12** settled_decisions_are_constraints: PASS
- **P13** parity_before_behavior_change: PASS
- **P14** public_repo_hygiene: PASS (no IPs, home paths, hostnames or emails in the 40 files)
- **P16** thresholds_are_explained: PASS
- **P17** ledger_format_frozen: N.A. (no ledger surface in this perimeter)
- **P18** cross_platform_from_day_one: PASS (ntpath/posixpath split, Windows surrogate leg EC-014, OD-159/183/190)
- **P19** go_hardening_toolchain: N.A.
- **P20** config_over_code: FINDING B06 (LOW); no DGX\_\* aliases (legacy names appear only as provenance)
- **P21** public_artifact_hygiene: PASS

### 3. Coverage gaps and unverified Python claims

**Not fully read:**
- the frontmatter `modified:` history blocks (lines 1-~25) of most BCs;
- VP files beyond their `bcs:` lines and the excerpts cited;
- prd.md beyond the BC tables;
- invariants.md and capabilities.md beyond the CAP rows;
- test-vectors.md;
- error-taxonomy beyond the CP-S, CP-C and CP-A rows.

**Python claims I could not check by hand** (no interpreter and no ntpath source available):
- **ntpath results** in BC-1.02.022 PC4. My reading of the 3.11 pure-Python `splitdrive`/`normpath` would give `normpath('//')` = `\`, not `\\`. The BC says these were oracle-verified and that the Windows CI leg regenerates them, so I did not raise a finding.
- **SHA-1 git cache keys** in the BC-1.02.005 vectors.
- **Golden byte totals:** 286/642/701/743/809.
- **Chunk-boundary measurements:** the BC-1.02.004 8191/8192 probes.
- **JSON depth:** the 993/994 depth budget.

### 4. Verdict

**Novelty: LOW.** B01 and B03 are new; the rest are refinements and propagation leftovers.

**NOT_CLEAN** (one MEDIUM: B01).

## Perimeter C (BC-1.03, BC-1.06, BC-1.07)

Findings: 5 (high 0, medium 2, low 3, cosmetic 0).

## ADV-P14 Perimeter C: BC-1.03.* (21), BC-1.06.* (2), BC-1.07.* (8)

**Result: NOT_CLEAN.** There are two MEDIUM findings, both in the transcript BCs. The cache (1.06) and subagent (1.07) BCs have only one LOW between them.

I recomputed every canonical vector byte count by hand from the stated templates and found no discrepancy. That covers BC-1.03.002, 003, 004, 005, 006, 007, 008, 009, 010 (CP-O08, the three non-raising closers, NaN-id), 011, 012, 014, 016 (T1, T13, T16), 017, 019 (all 21 rows plus BASE), 020 (C1–C3) and 021. I re-derived the turn-machine rows T1–T20, the rebuild five-call vector and the subagent wire strings (ensure_ascii escapes, joiner, glyphs, `_fmt_tokens` thresholds) from legacy SL:845-936 and SL:988-1154; all match. Titles, subsystem, parity_class and confidence agree across the BC files, BC-INDEX and the PRD. Every cited VP lists the BC back in its `bcs:` field, and every config-key range matches the interface-definitions.md registry (rows 254-260 and 271-285).

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P14-C01 | MEDIUM | Internal contradiction (test-misleading) | BC-1.03.005.md:98 (EC-008) vs :114 (CP-O09 parse-leg CTV); legacy SL:1108, SL:1150-1153, SL:203 | EC-008 says two counted 4,300-digit `input_tokens` give a "4,301-digit accumulator" and **no cache write**. The same BC's CTV, tagged as co-owner of that edge case, uses two 4,300-digit operands (10^4299 each), gets a 4,300-digit sum, and says the cache **is written**. A sum of two 4,300-digit ints exceeds the limit only when it reaches 10^4300 (e.g. 5·10^4299 each, as in BC-1.03.006's CTV). A test written from EC-008 alone, using operands like the CTV's, would assert the wrong outcome. Fix: EC-008 should state the operand bound (sum ≥ 10^4300) or point to BC-1.03.006's save-failure vector. | product-owner |
| ADV-P14-C02 | MEDIUM | Partial-fix regression (sibling not updated after ADV-P10-C01) | BC-1.03.018.md:103 (PC3 CP-O07 row) vs BC-1.03.007.md:78 (EC-007), :98-100; legacy SL:1104-1119 | BC-1.03.018 still calls "float `pp` from an earlier counted line meets a huge int `_w`" the **canonical** CP-O07 leg, with SL:1108 "overflow-free when `tin` is an int". BC-1.03.007 (v1.2.6) ruled the mirror leg canonical. It also found that no transcript or writer can pair an int `tin` with a float `pp`: a float prompt adds a float to `tin` on the same line (SL:1108), and float + int stays float. That leg (b) is therefore a hand-edited foreign-cache state, registered under OD-160, not D4-EX-2. Read alone, BC-1.03.018 sends an implementer to an unreachable seed as the canonical trigger and files it under the wrong exclusion id. Its own PC5 also says every predicate-triggering input is a D4-EX-2 entry. BC-1.03.018's history ends at pass 9 (line 36), so the pass-10 ruling never reached it. | product-owner |
| ADV-P14-C03 | LOW | Same imprecision as C01 | BC-1.03.006.md:99 (EC-009) | "Accumulator crosses 4,301 decimal digits (two counted 4,300-digit `input_tokens`…)" has the same operand gap. PC5 (line 70: "summing to 4,301 digits") and the CTV boundary bracket (line 115) already disambiguate it, so the effect is wording only. | product-owner |
| ADV-P14-C04 | LOW | Raise site cited incompletely | BC-1.03.002.md:86 (EC-007, CP-C26); legacy SL:1026-1028, SL:1033 | A string cached `size` raises at SL:1033 (`size < off`) only when `tin`, `c_wr` and `mixv6` are all present. If any of them is missing, `off > 0` at SL:1027 raises first. Both paths degrade the same way, so tests are unaffected. Name both sites. The matching error-taxonomy CP-C26 row (error-taxonomy.md:318) is outside this perimeter. | product-owner |
| ADV-P14-C05 | LOW | Body inconsistency | BC-1.07.002.md:173 (Purity "I/O operations: none") vs :63-67 (PC2), :78 (PC5) | PC2 and PC5 require stdin to be read to EOF when the switch is off or config errors (ADV-P13-C09). The Purity table still says the path does no I/O. | product-owner |

### 2. Policy compliance

- **P1** append_only_numbering: PASS. CP-T08 is kept as retired; CP-C25..27 are appended.
- **P2** lift_invariants_to_bcs: PASS. DI-007/008/012 are cited consistently with the sibling convention.
- **P4** semantic_anchoring_integrity: FINDING ADV-P14-C02 (canonical-leg anchor contradicts its owner BC). The ARCH-03 `#interfaces…`, `#subagent`, `#transcript` and `#statusline-guard` anchors and the ARCH-04 AD-08 anchor all resolve.
- **P5** creators_justify_anchors: PASS.
- **P6** subsystem name: PASS. All 31 BCs are SS-01.
- **P7** H1 = BC-INDEX = PRD title: PASS. All 31 were checked against BC-INDEX; a sample against prd.md.
- **P12** settled_decisions_are_constraints: PASS. OD-32, OD-155, OD-156, OD-160, OD-161, OD-163, OD-167, OD-168 and OD-172 are applied, not reopened.
- **P13** parity_before_behavior_change: PASS. Every deviation names an id from the closed set.
- **P14** public_repo_hygiene: PASS.
- **P16** thresholds_are_explained: PASS. T-054..T-061, T-042, the 993 depth edge and the 40-code-point name limit all carry rationale.
- **P17** ledger_format_frozen: N.A. These BCs never touch the ledger.
- **P18** cross_platform_from_day_one: PASS. Windows legs are stated, and the not-executed ones are flagged for the windows-2025 CI leg.
- **P19** go_hardening_toolchain: PASS. FMA detector, no `encoding/json`, pyfmt routing.
- **P20** config_over_code: PASS. Every behavior value is a registered key with a matching range; the 1e3/1e6 divisors, the name format and the 40-code-point truncation are documented format constants.
- **P21** public_artifact_hygiene: PASS.

### 3. What I did not fully read or verify

**Not fully read:**
- Front matter and closing sections (after the VP and Traceability tables) of BC-1.03.008, 009, 011–017 and 019–021, BC-1.06.002 (lines 1-27) and BC-1.07.005–008.
- domain-spec/capabilities.md, domain-spec/invariants.md, the ARCH-03 and ARCH-04 bodies (headings and anchors only), prd-supplements/test-vectors, and the bodies of the cited VP files (front matter and grep only, except the VP-002/VP-005 subagent lines).

**Python claims I could not verify:**
- `fh.seek(negative int)` raises OSError rather than ValueError on a BufferedReader (BC-1.03.002 EC-009).
- `json.loads` returns one shared NaN object (BC-1.03.005 PC5(a), BC-1.03.010 NaN vector).
- The digit count of the literal 10^309 in BC-1.03.010's CP-O08 `tout` golden.
- The measured 993/994 depth edges and the BC-5.02.006 encoder budgets.
- That `str()` of a deeply nested subagent `name` (≤ 990 levels) stays within the repr recursion budget. If it did not, there would be an uncatalogued RecursionError path in subagent mode.

### 4. Novelty and verdict

Novelty is LOW to MEDIUM: C02 is a real propagation gap left by the pass-10 ruling, and C01 is a contradiction inside one BC; C03–C05 are refinements. With two MEDIUM findings the verdict is **NOT_CLEAN** (OD-195).

Files: specs/behavioral-contracts/ss-01/BC-1.03.005.md, specs/behavioral-contracts/ss-01/BC-1.03.018.md, specs/behavioral-contracts/ss-01/BC-1.03.007.md, specs/behavioral-contracts/ss-01/BC-1.03.006.md, specs/behavioral-contracts/ss-01/BC-1.03.002.md, specs/behavioral-contracts/ss-01/BC-1.07.002.md, legacy/dgx_statusline.py

## Perimeter C2 (BC-1.04, BC-1.05)

Findings: 10 (high 0, medium 5, low 5, cosmetic 0).

## ADV-P14 Perimeter C2 (BC-1.04.*, BC-1.05.*): Pass 14 findings

### 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P14-C2-01 | MEDIUM | Incomplete OD-160 sibling sweep (partial fix of ADV-P13-C2-01) | BC-1.04.004.md:83-90; BC-1.04.008.md:72-81; BC-1.04.011.md:73-85; BC-1.04.006.md:76-77; legacy SL:740, 783, 816, 818; error-taxonomy.md:320-324 | BC-1.04.004 Inv 3 says the "equivalent unguarded render sites in the sibling segment contracts are pinned in their own edge cases". Four foreign cached-sample string faults have no EC and no CP-C row: (a) a string box rate, ValueError at `f"{rate:.0f}"` (SL:783); BC-1.04.008 has no OD-160 edge case at all and its L2 row lists only DI-007. (b) A string temperature `t`, ValueError at SL:816. (c) A string tariff `rate_c` with a truthy numeric wall, TypeError at `wall / 1000 * rate_c` (SL:818). (d) A string `dgx_preempt:rate5m` when `q > 0` is false, TypeError at the second operand of SL:740 (CP-C29 covers only `q`). Sweeping by hand missed these four, so the sweep needs a checklist [process-gap]. | product-owner |
| ADV-P14-C2-02 | MEDIUM | Missing crash family / contradicts PC1 | BC-1.04.004.md:81-84; BC-1.04.010.md:52; BC-1.04.013.md:49-53; legacy SL:741, 762, 783, 793, 813, 815, 816, 818, 825, 633 | Inv 3 limits the exact-giant-int OverflowError (\|n\| >= 2**1024 - 2**970) to mix-cache `lr[0]` (CP-C24). Cached sample values of that shape raise the same way at several more sites:<br>• `r`/`q` `.0f` (SL:741)<br>• host share `.0f` (SL:762, positive only)<br>• box rate (SL:783)<br>• `math.isnan(ttft)` (SL:793, both signs). This contradicts BC-1.04.010 PC1, which says the segment exists only if `ttft` is a number and not NaN.<br>• `w` (SL:813)<br>• `wall` (SL:815, both signs)<br>• `t` (SL:816)<br>• `rate_c` (SL:818)<br>• `now - last` (SL:825, positive only)<br>• a cached `dgx_mtok`, which BC-1.04.013 PC1 passes through raw, raises at `tot * dgx_mtok / 1e6` (SL:633)<br>One shape does not raise and should be pinned: a positive giant KV renders `KV▰▰▰▰ 100%`, because `min(int, 100.0)` returns `100.0`. The CP-C register has no rows for any of these. | product-owner |
| ADV-P14-C2-03 | MEDIUM | P20 config-over-code; ARCH contradicts BC | ARCH-03-statusline.md:378-384, 392-393, 401 vs BC-1.05.004.md:63, 79; interface-definitions.md:295 | The declared pure `RecordCost(history, sess, now)` decides the throttle with `record_throttle_s` (ARCH-03:392). However, neither its parameters nor `CostConfig` carry that key, and the package is declared to do no env or config reads (ARCH-03:343). An implementer of the declared API can only hard-code 60, which breaks the registered key `statusline.cost.record_throttle_s`. Fix: add a config parameter or a member to `CostConfig`. | architect |
| ADV-P14-C2-04 | MEDIUM | Mis-anchor: symbols that do not exist (pass-13 respell incomplete) | BC-1.05.004.md:161 vs :213; BC-1.05.005.md:152 vs :203; BC-1.05.006.md:141, 194; BC-1.05.009.md:190 | The Architecture Module rows and Owning-component prose name `Record`/`ForLane`. ARCH-03 declares only `RecordCost` and `CostThresholds` (ARCH-03:401, 413); a grep for `func Record` finds no other match. BC-1.05.004 and BC-1.05.005 each use both spellings within the same file. | product-owner |
| ADV-P14-C2-05 | MEDIUM | Purity residue contradicts ARCH-00/ARCH-03 | BC-1.05.004.md:209-211; BC-1.05.005.md:199-201; BC-1.05.006.md:190-192; BC-1.05.009.md:186-188; BC-1.05.008.md:186 | The Purity tables still say "store fake", "(store injected)" and "Overall classification: boundary", while the I/O cell in the same table says none. BC-1.05.008:186 states that ARCH-00 classifies `internal/cost` as boundary, "store writes behind the Store seam". ARCH-00:88 actually says **pure core**, and ARCH-03:343 forbids I/O. This text would lead an implementer to inject a store into `internal/cost`. | product-owner |
| ADV-P14-C2-06 | LOW | Mis-citation | ARCH-03-statusline.md:352, 373 | ARCH-03 cites "BC-1.05.005 PC-2" for the history load and "PC-3" for the config keys. In BC-1.05.005 those are Preconditions 2 and 3; PC2 is the usd skip and PC3 is the append rule. | architect |
| ADV-P14-C2-07 | LOW | Lossy declared type | ARCH-03-statusline.md:413; BC-1.05.009.md:73-76; legacy SL:613, 624 | `CostThresholds` returns `*[2]float64`, but hylo's own writer keeps int `usd` values as ints (BC-1.05.009 PC3: `3` → `3`), and legacy compares int with float exactly. A threshold int above 2**53 (for example 9007199254740993) against a stdin float 9007199254740992.0 gives `>=` False in Python and True in Go after the float64 conversion. Contrived values (about $9e15), but the gap is real. | architect |
| ADV-P14-C2-08 | LOW | Non-monotonic `modified` lists [process-gap] | BC-1.04.003.md:26; BC-1.04.004.md:26; BC-1.04.012.md:25 | The pass-13 residual-sweep entries (1.3.10, 1.2.7, 1.3.5) were inserted ahead of lower versions. This is the defect class already fixed in BC-1.05.005 as ADV-P12-C2-09; it has now recurred in three files, so the sweep needs an ordering check. | product-owner |
| ADV-P14-C2-09 | LOW | Ambiguous framing grammar | BC-1.04.001.md:144-146 | "A value that fails `int()`" does not say that this is Python's int grammar: underscores, surrounding whitespace, `+` and Unicode digits are all accepted, so `Content-Length: 1_0` reads 10 bytes. The chunk-size `int(line, 16)` after the `;` strip is likewise unspecified. A Go `strconv` parse would differ. VP-030 scopes malformed framing out, hence LOW. | product-owner |
| ADV-P14-C2-10 | LOW | P16/P20 sibling note gap (pending intent verification) | BC-1.04.012.md:61; BC-1.04.017.md:50-54 | The divisors 60 and 1440 lack the unit-constant ("named constant, not config") note that ADV-P13-C2-05 added to BC-1.04.007 and BC-1.04.011. | product-owner |

### 2. Policy compliance
- P1 append_only_numbering: PASS.
- P2 lift_invariants_to_bcs: FINDING ADV-P14-C2-01 (BC-1.04.008's L2 row needs DI-008 and DI-012 once its OD-160 edge case lands).
- P4 semantic_anchoring_integrity: FINDING ADV-P14-C2-04, ADV-P14-C2-05, ADV-P14-C2-06.
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS (SS-01 matches ARCH-INDEX:55).
- P7 H1 = BC-INDEX = PRD: PASS (all 30 match: BC-INDEX:143-177, prd.md:244-278).
- P12 settled_decisions_are_constraints: PASS.
- P13 parity_before_behavior_change: PASS.
- P14 public_repo_hygiene: PASS (only RFC 5737 addresses seen).
- P16 thresholds_are_explained: FINDING ADV-P14-C2-10 (LOW).
- P17 ledger_format_frozen: PASS.
- P18 cross_platform_from_day_one: PASS.
- P19 go_hardening_toolchain: N.A.
- P20 config_over_code: FINDING ADV-P14-C2-03.
- P21 public_artifact_hygiene: PASS.

### 3. Not fully read; Python claims I could not verify
- **Not fully read:** most BC-1.04 frontmatter blocks (changelogs were checked with grep); interface-definitions.md (only the relevant rows); ARCH-03 (only lines 335-420); error-taxonomy.md (only lines 270-349); the bodies of VP-001, VP-012, VP-030, VP-021 and VP-031 (only their frontmatter `bcs:` was checked); domain-spec capabilities.md and invariants.md; test-vectors; ARCH-04.
- **Python claims I could not run (no execution tool):** every giant-int site in C2-02 is derived from the source. Two of the operations it relies on are already oracle-verified elsewhere in the specs: `.0f` on a giant int (BC-1.04.018 PC-1) and float minus giant int (BC-1.04.002 Inv 1). Not verified at all: `math.isnan(giant int)` raising OverflowError; the positive-giant KV rendering `100%`; `int("1_0")` being accepted on the http.client Content-Length path; the int-vs-float comparison case in C2-07.
- **Spot-checked by hand and found correct:** all canonical vectors in BC-1.04.007, BC-1.04.009, BC-1.04.017, BC-1.04.019, BC-1.04.020, BC-1.05.002, BC-1.05.005, BC-1.05.006 and BC-1.05.008.

### 4. Novelty
Novelty is MEDIUM. C2-02, C2-03 and C2-05 are new classes of defect. C2-01 and C2-04 are gaps left by pass-13 fixes that did not reach every sibling file.

**NOT_CLEAN** (6 MEDIUM).

## Perimeter D (S2-S6 BCs)

Findings: 16 (high 1, medium 8, low 7, cosmetic 0).

## ADV-P14 Perimeter D: S2–S6 BCs (53 files)

Result: **NOT_CLEAN**. One HIGH and eight MEDIUM findings, plus seven LOW.

### 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P14-D01 | HIGH | partial-fix propagation / missing reason | BC-2.01.004:170-172, :231-235 vs :293-320; BC-2.01.005:168-171, :181-184; BC-5.03.001:55-59; error-taxonomy.md:107 | OD-194 (PC-13) added nine `statusline.labels.*` keys whose range includes "display width 1..16". Three places still say the width function is consulted ONLY for the pill-label bound: BC-2.01.004 PC-6, BC-2.01.004 PC-9 and BC-5.03.001 Inv 1. BC-2.01.005 PC-6 gives the width reason only for the three `pill.label_*` keys, and the error taxonomy lists it for "pill labels" only. So `HYLO_STATUSLINE_LABELS_OLD` with a 17-column value has no defined reason string, and the "ONLY" scope wording would skip the check. Affects 3+ files. | product-owner |
| ADV-P14-D02 | MEDIUM | contradiction | BC-2.01.001:75-78 vs BC-2.01.005:242-249 | BC-2.01.001 PC-2 says a default-only Text/List key with an empty value gives `expected non-empty control-free text`. BC-2.01.005 PC-7 pins `HYLO_STATUSLINE_LIMITS_WINDOWS=` → empty list → `(out of range)`. BC-2.01.001 PC-2 itself also says "list keys become the empty list". A test of the List member gets two answers. | product-owner |
| ADV-P14-D03 | MEDIUM | contradiction (reason precedence) | BC-2.02.003:68-70, :85 vs BC-2.02.001:189-196 | BC-2.02.003 places "result outside int64 → out of range" inside the grammar checks, which run before range ("grammar errors precede range errors"). BC-2.02.001 lists int64 overflow under range rule 3, after rule 2 `negative`. Example: `-99999999999999999999` on an Int key with floor ≥ 0 (e.g. `1..100`) is `out of range` by BC-2.02.003 and `negative` by BC-2.02.001. | product-owner |
| ADV-P14-D04 | MEDIUM | ambiguous error bytes | BC-2.03.002:108-121, :84-90, :125-129 | With `HYLO_PATHS_CACHE_DIR=~/c`, PC-4's general rule gives stderr `cannot determine cache directory (HOME unset)`. The same PC, and PC-3/PC-5 ("path grammar applies in full"), say it reports `home directory unknown`. The exact stderr line for both cases (home unset, home relative) is unstated, so the byte test cannot be written. | product-owner |
| ADV-P14-D05 | MEDIUM | cross-platform gap (P18) | BC-6.03.001:145-159, :163-168; BC-6.03.002:68-78; ARCH-07-parity-harness.md:212 | `*.windows.golden` files are written by `-update` on Windows from raw oracle stdout. Python's Windows text-mode `print()` writes CRLF (SL:1234). The open CRLF→LF conversion is defined only for comparisons, not for the golden write path. As specified, the Windows goldens hold CRLF, and Go's LF output then fails Tier B on windows-2025. | architect |
| ADV-P14-D06 | MEDIUM | unsatisfiable check [owner-question, pending intent verification] | BC-6.03.004:153-158 | For multi-step D4-EX-3 cases, the oracle self-consistency leg compares step k caches against step k-1 caches. Legacy rewrites clock-varying members every refresh in which they fire: `rl_ts` (SL:307), `fetch_ts`/`ts` (SL:349, :353). With `nan` TTL a refetch happens every step. So any step whose clock advances fails this leg, whatever hylo does. | product-owner |
| ADV-P14-D07 | MEDIUM | underspecified representation | BC-2.01.005:206-225; BC-5.02.004:58-60 | "Go maps each invalid byte to U+DC00+b" followed by a "bytewise" prefix match does not say the code point is stored in the BC-5.02.004 WTF-8 form. Go's `string(rune(0xDCFF))` yields U+FFFD. A U+FFFD or raw-byte implementation passes the acceptance pin but mis-matches models that carry a `\udcff` escape (legacy matches them, SL:902-907). The equivalence claim only holds under the WTF-8 encoding. | product-owner |
| ADV-P14-D08 | MEDIUM | mis-anchor (P4) | BC-2.01.004:302-304, :39 | PC-13 places `statusline.labels.input` in "PC-8"; it is defined in PC-6 (:166-168). It places `labels.vllm_down`/`lmcache_down` in "PC-11"; they are in PC-12 (:283-291), and PC-11 is the rename-retry keys. The pass-13 changelog says these anchors were verified on disk. | product-owner |
| ADV-P14-D09 | MEDIUM | signature contradiction | BC-4.01.001:52-59 vs ARCH-01-binary-cli.md:46-55, :62-73 | PC-1 says `--subagent` is selected "within" `runStatusline(env, stdin, stdout, stderr)`. That function takes no argv. ARCH-01 routes `--subagent` in `run` to a separate `runStatuslineSubagent(args, …)`. As written, a dispatch test against `runStatusline` cannot be built. | product-owner |
| ADV-P14-D10 | LOW | legacy line mis-cite | BC-6.03.003:86, :188 | The `get_sample` save is cited as SL:350. That line is `entry.update`; the `save_cache` call is SL:351 (legacy :349-351). BC-5.02.006 cites SL:351 correctly. | product-owner |
| ADV-P14-D11 | LOW | stale term | BC-6.02.003:181-182 | "The fake-table branch's first P1 consumer" sits in the same PC that states there is NO fake process table (:172-173, pass-12 call 2). | product-owner |
| ADV-P14-D12 | LOW | stale sibling text | BC-6.02.001:157, :138 | The VP-035 row still scopes the scan to `internal/statusline/testdata/`, while PC-4 (:95-102) uses runtime discovery of every `testdata/`. EC-001 uses the pre-OD-148 path `testdata/cases/x/`. | product-owner |
| ADV-P14-D13 | LOW | asymmetry | BC-6.01.003:72-83, :91-94, :116-118, EC-003 :187 | The text says "both shims implement this split identically", but only the Go fallback for a malformed value is specified (warning, real clock). The Python shim's malformed behaviour is unstated, and EC-003 gives KeyError → degraded when the value is missing. The env builder prevents both states, so there is no runtime effect. | product-owner |
| ADV-P14-D14 | LOW | threshold rationale (P16) | BC-5.01.004:51-55 | The width envelope 67 is labeled "derived" but no derivation is given; "exceeds the widest consumer cell" does not produce 67. | product-owner |
| ADV-P14-D15 | LOW | purity mislabel | BC-3.01.001:202-206 vs :84-113 | Purity says "I/O none / pure core / deterministic", but `LocalZone` loads zone files (`LoadLocation`), and leg (c) reads the OS zone through the runtime. | product-owner |
| ADV-P14-D16 | LOW | CI wording | BC-6.04.001:101-104 | The `HYLO_PARITY_PYTHON` export is stated for the Tier A job only, yet the timing job also needs the oracle (BC-6.04.002 Pre-3), and so does the nightly fuzz job. "setup-python must precede `go test ./...`" is also stale: these jobs run `-run <member>`, not `./...`. | architect |

### 2. Policy compliance

- P1 append_only_numbering: PASS (CP-T08 is retired and not reused).
- P2 lift_invariants_to_bcs: PASS.
- P4 semantic_anchoring_integrity: FINDING (D08, D09; D11 and D12 are minor).
- P5 creators_justify_anchors: PASS.
- P6 subsystem names: PASS (SS-02..06 match the ARCH-INDEX registry at :56-60).
- P7 H1 = BC-INDEX = PRD: PASS (12 BCs compared across all three).
- P12 settled_decisions_are_constraints: PASS (D06 is tagged [owner-question]).
- P13 parity_before_behavior_change: PASS.
- P14 public_repo_hygiene: PASS (only RFC 5737 addresses and generic placeholder paths in the perimeter).
- P16 thresholds_are_explained: FINDING D14.
- P18 cross_platform_from_day_one: FINDING D05.
- P19 go_hardening_toolchain: N.A.
- P20 config_over_code: PASS. `USER_HZ`, the 25 ms test constant and the depth constants all carry why-not-config notes.
- P21 public_artifact_hygiene: PASS.
- P3, P8, P9, P10, P11, P15, P17: N.A.

### 3. Coverage gaps and unverifiable claims

**Not fully read:**
- Most BC frontmatter `modified:` histories (body read from the H1 on).
- `prd-supplements/` (only `error-taxonomy.md` and `interface-definitions.md` checked by search).
- ARCH-02, 03, 04, 05 and 08 (only searched); ARCH-01, 06 and 07 read in part.
- The VP files, `capabilities.md`, `invariants.md` and BC-ALLOCATION.

**Python claims I could not verify (no interpreter):**
- All depth constants: 993/994, 991/992, 990/991, 992/993; encoders 991/990/994.
- The macOS libc `mktime` D1 values.
- The 4,300-digit limit counting leading zeros.
- `int()` rejecting U+001C.
- The 3.11 `fromisoformat` multi-byte separator.
- The BC-5.03.004 ntpath CTVs, which were taken from the pure-Python fallback on macOS while the Windows oracle uses the C `_path_normpath`.
- The 17% round-trip drift figure.
- The `_PyTime_AsSecondsDouble` 2^62 divergence.
- The CRLF behaviour of Windows `print()` under the shim.

**Spot-checked:** the BC-5.02.002 lengths (rows 4, 13, 21, 24, 29, 33, 35, 40, 44, 47, 51, 53, 54, 56, 62) and the golden A arithmetic (⌂, ⏱, $/h, limits, token totals, composition) both reproduce.

### 4. Novelty

MEDIUM. D01, D02, D03, D05, D06, D07 and D09 are new cross-file gaps. D08, D10 and D12 are leftovers of earlier fixes that did not fully propagate.

**NOT_CLEAN**: 1 HIGH, 8 MEDIUM, 7 LOW.
