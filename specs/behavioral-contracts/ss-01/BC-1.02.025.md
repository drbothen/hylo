---
document_type: behavioral-contract
level: L3
version: "1.5.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r5.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "853ca2d"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-062"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.3 pass-3 remediation (ADV-P3-B07): Inv 3 justification reworded to OD-162's actual test (non-default behavior cannot be defined); 2026-11-18T02:00:00Z"
  - "1.4 pass-4 remediation (ADV-P4-B04/B03): EC-010 names CP-O04 with the exact int->float threshold; canonical OV overflow vector added; float64 fuzz leg re-anchored to VP-041; 2026-11-18T03:00:00Z"
  - "1.4.1 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) — pass-4 stamp re-dated ascending (it predated pass-3's); no behavioral change"
  - "1.5 pass-6 remediation (ADV-P6-B03 + B16): EC-010 bearer relabeled — CP-O04 is not stdin-borne; the huge int arrives via an integer-only transcript accumulation (CP-O06 skip never fires) or the mix cache; history labels version-prefixed; 2026-11-19T04:00:00Z"
  - "1.5.1 pass-8 remediation (ADV-P8-B05, orchestrator call 10): Inv 3 registered range respelled to the interface-definitions canon — units.tokens = {`M`} (the `k` divisor is a registered render semantic, not an accepted value); no behavioral change; 2026-11-19T08:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.025: _fmt_tok_c performs no unit promotion

> Byte notation: all characters below are literal ASCII.

## Description

`_fmt_tok_c(n)` formats a token count compactly: `float(n)`, then `.1f` + `M` from one million, `.0f` + `k` from
one thousand, `.0f` below. The unit is chosen **before** rounding, so a value that rounds up to the next unit
boundary is not promoted: `999.5` → `1000`, `999500` → `1000k`. Rounding is half-even (`2500` → `2k`).

## Preconditions

1. `n` is any value (from the transcript accumulation, or `tin or 0` / `tout or 0` in BC-1.02.018).
2. Config `statusline.units.tokens` defaults: 1000 and 1e6, operator `>=` (T-042).

## Postconditions

1. `x = float(n)` with Python's grammar (`pyfmt.ParseFloat` for strings: surrounding whitespace, underscores between
   digits, `nan`/`inf` spellings, exponents; ints and bools convert numerically). TypeError or ValueError → return `?`.
2. With the registered semantics of the single Text key `statusline.units.tokens`
   (thresholds 1,000 (`>=` → k) and 1e6 (`>=` → M), per interface-definitions, T-042):
   `x >= 1e6` → `F(x/1e6, 1)` + `M`;
   else `x >= 1000` → `F(x/1000, 0)` + `k`; else `F(x, 0)`; `F` = Python
   `format(x, ".Nf")`, half-even, Python spellings `nan`, `inf`, `-inf` (BC-5.01.001).
3. No unit promotion after rounding.

## Invariants

1. Returns `?` on TypeError/ValueError at `float(n)`; the only raise is OverflowError on
   a JSON integer beyond float64 range (e.g. 10³⁰⁹), which is uncaught here and runs into the catalogued
   crash path → guard line (OD-156). Every other failure mode returns `?` or a string.
2. NaN fails both comparisons and prints `nan`; `+inf` passes `>= 1e6` and prints `infM`; `-inf` prints `-inf`.
3. Valid ranges (Policy 20, OD-162): `statusline.units.tokens` is a unit-selector key whose
   non-default behavior cannot be defined from legacy — the thresholds (1000 `>=` → k;
   1e6 `>=` → M; T-042) are baked into the single derivable semantics — so per OD-162's test
   its valid range is its registered default only; any other value is a number-range config
   error (BC-2.02.003, OD-162). Range for architect registration: units.tokens = {`M`}
   (registered default, matching interface-definitions; `k` is a registered render SEMANTIC of the key, not an
   accepted value). Byte parity (vectors) is obligated at the defaults.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `999.5` | `1000` (not `1k`) |
| EC-002 | `999500`, `999999` | `1000k` (not `1.0M`) |
| EC-003 | `2500` | `2k` (half-even); `3500` → `4k` |
| EC-004 | `1049999` / `1050000` | `1.0M` / `1.1M` |
| EC-005 | NaN / `+inf` / `-inf` | `nan` / `infM` / `-inf` |
| EC-006 | `"1e3"`, `"1_000"`, `" 12 "`, `"nan"` | `1k`, `1k`, `12`, `nan` |
| EC-007 | `None`, `"abc"`, `[1]` | `?` |
| EC-008 | `True` | `1` |
| EC-009 | `-5` | `-5` |
| EC-010 | a JSON integer at or beyond the int→float conversion threshold \|n\| ≥ 2**1024 − 2**970 (oracle-verified 2026-11-17), e.g. 10³⁰⁹ | `float(n)` raises OverflowError (uncaught) → guard line (OD-156; taxonomy **CP-O04**). Bearer (pass-6 ADV-P6-B03: **not** stdin-borne — `_fmt_tok_c` only receives transcript/mix totals, BC-1.02.018 Inv 1, SL:576-578): the huge int arrives through an **integer-only transcript accumulation** (no float operand on the accumulation path, so the CP-O06 wrong-shape skip never fires; error-taxonomy CP-O06 row) or through the mix cache; a test author triggers it from the transcript/mix inputs, not from the current stdin JSON |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `500` | `500` | happy-path |
| `1000` | `1k` | happy-path |
| `88000000` | `88.0M` | happy-path |
| `999.4` | `999` | edge-case |
| `999.5` | `1000` | edge-case |
| `1500` | `2k` | edge-case |
| `2500` | `2k` | edge-case |
| `3500` | `4k` | edge-case |
| `999499` | `999k` | edge-case |
| `999500` | `1000k` | edge-case |
| `999999` | `1000k` | edge-case |
| `1000000` | `1.0M` | edge-case |
| `1049999` | `1.0M` | edge-case |
| `1050000` | `1.1M` | edge-case |
| `1250000` | `1.2M` | edge-case |
| NaN | `nan` | edge-case |
| `+inf` | `infM` | edge-case |
| `-inf` | `-inf` | edge-case |
| `"1e3"` | `1k` | edge-case |
| `"1_000"` | `1k` | edge-case |
| `" 12 "` | `12` | edge-case |
| `True` | `1` | edge-case |
| `-5` | `-5` | edge-case |
| `None` | `?` | error |
| `"abc"` | `?` | error |
| `[1]` | `?` | error |
| OV = `2**1024 − 2**970` = 179769313486231580793728971405303415079934132710037826936173778980444968292764750946649017977587207096330286416692887910946555547851940402630657488671505820681908902000708383676273854845817711531764475730270069855571366959622842914819860834936475292719074168444365510704342711559699508093042880177904174497792 (the smallest positive integer that fails float conversion) | `float(n)` raises OverflowError (uncaught at SL:866; full render prints the 29-byte guard line; CP-O04, EC-010) | error |

Pinned 2026-11-15 by calling the legacy `_fmt_tok_c` under CPython 3.11 (oracle, OD-104); consistent with deep
pass-3 rounds 1 and 5.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-041 | For all float64 inputs, Go output equals CPython output | fuzz vs oracle (VP-028 retains the bounded golden tables) |
| VP-028 | Overflow behavior per Inv 1: `?` on TypeError/ValueError; beyond-float64 integers raise OverflowError → guard line | table test (fuzz leg rides VP-041) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/tokens.go`; BC-COMPONENT-MAP: internal/statusline/tokens.go (no unit promotion) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:_fmt_tok_c (SL:863-873) |
| Legacy contract | BC-SL-062 (deep pass-3 round 1, new; confirmed round 5) |
| Config keys | `statusline.units.tokens` (T-042) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.018 — composes with (token segment)
- BC-5.01.001 — depends on (`F` half-even and spellings)
- BC-5.01.002 — depends on (`ParseFloat` Python grammar)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/tokens.go (no unit promotion) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-041 — float64 fuzz equality; VP-028 — golden token-format vectors

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (_fmt_tok_c, SL:863-873) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `try: float(n) except (TypeError, ValueError)` (SL:865-868)
- **documentation**: SL:864 docstring (approved mockup)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config only |
| **Deterministic** | yes |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
