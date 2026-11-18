---
document_type: behavioral-contract
level: L3
version: "1.3.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "278b2ba"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-077"
parity_class: byte-exact
confidence: M
lifecycle_status: active
introduced: "0.1"
modified:
  - "pass-3 remediation (ADV-P3-B10): ARCH-03 anchor normalized to the stable #caches fragment; 2026-11-18T02:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.01.009: Side effects run in legacy order; a degrade keeps earlier writes

## Description

One refresh performs its cache writes and its render steps in exactly legacy `main()`'s order, interleaving the
render steps that can fault between the writes. When a step degrades (BC-1.01.001), every write made by earlier
steps stays on disk and no later write happens, so a degraded refresh leaves the same cache files as legacy.

## Preconditions

1. Configuration resolved (step 0 below). A config error stops before step 1 with **no** writes (D4-EX-3,
   BC-2.02.001).
2. The cache directory is `paths.cache_dir` (OD-101); files are compared with legacy's by file name (BC-6.03.002).
3. One clock value per refresh: Go reads `Env.Now` once and passes it down (design IM-14); output-neutral under the
   harness's frozen clock.

## Postconditions

1. Steps run in this order (design §3.1; P3r1 §A8):

   | # | Step | Legacy | Write | Can degrade? |
   |---|------|--------|-------|--------------|
   | 0 | config resolved | import, SL:73-100 | none | D4-EX-3 line, before any write |
   | 1 | stdin decode | SL:1201-1206 | none | no (`{}` on failure) |
   | 2 | transcript parse | SL:1213 | mix cache at the end (SL:1150) | CP-S14/S16 |
   | 3 | `effective_rl` | SL:1216 | session cache (`rl`, `rl_ts`) when stdin carries a non-empty dict (SL:307-308) | no catalogued vector; foreign-cache CP-C01/C02 only (Q-b)¹ |
   | 4 | metrics sample, when rows >= 2 | SL:1217-1218 | session cache (fetch result or `up: false`) | no catalogued vector; foreign-cache CP-C03/C04 only (Q-b)¹ |
   | 5 | row-2 render, only under the width rule | SL:1224-1227 | none | CP-N01/N02 |
   | 6 | window start, only with a truthy `session_id` | SL:1229 | may write `proc_start` | no catalogued vector; foreign-cache CP-C01 only (non-dict cache at SL:273-275, outside its try) (Q-b)¹ |
   | 7a | badge, model, project; git segment | SL:441-462, 411 | git cache | CP-S01..S04 (S04 before the git write); foreign-cache CP-C08 (string `ts` / array cache — BC-1.02.005 EC-009/EC-010) (Q-b)¹ |
   | 7b | thermometer, composition, cache hit, limits, lines, timer, window age, tokens | SL:463-600 | none | CP-S05..S13 |
   | 7c | `record_cost`, then `cost_thresholds` | SL:606-607 | cost history | CP-S15 (before the write); foreign-cache CP-C09/C10 fault **after** the record_cost write (Q-b)¹ |
   | 7d | `$`, `$/h`, ⛏ | SL:608-636 | none | no |
   | 8 | trim, surrogate check, single stdout write | SL:1232-1234 | stdout | CP-S17 (after every write) |

   ¹ Foreign-cache shapes CP-C01..C10 (BC-1.06.001 EC-001) are out of parity scope per owner ruling **Q-b** (P3r2
   ruling b): on caches Go authored itself these vectors are unreachable (the Go writer emits legacy's exact
   format), and Go's behavior on foreign cache shapes is a documented known difference, not a byte-parity
   obligation. Within step 7c the within-step order still holds for CP-C10: record_cost writes first, then
   cost_thresholds faults (SL:606-607).

2. A degrade at step k leaves the writes of steps 1..k-1 exactly as written and performs none of steps k..8. (For
   the out-of-scope foreign-cache classes¹ this holds at step granularity with one within-step exception: a CP-C10
   fault in `cost_thresholds` happens after step 7c's own record_cost write.)
3. Each write uses legacy's exact file format and in-file key order (BC-1.06.001; key order inherited from earlier
   writes within the same refresh, BC-1.04.020).
4. Later steps re-read files written earlier in the same refresh (step 4 re-reads step 3's session cache; step 6
   re-reads it again). A write that failed on disk stays invisible to the later read (no in-memory overlay;
   BC-1.06.002).

## Invariants

1. Order is fixed; no step is reordered, parallelized or skipped for performance.
2. stdout is written once, at step 8, or the degraded line replaces it.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Row-2 crash (CP-N01, KV NaN) | mix cache and session cache written; no `proc_start`, no git cache, no cost-history write |
| EC-002 | Thermometer crash (CP-S06, `used_percentage` NaN) | git cache written; cost history **not** written |
| EC-003 | Lone surrogate at output (CP-S17) | every write of the refresh done, then degraded line |
| EC-004 | Wrong-shape transcript line (legacy CP-T01..T07 degrade at step 2 and stay sticky) | Go does **not** degrade at step 2 — approved deviation **D4-EX-2** (BC-1.03.018, legacy BC-SL-098). Excluded from the parity diff by the OD-105 exclusion entry `D4-EX-2`, covered by the 21 table rows of BC-1.03.019 plus BC-1.03.020/021 rows |
| EC-005 | Invalid config value (legacy CP-X01/X02 crash at import) | Go: D4-EX-3 line at step 0, no writes — approved deviation **D4-EX-3**, OD-105 exclusion entry `D4-EX-3`, tests `TestConfigError_D4EX3_{Number,Boolean,URL,Enum}` (one per class with a dedicated grammar; number-grammar and theme/SGR are pinned by their class contracts BC-2.02.003 / BC-2.01.003; register closed at six) |
| EC-006 | Session id with `/` (failed atomic replace) | legacy leaks an mkstemp temp file, Go removes it — owner-ruled **temp-file** difference (OD-110), excluded only from the cache-file comparison (BC-6.03.003); stdout unaffected |
| EC-007 | rows = 1 | step 4 and 5 skipped (no metrics write) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| stdin `{}`, rows 2, metrics URL at a closed port, empty cache | 2-row output (BC-1.01.003); cache dir afterwards holds only `statusline-nosession.json` = `{"fetch_ts": <now>, "up": false}` | happy-path |
| Cache seeded `statusline-s9.json` = `{"proc_start": 900.0}`; git repo dir with `.git/HEAD` = `ref: refs/heads/main`; stdin `{"session_id":"s9","model":{"id":"claude-sonnet-x","display_name":"S"},"workspace":{"project_dir":"<repo>"},"context_window":{"used_percentage":NaN},"cost":{"total_cost_usd":1.5}}`; rows 1; prefixes `claude-sonnet` | degraded 29 bytes; afterwards `statusline-git-<sha1(dir)[:16]>.json` = `{"ts": <now>, "branch": "main"}` exists, `statusline-s9.json` unchanged, **no** `cost-history.json` | edge-case |
| Same stdin with `used_percentage` 40 | renders; `cost-history.json` now exists | happy-path |
| `{"session_id":"s1","model":{"display_name":"\ud800"},"rate_limits":{"five_hour":{"used_percentage":1,"resets_at":9999999999}}}`, rows 1 | degraded; `statusline-s1.json` holds exactly `rl` and `rl_ts` (probe pinned: harness fake `ps`, no `claude` ancestor — BC-3.02.002 case I4 — so no `proc_start` key) | error |
| Multi-step case (BC-6.02.002): compare every named cache file after every step | identical per-step cache bytes Python vs Go | edge-case |

Rows 1-4 verified 2026-11-15 on CPython 3.11.7 (live clock; under the harness `<now>` is `HYLO_TEST_NOW`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-008 | For every CP site k, the set of files written equals the writes of steps < k | table test over CP-S/CP-N triggers (multi-step harness, design §5.3) |
| VP-009 | Per-step cache bytes match legacy across the corpus | Tier A differential |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009, CAP-011 |
| L2 Domain Invariants | DI-007, DI-008 |
| Architecture Module | `internal/statusline` orchestrator `Render` (`statusline.go`) (BC-COMPONENT-MAP: internal/statusline/statusline.go (side-effect order) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`main` (SL:1200-1235); write sites SL:1150, 307-308, 351/355, 287-288, 411, 606 |
| Legacy contract | BC-SL-077 (new P3r1 §A8; index P3r4 §7.3); crash catalogue P3r1 §B |
| Decisions | D4; D4-EX-2 (P3r2 §0 (c)); D4-EX-3 (OD-102/OD-114); OD-105, OD-110 exclusions; OD-101 cache dir |

## Related BCs (Recommended)

- BC-1.01.001 — composes with (the degrade point)
- BC-1.06.001, BC-1.06.002 — depends on (cache write format, failed replace)
- BC-1.04.013, BC-1.04.020 — related to (metrics step and key order)
- BC-1.05.004 — related to (record_cost write at step 7c)
- BC-2.02.001 — related to (step 0)
- BC-1.03.018, BC-1.03.019 — related to (D4-EX-2 at step 2)
- BC-6.03.002, BC-6.03.003, BC-6.03.004 — verified by (per-step comparison, temp-file and exclusion machinery)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#caches` — internal/statusline/statusline.go (side-effect order) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — frame skeleton (design step S2), completed in goldens/burn-down (step S8)

## VP Anchors (Recommended)

- VP-008 — writes-before-fault property; VP-009 — per-step differential (VP-007 dropped from both rows as a
  mechanical citation: VP-007 is determinism, not effect order — pass-1 finding ADV-P1-B11)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1200-1235 and callees) |
| **Confidence** | medium (design §8: exact interleaving of writes and degrade points; pinned for the listed vectors) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: order follows statement order in `main()` and callees
- **assertion**: pinned runs 2026-11-15 (CP-S06, CP-S17, `{}` rows 2)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads + writes (four cache families, stdout) |
| **Global state access** | filesystem, clock, env |
| **Deterministic** | no (clock, metrics, process tree) — deterministic under the harness seams |
| **Thread safety** | n.a. |
| **Overall classification** | effectful shell (ordered effect script around pure widgets) |

#### Refactoring Notes

Pure widgets plus one ordered effect script (design §3.1); the script stops at the first `errDegraded`.
