---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/ubiquitous-language.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "f65e846"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-081"
parity_class: byte-exact
confidence: H
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

# Behavioral Contract BC-1.02.028: Window-age duration format

> Byte notation used below: `\e` = ESC (0x1B); `\n` = LF (0x0A). All other characters are literal UTF-8.

## Description

The text after `⌂` (process-age window, BC-1.02.017) is computed from `win_ms`: `wm = int(win_ms // 60000)` whole
minutes; from one day (1440 minutes) it renders `<days>d<hours, 2 digits>h` with minutes dropped, below one day it
renders `_hm(win_ms)` (`<m>m` or `<h>h<mm>m`).

## Preconditions

1. The window-age gate of BC-1.02.017 passed; `win_ms = (now - win_start) * 1000` (float64, no FMA).
2. `//` and `%` on floats follow CPython `float_divmod` (`pyfmt.FloorDiv/Mod`), on ints Python floor semantics
   (`pyfmt.FloorDivInt/ModInt`) (design IM-08).

## Postconditions

1. `wm = int(FloorDiv(win_ms, 60000))`.
2. If `wm >= 1440`: `wtxt = str(wm // 1440) + "d" + format((wm % 1440) // 60, "02d") + "h"`; minutes are not
   shown, the day count is not padded or capped.
3. Else: `wtxt = _hm(win_ms)` (BC-1.02.015): `mins = int(win_ms // 60000)`; `mins >= 60` →
   `str(mins // 60) + "h" + format(mins % 60, "02d") + "m"`, else `str(mins) + "m"`.
4. `win_ms = +inf` (only from `win_start = -Infinity`) → `int(nan)` raises ValueError at SL:560 → whole stdout is
   `\e[90mstatusline degraded\e[0m\n`.

## Invariants

1. The 1440-minute switch is a named constant (calendar unit, register T-041 NC "a day is a day"), not a config key.
2. Hours in the day form are always two digits (`00`..`23`).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | now − start = 86399 s | `23h59m` |
| EC-002 | now − start = 86400 s | `1d00h` |
| EC-003 | now − start = 7200 s | `2h00m` |
| EC-004 | 104 days | `104d04h` (no padding) |
| EC-005 | `win_start = true` at now = 1794600000 | `20770d19h` |
| EC-006 | `win_ms = +inf` | degraded |
| EC-007 | Very large finite `win_ms` (minutes beyond int64) | byte-exact big integers via `math/big` at this site (OD-137), same resolution as BC-1.02.027 EC-005; no exclusion entry |

## Canonical Test Vectors

now = 1794600000.0, `win_start = now - S`, dur 60001 unless noted; output is the full timer segment.

| Input S (s) | Expected Output | Category |
|-------|----------------|----------|
| 112000 (dur 26,700,000) | `\e[90m⏱ 7h25m\e[0m\e[90m ⌂1d07h\e[0m` | happy-path |
| 27000 (dur 26,700,000) | `\e[90m⏱ 7h25m\e[0m\e[90m ⌂7h30m\e[0m` | happy-path |
| 7200 | `\e[90m⏱ 1m\e[0m\e[90m ⌂2h00m\e[0m` | edge-case |
| 86399 | `\e[90m⏱ 1m\e[0m\e[90m ⌂23h59m\e[0m` | edge-case |
| 86400 | `\e[90m⏱ 1m\e[0m\e[90m ⌂1d00h\e[0m` | edge-case |
| 277200 | `\e[90m⏱ 1m\e[0m\e[90m ⌂3d05h\e[0m` | edge-case |
| 9000000 | `\e[90m⏱ 1m\e[0m\e[90m ⌂104d04h\e[0m` | edge-case |
| win_start = -Infinity | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error |

Pinned 2026-11-15 with the legacy `render_lane` under CPython 3.11 (oracle, OD-104); the first six match deep pass-3
round 1.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | For finite `win_ms` in [300000, 1e12] the Go text equals CPython's | fuzz vs oracle |
| VP-028 | Day form iff `wm >= 1440` | table test |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/session.go`; BC-COMPONENT-MAP: internal/statusline/session.go (window-age duration; big via OD-137) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:560-561, inside SL:554-563; `_hm` SL:545-548) |
| Legacy contract | BC-SL-081 (deep pass-3 round 1, new) |
| Config keys | none (T-041 is a named constant); glyph via `statusline.glyphs.*` |
| Parity | byte-exact (no exclusion entry; D4-EX-1 / OD-76 concern acquisition, BC-3.02.001/002) |

## Related BCs (Recommended)

- BC-1.02.017 — composes with (gate and placement)
- BC-1.02.015 — depends on (`_hm` below one day)
- BC-1.02.027 — related to (same ValueError class; big-integer gap)
- BC-5.01.003 — depends on (`FloorDiv`/`Mod`)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/session.go (window-age duration; big via OD-137) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-028 — format equality

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane, SL:560-561) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: f-string format, CPython float floor division; pinned against the oracle

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

Big-integer note resolved by OD-137: `math/big` at the two duration-format sites (here and
BC-1.02.027); see BC-1.02.027's Refactoring Notes for the IM-07 design note. No exclusion.
