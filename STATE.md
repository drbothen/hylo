---
document_type: pipeline-state
level: ops
version: "2.0"
status: draft
producer: state-manager
timestamp: 2026-11-14T04:46:23Z
phase: pre-0
pipeline: INITIALIZED
inputs: []
input-hash: "[live-state]"
traces_to: ""
project: hylo
product: hylo
mode: brownfield
current_step: ""
current_cycle: ""
dtu_required: false
---

<!-- Keep under 200 lines. History goes to cycles/<cycle>/ (see state-manager Content Routing Rules). -->

# Pipeline State: hylo

## Project Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo: hybrid local + cloud model routing for Claude Code (Go port of a Python prototype) |
| **Mode** | brownfield (owner override, 2026-11-14): auto-detection would pick greenfield because there is no src/ |
| **Phase 0 source** | `legacy/` only (scrubbed Python/zsh prototype, read-only). Not the repo root, not any path outside the repo |
| **Port** | Python -> Go (`semport-analyze legacy go`) |
| **Phase 1 inputs** | `docs/PLAN.md` (decisions D1-D12, phases P0-P7), `docs/STATUSLINE-WIDGETS.md`, `docs/STATUSLINE-REVIEW-2026-11-13.md`, `CLAUDE.md` |
| **Default branch** | main (no develop) |

## Owner Guardrails (standing; see policies.yaml 12-19)

1. **Commit / push / PR / merge only with explicit owner approval at that moment** (policy 15). The only exception is state-manager commits on `factory-artifacts`.
2. **Public repo.** `factory-artifacts` never goes to GitHub: inside `.factory/`, `origin` resolves to a local private backup, and a pre-push hook blocks factory history to the public remote. Never use `--no-verify`. Public-bound content follows policy 14.
3. **D1-D12 are settled** (policy 12). Adversary findings that challenge a decision become owner questions, not defects.
4. **Parity first** (D4, policy 13): BCs for statusline, exporter and proxy are extracted from `legacy/`; parity diffs are the acceptance criteria for P1-P3.
5. **Go hardening mapping** (policy 19) replaces Kani/cargo-fuzz/cargo-mutants.
6. **DTU candidates:** fake Anthropic upstream and fake local backend (OpenAI/Anthropic-compatible SSE) for proxy tests.
7. **Never touch the live prototype** or its backend from the pipeline. Phase 0 reads `legacy/` only.

## Current Phase

pre-0: initialized, policies and merge config in place. Next: Phase 0 codebase ingestion of `legacy/` (owner approval gate at the end).

## Blocking Issues

None.
