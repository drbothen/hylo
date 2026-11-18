---
document_type: adversarial-review
phase: 1d
pass: 6
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 124
---

# Adversarial Spec Review — Phase 1d, Pass 6

Pass 6 ran as six fresh-context perimeters, the same split as passes 1-5. Each section is the verbatim final report of one perimeter, unedited except for this framing and repo-relative paths. Per-perimeter novelty: A MEDIUM, A2 MEDIUM, B MEDIUM, C MEDIUM, C2 HIGH, D MEDIUM. NOT_CONVERGED (124 findings: HIGH 27 / MEDIUM 52 / LOW 38 / COSMETIC 7; pass 5 had 148 with 24 HIGH). The orchestrator spot-verified A04 (U+26A1 is East-Asian-Width W), A06 (SL:255 is a division), A2-03, A2-05, B02, B06, C2-01, C2-05 and D07 on disk and against CPython 3.11.7; all held. D07 shows the pass-5 rejection of ADV-P5-D16 was wrong.


## Perimeter A (PRD, supplements, architecture, CI)

Findings: 21 (high 6, medium 12, low 2, cosmetic 1).

## 1. Findings

| ID | Sev | Category | File:line | Defect (evidence) | Owner |
|---|---|---|---|---|---|
| ADV-P6-A01 | HIGH | contradiction / partial-fix regression | architecture/ARCH-02-configuration.md:58-61, :138, :142 | ARCH-02 still says the error register is "closable at six classes… a seventh class needs an owner decision". Its anchors `#seconds` and `#classes` also say "closed six-class register". OD-178 made it seven (ARCH-INDEX.md:79, error-taxonomy.md:71, prd.md:498). The Text class (BC-2.01.005) has no ARCH-02 home or anchor. | architect |
| ADV-P6-A02 | HIGH | contradiction (oracle pin) | prd-supplements/nfr-catalog.md:26; prd-supplements/assumptions-register.md:23 vs ARCH-08-build-ci-release.md:42, :59-62; cicd-setup.md:161-163, :168, :179 | NFR-003 and ASM-001 say "CI installs 3.11.x (setup-python resolves the latest patch, OD-104/ARCH-08)". ARCH-08 and cicd-setup now require "3.11.7 EXACT". ARCH-08:52-53 still records a "resolved patch version" in golden metadata (RK-4), which only makes sense for a floating pin. | product-owner, architect |
| ADV-P6-A03 | HIGH | cross-platform (P18) / unstated assumption [owner-question] | ARCH-07-parity-harness.md:68-75 | The Windows child-env allowlist has no locale setting and forbids `PYTHONUTF8` and `PYTHONIOENCODING` on both OSes. Legacy decodes stdin with `json.load(sys.stdin)` (legacy SL:930, :1202) and never reconfigures stdio (grep: no `reconfigure`). CPython 3.11 piped stdio on Windows uses the ANSI code page, so the strict-UTF-8 parity mode of BC-1.01.008 cannot be reached on the windows-2025 oracle. Glyphs outside cp1252 will raise UnicodeEncodeError, which turns into the degraded line in `*.windows.golden` and in Windows Tier A/C. OD-159 covers file reads only (prd.md:591). Needs a ruling: either a Windows stdio pin or an exclusion. | architect |
| ADV-P6-A04 | HIGH | config range contradicts default [owner-question] | prd-supplements/interface-definitions.md:263 (`watts` U+26A1); ARCH-06-pyfmt.md:190-219; BC-2.01.004:136, :183-187 | U+26A1 has East-Asian Width W in Unicode 14 (Emoji_Presentation=Yes). Under the OD-170 validation width it measures 2, so the legacy default breaks its own range "exactly 1 code point and 1 column" (OD-02). Result: either a build-time defaults-in-range check fails, or setting the default value explicitly through env is a config error. | product-owner |
| ADV-P6-A05 | HIGH | architecture contradiction (AD-02) | ARCH-05-platform.md:34 vs ARCH-00-overview.md:71-72; ARCH-06-pyfmt.md:19-20, :118-123 | `localtime_windows.go` (in platform) is "Consumed by py/time.go's LocalToUnix". That makes pyfmt import platform. ARCH-06 forbids this ("importing infrastructure from it would invert AD-02") and says Basename is pyfmt's only GOOS-dependent logic. The Windows mktime failure domain therefore has no legal home. | architect |
| ADV-P6-A06 | HIGH | wrong mechanism (would mislead implementer) | ARCH-03-statusline.md:93 | ARCH-03 says CP-O10/O11 is "a huge exact int… breaching int-to-string in `cost_thresholds` at SL:255". Legacy SL:255 is `usd / (api / 3.6e6)`, which raises OverflowError on int→float conversion at \|n\| >= 2**1024−2**970 (error-taxonomy.md:125, :135-136, :185). An int over 4,300 digits cannot even load. A trigger built on int-to-string would miss every 310..4,300-digit value. | architect |
| ADV-P6-A07 | MEDIUM | interface gap / parity | ARCH-06-pyfmt.md:31 ("Mode-site pairing"); ARCH-03-statusline.md:196 | The pairing names ModeText for stdin/caches and ModeBytes for transcript lines, and reads as exhaustive. It omits the metrics reply, which legacy decodes with `json.loads(resp.read())` on bytes (SL:171), so BOM/UTF-16/32 detection applies. No BC pins the mode (grep across behavioral-contracts). | architect |
| ADV-P6-A08 | MEDIUM | interface cannot express BC | ARCH-02-configuration.md:85, :103-106, :110 | `Load(opts) (*Config, *ErrorSet)` has no stderr sink, and `LoadOptions` defines no fields except FileLayer. BC-2.01.001 PC-6 and Inv-3 make Load emit unknown-setting warnings, with the order "warning first, then load error". Separately, BC-2.01.001:87 names a `platform.Environ` seam where ARCH-01:33 and ARCH-05:31 define `EnvVars`. | architect |
| ADV-P6-A09 | MEDIUM | parity outside the closed set (P13) / config over code (P20) [owner-question] | ARCH-04-data-files.md:61-72 | The Windows rename retry persists a cache write where legacy (no retry, IM-17) persists nothing. That is a cache-byte divergence. It is attributed to the `temp-file` exclusion, but that id covers temp names and cleanup only (BC-6.03.003 title, prd.md:409). Also: ":68 two attempts" contradicts VP-018:112 (fails = limit+1 = 3 attempts). The 10 ms retry delay is a timing value but is not a registry key (D15). | architect |
| ADV-P6-A10 | MEDIUM | CI positive coverage (P11) | ARCH-08:90-93, :98-100; cicd-setup.md:79, :81 | Tier A prints `K caches swapped` but nothing fails when K==0, so the four-cache swap tier (BC-6.02.004, VP-019, R-001 mitigation) can check nothing and pass. Tier C's `N inputs per side, M oracle spawns` has no N==0 or M==0 failure. Yet one clean Tier C nightly run is the P1 exit condition (OD-149, ARCH-INDEX:106-108). | architect, devops-engineer |
| ADV-P6-A11 | MEDIUM | CI gate wiring (P11) | cicd-setup.md:251-257 vs ARCH-08:70-77, :143-147 | The required checks list leaves out the coverage gate (a P1 exit gate), `govulncheck (required)`, and the staticcheck-extended lint job, whose name `lint (gofmt + vet)` goes stale. These gates can fail without blocking a merge. Whether coverage is a "required step" (ARCH-08:70) or a separate job (cicd-setup:86) is ambiguous. | devops-engineer |
| ADV-P6-A12 | MEDIUM | CI timeout / duplication (P11) | cicd-setup.md:52 vs :55 | Tier A runs inside the plain test step under the test job's 30-minute timeout. The dedicated Tier A job budgets 45 minutes for the same corpus. Which run is authoritative is undefined, and the tighter budget can kill the run. | devops-engineer |
| ADV-P6-A13 | MEDIUM | ambiguity (default-only keys) | interface-definitions.md:114-153, :195-197, :230 | These defaults cannot be written in their own env grammar: `theme.heat` is "Float (triple)" `0.22/0.85/0.80` with no per-key JSON shape in the binding list; `limits.windows` is a List with default `5h/7d` against a comma grammar; `units.lines` and `units.tokens` are single Text keys with default `k`/`M`. OD-162 says "an env value equal to the default is accepted" (:126), but which env string equals these defaults is undefined. | product-owner |
| ADV-P6-A14 | MEDIUM | missing error vocabulary | error-taxonomy.md:76-92; interface-definitions.md:169, :225 | Two cases have no reason string or class: a List-entry violation in `lane.reroute_all_prefixes` (empty or control-byte entry), and a control byte in the non-theme `subagent.joiner`. The joiner row cites the theme class's PC-3, while `control character` is mapped only to URL and theme. The bytes of the resulting D4-EX-3 line are therefore undefined. | product-owner |
| ADV-P6-A15 | MEDIUM | mis-anchor (P4) | ARCH-04-data-files.md:100 | ARCH-04 maps "BC-1.02.013/.005 git cache". BC-1.02.013 is rate-limit smoothing over the session cache (its H1; BC-COMPONENT-MAP:57). | architect |
| ADV-P6-A16 | MEDIUM | mis-anchor (P4) | interface-definitions.md:169 vs BC-2.01.004:177 | The reroute-all key's consumer is BC-1.02.009 in interface-definitions but BC-1.02.011 (pace bands) in BC-2.01.004. Legacy SL:487-489 is the limits-hide rule, which belongs to BC-1.02.009. | product-owner |
| ADV-P6-A17 | MEDIUM | inactive mitigation | prd-supplements/risk-register.md:29; ARCH-08:70-77 | R-004 (HIGH impact, fake-pass parity) relies on the "HIGH kill-rate tier". OD-158 makes kill rate a Phase 6 target, and `internal/parity` has no P1 line-coverage gate. The mitigation is inactive throughout P1. | architect |
| ADV-P6-A18 | MEDIUM | interface gap / ownership ping-pong | ARCH-06:32; ARCH-03:142-143, :201-205; BC-5.03.004:63-68 | ARCH-06 puts Windows `abspath` (GetFullPathNameW) in statusline "against the Cwd/Files seams". `Cwd func() string` cannot express drive-relative `C:rel` resolution, which BC-1.02.004 EC-012 needs. ARCH-06 also lists the flavor pinning as an open product-owner obligation, while BC-5.03.004 says the gap was flagged to the architect. | architect |
| ADV-P6-A19 | LOW | ambiguity | interface-definitions.md:226-227 | The cross-key constraint `k_from <= m_from` has no rule for which key and value the D4-EX-3 line names. The registry-order rule assumes each key is validated on its own. | product-owner |
| ADV-P6-A20 | LOW | rationale inconsistency (pending intent verification) | ARCH-07:127; error-taxonomy.md:96-99 | "No Theme member — corpus validator rejects theme settings" no longer explains the split: Text also has no legacy analog and still gets `TestD4EX3_Text`. The theme class line has no canonical test name. | architect |
| ADV-P6-A21 | COSMETIC | wording | ARCH-00-overview.md:20 | "Pure function of stdin + transcript + metrics + caches" leaves out the git, process, clock and env seams listed at prd.md:66 (AD-10). | architect |

## 2. Policy compliance
- P1: PASS
- P2: PASS (not deep-checked)
- P4: FINDING A15, A16
- P5: PASS
- P6: PASS
- P7: PASS (all 154 PRD titles match the BC H1s)
- P9: PASS (41 VPs; class and method sums and ARCH homes verified)
- P11: FINDING A10, A11, A12
- P12: PASS
- P13: FINDING A09, A03
- P14: PASS
- P16: PASS
- P17: PASS
- P18: FINDING A03, A05, A18
- P19: PASS
- P20: FINDING A09 (retry delay; no DGX_* aliases found)
- P21: PASS
- P3, P8, P10, P15: N.A.

## 3. Files not fully read
None in the perimeter. All perimeter files under .factory/specs/ were read in full. BC and VP files were opened only for spot checks: BC-1.05.004/.009, BC-5.03.004, BC-1.02.004, BC-2.01.001, BC-2.01.004, BC-1.01.008, BC-6.04.002, BC-1.04.001, VP-018, VP-INDEX.

## 4. Novelty
MEDIUM. A03, A04, A05, A06 and A07 are new substantive gaps; A01 and A02 are prior fixes that only partly propagated.

NOT_CONVERGED


## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 28 (high 8, medium 13, low 7, cosmetic 0).

## 1. Findings

| ID | Sev | Category | File:line | Defect (evidence) | Owner |
|---|---|---|---|---|---|
| ADV-P6-A2-01 | HIGH | Skeleton fails a correct implementation | VP-001:137-163 | In `assertPromisedOutputSet`, the subagent branch never returns. The parse-fault path drops into the renderer block (it has no `!parseFault` guard), and then the main-entry check `len(stdout)==0` → Fatal runs. So legal zero-byte output (config error per OD-168, zero tasks, non-object stdin) and valid NDJSON rows (which are not `isRenderBytes`) fail. | architect |
| ADV-P6-A2-02 | HIGH | Wrong fault site / wrong oracle | VP-020:52-56, 104-121 | The OD-166 leg seeds the cost *history* and expects `degradedLine` for both fields. BC-1.05.004 EC-010/011 (:113-114) put the unconvertible value on *stdin*, and EC-011 (huge negative `api_ms`) "renders normally". A seeded history value exercises CP-O10/O11 (`cost_thresholds`, SL:255), where record_cost at step 7c may legitimately write. The statement at :55 ("still degrades") also contradicts EC-011. | architect |
| ADV-P6-A2-03 | HIGH | Test can never fail; invalid Go | VP-016:113-120 | `TestTheme_SGREscapeFree` throws away the error from `quick.Check`, so it can never fail. This is the defect A2-05 fixed in VP-040; the sibling was missed. It also joins `[]byte` values with `+` (does not compile), and it generates arbitrary `[]string` rather than accepted SGR values. | architect |
| ADV-P6-A2-04 | HIGH | Never runs on CI (P18) | VP-026:111-136 | `osZoneExpectation` calls `t.Skip`, which ends the whole test. On UTC runners (the GitHub-hosted default) the OD-177 empty/UTC/IANA/unparseable rows therefore never execute. The rows need `t.Run` subtests. | architect |
| ADV-P6-A2-05 | HIGH | API drift; oracle legs missing | VP-024:85-100 | The skeleton calls `DumpsLen(v)` and `Dumps(v)` with one argument and one result. BC-5.02.001:39 (D28) and BC-5.02.006:41 now define `(v, budget) → (int or []byte, error)`, so the skeleton does not compile. BC-5.02.001:143 and BC-5.02.004:98 send "fuzz + oracle" legs to VP-024, but VP-024 disclaims any oracle call (:64-66). | architect |
| ADV-P6-A2-06 | HIGH | Cross-platform (P18) | VP-034:93-105 | `setsEqual` checks against `oracleAllowlistPosix` on every OS. The Windows child env this same VP mandates (TEMP/TMP/HOMEDRIVE/HOMEPATH/SYSTEMROOT, no TMPDIR/LANG) can never equal that set, so a correct implementation goes red on windows-2025. | architect |
| ADV-P6-A2-07 | HIGH | Contradicts BC; would mislead an implementer | domain-spec/state-machines.md:99; VP-013:41-43 | Both state the OD-32 reader rule as "numeric `cur.t0` ⇒ no open turn". They drop BC-1.03.020's second condition (:39, :104): `out` must also be non-numeric. Read literally, every normal open turn would be discarded. | business-analyst, architect |
| ADV-P6-A2-08 | HIGH | Partial fix not propagated (2+ files) | VP-016:75, 91, 150; architecture-feasibility-report.md:52; BC-2.01.002:135 | OD-178 (seven classes) did not reach these spots. VP-016 says "four canonical names" but lists five, and says "six classes" twice. The feasibility report says "six error classes closed". BC-2.01.002 says "closed six-class register (no seventh class)". | architect, product-owner |
| ADV-P6-A2-09 | MEDIUM | Internal contradiction; routed legs missing | VP-017:40-43, 59-61, 81-83 | On `backends=0`: the statement and skeleton say the guard is tested at P4, but Method says it is exercised at the validator seam now. Separately, BC-2.01.002:133-134 sends two testing/quick properties to VP-017 ("Load ⇒ exactly one entry"; "`metrics_url` never ends with `/`"). VP-017 contains neither. | architect |
| ADV-P6-A2-10 | MEDIUM | Sibling regression | VP-012:122, 70, 74, 162 | `LoadExclusions` uses a cwd-relative path. That is the A2-16 defect fixed with `ModuleRoot` in VP-009:83 and VP-010:83; from the `internal/parity` cwd it loads nothing and false-reds. The prose also still spells the family globs `…D4EX1_Windows*` and `…OD76_*`, which the VP's own glob check at :128 rejects. | architect |
| ADV-P6-A2-11 | MEDIUM | Stale prose; P11 | VP-011:57-59, 63-65, 87-93 | Two passages still say every divergence "must carry a closed-set exclusion id". That contradicts the 1.5 rule (:39-43): exclusions are kept out by construction and any divergence fails. The skeleton also never counts compared cases, so a run that hits only `continue` passes green. | architect |
| ADV-P6-A2-12 | MEDIUM | Prose contradicts skeleton | VP-021:62-63, 91-92; VP-030:66-67 | Both say each property's oracle "is that BC's canonical table". Their skeletons (VP-021:96-98, VP-030:101-103) say the opposite and re-derive the property instead. VP-021 also generates `th` independently of `rates` while asserting percentiles derived from `rates`, so `th` is unconstrained. | architect |
| ADV-P6-A2-13 | MEDIUM | Invalid Go | VP-005:102, 108; VP-008:79; VP-039:113-123 | VP-005 compares `stdout` with `==` against `degradedLine` and also passes it to `utf8.Valid`. One of the two fails to compile whichever type `stdout` has. VP-008: `err` is declared and never used. VP-039: the detector file has no `import "testing"`. | architect |
| ADV-P6-A2-14 | MEDIUM | Statement vs skeleton | VP-039:43-46, 52, 100-101 | The statement promises a bit-exact comparison against CPython goldens. The skeleton compares only `mmss()` strings, so ulp drift that doesn't change the displayed second passes. The bit-exact leg of the detector is absent. | architect |
| ADV-P6-A2-15 | MEDIUM | Wrong quantity generated | VP-040:115-124 | P7 is about the `statusline.rows` setting (BC-1.01.007:40-53). The generator varies segment text and guards on `len(segs)` instead. `rows` never varies, and the `rows==2` half of the "iff" (row 2 hidden) is never tested. | architect |
| ADV-P6-A2-16 | MEDIUM | Oracle discipline contradiction | VP-041:137-143, 83-85 | P-g calls live CPython from inside an in-tree `internal/statusline` quick test. VP-038:46-48 says the oracle is not callable from unit tests, and VP-010 promises interpreter-free matching. Method lists P-g under both quick and Tier C, and gives P-h an "oracle half" it doesn't have. | architect |
| ADV-P6-A2-17 | MEDIUM | Self-confirming oracle | VP-006:110-123, 48, 50 | `budgetOf(c.name)` looks the budget up by the test's own label, so the test only shows that Decode honours a budget it is given. A production call site passing the wrong budget, which the 1.6 note says is "now detected", is not detected. The subagent row (:48) is missing from the harness, and `bcs:` omits BC-5.02.004 (cited at :50). | architect |
| ADV-P6-A2-18 | MEDIUM | Skeleton fails a correct implementation | VP-003:77 | One `degradedStdin` serves both entries. A stdin that faults the main entry is usually not a CP-A fault for the subagent entry, which then legally emits zero bytes. `w.Writes()==0` then fails. | architect |
| ADV-P6-A2-19 | MEDIUM | Body vs history vs brief [owner-question] | VP-036:44-48, 22; product-brief.md:88-89 | The body declares the >512 KB exemption UNCONDITIONAL (citing ADV-P5-A2-13), with no version bump. The VP's latest history entry (1.4) says conditional, and the brief makes the exemption conditional on the fixture missing the target. | product-owner |
| ADV-P6-A2-20 | MEDIUM | Sibling gap | dtu-assessment.md:27-30, 84-90, 158-166 | The summary says "four non-network contracts" but lists five. Row #6 (transcript) is missing from the Dependency Summary and from "Services NOT Requiring DTU". Pass-4 A2-21 fixed exactly this gap for row #5. | architect |
| ADV-P6-A2-21 | MEDIUM | P11 positive coverage | VP-035:65; VP-036:81-86; VP-001:103 | The gitleaks/category-scan leg has no planted canary (VP-022/041 have one). The timing gate passes with zero measured cases. The `FaultInjectionTable` loop asserts no non-zero count. | architect |
| ADV-P6-A2-22 | LOW | Versioning [process-gap] | VP-028:42; VP-039:108-111; VP-036:48; VP-012:25-26 | Body edits for ADV-P5-A2-33/A2-18/A2-13 have no version bump or history entry; this is a three-file pattern. VP-012 history lists 1.4 (02:24) before 1.3 (09:04), even though 1.11 claims the history was re-ordered chronologically. | architect |
| ADV-P6-A2-23 | LOW | Statement vs skeleton | VP-009:37-38, 83 | The statement covers replay of `captures/`, and the brief's success criterion needs it. The skeleton loads only the committed corpus. | architect |
| ADV-P6-A2-24 | LOW | Stale count | invariants.md:46 | It says DI-008 = 83 BCs; the stated grep method returns 84 files today. | business-analyst |
| ADV-P6-A2-25 | LOW | Assessment no longer holds | gene-transfusion-assessment.md:43, 70, 116 | The 100/62 SP totals for all of P1 are reused verbatim as the `internal/statusline` row. The doc says "SA §4 estimate carries over unchanged" even though OD-155 later added the subagent renderer and 8 BCs. | architect |
| ADV-P6-A2-26 | LOW | Phase not split; ambiguity | capabilities.md:29, 37; invariants.md:33 | CAP-007 is marked P3, but its status-line clause (BC-1.02.030 `effective_rl`) ships in P1, with no split like CAP-015's. The "file → env → default" chain is ambiguous next to PLAN.md:109, where env overrides file. This matters at P4, not P1. | business-analyst |
| ADV-P6-A2-27 | LOW | Coverage scope | VP-035:37, 72 | `TestCorpusHygiene` only covers `internal/statusline/testdata`. Fixtures in `cmd/hylo/`, `internal/config/` and `internal/pyfmt/testdata` are outside it. | architect |
| ADV-P6-A2-28 | LOW | Oracle not connected to output | VP-015:112 | `env.StderrContainsUnknownSettingWarning()` is a method on the generated env. No stderr from `Load` is ever captured, so the check doesn't look at real output. | architect |

## 2. Policy compliance

- P1 append_only_numbering: PASS (version-order issue only, A2-22).
- P2 lift_invariants_to_bcs: PASS.
- P4 semantic_anchoring_integrity: FINDING A2-02, A2-07.
- P5 creators_justify_anchors: PASS.
- P6 subsystem names: PASS (spot-checked only, not exhaustive).
- P9 vp_index_is_vp_catalog_source_of_truth: PASS (catalog and coverage map match the VP frontmatter I sampled).
- P11 ci_positive_coverage_assertion: FINDING A2-11, A2-21.
- P12 settled_decisions_are_constraints: FINDING A2-19 [owner-question].
- P13 parity_before_behavior_change: PASS.
- P14 public_repo_hygiene: PASS.
- P16 thresholds_are_explained: PASS.
- P17 ledger_format_frozen: PASS.
- P18 cross_platform_from_day_one: FINDING A2-04, A2-06.
- P19 go_hardening_toolchain: PASS.
- P20 config_over_code: PASS.
- P21 public_artifact_hygiene: PASS.
- P3, P7, P8, P10, P15: N.A.

## 3. Files not fully read

All perimeter files were read. I skipped only frontmatter boilerplate: lines 1-8 of VP-005 through VP-041, lines 1-29 of VP-004, and lines 1-13 of the domain-spec shards.

## 4. Novelty

Novelty: MEDIUM. Eight HIGH findings are new, mostly skeletons that won't compile, can't fail, or would fail a correct implementation, plus fixes that didn't reach sibling files.

NOT_CONVERGED


## Perimeter B (BC-1.01/1.02)

Findings: 16 (high 1, medium 8, low 6, cosmetic 1).

## ADV-P6-B: adversarial pass 6, Perimeter B (BC-1.01.\*, BC-1.02.\*)

I checked all 40 BCs against the legacy lines they cite and re-derived the Python results by hand. The postconditions match legacy in every case I checked. That covers heat RGB, half-even ties, float floor-division countdowns, the 1.15 gate (695520.0 and 20700.0 rounding), the staircase sums, byte counts (29/45/64) and the smoothing sequences. The defects below are about anchoring, test vectors, cross-document consistency and cross-platform gaps, not wrong legacy transcription.

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P6-B01 | HIGH | VP anchoring / partial fix [process-gap] | BC-1.02.002:91, .003:104, .006:145-146, .007:102, .009:102, .010:102, .013:118, .015:111 | These rows assign "for all … / property test" proofs to VP-028. VP-028 (lines 53-56) says the testing/quick and for-all legs are delivered by VP-041. VP-041's `bcs:` (line 13) lists only .001/.004/.016/.018/.019/.021/.022/.023/.025/.027/.028. So about 8 BCs have for-all claims that no VP actually delivers. ADV-P4-B03 moved some siblings to VP-041 and left these behind. | architect + product-owner |
| ADV-P6-B02 | MEDIUM | Test vector doesn't discriminate | BC-1.02.011:88,111; BC-1.02.012:87 | EC-011/EC-013 say −10³⁰⁰ is "same magnitudes as EC-010". It is not: 1e300 < 2**1024−2**970 and converts to float fine. The CTV row (−10³⁰⁰) therefore passes on a Go port that converts to float64 at decode and would fail the real case. The oracle check quoted in the text used −10**400. The vector should use ≤ −OV. | product-owner |
| ADV-P6-B03 | MEDIUM | Wrong source label | BC-1.02.025:85 (EC-010) | The CP-O04 overflow is labelled "stdin-borne", but `_fmt_tok_c` only receives transcript/mix totals (BC-1.02.018 Inv 1; SL:576-578). The real path is an integer-only transcript accumulation (no float operand, so the CP-O06 skip never fires; error-taxonomy:176-178) or the mix cache. A test author following the BC cannot trigger it from stdin. | product-owner |
| ADV-P6-B04 | MEDIUM | Effect-order contract gap | BC-1.01.009:88-92 vs footnote 2 (:83-86) and legacy SL:606-607 | PC2 says a degrade at step k performs none of steps k..8 and lists only CP-C10 and OD-166 as within-step exceptions. The history-borne CP-O10/O11 raise in `cost_thresholds` (step 7c) happens after the same step's `record_cost` write. That case is reachable through a Python-written history (VP-019 swap) and is not foreign-shaped. As written, PC2 and VP-008 ("writes of steps < k") forbid a write that legacy performs. | product-owner |
| ADV-P6-B05 | MEDIUM | Cross-platform gap (P18) | BC-1.02.004:61-69, EC-013 :114 | The path-encoding pin (surrogateescape: U+DC80..DCFF become raw bytes, other lone surrogates make `isdir` return False) is POSIX-only. On Windows, CPython passes str paths as wide strings, so a lone surrogate is a valid UTF-16 unit and can stat a real directory. Go's UTF-16 conversion would substitute U+FFFD instead. No Windows leg is specified. Confidence medium (inferred, not oracle-run). | product-owner |
| ADV-P6-B06 | MEDIUM | Missing edge case | BC-1.01.008:49-52, EC table :72-79 | PC2 says Go keeps surrogates as WTF-8, but nothing says whether raw encoded surrogate bytes on stdin (ED A0 80) count as invalid UTF-8. CPython's strict decoder rejects them, giving `{}`. A WTF-8-lenient Go decoder would accept them and render. Needs an explicit EC and vector. | product-owner |
| ADV-P6-B07 | MEDIUM | Rationale-code mismatch (P16) | BC-1.02.012:68 vs interface-definitions:231; BC-1.02.015:67-69 / .016:62-63 vs :235-236; BC-1.01.003:70-72 vs :162-163 | Each pair gives a different rationale code: countdown_max_factor is "T-035 owner judgment, OD-57 E-A" in the BC but "DOC" with no T-code in the registry; timer.min_ms / api_min_ms are "derived" vs "DOC"; rows is "convention" vs "DOC"; narrow_cols is "OWNER group B" vs "J". The rationale is supposed to sit next to the default, and the two documents disagree on it. | architect |
| ADV-P6-B08 | MEDIUM | Sibling not updated after a fix | BC-1.02.023:110 (vs BC-1.02.008:109); also .007:63/115, .014:145, .015:123, .017:127, .028:110, .029:118 | ADV-P5-B03 renamed the ♻ glyph to `statusline.glyphs.cache_hit` in BC-1.02.008. BC-1.02.023 renders the same glyph and still cites the wildcard `statusline.glyphs.*`. The other listed BCs also cite the wildcard even though named members now exist (tools/conversation/thinking, lines_up/down, timer, window_age, cost_pick). | product-owner |
| ADV-P6-B09 | MEDIUM | Stale cross-reference (pass-4 B19 sibling) | BC-1.02.027:165 | "the int64 sketch in error-taxonomy.md:120-124 is superseded" points at lines that now hold the OD-156 register header. error-taxonomy:151-155 itself declares this cross-reference stale "in both directions"; this BC still carries it. | product-owner |
| ADV-P6-B10 | LOW | Vector under-specified | BC-1.02.011:110 | The OV row gives "5h `resets_at` = OV" with no `used_percentage`. Without a numeric pct the window `continue`s at SL:513-514 and SL:515 is never reached, so a literal reading produces no degrade. | product-owner |
| ADV-P6-B11 | LOW | Precondition incomplete | BC-1.01.001:56-61 | Precondition 1 includes the `--subagent` render, but the guarded-site list in Precondition 3 omits CP-A01..A05 (they appear only in EC-007). | product-owner |
| ADV-P6-B12 | LOW | Unexplained constant (P16/P20) | BC-1.02.004:41,84-85 | The detached-HEAD `ref[:7]` length is neither marked as a named format constant with a why-not-config note (D15) nor explained. Compare BC-1.02.005 Inv 2, which handles `[:16]` that way (T-062). | product-owner |
| ADV-P6-B13 | LOW | Ambiguous postcondition | BC-1.01.002:61-62 | "Leading/trailing whitespace (incl. newlines) … accepted" is ambiguous. Python json accepts only space, tab, LF and CR; form feed, VT and NBSP produce `{}`. A reader could implement `strings.TrimSpace`. Pin the four-character set. | product-owner |
| ADV-P6-B14 | LOW | PRD prose drift | prd.md:452-455 | "Objects read" omits `context_window` (SL:463, BC-1.02.006/.020) and `cwd` (SL:452, BC-1.02.003). | product-owner |
| ADV-P6-B15 | LOW | Stale supplement sentence | interface-definitions.md:300-301 | "Members of `statusline.glyphs.*` are never named individually in BC bodies" is now false: BC-1.02.001/.005/.006/.008/.018 name members. | architect |
| ADV-P6-B16 | COSMETIC | Version-history skew | BC-1.01.005:4,22-24 | Version is 1.3.3 but the history labels are 1.2.1, 1.2.2, 1.3.3, and the 1.3.3 entry refers to a "preceding 1.3.1" entry that doesn't exist. Separately, unversioned history entries remain in BC-1.02.001/.003/.011/.012/.016/.021/.023/.029, despite the SC-17/20 "version-prefixed" sweep. | product-owner |

### 2. Policy compliance

- **P1 append_only_numbering:** PASS (1.01.001-010 and 1.02.001-030 are contiguous; legacy_ids are unique).
- **P2 lift_invariants_to_bcs:** PASS (the DI-007/008/012 citations are present where exclusions or effects apply).
- **P4 semantic_anchoring_integrity:** FINDING B01, B08, B15.
- **P5 creators_justify_anchors:** PASS.
- **P6 subsystem name:** PASS (all `SS-01`, matching the ARCH-INDEX registry, line 55).
- **P7 H1 = BC-INDEX = PRD:** PASS (all 40 titles identical; H1s describe their postconditions).
- **P12 settled_decisions_are_constraints:** PASS.
- **P13 parity_before_behavior_change:** PASS.
- **P14 public_repo_hygiene:** PASS (no hygiene terms, real IPs or home paths in the perimeter).
- **P16 thresholds_are_explained:** FINDING B07, B12.
- **P17 ledger_format_frozen:** N.A. (no ledger surface in this perimeter).
- **P18 cross_platform_from_day_one:** FINDING B05.
- **P19 go_hardening_toolchain:** N.A.
- **P20 config_over_code:** FINDING B12 (LOW). OD-05 check passes: no `DGX_*` aliases.
- **P21 public_artifact_hygiene:** PASS.

### 3. Files not fully read, and Python claims I could not verify

**Partially read:**
- interface-definitions.md (lines 150-349 only)
- error-taxonomy.md (lines 110-210)
- ARCH-03 (lines 40-110 plus the anchor list)
- VP-028 and VP-041 (headers and property statements)
- VP-040
- prd.md (line ranges plus grep)
- invariants.md (DI rows 28-40)
- capabilities.md (grep only)

**Not read:** test-vectors.md, BC-5.\*, BC-2.\*.

**Not verified:**
- The golden A/B/C segment widths and the "ends `◈ 8%`" claim in BC-1.01.010 (the staircase arithmetic itself checks out).
- The ntpath C-implementation results on Windows.
- The exact digits of the 1e24 and 5e23 `_hm` outputs.
- The 993/994 depth boundary.
- CPython-on-Windows lone-surrogate stat behavior (the basis of B05; inferred).

### 4. Novelty

MEDIUM. B01, B04, B05 and B06 are new structural gaps; the rest are refinements and propagation misses.

NOT_CONVERGED


## Perimeter C (BC-1.03/1.06/1.07)

Findings: 17 (high 2, medium 2, low 11, cosmetic 2).

## ADV-P6-C: Adversarial review, Phase 1d, Pass 6, Perimeter C (BC-1.03.*, BC-1.06.*, BC-1.07.*)

I read all 31 perimeter BCs in full and opened the legacy lines each one cites (SL:190-206, 265-359, 849-1154, 1205-1245). I recomputed the byte sizes and Python results in every canonical vector by hand: BC-1.03.002, .003, .004, .005, .006, .007, .008, .009, .010, .011, .016, .017, .019, .020, .021 and the BC-1.07.004/.005 wire strings (`ensure_ascii` escaping included). Every vector size and result checked out except the one in C08.

### 1. Findings

| ID | Sev | Category | File:line (BC / legacy) | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P6-C01 | HIGH | contradiction / partial-fix regression | BC-1.03.018:106 (Inv3), :36; BC-1.03.010:47-48 (Pre2), :97 (EC-008); ARCH-03-statusline.md:66; legacy SL:983-985 | BC-5.04.001:66-74 (v1.2.3, ADV-P5-D01, owner call 8) now says: on Windows, a naive transcript timestamp on or before 1970-01-01, or from year 3001, raises `OSError`; `_iso_ts` catches only `ValueError`, so the whole line **degrades**, and hylo reproduces this. That change never reached its dependents. BC-1.03.018 Inv3 still says the line "never degrades on any transcript line content" and its description still counts "ten transcript crash paths". BC-1.03.010 Pre2 says an unparsable timestamp "gives null", and its EC-008 does not mention Windows. ARCH-03 step 2 also omits it. A Windows test derived from either BC would assert the wrong outcome. | product-owner (architect for ARCH-03) |
| ADV-P6-C02 | HIGH | config range drift (P20, partial-fix regression) | BC-1.03.003:45-49; BC-1.03.005:47-51; interface-definitions.md:198-199; BC-2.01.004:196-203 | Call 16 bounded `read_cap_bytes` to `1..67108864` and `dedup_memory` to `1..65536`, with a labeled judgment rationale. Both BCs still state the open range `>= 1` and give no reason for an upper bound. Sibling BCs from the same call (BC-1.04.003, BC-1.05.002) were updated; these two were not. A value of 100,000,000 is valid under the BC but a config error under the registry. | product-owner |
| ADV-P6-C03 | MEDIUM | unspecified quirk / testability | BC-1.03.010:62-65; BC-1.03.017:35-36; SL:1074 (`cur.get("id") == mid_`) vs SL:1099 (`mid in seen_ids`) | Turn identity uses Python `==`, which has no identity shortcut. Dedup uses set membership, which does short-circuit on identity (BC-1.03.005 PC5(a)). With a decoded `NaN` id, dedup treats repeated lines as one message, but `NaN == NaN` is False, so every line of that id opens a new turn. Example: U0, then A(NaN, out 300, ts 2), then A(NaN, out 900, ts 10), no closer. Legacy writes `lr [150.0,false]` and `cur {.., t1 10, out 900}`. A Go port that reuses the dedup key for turn identity writes `lr null` and `out 300`. BC-1.03.010 should pin `==` semantics for `cur.id` and add a NaN-id vector. | product-owner |
| ADV-P6-C04 | MEDIUM | ambiguity | BC-1.07.004:57-58 (PC4); SL:924 | "The `id` is echoed verbatim" reads as a byte-for-byte copy. Legacy actually decodes the id and re-serializes it with `json.dumps`: `1.50` becomes `1.5`, `1E2` becomes `100.0`, `"\u0041"` becomes `"A"`, duplicate object keys collapse. A test written from PC4 would assert raw-token echo. Reword to "the decoded value re-serialized by `pyfmt` Dumps" and add a float-id vector. | product-owner |
| ADV-P6-C05 | LOW | spec drift (wording) | BC-1.07.004:55-56 (PC3) | "ASCII text and SGR sequences pass through unescaped" is wrong in three ways. ESC inside SGR is escaped as `\u001b` (stated earlier in the same sentence). `"` and `\` are escaped. ASCII control characters are escaped (`\n`, `\u0007`). A name containing a quote would get wrong golden bytes. | product-owner |
| ADV-P6-C06 | LOW | anchoring consistency (pending intent verification) | BC-1.03.006:120-123, BC-1.03.007:110-113, BC-1.03.010:116-121 (VP tables); BC-1.03.015:102 | BC-1.03.015 cites VP-012 (exclusion closure) for its OD-161 leg. BC-1.03.006, .007 and .010 own the D4-EX-2 vectors for CP-O06..O08 (BC-1.03.018:121-123) but cite only VP-029, and none of them appears in the `bcs:` of VP-012 or VP-013. | product-owner |
| ADV-P6-C07 | LOW | stale count (prose propagation) | BC-1.07.008:122; error-taxonomy.md:224-226 | BC-1.07.008 says "count fixed at 45 total". The error taxonomy register now counts 47 (4+17+7+3+11+5). | product-owner |
| ADV-P6-C08 | LOW | test vector inconsistency | BC-1.03.014:78, 87-88 | The stated line template uses `json.dumps` spacing (`{"type": "assistant", "message": {"content": <list>}}`). The pinned sizes 70 and 81 only work for fully compact serialization; the spaced template gives 77 and 88 bytes (74/85 if only the list is compact). The template needs to say "compact separators". | product-owner |
| ADV-P6-C09 | LOW | implementer guidance contradiction | BC-1.03.013:52 (PC2) vs :62 (Inv3) | PC2: a lone surrogate (WTF-8) is one code point and becomes one `_`. Inv3: "Go must iterate runes". Go's `range` over a WTF-8 surrogate (`ED A0 80`) yields three `RuneError`s, which would give `___`. Inv3 should point to `pyfmt.SubNonWord` over Value code points (BC-5.03.003), not plain rune iteration. | product-owner |
| ADV-P6-C10 | LOW | oracle definition | BC-1.03.018:86-87 (PC4(a)); BC-1.03.004:48 | The delete-the-line oracle adds "each + 1 for its LF". BC-1.03.004 also splits on bare `\r` and `\r\n`, so a skipped line ending in CRLF adds 2 bytes, not 1. The expected `size` would be wrong for CR/CRLF-separated W-lines. | product-owner |
| ADV-P6-C11 | LOW | precondition too weak | BC-1.03.012:42-43 vs :50 (PC2) | Pre1 only requires `len(S)+len(G) > step`. PC2 asserts refresh 2's first step "lies inside G with no LF" and so triggers extension reads. That only holds when `len(G) > step`. With `len(G) ≤ step`, no extension happens (the outcome is the same, but PC2 and the VP row's extension claim do not hold). | product-owner |
| ADV-P6-C12 | LOW | template conformance | BC-1.07.001..008 frontmatter (e.g. BC-1.07.001:14-20) | All eight BC-1.07 files lack the `priority:` field that BC-1.03.* and BC-1.06.* carry. The PRD lists them as P0 (prd.md:278-285). `introduced: v0.2.2` also differs from the sibling format `"0.1"`. | product-owner |
| ADV-P6-C13 | LOW | unclassified foreign-cache shapes (pending intent verification) | BC-1.03.002:86 (EC-007); BC-1.03.005:62; SL:1019, 1033-1034, 1043 | EC-007 says any non-number cached `size` falls in the crash class. But JSON `true` is a number in Python: `seek(True)` works, so there is no crash. Separately, BC-1.03.005 PC5 says "duplicates cannot occur" in `ids`, but a foreign cached `ids` with duplicates, or a string (which `list()` splits into characters), is carried as is. Neither shape is tied to an OD-160 classification. | product-owner |
| ADV-P6-C14 | COSMETIC | wording | BC-1.07.005:85 (EC-006) | "rendered verbatim on the wire inside ensure-ASCII JSON" contradicts BC-1.07.004 PC3, which says non-ASCII is escaped as `\uXXXX`. | product-owner |
| ADV-P6-C15 | LOW | cross-platform assumption (pending intent verification) | BC-1.06.001:63 (PC1); SL:192 | PC1 says the cache is read "as UTF-8 text". Legacy `open(path)` uses the locale encoding (cp1252 on Windows outside UTF-8 mode). This only matters for foreign, non-ASCII caches, since legacy writes ASCII via `ensure_ascii`. The UTF-8 mode assumption is not stated, unlike BC-1.01.008 for stdio. | product-owner |
| ADV-P6-C16 | LOW | parity-class label (pending intent verification) | BC-1.06.001:26 vs :74-79, :109 | BC-1.06.001 carries the OD-163 own-temp cleanup divergence (OD-110 temp-file class, DI-012 cited) but is labeled `byte-exact`. Sibling BC-1.06.002 is labeled `temp-file`. | product-owner |
| ADV-P6-C17 | COSMETIC | incomplete informational column | BC-1.03.018:81 (CP-T07 row) | The "legacy mutations before the raise" column lists only the timed-assistant case. It omits that a timed user or system line with an unhashable id still closes the turn and advances `lu` before SL:1099 raises. hylo applies none of these mutations, so behavior is unaffected. | product-owner |

### 2. Policy compliance
- **P1 append_only_numbering:** PASS.
- **P2 lift_invariants_to_bcs:** PASS. DI-007, DI-008 and DI-012 are cited throughout.
- **P4 semantic_anchoring_integrity:** PASS, minor issue ADV-P6-C06. All ARCH-03 and ARCH-04 fragment anchors resolve.
- **P5 creators_justify_anchors:** PASS.
- **P6 subsystem name:** PASS. All files carry `SS-01` per the ARCH-INDEX rule.
- **P7 BC H1 = BC-INDEX = PRD:** PASS. All 31 titles match.
- **P12 settled_decisions_are_constraints:** PASS. ADV-P6-C01 asks for propagation of owner call 8, not a change to it.
- **P13 parity_before_behavior_change:** PASS.
- **P14 public_repo_hygiene:** PASS. Fixtures are synthetic.
- **P16 thresholds_are_explained:** FINDING ADV-P6-C02 (the call-16 upper-bound rationale is missing in the BCs).
- **P17 ledger_format_frozen:** N.A. (no ledger in this perimeter).
- **P18 cross_platform_from_day_one:** FINDING ADV-P6-C01, ADV-P6-C15.
- **P19 go_hardening_toolchain:** N.A.
- **P20 config_over_code:** FINDING ADV-P6-C02. All other keys are registered with ranges that match, including the subagent glyph, color, joiner, tokens, lane, theme and pill keys.
- **P21 public_artifact_hygiene:** PASS.

### 3. Not fully read, and Python claims not verified
- **Not fully read:**
  - The brownfield tails of BC-1.03.012 through .017.
  - capabilities.md and test-vectors.md.
  - The VP bodies (I read only their `bcs:` lines and titles, plus VP-002 and VP-005 for the subagent legs).
  - The ARCH-04 bodies.
- **Python claims I could not verify:** I re-derived these from CPython semantics rather than running them:
  - `seek(negative)` raising `OSError`.
  - The depth boundaries 993/994 and 991.
  - The shared `NaN` object identity across `json.load` calls (reasoned from `_CONSTANTS`).
  - The A-template lengths in the BC-1.03.006/.007 turn-drop legs (163 B, `conv` 5); I could not reconstruct those exactly from the stated template.
  - All Windows behavior: MSVC `localtime_s`, the cp1252 locale, and the `a/../b` normalization.

### 4. Novelty
Novelty is **MEDIUM**. ADV-P6-C01 and C02 come from fixes made in pass 5 that did not reach the dependent BCs. ADV-P6-C03 is a new parity quirk no earlier pass caught. The rest are refinements.

**NOT_CONVERGED**

Key files:
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.018.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.010.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.04.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.005.md
- .factory/specs/prd-supplements/interface-definitions.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.004.md
- .factory/specs/architecture/ARCH-03-statusline.md


## Perimeter C2 (BC-1.04/1.05)

Findings: 15 (high 4, medium 6, low 4, cosmetic 1).

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P6-C2-01 | HIGH | wrong canonical vector | BC-1.05.002:111; legacy SL:624 | The vector "api_ms +inf, th_rate (0.0, 0.0)" expects yellow `\e[33m`. Legacy tests red first: `RED if r >= th_rate[1]`. With r = 0.0 and p95 = 0.0, `0.0 >= 0.0` is true, so the output is red `\e[31m $0.0/h\e[0m`. A test written from this row fails against the oracle. EC-005's "(or red when also >= p95)" is already correct, so only the vector needs to change. | product-owner |
| ADV-P6-C2-02 | HIGH | wrong normative rule | BC-1.04.001:67-69, 106; ARCH-03-statusline.md:183 | The spec says an empty `Location` redirects "to the original URL". CPython does `urljoin(req.full_url, "")`, where `req` is the request that received this 3xx, not the first one. From the second hop on, the target is the current hop's URL B, not A. The normative Go rule ("present-but-empty value = the original URL") gives a different loop key and a different next GET, so the Tier C differential would diverge. | product-owner + architect |
| ADV-P6-C2-03 | HIGH | contradiction (architecture vs BC) | ARCH-03-statusline.md:187 vs BC-1.04.001:93-99 | ARCH-03 says "The hop budget is the pinned 37-hop cap". BC-1.04.001 says the cap "is NOT a hop counter": urllib refuses a chain of distinct targets at its 11th redirect, and 37 is only the worst case. An implementer reading ARCH-03 would follow redirects 11..37 that urllib refuses (sample vs no sample). | architect |
| ADV-P6-C2-04 | HIGH | VP skeleton contradicts the BC | VP-020:104-121 vs BC-1.05.004 PC1 and Inv 2 | `TestCostHistory_OD166_RecordGuard` (the test that covers exclusion OD-166) puts the huge int into the **cost history** and asserts the file is unchanged. Per BC-1.05.004 the guard checks the stdin `usd`/`api_ms`. The write happens before `cost_thresholds` (SL:606-607), so a seeded history with a giant value means the file **is** rewritten, then the refresh degrades at SL:255. That is the OD-160 foreign-history class (BC-1.05.005 EC-011). A huge seeded `usd` whose `api_ms` misses the gate does not degrade at all. As written, the test fails a correct implementation and can pass a wrong one. | architect |
| ADV-P6-C2-05 | MEDIUM | divergence not in the spec (Go header handling) | BC-1.04.001:64-72, 106-108 | CPython keeps trailing whitespace in header values (email compat32 strips only CR/LF), so `Location: /x␠` becomes `/x%20` after quote. Go's textproto trims header values, so Go gets `/x`. Separately, Go `url.Parse` rejects a `%` not followed by two hex digits, which urllib passes through because `%` is in the safe set. Either way Go follows a different target or none. VP-030 Tier C varies header values, so this is reachable. The BC requires byte-exact targets but gives no way to get them through net/http. | architect |
| ADV-P6-C2-06 | MEDIUM | unpinned parity constant | BC-1.04.001 PC3 → BC-5.02.003 PC7 | The JSON nesting-depth limit `L` must be measured per call site ("never inferred from another site"). Only the three stdin-adjacent sites (F = 6, L = 993) are pinned. The fetch path (`<module>→main→get_sample→fetch_sample→loads→decode→raw_decode`) has F = 7, which predicts L = 992, but it is unmeasured and missing from BC-1.04.001. Tier C body fuzzing would hit it. Also, BC-5.02.003 Precondition 1 (one line, no `\n`/`\r`) does not cover a multi-line metrics body. | product-owner |
| ADV-P6-C2-07 | MEDIUM | deviation without an exclusion id [owner-question] | BC-1.04.001:74-78; ARCH-03:186 | It says "legacy's default-handler attempt fails" for an `ftp:` redirect target. urllib's FTPHandler can actually fetch a JSON file and produce a sample. The hylo rule (no sample) rests on "pass-5 call 14", which does not appear in the OD log, and it is not one of the 11 closed exclusions (DI-012). Either rule it out of scope or add an exclusion id. | product-owner |
| ADV-P6-C2-08 | MEDIUM | spec gap, cross-platform (P18) | BC-1.04.001 (no TLS clause); BC-2.02.005 allows https | Nothing says whether an https metrics URL (or an http→https redirect) verifies certificates, or against which root store. CPython 3.11 uses OpenSSL's store; Go on macOS and Windows uses the OS store. A certificate trusted only by the OS gives Go a sample and legacy none. No test can be derived from the spec. | architect |
| ADV-P6-C2-09 | MEDIUM | partial fix (S-7.01) | BC-1.04.002:25 vs :74 | The v1.3.3 changelog says "KeyError site added to Invariant 1 alongside the IndexError site". Invariant 1 still names only IndexError (BC-1.04.003 EC-009) and omits the `hist[-1]["t"]` KeyError (BC-1.04.003 EC-008, SL:337). | product-owner |
| ADV-P6-C2-10 | MEDIUM | P2 invariant lift | BC-1.05.007:129; BC-1.05.002:126 | Both carry the CP-O10/CP-O11 degrade (29-byte line, exit 0) and cite VP-001, but their L2 invariants list "—" / DI-007 only. DI-008 (never blank) is missing. | product-owner |
| ADV-P6-C2-11 | LOW | incomplete normalization rule | BC-1.04.001:80-82 | The rule says empty query and empty params are dropped by `urlunparse`. An empty fragment is dropped too (`urlunsplit` adds `#` only when the fragment is non-empty), so `/x#` and `/x` are one key. Not stated. | product-owner |
| ADV-P6-C2-12 | LOW | ambiguity | BC-1.04.001:54-56 | "hylo sends what urllib sends" does not say whether Go must also send `User-Agent: Python-urllib/3.11` and `Connection: close`, or only `Accept-Encoding: identity`. | product-owner |
| ADV-P6-C2-13 | LOW | taxonomy cross-reference | error-taxonomy.md:45, :135 | E-REN-002 lists CP-N03 but not the BCs that carry it (BC-1.04.001 EC-013, BC-1.04.005 EC-007). The CP-O10 history row says the raise can come from "the percentile math". In Python, int-to-float comparisons and `sorted` never overflow, so only the SL:255 division raises. | product-owner |
| ADV-P6-C2-14 | LOW | P1 numbering | BC-1.04.013:79 | `EC-006b` is an inserted id; append-only numbering calls for EC-010. | product-owner |
| ADV-P6-C2-15 | COSMETIC | metadata drift | BC-1.04.002:7 vs :26; BC-1.04.020:21 and BC-1.04.021:21 vs BC-1.04.001:21 | The frontmatter `timestamp` is older than the last modified entry. The same ADV-P4-D22 sweep is dated 2026-11-17 in .020/.021 but redated to 2026-11-18 in .001/.002. BC-1.05.002 lists EC-009 between EC-005 and EC-006. | product-owner |

## 2. Policy compliance
- P1: FINDING ADV-P6-C2-14
- P2: FINDING ADV-P6-C2-10
- P4: FINDING ADV-P6-C2-03 (ARCH-03 describes the cap wrongly)
- P5: PASS
- P6: PASS (all 30 BCs are SS-01, which matches the ARCH-INDEX row "SS-01 Status Line")
- P7: PASS (H1 = BC-INDEX = PRD title for all 30)
- P12: FINDING ADV-P6-C2-07 [owner-question]
- P13: FINDINGS ADV-P6-C2-02, -05, -06, -07
- P14: PASS (only RFC 5737 addresses)
- P16: PASS
- P17: N.A. (no ledger in this perimeter)
- P18: FINDING ADV-P6-C2-08
- P19: N.A.
- P20: PASS (redirect caps 4/10 and the 3.6e6 factor are named protocol/unit constants with reasons)
- P21: PASS

## 3. Not fully read, and claims I could not check
- **Read only in part:**
  - Brownfield tail sections of BC-1.04.005–.012, .014–.019 and BC-1.05.006/.008.
  - ARCH-03, lines 150–229 only.
  - The PRD and interface-definitions.md, via grep only.
- **Not read:** ARCH-04-data-files.md, capabilities.md, invariants.md (grep only), VP-001/012/019/021/022/031.
- **Not run:** I could not execute anything, so every Python result in this review was worked out by hand. That covers the vectors and fades, the overflow boundary, and the percentile indices; all matched except -01.
- **From memory of the CPython 3.11.7 and Go sources, not opened:**
  - compat32 keeping trailing whitespace in header values (-05)
  - Go textproto `trim` (-05)
  - FTPHandler being able to fetch JSON (-07)
  - the F = 7 frame count (-06)
- **Not re-derived:** the NaN sort placement in BC-1.05.005 EC-009.

## 4. Novelty
HIGH: four HIGH findings are new. They are a wrong canonical vector, a wrong normative redirect rule, an ARCH-03 contradiction with BC-1.04.001, and a VP-020 test skeleton that contradicts BC-1.05.004. Several MEDIUM findings open new Go-vs-CPython divergence areas.

NOT_CONVERGED


## Perimeter D (S2-S6 BCs)

Findings: 27 (high 6, medium 11, low 8, cosmetic 2).

## Adversarial review, Phase 1d pass 6, Perimeter D (SS-02..SS-06)

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P6-D01 | HIGH | contradiction / test unwritable | BC-2.01.005:91, :129-141, EC-010/011 :162-163; interface-definitions.md:197 | PC-5 makes `statusline.theme.heat` a FloatTriple whose env grammar is strict JSON. PC-7 says a non-default value "runs the key's own grammar first". So EC-011 `0.5/0.5/0.5` should fail as a shape error (`expected JSON array of 3 numbers`, Text class), not as `out of range`. The default's "env spelling" `0.22/0.85/0.80` is not JSON, and no row says whether `[0.22,0.85,0.80]` is accepted. | product-owner |
| ADV-P6-D02 | HIGH | default fails its own validation (Unicode 14 width) | BC-2.01.004:136 (watts `⚡` U+26A1), PC-6 last sentence :151-152, PC-3(c) :100; BC-2.01.005 PC-6 :119-122 | U+26A1 has East-Asian-Width W, so the PC-9 width function gives it 2 columns. The legacy default glyph (SL:813) therefore fails "exactly 1 code point and 1 display column", the build-time default test fails, and the legacy default can never be set. It is the only W member in the glyph table. | product-owner [owner-question] (OD-02 vs legacy default) |
| ADV-P6-D03 | HIGH | contradiction | BC-2.01.004:141 vs :151-152; BC-2.01.005:119-122 | The `statusline.glyphs.sparkline` row is explicitly 8 code points. But PC-6's closing sentence and BC-2.01.005 PC-6 apply the 1-code-point rule to every `statusline.glyphs.*` member, with no carve-out. Result: the default fails PC-3(c), and any override is rejected. | product-owner |
| ADV-P6-D04 | HIGH | partial-fix regression (blast radius 5) | BC-2.01.002:135 ("closed six-class register (no seventh class)"); BC-2.01.005:183, :214; ARCH-02:59, :138, :142; VP-016:91 | OD-178 closed the register at SEVEN classes (BC-2.02.001:123-134, BC-2.02.006:46, PRD:498, error-taxonomy:33). These sites still say six, and BC-2.01.002 explicitly denies a seventh. | product-owner + architect |
| ADV-P6-D05 | HIGH | cross-BC contradiction (parity infeasible) | BC-6.02.003 PC-8 :154-162; BC-6.01.002 PC-1 :70-74 vs BC-3.02.002 Pre-3 :45-51, CTV :98-107 | The P1 corpus validator rejects any non-UTC `tz`. But the OD-76 difference table runs as parity cases under `TZ=America/Chicago`. D1, the repeated DST hour, cannot exist in UTC, and the I1/I2 identical-row epochs are Chicago values. So the `OD-76` closed-set entry cannot have a valid D1 case. | architect |
| ADV-P6-D06 | HIGH | cross-platform / signature gap (P18) | BC-5.04.001 PC-6 :66-74; ARCH-06:184-185 | The Windows MSVC `localtime_s` failure must make the line degrade (OSError is not caught at SL:984). But `FromISOFormat` returns `(float64, bool)` and `LocalToUnix` returns only `ErrValue`, which maps to None. No signature can carry a third outcome. Also, "the rule lives in internal/platform" while both helpers sit in pure-core pyfmt with no injected seam, so no failing test can be written against the canon. | architect |
| ADV-P6-D07 | MEDIUM | test vector mislabeled (re-raises rejected ADV-P5-D16) | BC-5.02.002:126 (generator literal) vs :80 row 51 cell; BC-5.02.001 EC-003 :114 | The Python literal `'{"t":"\\\\/\\""}'` evaluates to source text with TWO backslashes before `/`. A JSON scanner reads that as an escaped backslash followed by a plain `/`, so the `\/` escape is never exercised. The value `\/"` contains backslash-slash as characters, not as an escape. The table cell shows three backslashes. The length (14) is unchanged, but the "\/ decodes to /" path is untested, and a regenerated table will not match the BC cell. | product-owner |
| ADV-P6-D08 | MEDIUM | missing per-site budget | BC-5.02.006 PC-6 table :86-95; Description :44-45 | `Dumps` takes a mandatory budget, and the description puts the subagent `json.dumps` (SL:924) in scope, but the table has no SL:924 row. That site echoes `task["id"]` verbatim (any JSON value, BC-1.07.004 PC-4). From stdin, `id` can reach depth 990, so `{"id": X}` reaches 991, which is exactly the boundary at s=3 (`<module>`→`main_subagent`→`render_subagent_rows`). The budget is input-reachable and unpinned. | product-owner |
| ADV-P6-D09 | MEDIUM | internal contradiction | BC-5.01.007 PC-3 :85-93, PC-4 :102-109; ARCH-06:147 | `NumCmp` is declared "defined only for ordered operands", yet PC-4 defines `Max`/`Min` through `NumCmp`'s NaN verdict (0). `MaxSeq` "folds NumCmp" (Related BCs). The `error` return of `NumCmp(a, b) (int, error)` is never specified. If it errors on NaN, `Max(0, NaN)` breaks. | product-owner |
| ADV-P6-D10 | MEDIUM | partial-fix regression | BC-5.04.001 Pre-2 :48-50 | Still says "named zone → OS-zone fallback". OD-177 / ADV-P5-D23 (BC-3.01.001 PC-6(b)) changed empty or unparseable `TZ` to UTC. | product-owner |
| ADV-P6-D11 | MEDIUM | partial-fix regression | BC-6.01.003 CTV row 1 :152 vs PC-4 :111-116 | PC-4 was strengthened to `HYLO_TEST_NOW=1794615009.4245193` with exact stdout. The canonical vector still pins the superseded `1794615009.5` value, which cannot discriminate the round trip. | product-owner |
| ADV-P6-D12 | MEDIUM | partial-fix regression | BC-2.02.001 PC-6 :84-85 vs BC-2.01.002 PC-4 :77-80 | The `[from …]` tie-break still says "registry field order". ADV-P5-D31 redefined it as the lexicographically smallest FIELD name, because non-P1 fields have no registry order. | product-owner |
| ADV-P6-D13 | MEDIUM | partial-fix regression | BC-2.02.001 Refactoring Notes :257 vs BC-2.01.001 PC-6 :86-93 | "`config.Load` takes the environment as a map (seam)" contradicts ADV-P5-D25: Load receives the environment only through `platform.Environ`, never a raw Go map. | product-owner |
| ADV-P6-D14 | MEDIUM | contradiction | BC-2.02.001:123-134; BC-6.03.004 table row D4-EX-3 :93 | (1) BC-2.02.001 says all seven classes have dedicated class contracts and D4-EX-3 table tests, but theme has no `TestD4EX3_*` member and Text has no BC-2.02.00x class contract. (2) BC-6.03.004 drops Theme because the corpus validator rejects keys with no legacy equivalent. Text keys (glyphs, labels, suffix) also have no legacy equivalent, so by the same logic no `TestD4EX3_Text` exclusion entry can exist. | product-owner |
| ADV-P6-D15 | MEDIUM | ambiguity | BC-2.01.001 PC-6 :79-80 vs BC-2.01.002 PC-4 :68-84; BC-2.03.001 EC-005 :82 | `HYLO_BACKENDS_1_METRICS_URL` names no registry key and is not reserved, so PC-6 read literally requires an unknown-setting warning. BC-2.01.002 warns only for non-P1 fields, and EC-005 shows only the error line. Expected stderr is undefined. | product-owner |
| ADV-P6-D16 | MEDIUM | oracle drift [owner-question] | BC-6.01.001 PC-3 :72; BC-6.04.001 PC-3.3 :71-72, EC-003 | The version gate accepts any `3.11.[0-9]+`, and setup-python "3.11" floats to the latest patch. The measured depth constants (993/994, 991/990), the generated Unicode tables (BC-5.01.002 Pre-3) and OD-170 all pin 3.11.7, and the staleness regeneration runs under whatever CI resolves. Nothing pins 3.11.7. | architect |
| ADV-P6-D17 | MEDIUM | architecture grounding error (cross-check) | ARCH-06:221-223 | "a label such as `中文` measures 2" under the validation width. Both characters are EAW W, so the BC-2.01.004 PC-9 rule gives 4. The grounding contradicts its own rule. | architect |
| ADV-P6-D18 | LOW | factual error in rationale | BC-5.01.007 PC-2 :73-74, EC-005 :134 | "`10**310 / 3` raises even though both operands convert individually" is false: 10^310 exceeds DBL_MAX ≈ 1.8e308. For int/int with \|b\| ≥ 1, quotient overflow with both operands convertible is impossible. The expected `ErrOverflow` is right; the explanation is wrong. | product-owner |
| ADV-P6-D19 | LOW | ambiguity | BC-2.02.005 PC-4 :60 | "parsed host is empty" is undefined for `http://:8428`: Go's `u.Host` is `:8428` but `u.Hostname()` is empty. | product-owner |
| ADV-P6-D20 | LOW | internal tension | BC-2.03.002 PC-5 :97-98 vs PC-3 :79-85 | PC-5 says "HYLO_* settings are not validated", while PC-3 / EC-011 raise the `empty path` error with exit 1 for `HYLO_PATHS_CACHE_DIR=`. | product-owner |
| ADV-P6-D21 | LOW | spec accuracy | BC-3.01.001 PC-6 :69-80 | (1) The "libc semantics on every OS" claim is inaccurate: libc honors POSIX TZ strings that are not in the zone database, but (b) maps them to UTC. (2) Go `LoadLocation("Local")` special-cases `TZ=Local` to `time.Local`, which on Windows ignores TZ. (3) When `LocalZone` returns its `error` is never stated. | product-owner |
| ADV-P6-D22 | LOW | stale anchor (P4) | BC-5.03.004 Inv 3 :63-68, Source :111 | Still flags an "anchoring gap ... architect to pin the owning contract" for abspath/join/dirname. BC-1.02.004 PC-1 and EC-012 already own those per-flavor rules. | product-owner |
| ADV-P6-D23 | LOW | mis-anchor (P4) | BC-2.01.004 PC-9 :176 | Cites legacy SL:489 for the reroute-all markers. The tuple is at SL:487-488; SL:489 is the `rl = {} if reroute_all` line. | product-owner |
| ADV-P6-D24 | LOW | partial-fix regression | BC-6.03.004 EC-006 :183 | "both defaulting to `stdout+caches`" contradicts PC-2: scope is required with no default (ADV-P5-D20). | product-owner |
| ADV-P6-D25 | LOW | ambiguity | ARCH-06:166 | The `Dumps` comment reads as if both the 4,300-digit limit and the depth breach give `ErrDepth`. BC-5.02.006 PC-5 assigns `ErrValue` to the former. | architect |
| ADV-P6-D26 | COSMETIC | numbering | BC-3.01.001 EC table :104-106 | EC-011 and EC-012 are listed before EC-010. | product-owner |
| ADV-P6-D27 | COSMETIC | consistency | BC-6.01.002 Description :48 vs PC-3 :114 | The description says GP-1..GP-6 can never leak. PC-3 forbids GP-1..GP-4; GP-6 is undefined here. | product-owner |

### 2. Policy compliance
- P1 append_only_numbering: PASS. IDs are not renumbered; only out of order (D26).
- P2 lift_invariants_to_bcs: PASS. DI-008, DI-010 and DI-012 are cited throughout.
- P4 semantic_anchoring_integrity: FINDING D07, D22, D23.
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS. SS-02..SS-06 frontmatter is consistent.
- P7 H1 = BC-INDEX: PASS. All 53 H1s match BC-INDEX:203-320. PRD titles were not re-checked row by row.
- P12 settled_decisions: PASS, with one [owner-question] (D16; D02 pits OD-02 against the legacy default).
- P13 parity_before_behavior_change: FINDING D02, D05.
- P14 public_repo_hygiene: PASS. Only RFC 5737 addresses and synthetic paths appear.
- P16 thresholds_are_explained: PASS.
- P18 cross_platform: FINDING D05, D06, D21.
- P19 go_hardening: PASS. The sha1 `nolint` carries a reason.
- P20 config_over_code: PASS. The defects in D02/D03 are inside the config registry, not code literals.
- P21 public_artifact_hygiene: PASS. No flagged string is quoted.
- P3, P8–P11, P15, P17: N.A.

### 3. Not fully read; claims not verified
- Read only partially: the tails of BC-6.02.001, BC-6.02.002, BC-6.02.004, BC-6.03.002, BC-6.03.003, BC-6.04.001, BC-6.04.002 and BC-6.04.003 (the VP, traceability and anchor sections); BC-2.02.002, .003, .004 and .005 from their H1 onward only. Not opened: BC-ALLOCATION.md, prd-supplements beyond the greps, ARCH-01/03/05/07/08, VP files other than the VP-016 grep, capabilities.md, invariants.md.
- Not verified because there is no interpreter (read-only):
  - BC-5.01.001 EC-006 `round(1.00005, 4)`.
  - The BC-6.01.003 claim that `1794615009.4245193` becomes `…4245195` under the round trip.
  - The golden A/B/C byte totals and widths.
  - BC-5.02.006's s=3 frame count at SL:924 (inferred from SL:1238-1241 and SL:928-935).
  - Whether `str()` of a depth-990 stdin value at SL:453/896 stays under the repr recursion limit; BC-5.02.005 has no depth leg.
  - The East-Asian-Width class of U+26A1 (W) comes from the published EastAsianWidth table, not a generated check.

### 4. Novelty
Novelty is MEDIUM. D01–D03, D05–D09 and D17 are new substantive defects. The rest are propagation gaps left by the pass-5 fixes.

**NOT_CONVERGED**

