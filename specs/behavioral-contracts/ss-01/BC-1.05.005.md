---
document_type: behavioral-contract
level: L3
version: "1.4.0"
status: draft
producer: product-owner
timestamp: 2026-11-18T18:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - semport/hylo-legacy/hylo-legacy-pass-4-nfr-catalog.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "530237d"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:cost_thresholds (SL:240-262)"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-029"
parity_class: "byte-exact"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.3 2026-11-17: pass-2 remediation ADV-P2-C2-05 (min_sessions/percentiles ranges; OD-162)"
  - "1.3.1 2026-11-18: pass-3 remediation ADV-P3-C2-01 (foreign-history overflow EC-011) + ADV-P3-C2-02 (OD-160 on EC-010) + ADV-P3-C2-07 (percentile ordering rule)"
  - "1.3.2 2026-11-18: pass-5 remediation ADV-P5-C2-10 (EC-011 extended to the exact-int api_ms leg; crash ids CP-O10/CP-O11 named) and ADV-P5-C2-17 (DI-012 + VP-012 closure citations) and ADV-P5-C2-20 (stale architect-carry note removed) and design call 16 (rate_min_api_ms values Int > 0)"
  - "1.3.3 2026-11-18: pass-7 remediation ADV-P7-C2-10 (EC-011 overflow threshold corrected to >= 2**1024 − 2**970, matching BC-1.05.004 PC4 / BC-1.05.007 PC6)"
  - "1.3.4 2026-11-18: pass-8 remediation ADV-P8-C2-05 (DI-008 lifted into the L2 row — the EC-011 CP-O10/CP-O11 degrades ride the never-blank ladder)"
  - "1.3.5 2026-11-18: pass-9 remediation ADV-P9-C2-03 cross-reference: the EC-011 threshold citation now points at BC-1.05.004 PC4 (skip moved to the write step)"
  - "1.3.6 2026-11-18: pass-10 remediation ADV-P10-C2-06 (PC4 names the registered key statusline.cost.percentiles beside its (0.75, 0.95) literals, Pre 3 — the literals spell the default) + ADV-P10-C2-12 sibling sweep (PC3's 3.6e6 ms-per-hour factor carries the unit-constant note, BC-1.05.002 Pre 4)"
  - "1.3.7 2026-11-18: pass-10 remediation ADV-P10-C2-11 reciprocity (VP-001 row added to Verification Properties for the history-borne CP-O10/CP-O11 overflow degrade legs, EC-011; VP Anchors entry; VP-001 bcs: synced in the same burst, residual sweep)"
  - "1.3.8 2026-11-21T09:00:00Z: pass-11 residual — the Pre 3 defaults re-spelled to the env spellings {\"cc\":300000,\"other\":1800000} (T-023) and [0.75,0.95] (T-024; PC4's default statement follows), matching the interface-definitions.md Default cells exactly (pass-11 A09/call 4); no behavioral change"
  - "1.3.9 2026-11-21T10:00:00Z: pass-12 remediation ADV-P12-C2-09 (modified list restored to ascending version order — the 1.3.8 entry had been inserted before 1.3.7; no behavioral change)"
  - "1.4.0 2026-11-21T11:30:00Z: pass-13 sync closure — Owning component line and Purity Classification I/O cell respelled to the ARCH-03 declared cost API (§Interfaces, 'package internal/cost — DECLARED API'): internal/cost is pure core with no I/O; internal/statusline loads the cost-history file through its CacheStore before the call, step-7c record-before-percentile order noted (sync-check adv-p13 finding 1, call-7 residual); no behavioral change"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.05.005: cost_thresholds p75/p95 percentiles

## Description

For the client-view lane, the status line computes two percentile pairs from the cost
history, excluding the current session: one over session dollar totals and one over
burn rates ($ per model hour). Each pair is `(p75, p95)` by floor-index selection on the
sorted list (no interpolation), or None when fewer than the minimum number of
qualifying sessions exist (cold start).

## Preconditions

1. Called only when the lane is known (`dgx` or `anth`), after `record_cost`
   (SL:607).
2. History loaded with the BC-1.06.001 load (error → `{}`); `sessions` = `h.sessions`
   or `{}` when absent/falsy (SL:245).
3. Config (legacy defaults): `statusline.cost.window_s` = 2,592,000 (30 d, T-018);
   `statusline.cost.min_usd` = 1.0 (T-019); `statusline.cost.min_sessions` = 10
   (T-020, inclusive; OD-162 range: Int ≥ 1 — 0 is a number-range config error
   because with an empty qualifying list Python indexes `v[int(0.75 × −1)]` = `v[0]`
   of `[]` and raises IndexError, SL:257-261); `statusline.cost.rate_min_api_ms` =
   `{"cc":300000,"other":1800000}` (env spelling, pass-11 residual; T-023);
   `statusline.cost.percentiles` = [0.75,0.95] (env spelling; T-024; OD-162 range,
   ordering leg completed by owner ruling 2026-11-18, ADV-P3-C2-07:
   each a finite Float in [0, 1] — q > 1 overflows the index
   (`int(q × (n−1)) ≥ n` → IndexError) and q < 0 wraps into Python negative indexing,
   so both are number-range config errors — and the pair must be **ascending with
   equality allowed**: first (yellow) <= second (red); a descending pair such as
   (0.95, 0.75) is a number-range config error (D4-EX-3 class; ratified in
   interface-definitions.md's `statusline.cost.percentiles` row, pass-5 ADV-P5-C2-20).
   The `statusline.cost.rate_min_api_ms` map: each value Int > 0 (pass-5 call 16,
   ADV-P5-C2-08) — with a gate value of 0 or less a recorded `api_ms` of 0 (or `false`,
   which counts as a number) passes the gate and Python raises ZeroDivisionError at the
   divide (SL:255; the render-path analogue at SL:623 degrades the line).

## Postconditions

1. For each entry `(k, e)` in file order, skip it if `k == sid`, or `e.lane != lane`,
   or `now - e.get("ts", 0) > window_s` (strict: an entry exactly 30 d old counts)
   (SL:246-247).
2. Skip it if `e.usd` is not a number (bool counts) or `usd < min_usd` (SL:248-250).
3. Append `usd` to the dollar list (SL:251). If `e.api_ms` is a number and `api_ms >=
   need`, with `need = rate_min_api_ms.cc` when `e.src == "cc"` and `.other` for every
   other src (including absent), append `usd / (api_ms / 3.6e6)` to the rate list
   (SL:252-255; the ms-per-hour factor 3.6e6 is a unit constant — named constant, not
   config, the BC-1.05.002 Pre 4 note; ADV-P10-C2-12 sibling sweep).
4. Each list independently: `n < min_sessions` → None; else sort ascending and return
   `(v[int(lo * (n - 1))], v[int(hi * (n - 1))])` with `(lo, hi)` from
   `statusline.cost.percentiles` (default [0.75,0.95], Pre 3 — the literals in the
   legacy line spell the default), the index computed as a float64 product truncated
   toward zero, exactly as Python does (SL:257-261).
5. Return `(usd_pair | None, rate_pair | None)` (SL:262).

## Invariants

1. Pure function of (history bytes, lane, sid, now, config); no write.
2. The index rule equals integer `floor(75(n-1)/100)` / `floor(95(n-1)/100)` for every
   n in 10..400 (pinned); Go uses the float form, which equals Python for every n.
3. Self-exclusion compares the stored key with the sid (string sid ⇒ exact string
   compare; numeric sid ⇒ BC-1.05.006).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | n = 9 qualifying | None (cold start) |
| EC-002 | n = 10 | pair present; indices (6, 8) |
| EC-003 | n = 11 / 20 / 21 / 41 / 81 | indices (7,9) / (14,18) / (15,19) / (30,38) / (60,76) |
| EC-004 | entry `ts = now - 2592000` exactly | counted; `now - 2592000.001` excluded |
| EC-005 | entry usd `"5"` (string), or 0.99 | not counted in either list |
| EC-006 | `cc` entry with api 400,000 | counted in rates (cc gate 300,000) |
| EC-007 | backfill entry with api 1,000,000 | dollar list only (other gate 1,800,000) |
| EC-008 | entry usd `Infinity` | counted; sorts last |
| EC-009 | entry usd `NaN` (only writable by the backfill tool, BC-BF-012, or by hand) | Ruled OD-138: pin legacy byte-for-byte; the expected bytes come from the CPython 3.11 oracle (frozen clock, temp HOME, synthetic history; oracle run 2026-11-15). For the 10-session cc history [`sess-00`=NaN, `sess-01..09` = 90.0…10.0] (file order) with `ts = now - 3600`, `api_ms = 400000`, `src = cc`, `now = 1794615009.0`: sorted order `[NaN, 10, …, 90]` and thresholds `((60.0, 80.0), (540.0, 720.0))`. For file order [`10.0 … 90.0`, NaN]: sorted `[10, …, 90, NaN]` and thresholds `((70.0, 90.0), (630.0, 810.0))`. The outcome is deterministic per exact file order (Python `sorted` stability); Go must reproduce it per order, table-tested over both pinned histories |
| EC-010 | corrupt shapes (top level, `sessions` or entry not an object; entry `ts` non-numeric) | CP-C09/CP-C10: out of parity scope (P3r2 ruling b); the foreign-cache class carries named exclusion id **OD-160** (DI-012 named-deviation rule) |
| EC-011 | foreign history holds an exact-int `usd` **or an exact-int `api_ms`** >= 2**1024 − 2**970 (the smallest magnitude Python's int→float coercion raises at — the same threshold BC-1.05.004 PC4 and BC-1.05.007 PC6 pin; ADV-P7-C2-10) recorded by legacy `record_cost` (SL:234-237 stores `api_ms` unrounded) or by hand | any later refresh on the lane whose qualifying entry passes its API-time gate raises OverflowError at `usd / (api / 3.6e6)` (SL:255 — the int→float coercion of the giant exact int; no try in `cost_thresholds`) → degraded line on **every** qualifying refresh for up to the 30 d window (ADV-P3-C2-01). Crash ids: the `usd` leg is **CP-O10**, the `api_ms` leg **CP-O11** (taxonomy bearer note: the history-borne raise happens at the SL:255 division, not at SL:616/623; ADV-P5-C2-10). Foreign-history class (exclusion id **OD-160**): hylo's writer never writes it (OD-166, BC-1.05.004), so this is a Go table test, not a parity obligation |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| BC-1.05.008 21-key seed, lane anth, sid `sess-self`, now 1794615009.0 | `((24.0, 30.0), (20.0, 26.0))` (16 dollar values, 14 rates) | happy-path |
| same seed, lane dgx | `(None, None)` | edge-case |
| 10 `cc` sessions, rates [5, 8, 11, 14, 17, 19, 20, 23, 26, 40] at 1 h | `((20.0, 26.0), (20.0, 26.0))` | edge-case |
| 12 dollar entries usd 10…21, no rate-eligible entries | `((18.0, 20.0), None)` | edge-case |
| dgx lane, 10 entries usd 5…50 step 5, api 1,800,000 + i (i = 0…9), backfill src | `((35.0, 45.0), (69.99976666744445, 89.99960000177776))` | edge-case |
| empty / missing history file | `(None, None)` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-021 | p75 ≤ p95 whenever a pair is returned (finite inputs) — guaranteed by the ascending-config rule (ADV-P3-C2-07) | Go property test (testing/quick) |
| VP-021 | Go index equals `int(q*(n-1))` computed by CPython for n in 1..10,000 | manual (generated table) |
| VP-012 | The named deviation this contract carries — exclusion id `OD-160` (EC-010/EC-011 foreign-history crash shapes out of parity scope) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-160` entry and its riding table test `TestForeignCacheShape_OD160_Vectors`, and the mutation test fails closed if that entry is dropped (ADV-P5-C2-17) | property test (VP-012, go test) |
| VP-001 | The promised output set holds on the history-borne CP-O10/CP-O11 overflow degrade legs (EC-011): render output or the 29-byte degraded line — never blank, exit 0 (DI-008) | fault-injection ladder (assertPromisedOutputSet, DI-008) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 (percentile bands) |
| L2 Domain Invariants | DI-007, DI-008 (the EC-011 CP-O10/CP-O11 OverflowError degrades ride the never-blank ladder: 29-byte line, exit 0; ADV-P8-C2-05), DI-012 (foreign-history shapes OD-160 under the named-deviation rule) |
| Architecture Module | `internal/cost` history.go `ForLane` (BC-COMPONENT-MAP: internal/cost/history.go (p75/p95; NaN usd OD-138) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:cost_thresholds (SL:240-262); constants (SL:217-221) |
| Legacy contract | BC-SL-029 (P3r1 row 58; index table P3 deep r1; goldens P3r3 §4.1) |
| Thresholds | T-018 (30 d, owner design), T-019 ($1, derived from probe data), T-020 (10, owner decision), T-023 (300,000/1,800,000 ms, derived), T-024 (p75/p95 floor index, owner design) |
| Decisions | D4, D15, OD-101, OD-138 (NaN usd pinned byte-for-byte from the oracle) |

## Related BCs (Recommended)

- BC-1.05.001 / BC-1.05.002 — consumed by (colours)
- BC-1.05.004 — depends on (runs after the record)
- BC-1.05.006 — related to (numeric sid self-exclusion)
- BC-1.05.008 — verified by (goldens)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#effect-step-script-design-doc-31-normative` — internal/cost/history.go (p75/p95; NaN usd OD-138) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost history (filled by story-writer)

## VP Anchors (Recommended)

- VP-021 — percentile index equivalence
- VP-001 — never-blank/exit-0 ladder; the history-borne EC-011 CP-O10/CP-O11 legs ride it (ADV-P10-C2-11)


#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (cost_thresholds (SL:240-262)) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: lane/window/min-usd filters and the `len(v) < COST_MIN_N` cold-start return (SL:245-256)
- **inferred**: percentile index rule re-executed against CPython 3.11.7 (2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none in hylo — the legacy function only reads the history file (SL:240-262); per ARCH-03's declared cost API (§Interfaces, 'package internal/cost — DECLARED API') the scan is pure over the loaded history passed in, and `internal/statusline` loads it through its `CacheStore` |
| **Global state access** | none |
| **Deterministic** | yes (given samples and a store fake) |
| **Thread safety** | Safe for concurrent use (store injected) |
| **Overall classification** | boundary |

Owning component `internal/cost` (BC-COMPONENT-MAP: cost/history.go (p75/p95; NaN usd OD-138) - ARCH-03); per ARCH-03's declared cost API ('package internal/cost — DECLARED API' in the §Interfaces section, ADV-P13-A02 / orchestrator call 7), the package is pure core with no I/O — `CostThresholds` scans the loaded history passed in and returns the pairs, and `internal/statusline` loads the cost-history file through its `CacheStore` before the call (step 7c: the record runs before the percentile read).
