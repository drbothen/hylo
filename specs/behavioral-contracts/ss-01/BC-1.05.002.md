---
document_type: behavioral-contract
level: L3
version: "1.3.6"
status: draft
producer: product-owner
timestamp: 2026-11-18T12:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "49edce2"
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
modified:
  - "2026-11-17 (v1.3) pass-2 remediation ADV-P2-C2-11a (zero recorded rates)"
  - "2026-11-18 (v1.3.1) pass-3 remediation ADV-P3-C2-01 (CP-O11 overflow at SL:623; OD-166 record guard) + ADV-P3-C2-11 (EC-005 pinned pair)"
  - "2026-11-18 (v1.3.2) pass-4 remediation ADV-P4-C2-06 (PC5: negative huge api_ms renders normally and is likewise not recorded; guard is sign-agnostic)"
  - "2026-11-18 (v1.3.3) pass-5 design call 16 (ADV-P5-C2-08 BC-side: burn_min_api_ms range restricted to Int > 0 with the ZeroDivisionError rationale)"
  - "2026-11-18 (v1.3.4) pass-6 remediation ADV-P6-C2-01 (canonical vector +inf/(0.0,0.0) corrected to RED — SL:624 tests r >= p95 first) + ADV-P6-C2-10 (DI-008 lifted) + ADV-P6-C2-15 (EC-009 row reordered after EC-008, ascending)"
  - "2026-11-18 (v1.3.5) pass-9 remediation ADV-P9-C2-03 cross-reference: the OD-166 record-guard citation now points at BC-1.05.004 PC4 (skip moved to the write step)"
  - "2026-11-18 (v1.3.6) pass-10 remediation ADV-P10-C2-11 (VP-001 row added to Verification Properties for the EC-009 CP-O11 overflow degrade leg; VP Anchors entry)"
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
   noise", SL:619; OD-162 range: Int > 0 — a gate value of 0 or less is a number-range
   config error because a recorded `api_ms` of 0 (or `false`, which counts as a number)
   would then pass the gate and Python raises ZeroDivisionError at the divide, ADV-P5-C2-08,
   pass-5 call 16); the ms-per-hour factor 3.6e6 is a unit constant (named constant,
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
5. Catalogued stdin-borne overflow (OD-156, CP-O11, carried by BC-1.05.007): an exact
   stdin int `api_ms` that passes the gate with magnitude >= 2**1024 - 2**970 raises
   OverflowError at `usd / (api_ms / 3.6e6)` (SL:623) → degraded line. Per ruling
   **OD-166** that `api_ms` (and the paired `usd`) is then **not recorded** in the cost
   history (BC-1.05.004 guard); the current refresh still degrades. A **negative** huge
   `api_ms` fails the gate (`< burn_min_api_ms`), renders normally with no $/h segment
   (PC4), and is likewise **not recorded** — the OD-166 record guard is
   convertibility-only and sign-agnostic (BC-1.05.004 PC4, ADV-P4-C2-06).

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
| EC-005 | `api_ms` = +inf | `r = 0.0` → `\e[90m $0.0/h\e[0m` at cold start; with a pair the colour is grey **iff the lane's p75 > 0.0** (pin a positive-p75 pair, e.g. (20.0, 26.0), for the grey expectation); if at least 75% of the lane's qualifying rates are 0.0 then p75 = 0.0 and `0.0 >= p75` holds → yellow (or red when also >= p95). Recorded 0.0 rates exist: a stored `api_ms` of Infinity passes the gate and yields rate 0.0, SL:235, 255 (ADV-P3-C2-11) |
| EC-006 | usd = +inf, api 600000 | `$inf/h`; cold start → `\e[90m $inf/h\e[0m` |
| EC-007 | usd 0.5 (grey `$`), api 600000, `th_rate` (20.0, 26.0) | `\e[90m $3.0/h\e[0m` (3.0 < 20) — rate still shown |
| EC-008 | `th_usd` present, `th_rate` None (12 dollar entries, no rate entries) | `$` coloured, `$/h` grey |
| EC-009 | `api_ms` = 2**1024 (309-digit exact int, passes gate) | OverflowError at SL:623 → degraded line (CP-O11, OD-156); the unconvertible `api_ms`/`usd` pair is not recorded (OD-166, BC-1.05.004) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| usd 32.62, api 6711428.57, cold start, lane anth | segment `\e[33m$32.62\e[0m\e[90m $17.5/h\e[0m` (r = 17.497318011387254) | happy-path |
| usd 13.99, api 600000, th (24.0, 30.0)/(20.0, 26.0) | `\e[97m$13.99\e[0m\e[31m $83.9/h\e[0m` | happy-path |
| usd 20.0, api 3600000, th_rate (20.0, 26.0) | `\e[97m$20.00\e[0m\e[33m $20.0/h\e[0m` (p75 inclusive) | edge-case |
| usd 26.0, api 299999 | `\e[33m$26.00\e[0m` (no rate) | edge-case |
| api_ms `"600000"` (string) | no `$/h` | error |
| api_ms +inf, th_rate (0.0, 0.0) | `\e[31m $0.0/h\e[0m` red (SL:624 tests `r >= th_rate[1]` FIRST: 0.0 >= p95 = 0.0 is true → RED, before the p75 branch is reached; oracle-verified CPython 3.11.7, 2026-11-18; ADV-P6-C2-01) | edge-case |
| api_ms = 2**1024 - 2**970 (exact int, boundary) | degraded line (CP-O11 at SL:623) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-021 | `$/h` present iff `api_ms` numeric and ≥ burn_min_api_ms | Go property test (testing/quick) |
| VP-021 | `r` bit-identical to Python for the BC-1.05.008 goldens | manual (golden table test) |
| VP-001 | The promised output set holds on the stdin-borne CP-O11 overflow degrade leg (EC-009): render output or the 29-byte degraded line — never blank, exit 0 (DI-008) | fault-injection ladder (assertPromisedOutputSet, DI-008) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011, CAP-009 |
| L2 Domain Invariants | DI-007, DI-008 (the CP-O11 degrade rides the never-blank ladder: 29-byte line, exit 0; ADV-P6-C2-10) |
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
- VP-001 — never-blank/exit-0 ladder; the EC-009 CP-O11 overflow leg rides it (ADV-P10-C2-11)


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
