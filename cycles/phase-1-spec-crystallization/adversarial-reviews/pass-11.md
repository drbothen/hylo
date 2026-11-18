---
document_type: adversarial-review
phase: 1d
pass: 11
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 62
---

# Adversarial Spec Review — Phase 1d, Pass 11

Pass 11 ran as six fresh-context perimeters, the same split as passes 1-10. Each section is the verbatim final report of one perimeter, unedited except for this framing. NOT_CONVERGED (62 findings: HIGH 11 / MEDIUM 21 / LOW 27 / COSMETIC 3; pass 10 had 69 with 8 HIGH). The orchestrator spot-verified A01 (stdin fields absent from legacy), A2-01 (VP-018 overlay wording), C01 (lu assigned only at SL:1085, the user branch), C2-01 (legacy SL:338-347 fallback order) on disk, and measured B08 on CPython 3.11.7 (posixpath and ntpath normpath keep NUL); all held.

## Perimeter A (PRD, supplements, architecture, CI)

Findings: 12 (high 2, medium 7, low 3, cosmetic 0).

## Pass 11, Perimeter A: adversarial review

### 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P11-A01 | HIGH | Mis-anchoring / spec drift (P4, P13 risk) | prd-supplements/interface-definitions.md:86-92; prd.md:461-467 | The "Objects read" list does not match what legacy reads. **Listed but never read:** `rate_limits.windows`, `workspace.repo.*`, `version`, `output_style.name`, `pr.kind`, `prompt_cache.last_miss_cause`/`miss_causes` and `spend_limit`. Grepping every `d.get(`, `cost.get(` and `ws.get(` in legacy/dgx_statusline.py finds none of them. **Read but missing:** `workspace.project_dir` (SL:452), `prompt_cache.hit_ratio` (SL:477), `rate_limits.five_hour`/`seven_day` (SL:501), `cost.total_lines_added`/`removed` (SL:535), `total_api_duration_ms` (SL:550/603) and `total_cost_usd` (SL:601). A story writer working from this list would build reads legacy never makes, which is a P13 behavior change, and would miss real inputs. | product-owner |
| ADV-P11-A02 | HIGH | CI false-fail versus build order (P11) | architecture/ARCH-08-build-ci-release.md:105-108, 191-192; cicd-setup.md:58, 88; prd-supplements/module-criticality.md:136-149 | The required `coverage` check allows `G == 0` only "while no `internal/` Go package exists". The approved build order puts `internal/platform` first and `internal/config` third, before any gated package (`pyfmt` is step 2, `cost`/`statusline` are steps 4-5). The first platform PR leaves G = 0 with an `internal/` package present, so the required check fails. It is also undefined whether the committed manifest lists all three gated packages from day one (red until step 5) or grows as they land. | architect |
| ADV-P11-A03 | MEDIUM | CI semantics / ambiguity (P11) | ARCH-08:99-104; cicd-setup.md:58; nfr-catalog.md:77-78; module-criticality.md:37-38; ARCH-07:34-36 | Three problems with the coverage claim: (1) "parity runs do NOT count toward statusline coverage" is false. Only Tier A is excluded; Tier B (in-process Go output against committed goldens) and the machinery tests run under `./internal/...` with `-coverpkg=./internal/...`, so they credit `internal/statusline`. (2) Go measures statement coverage, not the "line coverage" the gate names. (3) nfr-catalog and module-criticality say the figure comes "from the coverage report of the package `go test` runs", while ARCH-08 merges a cross-package `-coverpkg` profile. How the per-package percentage is derived from that merged profile is never stated. | architect |
| ADV-P11-A04 | MEDIUM | CI positive-coverage false-fail (P11) | ARCH-08:133, 178-183; cicd-setup.md:53, 85, 284 | Gitleaks scans `--log-opts="--all"`, but its count N is compared with `git rev-list --count` over only main + factory-artifacts. With `fetch-depth: 0` on a pull_request run, `--all` also covers the PR merge ref, other remote branches and tags. N therefore differs from the comparison count on essentially every PR. cicd-setup.md:284 already records `--all` diverging from the two-ref set (a local-only tag). The compared rev set must equal the scanned rev set. | architect |
| ADV-P11-A05 | MEDIUM | Contradiction / NFR completeness | prd.md:494; nfr-catalog.md:28 vs ARCH-03:269-270, BC-1.04.001:109-111 and :223 | NFR-005 calls its four-cap list "exhaustive" and says "no cap outside this list exists in legacy". The spec itself mandates other legacy caps: `_MAXHEADERS`=100 and `_MAXLINE`=65536, urllib `max_repeats`=4 and `max_redirections`, the per-site JSON depth budgets, the 4,300-digit int limit, and `window_age.max_depth`=6. The NFR's table-test scope and its "none may be invented" rule therefore point at a wrong universe. | product-owner |
| ADV-P11-A06 | MEDIUM | Partial-fix propagation | prd-supplements/test-vectors.md:46 (v1.7, frontmatter :4-15) | The OD-156 overflow-vector row still lists only CP-O01..O05 and CP-O10/O11. Its owner list lacks BC-1.02.029 and BC-1.05.003. CP-O12 was minted in pass 9 and landed in prd.md:491/507, nfr-catalog.md:25 and error-taxonomy.md:177, but never reached the test-vector index that test writers use. | product-owner |
| ADV-P11-A07 | MEDIUM | Ambiguity / CI breakage risk | cicd-setup.md:52, 118, 208; ARCH-08:62-65; ARCH-07:182-187; BC-6.01.001:118-121 | The plain test step, the coverage job and the release job each exclude "the Tier A selector", but its membership is never defined. Two named oracle-dependent tests are separate from `TestParityTierA_Corpus`: `TestParityCanary_ShimLoaded` and `TestParityCacheSwap_FourCaches` (the swap's Python-writes side needs the oracle). On the macOS and Windows legs and the coverage job, no interpreter is installed and `CI=true`, where BC-6.01.001 makes an unset interpreter fail. These tests either go red there or need an unspecified skip rule. | architect |
| ADV-P11-A08 | MEDIUM | Interface cannot express a BC | ARCH-03:48-60, 121-128, 146-150; ARCH-04:23; ARCH-05:27, 35 vs BC-3.01.001 EC-004 (:133), PC-6 (:98-100) | The step-0 wiring in `Main` constructs `CacheStore`, `MetricsClient` and `ProcStarter`, yet: (a) no disposition is given when `CacheDir` errors on the default resolver. BC-3.01.001 EC-004 requires the render to continue with load-empty/save-no-op caches, but `Render` requires `env.Cache != nil`, and ARCH-02 puts the resolver inside `Load`, where an error could be misread as E-CFG-001. (b) `Env.Loc` construction and the `LocalZone` error result (non-nil on the TZ-unset path) have no caller disposition anywhere. | architect |
| ADV-P11-A09 | MEDIUM | Config default spelling inconsistency | interface-definitions.md:203, 247, 270-271, 276 vs :168-169 | Line 168 says each key's declared shape must hold its default (binding, pass-5 call 3). Yet `cost.rate_min_api_ms` defaults to `{cc: 300000, other: 1800000}`, which is not valid JSON (unquoted keys). Other defaults are also not env spellings: `cost.percentiles` `(0.75, 0.95)` (a Python tuple), `reroute_all_prefixes` `["claude", "claude-"]` for a comma-List key, and the bands written as `[80, 100] = [yellow, red]`. The pass-8 D06 respelling covered only `theme.heat` and `limits.windows`. | product-owner |
| ADV-P11-A10 | LOW | Missing named constant (P20) | ARCH-06:66-75; prd.md:616-622 vs BC-6.01.001:95-97 | ARCH-06's per-site encoder table omits the subagent wire `json.dumps` site (SL:924, s=3, budget 991). BC-6.01.001 and VP-006 pin it, but `Dumps(v, depthBudget)` in `sl/subagent.go` has no named ARCH constant, while ARCH-06 says "do not invent a value". PRD §8 also omits the subagent stdin and wire sites. | architect |
| ADV-P11-A11 | LOW | NFR ambiguity | nfr-catalog.md:24, 69-73; ARCH-08:119-123 | The timing sampling unit is "per corpus case", but cases can be multi-step (with transcript appends), seeded, or `--subagent`. Nothing says whether a timed run is one refresh or the whole step sequence, or whether caches and seeds are reset between the 21 runs. Warm caches change the measured workload and so the 19th-sample p95. | architect |
| ADV-P11-A12 | LOW | Coverage-note inaccuracy | architecture/BC-COMPONENT-MAP.md:227, 242-249 | The "multi-home rows" list presents itself as complete but omits BC-6.01.003 (`par/shim_canary.go` + `sl/testdata/pyhooks/sitecustomize.py`). It also contradicts "every row names exactly one primary component home". | architect |

### 2. Policy compliance
- **P1 append_only_numbering:** PASS. CP-T08 is retired, CP-C06/C07 are reserved, no ids are reused.
- **P2 lift_invariants_to_bcs:** PASS within the perimeter. DI-007/008/010/012 are cited to BCs.
- **P4 semantic_anchoring_integrity:** FINDING ADV-P11-A01.
- **P5 creators_justify_anchors:** PASS.
- **P6 subsystem names:** PASS. PRD §1.6 matches the ARCH-INDEX registry.
- **P7 BC H1 as title source:** PASS. All ss-02..06 H1s and the ss-01 .04-.07 H1s match the PRD rows verbatim.
- **P9 VP-INDEX source of truth:** PASS. 41 = 33+7+1 = 20+13+3+2+1+1+1; ARCH homes sum to 41; module-criticality counts reconcile.
- **P11 ci_positive_coverage_assertion:** FINDING ADV-P11-A02, A03, A04, A07.
- **P12 settled_decisions_are_constraints:** PASS. Nothing reopened.
- **P13 parity_before_behavior_change:** PASS on the specified deviations; A01 creates a risk of an unexcluded behavior change.
- **P14 public_repo_hygiene:** PASS. Only RFC 5737 addresses and the public module path appear.
- **P16 thresholds_are_explained:** PASS.
- **P17 ledger_format_frozen:** PASS (ARCH-04, ARCH-09).
- **P18 cross_platform:** PASS.
- **P19 go_hardening_toolchain:** PASS. The ordering of the toolchain line before govulncheck becomes required is stated.
- **P20 config_over_code:** FINDING ADV-P11-A10 (LOW); A09 is the related default-spelling issue.
- **P21 public_artifact_hygiene:** PASS. No flagged strings are quoted.
- **P3, P8, P10, P15:** N.A.

### 3. Files not fully read
None in the perimeter; all were read in full. Outside the perimeter I opened only targeted excerpts of legacy/dgx_statusline.py, BC-2.01.001, BC-3.01.001, BC-6.01.001 and BC-1.04.001, the BC H1 lines, and VP-INDEX.

### 4. Novelty
**MEDIUM.** A01, A02, A04, A05 and A08 are substantive and newly found; the rest are refinements or propagation gaps.

NOT_CONVERGED

## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 11 (high 3, medium 4, low 4, cosmetic 0).

## ADV-P11-A2 — Phase 1d adversarial review, pass 11, perimeter A2

### 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P11-A2-01 | HIGH | Contradiction (VP vs BC/ARCH) | VP-018:46-49 | **Defect:** the statement says a slash-sid save "persists nothing while the in-memory overlay still answers the same refresh". **Conflict:** ARCH-03:26-34 (AD-03) rejected the overlay option because it gets failed-replace semantics wrong. BC-1.06.001 Inv 3 says "no in-memory overlay". BC-1.06.002 PC2 says every load of that path returns `{}` within and across refreshes. **Risk:** an implementer who follows the VP builds an overlay, and that breaks parity. | architect |
| ADV-P11-A2-02 | HIGH | Contradiction / referee weakening | VP-011:45-50 (also VP-009:43-47) | **Defect:** VP-011 has the comparator normalize Windows oracle stdout to LF "before stepwise byte comparison … never a hidden shim". **Conflict:** BC-6.03.002 PC1 (:66-67) requires "no CRLF folding". BC-6.03.002 EC-006 (:114) says CRLF from the oracle "Cannot happen with the shim … If it does, FAIL. Never normalized". VP-034:69-72 puts the LF behavior in the shim's `newline="\n"` reconfigure. **Risk:** comparator folding would hide a shim regression. VP-009's "normalization … rather than hidden in the shim" wording is ambiguous in the same direction. | architect |
| ADV-P11-A2-03 | HIGH | False for-all / property clear only from the sketch (OD-182) | VP-021:42-46, :66-67 (sketch :107) | **Finite restriction:** "FINITE only" appears only in a sketch comment. The Method's corollary "p75 ≤ p95 whenever a pair is returned" is false for legal NaN-bearing histories (BC-1.05.005 EC-009). Python `sorted` with a NaN does not produce a monotone list, so `v[6]` can be NaN. **Wrong population:** the quantifier filters "rates of length ≥ COST_MIN_N", but the $ colour comes from the separate usd list. **Missing filters:** the src-dependent `api_ms` gate (BC-1.05.005 PC3, 300000 for cc vs 1800000 for other) is absent, and "a single recorded sid" misstates PC1's self-exclusion (`k == sid` skipped). | architect |
| ADV-P11-A2-04 | MEDIUM | Cross-VP contradiction / vacuous leg | VP-014:44-47 | **Claim:** the macOS/Linux bound "has legs" because native-probe rendering "rides the Tier A corpus parity (VP-009)". **Conflict:** VP-033:58-60 states the probe is "not exercised in parity" (seeded `proc_start`). **Mis-attribution:** macOS/Linux probe differences are the closed-set id OD-76 (OD-110), which VP-014 never mentions. | architect |
| ADV-P11-A2-05 | MEDIUM | Partial-fix propagation; P18 | VP-032:41-45, :59-60 | **Defect:** BC-3.01.001 v1.3.1 (pass 10) added EC-013: a relative `HOME`, `LOCALAPPDATA` or `APPDATA` is treated as unset. EC-004's Unix half adds the "home cannot be determined" error. **Gap:** the VP statement only covers empty `LOCALAPPDATA`/`APPDATA` on Windows, and its env matrix has no relative-base or HOME-unset rows. | architect |
| ADV-P11-A2-06 | MEDIUM | Stale invariant→BC counts (P2) | invariants.md:31, :35, :46 | **Stated:** DI-008 = 85 BCs and DI-012 = 76. **Measured:** the file's own counting method (`grep -l` over `ss-0*/`) gives 88 files for DI-008 and 77 for DI-012. DI-007 = 38 does verify. | business-analyst |
| ADV-P11-A2-07 | MEDIUM | Untested path (DI-008) | VP-003:37-40, :77-78; VP-004:52-53 | **Gap:** VP-003 covers only the case where the degraded-line write fails, and both of its rows use faulting stdin. No VP injects a failing writer under a normal (non-degraded) render. **Risk:** VP-004's "runStatusline cannot propagate a non-zero code" is asserted only with a working stdout. A port that returns exit 1 when the normal-row write fails passes every VP. | architect |
| ADV-P11-A2-08 | LOW | Weak for-all assertion | VP-029:54-57 | **Defect:** leg (a) lists the fields that must stay bit-identical after a W-line, and that list omits `cur`. **Risk:** a `cur` mutation on an ordinary (non-overflow) W-line cannot fail the leg as written. VP-013:54 says "every other tracked variable", which is the correct form. | architect |
| ADV-P11-A2-09 | LOW | Frontmatter–body coherence (P5) | VP-009:13 | `bcs:` carries BC-1.01.009. The body (statement and Source Contract :55-62) never names or justifies it. | architect |
| ADV-P11-A2-10 | LOW | Frontmatter–body coherence | VP-010:56-59 | The Source Contract partial-coverage list omits BC-1.07.004/005/006, which are in `bcs:` (:13) and in the statement (:44-45). | architect |
| ADV-P11-A2-11 | LOW | Ambiguity | VP-040:50-52 | **Defect:** P5's "max-prefix of segments" states no fit criterion. **Legacy behavior** (SL:1195-1196): keep the longest prefix with visible width ≤ cols, or the first segment alone once no SEP remains. **Status:** P5 is only derivable when read together with P6. | architect |

### 2. Policy compliance

- **P1** append_only_numbering: PASS. VP-001..041 are contiguous with no reuse.
- **P2** lift_invariants_to_bcs: FINDING A2-06.
- **P4** semantic_anchoring_integrity: FINDING A2-04 (OD-76 omitted from VP-014's scope legs).
- **P5** creators_justify_anchors: FINDING A2-09, A2-10.
- **P6** subsystem names: PASS. No drift in perimeter.
- **P9** vp_index_is_vp_catalog_source_of_truth: PASS.
  - Recount gives 283 `bcs:` edges with every map row matching.
  - Class buckets 33/7/1 and method buckets 20/13/3/2/1/1/1 match.
- **P11** ci_positive_coverage_assertion: PASS. Every harness sketch guards zero counts.
- **P12** settled_decisions_are_constraints: PASS. No OD challenged.
- **P13** parity_before_behavior_change: FINDING A2-01, A2-02.
- **P14** public_repo_hygiene: PASS.
- **P16** thresholds_are_explained: PASS.
- **P17** ledger_format_frozen: PASS.
- **P18** cross_platform_from_day_one: FINDING A2-05.
- **P19** go_hardening_toolchain: N.A. in perimeter.
- **P20** config_over_code: PASS.
- **P21** public_artifact_hygiene: PASS.

### 3. Files not fully read

- **Frontmatter `modified:` histories skipped:** VP-002..VP-041.
- **Proof Harness/Lifecycle tails skipped** (bodies read):
  - VP-017 from :79
  - VP-024 from :100
  - VP-025 from :90
  - VP-028 from :110
  - VP-029 from :90
  - VP-030 from :90
  - VP-034 from :80
  - VP-035 from :74
  - VP-036 from :105
  - VP-037 from :99
  - VP-038 from :80
  - VP-039 from :110
  - VP-041 from :110
- Everything else in the perimeter was read in full.

### 4. Novelty and convergence

Novelty: MEDIUM. Three new HIGH contradictions: VP-018 against AD-03, VP-011 against BC-6.03.002, and VP-021's false for-all.

**NOT_CONVERGED**

## Perimeter B (BC-1.01, BC-1.02)

Findings: 9 (high 0, medium 3, low 5, cosmetic 1).

1. **Findings**

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P11-B01 | MEDIUM | Semantic anchoring / traceability (pattern) | BC-1.02.001:95 (EC-007), BC-1.02.003:79 (EC-006), BC-1.02.006:121 (EC-008), BC-1.02.008:70 (EC-006), BC-1.02.014:102 (EC-010); ARCH-03:83-85; error-taxonomy.md:299 | Six crash-path IDs, CP-S02, S03, S04, S05, S08 and S10, are defined nowhere under specs/. Grep finds them only as ranges in BC-1.01.009:72 and ARCH-03:72. The behaviour is in the listed ECs, but those ECs never name the IDs. ARCH-03 says the trigger tables live in error-taxonomy; error-taxonomy says each trigger's disposition lives in the owning BC. The only definitions are in a semport input file (pass-3-deep:230-238). VP-001 needs one FaultInjectionTable row per CP-S01..S17, so a test author cannot map those six IDs from the specs alone. [process-gap] | product-owner (EC IDs); architect (taxonomy/ARCH-03 circular reference) |
| ADV-P11-B02 | MEDIUM | Missing edge case (parity-visible) | BC-1.02.004:109-112 (PC2.4) vs legacy SL:385-386; BC-1.01.003:63-64 | PC2.3 states universal-newline handling for the pointer-file read. PC2.4 only says the HEAD file is read "whole in text mode". Legacy `open(...).read()` also turns any CR or CRLF inside the file into LF. Example: HEAD `ref: refs/heads/a\rb\n` gives branch `a\nb` in legacy (also written to the git cache), while a raw-bytes port gives `a\rb`. EC-007 only covers a trailing CRLF, which strip removes either way. The rule appears only in the sibling BC-1.01.003 PC5. A failing vector can be written today. | product-owner |
| ADV-P11-B03 | MEDIUM | Partial-fix propagation (untested postcondition) | BC-1.01.005:54-63 (PC4); VP-040:54,93 (P7) | The pass-10 rule (compare beyond-int64 negative COLUMNS as an exact big int; the clamp fails when narrow_cols = MinInt64) has no EC and no canonical vector. VP-040 P7 draws cols only from a "negated int64 spread", so the counter-case (COLUMNS = −10^30, narrow_cols = MinInt64, rows 2) is never exercised. | product-owner (EC/vector); architect (VP-040 P7 generator) |
| ADV-P11-B04 | LOW | Mis-anchor (stale label) | BC-1.01.001:60-61 vs :141 | PC3 credits all three of CP-N01/N02/N03 to "BC-1.04.004/.005 per ARCH-03". Only CP-N03 belongs there. CP-N01 is owned by BC-1.04.015 (its H1) and CP-N02 by BC-1.04.014 (its H1), which the same file's Related BCs line says correctly. | product-owner |
| ADV-P11-B05 | LOW | Config-over-code range gap | BC-1.01.006:65-68 (Inv 1); interface-definitions.md:224; legacy SL:537, SL:596 | Inv 1 says the "prefix of segments" reading only breaks when stdin text contains SEP. But `statusline.theme.separator` is "free text, no control bytes". A configured `/` makes SEP equal to the built-in lines-segment bytes `\e[2m/\e[0m` (SL:537); `[` or `]` collides with the token brackets (SL:596). Trim then cuts inside built-in segments, and VP-040 P5's assumption (no SEP inside segment text) fails. Either narrow the range or widen the Inv 1 caveat. | architect (range); product-owner (Inv 1) |
| ADV-P11-B06 | LOW | Thresholds/format constants not declared (pending intent verification) | BC-1.02.014:62-65; BC-1.02.025:54-55; BC-1.02.014:59; BC-1.02.018:61; BC-1.02.004:99-108 | Passes 7-8 marked some literals as named format constants: BC-1.02.002 Inv 3 (`?`), BC-1.02.007 Inv 4, BC-1.02.012 Inv 4, BC-1.02.016 Inv 4. Sibling literals got no such treatment: the `?` fallback in `_fmt_lines`/`_fmt_tok_c`, the dim `/` in the lines segment, the token brackets `[`/`]`, and the 8192-byte decode chunk in BC-1.02.004 PC2.3 (no "named constant, why not config" note, unlike that BC's own Inv 4). | product-owner |
| ADV-P11-B07 | LOW | PRD↔BC traceability | prd.md:507 (E-REN-002 contract column) | Two BCs own typed-degrade ECs on the 29-byte line but are missing from the E-REN-002 contract list: BC-1.02.003 (EC-006; CP-S03/S04) and BC-1.02.008 (EC-006; CP-S08). | product-owner |
| ADV-P11-B08 | LOW | Oracle sensitivity, unverified [owner-question] | BC-1.02.022:58 (PC3 `a\0b`), :76 (EC-006); OD-185 | From memory, not checked here: keeping NUL in normpath depends on the CPython fix for gh-106242 (believed to be in 3.11.5). OD-185's oracle self-check measures only the depth limits and the Unicode table version, so a pre-fix 3.11 oracle would silently produce `a`. Confidence LOW. | architect |
| ADV-P11-B09 | COSMETIC | Edge-case wording | BC-1.02.028:72 (EC-004) vs :89 | The EC says "104 days → `104d04h`". Exactly 104 days renders `104d00h`; the vector actually uses S = 9,000,000 s (104 d 4 h). | product-owner |

What checked out against legacy:
- **Arithmetic:** every reachable postcondition and vector I could compute matches.
  - The heat colours and band, countdown, `_hm`, half-even and clamp vectors.
  - The BC-1.01.010 staircases, re-summed from the segment widths. The byte totals 701, 809 and 642 are consistent with each other.
  - The R1/R2 byte counts of 45 and 64.
  - The CP-O01..O05 and CP-O12 exact-int-versus-float logic.
  - The NaN-preserving argument order of max/min.
- **Titles:** all 40 H1 titles equal BC-INDEX and PRD.

2. **Policy compliance**
- P1 PASS
- P2 PASS
- P4 FINDING (B01, B04)
- P5 PASS
- P6 PASS (`SS-01` matches the ARCH-INDEX registry)
- P7 PASS
- P12 PASS (B08 is an owner-question only)
- P13 PASS
- P14 PASS
- P16 FINDING (B06)
- P17 PASS (no ledger contact in perimeter)
- P18 PASS (minor CR-handling gap B02)
- P19 PASS (no-fuse discipline stated)
- P20 FINDING (B05, B06)
- P21 PASS (no flagged strings found)

3. **Not fully read; claims not verified**
- **Read only in part (grep or excerpts):**
  - interface-definitions.md (key rows only)
  - error-taxonomy.md (CP rows and the deferral paragraph)
  - ARCH-03 (effect script, fragment anchors)
  - VP-INDEX (catalogue and coverage map)
  - VP-040 and VP-041
  - capabilities.md, invariants.md (CAP/DI rows)
- **Not read:** test-vectors supplement; the bodies of VP-001, 003, 005, 006, 008, 012, 019, 022, 027 and 028.
- **Python claims I could not verify:**
  - The SHA-1 cache keys in BC-1.02.005 (`5a3006e9…`, `09d4733e…`, `a77db2f8…`).
  - The OV decimal expansion.
  - The 5e23 and 1e24 `_hm` digits.
  - The 993/994 depth boundary.
  - The 8191/8192 chunk boundary.
  - The golden widths 198/173/174 and the 743-byte row.
  - The ntpath results in BC-1.02.022: they are consistent with the newer pure-Python `splitdrive`, which I recall without certainty.
  - The gh-106242 fix version behind B08.

4. **Novelty:** MEDIUM. B01 and B02 are new substantive gaps; the rest are refinements. NOT_CONVERGED.

## Perimeter C (BC-1.03, BC-1.06, BC-1.07)

Findings: 4 (high 1, medium 0, low 2, cosmetic 1).

## Pass 11, Perimeter C: status line BCs BC-1.03.\*, BC-1.06.\*, BC-1.07.\*

One HIGH defect: a canonical vector in BC-1.03.007 pins an impossible `lu` value, which pass 10 introduced. The other findings are LOW or COSMETIC. Result: **NOT_CONVERGED**.

### 1. Findings

| ID | Severity | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P11-C01 | HIGH | Wrong expected output; partial-fix regression of ADV-P10-C01 | BC-1.03.007:98 and :107; legacy SL:1069-1087 (`lu` is assigned only at SL:1085, on `typ == "user"`) | **What's wrong:** the CP-O07 canonical mirror vector has three timed **assistant** lines and no user line, yet the hylo expected cache pins `"lu": 1794650402.0`. **Why it can't be right:** no line in that window can set `lu`, so it stays null. The BC agrees elsewhere: its own oracle note at :98 says `cur` for "b" has `t0 null`, which is impossible unless `lu` is null. The OD-167 drop leaves `lu` unchanged (BC-1.03.018 PC2; VP-013:53 "`lr`/`lu` unchanged"). **Effect:** a test written from this row fails a correct implementation or forces a wrong one. The correct expectation is `"lu": null`; every other field and the 972-byte size check out under compact separators. **Secondary:** the vector never states the three timestamps (the size only implies 22-character `Z` stamps), and the `{"size": 972 …` code span at :107 is never closed. | product-owner |
| ADV-P11-C02 | LOW | Traceability mislabel | BC-1.03.006:135, against BC-1.03.006 PC5 (:69-76) and error-taxonomy.md:223 | The DI-012 row calls "the CP-O09 no-write" a named, tested deviation. PC5 and the taxonomy say the no-write is **reproduced** legacy behavior; the only CP-O09 divergence is the leaked partial temp, which rides `temp-file`/OD-163, not D4-EX-2. The row should name the temp-leak divergence. | product-owner |
| ADV-P11-C03 | LOW | Ambiguity / sibling inconsistency (pending intent verification) | BC-1.03.020:39, :45-46 (PC1/Pre-1) and :78 (EC-005) | PC1 fires the rule when `cur.out` "is not int/float/bool", but never says whether a `cur` with the `out` key **absent** fires it. Legacy (SL:993 `cur.get("out") or 0`) does not crash on it and keeps the turn open. EC-005 also files falsy or absent foreign shapes under "CP-C class … ruling b", while siblings BC-1.03.002 EC-007..009 and BC-1.03.005 PC5 name exclusion id `OD-160` for foreign-cache legs. | product-owner |
| ADV-P11-C04 | COSMETIC | Bound wording drift | BC-1.07.001:111 (VP-004 row) | The example says an int `tokenCount` "≥ 2\*\*1024 overflows"; the canonical bound everywhere else is ≥ 2\*\*1024 − 2\*\*970 (BC-1.07.007 PC6/EC-008, BC-1.07.008 PC4). The statement is true as written but understates the trigger set. | product-owner |

**Verified without finding** (exact sizes and caches re-derived by hand against the legacy lines):

- BC-1.03.002, .003, .004: every vector, including the `\r`, VT, NEL, LS, BOM, 0xFF and NaN rows.
- BC-1.03.005: the 430/615 sizes and the 256-window rows.
- BC-1.03.006: every row, including the 527/852/833 overflow legs.
- BC-1.03.007: the 678/839 rows and the 415/814 seed legs.
- BC-1.03.008: 413.
- BC-1.03.009: all `json.dumps` lengths, with `ensure_ascii` for é.
- BC-1.03.010: CP-O08 727, the 599/692/691 shortcut rows, NaN-id 420.
- BC-1.03.011: 532/534.
- BC-1.03.014: 70/81 compact against 77 default.
- BC-1.03.016: T1, T13, T15, T16 and the rate arithmetic of all 20 rows.
- BC-1.03.017: 618.
- BC-1.03.019: all 21 rows.
- BC-1.03.020: C1/C2/C3.
- BC-1.03.021: 669/921/1005.
- BC-1.07.004..008: the wire goldens against SL:845-936.
- Config ranges: all eight transcript/turn keys and the subagent keys match the interface-definitions registry, rationale classes included.
- Crash paths: the CP-A01..A05 subagent set is complete for SL:888-925.

### 2. Policy compliance

- P1 append_only_numbering: PASS (CP-T08 stays retired, CP-T09 is used).
- P2 lift_invariants_to_bcs: PASS.
- P4 semantic_anchoring_integrity: PASS (the ARCH-03 `#transcript`/`#subagent`/`#statusline-guard` anchors resolve; VP-INDEX and per-VP `bcs:` lists are reciprocal for every cited VP).
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS (SS-01 matches the ARCH-INDEX:55 registry).
- P7 BC title sync: PASS (H1 = BC-INDEX = PRD for all 31 BCs).
- P12 settled_decisions_are_constraints: PASS.
- P13 parity_before_behavior_change: PASS. C01 is a wrong expected value, not a deviation.
- P14 public_repo_hygiene: PASS. Observation: BC-1.03.010:132 and BC-1.07.004:78 name a machine-specific interpreter install path (not a home path, no username).
- P16 thresholds_are_explained: PASS.
- P17 ledger_format_frozen: PASS / N.A.
- P18 cross_platform_from_day_one: PASS.
- P19 go_hardening_toolchain: N.A.
- P20 config_over_code: PASS.
- P21 public_artifact_hygiene: PASS.

### 3. Files not fully read; Python claims not verified

**Read only partly:**
- BC-1.03.001/.008/.009/.011/.012/.013/.014/.015/.017: frontmatter and trailing anchor sections.
- BC-1.07.002/.003/.004/.005/.006/.007/.008: frontmatter history.
- ARCH-04: headings only.
- error-taxonomy.md and interface-definitions.md: grep hits only.

**Not opened:** capabilities.md, invariants.md, test-vectors supplement, and the VP bodies beyond their `bcs:` lines.

**Python claims I could not re-execute** (no Bash), accepted from the BCs:
- `seek(negative)` raising OSError rather than ValueError (BC-1.03.002 EC-009).
- The OverflowError message for out-of-range descriptors (BC-1.03.015 EC-004).
- The measured depth budgets (991/993/994) and the period-2 reload cycle (BC-1.03.021 PC5).
- The "19 bytes already streamed" in BC-1.03.006 EC-009. This one is plausible: `json.dump` uses the pure-Python iterencoder.

### 4. Novelty

Novelty: MEDIUM. C01 is a new, concrete error in an expected output, introduced by the pass-10 remediation; the rest are refinements. **NOT_CONVERGED.**

Relevant files:
- specs/behavioral-contracts/ss-01/BC-1.03.007.md
- specs/behavioral-contracts/ss-01/BC-1.03.006.md
- specs/behavioral-contracts/ss-01/BC-1.03.020.md
- specs/behavioral-contracts/ss-01/BC-1.07.001.md
- legacy/dgx_statusline.py

## Perimeter C2 (BC-1.04, BC-1.05)

Findings: 9 (high 1, medium 2, low 5, cosmetic 1).

**Adversarial review: Phase 1d, pass 11, perimeter C2 (BC-1.04.001..021, BC-1.05.001..009)**

I checked every postcondition, edge case and canonical vector against the legacy lines it cites, with the Python results worked out by hand. Every vector matched: BC-1.04.020's 11-step sequence and step-0/step-2 bytes, BC-1.05.008's 21-key goldens, the BC-1.05.005 index and NaN-sort pins, and the BC-1.04.009/.011/.015/.019 numbers. H1 titles match BC-INDEX and the PRD. The two ARCH-03 section anchors resolve.

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P11-C2-01 | HIGH | contradiction / semantic anchoring | VP-031 L61-67 and key-order table L71-88; BC-1.04.003 L130; legacy SL:338-347 | VP-031 says the gen_rate5m fallback fills `v` before `k`/`f`, and its 16 subsets vary v/k/f/p. Legacy inserts the fallback `v` after k and f (SL:344-345), as BC-1.04.003 PC4 L74-77, EC-005 L109 and BC-1.04.020 step 8 L64 (`"f"` before `"v"`) pin. So the fallback order is never tested, and a test built from VP-031's wording would fail a correct implementation. BC-1.04.003 L130 ("every subset of the four series") never names the four series, which allowed the misreading. VP-031 also cites SL:333-343 for the builder. | architect (VP-031), product-owner (BC-1.04.003 L130) |
| ADV-P11-C2-02 | MEDIUM | sibling not updated after a fix (P2) | BC-1.04.018 L51-57, L101, L110 | Pass 10 added a degrade case to PC1: a foreign mix-cache shape (exclusion OD-160) whose giant exact-int `lr[0]` raises OverflowError, giving the degraded line. But the L2 row still lists only DI-007 (no DI-008, no DI-012), and there is no VP-012 closure row and no VP-001 row. Siblings BC-1.04.002/.003 carry both, and pass-10 ADV-P10-C2-11 added VP-001 rows for this degrade class elsewhere. | product-owner |
| ADV-P11-C2-03 | MEDIUM | P20 config-over-code [owner-question] | BC-1.04.004 PC2 L60 and Pre 3 L52; BC-1.04.006 PC3 L50; BC-1.04.007 PC5 L65/72; BC-1.04.008 PC2 L55; BC-1.04.010 PC3 L55; BC-1.04.012 PC4 L62; BC-1.04.017 PC4 L54; BC-1.04.018 PC4 L62; BC-1.05.003 PC2 L73 | Displayed words are inline literals: `s old`, the dead-rung ` ?`, `r`/`·q`, `KV`, `host`, `t/s`, `max`, `idle`, `n/a`. Their siblings are config keys: `statusline.labels.input`, `labels.vllm_down` and `labels.lmcache_down` (interface-definitions L299-301; OD-189). The labels policy is inconsistent. | product-owner |
| ADV-P11-C2-04 | LOW | missing edge cases (OD-160 crash sites) | BC-1.04.009 Pre 1 L47; BC-1.04.014; reached via BC-1.04.002 PC1 L63-65 | On the cached path, `hist` is returned raw, and the sparkline has crash sites no BC lists: a dict/number/null `hist` fails at `hist[-12:]` (SL:664, TypeError; a dict slice is unhashable in 3.11); a short list point raises IndexError (SL:655 via 664); a plotted giant int raises OverflowError (SL:674); a non-numeric plotted value raises TypeError (SL:671/674). BC-1.04.002 Inv 1 lists its own sites in full. | product-owner |
| ADV-P11-C2-05 | LOW | rationale contradicts itself | BC-1.04.001 PC1 L82-86 vs L88-91 | The portless `Host` result is credited to `putrequest`'s urlsplit-netloc branch. But L88-91 say Host is already in the headers, so `_send_request` sets skip_host and that branch never runs. The real source is `Request.host` (`_parse`: `_splithost` plus `unquote`), added by `do_request_`. The wire output is the same; only the explanation is wrong. | product-owner |
| ADV-P11-C2-06 | LOW | hard-coded literal in prose (partial P20 sweep) | BC-1.04.021 L38-41, L46-47, L55 | The reachability claims are stated against a literal 2 s ("TTL ≥ 2", "only when TTL < 2 s"). `statusline.sparkline.min_gap_s` is a key with range finite > 0 (interface-definitions L296), so the gap does decide appends in steady state whenever TTL < min_gap_s (for example min_gap 5 with TTL 4). Pass 9 renamed the key in PC1/PC2 but not in this prose. | product-owner |
| ADV-P11-C2-07 | LOW | stale cross-reference after a pass-9 move | VP-020 L56 | VP-020 attributes the field- and sign-specific refresh outcome to "BC-1.05.004 PC1". Pass 9 (ADV-P9-C2-03) moved the OD-166 skip to PC4, and PC1 now says the skip is not part of the guard. | architect |
| ADV-P11-C2-08 | LOW | legacy line citations drifted | BC-1.04.001 L126; BC-1.04.018 L54; BC-1.04.007 L53 | `resp.read()` is at SL:171, not SL:172 (ARCH-03 already says 171). The BC-1.04.018 format crash site is at SL:778-779, not 776-777 (776 is the isinstance guard, 777 sets `dim`). The THRESHOLDS §8b comment is at SL:789, not 790. | product-owner |
| ADV-P11-C2-09 | COSMETIC | metadata | BC-1.04.012 L4 vs L24; BC-1.04.017 L4 vs L23 | The `version` field (1.3.1 and 1.2.1) is behind the last `modified` entry (1.3.2 and 1.2.2) added by the pass-9 sweep. Same pattern as the earlier SC-19 fix. | product-owner |

## 2. Policy compliance

- P1 append_only_numbering: PASS (EC ids are contiguous; BC-1.04.013 EC-010 renumbering was append-only).
- P2 lift_invariants_to_bcs: FINDING ADV-P11-C2-02.
- P4 semantic_anchoring_integrity: FINDING ADV-P11-C2-01 (the VP-031 key-order leg contradicts BC-1.04.003 and legacy).
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS (all 30 BCs say SS-01, matching the ARCH-INDEX registry).
- P7 H1 = BC-INDEX = PRD: PASS (all 30 match and describe their postconditions).
- P12 settled_decisions_are_constraints: PASS (OD-30/56/157/160/166/175/180/181/189 are respected; ADV-P11-C2-03 is raised as an owner question).
- P13 parity_before_behavior_change: PASS (every deviation carries a closed-set exclusion id).
- P14 public_repo_hygiene: PASS (only RFC 5737 and loopback addresses).
- P16 thresholds_are_explained: PASS (T-codes and the stdlib constants have rationale).
- P17 ledger_format_frozen: PASS.
- P18 cross_platform_from_day_one: PASS (TLS trust store and case-insensitive filesystem caveats are stated).
- P19 go_hardening_toolchain: N.A.
- P20 config_over_code: FINDINGS ADV-P11-C2-03 and ADV-P11-C2-06.
- P21 public_artifact_hygiene: PASS.

## 3. Not fully read, and claims I could not verify

**Not fully read:** VP-001, VP-012, VP-019, VP-021, VP-022, VP-024, VP-030 (grepped only); invariants.md DI-007/008/012 rows (the lines were too long to display); ARCH-04 (not opened); prd.md, error-taxonomy.md, test-vectors.md and capabilities.md (grepped only); BC-5.02.003 (grepped only).

**Python claims I could not execute:**
- The oracle measurements: JSON depth 992 accepted / 993 rejected; the 100/101-103 interim-response behaviour; the header limits; the OverflowError boundary 2**1024 - 2**970.
- `round(True, 4)` returning int 1.
- The dict-slice TypeError in 3.11, which I asserted from stdlib knowledge.
- The timsort placement of NaN, and every float product in the vectors, which I derived by hand.

## 4. Novelty and convergence

Novelty: MEDIUM. ADV-P11-C2-01 is a new contradiction between a BC and a cited VP. The rest are refinements and gaps left by earlier sweeps.

NOT_CONVERGED.

## Perimeter D (S2-S6 BCs)

Findings: 17 (high 4, medium 5, low 8, cosmetic 0).

## Adversarial review: Phase 1d, pass 11, perimeter D (SS-02..SS-06)

Seven of the findings below need a fix (3 HIGH, 4 MEDIUM). The other ten are LOW. The four that matter most:

- **ADV-P11-D01:** the one example case for the `temp-file` exclusion cannot exist in the corpus under the current seeding rule.
- **ADV-P11-D02:** when a case sets its own metrics URL, the oracle and Go would query different URLs.
- **ADV-P11-D03:** BC-6.04.001 says "Go 1.26.x" in its title while its body now pins exactly 1.26.0.
- **ADV-P11-D08:** the reroute-all default is written in display form, which the List grammar would parse into the wrong entries.

### 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P11-D01 | HIGH | cross-BC contradiction / harness | BC-6.03.003:77-81, 108, 151; BC-6.02.003:160-171; BC-6.02.002:105-108; legacy SL:201-204, 1215, 1229 | The canonical `temp-file` case `cache-003` (sid `../x`) cannot be built. The hermeticity rule rejects a truthy sid with an unseeded `proc_start` unless the case declares a fake process table, and no P1 case declares one (BC-6.01.002:101-104). The every-sid rule also rejects any sid the harness cannot seed. Seeding `statusline-../x.json` means creating the directory `statusline-..`. That makes legacy's `os.replace` succeed, so no temp file leaks and BC-6.03.003 PC-5 ("≥1 temp file") fails. Leaving it unseeded makes legacy run the real `ps` (SL:1229) and Go probe the real process tree. Either the case or the rule has to give. | product-owner [process-gap] |
| ADV-P11-D02 | HIGH | contradiction / metrics-URL injection | BC-6.01.002:91-95, 112-125, 144-147; BC-6.02.003:149-154 vs ARCH-07:96-103 | Both BCs say "the case value wins **on the Go side**". The oracle's `DGX_SL_VM_URL` stays the injected fake unconditionally (exact key set :112-113), and the settings translation (BC-6.02.003 PC-2) also maps the case value to `DGX_SL_VM_URL`, so that key has two values. ARCH-07 says "the case value wins" with no side named. A case with its own URL (e.g. a `/vm` path suffix) would make the two sides query different servers. A non-fake case URL also brings back the 1.5 s timeout flakiness that BC-6.02.003 Pre-3 bans. | product-owner |
| ADV-P11-D03 | HIGH | P7 title drift / partial-fix regression | BC-6.04.001:41, 46, 120, 128 vs :67-71; BC-INDEX:318; BC-ALLOCATION:354; prd.md:425; also BC-6.04.001:60 vs ARCH-08:24-27 | The ADV-P10-D09 fix pins the floor leg to exactly `1.26.0` ("NOT `1.26.x`"). The H1, Description, CTV row 1 and VP row still say "Go 1.26.x leg", and the three index/PRD titles copy it. Separately, Pre-2 says go.mod has "a `toolchain` line", while ARCH-08 says go.mod has **no toolchain directive** (the line is a pending, owner-gated remedy). | product-owner |
| ADV-P11-D04 | MEDIUM | P19 hardening | BC-6.04.001:72-88 vs ARCH-08:46, 235-239 | PC-3, "Steps per leg, in order", lists gofmt, vet, setup-python and go test only. ARCH-08's lint job also runs a pinned staticcheck and promotes govulncheck to a required check. The BC cannot drive a test of the full check suite. | architect / product-owner |
| ADV-P11-D05 | MEDIUM | legacy mismatch / Windows | BC-5.03.004:52-53 | PC-3 defines nt `Basename` as "text after the last separator (`/`, `\` and the drive colon)". CPython `ntpath.basename` is `split(p)[1]`, and `split` runs `splitdrive` first, so a UNC root `\\server\share` gives `''`. The SL:460 label then falls back to the normpath `\\server\share`. PC-3 as written gives `share`. The UNC-drive rule (and `\\?\` device prefixes) is missing. | product-owner |
| ADV-P11-D06 | MEDIUM | wrong boundary (S5 Windows localtime domain) | BC-5.04.001:54-56; BC-5.04.002:47-55; BC-6.04.003:84 | The working domain is stated as left-open `(1970-01-02T00:00:00 local wall, …)`. Under the parity pin `TZ=UTC`, the wall time 1970-01-02T00:00:00 gives t=86400, a=0, u1=86400 and the probe `u1-86400 = 0`, which is inside MSVC's domain. The interval is therefore left-closed, and a boundary test leg written from the text would expect a degrade where legacy renders. Also, "shifted by the zone offset" contradicts the zone-independent "every naive wall time on or before 1970-01-01 degrades" in BC-5.04.002 and BC-6.04.003. | product-owner |
| ADV-P11-D07 | MEDIUM | mis-anchor (P4) | BC-2.03.002:84 vs :76, BC-2.01.001:156, BC-2.01.004:115 | Names the key `statusline.paths.cache_dir`. The registry key is `paths.cache_dir`; the env name `HYLO_PATHS_CACHE_DIR` cited beside it only fits `paths.cache_dir` (grep: the string appears nowhere else). | product-owner |
| ADV-P11-D08 | HIGH | P20 / partial-fix regression | BC-2.01.004:209; interface-definitions:203 (same class :247, :276) | The default of `statusline.lane.reroute_all_prefixes` is written in display form `["claude", "claude-"]`, not the env spelling `claude,claude-`. Under the List grammar (BC-2.01.005 PC-2) it parses to the entries `["claude"` and `"claude-"]`. Build check (c) still passes, but reroute-all would never match. Pass-8 D06 moved `limits.windows` and `theme.heat` to env spellings, and BC-2.02.001 PC-3 relies on the Default column being the env spelling. The `cost.percentiles` default `(0.75, 0.95)` and `rate_min_api_ms` default `{cc: …}` are not strict JSON either. | product-owner |
| ADV-P11-D09 | MEDIUM | CI positive-coverage | BC-6.02.001:83-97 vs ARCH-08:175-177 | The public-hygiene perimeter test `TestCorpusHygiene` has no positive-coverage clause: nothing requires "K files scanned, K>0". If the scan roots are renamed or empty, the test passes without scanning anything. ARCH-08 requires `K == 0` to fail. | product-owner |
| ADV-P11-D10 | LOW | traceability vs legacy | BC-5.01.003:115; SL:919-920 | Lists SL:919-920 under **int** `//`/`%`. At SL:919, `secs = max(now_ms - start, 0) / 1000` is a float, so these are float_divmod sites (BC-1.07.007:75 agrees). The `int()` list also omits SL:525, 527, 529, 560 and 826. | product-owner |
| ADV-P11-D11 | LOW | contradiction | BC-5.01.005:74-75 vs BC-5.02.006:63-64 | Inv 1 calls Repr "the only float→string conversion used by the cache writers". Repr spells `nan`/`inf`, but the cache writers must emit `NaN`/`Infinity`. Read literally, Inv 1 would write `nan` into caches. | product-owner |
| ADV-P11-D12 | LOW | untestable grammar (S2 Text) | BC-2.01.005:149-180; BC-2.01.001:68-72 | BC-2.01.001 defines an "any text" class (`statusline.telemetry.query`) that accepts the empty string. BC-2.01.005 PC-6 gives no verdict for a control byte in an any-text key: its control-byte rule covers "free-text" keys only. | product-owner |
| ADV-P11-D13 | LOW | ambiguity | BC-4.01.002:63-70 vs BC-2.01.001:87-96 | It is unstated whether `config.Load` runs at all on an unknown-flag run. That decides whether stderr also carries unknown-setting warnings, so the stderr table test cannot be written. | product-owner |
| ADV-P11-D14 | LOW | P16 rationale | BC-5.01.004:50-52 vs :131 | The width envelope rationale cites "legacy's 2 and 3". Legacy has no width-3 spec; the same file's Related BCs say there is no `:3d`. | product-owner |
| ADV-P11-D15 | LOW | signature drift | BC-5.02.002:49 vs ARCH-06:196 | `DumpsLen(OrEmpty(Decode(...)))` omits the required `depthBudget` argument. | product-owner |
| ADV-P11-D16 | LOW | replay hermeticity / Windows | BC-6.02.002:82-97; legacy SL:452 | The capture path rewrite covers `transcript_path`, `project_dir` and `cwd` but not `workspace.current_dir`, which is in legacy's fallback chain, so a replay can read the developer's real `.git`. Windows paths in captured JSON are always backslash-escaped, so the "split by JSON escapes → build error" rule makes every Windows capture a build error. | product-owner |
| ADV-P11-D17 | LOW | cross-check (outside perimeter) | interface-definitions:271 | `absolute_bands` cites SL:520 (`else:`). The comparison is at SL:521, which BC-2.01.005 PC-5 cites correctly. | product-owner |

### 2. Policy compliance

- **P1** append_only_numbering: PASS (CP-T09 appended, CP-T08 retired).
- **P2** lift_invariants_to_bcs: PASS (DI-008, DI-010, DI-012 cited throughout).
- **P4** semantic_anchoring_integrity: FINDING D07, D10.
- **P5** creators_justify_anchors: PASS.
- **P6** subsystem name: PASS.
- **P7** H1 = BC-INDEX = PRD and describes postconditions: FINDING D03.
- **P12** settled_decisions_are_constraints: PASS (no settled decision challenged).
- **P13** parity_before_behavior_change: FINDING D01, D02.
- **P14** public_repo_hygiene: PASS.
- **P16** thresholds_are_explained: FINDING D14.
- **P18** cross_platform_from_day_one: FINDING D05, D16; per-OS routing through `internal/platform` otherwise PASS.
- **P19** go_hardening_toolchain: FINDING D04 (and the toolchain half of D03).
- **P20** config_over_code: FINDING D08.
- **P21** public_artifact_hygiene: PASS. BC-6.02.001:93 carries a hostname-shaped example that ADV-P3-D40 already ruled synthetic; not quoted here.
- **P3, P8–P11, P15, P17**: N.A.

### 3. Not fully read / not verified

- **Partly read:** for most BCs I skipped frontmatter lines 1–20/40 (the changelog was read, not the input-hash fields). Of `prd-supplements/` I read only interface-definitions:196-315.
- **Not read:** error-taxonomy, the other prd-supplements, ARCH-01..05, the cited VP files, capabilities.md.
- **Python/runtime claims I could not verify (no interpreter available):**
  - whether MSVC `localtime_s` rejects instants whose local date falls before 1970 west of UTC (bears on the zone part of D06);
  - CPython 3.11.7 Windows C `_path_normpath("//")`;
  - BC-5.01.001 EC-006 (`round(1.00005, 4)`);
  - the measured mix-save 994 exception;
  - whether Go `net/url.Parse` accepts ports above 65535 (BC-2.02.005 EC-007).

### 4. Novelty and convergence

Novelty: MEDIUM. D01 and D02 are new cross-BC harness contradictions; D03 and D08 are sibling-propagation gaps left by the pass-10 and pass-8 fixes.

NOT_CONVERGED
