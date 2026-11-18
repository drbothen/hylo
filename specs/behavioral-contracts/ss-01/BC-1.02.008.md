---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "acaa0ec"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:477-479)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-013
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.2 pass-5 remediation (ADV-P5-B03): the cache-hit glyph is named as the registry key statusline.glyphs.cache_hit (default U+267B) instead of the wildcard statusline.glyphs.*; 2026-11-18T05:42:56Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.008: Cache-hit segment

## Description

When stdin carries a numeric `prompt_cache.hit_ratio`, row 1 shows a cyan `♻` followed by
the ratio clamped to [0, 1] as a whole percentage. The figure is the client's own
per-session ratio and is shown on both lanes (local lane and cloud lane) identically.

Notation: `\e` is the byte 0x1B.

## Preconditions

1. `pc = d.prompt_cache` if truthy else `{}` (a truthy non-object degrades, EC-006).
2. `hr = pc.hit_ratio`.

## Postconditions

1. If `hr` is not a JSON number (Python `int`/`float`, booleans included) → no segment.
2. Otherwise segment = `\e[36m♻\e[0m ` + F(Min(Max(hr, 0.0), 1.0) * 100, 0) + `%`
   (one ASCII space after the reset; F = Python `'f'` formatting with zero decimals,
   half-even on the binary value, BC-5.01.001; Max/Min preserve Python NaN argument
   order, IM-09).
3. Position: after composition (BC-1.02.007), before the limits widget (BC-1.02.011).
4. The percentage text carries no colour; only the glyph is cyan.

## Invariants

1. Independent of lane, model and prefixes.
2. Output range `0%`..`100%` for finite input; NaN/inf handled by BC-1.02.023.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `hr` 1.5 / -0.2 | clamped: `100%` / `0%` |
| EC-002 | `hr` 0.005 (×100 = 0.5) | `0%` (half-even) |
| EC-003 | `hr` 0.015 / 0.025 | `2%` / `2%` (binary value of the product decides; oracle-pinned) |
| EC-004 | `hr` 0.995 | `100%` |
| EC-005 | `hr` `true` / `false` | `100%` / `0%` (bool is a number in Python) |
| EC-006 | `prompt_cache` truthy non-object (`"x"`) | AttributeError → guard line `\e[90mstatusline degraded\e[0m\n`, exit 0 |
| EC-007 | `hr` string `"0.9"`, null, missing | no segment |
| EC-008 | `hr` NaN / ±inf | BC-1.02.023 (`♻ nan%`, `100%`/`0%`) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15.

| Input (`prompt_cache`) | Expected segment | Category |
|-------|----------------|----------|
| `{"hit_ratio":0.964}` | `\e[36m♻\e[0m 96%` | happy-path |
| `{"hit_ratio":0.0}` | `\e[36m♻\e[0m 0%` | edge-case |
| `{"hit_ratio":1.0}` | `\e[36m♻\e[0m 100%` | edge-case |
| `{"hit_ratio":1.5}` | `\e[36m♻\e[0m 100%` | edge-case |
| `{"hit_ratio":-0.2}` | `\e[36m♻\e[0m 0%` | edge-case |
| `{"hit_ratio":0.005}` | `\e[36m♻\e[0m 0%` | edge-case |
| `{"hit_ratio":0.015}` | `\e[36m♻\e[0m 2%` | edge-case |
| `{"hit_ratio":0.125}` | `\e[36m♻\e[0m 12%` | edge-case |
| `{"hit_ratio":true}` | `\e[36m♻\e[0m 100%` | edge-case |
| `{"hit_ratio":"0.9"}` | no segment | edge-case |
| `prompt_cache` = `"x"` | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | For finite hr, text equals CPython `f"{min(max(hr,0.0),1.0)*100:.0f}%"` | property test vs CPython goldens (sweep 0..1 step 0.0005) |
| VP-028 | Segment absent iff hr is not a number | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane (SL:477-479) |
| Legacy contract | BC-SL-013 |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-113 (theme), OD-02 (glyph), OD-103 (pyfmt) |
| Config keys | `statusline.glyphs.cache_hit` (default ♻, U+267B), `statusline.theme.*` (cyan, reset) |
| Architecture Module | `internal/statusline/context.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.023 — composes with (NaN/inf rendering)
- BC-5.01.001 — depends on (`'f'` formatting)
- BC-5.01.003 — depends on (Max/Min NaN order)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#context` — internal/statusline/context.go (cache-hit segment) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — context widgets story

## VP Anchors (Recommended)

- VP-028 — cache-hit formatting property

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`render_lane`, SL:477-479; rationale comment SL:470-476) |
| **Confidence** | high (pass-3 HIGH-R #7) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(hr, (int, float))` (SL:478)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
