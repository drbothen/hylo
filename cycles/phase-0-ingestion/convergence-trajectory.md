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
| 0 (deep inventory) | 2026-11-14 | 3 (r1-r3) | — | — | — | — | decayed to NITPICK | — | — | CONVERGED (r3 NITPICK) |
| 1 (deep architecture) | 2026-11-14 | 3 (r1-r3) | — | — | — | — | decayed to NITPICK | — | — | CONVERGED (r3 NITPICK) |
| 2 (deep domain) | 2026-11-14 | 9 (r1-r9) | — | — | — | — | decayed to NITPICK | — | — | CONVERGED (r9 NITPICK) |
| 3 (deep behavioral contracts) | 2026-11-14 | 8 (r1-r8) | — | — | — | — | decayed to NITPICK | — | — | CONVERGED (r8 NITPICK) |
| 4 (deep NFR/thresholds) | 2026-11-14 | 7 (r1-r7) | — | — | — | — | decayed to NITPICK | — | — | CONVERGED (r7 NITPICK) |
| 5 (deep conventions) | 2026-11-14 | 5 (r1-r5) | — | — | — | — | decayed to NITPICK | — | — | CONVERGED (r5 NITPICK) |

## Trajectory Shorthand

`3→NITPICK` (pass 0); `3→NITPICK` (pass 1); `9→NITPICK` (pass 2); `8→NITPICK` (pass 3); `7→NITPICK` (pass 4); `5→NITPICK` (pass 5) — qualitative deepening series; the →0→0→0→0 formal finding-series placeholder in STATE.md is retained until the first tally-based adversary pass. Deepening order was 2, 3, then 0, 1, 4, 5; the table is sorted by pass number.

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

### Pass 0 — deep inventory (2026-11-14)

**Rounds:** 3 (SUBSTANTIVE r1-r2, NITPICK r3)
**Novelty:** decayed to NITPICK
**Verdict:** CONVERGED (declaration on disk: "Rounds: r1 SUBSTANTIVE, r2 SUBSTANTIVE, r3 NITPICK")
**Canonical artifact:** r3 §2 — `semport/hylo-legacy/hylo-legacy-pass-0-deep-inventory-r3.md`

---

### Pass 1 — deep architecture (2026-11-14)

**Rounds:** 3 (SUBSTANTIVE r1-r2, NITPICK r3)
**Novelty:** decayed to NITPICK
**Verdict:** CONVERGED (declaration on disk: "Rounds: r1 SUBSTANTIVE, r2 SUBSTANTIVE, r3 NITPICK")
**Canonical artifact:** r3 §B, including two Mermaid diagrams — `semport/hylo-legacy/hylo-legacy-pass-1-deep-architecture-r3.md`

---

### Pass 4 — deep NFR/thresholds (2026-11-14)

**Rounds:** 7 (SUBSTANTIVE r1-r6, NITPICK r7)
**Novelty:** decayed to NITPICK
**Verdict:** CONVERGED
**Override note:** the orchestrator overrode r4's self-declared NITPICK — r4 contained retractions and relied on a retracted HTTP/2 fact, so it was treated as SUBSTANTIVE.
**Canonical artifact:** r7 final catalogue — `semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md` (147 thresholds; 120 rationales resolved; OD-57: 18 bulk-confirm + 27 owner-rationale in 7 groups; OD-94 fact sheet carrying the Go 1.26.5 h2 facts).

---

### Pass 5 — deep conventions/env/determinism/pitfalls (2026-11-14)

**Rounds:** 5 (SUBSTANTIVE r1-r4, NITPICK r5)
**Novelty:** decayed to NITPICK
**Verdict:** CONVERGED
**Canonical artifact:** r3 consolidated, amended by r4-r5 — `semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md` (43 explicit + 21 implicit env inputs; 54 determinism rows + 6 Go-side pins; 19 conventions; 22 pitfalls).

---

<!-- Repeat for each pass. Maintain chronological order. -->

## Frontmatter Fields (extracted from STATE.md)

<!-- When compacting STATE.md, adversary_pass_* frontmatter fields are
     converted to rows in the Finding Progression table above.
     Original field format: adversary_pass_N_findings: "description"
     Original field format: adversary_pass_N_date: "YYYY-MM-DD" -->

## Extracted from STATE.md on 2026-11-17

### Convergence Status (as recorded at the 2026-11-17 session-wrap pause)

- **All six passes CONVERGED.** Rounds: pass 0 — 3 (SUBSTANTIVE r1-r2, NITPICK r3); pass 1 — 3 (SUBSTANTIVE r1-r2, NITPICK r3); pass 2 — 9 (SUBSTANTIVE r1-r8, NITPICK r9); pass 3 — 8 (SUBSTANTIVE r1-r7, NITPICK r8; r7 self-declared NITPICK overridden by the orchestrator — new crash path H-09, retraction CONV-ABS-22); pass 4 — 7 (SUBSTANTIVE r1-r6, NITPICK r7; r4 self-declared NITPICK overridden — retractions and reliance on a retracted HTTP/2 fact); pass 5 — 5 (SUBSTANTIVE r1-r4, NITPICK r5).
- Round-disposition declarations verified on disk in the final-round files (pass-0/1 r3 declarations; pass-4 r7 / pass-5 r5 "findings are nitpicks, not gaps").

### Phase Progress row detail — "Adversary passes (Phase 0)" (as recorded 2026-11-17)

**ALL SIX CONVERGED** — p0: 3 rounds (NITPICK r3); p1: 3 (NITPICK r3); p2: 9 (NITPICK r9); p3: 8 (r7 self-declared NITPICK overridden — crash path H-09, CONV-ABS-22); p4: 7 (NITPICK r7; r4 self-declared NITPICK overridden — retractions + reliance on a retracted HTTP/2 fact); p5: 5 (NITPICK r5). Trajectory-tail →0→0→0→0 placeholder retained for the formal finding series.

### Registers paragraph (was under the Canonical Phase 1 Inputs table)

Registers: BC index totals 232 BCs = 137 byte-exact + 44 JSON-equivalent + 10 out of scope + 6 approved deviation + 35 pending owner decision. Statement partition (1,809 Python statements): 903 re-read + 422 covered by pinned tables + 133 out of scope + 351 read in pass-2 r8; 0 uncovered. Retractions: RET crosswalk (pass-3 r4) plus CONV-ABS through 94; next free CONV-ABS 95; IDs 101-104 unused. Extraction validation (validate-extraction, not a deepening round): PASS-WITH-FIXES; exhaustive; 0 hallucinations. Final analysis (this burst): coverage audit PASS (step B.5, 0 gaps); extraction validation r2 PASS-WITH-FIXES (step B.6: 78/232 BCs sampled, 100% confirmed; 26/27 metric groups exact; 1 fix applied in-burst); definitive synthesis pass-8 (supersedes pass-6); lessons 53 — 13 P0 (L0-01..L0-13), 13 P1, 9 P2, 18 P3 — recorded in pass-8 §10. Evidence captured this burst: proxy venv `pyvenv.cfg` include-system-site-packages=false (proxy and preflight not affected by the user site; parity harness runs shimmed Python cases under -s); mitmproxy 12.3.1 with no config.yaml; Go 1.26.5 h2 facts recorded for OD-94. Trajectory-tail (D-433(e) LENGTH=4): →0→0→0→0 placeholder retained until the formal finding series begins.
