---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "334d138"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-046"
parity_class: byte-exact
confidence: H
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

# Behavioral Contract BC-1.04.007: KV segment

## Description

When the GPU KV-cache usage series is numeric, row 2 shows a 4-cell gauge by ceiling
quarters and the rounded percentage, colored yellow when the host-tier share of reused
history exceeds 5 %, else cyan; a dimmed `↺host N%` suffix follows when that share exceeds
0.5 %. The segment is hidden when the series is missing. Notation: `\e` is byte 0x1B.

## Preconditions

1. `kv_raw = m.get("vllm:kv_cache_usage_perc")`, `hs_raw = m.get("dgx_kv:host_hit_share")`.
2. Config: `statusline.kv.cells` 4 (T-048, derived: ceiling quarters keep 85-96 % steady,
   review #15), `statusline.kv.host_yellow_pct` 5 (T-049, measured: THRESHOLDS §8b),
   `statusline.kv.host_shown_pct` 0.5 (T-050, derived: at or below 0.5 the `.0f` value
   would print `0%`; OD-57 E-0).

## Postconditions

1. `host_share = hs_raw * 100` if `hs_raw` is a number (bool, int or float), else none.
2. Segment exists only if `kv_raw` is a number (`isinstance(int, float)`, bool included).
3. `kv = Min(Max(kv_raw * 100, 0.0), 100.0)` with Python argument-order NaN semantics
   (BC-5.01.003); `n = Min(Ceil(kv / 25), 4)`.
4. `warn = host_share is not none and host_share > 5`.
5. Segment = `("\e[33m" if warn else "\e[36m") + "KV" + "▰"*n + "▱"*(4-n) + " " + F(kv,0) + "%\e[0m"`,
   then, if `host_share is not none and host_share > 0.5`, append
   `" \e[2m↺host " + F(host_share,0) + "%\e[0m"`.
6. Stale mode does not change this segment.

## Invariants

1. No invented `KV 0%` when the series is missing (review #15).
2. A `NaN` KV value is the CP-N01 crash path, specified in BC-1.04.015.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | kv 0.0 | `KV▱▱▱▱ 0%` |
| EC-002 | kv 0.0001 | 1 cell, `0%` |
| EC-003 | kv 0.25 / 0.2500001 | 1 cell `25%` / 2 cells `25%` |
| EC-004 | kv 0.76 / 1.2 | 4 cells `76%` / 4 cells `100%` (clamped) |
| EC-005 | host 0.005 (0.5 %) | no suffix, cyan |
| EC-006 | host 0.05 (5 %) | cyan, ` ↺host 5%` |
| EC-007 | host 0.0500001 | yellow, ` ↺host 5%` |
| EC-008 | host NaN | no suffix, cyan |
| EC-009 | kv absent or a string | no segment |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| kv 0.92, host absent | `\e[36mKV▰▰▰▰ 92%\e[0m` | happy-path |
| kv 0.92, host 0.00501 | `\e[36mKV▰▰▰▰ 92%\e[0m \e[2m↺host 1%\e[0m` | edge-case |
| kv 0.92, host 0.0500001 | `\e[33mKV▰▰▰▰ 92%\e[0m \e[2m↺host 5%\e[0m` | edge-case |
| kv NaN | degraded line (CP-N01, BC-1.04.015) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Cell count = `min(ceil(clamp(kv*100)/25), 4)` for finite and ±inf inputs | proptest |
| VP-030 | 11-case review #15 table reproduces legacy bytes | manual (table) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:754-763) |
| Legacy contract | BC-SL-046 (P3 base, review #15, 11 cases) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | OD-57 E-0 (T-050), OD-113 |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.015 — refined by: NaN crash path and the full cell table
- BC-5.01.003 — depends on: `Max`/`Min`/`Ceil` semantics

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#row-2` — internal/statusline/row2.go (KV) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — KV cell math

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:754-763) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **type constraint**: `isinstance(kv_raw, (int, float))` (SL:757)
- **documentation**: comment SL:743-753

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Send + Sync |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. Never use Go builtin `max`/`min` or `math.Max` here (NaN
propagation differs, PR-04).
