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
extracted_from: "legacy/dgx_statusline.py:render_telemetry_fields (SL:801-820)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-050"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["1.2.1 2026-11-18: pass-8 remediation ADV-P8-C2-01 (the marker named as the config key statusline.glyphs.watts with default ⚡, OD-189 sibling treatment)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.011: Power segment

## Description

When GPU power is reported, row 2 shows `⚡<GPU>W` in neutral white, then the whole-box
wall estimate `·<wall>W` carrying the color (red above 95 %, yellow above 80 % of the
1,600 W rating), the GPU temperature, and the running electricity cost in ¢/h. Notation:
`\e` is byte 0x1B.

## Preconditions

1. `w = m.get("DCGM_FI_DEV_POWER_USAGE")`, `t = m.get("DCGM_FI_DEV_GPU_TEMP")`,
   `wall = m.get("dgx_power:est_wall_watts")`, `rate_c = m.get("dgx_power:rate_usd_per_kwh")`.
2. Config: `statusline.power.wall_red_w` 1520 and `statusline.power.wall_yellow_w` 1280
   (T-053, derived: 95 % / 80 % of the 1,600 W system rating).

## Postconditions

1. Segment exists only if `w is not None`.
2. `wc` = `"\e[31m"` if `wall > 1520`, `"\e[33m"` if `wall > 1280`, else `"\e[97m"`,
   evaluated only when `wall` is truthy; otherwise `"\e[97m"`.
3. `txt = "\e[97m" + glyphs.watts + F(w,0) + "W\e[0m"`, where `glyphs.watts` =
   `statusline.glyphs.watts` (Text, default `⚡` U+26A1, BC-2.01.004 PC-6; the ⚡
   literals in the vectors are the default spelling, ADV-P8-C2-01).
4. If `wall` truthy: `txt += "\e[90m·\e[0m" + wc + F(wall,0) + "W\e[0m"`.
5. If `t is not None`: `txt += "\e[90m " + F(t,0) + "°\e[0m"`.
6. If `wall` and `rate_c` both truthy: `txt += "\e[90m " + F(wall / 1000 * rate_c * 100, 0) + "¢/h\e[0m"`
   (operation order as written; no FMA contraction).
7. Stale mode does not change this segment.

## Invariants

1. The GPU number is never colored; the color judges the wall estimate it is attached to.
2. Wall 0 or rate 0 count as absent (Python truthiness).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | w 900, wall 0, temp 50, rate 0.2 | `⚡900W` + ` 50°` only (no wall, no ¢/h) |
| EC-002 | wall absent | GPU only |
| EC-003 | wall 1520.0 | yellow `1520W` (`> 1520` false) |
| EC-004 | wall 1520.4 | red `1520W` (color/number mismatch, BC-1.04.016) |
| EC-005 | wall 1280.0 | white `1280W` |
| EC-006 | rate 0 | no ¢/h |
| EC-007 | all NaN | `⚡nanW·nanW nan° nan¢/h` with white wall (BC-1.04.016) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| w 207.1, wall 346.25, t 36, rate 0.12 | `\e[97m⚡207W\e[0m\e[90m·\e[0m\e[97m346W\e[0m\e[90m 36°\e[0m\e[90m 4¢/h\e[0m` | happy-path |
| w 1059, wall 1400, t 66, rate 0.24 | `\e[97m⚡1059W\e[0m\e[90m·\e[0m\e[33m1400W\e[0m\e[90m 66°\e[0m\e[90m 34¢/h\e[0m` | happy-path |
| w 800, wall 1600, rate 0 | `\e[97m⚡800W\e[0m\e[90m·\e[0m\e[31m1600W\e[0m` | edge-case |
| w absent | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Review #19 table reproduces legacy bytes | manual (table) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:801-820) |
| Legacy contract | BC-SL-050 (P3 base, review #19) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | OD-113 |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.016 — refined by: NaN/inf and wall color mismatch

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/row2.go (power) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — power table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:801-820) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if w is not None`, `if wall`, `if wall and rate_c` (SL:802, 814, 817)
- **documentation**: comment SL:805-811

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
