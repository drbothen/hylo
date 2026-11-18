---
document_type: behavioral-contract
level: L3
version: "1.2.3"
status: draft
producer: product-owner
timestamp: 2026-11-19T17:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - behavioral-contracts/BC-ALLOCATION.md
  - product-brief.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "68cd3f4"
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
modified:
  - "2026-11-18T01:42:00Z ADV-P3 remediation A04: canonical gate parameters 1 warm-up + 20 runs per case, nearest-rank p95 = 19th sample, binding per case, no pooling; test target moved to internal/parity"
  - "1.2.2 2026-11-18: ADV-P4 remediation D23 - gate binds on EVERY case p95 (worst case named); VP-036 de-pooled; unreachable EC-005 low-sample note withdrawn"
  - "1.2.3 2026-11-19T17:00:00Z: ADV-P7 remediation A02/OD-191/D26 (orchestrator call 3) - PC-3 gains the conditional large-transcript exemption: exactly one validated case flag timing_exempt: large-transcript (transcript must exceed 512 KB), exempt from the 25 ms target only when it misses it, ceiling 100 ms (OD-191), and exactly one report line whenever the exemption is used; PC-1 states the 20-timed-runs rationale (smallest round count with an interior nearest-rank p95, fixed n, CI-budget judgment call). ARCH-08 and PRD NFR-001 to copy"
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
3. The timing run is a separate test target (`go test -run TestTiming ./internal/parity`
   or a dedicated tool; home `internal/parity` per BC-COMPONENT-MAP par/timing.go,
   ADV-P3-A04). It is not part of the Tier A/B parity verdict.

## Postconditions

1. **Measurement.**
   - CANONICAL GATE PARAMETERS (ADV-P3-A04, aligned with nfr-catalog NFR-001 rows and
     ARCH-08/cicd-setup): for each corpus CASE the harness runs 1 warm-up (rationale,
     convention: absorbs the first-execution page-cache and oracle-start cost so it does
     not skew the timed runs) and then 20 timed executions (nearest-rank p95 = the 19th
     ordered sample, BINDING per case — per case, never pooled across cases or steps).
     The former R = 5 pooled-times formulation was wrong and is superseded.
     Rationale for 20 (pass-7 D26, labeled judgment call): 20 is the smallest round
     sample count whose nearest-rank p95 is an interior order statistic (the 19th of
     20 ordered samples, two steps from the max, so one outlier cannot own the
     percentile) while keeping the timing job's wall time inside the CI budget; the
     count is fixed by construction, so the percentile is comparable across runs and
     OSes.
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
   Percentiles use the nearest-rank method COMPUTED PER CASE on that case's 20
   per-execution render times (no pooling across cases; nearest-rank p95 = the 19th
   ordered sample; ADV-P3-A04).
3. **Gate only on the owner's target.**
   - When the harness setting `HYLO_TIMING_GATE=1` is present, the gate evaluates
     EVERY case's per-case p95 (each from that case's own 20 timed runs; design call 14,
     ADV-P4-D23): if ANY case's p95 > 25.0 ms, the gate fails with
     `timing: p95 <p95> ms > 25 ms target (OD-117, judgment call)` naming the worst
     case. The owner sets
     this setting on the macOS arm64 machine; it is a harness setting, not a D15 key.
   - **Large-transcript exemption (OD-187 + OD-191; pass-7 orchestrator call 3).** The
     corpus contains exactly one case carrying the validated flag
     `timing_exempt: large-transcript`; the corpus validator admits the flag only on
     that one case and only when its transcript fixture exceeds 512 KB (OD-187's size
     condition, validated, not assumed). That case is CONDITIONALLY exempt from the
     25 ms target: if its p95 ≤ 25 ms the ordinary target applies and no exemption is
     reported; if it misses 25 ms, the exemption applies and its ceiling is 100 ms —
     the gate fails if its p95 > 100 ms
     (OD-191, judgment call: 4x the target, well under the refresh interval) — and the
     job prints exactly one report line, e.g.
     `timing: <case> exempt from 25 ms target (timing_exempt: large-transcript, >512 KB); p95 <p95> ms <= 100 ms ceiling`,
     whenever the exemption is used, so a used exemption is never silent. Every other
     case keeps an unconditional 25 ms target.
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
| EC-005 | Tiny corpus subset (few cases) | Unreachable-condition note withdrawn (ADV-P4-D23): every case runs exactly 1 warm-up + 20 timed runs, so the per-case sample count is fixed at 20 by construction and "fewer than 20 total samples" cannot occur; the report lists each case's own `n = 20` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Full synthetic corpus on the owner's Mac, `HYLO_TIMING_GATE=1`, p95 = 9.8 ms | Report `darwin/arm64 n=<N> median … p95 9.8 ms`; pass | happy-path |
| ubuntu-24.04 CI leg, p95 = 31.2 ms | Report printed; pass | edge-case |
| Owner's Mac, gate on, worst-case p95 = 27.4 ms | FAIL `timing: p95 27.4 ms > 25 ms target (OD-117, judgment call)` naming that case | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-036 | Nearest-rank p95 is computed correctly over each case's OWN 20 samples (per case, never pooled; ADV-P4-D23) | table test on the percentile helper |
| VP-036 | The gate fails iff `HYLO_TIMING_GATE=1` and ANY case's p95 > 25.0 ms | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-117 target (2): status line p95 render ≤ 25 ms on the owner's Mac excluding the metrics HTTP wait, vs the measured legacy baseline (median 84.5 ms), labeled JUDGMENT CALL; product-brief Success Criteria (baseline 2026-11-15: median 84.5 ms, p90 101 ms, ~25 ms interpreter start); CLAUDE.md (explain every threshold); D15/OD-57 rationale rule |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 (behavior changes only through named, tested deviations — the timing gate reports, it never changes bytes) |
| Architecture Module | `internal/parity` timing test (BC-COMPONENT-MAP: internal/parity/timing.go (p95 report, HYLO_TIMING_GATE) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.04.001 — related to: per-OS report produced on the CI matrix (non-gating there)
- BC-6.02.003 — depends on: fake VictoriaMetrics that records server-side handling time
- BC-6.01.002 — depends on: child env for the timed binary runs

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/timing.go (p95 report, HYLO_TIMING_GATE) (timing harness) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

> Names provisional — architect (OD-145): harness flag names, the timing method, proposed
> test names and seed paths in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

- VP-036 — timing report and gate properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/timing.go (p95 report, HYLO_TIMING_GATE) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
