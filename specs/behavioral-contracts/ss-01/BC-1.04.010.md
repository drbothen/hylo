---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "5f0276f"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_telemetry_fields (SL:792-799)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-049"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["1.2.1 2026-11-18: pass-8 remediation ADV-P8-C2-01 (the marker named as the config key statusline.glyphs.ttft with default ◔, OD-189 sibling treatment)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.010: TTFT segment

## Description

Row 2 shows the backend's box-wide 30-minute p95 time-to-first-token as `◔<value>`. With
fewer than 20 requests behind the percentile the value is really the maximum, so it renders
grey as `◔max <value>` and never turns yellow; otherwise it is yellow above 8 s, grey
otherwise. A NaN value hides the segment. Notation: `\e` is byte 0x1B.

## Preconditions

1. `ttft = m.get("dgx_ttft:p95_30m")`, `n = m.get("dgx_sl:ttft_n30m")`.
2. Config: `statusline.ttft.min_samples` 20 (T-015, derived: below 20 samples the p95 is
   the maximum, 1/20 = 5 %), `statusline.ttft.integer_from_s` 10 (T-051, derived: histogram
   buckets 20/40/80/… s, review #18.2), `statusline.ttft.yellow_s` 8 (T-052, measured:
   THRESHOLDS §8b).

## Postconditions

1. Segment exists only if `ttft` is a number and not NaN.
2. `val = F(ttft,0) + "s"` if `ttft >= 10`, else `F(ttft,1) + "s"` (formatting boundaries
   pinned in BC-1.04.019).
3. If `n` is a number and `n < 20`: segment = `"\e[90m" + glyphs.ttft + "max " + val + "\e[0m"`.
4. Else: segment = `("\e[33m" if ttft > 8 else "\e[90m") + glyphs.ttft + val + "\e[0m"`.
   In both forms `glyphs.ttft` = `statusline.glyphs.ttft` (Text, default `◔` U+25D4,
   BC-2.01.004 PC-6; the ◔ literals in the vectors are the default spelling,
   ADV-P8-C2-01).
5. Stale mode does not change this segment.

## Invariants

1. A "max" segment is never yellow.
2. Color tests the raw value (`> 8`), not the rounded display.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | ttft absent or NaN | no segment |
| EC-002 | n absent or non-numeric | normal rule (not max) |
| EC-003 | n NaN | normal rule (`nan < 20` false) |
| EC-004 | n 19.999 | max |
| EC-005 | n 20 | normal rule |
| EC-006 | ttft +inf | `\e[33m◔infs\e[0m` (BC-1.04.016) |
| EC-007 | ttft -1.0 | `\e[90m◔-1.0s\e[0m` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| ttft 4.2, n absent | `\e[90m◔4.2s\e[0m` | happy-path |
| ttft 0.059, n 6 | `\e[90m◔max 0.1s\e[0m` | edge-case |
| ttft 116, n 5 | `\e[90m◔max 116s\e[0m` | edge-case |
| ttft NaN | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Eight-case review #18 table reproduces legacy bytes | manual (table) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:792-799); TTFT_MIN_N (SL:124) |
| Legacy contract | BC-SL-049 (P3 base, review #18, 8 cases) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | OD-113 |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.019 — refined by: format boundaries
- BC-1.04.016 — refined by: non-finite rendering

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/row2.go (TTFT) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — TTFT table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:787-799) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(ttft, (int, float)) and not math.isnan(ttft)` (SL:793); `n < TTFT_MIN_N` (SL:796)
- **documentation**: comment SL:787-791

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
