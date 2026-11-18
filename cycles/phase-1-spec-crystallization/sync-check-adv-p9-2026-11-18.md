---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass"
producer: consistency-validator
timestamp: 2026-11-18T23:59:00Z
phase: 1
input-hash: "5c89f51"
inputs: [specs/behavioral-contracts/, specs/verification-properties/, specs/architecture/, specs/domain-spec/, specs/prd-supplements/, specs/prd.md, specs/cicd-setup.md, specs/dtu-assessment.md, specs/gene-transfusion-assessment.md, adversarial-reviews/pass-9.md, adversarial-reviews/ADV-P9-INDEX.md, pass-9-remediation-plan.md]
traces_to: ../../STATE.md
---

# Consistency Validation Report: hylo pass-9 fix-burst sync check

## Report Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo (status line + hybrid routing, P1 spec crystallization) |
| **Generated** | 2026-11-18T23:59:00Z |
| **Generator** | consistency-validator (fresh context; scripted sweeps under `/opt/homebrew/anaconda3/bin/python3 -I` 3.11.7 plus targeted file reads) |
| **Artifacts Scanned** | 100 dirty spec files vs `HEAD` (+1393/−675); 239 spec `.md` files swept (behavioral-contracts 156 incl. allocation/index, verification-properties 42 incl. index, architecture 11, domain-spec 9, prd-supplements 7, root files) |

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | L2 to L3 Requirement Coverage | pass (subagent interface source restored: A01; registry contract columns completed: C2-10) |
| 2 | L3 to L4 Verification Property Coverage | pass (270-edge union bijection; check 8) |
| 3 | Dependency Acyclicity | N.A. at Phase 1 — no story graph yet; ID minting append-only (CP-O12 minted, nothing reused) |
| 4 | Architecture Alignment | pass (platform.Abs single-home: A03/A12; metrics-client measured basis: C2-01/02/07; mix-cache asymmetry: A02/D03/D04) |
| 5 | Acceptance Criteria Quality | pass at spec stage (BC postcondition completions: B04/B05, C2-03, D06/D07/D08, D09) |
| 6 | Story Sizing (all <= 13 points) | N.A. — Phase 1 precedes story decomposition |
| 7 | Priority Consistency | N.A. at story level; PRD priorities unchanged by the burst |
| 8 | L1 to L2 to L3 to L4 Chain Completeness | pass (no orphans introduced; 270-edge recount clean; title quadruple 154/154) |
| 9 | AC Completeness Coverage | pass at spec stage (C2-04 VP-012 closure reciprocity; C2-05 DI-008 lift; CP-O12 carrier cites) |
| 10 | ASM/R Traceability | pass (no ASM/R regressions; A2-17 inventory recount done on disk) |

Detail for every row: the numbered sections below and "Burst-sync check matrix"
(rows 1-10) and "Finding disposition". Story-graph rows (3, 6, 7) are
explicitly out of scope for a Phase 1 spec-crystallization artifact and are marked
N.A. rather than assumed.

**Scope note.** Fresh-context post-remediation sync check for adversarial pass 9,
before the pass-10 decision. Inputs: `adversarial-reviews/pass-9.md` (85 verbatim
findings: HIGH 15 / MEDIUM 38 / LOW 28 / COSMETIC 4), `adversarial-reviews/ADV-P9-INDEX.md`,
and the calls in `pass-9-remediation-plan.md` (calls 1-15; no owner rulings this pass;
next free OD-194). Every disposition is spot-verified **on disk in the current working
tree**, not from history lines. Read-only on specs; nothing committed. Findings
continue the sync-check numbering lineage (SC-01..32 consumed by passes 3-8).
Repo-relative paths throughout.

## Headline result

**85 of 85 pass-9 findings verified CLOSED on disk; 0 REJECTED; 0 OPEN.** The two
burst-wide repairs are propagated at every named site: the mix-cache Save/Load
asymmetry (call 1) and the row-2 gate (call 2). CP-O12 is minted with the register at
49 paths (4+17+8+3+12+5) at every site that lists the register or the O family. All
surviving frontmatter parses (C02's five files plus the six companions repaired). Two
new sync-check findings are recorded (SC-33 Minor, SC-34 Cosmetic), neither blocking.
Validation gate: **PASS**.

## 1. Finding disposition (85 CLOSED / 0 REJECTED / 0 OPEN)

Perimeter A — A01 `specs/prd-supplements/interface-definitions.md:91-95` ("Subagent
stdin payload (--subagent)": `agentType`/`status`/`description`/`label`/`startTime`/
`model`/`tokenCount`/`tasks`) + `:120` + `:450` (NDJSON stdout schema, zero-byte and
row outputs both legitimate); A02 `specs/architecture/ARCH-03-statusline.md:174-198`
(session 991/991 YES; mix 991/994 with the measured exception, "Decode(Save(x)) CAN
reject what Save produced", re-read loop, "Session, git and cost-history keep
equality") + `specs/architecture/ARCH-06-pyfmt.md:82-96` (exception stated beside the
law; table row :71 save 994); A03 `specs/architecture/ARCH-05-platform.md:34`
(`abspath.go` + Win32 wrapper, `Abs(cwd, p string) (string, error)`, result type stated
once) + `specs/architecture/ARCH-03-statusline.md:157` ("platform.Abs(cwd, p string)
(ARCH-05) — NOT as an Env seam here"); A04 `specs/cicd-setup.md:58` (own job, RUNS ON
EVERY PR, never probe-gated) + `:151-154` (`coverage: G of 3 gated packages present`);
A05 `specs/cicd-setup.md:85` (`gitleaks: N commits scanned`, fail at N == 0, computed
at runtime across main + factory-artifacts); A06 `specs/architecture/ARCH-08-build-ci-release.md:24-32`
+ `:219` (toolchain line MUST land BEFORE govulncheck becomes required; go.mod itself
unchanged per "changes only when the owner asks"); A07 `specs/architecture/ARCH-07-parity-harness.md:32`
(in-process and as the built binary for a subset) + `specs/architecture/ARCH-08-build-ci-release.md:55`
(Tier A excluded because it needs the Python oracle, which the coverage job does not
install); A08 `specs/prd-supplements/risk-register.md:29` (R-004 carries the census +
gate-scope restatement); A09 `specs/prd-supplements/risk-register.md:26` (failed-replace
pinned by the AD-03 decision, the overlay OPTION rejected); A10
`specs/prd-supplements/interface-definitions.md:17` (Measured site list gains
`depthMetricsReply` 992/993) + `specs/prd.md:616` (§8 names all five measured sites);
A11 `specs/behavioral-contracts/ss-02/BC-2.01.005.md:82-92` (cache_dir MUST resolve
absolute, exact reason string, OD-144 rationale) + `specs/prd-supplements/interface-definitions.md:201`;
A12 `specs/architecture/ARCH-01-binary-cli.md:38-42` (type alias to `platform.EnvVars`,
"DECLARED ONCE", "no second declaration") + `specs/architecture/ARCH-03-statusline.md:149,161`;
A13 `specs/architecture/ARCH-09-reserved-boundaries.md:38-41` (enforcement credited to
VP-022's static analysis, "not itself the"); A14 `specs/prd.md:511` (dead rung follows
`statusline.theme.red` and `statusline.glyphs.degraded`); A15 `specs/cicd-setup.md:58`
(coverage job 30 min, matching the test job); A16 `specs/architecture/ARCH-08-build-ci-release.md:48,67-70`
(diagram and text: ubuntu leg ONLY); A17 `specs/architecture/ARCH-00-overview.md:21`
(`prd.md:70`).

Perimeter A2 — A2-01/B01 `specs/verification-properties/VP-040-frame-width-property-legs.md:55-58,93,135`
(P7 restated; generator domain covers rows {-1,0,1}; sketch asserts the full rule);
A2-02 `specs/verification-properties/VP-013-d4ex2-wrong-shape-tables.md:44` +
`specs/verification-properties/VP-029-transcript-parse-tables.md:52` (state after equals
state before EXCEPT as BC-1.03.018 PC2 says; offset advances; CP-O06..O08 drop `cur` to
null); A2-03 `VP-013:58-62` + `VP-029:60-66` (delete-the-line oracle adjusted per
PC4(a) AND PC4(b)); A2-04 `specs/verification-properties/VP-030-telemetry-row2-tables.md:56-59`
+ `specs/verification-properties/VP-031-bounded-resource-caps.md:46-50` (caps named by
their registered keys; pruning on the SUCCESS path only; failure path re-saves the
stored history verbatim); A2-05 `VP-031:27,61-69,101-103` (quick row is VP-030's alone;
the 16-subset key-order manual table now delivered here, routed jointly with VP-030);
A2-06 `specs/verification-properties/VP-001-never-blank-exit0.md:56-58` +
`specs/verification-properties/VP-005-stdin-decode-totality.md:44-46` (undecodable or
non-object stdin → EXACTLY ZERO stdout bytes); A2-07
`specs/verification-properties/VP-016-config-error-classes-line.md:59-63` (the riding
reasons belong to NONE of the seven classes; "ride the class register" wording
withdrawn); A2-08 `VP-013:71-73` (the canonical 21 contain no CP-O rows; dedicated legs
delivered beside); A2-09 `specs/verification-properties/VP-027-frame-width-tables.md:39-43`
(row 2 never rendered at rows ≤ 1; hiding qualified per PC2 v1.3.4/1.3.5); A2-10
`specs/verification-properties/VP-006-json-depth-budgets.md:143` (production symbol vs
measured literal — "CAN fail now"); A2-11 `specs/verification-properties/VP-035-corpus-hygiene.md:68,89-92`
(one planted canary per hygiene category, each MUST be flagged); A2-12
`specs/verification-properties/VP-004-closed-exit-code-surface.md:51-53` (MAIN fuzz
generator's domain EXCLUDES `--subagent`); A2-13 `specs/verification-properties/VP-041-row1-property-legs.md:45-48`
(P-b precondition: timer segment renders only when `dur > 60000`; generator draws it);
A2-14 `VP-041:52,119-120` (P-i named in the Method, dense-grid heat triple leg); A2-15
`specs/domain-spec/capabilities.md:31` (CAP-009 carve-out lists the unmapped-panic
backstop per OD-155); A2-16 `specs/verification-properties/VP-007-render-determinism-seams.md:57-59`
(DI-007 corollary restores the environment seams); A2-17 `specs/dtu-assessment.md:55`
("72 S1 BCs (all 101 S1 contracts less the 21 transcript and 8 subagent contracts)");
A2-18 `specs/gene-transfusion-assessment.md:52` ("10,893 naive-time golden rows per
zone grid, across four zone grids", aligned with VP-026); A2-19
`specs/domain-spec/owner-validation-list.md:242-244` (verbatim proposal retained with a
pass-9 disposition note: adopted as OD-125 "for now with a revisit flag", not as an
unqualified law); A2-20 `specs/verification-properties/VP-037-three-os-ci-matrix.md:40`
(typo fixed), `specs/verification-properties/VP-017-exactly-one-backend.md:82-97` (`Load`
is three-valued: `(*Config, []Warning, *ErrorSet)`), `VP-004`/`VP-016` generators feed
scalars via `reflect.ValueOf` (Go-fuzz-compatible).

Perimeter B — B02 `specs/behavioral-contracts/ss-01/BC-1.01.007.md:48-50,63-64,69-73,108,138-139`
(the rows ≥ 2 term everywhere: Description, PCs, Inv 1, VP row, VP Anchors; counterexample
rows=1/narrow_cols=-10/COLUMNS=-5 stated); B03 `specs/behavioral-contracts/ss-01/BC-1.02.029.md:87`
(EC-009: `tin`/`tout` each sub-bound, exact-int sum `tot` at SL:626, `tot * dgx_mtok`
at SL:633, local lane, valid basis → OverflowError → degraded line) + canonical vector
and `specs/behavioral-contracts/ss-01/BC-1.05.003.md:103` (co-owner, the `⛏` value);
B04 `specs/behavioral-contracts/ss-01/BC-1.02.004.md:94-95` (PC2.3: chunk-scoped strict
decode, `io.DEFAULT_BUFFER_SIZE` 8192, invalid byte after the first LF still fails);
B05 `BC-1.02.004:71-73,108-110` (`isdir`/`isfile` catch `(OSError, ValueError)`, stat
errors never stop the walk, only `open`/read failures reach the SL:394 handler); B06
`specs/behavioral-contracts/ss-01/BC-1.02.015.md:111` (segment-present row restricted to
finite `dur` in non-degrading renders, with the CP-S12/S13 and CP-O05 carve-outs) +
`VP-041` P-t; B07 `specs/behavioral-contracts/ss-01/BC-1.01.009.md:67` (step 4 Write
cell: nothing when the cached verdict is fresh — `fetch_ts > now − TTL` returns early
and writes nothing, SL:324-325).

Perimeter C — C01 `specs/behavioral-contracts/ss-01/BC-1.07.007.md:122-136` (CTV
Expected Output column uniform pure-ASCII wire notation; ESC spelled `\u001b`; the
Infinity row carries `✔`/`·` escapes, oracle re-run); C02 the five files
repaired and all 11 call-5 files now parse (check 9; no history entry lost per the
repair entries, e.g. `BC-1.07.002:29`); C03 `specs/behavioral-contracts/ss-01/BC-1.03.018.md:52,133`
(Inv 3 corrected: transcript-borne exact-int totals that are counted can still degrade
later at render — CP-O04, CP-O09, now CP-O12) + `specs/behavioral-contracts/ss-01/BC-1.03.006.md:78`
cross-reference; C04 `specs/behavioral-contracts/ss-01/BC-1.03.017.md:54,84` (Inv 1 and
the VP-029 row restricted to transcripts with no W-lines, with the D4-EX-2 counter-example);
C05 `specs/behavioral-contracts/ss-01/BC-1.07.002.md:29,45` (`enabled=false` is ruled
new behavior per OD-155, not a DI-012 named deviation — Description, VP-005 row and
Traceability aligned, "agrees with VP-005"); C06 `specs/behavioral-contracts/ss-01/BC-1.07.004.md:76,119`
(raw token restored to the `A` escape so input and output differ; PC4 respelled);
C07 `specs/behavioral-contracts/ss-01/BC-1.07.005.md:96` (EC-005: failed row with NO
name fields); C08 `specs/behavioral-contracts/ss-01/BC-1.06.001.md:97-98,133` (PC4
gains the no-regular-transcript precondition; with a transcript CP-S14 degrades first);
C09 `specs/behavioral-contracts/ss-01/BC-1.03.002.md:87` (EC-008 NaN leg: fails all of
`<`/`==`/`>`, reaches `fh.seek(nan)` raising TypeError either way — grow-path-only
wording does not hold for NaN); C10 `specs/behavioral-contracts/ss-01/BC-1.03.020.md:105`
(C2's native-hylo reference is row 15 plus appended `A9`, `S11`, giving `lr [90.0,false]`);
C11 `specs/behavioral-contracts/ss-01/BC-1.03.010.md:111` (CP-T05 when deduplicated,
CP-T04 at SL:1112 when counted — outcome the same) + `specs/behavioral-contracts/ss-01/BC-1.03.020.md:78`
(OD-32's literal text covers only the `t0` half; the non-numeric-`out` half comes from
CONV-ABS-15).

Perimeter C2 — C2-01 `specs/behavioral-contracts/ss-01/BC-1.04.001.md:108-115,342`
(interim skip = STATUS 100 ONLY; 101/102/103 final → HTTPError → no sample; new EC-025
pins the 103 Early Hints case); C2-02 `BC-1.04.001:170-173` (urlsplit sanitization
BEFORE the scheme guard and quote: leading C0/space stripped, TAB/CR/LF deleted,
scheme lowercased; `HTTP://` followed); C2-03 `specs/behavioral-contracts/ss-01/BC-1.05.004.md:70-71`
(the OD-166 convertibility skip is not part of the PC1 guard; decided at the write step,
PC4, after the load and the `sessions.get(sid)` lookup, so CP-S15 at SL:230 still fires);
C2-04 `specs/behavioral-contracts/ss-01/BC-1.05.009.md:127-128,163` (VP-012 closure rows
for OD-30 and OD-166) + `specs/verification-properties/VP-012-exclusion-set-closure.md:13`
(`bcs:` gains BC-1.05.009) + `specs/verification-properties/VP-INDEX.md` (map row synced,
v1.20); C2-05 `specs/behavioral-contracts/ss-01/BC-1.05.004.md:159` (L2 row gains DI-008
with the CP-S15 degrade rationale); C2-06 `BC-1.04.001:375,389` (ARCH-03 cited by
SECTION anchor only — `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract`
resolves against the `## Interfaces (design doc §2.2, reused as the contract)` heading
at ARCH-03:116); C2-07 `BC-1.04.001:73-78` (Host = URL netloc as written,
percent-unquoted, port only when written); C2-08 `specs/behavioral-contracts/ss-01/BC-1.04.016.md:102`
(VP row cites the Precondition 1 list, not PC1); C2-09
`specs/behavioral-contracts/ss-01/BC-1.04.003.md:27,50-52` (PC2/PC3 name
`statusline.sparkline.max_age_s` and `.history_cap` beside the default literals); C2-10
`specs/prd-supplements/interface-definitions.md:223,245,275` (registry contract columns
gain BC-1.04.009, BC-1.05.005 PC2, BC-1.05.003 respectively).

Perimeter D — D01 `specs/behavioral-contracts/ss-06/BC-6.03.004.md:39,66-72` (rider-test
closure pinned: NO exclusions.json entry for OD-76 or D4-EX-1; EC-006's example
respelled to a valid OD-30 + D4-EX-2 shape); D02
`specs/behavioral-contracts/ss-03/BC-3.02.001.md:26` (Inv 4: no unseeded corpus case;
probe exercised by dedicated Go table tests with a fake process table) +
`specs/behavioral-contracts/ss-03/BC-3.02.002.md:26,54-67` (rows I1-I6 run in the same
dedicated Go table tests against the pinned legacy column; corpus stays UTC-only); D03
`specs/behavioral-contracts/ss-05/BC-5.02.003.md:107-121` (PC-7 respelled: the mix cache
is the measured Save≠Load exception; equality scoped to the equal-budget caches); D04
`specs/behavioral-contracts/ss-05/BC-5.02.006.md:84-99,117-128` (one measured exception
to the 995 − s law; budget/payload unit defined — total object nesting, top-level saved
object = 1; the 992..994 consequence pinned); D05 `specs/behavioral-contracts/ss-02/BC-2.01.004.md:36,190-196`
(percentiles check INTRA-KEY; error names `statusline.cost.percentiles` with its full
JSON value) + `specs/behavioral-contracts/ss-02/BC-2.02.001.md:35` + error-taxonomy
agreement; D06 `specs/behavioral-contracts/ss-02/BC-2.01.002.md:33,87-100,121` (per-key
`backends[<i>]` errors sort AFTER all registry-key errors, by index then field name;
`[from <ENVNAME>]` names the variable that carried the value); D07
`specs/behavioral-contracts/ss-02/BC-2.01.005.md:187-193` (default-only Text/List keys:
Text-class checks first, then the default comparison); D08 `specs/behavioral-contracts/ss-02/BC-2.02.001.md:130`
(`invalid UTF-8` minted: Text class, WTF-8 lone-surrogate Windows clause) mirrored
byte-for-byte at `specs/prd-supplements/error-taxonomy.md:95` and applied at
`specs/behavioral-contracts/ss-02/BC-2.01.005.md:176`; D09
`specs/behavioral-contracts/ss-05/BC-5.04.001.md:52-57` (working domain's lower bound
corrected to 1970-01-02T00:00 local wall, the fold-0 `u1 − 86400` probe; 1970-01-01T12:00
degrades) + `specs/behavioral-contracts/ss-05/BC-5.04.002.md`; D10
`specs/behavioral-contracts/ss-06/BC-6.01.002.md:34` (delta = `PYTHONIOENCODING` plus
`TMP`, `TEMP`, `SYSTEMROOT`; the table test asserts the exact per-OS sets); D11
`specs/behavioral-contracts/ss-06/BC-6.01.003.md:35,128,144,179` (claim NARROWED to what
the canary can detect — measured: even `LC_ALL=C` round-trips U+0664 — plus a `-I`
negative-control table test); D12 `specs/behavioral-contracts/ss-06/BC-6.02.002.md:32,97-102`
(new Pre-3: replay caches start FRESH with a fixed synthetic `proc_start` exactly as
corpus cases under BC-6.02.003 PC-6; a replay NEVER consults the machine's real process
tree); D13 `specs/behavioral-contracts/ss-05/BC-5.02.003.md:30,55` (Pre-1 anchors
swapped: SL:1202 is main()'s load, SL:930 the subagent path's); D14
`specs/behavioral-contracts/ss-05/BC-5.02.002.md:27` (generator prose repinned to the
space-separated print emission; CI byte-compares); D15
`specs/behavioral-contracts/ss-05/BC-5.01.007.md:30,72-74` (`_fmt_lines` calls `int(n)`
at SL:853; the float crossing is the mixed division `n / 1e6` at SL:857, EC-011
reshaped); D16 `specs/behavioral-contracts/ss-05/BC-5.04.003.md:31,77-81` (the unverified
in-formula C description withdrawn; only the measurable consequence pinned — agreement
below |ns| ≥ 2^62, divergence confined to it, never under a frozen clock); D17
`specs/behavioral-contracts/ss-05/BC-5.01.004.md:27` (beyond-int64 rule for the
`{pct:>2d}` site: `round()` of a finite float64 is an exact unbounded int formatted in
full decimal, no degradation); D18 `specs/behavioral-contracts/ss-02/BC-2.01.005.md:89-92`
(set-but-empty `HOME`/`USERPROFILE` → `home directory unknown`, consistent with
BC-2.03.002 PC-4); D19 `specs/behavioral-contracts/ss-06/BC-6.04.002.md:31,40` (H1
enriched with the large-transcript exemption: 100 ms ceiling; BC-INDEX and
BC-ALLOCATION title columns synced); D20 `specs/behavioral-contracts/ss-02/BC-2.02.001.md:35,88`
(repeated word fixed; `indexed-entry` singular form).

### The one rejection check

None — no pass-9 finding was rejected. The one orchestrator-measured correction that
reversed a perimeter's reachability arithmetic (C02's companion claim that the
transcript-borne payload could trip the SAVE budget) was already REJECTED in pass 8
(ADV-P8-C02) and remains realized in
`specs/behavioral-contracts/ss-05/BC-5.02.006.md:93-99` and
`specs/behavioral-contracts/ss-01/BC-1.03.021.md:60-62` ("payload document depth 993 —
saves cleanly; boundary 994 saves / 995 fails"); pass 9 added the LOAD side (991) to the
same statements.

## 2. Citations added or changed in this burst resolve on disk (task check 2)

Beyond copies agreeing, each newly added or reworded citation was opened at its target:

| Citation (source) | Target | Resolves |
|---|---|---|
| BC-1.03.017:54,84 → "BC-1.03.018:95-96" (CP-T04/T05 skip predicates read `seen_ids`) | behavioral-contracts/ss-01/BC-1.03.018.md:95-96 | yes (both lines carry the predicates) |
| BC-1.03.002:87 → "BC-1.06.001 EC-002" (json.load accepts NaN) | behavioral-contracts/ss-01/BC-1.06.001.md | yes (EC-002 foreign-cache NaN row) |
| BC-1.07.007:122-123 → "BC-1.07.004 PC3/Inv 2" (ensure_ascii wire) | behavioral-contracts/ss-01/BC-1.07.004.md | yes (PC3/Inv 2 carry `json.dumps` ensure_ascii) |
| BC-1.04.001:389 → ARCH-03 section anchor `#interfaces-design-doc-22-reused-as-the-contract` | architecture/ARCH-03-statusline.md:116 heading | yes (slug derives from `## Interfaces (design doc §2.2, reused as the contract)`) |
| BC-1.02.029 / BC-1.05.003 → CP-O12 owners; error-taxonomy register row | prd-supplements/error-taxonomy.md:266-268 | yes (register row names both carriers) |
| BC-1.05.004:159 → VP-001 row "never-blank per DI-008" | verification-properties/VP-001-never-blank-exit0.md (`bcs:` carries BC-1.05.004) | yes |
| VP-012:13 `bcs:` → BC-1.05.009 | behavioral-contracts/ss-01/BC-1.05.009.md:127-128 (body closure rows) | yes (bidirectional) |
| BC-1.04.001 EC-025 (new) | same file, line 342 | yes (appended after EC-024, append-only numbering) |
| BC-5.02.003:181 five measured sites → "prd §8" | prd.md:616 | yes (stdin/transcript/metrics/session/git listed with the same figures) |
| BC-1.03.017:84 → VP-029 row (generator restricted to W-line-free transcripts) | verification-properties/VP-029-transcript-parse-tables.md | yes (generator restriction stated) |
| BC-1.01.007:108,138 → VP-040 P7 row and VP Anchors | verification-properties/VP-040-frame-width-property-legs.md:55-58 | yes (identical predicate) |

Lesson L-PG-29 honored: resolution verified at the target, not merely between two
copies of the citation.

## 3. For-all properties touched in this burst vs the owning BCs (task check 3)

Each "for all inputs" property was walked against the owning BC's postconditions,
including skips, degrades, drops and offset/size adjustments:

- **VP-040 P7 ↔ BC-1.01.007 (PC2-PC4, Inv 1) / BC-1.01.003 PC1.** The canonical gate
  "row 2 rendered iff `rows ≥ 2` AND (`rows > 2` OR `cols == 0` OR `cols ≥ narrow_cols`)"
  is stated identically in all four documents (BC-1.01.007:49,108,138; BC-1.01.003:56;
  VP-040:55-58,93,135; VP-027:39-43 with the rows ≤ 1 note). The omission-form
  equivalent ("omitted iff rows ≤ 1 or (rows == 2 and `cols ≠ 0` and `cols <
  narrow_cols`)") is logically equivalent to the rendered-form; the rows=1 /
  narrow_cols=-10 / COLUMNS=-5 counterexample is closed by PC4. No legal input breaks
  the property as now scoped: rows ≤ 1 never renders row 2, and at rows == 2 a
  negative configured narrow_cols admitting negative cols renders row 2 exactly when
  legacy does.
- **VP-013 / VP-029 W-line legs ↔ BC-1.03.018 PC2/PC4.** The quick leg now asserts
  "state after equals state before EXCEPT as BC-1.03.018 PC2 says" (offset advances;
  CP-O06..O08 drop `cur` → null), and the delete-the-line oracle adjusts for PC4(a)
  (hylo `size` = legacy's + each deleted line's bytes + terminator) and PC4(b) (the
  OD-167 cur-null at overflow skips). Previously a correct port failed every overflow
  W-line and every delete-the-line input; no legal input breaks the corrected forms.
- **VP-030 / VP-031 history leg ↔ BC-1.04.003 (Inv 2, PCs).** Pruning holds "on the
  SUCCESS path only"; the fetch-failure path re-saves the stored history verbatim
  (SL:327, SL:353-355), caps named by their registered keys
  (`statusline.sparkline.history_cap`, `statusline.sparkline.max_age_s`). The
  A2-04 counterexample (a t=0 point re-saved at t=200 after a failed fetch) is now
  inside the stated domain, not a violation. Hard-coded 32/90 literals are gone from
  the live for-alls (remaining 32/90 spellings are the registry Default cells and
  history provenance).
- **VP-041 P-b / P-t ↔ BC-1.02.015/016, BC-1.02.027.** P-b carries the
  timer-segment precondition (`dur > 60000`, gate SL:540, suffix SL:551-553) so a
  varying `dur` cannot false-fail; P-t is restricted to finite `dur` in non-degrading
  renders with the CP-S12/S13 and CP-O05 carve-outs, matching BC-1.02.015:111 exactly.
- **VP-016 ↔ BC-2.02.006.** The "exactly one of the seven classes" antecedent is
  preserved by scoping the claim to the seven-class register, with the
  path-grammar and backends-cardinality reasons stated to belong to none of the seven
  while riding the same one-line E-CFG-001 surface — the property is now evaluable.
- **VP-004.** The MAIN fuzz leg excludes `--subagent` from argv and the subagent entry
  is covered by its own legal-state legs (zero bytes legitimate), so no legal
  MAIN-mode input trips the stdout-empty assertion.
- **VP-001 / VP-005 subagent oracle.** Undecodable or non-object stdin → EXACTLY zero
  stdout bytes (matching `main_subagent` SL:928-936, DI-008, BC-1.07.003); the weak
  "rows or zero bytes" oracle is gone.

No legal input was found that breaks any touched property under its current, narrowed
domain.

## 4. Mix-cache Save/Load asymmetry (task check 4)

| Site | Save | Load | Depth unit | Equality claim | Re-read loop |
|---|---|---|---|---|---|
| specs/architecture/ARCH-03-statusline.md:174-198 | 994 | 991 | nesting of the saved document (rows table; unit defined once in BC-5.02.006) | "Session, git and cost-history keep equality" (:196); mix = MEASURED EXCEPTION (:186-189) | :192-195 |
| specs/architecture/ARCH-06-pyfmt.md:71,82-96 | 994 | 991 | "total object nesting" | equality restated for session/git/cost; mix = THE MEASURED EXCEPTION (:84-88); `Decode(Save(x))` can reject for mix | :91-94 |
| specs/behavioral-contracts/ss-05/BC-5.02.003.md:107-121 (PC-7) | 994 | 991 | "total nesting of the saved document, top-level object = 1" (:30,113) | "Save EQUALS Load" scoped to equal-budget caches (:120-121) | :117-119 |
| specs/behavioral-contracts/ss-05/BC-5.02.006.md:84-99,117-128 | 994 (row :99) | 991 | "**total object nesting** of the saved document, top-level saved object = 1" (:88,124) | exception stated as the ONE exception to the 995 − s law (:86-88); equality for equal-budget caches (:117-120) | :124-128 |
| specs/behavioral-contracts/ss-01/BC-1.03.021.md:26,60-64,81,101 | 994 | 991 | "total nesting of the saved document, top-level object = 1" (:26) | "ASYNMMETRIC for the mix cache — the measured exception" (:62-63); "session/git/cost keep equality" | PC5 (:63-64) + EC-004 (:81, "every refresh") |

All five state Save 994 / Load 991, the measured next-refresh re-read-and-rewrite loop,
and keep Save = Load for session/git/cost-history. No unscoped "Save budget EQUALS Load
budget" or "Decode(Save(x)) never rejects" claim survives for the mix cache anywhere in
the tree (grepped).

## 5. Row-2 rule (task check 5)

The call-2 rule — row 2 rendered iff `rows ≥ 2` and (`rows > 2` or `cols == 0` or
`cols ≥ narrow_cols`) — is byte-equivalent at: BC-1.01.007:49 (and the in-domain
reduction :70-72), BC-1.01.003:56, VP-040:55-58 (with the omission-form equivalent) and
the generator row :93 and sketch :135; VP-027:39-43 carries the qualifying form
("never rendered at rows ≤ 1"; hiding at rows == 2 with `cols < narrow_cols`) that
specializes to the same function on all (rows, cols). No contradicting formulation
survives.

## 6. CP-O12 and register 49 (task check 6)

CP-O12 ("cost-pick equivalence overflow", Surface 1, render-time degrade like CP-O04;
SL:626/SL:633; owner BC-1.02.029, co-owner BC-1.05.003) is present at every locus that
lists the register, the O family or the cpo families:

- `specs/prd-supplements/error-taxonomy.md`: register 49 = 4 + 17 + 8 + 3 + 12 + 5
  (:266-268, "CP-O01..O12"), mint history :22, O-row :175.
- `specs/prd.md`: NFR-002 trigger list `CP-O10/O11/O12` (:490), E-REN-002 "the
  cost-pick sum CP-O12" (:506), changelog 0.2.19 (:25).
- `specs/prd-supplements/nfr-catalog.md`: NFR-002 row (:25) and gate prose carry the
  register by reference to error-taxonomy's 49-path census (the literal families live in
  error-taxonomy and prd; no stale count remains).
- `specs/architecture/ARCH-03-statusline.md`: step 7d row (:74, CP-O12 raises HERE at
  render on the local lane) and the catalogue paragraph (:102-106).
- `specs/verification-properties/VP-001-never-blank-exit0.md:41-44` (catalogue
  "CP-O01..O12 ... O12 the cost-pick equivalence overflow") and its sketch;
  `specs/verification-properties/VP-011-tier-c-differential-fuzz.md:60-62` (49-path
  catalogue with the same arithmetic).
- `specs/gene-transfusion-assessment.md:52` (register coverage in the strategy row).
- `specs/behavioral-contracts/ss-01/BC-1.01.001.md:30`, `BC-1.01.009.md:32,73,81`
  (incl. the step 4/7d effect-table registration), `BC-1.02.029.md:24,61,87,108,149`
  (EC-009 + canonical vector), `BC-1.05.003.md:32,103,132`, `BC-1.03.018.md:35-36,52,133`
  (C03), `BC-1.03.006.md:22,78` (cross-reference).

Arithmetic re-derived independently: X4 + S17 + T8 (T01..T07 + T09, T08 retired) + N3
+ O12 + A5 = 49. No site still says 47 or 48 as a live claim (47/48 appearances are
history entries only).

## 7. Reason strings (task check 7)

- `not an absolute path` — behavioral-contracts/ss-02/BC-2.01.005.md:85 and
  prd-supplements/interface-definitions.md:201: backticked, byte-identical. It does not
  appear in BC-2.02.001/error-taxonomy (the path-grammar family intentionally rides
  E-CFG-001 without a dedicated class, per BC-2.01.005:85-86 and
  error-taxonomy:138); no competing spelling exists in any of the four files.
- `invalid UTF-8` — behavioral-contracts/ss-02/BC-2.02.001.md:130,157,159,
  behavioral-contracts/ss-02/BC-2.01.005.md:176 and
  prd-supplements/error-taxonomy.md:95: backticked, byte-identical, with the D08
  WTF-8 lone-surrogate Windows clause identical in the mint and the mirror. (The
  interface-definitions occurrence at :64 is the stdin-decode behavior note, not the
  reason string; no conflict.)

## 8. Reciprocity, union, counts, titles (task check 8)

Independent recount (scripted over all 41 VP files × 154 BC bodies):

- 154 BC contract files; 41 VP files; **270 directed `bcs:` edges** (= VP-INDEX v1.20's
  claim; pass 8 stood at 269; the +1 is BC-1.05.009 ↔ VP-012, C2-04).
- VP-INDEX BC Coverage Map = the union of `bcs:` EXACTLY: 0 forward-only, 0
  reverse-only, 0 edge BCs lacking a map row, 154/154 map rows.
- Catalog totals re-derive: 41 VPs; by property class invariant 33 + safety 7 (+ the
  per-method split 20 + 13 + 3 + 2 + 1 + 1 + 1 = 41) as printed in VP-INDEX "Totals".
- Title quadruple (H1 = BC-INDEX = prd §2 = BC-ALLOCATION) escape-aware equality holds
  154/154, including D19's enriched BC-6.04.002 H1 synced into all four loci and the
  escaped-pipe titles (BC-1.02.003, BC-2.02.006) verified with escaping respected.

## 9. Frontmatter (task check 9)

All 239 spec `.md` files swept with `yaml.safe_load` on the frontmatter block: 232
parse clean; the 7 files without a frontmatter block
(owner-decisions-log-2026-11-14.md and the six research/ notes) are the established
no-frontmatter design, all untouched by this diff. Exactly one `version:` key in every
file carrying frontmatter, and exactly one `modified:` key in every file that carries
the key (27 files — architecture/, domain-spec/, cicd-setup.md, three
prd-supplements, product-brief.md — have version-only frontmatter, the pre-existing
convention, unchanged by the diff: no `±modified`/`±version` regressions in the
diff beyond paired version bumps). Zero YAML failures remain from C02's five files
(BC-1.07.002/.003/.006/.007/.008) or the six companions (dtu-assessment.md, VP-001,
VP-011, VP-012, VP-030, VP-031); block-style lists preferred, no history entry lost.

## 10. Hygiene on the diff (task check 10)

All 1393 added lines reviewed:

- **Absolute paths:** one hit, the planted synthetic canary
  `{"home-path", "/home/example-user/projects"}` (VP-035 scan self-test) — by design,
  the fixture exists to look like a real path for the hygiene scanner. No real
  machine paths.
- **IPs:** zero IPv4 literals outside 192.0.2.x / 127.0.0.1 (the localhost HTTP
  oracle references use 127.0.0.1).
- **Emails:** one hit, the synthetic `example.com` canary planted in VP-035 —
  allowlisted.
- **Hostnames:** zero non-allowlisted host/domain spellings.
- **Personal/infra leakage:** zero hits against the private hygiene-terms list.
- **Non-English text / emoji:** no CJK/kana/hangul; the 30 distinct non-ASCII
  characters are typography and mathematics (dash, arrows, ≤/≥/≠, −, ×, …, ⁿ
  superscripts), the legacy glyph defaults the specs must name (⌂ ◔ ☾ ⚡ �️◂▓▒前不久
  ☾ ✔ and `⛏`), and the section/mark symbols (§ �̏) — no emoji-block characters.
  Nine raw-glyph lines are the watts/idle/cost_pick/cost_pick-pick defaults and
  CP-O12's `⛏` value carrier.

## Burst-sync check matrix (10/10 executed)

| # | Check (orchestrator wording) | Result |
|---|------------------------------|--------|
| 1 | Every finding CLOSED / REJECTED-with-evidence / OPEN | PASS — 85 CLOSED (section 1), 0 REJECTED, 0 OPEN; every fix verified in current working-tree content, none from history lines |
| 2 | Added/changed citations resolve on disk | PASS — 11-citation battery in section 2, all resolve at the target artifact |
| 3 | For-all properties consistent with owning BC postconditions | PASS — seven property families walked (section 3); no legal input breaks any of them |
| 4 | Mix-cache asymmetry identical at five sites; session/git/cost keep Save = Load | PASS — section 4 |
| 5 | Row-2 rule identical in BC-1.01.007, BC-1.01.003, VP-040, VP-027 | PASS — section 5 |
| 6 | CP-O12 / register 49 everywhere listed | PASS — section 6 (13 files) |
| 7 | Reason strings byte-identical | PASS — section 7 |
| 8 | bcs: ↔ BC reciprocity; VP-INDEX map = union; 154 BCs, 41 VPs; titles | PASS — 270-edge bijection with zero residues; title quadruple 154/154 (section 8) |
| 9 | Frontmatter parses; one version and one modified key | PASS — 232/232 frontmatter files parse; key counts clean (section 9) |
| 10 | Hygiene on added lines | PASS — section 10 |

## 1. L2 to L3 Requirement Coverage

Registry and interface closures hold: the subagent stdin payload and NDJSON stdout
schema now have a single interface source (A01,
`specs/prd-supplements/interface-definitions.md:91-120,450`); the config registry's
Contract columns are completed for the three under-registered keys (C2-10); the
`paths.cache_dir` domain is a stated set (A11, D18); BC-ALLOCATION and BC-INDEX title
sync verified in the quadruple (check 8). No capability loses its owning contract in
this burst; the CAP→BC spine is untouched apart from anchor repairs (D13).

## 2. L3 to L4 Verification Property Coverage

Verified by independent recount (check 8): 154 BCs ↔ 41 VPs, 270 directed `bcs:` edges,
VP-INDEX coverage map exactly the union of `bcs:` (0 diffs, 0 forward-only, 0
reverse-only). Burst-specific closures: C2-04 (VP-012 `bcs:` + body gain BC-1.05.009;
VP-INDEX v1.20 map row synced), B03/C03 (CP-O12 in VP-001's catalogue and VP-011's
census), A2-05 (VP-031 delivers the 16-subset key-order table BC-1.04.003 routes to
it). Every pass-9 VP change is reciprocated.

## 3. Dependency Acyclicity

N.A. at Phase 1 — no story dependency graph exists yet (story decomposition is Phase 2).
Nothing in this burst introduces a cycle in the spec cross-reference graph: all ID
minting is append-only (CP-O12 appended; CP-T08 stays retired-only; EC-025 appended
after EC-024; no suffixed IDs), and the directed `bcs:` relation re-verified as a clean
bipartite coverage relation (check 8), not a cyclic one.

## 4. Architecture Alignment

Platform path resolution has one home (A03/A12: `platform.Abs(cwd, p string)` in
ARCH-05, `EnvVars` a type alias declared once in `internal/platform`, ARCH-03 uses the
seam without re-declaring it). The metrics-client trio (BC-1.04.001 ↔ ARCH-03 ↔ VP-030)
is coherent over the measured status-100-only skip, urlsplit sanitization and Host-header
bytes (C2-01/02/07). The mix-cache asymmetry is stated consistently across ARCH-03,
ARCH-06 and the owning BCs (check 4). The coverage job is never probe-gated (A04) and
govulncheck's required-check promotion is sequenced after the toolchain line (A06).

## 5. Acceptance Criteria Quality

At spec stage the AC-equivalent surfaces are BC postconditions and VP properties: both
were the objects of the burst. Each remediated BC states testable outcomes with measured
bounds (B04's 8192-byte chunk decode, B05's swallowed stat errors, C2-01's status-100-only
skip with EC-025, D09's 1970-01-02 domain floor, D06/D07/D08's ordering and reason
rules); the for-all properties were walked against those postconditions with no legal
input left that breaks them (check 3).

## 6. Story Sizing

N.A. — Phase 1 precedes story decomposition; no story files exist to size. (Phase 2
will bound stories at ≤ 13 points.)

## 7. Priority Consistency

N.A. at story level (no story dependencies in Phase 1). At spec level the burst
introduces no priority changes: PRD priority columns are untouched by the remediation
diffs, and CP-O12's owners (BC-1.02.029 primary, BC-1.05.003 co-owner) are consistent
with the E-REN-002/NFR-002 carrier lists.

## 8. L1 to L2 to L3 to L4 Chain Completeness

No orphans introduced: the chain anchors verify at every layer touched by the burst —
title quadruple 154/154 (section 8), CP-O12 propagates brief-ward through E-REN-002
into NFR-002 and the parity register (check 6), A2-17's dtu-assessment decode-edge
recount (101 → 72 S1 BCs) keeps the L1/L2-adjacent inventory aligned with the
BC-INDEX census, and the 270-edge VP relation closes with zero residues.

## 9. AC Completeness Coverage

Clause-level reciprocity is maintained: VP-012's closed set gains BC-1.05.009 in both
frontmatter and body (C2-04); C2-05 lifts DI-008 into BC-1.05.004's L2 row beside its
degrade EC; the exclusions.json no-entry rule for OD-76/D4-EX-1 is stated in the owning
register BC (D01) and the sibling probe contract (D02). The VP-INDEX union bijection
(check 8) is the AC-completeness instrument at VP granularity.

## 10. ASM/R Traceability

No ASM/R regressions found in the diff. The burst's only assumption-adjacent edit
closes cleanly: A2-17's inventory recount in `specs/dtu-assessment.md:55` (72 S1 BCs)
and the pass-9 A2-19 disposition note in
`specs/domain-spec/owner-validation-list.md:242-244` keep validation-list and assessment
wording aligned with the logged rulings. Risk-linked knobs are otherwise untouched.

## Cross-Reference Validation

ID-vocabulary and cross-reference repairs verified byte-precise: `not an absolute path`
and `invalid UTF-8` (check 7), CP-O12/`cpt`-family lists (check 6), the row-2 predicate
(check 5), the five measured decode sites (prd §8:616 ↔ BC-5.02.003:181 ↔ ARCH-06:31),
and the section-anchor form for ARCH-03 citations (C2-06, resolving against the
`## Interfaces` heading). No stale count survives as a live claim; stale figures live
only in `modified:` provenance (SC-34).

## Spec vs Implementation Drift

N.A. — P1 spec crystallization precedes implementation (parity-first port not started).
The drift surface monitored at this stage is spec-vs-legacy parity, adjudicated by the
pass-9 perimeters themselves; the measurements this burst pinned (chunk-decode 8192,
status-100-only skip, urlsplit sanitization, the 994/991 mix boundary, the 2026-11-18
oracle re-runs) keep future drift auditable against pinned evidence.

## New sync-check findings

| SC-NN | Severity | File:line | Inconsistency | Owner |
|-------|----------|-----------|---------------|-------|
| SC-33 | Minor | `specs/stderr.txt` (untracked, 0 bytes, not git-ignored) | Stray empty file left in the spec tree by the remediation burst (a redirected-stderr artifact). Harmless but will churn `git status` on the factory branch and invites accidental commit. Remedy: delete the file (it is empty), or add a `specs/stderr.txt` ignore entry if the burst tooling recreates it. | architect |
| SC-34 | Cosmetic | 8 files' newest `modified:` entry: `specs/prd.md:26` (0.2.20), `specs/architecture-feasibility-report.md` (1.13), `specs/verification-properties/VP-007-render-determinism-seams.md` (1.5), `specs/verification-properties/VP-INDEX.md:33` (1.20), `specs/verification-properties/VP-035-corpus-hygiene.md` (1.3), `specs/behavioral-contracts/ss-01/BC-1.07.003.md` (1.0.8), `specs/behavioral-contracts/ss-01/BC-1.03.018.md` (1.3.1), `specs/behavioral-contracts/ss-01/BC-1.03.004.md` (1.2.6) | The pass-9 "residual sweep" history entries are all stamped `2026-11-18T16:52:00Z`, EARLIER than the entry that precedes them in each oldest-first list (e.g. prd 0.2.19 is dated 2026-11-20T18:00Z). Provenance dates are therefore non-monotone; the version field still matches the last entry (SC-26's invariant holds), and the live text is correct. Remedy: none required (history is as-of-its-date per the standing convention); if touched, re-stamp the cluster or annotate "(clock-skew stamp)" beside the 16:52 entries. Observed in the same sweep, not actionable: `specs/dtu-assessment.md` keeps its `modified:` list newest-first (1.12 at top), unlike the oldest-first convention everywhere else — pre-existing style, consistent within the file. | architect |

### Critical

None.

### Major

None.

### Minor

SC-33.

### Cosmetic

SC-34.

## Validation Gate Result

**PASS** — no blocking findings. The pass-9 remediation burst is fully propagated on
disk: all 85 findings verified closed at their cited loci, both burst-wide repairs
(mix-cache asymmetry, row-2 gate) land identically at every named site, CP-O12 and the
49-path register are coherent across thirteen files, the 270-edge `bcs:` bijection with
the VP-INDEX coverage map is exact (0 forward-only, 0 reverse-only), the title
quadruple holds 154/154, every frontmatter parses, and the added lines are
hygiene-clean. SC-33 and SC-34 are non-blocking housekeeping notes.

## Overall Metrics

| Metric | Value |
|--------|-------|
| **Pass-9 findings verified closed** | 85/85 (HIGH 15, MEDIUM 38, LOW 28, COSMETIC 4) |
| **Rejected with evidence** | 0 |
| **Open** | 0 |
| **New sync-check findings** | 2 (SC-33 Minor, SC-34 Cosmetic) |
| **Machine checks** | 10 orchestrated checks executed as scripted batteries + targeted reads; 239 spec files swept, 100-file diff (+1393/−675) reviewed line-wise for hygiene |

## Appendix: Validation Methodology

Fresh-context scripted sweep of the factory worktree's uncommitted spec tree
(`git diff HEAD` under `specs/`, 100 files, +1393/−675). Interpreter
`/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7), scripts in the session
scratchpad (not committed): (1) finding-by-finding anchor battery keyed to
`ADV-P9-INDEX.md` and the remediation plan's calls 1-15 — each PASS requiring an
on-disk regex hit at the locus the fix should occupy, with manual reads adjudicating
every miss; (2) structural battery — BC/VP file counts, `bcs:` edge recount (270),
VP-INDEX coverage-map union regeneration with 0/0 residues, and escape-aware title
quadruple-equality across 154 H1s, BC-INDEX, prd.md §2 and BC-ALLOCATION; (3)
citation-resolution battery (section 2) opening each newly cited target at its target
file and line; (4) for-all property walks against the owning BC postconditions
(section 3), including the logical equivalence check between the rendered-form and
omitted-form row-2 predicates; (5) cross-file wording identity greps for the mix-cache
five and the reason strings; (6) `yaml.safe_load` frontmatter sweep over all 239 files
with raw top-level key counting for `version`/`modified`; (7) hygiene regexes over all
1393 added lines with a full non-ASCII census; (8) provenance-date monotonicity scan
that surfaced SC-34. Manual reads adjudicated every scripted anomaly (the 14 initial
title "mismatches" were row-parser artifacts, re-verified escape-aware at 20/20 clean).
Nothing outside the report path was written; nothing committed.
