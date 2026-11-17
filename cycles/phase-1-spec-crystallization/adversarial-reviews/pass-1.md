---
document_type: adversarial-review
phase: 1d
pass: 1
date: 2026-11-17
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: HIGH
---

# Adversarial Spec Review — Phase 1d, Pass 1

Pass 1 ran as six fresh-context perimeters (A, A2, B, C, C2, D) because the spec corpus under review (~1.4 MB: PRD and supplements, domain spec, 145 behavioral contracts, architecture, verification properties) exceeds a single agent context. Each perimeter was reviewed by an independent fresh-context adversary with no visibility into the other perimeters or into any prior pass. Each section below is the verbatim final report of one perimeter, unedited except for this framing. Per-perimeter novelty rulings: A HIGH, A2 HIGH, B HIGH, C MEDIUM, C2 HIGH, D HIGH — aggregated as HIGH at pass level; the pass is NOT_CONVERGED.

## Perimeter A (cross-cutting)

Findings: 21 (high 6, medium 9, low 6).

## 1. Findings

| ID | Sev | Category | File:line | Defect | Owner |
|---|---|---|---|---|---|
| ADV-P1-A01 | HIGH | parity / invented cap (P13, P16) | prd-supplements/nfr-catalog.md:28; prd.md:453; verification-properties/VP-031-bounded-resource-caps.md:38,71; VP-029-transcript-parse-tables.md:52 | NFR-005 and VP-031 require a "1,000-line turn identity window", and the VP-031 harness asserts `turnIdentityWindow() != 1000`. Legacy has no such cap. The only caps in legacy are `ids[-256:]` (legacy/dgx_statusline.py:1153), `hist[-32:]` (:350) and `_READ_CAP = 524288` (:952). Building the window would add behavior legacy does not have and could break parity. "memory-256 mix cache" is the same 256-id dedup list counted twice, so "five caps" is really three. No BC owns the 1,000 value. | product-owner + architect |
| ADV-P1-A02 | HIGH | contradiction / closed set | prd-supplements/error-taxonomy.md:28,61 vs :76-79; architecture/ARCH-02-configuration.md:46-48; VP-016-config-error-classes-line.md:37,57,68,74-78; prd.md:467 | Several documents say the config-error class register is "closed at six". The canonical reason vocabulary (BC-2.02.001:90-109, repeated in error-taxonomy.md:76-79) also has `path` (`empty path`, `home directory unknown`), `backends` and `URL/text` (theme `control character`) entries. VP-016 has only five class tables (Number, Boolean, URL, Enum, Theme), so the path and backends reasons are never tested. Either these are classes (then the count is wrong and they need table tests) or they need re-classing. | product-owner |
| ADV-P1-A03 | MEDIUM | contradiction | prd.md:615-617; architecture/ARCH-INDEX.md:88-90; ARCH-05-platform.md:47-49 | These say that after OD-147, setting `statusline.window_age.ps_timeout_s` "is an ordinary unknown-key config error". The settled contract is that an unknown `HYLO_*` setting only produces a stderr warning, is ignored, and never changes exit status (BC-2.01.001:72; ARCH-02:32-33; interface-definitions.md:103-105). There is no unknown-key error class. A story writer could build a seventh class. | architect |
| ADV-P1-A04 | HIGH | partial-fix regression / ruling drift | behavioral-contracts/ss-06/BC-6.04.003.md:36,40,128; BC-INDEX.md:289; prd.md:391 | BC-6.04.003's H1 and body still say Tier C runs "nightly Linux" and clean "for an owner-picked number of nights (proposal 3)". OD-149 ruled three OSes and ONE clean run at 30 minutes per OS. That ruling is applied in ARCH-07:34, ARCH-08:43,63-65, VP-011:46-48 and cicd-setup.md:51, but not in the BC that stories will be built from. | product-owner |
| ADV-P1-A05 | MEDIUM | id mismatch in fail-closed machinery | architecture/ARCH-07-parity-harness.md:42 vs BC-6.03.004.md:56-57; prd.md:553-555 | ARCH-07 lists the closed exclusion ids as `od30` and `od76`; BC-6.03.004 uses `OD-30` and `OD-76`. The validator fails closed on any id outside the set, so a string mismatch either fails every entry or invites a silent alias. Separately, the DI-012 list in PRD §8 leaves out `cp-x03`, which PRD §10 OQ-1 (prd.md:599) and ARCH-07 include. | architect |
| ADV-P1-A06 | HIGH | VP catalog coverage drift (P9) | verification-properties/VP-INDEX.md:121-214 | The BC Coverage Map is missing pairs declared in the VP frontmatter `bcs:` lists. VP-012 lists 14 BCs (VP-012:13), but the map credits it only to BC-6.03.003 and BC-6.03.004. It omits BC-1.06.002, BC-3.02.001/.002, BC-1.03.018..020 and BC-2.02.001..006. Also missing: VP-019 for BC-1.04.020 (VP-019:13) and VP-007 for BC-5.04.003 (VP-007:13). The arithmetic is correct (37 VPs; 29/6/1/1 by class; 20/5/9/1/1/1 by method; 145 BCs). The per-BC view is not. | architect |
| ADV-P1-A07 | MEDIUM | toolchain (P19) | VP-005/007/012/015/023/024/025 line 15; ARCH-06-pyfmt.md:53; prd.md:536 | Seven VPs declare `proof_method: proptest`, which is a Rust library. No VP names a Go property-testing library (`testing/quick` or `rapid`); the Tool column just says "Go test" (VP-023:75). The random-sample property generators also never say what they assert: the CPython oracle is only available as committed tables, so random samples have no oracle. ARCH-00:91 and module-criticality.md:22-27 set mutation kill-rate targets, but no mutation tool (gremlins / go-mutesting) is named anywhere. | architect |
| ADV-P1-A08 | MEDIUM | ambiguous NFR | prd.md:124-125 vs prd-supplements/module-criticality.md:22-24; ARCH-00-overview.md:91 | The PRD (following OD-135's wording) says S1 and S5 need "coverage >= 95%". module-criticality.md and ARCH-00 say "mutation kill rate >= 95%". These are different gates. The metric that actually binds is unstated. If the documents' intent differs from OD-135's wording, that is an owner question. | product-owner [owner-question] |
| ADV-P1-A09 | HIGH | CI false-green risk (P11) | cicd-setup.md:45-56, 62-67, 110-113; ARCH-08-build-ci-release.md:31-53; VP-011:73 | Several regression detectors can pass while checking nothing: (1) The parity tiers are gated by a probe step, and "a skipped required check counts as success". (2) The Go jobs exit 0 when `git ls-files '*.go'` finds nothing. (3) Tier C calls `t.Skip` when the budget variable is 0 or unset. (4) The pattern scan only reports exit status. None of them specifies a runtime-computed positive-coverage line, for example "N cases compared, M exclusions validated, K files scanned". After Phase 3, a moved package or a dropped environment variable would leave the D4 referee permanently green with zero coverage. | architect / devops [process-gap] |
| ADV-P1-A10 | MEDIUM | vacuous verification / weak anchor (P4, P5) | VP-022-ledger-read-scope-absence.md:37-40, 57-61, 74-89; ARCH-03-statusline.md:101-105; ARCH-04-data-files.md:81 | VP-022 claims DI-007 is enforced "structurally". But `Env.Files.ReadFile(name string)` reads any path, including the ledger. The checks look for an Env field name containing "ledger" and for a `paths.ledger` reference, and that key does not exist in P1 (ARCH-04:81). Both checks always pass. VP-022 says "ARCH-08 hygiene legs carry" the import lint, but no such job exists in ARCH-08 or cicd-setup.md:43-53. The primary anchor, BC-1.06.001 (cache never-raise), does not state DI-007. | architect |
| ADV-P1-A11 | MEDIUM | ambiguity / interface cannot express the spec | VP-006-json-depth-budgets.md:37-38, 53, 70; ARCH-06-pyfmt.md:28, 80; interface-definitions.md:52-53; prd.md:559 | Problem 1: the transcript budget is "995 accepted / 1,000 rejected", which leaves depths 996-999 undefined. VP-006 asserts a single budget ±1, and BC-5.02.003 EC-010 says "limit / limit+1", which a gap cannot satisfy. Problem 2: `Decode(b, mode)` ties the budget to the mode, but ModeText serves both stdin and cache-file loads (BC-5.02.003 invariant 3). Those are different CPython call depths. So VP-006's "per-call-site parameter" claim does not match the signature. | architect |
| ADV-P1-A12 | MEDIUM | contradiction | prd-supplements/interface-definitions.md:67 | It says the degraded line's grey/reset "come from `statusline.theme.*` legacy defaults (OD-113)". BC-2.02.001 invariant 2 (:117-119), BC-2.01.003:84 and ARCH-00:32-33 make that SGR pair a built-in named constant. Following the supplement, a theme override would break the 29-byte line (BC-1.01.001). | product-owner |
| ADV-P1-A13 | HIGH | subsystem name drift (P6) | prd.md:109-120; prd-supplements/module-criticality.md:42-58 vs ARCH-INDEX.md:53-64 | PRD §1.6 names do not match the canonical registry: "Status line" vs "Status Line", "Python-compatible formatting (`internal/pyfmt`)" vs "Pyfmt", "Parity harness" vs "Parity Harness", "Proxy & routing" vs "Proxy And Routing", "Launcher / hook / doctor / CA" vs "Launcher Hook Doctor CA", "UIs (web + TUI)" vs "UIs". module-criticality.md has the same drift. | product-owner |
| ADV-P1-A14 | LOW | stale text | prd.md:40-42, 48-49, 103; module-criticality.md:17 | OD-131 is still described as "to be recorded / pending", but it is recorded (owner-decisions-log:95) and its pending item was resolved by OD-135. The stage-2 note still says "138/138" BC files. | product-owner |
| ADV-P1-A15 | MEDIUM | invariant orphans (P2) | domain-spec/invariants.md:22-44 | The table has no enforcer/BC column. 13 invariants (DI-001..006, 009, 011, 013..017) have no BC and no "deferred to Px (OD-115)" marker, so orphans cannot be told apart from planned deferrals. DI-007, 008, 010 and 012 are cited by BCs (verified by grep). | business-analyst |
| ADV-P1-A16 | MEDIUM | architecture gap | ARCH-00-overview.md:46-62, 73; interface-definitions.md:97; ARCH-04:23; module-criticality.md:29-47 | The `paths.cache_dir` default is the per-OS platform directory, and `~` expansion needs the home directory. Yet the dependency graph shows `internal/config` importing only pyfmt. Either a cfg→plat edge is missing or the owner of default resolution is unstated. Separately, `internal/cost` is a separate package (ARCH-00:51, 73) with no row in module-criticality, so its mutation tier is undefined. | architect |
| ADV-P1-A17 | LOW | NFR ambiguity | prd.md:452; nfr-catalog.md:27 vs ARCH-08:37, 46; VP-037:37 | NFR-004 says "-race clean" with no qualifier. ARCH-08 and VP-037 run `-race` only on the Linux and macOS legs. | product-owner |
| ADV-P1-A18 | LOW | unexplained constants (P16, P20) | ARCH-05-platform.md:26, 28 | The ancestor walk depth "at most 6 levels" has no key and no named-constant rationale. The source of `CLK_TCK` for the Linux start-time formula is unstated (Go's standard library has no sysconf). | architect |
| ADV-P1-A19 | LOW | ambiguous wording | prd.md:478; ARCH-01-binary-cli.md:49 | "by ruler TOM side (OD-102)" / "ruler TOM-side exits" is unreadable as a requirement. | product-owner |
| ADV-P1-A20 | LOW | anchor drift | BC-COMPONENT-MAP.md:31, 37, 117 vs ARCH-03-statusline.md:111-114 | `sl/statusline.go` is the component home for three BCs but is not in ARCH-03's file-family list. | architect |
| ADV-P1-A21 | LOW | untestable reason | ARCH-02:66-68; error-taxonomy.md:79 | In P1, config comes from the environment only, and `HYLO_BACKENDS_1_*` is an unknown (warned) setting (BC-2.01.002:73-77). No input can produce zero or more than one backend entries, so `exactly one backend entry until P6` cannot be reached or tested in P1. | architect |

## 2. Policy compliance

- P1 append_only_numbering: PASS. No renumbering seen; BC-SL-097 and BC-SL-068 are accounted for.
- P2 lift_invariants_to_bcs: FINDING A15.
- P4 semantic_anchoring_integrity: FINDING A06, A10, A20.
- P5 creators_justify_anchors: FINDING A10 (VP-022 primary anchor). Other sampled anchors are justified.
- P6 subsystem names: FINDING A13.
- P7 BC H1 title: PASS on H1 ↔ BC-INDEX ↔ PRD sync for the rows I sampled. The content of the BC-6.04.003 title is stale (A04).
- P9 VP-INDEX: arithmetic PASS; FINDING A06 (coverage map vs VP frontmatter).
- P11 CI positive coverage: FINDING A09.
- P12 settled decisions: D1-D16 PASS. FINDING A04 (BC contradicts OD-149); A08 is an owner question.
- P13 parity before behavior change: FINDING A01.
- P14 public repo hygiene: PASS. I grepped my perimeter for private IP ranges, home paths and personal emails: no hits. Only the 192.0.2.x placeholder appears.
- P16 thresholds explained: FINDING A01, A18.
- P17 ledger frozen: PASS. P1 has no ledger code; ARCH-04 and ARCH-09 reserve the boundary.
- P18 cross-platform: PASS for build-tag confinement (ARCH-05); see A17.
- P19 Go toolchain: FINDING A07.
- P20 config over code: FINDING A18 (minor); PASS otherwise.
- P21 artifact hygiene: PASS.

Not fully reviewed (context budget): product-brief.md; the domain-spec shards other than invariants.md; architecture-feasibility-report.md; dtu-assessment.md; gene-transfusion-assessment.md; test-vectors.md; risk-register.md. Of the 37 VPs I read only VP-006, 011, 016, 022, 023, 031 and 037 in full, plus every VP's `bcs:` frontmatter.

## 3. Novelty

HIGH. Six HIGH findings (A01, A02, A04, A06, A09, A13) are substantive contradictions or gaps, not wording issues.

NOT_CONVERGED


## Perimeter A2 (remaining cross-cutting docs)

Findings: 28 (high 6, medium 15, low 6, cosmetic 1).

## Adversarial review: Phase 1d, Pass 1, Perimeter A2

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P1-A2-01 | HIGH | Contradiction / settled decision vs parity | state-machines.md:66-71; owner-validation-list.md:211-215; dtu-assessment.md:110; VP-030:51; vs BC-1.04.001:77,109, BC-1.04.014:46-60, BC-1.04.016:42-50 | OD-130 says ±Inf telemetry samples are treated as unknown, like a stale sample. The P1 BCs instead accept `"+Inf"` as a float and render or crash exactly as legacy does (legacy SL:178 calls `float()` on the value). The PRD records no deviation, and no exclusion id exists for this in the closed set. VP-030 cites OD-130 as an invariant it verifies, yet its body tests the legacy crash path. VALID-13 was rated LOW although it changes P1 BCs, which its own header defines as HIGH. One of the two must change. [owner-question] | product-owner |
| ADV-P1-A2-02 | HIGH | Contradiction with BC and legacy | state-machines.md:67 ("NaN samples are dropped"); dtu-assessment.md:109 (fake row 3: `"NaN"` gives "sample dropped") | BC-1.04.001 PC-2 and legacy SL:178 keep `"NaN"` as a float, which is exactly what drives the CP-N01/N02 crash paths (BC-1.04.014/015/016, VP-001). A fake built to dtu row 3 would hide those crash paths from Tier A. | architect |
| ADV-P1-A2-03 | HIGH | VP oracle contradicts its BC (P13) | VP-020:37-45,81-82 vs BC-1.05.004 PC-2/PC-4 and legacy SL:228-237 | VP-020 says an unreadable cost-history file is "left untouched" and that Go "never overwrites an unreadable file". Its skeleton fails if `Record` rewrites the file. The BC and legacy both load `{}` and then save the whole history, which overwrites the corrupt file. Either the VP oracle is wrong, or it encodes a behaviour change that is not in the exclusion set. | architect |
| ADV-P1-A2-04 | HIGH | VP statement contradicts BCs | VP-004:37-41 | VP-004 says `config path` always exits 0 and "no verb/state pair exists outside the table". BC-2.03.002 EC-008/EC-010 make `config path` exit 1 when a directory is unavailable. BC-4.01.001 PC-5 (`help`/`-h`/`--help` prints usage to stdout, exit 0) is also missing. The skeleton only compares goldens against stderr. | architect |
| ADV-P1-A2-05 | HIGH | Wrong oracle: the test would fail a correct implementation | VP-002:32,36,68-71 | The skeleton expects the unknown-flag line for `{"--","x"}`, but BC-4.01.002 EC-004 says arguments after `--` render normally. The statement "any argument beginning with `-`" contradicts EC-005 (a bare `-` is positional). The H1 ("Any argv … renders the unknown-flag error") overclaims and differs from the VP-INDEX name. The test name differs from the BC's `TestStatusline_UnknownFlag`, and the method differs too (the BC says fuzz). | architect |
| ADV-P1-A2-06 | HIGH | P9: VP files disagree with the VP-INDEX coverage map | VP-007:13 (BC-5.04.003); VP-012:13 (BC-1.06.002, BC-3.02.001/002, BC-1.03.018-020, BC-2.02.001-006); VP-019:13 (BC-1.06.001, BC-1.04.020); body partial coverage in VP-002:46, VP-008:45, VP-010:46 | None of these BC→VP links appear in the VP-INDEX map (VP-INDEX.md:98-214). Six VPs (002, 003, 008, 010, 014, 017, 036) have no `bcs:` field at all, so the schema is inconsistent. VP-018/019 frontmatter modules add packages that the catalog row leaves out. | architect |
| ADV-P1-A2-07 | MEDIUM | Missing edge case | VP-001:37-41,72 | VP-001 claims "no fault class exists that yields blank output", but the table only enumerates CP-S, CP-T, CP-N and panics. The corrupt-cost-history shapes (CP-C09/C10, BC-1.05.004 EC-008) are out of parity scope, but they still have to satisfy never-blank/exit-0 (DI-008). No row covers them. | architect |
| ADV-P1-A2-08 | MEDIUM | Unreachable case | VP-017:36-38,68-71 | The skeleton's first assertion builds a zero-backend config. BC-2.01.002 Inv-2 says zero entries cannot happen in P1, because index 0 always exists through its defaults; it becomes reachable only with the P4 file layer. The asserted `Reason` also differs from the BC message `backends=<n> (…)`. | architect |
| ADV-P1-A2-09 | MEDIUM | Assertion can never fail | VP-034:75 | `env["*_proxy"]` looks up a key literally named `*_proxy`, so it can never catch a leaked proxy variable. The skeleton also never checks `-E`, HOME/USERPROFILE or TMPDIR, all of which the statement promises. | architect |
| ADV-P1-A2-10 | MEDIUM | Assertion can never fail | VP-033:76 | `int(start) != int(tc.WantStart)` truncates before comparing. An untruncated start time such as 100.7 passes when 100.0 is wanted, so the whole-second truncation rule the VP claims to verify is never tested. | architect |
| ADV-P1-A2-11 | MEDIUM | Wrong tool usage | VP-024:77-78 | Go native fuzzing (`f.Fuzz`) only accepts primitive argument types, so `func(t, v Value)` will not run. The round-trip check `Decode(Dumps(v)) == v` also fails for NaN unless a NaN-aware equality is specified. | architect |
| ADV-P1-A2-12 | MEDIUM | Oracle gaps and off-by-one | VP-012:38,42-43,81 | The closed set already has 7 ids, so "A seventh exclusion class requires an owner decision" is off by one (it seems to confuse this with the six config classes). The skeleton never checks that `Case` is non-empty or that case-ids are unique, both of which the statement asserts. | architect |
| ADV-P1-A2-13 | MEDIUM | Fix not propagated to sibling files (≥2 files) | VP-012:93, ARCH-07:85 vs BC-2.02.001:162, BC-6.03.004:68, BC-1.01.001:76, BC-1.01.009:85; test-vectors.md:40 | The VPs list five D4-EX-3 class tests (including Theme). The BCs still list four tests and "BC-2.02.001..005", leaving out BC-2.02.006 (boolean, OD-140) and the theme class (OD-134). | product-owner |
| ADV-P1-A2-14 | MEDIUM | Contradiction about who writes the Windows goldens | VP-010:36-38 vs BC-6.03.001:143 | VP-010 says the goldens are "recorded on Linux with `*.windows.golden` variants". The BC says the Windows variants are Python-written "on a Windows oracle run". A Linux run cannot produce ntpath output, so there is no stated oracle for the Windows variants (P18). | architect |
| ADV-P1-A2-15 | MEDIUM | Unexplained threshold; config over code (P16, P20) | VP-018:41-42; risk-register.md:25 (R-001 anchor) | "Retries 2-3 times" is ambiguous, has no rationale, and is neither a config key nor a named constant. `TestCacheStore_OD110_TempCleanup` with `failFirst(1)` then means different things on Windows (the retry succeeds) and on POSIX. "Interrupted save removes its temp" cannot be tested for a killed process; ARCH-04:74 says cleanup happens at the next Save. | architect |
| ADV-P1-A2-16 | MEDIUM | Risk mitigation does not hold | risk-register.md:31 (R-007) | It says setting the removed key is "an ordinary unknown-key config error". BC-2.01.001 PC-6, BC-2.01.002 PC-5 and VP-015:41 say unknown `HYLO_*` settings only produce a stderr warning and never change the output or exit status. | architect |
| ADV-P1-A2-17 | MEDIUM | Settled decision misstated (P12) | bounded-contexts.md:42-43 | It calls DI-007 "permanent per OD-125". OD-125 adopted it "for now with a REVISIT flag" at P7. | business-analyst |
| ADV-P1-A2-18 | MEDIUM | Stale strategy text contradicts rulings (P12) | gene-transfusion-assessment.md:54, :116 | Line 54 says "Go ignores unknown args" with stdlib `flag`, which contradicts OD-112, BC-4.01.002 and VP-002. Line 116 assumes "CPython 3.11 on all CI images", but the Windows leg runs Tier B without Python (VP-010, BC-6.04.001). It also says owner daily use starts "after S8 is green", but OD-107 puts it at P5 cutover. Stories inherit this text. | architect |
| ADV-P1-A2-19 | MEDIUM | L2 contradicts the architecture without a deferral | capabilities.md:31 (CAP-009 "Pure function of stdin + transcript + metrics + caches"); product-brief.md:122; VP-007:47-48 | AD-03, as endorsed in the feasibility report (line 92), explicitly rejects "one pure function". The listed inputs also leave out git state, the process table (⌂), clock and env, all of which are inputs to the `Env` seams. | business-analyst |
| ADV-P1-A2-20 | MEDIUM | Ordering ambiguity | state-machines.md:56-60 (SM-04) | The ladder order reads clean, then degraded, then config-error, then unknown-flag. The PRD and VP-002 say unknown-flag is checked first (E-CLI-001 outranks E-CFG-001), and the config error stops at step 0 before any render. "middle/hydration distinction" is unclear wording. | business-analyst |
| ADV-P1-A2-21 | MEDIUM | Wrong anchors | dtu-assessment.md:107 ("CP-N02 happy path"); VP-030:84 (`cache`/`row1` families) | CP-N02 is the sparkline NaN/+Inf crash path, not the success envelope. ARCH-07:78 defines a `row2` family, but the row-2 VP points to `row1`. | architect |
| ADV-P1-A2-22 | LOW | Glossary does not match the bytes | ubiquitous-language.md:39,46; bounded-contexts.md:61; product-brief.md:74,81 | "Degraded line ≤ 29 bytes for any fault" is wrong: the config-error and unknown-flag rungs are longer, and the BC line is exactly 29 bytes. The exclusion list is described as "D4-EX-1/2/3 + OD-110", leaving out od30, od76 and cp-x03 (OD-136). | business-analyst |
| ADV-P1-A2-23 | LOW | P1 slice incomplete | L2-INDEX.md:110-111 | The P1 slice is listed as CAP-009/010/011 only. CAP-015 (env + defaults config, 13 S2 BCs) is also P1. | business-analyst |
| ADV-P1-A2-24 | LOW | Measurement ambiguity | VP-036:38-39 | With "5 timed runs, nearest-rank p95", p95 is simply the maximum if the 5 samples are per fixture; whether samples are pooled across the corpus is not stated. The >512 KB-line exception promised in product-brief:86 is not stated either. | architect |
| ADV-P1-A2-25 | LOW | Rust terminology (P19) [process-gap] | VP-005/007/012/015/023/024/025 frontmatter `proof_method: proptest` | `proptest` is the name of a Rust crate. The template's enum should name Go tools (testing/quick, rapid, `go test -fuzz`). The BCs' "Send + Sync" (47 files) is the same pattern. | architect |
| ADV-P1-A2-26 | LOW | Subsystem name not verbatim (P6) | architecture-feasibility-report.md:46,51 | "S1 Status line" and "S6 Parity harness" differ in case from the ARCH-INDEX registry names "Status Line" and "Parity Harness". | architect |
| ADV-P1-A2-27 | LOW | Literal invisible character | test-vectors.md:42 | The second "escape" example is a literal invisible code point (grep confirms it), placed right next to the claim that no literal invisible characters are used. | product-owner |
| ADV-P1-A2-28 | COSMETIC | Typos and arithmetic | gene-transfusion-assessment.md:34 ("Sub Setsystem Registry"); owner-validation-list.md:226-232 (Entities 3 but section B has 4 items, VALID-05 counted under "Context boundaries"); entities.md:35 (`{t, v, k, f[, v], p}` repeats `v`) | Cosmetic only. | business-analyst |

### 2. Policy compliance

- **P1 append_only_numbering:** PASS. VP-001..037 and R-001..007 are contiguous, with nothing renumbered or reused.
- **P2 lift_invariants_to_bcs:** PASS within this perimeter. DI-007, DI-008, DI-010 and DI-012 are cited by VPs and BCs; invariants.md itself is outside my perimeter.
- **P4 semantic_anchoring_integrity:** FINDING (ADV-06, 21).
- **P5 creators_justify_anchors:** PASS. capabilities.md §"Why" and the VP Source Contract sections justify their anchors.
- **P6 subsystem names:** FINDING (ADV-26).
- **P9 VP-INDEX is the catalog source of truth:** FINDING (ADV-06).
- **P12 settled decisions are constraints:** FINDING (ADV-01, 17, 18).
- **P13 parity before behaviour change:** FINDING (ADV-01, 03).
- **P14 public-repo hygiene:** PASS. A grep for private IPs, home paths, usernames, emails and session links in the perimeter files came back clean; the `/home/user` examples are synthetic.
- **P16 thresholds are explained:** FINDING (ADV-15).
- **P17 ledger format frozen:** PASS.
- **P18 cross-platform from day one:** FINDING (ADV-14).
- **P19 Go hardening toolchain:** FINDING (ADV-25).
- **P20 config over code:** FINDING (ADV-15).
- **P21 public-artifact hygiene:** PASS.
- **P3, P7, P8, P10, P11, P15:** N.A.

### 3. Files not fully read

None in scope. For VP-032 through VP-036 I skipped frontmatter lines 1-8, which are standard boilerplate; lines 9 to the end were read. Outside my perimeter, I cross-checked BCs only where cited above.

### 4. Novelty

HIGH. Six HIGH findings: three VP oracles contradict their BCs (VP-002, VP-004, VP-020), the OD-130 and NaN handling has not reached the P1 BCs, and VP files disagree with the VP-INDEX coverage map.

**NOT_CONVERGED**


## Perimeter B (BC-1.01, BC-1.02)

Findings: 20 (medium 11, low 9).

## Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P1-B01 | MEDIUM | contradiction / error coverage | BC-1.01.009.md:55,56,58,61 vs BC-1.02.013.md:86,107; BC-1.02.005.md:90-91,109; BC-1.06.001.md:93; legacy SL:311-312, 324, 273-274, 409, 245-255 | **What's wrong:** the step table says steps 3, 4 and 6 cannot degrade, and that 7c degrades only before its write. Other BCs pin degrade vectors at those steps:<br>• Step 3: `effective_rl` with a string `rl_ts` (`now - ts` TypeError, SL:312).<br>• Step 7a: git cache with a string `ts` or a JSON array.<br>• Step 4: `get_sample` raises on a string `fetch_ts` (SL:324).<br>• Step 7c: `cost_thresholds` raises after `record_cost` already wrote, when a history entry is not an object. So PC2 ("none of steps k..8") is wrong there too.<br>**Why it matters:** BC-1.06.001 EC-001 puts these cache-shape crashes (CP-C01..C10) out of parity scope, and the error-taxonomy crash register leaves CP-C out entirely. What Go must do is contradictory, and the VP-008 per-site table can't be written. [owner-question: are CP-C cases in scope?] | product-owner |
| ADV-P1-B02 | MEDIUM | contradiction (arch vs BC) | ARCH-03-statusline.md:49 vs BC-1.01.009.md:54; BC-1.03.013 EC-007, BC-1.03.015 | ARCH-03 says step 2 is "D4-EX-2 skip, no degrade". BC-1.01.009 lists CP-S14/S16 (non-string sid at `re.sub` SL:1017; bad `transcript_path` type at SL:1010) as step-2 degrades, and the BC-1.03 BCs agree. | architect |
| ADV-P1-B03 | MEDIUM | postcondition not true of legacy | BC-1.01.003.md:54,58 (also interface-definitions.md:63, VP-027 line-count property) vs BC-1.02.002.md:54; legacy SL:442,453,1234 | **What's wrong:** "No `\r` is ever emitted" and "At most two rows" are false. Legacy prints stdin `display_name`/`id`/project label verbatim, so `"a\nb"` adds a line and `"a\rb"` emits a CR. A git ref containing `\r` is read with universal newlines (SL:385-386), so it can come back with an LF inside.<br>**Why it matters:** the VP-027 line-count property will fail under fuzzing. The BC needs a carve-out for verbatim input text. | product-owner |
| ADV-P1-B04 | MEDIUM | incomplete precondition | BC-1.02.021.md:79 vs BC-1.02.001.md:88; SL:446 | EC-010 (`id = 42` gives label `42`) holds only with an empty prefix list. Under the default prefix `claude-sonnet` (OD-123), `model_id.startswith` raises AttributeError and the refresh degrades. | product-owner |
| ADV-P1-B05 | MEDIUM | invariant false vs legacy | BC-1.02.025.md:55,111; SL:865-868 | Invariant 1 "never raises" (and the VP "never panics") is false. `float(n)` on an int beyond float range raises OverflowError, which the catch list (TypeError, ValueError) does not cover. `tin`/`tout`/`c_*` are unbounded transcript sums. The same uncaught OverflowError happens at other float-conversion sites that no BC covers: `rb:.0f` (SL:599, BC-1.02.018), `total / 1e6` (SL:435, BC-1.02.006/.020), `reset - now_rl` (SL:515, BC-1.02.011/.012) and `time.time() - win_start` (SL:558, BC-1.02.017). | product-owner |
| ADV-P1-B06 | MEDIUM | spec gap [owner-question] | BC-1.02.026.md:45, BC-1.02.014.md:54-60; SL:853,857 | **Why it matters:** the BC mandates `pyfmt.Int` (int64 with ErrOverflow), which would diverge from legacy on finite values beyond int64 (degrade or wrong text).<br>**What legacy does:** `_fmt_lines` renders them exactly. `int(1e19)` = 10**19, giving `10000000000000.0M`. Ints above about 1.8e314 raise OverflowError at `n / 1e6`.<br>**Owner question:** OD-137 (math/big) covers only the two duration sites. Should it be extended here? | product-owner |
| ADV-P1-B07 | MEDIUM | Policy 16 inconsistency | BC-1.01.003.md:63 vs interface-definitions.md:91; BC-1.02.005.md:129 vs interface-definitions.md:93 | The rationale labels conflict. `narrow_cols` is a "labeled judgment call" in the BC but code `M` (measured, T-014) in the interface table. `git.ttl_s` is "convention" in the BC but `M` (T-013) in the interface table. | product-owner |
| ADV-P1-B08 | MEDIUM | cross-platform parity gap | BC-1.02.004.md:47-48,90,119; SL:380,385 | **What's wrong:** Precondition 2 infers UTF-8 file decoding from `LANG=en_US.UTF-8`. On Windows, CPython 3.11 `open()` with no `encoding` uses the ANSI code page (cp1252), and BC-6.01.002 strips `PYTHONUTF8`. So the Windows oracle decodes invalid bytes in HEAD (EC-010) and non-ASCII branch names differently from Go's strict UTF-8.<br>**Why it matters:** "equals the oracle on all three OSes" can't hold without cp1252 emulation or a named deviation. (Inferred from CPython semantics, not executed.) | architect |
| ADV-P1-B09 | MEDIUM | semantic mis-anchor | prd.md:510, 511, 512 | Three PRD anchors to my BCs point at the wrong behavior:<br>• KD-001 (telemetry strip) cites BC-1.02.009, which is the row-1 plan-limits reroute-all widget.<br>• KD-002 calls BC-1.02.029 the "basis threshold". It is the 0.005 display threshold; the basis threshold is BC-1.05.003.<br>• KD-003 lists BC-1.02.019 (heat cells) under composition. Heat colours belong to the thermometer (BC-1.02.006). | product-owner |
| ADV-P1-B10 | MEDIUM | Policy 20: config key, undefined behavior | BC-1.02.006.md:47-49,55-58,131; also BC-1.02.014.md:47, BC-1.02.025.md:43 | **What's wrong:** these keys are declared, but the postconditions hard-code `pct/10`, `min(…,10)`, `range(10)`, `heat((i+0.5)*10)` and "1e6 → M, else K":<br>• `statusline.context.cells`<br>• `statusline.units.context`<br>• `statusline.units.lines`<br>• `statusline.units.tokens`<br>None of the four appears in the interface-definitions key table.<br>**Why it matters:** what a non-default value does (divisor, cell colours, unit letter) is undefined, so no test can be written for it. | product-owner / architect |
| ADV-P1-B11 | MEDIUM | VP mis-anchor | BC-1.01.008.md:99; BC-1.02.005.md:117; BC-1.02.013.md:114; BC-1.02.030.md:117-118 | Several properties sit under the wrong VP:<br>• "stdout is always valid UTF-8" is anchored to VP-005, which covers stdin decode only, so this property has no home.<br>• BC-1.02.005 and BC-1.02.013 put their Python↔Go cache-swap properties under VP-028 instead of VP-019 (four-cache swap). VP-019's `bcs` lists neither BC.<br>• BC-1.02.030 anchors its sequence-replay property (BC-6.02.002 family) to VP-019 (swap).<br>• BC-1.01.009 cites VP-007 and VP-008 jointly for both properties. VP-007 is determinism, not effect order, so that is a mechanical citation (Policy 5). | architect |
| ADV-P1-B12 | LOW | internal contradiction | BC-1.01.010.md:73 vs BC-1.01.003.md:74 | Invariant 2 says row 2 is trimmed only when `narrow_cols <= COLUMNS < width`. That is false for rows > 2: BC-1.01.003 EC-005 has rows 3, COLUMNS 10 trimming row 2. | product-owner |
| ADV-P1-B13 | LOW | legacy site misstatement | BC-1.02.019.md:70 | For NaN, the ValueError is raised inside `colorsys.hsv_to_rgb` at `i = int(h*6.0)`, not at `int(nan*255)`. The outcome is the same; the cited site is wrong. | product-owner |
| ADV-P1-B14 | LOW | incomplete edge case | BC-1.02.013.md:86; SL:312 | The EC-008 TypeError needs a cached `rl` that is an object (short-circuit `and`). With a non-object `rl` and a string `rl_ts`, the result is None and there is no crash. | product-owner |
| ADV-P1-B15 | LOW | Policy 19 [process-gap] | "proptest" in BC-1.01.001:98, .003:102, .004:85, .006:95-96, .007:87, .008:100, BC-1.02.016:101, .018:106, .019:95, .023:97; "Send + Sync" in BC-1.01.004:141 | Rust tool and trait vocabulary in a Go project. It should be `testing/quick` / `go test -fuzz`. The template's proof-method vocabulary is the likely source. | product-owner |
| ADV-P1-B16 | LOW | vector under-specified | BC-1.01.001.md:89, BC-1.01.008.md:87, BC-1.01.009.md:96 | Vectors with a truthy `session_id` (`s1`) don't pin the window-start probe. Legacy runs the `ps` ancestor walk (SL:276-289) and can add `proc_start` to the same file, so "holding `rl`/`rl_ts`" is ambiguous. | product-owner |
| ADV-P1-B17 | LOW | measurement fragility (pending verification) | BC-1.01.002.md:77-79 | The 993/994 depth limit depends on how deep the Python stack is at `json.load` (C scanner recursion counts with Python frames). The harness's stdio shim (BC-6.01.002) may move the oracle's limit. The BC doesn't say which invocation it measured. | architect |
| ADV-P1-B18 | LOW | inconsistency (pending intent verification) | BC-1.01.001.md:76, BC-1.01.009.md:85 vs error-taxonomy.md:57-62 | The dedicated D4-EX-3 tests are named `{Number,Boolean,URL,Enum}`, but the class register is closed at six (number-range, number-grammar, enum, URL, boolean, theme). | product-owner |
| ADV-P1-B19 | LOW | Policy 21 | BC-1.02.005.md:50 | Quotes the legacy cache-directory literal, which names the private upstream project. It is already public via legacy SL:78. BC-1.06.001 avoids it by citing "SL:78"; this BC should do the same. | product-owner |
| ADV-P1-B20 | LOW | incomplete list | BC-1.01.008.md:53-55; SL:412-413 | The list of string sinks that degrade on a surrogate (CP-S17) leaves out the cached git `branch`. A JSON `\udXXX` escape in the git cache reaches stdout as a str. | product-owner |

## Policy compliance
- P1 append_only_numbering: PASS (001-010 and 001-030 are contiguous; none retired).
- P2 lift_invariants_to_bcs: PASS (DI-007, DI-008 and DI-012 exist and fit).
- P4 semantic_anchoring_integrity: FINDINGS B09, B11.
- P5 creators_justify_anchors: FINDING B11 (BC-1.01.009 mechanical VP-007/008 citation).
- P6 subsystem name: PASS (`SS-01` = ARCH-INDEX.md:53).
- P7 H1 title: PASS (40/40 H1 = BC-INDEX = PRD §BC tables).
- P12 settled decisions: PASS (B01 and B06 are raised as owner questions).
- P13 parity before behavior change: FINDINGS B01, B03, B04, B05, B06, B08, B13, B14, B20.
- P14 public repo hygiene: PASS (vectors are synthetic; placeholder paths `<T>`, `/x/p`).
- P16 thresholds explained: FINDINGS B07, B10.
- P17 ledger format frozen: N.A. (no ledger reads; cache keys match legacy).
- P18 cross-platform: FINDING B08.
- P19 Go toolchain: FINDING B15.
- P20 config over code: FINDING B10.
- P21 public artifact hygiene: FINDING B19.

## Novelty
**HIGH.** Most findings are substantive cross-BC contradictions and legacy-behavior gaps, not wording. **NOT_CONVERGED**


## Perimeter C (BC-1.03, part of BC-1.04/1.05/1.06)

Findings: 8 (high 1, medium 4, low 2, cosmetic 1).

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P1-C01 | HIGH | Missing crash path / spec contradiction | BC-1.03.006.md:53-55; BC-1.03.007.md:51; BC-1.03.010.md:66-68; BC-1.03.018.md:83 vs legacy dgx_statusline.py:1108, 1117, 994, 996 | Mixing a big integer with a float raises Python `OverflowError` ("int too large to convert to float") in four places. (a) `tin`/`c_in` is already a float (for example after `input_tokens: 1.5`) and a later line has a 400-digit integer: SL:1108. (b) `prompt - pp` with `pp` a float: SL:1117. (c) `TURN_STALE * out` or `out / span` with an integer `out` above about 1.8e308: SL:994/996. None of these is among CP-T01..T07. BC-1.03.006 PC3 says only "int + float = float" and never mentions overflow. Yet BC-1.03.018 Inv 3 says hylo "never degrades on any transcript line content". Nobody can write a failing test from this. Either the spec reproduces the sticky degraded line byte for byte, or a new W-predicate is added under D4-EX-2. Choosing between them is an [owner-question]. Searched all specs for "OverflowError" and "too large": no transcript BC covers it. | product-owner |
| ADV-P1-C02 | MEDIUM | Postcondition vs legacy mismatch | BC-1.03.003.md:66 (Inv 3), :75 (EC-004), :96 (VP row "size ≤ the stat size") vs legacy :1049 | An extension read is `fh.read(_READ_CAP)` with no limit at `size`. Only the loop condition checks `size`. If the file grows between the stat and the read, the last extension chunk can pull in bytes beyond `size`. `cut` can then land past `size`, and the written `"size"` can be larger than the stat value. So "bytes appended after it are not read in this refresh" and "size ≤ stat size" are false for extension reads. Only the first read is bounded, by `min(size-off, step)`. | product-owner |
| ADV-P1-C03 | MEDIUM | VP anchor drift (index ↔ body) | BC-1.03.018.md:110-111, BC-1.03.019.md:120-121, BC-1.03.020.md:104-105 (VP-012); BC-1.06.001.md:116-117 (VP-019) vs VP-INDEX.md:122-124, :151 | The BC bodies cite VP-012 (and VP-019 for BC-1.06.001), tagged "(frontmatter closure)". The VP-INDEX coverage map, which is the catalog source of truth, lists only VP-029 and VP-013 for these BCs, and VP-018, VP-001 and VP-022 for BC-1.06.001. The tag is a mechanical label, not a justification. | architect |
| ADV-P1-C04 | MEDIUM | Semantic mis-anchoring (Policy 4/5) | BC-1.03.004.md:105-107; BC-1.03.002.md:106-108 | BC-1.03.004 attaches VP-006 ("Per-call-site JSON depth budgets") to the splitlines differential and skip-state properties. BC-1.03.002 attaches VP-018 (atomic writes) and VP-019 (four-cache swap) to the reset-predicate proptest and the key-order golden. In both, the property described does not match the VP's title. These are rows copied without checking the VP. | architect |
| ADV-P1-C05 | MEDIUM | Config-over-code registry gap (Policy 20) | BC-1.03.003.md:45, BC-1.03.005.md:47, BC-1.03.007.md:44, BC-1.03.009.md:45, BC-1.03.010.md:49-52 | The keys `statusline.transcript.read_cap_bytes`, `statusline.transcript.dedup_memory`, `statusline.tokens.rebuild_excess`, `statusline.composition.image_chars` and `statusline.turn.*` appear only inside BC bodies. Searching all of specs/ finds no schema or registry entry for them in prd-supplements or architecture. BC-1.03.003 points to "the S2 schema (OD-114)" for ranges, but that schema does not list them. The namespaces are also inconsistent: the rebuild threshold is computed inside the transcript parser but sits under `tokens`. | architect |
| ADV-P1-C06 | LOW | Unstated assumption | BC-1.06.001.md:62 vs legacy :192 | The BC says the load reads the file "as UTF-8 text". Legacy calls `open(path)` with the locale's preferred encoding and universal newlines. The two agree on UTF-8 locales. On Windows (cp1252) a foreign cache with non-ASCII bytes would decode differently. The BC should either state UTF-8 as a deliberate choice or note the difference. | product-owner |
| ADV-P1-C07 | LOW | Ambiguity | BC-1.03.020.md:45, :104 vs BC-1.03.018.md:49 | BC-1.03.020 fires the OD-32 rule when "`t0` [is] a number (int or float)". BC-1.03.018 defines "number" as int, float or bool. It is unclear whether a bool `t0` fires the rule. This only arises with foreign caches, but it should be pinned. | product-owner |
| ADV-P1-C08 | COSMETIC | Frontmatter consistency | all BC-1.04.*/1.05.*/1.06.* line 13-22 `extracted_from` | The frontmatter names only the file. BC-1.03.* frontmatter also gives the function and SL range. The bodies do cite line ranges (for example BC-1.04.018.md:94 and the SL references in BC-1.05.004), so Policy 13 is still met. | product-owner |

**Checked and correct:** byte counts and expected values in the test vectors of BC-1.03.002/003/004/005/006/007/011/012/017; all 20 rows of BC-1.03.016 (T1-T20) against SL:988-996 and 1064-1087; all 21 rows of BC-1.03.019 (BASE lr [15.0, true], T05+, T05−, T05~, T06− list, T07±); BC-1.03.020 C1-C3; BC-1.03.021; the epoch 1794650400. I also matched these against legacy: BC-1.04.018 vs SL:773-781, BC-1.05.004 vs SL:224-237, BC-1.06.001 vs SL:190-206 and 1214-1215, and BC-1.03.013/015 vs SL:1009-1017.

**Not fully reviewed (context budget):** BC-1.04.001-017 and 019-021, BC-1.05.001-003 and 005-009, BC-1.06.002. For these I checked only the frontmatter `subsystem`/`capability` fields. A follow-up pass should read them in full.

## 2. Policy compliance

- P1 append_only_numbering: PASS (no renumbering seen; BC-SL-068 is marked replaced in 1.03.018).
- P2 lift_invariants_to_bcs: PASS for the BCs reviewed. DI-007, DI-008 and DI-012 are cited and fit.
- P4 semantic_anchoring_integrity: FINDING C03, C04.
- P5 creators_justify_anchors: FINDING C03, C04 (mechanical "(frontmatter closure)" labels and copied VP rows).
- P6 subsystem name: PASS (every file in the perimeter has `subsystem: "SS-01"`; I did not re-open the registry).
- P7 H1 title: PASS for the BCs reviewed (H1s match their postconditions; the BC-INDEX comparison was not exhaustive).
- P12 settled decisions: PASS (C01's choice of remedy is an owner question).
- P13 parity_before_behavior_change: FINDING C01, C02 (C08 cosmetic). The D4-EX-2 and OD-32 deviations carry their citations.
- P14 public_repo_hygiene: PASS (fixtures synthetic, `msg_A`-style ids, no real data).
- P16 thresholds_are_explained: PASS (T-054..T-061 labeled measured / derived / judgment, with SL citations).
- P17 ledger_format_frozen: N.A. (the transcript and caches are not the ledger; mix-cache key order is pinned).
- P18 cross_platform: PASS (the fd semantics are assigned to `internal/platform`); C06 is a minor Windows note.
- P19 go_hardening_toolchain: PASS (Go tests, proptest and fuzz wording; no Rust tools named).
- P20 config_over_code: FINDING C05.
- P21 public_artifact_hygiene: PASS (no home paths, IPs or usernames found in the files read).

## 3. Novelty

MEDIUM. C01 is a new uncovered crash class and C02 a new legacy mismatch; the rest are anchoring and registry drift. NOT_CONVERGED.


## Perimeter C2 (remaining BC-1.04/1.05/1.06)

Findings: 19 (high 2, medium 7, low 9, cosmetic 1).

**Adversarial review: Phase 1d, Pass 1, Perimeter C2 (29 BCs)**

I re-derived every canonical test vector and the 11-step sequence in BC-1.04.020 by hand from `legacy/dgx_statusline.py`. Nearly all of them hold, including the quirks: the 0.05/0.15/2.35/9.95 ties, the cache key order, the KEEP_DEAD skip on the cached path, and the BC-1.05.008 seed giving 16 dollar values, 14 rates and pairs (24,30)/(20,26). The findings below are what remains.

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P1-C2-01 | HIGH | wrong bytes in test vector | BC-1.05.009:92, :108 vs :71-72; legacy SL:203 | Postcondition 6 says writes use `ensure_ascii` (non-ASCII escaped as `\uXXXX`), and legacy `json.dump` does escape by default. But EC-002 and canonical vector 2 show a raw `"café"` key. The real legacy bytes are `"caf\u00e9"`. EC-003, in the same file, does show the escaped form for its surrogate case. | product-owner |
| ADV-P1-C2-02 | HIGH | contradiction between BCs | BC-1.05.006:74-75 (PC5), :111 (VP-020 row) vs BC-1.03.013:72; legacy SL:1016-1017 | BC-1.05.006 says Go output for a numeric sid equals legacy output for the string sid `"777"`. That is false when a transcript exists. Legacy `re.sub(..., 777)` raises at SL:1017, so the refresh degrades (CP-S14, pinned in BC-1.03.013 EC-007), while the string sid renders normally. Precondition 2 must exclude a present `transcript_path`, and the VP property needs narrowing. | product-owner |
| ADV-P1-C2-03 | MEDIUM | parity gap (redirects) | BC-1.04.001:51, :57, :76; legacy SL:168-171 | `build_opener(ProxyHandler({}))` keeps urllib's default redirect handler, so legacy follows 301/302/303/307/308 and parses the final body. The BC says "exactly one HTTP GET", "at most one request" and "status outside 200-299 → no sample". A Go client built on a bare `Transport` (ARCH-03 `Proxy: nil`) would return no sample on a 302 that legacy follows. The redirect rule needs to be stated. | product-owner |
| ADV-P1-C2-04 | MEDIUM | quirk misstated | BC-1.04.005:71 (EC-007), BC-1.04.001:98 (EC-013); legacy SL:717 | A non-string sample key crashes only if it comes before the first `vllm:` key. `any(k.startswith("vllm:") for k in m)` stops at the first match, so `{"vllm:x":1, 5:1}` renders normally in legacy. Both BCs say "degraded line" without conditions. A related point: on later cached-path refreshes the key has become the string `"5"` and nothing crashes. BC-1.04.004:62-63 (Invariant 3) lists only CP-N01/N02 as crash paths, which also misses this one. | product-owner |
| ADV-P1-C2-05 | MEDIUM | description and VP contradict postcondition | BC-1.04.009:34-35, :100 vs :53-54; legacy SL:663-665 | Legacy slices `hist[-12:]` first and then drops points without the key. The Description says "the last 12 history points that carry it" (filter first), and the VP property "glyph count = min(12, plottable points)" is false when recent points lack the key, for example `f` when TTFT is absent. | product-owner |
| ADV-P1-C2-06 | MEDIUM | dangling anchors (P4), pattern across 29 files [process-gap] | e.g. BC-1.04.001:144 `#metrics-client`, BC-1.04.002:129 `#session-cache`, BC-1.04.004:115 `#row-2`, BC-1.05.001:145 `#cost-segment`, BC-1.05.007:121 `#num`, BC-1.06.002:131 `ARCH-04#cache-store` | ARCH-03 has only 4 headings (lines 15, 43, 64, 116) and ARCH-04 has none of these fragments. None of the Architecture Anchor fragments in this perimeter resolve. The target file is right; the fragment is not. | architect |
| ADV-P1-C2-07 | MEDIUM | mechanical VP citation (P4/P5) | BC-1.04.001:117-119; BC-1.06.002:105-106; BC-1.04.020:104 | VP-022 is "status line never reads the ledger". BC-1.04.001 puts it on all three property rows (map equality, no panic, URL bytes), and lists VP-022 twice per row. BC-1.06.002 likewise attaches VP-012 (exclusion-set closure) to temp-cleanup and stdout-parity properties, which VP-012 does not cover. | product-owner |
| ADV-P1-C2-08 | MEDIUM | missing invariant (P2) | BC-1.05.006:119, BC-1.05.009:124, BC-1.06.002:113 | DI-012 (behavior changes only through named, tested deviations) is exactly what these OD-30 and temp-file deviation BCs carry, but each cites only DI-007. The same gap applies to the D4-EX-3 edge cases in BC-1.04.009/013/020/021. | product-owner |
| ADV-P1-C2-09 | MEDIUM | internal contradiction | BC-1.05.005:151, :154 vs :76 | Purity says "writes via the injected `Store` seam"; Invariant 1 says "Pure function … no write". `cost_thresholds` (SL:240-262) only reads. | architect |
| ADV-P1-C2-10 | LOW | postcondition wording | BC-1.04.013:50-51; legacy SL:1221 | "Set to none unless it is a number and `> 0`" is wrong for NaN. Legacy keeps NaN because `nan <= 0` is false (BC-1.05.003 EC-005 gets this right). The output is the same (`⛏n/a`), but a unit test asserting `dgx_mtok == nil` would contradict legacy. | product-owner |
| ADV-P1-C2-11 | LOW | overbroad invariants | BC-1.04.016:60; BC-1.04.002:69 | Invariant 1 in BC-1.04.016 ("none of these inputs raise") ignores that a NaN/+Inf box rate or TTFT becomes the newest history point (BC-1.04.003 PC4) and triggers CP-N02 in the same render. Invariant 1 in BC-1.04.002 ("never raises") conflicts with BC-1.04.003 EC-009 (IndexError → degraded). | product-owner |
| ADV-P1-C2-12 | LOW | threshold codes conflict between docs (P16) | interface-definitions.md:100 vs BC-1.04.009:46; interface-definitions.md:91 vs BC-1.04.013:42; BC-1.04.009:46 vs pass-4-deep-nfr:42 | interface-definitions assigns T-045 to `sparkline.trace`, but T-045 is the scale (BC-1.04.009). It labels `narrow_cols` "M" while the BC says owner judgment (E-B). The 1e-9 "other" floor is now T-114, yet BC-1.04.009 folds it into T-045. | product-owner |
| ADV-P1-C2-13 | LOW | missing or conflicting rationale labels (P16) | BC-1.04.012:46 (T-108); BC-1.05.003:62 vs :130 (T-044); BC-1.04.002:45 (T-001) | T-108 and T-001 carry no measured/derived/convention/judgment label. T-044 is "judgment" in Traceability but the catalog says D (derived). | product-owner |
| ADV-P1-C2-14 | LOW | config key does not match formula (P20) | BC-1.04.007:42 vs :52-54; BC-1.04.006:42 | `statusline.kv.cells` is declared, but the postconditions hard-code `/25`, `4` and `4-n`, so behavior under a non-default value is undefined. `statusline.queue.yellow` is a "rule" with no stated type or values. | product-owner |
| ADV-P1-C2-15 | LOW | edge case cannot be tested as written | BC-1.04.009:80 (EC-005); BC-1.04.011:67 (EC-001) | EC-005 gives no input values for `▅█`, and EC-001 relies on an unstated `w=900`. | product-owner |
| ADV-P1-C2-16 | LOW | ambiguity | BC-1.05.006:60-62 | "The string JSON would emit as an object key" and "float as Python `repr`" disagree for NaN/±inf sids: JSON emits `"NaN"`/`"Infinity"`, `repr` gives `nan`/`inf`. | product-owner |
| ADV-P1-C2-17 | LOW | mechanical invariant citation (P5) | BC-1.04.017:96, BC-1.04.019:89, BC-1.04.020:114, BC-1.04.021:88 | DI-008 (degraded ladder) is cited on pure format, cache-order and gap contracts that have no fault path. | product-owner |
| ADV-P1-C2-18 | LOW | frontmatter and template drift [process-gap] | BC-1.05.001:19, BC-1.05.003:20, BC-1.05.005:20, BC-1.06.002:18 (and siblings) | These are `origin: greenfield` with `legacy_id`, `extracted_from` and byte-exact parity, while the BC-1.04.x files are `brownfield`. The 1.05/1.06 files also lack the Source Evidence section. | product-owner |
| ADV-P1-C2-19 | COSMETIC | template vocabulary [process-gap] | BC-1.04.003:155, BC-1.04.004:148, BC-1.05.005:154, BC-1.05.009:160, etc. | "Send + Sync" is Rust vocabulary in Go contracts. | product-owner |

## 2. Policy compliance

- **P1** append_only_numbering: PASS. The IDs are contiguous with BC-INDEX; no reuse seen.
- **P2** lift_invariants_to_bcs: FINDING ADV-P1-C2-08.
- **P4** semantic_anchoring_integrity: FINDING ADV-P1-C2-06, -07.
- **P5** creators_justify_anchors: FINDING ADV-P1-C2-07, -17.
- **P6** subsystem name: PASS. All files say `SS-01`.
- **P7** BC H1 vs BC-INDEX: PASS. All 29 titles match exactly.
- **P12** settled_decisions_are_constraints: PASS. OD-30, OD-56, OD-110, OD-138 and D4-EX-3 are respected.
- **P13** parity_before_behavior_change: FINDING ADV-P1-C2-01, -02, -03, -04, -05, -10.
- **P14** public_repo_hygiene: PASS. Only RFC 5737 addresses and synthetic seeds.
- **P16** thresholds_are_explained: FINDING ADV-P1-C2-12, -13.
- **P17** ledger_format_frozen: PASS. The metric name `dgx_llm_last_dgx_request_timestamp_seconds` is kept (D7).
- **P18** cross_platform_from_day_one: PASS. The unexecuted Windows cases in BC-1.06.002 EC-003/005 are honestly flagged for the CI leg.
- **P19** go_hardening_toolchain: PASS. No Rust tools; the Rust wording is cosmetic (ADV-P1-C2-19).
- **P20** config_over_code: FINDING ADV-P1-C2-14.
- **P21** public_artifact_hygiene: PASS. Grepped all 29 files for home paths, private IPs, emails, UUIDs and temp paths: no matches.
- **P3, P8, P9, P10, P11, P15**: N.A.

## 3. Files not fully read

All 29 BC bodies were read in full. Some frontmatter header lines were skipped:
- BC-1.05.002 lines 1-27
- BC-1.05.003 and BC-1.05.005 lines 1-9
- BC-1.05.006 and BC-1.05.007 lines 1-17
- BC-1.05.008 lines 1-17
- BC-1.05.009 lines 1-15
- BC-1.06.002 lines 1-9
- BC-1.04.004 through BC-1.04.021 lines 1-27

From the other documents I read only the sections I needed:
- **Read in part:** interface-definitions §config, ARCH-03, ARCH-04 headings, VP-INDEX rows, the capabilities and invariants rows.
- **Grep only:** error-taxonomy.

## 4. Convergence

Novelty: HIGH. Two vectors or postconditions contradict legacy or another BC (-01, -02), there is a new parity gap on redirects (-03), and the anchor problems run across the whole perimeter.

NOT_CONVERGED


## Perimeter D (S2-S6 BCs)

Findings: 33 (high 6, medium 17, low 8, cosmetic 2).

## 1. Findings

| ID | Sev | Category | file:line | Defect (evidence) | Owner |
|---|---|---|---|---|---|
| ADV-P1-D01 | HIGH | Python parity / self-contradiction | BC-5.01.005.md:58, :80; vs :53, :67; BC-5.02.001.md:60; BC-5.02.002.md:87 (row 63) | PC-4 and EC-008 say `Repr(-0.0)` = `-0`. CPython 3.11 gives `-0.0`. The BC contradicts its own PC-2 (`.0` suffix) and Invariant 2 (round-trip to -0.0). It also contradicts BC-5.02.001 PC-3, which lists `-0.0`, and row 63 (`{"x": -0.0}` = 11 bytes). Dumps uses Repr, so an implementation that passes this vector writes wrong cache bytes. | product-owner |
| ADV-P1-D02 | HIGH | Python parity / wrong vectors | BC-5.01.006.md:72, :73, :75, :84; vs :52; BC-5.01.003.md:100 | Python `max` replaces the current value only when `item > current`. So `max([1, nan, 2])` is `2` and `max([1, 2, nan])` is `2`, but EC-003, EC-004 and the canonical row say `nan`. These rows contradict the BC's own PC-2 and the BC-5.01.003 VP `Max(a, NaN) == a`. EC-006 `max([True, 1])` returns `True` (first wins on a tie), not `1`; the row contradicts its own "tie keeps the first" note. | product-owner |
| ADV-P1-D03 | HIGH | Settled decision contradicted (P12) | BC-6.04.003.md:36 (H1), :50-51, :86-89; OD log :119; VP-011:46-48 | OD-149: the Tier C exit is ONE clean nightly run on all three OSes, 30 min per OS. The BC (title included) says Linux only, "N consecutive nights, N picked by the owner, research proposes 3, not decided here". VP-011 already carries OD-149. | product-owner |
| ADV-P1-D04 | MEDIUM | Contradiction with OD-01 / BC-2.01.001 | BC-3.02.001.md:76-77; vs BC-2.01.001.md:71-73; also prd.md:615-616 | BC-3.02.001 says setting the removed key `ps_timeout_s` "now raises an ordinary unknown-key config error". OD-01 and BC-2.01.001 PC-6 say an unknown `HYLO_*` variable is ignored with a stderr warning, never a config error. The PRD repeats the same wrong claim. | product-owner |
| ADV-P1-D05 | MEDIUM | Cross-BC contradiction (harness) | BC-6.01.002.md:62, :102-103; vs BC-3.02.002.md:45-46; BC-3.02.001.md:83-84; vs BC-3.02.002.md:53-54, :62-67 | BC-3.02.002 needs a fake `ps` on the oracle's PATH and byte-compares unseeded I1-I6 cases. BC-6.01.002's exact oracle env set has no `PATH` key at all. BC-3.02.001 Invariant 4 says parity cases always seed `proc_start`, which makes the BC-3.02.002 rows impossible. | product-owner |
| ADV-P1-D06 | HIGH | Interface mismatch BC ↔ ARCH-06 | ARCH-06-pyfmt.md:62, :66-69, :72, :91; vs BC-5.01.003.md:49-50, :53-55; BC-5.01.006.md:50; BC-5.03.002.md:52-53; BC-5.01.001.md:41 | `Int`/`Ceil` return `(int64, error)`, which cannot hold the exact big integer the BC requires (EC-006 `Int(1e300)`). `FloorDiv`/`Mod` have no error return, but the BC requires `ErrZeroDivision`. `MaxSeq` has no error return, but the BC requires `ErrValue` on empty input. `RSplit1` returns `string`, but the BC returns a list. `Round(x Num)` differs from the BC's `Round(x float64)`. `FloorDivInt`/`ModInt` are absent. | architect |
| ADV-P1-D07 | HIGH | Mis-anchoring (P4/P6) | BC-6.01.002.md:162; BC-6.02.001.md:127; BC-6.02.002.md:132; BC-6.02.004.md:128; BC-6.03.002.md:130; BC-6.04.002.md:56, :127; ARCH-INDEX.md:58 | The "Architecture Module" rows name `internal/statusline` parity harness components. The same rows cite BC-COMPONENT-MAP `internal/parity/*.go`, and the registry gives SS-06 = `internal/parity` (OD-148). Each row contradicts itself; 6 files. | product-owner |
| ADV-P1-D08 | MEDIUM | Internal inconsistency | BC-2.02.006.md:46, :69, :100 | Invariant 1 and the VP say the grammar is a "seven-token set", but the grammar has six tokens. Precondition 1 cites "BC-2.01.005 postcondition 2" for the bool keys; the bool grammar is PC-1 there. "the other registry Bool entries" is never enumerated. | product-owner |
| ADV-P1-D09 | HIGH | Partial-fix propagation (OD-140) | BC-2.02.001.md:51, :100, :170-172; BC-6.03.004.md:68 | BC-2.02.006 was added for the boolean class. BC-2.02.001 still names the class contracts "BC-2.02.002..005", attributes the boolean reason to BC-2.01.005 only, and leaves 2.02.006 out of Related BCs. The BC-6.03.004 D4-EX-3 row still says "BC-2.02.001..005". Blast radius: 2 files. | product-owner |
| ADV-P1-D10 | MEDIUM | Contradiction BC ↔ interface-definitions | interface-definitions.md:90; vs BC-2.02.003.md:65-68, :88 | `statusline.rows` has range `>= 0` in interface-definitions, but BC-2.02.003 says "any int64" and EC-009 makes `-1` valid. Either `-1` is a config error or it is not; you cannot write one test for both. | product-owner |
| ADV-P1-D11 | MEDIUM | Contradiction BC ↔ interface-definitions | interface-definitions.md:67, :102; vs BC-2.01.003.md:83-85; BC-2.02.001.md:117-119; BC-2.01.004.md:82-85 | interface-definitions says the degraded line's grey/reset come from `statusline.theme.*`. BC-2.01.003 PC-5 and BC-2.02.001 Inv 2 make the grey pair a built-in named constant. interface-definitions also claims three default exceptions; BC-2.01.004 PC-4 lists exactly two (`metrics_url` equals legacy). | product-owner |
| ADV-P1-D12 | MEDIUM | Underspecified error line | BC-2.01.002.md:66-71; BC-2.02.001.md:70-74, :77-79; BC-2.03.001.md:75 | The backends error prints `backends=<count>`. BC-2.02.001 PC-3 says `<value>` is the raw supplied string, and `[from <ENVNAME>]` = `EnvName(key)` would give `HYLO_BACKENDS`, yet BC-2.03.001 EC-005 shows `HYLO_BACKENDS_1_METRICS_URL`. Not specified: which variable is named when several `i≠0` indices exist, and whether `HYLO_BACKENDS_1_FOO` (unknown field) also warns. | product-owner |
| ADV-P1-D13 | MEDIUM | Inconsistent vector | BC-2.03.002.md:92; vs :67-70, :94 | PC-4 writes one stderr line per unavailable line (EC-010 shows "twice"). EC-008 has all three lines unavailable but lists a single stderr line. The `<VAR>` named for a `~` override on Windows (USERPROFILE) is unspecified. | product-owner |
| ADV-P1-D14 | MEDIUM | Boundary not pinned | BC-5.02.003.md:64-71, :94 | Depth is pinned as "995 accepted / 1,000 rejected", which leaves 996-999 undefined. EC-010 demands limit / limit+1. The stdin site is pinned exactly (993/994). | product-owner |
| ADV-P1-D15 | MEDIUM | Python formatting edge underspecified | BC-5.02.005.md:52-53 | Container repr says only "single quotes". CPython `repr(str)` switches to double quotes when the string contains `'` and not `"`. It also escapes non-printables (`\x..`, `\u....`, lone surrogates) by `isprintable`. Stdin can reach this (a list as `display_name`, `["it's"]`), and the BC does not pin these rules. | product-owner |
| ADV-P1-D16 | MEDIUM | Harness fail-open | BC-6.03.003.md:70-73, :100-101 | The temp filter `^.+\.json\.[A-Za-z0-9_]+$` matches the named cache `statusline-q.json.json` (sid `q.json`). That contradicts "no named cache matches" and Invariant 1, and could hide a missing or extra named cache (fuzzed or synthetic sids). | product-owner |
| ADV-P1-D17 | MEDIUM | Harness machinery underspecified | BC-6.03.004.md:55-61, :86-88, :91-94, :125; BC-6.03.002.md:79-82, :104 | Entries have no package key, so `go test -list` has no package to look in (the tests live in config, platform and statusline). One `expected_output_file` cannot hold "stdout plus named caches"; its format is undefined. In a D4-EX-3 case legacy writes caches and Go writes none, and the scope is ambiguous. EC-006 is impossible: a config-error run never reaches the probe. | product-owner |
| ADV-P1-D18 | MEDIUM | Missing input spec (harness) | BC-6.02.002.md:49-56; BC-6.02.003.md:68-70 | Captured-session steps define no metrics source: no per-step reply and no mode. Without one, both sides hit the default unroutable URL, and the 1.5 s timeout flakiness that BC-6.02.003 bans returns. | product-owner |
| ADV-P1-D19 | MEDIUM | Public hygiene gate gap (P14) | BC-6.02.001.md:70-78 | `TestCorpusHygiene` scans only `internal/statusline/testdata/`. It skips `internal/pyfmt/testdata/`, `internal/config/testdata/` and `cmd/hylo/testdata/`. It also has no username or hostname patterns, both CLAUDE.md categories. | product-owner |
| ADV-P1-D20 | MEDIUM | Rust tooling in a Go spec (P19) [process-gap] | e.g. BC-2.01.001.md:113, :155; BC-5.01.001.md:99-101; 63 hits across 34 perimeter files | Proof methods say "proptest" (a Rust crate), and purity tables say "Send + Sync" (Rust traits). The Go equivalents are testing/quick or rapid, and goroutine-safety wording. This is a systematic template leak. | product-owner |
| ADV-P1-D21 | MEDIUM | OS-specific logic outside internal/platform (P18) | BC-2.01.005.md:62-64, :114; BC-2.01.001.md:47-48; BC-5.03.004.md:42; ARCH-06-pyfmt.md:96; ARCH-02 :34-35 | Three per-OS behaviors are specified outside `internal/platform`: the Windows `~\`/USERPROFILE expansion (in `internal/config/types.go`), case-insensitive env matching (`Load` over a map), and the `runtime.GOOS` flavor choice inside `pyfmt` (one `Basename`, no flavor parameter). None is routed through `internal/platform` or build tags. | architect |
| ADV-P1-D22 | MEDIUM | Product behavior unspecified | BC-6.01.003.md:78-81; BC-5.04.003.md:46-47; BC-2.01.001.md:73-75 | The shipped binary honors `HYLO_TEST_NOW`, but no BC says what a malformed value does (config error, ignored, or degraded), nor whether a stray value in a user's shell freezes the clock silently. | product-owner |
| ADV-P1-D23 | LOW | Legacy citation (P13) | BC-6.01.002.md:73-75; BC-6.02.003.md:78-80; vs legacy SL:89 | "SL:73-79, 92" is cited for the legacy env names. `DGX_SL_TRACE` is at SL:89; SL:78-79 are CACHE_DIR/STALE_OK; SL:92 is a comment. | product-owner |
| ADV-P1-D24 | MEDIUM | Mis-anchor (non-existent key) | BC-6.02.003.md:136; vs BC-2.01.003.md:55-69 | EC-007 cites `statusline.theme.sgr.*`. No such family exists; the keys are `statusline.theme.<role>`. | product-owner |
| ADV-P1-D25 | LOW | Cross-BC semantics | BC-2.01.005.md:67-68; vs BC-2.03.002.md:56, :91 | BC-2.01.005 applies "the same rule" (`""` gives `empty path`) to `HYLO_CONFIG`. BC-2.03.002 ignores an empty `HYLO_CONFIG`. | product-owner |
| ADV-P1-D26 | LOW | Vectors not byte-exact | BC-5.02.004.md:73-74; BC-5.03.001.md:68; BC-5.03.002.md:71; BC-5.02.001.md:87 | Glyphs are shown where escapes are meant. Dumps prints `"\ud83d\ude00"`, not a raw emoji. EC-004 "JSON escapes" shows a raw emoji. Cells contain literal invisible or ambiguous characters (combining-vs-precomposed é, U+3000, the blank EC-002 cell). | product-owner |
| ADV-P1-D27 | COSMETIC | Table broken | BC-5.01.002.md:84, :88 | The note paragraph is duplicated mid-table, which orphans the EC-007/EC-008 rows. | product-owner |
| ADV-P1-D28 | COSMETIC | Wrong annotation | BC-5.01.005.md:77 | `5e-324` has a one-digit mantissa, not "four-digit". | product-owner |
| ADV-P1-D29 | LOW | Unexplained thresholds (P16) | BC-5.01.004.md:46; BC-5.01.001.md:42-43; BC-6.04.002.md:62-63, :102 | These bounds have no labeled rationale: width ≤ 67, n ≤ 17, prec ≤ 20, R = 5 timed runs, 1 warm-up, and the `n < 20` low-sample note. | product-owner |
| ADV-P1-D30 | LOW | Traceability incomplete (P5) | BC-5.04.003.md:93-98; BC-6.04.002.md:126 vs :130 | BC-5.04.003 has no L2 Domain Invariants row and no Architecture Module row. BC-6.04.002 lists DI as "—" while its anchor note claims DI-012. | product-owner |
| ADV-P1-D31 | LOW | Wrong call-site claim | BC-5.03.004.md:86; vs legacy SL:454 | "Empty cwd still renders a label `.`" is wrong at the call site: `if proj_dir:` skips the label when the directory is empty. | product-owner |
| ADV-P1-D32 | LOW | Wrong claim | BC-3.02.001.md:65-66; vs legacy SL:278-290 | "pid 1 is never examined" is false when `Getppid()==1`. Both legacy and the Go walk probe startPID first. | product-owner |
| ADV-P1-D33 | LOW | Class count drift (pending intent verification) | BC-2.02.006.md:36; VP-016 title; vs BC-2.02.001.md:107-109 | BC-2.02.006 and VP-016 say "six classes". The BC-2.02.001 vocabulary adds `path` and `backends` classes, which have no class contract or D4-EX-3 test. | product-owner |

## 2. Policy compliance
- P1 append_only_numbering: PASS.
- P2 lift_invariants_to_bcs: PASS for this perimeter (DI-008/010/012 exist and fit). Minor gap in D30.
- P4 semantic_anchoring_integrity: FINDINGS D07, D24, D33.
- P5 creators_justify_anchors: FINDING D30. Otherwise PASS (OD-153 rationale notes are present).
- P6 subsystem source of truth: PASS (SS-02..06 match ARCH-INDEX). Module rows conflict, see D07.
- P7 H1 title source of truth: H1 ↔ BC-INDEX PASS for all 52. H1 accuracy FINDING D03 (BC-6.04.003).
- P12 settled decisions: FINDINGS D03 (OD-149), D04 (OD-01).
- P13 parity before behavior change: FINDINGS D01, D02, D23, D31, D32.
- P14 public repo hygiene: FINDING D19. No flagged strings found in the perimeter.
- P16 thresholds explained: FINDING D29.
- P18 cross-platform: FINDING D21.
- P19 Go hardening toolchain: FINDING D20.
- P20 config over code: PASS, with D22 noted (test hook in the product binary is unspecified).
- P21 public artifact hygiene: PASS. No home paths, LAN IPs, usernames or session IDs in the perimeter; only 192.0.2.x, /home/user, /t/h placeholders.
- P3, P8-P11, P15, P17: N.A.

## 3. Novelty
HIGH. NOT_CONVERGED.

