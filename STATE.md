---
document_type: pipeline-state
level: ops
version: "2.4"
status: in_progress
producer: state-manager
timestamp: 2026-11-18T11:11:02Z
last_amended: "2026-11-18 (v2.12 — state-manager — phase-1d pass-7 recording + remediation burst: ADV pass 7 recorded 114 findings (14H/47M/49L/4C, Δ −10, HIGH 27 → 14, perimeter A2 zero HIGH first time), NOT_CONVERGED, novelty MEDIUM; remediation DONE — rulings OD-188..192 incl. OD-188 rename_retry_limit and OD-192 ASM-007 owner capture before Phase 2 S1.07, 154 BCs, 41 VPs, crash register 48 paths (CP-T09 minted, CP-T08 retired), VP↔BC bcs: edges 261, sync check adv-p7 PASS-WITH-FINDINGS with all 114 closed / 0 open and SC-29..31 closed; lessons L-PG-23..26; next ADV pass 8 — OD-176 needs 3 consecutive cosmetic-only passes, 0 so far)"
phase: 1
phase_position: "RESUMED 2026-11-17. Phase 1 (spec crystallization), CI/CD done; phase-1-consistency-audit DONE 2026-11-17 (PASS-WITH-FINDINGS, all 12 fixed); re-check PASS + phase-1-gate PASSED 2026-11-17; phase-1d-adversarial-spec-review IN_PROGRESS 2026-11-17 — ADV passes 1-7 all NOT_CONVERGED: 1 (129 findings, novelty HIGH), 2 (116: 17H/58M/35L/6C, MEDIUM), 3 (150: 36H/61M/48L/5C — REGRESSION root-caused: pass-2 scope added without pre-validation), 4 (133: 39H/57M/32L/5C — Δ −17 but HIGH 36 → 39 sibling-propagation), 5 (148: 24H/75M/43L/6C — Δ +15, HIGH fell sharply), 6 (124: 27H/52M/38L/7C — Δ −24, largest total drop of the series), 7 (114: 14H/47M/49L/4C — Δ −10, HIGH 27 → 14, A2 zero HIGH first time); remediation after each pass: pass-1 fix burst DONE 2026-11-17 (~115/129 fixed; OD-156..159); pass-2 DONE 2026-11-17 (OD-160..165; contracts 145 → 153, VPs 38 → 40); pass-3 DONE 2026-11-18 (OD-166..168; BC-5.01.007 — contracts 153 → 154; VP-INDEX rebuilt 40 VPs); pass-4 DONE 2026-11-17 (OD-169..175; 41 VPs incl. VP-041; crash register 47 paths, CP-N03; SC-05..12 closed); pass-5 DONE 2026-11-18 (OD-176..180; 7th D4-EX-3 class Text; SC-13..20 closed; lessons L-PG-17..19); pass-6 DONE 2026-11-18 (OD-181..187 — transport exclusion closes the set at 12 ids, VP Go sketches non-normative, UTF-8 stdio, 1-code-point glyphs, CI 3.11.x + self-check, rename_retry_delay_ms, conditional timing exemption; sync check adv-p6 PASS-WITH-FINDINGS, SC-21..28 closed; lessons L-PG-20..22); pass-7 DONE 2026-11-18 (OD-188..192 — rename_retry_limit, dead-backend marker keys, UTF-8 + LF, 100 ms timing-fixture ceiling, ASM-007 owner capture before Phase 2 S1.07; crash register 47 → 48 paths, CP-T09 minted / CP-T08 retired; VP↔BC bcs: edges 261; sync check adv-p7 PASS-WITH-FINDINGS — 114 closed / 0 open, SC-29..31 closed; lessons L-PG-23..26); next free OD-193; next: ADV pass 8 (OD-176: 3 consecutive cosmetic-only passes to converge — 0 so far) — Phase 1 IN_PROGRESS via the greenfield-pipeline sub-workflow (phase-1-spec-crystallization), scoped to P1 statusline; create-domain-spec DONE 2026-11-15; create-prd DONE 2026-11-15; create-architecture DONE 2026-11-16; parallel Phase 1 steps DONE 2026-11-16 (feasibility review, DTU assessment, gene-transfusion assessment); owner rulings OD-132..OD-154 recorded; phase-1-cicd-setup DONE 2026-11-16 (PR #1 merged; main @ fd031da; branch protection live); Phase 0 PASSED 2026-11-14"
pipeline: IN_PROGRESS
inputs: []
input-hash: "[live-state]"
traces_to: ""
project: hylo
product: hylo
mode: brownfield
current_step: "pass-7 fixes committed; next adversarial pass 8 (OD-176: 3 consecutive cosmetic-only passes to converge — 0 so far); D-chain cite D-446 latest brownfield; trajectory-tail →150→133→148→124→114"
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

<!-- STATE.md SIZE BUDGET (per D-421(c) + D-422(c) reconciliation): soft target <=200 lines; hard cap 500 lines (validate-state-md-size hook enforcement); Hard cap (500 lines) margin from soft-target = 500 - 200 = 300; margin from actual = 500 - 200 = 300 (D-446(c) dual-margin form). 200 lines (wc-l) at the 2026-11-18 pass-7 recording + remediation. Historical content belongs in cycle files, NOT here. -->

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
| **Last Updated** | 2026-11-18 — phase-1d ADV pass 7 recorded 2026-11-18 (six fresh-context perimeters; 114 findings 14H/47M/49L/4C; Δ −10 vs pass 6 with HIGH 27 → 14 and perimeter A2 filing zero HIGH for the first time; novelty MEDIUM; reports `adversarial-reviews/pass-7.md` + `ADV-P7-INDEX.md`) and remediation DONE same burst across domain-spec, prd.md, prd-supplements, BCs, architecture, VPs and the assessment/cicd docs; owner rulings OD-188..OD-192 recorded (OD-188 config key `statusline.cache.rename_retry_limit` Int default 2 range 0..10; OD-189 dead-backend marker reuses `statusline.pill.label_local` + new Text keys `statusline.labels.vllm_down`/`statusline.labels.lmcache_down`/`statusline.subagent.name_fallback`; OD-190 LF line endings on every OS extending OD-183; OD-191 >512 KB timing fixture exempt from the 25 ms target but gated at 100 ms p95; OD-192 ASM-007 owner capture into git-ignored `captures/` before Phase 2 writes the S1.07 stories; next free OD-193); counts now 154 BCs, 41 VPs, crash register 48 paths (CP-T09 minted, CP-T08 retired), VP↔BC `bcs:` edges re-machine-checked at 261; sync check `sync-check-adv-p7-2026-11-18.md` verdict PASS-WITH-FINDINGS — all 114 pass-7 findings verified CLOSED on disk, 0 OPEN, and SC-29..SC-31 closed; lessons L-PG-23..26 codified; next: ADV pass 8 (OD-176: three consecutive cosmetic-only passes to converge — 0 so far); trajectory-tail →150→133→148→124→114. Full narratives: `cycles/phase-1-spec-crystallization/burst-log.md` |

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
| Phases 1-7 (spec crystallization .. convergence) | Phase 1 **IN_PROGRESS** — greenfield-pipeline sub-workflow (phase-1-spec-crystallization); create-domain-spec DONE 2026-11-15; create-prd DONE 2026-11-15; create-architecture DONE 2026-11-16; parallel Phase 1 steps DONE 2026-11-16 (feasibility review, DTU assessment, gene-transfusion assessment) | product brief + domain spec product-level (OD-115); PRD/BCs/supplements P1-scoped (OD-131); later phases via Feature Mode; owner rulings OD-115..149; no design system (OD-100); PRD OQ-1..14 resolved (OD-132..145; OQ-3 deferred); feasibility review verdict 'PRD CHANGES REQUIRED: none'; phase-1-cicd-setup DONE (PR #1 merged; main @ fd031da, CI green on 3 OSes; branch protection live: lint, test ubuntu-24.04, test macos-15, test windows-2025, gitleaks full history; strict; enforce_admins false; force-push/deletion blocked); consistency re-check PASS + phase-1-gate PASSED 2026-11-17; phase-1d ADV passes 1-7 recorded (129 → 116 → 150 → 133 → 148 → 124 → 114 findings; pass 3 a REGRESSION, root-caused: pass-2 scope added without pre-validation; pass 4 Δ −17 but HIGH 36 → 39, sibling-propagation; pass 5 Δ +15 with HIGH 39 → 24; pass 6 Δ −24; pass 7 Δ −10 with HIGH 27 → 14, A2 zero HIGH first time); owner rulings OD-155..165 recorded; pass-2 remediation DONE 2026-11-17 (sync check clean); pass-3 remediation DONE 2026-11-18 (rulings OD-166..168; contract count 153 → 154 incl. BC-5.01.007; VP-INDEX rebuilt — 40 VPs; sync check adv-p3 PASS); pass-4 remediation DONE 2026-11-17 (rulings OD-169..175; 41 VPs incl. VP-041; crash register 47 paths, CP-N03; sync check adv-p4 PASS-WITH-FINDINGS, SC-05..12 closed); pass-5 remediation DONE 2026-11-18 (rulings OD-176..180; 7 D4-EX-3 classes / 5 canonical tests; sync check adv-p5 PASS-WITH-FINDINGS, SC-13..20 closed); pass-6 remediation DONE 2026-11-18 (rulings OD-181..187; closed set 12 ids; sync check adv-p6 PASS-WITH-FINDINGS, SC-21..28 closed); pass-7 remediation DONE 2026-11-18 (rulings OD-188..192; crash register 48 paths; VP↔BC edges 261; sync check adv-p7 PASS-WITH-FINDINGS — 114 closed / 0 open, SC-29..31 closed); next: ADV pass 8 |
| Adversary passes (Phase 0) | **ALL SIX CONVERGED** | round record + extracted detail in `cycles/phase-0-ingestion/convergence-trajectory.md` (## Extracted from STATE.md on 2026-11-17); trajectory-tail →0→0→0→0 placeholder retained for the formal finding series |
| Fix bursts (Phase 0) | **NONE** | extracted detail in `cycles/phase-0-ingestion/burst-log.md` |

## Current Phase Steps (last 5)

| # | Step | Outcome |
|---|------|---------|
| 37 | phase-1d ADV pass-7 remediation DONE: fixes executed per `pass-7-remediation-plan.md` (calls 1-15) across domain-spec, prd.md, prd-supplements, BCs, architecture, VPs and the assessment/cicd docs; owner rulings OD-188..OD-192 recorded (OD-188 `statusline.cache.rename_retry_limit` Int default 2 range 0..10; OD-189 dead-backend marker reuses `statusline.pill.label_local`, new Text keys `statusline.labels.vllm_down`/`lmcache_down`/`statusline.subagent.name_fallback`; OD-190 LF line endings on every OS; OD-191 >512 KB fixture exempt from the 25 ms target but gated at 100 ms p95; OD-192 ASM-007 owner capture into git-ignored `captures/` before Phase 2 S1.07 story writing); crash register 47 → 48 paths (CP-T09 minted, CP-T08 retired); VP↔BC `bcs:` edges re-machine-checked at 261; sync check `sync-check-adv-p7-2026-11-18.md` PASS-WITH-FINDINGS — all 114 findings CLOSED, 0 OPEN, SC-29..31 closed; lessons L-PG-23..26 codified | COMPLETE — current_step = pass-7 fixes committed; next adversarial pass 8 |
| 36 | phase-1d adversarial spec review PASS 7 recorded 2026-11-18: same six fresh-context perimeters (A/A2/B/C/C2/D), final messages extracted verbatim; 114 findings (14 HIGH / 47 MEDIUM / 49 LOW / 4 COSMETIC; Δ −10 vs pass 6; HIGH 27 → 14; perimeter A2 reported zero HIGH for the first time); per-perimeter counts A 22, A2 22, B 15, C 14, C2 14, D 27; pass-level novelty MEDIUM; orchestrator spot-verified six findings on disk and against CPython 3.11.7, all held; reports `adversarial-reviews/pass-7.md` + `ADV-P7-INDEX.md` (114 rows cross-checked) | COMPLETE — current_step = owner rulings + fix burst, then ADV pass 8 |
| 35 | phase-1d ADV pass-6 remediation DONE: fixes executed per `pass-6-remediation-plan.md` (calls 1-16) across domain-spec, prd.md, prd-supplements, BCs, architecture, VPs and the cicd/dtu/feasibility docs; owner rulings OD-181..OD-187 recorded (OD-181 metrics-transport exclusion id — closed set now 12 ids; OD-182 VP Go sketches labelled non-normative; OD-183 UTF-8 stdio, Windows oracle PYTHONIOENCODING=utf-8; OD-184 glyph members = 1 code point, sparkline = 8; OD-185 CI stays 3.11.x, harness self-checks measured constants; OD-186 temp-file widened + `statusline.cache.rename_retry_delay_ms` Int default 10 range 1..1000; OD-187 VP-036 timing-fixture exemption conditional); counts 154 BCs, 41 VPs, 12 exclusion ids, 7 D4-EX-3 classes / 5 canonical tests; sync check `sync-check-adv-p6-2026-11-18.md` PASS-WITH-FINDINGS, all 8 findings SC-21..SC-28 closed | COMPLETE — current_step = pass-6 fixes committed; next adversarial pass 7 |
| 34 | phase-1d adversarial spec review PASS 6 recorded 2026-11-18: same six fresh-context perimeters (A/A2/B/C/C2/D), final messages extracted verbatim; 124 findings (27 HIGH / 52 MEDIUM / 38 LOW / 7 COSMETIC; Δ −24 vs pass 5 — the largest total drop of the series; HIGH 24 → 27); per-perimeter counts A 19, A2 30, B 16, C 17, C2 15, D 27; pass-level novelty MEDIUM; reports `adversarial-reviews/pass-6.md` + `ADV-P6-INDEX.md` (124 rows cross-checked) | COMPLETE — current_step = owner rulings + fix burst, then ADV pass 7 |
| 33 | phase-1d ADV pass-5 remediation DONE: fixes executed per `pass-5-remediation-plan.md` across domain-spec, product-brief, prd.md, prd-supplements, BCs, architecture, VPs and the cicd/dtu/gene-transfusion/feasibility docs; owner rulings OD-176..OD-180 recorded (OD-176 keeps the full VSDD convergence standard — every finding of every severity fixed each pass, three consecutive cosmetics-only passes to converge; no severity gate, no scope freeze; OD-177 libc TZ semantics refining OD-171; OD-178 seventh D4-EX-3 class **Text** with canonical tests TestD4EX3_Boolean/_Enum/_URL/_Number/_Text; OD-179 `statusline.lane.reroute_all_prefixes` List key; OD-180 metrics URL with userinfo reproduces legacy no-sample dead rung — no new exclusion id, closed set stays 11 ids); counts now 154 BCs (S5 = 20), 41 VPs, 7 D4-EX-3 classes / 5 canonical tests; sync check `sync-check-adv-p5-2026-11-18.md` verdict PASS-WITH-FINDINGS, all 8 findings SC-13..SC-20 closed; lessons L-PG-17..19 codified | COMPLETE — current_step = pass-5 fixes committed; next adversarial pass 6 |

## Convergence Status

- **All six passes CONVERGED** (Phase 0: 0:3 1:3 2:9 3:8 4:7 5:5). Round record + extracted detail: `cycles/phase-0-ingestion/convergence-trajectory.md` ("## Extracted from STATE.md on 2026-11-17"). Phase 1d ADV pass 1 recorded 2026-11-17: 129 findings (21H/63M/40L/5C), NOT_CONVERGED, novelty HIGH — `cycles/phase-1-spec-crystallization/adversarial-reviews/`. Pass 2 recorded 2026-11-17: 116 findings (17H/58M/35L/6C), NOT_CONVERGED, novelty MEDIUM; pass-2 remediation DONE same day (rulings OD-155..165 applied; contract count 145 → 153, VPs 38 → 40). Pass 3 recorded 2026-11-18: 150 findings (36H/61M/48L/5C), NOT_CONVERGED, novelty MEDIUM — REGRESSION (Δ +34, HIGH 17 → 36), investigated per the trajectory-monotonicity rule; root cause: pass-2 remediation added new scope without pre-validation; pass-3 remediation DONE 2026-11-18 (rulings OD-166..168; contract count 153 → 154, BC-5.01.007; VP-INDEX rebuilt — 40 VPs; sync check adv-p3 PASS, 4 warnings fixed). Pass 4 recorded 2026-11-17: 133 findings (39H/57M/32L/5C), NOT_CONVERGED, novelty MEDIUM-HIGH — Δ −17 (150 → 133) but HIGH 36 → 39; many findings sibling-propagation (fixed facts re-flagged at sibling sites, not relapses); HIGH concentration on interface-definitions/registry closure and partial-fix propagation; pass-4 remediation DONE 2026-11-17 (rulings OD-169..175; 41 VPs incl. VP-041; crash register 47 paths, CP-N03; sync check adv-p4 PASS-WITH-FINDINGS, SC-05..12 closed). Pass 5 recorded 2026-11-18: 148 findings (24H/75M/43L/6C), NOT_CONVERGED, novelty MEDIUM — Δ +15 (133 → 148) while HIGH fell 39 → 24, the series' first pass where the total rose but HIGH fell sharply; pass-5 remediation DONE same burst (rulings OD-176..180 incl. OD-176 keeping the full VSDD convergence standard; 7 D4-EX-3 classes / 5 canonical tests; sync check adv-p5 PASS-WITH-FINDINGS, SC-13..20 closed). Pass 6 recorded 2026-11-18: 124 findings (27H/52M/38L/7C), NOT_CONVERGED, novelty MEDIUM — Δ −24 (148 → 124), the largest total drop of the series, though HIGH ticked up 24 → 27; pass-6 remediation DONE same burst (rulings OD-181..187; closed exclusion set 12 ids; sync check adv-p6 PASS-WITH-FINDINGS, SC-21..28 closed). Pass 7 recorded 2026-11-18: 114 findings (14H/47M/49L/4C), NOT_CONVERGED, novelty MEDIUM — Δ −10 (124 → 114) with HIGH nearly halved 27 → 14 and perimeter A2 filing zero HIGH for the first time; pass-7 remediation DONE same burst (rulings OD-188..192; crash register 47 → 48 paths, CP-T09 minted / CP-T08 retired; VP↔BC `bcs:` edges re-machine-checked at 261; sync check adv-p7 PASS-WITH-FINDINGS — 114 closed / 0 open, SC-29..31 closed); next: ADV pass 8 (OD-176: three consecutive cosmetic-only passes to converge — 0 so far).

## Canonical Phase 1 Inputs (pointer table)

| Artifact | Canonical source |
|----------|------------------|
| Inventory | pass-0 r3 §2 — `semport/hylo-legacy/hylo-legacy-pass-0-deep-inventory-r3.md` |
| Architecture | pass-1 r3 §B, two Mermaid diagrams — `hylo-legacy-pass-1-deep-architecture-r3.md` |
| Domain | pass-2 r8 §7, amended by r9 — `hylo-legacy-pass-2-deep-domain-r8.md` |
| BC index | pass-3 r4, amended by r5-r8 — 232 BCs (legacy pass-3 catalogue, not the 154 P1 BCs) — `hylo-legacy-pass-3-deep-behavioral-contracts-r4.md` |
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

- OD numbering: OD-01..OD-192 allocated (Phase 0 gate list + 2026-11-15 market-intel review + porting-tension rulings OD-101..106 + semport-tension rulings OD-107..114 + Phase 1 scope rulings OD-115..117 + domain-spec validation rulings OD-118..130 + PRD subsystem-breakdown ruling OD-131 + PRD open-question rulings OD-132..145 + architecture rulings OD-146..149 + CI/CD landing ruling OD-150 + CI/CD merge rulings OD-151 + consistency-audit fix rulings OD-152..154 + phase-1d pass-2 rulings OD-155..159 + pass-2 remediation rulings OD-160..165 + pass-3 remediation rulings OD-166..168 + pass-4 remediation rulings OD-169..175 + pass-5 remediation rulings OD-176..180 + pass-6 remediation rulings OD-181..187 + pass-7 remediation rulings OD-188..192); next free OD-193 — log: `specs/owner-decisions-log-2026-11-14.md`.
- PRD open questions OQ-1..OQ-14 (prd.md §10) RESOLVED 2026-11-15 by owner rulings OD-132..OD-145 (OQ-3 deferred) — create-architecture gate cleared.
- Optional checks (deferred, non-blocking): Grafana per-session cost panel; offline promtool rule validation.
- Policy risk (owner awareness): Anthropic Usage Policy 2026-11-12 language on routing through consumer subscriptions.

## Concurrent Cycles

| Cycle | Type | Status | Notes |
|-------|------|--------|-------|
| phase-0-ingestion | brownfield-ingestion | **COMPLETE** — Phase 0 PASSED 2026-11-14; analysis converged; artifacts serve as Phase 1 context (pointer table above); transition to the greenfield sub-workflow performed 2026-11-15 | Commits: dff1f56 (passes 2-3) + be38c50 (passes 0/1/4/5) + 5e83b63 (porting rulings) + this burst (semport design, OD-107..114, transition; create-brief + OD-115..117; domain-spec + OD-118..130) |
| phase-1-spec-crystallization | spec-crystallization (greenfield-pipeline sub-workflow) | **IN_PROGRESS** — opened 2026-11-15; directory created retroactively 2026-11-17 | scope P1 statusline (OD-131); brief, domain-spec, PRD (154 BCs ss-01..ss-06 incl. BC-1.07 and BC-5.01.007), architecture (13 ADRs, 41 VPs), parallel steps, CI/CD DONE; phase-1-consistency-audit DONE 2026-11-17 (PASS-WITH-FINDINGS, 0C/0H/4M/8L, all fixed); re-check PASS + phase-1-gate PASSED 2026-11-17; phase-1d ADV passes 1-7 recorded (129 → 116 → 150 → 133 → 148 → 124 → 114 findings; pass 3 a REGRESSION, root-caused: pass-2 scope added without pre-validation); pass-2 remediation DONE 2026-11-17 (rulings OD-155..165 applied; sync check clean); pass-3 remediation DONE 2026-11-18 (rulings OD-166..168; sync check adv-p3 PASS); pass-4 remediation DONE 2026-11-17 (rulings OD-169..175; 41 VPs incl. VP-041; sync check adv-p4 PASS-WITH-FINDINGS); pass-5 recording + remediation DONE 2026-11-18 (rulings OD-176..180; 154 BCs, 41 VPs; sync check adv-p5 PASS-WITH-FINDINGS, SC-13..20 closed); pass-6 recording + remediation DONE 2026-11-18 (rulings OD-181..187; closed set 12 ids; sync check adv-p6 PASS-WITH-FINDINGS, SC-21..28 closed); pass-7 recording + remediation DONE 2026-11-18 (rulings OD-188..192; crash register 48 paths, CP-T09; VP↔BC edges 261; sync check adv-p7 PASS-WITH-FINDINGS — 114 closed / 0 open, SC-29..31 closed; lessons L-PG-23..26); next: ADV pass 8; manifest: `cycles/phase-1-spec-crystallization/cycle-manifest.md` |

## Session Resume Checkpoint (2026-11-17 — SESSION-WRAP-PAUSE)

> **SELF-SUFFICIENT RESUME CONTEXT** — read this section alone to resume after a session CLEAR.

### Where We Are

- Position: Phase 1 **IN PROGRESS** (greenfield-pipeline sub-workflow after the brownfield-to-greenfield transition), scoped to P1 = `hylo statusline`. Phase 0 PASSED 2026-11-14. DONE this session (2026-11-15..18): market intel GO (P1); porting decision; semport target design + validation; brownfield->greenfield transition; product brief (product-level); L2 domain spec (product-level); P1 PRD (154 BCs S1-S6 incl. BC-1.07 + supplements + BC-INDEX); architecture (ARCH-00..09, 13 ADRs, 41 VPs; VP↔BC citations re-verified after the `--subagent` BCs); feasibility review (no PRD changes); DTU assessment (DTU_REQUIRED false); gene-transfusion assessment; CI/CD (PR #1 merged; main fd031da; branch protection live); consistency audit + fix burst CA-01..12 (OD-152..154); consistency re-check PASS; phase-1-gate PASSED 2026-11-17; phase-1d ADV pass-2 remediation DONE (rulings OD-155..165 applied; sync check clean); phase-1d ADV pass-4 recording + remediation DONE (rulings OD-169..175; 154 BCs, 41 VPs incl. VP-041; crash register 47 paths, CP-N03; sync check adv-p4 PASS-WITH-FINDINGS, SC-05..12 closed); phase-1d ADV pass-5 recording + remediation DONE 2026-11-18 (148 findings 24H/75M/43L/6C; rulings OD-176..180; sync check adv-p5 PASS-WITH-FINDINGS, SC-13..20 closed; lessons L-PG-17..19); phase-1d ADV pass-6 recording + remediation DONE 2026-11-18 (124 findings 27H/52M/38L/7C; rulings OD-181..187; sync check adv-p6 PASS-WITH-FINDINGS, SC-21..28 closed; lessons L-PG-20..22); phase-1d ADV pass-7 recording + remediation DONE 2026-11-18 (114 findings 14H/47M/49L/4C; rulings OD-188..192; crash register 48 paths, CP-T09; VP↔BC edges 261; sync check adv-p7 PASS-WITH-FINDINGS — 114 closed / 0 open, SC-29..31 closed; lessons L-PG-23..26). NEXT: phase-1d adversarial spec review pass 8 (OD-176: >=3 clean passes, i.e. three consecutive cosmetic-only passes — 0 so far; inject .factory/policies.yaml incl. policy 21), phase-1d second-model spec review, phase-1-state-backup, check-input-drift, phase-1-human-approval.

### Convergence

- None active this minute. Phase 1d ADV pass 1 recorded 2026-11-17: 129 findings (21H/63M/40L/5C), NOT_CONVERGED, novelty HIGH; pass 2 recorded 2026-11-17: 116 findings (17H/58M/35L/6C), NOT_CONVERGED, novelty MEDIUM; pass 3 recorded 2026-11-18: 150 findings (36H/61M/48L/5C), REGRESSION vs pass 2 (Δ +34), root-caused (OD-155/OD-156..165 scope added without pre-validation; ARCH-06 signature canon; uXXXX escape corruption), NOT_CONVERGED; pass 4 recorded 2026-11-17: 133 findings (39H/57M/32L/5C), Δ −17 but HIGH 36 → 39 (sibling-propagation), NOT_CONVERGED, novelty MEDIUM-HIGH; pass-4 remediation DONE same burst (rulings OD-169..175); pass 5 recorded 2026-11-18: 148 findings (24H/75M/43L/6C), Δ +15 while HIGH fell 39 → 24, NOT_CONVERGED, novelty MEDIUM; pass-5 remediation DONE same burst (rulings OD-176..180). Pass 6 recorded 2026-11-18: 124 findings (27H/52M/38L/7C), Δ −24 (148 → 124) while HIGH ticked up 24 → 27, NOT_CONVERGED, novelty MEDIUM; pass-6 remediation DONE same burst (rulings OD-181..187; closed exclusion set 12 ids). Pass 7 recorded 2026-11-18: 114 findings (14H/47M/49L/4C), Δ −10 while HIGH fell 27 → 14 (perimeter A2 zero HIGH, first time), NOT_CONVERGED, novelty MEDIUM; pass-7 remediation DONE same burst (rulings OD-188..192; sync check adv-p7 114 closed / 0 open, SC-29..31 closed). Phase 0 passes converged 0:3 1:3 2:9 3:8 4:7 5:5.

### In Flight

- None. No sub-agents running; nothing abandoned. Public main fd031da (protected; CI green on 3 OSes). factory-artifacts = this commit. (Note: pass sessions have seen occasional subagent breakdowns — looping, early stops, and one pass-7 mid-burst garble after correct edits; every case verified on disk and the remainder re-dispatched, nothing lost — prefer short, tightly scoped briefs.)

### Pending Owner Decisions

1. PUBLIC DOC EDITS PENDING (PLAN D15 exception OD-101, D4-EX-3 OD-102) — commit to public main only when the owner asks.
2. REVISIT AT P7 — OD-125 (VALID-08): DI-007 "the status line never reads the ledger" stands for now; revisit during the P7 ledger redesign (flag in `specs/domain-spec/invariants.md`).
3. Three [process-gap] lessons (merge-commit author check, CI identity check, never quote flagged text) recorded as Drift Items, target before Phase 3 (L-PG-01..03 in `cycles/phase-0-ingestion/lessons.md`); six deferred PR #1 findings recorded in `code-delivery/phase-1-cicd-setup/review-findings.md`.
4. Housekeeping advisories: CLAUDE_AUTOCOMPACT_PCT_OVERRIDE advisory (add 70 to .claude/settings.json) — handled separately from the 2026-11-17 housekeeping burst, which resolved the other check-state-health warnings; next free OD = OD-193 (log: `specs/owner-decisions-log-2026-11-14.md`); former item 'Owner to confirm GitHub email settings' closed 2026-11-17: both settings on; prompt-injection sighting by a pass-4 subagent reported to the owner (source unidentified; see L-PG-16).

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
| Remediation-plan design calls are checked against settled ODs before dispatch (pass-4 plan call 10 contradicted OD-148; corrected post-burst) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-13 [process-gap] | before Phase 2 |
| Hook scratch files are untracked and gitignored on the public branch (regression-state.json was tracked and carried an absolute home path) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-14 [process-gap] | before Phase 2 |
| Every claimed fix is verified on disk against file content, not agent reports (BC-1.07.002 vector row unwritten; VP-011 count recomputed wrongly) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-15 [process-gap] | before Phase 2 |
| Injected instructions in a tool result are recorded verbatim and the owner notified (pass-4 subagent sighting; source unidentified) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-16 [process-gap] | before Phase 2 |
| Legacy-oracle runs from agent briefs must name the interpreter path (an agent used /usr/bin/python3, Python 3.9.6, not CPython 3.11.7; re-run on 3.11.7 identical) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-17 [process-gap] | before Phase 2 |
| One measurement per fact: a single agent measures end to end; parallel duplicate measurement pins conflicting values (encoder depth limits) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-18 [process-gap] | before Phase 2 |
| Canonical lists (glyph registries et al.) are minted centrally before parallel dispatch (parallel agents minted divergent registries) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-19 [process-gap] | before Phase 2 |
| Every agent's changes are verified on disk by diff and a non-English scan, regardless of its report (garbled or non-English reports; one agent made zero edits reporting nothing usable) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-20 [process-gap] | before Phase 2 |
| Fix-agent rejections are verified on disk like fixes (a pass-5 agent wrongly rejected valid finding ADV-P5-D16, overturned by ADV-P6-D07) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-21 [process-gap] | before Phase 2 |
| VP Go sketches are non-normative illustration, labelled per OD-182 (untypechecked sketches churned every pass) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-22 [process-gap] | before Phase 2 |
| ASM-007 (Claude Code 2.1.326 subagentStatusLine payload) must be validated by an owner capture into git-ignored `captures/` before Phase 2 writes the S1.07 stories | OD-192 (`specs/owner-decisions-log-2026-11-14.md`); ADV-P7-A22 | before Phase 2 S1.07 stories |
| Diff each fix agent's assigned file set on disk and re-dispatch the remainder — a fix agent can break down mid-burst (garbled output) after correct edits | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-23 [process-gap] | before Phase 2 |
| Parallel fix-agent briefs forbid edits outside the assigned set; out-of-set hits are listed back, not edited; orchestrator checks `git diff --name-only` against the set | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-24 [process-gap] | before Phase 2 |
| Validator/sync-check report briefs require repo-relative paths; the orchestrator scans the diff before commit (pass-6 report carried absolute home paths) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-25 [process-gap] | before Phase 2 |
| Before ordering an "exact copy of the authoritative source", verify the source's citations resolve (pass-7 call 10 copied the OD-159 rider citing BC-1.03.001 PC-3 instead of BC-1.02.004) | `cycles/phase-1-spec-crystallization/lessons.md` L-PG-26 [process-gap] | before Phase 2 |

## Skip Log

| Step | Skipped | Justification |
|------|---------|---------------|
| brownfield-design-system-extract | 2026-11-15 | OD-100: feature_type = cli — design-system extraction condition not met; this factory runs with no design system |
| prd-revision | 2026-11-16 | closed as a no-op: the Architect's feasibility review now exists (`specs/architecture-feasibility-report.md`) and its verdict is 'PRD CHANGES REQUIRED: none' — no PRD revision required |
| UX/design-system steps (create-ux-spec, design-system) | 2026-11-16 | OD-100: feature_type = cli — this factory runs with no design system, and the P1 statusline scope has no UX-spec artifact; the steps add no artifact at this altitude |

## Historical Content

| Content | Location |
|---------|----------|
| Burst narratives, convergence records, lessons, session checkpoints + the 2026-11-17 STATE.md extractions | `cycles/phase-0-ingestion/` (burst-log.md and convergence-trajectory.md each with an "## Extracted from STATE.md on 2026-11-17" section: owner rulings 2026-11-14, fix-burst row detail, Research detail, Convergence Status, adversary-pass row detail, Registers paragraph; cycle-manifest.md, session-checkpoints.md) |
| Phase 1 cycle artifacts (manifest, burst log incl. prior 'Last Updated' narratives, trajectory, checkpoints, lessons, remediation plans, sync checks, adversarial reviews) | `cycles/phase-1-spec-crystallization/` |

## Blocking Issues

None.
