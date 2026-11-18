---
artifact_type: verification-property-index
document_type: vp-index
level: L4
version: "1.15"
status: draft
producer: architect
timestamp: 2026-11-19T16:00:00Z
phase: 1b
inputs: [behavioral-contracts/BC-INDEX.md, architecture/ARCH-INDEX.md, domain-spec/invariants.md, prd-supplements/nfr-catalog.md, behavioral-contracts/BC-ALLOCATION.md]
input-hash: "784a8a4"
traces_to: ../architecture/ARCH-INDEX.md
lifecycle_status: active
introduced: "1.0"
modified:
  - "1.2 2026-11-17: VP-038 added (ADV-P1); catalog and BC coverage map regenerated from all 38 VP files"
  - "1.3 2026-11-17: BC coverage map reconciled \u2014 BC-1.03.002 row drops VP-018; VP-018/VP-010 bcs aligned (BC-1.06.002 row already carried VP-010)"
  - "1.4 2026-11-18: pass-2 rebuild - catalog regenerated from all 40 VP files (VP-039/VP-040 added); BC coverage map regenerated for all 153 BCs; BC-1.07.008 added to VP-003 bcs (shared-guard write-failure leg)"
  - "1.5 2026-11-18T05:30:00Z: BC-1.07.006 added to VP-028 bcs (shared startswith prefix rule, adv-p2 sync SC-07) - directional residual shrinks to BC-1.01.004 (VP-034) and BC-1.06.001 (VP-022)"
  - "1.6 2026-11-18T06:00:00Z: pass-3 rebuild - catalog regenerated from all 40 VP files; BC-5.01.007 added to VP-023 bcs (cited thrice in that contract's Verification Properties table); coverage map regenerated for all 154 BCs; VP-012 v1.4 rider names aligned to rider BCs (OD-30 rider respelled TestCostHistory_OD30_NumericSidStringKey); known prose-only citation exclusions: VP-022/BC-1.06.001, VP-024/BC-1.07.004, VP-034/BC-1.01.004"
  - "1.7 2026-11-18T15:10:00Z: pass-4 rebuild - catalog regenerated from all 41 VP files (VP-041 added: S1.02 for-all property legs split from VP-028, plan item 18); VP-021 title corrected to 21 seeded sessions (A09/C2-04); VP-007 re-anchored to BC-5.04.003 (A2-10); VP-022 bcs gains BC-1.01.009 and VP-006 bcs gains BC-1.07.003 (A2-11), both enumerated under the prose-only exceptions; VP-012 closed set becomes 11 ids with OD-166 (OD-169)"
  - "1.8 2026-11-18: pass-4 residual sweep \u2014 BC-2.02.003 coverage row gains VP-023 (its Verification Properties table cites VP-023 for the Unicode-14.0-pinned Nd-verdict tables leg, OD-170; VP-023 bcs reciprocated); removal-ruling cross-references of VP-026 (BC-3.01.001/6.01.002/6.02.003) enumerated as prose-only residuals"
  - "1.9 2026-11-18T23:30:00Z: pass-4 sync fix \u2014 SC-05: BC-1.01.002 map row drops VP-001 (that contract removed VP-001 from its VP Anchors, ADV-P4-B11/A2-16; VP-001 bcs: and Partial coverage reciprocated in the same burst); VP-007 catalog source_bc cell reconciled to BC-5.04.003 (A2-10 follow-through); SC-12: VP-007 in BC-1.01.009 enumerated as a removal-ruling cross-reference; scripted re-sweep (41 VP files \xD7 154 BC bodies) closes the bijection modulo the enumerated residuals"
  - "1.10 2026-11-18T23:45:00Z: ADV-P5 fix (A2-19) \u2014 coverage-map rows completed per the union definition: BC-1.01.009 gains VP-022 and BC-1.07.003 gains VP-006 (both in those VPs bcs: frontmatter); the residual prose no longer excludes them, it records the owed reciprocal BC-body rows"
  - "1.11 2026-11-19T01:00:00Z: SC-13/SC-14 closure (sync-check-adv-p5) \u2014 union-rule completion finished: BC-1.05.007 map row becomes VP-001, VP-021 and BC-1.07.007 becomes VP-001, VP-009, VP-039, matching VP-001 bcs: and those contracts' live BC-body rows (ADV-P5-A2-11/C15 reciprocals); VP-012 v1.10 gains BC-1.04.003 and BC-1.05.005 in bcs: (SC-14 reciprocity; ADV-P5-C2-17 closure citations) and the two corresponding map rows carry VP-012, so the Uncovered-BCs exception list is regenerated to exactly the re-run bijection residue (6 reverse-only edges: VP-022/BC-1.06.001, VP-024/BC-1.07.004, VP-034/BC-1.01.004 design references; VP-026 removal citations in BC-3.01.001, BC-6.01.002, BC-6.02.003); the stale VP-007/BC-1.01.009 exception is dropped \u2014 that body's removal note no longer cites VP-007 by ID"
  - "1.12 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) \u2014 the 1.6 pass-3-rebuild stamp re-dated ascending (it predated the preceding 1.5 adv-p2-sync entry); no behavioral change"
  - "1.13 2026-11-19T12:00:00Z: pass-6 rebuild \u2014 coverage map regenerated: BC-1.02.002/.003/.006/.007/.009/.010/.013/.015 gain VP-041 (ADV-P6-B01, call 10); BC-1.03.006/.007/.010 gain VP-013 (C06); BC-5.02.004 gains VP-006 (A2-17); VP-012 closed set becomes TWELVE ids with OD-181; owed reciprocal BC-body rows enumerated in the residuals prose"
  - "1.14 2026-11-19T14:00:00Z: pass-6 residual sweep \u2014 union re-machine-checked: 254 directed VP\u2192BC bcs: edges, 0 forward-only; pass-6 owed rows all delivered and disk-verified (BC-5.02.004's VP table gains VP-006; the eight BC-1.02.x VP-041 rows and three BC-1.03.x VP-013 rows verified on disk); map rows for BC-1.03.006/.007/.010 gain VP-012; VP-012 bcs: gains BC-1.03.006/.007/.010 (reciprocity over exception-listing); Uncovered-BCs exception list reduced to exactly the standing residue (3 design references + 3 removal-note citations)"
  - "1.15 2026-11-19T16:00:00Z: sync-check adv-p6 closure (SC-21) \u2014 reciprocity over exception-listing: VP-019 bcs: gains BC-1.01.009 (PC2 names the swap legs' Python-written history), VP-012 bcs: gains BC-1.06.001 (PC-1 cites the closure check), VP-018 bcs: gains BC-2.01.004 (PC-11 key cross-reference); the three corresponding map rows gain those VP ids and the union re-machine-checks at 257 directed bcs: edges, 0 forward-only, residue exactly the standing 3 design references + 3 removal-note citations; no catalog or class changes"
---

# VP-INDEX: hylo P1 verification properties (catalog source of truth)

> Generated by the architect in create-architecture Pass 2 (2026-11-16); regenerated
> 2026-11-18T15:10:00Z from all 41 revised VP files (VP-001..VP-041; every cell scripted from the
> VP file's frontmatter/body — Home = the ARCH docs in the VP's `inputs:`, Method =
> leading term of the body "Method" bullet with the v1.5 bucket dispositions). One file
> per property under `verification-properties/`; this index is the catalog source of truth
> (vp_index_is_vp_catalog_source_of_truth). Coverage: all 154 behavioral contracts
> (BC-INDEX, stage 3) are covered by at least one VP; the per-BC map is below. Derivation
> sources: the ADRs' verification-feasibility assessments (AD-01..13), domain invariants
> DI-007/DI-008/DI-010/DI-012 (P1 surfaces), NFR-001..006, BC-ALLOCATION "Verification
> Properties" obligations (D4-EX-1/2/3), and the approved-deviation closed set
> (OD-105/110/136).

## Totals

- **41 VPs**, all status draft, feasibility feasible.
- **By property class:** invariant 33 (32 + VP-041), safety 7 (VP-001, VP-002, VP-003, VP-005, VP-011, VP-015, VP-018), performance 1 (VP-036)
  (VP-011's body class reads "safety, not liveness (A2-26)"; the former liveness cell
  predates that amendment).
- **By primary verification method:** unit/table 20 (['VP-001', 'VP-003', 'VP-004', 'VP-008', 'VP-013', 'VP-014', 'VP-016', 'VP-017', 'VP-018', 'VP-020', 'VP-026', 'VP-027', 'VP-029', 'VP-030', 'VP-031', 'VP-032', 'VP-033', 'VP-034', 'VP-035', 'VP-039']), property/fuzz 13 (['VP-002', 'VP-005', 'VP-006', 'VP-007', 'VP-011', 'VP-012', 'VP-015', 'VP-023', 'VP-024', 'VP-025', 'VP-038', 'VP-040', 'VP-041']), golden 3 (['VP-010', 'VP-021', 'VP-028']), parity 2 (['VP-009', 'VP-019']), static analysis 1 (['VP-022']), measured 1 (['VP-036']), CI observation 1 (['VP-037']). Regenerated 2026-11-18T15:10:00Z from the
  Catalog Method column: buckets are the leading term of each VP's Method bullet
  with the v1.5 dispositions (VP-026 "oracle tables" and VP-039's dense grid bucket as
  unit/table; VP-002/038 are fuzz-led; VP-012's mutation generator is fuzz-family;
  VP-035's CI gate buckets as unit/table).
- **Iron-law honesty:** zero VPs claim a formal proof. The template's Kani/TLA+ path
  is not applicable to this Go cycle; the strongest surfaces (pyfmt, config grammars)
  are marked provable-grade in ARCH-00/06 and are verified by exhaustive
  oracle-generated tables plus property/fuzz targets — empirical, not deductive. Every
  effectful shell (env, filesystem, HTTP, process probes, interpreter spawning) is
  declared testable-only in its VP.
- **Revisit anchor:** VP-022 (DI-007 ledger read-scope absence) carries the OD-125
  REVISIT-at-P7 flag.

## Catalog

| ID | File | Name | Class | Method | Module | source_bc | Home |
|---|---|---|---|---|---|---|---|
| VP-001 | VP-001-never-blank-exit0.md | Never-blank, exit-0 rendering under every fault trigger | safety | unit/table | internal/statusline (guard), cmd/hylo | BC-1.01.001 | ARCH-00/ARCH-03 |
| VP-002 | VP-002-unknown-flag-one-line.md | Unknown flag renders one-line error, exit 0, never blank (flags before `--`) | safety | property/fuzz | cmd/hylo | BC-4.01.002 | ARCH-01 |
| VP-003 | VP-003-cpx03-write-failure-exit0.md | Degraded-line write failure still exits 0 (named exclusion `cp-x03`) | safety | unit/table | internal/statusline (guard), cmd/hylo | BC-1.01.001 | ARCH-03 |
| VP-004 | VP-004-closed-exit-code-surface.md | Verb-scoped exit-code surface is closed and exhaustively table-tested | invariant | unit/table | cmd/hylo | BC-4.01.001 | ARCH-01 |
| VP-005 | VP-005-stdin-decode-totality.md | stdio codec totality — stdin decode yields a render state; stdout is valid UTF-8 | safety | property/fuzz | internal/statusline (input.go, guard.go), internal/pyfmt | BC-1.01.002 | ARCH-03/ARCH-06 |
| VP-006 | VP-006-json-depth-budgets.md | Per-call-site JSON recursion depth budgets hold exactly | invariant | property/fuzz | internal/pyfmt (json.go) | BC-5.02.003 | ARCH-06 |
| VP-007 | VP-007-render-determinism-seams.md | Render is deterministic under injected seams | invariant | property/fuzz | internal/statusline (Render, Env) | BC-5.04.003 | ARCH-03 |
| VP-008 | VP-008-effect-order-preservation.md | Effect order is exactly legacy's; a crash at step k keeps writes 1..k-1 | invariant | unit/table | internal/statusline (Render orchestrator) | BC-1.01.009 | ARCH-03 |
| VP-009 | VP-009-tier-a-live-parity.md | Tier A live differential parity — zero unexplained diffs over corpus and captures | invariant | parity | internal/parity | BC-6.03.002 | ARCH-07 |
| VP-010 | VP-010-tier-b-committed-goldens.md | Tier B committed goldens — Python-written, Go matches on every OS | invariant | golden | internal/parity | BC-6.03.001 | ARCH-07 |
| VP-011 | VP-011-tier-c-differential-fuzz.md | Tier C differential fuzz hunts hidden divergence paths | safety | property/fuzz | internal/parity | BC-6.04.003 | ARCH-07 |
| VP-012 | VP-012-exclusion-set-closure.md | Exclusion machinery is closed, glob-free, and fails closed | invariant | property/fuzz | internal/parity | BC-6.03.004 | ARCH-07 |
| VP-013 | VP-013-d4ex2-wrong-shape-tables.md | D4-EX-2 wrong-shape transcript lines — W-predicates and exact expected caches | invariant | unit/table | internal/statusline (transcript parser) | BC-1.03.019 | ARCH-07 |
| VP-014 | VP-014-d4ex1-windows-window-age.md | D4-EX-1 — ⌂ window-age difference on Windows is bounded and tested | invariant | unit/table | internal/platform (proc), internal/statusline (window age) | BC-3.02.001 | ARCH-05/ARCH-07 |
| VP-015 | VP-015-config-resolution-totality.md | Config resolution is total over the environment; the registry is closed | safety | property/fuzz | internal/config | BC-2.01.001 | ARCH-02 |
| VP-016 | VP-016-config-error-classes-line.md | D4-EX-3 config-error classes, line format, and no-cache-writes guarantee | invariant | unit/table | internal/config (errors.go), cmd/hylo | BC-2.02.001 | ARCH-02 |
| VP-017 | VP-017-exactly-one-backend.md | Exactly-one-backend cardinality until P6 | invariant | unit/table | internal/config (backends validator) | BC-2.01.002 | ARCH-02 |
| VP-018 | VP-018-atomic-cache-writes.md | Atomic cache writes — no partial files, temp cleanup, failed replace persists nothing | safety | unit/table | internal/statusline (cache.go), internal/cost | BC-1.06.001 | ARCH-04 |
| VP-019 | VP-019-four-cache-swap-parity.md | Four-cache swap — Python-writes/Go-reads and reverse are byte-identical | invariant | parity | internal/parity (swap), internal/statusline (cache.go) | BC-6.02.004 | ARCH-04/ARCH-07 |
| VP-020 | VP-020-cost-history-integrity.md | Cost-history parse failure — legacy reload; next record regenerates the file | invariant | unit/table | internal/cost | BC-1.05.004 | ARCH-04/ARCH-03 |
| VP-021 | VP-021-cost-colour-goldens.md | Dynamic dollar colours and percentile goldens over 21 seeded sessions | invariant | golden | internal/statusline (cost.go), internal/cost | BC-1.05.008 | ARCH-03 |
| VP-022 | VP-022-ledger-read-scope-absence.md | The status line never reads the ledger (DI-007) — architectural absence, REVISIT P7 | invariant | static analysis | internal/statusline (Env read scope) | BC-1.04.001 | ARCH-03/ARCH-04/ARCH-09 |
| VP-023 | VP-023-pyfmt-num-equivalence.md | pyfmt number semantics equivalent to CPython 3.11 on oracle tables | invariant | property/fuzz | internal/pyfmt (num.go) | BC-5.01.001 | ARCH-06 |
| VP-024 | VP-024-pyfmt-json-equivalence.md | pyfmt JSON byte semantics equivalent to CPython 3.11 | invariant | property/fuzz | internal/pyfmt (json.go) | BC-5.02.001 | ARCH-06 |
| VP-025 | VP-025-pyfmt-str-equivalence.md | pyfmt code-point string ops equivalent to Python semantics | invariant | property/fuzz | internal/pyfmt (str.go) | BC-5.03.001 | ARCH-06 |
| VP-026 | VP-026-pyfmt-time-equivalence.md | pyfmt time semantics equivalent to CPython 3.11 (`_mktime` port, ISO grammar) | invariant | unit/table | internal/pyfmt (time.go) | BC-5.04.002 | ARCH-06 |
| VP-027 | VP-027-frame-width-tables.md | Frame, width, and trim math — breakpoint matrix and Python int grammar for COLUMNS | invariant | unit/table | internal/statusline (width.go, guard frame) | BC-1.01.010 | ARCH-03 |
| VP-028 | VP-028-row1-widget-tables.md | Row-1 widget family — oracle-pinned tables across all thirty contracts | invariant | golden | internal/statusline (row-1 file families) | BC-1.02.001 | ARCH-03 |
| VP-029 | VP-029-transcript-parse-tables.md | Transcript parsing family — turn machine and read-step totals | invariant | unit/table | internal/statusline (transcript*.go, mixcache.go, session.go) | BC-1.03.016 | ARCH-03 |
| VP-030 | VP-030-telemetry-row2-tables.md | Row-2 telemetry family — TTL machine, freshness ladder, NaN crash paths | invariant | unit/table | internal/statusline (sample.go, row2.go, sparkline.go, telemetry.go) | BC-1.04.002 | ARCH-03 |
| VP-031 | VP-031-bounded-resource-caps.md | Bounded per-refresh state — legacy-identical caps | invariant | unit/table | internal/statusline (store caps) | BC-1.03.005 | ARCH-03 |
| VP-032 | VP-032-platform-dir-rules.md | Per-OS directory resolution rules (OD-95/OD-101/OD-144) | invariant | unit/table | internal/platform (paths) | BC-3.01.001 | ARCH-05 |
| VP-033 | VP-033-process-probe-correctness.md | Native process probe correctness per OS | invariant | unit/table | internal/platform (proc_*.go) | BC-3.02.002 | ARCH-05 |
| VP-034 | VP-034-oracle-isolation.md | Oracle isolation — explicit interpreter, from-scratch child env, canary | invariant | unit/table | internal/parity (runner, pyhooks shim) | BC-6.01.001 | ARCH-07 |
| VP-035 | VP-035-corpus-hygiene.md | Corpus hygiene — synthetic committed fixtures only, secret-scan clean | invariant | unit/table | internal/parity (corpus), CI hygiene legs | BC-6.02.001 | ARCH-07/ARCH-08 |
| VP-036 | VP-036-render-latency-p95.md | Render latency p95 <= 25 ms on the owner's Mac target (measured) | performance | measured | internal/statusline (hot path), CI timing report | BC-6.04.002 | ARCH-08 |
| VP-037 | VP-037-three-os-ci-matrix.md | Three-OS CI matrix per change; race-clean Linux/macOS | invariant | CI observation | CI workflow (ARCH-08), in-tree corpus test | BC-6.04.001 | ARCH-08 |
| VP-038 | VP-038-splitlines-bytes-differential.md | SplitLinesBytes equals CPython bytes.splitlines (keepends=False) — corner-table pinned, fuzz self-oracle | invariant | property/fuzz | internal/pyfmt (str.go) | BC-1.03.004 | ARCH-03/ARCH-06 |
| VP-039 | VP-039-elapsed-clock-ulp-agreement.md | Elapsed-clock float computations agree at ulp level across fusion regimes | invariant | unit/table | internal/statusline (subagent elapsed clock) | BC-1.07.007 | ARCH-03 |
| VP-040 | VP-040-frame-width-property-legs.md | Frame, width, and trim — for-all property and Tier C differential legs (BC-1.01.003..007) | invariant | property/fuzz | internal/statusline (width.go, guard frame, term_cols) | BC-1.01.004 | ARCH-03 |
| VP-041 | VP-041-row1-property-legs.md | Row-1 widget family — for-all property, differential, and lint/syscall legs (S1.02) | invariant | property/fuzz | internal/statusline (row-1 file families) | BC-1.02.001 | ARCH-03 |
## BC Coverage Map (154/154; VP ids per BC)

### S1.01 (10)

| BC | VPs |
|---|---|
| BC-1.01.001 | VP-001, VP-003, VP-012 |
| BC-1.01.002 | VP-005, VP-006 |
| BC-1.01.003 | VP-027, VP-040 |
| BC-1.01.004 | VP-027, VP-040 |
| BC-1.01.005 | VP-027, VP-040 |
| BC-1.01.006 | VP-027, VP-040 |
| BC-1.01.007 | VP-027, VP-040 |
| BC-1.01.008 | VP-005 |
| BC-1.01.009 | VP-008, VP-009, VP-019, VP-022 |
| BC-1.01.010 | VP-027 |

### S1.02 (30)

| BC | VPs |
|---|---|
| BC-1.02.001 | VP-028, VP-041 |
| BC-1.02.002 | VP-028, VP-041 |
| BC-1.02.003 | VP-028, VP-041 |
| BC-1.02.004 | VP-012, VP-028, VP-041 |
| BC-1.02.005 | VP-019, VP-028 |
| BC-1.02.006 | VP-028, VP-041 |
| BC-1.02.007 | VP-028, VP-041 |
| BC-1.02.008 | VP-028 |
| BC-1.02.009 | VP-028, VP-041 |
| BC-1.02.010 | VP-028, VP-041 |
| BC-1.02.011 | VP-028 |
| BC-1.02.012 | VP-028 |
| BC-1.02.013 | VP-019, VP-028, VP-041 |
| BC-1.02.014 | VP-028 |
| BC-1.02.015 | VP-028, VP-041 |
| BC-1.02.016 | VP-028, VP-041 |
| BC-1.02.017 | VP-028 |
| BC-1.02.018 | VP-028, VP-041 |
| BC-1.02.019 | VP-028, VP-041 |
| BC-1.02.020 | VP-001, VP-028 |
| BC-1.02.021 | VP-028, VP-041 |
| BC-1.02.022 | VP-028, VP-041 |
| BC-1.02.023 | VP-028, VP-041 |
| BC-1.02.024 | VP-028 |
| BC-1.02.025 | VP-028, VP-041 |
| BC-1.02.026 | VP-001, VP-028 |
| BC-1.02.027 | VP-001, VP-028, VP-041 |
| BC-1.02.028 | VP-028, VP-041 |
| BC-1.02.029 | VP-028 |
| BC-1.02.030 | VP-019, VP-028 |

### S1.03 (21)

| BC | VPs |
|---|---|
| BC-1.03.001 | VP-029 |
| BC-1.03.002 | VP-019, VP-029 |
| BC-1.03.003 | VP-029, VP-031 |
| BC-1.03.004 | VP-006, VP-029, VP-038 |
| BC-1.03.005 | VP-029, VP-031 |
| BC-1.03.006 | VP-013, VP-029, VP-012 |
| BC-1.03.007 | VP-013, VP-029, VP-012 |
| BC-1.03.008 | VP-029 |
| BC-1.03.009 | VP-029 |
| BC-1.03.010 | VP-013, VP-029, VP-012 |
| BC-1.03.011 | VP-029 |
| BC-1.03.012 | VP-029 |
| BC-1.03.013 | VP-029 |
| BC-1.03.014 | VP-029 |
| BC-1.03.015 | VP-012, VP-029 |
| BC-1.03.016 | VP-029 |
| BC-1.03.017 | VP-029 |
| BC-1.03.018 | VP-012, VP-013, VP-029 |
| BC-1.03.019 | VP-012, VP-013, VP-029 |
| BC-1.03.020 | VP-012, VP-013, VP-029 |
| BC-1.03.021 | VP-029 |

### S1.04 (21)

| BC | VPs |
|---|---|
| BC-1.04.001 | VP-022, VP-030 |
| BC-1.04.002 | VP-030 |
| BC-1.04.003 | VP-012, VP-030, VP-031 |
| BC-1.04.004 | VP-030 |
| BC-1.04.005 | VP-030 |
| BC-1.04.006 | VP-030 |
| BC-1.04.007 | VP-030 |
| BC-1.04.008 | VP-030 |
| BC-1.04.009 | VP-030 |
| BC-1.04.010 | VP-030 |
| BC-1.04.011 | VP-030 |
| BC-1.04.012 | VP-030 |
| BC-1.04.013 | VP-030 |
| BC-1.04.014 | VP-001, VP-030 |
| BC-1.04.015 | VP-001, VP-030 |
| BC-1.04.016 | VP-001, VP-030 |
| BC-1.04.017 | VP-030 |
| BC-1.04.018 | VP-030 |
| BC-1.04.019 | VP-030 |
| BC-1.04.020 | VP-019, VP-030 |
| BC-1.04.021 | VP-030 |

### S1.05 (9)

| BC | VPs |
|---|---|
| BC-1.05.001 | VP-021 |
| BC-1.05.002 | VP-021 |
| BC-1.05.003 | VP-021 |
| BC-1.05.004 | VP-001, VP-012, VP-020 |
| BC-1.05.005 | VP-012, VP-021 |
| BC-1.05.006 | VP-012, VP-020 |
| BC-1.05.007 | VP-001, VP-021 |
| BC-1.05.008 | VP-021 |
| BC-1.05.009 | VP-019, VP-020 |

### S1.06 (2)

| BC | VPs |
|---|---|
| BC-1.06.001 | VP-001, VP-012, VP-018, VP-019 |
| BC-1.06.002 | VP-010, VP-012, VP-018 |

### S1.07 (8)

| BC | VPs |
|---|---|
| BC-1.07.001 | VP-002 |
| BC-1.07.002 | VP-005, VP-009 |
| BC-1.07.003 | VP-005, VP-006 |
| BC-1.07.004 | VP-010 |
| BC-1.07.005 | VP-010 |
| BC-1.07.006 | VP-010, VP-028 |
| BC-1.07.007 | VP-001, VP-009, VP-039 |
| BC-1.07.008 | VP-001, VP-003 |

### S2 (13)

| BC | VPs |
|---|---|
| BC-2.01.001 | VP-015 |
| BC-2.01.002 | VP-016, VP-017 |
| BC-2.01.003 | VP-015, VP-016 |
| BC-2.01.004 | VP-015, VP-018 |
| BC-2.01.005 | VP-015, VP-016 |
| BC-2.02.001 | VP-012, VP-016 |
| BC-2.02.002 | VP-012, VP-016 |
| BC-2.02.003 | VP-012, VP-016, VP-023 |
| BC-2.02.004 | VP-012, VP-016 |
| BC-2.02.005 | VP-012, VP-016 |
| BC-2.02.006 | VP-012, VP-016 |
| BC-2.03.001 | VP-004, VP-016 |
| BC-2.03.002 | VP-004, VP-032 |

### S3 (3)

| BC | VPs |
|---|---|
| BC-3.01.001 | VP-032 |
| BC-3.02.001 | VP-012, VP-014, VP-033 |
| BC-3.02.002 | VP-012, VP-033 |

### S4 (3)

| BC | VPs |
|---|---|
| BC-4.01.001 | VP-002, VP-004 |
| BC-4.01.002 | VP-002 |
| BC-4.01.003 | VP-004 |

### S5 (20)

| BC | VPs |
|---|---|
| BC-5.01.001 | VP-023 |
| BC-5.01.002 | VP-023 |
| BC-5.01.003 | VP-023 |
| BC-5.01.004 | VP-023 |
| BC-5.01.005 | VP-023 |
| BC-5.01.006 | VP-023 |
| BC-5.01.007 | VP-023 |
| BC-5.02.001 | VP-024 |
| BC-5.02.002 | VP-024 |
| BC-5.02.003 | VP-006, VP-024 |
| BC-5.02.004 | VP-006, VP-024 |
| BC-5.02.005 | VP-024 |
| BC-5.02.006 | VP-024 |
| BC-5.03.001 | VP-025 |
| BC-5.03.002 | VP-025, VP-038 |
| BC-5.03.003 | VP-025 |
| BC-5.03.004 | VP-025 |
| BC-5.04.001 | VP-026 |
| BC-5.04.002 | VP-026 |
| BC-5.04.003 | VP-007, VP-026 |

### S6 (14)

| BC | VPs |
|---|---|
| BC-6.01.001 | VP-034 |
| BC-6.01.002 | VP-034 |
| BC-6.01.003 | VP-034 |
| BC-6.02.001 | VP-035 |
| BC-6.02.002 | VP-009 |
| BC-6.02.003 | VP-009 |
| BC-6.02.004 | VP-019 |
| BC-6.03.001 | VP-010 |
| BC-6.03.002 | VP-009 |
| BC-6.03.003 | VP-012, VP-018 |
| BC-6.03.004 | VP-012 |
| BC-6.04.001 | VP-010, VP-035, VP-037 |
| BC-6.04.002 | VP-036 |
| BC-6.04.003 | VP-011 |

### Uncovered BCs

None. 154/154 covered (union of VP `bcs:` frontmatter and VP anchors in the BC
bodies' Verification Properties / VP Anchors sections; re-machine-checked
2026-11-19T16:00:00Z after the sync-check adv-p6 closure: 257 directed VP→BC `bcs:`
edges, 0 forward-only, exactly 3 reverse-only VP-table residuals plus the 3
removal-note citations enumerated below — the lists are therefore exactly the
residue). Design references, not citations (excluded by ruling):
VP-022 in BC-1.06.001 (mis-anchor note);
VP-024 in BC-1.07.004 ("VP-024 family" encoder references);
VP-034 in BC-1.01.004 (parenthetical isolation credit).
Removal-note citations:
VP-026 in BC-3.01.001 (EC-010);
VP-026 in BC-6.01.002 (PC text);
VP-026 in BC-6.02.003 (PC text) —
each records the OD-171 `posix-only` tag removal, and VP-026's `bcs:` correctly
excludes those BCs. In this version (SC-21, sync-check adv-p6): VP-019 `bcs:`
gains BC-1.01.009 (PC2 names the swap legs' Python-written cost history),
VP-012 `bcs:` gains BC-1.06.001 (PC-1 cites the closure check), and VP-018
`bcs:` gains BC-2.01.004 (PC-11 rename-retry key cross-reference) — reciprocity
preferred over exception-listing, the SC-13/SC-14 convention — which is why
those three edges no longer appear as residuals. Pass-6 owed reciprocal BC-body rows — all delivered and
disk-verified 2026-11-19 (ADV-P6-B01/C06/A2-17): BC-1.02.002/.003/.006/.007/
.009/.010/.013/.015 VP-table rows carry VP-041; BC-1.03.006/.007/.010 VP rows
carry VP-013 and VP-012; BC-5.02.004's VP row carries VP-006 (its metrics-decode
mode is pinned there). In this version: VP-012 `bcs:` gains BC-1.03.006/.007/.010
(reciprocity preferred over exception-listing, SC-13/SC-14 convention), which is
why those edges no longer appear as residuals. Historical closures (SC-13 /
SC-14, v1.11): the BC-1.05.007 and BC-1.07.007 map rows gained VP-001 per the
union rule; VP-012 `bcs:` gained BC-1.04.003 and BC-1.05.005; the
ADV-P5-A2-19 owed reciprocal rows for BC-1.01.009 (VP-022) and BC-1.07.003
(VP-006) were delivered; the former VP-007/BC-1.01.009 exception was dropped —
that body's removal note no longer cites VP-007 by ID.

## Propagation

Per POLICY 9, derived views (architecture/verification-coverage-matrix.md when created)
propagate from this file. Any VP addition/change lands here and in the VP file in the
same burst; the BC body anchors were back-filled 2026-11-16 (Pass 3 DONE — every BC
file carries VP links in its Verification Properties / VP Anchors body sections;
spot-checked 2026-11-17 across ss-01/02/04/05/06; the one-sided residuals are
re-enumerated under Uncovered BCs above, 2026-11-18T02:27:55Z).
