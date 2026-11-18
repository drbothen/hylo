---
document_type: adversarial-review
phase: 1d
pass: 8
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 88
---

# Adversarial Spec Review — Phase 1d, Pass 8

Pass 8 ran as six fresh-context perimeters, the same split as passes 1-7. Each section is the verbatim final report of one perimeter, unedited except for this framing. NOT_CONVERGED (88 findings: HIGH 12 / MEDIUM 36 / LOW 33 / COSMETIC 7; pass 7 had 114 with 14 HIGH). The orchestrator spot-verified A01, A02, A05, A2-01, A2-05, B01, C2-03 and C2-13 on disk and against CPython 3.11.7; all held. C05 is already ruled by OD-186 (temp-file widened to the rename-retry outcome); the fix is a citation.

## Perimeter A (PRD, supplements, architecture, CI)

Findings: 13 (high 2, medium 6, low 4, cosmetic 1).

Pass 8 of the Phase 1d adversarial review, Perimeter A: 13 findings (2 HIGH, 5 MEDIUM, 4 LOW, 2 COSMETIC). The verdict is NOT_CONVERGED.

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P8-A01 | MEDIUM | Mis-anchor (P4/P5) | prd-supplements/interface-definitions.md:314 | The unit-selector rationale cites "BC-2.01.006 'else `K`'" as the owner of the context-denominator rule. BC-2.01.006 does not exist: S2.01 is BC-2.01.001..005 (prd.md:295-299; BC-INDEX; no file in ss-02). The context-denominator owner is BC-1.02.006, which the same document cites at :200 and :319. Mis-anchors block convergence. | product-owner |
| ADV-P8-A02 | HIGH | Partial-fix propagation (pass-7 CP-T09) | prd.md:484; prd-supplements/nfr-catalog.md:31; architecture/ARCH-07-parity-harness.md:170 | Pass 7 minted CP-T09 (Windows localtime-domain degrade to the 29-byte line), and E-REN-002 now lists it (prd.md:500, error-taxonomy.md:47). (1) The NFR-002 "100% of triggers" list in prd.md and nfr-catalog.md still ends at CP-T01..T07, so the never-blank target omits a live degrade path. (2) The ARCH-07 case-id grammar lists families `cpt01..cpt07` with no `cpt09`, so the corpus validator would reject a Windows CP-T09 parity case. That is 3 files. | product-owner, architect |
| ADV-P8-A03 | HIGH | CI job cannot pass, or checks the wrong thing (P11) | architecture/ARCH-08-build-ci-release.md:79-92; cicd-setup.md:58 | The required `coverage` job runs `go test -count=1 -coverpkg=./internal/... ./internal/...` on ubuntu with a 10-minute timeout. Neither document excludes the Tier A selector, and ARCH-08:60-63 lists the coverage job as having no Python consumer, so it installs no interpreter. BC-6.01.001:116-119 says Tier A with `HYLO_PARITY_PYTHON` unset and `CI=true` FAILS. Once `internal/parity` lands, this required check therefore fails on every run, or hits the 10-minute cap against Tier A's 45-minute budget. If Tier A is instead silently excluded, the "parity exercising statusline counts" premise (ARCH-08:83-85) and the ≥95% gate on `internal/parity` rest on code paths the job never runs. Neither the interpreter wiring nor the exclusion is specified. | architect |
| ADV-P8-A04 | MEDIUM | Contradiction with settled ruling (P12) [owner-question] | ARCH-08:85-90; cicd-setup.md:58, :87, :143-148 vs nfr-catalog.md:70-71, :81-82; module-criticality.md:35-38; prd.md:131-133 | OD-158 gates P1 on ≥95% line coverage for S1 and S5 only. nfr-catalog.md:70-71 says that gate is "the only additional P1 exit gate". ARCH-08 and cicd-setup add `internal/parity` (S6) to the ≥95% gate (pass-7 A09). The PRD and supplements still describe an S1/S5-only gate. Either the owner widens OD-158 or the architecture drops `parity` from the gate. | architect / owner |
| ADV-P8-A05 | MEDIUM | Stale count inside a fail condition (P11) | ARCH-08:141-144 | The coverage-gate positive-coverage rule says it "fails if any of the **three** gated packages is ABSENT", but ARCH-08:85-90 and cicd-setup.md:87 gate **four** packages. An implementer following :142 would not fail when the fourth package is missing or reports `[no statements]`. | architect |
| ADV-P8-A06 | MEDIUM | Partial-fix propagation (pass-6 A12 / pass-7 A08) | cicd-setup.md:52, :112-119 vs ARCH-08:60-63 | The test-job row and lag note 1 still REQUIRE setup-python first and an exported `HYLO_PARITY_PYTHON` on all three test legs. Lag note 1 justifies this with "Tier A runs inside the plain test step", the rationale that pass-6 A12 superseded (Tier A is excluded from that step). ARCH-08:60-63 says the macOS and Windows test legs install no interpreter. The two CI documents give opposite instructions for the same legs. | architect (devops) |
| ADV-P8-A07 | MEDIUM | Partial-fix propagation (pass-7 A03 purity seam) | ARCH-02-configuration.md:46; ARCH-05-platform.md:81 | Pass 7 changed the resolver signatures to take an injected environment: `CacheDir(env EnvVars)`, `StateDir(env)`, `ConfigDir(env)`, `LocalZone(env EnvVars) (*time.Location, error)` (ARCH-05:26, :33). It also ruled that no resolver reads the real environment. ARCH-02:46 still says `CacheDir()/StateDir()/ConfigDir()`, and the ARCH-05 zone Decision (:81) still says `platform.LocalZone()`. These no-argument forms invite direct environment reads in stories. | architect |
| ADV-P8-A08 | MEDIUM | Partial-fix propagation (OD-158 schedule) | ARCH-01-binary-cli.md:156; ARCH-02:154; ARCH-05:19; ARCH-07:20; ARCH-03:42-43 | These lines state kill-rate tiers ("Criticality MEDIUM (>= 80% kill rate)", "HIGH (>= 90%)", "mutation target >= 95%") with no "Phase 6 target, not a P1 gate" qualifier. ARCH-03:21 and ARCH-06:21 carry that qualifier. Story writers may put mutation gates into P1 acceptance criteria. This is label-level drift across 5 files. | architect |
| ADV-P8-A09 | LOW | Owner list incomplete | prd-supplements/test-vectors.md:45 | The OD-156 vector row names BC-1.05.007 and BC-1.05.002 as CP-O10/O11 owners. It omits BC-1.05.005 (EC-011, the history-bearer raise site at SL:255), which error-taxonomy.md:167-168 and ARCH-03:73 name as an owner. | product-owner |
| ADV-P8-A10 | LOW | Cross-document inconsistency | ARCH-07:151 vs ARCH-03:241-244 | ARCH-07 says parity metrics go to "an httptest fake". ARCH-03 rules that metrics test fakes are a raw `net.Listener`, because httptest canonicalises and trims response headers. The parity fake needs the same ruling, or an explicit note that header-sensitive cases are table-test only. | architect |
| ADV-P8-A11 | LOW | Ambiguity | error-taxonomy.md:85; interface-definitions.md:217 | `statusline.cost.percentiles` is one composite key, but its ascending rule is called a "cross-key pair check fired at the second member p95's validation". error-taxonomy.md:119-120 also says the pair checks "are the only cross-key number-range cases". It is unclear whether the D4-EX-3 line names the whole key with its full JSON value, or a member. | product-owner |
| ADV-P8-A12 | LOW | Missing shape spec | interface-definitions.md:122-127 | The Composite-Type grammar lists shape names for Float pair, Float quad, Int map and RGB triples. It gives no name for `Float triple` (`statusline.theme.heat`, :203), so that key's shape-failure reason string (`expected JSON <shape>`) is unspecified. | product-owner |
| ADV-P8-A13 | COSMETIC | Pointer drift | ARCH-00-overview.md:21; ARCH-06-pyfmt.md:190 | ARCH-00 cites the seam set as "prd.md:66", but the seam list is at prd.md:68. ARCH-06's `ValidationWidth` comment says "see 'Two width functions' above", but that section is below the Interfaces block (:214). | architect |

## 2. Policy compliance

- **P1 append_only_numbering:** PASS. CP-T08 is retired and not reused; CP-C06/C07 are reserved; SS-IDs are append-only.
- **P2 lift_invariants_to_bcs:** PASS within the perimeter.
- **P4 semantic_anchoring_integrity:** FINDING A01.
- **P5 creators_justify_anchors:** FINDING A01.
- **P6 subsystem names:** PASS. The ARCH-INDEX registry rule is consistent with PRD §1.6, module-criticality and BC-COMPONENT-MAP.
- **P7 BC H1 is the title source:** PASS. All 154 H1s were compared against the PRD §2 rows with no drift.
- **P9 VP-INDEX is the catalog source:** PASS. 41 VPs; class split 33+7+1; method split 20+13+3+2+1+1+1; per-home mapping sums to 41; 8 dual homes match; module-criticality counts reconcile.
- **P11 ci_positive_coverage_assertion:** FINDING A03, A05, A06.
- **P12 settled_decisions_are_constraints:** FINDING A04 [owner-question].
- **P13 parity_before_behavior_change:** PASS. Exclusions stay within the closed twelve-id set.
- **P14 public_repo_hygiene:** PASS. A grep of the perimeter for private IPs, home paths and personal emails returned no hits.
- **P16 thresholds_are_explained:** PASS.
- **P17 ledger_format_frozen:** PASS.
- **P18 cross_platform_from_day_one:** PASS (signature drift is noted in A07).
- **P19 go_hardening_toolchain:** PASS (gremlins, staticcheck, govulncheck, -race).
- **P20 config_over_code:** PASS. No DGX_* aliases; DGX_* is never read.
- **P21 public_artifact_hygiene:** PASS. Nothing flagged; nothing quoted.
- **P3, P8, P10, P15:** N.A.

## 3. Files not fully read

All files in the perimeter were read in full. Outside the perimeter, only these were opened to check cross-references: VP-INDEX.md, BC-2.01.001.md (PC-6 reserved names), BC-6.01.001.md (unset-interpreter behaviour, via grep only), the H1 lines of all BC files, and legacy/dgx_statusline.py (proxy-bypass check, via grep only).

## 4. Novelty and convergence

Novelty: MEDIUM. A03 (the coverage job versus Tier A's interpreter and timeout) and A04 (the gate scope going beyond OD-158) are new substantive gaps. The rest are propagation residue from pass-6 and pass-7 fixes.

NOT_CONVERGED

## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 19 (high 5, medium 6, low 7, cosmetic 1).

**ADV-P8-A2 (Perimeter A2: brief, L2, VPs, assessments)**

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P8-A2-01 | HIGH | contradiction (BC/OD) | VP-001:54-58 | The statement says the transcript-borne overflows (CP-O06..O08, OD-167) "still degrade the current refresh". OD-156 (log:137) and BC-1.03.018:53-57 rule the opposite: the line is skipped and the refresh renders normally. VP-008:74-77 also calls these rows "not a degrade". Following VP-001, a test author would write degraded-line rows that fail a correct implementation. | architect |
| ADV-P8-A2-02 | MEDIUM | partial-fix propagation | VP-001:37-44, :111-112, :185 | The "closed" trigger catalogue lists CP-T01..T07 and the test families cpt01..cpt07. It omits CP-T09, the Windows MSVC localtime-domain degrade minted in pass 7 (error-taxonomy.md:291; BC-1.01.001:61; BC-1.03.018:47-52). VP-011:53-56 and gene-transfusion:50 were updated to 48 paths; VP-001 was not. As a result no VP has a CP-T09 fault row. | architect |
| ADV-P8-A2-03 | HIGH | statement contradicts BC; rule only in sketch (OD-182) | VP-008:37-40, :74-78 | The statement says "a crash at step k keeps writes 1..k-1 and suppresses all later writes". BC-1.01.009 PC2 (:91-99, VP row :139) has within-step exceptions: the step-7c record_cost write persists when CP-C10 or a history-borne CP-O10/O11 raises in cost_thresholds. OD-167 also makes step 2 skip without degrading. Both appear only in sketch comments, and the sketch puts the history-borne O10/O11 at "7d" where the BC says 7c. | architect |
| ADV-P8-A2-04 | HIGH | rule only in sketch (OD-182); P18 | VP-026:37-53, :96-97 | The statement never states the third LocalToUnix/FromISOFormat outcome: msvcDomain plus ErrLocaltimeDomain (BC-5.04.001:41-55; BC-5.04.002:39-49). VP-026 is the only VP for those BCs. Only the sketch carries `g.MsvcDomain`, and it fails on any `err`, so an expected-sentinel row cannot pass. The CPython goldens are Linux-generated and cannot produce the MSVC domain error, so this rule has no oracle. | architect |
| ADV-P8-A2-05 | HIGH | mis-anchor (P4) | VP-012:109-110, :240-242 (copied from BC-6.03.004:103) | The OD-160 riders "BC-1.02.017 EC-010" and "BC-1.01.008 EC-011" point at the wrong targets. BC-1.02.017 EC-010 is the CP-O05 overflow (:92); its OD-160 rows are EC-004..006 (:86-88). BC-1.01.008 has no EC-011 at all: its rows are EC-001..007 (:75-81), and the OD-160 clause is PC3 (:54-59). A rider test built from these anchors would test the wrong case. | architect (VP-012), product-owner (register) |
| ADV-P8-A2-06 | LOW | label mis-anchor | VP-INDEX:31; VP-012:40 | Both call `TestWindowAge_D4EX1_Windows_AncestorFound` "the OD-160 rider test". It is the D4-EX-1 rider (VP-012:88-90; BC-1.02.017:69-71). | architect |
| ADV-P8-A2-07 | HIGH | BC-routed legs with no VP home (pattern) [process-gap] | BC-4.01.001:106 / VP-004:37-61; BC-2.02.001:233,235 / VP-016:81-90; BC-1.03.018:160 / VP-029:65-67, VP-013:61-62 | Three BC VP-tables send for-all fuzz or property legs to VPs that only define closed tables: (a) all argv/env/stdin with the subagent NDJSON check, sent to VP-004 (unit table, proof_method manual); (b) "for every env map" and "config-error line iff validate exits non-zero", sent to VP-016 (class tables and permutation only); (c) delete-the-line equivalence fuzz, sent to VP-029 and VP-013 (tables only). This is the same class as the earlier pass-3 C2-08 and VP-040/VP-041 splits, recurring. | architect |
| ADV-P8-A2-08 | MEDIUM | contradiction (OD-168) | VP-016:37-42 | The statement says without qualification that "any invalid value renders exactly [config-error line] on stdout". In `--subagent` mode a config error gives zero stdout bytes with the diagnostic on stderr (OD-168; BC-2.02.001 PC-8 :182-188). VP-016 has no subagent leg. | architect |
| ADV-P8-A2-09 | MEDIUM | contradiction (BC); P18 | VP-019:37-42, :84-85 | The statement promises "byte-identical cache files afterwards" with no exclusion carve-out. BC-6.02.004:88,103 compares exclusion-carrying steps (e.g. OD-30 numeric sid) against the entry's expected file. On Windows, D4-EX-1 means Go writes `proc_start` where legacy cannot. A literal implementation of the statement fails on correct output. | architect |
| ADV-P8-A2-10 | MEDIUM | ambiguity / oracle gap | VP-013:37-40, :49-54, :61 | VP-013 places CP-O06..O08 rows in "the 21-row table". BC-1.03.019's 21 rows (H1 :31, :113, re-run 2026-11-15) predate OD-156/OD-167 and contain no CP-O rows (grep: none). The O vectors live in BC-1.03.006/.007/.010. It is unclear whether the table has 21 rows or more, and where the O-row oracle comes from. | architect |
| ADV-P8-A2-11 | MEDIUM | sketch contradicts property | VP-007:90-97 | The sketch computes `e.FreshCopy().NowReads() - first` on a fresh copy that never rendered, not on the copy used by the second render. It also never asserts that the first render read the clock exactly once. So the IM-14 "exactly one clock read" check can never observe a render. | architect |
| ADV-P8-A2-12 | MEDIUM | stale assessment claim (P12) | dtu-assessment.md:53, :54, :93 | The DTU assessment says the ASSUMP-107-1 / 2.x schema capture happens "before Phase 3". OD-192 (log:191) and assumptions-register.md:13 moved it to before the Phase 2 S1.07 stories are written. | architect |
| ADV-P8-A2-13 | LOW | count drift (P2) | invariants.md:46 | DI-008 is stated as cited by 84 BCs. Re-running the stated grep method (ss-0*/) finds 85 files. DI-007 = 38 and DI-012 = 76 verify. | business-analyst |
| ADV-P8-A2-14 | LOW | wording vs settled decision | invariants.md:30; VP-022:75 | Both say "permanent rule". OD-125 (log:86) reads "ADOPTED FOR NOW WITH A REVISIT FLAG", matching owner-validation-list.md:139 and bounded-contexts.md:42. | business-analyst, architect |
| ADV-P8-A2-15 | LOW | incomplete statement | VP-004:37-44 | "Usage errors on non-statusline verbs" does not cover bare `hylo` or an unknown verb (BC-4.01.001 PC-4, EC-004/005, exit 2). It also omits the subagent-mode statusline states. | architect |
| ADV-P8-A2-16 | LOW | within-file propagation | VP-016:166-171 | Named Tests lists two theme legs. The pass-7 `TestTheme_RejectionLines` is missing, although :58-63 and :88-90 say there are three legs. | architect |
| ADV-P8-A2-17 | LOW | stale description | VP-022:68-69 | VP-022 describes BC-1.04.001's client as a "`Proxy: nil` transport". BC-1.04.001:55-56 defines a minimal HTTP/1.1 client over `net.Conn`, and DTU:182 says "no http.Transport". BC-1.04.001:172 carries the same stale residue. | architect, product-owner |
| ADV-P8-A2-18 | LOW | sibling gap (pending intent verification) | VP-011:37-44 | Tier C runs the oracle on Windows (OD-149), but VP-011 does not name the OD-190 Windows-oracle LF normalization that VP-009:43-47 names openly. | architect |
| ADV-P8-A2-19 | COSMETIC | naming | VP-030:125-129 | Named Tests omits `TestMetricsClient_OD181_TransportTable`, which VP-012:245 says is defined in VP-030 (it does appear in the Method section). | architect |

## 2. Policy compliance

- **P1:** PASS. CP-T08 is retired and CP-T09 minted append-only; VP-001..041 are contiguous.
- **P2:** FINDING A2-13. Otherwise the DIs not covered in P1 carry explicit OD-115 deferrals.
- **P4:** FINDING A2-05, A2-06, A2-17.
- **P5:** PASS.
- **P6:** PASS. Feasibility and gene-transfusion names match the ARCH-INDEX registry rows SS-01..06.
- **P9:** PASS. The VP-INDEX catalog matches the 41 files. I re-summed the `bcs:` edges myself: 261, matching the index. Class and method totals check out.
- **P11:** PASS. VP-001/009/010/011/012/035/036 all assert non-zero counts. VP-007's sketch defect is A2-11.
- **P12:** FINDING A2-01 (OD-156), A2-08 (OD-168), A2-12 (OD-192), A2-14 (OD-125).
- **P13:** PASS.
- **P14:** PASS.
- **P16:** PASS. The OD-191 100 ms and OD-188 thresholds are labeled.
- **P17:** PASS. EVT-01..13 are frozen.
- **P18:** FINDING A2-02, A2-04, A2-09.
- **P19:** PASS. VP-037 runs the race legs with CGO_ENABLED=1.
- **P20:** PASS. VP-018 and VP-031 caps and retries are config keys.
- **P21:** PASS. No flagged strings in the perimeter; DTU uses an RFC 5737 address.
- **P3, P7, P8, P10, P15:** N.A.

## 3. Files not fully read

- VP-031 from line 98, VP-032 and VP-033 lifecycle tails, VP-034 sketch from line 119, VP-035/036/037 lifecycle tails, VP-039 from line 139, VP-040 from line 139, VP-041 from line 99.
- Frontmatter of VP-003..VP-041 was read only via a `bcs:` grep.

## 4. Novelty

MEDIUM-HIGH. A2-01, A2-03, A2-04, A2-05, A2-07, A2-09 and A2-10 are new statement-level contradictions or mis-anchors, not rewording of earlier findings.

**NOT_CONVERGED**

## Perimeter B (BC-1.01, BC-1.02)

Findings: 11 (high 1, medium 4, low 4, cosmetic 2).

**Pass 8, Perimeter B: status line contracts BC-1.01.\* and BC-1.02.\***

Not converged. I found one HIGH finding, four MEDIUM, four LOW and two COSMETIC.

The main problem is BC-1.02.030: it uses the wrong config key as the reroute-all trigger, so a test written from it fails against the default config.

Apart from these findings, the contracts held up against the legacy code. I checked the postconditions against the lines they cite, recomputed the heat colours, the half-even rounding cases, the floor-division countdown and duration strings, and the overflow boundary at 2\*\*1024 − 2\*\*970. Titles match across each file's H1, BC-INDEX and the PRD for all 40 contracts.

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P8-B01 | HIGH | Mis-anchoring; partial-fix regression [process-gap] | BC-1.02.030:54, :89 (EC-007), :92 (EC-010), :139 (config keys row); legacy SL:487-489 | Reroute-all depends on the configured model prefix list: `any(p.rstrip("*") in (…) for p in prefixes)`. BC-1.02.009 PC1 says the same. BC-1.02.030 instead says the marker key `statusline.lane.reroute_all_prefixes` "contains bare `claude`" — but it contains that by default. Under default config (`model_prefixes=claude-sonnet`), EC-010's input `{"five_hour":"x"}` degrades in legacy, while the contract says nothing raises. The config keys row also leaves out `backends[0].model_prefixes`. The pass-7 respelling (ADV-P7-B06) swapped key names without checking what they mean. | product-owner |
| ADV-P8-B02 | MEDIUM | Contradiction across contracts and config range | BC-1.01.007:40-42 (Description), :52 (PC2), :59 (Inv 1); legacy SL:1224 | Legacy shows row 2 when `rows > 2 or cols == 0 or cols >= NARROW_COLS`. `narrow_cols` is registered as "any Int", and negative values are explicitly admitted (interface-definitions:167). Example: `narrow_cols=-10`, `COLUMNS=-5`, `rows=2`: legacy shows row 2, and BC-1.01.003 PC1 agrees. BC-1.01.007 PC2 still says row 2 is omitted for any negative COLUMNS, without conditioning on `narrow_cols`. VP-040 P7 has the same gap. | product-owner |
| ADV-P8-B03 | MEDIUM | Contradiction; P20 anchoring | BC-1.01.003:91-93 vs BC-1.04.004:45-50, interface-definitions:193 | BC-1.01.003 says the `?` in the dead marker `◌ DGX ?` comes from `statusline.pill.label_unknown`. BC-1.04.004, which owns that rung, builds it as `label_local + " ?"`, a literal. The registry lists only BC-1.02.001 as consumer of `label_unknown`. With a non-default `label_unknown`, the two contracts predict different rows. | product-owner |
| ADV-P8-B04 | MEDIUM | Settled decision not propagated (P12, P18) | BC-1.01.008:37-38, :45, :117 (Decisions row) | OD-183 requires BC-1.01.008 to state three things: hylo reads and writes UTF-8 on every OS; the Windows oracle gets `PYTHONIOENCODING=utf-8`; and a table test shows that variable changes stdio encoding only. The contract mentions none of them and cites OD-183 only for WTF-8 iteration. It pins parity to `LANG=en_US.UTF-8`, which BC-1.02.004:60-62 says has no effect on Windows. OD-190 (the Windows oracle's LF normalization) is not cited either. | product-owner |
| ADV-P8-B05 | MEDIUM | Config range mismatch (P20) | BC-1.02.014:83-84 (Inv 3), BC-1.02.025:70-71 (Inv 3) vs interface-definitions:201-202 | Both contracts give the range of `statusline.units.lines` / `units.tokens` as {`k`/`M`}. The registry gives defaults `k` and `M`, ranges {`k`} and {`M`}. Whether `HYLO_STATUSLINE_UNITS_TOKENS=k/M` should be accepted or rejected cannot be decided from the specs. | architect, product-owner |
| ADV-P8-B06 | LOW | Wrong claim in an excluded path (OD-160) | BC-1.01.009:70 (step 7c) vs :90-99 (PC2); legacy SL:228-229, 237 | Step 7c says CP-C09 and CP-C10 both fault after the `record_cost` write. For CP-C09's non-object top level or `sessions` value, `h.setdefault` / `s.get` raise before `save_cache` (SL:237), so nothing is written. PC2 itself lists only CP-C10 as the within-step exception. | product-owner |
| ADV-P8-B07 | LOW | Inexact edge case | BC-1.01.009:115 (EC-001); legacy SL:1035-1036, 1055-1057 | The mix-cache write condition "file has grown since the cached offset" is inexact. A shrunk transcript (`size < off`) resets and saves. A grown file with no complete new line returns without saving. | product-owner |
| ADV-P8-B08 | LOW | Sibling not updated (pending intent verification) | BC-1.02.012:61 (`->`), BC-1.02.016:53 (`·`), BC-1.02.007:55 (` <1%`) | Pass 7 added a "named format constant, not config" rationale (D15) for the `?` in BC-1.02.002 Inv 3. These sibling display literals have neither a config key nor that rationale. | product-owner |
| ADV-P8-B09 | LOW | Ambiguous property | BC-1.02.006:147; VP-041 P-o (line 64-66) | The width formula `10 + 1 + len(number text) + len(denominator text)` doesn't say whether the trailing `%` (PC7) counts. If "number text" means `F(pct,0)` alone, the formula is one short. | product-owner (architect for VP-041) |
| ADV-P8-B10 | COSMETIC | Stale line cite | BC-1.02.011:89 (EC-011), BC-1.02.012:88 (EC-013) | For the canonical vector (5h window absent), the widget is dropped by the SL:510 `any(...)` check, not "hidden at SL:513-514". The outcome is the same. | product-owner |
| ADV-P8-B11 | COSMETIC | Anchor and tag drift | BC-1.02.017:91 (EC-007); BC-1.01.009:141 vs :175-177 | EC-007 has no inline OD-160 tag, while the same case in BC-1.02.028 EC-005 has one (Inv 3 covers it). BC-1.01.009's VP table lists VP-022, but its VP Anchors section leaves it out. | product-owner |

## 2. Policy compliance
- P1 append-only numbering: PASS
- P2 lift invariants to BCs: PASS (DI-007, DI-008 and DI-012 are cited where needed)
- P4 semantic anchoring: FINDING B01, B03
- P5 creators justify anchors: PASS
- P6 subsystem name per ARCH-INDEX: PASS (SS-01)
- P7 H1 = BC-INDEX = PRD title: PASS (all 40 match and describe their postconditions)
- P12 settled decisions are constraints: FINDING B04
- P13 parity before behavior change: PASS
- P14 public repo hygiene: PASS (no IPs, home paths or user names in the perimeter)
- P16 thresholds are explained: PASS
- P17 ledger format frozen: PASS (nothing in the perimeter reads the ledger)
- P18 cross-platform from day one: FINDING B04
- P19 Go hardening toolchain: N.A.
- P20 config over code: FINDING B05; B08 (LOW)
- P21 public artifact hygiene: PASS

## 3. Not fully read / not verified
- **Read in full:** all 40 contracts' bodies (frontmatter fields checked by search) and legacy SL:1-1246.
- **Read only in part:** VP-041 (lines 1-105), VP-040 (property list only), VP-022 (by search), ARCH-03 (lines 46-110 plus anchors), error-taxonomy, interface-definitions (lines 160-273), capabilities.md, invariants.md, test-vectors.md, and the prd.md tables.
- **Python claims I could not verify** (no execution available):
  - the SHA-1 cache keys in BC-1.02.005 (`5a3006e969bd95e3`, `09d4733efe0f2c7f`, `a77db2f8cb13007e`);
  - the golden-A byte totals 701, 809, 642, 286 and 743. The first four are consistent when rebuilt from segment byte widths; 743 is not checked;
  - the exact decimal digits printed for 2\*\*1024 − 2\*\*970;
  - the `ntpath` results for `//`, `///` and `//x`, which depend on the 3.11.7 `splitdrive` version;
  - the `_hm` strings for 1e24 and 5e23 (plausible given float spacing);
  - the 993/994 nesting depth measurement.

## 4. Novelty
Novelty MEDIUM. B01 is a regression introduced by a pass-7 fix, and B02–B05 are cross-document contradictions no earlier pass reported.

**NOT_CONVERGED**

## Perimeter C (BC-1.03, BC-1.06, BC-1.07)

Findings: 6 (high 1, medium 2, low 2, cosmetic 1).

**ADV-P8-C: status line BCs (BC-1.03.*, BC-1.06.*, BC-1.07.*): 6 findings, NOT_CONVERGED**

Most of the perimeter checks out against legacy. I recomputed by hand every pinned byte count and cache golden I opened, and they all agree with legacy:
- BC-1.03.002–.011, .016, .017, .019 (all 21 rows), .020 and .021, including the CP-O06/O07/O08 turn-drop legs.
- The `ensure_ascii` wire forms in BC-1.07.004–.006.
- Titles match across H1, BC-INDEX and PRD.
- The config keys in the perimeter are registered with ranges that match their BCs.

The six findings below are what remains.

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P8-C01 | MEDIUM | test-vector contradiction | BC-1.07.007:122 | **Wire-form vector mixes notations.** The `tokenCount=Infinity` expected content uses `\u001b` wire escapes but writes the check mark and the middle-dot joiner as raw characters. BC-1.07.004 PC3 and Inv2 say the wire is pure ASCII, so these must be `\u2714` and `\u00b7`. A test copied literally from this row would expect raw UTF-8 that legacy never emits. Row :114 also uses `\e` without the byte-notation note that BC-1.07.001:33 carries. | product-owner |
| ADV-P8-C02 | MEDIUM | missing edge case / cross-doc contradiction | BC-1.03.021 PC5 and VP row :88; BC-1.03.010 PC2 :71; ARCH-03:168; BC-5.02.006:92 | **Mix-cache save failure is reachable from the transcript, but two docs say it is not.** ARCH-03 and BC-5.02.006 call the mix-cache save a "flat payload — unreachable from input". But `cur.id` (SL:1078, a raw `message.id`) and `cur.out` (SL:1079, a raw value) are written back verbatim (SL:1153). Example: a timed assistant line with no usage, whose `message.id` is an array nested so the line's total depth is 992–993. The 993 transcript decode budget accepts it (BC-1.03.004 EC-009). It is saved at the same total depth, which exceeds the 991 mix save budget. Legacy's `json.dump` then raises `RecursionError`, `save_cache` swallows it (SL:205-206), nothing is written, a temp file is leaked, and this repeats every refresh while the turn stays open. No BC pins this, and the VP-029 "round-trips verbatim for any JSON value" property is false above 991. Derived from the documented budgets; I did not run the oracle. | architect + product-owner |
| ADV-P8-C03 | HIGH | partial-fix sibling gap (VP / exclusion reciprocity) | BC-1.03.014:90-91, :97-98; BC-1.03.016:73, :108; BC-1.03.018:113-116, :172; BC-1.03.002:87-88; BC-1.03.005:65-69 | **D4-EX-2 vectors are left out of the closure list and VP coverage.** BC-1.03.014's single-line CP-T06 rows (hylo cache with `"size"` 70 / 81) and BC-1.03.016 row T15 both trigger the D4-EX-2 skip and carry hylo-only expectations. BC-1.03.018's list of dedicated tests (PC5 / :172) does not include them, and VP-013 and VP-012 do not list BC-1.03.014 or BC-1.03.016. ADV-P6-C06 added VP-013/VP-012 only to the siblings .006/.007/.010. Separately, the OD-160 foreign-cache legs in BC-1.03.002 (EC-008/009) and BC-1.03.005 (PC5) cite no VP-012, while their siblings BC-1.03.015 (OD-161) and BC-1.06.001 (OD-159) do. This affects 4 files, so it rates HIGH under the partial-fix rule. | product-owner |
| ADV-P8-C04 | LOW | legacy claim likely wrong | BC-1.07.008:89 (EC-009) | **The "legacy exits 1" contrast is probably inaccurate.** It says a broken pipe while printing rows reaches the guard and the process exits 1. With stdout a pipe, CPython block-buffers 8 KiB, so `print(...)` (SL:935) does not raise and the guard is never entered. The broken pipe instead shows up when stdout is flushed at shutdown ("Exception ignored", exit status 120). This changes the deviation note only, not hylo's ruled behavior (OD-172). I reasoned this from CPython's buffering behavior and did not run it. | product-owner |
| ADV-P8-C05 | LOW | parity gap [owner-question] | BC-1.06.001:120 (EC-009) vs SL:198-206 | **The Windows rename retry has no exclusion id.** Legacy tries `os.replace` once and swallows the error. hylo retries `1 + rename_retry_limit` times (OD-186/OD-188), so a retry that succeeds persists a cache file legacy would not have written. That is a difference in file content, not just in the directory listing. None of the 12 closed exclusion ids names it; `temp-file` covers listings only. Should `temp-file` be extended, or is this a separately ruled deviation? | product-owner / owner |
| ADV-P8-C06 | COSMETIC | inconsistency | BC-1.03.018:100 (and error-taxonomy:206) vs BC-1.03.010:108 | CP-O08 lists "SL:994, 996" as raise sites. BC-1.03.010 EC-009 itself shows SL:996 can never raise at these magnitudes, because `stale_factor × out` at SL:994 raises first. | product-owner |

## 2. Policy compliance

- **P1** append-only numbering: PASS.
- **P2** lift invariants to BCs: PASS (DI-007/008/012 are cited consistently).
- **P4** semantic anchoring integrity: FINDING C03 (missing VP-013/VP-012 anchors); C02 (VP-029 round-trip anchor overclaims).
- **P5** creators justify anchors: PASS.
- **P6** subsystem name: PASS (all SS-01).
- **P7** H1 = BC-INDEX = PRD title: PASS (all 31 match).
- **P12** settled decisions: PASS (C05 is raised as an owner question).
- **P13** parity before behavior change: PASS, with C05 open.
- **P14** public-repo hygiene: PASS (synthetic data only; the oracle interpreter path is a system path, not a home path).
- **P16** thresholds explained: PASS (T-054 to T-061 and the subagent thresholds all carry rationales).
- **P17** ledger format frozen: N.A. (no ledger in the perimeter).
- **P18** cross-platform: PASS (the Windows legs that were not executed are flagged under ASM-005).
- **P19** Go hardening toolchain: N.A.
- **P20** config over code: PASS (keys registered; ranges match BC-1.03.003/005/007/009/010 and BC-1.07.002/004/005/007, plus `rename_retry_limit`).
- **P21** public-artifact hygiene: PASS.

## 3. Not fully read / not verified

- **Read only in part:** frontmatter of BC-1.03.003–.021 (checked by grep for version, subsystem, capability, parity class); BC-1.01.001 (EC-004/005 only); ARCH-03 (lines 111–306); interface-definitions (grep hits only).
- **Not read:** ARCH-04; domain-spec/capabilities.md; prd-supplements/test-vectors.md; the VP bodies (I checked their `bcs:` lists only); the owner-decisions log.
- **Python claims I could not verify by running anything:**
  - the 993 transcript decode / 991 mix save depth budgets (C02 depends on them);
  - the NaN shared-object identity for dedup;
  - `seek(negative)` raising `OSError` rather than `ValueError`;
  - the exit code on a broken pipe (C04);
  - the exact digit counts inside the 10^309 golden strings.

## 4. Novelty

MEDIUM. C02 (a reachable mix-save failure that two docs call unreachable) and C03 (the sibling reciprocity gaps) are new kinds of finding; C01 is a recurrence of the escape-notation problem from adv-p3 C01.

NOT_CONVERGED

## Perimeter C2 (BC-1.04, BC-1.05)

Findings: 15 (high 1, medium 8, low 6, cosmetic 0).

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P8-C2-01 | HIGH | P20 config-over-code / partial-fix sibling | BC-1.04.005:54, BC-1.04.007:61-63, BC-1.04.008:53, BC-1.04.010:52-53, BC-1.04.011:51, BC-1.04.012:57, BC-1.04.017:52, BC-1.04.018:51, BC-1.05.003:69-71 (registry: BC-2.01.004:137-147) | BC-2.01.004 PC-6 names these BCs as the consumers of the registered glyph keys (`telemetry_dot`, `cell_on`/`cell_off`, `box_rate`, `ttft`, `watts`, `idle`, `sess_rate`, `host`, `cost_pick`). Yet every one of their postconditions hard-codes the default glyph literal and never names the key. Only BC-1.04.004:45-50 got the OD-189 "closing the P20 gap" treatment. An implementer working from these BCs would hard-code ◉ ◔ ⚡ ☾ ▣ » ↺ ▰ ▱ ⛏. Blast radius is 11 BCs. | product-owner |
| ADV-P8-C2-02 | MEDIUM | Spec gap (urllib quirk) | BC-1.04.001:93-96, 161-164; legacy SL:168-171 | urllib's `http_error_302` drains the body of a 3xx it decides to follow (`fp.read(); fp.close()`) before it opens the next hop. That read uses the same http.client framing, so an IncompleteRead, a bad chunk, or a no-length body held open until the timeout raises and gives no sample. The BC covers only "never parse the refused 3xx body". It does not say a followed 3xx body must be drained under the PC1 ladder, or that a drain failure gives no sample. A hylo that skips straight to the next hop gets a sample where legacy gets none. | product-owner |
| ADV-P8-C2-03 | MEDIUM | Ambiguity at the parity edge | BC-1.04.001:82-84 | Chunked framing is described only as "`Transfer-Encoding: chunked` (case-insensitive)". CPython 3.11 `HTTPResponse.begin` tests `tr_enc.lower() == "chunked"`, an exact equality on the compat32 value. compat32 keeps trailing whitespace, so `chunked␠` and `gzip, chunked` are NOT chunked: the body falls to Content-Length/EOF, the chunk-size lines reach `json.loads`, and there is no sample. A Go EqualFold/TrimSpace/contains check yields a sample. VP-030's Tier C oracle varies header values, so this case is reachable. | product-owner |
| ADV-P8-C2-04 | MEDIUM | Invariant incomplete [process-gap] | BC-1.04.002:76-86; legacy SL:335, SL:356 | Invariant 1 claims to list every typed crash site but misses two. (a) A TypeError at SL:356 (`now - c.get("ts", 0)` on the fetch-failure path when `ts` is a string or null); SL:325 covers only the cached path. (b) A TypeError at the SL:335 comprehension when `hist` is not iterable (null or a number) on the success path. This is the fourth consecutive pass patching this one invariant (P5-C2-09, P6-C2-09, P7-C2-06). | product-owner |
| ADV-P8-C2-05 | MEDIUM | P2 lift_invariants / sibling propagation | BC-1.04.003:131; BC-1.05.005:135 | Both BCs specify degraded-line outcomes: BC-1.04.003 EC-008/EC-009 (KeyError/IndexError) and BC-1.05.005 EC-011 (CP-O10/O11 OverflowError). Their L2 rows cite only DI-007 and DI-012, not DI-008. ADV-P6-C2-10 lifted DI-008 into BC-1.05.002/.007 for the same degrade class, but these two siblings were not updated. | product-owner |
| ADV-P8-C2-06 | MEDIUM | VP contradiction with BC | VP-020:55-58 vs BC-1.05.004 PC1 (:72-76), BC-1.05.002 PC5/EC-009 | VP-020 says "an unconvertible `api_ms` renders normally". That holds only for a negative huge value. A positive huge `api_ms` passes the gate and degrades (CP-O11), as BC-1.05.004 PC1 explicitly states. VP-020 also attributes the `usd` degrade to "the $/h display math". CP-O10 actually fires at the `.2f` format (SL:616), before SL:622. | architect |
| ADV-P8-C2-07 | MEDIUM | P4 semantic anchoring | BC-1.05.009:121; BC-1.05.004:133; BC-1.05.006:121 | (a) BC-1.05.009 routes "`pyfmt.Dumps` equals CPython `json.dumps` … fuzz (differential)" to VP-020/VP-019. VP-020 is a poisoned-file unit table and VP-019 is swap parity; neither has a fuzz leg. The owning VP is VP-024 (pyfmt JSON equivalence), whose `bcs:` omits BC-1.05.009. (b) BC-1.05.004 and BC-1.05.006 route "Go property test (testing/quick)" rows to VP-020, whose method is unit/table only. This is the ADV-P3-C2-08 class (fixed for VP-030 only). | architect |
| ADV-P8-C2-08 | MEDIUM | VP leg coverage gap | VP-030:62-66, :92 vs BC-1.04.003:120, BC-1.04.008:89, BC-1.04.015:89, BC-1.04.018:88, BC-1.04.019:80 | VP-030's testing/quick leg lists only BC-1.04.002/004/006/007/009/013/017/021. Five other BCs route "Go property test (testing/quick)" rows to VP-030 (and VP-031, which has no quick leg). Those properties have no owning harness. | architect |
| ADV-P8-C2-09 | MEDIUM | Partial-fix regression (ADV-P7-C2-04) | VP-030:72-73 vs BC-1.04.001:55-58 | VP-030 still says the transport table "pins hylo's plain-http client behaviour". BC-1.04.001 PC1 now says the client handles https through crypto/tls, and that only the parity CORPUS is plain http. Blast radius is 1 file. | architect |
| ADV-P8-C2-10 | LOW | Mis-anchor (stale label) | BC-1.04.001:292 | The BC cites ARCH-03 "`MetricsClient` interface at line 183, `telemetry.go` … at line 235". The actual lines are 187 and 266. This label was already corrected once (ADV-P7-C2-09) and has drifted again. | product-owner |
| ADV-P8-C2-11 | LOW | Cross-doc contradiction | test-vectors.md:14, :45 vs BC-1.04.004:95 | test-vectors says "BC-1.04.004 carries the CP-N03 invariant with no vector row of its own". BC-1.04.004 does have a CP-N03 canonical vector row (`{5: 1.0}` → degraded). | product-owner |
| ADV-P8-C2-12 | LOW | Arch/BC inconsistency | ARCH-03:193-195; ARCH-03:211-212 | (a) ARCH-03 lists the request headers as "GET, Host, User-Agent, Accept-Encoding: identity, Connection: close, in urllib's order". BC-1.04.001:59-61 pins Accept-Encoding first (putrequest emits it before the dict), and the oracle confirms that. (b) ARCH-03 puts "non-http(s) schemes" in OD-181's scope. A non-http(s) configured metrics URL is the D4-EX-3 URL class (BC-2.02.005; BC-1.04.001:302), and BC-1.04.001's OD-181 VP-012 row scopes OD-181 to redirect targets and TLS only. | architect |
| ADV-P8-C2-13 | LOW | Spec gap (http.client limits) | BC-1.04.001:79-81 | "Parsed exactly as http.client does" is the only rule, but these http.client behaviours are observable and none is pinned: more than 100 header lines (`_MAXHEADERS`) raises HTTPException (no sample); a header line over 65536 bytes raises LineTooLong; an interim `100 Continue` is skipped and the next status line is read. A minimal client could diverge on any of them. | product-owner |
| ADV-P8-C2-14 | LOW | Ambiguity | BC-1.05.006:89-90 vs PC1:65-69 | For sid `true` the cost-history key is the JSON spelling `"true"`, but the session-cache file name is Python `str()`, giving `statusline-True.json`. Invariant 2 shows only the `777` example. An implementer who reuses the str_form helper would write `statusline-true.json`. The two names differ on Linux but are the same file on case-insensitive filesystems. | product-owner |
| ADV-P8-C2-15 | LOW | Test-vector underspecified | BC-1.05.008:53-69 | Precondition 3 gives defaults for `ts`, `src` and `api_ms` but not `lane`. The g13/g14/g15/g17-g20 rows and `sess-self` carry no lane, which the committed seed file needs. Anth is only implied by the "Counts" columns. | product-owner |

Re-derived without discrepancy: BC-1.04.020's 11-step table (every tuple, row byte and cache byte); BC-1.04.009 glyphs and fades; BC-1.04.007/015 cell math; BC-1.04.017 age text; BC-1.04.019 ties; BC-1.05.005 indices, EC-009 NaN sort orders and canonical rates; BC-1.05.008 thresholds (24,30)/(20,26) and all golden rows; BC-1.05.002/007 rates; BC-1.05.003 ⛏ values; the urllib redirect keying and the 37-hop bound.

## 2. Policy compliance

- **P1** append_only_numbering: PASS (BC-1.04.013 EC-010 renumbered correctly; no suffixed ids).
- **P2** lift_invariants_to_bcs: FINDING ADV-P8-C2-05.
- **P4** semantic_anchoring_integrity: FINDINGS ADV-P8-C2-07, -08, -10.
- **P5** creators_justify_anchors: PASS.
- **P6** subsystem name: PASS (30/30 `"SS-01"`, matching the ARCH-INDEX rule).
- **P7** BC H1 = BC-INDEX = PRD title: PASS (30/30 identical).
- **P12** settled_decisions_are_constraints: PASS.
- **P13** parity_before_behavior_change: PASS (deviations limited to the closed set: OD-30, OD-160, OD-166, OD-181, D4-EX-3).
- **P14** public_repo_hygiene: PASS (RFC 5737 addresses only).
- **P16** thresholds_are_explained: PASS.
- **P17** ledger_format_frozen: PASS.
- **P18** cross_platform_from_day_one: PASS (ADV-P8-C2-14 is a minor per-filesystem note).
- **P19** go_hardening_toolchain: N.A. in this perimeter.
- **P20** config_over_code: FINDING ADV-P8-C2-01.
- **P21** public_artifact_hygiene: PASS.

## 3. Coverage and unverified claims

**Read fully:** all 30 BCs, plus VP-020, VP-030 and VP-031.

**Read only in part:** BC-INDEX and prd.md (rows only); interface-definitions (key rows only); error-taxonomy (the CP rows I needed); ARCH-03 lines 140-273; ARCH-04 lines 25-104; invariants.md; BC-2.01.004 lines 108-147; VP-019 and VP-021 (grep only); legacy SL:60-380, 575-890, 1000-1021 and 1160-1246.

**Not read:** VP-001, VP-012, VP-022, VP-024; BC-5.02.003 beyond grep; BC-1.06.001 beyond grep.

**Python claims I could not execute** (checked from memory of the CPython 3.11 source or by hand reasoning only):
- The `tr_enc.lower() == "chunked"` exact match, the `_MAXHEADERS` = 100 header limit, and the 100-Continue skip.
- The redirect body drain order (`fp.read()` happens after the `visited` increment).
- The json depth result 992/993.
- The byte-for-byte urllib header order (I re-derived it from the source and it agrees with the BC).
- The binary value of 999.995 (derived by hand: just above the tie).

## 4. Novelty

Novelty: MEDIUM. ADV-P8-C2-02, -03 and -13 are genuinely new parity edges in the metrics client. The rest are sibling propagation from earlier fixes and anchor or VP-leg drift.

**NOT_CONVERGED**

## Perimeter D (S2-S6 BCs)

Findings: 24 (high 2, medium 10, low 10, cosmetic 2).

## Adversarial Review: Pass 8, Perimeter D (SS-02..SS-06 BCs)

### 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P8-D01 | HIGH | Partial-fix sibling / signature drift (P18) | BC-3.01.001:59-60, 62-64; BC-2.03.002:73, 76, 78; ARCH-02:46 | Pass-7 D12 changed only `CacheDir`/`LocalZone` to take `(env EnvVars)`. `ConfigDir()` and `StateDir()` still take no env. That contradicts the BC's own Pre-2 and Inv 3 (no platform function reads the real environment) and ARCH-05:26 (`ConfigDir(env EnvVars)`, `StateDir(env EnvVars)`). EC-004 requires these functions to return an error, but no signature shows one. BC-2.03.002 still calls the bare forms. The stale form appears in 3 files. [process-gap] (a sibling sweep was skipped again) | product-owner, architect |
| ADV-P8-D02 | HIGH | Same-document mis-anchor | BC-5.04.002:87-88 vs :44-50; ARCH-05:34 | Inv 2 says the Windows localtime-domain "rule [is] in `internal/platform`, table-tested". The Description says the rule lives in pure pyfmt (`ErrLocaltimeDomain`, no platform import). ARCH-05:34 says platform "no longer hosts the conversion". | product-owner |
| ADV-P8-D03 | MEDIUM | Legacy mismatch / mis-anchor | BC-5.02.003:49-55; legacy SL:192-193, 930, 1202 | Pre-1 calls the stdin decode and the cache loaders line-splitting sites, with the metrics reply as "the one whole-input exception". Legacy actually reads both whole: `json.load(sys.stdin)` and `json.load(fh)`. This also contradicts BC-1.01.002:182 ("read stdin fully") and ARCH-06:31 (ModeText). A port that splits pretty-printed stdin into lines would diverge from legacy. | product-owner |
| ADV-P8-D04 | MEDIUM | Contradiction / missing rule | BC-2.01.005:69, 136-140; BC-2.01.004:192-196; BC-2.02.001:116, 125 | PC-2 says List "items are not otherwise validated in P1", yet `reroute_all_prefixes` validates each entry. BC-2.02.001 says BC-2.01.005 raises the Text-class `control character` reason (for `subagent.joiner` and List entries), but BC-2.01.005 PC-6 has no such rule. BC-2.01.004 PC-9 states the entry range but not its reason string. A failing test for a control byte in the joiner cannot be derived from its owning BC. | product-owner |
| ADV-P8-D05 | MEDIUM | Count drift / mis-anchor | BC-2.01.005:140; BC-2.02.001:140-144 vs table :120-125; BC-2.02.003:57-70 | Three wrong statements about the Text-class reasons: (1) BC-2.01.005 says "all three reason strings", but PC-6 lists four. (2) BC-2.02.001 says "the five `expected ...` reasons", but its table lists six, since pass-7 D02 split the glyph reason in two. (3) BC-2.02.001 says Text reasons are minted in BC-2.02.003, which mints only number-grammar reasons. | product-owner |
| ADV-P8-D06 | MEDIUM | Partial-fix propagation | interface-definitions.md:203, 237 vs BC-2.01.005:153-157 | interface-definitions still gives `limits.windows` as Default/range `5h/7d` and `theme.heat` as `0.22/0.85/0.80`. Pass-7 D01 made each registry Default a single value equal to its env spelling: `5h,7d` and `[0.22,0.85,0.80]`. The slash spelling is now a shape error. | product-owner |
| ADV-P8-D07 | MEDIUM | P7: H1 does not describe the postconditions | BC-2.01.005:40, 44, 52-53 | The H1, the Description ("non-numeric shared types") and Pre-1 ("type `Bool`, `List` or `Path`") leave out PC-5 (composite strict JSON), PC-6 (Text) and PC-7 (default-only keys). That is most of the contract. | product-owner |
| ADV-P8-D08 | MEDIUM | Untestable rule (D15 golden) | BC-2.01.004:104-110, 241-254; BC-3.01.001:98-101 | PC-3(f) fails the build when any default differs from legacy, "except the two documented exceptions". PC-11 registers `cache.rename_retry_delay_ms` and `_limit`, which have no legacy value (legacy `save_cache` SL:198-206 never retries). Check (f) is undefined for them, and BC-3.01.001 Inv 1 ("every other P1 default equals legacy") is false. | product-owner |
| ADV-P8-D09 | MEDIUM | BC vs ARCH contradiction | BC-3.02.001:91-99 vs ARCH-05:30 | After a PID-reuse guard rejection, the BC says the walk keeps climbing to the depth cap and accepts no later match. ARCH-05 says the walk terminates and never continues upward. The final result is None either way, but probe counts differ, and so does the mandated table leg "rejection then clean climb to depth cap". | architect, product-owner |
| ADV-P8-D10 | MEDIUM | Internal contradiction (exclusion closure) | BC-3.02.002:48-54, 58-62, 102-106, 124-125; BC-6.02.003:168-174 | The PC preamble and the VP row treat D1-D4 as corpus cases under exclusion `OD-76`. The CTV note says all D1-D4 vectors run as Go table tests only, never as corpus cases. BC-6.02.003 PC-8 says only that the parity half has "no D1 case". It is unclear whether D2-D4 (which work under UTC) are corpus cases, and whether the conditional fake-`PATH` machinery (BC-6.01.002:91-96) has any consumer. | product-owner |
| ADV-P8-D11 | MEDIUM | Title sync | BC-ALLOCATION.md:267 vs BC-3.01.001:35, BC-INDEX:231, prd:325 | The allocation title predates the pass-5 LocalZone retitle ("...; hylo cache dir from P1 (XDG/hylo, LOCALAPPDATA)"). | product-owner |
| ADV-P8-D12 | MEDIUM | Interface signature drift | BC-4.01.001:46, 51 vs ARCH-01:26, 44-45, 61-63 | The BC writes `run(os.Args[1:], stdin, stdout, stderr)` and `runStatusline(args[1:], ...)`. ARCH-01 has `run(args, env EnvVars, ...)`, and `runStatusline(env, stdin, stdout, stderr)` takes no args because the unknown-flag scan runs in `run`. | product-owner |
| ADV-P8-D13 | LOW | Signature drift | BC-6.01.002:132 vs ARCH-01:39 | "env lookups via `EnvVars.Get`", but the interface method is `Lookup(name) (string, bool)`. | product-owner |
| ADV-P8-D14 | LOW | Exclusion-list inconsistency | BC-6.03.004:146-155 vs BC-2.02.002:138 | PC-3 calls its value list "the exhaustive union" of the BC-2.02.002/003 exclusion lists and includes `1e400`. BC-2.02.002's case list is only `nan`, `inf`, `-inf`, `-1`; `1e400` appears there only as EC-004. | product-owner |
| ADV-P8-D15 | LOW | Grammar gap | BC-2.01.005:81-121; BC-2.02.001:160-163 | An overflowing strict-JSON member (e.g. `[1e400,0.9]`) is unclassified: shape error or `not finite`? `not finite` is reachable for composites only through such literals. Also, the PC-5 type list (:83-85) omits `FloatQuad`, and changelog :31 says NumberList. | product-owner |
| ADV-P8-D16 | LOW | Platform seam leak (P18) | BC-3.01.001:85-90 | In the TZ-unset leg (c), Go's runtime local zone reads the real process `TZ` on POSIX. The injected-env table leg's expected value then depends on the CI runner, contradicting Inv 3. | architect |
| ADV-P8-D17 | LOW | Windows ambiguity (P18) | BC-2.01.002:85-90; BC-2.02.001:84-89 | Under the Windows case-fold, the `[from <ENVNAME>]` tie-break ("byte-exact FIELD") and the case of the printed name are undefined for names that differ only in case. Also undefined: whether a P1 field value at index ≠ 0 (e.g. `..._1_METRICS_URL=ftp://x`) is validated. | product-owner |
| ADV-P8-D18 | LOW | Unpinned ordering | BC-2.03.001:53-61 vs BC-2.01.001:86-92 | Validate claims "the same emission order as the statusline side" for its lexicographic warning order. The statusline side never pins any warning order. | product-owner |
| ADV-P8-D19 | LOW | Threshold unit (P16) | BC-6.04.002:100-102 | The validated `timing_exempt` condition ">512 KB" does not say whether it means 512,000 or 524,288 bytes (the latter is the `read_cap_bytes` default). | product-owner |
| ADV-P8-D20 | LOW | Missing limit leg [unverified] | BC-5.02.005:44-68 | `Str` has no recursion-limit or error outcome. `str()` of a nested stdin list at SL:442/453 (value depth up to 991) goes through CPython's repr recursion guard. Behavior at the limit was not measured. | product-owner |
| ADV-P8-D21 | LOW | CPython detail | BC-5.04.003:72 | `float64(ns)/1e9` omits `_PyTime_AsSecondsDouble`'s whole-second branch. It differs only for \|ns\| ≥ 2^62, and only on the real-clock path. | product-owner |
| ADV-P8-D22 | LOW | Mis-anchor (ARCH) | ARCH-06:32 vs BC-5.03.004:63-68 | ARCH-06 says BC-5.03.004 owns the per-flavor `join`/`dirname` rules. The BC says BC-1.02.004 owns them, which matches BC-1.02.004:85-95, 128. | architect |
| ADV-P8-D23 | COSMETIC | VP row wording | BC-4.01.002:107 | The VP-002 row omits the `--subagent` routing carve-out. The VP file (:52-56) has it. | product-owner |
| ADV-P8-D24 | COSMETIC | Wording | BC-6.01.003:121 | "feeds the probe a non-ASCII byte": a lone byte ≥0x80 is invalid UTF-8. It should say a non-ASCII code point, and the probe script is not specified. | product-owner |

### 2. Policy compliance
- **P1** PASS (CP-T08 retired and CP-T09 minted, append-only).
- **P2** PASS (DI-008/010/012 cited; sampled, not exhaustive).
- **P4** FINDING: D02, D03, D05, D22.
- **P5** PASS.
- **P6** PASS (SS-02..06 IDs match the ARCH-INDEX registry).
- **P7** FINDING: D07, D11.
- **P11** PASS (BC-6.04.003 PC-2 reports the case count and fails on a 0 budget; BC-6.03.004 PC-5 prints per-id counts).
- **P12** PASS (no owner challenges raised).
- **P13** PASS (the rename retry rides `temp-file`).
- **P14** PASS.
- **P16** FINDING: D19.
- **P18** FINDING: D01, D16, D17.
- **P19** PASS (the sha1 nolint in BC-5.03.003 is justified).
- **P20** PASS (D08 concerns the golden rule, not hard-coded values).
- **P21** PASS (nothing quoted).
- **P3, P8, P9, P10, P15, P17** N.A.

### 3. Not fully read / not verified
- **BC frontmatter:** the top 18-38 lines of several BCs were skipped (frontmatter only; bodies read in full).
- **Cross-check docs read only partly:** interface-definitions.md (lines 100-259), ARCH-07 (lines 60-149), ARCH-02, error-taxonomy and the VP files (grep only).
- **Not read:** capabilities.md, invariants.md, nfr-catalog, test-vectors, risk-register, assumptions-register, module-criticality.
- **Python claims not verified:**
  - BC-5.04.001 PC-3: 3.11 accepts an emoji (multi-byte) as the date/time separator.
  - BC-5.02.002 row 62: repr `…456.8` at a tie.
  - BC-5.01.002 PC-4: leading zeros count toward the 4,300-digit limit.
  - BC-5.01.001 EC-006: `round(1.00005, 4)`.
  - BC-6.01.003: canary round-trip value `…4245195`.
  - D20: repr recursion limit.

### 4. Novelty
MEDIUM. D01-D03 and D09-D10 are new contradictions; the rest are refinements or propagation leftovers. **NOT_CONVERGED**.
