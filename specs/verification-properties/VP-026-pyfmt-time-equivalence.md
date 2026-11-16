---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-05/BC-5.04.001.md, behavioral-contracts/ss-05/BC-5.04.002.md, behavioral-contracts/ss-05/BC-5.04.003.md, owner-decisions-log-2026-11-14.md]
input-hash: "bfa25fe"
traces_to: prd.md
source_bc: BC-5.04.002
bcs: [BC-5.04.001, BC-5.04.002, BC-5.04.003]
module: internal/pyfmt (time.go)
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

# VP-026: pyfmt time semantics equivalent to CPython 3.11 (`_mktime` port, ISO grammar)

## Property Statement

`FromISOFormat` implements the Python 3.11 grammar (naive = local, fraction truncation
beyond µs); `LocalToUnix` is the CPython `_mktime` port with gap/overlap semantics
achieving 0 mismatches over the committed 10,893 CPython goldens across four zone
grids (Go `time.Date` differs — that is why the port exists); `TimeFloat` holds the
Python time.time() value discipline (ns→s float, read once per render). Embedded
`time/tzdata` makes zone data interpreter-independent.

## Source Contract

- **Primary BC:** BC-5.04.002 — LocalToUnix: CPython `_mktime` port, gap/overlap
  semantics, TZ injection, embedded tzdata.
- **Partial coverage:** BC-5.04.001 (FromISOFormat 3.11 grammar), BC-5.04.003
  (TimeFloat once-per-render).
- **Invariant verified:** IM-14 (one clock read per render) jointly with VP-007;
  AD-04 (CPython fidelity for naive-local transcript timestamps, BC-5.04.001).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** oracle tables — 10,893 CPython `_mktime` goldens across four zone grids
  (DST gaps, overlaps, repeated hours), FromISOFormat grammar tables; a once-per-render
  counter for TimeFloat (joint with VP-007's counting seam).
- **Honesty:** testable-only; zone-grid breadth is the strongest table-pinning in the
  repo but remains empirical.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Zone-grid goldens | Go test, 10,893 rows x 4 grids | yes — committed grid | gap/overlap/all-zones |
| Grammar tables | Go test | yes | FromISOFormat rows |
| Counter assert | Go test | exact | one TimeFloat read per render |

## Proof Harness Skeleton

```go
func TestLocalToUnix_ZoneGridGoldens(t *testing.T) {
    for _, g := range LoadGolden("testdata/mktime.golden") {
        if got := pyfmt.LocalToUnix(g.Loc, g.Wall); got != g.Unix {
            t.Fatalf("%s %v: got %v want %v", g.Zone, g.Wall, got, g.Unix)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; goldens at `internal/pyfmt/testdata/mktime.golden`
(gen scripts under `testdata/gen/*.py`, pinned 3.11 oracle).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | 10,893 x 4 committed | generated offline |
| Proof complexity | Medium | DST edge enumeration offline |
| Tool support | Full | |
| Estimated proof time | Days | grid generation under the oracle |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
