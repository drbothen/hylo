---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md]
input-hash: "5c176a5"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-084"
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

# Behavioral Contract BC-1.04.017: Idle strict > 300 and age format

## Description

Pins the idle gate's strict comparison and the idle-age text. The gate opens only when
more than 300 s (strictly) have passed since the last local-lane request; the age is whole
minutes by floor division, shown as minutes, hours+minutes or days+hours with zero-padded
second fields. Notation: `\e` is byte 0x1B.

## Preconditions

1. The other idle conditions of BC-1.04.012 hold (`last` truthy and `> 0`, running < 1).
2. `delta = now - last`.

## Postconditions

1. Shown iff `delta > 300` (strict; 300.0 hidden).
2. `idle_min = int(delta // 60)` (Python float floor division).
3. Age text:
   - `idle_min >= 1440` → `str(idle_min // 1440) + "d" + D(idle_min % 1440 // 60, 2, zeroPad) + "h"`
   - `idle_min >= 60` → `str(idle_min // 60) + "h" + D(idle_min % 60, 2, zeroPad) + "m"`
   - else → `str(idle_min) + "m"`
4. Segment = `"\e[36m☾ idle " + age + "\e[0m"`.

## Invariants

1. Minutes are truncated, never rounded (300.5 s → `5m`).
2. The day branch drops minutes; the hour branch drops seconds.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | delta 300.0 | hidden |
| EC-002 | delta 300.5 | `5m` |
| EC-003 | delta 3599 / 3600 | `59m` / `1h00m` |
| EC-004 | delta 86399 | `23h59m` |
| EC-005 | delta 86400 | `1d00h` |
| EC-006 | delta 864059 (10 days + 59 s) | `10d00h` |
| EC-007 | delta NaN (via `last` NaN) | hidden (`nan > 0` false at the `last` check) |

## Canonical Test Vectors

`now` = 2000000000.0, running absent.

| Input | Expected Output | Category |
|-------|----------------|----------|
| delta 360 | `\e[36m☾ idle 6m\e[0m` | happy-path |
| delta 66000 | `\e[36m☾ idle 18h20m\e[0m` | happy-path |
| delta 274000 | `\e[36m☾ idle 3d04h\e[0m` | edge-case |
| delta 300.5 | `\e[36m☾ idle 5m\e[0m` | edge-case |
| delta 300.0 | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Age text equals legacy for every integer delta in [301, 10^7] and random float deltas | proptest |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:824-834); IDLE_AFTER (SL:93) |
| Legacy contract | BC-SL-084 (P3 r1 new) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | OD-57 (T-011 labeled judgment) |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.012 — refines: idle segment
- BC-5.01.003 — depends on: float floor division

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#row-2` — internal/statusline/row2.go (idle > 300, age format) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — idle age format

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:825-833) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `time.time() - last > IDLE_AFTER` (SL:825); branches SL:828-833

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (clock injected) |
| **Global state access** | reads config |
| **Deterministic** | yes given `now` |
| **Thread safety** | Send + Sync |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. Use `pyfmt.FloorDiv` (CPython `float_divmod`), not
`math.Floor(a/b)`.
