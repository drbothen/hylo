---
document_type: adversarial-review-index
phase: 1d
pass: 7
date: 2026-11-18
findings: 114
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P7 Index — Phase 1d Adversarial Spec Review, Pass 7

Every finding from pass 7, indexed from `pass-7.md`. Severity totals: HIGH 14 / MEDIUM 47 / LOW 49 / COSMETIC 4 — total 114. Against pass 6 (124, 27 HIGH): total -10, HIGH -13.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P7-A01 | HIGH | contradiction | specs/architecture/ARCH-07-parity-harness.md:68-89 | architect |  |
| ADV-P7-A02 | HIGH | partial-fix propagation | specs/prd-supplements/nfr-catalog.md:24-26 | product-owner + architect |  |
| ADV-P7-A03 | HIGH | interface cannot express BC | specs/architecture/ARCH-05-platform.md:26,32,33 | architect |  |
| ADV-P7-A04 | MEDIUM | ambiguity / default undefined | specs/prd-supplements/interface-definitions.md:198-199, :292 | product-owner |  |
| ADV-P7-A05 | MEDIUM | contradiction (cross-ref) | specs/prd-supplements/interface-definitions.md:289-293 | product-owner |  |
| ADV-P7-A06 | MEDIUM | partial-fix propagation | specs/prd-supplements/interface-definitions.md:167, :274-275 | product-owner |  |
| ADV-P7-A07 | MEDIUM | CI cannot work as designed | specs/cicd-setup.md:262, :267 | architect / devops |  |
| ADV-P7-A08 | MEDIUM | contradiction / CI timeout | ARCH-08:55-58 | architect |  |
| ADV-P7-A09 | MEDIUM | mitigation rests on nonexistent gate | ARCH-08-build-ci-release.md:139-144 | architect |  |
| ADV-P7-A10 | MEDIUM | cross-platform (P18) | ARCH-05-platform.md:31, :34 | architect |  |
| ADV-P7-A11 | MEDIUM | interface gap (https) | ARCH-03-statusline.md:184-209 | architect |  |
| ADV-P7-A12 | MEDIUM | mis-anchor (P4) | ARCH-04-data-files.md:109-111 | architect |  |
| ADV-P7-A13 | MEDIUM | missing exact string (sibling gap) | interface-definitions.md:214 | product-owner |  |
| ADV-P7-A14 | LOW | stale owner labels | error-taxonomy.md:46 | product-owner |  |
| ADV-P7-A15 | LOW | drift | prd.md:626-627 | product-owner |  |
| ADV-P7-A16 | LOW | user-facing message misdescribes rule | error-taxonomy.md:93 | product-owner | owner-question |
| ADV-P7-A17 | LOW | stale precedent | ARCH-09-reserved-boundaries.md:25, :41 | architect |  |
| ADV-P7-A18 | LOW | CI census ambiguity | ARCH-08:104-107 | architect |  |
| ADV-P7-A19 | LOW | config over code | ARCH-04-data-files.md:62-77 | architect | owner-question |
| ADV-P7-A20 | LOW | positive-coverage weak | ARCH-08:131-134 | architect |  |
| ADV-P7-A21 | LOW | threshold without rationale (P16) | interface-definitions.md:247 | product-owner |  |
| ADV-P7-A22 | LOW | assumption timing | assumptions-register.md:29 | product-owner | owner-question |
| ADV-P7-A2-01 | MEDIUM | semantic anchoring (P4) / L2↔PRD contradiction | domain-spec/capabilities.md:29 | business-analyst |  |
| ADV-P7-A2-02 | MEDIUM | VP bcs reciprocity (P4/P9) | verification-properties/VP-012-exclusion-set-closure.md:13, 65-68, 197-200 | architect |  |
| ADV-P7-A2-03 | MEDIUM | VP↔primary-BC contradiction / partial-fix propagation | VP-012:88-96, 174-196 | architect / product-owner |  |
| ADV-P7-A2-04 | MEDIUM | oracle gap (DI-012) / P11 | VP-012:56-61, 138-152, 155-166 | architect |  |
| ADV-P7-A2-05 | MEDIUM | sibling not updated (partial-fix) | VP-014-d4ex1-windows-window-age.md:53, 69, 79 | architect |  |
| ADV-P7-A2-06 | MEDIUM | config over code (P20) / propagation | VP-031-bounded-resource-caps.md:39-43, 77-80 | architect |  |
| ADV-P7-A2-07 | MEDIUM | internal contradiction / P20 | VP-018-atomic-cache-writes.md:55-61, 99-101 | architect |  |
| ADV-P7-A2-08 | MEDIUM | vacuous oracle | VP-018:84-85 (Method), 137 | architect |  |
| ADV-P7-A2-09 | MEDIUM | missing verification leg | VP-016-config-error-classes-line.md:37-53, 98-108 | architect |  |
| ADV-P7-A2-10 | MEDIUM | ambiguity | VP-007-render-determinism-seams.md:37-41, 80-84 | architect |  |
| ADV-P7-A2-11 | MEDIUM | sibling of pass-6 fix not propagated | VP-041-row1-property-legs.md:126 | architect |  |
| ADV-P7-A2-12 | MEDIUM | sketch contradicts property | VP-009-tier-a-live-parity.md:94-96 | architect |  |
| ADV-P7-A2-13 | LOW | possible false fail | VP-001-never-blank-exit0.md:158-163 | architect |  |
| ADV-P7-A2-14 | LOW | oracle incomplete | VP-021-cost-colour-goldens.md:97-108 | architect |  |
| ADV-P7-A2-15 | LOW | self-contradiction | VP-017-exactly-one-backend.md:41-47 | architect |  |
| ADV-P7-A2-16 | LOW | wording mismatch | VP-015-config-resolution-totality.md:38 | architect |  |
| ADV-P7-A2-17 | LOW | stale reference / wrong noun | VP-022-ledger-read-scope-absence.md:49, 90 | architect |  |
| ADV-P7-A2-18 | LOW | unfailable leg | VP-036-render-latency-p95.md:43-48 | owner | owner-question |
| ADV-P7-A2-19 | LOW | unnamed carve-out (DI-012) | VP-009:37-42 | product-owner | owner-question |
| ADV-P7-A2-20 | LOW | toolchain claim (P19) | VP-037-three-os-ci-matrix.md:38 | architect |  |
| ADV-P7-A2-21 | LOW | frontmatter↔body drift | VP-006-json-depth-budgets.md:13 | architect |  |
| ADV-P7-A2-22 | COSMETIC | stale wording | dtu-assessment.md:32-33, 48 | architect |  |
| ADV-P7-B01 | HIGH | P7 title does not match postconditions | BC-1.01.003:33, BC-INDEX:69, prd.md:157 | product-owner |  |
| ADV-P7-B02 | MEDIUM | Wrong bearer stated | BC-1.01.009:92-93 | product-owner |  |
| ADV-P7-B03 | MEDIUM | A step-2 degrade is missing from the step table | BC-1.01.009:62 (step-2 "Can degrade?" cell) | product-owner; architect (taxonomy id) |  |
| ADV-P7-B04 | MEDIUM | Mis-anchor | BC-1.01.001:58-59 | product-owner |  |
| ADV-P7-B05 | MEDIUM | Mis-anchor (cross-check) | BC-2.01.004:185 | product-owner |  |
| ADV-P7-B06 | MEDIUM | OD-179 fix not carried to a sibling | BC-1.02.030:52-53, 88, 91, 138 | product-owner |  |
| ADV-P7-B07 | MEDIUM | Unstated environment input | BC-1.02.004:49-52, 77-78, 212 | product-owner |  |
| ADV-P7-B08 | LOW | Mis-pointed footnote | BC-1.01.009:62 | product-owner |  |
| ADV-P7-B09 | LOW | Internal inconsistency | BC-1.01.001:94 | product-owner |  |
| ADV-P7-B10 | LOW | Registry back-references incomplete | interface-definitions:199, 233, 238 | architect |  |
| ADV-P7-B11 | LOW | Taxonomy carrier list incomplete | error-taxonomy:46 | architect |  |
| ADV-P7-B12 | LOW | Pass-6 B16 history-label sweep incomplete (pending intent verification) | BC-1.02.019:22-23, .020:22-23, .022:22-23, .024:22, .026:22, .030:22-23 | product-owner |  |
| ADV-P7-B13 | LOW | Pass-6 B01 re-anchoring incomplete (pending intent verification) | BC-1.02.008:96, BC-1.02.014:133 | product-owner |  |
| ADV-P7-B14 | LOW | Overstated edge case | BC-1.01.009:113 | product-owner |  |
| ADV-P7-B15 | COSMETIC | Test-name spelling | BC-1.02.017:70 | product-owner |  |
| ADV-P7-C01 | HIGH | Parity break that has no ruling (P13) | BC-1.06.001:119 (EC-011) | product-owner | owner-question |
| ADV-P7-C02 | MEDIUM | Spec text gives the wrong output bytes | BC-1.07.004:57-59 (PC3) | product-owner |  |
| ADV-P7-C03 | MEDIUM | Test vector cannot be reproduced as written | BC-1.03.010:125 (NaN-id row) | product-owner |  |
| ADV-P7-C04 | MEDIUM | Quirk not pinned in a spec or test | BC-1.07.007:54-61, EC table 94-104 | product-owner |  |
| ADV-P7-C05 | MEDIUM | VP link one-sided; earlier fix not copied to sibling | BC-1.06.001:130-136 (VP table), 166-169 (VP anchors) | product-owner |  |
| ADV-P7-C06 | LOW | Stale cross-reference | BC-1.07.001:80 (EC-003), :119 (Related BCs) | product-owner |  |
| ADV-P7-C07 | LOW | Vector contradicts itself | BC-1.03.007:106 | product-owner |  |
| ADV-P7-C08 | LOW | Vector depends on a template it does not define | BC-1.03.006:114 | product-owner |  |
| ADV-P7-C09 | LOW | Cross-platform claim untrue on Windows (P18) | BC-1.06.001:80, :125 | product-owner |  |
| ADV-P7-C10 | LOW | Config registry contract column incomplete | interface-definitions.md:170, 178, 182-183, 188-189 | architect |  |
| ADV-P7-C11 | LOW | Literal display text instead of a config key (P20) | BC-1.07.005:54-55, EC-004 (also BC-1.02.002:35) | product-owner | owner-question |
| ADV-P7-C12 | LOW | VP row claims too much | BC-1.07.008:112 | product-owner |  |
| ADV-P7-C13 | COSMETIC | Wrong cross-reference | prd.md:640 | product-owner |  |
| ADV-P7-C14 | COSMETIC | Garbled text | BC-1.07.007:54-55 | product-owner |  |
| ADV-P7-C2-01 | HIGH | spec gap (silent production failure) | BC-1.04.001:55-65, :253 | product-owner + architect |  |
| ADV-P7-C2-02 | HIGH | wrong normative rule | BC-1.04.001:66-73 | product-owner + architect |  |
| ADV-P7-C2-03 | HIGH | partial-fix gap, 2+ files (VP-012 reciprocity) | BC-1.04.001 VP table :249-256 and DI row :265 | product-owner + architect |  |
| ADV-P7-C2-04 | MEDIUM | contradiction / ambiguity | BC-1.04.001:55 | product-owner |  |
| ADV-P7-C2-05 | MEDIUM | VP cannot verify the BC | VP-030:72-75, :85, :131 | architect |  |
| ADV-P7-C2-06 | MEDIUM | wrong site / false totality | BC-1.04.002:75-78 | product-owner |  |
| ADV-P7-C2-07 | MEDIUM | P20 config over code | BC-1.04.004:45-46, :50 | product-owner | owner-question |
| ADV-P7-C2-08 | LOW | wire detail missing | BC-1.04.001:104-110, :140-141 | product-owner |  |
| ADV-P7-C2-09 | LOW | stale anchor | BC-1.04.001:267 | product-owner |  |
| ADV-P7-C2-10 | LOW | imprecise threshold | BC-1.05.005:109 | product-owner |  |
| ADV-P7-C2-11 | LOW | VP precondition missing | BC-1.04.021:78 | product-owner |  |
| ADV-P7-C2-12 | LOW | sibling wording not propagated | ARCH-03:102-104 | architect |  |
| ADV-P7-C2-13 | LOW | taxonomy understates the ladder | error-taxonomy:51 | product-owner |  |
| ADV-P7-C2-14 | LOW | vector register mismatch | test-vectors:43 | product-owner |  |
| ADV-P7-D01 | HIGH | contradiction / testability | BC-2.01.005:147-152 | product-owner (+architect for interface table) |  |
| ADV-P7-D02 | HIGH | vocabulary gap | BC-2.02.001:98-123, 138-141 | product-owner |  |
| ADV-P7-D03 | HIGH | untestable error surface | BC-2.02.002:51-54 | product-owner |  |
| ADV-P7-D04 | HIGH | contradiction (fail-closed harness constants) | BC-6.01.001:81-87 | product-owner + architect |  |
| ADV-P7-D05 | HIGH | three-way contradiction (exact-set assert) | BC-6.01.002:67-95, 169 | architect + product-owner |  |
| ADV-P7-D06 | HIGH | contradiction / Windows parity (blast radius 4) | BC-5.04.001:46-48 | product-owner + architect |  |
| ADV-P7-D07 | MEDIUM | stale signature | BC-5.04.001:54-55 | product-owner |  |
| ADV-P7-D08 | MEDIUM | contradiction | BC-2.01.001:62-67 | product-owner |  |
| ADV-P7-D09 | MEDIUM | undeclared type | BC-2.01.005:97-99, 115 | product-owner + architect |  |
| ADV-P7-D10 | MEDIUM | ordering gap | BC-2.01.002:69-84 | product-owner |  |
| ADV-P7-D11 | MEDIUM | P7 title vs postconditions | BC-2.02.002:38 | product-owner |  |
| ADV-P7-D12 | MEDIUM | P18 / injection | BC-3.01.001:48 | product-owner |  |
| ADV-P7-D13 | MEDIUM | mis-anchor | BC-2.01.004:228-235 | product-owner + architect |  |
| ADV-P7-D14 | MEDIUM | mis-anchor | BC-6.01.001:92-93 | architect + product-owner |  |
| ADV-P7-D15 | MEDIUM | incomplete enumeration | BC-6.03.004:139-150 | product-owner |  |
| ADV-P7-D16 | MEDIUM | domain gap | BC-6.04.003:71-91, 123-124 | product-owner |  |
| ADV-P7-D17 | MEDIUM | stale / anchor | BC-6.02.003:95-96, 161-162, 212 | product-owner |  |
| ADV-P7-D18 | LOW | anchor | BC-2.01.004:132 | product-owner |  |
| ADV-P7-D19 | LOW | wording | BC-5.01.007:105-107 | product-owner |  |
| ADV-P7-D20 | LOW | ambiguity | BC-5.04.002:58 | product-owner |  |
| ADV-P7-D21 | LOW | internal contradiction | BC-2.01.004:200-202 | product-owner |  |
| ADV-P7-D22 | LOW | interface gap | ARCH-06:128-189 | architect |  |
| ADV-P7-D23 | LOW | contradiction | BC-2.02.005:72, 105 | product-owner |  |
| ADV-P7-D24 | LOW | contradiction | BC-6.03.002:67-69 | product-owner |  |
| ADV-P7-D25 | LOW | grammar gap | BC-2.01.002:53-55, 97-98 | product-owner |  |
| ADV-P7-D26 | LOW | P16 | BC-6.04.002:65-69 | product-owner |  |
| ADV-P7-D27 | LOW | CLI gap | BC-2.03.002:55, 63 | product-owner |  |
