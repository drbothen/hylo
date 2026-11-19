---
document_type: architecture-section
level: L3
section: "build-ci-release"
version: "1.15"
status: draft
producer: architect
timestamp: 2026-11-23T10:00:00Z
phase: 1b
inputs: [prd.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "e0b60d4"

---

# ARCH-08 — Build, CI, release

> Implemented by the phase-1-cicd-setup step from this design. Classification:
> infrastructure (workflow YAML, release tooling); its logic lives in the repo, not the
> binary.

## Build

- Go >= 1.26: go.mod pins `go 1.26.0` only, **no toolchain directive** (actual repo
  state, ADV-P2-A14; cicd-setup.md agrees; verified on disk this burst — the landed
  go.mod is `module github.com/drbothen/hylo` + `go 1.26.0` only) — with
  `go-version-file`, CI therefore
  installs 1.26.0, the oldest 1.26 patch, so the "Go 1.26.x leg" lacks later stdlib
  security fixes. Approved-in-spec remedy: add a `toolchain go1.26.x` line to go.mod
  (lands on main with the owner's approval; spec-only here). BC-6.04.001 Pre-2's
  "`toolchain` line" is THIS remedy — the approved-in-spec posture, not a statement
  that the landed go.mod already carries it (ADV-P11-D03 reconciliation); the floor
  leg's exact `go-version: 1.26.0` pin (ADV-P10-D09) tests the oldest patch with or
  without the line. ORDERING (ADV-P9-A06, amended by orchestrator call 6 pass-13:
  ACTIVATION IS SAME-CHANGE — govulncheck runs and reports as its own job on every
  change from the start, and it becomes a required check in the SAME change that
  adds go.mod's `toolchain` line — never promoted onto a no-patch toolchain):
  govulncheck reports stdlib advisories against the Go
  version actually used (crypto/tls and net are reachable through the metrics client),
  so activating the required check on a no-patch 1.26.0 toolchain either goes
  permanently red or ships binaries carrying known stdlib vulnerabilities; go.mod
  changes only when the owner asks. `CGO_ENABLED=0`,
  one static binary per OS. Version stamping via `-ldflags "-X main.version=..."` from
  the released tag; fallback VCS stamp, then `dev` (BC-4.01.003).
- **Dependency policy (AD-02):** P1 runtime deps = `golang.org/x/sys` only; stdlib first
  each-new-dependency-needs-a-reason (CLAUDE.md); the YAML library lands with the P4
  file layer (OD-107). Build-time-only tooling (generators, Storybook-like tools) is not
  a runtime dep. Each new dependency needs an ADR line in ARCH-INDEX.

## CI workflow design (phase-1-cicd-setup implements; BC-6.04.001)

```mermaid
flowchart LR
    PR["pull_request / push"] --> L["lint JOB (ubuntu-24.04): gofmt -l . — ONCE, required<br/>(lint runs gofmt ONLY; pass-13 call 6)"]
    PR --> GV["govulncheck JOB (ubuntu-24.04): its OWN job — runs and reports on EVERY change;<br/>becomes a required check in the SAME change that adds go.mod's toolchain line<br/>(pass-13 call 6, ADV-P13-A03)"] --> GVR["required check-run `govulncheck (required)`"]
    L --> M{"test matrix — FOUR required legs (pass-12 call 5):<br/>ubuntu-24.04 / macos-15 (arm64) / windows-2025<br/>(Go from go.mod's toolchain line)<br/>+ ubuntu FLOOR leg, go-version: 1.26.0 (ADV-P10-D09)"}
    M -->|"vet + staticcheck run on EVERY OS leg<br/>(per-OS build tags, P18); the plain test legs<br/>install NO interpreter (pass-12 call 5)"| T["go test -race (Linux/macOS) -count=1 ./...<br/>— oracle-dependent tests EXCLUDED via -skip $ORACLE_TESTS (pass-6 A12;<br/>FIVE members, ARCH-07)"]
    T --> TB["Tier B goldens (no Python: committed) — the plain test legs ONLY, they own<br/>the tier-b census (no separate Tier B job; pass-13 call 5)"]
    TB --> HL["gitleaks detect --log-opts=--all after checkout with fetch-depth: 0<br/>(rev set corrected pass-12 call 1) + category pattern scan"]
    HL --> DONE["plain-leg chain ends here — NO timing report on the plain legs<br/>(the plain legs skip TestTiming; only the timing job reports, pass-13 call 5)"]
    PYA["dedicated tier A JOB (THREE OS legs: ubuntu-24.04 / macos-15 / windows-2025;<br/>placeholder until Phase 3): EVERY leg installs setup-python 3.11.x (floating latest<br/>patch, OD-104/OD-185; harness self-checks measured constants, fail closed on drift)<br/>-> absolute path -> HYLO_PARITY_PYTHON (pass-5 A04: interpreter precedes go generate)<br/>-> EVERY leg prints the resolved CPython patch (pass-13 call 5, ADV-P13-A04); the<br/>ubuntu leg ADDITIONALLY runs the OD-170 staleness check: go generate ./... +<br/>git diff --exit-code (moves INTO this job, pass-12 call 5 — the plain test legs install<br/>no interpreter) -> -run $ORACLE_TESTS, the ONE authoritative run (pass-6 A12);<br/>timeout derived from corpus size (pass-13 call 18)"]
    TIMING["timing JOB (THREE OS legs): EVERY leg installs setup-python (CPython 3.11.x) and<br/>prints the resolved patch; -runs TestTiming — the per-OS timing report comes from<br/>THIS job, non-gating (OD-117; pass-13 call 5, ADV-P13-A16); timeout derived from<br/>corpus size (pass-13 call 18)"]
    COVJOB["coverage JOB (ubuntu-24.04, pass-7 A07; runs on EVERY PR — never probe-gated<br/>on internal/parity, ADV-P9-A04):<br/>go test -coverpkg=./internal/... over IN-PROCESS tests; oracle-dependent tests excluded<br/>via the ORACLE_TESTS pattern (ARCH-07, ADV-P11-A07);<br/>checks each gated package that EXISTS — prints `coverage: G of 3 gated packages present`;<br/>>= 95 percent statement coverage (Go's figure; the OD-158 gate name "line coverage"<br/>denotes it, ADV-P11-A03), S1/S5 packages (OD-158)"] --> REQ["required check-run `coverage`"]
    Nightly["schedule nightly (3 OSes, OD-149)"] --> TC["Tier C differential fuzz JOB — installs Python and -runs its ORACLE_TESTS member<br/>(pass-12 call 6; resolved patch printed), non-gating"]
```

- Race detector on Linux and macOS; the resolved Python patch version is recorded in
  Tier B golden metadata (RK-4). Ordering (pass-3 D22 as superseded pass-7 A08; diagram
  corrected pass-4 D08 and again pass-5 A04): GitHub Actions always sets
  `CI=true`. RULED (pass-6 A12, orchestrator call 13): the dedicated
  `parity tier A (live corpus)` job (timeout derived from corpus size — see the
  formula beside this section's Tier A bullets, pass-13 call 18) is the ONE
  authoritative Tier A
  run — the plain `go test` step EXCLUDES the ORACLE_TESTS selector (defined below), so
  the corpus never
  executes under the test job's tighter 30-minute cap: one run, one timeout. The
  pass-3 "Tier A runs live inside the plain `go test` step" ordering rationale is
  superseded (pass-7 A08). INTERPRETER PLACEMENT (pass-12 call 5, superseding the
  pass-7 "ubuntu staleness step" placement): setup-python + the
  `HYLO_PARITY_PYTHON` export survive ONLY in jobs that -run an ORACLE_TESTS member —
  the dedicated Tier A job (whose ubuntu leg ALSO runs the OD-170 staleness step,
  which moves out of the plain test leg), the timing job, and nightly Tier C — and
  each of those three prints the resolved CPython patch (BC-6.04.001 PC-6 / BC-6.04.002
  PC-2). OS SCOPE (orchestrator call 5, pass-13, ADV-P13-A04): the dedicated Tier A job
  and the timing job each run on ALL THREE OSes, and every leg of each installs
  setup-python (CPython 3.11) and prints the resolved patch — so live parity meets the
  Windows oracle child env (ARCH-07) and the arm64 FMA sites on every change. Legs
  without a Python consumer — all FOUR plain test legs (ubuntu, macos-15,
  windows-2025, and the ubuntu go-version 1.26.0 floor leg), the coverage job and the
  release job — install no interpreter. `go vet` and `staticcheck` run on every OS leg
  (per-OS build tags, P18); `gofmt -l` runs once in the ubuntu lint job; govulncheck
  runs in its own job (pass-13 call 6).
  Pin: setup-python installs **3.11.x** (python-version: '3.11', the latest patch —
  OD-104 stands; the pass-5 exact-3.11.7 pin is WITHDRAWN by OD-185, pass-6 A02).
  Because the measured constants (JSON depth limits, Unicode 14.0 tables) were taken on
  3.11.7, the harness SELF-CHECKS them against the resolved oracle at start — measuring
  the depth boundaries, `unicodedata.unidata_version`, and a NUL-keeps probe (both
  `posixpath.normpath('a\0b')` and `ntpath.normpath('a\0b')` must keep the NUL and
  return `'a\x00b'` — the gh-106242-era behavior BC-1.02.022 PC-3 pins; a pre-fix
  oracle silently truncates, orchestrator-measured on 3.11.7, ADV-P11-B08),
  failing closed on any mismatch
  and printing the resolved version — and Tier B golden metadata records the resolved
  patch (RK-4); a moved boundary fails the staleness check loudly instead of flapping
  silently on patch drift.
- **ORACLE_TESTS selector (ADV-P11-A07, pass-11 orchestrator call 8; member set
  corrected pass-12 call 6): ONE named
  mechanism defines the oracle-dependent test set — the harness pattern constant
  `ORACLE_TESTS = ^(TestParityTierA_Corpus|TestParityCanary_ShimLoaded|TestParityCacheSwap_FourCaches|TestParityTierC_DiffFuzz|TestTiming)$`
  (single home: ARCH-07's OD-145 name table). Every test needing the resolved Python
  oracle is a member — the FIVE named today (`TestParityTierC_DiffFuzz` drives both
  sides; `TestTiming` must report the CPython oracle median, BC-6.04.002 PC-2); a new
  oracle-dependent test EXTENDS the
  pattern rather than inventing a second mechanism. The plain test step, the coverage
  job and the release job pass `-skip $ORACLE_TESTS` (they install no interpreter;
  BC-6.01.001's fail-closed interpreter rule would otherwise go red under `CI=true`),
  and the three Python-installing jobs each -run their own member(s) — the dedicated
  Tier A job (`TestParityTierA_Corpus` + `TestParityCanary_ShimLoaded` +
  `TestParityCacheSwap_FourCaches`), the timing job (`TestTiming`), and the nightly
  fuzz job (`TestParityTierC_DiffFuzz`).
- **Generated-table staleness (OD-170):** the staleness step runs `go generate ./...` and then
  `git diff --exit-code` over the generated paths (Unicode 14.0 class tables and the
  pyfmt oracle tables, ARCH-06); any diff fails the leg — a stale committed table can
  never pass CI. It runs on ubuntu-24.04, INSIDE the dedicated Tier A job's ubuntu leg
  (placement corrected pass-12 call 5 — the plain test legs install no interpreter, so
  the step rides the one ubuntu job that already resolves the oracle; the earlier
  "ubuntu test leg" placement was the pass-5 A04 structure). The generators are
  `testdata/gen/*.py` under the pinned oracle.
- **Coverage gate (OD-158, pass-4 A13; restructured pass-7 A07, orchestrator call 12; gate
  scope per OD-193 and Tier A exclusion per pass-8 orchestrator call 1; every-PR scope and
  Tier A rationale per ADV-P9-A04/A07):**
  coverage is its OWN JOB on ubuntu-24.04 — required checks bind to check-runs
  (jobs), and a step inside a 3-OS matrix job emits no `coverage` check-run — and it
  produces the profile with `go test -count=1 -coverpkg=./internal/...` over the SAME
  Tier A exclusion the plain test step applies (the dedicated Tier A job is the one
  authoritative run). The job RUNS ON EVERY PR — it is never gated on `internal/parity`
  existing (the probe placeholder mechanism does not apply to it: parity is built LAST,
  so a parity-keyed gate would leave S1/S5 merging while a required check is skipped —
  ADV-P9-A04). The coverage job therefore installs NO interpreter (no Python
  consumer) and keeps a 30-minute timeout — at least the test job's 30 minutes, since
  it runs the same selection plus `-coverpkg` instrumentation (ADV-P9-A15): one run,
  one timeout. S1/S5 coverage comes
  from IN-PROCESS tests only — Tier A is excluded because Tier A needs the Python
  oracle, which the coverage job does not install (ADV-P9-A07; Tier A runs every case
  in-process and a subset as the built binary — ARCH-07 — so the earlier blanket
  "drives the built binary as a subprocess" premise is superseded) — hence Tier A runs
  do NOT count toward statusline coverage (gate scope per OD-193), while Tier B golden
  tests and the harness-machinery tests run IN-PROCESS under `./internal/...` with
  `-coverpkg=./internal/...` and DO credit `internal/statusline` (ADV-P11-A03 — the
  earlier blanket "parity runs do not count" was false). The job checks each
  gated package that EXISTS and prints `coverage: G of 3 gated packages present`;
  `G` is compared with the COMMITTED package manifest — a manifest package missing
  from the profile (renamed or moved) fails the job, and `G == 0` is allowed while
  NONE of the three gated packages exists — the committed manifest lists the gated
  packages PRESENT in the repo and grows as each lands, so `internal/platform` or
  other non-gated `internal/` packages never bind (skeleton era and the approved build
  order — `internal/platform` first, `internal/config` third, both BEFORE any gated
  package — leave early PRs legitimately at `G == 0`; ADV-P11-A02). It enforces
  **statement coverage
  >= 95 %** per package for S1 — `internal/statusline` and `internal/cost` — and
  S5 — `internal/pyfmt` (OD-158 stands unchanged per OD-193). `internal/cost` IS gated:
  SS-01 comprises `internal/statusline` and
  `internal/cost` (ARCH-INDEX Subsystem Registry) and module-criticality.md classes it
  CRITICAL by inheritance. `internal/parity` (S6) coverage is PROFILED AND REPORTED, not
  gated — OD-193 withdraws pass-7 call 12's addition of `internal/parity` to the gate.
  Figure derivation (ADV-P11-A03): Go measures STATEMENT coverage, not line coverage —
  the OD-158 gate name "line coverage" denotes Go's statement-coverage figure, computed
  per gated package from the MERGED cross-package `-coverpkg=./internal/...` profile as
  covered-statements-of-P / instrumented-statements-of-P, where the numerator counts
  statements of package P hit by ANY test in the selection (including tests FROM OTHER
  packages — the point of `-coverpkg`), reported per package by
  `go tool cover -func` over the single merged profile. The
  mutation kill-rate targets stay Phase 6 targets (OD-158) — this gate is statement
  coverage only. Designed behaviour; see cicd-setup.md for the landed-ci.yml lag note.
- **Timing (NFR-001, BC-6.04.002):** the timing job's legs each print the per-OS report — per corpus
  case, 1 discarded warm-up + **20 timed runs**, samples sorted per (case, step), nearest-rank
  p95 = **19th of the 20 sorted samples** (per nfr-catalog.md; with 5 samples the
  statistic degenerates to the maximum), p95 computed **per (case, step)** and binding per (case, step),
  no pooling; fake-VM handling time subtracted. SAMPLING UNIT (pass-12 call 4,
  superseding ADV-P11-A11's whole-sequence model; follows NFR-001 "render latency" and
  BC-6.04.002 PC-1 "never pooled across cases or steps"): ONE timed sample = ONE
  invocation of hylo (one render). A multi-step case is replayed from its committed
  seeds 1 warm-up + 20 times; EACH STEP IS TIMED ON ITS OWN, giving a 20-sample series
  per (case, step); the nearest-rank p95 is computed AND GATED per (case, step). No
  summing over steps. Between the 21 runs the case temp tree is RE-LAID from the committed
  seeds (seed caches, transcript base, clock base) — no cache or seed state carries
  across runs, so all 20 samples measure the same workload (cold-start replay from
  committed seeds; the pass-12 call-4 unit, orchestrator call 10 pass-13); within a run, later
  refreshes see earlier refreshes' cache writes, which is the production shape legacy
  exhibits too. The p95 <= 25 ms
  gate fails the build only with `HYLO_TIMING_GATE=1` (binds on the owner's Mac target).
  TIMEOUT DERIVATION (orchestrator call 18, pass-13, ADV-P13-A13; oracle term made
  explicit ADV-P14-A12): the timing job's
  timeout-minutes is derived from corpus size —
  headroom × (P × 21 × (T_ceiling + T_oracle_ceiling)) + fixed startup, where P is the
  corpus's (case, step) PAIR count — the sum over cases of that case's step count,
  a quantity defined even when cases differ in step count, and the same pair count the
  timing census asserts — T_ceiling is the measured per-hylo-run ceiling on the slowest
  leg, and T_oracle_ceiling is the measured per-oracle-invocation ceiling on the slowest
  leg: the report also samples the CPython oracle median the same 1-warm-up + 20-timed
  way per (case, step) (BC-6.04.002 PC-2), so the oracle spawns are charged per pair at
  their own measured ceiling, not lumped into a vague allowance. The headroom factor and
  both ceilings are committed named constants written BESIDE the formula in the
  workflow, sized so the
  job cannot be killed before its positive-coverage line prints (D15: a named constant
  with its rationale, not a magic number).
  CONDITIONAL EXEMPTION (OD-187 + OD-191, pass-7 A02, orchestrator call 3): the >512 KB
  fixture is exempt from the 25 ms p95 target, but the gate FAILS if its p95 exceeds
  100.0 ms — fails when p95 > 100.0 ms; exactly 100.0 ms passes at the 0.1 ms report
  resolution, equivalently the brief's "at most 100 ms" (judgment call: 4x the target, well under the refresh interval). The exempt
  fixture is identified by the validated case flag `timing_exempt: large-transcript` —
  exactly one case, and its transcript must exceed 512 KB (the corpus validator checks
  both) — and the report prints one line whenever the exemption is used.
- **Public-repo hygiene (policy 21, NFR-006):** committed fixtures synthetic-only;
  real inputs replayed from git-ignored `captures/`; the CI secret scan is
  `gitleaks detect --source . --log-opts="--all"` after checkout with
  `fetch-depth: 0` (rev set corrected pass-12 call 1, superseding ADV-P11-A04's
  two-ref set: the two-ref scan missed a pull request's own commits — reachable from
  neither `main` nor `factory-artifacts` on a PR run — and depended on bare branch
  names that checkout does not always create as locals; `--all` includes HEAD, so a
  PR run scans the PR head and every fetched ref, factory-artifacts included).
  Positive coverage: the scanned-commit count equals `git rev-list --count --all`
  (same rev set by construction). Matches the CLAUDE.md pre-push command; plus the
  category pattern scan; `TestCorpusHygiene` in-tree.
  The factory-artifacts branch is scanned by a scheduled (nightly) and manually
  dispatchable job running ON `main` that checks out the `factory-artifacts` ref and
  runs the category pattern scan over that checked-out tree — a push trigger on that
  branch can never fire (GitHub runs push workflows from the pushed commit's workflow
  files; factory-artifacts has no `.github/`), and the local pre-push hook stays the
  push-time guard (ADV-P10-A03, orchestrator call 16).
- **Positive coverage (ADV-P1-A09, process gap — implementation lands on main later with
  owner approval):** every regression-detector job must print a runtime-computed
  positive-coverage line and must treat "checked nothing" as failure, never as a pass:
  - Tier A: `parity: N cases, P case-step comparisons, M exclusions validated, K caches
    swapped` — job
    fails if `N == 0`, if `N` differs from the COMMITTED expected case count (a committed
    manifest of the corpus, ADV-P10-A04) or if `N` differs from the number of case
    directories found (same runtime census the exclusions check applies to `M`; a deleted
    case directory shrinks the runtime count and the runtime census equally, so the
    committed manifest is what catches a partially lost corpus — ADV-P2-A15); it fails
    the same way on the comparison PAIR count `P` — `P == 0`, `P` ≠ the committed
    expected pair count (sum over cases of each case's step count), or `P` ≠ the runtime
    (case, step) pair census — so a harness that compares only the first step of a
    multi-step case cannot pass (ADV-P14-A04); or if
    `K == 0` while any compared case declares swap seeds — the
    four-cache swap tier (BC-6.02.004, VP-019, R-001 mitigation) must be unable to check
    nothing and pass (pass-6 A10, call 13). TIMEOUT DERIVATION (orchestrator call 18,
    pass-13, ADV-P13-A13; oracle term made explicit ADV-P14-A12): the Tier A job's
    timeout-minutes is derived from corpus
    size — headroom × (P × R_runs × (T_ceiling + T_oracle_ceiling)) + fixed startup,
    where P is the corpus's (case, step) PAIR count (sum over cases of that case's step
    count — the same pair count the Tier A census asserts), T_ceiling the measured
    per-hylo-run ceiling on the slowest OS leg, R_runs the replays per (case, step),
    and T_oracle_ceiling the measured per-oracle-invocation ceiling on the slowest leg
    (the live leg drives both sides per (case, step), so the oracle spawn is charged
    per pair at its own measured ceiling); the headroom factor and both ceilings are
    committed named constants
    written BESIDE the formula in the workflow (D15: a named constant with its
    rationale, not a magic number) — sized so the job cannot die before its
    positive-coverage census line prints.
  - Tier B: `tier-b: N goldens compared` — printed by the plain test legs, which OWN
    the census (no separate Tier B job exists; orchestrator call 5, pass-13,
    ADV-P13-A14) — counts golden COMPARISONS MADE (ADV-P14-A03): each corpus case is
    compared exactly ONCE, against the host-OS variant when one exists and otherwise
    against the DEFAULT golden (the BC-6.03.001 PC-8 fallback — the norm on the Windows
    leg, where goldens A/B/C have no Windows variant) — and it fails if `N == 0`, if
    `N` differs from that leg's COMMITTED expected CASE count (a committed manifest,
    ADV-P10-A04), or if `N` differs from the runtime case-directory census — the
    comparison count equals the case count, never a windows-only file census. The
    native-set FILE census stays a separate checker over the committed golden files —
    `*.golden` on POSIX legs, `*.windows.golden` on the Windows leg (the same
    native-set discipline as `-update`, pass-5 D29): a lost `*.windows.golden` variant
    shrinks the file census and fails its manifest comparison, and a POSIX file census
    never recounts Windows variants as present (pass-7 A18; pass-5 A19: a partially
    lost golden set must not pass).
  - Tier C: `tier-c: N inputs per side, M oracle spawns`; the PR-side budget skip
    (`t.Skip` on unset/0 `HYLO_PARITY_FUZZSECONDS`) is allowed only because the job is
    non-gating — on the nightly schedule a 0/unset budget FAILS, it does not skip, and
    a scheduled run that compares `N == 0` inputs or spawns `M == 0` oracles FAILS
    (pass-6 A10, call 13; one clean nightly run is the P1 exit condition, OD-149).
  - Exclusion machinery / canary: `exclusions: M entries validated against the closed
    set` — `M` must equal the file's entry count; a missing exclusions file fails.
  - Go jobs (lint/test/vet): `go: K files scanned` counts source files, so
    it is paired with a **test-run line**: `go test: N tests run, S skipped` (test jobs
    only — lint and govulncheck run no tests) — fails if
    `N == 0`; the reported skip count keeps an all-skip suite visible (an all-skip pass
    standing in for coverage is investigated, not accepted — ADV-P2-A15). The skeleton-era
    empty-module guard prints `go: 0 Go files — guard path, NOT a vet/test pass` and is
    removed once Phase 3 lands sources (after which `K == 0` fails).
  - govulncheck (ADV-P14-A08): its positive-coverage line is `govulncheck: P packages
    analysed`, derived from what the TOOL actually analysed — the package count in
    govulncheck's JSON output — and COMPARED with the `go list ./...` package count
    (fails if `P == 0` or `P` differs from the list count): a repo source-file count
    (`go: K files scanned`) stays healthy when the scan's package pattern is narrowed,
    so it cannot serve as govulncheck's coverage assertion.
  - Pattern scan: `hygiene: K files scanned, H hits` — fails if `K == 0` (scan ran over
    nothing) AND if `H > 0` (a found hit is a failure, pass-3 A18), so the scan cannot
    pass while flagging hygiene terms.
  - Gitleaks (secret scan; ADV-P9-A05; positive comparison ADV-P10-A05; rev-set
    equality ADV-P11-A04, corrected pass-12 call 1): `gitleaks: N
    commits scanned` — fails if `N == 0` AND if `N` differs from
    `git rev-list --count --all` (the scan's `--log-opts="--all"` and the counter
    name the SAME rev set by construction — HEAD plus every fetched ref, so a PR
    run's own commits are inside both); a shallow or narrowed
    scan still
    covers at least one commit and exits 0, so the zero-check alone cannot detect it —
    the scanned count is COMPARED with the rev count across `--all`
    (fetch-depth: 0).
  - Coverage gate (pass-5 A16; fail scope per pass-8 orchestrator call 1; presence scope
    per ADV-P9-A04; manifest census ADV-P10-A04/A06; manifest growth + skeleton-era
    scope ADV-P11-A02): `coverage: G of 3 gated packages
    present; min statement coverage
    M% >= 95` — checks each gated package that EXISTS — `internal/statusline`,
    `internal/cost`, `internal/pyfmt` — against the COMMITTED package manifest and
    fails if a manifest package is missing from the profile (renamed or moved), if one
    exists and reports `[no statements]` (a package trivially "passing" coverage by
    having no statements is a failure, not a pass), or if `M < 95`; the committed
    manifest lists the gated packages present in the repo and GROWS as each lands, and
    `G == 0` is allowed while NONE of the three gated packages exists, whatever other
    `internal/` packages exist (early build-order PRs, ADV-P11-A02); the job runs on every PR
    and is never gated
    on `internal/parity` existing (ADV-P9-A04); `internal/parity`'s figure is reported for
    information and does not bind (OD-193).
  - Generated-table staleness (pass-5 A16): `generate: N generated paths checked,
    D regenerated` — fails if `N == 0` (a tree with zero `go:generate` directives
    checks nothing and must not pass) and if `D > 0`.
  - Timing report (pass-3 A16/D39; manifest ADV-P10-A04; interpreter placement pass-12
    call 5): the timing job INSTALLS PYTHON — it -runs the ORACLE_TESTS member
    `TestTiming`, whose report must include the CPython oracle median (BC-6.04.002
    PC-2) — and prints the resolved CPython patch. It executes the in-tree timing test
    (`go test ./internal/parity -run '^TestTiming$' -count=1`, `par/timing.go`) and
    prints `timing: N cases timed > 0` — fails if `N == 0` (an activated job reporting
    on zero cases must not pass), AND if `N` differs from the COMMITTED expected case
    count (the same manifest discipline Tier A applies — ADV-P10-A04) or from the
    corpus case census (timing 1 of N cases
    must not pass; pass-7 A20). The census counts (case, STEP) PAIRS
    (ADV-P14-A04, per pass-14 orchestrator call 15): the report's pair count `P` — the
    (case, step) pairs actually timed, each pair's 20-sample series intact — fails the
    job when `P == 0`, when `P` differs from the committed expected pair count (sum over
    cases of each case's step count), or when `P` differs from the runtime pair census,
    so timing only the first step of a multi-step case cannot pass.
  A skipped required check must never stand in for a pass: probe-gated placeholder jobs
  are added to branch protection's required set only when they can execute (Phase 3),
  and from then on every activation of the job must satisfy its coverage line —
  `skip` on a required detector is investigated, not accepted.
  R-004 mitigation restated for P1 (pass-6 A17 adjudication inside call 13; corrected
  pass-7 A09, orchestrator call 12; gate scope per OD-193): the
  HIGH-impact fake-pass-parity risk is mitigated in P1 NOT by the HIGH kill-rate tier
  (a Phase 6 target, OD-158) but by THIS census discipline plus the >= 95 %
  statement-coverage gate over the gated packages (S1/S5, named above) — the mitigation
  names only gates that exist; the referee must demonstrably check something on every
  run (the Tier A census line), the refereed render path must be demonstrably exercised
  by in-process tests, and the
  kill-rate tier takes over in Phase 6.

### Decision: gate on three OSes per change; release via GitHub Releases (AD-11)

- **Context:** D5 cross-platform from day one; D12 distribution.
- **Decision:** every change runs the full matrix; releases publish to GitHub Releases
  (binaries + checksums), Homebrew tap/Scoop/`go install` as follow-ups.
- **Rationale:** parity must hold on all OSes before generalization (D4 ordering);
  GitHub Releases keeps the P1 toolchain zero-budget.
- **Consequences:** windows-2025 leg pins the "not executed" Windows assumptions
  (ASM-005, prd-supplements/assumptions-register.md) and the D4-EX-1 fake-probe test; the nightly Tier C exit condition is ONE
  clean nightly run on all three OSes, 30 minutes per OS (`HYLO_PARITY_FUZZSECONDS=1800`,
  OD-149).
- **Verification feasibility:** workflow behavior is testable-only (CI leg observation);
  the in-tree part (corpus hygiene test, timing report printer) is table-tested; gitleaks
  cleanliness is a push-gate, not a proof.

- **Hardening posture (P19, pass-4 A17; restructured by orchestrator call 6, pass-13,
  ADV-P13-A03):** govulncheck is ITS OWN JOB in ci.yml — it runs and reports on every
  change (pull_request and push), and it becomes a required check in the SAME change
  that adds go.mod's `toolchain` line (activation-is-same-change, Build section's
  ORDERING rule; never promoted onto a no-patch 1.26.0 toolchain). The lint job runs
  `gofmt -l` ONLY and is required (`lint (gofmt)` check-run); `go vet` and
  version-pinned `staticcheck` run on every OS test leg (per-OS build tags, P18), the
  pass-12 call-5 placement — the earlier "beside gofmt and vet" lint-job spelling is
  superseded. The branch-protection required list names EXACTLY the check-run contexts
  the jobs emit — one required context per emitted context, none omitted, none
  invented (the retired separate `govulncheck (required)` context that no job emitted
  is replaced by the dedicated job's own context, same name, now actually emitted) —
  with ONE activation-conditional member (ADV-P14-A05, pass-14 orchestrator call 14):
  the list carries `govulncheck (required)` ONLY FROM the change that adds go.mod's
  `toolchain` line — the same change that promotes the job (activation-is-same-change,
  Build section's ORDERING rule); until that change the list says govulncheck reports
  on every change but is NOT required, and the context stays out of
  `required_status_checks`. Applying the unconditional list today would do exactly
  what the ORDERING rule forbids: promote a required check onto the current no-patch
  1.26.0 toolchain.
  Workflow edits land on main with the owner's approval (spec-only here).

## Mapping

BC-6.04.001 -> matrix; BC-6.04.002 -> timing report + gate; BC-6.04.003 -> nightly
Tier C; hygiene legs serve NFR-006/policy 21.
