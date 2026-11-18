---
document_type: remediation-plan
phase: 1d
pass: 12
date: 2026-11-18
source: adversarial-reviews/pass-12.md, adversarial-reviews/ADV-P12-INDEX.md
---

# Pass-12 remediation plan (canonical calls)

Read with the Rules section of `pass-4-remediation-plan.md` and the gates of passes 9-11 (YAML parse after every edit; for-all properties derived from every PC/EC/exception and walked against legacy; state only what you measured, bracketing boundaries on both sides; ASCII wire goldens; cite ARCH and BC files by section/ID + PC/EC/Inv/row, never line numbers; synthetic values on the pre-push hook allowlist; edit only your file set, list out-of-set hits; a reasoned expected output is walked field by field against the legacy code that sets each field). New this pass: **when a fix changes a rule, grep every sibling that states the rule and list each hit** (pass-12 had 9 partial-propagation findings: A03, A05, A09, D01, D03, D05, C03, C2-02, C2-04).

No owner rulings this pass. Next free OD: OD-195.

## Orchestrator calls (binding; checked against the OD log)

1. **gitleaks rev set, corrected (A02, D04; supersedes pass-11 call 7).** The two-ref scan missed a pull request's own commits and depends on bare branch names that checkout does not create. The CI scan is `gitleaks detect --source . --log-opts="--all"` after checkout with `fetch-depth: 0`; `--all` includes HEAD, so a PR run scans the PR head and every fetched ref (factory-artifacts included). Positive coverage: the scanned-commit count equals `git rev-list --count --all` (same rev set by construction). Matches the CLAUDE.md pre-push command.
2. **temp-file case `cache-003`, corrected (D01, D02, D13; supersedes pass-11 call 2).** No fake process table. The oracle child gets the conditional `PATH=<case>/bin` with an EMPTY `bin` directory: legacy's `subprocess.run(["ps", ...])` raises FileNotFoundError, caught at SL:293-294, so `claude_window_start` returns None (orchestrator-measured on CPython 3.11.7 with an empty PATH directory: FileNotFoundError; the same holds on Windows, where no `ps` executable exists). The hylo child gets `HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0`, so `FindAncestor` makes zero probes and returns not-found (BC-3.02.001: at most `max_depth` probes). Both sides render no window-age segment; neither reads the real process tree; the session-cache target stays unseeded, so the leak happens; legacy never reaches SL:286-288 (no extra save, no `mktime`/`strptime`), so the leak count stays "up to two". BC-3.02.001 Inv 4 and BC-6.03.004's D4-EX-1 row are restated: every corpus case either seeds `proc_start` or is `cache-003` (no probe on either side). The conditional fake-PATH machinery's first P1 consumer is `cache-003` with an empty directory.
3. **`statusline.window_age.max_depth` range (A11).** Range `0..1000` (0 = no ancestor walk; upper bound mirrors `statusline.sparkline.history_cap`'s 1000, labelled judgment call); it is a tunable key, so NFR-005 lists it with the tunable caps, not with protocol constants.
4. **Timing unit (A07; follows NFR-001 "render latency" and BC-6.04.002 PC-1 "never pooled across cases or steps").** One timed sample = one invocation of hylo (one render). A multi-step case is replayed from its committed seeds 1 warm-up + 20 times; each step is timed on its own, giving a 20-sample series per (case, step); nearest-rank p95 is computed and gated per (case, step). No summing over steps. ARCH-08, nfr-catalog NFR-001 and BC-6.04.002 state this one unit.
5. **CI legs (A04, A06).** Four test legs: ubuntu-24.04, macos-15 arm64, windows-2025 (Go from go.mod's toolchain) plus an ubuntu floor leg with `go-version: 1.26.0`; all four are required checks and appear in the ARCH-08 diagram, the cicd-setup jobs table and the branch-protection list. Python (setup-python, CPython 3.11) is installed ONLY in jobs that run an `ORACLE_TESTS` member (call 6), and each such job prints the resolved CPython patch; the plain test legs install none. `go vet` and `staticcheck` run on every OS leg (per-OS build tags, P18); `gofmt -l` and `govulncheck` run once in the ubuntu lint job. BC-6.04.001 PC-3/PC-6 follow this.
6. **ORACLE_TESTS membership (A08).** The pattern lists every test that starts the Python oracle: `TestParityTierA_Corpus`, `TestParityCanary_ShimLoaded`, `TestParityCacheSwap_FourCaches`, `TestParityTierC_DiffFuzz`, `TestTiming`. Plain test, coverage and release pass `-skip $ORACLE_TESTS`; the Tier A job, the timing job and the nightly fuzz job each install Python and `-run` their own member(s).
7. **Shim canary (D03).** The clock leg (PC-4 first bullet) is the gating shim-loaded detector on every leg. The stdio leg is an environment check of the end-to-end UTF-8 round trip under the builder env, NOT a shim detector: it stays gating for the UTF-8 round trip, its "discriminates a missing shim" claims are removed, and PC-5's no-shim negative control is dropped.
8. **Windows environment decoding (D08).** `platform.EnvVars` on Windows reads the environment through Go's standard UTF-16 decoding, which substitutes U+FFFD for an unpaired surrogate (documented `unicode/utf16` behavior; not oracle-measured). The "lone surrogate → `invalid UTF-8`" leg is removed from the Windows env path; a table test pins the U+FFFD substitution.
9. **List item order (D06).** Each list item is stripped with Python `str.strip()` semantics first (legacy-identical), then validated (control bytes, emptiness) on the stripped item.
10. **Relative home (D07).** `~` expansion uses the same home source as BC-3.01.001: a relative `HOME` (and on Windows a relative `USERPROFILE`) is treated as unset, giving `home directory unknown`.
11. **E-REN-002 carriers (A01).** Stop hand-maintaining the list: prd.md's E-REN-002 row and error-taxonomy's carrier list are stated as "every owner BC of a degrade-disposition row in the error-taxonomy crash-path register", followed by the derived list, which agent 2 builds by walking the register (CP-X, CP-S, CP-T, CP-N, CP-O, CP-A rows with degrade disposition) and checks against each owner BC's EC text.
12. **Foreign-cache crash triggers (B01).** BC-1.02.018 EC-009 (SL:586 with a non-numeric cached `tin`) and the BC-1.02.007 SL:1181 non-numeric cached bucket are OD-160 foreign-cache vectors: tag them OD-160 and add two CP-C rows (next free CP-C ids) to the error-taxonomy CP-C register.
13. **Request selector (C2-03; orchestrator-measured on CPython 3.11.7: `Request('http://192.0.2.1:8428/a#b#c').selector` is `/a#b`).** The selector drops only the text after the LAST `#` (`_splittag` = `rpartition('#')`), then `_splithost`; pin this for both the initial URL and redirect targets in BC-1.04.001 and ARCH-03.
14. **Negative giant sparkline value (C2-01; measured: `max(-(2**1024), 0.0)` is `0.0`).** Only a positive value >= 2**1024 − 2**970 raises at SL:674; a negative giant draws the lowest glyph; add that row.
15. **Subagent 4,300-digit limit (C02; measured: a 5,000-digit int literal raises ValueError at decode).** CP-A04/A05 triggers are bounded to 309..4300-digit literals; longer literals give `{}` and zero bytes.
16. **Interpreter provenance (C08).** Spec text names the oracle as "CPython 3.11.7 (the oracle interpreter)", never an install path.
17. **ARCH-03 anchors (B02).** The architect adds anchor targets for `input.go` and `statusline.go` to the closed anchor set; the four BCs re-anchor to them.
18. **Everything else** as reported, routed below.

## Agent file sets and findings (routed by file)

| Agent | Role | Files | Findings |
|---|---|---|---|
| 1 | architect | specs/architecture/*, specs/cicd-setup.md | A02 (call 1), A04, A06 (call 5), A07 (call 4, ARCH-08), A08 (call 6), A10, A12 (ARCH-00, cicd-setup), B02 (call 17), B06, D02 (call 2, ARCH-07), D03 (call 7, ARCH-07 if stated), C2-03 (call 13, ARCH-03) |
| 2 | product-owner | specs/prd.md, specs/prd-supplements/*, specs/owner-decisions-log-2026-11-14.md | A01 (call 11), A03, A05, A07 (call 4, nfr-catalog), A09, A11 (call 3, incl. interface-definitions range), A12 (risk-register), B01 (call 12, CP-C rows), B05 (separator range note), C01, C04 |
| 3 | architect | VP-001..VP-020 | A2-02 (VP-019, call 2), A2-03, A2-04, A2-05, A2-06, A2-08, A2-14, A2-16, A2-17, A2-19 (VP-020); C2-02 (VP-001/VP-012 `bcs:` gain BC-1.04.009 and BC-1.04.014 as applicable) |
| 4 | architect | VP-021..VP-041, VP-INDEX, domain-spec/*, product-brief, dtu, gene-transfusion, feasibility | A2-01, A2-07, A2-09, A2-10, A2-11, A2-12, A2-13, A2-15, A2-18 (confirm allowlisted; no change if so), A2-19 (VP-021); B03 (VP-041 generator excludes NaN); VP-INDEX sync for agent 3's `bcs:` deltas |
| 5 | product-owner | ss-01 BC-1.01.*, BC-1.02.* | B01 (call 12), B02 (re-anchor, call 17), B03, B04, B05, B07, B08 |
| 6 | product-owner | ss-01 BC-1.03.*, BC-1.06.*, BC-1.07.* | C02 (call 15), C03, C05, C06, C07, C08 (call 16), C09 |
| 7 | product-owner | ss-01 BC-1.04.*, BC-1.05.* | C2-01 (call 14), C2-02 (BC rows), C2-03 (call 13), C2-04, C2-05, C2-06, C2-07, C2-08, C2-09 |
| 8 | product-owner | ss-02..ss-06 BCs, BC-INDEX, BC-ALLOCATION | D01..D16 (calls 1, 2, 5, 7, 8, 9, 10); A02/A06/A08 BC halves (BC-6.04.001, BC-6.01.001, BC-6.04.002); A07 BC-6.04.002 (call 4) |
