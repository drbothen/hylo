---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-04-data-files.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.05.004.md, behavioral-contracts/ss-01/BC-1.05.006.md, behavioral-contracts/ss-01/BC-1.05.009.md, owner-decisions-log-2026-11-14.md]
input-hash: "b7f58f5"
traces_to: prd.md
source_bc: BC-1.05.004
bcs: [BC-1.05.004, BC-1.05.006, BC-1.05.009]
module: internal/cost
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

# VP-020: Cost-history record integrity — no wipe on parse failure

## Property Statement

An unreadable or malformed `cost-history.json` never causes the status line to destroy
or silently overwrite it: the load yields an empty in-memory history, the file on disk
is left untouched, and the next successful `record_cost` writes the exact legacy JSON
format (separators, ensure_ascii, int/float distinction, OD-138's oracle-pinned NaN usd
bytes) starting from the loaded state. The throttle is strict `<`; numeric sids write
one string-form key (OD-30) and self-exclusion fails with a single string-form key.
Anti-pattern AP-16 (a cache parse failure wipes all history on the next write) is
disposed: the Go writer reproduces the legacy format and never overwrites an unreadable
file silently.

## Source Contract

- **Primary BC:** BC-1.05.004 — record_cost throttled write.
- **Partial coverage:** BC-1.05.006 (numeric sid: throttle and self-exclusion, single
  string-form key), BC-1.05.009 (record_cost exact JSON format).
- **Invariant verified:** OD-124 (status line owns the format; guests honor it), OD-138
  (NaN usd pinned from the oracle), AP-16 disposition (pass-8 anti-pattern register,
  porting-decision §8.2 item 5).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — poisoned-file fault injection: malformed JSON, wrong
  types, NaN-bearing history, wrong permissions; assert file bytes unchanged after load
  and after the first throttled write; format rows compare exact bytes against
  oracle-pinned expectations.
- **Honesty:** testable-only (filesystem seam); byte format is oracle-pinned.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Poisoned-file tables | Go test, temp dirs | yes — enumerated malformation classes | load-leave-intact + write-format rows |
| Byte pins | oracle-pinned expectations | yes | record_cost JSON format incl. NaN usd |

## Proof Harness Skeleton

```go
func TestCostHistory_NoWipeOnParseFailure(t *testing.T) {
    dir := tempCacheDir(t)
    poisoned := writeFile(dir, "cost-history.json", garbage)
    hist := cost.Load(poisoned)
    if !hist.Empty() { t.Fatal("poisoned load not empty") }
    cost.Record(hist, session, usd) // throttled record
    if readFile(dir, "cost-history.json") != poisoned {
        t.Fatal("unreadable file overwritten before a successful load (AP-16)")
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestCostHistory_NoWipeOnParseFailure`;
format rows additionally pinned by the `swap` cost family (VP-019).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Enumerated malformations | small |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | OD-30 single-key rows included |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
