---
document_type: pipeline-state
level: ops
version: "2.0"
status: draft
producer: state-manager
timestamp: 2026-11-14T05:41:45Z
last_amended: 2026-11-14
phase: 0
pipeline: IN_PROGRESS
inputs: []
input-hash: "[live-state]"
traces_to: ""
project: hylo
product: hylo
mode: brownfield
current_step: "phase-0 broad sweep complete and validated; next convergence-deepening; D-chain cite D-446 latest brownfield; governing owner decisions D13-D15 recorded 2026-11-14; trajectory-tail →0→0→0→0"
current_cycle: "phase-0-ingestion"
dtu_required: false
---

<!--
  STATE.md SIZE BUDGET (per D-421(c) + D-422(c) reconciliation):
  Soft target: ≤200 lines; actual 182 lines (wc-l) at phase-0 grounding burst; margin from soft-target = 500 - 200 = 300; margin from actual = 500 - 182 = 318 (D-446(c) dual-margin form).
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
| **Phase 1 inputs** | `docs/PLAN.md` (decisions D1-D15, phases P0-P7), `docs/STATUSLINE-WIDGETS.md`, `docs/STATUSLINE-REVIEW-2026-11-13.md`, `CLAUDE.md` |
| **Default branch** | main (no develop) |
| **Last Updated** | 2026-11-14 — phase-0 grounding burst: 4 research reports + legacy broad sweep passes 0-6 + extraction validation PASS-WITH-FIXES; D13-D15 recorded; policy 20 added; trajectory-tail →0→0→0→0 |

## Owner Guardrails (standing; see policies.yaml 12-20)

1. **Commit / push / PR / merge only with explicit owner approval at that moment** (policy 15). The only exception is state-manager commits on `factory-artifacts`.
2. **Public repo.** `factory-artifacts` never goes to GitHub: inside `.factory/`, `origin` resolves to a local private backup, and a pre-push hook blocks factory history to the public remote. Never use `--no-verify`. Public-bound content follows policy 14.
3. **D1-D15 are settled** (policy 12). Adversary findings that challenge a decision become owner questions, not defects.
4. **Parity first** (D4, policy 13): BCs for statusline, exporter and proxy are extracted from `legacy/`; parity diffs are the acceptance criteria for P1-P3.
5. **Go hardening mapping** (policy 19) replaces Kani/cargo-fuzz/cargo-mutants.
6. **DTU candidates:** fake Anthropic upstream and fake local backend (OpenAI/Anthropic-compatible SSE) for proxy tests.
7. **Never touch the live prototype** or its backend from the pipeline. Phase 0 reads `legacy/` only.

## Phase Progress

| Phase | Status | Notes |
|-------|--------|-------|
| pre-0 initialization | **COMPLETE** | policies 12-19 + merge/autonomy config committed (5007a34) |
| Phase 0 brownfield ingestion of `legacy/` | **IN_PROGRESS** — broad sweep passes 0-6 DONE; extraction validation PASS-WITH-FIXES (exhaustive; 0 hallucinations) | 136 BC candidates, 105 thresholds (52 rationale UNKNOWN), 40 env vars, 12 ledger events, 27 metric families. Remaining: convergence-deepening, coverage-audit, final-synthesis, input-hash drift check, owner approval gate. Trajectory-tail →0→0→0→0 |
| Phases 1-7 (spec crystallization .. convergence) | PENDING | gated on Phase 0 owner approval |
| Adversary passes (Phase 0) | **NOT STARTED** — no adversary pass dispatched yet; pass-N rows are appended here starting at convergence-deepening (pass-1) | 0 findings; trajectory-tail →0→0→0→0 is the pre-adversary placeholder |
| Fix bursts (Phase 0) | **NONE** — no fix burst required yet; extraction-validation fixes were applied in-burst during the sweep | narrative in cycles/phase-0-ingestion/burst-log.md |

## Current Phase Steps (last 5)

| # | Step | Outcome |
|---|------|---------|
| 1 | pre-0 initialization (policies 12-19, merge/autonomy config) | COMPLETE (5007a34) |
| 2 | research: 4 reports + RESEARCH-INDEX verification (one row per report) | COMPLETE |
| 3 | semport broad sweep passes 0-6 over `legacy/` | COMPLETE |
| 4 | extraction validation (exhaustive; 0 hallucinations) | PASS-WITH-FIXES |
| 5 | grounding burst: STATE.md + policies.yaml + cycle dir committed on factory-artifacts | COMPLETE |

## Convergence Status

- No adversary passes have run yet (Phase 0 is pre-adversary; the first adversary pass begins at convergence-deepening).
- Trajectory-tail (D-433(e) LENGTH=4): →0→0→0→0 — placeholder zeroes until the first adversary pass produces a real finding series.
- Extraction validation (validate-extraction, not an adversary pass): PASS-WITH-FIXES; exhaustive; 0 hallucinations.

## Owner Decisions (2026-11-14)

- **D13 — intercept all Claude Code traffic.** Committed to `docs/PLAN.md` on main (`b99082e`).
- **D14 — proxy settings do not leak to child processes.** Committed `b99082e`; mechanism chosen in P4; research recommendation in `specs/research/peer-tool-lessons-2026-11-14.md`.
- **D15 — config over code (iron rule).** Adopted; in `docs/PLAN.md` and `CLAUDE.md` working tree, public commit pending owner approval; enforced via policy 20 (`config_over_code`).
- Guardrail 3 above now reads D1-D15 (was D1-D12).

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

### Status line / parity

- **O1** — Python pin: proxy 3.12.10 venv; statusline/hook use PATH python3 = 3.11.7 locally, unconfirmed under Claude Code.
- **O2** — reproduce "statusline degraded" byte-for-byte.
- **O3** — allow ⌂ on Windows.
- **O4** — macOS notarization.
- **O5** — nightly differential-fuzz clean nights.
- Config dir mismatch: PLAN §6 `~/.config` vs `os.UserConfigDir()` on macOS.

### Proxy

- Intercept-failure behavior for non-interceptable hosts.
- Legacy keychain install (drop / `--os-trust`).
- Exclusion-only name constraint.
- Sandbox mode vs D14.
- HTTPS_PROXY-only parity.
- MCP stdio servers and user hooks = children or Claude traffic.
- Parity = byte-identical vs JSON-equivalent (may need Go 1.27 floor).
- Broken legacy WS ledger events (reproduce vs fix).
- x/sys dependency.

### Legacy quirks needing disposition

- Always-unknown account label.
- Always-zero anth duration metrics.
- Trust remove/rotate crash.
- profile.env read after proxy start.
- x-api-key forwarded on the local lane.
- Import-time crash on non-numeric DGX_SL_TTL / DGX_SL_ROWS.
- Unwired coordinator.
- 52 thresholds with UNKNOWN rationale.

### Policy risk (owner awareness)

- Anthropic Usage Policy 2026-11-12 language on routing through consumer subscriptions.

## Concurrent Cycles

| Cycle | Type | Status | Notes |
|-------|------|--------|-------|
| phase-0-ingestion | brownfield-ingestion | **ACTIVE** — broad sweep DONE; convergence-deepening next | Grounding burst committed: research (4 reports), semport passes 0-6 + validation, D13-D15, policy 20. Trajectory-tail →0→0→0→0 |

## Session Resume Checkpoint (2026-11-14 — grounding burst committed; next convergence-deepening)

> **SELF-SUFFICIENT RESUME CONTEXT** — read this section alone to resume after a session CLEAR.

### 1. Where We Are

- Phase 0 brownfield ingestion of `legacy/`: broad sweep passes 0-6 DONE (136 BC candidates, 105 thresholds with 52 rationale UNKNOWN, 40 env vars, 12 ledger events, 27 metric families); extraction validation PASS-WITH-FIXES (exhaustive; 0 hallucinations).
- 4 research reports indexed in `specs/research/RESEARCH-INDEX.md` (one row per report, verified).
- Owner decisions D13 + D14 committed to docs/PLAN.md on main (b99082e); D15 adopted (working tree), codified as policy 20; policy 12 range now D1-D15.
- No adversary passes yet; trajectory-tail →0→0→0→0 is the pre-adversary placeholder.

### 2. Next Steps

1. convergence-deepening on the 136 BC candidates (iterative passes until novelty decays).
2. coverage-audit, then final-synthesis.
3. input-hash drift check over `.factory/` artifacts.
4. Phase 0 owner approval gate before Phase 1 spec crystallization.

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
