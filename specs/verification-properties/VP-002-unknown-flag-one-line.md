---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-01-binary-cli.md, behavioral-contracts/ss-04/BC-4.01.002.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "b02f675"
traces_to: prd.md
source_bc: BC-4.01.002
module: cmd/hylo
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

# VP-002: Any argv on `hylo statusline` renders the one-line unknown-flag error, exit 0

## Property Statement

For every argv vector containing any argument beginning with `-` (except a bare `--`,
after which arguments are ignored) — including a leftover `--subagent` — `hylo
statusline` renders exactly `\e[90mhylo: unknown flag <flag>\e[0m\n` and exits 0. The
scan runs before config resolution (E-CLI-001 outranks E-CFG-001); stdlib `flag` with
`ExitOnError` (exit 2, blank line) never runs on this path.

## Source Contract

- **Primary BC:** BC-4.01.002 — Unknown flag renders one-line error, exit 0, never
  blank (incl. leftover --subagent).
- **Partial coverage:** BC-4.01.001 (statusline exits 0 for any argv).
- **Invariant verified:** DI-008 (unknown flags OD-112 included in the never-blank
  ladder). Owner ruling OD-112.

## Property Class and Verification Method

- **Class:** safety.
- **Method:** unit/table test — argv vectors crossed with config-valid/invalid states,
  asserting bytes, exit code, and precedence over the config-error line.
- **Honesty:** testable-only (CLI shell); the vector space is finite and small for the
  flag-shaped grammar, so the table is effectively exhaustive over arg shapes.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test | Go test, `cmd/hylo` | yes — argv shape grammar | every flag-shaped argv shape x config state |

## Proof Harness Skeleton

```go
func TestUnknownFlag_OneLineExitZero(t *testing.T) {
    for _, argv := range [][]string{{"--wat"}, {"--subagent"}, {"--subagent", "x"}, {"--", "x"}, {"ok", "--wat"}} {
        stdout, _, exit := runStatusline(argv, getenv, stdin, files)
        if exit != 0 || !bytes.Contains(stdout, unknownFlagPrefix) || len(stdout) == 0 {
            t.Fatalf("argv %v: exit=%d stdout=%q", argv, exit, stdout)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table (belongs to `cmd/hylo` table tests, ARCH-01 mapping);
named here as `TestUnknownFlag_OneLineExitZero`.

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
