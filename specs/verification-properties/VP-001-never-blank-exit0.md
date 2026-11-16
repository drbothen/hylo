---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-00-overview.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.001.md, domain-spec/invariants.md, prd-supplements/nfr-catalog.md, prd-supplements/error-taxonomy.md, owner-decisions-log-2026-11-14.md]
input-hash: "5a738fb"
traces_to: prd.md
source_bc: BC-1.01.001
bcs: [BC-1.01.001, BC-1.01.002, BC-1.02.020, BC-1.02.026, BC-1.02.027, BC-1.04.014, BC-1.04.015, BC-1.04.016, BC-1.06.001]
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

# VP-001: Never-blank, exit-0 rendering under every fault trigger

## Property Statement

For every fault trigger in the closed error taxonomy — CP-S01..S17 (typed widget/parser
degrades), CP-T01..T07 (transcript faults), CP-N01/N02 (NaN/inf crash paths), and
untyped panics — one refresh of `hylo statusline` produces at least one stdout byte and
terminates with exit code 0. No fault class exists that yields blank output or a
non-zero statusline exit.

## Source Contract

- **Primary BC:** BC-1.01.001 — Guard prints the 29-byte degraded line and exits 0.
- **Partial coverage:** BC-1.01.002 (invalid stdin renders from {}), BC-1.02.020
  (thermometer NaN crash path), BC-1.02.026 (_fmt_lines OverflowError), BC-1.02.027
  (_hm ValueError), BC-1.04.014 (sparkline NaN/+Inf), BC-1.04.015 (KV NaN), BC-1.04.016
  (row-2 NaN rendering), BC-1.06.001 (never-raise cache load/save).
- **Invariant verified:** DI-008 (rendering never fails; degraded ladder ends in
  one-line output, exit 0). NFR-002 (100% of CP-* triggers, fault-injection table).

## Property Class and Verification Method

- **Class:** safety.
- **Method:** unit/table test — exhaustive fault-injection table over the closed
  trigger catalogue, one row per CP-* id, asserting `len(stdout) >= 1 && exit == 0`.
- **Honesty (iron law):** testable-only. This is an empirical property over an
  enumerated trigger list, not a formal proof; completeness rests on the taxonomy being
  closed (error-taxonomy.md) and Tier C fuzz hunting for unenumerated paths (VP-011).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test | Go test, `go test ./internal/statusline -run TestDegradedLadder` | yes — closed CP-* catalogue | every enumerated fault trigger |

## Proof Harness Skeleton

```go
func TestDegradedLadder_AllTriggers(t *testing.T) {
    for _, tc := range FaultInjectionTable { // one row per CP-S01..S17, T01..T07, N01, N02 + panic rows
        stdout, _, exit := runStatusline(tc.Env, tc.Stdin, tc.Files)
        if exit != 0 { t.Fatalf("%s: exit = %d, want 0", tc.ID, exit) }
        if len(stdout) == 0 { t.Fatalf("%s: blank stdout", tc.ID) }
    }
}
```

## Named Tests (OD-145 table where applicable)

Fault rows are the cps01..cps17, cpt01..cpt07, cpn01, cpn02 parity-case families
(ARCH-07 case grammar); the degraded line itself is pinned by BC-1.01.001 table tests.
See also VP-003 for the degraded-write-failure case (`cp-x03`).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Small, closed | one row per taxonomied trigger |
| Proof complexity | N/A | enumeration, not deduction |
| Tool support | Full | plain Go tables |
| Estimated proof time | Hours | table authoring dominates |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
