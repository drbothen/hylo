---
document_type: consistency-report
level: ops
version: "1.0"
producer: consistency-validator
timestamp: 2026-11-17T21:54:28Z
phase: 1d
status: FAIL
inputs: [prd.md, product-brief.md, domain-spec/, prd-supplements/, behavioral-contracts/, architecture/, verification-properties/, behavioral-contracts/BC-ALLOCATION.md, cicd-setup.md]
input-hash: "cf848a2"
cycle: phase-1-spec-crystallization
step: adversarial-review 4b (cross-document sync check after pass-2 fix burst)
baseline_commit: 47e1a86
traces_to: ../../STATE.md
---

# Sync Check — ADV-P2 step 4b (2026-11-18)

## Report Metadata

- Baseline `47e1a86` (adversarial pass-2 findings commit); the pass-2 **fix burst** is the
  uncommitted working tree: 142 changed paths, 132 files vs baseline (diff-stat digest
  `9175e7c`). Checked against the full spec corpus; read-only; no artifacts modified.
- Method: scripted cross-checks (title quad-match, config-key registry sweep, value
  sweeps) + targeted reads. Owner rulings in force: OD-155..159 recorded;
  OD-160..165 checked by their stated effect (recorded at commit).

## Summary

| Check | Result |
|---|---|
| OD-155 `--subagent` P1 port (BC-1.07.001..008, flag validity, off switch) | SYNCED except product-brief remnant (SC-01) |
| OD-156 overflow ids CP-O01..O09 | SYNCED (no live CP-T08; CP-O01..O09 all registered and cited; changelog `modified:` history rows only) |
| OD-157 OD-130 from P6 only | SYNCED (prd-side, dtu-assessment:110,121, VP-030:53, BC-1.04.016:104, state-machines:72 — uniform "P6/post-cutover") |
| OD-158 coverage gate vs mutation target | SYNCED (prd.md:127 "line coverage >= 95% … mutation kill rate is the Phase 6 target, not a P1 gate" = nfr-catalog §"Test-coverage gating (OD-158)":76-80 = module-criticality target framing) |
| OD-159/160/161 exclusion set — exactly 10 ids, identical spelling | SYNCED in 7 sites (SC-02 for the domain spec) |
| OD-162 every BC config key in interface-definitions with a range | PARTIAL (SC-09) |
| OD-163 own-temp-only cleanup | SYNCED (ARCH-04 §"Temp-file cleanup (OD-110, OD-163)":77-82 "No sweeping", BC-1.06.001:77, BC-1.06.002:72-96, VP-018, error-taxonomy:156; zero "sweep stale temps" text) |
| OD-164/OD-165 | SYNCED (test-vectors:41, error-taxonomy:60, BC-2.02.003:77,96,121; interface-definitions:173, BC-2.03.002:41) |
| Depth limits 993/994 stdin+transcript, 991/992 session+mix, 990/991 git+cost | SYNCED in all 8 named docs (pass-1 SC-01..04 fixed); no live "989" (history/"does not transfer" mentions only) |
| ARCH-06 pyfmt signatures vs BC-5.* | SYNCED except two 2-arg call snippets (SC-08); ModeText/ModeBytes pairing confirmed in BC-5.02.002/.003 |
| Repr recipe | SYNCED (ARCH-06:87 ADV-P2-D01 formulation; BC-5.01.005 four `-0.0` rows) |
| BC count 153 everywhere stated | STALE in 2 docs (SC-04, SC-05); BC-INDEX:30,38 and VP-INDEX/ARCH-INDEX current |
| VP count 40 everywhere stated | STALE in module-criticality (SC-03); VP-INDEX:34 and ARCH-INDEX:114 current |
| Titles: BC H1 = BC-INDEX = PRD = BC-ALLOCATION (153 each) | 152/153 exact — one PRD-enrichment drift (SC-06); BC-2.02.006 escaped-pipe row verified |
| VP `bcs:` vs BC body citations | 1 asymmetry = known-open VP-028 / BC-1.07.006 (SC-07); 0 reverse-only |
| module-criticality VP counts vs VP-INDEX | STALE (SC-03) |
| Timing gate 20 runs / 19th sorted | SYNCED (nfr-catalog NFR-001:24 and :68, ARCH-08:54, VP-036:41,71, cicd-setup:181 — 1 warm-up + 20 timed, nearest-rank p95 = 19th, per case, no pooling) |

## Findings

| ID | Sev | Location | Inconsistency | Owner |
|---|---|---|---|---|
| SC-01 | High | specs/product-brief.md:67 | "Out of Scope" still lists "Claude Code custom agent-panel rows / `--subagent` (OD-14)" — OD-155 supersedes OD-14 and ports it in P1 (prd.md:132-134; BC-1.07.001..008; interface-definitions:140). Only remaining stale-OD-14 text in the corpus; the same file's exclusion-set line (:82) was refreshed, so this is a missed bullet, not an untended doc | product-owner |
| SC-02 | Medium | specs/domain-spec/bounded-contexts.md:63; specs/domain-spec/ubiquitous-language.md:46 | Closed exclusion set listed as 7 ids (…temp-file, cp-x03) — missing OD-159/OD-160/OD-161. Canon 10-id set: BC-6.03.004:57-58, ARCH-07:44, prd.md:73, product-brief:82, VP-009:41, VP-012:39. Both lines cite BC-6.03.004, which now disagrees with them | product-owner |
| SC-03 | Medium | specs/prd-supplements/module-criticality.md:55,71 | VP counts predate VP-039/040: S1 row lists 18 VPs and the footer reads "Union … = 38/38 (all 38 VPs)" ("pass-2 remediation … includes VP-038"). VP-INDEX regenerated to 40 (VP-039 subagent elapsed clock, VP-040 frame/width — both `internal/statusline`) → S1 = 20, union = 40/40 | architect |
| SC-04 | Medium | specs/behavioral-contracts/BC-ALLOCATION.md:558 | "Cycle total: **145 BCs** (101 mapped from legacy + 44 new)" — the file's own table, BC-INDEX:38, and PRD §7 all total 153 (101+13+3+3+19+14; +8 from OD-155). Narrative not rebalanced after BC-1.07.* allocation | product-owner |
| SC-05 | Medium | specs/architecture-feasibility-report.md:24,26,28,74 | Self-contradiction after the partial :29 amendment ("153 BCs total"): :24/:26/:74 still "145 BCs", :26/:28 still "38-VP catalog". Amend the remaining lines the same dated way (the CA-07 inline-amendment precedent applies) | architect |
| SC-06 | Medium | specs/prd.md:336 | BC-4.01.002 title enriched in PRD §7 — "…never blank (incl. leftover --subagent)" — but BC H1 (ss-04/BC-4.01.002.md) and BC-INDEX:230 lack the enrichment. Criterion 75: enrichment lives in the H1, not only downstream. Carry the parenthetical into H1 + BC-INDEX (or trim PRD) | product-owner |
| SC-07 | Low (known-open) | specs/behavioral-contracts/ss-01/BC-1.07.006.md:95,125 ↔ specs/verification-properties/VP-028-*.md | Confirmed still open: BC body says the startswith property leg "rides VP-028" (changelog :21 records the 2026-11-18 reconciliation deliberately); VP-028 (body and `bcs:`) never cites BC-1.07.006. Sole VP↔BC asymmetry in the corpus | product-owner |
| SC-08 | Low | specs/behavioral-contracts/ss-05/BC-5.02.003.md:38,126 | Call snippets `pyfmt.Decode(b, ModeBytes)` (2-arg) vs pinned signature `Decode(b, mode, depthBudget)` (ARCH-06:30; VP-024:83,93 use the 3-arg form). Prose at :73 ("Decode therefore takes the recursion budget as a per-call-site [parameter]") is correct — snippet arity only | product-owner |
| SC-09 | Medium | specs/prd-supplements/interface-definitions.md:98-101,113 | OD-162 incomplete: registry = 33 individual rows + ONE family row (`statusline.theme.*`, :113); ~30 BC-used keys still have no row/range — e.g. `statusline.cost.window_s` (BC-1.05.005:54), `cost.record_throttle_s` (BC-1.05.004:54), `telemetry.url/query/fresh_s/keep_dead_s/timeout_s` (BC-1.04.001-.002), `ttft.*` (BC-1.04.010), `idle.after_s` (BC-1.04.012), `power.wall_*_w` (BC-1.04.011), `timer.*` (BC-1.02.015/.016), `limits.keep_s/_bands/countdown_max_factor/windows` (BC-1.02.011/.012/.030), `kv.host_*_pct` (BC-1.04.007), `sparkline.colors` (BC-1.04.009), `window_age.min_margin_ms` (BC-1.02.017), `routing.local_model_prefixes` (BC-2.01.002) — while :98-99 still delegates the full registry to BC-2.01.004 + the not-yet-created golden. Newly touched keys are done (`statusline.subagent.enabled`, `rebuild_excess`); the tail is not. If OD-162's recorded text blesses the §2.4 delegation, downgrade to INFO | product-owner |

INFO-01 (non-blocking): CP-O02..O05 are registered in the error taxonomy but cited by
no downstream BC/VP (1 corpus hit each — the definition row). Availability is the point
of the register; noting for the next OverflowError-adjacent edit.

Deliberately excluded from this check per orchestrator instruction: holdout scenarios,
stories/dependency graphs (not yet decomposed), adversarial-reviews content.

## 1. L2 to L3 Requirement Coverage

Not re-planned in this burst; PRD §6/§7 rows and BC-INDEX agree 153/153 (title-verified,
including the escaped-pipe BC-2.02.006 row).

## 2. L3 to L4 Verification Property Coverage

VP-INDEX rebuilt from all 40 files; method buckets 20+12+3+2+1+1+1 = 40 arithmetic ✓;
BC coverage map regenerated for 153 BCs; ARCH-INDEX:114 aggregate current. Remaining
drift is downstream of VP-INDEX: module-criticality (SC-03). VP-028 asymmetry = SC-07.

## 3. Dependency Acyclicity

N/A — stories not yet decomposed (Phase 1); deferred to implementation-readiness.

## 4. Architecture Alignment

ARCH-06 depth-constant block (:30) now carries the end-to-end measurement story and is
mirrored exactly in VP-006:47-57, ARCH-07:67-75, interface-definitions:57-64,
BC-5.02.003:69-82, BC-1.01.002:73-84, BC-1.03.004:58-147, prd.md:448,593. Formula
`limit = 999 − frames` stated identically in ARCH-06, ARCH-07, VP-006. ModeText/ModeBytes
pairing consistent. Signature-snippet residue: SC-08.

## 5. Acceptance Criteria Quality

ACs rewritten during pass-2 remediation; clause-level AC audit deferred to the main
consistency gate (same as pass-1).

## 6. Story Sizing

N/A — no stories exist yet (Phase 1).

## 7. Priority Consistency

N/A — no stories exist yet (Phase 1).

## 8. L1 to L2 to L3 to L4 Chain Completeness

Chain intact: PRD §6/§7 ↔ BC-INDEX ↔ 153 BC files ↔ VP-INDEX mutually complete and
title-synced. L1 product-brief has one out-of-scope remnant contradicting OD-155 (SC-01);
L2 domain-spec has the 7-vs-10 exclusion-set lag (SC-02).

## 9. AC Completeness Coverage

Deferred to the main consistency gate (same reason as §5).

## 10. ASM/R Traceability

Spot-checked via the risk register and ASM-007 (prd.md:621, OD-155); no stale mitigation
references found in the changed files. Full ASM/R sweep not repeated — unchanged since
the pass-1 audit.

## Cross-Reference Validation

- VP⇄BC: 40 VPs; citation graph symmetric except the known SC-07; no orphan VPs, no
  phantom BCs; VP-003 `bcs:` gained BC-1.07.008 symmetrically (BC-1.07.008 body cites VP-003).
- BC H1 ↔ BC-INDEX ↔ BC-ALLOCATION: 153/153 exact. PRD: 152/153 (SC-06); BC-3.01.001 /
  BC-2.02.006 parser artifacts manually verified as correct.
- Counts: BC-INDEX per-SS tally 101+13+3+3+19+14 = 153 = files on disk ✓; VP-INDEX
  rows = files = 40 ✓.
- Config keys: swept 247 dotted identifiers in 153 BC bodies; residual non-config
  symbols (stdlib, JSON fields, filenames, dummies `statusline.foo_s`, `a.b_c`) are
  documented or self-evidently not config keys; genuine config-key gaps = SC-09.

## Spec vs Implementation Drift

Not applicable — no implementation exists yet (pre-P1 stories).

## Validation Gate Result

**FAIL** — 7 blocking findings (SC-01..06, SC-09; 1 High, 6 Medium), 2 Low notes.
All are localized value/list/title updates; no structural damage, and the pass-1
findings (SC-01..04 depth sites, ARCH-INDEX aggregate, OD-149 paraphrase) are verified
fixed. Fix the seven, then recheck: product-brief Out of Scope, domain-spec set lists,
module-criticality VP tallies, the two 145-BC narratives, the BC-4.01.002 H1/PRD title
pair, and the interface-definitions key tail — to converge to PASS.

## Overall Metrics

- Checks executed: 18 categories, all evaluated; 0 skipped.
- Findings: 9 (1 High, 6 Medium, 2 Low); 1 INFO note; 0 Critical.
- Sync rate: 153/153 BC titles synced (PRD 152/153); 40/40 VP-INDEXed;
  1/40 VP↔BC asymmetry (known-open); depth canon 8/8 docs agree.

## Appendix: Validation Methodology

Scripts (session scratchpad): quadruple title extraction (BC H1 regex incl.
`Behavioral Contract` prefix; escaped-pipe handling; BC-INDEX/PRD/BC-ALLOCATION row
parsers) with id-set diff and title compare; dotted-identifier sweep of BC bodies vs
interface-definitions registry (individual + family rows, wildcards expanded); value
sweeps (`99[0-4]`, `989`, `CP-T08`, `CP-[OT]0x`, `OD-130/155..165`, `subagent`,
`sweep stale|own-temp-only`, `95%`, `20 runs|19th`, `145 BC|153 BC|38 VP|40 VP`,
`VP-028`). Inputs digested as `9175e7c` (diff-stat of the checked tree vs `47e1a86`).
