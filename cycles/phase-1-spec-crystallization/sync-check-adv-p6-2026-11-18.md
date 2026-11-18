---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass-with-findings"
producer: consistency-validator
timestamp: 2026-11-18T09:11:17Z
phase: 1
inputs: [specs/behavioral-contracts/, specs/verification-properties/, specs/architecture/, specs/domain-spec/, specs/prd-supplements/, specs/prd.md, specs/product-brief.md, specs/cicd-setup.md, specs/dtu-assessment.md, specs/owner-decisions-log-2026-11-14.md, cycles/phase-1-spec-crystallization/pass-6-remediation-plan.md, adversarial-reviews/ADV-P6-INDEX.md]
input-hash: "4f07ae7"
traces_to: ../../STATE.md
---

# Consistency Validation Report: hylo pass-6 fix-burst sync check

## Report Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo (status line + hybrid routing, P1 spec crystallization) |
| **Generated** | 2026-11-18T09:11:17Z |
| **Generator** | consistency-validator (fresh context, scripted checks under `/opt/homebrew/anaconda3/bin/python3 -I` 3.11.7, PyYAML 6.0.2) |
| **Artifacts Scanned** | 156 dirty files vs `c26526e`; 239 spec `.md` files across 7 trees (behavioral-contracts 156 incl. allocation/component-map, verification-properties 42 incl. index, architecture 12, domain-spec 9, prd-supplements 7, research 6, root 7) |

**Scope note.** Fresh-context sync check after the pass-6 fix burst, before adversarial
pass 7. The thirteen orchestrator-declared checks were executed mechanically (scripted
sweeps over the whole spec tree, targeted file reads adjudicating every script hit),
mirroring the pass-5 methodology. Rulings in scope: OD-181..OD-187
(owner-decisions-log:175-183; next free OD-188); calls 1-16 of
pass-6-remediation-plan.md. Read-only on specs; nothing committed. Findings continue
the sync-check numbering lineage (SC-01..20 consumed by passes 3-5).

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | L2 to L3 Requirement Coverage | pass (154/154/154 counts; title triple-equality 154/154; parity_class frontmatter = BC-INDEX parity column 154/154) |
| 2 | L3 to L4 Verification Property Coverage | pass with SC-21 (three new unenumerated reverse edges: VP-019, VP-012, VP-018) |
| 3 | Dependency Acyclicity | n/a — burst-scoped (no story/wave deltas) |
| 4 | Architecture Alignment | pass (120/120 ARCH fragment links resolve; 0 line-number pointers into ARCH docs) |
| 5 | Acceptance Criteria Quality | n/a — burst-scoped (recurs at Phase 2) |
| 6 | Story Sizing | n/a — burst-scoped |
| 7 | Priority Consistency | n/a — burst-scoped |
| 8 | L1 to L2 to L3 to L4 Chain Completeness | pass (154 BC / 41 VP chain intact) |
| 9 | AC Completeness Coverage | n/a — burst-scoped (recurs at Phase 2) |
| 10 | ASM/R Traceability | pass (OD-181..OD-187 logged and propagated; see matrix below for SC-23's VP-009 lag) |

### Burst-sync check matrix (13/13 executed)

| # | Check (orchestrator wording) | Result |
|---|------------------------------|--------|
| 1 | Counts 154 BCs / 41 VPs; titles H1 = BC-INDEX = PRD; parity_class join | PASS — 154 files = 154 BC-INDEX rows = 154 PRD section-2 rows, identical ID sets all three universes; H1 (`# Behavioral Contract BC-x.y.z: …`) = BC-INDEX title = PRD title for 154/154 under escape-aware pipe parsing (the BC-5.03.002 `\n \r\n \r` cell matches verbatim); 41 VP files = 41 catalog rows, class arithmetic invariant 33 + safety 7 + performance 1 = 41, method buckets 20+13+3+2+1+1+1 = 41; `parity_class` frontmatter equals the BC-INDEX Parity-class column for all 154 (distribution: byte-exact 97, n.a. 39, D4-EX-3 6, temp-file 3, D4-EX-2 3, singles OD-161/OD-166/OD-30/OD-76/OD-30+OD-166/D4-EX-1) |
| 2 | VP<->BC links both ways; residue equals VP-INDEX's enumerated exceptions exactly | PASS WITH SC-21 — 254 directed VP→BC `bcs:` edges (exactly the v1.14 claim), 0 forward-only; reverse-only = 9, of which the 6 enumerated exceptions (VP-022/BC-1.06.001, VP-024/BC-1.07.004, VP-034/BC-1.01.004, VP-026 in BC-3.01.001/BC-6.01.002/BC-6.02.003) match the "Uncovered BCs" prose exactly — plus 3 NEW unenumerated pairs (SC-21); VP-INDEX coverage map equals the union of VP `bcs:` sets with 0 diffs (SC-13/SC-14 closed per the union rule) |
| 3 | Closed exclusion set = 12 ids (incl. OD-181); D4-EX-3 = seven classes, five canonical tests | PASS WITH SC-23, SC-25 — complete 12-member sets verified in the carriers of record: VP-012 `TestParityExclusions_ClosedSet` map incl. `"OD-181": true … // TWELVE ids` (VP-012:81-84), error-taxonomy.md:200-201 ("counts twelve ids"), prd.md:562-563 (DI-012 "closed twelve-id set"), ARCH-00-overview.md:33-37 (pass-3 "ten ids" retained only as quoted superseded history), domain-spec/invariants.md:35 (DI-012 with OD-181; :46 count "DI-012 = 76" re-verified: exactly 76 BC files cite DI-012 — ADV-P6-A2-24 correct); sole stale live enumeration is VP-009:10-12 (SC-23) plus one 11-id parenthetical at BC-1.05.004:63-65 (SC-25); D4-EX-3: seven classes with the five canonical tests `TestD4EX3_{Boolean,Enum,URL,Number,Text}` in error-taxonomy.md, BC-2.02.001, ARCH-07, VP-012 — no live four-name list, no live "closed at six" (SC-17 closed; ARCH-INDEX:66's "closed at six, extended to seven" is an accurate historical narrative) |
| 4 | OD-182: every VP Go block carries the non-normative label; 8-VP normative completeness | PASS — 41 fenced Go blocks across the 41 VP files, 41/41 labelled "Illustrative sketch (non-normative, not compiled; OD-182)" within 3 lines above the fence, 0 unlabelled; spot-check of 8 VPs (VP-001, VP-012, VP-016, VP-020, VP-026, VP-034, VP-036, VP-041) confirms the uniform normative scaffold (Property Statement / Source Contract / Property Class and Verification Method / Proof Method / Named Tests) carries property, oracle/reference, method, inputs and pass-fail rule without the sketch — e.g. VP-001's statement pins the full CP-taxonomy ladder and 29-byte/exit-0 rule, VP-036's statement pins the per-case p95 gate with OD-187's CONDITIONAL >512 KB exemption stated as an authored exception that is REPORTED when it fires (A2-19 resolved exactly per the ruling) |
| 5 | OD-183 (PYTHONIOENCODING=utf-8 only, PYTHONUTF8 forbidden) consistent | PASS — BC-6.01.002:115-118 (`PYTHONIOENCODING=utf-8`, stdio only, `PYTHONUTF8` stays forbidden, builder strips every PYTHON* except PYTHONPATH), :128, :156 (EC-002), :169; ARCH-07:79-87 (changes stdio encoding and nothing else; Windows only); VP-034:44-55, :102-110, :143-144 (table-test leg); BC-1.01.008:53 (OD-183 stdio leg), :68/:98 (PYTHONUTF8 surrogateescape is NOT the parity mode); BC-1.06.001:73 (changes stdio encoding, not file reads); BC-1.07.003:75 consistent; no contradictory wording anywhere (research/ PYTHONUTF8 mentions are pre-OD-183 research artifact provenance) |
| 6 | OD-184 glyph rule (1 code point; sparkline 8; EAW only for pill labels) consistent | PASS — BC-2.01.004:111-115 (code points, legacy's render width; sparkline exactly 8 ordered), :140 (`watts` ⚡ EAW-W does NOT violate), :156-159 (validation width NOT applied to glyph members; pill-label 1..16 only), :193-204 (OD-170 width function; `中文` measures 4 grounding per call 15); BC-2.01.005:121-129 (enforced rule is the code-point count, not a terminal-column check); interface-definitions.md:219-223, :266 (subagent glyphs + 27-member family row); ARCH-06:210-232 (render width vs validation width split; superseded OD-02 wording named); consumer BCs swept: BC-1.02.001:69-70, BC-1.02.005:72, BC-1.02.006:67, BC-1.02.018:73-74 — all on the OD-184 canon |
| 7 | OD-185: no live "3.11.7 exact" pin; self-check described | PASS — withdrawal stated at ARCH-08:64-68 ("the pass-5 exact-3.11.7 pin is WITHDRAWN… harness SELF-CHECKS… fail closed, printing the resolved version"), cicd-setup.md:160-166, BC-6.01.001 PC-4 (:75-86), BC-6.04.001 PC-3.3 (:78-81), VP-006:95-97 and :138-147 (re-measure flip depths 993/992 on the resolved oracle, fail closed), VP-023:54-55 and :115-118 (unidata_version self-check), NFR-003 (nfr-catalog.md:28 dual pin), ASM-001 (assumptions-register.md:23, dual-pin scope + self-check), prd.md:624-625; every remaining 3.11.7 occurrence is provenance/attestation ("measured"/"verified on CPython 3.11.7") or the withdrawal notices — 0 live exact pins |
| 8 | OD-186: rename retry = 3 attempts total; key `statusline.cache.rename_retry_delay_ms` consistent | PASS WITH SC-24 — ARCH-04:62-78 ("the INITIAL rename attempt plus `renameRetryLimit = 2` retries — three attempts in total, the one consistently" stated number; key registered, default 10), VP-018:48-51 and :97-124 ("exactly renameRetryLimit = 2 times — one initial attempt plus two retries, THREE…; `fails := renameRetryLimit + 1 // 3 attempts: initial + 2 retries (OD-186 single count)`"), BC-6.03.003:59-61 (same canon), BC-2.01.004:228-235 (PC-11 registry row: Int, default 10, range 1..1000, env `HYLO_STATUSLINE_CACHE_RENAME_RETRY_DELAY_MS`, attempt count stated once), interface-definitions.md:173 — all consistent; sole residue BC-1.06.001:117 EC-009 still reads "2-3 short retries" (SC-24) |
| 9 | Windows localtime signatures (call 2) consistent | PASS WITH SC-22 — ARCH-06:188 `LocalToUnix(fields Naive, loc *time.Location, msvcDomain bool) (int64, error)` with distinct `ErrLocaltimeDomain` (matches call 2 verbatim; :239-242 canon sentence), ARCH-05:34 (failure rule homed in PURE pyfmt, `internal/statusline` injects `msvcDomain = platform.IsWindows()`, epoch-negative/year-3001 probes, no exclusion id), ARCH-03:66 step-2 row (Windows MSVC OSError degrade, pass-6 C01), BC-5.04.002:38/:44 (full 3-arg signature + sentinel), BC-1.03.010:49-50/:107 (ErrLocaltimeDomain distinct from ErrValue; EC-008), BC-1.03.018:122 (Inv3) — consistent; one drift: ARCH-06:188 spells `FromISOFormat(s string, loc *time.Location)` while BC-5.04.001:40 carries `FromISOFormat(s, loc, msvcDomain bool) (float64, error)` (SC-22) |
| 10 | Metrics client (call 4) + ModeBytes/992/993 (call 5) consistent | PASS — BC-1.04.001:55-136 (minimal HTTP/1.1 client over `net.Conn`, plain http only per OD-181; exact urllib header set and order; empty `Location` resolves by `urljoin` of the CURRENT hop's URL — `urljoin(B, "")` returns B; 37 = worst-case chain "NOT a hop counter/budget", visited/max_repeats/max_redirections are the rule) agrees with ARCH-03:184-210 point for point; metrics reply decode: ModeBytes + 992/993 pinned in ARCH-03:214 (`Decode(b, ModeBytes, depthMetricsReply = 992)`), ARCH-06 (ModeText/ModeBytes consts, :157), BC-5.02.003:53-54 (PC-3 rider, multi-line body case per call 5), BC-5.02.004:100 (VP-006 row added, A2-17 reciprocal), VP-006:123 (harness row `{"metrics reply (get_sample → fetch_sample)", pyfmt.ModeBytes, 992, 992, 993}`) |
| 11 | Depth values: session save 991; subagent SL:924 991; metrics reply 992/993; decoders as pinned | PASS — encoder law 995 − s (json.dump) / 994 − s (json.dumps) stated identically (ARCH-03:168-169, ARCH-06:52-53, BC-5.02.001:25, BC-5.02.003:27, BC-5.02.006:28); decoder law 999 − F (ARCH-06:48/:162, ARCH-07:112); per-site budgets: stdin/transcript 993/994 (BC-1.01.002:88-89, BC-5.02.003:83-99, VP-006 table), session/mix save 991 equal budgets (ARCH-03:174, ARCH-06:82, BC-5.02.003:105-111, BC-5.02.006:111, VP-006:52-53), git/cost 990/990 (ARCH-06:72, :82); NEW subagent SL:924 row 991 (BC-5.02.006:97 PC-6 table, D08 fix, attainability argument :117-124; BC-1.07.004:62-68 PC4); metrics reply 992/993 everywhere as in check 10; pass-5 D08-era budgets survive only as supersession prose (ARCH-06:76) |
| 12 | Frontmatter parses (PyYAML + duplicate keys), version = last modified, modified ascending; ARCH links resolve; no ARCH line pointers | PASS WITH SC-26, SC-27 — 232/239 frontmatters parse; the 7 without frontmatter are the rulings log (starts with an HTML comment, by design) and 6 research documents (by design); 0 duplicate keys; version equals the last modified entry in all version-prefixed histories (SC-19 closed — apparent lags were timestamp-leading entry spellings, adjudicated); ordering: 4 files carry history-order defects (SC-26, SC-27 — SC-20 closed for VP-INDEX whose 1.12 re-date is in place); 120 `ARCH-*.md#fragment` references across BCs/VPs/supplements/root resolve 120/120 against `<a id>` anchors or heading slugs (0 unresolved); 0 line-number pointers into ARCH docs from any BC or VP body (SC-18 closed; VP-006's former pointer now an anchor) |
| 13 | Hygiene: IPs, home paths, emails, session links, non-English prose | PASS — 0 non-allowlisted IPv4 literals (sole hit 127.0.0.0 in a BC-6.02.001 test vector: loopback class); 0 emails; 0 session links; home-ish matches are bare `~/` examples plus the sanctioned `/home/user` synthetic; 33 block-script occurrences outside fences are all intentional Unicode test data or their provenance (`中文`/`漎字`/`Λ.titleLabel`-family width vectors, Arabic-Indic `٤ ٢ ٢ ٨٠ ١` numeral vectors, `日本` filename rows) — no non-English prose |

## 1. L2 to L3 Requirement Coverage

154 BC files = 154 BC-INDEX rows = 154 PRD section-2 rows with identical ID sets.
Title triple-equality holds for all 154 contracts; the pass-6 wording changes did not
retitle any contract. The parity-class frontmatter↔index join is exact for all 154,
including the pass-6 remap BC-1.06.001 → `temp-file` (feasibility-report v1.11 residual
sweep) which matches both the frontmatter and the BC-INDEX column.

## 2. L3 to L4 Verification Property Coverage

The VP weave is at its cleanest since pass 2: 254 directed edges, 0 forward-only, and
the VP-INDEX coverage map now equals the VP `bcs:` sets exactly (0 map diffs; SC-13
closure verified, including the BC-1.05.007 and BC-1.07.007 map rows and VP-012's
BC-1.04.003/BC-1.05.005 reciprocity). The v1.14 "exactly the residue" claim is short by
three prose citations the enumeration does not cover:

- **SC-21:** BC-1.01.009:58 cites VP-019 ("Python-written cost history (VP-019 swap)"),
  BC-1.06.001:40 cites VP-012 ("validated by the VP-012 closure check"), and
  BC-2.01.004:195 cites VP-018 (OD-186 key cross-reference) — none of the three VPs
  lists the citing BC in `bcs:`, and none of the three pairs appears in the
  "Uncovered BCs" residual prose. Same resolution class as v1.11: add the BCs to the
  respective `bcs:` (reciprocity preferred) and regenerate the map rows, or enumerate
  the three pairs as residuals.

## 3. Dependency Acyclicity

No story/wave inputs in delta; the burst introduces no ordering constraints. Recurs at
story decomposition.

## 4. Architecture Alignment

All 120 `ARCH-*.md#fragment` references from BCs/VPs/supplements/root resolve. The
pass-6 signature canon (call 2) is propagated through ARCH-03 step 2, ARCH-05:34,
ARCH-06's file table and signature block, BC-5.04.001/.002, BC-1.03.010 and
BC-1.03.018 — one arity drift between the ARCH-06 signature block and BC-5.04.001
(SC-22). VP-026's harness sketch still shows the pre-call-2 two-argument
`LocalToUnix(g.Loc, g.Wall)` shape (cosmetic per OD-182; VP-026 was not on call 2's
propagation list).

## 5. Acceptance Criteria Quality

Not in delta scope — no story files in the burst. Recurs at Phase 2.

## 6. Story Sizing

Not in delta scope — no story files in the burst.

## 7. Priority Consistency

Not in delta scope — no story files in the burst.

## 8. L1 to L2 to L3 to L4 Chain Completeness

| Level | Artifact | Count | Traced Forward | Traced Backward | Coverage |
|-------|----------|-------|----------------|-----------------|----------|
| L1 | Product Brief | 1 | yes | N/A | 100% |
| L2 | Domain Spec (capabilities, invariants, state machines) | 9 files | to L3 | to L1 | 100% |
| L3 | Behavioral Contracts (BC-S.SS.NNN) | 154 | to L4 | to L2 | 100% |
| L4 | Verification Properties (VP-NNN) | 41 | N/A | to L3 | 100% |

No broken chains or orphaned levels in the burst.

## 9. AC Completeness Coverage

Not in delta scope (no story ACs). BC-clause-level reverse coverage recurs at Phase 2.

## 10. ASM/R Traceability

OD-181..OD-183 and OD-185..OD-187 are propagated per the matrix (checks 3, 5-8, 10-11).
OD-184's glyph rule is coherent across the registry BC, the validation BC, the interface
registry, ARCH-06's two-width doctrine and every consumer BC (check 6). The closed-set
widening to 12 ids is discharged at the carriers of record (VP-012 test map,
error-taxonomy, prd DI-012, ARCH-00, invariants) but VP-009's live property statement
still enumerates the predecessor set (SC-23). ASM-001 reflects the OD-185 dual-pin and
self-check; R-004's mitigation row unchanged.

## Cross-Reference Validation

### ID Consistency

| Check | Status | Issues |
|-------|--------|--------|
| BC/VP/CAP IDs unique | pass | none observed in delta |
| BC ↔ CAP / VP ↔ BC traces | pass | 254 edges; 6 enumerated + 3 new reverse residues (SC-21) |
| Rulings | pass | OD-181..OD-187 logged (owner-decisions-log:177-183); next free OD-188 |
| Closed-set membership | pass | 12/12 at the carriers of record; SC-23/SC-25 stale enumerations |
| D4-EX-3 register | pass | seven classes / five canonical tests in all live registers |

### Naming Convention Compliance

| Convention | Expected Pattern | Violations |
|-----------|-----------------|------------|
| BC naming | BC-S.SS.NNN | none |
| VP naming | VP-NNN | none |
| OD numbering | OD-NNN sequential to 187 | none |
| Go symbols in spec prose | `LocalToUnix`/`ErrLocaltimeDomain`/`FromISOFormat`/`renameRetryLimit`/`ModeBytes` | none beyond SC-22's arity drift |

## Spec vs Implementation Drift

No Go implementation exists yet (P1 spec crystallization; code begins after the spec
gate). The only executable referent is the frozen legacy Python oracle. Burst-scoped
disposition unchanged from pass 5: parity obligations pinned to the legacy oracle,
VP skeletons specified with vehicles landing with stories, measured constants
(depth limits, Unicode 14.0 tables) taken on 3.11.7 and now guarded by the OD-185
fail-closed oracle self-check in lieu of a version pin.

## Findings

| SC-NN | Severity | File:line | Inconsistency | Owner agent |
|-------|----------|-----------|---------------|-------------|
| SC-21 | Major | `specs/behavioral-contracts/ss-01/BC-1.01.009.md:58` (VP-019), `specs/behavioral-contracts/ss-01/BC-1.06.001.md:40` (VP-012), `specs/behavioral-contracts/ss-02/BC-2.01.004.md:195` (VP-018) | Three one-sided VP↔BC edges, unenumerated: each BC body cites the VP, the cited VP's `bcs:` excludes the BC, and the VP-INDEX "Uncovered BCs" residual prose (v1.14, claiming the lists "are therefore exactly the residue") does not list the pairs. Same class the v1.11 pass closed by reciprocity. Remedy: add BC-1.01.009 to VP-019 `bcs:`, BC-1.06.001 to VP-012 `bcs:`, BC-2.01.004 to VP-018 `bcs:` and regenerate the map rows — or enumerate the three pairs as residuals. | architect |
| SC-22 | Major | `specs/architecture/ARCH-06-pyfmt.md:188` vs `specs/behavioral-contracts/ss-05/BC-5.04.001.md:40` | FromISOFormat arity drift: the ARCH-06 canonical signature block spells `FromISOFormat(s string, loc *time.Location) (float64, error)` (2-arg) while BC-5.04.001 (v1.2.4, ADV-P6-D06/call 2) spells `FromISOFormat(s, loc, msvcDomain bool) (float64, error)` (3-arg, msvcDomain threaded to LocalToUnix). An implementer of the ARCH-06 block cannot produce the BC's ErrLocaltimeDomain-outcome contract for naive timestamps on Windows. Remedy: add the `msvcDomain bool` parameter to ARCH-06:188 (ARCH-06:33's prose row already attributes the error-result canon, so only the signature line lags). | architect |
| SC-23 | Major | `specs/verification-properties/VP-009-tier-a-live-parity.md:10-12` | The Tier-A property statement still enumerates the closed exclusion set with ELEVEN ids ("…OD-159, OD-160, OD-161, OD-166) carving out ruled differences") — OD-181 (12th id, "metrics transport beyond plain http") is absent from the file entirely. VP-012, error-taxonomy, prd.md DI-012, ARCH-00 and invariants.md all carry the 12-id set. An implementer running Tier A would fail lawful OD-181 diffs. Remedy: extend the parenthetical to the 12-id set and bump the modified history. | architect |
| SC-24 | Minor | `specs/behavioral-contracts/ss-01/BC-1.06.001.md:117` | EC-009 reads "2-3 short retries, then swallow (design IM-17)" — inconsistent with the OD-186 single-count canon ("three attempts total, initial attempt + two retries") stated identically in ARCH-04:62-64, VP-018:49-51, BC-6.03.003:60-61 and BC-2.01.004:233. "2-3 retries" is neither the same number nor the same initial-vs-retry articulation. Remedy: respell to "three attempts total (initial attempt plus two retries)". | product-owner |
| SC-25 | Minor | `specs/behavioral-contracts/ss-01/BC-1.05.004.md:63-65` | The live OD-166 postcondition parenthetical enumerates the closed set at its pre-OD-181 state (11 ids, "the 11th id of the closed set — D4-EX-1 … OD-166"). The ordinal ("11th") remains true, but the set-presenting list lacks OD-181 and was not swept when the file's siblings were updated in pass 6 (file's history stops at v1.2.6, pass 5). Remedy: extend the parenthetical or rephrase to cite DI-012's set without re-listing it. | product-owner |
| SC-26 | Minor | `specs/architecture-feasibility-report.md` (frontmatter `modified:`) | History is ordered newest-first (1.11@2026-11-19 precedes 1.10@2026-11-18, then 1.9 …), against the factory-wide oldest-first convention whose repair the sibling files performed ("re-spun oldest-first so the version field matches the last entry", BC-6.03.003 v1.2.6). Content-safe; defeats "newest entry last" readers and monotonicity tooling. Remedy: reverse the list on the next wording touch. | architect |
| SC-27 | Minor | `specs/behavioral-contracts/ss-02/BC-2.02.006.md` (frontmatter), `specs/behavioral-contracts/ss-06/BC-6.03.004.md` (frontmatter), `specs/verification-properties/VP-012-exclusion-set-closure.md` (frontmatter) | Local timestamp dips inside otherwise-ascending histories: BC-2.02.006 (1.2.2@11-18 → 1.2.3@11-17), BC-6.03.004 (1.2.2@11-18T01:42 → (1.2.3)@11-18T00:00), VP-012 (1.3@11-18T09:04 → 1.4@11-18T02:24). SC-20 class, smaller blast radius (three files, vs 13 at pass 5). Remedy: re-stamp or reorder the dipping pairs on the next wording touch. | product-owner (BCs), architect (VP-012) |
| SC-28 | Cosmetic | `specs/verification-properties/VP-026-pyfmt-time-equivalence.md:96` | Harness sketch calls `pyfmt.LocalToUnix(g.Loc, g.Wall)` — the pre-call-2 two-argument shape; the canon is `LocalToUnix(fields, loc, msvcDomain bool) (int64, error)`. Sketch-only API-spelling defect: cosmetic per OD-182 (VP-026 was not on call 2's propagation list). Remedy: update the sketch alongside the next VP-026 edit. | architect |

### Critical

None. The headline invariants are machine-clean: 154/41 counts and title
triple-equality with the exact parity-class join, 254-edge VP weave with 0
forward-only edges and an index map in exact agreement, 41/41 OD-182 labels, the
OD-183/OD-184/OD-185/OD-186 ruling chains, the end-to-end depth reconciliation
(laws, per-site budgets, the new SL:924 row), the call-2 localtime signatures in five
of six locales, 120/120 anchor resolution, zero line-number pointers, zero duplicate
keys, and public-repo hygiene.

### Major

- **SC-21** — three new one-sided VP citations unenumerated against VP-INDEX's "exactly the residue" claim.
- **SC-22** — FromISOFormat arity drift between the ARCH-06 signature block and BC-5.04.001.
- **SC-23** — VP-009's live property statement on the pre-OD-181 11-id closed set.

### Minor

- **SC-24** — BC-1.06.001 EC-009 retry wording off the OD-186 single count.
- **SC-25** — BC-1.05.004's 11-id parenthetical.
- **SC-26/SC-27** — four modified-history ordering defects (one newest-first list, three timestamp dips).

### Cosmetic

- **SC-28** — VP-026 sketch shape vs the call-2 signature canon.

## Validation Gate Result

**PASS-WITH-FINDINGS** — no blocking (Critical) findings. SC-21..SC-23 are
single-block propagation repairs (three `bcs:` additions plus map-row regeneration, one
signature parameter, one parenthetical) and should ride the pre-pass-7 preparation
burst, ideally with the SC-15 experience in mind: index-regeneration and adversary
parsers consume exactly these anchors. SC-24..SC-28 are one-line respells that may ride
the next wording touch of their files.

## Overall Metrics

| Metric | Value |
|--------|-------|
| **Total Checks** | 13 burst-sync + 10 standing categories |
| **Passed** | 13 + 5 standing pass |
| **Failed** | 0 |
| **Warnings** | 8 (SC-21..SC-28: 3 Major, 4 Minor, 1 Cosmetic) |
| **Overall Status** | inconsistencies-found (localized; none blocking) |

Compared with pass 5 the residue moved shape rather than shrinking: every pass-5
finding (SC-13..SC-20) is verified closed, and the pass-6 burst's own fixes are almost
perfectly propagated — the three Majors are all edges the burst created or widened
(the OD-186 cross-reference in BC-2.01.004, the VP-012 reciprocity rule extended to
BC-1.06.001 prose, and the call-2 signature which reached BC-5.04.001 but stopped one
parameter short of the ARCH-06 canon block), plus VP-009, whose property statement is
the one live carrier the OD-181 widening did not reach. Pass 6's novelty decline
(148 → 124 findings) is corroborated by the sync surface: nothing structural moved.

## Appendix: Validation Methodology

Fresh-context scripted sweep over the factory worktree at baseline `c26526e` (156 dirty
files). Interpreter `/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7, PyYAML
6.0.2), matching the cycle convention. Scripts (scratchpad, not committed):
(1) structural pass — count and title joins across the 154 BC files, BC-INDEX rows and
PRD section-2 rows with escape-aware (`\|`) pipe-table parsing and the
`# Behavioral Contract BC-x.y.z:` H1 normalization; parity_class↔BC-INDEX column join;
VP `bcs:` YAML extraction versus BC-body `VP-\d+` citation sets (frontmatter filtered,
fenced code flattened) yielding the directed-edge bijection, its residue, and a
VP-INDEX coverage-map regeneration cross-check; frontmatter parse + duplicate-key
loader + version/modified joins + chronological-order check; ARCH fragment-link
resolution via `<a id>`/heading-slug reduction; line-pointer sweep; hygiene regexes;
relpath+size MD5 sweep digest `19ee958`. (2) rulings pass — closed-set
enumeration-site detection (±2-line sentinel windows over 12-id membership, plus a
stale-count sweep for ten/eleven/ten-id live text), D4-EX-3 register sweep,
OD-182 fenced-block labelling over all 41 VPs plus section-presence scaffolds, targeted
extractions for OD-183 (PYTHONIOENCODING/PYTHONUTF8), OD-184 (width doctrine),
OD-185 (3.11.7 pin sweep + self-check), OD-186 (rename-retry canon), call-2
(localtime symbols), calls 4-5 (metrics client, ModeBytes/992/993), and the depth
numeral field (989-995 co-occurrence with depth/budget context). Manual reads
adjudicated every scripted hit: the BC-5.03.002 title "mismatch" (parser ate the
literal `\n` escapes — title is clean), eight apparent version lags (entries whose
version token trails the timestamp — all consistent), the four ordering defects (real,
SC-26/SC-27), the three unenumerated VP pairs (real, SC-21), and the two signature
spellings of FromISOFormat (real, SC-22). All 239 spec `.md` files under
`.factory/specs` were read by script; targeted manual reads
covered 34 files. Nothing outside the report path was written.
