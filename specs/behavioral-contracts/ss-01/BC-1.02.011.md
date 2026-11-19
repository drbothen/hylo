---
document_type: behavioral-contract
level: L3
version: "1.5.3"
status: draft
producer: product-owner
timestamp: 2026-11-17T23:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "ea236ef"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:510-522, 531-532)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-016
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.3 pass-4 remediation (ADV-P4-B04): EC-010 names CP-O02 and states the exact int->float threshold; canonical OV overflow vector added; 2026-11-17T12:00:00Z"
  - "1.4 pass-5 remediation (ADV-P5-B05): EC-010 scoped to huge positive resets_at; new EC-011 pins the huge-negative behavior — window passed at SL:506 (exact int/float compare), hidden at SL:513-514, no degrade (oracle-verified); CTV row added; 2026-11-18T05:42:56Z"
  - "1.5 pass-6 remediation (ADV-P6-B02 + B10 + B16): EC-011 and its CTV row re-vectored from −10³⁰⁰ to −OV (the negated EC-010 boundary — discriminates a float64-at-decode port; −10³⁰⁰ converted cleanly); the OV CTV row now states a numeric used_percentage so the shown window reaches SL:515; history labels version-prefixed; 2026-11-19T04:00:00Z"
  - "1.5.1 pass-8 remediation (ADV-P8-B10): EC-011's hiding mechanism cited precisely — SL:510 widget drop for the canonical 5h-absent vector, SL:513-514 per-window continue when the other window is reported; outcome unchanged; 2026-11-19T08:00:00Z"
  - "1.5.2 2026-11-20T18:00:00Z: pass-10 remediation (ADV-P10-B03): Verification Properties gains the VP-001 ladder row for the CP-O02 overflow degrade (EC-010) — 29-byte line, exit 0; reciprocal VP-001 bcs: sync is the architect's"
  - "2026-11-24T01:00:00Z (1.5.3): pass-14 remediation (ADV-P14-B06): PC5 declares the two-space inter-window joiner (SL:532) a named format constant of this widget, not config (D15 rationale, sibling of the BC-1.02.007/018 intra-segment declarations); no behavioral change"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.011: Pace and absolute colour bands

## Description

Each reported plan window renders as `<label><pct>%` coloured by risk. Once at least 10 %
of the window has elapsed, the colour follows the projected use at reset (pct ÷ elapsed
share): red above 100 %, yellow from 80 %, grey otherwise. Earlier in the window, or when
no reset time is known, absolute bands apply: red above 90 %, yellow above 70 %, grey
otherwise. Reported windows are joined by two spaces, 5h first.

Notation: `\e` is the byte 0x1B; `T = 1800000000.0`; `D7` = 604800.

## Preconditions

1. At least one window is reported (BC-1.02.010); each reported window carries
   `label`, `length`, clamped `pct` in [0, 100], and `reset` (number or None).
2. Config resolved: `statusline.limits.projection_min_elapsed` (0.10),
   `statusline.limits.projected_bands` (red `> 100`, yellow `>= 80`),
   `statusline.limits.absolute_bands` (red `> 90`, yellow `> 70`); colours RED `\e[31m`,
   YELLOW `\e[33m`, GREY `\e[90m` from `statusline.theme.*`.

## Postconditions

1. `rem = reset - now` if `reset` is not None, else None;
   `elapsed = 1.0 - rem / length` if `rem` is not None, else None.
2. If `elapsed` is not None and `0.10 <= elapsed <= 1.0`: `proj = pct / elapsed`;
   `col = RED if proj > 100 else YELLOW if proj >= 80 else GREY`.
3. Else: `col = RED if pct > 90 else YELLOW if pct > 70 else GREY`.
4. Window text = `col` + `label` + F(pct, 0) + `%` + `\e[0m` (F = Python `'f'`, half-even,
   BC-5.01.001), followed by the countdown when BC-1.02.012 applies.
5. Limits segment = the window texts joined by exactly two spaces; it is one row-1
   element, placed after the cache-hit segment. The two-space inter-window joiner is a **named format
   constant** of this widget, not config (D15 rationale: intra-segment output markup, parity-bound at
   two bytes; the theme's `statusline.theme.separator` governs inter-segment separators, not
   intra-segment markup — no ruling mints a key for this site).

## Invariants

1. Projection is used only inside [0.10, 1.0] elapsed; outside it (early window, reset
   further than one window ahead, unknown reset) absolute bands apply.
2. Countdown colour equals the window colour.
3. Rationale (D15, T-032..T-034, documented): projection is noise in the first 10 % of a
   window (review #12 revisit); 80/100 = will use nearly all / runs out before reset;
   70 = pace, 90 = throttling imminent (review #12.3).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | proj exactly 80 (40 % at half-elapsed) | YELLOW (`>=`) |
| EC-002 | proj exactly 100 | YELLOW (red needs `> 100`) |
| EC-003 | absolute pct exactly 70 / 90 | GREY / YELLOW (strict `>`) |
| EC-004 | elapsed 0.05 (rem = 0.95·length) | absolute bands |
| EC-005 | rem = 1.1·length (elapsed negative) | absolute bands; countdown still shown (≤ 1.15) |
| EC-006 | rem = 0.9·length exactly | elapsed 0.09999999999999998 → absolute (BC-1.02.024) |
| EC-007 | pct 120 / -5 | clamped to 100 / 0 before banding and text |
| EC-008 | pct 44.5 / 45.5 | text `44%` / `46%` (half-even) |
| EC-009 | pct NaN | `7dnan%` grey, countdown kept (BC-1.02.024 family, pass-3 r1 BC-SL-061) |
| EC-010 | `resets_at` a JSON integer at or beyond the int→float conversion threshold \|n\| ≥ 2**1024 − 2**970 **on the positive side** (oracle-verified 2026-11-17: `2**1024 − 2**970 − 1` converts, `2**1024 − 2**970` raises; e.g. 10³⁰⁹) | `reset - now` raises OverflowError at SL:515 (mixed int/float arithmetic converts the int) → guard line (stdin-borne render overflow, OD-156; taxonomy **CP-O02**) |
| EC-011 | `resets_at` a huge **negative** JSON integer at the EC-010 magnitude, e.g. −OV (pass-6 ADV-P6-B02: the vector is now the negated EC-010 boundary, so a port that converts to float64 at decode overflows and diverges — the former −10³⁰⁰ converted cleanly and discriminated nothing) | no OverflowError, no degrade: the exact int/float compare `reset <= now_rl` (SL:506; −OV ≤ 1.7e9 is True — the comparison never converts the int) marks the window passed (pct = None) and the window is hidden — for the canonical 5h-absent vector the widget is dropped by the SL:510 `any(...)` check; the SL:513-514 per-window continue applies when the other window is reported (BC-1.02.010 unreported rule); SL:515 is never reached (oracle-verified 2026-11-17: loop simulation with resets_at = −10**400 hides the widget; re-verified 2026-11-18 with −OV: `-OV <= 1.7e9` is True, while `float(-OV)` raises OverflowError) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15; `rate_limits` shown, prefixes
`claude-sonnet`.

| Input | Expected limits segment | Category |
|-------|----------------|----------|
| 5h 31 % reset `T+9660`, 7d 44 % reset `T+15480` | `\e[90m5h31%\e[0m \e[90m->2h41m\e[0m  \e[90m7d44%\e[0m \e[90m->4h18m\e[0m` | happy-path |
| 7d 75 % reset `T+0.5·D7` (proj 150) | `\e[31m7d75%\e[0m \e[31m->3d12h\e[0m` | happy-path |
| 7d 40 % reset `T+0.5·D7` (proj 80) | `\e[33m7d40%\e[0m \e[33m->3d12h\e[0m` | edge-case |
| 7d 50 % reset `T+0.5·D7` (proj 100) | `\e[33m7d50%\e[0m \e[33m->3d12h\e[0m` | edge-case |
| 7d 51 % reset `T+0.5·D7` (proj 102) | `\e[31m7d51%\e[0m \e[31m->3d12h\e[0m` | edge-case |
| 7d 39 % reset `T+0.5·D7` | `\e[90m7d39%\e[0m \e[90m->3d12h\e[0m` | edge-case |
| 7d 75 % reset `T+0.95·D7` (early) | `\e[33m7d75%\e[0m \e[33m->6d15h\e[0m` | edge-case |
| 7d 75 % reset `T+1.1·D7` | `\e[33m7d75%\e[0m \e[33m->7d16h\e[0m` | edge-case |
| 7d 70 % no reset / 71 % / 90 % / 91 % | `\e[90m7d70%\e[0m` / `\e[33m7d71%\e[0m` / `\e[33m7d90%\e[0m` / `\e[31m7d91%\e[0m` | edge-case |
| 7d 120 % no reset | `\e[31m7d100%\e[0m` | edge-case |
| 7d -5 % no reset | `\e[90m7d0%\e[0m` | edge-case |
| 7d 44.5 % / 45.5 % no reset | `\e[90m7d44%\e[0m` / `\e[90m7d46%\e[0m` | edge-case |
| 7d `used_percentage` `"44"` | none (unreported, BC-1.02.010) | error |
| 5h `used_percentage` 31, `resets_at` = OV (`2**1024 − 2**970` = 179769313486231580793728971405303415079934132710037826936173778980444968292764750946649017977587207096330286416692887910946555547851940402630657488671505820681908902000708383676273854845817711531764475730270069855571366959622842914819860834936475292719074168444365510704342711559699508093042880177904174497792, the smallest positive integer that fails float conversion; pass-6 ADV-P6-B10: a numeric `used_percentage` is now stated, so the window is shown and reaches SL:515) | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 (`reset - now` OverflowError at SL:515; CP-O02, EC-010) | error |
| 7d `resets_at` = −OV (−`2**1024 − 2**970`, the negated EC-010 boundary; decimal digits as the positive row above), 5h absent | no limits segment (the window is marked passed at SL:506 and hidden, no degrade; EC-011) | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | Colour equals the oracle over a grid pct ∈ {0..100 step 0.5} × rem/length ∈ {0.0001..1.2 step 0.01} for both windows | table test vs CPython goldens |
| VP-028 | Windows joined by exactly two spaces, 5h before 7d | table test |
| VP-028, VP-001 | The CP-O02 overflow degrade (EC-010: `resets_at` at or beyond the int→float threshold, positive side) stays on the never-blank ladder — exactly the 29-byte degraded line, exit 0 | table test (fault-injection row of VP-001's ladder) |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane (SL:510-522 bands and text; SL:531-532 join) |
| Legacy contract | BC-SL-016 (refined + BC-SL-061 boundary in pass-3 deep r1 §A) |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | owner redesign 2026-11-14 (SL:490-498), OD-113 (theme), OD-156 (render-time overflow → catalogued crash path) |
| Config keys | `statusline.limits.projection_min_elapsed`, `statusline.limits.projected_bands`, `statusline.limits.absolute_bands`, `statusline.limits.windows`, `statusline.theme.*` |
| Architecture Module | `internal/statusline/limits.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.010 — depends on (reported windows)
- BC-1.02.012 — composes with (countdown appended)
- BC-1.02.024 — composes with (0.9·length boundary)
- BC-6.03.001 — related to (row goldens include the limits widget)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#limits` — internal/statusline/limits.go (pace/absolute bands) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — plan-window widget story

## VP Anchors (Recommended)

- VP-028 — band grid parity

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`render_lane`, SL:510-532; rationale SL:490-498) |
| **Confidence** | high (pass-3 HIGH-R #12 revisit, 7 cases; re-run 2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `0.10 <= elapsed <= 1.0` (SL:517)
- **documentation**: comment SL:490-498

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads clock (injected) and config |
| **Deterministic** | yes given `now` |
| **Thread safety** | n.a. |
| **Overall classification** | pure (given `now`) |

#### Refactoring Notes

No refactoring needed; compute `rem` and `elapsed` in float64 with the same operation order
as the source (no FMA contraction, IM-10).
