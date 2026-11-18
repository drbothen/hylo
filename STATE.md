---
document_type: pipeline-state
level: ops
version: "2.4"
status: in_progress
producer: state-manager
timestamp: 2026-11-18T02:58:22Z
last_amended: "2026-11-18 (v2.8 — state-manager — phase-1d pass-3 remediation burst recorded: rulings OD-166..168, BC-5.01.007 mixed int/float Num semantics (154 BCs, S5 20), 12 stable ARCH-03 anchors, subagent entry point, harness argv field, VP-INDEX rebuilt (40 VPs, no one-sided links); sync check adv-p3 PASS, 4 warnings fixed; next ADV pass 4)"
phase: 1
phase_position: "RESUMED 2026-11-17. Phase 1 (spec crystallization), CI/CD done; phase-1-consistency-audit DONE 2026-11-17 (verdict PASS-WITH-FINDINGS, 0 CRITICAL / 0 HIGH / 4 MEDIUM / 8 LOW, all 12 fixed this burst); consistency re-check PASS 2026-11-17 (CR-01..03 fixed; CR-04 = 69 dependent artifacts hash-stale, deferred to check-input-drift pre-gate); phase-1-gate PASSED 2026-11-17 (orchestrator evaluation); phase-1d-adversarial-spec-review IN_PROGRESS 2026-11-17 — pass 1 recorded: 129 findings (21 HIGH / 63 MEDIUM / 40 LOW / 5 COSMETIC), NOT_CONVERGED, novelty HIGH; pass-1 fix burst DONE 2026-11-17 (~115/129 fixed; pass-1 owner questions ruled by OD-156..159); ADV pass 2 recorded 2026-11-17: 116 findings (17H/58M/35L/6C), NOT_CONVERGED, novelty MEDIUM; owner rulings OD-155..159 recorded (incl. OD-155 reopening OD-14: subagent panel rows in P1); pass-2 remediation burst DONE 2026-11-17 (rulings OD-160..165; contract count 145→153, VPs 38→40); ADV pass 3 recorded 2026-11-18: 150 findings (36H/61M/48L/5C), REGRESSION vs pass 2, root-caused (new scope added without pre-validation), NOT_CONVERGED, novelty MEDIUM; pass-3 remediation burst DONE 2026-11-18 (rulings OD-166..168 recorded; BC-5.01.007 mixed int/float Num semantics — contract count 153 → 154, S5 = 20; 12 stable ARCH-03 anchors, subagent entry point, harness argv field; VP-INDEX rebuilt — 40 VPs, no one-sided links; sync check adv-p3 PASS, 4 warnings fixed); next free OD-169; next: ADV pass 4 — Phase 1 IN_PROGRESS via the greenfield-pipeline sub-workflow (phase-1-spec-crystallization), scoped to P1 statusline; create-domain-spec DONE 2026-11-15; create-prd DONE 2026-11-15; create-architecture DONE 2026-11-16; parallel Phase 1 steps DONE 2026-11-16 (feasibility review, DTU assessment, gene-transfusion assessment); owner rulings OD-132..OD-154 recorded; phase-1-cicd-setup DONE 2026-11-16 (PR #1 merged; main @ fd031da; branch protection live); Phase 0 PASSED 2026-11-14"
pipeline: IN_PROGRESS
inputs: []
input-hash: "[live-state]"
traces_to: ""
project: hylo
product: hylo
mode: brownfield
current_step: "pass-3 fixes committed; next adversarial pass 4; D-chain cite D-446 latest brownfield; trajectory-tail →0→129→116→150"
current_cycle: "phase-1-spec-crystallization"
market_intel:
  recommendation: GO
  human_decision: approved
  notes: "P1 only. Owner rulings: (1) P1 success criterion = owner's own daily use (byte parity on the owner's setup); community adoption is a P6 concern. (2) README positioning 'lane-aware with backend telemetry and owned-hardware cost' + honest Alternatives section approved in principle, written at P6. (3) no stdin `version` session-cache key until after parity (D4). (4) `7d_oi` Fable-only claim stays a watch note, no work. feature_type = cli, so brownfield-design-system-extract is skipped (condition not met). Allocated OD-96..OD-100."
dtu_required: false
dtu_assessment: 2026-11-16
dtu_clones_built: n/a
dtu_services: []
---

<!-- STATE.md SIZE BUDGET (per D-421(c) + D-422(c) reconciliation): soft target <=200 lines; hard cap 500 lines (validate-state-md-size hook enforcement); Hard cap (500 lines) margin from soft-target = 500 - 200 = 300; margin from actual = 500 - 198 = 302 (D-446(c) dual-margin form). 198 lines (wc-l) at the 2026-11-18 pass-3 remediation. Historical content belongs in cycle files, NOT here. -->

# Pipeline State: hylo

## Project Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo: hybrid local + cloud model routing for Claude Code (Go port of a Python prototype) |
| **Mode** | brownfield (owner override, 2026-11-14): auto-detection would pick greenfield because there is no src/ |
| **Phase 0 source** | `legacy/` only (scrubbed Python/zsh prototype, read-only). Not the repo root, not any path outside the repo |
| **Port** | Python -> Go (`semport-analyze legacy go`) |
| **Phase 1 inputs** | `docs/PLAN.md` (decisions D1-D16, phases P0-P7), `docs/STATUSLINE-WIDGETS.md`, `docs/STATUSLINE-REVIEW-2026-11-13.md`, `CLAUDE.md` |
| **Default branch** | main (no develop) |
| **Last Updated** | 2026-11-18 — phase-1d pass-3 remediation DONE (~145 files): business-analyst (one agent broke down with garbled output and zero tool calls — nothing written; re-dispatched), product-owner (7 sub-bursts incl. the new BC-5.01.007 mixed int/float Num semantics) and architect (4 sub-bursts incl. the VP-INDEX rebuild) fixed the 150 pass-3 findings across domain-spec, product-brief, prd.md, prd-supplements, BCs (contract count 153 → 154; S5 = 20), architecture (12 stable ARCH-03 anchors, `--subagent` entry point, harness argv field), VPs (VP-INDEX rebuilt: 40 VPs, no one-sided links) and the cicd/dtu/gene-transfusion/feasibility docs; owner rulings OD-166..168 recorded (OD-166 a cost value that cannot convert to float is not recorded in the cost history, current refresh still degrades — named deviation under OD-156; OD-167 a transcript-borne overflow skips the line AND drops the in-flight turn; OD-168 a `--subagent` config error prints zero bytes on stdout and the error on stderr); new crash ids CP-O10, CP-O11 (cost segment), CP-A04, CP-A05 (subagent tokens/clock); sync check `sync-check-adv-p3-2026-11-18.md` verdict PASS with 4 warnings, all fixed; orchestrator re-verification (python scripts): 154 titles consistent across BC files/BC-INDEX/PRD, VP↔BC links consistent (3 prose-only mentions), no live 989 depth value, no CP-T08, non-English text only as CJK test data in width/Unicode vectors; next free OD-169; next: ADV pass 4; trajectory-tail →0→129→116→150. Superseded records: pass-3 record (150 findings 36H/61M/48L/5C, Δ +34 REGRESSION root-caused — new scope added without pre-validation; reports `adversarial-reviews/pass-3.md` + `ADV-P3-INDEX.md`); pass-2 record (116 findings; remediation DONE with rulings OD-155..165, contract count 145 → 153, VPs 38 → 40, depth limits measured end to end — stdin/transcript 993/994, session/mix cache 991/992, git cache/cost history 990/991, sync check SC-01..09 fixed). Full narratives: `cycles/phase-1-spec-crystallization/burst-log.md` |

## Owner Guardrails (standing; see policies.yaml 12-21)

1. **Commit / push / PR / merge only with explicit owner approval at that moment** (policy 15). The only exception is state-manager commits on `factory-artifacts`.
2. **Public repo.** `factory-artifacts` is published as an orphan branch on the public GitHub repo (owner decision 2026-11-15). Every factory push is scanned by the local pre-push hook (gitleaks + hygiene patterns + a local private-terms file) and blocked on any hit; factory history may never reach `main` or any other ref. Never use `--no-verify`. All factory content follows policy 21 (public_artifact_hygiene); public-bound product content follows policy 14.
3. **D1-D16 are settled** (policy 12). Adversary findings that challenge a decision become owner questions, not defects.
4. **Parity first** (D4, policy 13): BCs for statusline, exporter and proxy are extracted from `legacy/`; parity diffs are the acceptance criteria for P1-P3.
5. **Go hardening mapping** (policy 19) replaces Kani/cargo-fuzz/cargo-mutants.
6. **DTU candidates:** fake Anthropic upstream and fake local backend (OpenAI/Anthropic-compatible SSE) for proxy tests.
7. **Never touch the live prototype** or its backend from the pipeline. Phase 0 reads `legacy/` only.

## Phase Progress

| Phase | Status | Notes |
|-------|--------|-------|
| pre-0 initialization | **COMPLETE** | policies 12-19 + merge/autonomy config committed (47e4c37) |
| Phase 0 brownfield ingestion of `legacy/` | **PASSED 2026-11-14** (owner approval) — **analysis COMPLETE**: all six passes converged; coverage-audit PASS; extraction-validation r2 PASS-WITH-FIXES; final-synthesis DONE (pass-8) | Gate passed: OD list presented and ruled; next Phase 1 spec crystallization |
| Phases 1-7 (spec crystallization .. convergence) | Phase 1 **IN_PROGRESS** — greenfield-pipeline sub-workflow (phase-1-spec-crystallization); create-domain-spec DONE 2026-11-15; create-prd DONE 2026-11-15; create-architecture DONE 2026-11-16; parallel Phase 1 steps DONE 2026-11-16 (feasibility review, DTU assessment, gene-transfusion assessment) | product brief + domain spec product-level (OD-115); PRD/BCs/supplements P1-scoped (OD-131); later phases via Feature Mode; owner rulings OD-115..149; no design system (OD-100); PRD OQ-1..14 resolved (OD-132..145; OQ-3 deferred); feasibility review verdict 'PRD CHANGES REQUIRED: none'; phase-1-cicd-setup DONE (PR #1 merged; main @ fd031da, CI green on 3 OSes; branch protection live: lint, test ubuntu-24.04, test macos-15, test windows-2025, gitleaks full history; strict; enforce_admins false; force-push/deletion blocked); consistency re-check PASS + phase-1-gate PASSED 2026-11-17; phase-1d ADV pass 1 recorded 2026-11-17 (129 findings: 21H/63M/40L/5C, NOT_CONVERGED, novelty HIGH); pass 2 recorded 2026-11-17 (116 findings: 17H/58M/35L/6C, Δ −13, NOT_CONVERGED, novelty MEDIUM); owner rulings OD-155..165 recorded; pass-2 remediation DONE 2026-11-17 (sync check clean); pass 3 recorded 2026-11-18 (150 findings: 36H/61M/48L/5C, Δ +34 REGRESSION root-caused, NOT_CONVERGED, novelty MEDIUM); pass-3 remediation DONE 2026-11-18 (rulings OD-166..168; contract count 153 → 154 incl. BC-5.01.007; VP-INDEX rebuilt — 40 VPs; sync check adv-p3 PASS); next: ADV pass 4 |
| Adversary passes (Phase 0) | **ALL SIX CONVERGED** | round record + extracted detail in `cycles/phase-0-ingestion/convergence-trajectory.md` (## Extracted from STATE.md on 2026-11-17); trajectory-tail →0→0→0→0 placeholder retained for the formal finding series |
| Fix bursts (Phase 0) | **NONE** | extracted detail in `cycles/phase-0-ingestion/burst-log.md` |

## Current Phase Steps (last 5)

| # | Step | Outcome |
|---|------|---------|
| 29 | phase-1d ADV pass-3 remediation DONE (~145 files): business-analyst (one agent broke down with garbled output and zero tool calls, nothing written — re-dispatched), product-owner (7 sub-bursts incl. the new BC-5.01.007 mixed int/float Num semantics) and architect (4 sub-bursts incl. the VP-INDEX rebuild) fixed the 150 pass-3 findings across domain-spec, product-brief, prd.md, prd-supplements, BCs (153 → 154; S5 = 20), architecture (12 stable ARCH-03 anchors, `--subagent` entry point, harness argv field), VPs (VP-INDEX rebuilt: 40 VPs, no one-sided links) and the cicd/dtu/gene-transfusion/feasibility docs; owner rulings OD-166..168 recorded (owner chose the recommended option); new crash ids CP-O10, CP-O11 (cost segment), CP-A04, CP-A05 (subagent tokens/clock); sync check `sync-check-adv-p3-2026-11-18.md` verdict PASS with 4 warnings, all fixed; orchestrator re-verification clean (154 titles consistent across BC files/BC-INDEX/PRD; VP↔BC links consistent, 3 prose-only mentions; no live 989 depth value; no CP-T08; CJK only as test data in width/Unicode vectors) | COMPLETE — current_step = pass-3 fixes committed; next adversarial pass 4 |
| 28 | phase-1d adversarial spec review PASS 3 recorded: same six fresh-context perimeters (A/A2/B/C/C2/D), final messages extracted verbatim; 150 findings (36 HIGH / 61 MEDIUM / 48 LOW / 5 COSMETIC; Δ +34 vs pass 2 — REGRESSION, investigated before continuing per the adversarial-review trajectory-monotonicity rule); per-perimeter novelty A MEDIUM, A2 MEDIUM-HIGH, B MEDIUM, C HIGH, C2 MEDIUM, D HIGH; root cause (orchestrator analysis): pass-2 remediation added new scope without pre-validation — OD-155 (8 new BC-1.07 `--subagent` BCs) and rulings OD-156..165 not yet propagated to harness, oracle, SS-02 config contracts, SS-05 consumer lists, L2; ARCH-06 signature canon not propagated to BC-5.04.002/003; escape-decoding uXXXX corruption in expected-output cells; most pre-existing content shows refinements only; verbatim reports `cycles/phase-1-spec-crystallization/adversarial-reviews/pass-3.md` + index `ADV-P3-INDEX.md` (rows cross-checked: A 29, A2 27, B 18, C 22, C2 14, D 40) | COMPLETE — current_step = owner questions + fix burst, then ADV pass 4 |
| 27 | phase-1d ADV pass-2 remediation DONE (~144 files): business-analyst, product-owner (7 sub-bursts incl. 8 new BC-1.07.001..008 for `--subagent` per OD-155) and architect (6 sub-bursts incl. the VP-INDEX rebuild) fixed the 116 pass-2 findings across domain-spec, product-brief, prd.md, prd-supplements, BCs, architecture, VPs (VP-039/040 minted) and cicd/dtu/gene-transfusion/feasibility docs; rulings OD-155..165 applied, new rulings OD-160..165 recorded (closed exclusion set now 10 ids); JSON depth limits measured end to end on the real legacy program (isolated HOME): 999 − Python frames to raw_decode — stdin/transcript 993/994, session/mix cache 991/992, git cache/cost history 990/991 (three sites measured, rest derived); contract count 145 → 153, VP count 38 → 40; sync check `sync-check-adv-p2-2026-11-18.md` initial verdict FAIL (SC-01..09), all nine fixed; orchestrator re-verification clean (VP bcs ↔ BC citations consistent incl. 3 prose-only mentions, no live 989 depth value, no stray characters, no Rust vocabulary) | COMPLETE — current_step = pass-2 fixes committed; next adversarial pass 3 |
| 25 | phase-1d ADV pass-1 remediation DONE: ~115 of 129 findings fixed by business-analyst, product-owner (4 parallel sub-bursts + 4 follow-ups) and architect (2 parallel + 3 follow-ups) across domain-spec, prd.md, product-brief.md, prd-supplements, BCs ss-01..ss-06 (+BC-INDEX, BC-ALLOCATION), architecture, VPs incl. new VP-038 (bijective 38 VP x 145 BC re-checked), cicd-setup, dtu/gene-transfusion/feasibility docs; ~45 Python vector cells re-run on CPython 3.11.7 (8 wrong, corrected); transcript depth re-measured 989/990; 4 findings held as owner questions (OverflowError C01/B05/B06; ±Inf/OD-130 A2-01 + VP-030 claim; coverage-vs-mutation 95% A08; Windows encoding B08/C06) — next free OD-155; sync check `sync-check-adv-p1-2026-11-17.md` initial verdict FAIL (SC-01..07), all fixed afterwards | COMPLETE — current_step = pass-1 fixes committed; next adversarial pass 2 |
| 26 | phase-1d adversarial spec review PASS 2 recorded: same six fresh-context perimeters (A/A2/B/C/C2/D), each resumed once after a transient API error — final messages extracted verbatim; 116 findings (17 HIGH / 58 MEDIUM / 35 LOW / 6 COSMETIC; Δ −13 vs pass 1), per-perimeter novelty A HIGH, A2 HIGH, B/C/C2/D MEDIUM, verdict NOT_CONVERGED; verbatim reports `cycles/phase-1-spec-crystallization/adversarial-reviews/pass-2.md` + index `ADV-P2-INDEX.md` (116 rows cross-checked); owner rulings OD-155..159 recorded 2026-11-17 — OD-155 subagent panel rows in P1 (supersedes OD-14 a), OD-156 OverflowError by source, OD-157 ±Inf/OD-130 after cutover, OD-158 coverage gate 95% line coverage, OD-159 UTF-8 named deviation — GitHub-email open item closed (both on); next free OD-160 | COMPLETE — current_step = ADV pass 2 fix burst incl. OD-155..159, then pass 3 |

## Convergence Status

- **All six passes CONVERGED** (Phase 0: 0:3 1:3 2:9 3:8 4:7 5:5). Round record + extracted detail: `cycles/phase-0-ingestion/convergence-trajectory.md` ("## Extracted from STATE.md on 2026-11-17"). Phase 1d ADV pass 1 recorded 2026-11-17: 129 findings (21H/63M/40L/5C), NOT_CONVERGED, novelty HIGH — `cycles/phase-1-spec-crystallization/adversarial-reviews/`. Pass 2 recorded 2026-11-17: 116 findings (17H/58M/35L/6C), NOT_CONVERGED, novelty MEDIUM; pass-2 remediation DONE same day (rulings OD-155..165 applied; contract count 145 → 153, VPs 38 → 40). Pass 3 recorded 2026-11-18: 150 findings (36H/61M/48L/5C), NOT_CONVERGED, novelty MEDIUM — REGRESSION (Δ +34, HIGH 17 → 36), investigated per the trajectory-monotonicity rule; root cause: pass-2 remediation added new scope without pre-validation; pass-3 remediation DONE 2026-11-18 (rulings OD-166..168; contract count 153 → 154, BC-5.01.007; VP-INDEX rebuilt — 40 VPs; sync check adv-p3 PASS, 4 warnings fixed); next: ADV pass 4.

## Canonical Phase 1 Inputs (pointer table)

| Artifact | Canonical source |
|----------|------------------|
| Inventory | pass-0 r3 §2 — `semport/hylo-legacy/hylo-legacy-pass-0-deep-inventory-r3.md` |
| Architecture | pass-1 r3 §B, two Mermaid diagrams — `hylo-legacy-pass-1-deep-architecture-r3.md` |
| Domain | pass-2 r8 §7, amended by r9 — `hylo-legacy-pass-2-deep-domain-r8.md` |
| BC index | pass-3 r4, amended by r5-r8 — 232 BCs (legacy pass-3 catalogue, not the 153 P1 BCs) — `hylo-legacy-pass-3-deep-behavioral-contracts-r4.md` |
| Thresholds / NFR | pass-4 r7 final catalogue — 147 thresholds; 120 rationales resolved; OD-57 (18 bulk-confirm + 27 owner-rationale in 7 groups); OD-94 fact sheet — `hylo-legacy-pass-4-deep-nfr-r7.md` |
| Conventions / env / determinism / pitfalls | pass-5 r3 consolidated, amended by r4-r5 — 43 explicit + 21 implicit env inputs; 54 determinism rows + 6 Go-side pins; 19 conventions; 22 pitfalls — `hylo-legacy-pass-5-deep-conventions-r3.md` |
| Synthesis (definitive) | pass-8 deep synthesis — supersedes pass-6; primary reference for create-brief / create-domain-spec / create-prd / semport-analyze — `hylo-legacy-pass-8-deep-synthesis.md` |
| Owner decision list (gate input) | 64 issued ODs in groups A-F; one recommendation + evidence per item; answer format in the file header — `hylo-legacy-owner-decisions.md` |
| Market intel (GO, approved) | `planning/market-intel.md` |
| Porting decision (needs_semport true; Python 3 + zsh -> Go 1.26) | `brownfield/porting-decision.md` |
| Semport target design (P1 status line; 103/103 BCs; tensions resolved) | `semport/hylo-legacy/statusline-target-design.md` + companion `semport/hylo-legacy/semport-assessment.md` |

Registers (BC index totals, statement partition, retractions, extraction-validation evidence, trajectory-tail): extracted to `cycles/phase-0-ingestion/convergence-trajectory.md` ("## Extracted from STATE.md on 2026-11-17").

## Decisions Log

Engine-level decisions live in `docs/PLAN.md` (owner decisions) and the plugin decision log; this table records pipeline-level decisions taken in this factory:

| Decision | Content | Source | Date |
|----------|---------|--------|------|
| D13 | Intercept all Claude Code traffic | docs/PLAN.md on main (b99082e) | 2026-11-14 |
| D14 | Proxy settings do not leak to child processes | docs/PLAN.md on main (b99082e); mechanism chosen in P4 | 2026-11-14 |
| D15 | Config over code iron rule | docs/PLAN.md + CLAUDE.md working tree; enforced via policy 20 | 2026-11-14 |
| policy 20 | config_over_code policy entry (policies.yaml v1.2) | this factory, grounding burst | 2026-11-14 |
| post-scrub publish | factory-artifacts history scrubbed and rewritten 2026-11-15 (owner-approved): private details removed, logs/ untracked and gitignored, stale SHA citations remapped to post-rewrite SHAs; pre-scrub tag (pre-scrub-2026-11-15) kept local, never pushed; branch to be published on the public repository as an orphan branch; policy 21 public_artifact_hygiene adopted | owner ruling at session wrap | 2026-11-15 |

## Open Owner Questions

- OD numbering: OD-01..OD-168 allocated (Phase 0 gate list + 2026-11-15 market-intel review + porting-tension rulings OD-101..106 + semport-tension rulings OD-107..114 + Phase 1 scope rulings OD-115..117 + domain-spec validation rulings OD-118..130 + PRD subsystem-breakdown ruling OD-131 + PRD open-question rulings OD-132..145 + architecture rulings OD-146..149 + CI/CD landing ruling OD-150 + CI/CD merge rulings OD-151 + consistency-audit fix rulings OD-152..154 + phase-1d pass-2 rulings OD-155..159 + pass-2 remediation rulings OD-160..165 + pass-3 remediation rulings OD-166..168); next free OD-169 — log: `specs/owner-decisions-log-2026-11-14.md`.
- PRD open questions OQ-1..OQ-14 (prd.md §10) RESOLVED 2026-11-15 by owner rulings OD-132..OD-145 (OQ-3 deferred) — create-architecture gate cleared.
- Optional checks (deferred, non-blocking): Grafana per-session cost panel; offline promtool rule validation.
- Policy risk (owner awareness): Anthropic Usage Policy 2026-11-12 language on routing through consumer subscriptions.

## Concurrent Cycles

| Cycle | Type | Status | Notes |
|-------|------|--------|-------|
| phase-0-ingestion | brownfield-ingestion | **COMPLETE** — Phase 0 PASSED 2026-11-14; analysis converged; artifacts serve as Phase 1 context (pointer table above); transition to the greenfield sub-workflow performed 2026-11-15 | Commits: dff1f56 (passes 2-3) + be38c50 (passes 0/1/4/5) + 5e83b63 (porting rulings) + this burst (semport design, OD-107..114, transition; create-brief + OD-115..117; domain-spec + OD-118..130) |
| phase-1-spec-crystallization | spec-crystallization (greenfield-pipeline sub-workflow) | **IN_PROGRESS** — opened 2026-11-15; directory created retroactively 2026-11-17 | scope P1 statusline (OD-131); brief, domain-spec, PRD (154 BCs ss-01..ss-06 incl. BC-1.07 and BC-5.01.007), architecture (13 ADRs, 40 VPs), parallel steps, CI/CD DONE; phase-1-consistency-audit DONE 2026-11-17 (PASS-WITH-FINDINGS, 0C/0H/4M/8L, all fixed); re-check PASS + phase-1-gate PASSED 2026-11-17; phase-1d ADV passes 1-3 recorded (129 → 116 → 150 findings; pass 3 a REGRESSION, root-caused: pass-2 scope added without pre-validation); pass-2 remediation DONE 2026-11-17 (rulings OD-155..165 applied; sync check clean); pass-3 remediation DONE 2026-11-18 (rulings OD-166..168; sync check adv-p3 PASS); next: ADV pass 4; manifest: `cycles/phase-1-spec-crystallization/cycle-manifest.md` |

## Session Resume Checkpoint (2026-11-17 — SESSION-WRAP-PAUSE)

> **SELF-SUFFICIENT RESUME CONTEXT** — read this section alone to resume after a session CLEAR.

### Where We Are

- Position: Phase 1 **IN PROGRESS** (greenfield-pipeline sub-workflow after the brownfield-to-greenfield transition), scoped to P1 = `hylo statusline`. Phase 0 PASSED 2026-11-14.
- DONE this session (2026-11-15..17): market intel GO (P1); porting decision; semport target design + validation; brownfield->greenfield transition; product brief (product-level); L2 domain spec (product-level); P1 PRD (154 BCs S1-S6 incl. BC-1.07 + supplements + BC-INDEX); architecture (ARCH-00..09, 13 ADRs, 40 VPs; VP↔BC citations re-verified after the `--subagent` BCs); feasibility review (no PRD changes); DTU assessment (DTU_REQUIRED false); gene-transfusion assessment; CI/CD (PR #1 merged; main fd031da; branch protection live); consistency audit + fix burst CA-01..12 (OD-152..154); consistency re-check PASS; phase-1-gate PASSED 2026-11-17; phase-1d ADV pass-2 remediation DONE (rulings OD-155..165 applied; sync check clean).
- NEXT: phase-1d adversarial spec review (>=3 clean passes; inject .factory/policies.yaml incl. policy 21), phase-1d second-model spec review, phase-1-state-backup, check-input-drift, phase-1-human-approval.

### Convergence

- None active this minute. Phase 1d ADV pass 1 recorded 2026-11-17: 129 findings (21H/63M/40L/5C), NOT_CONVERGED, novelty HIGH; pass 2 recorded 2026-11-17: 116 findings (17H/58M/35L/6C), NOT_CONVERGED, novelty MEDIUM; pass 3 recorded 2026-11-18: 150 findings (36H/61M/48L/5C), REGRESSION vs pass 2 (Δ +34), root-caused (OD-155/OD-156..165 scope added without pre-validation; ARCH-06 signature canon; uXXXX escape corruption), NOT_CONVERGED. Phase 0 passes converged 0:3 1:3 2:9 3:8 4:7 5:5.

### In Flight

- None. No sub-agents running; nothing abandoned. Public main fd031da (protected; CI green on 3 OSes). factory-artifacts = this commit. (Note: the pass-3 session saw several subagent breakdowns — looping or early stops; every case verified on disk, nothing lost — prefer short, tightly scoped briefs.)

### Pending Owner Decisions

1. PUBLIC DOC EDITS PENDING (PLAN D15 exception OD-101, D4-EX-3 OD-102) — commit to public main only when the owner asks.
2. REVISIT AT P7 — OD-125 (VALID-08): DI-007 "the status line never reads the ledger" stands for now; revisit during the P7 ledger redesign (flag in `specs/domain-spec/invariants.md`).
3. Three [process-gap] lessons (merge-commit author check, CI identity check, never quote flagged text) recorded as Drift Items, target before Phase 3 (L-PG-01..03 in `cycles/phase-0-ingestion/lessons.md`).
4. Six deferred PR #1 findings recorded in `code-delivery/phase-1-cicd-setup/review-findings.md`.
5. CLAUDE_AUTOCOMPACT_PCT_OVERRIDE advisory (add 70 to .claude/settings.json) — handled separately from the 2026-11-17 housekeeping burst, which resolved the other check-state-health warnings (status: draft, missing Phase 1 cycle directory, STATE.md 200+ lines).
6. Next free OD = OD-169 (log: `specs/owner-decisions-log-2026-11-14.md`). Former item 'Owner to confirm GitHub email settings' closed 2026-11-17: both settings on.

No blockers.

### WIP Branches

- None (ci/phase-1-setup merged and deleted).

### Resume

Open a new session in the hylo repo, read docs/RESUME.md, CLAUDE.local.md and .factory/STATE.md, then run /vsdd-factory:rehydrate-wave and then /vsdd-factory:next-step.

## Drift Items (deferred; target: before Phase 3)

| Item | Lesson | Target |
|------|--------|--------|
| PR process must verify the author/committer of the commit GitHub creates at merge | `cycles/phase-0-ingestion/lessons.md` L-PG-01 [process-gap] | before Phase 3 |
| CI must check that every author and committer on main is the GitHub no-reply address | `cycles/phase-0-ingestion/lessons.md` L-PG-02 [process-gap] | before Phase 3 |
| Documents explaining a scanner false positive must describe, never quote, the flagged text | `cycles/phase-0-ingestion/lessons.md` L-PG-03 [process-gap] | before Phase 3 |
| BC vectors carrying Python results must be machine-checked against the oracle interpreter when written (ASM-001 claimed oracle-verified; 8 of ~45 cells wrong) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-04 [process-gap] | before Phase 2 |
| Plugin-template Rust vocabulary (proptest, Send + Sync) must be adapted to the target language at instantiation (leaked into 60+ Go spec files) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-05 [process-gap] | before Phase 2 |
| Legacy-oracle runs from agent briefs must force an isolated HOME and cwd (a synthetic entry landed in the live prototype's cost-history cache; removed, live file verified intact) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-06 [process-gap] | before Phase 2 |
| Oracle facts (JSON depth limits et al.) must be measured on the real program end to end, not via wrapper probes (two agents reported 989/990 vs 993/994) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-07 [process-gap] | before Phase 2 |
| Finding ids are minted by one owner before parallel dispatch; parallel agents consume an allocation (CP-T08 vs CP-O06..08 collided for one crash class) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-08 [process-gap] | before Phase 2 |
| Non-ASCII expected bytes in BC vectors must be written as \uXXXX escapes and verified on disk by script (escape-decoding corrupted valid escapes into raw characters) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-09 [process-gap] | before Phase 2 |
| Character/non-English scans of committed specs must run as python scripts (a grep -P scan through a shell function wrapping ugrep silently matched nothing) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-10 [process-gap] | before Phase 2 |
| Line-number facts in agent briefs must come from a numbered read — awk/sed -n with NR (a misread SL:1238 vs the actual SL:1240 propagated into specs) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-11 [process-gap] | before Phase 2 |
| After adding new scope, run the sync check before the next adversarial pass (pass 3 regressed 116 → 150 on unpropagated OD-155/OD-156..165 scope) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-12 [process-gap] | before Phase 2 |

## Skip Log

| Step | Skipped | Justification |
|------|---------|---------------|
| brownfield-design-system-extract | 2026-11-15 | OD-100: feature_type = cli — design-system extraction condition not met; this factory runs with no design system |
| prd-revision | 2026-11-16 | closed as a no-op: the Architect's feasibility review now exists (`specs/architecture-feasibility-report.md`) and its verdict is 'PRD CHANGES REQUIRED: none' — no PRD revision required |
| UX/design-system steps (create-ux-spec, design-system) | 2026-11-16 | OD-100: feature_type = cli — this factory runs with no design system, and the P1 statusline scope has no UX-spec artifact; the steps add no artifact at this altitude |

## Historical Content

| Content | Location |
|---------|----------|
| Burst narratives, convergence records, lessons, session checkpoints | `cycles/phase-0-ingestion/` (burst-log.md, convergence-trajectory.md, cycle-manifest.md, session-checkpoints.md) |
| Phase 1 cycle artifacts (manifest, burst log, trajectory, checkpoints, lessons) | `cycles/phase-1-spec-crystallization/` |
| Phase 0 Convergence Status, adversary-pass row detail, Registers paragraph (extracted 2026-11-17) | `cycles/phase-0-ingestion/convergence-trajectory.md` — "## Extracted from STATE.md on 2026-11-17" |
| Owner decision rulings 2026-11-14, fix-burst row detail, Research section detail (extracted 2026-11-17) | `cycles/phase-0-ingestion/burst-log.md` — "## Extracted from STATE.md on 2026-11-17" |
| Project Metadata "Last Updated" narrative, phase-1 sessions 2026-11-15..17 | `cycles/phase-1-spec-crystallization/burst-log.md` |

## Blocking Issues

None.
