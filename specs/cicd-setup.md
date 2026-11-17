---
document_type: infrastructure-report
level: infra
version: "1.1"
status: draft
producer: devops-engineer
timestamp: 2026-11-17T23:59:00Z
phase: 1c
inputs: [architecture/ARCH-08-build-ci-release.md, architecture/ARCH-07-parity-harness.md]
traces_to: [ARCH-INDEX.md]
input-hash: "ef14751"
---

# CI/CD setup — phase-1-cicd-setup (OD-150)

Implements ARCH-08 (build, CI, release) and the CI legs of ARCH-07. Per OD-150
(owner, 2026-11-16) the work sits in a branch worktree, is **uncommitted** (owner
reviews the diff first), and nothing has been pushed; branch protection is applied
later, after the first green CI run, with admin bypass. Worktree:
`.worktrees/ci-phase-1-setup`, branch `ci/phase-1-setup`, cut from `main`
(`c023bc6`). One finding from setup: `.worktrees/` is **not** in `main`'s
`.gitignore` (only `.factory/` is); left to the owner to add.

## Files created (all uncommitted)

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
| `lint (gofmt + vet)` | ubuntu-24.04 | 10 min | `gofmt -l .` fails on any unformatted file; `go vet ./...` |
| `test (ubuntu-24.04)` / `(macos-15)` / `(windows-2025)` | 3 OSes (BC-6.04.001) | 30 min | `go test -race -count=1 ./...` — `-race` on Linux/macOS only, per ARCH-08 |
| `gitleaks (full history)` | ubuntu-24.04 | 10 min | `gitleaks detect --log-opts="--all"` (fetch-depth 0) **plus** the category pattern scan |
| `locate harness packages` (probe) | ubuntu-24.04 | 5 min | emits `parity`/`statusline` outputs gating the placeholder jobs |
| `parity tier A (live corpus)` | 3 OSes | 45 min | placeholder; skipped until `internal/parity` exists |
| `parity tier B (committed goldens)` | 3 OSes | 30 min | placeholder; no Python needed (goldens committed; Windows included) |
| `parity tier C (nightly differential fuzz)` | 3 OSes | 60 min | schedule-only; `HYLO_PARITY_FUZZSECONDS=1800` = 30 min/OS (OD-149); non-gating |
| `timing report (non-gating)` | 3 OSes | 15 min | placeholder for the BC-6.04.002 report; `HYLO_TIMING_GATE` intentionally unset (OD-117: gate binds only where the owner opts in) |

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
| `parity tier A` | `parity: N cases compared, M exclusions validated, K caches swapped` | `N == 0` |
| `parity tier B` | `tier-b: N goldens compared` | `N == 0` |
| `parity tier C` (nightly) | `tier-c: N inputs per side, M oracle spawns` | 0/unset `HYLO_PARITY_FUZZSECONDS` FAILS on the schedule (never skips); PR-side `t.Skip` is fine only because the job is non-gating |
| exclusion machinery / canary | `exclusions: M entries validated against the closed set` | `M` ≠ file entry count, or the file is missing |
| `lint` / `test` / `govulncheck` | `go: K files scanned` | guard path prints `go: 0 Go files — guard path, NOT a vet/test pass`; after Phase 3 lands sources, `K == 0` fails |
| gitleaks + category pattern scan | `hygiene: K files scanned, H hits` | `K == 0` (scan ran over nothing) |

Additionally: a skipped required check must not count as a pass — the parity/timing
placeholders stay out of `required_status_checks` until they can execute (Phase 3), and
once required, an activation that reports `skipped` is investigated rather than
accepted. The lines are printed by the in-tree test binaries/workflow steps, so they
surface in the runner logs the owner audits.

Category pattern scan (policy 21 / NFR-006): after gitleaks, a `git grep -E` pass
flags private-IP literals (10/8, 192.168/16, 172.16–31/12, with a
`(^|[^0-9])` boundary guard so long dotted-number chains do not false-positive),
POSIX/Windows home paths, and personal emails; GitHub no-reply identities and
`example` domains are exempt. Regexes verified against positive and negative
fixtures before landing.

## Release (`release.yml`)

Single job on `tags: v*` (timeout 30 min, `permissions: contents: write` scoped to
the job): final `go test ./...`, then cross-compiled static builds per ARCH-08 —
`CGO_ENABLED=0`, `-trimpath`, `-ldflags "-s -w -X main.version=<tag>"` (binary
falls back to the VCS stamp, then `dev`; BC-4.01.003). Targets: `linux/amd64`,
`linux/arm64`, `darwin/amd64`, `darwin/arm64`, `windows/amd64` — named
`hylo_<os>_<arch>[.exe]`. SHA-256 checksums in `SHA256SUMS`. Publishes via `gh
release create --generate-notes` — no third-party release action. Release context
(D12/AD-11): GitHub Releases now; Homebrew tap / Scoop / `go install` are follow-ups.

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
| `gitleaks` — full history (`--all`, 54 commits) | Initially 2 findings, both the `generic-api-key` heuristic firing on ordinary prose in the scope line of a factory research doc (`specs/research/domain-hybrid-routing-claude-code-2026-11-14.md`, line 6 — a coverage-domain list, not a credential). **Not secrets, and not a deleted file**: the `specs/` tree lives on the PUBLIC `factory-artifacts` branch, which checkout with `fetch-depth: 0` + `--log-opts="--all"` scans on GitHub — the finding would have failed the required check on every PR. Fixed with `.gitleaksignore` carrying the `9692c07...` fingerprint (reviewed 2026-11-15; comment does not quote the flagged text). Re-run: `--all` = exactly 1 finding, `535b6ae...` — reachable only from a local-only tag, never pushed; `--log-opts="main factory-artifacts"` (what GitHub has) = **CLEAN**. |

Not run: CI on real runners (requires push, OD-150 forbids). govulncheck was run
locally only against the empty module (documents its exit-2 empty-module
behavior above), not against the live vulndb with sources. Windows/macOS runner
behavior of the `-race` split is asserted from ARCH-08's design, not yet observed.

## Branch protection — to apply AFTER the first green run (owner action, OD-150)

`required_status_checks.contexts` (exact check-run names as the workflows emit them):

```
lint (gofmt + vet)
test (ubuntu-24.04)
test (macos-15)
test (windows-2025)
gitleaks (full history)
```

With: `strict: true` (require branches up to date), 0 approving reviews, `enforce_admins: false` (**admin bypass**, per OD-150), no restrictions. The parity/timing placeholders should be added to required checks only after Phase 3 makes them run. `security.yml` also produces PR check runs (`govulncheck`, `gitleaks (weekly)`) but they are informational and NOT in the required set.

## Deferred to Phase 3 (deliberately not done here)

- Real parity jobs: `TestParityTierA_Corpus`, `TestParityTierB_Goldens`,
  `TestParityTierC_DiffFuzz`, canary, exclusion machinery — workflows already
  carry the designed invocations; they activate when `internal/parity` and
  `internal/statusline` exist.
- The timing-report body (1 warm-up + 5 timed runs, nearest-rank p95,
  fake-VM handling subtracted; `HYLO_TIMING_GATE=1` remains owner-side only).
- `TestCorpusHygiene` wiring beyond the Tier A `-run` selector.
- Distribution follow-ups (Homebrew tap, Scoop, `go install`), container
  packaging, and Prometheus export configuration — not in P1 scope (ARCH-08).
- `.worktrees/` addition to the PARENT checkout's `.gitignore` on `main`
  (added to the worktree copy in this change; owner propagates to `main`).
