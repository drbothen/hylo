---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T09:06:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-01/BC-1.01.002.md, behavioral-contracts/ss-01/BC-1.01.008.md, domain-spec/invariants.md]
input-hash: "62dbef5"
traces_to: prd.md
source_bc: BC-1.01.002
bcs: [BC-1.01.002, BC-1.01.008, BC-1.07.002, BC-1.07.003]
module: internal/statusline (input.go, guard.go), internal/pyfmt
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fixes — skeleton asserts utf8.Valid(stdout) (A2-25); added the --subagent stdin-absorb totality leg (BC-1.07.003) and the subagent.enabled=false zero-lines leg (BC-1.07.002)", "1.3 2026-11-18T09:06:00Z: ADV-P3 fixes — 3-arg pyfmt.Decode(b, mode, per-site budget) everywhere (A2-08); subagent fuzz leg asserts rows-or-zero-bytes and never-the-degraded-line-via-the-parse-path, with OD-168 (subagent config error = zero bytes) in the output set (A2-07); enabled=false recast as a non-default config value, not a DI-012 named deviation (A2-21)"]
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
0). No stdin input can crash the decode step or abort the refresh. The `--subagent`
entry absorbs stdin faults the same way (BC-1.07.003): for every byte string the
subagent renderer yields its rows or zero bytes, exit 0 — never the degraded line via
the parse path; a subagent config error is likewise zero bytes (OD-168); and with
`statusline.subagent.enabled=false` (BC-1.07.002 — a non-default config value, not a
DI-012 parity exclusion; the DI-012 machinery governs parity exclusions and no
exclusion id covers this; default `true` = legacy) the render is zero JSON lines for every
stdin. Symmetrically,
whatever the fault, the stdout bytes are always valid UTF-8: the guard emits the
degraded line with lone surrogates encoded per the BC-1.01.008 rules, so `utf8.Valid`
holds on every rendered output (BC-1.01.008 stdout property, formerly "no VP yet").

## Source Contract

- **Primary BC:** BC-1.01.002 — Non-JSON or non-object stdin decodes to an empty
  object.
- **Partial coverage:** BC-1.01.008 (strict UTF-8 stdio; invalid stdin UTF-8 renders
  from {}), BC-1.07.003 (subagent stdin absorb: rows or zero bytes, never the degraded
  line via the parse path), BC-1.07.002 (`subagent.enabled=false` suppresses the
  entire subagent render — zero JSON lines, exit 0; the `enabled=true` parity leg rides
  the Tier A corpus, VP-009, and the Tier B goldens, VP-010).
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
    f.Fuzz(func(t *testing.T, stdin []byte, subagent bool, enabled bool) {
        // 3-arg Decode: per-call-site budget argument (VP-006), never a free constant
        v, err := pyfmt.Decode(stdin, pyfmt.ModeText, stdinSiteBudget)
        _ = v
        _ = err                                       // error allowed, panic is not
        stdout, _, exit := renderFromStdin(stdin, subagent, enabled)
        if exit != 0 { t.Fatal("render not total") }
        if !subagent && len(stdout) == 0 { t.Fatal("blank render on main entry") }
        if subagent && enabled { // BC-1.07.003 (A2-07): rows or zero bytes; never the
            // degraded line via the parse path; OD-168: config error = zero bytes
            if len(stdout) > 0 && !isNDJSONRows(stdout) {
                t.Fatal("subagent stdout outside the rows-or-zero-bytes output set")
            }
            if stdout == degradedLine { t.Fatal("degraded line via the parse path") }
        }
        if subagent && !enabled && len(stdout) != 0 { // BC-1.07.002 off switch
            t.Fatal("subagent render with enabled=false must be zero JSON lines")
        }
        if !utf8.Valid(stdout) { t.Fatal("stdout is not valid UTF-8 (BC-1.01.008)") }
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
