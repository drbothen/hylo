---
document_type: adversarial-review-index
phase: 1d
pass: 4
date: 2026-11-17
findings: 133
verdict: NOT_CONVERGED
novelty: MEDIUM-HIGH
---

# ADV-P4 Index — Phase 1d Adversarial Spec Review, Pass 4

Every finding from pass 4, indexed from the verbatim perimeter reports in `pass-4.md`. Severity totals: HIGH 39 / MEDIUM 57 / LOW 32 / COSMETIC 5 — total 133. Against pass 3 (150, 36 HIGH): total -17, HIGH +3.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P4-A01 | HIGH | broken anchors | architecture/ARCH-01-binary-cli.md, ARCH-02-configuration.md, ARCH-05-platform.md, ARCH-06-pyfmt.md (no `<a id>` in any of them) | architect | process-gap |
| ADV-P4-A02 | HIGH | contradiction | ARCH-03-statusline.md:79-81 | architect |  |
| ADV-P4-A03 | HIGH | range contradicts BC | prd-supplements/interface-definitions.md:114 | product-owner |  |
| ADV-P4-A04 | HIGH | interface cannot express registry (P20) | interface-definitions.md:142,154,156-159,179,180,185,206 | product-owner / architect |  |
| ADV-P4-A05 | HIGH | registry not closed (P20, AD-06) | interface-definitions.md:207, 227-231 | product-owner |  |
| ADV-P4-A06 | HIGH | interface cannot satisfy BC | ARCH-03-statusline.md:47-52, 92, 101-111 | architect |  |
| ADV-P4-A07 | HIGH | CI spec vs repo; P11 | cicd-setup.md:50 | architect | process-gap |
| ADV-P4-A08 | HIGH | false-green CI job (P11) | cicd-setup.md:24-26 | architect | process-gap |
| ADV-P4-A09 | HIGH | PRD row does not match BC H1 (P7/P9) | prd.md:527 | product-owner |  |
| ADV-P4-A10 | HIGH | duplicate ID (P1) | prd-supplements/assumptions-register.md:24-25 | product-owner |  |
| ADV-P4-A11 | MEDIUM | stale partial fix | interface-definitions.md:93 | product-owner |  |
| ADV-P4-A12 | MEDIUM | contradiction | ARCH-02-configuration.md:65-66 | architect / product-owner |  |
| ADV-P4-A13 | MEDIUM | missing gate | ARCH-08 (whole doc) | architect | process-gap |
| ADV-P4-A14 | MEDIUM | P11 / NFR-006 | cicd-setup.md:95-99 | architect | process-gap |
| ADV-P4-A15 | MEDIUM | harness can't stay in the closed set | ARCH-07-parity-harness.md:98 | architect |  |
| ADV-P4-A16 | MEDIUM | exclusion mis-anchor (P13/P4) | error-taxonomy.md:129-130 | product-owner | owner-question |
| ADV-P4-A17 | LOW | P19 hardening | cicd-setup.md:49, 119-122, 182 | architect |  |
| ADV-P4-A18 | LOW | stale propagation | BC-COMPONENT-MAP.md:159, 241-245 | architect / product-owner |  |
| ADV-P4-A19 | LOW | stale counts | risk-register.md:30 | architect / product-owner |  |
| ADV-P4-A20 | LOW | P18 completeness | ARCH-05-platform.md:23-30 | architect |  |
| ADV-P4-A21 | LOW | ambiguity | interface-definitions.md:168-171 | product-owner |  |
| ADV-P4-A22 | LOW | ambiguity | interface-definitions.md:263-271 | product-owner |  |
| ADV-P4-A23 | COSMETIC | editorial | module-criticality.md:63-79, 131 | architect / product-owner |  |
| ADV-P4-A2-01 | HIGH | contradiction (L2 vs BC) | invariants.md:31 | business-analyst |  |
| ADV-P4-A2-02 | HIGH | VP skeleton fails a correct implementation | VP-001:113-119 (and :92) | architect |  |
| ADV-P4-A2-03 | HIGH | partial-fix propagation (blast radius 4 or more) | VP-001:36-44, 87-88 | architect |  |
| ADV-P4-A2-04 | HIGH | DI-012 closure gap | invariants.md:35 | product-owner | owner-question |
| ADV-P4-A2-05 | HIGH | Go API misuse (skeleton panics) | VP-021:87-90 | architect |  |
| ADV-P4-A2-06 | HIGH | blanket exclusion vs D4/DI-012 | VP-026:47-51 | architect | owner-question |
| ADV-P4-A2-07 | MEDIUM | skeleton fails on POSIX | VP-018:94-99 | architect |  |
| ADV-P4-A2-08 | MEDIUM | ambiguous oracle | VP-002:47-49, 94-104, 113-121 | architect |  |
| ADV-P4-A2-09 | MEDIUM | vacuous or contradictory VP | VP-039:88, 91-94, 106-109 | architect |  |
| ADV-P4-A2-10 | MEDIUM | semantic mis-anchor (P4) | VP-007:12, 45-46 | architect |  |
| ADV-P4-A2-11 | MEDIUM | `bcs:` vs body vs index (P9) | VP-022:13 | architect |  |
| ADV-P4-A2-12 | MEDIUM | malformed frontmatter (P9) | VP-001:15 | architect |  |
| ADV-P4-A2-13 | MEDIUM | stale counts (P2) | invariants.md:31, 35, 46 | business-analyst |  |
| ADV-P4-A2-14 | MEDIUM | rider test-name drift | VP-003:68 | architect |  |
| ADV-P4-A2-15 | MEDIUM | stale vs OD-156 | VP-023:44-45 | architect |  |
| ADV-P4-A2-16 | MEDIUM | wrong observable in recipe | VP-006:66-67, 48 | architect |  |
| ADV-P4-A2-17 | MEDIUM | P11 inert leg | VP-022:86-90, 136-137 | architect | process-gap |
| ADV-P4-A2-18 | LOW | internal contradiction | VP-017:58 | architect |  |
| ADV-P4-A2-19 | LOW | brief drift | VP-036:44-46 | architect |  |
| ADV-P4-A2-20 | LOW | imprecise L2 | state-machines.md:81-82 | business-analyst |  |
| ADV-P4-A2-21 | LOW | stale assessments | dtu-assessment.md:155-162 | architect |  |
| ADV-P4-A2-22 | COSMETIC | skeleton consistency | VP-029:81 | architect |  |
| ADV-P4-B01 | HIGH | config-range contradiction (P20) | BC-1.02.019:62-67, :51-53 | architect + product-owner |  |
| ADV-P4-B02 | HIGH | mis-anchor (P4) | VP-028:37-39 | architect |  |
| ADV-P4-B03 | HIGH | VP over-claim; sibling of the pass-3 B03 fix | VP-028:61-75 | architect | process-gap |
| ADV-P4-B04 | HIGH | missing required vectors (sibling propagation) | error-taxonomy.md:106, :116-120 | product-owner |  |
| ADV-P4-B05 | HIGH | unnamed deviation (DI-012, P13); partial fix | BC-1.02.005 EC-009/EC-010 :91-92 and :110 | product-owner |  |
| ADV-P4-B06 | MEDIUM | internal contradiction | BC-1.02.004:136 | product-owner |  |
| ADV-P4-B07 | MEDIUM | invariant anchoring (P2/P5) | BC-1.02.001:123 | product-owner |  |
| ADV-P4-B08 | MEDIUM | config type mismatch (P20) | BC-1.02.006:85-88 | architect |  |
| ADV-P4-B09 | MEDIUM | sibling not updated (pass-3 A27) | interface-definitions.md:136 | architect |  |
| ADV-P4-B10 | LOW | stale rationale (P16) | interface-definitions.md:212 | architect |  |
| ADV-P4-B11 | MEDIUM | partial fix (pass-3 B16) | BC-1.01.002:145 | product-owner |  |
| ADV-P4-B12 | MEDIUM | settled decision not propagated (P12) | BC-1.01.001:44-47, :38 | product-owner |  |
| ADV-P4-B13 | MEDIUM | malformed frontmatter | BC-1.02.006:21-22 | product-owner |  |
| ADV-P4-B14 | MEDIUM | mis-anchor | error-taxonomy.md:122 (legacy SL:255, SL:550-553, SL:622-623) | architect |  |
| ADV-P4-B15 | MEDIUM | conflict with settled OD-02 (P12) | BC-1.02.018:67-68 | product-owner + architect |  |
| ADV-P4-B16 | LOW | decision mis-cite | BC-1.02.001:67-68 | product-owner | owner-question |
| ADV-P4-B17 | LOW | title vs postconditions (P7) | BC-1.02.003:30 (also BC-INDEX:72, PRD:171) | product-owner |  |
| ADV-P4-B18 | LOW | unspecified parity edge (P18) | BC-1.02.004:60-75 | product-owner |  |
| ADV-P4-B19 | LOW | stale circular cross-refs | error-taxonomy.md:134-135 | architect |  |
| ADV-P4-B20 | LOW | capability mapping | PRD:553-554 | product-owner |  |
| ADV-P4-B21 | LOW | misnamed key | BC-1.02.029:57-59, :65-67 | architect | owner-question |
| ADV-P4-B22 | LOW | incomplete registry description | interface-definitions.md:111 | architect |  |
| ADV-P4-C01 | HIGH | contradiction / settled decision | BC-1.07.002:89, EC-004 :80 | product-owner |  |
| ADV-P4-C02 | HIGH | mis-anchor | BC-1.07.006:109 | architect |  |
| ADV-P4-C03 | HIGH | mis-anchor (refactoring guidance) | BC-1.07.003:151 | product-owner |  |
| ADV-P4-C04 | MEDIUM | config over code; partial fix not propagated to a sibling BC | BC-1.07.004 PC7 :61-63 | product-owner |  |
| ADV-P4-C05 | MEDIUM | config over code / OD-162 | BC-1.07.007 Inv5 :80-82, PC1 :53-57 | architect + product-owner |  |
| ADV-P4-C06 | MEDIUM | spec vs legacy | BC-1.07.005 PC3 :52-53 | product-owner |  |
| ADV-P4-C07 | MEDIUM | config over code, ambiguity | BC-1.07.005:170-172 | architect |  |
| ADV-P4-C08 | MEDIUM | W-predicate gap (confidence M) | BC-1.03.018:74-75 | product-owner |  |
| ADV-P4-C09 | MEDIUM | test vector cannot be reproduced | BC-1.03.010:111 | product-owner |  |
| ADV-P4-C10 | MEDIUM | index drift | BC-INDEX.md:119 | product-owner |  |
| ADV-P4-C11 | LOW | contradiction | prd.md:496, error-taxonomy:40 | product-owner |  |
| ADV-P4-C12 | LOW | stale anchor labels (targets are correct) | BC-1.07.001:107, :122 | product-owner |  |
| ADV-P4-C13 | LOW | missing error path | BC-1.07.008 EC-005 :84 | product-owner | owner-question |
| ADV-P4-C14 | LOW | unstated assumption | BC-1.07.003 PC1 :47, EC-006 :71 | product-owner |  |
| ADV-P4-C15 | COSMETIC | precision | BC-1.07.006 Pre2 :47, EC-004 :78 | product-owner |  |
| ADV-P4-C2-01 | HIGH | Wrong test vector (Python result) | BC-1.04.001:145, :158 | product-owner |  |
| ADV-P4-C2-02 | HIGH | Wrong test vector (contradicts PC4/EC-011) | BC-1.04.001:159 | product-owner |  |
| ADV-P4-C2-03 | HIGH | Exclusion id outside the closed set; contradiction | BC-1.05.004:65 | product-owner / architect | owner-question |
| ADV-P4-C2-04 | HIGH | Partial fix not propagated (blast radius 6+) | VP-021:33, :37, :44, :72, :80 (`SeededSessions20`), :105, :112 | architect / product-owner |  |
| ADV-P4-C2-05 | MEDIUM | OD-166 deviation not carried through | BC-1.05.009:45-47, :25 (parity_class OD-30) | product-owner |  |
| ADV-P4-C2-06 | MEDIUM | Guard scope ambiguous; possible output divergence | BC-1.05.004:60-68, :102 | product-owner |  |
| ADV-P4-C2-07 | MEDIUM | Redirect prose wrong; rule key ambiguous | BC-1.04.001:64-67, :70-72 | product-owner |  |
| ADV-P4-C2-08 | MEDIUM | Missed urllib quirk | BC-1.04.001:54-57 | product-owner |  |
| ADV-P4-C2-09 | MEDIUM | Transport behaviour not pinned | BC-1.04.001:51-57, :75-76 | architect |  |
| ADV-P4-C2-10 | MEDIUM | Taxonomy contradicts BC and ARCH | error-taxonomy.md:121-125 | architect |  |
| ADV-P4-C2-11 | MEDIUM | ARCH table contradicts its own crash register | ARCH-03:66 | architect |  |
| ADV-P4-C2-12 | MEDIUM | Crash path missing from the register | BC-1.04.004:62-65 | architect |  |
| ADV-P4-C2-13 | MEDIUM | Config over code (P20) | BC-1.04.003:62-63 | architect |  |
| ADV-P4-C2-14 | LOW | Claim false under allowed config | BC-1.04.003:64-65 | product-owner |  |
| ADV-P4-C2-15 | LOW | Crash outcome missing from edge case | BC-1.04.003:84 | product-owner |  |
| ADV-P4-C2-16 | LOW | Ambiguous wording | BC-1.04.013:50 | product-owner |  |
| ADV-P4-C2-17 | LOW | Postcondition omits configured branch | BC-1.04.006:43-50 | product-owner |  |
| ADV-P4-D01 | HIGH | contradiction / test vector | BC-2.01.001:117 | product-owner |  |
| ADV-P4-D02 | HIGH | contradiction | BC-1.07.002:89 | product-owner |  |
| ADV-P4-D03 | HIGH | contradiction (OD-155/168) | BC-4.01.001:68 (Inv 1), :98 (VP-004), :51-55 (PC-1) | product-owner |  |
| ADV-P4-D04 | MEDIUM | contradiction | BC-2.02.001:132-133 (PC-8) | product-owner |  |
| ADV-P4-D05 | MEDIUM | partial-fix regression | BC-4.01.002:111 | product-owner |  |
| ADV-P4-D06 | HIGH | untestable / P18 | BC-3.02.001:60-62 | architect |  |
| ADV-P4-D07 | HIGH | interface / ARCH-06 signatures | ARCH-06:112-113 | architect |  |
| ADV-P4-D08 | HIGH | partial-fix regression / CI | BC-6.04.001:65-74 (PC-3) | architect | process-gap |
| ADV-P4-D09 | HIGH | contradiction / harness argv | BC-6.02.003:75-82 | architect |  |
| ADV-P4-D10 | HIGH | anchor / path contradiction | BC-6.02.001:61, BC-6.02.003:182, BC-6.04.003:94 | architect |  |
| ADV-P4-D11 | HIGH | P13 / harness translation | BC-6.02.003:89-97 (PC-2) | architect |  |
| ADV-P4-D12 | MEDIUM | harness gap (OD-107) | BC-6.03.004 PC-1 (:100-101), BC-6.02.001 PC-1/3 | architect |  |
| ADV-P4-D13 | MEDIUM | undefined comparison | BC-6.03.004:112-126 (PC-3) | architect |  |
| ADV-P4-D14 | HIGH | Python parity (Unicode DB) | BC-5.01.002 PC-2 (:51), BC-5.02.005 PC-4 (:60-63), BC-2.02.003 PC-2 (:57-58) | architect |  |
| ADV-P4-D15 | HIGH | Python parity | BC-5.01.007:48-50 (Pre 2), :72-74 (PC-2) | product-owner |  |
| ADV-P4-D16 | MEDIUM | untestable | BC-5.01.007:75-83 (PC-3/4), :94-95 (Inv 3), :111 | product-owner |  |
| ADV-P4-D17 | MEDIUM | missing boundary | BC-5.02.006 (whole), BC-5.02.001:86-87 | architect |  |
| ADV-P4-D18 | MEDIUM | anchoring / scope / P18 | BC-5.03.004:62-63 (Inv 3), :34-36 | architect |  |
| ADV-P4-D19 | MEDIUM | P20 / untestable grammar | interface-definitions.md:140, :154, :156, :179-180, :185, :206 | product-owner |  |
| ADV-P4-D20 | MEDIUM | contradiction | BC-2.03.002:76-79 | product-owner |  |
| ADV-P4-D21 | MEDIUM | P18 / Windows TZ | BC-5.04.001:45, BC-6.01.002 PC-2, BC-6.02.003 PC-8 | architect |  |
| ADV-P4-D22 | MEDIUM | anchor drift | BC-2.02.001:184, BC-6.03.004:83, ARCH-07:104, BC-2.02.003:121 | architect |  |
| ADV-P4-D23 | MEDIUM | contradiction | BC-6.04.002 PC-1/2 | architect |  |
| ADV-P4-D24 | MEDIUM | contradiction | BC-6.01.003:60-63 | architect |  |
| ADV-P4-D25 | MEDIUM | infeasible spec | BC-6.02.002:54, :67-74 | architect |  |
| ADV-P4-D26 | MEDIUM | P5/P12 anchor | BC-2.01.005:56, BC-2.02.006:51-52 | product-owner | owner-question |
| ADV-P4-D27 | LOW | anchor completeness | BC-2.01.001:65-67, BC-2.01.002:133, :140-146 | product-owner |  |
| ADV-P4-D28 | LOW | partial-fix | BC-6.01.003:46, :147 | product-owner |  |
| ADV-P4-D29 | COSMETIC | test-data accuracy | BC-3.02.002:68, :102-106 | product-owner |  |
| ADV-P4-D30 | COSMETIC | purity | BC-3.01.001:139-143 | product-owner |  |
| ADV-P4-D31 | LOW | ambiguous vector | BC-5.01.002:79, :87 | product-owner |  |
| ADV-P4-D32 | LOW | unspecified | BC-3.02.001:84-85 | architect |  |
| ADV-P4-D33 | LOW | nondeterminism | BC-2.03.001:52 | product-owner |  |
| ADV-P4-D34 | LOW | P4 mis-home | BC-5.04.003:53-60, :73-76 | product-owner |  |
