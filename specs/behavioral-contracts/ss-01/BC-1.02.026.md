---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "6005118"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-063"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.1 pass-3 remediation (ADV-P3-B11): degraded-line SGR constant credited to OD-113 (BC-2.02.001 inv 2), not OD-162; 2026-11-18T02:00:00Z"
  - "1.1.2 pass-7 remediation (ADV-P7-B12): history labels version-prefixed; no behavioral change; 2026-11-19T07:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.026: _fmt_lines OverflowError on inf degrades (CP-S11)

> Byte notation used below: `\e` = ESC (0x1B); `\n` = LF (0x0A). All other characters are literal UTF-8.

## Description

`_fmt_lines(n)` starts with `int(n)` and catches only TypeError and ValueError (returning `?`). For `±Infinity`
Python raises OverflowError, which is **not** caught, so a lines total of `Infinity` or `-Infinity` (JSON
`Infinity`, `-Infinity`, or an overflowing literal such as `1e400`) crashes the render into the 29-byte degraded
line (crash path CP-S11). NaN raises ValueError and is caught, so it prints `?`.

## Preconditions

1. `la = cost.total_lines_added or 0`, `lr = cost.total_lines_removed or 0`, and `la or lr` is truthy, so the lines
   segment is being built (BC-1.02.014).
2. Go implementation uses `pyfmt.Int(x float64) (Num, error)` (ARCH-06, BC-5.01.003) with
   typed errors `ErrValue` (NaN) and `ErrOverflow` (±Inf); `Num` is exact beyond int64
   (oracle: legacy `_fmt_lines(1e300)` renders the long `…M` string, SL:853, 857 — an
   int64 Int would overflow and degrade instead), so this site degrades only where
   Postconditions 1/3 say it does (design IM-07).

## Postconditions

1. If either `la` or `lr` is `+Infinity` or `-Infinity`, the refresh stops at this site with `errDegraded` and the
   entire stdout is exactly `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 (BC-1.01.001).
2. Side effects of earlier steps persist (transcript mix cache, `effective_rl` session-cache write, metrics sample
   cache, window-start `proc_start` write, git-cache write; BC-1.01.009); the later cost-history record (SL:606) does
   not run.
3. NaN in either field renders `?` for that side; the segment and the refresh continue.

## Invariants

1. The catch list is reproduced per site: at this site `ErrValue` and type errors map to `?`, `ErrOverflow` maps to
   `errDegraded` (design IM-15).
2. Values are evaluated left (`la`) to right (`lr`); either side alone triggers the crash.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `total_lines_added = Infinity` | degraded |
| EC-002 | `total_lines_removed = -Infinity`, added 0 | degraded |
| EC-003 | `total_lines_added = 1e400` (decodes to `+inf`) | degraded |
| EC-004 | `total_lines_removed` = NaN, added 5 | `▲5/▼?` |
| EC-005 | `total_lines_added` = NaN, removed 0 | `▲?/▼0` (NaN is truthy, so the segment is built) |
| EC-006 | both 0 / absent | no segment (BC-1.02.014) |

## Canonical Test Vectors

stdin `{"cost": {"total_lines_added": A, "total_lines_removed": R}}`.

| Input (A, R) | Expected Output | Category |
|-------|----------------|----------|
| 20000, 3 | lines segment `\e[32m▲20k\e[0m\e[2m/\e[0m\e[31m▼3\e[0m` | happy-path |
| 5, NaN | lines segment `\e[32m▲5\e[0m\e[2m/\e[0m\e[31m▼?\e[0m` | edge-case |
| NaN, 0 | lines segment `\e[32m▲?\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | edge-case |
| Infinity, 0 | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error |
| 0, -Infinity | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error |
| 1e400, 0 | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error |

Pinned 2026-11-15 with the legacy `render_lane` / `_fmt_lines` under CPython 3.11 (oracle, OD-104): `int(inf)` and
`int(-inf)` raise OverflowError, `int(nan)` raises ValueError. The `1e400` row follows from Python `json` decoding
`1e400` to `inf` (deep pass-3 round 1, CP-S11).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028, VP-001 | ±Inf in either lines field degrades; NaN never degrades | table test |
| VP-028, VP-001 | Degraded case keeps earlier cache writes | multi-step harness test (BC-1.01.009) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/session.go`; BC-COMPONENT-MAP: internal/statusline/session.go (CP-S11 degrade) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:_fmt_lines (SL:849-860; crash at SL:853) called from legacy/dgx_statusline.py:render_lane (SL:534-537) |
| Legacy contract | BC-SL-063 (deep pass-3 round 1, new; crash path CP-S11) |
| Config keys | — (none: the degraded line's grey/reset is a built-in named constant, independent of `statusline.theme.*`, OD-113; cf. BC-1.01.001 Inv 4) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.014 — refines (lines segment and `_fmt_lines`)
- BC-1.01.001 — depends on (degraded line)
- BC-1.01.009 — related to (earlier writes kept)
- BC-5.01.003 — depends on (`pyfmt.Int` typed errors)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/session.go (CP-S11 degrade) (degraded ladder) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-028, VP-001 — ±Inf degrades, NaN does not

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (_fmt_lines, SL:849-860) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `except (TypeError, ValueError)` (SL:854), which omits OverflowError
- **inferred**: CPython `int(float)` raises OverflowError on infinities

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
