---
document_type: adversarial-review-index
phase: 1d
pass: 14
date: 2026-11-18
findings: 65
verdict: NOT_CLEAN
novelty: MEDIUM
---

# ADV-P14 Index — Phase 1d Adversarial Spec Review, Pass 14

Every finding from pass 14, indexed from `pass-14.md`. Severity totals: HIGH 3 / MEDIUM 25 / LOW 33 / COSMETIC 4 — total 65. Against pass 13 (72, 11 HIGH): total -7, HIGH -8.

## Findings

| ID | Sev | Category | File (first location) | Owner | Tags |
|----|-----|----------|-----------------------|-------|------|
| ADV-P14-A01 | HIGH | Interface cannot express a BC; P20 config over code | specs/architecture/ARCH-03-statusline.md:401, :378-384, :392-393 | architect |  |
| ADV-P14-A02 | MEDIUM | Interface type loses parity exactness (P13) | ARCH-03-statusline.md:413 | architect |  |
| ADV-P14-A03 | MEDIUM | CI census contradicts a BC (P11) | ARCH-08-build-ci-release.md:248-252 | architect |  |
| ADV-P14-A04 | MEDIUM | Positive-coverage granularity weaker than the gate unit (P11; partial-fix sibling) | cicd-setup.md:80, :87 | architect |  |
| ADV-P14-A05 | MEDIUM | Contradiction: required-check list vs activation rule (P19) | cicd-setup.md:327-336 (line 334), :52 | architect |  |
| ADV-P14-A06 | MEDIUM | NFR target omits catalogued degrade triggers (pending intent verification) | prd.md:500, :518 | product-owner |  |
| ADV-P14-A07 | MEDIUM | Partial-fix sibling: self-contradictory requirement | nfr-catalog.md:24 vs prd.md:499, :30 | product-owner |  |
| ADV-P14-A08 | MEDIUM | Positive-coverage count not derived from the tool's inputs (P11) | cicd-setup.md:84 | architect |  |
| ADV-P14-A09 | LOW | Count propagation after the R-009 mint | prd.md:677 | product-owner / architect |  |
| ADV-P14-A10 | LOW | Incomplete exit-1 cites | interface-definitions.md:64 | architect / product-owner |  |
| ADV-P14-A11 | LOW | Mis-anchored line pointer (P4) | ARCH-00-overview.md:21 | architect |  |
| ADV-P14-A12 | LOW | Timeout formula misses a term (P11 item 5) | ARCH-08:193 | architect |  |
| ADV-P14-A13 | LOW | Literal command contradicts its own cell | cicd-setup.md:59 | architect |  |
| ADV-P14-A14 | COSMETIC | Severity model drift | prd.md:528-534 vs error-taxonomy.md:60-65 | product-owner |  |
| ADV-P14-A2-01 | HIGH | Oracle that cannot be built; positive coverage is illusory (P11) | VP-012-exclusion-set-closure.md:87-100, 181-182, 188-190, 243-263 | architect |  |
| ADV-P14-A2-02 | MEDIUM | VP statement contradicts BC and legacy | VP-021-cost-colour-goldens.md:55-56 | architect |  |
| ADV-P14-A2-03 | MEDIUM | Wrong module anchor (P4); partial-fix sibling | VP-020:14, :100 (Proof Method "Go test, temp dirs"), :111-113 | architect |  |
| ADV-P14-A2-04 | LOW | Contradiction inside one document | VP-004-closed-exit-code-surface.md:88-89 | architect |  |
| ADV-P14-A2-05 | LOW | Partial fix not propagated | VP-016-config-error-classes-line.md:104-105, :121 | architect |  |
| ADV-P14-A2-06 | LOW | Ambiguous oracle wording; sibling of a pass-12 fix | VP-029-transcript-parse-tables.md:62-63 | architect |  |
| ADV-P14-A2-07 | LOW | Stale enforcer counts (P2) | domain-spec/invariants.md:46 (and the :31, :35 cells) | business-analyst |  |
| ADV-P14-A2-08 | LOW | Derived prose lags the catalog (P9) | VP-INDEX.md:41 | architect |  |
| ADV-P14-A2-09 | LOW | Assessment pin no longer holds | architecture-feasibility-report.md:13, :19, :22 | architect |  |
| ADV-P14-A2-10 | COSMETIC | Sketch contradicts statement | VP-034-oracle-isolation.md:150-151 | architect |  |
| ADV-P14-A2-11 | COSMETIC | Sketch incomplete | VP-014-d4ex1-windows-window-age.md:101-109 | architect |  |
| ADV-P14-B01 | MEDIUM | Semantic anchoring / VP reciprocity (P4/P5) | BC-1.01.008 VP table (only VP-005) and PC3 | product-owner (BC rows); architect (VP-012 `bcs:`) |  |
| ADV-P14-B02 | LOW | Anchor completeness (pending intent verification) | VP-001:37, 82-99 (Source Contract) | product-owner; architect |  |
| ADV-P14-B03 | LOW | Unreachable degrade site | BC-1.01.009 PC1 step 6 row ("foreign-cache CP-C01 only (non-dict cache at SL:273-275)") | product-owner; architect (taxonomy row) |  |
| ADV-P14-B04 | LOW | Missing edge case | BC-1.02.013 PC1 ("missing/corrupt → `{}`") and its EC table | product-owner |  |
| ADV-P14-B05 | LOW | Ambiguous vector setup | BC-1.02.029 CP-O12 seed (`"transcript_path":"<T>"` and `"workspace":{"project_dir":"<T>"}`) | product-owner |  |
| ADV-P14-B06 | LOW | D15 named-constant declaration gap [process-gap] | BC-1.02.011 PC5 (two-space window joiner, SL:532) | product-owner | process-gap |
| ADV-P14-B07 | LOW | Wording gap vs. a sibling contract | BC-1.01.001 PC3 | product-owner |  |
| ADV-P14-B08 | LOW | Stale anchor label | interface-definitions:331 (Contract column of the `statusline.glyphs.*` family row) | architect |  |
| ADV-P14-B09 | COSMETIC | Stale count | BC-1.02.004 VP-028 row ("the 10-layout table") | product-owner |  |
| ADV-P14-C01 | MEDIUM | Internal contradiction (test-misleading) | BC-1.03.005.md:98 (EC-008) vs :114 (CP-O09 parse-leg CTV) | product-owner |  |
| ADV-P14-C02 | MEDIUM | Partial-fix regression (sibling not updated after ADV-P10-C01) | BC-1.03.018.md:103 (PC3 CP-O07 row) vs BC-1.03.007.md:78 (EC-007), :98-100 | product-owner |  |
| ADV-P14-C03 | LOW | Same imprecision as C01 | BC-1.03.006.md:99 (EC-009) | product-owner |  |
| ADV-P14-C04 | LOW | Raise site cited incompletely | BC-1.03.002.md:86 (EC-007, CP-C26) | product-owner |  |
| ADV-P14-C05 | LOW | Body inconsistency | BC-1.07.002.md:173 (Purity "I/O operations: none") vs :63-67 (PC2), :78 (PC5) | product-owner |  |
| ADV-P14-C2-01 | MEDIUM | Incomplete OD-160 sibling sweep (partial fix of ADV-P13-C2-01) | BC-1.04.004.md:83-90 | product-owner | process-gap |
| ADV-P14-C2-02 | MEDIUM | Missing crash family / contradicts PC1 | BC-1.04.004.md:81-84 | n\ |  |
| ADV-P14-C2-03 | MEDIUM | P20 config-over-code; ARCH contradicts BC | ARCH-03-statusline.md:378-384, 392-393, 401 vs BC-1.05.004.md:63, 79 | architect |  |
| ADV-P14-C2-04 | MEDIUM | Mis-anchor: symbols that do not exist (pass-13 respell incomplete) | BC-1.05.004.md:161 vs :213 | product-owner |  |
| ADV-P14-C2-05 | MEDIUM | Purity residue contradicts ARCH-00/ARCH-03 | BC-1.05.004.md:209-211 | product-owner |  |
| ADV-P14-C2-06 | LOW | Mis-citation | ARCH-03-statusline.md:352, 373 | architect |  |
| ADV-P14-C2-07 | LOW | Lossy declared type | ARCH-03-statusline.md:413 | architect |  |
| ADV-P14-C2-08 | LOW | Non-monotonic `modified` lists [process-gap] | BC-1.04.003.md:26 | product-owner | process-gap |
| ADV-P14-C2-09 | LOW | Ambiguous framing grammar | BC-1.04.001.md:144-146 | product-owner |  |
| ADV-P14-C2-10 | LOW | P16/P20 sibling note gap (pending intent verification) | BC-1.04.012.md:61 | product-owner |  |
| ADV-P14-D01 | HIGH | partial-fix propagation / missing reason | BC-2.01.004:170-172, :231-235 vs :293-320 | product-owner |  |
| ADV-P14-D02 | MEDIUM | contradiction | BC-2.01.001:75-78 vs BC-2.01.005:242-249 | product-owner |  |
| ADV-P14-D03 | MEDIUM | contradiction (reason precedence) | BC-2.02.003:68-70, :85 vs BC-2.02.001:189-196 | product-owner |  |
| ADV-P14-D04 | MEDIUM | ambiguous error bytes | BC-2.03.002:108-121, :84-90, :125-129 | product-owner |  |
| ADV-P14-D05 | MEDIUM | cross-platform gap (P18) | BC-6.03.001:145-159, :163-168 | architect |  |
| ADV-P14-D06 | MEDIUM | unsatisfiable check [owner-question, pending intent verification] | BC-6.03.004:153-158 | product-owner |  |
| ADV-P14-D07 | MEDIUM | underspecified representation | BC-2.01.005:206-225 | product-owner |  |
| ADV-P14-D08 | MEDIUM | mis-anchor (P4) | BC-2.01.004:302-304, :39 | product-owner |  |
| ADV-P14-D09 | MEDIUM | signature contradiction | BC-4.01.001:52-59 vs ARCH-01-binary-cli.md:46-55, :62-73 | product-owner |  |
| ADV-P14-D10 | LOW | legacy line mis-cite | BC-6.03.003:86, :188 | product-owner |  |
| ADV-P14-D11 | LOW | stale term | BC-6.02.003:181-182 | product-owner |  |
| ADV-P14-D12 | LOW | stale sibling text | BC-6.02.001:157, :138 | product-owner |  |
| ADV-P14-D13 | LOW | asymmetry | BC-6.01.003:72-83, :91-94, :116-118, EC-003 :187 | product-owner |  |
| ADV-P14-D14 | LOW | threshold rationale (P16) | BC-5.01.004:51-55 | product-owner |  |
| ADV-P14-D15 | LOW | purity mislabel | BC-3.01.001:202-206 vs :84-113 | product-owner |  |
| ADV-P14-D16 | LOW | CI wording | BC-6.04.001:101-104 | architect |  |
