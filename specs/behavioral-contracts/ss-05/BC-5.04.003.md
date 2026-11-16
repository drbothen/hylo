---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T21:30:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - ../semport/hylo-legacy/statusline-target-design.md
  - ../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces Python time.time() value discipline at the nine legacy clock reads, P3r1 §A0, DET-01..08)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.04.003: pyfmt.TimeFloat: Python time.time() value discipline (ns→s float, once per render)

## Description

`pyfmt.TimeFloat(t)` reproduces the Python `time.time()` value discipline (design IM-14,
research P20): `float64(t.UnixNano()) / 1e9` — the Python value, not Go's monotonic-annotated
wall-clock methods — read once per render and passed down. Helper-level contract per OD-141
(the nine legacy clock reads, P3r1 §A0, DET-01..08; motivates the idle-widget
minute-straddle fix, DET-08).

## Preconditions

1. `t` is a Go `time.Time` obtained once per render (Env.Now, design §2.1).
2. `HYLO_TEST_NOW` (a decimal string) when set is parsed by both sides identically (§3;
   RK-5 documents it as a harness hook, not a setting).

## Postconditions

1. `TimeFloat(t) = float64(t.UnixNano()) / 1e9` — the Python `time.time()` value, correct
   to the ns-derived float64 (≥ 1 ns granularity below the second is lost to float64, the
   same as Python).
2. Read once per render and passed down; the idle widget's two legacy reads (SL:825, 826)
   receive one value (DET-08 minute-straddle fix).
3. Frozen-clock neutrality: under the harness shim both sides parse `HYLO_TEST_NOW` the
   same way, so `TimeFloat(HYLO_TEST_NOW)` is output-neutral in parity runs (§3).

## Invariants

1. Pure conversion; no monotonic subtraction, no `time.Time.Sub`.
2. The ns→s division is the ONLY permitted clock conversion at status-line sites (D15:
   named helper, one discipline).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | t = epoch second 1794615009.734567891 | 1794615009.7345679 (float64 spelling via Repr) |
| EC-002 | t exactly on the second | .0 fractional — e.g. 1794650400.0 (Python `time.time()` spelling, cache `rl_ts` form) |
| EC-003 | `HYLO_TEST_NOW=1794650400` | parsed to 1794650400.0 on both sides |
| EC-004 | two widgets in one render | same value, not two reads |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| UnixNano 1794615009734567891 | 1794615009.7345679 | happy-path |
| UnixNano 1794650400000000000 | 1794650400.0 | happy-path |
| `HYLO_TEST_NOW` parse agreement | Go and CPython both parse the decimal string to the same float64 | edge-case |

Expectations generated from CPython 3.11 (OD-104 oracle discipline).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | TimeFloat equals CPython time.time() value for sampled instants | CPython oracle table |
| VP-TBD | One read per render (no widget performs its own clock read) | unit test with a counting Env.Now |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-14, research P20; consumers: the nine clock reads (BC-1.05.004, BC-1.04.002/.004, BC-1.02.028, idle widget) |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.04.001 — related to (FromISOFormat, the wall-clock parse sibling)
- BC-5.04.002 — related to (LocalToUnix, the mktime sibling)
- BC-1.04.017 — consumer (idle strict > 300 and age format; DET-08)

## Architecture Anchors (Recommended)

- `architecture/SS-05-pyfmt.md#time` — time.go helpers (TBD)

## Story Anchor (Recommended)

S-TBD — pyfmt time helpers

## VP Anchors (Recommended)

- VP-TBD — value-discipline equality
