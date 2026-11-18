---
document_type: behavioral-contract
level: L3
version: "1.4.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T21:21:12Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "a99539e"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-057"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "consolidated pass-2 follow-up: EC-011 overflow condition corrected (int operand converted to float first; e.g. 2\xB710\xB3\u2070\u2078) + taxonomy id CP-O01, 2026-11-17T21:21:41Z"
  - "pass-4 remediation (ADV-P4-B13/B04): repeated modified entry deduplicated; canonical OV overflow vector added; 2026-11-18T03:00:00Z"
  - "1.4.1 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) \u2014 pass-4 stamp re-dated ascending (it predated pass-3's); no behavioral change"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.020: Thermometer quirks (/0K, /1000K, NaN crash)

> Byte notation used below: `\e` = ESC (0x1B). All other characters are literal UTF-8.

## Description

The context thermometer (BC-1.02.006) has legacy quirks that the port must reproduce byte for byte: the `K`
denominator rounds half-even with no unit promotion (`/0K` for small windows, `/1000K` just below one million), odd
values of `used_percentage` and `context_window_size` render through Python semantics, and a NaN percentage or a
non-numeric truthy window size crashes the render into the degraded line.

## Preconditions

1. `cw` = stdin `context_window` object (or `{}`); `pct = cw.used_percentage` is an int or float (otherwise the
   thermometer is absent, BC-1.02.006).
2. `total = cw.context_window_size or 0` (Python truthiness).
3. Default theme (OD-113) and `statusline.context.*` / `statusline.units.context` defaults (T-027..T-029).

## Postconditions

1. `pct` is clamped `Min(Max(pct, 0.0), 100.0)` in source argument order (IM-09); `filled = min(int(pct/10 + 0.5), 10)`.
2. Denominator: `total >= 1e6` → `\e[2m/` + `format(total/1e6, ".1f")` + `M\e[0m`; else `total > 0` →
   `\e[2m/` + `format(total/1000, ".0f")` + `K\e[0m` (half-even, no promotion to `M`); else no denominator.
3. Quirks, exactly:
   1. `0 < total <= 500` → `/0K` (500/1000 = 0.5 rounds to even 0); 501 → `/1K`.
   2. `999500 <= total < 1e6` → `/1000K`; 999499 → `/999K`.
   3. `total = true` → `/0K` (True is 1).
   4. `total` = NaN → no denominator (NaN is truthy but fails both comparisons).
   5. `pct = true` → `1%`, 0 filled cells, no colour.
   6. `pct = +Infinity` → `100%`, 10 filled cells, BOLDRED `\e[1;91m`.
   7. `pct = -0.0` → `Max(-0.0, 0.0)` keeps `-0.0` (0.0 is not greater), so the text is `-0%` with 0 cells.
4. `pct` = NaN → `int(nan/10 + 0.5)` raises ValueError at SL:426 (CP-S06) → whole stdout is the 29-byte degraded line
   (BC-1.01.001).
5. `total` a truthy non-number (string, non-empty list or object) with numeric `pct` → `total >= 1e6` raises TypeError
   at SL:435 (CP-S07) → degraded line.

## Invariants

1. The number text is always `format(pct, ".0f")` of the clamped value (half-even).
2. The degraded outcomes keep earlier side effects (git cache write precedes the thermometer, BC-1.01.009).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `total = 500` / `500.0` | `/0K` |
| EC-002 | `total = 999999` | `/1000K` |
| EC-003 | `total` absent, `null` or 0 | no denominator |
| EC-004 | `total = true` | `/0K` |
| EC-005 | `total` = NaN | no denominator |
| EC-006 | `pct = true` | `1%`, 0 cells |
| EC-007 | `pct = +Infinity` | `100%`, 10 cells, `\e[1;91m` |
| EC-008 | `pct = -0.0` (JSON `-0.0`; JSON `-0` is int 0) | `-0%`, 0 cells |
| EC-009 | `pct` = NaN | degraded (CP-S06) |
| EC-010 | `total = "x"` or `[1]` | degraded (CP-S07) |
| EC-011 | `context_window_size` above float max (~1.8e308), e.g. 2·10³⁰⁸ | `total >= 1e6` compares exact; CPython converts the int operand to float first, so `total / 1e6` raises OverflowError at SL:435 (taxonomy CP-O01) → degraded line (stdin-borne render overflow, OD-156); a smaller giant such as 10³⁰⁸ renders a long `/…M` denominator with no error |

## Canonical Test Vectors

Output is the exact `fmt_ctx` string (thermometer segment). `G` below abbreviates the empty cell `\e[90m▱`.

| Input (`used_percentage`, `context_window_size`) | Expected Output | Category |
|-------|----------------|----------|
| 50.4, 500 | `\e[38;2;159;204;30m▰\e[38;2;182;204;30m▰\e[38;2;204;202;30m▰\e[38;2;204;179;30m▰\e[38;2;204;156;30m▰` + `G`×5 + `\e[0m \e[38;2;204;144;30m50%\e[0m\e[2m/0K\e[0m` | happy-path (quirk /0K) |
| 0, 999999 | `G`×10 + `\e[0m 0%\e[0m\e[2m/1000K\e[0m` | edge-case (/1000K) |
| 50, 999499 | 5 heat cells + `G`×5 + `\e[0m 50%\e[0m\e[2m/999K\e[0m` | edge-case |
| 84.5, 501 | 8 heat cells + `G`×2 + `\e[0m \e[38;2;204;66;30m84%\e[0m\e[2m/1K\e[0m` | edge-case (half-even text) |
| true, 1000000 | `G`×10 + `\e[0m 1%\e[0m\e[2m/1.0M\e[0m` | edge-case |
| +Infinity, 1000000 | 10 heat cells (`(i+0.5)*10` colours) + `\e[0m \e[1;91m100%\e[0m\e[2m/1.0M\e[0m` | edge-case |
| 50, NaN | 5 heat cells + `G`×5 + `\e[0m 50%\e[0m` | edge-case |
| 50, true | 5 heat cells + `G`×5 + `\e[0m 50%\e[0m\e[2m/0K\e[0m` | edge-case |
| -0.0, 1000 | `G`×10 + `\e[0m -0%\e[0m\e[2m/1K\e[0m` | edge-case |
| NaN, 1000 | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error (CP-S06) |
| 50, `"x"` | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error (CP-S07) |
| 50, OV with OV = `2**1024 − 2**970` = 179769313486231580793728971405303415079934132710037826936173778980444968292764750946649017977587207096330286416692887910946555547851940402630657488671505820681908902000708383676273854845817711531764475730270069855571366959622842914819860834936475292719074168444365510704342711559699508093042880177904174497792 (the smallest positive integer that fails float conversion; any int ≥ OV overflows) | whole stdout = `\e[90mstatusline degraded\e[0m\n`, exit 0 (`total >= 1e6` compares exact; `total / 1e6` raises OverflowError at SL:435; CP-O01, EC-011) | error |

"5 heat cells" = the first five cell colours of BC-1.02.019 each followed by `▰`. Pinned 2026-11-15 by calling the
legacy `fmt_ctx` under CPython 3.11 (oracle, OD-104). The `-0.0` vector is a new pin from this run (not listed in
the legacy pass-3 rows).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | For integer totals 1..2,000,000 the denominator equals the oracle's | generated table vs oracle |
| VP-028, VP-001 | NaN percentage and non-numeric truthy total degrade | table test |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/context.go`; BC-COMPONENT-MAP: internal/statusline/context.go (thermometer quirks) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:fmt_ctx (SL:418-437; crash sites SL:426 CP-S06, SL:435 CP-S07) |
| Legacy contract | BC-SL-057 (deep pass-3 round 1, new) |
| Config keys | `statusline.context.{cells, plain_max, red_from}` (T-027, T-028), `statusline.units.context` (T-029), `statusline.theme.*` |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.006 — refines (thermometer and denominator)
- BC-1.02.019 — depends on (`heat` colours)
- BC-1.01.001 — related to (degraded line)
- BC-5.01.001 — depends on (`pyfmt.F` half-even, `-0` spelling)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/context.go (thermometer quirks) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-028 — denominator table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (fmt_ctx, SL:418-437) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(pct, (int, float))` (SL:420)
- **inferred**: Python float formatting and comparison semantics, pinned against the oracle

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config only |
| **Deterministic** | yes |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

Use `pyfmt.F`, `pyfmt.Int` (typed `ErrValue` → `errDegraded`), `pyfmt.Max/Min`; never `math.Round`/`math.Max`.
