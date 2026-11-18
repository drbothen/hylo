---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md
input-hash: "14065a4"
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
modified:
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D15+D10+D33: countdown anchor corrected (no :3d in legacy, pads via :02d); SL:920 added; MinInt64 vector added and VP wording fixed"
  - "2026-11-20T18:30:00Z (1.2.3) ADV-P9 remediation D17 — beyond-int64 conversion rule stated for the {pct:>2d} site (SL:1171-1172): round() of a finite float64 is an exact unbounded int formatted in full decimal (verified CPython 3.11.7), no degradation; D's int64 signature is the bounded special case; the only caller degrade remains the preceding TrueDiv overflow (BC-5.01.007 PC-2)"
  - "2026-11-20T19:00:00Z (1.2.4) ADV-P10-A12 residual — PC-5 names the serving helper: pyfmt's big-integer formatter DBig(n *big.Int, width int, zeroPad bool) string (ARCH-06), applying PC-1's digit/width/padding rules to the exact beyond-int64 {pct:>2d} value; agrees with ARCH-06's num.go row and PC-5 comment"
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
2. `width` in 0..67 (rationale, derived: 67 exceeds the widest consumer cell in
   `render_telemetry_fields`/`render_lane` with margin over legacy's 2 and 3 — an envelope,
   not a legacy value; values above 67 are out of consumer range but behave by the same rule).
3. `zeroPad` selects the `02d` form; `!zeroPad` the `>2d` form.

## Postconditions

1. Output is `strconv`-independent: the decimal digits of `|n|`, prefixed by `-` when
   `n < 0`, right-aligned in `width` characters; padding is `0` when `zeroPad`, else a
   space. Zero-padding keeps the sign ahead of the zeros (Python `f"{-5:03d}"` is `-05`).
2. Digit count >= width (not `|n| >= width`; ADV-P2-D18) → no truncation: the full number
   is returned (Python never truncates).
3. `width <= len(digits)` → the number, unpadded (includes negative numbers whose digits
   meet the width).
4. Equal to Python `f"{n:>{width}d}"` / `f"{n:0{width}d}"` for every int64 and every width
   in 0..67, for every finite case in the CPython-generated table
   (`internal/pyfmt/testdata/`, same generator discipline as BC-5.01.001..003).
5. **Beyond-int64 conversion rule (ADV-P9-D17):** one consumer feeds `D` a value that is
   not bounded by int64 — the `{pct:>2d}` site (SL:1171-1172) where
   `pct = round(n / total * 100)` is a Python `round()` result: an exact int of
   unbounded magnitude (realizable far past int64 only from a poisoned-scale mix cache,
   since real counts are bounded). `round()` of a finite float64 is exact, and Python
   formats it in FULL DECIMAL with no error (verified CPython 3.11.7: `f"{2**64:>2d}"`
   is `18446744073709551616`), so no degradation exists to reproduce; the pct caller
   carries the value in the ordered-`Value` exact-int model (BC-5.02.004) and applies
   PC-1's digit/width rules to the exact integer value — `D`'s int64 signature is the
   bounded special case. The caller's only degrade remains the preceding TrueDiv
   overflow (BC-5.01.007 PC-2), not the formatting. The serving helper is pyfmt's
   big-integer formatter `DBig(n *big.Int, width int, zeroPad bool) string` (ARCH-06),
   which applies PC-1's digit/width/padding rules to the exact value, sharing `D`'s
   digit-padding code so the int64 and big-int paths cannot drift.

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
| `D(-9223372036854775808, 0, false)` | `"-9223372036854775808"` (MinInt64: `|n|` overflows int64 magnitudes handled in unsigned form; sign never lost) | edge-case |

Expectations generated from CPython 3.11 (`f"{n:0{w}d}"` forms; OD-104 oracle discipline).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-023 | D equals CPython for every (n, width, zeroPad) in the generated table | CPython oracle table |
| VP-023 | Sign placement holds for every negative int64 value, including the minimum -2^63 (digit derivation is magnitude-based, so the sign is never doubled or lost) | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-05 (`pyfmt.D`), consumers SL:1172, 525, 527, 548, 561, 829, 831, 920 (subagent clock `:02d`; ADV-P3-D10) |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| L2 Domain Invariants | DI-012 (byte parity machinery) |
| Architecture Module | `internal/pyfmt` num.go (BC-COMPONENT-MAP: internal/pyfmt/num.go (D) — ARCH-06) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.01.001 — related to (the `f`-spec sibling `F`)
- BC-5.02.005 — consumes Repr/Str alongside
- BC-1.02.012 — consumer (countdown zero-pad form — legacy has no `:3d` spec; the countdown pads via `:02d`, SL:525/527, via BC-5.01.003 helpers; ADV-P3-D15)

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
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/num.go (D)` (BC-COMPONENT-MAP: py/num.go (D) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
