---
document_type: adversarial-review-index
phase: 1d
pass: 13
date: 2026-11-18
findings: 72
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P13 Index — Phase 1d Adversarial Spec Review, Pass 13

Every finding from pass 13, indexed from `pass-13.md`. Severity totals: HIGH 11 / MEDIUM 34 / LOW 24 / COSMETIC 3 — total 72. Against pass 12 (73, 13 HIGH): total -1, HIGH -2.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P13-A01 | HIGH | contradiction / closed exit surface | error-taxonomy.md:33-35, :49-61, :154 | product-owner (taxonomy, PRD), architect (ARCH-00) |  |
| ADV-P13-A02 | HIGH | interface gap / anchor to a missing interface | ARCH-00-overview.md:84 | architect |  |
| ADV-P13-A03 | HIGH | CI contradiction / sibling missed in a partial fix | ARCH-08:52 vs :33-40, :308-314 | architect |  |
| ADV-P13-A04 | HIGH | CI contradiction / ambiguity | ARCH-08:58 | architect |  |
| ADV-P13-A05 | MEDIUM | partial-fix regression | ARCH-08:164-168 vs :168-174 | architect |  |
| ADV-P13-A06 | MEDIUM | stale wording | interface-definitions.md:48, :484 | product-owner |  |
| ADV-P13-A07 | MEDIUM | partial-fix regression (2 files) | nfr-catalog.md:89-90 | product-owner |  |
| ADV-P13-A08 | MEDIUM | NFR incomplete | prd.md:501 | product-owner |  |
| ADV-P13-A09 | MEDIUM | unstated assumption | prd.md:501 | product-owner |  |
| ADV-P13-A10 | MEDIUM | threshold rationale contradicts itself (P16) | interface-definitions.md:223-224 | product-owner, architect |  |
| ADV-P13-A11 | MEDIUM | missing risk | risk-register.md:40 | architect |  |
| ADV-P13-A12 | MEDIUM | CI self-test cannot pass (P11) | VP-035:93-108 vs cicd-setup.md:100-101, :295 | architect |  |
| ADV-P13-A13 | MEDIUM | CI timeouts without sizing (P11/P16) | cicd-setup.md:59 (timing, 15 min), :55 (Tier A, 45 min) | architect |  |
| ADV-P13-A14 | LOW | ambiguity | cicd-setup.md:56 vs ARCH-08:55, BC-6.04.001:83-88 | architect |  |
| ADV-P13-A15 | LOW | register coverage rule | error-taxonomy.md:322-345 | product-owner |  |
| ADV-P13-A16 | LOW | ambiguity / diagram drift | ARCH-08:57, :164 | architect |  |
| ADV-P13-A17 | LOW | ambiguity [owner-question] | cicd-setup.md:102-103, :86, :37 | architect | owner-question |
| ADV-P13-A18 | LOW | ambiguity | prd.md:519 | product-owner |  |
| ADV-P13-A19 | COSMETIC | wording | ARCH-05-platform.md:92-93 | architect |  |
| ADV-P13-A2-01 | HIGH | Missing oracle / vacuous property (P11, P4) | VP-001-never-blank-exit0.md:124-131, :243-248 | renderGrammar" finds only VP-001; ARCH-07 has no classifier either. So the oracle for "normal render bytes" is undefined, and the check is either vacuous or cannot be built. Separately, the statement decides the unknown-flag and config-error surfaces "by byte equality" against fixed constants. Both lines are parameterised: `<flag>` per VP-002:40, and `<key>=<value> (<reason>)` per VP-016:43. A fuzz over argv can therefore never match a constant. |  |
| ADV-P13-A2-02 | HIGH | Contradiction with BC/NFR; incomplete fix propagation | VP-036-render-latency-p95.md:37-43, :83 | architect |  |
| ADV-P13-A2-03 | MEDIUM | Internal contradiction in a normative statement | VP-001-never-blank-exit0.md:124-127 vs :51-54 | architect |  |
| ADV-P13-A2-04 | MEDIUM | Semantic anchoring (P4) | VP-014-d4ex1-windows-window-age.md:13, :41-43 | architect + product-owner |  |
| ADV-P13-A2-05 | MEDIUM | Config over code (P20); coverage gap | VP-033-process-probe-correctness.md:38, :68, :82 | architect |  |
| ADV-P13-A2-06 | MEDIUM | Oracle independence | VP-012-exclusion-set-closure.md:85-95, :225-244 | architect |  |
| ADV-P13-A2-07 | LOW | Stale count (P2) | domain-spec/invariants.md:31, :46 | business-analyst |  |
| ADV-P13-A2-08 | LOW | Boundary mismatch (P16) | product-brief.md:90-92 vs VP-036:53, :104 | architect |  |
| ADV-P13-A2-09 | LOW | Ambiguity in typed-error fields | VP-017-exactly-one-backend.md:38-39, :84-85 | architect |  |
| ADV-P13-A2-10 | LOW | Closed enumeration too narrow | VP-035-corpus-hygiene.md:37-39, :80-82 | architect |  |
| ADV-P13-A2-11 | LOW | Assessment claim no longer complete | gene-transfusion-assessment.md:53 | architect |  |
| ADV-P13-B01 | MEDIUM | test-vector contradiction / partial-fix | BC-1.01.001:111 vs :117 | product-owner |  |
| ADV-P13-B02 | MEDIUM | test-vector determinism / sibling not updated / mis-reference | BC-1.02.029:110-123 | product-owner |  |
| ADV-P13-B03 | MEDIUM | semantic mis-anchor (P4/P5) | BC-1.01.001:103 (EC-003) | product-owner |  |
| ADV-P13-B04 | MEDIUM | semantic mis-anchor in a cited VP | VP-019:22 (1.2 entry), :52-54, :63-64 | architect |  |
| ADV-P13-B05 | LOW | VP reciprocity | BC-1.01.009:146-150, :184-187 vs VP-019:13, :65-68 | product-owner |  |
| ADV-P13-B06 | LOW | stale wording after a ruling (pending intent verification) | BC-1.02.017:71-74 (Inv 3) vs BC-3.02.001:131 (EC-008) | product-owner |  |
| ADV-P13-B07 | LOW | cross-doc mislabel | error-taxonomy.md:289 (CP-C07, cited by BC-1.02.007:84) | architect |  |
| ADV-P13-B08 | COSMETIC | wording | BC-1.01.009:73 | product-owner |  |
| ADV-P13-C01 | HIGH | contradiction / settled decision (P12) | BC-1.06.001.md:52-55 | product-owner |  |
| ADV-P13-C02 | MEDIUM | missing postcondition | BC-1.06.001.md:113-125 (no row) vs BC-3.01.001.md:133, ARCH-04-data-files.md:26-28 | product-owner |  |
| ADV-P13-C03 | MEDIUM | mis-anchor (P4) | BC-1.06.001.md:84 | product-owner |  |
| ADV-P13-C04 | MEDIUM | likely wrong measured claim (confidence MEDIUM, not run) | BC-1.03.021.md:76-77 | architect |  |
| ADV-P13-C05 | MEDIUM | untestable / register gap | BC-1.03.002.md:86 (EC-007) | product-owner / architect |  |
| ADV-P13-C06 | MEDIUM | mis-anchor (P4) | BC-1.07.002.md:82-84 | product-owner |  |
| ADV-P13-C07 | MEDIUM | missing canonical vector | BC-1.03.005.md:106-113 | product-owner |  |
| ADV-P13-C08 | MEDIUM | mis-anchor in a cross-check index (P4) | prd-supplements/test-vectors.md:47 | product-owner |  |
| ADV-P13-C09 | LOW | under-specification | BC-1.07.002.md:62-63, 92 | architect |  |
| ADV-P13-C10 | LOW | internal inconsistency | BC-1.03.011.md:43-44 vs :67 | product-owner |  |
| ADV-P13-C2-01 | MEDIUM | Partial-fix regression (sibling lift) | BC-1.04.004.md:75-85, :126, :112-117 | product-owner |  |
| ADV-P13-C2-02 | MEDIUM | Contradiction (BC vs architecture) | ARCH-03-statusline.md:81-82 vs BC-1.04.002.md:87-113 | architect |  |
| ADV-P13-C2-03 | MEDIUM | Register completeness | error-taxonomy.md:276-292 vs BC-1.04.002 Inv 1, BC-1.04.003 EC-008/EC-010, BC-1.04.009 EC-011, BC-1.04.004 Inv 3, BC-1.04.018 PC1 | architect / owner | owner-question |
| ADV-P13-C2-04 | MEDIUM | Partial-fix regression (index propagation) | error-taxonomy.md:178 | architect / product-owner |  |
| ADV-P13-C2-05 | MEDIUM | P20 sibling sweep gap | BC-1.04.011.md:54-60 (also BC-1.04.007.md:60-63) | product-owner |  |
| ADV-P13-C2-06 | LOW | Testability gap | BC-1.04.016.md:46-51, :108 | product-owner |  |
| ADV-P13-C2-07 | LOW | Missing edge case | BC-1.04.007.md:62-64 | product-owner |  |
| ADV-P13-C2-08 | LOW | Inaccurate claim | BC-1.04.002.md:59-60, EC-006 :128 | product-owner |  |
| ADV-P13-C2-09 | COSMETIC | Line-cite drift | BC-1.04.009.md:66 | product-owner |  |
| ADV-P13-D01 | HIGH | Cross-platform / fail-closed harness (partial-fix regression) | BC-6.01.003:127 | product-owner |  |
| ADV-P13-D02 | HIGH | Positive coverage, POL-11 [process-gap] | BC-6.01.003:145-148, 155-163 | product-owner | process-gap |
| ADV-P13-D03 | HIGH | Child-env contradiction (pass-12 propagation gap) | BC-6.01.002:109 vs 135-145, CTV 241, PC-3 :183 | product-owner + architect |  |
| ADV-P13-D04 | MEDIUM | Mis-anchor, sibling not updated | ARCH-07:136-138 vs BC-6.01.002:102-104 | architect |  |
| ADV-P13-D05 | HIGH | Internal contradiction, P4/P18 | BC-3.01.001:123 (Inv 2), :162 (VP-032 row) vs :64 (PC-2), CTV :153 | product-owner |  |
| ADV-P13-D06 | MEDIUM | CI spec drift | BC-6.04.001:55-57 vs :87-89 | product-owner |  |
| ADV-P13-D07 | MEDIUM | Unspecified decoder | BC-6.02.002:70-71 vs :90-91, :115-118 | product-owner |  |
| ADV-P13-D08 | MEDIUM | Cross-BC contradiction | BC-5.01.002:36-38 vs BC-2.02.003:64-69, BC-2.02.002 EC-007 | product-owner |  |
| ADV-P13-D09 | MEDIUM | Missing error verdict | BC-2.01.005:74-87, :196-204 | product-owner |  |
| ADV-P13-D10 | LOW | VP drift | BC-6.04.002:168 vs :114-129 | product-owner |  |
| ADV-P13-D11 | LOW | Spec ambiguity | BC-5.02.002:51 vs :55-59 | product-owner |  |
| ADV-P13-D12 | LOW | Anchor completeness | BC-5.03.002:71-72 | product-owner |  |
| ADV-P13-D13 | LOW | Namespace/range inconsistency (pending intent verification) [owner-question] | BC-2.01.004:289-292 vs :165, :282-284 | product-owner | owner-question |
| ADV-P13-D14 | LOW | Untestable invariant | BC-5.01.007:138-141 | product-owner |  |
| ADV-P13-D15 | LOW | Machinery gap | BC-6.02.001:77-82 vs BC-6.03.004:78, PC-1 | product-owner |  |
