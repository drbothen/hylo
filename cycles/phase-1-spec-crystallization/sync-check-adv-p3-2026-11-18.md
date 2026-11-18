---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass"
producer: consistency-validator
timestamp: 2026-11-18T00:00:00
phase: 1
inputs: [specs/behavioral-contracts/, specs/architecture/, specs/domain-spec/, specs/verification-properties/, specs/prd.md, specs/prd-supplements/, specs/cicd-setup.md, specs/architecture-feasibility-report.md]
input-hash: "0d236f5"
traces_to: ../../STATE.md
---

# Consistency Validation Report: hylo pass-3 fix-burst sync check

## Report Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo (status line + hybrid routing, P1 spec crystallization) |
| **Generated** | 2026-11-18T00:00:00 |
| **Generator** | consistency-validator |
| **Artifacts Scanned** | 142 changed files vs `9122069` (checked: 40+ spec documents across 7 trees) |

**Scope note.** Step-4b cross-document sync check after the adversarial pass-3 fix
burst (delta validation, per orchestrator instruction). Items already machine-verified
by the orchestrator are excluded: 154 BC H1 titles vs BC-INDEX/PRD; VP bcs ↔ BC body
citation bijection (3 prose-only exclusions); no live 989 depth value; no live CP-T08;
language screening. Read-only except this file; nothing committed.

## Summary

Standing 10-category summary (delta-check dispositions; the full 80-criterion sweep
recurs at convergence):

| # | Check | Result |
|---|-------|--------|
| 1 | L2 to L3 Requirement Coverage | pass (burst-propagation rows below) |
| 2 | L3 to L4 Verification Property Coverage | pass (burst rows below) |
| 3 | Dependency Acyclicity | pass (no graph edges changed by the burst) |
| 4 | Architecture Alignment | pass with SC-03 |
| 5 | Acceptance Criteria Quality | n/a — burst-scoped (no story ACs in delta) |
| 6 | Story Sizing | n/a — burst-scoped (no story files in delta) |
| 7 | Priority Consistency | n/a — burst-scoped (no story files in delta) |
| 8 | L1 to L2 to L3 to L4 Chain Completeness | pass (154/40 chain intact; counts verified) |
| 9 | AC Completeness Coverage | n/a — burst-scoped (see #5) |
| 10 | ASM/R Traceability | pass (R-008 amendment verified against OD-167) |

### Burst-sync check matrix (16/16 executed)

| # | Check | Result |
|---|-------|--------|
| 1 | OD-155 `--subagent` routing (membership anywhere in argv[1:], incl. after `--`, before unknown-flag handling): BC-1.07.001, BC-4.01.002 EC-004, ARCH-01:59, VP-002, SM-04; corroborated in BC-2.02.001 §8, DI-008, CAP-009, ubiquitous-language, ARCH-07:98, prd:435 | PASS (SC-01, SC-02) |
| 2 | OD-166 unconvertible cost value not recorded: BC-1.05.002 EC-009, BC-1.05.004 record guard, BC-1.05.007 EC-012, BC-1.05.005 EC-011 xref, error-taxonomy:126/129/185, risk-register R-008; ARCH-04:35 carries no contradicting text | PASS |
| 3 | OD-167 skip line + drop in-flight turn: BC-1.03.010 EC-009 + CP-O08 canonical vector, BC-1.03.018 CP-O08, error-taxonomy:139-142/187, risk-register R-008; ARCH-03 `#transcript` anchor exists | PASS |
| 4 | OD-168 subagent config error → zero stdout bytes + stderr: BC-1.07.002, BC-2.02.001 §8, ARCH-01:44/62/93, ARCH-03:138, SM-04, DI-008, CAP-009, ubiquitous-language:39, VP-001, VP-005, interface-definitions:39, prd:435/480 | PASS |
| 5 | Never-blank carve-out for `--subagent`: DI-008, CAP-009, SM-04, prd NFR-002:480, nfr-catalog NFR-002:25, VP-001, VP-005 — identical carve-out wording everywhere | PASS |
| 6 | Crash ids CP-O01..O11 / CP-A01..A05: taxonomy register complete, owning-BC rows match the BCs on disk; no stray/malformed ids; prd:480 = nfr-catalog:25 trigger lists; ARCH-07 case-id families cpo01..cpo11/cpa01..cpa05 | PASS |
| 7 | Overflow threshold `2**1024 - 2**970` (raises at `>=`, one below converts): error-taxonomy:164, BC-1.02.014, BC-1.03.006/007/018, BC-1.04.001, BC-1.05.002/007, BC-1.07.007 — identical value and boundary direction | PASS |
| 8 | Closed 10-id exclusion set (D4-EX-1/2/3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161): identical membership in BC-6.03.004, VP-012, ARCH-07; VP-012 v1.4 rider names aligned | PASS |
| 9 | Config keys used in BCs registered in interface-definitions with matching ranges: `statusline.subagent.{enabled,glyphs.*,colors.*,joiner,tokens.*}` all present; owner column maps to BC-1.07.002/004/005/007 | PASS |
| 10 | Percentile ordering (yellow <= red): ratified in BC-1.05.005:63-64 and registry row :156 | PASS (SC-04 dangling mirror) |
| 11 | Seconds ranges: uniform "finite" predicates with legacy-honest exceptions (git.ttl_s negatives per pass-3 B08; telemetry.ttl_s int64-ns cap) | PASS |
| 12 | Counts: 154 BCs = 101+13+3+3+20+14 (disk: 154; ss-05 = 20); 40 VP files (disk: 40); all live statements match (BC-INDEX:38, BC-COMPONENT-MAP:241, prd:126/117, ARCH-INDEX:115, VP-INDEX:34, feasibility-report:36); feasibility-report's 145/153/38 figures are explicitly dated amendments, not live claims | PASS |
| 13 | Timing gate 1 warm-up + 20 timed runs, p95 = 19th sorted, per case, no pooling: nfr-catalog:24/68, ARCH-08:59, BC-6.04.002, VP-036, cicd-setup:190 — identical, incl. 5-sample note and VP-036 oversize exclusion | PASS |
| 14 | ARCH-06 canon signatures — `Decode(b, mode, depthBudget)`, `TimeFloat(time.Time)`, `LocalToUnix → (int64, error)`: quoted verbatim in BC-5.02.002, BC-5.02.003, BC-5.04.002:36, BC-5.04.003:40 | PASS |
| 15 | ARCH-03 anchors referenced by BCs: all friendly fragments inside the closed 12-anchor set; both heading-slug anchors resolve | PASS |
| 16 | Harness case model argv/subagent family: ARCH-07 (argv verbatim, default `["statusline"]`, subagent rows), BC-6.01.001 (oracle argv allows `--subagent`), BC-6.03.001 (`-sub` goldens), VP-009/010 (family replay, subagent goldens) agree — except SC-03 | PASS with SC-03 |

## 1. L2 to L3 Requirement Coverage

Delta scope: the burst's propagation rows are check #1-#5 of the matrix above
(CAP-009/DI-008/SM-04 carve-out wording and the OD-155/166/167/168 rulings). No CAP
mapping changed; CAP-009's row absorbed the OD-155/OD-168 carve-out consistently.

## 2. L3 to L4 Verification Property Coverage

Delta scope: VP-001, VP-002, VP-005, VP-010, VP-012, VP-036 amended in the burst; each
still cites its standing BC set, and VP-012's rider respelling (OD-30 rider →
TestCostHistory_OD30_NumericSidStringKey) matches the rider BC. VP-INDEX rebuilt from
all 40 VP files; coverage map regenerated for 154 BCs.

## 3. Dependency Acyclicity

No dependency-graph inputs (stories, waves) exist in the delta; burst introduced no new
ordering constraints. Full topological sweep recurs at story decomposition.

## 4. Architecture Alignment

Delta scope: ARCH-01/03/06/07/08 amendments all reconcile with their owning BCs (rows
6-16 above). SC-03 is the single alignment gap: the case-model BC (BC-6.02.003) does
not yet carry the `argv` case-field that ARCH-07:98 and VP-009 establish normatively.

## 5. Acceptance Criteria Quality

Not in delta scope (no story files in the 142-file burst). Standing check recurred in
pass-2 sync (SC-05) and recurs at Phase 2.

## 6. Story Sizing

Not in delta scope — no story files in the burst delta.

## 7. Priority Consistency

Not in delta scope — no story files in the burst delta.

## 8. L1 to L2 to L3 to L4 Chain Completeness

| Level | Artifact | Count | Traced Forward | Traced Backward | Coverage |
|-------|----------|-------|----------------|-----------------|----------|
| L1 | Product Brief | 1 | yes (unchanged in burst: 1 wording line) | N/A | 100% |
| L2 | Domain Capabilities (CAP-NNN) | 12 (incl. CAP-009 carve-out) | to L3 | to L1 | 100% |
| L3 | Behavioral Contracts (BC-S.SS.NNN) | 154 | to L4 | to L2 | 100% |
| L4 | Verification Properties (VP-NNN) | 40 | N/A | to L3 | 100% |

No new broken chains and no new orphans introduced by the burst.

## 9. AC Completeness Coverage

Not in delta scope (no story ACs in the burst). BC-clause-level reverse coverage
(criteria 34-41) recurs at Phase 2 decomposition.

## 10. ASM/R Traceability

Delta scope: R-008 (transcript-borne overflow skip) amended for OD-167 ("drops the
in-flight turn") and still names NFR-003 + ARCH-04/ARCH-07 mitigation columns; the
extended D4-EX-2 predicate family keeps the closed id set (rows 8 above). No ASM
status changed in the burst.

## Cross-Reference Validation

### ID Consistency

| Check | Status | Issues |
|-------|--------|--------|
| BC/VP/CAP IDs unique | pass | none observed in delta |
| BC ↔ CAP / VP ↔ BC traces | pass | orchestrator-verified bijective (3 prose-only exclusions honored) |
| Story ACs trace to valid BC | n/a | no story deltas |
| Crash-id spellings | pass | no CP-O12/CP-A06/CP-O00/CP-A00 or malformed range endpoints anywhere |

### Naming Convention Compliance

| Convention | Expected Pattern | Violations |
|-----------|-----------------|------------|
| BC naming | BC-S.SS.NNN | none |
| VP naming | VP-NNN | none |
| CAP naming | CAP-NNN | none |
| Error taxonomy | E-xxx-NNN + CP-xNN register | none |

## Spec vs Implementation Drift

Implementation phase not started; drift check not applicable. Nearest analog: SC-03 is
spec-internal lag (BC-6.02.003 behind ARCH-07's pass-3 A03 amendment).

## Findings

| SC-NN | Severity | File:line | Inconsistency | Owner agent |
|-------|----------|-----------|---------------|-------------|
| SC-01 | Minor | `specs/verification-properties/VP-002-unknown-flag-one-line.md:44` | Legacy scan quoted as `` `"-subagent" in sys.argv[1:]` `` (single dash); actual legacy source is `"--subagent" in sys.argv[1:]` (`legacy/dgx_statusline.py:1240`). BC-1.07.001:93 quotes it correctly; VP-002's normative rows are correct, so prose-only quote drift. | technical-writer |
| SC-02 | Minor | `specs/domain-spec/state-machines.md:67`, `specs/domain-spec/invariants.md:31` | Membership-test cite "legacy SL:1238"; SL:1238 is the `if __name__ == "__main__":` guard — the test sits at SL:1240-1241. BC-1.07.001:93 and VP-002 cite 1240. | business-analyst |
| SC-03 | Major | `specs/behavioral-contracts/ss-06/BC-6.02.003.md:56-63` | Case-model BC's manifest and `case.json` schema (`{now, tz?, columns?, settings, metrics, seed?, transcript?, steps?}`) contain no `argv` key (zero occurrences in file), while pass-3 A03 added `argv` as a case content "passed to the built `hylo` binary verbatim" (`specs/architecture/ARCH-07-parity-harness.md:98`, explicit supersession note) and VP-009:53 names BC-6.02.003 the case model. The file was untouched in this burst, so the authoritative case schema cannot express the argv field the harness, VP-002 skeleton, and BC-6.01.001 oracle rows rely on. Remedy: add `argv` to `case.json` + a both-sides-receive-identical-argv postcondition, or add an explicit pointer to ARCH-07's row. | architect |
| SC-04 | Minor | `specs/prd-supplements/interface-definitions.md:156` vs `:176-177` | `statusline.cost.percentiles` ASCENDING rule justified as "mirroring the yellow <= red band rule", but that band rule is ratified nowhere: the bands rows (`:176-177`) say only "each a finite Float (band comparison)" and BC-1.02.011/BC-1.02.024 pin defaults without an ordering constraint. State the ascending constraint on the bands rows or recast the mirror remark. The percentiles rule itself is properly ratified in BC-1.05.005:63-64. | product-owner |

### Critical

None. (Counts, title sync, citation bijection, exclusion-set closure, threshold, and
timing-gate propagation all verified clean.)

### Major

- **SC-03** — BC-6.02.003 case schema lags the pass-3 A03 argv amendment (see table).

### Minor

- **SC-01** — VP-002:44 single-dash legacy quote.
- **SC-02** — SL:1238 vs SL:1240 cite drift in SM-04/DI-008.
- **SC-04** — dangling "yellow <= red band rule" mirror reference in
  interface-definitions:156.

## Validation Gate Result

**PASS** — no blocking (Critical) findings. SC-03 (Major) should be remediated before
Phase 2 story decomposition so the case-model BC carries the argv field; SC-01/02/04
may ride the next wording touch of their files.

## Overall Metrics

| Metric | Value |
|--------|-------|
| **Total Checks** | 16 burst-sync + 10 standing categories |
| **Passed** | 16 + 6 standing pass |
| **Failed** | 0 |
| **Warnings** | 4 (SC-01..SC-04) |
| **Overall Status** | inconsistencies-found (minor; none blocking) |

The pass-3 fix burst propagated cleanly: all sixteen targeted propagation checks agree
across BCs, PRD, domain spec, architecture, VP catalog, and supplements. The four
findings are localized wording/cite/schema-lag items; only SC-03 affects an
implementer, and it is confined to one BC's case-manifest section.

## Appendix: Validation Methodology

Read-only grep/read sweep over the factory worktree at baseline `9122069` (142 changed
files). Method: per-check targeted greps across `specs/` (id inventories, count
statements, threshold strings, exclusion-set membership, signature strings, anchor
targets), full reads of the ruling-adjacent sections (BC-1.07.001/002, BC-4.01.002,
BC-6.01.001, BC-6.02.003, BC-6.03.001/004, VP-002/009/010/012, ARCH-03 fragment-anchor
table, ARCH-06 signature canon, ARCH-07 case tables, error-taxonomy OD-156 register,
domain-spec SM-04/DI-008/CAP-009), and cross-doc comparison against the legacy oracle
source read (never run: `legacy/dgx_statusline.py:1236-1246`). Excluded per
orchestrator: items already machine-verified. Delta-scoped check per instruction; the
full 80-criterion sweep is deferred to the convergence gate. Findings use SC-NN
continuing the pass-2 sync-check numbering lineage.
