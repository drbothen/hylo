---
document_type: adversarial-review
phase: 1d
pass: 10
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 69
---

# Adversarial Spec Review — Phase 1d, Pass 10

Pass 10 ran as six fresh-context perimeters, the same split as passes 1-9. Each section is the verbatim final report of one perimeter, unedited except for this framing. NOT_CONVERGED (69 findings: HIGH 8 / MEDIUM 33 / LOW 23 / COSMETIC 5; pass 9 had 85 with 15 HIGH). The orchestrator spot-verified A03 (no .github on factory-artifacts), A07 (reason string absent from error-taxonomy and BC-2.02.001), A2-01 and A2-03 (legacy SL:876-880, SL:900-908), D02 (ARCH-07 vs BC history), C2-01 (BC-1.04.001 step list) on disk, and measured B02 on CPython 3.11.7: the text reader decodes the first 8192 bytes (invalid byte at offset <8192 fails, >=8192 reads), independent of the 4096 st_blksize; all held.

## Perimeter A (PRD, supplements, architecture, CI)

Findings: 17 (high 3, medium 8, low 5, cosmetic 1).

## Adversarial Review: Phase 1d, Pass 10, Perimeter A

### 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P10-A01 | HIGH | contradiction, CI (P11) | cicd-setup.md:88 vs :58, :151-152; ARCH-08:105, :169-175 | The `coverage` row in the positive-coverage table still says the job fails when a gated package is "absent from the profile", and it prints `coverage: P packages profiled`. The job table, lag note 4 and ARCH-08 (ADV-P9-A04) instead print `coverage: G of 3 gated packages present` and check only packages that exist. Under the first reading this required check fails on every PR until all three packages exist. Under the second it passes. The pass-9 fix updated its sibling rows but not this one. | architect |
| ADV-P10-A02 | MEDIUM | partial-fix regression, CI timeout (P11) | cicd-setup.md:148-149 vs :58; ARCH-08:97-99 | Lag note 4 says the coverage job "keeps its 10-minute timeout". The job table and ARCH-08 give 30 minutes (ADV-P9-A15: it runs the test job's selection plus `-coverpkg` instrumentation). The fix landed in two places; the third still has the old value. | architect |
| ADV-P10-A03 | HIGH | CI cannot do what the spec requires, hygiene [process-gap] | cicd-setup.md:135-143; nfr-catalog.md:29; prd.md:494 | Lag note 3 requires the category pattern scan to run "on every push … including pushes to the public `factory-artifacts` branch", to be done by adding a branch trigger to ci.yml. GitHub runs push workflows from the workflow files in the pushed commit, and factory-artifacts has no `.github/` (I globbed the worktree: no matches). So that trigger can never fire. The scan is a `git grep` over the checked-out tree, so it never reads factory-artifacts content at all. NFR-006's "every push" cannot be met as designed. | architect |
| ADV-P10-A04 | MEDIUM | CI could pass while checking nothing (P11) | ARCH-08:134-147, :182-184; cicd-setup.md:80-81, :87 | Tier A, Tier B and timing compare N against a census taken at runtime of the directories or goldens that are present. A commit that deletes case directories or golden files shrinks both numbers equally, and the job passes. Nothing is compared against a committed expected count or manifest, so "a partially lost corpus/golden set must not pass" (ADV-P2-A15, pass-5 A19) is not achieved. | architect |
| ADV-P10-A05 | MEDIUM | CI could pass while checking nothing (P11) | ARCH-08:164-167; cicd-setup.md:85 | The gitleaks check fails only when `N == 0`. A shallow or narrowed scan still covers at least 1 commit, so it passes. The stated threat (shallow `--log-opts`) is therefore not detected. The check needs to compare N with `git rev-list --count` over both refs, or assert that the factory-artifacts ref was fetched. | architect |
| ADV-P10-A06 | MEDIUM | CI could pass while checking nothing (P11) | ARCH-08:105, :169-173; cicd-setup.md:58 | "Checks each gated package that EXISTS" has no rule for `G == 0`, or for a gated package that is renamed or moved after its sources land. Either way the required gate silently stops checking that package and still passes. | architect |
| ADV-P10-A07 | HIGH | partial-fix regression, error vocabulary | error-taxonomy.md:101; BC-2.02.001:111-141 (cross-ref); interface-definitions.md:201 | The path-grammar reason `not an absolute path` (minted pass-9 A11, BC-2.01.005:85) is missing from the error-taxonomy reason table and from BC-2.02.001's "exact strings" table. interface-definitions:201 says it is "mirrored in error-taxonomy", which is false. Two files are unsynced. | product-owner |
| ADV-P10-A08 | MEDIUM | mis-anchor (P4) | risk-register.md:29 | R-004 calls Tier A's runtime census the line `timing: N cases timed > 0`. That is the timing job's line. ARCH-08:134 defines the Tier A census as `parity: N cases compared, M exclusions validated, K caches swapped`. The R-004 mitigation therefore points at the wrong detector. | architect |
| ADV-P10-A09 | MEDIUM | contradiction about P1 exit gates | nfr-catalog.md:64-65 vs ARCH-08:207-209, risk-register.md:29, ARCH-INDEX.md:106-108 | NFR-catalog says the OD-158 coverage gate "is the only additional P1 exit gate". OD-149 makes one clean nightly Tier C run on all three OSes the P1 exit condition, and three other documents say so. Phase 2 exit stories would see conflicting lists of gates. | product-owner |
| ADV-P10-A10 | MEDIUM | mis-anchor, circular reference (P4) | ARCH-03:195; ARCH-06:93-94 | Both name BC-5.02.003 as "the owning cache BC" that pins the mix-cache re-read loop (Save 994 / Load 991). BC-5.02.003:119 hands this to "the owning transcript/cache BC". The loop is actually pinned in BC-1.03.021:64 (PC5/EC-004). A test writer would put the test in the wrong place. | architect |
| ADV-P10-A11 | MEDIUM | interface cannot express a requirement | ARCH-02:91, :117; ARCH-09:35 | `Load(opts LoadOptions)` is the injection point for the `platform.EnvVars` seam (ARCH-02:41-44, ARCH-03:49-50, AD-10). `LoadOptions` is never declared anywhere in specs/ (grep: only the `FileLayer` mention). The seam the whole config-testability design depends on has no field in the signature. | architect |
| ADV-P10-A12 | LOW | interface gap | ARCH-06:151, :257-279 | The signature canon has only `D(n int64, …)`. BC-5.01.004 PC-5 requires the `{pct:>2d}` site to format an exact integer beyond int64. No pyfmt helper serves that, so the caller has to format outside pyfmt, which breaks AD-04's single home. | architect |
| ADV-P10-A13 | LOW | VP catalog drift (P9) | module-criticality.md:58, :72-79 vs VP-INDEX.md:112 | VP-038 is counted under `internal/statusline` ("via source_bc"). The VP-INDEX Module column lists only `internal/pyfmt (str.go)`, yet module-criticality claims to be regenerated from that column. | product-owner |
| ADV-P10-A14 | LOW | internal inconsistency | error-taxonomy.md:104 vs :86-88 | The text says "the four strings above are the entire number-range vocabulary", but the table has six number-range strings (the four plus two ascending-pair reasons). | product-owner |
| ADV-P10-A15 | LOW | stale history notes | error-taxonomy.md:95; interface-definitions.md:201 | error-taxonomy:95 says the taxonomy is the "minting source of record" because "agent 8's amendment had not landed". BC-2.02.001:130 now says the string was minted there. interface-definitions:201 says BC-2.01.005's amendment is "not yet on disk", but it is at BC-2.01.005:85. | product-owner |
| ADV-P10-A16 | LOW | stale comment | ARCH-06:178-183 | The `Decode` comment lists four depth constants and leaves out `depthMetricsReply = 992`, which the file row at :31 and prd §8 both state. | architect |
| ADV-P10-A17 | COSMETIC | wording | interface-definitions.md:36 | `--config` is called a "Global flag" although `config path` is the only verb that accepts it. | product-owner |

### 2. Policy compliance

- **P1** append_only_numbering: PASS (CP-T08 retired, never reused; CP-C06/C07 reserved).
- **P2** lift_invariants_to_bcs: PASS for this perimeter.
- **P4** semantic_anchoring_integrity: FINDING A08, A10, A13.
- **P5** creators_justify_anchors: PASS.
- **P6** subsystem names: PASS (registry and PRD §1.6 agree; the SS-ID rule is stated).
- **P7** BC H1 vs PRD rows: PASS (all S2–S6 H1s and S1.01/.05/.06/.07 checked against PRD §2; no mismatches).
- **P9** VP-INDEX as catalog: FINDING A13 (LOW). Arithmetic PASS (41 = 33+7+1 = 20+13+3+2+1+1+1; the primary-home split sums to 41).
- **P11** ci_positive_coverage_assertion: FINDING A01, A02, A03, A04, A05, A06.
- **P12** settled decisions: PASS.
- **P13** parity before behavior change: PASS (closed twelve-id set is consistent across the PRD, ARCH-00/07 and the taxonomy).
- **P14** public_repo_hygiene: PASS.
- **P16** thresholds explained: PASS.
- **P17** ledger format frozen: PASS.
- **P18** cross-platform: PASS.
- **P19** Go hardening toolchain: PASS (the toolchain-before-govulncheck ordering is stated).
- **P20** config over code: PASS (no DGX_* aliases; vocabulary gap is tracked as A07).
- **P21** public_artifact_hygiene: PASS.

### 3. Files not fully read

None in the perimeter; every file in it was read in full. BC and VP files were opened only to check specific cross-references: BC-INDEX-adjacent H1s, BC-2.02.001, BC-2.01.001/.005, BC-5.01.004, BC-5.02.003/.006, BC-1.03.021, BC-1.02.027/.028, BC-6.04.002 and VP-INDEX.

### 4. Novelty and convergence

Novelty: MEDIUM. A03, A04, A05, A06 and A11 are new gaps. A01, A02, A07, A08 and A09 come from pass-9 fixes that were applied to some files but not their siblings.

**NOT_CONVERGED**

## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 10 (high 1, medium 6, low 3, cosmetic 0).

## Adversarial Review: Phase 1d, Pass 10, Perimeter A2

### 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P10-A2-01 | HIGH | for-all property false for legal input | VP-004:38-42, 55-57, 77-79, 130; also BC-4.01.001:109, BC-1.07.001:110 | VP-004 says the `--subagent` entry may only print "zero or more LF-terminated NDJSON lines, zero bytes allowed", and its fuzz fails on any non-empty output that is not NDJSON. But a catalogued renderer fault (CP-A01..A05) legally prints the 29-byte non-JSON degraded line: BC-1.07.008, the DI-008 carve-out (invariants.md:31) and VP-001:51-56 all say so. Fuzzed stdin reaches that state: a task whose `tokenCount` is an exact int ≥ 2**1024 makes `float()` raise OverflowError. `_fmt_tokens` catches only TypeError/ValueError (SL:876-880), so the guard prints the line (SL:1243-1244). A correct port therefore fails this fuzz. The same narrowed output set is copied into the BC-4.01.001 and BC-1.07.001 VP rows. | architect (VP-004); product-owner (BC rows) |
| ADV-P10-A2-02 | MEDIUM | oracle classifier uses the wrong decode mode (lets bad ports pass) | VP-001:144-147; sibling VP-005:105 | VP-001 tells `isJSONObject` to use `pyfmt.Decode` ModeBytes semantics. The subagent stdin site is ModeText with a 993 budget (VP-006:48, :136); legacy reads `json.load(sys.stdin)` in text mode (SL:930). ModeBytes accepts a UTF-8 BOM (utf-8-sig detection), UTF-16/32 input and unbudgeted depth. Legacy turns all of those into `{}`, which prints zero bytes. VP-001 instead files them under the renderer regime, where rows are legal, so a port that renders rows from BOM, UTF-16 or depth-994 stdin passes. This undoes the pass-9 A2-06 tightening for those inputs. VP-005 leaves its classifier's mode unspecified. | architect |
| ADV-P10-A2-03 | MEDIUM | contradicts a BC / semantic anchor | VP-028:40-41 | VP-028 says "only the subagent model segment drops its tag when no prefix matches". Legacy SL:902-907 and BC-1.07.006 (lines 45-46, 71, 76-78, EC-005) say a miss renders `◨ANTH`. The tag disappears only when the prefix list is empty. An implementer working from VP-028 would drop the cloud tag on every miss. | architect |
| ADV-P10-A2-04 | MEDIUM | VP-INDEX title drift (P9) | VP-INDEX:82 vs VP-008:33 | The catalog name lacks the qualifier "with the ruled PC2 exceptions" that VP-008 v1.5 (pass-8 A2-03) added to its title. The change never reached the index. | architect |
| ADV-P10-A2-05 | MEDIUM | overclaim: no leg can catch a wrong constant at a call site | VP-006:37-43, 94-103, 131-149 | The table checks the *values* of the shared budget constants against the measured flip depths. No leg checks *which* constant each production call site passes, and the self-check runs on the Python oracle, not on Go. A mix-cache site that passes `BudgetStdin` (993 instead of 991) would pass every leg, yet the statement says a wrong derived budget "is detected". Fix: add Go end-to-end depth rows at the measured sites, or a call-site lint. | architect |
| ADV-P10-A2-06 | MEDIUM | stated scopes have no oracle | VP-012:66-73, 137-150 | The statement fixes per-id scopes (OD-166 "and nothing else"; OD-181 transport). The closure check verifies only id membership, case-id uniqueness, test existence and the expected-file match. The mutant catalogue has no "valid id attached to an out-of-scope case" mutant, so an OD-166 entry on an unrelated case would hide a real diff and still pass. Either add per-id scope predicates or state scope review honestly as a manual obligation. | architect |
| ADV-P10-A2-07 | MEDIUM | pass/fail rule only clear from the sketch | VP-014:37-41, 53-56 | The oracle is "exactly as the ruled bytes demand", with no pointer to where those bytes are pinned (the BC-3.02.001 / BC-1.02.017 vectors). The expected output appears only as `tc.WantSuffix` in the sketch. The clause "macOS/Linux probe behaviour is not touched" has no leg at all. | architect |
| ADV-P10-A2-08 | LOW | contradiction inside the statement | VP-001:49-59 | "No fault class exists that yields blank output" conflicts with the same paragraph's rule that subagent parse-path faults print exactly zero bytes. "Every fault trigger in the closed error taxonomy" also leaves out CP-X01..X04 without saying why (error-taxonomy:307-308 disposes of them). Scope the sentence to the main entry. | architect |
| ADV-P10-A2-09 | LOW | absence claim false for one legal input (pending intent verification) | VP-022:38-53 | "No opened path matches the D7 ledger language" fails when stdin's `transcript_path` names the ledger file: legacy opens whatever path stdin gives (SL:1010-1042). Qualify the claim to "except as the stdin-designated transcript", or state DI-007's intent. | architect / business-analyst |
| ADV-P10-A2-10 | LOW | sketch contradicts its property (P11) | VP-012:191-196 vs :74-79 | The rider-existence loop walks `RiderRegister()` but never checks that the register's keys equal the twelve closed ids. A register missing an id passes, against the statement's "EVERY closed-set id". | architect |

### 2. Policy compliance
- P1 append_only_numbering: PASS (CP-T08 retired, not reused; CP-O12 appended).
- P2 lift_invariants_to_bcs: PASS (DI-007 grep re-verified at 38 files; the uncovered DIs are explicitly deferred per OD-115).
- P4 semantic_anchoring_integrity: FINDING A2-03.
- P5 creators_justify_anchors: PASS.
- P6 subsystem names: PASS (the feasibility report's S1-S6 names match ARCH-INDEX SS-01..06).
- P9 vp_index_is_vp_catalog_source_of_truth: FINDING A2-04 (totals, class and method arithmetic verified at 41 = 33+7+1 = 20+13+3+2+1+1+1).
- P11 ci_positive_coverage_assertion: FINDING A2-10.
- P12 settled_decisions_are_constraints: PASS.
- P13 parity_before_behavior_change: PASS.
- P14 public_repo_hygiene: PASS.
- P16 thresholds_are_explained: PASS.
- P17 ledger_format_frozen: PASS.
- P18 cross_platform_from_day_one: PASS.
- P19 go_hardening_toolchain: PASS.
- P20 config_over_code: PASS.
- P21 public_artifact_hygiene: PASS.
- P3, P7, P8, P10, P15: N.A.

### 3. Files not fully read
None in the perimeter; every file was read in full. Outside it I only spot-checked BC-1.07.001, BC-1.07.006, BC-4.01.001, BC-6.01.002, the OD log rows, the error-taxonomy CP-X rows, ARCH-INDEX, and legacy `dgx_statusline.py`.

### 4. Novelty and convergence
Novelty: MEDIUM. A2-01 is a new for-all violation that spans three artifacts; A2-02 and A2-05 are new weaknesses in the oracles.

**NOT_CONVERGED**

## Perimeter B (BC-1.01, BC-1.02)

Findings: 7 (high 0, medium 3, low 3, cosmetic 1).

**ADV-P10-B: findings for pass 10, perimeter B (BC-1.01.\*, BC-1.02.\*)**

I checked every canonical vector I could derive by hand against the legacy code, and all of them hold. That covered heat() and its HSV colours, every countdown floor-division, half-even rounding (including the 0.135 exact tie), the BC-1.01.010 staircase sums, and the Golden-A byte deltas. The findings below are spec gaps or contradictions, not vector errors.

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P10-B01 | MEDIUM | Contradiction between BCs | BC-1.01.008.md:78 vs BC-1.01.003.md:60-64; legacy SL:442-443, 453, 1234 | Inv 3 of BC-1.01.008 says "no CRLF appears in any rendered row". BC-1.01.003 PC5 allows a carve-out: stdin text is printed verbatim. In legacy, a `display_name` of `"a\r\nb"` prints the bytes 0D 0A inside row 1. As written, Inv 3 invites a Go port to strip or translate CR, which would break parity on reachable stdin. Fix: Inv 3 should say "the renderer itself emits no CR" and cite the BC-1.01.003 PC5 carve-out. | product-owner |
| ADV-P10-B02 | MEDIUM | Ambiguity; not testable; cross-platform (P18) | BC-1.02.004.md:93-101; legacy SL:380-381 | PC2.3 gives the decoded chunk as `io.DEFAULT_BUFFER_SIZE` = 8192, but then reports a "4096-byte prefetch observed". The two probes (offset 14 and offset 9015) both sit outside the 4096..8191 window, so they cannot tell the two sizes apart. Go's result for an invalid byte at offsets 4096..8191 is therefore unspecified. The real chunk also depends on the BufferedReader buffer size: st_blksize on POSIX, which varies by filesystem, and 8192 where st_blksize is missing (Windows). The BC should pin one chunk size per OS with a probe inside 4096..8191, or rule the band out of parity. | product-owner |
| ADV-P10-B03 | MEDIUM | Semantic anchoring (P4); partial fix of ADV-P9-B03 | BC-1.02.006:122/141, .011:89, .012:91, .014:104, .017:93, .020:89, .029:87; VP-001:13 and VP-001:41-45 | Seven BCs have CP-O overflow degrade vectors (CP-O01/O02/O03/O05/O12) with no VP row covering the degrade. Their VP tables only hold format or band rows; the VP-001 row in BC-1.02.020 (line 119) covers only NaN and a non-numeric total. On the VP side, VP-001's property text lists CP-O01..O12 and names BC-1.02.029, but its `bcs:` list leaves out .006/.011/.012/.014/.017/.029. The only sibling with a row is BC-1.02.025 (line 130). Pass 9 updated the VP-001 body but did not update `bcs:` or these BCs' VP tables. | architect (VP-001), product-owner (BC tables) |
| ADV-P10-B04 | LOW | Incorrect equivalence claim | BC-1.01.005.md:54-57; interface-definitions.md:194; legacy SL:1224 | PC4 says clamping a negative value beyond int64 to `math.MinInt64` is "output-equivalent". That is false when `narrow_cols` = MinInt64, which the "any Int" range allows. With rows = 2, Python evaluates `-10**30 >= -2**63` as False (row 2 hidden); clamped Go evaluates `MinInt64 >= MinInt64` as True (row 2 shown). Fix: require a sign-preserving big-int comparison, or bound the range of `narrow_cols`. | product-owner |
| ADV-P10-B05 | LOW | Ordering claim incomplete (foreign cache, OD-160) | BC-1.01.009.md:72, 79, 92-94; legacy SL:230-237 | The BC says CP-C10 always faults after the record_cost write. Counter-case: the current session's own history entry has `src:"cc"` and a non-numeric `ts`. Then `now - e.get("ts", 0)` raises at SL:232, before save_cache (SL:237), so nothing is written. The within-step exception assumed by VP-008 does not hold for this case. Error-taxonomy CP-O10's row (error-taxonomy.md:285) makes the same claim; that file is outside this perimeter. | product-owner |
| ADV-P10-B06 | LOW | Unstated assumption | BC-1.02.004.md:82, 87, 102; legacy SL:377, 379, 384 | `os.path.isdir`/`isfile` follow symlinks. PC2.2/2.4 never say so, and PC1's "no symlink resolution" (which is about abspath) could lead a port to use Lstat or DirEntry types. That port would diverge on a symlinked `.git` or HEAD. Fix: state "stat semantics, following symlinks". | product-owner |
| ADV-P10-B07 | COSMETIC | Anchor consistency between sibling BCs | BC-1.02.016..030, Architecture Anchors sections | BC-1.02.016..030 cite bare `ARCH-03-statusline.md`, while BC-1.02.001..015 use the existing fragments (`#session`, `#limits`, `#context`, `#lane`, `#cost`; ARCH-03:319-330). The Stories field reads "S-N.MM" in 016..030 and "TBD" in 001..015. | product-owner |

## 2. Policy compliance

- **P1** PASS: ids are contiguous (001-010, 001-030).
- **P2** PASS: DI-007, DI-008 and DI-012 are cited where they apply.
- **P4** FINDING: B03 (B07 cosmetic).
- **P5** PASS.
- **P6** PASS: subsystem "SS-01" matches the ARCH-INDEX registry.
- **P7** PASS: all 40 H1 titles match BC-INDEX and PRD:163-207; confidence levels match too.
- **P12** PASS.
- **P13** PASS.
- **P14** PASS: no IPs, home paths or private terms in the perimeter files (grep plus the hygiene-term list).
- **P16** PASS.
- **P17** N.A.: no ledger I/O.
- **P18** FINDING: B02 (B06 related).
- **P19** PASS: the no-fuse rule (IM-10) is cited where FMA could matter.
- **P20** PASS: every key used is registered and its range matches (context.cells 1..100, plain_max/red_from finite, units.\* default-only, pill labels 1..16, reroute_all_prefixes, git.ttl_s). B04 is an edge case in how the `narrow_cols` range interacts with PC4.
- **P21** PASS.

## 3. Not fully read, and Python claims I could not verify

**Not fully read:**
- The frontmatter `modified:` histories of most BCs (I read from the body onward).
- VP files: grep only, except VP-001:36-85.
- ARCH-03: only lines 60-90 and the anchor list.
- prd.md and capabilities.md: grep only.
- Legacy `_mix_counts` (SL:977-1156).

**Python claims not verified:**
- The stdin depth limit of 993/994.
- The SHA-1 cache keys (`5a3006e969bd95e3`, `09d4733efe0f2c7f`, `a77db2f8cb13007e`).
- The absolute byte counts 701 / 809 / 642 / 286 / 743. They are internally consistent: the per-segment deltas of 59, 28 and 72 bytes reconcile.
- The 3.11.7 ntpath splitdrive results for `//`, `///` and `//x`. They are consistent with the 3.11 device-path splitdrive code as I recall it.
- CPython's actual `read1` chunk size in TextIOWrapper (the open question behind B02).
- The CP-O12 end-to-end oracle run.

## 4. Novelty

MEDIUM. B01 and B02 are new substantive gaps, and B03 is an incomplete propagation of a pass-9 fix. No vector errors were found.

**NOT_CONVERGED**

## Perimeter C (BC-1.03, BC-1.06, BC-1.07)

Findings: 12 (high 0, medium 7, low 4, cosmetic 1).

## Adversarial Review: Pass 10, Perimeter C (BC-1.03.\*, BC-1.06.\*, BC-1.07.\*)

I read all 31 perimeter BCs in full against `legacy/dgx_statusline.py` (SL:190-206, 220-414, 820-1246). Every canonical vector byte count I recomputed matched. That covers the BC-1.03.002, .003, .004, .005, .006, .007 (incl. the CP-O07 vectors) and .008 vectors, BC-1.03.010 CP-O08 and its shortcut rows, BC-1.03.011, .012, .014 and .016 (T1/T13/T16), all 21 rows of BC-1.03.019, BC-1.03.020 (C1-C3), BC-1.03.021, and the subagent goldens in BC-1.07.004 to .007. The 20 turn-table rows also give the right `lr`.

### 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P10-C01 | MEDIUM | partial-fix propagation / unreachable vector | BC-1.03.007:78, :98-106; vs BC-1.03.018:103, error-taxonomy.md:212; legacy SL:1108, 1117 | **Mirror leg missing.** The owner BC of SL:1117 never states or tests the mirror CP-O07 leg (a huge-int `pp` meeting a float `prompt`, ADV-P4-C08), even though BC-1.03.018 and the taxonomy carry it. It is reachable from a real transcript: `{_i:10^309}`, then `{_i:-10^309}`, then `{_i:1.5}` leaves `tin` 0, so SL:1108 passes and SL:1117 computes `1.5-(-10^309)` and raises. **Canonical seed is foreign.** EC-007 itself says no legacy or hylo writer pairs an int `tin` with a float `pp`. The only pinned CP-O07 vectors (seed `tin 0`, `pp 5.0`) are therefore a foreign-cache state, the OD-160 / ruling-b class, yet they are registered under D4-EX-2. [owner-question] Should those vectors ride OD-160 or D4-EX-2? | product-owner |
| ADV-P10-C02 | MEDIUM | mis-anchor (line pointer drift) | BC-1.03.010:111; BC-1.03.017:54 | Both cite `BC-1.03.018:95-96` as the CP-T04/CP-T05 predicates. Lines 95-96 are actually the CP-T01 and CP-T02 rows; CP-T04 and CP-T05 are now at lines 98-99, shifted by the pass-9 frontmatter additions. This is the same drift class that ARCH-03:313-317 bans for ARCH-03 line pointers. [process-gap]: no rule bans line-number pointers into BC files. | product-owner |
| ADV-P10-C03 | MEDIUM | ambiguity (POSIX surrogate path encoding) | BC-1.03.001:77 (hylo POSIX clause), :22; BC-1.06.001:125, :31 | The hylo POSIX clause reads "each U+DCxx surrogate contributes the single raw byte 0xx … any other lone surrogate fails". Read literally, that maps U+DC00..U+DC7F to the bytes 0x00..0x7F, including NUL and `/`. Legacy's `surrogateescape` maps only U+DC80..U+DCFF and raises on everything else, as the legacy clause in the same row says. An implementer following the hylo wording diverges, and U+DC2F would inject a path separator into the session-cache name. The range should be stated explicitly. | product-owner |
| ADV-P10-C04 | MEDIUM | VP contradicts postcondition | BC-1.03.005:120 vs PC5 :65-68 | The VP-029/031 row says "`ids` has no duplicates after every write". PC5 says a foreign cached `ids` that already holds duplicates is carried as-is, and a string `ids` such as `"zz"` is `list()`-split into `['z','z']`. Both are written back with duplicates (SL:1033, 1153). A generator covering PC5's OD-160 legs falsifies the VP. The pass-6 PC5 qualification was not propagated to the VP row. | product-owner |
| ADV-P10-C05 | MEDIUM | P2 / sibling convention | BC-1.03.005:128 | The Traceability row cites only DI-007. Yet the BC carries named OD-160 deviation legs (PC5) and a VP-012 closure row (:121). Sibling BC-1.03.002:118 cites DI-012 for its OD-160 legs, which is the ADV-P5-C10 convention. | product-owner |
| ADV-P10-C06 | MEDIUM | mis-anchor | error-taxonomy.md:213 | CP-O08 lists "BC-1.03.010, BC-1.03.016" as owners. BC-1.03.016 has no CP-O08 content: its 20 rows include no huge-int `out` row. The CP-O08 vectors live in BC-1.03.010 EC-009 and BC-1.03.018 PC3. | product-owner |
| ADV-P10-C07 | MEDIUM | circular owner anchor | ARCH-03-statusline.md:195; BC-5.02.003:119 | ARCH-03 says "the owning cache BC (BC-5.02.003) pins the re-read loop". BC-5.02.003:119 in turn defers to "the owning transcript/cache BC". The loop is actually pinned in BC-1.03.021 PC5/EC-004, and no document names it as owner. | architect |
| ADV-P10-C08 | LOW | over-generalized postcondition | BC-1.03.021:63-66, :81; BC-1.03.010:73-75; ARCH-03:192-194 | All three say the 992..994-deep mix cache "is re-read from offset 0 and rewritten every refresh (same size)". That holds only when the transcript fits in one read step (524,288 B). Above that, the re-read from 0 parses one step (SL:1044-1058), saves a shallow cache, then advances step by step until the deep line is saved again. The `size` and totals cycle rather than staying constant. A test written from "same size every refresh" fails for large transcripts; 28 of 200 have a single line above 512 KB per SL:1045. | product-owner |
| ADV-P10-C09 | LOW | site-anchor inconsistency | error-taxonomy.md:236-238 vs BC-1.07.008:60-67 | The CP-A01..A03 "Site (legacy SL)" cells cite the guard (SL:1242-1245). BC-1.07.008 and the taxonomy's own CP-A04/A05 rows cite the raise sites (SL:891, 894, 906). | product-owner |
| ADV-P10-C10 | LOW | mis-anchor | error-taxonomy.md:297 | The text places CP-S01..S17 dispositions "in BC-1.02.x / BC-1.01.x". CP-S14 is owned by BC-1.03.013 PC3 and CP-S16 by BC-1.03.015 PC5. | product-owner |
| ADV-P10-C11 | LOW | stale count | BC-1.07.008:133 | Says "48 since pass-7 CP-T09". The register has been 49 since CP-O12 was minted in pass 9 (error-taxonomy.md:266-268; BC-1.03.018:52). | product-owner |
| ADV-P10-C12 | COSMETIC | wording | BC-1.07.008:73 | "exactly the 29 degraded bytes + LF" reads as 30 bytes. The 29 bytes already include the LF, as the hex listing on the same line and :48 show. | product-owner |

### 2. Policy compliance

- **P1** append_only_numbering: PASS (CP-T08 retired, CP-T09 appended; BC IDs contiguous).
- **P2** lift_invariants_to_bcs: FINDING C05.
- **P4** semantic_anchoring_integrity: FINDING C02, C06, C07, C09, C10.
- **P5** creators_justify_anchors: PASS.
- **P6** subsystem name: PASS (`SS-01` matches the ARCH-INDEX:55 registry).
- **P7** H1 = BC-INDEX = PRD: PASS (all 31 titles identical across BC files, BC-INDEX:117-197 and prd.md:213-293).
- **P12** settled_decisions_are_constraints: PASS (C01's exclusion class is raised as [owner-question], not a challenge).
- **P13** parity_before_behavior_change: PASS.
- **P14** public_repo_hygiene: PASS (hygiene-term and IP/home-path scan of the perimeter is clean).
- **P16** thresholds_are_explained: PASS.
- **P17** ledger_format_frozen: PASS (no ledger surface in the perimeter).
- **P18** cross_platform_from_day_one: PASS (C03 is a POSIX-clause ambiguity, not a missing OS).
- **P19** go_hardening_toolchain: N.A.
- **P20** config_over_code: PASS. All config keys cited in the perimeter are registered with ranges matching the BCs (interface-definitions.md:199-203, 231-237, 248-262).
- **P21** public_artifact_hygiene: PASS.

### 3. What I did not read or could not verify

**Not fully read:**
- error-taxonomy.md: lines 153-312 only.
- interface-definitions.md, VP-INDEX.md and the VP files: grep and frontmatter only (`bcs:` reciprocity checked for every cited VP; all reciprocal).
- prd.md and ARCH-04: partial.
- domain-spec/capabilities.md and prd-supplements/test-vectors.md: not read.
- BC-5.02.003 and BC-5.02.006: grep only.

**Python claims I could not verify without running the oracle:**
- The measured depth budgets: mix load 991 / save 994, and transcript 993/994. My frame-count derivation agrees with the 993 and 991 figures but cannot settle 994 vs 993.
- The shared-NaN-object identity in dedup.
- The APFS Errno 92 behavior.
- The `--subagent` EPIPE exit status 120.
- The exact 310-digit `tout` literal in the BC-1.03.010 CP-O08 golden; I did not count its digits.
- The `02:05` clock row, which depends on the test's run timing.

### 4. Novelty and convergence

Novelty is MEDIUM. C01, C02, C04 and C07 are genuine propagation or anchoring gaps that earlier passes missed; the rest are refinements.

NOT_CONVERGED

## Perimeter C2 (BC-1.04, BC-1.05)

Findings: 12 (high 1, medium 5, low 5, cosmetic 1).

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P10-C2-01 | HIGH | contradiction (partial-fix regression of ADV-P9-C2-02) | BC-1.04.001.md:226-236 (normative Go rule) and :190-191; legacy SL:168-171 (urllib `http_error_302`) | The scheme-guard paragraph (:169-178) and ARCH-03 (:229-234) say urlsplit sanitization runs before the guard. Two passages still put the guard first: the normative step list at :230-236 ("apply the scheme guard, normalize (urlsplit sanitization …)") and :191 ("AFTER the raw-header scheme check, the urlsplit sanitization"). An implementer who follows the designated recipe runs the guard on the raw header and rejects `Location: HTTP://…`. That gives no sample where urllib follows the hop, and the BC itself cites this case as oracle-verified (:175-177). | product-owner |
| ADV-P10-C2-02 | MEDIUM | completeness (claimed-exhaustive crash list) | BC-1.04.002.md:77-93 (Inv 1); BC-1.04.003.md:111-112; legacy SL:325, 336, 356 | Inv 1 says it lists every typed crash site "for good" (v1.3.7), but it leaves out OverflowError. In CPython, `now - <exact int ≥ 2**1024−2**970>` raises: a JSON-loaded 309..4300-digit `ts` or point `t` raises at SL:325, SL:336 or SL:356. The SL:324 comparison is exact and does not raise. These are foreign-cache shapes (OD-160), but the "total except" claim tells the Go side it need not degrade there. | product-owner |
| ADV-P10-C2-03 | MEDIUM | mis-anchor | ARCH-03-statusline.md:224-228 | The 101/102/103-is-final divergence cites "BC-1.04.001 EC-024". The 103 Early Hints row is EC-025 (BC-1.04.001.md:342). EC-024 covers the header limits and the 100-Continue skip. | architect |
| ADV-P10-C2-04 | MEDIUM | contradiction (cross-document) | ARCH-03-statusline.md:263-266 | This line says "Schemes outside http/https give NO sample as the D4-EX-3 URL class … NOT the OD-181 exclusion". It is wrong for both readings. A configured non-http(s) URL gives the D4-EX-3 config-error line at load, not a sample miss (BC-2.02.005:42-44). A non-http(s) redirect target is OD-181 (BC-1.04.001.md:178-185; ARCH-03 itself at :244-249). | architect |
| ADV-P10-C2-05 | MEDIUM | mis-anchor | VP-001-never-blank-exit0.md:41-42, :82-83 | VP-001 calls the BC-1.05.007 legs of CP-O10/O11 "cost-history-borne" and cites "EC-009/EC-010". BC-1.05.007 owns the stdin bearers (SL:616/623; error-taxonomy:173-174), and its CP-O10/O11 rows are EC-011/EC-012. EC-009 is api +inf and EC-010 is the Inf/Inf NaN rate. The history bearer is BC-1.05.005 EC-011 (SL:255). | architect |
| ADV-P10-C2-06 | MEDIUM | P20 sibling miss (ADV-P9-C2-09 sweep) | BC-1.05.005.md:88-90 (PC4); BC-1.04.009.md:70 (PC3) | PC4 hard-codes `0.75`/`0.95` although `statusline.cost.percentiles` is a registered key (Pre 3, interface-definitions:244). PC3 hard-codes the `k` top `1.0` although it comes from `statusline.sparkline.scale[k_top]` (Pre 2). The pass-9 sweep named every other registered key beside its literal in these same files. | product-owner |
| ADV-P10-C2-07 | LOW | anchor completeness | interface-definitions.md:218, :297-298, :299 (consumer column) | `pill.label_local` lists consumers BC-1.02.001/1.07.006 only, though its own range text and BC-1.04.004 Pre 3 make BC-1.04.004 a direct consumer. `labels.vllm_down`/`lmcache_down` list BC-1.04.004, which consumes them only indirectly through BC-1.04.005. The glyph-family consumer column leaves out BC-1.04.018 (`sess_rate`) and BC-1.04.019 (`ttft`), which its own member list cites. | architect |
| ADV-P10-C2-08 | LOW | testability | BC-1.04.001.md:63-64 vs Inv 1 (:308) | PC1 says "Exactly one HTTP GET is issued to `<url>/api/v1/query?…`". A redirect chain A→B→A re-keys A and issues a second GET to the same URL (the urllib loop rules in the same PC). A test asserting PC1 literally fails on loops. Reword to "one initial GET plus the hops Inv 1 allows". | product-owner |
| ADV-P10-C2-09 | LOW | Python quirk unstated | BC-1.04.018.md:47-48 (PC1); VP-030:63; legacy SL:776-779 | Per PC1 the segment exists for any number. A mix-cache `lr[0]` that is an exact int of 309..4300 digits instead raises OverflowError at `f"{x:.0f}"` (degrade). The VP-030 quick leg "every JSON value shape of mix[7]" would generate such ints. This is a foreign mix-cache shape, so the BC should either tag it OD-160 or keep the generator to floats. | product-owner |
| ADV-P10-C2-10 | LOW | mis-anchor (sibling of ADV-P9-C2-08: PC vs Precondition) | prd.md:511 | E-NET-001 cites "BC-1.04.004 PC3" for the config-sourced dead rung. That is Precondition 3; PC3 is the fresh-fields rung. | product-owner |
| ADV-P10-C2-11 | LOW (pending intent verification) | VP citation sibling gap | BC-1.04.001/004/005 (CP-N03), BC-1.05.002 EC-009 (CP-O11 co-owner), BC-1.05.003 EC-011 (CP-O12 co-owner); VP-001:13 `bcs` | VP-001 claims CP-N01..N03 and O01..O12, and the sibling owners BC-1.04.014/015/016 and BC-1.05.007 cite VP-001. These co-owner BCs carry degrade rows but no VP-001 row, and VP-001 `bcs` does not list them. | architect |
| ADV-P10-C2-12 | COSMETIC | P20 note | BC-1.05.003.md:76 | The `/ 1e6` MTok divisor has no "unit constant, not config" note. Sibling BC-1.05.002 Pre 4 carries one for 3.6e6. | product-owner |

Re-derived and confirmed correct, no finding:
- BC-1.04.020's 11-step sequence: every tuple, row byte string and cache byte string.
- BC-1.05.005: EC-009 NaN sort for both file orders, the index table, and all vectors.
- BC-1.05.008: the 16/14 lists, thresholds and all 12 golden rows.
- BC-1.05.006: legacy refresh 1 and 2 bytes.
- Sparkline idx/fade vectors (BC-1.04.009 rows 1-3 and EC-002..009) and BC-1.04.015's cell table.
- Power, TTFT and idle vectors.
- urllib header order, the loop caps (37 hops) and the drain ordering against the 3.11 `http_error_302` structure.
- Every BC H1 equals its BC-INDEX row and PRD row.

## 2. Policy compliance
- P1 append_only_numbering: PASS (EC ids sequential; EC-010 renumber holds).
- P2 lift_invariants_to_bcs: PASS.
- P4 semantic_anchoring_integrity: FINDING ADV-P10-C2-03, -05, -07, -10.
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS (SS-01 throughout).
- P7 H1 = BC-INDEX = PRD: PASS (30 of 30 match).
- P12 settled_decisions: PASS (OD-30/156/157/160/166/181/189 respected; no owner question raised).
- P13 parity_before_behavior_change: FINDING ADV-P10-C2-01 (recipe would break parity on an uppercase scheme).
- P14 public_repo_hygiene: PASS (RFC 5737 and loopback addresses only).
- P16 thresholds_are_explained: PASS (ADV-P10-C2-12 is cosmetic).
- P17 ledger_format_frozen: PASS.
- P18 cross_platform: PASS.
- P19 go_hardening: PASS.
- P20 config_over_code: FINDING ADV-P10-C2-06.
- P21 public_artifact_hygiene: PASS.

## 3. Coverage gaps
- **Not fully read:**
  - The VP-030, VP-021, VP-020, VP-012, VP-019, VP-022, VP-024 and VP-031 bodies (grepped only).
  - `domain-spec/capabilities.md` and `invariants.md`.
  - ARCH-03 outside lines 200-294.
  - error-taxonomy, test-vectors and prd.md (grep only, including the elided long lines prd:493/506).
  - interface-definitions lines 1-242.
- **Python claims I could not verify without running CPython:**
  - The fade product rounding at i=2 for n=8 (0.7 to 49).
  - The `999.995` to `$1000.00` rounding.
  - Oracle-measured items taken as given: depth 992/993, header-limit messages, Host for `%31`, the TE `Chunked␠` bodies.

## 4. Novelty
MEDIUM. The one HIGH is a residue of the pass-9 sanitization fix that never reached the normative step list. The rest are cross-document mis-anchors and sibling-sweep misses.

NOT_CONVERGED

## Perimeter D (S2-S6 BCs)

Findings: 11 (high 3, medium 4, low 3, cosmetic 1).

**Pass 10, Perimeter D: NOT_CONVERGED.** I found 2 HIGH and 4 MEDIUM defects, so the BCs are not ready for story-writing. The worst two are a contradiction about which metrics-server variables the harness puts in each child's environment, and a contradiction about how subagent cases are identified.

## 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P10-D01 | HIGH | Contradiction (harness env) | BC-6.01.002:103-124, CTV :209; BC-6.02.003:141-145, CTV :210; ARCH-07:79-93 | BC-6.01.002's "authoritative exact key sets" add `DGX_SL_*` / `HYLO_*` setting keys only when the case sets them. Its CTV with settings `{}` expects exactly 8 oracle keys, with no `DGX_SL_VM_URL`. BC-6.02.003 says one raw-listener fake serves both sides through `DGX_SL_VM_URL` / `backends[0].metrics_url`, and its CTV row 1 expects `DGX_SL_VM_URL=<fake>` even though the case does not set the metrics URL. The fake's port is assigned at run time, so a case cannot declare it; the harness has to inject it. Under the key-set rule both sides instead query the 192.0.2.10:8428 default, which is the 1.5 s timeout flake that BC-6.02.002 Pre-1 bans. The env-builder test and the case-model test cannot both pass. | product-owner + architect |
| ADV-P10-D02 | HIGH | Contradiction with ARCH (anchoring) | BC-6.01.001:109-112; BC-6.02.003:96-98 and changelog :36; BC-6.03.001:50-52; ARCH-07:179 | The BCs say a subagent case belongs to the `subagent` family of `<family>-<nnn>[-<variant>]`, call "-sub" an older shorthand for it, and state "not a bare id suffix". ARCH-07:179 says the opposite: a subagent case is a base case with the `-sub` suffix (e.g. `row1-003-sub`), "NOT a `<subagent>-<nnn>` spelling". It also claims these three BCs use the suffix. The corpus validator rule that decides which cases get argv `["--subagent"]` cannot be determined. | architect |
| ADV-P10-D03 | HIGH | Partial-fix propagation (ADV-P9-A11); P18 | BC-2.01.005:83-89 and :95-96; BC-2.03.002:81-83, :96-109, EC-006 :127; BC-3.01.001:67-69 | BC-2.01.005 rejects a relative `paths.cache_dir` with `not an absolute path`. This did not reach the sibling BCs: (a) BC-2.03.002 says overrides are "printed as given (not made absolute)", and PC-4/PC-5 define no output for `HYLO_PATHS_CACHE_DIR=rel` (no `cache:` line, stderr text or exit code). (b) BC-3.01.001 PC-3 omits the rule. (c) "The same rule applies to every path value … including `HYLO_CONFIG`" leaves open whether absoluteness applies to `HYLO_CONFIG`; if it does, EC-006 (prints `./c.yaml`) contradicts it. (d) No per-OS absoluteness test is named: on Windows, `\foo` and `C:foo` are not absolute under `filepath.IsAbs`. Two sibling files affected, so HIGH. | product-owner |
| ADV-P10-D04 | MEDIUM | Hermeticity gap (harness) | BC-6.02.002 Pre-3 :97-104 vs EC-005 :152; BC-6.02.003 PC-6 :150-156, PC-7 :159 | The replay seeds one fixed `proc_start` in `statusline-<sid>.json`, for one sid. EC-005 allows `session_id` to change mid-sequence (`/clear`), and PC-7 step `stdin` templates can change it too. A new sid has no seed, so legacy runs the runner's real `ps` (SL:274-280, `os.defpath`) and Go probes the real process tree. When tests run from a Claude Code session, a real `claude` ancestor exists. This breaks "a replay NEVER consults the real process tree". The PC-6 rejection runs only at case load. | product-owner |
| ADV-P10-D05 | MEDIUM | Spec vs consumer / ARCH-06 signature | BC-5.01.001:45, :59-61; legacy SL:226, SL:234; BC-1.05.009:72-75 | `RoundN(x float64, n int) float64` can only return a float. Legacy `round(usd, 4)` runs on any `isinstance(usd,(int,float))`, and Python returns an exact int for int or bool input. Consumer BC-1.05.009 PC-3 requires "an int stays an int (`3` → `3`); `true` → `1`" through `pyfmt.RoundN`. With a float return, `cost-history.json` bytes become `3.0` instead of `3` (seen by swap tests), and ints above 2^53 lose precision. | architect |
| ADV-P10-D06 | MEDIUM | Untestable `<value>` (error surface) | BC-2.02.001:78-82, :95-96, :191-194; BC-2.01.004:194-195; interface-definitions:260-261 | The ascending-pair error names `m_from` "with its own value". With only `HYLO_STATUSLINE_SUBAGENT_TOKENS_K_FROM=2000000` set, `m_from` holds its Float default 1000000, but PC-3 defines `<value>` only as "the raw string as supplied". `1000000`, `1000000.0` and `1e+06` are all possible readings, so the stdout bytes cannot be pinned. PC-6 also drops `[from]` for default-layer values, so stderr never names the variable that caused the error. | product-owner |
| ADV-P10-D07 | MEDIUM | Corpus layout anchoring | BC-6.03.004 CTV :213-216, EC-001 :202; BC-6.03.003:107-108, CTV :150; ARCH-07:178-179 | The example entries use nested paths (`config/ttl-nan`, `transcript/cp-t01`, `cache/sid-slash-temp`). ARCH-07 requires flat `cases/<case-id>/` with ids of the form `<family>-<nnn>[-<variant>]` (families include `cfgerr`, `cpt01`, `cache`). A validator built from ARCH-07 rejects every BC example. | product-owner |
| ADV-P10-D08 | LOW | Legacy citation drift | BC-2.01.005:128-129, :211, :213 | Three wrong line numbers. The fade formula is at SL:682, not SL:683 (SL:683 is the RGB scaling). `184k` is SL:859, not SL:860 (SL:860 is `return str(n)`). For `88.0M`, SL:871 is the `{n / 1000:.0f}k` branch; the `.1f}M` spelling is SL:870. | product-owner |
| ADV-P10-D09 | LOW | CI floor leg mislabelled | BC-6.04.001:66-68 | `go-version: 1.26.x` installs the newest 1.26 patch, not the `go 1.26.0` floor that go.mod declares. With the toolchain line (Pre-2), it can resolve to the same patch as the default legs, so the floor is never tested. | product-owner / architect |
| ADV-P10-D10 | LOW | Unspecified per-OS edge (pending intent verification) | BC-3.01.001:58-65, EC-004 :122 | A relative `HOME`, `LOCALAPPDATA` or `APPDATA` produces a relative `CacheDir`. That is the same cwd-splitting hazard ADV-P9-A11 rejects for `paths.cache_dir` and OD-144 rejects for `XDG_*`. The BC does not say whether to error or accept. | product-owner |
| ADV-P10-D11 | COSMETIC | Notation | BC-5.04.003:74 | PC-1 writes `TimeFloat(ns)`, but the signature is `TimeFloat(t time.Time)`. | product-owner |

## 2. Policy compliance

- **P1** append_only_numbering: PASS.
- **P2** lift_invariants_to_bcs: PASS (DI cross-check not run).
- **P4** semantic_anchoring_integrity: FINDING D02, D07.
- **P5** creators_justify_anchors: PASS.
- **P6** subsystem name: PASS (sampled SS-02..06 frontmatter).
- **P7** H1 = BC-INDEX = PRD title: PASS (6 sampled H1s match BC-INDEX).
- **P12** settled_decisions_are_constraints: PASS (D06 and D10 only ask for undefined bits to be specified; no ruling is challenged).
- **P13** parity_before_behavior_change: FINDING D05.
- **P14** public_repo_hygiene: PASS.
- **P16** thresholds_are_explained: PASS.
- **P18** cross_platform_from_day_one: FINDING D03(d), D10.
- **P19** go_hardening_toolchain: FINDING D09. BC-6.04.001 also has no govulncheck or staticcheck step; whether one is required depends on the policy text.
- **P20** config_over_code: PASS.
- **P21** public_artifact_hygiene: PASS (nothing flagged is quoted).
- **P3, P8, P9, P10, P11, P15, P17**: N.A.

## 3. Coverage gaps and unverified claims

**Not fully read:**
- BC-6.04.001 from line 128, and BC-6.04.002 and BC-6.04.003 from line 118.
- Frontmatter (roughly lines 1-35) of most BCs.
- ARCH-01..06 and ARCH-08; ARCH-07 only in grep fragments.
- prd.md, capabilities.md, invariants.md, VP-INDEX and the cited VP files; prd-supplements only through targeted greps.

**Python claims I could not verify (no execution possible):**
- Git cache key `29de25ac9bde9ad0`.
- Golden A/B/C byte totals and column widths (the mix percentages of golden A row 1 do check out by hand).
- Whether CPython 3.11's C `ntpath._path_normpath` matches pure-Python `ntpath` for `\\?\` paths.
- Linux procps deriving `lstart` from `btime`.
- The mix-cache save value of 994 (taken as settled).
- The MSVC `localtime_s` upper bound; my own arithmetic agrees with 3000-12-31T23:59:59Z.

## 4. Novelty

**MEDIUM.** D01, D02 and D04 are new cross-BC/ARCH contradictions in the SS-06 harness area. D03 is a gap from the pass-9 fix that did not reach its sibling BCs. D05 and D06 are new testability gaps. **NOT_CONVERGED**.
