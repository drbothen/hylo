---
document_type: adversarial-review-index
phase: 1d
pass: 11
date: 2026-11-18
findings: 62
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P11 Index — Phase 1d Adversarial Spec Review, Pass 11

Every finding from pass 10, indexed from `pass-11.md`. Severity totals: HIGH 11 / MEDIUM 21 / LOW 27 / COSMETIC 3 — total 62. Against pass 10 (69, 8 HIGH): total -7, HIGH +3.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P11-A01 | HIGH | Mis-anchoring / spec drift (P4, P13 risk) | prd-supplements/interface-definitions.md:86-92 | product-owner |  |
| ADV-P11-A02 | HIGH | CI false-fail versus build order (P11) | architecture/ARCH-08-build-ci-release.md:105-108, 191-192 | architect |  |
| ADV-P11-A03 | MEDIUM | CI semantics / ambiguity (P11) | ARCH-08:99-104 | architect |  |
| ADV-P11-A04 | MEDIUM | CI positive-coverage false-fail (P11) | ARCH-08:133, 178-183 | architect |  |
| ADV-P11-A05 | MEDIUM | Contradiction / NFR completeness | prd.md:494 | product-owner |  |
| ADV-P11-A06 | MEDIUM | Partial-fix propagation | prd-supplements/test-vectors.md:46 (v1.7, frontmatter :4-15) | product-owner |  |
| ADV-P11-A07 | MEDIUM | Ambiguity / CI breakage risk | cicd-setup.md:52, 118, 208 | architect |  |
| ADV-P11-A08 | MEDIUM | Interface cannot express a BC | ARCH-03:48-60, 121-128, 146-150 | architect |  |
| ADV-P11-A09 | MEDIUM | Config default spelling inconsistency | interface-definitions.md:203, 247, 270-271, 276 vs :168-169 | product-owner |  |
| ADV-P11-A10 | LOW | Missing named constant (P20) | ARCH-06:66-75 | architect |  |
| ADV-P11-A11 | LOW | NFR ambiguity | nfr-catalog.md:24, 69-73 | architect |  |
| ADV-P11-A12 | LOW | Coverage-note inaccuracy | architecture/BC-COMPONENT-MAP.md:227, 242-249 | architect |  |
| ADV-P11-A2-01 | HIGH | Contradiction (VP vs BC/ARCH) | VP-018:46-49 | architect |  |
| ADV-P11-A2-02 | HIGH | Contradiction / referee weakening | VP-011:45-50 (also VP-009:43-47) | architect |  |
| ADV-P11-A2-03 | HIGH | False for-all / property clear only from the sketch (OD-182) | VP-021:42-46, :66-67 (sketch :107) | architect |  |
| ADV-P11-A2-04 | MEDIUM | Cross-VP contradiction / vacuous leg | VP-014:44-47 | architect |  |
| ADV-P11-A2-05 | MEDIUM | Partial-fix propagation; P18 | VP-032:41-45, :59-60 | architect |  |
| ADV-P11-A2-06 | MEDIUM | Stale invariant→BC counts (P2) | invariants.md:31, :35, :46 | business-analyst |  |
| ADV-P11-A2-07 | MEDIUM | Untested path (DI-008) | VP-003:37-40, :77-78 | architect |  |
| ADV-P11-A2-08 | LOW | Weak for-all assertion | VP-029:54-57 | architect |  |
| ADV-P11-A2-09 | LOW | Frontmatter–body coherence (P5) | VP-009:13 | architect |  |
| ADV-P11-A2-10 | LOW | Frontmatter–body coherence | VP-010:56-59 | architect |  |
| ADV-P11-A2-11 | LOW | Ambiguity | VP-040:50-52 | architect |  |
| ADV-P11-B01 | MEDIUM | Semantic anchoring / traceability (pattern) | BC-1.02.001:95 (EC-007), BC-1.02.003:79 (EC-006), BC-1.02.006:121 (EC-008), BC-1.02.008:70 (EC-006), BC-1.02.014:102 (EC-010) | product-owner (EC IDs); architect (taxonomy/ARCH-03 circular reference) | process-gap |
| ADV-P11-B02 | MEDIUM | Missing edge case (parity-visible) | BC-1.02.004:109-112 (PC2.4) vs legacy SL:385-386 | product-owner |  |
| ADV-P11-B03 | MEDIUM | Partial-fix propagation (untested postcondition) | BC-1.01.005:54-63 (PC4) | product-owner (EC/vector); architect (VP-040 P7 generator) |  |
| ADV-P11-B04 | LOW | Mis-anchor (stale label) | BC-1.01.001:60-61 vs :141 | product-owner |  |
| ADV-P11-B05 | LOW | Config-over-code range gap | BC-1.01.006:65-68 (Inv 1) | architect (range); product-owner (Inv 1) |  |
| ADV-P11-B06 | LOW | Thresholds/format constants not declared (pending intent verification) | BC-1.02.014:62-65 | product-owner |  |
| ADV-P11-B07 | LOW | PRD↔BC traceability | prd.md:507 (E-REN-002 contract column) | product-owner |  |
| ADV-P11-B08 | LOW | Oracle sensitivity, unverified [owner-question] | BC-1.02.022:58 (PC3 `a\0b`), :76 (EC-006) | architect | owner-question |
| ADV-P11-B09 | COSMETIC | Edge-case wording | BC-1.02.028:72 (EC-004) vs :89 | product-owner |  |
| ADV-P11-C01 | HIGH | Wrong expected output; partial-fix regression of ADV-P10-C01 | BC-1.03.007:98 and :107 | product-owner |  |
| ADV-P11-C02 | LOW | Traceability mislabel | BC-1.03.006:135, against BC-1.03.006 PC5 (:69-76) and error-taxonomy.md:223 | product-owner |  |
| ADV-P11-C03 | LOW | Ambiguity / sibling inconsistency (pending intent verification) | BC-1.03.020:39, :45-46 (PC1/Pre-1) and :78 (EC-005) | product-owner |  |
| ADV-P11-C04 | COSMETIC | Bound wording drift | BC-1.07.001:111 (VP-004 row) | product-owner |  |
| ADV-P11-C2-01 | HIGH | contradiction / semantic anchoring | VP-031 L61-67 and key-order table L71-88 | architect (VP-031), product-owner (BC-1.04.003 L130) |  |
| ADV-P11-C2-02 | MEDIUM | sibling not updated after a fix (P2) | BC-1.04.018 L51-57, L101, L110 | product-owner |  |
| ADV-P11-C2-03 | MEDIUM | P20 config-over-code [owner-question] | BC-1.04.004 PC2 L60 and Pre 3 L52 | product-owner | owner-question |
| ADV-P11-C2-04 | LOW | missing edge cases (OD-160 crash sites) | BC-1.04.009 Pre 1 L47 | product-owner |  |
| ADV-P11-C2-05 | LOW | rationale contradicts itself | BC-1.04.001 PC1 L82-86 vs L88-91 | product-owner |  |
| ADV-P11-C2-06 | LOW | hard-coded literal in prose (partial P20 sweep) | BC-1.04.021 L38-41, L46-47, L55 | product-owner |  |
| ADV-P11-C2-07 | LOW | stale cross-reference after a pass-9 move | VP-020 L56 | architect |  |
| ADV-P11-C2-08 | LOW | legacy line citations drifted | BC-1.04.001 L126 | product-owner |  |
| ADV-P11-C2-09 | COSMETIC | metadata | BC-1.04.012 L4 vs L24 | product-owner |  |
| ADV-P11-D01 | HIGH | cross-BC contradiction / harness | BC-6.03.003:77-81, 108, 151 | product-owner [process-gap] | process-gap |
| ADV-P11-D02 | HIGH | contradiction / metrics-URL injection | BC-6.01.002:91-95, 112-125, 144-147 | product-owner |  |
| ADV-P11-D03 | HIGH | P7 title drift / partial-fix regression | BC-6.04.001:41, 46, 120, 128 vs :67-71 | product-owner |  |
| ADV-P11-D04 | MEDIUM | P19 hardening | BC-6.04.001:72-88 vs ARCH-08:46, 235-239 | architect / product-owner |  |
| ADV-P11-D05 | MEDIUM | legacy mismatch / Windows | BC-5.03.004:52-53 | product-owner |  |
| ADV-P11-D06 | MEDIUM | wrong boundary (S5 Windows localtime domain) | BC-5.04.001:54-56 | product-owner |  |
| ADV-P11-D07 | MEDIUM | mis-anchor (P4) | BC-2.03.002:84 vs :76, BC-2.01.001:156, BC-2.01.004:115 | product-owner |  |
| ADV-P11-D08 | HIGH | P20 / partial-fix regression | BC-2.01.004:209 | product-owner |  |
| ADV-P11-D09 | MEDIUM | CI positive-coverage | BC-6.02.001:83-97 vs ARCH-08:175-177 | product-owner |  |
| ADV-P11-D10 | LOW | traceability vs legacy | BC-5.01.003:115 | product-owner |  |
| ADV-P11-D11 | LOW | contradiction | BC-5.01.005:74-75 vs BC-5.02.006:63-64 | product-owner |  |
| ADV-P11-D12 | LOW | untestable grammar (S2 Text) | BC-2.01.005:149-180 | product-owner |  |
| ADV-P11-D13 | LOW | ambiguity | BC-4.01.002:63-70 vs BC-2.01.001:87-96 | product-owner |  |
| ADV-P11-D14 | LOW | P16 rationale | BC-5.01.004:50-52 vs :131 | product-owner |  |
| ADV-P11-D15 | LOW | signature drift | BC-5.02.002:49 vs ARCH-06:196 | product-owner |  |
| ADV-P11-D16 | LOW | replay hermeticity / Windows | BC-6.02.002:82-97 | product-owner |  |
| ADV-P11-D17 | LOW | cross-check (outside perimeter) | interface-definitions:271 | product-owner |  |
