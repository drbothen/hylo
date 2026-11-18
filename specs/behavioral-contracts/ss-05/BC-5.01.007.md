---
document_type: behavioral-contract
level: L3
version: "1.0.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md
input-hash: "0267ecc"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces CPython mixed int/float coercion behind legacy/dgx_statusline.py arithmetic: SL:435, 599, 882-885, 919)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z new contract (ADV-P3-D08): mixed int/float Num semantics — float(int) conversion with ErrOverflow, true division, exact comparison, Max/Min exact tie-breaks"
  - "1.0.1 2026-11-18: ADV-P4 remediation D15+D16 — ErrZeroDivision for ANY zero divisor (float zero included, CPython-verified); NumCmp NaN verdict (unordered → 0) and Max/Min Python-derivation formulas; Inv 3 rewritten (cross-multiplication, no quotient); phantom NumToInt64Aware name dropped from EC-011"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.01.007: Mixed int/float Num semantics: float(int) ErrOverflow bound, true division, exact comparison, Max/Min exact ties

## Description

`pyfmt.Num` (design §2.6 num.go: int64 / `*big.Int` / float64 / bool-as-int) participates in CPython's mixed
int/float arithmetic whenever a status-line site mixes an exact integer with a float operand (legacy SL:435
`total / 1e6`, SL:599 `{rb:.0f}`, SL:882-885 `_fmt_tokens`, SL:919 elapsed clock; SS-01 consumers BC-1.02.006
EC-010, BC-1.02.025 EC-010, BC-1.03.006). Go's `int64 → float64` conversions and `float64` comparisons silently
round or saturate where CPython raises, and round where CPython compares exactly, so the coercion points are
pinned helpers, not inline conversions (design IM-07..IM-09; pitfalls PR-03, PR-04). Helper-level contract per
OD-141. ADV-P3-D08 disposition.

## Preconditions

1. `NumToF(x Num) (float64, error)`: any `Num`; `ErrValue` for NaN-producing shapes is not possible (a float
   `Num` converts to itself); `ErrOverflow` when an int64/big-int operand has no float64 representation.
2. `TrueDiv(a, b Num) (float64, error)`: numeric `Num` operands; `b` nonzero — ANY zero
   divisor is an error, float zero included (CPython raises `ZeroDivisionError` for
   `1.0/0.0` and `1/0.0` just as for `1/0`; verified `python3 -I`, ADV-P4-D15).
3. `NumCmp(a, b Num) (int, error)`: numeric `Num` operands.
4. Callers keep the source operand order and reproduce each site's Python catch list from the typed errors
   (BC-5.01.003 Invariant 2 discipline).

## Postconditions

1. **NumToF (float(int)):** a float `Num` converts to itself; an int `Num` converts exactly when
   `|n| < 2**1024 - 2**970` (the largest int with a float64 representation, whose float value is `DBL_MAX`;
   CPython rounds to nearest, so every int in `[-(2**1024 - 2**970 - 1), 2**1024 - 2**970 - 1]` converts without
   error). At `|n| >= 2**1024 - 2**970` conversion raises CPython `OverflowError: int too large to convert to
   float` → typed `ErrOverflow` — NOT at `DBL_MAX` and not "when the quotient overflows" (ADV-P3-C07
   threshold, verified: `float(2**1024 - 2**970)` raises, `float(2**1024 - 2**970 - 1) == DBL_MAX`). This is the
   gate behind every float-operand site: `f"{n:.0f}"` of a huge int (SL:599), `_fmt_tokens(float(n))`
   (SL:882-885), and `float(n)` in `_fmt_tok_c`/`_fmt_lines` all degrade through it.
2. **TrueDiv (true division):**
   - int/int: exact rational quotient correctly rounded to the nearest float64 — operands are NOT first
     truncated to float64; the division is computed on the exact rational and rounded once (`10**400 / 10**300`
     is `1e+100`, `1 / 3` is `0.3333333333333333`). `OverflowError` (`ErrOverflow`) when the correctly rounded
     result exceeds the float64 range (`10**310 / 3` raises even though both operands convert individually —
     verified: the operand-range rule of PC 1 does NOT apply to the quotient's computation). `b == 0` → typed
     `ErrZeroDivision` (CPython `ZeroDivisionError`).
   - mixed (int op float, float op int, float/float): the int operand is converted per PC 1 first (possible
     `ErrOverflow`), then IEEE-754 division (`10**310 / 1e300` raises `ErrOverflow` from the operand
     conversion, not the quotient; `10**400 / 10**300` as int/int would succeed) — except that a zero
     FLOAT divisor (or dividend operand of zero divisor) raises `ErrZeroDivision` exactly like the int/int
     case: CPython raises `ZeroDivisionError` for any division by a zero float or int divisor and never
     produces IEEE `inf` from it (ADV-P4-D15, verified `python3 -I`); the calling site degrades exactly as
     legacy does.
3. **NumCmp (exact comparison):** int-vs-float comparison is performed on exact values — the int is never
   rounded to float64 first. Observable at 2^53: `(2**53 + 1) > 9007199254740992.0` is true and
   `(2**53 + 1) == 9007199254740992.0` is false (a rounding conversion would collapse both). Bool
   `Num`s compare as 0/1. **NaN (unordered) verdict (ADV-P4-D16):** when either operand is NaN no
   strict relation holds in CPython (`nan > 1`, `nan < 1`, `nan == nan` are all false; verified
   `python3 -I`), so `NumCmp` returns `0` (equal-or-unordered) — never an error.
4. **Max/Min exactness:** `Max(a, b)` (BC-5.01.003 PC 5) is exactly Python's `b if b > a else a`, i.e.
   `Max(a, b) = (NumCmp(a, b) == -1) ? b : a`, and `Min(a, b) = (NumCmp(a, b) == 1) ? b : a`; the
   tie-break and winner are exact: `Max(9007199254740992.0, 2**53+1)` returns the **int** `9007199254740993`
   (`b > a` exactly; a float-converting Go implementation would return the float `9007199254740992.0`);
   `Min(-(2**53) - 1, -9007199254740992.0)` returns the int `-9007199254740993`. The int-versus-float kind of
   the winner is preserved (serialization differs: `1` vs `1.0`, BC-5.02.006 EC-004). NaN folds into the
   "else a" arm, deriving CPython exactly (verified `python3 -I`): `max(1, nan) == 1`, `max(nan, 1) == nan`,
   `min(1, nan) == 1`, `min(nan, 1) == nan` (ADV-P4-D16).
5. All helpers are pure and deterministic; expectations generated from CPython 3.11.7 (`python3 -I` verified
   2026-11-18, ADV-P3-D08) under the OD-104 oracle discipline.

## Invariants

1. No inline Go `float64(n)` conversion on a `Num` at a status-line site: every int→float crossing goes through
   `NumToF` (typed `ErrOverflow`), every mixed division through `TrueDiv`, every cross-kind comparison through
   `NumCmp` (D15 named-helper discipline, mirroring BC-5.01.003 Invariant 1).
2. `ErrOverflow` from `NumToF`/mixed `TrueDiv` maps to CPython `OverflowError` at each site's catch list;
   sites that do not catch it degrade (OD-156 catalogued crash paths, BC-1.03.018).
3. Comparison helpers never allocate the full quotient (PC 2): int/int strict relations are decided by
   cross-multiplication in the integer domain (`a/b` vs `c/d` compared as `a·d` vs `c·b`, denominators kept
   positive), so no rational quotient is materialized; only the `NumCmp` verdict `-1/0/1` (equal-or-unordered
   → `0`, PC 3) is observable (ADV-P4-D16 rewrite of the unparsable prior wording).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `NumToF(2**1024 - 2**970)` | `ErrOverflow` (CPython `OverflowError`, verified `python3 -I`) |
| EC-002 | `NumToF(2**1024 - 2**970 - 1)` | `DBL_MAX` exactly (`1.7976931348623157e+308`) |
| EC-003 | `f"{10**400:.0f}"` shape: format a 401-digit int as `.0f` via float conversion | `ErrOverflow` → the site degrades (SL:599 shape) |
| EC-004 | `TrueDiv(10**400, 10**300)` | `1e+100` (int/int exact, no operand conversion) |
| EC-005 | `TrueDiv(10**310, 3)` | `ErrOverflow` (quotient out of float64 range; operands individually convertible) |
| EC-006 | `TrueDiv(10**310, 1e300)` | `ErrOverflow` (mixed: the int operand fails PC-1 conversion) |
| EC-007 | `TrueDiv(1, 3)` | `0.3333333333333333` |
| EC-008 | `NumCmp(2**53 + 1, 9007199254740992.0)` | `1` (greater; rounding conversion would say 0) |
| EC-009 | `Max(9007199254740992.0, 2**53+1)`; `Min(-(2**53)-1, -9007199254740992.0)` | int `9007199254740993`; int `-9007199254740993` |
| EC-010 | `TrueDiv(1, 0)` (int/int) | `ErrZeroDivision` |
| EC-011 | mixed division overflow: `_fmt_lines(n / 1e6)` with int `n = 10**310` (SL:857, BC-1.02.014 EC-012) | mixed division converts `n` via `NumToF` first → `ErrOverflow` → the site's catch degrades (legacy `float_div` converts `n` first) |
| EC-012 | `TrueDiv(1.0, 0.0)` and `TrueDiv(1, 0.0)` | `ErrZeroDivision` — a zero float divisor raises exactly like an int zero (CPython `ZeroDivisionError`; ADV-P4-D15) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `NumToF(2**1024 - 2**970 - 1)` | `DBL_MAX` | happy-path |
| `NumToF(10**400)` | `ErrOverflow` | error |
| `TrueDiv(10**400, 10**300)` | `1e+100` | happy-path |
| `TrueDiv(10**310, 1e300)` | `ErrOverflow` | error |
| `NumCmp(2**53 + 1, 9007199254740992.0)` | `1` (exact) | edge-case |
| `TrueDiv(1.0, 0.0)` | `ErrZeroDivision` (zero float divisor, ADV-P4-D15) | error |
| `Max(9007199254740992.0, 2**53+1)` | int `9007199254740993` | edge-case |

All values verified 2026-11-18 against CPython 3.11.7 with `python3 -I` (ADV-P3-D08 derivation).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-023 | `NumCmp(a, b)` agrees with the CPython oracle comparison for all int/float pairs in the generated boundary table (2^-10 around 2^53 and 2^63) | CPython oracle table |
| VP-023 | `TrueDiv(int,int)` equals `Fraction(a,b)` rounded once to float64 (CPython `long_true_divide`) on 2M random samples plus EC-004/005 boundaries | Go property test (testing/quick) + oracle |
| VP-023 | `NumToF` raises `ErrOverflow` exactly at the `|n| >= 2**1024 - 2**970` bound | Go property test over the bound neighborhood |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 (byte parity of rendered numbers) |
| L2 Domain Invariants | DI-008 (typed errors feed the degraded ladder), DI-012 |
| Architecture Module | `internal/pyfmt/num.go` (BC-COMPONENT-MAP: internal/pyfmt/num.go (NumToF/TrueDiv/NumCmp) — ARCH-06) |
| Stories | S-TBD (filled by story-writer) |
| Source | New contract — ADV-P3-D08. OD-103, OD-141; design IM-07..IM-09; pitfalls PR-03, PR-04. Legacy sites served: SL:435 (`total / 1e6`), SL:599 (`{rb:.0f}`), SL:882-885 (`_fmt_tokens` float conversion), SL:919 (elapsed clock), SL:857 (`_fmt_lines` n/1e6); SS-01 consumers BC-1.02.006 EC-010, BC-1.02.025 EC-010, BC-1.03.006 |

## Related BCs (Recommended)

- BC-5.01.003 — composes with (Int/Ceil typed errors, Max/Min pairwise form whose PC-5 exactness this contract pins)
- BC-5.01.006 — composes with (MaxSeq folds NumCmp)
- BC-5.01.001 — related to (Round returns Num from float, the inverse crossing)
- BC-1.02.006, BC-1.02.025, BC-1.03.006 — consumed by (SS-01 mixed-arithmetic sites)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#num` — internal/pyfmt/num.go (NumToF/TrueDiv/NumCmp) (num.go helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

S-TBD — pyfmt num helpers

## VP Anchors (Recommended)

- VP-023 — exact mixed-arithmetic equality tables

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/num.go (NumToF/TrueDiv/NumCmp)` (BC-COMPONENT-MAP: py/num.go (NumToF/TrueDiv/NumCmp) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
