---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass-with-findings"
producer: consistency-validator
timestamp: 2026-11-17T23:30:00Z
phase: 1
inputs: [specs/behavioral-contracts/, specs/verification-properties/, specs/architecture/, specs/domain-spec/, specs/prd-supplements/, specs/prd.md, specs/product-brief.md, specs/cicd-setup.md, specs/dtu-assessment.md, specs/owner-decisions-log-2026-11-14.md, cycles/phase-1-spec-crystallization/pass-4-remediation-plan.md, adversarial-reviews/ADV-P4-INDEX.md]
input-hash: "14c2f9d"
traces_to: ../../STATE.md
---

# Consistency Validation Report: hylo pass-4 fix-burst sync check

## Report Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo (status line + hybrid routing, P1 spec crystallization) |
| **Generated** | 2026-11-17T23:30:00Z |
| **Generator** | consistency-validator (fresh context, scripted checks under `python3 -I`, PyYAML 6.0.2) |
| **Artifacts Scanned** | 157 dirty files vs `9c5dda3`; 239 spec `.md` files across 7 trees (behavioral-contracts 156, verification-properties 42, architecture 12, domain-spec 9, prd-supplements 7, research 6, root 7) |

**Scope note.** Fresh-context sync check after the pass-4 fix burst and its post-burst
correction (plan item 10 as CORRECTED: OD-148 layout), before adversarial pass 5.
Delta validation per orchestrator instruction — the nine orchestrator-declared checks
were executed mechanically (scripted; no manual sampling) plus the standing 10-category
summary with delta dispositions. Read-only on specs; nothing committed. Findings
continue the sync-check numbering lineage (SC-01..04 consumed by pass-3).

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | L2 to L3 Requirement Coverage | pass (154/154/154 counts; title triple-equality clean) |
| 2 | L3 to L4 Verification Property Coverage | pass with SC-05, SC-12 (bijection residuals) |
| 3 | Dependency Acyclicity | n/a — burst-scoped (no story/wave deltas) |
| 4 | Architecture Alignment | pass (117/117 ARCH anchors resolve; OD-148 layout propagated) |
| 5 | Acceptance Criteria Quality | n/a — burst-scoped (no story ACs in delta) |
| 6 | Story Sizing | n/a — burst-scoped |
| 7 | Priority Consistency | n/a — burst-scoped |
| 8 | L1 to L2 to L3 to L4 Chain Completeness | pass (154 BC / 41 VP chain intact) |
| 9 | AC Completeness Coverage | n/a — burst-scoped (recurs at Phase 2) |
| 10 | ASM/R Traceability | pass with SC-06 (one 10-id closed-set residue); R-008/OD-169 linkage otherwise coherent |

### Burst-sync check matrix (9/9 executed)

| # | Check (orchestrator wording) | Result |
|---|------------------------------|--------|
| 1 | Counts: 154 BCs (files = BC-INDEX rows = PRD rows), 41 VPs (files = VP-INDEX rows; class arithmetic), titles H1 = BC-INDEX = PRD | PASS — 154 = 154 = 154; 41 = 41; class arithmetic invariant 33 + safety 7 + performance 1 = 41, method buckets 20+13+3+2+1+1+1 = 41; all 154 H1 titles equal BC-INDEX and PRD cells after CommonMark `\|` unescaping (BC-1.02.003, BC-2.02.006 legitimately escape pipes in tables) |
| 2 | VP↔BC bijection; every VP `bcs:` entry cites back; one-sided links vs VP-INDEX prose-only exceptions | PASS WITH SC-05, SC-12 — 236 directed VP→BC edges over 41 VP files; 3 one-sided: VP-022→BC-1.01.009 and VP-006→BC-1.07.003 (both enumerated prose-only in VP-INDEX v1.7), VP-001→BC-1.01.002 stale (SC-05); 7 reverse-only BC→VP citations: 6 enumerated (VP-034/VP-022/VP-024 exceptions + 3 VP-026 removal cross-refs), BC-1.01.009→VP-007 new (SC-12) |
| 3 | Closed exclusion set = 11 ids (incl. OD-166) everywhere enumerated; no "ten-id" in live text | PASS WITH SC-06 — 13 enumeration sites detected; 12 carry the complete 11-id set (BC-6.03.004, VP-012, ARCH-00, ARCH-07, error-taxonomy:195, prd.md, product-brief.md, BC-1.05.004, invariants, bounded-contexts, ubiquitous-language, owner-decisions-log); VP-009:41 still lists ten (SC-06); sole live "ten ids" is ARCH-00:35's quoted superseded description — clean |
| 4 | New plan keys in interface-definitions.md AND the BC-2.01.004 registry, type/default/range agreeing | PASS WITH SC-09 — all seven key groups present in interface-definitions with types/defaults/ranges matching OD-173 (pill labels DGX/ANTH/?, Text, width 1..16), OD-174 (display_floor_usd Float 0.005, `>=`), OD-175 (queue.yellow Bool true) and design calls 2/3/4/5; BC-2.01.004 PC-1/PC-6/PC-7 carries pill labels, display_floor_usd, labels.input, queue.yellow consistently, but three keys are absent (SC-09) |
| 5 | Every `ARCH-*.md#fragment` link in BCs/VPs resolves | PASS — 117 live fragment links, 117 resolve (explicit `<a id>` or heading slug); zero unresolved |
| 6 | No live occurrence of the eight banned strings/tags | PASS — 0 live hits for `TestConfigError_D4EX3`, `internal/parity/testdata`, "20 seeded", `SeededSessions20`; `basis_min_shown_usd` survives only as 6 renamed-from provenance remarks (OD-174); `steps.jsonl` only in ARCH-07:101's explicit negation ("not as a sibling steps.jsonl"); the "2026-11-18 owner ruling" phrase only inside owner-decisions-log:165 quoting OD-175's own text; all 8 live `posix-only` hits are removal prose ("tag removed", "no skip") — clean, with one wording observation on BC-5.04.002:76 |
| 7 | Frontmatter: parses as YAML, no duplicate keys, version equals last modified entry | PASS WITH SC-07, SC-08, SC-11 — 239 files; 0 duplicate keys; 2 unparseable frontmatters introduced by the burst (SC-07, SC-08); 5 files with version/modified-convention lag (SC-11) |
| 8 | CP-* ids cited in BCs/VPs exist in error-taxonomy.md (ranges count); CP-N03 present | PASS WITH SC-10 — 49 distinct CP ids cited live; S/O/N/A registers complete with ranges expanded; CP-N03 present (error-taxonomy:207-208, per design call 17); CP-C01..C10 cited but absent from the taxonomy register (SC-10) |
| 9 | Hygiene: IPs, home paths, emails, session links, non-English prose | PASS — 0 real IPs (all IPs on 192.0.2.x/doc/loopback), 0 emails, 0 session links; home-path hits are synthetic shapes (`/home/user`, `/Users/<name>` placeholders, corpus-hygiene rule text); all non-ASCII is test data (CJK width vectors, Arabic-Indic/FW digits) or math symbols (ε, Σ) — explicitly allowed |

## 1. L2 to L3 Requirement Coverage

Delta scope: the pass-4 rulings OD-169..OD-175 and design calls 1-19. Counts verified
mechanically: 154 BC files = 154 BC-INDEX rows = 154 PRD section-6 rows, no orphans in
either direction. H1-title triple-equality (file H1 = BC-INDEX title = PRD title) holds
for all 154 contracts; pipe-containing titles (BC-1.02.003, BC-2.02.006) are correctly
`\|`-escaped in the two tables and match their H1s modulo escaping.

## 2. L3 to L4 Verification Property Coverage

41 VP files (VP-001..VP-041) regenerated into VP-INDEX (v1.8); VP-041 (row-1 property
legs split from VP-028, plan item 18) is registered and the class/method arithmetic
closes exactly. The VP↔BC citation weave is bijective except the pass-3-enumerated
prose-only residuals plus two new residues:

- **SC-05 (stale edge):** BC-1.01.002 removed VP-001 from its anchors in the pass-4
  burst (its modified entry records "VP-001 removed from VP Anchors" for
  ADV-P4-B11/A2-16), but VP-001's `bcs:` still lists BC-1.01.002 and the VP-INDEX
  per-BC coverage map (VP-INDEX.md:104) regenerates the stale edge.
- **SC-12 (unenumerated residual):** BC-1.01.009's body cites VP-007, which was
  re-anchored to BC-5.04.003 in pass 4 (A2-10); the citation persists in the BC body
  but VP-007's `bcs:` no longer lists BC-1.01.009, and this residue is not in
  VP-INDEX's prose-only exception list.

## 3. Dependency Acyclicity

No dependency-graph inputs (stories, waves) exist in the delta; the burst introduced no
ordering constraints. Full sweep recurs at story decomposition.

## 4. Architecture Alignment

Delta scope: all 117 `ARCH-*.md#fragment` references from BCs and VPs resolve against
`<a id>` anchors or heading slugs (ADV-P4-A01's anchor gap is closed). The corrected
corpus layout (plan item 10, OD-148: root `internal/statusline/testdata/parity/cases/`,
exclusions `internal/statusline/testdata/parity/exclusions.json`, `steps` inside
`case.json`) is propagated consistently across ARCH-07, BC-6.02.001/.003, BC-6.03.003/
.004, BC-6.04.003 and VP-012's v1.7 correction; no live `internal/parity/testdata`
occurrence remains.

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
| L2 | Domain Spec (capacities, invariants, state machines) | 9 files | to L3 | to L1 | 100% |
| L3 | Behavioral Contracts (BC-S.SS.NNN) | 154 | to L4 | to L2 | 100% |
| L4 | Verification Properties (VP-NNN) | 41 | N/A | to L3 | 100% |

No broken chains and no orphaned levels introduced by the pass-4 burst.

## 9. AC Completeness Coverage

Not in delta scope (no story ACs in the burst). BC-clause-level reverse coverage
(criteria 34-41) recurs at Phase 2 decomposition.

## 10. ASM/R Traceability

Delta scope: OD-169's exclusion-split (OD-166) carries its required VP-012 closure row
and scope sentence, and the VP-012 v1.5 rider test-name canonicalization
(`TestD4EX3_{Number,Boolean,URL,Enum}`, no Theme member) matches design call 13 — the
old `TestConfigError_D4EX3` spelling is extinct. OD-171's TZ ruling removed the skip
tag coherently in VP-026, VP-INDEX, ARCH-05, and the four consumer BCs. No ASM status
changed in the burst. One closed-set enumeration site (VP-009) lags — SC-06.

## Cross-Reference Validation

### ID Consistency

| Check | Status | Issues |
|-------|--------|--------|
| BC/VP/CAP IDs unique | pass | none observed in delta |
| BC ↔ CAP / VP ↔ BC traces | pass | bijective modulo enumerated exceptions (SC-05, SC-12 residues) |
| Crash-id spellings | pass | no malformed range endpoints; CP-N03 minted per design call 17 |
| Closed-set membership | pass | 11 ids incl. OD-166 at 12 of 13 sites (SC-06) |

### Naming Convention Compliance

| Convention | Expected Pattern | Violations |
|-----------|-----------------|------------|
| BC naming | BC-S.SS.NNN | none |
| VP naming | VP-NNN | none |
| Rulings | OD-NNN (next free: OD-176) | none |
| Error taxonomy | E-xxx-NNN + CP-xNN register | CP-C01..C10 not registered (SC-10) |

## Findings

| SC-NN | Severity | File:line | Inconsistency | Owner agent |
|-------|----------|-----------|---------------|-------------|
| SC-05 | Major | `specs/verification-properties/VP-001-never-blank-exit0.md:13` | `bcs:` still lists BC-1.01.002, but BC-1.01.002 deliberately removed VP-001 from its VP Anchors in this burst (BC-1.01.002.md:24 modified entry, ADV-P4-B11 + A2-16 sibling sweep) and its body cites only VP-005/VP-006 (BC-1.01.002.md:114-115,146). VP-INDEX.md:104 coverage row (`BC-1.01.002 ← VP-001, VP-005, VP-006`) regenerates the stale edge. Remedy: drop BC-1.01.002 from VP-001 `bcs:` and regenerate the coverage map — or justify the retention and enumerate it as prose-only. | architect |
| SC-06 | Major | `specs/verification-properties/VP-009-tier-a-live-parity.md:41` | Live closed-set enumeration lists ten ids: "(D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161)" — OD-166 is missing, contrary to OD-169 ("the closed set becomes 11 ids ... everywhere") and to the other twelve enumeration sites (all complete). This is the Tier-A live-parity VP whose exclusion replay rides the set. Remedy: add OD-166 (cost-history unconvertible-field scope) to the enumeration. | architect |
| SC-07 | Major | `specs/behavioral-contracts/ss-04/BC-4.01.002.md:27` | Frontmatter does not parse: the v1.1.3 modified entry contains unescaped double quotes — `... only [] and ["--subagent"] in P1 ...` — so the scalar terminates at `and [` and `"--subagent"]` becomes a stray second scalar on the list line ("expected block end, but found '<scalar>'"). Introduced by the pass-4 D05 fix. Remedy: escape or single-quote the entry. | product-owner |
| SC-08 | Major | `specs/behavioral-contracts/ss-06/BC-6.04.001.md:27-28` | Frontmatter does not parse: `modified:` opens as an inline flow list on line 27 (`modified: ["1.2.1 2026-11-17: VP citation reconciliation — VP-010 added"]`) and line 28 appends a block-style continuation `  - "1.2.2 2026-11-18: ADV-P4 remediation D08 ..."` ("expected block end, but found '<block sequence start>'"). Introduced by the pass-4 D08 fix. Remedy: fold the 1.2.2 entry into the flow list (or convert both to block style). | product-owner |
| SC-09 | Major | `specs/behavioral-contracts/ss-02/BC-2.01.004.md:80-131` (PC-1/PC-6/PC-7) | Three pass-4-ratified keys are absent from the registry BC's live text (0 occurrences): `statusline.subagent.tokens.suffix` (design call 3, C05), `statusline.sparkline.preempt_marker_above` (design call 5, C2-13), and the full key spelling `statusline.subagent.glyphs.unknown` (design call 4/C07 — the family lists member `unknown` at :121 but never the dotted key). interface-definitions.md:197/205/238 has all three correctly. Because BC-2.01.004 PC-1 defines the amenable P1 key subset as design §2.4 "as amended by OD-113/OD-123/OD-173/OD-174/OD-175", an implementer building the `Registry()` test regime from this BC alone would omit the two keys. Remedy: extend PC-6/PC-7 (or add an OD-176-class amendment row) naming the two keys with type/default/range per interface-definitions. | product-owner |
| SC-10 | Major | `specs/prd-supplements/error-taxonomy.md:207-214` | The foreign-cache crash family CP-C01..C10 (minted by OD-160, owner-decisions-log:144) is absent from the CP register and the disposition paragraph: taxonomy table rows cover S/O/N/A plus CP-N, and :207's disposition mapping names only CP-S01..S17, CP-T01..T07, CP-N01/N02, CP-N03, CP-O01..O11, CP-A01..A05, CP-X01..X04. Yet BC-1.01.009:58-75, BC-1.02.013:109, BC-1.02.005:92/111, BC-1.04.003:96, BC-1.05.004:111/135 and BC-3.02.001/BC-1.06.001/BC-1.04.002 cite CP-C ids as their governing vectors. By the taxonomy's own rule (:213-214, "a trigger whose disposition is neither of those is a spec gap and fails the consistency check") the family must be registered. Remedy: add a CP-C01..C10 register row/paragraph (disposition: OD-160 named-exclusion vectors; Go table tests, not byte-parity). | product-owner |
| SC-11 | Minor | `specs/behavioral-contracts/ss-01/BC-1.03.015.md`, `ss-06/BC-6.02.001.md`, `ss-06/BC-6.02.003.md`, `ss-06/BC-6.03.003.md`, `ss-06/BC-6.03.004.md` (frontmatter) | Version/modified convention lag: frontmatter `version` is one patch ahead of the last version-prefixed modified entry (e.g. BC-6.03.004 version "1.2.4", last prefixed entry "1.2.3", later entries unprefixed phrase-style). Harmless but breaks the "version == last modified entry" convention the index tooling relies on. Remedy: prefix or re-spin the trailing entries. | product-owner |
| SC-12 | Minor | `specs/behavioral-contracts/ss-01/BC-1.01.009.md` (VP-007 citation, body) | BC-1.01.009's body cites VP-007 (render-determinism seams), but VP-007 was re-anchored to BC-5.04.003 in pass 4 (A2-10) and its `bcs:` no longer lists BC-1.01.009. Not covered by VP-INDEX's enumerated prose-only exceptions (v1.7/v1.8). Remedy: add to the exceptions list or restore the `bcs:` entry. | architect |

### Critical

None. Counts, title sync, anchor resolution, banned-string extinction, CP-N03 minting,
OD-148 layout propagation, and hygiene all verified clean by script.

### Major

- **SC-05** — VP-001 stale `bcs:` edge to BC-1.01.002 (post-removal drift).
- **SC-06** — VP-009 closed-set enumeration lacks OD-166.
- **SC-07** — BC-4.01.002 frontmatter unparseable (pass-4 introduced).
- **SC-08** — BC-6.04.001 frontmatter unparseable (pass-4 introduced).
- **SC-09** — BC-2.01.004 registry missing two ratified keys + one full-key spelling.
- **SC-10** — CP-C01..C10 uncatalogued in the error taxonomy.

### Minor

- **SC-11** — version/modified prefix lag in five BC frontmatters.
- **SC-12** — BC-1.01.009→VP-007 residual citation unenumerated.

## Validation Gate Result

**PASS-WITH-FINDINGS** — no blocking (Critical) findings. SC-07/SC-08 should be
remediated before adversarial pass 5 (both the adversary's frontmatter readers and any
index regeneration trip on unparseable YAML); SC-05/SC-06/SC-09/SC-10 are one-line
propagation fixes that close the OD-169/OD-160/registry-set promises and should ride
the pass-5 preparation burst; SC-11/SC-12 may ride the next wording touch of their
files.

## Overall Metrics

| Metric | Value |
|--------|-------|
| **Total Checks** | 9 burst-sync + 10 standing categories |
| **Passed** | 9 + 5 standing pass |
| **Failed** | 0 |
| **Warnings** | 8 (SC-05..SC-12: 6 Major, 2 Minor) |
| **Overall Status** | inconsistencies-found (localized; none blocking) |

The pass-4 burst propagated cleanly on the headline invariants: 154/41 counts, title
triple-equality, 117/117 anchor resolution, the corrected OD-148 corpus layout, the
eight banned-string retirements, and public-repo hygiene are all machine-clean. The
eight findings are concentrated in the long tail of sibling-sweep propagation: one
stale VP edge, one lagging closed-set enumeration, two frontmatter malformations from
the fix burst itself, one registry-BC key omission, one uncatalogued crash family, and
two convention nits. All are single-file or single-line remedies.

## Appendix: Validation Methodology

Fresh-context scripted sweep over the factory worktree at baseline `9c5dda3` (157 dirty
files). Method: one `python3 -I` pass (PyYAML 6.0.2) over all 239 spec `.md` files
performing — (1) frontmatter extraction with duplicate-key detection via YAML event
composition and version-vs-last-modified-entry comparison with shape census (120
version-prefixed lists, 75 phrase lists, 2 scalars); (2) count and title joins across
the 154 BC files, BC-INDEX rows, and PRD section-6 rows with escape-aware (`\|`)
pipe-table parsing and H1 normalization; (3) VP↔BC edge extraction from `bcs:`
frontmatter versus BC-body citations (frontmatter excluded, modified-history lines
filtered), contrasted with VP-INDEX's enumerated prose-only exceptions; (4) closed-set
enumeration-site detection (co-presence of OD-159/OD-161/OD-76) with per-site member
checking and a live `ten-id(s)` regex sweep; (5) per-key live presence/type/default/range
spot-verification of the nine plan keys in interface-definitions.md and BC-2.01.004;
(6) ARCH fragment-link resolution via `<a id>` or GitHub heading-slug reduction over
117 links; (7) banned-string greps with frontmatter-`modified` history filtering;
(8) CP-id universe construction from taxonomy register rows plus range expansion
(CP-S01..S17, CP-T01..T07, CP-N01/N02/N03, CP-O01..O11, CP-A01..A05, CP-X01..X04) and
cited-id subtraction; (9) hygiene regexes (IP-octet scan excluding 192.0.2.x/doc/
loopback, `/Users/`+`/home/` paths, emails, session links, CJK/Arabic/Cyrillic
prose detection with test-data allowance). Manual reads adjudicated every script hit:
all `basis_min_shown_usd`/`steps.jsonl`/`posix-only`/"2026-11-18 owner ruling"/ten-ids
residues are provenance, negation, removal-prose, or quoted-history contexts. Snapshot
input-hash `1fd4312` (SHA-256 over sorted relpath+size of the 239 files). Findings use
SC-NN continuing the pass-3 sync-check numbering lineage.
