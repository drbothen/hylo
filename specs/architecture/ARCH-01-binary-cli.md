---
document_type: architecture-section
level: L3
section: "binary-cli"
version: "1.8"
status: draft
producer: architect
timestamp: 2026-11-21T18:00:00Z
phase: 1b
inputs: [prd.md, prd-supplements/interface-definitions.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "f34b208"

---

# ARCH-01 — Binary & CLI (`cmd/hylo`)

> One static binary, subcommand dispatch (PLAN §6). P1 verbs: `statusline`, `version`,
> `config validate`, `config path`. Classification: **effectful shell** — argument
> decoding, writer wiring, `os.Exit`; zero render logic.

## Component & interfaces

```go
// main.go — the only os.Exit site
func main() { os.Exit(run(os.Args[1:], platform.NewEnvVars(), os.Stdin, os.Stdout, os.Stderr)) }
// platform.NewEnvVars() is the platform-provided, GOOS-selected EnvVars implementation
// (ARCH-05 matcher flavors; NT case-insensitive matching on Windows). main is the ONLY
// site that enumerates the real process environment; every other component receives the
// seam. The earlier local envOS{} wiring conflicted with the platform-provided
// implementation (pass-7 A03, orchestrator call 4).

// EnvVars is the injected environment seam (AD-10, amended pass 2): enumeration
// included, so the unknown-HYLO_* sweep (BC-2.01.001 PC-6) and the
// HYLO_BACKENDS_<i>_* discovery (BC-2.01.002 PC-4/PC-6) run against fakes in tests,
// and "set but empty" is distinguishable from "unset" (BC-2.01.002 PC-3: empty list
// value vs default). Never a bare func(string) string.
// DECLARED ONCE as platform.EnvVars in internal/platform (ARCH-05 — single home,
// ADV-P9-A12); cmd/hylo and internal/statusline consume the type, they do not
// re-declare it. The platform.NewEnvVars() constructor above is its GOOS-selected
// implementation (NT case-insensitive matching on Windows).
type EnvVars = platform.EnvVars // type alias — no second declaration (ADV-P9-A12)

// run dispatches on verb; unknown verb or bad args => usage.golden on stderr, exit 2.
func run(args []string, env EnvVars, stdin io.Reader, stdout, stderr io.Writer) int
func runStatusline(env EnvVars, stdin io.Reader, stdout, stderr io.Writer) int // always 0

// runStatuslineSubagent is the OD-155 subagent panel entry point (BC-1.07.001,
// pass-3 A02). It receives the FULL statusline argument slice — routing matches the
// exact element "--subagent" anywhere in it, at any index, including after a bare
// "--" terminator. Resolves config itself (OD-168: config IS loaded on the subagent
// path); on config error: ZERO bytes on stdout, the FULL E-CFG-001 reason list on
// stderr (one line per reason, registry order — the same surface as the main path;
// pass-5 A08), exit 0.
func runStatuslineSubagent(args []string, env EnvVars, stdin io.Reader, stdout, stderr io.Writer) int

func runVersion(stdout io.Writer) int                                        // 0
func runConfigValidate(env EnvVars, stdout, stderr io.Writer) int             // 0 | 1
func runConfigPath(args []string, env EnvVars, stdout, stderr io.Writer) int  // 0 | 1 | 2 (BC-2.03.002: 1 when a directory cannot be determined — pass-5 A01)
```

Dispatch order is contractual (BC-4.01.001, BC-4.01.002, interface-definitions.md):
verb parse -> for `statusline` only: exact-match `--subagent` routing -> unknown-flag
scan -> `statusline.Main` -> exit 0. The exact argument `--subagent` selects the
subagent panel renderer before the unknown-flag scan and the MAIN config step (OD-155,
superseding
OD-14; BC-1.07.001..008; pass-12 A10 wording — the subagent path then resolves config
ITSELF before evaluating the panel gate, OD-168, below, so "before any config
processing" would be false): when it is an element of args — at ANY index, including
after a bare `--` (pass-3 A01 ruling restatement: the flag is matched on the whole
argv tail, so `hylo statusline -- --subagent` routes to the panel, superseding the
BC-4.01.002 EC-004 "positional data" reading) — `runStatuslineSubagent` produces all
stdout and the main render never runs; the unknown-flag scan never runs either.
Config on the subagent path (OD-168, pass-3 A02): the subagent entry point resolves
config itself before evaluating the panel gate — the panel needs
`statusline.subagent.enabled` (BC-1.07.002) and `backends[0].model_prefixes`
(BC-1.07.006) — so a config error in `--subagent` mode prints ZERO bytes on stdout
(NDJSON-only surface) and the full E-CFG-001 reason list on stderr (one line per
reason, registry order; pass-5 A08), exit 0; the grey
stdout config-error line never applies in `--subagent` mode. With valid config the
panel is gated by `statusline.subagent.enabled` (default true = legacy,
BC-1.07.002; disabled = zero bytes, exit 0). Otherwise `statusline` takes no flags in
P1: any argument starting with `-` (except a bare `-`, which is positional, and a
bare `--`, which ends only the flag SCAN — trailing arguments are ignored by the scan
but still visible to `--subagent` routing, which precedes it) renders
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
  unknown-flag), `version`, `config path` when all three directories resolve, `config
  validate` when valid. Exit 1: `config validate` on invalid config (E-VAL-001, plain
  reasons, no SGR) and `config path` when a directory cannot be determined (BC-2.03.002
  PC-3, EC-008/010/011 — the verb's contract is three printed paths, so an unresolvable
  directory is a failure, not a degradation; pass-5 A01). Exit 2: usage
  errors on non-statusline verbs (E-CLI-002, golden text `cmd/hylo/testdata/usage.golden`).
  Non-zero harness exits never occur inside `hylo` (E-HAR-001 is the harness process).
- **Rationale:** one closed table (error-taxonomy.md) is testable exhaustively; a global
  rule cannot express validate's non-zero.
- **Consequences:** `runStatusline` literally cannot propagate an error code; the guard
  owns the degraded line; `cp-x03` (degraded-write failure) still exits 0 (OD-136); in
  `--subagent` mode a config error likewise exits 0 with zero stdout bytes (OD-168),
  so the panel surface stays NDJSON-only (pass-3 A02). OD-172 extends `cp-x03` to the
  panel's row writes: a stdout write failure while printing subagent rows stops writing
  and exits 0, with no degraded-line attempt (OD-172; no new exclusion id).
- **Verification feasibility:** all exits are stdout/exit-code byte tables — **testable
  only** (CLI shell), pinned by golden files and per-verb table tests; the pure pieces
  they call are covered under their own sections.

### Decision: version string chain

**Context/decision:** `hylo version` prints `hylo <version>`; version injected at build
via `-ldflags -X`, falling back to VCS stamp, then `dev` (BC-4.01.003; D12 releases tag it).
**Rationale:** keeps reproducible builds (design doc §6.7); **feasibility:** pure table
test on the chain, with the stamp itself testable-only.

## `hylo config path` (OD-132, OD-165)

Prints three lines in fixed order with fixed labels: `config:`, `cache:`, `state:`,
resolved as `--config` flag, then `HYLO_CONFIG`, then `internal/platform` per-OS defaults
(ARCH-05). `~` expanded (OD-61). The printed values are the **effective paths** (OD-165)
— exactly the resolutions the running binary uses, with the same overrides the status
line honors (cache/state lines resolve per BC-3.01.001), so `config path` can never
disagree with actual use. Paths are computed by `platform`, never assembled here.
Exit surface (BC-2.03.002, pass-5 A01): exit 0 when all three lines print; exit 1 when
any of the three directories cannot be determined (EC-008/010/011); exit 2 is usage
errors only.

## Fragment anchors (pass-4 A01; stable targets for BC-body fragment links)

BC bodies link fragments like `architecture/ARCH-01-binary-cli.md#dispatch`; the four
anchors below are the complete, closed set for this section — new BC fragment links
must target one of these.

<a id="dispatch"></a>
<a id="statusline-args"></a>
<a id="config"></a>
<a id="version"></a>

| Anchor | Target |
|---|---|
| `#dispatch` | the "Dispatch order is contractual" paragraph: verb parse → `--subagent` routing → unknown-flag scan → `statusline.Main` → exit 0 |
| `#statusline-args` | the P1 `statusline` argument rules in the same paragraph (no flags; unknown-flag line; bare `-` positional; bare `--` ends only the scan; `ExitOnError` ban) |
| `#config` | the `hylo config path` section (OD-132, OD-165) |
| `#version` | the "Decision: version string chain" section (BC-4.01.003) |

## Mapping

- BC-4.01.001 -> `run`/`runStatusline`; BC-4.01.002 -> flag scan; BC-4.01.003 ->
  `runVersion`; BC-2.03.001 -> `runConfigValidate` (reuses `config.Load` errors verbatim);
  BC-2.03.002 -> `runConfigPath`; BC-1.07.001 -> `runStatuslineSubagent` (argv routing +
  self-contained config resolution per OD-168, panel body per ARCH-03 `subagent.go`).
- Criticality MEDIUM (>= 80% kill rate — the Phase 6 mutation target, not a P1 gate;
  OD-158; module-criticality.md). Every rule above gets a
  table test; usage.golden pins the usage text byte-for-byte.
