---
document_type: domain-spec-index
level: L2
version: "1.2"
status: draft
producer: business-analyst
timestamp: 2026-11-18T05:40:00Z
phase: 1a
inputs:
  - .factory/specs/product-brief.md
  - .factory/specs/owner-decisions-log-2026-11-14.md
  - docs/PLAN.md
  - .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md
  - .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r4.md
  - .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r8.md
  - .factory/semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - .factory/specs/research/domain-hybrid-routing-claude-code-2026-11-14.md
  - .factory/specs/research/domain-statusline-landscape-2026-11-15.md
  - .factory/specs/research/peer-tool-lessons-2026-11-14.md
input-hash: "c53d62b"
traces_to: product-brief.md
sections:
  - entities.md
  - capabilities.md
  - invariants.md
  - domain-events.md
  - state-machines.md
  - bounded-contexts.md
  - ubiquitous-language.md
---

# L2 Domain Specification: hylo

> **Sharded artifact (DF-021).** This index provides navigation and summary.
> Detail lives in per-section files listed below. Each section targets
> 800-1,200 tokens for optimal LLM consumption.

## Domain Summary

hylo is a local, user-run hybrid routing domain: a single Claude Code session draws
its model traffic from two lanes — the user's own inference hardware (local lane) and
Anthropic's cloud (cloud lane) — switched per request by an invisible TLS-intercepting
proxy, with every request observed into an append-only ledger and surfaced on a
lane-aware status line. Product-level scope per owner ruling OD-115: this spec models
all of hylo; the PRD/BC cycle it feeds details P1 (the status line) only.

## Citation Legend (provenance)

Every element carries one of: **LEGACY-OBSERVED** (from Phase 0 codebase passes; cite
form `P2r4 §3.1`, `pass-8 §4` — see `hylo-legacy-pass-*-*.md`), **DECIDED** (owner
settled; cite `D1-D16` from docs/PLAN.md or `OD-NNN` from the owner decision log).
All formerly **PROPOSED** elements (this analyst's inference) were resolved by owner
rulings OD-118..OD-130 (2026-11-15), recorded with their evidence in
`owner-validation-list.md` (status: resolved); the shards cite the OD ids inline.
Ledger/event names (`dgx_*`, `anth_*`) are legacy wire
names kept by D7; domain terms (`local lane`, `backend`) are defined in
`ubiquitous-language.md`, which also carries the legacy→domain term mapping.

## Document Map

| Section | File | Tokens | Primary Consumer | Purpose |
|---------|------|--------|-----------------|---------|
| Entities | entities.md | ~1400 | architect, product-owner | ENT-NN entity model, aggregates, value objects |
| Capabilities | capabilities.md | ~1300 | product-owner, architect, story-writer | CAP-NNN capability catalog + differentiator trace |
| Invariants | invariants.md | ~1100 | product-owner, architect | DI-NNN domain rules |
| Domain Events | domain-events.md | ~1200 | architect, product-owner | EVT-NN: ledger catalog + live event feed |
| State Machines | state-machines.md | ~1100 | architect, test-writer | SM-NNN lifecycles: request, proxy, health, render |
| Bounded Contexts | bounded-contexts.md | ~1100 | architect, product-owner | BC1-BC10 context map and translations |
| Ubiquitous Language | ubiquitous-language.md | ~1200 | all | Glossary + legacy→domain term mapping |
| Owner Validation List | owner-validation-list.md | ~1300 | owner | All 13 items resolved (OD-118..OD-130, 2026-11-15) |

## Cross-References

| If you need... | Read these together |
|----------------|-------------------|
| BC creation input (P1 cycle) | capabilities.md + invariants.md + entities.md + owner-validation-list.md |
| Architecture design input | entities.md + invariants.md + state-machines.md + bounded-contexts.md + domain-events.md |
| Phase mapping (P1-P7) | capabilities.md Priority column + bounded-contexts.md |
| Glossary/term dispute | ubiquitous-language.md + owner-validation-list.md (terms resolved: OD-118..OD-120) |
| Parity/deviation framing | invariants.md DI-010..DI-012 + ubiquitous-language.md (exclusion list) |
| Full domain review (adversary/spec-reviewer) | ALL sections |

## ID Registry Summary

| ID Format | Count | Section |
|-----------|-------|---------|
| ENT-NN | 20 | entities.md |
| CAP-NNN | 18 | capabilities.md |
| DI-NNN | 17 | invariants.md |
| EVT-NN | 15 | domain-events.md |
| SM-NNN | 6 | state-machines.md |
| BOUNDED CONTEXT | 10 (BC1..BC10) | bounded-contexts.md |

Sections deliberately omitted: assumptions/risks/failure-modes/edge-cases — Phase 0
holds the exhaustive registers (232 BCs, 147 thresholds, 22 pitfalls, crash
catalogues in pass-8 §8; the risk/policy picture is in the domain research §4 and
pass-8 §10-11), and per DF-021 those registers become PRD/BC/VP artifacts rather than
being duplicated here at L2. Open items that would normally be assumptions are
itemized with resolutions in `owner-validation-list.md`.

## Priority Distribution (capabilities)

| Priority | Count | Items |
|----------|-------|-------|
| P0 (must-have) | 12 | CAP-001..007, CAP-009, CAP-012, CAP-014, CAP-015, CAP-017 |
| P1 (should-have) | 5 | CAP-008, CAP-010, CAP-011, CAP-013, CAP-016 |
| P2 (nice-to-have) | 1 | CAP-018 |

Priority expresses product necessity; the delivery phase for each capability is in
`capabilities.md` (P1-P7 per docs/PLAN.md §7). Under OD-115, this Phase 1 cycle
elaborates only the P1-phase slice (status line = CAP-009/010/011 render path;
configuration env + defaults = CAP-015).
