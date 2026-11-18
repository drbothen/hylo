---
document_type: behavioral-contract
level: L3
version: "1.3.2"
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
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r6.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r7.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "a614197"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:626-636)"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-027"
parity_class: "byte-exact"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.3 2026-11-17: pass-4 residual sweep — key renamed to statusline.cost.display_floor_usd (OD-174)"
  - "1.3.1 2026-11-18: pass-8 remediation ADV-P8-C2-01 (the pick named as the config key statusline.glyphs.cost_pick with default ⛏, OD-189 sibling treatment)"
  - "1.3.2 2026-11-18: pass-9 orchestrator call 4/B03 (CP-O12 co-owner EC-011 added — cost-pick equivalence overflow at SL:633; owner EC in BC-1.02.029) and DI-008 lifted into the L2 row"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.05.003: ⛏ pick inside the $ block (basis threshold)

## Description

On the local lane, the owned-hardware cost `⛏` (what this session's tokens cost at the
backend's blended $/MTok) is a suffix of the cost segment, never its own segment. It
appears only when the `$` block exists (`total_cost_usd > 0`). When the backend's
utilization basis is not representative it shows `⛏n/a`; otherwise it shows the dollar
equivalent, unless that is below half a cent.

## Preconditions

1. The cost segment exists: `cost.total_cost_usd` numeric and `> 0` (SL:601-602,
   amendment P3r6 R1-1). Without it no `⛏` and no `⛏n/a` is rendered, even on the
   local lane with a valid basis.
2. The client-view lane is the local lane (`on_dgx` truthy, BC-1.02.001) (SL:627).
3. `tot = (tin or 0) + (tout or 0) > 0`, where `tin`/`tout` are the session token totals
   from the transcript parse (mix fields 3 and 4, SL:574-576, 626).
4. `dgx_mtok` = metric `dgx_cost:dgx_usd_per_mtok` from the sample, reset to None when it
   is not a number or `<= 0` (SL:1220-1222); `dgx_rate` = metric
   `dgx_tokens:rate_mtok_month`, raw (SL:1223). Both are None when no sample was
   fetched (rows < 2, or no sample).
5. Config: `statusline.cost.basis_min_mtok_month` = 30.4 (T-012, derived: 1M backend
   tokens per 24 h ≈ 30.4 MTok/month, review #11.1); `statusline.cost.display_floor_usd`
   = 0.005 (T-044, derived: "skip sub-half-cent noise", SL:634; boundary detail in BC-1.02.029).
   Grey `\e[90m`, reset `\e[0m` (OD-113 theme keys).

## Postconditions

1. `basis_ok` = `dgx_rate` is a number and `dgx_rate >= basis_min_mtok_month`, **and**
   `dgx_mtok` is a number and `dgx_mtok > 0` (SL:628-629).
2. Not `basis_ok` → append exactly `\e[90m ` + glyphs.cost_pick + `n/a\e[0m` (SL:631),
   where `glyphs.cost_pick` = `statusline.glyphs.cost_pick` (Text, default `⛏` U+26CF,
   KD-002, BC-2.01.004 PC-6; the ⛏ literals in the vectors are the default spelling,
   ADV-P8-C2-01).
3. `basis_ok` → `eq = tot * dgx_mtok / 1e6` (left-to-right double arithmetic, SL:633);
   if `eq >= display_floor_usd` append `\e[90m ` + glyphs.cost_pick + F(eq, 2) + `\e[0m`
   (SL:634-635); else append nothing (not `n/a`).
4. The text is appended after `$` and any `$/h`, inside the same segment, with no
   separator (SL:636).

## Invariants

1. The cloud lane and lane None never show `⛏`.
2. `$`, `$/h` and `⛏` are built as one segment under one `usd > 0` guard (design §2.3,
   `cost.go`).
3. The metric names are protocol constants of the legacy recording rules, not config.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `total_cost_usd` absent / 0 / NaN / negative / string, valid basis | no `⛏`; the token segment is the last row-1 part |
| EC-002 | rows = 1 (no sample) | `dgx_mtok`/`dgx_rate` None → `⛏n/a` (when the cost segment exists) |
| EC-003 | `dgx_rate` = 30.3 | `⛏n/a` |
| EC-004 | `dgx_rate` NaN | `NaN >= 30.4` false → `⛏n/a` |
| EC-005 | `dgx_mtok` NaN | survives SL:1221 (`NaN <= 0` false) but fails `> 0` → `⛏n/a` |
| EC-006 | `dgx_mtok` +inf, tot > 0 | `⛏inf` |
| EC-007 | tot 999, mtok 5.0 → eq 0.004995 | nothing appended |
| EC-008 | tot 1000, mtok 5.0 → eq 0.005 | ` ⛏0.01` (inclusive; `.2f` of 0.005 → `0.01`) |
| EC-009 | `total_cost_usd` = `true` | `\e[97m$1.00\e[0m…\e[90m ⛏0.25\e[0m` with the basis below |
| EC-010 | tot = 0 | no `⛏` |
| EC-011 | cost-pick equivalence overflow (crash id **CP-O12**; Surface 1, render-time degrade, like CP-O04): `tin` and `tout` each below the int→float overflow bound but their exact-int sum `tot` (SL:626) at or above it enters `tot * dgx_mtok` (SL:633) on the local lane with a valid basis → OverflowError → degraded line | degraded line (BC-1.01.001); the pick is not rendered for this refresh |

## Canonical Test Vectors

Common inputs: model `claude-sonnet-5-5` (local lane under the default prefix), tin
3,400,000, tout 120,000, cold start (empty history).

| Input | Expected Output | Category |
|-------|----------------|----------|
| usd 2.5, api 600000, mtok 0.07, rate 31.0 | `\e[97m$2.50\e[0m\e[90m $15.0/h\e[0m\e[90m ⛏0.25\e[0m` | happy-path |
| usd 0.004, api 600000, mtok 0.07, rate 31.0 | `\e[90m$0.00\e[0m\e[90m $0.0/h\e[0m\e[90m ⛏0.25\e[0m` | edge-case |
| usd 2.5, no api, mtok 0.07, rate 30.3 | `\e[97m$2.50\e[0m\e[90m ⛏n/a\e[0m` | edge-case |
| usd 2.5, no api, mtok None, rate 31.0 | `\e[97m$2.50\e[0m\e[90m ⛏n/a\e[0m` | edge-case |
| usd 2.5, tin 999, tout 0, mtok 5.0, rate 31.0 | `\e[97m$2.50\e[0m` | edge-case |
| usd 2.5, model `claude-opus-5-5` (cloud lane) | `\e[97m$2.50\e[0m` | edge-case |
| usd absent, valid basis | no cost segment, no `⛏` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-021 | `⛏` text present ⇒ cost segment present and lane is local | Go property test (testing/quick) |
| VP-021 | Bytes equal legacy on the five P3r6 §1.1 rows and the P3r7 12-value fixture | manual (table test) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 (owned-hardware cost), CAP-010 |
| L2 Domain Invariants | DI-007, DI-008 (the EC-011 CP-O12 OverflowError degrade rides the never-blank ladder: 29-byte line, exit 0; pass-9 orchestrator call 4/B03) |
| Architecture Module | `internal/statusline` cost.go (BC-COMPONENT-MAP: internal/statusline/cost.go (⛏ in $ block) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:601-602, 626-636); main (SL:1220-1223); MIN_BASIS_MTOK_MONTH (SL:98) |
| Legacy contract | BC-SL-027 (amended P3r6 §2.1, re-verified P3r7) |
| Thresholds | T-012 (30.4 MTok/month, derived), T-044 (0.005, derived: sub-half-cent noise; aligned with the catalog) |
| Decisions | D4, D15, OD-113 |

## Related BCs (Recommended)

- BC-1.02.029 — related to (pick `eq` threshold 0.005 boundary, BC-SL-083)
- BC-1.05.001 — composes with (shares the `usd > 0` guard)
- BC-1.05.002 — composes with
- BC-1.04.013 — depends on (sample fetched only when rows ≥ 2)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/cost.go (⛏ in $ block) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost segment (filled by story-writer)

## VP Anchors (Recommended)

- VP-021 — `⛏` gating


#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane (SL:626-636); main (SL:1220-1223)) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `not isinstance(dgx_mtok, (int, float)) or dgx_mtok <= 0` keeps NaN (SL:1221)
- **inferred**: pit-badge gate and basis guards re-executed against CPython 3.11.7 (2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | only via injected `Env` seams |
| **Global state access** | none (seam-injected) |
| **Deterministic** | yes for widgets, given inputs and fake seams |
| **Thread safety** | single-threaded render loop |
| **Overall classification** | mixed (core-dominant) |

Owning component `internal/statusline` (BC-COMPONENT-MAP: sl/cost.go (⛏ in $ block) - ARCH-03); the ARCH-00 package table classifies the package mixed (core-dominant) - pure widgets plus the effect script (AD-03), I/O only via `Env` seams.
