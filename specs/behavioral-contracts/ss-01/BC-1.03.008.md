---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, ../semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1088-1095)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-037"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.008: compact_boundary resets composition and pp

## Description

A line with `type == "system"` and `subtype == "compact_boundary"` marks a context compaction. Everything before
it left the context, so the composition buckets (`res`, `conv`, `think`) restart at 0 and `pp` becomes null (the
next call's write is not a rebuild). Session usage totals are cumulative and are **not** reset. The rest of that
line (its usage, id, content) is skipped. The turn machine has already run for the line.

## Preconditions

1. A decoded object line `e` with `e.type == "system"` and `e.subtype == "compact_boundary"` (exact,
   case-sensitive string equality).
2. The turn machine step for `e` has run (BC-1.03.010): a **timed** boundary is a system line and closes the open
   turn; an untimed boundary does not touch turn state.

## Postconditions

1. `res = conv = think = 0`; `pp = null`.
2. `tin`, `tout`, `c_wr`, `c_rd`, `c_in`, `rb`, `lr`, `lu`, `cur` (beyond the turn step), and the id memory are
   unchanged by this step.
3. The line's `message` (usage, id, content) is ignored: no usage counted, no id recorded, no composition counted.
4. Lines after the boundary count composition from 0.

## Invariants

1. Compaction never shrinks the file; the offset keeps advancing (the shrink reset of BC-1.03.002 is a different
   path).
2. The boundary check precedes the D4-EX-2 predicates that are guarded by "not `cb`" (CP-T04/T06/T07,
   BC-1.03.018); a boundary line carrying wrong-shape usage or content is therefore never skipped. CP-T02 has its
   own `cb` exception (an untimed boundary with a non-object `message`).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Untimed boundary | composition and `pp` reset; turn state untouched |
| EC-002 | Timed boundary while a turn is open | turn closed first (rate may update), then reset |
| EC-003 | Boundary carrying `message.usage` `{"input_tokens": 99}` and an id | usage not counted, id not recorded |
| EC-004 | Boundary with `message: "oops"` (untimed) | processed as a boundary, no skip (BC-1.03.019 row T02− untimed cb) |
| EC-005 | Boundary with wrong-shape usage `{"input_tokens": "5"}` (timed) | processed as a boundary (row T04− cb) |
| EC-006 | `subtype: "Compact_Boundary"` | not a boundary |

## Canonical Test Vectors

One refresh, no cache. Re-pinned 2026-11-15 with the legacy oracle.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `{"type": "user", "message": {"content": "hello"}}`, `{"type": "assistant", "message": {"content": [{"type": "text", "text": "abc"}, {"type": "thinking", "thinking": "zz"}, {"type": "image"}], "id": "a", "usage": {"input_tokens": 7}}}`, `{"type": "system", "subtype": "compact_boundary", "message": {"content": "ignored", "usage": {"input_tokens": 99}, "id": "cbid"}}`, `{"type": "user", "message": {"content": "1234567"}}` | `{"size": 413, "res": 0, "conv": 7, "think": 0, "tin": 7, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 7, "rb": 0, "pp": null, "ids": ["a"], "lr": null, "lu": null, "cur": null}` | happy-path |
| Turn table row T9: U0, A2, timed boundary at 10 (BC-1.03.016) | `lr` [150.0, false], composition 0 after the boundary | edge-case |
| BC-1.03.019 row T02− untimed cb | `"conv": 0`, `"pp": null`, size 513 | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | A boundary line changes only `res`, `conv`, `think`, `pp` (plus turn state when timed) | proptest (state diff) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 (composition differentiator KD-003) |
| L2 Domain Invariants | DI-007 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1088-1095) |
| Legacy contract | BC-SL-037 (base; confirmed pass-3 r1 scenario C) |
| Parity class | byte-exact |
| Architecture Module | `internal/statusline/transcript.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.010 — depends on: turn step runs first
- BC-1.03.007 — composes with: `pp = null` disables the next rebuild test
- BC-1.03.018 — related to: `cb` exceptions in the W-predicates
- BC-1.02.007 — related to: composition percentages rendered from the reset buckets

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#transcript-compaction` — internal/statusline/transcript.go (compact_boundary reset) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029 — boundary state diff

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1088-1095) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if e.get("type") == "system" and e.get("subtype") == "compact_boundary": … continue` (SL:1088-1095)
- **documentation**: SL:1089-1092 (review #6.1: whole-file composition was misleading)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. The protocol strings `system` / `compact_boundary` are named constants (transcript format,
not config).
