---
document_type: pipeline-state
level: ops
version: "2.0"
status: draft
producer: state-manager
timestamp: 2026-11-15T04:58:34Z
last_amended: "2026-11-14 (v2.0) — phase-0 gate PASSED (owner approval 2026-11-14); phase 1 starting, P1 (hylo statusline) scope first"
phase: 1
pipeline: IN_PROGRESS
inputs: []
input-hash: "[live-state]"
traces_to: ""
project: hylo
product: hylo
mode: brownfield
current_step: "Phase 0 PASSED (owner approved 2026-11-14). Next: Phase 1 spec crystallization, P1 (hylo statusline) scope first: brownfield-market-intel step, then semport translation planning and the PRD/BC/architecture for the status line. D-chain cite D-446 latest brownfield; trajectory-tail →0→0→0→0"
current_cycle: "phase-0-ingestion"
dtu_required: false
---

<!--
  STATE.md SIZE BUDGET (per D-421(c) + D-422(c) reconciliation):
  Soft target: <=200 lines; actual 181 lines (wc-l) at phase-0 gate-PASSED transition burst; margin from soft-target = 500 - 200 = 300; margin from actual = 500 - 181 = 319 (D-446(c) dual-margin form).
  Hard cap: 500 lines (validate-state-md-size hook enforcement).
  Historical content belongs in cycle files, NOT here.
-->

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
| **Last Updated** | 2026-11-14 — Phase 0 final analysis COMPLETE: coverage-audit PASS (0 gaps); extraction-validation r2 PASS-WITH-FIXES (78/232 BCs sampled, 100% confirmed; 26/27 metric groups exact; 1 fix); pass-8 definitive synthesis (supersedes pass-6); owner decision list gate-ready (64 ODs, groups A-F). Next: Phase 1 spec crystallization (P1 statusline first); trajectory-tail →0→0→0→0 |

## Owner Guardrails (standing; see policies.yaml 12-20)

1. **Commit / push / PR / merge only with explicit owner approval at that moment** (policy 15). The only exception is state-manager commits on `factory-artifacts`.
2. **Public repo.** `factory-artifacts` never goes to GitHub: inside `.factory/`, `origin` resolves to a local private backup, and a pre-push hook blocks factory history to the public remote. Never use `--no-verify`. Public-bound content follows policy 14.
3. **D1-D16 are settled** (policy 12). Adversary findings that challenge a decision become owner questions, not defects.
4. **Parity first** (D4, policy 13): BCs for statusline, exporter and proxy are extracted from `legacy/`; parity diffs are the acceptance criteria for P1-P3.
5. **Go hardening mapping** (policy 19) replaces Kani/cargo-fuzz/cargo-mutants.
6. **DTU candidates:** fake Anthropic upstream and fake local backend (OpenAI/Anthropic-compatible SSE) for proxy tests.
7. **Never touch the live prototype** or its backend from the pipeline. Phase 0 reads `legacy/` only.

## Phase Progress

| Phase | Status | Notes |
|-------|--------|-------|
| pre-0 initialization | **COMPLETE** | policies 12-19 + merge/autonomy config committed (5007a34) |
| Phase 0 brownfield ingestion of `legacy/` | **PASSED 2026-11-14** (owner approval) — **analysis COMPLETE**: all six passes converged; coverage-audit PASS; extraction-validation r2 PASS-WITH-FIXES; final-synthesis DONE (pass-8) | Gate passed: OD list presented and ruled; next Phase 1 spec crystallization |
| Phases 1-7 (spec crystallization .. convergence) | Phase 1 **IN_PROGRESS** | Phase 0 gate PASSED 2026-11-14; P1 (hylo statusline) scope first |
| Adversary passes (Phase 0) | **ALL SIX CONVERGED** — p0: 3 rounds (NITPICK r3); p1: 3 (NITPICK r3); p2: 9 (NITPICK r9); p3: 8 (r7 self-declared NITPICK overridden — crash path H-09, CONV-ABS-22); p4: 7 (NITPICK r7; r4 self-declared NITPICK overridden — retractions + reliance on a retracted HTTP/2 fact); p5: 5 (NITPICK r5) | round record in cycles/phase-0-ingestion/convergence-trajectory.md; trajectory-tail →0→0→0→0 placeholder retained for the formal finding series |
| Fix bursts (Phase 0) | **NONE** — no fix burst required yet; extraction-validation fixes were applied in-burst during the sweep | narrative in cycles/phase-0-ingestion/burst-log.md |

## Current Phase Steps (last 5)

| # | Step | Outcome |
|---|------|---------|
| 4 | extraction validation (exhaustive; 0 hallucinations) | PASS-WITH-FIXES |
| 5 | grounding burst: STATE.md + policies.yaml + cycle dir committed on factory-artifacts | COMPLETE |
| 6 | convergence-deepening: pass 2 (9 rounds) + pass 3 (8 rounds) | CONVERGED (NITPICK) |
| 7 | convergence-deepening: passes 0, 1, 4, 5 (3/3/7/5 rounds) — all six passes converged | CONVERGED (NITPICK) |
| 8 | final analysis burst: coverage-audit (PASS) + extraction-validation r2 (PASS-WITH-FIXES) + pass-8 definitive synthesis + OD list A-F gate-ready | COMPLETE |

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

## Decisions Log

Engine-level decisions live in `docs/PLAN.md` (owner decisions) and the plugin decision log; this table records pipeline-level decisions taken in this factory:

| Decision | Content | Source | Date |
|----------|---------|--------|------|
| D13 | Intercept all Claude Code traffic | docs/PLAN.md on main (b99082e) | 2026-11-14 |
| D14 | Proxy settings do not leak to child processes | docs/PLAN.md on main (b99082e); mechanism chosen in P4 | 2026-11-14 |
| D15 | Config over code iron rule | docs/PLAN.md + CLAUDE.md working tree; enforced via policy 20 | 2026-11-14 |
| policy 20 | config_over_code policy entry (policies.yaml v1.2) | this factory, grounding burst | 2026-11-14 |

## Research (2026-11-14)

Four reports in `specs/research/`, indexed in `specs/research/RESEARCH-INDEX.md` (verified: exactly one row per report):

- `domain-hybrid-routing-claude-code-2026-11-14.md` — domain landscape, config surfaces, Messages API facts, policy risks, OpenAI translation.
- `general-go-port-parity-crossplatform-2026-11-14.md` — Python->Go byte-parity pitfalls, parity harness, cross-platform, deps, hardening, CI/release.
- `general-go-tls-intercepting-proxy-2026-11-14.md` — stdlib vs goproxy/martian/go-mitmproxy, selective interception + Remote Control, ALPN/SSE/WebSocket, CA semantics, mitmproxy parity behaviors, testing.
- `peer-tool-lessons-2026-11-14.md` — peer-tool lessons L1-L7; owner decisions OD-1 (= D13) and OD-2 (= D14).

## Open Owner Questions

- **OD-01..OD-94 decision list** — gate-ready in `semport/hylo-legacy/hylo-legacy-owner-decisions.md`; present at the Phase 0 gate (64 issued in groups A-F: 2 ruled, 62 pending; next free OD-95).
- Optional checks (deferred, non-blocking): Grafana per-session cost panel; offline promtool rule validation.
- Policy risk (owner awareness): Anthropic Usage Policy 2026-11-12 language on routing through consumer subscriptions.

## Concurrent Cycles

| Cycle | Type | Status | Notes |
|-------|------|--------|-------|
| phase-0-ingestion | brownfield-ingestion | **ACTIVE** — analysis COMPLETE (all six passes converged; coverage-audit PASS; extraction-validation r2 PASS-WITH-FIXES; pass-8 synthesis + OD list done); drift check → consistency audit → owner gate next | Commits: 560a861 (passes 2-3) + 66032bc (passes 0/1/4/5) + this burst (coverage audit, validation r2, synthesis, OD list) |

## Session Resume Checkpoint (2026-11-14 — Phase 0 final analysis COMPLETE)

> **SELF-SUFFICIENT RESUME CONTEXT** — read this section alone to resume after a session CLEAR.

### 1. Where We Are

- Phase 0 final analysis **COMPLETE**: coverage audit **PASS** (step B.5, 0 gaps — `hylo-legacy-coverage-audit.md`); extraction validation r2 **PASS-WITH-FIXES** (step B.6 — 78/232 BCs sampled, 100% confirmed; 26/27 metric groups exact; 1 fix applied in-burst — `hylo-legacy-extraction-validation-r2.md`); deep synthesis **DONE** — `hylo-legacy-pass-8-deep-synthesis.md` is the DEFINITIVE synthesis, supersedes pass-6; primary reference for create-brief / create-domain-spec / create-prd / semport-analyze.
- Owner decision list **gate-ready**: `semport/hylo-legacy/hylo-legacy-owner-decisions.md` — 64 issued ODs in groups A-F (A 12 incl. 2 ruled OD-24/OD-27, B 19, C 13, D 10, E 2, F 8); recommendations 23 KEEP / 30 DEVIATE / 11 NEW; answer format in the file header; next free OD-95.
- **OWNER FLAG (confirm at the gate):** OD-14 now recommends (a) do not port --subagent — reverses the earlier Phase-0 toggle recommendation (PLAN §3 lists custom agent-panel rows as a non-goal; Claude Code 2.1.323 removed subagentStatusLine).
- Lessons recorded in pass-8 §10: 53 total — 13 P0 (L0-01..L0-13), 13 P1, 9 P2, 18 P3. Pass-0 deep inventory corrected in place (spawn census 10 → 9, B.6 note).
- Public repo main is 4 commits ahead of GitHub (b99082e D13/D14, a7b5e04 D15, 3e05cfe D16, plus f562477) — not pushed; push awaits owner.

### 2. Next Steps

1. input-hash drift check over `.factory/` artifacts
2. fresh-context consistency audit
3. Phase 0 owner approval gate: present `semport/hylo-legacy/hylo-legacy-owner-decisions.md` (answer format: OD-06 a, or A: all recommended)

## Skip Log

| Step | Skipped | Justification |
|------|---------|---------------|
| (none to date) | — | — |

## Historical Content

| Content | Location |
|---------|----------|
| Burst narratives, convergence records, lessons, session checkpoints | `cycles/phase-0-ingestion/` (burst-log.md, convergence-trajectory.md, cycle-manifest.md, session-checkpoints.md) |

## Blocking Issues

None.
