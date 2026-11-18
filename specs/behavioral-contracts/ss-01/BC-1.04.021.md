---
document_type: behavioral-contract
level: L3
version: "1.3.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr.md]
input-hash: "e6b9d0e"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:get_sample (SL:337)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-092"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.3 2026-11-18: pass-4 residual sweep — D4-EX-3 table-test name canonicalized to TestD4EX3_* (ADV-P4-D22)"
  - "1.3.1 2026-11-18: pass-6 metadata alignment (ADV-P6-C2-15) — D22 sweep entry redated to the pass-4 burst date (2026-11-18) and timestamp raised above the last modified entry; no behavioral change"
  - "1.3.2 2026-11-18: pass-7 remediation ADV-P7-C2-11 (VP-030 property leg gains the monotonic non-decreasing clock precondition — a backward step voids the appended-gap property per EC-003)"
  - "1.3.3 2026-11-18: pass-9 remediation ADV-P9-C2-09 sibling sweep (PC1/PC2 name the registered key statusline.sparkline.min_gap_s beside its default literal)"
  - "1.3.4 2026-11-18: pass-11 remediation ADV-P11-C2-06 (Description, Pre 1 and PC3 respelled against statusline.sparkline.min_gap_s instead of the literal 2 s — the key's finite > 0 range means the gap decides appends whenever TTL < min_gap_s, e.g. min_gap 5 with TTL 4)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.021: HIST_MIN_GAP reachability (seeded)

## Description

With TTL ≥ the minimum gap (`statusline.sparkline.min_gap_s`, default 2), fetches (and
therefore history appends) are at least TTL apart, so the minimum gap never decides
anything in steady state. It is reachable whenever TTL < min_gap_s (the key's range is
finite > 0 — for example min_gap 5 with TTL 4), with a seeded or foreign history point
newer than `now - min_gap_s`, or a backward clock
step. The Go code must keep the gap rule anyway, and a seeded table test must exercise it.

## Preconditions

1. A successful fetch at `now` (BC-1.04.002), history rules per BC-1.04.003,
   `min_gap_s` = `statusline.sparkline.min_gap_s` = 2 (T-008; OD-55 keeps it as a key
   "only takes effect when TTL < min_gap_s or history is seeded").

## Postconditions

1. If the newest kept history point has
   `now - t < statusline.sparkline.min_gap_s` (default 2), no point is appended for this
   fetch; the sample is still stored and the row still renders from it.
2. If `now - t >= statusline.sparkline.min_gap_s` (default 2), a point is appended.
3. In steady state with TTL ≥ min_gap_s (e.g. TTL 4 at the default min_gap 2),
   consecutive points are ≥ TTL apart (gap never bites); with an allowed
   TTL < min_gap_s the gap decides appends in steady state (e.g. min_gap 5, TTL 4).

## Invariants

1. The gap rule is present in Go even though it is inert at the default TTL.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Seeded newest point `t`=999.0, fetch at 1000 | not appended |
| EC-002 | Seeded newest point `t`=998.0, fetch at 1000 | appended (gap exactly 2) |
| EC-003 | Seeded newest point in the future (`t`=1005, backward clock) | not appended (`-5 < 2`) |
| EC-004 | TTL 1 s, fetches at 1000 and 1001 | second point not appended |
| EC-005 | TTL `nan` (legacy: fetch every refresh) | not reproduced: D4-EX-3 config error (BC-2.02.002); OD-105 exclusion entry `D4-EX-3`, test `TestD4EX3_Number` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| seed `{"hist": [{"t": 998.0, "v": 5.0}]}`, now 1000, sample `{"dgx_sl:gen_rate1m": 9.0}` | cache `{"hist": [{"t": 998.0, "v": 5.0}, {"t": 1000.0, "v": 9.0}], "fetch_ts": 1000.0, "up": true, "ts": 1000.0, "sample": {"dgx_sl:gen_rate1m": 9.0}}` | happy-path |
| seed `{"hist": [{"t": 999.0, "v": 5.0}]}`, same | cache `{"hist": [{"t": 999.0, "v": 5.0}], "fetch_ts": 1000.0, "up": true, "ts": 1000.0, "sample": {"dgx_sl:gen_rate1m": 9.0}}` | edge-case |
| BC-1.04.020 step 0 (newest seed 998.5, now 1000) | 80 not plotted; sparkline `▇█` from 60, 70 | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | For TTL ≥ 2 and unseeded history, every appended point is ≥ TTL after the previous | Go property test (testing/quick); PRECONDITION: the generated clock is MONOTONIC NON-DECREASING — a backward step voids the property (EC-003: a newest point in the future suppresses appending), ADV-P7-C2-11 |
| VP-030 | Seeded gap table matches legacy bytes | manual (table) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:get_sample (SL:337); HIST_MIN_GAP (SL:84) |
| Legacy contract | BC-SL-092 (P3 r2 §A2); P4 F-2 |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-012 (TTL nan D4-EX-3 deviation, EC-005) |
| Decisions | OD-55, OD-57 E-0 (T-008), OD-114 |
| Architecture Module | `internal/statusline/sample.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.003 — refines: history rules
- BC-1.04.020 — related to: step 0 is a seeded gap case

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#effect-step-script-design-doc-31-normative` — internal/statusline/sample.go (HIST_MIN_GAP) (history storage) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — gap reachability

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:337) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if not hist or now - hist[-1]["t"] >= HIST_MIN_GAP` (SL:337)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (within the history step) |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
