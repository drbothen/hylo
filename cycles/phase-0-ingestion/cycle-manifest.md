---
document_type: cycle-manifest
cycle_id: phase-0-ingestion
cycle_type: brownfield-ingestion (pre-release Phase 0 cycle; template enum has no brownfield-ingestion type)
version: unversioned (pre-P1)
status: in-progress
started: 2026-11-13
completed:
producer: orchestrator
---

# Cycle Manifest: phase-0-ingestion (brownfield ingestion)

## Delivered

| Metric | Value |
|--------|-------|
| Stories delivered | none (Phase 0 precedes decomposition) |
| BCs created | 0 ratified; 136 BC candidates extracted from legacy/ (broad sweep passes 0-6) |
| VPs created | 0 (Phase 1 work) |
| Holdout scenarios | 0 new, 0 retired |
| Total cost | not tracked (session-local agents) |
| Adversarial passes | 0 adversary passes; extraction validation PASS-WITH-FIXES (exhaustive, 0 hallucinations) |
| Final holdout satisfaction | n/a |
| Release version | n/a |

## Spec Changes

| Artifact | Change | Before | After |
|----------|--------|--------|-------|
| specs/research/ | new: 4 research reports + RESEARCH-INDEX.md (verified: exactly one row per report) | absent | 4 reports indexed, status complete |
| semport/hylo-legacy/ | new: semport-analyze passes 0-6 + extraction validation over legacy/ | absent | 7 pass reports + 1 validation report |
| policies.yaml | policy 12 settled-decision range D1-D12 -> D1-D15; policy 20 config_over_code added | 1.1 | 1.2 |
| STATE.md | phase pre-0 -> 0, pipeline IN_PROGRESS; owner decisions D13-D15; research pointers; open owner questions | 52 lines | rewritten (kept under 200 lines) |

## Living Spec Snapshot

Captured at: n/a (no tag yet; Phase 0 in progress)
Retrieve: git -C .factory log --follow specs/ (history on factory-artifacts)

## Deprecations (if any)

| Artifact | Deprecated By | Replacement | Sunset Date |
|----------|--------------|-------------|-------------|
| none | | | |

## Tech Debt Created

| ID | Description | Priority | Source |
|----|-------------|----------|--------|
| (none formally registered yet; legacy quirks awaiting disposition are tracked as open owner questions in STATE.md) | | | |

## Governance Policies Adopted

| Policy | Adopted In | Incident Reference | Generalization |
|--------|-----------|-------------------|----------------|
| config_over_code (POL-20) | grounding burst, 2026-11-14 | owner decision D15 | behavior-shaping values live in internal/config (config file -> HYLO_* env -> default), never in logic |

## Notes

- Broad sweep yield: 136 BC candidates, 105 thresholds (52 with rationale UNKNOWN), 40 env vars, 12 ledger events, 27 metric families.
- Extraction validation verdict: PASS-WITH-FIXES (exhaustive; 0 hallucinations).
- Owner decisions recorded this cycle: D13 (intercept all Claude Code traffic), D14 (no proxy env leak to child processes), D15 (config over code iron rule).
- Remaining Phase 0 steps: convergence-deepening, coverage-audit, final-synthesis, input-hash drift check, owner approval gate.
