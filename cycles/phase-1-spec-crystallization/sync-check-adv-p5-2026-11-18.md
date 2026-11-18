---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass-with-findings"
producer: consistency-validator
timestamp: 2026-11-18T12:00:00Z
phase: 1
inputs: [specs/behavioral-contracts/, specs/verification-properties/, specs/architecture/, specs/domain-spec/, specs/prd-supplements/, specs/prd.md, specs/product-brief.md, specs/cicd-setup.md, specs/dtu-assessment.md, specs/owner-decisions-log-2026-11-14.md, cycles/phase-1-spec-crystallization/pass-5-remediation-plan.md, adversarial-reviews/ADV-P5-INDEX.md]
input-hash: "3e2faae"
traces_to: ../../STATE.md
---

# Consistency Validation Report: hylo pass-5 fix-burst sync check

## Report Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo (status line + hybrid routing, P1 spec crystallization) |
| **Generated** | 2026-11-18T12:00:00Z |
| **Generator** | consistency-validator (fresh context, scripted checks under `python3 -I` 3.11.7, PyYAML) |
| **Artifacts Scanned** | 131 dirty files vs `f920d7f`; 239 spec `.md` files across 7 trees (behavioral-contracts 156 incl. allocation/component-map, verification-properties 42 incl. index, architecture 12, domain-spec 9, prd-supplements 7, research 6, root 7) |

**Scope note.** Fresh-context sync check after the pass-5 fix burst and its post-burst
corrections (plan call 3 as CORRECTED: `fade = [base, span]`), before adversarial pass 6.
Delta validation per orchestrator instruction — the eleven orchestrator-declared checks
were executed mechanically (scripted; no manual sampling) plus the standing 10-category
summary. Rulings in scope: OD-176..OD-180 (owner-decisions-log:169-173; next free OD-181).
Read-only on specs; nothing committed. Findings continue the sync-check numbering
lineage (SC-01..12 consumed by passes 3-4).

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | L2 to L3 Requirement Coverage | pass (154/154/154 counts; title triple-equality clean incl. the two retitled contracts) |
| 2 | L3 to L4 Verification Property Coverage | pass with SC-14 (two new unenumerated VP-012 reverse edges) |
| 3 | Dependency Acyclicity | n/a — burst-scoped (no story/wave deltas) |
| 4 | Architecture Alignment | pass (301/301 ARCH anchors resolve) |
| 5 | Acceptance Criteria Quality | n/a — burst-scoped (recurs at Phase 2) |
| 6 | Story Sizing | n/a — burst-scoped |
| 7 | Priority Consistency | n/a — burst-scoped |
| 8 | L1 to L2 to L3 to L4 Chain Completeness | pass (154 BC / 41 VP chain intact) |
| 9 | AC Completeness Coverage | n/a — burst-scoped (recurs at Phase 2) |
| 10 | ASM/R Traceability | pass (OD-176..OD-180 logged; closed-set exclusion promises discharged) |

### Burst-sync check matrix (11/11 executed)

| # | Check (orchestrator wording) | Result |
|---|------------------------------|--------|
| 1 | Counts: 154 BCs (files = BC-INDEX rows = PRD rows), 41 VPs (files = VP-INDEX; class arithmetic), titles H1 = BC-INDEX = PRD | PASS — 154 = 154 = 154, no orphans either direction; 41 VP files = 41 catalog rows; class arithmetic invariant 33 + safety 7 + performance 1 = 41, method buckets 20+13+3+2+1+1+1 = 41; H1 = BC-INDEX = PRD section-2 for all 154 (0 mismatches, escape-aware pipe parsing) — both pass-5-retitled contracts verified in sync: BC-1.05.007 "$, $/h and ⛏ number formatting" and BC-3.01.001 "Per-OS cache/config/state dirs …; LocalZone TZ resolution (OS zone, UTC on empty/unparseable)" |
| 2 | VP↔BC links both ways; one-sided links vs VP-INDEX exceptions | PASS WITH SC-14 — 237 directed VP→BC `bcs:` edges (YAML-parsed); forward-only = 0; reverse-only = 8, of which 6 are VP-INDEX-enumerated (VP-022/BC-1.06.001, VP-024/BC-1.07.004, VP-034/BC-1.01.004, and the three VP-026 removal cross-refs) and 2 are NEW unenumerated residuals: BC-1.04.003→VP-012 and BC-1.05.005→VP-012 (SC-14). The v1.9/v1.10 pass-4-sync residuals held: VP-001/BC-1.01.002 edge removed on both sides (SC-05 closed); BC-1.01.009 gained its VP-022 row and BC-1.07.003 its VP-006 row, so the "owed" reciprocals of A2-19 were delivered |
| 3 | Closed exclusion set = 11 ids wherever enumerated; D4-EX-3 = seven classes with five canonical tests everywhere listed | PASS WITH SC-17 — 13 enumeration sites detected, all carrying the complete 11-id set {D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161, OD-166} incl. the p4-lagging VP-009:41 (SC-06 closed); sole live "ten ids" text is ARCH-00:35's quoted superseded description; class register closed at SEVEN with the five canonical tests `TestD4EX3_{Boolean,Enum,URL,Number,Text}` in error-taxonomy.md, BC-2.02.001, ARCH-07 and VP-012 — one stale live row remains at BC-1.01.009:111 ("closed at six", four-name list) (SC-17) |
| 4 | Glyph registry: canonical 27-member list identical in BC-2.01.004 and interface-definitions.md; every `glyphs.<name>` used is a member; renames applied; no live `glyphs.reroute`/`glyphs.stale` | PASS — 27 = 27 members, sets identical (tools … sparkline ramp); renames cache_read/cache_rebuild applied in both carriers with "not shipped, no alias" provenance; the only `glyphs.reroute`/`glyphs.stale` occurrences are BC-1.02.018:23's modified-history rename note; all non-registry `glyphs.<name>` matches are the legitimate `statusline.subagent.glyphs.*` family (running/unknown/killed/failed/completed). Observation (cosmetic, no action required): the `lane` subagent-tag legacy annotation reads SL:906-907 in interface-definitions.md:263 and SL:902-903 in BC-2.01.004:125 — both inside the legacy lane-build block (legacy/dgx_statusline.py:904-907); harmonize on the next wording touch |
| 5 | Keys ruled/minted in pass 5 agree between interface-definitions.md, BC-2.01.004/BC-2.01.005 and consumer BCs | PASS WITH SC-16 — `statusline.lane.reroute_all_prefixes` (OD-179) registered identically in interface-definitions.md:169, BC-2.01.004:172-173 and consumer BC-1.02.009:48-49/113-114/167 (default `["claude", "claude-"]`, legacy; every entry non-empty, no control bytes); `preempt_marker_above` Float >= 0 default 0 agreed (interface-definitions.md:260, BC-2.01.004 PC-8); composite shapes agreed between interface-definitions.md:121-145/209/261 and BC-2.01.005:88-100 — scale `[k_top, v_floor, f_floor, other]` each finite > 0, colors `fade = [base, span] = [0.55, 0.45]` with the corrected `base + span·i/max(n-2, 1)` law per legacy SL:683 (call 3 as corrected), IntMap `cc`/`other` int64 no-extra-keys, bands pairs with no ratified ordering; `context.cells` out-of-range = config error never clamp agreed (interface-definitions.md:191, BC-1.02.006 v1.6); but the four call-16 keys are absent from the registry BC (SC-16) |
| 6 | Encoder/decoder depth values agree across ARCH-03, ARCH-06, BC-5.02.001, BC-5.02.003, BC-5.02.006, VP-006 | PASS — law 995 − s (json.dump) / 994 − s (json.dumps) stated identically in ARCH-03:164-165, ARCH-06:52-53, BC-5.02.001:93-99, BC-5.02.003:96, BC-5.02.006:81; session/mix save 991/991 and git/cost 990/990 equal budgets (ARCH-03:160-162, BC-5.02.006:109, VP-006 per-site table 51-56); metrics reply 992/993 measured and pinned (VP-006:50 and :112, modified 1.6 per ADV-P5-A2-05) with the decoder law 999 − F coherent in ARCH-06:48 and VP-006:40; "993 − W" survives only as supersession prose (ARCH-06:77 negation; BC-5.02.001:24 and BC-5.02.006:27 modified history) — no live occurrence |
| 7 | TZ rule (OD-177) consistent | PASS — unset → OS zone; empty/unparseable → UTC stated in BC-3.01.001:72-80 (PC-6 with EC-009/EC-011 table legs), ARCH-05:33/76-77, VP-026:46-49 (table test with REAL unset via `os.Unsetenv`, :99-121); BC-5.04.001:48 routes Env.Loc through `internal/platform.LocalZone` (BC-3.01.001 PC-6, OD-171) without restating, and both harness BCs pin `TZ=UTC` for both binaries (BC-6.01.002:70-74, BC-6.02.003:153-160, with the LocalZone verdicts delegated to BC-3.01.001) — no contradictory wording found |
| 8 | Test names: OD-30 and OD-166 riders | PASS — `TestCostHistory_OD30_NumericSidStringKey` and `TestCostHistory_OD166_RecordGuard` are the only OD-numbered CostHistory spellings anywhere in specs (BC-1.05.004, BC-1.05.006, BC-1.05.009, VP-012, VP-020, VP-INDEX); no fossils of the pre-canon names |
| 9 | Frontmatter: parses (PyYAML), no duplicate keys, version = last modified entry, modified dates monotonic | PASS WITH SC-15, SC-19, SC-20 — 239 files; 0 duplicate top-level keys; 4 unparseable frontmatters, all introduced by pass-5 edits (SC-15); version-vs-last-modified lag persists/recurs in 3 files (SC-19); out-of-order modified histories in 13 files (SC-20). The two p4-breaking files (BC-4.01.002, BC-6.04.001, SC-07/SC-08) now parse clean |
| 10 | Every `ARCH-*.md#fragment` link resolves; no line-number pointers into ARCH docs from BCs | PASS WITH SC-18 — 301 live fragment links from BCs/VPs/ Supplements into ARCH docs, 301 resolve (`<a id>` or heading slug), 0 unresolved; exactly one live line-number pointer from a BC remains (SC-18); VP-006:32 additionally cites ARCH-04:43 (VP-side, outside the call-19 letter — observation) |
| 11 | Hygiene: IPs, home paths, emails, session links, non-English prose | PASS — 0 non-allowlisted IPv4 literals (all 192.0.2.x / loopback / doc ranges), 0 emails, 0 session links; home paths are the synthetic `/home/user` shapes only; all block-script text is intentional Unicode test data (CJK width vectors, Arabic-Indic digits, 日本語/中文 rows) or ruled identifiers |

## 1. L2 to L3 Requirement Coverage

Counts verified mechanically: 154 BC files = 154 BC-INDEX rows = 154 PRD section-2 rows,
identical ID sets in all three universes. H1-title triple-equality (file H1 = BC-INDEX
title = PRD title) holds for all 154 contracts under escape-aware (`\|`) pipe-table
parsing; the two contracts whose titles changed this pass — BC-1.05.007 (ADV-P5-C2-19
H1 completion) and BC-3.01.001 (ADV-P5-D24 H1/postcondition alignment) — match all three
representations exactly.

## 2. L3 to L4 Verification Property Coverage

41 VP files regenerate into VP-INDEX (v1.10) with exact class and method arithmetic. The
VP↔BC weave is directionally complete (0 forward-only edges) and reverse-side clean
modulo the enumerated exceptions plus two new residues:

- **SC-14 (unenumerated new reverse edges):** BC-1.04.003:122 and BC-1.05.005:128 gained
  VP-012 rows in this pass (ADV-P5-C2-17 "DI-012 + VP-012 closure citations"), but
  VP-012's `bcs:` frontmatter (19 entries) excludes both BCs, and the VP-INDEX residual
  prose (regenerated 2026-11-18T23:45:00Z, claiming one-sided residuals "enumerated
  explicitly") does not list them. By the same standard applied to VP-022/VP-006 in
  v1.7-v1.10, VP-012 `bcs:` gains BC-1.04.003 and BC-1.05.005 and the map rows follow —
  or the prose enumerates the residue.

## 3. Dependency Acyclicity

No dependency-graph inputs (stories, waves) exist in the delta; the burst introduced no
ordering constraints. Full sweep recurs at story decomposition.

## 4. Architecture Alignment

All 301 `ARCH-*.md#fragment` references across the spec tree resolve against `<a id>`
anchors or heading slugs. Call 19's line-number-anchor conversion is one residue short of
complete (SC-18). The depth-law statements newly propagated into ARCH-03:160-170 are
internally consistent with ARCH-06's measured per-site table and the owning BCs (check 6
above).

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

No broken chains and no orphaned levels introduced by the pass-5 burst.

## 9. AC Completeness Coverage

Not in delta scope (no story ACs in the burst). BC-clause-level reverse coverage
(criteria 34-41) recurs at Phase 2 decomposition.

## 10. ASM/R Traceability

Delta scope: OD-177's refinement of OD-171 is propagated coherently across the LocalZone
chain (check 7); OD-179's key minting and OD-178's class register are propagated except
for the SC-16 registry gap and the SC-17 stale row; OD-176 (process) and OD-180 (userinfo
dead rung, no exclusion id) introduce no cross-document surface. The closed exclusion set
promise of OD-169 ("11 ids everywhere") is now discharged at all 13 enumeration sites.
No ASM status changed in the burst.

## Cross-Reference Validation

### ID Consistency

| Check | Status | Issues |
|-------|--------|--------|
| BC/VP/CAP IDs unique | pass | none observed in delta |
| BC ↔ CAP / VP ↔ BC traces | pass | directional-complete; 6 enumerated + 2 new reverse residues (SC-14) |
| Rulings | pass | OD-176..OD-180 logged (owner-decisions-log:169-173); next free OD-181 |
| Closed-set membership | pass | 11/11 at all 13 sites |
| D4-EX-3 register | pass | seven classes / five canonical tests in all registers except SC-17 |

### Naming Convention Compliance

| Convention | Expected Pattern | Violations |
|-----------|-----------------|------------|
| BC naming | BC-S.SS.NNN | none |
| VP naming | VP-NNN | none |
| Rider test names | canonical call-15 spellings | none |
| OD numbering | OD-NNN sequential | none |

## Spec vs Implementation Drift

No Go implementation exists yet (Phase 1 spec crystallization; P1 code begins after the
spec gate), so spec-vs-implementation drift cannot be assessed by its Phase 3+ method.
The only executable referent this cycle is the frozen legacy Python oracle
(`legacy/`, read-only D4 reference). Burst-scoped disposition:

| Artifact | Spec Version | Implementation State | Drift Detected | Notes |
|----------|-------------|---------------------|---------------|-------|
| behavioral-contracts/ (154) | current (this burst) | missing (pre-P1) | n/a | parity obligations pinned to the legacy oracle; parity drift is what D4/Tier A-D will measure once Go code exists |
| verification-properties/ (41) | current (this burst) | missing (pre-P1) | n/a | VP skeletons specified, vehicles land with stories |
| architecture/, domain-spec/, prd-supplements/ | current (this burst) | missing (pre-P1) | n/a | no implementation surface to drift against; recurring check at Phase 3+ and maintenance Sweep 10 |
| legacy/ (oracle) | frozen 2026-11-14 | current (reference) | no | depth laws, TZ semantics and composite shapes re-verified against legacy SL sites this pass (checks 5-7) |

## Findings

| SC-NN | Severity | File:line | Inconsistency | Owner agent |
|-------|----------|-----------|---------------|-------------|
| SC-13 | Major | `specs/verification-properties/VP-INDEX.md:211`, `:232` | The per-BC coverage-map rows for BC-1.05.007 (`VP-021` only) and BC-1.07.007 (`VP-009, VP-039` only) lack VP-001, while VP-001's `bcs:` carries both BCs (modified v1.6, ADV-P5-A2-11/C15: "BC-1.07.007 and BC-1.05.007 added to bcs:") and both BC bodies reciprocate with live VP-001 rows. The v1.10 "map rows completed per the union definition" pass completed only the BC-1.01.009 and BC-1.07.003 rows. An implementer reading the map alone would under-count both contracts' coverage. Remedy: regenerate the two map rows to the union (`BC-1.05.007 ← VP-001, VP-021`; `BC-1.07.007 ← VP-001, VP-009, VP-039`). | architect |
| SC-14 | Major | `specs/verification-properties/VP-012-exclusion-set-closure.md:13`, `specs/behavioral-contracts/ss-01/BC-1.04.003.md:122`, `specs/behavioral-contracts/ss-01/BC-1.05.005.md:128` | Two new one-sided VP↔BC edges, unenumerated: BC-1.04.003 and BC-1.05.005 gained VP-012 rows in this pass (ADV-P5-C2-17 closure citations) but VP-012's `bcs:` (19 entries, VP-012-exclusion-set-closure.md:13) excludes both, and VP-INDEX.md:316-321's residual prose — rewritten this pass and asserting the residuals are "enumerated explicitly" — does not list them. Remedy: add both BCs to VP-012 `bcs:` and regenerate the two map rows (or enumerate the residue in VP-INDEX). | architect |
| SC-15 | Major | `specs/behavioral-contracts/ss-01/BC-1.03.013.md:22`, `specs/behavioral-contracts/ss-05/BC-5.02.002.md:24`, `specs/behavioral-contracts/ss-05/BC-5.03.002.md:24`, `specs/behavioral-contracts/ss-06/BC-6.02.003.md:33` | Four frontmatters do not parse under PyYAML, all introduced by pass-5 edits: BC-1.03.013's `modified:` opens with a stray leading comma (`modified: [, "1.3 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C12) …`, a deleted entry left its separator); BC-5.02.002's 1.1.3 entry embeds the row-51 generator literal with escape sequences that terminate the double-quoted scalar early; BC-5.03.002's 1.2.3 entry spells `\xNN` inside a YAML double-quoted scalar (letters N are not hex — unknown-escape failure); BC-6.02.003's 1.2.6 entry spells `\U/\t` (`\U` requires exactly 8 hex digits in YAML, so the unknown-escape failure hits at `\/`). Consequence: any frontmatter-consuming tooling (index regeneration, the adversary's parsers) fails or silently skips these four contracts. Remedy: single-quote or re-escape the four entries. | product-owner |
| SC-16 | Major | `specs/behavioral-contracts/ss-02/BC-2.01.004.md` (PC-1 amendment list ending at pass-4 call 5; registry omits the four keys entirely — 0 occurrences) | The registry BC's pass-5 additions (PC-6 item 9) cover OD-179 and the glyph/pill completions but not the four keys whose RANGES changed in call 16: `statusline.transcript.read_cap_bytes` (1..67108864, interface-definitions.md:198), `statusline.transcript.dedup_memory` (1..65536, :199), `statusline.sparkline.history_cap` (1..1000, :208), `statusline.cost.burn_min_api_ms` (Int > 0, :240) — each annotated "pass-5 A13/C2-08/call 16" in interface-definitions. BC-2.01.004's H1 promises "Key registry: every key declares type, range/operator, default and rationale", and PC-1's amendment sentence stops at pass-4 calls, so the call-16 ranges exist in only one document. Same SC-09 class as pass 4 (which the burst did fix for that generation of keys). Consumers BC-1.05.002 (v1.3.3) and BC-1.04.003 (v1.3.3) do carry their call-16 ranges; BC-1.03.005 carries only the legacy `dedup_memory` default. Remedy: register the four keys with type/default/range per interface-definitions and extend the PC-1 amendment sentence through call 16. | product-owner |
| SC-17 | Major | `specs/behavioral-contracts/ss-01/BC-1.01.009.md:111` | The live EC-005 row still reads "tests `TestD4EX3_{Number,Boolean,URL,Enum}` (one per class with a dedicated grammar; … register closed at six)" — both the four-name list and the "closed at six" count were superseded by OD-178 (register closed at SEVEN, five canonical names incl. `TestD4EX3_Text`). The rest of the corpus is aligned (BC-2.02.001:122-132/:198, error-taxonomy.md:65-70/:36-37, ARCH-07:127, VP-012 modified v1.9); this row was not swept when its file was edited for ADV-P5-B01/B02. Remedy: respell to the five-name/seven-class canon. | product-owner |
| SC-18 | Minor | `specs/behavioral-contracts/ss-01/BC-1.02.027.md:131` | Live line-number pointer "per ARCH-06:78" into ARCH-06 (call 19 replaced such pointers with stable fragment anchors; ARCH-06:78 is moreover the superseded-law remark line). Remedy: cite the ARCH-06 anchor the way sibling BCs do. | product-owner |
| SC-19 | Minor | `specs/behavioral-contracts/ss-01/BC-1.04.002.md` (frontmatter), `specs/behavioral-contracts/ss-06/BC-6.03.003.md`, `specs/behavioral-contracts/ss-06/BC-6.03.004.md` | Version/last-modified lag: BC-1.04.002's `version` (1.3.2) is one patch BEHIND its last version-prefixed modified entry (1.3.3); the ss-06 pair's `version` remains one patch ahead of its last prefixed entry (1.2.5 vs 1.2.4; 1.2.6 vs 1.2.5) — the p4 SC-11 lag persists there despite pass-5 touches. Remedy: prefix or re-spin the trailing entries. | product-owner |
| SC-20 | Minor | 13 frontmatters: `BC-1.01.002`, `BC-1.02.004/.005/.006/.014/.027/.030`, `BC-2.02.001`, `BC-6.02.002`, `BC-6.03.003`, `BC-6.03.004`, `BC-6.04.003`, `VP-012` | Modified histories are not chronologically monotonic: bursts appended entries whose embedded authoring timestamps predate their neighbours (e.g. BC-1.02.004: 11-18 02:00 → 11-17 12:00 → 11-18 05:42; BC-6.02.002: 11-19 00:12 → 11-17 21:45). Content-safe but defeats "newest entry last" readers and the input-hash-style tooling. Remedy: reorder entries by timestamp on the next wording touch of each file. | product-owner |

### Critical

None. Counts, title triple-equality (including both retitled contracts), 301/301
anchor resolution, the glyph registry's 27-member identity, the corrected fade
`[base, span]` composite shape, the depth-law coherence across six documents, the
OD-177 TZ chain, OD-rider test-name canon, the closed-set 11-id propagation, and
public-repo hygiene are all machine-clean.

### Major

- **SC-13** — VP-INDEX per-BC map rows for BC-1.05.007/BC-1.07.007 lack VP-001 (v1.10 completion incomplete).
- **SC-14** — VP-012 `bcs:` misses the two BCs that gained VP-012 closure rows this pass; unenumerated.
- **SC-15** — four pass-5-introduced unparseable frontmatters.
- **SC-16** — registry BC omits the four call-16 keys whose ranges changed this pass.
- **SC-17** — BC-1.01.009 EC-005 row stale against the OD-178 register ("six" / four-name list).

### Minor

- **SC-18** — surviving line-number pointer into ARCH-06 from BC-1.02.027.
- **SC-19** — version/last-modified lag in three BC frontmatters.
- **SC-20** — out-of-order modified histories in thirteen frontmatters.

## Validation Gate Result

**PASS-WITH-FINDINGS** — no blocking (Critical) findings. SC-15 should be remediated
before adversarial pass 6 (both the adversary's frontmatter readers and any index
regeneration trip on unparseable YAML); SC-13/SC-14 close the VP-INDEX/vp-frontend
completion the v1.10 entry promises and should ride the same preparation burst;
SC-16/SC-17 are one-row propagation fixes closing the call-16/OD-178 register promises;
SC-18/SC-19/SC-20 may ride the next wording touch of their files.

## Overall Metrics

| Metric | Value |
|--------|-------|
| **Total Checks** | 11 burst-sync + 10 standing categories |
| **Passed** | 11 + 5 standing pass |
| **Failed** | 0 |
| **Warnings** | 8 (SC-13..SC-20: 5 Major, 3 Minor) |
| **Overall Status** | inconsistencies-found (localized; none blocking) |

The pass-5 burst propagated cleanly on the headline invariants: 154/41 counts, title
triple-equality after the two retitles, 301/301 anchor resolution, the 27-member glyph
registry identity with both renames, the corrected fade `[base, span]` law, the
end-to-end depth-law reconciliation (995 − s / 994 − s, per-site budgets, no live
`993 − W`), the OD-177 TZ chain, the canonical rider test names, and the closed-set
11-id discharge at every enumeration site. Compared with pass 4 the residue shrank to
localized single-file items: two VP-map/`bcs:` completion debts on VP-001/VP-012, four
malformed frontmatters from the burst's own quoting, the call-16 registry gap, one stale
D4-EX-3 row, and three convention nits. All are single-line or single-file remedies.

## Appendix: Validation Methodology

Fresh-context scripted sweep over the factory worktree at baseline `f920d7f` (131 dirty
files). Method: three `python3 -I` passes (CPython 3.11.7, PyYAML) over all 239 spec
`.md` files — (1) count and title joins across the 154 BC files, BC-INDEX rows and PRD
section-2 rows with escape-aware (`\|`) pipe-table parsing and `# Behavioral Contract
BC-x.y.z:` H1 normalization; VP catalog/catalog-arithmetic joins; (2) VP↔BC edge
extraction from YAML-parsed `bcs:` frontmatter versus BC-body citations (frontmatter and
version-prefixed history lines filtered), contrasted with VP-INDEX.md:316-327's enumerated
exceptions; per-BC map-row regeneration cross-check; (3) closed-set enumeration-site
detection (±2-line windows around OD-159/OD-161/OD-76 co-occurrences) with per-site
11-member verification and a live `ten-id(s)` sweep; D4-EX-3 class/test-name canon
sweep; (4) per-key glyph-registry set comparison (BC-2.01.004 PC-6 rows vs the
interface-definitions COMPLETE MEMBER LIST row) with a specs-wide `glyphs.<name>`
membership audit; (5) per-key presence/range spot-verification of the pass-5 keys in
interface-definitions, BC-2.01.004/PC-1..PC-8, BC-2.01.005 PC-5 and consumer BCs;
(6) depth-statement extraction (995 − s / 994 − s / 999 − F, per-site budgets,
`993 − W` residue classification) across the six depth-bearing documents;
(7) TZ-rule statement extraction across BC-3.01.001, ARCH-05, VP-026, BC-5.04.001,
BC-6.01.002, BC-6.02.003; (8) canonical rider-name sweep; (9) frontmatter extraction
with duplicate-key detection, YAML parse, version-vs-last-modified-token comparison and
chronological-order checking; (10) ARCH fragment-link resolution via `<a id>` or
heading-slug reduction over 301 links plus a line-pointer sweep into ARCH docs;
(11) hygiene regexes (IP octets excluding 192.0.2.x/loopback/doc ranges, home paths,
emails, session links, block-script prose scan with test-data allowance). Manual reads
adjudicated every script hit (reroute/stale rename provenance, subagent-glyph family
false positives, date-only timestamp-granularity artifacts in the monotonicity check,
and a splitter off-by-three found and corrected mid-run for the frontmatter pass).
Raw sweep digest over sorted relpath+size of the 239 spec `.md` files was `670beb8`;
the frontmatter `input-hash` (3e2faae) is the factory-canonical recomputation by the
plugin's compute-input-hash tool. Findings use SC-NN continuing the pass-4 sync-check
numbering lineage.
