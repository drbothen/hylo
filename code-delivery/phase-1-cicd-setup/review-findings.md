# Review findings — phase-1-cicd-setup (PR #1, ci/phase-1-setup)

Convergence tracking per `.factory/merge-config.yaml` (`max_review_cycles: 3`).
PR: https://github.com/drbothen/hylo/pull/1 — greenfield infra step under
owner ruling OD-150 (no story ID; demo evidence N/A by construction).

## Convergence table

| Cycle | Findings | Blocking | Fixed | Remaining |
|-------|----------|----------|-------|-----------|
| 0 (baseline) | PR opened; baseRefName=main assertion passed; head d88e5ea | — | — | — |
| 1 | pr-reviewer: 10 non-blocking + 3 nits, verdict APPROVE; security-reviewer: 1 MEDIUM + 2 LOW + 4 INFO, no blocking | 0 | 7 fixes + 2 nits + 1 CI-observed fix landed in `66dd7fa` | 6 deferred with reasons (below) |
| 2 | pr-reviewer delta review of `66dd7fa`: 3 non-blocking + 1 nit, verdict APPROVE | 0 | n/a — operational/cosmetic, registered below | 4 registered (below) |

**Cycle 2 verdict: APPROVE.** covered_sha `66dd7faa6a2a3605ecae6b4b17f32d05de8f8daa`. All 8 fix
claims verified line-by-line (with quoted lines + actionlint + executed scan step + CI-log
confirmation of the gitleaks module path resolving and scanning 49 commits clean). No
regressions: diff is exactly the 8 claimed hunks. Converged at cycle 2 of max 3.

**Cycle-2 register (non-blocking):** (a) release.yml draft-create/edit-fail leaves a draft and
the rerun needs recovery — add recovery note before first real release; (b) release path
exercised only at first tag — dry-run via a throwaway `v0.0.0-rc` tag recommended; (c) email
filter's `|| true` also absorbs grep rc 2 (fixed literal, cannot practically fail); (d) NIT: the
two scan hit-lists join without a separating newline (cosmetic output only).

## Cycle 1 detail

**pr-reviewer (fresh eyes, HEAD d88e5ea) — APPROVE, 0 blocking.** covered_sha
`d88e5eaea43f26455daba1bd1deed6806f93e3b5`. Highlights of the non-blocking
set: F1 comment/code mismatch on Tier C trigger; F2 concurrency could cancel
nightly/main runs; F3 allowlist filter hid whole lines + swallowed `git grep`
errors; F4 IP-coverage narrower than policy; F5 scan duplicated across
workflows; F6 release test skipped on empty module; F7 loose tag filter +
immediate publish; F8 Phase-3 activation traps; F9 skipped-check renaming;
F10 private-repo references in public files. NITs: missing `shell: bash` on
timing-report, overstated pinning comment, optional release-token split.

**security-reviewer (same HEAD) — no blocking (0 CRITICAL / 0 HIGH).**
SEC-001 MEDIUM (CWE-693) line-span exclusions; SEC-002 LOW (CWE-636)
fail-open grep handling — both identical in substance to F3, fixed in the
same batch. SEC-003/004/005/006/007 LOW/INFO deferred or accepted (rationale
in the PR description's Security Review table).

**Triage disposition:** posted as PR comment
https://github.com/drbothen/hylo/pull/1#issuecomment-6926273054
(fix-now list + deferred-with-reasons table).

## CI history

| Run | SHA | Result |
|---|---|---|
| 1 (pull_request) | d88e5ea | 5 pass / 1 FAIL (`gitleaks` both copies: wrong Go module path `github.com/gitleaks/gitleaks/v8`; correct is `github.com/zricethezav/gitleaks/v8`) / 1 pending |
| 2 (pull_request) | 66dd7fa | **ALL GREEN** — lint, test ×3 OS, gitleaks (full history), gitleaks (weekly), govulncheck, probe all pass; parity/timing placeholders skipping by design |

## Cycle-1 fix commit

`66dd7faa6a2a3605ecae6b4b17f32d05de8f8daa` (single commit, d88e5ea..66dd7fa,
no-reply identity, no footers). F1, F2, F3/SEC-001/SEC-002, F4-release,
F5-filter/draft, 2 nits, gitleaks module path. Validation: actionlint 1.7.12
clean ×3; pattern scan executed verbatim (clean) + fault-injection proof that
rc>=2 now fails loudly; gitleaks HEAD-ancestry clean (the single `--all`
finding lives only behind the owner's local tag `pre-scrub-2026-11-15`,
never pushed — out of CI scope, tag untouched).

## Deferred findings register (non-blocking, owner fast-follow)

| Item | Where | Note |
|---|---|---|
| SEC-003 / F4 | scan patterns | Widen to IPv6 ULA/link-local, CGNAT 100.64/10, `/root/`, UNC — policy call |
| SEC-004 | release.yml | Build provenance (attest-build-provenance / cosign) |
| SEC-007 / F5 | ci.yml + security.yml | Extract shared scan into composite action at next touch |
| F8/F9 | ci.yml | Phase-3 activation semantics (tests-that-match-nothing, early-green placeholder, skip-name changes) land with Phase 3 |
| F10 | various | Replace `.factory/` path references, review internal-ID density, owner decides on relocating `.gitleaksignore` |

## Merge authorization package (autonomy level 3)

Automation gate: COMPLETE (all checks green at 66dd7fa; both reviews
0-blocking). Human gate: **APPROVED** — owner instruction 2026-11-16
(admin override authorized for PR #1); executed same day, see merge record.

Owner merge procedure when ready:
1. Review PR #1, the cycle-1 triage comment, and the cycle-2 verdict.
2. `~/.claude/plugins/cache/claude-mp/vsdd-factory/1.0.0-rc.25/bin/check-stale-verdict.sh 1 <covered_sha from the cycle-2 READY verdict>`
3. `~/.claude/plugins/cache/claude-mp/vsdd-factory/1.0.0-rc.25/bin/enforce-merge-strategy.sh 1 --squash` (squash_merge: true in merge-config; `ci/` is not a `^release/v` branch, so the flag passes through unchanged)
4. Branch deletion: `delete_branch_on_merge: true` is set repo-side (GitHub auto-deletes the head branch at merge).
5. After merge (owner action per OD-150): apply branch protection with the five required checks from `.factory/specs/cicd-setup.md` — `lint (gofmt + vet)`, `test (ubuntu-24.04)`, `test (macos-15)`, `test (windows-2025)`, `gitleaks (full history)` — with `strict: true`, 0 approvals, `enforce_admins: false`.

## Merge record (2026-11-16)

Executed by pr-manager step 8 under the owner's admin-override approval; the
dispatch prescribed the exact `gh` invocation, so the enforce-merge-strategy
wrapper was not additionally invoked (`ci/` is a non-release branch; squash is
permitted by merge-config and the release-branch `--merge` invariant does not
apply).

- **Pre-merge:** head `66dd7faa6a2a3605ecae6b4b17f32d05de8f8daa` unchanged from
  the cycle-2 READY verdict; `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`;
  checks green (8 pass; parity tiers + timing-report skipping by design —
  non-gating). `check-stale-verdict.sh 1 66dd7faa…` → exit 0.
- **Merge:** `gh pr merge 1 --squash --delete-branch --admin` with explicit
  `--subject` (PR title) and `--body` (clean summary). Recorded squash commit
  message verified via API: no session links, no claude.ai URLs, no private
  details. No `--no-verify`; main never pushed to directly.
- **Result:** state `MERGED`; mergeCommit `570a0fcfe997e15a4dcf3470f17a05f468193760`;
  mergedAt `2026-11-16T20:34:28Z`.
- **Post-merge assertions:** fetched `main` from the public remote and asserted
  `git merge-base --is-ancestor 570a0fcf…` → pass (merge commit on trunk).
  `git ls-remote … refs/heads/ci/phase-1-setup` → empty (head branch confirmed
  deleted on the remote); `refs/heads/main` resolves to `570a0fcf…`.
- Local worktree `.factory/code-delivery/phase-1-cicd-setup/` retained; branch
  protection left for the orchestrator (item 5 above).

**Status: DONE.** Converged at review cycle 2 of 3; deferred register above
carries forward for the owner fast-follow.
