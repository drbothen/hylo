---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-17T22:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.03.001.md, owner-decisions-log-2026-11-14.md]
input-hash: "35953d8"
traces_to: prd.md
source_bc: BC-6.03.001
bcs: [BC-1.06.002, BC-6.03.001, BC-6.04.001, BC-1.07.004, BC-1.07.005, BC-1.07.006]
module: internal/parity
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: added BC-1.06.002 to bcs — the Tier B golden statement verifies its slash-sid stdout-parity row", "1.3 2026-11-17: subagent goldens added — BC-1.07.004 (NDJSON row framing, ` · ` selector, ensure_ascii, zero-survivor zero-byte case), BC-1.07.005 (glyph/name-fallback/settled-suffix matrix), BC-1.07.006 (lane-pill byte rows; the startswith property leg is VP-028's rule, extended there)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-010: Tier B committed goldens — Python-written, Go matches on every OS

## Property Statement

Every committed Tier B golden under `internal/statusline/testdata/goldens/` is written
by the Python oracle (never Go): the POSIX goldens are recorded on Linux oracle runs,
and the `*.windows.golden` variants for OS-dependent cases are Python-written on a
**Windows oracle run** — a Linux run cannot produce ntpath output (BC-6.03.001 match
rule 7). The Go port's output matches the applicable golden
byte-for-byte on every CI OS without Python installed. The subagent row goldens
(BC-1.07.004/005/006) are Python-written NDJSON: one `{"id": ..., "content": ...}`
line per eligible task with CPython default separators and `ensure_ascii=True`, the
raw three-byte ` · ` selector, the glyph/name-fallback/settled-suffix matrix, the
lane-pill byte rows, and the zero-survivors-produce-zero-bytes case. Golden metadata
records the
resolved Python patch version (RK-4).

## Source Contract

- **Primary BC:** BC-6.03.001 — Row goldens A/B/C (Tier B, Python-written, OS-specific
  variants).
- **Partial coverage:** BC-1.06.002 (sid with `/`: stdout over an N-refresh sequence
  equals legacy — the Tier B golden row), BC-6.04.001 (Windows leg runs Tier B without
  Python).
- **Invariant verified:** DI-012 (the referee writes the expected bytes, keeping the
  refereed side from self-certifying); AD-13 (fixture co-location).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** golden/parity tier — `TestParityTierB_Goldens` over committed goldens;
  `-update` writes Python output and fails if the interpreter is unset (OD-104).
- **Honesty:** testable-only; OS coverage follows the CI matrix (VP-037).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Golden test | `go test ./internal/parity -run TestParityTierB_Goldens` | yes — committed goldens | all row goldens, per-OS variant selection |

## Proof Harness Skeleton

```go
func TestParityTierB_Goldens(t *testing.T) {
    for _, g := range LoadGoldens("internal/statusline/testdata/goldens") {
        out := RunGoPortForCase(g.Case) // variant-selects *.windows.golden on windows
        if !bytes.Equal(out, g.Bytes) { t.Fatalf("%s: bytes differ", g.Case) }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestParityTierB_Goldens`; flag `-update`; metadata records the setup-python patch
version (RK-4).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Committed goldens | fixed |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | variant bookkeeping is the cost |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
