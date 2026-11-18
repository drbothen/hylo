---
document_type: adversarial-review
phase: 1d
pass: 13
date: 2026-11-18
scope: full
perimeters: [A, A2, B, C, C2, D]
verdict: NOT_CONVERGED
novelty: MEDIUM
findings: 72
---

# Adversarial Spec Review — Phase 1d, Pass 13

Pass 13 ran as six fresh-context perimeters, the same split as passes 1-12. Each section is the verbatim final report of one perimeter, unedited except for this framing. NOT_CONVERGED (72 findings: HIGH 11 / MEDIUM 34 / LOW 24 / COSMETIC 3; pass 12 had 73 with 13 HIGH). The orchestrator spot-verified A01 (error-taxonomy has no 'config path' exit) and A02 (the only mention of a cost `Store` in architecture/ is ARCH-00's package row) on disk; both held.

## Perimeter A (PRD, supplements, architecture, CI)

Findings: 19 (high 4, medium 9, low 5, cosmetic 1).

**ADV-P13 Perimeter A (PRD, supplements, architecture, CI): findings**

## 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P13-A01 | HIGH | contradiction / closed exit surface | error-taxonomy.md:33-35, :49-61, :154; prd.md:508-509, :526-528; ARCH-00-overview.md:49 | `hylo config path` exits 1 when a directory cannot be determined (prd.md:450, ARCH-01:99-102, interface-definitions.md:62). Yet the taxonomy and PRD §5 say non-zero exits happen only in validate/usage/harness contexts. The catalog also has no error code for this exit. ARCH-01:105 calls error-taxonomy.md "one closed table", so the table it relies on is missing a case. | product-owner (taxonomy, PRD), architect (ARCH-00) |
| ADV-P13-A02 | HIGH | interface gap / anchor to a missing interface | ARCH-00-overview.md:84; ARCH-03-statusline.md:86, :136, :183-229; ARCH-04:119 | ARCH-00 says `internal/cost` "writes via injected `Store`". No `Store` is declared anywhere; grep across architecture/ finds only that one mention. `CacheStore` is declared in package statusline, and statusline imports cost (ARCH-00:60), so cost cannot use it without an import cycle. Step 7c says "internal/cost via Cache". No section gives cost's API (record_cost / cost_thresholds signatures) or its per-file depth constant (990). This is a CRITICAL, gated package with 4 BCs (BC-1.05.004/.005/.006/.009) and nothing for Phase 2 stories to target. | architect |
| ADV-P13-A03 | HIGH | CI contradiction / sibling missed in a partial fix | ARCH-08:52 vs :33-40, :308-314; cicd-setup.md:51 vs :187-196, :312, :318 | Pass-12 call 5 moved govulncheck into the required `lint (gofmt + govulncheck)` job (BC-6.04.001:102-104 also says "govulncheck is a required check"). That breaks the ordering rule that govulncheck becomes required only AFTER go.mod gains its `toolchain` line, which has not landed (ARCH-08:24-26). Branch protection also lists a separate `govulncheck (required)` context that no job in the new structure emits, so that required check would never report. ARCH-08:308-310 and cicd-setup:189-190 still say the lint job runs staticcheck "beside gofmt and vet"; ARCH-08:54/80-82 now put vet and staticcheck on every OS leg. | architect |
| ADV-P13-A04 | HIGH | CI contradiction / ambiguity | ARCH-08:58; cicd-setup.md:55; BC-6.04.001:134, :146 | ARCH-08 describes the Tier A job as "(ubuntu leg ...)". cicd-setup says "3 OSes (ubuntu leg carries setup-python + staleness)", and never says whether the macOS and Windows legs install an interpreter. Under `CI=true`, a leg with no interpreter fails closed (ARCH-08:104-105). BC-6.04.001 expects Tier A failures on macos-15 and "on every leg", and ARCH-07:88-91 defines Windows oracle child environments. Whether live parity runs on macOS/Windows is undecidable from the specs. | architect |
| ADV-P13-A05 | MEDIUM | partial-fix regression | ARCH-08:164-168 vs :168-174; VP-036:83, :90-91 | One timing bullet first says "p95 computed **per case** and binding per case" and then restates the pass-12 call 4 unit as per (case, step). VP-036 still says "binds per case". This conflicts with NFR-001 (nfr-catalog:24, per (case, step)). | architect |
| ADV-P13-A06 | MEDIUM | stale wording | interface-definitions.md:48, :484 | Both places still say `--subagent` is selected "before any flag scan or config processing". Pass-12 A10 (ARCH-01:66-69) explicitly calls that wording false: the subagent path resolves config itself (OD-168). | product-owner |
| ADV-P13-A07 | MEDIUM | partial-fix regression (2 files) | nfr-catalog.md:89-90; module-criticality.md:41-42 | Both say "only the Tier A oracle-differential runs are excluded" from coverage and that parity-machinery tests count. `-skip $ORACLE_TESTS` (ARCH-07:215, ARCH-08:98) excludes five tests, including `TestParityCacheSwap_FourCaches` (a parity-machinery test), the Canary, Tier C and `TestTiming`. So the definition of the gate figure is wrong. | product-owner |
| ADV-P13-A08 | MEDIUM | NFR incomplete | prd.md:501; nfr-catalog.md:28; interface-definitions.md:313 | The fourth legacy render-state cap (90 s `SPARK_MAX_AGE`) is the tunable key `statusline.sparkline.max_age_s`, which has only `> 0` plus the Duration ceiling. NFR-005's list of tunable caps with validation bounds leaves it out and lists `window_age.max_depth` instead, which is not a render-state cap. The four caps and the four bounded keys do not match up. | product-owner |
| ADV-P13-A09 | MEDIUM | unstated assumption | prd.md:501; nfr-catalog.md:28; BC-1.03.003:57-58, :72-74 | NFR-005 calls the 512 KB read step a bound on per-refresh state. The extension loop reads until a LF and is bounded only by file size, so an LF-less tail is buffered whole and re-read every refresh. The NFR does not say this, which invites an invented memory cap (P13) or a false "bounded memory" test. | product-owner |
| ADV-P13-A10 | MEDIUM | threshold rationale contradicts itself (P16) | interface-definitions.md:223-224; ARCH-04:66-71 | The upper bounds `rename_retry_limit` 10 and `rename_retry_delay_ms` 1000 allow about 10 s of sleeping per Save, with several Saves per refresh. The stated rationale is "short enough to stay inside the refresh budget", which the arithmetic contradicts. | product-owner, architect |
| ADV-P13-A11 | MEDIUM | missing risk | risk-register.md:40; ARCH-03:230-324 | The register claims "no security-category risks". ARCH-03 requires a hand-written HTTP/1.1 + crypto/tls client over net.Conn that parses untrusted network bytes: status line, headers, chunked framing, redirects, read-to-EOF bodies. There is no R-row and no named mitigation (fuzz target or parser limits) for that surface. | architect |
| ADV-P13-A12 | MEDIUM | CI self-test cannot pass (P11) | VP-035:93-108 vs cicd-setup.md:100-101, :295; prd.md:634-635 | The per-category canary test requires the scanner to flag planted RFC 5737 / `example.invalid` / `example.com` values. The category scan exempts RFC 5737 and `example` domains, and 192.0.2.x is the PRD-mandated fixture literal. As specified, the canary self-test fails every run, or the scan has to flag every fixture. | architect |
| ADV-P13-A13 | MEDIUM | CI timeouts without sizing (P11/P16) | cicd-setup.md:59 (timing, 15 min), :55 (Tier A, 45 min); ARCH-08:67 | The timing job runs 21 replays per (case, step) plus a CPython oracle median. No timeout is derived from corpus size, so a timeout can kill the job before its positive-coverage line prints. Only the coverage job's timeout has a rationale. | architect |
| ADV-P13-A14 | LOW | ambiguity | cicd-setup.md:56 vs ARCH-08:55, BC-6.04.001:83-88 | Tier B runs inside the plain test legs and also in a separate `parity tier B` job. Which run owns the `tier-b: N goldens compared` census, and whether the job is redundant, is not stated. | architect |
| ADV-P13-A15 | LOW | register coverage rule | error-taxonomy.md:322-345 | The coverage paragraph never states the hylo disposition of CP-T01..T07 (D4-EX-2 skip, BC-1.03.018). Its closing rule ("neither of those is a spec gap") only admits E-REN-001/002, a widget fallback, or CP-O06..O09, so CP-T01..T07 formally fail the consistency check. | product-owner |
| ADV-P13-A16 | LOW | ambiguity / diagram drift | ARCH-08:57, :164 | The diagram and text say "every leg prints the per-OS [timing] report". The plain legs skip `TestTiming` (ARCH-08:98, :104); only the timing job runs it. | architect |
| ADV-P13-A17 | LOW | ambiguity [owner-question] | cicd-setup.md:102-103, :86, :37 | The "usernames" scan category has no stated exemption for the GitHub owner segment of the D1 module path, which appears in go.mod and every import. With `H > 0` failing the job, either every Go file is flagged or the owner identity is silently excluded. Undefined either way. | architect |
| ADV-P13-A18 | LOW | ambiguity | prd.md:519; error-taxonomy.md:59 | The dead-rung text says the red code and the glyph follow config keys, but does not say whether the closing `\e[0m` follows `statusline.theme.reset` (interface-definitions.md:225). | product-owner |
| ADV-P13-A19 | COSMETIC | wording | ARCH-05-platform.md:92-93 | "`golang.org/x/sys/unix` only", followed immediately by `golang.org/x/sys/windows`. | architect |

**Verification for the HIGH findings:**
- **A01:** grep of error-taxonomy.md for "config path" returns 0 matches.
- **A02:** grep for `\bStore\b|package cost` across architecture/ finds only ARCH-00:84.
- **A03:** read ARCH-08:52, :308-314; cicd-setup:51, :312, :318; and BC-6.04.001:102-104.
- **A04:** read ARCH-08:58, cicd-setup:55 and BC-6.04.001:134/146.

## 2. Policy compliance
- **P1** append_only_numbering: PASS (CP-T08 retired; CP-C06/C07 allocated from reserved ids).
- **P2** lift_invariants_to_bcs: PASS (DI-007/008/010/012 are cited by the PRD §8 BCs; not deep-audited).
- **P4** semantic_anchoring_integrity: FINDING A02.
- **P5** creators_justify_anchors: PASS.
- **P6** subsystem names: PASS (PRD §1.6, module-criticality and ARCH-INDEX agree).
- **P7** BC H1 vs PRD rows: PASS (68 H1s sampled: ss-01 S1.01/05/06/07 and all of ss-02..06).
- **P9** VP-INDEX: PASS (41 VPs; 33+7+1; methods sum to 41; ARCH-INDEX homes agree).
- **P11** ci_positive_coverage_assertion: FINDING A12, A13, A14.
- **P12** settled_decisions_are_constraints: PASS.
- **P13** parity_before_behavior_change: FINDING A09 (risk of an invented cap).
- **P14** public_repo_hygiene: FINDING A17 [owner-question].
- **P16** thresholds_are_explained: FINDING A10, A13.
- **P17** ledger_format_frozen: PASS.
- **P18** cross_platform: PASS (A04 touches the per-OS Tier A scope).
- **P19** go_hardening_toolchain: FINDING A03.
- **P20** config_over_code: PASS.
- **P21** public_artifact_hygiene: PASS (no flagged strings quoted).

## 3. Files not fully read
All perimeter files were read in full. BC and VP files were opened only to check specific cross-references: BC-2.01.001, BC-1.03.003, BC-1.05.001, BC-1.04.009/.018, BC-6.04.001, VP-035, VP-036, plus the ss-01..06 H1s.

## 4. Novelty
Novelty: MEDIUM. A01–A04 are new structural gaps: an exit missing from the "closed" exit table, an undeclared cost interface, a govulncheck ordering break introduced by pass-12 call 5, and an unresolved Tier A OS scope. A05–A07 are pass-12 partial-fix leftovers.

**NOT_CONVERGED**

## Perimeter A2 (brief, L2, VPs, assessments)

Findings: 11 (high 2, medium 4, low 5, cosmetic 0).

**ADV-P13 Perimeter A2 (brief, L2 domain spec, VPs, assessments): 11 findings, NOT_CONVERGED**

## 1. Findings

| ID | Sev | Category | File:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P13-A2-01 | HIGH | Missing oracle / vacuous property (P11, P4) | VP-001-never-blank-exit0.md:124-131, :243-248 | The main-entry check says "normal render bytes" are decided by "the committed Tier B render-grammar classifier (VP-010 golden replay)". No such classifier exists. VP-010 (:35-50) defines only byte-equality against goldens, and searching specs/ for "render-grammar\|renderGrammar" finds only VP-001; ARCH-07 has no classifier either. So the oracle for "normal render bytes" is undefined, and the check is either vacuous or cannot be built. Separately, the statement decides the unknown-flag and config-error surfaces "by byte equality" against fixed constants. Both lines are parameterised: `<flag>` per VP-002:40, and `<key>=<value> (<reason>)` per VP-016:43. A fuzz over argv can therefore never match a constant. | architect |
| ADV-P13-A2-02 | HIGH | Contradiction with BC/NFR; incomplete fix propagation | VP-036-render-latency-p95.md:37-43, :83 | VP-036 says "Steady-state render latency", samples per **case**, and "binds per case". NFR-001 (nfr-catalog.md:69-79) and BC-6.04.002 PC1 (:74-86, :104-106) were amended in passes 11-12. They now sample, compute p95 and gate per **(case, step)**, and require "caches and seeds … reset … before every replay, warm-up included — cold-start discipline". The two readings measure different workloads. Under "steady-state", the warm-up fills the mix cache, the large transcript hits the `size == off` early return (SL:1039-1040), and the 100 ms large-transcript ceiling (OD-191) can never fail. | architect |
| ADV-P13-A2-03 | MEDIUM | Internal contradiction in a normative statement | VP-001-never-blank-exit0.md:124-127 vs :51-54 | The Method's main-entry legal set ends with "…the 29-byte degraded line, **zero bytes**". The statement says "On the MAIN entry, no fault class exists that yields blank output", and DI-008 agrees. Only the sketch's separate `len==0` check (:163, :176) blocks the case the normative set allows. | architect |
| ADV-P13-A2-04 | MEDIUM | Semantic anchoring (P4) | VP-014-d4ex1-windows-window-age.md:13, :41-43; BC-3.02.001.md:157-159; BC-1.02.017.md:74, :119-121 | VP-014's oracle is "the canonical vector tables of BC-3.02.001 **and BC-1.02.017**", and its rider test is the one BC-1.02.017 Inv 3 names. Yet `bcs:` is only [BC-3.02.001], and BC-1.02.017's VP table never cites VP-014; VP-012 already reciprocates the same Inv 3 test. In the other direction, BC-3.02.001 routes three rows to VP-014 that its statement does not verify: cache-first short-circuit, `.0` serialisation, and at most `max_depth` probes. | architect + product-owner |
| ADV-P13-A2-05 | MEDIUM | Config over code (P20); coverage gap | VP-033-process-probe-correctness.md:38, :68, :82 | The statement hard-codes "at most 6 levels" and the sketch passes a literal `6`. The depth is the registered key `statusline.window_age.max_depth` (prd, ARCH-03/05, BC-3.02.001). The `max_depth = 0` ⇒ zero-probes behaviour has no VP leg, yet VP-014:50-52, VP-019:46-48 and dtu-assessment.md:87 rely on it for `cache-003` parity. BC-3.02.001:159 routes "at most `max_depth` probe calls" to VP-033, whose statement only checks the default. | architect |
| ADV-P13-A2-06 | MEDIUM | Oracle independence | VP-012-exclusion-set-closure.md:85-95, :225-244 | Rider completeness is asserted against `RiderRegister()`. Only its **keys** are pinned to the 12-id closed set; how the per-id test sets are sourced is never stated. A change that deletes three D4-EX-3 tables, or `TestD4EX3_Text`, and also drops them from the register passes. The statement's claim that such deletions "red the check" holds only if the register values are pinned to BC-6.03.004 (for example, parsed from it). This is the same two-copies class that pass 9 fixed in VP-006. | architect |
| ADV-P13-A2-07 | LOW | Stale count (P2) | domain-spec/invariants.md:31, :46 | DI-008 is listed as "89 BCs" (pass-12 re-grep). The same `grep -l DI-008` over `ss-0*/` now returns 90 files; DI-007 = 38 and DI-012 = 79 still match. | business-analyst |
| ADV-P13-A2-08 | LOW | Boundary mismatch (P16) | product-brief.md:90-92 vs VP-036:53, :104 | The brief says the large-transcript p95 "must stay **under** 100 ms" (strict). The VP fails only when p95 "**exceeds** 100 ms", so p95 = 100.0 ms (0.1 ms report resolution) passes the VP but breaks the brief. Also at VP-036:56-59, "fails the build only with `HYLO_TIMING_GATE=1`" conflicts with "also fails … when zero cases were measured", which the sketch runs unarmed. | architect |
| ADV-P13-A2-09 | LOW | Ambiguity in typed-error fields | VP-017-exactly-one-backend.md:38-39, :84-85 | The statement says the error carries "the value `backends=<count>`" and the sketch pins `Value == "backends=2"`. The uniform renderer is `<key>=<value>` (VP-016:43, BC-2.01.002:81), which would print `backends=backends=2`. The split between Key and Value is unstated. | architect |
| ADV-P13-A2-10 | LOW | Closed enumeration too narrow | VP-035-corpus-hygiene.md:37-39, :80-82 | The hygiene scan covers a fixed list of four testdata trees. `internal/platform` (fake PID chains), `internal/cost` and `internal/parity` are absent, so a fixture added there escapes `TestCorpusHygiene`. | architect |
| ADV-P13-A2-11 | LOW | Assessment claim no longer complete | gene-transfusion-assessment.md:53 | The `internal/config` hybrid row cites only render-time `LOCAL_MODEL_PREFIXES` at SL:444. The OD-155 subagent lane tag reads the same variable at SL:902 (BC-1.07.006), and the row was never updated after OD-155. | architect |

## 2. Policy compliance

- **P1** append_only_numbering: PASS.
- **P2** lift_invariants_to_bcs: PASS, with one stale count (A2-07).
- **P4** semantic_anchoring_integrity: FINDING (A2-01, A2-04).
- **P5** creators_justify_anchors: PASS.
- **P6** subsystem names per ARCH-INDEX: PASS (no drift seen in the sample).
- **P9** vp_index_is_vp_catalog_source_of_truth: PASS. All 41 `bcs:` lists were cross-checked against the coverage map for VP-001, 012 and 041 and spot-checked for the rest; class and method totals add up.
- **P11** ci_positive_coverage_assertion: FINDING (A2-01).
- **P12** settled_decisions_are_constraints: PASS.
- **P13** parity_before_behavior_change: PASS.
- **P14** public_repo_hygiene: PASS.
- **P16** thresholds_are_explained: PASS, with one boundary nit (A2-08).
- **P17** ledger_format_frozen: N.A. (P1 does not touch the ledger).
- **P18** cross_platform_from_day_one: PASS.
- **P19** go_hardening_toolchain: PASS.
- **P20** config_over_code: FINDING (A2-05).
- **P21** public_artifact_hygiene: PASS.

## 3. Files not fully read

- **Sketch tails and Named Tests sections skimmed or unread** in VP-013, 015, 016, 018, 020-026, 029, 031 (the fallback-v table), 038, 040 and 041.
- **Frontmatter `modified:` histories** were read only for VP-INDEX, VP-001, 003, 004, 006, 012 and 036.
- **Fully read:** all domain-spec shards, product-brief, dtu-assessment, gene-transfusion-assessment and architecture-feasibility-report.

## 4. Novelty

MEDIUM. A2-01 and A2-02 are new, substantive defects: an oracle that does not exist, and a VP left behind by the pass-11/12 timing-unit amendments. The rest are refinements.

**NOT_CONVERGED**

## Perimeter B (BC-1.01, BC-1.02)

Findings: 8 (high 0, medium 4, low 3, cosmetic 1).

**ADV-P13 Perimeter B (BC-1.01.\*, BC-1.02.\*): Adversarial Review, Pass 13**

Result: NOT_CONVERGED. I found 4 MEDIUM, 3 LOW and 1 COSMETIC finding. I checked all 40 contracts line by line against `legacy/dgx_statusline.py` and recomputed the arithmetic by hand (HSV colours, half-even rounding, countdown divisions, float floor division, trim staircases, byte counts). Every postcondition I checked matches legacy. All the defects are in test-vector setup and in anchors.

## 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P13-B01 | MEDIUM | test-vector contradiction / partial-fix | BC-1.01.001:111 vs :117; BC-1.01.008:97 vs :105; BC-1.01.009:139 | **Contradictory cache setup in the lone-surrogate vector.** The config lines say "empty cache dir" / "empty cache", but the rows now assume a seeded `proc_start`. BC-1.01.001:117 also contradicts itself: it says the file holds "exactly `rl`/`rl_ts`", then lists "the seeded `proc_start` plus `rl`/`rl_ts`". Legacy keeps whatever was loaded: `effective_rl` loads the cache and appends keys (SL:306-308), so a seeded file ends as `proc_start, rl, rl_ts`. BC-1.01.009:139 asserts "the seeded `proc_start`" but its input never states the seed value, unlike row 2 (`{"proc_start": 900.0}`). The "Verified 2026-11-15" notes (BC-1.01.001:120, BC-1.01.009:142) predate the pass-12 re-pin to the seeded regime. A test author cannot tell which cache file to assert. | product-owner |
| ADV-P13-B02 | MEDIUM | test-vector determinism / sibling not updated / mis-reference | BC-1.02.029:110-123 | **The CP-O12 seed breaks the corpus admission rule.** It uses a truthy `session_id` (`r4`) and a session cache without `proc_start`, and records a "machine-dependent trailing `proc_start` key". BC-3.02.001:106-118 (Inv 4) says every corpus case seeds `proc_start` or is `cache-003`, and the harness rejects an unseeded case with a truthy `session_id`. The pass-12 sweep re-pinned BC-1.01.001/.009 to that regime but not this sibling. It also cites "BC-1.01.001 EC-003-style", but that EC is the unmapped-Go-panic backstop (BC-1.01.001:103) and has nothing to do with `proc_start`. | product-owner |
| ADV-P13-B03 | MEDIUM | semantic mis-anchor (P4/P5) | BC-1.01.001:103 (EC-003) | **Wrong VP for the crash-site register.** EC-003 says "the closed, mutation-tested site register (VP-012) is what keeps such a panic from hiding". VP-012 is the exclusion-set closure: its mutation leg mutates exclusion files (VP-012:15, :164). It has no CP-site register and cannot catch an unmapped panic on a mapped-degrade input. The crash-trigger catalogue is VP-001 (VP-001:37-49); the per-site write-set check is VP-008. | product-owner |
| ADV-P13-B04 | MEDIUM | semantic mis-anchor in a cited VP | VP-019:22 (1.2 entry), :52-54, :63-64 | **VP-019 mislabels BC-1.02.005.** It describes BC-1.02.005 as carrying "the rate-limit cache shape". BC-1.02.005 is the git-branch cache (`statusline-git-<key>.json`, BC-1.02.005:35-44, SL:399-413); rate-limit smoothing is BC-1.02.013/.030. VP-019's own four-cache list (VP-019:37) names the git cache separately, so the description contradicts its own document. An implementer could skip the git-cache swap leg that BC-1.02.005:124 relies on. | architect |
| ADV-P13-B05 | LOW | VP reciprocity | BC-1.01.009:146-150, :184-187 vs VP-019:13, :65-68 | **BC-1.01.009 never cites VP-019 back.** VP-019 lists BC-1.01.009 in `bcs:` and says "the reachability route its Verification Properties note names (SC-21 reciprocity)". BC-1.01.009's VP table and anchors list only VP-008, VP-009 and VP-022; VP-019 appears only in PC2 prose. | product-owner |
| ADV-P13-B06 | LOW | stale wording after a ruling (pending intent verification) | BC-1.02.017:71-74 (Inv 3) vs BC-3.02.001:131 (EC-008) | **D4-EX-1 wording predates ADV-P9-D01.** Inv 3 says D4-EX-1 "is excluded from the parity diff through the OD-105 exclusion-list entry". BC-3.02.001 EC-008 says no `exclusions.json` entry exists, no Windows `⌂` parity case can exist, and the id is closed by the rider test alone. Inv 3 implies excluded parity cases exist. | product-owner |
| ADV-P13-B07 | LOW | cross-doc mislabel | error-taxonomy.md:289 (CP-C07, cited by BC-1.02.007:84) | **CP-C07 describes the wrong data.** It says "a non-numeric per-model count bucket". The buckets summed at SL:1181 are the composition byte counts (res/conv/think, SL:1163-1167), not per-model counts. It also calls CP-C07 "uncatalogued", though it is now catalogued. | architect |
| ADV-P13-B08 | COSMETIC | wording | BC-1.01.009:73; BC-1.02.006:124; BC-1.02.004:90-98 | Three wording slips: (a) step 7a lists "badge, model, project; git segment", but legacy writes the git segment (SL:455-457) before the project label (SL:460-462). (b) EC-010 calls the CP-O01 overflow "CP-S07 family". (c) The PC2.3 "Stat semantics" paragraph is inserted mid-sentence, cutting off the "if it starts with `gitdir:`" clause. | product-owner |

## 2. Policy compliance

- **P1** append_only_numbering: PASS.
- **P2** lift_invariants_to_bcs: PASS (DI-007/008/012 cited where applicable; DI-017 explicitly disclaimed in BC-1.02.001 Inv 1).
- **P4** semantic_anchoring_integrity: FINDING B03, B04 (B07 is related).
- **P5** creators_justify_anchors: FINDING B03.
- **P6** subsystem name: PASS (`SS-01` matches ARCH-INDEX:55).
- **P7** BC H1 = BC-INDEX title: PASS for all 40 (BC-INDEX:67-111). I did not compare against PRD titles.
- **P12** settled_decisions_are_constraints: PASS.
- **P13** parity_before_behavior_change: PASS.
- **P14** public_repo_hygiene: PASS.
- **P16** thresholds_are_explained: PASS (T-codes cited for every threshold).
- **P17** ledger_format_frozen: N.A. (these contracts only state that no ledger is read).
- **P18** cross_platform_from_day_one: PASS.
- **P19** go_hardening_toolchain: N.A.
- **P20** config_over_code: PASS. Key ranges in interface-definitions:214-329 match the contracts, and the OD-194 punctuation constants carry their "why not config" notes.
- **P21** public_artifact_hygiene: PASS.

## 3. Not fully read / not verified

**Not fully read:**
- The frontmatter `modified:` history blocks of most contracts (lines 1-24).
- `prd.md` and `prd-supplements/test-vectors.md`.
- The ARCH-03 body (I read only the anchors at lines 348-389).
- Full `capabilities.md`.
- VP-001, VP-012, VP-019, VP-040 and VP-041 bodies beyond their `bcs:` lines and the excerpts cited above.

**Python claims I could not verify without running the oracle:**
- The stdin JSON depth boundary (993 accepted / 994 rejected).
- Golden-A byte totals (286 / 642 / 701 / 743 / 809) and the golden segment strings. The staircase widths do re-derive exactly from the segment widths.
- The full decimal expansion of OV.
- The 8192-byte chunk boundary in the `.git` pointer read.
- Windows C-implementation `ntpath` results. The pure-Python 3.11 derivation agrees.
- The 4,300-digit `ValueError` path.

## 4. Novelty

LOW to MEDIUM. Nothing new shows up in postcondition semantics. The live defects are propagation leftovers from the pass-12 "seed `proc_start`" regime (B01, B02) and anchor mislabels (B03, B04).

**NOT_CONVERGED**: B01-B04 are MEDIUM, and the mis-anchors B03/B04 block convergence on their own.

Files referenced:
- specs/behavioral-contracts/ss-01/BC-1.01.001.md
- specs/behavioral-contracts/ss-01/BC-1.01.008.md
- specs/behavioral-contracts/ss-01/BC-1.01.009.md
- specs/behavioral-contracts/ss-01/BC-1.02.029.md
- specs/behavioral-contracts/ss-01/BC-1.02.017.md
- specs/behavioral-contracts/ss-03/BC-3.02.001.md
- specs/verification-properties/VP-019-four-cache-swap-parity.md
- specs/verification-properties/VP-012-exclusion-set-closure.md
- specs/prd-supplements/error-taxonomy.md

## Perimeter C (BC-1.03, BC-1.06, BC-1.07)

Findings: 10 (high 1, medium 7, low 2, cosmetic 0).

**ADV-P13 Perimeter C: BC-1.03.\* (21), BC-1.06.\* (2), BC-1.07.\* (8)**

I recomputed the size and field values of every canonical cache vector I opened: BC-1.03.002, .003, .004, .005, .006, .007, .008, .010, .011, .012, .014, .016, .017, .019, .020 and .021. All of them match the legacy code at SL:999-1153. The W-predicates and subagent wire strings also check out against SL:888-936. The defects below are about contradictions with other documents, mis-anchors and gaps, not wrong numbers.

## 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P13-C01 | HIGH | contradiction / settled decision (P12) | BC-1.06.001.md:52-55 | Precondition 1 says the Windows cache dir is `%LOCALAPPDATA%\hylo`. OD-144 (owner-decisions-log:111), ARCH-04-data-files.md:25 and BC-3.01.001.md:64-66 set it to `%LOCALAPPDATA%\hylo\cache`; BC-3.01.001 explicitly rejects the shared-dir reading. | product-owner |
| ADV-P13-C02 | MEDIUM | missing postcondition | BC-1.06.001.md:113-125 (no row) vs BC-3.01.001.md:133, ARCH-04-data-files.md:26-28 | BC-3.01.001 EC-004 and ARCH-04 hand off "an unavailable cache dir is treated as load-empty / save-no-op" to BC-1.06.001. BC-1.06.001 has no postcondition or edge case for a `CacheDir` error, so no test can be written from the owning contract. | product-owner |
| ADV-P13-C03 | MEDIUM | mis-anchor (P4) | BC-1.06.001.md:84 | The Save postcondition sources the write-format rules for all four caches from BC-1.05.009. That BC is the record_cost contract and carries the cost-only deviations OD-30 and OD-166 (BC-INDEX:177). The generic writer is BC-5.02.006 "pyfmt.Dumps: json.dump cache-file bytes" (BC-INDEX:269), which is absent from both the postcondition and Related BCs. | product-owner |
| ADV-P13-C04 | MEDIUM | likely wrong measured claim (confidence MEDIUM, not run) | BC-1.03.021.md:76-77 | The postcondition says "Session, git and cost-history caches keep Save budget = Load budget." The mix-cache asymmetry (save 994 vs load 991) comes from the shared `load_cache`/`save_cache` frame shapes (SL:190-206). The session cache is called the same way from `effective_rl` (SL:306-308). Its `rl` field is taken unchanged from stdin `rate_limits`, so it can reach the stdin depth edge of 993. By the same frame arithmetic it should save and then fail to reload. Needs an oracle measurement or a retraction. | architect |
| ADV-P13-C05 | MEDIUM | untestable / register gap | BC-1.03.002.md:86 (EC-007); BC-1.06.001.md:115 (EC-001); error-taxonomy.md:276-292 | EC-007 sends a non-number cached `size` to "foreign-cache crash class CP-C" and says hylo behaviour is "not specified here". The CP-C register is stated as complete ("no reserved C ids remain"), yet it has no row for mix-cache foreign shapes. Uncatalogued legacy raises: a top-level non-object at SL:1019, a string `size` at SL:1033 (`size < off`), and a non-iterable `ids` at SL:1033 (`list(...)`). OD-160 requires Go table tests, but no expected hylo outcome (degrade or reset) is given. | product-owner / architect |
| ADV-P13-C06 | MEDIUM | mis-anchor (P4) | BC-1.07.002.md:82-84 | Invariant 3 justifies "an unparseable value must not masquerade as `false`" with DI-012 (named deviations). That rule is DI-010 ("invalid config never silently falls back", invariants.md:33), which neither the invariant nor Traceability cites. | product-owner |
| ADV-P13-C07 | MEDIUM | missing canonical vector | BC-1.03.005.md:106-113; BC-1.03.006.md:107-117 | error-taxonomy.md:163 requires each owning BC to carry its trigger "as an edge case + canonical vector". CP-O09 (the 4,301-digit save failure) has only edge cases (BC-1.03.005 EC-008, BC-1.03.006 EC-009). Neither owner has a canonical vector row with an exact cache-dir and stdout expectation. | product-owner |
| ADV-P13-C08 | MEDIUM | mis-anchor in a cross-check index (P4) | prd-supplements/test-vectors.md:47 | BC-1.03.016 is listed as an owner of OD-156 overflow vectors, "including an overflow (≥ 2**1024 − 2**970) row in each owning BC's table". BC-1.03.016 (rows T1-T20, canonical vectors T1/T13/T16/T15) has no overflow row and is not an owner in the register (error-taxonomy.md:216-226). BC-1.06.001 is also listed but has only EC-010. | product-owner |
| ADV-P13-C09 | LOW | under-specification | BC-1.07.002.md:62-63, 92 | With `enabled=false` or a config error, the BC says the renderer is not entered but does not say whether stdin is still read. Legacy always consumed stdin (SL:930). Exiting without draining a large payload can leave the Claude Code writer with a broken-pipe error. BC-1.07.003 Inv 1 ("read exactly once") only covers the enabled path. | architect |
| ADV-P13-C10 | LOW | internal inconsistency | BC-1.03.011.md:43-44 vs :67 | Precondition 1 says each line has a usage object; EC-003 ("first line has no usage") breaks that precondition. | product-owner |

## 2. Policy compliance

- P1 append_only_numbering: PASS (CP-T08 is kept as retired, not reused).
- P2 lift_invariants_to_bcs: PASS for DI-007/008/012. C06 is a DI-010 citation gap.
- P4 semantic_anchoring_integrity: FINDING C03, C06, C08.
- P5 creators_justify_anchors: PASS.
- P6 subsystem name per ARCH-INDEX: PASS (all 31 files say `SS-01`, matching ARCH-INDEX:50,55).
- P7 H1 = BC-INDEX = PRD title: PASS (all 31 checked against BC-INDEX:117-197 and prd.md:216-296).
- P12 settled decisions are constraints: FINDING C01 (OD-144).
- P13 parity before behavior change: PASS. The off switch defaults to legacy, and every deviation is named (D4-EX-2, OD-161, OD-163, temp-file).
- P14 public repo hygiene: PASS (no IPs, home paths, emails or hostnames in the perimeter files).
- P16 thresholds explained: PASS (T-054..T-061 and the k_from/m_from rationale are present and match the registry rationale codes).
- P17 ledger format frozen: N.A. (no ledger I/O in scope).
- P18 cross-platform from day one: PASS with caveat. The Windows legs of BC-1.06.002 EC-003/EC-005 and BC-1.06.001 EC-008 are explicitly marked not executed (ASM-005). C01 is a Windows path defect.
- P19 go hardening toolchain: PASS (the FMA detector placement is stated).
- P20 config over code: PASS. Every key in scope is registered with a matching range (interface-definitions.md:223-224, 252-258, 269-283).
- P21 public artifact hygiene: PASS.

## 3. What was not fully read or not verified

**Files read only in part:**
- error-taxonomy.md (read lines 150-323 plus targeted greps)
- interface-definitions.md (greps only)
- ARCH-03 (headings and file-family lines only)
- VP files (frontmatter `bcs:` lines only, plus the VP-INDEX rows)
- capabilities.md and invariants.md (targeted lines)
- BC-3.01.001 (grep only)
- BC-5.02.006, BC-5.04.001, BC-1.01.008 (not opened)

**Python claims I could not verify (I have no way to run code):**
- The depth edges: transcript and stdin 993/994, mix-cache load 991, save 994/995 (C04 rests on frame arithmetic, not a run).
- The pass-10 two-state cycle on the 608,960-byte transcript.
- Legacy exit status 120 on a shutdown-flush broken pipe (BC-1.07.008 EC-009).
- The surrogateescape and APFS Errno 92 behaviour.
- The shared NaN object identity across refreshes (it is consistent with the CPython `_CONSTANTS` lookup, but I did not execute it).
- All Windows legs.

## 4. Novelty and convergence

Novelty is LOW to MEDIUM. The vector arithmetic and the transcript-machine semantics have converged. The new findings come from cross-document coherence: OD-144 propagation, the BC-1.06.001 anchors and handoff gap, the CP-C register's completeness claim, the CP-O09 vector rule, and the test-vectors index.

NOT_CONVERGED

## Perimeter C2 (BC-1.04, BC-1.05)

Findings: 9 (high 0, medium 5, low 3, cosmetic 1).

## ADV-P13 Perimeter C2 (BC-1.04.*, BC-1.05.*) — Pass 13 findings

I checked every postcondition, edge case and vector against the cited legacy lines by reading the code. I could not run Python, so these are derived results, not oracle runs. The legacy behaviour holds up: the 11-step sequence, the sparkline glyph and colour tables, the KV cell table, the percentile indices, the BC-1.05.008 goldens, the NaN-ordering cases, and the urllib header order and redirect rules all match. The findings below are about propagation and coherence between documents.

### 1. Findings

| ID | Sev | Category | Location | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P13-C2-01 | MEDIUM | Partial-fix regression (sibling lift) | BC-1.04.004.md:75-85, :126, :112-117; VP-012 frontmatter `bcs:` | ADV-P12-C2-06 (v1.2.5, :26) added two degrade shapes to Inv 3, both under the OD-160 exclusion: the giant-int `lr[0]` OverflowError and foreign cached-sample values (string → ValueError at SL:741). The BC did not get the sibling lift that BC-1.04.018 (v1.2.4, ADV-P11-C2-02) and BC-1.04.009/014 (ADV-P12-C2-02) got: its L2 row is DI-008 only (no DI-012), there is no VP-012 OD-160 closure row, the VP-001 row covers only CP-N03, and VP-012 `bcs:` omits BC-1.04.004. The segment BC named as the site (BC-1.04.006, SL:741) has no foreign-value edge case. Its siblings BC-1.04.010/011/012 have no edge case either for their equivalent sites (string `w` at SL:813, `wall` at SL:812, `last` at SL:825). | product-owner |
| ADV-P13-C2-02 | MEDIUM | Contradiction (BC vs architecture) | ARCH-03-statusline.md:81-82 vs BC-1.04.002.md:87-113; error-taxonomy.md:285-286 | ARCH-03 says step 4 (get_sample) does not degrade, and lists only CP-N01/N02/N03 for step 5. BC-1.04.002 Inv 1 says each foreign-cache crash site "raises out of `get_sample` → errDegraded", and the CP-C03/C04 register rows place their sites at SL:1217-1218, which is step 4. Step 5 also omits the OD-160 render degrades in BC-1.04.004 Inv 3, BC-1.04.009 EC-011, BC-1.04.014 EC-008..010 and BC-1.04.018 PC1. Yet step 7c (ARCH-03:86) does list the same class of foreign-history degrade (history-borne CP-O10/O11). The column is applied inconsistently. | architect |
| ADV-P13-C2-03 | MEDIUM [owner-question] | Register completeness | error-taxonomy.md:276-292 vs BC-1.04.002 Inv 1, BC-1.04.003 EC-008/EC-010, BC-1.04.009 EC-011, BC-1.04.004 Inv 3, BC-1.04.018 PC1 | These BCs name foreign-cache degrade triggers that have no CP-C id: session-cache type faults at SL:324/325/335/336/356, the KeyError at SL:337, OverflowError on giant ints, the sparkline faults at SL:664/671/674, and the mix-cache `lr[0]` OverflowError at SL:778-779. That last one is the exact analogue of CP-C06 (mix-cache `tin`). Pass 12 assigned C06/C07 to "uncatalogued" triggers and declared "no reserved C ids remain" inside the OD-160-ruled label "CP-C01..C10" (owner-decisions-log:144). Cataloguing these needs either ids past C10 or a family-level ruling. | architect / owner |
| ADV-P13-C2-04 | MEDIUM | Partial-fix regression (index propagation) | error-taxonomy.md:178; test-vectors.md:47; prd.md:514 | ADV-P12-C2-07 added the stdin-borne CP-O10 overflow leg to BC-1.05.001 (PC5, EC-009, VP-001 row). The CP-O10 owner list, the OD-156 owner list and the E-REN-002 derived carrier set still leave out BC-1.05.001. The sibling CP-O11 lists BC-1.05.002 as co-owner (error-taxonomy:179) for the same "carried by BC-1.05.007" pattern. | architect / product-owner |
| ADV-P13-C2-05 | MEDIUM | P20 sibling sweep gap | BC-1.04.011.md:54-60 (also BC-1.04.007.md:60-63) | PC6 hard-codes `/ 1000` and `* 100` (W→kW, $→¢). PC3-PC6 paint `W`, `°` and `¢/h` without a note. BC-1.04.011 is the only row-2 widget BC with neither the unit-constant note (ADV-P10-C2-12 pattern: BC-1.05.002 Pre 4, BC-1.05.003 PC3) nor the OD-194 "named format constants, not config" note. BC-1.04.007's percent factor `* 100` (PC1/PC3) also has no unit-constant note. | product-owner |
| ADV-P13-C2-06 | LOW | Testability gap | BC-1.04.016.md:46-51, :108 | The VP row promises "each field × {NaN, +Inf, -Inf} … each surface has a pinned row". Precondition 1's preempt-rate field has no row in any class (expected from SL:740: +Inf → yellow `r…·q…`, NaN/-Inf → green). Most -Inf cells are unpinned too (TTFT -Inf → grey `◔-infs`, wall -Inf → white `-infW`, `-inf¢/h`). | product-owner |
| ADV-P13-C2-07 | LOW | Missing edge case | BC-1.04.007.md:62-64; BC-1.04.015.md:83-84 | For kv `-0.0`, Python `max(-0.0, 0.0)` keeps `-0.0`, so `ceil` gives 0 and `.0f` prints `-0`. Legacy therefore renders `KV▱▱▱▱ -0%`. PC3 mentions only NaN argument-order semantics and no table row pins `-0.0`. A Go implementation that clamps through any signed-zero-normalizing path prints `0%`. | product-owner |
| ADV-P13-C2-08 | LOW | Inaccurate claim | BC-1.04.002.md:59-60, EC-006 :128 | "TTL 0 is valid (always fetch)" is false when the stored `fetch_ts` is later than `now`: SL:324 `fetch_ts > now - 0` takes the cached path. This happens after a backward clock step, which BC-1.04.021 EC-003 treats as reachable. | product-owner |
| ADV-P13-C2-09 | COSMETIC | Line-cite drift | BC-1.04.009.md:66 | Pre 2 cites the `hist[-N:]` slice at SL:663. The slice is on SL:664, which is what Pre 1 (:56) and EC-011 cite. | product-owner |

### 2. Policy compliance

- **P1** append_only_numbering: PASS. Edge-case ids are sequential; BC-1.04.013 EC-010 was renumbered properly.
- **P2** lift_invariants_to_bcs: FINDING ADV-P13-C2-01 (DI-012 not lifted into BC-1.04.004).
- **P4** semantic_anchoring_integrity: PASS. ARCH-03 section anchors exist (:47, :133); CAP-010/011 are correct; VP `bcs:` lists are reciprocal except the gap noted in 01.
- **P5** creators_justify_anchors: PASS.
- **P6** subsystem name: PASS. All files use `SS-01`, matching ARCH-INDEX:49-55.
- **P7** H1 = BC-INDEX = PRD title: PASS. All 30 match (BC-INDEX:143-177, prd:242-276).
- **P12** settled_decisions_are_constraints: PASS. ADV-P13-C2-03 is raised only as an owner question.
- **P13** parity_before_behavior_change: PASS. The deviations are confined to the closed set (OD-30, OD-160, OD-166, OD-181, D4-EX-3, temp-file).
- **P14** public_repo_hygiene: PASS.
- **P16** thresholds_are_explained: PASS. Every T-code threshold carries a rationale.
- **P17** ledger_format_frozen: PASS. The metric name is kept (D7).
- **P18** cross_platform_from_day_one: PASS. TLS trust store and case-insensitive filename caveats are covered.
- **P19** go_hardening_toolchain: N.A. Nothing in this perimeter touches the toolchain.
- **P20** config_over_code: FINDING ADV-P13-C2-05.
- **P21** public_artifact_hygiene: PASS. Nothing flagged; only RFC 5737 and loopback addresses appear.

### 3. Not fully read, and Python claims not verified

- **Not read:** VP-030 and VP-001 file bodies (only their `bcs:` lists), domain-spec/invariants.md, BC-1.01.009, BC-5.02.003 beyond the digit-limit lines, and the frontmatter lines 1-30 of most BC-1.04.* files (bodies read in full).
- **Not verified by execution** (no Bash; derived by reading the code only):
  - `round(True, 4)` returns the int `1` (BC-1.05.009 PC3).
  - The urllib/http.client wire claims in BC-1.04.001 (checked only against my reading of the stdlib).
  - The exact float bit patterns of r = 17.497318011387254 and 83.94000000000001 and of the EC-004 rate pair.
  - The `-0` KV rendering in finding 07.

### 4. Convergence

Novelty: **MEDIUM**. I found no new mismatch between the BCs and legacy behaviour. The findings are coherence and propagation gaps: pass-12 fixes that did not reach siblings or index files, the ARCH-03 step 4/5 contradiction, and the CP-C register gap.

**NOT_CONVERGED**

Relevant files:
- specs/behavioral-contracts/ss-01/BC-1.04.004.md
- specs/behavioral-contracts/ss-01/BC-1.04.002.md
- specs/behavioral-contracts/ss-01/BC-1.04.011.md
- specs/behavioral-contracts/ss-01/BC-1.04.016.md
- specs/architecture/ARCH-03-statusline.md
- specs/prd-supplements/error-taxonomy.md
- specs/prd-supplements/test-vectors.md
- specs/prd.md

## Perimeter D (S2-S6 BCs)

Findings: 15 (high 4, medium 5, low 6, cosmetic 0).

## ADV-P13 Perimeter D: S2-S6 BCs, pass 13

### 1. Findings

| ID | Sev | Category | file:line | Defect and evidence | Owner |
|---|---|---|---|---|---|
| ADV-P13-D01 | HIGH | Cross-platform / fail-closed harness (partial-fix regression) | BC-6.01.003:127; BC-6.01.001:76-78; BC-6.01.003:63-66; BC-6.03.002:67-72 | Pass-11 removed the shim's newline reconfigure, so on Windows the canary prints the value followed by CRLF. CRLF→LF conversion is scoped to the case comparator only (BC-6.03.002 PC-1). Two exact-byte checks still expect bare LF: the clock canary (exact stdout `1794615009.4245193\n`) and the version probe (regex `^CPython 3 11 [0-9]+\n$`). As written, Tier A fails closed on every Windows run. The alternative is an ad-hoc normalization that no BC defines. | product-owner |
| ADV-P13-D02 | HIGH | Positive coverage, POL-11 [process-gap] | BC-6.01.003:145-148, 155-163; BC-6.01.002:190-191 | Pass-11 left the ADV-P9-D11 text stale. PC-4 still says the "Windows leg discriminates the LF half only". PC-5's negative control requires `\r\n` without the shim. With no newline reconfigure, the shim-loaded run also writes `\r\n`, so the stdio canary cannot detect anything on any leg. It is a false-green gate. BC-6.01.002 PC-4 ("Windows text-mode stdout would otherwise write `\r\n`") still implies the shim prevents CRLF. Blast radius: two files. | product-owner |
| ADV-P13-D03 | HIGH | Child-env contradiction (pass-12 propagation gap) | BC-6.01.002:109 vs 135-145, CTV 241, PC-3 :183; ARCH-07:92-99 | PC-1 gives the cache-003 Go child `HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0`. The "authoritative exact key sets" and their CTV omit it as a conditional member. PC-3 forbids "every HYLO_* key the case does not set" (cache-003 declares a fake PATH, not a setting). An env builder that passes the exact-set test drops the key. The Go side then walks the real process tree, which is non-hermetic: under a claude parent it renders ⌂ where legacy does not. BC-6.02.003:189 and BC-6.03.003:90 depend on the key. | product-owner + architect |
| ADV-P13-D04 | MEDIUM | Mis-anchor, sibling not updated | ARCH-07:136-138 vs BC-6.01.002:102-104 | ARCH-07 still defines the conditional-PATH trigger as "a subprocess-fake table (the fake `ps` of BC-3.02.002) or the cache-003 EMPTY-bin declaration". BC-6.01.002 (pass-12 call 2) says there is NO fake process table in any parity case. | architect |
| ADV-P13-D05 | HIGH | Internal contradiction, P4/P18 | BC-3.01.001:123 (Inv 2), :162 (VP-032 row) vs :64 (PC-2), CTV :153 | Inv 2 says "the last path component is always the literal `hylo`". The VP row says "the result ends in the component `hylo`". The Windows CacheDir and StateDir end in `cache` and `state` (OD-144). A property test written from Inv 2 or the VP row fails on windows-2025. VP-032 itself (:40) is correct, so the BC is the stale side. | product-owner |
| ADV-P13-D06 | MEDIUM | CI spec drift | BC-6.04.001:55-57 vs :87-89; CTV :146; EC-001 :134; EC-005 :138 | 1. The Description says "parity tiers A and B run in the jobs that execute an ORACLE_TESTS member". PC-3.3 runs Tier B in the plain `-skip` step. 2. The CTV ("Tier A fails on every leg") and EC-001 ("macos-15 leg fails Tier A/B") assume Tier A runs per OS leg, but the BC never states the dedicated Tier A job's OS matrix (ARCH-08:75 only implies legs). Without that, the Windows oracle env and the arm64 FMA check may never meet the oracle. 3. EC-005 says gofmt "fails at step 1", but gofmt moved to the lint job (step 5). | product-owner |
| ADV-P13-D07 | MEDIUM | Unspecified decoder | BC-6.02.002:70-71 vs :90-91, :115-118 | Pre-1 says the harness "never parses" `stdin.bin`. Pre-2, however, locates paths "ONLY as a JSON string value", and Pre-3 seeds every `session_id` any step uses. Both require tokenizing or decoding the snapshot with Python semantics (duplicate keys last-wins, NaN tokens, big ints, non-object snapshots). The decoder and its rules are unspecified. An `encoding/json` extractor would reject the captures Pre-1 says are representable. | product-owner |
| ADV-P13-D08 | MEDIUM | Cross-BC contradiction | BC-5.01.002:36-38 vs BC-2.02.003:64-69, BC-2.02.002 EC-007 | BC-5.01.002 says hylo settings "do **not** use this grammar". BC-2.02.003 parses config values with `pyfmt.ParseFloat`/`ParseInt`, narrowed only by the underscore and Nd checks, and `" 4 "` is valid. An implementer following BC-5.01.002 would use strconv and reject `" 4 "`. | product-owner |
| ADV-P13-D09 | MEDIUM | Missing error verdict | BC-2.01.005:74-87, :196-204; BC-2.02.001:140; BC-5.03.002 Pre-1 | The `invalid UTF-8` check covers Text, glyph, label and separator values only. A List item with invalid POSIX bytes has no verdict: `backends[0].model_prefixes`, `limits.windows`, reroute entries. `pyfmt.Strip` takes code points, and no byte→code-point rule exists. A test for `HYLO_BACKENDS_0_MODEL_PREFIXES=$'\xff'` cannot be written. Legacy accepts it (surrogateescape), so the choice affects parity. | product-owner |
| ADV-P13-D10 | LOW | VP drift | BC-6.04.002:168 vs :114-129 | The VP-036 row says "fails iff ... ANY case's p95 > 25.0 ms". It ignores the large-transcript exemption (100 ms ceiling) and the per-(case, step) unit. | product-owner |
| ADV-P13-D11 | LOW | Spec ambiguity | BC-5.02.002:51 vs :55-59 | The formula passes one identifier, `depthBudget`, to both Decode and DumpsLen. The next sentence says the constants differ (993 vs 991). | product-owner |
| ADV-P13-D12 | LOW | Anchor completeness | BC-5.03.002:71-72; legacy dgx_statusline.py:902-903 | Inv 2's "uses served" lists the prefix strip at SL:444-445 but omits its sibling, the subagent strip at SL:902-903. BC-2.01.001/002 cite both. | product-owner |
| ADV-P13-D13 | LOW | Namespace/range inconsistency (pending intent verification) [owner-question] | BC-2.01.004:289-292 vs :165, :282-284 | PC-13 says every label word is a `statusline.labels.*` key and the registry carries "exactly these nine members", with a width 1..16 range. `labels.input`, `labels.vllm_down` and `labels.lmcache_down` sit in the same namespace without the width bound. | product-owner |
| ADV-P13-D14 | LOW | Untestable invariant | BC-5.01.007:138-141 | Inv 3 requires a/b vs c/d cross-multiplication, but no `Num` kind is rational and no helper compares quotients. No test can be derived from it. | product-owner |
| ADV-P13-D15 | LOW | Machinery gap | BC-6.02.001:77-82 vs BC-6.03.004:78, PC-1 | `captures/exclusions.json` uses "the SAME closed-set machinery". BC-6.03.004 resolves `case` relative to the committed corpus root, so the case-existence check is undefined for capture cases. | product-owner |

### 2. Policy compliance
- P1 append_only_numbering: PASS. CP-T08 retired and CP-T09 appended; no renumbering seen.
- P2 lift_invariants_to_bcs: PASS on the sample (DI-008, DI-010, DI-012 cited).
- P4 semantic_anchoring_integrity: FINDING D04, D05, D12.
- P5 creators_justify_anchors: PASS.
- P6 subsystem name: PASS (SS-02..SS-06 frontmatter).
- P7 H1 = BC-INDEX: PASS on a 7-BC sample (2.02.002, 3.01.001, 5.01.003, 5.04.002, 6.01.002, 6.04.001, 6.04.002). PRD titles not checked.
- P12 settled_decisions: PASS. D13 is raised as an owner-question.
- P13 parity_before_behavior_change: PASS.
- P14 public_repo_hygiene: PASS. Only RFC 5737 placeholders in the perimeter.
- P16 thresholds_are_explained: PASS.
- P18 cross_platform_from_day_one: FINDING D01, D02, D05, D06.
- P19 go_hardening_toolchain: PASS (BC-6.04.001 PC-3, vet/staticcheck/govulncheck).
- P20 config_over_code: PASS. `window_age.max_depth` is a registry key; harness hooks are reserved names.
- P21 public_artifact_hygiene: PASS.
- P11 (CI positive coverage; applies because BC-6.01.003 is a CI gate): FINDING D02.
- P3, P8, P9, P10, P15, P17: N.A.

### 3. Not fully read; claims not verified
- **Not read:**
  - BC-2.02.004, BC-2.02.006, BC-3.02.002.
  - The BC-2.03.001 header (lines 1-39).
  - prd.md, prd-supplements/* (interface-definitions grep only), ARCH-01..06.
  - VP files (grep only), capabilities.md, invariants.md, BC-ALLOCATION.md.
- **Python and runtime claims not verified:**
  - `RoundN(1.00005, 4) = 1.0001`.
  - Whether int() counts leading zeros toward the 4,300-digit limit (EC-006, `"0"`×4,301).
  - The mix-cache save budget of 994 (the exception to 995 − s).
  - The canary's ns round-trip value `…4245195`.
  - The 10,893 tz goldens.
  - The MSVC parse of `TZ=UTC`.
  - Windows CreateProcess search order for `ps` under an empty PATH (system dirs, then the application dir).
  - D01/D02 rest on the documented CPython Windows stdio default (`newline=None`, so `\n` becomes CRLF) and on BC-6.03.002 EC-006. I did not run them.

### 4. Novelty
Novelty: MEDIUM. D01, D02, D03 and D04 are residue from pass-11/12 remediation that did not reach every file. D05 is a Windows contradiction that has gone unnoticed in earlier passes. D06 through D09 are substantive new gaps.

NOT_CONVERGED
