---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - ../semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md
  - ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - ../semport/hylo-legacy/hylo-legacy-pass-4-nfr-catalog.md
  - ../semport/hylo-legacy/statusline-target-design.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-029"
parity_class: "byte-exact"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified: []
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
   (T-020, inclusive); `statusline.cost.rate_min_api_ms` = `{cc: 300000, other:
   1800000}` (T-023); `statusline.cost.percentiles` = (0.75, 0.95) (T-024).

## Postconditions

1. For each entry `(k, e)` in file order, skip it if `k == sid`, or `e.lane != lane`,
   or `now - e.get("ts", 0) > window_s` (strict: an entry exactly 30 d old counts)
   (SL:246-247).
2. Skip it if `e.usd` is not a number (bool counts) or `usd < min_usd` (SL:248-250).
3. Append `usd` to the dollar list (SL:251). If `e.api_ms` is a number and `api_ms >=
   need`, with `need = rate_min_api_ms.cc` when `e.src == "cc"` and `.other` for every
   other src (including absent), append `usd / (api_ms / 3.6e6)` to the rate list
   (SL:252-255).
4. Each list independently: `n < min_sessions` → None; else sort ascending and return
   `(v[int(0.75 * (n - 1))], v[int(0.95 * (n - 1))])` with the index computed as a
   float64 product truncated toward zero, exactly as Python does (SL:257-261).
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
| EC-010 | corrupt shapes (top level, `sessions` or entry not an object; entry `ts` non-numeric) | CP-C09/CP-C10: out of parity scope (P3r2 ruling b) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| BC-1.05.008 20-session seed, lane anth, sid `sess-self`, now 1794615009.0 | `((24.0, 30.0), (20.0, 26.0))` (16 dollar values, 14 rates) | happy-path |
| same seed, lane dgx | `(None, None)` | edge-case |
| 10 `cc` sessions, rates [5, 8, 11, 14, 17, 19, 20, 23, 26, 40] at 1 h | `((20.0, 26.0), (20.0, 26.0))` | edge-case |
| 12 dollar entries usd 10…21, no rate-eligible entries | `((18.0, 20.0), None)` | edge-case |
| dgx lane, 10 entries usd 5…50 step 5, api 1,800,000 + i (i = 0…9), backfill src | `((35.0, 45.0), (69.99976666744445, 89.99960000177776))` | edge-case |
| empty / missing history file | `(None, None)` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | p75 ≤ p95 whenever a pair is returned (finite inputs) | proptest |
| VP-TBD | Go index equals `int(q*(n-1))` computed by CPython for n in 1..10,000 | manual (generated table) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 (percentile bands) |
| L2 Domain Invariants | DI-007 |
| Architecture Module | `internal/cost` history.go `ForLane` (filled by architect) |
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

- `architecture/[cost].md#for-lane` — (filled by architect)

## Story Anchor (Recommended)

S-N.MM — cost history (filled by story-writer)

## VP Anchors (Recommended)

- VP-TBD — percentile index equivalence
