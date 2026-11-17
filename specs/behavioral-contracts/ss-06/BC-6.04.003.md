---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
input-hash: "31c4e22"
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

# Behavioral Contract BC-6.04.003: Tier C differential fuzz: nightly Linux, non-gating, random valid inputs to both sides

## Description

Tier C runs once a night on Linux. A seeded generator produces random but valid inputs:
stdin, transcripts, metrics replies and cache seeds. Each generated case runs through
both the oracle and Go, and the outputs are compared with the Tier A comparator
(BC-6.03.002). Tier C exists to find hidden Python exception paths and other
divergences the hand-built corpus missed (research P27; risk RK-2). It never blocks a
change. It is part of the P1 exit gate: it must run clean for an owner-picked number of
consecutive nights.

## Preconditions

1. The workflow is a scheduled (`schedule`, once nightly) GitHub Actions workflow,
   separate from `ci.yml`, on `ubuntu-24.04`. It uses the same oracle setup
   (setup-python CPython 3.11, absolute path, `CI=true`) and the same canary
   (BC-6.01.001, BC-6.01.003).
2. The generator is committed Go code. It reuses the transcript generator
   (design §5.2), so every generated case is synthetic (BC-6.02.001).
3. The generator's domain is valid inputs only:
   - well-formed stdin objects, with optional fields present or absent at random;
   - transcripts of valid line shapes;
   - metrics replies in instant-vector form, values including NaN/±Inf;
   - settings inside the Go typed domain;
   - string session ids.
   Inputs whose difference is owner-ruled are out of the generator's domain: D4-EX-2
   wrong-shape lines, D4-EX-3 out-of-domain settings, OD-30 numeric sids, and
   D4-EX-1/OD-76 process probing (`proc_start` is always seeded).

## Postconditions

1. **Seeded and reproducible.**
   - Each nightly run derives a 64-bit seed (default: from the UTC date) and prints it.
   - Given the same seed and commit, the generator emits the identical case sequence.
   - Running locally with `-tierc.seed=<seed>` reproduces any night.
2. **Volume.** Each night runs as many cases as fit in a fixed time budget, a harness
   setting with default 30 minutes. At about 30-60 ms Python start per run, that is
   thousands of cases (research Q3c). The count is reported.
3. **Comparison.** Every generated case, including multi-step generated sequences, is
   compared per step by the BC-6.03.002 comparator, with temp names filtered
   (BC-6.03.003).
4. **Divergence artifact.** For each divergent case the run uploads a materialized
   case directory as a workflow artifact, in the BC-6.02.003 case model with seed and
   index. A maintainer can promote it into `internal/statusline/testdata/cases/` as a
   regression case. It is synthetic by construction.
5. **Non-gating.**
   - A divergence marks the nightly run failed and visible.
   - It never blocks pushes or pull requests: it is not a required status check and
     not part of `ci.yml`.
6. **Exit criterion input.** The run summary records `clean` (0 divergences) or
   `divergent: <count>`. P1 is declared done only after Tier C has been `clean` for N
   consecutive nights. N is picked by the owner; the research proposes 3 (open
   question O5, not decided here).

## Invariants

1. Tier C uses the same oracle runner, env builder, clock shim and comparator as
   Tier A. There is no separate, looser comparison.
2. Generated inputs never include real data.
3. The exclusion list (BC-6.03.004) still applies if a generated case happens to hit a
   listed case shape. Otherwise every difference counts as a divergence.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Generated stdin triggers an uncaught Python exception (oracle prints `statusline degraded`) and Go renders a row | Divergence reported with the seed; artifact uploaded (P27 class) |
| EC-002 | Night with 0 divergences | Summary `clean`; counts toward the N-night exit criterion |
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
| VP-011 | The generator never emits inputs in an owner-ruled difference class | proptest over the generator's domain filter |

## Traceability

| Field | Value |
|-------|-------|
| Source | design §5.1 Tier C (random valid stdin/transcripts/metrics, both sides, diff; Linux nightly; not gating; run clean for an owner-picked number of nights before P1 is declared done), §5.5 (Tier C nightly on Linux, not gating), §7.2 RK-2; research Q3c (thousands of cases per nightly job, not `go test -fuzz`), P27, open question O5 (proposal 3 nights); OD-104 (oracle); OD-117 target (1) |
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
