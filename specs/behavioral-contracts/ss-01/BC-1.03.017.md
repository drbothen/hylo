---
document_type: behavioral-contract
level: L3
version: "1.3"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "d937286"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1072-1079, 1096-1103)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-095"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.3 2026-11-20T18:00:00Z: pass-9 remediation (ADV-P9-C04) — Inv 1 and the VP-029 row restricted to transcripts with no W-lines: under D4-EX-2 the CP-T04/CP-T05 skip predicates read seen_ids, so pre-seeding changes which lines skip (counter-example: a timed user line with wrong-shape usage is skipped with seed ids [] and processed with seed ids [B)]"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.017: Turn identity ignores seen_ids

## Description

The turn machine decides "same turn" vs "new turn" only by comparing the line's `message.id` with `cur.id`. It
never consults the usage dedup memory. A message whose lines are separated by a closer (real user prompt, timed
system line) or by another message id is therefore measured as two turns, and each takes `out` from its own
opening line's `usage.output_tokens`, even though that usage is not counted again in the session totals.

## Preconditions

1. Timed assistant lines of id `A` occur on both sides of a closer or of another id's line.
2. `A` is in the dedup memory after its first counted line (BC-1.03.005).

## Postconditions

1. The line of `A` after the separator opens a new turn: `cur = {"id": "A", "t0": lu, "t1": t, "out": <that line's
   output_tokens or 0>}`.
2. The session totals do not change for that line (usage deduplicated).
3. The new turn is closed and rated by BC-1.03.010's rules independently of the first.

## Invariants

1. In transcripts with no W-lines, `seen_ids` membership never influences `cur`, `lr` or `lu`. Unrestricted, the claim fails under D4-EX-2: the CP-T04/CP-T05 skip predicates read `seen_ids` (BC-1.03.018:95-96), so pre-seeding changes which lines are skipped.
2. Dedup never depends on turn state.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | A split by a real user prompt | two turns; the second's t0 = the prompt's time |
| EC-002 | A split by another id B (row T14) | three turns A, B, A; the last A's t0 = the shared `lu` |
| EC-003 | A split only by a tool_result user line | one turn (tool_result does not close; row T2) |

## Canonical Test Vectors

`U0` = `{"type": "user", "timestamp": "2026-11-14T10:00:00Z", "message": {"content": "go"}}`; `F′` =
`{"type": "assistant", "timestamp": "2026-11-14T10:00:02Z", "message": {"id": "msg_A", "content": [{"type":
"text", "text": "a"}], "usage": {"input_tokens": 3, "output_tokens": 300}}}`; `U5` = U0 at `10:00:05Z`; `G2` =
`{"type": "assistant", "timestamp": "2026-11-14T10:00:08Z", "message": {"id": "msg_A", "content": [{"type":
"text", "text": "b"}], "usage": {"input_tokens": 3, "output_tokens": 900}}}`; `S` = `{"type": "system",
"subtype": "turn_duration", "timestamp": "2026-11-14T10:00:11Z"}`. TZ=UTC. Re-pinned 2026-11-15.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `U0, F′, U5, G2, S` | `{"size": 618, "res": 0, "conv": 6, "think": 0, "tin": 3, "tout": 300, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 3, "rb": 0, "pp": 3, "ids": ["msg_A"], "lr": [300.0, false], "lu": 1794650405.0, "cur": null}` (first turn 300/2 = 150, then second turn 900/3 = 300; `tout` stays 300) | happy-path |
| BC-1.03.016 row T14 | `lr [37.5, false]` | edge-case |
| BC-1.03.016 row T2 | `lr [30.0, false]` (no split) | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | Turn state is invariant under pre-seeding arbitrary ids into the dedup memory, for transcripts with no W-lines (under D4-EX-2 the CP-T04/CP-T05 skip legs read `seen_ids`, so seeding changes which lines skip — BC-1.03.018; generator restricted to W-line-free transcripts) | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1072-1079 turn, 1096-1103 dedup) |
| Legacy contract | BC-SL-095 (pass-3 r2 §A4) |
| Parity class | byte-exact |
| Architecture Module | `internal/statusline/transcript_turn.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.010 — depends on: turn rules
- BC-1.03.005 — related to: independent dedup memory
- BC-1.03.011 — related to: per-opening-line `out`

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript_turn.go (turn identity) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — turn machine

## VP Anchors (Recommended)

- VP-029 — turn/dedup independence

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1072-1079, 1096-1103) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: the turn block (SL:1069-1087) reads no dedup state; oracle-pinned

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

Keep turn state and dedup state in separate structs so the independence is structural.
