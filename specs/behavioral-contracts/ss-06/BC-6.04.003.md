---
document_type: behavioral-contract
level: L3
version: "1.2.7"
status: draft
producer: product-owner
timestamp: 2026-11-21T07:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
input-hash: "1162cba"
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
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D04+D25+D31: --subagent family in generator domain; OS-scoped exclusions named (Windows naive timestamps, OD-159/160/161); provenance updated to OD-149 three-leg wording"
  - "1.2.3 2026-11-18T22:00:00Z: pass-4 correction (item 10) - promotion target path restored to the OD-148 corpus root internal/statusline/testdata/parity/cases/ (fixtures stay with the subject package)"
  - "2026-11-19T00:25:00Z (1.2.4) ADV-P5 remediation D10+D30 — Windows skip removed per OD-171/OD-177 (naive-timestamp cases run on all three legs; BC-5.04.001 OSError rule cited); HYLO_PARITY_FUZZSECONDS named as this contract's harness budget with the 0/unset-fails-on-schedule semantics (D30)"
  - "1.2.5 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) — modified history re-ordered chronologically; no behavioral change"
  - "1.2.6 2026-11-19T17:00:00Z: ADV-P7 remediation D06 + D16 (orchestrator call 8) - the MSVC OSError rule applies at EVERY MSVC call in the local-to-UTC conversion (probes t, u1, u1-86400, u2), not only range-end extremes; new crash id CP-T09 named (Windows MSVC localtime domain OSError on a naive transcript timestamp; append-only, CP-T08 retired); Tier C out-of-domain list gains the OD-166 huge-int usd/api_ms divergence and the D4-EX-2 transcript-overflow extension; Inv 3 restated: entries are path-keyed, generated cases are covered by the PC-3 domain exclusion plus the rider register"
  - "1.2.7 2026-11-21T07:00:00Z: ADV-P11 remediation D06 (orchestrator call 13) - the CP-T09 note states the working domain once and consistently with BC-5.04.001/BC-5.04.002: LEFT-CLOSED [1970-01-02T00:00:00 local wall, year 3001) - under the parity pin TZ=UTC the boundary wall gives probe u1 - 86400 = 0, inside MSVC's domain (re-measured 2026-11-18, CPython 3.11.7), so the boundary instant itself renders"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.04.003: Tier C differential fuzz: nightly all three OSes, one clean run, non-gating, random valid inputs

## Description

Tier C runs once a night on all three OSes (macOS, Linux, Windows — OD-149). A seeded
generator produces random but valid inputs:
stdin, transcripts, metrics replies and cache seeds. Each generated case runs through
both the oracle and Go, and the outputs are compared with the Tier A comparator
(BC-6.03.002). Tier C exists to find hidden Python exception paths and other
divergences the hand-built corpus missed (research P27; risk RK-2). It never blocks a
change. It is part of the P1 exit gate: ONE clean nightly run on all three OSes, with a
30-minute budget per OS (OD-149).

## Preconditions

1. The workflow is a scheduled (`schedule`, once nightly) GitHub Actions workflow,
   separate from `ci.yml`, with a three-leg OS matrix matching `ci.yml` (macOS, Linux,
   Windows — ubuntu-24.04 on the Linux leg). It uses the same oracle setup
   (setup-python CPython 3.11, absolute path, `CI=true`; the Windows leg installs
   CPython the same way, so the differential fuzz runs on all three OSes, per OD-149 —
   ADV-P2-D03 disposition; BC-6.04.001) and the same canary
   (BC-6.01.001, BC-6.01.003).
2. The generator is committed Go code. It reuses the transcript generator
   (design §5.2), so every generated case is synthetic (BC-6.02.001). The nightly driver consumes the harness setting
   `HYLO_PARITY_FUZZSECONDS` — the Tier C differential-fuzz budget in seconds
   (schedule default 1800 = 30 min/OS, OD-149; a reserved harness name per
   BC-2.01.001 PC-6, never a D15 config key; this contract is its owning contract).
   On the nightly schedule a 0/unset budget FAILS the job (positive-coverage guard,
   cicd-setup "parity tier C" row); on a PR-side run the budget may skip via
   `t.Skip`, the job being non-gating.
3. The generator's domain is valid inputs only:
   - well-formed stdin objects, with optional fields present or absent at random;
   - transcripts of valid line shapes;
   - metrics replies in instant-vector form, values including NaN/±Inf;
   - settings inside the Go typed domain;
   - string session ids.
   OS-scoped notes (ADV-P3-D25, as amended by ADV-P5-D10): there is NO Windows skip —
   the harness pins `TZ=UTC` for both binaries on every leg (OD-171/OD-177;
   BC-6.02.003 PC-8, BC-5.04.002 Invariant 2), so generated cases with naive
   timestamps run on all three legs. On Windows the MSVC `localtime_s` OSError rule of
   BC-5.04.001 PC-6 is checked at EVERY MSVC call in the local-to-UTC conversion — the
   probes `t`, `u1`, `u1 - 86400` and `u2` (call 8, pass 7; crash id CP-T09: a naive
   transcript timestamp on or before 1970-01-01, or from year 3001, degrades wherever
   its probe leaves the domain; the working domain is LEFT-CLOSED
   `[1970-01-02T00:00:00 local wall, year 3001)` — under the parity pin `TZ=UTC` the
   boundary wall gives probe `u1 − 86400 = 0`, inside MSVC's domain, so the boundary
   instant itself renders; pass-11 D06, identical to BC-5.04.001/BC-5.04.002) — so the hole is not limited to extreme range-end
   probes; generated present-day values never enter it, and CP-T09's directional leg
   is the committed rider test, not a generated case. The OD-159/160/161
   foreign-shape classes are out of the generator's domain (their
   shapes are seeded by the dedicated directional tests, BC-6.03.004 riders).
   Inputs whose difference is owner-ruled are out of the generator's domain: D4-EX-2
   wrong-shape lines and the D4-EX-2 transcript-overflow extension (pass-7 D16), the
   OD-166 huge-int `usd`/`api_ms` cost-history divergence, D4-EX-3 out-of-domain
   settings, OD-30 numeric sids, and
   D4-EX-1/OD-76 process probing (`proc_start` is always seeded). IN domain since
   OD-155 (ADV-P3-D04/D25): the `--subagent` invocation family — generated cases
   exercise `main_subagent` with agent-panel stdin shapes, run under the same
   invocation rule as the goldens (BC-6.03.001) with the non-NDJSON
   config-error/output surfaces staying out of Tier C (D4-EX-3 class).

## Postconditions

1. **Seeded and reproducible.**
   - Each nightly run derives a 64-bit seed (default: from the UTC date) and prints it.
   - Given the same seed and commit, the generator emits the identical case sequence.
   - Running locally with `-tierc.seed=<seed>` reproduces any night.
2. **Volume.** Each night each OS leg runs as many cases as fit in a fixed time budget, a harness
   setting with default 30 minutes per OS (OD-149). At about 30-60 ms Python start per run, that is
   thousands of cases (research Q3c). The count is reported.
3. **Comparison.** Every generated case, including multi-step generated sequences, is
   compared per step by the BC-6.03.002 comparator, with temp names filtered
   (BC-6.03.003).
4. **Divergence artifact.** For each divergent case the run uploads a materialized
   case directory as a workflow artifact, in the BC-6.02.003 case model with seed and
   index. A maintainer can promote it into `internal/statusline/testdata/parity/cases/` as a
   regression case. It is synthetic by construction.
5. **Non-gating.**
   - A divergence marks the nightly run failed and visible.
   - It never blocks pushes or pull requests: it is not a required status check and
     not part of `ci.yml`.
6. **Exit criterion input.** The run summary records, per OS leg, `clean` (0 divergences) or
   `divergent: <count>`. Per OD-149 the P1 exit gate is satisfied by ONE clean nightly
   run on all three OSes with the 30-minute per-OS budget; no multi-night streak is
   required (this discharges the earlier "N consecutive nights" open question).

## Invariants

1. Tier C uses the same oracle runner, env builder, clock shim and comparator as
   Tier A. There is no separate, looser comparison.
2. Generated inputs never include real data.
3. Exclusion machinery (BC-6.03.004): exclusion entries are keyed by COMMITTED case
   path, so a generated case never carries one and no path-keyed entry can match a
   generated case. Instead, the owner-ruled difference shapes stay OUT of the
   generator's domain by construction (the PC-3 list), and every closed-set id is
   backed by a dedicated directional rider test (BC-6.03.004) — that rider register,
   not the path-keyed list, is what covers generated shapes. Any difference in a
   generated case outside the ruled shapes counts as a divergence.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Generated stdin triggers an uncaught Python exception (oracle prints `statusline degraded`) and Go renders a row | Divergence reported with the seed; artifact uploaded (P27 class) |
| EC-002 | Night with 0 divergences | Summary `clean`; satisfies the OD-149 exit gate (ONE clean nightly run on all three OSes — no N-night streak, ADV-P2-D04) |
| EC-003 | Oracle canary fails on the nightly runner | Run fails before generating cases; the night does not count as clean |
| EC-004 | Generator emits a numeric `session_id` (bug in the domain filter) | The comparator reports an OD-30-class difference without an entry. That is a generator bug: fixed in the generator, not by adding an exclusion |
| EC-005 | Time budget reached mid-sequence | The partial sequence is discarded, not counted; the case count reflects completed cases |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Nightly run, seed `0x1d2c…` (printed), 4,000 cases, no differences | Summary `clean`, count 4000, seed printed | happy-path |
| Local re-run with `-tierc.seed=<that seed>` | Identical first N cases (verified by a hash of the generated case bytes) | edge-case |
| Case where Go prints `▲31/▼4` and the oracle prints `statusline degraded` | Divergence, artifact `tierc-<seed>-<index>/` uploaded; nightly marked failed; no PR blocked | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-011 | The generator is deterministic for a given seed and commit | table test hashing generated cases |
| VP-011 | The generator never emits inputs in an owner-ruled difference class | Go property test (testing/quick) over the generator's domain filter |

## Traceability

| Field | Value |
|-------|-------|
| Source | design §5.1 Tier C (random valid stdin/transcripts/metrics, both sides, diff), §5.5, §7.2 RK-2; research Q3c (thousands of cases per nightly job, not `go test -fuzz`), P27; OD-104 (oracle); OD-117 target (1); per OD-149 the nightly Tier C differential runs on all THREE OS legs and is not gating; the "Linux nightly / owner-picked nights / 3 nights" wording is superseded (ADV-P3-D31) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012, DI-008 |
| Architecture Module | `.github/workflows/tierc.yml`; harness Tier C generator (BC-COMPONENT-MAP: internal/parity/fuzzdiff.go (nightly Tier C) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.03.002 — depends on: shared comparator
- BC-6.02.003 — composes with: divergences materialize as case directories
- BC-6.04.001 — related to: per-change CI, which Tier C is deliberately not part of
- BC-6.01.003 — depends on: clock shim and canary on the nightly runner

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/fuzzdiff.go (nightly Tier C) (Tier C generator and nightly workflow) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

> Names provisional — architect (OD-145): harness flag names, the timing method, proposed
> test names and seed paths in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

- VP-011 — generator determinism and domain properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/fuzzdiff.go (nightly Tier C) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
