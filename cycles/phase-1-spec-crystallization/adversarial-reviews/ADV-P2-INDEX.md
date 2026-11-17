---
document_type: adversarial-review-index
phase: 1d
pass: 2
date: 2026-11-17
findings: 116
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P2 Index — Phase 1d Adversarial Spec Review, Pass 2

Every finding from pass 2, indexed from the verbatim perimeter reports in `pass-2.md`. Severity totals: HIGH 17, MEDIUM 58, LOW 35, COSMETIC 6 — total 116.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P2-A01 | HIGH | Interface can't express a BC | architecture/ARCH-02-configuration.md:67-69 | architect |  |
| ADV-P2-A02 | HIGH | Interface can't express a BC | ARCH-01-binary-cli.md:25-32 | architect |  |
| ADV-P2-A03 | HIGH | Concurrency / data loss | ARCH-04-data-files.md:73-74 (VP-018:39, :100-106) | architect |  |
| ADV-P2-A04 | HIGH | P9: VP catalog drift | prd-supplements/module-criticality.md:49-63 | product-owner |  |
| ADV-P2-A05 | MEDIUM | Contradiction / ambiguity | ARCH-02:76-81 (copies BC-2.01.002:66-77) | architect, product-owner |  |
| ADV-P2-A06 | MEDIUM | Contradiction | ARCH-06-pyfmt.md:28 | architect |  |
| ADV-P2-A07 | MEDIUM | Missing value | ARCH-06:28, :93-96 | architect |  |
| ADV-P2-A08 | MEDIUM | Interface ambiguity | ARCH-03:47, :70, :83 | architect |  |
| ADV-P2-A09 | MEDIUM | Contradiction | ARCH-07-parity-harness.md:32-33 | architect |  |
| ADV-P2-A10 | MEDIUM | Misleads Phase 2 ordering | module-criticality.md:95-113 | product-owner |  |
| ADV-P2-A11 | MEDIUM | Contradiction | prd.md:113, :126 | product-owner |  |
| ADV-P2-A12 | MEDIUM | P20 / DI-010 totality | prd-supplements/interface-definitions.md:120-124, :108-109 | product-owner | owner-question |
| ADV-P2-A13 | MEDIUM | P16 / P20 | ARCH-04:62 | architect |  |
| ADV-P2-A14 | MEDIUM | Contradiction with repo | ARCH-08-build-ci-release.md:23 | architect, devops-engineer |  |
| ADV-P2-A15 | MEDIUM | P11: CI can pass while checking little | ARCH-08:57-58, :65 | architect | process-gap |
| ADV-P2-A16 | MEDIUM | NFR not executable | nfr-catalog.md:24, :55-58 | product-owner |  |
| ADV-P2-A17 | MEDIUM | Contradiction | prd.md:72-73, :556-558 | product-owner | owner-question |
| ADV-P2-A18 | MEDIUM | P4: mis-anchor | ARCH-00-overview.md:93 | architect |  |
| ADV-P2-A19 | MEDIUM | P19: unrecorded dependency | ARCH-06:54 | architect |  |
| ADV-P2-A20 | LOW | Wrong claim | nfr-catalog.md:28 | product-owner |  |
| ADV-P2-A21 | LOW | P4: mis-anchor | prd.md:64 | product-owner |  |
| ADV-P2-A22 | LOW | Stale anchor | ARCH-08:82 | architect |  |
| ADV-P2-A23 | LOW | Ambiguity | ARCH-07:91 | architect |  |
| ADV-P2-A24 | LOW | Stale status | cicd-setup.md:17-24, :33 | devops-engineer |  |
| ADV-P2-A25 | LOW | Interface drift | ARCH-03:93 | architect |  |
| ADV-P2-A26 | COSMETIC | Editorial | ARCH-00:104-109 | architect |  |
| ADV-P2-A2-01 | HIGH | contradiction / parity | domain-spec/state-machines.md:70-74 | product-owner | owner-question |
| ADV-P2-A2-02 | HIGH | VP skeleton fails a correct implementation | VP-012:38,80-81 | architect |  |
| ADV-P2-A2-03 | HIGH | H1 vs body | VP-020:33 (title, also VP-INDEX:76) vs VP-020:37-47 | architect |  |
| ADV-P2-A2-04 | HIGH | P9/P4 residual drift [pattern] | VP-INDEX.md:299-306 | product-owner |  |
| ADV-P2-A2-05 | MEDIUM | VP oracle wrong | VP-038:39,61-63,86 vs legacy dgx_statusline.py:1059 | architect |  |
| ADV-P2-A2-06 | MEDIUM | VP skeleton fails a correct implementation | VP-022:42-44,89 vs legacy dgx_statusline.py:369-389 | architect |  |
| ADV-P2-A2-07 | MEDIUM | test cannot fail a wrong implementation | VP-016:37-38,82-91 | architect |  |
| ADV-P2-A2-08 | MEDIUM | vacuous oracle | VP-015:37-43,79-85 | architect |  |
| ADV-P2-A2-09 | MEDIUM | wrong method / vacuous | VP-012:15,59-68,78-92 | architect |  |
| ADV-P2-A2-10 | MEDIUM | wrong oracle | VP-023:75 | architect |  |
| ADV-P2-A2-11 | MEDIUM | skeleton does not compile or run | VP-002:86-88 | architect |  |
| ADV-P2-A2-12 | MEDIUM | skeleton ignores its table | VP-032:72-77 | architect |  |
| ADV-P2-A2-13 | MEDIUM | coverage gap | VP-006:36-43,74-77 | architect |  |
| ADV-P2-A2-14 | MEDIUM | false closure claim | VP-031:37-46,76-77 vs legacy dgx_statusline.py:83 | architect |  |
| ADV-P2-A2-15 | MEDIUM | concurrency / unexplained threshold | VP-018:38-40,100-106 | architect | owner-question |
| ADV-P2-A2-16 | MEDIUM | contradiction (P18) | gene-transfusion-assessment.md:116-118 | architect |  |
| ADV-P2-A2-17 | MEDIUM | P18 isolation gap | VP-034:40-41,80-85 | architect |  |
| ADV-P2-A2-18 | MEDIUM | P2 enforcer mismatch | invariants.md:40 vs BC-1.02.001:74,123 | business-analyst |  |
| ADV-P2-A2-19 | MEDIUM | P4 mis-anchor | capabilities.md:29 | business-analyst |  |
| ADV-P2-A2-20 | MEDIUM | P4 mis-anchor | bounded-contexts.md:44-45 | business-analyst |  |
| ADV-P2-A2-21 | MEDIUM | contradiction | gene-transfusion-assessment.md:54 | architect |  |
| ADV-P2-A2-22 | LOW | ambiguity | product-brief.md:74 | product-owner |  |
| ADV-P2-A2-23 | LOW | stale assessment | architecture-feasibility-report.md:26,33 | architect |  |
| ADV-P2-A2-24 | LOW | ambiguity / factual | VP-026:39-42,66,91 | architect |  |
| ADV-P2-A2-25 | LOW | skeleton weaker than property | VP-005:41-43,74-83 | architect |  |
| ADV-P2-A2-26 | LOW | class / skeleton | VP-011:56-59,72-83 | architect |  |
| ADV-P2-A2-27 | LOW | internal inconsistency | VP-036:40-42 vs :70 | architect |  |
| ADV-P2-A2-28 | LOW | ambiguity | VP-018:39-45,94-95 | architect |  |
| ADV-P2-A2-29 | COSMETIC | typo / frontmatter | gene-transfusion-assessment.md:34 | architect |  |
| ADV-P2-B01 | HIGH | Parity gap (spec-implementation) | BC-1.02.006:65-66 / BC-1.02.020:51-52 (legacy SL:435) | product-owner |  |
| ADV-P2-B02 | HIGH | Contradiction / P20 / partial-fix propagation | BC-1.02.006:49,65-68,78-81 | architect + product-owner |  |
| ADV-P2-B03 | HIGH | Mis-anchor (config key) | BC-1.02.021:79 | product-owner |  |
| ADV-P2-B04 | MEDIUM | Contradiction / P20 | BC-1.01.001:66-67, :163 | product-owner |  |
| ADV-P2-B05 | MEDIUM | Interface mismatch / parity | BC-1.02.026:45 vs ARCH-06-pyfmt.md:76, BC-5.01.003:58 | product-owner |  |
| ADV-P2-B06 | MEDIUM | P20 non-default behavior undefined | BC-1.02.019:44, 50-52 | product-owner |  |
| ADV-P2-B07 | MEDIUM | Semantic anchoring (VP) | BC-1.01.001:98-99, 131 vs VP-INDEX.md:57,59 | product-owner |  |
| ADV-P2-B08 | MEDIUM | VP method coherence [pattern] | BC-1.01.003:106, BC-1.01.004:85-86, BC-1.01.005:95, BC-1.01.006:95-96, BC-1.01.007:87 vs VP-027:15,57-60 | architect |  |
| ADV-P2-B09 | MEDIUM | P2 invariant scope mismatch | invariants.md:40 vs BC-1.02.001:72-74, 123 | product-owner |  |
| ADV-P2-B10 | LOW | P5 mechanical citation | BC-1.02.020:112 | product-owner |  |
| ADV-P2-B11 | LOW | Q-b consistency | BC-1.02.017:68, 79-83 | product-owner [owner-question] | pending intent verification; owner-question |
| ADV-P2-B12 | LOW | Unsound invariant/property | BC-1.01.006:62, 95 (legacy SL:1196) | product-owner |  |
| ADV-P2-B13 | LOW | Missing edge case | BC-1.01.005:40-48 | product-owner |  |
| ADV-P2-B14 | LOW | Structure | BC-1.01.009:69 | product-owner |  |
| ADV-P2-B15 | LOW | P20 internal inconsistency | BC-1.02.006:47-49 vs :63-64, :137 | product-owner |  |
| ADV-P2-B16 | LOW | Semantic naming | BC-1.02.029:56, 63, 115 | product-owner |  |
| ADV-P2-B17 | COSMETIC | Numbering | BC-1.02.006:78, 82 | product-owner |  |
| ADV-P2-C01 | HIGH | Parity / missing crash path | BC-1.03.006:53-55 | product-owner | owner-question |
| ADV-P2-C02 | MEDIUM | Parity / cache format | BC-1.03.006:56-57 ("ints as decimal digits of any length") | product-owner |  |
| ADV-P2-C03 | HIGH | P20 / P16 | BC-1.03.003:45-46 ("Range is defined in the S2 schema (OD-114)") | architect + product-owner |  |
| ADV-P2-C04 | MEDIUM | Semantic anchoring (P4) | interface-definitions.md:114 vs BC-1.03.010:49 and legacy SL:958, SL:996 | architect |  |
| ADV-P2-C05 | MEDIUM | Mis-anchor (P4 / P5) | BC-1.06.001:116-117 | architect |  |
| ADV-P2-C06 | MEDIUM | Testability / safety | BC-1.03.015:51-54. Legacy SL:1042 | product-owner | owner-question |
| ADV-P2-C07 | LOW | Parity gap | BC-1.03.005:59, :65-66. Legacy SL:1099 | product-owner |  |
| ADV-P2-C08 | LOW | Contradiction | BC-1.03.004:51-53 vs BC-5.02.003:51-53 | product-owner |  |
| ADV-P2-C09 | LOW | Edge case | BC-1.03.002:86. Legacy SL:1027, SL:1043, SL:1053 | product-owner |  |
| ADV-P2-C10 | LOW | Spec gap | BC-1.06.001:68-72 | product-owner |  |
| ADV-P2-C11 | LOW | Mechanical citation (P5) | BC-1.03.002:115 | product-owner |  |
| ADV-P2-C12 | COSMETIC | Wording / frontmatter | VP-031:41-42, :75 | architect |  |
| ADV-P2-C2-01 | HIGH | P7 title vs postconditions | BC-1.05.006:38 | product-owner |  |
| ADV-P2-C2-02 | MEDIUM | P13 quirk fidelity, BC contradiction | BC-1.04.013:49-50 vs legacy SL:1221 | product-owner |  |
| ADV-P2-C2-03 | MEDIUM | Contradiction, untestable claim | BC-1.04.016:60-62 vs BC-1.04.003:54-55, BC-1.04.014:43-46, legacy SL:337, 662-666 | product-owner |  |
| ADV-P2-C2-04 | MEDIUM | BC vs interface-definitions contradiction (P20) | interface-definitions.md:120-124 vs BC-1.04.007:52-55, BC-1.04.006:42-44 | architect |  |
| ADV-P2-C2-05 | MEDIUM | P20: non-default behavior undefined | BC-1.04.003:43-46 | architect |  |
| ADV-P2-C2-06 | MEDIUM | VP/BC contradiction (P4) | VP-020:37-44, 61-63 vs BC-1.05.004:94, BC-1.05.006:74-75 | architect |  |
| ADV-P2-C2-07 | MEDIUM | P16, partial-fix propagation | BC-1.05.004:126 | product-owner |  |
| ADV-P2-C2-08 | LOW | Untestable postcondition | BC-1.04.001:54-57, 79 | architect |  |
| ADV-P2-C2-09 | LOW | Unspecified raise paths | BC-1.04.001:65-74, 101 vs SL:182-183 | product-owner |  |
| ADV-P2-C2-10 | LOW | Internal formula mismatch | BC-1.04.007:52 vs :92 | product-owner |  |
| ADV-P2-C2-11 | LOW | False claims | BC-1.05.002:85 | product-owner |  |
| ADV-P2-C2-12 | LOW | P16 rationale label drift | BC-1.04.007:43-44 vs SL:746 | product-owner |  |
| ADV-P2-C2-13 | LOW | P2 sibling citation drift | BC-1.04.001:131,143 | product-owner |  |
| ADV-P2-C2-14 | COSMETIC | Citation drift | BC-1.05.006:57-58, 164 | product-owner |  |
| ADV-P2-D01 | HIGH | contradiction / spec-impl recipe | BC-5.01.005:61-63 vs :53-54, :88 | product-owner, architect |  |
| ADV-P2-D02 | HIGH | per-OS gap (P18) | BC-6.02.003:115-116 | product-owner |  |
| ADV-P2-D03 | HIGH | contradiction | BC-6.04.003:54-55 vs BC-6.04.001:47, 71-74 and BC-6.04.003:40, 89-91 | product-owner |  |
| ADV-P2-D04 | MEDIUM | partial-fix regression | BC-6.04.003:107 vs :89-92 | product-owner |  |
| ADV-P2-D05 | MEDIUM | contradiction / fail-closed | BC-6.03.004:106-113 vs BC-6.03.002:79-82 | product-owner |  |
| ADV-P2-D06 | MEDIUM | partial-fix regression / mis-anchor | BC-6.02.003:80 | product-owner |  |
| ADV-P2-D07 | MEDIUM | mis-anchor / wrong rationale | BC-6.03.003:75-78, 118 | product-owner |  |
| ADV-P2-D08 | MEDIUM | interface drift (ARCH-06) | ARCH-06:84, 96, 114, 116 vs BC-5.04.002:34 | architect, product-owner |  |
| ADV-P2-D09 | MEDIUM | internal contradiction [owner-question] | BC-2.02.003:72-73 vs :89, :114 | product-owner | owner-question |
| ADV-P2-D10 | MEDIUM | ambiguity (untestable) | BC-2.01.002:66-77 | product-owner |  |
| ADV-P2-D11 | MEDIUM | semantic gap [owner-question] | BC-2.03.002:37, 61, 66 vs BC-3.01.001:57-58 | product-owner | owner-question |
| ADV-P2-D12 | MEDIUM | harness hermeticity | BC-6.01.002:81-83 | product-owner |  |
| ADV-P2-D13 | MEDIUM | semantic anchoring (P4) | VP-038:14, 39, 96 vs BC-5.03.002:57-59 | architect |  |
| ADV-P2-D14 | LOW | ambiguity | BC-6.02.002:58, 70-71, 89-92 | product-owner |  |
| ADV-P2-D15 | LOW | vector notation | BC-5.02.004:73-74 | product-owner |  |
| ADV-P2-D16 | LOW | unverified claim (pending verification) | BC-4.01.003:66, 51 | product-owner | pending verification |
| ADV-P2-D17 | LOW | per-OS ambiguity | BC-2.01.001:71-72, 99 | product-owner |  |
| ADV-P2-D18 | COSMETIC | wording | BC-5.01.004:56 | product-owner |  |

## Totals by perimeter

| Perimeter | HIGH | MEDIUM | LOW | COSMETIC | Total |
|-----------|------|--------|-----|----------|-------|
| A | 4 | 15 | 6 | 1 | 26 |
| A2 | 4 | 17 | 7 | 1 | 29 |
| B | 3 | 6 | 7 | 1 | 17 |
| C | 2 | 4 | 5 | 1 | 12 |
| C2 | 1 | 6 | 6 | 1 | 14 |
| D | 3 | 10 | 4 | 1 | 18 |
| **Pass 2** | **17** | **58** | **35** | **6** | **116** |
