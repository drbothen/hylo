---
document_type: adversarial-review-index
phase: 1d
pass: 3
date: 2026-11-18
findings: 150
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P3 Index — Phase 1d Adversarial Spec Review, Pass 3

Every finding from pass 3, indexed from the verbatim perimeter reports in `pass-3.md`. Severity totals: HIGH 36, MEDIUM 61, LOW 48, COSMETIC 5 — total 150. Pass 3 is a REGRESSION vs pass 2 (116 findings, 17 HIGH): delta +34, HIGH count +19; the root-cause analysis (new scope added without pre-validation) is recorded in `../convergence-trajectory.md`.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P3-A01 | HIGH | contradiction | architecture/ARCH-01-binary-cli.md:45-51 | architect + product-owner |  |
| ADV-P3-A02 | HIGH | interface cannot express BC | ARCH-01-binary-cli.md:39,48 | architect |  |
| ADV-P3-A03 | HIGH | missing harness capability | ARCH-07-parity-harness.md:97-98 | architect |  |
| ADV-P3-A04 | HIGH | contradiction (NFR method) | nfr-catalog.md:24,67-71 | product-owner |  |
| ADV-P3-A05 | HIGH | config range contradicts BC | interface-definitions.md:155,163,164,171,172,174,175,176,184,185 | product-owner |  |
| ADV-P3-A06 | HIGH | settled decision violated (P12) | ARCH-05-platform.md:31,63 | architect |  |
| ADV-P3-A07 | HIGH | count drift (partial-fix regression, blast radius 4) | prd.md:41-45,111,124 | product-owner |  |
| ADV-P3-A08 | HIGH | assumption mis-stated | assumptions-register.md:29 | product-owner | owner-question |
| ADV-P3-A09 | MEDIUM | contradiction (never-blank) | prd.md:432,477 | product-owner |  |
| ADV-P3-A10 | MEDIUM | coverage gap | prd.md:477,493 | product-owner |  |
| ADV-P3-A11 | MEDIUM | traceability gap | prd.md:548-569 | product-owner |  |
| ADV-P3-A12 | MEDIUM | stale placeholder (P4) | prd.md:132-136 | product-owner |  |
| ADV-P3-A13 | MEDIUM | subsystem-rule mis-statement (P6) | ARCH-INDEX.md:48-49 | architect |  |
| ADV-P3-A14 | MEDIUM | config over code (P20) | interface-definitions.md:154,187 | product-owner + architect | owner-question |
| ADV-P3-A15 | MEDIUM | stale after OD-156 | ARCH-06-pyfmt.md:19,42-43 | architect |  |
| ADV-P3-A16 | MEDIUM | CI checks nothing (P11) | cicd-setup.md:24-26,75-82 | architect (devops) |  |
| ADV-P3-A17 | MEDIUM | hygiene scan gap (P14/P21) | cicd-setup.md:90-95 | architect (devops) | process-gap |
| ADV-P3-A18 | LOW | hygiene fail rule incomplete | cicd-setup.md:82 | architect (devops) |  |
| ADV-P3-A19 | LOW | oracle pin ambiguity | nfr-catalog.md:26 | product-owner |  |
| ADV-P3-A20 | LOW | reserved-name list incomplete | ARCH-07:91 | architect |  |
| ADV-P3-A21 | LOW | wrong anchor (P4) | risk-register.md:30 | architect |  |
| ADV-P3-A22 | LOW | contradiction | risk-register.md:32 vs error-taxonomy.md:129-131 | architect |  |
| ADV-P3-A23 | LOW | register drift | risk-register.md:18-21 | product-owner + architect |  |
| ADV-P3-A24 | LOW | stale exclusion description | ARCH-00-overview.md:30 | architect |  |
| ADV-P3-A25 | LOW | contradicts OD-158 | ARCH-06-pyfmt.md:58 | architect |  |
| ADV-P3-A26 | LOW | stale message text | interface-definitions.md:31,87 | product-owner |  |
| ADV-P3-A27 | LOW | threshold unexplained (P16) | interface-definitions.md:144,146 | product-owner |  |
| ADV-P3-A28 | LOW | untested release targets (P18) | cicd-setup.md:103 | architect (devops) |  |
| ADV-P3-A29 | COSMETIC | typo | ARCH-01-binary-cli.md:81 | architect |  |
| ADV-P3-A2-01 | HIGH | L2 contradicts P1 BCs | domain-spec/invariants.md:31 | business-analyst |  |
| ADV-P3-A2-02 | HIGH | VP fails a correct impl | VP-002:89 (also :107-111) | architect |  |
| ADV-P3-A2-03 | HIGH | VP mis-states the computation; wrong oracle | VP-039:37-46, :84-94 | architect |  |
| ADV-P3-A2-04 | HIGH | Cross-platform: skeleton passes a wrong impl | VP-034:41-45, :86-99 | architect |  |
| ADV-P3-A2-05 | HIGH | Vacuous VP (can never fail) | VP-040:97-105, :118 | architect |  |
| ADV-P3-A2-06 | HIGH | CI positive coverage | VP-009:75 | architect | process-gap |
| ADV-P3-A2-07 | MEDIUM | Skeleton weaker than the property | VP-001:86, :96-101 | architect |  |
| ADV-P3-A2-08 | MEDIUM | Go API misuse | VP-005:85 | architect |  |
| ADV-P3-A2-09 | MEDIUM | Skeleton fails a correct impl | VP-036:77-80 vs :44-46 | architect |  |
| ADV-P3-A2-10 | MEDIUM | Contradiction with BC | VP-010:42 | architect |  |
| ADV-P3-A2-11 | MEDIUM | Cross-platform gap | VP-026:44-46 vs BC-6.04.001:71-73, VP-010:37-42 | architect |  |
| ADV-P3-A2-12 | MEDIUM | "Non-vacuous" claim overstated | VP-022:43-48, :71-79, :109-117 | architect |  |
| ADV-P3-A2-13 | MEDIUM | Semantic mis-anchor | VP-INDEX.md:218, :105, :314 | architect / product-owner |  |
| ADV-P3-A2-14 | MEDIUM | P2 enforcer column stale | invariants.md:30, :31, :35 | business-analyst |  |
| ADV-P3-A2-15 | MEDIUM | Resolved item contradicts a later ruling | owner-validation-list.md:211-215, :217-220 | business-analyst |  |
| ADV-P3-A2-16 | MEDIUM | Assessment claim no longer holds | dtu-assessment.md:21, :26-28, :45-46, :81, :177 | architect |  |
| ADV-P3-A2-17 | MEDIUM | Partial-fix propagation | VP-012:13, :52-55, :120-123 | architect |  |
| ADV-P3-A2-18 | MEDIUM | VP contradicts a ruling | VP-029:43 | architect |  |
| ADV-P3-A2-19 | MEDIUM | VP `bcs:` vs body | VP-019:13 vs :48-50 | architect |  |
| ADV-P3-A2-20 | MEDIUM | Unanchored claim | VP-009:53-54 | architect |  |
| ADV-P3-A2-21 | MEDIUM | DI-012 ambiguity | VP-005:43-44 | architect | owner-question |
| ADV-P3-A2-22 | LOW | Missing call site | VP-006:45-54 | architect |  |
| ADV-P3-A2-23 | LOW | Vacuous / stale invariant claims | VP-028:57 | architect |  |
| ADV-P3-A2-24 | LOW | Go API | VP-012:131 | architect |  |
| ADV-P3-A2-25 | LOW | Ambiguity | VP-015:89-96 | architect |  |
| ADV-P3-A2-26 | LOW | L2 wording | invariants.md:30 vs capabilities.md:31 | business-analyst | pending intent verification |
| ADV-P3-A2-27 | LOW | Stale derived note | architecture-feasibility-report.md:102 | architect |  |
| ADV-P3-B01 | HIGH | settled-decision drift (P12) | BC-1.01.001:81 (EC-007), :43-44 (PC1), :113 (cites OD-14) | product-owner |  |
| ADV-P3-B02 | HIGH | cross-platform parity (P18) | BC-1.02.004:47-48 (PC2) | architect / product-owner | owner-question |
| ADV-P3-B03 | HIGH | mis-anchoring; partial-fix propagation (5 files) | BC-1.01.003:138, .004:115, .005:127, .006:130, .007:117 | product-owner |  |
| ADV-P3-B04 | HIGH | partial-fix propagation (2 files) | BC-1.02.027:156-160 | product-owner |  |
| ADV-P3-B05 | MEDIUM | legacy mismatch | BC-1.02.014:59, :91-92 (EC-012/013) | product-owner |  |
| ADV-P3-B06 | MEDIUM | VP cannot catch the defect | BC-1.02.024:97 vs :57 | product-owner |  |
| ADV-P3-B07 | MEDIUM | OD-162 applied inconsistently (P20) | BC-1.02.006:56-65 vs :79-86 | product-owner / architect |  |
| ADV-P3-B08 | MEDIUM | key registration (P20, OD-162) | interface-definitions:106 (and :108) | architect |  |
| ADV-P3-B09 | MEDIUM | exclusion discipline (DI-012) | BC-1.02.005:85,87,88 (EC-005 null, EC-006 `5`, EC-008 `true`) | product-owner |  |
| ADV-P3-B10 | MEDIUM | dangling anchors (P4) | BC-1.01.001:125, .002:132, .003:130, .004/.005/.006/.007/.010 (`#statusline-width`), .008:127, .009:140 | architect | process-gap |
| ADV-P3-B11 | LOW | mis-cited decision | BC-1.01.001:66-69 (Inv 4) | product-owner |  |
| ADV-P3-B12 | LOW | unverified oracle provenance | BC-1.02.022:54, :70 (EC-005), :89-91 | product-owner |  |
| ADV-P3-B13 | LOW | test-vector extraction | BC-1.01.008:91-93 | product-owner |  |
| ADV-P3-B14 | LOW | missing edge case | BC-1.01.002:50-52 | product-owner |  |
| ADV-P3-B15 | LOW | wrong source citation | BC-1.01.003:56 | product-owner |  |
| ADV-P3-B16 | LOW | VP coverage gaps | BC-1.01.001:96-101 | product-owner |  |
| ADV-P3-B17 | LOW | precondition missing | BC-1.02.017:87 (EC-010) | product-owner |  |
| ADV-P3-B18 | COSMETIC | wording | BC-1.02.014:83 | product-owner |  |
| ADV-P3-C01 | HIGH | parity / bytes wrong (pattern, 3 files) | BC-1.07.004:37,52-53,57,82 | product-owner | process-gap |
| ADV-P3-C02 | HIGH | legacy mismatch / contradiction within the BC | BC-1.07.005:58-60, 103 vs SL:845-846 | product-owner |  |
| ADV-P3-C03 | HIGH | mis-anchor | BC-1.03.018:72 | product-owner |  |
| ADV-P3-C04 | HIGH | uncatalogued crash path | BC-1.07.007:36-37,109 | product-owner |  |
| ADV-P3-C05 | HIGH | P20 config over code; sibling drift | BC-1.07.005:116 | product-owner / architect |  |
| ADV-P3-C06 | MEDIUM | deviation design defect | BC-1.03.018:73 | product-owner | owner-question |
| ADV-P3-C07 | MEDIUM | Python semantics (not executed; derived from CPython rounding) | BC-1.03.006:55-56 | product-owner |  |
| ADV-P3-C08 | MEDIUM | P12 closed exclusion set | BC-1.03.006:59-60 vs error-taxonomy.md:159-161, BC-1.03.018:77-80 | product-owner |  |
| ADV-P3-C09 | MEDIUM | contradiction | error-taxonomy.md:128,144 | product-owner |  |
| ADV-P3-C10 | MEDIUM | testability / DI-012 | BC-1.03.006 vectors | product-owner |  |
| ADV-P3-C11 | MEDIUM | partial-fix regression | BC-1.03.018:35-42, 22 | product-owner |  |
| ADV-P3-C12 | MEDIUM | P4 / P7 mis-anchor after OD-161 | BC-1.03.015:31,51-57,108,119,150-152 | product-owner / architect |  |
| ADV-P3-C13 | MEDIUM | Python claim wrong | BC-1.03.002:87 vs SL:1027-1043 | product-owner |  |
| ADV-P3-C14 | MEDIUM | unspecified rendering | BC-1.07.005 PC2/PC3 | product-owner |  |
| ADV-P3-C15 | LOW | broken / stale anchor | BC-1.07.008:121 | product-owner |  |
| ADV-P3-C16 | LOW | P16 rationale wrong | BC-1.03.007:47-48 | product-owner |  |
| ADV-P3-C17 | LOW | range drift | BC-1.03.010:54-56 vs interface-definitions.md:142-143 | product-owner |  |
| ADV-P3-C18 | LOW | P2 DI-012 not cited | BC-1.03.002:117, BC-1.03.006:121, BC-1.03.010:123, BC-1.03.015:103 | product-owner |  |
| ADV-P3-C19 | LOW | contradictory wording | BC-1.07.007:53,62-63 vs :78 | product-owner |  |
| ADV-P3-C20 | LOW | untestable vector | BC-1.07.002:83 | product-owner |  |
| ADV-P3-C21 | LOW | P18 path encoding | BC-1.06.001 PC3 | product-owner |  |
| ADV-P3-C22 | COSMETIC | editorial | BC-1.03.006:65,71 | product-owner |  |
| ADV-P3-C2-01 | HIGH | parity / OD-156 coverage | BC-1.05.007:55 (PC1) | product-owner |  |
| ADV-P3-C2-02 | HIGH | partial-fix propagation (OD-160) | BC-1.04.002:86 (EC-008) | product-owner |  |
| ADV-P3-C2-03 | HIGH | contradiction / config registry | BC-1.04.006:42-44 | product-owner |  |
| ADV-P3-C2-04 | MEDIUM | parity / spec precision | BC-1.04.001:58-63 | product-owner |  |
| ADV-P3-C2-05 | MEDIUM | parity / catch list | BC-1.04.001:74-77, EC table:100-118 | product-owner |  |
| ADV-P3-C2-06 | MEDIUM | P16 rationale-code drift (pattern) | interface-definitions.md:163-168, 177-178, 150-152 vs BC-1.05.001:132, BC-1.05.004:126, BC-1.05.005:130, BC-1.05.002:117, BC-1.05.003:62/130, BC-1.04.011:44, BC-1.04.002:45 | architect |  |
| ADV-P3-C2-07 | MEDIUM | config range ambiguity | BC-1.05.005:59-62 | architect | owner-question |
| ADV-P3-C2-08 | MEDIUM | VP↔BC coherence (pattern) | VP-030:57-72 | architect |  |
| ADV-P3-C2-09 | LOW | sibling propagation | BC-1.04.015:47-48, 54 | product-owner |  |
| ADV-P3-C2-10 | LOW | parity / key identity | BC-1.04.001:81-87 | product-owner |  |
| ADV-P3-C2-11 | LOW | testability | BC-1.05.002:85 (EC-005) | product-owner |  |
| ADV-P3-C2-12 | LOW | anchor label | BC-1.04.001:133 | architect |  |
| ADV-P3-C2-13 | COSMETIC | internal inconsistency | BC-1.04.013:96 vs BC-1.04.001:92 | product-owner |  |
| ADV-P3-C2-14 | COSMETIC | title | BC-1.05.008:36, :40 | product-owner |  |
| ADV-P3-D01 | HIGH | contradiction / parity boundary | BC-5.02.003:70-71, 80-83 | product-owner |  |
| ADV-P3-D02 | HIGH | contradiction with ARCH-06 signature canon | BC-5.04.002:35, 59-60, 102 | product-owner |  |
| ADV-P3-D03 | HIGH | contradiction with ARCH-06 signature canon | BC-5.04.003:38-40, 47, 58 | product-owner |  |
| ADV-P3-D04 | HIGH | OD-155 propagation / P12 | BC-6.01.001:75-78 | product-owner |  |
| ADV-P3-D05 | HIGH | contradiction (CLI routing) | BC-4.01.002:40-44, 54-56, 61-63, 83 (EC-004) | product-owner |  |
| ADV-P3-D06 | HIGH | fail-closed harness made unsatisfiable | BC-6.03.004:111-121 | product-owner |  |
| ADV-P3-D07 | HIGH | OD-155 propagation (blast radius 4 files) | BC-2.02.006:48-50 ("the complete P1 set") | product-owner |  |
| ADV-P3-D08 | HIGH | missing contract: int/float mixing | ARCH-06:28 ("CPython 3.11 arithmetic on Num") | product-owner |  |
| ADV-P3-D09 | HIGH | systemic escape-rendering corruption | BC-5.02.001:103 | product-owner | process-gap |
| ADV-P3-D10 | HIGH | OD-155 propagation into SS-05/SS-06 consumer lists (partial-fix, 7 files) | BC-5.01.001:118 | product-owner |  |
| ADV-P3-D11 | MEDIUM | unmeasured parity boundary | BC-5.02.003:72-76 ("both current sites") | product-owner / architect |  |
| ADV-P3-D12 | MEDIUM | encoder failure paths unspecified | BC-5.02.001:80-81 (Inv 4) | product-owner |  |
| ADV-P3-D13 | MEDIUM | P18 (Windows oracle) | BC-5.04.001:59-62 | product-owner |  |
| ADV-P3-D14 | MEDIUM | uncontracted per-OS helpers / P18 | BC-5.03.004:62-63 | architect |  |
| ADV-P3-D15 | MEDIUM | mis-anchor (P4) | BC-5.01.004:113 | product-owner |  |
| ADV-P3-D16 | MEDIUM | contradiction (byte order) | BC-2.01.002:79-83 | product-owner |  |
| ADV-P3-D17 | MEDIUM | contradiction | BC-3.01.001:65-66 | product-owner |  |
| ADV-P3-D18 | MEDIUM | OD-155 gap | BC-2.02.001:43-48, 55-56 | product-owner | owner-question |
| ADV-P3-D19 | MEDIUM | exclusion closure | BC-6.03.004:87-89 | product-owner |  |
| ADV-P3-D20 | MEDIUM | spec self-inconsistency | BC-6.03.004:56-75, 158 | product-owner |  |
| ADV-P3-D21 | MEDIUM | fail-closed wording | BC-6.02.004:73-77 vs :101, :111 | product-owner |  |
| ADV-P3-D22 | MEDIUM | CI unsatisfiable as ordered | BC-6.04.001:65-74 | architect |  |
| ADV-P3-D23 | MEDIUM | uncontracted shim duty | BC-6.01.002:114-117 | product-owner |  |
| ADV-P3-D24 | MEDIUM | fidelity gap | BC-6.02.002:53, 74-75 | product-owner |  |
| ADV-P3-D25 | MEDIUM | Tier C domain gaps | BC-6.04.003:61-69 | product-owner |  |
| ADV-P3-D26 | MEDIUM | mis-anchor (P4) | BC-6.01.001:131 | product-owner |  |
| ADV-P3-D27 | MEDIUM | test-hook ambiguity | BC-5.04.003:49-54, 63-64 | product-owner |  |
| ADV-P3-D28 | LOW | stale text | BC-4.01.002:59 | product-owner |  |
| ADV-P3-D29 | LOW | anchor drift | VP-006:41-42, 57 | architect |  |
| ADV-P3-D30 | LOW | golden format | BC-5.02.002:93 vs :131 | product-owner |  |
| ADV-P3-D31 | LOW | stale provenance | BC-6.04.003:133 | product-owner |  |
| ADV-P3-D32 | LOW | error-detail rule | BC-2.02.001:77-79 | product-owner |  |
| ADV-P3-D33 | LOW | wording / edge | BC-5.01.006:58-59 | n |  |
| ADV-P3-D34 | LOW | unspecified | BC-5.02.005:52-53 | product-owner |  |
| ADV-P3-D35 | LOW | recipe wording | BC-5.01.005:62-70 | architect |  |
| ADV-P3-D36 | LOW | edge gaps | BC-2.03.002:66-69, 72-75 | product-owner |  |
| ADV-P3-D37 | LOW | reserved names | BC-2.01.001:79-82 | product-owner |  |
| ADV-P3-D38 | LOW | scope rule | BC-6.03.004:152 | product-owner |  |
| ADV-P3-D39 | LOW | not wired into CI | BC-6.04.002:56-57, 71 | architect |  |
| ADV-P3-D40 | LOW | P21 check | BC-6.02.001:80 | product-owner | owner-question |

## Totals by perimeter

| Perimeter | HIGH | MEDIUM | LOW | COSMETIC | Total |
|-----------|------|--------|-----|----------|-------|
| A | 8 | 9 | 11 | 1 | 29 |
| A2 | 6 | 15 | 6 | 0 | 27 |
| B | 4 | 6 | 7 | 1 | 18 |
| C | 5 | 9 | 7 | 1 | 22 |
| C2 | 3 | 5 | 4 | 2 | 14 |
| D | 10 | 17 | 13 | 0 | 40 |
| **Pass 3** | **36** | **61** | **48** | **5** | **150** |
