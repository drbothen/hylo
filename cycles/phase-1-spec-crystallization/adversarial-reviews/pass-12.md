---
document_type: adversarial-review
phase: 1d
pass: 12
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 73
---

# Adversarial Spec Review — Phase 1d, Pass 12

Pass 12 ran as six fresh-context perimeters, the same split as passes 1-11. Each section is the verbatim final report of one perimeter, unedited except for this framing. NOT_CONVERGED (73 findings: HIGH 13 / MEDIUM 26 / LOW 28 / COSMETIC 6; pass 11 had 62 with 11 HIGH). The orchestrator spot-verified A08 (BC-6.04.002 requires the CPython oracle median; TestParityTierC_DiffFuzz drives both sides; neither is in ORACLE_TESTS), A03/D05 (prd.md BC-6.04.001 row lacks "floor") and A07 (BC-6.04.002 per case, never pooled across steps) on disk, and measured on CPython 3.11.7: C2-01 (max of a negative giant int and 0.0 returns 0.0), C2-03 (Request selector for a URL with two fragments splits at the last '#') and C02 (a 5,000-digit int literal raises ValueError on the 4,300-digit limit); all held.

## Perimeter A (PRD, supplements, architecture, CI)

Findings: 12 (high 6, medium 3, low 2, cosmetic 1).

## Adversarial Review: Pass 12, Perimeter A (PRD, supplements, architecture, CI)

### 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner | Tags |
|---|---|---|---|---|---|---|
| ADV-P12-A01 | HIGH | Contradiction / semantic anchoring (P4) | prd.md:513; error-taxonomy.md:52 | The E-REN-002 "carrier list" is still missing owners that the same taxonomy names. error-taxonomy.md:311-315 assigns CP-S09 to BC-1.02.010/.013, CP-S12 to BC-1.02.015, CP-S13 to BC-1.02.016, CP-S14 to BC-1.03.013 and CP-S15 to BC-1.05.004. :176-177 assigns CP-O10/O11 to BC-1.05.005 and BC-1.05.002, and :241 assigns CP-A03 to BC-1.07.006. The CP-N01/N02 owners BC-1.04.015/.014 (their H1s name the CP ids) are also absent. Grep confirms all of these BCs cite their CP ids. Test authors working from E-REN-002 would leave about 11 degrade owners out of the never-blank fault-injection set. | product-owner | [process-gap]: 4th piecemeal "completion" (pass-7 A14/B11, pass-9 B03, pass-11 B07); derive the list from the register, don't hand-maintain it |
| ADV-P12-A02 | HIGH | CI-as-code / security (P11, P14) | ARCH-08:176-180, :225-234; cicd-setup.md:53, :85 | The required `gitleaks (full history)` check scans exactly `--log-opts="main factory-artifacts"` and asserts "scanned rev set EQUALS compared rev set". On a `pull_request` run the PR's own commits are reachable from neither ref, so a secret introduced in a PR passes the required check. It is caught only after merge, once already public on the PR. Second, MEDIUM-confidence issue: actions/checkout on a PR leaves `main` and `factory-artifacts` as `origin/*` refs only, not local branches, so the bare names may not resolve. The pass-11 A04 fix (from `--all` to two refs) introduced this; BC-6.04.001 PC-4 copies it. | architect | |
| ADV-P12-A03 | HIGH | BC title sync (P7) | prd.md:426 | The PRD row says "...; Go 1.26.0 leg; -race; gitleaks". The BC-6.04.001 H1 (ss-06/BC-6.04.001.md:43) and BC-INDEX.md:318 both say "Go 1.26.0 **floor** leg". The BC's 1.2.6 history entry claims the index titles were synced; the PRD was not. | product-owner | |
| ADV-P12-A04 | HIGH | Architecture cannot satisfy a BC | ARCH-08:50-63; cicd-setup.md:49-59, :303-311 | BC-6.04.001 PC-2 and its CTV require 4 test legs: 3 OS legs plus an ubuntu `go-version: 1.26.0` floor leg. VP-037 parses ci.yml expecting that leg. The floor leg appears only in ARCH-08 prose (:33). It is missing from the CI diagram, from the cicd-setup jobs table and from the branch-protection required list (3 test legs). Phase 3 would build, and require, a 3-leg matrix. | architect | |
| ADV-P12-A05 | MEDIUM | Partial-fix sibling drift | prd.md:499 vs nfr-catalog.md:27 | PRD NFR-004 was changed to "Go 1.26.0" (0.2.22, "aligned with the BC-6.04.001 floor pin"). The catalog's NFR-004, which the PRD defers to, still says "Go 1.26.x". Neither text says the matrix runs 1.26.x via the toolchain line while the floor leg runs 1.26.0. | product-owner | |
| ADV-P12-A06 | HIGH | Contradiction (architecture vs BC) | ARCH-08:54-57, :73-77; cicd-setup.md:52 | BC-6.04.001 PC-3 step 5 requires setup-python on each OS leg before any `go test`. PC-6 requires "each OS leg prints the resolved CPython patch". ARCH-08 and cicd-setup say the macOS/Windows test legs install no interpreter, and they move gofmt/vet/staticcheck into an ubuntu-only lint job (PC-3 lists those as per-leg steps). Story writers get two incompatible leg structures. | architect + product-owner | |
| ADV-P12-A07 | HIGH | NFR without an unambiguous measurement unit | nfr-catalog.md:24, :73-78; ARCH-08:157-163 | There are three different timed-run models. (1) nfr-catalog: "one full execution of the case's step sequence, wall-clocked end to end" (includes harness work between steps). (2) ARCH-08: a multi-step case "sums the per-invocation wall times". (3) BC-6.04.002 PC-1: per-execution process time, "never pooled across cases or steps". Both sequence models compare a multi-refresh total against the per-render p95 25 ms target, so any 3+ step case at roughly 8+ ms per render fails the binding owner-Mac gate by construction. | architect + product-owner | [owner-question] intended timing unit |
| ADV-P12-A08 | MEDIUM | CI-as-code (P11) | ARCH-07:198; ARCH-08:90-99, :153; cicd-setup.md:59 | ORACLE_TESTS claims "every test needing the resolved Python oracle is a member", but lists only TierA, Canary and CacheSwap. Two tests that need the oracle are missing. `TestParityTierC_DiffFuzz` drives both sides. `TestTiming` must report "the CPython oracle median" (BC-6.04.002 PC-2). Both run in the plain test step (`-skip $ORACLE_TESTS`) under `CI=true`, and the timing job installs no interpreter (it is absent from ARCH-08:74-76's Python-consumer list). So the oracle median either fails closed or is silently dropped. | architect | |
| ADV-P12-A09 | MEDIUM | Partial-fix sibling drift | nfr-catalog.md:26; assumptions-register.md:25 | The OD-185 self-check is listed as only "JSON depth boundaries and unicodedata.unidata_version". The NUL-keeps normpath probe added by pass-11 B08 (ARCH-07:65-69, ARCH-08:82-85, BC-6.01.001 PC-4 :100-110) did not propagate to these two siblings. | product-owner | |
| ADV-P12-A10 | LOW | Ambiguity | interface-definitions.md:44-48, :477; ARCH-01:64-66 | These lines say `--subagent` is selected "before any flag scan or config processing", yet the same path resolves config before evaluating the `statusline.subagent.enabled` gate (ARCH-01:71-73, OD-168). The text should say "before the unknown-flag scan and the MAIN config step". | architect | |
| ADV-P12-A11 | LOW | Misclassification / range | prd.md:500; nfr-catalog.md:28 | NFR-005 lists `window_age.max_depth`=6 among "protocol/stdlib constants... NOT render-state caps". It is actually a registered tunable key (interface-definitions.md:302, range "any Int"; ARCH-05:28). It is also the only tunable cap key with no validation upper bound, unlike its siblings read_cap_bytes, dedup_memory and history_cap. | product-owner | |
| ADV-P12-A12 | COSMETIC | Terminology drift | ARCH-00:102-104; risk-register.md:29; cicd-setup.md:166 | These still say "line coverage" / "line-coverage gate". PRD, nfr-catalog and module-criticality were renamed to Go statement coverage in pass 11 (A03). | architect | |

### 2. Policy compliance
- P1 append_only_numbering: PASS (CP-T08 is retired, not reused; CP-C06/C07 are reserved).
- P2 lift_invariants_to_bcs: PASS (nothing new in perimeter).
- P4 semantic_anchoring_integrity: FINDING A01.
- P5 creators_justify_anchors: PASS.
- P6 subsystem names: PASS (ARCH-INDEX registry matches the PRD §1.6 aliases).
- P7 BC H1 is the title source of truth: FINDING A03 (the other 125 sampled S1-S4/S6 H1s match the PRD rows).
- P9 VP-INDEX source of truth and arithmetic: PASS (41 = 20+13+3+2+1+1+1 = 33+7+1; ARCH-INDEX home mapping sums to 41; 8 second homes).
- P11 ci_positive_coverage_assertion: FINDINGS A02, A08.
- P12 settled_decisions_are_constraints: PASS (A07 is tagged [owner-question]).
- P13 parity_before_behavior_change: PASS.
- P14 public_repo_hygiene: FINDING A02 (the PR secret-scan gap).
- P16 thresholds_are_explained: PASS.
- P17 ledger_format_frozen_until_cutover: PASS.
- P18 cross_platform_from_day_one: FINDINGS A04, A06 (CI leg structure).
- P19 go_hardening_toolchain: PASS (toolchain-before-govulncheck sequencing is stated).
- P20 config_over_code: PASS (A11 is a classification issue only).
- P21 public_artifact_hygiene: PASS (no flagged strings quoted).
- P3, P8, P10, P15: N.A.

### 3. Files not fully read
None in the perimeter; every file was read in full (prd.md and interface-definitions.md in two parts each). Outside the perimeter, for cross-checks only: BC-6.04.001 and BC-6.04.002 (partial), the BC H1 grep, VP-INDEX, and legacy SL:70-139, 486-505, 872-931, 1180-1246.

### 4. Novelty
MEDIUM. A02, A04, A06, A07 and A08 are new structural defects in the CI and timing design. A01 is a recurring pattern escalated as a process gap. A03, A05 and A09 are incomplete propagation of pass-10/11 fixes.

**NOT_CONVERGED**

## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 19 (high 0, medium 9, low 9, cosmetic 1).

## ADV-P12 Perimeter A2: findings (L2 domain spec, VPs, assessments)

### 1. Findings

| ID | Sev | Category | File:line | Defect (evidence) | Owner |
|---|---|---|---|---|---|
| ADV-P12-A2-01 | MEDIUM | Count drift (P2) | domain-spec/invariants.md:31, :35, :46 | The counts are stale under the file's own method (`grep -rl` over `behavioral-contracts/ss-0*/`). DI-008 now matches 89 BC files, not 88. DI-012 matches 79, not 77. DI-007 = 38 still holds. Pass-11 citation additions did not propagate here. | business-analyst |
| ADV-P12-A2-02 | MEDIUM | Contradiction / mis-anchor | VP-019:43-45 vs VP-014:44-51; BC-3.02.001:105-113, EC-008 (:126) | VP-019 says that on Windows the D4-EX-1 native probe writes `proc_start` during swap legs, and that the step is compared against an exclusion entry's expected file. VP-014 says the probe is never exercised in parity. BC-3.02.001 Inv 4 says every corpus case seeds `proc_start`. EC-008 says no D4-EX-1 `exclusions.json` entry exists. VP-019's carve-out example therefore has no vehicle. | architect |
| ADV-P12-A2-03 | MEDIUM | Under-specified oracle | VP-012:84-93, sketch :214-226 | The rider-completeness leg checks one "canonical rider test" per closed id, with the register keyed id → one rider. But the BC-6.03.004 register (:100) maps D4-EX-3 to five tests, `TestD4EX3_{Number,Boolean,URL,Enum,Text}`, and OD-160 to several riders. As stated, deleting four of the five D4-EX-3 class tables need not fail the check. The statement should say the register is multi-valued and every listed test must exist. | architect |
| ADV-P12-A2-04 | MEDIUM | VP narrower than its primary BC | VP-011:38-41; BC-6.04.003:113-114, :131-132; VP-024:44-49 | VP-011 says Tier C compares only stdout bytes and exit codes. BC-6.04.003 PC3/Inv 1 require the full Tier A comparator, which includes named caches (BC-6.03.002). VP-024 sends the BC-1.05.009 cost-history `Dumps` differential to Tier C, but that leg's only observable is a cache file, which VP-011 says is never compared. | architect |
| ADV-P12-A2-05 | MEDIUM | Clause with no oracle | VP-007:39-41, :71-76 | The property claims no nondeterminism source "is read behind Render's back". The double-replay method cannot fail on a direct `time.Now`/`os.Getenv` call: same-second replays produce identical bytes, and recording fakes cannot see reads that bypass them. The cited "mirroring VP-022" lint (VP-022:96-103) covers only file opens and ledger names. Either add a lint leg for clock/env/exec calls or drop the clause. | architect |
| ADV-P12-A2-06 | MEDIUM | Under-defined membership oracle | VP-001:113-117; sketch :216 | The main-entry output set is "normal render bytes", which is defined only by the sketch-only `isRenderBytes`. The Method also says argv shapes are fuzzed, yet the set leaves out the unknown-flag and config-error lines. The main-entry membership check is therefore either vacuous or false-red. | architect |
| ADV-P12-A2-07 | MEDIUM | Untested normative clause | VP-034:55-66 vs :101-104, :112, :224-225 | The statement asserts an exact allowlisted key set for the Go-binary child too (`XDG_CACHE_HOME`, `LOCALAPPDATA`, `HYLO_PATHS_CACHE_DIR`, …). Method, Proof Method and Named Tests only cover the oracle child (`TestOracleEnv_FromScratch`). No test checks the Go child; `goAllowlist*` are declared and never asserted. | architect |
| ADV-P12-A2-08 | MEDIUM | P11 positive coverage | VP-006:99-100, :130, sketch :173-177 | The call-site AST lint loops over `DecodeCallSites()` with no non-zero or table-equality assertion. A mis-pathed AST scan finds zero sites and passes green. The statement should require a computed site count equal to the ten-row site table. | architect |
| ADV-P12-A2-09 | MEDIUM | L2 phase vs P1 scope | domain-spec/bounded-contexts.md:35 | BC10 "Trust & Platform" lists "per-OS platform services" as P4 only. Those services ship in P1: ARCH-INDEX SS-03 is P1, and BC-3.01.001/3.02.001/3.02.002 are P1 contracts. BC1 (:26) carries a "(config registry P1)" carve-out; BC10 has none. | business-analyst |
| ADV-P12-A2-10 | LOW | Brief vs BC wording | product-brief.md:89-90 vs BC-6.04.002:102-106, VP-036:48-49 | The brief exempts "the >512 KB-line fixture". The validator only requires the transcript to exceed 524,288 bytes; a large transcript made of short lines also qualifies. | product-owner |
| ADV-P12-A2-11 | LOW | Stale label | VP-036:60-61 | The Source Contract quotes the pre-1.2.5 BC-6.04.002 title, without the "(large-transcript exemption: 100 ms ceiling)" suffix now in BC-INDEX:319. | architect |
| ADV-P12-A2-12 | LOW | Title vs statement (pending intent) | VP-039:33, VP-INDEX:116 vs VP-039:44-46 | The title says "agree at ulp level", which reads as a tolerance claim. The statement says "not a tolerance claim … bit-exactly". | architect |
| ADV-P12-A2-13 | LOW | Stale assessment pin (pending intent) | architecture-feasibility-report.md:13, :21 | `prd_version: "0.1"` while prd.md:4 is 0.2.22, and "OD-115..OD-149 settled" predates OD-150..OD-194, even though the body was amended through pass 9. Either re-pin or label as a review-time snapshot. | architect |
| ADV-P12-A2-14 | LOW | Wrong attribution | VP-005:56-58 | It says "the guard emits the degraded line with lone surrogates encoded". The degraded line is constant ASCII; surrogate encoding (BC-1.01.008) applies to rendered rows. | architect |
| ADV-P12-A2-15 | LOW | Registry discipline (P20) | VP-031:50-51, :149-150 | The fourth cap key `statusline.sparkline.max_age_s` lacks the type/range the other three caps carry. "The registry set is exactly these four caps" reads as the whole registry. | architect |
| ADV-P12-A2-16 | LOW | Ambiguous oracle | VP-013:56-58 vs VP-029:66-68 | "the oracle run on the transcript with the W-line deleted" could mean CPython or the Go parser. VP-029 and the sketch use the Go parser (metamorphic). Say which. | architect |
| ADV-P12-A2-17 | LOW | Tautological norm | VP-016:50-51 | "stdout is either the config-error line … or not" can never fail. The operative rule is: if the config-error line is printed, it is exactly one LF-terminated line. | architect |
| ADV-P12-A2-18 | LOW [owner-question] | Public-artifact hygiene (P21) | VP-035:105 | The spec text itself contains a literal email-shaped canary (reserved example domain), not just the test. Confirm the hygiene allowlist covers it, or build the canary at runtime. | product-owner |
| ADV-P12-A2-19 | COSMETIC | Sketch only | VP-021:131-137; VP-020:158 | VP-021: a float is assigned to a `[]float64` quick parameter. VP-020: `recordThrottleMS` vs `record_throttle_s`. | architect |

**Checked and correct:**
- VP-INDEX against all 41 VP files: titles, classes, methods, `bcs:`. The coverage map recomputes to 285 edges and 154/154 BCs.
- The VP-006 frame-count law against the legacy call chains.
- These figures against legacy: 18 metric series, 16 mix-cache keys, the caps 256/32/524288/90, and the 29-byte degraded line.
- The 73 byte-exact BCs cited in VP-009.
- The S1 BC count (101) in the feasibility report.

### 2. Policy compliance
- P1 append_only_numbering: PASS (VP-001..041, DI/CAP/ENT IDs contiguous).
- P2 lift_invariants_to_bcs: FINDING A2-01.
- P4 semantic_anchoring_integrity: FINDING A2-02, A2-04, A2-09, A2-11.
- P5 creators_justify_anchors: PASS.
- P6 subsystem names: PASS (matches the ARCH-INDEX registry).
- P9 vp_index_is_vp_catalog_source_of_truth: PASS.
- P11 ci_positive_coverage_assertion: FINDING A2-08.
- P12 settled_decisions_are_constraints: PASS.
- P13 parity_before_behavior_change: PASS.
- P14 public_repo_hygiene: PASS (the ledger file name in ubiquitous-language.md:65 already appears in public legacy/).
- P16 thresholds_are_explained: PASS.
- P17 ledger_format_frozen: PASS.
- P18 cross_platform_from_day_one: PASS.
- P19 go_hardening_toolchain: N.A. in this perimeter (toolchain lives in ARCH-08/cicd-setup).
- P20 config_over_code: FINDING A2-15 (LOW).
- P21 public_artifact_hygiene: FINDING A2-18 [owner-question].

### 3. Files not fully read
Every perimeter body was read. The `modified:` histories (frontmatter lines about 1-30) of most VP files were skimmed, not read line by line.

### 4. Novelty and convergence
Novelty: MEDIUM. A2-02 through A2-08 are new defects in property statements and oracles, not rewordings of earlier findings.

**NOT_CONVERGED**

## Perimeter B (BC-1.01, BC-1.02)

Findings: 8 (high 0, medium 2, low 4, cosmetic 2).

**ADV-P12 Perimeter B (BC-1.01.\*, BC-1.02.\*) — adversarial review, pass 12**

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P12-B01 | MEDIUM | Missing exclusion tag / crash path not in the register | BC-1.02.018:96 (EC-009), :111 (vector `tin "x"`); legacy SL:586, SL:1105-1112 | **The defect:** EC-009 and its "legacy oracle" vector read as a byte-parity obligation, but they are not one. A non-numeric `tin` cannot reach SL:586 from a transcript. **Why:** at SL:1108, `tin += _i + _w + _r` always raises TypeError back at step 2 when a usage field is a string or list. The only legacy source is a hand-edited mix cache, where the SL:1039-1040 early return hands back the cached `tin`. That is a foreign-cache shape. **What is missing:** the vector has no OD-160 tag and no CP-C id. The CP-C01..C10 register (error-taxonomy:279-288) does not list this trigger, and grep finds no other spec citing the SL:586 raise. The sibling BCs do tag their foreign-cache vectors with OD-160 plus a CP-C id: BC-1.02.005 EC-009, BC-1.02.013 EC-008, BC-1.02.030 EC-008. **Same gap, uncatalogued:** non-numeric cached buckets reaching `sum(counts[:3])` at SL:1181 (BC-1.02.007). | product-owner; architect (taxonomy) |
| ADV-P12-B02 | MEDIUM | Anchors point at the wrong file `[process-gap]` | BC-1.01.002:143, BC-1.01.008:142, BC-1.01.003:140, BC-1.01.009:174; ARCH-03:361-365 | Each anchor's declared target differs from the BC's own module. **BC-1.01.002 / BC-1.01.008:** module `input.go`, anchored to `#statusline-guard`, whose target is `guard.go`. **BC-1.01.003:** module `statusline.go` (rows, LF join), anchored to `#statusline-width`, whose target is `width.go`. **BC-1.01.009:** module `statusline.go` (side-effect order), anchored to `#caches`, whose target is `cache.go` (ARCH-04). **Root cause:** the closed 12-anchor set (ARCH-03:340-359) has no target for `input.go` or `statusline.go`. ARCH-03:344 already recognises the effect-step-script heading slug, which is the precise target for BC-1.01.002 (step 1) and BC-1.01.009. | architect; product-owner |
| ADV-P12-B03 | LOW | Property false for one input | BC-1.02.010:64 (Inv 1), :102 (VP-041 row); VP-041:76-77, :151; legacy SL:506 | **Claim:** "for numeric reset, shown ⇒ reset > now — for all renders". **Counterexample:** `resets_at` NaN is numeric, `NaN <= now` is False, so the window stays reported, yet `NaN > now` is also False. BC-1.02.012 EC-010 already pins exactly this case (shown, absolute bands). **Needed:** the P-r generator does not exclude NaN; the property must exclude it, or EC-010 must be carved out. | product-owner; architect |
| ADV-P12-B04 | LOW | Contradiction between two BCs | BC-1.02.008:60 (Inv 2) vs BC-1.02.023:55, :70; legacy SL:479 | **Claim:** Inv 2 says finite input renders between `0%` and `100%`. **Counterexample:** `hr = -0.0` is finite. `max(-0.0, 0.0)` keeps -0.0, so the segment prints `-0%`. BC-1.02.023 PC2 and EC-005 pin `-0%`. | product-owner |
| ADV-P12-B05 | LOW | Incomplete enumeration | BC-1.01.006:66-74 (Inv 1(b)); interface-definitions:235 | **Claim:** separator collisions are listed as `/`, `[`, `]` ("measured built-in exact literals"). **Missing:** a separator value matching any of these dim-wrapped built-in runs also collides: <br>• `/1.0M` or `/200K` (the denominator `{DIM}/…M{RESET}`, SL:435-436) <br>• `·1m` (the API suffix, SL:553) <br>• `(~5s old)` (SL:700) <br>• `↺host 30%` (SL:762) <br>All of these are admissible separator values. **Impact:** the trim outcome is still pinned by PC1. | product-owner; architect |
| ADV-P12-B06 | LOW | Sibling docs out of sync | ARCH-03:85 (step 7b), :79 (step 2) vs BC-1.01.009:66, :72 and BC-1.01.001:66-67 | **Step 7b:** ARCH-03's Degrade? column lists only CP-S05..S13 and omits CP-O01..O05, which both BCs place there. **Step 2:** ARCH-03 omits CP-O09, which BC-1.01.009 lists. | architect |
| ADV-P12-B07 | COSMETIC | Wording contradicts itself | BC-1.02.028:73 (EC-004); legacy SL:561 | EC-004 says the S = 9,000,000 vector renders `104d04h` "with no padding", but `04` is the zero-padded `:02d` hour. The wording came in with pass-11 B09. | product-owner |
| ADV-P12-B08 | COSMETIC | History entries out of order | BC-1.01.001:31-32 (1.4.2 listed before 1.4.1); BC-1.02.030:28-29 (1.3.5 listed before 1.3.4) | The `modified` lists are not in ascending version order. This is about list order, not timestamps. | product-owner |

**Re-derived and correct (no finding):**
- Every byte vector and staircase I re-derived from legacy matched:
  - degraded line 29 bytes; R1 44+1 bytes; R2 18+1 bytes
  - all ten heat cell colours, and `heat(0/true/51/84.5/50.4)`
  - half-even rounding cases (0.015, 0.025, 0.995, 99.5, 999.5)
  - the 0.9·length boundary (0.09999999999999998), the 1.15 gates (695520, 20700), and every countdown and window-age string
  - the A/B/C and row-2 staircases, and the golden byte deltas at COLUMNS 72/80/100
  - every BC-1.02.030 sequence step
- Titles: H1, BC-INDEX and PRD titles agree for all 40 BCs; `confidence` matches the index; `subsystem: SS-01` matches the ARCH-INDEX registry.

## 2. Policy compliance

| Policy | Result |
|---|---|
| P1 append_only_numbering | PASS (001-030 contiguous); B08 is cosmetic |
| P2 lift_invariants_to_bcs | PASS (DI-007/008/012 cited and back-anchored) |
| P4 semantic_anchoring_integrity | FINDING B02, B03 |
| P5 creators_justify_anchors | FINDING B02 |
| P6 subsystem name | PASS |
| P7 H1 = BC-INDEX = PRD title | PASS (B04 is an invariant-text defect, not a title defect) |
| P12 settled_decisions_are_constraints | PASS |
| P13 parity_before_behavior_change | FINDING B01 (vector parity class unstated) |
| P14 public_repo_hygiene | PASS |
| P16 thresholds_are_explained | PASS |
| P17 ledger_format_frozen | PASS (DI-007: no ledger read) |
| P18 cross_platform_from_day_one | PASS |
| P19 go_hardening_toolchain | N.A. |
| P20 config_over_code | PASS (no `DGX_*` keys; legacy env names appear only as oracle provenance; every key I cross-checked is registered with a matching range) |
| P21 public_artifact_hygiene | PASS |

## 3. Not fully read, and claims I could not verify

**Read only in part:**
- The `modified` history blocks of most BCs (only scanned).
- interface-definitions (rows 180-399), error-taxonomy (rows 165-178 and 279-334), ARCH-03 (lines 16-124 and 329-367), VP-041 (lines 40-153).

**Not read:** test-vectors supplement, VP-INDEX body, VP-001, VP-003, VP-005, VP-006, VP-012, VP-027, VP-028, VP-040.

**Python claims I could not verify by hand:**
- SHA-1 cache keys (BC-1.02.005).
- The OV decimal expansion.
- The 8192-byte chunk-decode boundary.
- Depth limits 993/994.
- Exact float-divmod results for 5e23 and 1e24 (`…883h12m` and `…766h24m` are consistent with ulp spacing but were not computed).
- ntpath pure-Python versus C results.
- The golden A/B/C byte totals (only the deltas were checked).

## 4. Verdict

Novelty: LOW to MEDIUM. B01 and B02 are new; the rest are refinements. **NOT_CONVERGED** (two MEDIUM findings).

## Perimeter C (BC-1.03, BC-1.06, BC-1.07)

Findings: 9 (high 1, medium 2, low 5, cosmetic 1).

**ADV-P12 Perimeter C (BC-1.03.\*, BC-1.06.\*, BC-1.07.\*): pass 12 adversarial review**

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P12-C01 | HIGH | Contradiction (interface vs BC) | prd-supplements/interface-definitions.md:134-141 vs BC-1.07.008.md:61-76; legacy SL:1242-1245 | The subagent-mode output contract lists rows, zero bytes and config-error zero bytes. It then says the "degraded ladder" from main mode "do[es] not apply in this mode". In legacy, `main_subagent` catches only stdin faults (SL:929-932), so CP-A01..A05 reach the guard and print the 29-byte line (SL:1243-1244). BC-1.07.008 PC1-6, BC-1.07.001:112 (VP-004 row), capabilities.md:31 (CAP-009 carve-out), ARCH-03:155-156 and error-taxonomy.md:232-233 all pin that line. An implementer or test author working from the interface definition would exclude a legal output. | product-owner |
| ADV-P12-C02 | MEDIUM | Spec drift (quirk overgeneralized) | BC-1.07.007.md:48, :79-81 (PC6), :82-83 (PC7); BC-1.07.008.md:69-71 (PC4), :72-73 (PC5); BC-1.07.001.md:112; legacy SL:930-932 | The CP-A04/A05 trigger is stated as an open-ended `\|n\| >= 2**1024 - 2**970`. An int literal of more than 4,300 digits never reaches the gate: `json.load` (SL:930) raises ValueError on CPython 3.11's int-digit limit, the error is absorbed to `{}` (SL:931-932), and stdout is zero bytes, not the degraded line. A test built from PC6 with a 5,000-digit `tokenCount` would fail against the oracle. Sibling specs already bound this: BC-1.04.002:98 ("only 309..4300-digit literals"), BC-1.01.002 EC-009 (oracle-verified) and ARCH-03:114-115. This is a sibling-propagation gap. | product-owner |
| ADV-P12-C03 | MEDIUM | Partial-fix regression | BC-1.07.002.md:66-70 (PC5), :78-80 (Inv 3), :89 (EC-004) vs interface-definitions.md:49-51, :138-139; error-taxonomy.md:68 | BC-1.07.002 says "the `hylo: config error: …` diagnostic goes to stderr", which reads as one line. The supplements say all reason lines (the full list, in registry order) go to stderr, and interface-definitions:50-51 records that the singular wording was "corrected pass-5 A08". The correction never reached the owning BC. With two invalid keys, a test written from PC5 would assert one stderr line. | product-owner |
| ADV-P12-C04 | LOW | Mis-anchor (label) | prd.md:665 | ASM-007 cites ASSUMP-107-1 at "BC-1.07.001 PC-2, BC-1.07.002 PC-1". The assumption actually sits in Precondition 2 (BC-1.07.001:58) and Precondition 1 (BC-1.07.002:51). BC-1.07.001 PC2 (:70) is the absent-flag main-render rule. The BC itself uses "Pre-N" for preconditions (BC-1.07.001:112). | product-owner |
| ADV-P12-C05 | LOW (pending intent verification) | Mis-anchor (range owner) | BC-1.07.004.md:85-86 (PC7) | The joiner's range ("free text with no control bytes") is anchored to BC-2.01.003 PC-3. That postcondition is the `statusline.theme.separator` rule (BC-2.01.003:78). The joiner is a Text-class key, and its control-byte error is raised by BC-2.01.005 (interface-definitions.md:272; BC-2.02.001:136; error-taxonomy.md:96). | product-owner |
| ADV-P12-C06 | LOW | Thresholds rationale (P16) | BC-1.07.007.md:46-47; legacy SL:863-864 vs SL:876-885; interface-definitions.md:274-275 | The subagent `_fmt_tokens` thresholds cite "compact tokens approved mockup" / T-042. That rationale is the docstring of a different function, `_fmt_tok_c` (SL:864), which uses different formats (`.0f`k / `.1f`M). `_fmt_tokens` (SL:876) carries no rationale. The k_from/m_from rationale should be stated as its own (for example, a unit-boundary convention) rather than borrowed. | product-owner |
| ADV-P12-C07 | LOW | Ambiguity | BC-1.07.004.md:63-65 (PC3) | "Every non-ASCII character goes on the wire as a `\uXXXX` escape" is wrong for astral code points. CPython `ensure_ascii` emits a surrogate pair of two escapes. BC-1.07.005 EC-006 explicitly includes emoji, and BC-5.02.001:68-69 states the 12-character pair. PC3's example list is BMP-only. | product-owner |
| ADV-P12-C08 | LOW [owner-question] | Public-repo hygiene (P14) | BC-1.07.004.md:78; BC-1.07.007.md:143; BC-1.03.010.md:132 | Oracle provenance cites a machine-specific interpreter install path (not a home path; no username). The owner should decide whether that level of tool-layout detail belongs in the public specs. | product-owner |
| ADV-P12-C09 | COSMETIC | Arithmetic | BC-1.07.004.md:119 | The vector calls the raw stdin token a "7-byte JSON escape spelling". The escape is 6 bytes, or 8 with quotes. | product-owner |

## 2. Policy compliance

- **P1 append_only_numbering:** PASS. CP-T08 is retired, not reused; the register totals 49 (BC-1.03.018:51-53).
- **P2 lift_invariants_to_bcs:** PASS. DI-007, DI-008 and DI-012 are cited throughout.
- **P4 semantic_anchoring_integrity:** FINDING (C04, C05).
- **P5 creators_justify_anchors:** PASS.
- **P6 subsystem name:** PASS. All 31 BCs carry `subsystem: "SS-01"`, matching ARCH-INDEX:50,55.
- **P7 titles:** PASS. All 31 H1 headings match BC-INDEX:117-137, 183-184, 190-197 and prd.md:215-235, 281-295, and describe their postconditions.
- **P12 settled decisions:** PASS. No settled decision is challenged.
- **P13 parity before behavior change:** PASS. Every deviation is named: D4-EX-2, OD-161, temp-file/OD-163, OD-155 off switch, OD-172/cp-x03, OD-160.
- **P14 public_repo_hygiene:** FINDING (C08, owner question).
- **P16 thresholds_are_explained:** FINDING (C06). The other rationale codes match the registry: T-054 J, T-055 DOC, T-056 M, T-057 DOC, T-058 J, T-059 J, T-060 Dv.
- **P17 ledger_format_frozen:** N.A. No ledger access in these BCs (DI-007).
- **P18 cross_platform_from_day_one:** PASS. Windows legs are specified and their not-executed status is disclosed (ASM-005).
- **P19 go_hardening_toolchain:** PASS (FMA/PR-15 discipline in BC-1.07.007 is consistent).
- **P20 config_over_code:** PASS. The ranges for transcript, turn, composition and subagent keys match interface-definitions.md:245-251 and 262-276.
- **P21 public_artifact_hygiene:** PASS. No flagged strings are quoted in this report.

## 3. Coverage and unverified claims

**Read fully (body):** all 31 BCs. Most frontmatter was skimmed, and the `modified` histories were not audited.

**Read partly:** BC-INDEX, prd.md, interface-definitions.md, error-taxonomy.md, ARCH-03 (lines 80-170 plus headings), ARCH-04 (headings only), BC-2.01.004 (lines 150-320), BC-5.02.006 (lines 90-142), and VP frontmatter `bcs:` lines.

**Not read:** domain-spec/invariants.md, prd-supplements/test-vectors.md, VP bodies (other than VP-004 grep hits), BC-5.04.001.

**Python claims I could not execute (read-only, no Bash).** I hand-recomputed the byte sizes and values for every vector in BC-1.03.002-.021, BC-1.06.\* and BC-1.07.\*, and all of them check. Taken on trust:
- JSON int-digit-limit ValueError (from BC-1.01.002 EC-009).
- `seek(negative)` raising OSError on a binary file (BC-1.03.002 EC-009).
- The shared NaN decode constant.
- The depth budgets 993/994 and 991/994.
- That Windows `fd` OverflowError text.
- CPython recursion behavior at the SL:924 dump site.

## 4. Novelty

MEDIUM. C01-C03 are substantive propagation and contradiction gaps; C04-C09 are refinements.

**NOT_CONVERGED**

## Perimeter C2 (BC-1.04, BC-1.05)

Findings: 9 (high 1, medium 4, low 3, cosmetic 1).

## Adversarial Review: Pass 12, Perimeter C2 (BC-1.04.*, BC-1.05.*)

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P12-C2-01 | MEDIUM | Wrong legacy semantics | BC-1.04.009:55-56 (Pre 1), :116 (EC-011); BC-1.04.014:76 (EC-010); legacy SL:671, SL:674 | These rows say a plotted giant exact int of *magnitude* ≥ 2**1024 − 2**970 raises OverflowError at SL:674. That holds only for positive values. For a negative giant, SL:674 `max(v, 0.0)` compares int to float exactly and returns `0.0`. The `v`/`f` top at SL:671 (`max(max(vals), floor)`) ignores it too. So legacy draws `▁` and does not degrade. A test written from these rows would expect errDegraded where legacy renders. Fix: say "value ≥ 2**1024 − 2**970" and add a negative-giant row that renders `▁`. Contrast BC-1.04.003 EC-010, where "both signs" is correct (that site is a subtraction). | product-owner |
| ADV-P12-C2-02 | HIGH | Partial-fix sibling gap (2 files) | BC-1.04.009:129-132; BC-1.04.014:88-91; VP-012:13; VP-001:13 | Pass 11 (ADV-P11-C2-04) added OD-160 foreign-hist crash legs to both BCs. Neither got the VP-012 exclusion-closure row that every other OD-160 BC carries (BC-1.04.002:140, BC-1.04.003:132, BC-1.04.018:105, BC-1.05.004:151, BC-1.05.005:141). VP-012 `bcs:` lists neither. BC-1.04.009 also has no VP-001 row for its EC-011 degrade legs, and VP-001 `bcs:` omits it. ADV-P11-C2-02 did exactly this lift for BC-1.04.018 in the same pass. | product-owner |
| ADV-P12-C2-03 | MEDIUM | Spec gap / false universal claim | BC-1.04.001:214-217 (PC1), :256 (Go step list); ARCH-03:281-283; legacy SL:165, SL:170 | PC1 says the next GET drops "the fragment" and that "a request line never carries #frag". In CPython 3.11, `Request.full_url` uses `_splittag`, which is `url.rpartition('#')` and splits at the **last** `#`. `quote(..., safe=string.punctuation)` keeps `#`. So `Location: /a#b#c` gives the request line `GET /a#b HTTP/1.1`. A first-`#` split (urlsplit, or Go `url.Parse`) gives `GET /a`. The same rule, plus `_splithost` prepending `/`, decides the *initial* selector for a metrics URL that contains `#`, which BC-2.02.005:68-70 accepts. VP-030 Tier C varies header values, so this is reachable. The BC should pin selector = last-`#` split, then `_splithost`. Source-derived, not oracle-run. | product-owner |
| ADV-P12-C2-04 | MEDIUM | Anchor/count drift after a pass-11 fix | BC-1.04.003:131 (VP row); VP-031:74-98, :134 | The BC row says it covers the fallback cases but gives the proof method as "manual (table over 16 subsets)". VP-031 v1.6 (pass-11 C2-01) now defines 24 rows: 16 primary-`v` plus 8 fallback-`v`. The BC was not updated to match. | product-owner |
| ADV-P12-C2-05 | MEDIUM | P20 literal contradicts a sibling under allowed config | BC-1.04.002:69 (PC3 `hist[-32:]`); BC-1.04.003:88 (PC5 `hist[-cap:]`); BC-1.04.014:46, :72 ("last 12"); BC-1.04.009:131 (VP row "last 12") | With a non-default `statusline.sparkline.history_cap` (1..1000), BC-1.04.002 PC3 contradicts BC-1.04.003 PC5 about what gets saved. With a non-default `statusline.sparkline.points` (1..100), BC-1.04.014's crash precondition picks the wrong window. Earlier key-naming sweeps (ADV-P9-C2-09, ADV-P10-C2-06) missed these spots. | product-owner |
| ADV-P12-C2-06 | LOW | Incomplete exhaustive invariant | BC-1.04.004:73-77 (Inv 3); legacy SL:741, SL:778-779 | Inv 3 lists every way row-2 rendering can fail for a dict sample, and the list is incomplete. It omits the BC-1.04.018 PC1 OD-160 overflow (a giant `lr[0]` at SL:778-779, inside render_telemetry_fields). It also omits foreign cached-sample value shapes (OD-160, BC-1.04.002 EC-008), e.g. a string `vllm:num_requests_running` raises ValueError at the SL:741 `.0f` format. | product-owner |
| ADV-P12-C2-07 | LOW | Sibling asymmetry (pending intent verification) | BC-1.05.001:50-52 (Pre 1), :72 (PC2), :127 (L2 row); legacy SL:616 | Pre 1 admits a 309-digit exact int `usd`, and PC2 promises the `$` bytes. Legacy raises CP-O10 at that very format. Sibling BC-1.05.002 restates its CP-O11 leg (PC5, EC-009, DI-008, VP-001 row); BC-1.05.001 restates nothing. It may be enough that the error taxonomy names BC-1.05.007 as the CP-O10 owner. | product-owner |
| ADV-P12-C2-08 | LOW | P20 named-constant note missing | BC-1.04.002:64, :86, :118 | The cached-path sentinel `c.get("ts", 9999)` changes behaviour: a foreign sample with no `ts` displays the age `now − 9999`. Neither it nor the `0` fallbacks carry the named-constant / "why not config" note P20 requires. | architect |
| ADV-P12-C2-09 | COSMETIC | Changelog order | BC-1.05.005:37-38 | The `modified:` list runs 1.3.6, 1.3.8, 1.3.7. The 1.3.8 entry was inserted instead of appended. | product-owner |

**Re-derived and confirmed against legacy, no issue found:**
- **BC-1.04.020:** the full 11-step sequence, both exact rows and every set of cache bytes.
- **BC-1.04.009 / BC-1.04.008:** glyph indices, the trail RGB at n = 8 and n = 12, and EC-002 through EC-009.
- **BC-1.05.005:** the indices for n = 10, 11, 20, 21, 41, 81, plus the 0.95 float-product proof behind Inv 2.
- **BC-1.05.008:** the 16-value and 14-value threshold lists and all 12 golden rows.
- **BC-1.05.006:** the legacy duplicate-key tail.
- **BC-1.05.002 / .003 / .007:** the arithmetic vectors.
- **Tables:** the BC-1.04.007 and BC-1.04.015 KV tables, the BC-1.04.017 age formats, and the BC-1.04.019 rounding ties.
- **Redirect handling:** the `http_error_302` order in BC-1.04.001 (loop check before the body drain; no check on the first hop).

### 2. Policy compliance
- P1 append_only_numbering: PASS (EC ids append-only; C2-09 is changelog order, not ID numbering)
- P2 lift_invariants_to_bcs: FINDING C2-02, C2-07
- P4 semantic_anchoring_integrity: FINDING C2-04
- P5 creators_justify_anchors: PASS
- P6 subsystem name: PASS (all 30 BCs carry `SS-01`, matching ARCH-INDEX:55)
- P7 H1 = BC-INDEX = PRD title: PASS (all 30 match BC-INDEX:143-177; PRD rows sampled)
- P12 settled_decisions_are_constraints: PASS
- P13 parity_before_behavior_change: PASS
- P14 public_repo_hygiene: PASS (only RFC 5737 and loopback addresses)
- P16 thresholds_are_explained: PASS
- P17 ledger_format_frozen: PASS (BC-1.04.012 keeps the D7 metric name)
- P18 cross_platform_from_day_one: PASS
- P19 go_hardening_toolchain: PASS
- P20 config_over_code: FINDING C2-05, C2-08
- P21 public_artifact_hygiene: PASS

### 3. Not fully read / not verified
- **Read only in part:** ARCH-03 (lines 225-324 only), ARCH-04 (not read), domain-spec/invariants.md (not read), capabilities.md, error-taxonomy, test-vectors and prd.md (grep only). Of the VPs, VP-030 lines 40-160 and VP-031 by grep only. In BC-1.04.006, .007, .010-.013 and .015-.019 I skipped the frontmatter changelogs.
- **Python claims I derived from source but did not run:**
  - C2-01: `max(-(2**1024), 0.0)` returns `0.0` through exact int-to-float comparison.
  - C2-03: `_splittag` uses rpartition, and `_splithost` prepends `/`.
- **Taken from prior oracle runs, not re-checked:** `format(999.995, ".2f")` = `1000.00` (BC-1.05.007 EC-005), and the NaN sort orders in BC-1.05.005 EC-009.

### 4. Novelty
MEDIUM. C2-01 and C2-03 are new legacy-semantics defects. C2-02, C2-04 and C2-05 are fixes from passes 9-11 that did not carry over to sibling files.

**NOT_CONVERGED**

## Perimeter D (S2-S6 BCs)

Findings: 16 (high 5, medium 6, low 5, cosmetic 0).

**ADV-P12 Perimeter D (BCs in SS-02 to SS-06): NOT_CONVERGED.** I found 16 problems: 5 HIGH, 6 MEDIUM, 5 LOW. Three of them come from pass-11 fixes that were applied to one file but not carried into its siblings.

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P12-D01 | HIGH | Contradiction (partial-fix propagation) | BC-3.02.001:104-113, :126; BC-6.03.004:98, :111-116; vs BC-3.02.002:57-62, BC-6.03.003:83-89, :161 | Pass-11 D01 made `cache-003` a corpus case with an **unseeded** `proc_start` and a declared fake process table. BC-3.02.001 Inv 4 still says "NO unseeded corpus case exists" and "no P1 corpus case declares the fake process table". BC-6.03.004's D4-EX-1 row and closure paragraph still say "every corpus case seeds `proc_start`" and "no unseeded-probe … case exists". The sibling files were not updated (blast radius 2 or more files). | product-owner |
| ADV-P12-D02 | HIGH | Spec cannot be implemented / hermeticity (P18) | BC-6.01.002:126-136, :141-155; BC-2.01.001:122-129; BC-6.02.002:118-121; BC-6.03.003:84-86 | For `cache-003` the Go side is said to use "a `ProcStarter` fake", but the Go child is the built `hylo` binary. Its exact env key set has no fake-table key, no `PATH`, and no reserved name that could carry one. As specified, the built binary walks the runner's real process tree, which can contain a real `claude` ancestor. BC-6.02.002 Pre-3 also says "the fake `ps` serves both sides", but Go has no `ps`. The Windows leg is not specified either: a script-only fake `ps` is not an `.exe`, so legacy gets FileNotFoundError while the Go fake returns a start time. That is D4-EX-1 territory, which these same files say no corpus case reaches. | architect |
| ADV-P12-D03 | HIGH | Inert regression detector (CI positive coverage) [process-gap] | BC-6.01.003:62-66 vs :141-143, :150-158; BC-6.01.002:178-194 | Pass-11 A2-02 removed the shim's newline reconfigure, but PC-4 still says "the Windows leg discriminates the LF half only". PC-5's negative control (no shim, so stdout must contain CRLF) proves nothing now, because stdout contains CRLF with the shim loaded too. The stdio canary can no longer detect a missing shim on any leg: on POSIX this is stated, on Windows the encoding is fixed by the builder, and the LF half was withdrawn. Yet it is still described as a gating, discriminating check. | architect |
| ADV-P12-D04 | HIGH | Public-repo hygiene gap (P14), CI-as-code [owner-question] | BC-6.04.001:56-57, :102-107, :151 | `--log-opts="main factory-artifacts"` never scans the commits of a pull-request head or a feature-branch push that are not yet on those two refs. A secret in a PR therefore passes CI. Also, under `actions/checkout`, `factory-artifacts` (and `main` on PR runs) usually exists only as `origin/<ref>`, so both `git log` and `git rev-list --count main factory-artifacts` can fail to resolve. The Traceability row (:151) still says `--log-opts="--all"` and "Go 1.26.x leg". Confidence MEDIUM, because it depends on checkout's ref behavior. | architect |
| ADV-P12-D05 | HIGH | Title sync (P7) | prd.md:426 vs BC-6.04.001:43 and BC-INDEX:318 | The PRD title says "Go 1.26.0 leg"; the H1 and BC-INDEX say "Go 1.26.0 floor leg". The 1.2.6 changelog claims "index titles synced", but the PRD was missed. | product-owner |
| ADV-P12-D06 | MEDIUM | Ambiguity, no failing test can be written | BC-2.01.005:73-81, :169-180; BC-5.03.002:52-55 | List items are stripped with Python `str.strip()`, whose set includes 0x09-0x0D and 0x1C-0x1F, and are also checked for control bytes. The check order is never stated. For `HYLO_BACKENDS_0_MODEL_PREFIXES` with a value ending in a tab, strip-first accepts the value (legacy-identical) and check-first raises `control character`. The same ambiguity applies to `limits.windows` and to reroute-all entries. | product-owner |
| ADV-P12-D07 | MEDIUM | Contradiction (per-OS, P18) | BC-3.01.001:68-73, :142 vs BC-2.01.005:91-96; BC-2.03.002:83-93, :107-114 | BC-3.01.001 treats a relative `HOME` as unset. BC-2.01.005's `~` expansion treats only set-but-empty as "home unknown", so with a relative `HOME`, `HYLO_PATHS_CACHE_DIR` set to `~/c` yields `not an absolute path` instead of `home directory unknown`. With a relative `HOME`, `HYLO_CONFIG` set to `~/alt.yaml` could print a relative path or `(HOME unset)`; the spec does not say which. A relative `USERPROFILE` (Windows home) is not covered by the base-directory rule at all. | product-owner |
| ADV-P12-D08 | MEDIUM | Per-OS behavior not specified (P18) | BC-2.01.001:111-122; BC-2.01.003:79-82; BC-2.01.005:181-186; BC-2.02.001:138 | The Windows "WTF-8 value with a lone surrogate leads to `invalid UTF-8`" leg assumes `platform.EnvVars` decodes the UTF-16 environment while preserving lone surrogates. The seam contract never says how the UTF-16 is decoded. Go's native environment read substitutes U+FFFD, which would make this leg unreachable and its test impossible to write. ARCH-05:51 pins surrogate preservation for the outbound path direction only. Confidence MEDIUM, because the Go runtime behavior was not checked against source. | architect |
| ADV-P12-D09 | MEDIUM | Sibling not updated / anchoring | BC-2.02.005:49-50, :54-55 vs BC-2.01.002:95-101 | The URL class is scoped to `HYLO_BACKENDS_0_METRICS_URL`, with `<key>` fixed as `backends[0].metrics_url`. Pass-8 D17 rules that index ≠ 0 values are validated by their field's class and render as `backends[1].metrics_url=… (scheme must be http or https)`. The class contract does not admit that. | product-owner |
| ADV-P12-D10 | MEDIUM | Wrong expected value | BC-5.03.004:89 vs :56-63 | EC-008 gives the UNC-root label with one leading backslash; PC-3 and PC-4 give `\\server\share`. A test derived from EC-008 asserts the wrong bytes. | product-owner |
| ADV-P12-D11 | MEDIUM | CI positive coverage | BC-6.04.003:110-112, :124-127, :150 | The nightly run is `clean` when there are 0 divergences, but no completed-case count of at least 1 is required. EC-005 discards partial sequences, so a run that completes zero cases still reports `clean` and satisfies the OD-149 P1 exit gate. | architect |
| ADV-P12-D12 | LOW | Spec choice not carried through | BC-2.01.005:85-91 vs BC-2.03.002:90-91, BC-3.01.001:75-77 | The canonical grammar BC requires `paths.cache_dir` to be absolute but omits the per-OS rule (filepath.IsAbs, where `\foo` and `C:foo` count as relative). Only the sibling BCs carry it. | product-owner |
| ADV-P12-D13 | LOW | Stale claim | BC-6.03.003:80-82; BC-6.01.003:97-99 | With `cache-003`'s fake `ps` matching `claude`, legacy also saves at SL:288 into the same failing path, so up to **three** temp files leak, not "up to two". The shim's statement that mktime and strptime "run only on the ps path, which the seeded proc_start bypasses" is stale now that `cache-003` runs that path (it is deterministic under the UTC pin). | product-owner |
| ADV-P12-D14 | LOW | Composition under-specified | BC-5.02.002:50-53 vs BC-5.02.001:92-106, ARCH-06:69-77 | Pre-2 passes one `depthBudget` to both Decode and DumpsLen, but the measured budgets differ (line decode 993; encode 991 or 990). It does not say which constant the oracle test uses. | product-owner |
| ADV-P12-D15 | LOW | Ambiguity | BC-6.04.001:92-101 | "The run includes the Tier B goldens, the exclusion table tests and the corpus hygiene test" follows the `-run "$ORACLE_TESTS"` job, whose pattern excludes exactly those tests. The intended job is the `-skip` step. | architect |
| ADV-P12-D16 | LOW | Stale traceability | BC-6.04.001:151 | The Source row still cites "Go 1.26.x leg" and gitleaks `--all`, contradicting the body (same file as D04; recorded separately for the index sweep). | product-owner |

## 2. Policy compliance
- P1 append_only_numbering: PASS
- P2 lift_invariants_to_bcs: PASS (DI citations present; not exhaustively audited)
- P4 semantic_anchoring_integrity: FINDING D01, D09, D10
- P5 creators_justify_anchors: PASS
- P6 subsystem names: PASS (sampled frontmatter matches SS-02 to SS-06)
- P7 title sync: FINDING D05
- P12 settled decisions as constraints: PASS (D04 tagged owner-question because the two-ref scan was an orchestrator binding)
- P13 parity before behavior change: PASS
- P14 public_repo_hygiene: FINDING D04
- P16 thresholds explained: PASS
- P18 cross-platform from day one: FINDING D02, D07, D08
- P19 Go hardening toolchain: PASS (staticcheck and govulncheck required)
- P20 config over code: PASS
- P21 public_artifact_hygiene: PASS (no flagged strings quoted here)
- P3, P8, P9, P10, P11, P15, P17: N.A. (no ledger surface; the CI aspects are covered under D04 and D11)

## 3. Not fully read, and claims I could not verify
- **Not read:** ARCH-07, ARCH-08, the ARCH-01/02/05 bodies (only grep hits), the VP bodies (index only), prd-supplements, and capabilities/invariants. The top 20-40 frontmatter lines of most BCs were skipped (the H1 and all body text were read). prd.md and BC-INDEX were read through targeted grep only.
- **Python claims not verified:**
  - The MSVC `localtime_s` lower bound (0 versus about -43200) that the "left-closed [1970-01-02 …)" domain rests on. The cited "re-measurement" is probe arithmetic, not a Windows run.
  - The 3.11.x patch range of gh-106242.
  - CPython 3.11.7 `ntpath.splitdrive` behavior for device roots with the long-path prefix.
  - The golden A heat RGB triples. Every other golden A/B/C value I hand-checked against legacy matched.
- **Go claim not verified:** whether `os.Environ` on Windows replaces lone surrogates with U+FFFD (this is the basis of D08).
- **Legacy citations I spot-checked and found correct:** SL:73-77, 89, 165, 198-206, 265-295, 426, 444-449, 487-489, 519-521, 545-561, 631, 675, 696-834, 857-885, 902-924, 1059-1174, 1185-1245.

## 4. Novelty: MEDIUM
D01-D04, D08 and D11 are new and substantive. The rest are refinements.

**NOT_CONVERGED**
