---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md]
input-hash: "5c176a5"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-086"
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

# Behavioral Contract BC-1.04.019: TTFT format boundaries

## Description

Pins the TTFT value text: integer seconds (`.0f`) from 10 s, one decimal (`.1f`) below,
both rounded half-even on the binary value. Because the branch tests the raw value, values
just under 10 can print `10.0s`; the yellow test also uses the raw value. Notation: `\e` is
byte 0x1B.

## Preconditions

1. `ttft` is a finite number (NaN hidden, ±Inf per BC-1.04.016).
2. `integer_from_s` 10, `yellow_s` 8, `min_samples` 20 (BC-1.04.010).

## Postconditions

1. `val = F(ttft, 0) + "s"` if `ttft >= 10`, else `F(ttft, 1) + "s"`.
2. Color yellow iff `ttft > 8` (raw) and not in the "max" form.
3. "max" form iff `n` is a number and `n < 20`.

## Invariants

1. `F` matches Python `format(x, ".Nf")` for every finite double (BC-5.01.001).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | 9.94 / 9.95 | `9.9s` (9.95 is binary-below the tie) |
| EC-002 | 9.96 / 9.99 | `10.0s` (`.1f` branch rounds up) |
| EC-003 | 10.0 / 10.5 / 11.5 | `10s` / `10s` / `12s` (half-even) |
| EC-004 | 2.25 / 2.35 | `2.2s` / `2.4s` |
| EC-005 | 0.05 / 0.15 / 0.25 | `0.1s` / `0.1s` / `0.2s` |
| EC-006 | 8.0 / 8.04 | grey `8.0s` / yellow `8.0s` |
| EC-007 | n 19.999 | `◔max …` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| ttft 2.25 | `\e[90m◔2.2s\e[0m` | happy-path |
| ttft 9.96 | `\e[33m◔10.0s\e[0m` | edge-case |
| ttft 10 | `\e[33m◔10s\e[0m` | edge-case |
| ttft 8.04 | `\e[33m◔8.0s\e[0m` | edge-case |
| ttft 3.0, n 19.999 | `\e[90m◔max 3.0s\e[0m` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | TTFT text equals CPython for random doubles in [0, 10^4] and all tie points k+0.05 | proptest against a CPython-generated table |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:792-799) |
| Legacy contract | BC-SL-086 (P3 r1 new) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | OD-103 (pyfmt package) |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.010 — refines: TTFT segment
- BC-5.01.001 — depends on: `F` formatting

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#row-2` — internal/statusline/row2.go (TTFT boundaries) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — TTFT format boundaries

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:795-799) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if ttft >= 10` (SL:795); `ttft > 8` (SL:799)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Send + Sync |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
