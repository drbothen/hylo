---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "d937286"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1120-1125, 1142-1145)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-072"
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

# Behavioral Contract BC-1.03.014: text/thinking block value types

## Description

The composition step counts `text` and `thinking` blocks with Python `len(value or "")`, so the result depends on
the JSON type of the value: a string counts code points, a list or object counts its item count, a falsy value
counts 0. A truthy number or `true` has no length: legacy raises (crash path CP-T06, degraded line, sticky); hylo
skips the line under the owner-approved deviation **D4-EX-2** (BC-1.03.018). Message-level `content` that is a
string counts code points; an object is ignored.

## Preconditions

1. A processed line whose `message.content` is a list containing an object block with `type` `"text"` (value in
   `text`) or `"thinking"` (value in `thinking`), or a line whose `message.content` is a string/object.

## Postconditions

1. Block value string → `Len` code points added (`conv` for text, `think` for thinking).
2. Block value list → number of elements added; object → number of keys (after duplicate-key collapse).
3. Block value falsy (`""`, `0`, `0.0`, `false`, `null`, `[]`, `{}`, missing) → 0.
4. Block value truthy number (`5`, `1.5`, `-1`) or `true` → **legacy:** `TypeError` (CP-T06) at SL:1143 (text) or
   SL:1145 (thinking), degraded line, no cache write, sticky across refreshes. **hylo:** the whole line is skipped
   under D4-EX-2 (BC-1.03.018 CP-T06 predicate): no partial effects from that line (earlier blocks of the same line,
   its usage, ids and turn effects are not applied). This case is in the D4-EX-2 entry of the OD-105/OD-110 named
   exclusion list and is tested by BC-1.03.019 rows **T06+ text** and **T06+ thinking**.
5. Message-level `content` string → `conv += Len(content)`; object → ignored (BC-1.03.009).

## Invariants

1. Only `text` and `thinking` blocks use `len(value or "")`; `tool_result` and `tool_use` use other rules
   (BC-1.03.009).
2. The CP-T06 skip applies only to non-boundary lines (a `compact_boundary` line never reaches this step).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `text: [1, 2, 3]` | conv 3 |
| EC-002 | `thinking: {"a": 1, "b": 2}` | think 2 |
| EC-003 | `text: 0`, `""`, `null`; `thinking: []`, `false` | 0 each |
| EC-004 | `text: 5` | legacy crash CP-T06; hylo skips the line (D4-EX-2) |
| EC-005 | `thinking: true` | legacy crash CP-T06; hylo skips the line (D4-EX-2) |
| EC-006 | `text: 1.5` | legacy crash; hylo skips (D4-EX-2) |
| EC-007 | `text` block in a `compact_boundary` line | never counted (BC-1.03.008; row T06− cb) |

## Canonical Test Vectors

One line `{"type": "assistant", "message": {"content": <list>}}`; result from the legacy oracle (re-pinned
2026-11-15), and the hylo expectation where they differ.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `[{"type":"text","text":"abc"},{"type":"thinking","thinking":"wxyz"}]` | conv 3, think 4 | happy-path |
| `[{"type":"text","text":[1,2,3]}]` | conv 3 | edge-case |
| `[{"type":"thinking","thinking":{"a":1,"b":2}}]` | think 2 | edge-case |
| `[{"type":"text","text":0},{"type":"text","text":""},{"type":"text","text":null},{"type":"thinking","thinking":[]},{"type":"thinking","thinking":false}]` | all 0 | edge-case |
| `[{"type":"text","text":5}]` | legacy: `TypeError: object of type 'int' has no len()`, degraded; hylo: line skipped, expected cache per BC-1.03.019 T06+ text (`"size": 691`, T01+ state otherwise) | error |
| `[{"type":"thinking","thinking":true}]` | legacy: `TypeError: object of type 'bool' has no len()`; hylo: BC-1.03.019 T06+ thinking (`"size": 584`) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | For every JSON type of the block value, the count equals CPython `len(v or "")` where defined | table test |
| VP-029 | A truthy-number value never degrades in hylo and leaves no partial mutation | table test (D4-EX-2 rows) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007, DI-008, DI-012 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1120-1125, 1142-1145) |
| Legacy contract | BC-SL-072 (pass-3 r1, new) |
| Parity class | byte-exact for non-crash values; crash form → D4-EX-2 (design §8 row 072) |
| Decisions | D4-EX-2 (owner ruling Q-c, 2026-11-14); OD-105 / OD-110 named exclusion list |
| Exclusion entry | `D4-EX-2` in `internal/statusline/testdata/parity/exclusions.json`; table tests = BC-1.03.019 rows T06+ text, T06+ thinking, T06− cb, T06− list |
| Architecture Module | `internal/statusline/transcript_mix.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.009 — composes with: composition rules
- BC-1.03.018 — depends on: CP-T06 W-predicate
- BC-1.03.019 — related to: T06 table rows

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript_mix.go (block value types) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript composition

## VP Anchors (Recommended)

- VP-029 — value-type table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1120-1125, 1142-1145) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: Python `len(x or "")` semantics; pinned by oracle
- **guard clause**: none (the crash is the absence of a guard)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

Implement `pyLen(v Value) (int, ok bool)`; `ok == false` is detected up front by the CP-T06 predicate, so the
composition step itself never fails.
