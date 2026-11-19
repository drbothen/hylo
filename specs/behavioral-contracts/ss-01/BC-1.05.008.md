---
document_type: behavioral-contract
level: L3
version: "1.2.3"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "07d9f83"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:601-625)"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-101"
parity_class: "byte-exact"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified: ["1.2.1 2026-11-18: pass-3 remediation ADV-P3-C2-14 (seed count corrected to 21)", "1.2.2 2026-11-18: pass-8 remediation ADV-P8-C2-15 (every seed row spells its lane explicitly — the committed seed file needs it; anth unless noted)", "1.2.3 2026-11-18: pass-14 remediation ADV-P14-C2-05 (the Owning-components line respelled to the ARCH-00 package table: internal/cost is pure core, no store, no injected seam; internal/statusline owns the file I/O through its CacheStore; no behavioral change)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.05.008: Cost colouring goldens (21 seeded sessions)

## Description

A fixed, synthetic 21-key cost history (12 `s` sessions, 8 `g` filter probes and
`sess-self`) exercises every filter of the percentile
computation (lane, window edge, floor, type, rate gates, self-exclusion) and pins the
exact cost-segment bytes for twelve cost values, including the two documented
colour/number mismatches at the rate boundaries. Five extra scenarios pin cold start,
the inclusive minimum, a missing rate pair, the local lane, and an unknown lane. Go
must reproduce every byte.

## Preconditions

1. Frozen clock `now = 1794615009.0` (harness clock shim, BC-6.01.003).
2. `backends[0].model_prefixes` = `claude-sonnet`; stdin model id `claude-opus-5-5`
   (cloud lane, `anth`) unless noted; stdin carries only `session_id`, `model`, `cost`.
3. The cost history is seeded before each render with the table below (key order as
   listed; all entries `ts = now − 3600` unless noted; `src: "backfill"` unless noted;
   `api_ms` 3,600,000 unless noted). Every row spells its `lane` explicitly — the
   committed seed file carries it (anth unless noted; ADV-P8-C2-15). Golden seed file
   (proposed path): `internal/statusline/testdata/cost/bc-1.05.008-seed.json`,
   synthetic, committed.

| Key | Entry | Counts in $ | Counts in $/h | Why |
|---|---|---|---|---|
| `s01`…`s12` | lane anth, usd 2.0, 4.0, …, 24.0 | yes | yes (rate = usd) | 1 h ≥ 1,800,000 |
| `g13-cc-short` | lane anth, **cc**, usd 30.0, api 400,000 | yes | yes (270 $/h) | cc gate 300,000 |
| `g14-bf-short` | lane anth, usd 30.0, api 1,000,000 | yes | no | other gate 1,800,000 |
| `g15-small` | lane anth, usd 0.99 | no | no | < min_usd |
| `g16-dgx` | lane dgx, usd 100.0 | no | no | other lane |
| `g17-old` | lane anth, usd 50.0, ts = now − 2,592,000.001 | no | no | `now − ts > 30 d` |
| `g18-edge` | lane anth, usd 26.0, ts = now − 2,592,000 | yes | yes | window test strict `>` |
| `g19-str` | lane anth, usd `"5"` | no | no | not a number |
| `g20-noapi` | lane anth, usd 28.0, api `null` | yes | no | no model time |
| `sess-self` | lane anth, **cc**, usd 500.0, ts = now − 10 | no | no | self-exclusion; also throttles its own write, so the seed is not rewritten |

## Postconditions

1. `cost_thresholds("anth", "sess-self")` = `((24.0, 30.0), (20.0, 26.0))` (16 dollar
   values: indices 11 and 14; 14 rates: indices 9 and 12). `cost_thresholds("dgx", …)`
   = `(None, None)`.
2. With `session_id = "sess-self"`, the cost segment (last row-1 part) is exactly the
   bytes in the golden table below (`\e` = 0x1B).
3. `cost-history.json` is byte-identical to the seed after each render (throttle).

## Invariants

1. Colours compare raw values; the display rounds — mismatches at 19.99 and 25.99 are
   legacy behavior and must be reproduced, not fixed (D4).
2. The seed is synthetic (CLAUDE.md public-repo hygiene); no real history is committed.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | 9 qualifying sessions (usd 10…18, 1 h), new sid `x`, usd 25.0, api 3,600,000 | cold start: `\e[33m$25.00\e[0m\e[90m $25.0/h\e[0m`; `x` is recorded first, so for any **other** sid the lane now has 10 → `((16.0, 18.0), (16.0, 18.0))` |
| EC-002 | exactly 10 qualifying | pair present (min_sessions inclusive) |
| EC-003 | 12 dollar entries usd 10…21, `api_ms` null | `((18.0, 20.0), None)`; usd 21.0 at 1 h → `\e[31m$21.00\e[0m\e[90m $21.0/h\e[0m` |
| EC-004 | dgx lane, 10 entries usd 5…50, api 1,800,000 + i; model `claude-sonnet-5-5` | `((35.0, 45.0), (69.99976666744445, 89.99960000177776))`; usd 45.0 at 1,800,000 → `\e[31m$45.00\e[0m\e[31m $90.0/h\e[0m` |
| EC-005 | `backends[0].model_prefixes` set explicitly empty (OD-111 parity rule) | lane None: no `record_cost` write; usd 26.0 at 1 h → `\e[33m$26.00\e[0m\e[90m $26.0/h\e[0m` |

## Canonical Test Vectors

Golden table (sid `sess-self`, seed above):

| usd | `api_ms` | Expected cost segment | Category |
|---|---|---|---|
| 0.5 | 600,000 | `\e[90m$0.50\e[0m\e[90m $3.0/h\e[0m` | edge-case (grey $; rate still shown) |
| 1.0 | 100,000 | `\e[97m$1.00\e[0m` | edge-case |
| 13.99 | 600,000 | `\e[97m$13.99\e[0m\e[31m $83.9/h\e[0m` | happy-path |
| 19.99 | 3,600,000 | `\e[97m$19.99\e[0m\e[90m $20.0/h\e[0m` | edge-case (shows 20.0, grey) |
| 20.0 | 3,600,000 | `\e[97m$20.00\e[0m\e[33m $20.0/h\e[0m` | edge-case (rate p75 inclusive) |
| 23.99 | 3,600,000 | `\e[97m$23.99\e[0m\e[33m $24.0/h\e[0m` | happy-path |
| 24.0 | 3,600,000 | `\e[33m$24.00\e[0m\e[33m $24.0/h\e[0m` | edge-case ($ p75 inclusive) |
| 25.99 | 3,600,000 | `\e[33m$25.99\e[0m\e[33m $26.0/h\e[0m` | edge-case (shows 26.0, yellow) |
| 26.0 | 299,999 | `\e[33m$26.00\e[0m` | edge-case (no rate) |
| 29.99 | 3,600,000 | `\e[33m$29.99\e[0m\e[31m $30.0/h\e[0m` | happy-path |
| 30.0 | 3,600,000 | `\e[31m$30.00\e[0m\e[31m $30.0/h\e[0m` | edge-case ($ p95 inclusive) |
| 40.0 | 360,000 | `\e[31m$40.00\e[0m\e[31m $400.0/h\e[0m` | happy-path |
| `"30"` (string) | 3,600,000 | no cost segment | error |

All twelve numeric rows and EC-001/003/004/005 were re-executed against
`legacy/dgx_statusline.py` under CPython 3.11.7 on 2026-11-15 and match.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-021 | Go cost segment bytes equal the golden table for all rows | manual (golden table test, Tier A) |
| VP-021 | Same seed through the parity harness gives identical stdout and cost-history bytes on all three OSes | manual (parity harness case) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 (percentile bands) |
| L2 Domain Invariants | DI-007 |
| Architecture Module | `internal/cost` history.go + `internal/statusline` cost.go (BC-COMPONENT-MAP: internal/statusline/cost.go + internal/cost/history.go (goldens) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:601-625); cost_thresholds (SL:240-262); record_cost throttle (SL:232) |
| Legacy contract | BC-SL-101 (P3r3 §4.1; mismatches re-confirmed P3r4 §1.1) |
| Thresholds | T-018..T-021, T-023, T-024, T-043 (via BC-1.05.001/002/005) |
| Decisions | D4, OD-104 (oracle), OD-111 (explicit empty prefixes for unknown-lane cases) |

## Related BCs (Recommended)

- BC-1.05.001 / BC-1.05.002 / BC-1.05.005 — verifies
- BC-1.05.004 — verifies (throttle keeps the seed)
- BC-6.01.003 — depends on (clock shim)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/cost.go + internal/cost/history.go (goldens) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost colouring (filled by story-writer)

## VP Anchors (Recommended)

> Names provisional — architect (OD-145): harness flag names, the timing method, proposed
> test names and seed paths in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

- VP-021 — golden equality


#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane (SL:601-625); cost_thresholds (SL:240-262)) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: seeded 21-key goldens regenerated from CPython 3.11.7 (2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | only via injected `Env` seams |
| **Global state access** | none (seam-injected) |
| **Deterministic** | yes for widgets, given inputs and fake seams |
| **Thread safety** | single-threaded render loop |
| **Overall classification** | mixed (core-dominant) |

Owning components `internal/statusline` and `internal/cost` (BC-COMPONENT-MAP: sl/cost.go + cost/history.go (goldens) - ARCH-03); ARCH-00 classifies the former mixed (core-dominant) and the latter **pure core** (ARCH-00 package table; ARCH-03 §Interfaces: internal/cost does no I/O of any kind), so the render-side logic stays `Env`-seam pure and internal/cost stays a pure function over the loaded history — no store, no injected seam; `internal/statusline` loads and saves the cost-history file through its `CacheStore`.
