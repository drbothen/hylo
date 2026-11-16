---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, ../semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, ../semport/hylo-legacy/statusline-target-design.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:mix_labels (SL:1157-1174), mix_segment (SL:1177-1183)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-012
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

# Behavioral Contract BC-1.02.007: Composition percentage rounds half-even

## Description

The context-composition segment shows, for the three byte buckets of the transcript's
context content (resident `▤` cyan, conversation `❙` green, thinking `◈` magenta), each
non-zero bucket's share as a whole percentage computed with Python `round()` — banker's
rounding (half-to-even) — right-aligned to two digits, or ` <1%` when a present bucket
rounds to 0. Zero buckets are omitted; the percentages may sum to 99, 100 or 101.

Notation: `\e` is the byte 0x1B.

## Preconditions

1. `mix` = the transcript composition tuple from the mix cache (contract family S1.03,
   e.g. BC-1.03.002); only its first three elements `(res, conv, think)` participate.
2. The segment is attempted only when `mix` is truthy (SL:466).

## Postconditions

1. If `sum(mix[:3]) <= 0` → no segment.
2. `total = sum(mix[:3])`. For each bucket in the order (`\e[36m`, `▤`, res),
   (`\e[32m`, `❙`, conv), (`\e[35m`, `◈`, think) with `n > 0`:
   `pct = pyfmt.Round(n / total * 100)` (ties to even; IM-06, BC-5.01.001);
   body = `pct` right-aligned in width 2 followed by `%` (Python `f"{pct:>2d}%"`) when
   `pct > 0`, else ` <1%`; bit = colour + glyph + body + `\e[0m`.
3. Segment = bits joined by a single space; no segment if no bit.
4. Position: after the thermometer (BC-1.02.006), before cache hit (BC-1.02.008).

## Invariants

1. Elements 4..n of `mix` (token totals, last-turn data) never affect this segment
   (SL:1158-1163: summing mixed units diluted the percentages).
2. Bucket order and glyph/colour mapping are fixed (glyphs from `statusline.glyphs.*`,
   colours from `statusline.theme.*`; defaults SL:1167).
3. Rounding is half-even, never half-up: 12.5 → 12, 62.5 → 62.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `(1,1,1)` | `33%` ×3 (sum 99) |
| EC-002 | `(125,250,625)` | `12%`, `25%`, `62%` (ties to even) |
| EC-003 | present bucket < 0.5 % | ` <1%` (e.g. `(1,199,0)` → `▤ <1%`) |
| EC-004 | single-digit percentage | space-padded: `▤ 1%`, `◈ 2%` |
| EC-005 | 100 % | three digits, no padding: `❙100%` |
| EC-006 | `(0,0,0)` or mix empty/None | no segment |
| EC-007 | negative bucket `(-1,3,0)` (sum 2 > 0) | negative bucket skipped (`n > 0`), others divided by the net total: `\e[32m❙150%\e[0m` |
| EC-008 | float buckets `(0.5,0.5,0)` | `▤50% ❙50%` |
| EC-009 | 5-tuple `(30,50,20,999,999)` | only first three used: `▤30% ❙50% ◈20%` |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15 (`mix_segment`).

| Input (mix) | Expected segment | Category |
|-------|----------------|----------|
| `(1,1,0)` | `\e[36m▤50%\e[0m \e[32m❙50%\e[0m` | happy-path |
| `(30,68,2)` | `\e[36m▤30%\e[0m \e[32m❙68%\e[0m \e[35m◈ 2%\e[0m` | happy-path |
| `(1,1,1)` | `\e[36m▤33%\e[0m \e[32m❙33%\e[0m \e[35m◈33%\e[0m` | edge-case |
| `(125,250,625)` | `\e[36m▤12%\e[0m \e[32m❙25%\e[0m \e[35m◈62%\e[0m` | edge-case |
| `(1,199,0)` | `\e[36m▤ <1%\e[0m \e[32m❙100%\e[0m` | edge-case |
| `(5,1990,5)` | `\e[36m▤ <1%\e[0m \e[32m❙100%\e[0m \e[35m◈ <1%\e[0m` | edge-case |
| `(7,0,993)` | `\e[36m▤ 1%\e[0m \e[35m◈99%\e[0m` | edge-case |
| `(30,50,20,999,999)` | `\e[36m▤30%\e[0m \e[32m❙50%\e[0m \e[35m◈20%\e[0m` | edge-case |
| `(0,0,0)` | no segment | edge-case |
| `(-1,3,0)` | `\e[32m❙150%\e[0m` | error (malformed counts, rendered not rejected) |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | For all non-negative int triples with positive sum, each pct equals CPython `round(n/total*100)` | property test against `pyfmt.Round` + CPython goldens |
| VP-TBD | Bytes equal the oracle on the pass-3 r1 vector table | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:mix_labels (SL:1157-1174; rounding SL:1171) and mix_segment (SL:1177-1183); call site render_lane SL:466-468 |
| Legacy contract | BC-SL-012 |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-103 (pyfmt Round), OD-113 (theme), OD-02 (glyph keys) |
| Config keys | `statusline.glyphs.*` (▤ ❙ ◈), `statusline.theme.*` (cyan, green, magenta, reset) |
| Architecture Module | `internal/statusline/context.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.03.002 — depends on (mix cache supplies the counts)
- BC-5.01.001 — depends on (half-even Round)
- BC-1.02.006 — composes with (preceding segment)

## Architecture Anchors (Recommended)

- `architecture/SS-01-statusline.md#context` — TBD by architect

## Story Anchor (Recommended)

TBD — context widgets story

## VP Anchors (Recommended)

- VP-TBD — half-even percentage property

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`mix_labels` SL:1157-1174, `mix_segment` SL:1177-1183) |
| **Confidence** | high (pass-3 HIGH-R #6) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `sum(counts) <= 0` (SL:1164, 1181), `n > 0` (SL:1170)
- **documentation**: docstring SL:1158-1162

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
