---
document_type: adversarial-review
phase: 1d
pass: 7
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 114
---

# Adversarial Spec Review — Phase 1d, Pass 7

Pass 7 ran as six fresh-context perimeters, the same split as passes 1-6. Each section is the verbatim final report of one perimeter, unedited except for this framing and repo-relative paths. All perimeters MEDIUM novelty. NOT_CONVERGED (114 findings: HIGH 14 / MEDIUM 47 / LOW 49 / COSMETIC 4; pass 6 had 124 with 27 HIGH). Perimeter A2 reported zero HIGH (first time). The orchestrator spot-verified A03, A2-08, B01, C02, C2-02 and D01 on disk and against CPython 3.11.7; all held.


## Perimeter A (PRD, supplements, architecture, CI)

Findings: 22 (high 3, medium 10, low 9, cosmetic 0).

**ADV-P7-A: Adversarial spec review, Phase 1d, pass 7, perimeter A**

Result: 22 findings (3 HIGH, 10 MEDIUM, 9 LOW). NOT_CONVERGED.

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P7-A01 | HIGH | contradiction | specs/architecture/ARCH-07-parity-harness.md:68-89 | ARCH-07 says its child-env allowlists are the "exact key sets", that BC-6.01.002 is authoritative, and that VP-034 asserts the exact set. The lists disagree with that BC in four ways. **POSIX list:** it sets `PATH` unconditionally and omits `USERPROFILE`, `HYLO_TEST_NOW`, `COLUMNS` and the translated case settings. **Windows list:** it omits `HOME`. **Go-binary list:** absent from ARCH-07 entirely (no `XDG_CACHE_HOME`, `LOCALAPPDATA` or `HYLO_PATHS_CACHE_DIR`). **The BC:** sets `PATH` only when the case has a fake-subprocess table, and its canonical oracle key set has no `PATH` (BC-6.01.002:67-106, :167-168). A story written from ARCH-07 builds an env builder that fails the BC's exact-set test. | architect |
| ADV-P7-A02 | HIGH | partial-fix propagation | specs/prd-supplements/nfr-catalog.md:24-26 | NFR-001 and VP-036 carry the OD-187 conditional exemption for the >512 KB timing fixture. Three other places do not. BC-6.04.002 PC-3 fails the gate if ANY case has p95 > 25 ms, with no exemption (BC-6.04.002:85-89). The ARCH-08 timing bullet (:86-91) and PRD NFR-001 (prd.md:481) also omit it. Blast radius is 3 files, and none defines how the fixture is identified or how use of the exemption is reported. | product-owner + architect |
| ADV-P7-A03 | HIGH | interface cannot express BC | specs/architecture/ARCH-05-platform.md:26,32,33 | **Signature mismatch:** ARCH-05 declares `LocalZone() *time.Location`, but BC-3.01.001:68 requires `LocalZone(env) (*time.Location, error)`. **No env injection:** `CacheDir()` and `HomeDir()` take no env argument, so XDG, HOME, LOCALAPPDATA and TZ are read from the real process. That breaks BC-3.01.001's "pure over injected env" purity scope and BC-6.01.002 PC-2 ("in-process path never reads the real process environment"). **Stale BC reference:** BC-6.01.002:107 still names `Env.Getenv`/`Home`, which ARCH-03:140 superseded. ARCH-01:26 wiring `envOS{}` also conflicts with the platform-provided EnvVars implementation (ARCH-05:31). | architect |
| ADV-P7-A04 | MEDIUM | ambiguity / default undefined | specs/prd-supplements/interface-definitions.md:198-199, :292 | `statusline.units.lines` and `statusline.units.tokens` are both Text keys with default `k`/`M` and range {`k`/`M`}. The "exact env spelling of the default" is `k` for lines but `M` for tokens. A default-only key accepts only the parsed default, so the default value itself is undefined (what goes in `legacy_defaults.golden`?). The two sibling keys also pick different letters with no stated reason. | product-owner |
| ADV-P7-A05 | MEDIUM | contradiction (cross-ref) | specs/prd-supplements/interface-definitions.md:289-293 vs BC-2.01.005:150-151 | The supplement spells the env names `HYLO_STATUSLINE_UNITS_*` / `HYLO_STATUSLINE_LIMITS_WINDOWS`, which is correct per `EnvName`. BC-2.01.005 PC-7 says `HYLO_LIMITS_WINDOWS`, `HYLO_UNITS_LINES`, `HYLO_UNITS_TOKENS`, `HYLO_UNITS_CONTEXT`. Under BC-2.01.001 PC-6 those would only draw the unknown-setting warning. | product-owner |
| ADV-P7-A06 | MEDIUM | partial-fix propagation | specs/prd-supplements/interface-definitions.md:167, :274-275 | The supplement says the `git.ttl_s` exception "has no negative floor of its own (any finite value above the ceiling's magnitude bound)", and the row omits a floor. BC-2.02.002:64-71 (ADV-P5-D11) pins a mirrored floor of -9223372036.854775, with values below it rejected as `out of range`. | product-owner |
| ADV-P7-A07 | MEDIUM | CI cannot work as designed | specs/cicd-setup.md:262, :267; ARCH-08-build-ci-release.md:78-85 | **Required check:** `coverage` is listed as a required status check but defined as "a required STEP of the test job … not a separate job". GitHub required checks bind to check-runs (jobs), and the test job is a 3-OS matrix, so no `coverage` check-run is ever emitted. The gate either blocks forever or gets removed. **Coverage scope:** `go test -coverprofile` per package does not count `internal/parity`'s cross-package execution of statusline unless `-coverpkg` is used, and the spec does not say which. | architect / devops |
| ADV-P7-A08 | MEDIUM | contradiction / CI timeout | ARCH-08:55-58 vs :59-62; cicd-setup.md:52, :115-117, :170-177 | ARCH-08 and cicd-setup still justify the setup-python ordering by "Tier A runs inside the plain `go test` step". The pass-6 A12 ruling excludes Tier A from that step. Lag note 7 says release.yml's plain `go test ./...` "includes Tier A". That puts a second Tier A run under a 30-minute cap, contradicting "one run, one timeout". | architect |
| ADV-P7-A09 | MEDIUM | mitigation rests on nonexistent gate | ARCH-08-build-ci-release.md:139-144 | The P1 restatement of the R-004 mitigation cites a ">= 95 % line-coverage gate over the referee's own packages (`internal/parity` included)". The gate covers only `internal/statusline`, `internal/cost` and `internal/pyfmt` (ARCH-08:46, :80; cicd-setup:141-142), so the HIGH-impact fake-pass risk claims a control that does not exist. | architect |
| ADV-P7-A10 | MEDIUM | cross-platform (P18) | ARCH-05-platform.md:31, :34; ARCH-06:125-126 | The files are named `envvars_windows.go` and `localtime_windows.go`. Go applies an implicit GOOS build constraint to `_windows.go`, so those files never compile on Linux/macOS. That contradicts "BOTH flavors always compiled and table-pinned on every OS — the Windows case-insensitivity table runs on POSIX CI legs". `envvars_unix.go` has no implicit constraint (`_unix` is not a recognized suffix), so it would also compile on Windows. | architect |
| ADV-P7-A11 | MEDIUM | interface gap (https) | ARCH-03-statusline.md:184-209 | The MetricsClient is a "MINIMAL HTTP/1.1 CLIENT OVER net.Conn, plain http only". The URL class admits https (interface-definitions:169), OD-181 says hylo verifies https against the OS trust store, and BC-1.04.001:93-103 follows https redirect targets. The architecture gives no TLS path: no `crypto/tls` dialer, no ALPN pinned to http/1.1, no SNI, no Linux trust root ("OS store (macOS/Windows)" only), and no test seam. | architect |
| ADV-P7-A12 | MEDIUM | mis-anchor (P4) | ARCH-04-data-files.md:109-111 vs BC-COMPONENT-MAP.md:57 | ARCH-04's pass-6 A15 fix says BC-1.02.013's home is the `cache.go` session row. BC-COMPONENT-MAP still homes it at `sl/limits.go`. | architect |
| ADV-P7-A13 | MEDIUM | missing exact string (sibling gap) | interface-definitions.md:214; error-taxonomy.md:82-83 | A descending `statusline.cost.percentiles` pair is a number-range error, but no reason string is pinned. Its sibling cross-key check (`subagent.tokens`) received an exact reason in pass-6 A19. The D4-EX-3 table test bytes are therefore unspecifiable. | product-owner |
| ADV-P7-A14 | LOW | stale owner labels | error-taxonomy.md:46; ARCH-03:104-105; test-vectors.md:43; prd.md:498 | The CP-N03 owner set differs in four places: error-taxonomy says BC-1.04.001/.005, ARCH-03 says .005/.004, test-vectors says .001/.004/.005, and the PRD E-REN-002 row lists none. On disk, BC-1.04.001, .004 and .005 all cite CP-N03. | product-owner |
| ADV-P7-A15 | LOW | drift | prd.md:626-627 | PRD §9 ASM-002 says "2.1.325 is the tested surface — validated". The canonical register (assumptions-register.md:24) has been revised: 2.1.325 was tested at mint time, 2.1.326 is installed, and subagent compatibility is split out to ASM-007. | product-owner |
| ADV-P7-A16 | LOW | user-facing message misdescribes rule | error-taxonomy.md:93 | The glyph reason says "exactly 1 code point and 1 display column". Under OD-184 there is no column check, and the `sparkline` member needs 8 code points, so a 7-code-point sparkline gets a false reason. BC-2.02.001:121 keeps this as fixed vocabulary on purpose. [owner-question] | product-owner |
| ADV-P7-A17 | LOW | stale precedent | ARCH-09-reserved-boundaries.md:25, :41; ARCH-03:209 | "P1 metrics client's `Proxy: nil` transport" is cited as the D14-(b) precedent. The P1 client is now a raw net.Conn client with no http.Transport, so the precedent no longer exists as written. | architect |
| ADV-P7-A18 | LOW | CI census ambiguity | ARCH-08:104-107; cicd-setup.md:80 | Tier B fails if N differs from the "committed golden file census". The spec does not say whether `*.windows.golden` counts on POSIX legs, or `*.golden` on Windows. Read one way the job is always red; read the other way a lost variant can go unnoticed. | architect |
| ADV-P7-A19 | LOW | config over code | ARCH-04-data-files.md:62-77 | `renameRetryLimit = 2` shapes behaviour (it decides whether a Windows write persists) but stays a code constant, while its sibling delay became a registry key (OD-186). [owner-question] | architect |
| ADV-P7-A20 | LOW | positive-coverage weak | ARCH-08:131-134; cicd-setup.md:85 | The timing job only requires `N > 0`. There is no census against the corpus, so timing 1 of N cases passes (Tier A and Tier B do use a census). | architect |
| ADV-P7-A21 | LOW | threshold without rationale (P16) | interface-definitions.md:247 | `telemetry.timeout_s` is bounded only by the Duration ceiling (about 292 years). A large value blocks the render, and no labeled upper bound or rationale is given (compare `rename_retry_delay_ms` 1..1000 J). | product-owner |
| ADV-P7-A22 | LOW | assumption timing | assumptions-register.md:29 | ASM-007 is to be validated "before Phase 3", but Phase 2 decomposes S1.07 (eight BCs) into stories against an unverified payload surface. Validating before Phase 2 story writing would avoid that. [owner-question] | product-owner |

## 2. Policy compliance

- **P1 append-only numbering:** PASS.
- **P2 lift invariants to BCs:** PASS (within perimeter).
- **P4 semantic anchoring:** FINDING A12, A14, A03.
- **P5 creators justify anchors:** PASS.
- **P6 subsystem names:** PASS (PRD §1.6 and module-criticality match the ARCH-INDEX registry).
- **P7 BC H1 is the title source:** PASS (all 154 PRD rows checked against BC H1s, no mismatch).
- **P9 VP-INDEX is the VP catalog:** PASS (41 = 33+7+1; methods sum to 41; module union 41/41).
- **P11 CI positive coverage:** FINDING A07, A08, A18, A20.
- **P12 settled decisions:** PASS.
- **P13 parity before behaviour change:** PASS (no new deviation outside the 12-id set).
- **P14 public-repo hygiene:** PASS.
- **P16 thresholds explained:** FINDING A21 (A19 minor).
- **P17 ledger format frozen:** PASS.
- **P18 cross-platform:** FINDING A10, A03.
- **P19 Go hardening toolchain:** PASS (lags disclosed with deadlines).
- **P20 config over code:** PASS on OD-05; A19 is an owner-question.
- **P21 public-artifact hygiene:** PASS (no flagged strings quoted).

## 3. Files not fully read

None in the perimeter; every perimeter file was read in full. Outside the perimeter, only these were opened, to check specific cross-references: BC-6.01.002, BC-6.04.002, BC-1.04.001 (part), BC-2.01.005 PC-7, BC-2.02.002 (grep), BC-1.05.005 (part), BC-3.01.001 (grep), the VP-INDEX catalog rows, and legacy SL:158-187, 700-729, 1195-1246.

## 4. Novelty

MEDIUM. A01, A03, A07, A10 and A11 are new structural gaps; the rest are propagation and drift from pass-6 fixes. **NOT_CONVERGED.**


## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 22 (high 0, medium 12, low 9, cosmetic 1).

**ADV-P7-A2: adversarial review, pass 7, perimeter A2 (brief, L2 domain spec, VPs, assessments)**

I found 21 findings: 12 MEDIUM, 8 LOW, 1 COSMETIC. None are CRITICAL or HIGH, but the MEDIUM findings mean the specs have not converged.

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P7-A2-01 | MEDIUM | semantic anchoring (P4) / L2↔PRD contradiction | domain-spec/capabilities.md:29; L2-INDEX.md:111; invariants.md:49 | CAP-007's Phase cell says "P1 (plan-window widgets, BC-1.02.030)". But BC-1.02.030 anchors `capability: "CAP-009"` (BC-1.02.030:15). prd.md:122 maps CAP-007 only to the reserved S9. L2-INDEX and invariants.md list the P1 slice as CAP-009/010/011/015 only. So the L2 claims P1 work for a capability that the PRD and the BC both place elsewhere. Also cosmetic: the cell cites SL:297-312, but `effective_rl` spans SL:298-312. | business-analyst |
| ADV-P7-A2-02 | MEDIUM | VP bcs reciprocity (P4/P9) | verification-properties/VP-012-exclusion-set-closure.md:13, 65-68, 197-200 | VP-012 names BC-1.04.001 as the OD-181 rider (`TestMetricsClient_OD181_TransportTable`), but its `bcs:` omits BC-1.04.001. BC-1.04.001's VP table cites only VP-022 and VP-030 (grep), and the VP-INDEX:193 map row matches that. Every other exclusion-riding BC (even BC-1.04.003 and BC-1.05.005, which have no rider test) was brought into `bcs:` under the SC-13/14/21 reciprocity convention. This is the one sibling that was missed. | architect |
| ADV-P7-A2-03 | MEDIUM | VP↔primary-BC contradiction / partial-fix propagation | VP-012:88-96, 174-196 vs BC-6.03.004:93-104 | VP-012 says its rider names are "as fixed by the rider BCs and the BC-6.03.004 register", but that register disagrees on four ids:<br>• OD-159: register rider is BC-1.03.001 PC-3, and BC-1.03.001 does not cite OD-159 at all (grep). VP-012 names BC-1.02.004.<br>• OD-160: register names BC-1.02.017 EC-010 and BC-1.01.008 EC-011; VP-012 names BC-1.05.004.<br>• temp-file: register lists one test; VP-012 has two entries.<br>• cp-x03: register still says the test name is provisional.<br>An implementer cannot tell which riders the closure check requires. | architect / product-owner |
| ADV-P7-A2-04 | MEDIUM | oracle gap (DI-012) / P11 | VP-012:56-61, 138-152, 155-166 | `TestParityExclusions_ClosedSet` only walks the exclusion entries. Some ids legitimately have no entry: OD-181 ("parity cases use plain http only") and the Text rider (`TestD4EX3_Text`, which "backs no parity entry", BC-6.03.004:95). Nothing checks that those ids' rider tests exist. Deleting `TestMetricsClient_OD181_TransportTable` would leave the check green, so DI-012's "every exclusion carries its own table tests" has no oracle for these ids. Separately, the mutation leg has no guard against an empty mutant catalogue, so it can pass while checking nothing. | architect |
| ADV-P7-A2-05 | MEDIUM | sibling not updated (partial-fix) | VP-014-d4ex1-windows-window-age.md:53, 69, 79; dtu-assessment.md:80, 89, 157 vs VP-012:177 | VP-012 v1.13 fixed the D4-EX-1 rider name as `TestWindowAge_D4EX1_Windows_AncestorFound`. VP-014, the VP that defines that test, still calls `TestWindowAge_D4EX1_Windows` the "settled name", and the DTU assessment repeats the old name. Two files are affected; the closure check would fail closed rather than pass silently. | architect |
| ADV-P7-A2-06 | MEDIUM | config over code (P20) / propagation | VP-031-bounded-resource-caps.md:39-43, 77-80 | VP-031 calls the 512 KB read step a "module constant `_READ_CAP`" and names no registry key for the 32-point history cap. BC-2.01.004:212-222 (PC-10, call 16, SC-16) registers both as config keys: `statusline.transcript.read_cap_bytes` and `statusline.sparkline.history_cap`, each with a range. VP-031 (last revised v1.2, 2026-11-17) was never updated. It also never says whether "legacy-identical" means the default values or what eviction does at non-default values. | architect |
| ADV-P7-A2-07 | MEDIUM | internal contradiction / P20 | VP-018-atomic-cache-writes.md:55-61, 99-101 | The statement calls the rename retry "an internal durability knob … no parity-visible behavior". The same statement (and OD-186) then says hylo "may persist a cache write legacy would not", which rides the widened `temp-file` exclusion — a parity-visible difference. The only stated reason for keeping `renameRetryLimit = 2` a constant instead of config was "no parity-visible behavior", so that reason no longer holds. | architect |
| ADV-P7-A2-08 | MEDIUM | vacuous oracle | VP-018:84-85 (Method), 137 | The Method asserts "no `.tmp` residue". Legacy's temps (SL:201) and the "mkstemp-pattern" temps the statement requires use the target's basename plus `.` as the prefix and have no suffix. A check keyed on a `.tmp` suffix can never see a leaked temp, so the assertion can never fail. The sketch's planted name (`*.json.tmp123`) repeats the wrong pattern. | architect |
| ADV-P7-A2-09 | MEDIUM | missing verification leg | VP-016-config-error-classes-line.md:37-53, 98-108 | The statement claims seven classes and says each class's reasons are pinned "inside the class tables". Only five tables exist (`TestD4EX3_{Number,Boolean,URL,Enum,Text}`), and the two theme legs test default bytes and accepted values only. No test pins the theme rejection line. BC-2.01.003 EC-002/EC-003 and its canonical vector (BC-2.01.003:99-111) route to no VP test. Because the corpus validator rejects theme settings, Tier A does not cover it either. | architect |
| ADV-P7-A2-10 | MEDIUM | ambiguity | VP-007-render-determinism-seams.md:37-41, 80-84 | The VP replays twice on the same recorded env. It does not say whether the first render's cache writes are visible to the second. If they are, the property silently claims the effect script is idempotent at a fixed clock. Legacy writes `rl_ts`, `fetch_ts`, `hist`, mix offsets, `proc_start` and cost history on the first run, and no BC states that claim. If they are not, the env must be reset, but the sketch reuses `e`. | architect |
| ADV-P7-A2-11 | MEDIUM | sibling of pass-6 fix not propagated | VP-041-row1-property-legs.md:126 vs 109-111, 152 | The Generators table says P-b's oracle is a "live `_hm` oracle call". The Method puts P-b in the in-tree quick set with no interpreter call, and the Tier C Proof Method row omits P-b. Pass 6 (A2-16) moved P-g's live oracle to Tier C but left P-b behind. | architect |
| ADV-P7-A2-12 | MEDIUM (sketch) | sketch contradicts property | VP-009-tier-a-live-parity.md:94-96 vs 39-40, 80-83 | The captures leg uses `LoadCases("captures")`, a cwd-relative path — exactly the A2-16 defect the sketch's own comment warns about. `go test` runs in the package directory, so captures load as zero cases, and the corpus count keeps n > 0, hiding it. The leg also skips `CompareNamedCaches`, although the statement requires named caches to match byte for byte. | architect |
| ADV-P7-A2-13 | LOW (sketch) | possible false fail | VP-001-never-blank-exit0.md:158-163 | In the subagent renderer branch, a JSON-object stdin with zero tasks is a legal zero-byte output (BC-1.07.004 PC6). The check `!isNDJSONRows(stdout)` fails on that unless `isNDJSONRows("")` is true, which is not defined. The statement also never says where zero tasks fall in the renderer branch. | architect |
| ADV-P7-A2-14 | LOW (sketch) | oracle incomplete | VP-021-cost-colour-goldens.md:97-108 | The quick-leg oracle `c.p75 == derivePercentile(rates, …)` ignores the `COST_MIN_N = 10` cold-start case (returns None) and the sid/lane/30-day/$1 filters in `cost_thresholds` (SL:240-262). With arbitrary-length rates, a correct implementation would fail it. | architect |
| ADV-P7-A2-15 | LOW | self-contradiction | VP-017-exactly-one-backend.md:41-47 | One sentence says the `backends=0` guard "is validated directly when the P4 file layer makes the case reachable". The next says it is "exercised NOW directly at the validator seam". This is leftover wording from the A2-09 fix. | architect |
| ADV-P7-A2-16 | LOW | wording mismatch | VP-015-config-resolution-totality.md:38 vs 75-76 | The statement says Load returns "a non-empty typed `*ErrorSet`". The Honesty paragraph says "exactly one of {*Config, single typed *Error}". | architect |
| ADV-P7-A2-17 | LOW | stale reference / wrong noun | VP-022-ledger-read-scope-absence.md:49, 90 | "(see Propagation note)" points to a section the file does not have. The allowed path set lists "metrics caches", but none of the four caches is a metrics cache; the sample lives in the session cache (ENT-14). | architect |
| ADV-P7-A2-18 | LOW [owner-question] | unfailable leg | VP-036-render-latency-p95.md:43-48 | Under OD-187, the >512 KB fixture is exempt when it misses the target and passes when it meets it, so it can never fail the gate and has no upper bound. The brief (product-brief.md:89) asks the spec to "state that exception explicitly", which suggests a stated number. | owner |
| ADV-P7-A2-19 | LOW [owner-question] | unnamed carve-out (DI-012) | VP-009:37-42; BC-6.01.002:125-127 | The oracle shim forces stdout to `newline="\n"`. Legacy on Windows would print CRLF (`print()` in text mode, SL:1234). That normalization is a carve-out outside the 12-id closed set, and OD-183 covers encoding only. VP-009 says only the closed set carves out differences. | product-owner |
| ADV-P7-A2-20 | LOW | toolchain claim (P19) | VP-037-three-os-ci-matrix.md:38 | "CGO_ENABLED=0 builds, `-race` on Linux and macOS legs": as I understand current Go (not checked against the release notes), `-race` on Linux needs cgo. The statement should say the race leg sets `CGO_ENABLED=1`. Confidence: MEDIUM. | architect |
| ADV-P7-A2-21 | LOW | frontmatter↔body drift | VP-006-json-depth-budgets.md:13 vs 81-83 | `bcs:` includes BC-5.02.004 and BC-1.07.003, but the Source Contract's partial-coverage list names only BC-1.01.002 and BC-1.03.004. | architect |
| ADV-P7-A2-22 | COSMETIC | stale wording | dtu-assessment.md:32-33, 48 | It says the legacy oracle hits the fake "in-process". The oracle is a separate child process (VP-034). | architect |

## 2. Policy compliance

- **P1 append_only_numbering:** PASS (VP-001..041 contiguous; no ID reuse).
- **P2 lift_invariants_to_bcs:** PASS (DI-007/008/010/012 enforced; others explicitly deferred under OD-115; DI-007 count of 38 re-verified by grep).
- **P4 semantic_anchoring_integrity:** FINDING: 01, 02, 03.
- **P5 creators_justify_anchors:** PASS.
- **P6 subsystem names:** PASS (spot check only).
- **P9 vp_index_is_vp_catalog_source_of_truth:** PASS on index-to-file sync (totals, titles and map are internally consistent). The underlying gap is 02.
- **P11 ci_positive_coverage_assertion:** FINDING: 04, 08.
- **P12 settled_decisions_are_constraints:** PASS (18 and 19 raised as owner questions).
- **P13 parity_before_behavior_change:** PASS (19 is an owner question).
- **P14 public_repo_hygiene:** PASS (scan for private IPs, home paths and identities: clean).
- **P16 thresholds_are_explained:** PASS.
- **P17 ledger_format_frozen:** PASS.
- **P18 cross_platform_from_day_one:** PASS.
- **P19 go_hardening_toolchain:** FINDING: 20.
- **P20 config_over_code:** FINDING: 06, 07.
- **P21 public_artifact_hygiene:** PASS (no flagged strings quoted).
- **P3, P7, P8, P10, P15:** N.A.

## 3. Files not fully read

None in the perimeter; every file was read in full. Outside it I only spot-checked BC-1.02.030, BC-1.04.001, BC-2.01.003, BC-2.01.004, BC-2.01.005, BC-3.01.001, BC-6.01.002 and BC-6.03.004, and the matching lines in `legacy/dgx_statusline.py`.

## 4. Novelty and convergence

Novelty: MEDIUM. Findings 03, 04, 06, 08, 09 and 10 are new gaps. 02, 05 and 11 are siblings that earlier fixes missed. The rest are refinements.

NOT_CONVERGED


## Perimeter B (BC-1.01/1.02)

Findings: 15 (high 1, medium 6, low 7, cosmetic 1).

1. **Findings**

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P7-B01 | HIGH | P7 title does not match postconditions | BC-1.01.003:33, BC-INDEX:69, prd.md:157; BC-1.01.007:33, BC-INDEX:73, prd.md:161; interface-definitions:164 | The BC-1.01.003 H1 says row 2 is shown "only when width permits". PC1 and EC-005 say `rows > 2` forces row 2 at any width (legacy SL:1224), so with rows=3 and COLUMNS=10 there are 2 rows. The BC-1.01.007 H1 says negative COLUMNS "hides row 2", but its PC3/EC-004 say rows >= 3 keeps row 2. The `statusline.rows` registry note repeats the same imprecision. | product-owner |
| ADV-P7-B02 | MEDIUM | Wrong bearer stated | BC-1.01.009:92-93 vs SL:224-262 | PC2 says the history-borne CP-O10/O11 raise is reachable "through a Python-written cost history (VP-019 swap) **or the mix cache**". `cost_thresholds` reads only `COST_HIST` (SL:245), and `record_cost` takes `usd`/`api_ms` from stdin (SL:601-606). No mix-cache value can reach SL:255. The phrase looks copied from BC-1.02.025 EC-010, where the mix cache is a correct bearer. | product-owner |
| ADV-P7-B03 | MEDIUM | A step-2 degrade is missing from the step table [P18] | BC-1.01.009:62 (step-2 "Can degrade?" cell); BC-1.01.001:57-62 (PC3 list of guarded sites) | ARCH-03:66 and BC-5.04.001 PC6 / v1.2.3 rule that a Windows MSVC `localtime_s` OSError escapes `_iso_ts` (SL:984 catches only ValueError) and degrades the whole line (`ErrLocaltimeDomain`). BC-1.01.009's normative order table leaves this out of step 2. BC-1.01.001 PC3 leaves it out too, and it is neither a CP site nor a panic. The error taxonomy has no CP id for it. | product-owner; architect (taxonomy id) |
| ADV-P7-B04 | MEDIUM | Mis-anchor | BC-1.01.001:58-59 | PC3 attributes "the metrics-borne numeric-`__name__` degrade" (CP-N03) to BC-1.04.014/015. Neither file mentions CP-N03 (grep). ARCH-03:102-105 and error-taxonomy:46 name BC-1.04.004/.005 (and .001) as the owners. | product-owner |
| ADV-P7-B05 | MEDIUM | Mis-anchor (cross-check) | BC-2.01.004:185 vs interface-definitions:171 | Names "Consumer: BC-1.02.011" for `statusline.lane.reroute_all_prefixes`. BC-1.02.011 is the pace/absolute bands contract. The consumer is BC-1.02.009 (PC1), which is what the registry says. | product-owner |
| ADV-P7-B06 | MEDIUM | OD-179 fix not carried to a sibling [P20] | BC-1.02.030:52-53, 88, 91, 138 | Still says "`backends[0].model_prefixes` controls reroute-all", and EC-007/EC-010 say "contains bare `claude`". Its Config keys row leaves out `statusline.lane.reroute_all_prefixes`. Since OD-179 the markers are config (BC-1.02.009 PC1). Pass-5 B09 fixed only the primary file. | product-owner |
| ADV-P7-B07 | MEDIUM | Unstated environment input | BC-1.02.004:49-52, 77-78, 212 | Claims cwd is read only on an "unreachable fallback" (Purity row: "cwd only on the unreachable fallback"). But `os.path.abspath(directory)` (SL:373) reads `os.getcwd()` for any relative `proj_dir`. Relative input is reachable: BC-1.02.003 EC-004 renders `"."` and `rel/dir`. PC1 does not route abspath through `Env.Cwd`, so a port using the process cwd would make harness results depend on cwd. | product-owner |
| ADV-P7-B08 | LOW | Mis-pointed footnote | BC-1.01.009:62 | "CP-S14/S16²" points at footnote ², which covers the OD-156 overflow family and OD-166. CP-S14/S16 are degrading crash paths (ARCH-03:66 "degrade sticky"; BC-1.03.013 EC-007), not overflow. | product-owner |
| ADV-P7-B09 | LOW | Internal inconsistency | BC-1.01.001:94 vs :117, VP-003:72 | EC-005 calls the `cp-x03` test name "provisional — architect (OD-145)". The same BC's VP-012 row and VP-003 pin `TestCPX03_WriteFailureExit0` as the canonical name. | product-owner |
| ADV-P7-B10 | LOW | Registry back-references incomplete | interface-definitions:199, 233, 238 | The Contract column for `units.tokens` leaves out BC-1.02.018 (it cites the key in Inv 3). `limits.windows` leaves out BC-1.02.011. `timer.min_ms` leaves out BC-1.02.016 PC1 and BC-1.02.027. | architect |
| ADV-P7-B11 | LOW | Taxonomy carrier list incomplete | error-taxonomy:46 | The E-REN-002 carrier list leaves out the CP-O01..O05 owners (BC-1.02.006/.011/.012/.014/.017/.025, listed per row at :137-141). It also leaves out the CP-S owners in this perimeter (BC-1.02.001, .030, BC-1.01.008). | architect |
| ADV-P7-B12 | LOW | Pass-6 B16 history-label sweep incomplete (pending intent verification) | BC-1.02.019:22-23, .020:22-23, .022:22-23, .024:22, .026:22, .030:22-23 | These `modified` entries still lack the version prefix that ADV-P6-B16 added to the sibling files. No behavioral effect. | product-owner |
| ADV-P7-B13 | LOW | Pass-6 B01 re-anchoring incomplete (pending intent verification) | BC-1.02.008:96, BC-1.02.014:133 | Rows labelled "property test vs CPython goldens" stay on VP-028. The ADV-P6-B01 sweep moved rows like these to VP-041, and VP-041:97-102 lists neither BC. They may be intended as bounded golden sweeps. | product-owner |
| ADV-P7-B14 | LOW | Overstated edge case | BC-1.01.009:113 | EC-001 says the mix cache is written unconditionally. Legacy writes it only when a transcript exists and has grown (SL:1009-1011, 1039-1040). | product-owner |
| ADV-P7-B15 | COSMETIC | Test-name spelling | BC-1.02.017:70 vs VP-012:76 | Uses the wildcard `TestWindowAge_D4EX1_Windows*`; VP-012 names the concrete test `TestWindowAge_D4EX1_Windows_AncestorFound`. | product-owner |

**Re-derived and correct (no finding):**
- Every postcondition and vector I recomputed matches the legacy code, quirks included:
  - Byte counts: 29-byte degraded line, 45-byte default line, 64-byte two-row output.
  - Staircase sums in BC-1.01.010.
  - All `heat` triples, plus the 50.4/51/84.5/true cases.
  - Half-even text: `/0K`, `/1000K`, `-0%`, `999500` → `1000k`.
  - Countdown floor-division and the 1.15 gate. `604800×1.15` and `18000×1.15` round to exactly 695520.0 and 20700.0.
  - The `1.0-0.9` pace boundary, which the 5h pct 8 vector does catch.
  - OV = 2**1024−2**970 as the smallest int that fails float conversion; the −OV compare at SL:506 never converts.
  - Python `max`/`min` NaN ordering, `int(inf)` vs `int(nan)` exception classes, `inf//60000 = nan`.
  - The `effective_rl` step sequence in BC-1.02.030.
  - ntpath 3.11 `splitdrive` results for `//`, `///`, `//x`.
- Config keys in this perimeter are registered with ranges that agree with the BCs.

2. **Policy compliance**
- P1: PASS
- P2: PASS
- P4: FINDING B04, B05, B06
- P5: PASS
- P6: PASS (SS-01 matches ARCH-INDEX:55)
- P7: FINDING B01 (all H1 = BC-INDEX = PRD titles match textually)
- P12: PASS
- P13: PASS
- P14: PASS (grep for paths, IPs and identities: clean)
- P16: PASS
- P17: N.A.
- P18: FINDING B03 (B07 also concerns host-environment portability)
- P19: PASS (FMA no-fuse and arm64 legs stated)
- P20: FINDING B06
- P21: PASS (no flagged strings quoted)

3. **Coverage and unverified claims**
- **Read fully:** all 40 perimeter BC bodies (frontmatter read in full for BC-1.01.001-003 and BC-1.02.*; the other BC-1.01.* frontmatters only through the `confidence`/`subsystem` fields), legacy SL:1-1246, and VP-041.
- **Read partially:** interface-definitions:140-274, error-taxonomy:40-59 plus grepped rows, ARCH-03:46-106 and the anchor list, invariants:30-40, capabilities rows, BC-INDEX/PRD rows, VP-INDEX rows, BC-2.01.004:180-187.
- **Not read:** VP-001, VP-003 (beyond grep), VP-005, VP-006, VP-008, VP-012 (beyond grep), VP-019, VP-022 (beyond grep), VP-027, VP-028 body, VP-040 body; test-vectors beyond grep.
- **Python claims I could not verify:**
  - SHA-1 cache keys in BC-1.02.005.
  - Golden byte totals (743/701/809/642/286) and the golden segment contents.
  - `_hm(5e23)` and `_hm(1e24)` exact digits (only checked as plausible doubles).
  - The 993/994 stdin depth boundary.
  - The 4,300-digit `int()` digit-counting detail (whether underscores count).

4. **Novelty:** MEDIUM. B02, B03, B04, B07 and B05/B06 are new substantive anchoring and semantic gaps; the rest are refinements. **NOT_CONVERGED**


## Perimeter C (BC-1.03/1.06/1.07)

Findings: 14 (high 1, medium 4, low 7, cosmetic 2).

## ADV-P7 Perimeter C: findings (status line BCs BC-1.03.*, BC-1.06.*, BC-1.07.*)

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P7-C01 | HIGH | Parity break that has no ruling (P13) | BC-1.06.001:119 (EC-011); BC-1.03.001:77 (EC-009); legacy SL:1010, SL:191, SL:201-204 | **What happens:** Both edge cases say hylo carries a lone-surrogate sid or path as a 3-byte WTF-8 sequence. Legacy encodes U+DC80..DCFF with surrogateescape as one raw byte. So the session-cache file name differs byte for byte, and the transcript probe opens a different file.<br>**Why it is a finding:** No OD ruling covers this (the OD log has no surrogateescape or WTF-8 entry) and no id in the closed set of 12 covers it. Instead it leans on OD-03, which only rules "raw sid kept".<br>**Fix:** On POSIX, Go can reproduce legacy, because file names are bytes. Either specify the surrogateescape-equivalent encoding, or get a ruling plus an exclusion id. [owner-question] | product-owner |
| ADV-P7-C02 | MEDIUM | Spec text gives the wrong output bytes | BC-1.07.004:57-59 (PC3); legacy SL:924 | **What happens:** PC3 lists the short escapes as only `\n`, `\t`, `\r`, and says `\uXXXX` covers "the rest". CPython's `ensure_ascii` encoder also emits `\b` (0x08) and `\f` (0x0C) as short escapes.<br>**Impact:** A task name holding a backspace or form feed goes on the wire as `\b` or `\f`, not `\u0008` or `\u000c`. Anyone implementing from PC3 breaks byte parity.<br>**Fix:** Add `\b` and `\f` to the PC3 list. | product-owner |
| ADV-P7-C03 | MEDIUM | Test vector cannot be reproduced as written | BC-1.03.010:125 (NaN-id row) | **What happens:** The row says "compact lines", but its 420 B size only works with `json.dumps` default separators. U0 is 100 B and each NaN assistant line is 160 B: 100 + 2×160 = 420. The compact form gives 92 + 2×146 = 384.<br>**Fix:** Replace "compact" with "default separators". | product-owner |
| ADV-P7-C04 | MEDIUM | Quirk not pinned in a spec or test | BC-1.07.007:54-61, EC table 94-104; legacy SL:876-883, 909-911 | **What happens:** A `tokenCount` of `Infinity` or `1e400` decodes to float inf, passes the `> 0` gate, and renders `infM tok`. Go's `fmt` prints `+Inf`.<br>**What is missing:** No edge case or vector pins this, although BC-1.07.003's refactoring note says legacy accepts and renders Infinity. `startTime` = Infinity clamps to `00:00`, and that is unpinned too.<br>**Fix:** Add edge cases and vectors for both. | product-owner |
| ADV-P7-C05 | MEDIUM | VP link one-sided; earlier fix not copied to sibling | BC-1.06.001:130-136 (VP table), 166-169 (VP anchors) vs VP-012 `bcs:` | **What happens:** VP-012 lists BC-1.06.001 in its `bcs:`, and PC1 (line 77) says the check is "validated by the VP-012 closure check". But BC-1.06.001 has no VP-012 row and no VP-012 anchor.<br>**Why it is a finding:** Sibling BC-1.06.002 received exactly this row in pass 5 (ADV-P5-C15), so the fix was not copied across. | product-owner |
| ADV-P7-C06 | LOW | Stale cross-reference | BC-1.07.001:80 (EC-003), :119 (Related BCs) vs BC-4.01.002:89 | BC-1.07.001 still says BC-4.01.002's EC-004 "positional data" reading must defer or is superseded. BC-4.01.002 EC-004 was already aligned in v1.1.3, so the text points at a reading that no longer exists. | product-owner |
| ADV-P7-C07 | LOW | Vector contradicts itself | BC-1.03.007:106 vs :98-100 | The turn-drop leg says "the same seed cache" with `ids ["x"]`. The seed defined three lines above has `ids: []`. The expected result depends on the `["x"]` variant. | product-owner |
| ADV-P7-C08 | LOW | Vector depends on a template it does not define | BC-1.03.006:114 | `A_x` and `A_y` are built from "the A-template", which is defined only in BC-1.03.010:121 and BC-1.03.016:47. I re-derived the 163 and 486 B sizes from that template. BC-1.03.006 should define the template inline or cite where it lives. | product-owner |
| ADV-P7-C09 | LOW | Cross-platform claim untrue on Windows (P18) | BC-1.06.001:80, :125 | "Mode 0600" is stated with no OS qualifier. On Windows Go reports 0666 or 0444, so the happy-path vector's mode assertion cannot pass on the windows CI leg. | product-owner |
| ADV-P7-C10 | LOW | Config registry contract column incomplete | interface-definitions.md:170, 178, 182-183, 188-189 | The "Contract" cells for `backends[0].model_prefixes`, `theme.cyan/grey/magenta` and `pill.label_local/label_cloud` omit BC-1.07.006 and BC-1.07.007, although both BCs consume these keys. The `model_prefixes` cell also omits BC-1.07.008 (CP-A03). | architect |
| ADV-P7-C11 | LOW | Literal display text instead of a config key (P20) | BC-1.07.005:54-55, EC-004 (also BC-1.02.002:35); legacy SL:895 | The name fallback `?` is a hard-coded literal. The equivalent `?` in the lane pill is a config key (`statusline.pill.label_unknown`, OD-173). Is this a format constant or a label? [owner-question] | product-owner |
| ADV-P7-C12 | LOW | VP row claims too much | BC-1.07.008:112 | "Every fault routed to the subagent renderer ends in exactly the 29 degraded bytes" contradicts two other rules. BC-1.07.003 says stdin faults produce zero bytes. EC-009 says a row-write EPIPE makes no degraded-line attempt. | product-owner |
| ADV-P7-C13 | COSMETIC | Wrong cross-reference | prd.md:640 | "BC-1.07.001/.002 PC-2": in BC-1.07.002 the ASSUMP-107-1 assumption is precondition 1, not 2. | product-owner |
| ADV-P7-C14 | COSMETIC | Garbled text | BC-1.07.007:54-55; BC-1.07.008:83; BC-1.07.004:106; BC-1.07.005:74; BC-1.07.006:35-36, 81 | In BC-1.07.007:54-55 the clause "where `<suffix>` is…" is attached to the wrong sentence. BC-1.07.008:83 has a stray "`{}`-less". Wire-escape notation shows up in plain prose: the `\u2014`, `\u25cd`, `\u25e8DGX` and `\u25e8ANTH` literals. | product-owner |

What I checked and found correct (no finding):
- **Byte counts by hand:** I re-derived every byte count in the vectors of BC-1.03.002, .003, .004, .005, .006, .007, .008, .011, .012, .014, .016 (T1, T13, T16 and the rules of all 20 rows), .019 (all 21 rows), .020 and .021. All of them match, apart from C03 above.
- **Subagent goldens:** BC-1.07.004, .005, .006 and .007 match legacy SL:845-936.
- **Crash-path catalogues:** CP-A01..A05 is complete. Deep name repr and deep id dumps are within the recursion budget. CP-T01..T07 and CP-O06..O08 match the raise sites.
- **Config:** every key is registered with the same range the BC states.

### 2. Policy compliance

- **P1 append-only numbering:** PASS. IDs are contiguous (1.03.001-021, 1.06.001-002, 1.07.001-008).
- **P2 lift invariants to BCs:** PASS.
- **P4 semantic anchoring:** FINDING (C05, C06, C13).
- **P5 creators justify anchors:** PASS.
- **P6 subsystem name:** PASS. All are "SS-01", which matches ARCH-INDEX.
- **P7 titles:** PASS. All 31 H1 titles match BC-INDEX and the PRD.
- **P12 settled decisions are constraints:** PASS.
- **P13 parity before behavior change:** FINDING (C01).
- **P14 public repo hygiene:** PASS. The private-term and IP/path scan of all 31 files is clean.
- **P16 thresholds explained:** PASS.
- **P17 ledger format frozen:** N.A. No ledger access in this perimeter (DI-007).
- **P18 cross-platform:** FINDING (C09).
- **P19 Go hardening toolchain:** PASS.
- **P20 config over code:** FINDING (C11, owner-question).
- **P21 public artifact hygiene:** PASS.

### 3. Not fully read, and Python claims I could not verify

**Not fully read:**
- For BC-1.03.003-.021 I read from line 29 to about line 108-188. The trailing brownfield and anchor sections were truncated on several, and I checked frontmatter only by grep.
- Cross-check files read only partly or by grep: ARCH-03 (lines 100-274), interface-definitions, error-taxonomy, the VP files (`bcs:` lines only), BC-5.02.006 and BC-5.04.001 (excerpts).
- Not read at all: capabilities.md, the test-vectors supplement, ARCH-04.

**Python claims I could not verify:** I did not run CPython. All byte math was done by hand.
- The BC-1.03.002 EC-009 claim that a negative `seek` raises `OSError` (not `ValueError`).
- The digit count of the 10^309 literal pinned in the BC-1.03.010 CP-O08 golden.
- `conv` 5 in the BC-1.03.006 and BC-1.03.007 turn-drop legs. It holds only if the A-template text is `"x"`.
- The BC-5.02.006 encoder budgets.
- That passing a bool `transcript_path` as a descriptor only warns, on stderr.

### 4. Convergence

Novelty: MEDIUM. C02, C03 and C04 are new defects in the output bytes. C01 has been visible since pass 3 (ADV-P3-C21) but was never ruled.

NOT_CONVERGED


## Perimeter C2 (BC-1.04/1.05)

Findings: 14 (high 3, medium 4, low 7, cosmetic 0).

**Adversarial review, Phase 1d, pass 7, perimeter C2 (BC-1.04.\*, BC-1.05.\*)**

I opened every cited legacy line and re-derived the Python results by hand. The KV and sparkline cells and fades, the TTFT/$/⛏ rounding, the percentile indices, the NaN sort orders, the 37-hop redirect cap, the 11-step cache bytes and the 21-session goldens all match. The defects below are in what the specs say about the minimal metrics client, plus a few sibling-propagation and anchor gaps.

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P7-C2-01 | HIGH | spec gap (silent production failure) | BC-1.04.001:55-65, :253; ARCH-03:184-217 | **No response body framing is specified for the hand-written HTTP/1.1 client.** Legacy `resp.read()` (SL:171) goes through `http.client`, which de-chunks `Transfer-Encoding: chunked`, honours `Content-Length`, and otherwise reads to EOF. The BC says only "parses the response body raw". A literal implementation feeds chunk-size lines to `json.loads`, so every chunked reply gives no sample, where legacy gets one. The VP-030 row (:253) still puts framing out of scope because "net/http and http.client frame-parse differently". That reason is stale since pass 6 removed net/http: framing is now hylo's own code. Confidence: MEDIUM (spec text verified; I did not check whether the production metrics store actually chunks). | product-owner + architect |
| ADV-P7-C2-02 | HIGH | wrong normative rule | BC-1.04.001:66-73; ARCH-03:191-192 | **Header values are wrongly said to strip "only CR/LF".** CPython 3.11 compat32 `header_source_parse` does `value.lstrip(' \t')` and then `rstrip('\r\n')`, so leading spaces and tabs are stripped too. A parser built from the stated rule keeps the space after the colon: `Location: /x` becomes target ` /x`, quoted to `%20/x`, which resolves to the wrong URL. Multiple spaces or a tab also diverge. The BC's own `/x␠` example quietly assumes the leading strip. Both files carry the error. Tag: P13. | product-owner + architect |
| ADV-P7-C2-03 | HIGH | partial-fix gap, 2+ files (VP-012 reciprocity) | BC-1.04.001 VP table :249-256 and DI row :265; BC-1.04.002 EC-008 :95 and VP table :112-113; VP-012:13, :70-96, :197; VP-INDEX:193-194 | **Two exclusion carriers are missing their closure-check rows.** BC-1.04.001 carries OD-181, and VP-012 names its riding test `TestMetricsClient_OD181_TransportTable (BC-1.04.001)` (:197). But BC-1.04.001 has no VP-012 row and never names the test; VP-012 `bcs:` and its Source Contract omit BC-1.04.001; the VP-INDEX coverage row omits VP-012. Separately, BC-1.04.002 EC-008 carries OD-160, yet it has no VP-012 row and is not in VP-012 `bcs:`, while its siblings BC-1.04.003 and BC-1.05.005 received exactly that row (ADV-P5-C2-17). | product-owner + architect |
| ADV-P7-C2-04 | MEDIUM | contradiction / ambiguity | BC-1.04.001:55 vs :99-103; ARCH-03:184 vs interface-definitions:169 | **"Plain http only" contradicts the TLS rules in the same postcondition.** :55 says the client is "plain http only (OD-181)". :99-103, and the registry row allowing "scheme http(s)", say hylo verifies https certificates against the OS trust store. One reading gives no sample for any https metrics URL; the other requires a TLS dial over the `net.Conn`. The intent appears to be that parity cases are plain http only, but the text does not say so. | product-owner |
| ADV-P7-C2-05 | MEDIUM | VP cannot verify the BC | VP-030:72-75, :85, :131 vs BC-1.04.001:63, :68 | **VP-030's httptest fake cannot exercise the transport rows it claims.** It names "httptest fake" for the transport table. Go's server canonicalises incoming headers into a map, so urllib's header order cannot be observed. Its `Header.writeSubset` trims values with `textproto.TrimString`, so it cannot send `Location: /x␠` (the ADV-P6-C2-05 quirk). A raw `net.Listener`, or a hijacked connection, is needed. | architect |
| ADV-P7-C2-06 | MEDIUM | wrong site / false totality | BC-1.04.002:75-78 vs BC-1.04.003:60-61, EC-009 :105 | **The degrade sites in Invariant 1 are wrong and incomplete.** It places the IndexError at "a non-dict point `hist[-1]`". Actually `_norm_pt` raises it at SL:655 (called from SL:335) for any list point shorter than 2, anywhere in the history. After normalisation `hist[-1]` is always a dict. "Total except" also leaves out the TypeError sites: a non-numeric `t` at SL:336, `fetch_ts` at SL:324, `ts` at SL:325. These shapes are foreign (OD-160), but an implementer following this invariant guards the wrong expression. | product-owner |
| ADV-P7-C2-07 | MEDIUM | P20 config over code | BC-1.04.004:45-46, :50; BC-1.04.005:47-52; interface-definitions:188, :266 | **The dead-marker word has no config key.** Precondition 3 says the dead label comes from theme and glyph keys, but only `glyphs.degraded` (◌) exists. The word "DGX" in `◌ DGX ?` is not sourced from any key; OD-173 made the same word a key (`pill.label_local`) only for the pill. The `vLLM down` / `LMCache down` labels, and the `up:vllm` / `up:lmcache` job keys, are hard-coded even though `telemetry.query` (which selects those jobs) is configurable. Tag: [owner-question] (may be intended under OD-173 or OD-02 scope). | product-owner |
| ADV-P7-C2-08 | LOW | wire detail missing | BC-1.04.001:104-110, :140-141 | **The BC never says the next GET drops the URL fragment.** The loop key keeps a non-empty fragment, but urllib's `Request` splits it off (`_splittag`), so the request line never carries `#frag`. A client following the BC literally could send it. | product-owner |
| ADV-P7-C2-09 | LOW | stale anchor | BC-1.04.001:267 | "listed in ARCH-03 §Interfaces, line 114": ARCH-03:114 is the `Main` wiring comment. `MetricsClient` is at :183 and `telemetry.go` is listed at :235. The anchored section is right; only the line label is stale. | product-owner |
| ADV-P7-C2-10 | LOW | imprecise threshold | BC-1.05.005:109 | EC-011 says the overflow happens at ">= 2\*\*1024". Python's int-to-float coercion at SL:255 already raises from 2\*\*1024 − 2\*\*970, which is the value BC-1.05.004 PC1 and BC-1.05.007 PC6 use. | product-owner |
| ADV-P7-C2-11 | LOW | VP precondition missing | BC-1.04.021:78 | The property "every appended point is ≥ TTL after the previous" fails under a backward clock step, which the same BC admits (Description, EC-003). The VP needs a monotonic-clock precondition. | product-owner |
| ADV-P7-C2-12 | LOW | sibling wording not propagated | ARCH-03:102-104 vs error-taxonomy:15 (C2-21) | ARCH-03 still says CP-N03 is a numeric key "sorting ahead of" every `vllm:` key. The taxonomy was corrected to insertion order (dicts are not sorted, SL:717 `any()`). | architect |
| ADV-P7-C2-13 | LOW | taxonomy understates the ladder | error-taxonomy:51; prd:503 | E-NET-001 says "freshness ladder down to the stale suffix". Past KEEP_DEAD the outcome is the dead rung `◌ DGX ?` (BC-1.04.002 PC4, BC-1.04.020 step 5), and BC-1.04.002 is not cited. | product-owner |
| ADV-P7-C2-14 | LOW | vector register mismatch | test-vectors:43 vs BC-1.04.004 EC table :70-79 | The register lists BC-1.04.004 as a CP-N03 owner with at least one vector row. BC-1.04.004 mentions CP-N03 only in Invariant 3 and has no vector row; BC-1.04.005 EC-007 and BC-1.04.001 EC-013 do have rows. | product-owner |

## 2. Policy compliance

- P1 append_only_numbering: PASS (EC-006b was renumbered to EC-010; no inserted ids remain).
- P2 lift_invariants_to_bcs: PASS.
- P4 semantic_anchoring_integrity: FINDING 03, 09.
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS (`SS-01`, as in ARCH-INDEX:55).
- P7 BC H1 = BC-INDEX = PRD title: PASS (all 30 titles match three ways).
- P12 settled_decisions_are_constraints: PASS (07 is raised as an owner-question, not a challenge).
- P13 parity_before_behavior_change: FINDING 01, 02 (parity of the transport surface).
- P14 public_repo_hygiene: PASS (only 192.0.2.x addresses; no paths or identities).
- P16 thresholds_are_explained: PASS.
- P17 ledger_format_frozen: PASS.
- P18 cross_platform_from_day_one: PASS.
- P19 go_hardening_toolchain: N.A. (nothing in this perimeter).
- P20 config_over_code: FINDING 07.
- P21 public_artifact_hygiene: PASS.

## 3. Unread files and unverified claims

**Not fully read:** prd.md (only BC rows and the E-NET line), domain-spec/invariants.md, ARCH-04-data-files.md, VP-001, VP-019, VP-020, VP-021, VP-022, and BC-5.02.003 (only checked for the 4,300-digit rule).

**Python claims I could not verify:** I reasoned from the CPython stdlib source and could not run anything. Not verified:
- The fetch-site JSON depth limit of 992 accepted / 993 rejected.
- The exact byte capture of the request headers.
- The CPython 3.11.7 trust-store behaviour.
- `round(True, 4)` returning int 1 (consistent with the `int.__round__` source).
- The 12-cell trail RGB values beyond i=0, 1 and 2.

## 4. Novelty and convergence

Novelty: MEDIUM. Findings 01, 02, 04 and 05 are new holes in the minimal-client spec added in pass 6. Finding 03 is a partial-fix propagation gap. The rest are refinements.

NOT_CONVERGED.


## Perimeter D (S2-S6 BCs)

Findings: 27 (high 6, medium 11, low 10, cosmetic 0).

## Adversarial Review: Phase 1d, Pass 7, Perimeter D (SS-02..SS-06)

I read all 53 perimeter BCs fully. Of the 27 findings, 5 are HIGH and 12 MEDIUM, so the perimeter has not converged. Four of the HIGH findings are about one value being stated in incompatible ways across files.

### 1. Findings

| ID | Sev | Category | File:line | Defect (evidence) | Owner |
|---|---|---|---|---|---|
| ADV-P7-D01 | HIGH | contradiction / testability | BC-2.01.005:147-152; BC-2.01.004:89-92; interface-definitions.md:197-199, 233, 287-293 | PC-7 names the default-only env vars `HYLO_LIMITS_WINDOWS`, `HYLO_UNITS_LINES`, `HYLO_UNITS_TOKENS`, `HYLO_UNITS_CONTEXT`. Under the BC-2.01.004 PC-2 `EnvName` rule these are `HYLO_STATUSLINE_*`, and interface-definitions spells them that way. As written, a test vector sets an unknown setting and gets a warning instead of acceptance. `units.context` gets no concrete spelling (interface says `K`). The registry default for `units.lines`/`units.tokens` is shown as `k`/`M` while the env spellings are `k` and `M` respectively, so the parsed-vs-default comparison is undefined. | product-owner (+architect for interface table) |
| ADV-P7-D02 | HIGH | vocabulary gap | BC-2.02.001:98-123, 138-141; error-taxonomy.md:83, 87-88; BC-2.01.004:184; BC-2.01.005:131-135 | BC-2.02.001 calls itself the canonical home of the reason vocabulary, but lacks the pass-6 strings `ascending pair violated (k_from <= m_from)` and `expected non-empty control-free text in every entry`. It also maps `control character` only to the URL and theme classes, not Text. The taxonomy says BC-2.01.004 raises the first two; grep finds neither string in any SS-02 BC. The joiner's control-byte reason is `control character` per the taxonomy but `expected non-empty control-free text` per BC-2.01.005 PC-6 ("every other Text key"). | product-owner |
| ADV-P7-D03 | HIGH | untestable error surface | BC-2.02.002:51-54; BC-2.02.003:71-72, 85-86; interface-definitions.md:194, 206, 208, 213-214 | The range-check order and reason strings are defined for `Seconds` keys only. For Int/Float/composite keys BC-2.02.003 PC-5 just says "the key's registry range". Which bytes appear for `kv.cells=0` (range 1..100), `turn.floor_tps=nan`, `context.plain_max=inf`, a descending `cost.percentiles`, or `cost.min_sessions=0` (`out of range`, `must be > 0`, `not finite`, `negative`?) is undefined. ARCH-02 has no rule either (grepped). | product-owner |
| ADV-P7-D04 | HIGH | contradiction (fail-closed harness constants) | BC-6.01.001:81-87 vs BC-5.02.006:82-84, 144; BC-5.02.003:79-80; VP-006:138-149 | The OD-185 self-check probe ("one helper function at script scope") must read decode 994, `json.dumps` 994, `json.dump` 995. Under the pinned laws (decode 999−F; dumps 994−s; dump 995−s; s ≥ 1, EC-007 says module scope = 993/994), no single convention yields that triple. Decode 994 means accepted at F=5; dumps 994 / dump 995 mean first-rejected at s=1. VP-006's skeleton checks entirely different constants (end-to-end flips 993/992). The gate either reds every CI leg or is implemented to match nothing. | product-owner + architect |
| ADV-P7-D05 | HIGH | three-way contradiction (exact-set assert) | BC-6.01.002:67-95, 169; VP-034:95-105; ARCH-07:72-84 | Windows oracle allowlist: the BC requires HOME+USERPROFILE+TMPDIR+LANG+TMP+TEMP+SYSTEMROOT+PYTHONIOENCODING with no PATH unless a fake table is declared. VP-034 omits HOME/TMPDIR/LANG and adds HOMEDRIVE/HOMEPATH. ARCH-07 always includes PATH, omits HOME on Windows and USERPROFILE on POSIX. Each artifact claims an exact key set, so a correct implementation of one fails another's assertion. | architect + product-owner |
| ADV-P7-D06 | HIGH | contradiction / Windows parity (blast radius 4) | BC-5.04.001:46-48 vs :82-83; BC-5.04.002:43-45; ARCH-06:33, 188; BC-6.04.003:81-82 | BC-5.04.001 PC-6 correctly says legacy degrades for naive wall times "on or before 1970-01-01", because CPython's fold-0 `u1-86400` probe hits MSVC `localtime_s`. Its own Description ("[1970-01-01, year 3001)"), ARCH-06 and BC-6.04.003 ("before 1970-01-01") say otherwise. BC-5.04.002 says only "an instant outside the domain" without saying the check applies to every probe (t, u1, u1−86400, u2). A Go port following the Description returns a value for naive `1970-01-01T12:00:00` (TZ=UTC) where legacy degrades. | product-owner + architect |
| ADV-P7-D07 | MEDIUM | stale signature | BC-5.04.001:54-55; ARCH-06:187 | Pre-1 still says a non-string returns `(0, false)`. The canon is `FromISOFormat(s string, loc, msvcDomain) (float64, error)` with `ErrValue`. A `string` parameter also cannot receive a non-string Value, so who owns the non-str check is contradictory. | product-owner |
| ADV-P7-D08 | MEDIUM | contradiction | BC-2.01.001:62-67 vs BC-2.01.003:77; interface-definitions.md:191, 228, 246 | PC-2 says any present-but-empty Text value is a config error ("fails the non-empty range"). But `theme.separator`, `subagent.joiner` and `telemetry.query` are registered as free text / any text with no non-empty bound. It is undecidable whether `HYLO_STATUSLINE_THEME_SEPARATOR=` errors. | product-owner |
| ADV-P7-D09 | MEDIUM | undeclared type | BC-2.01.005:97-99, 115; BC-2.01.004:72-76; interface-definitions.md:212 | `statusline.sparkline.scale` has shape `array of 4 numbers`, but no registry Type declares a 4-tuple (the composites are FloatPair, FloatTriple, IntMap, RGBTriplesFloat, NumberList). If it is NumberList, the shape is `array of numbers` and `[1,2,3]` passes the shape check. The expected bytes for that input are undefined. | product-owner + architect |
| ADV-P7-D10 | MEDIUM | ordering gap | BC-2.01.002:69-84; BC-2.02.001:67-69, 75 | `backends` cardinality is not a registry key, yet stdout shows "the first error in registry order". With `HYLO_BACKENDS_1_METRICS_URL` and `HYLO_STATUSLINE_ROWS=x` both set, which line prints is unspecified. `<value>` = the synthesized count also contradicts PC-3 ("the raw string as supplied"). | product-owner |
| ADV-P7-D11 | MEDIUM | P7 title vs postconditions | BC-2.02.002:38 vs :63-70 | The H1, BC-INDEX and PRD title all say "negative durations are config errors". PC-2 admits negative `statusline.git.ttl_s` down to the mirrored floor, so the title misdescribes a postcondition. | product-owner |
| ADV-P7-D12 | MEDIUM | P18 / injection | BC-3.01.001:48 vs :98, 171-173; BC-2.01.005:69-73 | Pre-2 takes the home directory from `os.UserHomeDir`, which reads the real process env. That contradicts Inv 3 and the purity table ("depends only on the injected env"), and BC-2.01.001 PC-6's rule that config reads go only through `platform.EnvVars`. The `~` expansion's home source is not routed through the seam. | product-owner |
| ADV-P7-D13 | MEDIUM | mis-anchor | BC-2.01.004:228-235; interface-definitions.md:173; BC-6.03.003:58-64, EC-004 | The consumer of `statusline.cache.rename_retry_delay_ms` is BC-6.03.003 (a harness BC) here, but BC-1.06.001 in interface-definitions. The Windows retry behavior, which is product cache-store logic, is specified only inside a harness contract. | product-owner + architect |
| ADV-P7-D14 | MEDIUM | mis-anchor | BC-6.01.001:92-93; BC-6.02.003:92-93; BC-6.03.001:49; ARCH-07:134 | Three BCs identify subagent cases by an "id suffix `-sub`". ARCH-07's case-id grammar has a `subagent` family (`<family>-<nnn>[-<variant>]`), so the validator's family rule is ambiguous. | architect + product-owner |
| ADV-P7-D15 | MEDIUM | incomplete enumeration | BC-6.03.004:139-150; BC-2.02.003:127 | PC-3 claims the Number values are named exhaustively (crash leg vs two-legged asymmetry). It omits values from the Number exclusion list in BC-2.02.003: `2_0`, `٢`, `99999999999999999999` (all accepted by legacy `int()`, so they render), and `9223372036.854776`. `-inf` (BC-2.02.002) is also omitted. The oracle leg to pin is therefore unstated for those cases. | product-owner |
| ADV-P7-D16 | MEDIUM | domain gap | BC-6.04.003:71-91, 123-124; error-taxonomy.md (OD-166, CP-O06..O08) | The Tier C out-of-domain list omits OD-166 (huge-int `usd`/`api_ms`, so cost-history bytes diverge) and the transcript-overflow D4-EX-2 extension. Inv 3 says the exclusion list "applies if a generated case hits a listed shape", but entries are keyed by case path and cannot match a generated case. | product-owner |
| ADV-P7-D17 | MEDIUM | stale / anchor | BC-6.02.003:95-96, 161-162, 212 | Three problems. First, the note "architect to align ARCH-07" is stale (ARCH-07:135 is already aligned). Second, the provenance cites "SL:73-79, 92"; SL:92 is a comment, the trace read is SL:89, as PC-2 itself says. Third, the LocalZone legs omit "empty" (BC-3.01.001 lists five). | product-owner |
| ADV-P7-D18 | LOW | anchor | BC-2.01.004:132; legacy dgx_statusline.py:906-907; interface-definitions.md:266 | The subagent `◨` glyph is cited at SL:902-903. That is the prefix read; the glyph is at SL:906-907, which interface-definitions cites. | product-owner |
| ADV-P7-D19 | LOW | wording | BC-5.01.007:105-107; legacy SL:254 | It calls the legacy gate "`api_ms / 3.6e6`". The gate is `api >= need`; the division at SL:255 follows it. | product-owner |
| ADV-P7-D20 | LOW | ambiguity | BC-5.04.002:58 | "Otherwise b = t1 − u1" can be read as the else-branch of `a == b`; in CPython it is the else-branch of `t1 == t`. The misreading gives wrong overlap results (goldens would catch it). | product-owner |
| ADV-P7-D21 | LOW | internal contradiction | BC-2.01.004:200-202 vs :157-159; ARCH-06:225-226; BC-5.03.001:54 | PC-9 applies the validation width to "the general Text ranges of BC-2.01.005 PC-6"; PC-6 and ARCH-06 say ONLY the pill-label bound. BC-5.03.001 Inv 1 bans EA-width logic without restricting it to the render path. | product-owner |
| ADV-P7-D22 | LOW | interface gap | ARCH-06:128-189 | The interfaces block lacks signatures for NumLT, NumLE, NumGT, NumGE, NumEQ, NumNE (mandated by BC-5.01.007 PC-3b) and for the validation-width function. | architect |
| ADV-P7-D23 | LOW | contradiction | BC-2.02.005:72, 105 vs :61-65 | Inv 1 and the VP say "has a host / host ≠ ''", while PC-4 accepts `http://:8428` with an empty `Hostname()`. | product-owner |
| ADV-P7-D24 | LOW | contradiction | BC-6.03.002:67-69 vs BC-6.03.004:141-143 | "A non-zero value on either side is a failure", yet the D4-EX-3 Number crash leg (and cp-x03) pins oracle exit 1. | product-owner |
| ADV-P7-D25 | LOW | grammar gap | BC-2.01.002:53-55, 97-98 | Well-formedness of `<FIELD>` is undefined for `HYLO_BACKENDS_1`, `HYLO_BACKENDS_1_`, or a lowercase field on Windows. | product-owner |
| ADV-P7-D26 | LOW | P16 | BC-6.04.002:65-69 | The warm-up is justified, but "20 timed runs" has no rationale. | product-owner |
| ADV-P7-D27 | LOW | CLI gap | BC-2.03.002:55, 63; BC-4.01.001:60-61 | `config path --config=x` and a bare `--config` with no value are undefined (usage, or accepted?). | product-owner |

### 2. Policy compliance

- **P1 (append-only numbering):** PASS.
- **P2 (lift invariants to BCs):** PASS (DI-008, DI-010, DI-012 are cited).
- **P4 (semantic anchoring):** FINDING D13, D14, D17, D18, D19.
- **P5 (creators justify anchors):** PASS (OD-153 rationale is present).
- **P6 (subsystem names):** PASS.
- **P7 (titles):** FINDING D11.
- **P12 (settled decisions):** PASS (no challenges, no [owner-question]).
- **P13 (parity before behavior change):** PASS.
- **P14 (public-repo hygiene):** PASS (RFC 5737 addresses and synthetic paths only; the BC-6.02.001:93 hostname example is labeled synthetic).
- **P16 (thresholds explained):** FINDING D26.
- **P18 (cross-platform):** FINDING D06, D12.
- **P19 (Go hardening):** PASS.
- **P20 (config over code):** PASS (named constants carry why-not-config notes).
- **P21 (public-artifact hygiene):** PASS.
- **P3, P8, P9, P10, P11, P15, P17:** N.A.

### 3. Not fully read, and Python claims not verified

**Read only in part:** interface-definitions.md (lines 150-310), VP-006 (lines 80-160).

**Not read:** ARCH-01/02/03/04/05/08, capabilities.md, the prd-supplements other than error-taxonomy, BC-ALLOCATION.md.

**Python claims I could not verify:**
- `ntpath.normpath("//")` → `\\` (BC-5.03.004:51). I believe the 3.11 pure-Python fallback that runs on macOS returns a single `\`.
- The exact MSVC `localtime_s` year-3001 bound.
- The canary round trip `…4245193` → `…4245195`.
- Golden byte totals 1,179 / 1,120 / 999 (I re-checked the segment values but did not recount bytes).
- utf-32 decoding with `surrogatepass`.
- Whether leading zeros count toward the 4,300-digit limit.
- Whether repr recursion can be reached for deeply nested `Str` inputs.

### 4. Novelty and convergence

**Novelty: MEDIUM.** D01, D04, D05 and D06 are new cross-file contradictions introduced or exposed by the pass-6 edits.

**NOT_CONVERGED**

