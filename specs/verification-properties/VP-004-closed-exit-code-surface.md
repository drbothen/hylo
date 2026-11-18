---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-20T08:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-01-binary-cli.md, behavioral-contracts/ss-04/BC-4.01.001.md, behavioral-contracts/ss-02/BC-2.03.001.md, behavioral-contracts/ss-02/BC-2.03.002.md, prd-supplements/error-taxonomy.md]
input-hash: "40e3681"
traces_to: prd.md
source_bc: BC-4.01.001
bcs: [BC-4.01.001, BC-4.01.003, BC-2.03.001, BC-2.03.002, BC-1.07.001]
module: cmd/hylo
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-20T08:00:00Z: pass-8 fixes (A2-15, A2-07) — the usage-error norm names bare `hylo` (EC-004) and an unknown verb (EC-005, e.g. `hylo status`) exit 2 beside the non-statusline verbs (BC-4.01.001 PC-4), and the legal statusline states include BOTH entries (subagent: zero or more LF-terminated NDJSON lines, zero bytes allowed, config error = zero stdout bytes per OD-168, BC-1.07.001); the BC-4.01.001 for-all row gained a matching property leg: fuzz over all argv/env/stdin with args[0]==\"statusline\" (FuzzStatuslineExitSurface), method and Proof Method table updated; bcs: gains BC-1.07.001 (subagent NDJSON wire grammar of the subagent leg)"]
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
every `statusline` run in EITHER entry (happy, degraded, config-error, unknown-flag —
main entry; the `--subagent` entry with its own legal states: zero or more
LF-terminated NDJSON lines, zero bytes allowed, a config error emitting zero stdout
bytes with the diagnostic on stderr per OD-168, BC-1.07.001 wire grammar) and
`version`;
`config path` exits 0 with the three path lines, or 1 when a requested directory is
unavailable (stderr detail per unavailable line, BC-2.03.002 EC-008/EC-010);
`config validate` exits 0 on valid config and 1 on invalid; `help`/`-h`/`--help` print
the usage text on stdout, exit 0 (BC-4.01.001 PC-5); 2 for every dispatch-level usage
error — bare `hylo` with no args (EC-004), an unknown verb (EC-005, e.g. `hylo
status`), and usage errors on non-statusline verbs — with the golden usage text on
stderr (BC-4.01.001 PC-4). No verb/state pair exists
outside the table, and `runStatusline` cannot propagate a non-zero code. For all argv
with `args[0]=="statusline"`, all env and all stdin — the BC-4.01.001 for-all row —
the exit is 0: MAIN-mode stdout is non-empty and LF-terminated; SUBAGENT-mode stdout
is zero or more LF-terminated NDJSON lines, zero bytes allowed.

## Source Contract

- **Primary BC:** BC-4.01.001 — Dispatch statusline / version / config; statusline
  exits 0 for any argv.
- **Partial coverage:** BC-4.01.003 (version string chain), BC-4.01.001 PC-5
  (`help`/`-h`/`--help` usage on stdout, exit 0), BC-2.03.001 (validate exits non-zero
  on D4-EX-3 errors), BC-2.03.002 (config path prints three paths; exit 1 when a
  directory is unavailable, EC-008/EC-010).
- **Invariant verified:** DI-008 antecedent (non-zero exits only in validate/usage/
  harness contexts, per ARCH-00 Principle 4); AD-11 closed-table consequence.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — the full verb x state table with golden files
  (`usage.golden`), plus the version-chain fallback table (ldflags stamp -> VCS -> dev);
  plus the BC-4.01.001 for-all property leg as a fuzz harness over arbitrary argv /
  env / stdin shapes with `args[0]=="statusline"`: exit 0 always, MAIN-mode stdout
  non-empty LF-terminated, SUBAGENT-mode stdout zero or more LF-terminated NDJSON
  lines with zero bytes legal (BC-1.07.001; the subagent NDJSON check of the BC row).
- **Honesty:** testable-only. The table is the proof object; exhaustiveness follows
  from the dispatcher being a closed switch (statically checkable, ARCH-01).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test + golden | Go test, `cmd/hylo` | yes — closed verb/state table | every verb x validity state |
| For-all fuzz (`FuzzStatuslineExitSurface`) | `go test -fuzz`, `cmd/hylo` | bounded by the closed dispatcher switch | all argv/env/stdin with `args[0]=="statusline"`, both entries |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestExitSurface_ClosedTable(t *testing.T) {
    for _, tc := range ExitTable { // {verb, args, env, validConfig} -> {exit, stdout golden, stderr golden}
        stdout, stderr, exit := runHylo(tc.Verb, tc.Args, tc.Env, tc.Stdin, tc.Valid)
        if exit != tc.WantExit { t.Fatalf("%s: exit=%d", tc.Name, exit) }
        if tc.Stdout != "" { assertGoldenBytes(t, tc.Stdout, stdout) } // help/-h/--help usage rows
        if tc.Golden != "" { assertGoldenBytes(t, tc.Golden, stderr) }
    }
}

func FuzzStatuslineExitSurface(f *testing.F) { // BC-4.01.001 for-all row (A2-07): all
    // argv with args[0]=="statusline", all env, all stdin — exit 0; MAIN-mode stdout
    // non-empty LF-terminated; SUBAGENT-mode stdout zero or more LF-terminated
    // NDJSON lines, zero bytes allowed (BC-1.07.001; OD-168 for the config-error case).
    f.Fuzz(func(t *testing.T, args []string, env map[string]string, stdin []byte) {
        mainStdout, _, exit := runStatusline(append([]string{"statusline"}, args...), env, stdin)
        if exit != 0 { t.Fatalf("MAIN: exit = %d, want 0", exit) }
        if len(mainStdout) == 0 || mainStdout[len(mainStdout)-1] != '\n' {
            t.Fatal("MAIN: stdout empty or not LF-terminated")
        }
        subArgs := append([]string{"statusline", "--subagent"}, args...)
        subStdout, _, subExit := runStatusline(subArgs, env, stdin)
        if subExit != 0 { t.Fatalf("SUBAGENT: exit = %d, want 0", subExit) }
        if len(subStdout) > 0 && !isNDJSONRows(subStdout) { // zero bytes legal; wire grammar BC-1.07.001
            t.Fatal("SUBAGENT: stdout is not zero or more LF-terminated NDJSON lines")
        }
    })
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table (CLI-scope, ARCH-01 mapping); named here as
`TestExitSurface_ClosedTable` and the for-all fuzz `FuzzStatuslineExitSurface`;
usage text pinned by `cmd/hylo/testdata/usage.golden`.

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
