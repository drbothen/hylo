---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass"
producer: consistency-validator
timestamp: 2026-11-17T10:30:00Z
phase: 1
inputs: [consistency-audit-2026-11-17.md, specs/prd.md, specs/prd-supplements/assumptions-register.md, specs/prd-supplements/risk-register.md, specs/verification-properties/VP-INDEX.md, specs/architecture/ARCH-INDEX.md, specs/behavioral-contracts/BC-ALLOCATION.md]
input-hash: "e340f7c"
traces_to: consistency-audit-2026-11-17.md
---

# Consistency Re-check: CA-01..CA-12 Fix Burst (hylo P1)

Fresh-context re-check of the 2026-11-17 fix burst (commit `6b67d35` plus the uncommitted
145-BC input-hash normalization in the working tree). Scope per orchestrator instruction:
resolution status of each audit finding, then consistency of the NEW files
(`assumptions-register.md`, `risk-register.md`) with the rest of the package. Untouched
files not re-audited. Owner rulings OD-152..OD-154 treated as settled.

## Part 1: Resolution Status

| ID | Verdict | Evidence (file:line) |
|----|---------|---------------------|
| CA-01 | RESOLVED | `specs/prd.md:288` now carries the source-of-truth title "prints the config, cache and state paths (OD-132)", matching H1 `ss-02/BC-2.03.002.md:33` and `BC-INDEX.md:195`. All four titles agree. |
| CA-02 | RESOLVED | `VP-INDEX.md:34-40` Totals regenerated from the Catalog Method column. Independent recount of the Method column: 18 unit/table + VP-026 "tables" + VP-035 "unit/table + gate" = 20; golden 3 + parity 2 = 5; fuzz 1 + "fuzz + tables" (VP-006) + property 2 + "property + build-time check" (VP-015) + "property + tables" 3 + property/fuzz 1 = 9; static 1; measured 1; CI 1. Sum 37. Bucketing judgment calls documented in-band (:38-40). `ARCH-INDEX.md:104-105` aggregate matches (20/5/9/1/1/1). |
| CA-03 | RESOLVED | 14/14 ss-06 BC files carry the OD-153 rationale blockquote (e.g. `ss-06/BC-6.02.001.md:130`); PRD §1.6 S6 row updated to "CAP-009 (parity verification); DI-012 machinery" (`prd.md:113`). Consistent with OD-153's "no new L2 capability". |
| CA-04 | RESOLVED | Registers minted per OD-152: `specs/prd-supplements/assumptions-register.md` (ASM-001..006), `specs/prd-supplements/risk-register.md` (R-001..R-007). Pointers: `prd.md:567-568` (§9 canonical register), `architecture-feasibility-report.md:83-85` (R-001..R-007 mapping), `ARCH-INDEX.md:43` (risk-register row). See Part 2 for new-file checks. |
| CA-05 | RESOLVED | Discharged as declared: Pass 3 body anchors exist — "Verification Properties" sections in 145/145 BC files (93+13+3+3+19+14), sampled BC-1.01.001.md:94-100 (VP-001/VP-003 rows matching VP-INDEX source_bc). ARCH-INDEX:103-106 and VP-INDEX:223-225 now record Pass 3 DONE consistently; nothing still promises a frontmatter field. |
| CA-06 | RESOLVED | `module-criticality.md:42-47` VP counts verified against the VP-INDEX Catalog Module column: S1 17, S2 3, S3 3, S4 2, S5 6, S6 8; 39 slots − VP-005 − VP-014 (dual) = 37/37 union. Dual-attribution note (:48-52) accurate — spot-checked VP-020 (internal/cost → S1), VP-022 (module internal/statusline, home ARCH-04/09), VP-035, VP-037. |
| CA-07 | RESOLVED | `architecture-feasibility-report.md:81` amended in place ("on-disk count is now 145/145; original verdict retained"); the 145/145 figure independently confirmed. |
| CA-08 | RESOLVED | `ARCH-INDEX.md:116-121`: ARCH-00 P4 → VP-001; ARCH-04/09 → VP-022; ARCH-08 (timing gate) → VP-036 — each matching the catalog Home column (`VP-INDEX.md:54`, VP-022 home "ARCH-04/09, DI-007", VP-036 home "ARCH-08, NFR-001"). One residual in the rewritten line — CR-03 below. |
| CA-09 | RESOLVED | Working-tree normalization: 145/145 BC files re-stamped with computed 7-hex hashes (0 residual `0000000`; 0 traversal-form `inputs:` left); registers stamped (`assumptions-register.md:10`, `risk-register.md:10`). Verified with compute-input-hash: spot `--check` OK on 3 BCs + both registers; `--scan specs` reports 0 MISSING (was 145) and all 145 BCs MATCH. Hash collisions are legitimate (hash covers inputs, not the file — same-input shards share hashes). |
| CA-10 | RESOLVED | `BC-ALLOCATION.md:420-422` postcondition now "at most 22 contracts — G reached 22 after the OD-141/OD-140 additions (stage-2 baseline cap was 21)", consistent with the per-group line "G 22" (:378). |
| CA-11 | RESOLVED | `ss-04/BC-4.01.003.md:91` re-anchored with substantive CAP-015 rationale (build-injected product metadata; reads no runtime config). |
| CA-12 | RESOLVED | `prd.md:525` RTM row now "`internal/statusline` + `internal/cost`", matching BC-COMPONENT-MAP and the feasibility report's cost-inherits-S1 decision. |

Score: **12/12 RESOLVED**, 0 PARTIAL, 0 OPEN.

## Part 2: New Files vs the Rest of the Package

Checked: every ASM/R cited anywhere exists in the registers; every HIGH risk's
architecture anchor exists and says what the register claims; NFR links resolve; PRD
pointer and ID lists match.

- ASM citations: ASM-001..006 defined (`assumptions-register.md:23-28`); PRD §9 items map
  1:1 (`prd.md:571-582`); no dangling ASM references found elsewhere on disk.
- HIGH-risk anchors: R-001 → AD-08 (`ARCH-04-data-files.md:37` "Go is byte-exact cache
  writer and reader across Python/Go swaps") and R-004 → AD-09
  (`ARCH-07-parity-harness.md:22` "three-tier harness with a closed named exclusion
  list") — both say what the register claims. R-003's AD-11 = `ARCH-08-build-ci-release.md:55`
  (gate on three OSes). R-006's AD-10 = `ARCH-INDEX.md:81` (env seam set, RK-5
  disposition); its BC-2.01.001 invariant-6 citation checks out (`ss-02/BC-2.01.001.md:71`,
  reserved names excluded from unknown-key warnings).
- NFR links: NFR-001 (p95 <= 25 ms), NFR-003 (byte parity), NFR-004 (three-OS CI) all
  exist in `prd-supplements/nfr-catalog.md:24-29` and match the R-002/R-001/R-003 rows'
  substance. Note CR-04 on the reverse direction.
- ID lists: feasibility report's "rows above are minted as R-001..R-005, and the
  PRD-carried RK-5/RK-6 dispositions as R-006/R-007" matches the register exactly
  (`risk-register.md:25-31`; RK-5/RK-6 exist at `prd.md:613-614`). Register statuses
  (R-005 closed-remediated; R-006/R-007 closed) align with their anchors.
- Register frontmatter canonical (document_type, level, version, producer, timestamp,
  traces_to); risk-register `inputs:` includes its five declared sources; both hashes
  verify with compute-input-hash.

## Part 3: New Findings (introduced by the fixes)

| ID | Severity | Finding | Evidence |
|----|----------|---------|----------|
| CR-01 | LOW | Stale "follow-up burst" self-reference: both files say the R-NNN risk register is still to be minted, but `risk-register.md` exists in the same commit (timestamp 2026-11-17T16:00). Two spots: prd.md:588 and assumptions-register.md:19. One-line cleanup in each. | `specs/prd.md:588`; `specs/prd-supplements/assumptions-register.md:19` |
| CR-02 | LOW | Supplement-registration asymmetry: prd.md frontmatter `supplements:` gained assumptions-register.md but not risk-register.md, leaving the architect-produced register reachable only via ARCH-INDEX:43 / feasibility:85. Add it to the list (or record why the two are registered differently). | `specs/prd.md:21-27` |
| CR-03 | LOW | ARCH-INDEX by-home aggregate retains VP-006 under the ARCH-03 bucket although its catalog Home is "ARCH-06" only (it is also, correctly, in the ARCH-06 bucket). Pre-existing membership carried through a rewritten line, so the line's "aligned to the VP-INDEX catalog rows" claim is overstated for this one row. Drop VP-006 from the ARCH-03 bucket or annotate. | `specs/architecture/ARCH-INDEX.md:117-118` vs `VP-INDEX.md:59` |
| CR-04 | LOW | 64 downstream input-hashes went stale because the burst edited shared inputs (prd.md, VP-INDEX, ARCH-INDEX, BC-ALLOCATION, module-criticality, feasibility report, 14 ss-06 BCs) without re-stamping dependents: 37 VP files, 11 architecture, 6 domain-spec, 5 prd-supplements, 4 specs-root, BC-ALLOCATION (`compute-input-hash --scan specs`: STALE=64, MATCH=151, MISSING=0). None of the 145 BCs are affected. Deliberately scoped out per the committed burst-log (placeholder-only recompute); recommend a `--scan specs --update` pass at burst close, before phase-1-gate. | `specs/verification-properties/` (37), `specs/architecture/` (11), et al. |

No CRITICAL or HIGH findings. Nothing in the fix burst broke a chain that was intact
before: the L1→L2→L3→L4 counts (145/37/18) still reconcile across BC-INDEX, BC-ALLOCATION,
PRD §1.6/§2, BC-COMPONENT-MAP, VP-INDEX and module-criticality, and the new registers'
cross-references all resolve.

## Verdict

**PASS** — all 12 audit findings verified resolved on disk; 4 new LOW findings (CR-01..04),
all one-burst cleanups, none blocking. Recommended before phase-1-gate: CR-01/CR-02
(two-minute edits) and the CR-04 hash-sync pass. Consistency score 96/100 (was 92/100).

Gate status: remains PASS-WITH-FINDINGS.
