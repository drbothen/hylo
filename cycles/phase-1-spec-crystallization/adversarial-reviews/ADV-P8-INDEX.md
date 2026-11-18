---
document_type: adversarial-review-index
phase: 1d
pass: 8
date: 2026-11-18
findings: 88
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P8 Index — Phase 1d Adversarial Spec Review, Pass 8

Every finding from pass 8, indexed from `pass-8.md`. Severity totals: HIGH 12 / MEDIUM 36 / LOW 33 / COSMETIC 7 — total 88. Against pass 7 (114, 14 HIGH): total -26, HIGH -2.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P8-A01 | MEDIUM | Mis-anchor (P4/P5) | prd-supplements/interface-definitions.md:314 | product-owner |  |
| ADV-P8-A02 | HIGH | Partial-fix propagation (pass-7 CP-T09) | prd.md:484 | product-owner, architect |  |
| ADV-P8-A03 | HIGH | CI job cannot pass, or checks the wrong thing (P11) | architecture/ARCH-08-build-ci-release.md:79-92 | architect |  |
| ADV-P8-A04 | MEDIUM | Contradiction with settled ruling (P12) [owner-question] | ARCH-08:85-90 | architect / owner | owner-question |
| ADV-P8-A05 | MEDIUM | Stale count inside a fail condition (P11) | ARCH-08:141-144 | architect |  |
| ADV-P8-A06 | MEDIUM | Partial-fix propagation (pass-6 A12 / pass-7 A08) | cicd-setup.md:52, :112-119 vs ARCH-08:60-63 | architect (devops) |  |
| ADV-P8-A07 | MEDIUM | Partial-fix propagation (pass-7 A03 purity seam) | ARCH-02-configuration.md:46 | architect |  |
| ADV-P8-A08 | MEDIUM | Partial-fix propagation (OD-158 schedule) | ARCH-01-binary-cli.md:156 | architect |  |
| ADV-P8-A09 | LOW | Owner list incomplete | prd-supplements/test-vectors.md:45 | product-owner |  |
| ADV-P8-A10 | LOW | Cross-document inconsistency | ARCH-07:151 vs ARCH-03:241-244 | architect |  |
| ADV-P8-A11 | LOW | Ambiguity | error-taxonomy.md:85 | product-owner |  |
| ADV-P8-A12 | LOW | Missing shape spec | interface-definitions.md:122-127 | product-owner |  |
| ADV-P8-A13 | COSMETIC | Pointer drift | ARCH-00-overview.md:21 | architect |  |
| ADV-P8-A2-01 | HIGH | contradiction (BC/OD) | VP-001:54-58 | architect |  |
| ADV-P8-A2-02 | MEDIUM | partial-fix propagation | VP-001:37-44, :111-112, :185 | architect |  |
| ADV-P8-A2-03 | HIGH | statement contradicts BC; rule only in sketch (OD-182) | VP-008:37-40, :74-78 | architect |  |
| ADV-P8-A2-04 | HIGH | rule only in sketch (OD-182); P18 | VP-026:37-53, :96-97 | architect |  |
| ADV-P8-A2-05 | HIGH | mis-anchor (P4) | VP-012:109-110, :240-242 (copied from BC-6.03.004:103) | architect (VP-012), product-owner (register) |  |
| ADV-P8-A2-06 | LOW | label mis-anchor | VP-INDEX:31 | architect |  |
| ADV-P8-A2-07 | HIGH | BC-routed legs with no VP home (pattern) [process-gap] | BC-4.01.001:106 / VP-004:37-61 | architect | process-gap |
| ADV-P8-A2-08 | MEDIUM | contradiction (OD-168) | VP-016:37-42 | architect |  |
| ADV-P8-A2-09 | MEDIUM | contradiction (BC); P18 | VP-019:37-42, :84-85 | architect |  |
| ADV-P8-A2-10 | MEDIUM | ambiguity / oracle gap | VP-013:37-40, :49-54, :61 | architect |  |
| ADV-P8-A2-11 | MEDIUM | sketch contradicts property | VP-007:90-97 | architect |  |
| ADV-P8-A2-12 | MEDIUM | stale assessment claim (P12) | dtu-assessment.md:53, :54, :93 | architect |  |
| ADV-P8-A2-13 | LOW | count drift (P2) | invariants.md:46 | business-analyst |  |
| ADV-P8-A2-14 | LOW | wording vs settled decision | invariants.md:30 | business-analyst, architect |  |
| ADV-P8-A2-15 | LOW | incomplete statement | VP-004:37-44 | architect |  |
| ADV-P8-A2-16 | LOW | within-file propagation | VP-016:166-171 | architect |  |
| ADV-P8-A2-17 | LOW | stale description | VP-022:68-69 | architect, product-owner |  |
| ADV-P8-A2-18 | LOW | sibling gap (pending intent verification) | VP-011:37-44 | architect |  |
| ADV-P8-A2-19 | COSMETIC | naming | VP-030:125-129 | architect |  |
| ADV-P8-B01 | HIGH | Mis-anchoring; partial-fix regression [process-gap] | BC-1.02.030:54, :89 (EC-007), :92 (EC-010), :139 (config keys row) | product-owner | process-gap |
| ADV-P8-B02 | MEDIUM | Contradiction across contracts and config range | BC-1.01.007:40-42 (Description), :52 (PC2), :59 (Inv 1) | product-owner |  |
| ADV-P8-B03 | MEDIUM | Contradiction; P20 anchoring | BC-1.01.003:91-93 vs BC-1.04.004:45-50, interface-definitions:193 | product-owner |  |
| ADV-P8-B04 | MEDIUM | Settled decision not propagated (P12, P18) | BC-1.01.008:37-38, :45, :117 (Decisions row) | product-owner |  |
| ADV-P8-B05 | MEDIUM | Config range mismatch (P20) | BC-1.02.014:83-84 (Inv 3), BC-1.02.025:70-71 (Inv 3) vs interface-definitions:201-202 | architect, product-owner |  |
| ADV-P8-B06 | LOW | Wrong claim in an excluded path (OD-160) | BC-1.01.009:70 (step 7c) vs :90-99 (PC2) | product-owner |  |
| ADV-P8-B07 | LOW | Inexact edge case | BC-1.01.009:115 (EC-001) | product-owner |  |
| ADV-P8-B08 | LOW | Sibling not updated (pending intent verification) | BC-1.02.012:61 (`->`), BC-1.02.016:53 (`·`), BC-1.02.007:55 (` <1%`) | product-owner |  |
| ADV-P8-B09 | LOW | Ambiguous property | BC-1.02.006:147 | product-owner (architect for VP-041) |  |
| ADV-P8-B10 | COSMETIC | Stale line cite | BC-1.02.011:89 (EC-011), BC-1.02.012:88 (EC-013) | product-owner |  |
| ADV-P8-B11 | COSMETIC | Anchor and tag drift | BC-1.02.017:91 (EC-007) | product-owner |  |
| ADV-P8-C01 | MEDIUM | test-vector contradiction | BC-1.07.007:122 | product-owner |  |
| ADV-P8-C02 | MEDIUM | missing edge case / cross-doc contradiction | BC-1.03.021 PC5 and VP row :88 | architect + product-owner |  |
| ADV-P8-C03 | HIGH | partial-fix sibling gap (VP / exclusion reciprocity) | BC-1.03.014:90-91, :97-98 | product-owner |  |
| ADV-P8-C04 | LOW | legacy claim likely wrong | BC-1.07.008:89 (EC-009) | product-owner |  |
| ADV-P8-C05 | LOW | parity gap [owner-question] | BC-1.06.001:120 (EC-009) vs SL:198-206 | product-owner / owner | owner-question |
| ADV-P8-C06 | COSMETIC | inconsistency | BC-1.03.018:100 (and error-taxonomy:206) vs BC-1.03.010:108 | product-owner |  |
| ADV-P8-C2-01 | HIGH | P20 config-over-code / partial-fix sibling | BC-1.04.005:54, BC-1.04.007:61-63, BC-1.04.008:53, BC-1.04.010:52-53, BC-1.04.011:51, BC-1.04.012:57, BC-1.04.017:52, BC-1.04.018:51, BC-1.05.003:69-71 (registry: BC-2.01.004:137-147) | product-owner |  |
| ADV-P8-C2-02 | MEDIUM | Spec gap (urllib quirk) | BC-1.04.001:93-96, 161-164 | product-owner |  |
| ADV-P8-C2-03 | MEDIUM | Ambiguity at the parity edge | BC-1.04.001:82-84 | product-owner |  |
| ADV-P8-C2-04 | MEDIUM | Invariant incomplete [process-gap] | BC-1.04.002:76-86 | product-owner | process-gap |
| ADV-P8-C2-05 | MEDIUM | P2 lift_invariants / sibling propagation | BC-1.04.003:131 | product-owner |  |
| ADV-P8-C2-06 | MEDIUM | VP contradiction with BC | VP-020:55-58 vs BC-1.05.004 PC1 (:72-76), BC-1.05.002 PC5/EC-009 | architect |  |
| ADV-P8-C2-07 | MEDIUM | P4 semantic anchoring | BC-1.05.009:121 | architect |  |
| ADV-P8-C2-08 | MEDIUM | VP leg coverage gap | VP-030:62-66, :92 vs BC-1.04.003:120, BC-1.04.008:89, BC-1.04.015:89, BC-1.04.018:88, BC-1.04.019:80 | architect |  |
| ADV-P8-C2-09 | MEDIUM | Partial-fix regression (ADV-P7-C2-04) | VP-030:72-73 vs BC-1.04.001:55-58 | architect |  |
| ADV-P8-C2-10 | LOW | Mis-anchor (stale label) | BC-1.04.001:292 | product-owner |  |
| ADV-P8-C2-11 | LOW | Cross-doc contradiction | test-vectors.md:14, :45 vs BC-1.04.004:95 | product-owner |  |
| ADV-P8-C2-12 | LOW | Arch/BC inconsistency | ARCH-03:193-195 | architect |  |
| ADV-P8-C2-13 | LOW | Spec gap (http.client limits) | BC-1.04.001:79-81 | product-owner |  |
| ADV-P8-C2-14 | LOW | Ambiguity | BC-1.05.006:89-90 vs PC1:65-69 | product-owner |  |
| ADV-P8-C2-15 | LOW | Test-vector underspecified | BC-1.05.008:53-69 | product-owner |  |
| ADV-P8-D01 | HIGH | Partial-fix sibling / signature drift (P18) | BC-3.01.001:59-60, 62-64 | product-owner, architect | process-gap |
| ADV-P8-D02 | HIGH | Same-document mis-anchor | BC-5.04.002:87-88 vs :44-50 | product-owner |  |
| ADV-P8-D03 | MEDIUM | Legacy mismatch / mis-anchor | BC-5.02.003:49-55 | product-owner |  |
| ADV-P8-D04 | MEDIUM | Contradiction / missing rule | BC-2.01.005:69, 136-140 | product-owner |  |
| ADV-P8-D05 | MEDIUM | Count drift / mis-anchor | BC-2.01.005:140 | product-owner |  |
| ADV-P8-D06 | MEDIUM | Partial-fix propagation | interface-definitions.md:203, 237 vs BC-2.01.005:153-157 | product-owner |  |
| ADV-P8-D07 | MEDIUM | P7: H1 does not describe the postconditions | BC-2.01.005:40, 44, 52-53 | product-owner |  |
| ADV-P8-D08 | MEDIUM | Untestable rule (D15 golden) | BC-2.01.004:104-110, 241-254 | product-owner |  |
| ADV-P8-D09 | MEDIUM | BC vs ARCH contradiction | BC-3.02.001:91-99 vs ARCH-05:30 | architect, product-owner |  |
| ADV-P8-D10 | MEDIUM | Internal contradiction (exclusion closure) | BC-3.02.002:48-54, 58-62, 102-106, 124-125 | product-owner |  |
| ADV-P8-D11 | MEDIUM | Title sync | BC-ALLOCATION.md:267 vs BC-3.01.001:35, BC-INDEX:231, prd:325 | product-owner |  |
| ADV-P8-D12 | MEDIUM | Interface signature drift | BC-4.01.001:46, 51 vs ARCH-01:26, 44-45, 61-63 | product-owner |  |
| ADV-P8-D13 | LOW | Signature drift | BC-6.01.002:132 vs ARCH-01:39 | product-owner |  |
| ADV-P8-D14 | LOW | Exclusion-list inconsistency | BC-6.03.004:146-155 vs BC-2.02.002:138 | product-owner |  |
| ADV-P8-D15 | LOW | Grammar gap | BC-2.01.005:81-121 | product-owner |  |
| ADV-P8-D16 | LOW | Platform seam leak (P18) | BC-3.01.001:85-90 | architect |  |
| ADV-P8-D17 | LOW | Windows ambiguity (P18) | BC-2.01.002:85-90 | product-owner |  |
| ADV-P8-D18 | LOW | Unpinned ordering | BC-2.03.001:53-61 vs BC-2.01.001:86-92 | product-owner |  |
| ADV-P8-D19 | LOW | Threshold unit (P16) | BC-6.04.002:100-102 | product-owner |  |
| ADV-P8-D20 | LOW | Missing limit leg [unverified] | BC-5.02.005:44-68 | product-owner |  |
| ADV-P8-D21 | LOW | CPython detail | BC-5.04.003:72 | product-owner |  |
| ADV-P8-D22 | LOW | Mis-anchor (ARCH) | ARCH-06:32 vs BC-5.03.004:63-68 | architect |  |
| ADV-P8-D23 | COSMETIC | VP row wording | BC-4.01.002:107 | product-owner |  |
| ADV-P8-D24 | COSMETIC | Wording | BC-6.01.003:121 | product-owner |  |
