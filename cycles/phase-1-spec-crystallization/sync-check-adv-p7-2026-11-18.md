---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass-with-findings"
producer: consistency-validator
timestamp: 2026-11-18T23:30:00Z
phase: 1
inputs: [specs/behavioral-contracts/, specs/verification-properties/, specs/architecture/, specs/domain-spec/, specs/prd-supplements/, specs/prd.md, specs/product-brief.md, specs/cicd-setup.md, specs/dtu-assessment.md, specs/owner-decisions-log-2026-11-14.md, cycles/phase-1-spec-crystallization/pass-7-remediation-plan.md, adversarial-reviews/ADV-P7-INDEX.md]
input-hash: "5777eb0"
traces_to: ../../STATE.md
---

# Consistency Validation Report: hylo pass-7 fix-burst sync check

## Report Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo (status line + hybrid routing, P1 spec crystallization) |
| **Generated** | 2026-11-18T23:30:00Z |
| **Generator** | consistency-validator (fresh context; scripted sweeps under `/opt/homebrew/anaconda3/bin/python3 -I` 3.11.7 plus targeted file reads) |
| **Artifacts Scanned** | 102 dirty spec files vs `HEAD`; 244 spec `.md` files (behavioral-contracts 156 incl. allocation/index, verification-properties 42 incl. index, architecture 10, domain-spec 9, prd-supplements 7, root 7+1) |

**Scope note.** Fresh-context post-remediation sync check for adversarial pass 7, before
the pass-8 decision. Inputs: `adversarial-reviews/pass-7.md` (114 verbatim findings:
HIGH 14 / MEDIUM 47 / LOW 49 / COSMETIC 4), `adversarial-reviews/ADV-P7-INDEX.md`,
and the rulings/calls in `pass-7-remediation-plan.md` (OD-188..OD-192; calls 1-15).
Rulings verified in `specs/owner-decisions-log-2026-11-14.md` (next free OD-193) and,
per instructions, spot-verified **on disk in the current working tree**, not from
history lines. Read-only on specs; nothing committed. Findings continue the sync-check
numbering lineage (SC-01..28 consumed by passes 3-6).

## Headline result

**All 114 pass-7 findings verified CLOSED on disk (0 OPEN).** OD-188..OD-192 are
logged and propagated. 9 of the 11 orchestrator-declared checks pass clean; check 6
passes with a wording note and check 9 with one new minor residue (SC-29). Three new
sync-check findings are recorded (SC-29, SC-30, SC-31 — none blocking). Validation
gate: **PASS-WITH-FINDINGS**.

## 1. Finding disposition (114/114 CLOSED)

Perimeter A — A01 ARCH-07:70 (allowlists copied verbatim from BC-6.01.002); A02
BC-6.04.002:98 + ARCH-08:99 + prd.md:483 (NFR-001) + nfr-catalog.md:27; A03
ARCH-05:33 (`LocalZone(env EnvVars) (*time.Location, error)`, `CacheDir(env)`,
`HomeDir(env)`) + ARCH-01:30 (envOS wiring withdrawn) + BC-6.01.002:130 (`EnvVars`
seam replaces `Env.Getenv`/`Home`); A04 interface-definitions.md:201 (defaults =
single accepted spelling; render-vs-registered distinction); A05 BC-2.01.005:31
(`HYLO_STATUSLINE_UNITS_*`/`_LIMITS_WINDOWS` spellings); A06 interface-definitions.md:281
(mirrored floor −9223372036.854775); A07 cicd-setup.md:58 (coverage its own job,
`-coverpkg=./internal/...`); A08 ARCH-08:60 (supersession of the Tier-A-in-plain-test
rationale); A09 ARCH-08:89 (`internal/parity` joins the gate); A10 ARCH-05:31
(`envfold_posix.go`/`envfold_nt.go` naming rule); A11 ARCH-03:205 (crypto/tls, SNI,
ALPN http/1.1, Linux system roots, raw-`net.Listener` seam); A12 BC-COMPONENT-MAP:57;
A13 error-taxonomy:85 (`ascending pair violated (p75 <= p95)`); A14 error-taxonomy:47
(CP-N03 carriers BC-1.04.001/.004/.005, agreeing with ARCH-03:106 and test-vectors:45);
A15 prd.md:629 (ASM-002 mint-time wording, 2.1.326/ASM-007 split); A16 error-taxonomy:16
(OD-184 code-point reasons); A17 ARCH-09:25 (D14-(b) precedent respelled to raw
net.Conn); A18 ARCH-08:121 (host-OS golden census); A19 ARCH-04:75 (retry count is a
registry key); A20 ARCH-08:151 (timing census vs corpus); A21 interface-definitions.md:251
(`timeout_s <= 25` + rationale); A22 assumptions-register:31 (ASM-007 before Phase 2
S1.07 stories).

Perimeter A2 — A2-01 capabilities.md:29 (widgets attributed to the CAP-009 path);
A2-02 VP-012:13 (`bcs:` reciprocity: +BC-1.04.001, +BC-1.04.002, +BC-1.06.001); A2-03
VP-012:85 (register copied exactly; temp-file back to ONE riding test); A2-04 VP-012:71
(rider-complete closure check + non-empty mutant-catalogue guard); A2-05 VP-014:22 +
dtu-assessment:14 (`TestWindowAge_D4EX1_Windows_AncestorFound`); A2-06 VP-031:22
(config keys named; default-vs-non-default stated); A2-07 VP-018:50 (count is config;
parity-visibility reason inverted); A2-08 VP-018:23 (`<basename>.XXXXXXXX` mkstemp
pattern, no `.tmp`); A2-09 VP-016:22 (`TestTheme_RejectionLines`); A2-10 VP-007:22
(fresh-copy second render); A2-11 VP-041:22 (P-b differential half to Tier C); A2-12
VP-009:22 (module-root captures resolution + `CompareNamedCaches`); A2-13 VP-001:22
(zero-task subagent output legality); A2-14 VP-021:102 (filtered-population quantifier,
cold-start table leg); A2-15 VP-017:22; A2-16 VP-015:77; A2-17 VP-022:22 (dangling
pointer removed; "no metrics cache" noun fix); A2-18 VP-036:47 (100 ms ceiling);
A2-19 VP-009:23 (OD-190 LF normalization named); A2-20 VP-037:22 (`CGO_ENABLED=1` race
legs); A2-21 VP-006:13 (bcs membership all named in body); A2-22 dtu-assessment:35
(child-process wording).

Perimeter B — B01 BC-1.01.003:34 + BC-1.01.007:34 (H1s state the `rows > 2` override;
BC-INDEX:69/73 and prd.md:157/161 rows synced; `statusline.rows` registry note
interface-definitions.md:192); B02 BC-1.01.009:95; B03 BC-1.01.009:63 (step-2 CP-T09
cell) + BC-1.01.001:60 (PC3); B04 BC-1.01.001:60; B05 BC-2.01.004:196; B06
BC-1.02.030:54; B07 BC-1.02.004:51 (cwd via `Env.Cwd`); B08 BC-1.01.009:30 (footnote
marker retired); B09 BC-1.01.001:29 (`TestCPX03_WriteFailureExit0`); B10
interface-definitions.md:202 (+BC-1.02.018/BC-1.02.011/BC-1.02.016+.027 rows); B11
error-taxonomy:47; B12 BC-1.02.019:25 (and .020/.022/.024/.026/.030 — version-prefixed
histories verified); B13 BC-1.02.008:96 + BC-1.02.014 (rows kept on VP-028 as declared
bounded golden sweeps with the VP-041 scope split stated); B14 BC-1.01.009:115; B15
BC-1.02.017:26.

Perimeter C — C01 BC-1.06.001:122 (EC-011) + BC-1.03.001:77 (EC-009), ruling reproduced
(call 1, no exclusion, per-site outcomes pinned); C02 BC-1.07.004:22 (PC3 `\b`/`\f`);
C03 BC-1.03.010:125 (default separators; 420 B = 100+160+160); C04 BC-1.07.007:107
(EC-010/EC-011 oracle-pinned); C05 BC-1.06.001:140 (VP-012 row + anchor, SC-21
reciprocity); C06 BC-1.07.001:80; C07 BC-1.03.007:106 (self-consistent seed); C08
BC-1.03.006:114 (A-template located + self-contained copy); C09 BC-1.06.001:80 (mode
0600 POSIX-qualified, Windows 0666/0444); C10 interface-definitions.md:181 (S1.07
consumer cells completed; `pill.label_local` lists BC-1.07.006 but not BC-1.07.007,
matching that BC's actual consumption); C11 BC-1.07.005:22 (`name_fallback` key,
OD-189); C12 BC-1.07.008:112 (promise respelled to the actual ladder); C13 prd.md:645
(`BC-1.07.002 PC-1`); C14 BC-1.07.007:55 (+ the .004/.005/.006/.008 garble fixes).

Perimeter C2 — C2-01 BC-1.04.001:81 (http.client framing ladder, oracle-measured);
C2-02 BC-1.04.001:71 (`lstrip(' \t')` then `rstrip('\r\n')`); C2-03 BC-1.04.001:281 +
BC-1.04.002:122 + VP-INDEX:92 (VP-012 rows and map rows reciprocated); C2-04
BC-1.04.001:58 (client speaks https; parity corpus plain http only); C2-05 VP-030:76
(raw `net.Listener` fake); C2-06 BC-1.04.002:77 (sites corrected: `_norm_pt` SL:655,
TypeError trio SL:324/325/336); C2-07 BC-1.04.004:46 + BC-1.04.005:21 (OD-189 label
keys); C2-08 BC-1.04.001:131 (fragment dropped from the request line); C2-09
BC-1.04.001:292 (ARCH-03 §Interfaces anchor refreshed); C2-10 BC-1.05.005:29
(2**1024 − 2**970); C2-11 BC-1.04.021:78 (monotonic-clock precondition); C2-12
ARCH-03:106 (insertion order); C2-13 error-taxonomy:52 (KEEP_DEAD dead rung, BC-1.04.002
cited); C2-14 test-vectors:45 (vector locator note).

Perimeter D — D01 BC-2.01.005:31 (PC-7 canonized, call 5); D02 BC-2.02.001:127 (pass-6
strings homed; `control character` mapped to Text for non-theme free text); D03
BC-2.02.001:33 ("Numeric-range failures by type", total mapping); D04 BC-6.01.001:83
(PC-4 ONE end-to-end definition); D05 BC-6.01.002:97 (PC-1 authoritative exact key
sets); D06 BC-5.04.001:49 (every-probe domain rule) + ARCH-06:33 + BC-6.04.003:33 +
BC-5.04.002:45; D07 BC-5.04.001:61 (caller owns the non-str check; `(float64, error)`
canon); D08 BC-2.01.001:69 (empty-Text keyed to registered range); D09 BC-2.01.004:75
(`FloatQuad` fixed length 4); D10 BC-2.01.002:93 (structural ordering; `<value>`
provenance); D11 BC-2.02.002:39 (H1 admits the `git.ttl_s` exception); D12
BC-3.01.001:50 (`HomeDir(env EnvVars)`); D13 BC-2.01.004:252 (product consumer
retargeted to BC-1.06.001); D14 BC-6.01.001:110 + ARCH-07:166 + BC-6.02.003 + BC-6.03.001
(subagent case-id family rule); D15 BC-6.03.004:36 (exhaustive union incl. `2_0`, `٢`,
range-misses, `-inf`); D16 BC-6.04.003:33 (OD-166 + D4-EX-2 extension; Inv 3 restated);
D17 BC-6.02.003:217 (stale note closed; SL:89; `empty` leg added); D18 BC-2.01.004:135
(SL:906-907); D19 BC-5.01.007:107; D20 BC-5.04.002:64; D21 BC-2.01.004:212 +
BC-5.03.001:56 + ARCH-06:153 (`ValidationWidth`, render/validation split); D22
ARCH-06:153 (NumLT..NumNE); D23 BC-2.02.005:75; D24 BC-6.03.002:70 (pinned non-zero
oracle-exit exception); D25 BC-2.01.002:55 (`<FIELD>` well-formedness); D26
BC-6.04.002:72 (20-runs rationale); D27 BC-2.03.002:29 + BC-4.01.001:25.

## 2. OD-188..OD-192 propagation (task check 2)

| Ruling | Log | Registry/signature | Consumers |
|---|---|---|---|
| OD-188 `statusline.cache.rename_retry_limit` (Int, default 2, 0..10; attempts = 1 + limit) | owner-decisions-log (pass-7 block) | BC-2.01.004:234 (PC-11) | interface-definitions.md:199, ARCH-04:66-78, VP-018:50, BC-6.03.003:62/EC-004, BC-1.06.001 EC-009 — attempt count "1 + limit" stated identically at every site |
| OD-189 dead marker + labels | owner-decisions-log | BC-2.01.004 PC-12 (PC-12, entry 12) | interface-definitions (`statusline.labels.vllm_down`/`lmcache_down`, `statusline.subagent.name_fallback`), BC-1.04.004:46, BC-1.04.005:21, BC-1.07.005:22, E-NET-001 (error-taxonomy:52, prd) |
| OD-190 LF on every OS | owner-decisions-log | BC-6.01.002:126-131, ARCH-07:88-96, VP-034, VP-009, invariants.md (DI-012 note), ubiquitous-language.md | BC-1.07.004:64-68 (PC5); BC-1.01.008 untouched (encoding-scoped, correct) |
| OD-191 100 ms ceiling | owner-decisions-log | BC-6.04.002:98-114 | ARCH-08:99-104, nfr-catalog.md:27, prd.md:483 (NFR-001), VP-036:47, product-brief:89 |
| OD-192 ASM-007 before S1.07 stories | owner-decisions-log | assumptions-register:31 (v1.3.2) | prd.md §9 (A22), next-free-OD-193 noted |

All five propagated consistently; no contradicting wording found anywhere in the tree.

## 3. Burst-sync check matrix (11/11 executed)

| # | Check (orchestrator wording) | Result |
|---|------------------------------|--------|
| 1 | Every finding CLOSED/OPEN | PASS — 114/114 CLOSED (table above); no finding relied on history lines; every fix verified in current content |
| 2 | OD-188..192 propagated | PASS (section 2) |
| 3 | Crash register = 48 (X4 S17 T8 N3 O11 A5); CP-T09 named at register/T-family sites; CP-T08 retired-only | PASS — error-taxonomy:21-23 ("48"; "4 + 17 + 8 + 3 + 11 + 5"; "T family counts 8"; "CP-T08 is a RETIRED id"); CP-T09 named in ARCH-03, BC-1.01.001, BC-1.01.009, BC-1.03.018, BC-5.04.001, BC-6.04.003, test-vectors, prd E-REN-002; every live CP-T08 occurrence is retired-marked (BC-1.03.018 occurrences are provenance history or "CP-T08 retired"); ARCH-06 carries the corrected domain statement without the id (acceptable — ARCH-06 does not host the register) |
| 4 | Reason-vocabulary byte identity BC-2.02.001 ↔ error-taxonomy.md | PASS — all 14 vocabulary strings verified byte-identical in both (incl. `ascending pair violated (k_from <= m_from)`, `ascending pair violated (p75 <= p95)`, `expected non-empty control-free text in every entry`, `expected exactly 1/8 code points`, the four number-range strings, the three URL strings); class attributions agree; presentation differs only in row grouping (BC-2.02.001 one row per string; taxonomy groups siblings) which is not a byte difference in the strings |
| 5 | Oracle env allowlists identical (BC-6.01.002 ↔ ARCH-07 ↔ VP-034) | PASS — POSIX/Windows × oracle/Go key sets, conditional `PATH`/`COLUMNS`/setting keys, `HOME`+`USERPROFILE` both OSes, `HOMEDRIVE`/`HOMEPATH` withdrawn everywhere (incl. VP-034's arrays), `PYTHONIOENCODING=utf-8`, OD-190 LF note — verbatim copy in all three (BC-6.01.002:97-131, ARCH-07:70-96, VP-034:24-90) |
| 6 | Self-check constants identical (BC-6.01.001 ↔ VP-006 ↔ ARCH-07) | PASS with note — BC-6.01.001:83-100 and VP-006 state the identical quartet (decode 993/994; save 991 writes/992 skips; wire 991 renders; unidata 14.0.0) with the ONE end-to-end definition; ARCH-07:59-64 describes the same fail-closed self-check measure-set but pins no numerals (no conflict; see SC-31) |
| 7 | Exclusion register (12 ids) BC-6.03.004 ↔ VP-012 + rider per id | PASS — 12-id sets equal; every register row complete; rider/citation attributions agree in both directions (OD-159 rider = BC-1.02.004 `TestGitTextReads_OD159_StrictUTF8` after the v1.17 correction, both sides; OD-160 = BC-1.02.017 EC-010 + BC-1.01.008 EC-011 + dedicated BC-1.05.004 test; temp-file = the register's ONE test; cp-x03 = `TestCPX03_WriteFailureExit0`, "provisional" settled both sides); VP-012's closure check additionally requires a rider test for every closed id (OD-181, Text) and guards an empty mutant catalogue |
| 8 | Metrics-client (call 9) consistency | PASS — framing ladder, header rule, fragment drop, https-over-`crypto/tls` with plain-http parity corpus, raw-`net.Listener` seam: ARCH-03:184-210, BC-1.04.001 (PC1/PC2/VP rows), BC-1.04.002 (sites), BC-1.04.004/.005 (labels), VP-030 (transport table), VP-012 (OD-181 rider) agree point for point |
| 9 | Titles; counts 154/41; VP `bcs:` bijection | PASS with SC-29 — 154 BC files = 154 BC-INDEX rows = 154 PRD rows; title triple-equality 154/154 (escape-aware, incl. the BC-1.02.003/BC-2.02.006 `\|` cells) and BC-ALLOCATION main-section titles equal; 41 VP files = 41 catalog rows; 259 directed `bcs:` edges (exactly VP-INDEX v1.16's claim), 0 forward-only beyond the 6 enumerated residues + 4 new provenance mentions (SC-29); VP-INDEX coverage map = union of `bcs:` sets exactly (0 diffs) |
| 10 | Frontmatter: one `version`, one `modified`, no duplicate keys (changed files) | PASS — 0 duplicate keys; exactly one `version` and at most one `modified`/`timestamp` per changed file; the rulings log carries no frontmatter (established design, unchanged) |
| 11 | Hygiene on the diff (added lines) | PASS — no `/Users/` paths; no non-192.0.2.x/127.x IPv4; no emails; no session links; no CR line endings; sole ≥U+2600 character is U+2714 (the legacy-rendered `✔` test byte in a BC-1.07.007 golden — parity test data, not an emoji); the only non-ASCII script characters are the Arabic-Indic `٤`/`٢` numeral vectors that finding D15's fix was required to name |

## 3a. New sync-check findings

| SC-NN | Severity | File:line | Inconsistency | Owner |
|-------|----------|-----------|---------------|-------|
| SC-29 | Minor | `specs/verification-properties/VP-INDEX.md:22-34` (Uncovered BCs prose) | The residual prose still claims "257 directed VP→BC `bcs:` edges … re-machine-checked 2026-11-19T16:00:00Z" while v1.16's own modified entry and the tree state 259 (VP-012's `bcs:` gained BC-1.04.001 and BC-1.04.002 after the 16:00 machine check). Additionally, four NEW BC-body→VP prose mentions are unenumerated against the "the lists are therefore exactly the residue" claim: BC-1.02.008:96 and BC-1.02.014 → VP-041 ("per the VP-041 scope split", added by the B13 fix), BC-1.02.017 → VP-012 ("VP-012 concrete name", B15 fix), BC-6.01.001 → VP-006 ("state these same constants", D04 fix). All four are provenance/contrast mentions, not property routings — but the standing convention (SC-13/SC-14/SC-21) is reciprocity or enumeration. Remedy: refresh the counts to 259 and the date; either add BC-6.01.001 to VP-006 `bcs:` (and BC-1.02.017 to VP-012 `bcs:`) or enumerate the four pairs beside the existing design-reference exclusions. | architect |
| SC-30 | Minor | `specs/verification-properties/VP-011-tier-c-differential-fuzz.md:22` | Live recount says "47 catalogued crash paths (CP-X01..X04, CP-S01..S17, …)" — the register is 48 since pass-7 call 8 (CP-T09 minted; CP-T08 retired; T family 8). VP-011 was not on call 8's propagation list. Remedy: recount to 48, add CP-T09 to the family enumeration, drop CP-T08. | architect |
| SC-31 | Cosmetic | `specs/behavioral-contracts/ss-01/BC-1.07.008.md:123`; `specs/architecture/ARCH-07-parity-harness.md:59-64` | (a) BC-1.07.008's provenance cell still reads "crash register count 47 total, ADV-P6-C07" — accurate as pass-6 history, easily misread as a live count at the next adversarial read. (b) ARCH-07's oracle self-check paragraph names the measure-set (JSON depth boundaries, `unicodedata.unidata_version`, fail-closed) without pinning the numerals BC-6.01.001:99-100 attributes to it ("VP-006 and ARCH-07 state these same constants") — no contradiction exists; the sentence is just looser than the claim. Remedy: count wording touch on the next edit of each file. | product-owner / architect |

### Critical
None.

### Major
None.

### Minor
SC-29, SC-30.

### Cosmetic
SC-31.

## Validation Gate Result

**PASS-WITH-FINDINGS** — no blocking findings. The pass-7 remediation burst is fully
propagated on disk: every one of the 114 findings verified closed at its cited locus,
the five rulings land consistently at every site the remediation plan names, and the
machine-checked invariants (154/154/154 title triple-equality, 259-edge bijection with
an exact VP-INDEX map, byte-identical vocabularies, three-way allowlist identity,
12-id rider register agreement, frontmatter and hygiene cleanliness) all hold. SC-29
and SC-30 are two-file, few-line prose repairs (index-prose counts and one stale
recount) that can ride the next wording touch or the pre-pass-8 preparation burst;
per OD-176 they must be fixed before convergence is claimed, but nothing here blocks
dispatching pass 8.

## Overall Metrics

| Metric | Value |
|--------|-------|
| **Pass-7 findings verified closed** | 114/114 (HIGH 14, MEDIUM 47, LOW 49, COSMETIC 4) |
| **Open** | 0 |
| **New sync-check findings** | 3 (SC-29 Minor, SC-30 Minor, SC-31 Cosmetic) |
| **Machine checks** | 86 scripted assertions, all adjudicated; 244 spec files swept (digest `0dff13d`) |

Compared with pass 6, the residue improved in kind and volume: pass 6 left 8 sync
findings (3 Major), this burst leaves 3 (0 Major). The sync surface is entirely in
prose counts and unenumerated provenance mentions — the natural wake of a 102-file
burst — with the structural weaves (title equality, VP bijection, allowance/vocabulary
identity, register riders) clean.

## Appendix: Validation Methodology

Fresh-context scripted sweep of the factory worktree's uncommitted spec tree
(`git diff HEAD`, 102 files, +1559/−798). Interpreter `/opt/homebrew/anaconda3/bin/python3
-I` (CPython 3.11.7). Scripts (scratchpad, not committed): (1) full added-line review per
file for finding-by-finding adjudication against `ADV-P7-INDEX.md` and the remediation
plan's rulings/calls; (2) cross-file equality batteries — vocabulary strings
(BC-2.02.001 ↔ error-taxonomy), allowlists (BC-6.01.002 ↔ ARCH-07 ↔ VP-034 incl.
HOMEDRIVE/HOMEPATH withdrawal and conditional keys), self-check quartet
(BC-6.01.001 ↔ VP-006 ↔ ARCH-07), 12-id exclusion register rows and rider mappings
(BC-6.03.004 ↔ VP-012), CP-T09/CP-T08 contexts, register-count arithmetic; (3) title
triple-equality across 154 H1s, BC-INDEX and PRD rows with escape-aware pipe-table
parsing; (4) VP `bcs:` bi-directional edge extraction (259 edges), VP-INDEX
coverage-map union regeneration (0 diffs) and forward/reverse residue classification;
(5) frontmatter duplicate-key/version/modified scans over all changed files; (6)
hygiene regexes over added lines (absolute paths, IPs, emails, session links, emoji,
block-script prose, CR endings). Manual reads adjudicated every scripted anomaly;
six initially-unresolved citations were re-anchored (regex word-splitting artifacts,
not missing fixes). Nothing outside the report path was written.
