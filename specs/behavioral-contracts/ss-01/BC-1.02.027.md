---
document_type: behavioral-contract
level: L3
version: "1.6"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "8885139"
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
modified:
  - "1.3 pass-3 remediation (ADV-P3-B04): Refactoring Notes aligned with the superseding definition — pyfmt.Int(x float64) (Num, error), exact beyond int64 (BC-1.02.026 PC2, ARCH-06); 2026-11-18T02:00:00Z"
  - "1.4 pass-4 remediation (ADV-P4-B05/B03): EC-006 and its vector row tagged OD-160 (hand-edited-cache shape); _hm fuzz leg re-anchored to VP-041; 2026-11-18T03:00:00Z"
  - "1.4.1 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-18/SC-20) — the ARCH-06 line pointer replaced with the stable #pyfmt-num fragment anchor; pass-4 stamp re-dated ascending (it predated pass-3's); no behavioral change"
  - "1.5 pass-6 remediation (ADV-P6-B09): the stale line-pointer cross-reference into error-taxonomy.md (the 'superseded int64 sketch') removed; the supersession now cites the taxonomy's own stale-in-both-directions declaration; 2026-11-19T04:00:00Z"
  - "1.6 2026-11-20T18:00:00Z: pass-10 remediation (ADV-P10-B07): Architecture Anchors bullet gains the file-family fragment anchor (sibling convention of BC-1.02.001..015); the Stories placeholder respelled from S-N.MM to the TBD convention; no behavioral change"
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
| EC-006 | Window-age `win_ms = +inf` (win_start `-Infinity`; hand-edited-cache shape, **OD-160**) | raises the same ValueError at SL:560 (not via `_hm`); owned by BC-1.02.028 |

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
| `total_duration_ms: 120000`, win_start = `-Infinity` (hand-edited-cache shape, **OD-160**) | whole stdout = `\e[90mstatusline degraded\e[0m\n` (ValueError at SL:560; owned by BC-1.02.028, EC-006) | error |
| `total_duration_ms: 120000, total_api_duration_ms: Infinity` | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error (CP-S13) |

Pinned 2026-11-15 with the legacy `render_lane` under CPython 3.11 (oracle, OD-104).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028, VP-001 | `+Infinity` in `dur`, or in `api` with a shown timer, degrades; NaN/`-Infinity` never degrade | table test |
| VP-041 | `_hm` output equals CPython for finite float64 inputs across the full range | fuzz vs oracle (VP-028 retains the bounded golden tables) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Architecture Module | `internal/statusline` (design §8 home `sl/session.go`; BC-COMPONENT-MAP: internal/statusline/session.go (CP-S12/S13 degrade) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane `_hm` (SL:545-548; crash at SL:546 via SL:549 for CP-S12 and SL:553 for CP-S13), timer block SL:534-563 |
| Legacy contract | BC-SL-064 (deep pass-3 round 1, new; crash paths CP-S12, CP-S13) |
| Config keys | `statusline.timer.{min_ms, api_min_ms}` (T-038, T-039) |
| Parity | byte-exact for Go-authored caches; the hand-edited-cache vector (win_start = -Infinity, owned by BC-1.02.028 EC-006) rides the **OD-160** exclusion entry, cited per DI-012 |

## Related BCs (Recommended)

- BC-1.02.015 — refines (timer and `_hm`)
- BC-1.02.016 — related to (API suffix, CP-S13)
- BC-1.02.028 — related to (same ValueError class at SL:560)
- BC-1.01.001 — depends on (degraded line)
- BC-5.01.003 — depends on (`FloorDiv`, typed `Int` errors)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#session` — internal/statusline/session.go (CP-S12/S13 degrade) (degraded ladder) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-028, VP-001 — `+Infinity` degrades; VP-041 — `_hm` fuzz equality

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
IM-07 (superseding definition per architecture/ARCH-06-pyfmt.md#pyfmt-num, BC-5.01.003 PC-3
and BC-1.02.026 PC2; the former "superseded int64 sketch" line reference into
error-taxonomy.md was retired pass-6 ADV-P6-B09 — the sketch is gone and the taxonomy's
own register declares the cross-reference stale in both directions, see its Surface-1
exception row): `pyfmt.Int(x float64) (Num, error)` is
the typed path and is exact beyond int64 (`Num`); the duration sites call `Int` directly and
reach for `math/big` only where Python's unbounded `int()` arithmetic demands it (exact
integer floor division of huge float minutes). No exclusion entry exists for this gap.
