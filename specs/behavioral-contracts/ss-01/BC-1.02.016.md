---
document_type: behavioral-contract
level: L3
version: "1.3"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "748d355"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-021"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "pass-4 remediation (ADV-P4-B03): for-all suffix-presence leg re-anchored to VP-041; 2026-11-17T12:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.016: API-time suffix

> Byte notation used below: `\e` = ESC (0x1B). All other characters are literal UTF-8.

## Description

Inside a shown timer segment, the cumulative model-wait time (`cost.total_api_duration_ms`) is appended as a dimmed
`·<duration>` suffix when it is at least 60,000 ms. The suffix is not capped at the elapsed wall time, because
concurrent (subagent) API calls can sum past it. The duration is formatted by `_hm` (BC-1.02.015).

## Preconditions

1. The timer segment is shown: `cost.total_duration_ms` is a JSON number and `> statusline.timer.min_ms`
   (default 60000; BC-1.02.015). Without a shown timer there is no suffix.
2. `api` = stdin `cost.total_api_duration_ms` (any JSON value, or absent).
3. Default theme (`statusline.theme.*`, OD-113): DIM = `\e[2m`, RESET = `\e[0m`.

## Postconditions

1. If `api` is a number (int or float; a JSON `true`/`false` counts as int 1/0, as Python `isinstance(x, (int, float))`)
   and `api >= statusline.timer.api_min_ms` (default 60000, operator `>=`), the bytes
   `\e[2m·` + `_hm(api)` + `\e[0m` are appended to the timer segment immediately after the timer's own `\e[0m`
   and before any window-age suffix (BC-1.02.017).
2. Otherwise nothing is appended (absent, `null`, string, NaN, `-Infinity`, values below 60000).
3. The value is never clamped to `total_duration_ms`: `api > dur` renders as is.

## Invariants

1. The suffix is only ever produced inside the timer segment (no standalone API segment).
2. The threshold comparison is `>=` exactly; `api == 60000` with a shown timer prints `·1m` (CONV-ABS-64,
   observable; keep under D4).
3. The 60000 default and its operator come from the `internal/config` key `statusline.timer.api_min_ms`
   (register T-039, derived: `_hm` has minute granularity, below one minute it would print `0m`).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `api == 60000`, `dur = 120000` | suffix `\e[2m·1m\e[0m` (the `>=` boundary is observable) |
| EC-002 | `api = 59999` | no suffix |
| EC-003 | `api > dur` (subagents) | rendered uncapped |
| EC-004 | `api` = NaN | no suffix (NaN fails `>=`) |
| EC-005 | `api` = `true` | no suffix (`1 >= 60000` false) |
| EC-006 | `api` = `"90000"` (string) | no suffix (not numeric) |
| EC-007 | `api` = `-Infinity` | no suffix |
| EC-008 | `api` = `+Infinity` with a shown timer (CP-S13) | `_hm` raises ValueError; the whole refresh renders the 29-byte degraded line (BC-1.02.027, BC-1.01.001) |
| EC-009 | `dur <= 60000` (timer hidden), `api = 120000` | no timer segment, no suffix |

## Canonical Test Vectors

Each vector: stdin `{"cost": {...}}` with no model, workspace or other widgets; shown is the exact timer segment
(the last row-1 segment).

| Input | Expected Output | Category |
|-------|----------------|----------|
| `total_duration_ms: 120000, total_api_duration_ms: 60000` | `\e[90m⏱ 2m\e[0m\e[2m·1m\e[0m` | happy-path |
| `total_duration_ms: 120000, total_api_duration_ms: 4500000` | `\e[90m⏱ 2m\e[0m\e[2m·1h15m\e[0m` | happy-path (uncapped) |
| `total_duration_ms: 3600000, total_api_duration_ms: 7500000` | `\e[90m⏱ 1h00m\e[0m\e[2m·2h05m\e[0m` | happy-path |
| `total_duration_ms: 120000, total_api_duration_ms: 59999` | `\e[90m⏱ 2m\e[0m` | edge-case |
| `total_duration_ms: 120000` (api absent) | `\e[90m⏱ 2m\e[0m` | edge-case |
| `total_duration_ms: 120000, total_api_duration_ms: NaN` | `\e[90m⏱ 2m\e[0m` | edge-case |
| `total_duration_ms: 120000, total_api_duration_ms: true` | `\e[90m⏱ 2m\e[0m` | edge-case |
| `total_duration_ms: 120000, total_api_duration_ms: "90000"` | `\e[90m⏱ 2m\e[0m` | edge-case |
| `total_duration_ms: 120000, total_api_duration_ms: Infinity` | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error |

All expected values pinned 2026-11-15 by running the legacy `render_lane` under CPython 3.11 (oracle, OD-104).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-041 | For every finite numeric `api` and shown timer, the suffix is present iff `api >= 60000` | Go property test (testing/quick; table + generated values vs oracle; VP-028 retains the bounded golden tables) |
| VP-028 | The suffix bytes equal `\e[2m·` + `_hm(api)` + `\e[0m` | table test vs oracle |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (degraded ladder for `+Infinity`) |
| Architecture Module | `internal/statusline` (design §8 home `sl/session.go`; BC-COMPONENT-MAP: internal/statusline/session.go (API-time suffix) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:550-553, inside the timer block SL:539-563) |
| Legacy contract | BC-SL-021 (pass-3 r1 table; refined in deep pass-3 round 1: `api >= 60000`, `+inf` → CP-S13) |
| Config keys | `statusline.timer.api_min_ms` (T-039), `statusline.theme.*` (OD-113) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.015 — depends on (timer segment and `_hm`)
- BC-1.02.017 — composes with (window-age suffix follows this suffix)
- BC-1.02.027 — related to (`_hm` ValueError on `+Infinity`, CP-S13)
- BC-1.01.001 — related to (degraded line)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/session.go (API-time suffix) (status line row-1 session widgets) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-041 — presence iff `api >= 60000` (for-all); VP-028 — golden suffix bytes

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane, SL:550-553) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(api, (int, float)) and api >= 60000` (SL:551)
- **documentation**: SL:552 comment "not capped at elapsed"
- **inferred**: values pinned against the CPython 3.11 oracle

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config only |
| **Deterministic** | yes |
| **Thread safety** | unknown (single-threaded render) |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; suitable for table tests. `_hm` is shared with BC-1.02.015 and must keep the
`pyfmt.FloorDiv` + `pyfmt.Int` typed-error path (design IM-07/IM-08).
