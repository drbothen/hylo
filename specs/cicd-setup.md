---
document_type: infrastructure-report
level: infra
version: "1.13"
status: draft
producer: devops-engineer
timestamp: 2026-11-21T18:00:00Z
phase: 1c
inputs: [architecture/ARCH-08-build-ci-release.md, architecture/ARCH-07-parity-harness.md]
traces_to: [ARCH-INDEX.md]
input-hash: "162dc77"

---

# CI/CD setup — phase-1-cicd-setup (OD-150)

Implements ARCH-08 (build, CI, release) and the CI legs of ARCH-07. Per OD-150
(owner, 2026-11-16) the work was prepared in a branch worktree and reviewed by the
owner before landing. STATUS UPDATE (ADV-P2-A24, 2026-11-17): the change is now
**committed on main** — PR #1 (squashed, `fd031da` "Add CI, release and security
workflows (phase-1)") — the `.worktrees/ci-phase-1-setup` worktree no longer exists,
and `.github/workflows/*.yml`, `go.mod` and `.gitleaksignore` live in the repo root
(branch protection applied per OD-151 after the first green run). One finding from
setup stands: `.worktrees/` belongs in `main`'s `.gitignore`; the appended line below
landed with the change. The ci.yml timing job's placeholder body predates the pass-3 D39
wiring — the REQUIRED behaviour is the in-tree timing test below, not an echo (see the
lag notes section; ADV-P4-A08). Activating it (with the
positive-coverage lines below) is Phase 3 work.

## Files created (landed on main via PR #1)

| Path | Purpose |
|---|---|
| `.github/workflows/ci.yml` | lint + 3-OS test matrix + gitleaks + parity harness placeholders + nightly Tier C + timing report |
| `.github/workflows/release.yml` | version tags `v*` → static binaries + checksums → GitHub Release |
| `.github/workflows/security.yml` | weekly govulncheck + gitleaks, plus PR trigger (job names suffixed "weekly" to avoid required-check collisions with ci.yml on PRs) |
| `go.mod` | `module github.com/drbothen/hylo`, `go 1.26.0` only — no Go sources (Phase 3 writes tests first) |
| `.gitleaksignore` | one reviewed false-positive fingerprint (9692c07...:specs/research/...:generic-api-key:6) plus one comment; see validation section |
| `.gitignore` (appended) | `.worktrees/` — story/CI worktree dirs are never committed (parent `main` checkout still needs the same line added by the owner) |

No product code, no scripts, no branch/repo settings touched; `.gitleaksignore` holds a reviewed false-positive fingerprint only (see validation).

## CI (`ci.yml`) — jobs, triggers, design

Triggers: `pull_request`, `push` to `main`, `workflow_dispatch`, and `schedule`
(nightly `30 3 * * *` UTC). Least privilege (`permissions: contents: read`);
`concurrency` cancels superseded runs per ref.

| Job | Matrix | Timeout | What it does |
|---|---|---|---|
| `lint (gofmt + govulncheck)` | ubuntu-24.04 | 10 min | `gofmt -l .` fails on any unformatted file; `govulncheck ./...` beside it — each runs ONCE, in this ubuntu job (pass-12 call 5; check-run name updated from the staticcheck-era spelling). `go vet` and version-pinned `staticcheck` run on EVERY OS test leg instead (per-OS build tags, P18) |
| `test (ubuntu-24.04)` / `(macos-15)` / `(windows-2025)` / `(ubuntu-24.04-floor)` | 3 OSes + ubuntu floor (BC-6.04.001; pass-12 call 5) | 30 min | FOUR required legs: the three OS legs (Go from go.mod's `toolchain` line) plus an ubuntu floor leg pinned `go-version: 1.26.0` (ADV-P10-D09). NO leg installs an interpreter (pass-12 call 5: setup-python is installed ONLY in jobs that -run an ORACLE_TESTS member). Each leg: `go vet ./...` + version-pinned `staticcheck` (per-OS build tags, P18), then `go test -race -count=1 ./...` (`-race` on Linux/macOS only, per ARCH-08; CGO_ENABLED=1 on the -race legs, VP-037). The plain test step EXCLUDES the ORACLE_TESTS selector (ARCH-07's named pattern — `^(TestParityTierA_Corpus\|TestParityCanary_ShimLoaded\|TestParityCacheSwap_FourCaches\|TestParityTierC_DiffFuzz\|TestTiming)$` — ADV-P11-A07, five members per pass-12 call 6) on every leg (pass-6 A12, call 13: the dedicated tier A job is the one authoritative run — one run, one timeout) |
| `gitleaks (full history)` | ubuntu-24.04 | 10 min | `gitleaks detect --source . --log-opts="--all"` after checkout with `fetch-depth: 0` (rev set corrected pass-12 call 1: the scan covers the PR head and every fetched ref) — the scanned rev set EQUALS `git rev-list --count --all` by construction — **plus** the category pattern scan |
| `locate harness packages` (probe) | ubuntu-24.04 | 5 min | emits `parity`/`statusline` outputs gating the placeholder jobs |
| `parity tier A (live corpus)` | 3 OSes (ubuntu leg carries setup-python + the OD-170 staleness step, pass-12 call 5) | 45 min | placeholder; skipped until `internal/parity` exists. Once activated this is the SINGLE authoritative Tier A run (pass-6 A12, call 13) with its own 45-minute timeout — the plain test step never also runs the corpus. Its ubuntu leg installs Python, prints the resolved CPython patch, and runs the OD-170 staleness check (`go generate ./...` + `git diff --exit-code`) before the corpus `-run` |
| `parity tier B (committed goldens)` | 3 OSes | 30 min | placeholder; no Python needed (goldens committed; Windows included) |
| `parity tier C (nightly differential fuzz)` | 3 OSes | 60 min | schedule-only; installs Python and -runs its ORACLE_TESTS member `TestParityTierC_DiffFuzz` (resolved CPython patch printed, pass-12 call 5); `HYLO_PARITY_FUZZSECONDS=1800` = 30 min/OS (OD-149); non-gating |
| `coverage (gate)` | ubuntu-24.04 | 30 min | OWN JOB (pass-7 A07, orchestrator call 12 — required checks bind to check-runs/jobs, and a step of the 3-OS `test` matrix job emits no `coverage` check-run); RUNS ON EVERY PR — never probe-gated on `internal/parity` (ADV-P9-A04: parity is built LAST, so a parity-keyed gate would leave S1/S5 code merging while a required check is skipped, and GitHub counts a skip as success): runs `go test -count=1 -coverpkg=./internal/... -coverprofile=cover.out ./internal/...`, prints `coverage: G of 3 gated packages present`, checks each gated package that EXISTS against the COMMITTED package manifest — a manifest package missing from the profile (renamed or moved) fails the job, and `G == 0` is allowed while NONE of the three gated packages exists: the committed manifest lists the gated packages present in the repo and grows as each lands, so `internal/platform` or other non-gated `internal/` packages never bind (the approved build order lands `internal/platform` first and `internal/config` third, BEFORE any gated package — early PRs legitimately sit at `G == 0`; ADV-P11-A02) — and enforces OD-158's **>= 95 % statement coverage** (Go's figure; the OD-158 gate name "line coverage" denotes it, ADV-P11-A03; per-package figure derived from the merged `-coverpkg` profile per ARCH-08) for S1 — `internal/statusline`, `internal/cost` — and S5 — `internal/pyfmt` (OD-193). Timeout 30 min = the test job's, the floor for the same selection plus `-coverpkg` instrumentation (ADV-P9-A15). Oracle-dependent tests (the ORACLE_TESTS pattern, ARCH-07) are excluded because they need the Python oracle, which the coverage job does not install (ADV-P9-A07 — Tier A runs every case in-process and a subset as the built binary, ARCH-07), so Tier A runs do NOT count toward statusline coverage (gate scope per OD-193) while Tier B golden tests and harness-machinery tests run in-process under `./internal/...` and DO credit `internal/statusline` (ADV-P11-A03). `internal/parity` (S6) coverage is profiled and REPORTED, not gated (OD-193 withdraws pass-7 call 12's addition of the referee to the gate). It is the `coverage` required check in branch protection |
| `timing report (non-gating)` | 3 OSes | 15 min | INSTALLS PYTHON (it -runs the ORACLE_TESTS member `TestTiming`, pass-12 call 5; resolved CPython patch printed — the report must include the CPython oracle median, BC-6.04.002 PC-2); runs `go test ./internal/parity -run '^TestTiming$' -count=1` once `internal/parity` exists (pass-3 D39 wiring; upload the report as a workflow artifact); `HYLO_TIMING_GATE` intentionally unset (OD-117: gate binds only where the owner opts in). Positive coverage (pass-3 A16; census added pass-7 A20): the job fails unless it prints `timing: N cases timed > 0` with `N >= 1` AND `N` equals the corpus case census — timing 1 of N cases must not pass |

Harness-placeholder semantics: job-level `if` reads `needs.probe.outputs.*`
(hashFiles() is not allowed in job-level `if` — actionlint-enforced); a skipped
required check counts as success on GitHub, so the placeholders must NOT be added to
branch protection's required set until Phase 3 makes them execute (the section below
tightens this: from activation on, every required detector must print a
positive-coverage line and fail on zero coverage — a skip is never accepted as a pass;
ADV-P1-A09). Proposed
invocations (test names per ARCH-07 OD-145) are baked into the step bodies so
Phase 3 activates them by adding code, not by editing workflows. Tier A sets
`HYLO_PARITY_PYTHON` from `actions/setup-python`'s `python-path` output (OD-108:
absolute interpreter path, never PATH discovery).

## Positive-coverage requirement (spec-side; ADV-P1-A09 — implementation lands later on main with owner approval)

Every regression-detector job must log a runtime-computed positive-coverage line and
fail when it checked nothing. Per job, the required line is:

| Job | Positive-coverage line | Fail condition |
|---|---|---|
| `parity tier A` | `parity: N cases compared, M exclusions validated, K caches swapped` | `N == 0`, `N` ≠ the COMMITTED expected case count (manifest, ADV-P10-A04) or `N` ≠ case-directory census — a deleted case directory shrinks the runtime count and the runtime census equally, so the committed manifest is what catches a partially lost corpus (ADV-P2-A15) — or `K == 0` while any compared case declares swap seeds (pass-6 A10, call 13 — the swap tier must not check nothing and pass) |
| `parity tier B` | `tier-b: N goldens compared` | `N == 0`, `N` ≠ the COMMITTED expected golden count for the host OS (manifest, ADV-P10-A04) OR `N` ≠ HOST-OS golden census — `*.golden` on POSIX legs, `*.windows.golden` on the Windows leg (pass-7 A18; the same native-set discipline as `-update`, pass-5 D29). Partially lost golden set must not pass, pass-5 A19 |
| `parity tier C` (nightly) | `tier-c: N inputs per side, M oracle spawns` | 0/unset `HYLO_PARITY_FUZZSECONDS` FAILS on the schedule (never skips); a scheduled run comparing `N == 0` inputs or spawning `M == 0` oracles FAILS (pass-6 A10, call 13); PR-side `t.Skip` is fine only because the job is non-gating |
| exclusion machinery / canary | `exclusions: M entries validated against the closed set` | `M` ≠ file entry count, or the file is missing |
| `lint` / `test` / `govulncheck` | `go: K files scanned` + `go test: N tests run, S skipped` (test jobs) | guard path prints `go: 0 Go files — guard path, NOT a vet/test pass`; after Phase 3 lands sources, `K == 0` or `N == 0` fails; an all-skip suite is reported via `S` and investigated, not accepted (ADV-P2-A15) |
| gitleaks (secret scan) | `gitleaks: N commits scanned` | `N == 0` or `N` ≠ `git rev-list --count --all` — the scan's `--log-opts="--all"` and the counter name the SAME rev set by construction (HEAD plus every fetched ref; a PR run's own commits are inside both), pass-12 call 1 — a shallow or narrowed scan still covers at least 1 commit, so the scanned count is COMPARED with the rev count across `--all`, not merely checked against zero (ADV-P9-A05, ADV-P10-A05) |
| category pattern scan | `hygiene: K files scanned, H hits` | `K == 0` (scan ran over nothing) or `H > 0` (any flagged hit fails the job — pass-3 A18: "found hits" is a failure, never an accepted pass) |
| `timing report` (pass-3 A16/D39; census added pass-7 A20; manifest ADV-P10-A04) | `timing: N cases timed > 0` | `N == 0` (an activated timing job reporting on zero cases must not pass), `N` ≠ the COMMITTED expected case count (manifest) or `N` ≠ corpus case census (timing 1 of N cases must not pass) |
| `coverage` gate (pass-5 A16; job + scope pass-7 A07; fail scope pass-8 call 1; manifest census ADV-P10-A04/A06; manifest growth ADV-P11-A02) | `coverage: G of 3 gated packages present; min statement coverage M% >= 95` (profile produced with `-coverpkg=./internal/...`) | `G` is compared with the COMMITTED package manifest as well as with zero: a gated package — `internal/statusline`, `internal/cost`, `internal/pyfmt` — that is in the manifest but absent from the profile (renamed or moved) fails the job, as does an existing gated package reporting `[no statements]` (trivial pass) or `M < 95`; the committed manifest lists the gated packages present in the repo and GROWS as each lands, and `G == 0` is allowed while NONE of the three gated packages exists, whatever other `internal/` packages exist (early build-order PRs, ADV-P11-A02); `internal/parity`'s figure is reported for information and does not bind (OD-193) |
| generated-table staleness (pass-5 A16) | `generate: N generated paths checked, D regenerated` | `N == 0` (zero `go:generate` directives checks nothing) or `D > 0` |

Additionally: a skipped required check must not count as a pass — the parity/timing
placeholders stay out of `required_status_checks` until they can execute (Phase 3), and
once required, an activation that reports `skipped` is investigated rather than
accepted. The lines are printed by the in-tree test binaries/workflow steps, so they
surface in the runner logs the owner audits.

Category pattern scan (policy 21 / NFR-006): after gitleaks, a `git grep -E` pass
flags private-IP literals (10/8, 192.168/16, 172.16–31/12, with a
`(^|[^0-9])` boundary guard so long dotted-number chains do not false-positive),
POSIX/Windows home paths, and personal emails; GitHub no-reply identities and
`example` domains are exempt. Categories added pass-3 (A17, closing the gap to the
CLAUDE.md hygiene set): personal/infra hostnames, usernames, session links and
UUIDs (Claude-session links included), and "Claude" in product/binary/logo names.
Regexes verified against positive and negative
fixtures before landing.

## Pass-4 required behaviour and landed-ci.yml lag notes (ADV-P4-A07/A08/A13/A14/A17)

The spec above states the REQUIRED job behaviour; the committed `.github/workflows/ci.yml`
(on public `main`, owner-committed — not edited in this burst) lags it in four places.
Each lag carries its own "change required before" deadline.

1. **Test job interpreter (ADV-P4-A07; corrected pass-8 A06, orchestrator call 1;
   placement corrected pass-12 call 5).**
   REQUIRED: the plain test legs — all FOUR, including the ubuntu `go-version: 1.26.0`
   floor leg — install NO interpreter and export nothing: setup-python is installed
   ONLY in jobs that -run an ORACLE_TESTS member (pass-12 call 5). The OD-170
   generated-table staleness step (lag note 6) rides the dedicated tier A job's ubuntu
   leg, the one ubuntu job that already resolves the oracle. Each leg gains `go vet` +
   version-pinned `staticcheck` steps (per-OS build tags, P18). **Landed
   ci.yml lags:** the committed ubuntu test leg has neither the setup-python step nor
   the `HYLO_PARITY_PYTHON` export that lag note 6's staleness step requires; the
   committed legs match the required no-interpreter design and need only the
   vet/staticcheck steps and the floor leg. **Change required before the pyfmt
   generators land (Phase 3).**
2. **Timing job (ADV-P4-A08).** REQUIRED: the timing job gates on the probe's
   `parity` output — `TestTiming` lives in `internal/parity` (`par/timing.go`,
   BC-COMPONENT-MAP), not `internal/statusline`, so a statusline-probe gate is
   wrong — and executes `go test ./internal/parity -run '^TestTiming$' -count=1`
   with the positive-coverage line `timing: N cases timed > 0`. Its echoed placeholder
   text must state the designed sampling (1 discarded warm-up + 20 timed replays per
   case; ONE timed sample = ONE invocation of hylo, each step timed on its own — a
   20-sample series per (case, step); nearest-rank p95 = 19th sorted sample, computed
   and gated per (case, step), no pooling, no summing over steps — pass-12 call 4) —
   the stale
   "1 warm-up + 5 timed runs" wording must not survive activation. **Landed ci.yml
   lags:** the committed job is an `echo` gated on the statusline probe with the
   stale 5-sample wording. **Change required before Phase 3 activates the timing
   job.**
3. **Hygiene scan (ADV-P4-A14; factory-artifacts leg redesigned ADV-P10-A03, orchestrator
   call 16).** REQUIRED: the category pattern scan implements ALL
   categories above (adding hostnames, usernames, session links, UUIDs and the
   product-name rule to the landed three), prints `hygiene: K files scanned, H hits`
   and fails on `K == 0` or `H > 0`; the scan runs in ci.yml on every PR and every
   `push` to `main`, and the public `factory-artifacts` branch is scanned by a
   dedicated SCHEDULED (nightly, riding ci.yml's existing schedule trigger) and
   MANUALLY DISPATCHABLE (workflow_dispatch) job that runs ON `main` — where the
   workflow files live — checks out the `factory-artifacts` ref, and runs the category
   pattern scan over that checked-out tree. A push trigger added on the
   factory-artifacts branch can never fire (GitHub runs push workflows from the
   workflow files in the pushed commit, and factory-artifacts carries no `.github/`),
   and a `git grep` pass inside an ordinary ci.yml checkout never reads
   factory-artifacts content — the checked-out-ref job is the only CI-side way to scan
   the branch's committed tree. The local pre-push hook stays the PUSH-TIME guard for
   factory-artifacts (NFR-006's every-push guarantee); the nightly/manual job is CI's
   independent verification of what the branch actually contains.
   **Landed ci.yml lags:** only IPs, home paths and emails are scanned, a fixed
   "clean" message prints with no count, and the factory-artifacts checkout job does
   not exist.
   **Change required before the next factory-artifacts push (NFR-006).**
4. **Coverage gate (ADV-P4-A13; restructured pass-7 A07/A09, orchestrator call 12; gate
   scope per OD-193, pass-8 orchestrator call 1; every-PR scope and Tier A rationale per
   ADV-P9-A04/A07).** REQUIRED: coverage is its OWN JOB on
   ubuntu-24.04 — the `coverage` required check-run — which applies the SAME Tier A
   exclusion as the plain test step (so it installs NO interpreter and keeps its
   30-minute timeout — ADV-P9-A15: at least the test job's 30 minutes, the floor for
   the same selection plus `-coverpkg` instrumentation), produces the
   per-package profile (`go test -count=1 -coverpkg=./internal/...`), prints
   `coverage: G of 3 gated packages present`, checks each gated package that EXISTS and
   enforces OD-158's
   statement-coverage gate (metric name aligned pass-12 A12), **>= 95 %**, for S1 —
   `internal/statusline`, `internal/cost` —
   and S5 — `internal/pyfmt`. The job runs on every PR and is never gated on
   `internal/parity` existing (ADV-P9-A04: parity is built LAST; keying the required
   gate on parity leaves S1/S5 merging while the check skips, and a skip counts as
   success). `internal/cost` IS gated — SS-01 comprises
   `internal/statusline` and `internal/cost` (ARCH-INDEX Subsystem Registry) and
   module-criticality.md classes it CRITICAL by inheritance. `internal/parity` (S6)
   coverage is profiled and REPORTED, not gated — OD-193 withdraws pass-7 call 12's
   addition of the referee to the gate. S1/S5 coverage comes from IN-PROCESS tests;
   Tier A is excluded because Tier A needs the Python oracle, which the coverage job
   does not install (ADV-P9-A07 — Tier A runs every case in-process and a subset as
   the built binary, ARCH-07).
   Kill-rate targets stay Phase 6 (OD-158).
   **Landed ci.yml lags:** no coverage job, no profile producer, no threshold check.
   **Change required before the P1 exit record is written (Phase 5 gate).**
5. **Hardening posture (ADV-P4-A17).** REQUIRED: govulncheck promoted to a required
   PR check in ci.yml (`govulncheck (required)`, distinct from security.yml's weekly
   `govulncheck`), and the lint job gains a version-pinned staticcheck-class analysis
   (`honnef.co/go/tools/cmd/staticcheck`) beside gofmt and vet, both with the
   empty-module guard. ORDERING (ADV-P9-A06): the go.mod `toolchain go1.26.x` line
   (ARCH-08 Build section) MUST land before this check becomes required — govulncheck
   reports stdlib advisories against the Go version actually used. **Landed ci.yml
   lags:** govulncheck runs only in the
   informational security.yml; lint is gofmt + vet. **Change lands on main with the
   owner's approval (workflow edits are owner-committed); before Phase 4.**
6. **Generated-table staleness (OD-170).** REQUIRED: the staleness step — which runs
   `go generate ./...` followed by `git diff --exit-code` over the generated paths; any
   diff fails the leg, so a stale committed Unicode 14.0 table or pyfmt oracle table can
   never pass CI — runs AFTER setup-python (pass-5 A04: the generators are
   `testdata/gen/*.py` under the 3.11.x oracle (OD-185: floating latest patch, harness
   self-checks the measured constants), so setup-python must precede
   `go generate`, never follow it). Its HOME is the dedicated tier A job's ubuntu leg
   (corrected pass-12 call 5: the plain test legs install no interpreter, so the step
   cannot ride a test leg; it rides the one ubuntu job that already resolves the
   oracle). The interpreter is the floating
   3.11.x latest patch (OD-104/OD-185 — the pass-5 exact-3.11.7 pin is withdrawn):
   the harness self-checks the 3.11.7-era measured constants against the resolved
   oracle at start (depth boundaries + `unicodedata.unidata_version` + the NUL-keeps
   normpath probe — `posixpath.normpath('a\0b')` and `ntpath.normpath('a\0b')` must
   both return `'a\x00b'`, ADV-P11-B08 — fail closed,
   resolved version printed) and golden metadata records the resolved patch, so a
   moved boundary fails loudly instead of flapping silently on patch drift.
   **Landed ci.yml lags:** no such step. **Change required
   before the pyfmt generators land (Phase 3).**
7. **Release job interpreter (pass-5 A17, call 6; corrected pass-7 A08, orchestrator
   call 12; member set per pass-12 call 6).** REQUIRED: `release.yml`'s plain
   `go test ./...` EXCLUDES the
   ORACLE_TESTS selector (ARCH-07, ADV-P11-A07 — now FIVE members, pass-12 call 6) —
   the oracle-dependent tests run ONLY
   via ci.yml's dedicated job (one authoritative run,
   pass-6 A12; the tag push also triggers ci.yml), never inside the release job's
   `go test`, where it would face the release job's 30-minute cap: one run, one
   timeout. The release job therefore installs NO interpreter (no setup-python, no
   `HYLO_PARITY_PYTHON` export) — the pass-5 setup-python requirement for
   `release.yml` is withdrawn. **Landed release.yml lags:** the committed job runs
   `go test ./...` with no Tier A exclusion. **Change required before the first
   release tag cut after Tier A integration (Phase 3).**

## Release (`release.yml`)

Single job on `tags: v*` (timeout 30 min, `permissions: contents: write` scoped to
the job): final `go test ./...` (the ORACLE_TESTS selector EXCLUDED — the
oracle-dependent tests run only via ci.yml's dedicated job; pass-7 A08, orchestrator
call 12, pattern per ADV-P11-A07 with the FIVE-member set of pass-12 call 6), then cross-compiled
static builds per ARCH-08 —
with NO interpreter installation (no setup-python, no
`HYLO_PARITY_PYTHON` export; the pass-5 requirement is withdrawn, lag note 7 above).
Builds:
`CGO_ENABLED=0`, `-trimpath`, `-ldflags "-s -w -X main.version=<tag>"` (binary
falls back to the VCS stamp, then `dev`; BC-4.01.003). Targets: `linux/amd64`,
`linux/arm64`, `darwin/amd64`, `darwin/arm64`, `windows/amd64` — named
`hylo_<os>_<arch>[.exe]`. SHA-256 checksums in `SHA256SUMS`. Publishes via `gh
release create --generate-notes` — no third-party release action. Release context
(D12/AD-11): GitHub Releases now; Homebrew tap / Scoop / `go install` are follow-ups.
Untested-target disclosure (pass-3 A28): the CI test matrix exercises `linux/amd64`
(ubuntu), `darwin/arm64` (macos-15) and `windows/amd64` (windows-2025); the release
targets `linux/arm64` and `darwin/amd64` are cross-compiled but never test-exercised
in CI — a disclosed gap, accepted for P1 because the FMA-sensitive arm64 sites
(ARCH-06) are compiled identically per-GOOS and are exercised on `darwin/arm64`.

## Security (`security.yml`)

Weekly schedule (`17 4 * * 1`, Mondays) plus `pull_request` (timeout 10–15 min per
job): `govulncheck ./...` via `go run golang.org/x/vuln/cmd/govulncheck@v1.9.0`,
and the identical gitleaks + pattern-scan pair from CI. Blocking per-push scans
already live in `ci.yml`. Job names differ deliberately — `gitleaks (weekly)`
here vs `gitleaks (full history)` in ci.yml — because both workflows fire on
`pull_request` and check-run names must not collide. govulncheck carries the
same empty-module guard as the Go jobs; verified locally that it needs it:
`govulncheck ./...` on the skeleton exits 2 with "no packages matched the
provided patterns".

## Pinned actions (full SHA, version in comment)

| Action | Pin | Version |
|---|---|---|
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | v7.0.1 |
| `actions/setup-go` | `b7ad1dad31e06c5925ef5d2fc7ad053ef454303e` | v7.0.0 |
| `actions/setup-python` | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` | v7.1.0 |

Tool versions are pinned in-place (`gitleaks/gitleaks/v8@v8.30.1`,
`govulncheck@v1.9.0`), so `go run` reproducibility matches action pinning.
Every job sets `timeout-minutes`; every `run` block is bash (`shell: bash` on the
matrix jobs); `persist-credentials: false` on all checkouts.

## Empty-module handling (verified, not assumed)

With go1.26 (locally 1.26.5) on a module whose only file is `go.mod`:
`go vet ./...` and `go test ./...` both **exit 1** with
`"./..." matched no packages` — verified in `.worktrees/ci-phase-1-setup` before
writing the workflows; `gofmt -l .` exits 0. Therefore every Go invocation in CI
first checks `git ls-files '*.go'`: no sources yet → prints a notice and exits 0.
Once Phase 3 lands sources, the guard passes through to the real command
unchanged. This behavior is why `lint`, `test`, and `govulncheck` go green on the
initial skeleton commit.

## Validation performed

| Check | Result |
|---|---|
| `actionlint` (v1.7.12) on all three workflows | PASS (after fixing two real findings it caught: hashFiles() illegality at job level; shellcheck SC2012 on the probe's ls) |
| gofmt / vet / test on the worktree (go1.26.5) | gofmt clean; vet/test exit-1-on-empty confirmed and guarded |
| probe logic under bash (3 fixture layouts) | PASS — empty / both / statusline-only |
| pattern-scan regexes (positive + negative fixtures) | PASS — private IPs (incl. `ip:port`), home paths, emails hit; RFC 5737, dates, no-reply filtered; residual: a private-IP-shaped quad embedded in a 5+-octet dotted chain still hits (accepted, errs loud) |
| full-worktree pattern scan | CLEAN — zero hits incl. the new workflow files |
| `gitleaks` — uncommitted tree | CLEAN (no leaks) |
| `gitleaks` — full history (`--all`, 54 commits) | Initially 2 findings, both the `generic-api-key` heuristic firing on ordinary prose in the scope line of a factory research doc (`specs/research/domain-hybrid-routing-claude-code-2026-11-14.md`, line 6 — a coverage-domain list, not a credential). **Not secrets, and not a deleted file**: the `specs/` tree lives on the PUBLIC `factory-artifacts` branch, which checkout with `fetch-depth: 0` + `--log-opts="--all"` scans on GitHub — the finding would have failed the required check on every PR. Fixed with `.gitleaksignore` carrying the `9692c07...` fingerprint (reviewed 2026-11-15; comment does not quote the flagged text). Re-run: `--all` = exactly 1 finding, `535b6ae...` — reachable only from a local-only tag, never pushed; `--log-opts="main factory-artifacts"` (the interim invocation) = **CLEAN**. Historical record of the local validation runs; the REQUIRED ci.yml invocation is now the `--all` scan with the `git rev-list --count --all` counter (pass-12 call 1, superseding the interim two-ref set of ADV-P11-A04), so this divergence class is closed. |

Not run: CI on real runners (requires push, OD-150 forbids). govulncheck was run
locally only against the empty module (documents its exit-2 empty-module
behavior above), not against the live vulndb with sources. Windows/macOS runner
behavior of the `-race` split is asserted from ARCH-08's design, not yet observed.

## Branch protection — to apply AFTER the first green run (owner action, OD-150)

`required_status_checks.contexts` (exact check-run names as the workflows emit them;
updated pass-6 A11, call 13; the list gains the ubuntu floor test leg and the
gofmt+govulncheck lint spelling per pass-12 call 5):

```
lint (gofmt + govulncheck)
test (ubuntu-24.04)
test (macos-15)
test (windows-2025)
test (ubuntu-24.04-floor)
coverage
govulncheck (required)
gitleaks (full history)
```

With: `strict: true` (require branches up to date), 0 approving reviews, `enforce_admins: false` (**admin bypass**, per OD-150), no restrictions. Disambiguation (pass-6 A11, call 13; corrected pass-7 A07, orchestrator call 12): the coverage gate is its OWN JOB on ubuntu-24.04 whose check-run is named `coverage` — required checks bind to check-runs (jobs), and a step of the 3-OS `test` matrix job emits no `coverage` check-run, so the earlier "required STEP of the test job" reading would have blocked forever or been removed. The parity/timing placeholders should be added to required checks only after Phase 3 makes them run. `security.yml` also produces PR check runs (`govulncheck`, `gitleaks (weekly)`) but they are informational and NOT in the required set.

## Deferred to Phase 3 (deliberately not done here)

- Real parity jobs: `TestParityTierA_Corpus`, `TestParityTierB_Goldens`,
  `TestParityTierC_DiffFuzz`, canary, exclusion machinery — workflows already
  carry the designed invocations; they activate when `internal/parity` and
  `internal/statusline` exist.
- The timing-report body (1 warm-up + 20 timed replays per case; ONE timed sample =
  ONE invocation of hylo, each step timed on its own — a 20-sample series per
  (case, step); nearest-rank p95 = 19th sorted sample, computed and gated per
  (case, step), no pooling, no summing over steps — pass-12 call 4; fake-VM handling
  subtracted; `HYLO_TIMING_GATE=1` remains owner-side only).
- `TestCorpusHygiene` wiring beyond the Tier A `-run` selector (the exclusion pattern
  is now the named ORACLE_TESTS constant, ARCH-07 — TestCorpusHygiene itself needs no
  oracle and is not a member).
- Distribution follow-ups (Homebrew tap, Scoop, `go install`), container
  packaging, and Prometheus export configuration — not in P1 scope (ARCH-08).
- `.worktrees/` addition to the PARENT checkout's `.gitignore` on `main`
  (added to the worktree copy in this change; owner propagates to `main`).
