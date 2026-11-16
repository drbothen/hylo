---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - behavioral-contracts/BC-ALLOCATION.md
  - product-brief.md
  - owner-decisions-log-2026-11-14.md
  - ../semport/hylo-legacy/statusline-target-design.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (new contract, no legacy source)"
subsystem: "SS-06"
capability: "CAP-009"
legacy_id: "new"
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

# Behavioral Contract BC-6.04.002: Per-OS timing report; p95 <= 25 ms binds on the owner's Mac target

## Description

The harness measures wall time per render of the built `hylo statusline` binary over
the synthetic fixture corpus. The time spent waiting on the metrics HTTP reply is
excluded. The harness reports per-OS percentiles on every OS. The OD-117 target, p95
≤ 25 ms, gates only on the owner's Mac. Shared CI runners report the number without
gating, because runner timing noise would make a 25 ms gate flaky. The 25 ms value is
a labeled **judgment call** (OD-117): roughly 3× faster than the measured legacy
median of 84.5 ms, about 25 ms of which is interpreter start-up that the static binary
removes.

## Preconditions

1. The binary is built once per run (`go build ./cmd/hylo`) and executed as a
   subprocess per step, with the child env of BC-6.01.002. Process start-up is part of
   the measured render, as it is in production.
2. Metrics come from the fake VictoriaMetrics on loopback (BC-6.02.003). The fake VM
   records, per request, the server-side handling time from request receipt to
   response flush.
3. The timing run is a separate test target (`go test -run TestTiming ./internal/statusline`
   or a dedicated tool). It is not part of the Tier A/B parity verdict.

## Postconditions

1. **Measurement.**
   - For each corpus step the harness runs 1 warm-up and then `R = 5` timed
     executions.
   - Render time per execution = process wall time (exec start to exit) minus the fake
     VM's server-side handling time for requests made during that execution.
   - Loopback connect and transfer time stays counted against hylo, which is the
     conservative choice.
2. **Report.** The report is printed on every OS and written as a CI artifact. It
   contains:
   - `os/arch`, sample count `n`;
   - `median`, `p90`, `p95` and `max` in milliseconds with 0.1 ms resolution;
   - the CPython oracle median measured the same way, for reference. Interpreter
     start-up is included on the Python side.
   Percentiles use the nearest-rank method on the pooled per-execution render times.
3. **Gate only on the owner's target.**
   - When the harness setting `HYLO_TIMING_GATE=1` is present, `p95 > 25.0 ms` fails
     with `timing: p95 <p95> ms > 25 ms target (OD-117, judgment call)`. The owner sets
     this setting on the macOS arm64 machine; it is a harness setting, not a D15 key.
   - CI never sets `HYLO_TIMING_GATE`. CI legs print the report and pass whatever the
     value.
4. **Threshold rationale in code.** The 25 ms constant lives in the timing test as a
   named constant. Its comment cites OD-117, labels the value a judgment call, and
   states the measured legacy baseline (2026-11-15: median 84.5 ms, p90 101 ms on a
   synthetic input with no transcript and a metrics fetch failing fast). This
   satisfies the CLAUDE.md "explain every threshold" rule. It is a test target, not
   product behavior, so it is not a config key.

## Invariants

1. Timing never influences parity verdicts, and parity never depends on timing.
2. The metrics HTTP wait is excluded by measurement, never by disabling the fetch.
   ROWS and TTL stay as each case declares them.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | CI windows-2025 leg reports p95 40 ms | Reported; leg passes (no gate in CI) |
| EC-002 | Owner Mac with `HYLO_TIMING_GATE=1`, p95 = 25.0 ms | Pass (the gate is `> 25.0`) |
| EC-003 | Owner Mac with `HYLO_TIMING_GATE=1`, p95 = 25.1 ms | FAIL with the OD-117 message |
| EC-004 | Case with metrics mode `down` (closed listener) | No server-side time to subtract. The connect-refused time (sub-millisecond on loopback) is counted against hylo |
| EC-005 | Fewer than 20 total samples (tiny corpus subset) | Report printed with `n` and a `low sample count` note; gate still applies if enabled |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Full synthetic corpus on the owner's Mac, `HYLO_TIMING_GATE=1`, p95 = 9.8 ms | Report `darwin/arm64 n=<N> median … p95 9.8 ms`; pass | happy-path |
| ubuntu-24.04 CI leg, p95 = 31.2 ms | Report printed; pass | edge-case |
| Owner's Mac, gate on, p95 = 27.4 ms | FAIL `timing: p95 27.4 ms > 25 ms target (OD-117, judgment call)` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | Nearest-rank p95 is computed correctly over pooled samples | table test on the percentile helper |
| VP-TBD | The gate fails iff `HYLO_TIMING_GATE=1` and p95 > 25.0 ms | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-117 target (2): status line p95 render ≤ 25 ms on the owner's Mac excluding the metrics HTTP wait, vs the measured legacy baseline (median 84.5 ms), labeled JUDGMENT CALL; product-brief Success Criteria (baseline 2026-11-15: median 84.5 ms, p90 101 ms, ~25 ms interpreter start); CLAUDE.md (explain every threshold); D15/OD-57 rationale rule |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | — |
| Architecture Module | `internal/statusline` timing test (filled by architect) |
| Stories | TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-6.04.001 — related to: per-OS report produced on the CI matrix (non-gating there)
- BC-6.02.003 — depends on: fake VictoriaMetrics that records server-side handling time
- BC-6.01.002 — depends on: child env for the timed binary runs

## Architecture Anchors (Recommended)

- TBD (filled by architect) — timing harness

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

> Names provisional — architect (OD-145): harness flag names, the timing method, proposed
> test names and seed paths in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

- TBD — timing report and gate properties above
