---
document_type: architecture-section
level: L3
section: "build-ci-release"
version: "1.11"
status: draft
producer: architect
timestamp: 2026-11-20T22:00:00Z
phase: 1b
inputs: [prd.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "604b20b"

---

# ARCH-08 — Build, CI, release

> Implemented by the phase-1-cicd-setup step from this design. Classification:
> infrastructure (workflow YAML, release tooling); its logic lives in the repo, not the
> binary.

## Build

- Go >= 1.26: go.mod pins `go 1.26.0` only, **no toolchain directive** (actual repo
  state, ADV-P2-A14; cicd-setup.md agrees) — with `go-version-file`, CI therefore
  installs 1.26.0, the oldest 1.26 patch, so the "Go 1.26.x leg" lacks later stdlib
  security fixes. Approved-in-spec remedy: add a `toolchain go1.26.x` line to go.mod
  (lands on main with the owner's approval; spec-only here). ORDERING (ADV-P9-A06):
  the `toolchain` line MUST land BEFORE govulncheck becomes a required PR check
  (Hardening posture below) — govulncheck reports stdlib advisories against the Go
  version actually used (crypto/tls and net are reachable through the metrics client),
  so promoting the required check onto a no-patch 1.26.0 toolchain either goes
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
    PR["pull_request / push"] --> L["lint: gofmt, vet, staticcheck"]
    L --> M{"matrix:<br/>ubuntu-24.04 / macos-15 (arm64) / windows-2025"}
    M -->|"ubuntu-24.04 leg ONLY<br/>(ADV-P9-A16: the macOS/Windows test legs<br/>install NO interpreter — text below)"| PY["setup-python 3.11.x (floating latest patch, OD-104/OD-185;<br/>harness self-checks measured constants, fail closed on drift) -> absolute path -> HYLO_PARITY_PYTHON<br/>(pass-5 A04: setup-python precedes go generate, so the<br/>staleness step never falls back to PATH Python, OD-104)"]
    PY --> GEN["go generate ./... staleness check: git diff --exit-code (OD-170)<br/>ubuntu-24.04 ONLY — the Windows Tier B leg needs no Python (goldens committed)"]
    GEN --> T["go test -race (Linux/macOS) -count=1 ./... — Tier A EXCLUDED (pass-6 A12); setup-python BEFORE go test/generate (pass-3 D22, pass-4 D08)"]
    M -->|"macos-15 / windows-2025 legs"| T
    T --> TB["Tier B goldens (no Python needed on Windows leg: committed)"]
    TB --> HL["gitleaks --log-opts=--all + category pattern scan"]
    HL --> J["report timing per leg, non-gating (OD-117)"]
    COVJOB["coverage JOB (ubuntu-24.04, pass-7 A07; runs on EVERY PR — never probe-gated<br/>on internal/parity, ADV-P9-A04):<br/>go test -coverpkg=./internal/... over IN-PROCESS tests; Tier A excluded because it<br/>needs the Python oracle, which the coverage job does not install (ADV-P9-A07);<br/>checks each gated package that EXISTS — prints `coverage: G of 3 gated packages present`;<br/>>= 95 percent line coverage, S1/S5 packages (OD-158)"] --> REQ["required check-run `coverage`"]
    Nightly["schedule nightly (3 OSes, OD-149)"] --> TC["Tier C differential fuzz, non-gating"]
```

- Race detector on Linux and macOS; the resolved Python patch version is recorded in
  Tier B golden metadata (RK-4). Ordering (pass-3 D22 as superseded pass-7 A08; diagram
  corrected pass-4 D08 and again pass-5 A04): GitHub Actions always sets
  `CI=true`. RULED (pass-6 A12, orchestrator call 13): the dedicated
  `parity tier A (live corpus)` job (45-minute budget) is the ONE authoritative Tier A
  run — the plain `go test` step EXCLUDES the Tier A selector, so the corpus never
  executes under the test job's tighter 30-minute cap: one run, one timeout. The
  pass-3 "Tier A runs live inside the plain `go test` step" ordering rationale is
  superseded (pass-7 A08): setup-python + the `HYLO_PARITY_PYTHON` export survive only
  where a Python consumer remains — the ubuntu staleness step (OD-170), the dedicated
  Tier A job, and nightly Tier C; legs without a Python consumer (macOS/Windows test
  legs, release job) install no interpreter.
  Pin: setup-python installs **3.11.x** (python-version: '3.11', the latest patch —
  OD-104 stands; the pass-5 exact-3.11.7 pin is WITHDRAWN by OD-185, pass-6 A02).
  Because the measured constants (JSON depth limits, Unicode 14.0 tables) were taken on
  3.11.7, the harness SELF-CHECKS them against the resolved oracle at start — measuring
  the depth boundaries and `unicodedata.unidata_version`, failing closed on any mismatch
  and printing the resolved version — and Tier B golden metadata records the resolved
  patch (RK-4); a moved boundary fails the staleness check loudly instead of flapping
  silently on patch drift.
- **Generated-table staleness (OD-170):** the staleness step runs `go generate ./...` and then
  `git diff --exit-code` over the generated paths (Unicode 14.0 class tables and the
  pyfmt oracle tables, ARCH-06); any diff fails the leg — a stale committed table can
  never pass CI. It runs on ubuntu-24.04 ONLY (pass-5 A04): the generators are
  `testdata/gen/*.py` under the pinned oracle, and confining the step to ubuntu keeps
  Python off the Windows leg's critical path — Windows consumes committed Tier B
  goldens, which need no interpreter.
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
  "drives the built binary as a subprocess" premise is superseded) — hence parity runs
  do NOT count toward statusline coverage (gate scope per OD-193). The job checks each
  gated package that EXISTS and prints `coverage: G of 3 gated packages present`;
  `G` is compared with the COMMITTED package manifest — a manifest package missing
  from the profile (renamed or moved) fails the job, and `G == 0` is allowed only
  while no `internal/` Go package exists (skeleton era; ADV-P10-A06); it
  enforces **line coverage
  >= 95 %** per package for S1 — `internal/statusline` and `internal/cost` — and
  S5 — `internal/pyfmt` (OD-158 stands unchanged per OD-193). `internal/cost` IS gated:
  SS-01 comprises `internal/statusline` and
  `internal/cost` (ARCH-INDEX Subsystem Registry) and module-criticality.md classes it
  CRITICAL by inheritance. `internal/parity` (S6) coverage is PROFILED AND REPORTED, not
  gated — OD-193 withdraws pass-7 call 12's addition of `internal/parity` to the gate.
  The
  mutation kill-rate targets stay Phase 6 targets (OD-158) — this gate is line coverage
  only. Designed behaviour; see cicd-setup.md for the landed-ci.yml lag note.
- **Timing (NFR-001, BC-6.04.002):** every leg prints the per-OS report — per corpus
  case, 1 discarded warm-up + **20 timed runs**, samples sorted per case, nearest-rank
  p95 = **19th of the 20 sorted samples** (per nfr-catalog.md; with 5 samples the
  statistic degenerates to the maximum), p95 computed **per case** and binding per case,
  no pooling; fake-VM handling time subtracted. The p95 <= 25 ms
  gate fails the build only with `HYLO_TIMING_GATE=1` (binds on the owner's Mac target).
  CONDITIONAL EXEMPTION (OD-187 + OD-191, pass-7 A02, orchestrator call 3): the >512 KB
  fixture is exempt from the 25 ms p95 target, but the gate FAILS if its p95 exceeds
  100 ms (judgment call: 4x the target, well under the refresh interval). The exempt
  fixture is identified by the validated case flag `timing_exempt: large-transcript` —
  exactly one case, and its transcript must exceed 512 KB (the corpus validator checks
  both) — and the report prints one line whenever the exemption is used.
- **Public-repo hygiene (policy 21, NFR-006):** committed fixtures synthetic-only;
  real inputs replayed from git-ignored `captures/`; gitleaks with
  `--log-opts="--all"` plus the category pattern scan; `TestCorpusHygiene` in-tree.
  The factory-artifacts branch is scanned by a scheduled (nightly) and manually
  dispatchable job running ON `main` that checks out the `factory-artifacts` ref and
  runs the category pattern scan over that checked-out tree — a push trigger on that
  branch can never fire (GitHub runs push workflows from the pushed commit's workflow
  files; factory-artifacts has no `.github/`), and the local pre-push hook stays the
  push-time guard (ADV-P10-A03, orchestrator call 16).
- **Positive coverage (ADV-P1-A09, process gap — implementation lands on main later with
  owner approval):** every regression-detector job must print a runtime-computed
  positive-coverage line and must treat "checked nothing" as failure, never as a pass:
  - Tier A: `parity: N cases compared, M exclusions validated, K caches swapped` — job
    fails if `N == 0`, if `N` differs from the COMMITTED expected case count (a committed
    manifest of the corpus, ADV-P10-A04) or if `N` differs from the number of case
    directories found (same runtime census the exclusions check applies to `M`; a deleted
    case directory shrinks the runtime count and the runtime census equally, so the
    committed manifest is what catches a partially lost corpus — ADV-P2-A15), or if
    `K == 0` while any compared case declares swap seeds — the
    four-cache swap tier (BC-6.02.004, VP-019, R-001 mitigation) must be unable to check
    nothing and pass (pass-6 A10, call 13).
  - Tier B: `tier-b: N goldens compared` — fails if `N == 0`, if `N` differs from the
    COMMITTED expected golden count for the host OS (a committed manifest,
    ADV-P10-A04), or if `N` differs from
    the number of committed golden files found by the same runtime census
    (pass-5 A19: a partially lost golden set must not pass — the Tier A
    case-directory census discipline applied to Tier B). The census counts ONLY the
    HOST OS's golden set — `*.golden` on POSIX legs, `*.windows.golden` on the
    Windows leg (the same native-set discipline as `-update`, pass-5 D29): a lost
    `*.windows.golden` variant is caught by the Windows leg's census, and a POSIX
    census never recounts Windows variants as present (pass-7 A18).
  - Tier C: `tier-c: N inputs per side, M oracle spawns`; the PR-side budget skip
    (`t.Skip` on unset/0 `HYLO_PARITY_FUZZSECONDS`) is allowed only because the job is
    non-gating — on the nightly schedule a 0/unset budget FAILS, it does not skip, and
    a scheduled run that compares `N == 0` inputs or spawns `M == 0` oracles FAILS
    (pass-6 A10, call 13; one clean nightly run is the P1 exit condition, OD-149).
  - Exclusion machinery / canary: `exclusions: M entries validated against the closed
    set` — `M` must equal the file's entry count; a missing exclusions file fails.
  - Go jobs (lint/test/vet/govulncheck): `go: K files scanned` counts source files, so
    it is paired with a **test-run line**: `go test: N tests run, S skipped` — fails if
    `N == 0`; the reported skip count keeps an all-skip suite visible (an all-skip pass
    standing in for coverage is investigated, not accepted — ADV-P2-A15). The skeleton-era
    empty-module guard prints `go: 0 Go files — guard path, NOT a vet/test pass` and is
    removed once Phase 3 lands sources (after which `K == 0` fails).
  - Pattern scan: `hygiene: K files scanned, H hits` — fails if `K == 0` (scan ran over
    nothing) AND if `H > 0` (a found hit is a failure, pass-3 A18), so the scan cannot
    pass while flagging hygiene terms.
  - Gitleaks (secret scan; ADV-P9-A05; positive comparison ADV-P10-A05): `gitleaks: N
    commits scanned` — fails if `N == 0` AND if `N` differs from
    `git rev-list --count` over both refs; a shallow or narrowed `--log-opts` still
    covers at least one commit and exits 0, so the zero-check alone cannot detect it —
    the scanned count is COMPARED with the fetched commit count across main +
    factory-artifacts (fetch-depth 0).
  - Coverage gate (pass-5 A16; fail scope per pass-8 orchestrator call 1; presence scope
    per ADV-P9-A04; manifest census ADV-P10-A04/A06): `coverage: G of 3 gated packages
    present; min line coverage
    M% >= 95` — checks each gated package that EXISTS — `internal/statusline`,
    `internal/cost`, `internal/pyfmt` — against the COMMITTED package manifest and
    fails if a manifest package is missing from the profile (renamed or moved), if one
    exists and reports `[no statements]` (a package trivially "passing" coverage by
    having no statements is a failure, not a pass), or if `M < 95`; `G == 0` is allowed
    only while no `internal/` Go package exists (skeleton era); the job runs on every PR
    and is never gated
    on `internal/parity` existing (ADV-P9-A04); `internal/parity`'s figure is reported for
    information and does not bind (OD-193).
  - Generated-table staleness (pass-5 A16): `generate: N generated paths checked,
    D regenerated` — fails if `N == 0` (a tree with zero `go:generate` directives
    checks nothing and must not pass) and if `D > 0`.
  - Timing report (pass-3 A16/D39; manifest ADV-P10-A04): the timing job executes the in-tree timing test
    (`go test ./internal/parity -run '^TestTiming$' -count=1`, `par/timing.go`) and
    prints `timing: N cases timed > 0` — fails if `N == 0` (an activated job reporting
    on zero cases must not pass), AND if `N` differs from the COMMITTED expected case
    count (the same manifest discipline Tier A applies — ADV-P10-A04) or from the
    corpus case census (timing 1 of N cases
    must not pass; pass-7 A20).
  A skipped required check must never stand in for a pass: probe-gated placeholder jobs
  are added to branch protection's required set only when they can execute (Phase 3),
  and from then on every activation of the job must satisfy its coverage line —
  `skip` on a required detector is investigated, not accepted.
  R-004 mitigation restated for P1 (pass-6 A17 adjudication inside call 13; corrected
  pass-7 A09, orchestrator call 12; gate scope per OD-193): the
  HIGH-impact fake-pass-parity risk is mitigated in P1 NOT by the HIGH kill-rate tier
  (a Phase 6 target, OD-158) but by THIS census discipline plus the >= 95 %
  line-coverage gate over the gated packages (S1/S5, named above) — the mitigation
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

- **Hardening posture (P19, pass-4 A17):** the lint job runs a staticcheck-class
  analysis (`honnef.co/go/tools/cmd/staticcheck`, version-pinned, same empty-module
  guard) beside gofmt and vet, and govulncheck is promoted from the informational
  weekly sweep to a required PR check in ci.yml (distinct check-run name, e.g.
  `govulncheck (required)`, alongside the weekly `govulncheck` in security.yml).
  Sequencing (ADV-P9-A06): this promotion lands AFTER the go.mod `toolchain go1.26.x`
  line (Build section) — never before it.
  Workflow edits land on main with the owner's approval (spec-only here).

## Mapping

BC-6.04.001 -> matrix; BC-6.04.002 -> timing report + gate; BC-6.04.003 -> nightly
Tier C; hygiene legs serve NFR-006/policy 21.
