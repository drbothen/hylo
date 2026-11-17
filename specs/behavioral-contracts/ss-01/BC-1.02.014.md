---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "aac2048"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_fmt_lines (SL:849-860), render_lane (SL:534-537)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-019
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

# Behavioral Contract BC-1.02.014: Lines segment formats via _fmt_lines

## Description

When the session has added or removed lines, row 1 shows `▲<added>/▼<removed>` (green up,
dim slash, red down). Each count is formatted by `_fmt_lines`: Python `int()` of the value
(truncating floats, parsing numeric strings), exact below 10,000, whole thousands with `k`
below 1,000,000, then millions with one decimal and `M`; a value `int()` rejects renders
`?`.

Notation: `\e` is the byte 0x1B.

## Preconditions

1. `cost = d.cost` if truthy else `{}` (a truthy non-object degrades, EC-010).
2. `la = cost.total_lines_added` if truthy else `0`; `lr = cost.total_lines_removed` if
   truthy else `0`.
3. `statusline.units.lines` thresholds: 10,000 (`>=` → k) and 1,000,000 (`>=` → M).

## Postconditions

1. If neither `la` nor `lr` is truthy → no segment.
2. Otherwise segment = `\e[32m▲` + fmt(la) + `\e[0m\e[2m/\e[0m\e[31m▼` + fmt(lr) + `\e[0m`.
3. `fmt(n)`:
   1. `n = int(n)` with Python semantics (`pyfmt.ParseInt` for strings — surrounding
      whitespace and `_` digit separators accepted, BC-5.01.002; floats truncate toward
      zero; `true` → 1); a TypeError or ValueError (non-numeric string such as `"1e3"`,
      list, object, NaN) → return `?`.
   2. `n >= 1000000` → F(n / 1e6, 1) + `M` (Python `'f'`, half-even on the binary value).
   3. `n >= 10000` → `n // 1000` + `k` (integer floor division).
   4. else → decimal `n` (negative values exact, e.g. `-20000`).
4. Position: after the limits segment, before the timer segment.

## Invariants

1. Both counts are always shown together once either is non-zero (`▲0` or `▼0` possible).
2. Rationale (D15, T-037, documented): keep row 1 narrow on big refactors (review #8.1).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | 0/0, null/null, missing | no segment |
| EC-002 | 9999 / 10000 | `9999` / `10k` |
| EC-003 | 999999 / 1000000 | `999k` / `1.0M` |
| EC-004 | 1,250,000 / 1,350,000 | `1.2M` / `1.4M` (half-even on exact ties) |
| EC-005 | 12345.9 / 2.9 | `12k` / `2` (truncation) |
| EC-006 | strings `"12"`, `" 42 "`, `"  -3\n"`, `"1_000"` | `12`, `42`, `-3`, `1000` |
| EC-007 | `"1e3"`, `"abc"`, `[1]`, NaN | `?` (NaN is truthy, so `▲?/▼0` shows) |
| EC-008 | `true` | `1` |
| EC-009 | negative below threshold, e.g. -20000 | `-20000` (thresholds are `>=` on signed value) |
| EC-010 | `cost` truthy non-object | AttributeError → guard line `\e[90mstatusline degraded\e[0m\n`, exit 0 |
| EC-011 | ±Infinity | OverflowError not caught → guard line (BC-1.02.026, CP-S11) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15.

| Input (`cost` added, removed) | Expected segment | Category |
|-------|----------------|----------|
| 12, 3 | `\e[32m▲12\e[0m\e[2m/\e[0m\e[31m▼3\e[0m` | happy-path |
| 12345, 0 | `\e[32m▲12k\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | happy-path |
| 0, 7 | `\e[32m▲0\e[0m\e[2m/\e[0m\e[31m▼7\e[0m` | edge-case |
| 1050000, 250 | `\e[32m▲1.1M\e[0m\e[2m/\e[0m\e[31m▼250\e[0m` | edge-case |
| 9999, 10000 | `\e[32m▲9999\e[0m\e[2m/\e[0m\e[31m▼10k\e[0m` | edge-case |
| 999999, 1000000 | `\e[32m▲999k\e[0m\e[2m/\e[0m\e[31m▼1.0M\e[0m` | edge-case |
| 1250000, 1350000 | `\e[32m▲1.2M\e[0m\e[2m/\e[0m\e[31m▼1.4M\e[0m` | edge-case |
| `"12"`, `" 42 "` | `\e[32m▲12\e[0m\e[2m/\e[0m\e[31m▼42\e[0m` | edge-case |
| 12345.9, 0 | `\e[32m▲12k\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | edge-case |
| -20000, 0 | `\e[32m▲-20000\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | edge-case |
| `true`, 0 | `\e[32m▲1\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | edge-case |
| 0, 0 | no segment | edge-case |
| `"1e3"`, 1 | `\e[32m▲?\e[0m\e[2m/\e[0m\e[31m▼1\e[0m` | error |
| NaN, 0 | `\e[32m▲?\e[0m\e[2m/\e[0m\e[31m▼0\e[0m` | error |

`_fmt_lines` direct: `10000000` → `10.0M`; `"1_000"` → `1000`; `"  -3\n"` → `-3`;
`999950` → `999k` (verified).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | fmt equals CPython `_fmt_lines` for ints in [-1e7, 1e8] sampled around thresholds and ties | property test vs CPython goldens |
| VP-028 | fmt of strings equals CPython for the BC-5.01.002 grammar corpus | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:_fmt_lines (SL:849-860); segment in render_lane SL:534-537 |
| Legacy contract | BC-SL-019 (refined with BC-SL-063 in pass-3 deep r1) |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-103 (pyfmt ParseInt/Int/F), OD-113 (theme), OD-02 (glyphs) |
| Config keys | `statusline.units.lines`, `statusline.glyphs.*` (▲ ▼), `statusline.theme.*` |
| Architecture Module | `internal/statusline/session.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.026 — composes with (±inf degrade)
- BC-5.01.002 — depends on (Python int grammar)
- BC-5.01.001 — depends on (`'f'` formatting)
- BC-1.02.015 — composes with (next segment)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#session` — internal/statusline/session.go (_fmt_lines) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — session widgets story

## VP Anchors (Recommended)

- VP-028 — `_fmt_lines` parity property

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_fmt_lines` SL:849-860; `render_lane` SL:534-537) |
| **Confidence** | high (pass-3 HIGH-R #8, 6 cases; r1 table) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `except (TypeError, ValueError): return "?"` (SL:854-855); `if la or lr` (SL:536)
- **documentation**: docstring SL:850-851

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; the typed `pyfmt` errors (`ErrValue` vs `ErrOverflow`) let the Go
code reproduce Python's catch list exactly (IM-07).
