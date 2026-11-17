---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-01/BC-1.01.002.md, behavioral-contracts/ss-01/BC-1.01.008.md, domain-spec/invariants.md]
input-hash: "0013234"
traces_to: prd.md
source_bc: BC-1.01.002
bcs: [BC-1.01.002, BC-1.01.008]
module: internal/statusline (input.go, guard.go), internal/pyfmt
proof_method: fuzz
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

# VP-005: stdio codec totality — stdin decode yields a render state; stdout is valid UTF-8

## Property Statement

For every possible stdin byte string (valid JSON, non-JSON, non-object, empty, invalid
UTF-8), the stdin decode step produces a defined `pyfmt.Value` — an empty object on any
decode failure per the legacy semantics — and the render completes (never blank, exit
0). No stdin input can crash the decode step or abort the refresh. Symmetrically,
whatever the fault, the stdout bytes are always valid UTF-8: the guard emits the
degraded line with lone surrogates encoded per the BC-1.01.008 rules, so `utf8.Valid`
holds on every rendered output (BC-1.01.008 stdout property, formerly "no VP yet").

## Source Contract

- **Primary BC:** BC-1.01.002 — Non-JSON or non-object stdin decodes to an empty
  object.
- **Partial coverage:** BC-1.01.008 (strict UTF-8 stdio; invalid stdin UTF-8 renders
  from {}).
- **Invariant verified:** DI-008 (stdin faults are on the degraded ladder's safe side).

## Property Class and Verification Method

- **Class:** safety.
- **Method:** property-based/fuzz test — `go test -fuzz` over arbitrary stdin byte
  strings through `pyfmt.Decode(ModeText)` plus the render completion and
  `utf8.Valid(stdout)` asserts; plus boundary tables (BOM, truncated objects, arrays,
  scalars, invalid UTF-8, CP-S17 surrogate shapes).
- **Honesty:** testable-only; the fuzz oracle is totality itself (defined decode
  outcome + non-blank valid-UTF-8 stdout), not a live CPython call — equivalence rows
  come from the committed oracle tables and the BC-1.01.008 vector table.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Fuzz | `go test -fuzz` (stdlib), CI-seeded, nightly-extensible | no (fuzzer), bounded runs | arbitrary stdin byte strings |
| Boundary tables | Go test | yes | BOM/scalar/truncated/invalid-UTF-8 rows |

## Proof Harness Skeleton

```go
func FuzzStdinDecodeTotality(f *testing.F) {
    for _, s := range SeedStdinCorpus { f.Add(s) }
    f.Fuzz(func(t *testing.T, stdin []byte) {
        v, err := pyfmt.Decode(stdin, pyfmt.ModeText) // must not panic
        _ = v
        _ = err                                       // error allowed, panic is not
        stdout, _, exit := renderFromStdin(stdin)
        if exit != 0 || len(stdout) == 0 { t.Fatal("render not total") }
    })
}
```

## Named Tests (OD-145 table where applicable)

stdin decode rows ride the `frame` parity-case family (ARCH-07); fuzz target named
`FuzzStdinDecodeTotality` (in-tree; Tier C extension optional).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Infinite | mitigated by fuzzing |
| Proof complexity | Low | decode is total by construction |
| Tool support | Full | stdlib fuzzing |
| Estimated proof time | Hours | seed corpus from BC tables |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
