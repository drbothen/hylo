---
document_type: adversarial-review-index
phase: 1d
pass: 12
date: 2026-11-18
findings: 73
verdict: NOT_CONVERGED
novelty: MEDIUM
---

# ADV-P12 Index — Phase 1d Adversarial Spec Review, Pass 12

Every finding from pass 12, indexed from `pass-12.md`. Severity totals: HIGH 13 / MEDIUM 26 / LOW 28 / COSMETIC 6 — total 73. Against pass 11 (62, 11 HIGH): total +11, HIGH +2.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P12-A01 | HIGH | Contradiction / semantic anchoring (P4) | prd.md:513 | product-owner | process-gap |
| ADV-P12-A02 | HIGH | CI-as-code / security (P11, P14) | ARCH-08:176-180, :225-234 | architect |  |
| ADV-P12-A03 | HIGH | BC title sync (P7) | prd.md:426 | product-owner |  |
| ADV-P12-A04 | HIGH | Architecture cannot satisfy a BC | ARCH-08:50-63 | architect |  |
| ADV-P12-A05 | MEDIUM | Partial-fix sibling drift | prd.md:499 vs nfr-catalog.md:27 | product-owner |  |
| ADV-P12-A06 | HIGH | Contradiction (architecture vs BC) | ARCH-08:54-57, :73-77 | architect + product-owner |  |
| ADV-P12-A07 | HIGH | NFR without an unambiguous measurement unit | nfr-catalog.md:24, :73-78 | architect + product-owner | owner-question |
| ADV-P12-A08 | MEDIUM | CI-as-code (P11) | ARCH-07:198 | architect |  |
| ADV-P12-A09 | MEDIUM | Partial-fix sibling drift | nfr-catalog.md:26 | product-owner |  |
| ADV-P12-A10 | LOW | Ambiguity | interface-definitions.md:44-48, :477 | architect |  |
| ADV-P12-A11 | LOW | Misclassification / range | prd.md:500 | product-owner |  |
| ADV-P12-A12 | COSMETIC | Terminology drift | ARCH-00:102-104 | architect |  |
| ADV-P12-A2-01 | MEDIUM | Count drift (P2) | domain-spec/invariants.md:31, :35, :46 | business-analyst |  |
| ADV-P12-A2-02 | MEDIUM | Contradiction / mis-anchor | VP-019:43-45 vs VP-014:44-51 | architect |  |
| ADV-P12-A2-03 | MEDIUM | Under-specified oracle | VP-012:84-93, sketch :214-226 | architect |  |
| ADV-P12-A2-04 | MEDIUM | VP narrower than its primary BC | VP-011:38-41 | architect |  |
| ADV-P12-A2-05 | MEDIUM | Clause with no oracle | VP-007:39-41, :71-76 | architect |  |
| ADV-P12-A2-06 | MEDIUM | Under-defined membership oracle | VP-001:113-117 | architect |  |
| ADV-P12-A2-07 | MEDIUM | Untested normative clause | VP-034:55-66 vs :101-104, :112, :224-225 | architect |  |
| ADV-P12-A2-08 | MEDIUM | P11 positive coverage | VP-006:99-100, :130, sketch :173-177 | architect |  |
| ADV-P12-A2-09 | MEDIUM | L2 phase vs P1 scope | domain-spec/bounded-contexts.md:35 | business-analyst |  |
| ADV-P12-A2-10 | LOW | Brief vs BC wording | product-brief.md:89-90 vs BC-6.04.002:102-106, VP-036:48-49 | product-owner |  |
| ADV-P12-A2-11 | LOW | Stale label | VP-036:60-61 | architect |  |
| ADV-P12-A2-12 | LOW | Title vs statement (pending intent) | VP-039:33, VP-INDEX:116 vs VP-039:44-46 | architect |  |
| ADV-P12-A2-13 | LOW | Stale assessment pin (pending intent) | architecture-feasibility-report.md:13, :21 | architect |  |
| ADV-P12-A2-14 | LOW | Wrong attribution | VP-005:56-58 | architect |  |
| ADV-P12-A2-15 | LOW | Registry discipline (P20) | VP-031:50-51, :149-150 | architect |  |
| ADV-P12-A2-16 | LOW | Ambiguous oracle | VP-013:56-58 vs VP-029:66-68 | architect |  |
| ADV-P12-A2-17 | LOW | Tautological norm | VP-016:50-51 | architect |  |
| ADV-P12-A2-18 | LOW | Public-artifact hygiene (P21) | VP-035:105 | product-owner | owner-question |
| ADV-P12-A2-19 | COSMETIC | Sketch only | VP-021:131-137 | architect |  |
| ADV-P12-B01 | MEDIUM | Missing exclusion tag / crash path not in the register | BC-1.02.018:96 (EC-009), :111 (vector `tin "x"`) | product-owner; architect (taxonomy) |  |
| ADV-P12-B02 | MEDIUM | Anchors point at the wrong file `[process-gap]` | BC-1.01.002:143, BC-1.01.008:142, BC-1.01.003:140, BC-1.01.009:174 | architect; product-owner | process-gap |
| ADV-P12-B03 | LOW | Property false for one input | BC-1.02.010:64 (Inv 1), :102 (VP-041 row) | product-owner; architect |  |
| ADV-P12-B04 | LOW | Contradiction between two BCs | BC-1.02.008:60 (Inv 2) vs BC-1.02.023:55, :70 | product-owner |  |
| ADV-P12-B05 | LOW | Incomplete enumeration | BC-1.01.006:66-74 (Inv 1(b)) | product-owner; architect |  |
| ADV-P12-B06 | LOW | Sibling docs out of sync | ARCH-03:85 (step 7b), :79 (step 2) vs BC-1.01.009:66, :72 and BC-1.01.001:66-67 | architect |  |
| ADV-P12-B07 | COSMETIC | Wording contradicts itself | BC-1.02.028:73 (EC-004) | product-owner |  |
| ADV-P12-B08 | COSMETIC | History entries out of order | BC-1.01.001:31-32 (1.4.2 listed before 1.4.1) | product-owner |  |
| ADV-P12-C01 | HIGH | Contradiction (interface vs BC) | prd-supplements/interface-definitions.md:134-141 vs BC-1.07.008.md:61-76 | product-owner |  |
| ADV-P12-C02 | MEDIUM | Spec drift (quirk overgeneralized) | BC-1.07.007.md:48, :79-81 (PC6), :82-83 (PC7) | n\ |  |
| ADV-P12-C03 | MEDIUM | Partial-fix regression | BC-1.07.002.md:66-70 (PC5), :78-80 (Inv 3), :89 (EC-004) vs interface-definitions.md:49-51, :138-139 | product-owner |  |
| ADV-P12-C04 | LOW | Mis-anchor (label) | prd.md:665 | product-owner |  |
| ADV-P12-C05 | LOW | Mis-anchor (range owner) | BC-1.07.004.md:85-86 (PC7) | product-owner |  |
| ADV-P12-C06 | LOW | Thresholds rationale (P16) | BC-1.07.007.md:46-47 | product-owner |  |
| ADV-P12-C07 | LOW | Ambiguity | BC-1.07.004.md:63-65 (PC3) | product-owner |  |
| ADV-P12-C08 | LOW | Public-repo hygiene (P14) | BC-1.07.004.md:78 | product-owner | owner-question |
| ADV-P12-C09 | COSMETIC | Arithmetic | BC-1.07.004.md:119 | product-owner |  |
| ADV-P12-C2-01 | MEDIUM | Wrong legacy semantics | BC-1.04.009:55-56 (Pre 1), :116 (EC-011) | product-owner |  |
| ADV-P12-C2-02 | HIGH | Partial-fix sibling gap (2 files) | BC-1.04.009:129-132 | product-owner |  |
| ADV-P12-C2-03 | MEDIUM | Spec gap / false universal claim | BC-1.04.001:214-217 (PC1), :256 (Go step list) | product-owner |  |
| ADV-P12-C2-04 | MEDIUM | Anchor/count drift after a pass-11 fix | BC-1.04.003:131 (VP row) | product-owner |  |
| ADV-P12-C2-05 | MEDIUM | P20 literal contradicts a sibling under allowed config | BC-1.04.002:69 (PC3 `hist[-32:]`) | product-owner |  |
| ADV-P12-C2-06 | LOW | Incomplete exhaustive invariant | BC-1.04.004:73-77 (Inv 3) | product-owner |  |
| ADV-P12-C2-07 | LOW | Sibling asymmetry (pending intent verification) | BC-1.05.001:50-52 (Pre 1), :72 (PC2), :127 (L2 row) | product-owner |  |
| ADV-P12-C2-08 | LOW | P20 named-constant note missing | BC-1.04.002:64, :86, :118 | architect |  |
| ADV-P12-C2-09 | COSMETIC | Changelog order | BC-1.05.005:37-38 | product-owner |  |
| ADV-P12-D01 | HIGH | Contradiction (partial-fix propagation) | BC-3.02.001:104-113, :126 | product-owner |  |
| ADV-P12-D02 | HIGH | Spec cannot be implemented / hermeticity (P18) | BC-6.01.002:126-136, :141-155 | architect |  |
| ADV-P12-D03 | HIGH | Inert regression detector (CI positive coverage) [process-gap] | BC-6.01.003:62-66 vs :141-143, :150-158 | architect | process-gap |
| ADV-P12-D04 | HIGH | Public-repo hygiene gap (P14), CI-as-code [owner-question] | BC-6.04.001:56-57, :102-107, :151 | architect | owner-question |
| ADV-P12-D05 | HIGH | Title sync (P7) | prd.md:426 vs BC-6.04.001:43 and BC-INDEX:318 | product-owner |  |
| ADV-P12-D06 | MEDIUM | Ambiguity, no failing test can be written | BC-2.01.005:73-81, :169-180 | product-owner |  |
| ADV-P12-D07 | MEDIUM | Contradiction (per-OS, P18) | BC-3.01.001:68-73, :142 vs BC-2.01.005:91-96 | product-owner |  |
| ADV-P12-D08 | MEDIUM | Per-OS behavior not specified (P18) | BC-2.01.001:111-122 | architect |  |
| ADV-P12-D09 | MEDIUM | Sibling not updated / anchoring | BC-2.02.005:49-50, :54-55 vs BC-2.01.002:95-101 | product-owner |  |
| ADV-P12-D10 | MEDIUM | Wrong expected value | BC-5.03.004:89 vs :56-63 | product-owner |  |
| ADV-P12-D11 | MEDIUM | CI positive coverage | BC-6.04.003:110-112, :124-127, :150 | architect |  |
| ADV-P12-D12 | LOW | Spec choice not carried through | BC-2.01.005:85-91 vs BC-2.03.002:90-91, BC-3.01.001:75-77 | product-owner |  |
| ADV-P12-D13 | LOW | Stale claim | BC-6.03.003:80-82 | product-owner |  |
| ADV-P12-D14 | LOW | Composition under-specified | BC-5.02.002:50-53 vs BC-5.02.001:92-106, ARCH-06:69-77 | product-owner |  |
| ADV-P12-D15 | LOW | Ambiguity | BC-6.04.001:92-101 | architect |  |
| ADV-P12-D16 | LOW | Stale traceability | BC-6.04.001:151 | product-owner |  |
