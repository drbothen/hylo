---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass"
producer: consistency-validator
timestamp: 2026-11-18T23:30:00Z
phase: 1
input-hash: "8adf7cb"
inputs: [specs/behavioral-contracts/, specs/verification-properties/, specs/architecture/, specs/prd-supplements/, specs/prd.md, specs/cicd-setup.md, adversarial-reviews/pass-10.md, adversarial-reviews/ADV-P10-INDEX.md, pass-10-remediation-plan.md]
traces_to: ../../STATE.md
---

# Consistency Validation Report: hylo pass-10 fix-burst sync check

## Report Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo (status line + hybrid routing, P1 spec crystallization) |
| **Generated** | 2026-11-18T23:30:00Z |
| **Generator** | consistency-validator (fresh context; scripted sweeps under CPython 3.11.7 plus targeted file reads) |
| **Artifacts Scanned** | 88 dirty spec files vs `HEAD` (+1016/−533); 239 spec `.md` files swept |

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | L2 to L3 Requirement Coverage | pass (call 17 reason vocabulary synced to every named surface; call 1-2 contradictions resolved across BC-6.x, ARCH-07, VP-034) |
| 2 | L3 to L4 Verification Property Coverage | pass (283-edge union bijection; check 8) |
| 3 | Dependency Acyclicity | N.A. at Phase 1 — no story graph yet; ID minting append-only (nothing retired or reused this pass) |
| 4 | Architecture Alignment | pass (LoadOptions declared with the EnvVars seam: A11; RoundN re-signed Num: D05/call 5; DBig minted: A12; mix-loop owner BC-1.03.021 by ID everywhere: A10/C07) |
| 5 | Acceptance Criteria Quality | pass at spec stage (sanitization-before-guard reorder: C2-01; crash-list completion: C2-02; default-layer value rule: D06/call 6) |
| 6 | Story Sizing (all <= 13 points) | N.A. — Phase 1 precedes story decomposition |
| 7 | Priority Consistency | N.A. at story level; PRD priorities unchanged by the burst |
| 8 | L1 to L2 to L3 to L4 Chain Completeness | pass (no orphans introduced; 283-edge recount clean; title quadruple 154/154) |
| 9 | AC Completeness Coverage | pass at spec stage (B03/C2-11 VP-row and `bcs:` reciprocity restored; A2-06/A2-10 closure honesty; D04 every-sid seeding) |
| 10 | ASM/R Traceability | pass (no ASM/R regressions; A08 R-004 census line corrected to the parity detector) |

Detail for every row: the numbered sections below and the "Burst-sync check
matrix". Story-graph rows (3, 6, 7) are explicitly out of scope for a Phase 1
spec-crystallization artifact and are marked N.A. rather than assumed.

**Scope note.** Fresh-context post-remediation sync check for adversarial pass 10,
before the pass-11 decision. Inputs: `adversarial-reviews/pass-10.md` (69 verbatim
findings: HIGH 8 / MEDIUM 33 / LOW 23 / COSMETIC 5), `adversarial-reviews/ADV-P10-INDEX.md`,
and the calls in `pass-10-remediation-plan.md` (calls 1-18; no owner rulings this pass;
next free OD-194). Every disposition is spot-verified **on disk in the current working
tree**, not from history lines. Read-only on specs; nothing committed. Findings
continue the sync-check numbering lineage (SC-01..34 consumed by passes 3-9). 
Repo-relative paths throughout.

## Headline result

**69 of 69 pass-10 findings verified CLOSED on disk; 0 REJECTED; 0 OPEN.** All ten
orchestrator calls with cross-file statements (1-5, 9-14) land identically at every
carrier. The new pass rule (no line-number pointers into BC or ARCH files outside
provenance) is honored: one live ARCH line pointer survives in a sketch comment
(SC-35, pre-existing, Minor). The last unqualified constant-size claim of the mix
re-read saga survives at one sibling site (SC-36, Minor). Validation gate: **PASS**.

## 1. Finding disposition (69 CLOSED / 0 REJECTED / 0 OPEN)

Perimeter A — A01 `specs/cicd-setup.md:88` (coverage row prints the G-of-3 line and
compares against the committed package manifest, census per ADV-P10-A04) + `:164`;
A02 `specs/cicd-setup.md:58` (coverage job 30 min) + `:161` (lag note 4 says
30-minute, matching the test-job floor); A03 `specs/cicd-setup.md:135-155` (scheduled
nightly + manual-dispatch job on `main` checks out the `factory-artifacts` ref and
runs the category scan over it; the impossible push trigger is documented as
impossible) + `specs/prd-supplements/nfr-catalog.md:29` (NFR-006 target restated) +
`specs/prd.md:27` (changelog 0.2.21); A04 `specs/cicd-setup.md:80-81,87` +
`specs/architecture/ARCH-08-build-ci-release.md:145,153,203` (Tier A/B and timing
compare runtime counts against committed manifests as well as censuses); A05
`specs/cicd-setup.md:85` + `specs/architecture/ARCH-08-build-ci-release.md:180,183`
(gitleaks compares N with the fetched-commit count over both refs, fetch-depth 0);
A06 `specs/architecture/ARCH-08-build-ci-release.md:105-106,185-189` (G compared with
the committed package manifest; a renamed/moved gated package fails the job; the
zero-gated-packages allowance scoped to before any `internal/` package exists);
A07 `specs/prd-supplements/error-taxonomy.md:102` (reason minted in the table,
E-CFG-001 reconciliation sentence) + `specs/behavioral-contracts/ss-02/BC-2.02.001.md:140`
(exact-strings table row); A08 `specs/prd-supplements/risk-register.md:29` (R-004
mitigation cites the parity census line, timing line no longer named); A09
`specs/prd-supplements/nfr-catalog.md:63-65` ("the other P1 exit conditions are two",
OD-149 nightly Tier C condition stated beside the coverage gate); A10
`specs/architecture/ARCH-03-statusline.md:195-196` + `specs/architecture/ARCH-06-pyfmt.md:96-97`
(both name BC-1.03.021 as the owner of the re-read loop and disclaim ownership);
A11 `specs/architecture/ARCH-02-configuration.md:98-102` (`LoadOptions` declared with
the `EnvVars` field and the reserved `FileLayer`, beside the `Load` signature);
A12 `specs/architecture/ARCH-06-pyfmt.md:156,287` (`DBig(n *big.Int, width int,
zeroPad bool) string` serving the beyond-int64 `{pct:>2d}` site) +
`specs/behavioral-contracts/ss-05/BC-5.01.004.md:78`; A13
`specs/prd-supplements/module-criticality.md:75-77` (derivation note: VP-038 counted
via its source_bc, primary-home cell keeps the pyfmt spelling); A14
`specs/prd-supplements/error-taxonomy.md:106` ("exactly the six strings above");
A15 `specs/prd-supplements/error-taxonomy.md` (minting-source note removed; grep for
both stale phrases now returns no live hit) +
`specs/prd-supplements/interface-definitions.md:18,204` (not-yet-on-disk note dropped,
mirror asserted); A16 `specs/architecture/ARCH-06-pyfmt.md:185-186` (the Decode
comment lists all five depth constants incl. the metrics-reply one); A17
`specs/prd-supplements/interface-definitions.md:38` (config-path-only flag note).

Perimeter A2 — A2-01 `specs/verification-properties/VP-004-closed-exit-code-surface.md:38-43,60-65,86-87,140-143`
(output set = zero or more NDJSON lines OR the 29-byte degraded line on a catalogued
renderer fault; fuzz oracle updated) + `specs/behavioral-contracts/ss-04/BC-4.01.001.md:109`
+ `specs/behavioral-contracts/ss-01/BC-1.07.001.md:111` (both VP rows state the full
set); A2-02 `specs/verification-properties/VP-001-never-blank-exit0.md:160-165` +
`specs/verification-properties/VP-005-stdin-decode-totality.md:47-49,109-110` (both
classifiers pinned to ModeText semantics with the 993 subagent-stdin budget; BOM,
UTF-16/32 and depth-994 stdin decode to empty and print zero bytes); A2-03
`specs/verification-properties/VP-028-row1-widget-tables.md:37-42` (a prefix miss
renders the cloud pill; the tag drops only on an empty prefix list; BC-1.07.006
cited); A2-04 `specs/verification-properties/VP-INDEX.md:84` (VP-008 catalog title
carries the ruled-PC2-exceptions qualifier, changelog :35); A2-05
`specs/verification-properties/VP-006-json-depth-budgets.md:94-111,125,160-164`
(call-site lint added as a Go leg; detection limits stated honestly — the pin proves
symbol values, the lint proves each site passes its own constant, the self-check runs
on the oracle); A2-06 `specs/verification-properties/VP-012-exclusion-set-closure.md:74-81,162-164`
(scope review stated as a manual obligation with the precise predicate argument) ;
A2-07 `specs/verification-properties/VP-014-d4ex1-windows-window-age.md:41-46,62-63`
(expected bytes pointed at the BC-3.02.001 / BC-1.02.017 vector tables; the
macOS/Linux bound given legs via VP-009/VP-033); A2-08
`specs/verification-properties/VP-001-never-blank-exit0.md:52-56` (claim scoped to
the main entry; CP-X01..X04 disposal cited from the register); A2-09
`specs/verification-properties/VP-022-ledger-read-scope-absence.md:55-56,92` (absence
claim qualified: except the stdin-designated transcript path; DI-007 intent stated);
A2-10 `specs/verification-properties/VP-012-exclusion-set-closure.md:209` (sketch
asserts register keys equal the closed twelve-id set).

Perimeter B — B01 `specs/behavioral-contracts/ss-01/BC-1.01.008.md:78-81` (Inv 3
restated to renderer-emits-no-CR with the BC-1.01.003 PC5 verbatim-text carve-out and
the do-not-strip instruction); B02 `specs/behavioral-contracts/ss-01/BC-1.02.004.md:101-107`
(chunk pinned at the measured 8192 bytes, independent of block size, boundary probes
at 8191/8192; the 4096-prefetch note removed) + `:91-94` (stat semantics, B06);
B03 seven BC VP-table rows plus the VP-001 `bcs:` repair —
`specs/behavioral-contracts/ss-01/BC-1.02.006.md:141`, `BC-1.02.011.md:89`,
`BC-1.02.012.md:91`, `BC-1.02.014.md:104`, `BC-1.02.017.md:93`, `BC-1.02.020.md`
(degrade rows), `BC-1.02.029.md:87`, and
`specs/verification-properties/VP-001-never-blank-exit0.md` (frontmatter lists all
seven; the BC-edge union check confirms reciprocity); B04
`specs/behavioral-contracts/ss-01/BC-1.01.005.md:58-61` (clamp-equivalence claim
withdrawn; sign-preserving big-int comparison required with the MinInt64
counter-example); B05 `specs/behavioral-contracts/ss-01/BC-1.01.009.md:82,98` (within-step
ordering made site-dependent; the record-cost throttle-check site precedes the write)
+ `specs/prd-supplements/error-taxonomy.md:175` (CP-O10 row carries both bearer
sites); B06 see B02; B07 `specs/behavioral-contracts/ss-01/BC-1.02.016.md:134` through
`BC-1.02.030.md` (all fifteen gain the file-family fragment anchor and the TBD
Stories convention; scripted sweep 15/15).

Perimeter C — C01 `specs/behavioral-contracts/ss-01/BC-1.03.007.md:78,98-109,117-118,125,150`
(mirror leg stated and reachable vector canonical under D4-EX-2; int-tin/float-pp
seed labelled a foreign-cache state per OD-160 in body, VP rows and Traceability);
C02 `specs/behavioral-contracts/ss-01/BC-1.03.010.md:113` +
`BC-1.03.017.md:54,84` (predicates cited by BC id plus PC/row number, never line
numbers); C03 `specs/behavioral-contracts/ss-01/BC-1.03.001.md:77` +
`BC-1.06.001.md:125` (surrogate range stated explicitly U+DC80..U+DCFF, other lone
surrogates raise); C04 `specs/behavioral-contracts/ss-01/BC-1.03.005.md:120` (VP row
restricted to caches hylo authors; foreign-carried and list-split duplicates
re-stated per PC5 with the SL:1033/1153 cites); C05 `BC-1.03.005.md:128` (DI-012
lifted for the OD-160 legs, sibling convention); C06
`specs/prd-supplements/error-taxonomy.md:215` (CP-O08 owners corrected to
BC-1.03.010 EC-009 and BC-1.03.018 PC3); C07 `specs/architecture/ARCH-03-statusline.md:195-196`,
`specs/architecture/ARCH-06-pyfmt.md:96-97`, `specs/behavioral-contracts/ss-05/BC-5.02.003.md:120`
(owner named by ID at all three sites); C08 `specs/behavioral-contracts/ss-01/BC-1.03.021.md:67-76`
(measured period-2 alternation with the full oracle provenance) +
`BC-1.03.010.md:73-76` + `specs/architecture/ARCH-03-statusline.md:197-201` +
`specs/architecture/ARCH-06-pyfmt.md:93-95`; C09
`specs/prd-supplements/error-taxonomy.md:238` (CP-A01..A03 site cells now cite the
raise sites, agreeing with BC-1.07.008 and the CP-A04/A05 rows); C10
`specs/prd-supplements/error-taxonomy.md:300` (CP-S14/CP-S16 carve-outs named with
their owning BCs); C11 `specs/behavioral-contracts/ss-01/BC-1.07.008.md:135` (register
progression states 49 since pass-9 CP-O12); C12 `BC-1.07.008.md:49` (29-byte wording
and hex listing agree).

Perimeter C2 — C2-01 `specs/behavioral-contracts/ss-01/BC-1.04.001.md:201,243-246`
(both residual guard-first passages reordered; sanitization before the scheme guard)
+ `:234-238` (stale client-redirect recipe replaced by the minimal-client loop
statement with the historical note); C2-02
`specs/behavioral-contracts/ss-01/BC-1.04.002.md:94-96` (Inv 1 names the
OverflowError class on the three subtraction sites, oracle-measured); C2-03
`specs/architecture/ARCH-03-statusline.md:234-236` (Early-Hints row cites EC-025 with
the correction noted); C2-04 `specs/architecture/ARCH-03-statusline.md:256,274-276`
(configured non-http(s) is the D4-EX-3 config error at load; a non-http(s) redirect
target is the OD-181 exclusion; the contradictory sentence removed); C2-05
`specs/verification-properties/VP-001-never-blank-exit0.md:43-44,91-92,98` (stdin
bearers located at BC-1.05.007 EC-011/EC-012; history bearer at BC-1.05.005 EC-011);
C2-06 `specs/behavioral-contracts/ss-01/BC-1.05.005.md:93` +
`BC-1.04.009.md:71` (registered keys named beside their default literals); C2-07
`specs/prd-supplements/interface-definitions.md:221,300-302` (label_local gains the
direct consumer; down-labels mark the indirect consumer; glyph-family column completes
the two segment BCs); C2-08 `specs/behavioral-contracts/ss-01/BC-1.04.001.md:321`
(PC1 reworded to one initial GET plus the hops the loop rules allow); C2-09
`specs/behavioral-contracts/ss-01/BC-1.04.018.md:51-57,101` (OD-160-tagged exact-int
leg; degrade behavior pinned) + `specs/verification-properties/VP-030-telemetry-row2-tables.md:64-67`
(generator narrowed to bool or float-range numbers); C2-10 `specs/prd.md:512`
(E-NET-001 cites Precondition 3 of BC-1.04.004); C2-11 VP-001 rows added at the
co-owner BCs and the frontmatter list completed (reciprocity battery, section 8);
C2-12 `specs/behavioral-contracts/ss-01/BC-1.05.003.md:78` (unit-constant note beside
the MTok divisor).

Perimeter D — D01 `specs/behavioral-contracts/ss-06/BC-6.01.002.md:88-95,111-147`
(unconditional injected metrics keys in both children's exact key sets, case value
wins) + `BC-6.02.003.md:149-152` + `specs/architecture/ARCH-07-parity-harness.md:96-100`
+ `specs/verification-properties/VP-034-oracle-isolation.md:46,57,116,134` (copies
verbatim); D02 `specs/behavioral-contracts/ss-06/BC-6.01.001.md:110-113` +
`BC-6.02.003.md:96-101` + `BC-6.03.001.md:50-55` + `specs/architecture/ARCH-07-parity-harness.md:190`
(one subagent-family rule; the older suffix shorthand notation removed everywhere incl.
changelog entries); D03 `specs/behavioral-contracts/ss-02/BC-2.03.002.md:83-91,117-121,145`
(cache-dir override absoluteness, exit-1 error line, per-OS IsAbs semantics,
HYLO_CONFIG explicitly exempt) + `specs/behavioral-contracts/ss-03/BC-3.01.001.md:68-78,142`
(base-directory kind discipline: relative HOME/LOCALAPPDATA/APPDATA treated as unset;
EC-013); D04 `specs/behavioral-contracts/ss-06/BC-6.02.002.md:98-110,158` +
`BC-6.02.003.md:162-176` (every-sid seeding; validator rejects an unseedable case; no
replay consults the real process tree); D05 `specs/architecture/ARCH-06-pyfmt.md:153,290-292`
+ `specs/behavioral-contracts/ss-05/BC-5.01.001.md:46,66` (RoundN re-signed over Num,
kind-preserving semantics, BC-1.05.009 PC-3 stands); D06
`specs/behavioral-contracts/ss-02/BC-2.02.001.md:84-90,200-204` (default-layer value
spells the interface-definitions default exactly; no provenance suffix on that path);
D07 `specs/behavioral-contracts/ss-06/BC-6.03.004.md:164,214-217` +
`BC-6.03.003.md:36` (flat corpus ids of the ARCH-07 grammar); D08
`specs/behavioral-contracts/ss-02/BC-2.01.005.md:129,212,214` (three legacy citations
corrected); D09 `specs/behavioral-contracts/ss-06/BC-6.04.001.md:67-68` (floor leg
installs the exact go.mod version); D10 see D03 (BC-3.01.001); D11
`specs/behavioral-contracts/ss-05/BC-5.04.003.md:75` (canonical TimeFloat signature).

## 2. Citations added or changed in this burst resolve on disk (task check 2)

Scripted sweep over all 239 spec files for live line-number pointers into ARCH and BC
files (frontmatter provenance excluded): exactly **one** live hit survives —
`specs/verification-properties/VP-017-exactly-one-backend.md:82` citing ARCH-02 by
line in a non-normative sketch comment. The cited content (the LoadOptions injection
seam) exists but moved from line 91 to 102 when A11 inserted the struct declaration
above it. Recorded as SC-35 below. Every other new or changed anchor resolves:

- Section anchors: all B07 fragment anchors resolve against the ARCH-03 heading
  set; the C2-03 EC-025 and C2-10 Precondition-3 anchors resolve against their BCs.
- BC-internal row citations (C02): BC-1.03.018's PC3 carries the CP-T04/CP-T05 rows
  where both citing files say.
- Cross-BC owner citations (C07/A10): BC-1.03.021 PC5/EC-004 exists as cited.
- Legacy SL citations corrected by D08 match the cited source lines.
- The newly added register, key-set and reason-table rows (calls 1, 2, 17) resolve
  at every named mirror (see section 4).

## 3. For-all properties touched in this burst vs the owning BCs (task check 5)

- **VP-004** (subagent output set): now quantifies over every legal stdin including
  the fuzz regime; the CP-A01..A05 degraded-line leg is stated with the DI-008
  carve-out and matches BC-1.07.008's degrade table and the catalogued fault list.
  The property is true for every legal input after the fix; a port passing the old
  NDJSON-only fuzz would have failed on a legal renderer fault.
- **VP-001 / VP-005** (classifier mode): the ModeText-plus-993 pinned semantics make
  the zero-byte implication hold for BOM, UTF-16/32 and over-depth stdin, matching
  the legacy text-mode load and the VP-006 site table. Main-entry scoping (A2-08)
  removes the last over-broad reading.
- **VP-030** (telemetry segment generator): narrowed to bool or float-range
  `sess_rate[0]`, which is exactly the domain over which the presence-and-dimming
  claim holds; the excluded exact-giant-int shape is BC-1.04.018's OD-160-tagged
  degrade leg, so VP and BC partition the input space without overlap or gap.
- **VP-022** (ledger absence): the qualified claim (never initiates ledger access;
  opens only the stdin-designated transcript) is true for every legal stdin,
  including one whose transcript path names the ledger file.
- **VP-006** (call-site budgets): the statement now separates what each leg proves;
  the newly added call-site lint closes the wrong-constant-at-a-call-site hole for
  the Go side, and the residual oracle-only scope is stated, not implied.

## 4. REQUIRED-PRESENCE checks (task check 3)

- `not an absolute path` present in `specs/behavioral-contracts/ss-02/BC-2.01.005.md:86`,
  `specs/behavioral-contracts/ss-02/BC-2.02.001.md:140`,
  `specs/prd-supplements/error-taxonomy.md:102`,
  `specs/prd-supplements/interface-definitions.md:204`. Byte-identical spelling.
- `invalid UTF-8` present in `specs/behavioral-contracts/ss-02/BC-2.02.001.md:138,166,168,247`,
  `specs/behavioral-contracts/ss-02/BC-2.01.005.md:175,177`,
  `specs/prd-supplements/error-taxonomy.md:96` (plus history rows).
- CP-O12 present at every register-listing locus: `specs/prd-supplements/error-taxonomy.md:51,177`
  with the 49 = 4+17+8+3+12+5 arithmetic at :270; `specs/prd.md:51,507`;
  `specs/architecture/ARCH-03-statusline.md:74,102`; `specs/verification-properties/VP-001-never-blank-exit0.md:96-98`;
  `specs/verification-properties/VP-011-tier-c-differential-fuzz.md:60`;
  `specs/behavioral-contracts/ss-01/BC-1.01.001.md:30`, `BC-1.01.009.md:32`,
  `BC-1.02.029.md` (owner, seven loci), `BC-1.05.003.md:106` (co-owner),
  `BC-1.03.018.md:52` (register census "49 paths — X4 S17 T8 N3 O12 A5"),
  `BC-1.03.006.md:78`, `BC-1.07.008.md:135`; `specs/gene-transfusion-assessment.md:50`.
  No live 47/48-as-total claim survives (47/48 appear only inside the historical
  progression and provenance lines).
- Lowercase family tokens `cpo01..cpo12` present at every file that enumerates the
  cpo families: `specs/verification-properties/VP-001-never-blank-exit0.md:222` and
  `specs/architecture/ARCH-07-parity-harness.md:190` (which also carries
  `cps01..cps17`, `cpt01..cpt07`, `cpt09`, `cpn01..cpn03`, `cpa01..cpa05`).
- `DGX_SL_VM_URL` and `HYLO_BACKENDS_0_METRICS_URL` as **unconditional** members of
  the exact key sets: `specs/behavioral-contracts/ss-06/BC-6.01.002.md:91-93,112-113,122-124,144-147`
  (both oracle-child and Go-child sets, with the case-value-wins rider),
  `specs/architecture/ARCH-07-parity-harness.md:96-100` (UNCONDITIONAL METRICS
  INJECTION), `specs/verification-properties/VP-034-oracle-isolation.md:46,57,116,134`
  (copied key sets and sketch), `specs/behavioral-contracts/ss-06/BC-6.02.003.md:149-152`
  (run-time injection rule, port known only at run time).

## 5. Orchestrator calls 1-5 and 9-14 stated identically at every carrier (task check 4)

| Call | Statement | Carriers verified |
|------|-----------|-------------------|
| 1 | metrics URL always injected, case value wins | BC-6.01.002 PC-1 + key sets; BC-6.02.003 PC-5; ARCH-07; VP-034 (4 sites) |
| 2 | subagent family rule, no suffix rule | ARCH-07 grammar row; BC-6.01.001 PC-5; BC-6.02.003 (Description + history); BC-6.03.001 |
| 3 | only cache_dir must be absolute; config path exit 1; relative HOME = unset | BC-2.01.005 PC-3; BC-2.03.002 (absoluteness scope + EC-012 + exit 1); BC-3.01.001 (PC-3 + kind discipline + EC-013); ARCH-02 LoadOptions comment context |
| 4 | per-sid seeding, reject unseedable | BC-6.02.002 Pre-3 + EC-005; BC-6.02.003 PC-6/PC-7 |
| 5 | RoundN(x Num, n int) Num kind-preserving | ARCH-06 signature row + reconciliation note; BC-5.01.001 PC-2 + postcondition |
| 9 | subagent output set incl. 29-byte line | VP-004 property + sketch; BC-4.01.001 VP row; BC-1.07.001 VP row |
| 10 | ModeText classifier, 993 budget | VP-001 sketch comment; VP-005 boundary note + sketch; VP-006 site table rows |
| 11 | mix re-read loop owner BC-1.03.021; period-2 cycle above one read step | ARCH-03; ARCH-06; BC-5.02.003 PC-7 (owner part); BC-1.03.021 PC5/EC-004 (measurement); BC-1.03.010 PC rider |
| 12 | 8192-byte chunk, probes 8191/8192, prefetch note removed; stat semantics | BC-1.02.004 PC2.3 + stat-semantics paragraph |
| 13 | CP-O07 canonical = transcript-reachable mirror vector; foreign seed = OD-160 | BC-1.03.007 EC-007 + vector block + VP rows + Traceability; error-taxonomy CP-O07 row |
| 14 | surrogate range U+DC80..U+DCFF | BC-1.03.001 EC-009; BC-1.06.001 EC-011 (range + raise otherwise) |

Wording identity was grepped carrier-by-carrier; each row's shared claims
(injection, family rule, unset treatment, seeding, Num signature, output set, mode,
owner id, chunk size, vector designation, surrogate bounds) appear in consistent
formulations at every carrier with no residual contrary sentence, except the one
sister site recorded as SC-36.

## 6. Reciprocity, union, counts, titles (task check 8)

- **BC/VP file counts:** 154 BC contract files (excluding BC-INDEX, BC-ALLOCATION),
  41 VP files (excluding VP-INDEX). Matches the ADV-P10 arithmetic (41 = 33+7+1).
- **Edge bijection:** VP-frontmatter `bcs:` edges = 283; BC VP-table edges = 270;
  union = 283. The 13 table-row-short edges are the established prose-citation
  convention (each BC names the VP in body prose or history; each verified by grep,
  e.g. the VP-027/VP-028 rows delegated to VP-040/VP-041 per pass-3/4 reconciliation,
  and BC-6.01.001's VP-006 self-check mention). Every edge mandated by pass 10
  (A2-01 rows, B03 rows, C2-11 rows) exists as a table row. Zero reverse-only edges.
- **VP-INDEX coverage map** regenerated from the index tables: 283 edges, identical
  to the union — 0 index-only, 0 union-only. The union recount matches the expected
  283 exactly.
- **Title quadruple:** all 154 BC H1 titles = BC-INDEX rows = prd section-2 rows
  (link-cell format) = BC-ALLOCATION rows, 154/154, escape-aware comparison.

## 7. Frontmatter (task check 7)

- All 239 spec `.md` files: YAML frontmatter parses with `yaml.safe_load`. Seven
  files intentionally carry no frontmatter (the owner-decisions log and the six
  research files) — all pre-existing, none touched by this burst.
- Exactly one `version:` key in every file; exactly one `modified:` key in every
  file that carries the key. The ARCH section family, the three supplements touched,
  and `cicd-setup.md` carry version-only frontmatter; verified against HEAD that
  these files had no `modified:` key before the burst either (family convention, not
  a burst omission).
- No file has a duplicated `version` or `modified` key; changed-file anomalies: 0/88.

## 8. Hygiene on the diff (task check 8)

Over all 1016 added lines: zero absolute-path hits, zero home-path hits, zero IP
literal hits outside the RFC 5737 and loopback allowances, zero email-like hits
outside the reserved example domains, zero emoji. The non-ASCII census shows 19
distinct characters, all established technical typography (dash, arrows, comparison
signs, section sign, the four status-line glyphs, superscripts, middle dot,
multiplication and minus signs). No non-English text detected.

## Burst-sync check matrix (10/10 executed)

| Check | Task | Result |
|-------|------|--------|
| Finding disposition | 1 | 69/69 closed on disk; 0 rejected; 0 open |
| Citation resolution | 2 | 1 live stale pointer (SC-35); all others resolve |
| Required presence | 3 | all five groups present at every required locus |
| Statement identity (calls 1-5, 9-14) | 4 | identical everywhere; SC-36 sister site |
| For-all vs owning BCs | 5 | consistent over every legal input (5/5) |
| Reciprocity/union/counts/titles | 6 | 283/283/283; 154; 41; quadruple 154/154 |
| Frontmatter | 7 | all parse; no key duplication; 0/88 anomalies |
| Hygiene | 8 | clean on all categories |

## 1. L2 to L3 Requirement Coverage

Pass (subagent interface contradictions resolved: D01 unconditional metrics injection
and D02 one family rule stated identically across BC-6.01.001/.002, BC-6.02.003,
BC-6.03.001, ARCH-07 and VP-034; call 17 reason vocabulary synced across BC-2.01.005,
BC-2.02.001, error-taxonomy and interface-definitions).

## 2. L3 to L4 Verification Property Coverage

Pass (283-edge union bijection; check 8). Pass-10's VP-side repairs (A2-01/02/05/06/07/08/09/10,
B03, C2-05, C2-09, C2-11) all carry matching BC-table rows; the 13 table-row-short
edges are the established prose-citation convention, each grep-verified.

## 3. Dependency Acyclicity

N.A. at Phase 1 — no story graph yet; ID minting append-only (nothing retired or
reused this pass; CP families extended only by the pass-9 CP-O12, still at 49 paths).

## 4. Architecture Alignment

Pass (LoadOptions declared with the EnvVars seam: A11; RoundN re-signed Num: D05/
call 5; DBig minted for the beyond-int64 site: A12; mix-loop owner BC-1.03.021 by ID
at every site: A10/C07; sanitization-before-guard consistent across BC-1.04.001 and
ARCH-03: C2-01/C2-03/C2-04).

## 5. Acceptance Criteria Quality

Pass at spec stage (BC postcondition completions: C2-01 reorder, C2-02 crash-list
completion, D06 default-layer value rule, D04 every-sid seeding, B01 renderer-CR
restatement; each verified against its owning BC's vectors).

## 6. Story Sizing

N.A. — Phase 1 precedes story decomposition; no story files touched by the burst.

## 7. Priority Consistency

N.A. at story level; PRD priorities unchanged by the burst (changelog 0.2.21 adds
only the NFR-006 nightly-scan target).

## 8. L1 to L2 to L3 to L4 Chain Completeness

No orphans introduced: the chain anchors verify at every layer touched by the burst —
title quadruple 154/154 (section 8 of the checks), the 283-edge VP relation closes
with zero residues against the VP-INDEX coverage map, and the register census (49
paths) is coherent from error-taxonomy through prd, ARCH-03, BC-INDEX-side contracts
and the VP catalogue.

## 9. AC Completeness Coverage

Clause-level reciprocity is maintained: the B03/C2-11 VP-001 rows exist at every
co-owner BC and in the frontmatter list; the A2-01 output-set rows exist at both
dispatcher BCs; A2-06/A2-10 state the closure check's powers honestly (membership,
uniqueness, test existence, expected-file match) with scope review as a manual
obligation and the register-keys-equal-ids assertion in the sketch.

## 10. ASM/R Traceability

No ASM/R regressions found in the diff. A08's R-004 correction binds the mitigation
to the parity census detector, agreeing with ARCH-08's restatement; the A09 P1-exit
wording in NFR-catalog no longer contradicts the OD-149 Tier C condition. No
assumption-adjacent edits beyond these.

## Cross-Reference Validation

ID-vocabulary and cross-reference repairs verified byte-precise: the path-grammar
reason string in all four mandated files, the harness metrics keys in all four
carriers, CP-O12 and the 49-path register at every listing locus, the lowercase cpo
family tokens, and the row-id (never line-number) citation form for BC-internal
predicates. All new section anchors resolve; the single residual line pointer is
SC-35.

## Spec vs Implementation Drift

N.A. — P1 spec crystallization precedes implementation (parity-first port not
started). The drift surface monitored at this stage is spec-vs-legacy parity,
adjudicated by the pass-10 perimeters themselves; the measurements this burst pinned
(8192-byte chunk, per-OS IsAbs semantics, the period-2 mix-cache cycle, RoundN
kind-preservation, surrogate byte range, oracle-run C2-02 OverflowError sites) keep
future drift auditable against pinned evidence.

## New sync-check findings

| SC-NN | Severity | File:line | Inconsistency | Owner |
|-------|----------|-----------|---------------|-------|
| SC-35 | Minor | `specs/verification-properties/VP-017-exactly-one-backend.md:82` | Last surviving live line-number pointer into an architecture file (inside the illustrative sketch comment). The cited LoadOptions seam moved from ARCH-02 line 91 to line 102 when ADV-P10-A11 inserted the LoadOptions declaration above it, so the pointer is stale by eleven lines. Remedy: cite by section anchor per the pass-10 no-line-pointers rule. | architect |
| SC-36 | Minor | `specs/behavioral-contracts/ss-05/BC-5.02.003.md:119` | Sister site of ADV-P10-C08: the PC-7 parenthetical still says the mix cache is rewritten "same size" every refresh without the one-read-step qualifier that ARCH-03, ARCH-06, BC-1.03.021 and BC-1.03.010 now carry. Above a single read step the size alternates with period 2. Remedy: add the same qualifier or defer to BC-1.03.021 PC5 explicitly. | product-owner |

### Critical

None.

### Major

None.

### Minor

SC-35, SC-36.

### Cosmetic

None.

## Validation Gate Result

**PASS** — no blocking findings. The pass-10 remediation burst is fully propagated on
disk: all 69 findings verified closed at their cited loci; the ten cross-file
orchestrator statements land identically at every carrier; the unconditional metrics
keys, the subagent-family rule, the reason vocabulary and the CP-O12/49-path register
are coherent across every listing site; the 283-edge `bcs:` bijection with the
VP-INDEX coverage map is exact; 154 BCs and 41 VPs with the title quadruple intact;
every frontmatter parses; the added lines are hygiene-clean. SC-35 and SC-36 are
non-blocking.

## Overall Metrics

| Metric | Value |
|--------|-------|
| **Pass-10 findings verified closed** | 69/69 (HIGH 8, MEDIUM 33, LOW 23, COSMETIC 5) |
| **Rejected with evidence** | 0 |
| **Open** | 0 |
| **New sync-check findings** | 2 (SC-35 Minor, SC-36 Minor) |
| **Machine checks** | 8 orchestrated batteries + targeted reads; 239 spec files swept, 88-file diff (+1016/−533) reviewed line-wise |

## Appendix: Validation Methodology

Fresh-context scripted sweep of the factory worktree's uncommitted spec tree
(`git diff HEAD` under `specs/`, 88 files, +1016/−533), scripts in the session
scratchpad (not committed): (1) live line-pointer sweep for the two required patterns
with frontmatter provenance classified separately, every hit adjudicated by reading
the citing and cited loci; (2) required-presence greps for the four mandated string
groups, key names and family tokens; (3) finding-by-finding anchor battery keyed to
`ADV-P10-INDEX.md` and the remediation plan's calls 1-18, each PASS requiring an
on-disk hit at the locus the fix should occupy, with full-cell reads adjudicating
truncated table evidence; (4) cross-file statement-identity battery for calls 1-5 and
9-14 across every named carrier; (5) structural battery — BC/VP counts, VP-frontmatter
edge set, BC-table edge set, VP-INDEX coverage-map regeneration with residue
comparison, and an escape-aware title quadruple across 154 contracts including the
prd link-cell row format; (6) `yaml.safe_load` frontmatter sweep over all 239 files
with key multiplicity counting, plus a HEAD comparison for the version-only families;
(7) hygiene regexes over all added lines with a full non-ASCII census. Manual reads
adjudicated every scripted anomaly (13 union-forward edges resolved as the
prose-citation convention; 10 changed files without a `modified:` key resolved as the
pre-existing family convention via HEAD). Nothing outside the report path was
written; nothing committed.
