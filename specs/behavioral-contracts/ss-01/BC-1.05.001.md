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
  - ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - ../semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-025"
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

# Behavioral Contract BC-1.05.001: $ colours from lane percentile thresholds

## Description

The `$` part of the row-1 cost segment shows Claude Code's exact session cost
(`cost.total_cost_usd`) with two decimals, coloured against the user's own same-lane
history: grey below the minimum-session floor, then red at or above the lane p95,
yellow at or above the lane p75, otherwise white. With no percentile pair (cold start,
or no client-view lane) a fixed yellow cut-off applies instead. The number format
itself is BC-1.05.007; the percentile computation is BC-1.05.005.

## Preconditions

1. stdin `cost.total_cost_usd` is a number in the Python `isinstance(x, (int, float))`
   sense (bool included, NaN included) **and** `> 0`. Otherwise the entire cost segment
   (`$`, `$/h`, `⛏`) is absent (SL:601-602).
2. The client-view lane (BC-1.02.001) is `dgx` (local lane), `anth` (cloud lane) or
   None. `backends[0].model_prefixes` (default `claude-sonnet`, OD-111/OD-123) drives it.
3. `record_cost` (BC-1.05.004) has already run for this refresh, then
   `th_usd, th_rate = cost_thresholds(lane, sid)` (BC-1.05.005) when the lane is known,
   else `(None, None)` (SL:606-607).
4. Config: `statusline.cost.min_usd` = 1.0 (T-019), `statusline.cost.cold_yellow_usd`
   = 25.0 (T-021); palette from `statusline.theme.*` (OD-113) with legacy defaults
   grey `\e[90m`, white `\e[97m`, yellow `\e[33m`, red `\e[31m`, reset `\e[0m`
   (SL:127, 131-132). `\e` = byte 0x1B.

## Postconditions

1. Colour `col` is chosen in exactly this order (SL:610-615):
   - `usd < min_usd` → grey (even when a percentile pair exists);
   - else if `th_usd` is a pair `(p75, p95)` → red if `usd >= p95`, else yellow if
     `usd >= p75`, else white;
   - else (cold start or lane None) → yellow if `usd >= cold_yellow_usd`, else white.
2. The `$` part is exactly `col + "$" + F(usd, 2) + "\e[0m"` (SL:616), where `F` is the
   Python `.2f` format (BC-1.05.007).
3. The `$` part is the first bytes of the cost segment; `$/h` (BC-1.05.002) and `⛏`
   (BC-1.05.003) are appended to the same segment with no separator. The whole segment
   is the last row-1 part (SL:636) and is joined to the previous part by the row
   separator.
4. Both comparisons are `>=` (inclusive); the grey test is strict `<`.

## Invariants

1. The `$` colour never depends on `$/h`, and `$/h` colour never depends on `usd`
   being above the floor (BC-1.05.002).
2. Defaults equal legacy (D15); thresholds are config keys, never literals in logic.
3. The colour tests use the raw `usd` value, not the rounded display value, so the
   displayed number and its colour can disagree at a boundary (BC-1.05.008).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `total_cost_usd` absent, `null`, `0`, `0.0`, negative, NaN, a string, `false` | no cost segment at all (no `$`, `$/h`, `⛏`) |
| EC-002 | `total_cost_usd` = `true` (bool is an int) | treated as 1: `1 < 1.0` false → percentile/cold colours; cold start → `\e[97m$1.00\e[0m` |
| EC-003 | `0.004` | grey `\e[90m$0.00\e[0m` (display rounds to zero; segment still present) |
| EC-004 | `+inf`, cold start | `\e[33m$inf\e[0m` (inf ≥ 25) |
| EC-005 | `+inf` with a pair | red (inf ≥ p95) |
| EC-006 | lane None (no prefixes, or empty `model.id`) | no record, no thresholds; cold-start colours (`26.0` → `\e[33m$26.00\e[0m`) |
| EC-007 | usd exactly p75 / p95 | yellow / red (inclusive) |
| EC-008 | usd < 1 while a pair exists | grey regardless of the pair |

## Canonical Test Vectors

Thresholds pinned from the BC-1.05.008 seed: `th_usd = (24.0, 30.0)`.

| Input | Expected Output | Category |
|-------|----------------|----------|
| usd 24.0, api 100000, th_usd (24.0, 30.0) | `\e[33m$24.00\e[0m` | happy-path |
| usd 30.0, api 100000, th_usd (24.0, 30.0) | `\e[31m$30.00\e[0m` | edge-case (p95 inclusive) |
| usd 1.0, api 100000, th_usd (24.0, 30.0) | `\e[97m$1.00\e[0m` | edge-case (floor not grey) |
| usd 0.5, api 100000, th_usd (24.0, 30.0) | `\e[90m$0.50\e[0m` | edge-case |
| usd 25.0, cold start | `\e[33m$25.00\e[0m` | edge-case (cold cut-off inclusive) |
| usd 24.99, cold start | `\e[97m$24.99\e[0m` | edge-case |
| usd NaN | no cost segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-021 | For every finite usd > 0 and pair p75 ≤ p95, the colour equals the three-way rule above | proptest (Go testing/quick vs the oracle table) |
| VP-021 | The `$` part bytes equal legacy on the BC-1.05.008 goldens | manual (golden table test) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 (cost accounting), CAP-009 |
| L2 Domain Invariants | DI-007 (status line inputs are stdin, transcript, metrics, its own caches) |
| Architecture Module | `internal/statusline` cost.go (design §2.3; BC-COMPONENT-MAP: internal/statusline/cost.go ($ percentile colors) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:601-616); constants COST_MIN_USD, COST_FALLBACK_YELLOW (SL:219, 221) |
| Legacy contract | BC-SL-025 (P3r1 §D row 54; refined P3 deep r1) |
| Thresholds | T-019 ($1, derived: owner design review #11), T-021 ($25, owner decision) |
| Decisions | D4 (parity), D15, OD-111, OD-113, OD-123 |

## Related BCs (Recommended)

- BC-1.05.002 — composes with (same segment, `$/h`)
- BC-1.05.003 — composes with (same segment, `⛏`)
- BC-1.05.004 — depends on (record before thresholds)
- BC-1.05.005 — depends on (percentile pair)
- BC-1.05.007 — depends on (number format)
- BC-1.05.008 — verified by (goldens)
- BC-1.02.001 — depends on (client-view lane)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#cost-segment` — internal/statusline/cost.go ($ percentile colors) (`$`/`$/h`/`⛏` built as one segment under one `usd > 0` guard) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost segment (filled by story-writer)

## VP Anchors (Recommended)

- VP-021 — `$` colour rule
