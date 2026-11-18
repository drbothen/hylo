---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-18T02:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.003.md, behavioral-contracts/ss-01/BC-1.01.004.md, behavioral-contracts/ss-01/BC-1.01.005.md, behavioral-contracts/ss-01/BC-1.01.006.md, behavioral-contracts/ss-01/BC-1.01.007.md, behavioral-contracts/ss-01/BC-1.01.010.md]
input-hash: "aa6c5a2"
traces_to: prd.md
source_bc: BC-1.01.010
bcs: [BC-1.01.003, BC-1.01.004, BC-1.01.005, BC-1.01.006, BC-1.01.007, BC-1.01.010]
module: internal/statusline (width.go, guard frame)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: pass-2 follow-up — the for-all property rows and Tier C differential legs claimed by BC-1.01.003..007 (row/LF structure, visible additivity and CPython differential, term_cols grammar differential, trim structure/boundedness, negative-COLUMNS) spun off to VP-040; this VP remains the fixed breakpoint matrix + Python int grammar for COLUMNS"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-027: Frame, width, and trim math — breakpoint matrix and Python int grammar for COLUMNS

## Property Statement

Row joining (LF, row 2 only when width permits), visible-width counting (code points
after SGR stripping), the trim breakpoint matrix across widths (double-reset, recycle
row, single-reset), negative-COLUMNS disabling trim and hiding row 2, and COLUMNS
parsing with the Python int grammar (else 0; overflowing negative stays negative —
row 2 hidden; only the over-4,300-digit error path maps to 0) all match the
oracle-pinned matrix exactly.

## Source Contract

- **Primary BC:** BC-1.01.010 — Trim breakpoint matrix across widths.
- **Partial coverage:** BC-1.01.003 (LF join, width rule), BC-1.01.004 (visible width
  = code points after SGR strip), BC-1.01.005 (COLUMNS grammar, else 0), BC-1.01.006
  (double-reset/recycle), BC-1.01.007 (negative COLUMNS).
- **Not covered here:** the for-all property rows and Tier C differential legs these
  BCs also claim (quantified over generators, not a fixed matrix) are delivered by
  VP-040.
- **Invariant verified:** NFR-005 joint (caps are legacy-fixed named constants where
  applicable); stage-3 normalization restatement (overflowing-negative behavior
  identical in BC-1.01.005 PC-4 and BC-5.01.002 PC-3).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — the canonical breakpoint matrix across widths crossed
  with SGR-bearing contents, COLUMNS grammar corners (int64 edges, 4,301 digits,
  underscores, Unicode digits).
- **Honesty:** testable-only; matrix breadth rides the corpus and Tier C.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Breakpoint matrix | Go test | yes — canonical width matrix | join/width/trim/negative rows |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestTrim_BreakpointMatrix(t *testing.T) {
    for _, r := range BreakpointMatrix {
        got := renderFrame(r.Contents, r.COLUMNS)
        if got != r.Want { t.Fatalf("width %d: %q", r.COLUMNS, got) }
    }
}
```

## Named Tests (OD-145 table where applicable)

`frame` parity family (ARCH-07 case grammar); in-tree matrix named
`TestTrim_BreakpointMatrix`; COLUMNS corners shared with BC-5.01.002 tables.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Matrix-sized | bounded |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | width matrix authoring |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
