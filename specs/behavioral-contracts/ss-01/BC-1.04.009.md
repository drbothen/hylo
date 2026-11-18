---
document_type: behavioral-contract
level: L3
version: "1.4.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T15:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md]
input-hash: "81a6f43"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:sparkline (SL:659-690)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-048"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["1.3 2026-11-17: pass-2 remediation ADV-P2-C2-05 (points/scale ranges, OD-162)", "1.4 2026-11-17: pass-4 residual sweep — D4-EX-3 table-test name canonicalized to TestD4EX3_* (ADV-P4-D22)", "1.4.1 2026-11-18: pass-8 remediation ADV-P8-C2-01 (the ramp named as the config key statusline.glyphs.sparkline with its 8-glyph default, OD-189 sibling treatment)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.009: Sparkline glyphs, scale and colors

## Description

The sparkline plots the configured trace (box rate, KV fraction or TTFT) from the last 12
history points — sliced first (`hist[-12:]`), then filtered to those carrying the key —
zero-anchored, with a fading cyan trail, an amber cell for
points marked with preemptions, and a bright head cell. Fewer than two plottable points
yield an empty string. Notation: `\e` is byte 0x1B.

## Preconditions

1. `hist` is the history list (dict points or legacy `[t, v]` lists).
2. Config: `statusline.sparkline.trace` enum `rate|kv|ttft` → key `v|k|f` (legacy
   `TRACE_KEYS`; unknown values are a config error in Go, BC-2.02.004, D4-EX-3);
   `statusline.sparkline.points` 12 (T-006, judgment "long flats read as blobs";
   OD-162 range: Int 1..100 — 0 is a number-range config error because Python
   `hist[-0:]` returns the whole list (SL:663), and 1 is valid but always draws ""
   given PC2's `len(pts) < 2` gate);
   `statusline.sparkline.scale` = fixed top `k` 1.0, floors `v` 1.0 and `f` 0.1, other
   1e-9 (T-045, derived review #17.1; OD-162 range: each value a finite Float > 0,
   out-of-range = number-range config error — a fixed top of 0 is falsy in
   `_SPARK_FIXED.get(key) or …` (SL:671) and silently falls back to the window max,
   and a floor ≤ 0 breaks zero-anchoring); `statusline.sparkline.colors` = trail RGB
   (70,170,190), fade 0.55..1.0, amber (220,170,60), head (140,235,255), preempt-marked
   head = theme yellow `\e[33m` (T-046, owner judgment, presentation); the glyph ramp is
   the config key `statusline.glyphs.sparkline` = exactly 8 ordered
   glyphs `▁▂▃▄▅▆▇█` (default; U+2581..U+2588, OD-02, BC-2.01.004 PC-6 — the ramp
   literals in the vectors are the default spelling, ADV-P8-C2-01).

## Postconditions

1. `pts` = for each point in `hist[-12:]`, normalized (`_norm_pt`), the triple
   `(t, p.get(key), p.get("p"))`, kept only when the value is not None.
2. If `len(pts) < 2` → `""`.
3. `top` = 1.0 when key is `k`; else `Max(Max(vals), floor)` (Python `max` semantics).
4. `idx(v) = Int(Min(Max(v, 0.0) / top * 7, 7) + 0.5)` (half-up, BC-5.01.003).
5. For each trail point `i` in `pts[:-1]`: if `p` truthy → RGB (220,170,60); else
   `fade = 0.55 + 0.45 * i / Max(len(pts) - 2, 1)` and RGB = `int(c * fade)` per channel
   of (70,170,190); emit `"\e[38;2;R;G;Bm" + glyph[idx(v)]`.
6. Head: if `p` truthy → `"\e[33m" + glyph`; else `"\e[38;2;140;235;255m" + glyph`.
7. Return the concatenation + `"\e[0m"`.

## Invariants

1. Bar height is proportional to value (zero-anchored), not min-max scaled.
2. The trail at n = 12 uses exactly: (38,93,104) (41,101,113) (44,108,121) (47,116,130)
   (51,124,138) (54,131,147) (57,139,155) (60,147,164) (63,154,172) (66,162,181)
   (70,170,190).
3. Non-finite inputs follow BC-1.04.014.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | 1 plottable point | `""` |
| EC-002 | Idle box `v` [0.2, 0.6] (floor 1.0) | `▂▅` |
| EC-003 | Flat `v` [3,3,3] | `███` (top = max) |
| EC-004 | Negative value `v` [-5, 2] | `▁█` (clamped to 0) |
| EC-005 | `kv` trace, `k` [0.5, 1.0], both points `p=1` | `\e[38;2;220;170;60m▅\e[33m█\e[0m` |
| EC-006 | Legacy list points `[[900,50],[990,60]]` | `\e[38;2;38;93;104m▇\e[38;2;140;235;255m█\e[0m` |
| EC-007 | `kv` trace, `k` [0.5, 1.0] | `▅█` (fixed top 1.0) |
| EC-008 | `ttft` trace, `f` [0.02, 0.05] (floor 0.1) | `▂▅` |
| EC-009 | idx at top 7: v/top*7 = 0.49 / 0.5 / 2.5 | glyph 0 / 1 / 3 (half-up) |
| EC-010 | Legacy `DGX_SL_TRACE=mine` (or any unknown trace) | not reproduced: approved deviation D4-EX-3 — config error line, no cache writes (BC-2.02.004); legacy fell back to `rate`. OD-105 exclusion entry `D4-EX-3`, dedicated test `TestD4EX3_Enum` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `v` [100, 100.3, 101, 99, 200, 0, 0.5, 50] | `\e[38;2;38;93;104m▅\e[38;2;43;106;118m▅\e[38;2;49;119;133m▅\e[38;2;54;131;147m▄\e[38;2;59;144;161m█\e[38;2;64;157;175m▁\e[38;2;70;170;190m▁\e[38;2;140;235;255m▃\e[0m` | happy-path |
| `v` [1..12] | `\e[38;2;38;93;104m▂\e[38;2;41;101;113m▂\e[38;2;44;108;121m▃\e[38;2;47;116;130m▃\e[38;2;51;124;138m▄\e[38;2;54;131;147m▅\e[38;2;57;139;155m▅\e[38;2;60;147;164m▆\e[38;2;63;154;172m▆\e[38;2;66;162;181m▇\e[38;2;70;170;190m▇\e[38;2;140;235;255m█\e[0m` | happy-path |
| `v` [0.2, 0.6] | `\e[38;2;38;93;104m▂\e[38;2;140;235;255m▅\e[0m` | edge-case |
| `v` [5] | `""` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Glyph count = the number of the last 12 history points carrying the key (slice first, then filter), when ≥ 2, else empty | Go property test (testing/quick) |
| VP-030 | Byte equality with legacy over random finite histories | fuzz (Tier C) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:sparkline (SL:659-690); TRACE_KEYS/_SPARK_FIXED/_SPARK_FLOOR (SL:644-649); SPARK (SL:136); SPARK_PTS (SL:82); TRACE (SL:89) |
| Legacy contract | BC-SL-048 (P3 base; r1 color table via BC-SL-073) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008, DI-012 (unknown-trace D4-EX-3 deviation) |
| Decisions | OD-02 (glyph keys), OD-113 (theme), OD-114 (enum range), OD-57 E-B (T-046 presentation judgment) |
| Architecture Module | `internal/statusline/sparkline.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.014 — refined by: NaN/+Inf crash path
- BC-1.04.003 — depends on: history points
- BC-1.04.008 — composes with: drawn after the box rate
- BC-2.02.004 — related to: unknown trace is a D4-EX-3 config error

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/sparkline.go (glyphs/scale/colors) (sparkline) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — sparkline equivalence

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:644-690) |
| **Confidence** | high — re-executed on CPython 3.11.7 (all vectors above) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if len(pts) < 2: return ""` (SL:666)
- **documentation**: comments SL:645-649, 669-670

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. `int(c * fade)` truncates toward zero per channel; the fade
product must not be FMA-contracted (wrap in `float64(...)`, PR-15).
