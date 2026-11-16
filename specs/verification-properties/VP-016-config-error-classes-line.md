---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-02-configuration.md, behavioral-contracts/ss-02/BC-2.02.001.md, behavioral-contracts/ss-02/BC-2.02.002.md, behavioral-contracts/ss-02/BC-2.02.003.md, behavioral-contracts/ss-02/BC-2.02.004.md, behavioral-contracts/ss-02/BC-2.02.005.md, behavioral-contracts/ss-02/BC-2.02.006.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "0863dac"
traces_to: prd.md
source_bc: BC-2.02.001
bcs: [BC-2.01.003, BC-2.02.001, BC-2.02.002, BC-2.02.003, BC-2.02.004, BC-2.02.005, BC-2.02.006, BC-2.03.001]
module: internal/config (errors.go), cmd/hylo
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

# VP-016: D4-EX-3 config-error classes, line format, and no-cache-writes guarantee

## Property Statement

Every invalid setting value falls into exactly one of the six closed config-error
classes (number-range, number-grammar, enum, URL, boolean, theme/SGR), and any invalid
value renders exactly `\e[90mhylo: config error: <key>=<value> (<reason>)\e[0m\n` on
stdout, exits 0, prints the full error list plus `[from <ENVNAME>]` on stderr, selects
the first error in registry order (order-stable selection), and — critically — writes
no cache files. `hylo config validate` exits 1 for the same errors.

## Source Contract

- **Primary BC:** BC-2.02.001 — D4-EX-3 config-error line: exact format, exit 0,
  stderr detail, no cache writes.
- **Partial coverage:** BC-2.02.002 (number-range), BC-2.02.003 (number-grammar),
  BC-2.02.004 (enum), BC-2.02.005 (URL), BC-2.02.006 (boolean, OD-140); BC-2.03.001
  (validate exit 1).
- **Invariant verified:** DI-008 (config errors are one-line outputs, D4-EX-3);
  OD-102/OD-114/OD-134; approved-deviation closed set membership (D4-EX-3).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — one table per class (the five settled names below) with
  exact expected bytes; plus a registry-order property test (first-error selection is
  order-stable under permutation of invalid variables); plus a no-cache-writes assert
  (empty temp dir after a config-error run).
- **Honesty:** testable-only; class closure is a ruling (a seventh class needs an owner
  decision — AD-06), enumerated exhaustively because the registry domain is closed.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Class tables | Go test, `cmd/hylo` + `internal/config` | yes — six classes | every class x representative + boundary values |
| Order property | Go test | yes — permutation check | registry-order stability |

## Proof Harness Skeleton

```go
func TestConfigError_D4EX3_Number(t *testing.T)   { runClassTable(t, numberRangeRows) }
func TestConfigError_D4EX3_Boolean(t *testing.T)  { runClassTable(t, booleanRows) }
func TestConfigError_D4EX3_URL(t *testing.T)      { runClassTable(t, urlRows) }
func TestConfigError_D4EX3_Enum(t *testing.T)     { runClassTable(t, enumRows) }
func TestConfigError_D4EX3_Theme(t *testing.T)    { runClassTable(t, themeRows) }

func TestConfigError_FirstErrorRegistryOrder(t *testing.T) {
    if firstErr permuted == firstErr canonical { /* order-stable */ } { t.Fatal("order drifted") }
}
```

## Named Tests (OD-145 table where applicable)

`TestConfigError_D4EX3_{Number,Boolean,URL,Enum,Theme}` (settled, ARCH-07); order
property named `TestConfigError_FirstErrorRegistryOrder`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Six classes, small | registry-closed |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | boundary values per class (TTL nan/inf/neg, 4_0, Unicode digits, TRACE, URL scheme, bool spellings) |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
