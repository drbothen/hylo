---
document_type: architecture-section
level: L3
section: "binary-cli"
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-18T01:00:00Z
phase: 1b
inputs: [prd.md, prd-supplements/interface-definitions.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "bf7d2d7"
---

# ARCH-01 — Binary & CLI (`cmd/hylo`)

> One static binary, subcommand dispatch (PLAN §6). P1 verbs: `statusline`, `version`,
> `config validate`, `config path`. Classification: **effectful shell** — argument
> decoding, writer wiring, `os.Exit`; zero render logic.

## Component & interfaces

```go
// main.go — the only os.Exit site
func main() { os.Exit(run(os.Args[1:], envOS{}, os.Stdin, os.Stdout, os.Stderr)) }

// EnvVars is the injected environment seam (AD-10, amended pass 2): enumeration
// included, so the unknown-HYLO_* sweep (BC-2.01.001 PC-6) and the
// HYLO_BACKENDS_<i>_* discovery (BC-2.01.002 PC-4/PC-6) run against fakes in tests,
// and "set but empty" is distinguishable from "unset" (BC-2.01.002 PC-3: empty list
// value vs default). Never a bare func(string) string.
type EnvVars interface {
    Lookup(name string) (value string, ok bool) // ok=false => unset; ok=true + "" => set-but-empty
    Names() []string                            // full environ listing (os.Environ()-backed in main)
}

// run dispatches on verb; unknown verb or bad args => usage.golden on stderr, exit 2.
func run(args []string, env EnvVars, stdin io.Reader, stdout, stderr io.Writer) int
func runStatusline(env EnvVars, stdin io.Reader, stdout, stderr io.Writer) int // always 0
func runVersion(stdout io.Writer) int                                         // 0
func runConfigValidate(env EnvVars, stdout, stderr io.Writer) int              // 0 | 1
func runConfigPath(args []string, env EnvVars, stdout, stderr io.Writer) int   // 0 | 2
```

Dispatch order is contractual (BC-4.01.001, BC-4.01.002, interface-definitions.md):
verb parse -> for `statusline` only: exact-match `--subagent` routing -> unknown-flag
scan -> `statusline.Main` -> exit 0. The exact argument `--subagent` selects the
subagent panel renderer before any flag or config processing (OD-155, superseding
OD-14; BC-1.07.001..008): when it is an element of argv, the panel produces all stdout
and the main render never runs; the panel is gated by `statusline.subagent.enabled`
(default true = legacy, BC-1.07.002). Otherwise `statusline` takes no flags in P1:
any argument starting with `-` (except a bare `-`, which is positional, and a bare
`--`, after which arguments are ignored) renders
`\e[90mhylo: unknown flag <flag>\e[0m\n`, exit 0, **checked before config resolution**
(OD-112; E-CLI-001 outranks E-CFG-001). Stdlib `flag` with `ExitOnError` is banned on
this path — it would exit 2 with a blank line (design doc tension T8; resolved by
OD-112: adapt or hand-roll the scan).

### Decision: exit-code surface is closed and verb-scoped

- **Context:** legacy exits non-zero with blank output on import errors; the client
  contract requires >= 1 byte and exit 0 from every statusline run (DI-008, NFR-002).
- **Options considered:** (1) process-wide never-non-zero — breaks `config validate`;
  (2) per-verb exit contracts with a closed table — matches the ruler TOM-side exits.
- **Decision:** option 2. Exit 0: all statusline runs (happy, degraded, config-error,
  unknown-flag), `version`, `config path`, `config validate` when valid. Exit 1:
  `config validate` on invalid config (E-VAL-001, plain reasons, no SGR). Exit 2: usage
  errors on non-statusline verbs (E-CLI-002, golden text `cmd/hylo/testdata/usage.golden`).
  Non-zero harness exits never occur inside `hylo` (E-HAR-001 is the harness process).
- **Rationale:** one closed table (error-taxonomy.md) is testable exhaustively; a global
  rule cannot express validate's non-zero.
- **Consequences:** `runStatusline` literally cannot propagate an error code; the guard
  owns the degraded line; `cp-x03` (degraded-write failure) still exits 0 (OD-136).
- **Verification feasibility:** all exits are stdout/exit-code byte tables — **testable
  only** (CLI shell), pinned by golden files and per-verb table tests; the pure pieces
  they call are covered under their own sections.

### Decision: version string chain

**Context/decision:** `hylo version` prints `hylo <version>`; version injected at build
via `-ldfs -X`, falling back to VCS stamp, then `dev` (BC-4.01.003; D12 releases tag it).
**Rationale:** keeps reproducible builds (design doc §6.7); **feasibility:** pure table
test on the chain, with the stamp itself testable-only.

## `hylo config path` (OD-132, OD-165)

Prints three lines in fixed order with fixed labels: `config:`, `cache:`, `state:`,
resolved as `--config` flag, then `HYLO_CONFIG`, then `internal/platform` per-OS defaults
(ARCH-05). `~` expanded (OD-61). The printed values are the **effective paths** (OD-165)
— exactly the resolutions the running binary uses, with the same overrides the status
line honors (cache/state lines resolve per BC-3.01.001), so `config path` can never
disagree with actual use. Paths are computed by `platform`, never assembled here.

## Mapping

- BC-4.01.001 -> `run`/`runStatusline`; BC-4.01.002 -> flag scan; BC-4.01.003 ->
  `runVersion`; BC-2.03.001 -> `runConfigValidate` (reuses `config.Load` errors verbatim);
  BC-2.03.002 -> `runConfigPath`.
- Criticality MEDIUM (>= 80% kill rate, module-criticality.md). Every rule above gets a
  table test; usage.golden pins the usage text byte-for-byte.
