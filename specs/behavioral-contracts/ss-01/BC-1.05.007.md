---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r7.md
  - ../semport/hylo-legacy/statusline-target-design.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-082"
parity_class: "byte-exact"
confidence: "H"
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

# Behavioral Contract BC-1.05.007: $ and $/h number formatting

## Description

The numbers inside the cost segment are formatted exactly as Python's fixed-point
format specs: `$` with `.2f` of the raw `total_cost_usd`, `$/h` with `.1f` of the
computed rate, and `⛏` with `.2f` of `eq`. Rounding is of the exact binary value
(correctly rounded, so ties in decimal look like half-even or half-down), never
`math.Round`, and non-finite values print Python's spelling.

## Preconditions

1. The cost segment exists (BC-1.05.001) and, for `$/h`, the rate gate passed
   (BC-1.05.002); for `⛏`, BC-1.05.003 decided to show a number.
2. Formatting goes through `pyfmt.F(x, prec)` (`internal/pyfmt` `[num]`, OD-103):
   `strconv.FormatFloat(x, 'f', prec, 64)` for finite values, which matches Python
   for every finite double including `-0`, plus Python spellings for non-finite values.

## Postconditions

1. `$` text = `"$" + F(usd, 2)` (SL:616). A bool `true` formats as `1.00`; an int
   formats as its float value.
2. `$/h` text = `" $" + F(r, 1) + "/h"` with `r = usd / (api_ms / 3.6e6)` (SL:623, 625).
3. `⛏` text = `" ⛏" + F(eq, 2)` (SL:635).
4. Non-finite: `+inf` → `inf` (so `$inf`, `$inf/h`, `⛏inf`). NaN never reaches `$`
   (the `usd > 0` guard is false for NaN); NaN `r` is unreachable because a NaN
   `api_ms` fails the `>= 300000` gate.
5. No thousands separators, no exponent form: `1e16` → `10000000000000000.00`.

## Invariants

1. Formatting never changes the value used for colouring (colours use raw values,
   BC-1.05.001/002).
2. Go never uses `fmt` `%f` directly on these values (`NaN`/`+Inf` spelling differs,
   design IM-05).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | usd 0.125 | `$0.12` |
| EC-002 | usd 0.995 | `$0.99` |
| EC-003 | usd 1.005 | `$1.00` |
| EC-004 | usd 2.675 | `$2.67` |
| EC-005 | usd 999.995 | `$1000.00` |
| EC-006 | usd `true` | `$1.00` |
| EC-007 | usd +inf | `$inf`; with api 600000 → ` $inf/h` |
| EC-008 | usd 1e16, api 600000 | `$10000000000000000.00`, ` $60000000000000000.0/h` |
| EC-009 | api +inf | `r = 0.0` → ` $0.0/h` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| usd 32.62, api 6,711,428.57 | `$32.62`, ` $17.5/h` (r = 17.497318011387254) | happy-path |
| usd 1.0, api 300,000 | `$1.00`, ` $12.0/h` | edge-case |
| usd 13.99, api 600,000 | `$13.99`, ` $83.9/h` (r = 83.94000000000001) | edge-case |
| usd 1e16, api 600,000, cold start, lane anth | `\e[33m$10000000000000000.00\e[0m\e[90m $60000000000000000.0/h\e[0m` | edge-case |
| usd NaN | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-021 | `pyfmt.F(x, p)` equals CPython `format(x, f".{p}f")` for p ∈ {1, 2} over a generated corpus (boundaries, ties, subnormals, ±0, inf) | fuzz (differential vs the oracle) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011, CAP-009 |
| L2 Domain Invariants | — |
| Architecture Module | `internal/pyfmt` num.go `F`; `internal/statusline` cost.go (BC-COMPONENT-MAP: internal/statusline/cost.go ($, $/h formats) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:601-636; formats at SL:616, 625, 635) |
| Legacy contract | BC-SL-082 (P3 deep r1 row 123; `true → $1.00` re-verified P3r7) |
| Decisions | D4, OD-103 (single `internal/pyfmt`), OD-104 (CPython 3.11 oracle) |

## Related BCs (Recommended)

- BC-1.05.001 / BC-1.05.002 / BC-1.05.003 — consumed by
- BC-1.05.008 — verified by (goldens show the number/colour mismatches)
- BC-5.01.001 — depends on (`pyfmt` Round/RoundN/F, nan/inf spellings)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#num` — internal/statusline/cost.go ($, $/h formats) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost segment (filled by story-writer)

## VP Anchors (Recommended)

- VP-021 — `F` differential equivalence

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | only via injected `Env` seams |
| **Global state access** | none (seam-injected) |
| **Deterministic** | yes for widgets, given inputs and fake seams |
| **Thread safety** | single-threaded render loop |
| **Overall classification** | mixed (core-dominant) |

Owning component `internal/statusline` (BC-COMPONENT-MAP: sl/cost.go ($, $/h formats) - ARCH-03); the ARCH-00 package table classifies the package mixed (core-dominant) - pure widgets plus the effect script (AD-03), I/O only via `Env` seams.
