---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.001.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "09335de"
traces_to: prd.md
source_bc: BC-1.01.001
module: internal/statusline (guard), cmd/hylo
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

# VP-003: Degraded-line write failure still exits 0 (named exclusion `cp-x03`)

## Property Statement

When the write of the 29-byte degraded line itself fails (legacy CP-X03, e.g. stdout
closed), Go swallows the write error and the process exit code is still 0. This is a
ruled byte-behaviour difference from legacy, carried as named exclusion `cp-x03` in the
OD-105 closed set with its own table test.

## Source Contract

- **Primary BC:** BC-1.01.001 — Guard prints the 29-byte degraded line and exits 0
  (EC-005: degraded-write failure).
- **Invariant verified:** DI-008 (exit 0 even when the degraded write fails — owner
  ruling OD-136); DI-012 (difference rides a named, tested exclusion).

## Property Class and Verification Method

- **Class:** safety.
- **Method:** unit/table test — a failing-stdout writer injected into `Main`; assert
  exit == 0 and that the error is not propagated to the exit path.
- **Honesty:** testable-only; trivial fault injection at the writer seam.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test | Go test, `internal/statusline` | yes — single fault site | stdout closed / write error at step 8 |

## Proof Harness Skeleton

```go
func TestCpX03_DegradedWriteFailureExitZero(t *testing.T) {
    exit := runStatuslineWith_stdoutWriter(failingWriter{}, degradedStdin)
    if exit != 0 { t.Fatalf("exit = %d, want 0 (OD-136)", exit) }
}
```

## Named Tests (OD-145 table where applicable)

Exclusion id `cp-x03` is in the ARCH-07 closed set; the parity-case family `cfgerr`/
`cps01..cps17` neighbours do not cover it — its table test lives with the guard
(`internal/statusline`), and `TestParityExclusions_ClosedSet` (VP-012) verifies the
exclusion entry has this test.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Single fault site | failing writer |
| Proof complexity | N/A | |
| Tool support | Full | io.Writer seam |
| Estimated proof time | Minutes | |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
