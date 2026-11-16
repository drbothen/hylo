---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.03.001.md, owner-decisions-log-2026-11-14.md]
input-hash: "2ac3fc3"
traces_to: prd.md
source_bc: BC-6.03.001
module: internal/parity
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

# VP-010: Tier B committed goldens — Python-written, Go matches on every OS

## Property Statement

Every committed Tier B golden under `internal/statusline/testdata/goldens/` is written
by the Python oracle (never Go) — recorded on Linux with `*.windows.golden` variants
for OS-dependent cases — and the Go port's output matches the applicable golden
byte-for-byte on every CI OS without Python installed. Golden metadata records the
resolved Python patch version (RK-4).

## Source Contract

- **Primary BC:** BC-6.03.001 — Row goldens A/B/C (Tier B, Python-written, OS-specific
  variants).
- **Partial coverage:** BC-6.04.001 (Windows leg runs Tier B without Python).
- **Invariant verified:** DI-012 (the referee writes the expected bytes, keeping the
  refereed side from self-certifying); AD-13 (fixture co-location).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** golden/parity tier — `TestParityTierB_Goldens` over committed goldens;
  `-update` writes Python output and fails if the interpreter is unset (OD-104).
- **Honesty:** testable-only; OS coverage follows the CI matrix (VP-037).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Golden test | `go test ./internal/parity -run TestParityTierB_Goldens` | yes — committed goldens | all row goldens, per-OS variant selection |

## Proof Harness Skeleton

```go
func TestParityTierB_Goldens(t *testing.T) {
    for _, g := range LoadGoldens("internal/statusline/testdata/goldens") {
        out := RunGoPortForCase(g.Case) // variant-selects *.windows.golden on windows
        if !bytes.Equal(out, g.Bytes) { t.Fatalf("%s: bytes differ", g.Case) }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestParityTierB_Goldens`; flag `-update`; metadata records the setup-python patch
version (RK-4).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Committed goldens | fixed |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | variant bookkeeping is the cost |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
