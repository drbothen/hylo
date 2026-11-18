---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "1580f27"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane._hm (SL:539-549, 563)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-020
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["1.2 pass-6 remediation (ADV-P6-B01 call 10 + B08): the segment-presence for-all row re-anchored from VP-028 to VP-041 (VP-028 keeps the golden leg); the timer glyph is named as the registry key statusline.glyphs.timer instead of the wildcard statusline.glyphs.* (Config keys row); 2026-11-19T04:00:00Z"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.015: Timer segment formats via _hm

## Description

Once the session's wall-clock duration (stdin `cost.total_duration_ms`) exceeds one
minute, row 1 shows a grey `⏱ <elapsed>` segment. `_hm` formats milliseconds as whole
minutes (`<m>m`) below an hour and as `<h>h<mm>m` from an hour on, with unbounded hours
(`25h00m`). The API-time suffix and the process-age window suffix (`⌂`) are appended inside
the same segment by separate contracts.

Notation: `\e` is the byte 0x1B.

## Preconditions

1. `cost = d.cost` if truthy else `{}` (a truthy non-object degrades before this point,
   BC-1.02.014 EC-010).
2. `dur = cost.total_duration_ms`.
3. `statusline.timer.min_ms` = 60000 (operator `>`).

## Postconditions

1. The segment exists iff `dur` is a number (Python `int`/`float`, booleans included) and
   `dur > 60000`.
2. `_hm(ms)`: `mins = Int(ms // 60000)` (CPython float floor division for floats,
   `pyfmt.FloorDiv`, IM-08; integer floor division for ints); if `mins >= 60` →
   decimal `mins // 60` + `h` + 2-digit zero-padded `mins % 60` + `m`; else decimal
   `mins` + `m`.
3. Base segment bytes: `\e[90m⏱ ` + `_hm(dur)` + `\e[0m`; then, in order, the optional
   API-time suffix (BC-1.02.016) and window-age suffix (BC-1.02.017, BC-1.02.028) are
   appended to the same row-1 element.
4. Position: after the lines segment (BC-1.02.014), before the token segment
   (BC-1.02.018).

## Invariants

1. Minute granularity; hours are not capped and never roll into days in this segment.
2. `% 60` (not `% 100`) for the minutes part (review 2026-11-13 #9.1).
3. Rationale (D15, T-038, derived): `_hm` has minute granularity, so a timer below one
   minute would only ever read `0m`/`1m` noise; the code comment "show timer after 1
   minute" (SL:540).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | dur exactly 60000 | no segment (`>`) |
| EC-002 | dur 60000.5 / 60001 / 119999 | `1m` |
| EC-003 | dur 3,599,999 / 3,600,000 | `59m` / `1h00m` |
| EC-004 | dur 90,000,000 | `25h00m` |
| EC-005 | float dur 26,700,000.0 | `7h25m` |
| EC-006 | dur string `"90000"`, null, missing, 0 | no segment |
| EC-007 | dur `true` (= 1) | no segment |
| EC-008 | dur NaN | no segment (`NaN > 60000` is false) |
| EC-009 | dur +inf | `inf // 60000` = NaN → `int()` ValueError → guard line (BC-1.02.027, CP-S12) |
| EC-010 | `nextafter(120000, 0)` | `1m` (float floor division, pass-3 r1 vector) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15 (no API time, no window
start, so only the base segment appears).

| Input (`cost.total_duration_ms`) | Expected segment | Category |
|-------|----------------|----------|
| 4500000 | `\e[90m⏱ 1h15m\e[0m` | happy-path |
| 120000 | `\e[90m⏱ 2m\e[0m` | happy-path |
| 60000 | no segment | edge-case |
| 60001 | `\e[90m⏱ 1m\e[0m` | edge-case |
| 60000.5 | `\e[90m⏱ 1m\e[0m` | edge-case |
| 119999 | `\e[90m⏱ 1m\e[0m` | edge-case |
| 3599999 | `\e[90m⏱ 59m\e[0m` | edge-case |
| 3600000 | `\e[90m⏱ 1h00m\e[0m` | edge-case |
| 7500000 | `\e[90m⏱ 2h05m\e[0m` | edge-case |
| 90000000 | `\e[90m⏱ 25h00m\e[0m` | edge-case |
| 26700000.0 | `\e[90m⏱ 7h25m\e[0m` | edge-case |
| `"90000"` / `true` / NaN | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | `_hm` equals CPython for ints and floats sampled at every k·60000 ± {0, 1, 0.5, 1 ulp} up to 1e8 | table test vs CPython goldens — golden leg |
| VP-041 | Segment present iff number and `> 60000` — for all renders | property test (for-all leg; VP-028 delivers the oracle legs) |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane._hm (SL:539-549 gate, `_hm` SL:545-548, base segment SL:549, append SL:563) |
| Legacy contract | BC-SL-020 (refined with BC-SL-064 in pass-3 deep r1) |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-57 E-0 (derived rationales accepted, T-038), OD-103 (pyfmt FloorDiv/Int), OD-113 (theme), OD-02 (glyph ⏱) |
| Config keys | `statusline.timer.min_ms` (60000), `statusline.glyphs.timer` (⏱), `statusline.theme.*` |
| Architecture Module | `internal/statusline/session.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.016 — composes with (API-time suffix)
- BC-1.02.017 / BC-1.02.028 — composes with (process-age window suffix)
- BC-1.02.027 — composes with (+inf degrade)
- BC-5.01.003 — depends on (float floor division, Int)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#session` — internal/statusline/session.go (_hm) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — session widgets story

## VP Anchors (Recommended)

- VP-041 — segment-presence for-all property (VP-028 retains the `_hm` golden leg)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`render_lane`, SL:539-549, 563) |
| **Confidence** | high (pass-3 HIGH-R #9, 12 cases) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(dur, (int, float)) and dur > 60000` (SL:540)
- **documentation**: comments SL:541-544, SL:547

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | pure |

#### Refactoring Notes

Lift `_hm` from a nested function to a package-level helper shared with BC-1.02.016 and
BC-1.02.028.
