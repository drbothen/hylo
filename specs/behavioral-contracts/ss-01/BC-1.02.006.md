---
document_type: behavioral-contract
level: L3
version: "1.4"
status: draft
producer: product-owner
timestamp: 2026-11-17T21:21:12Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "da302c2"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:fmt_ctx (SL:418-437)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-011
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["consolidated pass-2 follow-up: EC-010 overflow condition corrected (CPython converts the int operand to float first; e.g. 2·10³⁰⁸) + taxonomy id CP-O01", "consolidated pass-2 follow-up: EC-010 overflow condition corrected (CPython converts the int operand to float first; e.g. 2·10³⁰⁸) + taxonomy id CP-O01, 2026-11-17T21:21:41Z"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.006: Context thermometer and its denominator

## Description

When stdin reports a numeric `context_window.used_percentage`, row 1 shows a 10-cell
context thermometer (filled cells coloured along the heat gradient, empty cells grey), the
percentage (uncoloured up to 50 %, heat-coloured above 50 %, bold red from 85 %), and a
dim denominator giving the window size in `M` (one decimal) or `K` (whole thousands).

Notation: `\e` is the byte 0x1B.

## Preconditions

1. `cw = d.context_window` if truthy else `{}` (a truthy non-object degrades, EC-008).
2. `pct = cw.used_percentage`; the widget renders only when `pct` is a JSON number
   (Python `int`/`float`, booleans included).
3. `total = cw.context_window_size` if truthy else `0`.
4. Config resolved: `statusline.context.cells` (10), `statusline.context.plain_max`
   (50, operator `>`), `statusline.context.red_from` (85, operator `>=`),
   `statusline.units.context` (registered semantics: denominators divide by 1e6 → `M`,
   else by the SI 1000 → `K`), `statusline.theme.heat`.

## Postconditions

1. If `pct` is not a number → no segment.
2. `pct = Min(Max(pct, 0.0), 100.0)` (NaN-order-preserving `pyfmt.Max/Min`, IM-09).
3. With `n = cells` and `d = 100.0/n` (exactly 10.0 at the default): `filled =
   min(Int(pct/d + 0.5), n)` — explicit half-up, never `math.Round` (IM-06).
4. Bar = for `i` in `0..n-1`: `truecolor(heat((i+0.5)*d)) + "▰"` if `i < filled`, else
   `\e[90m▱`; then `\e[0m`. With the default heat theme the 10 cell colours are, in order,
   `\e[38;2;159;204;30m`, `\e[38;2;182;204;30m`, `\e[38;2;204;202;30m`,
   `\e[38;2;204;179;30m`, `\e[38;2;204;156;30m`, `\e[38;2;204;133;30m`,
   `\e[38;2;204;110;30m`, `\e[38;2;204;87;30m`, `\e[38;2;204;64;30m`,
   `\e[38;2;204;42;30m` (heat itself: BC-1.02.019).
5. Number colour `col`: `\e[1;91m` if `pct >= red_from`; else `truecolor(heat(pct))` if
   `pct > plain_max`; else `""` (resolved values of PC4; 85 / 50 at the defaults).
6. Denominator: `\e[2m/` + F(total/1e6, 1) + `M\e[0m` if `total >= 1e6`; else
   `\e[2m/` + F(total/1000, 0) + `K\e[0m` if `total > 0`; else `""` — the registered
   semantics of `statusline.units.context` (`1e6 → M`, else `K`; the K divisor is the SI
   1000, a named constant) (F = Python `'f'`
   formatting, half-even on the binary value, BC-5.01.001).
7. Segment = bar + `" "` + col + F(pct, 0) + `"%"` + `\e[0m` + denominator. The reset after
   the number is present even when `col` is empty.
8. Position: after the project label, before composition (BC-1.02.007).

## Invariants

1. Exactly 10 cells (with the default `cells`); filled count is in 0..10.
2. The cell colours depend only on cell index, never on `pct`.
3. Valid ranges (Policy 20, OD-162): legacy bakes every value this widget reads —
   `statusline.context.cells` (10), `statusline.context.plain_max` (50 `>`),
   `statusline.context.red_from` (85 `>=`), `statusline.units.context` (`1e6 → M`, else
   `K`) — and defines no override for any of them, so each key's valid range is its
   default only; any other value is a number-range config error (BC-2.02.003, OD-162).
   Assumed ranges for architect registration: cells = {10}, plain_max = {50},
   red_from = {85}, units.context = {`K`}. Byte parity (vectors, VP sweeps) is obligated
   at the defaults.
4. Rationale (D15, design T-027..T-029): 10 cells half-up (review #5.2: half-even gave
   45 % → 4 cells but 55 % → 6); 50 / 85 thresholds (85 % leaves ~117K tokens before the
   ~967K auto-compact of a 1M window, review #5.1; documented); M/K are SI units
   (convention).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `used_percentage` null/missing/string `"45"` | no segment |
| EC-002 | pct 44.9 | 4 filled cells (4.49+0.5 → 4), text `45%` (half-even format), no colour |
| EC-003 | pct exactly 50 | uncoloured (`> 50` required) |
| EC-004 | pct exactly 85 | `\e[1;91m85%` |
| EC-005 | pct -3 | clamped to 0: 0 cells, `0%` |
| EC-006 | `context_window_size` 0/missing/null | no denominator |
| EC-007 | total 999999 | `/1000K` (K branch, half-even on 999.999); quirks `/0K`, `True`, NaN → BC-1.02.020 |
| EC-008 | `context_window` a truthy non-object (`"x"`) | AttributeError → guard line `\e[90mstatusline degraded\e[0m\n`, exit 0 |
| EC-009 | pct NaN; non-numeric truthy total | crash cases CP-S06 / CP-S07 → guard line (BC-1.02.020) |
| EC-010 | `context_window_size` above float max (~1.8e308), e.g. 2·10³⁰⁸ | `total >= 1e6` compares exact (no error); CPython converts the int operand to float first, so `total / 1e6` raises OverflowError at SL:435 (taxonomy CP-O01) → guard line (CP-S07 family, BC-1.02.020; stdin-borne render overflow, OD-156) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15. `C0..C9` = the ten cell colour
prefixes listed in Postcondition 4; `E` = `\e[90m▱`.

| Input (`context_window`) | Expected segment | Category |
|-------|----------------|----------|
| `{"used_percentage":45,"context_window_size":1000000}` | `C0▰C1▰C2▰C3▰C4▰` + `E`×5 + `\e[0m 45%\e[0m\e[2m/1.0M\e[0m` | happy-path |
| `{"used_percentage":55,"context_window_size":200000}` | `C0▰`..`C5▰` + `E`×4 + `\e[0m \e[38;2;204;133;30m55%\e[0m\e[2m/200K\e[0m` | happy-path |
| `{"used_percentage":50,"context_window_size":200000}` | `C0▰`..`C4▰` + `E`×5 + `\e[0m 50%\e[0m\e[2m/200K\e[0m` | edge-case |
| `{"used_percentage":44.9}` | `C0▰`..`C3▰` + `E`×6 + `\e[0m 45%\e[0m` | edge-case |
| `{"used_percentage":85,"context_window_size":1048576}` | `C0▰`..`C8▰` + `E` + `\e[0m \e[1;91m85%\e[0m\e[2m/1.0M\e[0m` | edge-case |
| `{"used_percentage":100,"context_window_size":0}` | `C0▰`..`C9▰` + `\e[0m \e[1;91m100%\e[0m` | edge-case |
| `{"used_percentage":-3,"context_window_size":1500}` | `E`×10 + `\e[0m 0%\e[0m\e[2m/2K\e[0m` | edge-case |
| `{"used_percentage":50.4,"context_window_size":500}` | `C0▰`..`C4▰` + `E`×5 + `\e[0m \e[38;2;204;144;30m50%\e[0m\e[2m/0K\e[0m` | edge-case |
| `{"used_percentage":null}` | no segment | edge-case |
| `context_window` = `"x"` | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | `filled == min(floor(pct/10 + 0.5), 10)` for all finite pct in [0,100] | property test |
| VP-028 | Visible width of the segment = 10 + 1 + len(number text) + len(denominator text) | property test with `visible()` (BC-1.01.004) |
| VP-028 | Bytes equal the oracle across a pct sweep 0..100 step 0.1 × totals {0, 500, 501, 200000, 999999, 1e6, 1048576} | table test against CPython goldens |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:fmt_ctx (SL:418-437); call site render_lane SL:463-465; heat/truecolor SL:140-148 |
| Legacy contract | BC-SL-011 (refined in pass-3 deep r1 §A) |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-113 (theme keys incl. heat), OD-103 (pyfmt), OD-156 (render-time overflow → catalogued crash path), OD-162 (valid ranges of the resolved keys) |
| Config keys | `statusline.context.cells`, `statusline.context.plain_max`, `statusline.context.red_from`, `statusline.units.context`, `statusline.theme.heat` |
| Architecture Module | `internal/statusline/context.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.019 — depends on (heat HSV colours)
- BC-1.02.020 — composes with (thermometer quirks and crash cases)
- BC-5.01.001 — depends on (half-even `'f'` formatting)
- BC-5.01.003 — depends on (Int, Max/Min NaN order)
- BC-1.02.007 — composes with (next segment)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#context` — internal/statusline/context.go (thermometer, denominator) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — context widgets story

## VP Anchors (Recommended)

- VP-028 — filled-cell formula

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`fmt_ctx`, SL:418-437) |
| **Confidence** | high (pass-3 HIGH-R #5) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(pct, (int, float))` (SL:420)
- **documentation**: comments SL:424-425, SL:430-433

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes (FMA contraction must be disabled in heat, IM-10) |
| **Thread safety** | n.a. |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
