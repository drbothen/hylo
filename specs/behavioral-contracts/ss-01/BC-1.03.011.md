---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "372936a"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1073-1079, 1096-1103)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-065"
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

# Behavioral Contract BC-1.03.011: First line of a message supplies its usage

## Description

When an API message spans several transcript lines, the **first** line parsed for that message id supplies both
its counted usage (session totals) and the `out` of the turn it opens. Later lines of the same id are ignored for
usage, even when they carry a larger `output_tokens` (for example, the first line holds a streaming placeholder
`output_tokens: 1`). A placeholder `out` therefore makes the turn fail the stale-span test, and the previous
last-turn rate stays.

## Preconditions

1. Lines of one message id `A` appear in order, each with a usage object; the first was not already seen
   (BC-1.03.005).
2. The lines carry valid timestamps when the turn behavior is under test (BC-1.03.010).

## Postconditions

1. Totals (`tin`, `tout`, `c_*`) include only the first line's usage for `A` (BC-1.03.005, postcondition 1).
2. When the first line opens a new turn, `cur.out = first_line.usage.output_tokens or 0`; later lines of the same
   id while that turn is open only move `cur.t1` (BC-1.03.010).
3. The turn closes with `out` from the first line: if the first line's `out` is small, `span ≤ 4·out/15` fails and
   `lr` is unchanged.

## Invariants

1. "First" means first in parse order across refreshes while the id stays in the stored id window.
2. If the message's lines are split by a closer, the reopened turn takes `out` from **its** opening line, while usage
   stays deduplicated (BC-1.03.017).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | First line `output_tokens: 1`, last line 900, span 10 s | `tout` +1; turn skipped (4·1/15 < 10); `lr` stays null |
| EC-002 | First line 300, last line 900, span 10 s | `tout` +300; `lr` = [30.0, false] |
| EC-003 | First line has no usage, second line has usage | the second line's usage is counted (first counted line wins); the turn's `out` is 0 from the opening line |

## Canonical Test Vectors

`U0` = `{"type": "user", "timestamp": "2026-11-14T10:00:00Z", "message": {"content": "go"}}`; `F` =
`{"type": "assistant", "timestamp": "2026-11-14T10:00:02Z", "message": {"id": "msg_A", "content": [{"type":
"text", "text": "a"}], "usage": {"input_tokens": 3, "output_tokens": 1}}}`; `G` = same id at `10:00:10Z`, text
`"b"`, `output_tokens` 900; `S` = `{"type": "system", "subtype": "turn_duration", "timestamp":
"2026-11-14T10:00:11Z"}`. TZ=UTC. Re-pinned 2026-11-15 with the legacy oracle.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `U0, F, G, S` | `{"size": 532, "res": 0, "conv": 4, "think": 0, "tin": 3, "tout": 1, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 3, "rb": 0, "pp": 3, "ids": ["msg_A"], "lr": null, "lu": 1794650400.0, "cur": null}` | edge-case |
| `U0, F′, G, S` with F′ = F but `output_tokens` 300 | `{"size": 534, …, "tin": 3, "tout": 300, …, "lr": [30.0, false], "lu": 1794650400.0, "cur": null}` | happy-path |
| refresh 1 `F′`; refresh 2 `G` (same id, next refresh) | refresh 2 leaves `tout` 300 | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | For any sequence of same-id lines, totals equal the first counted line's usage | proptest |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1073-1079, 1096-1103) |
| Legacy contract | BC-SL-065 (pass-3 r1, new); BC-SL-039 refinement (placeholder out) |
| Parity class | byte-exact |
| Architecture Module | `internal/statusline/transcript.go`, `transcript_turn.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.005 — depends on: dedup mechanism
- BC-1.03.010 — composes with: turn `out` and stale-span test
- BC-1.03.017 — related to: reopened turns take their own opening line's `out`

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#transcript-usage` — internal/statusline/transcript.go (first-line usage) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029 — first counted line wins

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1073-1079, 1096-1103) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: dedup at SL:1099-1100; turn opened only on a new id at SL:1076-1079
- **inferred**: "first wins" follows from those two guards; pinned by oracle

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

No dedicated code; emerges from BC-1.03.005 and BC-1.03.010 ported literally.
