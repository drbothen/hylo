---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-02-configuration.md, behavioral-contracts/ss-02/BC-2.01.002.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "97d0de8"
traces_to: prd.md
source_bc: BC-2.01.002
module: internal/config (backends validator)
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

# VP-017: Exactly-one-backend cardinality until P6

## Property Statement

The `backends[]` config validator accepts exactly one entry in P1-P5: zero entries and
more than one entry are config errors carrying the reason `exactly one backend entry
until P6`, riding the D4-EX-3 output path. The status line's metrics URL and model
prefixes are read exclusively at `backends[0].metrics_url` / `backends[0].model_prefixes`
(default `claude-sonnet`), and the cardinality check is isolated in one validator
function that P6 widens — no other code learns the cardinality rule.

## Source Contract

- **Primary BC:** BC-2.01.002 — backends array: exactly one entry validated until P6;
  backends[0].metrics_url / backends[0].model_prefixes; default prefixes claude-sonnet.
- **Invariant verified:** DI-010 (validated config, named reasons); OD-123 (N backends
  schema from the start, one entry validated); AD-12 (validator-isolated seam for P6).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — cardinality 0, 1, 2 through `Load`, asserting the
  typed error reason and the D4-EX-3 line; plus a `backends[0]` default-values table
  (prefixes default, metrics_url plumb-through).
- **Honesty:** testable-only; the rule is a ruling (OD-123), finite case space.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Cardinality table | Go test, `internal/config` | yes — 0/1/2/N | error rows + defaults plumb-through |

## Proof Harness Skeleton

```go
func TestBackends_ExactlyOneUntilP6(t *testing.T) {
    if _, err := config.Load(optsWithBackends()); err == nil ||
        err.Reason != "exactly one backend entry until P6" {
        t.Fatalf("zero backends: got %v", err)
    }
    if _, err := config.Load(oneBackendOpts()); err != nil { t.Fatalf("one backend rejected: %v", err) }
    if _, err := config.Load(twoBackendsOpts()); err == nil { t.Fatal("two backends accepted") }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestBackends_ExactlyOneUntilP6`; the
error line itself is pinned by the VP-016 class tables.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Tiny | 0/1/2/N backends |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Hours | |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
