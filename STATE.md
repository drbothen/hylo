---
document_type: pipeline-state
level: ops
version: "2.0"
status: draft
producer: state-manager
timestamp: 2026-11-14T08:15:46Z
last_amended: 2026-11-14
phase: 0
pipeline: IN_PROGRESS
inputs: []
input-hash: "[live-state]"
traces_to: ""
project: hylo
product: hylo
mode: brownfield
current_step: "phase-0 convergence-deepening — broad-sweep passes 2 and 3 CONVERGED (9 and 8 deep rounds, novelty decayed to NITPICK); next: deepen passes 0, 1, 4, 5 (at least 2 rounds each), then coverage-audit, final-synthesis, input-hash drift check, owner approval gate; D-chain cite D-446 latest brownfield; owner rulings 2026-11-14 recorded (D16/D15 on main, OD-24/OD-27 ruled); trajectory-tail →0→0→0→0"
current_cycle: "phase-0-ingestion"
dtu_required: false
---

<!--
  STATE.md SIZE BUDGET (per D-421(c) + D-422(c) reconciliation):
  Soft target: ≤200 lines; actual 161 lines (wc-l) at phase-0 convergence-deepening burst; margin from soft-target = 500 - 200 = 300; margin from actual = 500 - 161 = 339 (D-446(c) dual-margin form).
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
| **Last Updated** | 2026-11-14 — phase-0 convergence-deepening burst: pass 2 (9 rounds) and pass 3 (8 rounds) CONVERGED at NITPICK; 232-BC canonical index; OD-01..OD-45 list + owner rulings recorded; captures done. Next: deepen passes 0, 1, 4, 5. trajectory-tail →0→0→0→0 |

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
| Phase 0 brownfield ingestion of `legacy/` | **IN_PROGRESS** — broad sweep passes 0-6 DONE; extraction validation PASS-WITH-FIXES; convergence-deepening: passes 2 and 3 CONVERGED | Canonical index: 232 BCs (137 byte-exact, 44 JSON-equivalent, 10 out of scope, 6 approved deviation, 35 pending owner decision). Remaining: deepen passes 0, 1, 4, 5 (≥2 rounds each), coverage-audit, final-synthesis, input-hash drift check, owner approval gate |
| Phases 1-7 (spec crystallization .. convergence) | PENDING | gated on Phase 0 owner approval |
| Adversary passes (Phase 0) | **CONVERGENCE-DEEPENING ACTIVE** — pass 2: 9 rounds (SUBSTANTIVE r1-r8, NITPICK r9); pass 3: 8 rounds (SUBSTANTIVE r1-r7, NITPICK r8; r7 self-declared NITPICK overridden — crash path H-09, retraction CONV-ABS-22) | round record in cycles/phase-0-ingestion/convergence-trajectory.md; trajectory-tail →0→0→0→0 placeholder retained for the formal finding series |
| Fix bursts (Phase 0) | **NONE** — no fix burst required yet; extraction-validation fixes were applied in-burst during the sweep | narrative in cycles/phase-0-ingestion/burst-log.md |

## Current Phase Steps (last 5)

| # | Step | Outcome |
|---|------|---------|
| 2 | research: 4 reports + RESEARCH-INDEX verification (one row per report) | COMPLETE |
| 3 | semport broad sweep passes 0-6 over `legacy/` | COMPLETE |
| 4 | extraction validation (exhaustive; 0 hallucinations) | PASS-WITH-FIXES |
| 5 | grounding burst: STATE.md + policies.yaml + cycle dir committed on factory-artifacts | COMPLETE |
| 6 | convergence-deepening: pass 2 (9 rounds) + pass 3 (8 rounds) | CONVERGED (NITPICK) |

## Convergence Status

- Broad-sweep pass 2 (deep domain): **CONVERGED** at deep round r9 — SUBSTANTIVE r1-r8, NITPICK r9. Canonical artifact: pass-2 r8 §7 combined pointer table, amended by r9 (`semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r8.md`).
- Broad-sweep pass 3 (deep behavioral contracts): **CONVERGED** at deep round r8 — SUBSTANTIVE r1-r7, NITPICK r8. The orchestrator overrode r7's self-declared NITPICK: new crash path H-09 and retraction CONV-ABS-22 were substantive. Canonical artifact: pass-3 r4 canonical BC index, amended by r5-r8 (`semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md`).
- BC index totals: 232 BCs = 137 byte-exact + 44 JSON-equivalent + 10 out of scope + 6 approved deviation + 35 pending owner decision.
- Statement partition (1,809 Python statements): 903 re-read + 422 covered by pinned tables + 133 out of scope + 351 read in r8 = 1,809; 0 uncovered.
- Retractions: RET crosswalk (pass-3 r4) plus CONV-ABS 12-28; next free CONV-ABS 29.
- Extraction validation (validate-extraction, not a deepening round): PASS-WITH-FIXES; exhaustive; 0 hallucinations.
- Trajectory-tail (D-433(e) LENGTH=4): →0→0→0→0 — placeholder retained until the formal per-pass finding series begins.

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
- **OD-01..OD-45** decision list recorded (OD-44 unused): 42 pending, 2 ruled; next free OD-46. Presented at the Phase 0 gate. D13/D14 remain recorded in the Decisions Log below.

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

- **OD-01..OD-45 decision list** — presented at the Phase 0 gate (42 pending, 2 ruled (OD-24/OD-27); OD-44 unused; next free OD-46).
- Optional checks (deferred, non-blocking): Grafana per-session cost panel; offline promtool rule validation.
- Policy risk (owner awareness): Anthropic Usage Policy 2026-11-12 language on routing through consumer subscriptions.

## Concurrent Cycles

| Cycle | Type | Status | Notes |
|-------|------|--------|-------|
| phase-0-ingestion | brownfield-ingestion | **ACTIVE** — convergence-deepening: passes 2-3 converged; deepen passes 0, 1, 4, 5 next | Deep-burst committed: 17 semport deep files, 232-BC index, OD-01..OD-45, owner rulings, captures. Rounds: 9 + 8 → NITPICK |

## Session Resume Checkpoint (2026-11-14 — convergence-deepening passes 2-3 converged)

> **SELF-SUFFICIENT RESUME CONTEXT** — read this section alone to resume after a session CLEAR.

### 1. Where We Are

- Phase 0 convergence-deepening: pass 2 **CONVERGED** (9 rounds: SUBSTANTIVE r1-r8, NITPICK r9); pass 3 **CONVERGED** (8 rounds: SUBSTANTIVE r1-r7, NITPICK r8; the orchestrator overrode r7's self-declared NITPICK — new crash path H-09 and retraction CONV-ABS-22 forced one more round).
- Canonical Phase 1 inputs: pass-2 r8 §7 combined pointer table (amended by r9); pass-3 r4 canonical BC index (amended by r5-r8). 232 BCs = 137 byte-exact + 44 JSON-equivalent + 10 out of scope + 6 approved deviation + 35 pending owner decision.
- Statement partition (1,809 Python statements): 903 re-read + 422 covered by pinned tables + 133 out of scope + 351 read in r8; 0 uncovered. Retractions: RET crosswalk (pass-3 r4) + CONV-ABS 12-28; next free 29.
- Owner rulings 2026-11-14 (see Owner Decisions section): D16 committed on main (3e05cfe) + D15 (a7b5e04); policy 12 now D1-D16. O1/O2/O3/O5 and Q-a/Q-b/Q-c ruled; LAN exposure accepted until cutover (OD-24/OD-27). OD-01..OD-45 list (42 pending, OD-44 unused); next free OD-46.
- Captures done: env probe (stdio STRICT; Python 3.11.7 statusline / 3.12.10 proxy venv); VictoriaMetrics post-soak capture (19 series, all finite; idle windows ABSENT rather than NaN → CP-N01/N02 latent). DGX 24 h soak over.

### 2. Next Steps

1. Deepen broad-sweep passes 0, 1, 4, 5 — at least 2 rounds each.
2. coverage-audit, then final-synthesis.
3. input-hash drift check over `.factory/` artifacts.
4. Phase 0 owner approval gate: present the OD-01..OD-45 decision list.

## Skip Log

| Step | Skipped | Justification |
|------|---------|---------------|
| (none to date) | — | — |

## Historical Content

| Content | Location |
|---------|----------|
| Burst narratives, adversarial passes, lessons, session checkpoints | `cycles/phase-0-ingestion/` (burst-log.md, cycle-manifest.md) |

## Blocking Issues

None.
