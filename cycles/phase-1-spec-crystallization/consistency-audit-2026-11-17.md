---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass"
producer: consistency-validator
timestamp: 2026-11-17T09:30:00Z
phase: 1
inputs: [specs/product-brief.md, specs/domain-spec/, specs/prd.md, specs/prd-supplements/, specs/behavioral-contracts/ (145 + BC-INDEX + BC-ALLOCATION), specs/architecture/ (ARCH-00..09 + ARCH-INDEX + BC-COMPONENT-MAP), specs/verification-properties/ (37 + VP-INDEX), specs/architecture-feasibility-report.md, specs/dtu-assessment.md, specs/gene-transfusion-assessment.md, specs/cicd-setup.md, specs/owner-decisions-log-2026-11-14.md, docs/PLAN.md]
input-hash: "e49aec4"
traces_to: prd.md
---

# Consistency Validation Report: hylo P1 — Phase 1 Spec Package

## Report Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo P1 (status line) |
| **Generated** | 2026-11-17T09:30:00Z |
| **Generator** | consistency-validator (fresh context) |
| **Artifacts Scanned** | 218 core spec files (145 BC + 37 VP + 12 architecture + 9 domain-spec + 5 supplements + 10 top-level), plus docs/PLAN.md |

Audit scope per orchestrator instruction: semantic, not only structural; owner rulings
OD-01..OD-151 treated as settled. Story-anchored criteria are out of scope (no stories
exist yet — Phase 2).

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | L2 to L3 Requirement Coverage | pass (1 MEDIUM anchor finding, CA-03) |
| 2 | L3 to L4 Verification Property Coverage | pass (CA-02, CA-05, CA-08) |
| 3 | Dependency Acyclicity | pass (module graph acyclic; no story graph yet) |
| 4 | Architecture Alignment | pass (CA-12 minor) |
| 5 | Acceptance Criteria Quality | n/a — no stories yet (Phase 2) |
| 6 | Story Sizing (all <= 13 points) | n/a — no stories yet (Phase 2) |
| 7 | Priority Consistency | pass at spec level (PRD §2 priorities internally consistent) |
| 8 | L1 to L2 to L3 to L4 Chain Completeness | pass (1 MEDIUM title drift, CA-01) |
| 9 | AC Completeness Coverage | n/a — no stories yet (Phase 2) |
| 10 | ASM/R Traceability | partial — no ASM/R register exists (CA-04) |
| 11 | Index/registry integrity (BC-INDEX, VP-INDEX, ARCH-INDEX, L2-INDEX, PRD §2) | pass (CA-01, CA-09) |
| 12 | Count reconciliation (BC 145, VP 37, ADR 13) | pass — all stated counts agree |

## 1. L2 to L3 Requirement Coverage

### 1.1 Domain Capabilities to Behavioral Contracts

| CAP-NNN | Description | Covered by BC-NNN? | Gap? |
|---------|-------------|-------------------|------|
| CAP-009 | Lane-aware status line | BC-1.01.x, 1.02.x, 1.03.x, 1.06.x, 3.01.001, 3.02.x, 4.01.001/.002, 5.x (enabler), 6.x (protector) | no |
| CAP-010 | Backend telemetry strip | BC-1.04.001..021 | no |
| CAP-011 | Cost accounting | BC-1.05.001..009 (and BC-1.02.029) | no |
| CAP-015 | Configuration management | BC-2.01.x, 2.02.x, 2.03.x, BC-4.01.003 | no |
| CAP-001..008, 012..014, 016..018 | Later-phase capabilities (P2-P6) | none — reserved rows in PRD §1.6, no BCs by design | no (by design) |

Anchor semantics: S1/S2 anchors are apt (CAP-010 telemetry, CAP-011 cost). Findings CA-03
(ss-06 anchors CAP-009 against PRD §1.6's DI-012 governance) and CA-11 (BC-4.01.003
version verb anchored CAP-015).

## 2. L3 to L4 Verification Property Coverage

### 2.1 Behavioral Contracts to Verification Properties

Verified via VP-INDEX "BC Coverage Map" cross-checked against all 37 VP files'
`source_bc` fields: 37/37 exact matches. VP-INDEX claims 145/145 BC coverage; the
per-family map is consistent on spot checks (BC-1.01.001 -> VP-001/VP-003; BC-1.06.002 ->
VP-018; BC-6.03.003 -> VP-012/VP-018).

| Family | BCs | VPs |
|--------|-----|-----|
| S1 status line | 93 | VP-001/003/005/006/007/008/013/014/018/020/021/022/027/028/029/030/031 |
| S2 config | 13 | VP-004/015/016/017 |
| S3 platform | 3 | VP-014/032/033 |
| S4 CLI | 3 | VP-002/004 |
| S5 pyfmt | 19 | VP-023/024/025/026 (+VP-006) |
| S6 harness | 14 | VP-009/010/011/012/019/034/035/037/019 |

Finding CA-05: no BC file carries a structured VP-anchor frontmatter field (Pass 3
deferral, self-declared in ARCH-INDEX and VP-INDEX propagation notes).

## 3. Dependency Acyclicity

### 3.1 Topological Order

No story dependency graph exists yet (Phase 2). At module level, the
module-criticality build order (pyfmt -> config/platform -> statusline -> cmd/hylo ->
parity) matches the ARCH-00 package graph; both are acyclic; pyfmt/platform are sinks
(`.factory/specs/prd-supplements/module-criticality.md`, mermaid graph; ARCH-00).

### 3.2 Critical Path

Not computable without stories. Module-level critical path: pyfmt -> statusline ->
cmd/hylo (nothing downstream of parity).

## 4. Architecture Alignment

### 4.1 Module Coverage

| Architecture Component | Stories Covering It | Coverage |
|-----------------------|--------------------|---------:|
| internal/statusline (+internal/cost) | BC-1.01..1.06 (93 BCs) via BC-COMPONENT-MAP | full (spec level) |
| internal/config | BC-2.01..2.02 (11 BCs) | full (spec level) |
| internal/platform | BC-3.01.001, 3.02.001/.002 | full (spec level) |
| cmd/hylo | BC-2.03.x, BC-4.01.x | full (spec level) |
| internal/pyfmt | BC-5.01..5.04 (19 BCs) | full (spec level) |
| internal/parity | BC-6.01..6.04 (14 BCs) | full (spec level) |

### 4.2 Component Consistency

BC-COMPONENT-MAP (145/145 rows) agrees with ARCH-02/06/07 file inventories (cfg/
registry.go, cfg/errors.go, py/num.go, py/json.go, py/str.go, py/time.go, par/oracle.go,
par/compare.go, par/exclusions.go) and with the ARCH-INDEX Subsystem Registry. Finding
CA-12 (RTM module cell for BC-1.05 omits internal/cost).

## 5. Acceptance Criteria Quality

Not evaluable: no stories exist yet (Phase 2). BC clause quality itself is high —
numbered Preconditions/Postconditions/Invariants, EC tables, canonical vectors (sampled
BC-1.01.001, BC-4.01.003, BC-6.01.001).

## 6. Story Sizing

Not evaluable: no stories exist yet (Phase 2).

## 7. Priority Consistency

At spec level: PRD §2 priorities are internally consistent (P0 core render paths, P1
registry/harness support, P2 `hylo version`/`config path`), and the RTM priority ranges
match the per-BC rows (spot-checked BC-2.03.x, BC-6.04.x). BC-ALLOCATION's own
Postcondition 3 writer-size claim is stale (CA-10).

## 8. L1 to L2 to L3 to L4 Chain Completeness

| Level | Artifact | Count | Traced Forward | Traced Backward | Coverage |
|-------|----------|-------|---------------|----------------|----------|
| L1 | Product brief (v1.0) | in scope | to L2 CAPs | N/A | 100% (P1 slice) |
| L2 | Domain capabilities (CAP-NNN) | 18 | 4 P1-phase CAPs to BCs; rest reserved | all (differentiator table) | 100% (P1 slice) |
| L3 | Behavioral contracts (BC-S.SS.NNN) | 145 | 145 to L4 (via VP-INDEX) | 145 to CAP/DI | 100% |
| L4 | Verification properties (VP-NNN) | 37 | N/A | 37 to BC | 100% |

Counts agree across BC-INDEX, BC-ALLOCATION, PRD §1.6/§2, BC-COMPONENT-MAP, VP-INDEX,
and module-criticality. Legacy accounting closes (101 + 1 OOS + 1 replaced = 103).

### Broken Chains

| Gap ID | From | To | Missing Link | Impact | Priority |
|--------|------|----|-------------|--------|----------|
| CHAIN-001 | BC-2.03.002 title (H1, BC-INDEX) | prd.md §2 | PRD §2:287 carries the pre-OD-132 title | Title lookups mislead during story decomposition | P1 |

### Orphaned Artifacts

| Artifact | Level | Issue | Resolution |
|----------|-------|-------|------------|
| (none) | — | — | — |

## 9. AC Completeness Coverage

Not evaluable (no stories). Structure verified instead: all 145 BC files carry numbered
Preconditions/Postconditions/Invariants, EC tables, canonical vectors, and a Purity
Classification section (145/145 on disk — the feasibility report's 90/145 note is stale,
CA-07).

## 10. ASM/R Traceability

### 10.1 Assumption Coverage

No ASM-NNN register exists. De facto register: PRD §9 assumptions 1-6 (prose-numbered,
resolved provenance); L2-INDEX deliberately omits assumption registers. Mapping by prose:

| PRD §9 item | Description | Status | Traced To | Holdout? | Story? | Coverage |
|---------|-------------|--------|-----------|----------|--------|----------|
| 1 | CPython 3.11.7 oracle pin | validated (writer re-runs 2026-11-15) | all vector-table BCs | -- | pending | full |
| 2 | Client surface stability | validated | BC-1.01.002 | -- | pending | full |
| 3 | Settings translation | validated | BC-1.02.005 | -- | pending | full |
| 4 | Binding latency target | validated | BC-6.04.002, NFR-001, VP-036 | -- | pending | full |
| 5 | Pending CI-leg verification (Windows edges) | open, disclosed | BC-1.06.001/.002, BC-6.01.003 | -- | pending | partial |
| 6 | Timeout ruling | validated | BC-1.04.001 | -- | pending | full |

### 10.2 Risk Register Coverage

No R-NNN register exists. De facto register: feasibility report "Risks and Mitigations"
(five rows, Likelihood/Impact populated, no IDs). Highest-impact row (cache-swap
divergence, HIGH) is addressed in architecture (AD-08, AD-09, VP-019).

| Feasibility risk row | Impact | Traced To | NFR? | Architecture? | Coverage |
|----------------------|--------|-----------|------|---------------|----------|
| Cache-swap byte divergence | high | VP-019, AD-08, BC-6.02.004 | -- | yes | full |
| p95 latency miss | medium | NFR-001, VP-036 | NFR-001 | yes (ARCH-08 gate) | full |
| Windows edges not executed | medium | Assumption 5, BC-6.04.001 | NFR-004 | yes (CI leg) | full |
| Fake-pass parity | high | AD-09, VP-012, BC-6.01.003 | -- | yes | full |
| Purity-annotation drift | low | remediated (145/145 on disk) | -- | yes | closed (stale count, CA-07) |

### 10.3 ASM/R Gate Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| HIGH-impact ASMs with holdout scenario | n/a — no register/holdouts (Phase 2 artifact) | 100% | n/a |
| Testable ASMs with story + assumption_validations | n/a | 100% | n/a |
| HIGH-impact R-NNNs with architecture mitigation | 2/2 (substance) | 100% | pass |
| Security R-NNNs in security review scope | 0 security-category risks identified | 100% | pass (vacuous) |
| R-NNN NFR candidates with corresponding NFR | 0 candidates flagged (no IDs exist) | 100% | pass (vacuous) |
| HIGH/HIGH R-NNNs with holdout scenario | n/a | 100% | n/a |
| Unvalidated ASMs after Phase 3 | 1 (Assumption 5) | 0 | deferred to Phase 3 by disclosure |
| Invalidated ASMs with risk escalation | 0 invalidated | 100% | pass |
| R-NNN Traced To bidirectional consistency | prose-level only (CA-04) | 100% | partial |

CA-04: either mint the ASM/R register (IDs, Impact fields) before Phase 2 or record an
explicit waiver that PRD §9 + feasibility Risks table are the canonical homes.

## Cross-Reference Validation

### ID Consistency

| Check | Status | Issues |
|-------|--------|--------|
| BC IDs unique (145) | pass | none |
| VP IDs unique (37) | pass | none |
| CAP IDs unique (18) | pass | none |
| BC traces to valid CAP | pass | CA-03/CA-11 semantics |
| VP traces to valid BC (37/37 source_bc) | pass | none |
| Story ACs trace to valid BC | n/a | no stories |

### Naming Convention Compliance

| Convention | Expected Pattern | Violations |
|-----------|-----------------|------------|
| BC naming | BC-S.SS.NNN | none |
| VP naming | VP-NNN | none |
| CAP naming | CAP-NNN | none |
| Error taxonomy | E-xxx-NNN | none (E-REN-*, E-CFG-001, E-CLI-001/002, E-VAL-001, E-HAR-001 used consistently) |

### Canonical Frontmatter Validation

Sampled BC-1.01.001, BC-6.01.001, all 37 VP source_bc lines, all indexes: document_type,
level, version, producer, timestamp, traces_to present throughout; lifecycle fields
coherent. Exception: `input-hash: "0000000"` placeholder in all 145 BC files (CA-09).

## Spec vs Implementation Drift

Not evaluable for code (no implementation yet). Spec-to-spec staleness found: CA-01
(PRD §2 title), CA-07 (feasibility purity count), CA-08 (feasibility VP-022 log entry),
CA-10 (BC-ALLOCATION postcondition).

## Findings

### Critical

None.

### Major

| ID | Files (line refs) | Inconsistency | Suggested owner |
|----|-------------------|---------------|-----------------|
| CA-01 | `.factory/specs/prd.md:287` vs `ss-02/BC-2.03.002.md:33`, `BC-INDEX.md:195`, `BC-ALLOCATION.md:247` (Invariant 4 at :432-434) | PRD §2 title stale: "prints the per-OS config file path" vs H1/source-of-truth "prints the config, cache and state paths (OD-132)" | product-owner (one-line PRD edit) |
| CA-02 | `VP-INDEX.md:31-37` vs catalog rows :56, :62, :65, :77, :79, :80 | Method-bucket memberships contradict the Catalog Method column (VP-006/012/015 missing from property/fuzz; VP-027/029/030 claimed by golden/parity while cataloged unit/table); sums to 37 regardless | architect (regenerate Totals bullets) |
| CA-03 | `ss-06/BC-6.02.001.md:22,125` (pattern: all 14 ss-06 files) | Harness BCs anchor `capability: "CAP-009"` while PRD §1.6 (:106) governs S6 by DI-012 machinery; unjustified semantic stretch | product-owner (annotate or re-anchor) |
| CA-04 | `prd.md:564-572`; `architecture-feasibility-report.md:75-82`; `L2-INDEX.md` omission note | No ASM-NNN/R-NNN register anywhere; gate criteria must be evaluated against de facto prose registers (PRD §9, feasibility risk table) | architect + product-owner (mint register or waive) |

### Minor

| ID | Files (line refs) | Inconsistency | Suggested owner |
|----|-------------------|---------------|-----------------|
| CA-05 | grep verification_properties over ss-0* = 0; `ARCH-INDEX.md:99-104`; `VP-INDEX.md:217-222` | Structured BC->VP anchors pending Pass 3 (self-declared) | architect |
| CA-06 | `module-criticality.md:38-44` | VP Count column all "VP-TBD" though 37 VPs are module-assigned | product-owner |
| CA-07 | `architecture-feasibility-report.md:81` | Says purity sections in 90/145 BCs; disk now 145/145 | architect |
| CA-08 | `architecture-feasibility-report.md:96` vs `ARCH-INDEX.md:116`, `VP-INDEX.md:72,86` | VP-022 log entry outstanding though fixed; VP-036 home ARCH-08 (VP-INDEX) vs ARCH-03 bucket (ARCH-INDEX); VP-001 ARCH-00 vs ARCH-03 | architect |
| CA-09 | all 145 `ss-0*/BC-*.md:14` | `input-hash: "0000000"` placeholder everywhere | product-owner |
| CA-10 | `BC-ALLOCATION.md:420` vs :378 | Postcondition "at most 21 contracts/group" vs writer G=22 post-OD-141 | product-owner |
| CA-11 | `ss-04/BC-4.01.003.md:91` | `hylo version` anchored CAP-015 glossed "CLI surface" — loose | product-owner |
| CA-12 | `prd.md:530` vs `BC-COMPONENT-MAP.md:134-139`; docs/PLAN.md §6 | RTM BC-1.05 module omits internal/cost; PLAN §6 predates internal/pyfmt, internal/parity (informational) | product-owner |

## Validation Gate Result

**PASS** (with findings) — no blocking findings; CA-01..CA-04 recommended before Phase 2
story decomposition.

## Overall Metrics

| Metric | Value |
|--------|-------|
| **Total Checks** | 12 |
| **Passed** | 8 |
| **Failed** | 0 |
| **Warnings** | 4 MEDIUM + 8 LOW findings |
| **Overall Status** | inconsistencies-found (minor, none blocking) |

Consistency score 92/100: identifiers, counts, and cross-links are effectively exact; the
four MEDIUM findings are semantic-title, bucket-membership, capability-anchor, and
register-shape drifts rather than broken chains.

## Appendix: Validation Methodology

Fresh-context audit (no prior passes consulted). Structural: enumerated all spec files,
diffed indexes against files (BC-INDEX 145 rows <-> 145 files; VP-INDEX 37 <-> 37;
ARCH-INDEX Document Map <-> 10 ARCH files; L2-INDEX <-> 8 sections; PRD §2 145 unique
links), reconciled counts across seven statements, cross-checked all 37 `source_bc`
fields against VP-INDEX. Semantic: read representative BC files per shard (BC-1.01.001,
BC-4.01.003, BC-6.02.001, BC-6.01.001), compared capability anchors against PRD §1.6 and
L2 capabilities.md, compared BC-COMPONENT-MAP homes against ARCH-02/06/07 file
inventories and docs/PLAN.md §6, evaluated gate criteria against the artifacts where they
actually live (flagging the ASM/R shape gap). Owner rulings OD-01..OD-151 were treated as
settled and none are counted as findings. Full criteria list: consistency-validator
agent definition (80 criteria); story-dependent criteria marked n/a.
