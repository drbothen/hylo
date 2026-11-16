---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-08-build-ci-release.md, behavioral-contracts/ss-06/BC-6.04.001.md, prd-supplements/nfr-catalog.md]
input-hash: "00083a4"
traces_to: prd.md
source_bc: BC-6.04.001
module: CI workflow (ARCH-08), in-tree corpus test
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-037: Three-OS CI matrix per change; race-clean Linux/macOS

## Property Statement

Every change runs the full matrix — ubuntu-24.04, macos-15 (arm64), windows-2025 — on
Go 1.26.x with `CGO_ENABLED=0` builds, `-race` on Linux and macOS legs, Tier A corpus
(interpreter path from setup-python, OD-108), Tier B goldens (Windows runs Tier B
without Python), gitleaks + category scan, and the printed timing report. The resolved
Python patch version is recorded in Tier B golden metadata (RK-4). Non-zero harness
exits never occur inside `hylo` (E-HAR-001 is the harness process).

## Source Contract

- **Primary BC:** BC-6.04.001 — CI matrix: ubuntu-24.04 / macos-15 arm64 /
  windows-2025; Go 1.26.x leg; -race; gitleaks.
- **Partial coverage:** NFR-004 (three-OS CI green for every change); RK-4 (golden
  metadata); OD-108 (absolute interpreter path from setup-python).
- **Invariant verified:** D5 ordering (cross-platform before generalization); the
  process-invariant form of every "on every OS" claim elsewhere in this index
  (VP-010/014/032/033 observe their OS legs here).

## Property Class and Verification Method

- **Class:** invariant (process invariant — a property of the workflow, not the
  binary).
- **Method:** CI leg observation — workflow conformance is testable-only (ARCH-08); the
  in-tree parts (corpus hygiene test, timing printer, golden metadata recorder) are
  table-tested.
- **Honesty:** testable-only by observation; the weakest enforcement form, honestly a
  process gate.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Matrix observation | GitHub Actions workflow | process | every change, three OSes |

## Proof Harness Skeleton

```yaml
# ARCH-08 workflow sketch; no in-tree test object — conformance is observational.
matrix: [ubuntu-24.04, macos-15, windows-2025]
steps: [lint, test(-race on linux/mac), setup-python-3.11 → HYLO_PARITY_PYTHON,
        tierA, tierB, gitleaks, timing-report]
```

## Named Tests (OD-145 table where applicable)

Not applicable (workflow object); in-tree hooks: `TestCorpusHygiene` (VP-035), timing
printer (VP-036), golden-metadata recorder (VP-010).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Workflow config | static |
| Proof complexity | N/A | observation |
| Tool support | Full | GitHub Actions |
| Estimated proof time | Continuous | every push |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
