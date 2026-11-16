---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, ../semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, ../semport/hylo-legacy/statusline-target-design.md, ../semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "0000000"
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
modified: []
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
   element, placed after the cache-hit segment.

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

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | Colour equals the oracle over a grid pct ∈ {0..100 step 0.5} × rem/length ∈ {0.0001..1.2 step 0.01} for both windows | table test vs CPython goldens |
| VP-028 | Windows joined by exactly two spaces, 5h before 7d | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane (SL:510-522 bands and text; SL:531-532 join) |
| Legacy contract | BC-SL-016 (refined + BC-SL-061 boundary in pass-3 deep r1 §A) |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | owner redesign 2026-11-14 (SL:490-498), OD-113 (theme) |
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
