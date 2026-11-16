---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/statusline-target-design.md, ../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md, owner-decisions-log-2026-11-14.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces CPython //, %, int(), math.ceil, max/min used throughout legacy/dgx_statusline.py)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
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

# Behavioral Contract BC-5.01.003: CPython float divmod/mod; Int/Ceil typed NaN/Overflow errors; Max/Min NaN argument order

## Description

Three CPython number behaviors that Go's builtins get wrong for the status line: float `//` and `%` (CPython
`float_divmod`, not `math.Floor(a/b)`), `int()`/`math.ceil()` truncation that raises on non-finite input, and
`max`/`min` whose NaN result depends on argument order. `pyfmt` provides `FloorDiv`, `Mod`, `FloorDivInt`, `ModInt`,
`Int`, `Ceil`, `Max`, `Min` with exact CPython semantics (design IM-07, IM-08, IM-09; pitfalls PR-03, PR-04, PR-05).

## Preconditions

1. Float helpers take float64 operands; int helpers take integer `Num` operands.
2. Callers keep the source's argument order for `Max`/`Min` and reproduce each site's Python catch list from the
   typed errors.

## Postconditions

1. **FloorDiv/Mod (float).** Port of CPython `float_divmod`: `mod = fmod(a, b)`; `div = (a - mod) / b`; if
   `mod != 0` and `(b < 0) != (mod < 0)` then `mod += b`, `div -= 1`; if `mod == 0` then `mod = copysign(0, b)`; if
   `div != 0` then `q = floor(div)`, and `q += 1` when `div - q > 0.5`; else `q = copysign(0, a / b)`. `b == 0` →
   typed `ErrZeroDivision`.
2. **FloorDivInt/ModInt.** Python integer floor division and modulo: quotient rounds toward −∞, remainder takes the
   divisor's sign (`-7 // 2 = -4`, `-7 % 2 = 1`, `7 // -2 = -4`, `7 % -2 = -1`); exact for big integers.
3. **Int(x float64).** Truncates toward zero and returns the exact integer (`Num`: int64 when it fits, otherwise a
   big integer; Python `int(1e300)` is exact). `NaN` → `ErrValue`; `±Inf` → `ErrOverflow`.
4. **Ceil(x float64).** Smallest integer ≥ x, exact (`Ceil(-0.5) = 0`); `NaN` → `ErrValue`; `±Inf` → `ErrOverflow`.
5. **Max(a, b)** returns `b` only if `b > a`, else `a`; **Min(a, b)** returns `b` only if `b < a`, else `a`. With a
   NaN operand the comparison is false, so the **first** argument is returned (`Max(0, NaN) = 0`,
   `Max(NaN, 0) = NaN`). For equal values of different type the first is kept (`Max(1, 1.0)` is int `1`).
   `MaxSeq` folds left with the same rule.

## Invariants

1. Never `math.Floor(a/b)`, `math.Mod` alone, the builtin `max`/`min`, `math.Max`/`math.Min`, or a bare `int64(x)`
   conversion at a status-line site.
2. Typed errors (`ErrValue`, `ErrOverflow`, `ErrZeroDivision`) let each site reproduce Python's catch list:
   `_fmt_lines` catches `TypeError`/`ValueError` only (SL:854), so `Int(NaN)` gives `"?"` while `Int(±Inf)` degrades
   (BC-1.02.026); uncaught sites map either error to degraded (CP-S06, S11, S12, S13, N01, N02).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `FloorDiv(-0.0, 5.0)`, `Mod(-0.0, 5.0)` | `-0.0`, `0.0` |
| EC-002 | `FloorDiv(0.0, -5.0)`, `Mod(0.0, -5.0)` | `-0.0`, `-0.0` |
| EC-003 | `FloorDiv(+Inf, 60.0)`, `Mod(+Inf, 60.0)` | NaN, NaN (then `Int(NaN)` → `ErrValue` at `_hm`, BC-1.02.027) |
| EC-004 | `FloorDiv(5.0, +Inf)`, `Mod(5.0, +Inf)`; `FloorDiv(-5.0, +Inf)`, `Mod(-5.0, +Inf)` | `0.0`, `5.0`; `-1.0`, `+Inf` |
| EC-005 | `FloorDiv(100000000.1, 60000.0)`, `Mod(…)` | `1666.0`, `40000.09999999404` (dividends near 1e8 ms are why `math.Floor(a/b)` is unsafe, research §2b P7) |
| EC-006 | `Int(-2.7)`; `Int(1e300)` | `-2`; exact 301-digit integer |
| EC-007 | `Min(0, NaN)`, `Min(NaN, 0)` | `0`, NaN |
| EC-008 | `FloorDiv(1.0, 0.0)` | `ErrZeroDivision` (no legacy site divides by a zero literal; listed for completeness) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `FloorDiv(7.0, 2.0)`, `Mod(7.0, 2.0)` | `3.0`, `1.0` | happy-path |
| `FloorDiv(-7.0, 2.0)`, `Mod(-7.0, 2.0)`; `FloorDiv(7.0, -2.0)`, `Mod(7.0, -2.0)` | `-4.0`, `1.0`; `-4.0`, `-1.0` | happy-path |
| `Max(0, NaN)`; `Max(NaN, 0)`; `Max(1, 1.0)` | `0`; NaN; `1` (int) | edge-case |
| `Ceil(2.0000001)`; `Ceil(-0.5)` | `3`; `0` | edge-case |
| `Int(NaN)`; `Int(+Inf)`; `Ceil(NaN)`; `Ceil(-Inf)` | `ErrValue`; `ErrOverflow`; `ErrValue`; `ErrOverflow` | error |

All values verified 2026-11-15 against CPython 3.11.7.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-023 | `FloorDiv`/`Mod` equal CPython on 2M random samples plus the boundary rows | proptest + oracle table |
| VP-023 | For finite b ≠ 0: `FloorDiv(a,b)*b + Mod(a,b)` ≈ a and `Mod` has b's sign or is a signed zero | proptest |
| VP-023 | `Max(a, NaN) == a` and `Max(NaN, a)` is NaN for all a | proptest |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (typed errors feed the degraded ladder), DI-012 |
| Architecture Module | `internal/pyfmt/num.go` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/num.go (divmod/mod, Int/Ceil, Max/Min) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103; design IM-07, IM-08, IM-09; pitfalls PR-03, PR-04, PR-05. Legacy sites served: float `//`/`%` SL:525-529, 546, 560, 826; int `//`/`%` SL:548, 561, 829-831, 859; `int()` SL:148, 426, 546, 675, 683, 853; `math.ceil` SL:759; `max`/`min` SL:146, 422, 479, 508, 671, 674-675, 758-759, 1117 |

## Related BCs (Recommended)

- BC-1.02.012, BC-1.02.027, BC-1.02.028 — consumed by (countdown, `_hm`, window-age formats)
- BC-1.02.026 — consumed by (`_fmt_lines` catch list)
- BC-1.04.009, BC-1.04.014, BC-1.04.015 — consumed by (sparkline and KV NaN paths)
- BC-5.01.001 — related to (`Round` errors share the typed-error scheme)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-num` — internal/pyfmt/num.go (divmod/mod, Int/Ceil, Max/Min) (Python arithmetic helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt num (design step S1)

## VP Anchors (Recommended)

- VP-023 — float divmod equals CPython

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | Send + Sync (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/num.go (divmod/mod, Int/Ceil, Max/Min)` (BC-COMPONENT-MAP: py/num.go (divmod/mod, Int/Ceil, Max/Min) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
