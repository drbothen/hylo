---
document_type: adversarial-review-index
phase: 1d
pass: 10
date: 2026-11-18
findings: 69
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P10 Index — Phase 1d Adversarial Spec Review, Pass 10

Every finding from pass 10, indexed from `pass-10.md`. Severity totals: HIGH 8 / MEDIUM 33 / LOW 23 / COSMETIC 5 — total 69. Against pass 9 (85, 15 HIGH): total -16, HIGH -7.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P10-A01 | HIGH | contradiction, CI (P11) | cicd-setup.md:88 vs :58, :151-152 | architect |  |
| ADV-P10-A02 | MEDIUM | partial-fix regression, CI timeout (P11) | cicd-setup.md:148-149 vs :58 | architect |  |
| ADV-P10-A03 | HIGH | CI cannot do what the spec requires, hygiene [process-gap] | cicd-setup.md:135-143 | architect | process-gap |
| ADV-P10-A04 | MEDIUM | CI could pass while checking nothing (P11) | ARCH-08:134-147, :182-184 | architect |  |
| ADV-P10-A05 | MEDIUM | CI could pass while checking nothing (P11) | ARCH-08:164-167 | architect |  |
| ADV-P10-A06 | MEDIUM | CI could pass while checking nothing (P11) | ARCH-08:105, :169-173 | architect |  |
| ADV-P10-A07 | HIGH | partial-fix regression, error vocabulary | error-taxonomy.md:101 | product-owner |  |
| ADV-P10-A08 | MEDIUM | mis-anchor (P4) | risk-register.md:29 | architect |  |
| ADV-P10-A09 | MEDIUM | contradiction about P1 exit gates | nfr-catalog.md:64-65 vs ARCH-08:207-209, risk-register.md:29, ARCH-INDEX.md:106-108 | product-owner |  |
| ADV-P10-A10 | MEDIUM | mis-anchor, circular reference (P4) | ARCH-03:195 | architect |  |
| ADV-P10-A11 | MEDIUM | interface cannot express a requirement | ARCH-02:91, :117 | architect |  |
| ADV-P10-A12 | LOW | interface gap | ARCH-06:151, :257-279 | architect |  |
| ADV-P10-A13 | LOW | VP catalog drift (P9) | module-criticality.md:58, :72-79 vs VP-INDEX.md:112 | product-owner |  |
| ADV-P10-A14 | LOW | internal inconsistency | error-taxonomy.md:104 vs :86-88 | product-owner |  |
| ADV-P10-A15 | LOW | stale history notes | error-taxonomy.md:95 | product-owner |  |
| ADV-P10-A16 | LOW | stale comment | ARCH-06:178-183 | architect |  |
| ADV-P10-A17 | COSMETIC | wording | interface-definitions.md:36 | product-owner |  |
| ADV-P10-A2-01 | HIGH | for-all property false for legal input | VP-004:38-42, 55-57, 77-79, 130 | architect (VP-004); product-owner (BC rows) |  |
| ADV-P10-A2-02 | MEDIUM | oracle classifier uses the wrong decode mode (lets bad ports pass) | VP-001:144-147 | architect |  |
| ADV-P10-A2-03 | MEDIUM | contradicts a BC / semantic anchor | VP-028:40-41 | architect |  |
| ADV-P10-A2-04 | MEDIUM | VP-INDEX title drift (P9) | VP-INDEX:82 vs VP-008:33 | architect |  |
| ADV-P10-A2-05 | MEDIUM | overclaim: no leg can catch a wrong constant at a call site | VP-006:37-43, 94-103, 131-149 | architect |  |
| ADV-P10-A2-06 | MEDIUM | stated scopes have no oracle | VP-012:66-73, 137-150 | architect |  |
| ADV-P10-A2-07 | MEDIUM | pass/fail rule only clear from the sketch | VP-014:37-41, 53-56 | architect |  |
| ADV-P10-A2-08 | LOW | contradiction inside the statement | VP-001:49-59 | architect |  |
| ADV-P10-A2-09 | LOW | absence claim false for one legal input (pending intent verification) | VP-022:38-53 | architect / business-analyst |  |
| ADV-P10-A2-10 | LOW | sketch contradicts its property (P11) | VP-012:191-196 vs :74-79 | architect |  |
| ADV-P10-B01 | MEDIUM | Contradiction between BCs | BC-1.01.008.md:78 vs BC-1.01.003.md:60-64 | product-owner |  |
| ADV-P10-B02 | MEDIUM | Ambiguity; not testable; cross-platform (P18) | BC-1.02.004.md:93-101 | product-owner |  |
| ADV-P10-B03 | MEDIUM | Semantic anchoring (P4); partial fix of ADV-P9-B03 | BC-1.02.006:122/141, .011:89, .012:91, .014:104, .017:93, .020:89, .029:87 | architect (VP-001), product-owner (BC tables) |  |
| ADV-P10-B04 | LOW | Incorrect equivalence claim | BC-1.01.005.md:54-57 | product-owner |  |
| ADV-P10-B05 | LOW | Ordering claim incomplete (foreign cache, OD-160) | BC-1.01.009.md:72, 79, 92-94 | product-owner |  |
| ADV-P10-B06 | LOW | Unstated assumption | BC-1.02.004.md:82, 87, 102 | product-owner |  |
| ADV-P10-B07 | COSMETIC | Anchor consistency between sibling BCs | BC-1.02.016..030, Architecture Anchors sections | product-owner |  |
| ADV-P10-C01 | MEDIUM | partial-fix propagation / unreachable vector | BC-1.03.007:78, :98-106 | product-owner | owner-question |
| ADV-P10-C02 | MEDIUM | mis-anchor (line pointer drift) | BC-1.03.010:111 | product-owner | process-gap |
| ADV-P10-C03 | MEDIUM | ambiguity (POSIX surrogate path encoding) | BC-1.03.001:77 (hylo POSIX clause), :22 | product-owner |  |
| ADV-P10-C04 | MEDIUM | VP contradicts postcondition | BC-1.03.005:120 vs PC5 :65-68 | product-owner |  |
| ADV-P10-C05 | MEDIUM | P2 / sibling convention | BC-1.03.005:128 | product-owner |  |
| ADV-P10-C06 | MEDIUM | mis-anchor | error-taxonomy.md:213 | product-owner |  |
| ADV-P10-C07 | MEDIUM | circular owner anchor | ARCH-03-statusline.md:195 | architect |  |
| ADV-P10-C08 | LOW | over-generalized postcondition | BC-1.03.021:63-66, :81 | product-owner |  |
| ADV-P10-C09 | LOW | site-anchor inconsistency | error-taxonomy.md:236-238 vs BC-1.07.008:60-67 | product-owner |  |
| ADV-P10-C10 | LOW | mis-anchor | error-taxonomy.md:297 | product-owner |  |
| ADV-P10-C11 | LOW | stale count | BC-1.07.008:133 | product-owner |  |
| ADV-P10-C12 | COSMETIC | wording | BC-1.07.008:73 | product-owner |  |
| ADV-P10-C2-01 | HIGH | contradiction (partial-fix regression of ADV-P9-C2-02) | BC-1.04.001.md:226-236 (normative Go rule) and :190-191 | product-owner |  |
| ADV-P10-C2-02 | MEDIUM | completeness (claimed-exhaustive crash list) | BC-1.04.002.md:77-93 (Inv 1) | product-owner |  |
| ADV-P10-C2-03 | MEDIUM | mis-anchor | ARCH-03-statusline.md:224-228 | architect |  |
| ADV-P10-C2-04 | MEDIUM | contradiction (cross-document) | ARCH-03-statusline.md:263-266 | architect |  |
| ADV-P10-C2-05 | MEDIUM | mis-anchor | VP-001-never-blank-exit0.md:41-42, :82-83 | architect |  |
| ADV-P10-C2-06 | MEDIUM | P20 sibling miss (ADV-P9-C2-09 sweep) | BC-1.05.005.md:88-90 (PC4) | product-owner |  |
| ADV-P10-C2-07 | LOW | anchor completeness | interface-definitions.md:218, :297-298, :299 (consumer column) | architect |  |
| ADV-P10-C2-08 | LOW | testability | BC-1.04.001.md:63-64 vs Inv 1 (:308) | product-owner |  |
| ADV-P10-C2-09 | LOW | Python quirk unstated | BC-1.04.018.md:47-48 (PC1) | product-owner |  |
| ADV-P10-C2-10 | LOW | mis-anchor (sibling of ADV-P9-C2-08: PC vs Precondition) | prd.md:511 | product-owner |  |
| ADV-P10-C2-11 | LOW | VP citation sibling gap | BC-1.04.001/004/005 (CP-N03), BC-1.05.002 EC-009 (CP-O11 co-owner), BC-1.05.003 EC-011 (CP-O12 co-owner) | architect |  |
| ADV-P10-C2-12 | COSMETIC | P20 note | BC-1.05.003.md:76 | product-owner |  |
| ADV-P10-D01 | HIGH | Contradiction (harness env) | BC-6.01.002:103-124, CTV :209 | product-owner + architect |  |
| ADV-P10-D02 | HIGH | Contradiction with ARCH (anchoring) | BC-6.01.001:109-112 | architect |  |
| ADV-P10-D03 | HIGH | Partial-fix propagation (ADV-P9-A11); P18 | BC-2.01.005:83-89 and :95-96 | product-owner |  |
| ADV-P10-D04 | MEDIUM | Hermeticity gap (harness) | BC-6.02.002 Pre-3 :97-104 vs EC-005 :152 | product-owner |  |
| ADV-P10-D05 | MEDIUM | Spec vs consumer / ARCH-06 signature | BC-5.01.001:45, :59-61 | architect |  |
| ADV-P10-D06 | MEDIUM | Untestable `<value>` (error surface) | BC-2.02.001:78-82, :95-96, :191-194 | product-owner |  |
| ADV-P10-D07 | MEDIUM | Corpus layout anchoring | BC-6.03.004 CTV :213-216, EC-001 :202 | product-owner |  |
| ADV-P10-D08 | LOW | Legacy citation drift | BC-2.01.005:128-129, :211, :213 | product-owner |  |
| ADV-P10-D09 | LOW | CI floor leg mislabelled | BC-6.04.001:66-68 | product-owner / architect |  |
| ADV-P10-D10 | LOW | Unspecified per-OS edge (pending intent verification) | BC-3.01.001:58-65, EC-004 :122 | product-owner |  |
| ADV-P10-D11 | COSMETIC | Notation | BC-5.04.003:74 | product-owner |  |
