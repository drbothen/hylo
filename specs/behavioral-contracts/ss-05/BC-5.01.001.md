---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md, owner-decisions-log-2026-11-14.md]
input-hash: "27f5d0f"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces CPython round()/format() used at legacy/dgx_statusline.py SL:1171, 234 and the .Nf sites)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D10: _fmt_tokens .Nf site SL:882-885 added to served sites"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.01.001: Round/RoundN/F: half-even, decimal re-round, 'f' format incl. -0; nan/inf/-inf spellings

## Description

`internal/pyfmt` (`num.go`) reproduces three CPython 3.11 number operations the status line formats with:
`round(x)` (ties to even, returns int), `round(x, n)` (correctly rounded decimal, returns float) and the
`f"{x:.Nf}"` format spec. Go's `math.Round` (ties away from zero) and `strconv` spellings `NaN`/`+Inf` differ, so
every status-line site uses these helpers (design IM-05, IM-06; pitfalls PR-01, PR-02). Signature note
(ADV-P1-D06, resolved ADV-P2-D08): `Round(x float64) (Num, error)` — the ARCH-06 row is reconciled.

## Preconditions

1. `Round(x float64) (Num, error)`: any float64.
2. `RoundN(x float64, n int) float64`: `0 <= n <= 17` (rationale, derived: 17 significant
   decimal digits uniquely determine any IEEE-754 binary64, so no shorter-round-trip site can
   need more; legacy's largest is `n = 4`, SL:234 — the envelope is a judgment-call margin,
   not a legacy value).
3. `F(x float64, prec int) string`: `0 <= prec <= 20` (rationale, labeled judgment call: legacy
   uses 0, 1, 2 and CPython's `f` format imposes no upper bound; 20 bounds pathological widths
   while covering every conceivable site).

## Postconditions

1. **Round.** Returns the integer nearest to the exact binary value of `x`, ties to even (Python `round(x)`), as a
   `Num` int: int64 when it fits, otherwise an exact big integer (`round(1e300) == int(1e300)`). `NaN` → typed
   `ErrValue`; `±Inf` → typed `ErrOverflow` (Python `ValueError` / `OverflowError`). The result is an int, so
   `round(-0.4)` is `0` (no negative zero).
2. **RoundN.** Returns the float64 nearest to `x` rounded to `n` decimal places, rounding the exact binary value
   half-even; implemented as `strconv.ParseFloat(strconv.FormatFloat(x, 'f', n, 64), 64)` (research P2). `NaN`,
   `±Inf` and `-0.0` are returned unchanged (`round(inf, 4)` is `inf`).
3. **F.** For finite `x` returns `strconv.FormatFloat(x, 'f', prec, 64)`, which equals Python `format(x, f".{prec}f")`
   for every finite value, including a negative zero result (`-0.0` → `-0`, `-0.4` at prec 0 → `-0`, `-0.004` at
   prec 2 → `-0.00`). Non-finite: `NaN` (either sign) → `nan`, `+Inf` → `inf`, `-Inf` → `-inf`, regardless of `prec`.
4. All three are pure and deterministic.

## Invariants

1. `math.Round` is never used at a status-line site; deliberate half-up sites (SL:426, 675) are written
   `pyfmt.Int(x + 0.5)` (BC-5.01.003), never `math.Round`.
2. `F` output is ASCII and never contains `NaN`, `+Inf` or an exponent.
3. Each helper has a committed CPython-generated expectation table under `internal/pyfmt/testdata/` produced by the
   pinned 3.11 oracle (OD-103, OD-104).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `Round(0.5)`, `Round(1.5)`, `Round(2.5)`, `Round(-0.5)` | `0`, `2`, `2`, `0` |
| EC-002 | `Round(999.5)` | `1000` |
| EC-003 | `Round(12.5)` (composition `round(n / total * 100)`, SL:1171) | `12` |
| EC-004 | `Round(NaN)` / `Round(+Inf)` | `ErrValue` / `ErrOverflow` (the caller maps to degraded where Python does not catch) |
| EC-005 | `RoundN(2.675, 2)` / `RoundN(0.125, 2)` | `2.67` / `0.12` (binary value below the tie; exact tie to even) |
| EC-006 | `RoundN(1.00005, 4)` | `1.0001` |
| EC-007 | `F(0.005, 2)` | `0.01` (binary 0.005 is slightly above the tie) |
| EC-008 | `F(1e16, 1)` | `10000000000000000.0` (no exponent in 'f') |
| EC-009 | `F(1e300, 0)` | 301-digit string starting `1000000000000000052…` |
| EC-010 | `F(-NaN, 1)` | `nan` (sign of NaN not printed) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `Round(2.5)`; `Round(999.5)` | `2`; `1000` | happy-path |
| `F(2.675, 2)`; `F(0.125, 2)`; `F(999.5, 0)`; `F(1.5, 0)`; `F(0.5, 0)` | `2.67`; `0.12`; `1000`; `2`; `0` | happy-path |
| `F(-0.0, 0)`; `F(-0.4, 0)`; `F(-1e-9, 0)` | `-0`; `-0`; `-0` | edge-case |
| `F(NaN, 1)`; `F(+Inf, 0)`; `F(-Inf, 2)` | `nan`; `inf`; `-inf` | edge-case |
| `RoundN(+Inf, 4)`; `RoundN(NaN, 4)`; `RoundN(-0.0, 4)` | `+Inf`; `NaN`; `-0.0` | edge-case |
| `Round(NaN)`; `Round(-Inf)` | `ErrValue`; `ErrOverflow` | error |

All values verified 2026-11-15 against CPython 3.11.7 (`round`, `format`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-023 | `F(x, p)` equals the CPython oracle for every finite x in a 2M-sample random set and all boundary rows | Go property test (testing/quick) + oracle table |
| VP-023 | `Round(x)` equals `math.RoundToEven(x)` for finite x with magnitude below 2^53 and is exact beyond | Go property test (testing/quick) |
| VP-023 | `RoundN(RoundN(x, n), n) == RoundN(x, n)` | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 (byte parity of rendered numbers) |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/num.go` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/num.go (Round/RoundN/F) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103 (one `internal/pyfmt` package, four files); design IM-05, IM-06; pitfalls PR-01, PR-02. Legacy call sites it serves: SL:1171 (`round`), SL:234 (`round(usd, 4)`), `.Nf` sites SL:435-437, 479, 522, 599, 616, 625, 635, 700, 741, 761-762, 778-783, 795, 813-819, 857, 870-873, 882-885 (`_fmt_tokens`, the subagent token segment; ADV-P3-D10) |

## Related BCs (Recommended)

- BC-1.02.007 — consumed by (composition % rounds half-even)
- BC-1.05.007, BC-1.05.009 — consumed by (`$` formatting, `round(usd, 4)` in the cost history)
- BC-5.01.003 — related to (`Int` used for half-up sites)
- BC-5.02.001 — related to (float `repr`, a different spelling from `F`)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-num` — internal/pyfmt/num.go (Round/RoundN/F) (Python number helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt num (design step S1)

## VP Anchors (Recommended)

- VP-023 — `F` equals CPython on finite values

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/num.go (Round/RoundN/F)` (BC-COMPONENT-MAP: py/num.go (Round/RoundN/F) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
