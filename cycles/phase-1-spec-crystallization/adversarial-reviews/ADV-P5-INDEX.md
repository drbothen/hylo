---
document_type: adversarial-review-index
phase: 1d
pass: 5
date: 2026-11-18
findings: 148
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P5 Index — Phase 1d Adversarial Spec Review, Pass 5

Every finding from pass 5, indexed from `pass-5.md`. Severity totals: HIGH 24 / MEDIUM 75 / LOW 43 / COSMETIC 6 — total 148. Against pass 4 (133, 39 HIGH): total +15, HIGH -15.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P5-A01 | HIGH | contradiction / closed exit surface | architecture/ARCH-01-binary-cli.md:51, :85-88 | architect + product-owner |  |
| ADV-P5-A02 | HIGH | contradiction (oracle env), P18 | VP-034-oracle-isolation.md:47-48, :106 | architect |  |
| ADV-P5-A03 | HIGH | interface cannot express BC | interface-definitions.md:116-120, :183, :239 | product-owner |  |
| ADV-P5-A04 | HIGH | CI design / ordering, P11 | ARCH-08-build-ci-release.md:42-43, :60-62 | architect |  |
| ADV-P5-A05 | HIGH | P9 VP arithmetic | prd-supplements/module-criticality.md:55, :69-79 | product-owner |  |
| ADV-P5-A06 | MEDIUM | closed vocabulary incomplete | error-taxonomy.md:70-93 | product-owner |  |
| ADV-P5-A07 | MEDIUM | contradiction | ARCH-07-parity-harness.md:107 | architect |  |
| ADV-P5-A08 | MEDIUM | ambiguity (OD-168 routing) | ARCH-01-binary-cli.md:46, :67 | architect |  |
| ADV-P5-A09 | MEDIUM | partial-fix propagation | ARCH-03-statusline.md:69-70, :89-91 | architect |  |
| ADV-P5-A10 | MEDIUM | interface cannot express BC | ARCH-03-statusline.md:143-145 | architect |  |
| ADV-P5-A11 | MEDIUM | unstated wiring | ARCH-03-statusline.md:103-108, :132-133, :155-157 | architect |  |
| ADV-P5-A12 | MEDIUM | mis-anchor (P4) | BC-COMPONENT-MAP.md:185 | architect |  |
| ADV-P5-A13 | MEDIUM | NFR vs config ranges | prd.md:483 | product-owner | owner-question |
| ADV-P5-A14 | MEDIUM | ranges vs BC | interface-definitions.md:140, :206, :214-215, :222-228, :236-237 | product-owner |  |
| ADV-P5-A15 | MEDIUM | ambiguity | interface-definitions.md:118, :210-211 | product-owner |  |
| ADV-P5-A16 | MEDIUM | P11 | ARCH-08-build-ci-release.md:60-71, :81-110 | architect | process-gap |
| ADV-P5-A17 | MEDIUM | sibling not updated | cicd-setup.md:162 | architect |  |
| ADV-P5-A18 | MEDIUM | P20 | BC-2.01.004.md:102-104 | product-owner | owner-question |
| ADV-P5-A19 | LOW | partial-fix | ARCH-08-build-ci-release.md:88 | architect |  |
| ADV-P5-A20 | LOW | duplicate registry row | interface-definitions.md:219-220 | product-owner |  |
| ADV-P5-A21 | LOW | self-contradiction | error-taxonomy.md:168 (and :151-152) | product-owner |  |
| ADV-P5-A22 | LOW | missing carve-out | prd.md:77-78, :581-582 | product-owner |  |
| ADV-P5-A23 | LOW | ambiguity | ARCH-06-pyfmt.md:34 | architect |  |
| ADV-P5-A24 | LOW | anchor | ARCH-03-statusline.md:96 | architect |  |
| ADV-P5-A25 | LOW | P13 wording | interface-definitions.md:297-298 | product-owner | owner-question |
| ADV-P5-A2-01 | HIGH | Invalid Go / API drift | VP-015:37-38,97 | architect |  |
| ADV-P5-A2-02 | HIGH | Invalid Go / partial-fix regression | VP-024:87,97,100 | architect |  |
| ADV-P5-A2-03 | HIGH | Mis-anchor / coverage hole | VP-016:37-38,48,88-89 | architect |  |
| ADV-P5-A2-04 | HIGH | Mis-anchor (multiple BCs) | VP-041:42-59 | architect |  |
| ADV-P5-A2-05 | MEDIUM | Missing decode site | VP-006:45-55 | architect |  |
| ADV-P5-A2-06 | MEDIUM | Skeleton fails a correct impl / cross-platform | VP-026:95,100 | architect | owner-question |
| ADV-P5-A2-07 | MEDIUM | Weak oracle | VP-034:86-119 | architect |  |
| ADV-P5-A2-08 | MEDIUM | Vacuous / no-oracle property legs | VP-021:91-96 | architect | process-gap |
| ADV-P5-A2-09 | MEDIUM | Contradiction VP-011↔VP-012 | VP-011:39-40,87 | architect |  |
| ADV-P5-A2-10 | MEDIUM | Vacuous fuzz regime | VP-001:142-144,120 | architect |  |
| ADV-P5-A2-11 | MEDIUM | VP bcs↔body drift | VP-001:13 | architect |  |
| ADV-P5-A2-12 | MEDIUM | Weak oracle | VP-003:68-71 | architect |  |
| ADV-P5-A2-13 | MEDIUM | Tautological rule | VP-036:44-47 | architect |  |
| ADV-P5-A2-14 | MEDIUM | Stale count | VP-009:54-55 | architect |  |
| ADV-P5-A2-15 | MEDIUM | Stale count (P2) | invariants.md:35,46 | business-analyst |  |
| ADV-P5-A2-16 | MEDIUM | Skeleton fails a correct impl | VP-009:77 | architect |  |
| ADV-P5-A2-17 | MEDIUM | Partial fix (A2-14) | VP-012:139-153 | architect |  |
| ADV-P5-A2-18 | MEDIUM | Go misuse (P19/P18) | VP-039:107-111 | architect |  |
| ADV-P5-A2-19 | MEDIUM | P9 self-inconsistency | VP-INDEX:111,228,315 | architect |  |
| ADV-P5-A2-20 | MEDIUM | Cross-ref contradiction | BC-1.03.004:111 | product-owner |  |
| ADV-P5-A2-21 | MEDIUM | Stale assessment | architecture-feasibility-report.md:33-36 | architect |  |
| ADV-P5-A2-22 | MEDIUM | Stale assessment | gene-transfusion-assessment.md:52 | architect |  |
| ADV-P5-A2-23 | MEDIUM | Inventory gap | dtu-assessment.md:27-30,41-49 | architect |  |
| ADV-P5-A2-24 | MEDIUM | Contradiction | VP-015:44-45,101-103 | architect |  |
| ADV-P5-A2-25 | MEDIUM | Missing oracle | VP-016:93-101 | architect |  |
| ADV-P5-A2-26 | MEDIUM | Untestable leg | VP-020:52-57,107,111 | architect |  |
| ADV-P5-A2-27 | LOW | Ambiguity | capabilities.md:29 | business-analyst |  |
| ADV-P5-A2-28 | LOW | Factual error | owner-validation-list.md:217 | business-analyst |  |
| ADV-P5-A2-29 | LOW | Factual error | VP-023:105 | architect |  |
| ADV-P5-A2-30 | LOW | Oracle under-specified | VP-002:37-40 | architect |  |
| ADV-P5-A2-31 | LOW | Ambiguous skeleton | VP-007:80-83 | architect |  |
| ADV-P5-A2-32 | LOW | Threshold rationale (P16) | VP-018:49,90-92 | architect |  |
| ADV-P5-A2-33 | LOW | Spec drift | VP-028:42 | architect |  |
| ADV-P5-A2-34 | LOW | Vacuous generator | VP-040:102-111 | architect |  |
| ADV-P5-A2-35 | LOW | Carve-out not propagated | entities.md:39 | business-analyst |  |
| ADV-P5-A2-36 | COSMETIC | Label | VP-012:15 | architect / business-analyst |  |
| ADV-P5-B01 | HIGH | contradiction / partial-fix propagation | BC-1.01.009:63-67 | product-owner (VP-008: architect) |  |
| ADV-P5-B02 | MEDIUM | incompleteness | BC-1.01.001:53-54, :84 | product-owner |  |
| ADV-P5-B03 | HIGH | P20 config-over-code / P4 mis-anchor | BC-1.02.001:67 | product-owner |  |
| ADV-P5-B04 | MEDIUM | semantic mis-anchoring | BC-2.01.004:117, :119 (consumer BC-1.02.018) | product-owner |  |
| ADV-P5-B05 | MEDIUM | legacy mismatch (P13) | BC-1.02.011:86 | product-owner |  |
| ADV-P5-B06 | MEDIUM | legacy mismatch | BC-1.02.004:62, :109 | product-owner |  |
| ADV-P5-B07 | MEDIUM | sibling drift (P2) | BC-1.02.027:86, :103, :109 | product-owner |  |
| ADV-P5-B08 | MEDIUM | P4 VP anchoring | VP-041:37-59 | architect |  |
| ADV-P5-B09 | MEDIUM | P20 | BC-1.02.009:47, :111, :163 | product-owner | owner-question |
| ADV-P5-B10 | LOW | spec gap | BC-1.02.030:63-65 | product-owner |  |
| ADV-P5-B11 | LOW | registry inconsistency | interface-definitions.md:140 | architect |  |
| ADV-P5-B12 | LOW | stale citation | BC-1.02.014:77 | product-owner |  |
| ADV-P5-B13 | LOW | registry duplicate | interface-definitions.md:219-220 | architect |  |
| ADV-P5-B14 | LOW | provenance | BC-1.01.001:7 | product-owner | process-gap |
| ADV-P5-B15 | LOW | ambiguity | BC-1.02.006:86 | product-owner |  |
| ADV-P5-B16 | COSMETIC | typo | BC-1.02.004:63 | product-owner |  |
| ADV-P5-C01 | HIGH | contradiction / settled decision (P12) | BC-1.03.018:49-50, 64-66, rows 78-79 | product-owner | owner-question |
| ADV-P5-C02 | HIGH | self-contradiction / untestable property | BC-1.03.018:82-83 (PC4), VP row 126 | product-owner |  |
| ADV-P5-C03 | HIGH | config over code (P20) / mis-anchor (P4) / P12 (OD-173) | BC-1.07.006:110, 166-169 | architect (registry) + product-owner |  |
| ADV-P5-C04 | MEDIUM | spec drift vs legacy | BC-1.03.018 rows 78-79 | product-owner |  |
| ADV-P5-C05 | MEDIUM | under-specified predicate | BC-1.03.010:98 (EC-009) | product-owner |  |
| ADV-P5-C06 | MEDIUM | internal contradiction / P12 (OD-170) | BC-1.07.006:163-165 | product-owner |  |
| ADV-P5-C07 | MEDIUM | parity hazard in implementer guidance | BC-1.07.007:193-194 | product-owner |  |
| ADV-P5-C08 | MEDIUM | partial fix not propagated | error-taxonomy.md:158-159 | architect |  |
| ADV-P5-C09 | MEDIUM | vector cannot be satisfied as a test | BC-1.03.014:78, 87-88 | product-owner |  |
| ADV-P5-C10 | MEDIUM | invariants not lifted to sibling BCs (P2) | BC-1.03.007:119 | product-owner |  |
| ADV-P5-C11 | MEDIUM | mis-anchor (stale line numbers) | BC-1.07.001:107, 122 | product-owner | process-gap |
| ADV-P5-C12 | LOW | vector does not discriminate | BC-1.03.013:67, 85 | product-owner |  |
| ADV-P5-C13 | LOW | mislabel | BC-1.07.004:91 | product-owner |  |
| ADV-P5-C14 | LOW | partial fix not propagated | BC-1.07.008:176 | product-owner |  |
| ADV-P5-C15 | LOW | VP anchor reciprocity (P4) | BC-1.06.002:111-112 | product-owner |  |
| ADV-P5-C16 | LOW | parity vocabulary | BC-1.07.002:17 | product-owner |  |
| ADV-P5-C17 | COSMETIC | hygiene | BC-1.03.004:22 | product-owner |  |
| ADV-P5-C2-01 | MEDIUM | spec cannot be implemented as written | BC-1.04.001:64-69, 90-95 | product-owner / architect |  |
| ADV-P5-C2-02 | MEDIUM | loose quirk spec | BC-1.04.001:73-76 | product-owner |  |
| ADV-P5-C2-03 | MEDIUM | unnamed parity divergence | BC-1.04.001:96-97 (PC2) | product-owner | owner-question |
| ADV-P5-C2-04 | MEDIUM | unverifiable VP | BC-1.04.001:187 | product-owner / architect |  |
| ADV-P5-C2-05 | MEDIUM | internal contradiction | BC-1.05.006:122 | product-owner |  |
| ADV-P5-C2-06 | MEDIUM | cross-doc name drift | BC-1.05.004:137 | product-owner / architect |  |
| ADV-P5-C2-07 | MEDIUM | propagation gap (partial fix) | BC-INDEX.md:166,171 | product-owner |  |
| ADV-P5-C2-08 | MEDIUM | config range admits undefined behavior (P20) | interface-definitions.md:216-217 | architect |  |
| ADV-P5-C2-09 | MEDIUM | imprecise edge case | BC-1.04.003:95 | product-owner |  |
| ADV-P5-C2-10 | LOW | incomplete crash register | BC-1.05.005:105 | architect |  |
| ADV-P5-C2-11 | LOW | threshold type | interface-definitions.md:238 | architect | owner-question |
| ADV-P5-C2-12 | LOW | coverage gap | BC-1.04.016:42-44 | product-owner |  |
| ADV-P5-C2-13 | LOW | missing condition | BC-1.04.001:161 (EC-013) | product-owner |  |
| ADV-P5-C2-14 | LOW | anchoring rule vs practice (P4) | ARCH-03:179-181 | architect | process-gap |
| ADV-P5-C2-15 | LOW | registry duplicate | interface-definitions.md:219-220 | architect |  |
| ADV-P5-C2-16 | LOW | wrong disposition note | interface-definitions.md:221 | architect |  |
| ADV-P5-C2-17 | LOW | sibling citation gap (pending intent verification) | BC-1.04.003:121 | product-owner |  |
| ADV-P5-C2-18 | LOW | test-vector index incomplete | test-vectors.md:43 | architect |  |
| ADV-P5-C2-19 | LOW | H1 incomplete (P7) | BC-1.05.007:35 | product-owner |  |
| ADV-P5-C2-20 | COSMETIC | stale text | BC-1.04.007:43-45 | product-owner |  |
| ADV-P5-C2-21 | COSMETIC | wording | error-taxonomy.md:240 | architect |  |
| ADV-P5-D01 | HIGH | Parity (P13/P18): unregistered Windows deviation | BC-5.04.001:65-68 | product-owner |  |
| ADV-P5-D02 | HIGH | Harness determinism (frozen clock) | BC-6.01.003 Pre-3, PC-1, PC-3 | architect |  |
| ADV-P5-D03 | HIGH | Windows harness false-green | BC-6.02.003 Pre-1, PC-1 | product-owner |  |
| ADV-P5-D04 | HIGH | Wrong statement of legacy behavior | BC-6.03.004:132-137 | product-owner |  |
| ADV-P5-D05 | HIGH | Contradiction: error surface | BC-2.01.005 PC-5/PC-6 and Inv 2 | product-owner [owner-question: class register] |  |
| ADV-P5-D06 | HIGH | Contradiction with interface definitions | BC-2.01.005:85 | product-owner |  |
| ADV-P5-D07 | HIGH | Contradiction: default-only keys | BC-2.01.005:88-90 | product-owner |  |
| ADV-P5-D08 | HIGH | pyfmt: unpinned boundary, signature gap | BC-5.02.006 PC-6, EC-008 | architect |  |
| ADV-P5-D09 | HIGH | pyfmt semantics | BC-5.01.007 PC-3, Inv 1 | product-owner |  |
| ADV-P5-D10 | HIGH | Partial-fix regression (OD-171), blast radius 2 | BC-5.04.002 Inv 2 (lines 70-72) | product-owner |  |
| ADV-P5-D11 | MEDIUM | Contradiction, VP drift | BC-2.02.002:80-84, 121 | product-owner |  |
| ADV-P5-D12 | MEDIUM | Test vector contradicts the range | BC-2.01.005:79 | product-owner |  |
| ADV-P5-D13 | MEDIUM | Untestable grammar | BC-2.01.005 PC-5 | product-owner |  |
| ADV-P5-D14 | MEDIUM | Registry self-contradiction | BC-2.01.004 PC-3(e) | product-owner |  |
| ADV-P5-D15 | MEDIUM | Undefined function, contradicts another BC | BC-2.01.004 PC-6/7 | architect |  |
| ADV-P5-D16 | MEDIUM | Oracle generator defect | BC-5.02.002:124 | product-owner |  |
| ADV-P5-D17 | MEDIUM | Contradicting depth laws | BC-5.02.001 Inv 4 | architect |  |
| ADV-P5-D18 | MEDIUM | Mis-anchor (P4) | BC-5.02.006:80 | product-owner |  |
| ADV-P5-D19 | MEDIUM | Inconsistent shim contract | BC-6.01.003 Pre-3 | product-owner |  |
| ADV-P5-D20 | MEDIUM | Sibling contradiction: entry schema | BC-6.03.003 PC-3 | product-owner |  |
| ADV-P5-D21 | MEDIUM | Harness translation gap | BC-6.02.003 PC-2 | product-owner |  |
| ADV-P5-D22 | MEDIUM | Logic hazard (Windows) | BC-3.02.001 Inv 2 (ADV-P4-D32) | architect |  |
| ADV-P5-D23 | MEDIUM | Per-OS TZ semantics | BC-3.01.001 PC-6 | architect [owner-question] | owner-question |
| ADV-P5-D24 | MEDIUM | P7: H1 vs postconditions | BC-3.01.001 H1 | product-owner |  |
| ADV-P5-D25 | MEDIUM | P18 routing | BC-2.01.001 PC-6, EC-008/009 | architect |  |
| ADV-P5-D26 | MEDIUM | Partial-fix sibling (D31 notation) | BC-5.03.002 EC-002 | product-owner |  |
| ADV-P5-D27 | LOW | Unparsable text | BC-5.01.007 PC-2 (lines 77-81) | product-owner |  |
| ADV-P5-D28 | LOW | Stale signature | BC-5.02.001:38 | product-owner |  |
| ADV-P5-D29 | LOW | Workflow contradiction | BC-6.03.001 PC-6 | architect |  |
| ADV-P5-D30 | LOW | Anchor | BC-2.01.001:87, BC-2.01.004:91 | product-owner |  |
| ADV-P5-D31 | LOW | Ambiguity | BC-2.01.002 PC-4 | product-owner |  |
| ADV-P5-D32 | LOW | Incomplete list | BC-2.01.001 PC-2 | product-owner |  |
| ADV-P5-D33 | COSMETIC | Duplicate row | interface-definitions.md:219-220 | product-owner |  |
