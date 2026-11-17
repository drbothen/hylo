---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "12ee8f9"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_telemetry_fields (SL:822-834)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-051"
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

# Behavioral Contract BC-1.04.012: Idle segment

## Description

Row 2 ends with `☾ idle <age>` when the local lane has not received a request for more than
5 minutes and nothing is running on the backend. Only local-lane recency counts, so
cloud-lane traffic cannot mask an idle backend. Notation: `\e` is byte 0x1B.

## Preconditions

1. `last = m.get("dgx_llm_last_dgx_request_timestamp_seconds")` (local-lane last request,
   exported metric; legacy wire name kept, D7).
2. `now` = the single per-render clock read (Go reads it once; legacy reads `time.time()`
   twice at SL:825-826 — output-neutral under the frozen harness clock, design IM-14).
3. Config: `statusline.idle.after_s` 300 (T-011, labeled judgment: "longer than a normal
   think/tool gap between turns", review #20.2), `statusline.idle.running_below` 1
   (T-108, judgment: review #20 threshold choice).

## Postconditions

1. Segment exists iff `last` is truthy, `last > 0`, `now - last > 300` (strict) and
   `(m.get("vllm:num_requests_running") or 0) < 1`.
2. `idle_min = int((now - last) // 60)` (float floor division, CPython `float_divmod`
   semantics, BC-5.01.003).
3. Age text and boundaries per BC-1.04.017: `<d>d<hh>h` from 1440 min, `<h>h<mm>m` from
   60 min, else `<m>m`.
4. Segment = `"\e[36m☾ idle " + age + "\e[0m"`, appended last in row 2.

## Invariants

1. A running request (≥ 1) always suppresses the segment.
2. Stale mode does not change this segment.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `last` absent, 0, negative, NaN | no segment |
| EC-002 | running 1 | no segment |
| EC-003 | running 0.5 | shown (`< 1`) |
| EC-004 | running NaN | no segment (`nan < 1` false) |
| EC-005 | running absent or 0.0 | treated as 0 → shown |

## Canonical Test Vectors

`now` = 2000000000.0.

| Input | Expected Output | Category |
|-------|----------------|----------|
| last = now - 360, running absent | `\e[36m☾ idle 6m\e[0m` | happy-path |
| last = now - 66000 | `\e[36m☾ idle 18h20m\e[0m` | happy-path |
| last = now - 300.0 | no segment | edge-case |
| last = now - 400, running 1 | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Seven-case review #20 table reproduces legacy bytes | manual (table) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:822-834); IDLE_AFTER (SL:90-93) |
| Legacy contract | BC-SL-051 (P3 base; r1 refined, review #20, 7 cases) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007 |
| Decisions | OD-113; D7 (metric name frozen) |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.017 — refined by: strict gate and age format
- BC-5.01.003 — depends on: float floor division

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/row2.go (idle) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — idle table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:822-834) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: SL:825
- **documentation**: comment SL:822-823, 827

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (clock injected) |
| **Global state access** | reads config |
| **Deterministic** | yes given `now` |
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure |

#### Refactoring Notes

Pass `now` in; read the clock once per render (removes legacy's minute-straddle between
SL:825 and SL:826 with a live clock; identical under the frozen clock).
