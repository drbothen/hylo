---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T02:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-01/BC-1.01.002.md, behavioral-contracts/ss-05/BC-5.02.003.md, behavioral-contracts/ss-01/BC-1.03.004.md, prd-supplements/nfr-catalog.md]
input-hash: "7adfd2a"
traces_to: prd.md
source_bc: BC-5.02.003
bcs: [BC-5.02.003, BC-1.01.002, BC-1.03.004]
module: internal/pyfmt (json.go)
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — per-site table states both protocol sites at 993/994 (measured end to end on legacy 2026-11-17, superseding the 989/990 direct-probe figure); cache-load sites declared unmeasured/open, due before Phase 3 (A2-13); proof_file_hash field added (A2-29)", "1.3 2026-11-17: pass-2 follow-up — ADV-P2-A07 closed: governing formula limit = 999 − Python frames from <module> down to json.raw_decode recorded; all eight loader sites stated (stdin/transcript 993/994, session cache 991/992 and git cache 990/991 measured; get_sample, claude_window_start, mix cache and the cost-history loaders derived from equal chain depth); per-site measurement recipe added; harness asserts limit/limit+1 at every site"]
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
explicit per-call-site argument (BC-5.02.003:71-72), not baked into the decode mode.
Governing formula, validated end to end on the real legacy program with isolated HOME
(orchestrator, 2026-11-17): **limit at a call site = 999 − (number of Python frames
from `<module>` down to json's `raw_decode`)**. Each site flips at a single limit —
depth L accepted, L+1 rejected, no gap (BC-5.02.003:65-66); hylo's per-site budget
argument is derived from the observed flip depth, not a free constant.

| Call site (chain from `<module>`) | Frames | Accepted | Rejected | Status |
|---|---|---|---|---|
| stdin payload — main → json.load | 6 | 993 | 994 | measured |
| transcript lines — main → _mix_counts → json.loads | 6 | 993 | 994 | measured |
| session cache — main → effective_rl → load_cache | 8 | 991 | 992 | measured |
| get_sample loader (session-cache chain depth) | 8 | 991 | 992 | derived |
| claude_window_start loader (session-cache chain depth) | 8 | 991 | 992 | derived |
| mix cache — main → _mix_counts → load_cache | 8 | 991 | 992 | derived |
| git cache — main → render_lane → git_segment → load_cache | 9 | 990 | 991 | measured |
| cost history — record_cost / cost_thresholds (called from render_lane) | 9 | 990 | 991 | derived |

(stdin: BC-1.01.002 EC-005/EC-006; transcript: re-measured end to end 2026-11-17,
superseding the 989/990 direct-probe figure quoted at BC-5.02.003:67. Cache loaders:
ADV-P2-A07 closed — session and git caches measured end to end; peer loaders derived
from equal chain depth; sites are ModeText, ARCH-04:43.) Each measured site is tested
at exactly L accepted / L+1 rejected. Boundary values behave identically to CPython
3.11 `json.load`/`json.loads(bytes)`.

Measurement recipe (isolated HOME; a nested list grown under a key until the flip):
stdin — pipe the payload; depth L renders, L+1 degrades. Transcript — deep JSON line;
acceptance observable: the count shows in the mix-cache tin. Session cache — deep key
accepted: the key is kept after a run with rate_limits. Git cache — deep cache
accepted: the cached branch is shown.

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
    // Flip depths measured end to end on legacy, isolated HOME, 2026-11-17
    // (ADV-P2-A07 closed): limit = 999 − Python frames from <module> down to
    // json.raw_decode. Peer loaders at equal chain depth share the row.
    cases := []struct{ name string; mode pyfmt.DecodeMode; ok, reject int }{
        {"stdin site", pyfmt.ModeText, 993, 994},
        {"transcript site", pyfmt.ModeBytes, 993, 994},
        {"session cache (+ get_sample, claude_window_start, mix cache)", pyfmt.ModeText, 991, 992},
        {"git cache (+ record_cost, cost_thresholds)", pyfmt.ModeText, 990, 991},
    }
    for _, c := range cases {
        if _, err := pyfmt.Decode(nested(c.ok), c.mode, budgetOf(c.name)); err != nil {
            t.Fatalf("%s: depth %d rejected", c.name, c.ok)
        }
        if _, err := pyfmt.Decode(nested(c.reject), c.mode, budgetOf(c.name)); err == nil {
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
