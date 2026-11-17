---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r7.md]
input-hash: "58646e3"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-075"
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

# Behavioral Contract BC-1.04.016: Row-2 NaN/inf rendering; wall-colour mismatch

## Description

Outside the two crash paths, non-finite values in the queue, throughput, TTFT and power
fields render without crashing, using Python's spellings (`nan`, `inf`, `-inf`) and
Python comparison semantics (every comparison with NaN is false). Colors test raw values,
so a displayed number can disagree with its color (wall 1520.4 W shows red `1520W`).
Latent in production (capture 2026-11-14). Notation: `\e` is byte 0x1B.

## Preconditions

1. Row 2 is rendered with a dict sample containing NaN or ±Inf in one of: running,
   waiting, preempt rate, box rate, TTFT, TTFT sample count, GPU watts, wall watts,
   temperature, tariff.
2. `F(x, p)` follows BC-5.01.001: Go must emit `nan`/`inf`/`-inf`, never `NaN`/`+Inf`.

## Postconditions

1. Queue: NaN running/waiting → green `rnan·qnan` (`nan > 0` false).
2. TTFT: +Inf → yellow `◔infs` (`inf >= 10` → `.0f` → `inf`; `inf > 8`); `n` NaN → not
   "max"; ttft NaN → hidden (BC-1.04.010).
3. Power: all NaN → `⚡nanW·nanW nan° nan¢/h`, wall colored white (`nan > 1520` and
   `nan > 1280` false; NaN is truthy so the wall and ¢/h parts are shown).
4. Wall color mismatch: the color tests `wall > 1520` on the raw value, the text uses
   `.0f`, so 1520.4 → red `1520W` while 1520.0 → yellow `1520W`.
5. Box rate NaN → `▣nant/s` (sparkline behavior per BC-1.04.014).

## Invariants

1. None of these inputs raise.
2. Output bytes equal legacy's for every non-finite value class.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | running 2.6, waiting 0.5 | yellow `r3·q0` (q > 0 though it displays 0) |
| EC-002 | TTFT -1.0 | grey `◔-1.0s` |
| EC-003 | TTFT 3.0 with n NaN | grey `◔3.0s` |
| EC-004 | wall 1520.0 | yellow `1520W` |
| EC-005 | GPU watts +Inf, no wall | `\e[97m⚡infW\e[0m` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| w 1059, wall 1400, t 66, rate 0.24 | `\e[97m⚡1059W\e[0m\e[90m·\e[0m\e[33m1400W\e[0m\e[90m 66°\e[0m\e[90m 34¢/h\e[0m` | happy-path |
| w 900, wall 1520.4 | `\e[97m⚡900W\e[0m\e[90m·\e[0m\e[31m1520W\e[0m` | edge-case |
| running NaN, waiting NaN | `\e[32mrnan·qnan\e[0m` | edge-case |
| TTFT +Inf | `\e[33m◔infs\e[0m` | edge-case |
| w, wall, t, rate all NaN | `\e[97m⚡nanW\e[0m\e[90m·\e[0m\e[97mnanW\e[0m\e[90m nan°\e[0m\e[90m nan¢/h\e[0m` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030, VP-001 | For each field × {NaN, +Inf, -Inf}, Go bytes equal legacy bytes and no error is returned | manual (table) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:732-741, 772-785, 792-820) |
| Legacy contract | BC-SL-075 (P3 r1 new; r7 flag "latent in production") |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | owner ruling on catalogued crash paths (P3 r7 §5) |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.006 / BC-1.04.010 / BC-1.04.011 — refines: queue, TTFT, power
- BC-5.01.001 — depends on: non-finite spellings

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#row-2` — internal/statusline/row2.go (NaN/inf, wall mismatch) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030, VP-001 — non-finite rendering table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:732-820) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: Python float formatting and NaN comparison semantics

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Send + Sync |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; all formatting goes through `pyfmt.F`.
