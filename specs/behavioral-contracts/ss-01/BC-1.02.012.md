---
document_type: behavioral-contract
level: L3
version: "1.5.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T23:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "42cc87e"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:523-530)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-017
parity_class: byte-exact
confidence: M
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.3 pass-4 remediation (ADV-P4-B04): EC-012 names CP-O02 and states the exact int->float threshold; canonical OV overflow vector added; 2026-11-17T12:00:00Z"
  - "1.4 pass-5 remediation (ADV-P5-B05): EC-012 scoped to huge positive resets_at; new EC-013 pins the huge-negative behavior — window hidden at SL:513-514 before the SL:515 subtraction, no countdown, no degrade (oracle-verified, BC-1.02.011 EC-011); 2026-11-18T05:42:56Z"
  - "1.5 pass-6 remediation (ADV-P6-B02 + B16): EC-013 re-vectored from −10³⁰⁰ to −OV (negated EC-012 boundary, discriminating); history labels version-prefixed; 2026-11-19T04:00:00Z"
  - "1.5.1 pass-8 remediation (ADV-P8-B08/B10): new Inv 4 pins the `->` countdown prefix as a named format constant, not config (D15); EC-013's hiding mechanism cited precisely — SL:510 widget drop for the canonical 5h-absent vector, SL:513-514 per-window continue when the other window is reported; 2026-11-19T08:00:00Z"
  - "1.5.2 2026-11-20T18:00:00Z: pass-10 remediation (ADV-P10-B03): Verification Properties gains the VP-001 ladder row for the CP-O02 overflow degrade (EC-012) — 29-byte line, exit 0; reciprocal VP-001 bcs: sync is the architect's"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.012: Countdown format and the 1.15 gate

## Description

A reported plan window with a known reset time gets a countdown `-><time>` in the window's
colour, but only when the reset lies in the future and no more than 1.15 window lengths
ahead (a reset further out is treated as implausible data). The time is formatted with
floor divisions as `<d>d<hh>h` from one day, `<h>h<mm>m` from one hour, else `<m>m` —
so a reset under a minute away shows `->0m`.

Notation: `\e` is the byte 0x1B; `T = 1800000000.0`; `D7` = 604800.

## Preconditions

1. The window is reported (BC-1.02.010) and its colour `col` is decided (BC-1.02.011).
2. `rem = reset - now` (float) when `reset` is a number; otherwise no countdown.
3. `statusline.limits.countdown_max_factor` = 1.15.

## Postconditions

1. A countdown is appended iff `rem` is not None and `0 < rem <= length * 1.15`.
2. `cd` is computed with CPython float floor-division and modulo (`pyfmt.FloorDiv` /
   `pyfmt.Mod`, a port of `float_divmod`, never `math.Floor(a/b)`; IM-08, BC-5.01.003):
   - `rem >= 86400` → `Int(rem // 86400)` + `d` + 2-digit zero-padded
     `Int((rem % 86400) // 3600)` + `h`;
   - else `rem >= 3600` → `Int(rem // 3600)` + `h` + 2-digit zero-padded
     `Int((rem % 3600) // 60)` + `m`;
   - else → `Int(rem // 60)` + `m`.
3. Appended bytes: `" "` + `col` + `->` + `cd` + `\e[0m` (`->` is ASCII hyphen-minus and
   greater-than).

## Invariants

1. The countdown never appears for a past or present reset (also guaranteed upstream by
   BC-1.02.010).
2. Units 86400 / 3600 / 60 are time-unit constants, not configuration.
3. Rationale for 1.15 (D15, T-035): owner judgment, OD-57 E-A — "15 % slack before a reset
   time counts as bogus".
4. The `->` prefix of PC3 is ASCII hyphen-minus + greater-than — a **named format constant** of this
   widget, not config (D15 rationale: display-format constant of the output, parity-bound at two
   bytes; why not config = no ruling mints a key for this site).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `0 < rem < 60` (59, 59.999, 0.5) | `->0m` |
| EC-002 | rem 3599 / 3599.9 | `->59m` |
| EC-003 | rem 3600 / 3600.0001 | `->1h00m` |
| EC-004 | rem 86399 / 86399.99 | `->23h59m` |
| EC-005 | rem 86400 | `->1d00h` |
| EC-006 | rem = 1.15·7d = 695520 | shown `->8d01h` (`<=`) |
| EC-007 | rem = 1.16·7d | no countdown; window text still shown |
| EC-008 | 5h: rem 20700 (= 1.15·18000) / 20701 | `->5h45m` / none |
| EC-009 | `resets_at` non-numeric | no countdown (rem None) |
| EC-010 | rem NaN (`resets_at` NaN) | gate false → no countdown, absolute bands (pass-3 r1 BC-SL-061) |
| EC-011 | float dividends near unit boundaries | must match CPython `float_divmod` exactly (reason for confidence M) |
| EC-012 | `resets_at` a JSON integer at or beyond the int→float conversion threshold \|n\| ≥ 2**1024 − 2**970 **on the positive side** (oracle-verified 2026-11-17; e.g. 10³⁰⁹) | `rem = reset - now` raises OverflowError at SL:515 before any gate → guard line (stdin-borne render overflow, OD-156; same site as BC-1.02.011 EC-010; taxonomy **CP-O02**) |
| EC-013 | `resets_at` a huge **negative** JSON integer at the EC-012 magnitude, e.g. −OV = −(2**1024 − 2**970) (pass-6 ADV-P6-B02: re-vectored from the former −10³⁰⁰, which converted cleanly to float and discriminated nothing; see BC-1.02.011 EC-011) | no countdown, no degrade: SL:506 marks the window passed (exact int/float compare, no conversion), so pct = None and the window is hidden before SL:515's subtraction — for the canonical 5h-absent vector the widget is dropped by the SL:510 `any(...)` check; the SL:513-514 per-window continue applies when the other window is reported (oracle-verified 2026-11-17, BC-1.02.011 EC-011) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15; `used_percentage` 10, so the
colour is GREY `\e[90m`; segment = `\e[90m7d10%\e[0m` + countdown.

| Input (rem = resets_at − T) | Expected countdown bytes | Category |
|-------|----------------|----------|
| 15480 | ` \e[90m->4h18m\e[0m` | happy-path |
| 518400 | ` \e[90m->6d00h\e[0m` | happy-path |
| 544320 (0.9·7d) | ` \e[90m->6d07h\e[0m` | edge-case |
| 86400 | ` \e[90m->1d00h\e[0m` | edge-case |
| 86399 | ` \e[90m->23h59m\e[0m` | edge-case |
| 86399.99 | ` \e[90m->23h59m\e[0m` | edge-case |
| 3600 | ` \e[90m->1h00m\e[0m` | edge-case |
| 3599.9 | ` \e[90m->59m\e[0m` | edge-case |
| 60 | ` \e[90m->1m\e[0m` | edge-case |
| 59 | ` \e[90m->0m\e[0m` | edge-case |
| 0.5 | ` \e[90m->0m\e[0m` | edge-case |
| 695520 (1.15·7d) | ` \e[90m->8d01h\e[0m` | edge-case |
| 701568 (1.16·7d) | none (segment `\e[90m7d10%\e[0m` only) | edge-case |
| 5h window, rem 20700 / 20701 | ` \e[90m->5h45m\e[0m` / none | edge-case |
| 0 | none — window unreported (BC-1.02.010) | error |
| `resets_at` = OV (`2**1024 − 2**970` = 179769313486231580793728971405303415079934132710037826936173778980444968292764750946649017977587207096330286416692887910946555547851940402630657488671505820681908902000708383676273854845817711531764475730270069855571366959622842914819860834936475292719074168444365510704342711559699508093042880177904174497792, the smallest positive integer that fails float conversion) | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 (OverflowError at SL:515 before any gate; CP-O02, EC-012) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | `cd` equals the oracle for rem sampled densely around every unit boundary (k·60, k·3600, k·86400 ± 1e-6, ± 1 ulp) up to 1.15·7d | table test vs CPython goldens |
| VP-028 | Gate `0 < rem <= 1.15·length` matches the oracle at both ends for both windows | table test |
| VP-028, VP-001 | The CP-O02 overflow degrade (EC-012: `resets_at` at or beyond the int→float threshold, positive side) stays on the never-blank ladder — exactly the 29-byte degraded line, exit 0 | table test (fault-injection row of VP-001's ladder) |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane (SL:523-530) |
| Legacy contract | BC-SL-017 (refined in pass-3 deep r1 §A) |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-57 E-A (1.15 rationale), OD-103 (pyfmt FloorDiv/Mod), OD-156 (render-time overflow → catalogued crash path) |
| Config keys | `statusline.limits.countdown_max_factor` (1.15, operator `<=`) |
| Architecture Module | `internal/statusline/limits.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.011 — depends on (window colour)
- BC-1.02.010 — depends on (reported windows; expiry)
- BC-5.01.003 — depends on (CPython float divmod)
- BC-1.02.024 — related to (0.9·length boundary)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#limits` — internal/statusline/limits.go (countdown, 1.15 gate) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — plan-window widget story

## VP Anchors (Recommended)

- VP-028 — countdown boundary parity

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`render_lane`, SL:523-530) |
| **Confidence** | medium for translation (float divmod near unit boundaries, design §8); behavior itself HIGH-R |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `rem is not None and 0 < rem <= length * 1.15` (SL:523)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none (given `rem`) |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; the only risk is using Go integer or `math.Floor` arithmetic instead
of the `pyfmt` divmod port.
