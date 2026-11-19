---
document_type: behavioral-contract
level: L3
version: "1.2.5"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "84514f5"
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
modified: ["1.2 pass-6 remediation (ADV-P6-B01 call 10 + B08): for-all percentage row re-anchored from VP-028 to VP-041 (VP-028 keeps the golden leg); the composition glyph/colour mapping names its registry keys tools/conversation/thinking instead of the wildcard statusline.glyphs.* (Inv 2 and Config keys row); 2026-11-19T04:00:00Z", "1.2.1 pass-8 remediation (ADV-P8-B08): new Inv 4 pins the ` <1%` zero-bucket body as a named format constant, not config (D15); no behavioral change; 2026-11-19T08:00:00Z", "1.2.2 pass-12 remediation (ADV-P12-B01; orchestrator call 12): new EC-010 and vector row — non-numeric buckets restored from a hand-edited mix cache reach sum(counts[:3]) (SL:1181), the OD-160 foreign-cache vector CP-C07 (allocated from the formerly reserved id, rows built by the architect in error-taxonomy); Go table test, not byte-parity; no behavioral change; 2026-11-23T00:00:00Z", "1.2.3 pass-12 residual sweep (orchestrator pass-12 residual register alignment): EC-010, its vector row and the 1.2.2 note renumber CP-C12 to CP-C07 per the orchestrator ruling that the formerly reserved id is ALLOCATED, keeping the register label CP-C01..C10 true; no behavioral change; 2026-11-23T14:00:00Z", "2026-11-24T01:00:00Z (1.2.4): pass-14 remediation (ADV-P14-B06): PC3 declares the single-space bit joiner (SL:1174) a named format constant of this widget, not config (D15 rationale, sibling of the Inv-4 zero-bucket declaration); no behavioral change", "1.2.5 2026-11-26T15:00:00Z: pass-14 residual sweep (OD-160 owner id-range alignment): EC-010 gains the positive-giant bucket OverflowError leg CP-C52 (ratio-dependent, SL:1173; negative giant skipped by n > 0); no behavioral change"]
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
3. Segment = bits joined by a single space; no segment if no bit. The single-space joiner is a
   **named format constant** of this widget, not config (D15 rationale: intra-segment output markup,
   parity-bound at one byte; the theme's `statusline.theme.separator` governs inter-segment
   separators, not intra-segment markup — no ruling mints a key for this site).
4. Position: after the thermometer (BC-1.02.006), before cache hit (BC-1.02.008).

## Invariants

1. Elements 4..n of `mix` (token totals, last-turn data) never affect this segment
   (SL:1158-1163: summing mixed units diluted the percentages).
2. Bucket order and glyph/colour mapping are fixed (glyphs from the registry keys
   `statusline.glyphs.tools`, `statusline.glyphs.conversation`, `statusline.glyphs.thinking`,
   colours from `statusline.theme.*`; defaults SL:1167).
3. Rounding is half-even, never half-up: 12.5 → 12, 62.5 → 62.
4. The ` <1%` body of a zero bucket (PC2) is a **named format constant** of this widget, not
   config (D15 rationale: display-format constant of the output, parity-bound at four bytes;
   why not config = no ruling mints a key for this site).

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
| EC-010 | a restored mix cache holds non-numeric bucket values that reach the `sum(counts[:3])` total (SL:1181; foreign-cache shape, **OD-160**, **CP-C07** scalars, **CP-C52** giants) | legacy TypeError → guard line `\e[90mstatusline degraded\e[0m\n`, exit 0; unreachable on Go-authored caches; Go's foreign-cache behavior carries exclusion **OD-160** (ruling Q-b) — Go table test, not byte-compared; a bucket a POSITIVE giant exact int passes `sum` and `n > 0` exactly and raises OverflowError at `round(n / total * 100)` only when the true-division quotient exceeds float64 (ratio-dependent, SL:1173; a negative giant is skipped by `n > 0`; **CP-C52**, measured pass-14) |

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
| hand-edited cached mix `["x", 2, 3]` | whole stdout = `\e[90mstatusline degraded\e[0m\n`, exit 0 (foreign-cache vector, CP-C07 — see EC-010; exclusion **OD-160**, ruling Q-b) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-041 | For all non-negative int triples with positive sum, each pct equals CPython `round(n/total*100)` | property test against `pyfmt.Round` + CPython goldens — for-all leg (VP-028 delivers the oracle legs) |
| VP-028 | Bytes equal the oracle on the pass-3 r1 vector table | table test — golden leg |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:mix_labels (SL:1157-1174; rounding SL:1171) and mix_segment (SL:1177-1183); call site render_lane SL:466-468 |
| Legacy contract | BC-SL-012 |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-103 (pyfmt Round), OD-113 (theme), OD-02 (glyph keys) |
| Config keys | `statusline.glyphs.tools` (▤), `statusline.glyphs.conversation` (❙), `statusline.glyphs.thinking` (◈), `statusline.theme.*` (cyan, green, magenta, reset) |
| Architecture Module | `internal/statusline/context.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.03.002 — depends on (mix cache supplies the counts)
- BC-5.01.001 — depends on (half-even Round)
- BC-1.02.006 — composes with (preceding segment)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#context` — internal/statusline/context.go (half-even percentage) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — context widgets story

## VP Anchors (Recommended)

- VP-041 — half-even percentage for-all property (VP-028 retains the oracle legs)

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
