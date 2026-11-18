---
document_type: adversarial-review
phase: 1d
pass: 4
date: 2026-11-17
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM-HIGH
findings: 133
---

# Adversarial Spec Review — Phase 1d, Pass 4

Pass 4 ran as six fresh-context perimeters (A, A2, B, C, C2, D), the same split as passes 1-3. Each section below is the verbatim final report of one perimeter, unedited except for this framing and one absolute local path made repo-relative (public-repo hygiene). Per-perimeter novelty: A HIGH, A2 HIGH, B MEDIUM, C MEDIUM, C2 MEDIUM, D MEDIUM. The pass is NOT_CONVERGED (133 findings: HIGH 39 / MEDIUM 57 / LOW 32 / COSMETIC 5; pass 3 had 150 with 36 HIGH). The orchestrator spot-verified a sample of claims on disk and against CPython 3.11.7 / Go 1.26.5 before triage; all sampled claims held.


## Perimeter A (PRD, supplements, architecture, CI)

Findings: 23 (high 10, medium 6, low 6, cosmetic 1).

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P4-A01 | HIGH | broken anchors [process-gap] | architecture/ARCH-01-binary-cli.md, ARCH-02-configuration.md, ARCH-05-platform.md, ARCH-06-pyfmt.md (no `<a id>` in any of them) | About 40 fragment links in BC bodies point nowhere. Examples: BC-2.02.002:133 `ARCH-02…#seconds`, BC-2.01.004:142 `#registry`, BC-4.01.001:121 `ARCH-01…#dispatch`, BC-5.01.001:130 `ARCH-06…#pyfmt-num`, BC-3.01.001:125 `ARCH-05…#platform-paths`. Pass-3 B10/C15 added explicit anchors only to ARCH-03 (12 total, all in ARCH-03); the sibling docs were not fixed. | architect |
| ADV-P4-A02 | HIGH | contradiction | ARCH-03-statusline.md:79-81 | ARCH-03 says "CP-O09 moot in hylo". error-taxonomy.md:155 says "reachable in hylo (ADV-P3-C09; not moot)". ARCH-03 also calls CP-O10/O11 "stdin-borne", but error-taxonomy.md:124-130 says the bearer is the cost-history cache (OD-166). ARCH-03's step-2 Degrade cell leaves out the OD-167 rule that the in-flight turn is dropped. A story writer working from ARCH-03 would skip CP-O09. | architect |
| ADV-P4-A03 | HIGH | range contradicts BC | prd-supplements/interface-definitions.md:114 | `statusline.git.ttl_s` (type Seconds) is listed as "any finite number; negatives admitted (pass-3 B08)". BC-2.02.002 PC-2, PC-3 and Inv-1 (lines 60-75) apply to every Seconds key: negative is an error, the ceiling is 9223372036.854775, and loaded values are always >= 0. Only one of the two can be implemented. | product-owner |
| ADV-P4-A04 | HIGH | interface cannot express registry (P20) | interface-definitions.md:142,154,156-159,179,180,185,206 | Several keys are typed "Float pair", "Float (triple)", "three finite Floats", "Int map {cc, other}" or "RGB triples + Float", but no HYLO_* grammar exists for any composite type. BC-2.01.005 PC-1..3 (lines 51-72) covers only Bool, List and Path, and ARCH-02:34-36 lists the same three. Nothing says how `HYLO_STATUSLINE_COST_RATE_MIN_API_MS` encodes a map, and there is no reason string for a descending `percentiles` pair. | product-owner / architect |
| ADV-P4-A05 | HIGH | registry not closed (P20, AD-06) | interface-definitions.md:207, 227-231 | The `statusline.glyphs.*` row says "members per BC-2.01.004 registry", but BC-2.01.004 contains no glyph or subagent entries (grep: no matches). BC-1.07.007 Inv-5 (lines 80-82) needs a configurable ` tok` suffix key, and only `tokens.k_from`/`m_from` are registered. That contradicts the claim "every dotted key named in a BC body now carries a row". Env names, the collision test and the unknown-setting warning are all undefined for these members. | product-owner |
| ADV-P4-A06 | HIGH | interface cannot satisfy BC | ARCH-03-statusline.md:47-52, 92, 101-111; ARCH-01-binary-cli.md:32-35 | `Main(stdin, stdout, stderr, env Env)` is said to own step 0 (`config.Load`), but neither its signature nor `Env` carries the `EnvVars` seam that Load needs. `Env.Cache` presupposes `paths.cache_dir` already resolved, which is circular. `Env.Getenv func(string) string` is exactly what the AD-10 amendment forbids ("Never a bare func(string) string"). There is also no `statusline` entry point for the panel body that `runStatuslineSubagent` would call, and the panel needs `Now` (BC-1.07.007). | architect |
| ADV-P4-A07 | HIGH | CI spec vs repo; P11 [process-gap] | cicd-setup.md:50 vs .github/workflows/ci.yml:68-101 | cicd-setup.md says the `test` job runs setup-python first and exports `HYLO_PARITY_PYTHON` before `go test` (pass-3 D22). The landed test job has no setup-python step and no such env. Once internal/parity lands, Tier A runs inside the plain `go test ./...` with no interpreter, so it either fails or quietly skips. | architect |
| ADV-P4-A08 | HIGH | false-green CI job (P11) [process-gap] | cicd-setup.md:24-26 vs :56; ci.yml:322, 343-347 | The timing job is only an `echo`: it passes once `internal/statusline` exists and prints a stale "1 warm-up + 5 timed runs" (the spec says 20). It is gated on the statusline probe, but `TestTiming` lives in `internal/parity` (BC-COMPONENT-MAP:236). cicd-setup.md contradicts itself: line 24 says "still just echoes", line 56 says "runs go test". | architect |
| ADV-P4-A09 | HIGH | PRD row does not match BC H1 (P7/P9) | prd.md:527; test-vectors.md:34; VP-INDEX.md:76 (VP-021 name) | These say "20 seeded sessions". The BC-1.05.008 H1 (line 36) and body (line 40: 12 + 8 + `sess-self`) say 21, and so do prd.md:263 and BC-INDEX:164. | product-owner |
| ADV-P4-A10 | HIGH | duplicate ID (P1) | prd-supplements/assumptions-register.md:24-25 | There are two ASM-002 rows with different content: one cites 2.1.326 and defers to ASM-007, the other does not. | product-owner |
| ADV-P4-A11 | MEDIUM | stale partial fix | interface-definitions.md:93 | The stderr suffix is still "(hylo statusline takes no flags)". BC-4.01.002 PC-3 (lines 61-63) changed it to "(--subagent is the only P1 flag)" because the old text is false since OD-155. | product-owner |
| ADV-P4-A12 | MEDIUM | contradiction | ARCH-02-configuration.md:65-66; interface-definitions.md:212 vs 215-218 | ARCH-02 still calls "the units/context/heat triples" default-only. The interface supplement (and BC-1.02.006 ADV-P3-B07) say context and heat are not default-only, yet line 212 of the same supplement still says BC-1.02.006 "hard-codes pct/10, range(10)". `plain_max`/`red_from` are typed Int there, while BC-1.02.006:23 says "any finite number". | architect / product-owner |
| ADV-P4-A13 | MEDIUM | missing gate [process-gap] | ARCH-08 (whole doc); cicd-setup.md:47-56; nfr-catalog.md:64,75-79 | The OD-158 P1 exit gate (line coverage >= 95% for S1/S5) has no CI job, no coverage-profile producer and no threshold check anywhere in the design. It is also unclear whether `internal/cost` (CRITICAL by inheritance, module-criticality.md:56) falls under the gate. | architect |
| ADV-P4-A14 | MEDIUM | P11 / NFR-006 [process-gap] | cicd-setup.md:95-99; ci.yml:16-17, 132-136, 172 | cicd-setup.md says the A17 categories (hostnames, usernames, session links, UUIDs, product-name rule) were "added" and their regexes "verified before landing". ci.yml scans only IPs, home paths and emails, and prints a fixed "clean" message with no `hygiene: K files scanned, H hits` count. CI only runs on pushes to main and greps the checked-out tree, so the public factory-artifacts branch is never pattern-scanned. NFR-006 requires the scan "on every push". | architect |
| ADV-P4-A15 | MEDIUM | harness can't stay in the closed set | ARCH-07-parity-harness.md:98 | The case `argv` field accepts any array. Legacy ignores every flag except `--subagent` (legacy/dgx_statusline.py:1240), so an argv with an unknown flag diffs on stdout with no exclusion id in the closed set. The spec does not say how case argv maps to the oracle, which has no `statusline` verb. BC-4.01.002:111 still says the harness passes no flags. | architect |
| ADV-P4-A16 | MEDIUM [owner-question] | exclusion mis-anchor (P13/P4) | error-taxonomy.md:129-130 | The OD-166 cost-history cache-byte divergence "rides the extended D4-EX-2". D4-EX-2 is the transcript wrong-shape id, so exclusion entries for cost-history cases would carry an id that means something else. | product-owner |
| ADV-P4-A17 | LOW | P19 hardening | cicd-setup.md:49, 119-122, 182 | govulncheck runs only in the informational security.yml and is not a required check. Lint is gofmt + vet only, with no staticcheck-class analysis. | architect |
| ADV-P4-A18 | LOW | stale propagation | BC-COMPONENT-MAP.md:159, 241-245; interface-definitions.md:221-225 | BC-1.07.008 is mapped to "CP-A01..A03"; it should be A01..A05. The "two-row exception" note is wrong: BC-1.07.001 and BC-1.05.008 also have more than one home. The supplement says the BC-1.07.005 amendment is "pending", but it already landed (BC-1.07.005:21). | architect / product-owner |
| ADV-P4-A19 | LOW | stale counts | risk-register.md:30; prd.md:653; ARCH-INDEX.md:73 | R-005 still says "153/153" (now 154). prd.md:653 has an old total. AD-01 says "six P1 packages", but there are seven modules (module-criticality.md:101). | architect / product-owner |
| ADV-P4-A20 | LOW | P18 completeness | ARCH-05-platform.md:23-30 vs ARCH-02-configuration.md:38-43 | The ARCH-05 file table leaves out `platform.HomeDir()` and the Windows case-insensitive `EnvVars` implementation, both of which ARCH-02 assigns to platform. | architect |
| ADV-P4-A21 | LOW | ambiguity | interface-definitions.md:168-171 | Default "`33` (= `statusline.theme.yellow`)" does not say whether it is a literal value or an alias that follows the theme key when that key changes. | product-owner |
| ADV-P4-A22 | LOW | ambiguity | interface-definitions.md:263-271; ARCH-01:66 vs error-taxonomy.md:56 | The Flag Interactions table has no `--subagent` rows. For a subagent-mode config error, stderr is described as "the E-CFG-001 detail line" in one place and "the reason lines" in another, so it is unclear whether the full list goes to stderr. | product-owner |
| ADV-P4-A23 | COSMETIC | editorial | module-criticality.md:63-79, 131; prd.md:75; ARCH-07:35 | module-criticality.md:131 says platform is something "nothing imports"; it is actually an import sink that everything imports. A blockquote at lines 63-73 breaks the classification table. prd.md:75 has an unbalanced parenthesis. ARCH-07:35 has a malformed bullet. | architect / product-owner |

## 2. Policy compliance
- P1: FINDING A10.
- P2: PASS. No new invariants found that should have been lifted into BCs.
- P4: FINDING A01, A16.
- P5: PASS.
- P6: PASS. The SS-ID/Name rule in ARCH-INDEX is followed.
- P7: FINDING A09, A11.
- P9: FINDING A09 (VP-021 name). VP-INDEX arithmetic (40 = 32+7+1 = 20+12+3+2+1+1+1) and the ARCH-INDEX home mapping (40) agree.
- P11: FINDING A07, A08, A14.
- P12: PASS. OD-155 overriding the PLAN non-goal is settled; A16 is raised only as an owner-question.
- P13: FINDING A15, A16.
- P14: PASS. No real IPs, paths or identities found in the perimeter.
- P16: PASS. Thresholds carry rationale (retry constants, the 1..100 judgment calls, 20 samples).
- P17: PASS. ARCH-04 and ARCH-09 keep the ledger reserved.
- P18: PASS with a LOW note (A20).
- P19: FINDING A17.
- P20: FINDING A04, A05, A06.
- P21: PASS. No flagged strings are quoted here.
- P3, P8, P10, P15: N.A.

## 3. Files not fully read
None in the perimeter; every perimeter file was read in full. Outside the perimeter I opened only targeted pieces: BC-1.05.008, BC-2.02.002, BC-2.01.001, BC-2.01.005, BC-4.01.002, BC-1.02.006, BC-1.05.005 and BC-1.07.005/.007 (by grep), VP-INDEX, and `.github/workflows/ci.yml` on main. release.yml and security.yml were not read.

## 4. Novelty
HIGH. A01, A04, A05, A06, A07, A08 and A15 are new classes of problem, and A02, A09 and A11 are fixes from earlier passes that did not reach sibling files.

NOT_CONVERGED


## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 22 (high 6, medium 11, low 4, cosmetic 1).

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P4-A2-01 | HIGH | contradiction (L2 vs BC) | invariants.md:31; state-machines.md:69-73; capabilities.md:31; ubiquitous-language.md:39; bounded-contexts.md:32 | The L2 says `--subagent` mode prints "JSON lines or zero bytes", "the ladder does not apply" and "never the ladder". BC-1.07.008:36-38, 62-69 says CP-A01..A05 faults in that mode print the 29-byte non-JSON degraded line, with "one ladder, one rung text". The DI-008 carve-out leaves out a real output class. | business-analyst |
| ADV-P4-A2-02 | HIGH | VP skeleton fails a correct implementation | VP-001:113-119 (and :92); VP-005:94-100 | `assertPromisedOutputSet` and the VP-005 fuzz leg fail whenever subagent stdout equals the degraded line, with no condition attached. BC-1.07.008 requires exactly that line for CP-A rows (canonical vector `{"tasks":123}`). VP-001's own table rows for CP-A01..A03, and any fuzz input that is a JSON object, would fail. The intended "parse path only" limit is never coded. | architect |
| ADV-P4-A2-03 | HIGH | partial-fix propagation (blast radius 4 or more) | VP-001:36-44, 87-88; VP-013:37; VP-029:47-48; VP-020; VP-021 | The pass-3 additions were not carried into the VPs. CP-O10/O11 and CP-A04/A05 (error-taxonomy.md:40, 103-105, 121-122, 179-180) are missing from VP-001's "closed" catalogue, even though NFR-002 requires 100% of CP-* triggers. OD-167's turn-drop (CP-O06..O08) and OD-166's record guard have no VP leg anywhere: a grep for OD-166/167, CP-O10/11 and CP-A04/05 across verification-properties/ finds nothing. VP-013's W-predicate check ("mutated on skip") would reject OD-167's `cur`→null. | architect |
| ADV-P4-A2-04 | HIGH | DI-012 closure gap [owner-question] | invariants.md:35; product-brief.md:83; VP-009:41; VP-012:39, 96-98 | OD-166 makes Go skip recording an unconvertible cost while legacy persists it, so cost-history bytes differ from the oracle. BC-1.05.004:65 labels this "exclusion id `OD-166`", which VP-012's closed-set validator rejects. error-taxonomy.md:129-130 instead says it "rides the extended D4-EX-2 discipline", but D4-EX-2 is the transcript wrong-shape class. Tier A, swap (VP-019) or Tier C on such an input has no admissible id, so either the parity referee fails or a blanket exclusion appears. | product-owner |
| ADV-P4-A2-05 | HIGH | Go API misuse (skeleton panics) | VP-021:87-90; VP-030:95-97; VP-040:100-102, 110-113 | `quick.Config.Values` gets a slice of zero `reflect.Value`s that the filler must assign (`args[i] = reflect.ValueOf(x)`). Calling `args[0].Elem().Set…` panics. VP-040's `segCfg` also leaves `args[1]` (`cols int`) unset for a 2-argument function. This regression came from the pass-3 A2-05 fix and was copied into two sibling files. | architect |
| ADV-P4-A2-06 | HIGH | blanket exclusion vs D4/DI-012 [owner-question] | VP-026:47-51 | Every naive local-time conversion case is tagged `posix-only` and skipped "by rule" on the Windows Tier A leg. That is a class-wide carve-out with no closed-set id and no table test. Go (IANA tzdata) and CPython (MS CRT) differ there (VP-026:44-46), and the difference is never named as a deviation. This also bears on P18. | architect |
| ADV-P4-A2-07 | MEDIUM | skeleton fails on POSIX | VP-018:94-99 vs :53-55 | `TestCacheStore_OD110_TempCleanup` expects success after `renameRetryLimit` failed renames. The property says the retry arm is Windows-only and POSIX "reports failure immediately". The skeleton has no OS gate, so a correct implementation goes red on the ubuntu and macos legs. | architect |
| ADV-P4-A2-08 | MEDIUM | ambiguous oracle | VP-002:47-49, 94-104, 113-121 | Rows are said to be "handler-relative" (the harness pins `argv[0]`), yet some rows spell `"statusline"` and others do not. The fuzz oracle checks `argv[1:]` of the raw fuzz vector. If the harness prepends the verb, `joined="--subagent"` routes to subagent while the oracle expects the unknown-flag line, a false failure. `stdin`/`files` are also used as values at :106 and as types at :114 (invalid Go). | architect |
| ADV-P4-A2-09 | MEDIUM | vacuous or contradictory VP | VP-039:88, 91-94, 106-109 | `//go:build arm64 // comment` is not a valid constraint expression. The build tag means nothing compiles on amd64, yet :107-109 claims "the golden comparison still runs" on the amd64 legs. The grid takes a single `ms` delta, but the fusion hazard is `time*1000 - start` at wall-clock magnitude, so the grid cannot exercise the regime it guards. | architect |
| ADV-P4-A2-10 | MEDIUM | semantic mis-anchor (P4) | VP-007:12, 45-46 | VP-007's `source_bc` and Primary BC are BC-1.01.009 (effect order). BC-1.01.009:149-150 explicitly drops VP-007 ("VP-007 is determinism, not effect order", ADV-P1-B11). VP-INDEX:110 still maps the pair, and VP-INDEX:315's claim "No one-sided VP↔BC links remain" is false. | architect |
| ADV-P4-A2-11 | MEDIUM | `bcs:` vs body vs index (P9) | VP-022:13 vs :72-73; VP-006:13 vs :48 | VP-022's body claims partial coverage of BC-1.01.009, but its `bcs:` lacks it. VP-006 pins a BC-1.07.003 row without listing that BC. Neither appears in VP-INDEX:316-317's enumerated prose-only exclusions. | architect |
| ADV-P4-A2-12 | MEDIUM | malformed frontmatter (P9) | VP-001:15 | `proof_method: manualfeasibility: feasible` is invalid YAML and the `feasibility` key is missing. VP-INDEX:34 claims every cell was scripted from frontmatter, with "all feasible". | architect |
| ADV-P4-A2-13 | MEDIUM | stale counts (P2) | invariants.md:31, 35, 46 | The text claims DI-008 = 82 and DI-012 = 57 by the stated grep method. A re-grep of the `ss-0*` files finds 83 and 63 (BC-5.01.007 and later citations not recounted). | business-analyst |
| ADV-P4-A2-14 | MEDIUM | rider test-name drift | VP-003:68 vs VP-012:60, 140 and BC-1.01.001:104; VP-013:69 vs VP-012:55, 135 | `TestCpX03_DegradedWriteFailureExitZero` does not match `TestCPX03_WriteFailureExit0`, and `TestD4EX2_WrongShapeTables` does not match `TestMixCache_OD32_*`. `TestParityExclusions_ClosedSet`'s `TableTestExists` check would fail. The rider names are globs (`*`) inside a "glob-free" machinery, and VP-012:105 only checks `e.Case`. | architect |
| ADV-P4-A2-15 | MEDIUM | stale vs OD-156 | VP-023:44-45; architecture-feasibility-report.md:49 | Both say `math/big` sits at "exactly the two ruled duration-format sites (OD-137)". OD-156 (log:137) adds `_fmt_lines`. VP-023's "entire closed helper set" also leaves out the BC-5.01.007 helpers (NumToF/TrueDiv/NumCmp) that its `bcs:` claims. | architect |
| ADV-P4-A2-16 | MEDIUM | wrong observable in recipe | VP-006:66-67, 48 | The recipe says "depth L renders, L+1 degrades". BC-1.01.002:77, 103 says L+1 decodes to `{}` and renders the 45-byte default line, not the degraded line. Separately, the subagent chain is labelled "main → main_subagent", but legacy SL:1240-1241 calls `main_subagent` from `<module>`, not from `main`. | architect |
| ADV-P4-A2-17 | MEDIUM | P11 inert leg [process-gap] | VP-022:86-90, 136-137 | Enforcement of no direct `os.Open` rests on an AST/imports lint that VP-022 itself says is not in CI (the lint job runs "gofmt + vet only"). No owner or story tracks it, and no positive-coverage count is specified. | architect |
| ADV-P4-A2-18 | LOW | internal contradiction | VP-017:58 vs :40-43, 67 | The Method says cardinality 0/1/2 is tested "through `Load`". The Property and skeleton say 0 is unreachable through `Load` in P1. | architect |
| ADV-P4-A2-19 | LOW | brief drift | VP-036:44-46 vs product-brief.md:88 | The brief allows the over-512 KB fixture exception only if it misses the target. VP-036 exempts it from the gate unconditionally. | architect |
| ADV-P4-A2-20 | LOW | imprecise L2 | state-machines.md:81-82; owner-validation-list.md:215-216 | "+Inf degrades the sample" is too coarse: VP-030:52-53 and BC-1.04.014 say +Inf on the `k` trace is safe and only the `v`/`f` traces degrade. | business-analyst |
| ADV-P4-A2-21 | LOW | stale assessments | dtu-assessment.md:155-162; gene-transfusion-assessment.md:50; architecture-feasibility-report.md:74, 91 | The DTU "not requiring DTU" table leaves out dependency #5 (subagent stdin). "43 crash paths" predates CP-O/CP-A. The "CRITICAL/HIGH kill-rate target" wording contradicts OD-158 (non-gating in P1). | architect |
| ADV-P4-A2-22 | COSMETIC | skeleton consistency | VP-029:81; VP-022:108 vs VP-001:89 | `st != r.Want` on a parser state that holds slices does not compile. `runStatusline` has three different signatures across VPs. | architect |

## 2. Policy compliance

- P1 append_only_numbering: PASS
- P2 lift_invariants_to_bcs: FINDING ADV-P4-A2-13
- P4 semantic_anchoring_integrity: FINDING ADV-P4-A2-10, -11
- P5 creators_justify_anchors: FINDING ADV-P4-A2-10 (the justification "order totality implies seam-closedness" is refuted by the BC)
- P6 subsystem names: PASS (sampled, not exhaustive)
- P9 vp_index_is_vp_catalog_source_of_truth: FINDING ADV-P4-A2-10, -11, -12
- P11 ci_positive_coverage_assertion: FINDING ADV-P4-A2-17 (Tier A/B, exclusion-closure and hygiene count asserts PASS)
- P12 settled_decisions_are_constraints: FINDING ADV-P4-A2-04, -06
- P13 parity_before_behavior_change: FINDING ADV-P4-A2-04, -06
- P14 public_repo_hygiene: PASS (the one ledger-path mention is already public in legacy/)
- P16 thresholds_are_explained: PASS
- P17 ledger_format_frozen: PASS
- P18 cross_platform_from_day_one: FINDING ADV-P4-A2-06, -07, -09
- P19 go_hardening_toolchain: PASS
- P20 config_over_code: PASS
- P21 public_artifact_hygiene: PASS
- P3, P7, P8, P10, P15: N.A.

## 3. Files not fully read

None in the perimeter. For VP files I read from frontmatter line 9 onward; lines 1-8 of VP-001, VP-002 and VP-003 were read in full. I opened only the specific BC files and sections needed to check VP claims (BC-1.07.008, BC-1.01.009, BC-1.01.001, BC-1.01.002, BC-1.05.004, BC-2.01.002, BC-6.03.004), plus error-taxonomy.md:124-133 and grep hits.

## 4. Novelty

Novelty is HIGH. Three findings are regressions introduced or left incomplete by pass-3 fixes: -02 (the subagent "never degraded" assertion), -03 (the CP-O10/11, CP-A04/05 and OD-166/167 propagation) and -05 (the quick.Values misuse copied into three files). -04 (OD-166 has no admissible exclusion id) and -06 (the Windows time-case blanket skip) are new contradictions with settled decisions.

NOT_CONVERGED


## Perimeter B (BC-1.01/1.02)

Findings: 22 (high 5, medium 9, low 8, cosmetic 0).

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P4-B01 | HIGH | config-range contradiction (P20) | BC-1.02.019:62-67, :51-53; interface-definitions.md:142, :215-217 | The BC says `statusline.theme.heat` accepts only the default triple, and any other value is a config error. The registry says the opposite: "three finite Floats, hue span > 0", NOT default-only, because "BC-1.02.019 PC defines the HSV gradient for non-default triples". That is false. PC2 only specifies HSV sectors i ∈ {0,1}, so a hue span ≥ 1/3, which the registry admits, has no defined behavior. | architect + product-owner |
| ADV-P4-B02 | HIGH | mis-anchor (P4) | VP-028:37-39 vs BC-1.02.001:59-64, :82 (legacy SL:446-449 vs SL:905-907) | VP-028 says the lane pill is omitted when the prefix list is empty, "the same rule" as BC-1.07.006. In legacy only the subagent tag disappears (SL:905). The main pill renders the unknown pill (`◨ ?`) and is never omitted (BC-1.02.001 PC3, EC-001). The primary VP would lead someone to write a test that asserts the wrong bytes. | architect |
| ADV-P4-B03 | HIGH | VP over-claim; sibling of the pass-3 B03 fix [process-gap] | VP-028:61-75; BC-1.02.001:111, .004:126, .016:101, .018:106, .019:100-101, .021:108, .022:100-101, .023:96-97, .025:123, .027:94, .028:95 | VP-028 delivers only bounded golden tables ("testable-only; authored corners"). Its frontmatter says `proof_method: manual`, while VP-INDEX says golden. Yet these BC rows claim for-all `testing/quick`, fuzz-vs-oracle, "all float64 inputs", lint and fake-filesystem syscall legs under VP-028. Pass 3 split exactly this gap out of VP-027 into VP-040 for BC-1.01.003..007. The S1.02 family did not get the same split. | architect |
| ADV-P4-B04 | HIGH | missing required vectors (sibling propagation) | error-taxonomy.md:106, :116-120; test-vectors.md:43; BC-1.02.006:118-129, .011:92-106, .012:91-107, .014:104-122, .017:94-102, .020:91-103, .025:87-114 | The taxonomy requires each owning BC to carry its CP-O trigger "as an edge case + canonical vector". test-vectors.md claims "1+ per trigger" in these seven BCs. None of the seven vector tables has an overflow row; I checked each one. Also, BC-1.02.011 EC-010, .012 EC-012, .014 EC-013, .017 EC-010 and .025 EC-010 never name CP-O02/O03/O04/O05. Only .006 and .020 got a CP-O id in the pass-2 fix. | product-owner |
| ADV-P4-B05 | HIGH | unnamed deviation (DI-012, P13); partial fix | BC-1.02.005 EC-009/EC-010 :91-92 and :110; BC-1.02.013 EC-008 :87 and :108; BC-1.01.009 footnote :66-70 and rows 3/4/6/7a/7c; BC-1.02.017 Inv 3 :64-71, EC-004..006, :102; BC-1.02.028:86; BC-1.02.027 EC-006 | OD-160 (OD log:144) names CP-C01..C10 as a closed-set exclusion. These rows still describe foreign-cache behavior as an unnamed "documented known difference (Q-b), not byte-compared". BC-1.02.017 contradicts itself: "No case of this contract is excluded", then it excludes EC-007. Its NaN/±Infinity `win_start` cases, which are only reachable through a hand-edited `proc_start`, are untagged. | product-owner |
| ADV-P4-B06 | MEDIUM | internal contradiction | BC-1.02.004:136 vs :48-56, :128 | The Traceability row says "byte-exact (no exclusion-list entry)", but the same BC defines exclusion OD-159 and gives it a VP-012 closure row. | product-owner |
| ADV-P4-B07 | MEDIUM | invariant anchoring (P2/P5) | BC-1.02.001:123; Traceability of BC-1.01.001, .008, .009, BC-1.02.004, .005, .013, .017, .030 | DI-012 is cited only by BC-1.02.001, which defines no deviation. The eight BCs that do carry closed-set ids (cp-x03, OD-159, OD-160, D4-EX-2/3, temp-file) cite only DI-007/DI-008. | product-owner |
| ADV-P4-B08 | MEDIUM | config type mismatch (P20) | BC-1.02.006:85-88 vs interface-definitions.md:137-138 | The BC says `plain_max`/`red_from` accept any finite JSON number. The registry types them Int ("any Int"), so 50.5 is valid per the BC and a config error per the registry. Row :137 also describes plain_max as the "`min(…,n)` gate", which is the cells formula. | architect |
| ADV-P4-B09 | MEDIUM | sibling not updated (pass-3 A27) | interface-definitions.md:136 vs :150, :152; BC-1.02.006:84 | `statusline.context.cells` is only bounded `>= 1`. `kv.cells` and `sparkline.points` got a 1..100 cap for the same reason (O(cells) render work and width against the 25 ms p95 budget). cells = 10⁹ would build a billion-cell bar on every refresh. | architect |
| ADV-P4-B10 | LOW | stale rationale (P16) | interface-definitions.md:212 vs BC-1.02.006:58-60 | The reason given for `units.context` being default-only is "BC-1.02.006 hard-codes pct/10, min(…,10), range(10)". Those are now parameterized on `cells`. The real reason (the fixed 1e6/1000 M/K divisors) is not stated. | architect |
| ADV-P4-B11 | MEDIUM | partial fix (pass-3 B16) | BC-1.01.002:145 vs :113-114, :23 | VP-001 was removed from the VP table but is still listed in the VP Anchors section. | product-owner |
| ADV-P4-B12 | MEDIUM | settled decision not propagated (P12) | BC-1.01.001:44-47, :38 vs OD-168 (OD log:155), PRD:435 | The BC brings `--subagent` under this contract and says a config error "renders the D4-EX-3 line". OD-168 says a config error in `--subagent` mode prints zero stdout bytes. "Never blank" also ignores the PRD's carve-out for that mode. | product-owner |
| ADV-P4-B13 | MEDIUM | malformed frontmatter | BC-1.02.006:21-22; BC-1.02.020:21 | BC-1.02.006 has the `modified:` key twice. Strict YAML (Go yaml.v3) rejects duplicate keys, and lenient parsers silently drop the first list. Both files also repeat the same history entry twice. | product-owner |
| ADV-P4-B14 | MEDIUM | mis-anchor | error-taxonomy.md:122 (legacy SL:255, SL:550-553, SL:622-623) | CP-O11 is labelled "API-time suffix (SL:623) … api_ms from the cost history". SL:622-623 is the `$/h` burn rate and uses stdin `api_ms`. The cost-history division is SL:255. The API-time suffix is BC-1.02.016, whose `_hm` uses integer arithmetic only and cannot overflow. | architect |
| ADV-P4-B15 | MEDIUM | conflict with settled OD-02 (P12) | BC-1.02.018:67-68; interface-definitions.md:207; OD log:7 | BC-1.02.018 makes the two-character `in` label a member of `statusline.glyphs.*`. OD-02 requires each glyph to be exactly 1 code point and 1 column. The registry's glyph range ("non-empty, no control bytes") also drops the OD-02 rule. | product-owner + architect |
| ADV-P4-B16 | LOW | decision mis-cite [owner-question] | BC-1.02.001:67-68 | The pill words DGX/ANTH/? are frozen by citing D7, but D7 covers the ledger format and metric names. No config key exists for them (OD-113 covers SGR codes, pill codes and separator only). Does P20 require a label key? | product-owner |
| ADV-P4-B17 | LOW | title vs postconditions (P7) | BC-1.02.003:30 (also BC-INDEX:72, PRD:171) vs :46 | The title says `basename(normpath(cwd))`. The postconditions select `workspace.project_dir`, then `workspace.current_dir`, then `cwd`. | product-owner |
| ADV-P4-B18 | LOW | unspecified parity edge (P18) | BC-1.02.004:60-75 | Path encoding for lone surrogates is unspecified. Assuming standard CPython path encoding (not run): U+DC80..DCFF become raw bytes, so `.../\udcff/sub` stats a real 0xFF directory, and other surrogates count as not-a-directory. A WTF-8 Go port stats the three bytes ED B3 BF. The label `sub` does not degrade, so the branch can differ. | product-owner |
| ADV-P4-B19 | LOW | stale circular cross-refs | error-taxonomy.md:134-135; BC-1.02.027:159-160 | Each document says the other holds a superseded int64 sketch. BC-1.02.026 PC2 is now exact beyond int64, and error-taxonomy:120-124 now holds the CP-O05/O10/O11 rows. | architect |
| ADV-P4-B20 | LOW | capability mapping | PRD:553-554 vs BC-1.02.029:15, BC-1.01.003/.009/.010 Traceability | The PRD maps all of BC-1.01/1.02 to CAP-009. BC-1.02.029's frontmatter says CAP-011, and BC-1.01.003/.010 add CAP-010, BC-1.01.009 adds CAP-011. | product-owner |
| ADV-P4-B21 | LOW | misnamed key [owner-question] | BC-1.02.029:57-59, :65-67; interface-definitions.md:187 | `cost.basis_min_shown_usd` is a display floor, not a basis minimum. The BC needs a disclaimer in two places to say so. The key is not yet shipped, so renaming is cheap. | architect |
| ADV-P4-B22 | LOW | incomplete registry description | interface-definitions.md:111 vs BC-1.01.003:50 | The `statusline.rows` row says "row 2 shown when rows >= 2" and omits the width condition. | architect |

All other postconditions and canonical vectors I re-derived match the legacy code (thermometer colours, mix rounding, countdowns, band boundaries, _hm/_fmt_* outputs, the sticky CP-S09 sequence, and the staircase arithmetic).

## 2. Policy compliance
- P1 append_only_numbering: PASS
- P2 lift_invariants_to_bcs: FINDING B07
- P4 semantic_anchoring_integrity: FINDING B02, B03, B14
- P5 creators_justify_anchors: FINDING B07, B16
- P6 subsystem name: PASS (all "SS-01", matches ARCH-INDEX:54)
- P7 titles: H1 = BC-INDEX = PRD for all 40 BCs; FINDING B17 (LOW)
- P12 settled_decisions_are_constraints: FINDING B12, B15
- P13 parity_before_behavior_change: FINDING B05
- P14 public_repo_hygiene: PASS
- P16 thresholds_are_explained: FINDING B10; otherwise PASS
- P17 ledger_format_frozen: PASS (no ledger reads or writes; DI-007)
- P18 cross_platform_from_day_one: PASS (B18 is a LOW note)
- P19 go_hardening_toolchain: PASS (no-FMA rule and arm64 leg specified)
- P20 config_over_code: FINDING B01, B08, B09, B16
- P21 public_artifact_hygiene: PASS

## 3. Coverage gaps and unverified Python claims
- **Files not fully read:**
  - For the BC frontmatter, I grepped only version, subsystem, capability, parity_class and confidence (all 40 files). The bodies were read in full.
  - Partially read: ARCH-03 (lines 40-165), interface-definitions (95-239), error-taxonomy (100-149 plus greps), and capabilities, invariants and test-vectors (grep only).
  - Not opened beyond their VP-INDEX rows: VP-001/003/005/006/008/009/012/019/027.
  - Not read: docs/STATUSLINE-WIDGETS.md and the review doc.
- **Python claims I could only reason about, not run:**
  - Stdin depth limit 993/994.
  - SHA-1 cache keys (5a3006…, 09d473…, a77db2…).
  - The 4,300-digit limit counting with underscores.
  - Windows `ntpath` C-implementation results.
  - Golden A/B/C byte totals (701/809/642/286/743) and the segment widths (only re-summed).
  - Float edge products (0.015×100, 0.135×100, 1.15×length, 0.95×D7), which I derived by hand, not on CPython.
  - The surrogateescape stat behaviour in B18.

## 4. Novelty
Novelty is MEDIUM. B01, B02, B04, B08, B09, B12, B14 and B15 are new. B03, B05, B07 and B11 are sibling-propagation regressions from pass-3 fixes. Several findings are HIGH or MEDIUM, so this pass is not converged.

NOT_CONVERGED


## Perimeter C (BC-1.03/1.06/1.07)

Findings: 15 (high 3, medium 7, low 4, cosmetic 1).

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P4-C01 | HIGH | contradiction / settled decision | BC-1.07.002:89, EC-004 :80 | The vector says `statusline.subagent.enabled = "yes"` is a config error with reason `boolean expected`. The typed-boolean grammar (OD-05) accepts `yes` as true: BC-2.01.005:52-53, BC-2.02.006:58, interface-definitions:102. The canonical reason text is also different: `not a boolean (true\|false\|1\|0\|yes\|no)` (BC-2.02.001:105). A test written from this row asserts the wrong result. | product-owner |
| ADV-P4-C02 | HIGH | mis-anchor | BC-1.07.006:109 vs PC2 :52-53 | The Config-keys row sources the pill SGR from "the same keys BC-1.02.001 PC4 sources". Those keys are `statusline.theme.pill_local` / `pill_cloud`, whose defaults are `106;30;1` / `105;30;1` (BC-1.02.001:65-67, interface-definitions:130-131). The subagent pill uses CYAN `36` and MAGENTA `35` (SL:906-907), and this BC's own PC2 says so. Building from the anchor breaks byte parity. | architect |
| ADV-P4-C03 | HIGH | mis-anchor (refactoring guidance) | BC-1.07.003:151; BC-1.07.004:166 | The notes prescribe Go `json.Unmarshal` and `task.(map[string]any)`. That decoder rejects `NaN`/`Infinity` (Python accepts them and renders rows). It turns `\ud800` into U+FFFD, which contradicts BC-1.07.004 row 4 (:91, wire `a\ud800b`). It reads big-int ids as float64, which breaks PC4's verbatim echo. A Go map plus `json.Marshal` reorders object-id keys. It has no CPython depth budget. It should be `pyfmt.Decode(ModeText)` (BC-1.01.002, BC-5.02.003). | product-owner |
| ADV-P4-C04 | MEDIUM | config over code; partial fix not propagated to a sibling BC | BC-1.07.004 PC7 :61-63 | The joiner bytes are hard-coded. `statusline.subagent.joiner` is registered against BC-1.07.004 (interface-definitions:172), and :221-225 says the sibling BC amendments are still pending. BC-1.07.005/.006/.007 got the ADV-P3-C05 config sourcing; BC-1.07.004 has no `statusline.` reference at all (grep). | product-owner |
| ADV-P4-C05 | MEDIUM | config over code / OD-162 | BC-1.07.007 Inv5 :80-82, PC1 :53-57 | Inv5 says the ` tok` suffix comes from `statusline.subagent.tokens.*`, but the registry has only `k_from` and `m_from` (interface-definitions:173-174); no suffix key exists. The registry also admits any `k_from > 0` with `k_from <= m_from`, while PC1 hard-codes the `/1000` and `/1e6` divisors. Non-default behavior is undefined (does the divisor follow `k_from`?). Under interface-definitions:209-211 the keys must then be default-only, or the BC must define them. | architect + product-owner |
| ADV-P4-C06 | MEDIUM | spec vs legacy | BC-1.07.005 PC3 :52-53 vs Inv3 :69-70; SL:921 | PC3 says "status present and not running → grey suffix". Legacy tests `if st and st != "running"`, so a present but falsy status (`""`, `0`, `false`, `null`) adds no suffix. Inv3 states this correctly, so the BC contradicts itself. No edge case or vector covers a present falsy status. | product-owner |
| ADV-P4-C07 | MEDIUM | config over code, ambiguity | BC-1.07.005:170-172; interface-definitions:164-171 | The unknown-status fallback `("◍", GREY)` (SL:894) has no key. The note says "packed default drawn from the same keys" but never names which key. If the owner changes `glyphs.killed`, it is unspecified whether unknown statuses follow. A Go literal here would violate D15. | architect |
| ADV-P4-C08 | MEDIUM | W-predicate gap (confidence M) | BC-1.03.018:74-75; BC-1.03.006 PC3 :55-60 | The CP-O06 predicate lists only the SL:1108 and SL:1112 sites; CP-O07 covers only a float `pp` meeting a huge `_w`. Legacy also overflows at SL:1109-1111 and at SL:1117 when a huge-int `pp` meets a float `prompt`. These are reachable with negative tokens, which BC-1.03.006 EC-006 admits. Example: line A `{"input_tokens": -10^309, "cache_creation_input_tokens": 10^309}`, then line B `{"cache_creation_input_tokens": 1.5}`. SL:1108 succeeds (0 + 1.5) and SL:1110 raises. Following the row-wise predicates, hylo would either degrade (breaking BC-1.03.018 Inv3) or diverge with no exclusion. The general rule in error-taxonomy:140 already covers this case. | product-owner |
| ADV-P4-C09 | MEDIUM | test vector cannot be reproduced | BC-1.03.010:111 vs :102 | The CP-O08 row never defines its line templates, and the BC points to BC-1.03.016's templates. With those templates, U0 + A2(10^309) + B10 is 100 + 467 + 160 = 727 B with conv 3, not the pinned 656 / conv 5. The pinned "131 deleted bytes" implies a B10 with string content `""`, which no template in scope defines. | product-owner |
| ADV-P4-C10 | MEDIUM | index drift | BC-INDEX.md:119 vs BC-1.03.015:17, :109 | The index parity column says `byte-exact`; the BC's frontmatter and traceability say `OD-161`. | product-owner |
| ADV-P4-C11 | LOW | contradiction | prd.md:496, error-taxonomy:40 vs BC-1.03.006 PC5 :67-74, error-taxonomy:155-161 | The PRD and taxonomy say CP-O06..O09 "resolve to the D4-EX-2 skip". BC-1.03.006 PC5 says CP-O09 is explicitly not skipped: hylo reproduces the no-write. | product-owner |
| ADV-P4-C12 | LOW | stale anchor labels (targets are correct) | BC-1.07.001:107, :122; :80, :109; BC-1.07.008:54 | ARCH-03:133-135 should be :137-138 (where `subagent.go` placement is). The launcher cite "claude-dgx:176" should be legacy/claude-dgx:177. The env cite "SL:903-905" should be SL:902-903. | product-owner |
| ADV-P4-C13 | LOW | missing error path [owner-question] | BC-1.07.008 EC-005 :84 | Only an EPIPE while writing the degraded line is ruled. A write failure while printing the rows is unspecified for this entry point. In legacy, BrokenPipe goes to the guard, the degraded print also fails, and the process exits 1. It is unclear whether cp-x03 extends to this case. | product-owner |
| ADV-P4-C14 | LOW | unstated assumption | BC-1.07.003 PC1 :47, EC-006 :71 | "Non-UTF-8 → zero bytes" holds only under the strict UTF-8 parity locale pinned in BC-1.01.008. Under a C locale or `PYTHONUTF8=1`, surrogateescape lets legacy render rows. The BC cites neither BC-1.01.008 nor BC-1.01.002, and omits the BOM case (U+FEFF → JSONDecodeError → `{}`). | product-owner |
| ADV-P4-C15 | COSMETIC | precision | BC-1.07.006 Pre2 :47, EC-004 :78 | "Entries stripped" does not name Python Unicode whitespace (`pyfmt.Strip`) the way BC-1.02.001:50 does. It is moot in practice because both read the one config list. | product-owner |

Re-derived and correct: these vectors all match byte counts I derived from the cited legacy lines and templates (cache `size`, `conv`, `tin`/`tout`, `lr`, `rb`/`pp`, and the 10^309 digit count in C09's row, checked by grep):
- BC-1.03.002, .005, .006, .007 (including the CP-O06 and CP-O07 vectors)
- BC-1.03.008, .009, .012, .016 (T1, T13, T16), .019 (rows 1-2, 7, 11, 13, 15, 16, 19), .020 (C1-C3), .021
- BC-1.07.004/.005/.007: escapes and `_fmt_tokens` cells

## 2. Policy compliance
- P1 PASS.
- P2 PASS: DI-007/008/012 are cited throughout.
- P4 FINDING: C02, C03, C12.
- P5 PASS.
- P6 PASS: all 31 BCs use `SS-01`, matching ARCH-INDEX:54.
- P7 PASS on titles: all 31 H1s match BC-INDEX, and the PRD S1.07 rows match. Index parity-column drift is reported as C10.
- P12 FINDING: C01 (OD-05 grammar).
- P13 PASS, with C08 as a risk of an unexcluded divergence.
- P14 PASS.
- P16 PASS: T-054/055/056/057/058/059/060/042 all carry rationale.
- P17 PASS: the ledger is untouched and the mix-cache format is pinned.
- P18 PASS: the Windows legs are honestly marked "not executed".
- P19 N.A.
- P20 FINDING: C04, C05, C07.
- P21 PASS: I quoted nothing flagged that I could detect. I could not read the hygiene term list.

## 3. Not fully read, and Python claims not verified
- **Not fully read:**
  - Frontmatter (lines 1-29) and trailing anchor sections of BC-1.03.004 through BC-1.03.021, and BC-1.06.001 past line 138.
  - ARCH-03/ARCH-04 (grep only), capabilities.md, invariants.md and test-vectors.md: not read.
  - VP files: only the VP-INDEX rows and a grep of VP-002.
- **Python claims not verified (no oracle run):**
  - C08's overflow at SL:1110 and SL:1117 is derived from CPython semantics.
  - `os.path.isfile(True)` behavior is not checked.
  - That every decoded NaN, from the cache and the transcript alike, is the same `json` constant object is reasoned, not run.
  - The OSError on a negative `seek` is taken from BC-1.03.002 EC-009.

## 4. Novelty
MEDIUM. C01-C03, C05, C08 and C09 are new defects. C04 and C10 are fixes that did not propagate. **NOT_CONVERGED.**


## Perimeter C2 (BC-1.04/1.05)

Findings: 17 (high 4, medium 9, low 4, cosmetic 0).

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P4-C2-01 | HIGH | Wrong test vector (Python result) | BC-1.04.001:145, :158; legacy SL:177-180 | EC-018 and the 309-digit vector use 10**308 ("1 then 308 zeros") as the overflow case. But 10**308 is below DBL_MAX (about 1.797e308): `float(10**308)` returns `1e+308` and does not raise. Legacy gives `{"y": 7.0, "x": 1e308}`, not "no sample". The overflow example must be at least 2**1024 - 2**970. | product-owner |
| ADV-P4-C2-02 | HIGH | Wrong test vector (contradicts PC4/EC-011) | BC-1.04.001:159; SL:176 | The vector `[{ "__name__": "5", "value":[1,"1"]}, …]` has no `metric` wrapper. `s["metric"]` raises KeyError outside the per-series catch, so legacy returns no sample (EC-011). The stated "two keys stored, one `"5"` holding 2.0" cannot happen. EC-020 intends `{"metric":{"__name__":…}}`. | product-owner |
| ADV-P4-C2-03 | HIGH | Exclusion id outside the closed set; contradiction | BC-1.05.004:65 vs error-taxonomy.md:129-130, :189-192; owner log :142, :153 | BC-1.05.004 PC1 cites "exclusion id `OD-166`". OD-166 is not one of the ten closed ids. The taxonomy instead says the cache-byte divergence "rides the extended D4-EX-2 discipline" and the set is unchanged. D4-EX-2 is the transcript skip rule, so applying it to a stdin cost-history write is a mis-anchor. VP-012 rows cover only OD-160/OD-30, so the legacy-writes / hylo-skips cost-history difference in a CP-O10/O11 parity case has no working exclusion. [owner-question]: own id, or which existing id? | product-owner / architect |
| ADV-P4-C2-04 | HIGH | Partial fix not propagated (blast radius 6+) | VP-021:33, :37, :44, :72, :80 (`SeededSessions20`), :105, :112; VP-INDEX.md:76; prd.md:527; test-vectors.md:34; BC-ALLOCATION.md:481 | Pass 3 changed BC-1.05.008 to 21 seeded sessions (12 s + 8 g + sess-self; checked). The VP-021 H1, VP-INDEX title, PRD body row, test-vectors register and BC-ALLOCATION prose still say 20. | architect / product-owner |
| ADV-P4-C2-05 | MEDIUM | OD-166 deviation not carried through | BC-1.05.009:45-47, :25 (parity_class OD-30); BC-1.05.004:25 (byte-exact), :124-131 (DI-007 only); VP-020 (no OD-166 leg) | BC-1.05.009 says "the only permitted difference is the OD-30 sub-case", but OD-166 adds a second write difference (huge-int usd/api_ms not recorded). BC-1.05.004 is labelled byte-exact, does not cite DI-012, and no VP covers the guard. | product-owner |
| ADV-P4-C2-06 | MEDIUM | Guard scope ambiguous; possible output divergence | BC-1.05.004:60-68, :102 vs BC-1.05.002:68-72; SL:226, :235, :622 | The BC-1.05.004 guard checks only `usd` ("and the paired api_ms"). BC-1.05.002 PC5 says a huge `api_ms` alone also blocks the record. A test written from BC-1.05.004 would record it. Also undefined: a negative huge `api_ms` fails the `>= 300000` gate, so legacy renders normally and records it harmlessly. A magnitude-only guard would drop that session's cost, changing other sessions' percentile colours with no exclusion. The guard needs: which field, and whether it is sign- or gate-aware. | product-owner |
| ADV-P4-C2-07 | MEDIUM | Redirect prose wrong; rule key ambiguous | BC-1.04.001:64-67, :70-72 | With CPython 3.11.7 `redirect_dict`: (a) worst case is 9×4 + 1 = 37 hops, not 40, because once `len >= 10` every further redirect is refused. (b) "A→B→A→B…→C whose intermediate targets are pairwise distinct … followed even at 11+ hops" contradicts itself: A/B repeat, and a pairwise-distinct chain is refused at redirect 11. (c) The key "whose `Location` is `L`" could mean the raw header, but urllib keys on the resolved, quoted `urljoin(req.full_url, quote(newurl))`. Keying the raw header splits `/x` and `http://h/x` into two keys. | product-owner |
| ADV-P4-C2-08 | MEDIUM | Missed urllib quirk | BC-1.04.001:54-57 | CPython `http_error_302` reads `location`, then falls back to a `uri` header. A 301/302/303/307/308 with only `URI:` is followed by legacy; Go's client and the BC's rule ("Location") do not, so legacy gets a sample and Go gets none. This shows up under the VP-030 "any response bytes" fuzz. Pin the URI fallback (from memory of 3.11 stdlib source, not re-run). | product-owner |
| ADV-P4-C2-09 | MEDIUM | Transport behaviour not pinned | BC-1.04.001:51-57, :75-76 | Go's default Transport sends `Accept-Encoding: gzip` and silently decompresses. urllib sends `identity` and parses raw bytes with `json.loads`. A gzip response legacy never asked for: legacy gets no sample, Go gets a sample, so VP-030 fails. The BC should require `DisableCompression: true` (or an equivalent). | architect |
| ADV-P4-C2-10 | MEDIUM | Taxonomy contradicts BC and ARCH | error-taxonomy.md:121-125 vs BC-1.05.007:64-79, ARCH-03:79-81; SL:601-603, :616, :623 | The taxonomy says the CP-O10/O11 trigger is a huge int "from the cost history". SL:616 and SL:623 read stdin `cost.total_cost_usd` / `total_api_duration_ms`. The cost-history crash site is SL:255 (BC-1.05.005 EC-011), not SL:616/623. | architect |
| ADV-P4-C2-11 | MEDIUM | ARCH table contradicts its own crash register | ARCH-03:66 vs :79-81 | Effect step 7d ($, $/h, ⛏) says Degrade? "no", but CP-O10 (SL:616) and CP-O11 (SL:623) degrade in exactly that step. | architect |
| ADV-P4-C2-12 | MEDIUM | Crash path missing from the register | BC-1.04.004:62-65; BC-1.04.005:71; BC-1.04.001:140; SL:717; error-taxonomy (no SL:717 row); ARCH-03:61 | The metrics-borne degrade (numeric `__name__` key ahead of every `vllm:` key; AttributeError at `k.startswith`) is called a "named" crash path but has no CP-* id. ARCH-03 step 5 lists only CP-N01/N02, so Go would rely on the `recover()` backstop rather than a typed site (IM-15). | architect |
| ADV-P4-C2-13 | MEDIUM | Config over code (P20) | BC-1.04.003:62-63; interface-definitions.md:151; semport pass-4-deep-nfr-r2:260 | T-107 (history `p` marker at preempt > 0) has no config key. The NFR plan tied it to the queue rule map, but `statusline.queue.yellow` is now a Bool. The threshold is hard-coded, and it is unspecified whether `queue.yellow=false` affects `p`. | architect |
| ADV-P4-C2-14 | LOW | Claim false under allowed config | BC-1.04.003:64-65; interface-definitions.md:152-153 | "Output-neutral: the sparkline reads only the last 12" holds only when `points <= history_cap`. With points 100 and cap 32 (both in range), the fetch-path render plots up to about 45 points and the next cached render plots 32. | product-owner |
| ADV-P4-C2-15 | LOW | Crash outcome missing from edge case | BC-1.04.003:84; SL:336-337 | EC-008: a `{}` point is kept when `now < 90`, then `hist[-1]["t"]` raises KeyError and the line degrades. The EC says only "dropped unless now < 90". | product-owner |
| ADV-P4-C2-16 | LOW | Ambiguous wording | BC-1.04.013:50 | "Not a number (bool included)" reads as "bool → none". Legacy accepts `True` as a number (`True <= 0` false, so it is kept); only `False` becomes None. | product-owner |
| ADV-P4-C2-17 | LOW | Postcondition omits configured branch | BC-1.04.006:43-50 | PC3's colour formula uses only `busy`; the `statusline.queue.yellow=false` (never yellow) branch is stated only in the preconditions. | product-owner |

Checked against legacy and matching (no finding): BC-1.04.002/004/005/007/008/009/010/011/012/015/016/017/018/019/020 (all 11 steps re-derived), BC-1.04.021, BC-1.05.001/003/005 (NaN sort orders and the index table checked), BC-1.05.006 and BC-1.05.008 (thresholds ((24,30),(20,26)) re-derived).

## 2. Policy compliance

- P1 append_only_numbering: PASS (BC-1.05.002 EC-009 is out of order on the page but not renumbered).
- P2 lift_invariants_to_bcs: FINDING 05 (BC-1.05.004 carries a deviation without citing DI-012).
- P4 semantic_anchoring_integrity: FINDING 03 (OD-166 / D4-EX-2 mis-anchor), 04.
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS (all 30 BCs are "SS-01", matching ARCH-INDEX:54).
- P7 H1 = BC-INDEX = PRD: PASS (30/30 match); FINDING 04 for the related VP title and PRD body row.
- P12 settled decisions: PASS (OD-166 and OD-157 applied; the question is raised as [owner-question] in 03).
- P13 parity before behaviour change: FINDING 03, 06, 08, 09.
- P14 public repo hygiene: PASS (only RFC 5737 192.0.2.10 appears).
- P16 thresholds explained: PASS, except the urllib caps 4/10 have no "why not config" note (part of 07).
- P17 ledger format frozen: PASS (metric wire name kept, BC-1.04.012).
- P18 cross-platform: PASS.
- P19 Go hardening toolchain: N.A.
- P20 config over code: FINDING 13.
- P21 public artifact hygiene: PASS.

## 3. Not fully read, and claims I could not verify

- **Not fully read:** VP-001, VP-012, VP-019, VP-022, VP-030, VP-031 (searched only); ARCH-04; capabilities.md; invariants.md; prd.md body; test-vectors.md (searched only); interface-definitions.md (statusline rows only). I also did not read the frontmatter lines 1-25 of the BC-1.05.* files.
- **Python claims not re-run:**
  - `f"{999.995:.2f}"` gives `1000.00` (BC-1.05.007 EC-005).
  - Sparkline fade RGB values beyond the samples I hand-computed.
  - The CPython 3.11.7 `http_error_302` `uri` fallback and its key normalization, recalled from stdlib source and not run here.
  - The percentile index table up to n = 10,000.

## 4. Novelty

MEDIUM. Two test vectors give results legacy would not produce (01, 02). Fixes from pass 3 have new gaps: the OD-166 exclusion id (03, 05, 06) and the 21-session count (04). The urllib redirect and transport findings are new (07, 08, 09).

NOT_CONVERGED


## Perimeter D (S2-S6 BCs)

Findings: 34 (high 11, medium 15, low 6, cosmetic 2).

## Adversarial Review: Phase 1d Pass 4, Perimeter D (SS-02..SS-06)

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P4-D01 | HIGH | contradiction / test vector | BC-2.01.001:117 | The all-defaults vector says `queue.yellow false`. interface-definitions.md:151 and BC-1.04.006:43 both give default `true`, which is legacy's rule `q > 0 or preempt > 0`. Building to this vector breaks parity on row 2. | product-owner |
| ADV-P4-D02 | HIGH | contradiction | BC-1.07.002:89 vs BC-2.02.006 PC-1/2, BC-2.01.005 PC-1 | The subagent toggle vector treats `yes` as invalid. It uses the reason `(boolean expected)`, which is not in the BC-2.02.001 vocabulary, and the stderr line has no `[from …]`. The typed grammar accepts `yes` as true. Out-of-perimeter file that contradicts in-perimeter BCs. | product-owner |
| ADV-P4-D03 | HIGH | contradiction (OD-155/168) | BC-4.01.001:68 (Inv 1), :98 (VP-004), :51-55 (PC-1) | "runStatusline never leaves stdout empty" and the fuzz property "stdout non-empty for every `statusline` argv" both fail on the zero-byte subagent outputs: BC-1.07.001 CTV :87, BC-1.07.004 PC-6, and BC-2.02.001 PC-8. PC-1 also never routes `--subagent` to BC-1.07.001. | product-owner |
| ADV-P4-D04 | MEDIUM | contradiction | BC-2.02.001:132-133 (PC-8) | Says "an unknown flag still wins before config resolution" in subagent mode. BC-1.07.001 EC-002 (:78) and BC-4.01.002 EC-004 say other flags are not validated in that mode. An unknown-flag grey line on stdout would also break the NDJSON wire. | product-owner |
| ADV-P4-D05 | MEDIUM | partial-fix regression | BC-4.01.002:111 | Still says "no parity case passes flags; the harness invokes `hylo statusline` without flags". ARCH-07:98 explicitly superseded that, and BC-6.02.003 PC-4 sends argv such as `["--","--subagent"]`. | product-owner |
| ADV-P4-D06 | HIGH | untestable / P18 | BC-3.02.001:60-62 vs :121 | PC-2b strips `.exe` without regard to case and then compares the name exactly, case-sensitive. So `CLAUDE.EXE` becomes `CLAUDE` ≠ `claude`, yet the Windows vector expects a match. ARCH-05:26 is silent on how the name itself is compared on Windows. | architect |
| ADV-P4-D07 | HIGH | interface / ARCH-06 signatures | ARCH-06:112-113 vs BC-5.02.006:38, BC-5.02.001:83 | ARCH-06 has `Dumps(v) []byte` and `DumpsLen(v) int`. The BCs (ADV-P3-D12) require `([]byte, error)` and `(int, error)` for the 4,300-digit encoder failure. ARCH-06's "Signature canon" section claims the signatures are reconciled. | architect |
| ADV-P4-D08 | HIGH | partial-fix regression / CI | BC-6.04.001:65-74 (PC-3) | Step 3 is `go test ./...`, which includes Tier A; setup-python only comes at step 4. GitHub always sets `CI=true`, so BC-6.01.001 PC-6 makes Tier A fail on every leg. ARCH-08:51-56 fixed this (pass-3 D22) but the BC was not updated, and ARCH-08's own diagram (:41-42) still shows the old order. [process-gap] | architect |
| ADV-P4-D09 | HIGH | contradiction / harness argv | BC-6.02.003:75-82 vs BC-6.01.001:76-83, :93, :124 | BC-6.02.003 appends the same argv to the oracle, so `["--","--subagent"]` becomes `[…script, "--", "--subagent"]`. BC-6.01.001 PC-5 allows only a single `--subagent` and says "no other script arguments". Inv 2 and VP-034 still require exactly `[python,-s,script]` for every case shape. ARCH-07:98 defines `argv` as the full binary argv (default `["statusline"]`) while the BC default is `[]`, so the case.json schema is ambiguous. | architect |
| ADV-P4-D10 | HIGH | anchor / path contradiction | BC-6.02.001:61, BC-6.02.003:182, BC-6.04.003:94 vs ARCH-07:96 | The corpus root is `internal/parity/testdata/cases/` in the BCs and `internal/statusline/testdata/parity/cases/` in ARCH-07. Two related splits: BC-6.03.001:139 has `-update` in `./internal/statusline`, ARCH-07:88 in `./internal/parity`; ARCH-07:98 has `steps.jsonl`, BC-6.02.003:61 puts `steps` inside case.json. BC-6.03.004's "relative to the corpus root" therefore has no single meaning. | architect |
| ADV-P4-D11 | HIGH | P13 / harness translation | BC-6.02.003:89-97 (PC-2) | Settings are translated by name only, with no value mapping for Bool keys. Go accepts `false`/`no`/`0`; legacy treats anything except `"0"` as on (SL:76-77). A case `sparkline.enabled:"false"` gives legacy `DGX_SL_SPARK=false` (on) vs Go off: a spurious divergence, and no rule says otherwise. | architect |
| ADV-P4-D12 | MEDIUM | harness gap (OD-107) | BC-6.03.004 PC-1 (:100-101), BC-6.02.001 PC-1/3 | Replays from `captures/` have no exclusion path. `exclusions.json` is committed, and validation fails the whole run when a `case` dir is missing, which captures always are in CI. Naming captures in a public file also risks hygiene. Real sessions will hit D4-EX-2, OD-76 or OD-159, which makes "0 unexplained diffs on real inputs" unreachable. | architect |
| ADV-P4-D13 | MEDIUM | undefined comparison | BC-6.03.004:112-126 (PC-3) | The D4-EX-3 asymmetric check compares the oracle's caches with "the oracle's own previous refresh". That is undefined for single-step cases, and for number-class cases where legacy crashes at import (CP-X01/X02: exit 1, no caches). PC-3 names only the Boolean, Enum and URL classes. | architect |
| ADV-P4-D14 | HIGH | Python parity (Unicode DB) | BC-5.01.002 PC-2 (:51), BC-5.02.005 PC-4 (:60-63), BC-2.02.003 PC-2 (:57-58) | CPython 3.11 uses Unicode 14.0; Go 1.26's `unicode` tables are newer. No spec pins the version (grep found none). Code points assigned after 14.0 differ in Nd and `isprintable`; e.g. Kawi digits U+11F50-59: Python `int()` rejects them, Go `unicode.IsDigit` accepts. The VP-023/VP-024 oracle fuzz targets will diverge. Confidence MEDIUM on Go's exact Unicode version. | architect |
| ADV-P4-D15 | HIGH | Python parity | BC-5.01.007:48-50 (Pre 2), :72-74 (PC-2) | Mixed and float division is specified as "IEEE-754 division", and only int/int forbids a zero divisor. CPython raises `ZeroDivisionError` for `1.0/0.0` and `1/0.0`; IEEE gives `inf`. A site would render `inf` where legacy degrades. | product-owner |
| ADV-P4-D16 | MEDIUM | untestable | BC-5.01.007:75-83 (PC-3/4), :94-95 (Inv 3), :111 | `NumCmp → (int, error)` has no defined result for NaN (unordered). Max/Min "decide via NumCmp", so BC-5.01.003 PC-5's NaN order cannot be derived from it. Inv 3 ("…cross-multiplied when b is an exact reciprocal") does not parse. EC-011 names `NumToInt64Aware`, which exists nowhere. | product-owner |
| ADV-P4-D17 | MEDIUM | missing boundary | BC-5.02.006 (whole), BC-5.02.001:86-87 | Legacy `save_cache` uses `json.dump`, which encodes through Python generator frames. A deeply nested stdin `rate_limits` (accepted up to depth 993) is stored at SL:307; a RecursionError there is swallowed, so nothing is written. No Dumps depth boundary is pinned. BC-5.02.001 Inv 4's "encoder budget = decoder's" is unmeasured, and the frame cost differs from the C encoder used by `json.dumps`. | architect |
| ADV-P4-D18 | MEDIUM | anchoring / scope / P18 | BC-5.03.004:62-63 (Inv 3), :34-36 vs ARCH-06:34, :127 | The BC lists `abspath`/`join`/`dirname` (SL:373-390) as served by pyfmt; ARCH-06 says they are NOT pyfmt. No BC pins posix/nt `join`, `dirname` or `abspath` (Windows uses GetFullPathNameW). The Description says the caller picks the flavor; ARCH-06 says `Basename` uses `runtime.GOOS`. | architect |
| ADV-P4-D19 | MEDIUM | P20 / untestable grammar | interface-definitions.md:140, :154, :156, :179-180, :185, :206 vs BC-2.01.004:58, BC-2.01.005 | Registry types `Float pair`, `Int map`, `Float (triple)`, `RGB triples + Float` and default-only `Text` are not in BC-2.01.004's Type enum and have no env grammar (BC-2.01.005 covers Bool/List/Path only). The vocabulary has no reason for empty or out-of-range Text. A failing test for `HYLO_STATUSLINE_COST_PERCENTILES` cannot be written. | product-owner |
| ADV-P4-D20 | MEDIUM | contradiction | BC-2.03.002:76-79 vs BC-2.01.005:67, :70-72 and BC-2.01.001 PC-2 | `config path` treats `HYLO_PATHS_CACHE_DIR=` (empty) as unset and prints the platform default. The grammar carves out only `HYLO_CONFIG`, so the status line raises `empty path` and uses no cache dir. That contradicts OD-165 "same directory the status line uses". | product-owner |
| ADV-P4-D21 | MEDIUM | P18 / Windows TZ | BC-5.04.001:45, BC-6.01.002 PC-2, BC-6.02.003 PC-8 | The "harness `HYLO_TEST_*`-controlled zone" names no variable, and none is reserved. The Go child gets only `TZ`, which Go's `time.Local` ignores on Windows. The UTC naive-timestamp cases on windows-2025 pass only because the runners are UTC; a non-UTC Windows host diverges from CPython, whose MSVC runtime honors `TZ=UTC`. How `Env.Loc` is derived is not routed through `internal/platform`. | architect |
| ADV-P4-D22 | MEDIUM | anchor drift | BC-2.02.001:184, BC-6.03.004:83, ARCH-07:104, BC-2.02.003:121 | The D4-EX-3 table-test names are inconsistent across three documents: 4 names (BC-2.02.001), 5 (+Theme, BC-6.03.004), 6 (+NumberGrammar, ARCH-07). BC-2.02.003 maps the grammar class to `_Number`. A Theme D4-EX-3 case cannot exist in the corpus, because BC-6.02.003 PC-3/EC-007 rejects theme settings. | architect |
| ADV-P4-D23 | MEDIUM | contradiction | BC-6.04.002 PC-1/2 vs :124 (VP), :110 (EC-005), :116-118 (CTVs) | The text says p95 is computed per case and never pooled. VP-036 says "pooled samples", the vectors show one p95 per OS, and EC-005 ("fewer than 20 total samples") cannot occur with a fixed 20 runs per case. The PC-3 gate does not say which p95 it applies to. | architect |
| ADV-P4-D24 | MEDIUM | contradiction | BC-6.01.003:60-63 vs BC-5.04.003:53-60, :73-76 | Go parses `HYLO_TEST_NOW` with `strconv.ParseFloat`, which accepts `inf`, `NaN` and `0x1p3`. BC-5.04.003 declares nan/inf, whitespace and `_` malformed, while the shim's Python `float()` accepts whitespace, `_` and nan. Finite values beyond the `time.Time` range (e.g. `1e300`) are unspecified. | architect |
| ADV-P4-D25 | MEDIUM | infeasible spec | BC-6.02.002:54, :67-74 | `stdin` is a JSON object inside session.json, yet it must be a byte-level splice that is never parsed, with NaN/Infinity tokens preserved. Extracting the raw member requires parsing session.json, and Go's `encoding/json` rejects NaN tokens. Non-object or invalid captured stdin cannot be represented, and there is no marker for subagent-mode captures. | architect |
| ADV-P4-D26 | MEDIUM | P5/P12 anchor | BC-2.01.005:56, BC-2.02.006:51-52 | Both cite "P1 per the 2026-11-18 owner ruling" for `statusline.queue.yellow`. The decision log (:151-155) has no such entry; the pass-3 rulings are OD-166..168 only. [owner-question] | product-owner |
| ADV-P4-D27 | LOW | anchor completeness | BC-2.01.001:65-67, BC-2.01.002:133, :140-146 | Only SL:444 is cited for `LOCAL_MODEL_PREFIXES`. Legacy also reads it at SL:902-903 (subagent lane tag, in P1 since OD-155), and no BC-1.07.x consumer is listed. | product-owner |
| ADV-P4-D28 | LOW | partial-fix | BC-6.01.003:46, :147 vs :79-80 | The Description says "nine" `time.time()` reads and the Traceability lists eight sites; PC-2 lists ten (adds SL:889), which matches legacy's grep. | product-owner |
| ADV-P4-D29 | COSMETIC | test-data accuracy | BC-3.02.002:68, :102-106; BC-3.02.001:124 | 2026-11-13 and 2026-11-06 are labelled `Thu`; both are Fridays. Harmless to legacy (`%a` is not validated) but unrealistic `ps` output. | product-owner |
| ADV-P4-D30 | COSMETIC | purity | BC-3.01.001:139-143 | The Purity table says "Deterministic: no (live OS state)" and lists syscalls, contradicting Inv 3 (pure over an injected env lookup) and PC-5. | product-owner |
| ADV-P4-D31 | LOW | ambiguous vector | BC-5.01.002:79, :87 | `"\x855"`: in Go notation `\x85` is a raw invalid byte, not U+0085, and the escape note covers only `\uXXXX`. | product-owner |
| ADV-P4-D32 | LOW | unspecified | BC-3.02.001:84-85 | The outcome when the Windows PID-reuse guard rejects a parent is not stated (None, or continue the walk). | architect |
| ADV-P4-D33 | LOW | nondeterminism | BC-2.03.001:52 | "Encounter order" of unknown-setting warnings follows `os.Environ`, whose order depends on the OS. Pin an order. | product-owner |
| ADV-P4-D34 | LOW | P4 mis-home | BC-5.04.003:53-60, :73-76 | `HYLO_TEST_NOW` parsing and warning (an effectful cmd-layer duty) sit inside a pure pyfmt helper contract, and the text is duplicated. | product-owner |

### 2. Policy compliance

- P1: PASS
- P2: PASS (sampled DI-008/010/012 citations)
- P4: FINDING D18, D22, D27, D34
- P5: FINDING D26
- P6: PASS (subsystem IDs checked; registry names not re-read)
- P7: PASS (sampled 9 H1 / BC-INDEX / PRD rows)
- P12: PASS (D26 tagged owner-question)
- P13: FINDING D01, D11, D14, D15
- P14: PASS
- P16: PASS (minor: BC-5.01.004:48 calls the 0..67 width bound "derived", but it reads as a judgment call)
- P18: FINDING D06, D18, D21
- P19: PASS
- P20: FINDING D19
- P21: PASS
- P3, P8–P11, P15, P17: N.A.

### 3. Not fully read, and Python claims not verified

- **Perimeter coverage:** all 53 BCs were read from just after the frontmatter (about line 28-34) to the end.
- **Cross-checks only partly done:**
  - Read only partly: interface-definitions.md (lines 120-239), error-taxonomy.md (lines 40-110), ARCH-06, ARCH-07, ARCH-08 (lines 36-60).
  - Grep only: ARCH-05, VP-INDEX, prd.md.
  - Not read: ARCH-01..04, individual VP files, capabilities.md, invariants.md, BC-ALLOCATION.md.
- **Python claims not verified:**
  - 4,300-digit counting (leading zeros included).
  - The 3.11 `fromisoformat` details: any-character separator, `+HH` offset, hour 24 rejected.
  - The git key `29de25ac9bde9ad0`.
  - Golden byte totals and heat RGB values. Composition, token, limit and window-age figures were hand-checked and agree.
  - Go 1.26's exact Unicode version.
  - `go run` → `(devel)`.
  - The json.dump encoder depth boundary (D17).

### 4. Novelty

Novelty: MEDIUM. Most findings are new contradictions between documents: harness argv and corpus layout, CI step order, the ARCH-06 signatures, default values, and the Unicode database version. D05, D08 and D28 are fixes from pass 3 that reached one document but not its siblings. **NOT_CONVERGED**

