---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, ../semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r6.md, ../semport/hylo-legacy/statusline-target-design.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:442, 453)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-007
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

# Behavioral Contract BC-1.02.002: Model label falls back display_name → id → "?"

## Description

The second segment of row 1 is the model label: stdin `model.display_name` if truthy,
else `model.id` if truthy, else the literal `?`, wrapped in white SGR and a reset. The
fallback uses Python truthiness, so empty strings, `null`, `0`, `false`, `[]` and `{}` all
fall through to the next candidate.

Notation: `\e` is the byte 0x1B.

## Preconditions

1. stdin decoded to an object `d` (BC-1.01.002); `model = d.model` if truthy else `{}`
   (a truthy non-object `model` degrades, see BC-1.02.001 EC-007).
2. The pill (BC-1.02.001) has been computed; it does not raise for this input.

## Postconditions

1. `model_name` = first truthy of (`model.display_name`, `model.id`), else `"?"`
   (Python truthiness, design IM-02).
2. The label segment is exactly `\e[97m` + `model_name` + `\e[0m` (WHITE and RESET from
   `statusline.theme.*`, OD-113; defaults SL:131, SL:127).
3. The label is element 1 of row 1, immediately after the pill; it is never omitted.
4. A string `model_name` is emitted verbatim: no truncation, escaping or trimming. A truthy
   non-string value renders through Python `str()` (contract BC-1.02.021).

## Invariants

1. The label never decides the lane; it is presentation only.
2. The label segment is always present, so row 1 always has at least two elements.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `display_name` is `""`, id `claude-opus-5` | label `claude-opus-5` |
| EC-002 | both missing / `model` null / `model` `{}` | label `?` |
| EC-003 | id `""` only | label `?` |
| EC-004 | `display_name` `0` or `false`, id `m` | label `m` (falsy values fall through) |
| EC-005 | truthy non-string `display_name` (e.g. `1e16`, `true`, a list) | Python `str()` rendering per BC-1.02.021 (e.g. `1e+16`, `True`) |
| EC-006 | lone surrogate inside a string label | strict UTF-8 stdout fails at print → guard line (BC-1.01.008, CP-S17) |
| EC-007 | very long name | emitted in full; width trimming happens only at row level (BC-1.01.006) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15; prefixes `claude-sonnet`.

| Input (`model` value) | Expected label segment | Category |
|-------|----------------|----------|
| `{"display_name":"Sonnet 5.5","id":"claude-sonnet-5-5"}` | `\e[97mSonnet 5.5\e[0m` | happy-path |
| `{"display_name":"","id":"claude-opus-5"}` | `\e[97mclaude-opus-5\e[0m` | edge-case |
| `{"id":""}` | `\e[97m?\e[0m` | edge-case |
| `{}` | `\e[97m?\e[0m` | edge-case |
| `null` | `\e[97m?\e[0m` | edge-case |
| `"x"` (non-object) | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | For string inputs, label = first non-empty of (display_name, id, "?") | property test + table test |
| VP-TBD | Label bytes equal the oracle on the Tier A corpus | parity harness (BC-6.03.002) |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane (SL:442, 453) |
| Legacy contract | BC-SL-007 (cite restored to `:442,453` by pass-3 r6 COR-1) |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-113 (theme keys) |
| Config keys | `statusline.theme.*` (white, reset) |
| Architecture Module | `internal/statusline/lane.go` (design §2.2) |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.001 — composes with (preceding segment)
- BC-1.02.021 — composes with (non-string `str()` rendering)
- BC-1.01.008 — related to (strict UTF-8 stdout)
- BC-5.02.004 — depends on (ordered JSON value and truthiness helpers)

## Architecture Anchors (Recommended)

- `architecture/SS-01-statusline.md#lane` — TBD by architect

## Story Anchor (Recommended)

TBD — row-1 lane segments story

## VP Anchors (Recommended)

- VP-TBD — label fallback property

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`render_lane`, SL:442 assignment, SL:453 use) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `or` chain with literal fallback (SL:442)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
