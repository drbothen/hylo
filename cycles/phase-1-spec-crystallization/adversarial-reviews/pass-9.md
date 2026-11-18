---
document_type: adversarial-review
phase: 1d
pass: 9
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 85
---

# Adversarial Spec Review — Phase 1d, Pass 9

Pass 9 ran as six fresh-context perimeters, the same split as passes 1-8. Each section is the verbatim final report of one perimeter, unedited except for this framing. NOT_CONVERGED (85 findings: HIGH 15 / MEDIUM 38 / LOW 28 / COSMETIC 4; pass 8 had 88 with 12 HIGH). The orchestrator spot-verified A02 (and measured legacy: a 993-deep mix cache fails reload at 991 and the transcript is re-read and the cache rewritten every refresh), A2-01, A2-04, B03 (int-sum overflow at SL:633 reproduced), C02 (11 spec files with unparsable YAML frontmatter, all introduced in pass 8), C2-01 and C2-02 (CPython 3.11.7 source and urlsplit) on disk; all held.

## Perimeter A (PRD, supplements, architecture, CI)

Findings: 17 (high 3, medium 9, low 4, cosmetic 1).

## 1. Findings

| ID | Sev | Category | File:line | Defect (evidence) | Owner |
|---|---|---|---|---|---|
| ADV-P9-A01 | HIGH | contradiction / missing interface | prd-supplements/interface-definitions.md:392; :89; :60-85 | The supplement says "P1 emits no JSON on stdout", and its Output Byte Contract lists only the 1-2 line, degraded, config-error and unknown-flag outcomes. But `--subagent` mode emits NDJSON rows (BC-1.07.004), and the same file's Flag Interactions row at :419 says so. Neither the subagent stdout schema (rows, zero-byte cases) nor the subagent stdin payload (`tasks`, `status`, `model`, `tokenCount`, `startTime`) appears in the stdin or output contracts. Phase 2 S1.07 story writers have no interface source. | product-owner |
| ADV-P9-A02 | HIGH | contradiction / partial-fix regression | architecture/ARCH-06-pyfmt.md:70 vs :52, :79-83; ARCH-03-statusline.md:168 vs :174-178 | The pass-8 re-measurement set the mix-cache Save budget to 994 at s=4. The "one law" (995 − s = 991 at s=4) and the reconciliation sentences were not updated: both files still say "every cache's Save budget EQUALS its Load budget (session/mix 991/991)" and "Decode(Save(x)) never rejects what Save produced". Mix Load is 991 and Save is 994, so a saved mix cache nested 992-994 deep is rejected on reload. ARCH-03:168 itself says mix nesting is reachable from input. A builder could take either constant, and a swap or round-trip test would assert a false property. Two files affected. | architect |
| ADV-P9-A03 | HIGH | P18 / interface mismatch | ARCH-03-statusline.md:151; ARCH-05-platform.md:23-37; behavioral-contracts/ss-01/BC-1.02.004.md:55 | ARCH-03 puts the Win32 `GetFullPathNameW` resolution in `internal/statusline`, with signature `Env.Abs func(p string)`. BC-1.02.004 calls `platform.Abs(env.Cwd(), directory)`, which has two arguments and lives in platform. ARCH-05's Files table has no `Abs` row at all. This breaks NFR-004 / CLAUDE.md ("OS-specific code lives in internal/platform"), and the BC and ARCH signatures cannot both be implemented. | architect |
| ADV-P9-A04 | MEDIUM | P11: CI can pass while checking nothing | cicd-setup.md:58, :278 vs :61-66, :90-93; .github/workflows/ci.yml:203 | The `coverage` job is a placeholder gated on `internal/parity` existing, yet it is listed as the required check `coverage`. module-criticality.md:133-146 builds parity LAST, after pyfmt, cost and statusline. So for all of Phase 3, S1/S5 code merges while a required check is skipped, and GitHub counts a skip as success. The same file forbids exactly this (:61-66). The gate should key on the gated packages, not on parity. | architect / devops |
| ADV-P9-A05 | MEDIUM | P11: security-perimeter detector without a positive-coverage line | cicd-setup.md:78-88; ARCH-08:111-146; ci.yml:118-121 | The positive-coverage table covers only the pattern scan (`hygiene: K files, H hits`). gitleaks, the secret scan for the public repo, has no runtime-computed "N commits scanned across main + factory-artifacts" assertion. A shallow or narrowed `--log-opts` would scan nothing and still exit 0. | architect / devops |
| ADV-P9-A06 | MEDIUM | CI contradiction / missing sequencing | ARCH-08-build-ci-release.md:24-28, :191-195; go.mod:3 | go.mod is `go 1.26.0` with no toolchain line, so CI and release builds use 1.26.0. ARCH-08 also promotes govulncheck to a required PR check. govulncheck reports stdlib advisories against the Go version actually used (crypto/tls and net are reachable through the metrics client). The `toolchain` remedy is "spec-only" and is not ordered before the required check lands, so the required check will go permanently red, or shipped binaries will carry known stdlib vulnerabilities. | architect |
| ADV-P9-A07 | MEDIUM | contradiction (premise of OD-193 rationale) | ARCH-07-parity-harness.md:32 vs ARCH-08:87-88; cicd-setup.md:58 | ARCH-07 says Tier A runs "Go in-process and as the built binary for a subset". ARCH-08 and cicd-setup justify excluding Tier A from coverage because "Tier A drives the built binary as a subprocess". It is unclear which execution model the harness implements. | architect |
| ADV-P9-A08 | MEDIUM | partial-fix propagation | prd-supplements/risk-register.md:29 vs ARCH-08:166-174 | ARCH-08 corrected the R-004 P1 mitigation in pass-7 A09 to "census discipline + ≥95% line-coverage gate". The risk register still gives the pass-6 wording (Tier A swap, Tier C, fail-closed machinery) and mentions neither the census nor the coverage gate. | architect |
| ADV-P9-A09 | MEDIUM | semantic mis-anchor (P4) | prd-supplements/risk-register.md:26 | The R-001 mitigation reads "failed-replace semantics pinned by the AD-03 overlay decision". AD-03 rejected the overlay; ARCH-03:28-33 calls it option 1, "wrong persistence semantics". The anchor is right but its description says the opposite. | architect |
| ADV-P9-A10 | MEDIUM | partial-fix propagation / incomplete enumeration | prd-supplements/interface-definitions.md:66-78; prd.md:613-614 | ARCH-06:31 has the measured metrics-reply decode site `depthMetricsReply = 992`, added pass-6 A07. The supplement's "Measured:" site list omits it. PRD §8 still says "both current sites (stdin, transcript) measure 993/994", ignoring the cache loaders (991/990) and the metrics reply. | product-owner |
| ADV-P9-A11 | MEDIUM | config key without a range / missing edge case (P20, OD-162) | prd-supplements/interface-definitions.md:176; ss-02/BC-2.01.005.md:81 | The `paths.cache_dir` Range cell is "not the legacy literal (exception)", which is not a domain. BC-2.01.005 uses any non-empty value "as given", so a relative `HYLO_PATHS_CACHE_DIR` resolves against Claude Code's per-project cwd and splits caches and cost history. Relative `XDG_*` values are rejected for exactly that reason (OD-144). No reason string or ruling covers it. | product-owner |
| ADV-P9-A12 | MEDIUM | interface ambiguity (single-home rule) | ARCH-01-binary-cli.md:38-41; ARCH-03-statusline.md:154-157; ss-02/BC-2.01.001.md:109 | `EnvVars` is declared as an interface in cmd/hylo (ARCH-01) and again in package statusline (ARCH-03). BC-2.01.001 names the seam `platform.EnvVars`, and ARCH-05 platform resolvers take `env EnvVars`. This violates ARCH-00:94-95 ("every component appears in exactly one ARCH section"), and story writers will mint duplicate types. | architect |
| ADV-P9-A13 | LOW | overstated enforcement claim | ARCH-09-reserved-boundaries.md:38-39; ARCH-03:149, :259-263 | The claim "DI-007 enforced architecturally ... Env has no ledger seam" does not hold: `FileSystem.ReadFile(name string)` reads any path, so ledger reads are prevented only by VP-022's static analysis. | architect |
| ADV-P9-A14 | LOW | ambiguity | prd.md:509; error-taxonomy.md:54 | The E-NET-001 dead rung is written with literal `\e[31m` and `◌`, but red (`statusline.theme.red`) and the glyph (`statusline.glyphs.degraded`) are config keys. It does not say whether the rung follows them. | product-owner |
| ADV-P9-A15 | LOW | CI timeout budget | cicd-setup.md:58 vs :52 | The coverage job runs the same selection as the test job (Tier A excluded) plus `-coverpkg` instrumentation, with a 10-minute cap against the test job's 30. The rubric names this a false-fail risk that can kill the assertion phase before it runs. | devops |
| ADV-P9-A16 | LOW | diagram contradicts text | ARCH-08-build-ci-release.md:41-43 vs :60-63 | The mermaid diagram routes every matrix leg through setup-python. The text says only the ubuntu leg (and the Tier A and nightly jobs) install an interpreter. | architect |
| ADV-P9-A17 | COSMETIC | stale line pointer | ARCH-00-overview.md:21 | `prd.md:68` points at the AD-10 seam mention, which is at prd.md:70. | architect |

## 2. Policy compliance
- P1 append_only_numbering: PASS. CP-T08 is kept as a retired id; CP-C06/C07 are reserved.
- P2 lift_invariants_to_bcs: N.A. within this perimeter (DI citations present).
- P4 semantic_anchoring_integrity: FINDING A09, A03.
- P5 creators_justify_anchors: PASS.
- P6 subsystem names: PASS. PRD §1.6, ARCH-INDEX and module-criticality agree.
- P7 BC H1 = PRD rows: PASS (all S1.01, S1.05-S1.07 and S2-S6 H1s sampled; they match).
- P9 VP-INDEX arithmetic and arch agreement: PASS (41 = 33+7+1 = 20+13+3+2+1+1+1; ARCH-INDEX primary-home split 41; module counts consistent).
- P11 ci_positive_coverage_assertion: FINDING A04, A05 (also A15).
- P12 settled decisions: PASS.
- P13 parity before behavior change: PASS (deviations ride the twelve-id set; OD-186 widening is ruled).
- P14 public repo hygiene: PASS.
- P16 thresholds explained: PASS.
- P17 ledger frozen: PASS.
- P18 cross-platform: FINDING A03.
- P19 go hardening toolchain: FINDING A06.
- P20 config over code: FINDING A11.
- P21 public artifact hygiene: PASS (nothing flagged is quoted).

## 3. Files not fully read
None in the perimeter. prd.md was read in two pages. BC files were opened only to check specific cross-references: BC-2.01.001, BC-2.01.004 (partial), BC-2.01.005 (partial), BC-4.01.002 (grep), BC-6.04.002 (grep), BC-1.02.004 (grep), and the H1 sweeps.

## 4. Novelty
HIGH. A01-A03 are new contradictions; A02 is a residue of the pass-8 re-measurement.

NOT_CONVERGED

## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 20 (high 4, medium 8, low 7, cosmetic 1).

## Adversarial Review: Phase 1d, Pass 9, Perimeter A2

### 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P9-A2-01 | HIGH | VP property false over its own generator | VP-040:54-56, :87, :120-129 | P7 says "for all `statusline.rows` settings and cols < 0", row 2 is omitted only when rows == 2 and cols < narrow_cols. The generator includes rows {-1, 0, 1}. Legacy only renders row 2 when rows_env >= 2 (SL:1217), so row 2 is never present for rows <= 1, but P7 requires it there. BC-1.01.007 PC2/PC3 (:57-59) only covers rows == 2 and rows >= 3. A correct port fails 3 of the 8 settings. The sketch adds a second wrong rule ("present IFF rows > 2"). | architect |
| ADV-P9-A2-02 | HIGH | VP contradicts its own statement and the BC | VP-013:49-51, :107-115; VP-029:50-53 | The testing/quick leg says that for every generated W-line, "per CP", parser state after equals state before, bit-identical. But the CP-O06..O08 W-lines drop `cur` to null (OD-167). Both VPs say so in the same paragraph, and BC-1.03.018 PC2 (:83-87) agrees. PC2 also says "the offset still advances". A correct port fails every overflow W-line drawn by the generator. Affects 2 files. | architect |
| ADV-P9-A2-03 | HIGH | Wrong oracle | VP-013:52-55; VP-029:53-58 | The delete-the-line equivalence leg is adjusted only for PC4(b). BC-1.03.018 PC4(a) (:104-107) says hylo's `size` equals legacy's plus each deleted line's bytes and terminator. Without that adjustment the cache/state comparison false-fails on every input that contains a W-line. Affects 2 files. | architect |
| ADV-P9-A2-04 | HIGH | VP property false on a legal path | VP-030:55-57; VP-031:56-59 | The for-all says every saved history point satisfies `now - t < 90`. On fetch failure, legacy saves the stored `hist` unpruned (`entry = dict(c)`, SL:327, SL:353-355). BC-1.04.003 Inv 2 (:90-91) says the failure path keeps points verbatim. So a point saved at t=0 is re-saved at t=200 after a failed fetch, which is a legitimate state that violates the property. Separately, "<= 32" and "90" are hard-coded although both caps are config keys (`history_cap`, `max_age_s`; P20). | architect |
| ADV-P9-A2-05 | MEDIUM | Semantic anchoring (P4) | VP-031:56-59, :72-73; VP-030:56 | VP-031 v1.4 says BC-1.04.003's quick row "routes here jointly with VP-030", and VP-030 cites "VP-031's quick leg". BC-1.04.003:120 says "VP-031 de-cited from this row". BC-1.04.003:121 also routes a 16-subset key-order table to VP-031, and VP-031 delivers no such table. | architect |
| ADV-P9-A2-06 | MEDIUM | Weak oracle | VP-001:53-55, :155-159; VP-005:41-43, :99-103 | The subagent parse-path oracle accepts "rows or zero bytes". Legacy `main_subagent` maps any undecodable or non-object stdin to `{}`, which gives zero rows (SL:928-936). DI-008 (invariants.md:31) and BC-1.07.003 also say zero bytes. A port that renders rows from non-object stdin passes both VPs. | architect |
| ADV-P9-A2-07 | MEDIUM | Ambiguity / contradiction | VP-016:37-39 vs :53-58 | The statement says every invalid value falls into "exactly one of the seven" classes. Then it says the path-grammar and backends-cardinality reasons "ride the class register". BC-2.02.006:47-49 says those reasons "are not additional classes". So an invalid path value belongs to none of the seven, and the stated property cannot be evaluated. | architect |
| ADV-P9-A2-08 | MEDIUM | Internal contradiction (partial fix) | VP-013:37-40 vs :61-64 | The pass-8 statement says the 21 canonical rows "contain no CP-O rows". The Partial-coverage bullet still says the CP-O06..O08 rows are "of the canonical table ... delivered by this VP's 21-row table". | architect |
| ADV-P9-A2-09 | MEDIUM | Sibling propagation gap | VP-027:38-41 | The VP still says negative COLUMNS hides row 2 unconditionally ("overflowing negative stays negative — row 2 hidden"). BC-1.01.007 v1.3.4/1.3.5 qualified this to rows == 2 and cols < narrow_cols. VP-027 (v1.1, 2026-11-18) was never updated. | architect |
| ADV-P9-A2-10 | MEDIUM | Detection claimed without an oracle (P11) | VP-006:94-97, :133, :52-56 | The Method says a wrong budget at a production call site "is a detected defect", but no oracle compares production constants with the table, and no end-to-end leg exists for the five derived sites. The sketch's pin check compares two literals from the same row, so it can never fail. | architect |
| ADV-P9-A2-11 | MEDIUM | Positive-coverage gap (P11) | VP-035:68, :89-97 | The scan self-test plants one token-shaped canary. The category scan covers several independent categories (IPs, usernames, home paths, hostnames, emails), and any of those patterns could be inert without the test noticing. VP-022:97 sets the standard at one planted violation per rule. | architect |
| ADV-P9-A2-12 | MEDIUM | Sketch contradicts property (OD-182 cap) | VP-004:102-107 vs :50-53 | The MAIN-mode fuzz leg passes arbitrary `args`, which can include `--subagent`. That routes to the subagent renderer, whose zero-byte output is legal, and the sketch's "MAIN: stdout empty" check then fails a correct port. | architect |
| ADV-P9-A2-13 | LOW | Ambiguity | VP-041:45-46 | P-b leaves out the precondition that the API suffix exists only inside the timer segment (dur > 60000, SL:540, :551-553). A generator that varies `dur` false-fails. | architect |
| ADV-P9-A2-14 | LOW | Method incomplete | VP-041:110-118 | The Method bullet never names P-i (the dense-grid heat triple). It appears only in the Proof Method table (:153). | architect |
| ADV-P9-A2-15 | LOW | L2 drift | domain-spec/capabilities.md:31 | The CAP-009 carve-out omits the unmapped-panic backstop. DI-008 (invariants.md:31) and SM-04 (state-machines.md:76) both list it as a source of the degraded line. | business-analyst |
| ADV-P9-A2-16 | LOW | Scope narrowing | VP-007:57-58 | The DI-007 corollary lists only stdin, transcript, metrics and caches. It drops the environment seams (git, process table, clock, env) that DI-007 includes (invariants.md:30). | architect |
| ADV-P9-A2-17 | LOW | Stale assessment claim | dtu-assessment.md:54 | "Decode edges carry 101 S1 BCs": 101 is all of S1, including the transcript (#6) and subagent (#5) contracts that have their own inventory rows. | architect |
| ADV-P9-A2-18 | LOW | Count ambiguity | gene-transfusion-assessment.md:52 vs VP-026:39-40 | The assessment says "10,893 naive-time goldens"; VP-026 says 10,893 rows per grid across four grids. | architect |
| ADV-P9-A2-19 | LOW (pending intent verification) | Sibling wording | domain-spec/owner-validation-list.md:242 | VALID-08 is restated as "permanent domain law". Pass 8 corrected the same wording in VP-022 to OD-125's "adopted for now with a revisit flag". The line here is labelled as a verbatim proposal, so it may be intentional. | business-analyst |
| ADV-P9-A2-20 | COSMETIC | Sketch / typo | VP-037:40; VP-017:82-85; VP-004:102; VP-016:168 | Missing space in "report.The". VP-017 uses a two-value `Load`, while ARCH-02 per VP-015 returns three values. VP-004 and VP-016 fuzz over `[]string`/`map` parameters, which Go fuzzing does not support. | architect |

### 2. Policy compliance
- P1 append_only_numbering: PASS (CP-T08 retired, CP-T09 minted).
- P2 lift_invariants_to_bcs: PASS (the P1 DIs have BCs; the rest are explicitly deferred under OD-115).
- P4 semantic_anchoring_integrity: FINDING ADV-P9-A2-05, -08.
- P5 creators_justify_anchors: PASS.
- P6 subsystem names: PASS (they match the ARCH-INDEX SS-01..06 registry).
- P9 vp_index_is_vp_catalog_source_of_truth: PASS (41 VPs; class totals 33+7+1 and method totals 20+13+3+2+1+1+1 both reconcile; the coverage map matches the `bcs:` fields I sampled; the 73-BC byte-exact census re-grepped correct).
- P11 ci_positive_coverage_assertion: FINDING ADV-P9-A2-10, -11.
- P12 settled_decisions_are_constraints: PASS.
- P13 parity_before_behavior_change: FINDING ADV-P9-A2-01, -02, -03, -04 (these VPs would fail a legacy-faithful port).
- P14 public_repo_hygiene: PASS.
- P16 thresholds_are_explained: PASS.
- P17 ledger_format_frozen: PASS.
- P18 cross_platform_from_day_one: PASS.
- P19 go_hardening_toolchain: PASS.
- P20 config_over_code: FINDING ADV-P9-A2-04 (hard-coded 32/90 in the for-all).
- P21 public_artifact_hygiene: PASS.

### 3. Files not fully read
None in the perimeter. I opened BC-1.03.018, BC-1.04.003, BC-1.01.007, BC-2.02.006 and ARCH-INDEX only to check specific claims.

### 4. Novelty
HIGH. Four HIGH findings are new property-falsity defects, each checked against legacy line numbers and the BCs. NOT_CONVERGED.

## Perimeter B (BC-1.01, BC-1.02)

Findings: 7 (high 1, medium 4, low 2, cosmetic 0).

## Adversarial Review, Phase 1d, Pass 9, Perimeter B (BC-1.01.*, BC-1.02.*)

I read all 40 BCs and checked every vector against the legacy lines they cite, deriving the Python results by hand. That covers the floating-point products, the floor-division rows, the HSV channels, the staircase sums and the countdowns. All of them reproduce. The findings below are spec gaps and one regression from a pass-8 fix, not wrong vectors.

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P9-B01 | HIGH | VP statement wrong (regression from the pass-8 B02 fix) | VP-040 lines 54-56, generator line 87; legacy SL:1217, 1224 | P7 says "row 2 omitted iff rows == 2 and cols < narrow_cols". That is false for rows ≤ 1. Legacy only enters the row-2 block when `rows_env >= 2` (SL:1217), so rows=1 with cols=-5 omits row 2 while the right-hand side is false. P7's own generator includes rows {-1, 0, 1}, so correct code fails P7 as written. It should read: omitted iff rows ≤ 1, or (rows == 2 and cols < narrow_cols). | architect |
| ADV-P9-B02 | MEDIUM | BC/VP mismatch, same pass-8 sweep | BC-1.01.007:100 (VP row), :130-131 (VP Anchors), :65-67 (Inv 1); SL:1217 | The P7 row says "row 2 present iff (rows > 2 or cols >= narrow_cols)" and drops the `rows >= 2` term. Counterexample: rows=1, narrow_cols=-10, COLUMNS=-5. The predicate holds (-5 ≥ -10), but legacy prints no row 2. This contradicts the BC's own PC4 ("rows = 1 → row 1 only") and BC-1.01.003 PC1. | product-owner |
| ADV-P9-B03 | MEDIUM | Overflow site missing from the crash register (OD-156) | BC-1.02.029:57 (PC1 "in float64"), :59; legacy SL:626, 633; error-taxonomy:166-172 (CP-O rows); ARCH-03:74 (step 7d) | `tot = (tin or 0) + (tout or 0)` is an exact int sum. When tin and tout are each below OV (each passes `_fmt_tok_c` at SL:587/597) but their sum is ≥ OV, `tot * dgx_mtok` at SL:633 raises OverflowError, so legacy prints the degraded line. A float64 port gets inf and prints ` ⛏inf`, which is a parity diff. It needs the local lane and a valid basis. The bearer is the same integer-only transcript accumulation as CP-O04 (BC-1.02.025 EC-010). The CP-O list and BC-1.02.029 / BC-1.05.003 do not record this site. | architect (taxonomy), product-owner (BC) |
| ADV-P9-B04 | MEDIUM | Decode scope not pinned | BC-1.02.004:87-90 (PC2.3), :96-97 (PC3); legacy SL:380-381 | `open(dotgit).readline()` decodes a whole buffered chunk (up to 8192 bytes), not just the first line. Example pointer file: `gitdir: ../wt` LF followed by a raw 0xFF byte. Legacy raises UnicodeDecodeError and returns "" (the walk stops). A Go port that reads and validates only the first line finds the gitdir and returns the branch. PC2.3 ("read its first line") points the implementer at that wrong reading. | product-owner |
| ADV-P9-B05 | MEDIUM | Spec drift: which errors stop the walk | BC-1.02.004:96-97 (PC3 "permission error → return \"\" immediately"); legacy SL:377, 379, 384 | `os.path.isdir`/`isfile` (CPython `genericpath`) catch OSError and ValueError and return False. So stat-level errors never raise and the walk continues upward: EACCES on a parent component, ENAMETOOLONG, ENOTDIR, an embedded NUL from JSON `\u0000`. Only `open`/read failures reach the outer try at SL:394. Read literally, PC3 makes a stat EACCES return "", but legacy returns the nearest ancestor repo's branch. The PC2 pin generalizes the "level counts as not-a-directory" rule only for lone surrogates. | product-owner |
| ADV-P9-B06 | LOW | Property row has no degrade carve-out | BC-1.02.015:111; VP-041:77-78 (P-t); SL:540, 546, 559 | "Segment present iff number and > 60000 — for all renders" is false for dur=+Infinity (CP-S12, BC-1.02.027), for api=+Infinity (CP-S13), and for dur ≥ OV with a numeric win_start (CP-O05). In each case the predicate holds but the render degrades, so there is no segment. It should be restricted to finite dur in non-degrading renders, as P-b already does. | product-owner, architect |
| ADV-P9-B07 | LOW | Effect table incomplete | BC-1.01.009:66 (step 4 Write cell); SL:324-325 | Step 4 shows a write of "fetch result or `up: false`", but a fresh cached verdict (`fetch_ts > now - TTL`) returns at SL:325 and writes nothing. VP-008's expected write set, modelled from this table, would over-predict the writes. | product-owner |

### 2. Policy compliance
- P1 append_only_numbering: PASS (001-010 and 001-030 are contiguous, no reuse).
- P2 lift_invariants_to_bcs: PASS (DI-007, DI-008 and DI-012 are cited wherever an exclusion is carried).
- P4 semantic_anchoring_integrity: FINDING ADV-P9-B01, B02 (the P7 legs of VP-040 misstate the BC).
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS (all 40 use "SS-01", matching the ARCH-INDEX registry).
- P7 H1 = BC-INDEX = PRD: PASS (all 40 titles identical in all three places).
- P12 settled_decisions_are_constraints: PASS (no settled decision is challenged).
- P13 parity_before_behavior_change: FINDING ADV-P9-B03, B04, B05 (paths where a port can diverge without a named exclusion).
- P14 public_repo_hygiene: PASS (I scanned for the local hygiene terms, private IP ranges and home paths: no hits).
- P16 thresholds_are_explained: PASS.
- P17 ledger_format_frozen: N.A.
- P18 cross_platform_from_day_one: PASS.
- P19 go_hardening_toolchain: PASS (the no-FMA sites are pinned).
- P20 config_over_code: PASS (all keys are registered in interface-definitions with matching ranges; no DGX_* aliases).
- P21 public_artifact_hygiene: PASS.

### 3. Not fully read, and Python claims I could not verify
- **Not fully read:**
  - `specs/prd-supplements/test-vectors.md` (not opened)
  - `specs/prd-supplements/error-taxonomy.md` (CP-O, CP-A and CP-C rows only)
  - `specs/prd-supplements/interface-definitions.md` (lines 160-280)
  - `specs/architecture/ARCH-03-statusline.md` (lines 46-110 and the anchor list)
  - VP-040, VP-041 and VP-022 (property statements and method sections only)
  - prd.md, capabilities.md and invariants.md (checked by grep only)
- **Not checked by running Python (I have no execution tool):**
  - B04's 8192-byte chunk behavior, which comes from my knowledge of CPython's io module.
  - The SHA-1 cache keys in BC-1.02.005.
  - The OV decimal digits.
  - The ntpath results.
  - The 993/994 depth limit.
  - The 5e23 and 1e24 `_hm` outputs.
  - The byte totals of the golden-A end-to-end runs. Only the visible widths were re-derived.

### 4. Novelty
MEDIUM. B01 and B02 are a partial-fix regression from pass 8. B03, B04 and B05 are new parity gaps.

**NOT_CONVERGED**

## Perimeter C (BC-1.03, BC-1.06, BC-1.07)

Findings: 11 (high 2, medium 4, low 4, cosmetic 1).

**Adversarial review: Pass 9, Perimeter C (BC-1.03.\*, BC-1.06.\*, BC-1.07.\*)**

I read all 31 BCs in full and checked them against `legacy/dgx_statusline.py` SL:78, 125-136, 190-206, 270-413, 568-600, 837-1245. I recomputed every byte size and cache golden in BC-1.03.002 through .021 from the legacy semantics, and all of them reproduce. That includes the 21 rows of BC-1.03.019, the 20 turn rows of BC-1.03.016, the CP-O06, O07 and O08 legs, and the 420-byte NaN-id row. The 11 findings are below.

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P9-C01 | HIGH | Wrong golden; partial-fix regression | BC-1.07.007:125; also :112-113, :117-124, :126 | The Infinity row says it is the "pure-ASCII wire" form, but its content holds raw U+2714 and U+00B7 characters. The correct wire form is `\u2714` and `\u00b7` (BC-1.07.004 PC3, SL:924 `json.dumps` with ensure_ascii). The changelog says ADV-P8-C01 fixed this; the fix decoded the escapes instead. The preamble at :112-113 also says the rows are wire forms, yet rows :117-124 and :126 use `\e` (a raw 0x1B byte), which the wire always writes as `\u001b`. Row :117 mixes `\e` and `\u00b7` in one string. A test written from these rows would push Go away from byte parity. [process-gap]: this is the third escape-decoding incident (ADV-P3-C01, ADV-P9-C06, this one), and no check confirms that wire goldens are ASCII-only. | product-owner |
| ADV-P9-C02 | HIGH | Broken frontmatter (5 files) | BC-1.07.002:22, BC-1.07.003:22, BC-1.07.006:22, BC-1.07.007:22, BC-1.07.008:22 | In each file the `modified:` list is broken: the second-to-last entry lost its closing quote. The quote that opens the final pass-8 "task 9" entry closes the earlier string instead, so the version text that follows sits outside the quotes and the YAML does not parse. BC-1.07.001, .004 and .005 use block lists and are fine. BC-1.03.013 had the same class fixed (SC-15). [process-gap]: the sweep edit dropped the quotes and no YAML-parse gate caught it. | product-owner |
| ADV-P9-C03 | MEDIUM | Contradiction between BCs | BC-1.03.018:127 (Inv 3); BC-1.03.006:53-54 (PC3), :69-76 (PC5) | Inv 3 says transcript content never degrades the status line on POSIX. That is false. An integer-only line such as `input_tokens: 10^309` is counted exactly (BC-1.03.006 PC3, so no CP-O06 skip) and saved. Row 1 then calls `_fmt_tok_c(tin)` (SL:586-587), and `float(n)` at SL:866 raises OverflowError, which is CP-O04 → guard line (BC-1.02.025 EC-010, error-taxonomy :169). The degrade is sticky because the cache keeps the total. The CP-O09 4,301-digit case degrades the same way. BC-1.03.006 has no cross-reference to this. An implementer honouring Inv 3 would add a skip that breaks parity. | product-owner |
| ADV-P9-C04 | MEDIUM | Invariant false under D4-EX-2; untestable VP row | BC-1.03.017:54 (Inv 1), :84 (VP-029 row) | Inv 1 says `seen_ids` membership never influences `cur`, `lr` or `lu`. Under D4-EX-2, CP-T04 skips the whole line, turn step included, only when `m.id ∉ seen_ids` (BC-1.03.018:95), and CP-T05 depends on `id ∈ seen_ids` (:96). Counter-example: transcript U0, then AA(2), then a timed user line with id `B` and usage `{"input_tokens":"5"}`. With seed ids `[]` the line is skipped: A stays open and `lu` stays 0. With seed ids `["B"]` the line closes A (`lr [150.0,false]`, `lu` 5). The "invariant under pre-seeding" property fails. It needs to be limited to transcripts with no W-lines. | product-owner |
| ADV-P9-C05 | MEDIUM | Anchoring contradiction; partial fix | BC-1.07.002:37, :99, :107 | Three places call `enabled=false` a "DI-012 named deviation". VP-005:44-46 says it is "not a DI-012 parity exclusion; no exclusion id covers this". DI-012 (invariants.md:35) lists a closed set of 12 ids that does not include it. ADV-P5-C16 corrected only `parity_class`; the Description, the VP row and the Traceability row were not updated. | product-owner |
| ADV-P9-C06 | MEDIUM | Vacuous vector | BC-1.07.004:76, :119 | The third ADV-P6-C04 example maps `"A"` to `"A"`: input token and output are identical, so it cannot catch an implementation that copies raw string tokens. This is almost certainly an escaped `\u0041` that got decoded during editing. String-token normalization therefore has no discriminating vector; only the numeric examples (`1.50`, `1E2`) discriminate. | product-owner |
| ADV-P9-C07 | LOW | Edge case contradicts PC2 | BC-1.07.005:95 (EC-005) | EC-005 says "failed row with all name fields" yet expects `?`. Under PC2 (:62) and SL:895, `?` only appears when every name field is missing. The text should say "with no name fields". | product-owner |
| ADV-P9-C08 | LOW | Missing precondition | BC-1.06.001:95-97 (PC4), :130 (vector) | The `777`, `true` and `1.5` session-cache names only happen when no regular transcript file exists. With a transcript, SL:1017 raises CP-S14 before SL:1215 runs (BC-1.03.013 EC-007/008): the line degrades and no session cache is written. | product-owner |
| ADV-P9-C09 | LOW | Edge case not exhaustive (OD-160) | BC-1.03.002:87 (EC-008) | A cached `size` of NaN, which `json.load` accepts (BC-1.06.001 EC-002), fails all of `<`, `==` and `>`. It never takes the reset path, reaches `fh.seek(nan)` at SL:1043 and raises TypeError whether the file grew or shrank. "hylo degrades only on the grow path" is therefore ambiguous for NaN. | product-owner |
| ADV-P9-C10 | LOW | Wrong VP reference | BC-1.03.020:105 | The VP row compares C2 with BC-1.03.019 row 13. Only C1 matches row 13. C2's native-hylo reference is row 15 + A9 + S11, which gives `lr [90.0,false]`. | product-owner |
| ADV-P9-C11 | COSMETIC | Mislabel and misquote | BC-1.03.010:110 (EC-007); BC-1.03.020:78 (EC-005) | EC-007 labels every non-numeric-`out` opener as CP-T05. When the usage is counted, the crash is CP-T04 at SL:1112 (BC-1.03.018:95-96); the outcome (skip) is the same. BC-1.03.020 EC-005 attributes the phrase "not int/float/bool" to OD-32's literal text. OD-32 (owner log :13) only says "cur.t0 is a number"; the `out` condition comes from CONV-ABS-15. | product-owner |

## 2. Policy compliance

- **P1** PASS. CP-T08 is retired and CP-T09 appended; EC and row numbering is monotone.
- **P2** PASS. Not citing DI-017 is deliberate (BC-1.02.001:81 disclaims it).
- **P4** FINDING: C05, C10.
- **P5** PASS.
- **P6** PASS. All 31 BCs use `SS-01`, matching ARCH-INDEX:55.
- **P7** PASS. All 31 H1 titles match BC-INDEX:117-197 and the PRD.
- **P12** PASS.
- **P13** FINDING: C01 and C03 would push the implementation away from byte parity.
- **P14** PASS. No personal data. The only machine detail is a generic interpreter path at BC-1.03.010:128, BC-1.07.004:78 and BC-1.07.007:132.
- **P16** PASS.
- **P17** PASS. The ledger is untouched (DI-007).
- **P18** PASS.
- **P19** PASS.
- **P20** PASS. All perimeter keys are registered at interface-definitions:206-237 with ranges that match the BCs.
- **P21** PASS.

## 3. Not fully read, and claims not verified

**Read only partly or by search:** VP-029, VP-013 and VP-012 (frontmatter `bcs:` only), ARCH-03 and ARCH-04 (searched), error-taxonomy (searched), BC-1.02.025 (searched), capabilities.md, and the BC-5.x helper contracts.

**Python claims I could not verify by reading the code** (they need the oracle):
- The 993/994 decode edges and the 994/995 mix-save encoder boundary.
- APFS errno 92 for raw-byte names.
- CP-O09's "19 bytes streamed".
- All Windows legs: MSVC localtime domain, `a/../b`, `../x`, and the invalid-character names.
- Python 3.11 accepting a bool as a file descriptor.
- BC-1.03.015 EC-002's mechanism for `-1`. By my reading it is a NULL-path stat, not an fd stat; the outcome is the same.

## 4. Novelty: MEDIUM

C03 and C04 are new semantic contradictions. C01, C02 and C06 are recurrences of known defect classes, flagged [process-gap].

**NOT_CONVERGED**

## Perimeter C2 (BC-1.04, BC-1.05)

Findings: 10 (high 1, medium 4, low 5, cosmetic 0).

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P9-C2-01 | HIGH | spec drift (HTTP client) | BC-1.04.001:98-101, EC-024 :308 | The BC says an interim **1xx** header block is skipped. In CPython 3.11.7, `HTTPResponse.begin` loops only while `status == CONTINUE` (100). Any 101/102/103 becomes the final response: http.client sets length 0 for 1xx, urllib's `HTTPErrorProcessor` raises `HTTPError` (not in 200-299), so legacy gets no sample. A Go client built to "skip any 1xx" gets a sample from `103 Early Hints` followed by 200. Fix: change "1xx" to "status 100 only" and add an EC for 103 → no sample. VP-030 Tier C varies status codes, so a test would hit this. | product-owner |
| ADV-P9-C2-02 | MEDIUM | spec drift (redirect normalization) | BC-1.04.001:151-153, 165-182, 199-203; same chain at ARCH-03:228-229 | The normalization chain (empty-path fix → urlunparse → quote → urljoin) leaves out what `urlparse`/`urlsplit` itself does to the target in 3.11.7: it strips all leading C0 controls and spaces, deletes every `\t`, `\r`, `\n`, and lowercases the scheme. All of this happens before the scheme guard and before quote. compat32 strips only leading space and tab, so a leading `\x0b` or an inner tab reaches urlsplit. Example: `Location: /a<TAB>b` gives the legacy key and target `/ab`, but the BC as written gives `/a%09b`. Also, "scheme of the raw (pre-normalization) target" would reject `HTTP://`, which urllib follows. | product-owner, architect |
| ADV-P9-C2-03 | MEDIUM | step ordering / unexcluded stdout divergence | BC-1.05.004:60-79 vs EC-005 :108; BC-1.05.009:135 | PC1 runs the OD-166 convertibility check inside the "no read, no write" guard, i.e. before the load. Legacy raises CP-S15 at SL:230 (`s.get(sid)`) after the load. Case: unhashable sid `["x"]` with `api_ms = -(2**1024)`. Legacy degrades (CP-S15). hylo returns at the guard, the $/h gate fails (no CP-O11), `cost_thresholds` never raises on `k == sid`, so it renders normally. That is a stdout difference. OD-166's scope is only the absent entry (BC-1.05.009:135). Fix: do the OD-166 skip at the write step (PC4), after load and lookup. [owner-question] if the intent is instead to widen OD-166. | product-owner |
| ADV-P9-C2-04 | MEDIUM | partial-fix sibling (VP-012 closure) | BC-1.05.009:25 (parity_class `OD-30, OD-166`), BC-INDEX:177; VP-012:13 bcs | BC-1.05.009 declares two closed-set ids but has no VP-012 closure row and is missing from VP-012's `bcs`. Every sibling that carries an id has one: BC-1.05.004 and BC-1.05.006 (same ids), and BC-1.04.001/.002/.003 (the ADV-P5-C2-17 and ADV-P7-C2-03 pattern). | product-owner, architect |
| ADV-P9-C2-05 | MEDIUM | P2 lift invariants (sibling) | BC-1.05.004:144 | The L2 row cites only DI-007 and DI-012. Yet EC-005 (:108) degrades via CP-S15, and the VP-001 row (:135) itself says "never-blank per DI-008". ADV-P6-C2-10 and ADV-P8-C2-05 added DI-008 to the siblings with degrade ECs (BC-1.05.002/.005/.007, BC-1.04.003); this file was missed. | product-owner |
| ADV-P9-C2-06 | LOW | mis-anchor (stale line labels) [process-gap] | BC-1.04.001:341 | Says "`MetricsClient` interface at line 187, `telemetry.go` … line 270, re-verified ADV-P8-C2-10". On disk they are ARCH-03:189 and :272. This is the third time (ADV-P7-C2-09, ADV-P8-C2-10): line-number anchors break on every ARCH-03 edit. Codify section-anchor citations instead. | product-owner |
| ADV-P9-C2-07 | LOW | wire-byte ambiguity | BC-1.04.001:71-72 | `Host: <host:port>` is imprecise. urllib sends the URL's netloc as written and percent-unquoted (`Request._parse` → `unquote(host)`), with a port only if the URL has one. An implementer could append a default port and diverge from the bytes on the fake listener. | product-owner |
| ADV-P9-C2-08 | LOW | mis-anchor | BC-1.04.016:99 | The VP row says "fields = the PC1 list". The field list is Precondition 1 (:42-47); PC1 (:52) is the queue postcondition only. | product-owner |
| ADV-P9-C2-09 | LOW | P20 convention drift (pending intent verification) | BC-1.04.003:62-65; .007:60,66; .009:62,65; .010:50-53; .011:49; .012:51-52; .017:46 | These postconditions hard-code default literals (90, 2, 5, 0.5, 12, 10/20/8, 1520/1280, 300, 1) even though registered keys exist. Siblings use the key names instead (BC-1.04.004 PC2 `fresh_s`, BC-1.04.007 PC3 `C`, BC-1.05.001/.002). An implementer reading the postconditions literally could hard-code the values. | product-owner |
| ADV-P9-C2-10 | LOW | registry contract column | interface-definitions.md:250, :220, :198 | `cost.display_floor_usd` lists only BC-1.02.029, but BC-1.05.003 PC3 also uses it. `cost.min_usd` lists only BC-1.05.001, but BC-1.05.005 PC2 also uses it. `sparkline.trace` lists only BC-2.02.004, but BC-1.04.009 also uses it. | architect |

I re-derived every other postcondition, edge case and vector in the 30 BCs against the legacy lines and found no mismatch. That covers the BC-1.04.020 11-step sequence and its cache bytes, the BC-1.05.008 thresholds (24,30)/(20,26) and all 12 golden rows, BC-1.05.005 indices and the NaN sort orders, the 37-hop worst case, the 2**1024 − 2**970 overflow threshold, sparkline glyphs and colours, KV cells, TTFT boundaries, and idle age text.

## 2. Policy compliance
- P1 PASS (EC numbering is append-only; BC-1.04.013 EC-010 sits after EC-009).
- P2 FINDING 05.
- P4 FINDING 06, 08.
- P5 PASS.
- P6 PASS: all 30 have `subsystem: "SS-01"`. I did not open the ARCH-INDEX registry this pass.
- P7 PASS: all 30 H1s match BC-INDEX; 9 sampled match the PRD.
- P12 PASS.
- P13 FINDING 01, 02, 03.
- P14 PASS (only RFC 5737 addresses).
- P16 PASS.
- P17 PASS.
- P18 PASS.
- P19 N.A.
- P20 FINDING 09 (LOW, pending intent).
- P21 PASS (no flagged strings quoted).

## 3. Not fully read / not verified
- **Read only in part or by grep:** VP-030, VP-012, VP-021, VP-001, VP-020, VP-024 bodies (frontmatter only); error-taxonomy.md, test-vectors.md, prd.md, invariants.md (grep); ARCH-03 (lines 180-239 only).
- **Not opened:** capabilities.md, ARCH-04, ARCH-INDEX.
- **Skipped:** the frontmatter header lines of BC-1.04.004-.021 and the BC-1.05 files.
- **Not oracle-run:**
  - Findings 01, 02 and 07 rest on my reading of the CPython 3.11.7 stdlib (`HTTPResponse.begin`, `urlsplit` sanitization, `Request._parse`), not on a run.
  - I accepted the BCs' stated oracle results without re-running them: BC-1.04.001 depth 992/993, the EC-022/023/024 runs, the BC-1.05.005 EC-009 exact values (540.0/720.0), and the BC-1.04.009 vector-1 colour bytes (only partly hand-checked).

## 4. Novelty
MEDIUM. Two new HTTP-client parity gaps and one new guard-ordering gap; the rest are sibling-propagation and anchor findings. **NOT_CONVERGED.**

## Perimeter D (S2-S6 BCs)

Findings: 20 (high 4, medium 9, low 6, cosmetic 1).

## Adversarial review, Phase 1d, pass 9, perimeter D (SS-02 to SS-06, 53 BCs)

### 1. Findings

All BC paths are relative to `specs/behavioral-contracts/`.

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P9-D01 | HIGH | Contradiction between BCs; mis-anchor (pass-8 D10 fix only partly applied) | `ss-06/BC-6.03.004.md:75-76, 94-107, 116-118, 197`; `ss-03/BC-3.02.002.md:86-88, 132`; `ss-06/BC-6.02.003.md:170-177`; `ss-03/BC-3.02.001.md:122` | BC-6.03.004 PC-1 says an entry's `case` must name an existing directory under `parity/cases/`. BC-3.02.002 Inv 2 and its VP row require one `OD-76` entry per D1-D4 case. Pass-8 D10 says no D1-D4 case is ever a corpus case. No exclusions.json can satisfy all three. EC-006 (line 197) still uses an OD-76 repeated-DST corpus case as its example; BC-6.02.003:174 says that hour cannot exist under UTC. The same problem applies to D4-EX-1: corpus cases seed `proc_start` (BC-3.02.001 Inv 4), so no Windows ⌂ corpus case can exist. | product-owner |
| ADV-P9-D02 | MEDIUM | Sibling BC not updated | `ss-03/BC-3.02.001.md:104-109`; `ss-03/BC-3.02.002.md:65-67` | BC-3.02.001 Inv 4 still says OD-76 cases "run UNSEEDED precisely to exercise the probe" with a fake process table. That contradicts pass-8 D10 (no corpus case declares a fake table). In BC-3.02.002, rows I1-I6 "must pass the ordinary byte comparison", but unseeded corpus cases are rejected, so these rows have no test vehicle. | product-owner |
| ADV-P9-D03 | HIGH | Propagation gap (blast radius 2+ files) | `ss-05/BC-5.02.003.md:107-111`; `architecture/ARCH-06-pyfmt.md:82`; `architecture/ARCH-03-statusline.md:177-178` | BC-5.02.006:93 changed the mix-cache save limit to 994 (pass-8 residual). BC-5.02.003 PC-7 still says "session/mix saves 991" and "Save budget EQUALS Load (session/mix 991/991)". ARCH-06:82 and ARCH-03:177 still say every cache has Save equal to Load. ARCH-06's own table row 70 says 994. | product-owner, architect |
| ADV-P9-D04 | MEDIUM | Contradiction within one BC | `ss-05/BC-5.02.006.md:78-85, 93` | PC-6 says the law `995 − s` holds "at every legacy encode site", which gives 991 at s=4. The mix row is s=4 with budget 994, and the BC does not state it as an exception to the law. "Payload 994" is never defined in the `Dumps` budget unit (total object nesting). | product-owner |
| ADV-P9-D05 | HIGH | Propagation gap (2 files) | `ss-02/BC-2.01.004.md:186-194`; `ss-02/BC-2.02.001.md:134, 183-187` | error-taxonomy.md:87 (pass-8 A11) treats `p75 <= p95` as a check inside the one key `statusline.cost.percentiles`: the error line names the whole key with its full JSON value. Both BCs still call it a cross-key pair that "names the SECOND key with its own value" and fires "at p95's validation". The stdout bytes for a descending percentiles pair therefore differ between the BCs and the taxonomy. | product-owner |
| ADV-P9-D06 | MEDIUM | Ambiguity in error order and `[from]` | `ss-02/BC-2.01.002.md:94-99`; `ss-02/BC-2.01.001.md:93-95`; `ss-02/BC-2.02.001.md:86-90` | BC-2.01.002 places a per-key `backends[1].metrics_url` error "in registry order", but BC-2.01.001 says `backends[<i>]` has no registry entry, so its position relative to e.g. `statusline.rows` is undefined. BC-2.02.001 PC-6's rule for array keys always names the lowest extra index. For an error at index 0 or index 2 that is the wrong variable. | product-owner |
| ADV-P9-D07 | MEDIUM | Ambiguous reason string and class | `ss-02/BC-2.01.005.md:151-162, 166-176`; `ss-02/BC-2.01.001.md:64-74` | For default-only Text/List keys (`units.*`, `limits.windows`), an empty value or a control byte could fail the parse (Text class: `expected non-empty control-free text` or `control character`) or parse and then fail the default comparison (number-range class: `out of range`). Both readings fit the text, and they produce different bytes. | product-owner |
| ADV-P9-D08 | MEDIUM | Missing error handling; per-OS gap (P18) | `ss-02/BC-2.01.005.md:137-164`; `ss-02/BC-2.01.003.md:77-79`; `ss-02/BC-2.01.004.md:207-216` | No BC says what happens when a Text, glyph, label or separator value contains invalid UTF-8. The width function is "total over valid UTF-8" only, and glyph code-point counting is undefined for invalid bytes. POSIX passes raw bytes; on Windows, Go converts the UTF-16 environment and maps unpaired surrogates to U+FFFD. Results therefore differ by OS, and `platform.EnvVars` does not specify this. | product-owner |
| ADV-P9-D09 | MEDIUM | Wrong domain statement | `ss-05/BC-5.04.001.md:53-54` (vs its own lines 92-94); `ss-05/BC-5.04.002.md:46-50` | The Description gives the working domain as the open interval `(1970-01-01T00:00:00, year 3001)`. CPython's fold-0 probe `u1 − 86400` is negative for any naive wall time before 1970-01-02T00:00 (in UTC; shifted by the zone offset), so e.g. 1970-01-01T12:00 degrades. A test written from the interval would expect a value. | product-owner |
| ADV-P9-D10 | MEDIUM | Test that cannot pass; per-OS (P18) | `ss-06/BC-6.01.002.md:160-162` vs `109-112` | PC-4 says the Windows oracle env "differs from the POSIX builder in that key alone" (`PYTHONIOENCODING`). PC-1's Windows set also adds `TMP`, `TEMP` and `SYSTEMROOT`. The table test as written cannot pass. | product-owner |
| ADV-P9-D11 | MEDIUM | Regression detector that detects nothing on some legs [process-gap] | `ss-06/BC-6.01.003.md:121-135` | The stdio canary claims to prove the stdio duty. On POSIX, `LANG=en_US.UTF-8` already gives UTF-8 and LF without the shim, so it cannot fail. On Windows, `PYTHONIOENCODING=utf-8` already fixes the encoding, so only the newline half is tested. PC-5's negative control covers the clock canary only. | product-owner |
| ADV-P9-D12 | MEDIUM | Integration gap [owner-question] | `ss-06/BC-6.02.002.md:54-79`; `ss-06/BC-6.02.003.md:149-155` | Real captures have a truthy `session_id` and no `proc_start` in a fresh cache dir. BC-6.02.003 PC-6 then rejects them (or they run against the machine's real process tree). BC-6.02.002 has no seeding rule, so the OD-107 real-input criterion cannot be met as written. | product-owner |
| ADV-P9-D13 | HIGH (per the rubric: mis-anchor that contradicts the same doc; actual impact low) | Mis-anchor | `ss-05/BC-5.02.003.md:52-53`; legacy `dgx_statusline.py:930`, `:1202` | Pre-1 says "SL:930, and SL:1202 for the subagent path". SL:930 is `main_subagent`; SL:1202 is `main()`. PC-7 (line 88) of the same BC anchors SL:930 to the subagent path correctly. | product-owner |
| ADV-P9-D14 | LOW | Generator format conflict | `ss-05/BC-5.02.002.md:96-97` vs `135` | The output format is stated as tab-separated `#\t<len>\t<repr>`, but the snippet prints space-separated (and the ADV-P3 D30 changelog says space-separated). CI byte-compares the committed table against a fresh run, so the format must be pinned. | product-owner |
| ADV-P9-D15 | LOW | Legacy site misdescribed | `ss-05/BC-5.01.007.md:69-70, 152`; legacy `:853, :857` | `_fmt_lines` calls `int(n)`, not `float(n)`. The float crossing is the mixed division at SL:857 (`n / 1e6`), not a call shaped `_fmt_lines(n / 1e6)`. | product-owner |
| ADV-P9-D16 | LOW | CPython algorithm misdescribed (could not verify) | `ss-05/BC-5.04.003.md:75-76` | CPython 3.11 `_PyTime_AsSecondsDouble` is, from memory, a whole-second integer branch, else `(double)t / 1e9`; it is not `secs + ns/1e9`. The BC's conclusion (divergence only when \|ns\| ≥ 2^62) follows from the real form, not the stated one. | product-owner |
| ADV-P9-D17 | LOW (pending intent check) | Domain gap | `ss-05/BC-5.01.004.md:47`; legacy `:1171-1172` | `D(n int64)` serves `{pct:>2d}`, where `pct = round(...)` is a `Num`. Mix counts from a poisoned cache (negative values) could push it past int64. No conversion rule is stated. | product-owner |
| ADV-P9-D18 | LOW | Edge case not covered | `ss-02/BC-2.01.005.md:79-83` | `HOME=""` (set but empty) during `~` expansion is unspecified. BC-2.03.002 PC-4 treats empty as unavailable. | product-owner |
| ADV-P9-D19 | LOW | H1 incomplete (P7) | `ss-06/BC-6.04.002.md:39` | The H1 and BC-INDEX title omit the large-transcript exemption (100 ms ceiling) that PC-3 defines. | product-owner |
| ADV-P9-D20 | COSMETIC | Wording | `ss-02/BC-2.02.001.md:87` | Repeated word "indexed indexed-entry". | product-owner |

### 2. Policy compliance
- **P1 (append-only numbering):** PASS. CP-T09 was appended and CP-T08 retired correctly.
- **P2 (lift invariants to BCs):** PASS, sampled only (DI-008, DI-010, DI-012 citations present).
- **P4 (semantic anchoring):** FINDING D01, D13.
- **P5 (creators justify anchors):** PASS.
- **P6 (subsystem names):** PASS. Labels are SS-02..SS-06; I did not open the ARCH-INDEX registry.
- **P7 (H1 = BC-INDEX = PRD title):** PASS for all 53 H1 vs BC-INDEX rows; LOW D19. PRD not checked.
- **P12 (settled decisions are constraints):** PASS; D12 tagged [owner-question].
- **P13 (parity before behavior change):** PASS.
- **P14 (public-repo hygiene):** PASS.
- **P16 (thresholds explained):** PASS. The BC-5.01.004 width rationale is thin but labeled.
- **P18 (cross-platform from day one):** FINDING D08, D10, D11.
- **P19 (Go hardening toolchain):** N.A.
- **P20 (config over code):** PASS.
- **P21 (public-artifact hygiene):** PASS.
- **P3, P8, P9, P10, P11, P15, P17:** N.A.

### 3. Coverage and unverified claims
- **Read in full:** all 53 BCs in the perimeter.
- **Cross-checked in part:** ARCH-06 (lines 60-99 and 130-189), ARCH-03:155-180, error-taxonomy rows 86-94, BC-INDEX, and VP and ARCH-07 by grep.
- **Not read:** prd.md, capabilities.md, invariants.md, the other ARCH documents, and the VP bodies.
- **Python claims I could not verify:**
  - CPython 3.11.7 actually uses C `_path_normpath` for ntpath (BC-5.03.004 Inv 2).
  - The exact `_PyTime_AsSecondsDouble` form (D16).
  - The upper bound of MSVC `_localtime64_s`.
  - Whether the 4,300-digit limit counts leading zeros.
  - The mix-save measurement of 994.
  - The golden A/B/C byte totals.

### 4. Novelty
MEDIUM. D01, D03 and D05 are fixes made in pass 8 that did not reach sibling files; D06-D12 are new.

NOT_CONVERGED
