---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "76b3a2d"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:serving_state (SL:705-722)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-044"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["2026-11-18 (v1.2.1) pass-4 remediation ADV-P4-C2-12 (metrics-borne SL:717 degrade named CP-N03 on EC-007)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.005: Health dot

## Description

The first row-2 segment is the health dot. It shows backend serving state from the scrape
health series: red text `◉ vLLM down` or `◉ LMCache down` when serving is broken,
otherwise a bare dot colored by freshness (green fresh, yellow stale). Notation: `\e` is
byte 0x1B.

## Preconditions

1. `m` is a dict sample; `stale` is from BC-1.04.004.
2. Keys of interest: `up:vllm`, `up:lmcache` (BC-1.04.001 `up` rewrite), any key starting
   with `vllm:`, and `vllm:lmcache_mp_lookup_duration_seconds_count`.

## Postconditions

1. `down = "vLLM down"` if `m.get("up:vllm") == 0`, or if `up:vllm` is absent **and** no
   key starts with `vllm:`.
2. Else `down = "LMCache down"` if `vllm:lmcache_mp_lookup_duration_seconds_count` is
   present **and** `m.get("up:lmcache") == 0`.
3. Else `down = none`.
4. Segment = `"\e[31m◉ " + down + "\e[0m"` if `down`, else `"\e[33m◉\e[0m"` when stale,
   `"\e[32m◉\e[0m"` when fresh. A down state is red regardless of `stale`.

## Invariants

1. `LMCache down` is reported only when the LMCache connector is in use (its lookup
   counter is exported); under native offload a down `lmcache` job never shows.
2. Equality is numeric (`0.0 == 0` true; `NaN == 0` false).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `{}`-like sample with no vllm keys and no `up:vllm` (non-empty, e.g. only `DCGM_FI_DEV_POWER_USAGE`) | `vLLM down` |
| EC-002 | `up:vllm`=0 with vllm series present | `vLLM down` |
| EC-003 | `up:vllm` absent, `vllm:x` present | dot (no down) |
| EC-004 | `up:vllm`=1, `up:lmcache`=0, no lookup counter | dot |
| EC-005 | `up:vllm`=1, lookup counter present, `up:lmcache`=0 | `LMCache down` |
| EC-006 | `up:vllm`=NaN, no vllm keys | dot (`nan == 0` false; not None) |
| EC-007 | non-string key in sample (BC-1.04.001 EC-013) | degraded line only when the key precedes every `vllm:` key (`any()` stops at the first match, SL:717; metrics-borne degrade, crash id **CP-N03**); `{"vllm:x": 1, 5: 1}` renders normally; on later cached-path refreshes the key is the string `"5"` and nothing degrades |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `{"up:vllm": 1.0}`, fresh | `\e[32m◉\e[0m` | happy-path |
| `{"up:vllm": 1.0}`, stale | `\e[33m◉\e[0m` | happy-path |
| `{"up:vllm": 1.0, "vllm:lmcache_mp_lookup_duration_seconds_count": 3.0, "up:lmcache": 0.0}` | `\e[31m◉ LMCache down\e[0m` | edge-case |
| `{"up:vllm": 0.0, "vllm:x": 1.0}` | `\e[31m◉ vLLM down\e[0m` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Six-case table (review #13) reproduces legacy bytes in fresh and stale modes | manual (table) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:serving_state (SL:705-722); render_telemetry_fields (SL:726-730) |
| Legacy contract | BC-SL-044 (P3 base, review #13 six cases) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | OD-113 (colors from theme keys, legacy defaults) |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.004 — depends on: `stale`
- BC-1.04.001 — depends on: `up:<job>` keys

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/row2.go (health dot) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — health table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:705-730) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: SL:718, SL:720
- **documentation**: docstring SL:706-715

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config (theme) |
| **Deterministic** | yes |
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
