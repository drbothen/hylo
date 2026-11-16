---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-01-binary-cli.md, behavioral-contracts/ss-04/BC-4.01.001.md, behavioral-contracts/ss-02/BC-2.03.001.md, behavioral-contracts/ss-02/BC-2.03.002.md, prd-supplements/error-taxonomy.md]
input-hash: "c1ecf7f"
traces_to: prd.md
source_bc: BC-4.01.001
bcs: [BC-4.01.001, BC-4.01.003, BC-2.03.001, BC-2.03.002]
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

# VP-004: Verb-scoped exit-code surface is closed and exhaustively table-tested

## Property Statement

The exit code of `hylo` is a total function over the closed verb-scoped table: 0 for
every `statusline` run (happy, degraded, config-error, unknown-flag), `version`, and
`config path`; 0 for `config validate` on valid config and 1 on invalid; 2 for usage
errors on non-statusline verbs with the golden usage text on stderr. No verb/state pair
exists outside the table, and `runStatusline` cannot propagate a non-zero code.

## Source Contract

- **Primary BC:** BC-4.01.001 — Dispatch statusline / version / config; statusline
  exits 0 for any argv.
- **Partial coverage:** BC-4.01.003 (version string chain), BC-2.03.001 (validate
  exits non-zero on D4-EX-3 errors), BC-2.03.002 (config path prints three paths).
- **Invariant verified:** DI-008 antecedent (non-zero exits only in validate/usage/
  harness contexts, per ARCH-00 Principle 4); AD-11 closed-table consequence.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — the full verb x state table with golden files
  (`usage.golden`), plus the version-chain fallback table (ldflags stamp -> VCS -> dev).
- **Honesty:** testable-only. The table is the proof object; exhaustiveness follows
  from the dispatcher being a closed switch (statically checkable, ARCH-01).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test + golden | Go test, `cmd/hylo` | yes — closed verb/state table | every verb x validity state |

## Proof Harness Skeleton

```go
func TestExitSurface_ClosedTable(t *testing.T) {
    for _, tc := range ExitTable { // {verb, args, env, validConfig} -> {exit, golden}
        stdout, stderr, exit := runHylo(tc.Verb, tc.Args, tc.Env, tc.Stdin, tc.Valid)
        if exit != tc.WantExit { t.Fatalf("%s: exit=%d", tc.Name, exit) }
        if tc.Golden != "" { assertGoldenBytes(t, tc.Golden, stderr) }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table (CLI-scope, ARCH-01 mapping); named here as
`TestExitSurface_ClosedTable`; usage text pinned by `cmd/hylo/testdata/usage.golden`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Tiny | 5 verbs x 2-3 states |
| Proof complexity | N/A | closed switch |
| Tool support | Full | golden files |
| Estimated proof time | Hours | version-chain rows included |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
