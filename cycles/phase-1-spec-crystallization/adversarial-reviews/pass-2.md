---
document_type: adversarial-review
phase: 1d
pass: 2
date: 2026-11-17
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 116
---

# Adversarial Spec Review — Phase 1d, Pass 2

Pass 2 ran as six fresh-context perimeters (A, A2, B, C, C2, D), the same split as pass 1, because the spec corpus under review (~1.4 MB) exceeds a single agent context. Each perimeter was re-reviewed by an independent fresh-context adversary with no visibility into the other perimeters. Each section below is the verbatim final report of one perimeter, unedited except for this framing and one disclosed normalization: perimeter C's closing file list spells the repo root as an absolute path; it is reproduced repo-relative, as policy 21 requires. Per-perimeter novelty rulings: A HIGH, A2 HIGH, B MEDIUM, C MEDIUM, C2 MEDIUM, D MEDIUM — aggregated as MEDIUM at pass level; the pass is NOT_CONVERGED (116 findings: 17 HIGH / 58 MEDIUM / 35 LOW / 6 COSMETIC, against 129 in pass 1).


## Perimeter A (cross-cutting)

Findings: 26 (high 4, medium 15, low 6, cosmetic 1).

## Perimeter A — Pass 2 findings

All files in Perimeter A were read in full. BC and VP files were opened only to check specific cross-references.

### 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P2-A01 | HIGH | Interface can't express a BC | architecture/ARCH-02-configuration.md:67-69 | `Load(...) (*Config, *Error)` returns one `Error{Key,Value,Reason,EnvName}`. BC-2.02.001 needs the full error list on stderr in registry order, and BC-2.03.001 / E-VAL-001 prints one reason line per error. A single error can't carry either. | architect |
| ADV-P2-A02 | HIGH | Interface can't express a BC | ARCH-01-binary-cli.md:25-32; ARCH-03-statusline.md:82; ARCH-02:38-39 | The only env seam is `getenv func(string) string`. That cannot list variables, so it can't find unknown `HYLO_*` settings (BC-2.01.001 PC-6) or any `HYLO_BACKENDS_<i>_*` (BC-2.01.002 PC-4/PC-6). It also can't tell "set but empty" from "unset" (BC-2.01.002 PC-3: empty list vs default). Separately, `platform.EnvLookup` goes around the injected seam, so Windows env behaviour can't be faked in tests. | architect |
| ADV-P2-A03 | HIGH | Concurrency / data loss | ARCH-04-data-files.md:73-74 (VP-018:39, :100-106) | Every Save deletes all stale temp files, with no age or owner check ("one save, any sid"). Several Claude Code windows render at once and share `cost-history.json` and the git cache. One process can delete another's in-flight temp; on POSIX that process's rename then fails with ENOENT and its write is silently lost. | architect |
| ADV-P2-A04 | HIGH | P9: VP catalog drift | prd-supplements/module-criticality.md:49-63 | VP counts are out of date. VP-038 (internal/statusline, VP-INDEX:94) is missing and the "37/37" note is stale. The S1 row lists VP-020, which is internal/cost only (VP-INDEX:76), and omits VP-019 (statusline cache.go, VP-INDEX:75). The cost row omits VP-018 and VP-021 (VP-INDEX:74,77). The CLI row omits VP-001, VP-003 and VP-016, all of which name cmd/hylo (VP-INDEX:57,59,72). | product-owner |
| ADV-P2-A05 | MEDIUM | Contradiction / ambiguity | ARCH-02:76-81 (copies BC-2.01.002:66-77) | One sentence says "any field name" at index ≠ 0 creates an extra entry, which is an error. The next says a field that isn't a P1 key "warns as an unknown setting for every index". For `HYLO_BACKENDS_1_NAME` it is unclear whether the result is an error, a warning, or both. Where the `backends=` error sits in registry order (which decides which error gets rendered) is also undefined. | architect, product-owner |
| ADV-P2-A06 | MEDIUM | Contradiction | ARCH-06-pyfmt.md:28 | Says ModeText "serves both stdin and cache/transcript loads". BC-1.03.004:38,44, BC-5.02.003:36 and VP-006:38 put transcript lines on ModeBytes, and the 989 constant ARCH-06 names belongs to that ModeBytes site. | architect |
| ADV-P2-A07 | MEDIUM | Missing value | ARCH-06:28, :93-96; prd.md:562 | `Decode` needs a depth budget for every call site, but only stdin (993) and `_mix_counts` (989) are pinned. The four cache-load sites (ModeText per VP-006:38 and ARCH-04:43) have no value, so implementers would have to invent one. | architect |
| ADV-P2-A08 | MEDIUM | Interface ambiguity | ARCH-03:47, :70, :83; ARCH-01:36 | Step 0 ("config resolved", which renders the D4-EX-3 line) is inside the `Render` script. But `Main` receives `Env.Config` already resolved as a non-error `*config.Config`. It is unclear who emits E-CFG-001 and who guarantees "no cache writes". | architect |
| ADV-P2-A09 | MEDIUM | Contradiction | ARCH-07-parity-harness.md:32-33 | Says Tier B goldens are "written by Python on Linux". BC-6.03.001:143 says `.windows.golden` files are Python-written on a Windows oracle run. | architect |
| ADV-P2-A10 | MEDIUM | Misleads Phase 2 ordering | module-criticality.md:95-113 | The build order puts config (2) before platform (3), and the graph leaves out cfg→plat, cmd→cfg, cmd→plat and internal/cost. ARCH-00:49-63 and ARCH-02:36-42 show config imports platform, so this order can't be built. | product-owner |
| ADV-P2-A11 | MEDIUM | Contradiction | prd.md:113, :126 | PRD gives S3 Platform priority MEDIUM; module-criticality.md:52 and ARCH-05:19 give it HIGH (≥ 90%). prd.md:126 says "coverage ≥ 95%" where the supplement defines a mutation kill rate. | product-owner |
| ADV-P2-A12 | MEDIUM | P20 / DI-010 totality | prd-supplements/interface-definitions.md:120-124, :108-109 | Some keys are "default-only": `kv.cells`, `context.cells`, `units.context`, `queue.yellow` are accepted as valid but non-default behaviour is "undefined". So `HYLO_STATUSLINE_KV_CELLS=8` passes validation into undefined behaviour. Also, `units.lines` and `units.tokens` are typed Text but carry two units plus two thresholds, which one Text key can't hold. [owner-question] | product-owner |
| ADV-P2-A13 | MEDIUM | P16 / P20 | ARCH-04:62 | ARCH-04 says "2-3 short retries"; VP-018:45 says exactly 2 (`renameRetryLimit`). The delay between retries is never given: no named constant, no rationale. | architect |
| ADV-P2-A14 | MEDIUM | Contradiction with repo | ARCH-08-build-ci-release.md:23 | Claims go.mod has `go 1.26.0` plus a toolchain line. The actual go.mod:3 is only `go 1.26.0` (cicd-setup.md:31 agrees). With `go-version-file`, CI installs 1.26.0, not the latest 1.26.x patch, so the "Go 1.26.x leg" runs the oldest patch, without later stdlib security fixes. | architect, devops-engineer |
| ADV-P2-A15 | MEDIUM | P11: CI can pass while checking little | ARCH-08:57-58, :65; cicd-setup.md:73, :77 | Tier A fails only when N == 0, so losing part of the corpus still passes; N should equal the number of case directories found, as the exclusions check does with M. For the test job, `go: K files scanned` counts source files, not tests run, so a suite where every test skips passes. [process-gap] | architect |
| ADV-P2-A16 | MEDIUM | NFR not executable | nfr-catalog.md:24, :55-58; ARCH-08:48-50 | The binding p95 gate runs only with `HYLO_TIMING_GATE=1`, which no job or written procedure sets, so nothing says when the owner-Mac gate runs for P1 exit. Also, with 1 warm-up + 5 runs, nearest-rank p95 of 5 samples is just the maximum, and whether p95 is pooled across cases is not stated. | product-owner |
| ADV-P2-A17 | MEDIUM | Contradiction | prd.md:72-73, :556-558 | DI-012 says behaviour may differ "only via named, tested exclusions", from a closed set. BC-1.01.009:65-68 (ruling Q-b) declares Go's handling of foreign cache shapes a "documented known difference" that is not in that set. [owner-question] | product-owner |
| ADV-P2-A18 | MEDIUM | P4: mis-anchor | ARCH-00-overview.md:93 | Cites "AD-01 classes S1/S5" for the ≥ 95% mutation target. AD-01 is the single-binary decision; the target comes from OD-135 and module-criticality. | architect |
| ADV-P2-A19 | MEDIUM | P19: unrecorded dependency | ARCH-06:54 | Adds `github.com/flyingmutant/rapid` as a go.mod test dependency. ARCH-08:29 requires an ADR line in ARCH-INDEX for each new dependency, and ARCH-INDEX has none (AD-02 still says x/sys is the only one). No gremlins version is pinned. | architect |
| ADV-P2-A20 | LOW | Wrong claim | nfr-catalog.md:28; prd.md:455 | Says "No other cap exists in legacy", but legacy/dgx_statusline.py:83 `SPARK_MAX_AGE = 90.0` is a history age cap (BC-1.04.003 "90 s cap"). | product-owner |
| ADV-P2-A21 | LOW | P4: mis-anchor | prd.md:64 | Environment seams are cited as AD-03; the Env seam set is AD-10 (ARCH-INDEX:81). | product-owner |
| ADV-P2-A22 | LOW | Stale anchor | ARCH-08:82 | Cites "PRD §9.5", which does not exist; the intended target is ASM-005 (prd.md:586). | architect |
| ADV-P2-A23 | LOW | Ambiguity | ARCH-07:91 | Five D4-EX-3 class test names cover six closed classes (number-range and number-grammar share `Number`). Confirm this is intended. | architect |
| ADV-P2-A24 | LOW | Stale status | cicd-setup.md:17-24, :33 | Says the workflows are uncommitted in `.worktrees/ci-phase-1-setup`. That worktree no longer exists, and `.github/workflows/*.yml`, go.mod and .gitleaksignore are in the repo root. Also, the ci.yml:343-348 timing placeholder just echoes text and passes once internal/statusline exists. | devops-engineer |
| ADV-P2-A25 | LOW | Interface drift | ARCH-03:93 | `CacheStore.Save` returns nothing, but the VP-018:87,94 test skeleton checks an error returned by Save. | architect |
| ADV-P2-A26 | COSMETIC | Editorial | ARCH-00:104-109; ARCH-02:84-85; ARCH-06:20 | Duplicated bullet, duplicated line, and garbled header text ("strconv-only-on-finite-banned"). | architect |

### 2. Policy compliance
- **P1 append_only_numbering:** PASS (no renumbering or reuse seen; S7–S12 and SS-IDs kept).
- **P2 lift_invariants_to_bcs:** PASS for the P1 DIs (007/008/010/012/017 have enforcers); the deferred DIs are out of P1 scope.
- **P4 semantic_anchoring_integrity:** FINDING A18, A21, A22.
- **P5 creators_justify_anchors:** PASS.
- **P6 subsystem names:** PASS (PRD §1.6 matches the ARCH-INDEX registry word for word).
- **P7 BC H1 is title source:** PASS (22 sampled H1s match the PRD rows).
- **P9 VP-INDEX is VP source:** FINDING A04 (ARCH-INDEX totals and homes do agree).
- **P11 ci_positive_coverage_assertion:** FINDING A15, A24 (current ci.yml prints no coverage lines yet; the deferral is disclosed).
- **P12 settled_decisions_are_constraints:** PASS (challenges are tagged [owner-question]: A12, A17).
- **P13 parity_before_behavior_change:** FINDING A03 (cleanup goes beyond the ruled own-temp cleanup), A17.
- **P14 public_repo_hygiene:** PASS (grep for private IPs, home paths and emails across the perimeter found nothing).
- **P16 thresholds_are_explained:** FINDING A13, A16.
- **P17 ledger_format_frozen_until_cutover:** PASS.
- **P18 cross_platform_from_day_one:** PASS, with a note (the `Basename` GOOS exception is justified; the seam bypass is covered under A02).
- **P19 go_hardening_toolchain:** FINDING A14, A19.
- **P20 config_over_code:** FINDING A12, A13.
- **P21 public_artifact_hygiene:** PASS.
- **P3, P8, P10, P15:** N.A.

### 3. Files not fully read
None in the perimeter. These were read only for spot cross-checks: BC-2.01.002, BC-1.01.009, BC-1.06.002, BC-1.04.001, BC-6.04.001, BC-6.03.001, VP-INDEX, VP-006, VP-018, invariants.md, legacy/dgx_statusline.py, .github/workflows/ci.yml, go.mod.

### 4. Novelty
Novelty is **HIGH**. A01–A03, A06–A08, A14 and A15 are new interface, concurrency and toolchain defects, not rewordings of earlier findings. **NOT_CONVERGED**.


## Perimeter A2 (remaining cross-cutting docs)

Findings: 29 (high 4, medium 17, low 7, cosmetic 1).

1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P2-A2-01 | HIGH | contradiction / parity | domain-spec/state-machines.md:70-74; dtu-assessment.md:110; VP-030:37-43,51 vs behavioral-contracts/ss-01/BC-1.04.014.md:46,58-60,67-69 | OD-130 says ±Inf samples are "unknown, like a stale sample". BC-1.04.014 instead keeps legacy behaviour: +Inf on `v`/`f` degrades, -Inf clamps to `▁`. VP-030 cites both, and no BC cites OD-130. If OD-130 were implemented, Tier A would show a diff that has no exclusion id (OD-130 is not in the closed set). Fixing NaN in pass 1 (ADV-P1-A2-02) left +Inf unreconciled. [owner-question]: does OD-130 override parity, which would need an 8th exclusion id, or is it scoped out of P1? | product-owner |
| ADV-P2-A2-02 | HIGH | VP skeleton fails a correct implementation | VP-012:38,80-81; VP-009:41 | The closed-set map uses `"od30"`/`"od76"`. BC-6.03.004:56,81 and BC-1.05.006:134 require ids `OD-30`/`OD-76`. ARCH-07:42, PRD:73, the brief and UL all agree with the BC. The skeleton would flag a correct `exclusions.json` as "foreign exclusion id". | architect |
| ADV-P2-A2-03 | HIGH | H1 vs body | VP-020:33 (title, also VP-INDEX:76) vs VP-020:37-47; VP-018:58-60 | The title says "no wipe on parse failure". The body says the next record overwrites the corrupt file, as legacy does. VP-018 says "parse failure never destroys the file", which contradicts VP-020 and is false for any cache saved after an empty load. | architect |
| ADV-P2-A2-04 | HIGH | P9/P4 residual drift [pattern] | VP-INDEX.md:299-306; VP-002:51 vs :13; VP-008:46 vs :13 | VP-INDEX reports, but does not resolve, 7 BCs whose bodies do not anchor the VP that claims them. It also notes BC-1.03.004 still says "no VP yet" although VP-038 now covers it. VP bodies also name partial-coverage BCs missing from their `bcs:` (VP-002→BC-4.01.001, VP-008→BC-1.06.002). That is 8+ BCs, so this is a systematic pattern, a partial-fix regression from pass 1. | product-owner |
| ADV-P2-A2-05 | MEDIUM | VP oracle wrong | VP-038:39,61-63,86 vs legacy dgx_statusline.py:1059 | The VP says "ends-retained pieces", but legacy calls `blob[:cut].splitlines()` (keepends=False). The skeleton asserts no piece contains `\r`/`\n`, which fails an ends-retained implementation. The reconstruction oracle depends on `terminatorOf(b,p,i)`, which cannot be derived from pieces alone. The title says "differential", but there is no live differential. | architect |
| ADV-P2-A2-06 | MEDIUM | VP skeleton fails a correct implementation | VP-022:42-44,89 vs legacy dgx_statusline.py:369-389; dtu-assessment.md:74 | The allowed path set is transcript, caches and cost history. The render also reads `.git`/HEAD files up the ancestor walk (the git widget), so `TestEnvScope_AllowedPathSet` fails a correct port. | architect |
| ADV-P2-A2-07 | MEDIUM | test cannot fail a wrong implementation | VP-016:37-38,82-91 | There are six classes but `TestConfigError_D4EX3_Number` runs only `numberRangeRows`, so number-grammar (BC-2.02.003) has no table. The `FirstErrorRegistryOrder` body is not valid Go and, as written, fails when the order is stable. | architect |
| ADV-P2-A2-08 | MEDIUM | vacuous oracle | VP-015:37-43,79-85 | The skeleton only checks that `Load` returns exactly one of a config or an error. A silent fallback (invalid value replaced by its default, which returns a config) passes, and that is the core DI-010 claim. The claims that unknown `HYLO_*` warns and `DGX_*` is never read are not asserted. | architect |
| ADV-P2-A2-09 | MEDIUM | wrong method / vacuous | VP-012:15,59-68,78-92; VP-INDEX:68 | Catalogued as property/fuzz, but there is no generator. The checks are reimplemented in the test and run against the committed file. The production harness's fail-closed rejections (glob, foreign id, missing test, duplicate) are never driven with mutated exclusion files, so a harness that validates nothing still passes. | architect |
| ADV-P2-A2-10 | MEDIUM | wrong oracle | VP-023:75 | The divmod identity is written `a*b ≡ FloorDiv*a + Mod*a`. The correct form is `a == b*FloorDiv(a,b) + Mod(a,b)`, and for floats it holds only approximately. A test built from the line as written would fail a correct implementation. | architect |
| ADV-P2-A2-11 | MEDIUM | skeleton does not compile or run | VP-002:86-88 | `f.Fuzz(func(t *testing.T, flags ...string))`: Go fuzzing does not accept variadic or `[]string` parameters, so `f.Fuzz` panics at runtime. The method text ("primitive string sequences") implies an encoded `string`/`[]byte` argument. | architect |
| ADV-P2-A2-12 | MEDIUM | skeleton ignores its table | VP-032:72-77 | `platform.CacheDir()` takes no env or home seam and `tc` env is never applied. Every row computes the same value, so a correct implementation fails on all but one row. Config/State dirs are not asserted. | architect |
| ADV-P2-A2-13 | MEDIUM | coverage gap | VP-006:36-43,74-77 | The VP says `ModeText` serves both stdin and cache-load at different depths and that "each site is tested". The table has only `_mix_counts` and stdin; the cache-load site's budget is neither measured nor tested. | architect |
| ADV-P2-A2-14 | MEDIUM | false closure claim | VP-031:37-46,76-77 vs legacy dgx_statusline.py:83; VP-030:39; VP-031:51 | VP-031 says "legacy has exactly three caps". `SPARK_MAX_AGE = 90.0` is a fourth (age-based) history bound, and VP-030/VP-031 themselves call it the "90 s cap". The planned "exactly these three" registry check is wrong. | architect |
| ADV-P2-A2-15 | MEDIUM | concurrency / unexplained threshold | VP-018:38-40,100-106; ARCH-04:73-74 | "A temp left by a killed process is removed at the next Save", but no staleness criterion or temp-name pattern is defined. `cost-history.json` is shared across sessions, so one Save can delete another process's in-flight temp and lose that process's write. [owner-question]: what staleness threshold applies? | architect |
| ADV-P2-A2-16 | MEDIUM | contradiction (P18) | gene-transfusion-assessment.md:116-118; VP-037:39-40 vs VP-010:38-41; VP-011:37-49 (OD-149) | The GTA and VP-037 say CPython runs only on the Linux/macOS legs and Windows runs Tier B without Python. VP-010 requires `*.windows.golden` from a Windows oracle run, and the OD-149 Tier C nightly runs the oracle on Windows. Who produces Windows goldens, and where, is undefined. | architect |
| ADV-P2-A2-17 | MEDIUM | P18 isolation gap | VP-034:40-41,80-85 | Isolation is POSIX-only. The skeleton hard-codes `/tmp` HOME/TMPDIR and pins only `TMPDIR` and `LANG`. On Windows, Python reads TEMP/TMP, and pipe stdout uses the locale code page unless PYTHONUTF8/PYTHONIOENCODING is set, so oracle bytes on the Windows leg are not pinned. | architect |
| ADV-P2-A2-18 | MEDIUM | P2 enforcer mismatch | invariants.md:40 vs BC-1.02.001:74,123 | DI-017 names BC-1.02.001 as its enforcer. BC-1.02.001 says "DI-017 is the proxy's concern, not this widget's" and cites only DI-008/DI-012. The "server-tools stay on cloud" clause has no BC. DI-017 should be "deferred to P3/P6 (OD-115)". | business-analyst |
| ADV-P2-A2-19 | MEDIUM | P4 mis-anchor | capabilities.md:29; ubiquitous-language.md:45 vs legacy dgx_statusline.py:489,496-497 | CAP-007 header capture "powering plan-window widgets", and the UL defining plan window "from captured rate-limit headers and stdin", imply the status line reads captured headers. Legacy reads stdin `rate_limits` only; raw headers stay in the ledger. As written, this conflicts with DI-007. | business-analyst |
| ADV-P2-A2-20 | MEDIUM | P4 mis-anchor | bounded-contexts.md:44-45 | BC7 consumes "the metrics store fed by BC5 through the export tunnel". The backend telemetry series (e.g. legacy dgx_statusline.py:340, `vllm:kv_cache_usage_perc`) come from the backend's own metrics, not the ledger exporter. | business-analyst |
| ADV-P2-A2-21 | MEDIUM | contradiction | gene-transfusion-assessment.md:54 | Says the unknown-flag error fires "for any argument starting with `-`, except a bare `--`", and "flag-error for any `-` argument". BC-4.01.002 EC-004/005 and VP-002:41-43 say bare `-` is positional and `--` is a terminator. | architect |
| ADV-P2-A2-22 | LOW | ambiguity | product-brief.md:74 | Parity target: "owner's recorded real inputs … on all 3 OSes". Captures are git-ignored and local (OD-107), so they cannot be replayed on the Linux/Windows CI legs. | product-owner |
| ADV-P2-A2-23 | LOW | stale assessment | architecture-feasibility-report.md:26,33 | Says "37-VP catalog" (now 38) and "CPython 3.11.7"; the VPs and OD-104 say 3.11.x. | architect |
| ADV-P2-A2-24 | LOW | ambiguity / factual | VP-026:39-42,66,91 | Says "10,893 goldens across four grids" in one place and "10,893 rows x 4 grids" in another. Also, Go's `time/tzdata` is only a fallback behind system zoneinfo, so "interpreter-independent" is inaccurate. Windows CPython uses CRT localtime, not IANA. | architect |
| ADV-P2-A2-25 | LOW | skeleton weaker than property | VP-005:41-43,74-83 | `utf8.Valid(stdout)` is claimed but not asserted. | architect |
| ADV-P2-A2-26 | LOW | class / skeleton | VP-011:56-59,72-83 | "No unexplained divergence within budget" is safety-shaped, not liveness. The skeleton omits the BC-6.04.003:65-67 domain filter (seeded `proc_start`, no numeric sids) and the seed print. | architect |
| ADV-P2-A2-27 | LOW | internal inconsistency | VP-036:40-42 vs :70 | The proof table says "6 runs, nearest-rank p95"; the statement says pooled 5×\|fixtures\|. | architect |
| ADV-P2-A2-28 | LOW | ambiguity | VP-018:39-45,94-95 | "Swallowing" vs a skeleton that expects `err != nil`; "never at render time" while Save runs inside the render effect script. | architect |
| ADV-P2-A2-29 | COSMETIC | typo / frontmatter | gene-transfusion-assessment.md:34; VP-006:18-19; VP-012:18 | "Sub Setsystem Registry"; `proof_file_hash` missing in VP-006 and VP-012. | architect |

2. Policy compliance
- P1 append_only_numbering: PASS (VP-038 appended; no reuse).
- P2 lift_invariants_to_bcs: FINDING 18.
- P4 semantic_anchoring_integrity: FINDING 03, 04, 19, 20.
- P5 creators_justify_anchors: PASS.
- P6 subsystem names: PASS (feasibility report and GTA match the ARCH-INDEX registry; only the GTA:34 typo, 29).
- P9 vp_index source of truth: FINDING 04, 09 (catalog says property/fuzz, body is deterministic). Totals = 38 rows, class and method arithmetic verified.
- P12 settled decisions: FINDING 01 (OD-130 not carried into the BCs).
- P13 parity before behaviour change: FINDING 01 (an OD-130 deviation has no named exclusion).
- P14 public repo hygiene: PASS (only 192.0.2.10 RFC 5737; no "Claude" in names).
- P16 thresholds explained: FINDING 15 (no staleness threshold); `renameRetryLimit` is justified.
- P17 ledger format frozen: PASS.
- P18 cross-platform: FINDING 16, 17.
- P19 Go toolchain: PASS (Kani/TLA+ explicitly N/A).
- P20 config over code: PASS. Observation: the dedup cap is a registry key while the read and history caps are module constants, with no stated reason for the split.
- P21 public artifact hygiene: FINDING 17, minor (literal temp paths at VP-034:80,84). Otherwise PASS.

3. Files not fully read
Lifecycle and feasibility tails (after about line 93) of VP-017, VP-019, VP-020, VP-021, VP-024 (the FuzzJSONRoundTrip body), VP-025, VP-028..VP-031 and VP-033. The property, method and skeleton sections of every VP were read. All domain-spec files, the brief, the feasibility report, the DTU assessment and the GTA were read in full.

4. Novelty: HIGH. New issues include the ±Inf vs OD-130 contradiction, the exclusion-id spelling mismatch, the VP-038 keepends error, the `.git` path omission in VP-022, the missing fourth cap, and the Windows oracle and encoding gaps. NOT_CONVERGED.


## Perimeter B (BC-1.01, BC-1.02)

Findings: 17 (high 3, medium 6, low 7, cosmetic 1).

## Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P2-B01 | HIGH | Parity gap (spec-implementation) | BC-1.02.006:65-66 / BC-1.02.020:51-52 (legacy SL:435); BC-1.02.011:53-54, BC-1.02.012:45 (SL:515); BC-1.02.014:59 (SL:857); BC-1.02.025:47-50 and Inv1:57 (SL:866); BC-1.02.017:52 (SL:558-559) | A JSON integer larger than float max is decoded by Python as an exact int and stays under the 4,300-digit limit. Example: a 309-digit `context_window_size`, `resets_at`, `total_lines_added` or `total_duration_ms`, or a transcript `input_tokens`. Feeding it to `total/1e6`, `reset - now`, `n / 1e6`, `float(n)` or `win_ms - dur` raises an uncaught OverflowError, so legacy degrades. None of these BCs specify that, and BC-1.02.025 Inv1 ("never raises") is false. Verified absent: grepped specs for `too large to convert` / `int too large`, no hits; pyfmt `ErrOverflow` (BC-5.01.001/003) covers only ±Inf. Tier C fuzz would expose this as an unexplained diff. Fix: one edge case per site, plus a pyfmt int-to-float conversion contract. | product-owner |
| ADV-P2-B02 | HIGH | Contradiction / P20 / partial-fix propagation | BC-1.02.006:49,65-68,78-81; BC-1.02.014:53-54,69-72; BC-1.02.025:49-50,59-62 vs interface-definitions.md:107-109,120-122 | The pass-1 Policy-20 fix invented the sub-keys `statusline.units.{context,lines,tokens}.k_from/M_from` and declared them "generalized" for non-default values. interface-definitions still defines these as single Text keys (`K`, `k`/`M`). It also lists `statusline.context.cells` and `statusline.units.context` as "default-only … non-default behavior undefined", stating that BC-1.02.006 hard-codes the formula. `k_from`/`M_from` appear in no file outside these three BCs. Blast radius is 4 files. | architect + product-owner |
| ADV-P2-B03 | HIGH | Mis-anchor (config key) | BC-1.02.021:79 | EC-010 names the hylo key `statusline.routing.prefixes` and cites OD-123. OD-123 (decisions log :84) places the key at `backends[0].model_prefixes`, as do BC-1.02.001:48 and interface-definitions.md:101. An implementer following this edge case would look up a key that does not exist. | product-owner |
| ADV-P2-B04 | MEDIUM | Contradiction / P20 | BC-1.01.001:66-67, :163; BC-1.02.026:108 vs ARCH-03-statusline.md:76, interface-definitions.md:70-72 | BC-1.01.001 Inv4 says the degraded line's bytes are "the default-config output" built from `statusline.theme.*` defaults. BC-1.02.026 lists `statusline.theme.*` as the "degraded line colours" key. ARCH-03 and interface-definitions both fix the line as a constant that does not depend on the theme. What a non-default theme does to the degraded line is therefore contradictory. | product-owner |
| ADV-P2-B05 | MEDIUM | Interface mismatch / parity | BC-1.02.026:45 vs ARCH-06-pyfmt.md:76, BC-5.01.003:58 | BC-1.02.026 PC2 specifies `pyfmt.Int(x) (int64, error)`. ARCH-06 and BC-5.01.003 specify `Int(x float64) (Num, error)`, exact beyond int64. Legacy `_fmt_lines(1e300)` renders a long `…M` string (int(1e300) is exact, SL:853, 857). An int64 Int would overflow and degrade instead. | product-owner |
| ADV-P2-B06 | MEDIUM | P20 non-default behavior undefined | BC-1.02.019:44, 50-52 | `statusline.theme.heat` is said to hold the hue span, saturation and value. PC2 only defines the hsv_to_rgb sectors `i` in {0,1}, valid only because h ≤ 0.22. With a hue span above 1/3, sectors 2-5 are undefined, and no range validation is stated for s, v or the span. | product-owner |
| ADV-P2-B07 | MEDIUM | Semantic anchoring (VP) | BC-1.01.001:98-99, 131 vs VP-INDEX.md:57,59 | Both VP rows cite VP-003. VP-003 covers "degraded-line write failure still exits 0 (cp-x03)", not "errDegraded/panic → 29 bytes" or "never non-zero for any stdin". Both rows also claim fuzz (Tier C), but VP-001 and VP-003 are unit/table. | product-owner |
| ADV-P2-B08 | MEDIUM | VP method coherence [pattern] | BC-1.01.003:106, BC-1.01.004:85-86, BC-1.01.005:95, BC-1.01.006:95-96, BC-1.01.007:87 vs VP-027:15,57-60 | These rows attribute `testing/quick` property tests and "Tier C differential fuzz" to VP-027. VP-027 is `proof_method: manual`, a unit/table breakpoint matrix, "testable-only". The properties the BCs promise have no VP that delivers them. Five BCs are affected. | architect |
| ADV-P2-B09 | MEDIUM | P2 invariant scope mismatch | invariants.md:40 vs BC-1.02.001:72-74, 123 | DI-017 names BC-1.02.001 as its enforcer. BC-1.02.001 Inv1 explicitly disclaims DI-017 ("the proxy's concern, not this widget's") and does not cite it in its Traceability row. | product-owner |
| ADV-P2-B10 | LOW | P5 mechanical citation | BC-1.02.020:112; BC-1.02.027:93 | VP-001 (never-blank, exit 0) is cited on rows "denominator equals oracle for totals 1..2,000,000" and "`_hm` equals CPython for finite inputs". Neither row is a degrade property. | product-owner |
| ADV-P2-B11 | LOW (pending intent verification) | Q-b consistency | BC-1.02.017:68, 79-83; BC-1.01.008:53-55 | Byte-pinned vectors depend on a hand-edited cache: `proc_start` of `true`/±Infinity (EC-007 says so itself), and a surrogate-bearing cached git `branch`. Under ruling Q-b, foreign-cache shapes are not a byte-parity obligation, yet BC-1.02.017 Inv3 says "No case of this contract is excluded". | product-owner [owner-question] |
| ADV-P2-B12 | LOW | Unsound invariant/property | BC-1.01.006:62, 95 (legacy SL:1196) | Inv1 and the VP-027 property say the output is always a "prefix of segments". That is false when stdin text (display name, project label) contains the exact SEP bytes, which BC-1.01.004 PC3 admits can arrive: `rsplit` then cuts inside a segment. The generator for the property test would have to exclude that case. | product-owner |
| ADV-P2-B13 | LOW | Missing edge case | BC-1.01.005:40-48 | COLUMNS containing undecodable bytes is not covered. Python decodes the env var with surrogateescape, then `int()` raises ValueError, giving 0. Go's `Getenv` returns raw bytes, so the expected result should be pinned. | product-owner |
| ADV-P2-B14 | LOW | Structure | BC-1.01.009:69 | Postcondition 2 is glued onto the end of footnote ¹ ("(SL:606-607).2. A degrade…"). It renders as footnote text, not as a numbered postcondition. | product-owner |
| ADV-P2-B15 | LOW | P20 internal inconsistency | BC-1.02.006:47-49 vs :63-64, :137 | The preconditions name `plain_max`/`red_from` and `statusline.units.context.M_from`. PC5 hard-codes 85/50, and the Config-keys row names `statusline.units.context`. | product-owner |
| ADV-P2-B16 | LOW | Semantic naming | BC-1.02.029:56, 63, 115 | `statusline.cost.basis_min_shown_usd` is the display floor for the `eq` estimate, not a basis minimum. It sits beside `basis_min_mtok_month`, which is a real basis guard, so readers can confuse the two. | product-owner |
| ADV-P2-B17 | COSMETIC | Numbering | BC-1.02.006:78, 82 | Two invariants are both numbered "3". | product-owner |

Checks that turned up no defect: I recomputed by hand the byte counts (45/64/29), every BC-1.01.010 staircase, and the row-1 widths. I also recomputed the vectors for limits/countdown (incl. 0.9·length = 0.09999999999999998 and the 1.15 products), heat C0/C5/50.4/0/true, the cache-hit ties (0.015, 0.025, 0.135, 0.995), `_fmt_tok_c`/`_fmt_lines` ties, `⌂` texts (20770d19h, 1d07h, 7h30m), the BC-1.02.030 sequence countdowns, and the BC-1.01.009 write sets. All match legacy semantics.

## Policy compliance
- P1 append_only_numbering: PASS
- P2 lift_invariants_to_bcs: FINDING B09
- P4 semantic_anchoring_integrity: FINDING B03, B07, B08
- P5 creators_justify_anchors: FINDING B10
- P6 subsystem name: PASS (SS-01 = "Status Line", ARCH-INDEX:53)
- P7 H1 = BC-INDEX: PASS for 40/40 against BC-INDEX:49-93. PRD title column not sampled.
- P12 settled_decisions: PASS
- P13 parity_before_behavior_change: FINDING B01, B05
- P14 public_repo_hygiene: PASS
- P16 thresholds_are_explained: PASS
- P17 ledger_format_frozen: PASS (no ledger surface in scope)
- P18 cross_platform: PASS (per-OS path/normpath goldens, BC-1.02.003/004/022)
- P19 go_hardening_toolchain: PASS
- P20 config_over_code: FINDING B02, B04, B06, B15
- P21 public_artifact_hygiene: PASS
- P3, P8, P9, P10, P11, P15: N.A.

## Files not fully read / limits
- The Brownfield and Related-BC tails of BC-1.02.007 through BC-1.02.030 were not read (I read through the Traceability or VP sections).
- Not opened: prd.md, error-taxonomy, test-vectors supplement, VP files other than VP-027 and VP-INDEX. ARCH-03 and ARCH-06 were grep-checked only.
- I had no Bash, so `python3 -I` was not run. These oracle claims are unverified: BC-1.01.002 depth 993/994, the BC-1.02.005 SHA-1 keys, heat cells C1-C4 and C6-C9, and the ntpath results in BC-1.02.022.
- B01 rests on CPython int-to-float semantics, not on an oracle run.

## Novelty
MEDIUM. B01, B02, B04 and B05 are new substantive gaps, and B02 is an incomplete propagation of a pass-1 fix. **NOT_CONVERGED**


## Perimeter C (BC-1.03, part of BC-1.04/1.05/1.06)

Findings: 12 (high 2, medium 4, low 5, cosmetic 1).

## Perimeter C findings (BC-1.03.001..021, BC-1.06.001..002), pass 2

I had no Bash tool, so I could not run `python3 -I`. Instead I recounted every size, `conv`, `tin`, `rb` and `lr` vector by hand against legacy SL:988-1154. All of the following match legacy exactly: BC-1.03.002/003/004/005/006/007/008/009/011/012/016 (T1, T13, T16 and all 20 row rules), all 21 rows of BC-1.03.019 plus BASE, and the vectors of BC-1.03.020 (C1-C3) and BC-1.03.021. Python claims that depend on runtime behavior (the depth limits 989/990, NaN identity, the error text) are not oracle-verified.

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P2-C01 | HIGH | Parity / missing crash path | BC-1.03.006:53-55; BC-1.03.018:35, :83; BC-1.03.010:66-68. Legacy SL:1108, SL:1117, SL:994, SL:996 | **Legacy has an eighth transcript crash path that no BC lists.** Python raises `OverflowError` when an int too large for a double (about 1.8e308; JSON allows up to 4,300 digits) meets a float. Examples: `_i + _w` with `input_tokens: 1.5` plus a 310-digit `cache_creation_input_tokens` (SL:1108); a cached float `tin` plus a huge int (SL:1108); `prompt - pp` when `pp` is a float (SL:1117); `TURN_STALE * out` or `out / span` when the opening line's `out` is a huge int, `lu` is set and a closer follows (SL:994/996). In legacy this degrades and is sticky because nothing is saved. BC-1.03.006 PC3 says "anything + float = float" and BC-1.03.018 says "seven crash paths" and "never degrades on any transcript line content", so hylo's behavior here is undefined. None of the W-predicates match these lines, because the values are numbers. [owner-question]: extend D4-EX-2, or keep the degrade for parity. | product-owner |
| ADV-P2-C02 | MEDIUM | Parity / cache format | BC-1.03.006:56-57 ("ints as decimal digits of any length"); BC-5.02.001:79 covers decoded values only. Legacy SL:203, SL:205 | **Large token totals stop the mix cache from saving in legacy.** Two counted 4,300-digit `input_tokens` add up to 4,301 digits. CPython 3.11 `json.dump` then raises `ValueError` (the int-to-string digit limit), and `save_cache` swallows it. Result: no write and a partial temp file left behind, every refresh after that. A Go big-int encoder would write the file, so the caches diverge. The BC needs a postcondition for accumulators above 4,300 digits. | product-owner |
| ADV-P2-C03 | HIGH | P20 / P16 | BC-1.03.003:45-46 ("Range is defined in the S2 schema (OD-114)"); interface-definitions.md:110-116 and :120-124; BC-2.01.004 (no entries) | **None of the 7 transcript/turn keys has a range or defined non-default behavior.** The keys are `read_cap_bytes`, `dedup_memory`, `rebuild_excess`, `image_chars`, `dim_below_out`, `floor_tps`, `stale_factor`. They are also missing from the "Default-only parameters" list. Values that would break under legacy semantics: `floor_tps=0` divides by zero at the SL:994 expression; `read_cap_bytes=0` makes `fh.read(0)` hit the loop break, `cut<0`, and the parse freezes for good; a negative value makes `read(-1)` read the whole file; `dedup_memory=0` turns `ids[-0:]` into the whole list, which breaks VP-031's cap. Without ranges, no failing test can be written for these. | architect + product-owner |
| ADV-P2-C04 | MEDIUM | Semantic anchoring (P4) | interface-definitions.md:114 vs BC-1.03.010:49 and legacy SL:958, SL:996 | **Wrong description of `dim_below_out`.** The registry row calls it "dim … below this **out-rate**". The BC and legacy compare the output **token count** (`out < TURN_DIM_OUT`), not the rate. An implementer following the registry would compare the wrong value. | architect |
| ADV-P2-C05 | MEDIUM | Mis-anchor (P4 / P5) | BC-1.06.001:116-117; VP-INDEX.md:78; VP-022 frontmatter `source_bc` | **VP-022 is cited for something it does not verify.** BC-1.06.001 lists VP-022 as "primary" for the load-differential fuzz and the save-never-panics property. VP-022 is "status line never reads the ledger". The reverse anchor is wrong too: VP-022's `source_bc` is BC-1.06.001, which has no ledger-scope postcondition. | architect |
| ADV-P2-C06 | MEDIUM | Testability / safety | BC-1.03.015:51-54. Legacy SL:1042 | **Undefined behavior when `transcript_path` is an int naming a regular-file descriptor.** The BC leaves hylo's behavior "unspecified/out of scope". Legacy reads that descriptor and closes it (`open(int)` with closefd). Go's descriptor table is different from CPython's (runtime poller descriptors, files hylo has open), so a literal port could read or close descriptors hylo does not own. The BC also models the check as a stat of `/dev/fd/n`, while legacy calls `fstat`. It needs a stated rule, for example "never read or close a foreign descriptor → no-transcript". [owner-question] | product-owner |
| ADV-P2-C07 | LOW | Parity gap | BC-1.03.005:59, :65-66. Legacy SL:1099 | **Dedup equality is underspecified.** "Equality of the decoded id value / duplicates cannot occur" says nothing about Python semantics. My reading of CPython's json decoder is that every decoded `NaN` is the same shared object, so NaN ids dedupe by identity; Go's `NaN != NaN` would never dedupe them. Also `1`, `1.0` and `true` collide as Python keys. Not oracle-verified. | product-owner |
| ADV-P2-C08 | LOW | Contradiction | BC-1.03.004:51-53 vs BC-5.02.003:51-53 | **Contradicts the decoder BC.** PC3 lists "invalid UTF-8 fails" with no exception, but `surrogatepass` accepts CESU-encoded surrogates (`ED A0 80`). The partial list conflicts with the BC that owns decoding. | product-owner |
| ADV-P2-C09 | LOW | Edge case | BC-1.03.002:86. Legacy SL:1027, SL:1043, SL:1053 | **EC-007 only classifies a "non-number" cached `size`.** A float `size` hits `seek(float)`, a `TypeError` that is not caught (crash). A negative `size` never resets (`off > 0` is false), then the seek's `OSError` is caught and the parse makes no progress, permanently. Both are foreign-cache forms and should be classified (ruling b). | product-owner |
| ADV-P2-C10 | LOW | Spec gap | BC-1.06.001:68-72; BC-1.06.002:67-69 vs ARCH-04-data-files.md:72. Legacy SL:202-205 | **Temp cleanup on write failure is unspecified.** The BCs only require removing the temp after a failed *rename*. ARCH-04 says all failed or interrupted saves remove their temp. A `json.dump` or disk-full failure mid-write leaves a partial temp in legacy; hylo's behavior there is not in any BC. | product-owner |
| ADV-P2-C11 | LOW | Mechanical citation (P5) | BC-1.03.002:115; BC-1.03.021:94 | **DI-012 cited without a matching deviation.** Both BCs cite DI-012 (named deviations only) but are byte-exact. BC-1.03.021 even says "no exclusion entry". OD-101 (cache dir) is not one of DI-012's named entries. | product-owner |
| ADV-P2-C12 | COSMETIC | Wording / frontmatter | VP-031:41-42, :75; BC-1.06.001:29 and BC-1.06.002:26 | VP-031 calls the read step a "module constant" while BC-1.03.003 makes it a config key. BC-1.06.001/002 use `introduced: v0.1.0` where the BC-1.03.* files use `"0.1"`, and they have no `priority:` field. | architect |

### 2. Policy compliance
- **P1:** PASS. BC-1.03.001..021 and BC-1.06.001..002 are contiguous, with no reuse.
- **P2:** FINDING C11. All cited DIs (007, 008, 012) exist.
- **P4:** FINDING C04, C05.
- **P5:** FINDING C05, C11.
- **P6:** PASS. SS-01 matches ARCH-INDEX:53.
- **P7:** PASS. All 23 H1s match BC-INDEX:99-119, :165-166 and PRD:194-214, :260-261, and describe their postconditions.
- **P12:** PASS. Challenges to settled decisions are tagged [owner-question] (C01, C06).
- **P13:** FINDING C01, C02, C07, C09. Legacy line citations are otherwise correct and the pinned vectors reproduce.
- **P14:** PASS. Fixtures are synthetic.
- **P16:** FINDING C03 (no range rationale). Default rationales are present and match the SL:954-974 comments.
- **P17:** PASS (the mix cache is not the ledger).
- **P18:** PASS, with a note on C06. The Windows rows in BC-1.06.001 EC-008 and BC-1.06.002 EC-003/005 are marked not executed.
- **P19:** PASS (Go tools only).
- **P20:** FINDING C03. No DGX_* aliases. The T-061 named constant is justified.
- **P21:** PASS. No home paths, private IPs or session IDs in the perimeter.
- **P3, P8, P9, P10, P11, P15:** N.A.

### 3. Files not fully read
- **BC-1.03.004..021:** the trailing Brownfield sections, roughly the last 20-40 lines of each.
- **BC-1.06.001:** lines 1-9 and 140 onward. **BC-1.06.002:** lines 1-9 and 140 onward.
- **Not opened:** ARCH-03-statusline.md, domain-spec/capabilities.md, prd-supplements/test-vectors.md, VP-029, VP-013, VP-012, VP-018, VP-019, VP-038, VP-006.
- **Grep only:** error-taxonomy.md, BC-2.01.004, BC-5.02.001/003, ARCH-04.
- **Not done:** no `python3 -I` run (no Bash tool available).

### 4. Novelty
Novelty: **MEDIUM**. C01 (an unlisted legacy crash class that contradicts BC-1.03.018's "seven paths / never degrades") and C03 (the P20 range gap for 7 keys) are substantive and new. The other findings are narrower parity and anchoring gaps.

**NOT_CONVERGED**

Relevant paths:
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.018.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.015.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.06.001.md
- .factory/specs/prd-supplements/interface-definitions.md
- .factory/specs/verification-properties/VP-022-ledger-read-scope-absence.md
- legacy/dgx_statusline.py


## Perimeter C2 (remaining BC-1.04/1.05/1.06)

Findings: 14 (high 1, medium 6, low 6, cosmetic 1).

1. **Findings**

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P2-C2-01 | HIGH | P7 title vs postconditions | BC-1.05.006:38; BC-INDEX.md:156; prd.md:251 | The title "Numeric sid: throttle and self-exclusion fail" describes the legacy behavior that is not reproduced. The Go postconditions say the opposite: the throttle applies (PC2) and self-exclusion works (PC3). Someone reading the index would build the wrong thing. | product-owner |
| ADV-P2-C2-02 | MEDIUM | P13 quirk fidelity, BC contradiction | BC-1.04.013:49-50 vs legacy SL:1221; BC-1.05.003:91,163 | BC-1.04.013 PC1 says `dgx_mtok` becomes none "unless it is a number and `> 0`", so NaN would become none. Legacy `dgx_mtok <= 0` keeps NaN, and BC-1.05.003 EC-005 says exactly that. Output is the same either way (the basis check at SL:629 re-tests `> 0`), but a test on the intermediate value would contradict the sibling BC. | product-owner |
| ADV-P2-C2-03 | MEDIUM | Contradiction, untestable claim | BC-1.04.016:60-62 vs BC-1.04.003:54-55, BC-1.04.014:43-46, legacy SL:337, 662-666 | Invariant 1 says a NaN/+Inf box rate or TTFT goes into history and "surfaces as CP-N02 in the same render". That is false in three cases: the new point is skipped when the 2 s gap is not met; a first fetch gives fewer than 2 plotted points; a NaN TTFT never crashes under the default `rate` trace (key `v`). A test written from this invariant fails against legacy. | product-owner |
| ADV-P2-C2-04 | MEDIUM | BC vs interface-definitions contradiction (P20) | interface-definitions.md:120-124 vs BC-1.04.007:52-55, BC-1.04.006:42-44 | The supplement still lists `statusline.kv.cells` ("BC-1.04.007 hard-codes `/25`, `4`, `4-n`") and `statusline.queue.yellow` ("rule shape unstated") as default-only. Both BCs now define non-default behavior: a general `C` formula, and `false` means never yellow. The fix reached the BCs but not the supplement. | architect |
| ADV-P2-C2-05 | MEDIUM | P20: non-default behavior undefined | BC-1.04.003:43-46; BC-1.04.007:42; BC-1.04.009:45-48; BC-1.05.005:54-57; BC-1.05.001:58; BC-1.04.012:44-46 | The Int/Float keys these BCs add (`kv.cells`, `sparkline.points`, `sparkline.history_cap`, `sparkline.scale`, `cost.min_sessions`, `cost.percentiles`, `idle.running_below`, among others) have no range anywhere. BC-2.02.002 covers only `Seconds` keys. Python quirks make a literal port diverge: `hist[-0:]` is the whole list (SL:350, 664); `min_sessions` 0 on an empty list raises IndexError (SL:261); a percentile above 1 overflows the index; `_SPARK_FIXED.get(key) or …` (SL:671) falls back to the window max when the fixed top is 0. | architect |
| ADV-P2-C2-06 | MEDIUM | VP/BC contradiction (P4) | VP-020:37-44, 61-63 vs BC-1.05.004:94, BC-1.05.006:74-75 | VP-020 says wrong-type history loads as empty and is regenerated. BC-1.05.004 EC-008 says those shapes are CP-C09/C10 crash paths (`h.setdefault` on a list raises, SL:229) with no write. VP-020:44 also says "self-exclusion fails" for numeric sids, which contradicts BC-1.05.006 PC3. | architect |
| ADV-P2-C2-07 | MEDIUM | P16, partial-fix propagation | BC-1.05.004:126 | T-022 is still marked "rationale UNKNOWN … pending owner confirmation". OD-57 E-0 already accepted it as derived (hylo-legacy-owner-decisions.md:122), and pass-4-deep-nfr-r7.md:284 gives the R-4 rationale. | product-owner |
| ADV-P2-C2-08 | LOW | Untestable postcondition | BC-1.04.001:54-57, 79 | "Follows redirects exactly as urllib's default handler" gives no limits. urllib allows 10 redirects, max 4 repeats of one URL, and only http/https/ftp targets. Go's default policy stops after 10 requests, so it follows one redirect fewer. A Go test cannot be pinned from this text. | architect |
| ADV-P2-C2-09 | LOW | Unspecified raise paths | BC-1.04.001:65-74, 101 vs SL:182-183 | Non-string label cases are not stated. An unhashable non-empty `__name__` (list or object) raises TypeError at `name not in out` and drops the whole sample. A non-string `job` makes `"up:" + job` raise. `1`, `1.0` and `true` used as names collide under first-wins. PC3 only says "any series raises" in general. | product-owner |
| ADV-P2-C2-10 | LOW | Internal formula mismatch | BC-1.04.007:52 vs :92 | PC3 uses `Ceil(kv / (100 / C))`; the VP row uses `ceil(kv·C/100)`. They agree at C=4 but can round differently for other C values. | product-owner |
| ADV-P2-C2-11 | LOW | False claims | BC-1.05.002:85; BC-1.05.007:59-61 | (a) "Every recorded rate is > 0" is false: a raw `api_ms` of Infinity is stored (SL:235) and gives rate 0.0 (SL:255). (b) "NaN `r` is unreachable" is false: `usd`=+inf with `api_ms`=+inf gives inf/inf = NaN, rendered grey ` $nan/h` (SL:622-625). | product-owner |
| ADV-P2-C2-12 | LOW | P16 rationale label drift | BC-1.04.007:43-44 vs SL:746; BC-1.04.012:45-46 vs pass-4-deep-nfr.md:102 | T-049 cites "THRESHOLDS §8b", but legacy says §8 (§8b is the TTFT rule, SL:790). T-108 is labeled a judgment call, but the catalogue classes it DOC (review #20 gating). | product-owner |
| ADV-P2-C2-13 | LOW | P2 sibling citation drift | BC-1.04.001:131,143; BC-1.04.002:47-50,113 | Both BCs describe D4-EX-3 deviations (URL, TTL) but do not cite DI-012. Their siblings BC-1.04.020:114 and BC-1.04.021:88 cite DI-012 for the same TTL deviation. | product-owner |
| ADV-P2-C2-14 | COSMETIC | Citation drift | BC-1.05.006:57-58, 164; BC-1.05.009:164; BC-1.04.001:133 | `re.sub` is at SL:1017, not "SL:1013-1016" (the early return is SL:1010-1011). The isinstance guards are at SL:226/235, not "SL:225, 233". BC-1.05.006 frontmatter says confidence H but Source Evidence says "medium". "Architect to confirm" is stale: ARCH-03:114 already lists `telemetry.go`. | product-owner |

What checked out: these were hand-computed against the legacy source rather than run through `python3 -I` (no shell in this read-only run, so no oracle runs were possible).
- The BC-1.04.020 11-step sequence: tuples, row bytes, cache key order.
- All sparkline vectors, including the RGB fades and half-up indices.
- The KV, TTFT, power, idle and mine tables.
- The BC-1.05.005 indices and NaN sort orders (traced through timsort by hand).
- The BC-1.05.008 thresholds (24, 30)/(20, 26) and all twelve golden rows.
- The BC-1.05.006 legacy duplicate-key and red-colour case.
- The ARCH-03 anchor slugs resolve.

The only FP-tie-sensitive values that rest on the BCs' own oracle claims are the 0.7 fade channel (49) and `999.995` → `$1000.00`.

2. **Policy compliance**
- P1: PASS.
- P2: FINDING 13.
- P4: FINDING 06.
- P5: PASS.
- P6: PASS (SS-01 matches ARCH-INDEX:53).
- P7: FINDING 01.
- P12: PASS.
- P13: FINDINGS 02, 03, 09 (all quirk-specification gaps; no unapproved deviation found).
- P14: PASS (RFC 5737 192.0.2.10 only; fixtures synthetic).
- P16: FINDINGS 07, 12.
- P17: PASS (query and metric names byte-identical to SL:102-123).
- P18: PASS.
- P19: PASS.
- P20: FINDINGS 04, 05.
- P21: PASS.
- P3, P8, P9, P10, P11, P15: N.A.

3. **Files not fully read**
- Frontmatter lines 1-28 of BC-1.04.004 to 021 and lines 1-16 of BC-1.05.* were skipped (spot-checked through BC-INDEX).
- Not read in full: prd.md (grepped), ARCH-04-data-files.md, prd-supplements/test-vectors.md, VP-030/031/021/019/022/001 (only VP-020 was read), capabilities.md and invariants.md (grepped), error-taxonomy.md (grepped).
- Legacy SL:420-600 and SL:1020-1150 were not read; they are outside this perimeter apart from the main tuple order, which was checked.

4. **Novelty: MEDIUM.** One HIGH title/postcondition mismatch, three cross-document contradictions, and an unfixed config-range gap. **NOT_CONVERGED.**


## Perimeter D (S2-S6 BCs)

Findings: 18 (high 3, medium 10, low 4, cosmetic 1).

1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P2-D01 | HIGH | contradiction / spec-impl recipe | BC-5.01.005:61-63 vs :53-54, :88 | PC-5 says to build `Repr` from `strconv.FormatFloat(x,'g',-1,64)` and then post-process. In shortest mode, Go's `'g'` switches to an exponent at exponent ≥ 6 (`eprec = 6`), so the recipe gives `1.794615009e+09`. The BC's own canonical vector requires `1794615009.0`. The listed post-processing (signed 2-digit exponent, `.0`, nan/inf) never converts exponents 6..15 back to fixed notation, so following PC-5 breaks PC-1/PC-2 and every cache float. | product-owner, architect |
| ADV-P2-D02 | HIGH | per-OS gap (P18) | BC-6.02.003:115-116; BC-6.01.002:68; BC-6.04.001:47, 71-74 | Naive-timestamp cases run under `America/Chicago`/`Europe/London`, and Tier A runs with the oracle on windows-2025. CPython on Windows does not read IANA `TZ` values (the MS CRT expects the `EST5EDT` form). So the oracle's naive `.timestamp()` (SL:983) disagrees with Go's injected `Loc`, and there is no exclusion entry or OS restriction for this. Research §476 recommended Linux/macOS-only for these cases; no BC carries that. BC-5.04.002 Inv-2 covers only the Go side. | product-owner |
| ADV-P2-D03 | HIGH | contradiction | BC-6.04.003:54-55 vs BC-6.04.001:47, 71-74 and BC-6.04.003:40, 89-91 | Tier C says "the Windows leg runs Tier B without Python, BC-6.04.001". BC-6.04.001 installs CPython and runs Tier A on all three OSes. A Windows leg with no oracle cannot run a differential fuzz, so the OD-149 exit gate ("ONE clean nightly run on all three OSes", PC-6) cannot be met. | product-owner |
| ADV-P2-D04 | MEDIUM | partial-fix regression | BC-6.04.003:107 vs :89-92 | EC-002 still says a clean night "counts toward the N-night exit criterion". PC-6 (OD-149) says one clean run and no streak. | product-owner |
| ADV-P2-D05 | MEDIUM | contradiction / fail-closed | BC-6.03.004:106-113 vs BC-6.03.002:79-82 | D4-EX-3 cases use scope `stdout`, with caches "compared to nothing". The same PC's next bullet, and BC-6.03.002 PC-6, say every artifact outside the scope is still compared to the oracle. For the bool, enum and URL classes, legacy renders normally and writes caches (SL:76-77, 89, 186), so the named-cache set check would fail. The stated reason ("legacy may still have written caches before its import-time parse") is also wrong: the import-time crash happens before any write. | product-owner |
| ADV-P2-D06 | MEDIUM | partial-fix regression / mis-anchor | BC-6.02.003:80 | The provenance cites "SL:73-79, 92 and 444". SL:79 is `STALE_OK`, SL:92 is a comment, and `DGX_SL_TRACE` is at SL:89. BC-6.01.002:74 was corrected (ADV-P1-D23); this sibling was not. | product-owner |
| ADV-P2-D07 | MEDIUM | mis-anchor / wrong rationale | BC-6.03.003:75-78, 118 | PC-1 says named caches can never match the temp pattern because the sid sanitizer removes dots (cites SL:1015-1016). The sanitizer is at SL:1017 and applies only to the mix cache. The session cache uses the raw sid (SL:1215, OD-03), and this BC's own EC-002 shows `statusline-a.json.b.json`. The guarantee does hold, but because every named cache ends in `.json`, so its last 8 characters include a `.`. Separately, EC-003 is wrong: Go `os.CreateTemp` replaces `*` with a decimal of variable length, so it is not always 8 characters and not always matched. | product-owner |
| ADV-P2-D08 | MEDIUM | interface drift (ARCH-06) | ARCH-06:84, 96, 114, 116 vs BC-5.04.002:34; BC-5.04.003:37; BC-5.01.006:37; BC-5.02.002:43 | Signatures disagree. `LocalToUnix`: ARCH says `(loc, wall time.Time) (float64, bool)`, the BC says `(int64, error)` with `ErrValue`. `TimeFloat`: ARCH takes `ns int64`, the BC takes `t time.Time`. BC-5.01.006 Description says `MaxSeq(vals ...Num) Num`, contradicting its own PC-1 and ARCH `(Num, error)`. BC-5.02.002 calls `Decode` with 2 args, while ARCH and BC-5.02.003 PC-7 need `depthBudget`. Also, BC-5.01.001:38, BC-5.01.003:38-41, BC-5.01.006:41-43 and BC-5.03.002:37-40 still say "the ARCH-06 row is stale", but ARCH-06:72-84, 107 is already reconciled. | architect, product-owner |
| ADV-P2-D09 | MEDIUM | internal contradiction [owner-question] | BC-2.02.003:72-73 vs :89, :114; BC-2.02.002:62 | Invariant 1 says any value legacy parsed that has no `_` and no non-ASCII digit gives the same number in hylo. EC-010 contradicts it: rows `99999999999999999999` is accepted by legacy `int()` (SL:75) but is `out of range` in hylo. So do the range errors (`nan`, `inf`, `-1`, values above 9223372036.854775). The int64-overflow and Duration-ceiling deviations are not in the D4-EX-3 case list (:114). Question for the owner: does OD-114 cover them? | product-owner |
| ADV-P2-D10 | MEDIUM | ambiguity (untestable) | BC-2.01.002:66-77 | PC-4 says `HYLO_BACKENDS_<i>_<FIELD>` with i≠0 and "any field name" defines an extra entry. The same PC then says a non-P1 field only "warns as an unknown setting for every index". For `HYLO_BACKENDS_1_NAME=x`, the outcome (cardinality error, warning only, or both) cannot be determined. | product-owner |
| ADV-P2-D11 | MEDIUM | semantic gap [owner-question] | BC-2.03.002:37, 61, 66 vs BC-3.01.001:57-58 | `config path` claims to print "the paths hylo uses", but overrides apply to the config line only. With `HYLO_PATHS_CACHE_DIR` set, the `cache:` line prints `CacheDir()`, a directory the status line does not use (BC-3.01.001 PC-3). | product-owner |
| ADV-P2-D12 | MEDIUM | harness hermeticity | BC-6.01.002:81-83; BC-6.02.003:108-109; BC-3.02.001:84-89 | "No PATH key" is assumed to mean no `ps`. With no `PATH`, CPython subprocess falls back to `os.defpath` (`/bin:/usr/bin`) and runs the real `ps` (SL:280), and Go's native probe reads the runner's real process tree. Seeding `proc_start` is optional, so an unseeded case with a truthy `session_id` depends on the machine (for example, a real `claude` ancestor when tests run inside a Claude Code session). The harness needs a rule that rejects such a case unless a fake table is declared. | product-owner |
| ADV-P2-D13 | MEDIUM | semantic anchoring (P4) | VP-038:14, 39, 96 vs BC-5.03.002:57-59; ARCH-06:29 | VP-038 puts `SplitLinesBytes` in `internal/statusline (transcript*.go)` with goldens under `internal/statusline/testdata`, and asserts "ends-retained pieces". BC-5.03.002 and ARCH-06 place it in `internal/pyfmt/str.go` and drop terminators (`bytes.splitlines()` default). BC-5.03.002 also does not cite VP-038. | architect |
| ADV-P2-D14 | LOW | ambiguity | BC-6.02.002:58, 70-71, 89-92 | `transcript_bytes` is optional per step. The monotonic check is undefined when some steps omit it ("full copy") and a later step gives a smaller value. | product-owner |
| ADV-P2-D15 | LOW | vector notation | BC-5.02.004:73-74; BC-5.02.001:102 | EC-004 says "JSON escape text" but shows a raw emoji. EC-003's expected `Dumps` output shows a raw emoji while saying "escaped surrogate pair, 14 chars". This conflicts with the escape-notation convention (BC-5.01.002:87), so a test writer may encode the wrong bytes. | product-owner |
| ADV-P2-D16 | LOW | unverified claim (pending verification) | BC-4.01.003:66, 51 | EC-002 says `go run ./cmd/hylo version` gives `(devel)`. Go ≥1.24 stamps VCS-derived versions into `Main.Version` for builds in a VCS checkout, so a no-ldflags build may give a pseudo-version instead. Not verified for `go run` under Go 1.26. | product-owner |
| ADV-P2-D17 | LOW | per-OS ambiguity | BC-2.01.001:71-72, 99 | On Windows, `os.Environ()` keeps the original case of names. Whether `hylo_foo` is recognized as an unknown `HYLO_*` setting (and warned about) is not specified. | product-owner |
| ADV-P2-D18 | COSMETIC | wording | BC-5.01.004:56 | "`|n| >= width`" should be "digit count ≥ width". | product-owner |

2. Policy compliance
- P1 append_only_numbering: PASS
- P2 lift_invariants_to_bcs: PASS (DI-008, DI-010 and DI-012 are cited throughout)
- P4 semantic_anchoring_integrity: FINDING D06, D07, D13
- P5 creators_justify_anchors: PASS
- P6 subsystem name verbatim: PASS (all `SS-0N` match the ARCH-INDEX:54-58 registry)
- P7 BC H1 = BC-INDEX: PASS (all 52 H1s match BC-INDEX:172-288). PRD titles were not compared.
- P12 settled_decisions_are_constraints: PASS (questions to the owner are tagged on D09 and D11)
- P13 parity_before_behavior_change: PASS; D09 is a gap in which deviations are enumerated
- P14 public_repo_hygiene: PASS (only 192.0.2.x addresses; placeholder home paths)
- P16 thresholds_are_explained: PASS (D09 touches on the int64/Duration ceilings)
- P18 cross_platform_from_day_one: FINDING D02, D03, D17
- P19 go_hardening_toolchain: PASS (`x/sys/unix` has a stated reason)
- P20 config_over_code: PASS (no `DGX_*` on the Go side; process name and depth are config keys)
- P21 public_artifact_hygiene: PASS
- P3, P8–P11, P15, P17: N.A.

3. Coverage
- All 52 BCs were read through Postconditions, Invariants, Edge Cases and Vectors.
- Not fully read: Related BCs and Purity tails of about 20 BCs; the tail of BC-6.03.001 (edge cases and VPs); the generator tail of BC-5.02.002; ARCH-06:27-28.
- Not read: prd.md, prd-supplements/, capabilities.md, invariants.md, ARCH-01/02/05/07/08.
- Python checks: I ran 0 vectors with `python3 -I`, because this agent has no command-execution tool. About 170 Python-result vectors were derived by hand from CPython source semantics: all 63 rows of BC-5.02.002, BC-5.01.001/002/003, BC-5.03.002/003, and the epoch arithmetic in BC-5.04.001/002. 0 were found wrong. Still unverified: the sha1 key `29de25ac9bde9ad0` (BC-5.03.003), the 989/990 depth limits (BC-5.02.003), the byte totals of goldens A/B/C (BC-6.03.001) and the repr in BC-5.04.003 EC-001. Rerun these with the real interpreter.

4. Novelty: MEDIUM. D01, D02, D03, D05 and D12 are new substantive gaps; the rest are refinements or propagation residue. **NOT_CONVERGED**

