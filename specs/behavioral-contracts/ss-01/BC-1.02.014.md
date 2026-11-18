---
document_type: behavioral-contract
level: L3
version: "1.5.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "2b4b237"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_fmt_lines (SL:849-860), render_lane (SL:534-537)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-019
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.4.1 pass-3 remediation (ADV-P3-B05/B07/B18): float_div converts the int operand to float first (OverflowError at the int->float threshold, double-rounded quotient); OD-162 justification reworded to its actual test; EC-004 tie wording fixed; 2026-11-18T02:00:00Z"
  - "1.4.2 pass-4 remediation (ADV-P4-B04): EC-013 names CP-O03; canonical OV overflow vector added; 2026-11-18T03:00:00Z"
  - "1.5 pass-5 remediation (ADV-P5-B12/B05): units.lines thresholds cited at SL:856/858 (was the stale SL:866-867); EC-013 scoped to the positive side and notes a huge negative renders exactly via str(n) (SL:860, oracle-verified); 2026-11-18T05:42:56Z"
  - "1.5.1 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) — pass-4 stamp re-dated ascending (it predated pass-3's); no behavioral change"
  - "1.5.2 pass-6 remediation (ADV-P6-B08): the lines arrows are named as the registry keys statusline.glyphs.lines_up / lines_down instead of the wildcard statusline.glyphs.* (Config keys row); 2026-11-19T04:00:00Z"
  - "1.5.3 pass-8 remediation (ADV-P8-B05, orchestrator call 10): Inv 3 registered range respelled to the interface-definitions canon — units.lines = {`k`} (the `M` divisor is a registered render semantic, not an accepted value); no behavioral change; 2026-11-19T08:00:00Z"
  - "1.5.4 2026-11-20T18:00:00Z: pass-10 remediation (ADV-P10-B03): Verification Properties gains the VP-001 ladder row for the CP-O03 overflow degrade (EC-013) — 29-byte line, exit 0; reciprocal VP-001 bcs: sync is the architect's"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.014: Lines segment formats via _fmt_lines

## Description

When the session has added or removed lines, row 1 shows `▲<added>/▼<removed>` (green up,
dim slash, red down). Each count is formatted by `_fmt_lines`: Python `int()` of the value
(truncating floats, parsing numeric strings), exact below 10,000, whole thousands with `k`
below 1,000,000, then millions with one decimal and `M`; a value `int()` rejects renders
`?`.

Notation: `\e` is the byte 0x1B.

## Preconditions

1. `cost = d.cost` if truthy else `{}` (a truthy non-object degrades, EC-010).
2. `la = cost.total_lines_added` if truthy else `0`; `lr = cost.total_lines_removed` if
   truthy else `0`.
3. `statusline.units.lines` thresholds: 10,000 (`>=` → k) and 1,000,000 (`>=` → M).

## Postconditions

1. If neither `la` nor `lr` is truthy → no segment.
2. Otherwise segment = `\e[32m▲` + fmt(la) + `\e[0m\e[2m/\e[0m\e[31m▼` + fmt(lr) + `\e[0m`.
3. `fmt(n)` with the registered semantics of the single Text key `statusline.units.lines`
   (thresholds 10,000 (`>=` → k) and 1,000,000 (`>=` → M), per interface-definitions):
   1. `n = int(n)` with Python semantics (`pyfmt.ParseInt` for strings — surrounding
      whitespace and `_` digit separators accepted, BC-5.01.002; floats truncate toward
      zero; `true` → 1); a TypeError or ValueError (non-numeric string such as `"1e3"`,
      list, object, NaN) → return `?`.
   2. `n >= 1,000,000` → F(n / 1e6, 1) + `M` (Python `'f'`, half-even on the binary value). The
      division is CPython `float_div`: an int operand is converted to float FIRST, so
      `OverflowError` fires at the int→float threshold |n| ≥ 2**1024 − 2**970 ≈ 1.8·10³⁰⁸
      (oracle-verified 2026-11-18, e.g. 10**310), and the quotient is the double-rounded
      `float(n)/1e6`, not the correctly rounded exact quotient (EC-012).
   3. `n >= 10,000` → `n // 1000` + `k` (integer floor division; the k divisor is the SI
      1000, a named constant).
   4. else → decimal `n` (negative values exact, e.g. `-20000`).
4. Position: after the limits segment, before the timer segment.

## Invariants

1. Both counts are always shown together once either is non-zero (`▲0` or `▼0` possible).
2. Rationale (D15, T-037, documented): keep row 1 narrow on big refactors (review #8.1).
3. Valid ranges (Policy 20, OD-162): `statusline.units.lines` is a unit-selector key whose
   non-default behavior cannot be defined from legacy — the thresholds (10,000 `>=` → k;
   1,000,000 `>=` → M, SL:856 and SL:858) are baked into the single derivable semantics, and no
   alternative scheme is derivable from the legacy program — so per OD-162's test its valid
   range is its registered default only; any other value is a number-range config error
   (BC-2.02.003, OD-162). Range for architect registration: units.lines = {`k`}
   (registered default, matching interface-definitions; `M` is a registered render SEMANTIC of the key, not an
   accepted value). Byte parity (vectors) is obligated at the defaults.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | 0/0, null/null, missing | no segment |
| EC-002 | 9999 / 10000 | `9999` / `10k` |
| EC-003 | 999999 / 1000000 | `999k` / `1.0M` |
| EC-004 | 1,250,000 / 1,350,000 | `1.2M` / `1.4M` (nearest rounding of the binary value; 1.35 is not a binary tie — it is 1.3500000000000000888, so `1.4` is plain nearest, not half-even) |
| EC-005 | 12345.9 / 2.9 | `12k` / `2` (truncation) |
| EC-006 | strings `"12"`, `" 42 "`, `"  -3\n"`, `"1_000"` | `12`, `42`, `-3`, `1000` |
| EC-007 | `"1e3"`, `"abc"`, `[1]`, NaN | `?` (NaN is truthy, so `▲?/▼0` shows) |
| EC-008 | `true` | `1` |
| EC-009 | negative below threshold, e.g. -20000 | `-20000` (thresholds are `>=` on signed value) |
| EC-010 | `cost` truthy non-object | AttributeError → guard line `\e[90mstatusline degraded\e[0m\n`, exit 0 |
| EC-011 | ±Infinity | OverflowError not caught → guard line (BC-1.02.026, CP-S11) |
| EC-012 | `total_lines_added` a JSON integer beyond int64 but within float64, e.g. int(1e300) | `int(n)` is exact (Python arbitrary precision); `n / 1e6` converts `n` to float first (exact here) and rounds twice — the result is `float(n)/1e6`, not the correctly rounded exact quotient (e.g. n = 2**53+1 → 9007199254.740992, where the exact quotient rounds to …93; oracle-verified 2026-11-18) → hylo reproduces the oracle bytes by emulating the double rounding (OD-156, extends OD-137; oracle: `format(int(1e300)/1e6, ".1f")` = the 298-character `……1056.0M` string) |
| EC-013 | a JSON integer beyond the int→float conversion threshold, e.g. 2·10³¹⁵ or 10**310 | **Positive side:** `n / 1e6` raises OverflowError because the int operand cannot be converted to float (|n| ≥ 2**1024 − 2**970 ≈ 1.8·10³⁰⁸; taxonomy **CP-O03**) — even though a 1e304 quotient would fit — uncaught at SL:857 → guard line (stdin-borne render overflow, OD-156; oracle-verified 2026-11-18). A huge **negative** integer never divides: it fails both `>=` tests and renders exactly via `str(n)` (SL:860; oracle-verified 2026-11-17: `_fmt_lines(−10**400)` emits the exact decimal) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15.

| Input (`cost` added, removed) | Expected segment | Category |
|-------|----------------|----------|
| 12, 3 | `\e[32m▲12\e[0m\e[2m/\e[0m\e[31m▼3\e[0m` | happy-path |
| 12345, 0 | `\e[32m▲12k\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | happy-path |
| 0, 7 | `\e[32m▲0\e[0m\e[2m/\e[0m\e[31m▼7\e[0m` | edge-case |
| 1050000, 250 | `\e[32m▲1.1M\e[0m\e[2m/\e[0m\e[31m▼250\e[0m` | edge-case |
| 9999, 10000 | `\e[32m▲9999\e[0m\e[2m/\e[0m\e[31m▼10k\e[0m` | edge-case |
| 999999, 1000000 | `\e[32m▲999k\e[0m\e[2m/\e[0m\e[31m▼1.0M\e[0m` | edge-case |
| 1250000, 1350000 | `\e[32m▲1.2M\e[0m\e[2m/\e[0m\e[31m▼1.4M\e[0m` | edge-case |
| `"12"`, `" 42 "` | `\e[32m▲12\e[0m\e[2m/\e[0m\e[31m▼42\e[0m` | edge-case |
| 12345.9, 0 | `\e[32m▲12k\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | edge-case |
| -20000, 0 | `\e[32m▲-20000\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | edge-case |
| `true`, 0 | `\e[32m▲1\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | edge-case |
| 0, 0 | no segment | edge-case |
| `"1e3"`, 1 | `\e[32m▲?\e[0m\e[2m/\e[0m\e[31m▼1\e[0m` | error |
| NaN, 0 | `\e[32m▲?\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | error |
| 10**310, 0 (a JSON integer ≥ OV = `2**1024 − 2**970` = 179769313486231580793728971405303415079934132710037826936173778980444968292764750946649017977587207096330286416692887910946555547851940402630657488671505820681908902000708383676273854845817711531764475730270069855571366959622842914819860834936475292719074168444365510704342711559699508093042880177904174497792) | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 (`n / 1e6` OverflowError at SL:857; CP-O03, EC-013) | error |

`_fmt_lines` direct: `10000000` → `10.0M`; `"1_000"` → `1000`; `"  -3\n"` → `-3`;
`999950` → `999k` (verified).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | fmt equals CPython `_fmt_lines` for ints in [-1e7, 1e8] sampled around thresholds and ties | property test vs CPython goldens — a bounded golden sweep on an authored fixed sampling grid, staying on VP-028 per the VP-041 scope split (VP-041 takes generator-based for-all legs only) |
| VP-028 | fmt of strings equals CPython for the BC-5.01.002 grammar corpus | table test |
| VP-028, VP-001 | The CP-O03 overflow degrade (EC-013 positive side: `n / 1e6` at or beyond the int→float threshold) stays on the never-blank ladder — exactly the 29-byte degraded line, exit 0 | table test (fault-injection row of VP-001's ladder) |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:_fmt_lines (SL:849-860); segment in render_lane SL:534-537 |
| Legacy contract | BC-SL-019 (refined with BC-SL-063 in pass-3 deep r1) |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-103 (pyfmt ParseInt/Int/F), OD-113 (theme), OD-02 (glyphs), OD-156 (beyond-int64 ints via `math/big`; render overflow → crash path), OD-162 (valid range of `statusline.units.lines`) |
| Config keys | `statusline.units.lines`, `statusline.glyphs.lines_up` (▲), `statusline.glyphs.lines_down` (▼), `statusline.theme.*` |
| Architecture Module | `internal/statusline/session.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.026 — composes with (±inf degrade)
- BC-5.01.002 — depends on (Python int grammar)
- BC-5.01.001 — depends on (`'f'` formatting)
- BC-1.02.015 — composes with (next segment)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#session` — internal/statusline/session.go (_fmt_lines) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — session widgets story

## VP Anchors (Recommended)

- VP-028 — `_fmt_lines` parity property

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_fmt_lines` SL:849-860; `render_lane` SL:534-537) |
| **Confidence** | high (pass-3 HIGH-R #8, 6 cases; r1 table) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `except (TypeError, ValueError): return "?"` (SL:854-855); `if la or lr` (SL:536)
- **documentation**: docstring SL:850-851

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; the typed `pyfmt` errors (`ErrValue` vs `ErrOverflow`) let the Go
code reproduce Python's catch list exactly (IM-07).
