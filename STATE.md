---
document_type: pipeline-state
level: ops
version: "2.1"
status: draft
producer: state-manager
timestamp: 2026-11-16T06:42:44Z
last_amended: "2026-11-16 (v2.3, state-manager backup-create-prd burst: owner rulings OD-132..OD-145 recorded in specs/owner-decisions-log-2026-11-14.md — PRD OQ-1..14 resolved, OQ-3 deferred; OD-135 amends OD-131 labels, S1/S5 CRITICAL; create-prd DONE — 145 BCs behavioral-contracts/ss-01..ss-06: S1 93, S2 13, S3 3, S4 3, S5 19, S6 14; 101 legacy-mapped + 44 new; BC-INDEX + five supplements; subsystem breakdown OD-131; input-hashes re-stamped BC-ALLOCATION/BC-INDEX/prd for the OD-log append); current_step = create-architecture NEXT"
phase: 1
phase_position: "Phase 1 IN_PROGRESS via the greenfield-pipeline sub-workflow (phase-1-spec-crystallization), scoped to P1 statusline; create-domain-spec DONE 2026-11-15; create-prd DONE 2026-11-15; owner rulings OD-132..OD-145 recorded 2026-11-16; current_step = create-architecture NEXT; Phase 0 PASSED 2026-11-14"
pipeline: ACTIVE
inputs: []
input-hash: "[live-state]"
traces_to: ""
project: hylo
product: hylo
mode: brownfield
current_step: "phase-1-spec-crystallization (greenfield-pipeline): create-prd DONE 2026-11-15 (145 BCs S1-S6: S1 93, S2 13, S3 3, S4 3, S5 19, S6 14; supplements, OD-131); owner rulings OD-132..OD-145 recorded 2026-11-16 resolving OQ-1..14 (OQ-3 deferred); current_step = create-architecture NEXT. D-chain cite D-446 latest brownfield; trajectory-tail →0→0→0→0"
current_cycle: "phase-0-ingestion"
market_intel:
  recommendation: GO
  human_decision: approved
  notes: "P1 only. Owner rulings: (1) P1 success criterion = owner's own daily use (byte parity on the owner's setup); community adoption is a P6 concern. (2) README positioning 'lane-aware with backend telemetry and owned-hardware cost' + honest Alternatives section approved in principle, written at P6. (3) no stdin `version` session-cache key until after parity (D4). (4) `7d_oi` Fable-only claim stays a watch note, no work. feature_type = cli, so brownfield-design-system-extract is skipped (condition not met). Allocated OD-96..OD-100."
dtu_required: false
---

<!-- STATE.md SIZE BUDGET (per D-421(c) + D-422(c) reconciliation): soft target <=200 lines; actual 204 lines (wc-l) at the 2026-11-16 backup-create-prd burst; hard cap: 500 lines (validate-state-md-size hook enforcement); margin from soft-target = 500 - 204 = 296; margin from actual = 500 - 204 = 296 (D-446(c) dual-margin form). Historical content belongs in cycle files, NOT here. -->

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
| **Last Updated** | 2026-11-16 — backup-create-prd DONE: owner rulings OD-132..OD-145 recorded in `specs/owner-decisions-log-2026-11-14.md` (PRD OQ-1..14 resolved; OQ-3 deferred; OD-135 amends OD-131 labels — S1/S5 CRITICAL, coverage >= 95%). create-prd COMPLETE: `specs/prd.md` (P1-scoped L3 per OD-115; three-stage writing per OD-131; 145 BCs under `behavioral-contracts/ss-01..ss-06`: S1 93, S2 13, S3 3, S4 3, S5 19, S6 14; 101 legacy-mapped + 44 new; BC-INDEX + BC-ALLOCATION; supplements: interface-definitions, error-taxonomy, nfr-catalog, test-vectors, module-criticality). Next: create-architecture. Prior bursts: create-domain-spec DONE (`specs/domain-spec/`, product-level L2 per OD-115: 18 capabilities, 20 entities, 17 invariants, 15 events, 6 state machines, 10 bounded contexts; VALID-01..13 resolved — OD-118..OD-130; OD-123 supersedes OD-111 key placement; OD-125 REVISIT at P7); create-brief DONE (`specs/product-brief.md`, product-level L1; OD-115..117); semport-translation DONE (design + assessment: 103/103 BCs, 84 H/18 M, S0-S8; validation PASSED; owner ruled T1-T10, OD-107..114); trajectory-tail →0→0→0→0 |

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
| Phases 1-7 (spec crystallization .. convergence) | Phase 1 **IN_PROGRESS** — greenfield-pipeline sub-workflow (phase-1-spec-crystallization); create-domain-spec DONE 2026-11-15; create-prd DONE 2026-11-15 | product brief + domain spec product-level (OD-115); PRD/BCs/supplements P1-scoped (OD-131); later phases via Feature Mode; owner rulings OD-115..145; no design system (OD-100); PRD OQ-1..14 resolved (OD-132..145; OQ-3 deferred); next: create-architecture |
| Adversary passes (Phase 0) | **ALL SIX CONVERGED** — p0: 3 rounds (NITPICK r3); p1: 3 (NITPICK r3); p2: 9 (NITPICK r9); p3: 8 (r7 self-declared NITPICK overridden — crash path H-09, CONV-ABS-22); p4: 7 (NITPICK r7; r4 self-declared NITPICK overridden — retractions + reliance on a retracted HTTP/2 fact); p5: 5 (NITPICK r5) | round record in cycles/phase-0-ingestion/convergence-trajectory.md; trajectory-tail →0→0→0→0 placeholder retained for the formal finding series |
| Fix bursts (Phase 0) | **NONE** — no fix burst required yet; extraction-validation fixes were applied in-burst during the sweep | narrative in cycles/phase-0-ingestion/burst-log.md |

## Current Phase Steps (last 5)

| # | Step | Outcome |
|---|------|---------|
| 16 | create-prd DONE: `specs/prd.md` integrated (three-stage writing per OD-131; subsystem breakdown OD-131 — S1 Status line CRITICAL, S2 Configuration HIGH, S3 Platform MEDIUM, S4 CLI MEDIUM, S5 pyfmt CRITICAL, S6 Parity harness HIGH; reserved S7-S12; S1/S5 CRITICAL per OD-135 amending the OD-131 HIGH labels) + 145 BC files under `behavioral-contracts/ss-01..ss-06` (S1 93, S2 13, S3 3, S4 3, S5 19, S6 14; 101 legacy-mapped from BC-SL + 44 new; ids BC-S.SS.NNN with legacy_id) + BC-INDEX + 5 supplements (interface-definitions, error-taxonomy, nfr-catalog, test-vectors, module-criticality); owner rulings OD-132..OD-145 recorded 2026-11-16 resolving OQ-1..OQ-14 (OQ-3 deferred; OD-135 S1/S5 CRITICAL); input-hashes re-stamped (BC-ALLOCATION, BC-INDEX, prd) | COMPLETE — current_step = create-architecture NEXT |
| 15 | create-prd STAGE 1 (allocation) DONE: `specs/prd.md` skeleton (template-conforming; sections 3-10 marked STAGE 3) + `specs/behavioral-contracts/BC-ALLOCATION.md` — 138 BCs allocated (101 mapped from legacy BC-SL-001..103; BC-SL-097 out of scope per OD-14; BC-SL-068 accounted as replaced by the BC-SL-098 mapping, D4-EX-2; 37 new contracts for S2/S3/S4/S5/S6), writer groups A-H each <= 21 | COMPLETE — stage 2 (parallel BC file creation by writer groups) NEXT |
| 14 | create-domain-spec DONE: `specs/domain-spec/` committed (product-level L2 per OD-115 — 18 CAP, 20 ENT, 17 DI, 15 EVT, 6 SM, BC1-BC10; owner validation VALID-01..13 resolved, rulings OD-118..OD-130 in the OD log; OD-123 supersedes OD-111 top-level key placement, claude-sonnet default stands; OD-125 adopted for now, REVISIT at P7; shard input-hashes recomputed, 8/8 MATCH) | COMPLETE — current_step = create-prd NEXT (P1 scope only, OD-115) |
| 13 | create-brief DONE: specs/product-brief.md committed (product-level L1 per OD-115; personas OD-116; success targets OD-117 incl. p95 <= 25 ms vs legacy median 84.5 ms; proxy overhead deferred to P3) + rulings logged in the OD log | COMPLETE — current_step = create-domain-spec NEXT |
| 12 | semport-translation DONE (design doc + companion assessment; 103/103 BCs: 84 H/18 M; steps S0-S8; ~62 ideal eng-days range 50-80; tensions T1-T10 listed §7.1) + validation gate PASSED (validate-extraction PASS-WITH-FIXES: 3 iterations, ~80 citations + all MEDIUM chains, 3 citation fixes, 1 Python-semantics fix, tally fix, 0 hallucinations) + owner rulings OD-107..114 on T1-T10 + brownfield-to-greenfield transition performed | COMPLETE — GREENFIELD-PIPELINE NEXT |

## Convergence Status

- **All six passes CONVERGED.** Rounds: pass 0 — 3 (SUBSTANTIVE r1-r2, NITPICK r3); pass 1 — 3 (SUBSTANTIVE r1-r2, NITPICK r3); pass 2 — 9 (SUBSTANTIVE r1-r8, NITPICK r9); pass 3 — 8 (SUBSTANTIVE r1-r7, NITPICK r8; r7 self-declared NITPICK overridden by the orchestrator — new crash path H-09, retraction CONV-ABS-22); pass 4 — 7 (SUBSTANTIVE r1-r6, NITPICK r7; r4 self-declared NITPICK overridden — retractions and reliance on a retracted HTTP/2 fact); pass 5 — 5 (SUBSTANTIVE r1-r4, NITPICK r5).
- Round-disposition declarations verified on disk in the final-round files (pass-0/1 r3 declarations; pass-4 r7 / pass-5 r5 "findings are nitpicks, not gaps").

## Canonical Phase 1 Inputs (pointer table)

| Artifact | Canonical source |
|----------|------------------|
| Inventory | pass-0 r3 §2 — `semport/hylo-legacy/hylo-legacy-pass-0-deep-inventory-r3.md` |
| Architecture | pass-1 r3 §B, two Mermaid diagrams — `hylo-legacy-pass-1-deep-architecture-r3.md` |
| Domain | pass-2 r8 §7, amended by r9 — `hylo-legacy-pass-2-deep-domain-r8.md` |
| BC index | pass-3 r4, amended by r5-r8 — 232 BCs — `hylo-legacy-pass-3-deep-behavioral-contracts-r4.md` |
| Thresholds / NFR | pass-4 r7 final catalogue — 147 thresholds; 120 rationales resolved; OD-57 (18 bulk-confirm + 27 owner-rationale in 7 groups); OD-94 fact sheet — `hylo-legacy-pass-4-deep-nfr-r7.md` |
| Conventions / env / determinism / pitfalls | pass-5 r3 consolidated, amended by r4-r5 — 43 explicit + 21 implicit env inputs; 54 determinism rows + 6 Go-side pins; 19 conventions; 22 pitfalls — `hylo-legacy-pass-5-deep-conventions-r3.md` |
| Synthesis (definitive) | pass-8 deep synthesis — supersedes pass-6; primary reference for create-brief / create-domain-spec / create-prd / semport-analyze — `hylo-legacy-pass-8-deep-synthesis.md` |
| Owner decision list (gate input) | 64 issued ODs in groups A-F; one recommendation + evidence per item; answer format in the file header — `hylo-legacy-owner-decisions.md` |
| Market intel (GO, approved) | `planning/market-intel.md` |
| Porting decision (needs_semport true; Python 3 + zsh -> Go 1.26) | `brownfield/porting-decision.md` |
| Semport target design (P1 status line; 103/103 BCs; tensions resolved) | `semport/hylo-legacy/statusline-target-design.md` + companion `semport/hylo-legacy/semport-assessment.md` |

Registers: BC index totals 232 BCs = 137 byte-exact + 44 JSON-equivalent + 10 out of scope + 6 approved deviation + 35 pending owner decision. Statement partition (1,809 Python statements): 903 re-read + 422 covered by pinned tables + 133 out of scope + 351 read in pass-2 r8; 0 uncovered. Retractions: RET crosswalk (pass-3 r4) plus CONV-ABS through 94; next free CONV-ABS 95; IDs 101-104 unused. Extraction validation (validate-extraction, not a deepening round): PASS-WITH-FIXES; exhaustive; 0 hallucinations. Final analysis (this burst): coverage audit PASS (step B.5, 0 gaps); extraction validation r2 PASS-WITH-FIXES (step B.6: 78/232 BCs sampled, 100% confirmed; 26/27 metric groups exact; 1 fix applied in-burst); definitive synthesis pass-8 (supersedes pass-6); lessons 53 — 13 P0 (L0-01..L0-13), 13 P1, 9 P2, 18 P3 — recorded in pass-8 §10. Evidence captured this burst: proxy venv `pyvenv.cfg` include-system-site-packages=false (proxy and preflight not affected by the user site; parity harness runs shimmed Python cases under -s); mitmproxy 12.3.1 with no config.yaml; Go 1.26.5 h2 facts recorded for OD-94. Trajectory-tail (D-433(e) LENGTH=4): →0→0→0→0 placeholder retained until the formal finding series begins.

## Owner Decisions — rulings recorded 2026-11-14

- **D16 committed on main (3e05cfe):** web UI (React + TypeScript + Vite, go:embed, Node build-time only) plus terminal UI on one local event API; design system in Storybook; guardrails. **D15 committed (a7b5e04).** Policy 12 now reads D1-D16.
- **O1:** CI pins Python 3.11 for the statusline and Stop hook (confirmed 3.11.7 by the env probe); 3.12 for the proxy (venv 3.12.10).
- **O2:** degraded output reproduced byte-for-byte for catalogued crash paths.
- **O3 = D4-EX-1:** Go may show ⌂ on Windows.
- **O5:** the nightly differential fuzz job runs but does not gate P1.
- **Q-a:** harness stdio STRICT, confirmed by the env probe (LANG=en_US.UTF-8, no LC_ALL/PYTHONUTF8, utf8_mode 0, strict stdin/stdout, COLUMNS supplied by Claude Code).
- **Q-b:** foreign-cache crash paths CP-C01..C10 are out of parity scope; the Go writer must produce legacy's exact cache format.
- **Q-c = D4-EX-2:** fix the sticky transcript crash. Skip wrong-shape JSON lines as legacy skips invalid JSON (dgx_statusline.py:1060-1063); excluded from the parity diff; covered by Go table tests (BC-SL-098/099).
- **LAN exposure** of the live legacy proxies/exporter: accepted by the owner until cutover (ruled via OD-24/OD-27). hylo proxy, UI and exporter bind to loopback by default (HY-BIND).
- **OD-01..OD-94 decision list gate-ready** — `semport/hylo-legacy/hylo-legacy-owner-decisions.md`. Groups A-F: A 12 (incl. 2 ruled: OD-24/OD-27), B 19, C 13, D 10, E 2, F 8 = 64 issued; unused or reserved (30): OD-44, OD-49, OD-62-65, OD-67-73, OD-77-93; next free OD-95. Recommendations: 23 KEEP / 30 DEVIATE / 11 NEW. **Owner flag: OD-14** now recommends (a) do not port --subagent, reversing the earlier Phase-0 toggle recommendation (PLAN §3 non-goal; CC 2.1.323 removed subagentStatusLine) — confirm at the gate. D13/D14 remain recorded in the Decisions Log below.
- **DECIDED 2026-11-14 (gate rulings; full log in `specs/owner-decisions-log-2026-11-14.md`):**
  - No DGX_* aliases / no backwards compatibility (OD-05)
  - No shadow week, full cutover (OD-52 moot)
  - --subagent not ported (OD-14)
  - Credential hygiene OD-06/07
  - Upstream TLS OD-41
  - HTTP/1.1 only OD-94
  - Proxy lifecycle OD-66/50/38
  - Config paths OD-95
  - Public doc edits drafted in the main working tree (PLAN, STATUSLINE-WIDGETS, RESUME) → committed on main as c023bc6 (ruling below).
- **Public doc edits committed on main as c023bc6** (PLAN D13/D15/P3/P5/P6/§6/§9, STATUSLINE-WIDGETS health dot, RESUME). Public main is 5 commits ahead of GitHub (f562477, b99082e, a7b5e04, 3e05cfe, c023bc6), not pushed.
- **DECIDED 2026-11-15 (market-intel human gate; rows in `specs/owner-decisions-log-2026-11-14.md`):** rulings OD-96..OD-100, summarized in the market_intel frontmatter block above.

## Decisions Log

Engine-level decisions live in `docs/PLAN.md` (owner decisions) and the plugin decision log; this table records pipeline-level decisions taken in this factory:

| Decision | Content | Source | Date |
|----------|---------|--------|------|
| D13 | Intercept all Claude Code traffic | docs/PLAN.md on main (b99082e) | 2026-11-14 |
| D14 | Proxy settings do not leak to child processes | docs/PLAN.md on main (b99082e); mechanism chosen in P4 | 2026-11-14 |
| D15 | Config over code iron rule | docs/PLAN.md + CLAUDE.md working tree; enforced via policy 20 | 2026-11-14 |
| policy 20 | config_over_code policy entry (policies.yaml v1.2) | this factory, grounding burst | 2026-11-14 |
| post-scrub publish | factory-artifacts history scrubbed and rewritten 2026-11-15 (owner-approved): private details removed, logs/ untracked and gitignored, stale SHA citations remapped to post-rewrite SHAs; pre-scrub tag (pre-scrub-2026-11-15) kept local, never pushed; branch to be published on the public repository as an orphan branch; policy 21 public_artifact_hygiene adopted | owner ruling at session wrap | 2026-11-15 |

## Research (2026-11-14)

Four reports in `specs/research/`, indexed in `specs/research/RESEARCH-INDEX.md` (verified: exactly one row per report):

- `domain-hybrid-routing-claude-code-2026-11-14.md` (domain landscape, config surfaces, Messages API facts, policy risks, OpenAI translation); `general-go-port-parity-crossplatform-2026-11-14.md` (Python->Go byte-parity pitfalls, parity harness, cross-platform, deps, hardening, CI/release).
- `general-go-tls-intercepting-proxy-2026-11-14.md` (stdlib vs goproxy/martian/go-mitmproxy, selective interception + Remote Control, ALPN/SSE/WebSocket, CA semantics, mitmproxy parity behaviors, testing); `peer-tool-lessons-2026-11-14.md` (peer lessons L1-L7; owner decisions OD-1 = D13, OD-2 = D14).
- `domain-statusline-landscape-2026-11-15.md` (2026-11-15, domain): status line peer landscape + freshness delta since 11-14 + P1 risk signals — the market-intel input; row in `specs/research/RESEARCH-INDEX.md`.

## Open Owner Questions

- OD numbering: OD-01..OD-145 allocated (Phase 0 gate list + 2026-11-15 market-intel review + porting-tension rulings OD-101..106 + semport-tension rulings OD-107..114 + Phase 1 scope rulings OD-115..117 + domain-spec validation rulings OD-118..130 + PRD subsystem-breakdown ruling OD-131 + PRD open-question rulings OD-132..145); next free OD-146 — log: `specs/owner-decisions-log-2026-11-14.md`.
- PRD open questions OQ-1..OQ-14 (prd.md §10) RESOLVED 2026-11-15 by owner rulings OD-132..OD-145 (OQ-3 deferred) — create-architecture gate cleared.
- Optional checks (deferred, non-blocking): Grafana per-session cost panel; offline promtool rule validation.
- Policy risk (owner awareness): Anthropic Usage Policy 2026-11-12 language on routing through consumer subscriptions.

## Concurrent Cycles

| Cycle | Type | Status | Notes |
|-------|------|--------|-------|
| phase-0-ingestion | brownfield-ingestion | **COMPLETE** — Phase 0 PASSED 2026-11-14; analysis converged; artifacts serve as Phase 1 context (pointer table above); transition to the greenfield sub-workflow performed 2026-11-15 | Commits: dff1f56 (passes 2-3) + be38c50 (passes 0/1/4/5) + 5e83b63 (porting rulings) + this burst (semport design, OD-107..114, transition; create-brief + OD-115..117; domain-spec + OD-118..130) |

## Session Resume Checkpoint (2026-11-16 — Phase 1 in progress: create-prd DONE incl. owner rulings OD-132..145; current_step = create-architecture NEXT)

> **SELF-SUFFICIENT RESUME CONTEXT** — read this section alone to resume after a session CLEAR.

### Where We Are

- Date 2026-11-15. Position: Phase 1 **IN_PROGRESS** — brownfield-to-greenfield transition performed; the pipeline now runs the greenfield-pipeline sub-workflow scoped to P1 = `hylo statusline`. Phase 0 PASSED 2026-11-14.
- Done: market-intel GO + approval (OD-96..OD-100); detect-cross-language-porting DONE (`brownfield/porting-decision.md`: needs_semport true; Python 3 + zsh -> Go 1.26; P1 modules only — `legacy/dgx_statusline.py` minus --subagent; 103 BC-SL). Owner ruled the 6 porting tensions 2026-11-15 (OD-101..OD-106; §9). semport-translation DONE (`semport/hylo-legacy/statusline-target-design.md` + `semport-assessment.md`: 103/103 BCs mapped, 84 H/18 M, steps S0-S8, ~62 ideal engineer-days range 50-80; tensions T1-T10 listed §7.1); validation gate PASSED (validate-extraction PASS-WITH-FIXES: 3 iterations, ~80 citations + all MEDIUM chains checked, 3 citation fixes, 1 Python-semantics fix, per-step tally fix, 0 hallucinations; design doc Validation log); owner ruled the 10 semport tensions (OD-107..OD-114; resolutions appended to the design doc). CREATE-BRIEF DONE 2026-11-15: `specs/product-brief.md` (product-level L1; scope ruling OD-115 — brief + domain spec product-level, PRD/BCs/VPs/architecture detail P1-only; personas OD-116; success targets OD-117). Next: create-domain-spec (product-level L2), then the P1-scoped PRD, BCs from the 103 BC-SL contracts, D15 config registry (incl. `statusline.theme.*`, OD-113), parity-harness spec, internal/pyfmt spec. DOMAIN-SPEC DONE 2026-11-15: `specs/domain-spec/` (product-level L2: 18 CAP, 20 ENT, 17 DI, 15 EVT, 6 SM, BC1-BC10; VALID-01..13 all resolved — rulings OD-118..OD-130; OD-123 supersedes OD-111 top-level key placement, claude-sonnet default stands; OD-125 adopted for now, REVISIT at P7). CREATE-PRD DONE 2026-11-15: `specs/prd.md` (three-stage writing per OD-131) + `behavioral-contracts/ss-01..ss-06` — 145 BCs (S1 93, S2 13, S3 3, S4 3, S5 19, S6 14; 101 legacy-mapped from BC-SL + 44 new) + BC-INDEX + five supplements (interface-definitions, error-taxonomy, nfr-catalog, test-vectors, module-criticality); PRD OQ-1..OQ-14 resolved by owner rulings OD-132..OD-145 (2026-11-16; OQ-3 deferred; OD-135 S1/S5 CRITICAL). Next: create-architecture.
- Gate inputs (Phase 0 artifacts verified accessible as Phase 1 context, 2026-11-15): `semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md`; `planning/market-intel.md`; `brownfield/porting-decision.md`; `semport/hylo-legacy/statusline-target-design.md`; decisions in `specs/owner-decisions-log-2026-11-14.md` (through OD-145; next free OD-146, next free CONV-ABS 95).

### Convergence

- None active. Phase 0 passes converged 0:3 1:3 2:9 3:8 4:7 5:5.

### In Flight

- None. No sub-agents running, nothing abandoned.
- Public repo main is clean except pre-existing untracked local config (.claude/, .mcp.json), intentionally uncommitted.

### Pending Owner Decisions

1. DONE 2026-11-15 — Phase 1 start scoped to P1: YES (feature routing recorded); public main pushed to GitHub (f562477, b99082e, a7b5e04, 3e05cfe, c023bc6; full-history gitleaks + pattern scan clean); 6 porting tensions ruled (OD-101..106); 10 semport tensions ruled (OD-107..114; resolutions in the design doc).
2. Optional: CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70 advisory from check-state-health.
3. PUBLIC DOC EDITS PENDING — PLAN D15 exception (OD-101), D4-EX-3 (OD-102), expanded named exclusion list (OD-110); commit to public main only when the owner asks.
4. REVISIT AT P7 — OD-125 (VALID-08): DI-007 "the status line never reads the ledger" is in force for now (live per-request data reaches the status line only via exporter metrics or the D16 event feed); revisit at P7 during the ledger redesign — allowing ledger-backed widgets then would amend DI-007 and add a BC7←BC4 dependency; flag recorded in `specs/domain-spec/invariants.md` next to DI-007.

No blockers.

### WIP Branches

- None. Public main @ c023bc6 (pushed to GitHub 2026-11-15). factory-artifacts: scrubbed history, published on GitHub as an orphan branch (the local bare repo is now an archive holding the local-only pre-scrub tag).

### Resume

Open a new session in $HOME/Dev/hylo, read docs/RESUME.md and .factory/STATE.md, then run /vsdd-factory:rehydrate-wave then /vsdd-factory:next-step.

## Skip Log

| Step | Skipped | Justification |
|------|---------|---------------|
| brownfield-design-system-extract | 2026-11-15 | OD-100: feature_type = cli — design-system extraction condition not met; this factory runs with no design system |

## Historical Content

| Content | Location |
|---------|----------|
| Burst narratives, convergence records, lessons, session checkpoints | `cycles/phase-0-ingestion/` (burst-log.md, convergence-trajectory.md, cycle-manifest.md, session-checkpoints.md) |

## Blocking Issues

None.
