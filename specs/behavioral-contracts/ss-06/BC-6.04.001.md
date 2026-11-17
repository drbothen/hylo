---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T13:05:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
  - CLAUDE.md
input-hash: "ea5a0e4"
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
modified: ["1.2.1 2026-11-17: VP citation reconciliation — VP-010 added"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.04.001: CI matrix: ubuntu-24.04 / macos-15 arm64 / windows-2025; Go 1.26.x leg; -race; gitleaks

## Description

Every change (each push and pull request) runs the full check suite on three pinned
operating system images, plus one extra Linux leg on the Go 1.26.x floor:

- ubuntu-24.04;
- macos-15 (arm64), which detects floating-point contraction (FMA) mismatches;
- windows-2025.

On all three OSes the parity tiers A and B run against a CPython 3.11 oracle, installed
by setup-python and passed by absolute path. The race detector runs on Linux and macOS.
gitleaks scans the full history. The workflow is gating: any red leg blocks the change.

## Preconditions

1. The workflow is `.github/workflows/ci.yml`, triggered on `push` and `pull_request`.
   Tier C runs separately (BC-6.04.003).
2. `go.mod` declares `go 1.26.0` with a `toolchain` line (design §4 S0).

## Postconditions

1. **OS legs.** `runs-on` uses exactly `ubuntu-24.04`, `macos-15` and `windows-2025`.
   Floating labels (`ubuntu-latest`, `macos-latest`, `windows-latest`) are never used,
   because they move to new images without a code change.
2. **Go versions.** Each OS leg uses `actions/setup-go` with `go-version-file: go.mod`.
   One additional leg on `ubuntu-24.04` uses `go-version: 1.26.x`, the floor declared
   by `go.mod`.
3. **Steps per leg, in order:**
   1. `gofmt -l .`, which must print nothing;
   2. `go vet ./...`;
   3. `go test ./...`, which includes the Tier B goldens (BC-6.03.001), the exclusion
      table tests (BC-6.03.004) and the corpus hygiene test (BC-6.02.001). Linux and
      macOS add `-race`; Windows runs without it.
   4. the parity job: `actions/setup-python` installs CPython 3.11. Its reported
      absolute interpreter path is exported as `HYLO_PARITY_PYTHON` (OD-108), with
      `CI=true`, so Tier A cannot skip (BC-6.01.001). The clock-shim canary runs first
      (BC-6.01.003).
4. **gitleaks.** One job checks out with `fetch-depth: 0` and runs a pinned,
   checksum-verified gitleaks binary over the whole history with
   `--log-opts="--all"`. This matches the CLAUDE.md pre-push command. A finding fails
   the workflow.
5. **Gating.** The workflow passes only if every leg and job passes. No leg is
   `continue-on-error`.
6. **Python patch recorded.** Each OS leg prints the resolved CPython patch version
   from the BC-6.01.001 probe, so a patch drift is visible in the logs (RK-4).

## Invariants

1. CI covers all three OSes for every change (D5; CLAUDE.md "CI runs on all three OSes
   for every change").
2. The interpreter path given to the harness is always absolute; `python` from `PATH`
   is never used (OD-104/OD-108).
3. No CI step writes goldens. `-update` is never passed in CI.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | A float expression in Go is fused (FMA) on arm64 and shifts a heat colour | macos-15 leg fails Tier A/B; the Linux amd64 legs may pass. The arm64 leg is the gate (PR-15) |
| EC-002 | Windows leg with `-race` | Not run; Windows runs plain `go test` |
| EC-003 | setup-python yields 3.11.x where x differs from the golden metadata | Tier B still compares against committed (Python-written) goldens; the patch is printed; a resulting diff fails the leg and is reviewed (RK-4) |
| EC-004 | gitleaks finds a secret in an old commit | Workflow fails (full-history scan) |
| EC-005 | `gofmt -l .` lists a file | Leg fails at step 1 |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| PR with a passing change | 4 test legs (3 OS + Go 1.26.x) green, gitleaks green → workflow green | happy-path |
| Change that breaks a golden only on Windows (e.g. root-path label) | windows-2025 leg red → workflow red | edge-case |
| Workflow edited to use `HYLO_PARITY_PYTHON=python` | Tier A fails on every leg (BC-6.01.001 absolute-path rule) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-037, VP-035 | The workflow file pins exactly the three OS labels, includes the Go 1.26.x leg, `-race` on Linux/macOS, and the gitleaks full-history step | manual review + a repository test that parses `ci.yml` |
| VP-037, VP-035 | Every CI parity run uses an absolute interpreter path with `CI=true` | CI log check + BC-6.01.001 tests |
| VP-010 | Go output matches the committed Tier B goldens byte-for-byte on every CI OS — the property the three-OS matrix (windows-2025 golden leg) exists to enforce | `TestParityTierB_Goldens` on all CI legs |

## Traceability

| Field | Value |
|-------|-------|
| Source | design §5.5 (ubuntu-24.04, macos-15 arm64 PR-15 FMA detector, windows-2025 for every change; Go 1.26.x leg; setup-python CPython 3.11 on all three OSes; `-race` on Linux and macOS; Tier C nightly not gating; gitleaks `--log-opts="--all"`); CLAUDE.md (CI on all three OSes for every change; pre-push gitleaks command); D5; OD-104, OD-108; research Q7 (pinned OS labels, `-race` on Linux/macOS only, gitleaks binary with `fetch-depth: 0`) |
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
