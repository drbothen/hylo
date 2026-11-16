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
extracted_from: "n.a. (greenfield helper; reproduces CPython repr(float) used at legacy/dgx_statusline.py cache and render sites)"
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

# Behavioral Contract BC-5.01.005: pyfmt.Repr: CPython float repr (shortest round-trip, .0 suffix, inf/nan spellings)

## Description

`pyfmt.Repr(x float64) string` (num.go) reproduces CPython 3.11 `repr(float)` — the shortest
decimal string that round-trips, two-digit signed exponents, integral values with a `.0`
suffix, and Python's `inf`/`-inf`/`nan` spellings — everywhere a float enters a cache file,
a rendered segment or a `str()` coercion (design IM-03/IM-05, pitfalls PR-07/PR-08).
Helper-level contract per OD-141.

## Preconditions

1. `x` any float64 (IEEE-754 binary64; ±0 and subnormals included).

## Postconditions

1. For finite `x` the output equals CPython `repr(x)`: the shortest decimal string `s` with
   `float(s) == x` (closest when tied), switching to scientific notation exactly when
   CPython switches — exponent < -4 or >= 16 — with a signed two-digit exponent (`1e+16`,
   `1e-05`, `1.5e-07`, `5e-324`).
2. Integral values in normal range keep the `.0` suffix: `Repr(1794615009.0)` =
   `1794615009.0`, `Repr(100.0)` = `100.0`; beyond the 16-digit threshold the scientific
   form applies (`Repr(1e16)` = `1e+16`).
3. Non-finite spellings: `Repr(NaN)` = `nan`; `Repr(+Inf)` = `inf`; `Repr(-Inf)` = `-inf`
   (never Go's `NaN`/`+Inf`).
4. `-0.0` → `-0` (Python repr; Go `strconv` 'g' gives `-0` too, but strconv is not used here).
5. Implementation: `strconv.FormatFloat(x, 'g', -1, 64)` post-processed for the Python
   spellings — exponent always signed and at least two digits, integral values forced to
   the `.0` form, and postcondition 3's non-finite spellings.

## Invariants

1. Pure; the only float→string conversion used by the cache writers (IM-03) and by
   `Str` (BC-5.02.005).
2. `float(Repr(x)) == x` exactly for every finite `x`; `-0.0` round-trips to `-0.0`.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `Repr(1e16)` | `1e+16` |
| EC-002 | `Repr(1e15)` | `1000000000000000.0` |
| EC-003 | `Repr(1e-5)` | `1e-05` |
| EC-004 | `Repr(1.5e-7)` | `1.5e-07` |
| EC-005 | `Repr(5e-324)` | `5e-324` (three-digit exponent, four-digit mantissa) |
| EC-006 | `Repr(NaN)` | `nan` |
| EC-007 | `Repr(+Inf)` / `Repr(-Inf)` | `inf` / `-inf` |
| EC-008 | `Repr(-0.0)` | `-0` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `Repr(1794615009.0)` | `1794615009.0` (cache `proc_start` form, BC-3.02.001) | happy-path |
| `Repr(1e16)` | `1e+16` | edge-case |
| `Repr(5e-324)` | `5e-324` | edge-case |
| `Repr(-Inf)` | `-inf` | edge-case |

Expectations generated from CPython 3.11 (OD-104 oracle discipline; generator in
`internal/pyfmt/testdata/gen/`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | `Repr` equals CPython `repr` for every float64 bit pattern in the generated table (incl. extremes and subnormals) | CPython oracle table |
| VP-TBD | Round-trip `float(Repr(x)) == x` for every finite pattern | proptest |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-03/IM-05, pitfalls PR-07/PR-08; consumers: every cache writer (BC-1.02.013, BC-1.03.002, BC-1.05.009, BC-1.06.001) and `Str` |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| L2 Domain Invariants | DI-012 (byte parity machinery) |
| Architecture Module | `internal/pyfmt` num.go (filled by architect) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.01.001 — related to (the `f`-spec sibling `F`; different spelling rules)
- BC-5.02.005 — composes with (Str coerces non-str values via Repr)
- BC-5.02.006 — composes with (Dumps emits floats via Repr)
- BC-1.05.009 — consumer (record_cost exact JSON format)

## Architecture Anchors (Recommended)

- `architecture/SS-05-pyfmt.md#num` — num.go helpers (TBD)

## Story Anchor (Recommended)

S-TBD — pyfmt num helpers

## VP Anchors (Recommended)

- VP-TBD — oracle-table equality, exact round-trip
