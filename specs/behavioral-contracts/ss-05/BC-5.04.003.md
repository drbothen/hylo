---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md
input-hash: "0267ecc"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces Python time.time() value discipline at the ten legacy clock reads, P3r1 §A0, DET-01..08)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D27: precondition 2 pins the malformed HYLO_TEST_NOW set (nan/inf/-inf/underscore/whitespace/empty)"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D03+D27+D10: TimeFloat takes time.Time per ARCH-06 canon; HYLO_TEST_NOW resolved once to time.Time (never a raw string), malformed = non-finite/non-decimal; subagent now_ms read SL:889 added to consumers"
  - "1.2.4 2026-11-18: ADV-P4 remediation D24+D34 - HYLO_TEST_NOW grammar pinned (finite decimal within time.Time range; nan/inf/0x/underscore/whitespace/1e300 malformed) with BC-6.01.003 as the single owner; pyfmt contract de-duplicated to value discipline only"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.04.003: pyfmt.TimeFloat: Python time.time() value discipline (ns→s float, once per render)

## Description

`pyfmt.TimeFloat(t time.Time) float64` (ADV-P3-D03: aligned with the ARCH-06 canon row
`TimeFloat(t time.Time) float64`) reproduces the Python `time.time()` value discipline (design IM-14,
research P20): with `ns = t.UnixNano()` read once per render, the value is
`float64(ns) / 1e9` — the Python value, not Go's monotonic-annotated
wall-clock methods — read once per render and passed down. Helper-level contract per OD-141
(the ten legacy clock reads, P3r1 §A0, DET-01..08; motivates the idle-widget
minute-straddle fix, DET-08).

## Preconditions

1. `t` is the wall-clock instant obtained once per render from `Env.Now`
   (design §2.1); the caller owns the single read, and the helper derives
   `ns = t.UnixNano()` internally.
2. `HYLO_TEST_NOW` (a decimal string) when set is parsed by both sides identically (§3;
   RK-5 documents it as a harness hook, not a setting). **The grammar is owned by
   BC-6.01.003** (cmd-layer shim duty, ADV-P4-D34); summarized here only for the helper's
   parity-neutrality claim: a value is well-formed iff it matches
   `^[+-]?[0-9]+(\.[0-9]*)?([eE][+-]?[0-9]+)?$`, parses to a finite float64, and lies
   within the `time.Time` representable range (|seconds| ≤ 62135596800, years 1..9999);
   everything else — `abc`, empty, `nan`, `inf`, `-inf`, `0x1p3`, containing `_` or
   whitespace, or out-of-range like `1e300` (unspecified before, ADV-P4-D24) — is
   malformed and ignored with exactly one stderr warning, the real clock used. It never
   config-errors and never degrades the line (spec choice, ADV-P1-D22).

## Postconditions

1. `TimeFloat(ns) = float64(ns) / 1e9` — the Python `time.time()` value, correct
   to the ns-derived float64 (≥ 1 ns granularity below the second is lost to float64, the
   same as Python).
2. Read once per render and passed down; the idle widget's two legacy reads (SL:825, 826)
   receive one value (DET-08 minute-straddle fix).
3. Frozen-clock neutrality: under the harness shim both sides parse `HYLO_TEST_NOW` the
   same way — the decimal string is resolved ONCE into a `time.Time` (per the BC-6.01.003
   grammar of precondition 2, whose well-formed/malformed split both shims implement
   identically) — so
   `TimeFloat(resolvedNow)` is output-neutral in parity runs (§3). `TimeFloat` never
   receives the raw string (ADV-P3-D27). Parsing and warning are cmd-layer duties, not
   pyfmt's (ADV-P4-D34); this contract pins only the value discipline.

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
| EC-005 | `HYLO_TEST_NOW=1e300`; `HYLO_TEST_NOW=0x1p3` | both malformed (out-of-range / non-decimal, ADV-P4-D24): one stderr warning, real clock used |

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
| VP-026, VP-007 (frontmatter closure) | TimeFloat equals CPython time.time() value for sampled instants | CPython oracle table |
| VP-026, VP-007 (frontmatter closure) | One read per render (no widget performs its own clock read) | unit test with a counting Env.Now |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-14, research P20; consumers: the nine clock reads (BC-1.05.004, BC-1.04.002/.004, BC-1.02.028, idle widget) plus the subagent `now_ms` read SL:889 (BC-1.07.007, ADV-P3-D10) |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| L2 Domain Invariants | DI-012 (byte parity machinery) |
| Architecture Module | `internal/pyfmt` time.go (BC-COMPONENT-MAP: internal/pyfmt/time.go (TimeFloat) — ARCH-06) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.04.001 — related to (FromISOFormat, the wall-clock parse sibling)
- BC-5.04.002 — related to (LocalToUnix, the mktime sibling)
- BC-1.04.017 — consumer (idle strict > 300 and age format; DET-08)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#time` — internal/pyfmt/time.go (TimeFloat) (time.go helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

S-TBD — pyfmt time helpers

## VP Anchors (Recommended)

- VP-026, VP-007 — value-discipline equality

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/time.go (TimeFloat)` (BC-COMPONENT-MAP: py/time.go (TimeFloat) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
