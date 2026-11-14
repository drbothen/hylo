---
document_type: convergence-trajectory
level: ops
version: "1.0"
status: in-progress
producer: state-manager
timestamp: 2026-11-14T08:30:00Z
cycle: "phase-0-ingestion"
inputs: [STATE.md, "semport/hylo-legacy"]
input-hash: "[live-state]"
traces_to: STATE.md
---

# Convergence Trajectory — phase-0-ingestion

<!-- Scope note: rows record convergence-deepening rounds over broad-sweep
     passes of the brownfield-ingest protocol (S = SUBSTANTIVE round,
     N = NITPICK round). Round counts are dispositions, not finding tallies;
     per-round detail lives in the linked semport deep files. -->

## Finding Progression

| Pass | Date | Total (deep rounds) | CRIT | HIGH | MED | LOW | Novelty | Score | Counter | Verdict |
|------|------|---------------------|------|------|-----|-----|---------|-------|---------|---------|
| 2 (deep domain) | 2026-11-14 | 9 (r1-r9) | — | — | — | — | decayed to NITPICK | — | — | CONVERGED (r9 NITPICK) |
| 3 (deep behavioral contracts) | 2026-11-14 | 8 (r1-r8) | — | — | — | — | decayed to NITPICK | — | — | CONVERGED (r8 NITPICK) |

## Trajectory Shorthand

`9→NITPICK` (pass 2); `8→NITPICK` (pass 3) — qualitative deepening series; the →0→0→0→0 formal finding-series placeholder in STATE.md is retained until the first tally-based adversary pass.

## Per-Pass Details

### Pass 2 — deep domain (2026-11-14)

**Rounds:** 9 (SUBSTANTIVE r1-r8, NITPICK r9)
**Novelty:** decayed to NITPICK
**Verdict:** CONVERGED
**Canonical artifact:** pass-2 r8 §7 combined pointer table, amended by r9 — `semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r8.md`

Statement partition contribution: of the 1,809 Python statements, 903 re-read and 351 read in r8; 422 covered by pinned tables; 133 out of scope; 0 uncovered.

---

### Pass 3 — deep behavioral contracts (2026-11-14)

**Rounds:** 8 (SUBSTANTIVE r1-r7, NITPICK r8)
**Novelty:** decayed to NITPICK
**Verdict:** CONVERGED
**Override note:** the orchestrator overrode r7's self-declared NITPICK — round r7 surfaced new crash path H-09 and retraction CONV-ABS-22, which are substantive, so r8 was mandated.
**Canonical artifact:** pass-3 r4 canonical BC index, amended by r5-r8 — `semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md`

Index totals at convergence: 232 BCs = 137 byte-exact + 44 JSON-equivalent + 10 out of scope + 6 approved deviation + 35 pending owner decision. Retraction ledger: RET crosswalk in pass-3 r4; CONV-ABS 12-28; next free CONV-ABS 29.

---

<!-- Repeat for each pass. Maintain chronological order. -->

## Frontmatter Fields (extracted from STATE.md)

<!-- When compacting STATE.md, adversary_pass_* frontmatter fields are
     converted to rows in the Finding Progression table above.
     Original field format: adversary_pass_N_findings: "description"
     Original field format: adversary_pass_N_date: "YYYY-MM-DD" -->
