---
document_type: behavioral-contract
level: L3
version: "1.3"
status: draft
producer: product-owner
timestamp: 2026-11-17T15:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "e5f0d55"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:617-625)"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-026"
parity_class: "byte-exact"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified: ["1.3 2026-11-17: pass-2 remediation ADV-P2-C2-11a (zero recorded rates)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.05.002: $/h segment with threshold colouring

## Description

Inside the cost segment, after `$`, the burn rate `$/h` (dollars per hour of model
time = `total_cost_usd / total_api_duration_ms`) is appended once the session has at
least 5 minutes of API time. It is coloured red at or above the lane's rate p95,
yellow at or above the rate p75, otherwise grey; at cold start it is always grey.

## Preconditions

1. The cost segment exists (stdin `cost.total_cost_usd` numeric and `> 0`, SL:602).
2. `api_ms = cost.total_api_duration_ms` is read once (SL:603).
3. `th_rate` is the second element returned by `cost_thresholds` (BC-1.05.005), or
   None (cold start, or lane None).
4. Config: `statusline.cost.burn_min_api_ms` = 300000 (T-043, "below that the ratio is
   noise", SL:619); the ms-per-hour factor 3.6e6 is a unit constant (named constant,
   not config). Palette per `statusline.theme.*` (OD-113): grey `\e[90m`, yellow
   `\e[33m`, red `\e[31m`, reset `\e[0m`.

## Postconditions

1. If `api_ms` is a number (bool included) and `api_ms >= burn_min_api_ms`, then
   `r = usd / (api_ms / 3.6e6)` in IEEE-754 double arithmetic, evaluated in this order
   (SL:622-623).
2. Colour `rc` (SL:624): if `th_rate` is a pair `(p75, p95)` → red if `r >= p95`,
   else yellow if `r >= p75`, else grey; if `th_rate` is None → grey.
3. Appended bytes: `rc + " $" + F(r, 1) + "/h" + "\e[0m"` (SL:625) — the leading space
   is inside the colour; `F` is Python `.1f` (BC-1.05.007).
4. Otherwise (`api_ms` absent, null, non-number, NaN, or `< burn_min_api_ms`) nothing is
   appended.

## Invariants

1. `$/h` is not gated on `usd >= min_usd`: a grey `$` (< $1) can carry a percentile-
   coloured `$/h` (SL:624 does not test usd).
2. The colour uses the unrounded `r`, so a value displayed as `20.0` can be grey when
   `r = 19.99 < p75 = 20` (BC-1.05.008).
3. One `api_ms` read serves both this display and `record_cost` (SL:603, 606).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `api_ms` = 299999 | no `$/h` |
| EC-002 | `api_ms` = 300000 exactly | shown (inclusive); usd 1.0 → ` $12.0/h` |
| EC-003 | `api_ms` = `true` | 1 < 300000 → no `$/h` |
| EC-004 | `api_ms` = NaN | `NaN >= 300000` false → no `$/h` |
| EC-005 | `api_ms` = +inf | `r = 0.0` → `\e[90m $0.0/h\e[0m` at cold start; with a pair, grey (a recorded rate can be 0.0 — a stored `api_ms` of Infinity passes the gate and yields rate 0.0, SL:235, 255 — and 0.0 < any positive p75) |
| EC-006 | usd = +inf, api 600000 | `$inf/h`; cold start → `\e[90m $inf/h\e[0m` |
| EC-007 | usd 0.5 (grey `$`), api 600000, `th_rate` (20.0, 26.0) | `\e[90m $3.0/h\e[0m` (3.0 < 20) — rate still shown |
| EC-008 | `th_usd` present, `th_rate` None (12 dollar entries, no rate entries) | `$` coloured, `$/h` grey |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| usd 32.62, api 6711428.57, cold start, lane anth | segment `\e[33m$32.62\e[0m\e[90m $17.5/h\e[0m` (r = 17.497318011387254) | happy-path |
| usd 13.99, api 600000, th (24.0, 30.0)/(20.0, 26.0) | `\e[97m$13.99\e[0m\e[31m $83.9/h\e[0m` | happy-path |
| usd 20.0, api 3600000, th_rate (20.0, 26.0) | `\e[97m$20.00\e[0m\e[33m $20.0/h\e[0m` (p75 inclusive) | edge-case |
| usd 26.0, api 299999 | `\e[33m$26.00\e[0m` (no rate) | edge-case |
| api_ms `"600000"` (string) | no `$/h` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-021 | `$/h` present iff `api_ms` numeric and ≥ burn_min_api_ms | Go property test (testing/quick) |
| VP-021 | `r` bit-identical to Python for the BC-1.05.008 goldens | manual (golden table test) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011, CAP-009 |
| L2 Domain Invariants | DI-007 |
| Architecture Module | `internal/statusline` cost.go (BC-COMPONENT-MAP: internal/statusline/cost.go ($/h thresholds) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:601-603, 617-625) |
| Legacy contract | BC-SL-026 (P3r1 row 55; refined P3 deep r1 with BC-SL-082) |
| Thresholds | T-043 (300,000 ms, derived: "below that the ratio is noise", SL:619) |
| Decisions | D4, D15, OD-113 |

## Related BCs (Recommended)

- BC-1.05.001 — composes with (`$` precedes `$/h` in one segment)
- BC-1.05.005 — depends on (`th_rate`)
- BC-1.05.007 — depends on (`.1f` format)
- BC-1.05.008 — verified by (goldens)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/cost.go ($/h thresholds) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost segment (filled by story-writer)

## VP Anchors (Recommended)

- VP-021 — `$/h` presence and colour rule


#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane (SL:617-625)) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `burn_min_api_ms` gate on the $/h leg (SL:618-625)
- **inferred**: burn-rate division and rounding re-executed against CPython 3.11.7 (2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | only via injected `Env` seams |
| **Global state access** | none (seam-injected) |
| **Deterministic** | yes for widgets, given inputs and fake seams |
| **Thread safety** | single-threaded render loop |
| **Overall classification** | mixed (core-dominant) |

Owning component `internal/statusline` (BC-COMPONENT-MAP: sl/cost.go ($/h thresholds) - ARCH-03); the ARCH-00 package table classifies the package mixed (core-dominant) - pure widgets plus the effect script (AD-03), I/O only via `Env` seams.
