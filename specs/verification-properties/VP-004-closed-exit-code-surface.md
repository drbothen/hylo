---
document_type: verification-property
level: L4
version: "1.7"
status: draft
producer: architect
timestamp: 2026-11-24T16:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-01-binary-cli.md, behavioral-contracts/ss-04/BC-4.01.001.md, behavioral-contracts/ss-02/BC-2.03.001.md, behavioral-contracts/ss-02/BC-2.03.002.md, prd-supplements/error-taxonomy.md]
input-hash: "102a0f6"
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
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-20T08:00:00Z: pass-8 fixes (A2-15, A2-07) — the usage-error norm names bare `hylo` (EC-004) and an unknown verb (EC-005, e.g. `hylo status`) exit 2 beside the non-statusline verbs (BC-4.01.001 PC-4), and the legal statusline states include BOTH entries (subagent: zero or more LF-terminated NDJSON lines, zero bytes allowed, config error = zero stdout bytes per OD-168, BC-1.07.001); the BC-4.01.001 for-all row gained a matching property leg: fuzz over all argv/env/stdin with args[0]==\"statusline\" (FuzzStatuslineExitSurface), method and Proof Method table updated; bcs: gains BC-1.07.001 (subagent NDJSON wire grammar of the subagent leg)", "1.3 2026-11-20T12:00:00Z: pass-9 fixes (A2-12, A2-20) — the MAIN fuzz leg's generator domain excludes `--subagent` (a `--subagent` anywhere in argv routes the run to the subagent renderer, whose legal zero-byte output false-failed the MAIN non-empty check; legacy routes on `--subagent` anywhere in argv, SL:1240-1241); the fuzz sketch derives argv/env from byte blobs — Go fuzzing supports only primitive parameter types, not []string or map[string]string (A2-20)", "1.4 2026-11-18T17:50:00Z: pass-10 fix (A2-01, orchestrator call 9) — the `--subagent` entry's legal output set stated exactly (DI-008 carve-out): zero or more NDJSON lines OR, on a catalogued renderer fault (CP-A01..A05), the 29-byte non-JSON degraded line; zero bytes allowed (empty task list, unparseable/non-object stdin, OD-168 config error) — the former NDJSON-only oracle falsely failed a correct port whose fuzzed stdin drove a tokenCount ≥ 2**1024 OverflowError into the guard (SL:876-880 → SL:1243-1244); property statement, method bullet and sketch's SUBAGENT check aligned", "1.5 2026-11-18T21:00:00Z: pass-11 fix (A2-07) — the '`runStatusline` cannot propagate a non-zero code' claim given its faulting-stdout detection mechanism: VP-003's writer-seam legs (pass-11) inject a counting failing writer under a NORMAL render in both entries and assert exit 0, so a port returning exit 1 on a faulted normal-row write fails VP-003 rather than passing every VP; method bullet states the fuzz injects no I/O faults", "1.6 2026-11-22T03:00:00Z: pass-12 residual (item 4, call 15) — the CP-A04/A05 example trigger in the property statement is bounded: `tokenCount` reaches `_fmt_tokens` as a 309..4300-digit decimal literal; a longer literal raises ValueError at legacy's decode ({} → zero bytes, inside the wire-grammar leg), so the degraded-line example is reachable only in that range", "1.7 2026-11-24T16:00:00Z: pass-13 residual (item 3, orchestrator call 8) — the closed exit surface gains E-CLI-003: `hylo config path` exit 1 when a directory cannot be determined, minted by error-taxonomy (pass-13, A01) and listed by ARCH-00 Principle 4 as the one non-zero exit outside validate/usage/harness; the property statement and the Source Contract partial-coverage row cite the id and the EC-008/EC-010/EC-011/EC-012 anchors"]
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
LF-terminated NDJSON lines, zero bytes allowed (empty task list BC-1.07.004 PC6,
unparseable/non-object stdin BC-1.07.003, a config error emitting zero stdout
bytes with the diagnostic on stderr per OD-168), a catalogued renderer fault
(CP-A01..A05) ending in the shared 29-byte non-JSON degraded line (DI-008 carve-out,
BC-1.07.008); BC-1.07.001 wire grammar) and
`version`;
`config path` exits 0 with the three path lines, or 1 when a directory cannot be
determined (E-CLI-003, error-taxonomy's closed exit table — the ONE non-zero exit
outside validate/usage/harness; stderr detail per unavailable line,
BC-2.03.002 EC-008/EC-010/EC-011/EC-012);
`config validate` exits 0 on valid config and 1 on invalid; `help`/`-h`/`--help` print
the usage text on stdout, exit 0 (BC-4.01.001 PC-5); 2 for every dispatch-level usage
error — bare `hylo` with no args (EC-004), an unknown verb (EC-005, e.g. `hylo
status`), and usage errors on non-statusline verbs — with the golden usage text on
stderr (BC-4.01.001 PC-4). No verb/state pair exists
outside the table, and `runStatusline` cannot propagate a non-zero code — including
when the stdout write itself faults: VP-003's writer-seam legs (pass-11 A2-07)
inject a counting failing writer under a NORMAL (non-degraded) render in BOTH entries
and assert exit 0 (main: BC-1.01.001's VP-003 anchor row + ARCH-01 AD-11; subagent
rows: BC-1.07.008 EC-009 / OD-172), so a port returning exit 1 on a faulted
normal-row write fails VP-003. For all argv
with `args[0]=="statusline"` and no `--subagent` argument — the BC-4.01.001 for-all
row; the MAIN fuzz generator's domain EXCLUDES `--subagent` (A2-12: `--subagent`
anywhere in argv routes the whole run to the subagent renderer, legacy SL:1240-1241,
whose legal zero-byte output would false-fail the MAIN non-empty check) —
all env and all stdin, the exit is 0: MAIN-mode stdout is non-empty and LF-terminated;
SUBAGENT-mode stdout
is zero or more LF-terminated NDJSON lines, zero bytes allowed, or — on a catalogued
renderer fault (CP-A01..A05) — exactly the 29-byte non-JSON degraded line (DI-008
carve-out, BC-1.07.008; A2-01: fuzzed stdin reaches that state when a task's
`tokenCount` is an exact int ≥ 2**1024 carried as a 309..4300-digit decimal
literal (pass-12 residual, call 15: the CP-A04/A05 example trigger is bounded to
that range — a literal longer than 4300 digits raises ValueError at legacy's
decode, stdin decodes to {} and the refresh legally prints zero bytes, inside the
wire-grammar leg rather than the degraded line) —
`_fmt_tokens` catches only
TypeError/ValueError, SL:876-880, so the guard prints the line, SL:1243-1244 — and a
correct port therefore fails the former NDJSON-only fuzz).

## Source Contract

- **Primary BC:** BC-4.01.001 — Dispatch statusline / version / config; statusline
  exits 0 for any argv.
- **Partial coverage:** BC-4.01.003 (version string chain), BC-4.01.001 PC-5
  (`help`/`-h`/`--help` usage on stdout, exit 0), BC-2.03.001 (validate exits non-zero
  on D4-EX-3 errors), BC-2.03.002 (config path prints three paths; exit 1 when a
  directory cannot be determined — E-CLI-003, the closed exit table's one non-zero
  exit outside validate/usage/harness, EC-008/EC-010/EC-011/EC-012).
- **Invariant verified:** DI-008 antecedent (non-zero exits only in validate/usage/
  harness contexts, per ARCH-00 Principle 4); AD-11 closed-table consequence.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — the full verb x state table with golden files
  (`usage.golden`), plus the version-chain fallback table (ldflags stamp -> VCS -> dev);
  plus the BC-4.01.001 for-all property leg as a fuzz harness over arbitrary argv /
  env / stdin shapes with `args[0]=="statusline"`: exit 0 always, MAIN-mode stdout
  non-empty LF-terminated (generator excludes `--subagent`, A2-12), SUBAGENT-mode
  stdout zero or more LF-terminated NDJSON
  lines with zero bytes legal, or exactly the 29-byte degraded line on a catalogued
  renderer fault (CP-A01..A05, DI-008/BC-1.07.008; BC-1.07.001; the subagent output
  check of the BC row). The faulting-stdout slice of the table is evidenced by VP-003's
  writer-seam legs (pass-11 A2-07), not by this fuzz, which injects no I/O faults.
- **Honesty:** testable-only. The table is the proof object; exhaustiveness follows
  from the dispatcher being a closed switch (statically checkable, ARCH-01).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test + golden | Go test, `cmd/hylo` | yes — closed verb/state table | every verb x validity state |
| For-all fuzz (`FuzzStatuslineExitSurface`) | `go test -fuzz`, `cmd/hylo` | bounded by the closed dispatcher switch | all argv/env/stdin with `args[0]=="statusline"`, both entries (MAIN leg: no `--subagent`, A2-12) |

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
    // A2-20: Go fuzzing supports only primitive parameter types — argv and env are
    // derived in-body from byte blobs (argv split on NUL, env on LF "K=V" lines).
    f.Fuzz(func(t *testing.T, argBlob, envBlob, stdin []byte) {
        var args []string
        for _, a := range strings.Split(string(argBlob), "\x00") {
            if a != "" {
                args = append(args, a)
            }
        }
        if slices.Contains(args, "--subagent") {
            return // MAIN generator domain excludes --subagent (A2-12): any
            // --subagent in argv routes the run to the subagent renderer
            // (SL:1240-1241), whose legal zero-byte output would false-fail MAIN.
        }
        env := parseEnvBlob(envBlob) // LF-separated "K=V" lines; malformed lines skipped
        mainStdout, _, exit := runStatusline(append([]string{"statusline"}, args...), env, stdin)
        if exit != 0 { t.Fatalf("MAIN: exit = %d, want 0", exit) }
        if len(mainStdout) == 0 || mainStdout[len(mainStdout)-1] != '\n' {
            t.Fatal("MAIN: stdout empty or not LF-terminated")
        }
        subArgs := append([]string{"statusline", "--subagent"}, args...)
        subStdout, _, subExit := runStatusline(subArgs, env, stdin)
        if subExit != 0 { t.Fatalf("SUBAGENT: exit = %d, want 0", subExit) }
        // A2-01: zero bytes legal; a catalogued renderer fault ends in the 29-byte
        // degraded line (CP-A01..A05, DI-008/BC-1.07.008); otherwise the wire
        // grammar BC-1.07.001.
        if len(subStdout) > 0 && subStdout != degradedLine && !isNDJSONRows(subStdout) {
            t.Fatal("SUBAGENT: stdout outside the legal output set")
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
