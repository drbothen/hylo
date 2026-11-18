---
document_type: behavioral-contract
level: L3
version: "1.2.9"
status: draft
producer: product-owner
timestamp: 2026-11-21T09:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
  - CLAUDE.md
input-hash: "fe153e7"
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
  - "2026-11-17T00:00:00Z (1.2.1): VP citation reconciliation — VP-010 added"
  - "2026-11-18T00:00:00Z (1.2.2): ADV-P4 remediation D08 - setup-python reordered BEFORE go test (Tier A cannot skip under CI=true; aligns with ARCH-08)"
  - "2026-11-18T12:00:00Z (1.2.3): pass-4 sync-check SC-08 — converted the mixed flow/block modified history to uniform block style (the mix broke YAML parsing); no behavioral change"
  - "2026-11-19T03:35:00Z (1.2.4): ADV-P6 remediation D16/OD-185 — PC-3.3 gains the Tier A oracle self-check: the harness measures the resolved oracle's JSON depth boundaries and unicodedata.unidata_version at start and fails closed on mismatch (constants measured on 3.11.7; OD-185), printing the resolved patch; setup-python keeps installing floating 3.11.x"
  - "2026-11-21T06:00:00Z (1.2.5): ADV-P10 remediation D09 (orchestrator call 8) — the floor leg installs exactly go-version: 1.26.0 (the go.mod floor), not 1.26.x: with the toolchain line a floating 1.26.x could resolve to the same patch as the default legs, leaving the floor never tested"
  - "2026-11-21T07:00:00Z (1.2.6): ADV-P11 remediation D03 (H1 sync after the ADV-P10-D09 pin) + D04 (orchestrator call 16) + A07 (call 8) — H1/Description/CTV/VP-row now say the Go 1.26.0 FLOOR leg (the body pinned exactly 1.26.0 in 1.2.5; index titles synced); PC-3 gains the lint-job steps ARCH-08 runs (pinned staticcheck, govulncheck as a required check); PC-3's test step references BC-6.01.001 PC-7's oracle build tag for the plain/oracle test-step split"
  - "2026-11-21T09:00:00Z (1.2.7): pass-11 residual — PC-3 step 6 respelled to the ORACLE_TESTS -run/-skip pattern (BC-6.01.001 PC-7; ARCH-07 OD-145 binding), removing the minted `oracle` build tag; PC-3 item 4 and the Description state the two-ref scan `--log-opts=\"main factory-artifacts\"` with the scanned-commit count compared against `git rev-list --count main factory-artifacts` (ARCH-08 hygiene bullet); EC-004 respelled 'old commit of either ref'; the VP-table row says the gitleaks two-ref scan step"
  - "2026-11-22T00:00:00Z (1.2.8): ADV-P12 remediation A02/D04/D16 (orchestrator call 1) + A06 (call 5) + D15 — PC-4 and the Description respelled to the FULL-HISTORY scan `--log-opts=\"--all\"` after checkout with fetch-depth: 0 (--all includes HEAD, so a PR run scans the PR head and every fetched ref; scanned-commit count asserted equal to `git rev-list --count --all`; matches the CLAUDE.md pre-push command; supersedes the two-ref scan of 1.2.7); EC-004 and the VP-table row follow; PC-3 restructured per call 5: gofmt -l and govulncheck run ONCE in the ubuntu lint job, go vet and staticcheck on every OS leg, setup-python ONLY in the ORACLE_TESTS jobs (Tier A, timing, nightly fuzz; each -runs its own member(s) and prints the resolved CPython patch, PC-6), plain legs install none; D15: the Tier B goldens / exclusion-table / corpus-hygiene sentence now attaches to the plain -skip step; Source row: Go 1.26.0 floor leg (D16)"
  - "2026-11-23T00:00:00Z (1.2.9): ADV-P13 remediation D06 (orchestrator call 5) + call 6 — Description respelled: Tier B runs in the plain test legs ONLY (no separate Tier B job; the plain legs own the tier-b census), and the Tier A job and the timing job EACH run on all three OSes with setup-python (CPython 3.11) on every leg of each, printing the resolved patch (PC-3 step 4, PC-6); PC-3 step 5 restructured per call 6: the lint job runs gofmt -l only and is required, govulncheck is its OWN job that runs and reports on every change and becomes a required check with the go.mod toolchain line (ARCH-08 ordering rule); EC-001 and EC-005 follow (Tier A job matrix named; gofmt fails in the lint job, not at step 1); CTV row tightened"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.04.001: CI matrix: ubuntu-24.04 / macos-15 arm64 / windows-2025; Go 1.26.0 floor leg; -race; gitleaks

## Description

Every change (each push and pull request) runs the full check suite on three pinned
operating system images, plus one extra Linux leg on the Go 1.26.0 floor:

- ubuntu-24.04;
- macos-15 (arm64), which detects floating-point contraction (FMA) mismatches;
- windows-2025.

On all three OSes the plain test legs install no interpreter; Tier B runs in those
plain legs only — no separate Tier B job — and the plain legs own the
`tier-b: N goldens compared` census (PC-3 step 3). Tier A runs in the dedicated
ORACLE_TESTS jobs: the Tier A job and the timing job EACH run on all three OSes, and
every leg of each installs the CPython 3.11 oracle by setup-python, prints the
resolved patch and passes it by absolute path (PC-3 step 4, PC-6; pass-13
orchestrator call 5). The race
detector runs on Linux and macOS. gitleaks scans the full history — every fetched ref
plus HEAD — with `--log-opts="--all"` (ARCH-08 hygiene bullet; pass-12 call 1), so a
pull request's own commits are scanned before merge. The workflow is gating: any red leg blocks the change.

## Preconditions

1. The workflow is `.github/workflows/ci.yml`, triggered on `push` and `pull_request`.
   Tier C runs separately (BC-6.04.003).
2. `go.mod` declares `go 1.26.0` with a `toolchain` line (design §4 S0).

## Postconditions

1. **OS legs.** `runs-on` uses exactly `ubuntu-24.04`, `macos-15` and `windows-2025`.
   Floating labels (`ubuntu-latest`, `macos-latest`, `windows-latest`) are never used,
   because they move to new images without a code change.
2. **Go versions.** Each OS leg uses `actions/setup-go` with `go-version-file: go.mod`.
   One additional leg on `ubuntu-24.04` uses `go-version: 1.26.0` — exactly the `go 1.26.0`
   floor `go.mod` declares, NOT `1.26.x` (which would install the newest 1.26 patch and,
   with the `toolchain` line of Pre-2, could resolve to the same patch as the default
   legs, leaving the floor never tested — ADV-P10-D09, orchestrator call 8).
3. **Steps per leg, in order (pass-12 call 5 structure):**
   1. `go vet ./...` on every OS leg (per-OS build tags, P18);
   2. `staticcheck ./...` on every OS leg, at the version ARCH-08's lint job pins
      (pass-11 D04: the lint job's checker is part of the check suite this BC drives a
      test of);
   3. `go test ./...`, split by the ORACLE_TESTS pattern (BC-6.01.001 PC-7; the
      ARCH-07 OD-145 binding; pass-12 call 6): the plain test
      step, the coverage job and the release job pass `-skip "$ORACLE_TESTS"` and
      exclude exactly that set; this plain run
      includes the Tier B goldens (BC-6.03.001), the exclusion
      table tests (BC-6.03.004) and the corpus hygiene test (BC-6.02.001). Linux and
      macOS add `-race`; Windows runs without it.
   4. The ORACLE_TESTS jobs are separate from the plain legs: the dedicated Tier A
      job and the timing job (BC-6.04.002) EACH run on all three OSes
      (ubuntu-24.04 / macos-15 / windows-2025; pass-13 orchestrator call 5), and the
      nightly fuzz job runs its own member(s) nightly; every Tier A and timing leg
      installs CPython 3.11 by `actions/setup-python` BEFORE its `go test` and prints
      the resolved patch, and each runs its
      own member(s) with `-run`. In the Tier A job the interpreter's reported absolute
      path is exported as `HYLO_PARITY_PYTHON` (OD-108), with `CI=true`, so Tier A
      cannot skip (BC-6.01.001 PC-6) — setup-python must precede
      `go test ./...` or the job fails (ADV-P4-D08, aligning this BC with ARCH-08's
      corrected order). The clock-shim canary runs first (BC-6.01.003), then the
      OD-185 oracle self-check: the harness measures the resolved oracle's JSON depth
      boundaries and `unicodedata.unidata_version` (constants measured on 3.11.7,
        floating 3.11.x install) and fails closed on any mismatch, printing the
      resolved version (BC-6.01.001 PC-4).
   5. `gofmt -l .` (which must print nothing) runs ONCE, in the ubuntu lint job — not
      per leg — and the lint job is required (ARCH-08; pass-13 orchestrator call 6).
      `govulncheck ./...` is its OWN job, separate from lint: it runs and reports on
      every change, and it becomes a required check in the same change that adds
      go.mod's `toolchain` line (the ARCH-08 ordering rule; a finding blocks the
      change like any red leg). The branch-protection list names exactly the contexts
      the jobs emit (architect's list in cicd-setup).
4. **gitleaks.** One job checks out with `fetch-depth: 0` and runs a pinned,
   checksum-verified gitleaks binary over the full history —
   `--log-opts="--all"` (ARCH-08 hygiene bullet; pass-12 call 1): `--all` includes
   HEAD, so on a `pull_request` run the PR's own commits and every fetched ref
   (factory-artifacts included) are scanned before merge; the former two-ref scan
   (`--log-opts="main factory-artifacts"`) missed a PR's own commits and depended on
   bare branch names that checkout does not create. Positive coverage: the
   scanned-commit count is asserted equal to `git rev-list --count --all` (the same
   rev set by construction). The command matches the CLAUDE.md pre-push command. A
   finding fails the workflow.
5. **Gating.** The workflow passes only if every leg and job passes. No leg is
   `continue-on-error`.
6. **Python patch recorded.** Each job that installs an interpreter (the ORACLE_TESTS
   jobs of PC-3 step 4) prints the resolved CPython patch version
   from the BC-6.01.001 probe, so a patch drift is visible in the logs (RK-4) — every
   leg of the Tier A job and the timing job included (all three OSes each; pass-13
   orchestrator call 5); the
   plain test legs install no interpreter and print none (pass-12 call 5).

## Invariants

1. CI covers all three OSes for every change (D5; CLAUDE.md "CI runs on all three OSes
   for every change").
2. The interpreter path given to the harness is always absolute; `python` from `PATH`
   is never used (OD-104/OD-108).
3. No CI step writes goldens. `-update` is never passed in CI.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | A float expression in Go is fused (FMA) on arm64 and shifts a heat colour | macos-15 plain leg fails Tier B and the macos-15 leg of the Tier A job fails Tier A (the Tier A job runs on all three OSes, PC-3 step 4); the Linux amd64 legs may pass. The arm64 legs are the gate (PR-15) |
| EC-002 | Windows leg with `-race` | Not run; Windows runs plain `go test` |
| EC-003 | setup-python yields 3.11.x where x differs from the golden metadata | Tier B still compares against committed (Python-written) goldens; the patch is printed; a resulting diff fails the leg and is reviewed (RK-4) |
| EC-004 | gitleaks finds a secret in an old commit reachable from any fetched ref or the PR head | Workflow fails (the `--all` scan covers every fetched ref plus HEAD) |
| EC-005 | `gofmt -l .` lists a file | The ubuntu lint job fails (PC-3 step 5; gofmt runs there, not at step 1) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| PR with a passing change | 4 test legs (3 OS + Go 1.26.0 floor) green, gitleaks green → workflow green | happy-path |
| Change that breaks a golden only on Windows (e.g. root-path label) | windows-2025 leg red → workflow red | edge-case |
| Workflow edited to use `HYLO_PARITY_PYTHON=python` | Tier A fails on every leg of the Tier A job — all three OSes (BC-6.01.001 absolute-path rule) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-037, VP-035 | The workflow file pins exactly the three OS labels, includes the Go 1.26.0 floor leg, `-race` on Linux/macOS, and the gitleaks full-history (`--all`) scan step | manual review + a repository test that parses `ci.yml` |
| VP-037, VP-035 | Every CI parity run uses an absolute interpreter path with `CI=true` | CI log check + BC-6.01.001 tests |
| VP-010 | Go output matches the committed Tier B goldens byte-for-byte on every CI OS — the property the three-OS matrix (windows-2025 golden leg) exists to enforce | `TestParityTierB_Goldens` on all CI legs |

## Traceability

| Field | Value |
|-------|-------|
| Source | design §5.5 (ubuntu-24.04, macos-15 arm64 PR-15 FMA detector, windows-2025 for every change; Go 1.26.0 floor leg, aligned with the body's PC-2 pin — pass-12 D16; setup-python CPython 3.11 in the ORACLE_TESTS jobs, pass-12 call 5; `-race` on Linux and macOS; Tier C nightly not gating; gitleaks `--log-opts="--all"`, pass-12 call 1); CLAUDE.md (CI on all three OSes for every change; pre-push gitleaks command); D5; OD-104, OD-108; research Q7 (pinned OS labels, `-race` on Linux/macOS only, gitleaks binary with `fetch-depth: 0`) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `.github/workflows/ci.yml` (BC-COMPONENT-MAP: CI matrix (ARCH-08 workflow) + internal/parity/ci.go — ARCH-07, ARCH-08) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.01.001 — depends on: absolute interpreter path and `CI=true` fail-not-skip rule
- BC-6.03.001 — composes with: Tier B goldens run on every leg
- BC-6.04.002 — related to: per-OS timing report produced by the same matrix
- BC-6.04.003 — related to: Tier C runs in a separate nightly workflow

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — CI matrix (ARCH-08 workflow) + internal/parity/ci.go (CI workflow) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md), ARCH-08 (ARCH-08-build-ci-release.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- VP-037, VP-035 — CI matrix properties above; VP-010 — Tier B golden parity on every leg

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/ci.go (CI matrix, ARCH-08 workflow) - ARCH-07, ARCH-08); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
