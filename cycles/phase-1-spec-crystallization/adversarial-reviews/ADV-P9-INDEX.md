---
document_type: adversarial-review-index
phase: 1d
pass: 9
date: 2026-11-18
findings: 85
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P9 Index — Phase 1d Adversarial Spec Review, Pass 9

Every finding from pass 9, indexed from `pass-9.md`. Severity totals: HIGH 15 / MEDIUM 38 / LOW 28 / COSMETIC 4 — total 85. Against pass 8 (88, 12 HIGH): total -3, HIGH +3.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P9-A01 | HIGH | contradiction / missing interface | prd-supplements/interface-definitions.md:392 | product-owner |  |
| ADV-P9-A02 | HIGH | contradiction / partial-fix regression | architecture/ARCH-06-pyfmt.md:70 vs :52, :79-83 | architect |  |
| ADV-P9-A03 | HIGH | P18 / interface mismatch | ARCH-03-statusline.md:151 | architect |  |
| ADV-P9-A04 | MEDIUM | P11: CI can pass while checking nothing | cicd-setup.md:58, :278 vs :61-66, :90-93 | architect / devops |  |
| ADV-P9-A05 | MEDIUM | P11: security-perimeter detector without a positive-coverage line | cicd-setup.md:78-88 | architect / devops |  |
| ADV-P9-A06 | MEDIUM | CI contradiction / missing sequencing | ARCH-08-build-ci-release.md:24-28, :191-195 | architect |  |
| ADV-P9-A07 | MEDIUM | contradiction (premise of OD-193 rationale) | ARCH-07-parity-harness.md:32 vs ARCH-08:87-88 | architect |  |
| ADV-P9-A08 | MEDIUM | partial-fix propagation | prd-supplements/risk-register.md:29 vs ARCH-08:166-174 | architect |  |
| ADV-P9-A09 | MEDIUM | semantic mis-anchor (P4) | prd-supplements/risk-register.md:26 | architect |  |
| ADV-P9-A10 | MEDIUM | partial-fix propagation / incomplete enumeration | prd-supplements/interface-definitions.md:66-78 | product-owner |  |
| ADV-P9-A11 | MEDIUM | config key without a range / missing edge case (P20, OD-162) | prd-supplements/interface-definitions.md:176 | product-owner |  |
| ADV-P9-A12 | MEDIUM | interface ambiguity (single-home rule) | ARCH-01-binary-cli.md:38-41 | architect |  |
| ADV-P9-A13 | LOW | overstated enforcement claim | ARCH-09-reserved-boundaries.md:38-39 | architect |  |
| ADV-P9-A14 | LOW | ambiguity | prd.md:509 | product-owner |  |
| ADV-P9-A15 | LOW | CI timeout budget | cicd-setup.md:58 vs :52 | devops |  |
| ADV-P9-A16 | LOW | diagram contradicts text | ARCH-08-build-ci-release.md:41-43 vs :60-63 | architect |  |
| ADV-P9-A17 | COSMETIC | stale line pointer | ARCH-00-overview.md:21 | architect |  |
| ADV-P9-A2-01 | HIGH | VP property false over its own generator | VP-040:54-56, :87, :120-129 | architect |  |
| ADV-P9-A2-02 | HIGH | VP contradicts its own statement and the BC | VP-013:49-51, :107-115 | architect |  |
| ADV-P9-A2-03 | HIGH | Wrong oracle | VP-013:52-55 | architect |  |
| ADV-P9-A2-04 | HIGH | VP property false on a legal path | VP-030:55-57 | architect |  |
| ADV-P9-A2-05 | MEDIUM | Semantic anchoring (P4) | VP-031:56-59, :72-73 | architect |  |
| ADV-P9-A2-06 | MEDIUM | Weak oracle | VP-001:53-55, :155-159 | architect |  |
| ADV-P9-A2-07 | MEDIUM | Ambiguity / contradiction | VP-016:37-39 vs :53-58 | architect |  |
| ADV-P9-A2-08 | MEDIUM | Internal contradiction (partial fix) | VP-013:37-40 vs :61-64 | architect |  |
| ADV-P9-A2-09 | MEDIUM | Sibling propagation gap | VP-027:38-41 | architect |  |
| ADV-P9-A2-10 | MEDIUM | Detection claimed without an oracle (P11) | VP-006:94-97, :133, :52-56 | architect |  |
| ADV-P9-A2-11 | MEDIUM | Positive-coverage gap (P11) | VP-035:68, :89-97 | architect |  |
| ADV-P9-A2-12 | MEDIUM | Sketch contradicts property (OD-182 cap) | VP-004:102-107 vs :50-53 | architect |  |
| ADV-P9-A2-13 | LOW | Ambiguity | VP-041:45-46 | architect |  |
| ADV-P9-A2-14 | LOW | Method incomplete | VP-041:110-118 | architect |  |
| ADV-P9-A2-15 | LOW | L2 drift | domain-spec/capabilities.md:31 | business-analyst |  |
| ADV-P9-A2-16 | LOW | Scope narrowing | VP-007:57-58 | architect |  |
| ADV-P9-A2-17 | LOW | Stale assessment claim | dtu-assessment.md:54 | architect |  |
| ADV-P9-A2-18 | LOW | Count ambiguity | gene-transfusion-assessment.md:52 vs VP-026:39-40 | architect |  |
| ADV-P9-A2-19 | LOW | Sibling wording | domain-spec/owner-validation-list.md:242 | business-analyst |  |
| ADV-P9-A2-20 | COSMETIC | Sketch / typo | VP-037:40 | architect |  |
| ADV-P9-B01 | HIGH | VP statement wrong (regression from the pass-8 B02 fix) | VP-040 lines 54-56, generator line 87 | architect |  |
| ADV-P9-B02 | MEDIUM | BC/VP mismatch, same pass-8 sweep | BC-1.01.007:100 (VP row), :130-131 (VP Anchors), :65-67 (Inv 1) | product-owner |  |
| ADV-P9-B03 | MEDIUM | Overflow site missing from the crash register (OD-156) | BC-1.02.029:57 (PC1 "in float64"), :59 | architect (taxonomy), product-owner (BC) |  |
| ADV-P9-B04 | MEDIUM | Decode scope not pinned | BC-1.02.004:87-90 (PC2.3), :96-97 (PC3) | product-owner |  |
| ADV-P9-B05 | MEDIUM | Spec drift: which errors stop the walk | BC-1.02.004:96-97 (PC3 "permission error → return \"\" immediately") | product-owner |  |
| ADV-P9-B06 | LOW | Property row has no degrade carve-out | BC-1.02.015:111 | product-owner, architect |  |
| ADV-P9-B07 | LOW | Effect table incomplete | BC-1.01.009:66 (step 4 Write cell) | product-owner |  |
| ADV-P9-C01 | HIGH | Wrong golden; partial-fix regression | BC-1.07.007:125 | product-owner | process-gap |
| ADV-P9-C02 | HIGH | Broken frontmatter (5 files) | BC-1.07.002:22, BC-1.07.003:22, BC-1.07.006:22, BC-1.07.007:22, BC-1.07.008:22 | product-owner | process-gap |
| ADV-P9-C03 | MEDIUM | Contradiction between BCs | BC-1.03.018:127 (Inv 3) | product-owner |  |
| ADV-P9-C04 | MEDIUM | Invariant false under D4-EX-2; untestable VP row | BC-1.03.017:54 (Inv 1), :84 (VP-029 row) | product-owner |  |
| ADV-P9-C05 | MEDIUM | Anchoring contradiction; partial fix | BC-1.07.002:37, :99, :107 | product-owner |  |
| ADV-P9-C06 | MEDIUM | Vacuous vector | BC-1.07.004:76, :119 | product-owner |  |
| ADV-P9-C07 | LOW | Edge case contradicts PC2 | BC-1.07.005:95 (EC-005) | product-owner |  |
| ADV-P9-C08 | LOW | Missing precondition | BC-1.06.001:95-97 (PC4), :130 (vector) | product-owner |  |
| ADV-P9-C09 | LOW | Edge case not exhaustive (OD-160) | BC-1.03.002:87 (EC-008) | product-owner |  |
| ADV-P9-C10 | LOW | Wrong VP reference | BC-1.03.020:105 | product-owner |  |
| ADV-P9-C11 | COSMETIC | Mislabel and misquote | BC-1.03.010:110 (EC-007) | product-owner |  |
| ADV-P9-C2-01 | HIGH | spec drift (HTTP client) | BC-1.04.001:98-101, EC-024 :308 | product-owner |  |
| ADV-P9-C2-02 | MEDIUM | spec drift (redirect normalization) | BC-1.04.001:151-153, 165-182, 199-203 | product-owner, architect |  |
| ADV-P9-C2-03 | MEDIUM | step ordering / unexcluded stdout divergence | BC-1.05.004:60-79 vs EC-005 :108 | product-owner | owner-question |
| ADV-P9-C2-04 | MEDIUM | partial-fix sibling (VP-012 closure) | BC-1.05.009:25 (parity_class `OD-30, OD-166`), BC-INDEX:177 | product-owner, architect |  |
| ADV-P9-C2-05 | MEDIUM | P2 lift invariants (sibling) | BC-1.05.004:144 | product-owner |  |
| ADV-P9-C2-06 | LOW | mis-anchor (stale line labels) [process-gap] | BC-1.04.001:341 | product-owner | process-gap |
| ADV-P9-C2-07 | LOW | wire-byte ambiguity | BC-1.04.001:71-72 | product-owner |  |
| ADV-P9-C2-08 | LOW | mis-anchor | BC-1.04.016:99 | product-owner |  |
| ADV-P9-C2-09 | LOW | P20 convention drift (pending intent verification) | BC-1.04.003:62-65 | product-owner |  |
| ADV-P9-C2-10 | LOW | registry contract column | interface-definitions.md:250, :220, :198 | architect |  |
| ADV-P9-D01 | HIGH | Contradiction between BCs; mis-anchor (pass-8 D10 fix only partly applied) | `ss-06/BC-6.03.004.md:75-76, 94-107, 116-118, 197` | product-owner |  |
| ADV-P9-D02 | MEDIUM | Sibling BC not updated | `ss-03/BC-3.02.001.md:104-109` | product-owner |  |
| ADV-P9-D03 | HIGH | Propagation gap (blast radius 2+ files) | `ss-05/BC-5.02.003.md:107-111` | product-owner, architect |  |
| ADV-P9-D04 | MEDIUM | Contradiction within one BC | `ss-05/BC-5.02.006.md:78-85, 93` | product-owner |  |
| ADV-P9-D05 | HIGH | Propagation gap (2 files) | `ss-02/BC-2.01.004.md:186-194` | product-owner |  |
| ADV-P9-D06 | MEDIUM | Ambiguity in error order and `[from]` | `ss-02/BC-2.01.002.md:94-99` | product-owner |  |
| ADV-P9-D07 | MEDIUM | Ambiguous reason string and class | `ss-02/BC-2.01.005.md:151-162, 166-176` | product-owner |  |
| ADV-P9-D08 | MEDIUM | Missing error handling; per-OS gap (P18) | `ss-02/BC-2.01.005.md:137-164` | product-owner |  |
| ADV-P9-D09 | MEDIUM | Wrong domain statement | `ss-05/BC-5.04.001.md:53-54` (vs its own lines 92-94) | product-owner |  |
| ADV-P9-D10 | MEDIUM | Test that cannot pass; per-OS (P18) | `ss-06/BC-6.01.002.md:160-162` vs `109-112` | product-owner |  |
| ADV-P9-D11 | MEDIUM | Regression detector that detects nothing on some legs [process-gap] | `ss-06/BC-6.01.003.md:121-135` | product-owner | process-gap |
| ADV-P9-D12 | MEDIUM | Integration gap [owner-question] | `ss-06/BC-6.02.002.md:54-79` | product-owner | owner-question |
| ADV-P9-D13 | HIGH | Mis-anchor | `ss-05/BC-5.02.003.md:52-53` | product-owner |  |
| ADV-P9-D14 | LOW | Generator format conflict | `ss-05/BC-5.02.002.md:96-97` vs `135` | product-owner |  |
| ADV-P9-D15 | LOW | Legacy site misdescribed | `ss-05/BC-5.01.007.md:69-70, 152` | product-owner |  |
| ADV-P9-D16 | LOW | CPython algorithm misdescribed (could not verify) | `ss-05/BC-5.04.003.md:75-76` | product-owner |  |
| ADV-P9-D17 | LOW | Domain gap | `ss-05/BC-5.01.004.md:47` | product-owner |  |
| ADV-P9-D18 | LOW | Edge case not covered | `ss-02/BC-2.01.005.md:79-83` | product-owner |  |
| ADV-P9-D19 | LOW | H1 incomplete (P7) | `ss-06/BC-6.04.002.md:39` | product-owner |  |
| ADV-P9-D20 | COSMETIC | Wording | `ss-02/BC-2.02.001.md:87` | product-owner |  |
