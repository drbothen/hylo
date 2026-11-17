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
  - semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r6.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r7.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "e56ce12"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-027"
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
   tokens per 24 h ≈ 30.4 MTok/month, review #11.1); `statusline.cost.basis_min_shown_usd`
   = 0.005 (T-044, "skip sub-half-cent noise", SL:634; boundary detail in BC-1.02.029).
   Grey `\e[90m`, reset `\e[0m` (OD-113 theme keys).

## Postconditions

1. `basis_ok` = `dgx_rate` is a number and `dgx_rate >= basis_min_mtok_month`, **and**
   `dgx_mtok` is a number and `dgx_mtok > 0` (SL:628-629).
2. Not `basis_ok` → append exactly `\e[90m ⛏n/a\e[0m` (SL:631).
3. `basis_ok` → `eq = tot * dgx_mtok / 1e6` (left-to-right double arithmetic, SL:633);
   if `eq >= basis_min_shown_usd` append `\e[90m ⛏` + F(eq, 2) + `\e[0m` (SL:634-635);
   else append nothing (not `n/a`).
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
| VP-021 | `⛏` text present ⇒ cost segment present and lane is local | proptest |
| VP-021 | Bytes equal legacy on the five P3r6 §1.1 rows and the P3r7 12-value fixture | manual (table test) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 (owned-hardware cost), CAP-010 |
| L2 Domain Invariants | DI-007 |
| Architecture Module | `internal/statusline` cost.go (BC-COMPONENT-MAP: internal/statusline/cost.go (⛏ in $ block) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:601-602, 626-636); main (SL:1220-1223); MIN_BASIS_MTOK_MONTH (SL:98) |
| Legacy contract | BC-SL-027 (amended P3r6 §2.1, re-verified P3r7) |
| Thresholds | T-012 (30.4 MTok/month, derived), T-044 (0.005, judgment: sub-half-cent noise) |
| Decisions | D4, D15, OD-113 |

## Related BCs (Recommended)

- BC-1.02.029 — related to (pick `eq` threshold 0.005 boundary, BC-SL-083)
- BC-1.05.001 — composes with (shares the `usd > 0` guard)
- BC-1.05.002 — composes with
- BC-1.04.013 — depends on (sample fetched only when rows ≥ 2)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#cost-segment` — internal/statusline/cost.go (⛏ in $ block) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost segment (filled by story-writer)

## VP Anchors (Recommended)

- VP-021 — `⛏` gating

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | only via injected `Env` seams |
| **Global state access** | none (seam-injected) |
| **Deterministic** | yes for widgets, given inputs and fake seams |
| **Thread safety** | single-threaded render loop |
| **Overall classification** | mixed (core-dominant) |

Owning component `internal/statusline` (BC-COMPONENT-MAP: sl/cost.go (⛏ in $ block) - ARCH-03); the ARCH-00 package table classifies the package mixed (core-dominant) - pure widgets plus the effect script (AD-03), I/O only via `Env` seams.
