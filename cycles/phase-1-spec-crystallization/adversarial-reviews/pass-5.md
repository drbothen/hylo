---
document_type: adversarial-review
phase: 1d
pass: 5
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 148
---

# Adversarial Spec Review — Phase 1d, Pass 5

Pass 5 ran as six fresh-context perimeters, the same split as passes 1-4. Each section is the verbatim final report of one perimeter, unedited except for this framing. Per-perimeter novelty: A MEDIUM-HIGH, A2 MEDIUM, B MEDIUM, C MEDIUM, C2 MEDIUM, D HIGH. NOT_CONVERGED (148 findings: HIGH 24 / MEDIUM 75 / LOW 43 / COSMETIC 6; pass 4 had 133 with 39 HIGH). The orchestrator spot-verified a sample of claims (A01, A03, A2-02, A2-18, B05, B06, D02, D04, C2-02) on disk and against CPython 3.11.7; all held. B14 (future-dated timestamps) is a false positive: agent timestamps are UTC, which was already 2026-11-18.


## Perimeter A (PRD, supplements, architecture, CI)

Findings: 25 (high 5, medium 13, low 7, cosmetic 0).

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P5-A01 | HIGH | contradiction / closed exit surface | architecture/ARCH-01-binary-cli.md:51, :85-88; prd-supplements/interface-definitions.md:47-52; prd.md:438 | `config path` exits 1 when a directory can't be resolved: BC-2.03.002:85, :91, EC-008/010/011. Every document in the perimeter says otherwise. ARCH-01 has `runConfigPath` return `0 \| 2`. Its "closed" exit decision gives exit 1 only to `config validate`. The supplement's exit table and the PRD's §3.1 row both say exit 0 only. VP-004's "closed, exhaustively table-tested" surface would therefore reject behavior that a BC requires. | architect + product-owner |
| ADV-P5-A02 | HIGH | contradiction (oracle env), P18 | VP-034-oracle-isolation.md:47-48, :106; BC-6.01.002.md:112-113, :146, :159; BC-1.01.008.md:67; ARCH-07-parity-harness.md:61-62 | VP-034 requires `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` in the Windows oracle env. It also adds HOMEDRIVE/HOMEPATH. BC-6.01.002 says every PYTHON* variable except PYTHONPATH is absent (EC-002), and its Windows key set is only TMP/TEMP/SYSTEMROOT. BC-1.01.008 inv 2 says PYTHONUTF8=1 is not the parity mode (surrogateescape). ARCH-07, which hosts VP-034, has no per-OS env table, so nothing settles the conflict. Implementing VP-034 would change oracle output on invalid UTF-8. | architect |
| ADV-P5-A03 | HIGH | interface cannot express BC | interface-definitions.md:116-120, :183, :239; BC-1.04.009.md:49-54, :66 | The composite env grammar fixes the shapes. `Float triple` is "array of 3 numbers", and `RGB triples + Float` allows "one finite number". The defaults don't fit. `statusline.sparkline.scale` has four values (k top, v floor, f floor, other). The `colors` fade is a span: 0.55 base + 0.45 range, two numbers. The declared default can't be written in the declared shape, and the shape-check error would fire on the default itself. | product-owner |
| ADV-P5-A04 | HIGH | CI design / ordering, P11 | ARCH-08-build-ci-release.md:42-43, :60-62; ARCH-06-pyfmt.md:34, :44-45, :140; cicd-setup.md:153-157 | The `go generate` staleness step regenerates the pyfmt oracle tables and Unicode tables. Their generators are `testdata/gen/*.py` and run "under the pinned 3.11 oracle". The CI diagram runs that step before setup-python (GEN before PY), so it either fails or falls back to PATH Python, which OD-104 forbids. CI also installs 3.11.x, not 3.11.7 (ASM-001 dual pin), so regenerated depth/oracle tables can drift and the check can flap. It also makes Python a dependency of the Windows leg, which Tier B says needs no Python. | architect |
| ADV-P5-A05 | HIGH | P9 VP arithmetic | prd-supplements/module-criticality.md:55, :69-79 | The S1 row says 20 VPs and omits VP-041. The footnote says "Union ... = 40/40". VP-INDEX.md:34 and :96 show 41 VPs, and VP-041's module is `internal/statusline`. ARCH-INDEX:122 already says 41. Stale since the pass-4 VP-041 addition. | product-owner |
| ADV-P5-A06 | MEDIUM | closed vocabulary incomplete | error-taxonomy.md:70-93 | The "Reason Vocabulary (exact strings)" is presented as complete with a reconciliation. It omits two reasons BC-2.01.005 raises on the same E-CFG-001 surface: `expected JSON <shape>` (BC-2.01.005:82) and the pill-label reason (BC-2.01.005:96). Runtime values that break the glyph rule (not exactly 1 code point / 1 column) have no reason string or class at all. BC-2.01.004:130-131 only covers build-time defaults. | product-owner |
| ADV-P5-A07 | MEDIUM | contradiction | ARCH-07-parity-harness.md:107 vs error-taxonomy.md:86-87 (and BC-2.02.001:117-118) | ARCH-07 defines four D4-EX-3 test names (Number merges range and grammar; no Theme). The taxonomy says all six classes have "dedicated class contracts and D4-EX-3 table tests". A Phase 2 story can't satisfy both. | architect |
| ADV-P5-A08 | MEDIUM | ambiguity (OD-168 routing) | ARCH-01-binary-cli.md:46, :67; interface-definitions.md:39-40 vs :319; error-taxonomy.md:58 | On a subagent-mode config error, ARCH-01 and interface-definitions :39-40 put "the error line" (singular) on stderr. The same supplement at :319, and the taxonomy, say all reason lines, i.e. the full list. | architect |
| ADV-P5-A09 | MEDIUM | partial-fix propagation | ARCH-03-statusline.md:69-70, :89-91 | ARCH-03 still says the history-borne CP-O10/O11 raise happens at the render sites SL:616/623 (step 7d), with owners BC-1.05.007/.002. The pass-4 B14 correction (error-taxonomy.md:126-130) puts that raise in `cost_thresholds` at SL:255, which is step 7c, owner BC-1.05.005 EC-011. The effect-step script, the normative order stories follow, carries the stale site. | architect |
| ADV-P5-A10 | MEDIUM | interface cannot express BC | ARCH-03-statusline.md:143-145; ARCH-06-pyfmt.md:34, :112 | `Decode` takes a depth budget per call site: session/mix 991, git/cost-history 990. `CacheStore.Load(name)` has no budget parameter, and no name-to-budget mapping is stated in ARCH-03 or ARCH-04. A single-budget Load would fail VP-006 at the git and cost sites. | architect |
| ADV-P5-A11 | MEDIUM | unstated wiring | ARCH-03-statusline.md:103-108, :132-133, :155-157; ARCH-05-platform.md:27 | Main builds only `Cache` after step 0. `Metrics` needs `backends[0].metrics_url` and `telemetry.timeout_s`. `Proc` needs `window_age.process_name` and `max_depth`. Neither `Query` nor `WindowStart()` takes config, so both must also be built after step 0. That is unstated, and the Env doc implies they arrive pre-built. | architect |
| ADV-P5-A12 | MEDIUM | mis-anchor (P4) | BC-COMPONENT-MAP.md:185 | BC-3.02.001 (whose title says "proc_start key first", a session-cache read) is homed only in `plat/proc.go`. `internal/platform` is a sink with no CacheStore (ARCH-00:71-72). The cache-first logic belongs in step 6 of `internal/statusline` (ARCH-03:66). This homing invites an AD-02 violation. | architect |
| ADV-P5-A13 | MEDIUM | NFR vs config ranges | prd.md:483; nfr-catalog.md:28; interface-definitions.md:172-173, :182 | NFR-005 says "bounded state, legacy caps only". The cap keys `read_cap_bytes`, `dedup_memory` and `history_cap` are ranged `>= 1` with no upper bound. Meanwhile `cells`/`points` are capped at 100 to protect the 25 ms p95 budget, so the same rationale is applied inconsistently. [owner-question] on bounds. | product-owner |
| ADV-P5-A14 | MEDIUM | ranges vs BC | interface-definitions.md:140, :206, :214-215, :222-228, :236-237 | BC-2.02.002:68 and :80 apply the Duration ceiling (`<= 9223372036.854775`) to every Seconds key. The supplement shows it only on `telemetry.ttl_s` (:141). The `git.ttl_s` exception doesn't say whether the ceiling, or any negative floor, applies. | product-owner |
| ADV-P5-A15 | MEDIUM | ambiguity | interface-definitions.md:118, :210-211 | For the Float pairs `limits.projected_bands` and `absolute_bands`, the spec never says which array element is red and which is yellow. No ordering constraint applies ("comparison-total"), so `[80,100]` and `[100,80]` both pass validation and silently produce different coloring. | product-owner |
| ADV-P5-A16 | MEDIUM | P11 [process-gap] | ARCH-08-build-ci-release.md:60-71, :81-110; cicd-setup.md:77-85 | The coverage gate and the OD-170 staleness check are both regression detectors, but neither has a positive-coverage line. A package with `[no statements]` or absent from the profile, or a tree with zero `go:generate` directives, passes trivially. | architect |
| ADV-P5-A17 | MEDIUM | sibling not updated | cicd-setup.md:162 vs :109-116 | `release.yml` runs `go test ./...` with no setup-python step and no `HYLO_PARITY_PYTHON`. Lag note 1 flags exactly this defect for the test job, because Tier A lives in the plain test step. The release job inherits it unflagged. | architect |
| ADV-P5-A18 | MEDIUM | P20 [owner-question] | BC-2.01.004.md:102-104; interface-definitions.md:241 | The glyph family is declared exhaustive ("exactly these members"). Several behavior-shaping glyphs are missing from it with no "why not config" note: `⛏` (KD-002), the `◨` lane marker, and the sparkline 8-glyph ramp (BC-1.04.009:55 calls it a "glyph key"). Row-2 dot/cell glyphs are also absent. | product-owner |
| ADV-P5-A19 | LOW (pending intent verification) | partial-fix | ARCH-08-build-ci-release.md:88; cicd-setup.md:80 | Tier A fails when its case count differs from the case-directory census (ADV-P2-A15). Tier B fails only when `N == 0`, so a partially lost golden set passes. | architect |
| ADV-P5-A20 | LOW | duplicate registry row | interface-definitions.md:219-220 | The `statusline.cost.basis_min_mtok_month` row appears twice. | product-owner |
| ADV-P5-A21 | LOW | self-contradiction | error-taxonomy.md:168 (and :151-152); risk-register.md:33 | CP-O09 "reproduces the no-write", yet "the cache-byte divergence rides the extended D4-EX-2 entry". If both sides write nothing, there is no divergence; the leaked temp is the `temp-file` id. R-008 lists CP-O06..O09 as skip triggers. | product-owner |
| ADV-P5-A22 | LOW | missing carve-out | prd.md:77-78, :581-582 | §1.2 and §8 (DI-008) state that config errors always render the one-line D4-EX-3 output. Neither gives the OD-168 zero-byte subagent carve-out that §3.1 and NFR-002 do. | product-owner |
| ADV-P5-A23 | LOW | ambiguity | ARCH-06-pyfmt.md:34 | The ModeText/ModeBytes parenthetical lists NaN/Infinity tokens only under ModeBytes. Stdin, which is ModeText, accepts them (interface-definitions.md:57-58). The cache writer emits NaN tokens that are read back via ModeText (ARCH-04:43-45). | architect |
| ADV-P5-A24 | LOW | anchor | ARCH-03-statusline.md:96; prd.md:496 | ARCH-03 names BC-1.04.001 as the CP-N03 owner, but the SL:717 degrade sits in `serving_state` (BC-1.04.005 EC-007 / BC-1.04.004). The PRD E-REN-002 contract column also omits BC-1.04.005 and the CP-O01..O05 owners. | architect |
| ADV-P5-A25 | LOW [owner-question] | P13 wording | interface-definitions.md:297-298 | The supplement says the `backends[0].metrics_url` default (an RFC 5737 address) is "not an exception" to legacy defaults. It is a different value from legacy's, and an out-of-box binary targets a non-routable address. | product-owner |

## 2. Policy compliance
- P1: PASS. CP-C06/C07 are reserved rather than reused, and the key rename is not an ID.
- P2: PASS within the perimeter.
- P4: FINDING A12, A24.
- P5: PASS.
- P6: PASS. PRD §1.6 names match the ARCH-INDEX registry exactly.
- P7: PASS. 45 BC H1s sampled across all six shards match the PRD rows.
- P9: FINDING A05. ARCH-INDEX aggregate checked: 41 VPs, 8 second homes, correct.
- P11: FINDING A04, A16, A19.
- P12: PASS. Settled challenges are tagged [owner-question] (A13, A18, A25).
- P13: PASS with an [owner-question] (A25). Exclusion set is eleven ids everywhere I checked.
- P14: PASS. No private identifiers found.
- P16: PASS. Retry constants, the label width of 16 and the Duration ceiling are explained.
- P17: PASS.
- P18: FINDING A02.
- P19: PASS. staticcheck, govulncheck and -race are specified, with landing lags disclosed.
- P20: FINDING A18.
- P21: PASS. No flagged string quoted.
- P3, P8, P10, P15: N.A.

## 3. Files not fully read
None in the perimeter: all 21 files were read in full. Outside the perimeter I spot-read only for cross-references: VP-INDEX (lines 1-100), VP-034 (38-112), BC-1.04.009, BC-2.01.004 (96-131), BC-2.02.001 (95-124), BC-5.01.004 (36-75), grep hits in BC-2.03.002, BC-2.02.002 and BC-1.07.002, and legacy SL:700-729.

## 4. Novelty
MEDIUM-HIGH. A01-A04 and A10-A12 are new defect classes: the exit surface contradicting a BC, a VP conflicting with a BC on the oracle env, composite shapes that can't hold their own defaults, CI step ordering, and the interface/seam wiring gaps. The others are propagation residue from earlier passes.

NOT_CONVERGED


## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 36 (high 4, medium 22, low 9, cosmetic 1).

## 1. Findings

| ID | Sev | Category | file:line | Defect (evidence) | Owner |
|---|---|---|---|---|---|
| ADV-P5-A2-01 | HIGH | Invalid Go / API drift | VP-015:37-38,97; VP-017:76-77 | `config.Load` returns `(*Config, *ErrorSet)` (ARCH-02-configuration.md:85-88; ARCH-02 says a single `*Error` cannot carry the error list). VP-015 still promises "a single typed `*Error`". Both skeletons read `err.Key`/`err.EnvName`/`err.Reason`/`err.Value` on an `*ErrorSet`, which does not compile; they should go through `err.First()`. | architect |
| ADV-P5-A2-02 | HIGH | Invalid Go / partial-fix regression | VP-024:87,97,100 | ARCH-06-pyfmt.md:113-114 (ADV-P4-D07) made `Dumps` return `([]byte, error)` and `DumpsLen` return `(int, error)`. The skeleton still uses them as single values, so it does not compile. Once corrected, the round-trip also needs a skip arm: the encoder fails at depth 993 (BC-5.02.006), but `Decode` accepts 993 at the 993/994 sites. | architect |
| ADV-P5-A2-03 | HIGH | Mis-anchor / coverage hole | VP-016:37-38,48,88-89; BC-2.01.003:117-118 | VP-016 claims six classes including theme/SGR, keeps BC-2.01.003 in `bcs:`, and says control-character rows of the theme class sit "inside the class tables". Yet it has no Theme table, citing the corpus validator. That validator governs the parity corpus, not in-tree unit tables. BC-2.01.003 routes its default-theme-bytes golden and its ESC-free-SGR property to "VP-015, VP-016 (theme/SGR class)", and neither VP carries them. | architect |
| ADV-P5-A2-04 | HIGH | Mis-anchor (multiple BCs) | VP-041:42-59 vs BC-1.02.019:101, BC-1.02.025:125, BC-1.02.027:96, BC-1.02.028:96 | These four BCs route legs to VP-041: dense-grid triple equality, float64 token-format fuzz, `_hm` fuzz, and `win_ms` fuzz. VP-041's P-a..P-h contain none of them. VP-041 `bcs:` lists 025/027/028 but its body has no corresponding property. | architect |
| ADV-P5-A2-05 | MEDIUM | Missing decode site | VP-006:45-55 | The table claims all loader sites but omits the metrics reply: `fetch_sample` calls `json.loads(resp.read())` at legacy SL:171, a 7-frame chain via get_sample, so 992 accepted / 993 rejected (derived). BC-5.02.004:36 names metrics replies as `pyfmt.Value` decodes, so a Go budget drift here goes undetected. | architect |
| ADV-P5-A2-06 | MEDIUM | Skeleton fails a correct impl / cross-platform | VP-026:95,100 | `t.Setenv("TZ", "")` sets TZ to empty; it cannot unset it. POSIX and Go treat an empty TZ as UTC, so the row "TZ unset → OS zone" mis-encodes the case. On UTC CI runners, "os-zone" and "UTC" cannot be told apart, so the fallback rows are vacuous there. Separately, falling back to the OS zone for an unparseable TZ differs from glibc/Go UTC semantics. [owner-question] on OD-171. | architect |
| ADV-P5-A2-07 | MEDIUM | Weak oracle | VP-034:86-119 vs BC-6.01.002:70,157 | The skeleton checks only the `*_proxy` sweep plus individual pins. It never asserts the exact allowlisted key set (BC-6.01.002:157) or the OD-171 `TZ=UTC` pin. A child env inheriting everything except proxies passes, including `DGX_SL_TTL`, which changes legacy TTL. It also reads `env["SYSTEMROOT"]`, but Windows env keys are case-insensitive (often `SystemRoot`). | architect |
| ADV-P5-A2-08 | MEDIUM | Vacuous / no-oracle property legs [process-gap] | VP-021:91-96; VP-030:101; VP-041:124 | VP-021 generates the thresholds as inputs, then checks p75≤p95 on `costColor`'s output, so the check cannot fail. It also drops BC-1.05.005:122's "(finite inputs)" qualifier, although OD-138 NaN usd can break ordering after `sorted()`. VP-030 `row2InvariantsHold` and VP-041 `oracleSegment(hr)` claim "the BC's canonical table" as oracle for randomly generated inputs, which no pinned table can cover. Same pattern in 3 VPs. | architect |
| ADV-P5-A2-09 | MEDIUM | Contradiction VP-011↔VP-012 | VP-011:39-40,87; VP-012:41-46 | Tier C accepts a divergence that "carries a closed-set id", but VP-012 admits only per-case entries with no globs. Randomly generated cases can never be in `exclusions.json`, so `isClosedExclusion(cs)` has no mechanism. Either a ruled-class divergence such as OD-159 fails Tier C, or a classifier acts as an implicit glob. | architect |
| ADV-P5-A2-10 | MEDIUM | Vacuous fuzz regime | VP-001:142-144,120 | In the renderer regime (subagent stdin is a JSON object), `assertPromisedOutputSet` returns without asserting anything. "Rows and degraded line never mix" (DI-008) is therefore never fuzzed. `isJSONObject` is also undefined: unless it uses Python decode semantics (NaN tokens, ARCH-06), it misclassifies inputs and false-fails. | architect |
| ADV-P5-A2-11 | MEDIUM | VP bcs↔body drift | VP-001:13 vs :40-48 | The body covers CP-A04/A05 (BC-1.07.007) and CP-O10/O11 (BC-1.05.007). Neither BC is in `bcs:`, and neither BC cites VP-001 (grep shows BC-1.05.007 cites only VP-021). | architect |
| ADV-P5-A2-12 | MEDIUM | Weak oracle | VP-003:68-71 | The test asserts only exit 0. It never shows the degraded write was attempted (no writer call count), so an implementation that never writes passes. The BC-1.07.008 subagent write-failure leg claimed at :46-48 has no row. | architect |
| ADV-P5-A2-13 | MEDIUM | Tautological rule | VP-036:44-47 | The >512 KB fixture is exempt "only if it misses" and gated "if it meets", so it can never fail the gate. The brief (:89) asks for an explicit stated exception, not an automatic one. | architect |
| ADV-P5-A2-14 | MEDIUM | Stale count | VP-009:54-55 | The VP claims 68 BCs carry `parity_class: byte-exact` by file grep. The grep finds 97 files, 92 of them in SS-01. | architect |
| ADV-P5-A2-15 | MEDIUM | Stale count (P2) | invariants.md:35,46 | DI-012 is stated as 63 citing BCs. Re-grep by the stated method returns 71. DI-007 = 38 and DI-008 = 83 are correct. | business-analyst |
| ADV-P5-A2-16 | MEDIUM | Skeleton fails a correct impl | VP-009:77; VP-010:81; VP-012:106 | These tests in package `internal/parity` load `internal/statusline/testdata/...` by relative path. `go test` runs with cwd set to the package dir, so they load zero cases and the POL-11 guard turns that into a false red. A module-root resolver must be specified. | architect |
| ADV-P5-A2-17 | MEDIUM | Partial fix (A2-14) | VP-012:139-153 | The register promises "one canonical concrete name per id". OD-76 is still the family glob `TestWindowStart_OD76_*`, with no concrete member in any VP (VP-033 names only TestFindAncestor_RuleRegister). temp-file has two names (:148-149). The glob check covers only `e.Case`, not `e.TableTest`. | architect |
| ADV-P5-A2-18 | MEDIUM | Go misuse (P19/P18) | VP-039:107-111 | A `//go:build arm64` line in the middle of a file is not a build constraint: constraints are per file and must precede `package`, and `go vet` flags a misplaced one. As written, the detector compiles on amd64 legs and fails there. The A2-09 claim that it is "made valid" does not hold. | architect |
| ADV-P5-A2-19 | MEDIUM | P9 self-inconsistency | VP-INDEX:111,228,315 | The map is defined as the union of VP `bcs:` and BC-body anchors. Yet the BC-1.01.009 row omits VP-022 and the BC-1.07.003 row omits VP-006, although both BCs are in those VPs' `bcs:`. | architect |
| ADV-P5-A2-20 | MEDIUM | Cross-ref contradiction | BC-1.03.004:111; VP-038:52-56 | BC-1.03.004 describes VP-038 as "ends-retained pieces … differential vs oracle", but VP-038 is keepends=False with no live differential. VP-038's own Source Contract prose is also stale ("no VP yet", "currently cites VP-025"). | product-owner |
| ADV-P5-A2-21 | MEDIUM | Stale assessment | architecture-feasibility-report.md:33-36 | Says the catalog is 40 VPs. VP-041 (pass 4) makes it 41; the pass-4 sweep did not propagate the count. | architect |
| ADV-P5-A2-22 | MEDIUM | Stale assessment | gene-transfusion-assessment.md:52 | Says "20-session cost goldens". VP-021 and BC-1.05.008 were corrected to 21 sessions (A09/C2-04). | architect |
| ADV-P5-A2-23 | MEDIUM | Inventory gap | dtu-assessment.md:27-30,41-49 | The external-contract inventory omits the Claude Code transcript JSONL. That format is upstream-owned and drives 21 S1.03 BCs, yet it has no fidelity row, extension vectors, or compatibility assumption, unlike both stdin contracts. | architect |
| ADV-P5-A2-24 | MEDIUM | Contradiction | VP-015:44-45,101-103 vs ARCH-02:98-106 | "Unknown `HYLO_*` never changes exit status (asserted)": the skeleton observes no exit status at all. Also, `HYLO_BACKENDS_1_NAME` both warns and trips the cardinality error, so `config validate` exits 1. | architect |
| ADV-P5-A2-25 | MEDIUM | Missing oracle | VP-016:93-101 | `want` is computed by the same `FirstErrorLine`, so only stability under permutation is checked. A consistently wrong order (for example alphabetical by env name) passes. Registry order itself is never asserted. | architect |
| ADV-P5-A2-26 | MEDIUM | Untestable leg | VP-020:52-57,107,111 | The OD-166 guard covers usd or api_ms, but `cost.Record(hist, sid, usd)` has no api_ms parameter. `degradeAttempted(t, dir)` has nothing to observe after a library call that does not render. | architect |
| ADV-P5-A2-27 | LOW | Ambiguity | capabilities.md:29; ubiquitous-language.md:45 | "stdin `rate_limits` only" conflicts with effective_rl smoothing, which shows cached `rl` for RL_KEEP=1800 s (legacy SL:298-312). An implementer could drop the smoothing. | business-analyst |
| ADV-P5-A2-28 | LOW | Factual error | owner-validation-list.md:217 | Calls U+2581 the "light-shade glyph". U+2581 is LOWER ONE EIGHTH BLOCK; light shade is U+2591. SM-05:88 correctly shows the one-eighth block. | business-analyst |
| ADV-P5-A2-29 | LOW | Factual error | VP-023:105 | Says Kawi digits are "in 14.1". There is no Unicode 14.1; Kawi arrived in 15.0. | architect |
| ADV-P5-A2-30 | LOW | Oracle under-specified | VP-002:37-40 | The statement echoes `<flag>` raw, but BC-4.01.002:60 escapes control bytes and invalid UTF-8 as `\xNN`. The fuzz feeds arbitrary bytes, so an oracle written from the statement would false-fail a correct implementation. | architect |
| ADV-P5-A2-31 | LOW | Ambiguous skeleton | VP-007:80-83 | `env.NowReads()` is read after two `Render` calls on the same generator env. If the counter is cumulative, a correct implementation reports 2 and fails. | architect |
| ADV-P5-A2-32 | LOW | Threshold rationale (P16) | VP-018:49,90-92 | Explains why `renameRetryLimit` is a constant but not why the value is 2; it carries no measured or judgment-call label. | architect |
| ADV-P5-A2-33 | LOW | Spec drift | VP-028:42 | The project label omits legacy's root fallback `or normpath(proj_dir)` (SL:460). | architect |
| ADV-P5-A2-34 | LOW | Vacuous generator | VP-040:102-111 vs :85 | One `anchorCols` config serves P1/P5/P6/P7, but P7 needs the "negated int64 spread" generator. A single text argument also cannot express P7's "rows > 2". | architect |
| ADV-P5-A2-35 | LOW | Carve-out not propagated | entities.md:39; capabilities.md:37 | ENT-15 and CAP-015 still say config errors are "one-line" output. They lack the OD-168 subagent rule (zero bytes, diagnostic on stderr) that CAP-009 and DI-008 carry. | business-analyst |
| ADV-P5-A2-36 | COSMETIC | Label | VP-012:15; L2-INDEX:87,90 | VP-012 `proof_method` says testing/quick, but the method is a mutation catalogue. L2-INDEX gives ID formats ENT-NNN/EVT-NNN, but the actual IDs are ENT-01/EVT-01. | architect / business-analyst |

## 2. Policy compliance
- P1 append_only_numbering: PASS (VP-001..041 contiguous, no reuse)
- P2 lift_invariants_to_bcs: FINDING 15 (deferrals are explicit; the count is stale)
- P4 semantic_anchoring_integrity: FINDING 03, 04, 20
- P5 creators_justify_anchors: PASS
- P6 subsystem names: PASS (matches ARCH-INDEX:55-60)
- P9 vp_index_is_vp_catalog_source_of_truth: FINDING 19, 11
- P11 ci_positive_coverage_assertion: PASS (count guards present; see 16 for the path that would trip them)
- P12 settled_decisions_are_constraints: PASS (06 raised as [owner-question] only)
- P13 parity_before_behavior_change: FINDING 08 (NaN ordering)
- P14 public_repo_hygiene: PASS
- P16 thresholds_are_explained: FINDING 32
- P17 ledger_format_frozen: PASS
- P18 cross_platform_from_day_one: FINDING 06, 07, 18
- P19 go_hardening_toolchain: FINDING 18
- P20 config_over_code: PASS
- P21 public_artifact_hygiene: PASS

## 3. Files not fully read
VP-004 lines 1-29 and the first 9 frontmatter lines of VP-007/008 and VP-010..041 were skipped; I relied on VP-INDEX for their `bcs:` except where I read them. Everything else in the perimeter was read in full.

## 4. Novelty
MEDIUM. The new classes this pass are: API drift after ADV-P4-D07 (01, 02), BC routings that point at VP legs that do not exist (03, 04), a missed decode site (05), and skeletons that fail a correct implementation for environment or toolchain reasons (06, 16, 18).

NOT_CONVERGED


## Perimeter B (BC-1.01/1.02)

Findings: 16 (high 2, medium 7, low 6, cosmetic 1).

## Adversarial Review: Pass 5, Perimeter B (BC-1.01.\*, BC-1.02.\*)

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P5-B01 | HIGH | contradiction / partial-fix propagation | BC-1.01.009:63-67 vs ARCH-03-statusline.md:62-70, error-taxonomy.md:42,123-124 | The step table is out of date against ARCH-03 and the error taxonomy in five places:<br>(a) Step 7d says "Can degrade? no". But CP-O10 (legacy SL:616, `f"{usd:.2f}"` on a huge int) and CP-O11 (SL:623, `api_ms / 3.6e6`) degrade at that step. ARCH-03:70 lists both.<br>(b) Step 7c omits OD-166, under which Go skips the record_cost write. So PC2 ("writes of steps 1..k-1 exactly as written") is false for a 7d degrade.<br>(c) Step 2 omits the CP-O06..O08 skip and CP-O09.<br>(d) Step 5 omits CP-N03.<br>(e) Step 7b omits CP-O01..O05.<br>The Decisions row lacks OD-156 and OD-166. Sibling: VP-008:63 tests only "CP-S/CP-N triggers". | product-owner (VP-008: architect) |
| ADV-P5-B02 | MEDIUM | incompleteness | BC-1.01.001:53-54, :84 | PC3 lists the guarded sites as CP-S01..S17, CP-N01/N02 and unmapped panics only. E-REN-002 (error-taxonomy.md:42) also routes CP-N03, CP-O01..O05 and CP-O10/O11 through this guard. EC-003 says an unmapped panic is a parity failure "because legacy would not degrade", which is false for the CP-O sites. | product-owner |
| ADV-P5-B03 | HIGH | P20 config-over-code / P4 mis-anchor | BC-1.02.001:67; BC-2.01.004:102-120; BC-1.02.005:67; BC-1.02.006:61-62; interface-definitions.md:241 | BC-1.02.001 PC4 says the `◨` glyph comes from `statusline.glyphs.*`. BC-2.01.004 PC6 enumerates "exactly" 13 members and `◨` is not one of them. The glyphs `⎇` (SL:413), `▰` and `▱` (SL:428) have no key at all, which contradicts OD-02 (a glyph table with legacy defaults). The Contract column of the glyph-family row also omits .001, .005, .006 and .008. | product-owner |
| ADV-P5-B04 | MEDIUM | semantic mis-anchoring | BC-2.01.004:117, :119 (consumer BC-1.02.018) | `statusline.glyphs.reroute` is `⟳`, which in legacy means cache reads (SL:594). `statusline.glyphs.stale` is `↻`, which means cache rebuilds (SL:598-599). Neither name describes its glyph, and both become public `HYLO_*` env names, so renaming after release would break users. | product-owner |
| ADV-P5-B05 | MEDIUM | legacy mismatch (P13) | BC-1.02.011:86; BC-1.02.012:85; sibling BC-1.02.014:99 | Both ECs claim OverflowError for any `\|n\| ≥ 2**1024−2**970`. A huge negative `resets_at` instead satisfies `reset <= now_rl` at SL:506 (an exact int/float compare), so pct becomes None and the window is skipped at SL:514. SL:515 is never reached: the window is hidden and nothing degrades. Sibling: in `_fmt_lines` a huge negative `n` takes the `str(n)` path (SL:860) and renders exactly. A test written from these ECs would wrongly expect a degrade. | product-owner |
| ADV-P5-B06 | MEDIUM | legacy mismatch | BC-1.02.004:62, :109 | The claim "any other lone surrogate … the walk's except returns `""`" is wrong. CPython's `genericpath.isdir`/`isfile` catch ValueError (UnicodeEncodeError is a subclass) and return False. The walk therefore continues upward and returns the nearest ancestor repo's branch, not `""`. Confidence MEDIUM: derived from the CPython 3.11 genericpath source, not run. | product-owner |
| ADV-P5-B07 | MEDIUM | sibling drift (P2) | BC-1.02.027:86, :103, :109; BC-1.02.028:70-71, :87, :104, :110 | Both BCs carry vectors tagged with the OD-160 exclusion. Yet both list only DI-008 and state "byte-exact (no exclusion entry)". Their sibling BC-1.02.017:121 cites DI-012 for the same OD-160 shapes. | product-owner |
| ADV-P5-B08 | MEDIUM | P4 VP anchoring | VP-041:37-59 vs BC-1.02.019:101, BC-1.02.025:125, BC-1.02.027:96, BC-1.02.028:96 | These BCs route their fuzz/for-all legs to VP-041, and VP-041 lists them as partially covered (:64-65). Its Property Statement has no claim for them: P-d covers only "blue channel = 30", not the grid-equality leg. | architect |
| ADV-P5-B09 | MEDIUM | P20 [owner-question] | BC-1.02.009:47, :111, :163 | The reroute-all literals `claude` / `claude-` stay hard-coded in logic as a "named constant". The CLAUDE.md iron rule forbids hard-coded models, and no OD rules on this. Question for the owner: register the list as a key with the legacy default? | product-owner |
| ADV-P5-B10 | LOW | spec gap | BC-1.02.030:63-65 | PC4 says a malformed window "makes the limits loop raise at SL:503", with no reroute-all carve-out. Under reroute-all, SL:489 sets `rl = {}` and nothing raises. EC-007 covers only good objects. | product-owner |
| ADV-P5-B11 | LOW | registry inconsistency | interface-definitions.md:140 | `statusline.git.ttl_s` says a negative TTL means "always recomputed". Legacy SL:409 (`now - ts > ttl`) keeps a `ts` more than \|ttl\| in the future fresh, which is consistent with BC-1.02.005 EC-007. The row also cites SL:99-100, but SL:100 is NARROW_COLS. | architect |
| ADV-P5-B12 | LOW | stale citation | BC-1.02.014:77 | The `_fmt_lines` thresholds are cited as "SL:866-867", which is `_fmt_tok_c`'s `float()` try block. The correct lines are SL:856 and SL:858. | product-owner |
| ADV-P5-B13 | LOW | registry duplicate | interface-definitions.md:219-220 | The `statusline.cost.basis_min_mtok_month` row appears twice. BC-1.02.029 consumes it. | architect |
| ADV-P5-B14 | LOW [process-gap] | provenance | BC-1.01.001:7; BC-1.01.009:7, :22-24; BC-1.01.002:81; BC-1.02.014:64, :98-99; BC-1.02.022:94 | Timestamps and "oracle-verified 2026-11-18" claims postdate today (2026-11-17). Modification histories also list 2026-11-17 entries after 2026-11-18 ones. Verification provenance cannot be audited. | product-owner |
| ADV-P5-B15 | LOW | ambiguity | BC-1.02.006:86 | "n > 100 is capped" conflicts with "Any out-of-range value is a number-range config error": does Go clamp or reject? | product-owner |
| ADV-P5-B16 | COSMETIC | typo | BC-1.02.004:63 | "statt" should be "stat". | product-owner |

Checks that came out clean:
- Every canonical vector I recomputed matches legacy: heat colours, `/0K` and `/1000K`, half-even percentages, the countdown floor-divmod, the 0.9 boundary, the effective_rl sequence countdowns, `_hm`, window-age, the trim staircase arithmetic, and the 29/45/64-byte counts.
- No defect found in BC-1.01.002..008, BC-1.01.010, BC-1.02.002, .003, .007, .008, .010, .013, .015, .016, .018, .020..026 or .029 beyond the items above.

### 2. Policy compliance

- P1 append_only_numbering: PASS (contiguous .001-.010 and .001-.030).
- P2 lift_invariants_to_bcs: FINDING B07.
- P4 semantic_anchoring_integrity: FINDING B03, B04, B08.
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS (all 40 are `"SS-01"`, matching ARCH-INDEX:55).
- P7 H1 = BC-INDEX = PRD: PASS (all 40 titles match; H1s describe the postconditions).
- P12 settled_decisions_are_constraints: PASS (B09 is raised as an owner question, not a challenge).
- P13 parity_before_behavior_change: FINDING B01, B05, B06.
- P14 public_repo_hygiene: PASS (scanned for private paths, private-range IPs and the hygiene terms; none found).
- P16 thresholds_are_explained: PASS.
- P17 ledger_format_frozen: PASS (no ledger contact; DI-007 is respected).
- P18 cross_platform_from_day_one: PASS.
- P19 go_hardening_toolchain: N.A. in this perimeter.
- P20 config_over_code: FINDING B03, B09.
- P21 public_artifact_hygiene: PASS (no flagged strings quoted).

### 3. Coverage limits

**Read only partly:**
- Frontmatter (lines 1-27) was read only for BC-1.01.001-004 and BC-1.01.009; the other 35 BCs were read from the H1 onward.
- VP-028, VP-001 and VP-008 bodies were not read (VP-008 was searched only).
- prd-supplements/test-vectors.md was not opened.
- capabilities.md, invariants.md and the PRD were searched, not read in full.
- BC-2.01.004 was read only at lines 95-135.

**Python claims I could not verify (no execution):**
- The SHA-1 cache keys in BC-1.02.005.
- The `ntpath` outputs in BC-1.02.022 PC4.
- The golden byte counts in BC-1.01.010 PC4 and BC-1.01.007.
- The JSON depth limit (993/994).
- The `_hm` outputs for 5e23 and 1e24.
- The B06 behaviour, which comes from reading the genericpath source rather than running it.

### 4. Novelty and convergence

Novelty: **MEDIUM**. B01, B03, B05, B06 and B08 are new defects; B01 and B02 are gaps where pass-3/4 changes reached ARCH-03 but not these BCs.

**NOT_CONVERGED**


## Perimeter C (BC-1.03/1.06/1.07)

Findings: 17 (high 3, medium 8, low 5, cosmetic 1).

**Adversarial review, Phase 1d, pass 5, perimeter C** (status line BCs: BC-1.03.001..021, BC-1.06.001..002, BC-1.07.001..008)

Overall: 17 findings (3 HIGH, 7 MEDIUM, 6 LOW, 1 COSMETIC). Not converged.

Most canonical vectors are correct. I recomputed the byte sizes and caches by hand against the legacy source:
- BC-1.03.002–.012, .016, .017, .019, .020, .021
- the CP-O06/O07/O08 overflow vectors in BC-1.03.006, .007 and .010
- every subagent wire string in BC-1.07.004–.006
- the D4-EX-2 wrong-shape table: all 21 rows in BC-1.03.019 and its BASE cache

The two weak vectors are in findings C09 and C12. Titles match across each BC's H1, BC-INDEX and the PRD for all 31 BCs. The config ranges in interface-definitions.md:172-178 and 192-205 match the BCs, with C03 as the exception.

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P5-C01 | HIGH | contradiction / settled decision (P12) | BC-1.03.018:49-50, 64-66, rows 78-79; BC-1.03.006:97; BC-1.03.007:78 | **Scope of OD-167.** BC-1.03.018 drops the in-flight turn only at the CP-O08 site; the CP-O06/O07 skips leave `cur` unchanged. Every other artifact applies the drop to all three overflow paths: OD-167's text ("a transcript-borne overflow skips the offending line AND drops the in-flight turn", log:154), ARCH-03:62 and 84-86, error-taxonomy:145-149, and VP-013:38-40. The CP-O06/O07 vectors in BC-1.03.006/.007 have no timestamps, so `cur` is null anyway and no test settles it. [owner-question] only if the narrow reading is intended; then OD-167, ARCH-03, the taxonomy and VP-013 must narrow instead. | product-owner |
| ADV-P5-C02 | HIGH | self-contradiction / untestable property | BC-1.03.018:82-83 (PC4), VP row 126; BC-1.03.010:111 | **Delete-the-line oracle has no OD-167 exception.** PC4 says hylo's cache equals legacy's on T with the skipped lines deleted, except `size`. PC2 (64-66) makes an exception for CP-O08, PC4 does not. The CP-O08 vector forces `"cur": null`, while legacy run on U0+A2 keeps `cur` open with the huge `out`. Legacy-with-deletion would also re-raise at the next closer, so the oracle is undefined there. The fuzz property "Delete-the-line equivalence holds … with injected W-lines" fails as written for CP-O08, and for CP-O06/O07 under C01's broad reading. | product-owner |
| ADV-P5-C03 | HIGH | config over code (P20) / mis-anchor (P4) / P12 (OD-173) | BC-1.07.006:110, 166-169; BC-2.01.004:102-120; interface-definitions:159-160 | **Agent-panel lane tag has no config source.** BC-1.07.006 takes the U+25E8 square from `statusline.glyphs.*`, but that registry is closed ("exactly these members", 13 entries) and has no U+25E8 member. A grep for 25E8 across specs/ finds only BC-1.07.004/.005/.006. The words `DGX`/`ANTH` are not tied to the OD-173 keys `statusline.pill.label_local`/`label_cloud`, whose only listed consumer is BC-1.02.001. An implementer would hard-code the tag text, which violates D15/OD-173. Also, BC-1.07.007 PC1 and BC-1.07.006 PC2 never name the theme keys behind the cyan token colour and the grey model/clock colour. | architect (registry) + product-owner |
| ADV-P5-C04 | MEDIUM | spec drift vs legacy | BC-1.03.018 rows 78-79 vs SL:1069-1087, 1101-1103, 1108-1112 | **"Legacy mutations before the raise: none" is wrong for CP-O06/O07.** By the time legacy reaches SL:1108, it has already run the turn step (SL:1069-1087) and recorded the id (`seen_ids.add`/`recent_ids.append`, SL:1102-1103). For the SL:1109-1112 and SL:1117 sites it has also updated `tin`/`c_in`/`c_wr`/`c_rd`/`tout`. The CP-T04 row (74) lists the equivalent mutations correctly. "none" invites a catch-at-site implementation that leaves partial mutations behind. | product-owner |
| ADV-P5-C05 | MEDIUM | under-specified predicate | BC-1.03.010:98 (EC-009); BC-1.03.018:80 vs SL:991-994 | **CP-O08 is stated by magnitude only.** Legacy `_finish_turn` returns before `TURN_STALE * out` in three cases: `t0` is null (SL:991), `out <= 0` (so a huge *negative* `out` never raises), or `span <= 0` (SL:994). A magnitude-only predicate would skip closers that legacy processes cleanly. The SL:996 site is unreachable, because the multiplication always raises first once `out` is at or above the bound. No vector pins the non-raising cases. | product-owner |
| ADV-P5-C06 | MEDIUM | internal contradiction / P12 (OD-170) | BC-1.07.006:163-165 vs PC2 47-48, EC-004:79 | **Refactoring note says `TrimSpace`.** The authoritative text uses `pyfmt.Strip`, and OD-170 (log:160) rules that pyfmt never consults Go's `unicode` package for whitespace. Go's `unicode.IsSpace` leaves U+001C..U+001F, which Python's `str.strip()` removes. A prefix entry with a leading U+001F would match differently from legacy. | product-owner |
| ADV-P5-C07 | MEDIUM | parity hazard in implementer guidance | BC-1.07.007:193-194 vs Inv3/Inv4 (79-82), ARCH-03:127 | **Refactoring note uses `float64(time.Now().UnixMilli())`.** That truncates below 1 ms, bypasses the injected `Env.Now` (a Python `time.time()` value), and contradicts the `time.time() * 1000` float-product rule. When the true elapsed time is less than 1 ms past a whole second, legacy shows N s and Go shows N−1 s, so the MM:SS bytes differ. | product-owner |
| ADV-P5-C08 | MEDIUM | partial fix not propagated | error-taxonomy.md:158-159 vs BC-1.03.018:45-48, 78-79 | **Taxonomy not updated after ADV-P4-C08.** BC-1.03.018 widened CP-O06 to SL:1108-1112 and added the CP-O07 mirror case (a huge-int `pp` meeting a float `prompt`). The taxonomy rows still give CP-O06 as "SL:1108" only and CP-O07 as the float-`pp` case only. | architect |
| ADV-P5-C09 | MEDIUM | vector cannot be satisfied as a test | BC-1.03.014:78, 87-88 | **Hylo expectation mismatches the stated input.** The rows define the input as one line (`{"type": "assistant", "message": {"content": <list>}}`) but expect BC-1.03.019's four-line-transcript cache (`"size": 691` / `584`) and say "T01+ state otherwise" (it should be BASE; T01+ is a different row). For the stated single line, hylo writes an all-zero cache with a size of about 77 bytes. | product-owner |
| ADV-P5-C10 | MEDIUM | invariants not lifted to sibling BCs (P2) | BC-1.03.007:119; BC-1.06.001:134 | **Missing DI-012 citations.** BC-1.03.007 owns the CP-O07 D4-EX-2 skip vector (98-105) but cites only DI-007; its siblings BC-1.03.006:129 and BC-1.03.010:125 cite DI-012 (ADV-P3-C18). BC-1.06.001 PC2 (74-79) carries the OD-163 own-temp cleanup deviation but cites only DI-007; its sibling BC-1.06.002:119 cites DI-012. | product-owner |
| ADV-P5-C11 | MEDIUM | mis-anchor (stale line numbers) [process-gap] | BC-1.07.001:107, 122; BC-1.07.008:136 | **Line anchors into ARCH-03 drifted again.** "ARCH-03:137-138" now points at the `EnvVars` interface; the subagent.go placement is ARCH-03:172-174. "ARCH-03:125-133" points at the `Env` struct; the `recover()` backstop is at ARCH-03:165-167. This is the second drift after ADV-P4-C12. Line-number anchors should be replaced with the stable fragment `#subagent` (ARCH-03:199). | product-owner |
| ADV-P5-C12 | LOW | vector does not discriminate | BC-1.03.013:67, 85 | **50×é does not test per-code-point behaviour.** EC-002 says per-byte substitution "would give 80"; it gives 100 underscores, and truncating to 40 yields the same 40 underscores as the correct answer. Neither EC-002 nor vector row 3 catches a per-byte implementation. Only EC-006 (`日本`) does, and it is not a canonical vector. | product-owner |
| ADV-P5-C13 | LOW | mislabel | BC-1.07.004:91 | **`killed` row called the fallback.** The row is labelled "glyph fallback U+25CD grey", but `killed` is an explicit `_SUB_GLYPH` entry (SL:846) served by `glyphs.killed`. The fallback is the independent key `glyphs.unknown` (BC-1.07.005 PC1). | product-owner |
| ADV-P5-C14 | LOW | partial fix not propagated | BC-1.07.008:176 | **Refactoring note stale.** It says to fold "CP-A01..A03"; CP-A04/A05 were added in 1.1.1 and are missing. | product-owner |
| ADV-P5-C15 | LOW | VP anchor reciprocity (P4) | BC-1.06.002:111-112 vs 149; BC-1.07.003:93 vs VP-006:13 | **VP cross-references don't match.** BC-1.06.002's VP table lists {VP-018, VP-010}, but its VP Anchors list {VP-018, VP-012}. VP-006 lists BC-1.07.003 in its `bcs`, but BC-1.07.003 never cites VP-006. | product-owner |
| ADV-P5-C16 | LOW | parity vocabulary | BC-1.07.002:17; BC-INDEX:185 | **Undefined `parity_class` value.** `parity_class: OD-155 off switch` is neither in the closed 11-id exclusion set nor `byte-exact`, and the harness has no defined handling for it. | product-owner |
| ADV-P5-C17 | COSMETIC | hygiene | BC-1.03.004:22; BC-1.07.008:85 | A duplicate `1.2.4` entry in BC-1.03.004's `modified`; BC-1.07.008's EC-009 sits between EC-005 and EC-006. | product-owner |

## 2. Policy compliance

| Policy | Result |
|---|---|
| P1 append_only_numbering | PASS |
| P2 lift_invariants_to_bcs | FINDING C10 |
| P4 semantic_anchoring_integrity | FINDING C03, C11, C15 |
| P5 creators_justify_anchors | PASS |
| P6 subsystem name (ARCH-INDEX rule) | PASS (all `"SS-01"`, per ARCH-INDEX:50-55) |
| P7 title consistency | PASS (31/31 identical; titles describe the postconditions) |
| P12 settled_decisions_are_constraints | FINDING C01 (OD-167), C03 (OD-173), C06 (OD-170) |
| P13 parity_before_behavior_change | FINDING C02 (oracle conflicts with the ruled deviation); otherwise deviations are named |
| P14 public_repo_hygiene | PASS |
| P16 thresholds_are_explained | PASS |
| P17 ledger_format_frozen | N.A. (the perimeter never touches the ledger) |
| P18 cross_platform_from_day_one | PASS (the Windows edge cases are disclosed as not executed, ASM-005) |
| P19 go_hardening_toolchain | N.A. |
| P20 config_over_code | FINDING C03 |
| P21 public_artifact_hygiene | PASS |

## 3. Coverage gaps and unverified claims

**Not fully read.** These tails are anchor/boilerplate sections; I read the contracts themselves in full:
- BC-1.03.012 past line 110, BC-1.03.013 past 120, BC-1.03.014 past 115, BC-1.03.015 past 120
- BC-1.03.016 past 130, BC-1.03.017 past 100, BC-1.03.020 past 130, BC-1.03.021 past 120

**Read only partially:** prd.md (BC rows and the NFR and error lines), ARCH-03 (lines 62-86, 120-199), error-taxonomy (lines 38-45, 145-174), interface-definitions (grep only), BC-2.01.004 (lines 88-149), VP-013. **Not read:** ARCH-04, test-vectors.md, capabilities.md, invariants.md, and the other VPs (frontmatter only).

**Python claims I could not verify** (I can't execute code, so these rest on the BCs' own oracle runs):
- the depth limit at the transcript site: 993 accepted, 994 rejected (BC-1.03.004)
- `seek(float)` raising TypeError and `seek(negative)` raising OSError (BC-1.03.002 EC-008/009)
- the "19 bytes already streamed" figure (BC-1.03.006 EC-009); it looks like it came from a synthetic `{"size":0,"tin":…}` probe, not a real mix cache
- `os.stat(True)` being silent in 3.11
- the Windows edge cases, all marked not executed

## 4. Novelty

Novelty: MEDIUM. C01–C07 and C09 are new: the OD-167 scope split, the self-contradicting oracle, the unregistered lane-tag glyph and words, the pre-raise mutation table, the CP-O08 shortcuts, the OD-170 and clock guidance in refactoring notes, and the unsatisfiable vector. C08, C10, C11 and C14 are incomplete propagation of pass-3/pass-4 fixes.

**NOT_CONVERGED**

Main files:
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.018.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.014.md
- .factory/specs/prd-supplements/error-taxonomy.md
- .factory/specs/verification-properties/VP-013-d4ex2-wrong-shape-tables.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.004.md
- legacy/dgx_statusline.py


## Perimeter C2 (BC-1.04/1.05)

Findings: 21 (high 0, medium 9, low 10, cosmetic 2).

## ADV-P5-C2: Perimeter C2 (BC-1.04.*, BC-1.05.*), pass 5

I read all 30 BCs and the legacy file in full, and re-derived the cited legacy lines. Most postconditions, vectors and goldens check out against the source, including the 11-step sequence, the 21-key goldens, the KV/sparkline/TTFT/idle arithmetic, the 37-hop redirect cap and the OverflowError threshold. The findings below are what remains.

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P5-C2-01 | MEDIUM | spec cannot be implemented as written | BC-1.04.001:64-69, 90-95 | PC1 requires hylo to follow a `URI`-only redirect (ADV-P4-C2-08), but its "Normative Go rule" puts all redirect logic in `CheckRedirect`. Go's `Client.do` never calls `CheckRedirect` when `Location` is empty; it returns the 3xx as final (no sample). Go also cannot rewrite the target to urllib's normalized URL from there. Two related gaps: an empty `Location:` makes urllib redirect to `urljoin(full_url, "")`, the original URL, while Go treats it as absent; and the scheme guard admits `ftp`, which urllib's default FTPHandler would try while Go errors. The spec should require a manual redirect loop (`ErrUseLastResponse` plus hops driven by hylo) and say what happens on ftp. Go behavior is from memory of net/http `client.go`; see §3. | product-owner / architect |
| ADV-P5-C2-02 | MEDIUM | loose quirk spec | BC-1.04.001:73-76 | The normalization step is written as `quote(..., encoding="iso-8859-1")`. CPython 3.11 `http_error_302` also passes `safe=string.punctuation`. Read literally (default `safe='/'`), the rule encodes `:` and re-encodes existing `%XX`, so loop keys come out different from urllib's. The spec also omits the `urlunparse` round trip (an empty `?` or `;` is dropped, so `/x?` and `/x` become one key) and that the fragment stays in the key. | product-owner |
| ADV-P5-C2-03 | MEDIUM | unnamed parity divergence [owner-question] | BC-1.04.001:96-97 (PC2); BC-2.02.005:62 | A metrics URL with userinfo (`http://u:p@host:8428`) passes BC-2.02.005. urllib puts `u:p@host` into the HTTPConnection host, DNS fails, and legacy gets no sample. Go's client sends Basic auth and gets a sample. This difference is not in the 11-id exclusion set. Either reject userinfo at load or name the deviation. | product-owner |
| ADV-P5-C2-04 | MEDIUM | unverifiable VP | BC-1.04.001:187 | The VP-030 row says "for any response bytes" the Go map equals legacy's. If that means wire bytes, net/http and http.client disagree on framing: Go rejects malformed header lines that Python's email parser tolerates, and they differ on LF-only lines and duplicate Content-Length. That makes the property false for Tier C fuzz. It should be scoped to body bytes over well-formed HTTP, or the framing cases need enumerating. | product-owner / architect |
| ADV-P5-C2-05 | MEDIUM | internal contradiction | BC-1.05.006:122 vs :135-136 | The VP-012 row names the OD-30 table test `TestCacheSwap_OD30_DuplicateKeyTail`. The Exclusion entry and Dedicated test rows of the same BC name `TestCostHistory_OD30_NumericSidStringKey`, which is also what VP-012:64,147 and VP-INDEX:15 use. The closure check validates the test by name. | product-owner |
| ADV-P5-C2-06 | MEDIUM | cross-doc name drift | BC-1.05.004:137; BC-1.05.009:134 vs VP-012:22,69,152; VP-020:56,104,121 | The OD-166 test is `TestCostHistory_OD166_UnconvertibleNotRecorded` in both BCs and `TestCostHistory_OD166_RecordGuard` in both VPs. VP-012's fail-closed closure cannot validate both names. | product-owner / architect |
| ADV-P5-C2-07 | MEDIUM | propagation gap (partial fix) | BC-INDEX.md:166,171 vs BC-1.05.004:25, BC-1.05.009:25 | The index parity column still says `byte-exact` and `OD-30`. The frontmatter was changed in pass 4 to `OD-166` and `OD-30, OD-166`. The index row was not updated. | product-owner |
| ADV-P5-C2-08 | MEDIUM | config range admits undefined behavior (P20) | interface-definitions.md:216-217; BC-1.05.002 PC1; BC-1.05.005 PC3 | `burn_min_api_ms` and `rate_min_api_ms` accept "any Int". With a value of 0 or less, `api_ms` = 0 (or `false`) passes the gate and Python raises ZeroDivisionError at SL:623 (render degrade) or SL:255. Go's float division would silently give ±Inf or NaN. Neither BC says what happens. Restrict the range to > 0 or specify the outcome. | architect |
| ADV-P5-C2-09 | MEDIUM | imprecise edge case | BC-1.04.003:95; BC-1.04.002:69 | EC-008 says any kept `{}` point raises KeyError at SL:337. It only raises when the `{}` is `hist[-1]`; `[{}, {"t": now-1}]` does not raise. The string/number point shapes are foreign-cache forms but carry no OD-160 tag, unlike EC-009. BC-1.04.002 Invariant 1 still lists only the IndexError site. | product-owner |
| ADV-P5-C2-10 | LOW | incomplete crash register | BC-1.05.005:105; error-taxonomy.md:123-129; ARCH-03:88-91 | EC-011 covers only a huge recorded `usd`. A huge positive `api_ms` that legacy recorded also raises at SL:255 (`api / 3.6e6`). The taxonomy's CP-O10 row says history-borne `usd` "enters `f"{usd:.2f}"`", which contradicts taxonomy:126-129 (the raise is at SL:255). ARCH-03:90-91 calls the history cache the bearer at SL:616/623. EC-011 names no CP id. | architect |
| ADV-P5-C2-11 | LOW | threshold type [owner-question] | interface-definitions.md:238; BC-1.04.003:49-50, 64-66 | `preempt_marker_above` is an Int, but `dgx_preempt:rate5m` is a per-second rate. The historical rule was > 0.01/s (SL:737-738). Any non-zero Int means at least 1/s (300 per 5 min), so the key cannot express a useful threshold. | architect |
| ADV-P5-C2-12 | LOW | coverage gap | BC-1.04.016:42-44; BC-1.04.007 EC-008 | The non-finite field list omits host share (+Inf gives yellow `↺host inf%`), running ±Inf at the idle gate (SL:825), and `last` ±Inf. Its VP claims "each field × {NaN, ±Inf}", but there are no pinned rows for these. | product-owner |
| ADV-P5-C2-13 | LOW | missing condition | BC-1.04.001:161 (EC-013) | The CP-N03 degrade happens only when row 2 is rendered (SL:1224 width rule). With rows ≥ 2 on a narrow terminal, `serving_state` never runs and nothing degrades. EC-013 leaves this condition out. | product-owner |
| ADV-P5-C2-14 | LOW | anchoring rule vs practice (P4) [process-gap] | ARCH-03:179-181 | ARCH-03 says its 12 fragment anchors are "the complete, closed set" for BC links. All 30 perimeter BCs link heading slugs (`#interfaces-design-doc-22-…`, `#effect-step-script-…`) instead of `#telemetry`/`#cost`. The links resolve, but the rule is not followed or enforced. | architect |
| ADV-P5-C2-15 | LOW | registry duplicate | interface-definitions.md:219-220 | The `statusline.cost.basis_min_mtok_month` row appears twice. | architect |
| ADV-P5-C2-16 | LOW | wrong disposition note | interface-definitions.md:221 | The `telemetry.query` note says upstream errors "degrade per the CP-S register". Per BC-1.04.001 PC3/PC5 a failed query gives no sample (the dead rung), never a CP-S degrade. | architect |
| ADV-P5-C2-17 | LOW | sibling citation gap (pending intent verification) | BC-1.04.003:121; BC-1.05.005:130 | Both carry the OD-160 exclusion (EC-009; EC-010/011) but cite neither DI-012 nor a VP-012 row. Their siblings BC-1.04.002:113 and BC-1.05.004:136 do. | product-owner |
| ADV-P5-C2-18 | LOW | test-vector index incomplete | test-vectors.md:43 | The row lists CP-N03 but its owning-BC column omits BC-1.04.001/.004/.005. It also omits BC-1.05.002, which co-owns CP-O11 (ARCH-03:91; BC-1.05.002 EC-009). | architect |
| ADV-P5-C2-19 | LOW | H1 incomplete (P7) | BC-1.05.007:35 | The title says "$ and $/h number formatting", but PC3 also specifies the `⛏` format. | product-owner |
| ADV-P5-C2-20 | COSMETIC | stale text | BC-1.04.007:43-45; BC-1.05.005:65-66 | "architect to ratify" and "for the architect to carry into interface-definitions.md" are stale: registry:179 and :185 already carry both rules. The `kv.cells` rationale also differs (BC: line width; registry: render work). | product-owner |
| ADV-P5-C2-21 | COSMETIC | wording | error-taxonomy.md:240; ARCH-03:95 | "a numeric key sorts ahead of every `vllm:` key": dict order is insertion order, not sorting. | architect |

### 2. Policy compliance
- P1 append_only_numbering: PASS
- P2 lift_invariants_to_bcs: FINDING C2-17
- P4 semantic_anchoring_integrity: FINDING C2-14 (anchors otherwise semantically correct)
- P5 creators_justify_anchors: PASS
- P6 subsystem name (SS-01): PASS
- P7 H1 = BC-INDEX = PRD title: titles match across all three; FINDING C2-19, and C2-07 (index parity column)
- P12 settled decisions: PASS; C2-03 and C2-11 raised as owner questions
- P13 parity before behavior change: FINDING C2-01, C2-02, C2-03
- P14 public-repo hygiene: PASS (only RFC 5737 addresses; no paths or names)
- P16 thresholds explained: FINDING C2-11, C2-20
- P17 ledger format frozen: PASS
- P18 cross-platform: PASS
- P19 Go hardening toolchain: N.A. for this perimeter
- P20 config over code: FINDING C2-08
- P21 public-artifact hygiene: PASS

### 3. Not fully read; claims not verified
- **Not read:** VP-001, VP-012 (grepped only), VP-019, VP-021, VP-022, VP-031, ARCH-04, the owner-decisions log; interface-definitions, prd, capabilities, invariants and BC-2.02.005 were read only partly (grep and excerpts).
- **CPython claims I could not check (no execution available):**
  - BC-1.05.007 EC-005: 999.995 formats as `$1000.00` (depends on the nearest double).
  - BC-1.05.005 EC-009: the NaN sort orders.
  - BC-1.04.009 Invariant 2: the n=12 trail RGB table.
  - BC-1.05.005: the 69.9997… and 89.9996… rate digits.
- **Behavior cited from memory, not run:**
  - The 3.11.7 `http_error_302` source text (`safe=string.punctuation`) behind C2-02.
  - Go net/http skipping `CheckRedirect` when `Location` is empty (C2-01).
  - urllib's lack of userinfo support (C2-03).

### 4. Novelty
MEDIUM. The redirect-mechanism, quoting, userinfo, wire-bytes VP, ZeroDivision range and test-name drift findings are new. The rest are propagation residue from pass 4.

NOT_CONVERGED


## Perimeter D (S2-S6 BCs)

Findings: 33 (high 10, medium 16, low 6, cosmetic 1).

## Adversarial Review, Phase 1d Pass 5, Perimeter D (SS-02..SS-06)

All 53 BCs were read. Six findings came from comparing BC text with the legacy source. The Python-side facts in ADV-P5-D01, D02, D06, D07 and D08 rest on my memory of CPython 3.11 and libc internals and were not run here (see section 3).

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P5-D01 | HIGH | Parity (P13/P18): unregistered Windows deviation | BC-5.04.001:65-68; BC-5.04.002 PC-4; legacy SL:984 | Legacy `_iso_ts` catches `ValueError` only (SL:984). On Windows, MSVC `localtime_s` raises `OSError` for negative or post-year-3000 instants. CPython's fold-0 `u1-86400` probe hits that for any naive wall time on or before 1970-01-01 or at or after 3001. The `OSError` propagates out of `_mix_counts` (SL:1069) to the top-level guard, so legacy prints the degraded line. The BC maps every failure to `(0,false)` and the line renders. OD-171 runs the Windows naive cases with no skip, and no closed-set id covers this. | product-owner |
| ADV-P5-D02 | HIGH | Harness determinism (frozen clock) | BC-6.01.003 Pre-3, PC-1, PC-3; BC-5.04.003 PC-1, PC-3; BC-6.02.002 Pre-1 | Python's `time.time()` returns exactly `float(HYLO_TEST_NOW)`. Go converts the string to `time.Time`, then `TimeFloat` computes `float64(UnixNano)/1e9`. At about 1.79e18 ns, float64 spacing is 256 ns, larger than half an ulp of the seconds value (about 1.19e-7 s), so fractional instants can come back as a neighbouring double. Cache `rl_ts`/`ts`/`fetch_ts` are written with repr, so bytes differ. Captured `now` values (decimal, fractional) hit this. The VP-034 row checks only the parse, not the round trip. The canary value `.5` hides it. | architect |
| ADV-P5-D03 | HIGH | Windows harness false-green | BC-6.02.003 Pre-1, PC-1; BC-6.02.002 Pre-2 | Placeholders are "replaced with absolute per-case paths" inside a JSON template, and captured-snapshot paths are byte-spliced. No rule requires JSON-escaping the replacement. Windows temp paths contain `\U…`, `\t…` and similar sequences, which make invalid or altered JSON. Both sides then decode `{}`, produce identical output, and the Windows leg passes while testing nothing. Grep of ss-06 and ARCH-07 found no escaping rule. | product-owner |
| ADV-P5-D04 | HIGH | Wrong statement of legacy behavior | BC-6.03.004:132-137 vs BC-2.02.002:42-44, legacy SL:74 | PC-3 says the NUMBER class "degenerates trivially: legacy crashes at import … exit 1, empty stdout, no caches". That holds only for the grammar crashes (`""`, `four`, `0x4`, rows `2.0`). `float("nan")`, `inf`, `-1`, `1e400`, `4_0` and `٤` all parse at SL:74: legacy renders normally and writes caches, as BC-2.02.002 itself says. The pinned oracle leg for the BC's own canonical case `config/ttl-nan` would fail against real legacy. | product-owner |
| ADV-P5-D05 | HIGH | Contradiction: error surface | BC-2.01.005 PC-5/PC-6 and Inv 2; BC-2.02.001:94-115; error-taxonomy:70-84; BC-2.01.004 PC-6 | The reasons `expected JSON <shape>` and `expected non-empty control-free text of display width 1..16` are absent from both reason vocabularies, yet Inv 2 says every reason comes from that vocabulary. There is no runtime reason string at all for a glyph value that is not 1 code point / 1 column, or for an empty `Text` key (tokens.suffix, process_name, labels.input). Neither the closed six-class register nor the reason-category list says where these errors belong. | product-owner [owner-question: class register] |
| ADV-P5-D06 | HIGH | Contradiction with interface definitions | BC-2.01.005:85 vs interface-definitions.md:118-120 | Shape for RGBTriplesFloat: the BC says `array of 3 arrays of 3 numbers plus 1 number`; interface-definitions says `object {trail,fade,amber,head}`. These differ in both the accepted grammar and the error-line bytes. | product-owner |
| ADV-P5-D07 | HIGH | Contradiction: default-only keys | BC-2.01.005:88-90 vs interface-definitions.md:243-245 | The BC says default-only composite keys "never read their env name". Interface-definitions (OD-162) says any non-default value is a number-range config error. It is unspecified whether `HYLO_STATUSLINE_THEME_HEAT` causes a warning, a config error, or nothing. The BC also calls `statusline.units.context` composite, but it is `Text`, and `limits.windows`/`units.*` are not covered at all. | product-owner |
| ADV-P5-D08 | HIGH | pyfmt: unpinned boundary, signature gap | BC-5.02.006 PC-6, EC-008; BC-5.02.001 Inv 4; ARCH-06:113-114 | The encoder depth boundary is per call site ("reference minus legacy caller-frame depth"), but no site value is measured. The only vector uses a module-scope "reference" that no legacy site has. `Dumps(v)`/`DumpsLen(v)` have no budget parameter, and `ErrDepth` is not in ARCH-06. Real exposure: stdin `rate_limits` deep enough to decode but too deep to re-encode makes legacy skip the session-cache write (SL:307-308). A deep tool_use input makes `json.dumps` raise in `_mix_counts`, which degrades the whole line. | architect |
| ADV-P5-D09 | HIGH | pyfmt semantics | BC-5.01.007 PC-3, Inv 1; legacy SL:254 | `NumCmp` returns 0 for unordered (NaN), and Inv 1 forces every cross-kind comparison through it. Derived `>=`/`<=`/`==` then come out true for NaN where Python says False. Concrete case: cost-history `api_ms` = NaN against int `need` at SL:254 is False in legacy but appends in Go, which changes the percentile colors. The contract defines no NaN-aware relational helpers. | product-owner |
| ADV-P5-D10 | HIGH | Partial-fix regression (OD-171), blast radius 2 | BC-5.04.002 Inv 2 (lines 70-72); BC-6.04.003 Pre-3 (lines 69-71) | Both still say naive or non-UTC cases skip the Windows leg and cite BC-6.02.003 PC-8, which now says the opposite (no skip, TZ=UTC everywhere). | product-owner |
| ADV-P5-D11 | MEDIUM | Contradiction, VP drift | BC-2.02.002:80-84, 121 | `git.ttl_s` admits any finite negative value, but there is no lower bound: −1e300 overflows the Duration conversion, contradicting Inv 1's "conversion well-defined". The VP row still asserts `v >= 0` for every accepted Seconds value, so the property fails for the BC's own EC-010. | product-owner |
| ADV-P5-D12 | MEDIUM | Test vector contradicts the range | BC-2.01.005:79 | The FloatPair example `[50,90]` is outside the registered `[0,1]` range of `cost.percentiles` (interface-definitions:185); the CTV and interface-definitions use `[0.5,0.9]`. | product-owner |
| ADV-P5-D13 | MEDIUM | Untestable grammar | BC-2.01.005 PC-5 | The IntMap rules are unspecified for: extra keys, missing `cc`/`other`, duplicate JSON keys, whether `1.0`/`1e3` count as "JSON integers", and integers beyond int64. | product-owner |
| ADV-P5-D14 | MEDIUM | Registry self-contradiction | BC-2.01.004 PC-3(e) vs interface-definitions:216 | The build test requires every `_ms` key to be a "millisecond integer/float type", but `statusline.cost.rate_min_api_ms` is `IntMap`. Either the build fails or the rule is ambiguous. | product-owner |
| ADV-P5-D15 | MEDIUM | Undefined function, contradicts another BC | BC-2.01.004 PC-6/7; BC-2.01.005 PC-6 vs BC-5.03.001 Inv 1 | "Display width 1..16" and "1 column" require a width function. BC-5.03.001 says East-Asian-width logic is never used, and OD-170's table list has no width class. A label such as `中文` cannot be tested. | architect |
| ADV-P5-D16 | MEDIUM | Oracle generator defect | BC-5.02.002:124 vs table row 51 | The generator literal decodes to JSON text without the `\/` escape, so row 51's stated purpose ("`\/` decodes to `/`") is never exercised. The length still matches (14), so the gap stays hidden. Separately, `print(i, L, repr)` emits spaces, but line 94 says tab-separated output. | product-owner |
| ADV-P5-D17 | MEDIUM | Contradicting depth laws | BC-5.02.001 Inv 4 vs BC-5.02.003 PC-7 | Inv 4 says the decoder and encoder both follow "max depth = limit − 8 at module scope" (992). BC-5.02.003's law `L = 999 − F` gives 995 at module scope (F about 4) and 993 at F=6. A shallower stack cannot have the smaller budget. | architect |
| ADV-P5-D18 | MEDIUM | Mis-anchor (P4) | BC-5.02.006:80 | It cites `save_cache (SL:307)` "invoked from the hook-handler stack". SL:307 is the `c["rl"]` assignment in `effective_rl`, `save_cache` is called at SL:308, and the status line has no hook handler. | product-owner |
| ADV-P5-D19 | MEDIUM | Inconsistent shim contract | BC-6.01.003 Pre-3 vs PC-1; BC-5.04.003 Pre-2 | Pre-3 says the Python shim rejects `float()`'s surplus forms. PC-1 defines `N = float(...)` with no validation and no fallback. The range is stated both as "\|s\| ≤ 62135596800" and as "years 1..9999" (up to 253402300799); these disagree for years after about 3938. | product-owner |
| ADV-P5-D20 | MEDIUM | Sibling contradiction: entry schema | BC-6.03.003 PC-3 vs BC-6.03.004 Pre-2, PC-1; BC-2.02.001:188 | The `temp-file` example entry lacks `package` and `scope`, and its `expected.go-cache-listing.txt` is not the mandated JSON object. BC-6.03.004's validator would reject it ("a key is missing"). BC-6.03.004 also gives `scope` a default while requiring exactly six keys. | product-owner |
| ADV-P5-D21 | MEDIUM | Harness translation gap | BC-6.02.003 PC-2 vs Pre-2 | The Bool mapping covers only `true`/`false` (described as "the JSON literal"), but settings are operator strings. A string `no` or `0` passes through verbatim to legacy, where `no` means on (SL:76-77), which fabricates a divergence. | product-owner |
| ADV-P5-D22 | MEDIUM | Logic hazard (Windows) | BC-3.02.001 Inv 2 (ADV-P4-D32) | When the PID-reuse guard rejects a parent, the walk continues with that impostor's PPID, i.e. up an unrelated process chain, and can match a stranger's `claude` and show a wrong `⌂`. | architect |
| ADV-P5-D23 | MEDIUM | Per-OS TZ semantics | BC-3.01.001 PC-6; OD-171 | `TZ=` (empty: Go `LoadLocation("")` gives UTC, so it is unclear whether that is (a) or (b)) and `TZ=:Area/City` are unspecified. On POSIX, libc (the oracle) treats an invalid TZ as UTC, while OD-171 falls back to the OS zone, an unregistered divergence outside parity. | architect [owner-question] |
| ADV-P5-D24 | MEDIUM | P7: H1 vs postconditions | BC-3.01.001 H1 vs PC-6 | The H1 covers per-OS directories only. PC-6 adds a separate responsibility (`LocalZone`) that the H1, BC-INDEX and PRD title do not mention. | product-owner |
| ADV-P5-D25 | MEDIUM | P18 routing | BC-2.01.001 PC-6, EC-008/009; BC-2.02.001 refactoring note | Windows case-insensitive env matching sits in `internal/config` over an injected Go map (which is case-sensitive). There is no `internal/platform` seam and no rule for how POSIX CI exercises the Windows rule. | architect |
| ADV-P5-D26 | MEDIUM | Partial-fix sibling (D31 notation) | BC-5.03.002 EC-002 | `\x85` is used to mean U+0085. Under the ADV-P4-D31 convention applied in BC-5.01.002:95 it means an invalid raw byte. (pending intent verification) | product-owner |
| ADV-P5-D27 | LOW | Unparsable text | BC-5.01.007 PC-2 (lines 77-81) | "(or dividend operand of zero divisor)" is garbled. Precedence for `10**400 / 0.0` is unpinned: CPython raises `OverflowError` first. | product-owner |
| ADV-P5-D28 | LOW | Stale signature | BC-5.02.001:38 | The Description still says `DumpsLen(v Value) int`; Inv 4 and ARCH-06 say `(int, error)`. | product-owner |
| ADV-P5-D29 | LOW | Workflow contradiction | BC-6.03.001 PC-6 vs PC-8 | `-update` "runs the oracle on Linux", yet `.windows.golden` files must come from a Windows oracle run. The Windows regeneration path is undefined. | architect |
| ADV-P5-D30 | LOW | Anchor | BC-2.01.001:87, BC-2.01.004:91 vs BC-6.04.003 | Both cite BC-6.04.003 as the home of `HYLO_PARITY_FUZZSECONDS`, but BC-6.04.003 never names it, nor its 0/unset semantics (cicd-setup:81 says unset fails on schedule). | product-owner |
| ADV-P5-D31 | LOW | Ambiguity | BC-2.01.002 PC-4 | "Distinct indices present plus index 0" double-counts when `HYLO_BACKENDS_0_*` is set. The tie-break "by registry field order" is undefined for non-P1 fields. | product-owner |
| ADV-P5-D32 | LOW | Incomplete list | BC-2.01.001 PC-2 | The present-but-empty rule omits Text, SGR and composite types. | product-owner |
| ADV-P5-D33 | COSMETIC | Duplicate row | interface-definitions.md:219-220 | The `cost.basis_min_mtok_month` row appears twice. | product-owner |

### 2. Policy compliance
- **P1 (append-only numbering):** PASS.
- **P2 (lift invariants to BCs):** PASS for DI-008/010/012 citations; invariants.md not swept.
- **P4 (semantic anchoring):** FINDING D18, D30.
- **P5 (creators justify anchors):** PASS.
- **P6 (subsystem names):** PASS (SS-02..06 match the ARCH-INDEX registry).
- **P7 (BC H1 = BC-INDEX = PRD title):** FINDING D24. H1 and BC-INDEX titles match for all 53; PRD titles not sampled.
- **P12 (settled decisions):** PASS; D23 is tagged [owner-question].
- **P13 (parity before behavior change):** FINDING D01, D04, D09, D23.
- **P14 (public-repo hygiene):** PASS.
- **P16 (thresholds explained):** PASS.
- **P18 (cross-platform):** FINDING D01, D03, D22, D23, D25.
- **P19 (Go hardening toolchain):** N.A.
- **P20 (config over code):** FINDING D07, D14.
- **P21 (public-artifact hygiene):** PASS (nothing flagged is quoted).
- **P3, P8, P9, P10, P11, P15, P17:** N.A.

### 3. Not fully read, and claims not verified
- **Not read:** prd.md, BC-ALLOCATION.md, ARCH-01/02/05/07/08, VP files (only grepped), capabilities.md, invariants.md. In BC files, the frontmatter above line 30 was skipped in about 40 of them.
- **CPython and libc claims recalled from memory, not run:**
  - glibc and macOS libc fall back to UTC on an invalid `TZ` (D23).
  - MSVC `localtime_s` returns EINVAL for negative or post-3000 `time_t`, and CPython raises `OSError` from it (D01).
  - `json.dump` uses the pure-Python encoder while `json.dumps` uses the C encoder, and the recursion-slot accounting (D08, D17).
  - The ntpath C `_path_normpath` on Windows versus the Python implementation for `//` (BC-5.03.004 PC-2).
  - The `float_divmod` and `local_to_seconds` algorithms; checked against my recollection of CPython source, and they match the BCs.

### 4. Novelty
HIGH. D01–D04, D08 and D09 are new defect classes. Verdict: NOT_CONVERGED.

