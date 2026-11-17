---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-01-binary-cli.md, behavioral-contracts/ss-04/BC-4.01.002.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "b02f675"
traces_to: prd.md
source_bc: BC-4.01.002
bcs: [BC-4.01.002]
module: cmd/hylo
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

# VP-002: Unknown flag renders one-line error, exit 0, never blank (flags before `--`)

## Property Statement

For every argv vector containing at least one **flag** — an argument that starts with
`-`, is not exactly `-`, and appears before a `--` terminator (BC-4.01.002
Precondition 2) — `hylo statusline` renders exactly
`\e[90mhylo: unknown flag <flag>\e[0m\n` for the first flag in argv order and exits 0.
A bare `-` is positional and does not trigger the error (EC-005); arguments after `--`
are positional and render normally (EC-004); positional arguments alone run the normal
render (BC-4.01.001). Includes a leftover `--subagent` (OD-14). The scan runs before
config resolution (E-CLI-001 outranks E-CFG-001); stdlib `flag` with `ExitOnError`
(exit 2, blank line) never runs on this path.

## Source Contract

- **Primary BC:** BC-4.01.002 — Unknown flag renders one-line error, exit 0, never
  blank (incl. leftover --subagent).
- **Partial coverage:** BC-4.01.001 (statusline exits 0 for any argv).
- **Invariant verified:** DI-008 (unknown flags OD-112 included in the never-blank
  ladder). Owner ruling OD-112.

## Property Class and Verification Method

- **Class:** safety.
- **Method:** fuzz — `go test -fuzz` over argv vectors (primitive string sequences
  through the dispatcher scan), plus the BC-4.01.002 canonical table (EC-001..EC-008
  including `--` and bare `-` rows), asserting exact stdout bytes, exit code, and
  precedence over the config-error line.
- **Honesty:** testable-only (CLI shell); the fuzz oracle is the BC-4.01.002 grammar
  (first-flag rule + `--`/`-` precedence) pinned by the canonical table.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Fuzz | `go test -fuzz`, `cmd/hylo` | budget-bounded | argv vectors through the flag scan |
| Canonical table | Go test | yes — EC-001..EC-008 | flag/`--`/`-`/positional grammar |

## Proof Harness Skeleton

```go
func TestStatusline_UnknownFlag(t *testing.T) { // BC-4.01.002 named test
    for _, argv := range [][]string{
        {"--subagent"}, {"foo", "--a", "--b"}, // error rows: first flag named
        {"--", "--subagent"},                  // after --: normal render (EC-004)
        {"-"},                                 // bare -: positional (EC-005)
    } {
        stdout, _, exit := runStatusline(argv, getenv, stdin, files)
        assertMatchesBCEitherExactOrNormalRender(t, argv, stdout, exit)
    }
}

func FuzzStatusline_UnknownFlag(f *testing.F) {
    f.Fuzz(func(t *testing.T, flags ...string) {
        stdout, _, exit := runStatusline(flags, getenv, stdin{}, files{})
        // oracle: if any arg before -- starts with "-" and != "-", stdout is
        // exactly the one-line error; otherwise a normal (non-blank) render.
        assertUnknownFlagGrammar(t, flags, stdout, exit)
    })
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table (belongs to `cmd/hylo` tests, ARCH-01 mapping);
named per the BC as `TestStatusline_UnknownFlag` + fuzz target
`FuzzStatusline_UnknownFlag`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Small | argv shapes, not values |
| Proof complexity | N/A | enumeration |
| Tool support | Full | Go tables |
| Estimated proof time | Hours | includes precedence rows vs E-CFG-001 |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
