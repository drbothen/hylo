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
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces Python str() of values used at legacy/dgx_statusline.py SL:442, 453; BC-SL-058)"
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

# Behavioral Contract BC-5.02.005: pyfmt.Str: Python str() of values (str unchanged, non-str via repr)

## Description

`pyfmt.Str(v Value) string` (json.go, design IM-05) reproduces Python `str()` of a decoded
value: a str is returned unchanged; anything else goes through Python `repr`, with float
repr from `pyfmt.Repr` (BC-5.01.005). Go's `fmt.Sprint` reorders cases and reformats
floats, so every `str()` site routes through this helper. Helper-level contract per OD-141
(consumer site: the model label str() of a non-str value, SL:442, 453).

## Preconditions

1. `v` is a decoded `Value` (str, int, float, bool, None, list, dict).

## Postconditions

1. str → returned unchanged, byte-identical (WTF-8 preserved, IM-11).
2. True/False/None → `True`, `False`, `None`.
3. int/float → Python repr spelling (BC-5.01.005): `str(1794615009.0)` = `1794615009.0`;
   `str(1e16)` = `1e+16`; non-finite: `nan`/`inf`/`-inf`.
4. list/dict → Python repr of the container: `str([1, "a"])` is `[1, 'a']` — single quotes,
   comma+space separators, repr of each element. Containers nest.
5. All cases pure and deterministic; equal to CPython `str(value)` for every decoded value
   shape in the generated table (OD-104 oracle discipline).

## Invariants

1. A str input is never re-quoted: `Str("x")` = `x`, never `'x'` (Python distinction of
   `str` vs `repr` for strings).
2. Container rendering reuses the same scalar repr primitive as Repr (no drift).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `Str("x")` | `x` (unchanged) |
| EC-002 | `Str(True)` | `True` |
| EC-003 | `Str(1e16)` | `1e+16` |
| EC-004 | `Str([1, "a"])` | `[1, 'a']` (repr spelling, single quotes) |
| EC-005 | `Str(NaN)` | `nan` |
| EC-006 | `Str({})` | `{}` (empty dict repr) |
| EC-007 | `Str(None)` | `None` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `Str("x")` | `x` | happy-path |
| `Str(True)` | `True` | happy-path |
| `Str([1, "a"])` | `[1, 'a']` | edge-case |
| `Str(NaN)` | `nan` | edge-case |

Expectations generated from CPython 3.11 (OD-104 oracle discipline).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-024 | `Str` equals CPython `str(value)` for every value shape (nested containers included) | CPython oracle table |
| VP-024 | A str input is returned byte-identical (WTF-8) | proptest |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-05; consumer: model label str() site SL:442, 453 (BC-1.02.021) |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| L2 Domain Invariants | DI-012 (byte parity machinery) |
| Architecture Module | `internal/pyfmt` json.go (BC-COMPONENT-MAP: internal/pyfmt/json.go (Str) — ARCH-06) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.01.005 — composes with (Repr for scalars)
- BC-1.02.021 — consumer (model label str() of a non-str value, BC-SL-058)
- BC-5.02.006 — related to (Dumps shares the escaping primitive)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#json` — internal/pyfmt/json.go (Str) (json.go helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

S-TBD — pyfmt json helpers

## VP Anchors (Recommended)

- VP-024 — str() equality table
