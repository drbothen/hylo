---
document_type: adversarial-review-index
phase: 1d
pass: 6
date: 2026-11-18
findings: 124
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P6 Index — Phase 1d Adversarial Spec Review, Pass 6

Every finding from pass 6, indexed from `pass-6.md`. Severity totals: HIGH 27 / MEDIUM 52 / LOW 38 / COSMETIC 7 — total 124. Against pass 5 (148, 24 HIGH): total -24, HIGH +3.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P6-A01 | HIGH | contradiction / partial-fix regression | architecture/ARCH-02-configuration.md:58-61, :138, :142 | architect |  |
| ADV-P6-A02 | HIGH | contradiction (oracle pin) | prd-supplements/nfr-catalog.md:26 | product-owner, architect |  |
| ADV-P6-A03 | HIGH | cross-platform (P18) / unstated assumption | ARCH-07-parity-harness.md:68-75 | architect | owner-question |
| ADV-P6-A04 | HIGH | config range contradicts default | prd-supplements/interface-definitions.md:263 (`watts` U+26A1) | product-owner | owner-question |
| ADV-P6-A05 | HIGH | architecture contradiction (AD-02) | ARCH-05-platform.md:34 | architect |  |
| ADV-P6-A06 | HIGH | wrong mechanism (would mislead implementer) | ARCH-03-statusline.md:93 | architect |  |
| ADV-P6-A07 | MEDIUM | interface gap / parity | ARCH-06-pyfmt.md:31 ("Mode-site pairing") | architect |  |
| ADV-P6-A08 | MEDIUM | interface cannot express BC | ARCH-02-configuration.md:85, :103-106, :110 | architect |  |
| ADV-P6-A09 | MEDIUM | parity outside the closed set (P13) / config over code (P20) | ARCH-04-data-files.md:61-72 | architect | owner-question |
| ADV-P6-A10 | MEDIUM | CI positive coverage (P11) | ARCH-08:90-93, :98-100 | architect, devops-engineer |  |
| ADV-P6-A11 | MEDIUM | CI gate wiring (P11) | cicd-setup.md:251-257 | devops-engineer |  |
| ADV-P6-A12 | MEDIUM | CI timeout / duplication (P11) | cicd-setup.md:52 | devops-engineer |  |
| ADV-P6-A13 | MEDIUM | ambiguity (default-only keys) | interface-definitions.md:114-153, :195-197, :230 | product-owner |  |
| ADV-P6-A14 | MEDIUM | missing error vocabulary | error-taxonomy.md:76-92 | product-owner |  |
| ADV-P6-A15 | MEDIUM | mis-anchor (P4) | ARCH-04-data-files.md:100 | architect |  |
| ADV-P6-A16 | MEDIUM | mis-anchor (P4) | interface-definitions.md:169 | product-owner |  |
| ADV-P6-A17 | MEDIUM | inactive mitigation | prd-supplements/risk-register.md:29 | architect |  |
| ADV-P6-A18 | MEDIUM | interface gap / ownership ping-pong | ARCH-06:32 | architect |  |
| ADV-P6-A19 | LOW | ambiguity | interface-definitions.md:226-227 | product-owner |  |
| ADV-P6-A20 | LOW | rationale inconsistency (pending intent verification) | ARCH-07:127 | architect |  |
| ADV-P6-A21 | COSMETIC | wording | ARCH-00-overview.md:20 | architect |  |
| ADV-P6-A2-01 | HIGH | Skeleton fails a correct implementation | VP-001:137-163 | architect |  |
| ADV-P6-A2-02 | HIGH | Wrong fault site / wrong oracle | VP-020:52-56, 104-121 | architect |  |
| ADV-P6-A2-03 | HIGH | Test can never fail; invalid Go | VP-016:113-120 | architect |  |
| ADV-P6-A2-04 | HIGH | Never runs on CI (P18) | VP-026:111-136 | architect |  |
| ADV-P6-A2-05 | HIGH | API drift; oracle legs missing | VP-024:85-100 | architect |  |
| ADV-P6-A2-06 | HIGH | Cross-platform (P18) | VP-034:93-105 | architect |  |
| ADV-P6-A2-07 | HIGH | Contradicts BC; would mislead an implementer | domain-spec/state-machines.md:99 | business-analyst, architect |  |
| ADV-P6-A2-08 | HIGH | Partial fix not propagated (2+ files) | VP-016:75, 91, 150 | architect, product-owner |  |
| ADV-P6-A2-09 | MEDIUM | Internal contradiction; routed legs missing | VP-017:40-43, 59-61, 81-83 | architect |  |
| ADV-P6-A2-10 | MEDIUM | Sibling regression | VP-012:122, 70, 74, 162 | architect |  |
| ADV-P6-A2-11 | MEDIUM | Stale prose; P11 | VP-011:57-59, 63-65, 87-93 | architect |  |
| ADV-P6-A2-12 | MEDIUM | Prose contradicts skeleton | VP-021:62-63, 91-92 | architect |  |
| ADV-P6-A2-13 | MEDIUM | Invalid Go | VP-005:102, 108 | architect |  |
| ADV-P6-A2-14 | MEDIUM | Statement vs skeleton | VP-039:43-46, 52, 100-101 | architect |  |
| ADV-P6-A2-15 | MEDIUM | Wrong quantity generated | VP-040:115-124 | architect |  |
| ADV-P6-A2-16 | MEDIUM | Oracle discipline contradiction | VP-041:137-143, 83-85 | architect |  |
| ADV-P6-A2-17 | MEDIUM | Self-confirming oracle | VP-006:110-123, 48, 50 | architect |  |
| ADV-P6-A2-18 | MEDIUM | Skeleton fails a correct implementation | VP-003:77 | architect |  |
| ADV-P6-A2-19 | MEDIUM | Body vs history vs brief | VP-036:44-48, 22 | product-owner | owner-question |
| ADV-P6-A2-20 | MEDIUM | Sibling gap | dtu-assessment.md:27-30, 84-90, 158-166 | architect |  |
| ADV-P6-A2-21 | MEDIUM | P11 positive coverage | VP-035:65 | architect |  |
| ADV-P6-A2-22 | LOW | Versioning | VP-028:42 | architect | process-gap |
| ADV-P6-A2-23 | LOW | Statement vs skeleton | VP-009:37-38, 83 | architect |  |
| ADV-P6-A2-24 | LOW | Stale count | invariants.md:46 | business-analyst |  |
| ADV-P6-A2-25 | LOW | Assessment no longer holds | gene-transfusion-assessment.md:43, 70, 116 | architect |  |
| ADV-P6-A2-26 | LOW | Phase not split; ambiguity | capabilities.md:29, 37 | business-analyst |  |
| ADV-P6-A2-27 | LOW | Coverage scope | VP-035:37, 72 | architect |  |
| ADV-P6-A2-28 | LOW | Oracle not connected to output | VP-015:112 | architect |  |
| ADV-P6-B01 | HIGH | VP anchoring / partial fix | BC-1.02.002:91, .003:104, .006:145-146, .007:102, .009:102, .010:102, .013:118, .015:111 | architect + product-owner | process-gap |
| ADV-P6-B02 | MEDIUM | Test vector doesn't discriminate | BC-1.02.011:88,111 | product-owner |  |
| ADV-P6-B03 | MEDIUM | Wrong source label | BC-1.02.025:85 (EC-010) | product-owner |  |
| ADV-P6-B04 | MEDIUM | Effect-order contract gap | BC-1.01.009:88-92 | product-owner |  |
| ADV-P6-B05 | MEDIUM | Cross-platform gap (P18) | BC-1.02.004:61-69, EC-013 :114 | product-owner |  |
| ADV-P6-B06 | MEDIUM | Missing edge case | BC-1.01.008:49-52, EC table :72-79 | product-owner |  |
| ADV-P6-B07 | MEDIUM | Rationale-code mismatch (P16) | BC-1.02.012:68 | architect |  |
| ADV-P6-B08 | MEDIUM | Sibling not updated after a fix | BC-1.02.023:110 (vs BC-1.02.008:109) | product-owner |  |
| ADV-P6-B09 | MEDIUM | Stale cross-reference (pass-4 B19 sibling) | BC-1.02.027:165 | product-owner |  |
| ADV-P6-B10 | LOW | Vector under-specified | BC-1.02.011:110 | product-owner |  |
| ADV-P6-B11 | LOW | Precondition incomplete | BC-1.01.001:56-61 | product-owner |  |
| ADV-P6-B12 | LOW | Unexplained constant (P16/P20) | BC-1.02.004:41,84-85 | product-owner |  |
| ADV-P6-B13 | LOW | Ambiguous postcondition | BC-1.01.002:61-62 | product-owner |  |
| ADV-P6-B14 | LOW | PRD prose drift | prd.md:452-455 | product-owner |  |
| ADV-P6-B15 | LOW | Stale supplement sentence | interface-definitions.md:300-301 | architect |  |
| ADV-P6-B16 | COSMETIC | Version-history skew | BC-1.01.005:4,22-24 | product-owner |  |
| ADV-P6-C01 | HIGH | contradiction / partial-fix regression | BC-1.03.018:106 (Inv3), :36 | product-owner (architect for ARCH-03) |  |
| ADV-P6-C02 | HIGH | config range drift (P20, partial-fix regression) | BC-1.03.003:45-49 | product-owner |  |
| ADV-P6-C03 | MEDIUM | unspecified quirk / testability | BC-1.03.010:62-65 | product-owner |  |
| ADV-P6-C04 | MEDIUM | ambiguity | BC-1.07.004:57-58 (PC4) | product-owner |  |
| ADV-P6-C05 | LOW | spec drift (wording) | BC-1.07.004:55-56 (PC3) | product-owner |  |
| ADV-P6-C06 | LOW | anchoring consistency (pending intent verification) | BC-1.03.006:120-123, BC-1.03.007:110-113, BC-1.03.010:116-121 (VP tables) | product-owner |  |
| ADV-P6-C07 | LOW | stale count (prose propagation) | BC-1.07.008:122 | product-owner |  |
| ADV-P6-C08 | LOW | test vector inconsistency | BC-1.03.014:78, 87-88 | product-owner |  |
| ADV-P6-C09 | LOW | implementer guidance contradiction | BC-1.03.013:52 (PC2) | product-owner |  |
| ADV-P6-C10 | LOW | oracle definition | BC-1.03.018:86-87 (PC4(a)) | product-owner |  |
| ADV-P6-C11 | LOW | precondition too weak | BC-1.03.012:42-43 | product-owner |  |
| ADV-P6-C12 | LOW | template conformance | BC-1.07.001..008 frontmatter (e.g. BC-1.07.001:14-20) | product-owner |  |
| ADV-P6-C13 | LOW | unclassified foreign-cache shapes (pending intent verification) | BC-1.03.002:86 (EC-007) | product-owner |  |
| ADV-P6-C14 | COSMETIC | wording | BC-1.07.005:85 (EC-006) | product-owner |  |
| ADV-P6-C15 | LOW | cross-platform assumption (pending intent verification) | BC-1.06.001:63 (PC1) | product-owner |  |
| ADV-P6-C16 | LOW | parity-class label (pending intent verification) | BC-1.06.001:26 | product-owner |  |
| ADV-P6-C17 | COSMETIC | incomplete informational column | BC-1.03.018:81 (CP-T07 row) | product-owner |  |
| ADV-P6-C2-01 | HIGH | wrong canonical vector | BC-1.05.002:111 | product-owner |  |
| ADV-P6-C2-02 | HIGH | wrong normative rule | BC-1.04.001:67-69, 106 | product-owner + architect |  |
| ADV-P6-C2-03 | HIGH | contradiction (architecture vs BC) | ARCH-03-statusline.md:187 | architect |  |
| ADV-P6-C2-04 | HIGH | VP skeleton contradicts the BC | VP-020:104-121 | architect |  |
| ADV-P6-C2-05 | MEDIUM | divergence not in the spec (Go header handling) | BC-1.04.001:64-72, 106-108 | architect |  |
| ADV-P6-C2-06 | MEDIUM | unpinned parity constant | BC-1.04.001 PC3 → BC-5.02.003 PC7 | product-owner |  |
| ADV-P6-C2-07 | MEDIUM | deviation without an exclusion id | BC-1.04.001:74-78 | product-owner | owner-question |
| ADV-P6-C2-08 | MEDIUM | spec gap, cross-platform (P18) | BC-1.04.001 (no TLS clause) | architect |  |
| ADV-P6-C2-09 | MEDIUM | partial fix (S-7.01) | BC-1.04.002:25 | product-owner |  |
| ADV-P6-C2-10 | MEDIUM | P2 invariant lift | BC-1.05.007:129 | product-owner |  |
| ADV-P6-C2-11 | LOW | incomplete normalization rule | BC-1.04.001:80-82 | product-owner |  |
| ADV-P6-C2-12 | LOW | ambiguity | BC-1.04.001:54-56 | product-owner |  |
| ADV-P6-C2-13 | LOW | taxonomy cross-reference | error-taxonomy.md:45, :135 | product-owner |  |
| ADV-P6-C2-14 | LOW | P1 numbering | BC-1.04.013:79 | product-owner |  |
| ADV-P6-C2-15 | COSMETIC | metadata drift | BC-1.04.002:7 | product-owner |  |
| ADV-P6-D01 | HIGH | contradiction / test unwritable | BC-2.01.005:91, :129-141, EC-010/011 :162-163 | product-owner |  |
| ADV-P6-D02 | HIGH | default fails its own validation (Unicode 14 width) | BC-2.01.004:136 (watts `⚡` U+26A1), PC-6 last sentence :151-152, PC-3(c) :100 | product-owner [owner-question] (OD-02 vs legacy default) | owner-question |
| ADV-P6-D03 | HIGH | contradiction | BC-2.01.004:141 | product-owner |  |
| ADV-P6-D04 | HIGH | partial-fix regression (blast radius 5) | BC-2.01.002:135 ("closed six-class register (no seventh class)") | product-owner + architect |  |
| ADV-P6-D05 | HIGH | cross-BC contradiction (parity infeasible) | BC-6.02.003 PC-8 :154-162 | architect |  |
| ADV-P6-D06 | HIGH | cross-platform / signature gap (P18) | BC-5.04.001 PC-6 :66-74 | architect |  |
| ADV-P6-D07 | MEDIUM | test vector mislabeled (re-raises rejected ADV-P5-D16) | BC-5.02.002:126 (generator literal) | product-owner |  |
| ADV-P6-D08 | MEDIUM | missing per-site budget | BC-5.02.006 PC-6 table :86-95 | product-owner |  |
| ADV-P6-D09 | MEDIUM | internal contradiction | BC-5.01.007 PC-3 :85-93, PC-4 :102-109 | product-owner |  |
| ADV-P6-D10 | MEDIUM | partial-fix regression | BC-5.04.001 Pre-2 :48-50 | product-owner |  |
| ADV-P6-D11 | MEDIUM | partial-fix regression | BC-6.01.003 CTV row 1 :152 | product-owner |  |
| ADV-P6-D12 | MEDIUM | partial-fix regression | BC-2.02.001 PC-6 :84-85 | product-owner |  |
| ADV-P6-D13 | MEDIUM | partial-fix regression | BC-2.02.001 Refactoring Notes :257 | product-owner |  |
| ADV-P6-D14 | MEDIUM | contradiction | BC-2.02.001:123-134 | product-owner |  |
| ADV-P6-D15 | MEDIUM | ambiguity | BC-2.01.001 PC-6 :79-80 | product-owner |  |
| ADV-P6-D16 | MEDIUM | oracle drift | BC-6.01.001 PC-3 :72 | architect | owner-question |
| ADV-P6-D17 | MEDIUM | architecture grounding error (cross-check) | ARCH-06:221-223 | architect |  |
| ADV-P6-D18 | LOW | factual error in rationale | BC-5.01.007 PC-2 :73-74, EC-005 :134 | product-owner |  |
| ADV-P6-D19 | LOW | ambiguity | BC-2.02.005 PC-4 :60 | product-owner |  |
| ADV-P6-D20 | LOW | internal tension | BC-2.03.002 PC-5 :97-98 | product-owner |  |
| ADV-P6-D21 | LOW | spec accuracy | BC-3.01.001 PC-6 :69-80 | product-owner |  |
| ADV-P6-D22 | LOW | stale anchor (P4) | BC-5.03.004 Inv 3 :63-68, Source :111 | product-owner |  |
| ADV-P6-D23 | LOW | mis-anchor (P4) | BC-2.01.004 PC-9 :176 | product-owner |  |
| ADV-P6-D24 | LOW | partial-fix regression | BC-6.03.004 EC-006 :183 | product-owner |  |
| ADV-P6-D25 | LOW | ambiguity | ARCH-06:166 | architect |  |
| ADV-P6-D26 | COSMETIC | numbering | BC-3.01.001 EC table :104-106 | product-owner |  |
| ADV-P6-D27 | COSMETIC | consistency | BC-6.01.002 Description :48 | product-owner |  |
