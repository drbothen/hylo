---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T21:30:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - ../semport/hylo-legacy/statusline-target-design.md
  - ../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces the {:d}-family format spec used at legacy/dgx_statusline.py SL:1172, 525, 527, 548, 561, 829, 831)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: new
parity_class: "n.a."
confidence: "—"
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

# Behavioral Contract BC-5.01.004: pyfmt.D: {:d} decimal formatting with width and zero-pad

## Description

`pyfmt.D(n int64, width int, zeroPad bool)` (num.go, design IM-05) is the single helper for
every Python `d`-spec f-string site: `{n:>2d}` (SL:1172) and `{n:02d}` (SL:525, 527, 548,
561, 829, 831). Python formats the int in decimal, right-aligned in `width` (sign counts
into the width), left-padded with spaces, or with zeros for the `0Nd` form. Helper-level
contract per OD-141.

## Preconditions

1. `n` any int64.
2. `width` in 0..67 (legacy uses 2 and 3); values above 67 are out of consumer range but
   behave by the same rule.
3. `zeroPad` selects the `02d` form; `!zeroPad` the `>2d` form.

## Postconditions

1. Output is `strconv`-independent: the decimal digits of `|n|`, prefixed by `-` when
   `n < 0`, right-aligned in `width` characters; padding is `0` when `zeroPad`, else a
   space. Zero-padding keeps the sign ahead of the zeros (Python `f"{-5:03d}"` is `-05`).
2. `|n| >= width` → no truncation: the full number is returned (Python never truncates).
3. `width <= len(digits)` → the number, unpadded (includes negative numbers whose digits
   meet the width).
4. Equal to Python `f"{n:>{width}d}"` / `f"{n:0{width}d}"` for every int64 and every width
   in 0..67, for every finite case in the CPython-generated table
   (`internal/pyfmt/testdata/`, same generator discipline as BC-5.01.001..003).

## Invariants

1. Pure; no fallback to Go's `%d`/`fmt.Sprintf` at the consumer sites.
2. Digits are ASCII; no grouping, no locale.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `D(5, 2, false)` | `" 5"` (`{n:>2d}`, SL:1172) |
| EC-002 | `D(5, 2, true)` | `"05"` |
| EC-003 | `D(-5, 3, true)` | `"-05"` (sign ahead of the zeros) |
| EC-004 | `D(23, 2, true)` | `"23"` (no truncation) |
| EC-005 | `D(0, 2, true)` | `"00"` |
| EC-006 | `D(-1, 2, false)` | `"-1"` (width exceeded) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `D(5, 2, false)` | `" 5"` | happy-path |
| `D(-5, 3, true)` | `"-05"` | edge-case |
| `D(0, 2, true)` | `"00"` | edge-case |

Expectations generated from CPython 3.11 (`f"{n:0{w}d}"` forms; OD-104 oracle discipline).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-023 | D equals CPython for every (n, width, zeroPad) in the generated table | CPython oracle table |
| VP-023 | Sign placement holds for every negative int64 minimum | proptest |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-05 (`pyfmt.D`), consumers SL:1172, 525, 527, 548, 561, 829, 831 |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| L2 Domain Invariants | DI-012 (byte parity machinery) |
| Architecture Module | `internal/pyfmt` num.go (BC-COMPONENT-MAP: internal/pyfmt/num.go (D) — ARCH-06) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.01.001 — related to (the `f`-spec sibling `F`)
- BC-5.02.005 — consumes Repr/Str alongside
- BC-1.02.012 — consumer (countdown `{je:3d}` form, via BC-5.01.003 helpers)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#num` — internal/pyfmt/num.go (D) (num.go helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

S-TBD — pyfmt num helpers

## VP Anchors (Recommended)

- VP-023 — oracle-table equality

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | Send + Sync (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/num.go (D)` (BC-COMPONENT-MAP: py/num.go (D) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
