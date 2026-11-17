---
document_type: adversarial-review-index
phase: 1d
pass: 1
date: 2026-11-17
findings: 129
verdict: NOT_CONVERGED
novelty: HIGH
---

# ADV-P1 Index — Phase 1d Adversarial Spec Review, Pass 1

Every finding from pass 1, indexed from the verbatim perimeter reports in `pass-1.md`. Severity totals: HIGH 21, MEDIUM 63, LOW 40, COSMETIC 5 — total 129.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P1-A01 | HIGH | parity / invented cap (P13, P16) | prd-supplements/nfr-catalog.md:28 | product-owner + architect |  |
| ADV-P1-A02 | HIGH | contradiction / closed set | prd-supplements/error-taxonomy.md:28,61 | product-owner |  |
| ADV-P1-A03 | MEDIUM | contradiction | prd.md:615-617 | architect |  |
| ADV-P1-A04 | HIGH | partial-fix regression / ruling drift | behavioral-contracts/ss-06/BC-6.04.003.md:36,40,128 | product-owner |  |
| ADV-P1-A05 | MEDIUM | id mismatch in fail-closed machinery | architecture/ARCH-07-parity-harness.md:42 | architect |  |
| ADV-P1-A06 | HIGH | VP catalog coverage drift (P9) | verification-properties/VP-INDEX.md:121-214 | architect |  |
| ADV-P1-A07 | MEDIUM | toolchain (P19) | VP-005/007/012/015/023/024/025 line 15 | architect |  |
| ADV-P1-A08 | MEDIUM | ambiguous NFR | prd.md:124-125 | product-owner [owner-question] | owner-question |
| ADV-P1-A09 | HIGH | CI false-green risk (P11) | cicd-setup.md:45-56, 62-67, 110-113 | architect / devops [process-gap] | process-gap |
| ADV-P1-A10 | MEDIUM | vacuous verification / weak anchor (P4, P5) | VP-022-ledger-read-scope-absence.md:37-40, 57-61, 74-89 | architect |  |
| ADV-P1-A11 | MEDIUM | ambiguity / interface cannot express the spec | VP-006-json-depth-budgets.md:37-38, 53, 70 | architect |  |
| ADV-P1-A12 | MEDIUM | contradiction | prd-supplements/interface-definitions.md:67 | product-owner |  |
| ADV-P1-A13 | HIGH | subsystem name drift (P6) | prd.md:109-120 | product-owner |  |
| ADV-P1-A14 | LOW | stale text | prd.md:40-42, 48-49, 103 | product-owner |  |
| ADV-P1-A15 | MEDIUM | invariant orphans (P2) | domain-spec/invariants.md:22-44 | business-analyst |  |
| ADV-P1-A16 | MEDIUM | architecture gap | ARCH-00-overview.md:46-62, 73 | architect |  |
| ADV-P1-A17 | LOW | NFR ambiguity | prd.md:452 | product-owner |  |
| ADV-P1-A18 | LOW | unexplained constants (P16, P20) | ARCH-05-platform.md:26, 28 | architect |  |
| ADV-P1-A19 | LOW | ambiguous wording | prd.md:478 | product-owner |  |
| ADV-P1-A20 | LOW | anchor drift | BC-COMPONENT-MAP.md:31, 37, 117 | architect |  |
| ADV-P1-A21 | LOW | untestable reason | ARCH-02:66-68 | architect |  |
| ADV-P1-A2-01 | HIGH | Contradiction / settled decision vs parity | state-machines.md:66-71 | product-owner | owner-question |
| ADV-P1-A2-02 | HIGH | Contradiction with BC and legacy | state-machines.md:67 ("NaN samples are dropped") | architect |  |
| ADV-P1-A2-03 | HIGH | VP oracle contradicts its BC (P13) | VP-020:37-45,81-82 | architect |  |
| ADV-P1-A2-04 | HIGH | VP statement contradicts BCs | VP-004:37-41 | architect |  |
| ADV-P1-A2-05 | HIGH | Wrong oracle: the test would fail a correct implementation | VP-002:32,36,68-71 | architect |  |
| ADV-P1-A2-06 | HIGH | P9: VP files disagree with the VP-INDEX coverage map | VP-007:13 (BC-5.04.003) | architect |  |
| ADV-P1-A2-07 | MEDIUM | Missing edge case | VP-001:37-41,72 | architect |  |
| ADV-P1-A2-08 | MEDIUM | Unreachable case | VP-017:36-38,68-71 | architect |  |
| ADV-P1-A2-09 | MEDIUM | Assertion can never fail | VP-034:75 | architect |  |
| ADV-P1-A2-10 | MEDIUM | Assertion can never fail | VP-033:76 | architect |  |
| ADV-P1-A2-11 | MEDIUM | Wrong tool usage | VP-024:77-78 | architect |  |
| ADV-P1-A2-12 | MEDIUM | Oracle gaps and off-by-one | VP-012:38,42-43,81 | architect |  |
| ADV-P1-A2-13 | MEDIUM | Fix not propagated to sibling files (≥2 files) | VP-012:93, ARCH-07:85 | product-owner |  |
| ADV-P1-A2-14 | MEDIUM | Contradiction about who writes the Windows goldens | VP-010:36-38 | architect |  |
| ADV-P1-A2-15 | MEDIUM | Unexplained threshold; config over code (P16, P20) | VP-018:41-42 | architect |  |
| ADV-P1-A2-16 | MEDIUM | Risk mitigation does not hold | risk-register.md:31 (R-007) | architect |  |
| ADV-P1-A2-17 | MEDIUM | Settled decision misstated (P12) | bounded-contexts.md:42-43 | business-analyst |  |
| ADV-P1-A2-18 | MEDIUM | Stale strategy text contradicts rulings (P12) | gene-transfusion-assessment.md:54, :116 | architect |  |
| ADV-P1-A2-19 | MEDIUM | L2 contradicts the architecture without a deferral | capabilities.md:31 (CAP-009 "Pure function of stdin + transcript + metrics + caches") | business-analyst |  |
| ADV-P1-A2-20 | MEDIUM | Ordering ambiguity | state-machines.md:56-60 (SM-04) | business-analyst |  |
| ADV-P1-A2-21 | MEDIUM | Wrong anchors | dtu-assessment.md:107 ("CP-N02 happy path") | architect |  |
| ADV-P1-A2-22 | LOW | Glossary does not match the bytes | ubiquitous-language.md:39,46 | business-analyst |  |
| ADV-P1-A2-23 | LOW | P1 slice incomplete | L2-INDEX.md:110-111 | business-analyst |  |
| ADV-P1-A2-24 | LOW | Measurement ambiguity | VP-036:38-39 | architect |  |
| ADV-P1-A2-25 | LOW | Rust terminology (P19) [process-gap] | VP-005/007/012/015/023/024/025 frontmatter `proof_method: proptest` | architect | process-gap |
| ADV-P1-A2-26 | LOW | Subsystem name not verbatim (P6) | architecture-feasibility-report.md:46,51 | architect |  |
| ADV-P1-A2-27 | LOW | Literal invisible character | test-vectors.md:42 | product-owner |  |
| ADV-P1-A2-28 | COSMETIC | Typos and arithmetic | gene-transfusion-assessment.md:34 ("Sub Setsystem Registry") | business-analyst |  |
| ADV-P1-B01 | MEDIUM | contradiction / error coverage | BC-1.01.009.md:55,56,58,61 | product-owner | owner-question |
| ADV-P1-B02 | MEDIUM | contradiction (arch vs BC) | ARCH-03-statusline.md:49 | architect |  |
| ADV-P1-B03 | MEDIUM | postcondition not true of legacy | BC-1.01.003.md:54,58 (also interface-definitions.md:63, VP-027 line-count property) | product-owner |  |
| ADV-P1-B04 | MEDIUM | incomplete precondition | BC-1.02.021.md:79 | product-owner |  |
| ADV-P1-B05 | MEDIUM | invariant false vs legacy | BC-1.02.025.md:55,111 | product-owner |  |
| ADV-P1-B06 | MEDIUM | spec gap [owner-question] | BC-1.02.026.md:45, BC-1.02.014.md:54-60 | product-owner | owner-question |
| ADV-P1-B07 | MEDIUM | Policy 16 inconsistency | BC-1.01.003.md:63 | product-owner |  |
| ADV-P1-B08 | MEDIUM | cross-platform parity gap | BC-1.02.004.md:47-48,90,119 | architect |  |
| ADV-P1-B09 | MEDIUM | semantic mis-anchor | prd.md:510, 511, 512 | product-owner |  |
| ADV-P1-B10 | MEDIUM | Policy 20: config key, undefined behavior | BC-1.02.006.md:47-49,55-58,131 | product-owner / architect |  |
| ADV-P1-B11 | MEDIUM | VP mis-anchor | BC-1.01.008.md:99 | architect |  |
| ADV-P1-B12 | LOW | internal contradiction | BC-1.01.010.md:73 | product-owner |  |
| ADV-P1-B13 | LOW | legacy site misstatement | BC-1.02.019.md:70 | product-owner |  |
| ADV-P1-B14 | LOW | incomplete edge case | BC-1.02.013.md:86 | product-owner |  |
| ADV-P1-B15 | LOW | Policy 19 [process-gap] | "proptest" in BC-1.01.001:98, .003:102, .004:85, .006:95-96, .007:87, .008:100, BC-1.02.016:101, .018:106, .019:95, .023:97 | product-owner | process-gap |
| ADV-P1-B16 | LOW | vector under-specified | BC-1.01.001.md:89, BC-1.01.008.md:87, BC-1.01.009.md:96 | product-owner |  |
| ADV-P1-B17 | LOW | measurement fragility (pending verification) | BC-1.01.002.md:77-79 | architect | pending verification |
| ADV-P1-B18 | LOW | inconsistency (pending intent verification) | BC-1.01.001.md:76, BC-1.01.009.md:85 | product-owner | pending intent verification |
| ADV-P1-B19 | LOW | Policy 21 | BC-1.02.005.md:50 | product-owner |  |
| ADV-P1-B20 | LOW | incomplete list | BC-1.01.008.md:53-55 | product-owner |  |
| ADV-P1-C01 | HIGH | Missing crash path / spec contradiction | BC-1.03.006.md:53-55 | product-owner | owner-question |
| ADV-P1-C02 | MEDIUM | Postcondition vs legacy mismatch | BC-1.03.003.md:66 (Inv 3), :75 (EC-004), :96 (VP row "size ≤ the stat size") | product-owner |  |
| ADV-P1-C03 | MEDIUM | VP anchor drift (index ↔ body) | BC-1.03.018.md:110-111, BC-1.03.019.md:120-121, BC-1.03.020.md:104-105 (VP-012) | architect |  |
| ADV-P1-C04 | MEDIUM | Semantic mis-anchoring (Policy 4/5) | BC-1.03.004.md:105-107 | architect |  |
| ADV-P1-C05 | MEDIUM | Config-over-code registry gap (Policy 20) | BC-1.03.003.md:45, BC-1.03.005.md:47, BC-1.03.007.md:44, BC-1.03.009.md:45, BC-1.03.010.md:49-52 | architect |  |
| ADV-P1-C06 | LOW | Unstated assumption | BC-1.06.001.md:62 | product-owner |  |
| ADV-P1-C07 | LOW | Ambiguity | BC-1.03.020.md:45, :104 | product-owner |  |
| ADV-P1-C08 | COSMETIC | Frontmatter consistency | all BC-1.04.*/1.05.*/1.06.* line 13-22 `extracted_from` | product-owner |  |
| ADV-P1-C2-01 | HIGH | wrong bytes in test vector | BC-1.05.009:92, :108 | product-owner |  |
| ADV-P1-C2-02 | HIGH | contradiction between BCs | BC-1.05.006:74-75 (PC5), :111 (VP-020 row) | product-owner |  |
| ADV-P1-C2-03 | MEDIUM | parity gap (redirects) | BC-1.04.001:51, :57, :76 | product-owner |  |
| ADV-P1-C2-04 | MEDIUM | quirk misstated | BC-1.04.005:71 (EC-007), BC-1.04.001:98 (EC-013) | product-owner |  |
| ADV-P1-C2-05 | MEDIUM | description and VP contradict postcondition | BC-1.04.009:34-35, :100 | product-owner |  |
| ADV-P1-C2-06 | MEDIUM | dangling anchors (P4), pattern across 29 files [process-gap] | e.g. BC-1.04.001:144 `#metrics-client`, BC-1.04.002:129 `#session-cache`, BC-1.04.004:115 `#row-2`, BC-1.05.001:145 `#cost-segment`, BC-1.05.007:121 `#num`, BC-1.06.002:131 `ARCH-04#cache-store` | architect | process-gap |
| ADV-P1-C2-07 | MEDIUM | mechanical VP citation (P4/P5) | BC-1.04.001:117-119 | product-owner |  |
| ADV-P1-C2-08 | MEDIUM | missing invariant (P2) | BC-1.05.006:119, BC-1.05.009:124, BC-1.06.002:113 | product-owner |  |
| ADV-P1-C2-09 | MEDIUM | internal contradiction | BC-1.05.005:151, :154 | architect |  |
| ADV-P1-C2-10 | LOW | postcondition wording | BC-1.04.013:50-51 | product-owner |  |
| ADV-P1-C2-11 | LOW | overbroad invariants | BC-1.04.016:60 | product-owner |  |
| ADV-P1-C2-12 | LOW | threshold codes conflict between docs (P16) | interface-definitions.md:100 | product-owner |  |
| ADV-P1-C2-13 | LOW | missing or conflicting rationale labels (P16) | BC-1.04.012:46 (T-108) | product-owner |  |
| ADV-P1-C2-14 | LOW | config key does not match formula (P20) | BC-1.04.007:42 | product-owner |  |
| ADV-P1-C2-15 | LOW | edge case cannot be tested as written | BC-1.04.009:80 (EC-005) | product-owner |  |
| ADV-P1-C2-16 | LOW | ambiguity | BC-1.05.006:60-62 | product-owner |  |
| ADV-P1-C2-17 | LOW | mechanical invariant citation (P5) | BC-1.04.017:96, BC-1.04.019:89, BC-1.04.020:114, BC-1.04.021:88 | product-owner |  |
| ADV-P1-C2-18 | LOW | frontmatter and template drift [process-gap] | BC-1.05.001:19, BC-1.05.003:20, BC-1.05.005:20, BC-1.06.002:18 (and siblings) | product-owner | process-gap |
| ADV-P1-C2-19 | COSMETIC | template vocabulary [process-gap] | BC-1.04.003:155, BC-1.04.004:148, BC-1.05.005:154, BC-1.05.009:160, etc. | product-owner | process-gap |
| ADV-P1-D01 | HIGH | Python parity / self-contradiction | BC-5.01.005.md:58, :80 | product-owner |  |
| ADV-P1-D02 | HIGH | Python parity / wrong vectors | BC-5.01.006.md:72, :73, :75, :84 | product-owner |  |
| ADV-P1-D03 | HIGH | Settled decision contradicted (P12) | BC-6.04.003.md:36 (H1), :50-51, :86-89 | product-owner |  |
| ADV-P1-D04 | MEDIUM | Contradiction with OD-01 / BC-2.01.001 | BC-3.02.001.md:76-77 | product-owner |  |
| ADV-P1-D05 | MEDIUM | Cross-BC contradiction (harness) | BC-6.01.002.md:62, :102-103 | product-owner |  |
| ADV-P1-D06 | HIGH | Interface mismatch BC ↔ ARCH-06 | ARCH-06-pyfmt.md:62, :66-69, :72, :91 | architect |  |
| ADV-P1-D07 | HIGH | Mis-anchoring (P4/P6) | BC-6.01.002.md:162 | product-owner |  |
| ADV-P1-D08 | MEDIUM | Internal inconsistency | BC-2.02.006.md:46, :69, :100 | product-owner |  |
| ADV-P1-D09 | HIGH | Partial-fix propagation (OD-140) | BC-2.02.001.md:51, :100, :170-172 | product-owner |  |
| ADV-P1-D10 | MEDIUM | Contradiction BC ↔ interface-definitions | interface-definitions.md:90 | product-owner |  |
| ADV-P1-D11 | MEDIUM | Contradiction BC ↔ interface-definitions | interface-definitions.md:67, :102 | product-owner |  |
| ADV-P1-D12 | MEDIUM | Underspecified error line | BC-2.01.002.md:66-71 | product-owner |  |
| ADV-P1-D13 | MEDIUM | Inconsistent vector | BC-2.03.002.md:92 | product-owner |  |
| ADV-P1-D14 | MEDIUM | Boundary not pinned | BC-5.02.003.md:64-71, :94 | product-owner |  |
| ADV-P1-D15 | MEDIUM | Python formatting edge underspecified | BC-5.02.005.md:52-53 | product-owner |  |
| ADV-P1-D16 | MEDIUM | Harness fail-open | BC-6.03.003.md:70-73, :100-101 | product-owner |  |
| ADV-P1-D17 | MEDIUM | Harness machinery underspecified | BC-6.03.004.md:55-61, :86-88, :91-94, :125 | product-owner |  |
| ADV-P1-D18 | MEDIUM | Missing input spec (harness) | BC-6.02.002.md:49-56 | product-owner |  |
| ADV-P1-D19 | MEDIUM | Public hygiene gate gap (P14) | BC-6.02.001.md:70-78 | product-owner |  |
| ADV-P1-D20 | MEDIUM | Rust tooling in a Go spec (P19) [process-gap] | e.g. BC-2.01.001.md:113, :155 | product-owner | process-gap |
| ADV-P1-D21 | MEDIUM | OS-specific logic outside internal/platform (P18) | BC-2.01.005.md:62-64, :114 | architect |  |
| ADV-P1-D22 | MEDIUM | Product behavior unspecified | BC-6.01.003.md:78-81 | product-owner |  |
| ADV-P1-D23 | LOW | Legacy citation (P13) | BC-6.01.002.md:73-75 | product-owner |  |
| ADV-P1-D24 | MEDIUM | Mis-anchor (non-existent key) | BC-6.02.003.md:136 | product-owner |  |
| ADV-P1-D25 | LOW | Cross-BC semantics | BC-2.01.005.md:67-68 | product-owner |  |
| ADV-P1-D26 | LOW | Vectors not byte-exact | BC-5.02.004.md:73-74 | product-owner |  |
| ADV-P1-D27 | COSMETIC | Table broken | BC-5.01.002.md:84, :88 | product-owner |  |
| ADV-P1-D28 | COSMETIC | Wrong annotation | BC-5.01.005.md:77 | product-owner |  |
| ADV-P1-D29 | LOW | Unexplained thresholds (P16) | BC-5.01.004.md:46 | product-owner |  |
| ADV-P1-D30 | LOW | Traceability incomplete (P5) | BC-5.04.003.md:93-98 | product-owner |  |
| ADV-P1-D31 | LOW | Wrong call-site claim | BC-5.03.004.md:86 | product-owner |  |
| ADV-P1-D32 | LOW | Wrong claim | BC-3.02.001.md:65-66 | product-owner |  |
| ADV-P1-D33 | LOW | Class count drift (pending intent verification) | BC-2.02.006.md:36 | product-owner | pending intent verification |

## Totals by perimeter

| Perimeter | HIGH | MEDIUM | LOW | COSMETIC | Total |
|-----------|------|--------|-----|----------|-------|
| A | 6 | 9 | 6 | 0 | 21 |
| A2 | 6 | 15 | 6 | 1 | 28 |
| B | 0 | 11 | 9 | 0 | 20 |
| C | 1 | 4 | 2 | 1 | 8 |
| C2 | 2 | 7 | 9 | 1 | 19 |
| D | 6 | 17 | 8 | 2 | 33 |
| **Pass 1** | **21** | **63** | **40** | **5** | **129** |
