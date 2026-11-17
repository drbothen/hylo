---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md]
input-hash: "4bc28df"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_telemetry_fields (SL:773-781)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-085"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.018: Mine (last-turn) segment

## Description

The `»N t/s` segment shows this session's last completed API call rate from the transcript
(both lanes), bright when the reply was large enough to measure throughput and grey ("dim")
when it was short and latency-dominated. The input shape rules are Python's: a non-empty
list or tuple whose first element is a number. Notation: `\e` is byte 0x1B.

## Preconditions

1. `sess_rate` = transcript value `mix[7]` (BC-1.03.010; the dim flag is set by the
   transcript machine when the reply had fewer than `statusline.turn.dim_below_out` output
   tokens, default 200).

## Postconditions

1. Segment exists iff `sess_rate` is a list or tuple, non-empty, and `sess_rate[0]` is a
   number (bool, int or float; NaN and ±Inf included).
2. `dim = len(sess_rate) > 1 and truthy(sess_rate[1])` (Python truthiness: `""`, `0`,
   `False`, `None`, `[]`, `{}` are false; any non-empty string is true).
3. `mine = "\e[90m" + F(sess_rate[0],0) + "\e[0m"` if dim, else
   `"\e[1m\e[97m" + F(sess_rate[0],0) + "\e[0m"`.
4. Segment = `"\e[90m»\e[0m" + mine + "\e[90mt/s\e[0m"`, placed before the box segment.
5. Stale mode does not change this segment (it comes from the transcript, not the metrics
   store).

## Invariants

1. A 1-element list renders bright.
2. Extra elements beyond index 1 are ignored.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `[81.5, true]` | grey `82` (half-even) |
| EC-002 | `[82.5, 1]` | grey `82` |
| EC-003 | `[0.5, false]` / `[1.5, false]` | bright `0` / `2` |
| EC-004 | `[]`, `"x"`, `[null, true]`, none | hidden |
| EC-005 | `[NaN, false]` / `[+Inf, 0]` | bright `nan` / `inf` |
| EC-006 | `[true]` | bright `1` |
| EC-007 | `[113.4, "x"]` / `[113.4, ""]` | grey `113` / bright `113` |
| EC-008 | `[113.4, false, 9]` | bright `113` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `[113.4, false]` | `\e[90m»\e[0m\e[1m\e[97m113\e[0m\e[90mt/s\e[0m` | happy-path |
| `[81.5, true]` | `\e[90m»\e[0m\e[90m82\e[0m\e[90mt/s\e[0m` | edge-case |
| `[5]` | `\e[90m»\e[0m\e[1m\e[97m5\e[0m\e[90mt/s\e[0m` | edge-case |
| `[null, true]` | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Segment presence and dimming equal legacy for every JSON value shape of `mix[7]` | Go property test (testing/quick) (generated Values) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:773-781); main (SL:1225) |
| Legacy contract | BC-SL-085 (P3 r1 new) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007 |
| Decisions | OD-113 |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.008 — refines: throughput segments
- BC-1.03.010 — depends on: last-turn rate machine
- BC-5.01.001 — depends on: `.0f` half-even

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/row2.go (mine) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — mine segment shapes

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:773-781) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **type constraint**: `isinstance(sess_rate, (list, tuple)) and sess_rate and isinstance(sess_rate[0], (int, float))` (SL:776)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; operate on `pyfmt.Value` (`IsNumber`, `Truthy`).
