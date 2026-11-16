---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-05/BC-5.03.001.md, behavioral-contracts/ss-05/BC-5.03.002.md, behavioral-contracts/ss-05/BC-5.03.003.md, behavioral-contracts/ss-05/BC-5.03.004.md, owner-decisions-log-2026-11-14.md]
input-hash: "904a6b4"
traces_to: prd.md
source_bc: BC-5.03.001
bcs: [BC-5.03.001, BC-5.03.002, BC-5.03.003, BC-5.03.004]
module: internal/pyfmt (str.go)
proof_method: proptest
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

# VP-025: pyfmt code-point string ops equivalent to Python semantics

## Property Statement

WTF-8-aware helpers agree with Python 3.11 semantics: `Len` (surrogate = 1 code point,
not terminal cells), `Truncate`, `HasSurrogate`, `EncodeUTF8Replace` (lone surrogate →
`?`), `Strip`/`RStrip` (Python whitespace incl. NBSP; `\n` `\r\n` `\r` splitting only in
`SplitLinesBytes`), `RSplit1`, `SubNonWord` (per code point before truncation),
`PosixNormpath`/`NtNormpath`/`Basename` (per-OS selection with ntpath on Windows).

## Source Contract

- **Primary BC:** BC-5.03.001 — Len/Truncate/HasSurrogate: code points, surrogate =
  1, not terminal cells.
- **Partial coverage:** BC-5.03.002 (Strip/RStrip/RSplit1/SplitLinesBytes), BC-5.03.003
  (SubNonWord; EncodeUTF8Replace), BC-5.03.004 (per-OS normpath selection).
- **Invariant verified:** AD-04 (CPython fidelity); NFR-003 substrate.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** property-based + oracle tables — generated Unicode/UTF-8/wtf8 strings
  sampled over planes, surrogates, combining marks; committed oracle tables for
  whitespace-set and normpath corner cases.
- **Honesty:** testable-only; Python whitespace and normpath semantics are pinned by
  tables, breadth via generators.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Oracle tables | Go test | yes | whitespace corners, normpath cases |
| Property generators | Go test | no (random), seeded | Unicode string space |

## Proof Harness Skeleton

```go
func TestStr_OracleTables(t *testing.T) {
    for _, row := range LoadGolden("testdata/str.golden") {
        if got := row.Op(row.Input); got != row.Want {
            t.Fatalf("%q: got %q want %q", row.Input, got, row.Want)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; consumed by the S1.03 parser family (VP-029) via
BC-5.03 dual-home rule (helper home in S5 per BC-ALLOCATION edge case 3).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Very large | Unicode; sampled |
| Proof complexity | Medium | code-point vs byte semantics |
| Tool support | Full | |
| Estimated proof time | Days | generator quality decides |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
