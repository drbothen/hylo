---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "8e821c7"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_telemetry_fields (SL:732-741)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-045"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["2026-11-18 (v1.2.1) pass-4 remediation ADV-P4-C2-17 (PC3 states the statusline.queue.yellow=false never-yellow branch as an output)", "2026-11-18 (v1.2.2) pass-11 OD-194 consumer (PC3 names statusline.labels.rate and statusline.labels.queue beside their defaults; the · separator carries the named-format-constant note)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.006: Queue segment

## Description

When the backend reports running requests, row 2 shows `r<running>·q<waiting>`, yellow
when anything waits or any preemption happened in the last 5 minutes, otherwise green.
Notation: `\e` is byte 0x1B.

## Preconditions

1. `m` is a dict sample; the segment is considered only if
   `m.get("vllm:num_requests_running")` is not None.
2. Yellow rule = `statusline.queue.yellow` (T-047, derived from review #14:
   "q > 0 or preempt > 0") — a boolean toggle, default `true`; when `true` the fixed
   rule `q > 0 or preempt > 0` decides yellow, when `false` the segment never yellows.

## Postconditions

1. `r` = running; `q = m.get("vllm:num_requests_waiting", 0)`.
2. `busy = q > 0 or m.get("dgx_preempt:rate5m", 0) > 0`.
3. Segment = `<colour> + labels.rate + F(r,0) + "·" + labels.queue + F(q,0) + "\e[0m"`
   where `labels.rate` = `statusline.labels.rate` (Text, default `r`, SL:741, OD-194)
   and `labels.queue` = `statusline.labels.queue` (Text, default `q`, SL:741, OD-194;
   the `·` between them stays literal — a named format constant, not config: template
   scaffolding, only the readable words vary); `F(x,0)` = Python
   `f"{x:.0f}"` (half-even on the binary value; `nan`/`inf` spellings, BC-5.01.001) and
   `<colour>` = `"\e[33m"` if `busy` else `"\e[32m"` when `statusline.queue.yellow` is
   `true` (default), and always `"\e[32m"` when it is `false` (never yellow; OD-175 —
   the configured branch restated as an output, ADV-P4-C2-17).
4. Stale mode does not change this segment.

## Invariants

1. Color tests the raw values, not the rounded display (`q=0.5` shows `q0` in yellow).
2. Absent running → no segment.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `r0·q>0` (stalled scheduler) | yellow |
| EC-002 | running 1, preempt 0.01 | yellow `r1·q0` |
| EC-003 | running 2.6, waiting 0.5 | yellow `r3·q0` |
| EC-004 | running NaN, waiting NaN | green `rnan·qnan` (`nan > 0` false) |
| EC-005 | running NaN, waiting absent | green `rnan·q0` |
| EC-006 | running 0.0 | segment shown (`0.0` is not None) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| running 3, waiting 0, preempt 0 | `\e[32mr3·q0\e[0m` | happy-path |
| running 0, waiting 2 | `\e[33mr0·q2\e[0m` | edge-case |
| running 2.6, waiting 0.5 | `\e[33mr3·q0\e[0m` | edge-case |
| running absent | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Color = yellow iff `q > 0 or preempt > 0` under Python comparison semantics (NaN false) | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:732-741) |
| Legacy contract | BC-SL-045 (P3 base, review #14) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | OD-113 (theme colors) |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.016 — refined by: NaN/inf rendering rows
- BC-1.04.003 — related to: the same preempt rule marks history points (T-107)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/row2.go (queue) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — queue color rule

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:732-741) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if r is not None` (SL:733); `busy = ...` (SL:740)

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
