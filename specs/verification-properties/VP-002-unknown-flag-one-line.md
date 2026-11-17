---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T06:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-01-binary-cli.md, behavioral-contracts/ss-04/BC-4.01.002.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "4bb618d"
traces_to: prd.md
source_bc: BC-4.01.002
bcs: [BC-4.01.002, BC-4.01.001, BC-1.07.001]
module: cmd/hylo
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — fuzz argv encoded as NUL-separated []byte (A2-11); BC-4.01.001 added to bcs, matching the body's partial-coverage claim (A2-04); BC-1.07.001 dispatch-grammar rows added (exact-member --subagent routing and its --subagent=1 unknown-flag complement)", "1.3 2026-11-18T06:00:00Z: Source Contract title quote synced to the current BC-4.01.002 H1 (no --subagent enrichment; adv-p2 sync SC-06 aftermath); harness comment fixed — exact-member --subagent routes to the subagent renderer, it is the substring/suffixed forms that error"]
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
render (BC-4.01.001 — verified here on the flag-less/positional branch of the same
dispatcher). Routing rows (BC-1.07.001, OD-155): the exact argument `--subagent`, as an
element of `argv[1:]` at any index, routes to the subagent renderer before flag
handling, regardless of other unknown flags; substring or suffixed forms (`--subagent=1`,
`-subagent`) are NOT matches and fall through to the main path, where they hit the
unknown-flag grammar above; a doubled `--subagent` behaves as one occurrence. The scan
runs before
config resolution (E-CLI-001 outranks E-CFG-001); stdlib `flag` with `ExitOnError`
(exit 2, blank line) never runs on this path.

## Source Contract

- **Primary BC:** BC-4.01.002 — Unknown flag renders one-line error, exit 0, never
  blank.
- **Partial coverage:** BC-4.01.001 (statusline exits 0 for any argv — the flag-less/
  positional branch of this dispatcher), BC-1.07.001 (exact-member `--subagent` routing
  grammar and its unknown-flag complement; the dispatch rows below realize its
  exactly-one-renderer invariant observationally).
- **Invariant verified:** DI-008 (unknown flags OD-112 included in the never-blank
  ladder). Owner ruling OD-112.

## Property Class and Verification Method

- **Class:** safety.
- **Method:** fuzz — `go test -fuzz` over argv vectors (a primitive `[]byte` argument
  decoded into an argv by splitting on NUL, then run through the dispatcher scan), plus
  the BC-4.01.002 canonical table (EC-001..EC-008
  including `--` and bare `-` rows) extended with the BC-1.07.001 routing rows, asserting exact stdout bytes, exit code, and
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
        {"foo", "--a", "--b"},                 // error row: first flag named
                                               // (exact-member --subagent routes to the subagent renderer — see routing rows below)
        {"--", "--subagent"},                  // after --: normal render (EC-004)
        {"-"},                                 // bare -: positional (EC-005)
        // BC-1.07.001 routing rows: exact-member --subagent routes before flags
        {"statusline", "--subagent"},           // routes to subagent renderer
        {"statusline", "x", "--subagent"},      // position-independent (PC-4)
        {"statusline", "--subagent", "--subagent"}, // EC-001: doubled == once
        {"--subagent=1"},                       // NOT a match: unknown-flag line (OD-112/OD-155)
        {"-subagent"},                          // NOT a match: unknown-flag line
    } {
        stdout, _, exit := runStatusline(argv, getenv, stdin, files)
        assertMatchesBCEitherExactOrNormalRender(t, argv, stdout, exit)
    }
}

func FuzzStatusline_UnknownFlag(f *testing.F) {
    f.Fuzz(func(t *testing.T, joined []byte) { // A2-11: []byte, split into argv
        argv := strings.Split(string(joined), "\x00") // NUL-separated argv encoding
        stdout, _, exit := runStatusline(argv, getenv, stdin{}, files{})
        // oracle: if any arg before -- starts with "-" and != "-", stdout is
        // exactly the one-line error; if argv[1:] contains the exact element
        // "--subagent", the subagent renderer produced all stdout (BC-1.07.001);
        // otherwise a normal (non-blank) render.
        assertUnknownFlagGrammar(t, argv, stdout, exit)
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
