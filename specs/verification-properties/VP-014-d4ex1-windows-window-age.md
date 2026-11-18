---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-05-platform.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-03/BC-3.02.001.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "3e6513a"
traces_to: prd.md
source_bc: BC-3.02.001
bcs: [BC-3.02.001]
module: internal/platform (proc), internal/statusline (window age)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
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

# VP-014: D4-EX-1 — ⌂ window-age difference on Windows is bounded and tested

## Property Statement

The ruled Windows difference (legacy showed no ⌂ on Windows because `ps` is absent; the
native probe shows it) is admitted only through the exclusion id `D4-EX-1` with its
dedicated fake-probe test: with `ProcStarter.WindowStart` faked, the Go port renders the
⌂ suffix with the ruled visibility gate on Windows exactly as the ruled bytes demand;
macOS/Linux probe behaviour is not touched by this exclusion.

## Source Contract

- **Primary BC:** BC-3.02.001 — Window start via native per-OS ancestor probe;
  whole-second truncation; `proc_start` key first.
- **Invariant verified:** DI-012 (named, tested deviation — OD-105/OD-110); the
  exclusion list cannot broaden (VP-012 closes the machinery).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test with fake probe — `TestWindowAge_D4EX1_Windows` exercises
  the suffix format, the visibility gate, and the whole-second truncation, with the
  fake probe returning ruled values.
- **Honesty:** testable-only; the OS-scoped difference itself is a ruling, not a
  derivable fact.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Fake-probe table | Go test, `internal/statusline` + `internal/platform` | yes — ruled value table | ⌂ format x gate x truncation on the ruled OS |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestWindowAge_D4EX1_Windows(t *testing.T) {
    for _, tc := range WindowAgeTable {
        out := renderWindowAge(fakeProc(tc.Start), fakeNow(tc.Now), tc.Width)
        if out != tc.WantSuffix { t.Fatalf("%s: %q", tc.Name, out) }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestWindowAge_D4EX1_Windows` (settled name, ARCH-07); Windows-leg pinned by the
windows-2025 CI assumption set (PRD §9.5).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Small | ruled value table |
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
