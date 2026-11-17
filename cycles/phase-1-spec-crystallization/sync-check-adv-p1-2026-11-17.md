---
document_type: consistency-report
level: ops
version: "1.0"
producer: consistency-validator
timestamp: 2026-11-17T21:30:00Z
phase: 1d
status: FAIL
inputs: [prd.md, product-brief.md, domain-spec/, prd-supplements/, behavioral-contracts/, architecture/, verification-properties/, behavioral-contracts/BC-ALLOCATION.md]
input-hash: "8eef662"
cycle: phase-1-spec-crystallization
step: adversarial-review 4b (cross-document sync check after fix burst)
baseline_commit: 6fa2b38
traces_to: ../../STATE.md
---

# Sync Check — ADV-P1 step 4b (2026-11-17)

## Report Metadata

- Baseline `6fa2b38` (working tree, ~180 changed files), checked against the unchanged corpus.
- Method: scripted cross-checks + targeted reads; read-only; no artifacts modified.
- Input-hash basis: MD5 over the declared `inputs:` tree (resolver-computed).

## Summary

| Check | Result |
|---|---|
| Depth-limit values (989/990 transcript, 993/994 stdin) | STALE in 4 files (SC-01..04) |
| `statusline.transcript.rebuild_excess` rename | SYNCED (no `.tokens.` remnants; name/type/default agree: interface-definitions.md:112 ↔ BC-1.03.007:44,108) |
| Tier C = OD-149 one clean nightly run, 3 OSes, 30 min/OS | SYNCED (OD-149, prd.md:393, cicd-setup.md, VP-011 statement); one stale paraphrase (SC-07) |
| `ps_timeout_s` = removed key / unknown-setting warning | SYNCED (risk-register R-007, ARCH-02:47ff, ARCH-05:47, ARCH-INDEX:88, BC-3.02.001:78, prd.md:618) |
| 29-byte degraded line | SYNCED (prd.md:144,411,467; BC-1.01.001; interface-definitions.md:69; test-vectors.md:25; VP-001/003; BC-ALLOCATION.md:102) |
| Exclusion-id spelling | SYNCED (prose `D4-EX-N` per BC-6.03.004; `D4EXN` only in Go test identifiers) |
| Subsystem names vs ARCH-INDEX registry | SYNCED (uniform `SS-01..06`; tallies 93/13/3/3/19/14 = 145 = BC-INDEX totals) |
| VP count 38 / VP-INDEX map | VP-INDEX and files agree (38, VP-038 included, rows↔files bijective, BC map present); ARCH-INDEX aggregate STALE (SC-05) |
| ARCH-06 pyfmt signatures vs BC-5.* | SYNCED (`Decode(b, mode, depthBudget)`, `FloorDiv/Mod` + `FloorDivInt/ModInt`, `RoundN`, `ParseFloat`, `FromISOFormat`, `SplitLinesBytes`) |
| `Repr(-0.0)` | SYNCED (BC-5.01.005:58,:82 → `-0.0`; ARCH-06:27) |
| Config keys: BC bodies vs registry | SYNCED for every registered key; wildcard families covered; INFO-01 |
| VP ↔ BC citation symmetry (38 VPs × 145 BCs) | 1 asymmetry = known-open VP-006/BC-1.03.004 (SC-06); 0 reverse-only |
| Titles: BC H1 = BC-INDEX = PRD rows | SYNCED (145/145; BC-2.02.006 pipe-escaped rows verified) |

## Findings

| ID | Sev | Location | Inconsistency | Owner |
|---|---|---|---|---|
| SC-01 | Medium | specs/behavioral-contracts/ss-01/BC-1.03.004.md:55 | "(depth 995 accepted, 1,000 rejected, BC-5.02.003)" — transcript `_mix_counts` site is 989 accepted / 990 rejected (BC-5.02.003:102; ARCH-06:28; VP-006) | product-owner |
| SC-02 | Medium | specs/behavioral-contracts/ss-01/BC-1.03.004.md:80 | EC-009 "Nesting depth 1,000" — boundary row should read depth 990 (L/L+1 single-limit) | product-owner |
| SC-03 | Medium | specs/prd.md:562 | "(stdin 993/994; transcript 995/1000)" — transcript half stale → 989/990 | product-owner |
| SC-04 | Medium | specs/behavioral-contracts/BC-ALLOCATION.md:525 | "transcript bytes mode 995 accepted / 1,000 rejected" — stale → 989/990 | product-owner |
| SC-05 | Medium | specs/architecture/ARCH-INDEX.md:113-121 | VP aggregate not regenerated after VP-038: "37 VPs"→38; "invariant 29"→30; method tally "unit/table 20"→19, "property/fuzz 9"→11; ARCH-03 home list omits VP-038 | architect |
| SC-06 | Low (known-open) | specs/verification-properties/VP-006-json-depth-budgets.md:15 ↔ specs/behavioral-contracts/ss-01/BC-1.03.004.md | Confirmed still open: VP-006 `bcs:` lists BC-1.03.004; BC body never cites VP-006; sole asymmetry in corpus | product-owner |
| SC-07 | Low | specs/verification-properties/VP-011-tier-c-differential-fuzz.md:45 | Source-Contract paraphrase "nightly Linux, non-gating" predates OD-149; BC-6.04.003 H1 is "nightly all three OSes, one clean run" | architect |

INFO-01 (non-blocking): interface-definitions.md:88 declares "Full registry (every key)"
but delegates to BC-2.01.004 + the not-yet-created golden
`internal/config/testdata/legacy_defaults.golden`; families `statusline.cost.*`,
`limits.*`, `timer.*`, `ttft.*`, `idle.*`, `power.*` are enumerated in no current spec
table. Pre-declared design deferral, not a contradiction.

Deliberately excluded per orchestrator instruction (owner rulings pending): OverflowError
handling; ±Inf / OD-130 telemetry; coverage-vs-mutation 95% for S1/S5; Windows file
encoding.

## 1. L2 to L3 Requirement Coverage

Not re-planned in this burst; PRD §7 rows and BC-INDEX agree 145/145 (title-verified).

## 2. L3 to L4 Verification Property Coverage

Primary subject of this check — see Summary and SC-05, SC-06. VP-INDEX itself is
self-consistent (38 rows = 38 files; class tally 30+6+1+1; method buckets sum to 38).

## 3. Dependency Acyclicity

N/A — stories not yet decomposed (Phase 1); deferred to implementation-readiness.

## 4. Architecture Alignment

ARCH-06 signatures and BC-5.* call shapes agree (including integer divmod pair and
`SplitLinesBytes`, newly exercised by VP-038/BC-1.03.004). ARCH-INDEX carries one stale
block (SC-05); ARCH-02/ARCH-05/ARCH-07 statements on removed `ps_timeout_s` agree.

## 5. Acceptance Criteria Quality

ACs are being rewritten this cycle; clause-level AC audit deferred to the main
consistency gate. Not re-audited here.

## 6. Story Sizing

N/A — no stories exist yet (Phase 1).

## 7. Priority Consistency

N/A — no stories exist yet (Phase 1).

## 8. L1 to L2 to L3 to L4 Chain Completeness

Chain is intact: PRD §6/§7 ↔ BC-INDEX ↔ BC files ↔ VP-INDEX are mutually complete
(144+1 pipe-escaped rows verified per side, 145 BCs, 38 VPs).

## 9. AC Completeness Coverage

Deferred to the main consistency gate (same reason as §5).

## 10. ASM/R Traceability

Assessment docs changed in this burst were spot-checked via the risk register
(R-007 disposition current; no stale mitigation references found). Full ASM/R sweep
not repeated here — unchanged since pass-1 audit.

## Cross-Reference Validation

- VP⇄BC: 38 VPs, citation graph symmetric except SC-06; no orphan VPs; no phantom BCs.
- VP-INDEX rows ↔ files: bijective; per-class and per-method tallies arithmetically correct.
- BC H1 ↔ BC-INDEX ↔ PRD titles: 145/145 exact (escaped-pipe row parsed and verified).
- Config keys: every dotted key in a BC body is either registered
  (interface-definitions representative table), covered by a wildcard family row, or a
  documented filename/dummy (`statusline.go`, `statusline.foo_s`) — see INFO-01.

## Spec vs Implementation Drift

Not applicable — no implementation exists yet (pre-P1 stories).

## Validation Gate Result

**FAIL** — 6 actionable findings (SC-01..05, SC-07; SC-06 known-open), all localized
value/index updates; no structural damage. Fix SC-01..05 and SC-07, then recheck the
four depth sites and the ARCH-INDEX aggregate to converge to PASS.

## Overall Metrics

- Checks executed: 13 categories, all evaluated; 0 skipped.
- Findings: 7 (5 Medium, 2 Low); 1 INFO note; 0 Critical.
- Sync rate: 38/38 VPs indexed; 145/145 BC titles synced; 1/38 VP↔BC asymmetry (known).

## Appendix: Validation Methodology

Scripts (session scratchpad): VP `bcs:` extraction vs full-text BC-body citation scan;
H1/BC-INDEX/PRD title triple-match with escaped-pipe handling; registry-key extraction
(wildcard-aware) vs dotted-key sweep of 145 BC bodies; git-diff-bounded value sweeps
(`995`, `1,000`, `rebuild_excess`, `ps_timeout`, Tier C/OD-149, "29-byte", `D4-EX`,
`Repr(-0.0)`, ARCH-06 signature list). Inputs hashed as `859ca5` (diff-stat of the
checked tree vs `6fa2b38`).
