---
document_type: verification-property
level: L4
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-18T23:45:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.001.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "8f19607"
traces_to: prd.md
source_bc: BC-1.01.001
bcs: [BC-1.01.001, BC-1.07.008]
module: internal/statusline (guard), cmd/hylo
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-18: BC-1.07.008 added to bcs — shared-guard write-failure leg (BC-1.07.008's Verification Properties table anchors VP-003)", "1.3 2026-11-18T14:12:00Z: ADV-P4 fix (A2-14) — skeleton test renamed to the canonical rider name TestCPX03_WriteFailureExit0 fixed by BC-1.01.001's traceability register and quoted by VP-012", "1.4 2026-11-18T23:45:00Z: ADV-P5 fix (A2-12) — the harness now OBSERVES the degraded write: counting failing writer, call count ≥ 1 on both the main and the --subagent entry (BC-1.07.008 write-failure leg row added) — an implementation that never writes fails the test"]
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
- **Shared-guard leg:** BC-1.07.008 (`--subagent` degraded path) anchors VP-003 for its
  write-failure leg — every fault routed to the subagent renderer ends in the same 29
  degraded bytes, exit 0.
- **Invariant verified:** DI-008 (exit 0 even when the degraded write fails — owner
  ruling OD-136); DI-012 (difference rides a named, tested exclusion).

## Property Class and Verification Method

- **Class:** safety.
- **Method:** unit/table test — a counting failing-stdout writer injected into `Main`
  (main entry and `--subagent` entry, BC-1.07.008's write-failure leg); assert
  exit == 0, that the degraded write was ATTEMPTED (writer call count ≥ 1 — an
  implementation that never writes must fail this test), and that the error is not
  propagated to the exit path.
- **Honesty:** testable-only; trivial fault injection at the writer seam.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test | Go test, `internal/statusline` | yes — single fault site | stdout closed / write error at step 8 |

## Proof Harness Skeleton

```go
func TestCPX03_WriteFailureExit0(t *testing.T) { // canonical rider name, BC-1.01.001 (A2-14)
    for _, tc := range []struct{ name, entry string }{
        {"main entry", "main"},                  // BC-1.01.001 EC-005
        {"--subagent entry", "subagent"},        // BC-1.07.008 write-failure leg (A2-12)
    } {
        w := &countingFailingWriter{}            // fails every Write, COUNTS attempts
        exit := runStatuslineWith_stdoutWriter(w, degradedStdin, tc.entry)
        if exit != 0 { t.Fatalf("%s: exit = %d, want 0 (OD-136)", tc.name, exit) }
        if w.Writes() == 0 { // the degraded write must have been attempted:
            t.Fatalf("%s: no write attempt observed — an implementation that "+ // A2-12
                "never writes must fail here", tc.name)
        }
    }
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
