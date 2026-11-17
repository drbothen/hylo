---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "7d75fbc"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-064"
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

# Behavioral Contract BC-1.02.027: _hm ValueError on inf degrades (CP-S12/S13)

> Byte notation used below: `\e` = ESC (0x1B); `\n` = LF (0x0A). All other characters are literal UTF-8.

## Description

`_hm(ms)` computes `mins = int(ms // 60000)`. For `ms = +Infinity`, CPython's float floor division gives
`inf // 60000 = nan`, and `int(nan)` raises ValueError, which nothing catches. A `+Infinity` session duration
(CP-S12) or a `+Infinity` API duration inside a shown timer (CP-S13) therefore crashes the render into the 29-byte
degraded line. NaN and `-Infinity` durations never reach `_hm` (they fail the `> 60000` / `>= 60000` gates).

## Preconditions

1. `dur = cost.total_duration_ms`, `api = cost.total_api_duration_ms` from stdin.
2. Go implementation: `pyfmt.FloorDiv` is a port of CPython `float_divmod` (returns NaN for an infinite dividend) and
   `pyfmt.Int` returns typed `ErrValue` for NaN (design IM-07, IM-08).

## Postconditions

1. `dur = +Infinity` → timer gate `inf > 60000` passes → `_hm(inf)` fails → whole stdout is
   `\e[90mstatusline degraded\e[0m\n`, exit 0 (CP-S12).
2. `dur` finite `> 60000` and `api = +Infinity` → API gate passes → `_hm(inf)` fails → degraded line (CP-S13).
3. `dur` NaN or `-Infinity` → timer hidden, no crash; `api` NaN or `-Infinity` → no API suffix, no crash.
4. Earlier side effects persist (BC-1.01.009); the later cost-history record (SL:606) does not run.

## Invariants

1. At this site `ErrValue` is not caught: it maps to `errDegraded` (design IM-15).
2. Large finite durations do not crash: `_hm` returns the exact Python integer arithmetic result (see EC-005).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `dur = Infinity` | degraded (CP-S12) |
| EC-002 | `dur = 120000`, `api = Infinity` | degraded (CP-S13) |
| EC-003 | `dur` = NaN | timer hidden |
| EC-004 | `api = -Infinity` | no suffix |
| EC-005 | Finite `dur` above about 5.53e23 ms (minutes beyond int64) | legacy renders exact big-integer hours (for `1e24`: `⏱ 277777777777777766h24m`); resolved by OD-137: byte-exact via `math/big` at this duration-format site — no wrap, no degrade, no exclusion entry |
| EC-006 | Window-age `win_ms = +inf` (win_start `-Infinity`) | raises the same ValueError at SL:560 (not via `_hm`); owned by BC-1.02.028 |

## Canonical Test Vectors

stdin `{"cost": {...}}`.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `total_duration_ms: 7500000` | timer segment `\e[90m⏱ 2h05m\e[0m` | happy-path |
| `total_duration_ms: 5e23` | timer segment `\e[90m⏱ 138888888888888883h12m\e[0m` | edge-case (fits int64 minutes) |
| `total_duration_ms: 1e24` | timer segment `\e[90m⏱ 277777777777777766h24m\e[0m` | edge-case (exceeds int64 minutes) |
| `total_duration_ms: NaN` | no timer segment | edge-case |
| `total_duration_ms: -Infinity` | no timer segment | edge-case |
| `total_duration_ms: 120000, total_api_duration_ms: -Infinity` | timer segment `\e[90m⏱ 2m\e[0m` | edge-case |
| `total_duration_ms: Infinity` | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error (CP-S12) |
| `total_duration_ms: 120000, total_api_duration_ms: Infinity` | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error (CP-S13) |

Pinned 2026-11-15 with the legacy `render_lane` under CPython 3.11 (oracle, OD-104).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028, VP-001 | `+Infinity` in `dur`, or in `api` with a shown timer, degrades; NaN/`-Infinity` never degrade | table test |
| VP-028, VP-001 | `_hm` output equals CPython for finite float64 inputs across the full range | fuzz vs oracle |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/session.go`; BC-COMPONENT-MAP: internal/statusline/session.go (CP-S12/S13 degrade) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane `_hm` (SL:545-548; crash at SL:546 via SL:549 for CP-S12 and SL:553 for CP-S13), timer block SL:534-563 |
| Legacy contract | BC-SL-064 (deep pass-3 round 1, new; crash paths CP-S12, CP-S13) |
| Config keys | `statusline.timer.{min_ms, api_min_ms}` (T-038, T-039) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.015 — refines (timer and `_hm`)
- BC-1.02.016 — related to (API suffix, CP-S13)
- BC-1.02.028 — related to (same ValueError class at SL:560)
- BC-1.01.001 — depends on (degraded line)
- BC-5.01.003 — depends on (`FloorDiv`, typed `Int` errors)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/session.go (CP-S12/S13 degrade) (degraded ladder) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-028, VP-001 — `+Infinity` degrades

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane `_hm`, SL:545-548) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: CPython `float.__floordiv__(inf, 60000)` returns NaN; `int(nan)` raises ValueError

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

Resolved by OD-137: the two duration-format sites (`_hm` here and the window-age form,
BC-1.02.028) keep byte-exact arbitrary-precision behavior using `math/big`. Design note on
IM-07: `pyfmt.Int(x float64) (int64, error)` remains the typed fast path; the duration sites
use the big-integer path when the minute count exceeds int64 (Python's `int()` of a finite
float is unbounded). No exclusion entry exists for this gap.
