---
document_type: behavioral-contract
level: L3
version: "1.3"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "4f5dcbc"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-060"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "pass-4 remediation (ADV-P4-B03): float64-table and never-degrade for-all legs re-anchored to VP-041; 2026-11-17T12:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.023: Cache-hit NaN/inf rendering

> Byte notation used below: `\e` = ESC (0x1B). All other characters are literal UTF-8.

## Description

The cache-hit segment (BC-1.02.008) renders `prompt_cache.hit_ratio` as a clamped whole percentage. Non-finite
and boolean ratios do not crash: NaN survives the clamp (argument order) and prints `nan%`, `+Infinity` and `true`
print `100%`, `-Infinity` and `false` print `0%`, and `-0.0` prints `-0%`.

## Preconditions

1. `hr = (prompt_cache or {}).hit_ratio` is an int or float (bool counts as int). Non-numeric values (strings,
   `null`, lists) omit the segment entirely.
2. Default theme (OD-113): CYAN `\e[36m`, RESET `\e[0m`.

## Postconditions

1. The segment is `\e[36m♻\e[0m ` + `F(Min(Max(hr, 0.0), 1.0) * 100, 0)` + `%`, where `Max`/`Min` keep the source
   argument order (design IM-09: `Max(a, b)` returns `b` only if `b > a`) and `F` is Python `format(x, ".0f")`
   (half-even; `nan`, `inf`, `-0` spellings, BC-5.01.001).
2. Resulting texts: NaN → `nan%`; `+Infinity` → `100%`; `-Infinity` → `0%`; `true` → `100%`; `false` → `0%`;
   `-0.0` → `-0%`; `1.5` → `100%`; `-0.2` → `0%`.

## Invariants

1. The segment never degrades the render, for any numeric `hr`.
2. Go never uses the builtin `max`/`min` or `math.Max`/`math.Min` here (they propagate or reorder NaN differently).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `hr` = NaN | `♻ nan%` (no crash) |
| EC-002 | `hr = +Infinity` | `100%` |
| EC-003 | `hr = -Infinity` | `0%` |
| EC-004 | `hr = true` / `false` | `100%` / `0%` |
| EC-005 | `hr = -0.0` | `-0%` (`Max(-0.0, 0.0)` keeps `-0.0`) |
| EC-006 | `hr = 0.995` | `100%` (99.5 rounds half-even to 100) |
| EC-007 | `hr = 0.005` | `0%` (0.5 rounds half-even to 0) |
| EC-008 | `hr = "0.5"` or `null` | segment absent |

## Canonical Test Vectors

stdin `{"prompt_cache": {"hit_ratio": X}}`; output is the exact cache-hit segment.

| Input X | Expected Output | Category |
|-------|----------------|----------|
| `0.5` | `\e[36m♻\e[0m 50%` | happy-path |
| `0.135` | `\e[36m♻\e[0m 14%` | happy-path |
| `NaN` | `\e[36m♻\e[0m nan%` | edge-case |
| `Infinity` | `\e[36m♻\e[0m 100%` | edge-case |
| `-Infinity` | `\e[36m♻\e[0m 0%` | edge-case |
| `true` | `\e[36m♻\e[0m 100%` | edge-case |
| `-0.0` | `\e[36m♻\e[0m -0%` | edge-case |
| `0.995` | `\e[36m♻\e[0m 100%` | edge-case |
| `0.005` | `\e[36m♻\e[0m 0%` | edge-case |
| `"0.5"` | segment absent (no error) | error (wrong type, tolerated) |

Pinned 2026-11-15 with the legacy `render_lane` under CPython 3.11 (oracle, OD-104). The `-0.0` vector is a new pin
from this run (not listed in the legacy pass-3 rows).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-041 | For all float64 `hr` (including NaN, ±Inf, ±0) the Go segment equals the oracle's | generated table vs oracle (VP-028 retains the bounded golden vector table above) |
| VP-041 | No numeric `hr` degrades | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/context.go`; BC-COMPONENT-MAP: internal/statusline/context.go (cache-hit NaN/inf) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:477-479) |
| Legacy contract | BC-SL-060 (deep pass-3 round 1, new) |
| Config keys | `statusline.glyphs.*` (`♻`), `statusline.theme.*` (OD-113) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.008 — refines (cache-hit segment)
- BC-5.01.001 — depends on (`F` spellings)
- BC-5.01.003 — depends on (`Max`/`Min` NaN argument order)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/context.go (cache-hit NaN/inf) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-041 — float64 table equality (for-all/differential) and the never-degrade property; VP-028 — the pinned golden vector table above

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane, SL:477-479) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(hr, (int, float))` (SL:478)
- **inferred**: Python `max`/`min` NaN behaviour, pinned against the oracle

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
