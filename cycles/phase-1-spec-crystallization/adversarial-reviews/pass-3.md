---
document_type: adversarial-review
phase: 1d
pass: 3
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 150
---

# Adversarial Spec Review — Phase 1d, Pass 3

Pass 3 ran as six fresh-context perimeters (A, A2, B, C, C2, D), the same split as passes 1 and 2, because the spec corpus under review (~1.4 MB) exceeds a single agent context. Each perimeter was re-reviewed by an independent fresh-context adversary with no visibility into the other perimeters. Each section below is the verbatim final report of one perimeter, unedited except for this framing; no textual normalization was needed. Per-perimeter novelty rulings: A MEDIUM, A2 MEDIUM-HIGH, B MEDIUM, C HIGH, C2 MEDIUM, D HIGH — aggregated as MEDIUM at pass level; the pass is NOT_CONVERGED (150 findings: 36 HIGH / 61 MEDIUM / 48 LOW / 5 COSMETIC, against 116 in pass 2 — a regression in both count and HIGH severity, root-caused by the orchestrator and recorded in `../convergence-trajectory.md`: the pass-2 remediation added new scope without pre-validation, and the pre-existing content shows refinements only).


## Perimeter A (cross-cutting)

Findings: 29 (high 8, medium 9, low 11, cosmetic 1).

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P3-A01 | HIGH | contradiction | specs/architecture/ARCH-01-binary-cli.md:45-51; specs/prd-supplements/interface-definitions.md:31-35 | ARCH-01 routes on an exact `--subagent` "before any flag ... processing", so a `--subagent` after `--` would still route. BC-1.07.001 PC-4 agrees: any index matches. BC-4.01.002 EC-004 says the opposite: `hylo statusline -- --subagent` is positional data for the normal render. Neither supplement settles which wins. | architect + product-owner |
| ADV-P3-A02 | HIGH | interface cannot express BC | ARCH-01-binary-cli.md:39,48; ARCH-03-statusline.md:47-52,88 | ARCH-01 says subagent routing happens "before any flag or config processing", yet the panel needs config: the `statusline.subagent.enabled` gate, `backends[0].model_prefixes` (BC-1.07.006), and the D4-EX-3 line on a bad value (BC-1.07.002 EC-003/004, "config check precedes any stdin parse"). `runStatusline` takes no args and `statusline.Main` has no argv or subagent entry point. ARCH-01 §Mapping omits BC-1.07.001, while BC-COMPONENT-MAP:152 homes it in sl/subagent.go. Nothing says who loads config on the subagent path, or what it prints when an unrelated key is invalid. | architect |
| ADV-P3-A03 | HIGH | missing harness capability | ARCH-07-parity-harness.md:97-98 | BC-1.07.002 cites VP-009 "subagent corpus family rows" for the enabled half. The case model has no argv field and the case-id grammar has no subagent family; only cpa01..03 exist. BC-4.01.002:108 says "the harness invokes `hylo statusline` without flags". So the legacy-parity half of S1.07 cannot run in Tier A/B. | architect |
| ADV-P3-A04 | HIGH | contradiction (NFR method) | nfr-catalog.md:24,67-71; ARCH-08-build-ci-release.md:52-57; cicd-setup.md:181-182 | All three say 1 warm-up + **20** runs per case, nearest-rank p95 = 19th sample, binding per case, **no pooling**. The contract BC-6.04.002 PC-1/PC-2 (lines 64, 77) says **R = 5** runs per step, percentiles on the **pooled** times. That is a different, much less strict gate. BC-6.04.002:56 also puts the timing test in `internal/statusline`, while BC-COMPONENT-MAP:235 says par/timing.go. | product-owner |
| ADV-P3-A05 | HIGH | config range contradicts BC | interface-definitions.md:155,163,164,171,172,174,175,176,184,185 | These `Seconds` keys are registered as "any finite number", which admits negatives. BC-2.02.002 PC-2 makes negative `Seconds` values a config error, and PC-4/line 67 defaults `Seconds` ranges to `> 0` unless a `>= 0` rationale is stated. The range column is wrong for 10 keys. | product-owner |
| ADV-P3-A06 | HIGH | settled decision violated (P12) | ARCH-05-platform.md:31,63; BC-COMPONENT-MAP.md:93,241 | ARCH-05 still builds `StatFD(n int)` for the "int `transcript_path` = fd semantics" and maps BC-1.03.015 to plat/fd_*.go. OD-161 (BC-1.03.015 lines 51-55, 65-66) rules that the int branch does **no descriptor I/O at all**. A story built from ARCH-05 would add exactly the foreign-descriptor access OD-161 forbids. | architect |
| ADV-P3-A07 | HIGH | count drift (partial-fix regression, blast radius 4) | prd.md:41-45,111,124; module-criticality.md:55; risk-register.md:29 | PRD §1.6 says S1 = 93 BCs and the total is 145. §2 lists 101 S1 rows (incl. BC-1.07.001..008), and ARCH-INDEX:115 / BC-COMPONENT-MAP:240 say 153. module-criticality still says "all 93". R-005 still claims "145/145 on disk". The "101 mapped + 44 new" split is also stale. | product-owner |
| ADV-P3-A08 | HIGH | assumption mis-stated [owner-question] | assumptions-register.md:29; prd.md:621-624 | ASM-007 is marked "validated" against the 2.1.322 client. BC-1.07.001/.002 PC-2 instead carry ASSUMP-107-1: compatibility with the 2.1.326 payload is assumed, "to be verified by a capture before Phase 3". ASM-002 names 2.1.325. The register should mark ASM-007 open and say whether current clients still send the `subagentStatusLine` payload. The owner's private machine context records a client change affecting this surface; not quoted here. | product-owner |
| ADV-P3-A09 | MEDIUM | contradiction (never-blank) | prd.md:432,477; nfr-catalog.md:25 | §3.1 says `hylo statusline` prints "1 or 2 rendered lines ... never blank". NFR-002 requires >= 1 byte. BC-1.07.004 and BC-1.07.002 PC-2 legitimately emit zero bytes. The subagent-mode exception is not stated, so a story writer will add a never-blank assertion to that mode. | product-owner |
| ADV-P3-A10 | MEDIUM | coverage gap | prd.md:477,493; nfr-catalog.md:25; error-taxonomy.md:40 | NFR-002 counts only CP-S/T/N triggers. The E-REN-002 contract lists omit CP-O01..O05 (render-time overflow) and CP-A01..A03 (BC-1.07.008), even though error-taxonomy:165-168 says those resolve to the degraded line. | product-owner |
| ADV-P3-A11 | MEDIUM | traceability gap | prd.md:548-569 | The §7 traceability matrix has no BC-1.07.001..008 row. The S1.07 subsection is invisible to rollups built from §7. | product-owner |
| ADV-P3-A12 | MEDIUM | stale placeholder (P4) | prd.md:132-136; test-vectors.md:44; assumptions-register.md:29 | These still say "rows inserted by the pass-2 remediation burst" / "S1 agent-panel BCs + BC-4.01.002" instead of BC-1.07.001..008. The rows have been inserted, so the anchors are unresolved placeholders. | product-owner |
| ADV-P3-A13 | MEDIUM | subsystem-rule mis-statement (P6) | ARCH-INDEX.md:48-49 | ARCH-INDEX says BC `subsystem:` and stories "use the Name column verbatim". All 153 BC files carry `subsystem: "SS-0N"` (grep: 153/153 match the SS-ID form). Either the rule or the practice is wrong, and Phase-2 `subsystems:` fields will follow whichever the story writer reads. | architect |
| ADV-P3-A14 | MEDIUM | config over code (P20) [owner-question] | interface-definitions.md:154,187 | `statusline.subagent.enabled` is the only subagent key. BC-1.07.005:116 pins `_SUB_GLYPH` as a Go map literal. The settled suffix and `_fmt_tokens` thresholds (BC-1.07.007) have no registry rows. Main-row glyphs are config (`statusline.glyphs.*`, OD-02), so the panel's glyphs and thresholds should join the registry or carry a why-not-config note. | product-owner + architect |
| ADV-P3-A15 | MEDIUM | stale after OD-156 | ARCH-06-pyfmt.md:19,42-43 | ARCH-06 says "`math/big` at exactly two duration-format sites (OD-137)". OD-156 adds the `_fmt_lines` site and makes `Int`/`Ceil`/`Round` exact beyond int64 (error-taxonomy:120-124; ARCH-06:28,74-79 itself). | architect |
| ADV-P3-A16 | MEDIUM | CI checks nothing (P11) | cicd-setup.md:24-26,75-82; ARCH-08:61-80 | The timing-report job "just echoes its report text and passes", and the positive-coverage table has no timing row. Nothing requires "N cases timed > 0", so an activated timing job could report on zero cases and pass. | architect (devops) |
| ADV-P3-A17 | MEDIUM | hygiene scan gap (P14/P21) [process-gap] | cicd-setup.md:90-95 | The category scan covers only private IPs, home paths and emails. It does not cover the CLAUDE.md categories hostnames, usernames, session links/UUIDs, or "Claude" in names, so the claim that NFR-006 is enforced in CI is overstated. | architect (devops) |
| ADV-P3-A18 | LOW | hygiene fail rule incomplete | cicd-setup.md:82 | The pattern-scan fail condition is only `K == 0`. It never says that `H > 0` fails, so a scan could find hits and still pass. | architect (devops) |
| ADV-P3-A19 | LOW | oracle pin ambiguity | nfr-catalog.md:26; assumptions-register.md:23; ARCH-08:42,50 | NFR-003 and ASM-001 pin CPython **3.11.7**. OD-104 and CI pin **3.11.x** (setup-python resolves the latest patch). The NFR target names an interpreter CI does not install. | product-owner |
| ADV-P3-A20 | LOW | reserved-name list incomplete | ARCH-07:91; ARCH-08:57 vs BC-2.01.001:79-82 | `HYLO_TIMING_GATE` and `HYLO_PARITY_FUZZSECONDS` are in the `HYLO_*` namespace but missing from BC-2.01.001's closed reserved list. They would draw the unknown-setting warning wherever hylo inherits them. | architect |
| ADV-P3-A21 | LOW | wrong anchor (P4) | risk-register.md:30 | R-006 cites "BC-2.01.001 invariant 6". The reserved-names rule is postcondition 6 (BC-2.01.001:72-82). | architect |
| ADV-P3-A22 | LOW | contradiction | risk-register.md:32 vs error-taxonomy.md:129-131 | R-008 says legacy "accumulates and saves where hylo skips". The taxonomy says legacy "degrades sticky (nothing saved)". | architect |
| ADV-P3-A23 | LOW | register drift | risk-register.md:18-21; prd.md:626; ARCH-INDEX.md:43 | These say "R-001..R-007" and "ASM-001..006". R-008 and ASM-007 now exist. | product-owner + architect |
| ADV-P3-A24 | LOW | stale exclusion description | ARCH-00-overview.md:30 | ARCH-00 says "D4-EX-1/2/3 + OD-110/OD-136 entries". OD-110 is not an id in the set; the closed set is the ten ids, including `temp-file`, OD-159, OD-160 and OD-161 (ARCH-07:43-47). | architect |
| ADV-P3-A25 | LOW | contradicts OD-158 | ARCH-06-pyfmt.md:58 | ARCH-06 says "mutation kill rate >= 95% binds here first". OD-158 makes mutation a Phase 6 target that does not gate P1 (module-criticality:35-39). | architect |
| ADV-P3-A26 | LOW | stale message text | interface-definitions.md:31,87 | The doc says "`hylo statusline` takes no flags in P1", and the stderr detail reads "(hylo statusline takes no flags)". Both are false now that `--subagent` is a valid flag (BC-4.01.002:59 carries the same text). | product-owner |
| ADV-P3-A27 | LOW | threshold unexplained (P16) | interface-definitions.md:144,146 | The upper bound `100` in `kv.cells` and `sparkline.points` (`1..100`) has no rationale; the cited T-codes justify the defaults, not the bound. | product-owner |
| ADV-P3-A28 | LOW | untested release targets (P18) | cicd-setup.md:103 | Releases ship `linux/arm64` and `darwin/amd64`, which the CI matrix never tests. ARCH-06:52 notes FMA-sensitive arm64 sites that are tested only on macOS. | architect (devops) |
| ADV-P3-A29 | COSMETIC | typo | ARCH-01-binary-cli.md:81 | `-ldfs -X` should be `-ldflags -X`. | architect |

## 2. Policy compliance

- **P1 append_only_numbering:** PASS. SS/BC/VP ids are append-only and no gaps were found.
- **P2 lift_invariants_to_bcs:** N.A. within this perimeter. The DI references in PRD §8 resolve.
- **P4 semantic_anchoring_integrity:** FINDING (A06, A12, A21, A24).
- **P5 creators_justify_anchors:** FINDING (A13).
- **P6 subsystem names verbatim:** FINDING (A13). The PRD §1.6 names match the registry.
- **P7 BC H1 is the title source:** PASS on 31 sampled H1s against PRD §2. The count drift is filed as A07.
- **P9 VP-INDEX is the catalog source:** PASS. 40 VPs; classes 32/7/1 and methods 20/12/3/2/1/1/1 add up; the ARCH-INDEX primary and second homes agree with VP-INDEX.
- **P11 ci_positive_coverage_assertion:** FINDING (A16, A18).
- **P12 settled_decisions_are_constraints:** FINDING (A06, A25).
- **P13 parity_before_behavior_change:** FINDING (A03: the legacy-parity half of the subagent mode cannot be verified).
- **P14 public_repo_hygiene:** PASS on content. The perimeter grep found no private IPs, home paths, emails or session ids. The scan-coverage gap is filed as A17.
- **P16 thresholds_are_explained:** FINDING (A27).
- **P17 ledger_format_frozen_until_cutover:** PASS (ARCH-04 and ARCH-09 reserve the ledger only).
- **P18 cross_platform_from_day_one:** PASS with a LOW note (A28).
- **P19 go_hardening_toolchain:** PASS (AD-14 test deps have reasons; x/sys is the sole runtime dep).
- **P20 config_over_code:** FINDING (A05, A14).
- **P21 public_artifact_hygiene:** PASS (grep clean; A08 deliberately does not quote the private context).

## 3. Files not fully read

All files in the perimeter were read in full. BC and VP files were opened only to check cross-references: BC-1.07.001/.002, BC-1.03.015, BC-2.01.001, BC-2.02.002, BC-4.01.002 (grep), BC-6.04.002 and the VP-INDEX catalog.

## 4. Novelty

**Novelty: MEDIUM.** A01–A06 are new substantive contradictions. Most come from the OD-155 subagent insertion and the OD-156/OD-161 rulings not reaching the architecture, harness and NFR documents. The rest are propagation and wording drift.

**NOT_CONVERGED**


## Perimeter A2 (remaining cross-cutting docs)

Findings: 27 (high 6, medium 15, low 6, cosmetic 0).

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P3-A2-01 | HIGH | L2 contradicts P1 BCs | domain-spec/invariants.md:31; capabilities.md:31; state-machines.md:56-60; ubiquitous-language.md:39 | DI-008, CAP-009 ("output is never blank"), SM-04 ("at least one line") and the UL "Degraded line/ladder" entry all require at least one line of output. The `--subagent` BCs require zero bytes for: zero tasks (BC-1.07.004 PC6), unparseable stdin (BC-1.07.003:36-37, which invents a "DI-008 rung: silent emptiness" that DI-008 does not contain), and `enabled=false` (BC-1.07.002 PC2). SM-04 says the unknown-flag check runs "first", but BC-1.07.001 routes `--subagent` before any flag check. The L2 has no carve-out for this mode. | business-analyst |
| ADV-P3-A2-02 | HIGH | VP fails a correct impl | VP-002:89 (also :107-111); gene-transfusion-assessment.md:55 | The row `{"--", "--subagent"}` expects "normal render". BC-1.07.001 PC1/PC4 and legacy SL:1240 (`"--subagent" in sys.argv[1:]`) route this argv to the subagent renderer. The fuzz-oracle comment checks the unknown-flag rule before the `--subagent` match, which is the reverse of the property statement ("regardless of other unknown flags"). The gene assessment says arguments after `--` are "ignored", which is false for `--subagent`. Table rows also mix argv with and without the verb `statusline`, so "argv[1:]" is ambiguous. | architect |
| ADV-P3-A2-03 | HIGH | VP mis-states the computation; wrong oracle | VP-039:37-46, :84-94 | The VP specifies `float64(ms) * 0.001`. BC-1.07.007:38,55,68 and legacy SL:919 compute `max(now_ms - start, 0)/1000`; multiplying by 0.001 is not the same as dividing by 1000. The actual fusion site is `time*1000 - start`, which the VP never names. The VP accepts up to 1 ulp of difference between helpers local to the test (`EvalFused`/`EvalUnfused`), so production code is never compared with CPython. Parity needs the unfused result exactly, enforced by an explicit `float64()` conversion as the BC requires. "On all other OSes the same source path compiles without contraction" is false: linux/arm64 and windows/arm64 also fuse. | architect |
| ADV-P3-A2-04 | HIGH | Cross-platform: skeleton passes a wrong impl | VP-034:41-45, :86-99 | On Windows the child-env table pins only TEMP, TMP and PYTHONUTF8/PYTHONIOENCODING. HOME/USERPROFILE are checked only on POSIX. CPython 3.8+ `ntpath.expanduser` reads USERPROFILE and ignores HOME, so the Windows oracle (which writes the `*.windows.golden` files) would put caches in the real profile; the skeleton passes that leak. A from-scratch env without SYSTEMROOT can also break Windows socket initialization, which the oracle's metrics fetch needs (MEDIUM confidence). | architect |
| ADV-P3-A2-05 | HIGH | Vacuous VP (can never fail) | VP-040:97-105, :118 | Both `quick.Check(...)` return values are discarded, so the test cannot fail. With a nil config, `testing/quick` uses its default generators, so the LF/CR-free and SEP-free generators the VP claims are not applied. The P2 split guard is not implemented. "quick shrink keeps failures reproducible" is false: `testing/quick` does not shrink. | architect |
| ADV-P3-A2-06 | HIGH | CI positive coverage [process-gap] | VP-009:75; VP-010:77; VP-012:92; VP-035:71; VP-037:72-77 | Every regression-detector skeleton loops over a loaded set (cases, goldens, exclusions, fixtures) and has no non-zero count assertion. An empty or mis-pathed load passes green. No VP requires a computed "N cases validated" log line (POL-11). This applies to several security- and parity-critical legs. | architect |
| ADV-P3-A2-07 | MEDIUM | Skeleton weaker than the property | VP-001:86, :96-101; VP-005:84-95 | VP-001's FaultInjectionTable comment omits the CP-A01..A03 rows, and `runStatusline` takes no argv, so the subagent fault legs (BC-1.07.008) are not exercised. Both fuzz legs check only exit code 0 and non-blank output on the main entry. The method promises stdout ∈ {render, 29-byte line, JSON lines, zero bytes}, and VP-005 promises "never the degraded line via the parse path" for the subagent entry; neither is asserted. | architect |
| ADV-P3-A2-08 | MEDIUM | Go API misuse | VP-005:85; VP-006:107; VP-024:83, :95 | `pyfmt.Decode` is called with 2 arguments in VP-005 and with 3 (budget) in VP-006/VP-024. VP-024:95 assigns a multi-value call to a single variable (`again := pyfmt.Decode(...)`), which does not compile. `pyfmtDefaultBudget` contradicts VP-006 ("per-call-site, not a free constant"). | architect |
| ADV-P3-A2-09 | MEDIUM | Skeleton fails a correct impl | VP-036:77-80 vs :44-46 | `MeasureCorpus(warmup: 1, ...)` uses named arguments, which Go does not have. `worstCaseP95()` includes the >512 KB-line fixture that the property exempts from the gate, so an armed gate fails a correct build. | architect |
| ADV-P3-A2-10 | MEDIUM | Contradiction with BC | VP-010:42; VP-037:39-40 vs BC-6.04.001:71-73; gene-transfusion-assessment.md:117-118; architecture-feasibility-report.md:87 | VP-010 says Go matches the goldens "without Python installed" and VP-037 says "Windows runs Tier B without Python". BC-6.04.001 puts setup-python and Tier A on all three legs, and the gene and feasibility documents agree with the BC. | architect |
| ADV-P3-A2-11 | MEDIUM | Cross-platform gap | VP-026:44-46 vs BC-6.04.001:71-73, VP-010:37-42 | VP-026 claims no Windows equality for naive local-time conversion (CRT vs IANA). Tier A runs live on Windows, and VP-010 commits Windows goldens. No exclusion id or corpus rule keeps naive-timestamp cases off the Windows leg, so any such case is an unexplained diff. | architect |
| ADV-P3-A2-12 | MEDIUM | "Non-vacuous" claim overstated | VP-022:43-48, :71-79, :109-117 | The recording wrapper sees only `Env.Files` opens, so a direct `os.Open` is invisible, contrary to "fails if any code path opens anything else". The allowed set omits the native probe's `/proc` reads on Linux (either a vacuous pass or a false fail, depending on the seam). The reflection check matches field names only. | architect |
| ADV-P3-A2-13 | MEDIUM | Semantic mis-anchor | VP-INDEX.md:218, :105, :314; VP-022:55-61 | VP-022 says BC-1.06.001 was a mis-anchor and was removed, yet the VP-INDEX map still lists VP-022 under BC-1.06.001. BC-1.01.004 → VP-034 (oracle isolation does not verify visible width) is also still carried. Both were "known residual" in pass 2 and are unresolved; mis-anchors block convergence. | architect / product-owner |
| ADV-P3-A2-14 | MEDIUM | P2 enforcer column stale | invariants.md:30, :31, :35 | The column states DI-007 = 35 BCs, DI-008 = 78, DI-012 = 42. A grep of BC files (excluding ALLOCATION) gives 38, 82 and 57. The counts predate the BC-1.07.* additions. | business-analyst |
| ADV-P3-A2-15 | MEDIUM | Resolved item contradicts a later ruling | owner-validation-list.md:211-215, :217-220 | VALID-13 still reads "until then the defensive rule stands" (OD-130 in force now). OD-157 moved OD-130 to P6 and kept legacy ±Inf behavior in P1. L2-INDEX:76 lists this file as BC-creation input. | business-analyst |
| ADV-P3-A2-16 | MEDIUM | Assessment claim no longer holds | dtu-assessment.md:21, :26-28, :45-46, :81, :177 | The inventory omits the `subagentStatusLine` stdin contract (a separate push contract; the ASSUMP-107-1 capture is still pending). "Exactly ... three non-network external contracts" is therefore false. "OD-130 vectors" are still listed as P1 fake extensions at :45/:81/:177 even though row 4 was corrected to OD-157 (partial fix). "93 S1 BCs" is stale; the count is now 101. | architect |
| ADV-P3-A2-17 | MEDIUM | Partial-fix propagation | VP-012:13, :52-55, :120-123 | The closed set grew to ten ids, but the riding-contract list and `bcs:` cover only D4-EX-1/2/3, OD-76 and temp-file. OD-30 (BC-1.05.006), cp-x03 (BC-1.01.001), OD-159, OD-160 (BC-1.05.004) and OD-161 (BC-1.03.015) have no rider and no named table test. | architect |
| ADV-P3-A2-18 | MEDIUM | VP contradicts a ruling | VP-029:43 | The property requires oracle-matching "int-`transcript_path` fd semantics". OD-161 / BC-1.03.015 PC3 make an integer path mean no transcript, with no descriptor I/O. | architect |
| ADV-P3-A2-19 | MEDIUM | VP `bcs:` vs body | VP-019:13 vs :48-50 | BC-1.02.005 and BC-1.02.013 are in `bcs:` but not in Source Contract, and nothing in the body checks them. | architect |
| ADV-P3-A2-20 | MEDIUM | Unanchored claim | VP-009:53-54 | "Every byte-exact-class S1 contract (93 contracts, see the VP-INDEX coverage table)": the index maps VP-009 to only 6 BCs, and a grep finds 68 SS-01 BCs with `parity_class: byte-exact`. | architect |
| ADV-P3-A2-21 | MEDIUM | DI-012 ambiguity [owner-question] | VP-005:43-44 | `subagent.enabled=false` is called a "DI-012 named deviation", but no id in the 10-id closed set covers it, so per VP-012 it can carry no exclusion entry. Either it is not a deviation (a non-default config value), or it needs an id. | architect |
| ADV-P3-A2-22 | LOW | Missing call site | VP-006:45-54 | The depth table has no `main_subagent → json.load` row. It is the same 6-frame chain, but over-limit input there yields zero bytes, not the degraded line. | architect |
| ADV-P3-A2-23 | LOW | Vacuous / stale invariant claims | VP-028:57; VP-021:49 | These golden VPs claim to verify the OD-135 coverage/mutation tier. OD-158 makes mutation kill rate non-gating in P1. | architect |
| ADV-P3-A2-24 | LOW | Go API | VP-012:131; VP-033:79 | "Reflection over the test registry" does not exist in Go (`go test -list` or AST parsing would be needed). VP-033 calls `FindAncestor(tc.PID, ...)` with no fake-chain seam, so it would hit the real OS. | architect |
| ADV-P3-A2-25 | LOW | Ambiguity | VP-015:89-96; VP-032:40; VP-018:47-50 | VP-015: with several invalid values, the expected key must be the first in registry order (BC-2.02.001:64); this is unstated. VP-032: the Windows config dir and the LOCALAPPDATA-unset result are unstated. VP-018: whether the rename retry applies on all OSes or only Windows is unstated. | architect |
| ADV-P3-A2-26 | LOW (pending intent verification) | L2 wording | invariants.md:30 vs capabilities.md:31; invariants.md:35; bounded-contexts.md:32; capabilities.md:38 vs owner-validation-list.md:86 | DI-007's input list omits the environment seams (git, process table, clock) that CAP-009, VP-022 and the brief allow. DI-012's parenthetical list does not match the 10-id set. BC7 says "two-row render" without agent-panel rows. CAP-016 puts both UIs in P4, while VALID-05 puts the terminal UI in P6. | business-analyst |
| ADV-P3-A2-27 | LOW | Stale derived note | architecture-feasibility-report.md:102 | It quotes the VP-022 home as "ARCH-04/09"; the catalog row now reads ARCH-03/ARCH-04/ARCH-09. | architect |

## 2. Policy compliance
- P1 append_only_numbering: PASS (VP-001..040, DI-001..017 contiguous).
- P2 lift_invariants_to_bcs: FINDING 14 (every DI is cited by a BC or explicitly deferred; the counts are stale).
- P4 semantic_anchoring_integrity: FINDING 13, 18, 20.
- P5 creators_justify_anchors: PASS (VP-022 anchor note justified).
- P6 subsystem names: PASS (they match the ARCH-INDEX registry).
- P9 vp_index source of truth: FINDING 13, 20.
- P12 settled decisions: PASS (21 tagged [owner-question]).
- P13 parity before behavior change: PASS.
- P14 public repo hygiene: PASS.
- P16 thresholds explained: PASS.
- P17 ledger format frozen: PASS.
- P18 cross-platform: FINDING 03, 04, 10, 11.
- P19 Go toolchain: PASS.
- P20 config over code: PASS.
- P21 public artifact hygiene: PASS (only RFC 5737 addresses, plus a legacy default file name that already appears in public `legacy/`).

## 3. Files not fully read
VP-004, VP-006, VP-030, VP-031, VP-032, VP-033 and VP-034 were read from the property statement onward (frontmatter checked via a `bcs:` grep; lifecycle tails skipped). Everything else in the perimeter was read in full.

## 4. Novelty
Novelty is MEDIUM-HIGH. The integration of the `--subagent` mode into the L2, VPs and assessments is new ground, and the VP-039, VP-034 and VP-040 defects are substantive. **NOT_CONVERGED**.


## Perimeter B (BC-1.01, BC-1.02)

Findings: 18 (high 4, medium 6, low 7, cosmetic 1).

## 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P3-B01 | HIGH | settled-decision drift (P12) | BC-1.01.001:81 (EC-007), :43-44 (PC1), :113 (cites OD-14) | EC-007 says `--subagent` is unknown under OD-14 and renders the unknown-flag line. OD-155 (decisions log :136) supersedes OD-14, and BC-4.01.002:72-80, BC-1.07.001 and CAP-009 all say `--subagent` is a valid P1 flag. Legacy runs `main_subagent` under the same guard (SL:1239-1245), so this BC's scope note is also wrong. | product-owner |
| ADV-P3-B02 | HIGH | cross-platform parity (P18) | BC-1.02.004:47-48 (PC2); legacy SL:380-381, 385-386 | The BC says HEAD and `.git` text reads are strict UTF-8 "because the oracle runs with LANG=en_US.UTF-8". That is false on Windows: CPython 3.11 `open()` uses the ANSI code page (cp1252) there, LANG has no effect, and the BC-6.01.002:114-116 shim only reconfigures stdin/stdout. The Windows oracle decodes vector `ref: refs/heads/\xff\xfe` to `ÿþ`, not `""`, and garbles non-ASCII branch names, so the Windows goldens will diverge from Go. Needs an emulation, a harness pin, or a named exclusion. [owner-question] | architect / product-owner |
| ADV-P3-B03 | HIGH | mis-anchoring; partial-fix propagation (5 files) | BC-1.01.003:138, .004:115, .005:127, .006:130, .007:117 | The VP Anchors sections still name only VP-027, and describe properties that VP-027 v1.1 handed off to VP-040 (VP-027:22). Example: BC-1.01.006:130 says "VP-027 — trim structure property", but that is VP-040 P5. The VP tables in the same files cite VP-040, so each file contradicts itself. | product-owner |
| ADV-P3-B04 | HIGH | partial-fix propagation (2 files) | BC-1.02.027:156-160; BC-1.02.028:158-159 (defers to it) | Says `pyfmt.Int(x float64) (int64, error)` remains the fast path. ARCH-06:78, BC-5.01.003:57 and BC-1.02.026:45 define `Int(...) (Num, error)`, exact beyond int64, and error-taxonomy:120-124 declares the int64 sketch superseded. The fix reached BC-1.02.026 but not this sibling. | product-owner |
| ADV-P3-B05 | MEDIUM | legacy mismatch | BC-1.02.014:59, :91-92 (EC-012/013); legacy SL:857 | `n / 1e6` with an int `n` and a float literal goes through `float_div`, which converts `n` to float first. So (a) OverflowError fires whenever `n` > ~1.8e308, not only when the quotient overflows: `10**310` degrades in legacy even though 1e304 fits. (b) The result is `float(n)/1e6` (rounded twice), not "the correctly rounded quotient", so an exact math/big quotient can diverge for ints above 2^53 near `.x5` ties. Contradicts error-taxonomy:107-110 and BC-1.02.006 EC-010 / BC-1.02.020 EC-011, which correctly say the int is converted first. | product-owner |
| ADV-P3-B06 | MEDIUM | VP cannot catch the defect | BC-1.02.024:97 vs :57 | The VP-028 row grids REM around `0.10 × length` (60480 s for 7d). The boundary is at `rem = 0.9 × length` (544320 s, PC4). A test built from this row never touches the boundary. | product-owner |
| ADV-P3-B07 | MEDIUM | OD-162 applied inconsistently (P20) | BC-1.02.006:56-65 vs :79-86; interface-definitions:189-193; same wording in BC-1.02.014:69-74, .019:61-66, .025:62-67 | PC3-PC5 define the widget for any `cells`/`plain_max`/`red_from` (`d=100/n`, `min(…,n)`, a loop over n cells), yet Inv 3 makes them default-only. The registry justifies default-only with "BC hard-codes pct/10, range(10)", which the BC no longer does. The stated reason, "legacy bakes it and defines no override", is not OD-162's test ("non-default behavior cannot be defined"): GIT_TTL (SL:99), NARROW_COLS (SL:100) and RL_KEEP (SL:85) are also baked and got real ranges. | product-owner / architect |
| ADV-P3-B08 | MEDIUM | key registration (P20, OD-162) | interface-definitions:106 (and :108) | The `statusline.narrow_cols` row (BC-1.01.003 PC1) states only the operator, with no valid range, against OD-162's "every key has a valid range". Separately, `git.ttl_s` ">= 0" excludes negative values that legacy defines (always recompute), unlike `limits.keep_s` "any finite number". | architect |
| ADV-P3-B09 | MEDIUM | exclusion discipline (DI-012) | BC-1.02.005:85,87,88 (EC-005 null, EC-006 `5`, EC-008 `true`); BC-1.02.013:83-84, :104-105; BC-1.02.030:82, :107 | These vectors need hand-edited caches. Go never writes a non-string `branch`, a bool `ts`, an `rl` without `rl_ts`, or an empty `rl` (`effective_rl` stores only non-empty dicts, SL:305-308). They are not tagged OD-160, and each BC says "byte-exact (no exclusion-list entry)". Siblings BC-1.02.017:68-70 and BC-1.01.008:56-58 tag the same class OD-160. | product-owner |
| ADV-P3-B10 | MEDIUM | dangling anchors (P4) [process-gap] | BC-1.01.001:125, .002:132, .003:130, .004/.005/.006/.007/.010 (`#statusline-width`), .008:127, .009:140; BC-1.02.001-015 (`#lane`, `#git`, `#context`, `#limits`, `#session`) | None of these fragments exist. ARCH-03's only headings are at lines 15, 23, 45, 82 and 138; I grepped for explicit anchors and found none. No validator catches dangling fragments. | architect |
| ADV-P3-B11 | LOW | mis-cited decision | BC-1.01.001:66-69 (Inv 4); BC-1.02.026:111 | Credits the theme-independent degraded-line SGR to OD-162. OD-162 (log :146) rules only on config ranges; interface-definitions:80-81 credits OD-113 / BC-2.02.001 inv 2. | product-owner |
| ADV-P3-B12 | LOW | unverified oracle provenance | BC-1.02.022:54, :70 (EC-005), :89-91 | ntpath values are "pinned by calling ntpath.normpath" without naming the host. Off Windows, `nt._path_normpath` is missing, so the pure-Python fallback runs. My reading of its 3.11 `splitdrive` gives `//` → `\` and `//x` → label `x`, not `\\` / `\\x`. Either state that the Windows C implementation is the oracle, or re-pin. (Confidence LOW; not executed.) | product-owner |
| ADV-P3-B13 | LOW | test-vector extraction | BC-1.01.008:91-93 | A blank line at :91 ends the GFM table, so the list-repr and unrendered-key surrogate vectors sit outside it and table extraction drops them. | product-owner |
| ADV-P3-B14 | LOW | missing edge case | BC-1.01.002:50-52 | The PC2 list of `{}` causes omits integer literals over 4,300 digits: CPython 3.11.7 json raises ValueError, caught at SL:1203-1204, giving `{}`. pyfmt rejects them too (BC-5.02.003:63), but PC4's "integers stay exact" invites a math/big decoder. Add an edge case and a vector. | product-owner |
| ADV-P3-B15 | LOW | wrong source citation | BC-1.01.003:56 | Cites the project label at SL:442/453/1234; the project label is SL:460-462. | product-owner |
| ADV-P3-B16 | LOW | VP coverage gaps | BC-1.01.001:96-101; BC-1.01.002:108-109 | The VP table lists VP-001 twice and omits VP-003, which the VP Anchors (:133) and EC-005 rely on. BC-1.01.002 ties decode equivalence to VP-001, which is the never-blank property. | product-owner |
| ADV-P3-B17 | LOW | precondition missing | BC-1.02.017:87 (EC-010) | The SL:559 OverflowError fires only when `win_start` is numeric. Otherwise legacy renders the huge exact `_hm(10**309)` with no degrade. The condition is not stated. | product-owner |
| ADV-P3-B18 | COSMETIC | wording | BC-1.02.014:83 | "half-even on exact ties": 1.35 is not a binary tie (1.3500000000000000888); `1.4` is plain nearest rounding. | product-owner |

Outside this perimeter (deferred, not counted):
- **BC-1.06.001 (cross-story):** a session_id with a lone surrogate goes raw into the session-cache file name. Python cannot encode `\ud800` (load returns `{}`, save fails silently), while `\udcXX` maps to raw bytes. A Go writer emitting WTF-8 file names on Linux would diverge across refreshes.
- **invariants.md:35 (system-level):** DI-012's exclusion list omits OD-30 and OD-76 from the closed set of ten.

## 2. Policy compliance
- P1 append_only_numbering: PASS (BC-1.01.001-010 and 1.02.001-030 contiguous, matching BC-INDEX).
- P2 lift_invariants_to_bcs: PASS (DI-008, DI-007 and DI-012 are cited correctly).
- P4 semantic_anchoring_integrity: FINDING B03, B10, B11.
- P5 creators_justify_anchors: FINDING B03, B16.
- P6 subsystem verbatim: PASS (`SS-01` in every frontmatter matches the ARCH-INDEX:53 registry).
- P7 BC H1 = BC-INDEX = PRD title: PASS (all 40 H1s match BC-INDEX:52-96; PRD not re-read).
- P12 settled_decisions_are_constraints: FINDING B01.
- P13 parity_before_behavior_change: FINDING B02, B05, B09.
- P14 public_repo_hygiene: PASS.
- P16 thresholds_are_explained: PASS (rows, narrow_cols, ttl, 1.15, 1800, 0.005, 60000, 300000 and the 50/85 thresholds all carry rationales).
- P17 ledger_format_frozen: PASS (no ledger contact; DI-007).
- P18 cross_platform_from_day_one: FINDING B02 (B12 related).
- P19 go_hardening_toolchain: PASS (FMA no-fuse and the arm64 CI leg are specified).
- P20 config_over_code: FINDING B07, B08 (no DGX_* aliases found).
- P21 public_artifact_hygiene: PASS.

## 3. Coverage and unverified Python claims
- **Fully read:** all 40 perimeter BCs (bodies; frontmatter grepped for subsystem, capability, confidence and parity_class) and `legacy/dgx_statusline.py` 1-1246.
- **Only grepped or partly read:** interface-definitions, error-taxonomy (:95-172), ARCH-03, VP-INDEX, VP-027, VP-040, capabilities, invariants, decisions log, BC-4.01.002, BC-1.07.001, BC-1.06.001, BC-6.01.002.
- **Not read:** prd.md, test-vectors.md, BC-COMPONENT-MAP.md, VP-001/003/005/006/008/009/019/028.
- **Python claims I could not re-derive:**
  - Golden A/B/C segment widths and byte counts (743/701/809/642/286). The A-row token segment of 29 does not match the docstring example, which is 32 columns.
  - The SHA-1 cache keys.
  - The `5e23`/`1e24` hour strings and the 298-character `1e300` string.
  - The 993/994 depth boundary.
  - All ntpath outputs (B12).
- **Hand-verified and correct:** all heat colours, half-even percentages, countdowns, trim staircases, and the BC-1.02.030 sequence countdowns.

## 4. Novelty and convergence
Novelty: MEDIUM. B01, B02, B04-B07 and B10 are substantive and new; the rest are refinements.
NOT_CONVERGED


## Perimeter C (BC-1.03, BC-1.06, BC-1.07)

Findings: 22 (high 5, medium 9, low 7, cosmetic 1).

## Adversarial Review: Phase 1d, Pass 3, Perimeter C (BC-1.03.*, BC-1.06.*, BC-1.07.*)

### 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P3-C01 | HIGH | parity / bytes wrong (pattern, 3 files) [process-gap] | BC-1.07.004:37,52-53,57,82; BC-1.07.005:80,87; BC-1.07.006:89; legacy SL:924 | SL:924 uses `json.dumps` with default `ensure_ascii`, so `»`, `·`, `◨`, `◍` go on the wire as `\u00bb`, `\u00b7`, `\u25e8`, `\u25cd`. The goldens instead show raw non-ASCII inside the JSON, which contradicts BC-1.07.004 Invariant 2 (pure ASCII on the wire). PC3 maps each character to itself (e.g. `»`→`»`), and the "bytes:" notes do the same. PC7 gives the joiner as `20 e2 80 a7 20`, which is U+2027; legacy uses U+00B7 (`c2 b7`), and on the wire it is escaped anyway. Only `\u001b` and the lone-surrogate escape `\ud800` survived, which suggests a tool unescaped valid `\uXXXX` sequences. These goldens cannot be byte-reproduced. | product-owner |
| ADV-P3-C02 | HIGH | legacy mismatch / contradiction within the BC | BC-1.07.005:58-60, 103 vs SL:845-846 | Invariant 1 gives the running glyph as `«` (U+00AB). Legacy and the BC's own Description use `»` (U+00BB). The cited SL:884-886 is `_fmt_tokens`; `_SUB_GLYPH` is at SL:845-846. The status-suffix cite SL:922-923 should be SL:921-922. | product-owner |
| ADV-P3-C03 | HIGH | mis-anchor | BC-1.03.018:72; error-taxonomy.md:137 | CP-O07 is labelled "last-turn rate (SL:1117)" and assigned to BC-1.03.010. SL:1117 is actually the rebuild check `_w - max(0, prompt - pp) > REBUILD_EXCESS`, which is BC-1.03.007. Neither BC-1.03.007 nor BC-1.03.010 carries a CP-O07 edge case. An implementer would put the overflow predicate in the turn machine. | product-owner |
| ADV-P3-C04 | HIGH | uncatalogued crash path | BC-1.07.007:36-37,109; BC-1.07.008:34-57; legacy SL:877-879, 910-911, 918-919 | A huge-int `tokenCount` passes the `isinstance`/`> 0` gate. `float(n)` then raises `OverflowError`, which the helper does not catch (it catches only TypeError/ValueError), so the render degrades. A huge-int `startTime` fails the same way at `now_ms - start`. The BC claims the `?` fallback is unreachable and that the gates never raise. CP-A01..A03 and taxonomy Surface 3 omit both paths. OD-156 requires stdin-borne overflow at render to be a catalogued degrade. | product-owner |
| ADV-P3-C05 | HIGH | P20 config over code; sibling drift | BC-1.07.005:116; BC-1.07.005/006/007 Postconditions; contrast BC-1.02.001:65-68 | BC-1.07.005 says to pin `_SUB_GLYPH` "as a Go map literal". The subagent BCs give raw SGR codes and glyphs with no `statusline.theme.*` or `statusline.glyphs.*` sourcing. The sibling BC-1.02.001 PC4 does source the same colors and `◨` from config. The BC-2.01.004 registry has no subagent glyphs (`»✔✘◍`, raw ` · ` joiner, ` tok`) (grep: no match). | product-owner / architect |
| ADV-P3-C06 | MEDIUM | deviation design defect [owner-question] | BC-1.03.018:73; BC-1.03.010:97; ARCH-03:78-79 | CP-O08 skips the closer line, so the turn with the huge `out` never closes. Every later closer then re-raises inside `finish` and is skipped too: new-id assistant lines (including their usage and composition), real user prompts, and timed system/`compact_boundary` lines. Totals freeze for the rest of the session. This contradicts ARCH-03's "no sticky state". OD-156 does not say which line to skip. | product-owner |
| ADV-P3-C07 | MEDIUM | Python semantics (not executed; derived from CPython rounding) | BC-1.03.006:55-56; BC-1.03.018:71 | The predicate is "\|int\| > DBL_MAX". CPython's int-to-float conversion rounds to nearest and overflows only when \|n\| ≥ 2^1024 − 2^970. Ints between DBL_MAX and that bound convert to DBL_MAX without error. Hylo would skip lines legacy processes, giving an unexplained diff. Test case: DBL_MAX+1 as an int plus a float operand. | product-owner |
| ADV-P3-C08 | MEDIUM | P12 closed exclusion set | BC-1.03.006:59-60 vs error-taxonomy.md:159-161, BC-1.03.018:77-80 | The BC names "exclusion id `OD-156`". The closed ten-id set is unchanged by OD-156: CP-O entries ride `D4-EX-2` and only *cite* OD-156. An `OD-156` id in `exclusions.json` would fail the closed-set check. | product-owner |
| ADV-P3-C09 | MEDIUM | contradiction | error-taxonomy.md:128,144; ARCH-03:79 vs BC-1.03.006 PC5/EC-009, EC-002 | The taxonomy says CP-O09 is "moot in hylo, prevented by the CP-O06..O08 skip". But two 4,300-digit ints add without ever touching a float, so no skip occurs. BC-1.03.006 says hylo reproduces the no-write and the parse re-fails every refresh, i.e. frozen. CP-O09's named owner, BC-1.03.005, does not carry it. Taxonomy :128 ("int64 accumulation overflow is skipped") also contradicts BC-1.03.006 EC-002, which requires big ints to be stored exactly. | product-owner |
| ADV-P3-C10 | MEDIUM | testability / DI-012 | BC-1.03.006 vectors; BC-1.03.010 vectors; BC-1.03.018:77-80,129 | CP-O06..O08 have no canonical vector with an exact expected cache. The taxonomy (:103-104) requires an edge case plus a canonical vector in each owning BC. BC-1.03.019's 21 rows cover only T01..T07, yet BC-1.03.018 names them as the dedicated tests. | product-owner |
| ADV-P3-C11 | MEDIUM | partial-fix regression | BC-1.03.018:35-42, 22 | Still says "eight transcript crash paths CP-T01..T08" and "defines the seven predicates", but the table has 10 (T01-T07 plus O06-O08). The `modified[]` 1.2.3 entry is duplicated. | product-owner |
| ADV-P3-C12 | MEDIUM | P4 / P7 mis-anchor after OD-161 | BC-1.03.015:31,51-57,108,119,150-152; ARCH-05:31; BC-COMPONENT-MAP:93 | PC3 and Invariant 3 say hylo does no descriptor I/O, yet the BC still anchors `platform.StatFD` / `fd_*.go`. The Purity section ("reads fd table, nondeterministic") describes legacy. The H1 "(int = fd)" no longer describes hylo's behavior. PC3 says "truthy int → no transcript" without qualification, while PC4 says out-of-C-int-range ints degrade; it is unclear which applies to hylo. `parity_class` is byte-exact despite the OD-161 exclusion. | product-owner / architect |
| ADV-P3-C13 | MEDIUM | Python claim wrong | BC-1.03.002:87 vs SL:1027-1043 | A float cached `size` raises TypeError only on the incremental path. Cached 39.0 against file size 39 hits `size == off` and returns cached values with no seek. `size < off` resets. A missing key with off > 0 resets. "hylo degrades likewise" therefore over-degrades. | product-owner |
| ADV-P3-C14 | MEDIUM | unspecified rendering | BC-1.07.005 PC2/PC3; BC-1.07.006 PC2/EC-003; BC-1.07.004:54 | Truthy non-string `name`/`label`, `status`, and `model` (when prefixes are empty) render through Python f-string `str()`: `True`, `1.0`, `['x']`, `{'a': 1}`. Only strings and an int `model` are specified. PC4 says `id` is "any JSON scalar", but arrays and objects are echoed too. A `pyfmt.Str` rule is needed. | product-owner |
| ADV-P3-C15 | LOW | broken / stale anchor | BC-1.07.008:121; BC-1.07.001:102 | `#statusline-guard` does not exist; ARCH-03 headings are at :15, 23, 45, 82, 138. BC-1.07.001 says "architect to place", but ARCH-03:133-135 already places `subagent.go`. | product-owner |
| ADV-P3-C16 | LOW | P16 rationale wrong | BC-1.03.007:47-48 | "A negative X marks every call a rebuild" is false: the excess `_w − max(0, growth)` is negative whenever context growth exceeds the write. The range itself is fine. | product-owner |
| ADV-P3-C17 | LOW | range drift | BC-1.03.010:54-56 vs interface-definitions.md:142-143 | The BC omits "(finite)" for `floor_tps` and `stale_factor`. | product-owner |
| ADV-P3-C18 | LOW | P2 DI-012 not cited | BC-1.03.002:117, BC-1.03.006:121, BC-1.03.010:123, BC-1.03.015:103 | Each carries a named deviation (OD-160, OD-156/D4-EX-2, D4-EX-2/CP-O08, OD-161) but does not cite DI-012. | product-owner |
| ADV-P3-C19 | LOW | contradictory wording | BC-1.07.007:53,62-63 vs :78 | Invariant 1 says "format before threshold"; EC-003 says "threshold-then-format" (EC-003 is correct). "Quarter-rounding (banker's)" is imprecise. | product-owner |
| ADV-P3-C20 | LOW | untestable vector | BC-1.07.002:83 | The `"yes"` row's expected output is "per BC-2.02.00x grammar", not concrete bytes. | product-owner |
| ADV-P3-C21 | LOW | P18 path encoding | BC-1.06.001 PC3; BC-1.03.001 PC2 | Lone-surrogate sid or path behavior is unspecified. Python's surrogateescape turns U+DC80..U+DCFF into raw bytes and raises on other surrogates (swallowed, or `isfile` returns False). Go's WTF-8 bytes would name a different file. | product-owner |
| ADV-P3-C22 | COSMETIC | editorial | BC-1.03.006:65,71; BC-1.07.003:83; BC-1.07.004:51; BC-1.07.001:59 | Two postconditions are numbered 5. BC-1.07.003:83 contains non-English text (breaks the repo's "write everything in English" rule). A stray `, )`. The example `hylo --subagent` is confusing. | product-owner |

What I checked against the cited legacy lines and found exact: every canonical cache byte count and value in BC-1.03.002, 003, 004, 005, 006, 007, 008, 009, 011, 012, 013, 016 (T1, T13, T16 and all `lr` values), 017, 019 (all 21 rows plus `BASE`), 020 (C1-C3) and 021, plus the subagent `_fmt_tokens` and clock cells.

### 2. Policy compliance

- P1 append_only_numbering: PASS
- P2 lift_invariants_to_bcs: FINDING C18
- P4 semantic_anchoring_integrity: FINDING C03, C12, C15
- P5 creators_justify_anchors: PASS
- P6 subsystem name verbatim: PASS (SS-01 throughout)
- P7 BC H1 = BC-INDEX = PRD title: titles all sync; FINDING C12 (H1 does not describe the postconditions)
- P12 settled_decisions_are_constraints: FINDING C08
- P13 parity_before_behavior_change: FINDING C01, C02, C04, C07, C13
- P14 public_repo_hygiene: PASS (hygiene-term and IP/path scan of the perimeter is clean)
- P16 thresholds_are_explained: FINDING C16
- P17 ledger_format_frozen: PASS (nothing touched)
- P18 cross_platform_from_day_one: FINDING C21 (LOW); the Windows edge cases are honestly marked not-executed
- P19 go_hardening_toolchain: N.A.
- P20 config_over_code: FINDING C05; OD-05 is respected (no legacy env alias read)
- P21 public_artifact_hygiene: PASS

### 3. Not fully read, and claims I could not verify

**Not fully read:**
- BC-1.03.017 after line 99
- BC-1.03.019 after line 129
- BC-1.03.020 after line 119
- BC-1.03.021 after line 99
- BC-1.07.003-008 tail sections (story anchor, brownfield)
- BC-1.06.001 frontmatter
- capabilities.md, test-vectors.md, ARCH-04, and the individual VP files (checked by grep only)

**Python claims I could not verify:**
- The CESU lone-surrogate acceptance, the 993/994 depth edge, and the shared-NaN-object dedup.
- `seek(negative)` raising OSError (as opposed to ValueError).
- My own C07 threshold, which is derived from CPython's rounding rule but was not executed.
- The BC-1.06.002 Windows edge cases.
- The claim that Claude Code treats the degraded line as a row-body miss.

### 4. Novelty

Novelty is **HIGH**. C01-C05 and C06/C07/C09/C10 are new substantive defects, not rewordings of earlier passes.

**NOT_CONVERGED**


## Perimeter C2 (BC-1.04, BC-1.05)

Findings: 14 (high 3, medium 5, low 4, cosmetic 2).

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P3-C2-01 | HIGH | parity / OD-156 coverage | BC-1.05.007:55 (PC1); BC-1.05.002:59-60; BC-1.05.005:70-73; error-taxonomy.md:112-118; legacy SL:616, 623, 255 | **Overflow crash paths in the cost segment are missing.** BC-1.05.007 says "an int formats as its float value". For an exact stdin int of 2^1024 or more (about 309+ digits, under the 4,300-digit limit), `f"{usd:.2f}"` (SL:616) converts to float and raises OverflowError, so the render degrades. A huge `api_ms` raises the same way at `api_ms / 3.6e6` (SL:623). `record_cost` has already written the huge int (SL:234-237). After that, any other session on that lane whose entry passes the API-time gate raises at `usd / (api / 3.6e6)` (SL:255) and degrades on every refresh for up to 30 days. OD-156 rules that stdin-borne overflow at render is a catalogued crash path that the owning BC must carry, but the CP-O register stops at CP-O05 and no BC-1.05.x lists these sites. | product-owner |
| ADV-P3-C2-02 | HIGH | partial-fix propagation (OD-160) | BC-1.04.002:86 (EC-008); BC-1.04.003:85 (EC-009); BC-1.05.004:94 (EC-008) and :114 (VP-001 row); BC-1.05.005:100 (EC-010) | OD-160 gave foreign-cache shapes CP-C01..C10 a named exclusion id, and its siblings were updated (BC-1.01.008:57, BC-1.02.017:69, BC-1.03.002:87-88, VP-020:49). These four BCs still say only "out of parity scope (P3r2 ruling b)" and name no exclusion id. DI-012 requires a named, tested deviation. Blast radius is 4 files. | product-owner |
| ADV-P3-C2-03 | HIGH | contradiction / config registry | BC-1.04.006:42-44; interface-definitions.md:145, 196-199 vs BC-2.02.006:49-50, BC-2.01.005:54-55 | `statusline.queue.yellow` is a P1 Bool key with defined non-default behavior in BC-1.04.006 and in the P1 key table. BC-2.02.006 PC1 says the P1 Bool set is "complete" with sparkline.enabled and git.enabled, and that queue.yellow "joins in P4". BC-2.01.005 PC1 lists the same two keys. A P1 implementer following SS-02 would not grammar-check this key. Blast radius is 2 files. | product-owner |
| ADV-P3-C2-04 | MEDIUM | parity / spec precision | BC-1.04.001:58-63 | **The redirect limit is misstated.** "At most 10 redirects (`max_redirections = 10`)" is not how CPython 3.11 behaves. `HTTPRedirectHandler.redirect_request` refuses when `len(visited) >= max_redirections`, and `visited` is keyed by distinct target URL. So the cap is 10 distinct targets, each followed up to 4 times. Example: A→B→A→B…→C with more than 10 hops is followed by urllib and refused by a Go `CheckRedirect` that counts hops. Result: sample vs no sample. The BC calls these limits normative ("Go must reproduce"). | product-owner |
| ADV-P3-C2-05 | MEDIUM | parity / catch list | BC-1.04.001:74-77, EC table:100-118; legacy SL:177-180, 186 | PC4 lists only KeyError/ValueError/IndexError as per-series skips and TypeError as whole-fetch abort. It leaves out OverflowError. A JSON int literal at or above 2^1024 in `value[1]` makes `float(int)` raise outside the per-series catch, so the whole fetch returns no sample. The JSON float literal `1e400` instead becomes +Inf and is kept. A Go float64 decode turns both into ±Inf. This needs an EC row and a vector. | product-owner |
| ADV-P3-C2-06 | MEDIUM | P16 rationale-code drift (pattern) | interface-definitions.md:163-168, 177-178, 150-152 vs BC-1.05.001:132, BC-1.05.004:126, BC-1.05.005:130, BC-1.05.002:117, BC-1.05.003:62/130, BC-1.04.011:44, BC-1.04.002:45 | The registry and the BCs give different rationale classes for the same thresholds. T-022, T-023 and T-043: "derived" in the BC, `DOC` in the registry. T-020, T-021 and T-024: "owner decision/design" in the BC, `Dv` in the registry. T-018: "owner design" vs `DOC`. T-044: "derived" vs `J`. T-053 (power): "derived" in the BC, while the registry has `DOC` and no T-id. T-001: "convention" vs `DOC`. The registry text treats the codes as mutually exclusive (:218-220). | architect |
| ADV-P3-C2-07 | MEDIUM | config range ambiguity | BC-1.05.005:59-62; interface-definitions.md:150; BC-1.05.005:117 (VP row) | The range for `statusline.cost.percentiles` is "each in [0,1]" with no ordering rule. The BC says "p75 ≤ p95 ratified by the architect", which does not say whether (0.95, 0.75) is a config error. The VP-021 property "p75 ≤ p95 whenever a pair is returned" fails under that config. The same open "architect to ratify" note sits in normative BC-1.04.007:43-44 (kv.cells cap). [owner-question] | architect |
| ADV-P3-C2-08 | MEDIUM | VP↔BC coherence (pattern) | VP-030:57-72; VP-021:52-62 vs the VP tables in BC-1.04.001:133, BC-1.04.009:108, BC-1.05.007:101 (fuzz) and BC-1.04.002/004/006/007/009/013/017/021, BC-1.05.001/002/003/005 (testing/quick) | The BCs claim fuzz (Tier C differential) and property-test proofs under VP-030/VP-021. Those VP documents list only unit/table and golden methods, and their proof tables contain no fuzz or property harness. The verification claims cannot be traced. | architect |
| ADV-P3-C2-09 | LOW | sibling propagation | BC-1.04.015:47-48, 54 | Invariant 1 and PC1 hard-code `min(ceil(kv/25), 4)` and `Ceil(NaN/25)`. After pass-2 C2-04, BC-1.04.007 PC3 defines cells as `C = statusline.kv.cells`. BC-1.04.015 does not say that its table pins C = 4 only. | product-owner |
| ADV-P3-C2-10 | LOW | parity / key identity | BC-1.04.001:81-87; VP row :133 | (a) A string `"5"` and an int `5` `__name__` do not collide in Python, so both are stored and `json.dump` writes two `"5"` keys (SL:203). On reload the last one wins. (b) The JSON `NaN` constant is one shared object, so two NaN names collide through dict identity. A Go `map[string]float64` model diverges under the VP-030 "same map (keys, order)" fuzz differential. | product-owner |
| ADV-P3-C2-11 | LOW | testability | BC-1.05.002:85 (EC-005) | The expected result says "with a pair, grey", but the same row admits that recorded 0.0 rates exist. If at least 75% of qualifying rates are 0.0, then p75 = 0.0 and `0.0 >= p75` gives yellow or red. The row needs a conditional or a pinned pair. | product-owner |
| ADV-P3-C2-12 | LOW | anchor label | BC-1.04.001:133 | VP-022 ("the status line never reads the ledger") is paired with the property "Go fetch returns the same map as legacy". The VP and BC link is valid (VP-022's source BC is BC-1.04.001), but the row assigns the wrong property to it. | architect |
| ADV-P3-C2-13 | COSMETIC | internal inconsistency | BC-1.04.013:96 vs BC-1.04.001:92 | "Fake-metrics request count = 1" conflicts with redirect hops counting as requests (BC-1.04.001 Inv 1). | product-owner |
| ADV-P3-C2-14 | COSMETIC | title | BC-1.05.008:36, :40 | The title says "20 seeded sessions" but the seed table has 21 keys (s01-s12, g13-g20, sess-self). | product-owner |

Checked and found correct (re-derived by hand from the legacy lines):
- BC-1.04.020: all 11 steps, both pinned row byte strings, and the key order.
- BC-1.04.009: the sparkline vectors and fade RGB values (including the 0.7000000000000001 case at i=2).
- BC-1.04.015 and BC-1.04.007: the KV cell and percent table and the host-share boundaries (0.005, 0.05).
- BC-1.04.019: the TTFT rounding ties.
- BC-1.04.017: the idle ages.
- BC-1.04.011: the power and cents vectors.
- BC-1.05.005: percentile indices and all vectors, including the OD-138 NaN Timsort orderings.
- BC-1.05.008: the goldens and thresholds ((24,30) and (20,26)).
- BC-1.05.006: the legacy duplicate-key tail.
- BC-1.05.009: the write vectors.

## 2. Policy compliance

- P1 PASS. IDs are contiguous (BC-1.04.001-021, BC-1.05.001-009).
- P2 PASS. DI-007, DI-008 and DI-012 are cited where they apply.
- P4 FINDING: 08, 12.
- P5 PASS.
- P6 PASS. SS-01 matches the ARCH-INDEX registry.
- P7 PASS. All 30 titles match across H1, BC-INDEX and PRD (14 is cosmetic).
- P12 PASS. No settled decision is reopened; 07 is tagged [owner-question].
- P13 FINDING: 01, 04, 05, 10.
- P14 PASS. Only RFC 5737 IPs appear; the hygiene-term scan is clean.
- P16 FINDING: 06.
- P17 PASS. Metric names match legacy.
- P18 PASS.
- P19 N.A. (nothing in these BCs touches the hardening toolchain).
- P20 FINDING: 03, 07. No DGX_* aliases found.
- P21 PASS.

## 3. Files not fully read, and claims I could not verify

- Read in full: all 30 BCs, legacy SL:1-940 and 1180-1246, VP-020, the VP-030 body, and the relevant sections of interface-definitions and error-taxonomy.
- Only grepped or skimmed: prd.md (BC table rows only), ARCH-03 (lines 95-143), ARCH-04 (lines 25-95), VP-021 and VP-031, invariants.md and capabilities.md (registry rows only).
- Not opened: test-vectors.md and BC-2.01.004 (the registry golden).
- From memory of CPython 3.11, not executed:
  - `len(visited)` redirect semantics (04).
  - 308 support in 3.11 urllib.
  - `format(huge_int, '.2f')` raises OverflowError via `PyNumber_Float` (01).
  - The json decoder's shared NaN constant (10b).
  - `round(True, 4)` returns int `1` (matches BC-1.05.009).
- Outside this perimeter, deferred to the cross-story/wave-gate review: ARCH-04:34 names the git cache `git-<sha1[:16]>.json`, but legacy SL:406 writes `statusline-git-{key}.json`.

## 4. Novelty

**Novelty: MEDIUM.** Findings 01, 04, 05 and 10 are new Python-semantics gaps. 02, 03 and 06 are propagation and coherence drift left over from the pass-2 fixes.

**NOT_CONVERGED**


## Perimeter D (SS-02..SS-06 BCs)

Findings: 40 (high 10, medium 17, low 13, cosmetic 0).

## Adversarial Review: Phase 1d Pass 3, Perimeter D (SS-02..SS-06 BCs)

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P3-D01 | HIGH | contradiction / parity boundary | BC-5.02.003:70-71, 80-83; BC-1.01.002:73-74 | The depth recipe's test line wraps `"["·d + "]"·d` inside an outer object, so the total depth is d+1. The recipe then says "the largest accepted d is L" with L = 993 total depth. BC-1.01.002 EC-005 pins "992 nested arrays (total depth 993)". Followed literally, the recipe gives 994. EC-010 cannot be turned into an unambiguous test. | product-owner |
| ADV-P3-D02 | HIGH | contradiction with ARCH-06 signature canon | BC-5.04.002:35, 59-60, 102; ARCH-06:121, 126-127 | The BC declares `LocalToUnix(...) (float64, bool)` and says this is "aligned with the reconciled ARCH-06 row". ARCH-06 canon says `(int64, error)`, "ErrValue (not a bool)". The vectors use `ok = false`. | product-owner |
| ADV-P3-D03 | HIGH | contradiction with ARCH-06 signature canon | BC-5.04.003:38-40, 47, 58; ARCH-06:119, 127-128 | The BC declares `TimeFloat(ns int64)` and claims alignment with ARCH-06. ARCH-06 says "TimeFloat takes time.Time (BC-5.04.003)". | product-owner |
| ADV-P3-D04 | HIGH | OD-155 propagation / P12 | BC-6.01.001:75-78; ARCH-07 (grep finds no `subagent`) | The fixed oracle argv says "`--subagent` is never passed (OD-14)", but OD-155 supersedes OD-14. VP-010 and BC-1.07.004 require Python-written subagent goldens, which the oracle can then never produce. BC-6.03.001 (goldens A/B/C only) and the BC-6.04.003 generator domain have no subagent leg either. | product-owner |
| ADV-P3-D05 | HIGH | contradiction (CLI routing) | BC-4.01.002:40-44, 54-56, 61-63, 83 (EC-004); BC-1.07.001:61, 75 | BC-1.07.001 says `--subagent` at any index routes before flag handling, regardless of other unknown flags (legacy SL:1240 checks `in sys.argv[1:]`). BC-4.01.002 says any other flag prints the unknown-flag line first, and that `-- --subagent` is a normal render. `statusline --x --subagent` and `-- --subagent` get opposite outcomes. VP-002:89 vs :93 carries the same split. | product-owner |
| ADV-P3-D06 | HIGH | fail-closed harness made unsatisfiable | BC-6.03.004:111-121; BC-6.03.002:69-73; BC-2.02.001:81-86 | For Boolean, Enum and URL D4-EX-3 cases, scope `stdout` keeps the caches "compared to the oracle". The BC itself notes Go writes no caches while legacy renders and writes them. BC-6.03.002 PC-3 fails any file present on one side only, so these cases can never pass. BC-6.03.002 EC-005 says the entry asserts "Go writes no cache", which contradicts this scope. | product-owner |
| ADV-P3-D07 | HIGH | OD-155 propagation (blast radius 4 files) | BC-2.02.006:48-50 ("the complete P1 set"); BC-2.01.005:54-55; BC-2.01.004:47-49; BC-2.01.001:112; ARCH-02:29; interface-definitions:154 | `statusline.subagent.enabled` is a P1 Bool key in ARCH-02, the PRD and BC-1.07.002. The SS-02 BCs name only sparkline.enabled and git.enabled as the complete Bool set. They omit it from the registry precondition and from the all-defaults vector. | product-owner |
| ADV-P3-D08 | HIGH | missing contract: int/float mixing | ARCH-06:28 ("CPython 3.11 arithmetic on Num"); BC-5.01.003:60-63; legacy SL:435, 599, 878, 1171 | No SS-05 BC pins: `float(int)` with ErrOverflow; true division (exact int/int division, OverflowError when an int operand meets a float); exact int-vs-float comparison. SS-01 depends on all of these (BC-1.02.006 EC-010, BC-1.02.025 EC-010, BC-1.03.006). `F(x float64)` cannot take an int operand (`{rb:.0f}` with an int `rb`). Max/Min PC-5 does not say comparisons are exact: `Max(9007199254740992.0, 2**53+1)` returns the int in Python, but a float-converting Go returns the float. | product-owner |
| ADV-P3-D09 | HIGH [process-gap] | systemic escape-rendering corruption | BC-5.02.001:103; BC-5.02.004:74-75; cross-perimeter BC-1.07.004:52-53 | Cells meant as `\uXXXX` escapes show raw characters. Examples: Dumps of a raw surrogate pair is shown as the raw emoji yet called an "escaped surrogate pair, 14 chars". EC-004 "JSON escape text" also shows the raw emoji. BC-1.07.004 shows "»→`»`". ESC and lone surrogates kept their escapes, so some transform appears to unescape non-ASCII. Expected bytes are ambiguous. The "per BC-5.01.002" anchors are also wrong (that BC is ParseInt/ParseFloat). | product-owner |
| ADV-P3-D10 | HIGH | OD-155 propagation into SS-05/SS-06 consumer lists (partial-fix, 7 files) | BC-5.01.001:118; BC-5.01.003:114; BC-5.01.004:102; BC-5.02.005:109; BC-5.02.006:40, 52-53; BC-5.04.003:41-42, 102; BC-6.01.003:74-75 | These subagent sites are absent from the lists: `_fmt_tokens` `.Nf` (SL:882-885); `max`, `//`, `%`, `int()` (SL:919-920); `:02d` (SL:920); `str()` of name/model/status (SL:896, 908, 922); the 10th clock read (SL:889). Dumps is scoped to "the four cache files", yet BC-1.07.004 needs it for the stdout `json.dumps` (SL:924). | product-owner |
| ADV-P3-D11 | MEDIUM | unmeasured parity boundary | BC-5.02.003:72-76 ("both current sites"); ARCH-06:30; legacy SL:930 | The `main_subagent` `json.load` is a third stdin call site. Its depth budget is neither measured nor pinned, even though PC-7 requires end-to-end measurement per site. BC-1.07.003 has no depth row. | product-owner / architect |
| ADV-P3-D12 | MEDIUM | encoder failure paths unspecified | BC-5.02.001:80-81 (Inv 4); BC-5.02.006:52-53; legacy SL:202-203 | Cache writes use `json.dump`, the pure-Python encoder. It raises ValueError on ints over 4,300 digits, which accumulated token sums can reach, and has its own recursion depth. Legacy then swallows the error and leaks a partial temp file, while Go's `Dumps` (no error return) would write the cache. The claim "encoder budget = decoder budget" is asserted, not measured, and the temp-file exclusion does not cover this case. | product-owner |
| ADV-P3-D13 | MEDIUM | P18 (Windows oracle) | BC-5.04.001:59-62; BC-5.04.002 Inv 2 | On Windows, CPython's naive `.timestamp()` goes through MSVC `localtime_s`, which raises OSError (not ValueError) for negative probes and for years above 3000. That contradicts "only ValueError occurs" and the "9999-12-31 → float under UTC" claim on the windows-2025 UTC leg. Not verified on Windows. | product-owner |
| ADV-P3-D14 | MEDIUM | uncontracted per-OS helpers / P18 | BC-5.03.004:62-63; legacy SL:373, 375, 390; ARCH-06:60-65 | The BC claims to serve `abspath`, `join` and `dirname` but contracts only normpath and basename. Windows `abspath` uses GetFullPathNameW and cwd, which is not pure. The caller-side GOOS selection of the normpath flavor (in the statusline package, not `internal/platform`) is not justified. | architect |
| ADV-P3-D15 | MEDIUM | mis-anchor (P4) | BC-5.01.004:113 | Cites "countdown `{je:3d}` form". No `:3d` exists in legacy; the countdown uses `:02d` (SL:525/527). | product-owner |
| ADV-P3-D16 | MEDIUM | contradiction (byte order) | BC-2.01.002:79-83; BC-2.03.001:50-53 | `config validate` stderr: BC-2.01.002 puts the unknown-setting warning before the cardinality error; BC-2.03.001 puts errors first, then warnings. | product-owner |
| ADV-P3-D17 | MEDIUM | contradiction | BC-3.01.001:65-66; BC-2.01.004:82-85 | BC-3.01.001 says `paths.cache_dir` is "the one explicit owner exception" and every other default equals legacy. BC-2.01.004 lists two exceptions (adds `backends[0].model_prefixes`, OD-111). | product-owner |
| ADV-P3-D18 | MEDIUM [owner-question] | OD-155 gap | BC-2.02.001:43-48, 55-56; BC-4.01.002:54-56; BC-1.07.002:64 | Under `--subagent`, BC-2.02.001 does not say whether the grey config-error line (which is not NDJSON) goes to the agent panel. Legacy crashes at import there (blank, exit 1). | product-owner |
| ADV-P3-D19 | MEDIUM | exclusion closure | BC-6.03.004:87-89 | OD-159, OD-160 and OD-161 name "stories owning ... verbs (SS-01)" as their defining contract, with no BC and no table test. Every other id has both. | product-owner |
| ADV-P3-D20 | MEDIUM | spec self-inconsistency | BC-6.03.004:56-75, 158; BC-6.03.003:92-94 | The validator requires exactly six keys (`package` and `scope` included; a missing key fails), yet the canonical entries omit both. `expected_output_file` is defined as a JSON object, but the examples use `expected.go-cache-listing.txt` and `expected.stdout`. | product-owner |
| ADV-P3-D21 | MEDIUM | fail-closed wording | BC-6.02.004:73-77 vs :101, :111 | PC-3 fails only if a cache is "absent in both directions". EC-004 and the vector check each direction separately. | product-owner |
| ADV-P3-D22 | MEDIUM | CI unsatisfiable as ordered | BC-6.04.001:65-74; BC-6.01.001:79-82 | GitHub Actions always sets `CI=true`. Step 3 (`go test ./...`) runs before step 4 exports `HYLO_PARITY_PYTHON`, so Tier A fails in step 3 unless it is excluded from that step, and no exclusion is specified. | architect |
| ADV-P3-D23 | MEDIUM | uncontracted shim duty | BC-6.01.002:114-117; BC-6.01.003:41-48, 63-71; BC-6.03.002:105 | The UTF-8, `newline="\n"` stdio reconfigure is assigned to the shim in BC-6.01.002, but the shim contract (BC-6.01.003) never lists it and no canary checks it. BC-6.03.002 EC-006 still relies on it. | product-owner |
| ADV-P3-D24 | MEDIUM | fidelity gap | BC-6.02.002:53, 74-75 | Captured `stdin` is stored as a JSON object and rewritten. The re-serialization (big ints, NaN, duplicate keys, key order, escaping) is unspecified, which weakens the OD-107 byte-parity-on-real-inputs criterion. | product-owner |
| ADV-P3-D25 | MEDIUM | Tier C domain gaps | BC-6.04.003:61-69 | The domain filter omits non-UTC naive timestamps on Windows (BC-6.02.003 PC-8), the OD-159/160/161 classes and `--subagent`. A clean night on all three OSes (the P1 gate) is not well defined. | product-owner |
| ADV-P3-D26 | MEDIUM | mis-anchor (P4) | BC-6.01.001:131 | The Architecture Module column says "`internal/statusline` parity harness" while BC-COMPONENT-MAP and ARCH-INDEX say `internal/parity`. | product-owner |
| ADV-P3-D27 | MEDIUM | test-hook ambiguity | BC-5.04.003:49-54, 63-64 | "TimeFloat(HYLO_TEST_NOW)" passes a decimal string to an ns-int64 function; the float→ns→float round trip can drift by one ulp from `float(s)`. The rule for what counts as malformed (`nan`, `inf`, `_`, whitespace) is unpinned. | product-owner |
| ADV-P3-D28 | LOW | stale text | BC-4.01.002:59 | The stderr suffix "(hylo statusline takes no flags)" is false now that `--subagent` is valid. | product-owner |
| ADV-P3-D29 | LOW | anchor drift | VP-006:41-42, 57 | Cites BC-5.02.003 lines 71-72, 65-66 and 67 ("quoted 989/990"); those lines no longer hold that content. | architect |
| ADV-P3-D30 | LOW | golden format | BC-5.02.002:93 vs :131 | The stated output is `#\t<len>\t<repr>`, but the code prints space-separated values. CI compares a fresh generation against the committed table. | product-owner |
| ADV-P3-D31 | LOW | stale provenance | BC-6.04.003:133 | Traceability still says "Linux nightly", "owner-picked number of nights" and "3 nights"; the body follows OD-149. | product-owner |
| ADV-P3-D32 | LOW | error-detail rule | BC-2.02.001:77-79 | `[from EnvName(key)]` does not fit the backends reason, where BC-2.01.002 names `HYLO_BACKENDS_1_*`, not `EnvName("backends")`. | product-owner |
| ADV-P3-D33 | LOW | wording / edge | BC-5.01.006:58-59; BC-5.01.004:96 | MaxSeq: "or when every later element also fails to displace" implies a non-first NaN can win, which it cannot. D: no vector for MinInt64 (`|n|` overflows int64); the VP wording there is garbled. | product-owner |
| ADV-P3-D34 | LOW | unspecified | BC-5.02.005:52-53 | The dict repr key/value separator `': '` is not stated. | product-owner |
| ADV-P3-D35 | LOW | recipe wording | BC-5.01.005:62-70; ARCH-06:29 | The BC says to take digits from `'e'` and that the `'g'` recipe breaks parity; ARCH-06 calls a `'g'`-digits recipe normative. | architect |
| ADV-P3-D36 | LOW | edge gaps | BC-2.03.002:66-69, 72-75; BC-3.01.001:60 | An empty `HYLO_PATHS_CACHE_DIR` is undefined for `config path`. A trailing slash in an override is printed "as given", while the store path has "no trailing separator", so OD-165's "same directory" does not hold byte for byte. | product-owner |
| ADV-P3-D37 | LOW | reserved names | BC-2.01.001:79-82; BC-2.01.004:77-78 | `HYLO_TIMING_GATE` (harness setting, BC-6.04.002) is not reserved, so it would be warned as unknown and is not collision-checked. | product-owner |
| ADV-P3-D38 | LOW | scope rule | BC-6.03.004:152 | "Scopes must not both claim stdout", yet OD-30 and OD-76 both default to `stdout+caches`, so the cited example is invalid. | product-owner |
| ADV-P3-D39 | LOW | not wired into CI | BC-6.04.002:56-57, 71 | "Written as a CI artifact" and "nightly matrix", but neither BC-6.04.001 nor BC-6.04.003 runs `TestTiming`. | architect |
| ADV-P3-D40 | LOW [owner-question] | P21 check | BC-6.02.001:80 | Confirm the hostname example in the hygiene pattern list is synthetic (not quoted here). | product-owner |

### 2. Policy compliance

- **P1** PASS.
- **P2** PASS.
- **P4** FINDING: D09, D15, D26, D29.
- **P5** PASS.
- **P6** PASS (SS-IDs match the ARCH-INDEX registry).
- **P7** FINDING: D02, D03 (H1/body signatures contradict ARCH-06). Every H1 matches its BC-INDEX title.
- **P12** FINDING: D04 (OD-14 cited after OD-155), D07.
- **P13** FINDING: D06, D19.
- **P14** PASS (RFC 5737 IPs, placeholder paths).
- **P16** PASS, with a LOW note on D:width 0..67, whose rationale is weak.
- **P18** FINDING: D13, D14.
- **P19** N.A. (BC-6.04.001 covers gofmt, vet and -race; no further hardening tools are in scope).
- **P20** PASS.
- **P21** PASS, with D40 open for confirmation.

### 3. Not fully read / not verified

- **Partial reads:** BC-2.02.002 and BC-2.02.003 from line 30, BC-2.02.004/005/006 lines 34-105 only, BC-2.03.001 lines 30-118, SS-03 and SS-04 files from line 28. Frontmatter for these was checked by grep.
- **Not reread this pass:** prd-supplements beyond interface-definitions, capabilities.md, invariants.md, ARCH-02/03/05/07/08 bodies, and VPs other than VP-006.
- **Python claims not run:**
  - Windows `localtime_s` OSError path (D13).
  - Whether `json.dump`'s pure-Python encoder flips at the same depth as `load_cache` (D12).
  - The CPython 3.11.7 4,300-digit leading-zero counting.
  - Golden A/B/C byte totals (only spot-checked: ⏱, ⌂ and countdown values recomputed and match).

### 4. Convergence

**Novelty: HIGH.** D01, D04-D08, D10 and D12 are new defect classes, mostly OD-155 propagation and newly found contradictions, not rewordings of earlier findings.

**NOT_CONVERGED.**
