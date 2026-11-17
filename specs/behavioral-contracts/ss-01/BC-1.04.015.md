---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r7.md]
input-hash: "58646e3"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-074"
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

# Behavioral Contract BC-1.04.015: KV NaN crash path (CP-N01) and cell math

## Description

A NaN KV-usage value survives the clamp (`max(nan, 0.0)` keeps NaN) and makes `ceil` raise,
so legacy prints the degraded line, on both the fresh and the stale path. The Go port
reproduces that, and pins the full KV cell/percentage table for finite and infinite values.
Latent in production (capture 2026-11-14), kept per the owner ruling on catalogued crash
paths. Notation: `\e` is byte 0x1B.

## Preconditions

1. Row 2 is rendered with a dict sample (fresh or stale) and
   `vllm:kv_cache_usage_perc` is a number.

## Postconditions

1. NaN → `Max(NaN*100, 0.0)` = NaN (Python argument order), `Min(NaN, 100.0)` = NaN,
   `Ceil(NaN/25)` raises → `errDegraded` (CP-N01); stdout is the 29-byte degraded line,
   exit 0; writes before the row-2 render persist, later ones do not (BC-1.01.009).
2. Otherwise the cell count and percentage follow the table below exactly.

## Invariants

1. Cells = `min(ceil(kv/25), 4)` with `kv` clamped to [0, 100]; ±Inf never crash.
2. Percentage text = `F(kv, 0)` of the clamped value.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | kv NaN, fresh | degraded |
| EC-002 | kv NaN, stale (failed fetch, last-known NaN) | degraded |
| EC-003 | kv +Inf | `KV▰▰▰▰ 100%` |
| EC-004 | kv -Inf | `KV▱▱▱▱ 0%` |
| EC-005 | kv 0.29 (`28.999999999999996`) | 2 cells, `29%` |
| EC-006 | host share NaN with finite kv | cyan, no suffix (no crash) |

## Canonical Test Vectors

Cyan prefix `\e[36m`, suffix `\e[0m` unless noted.

| Input | Expected Output | Category |
|-------|----------------|----------|
| 0.0 / 0.0001 / 0.25 / 0.2500001 / 0.29 | `KV▱▱▱▱ 0%` / `KV▰▱▱▱ 0%` / `KV▰▱▱▱ 25%` / `KV▰▰▱▱ 25%` / `KV▰▰▱▱ 29%` | happy-path |
| 0.51 / 0.75 / 0.76 / 1.2 | `KV▰▰▰▱ 51%` / `KV▰▰▰▱ 75%` / `KV▰▰▰▰ 76%` / `KV▰▰▰▰ 100%` | edge-case |
| kv 0.5, host NaN | `\e[36mKV▰▰▱▱ 50%\e[0m` | edge-case |
| kv NaN | `\e[90mstatusline degraded\e[0m\n` (whole stdout), exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030, VP-001 | Go degrades iff kv is NaN; finite/±Inf rows equal legacy bytes | proptest + table |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:754-763; raise at SL:759); guard (SL:1238-1245) |
| Legacy contract | BC-SL-074 (P3 r1 new; r7 flag "latent in production") |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | owner ruling on catalogued crash paths (P3 r7 §5) |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.007 — refines: KV segment
- BC-1.01.001 — depends on: degraded line
- BC-5.01.003 — depends on: `Max`/`Min` argument order, `Ceil` ErrValue

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#degraded-ladder` — internal/statusline/row2.go (CP-N01, cell math) (errDegraded sites) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030, VP-001 — CP-N01 equivalence

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:757-759) |
| **Confidence** | high — re-executed on CPython 3.11.7 (`ValueError: cannot convert float NaN to integer`) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: no guard around `math.ceil` (SL:759)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Send + Sync |
| **Overall classification** | pure (returns an error) |

#### Refactoring Notes

`renderTelemetry` returns `([]string, error)`; never use builtin `max`/`min` (they would
make NaN propagate differently, PR-04).
