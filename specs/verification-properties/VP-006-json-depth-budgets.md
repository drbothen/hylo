---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-01/BC-1.01.002.md, behavioral-contracts/ss-05/BC-5.02.003.md, behavioral-contracts/ss-01/BC-1.03.004.md, prd-supplements/nfr-catalog.md]
input-hash: "ad5ccd8"
traces_to: prd.md
source_bc: BC-5.02.003
bcs: [BC-5.02.003, BC-1.01.002, BC-1.03.004]
module: internal/pyfmt (json.go)
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-006: Per-call-site JSON recursion depth budgets hold exactly

## Property Statement

`pyfmt.Decode` honours the per-call-site recursion budget exactly: the budget is an
explicit per-call-site argument (BC-5.02.003:71-72), not baked into the decode mode —
`ModeText` serves both the stdin and cache-load sites, which sit at different
CPython frame depths. Measured boundaries: the transcript `_mix_counts` call site
pins L = 989 accepted / 990 rejected (BC-5.02.003:67, reproduced four consecutive
runs); the stdin text-mode site pins 993 accepted / 994 rejected (BC-1.01.002
EC-005/EC-006, re-probed 2026-11-17). Each site is tested at exactly L accepted /
L+1 rejected — a single limit, no gap (BC-5.02.003:65-66). Boundary values behave
identically to CPython 3.11 `json.load`/`json.loads(bytes)`.

## Source Contract

- **Primary BC:** BC-5.02.003 — json.loads(bytes) acceptance set (depth bounds).
- **Partial coverage:** BC-1.01.002 (stdin text-mode budget via Decode ModeText),
  BC-1.03.004 (transcript bytes-mode consumption).
- **Invariant verified:** NFR-003 plumbing (hand-written decoder, banned stdlib codecs
  on protocol inputs, cannot silently change the budget).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** fuzz + boundary tables — generate deeply nested Values around each
  budget; assert accept/reject at budget-1, budget, budget+1 for both modes; fuzz for
  the absence of stack exhaustion below budget.
- **Honesty:** testable-only; the budget parameterisation is statically checkable
  (no global), the boundary rows are exact.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Boundary tables | Go test | yes — ±1 around each budget | both modes |
| Fuzz | `go test -fuzz` | bounded runs | nested-input robustness below budget |

## Proof Harness Skeleton

```go
func TestDecode_DepthBudgetsPerCallSite(t *testing.T) {
    cases := []struct{ name string; mode pyfmt.DecodeMode; budget, ok, reject int }{
        {"mix_counts site", pyfmt.ModeBytes, budgetOf("_mix_counts"), 989, 990},
        {"stdin site", pyfmt.ModeText, budgetOf("stdin"), 993, 994},
    }
    for _, c := range cases {
        if _, err := pyfmt.Decode(nested(c.ok), c.mode, c.budget); err != nil {
            t.Fatalf("%s: depth %d rejected", c.name, c.ok)
        }
        if _, err := pyfmt.Decode(nested(c.reject), c.mode, c.budget); err == nil {
            t.Fatalf("%s: depth %d accepted", c.name, c.reject)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table (pyfmt scope); restaged per BC-5.02.003's canonical
tables; fuzz target `FuzzDecode_depth` (in-tree pyfmt fuzz set, ARCH-06 §2.6 hom_set).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Small (boundary) + infinite (fuzz) | |
| Proof complexity | Low | recursion is budget-guarded |
| Tool support | Full | stdlib fuzzing |
| Estimated proof time | Hours | generator must emit WTF-8-safe nesting |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
