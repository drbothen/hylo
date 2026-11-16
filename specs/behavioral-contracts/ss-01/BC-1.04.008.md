---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/statusline-target-design.md, ../semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-047"
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

# Behavioral Contract BC-1.04.008: Throughput segments

## Description

Row 2 carries two separate throughput segments: `»N t/s` for this session's last completed
API call (from the transcript, both lanes) and `▣N t/s` for the backend box rate over one
minute (all clients), followed by the sparkline when fresh. The segments measure different
things and are never combined. Notation: `\e` is byte 0x1B.

## Preconditions

1. `sess_rate` is the last-turn value from the transcript parser (`mix[7]`, BC-1.03.010),
   possibly none.
2. `rate = m.get("dgx_sl:gen_rate1m", m.get("dgx_tokens:gen_rate5m"))` (1-minute rate,
   5-minute fallback only when the 1-minute key is absent).
3. Sparkline enable = `statusline.sparkline.enabled` (legacy `DGX_SL_SPARK != "0"`,
   default on).

## Postconditions

1. **Mine segment**: rendered per BC-1.04.018 and appended first when non-empty:
   `"\e[90m»\e[0m" + mine + "\e[90mt/s\e[0m"`.
2. **Box segment**: if `rate is not None`:
   `box = "\e[90m▣\e[0m" + ("\e[90m" if stale else "\e[97m") + F(rate,0) + "\e[0m\e[90mt/s\e[0m"`;
   `sp = ""` if stale or sparkline disabled, else `sparkline(hist)` (BC-1.04.009);
   segment = `(box + " " + sp).rstrip()` (Python `rstrip()` of whitespace: an empty
   sparkline leaves no trailing space).
3. Order within row 2: dot, queue, KV, mine, box, TTFT, power, idle.

## Invariants

1. The sparkline is never drawn on a stale row.
2. A present `gen_rate1m` key wins even when its value is NaN (`dict.get` default is not
   consulted).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Only `gen_rate5m` 12.5 present | `▣12t/s` (half-even of 12.5 → 12) |
| EC-002 | Stale with 2+ history points | grey value, no sparkline, no trailing space |
| EC-003 | Fresh, < 2 plottable points | no sparkline, no trailing space |
| EC-004 | Neither rate key present | no box segment |
| EC-005 | Sparkline disabled | box only; main also passes `[]` as hist (SL:1227) |
| EC-006 | `gen_rate1m` NaN | `▣nant/s`; sparkline then hits CP-N02 if NaN is among plotted points (BC-1.04.014) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| fresh, `gen_rate1m` 204.0, hist `[]` | `\e[90m▣\e[0m\e[97m204\e[0m\e[90mt/s\e[0m` | happy-path |
| fresh, `gen_rate1m` 80.0, hist `[{"t":990.0,"v":60.0},{"t":998.5,"v":70.0}]` | `\e[90m▣\e[0m\e[97m80\e[0m\e[90mt/s\e[0m \e[38;2;38;93;104m▇\e[38;2;140;235;255m█\e[0m` | happy-path |
| stale, `gen_rate1m` 204.0, 2 points | `\e[90m▣\e[0m\e[90m204\e[0m\e[90mt/s\e[0m` | edge-case |
| no rate keys, `sess_rate` none | neither segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Box segment never ends in a space | proptest |
| VP-030 | Six-case review #16 table reproduces legacy bytes | manual (table) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:772-785); SPARK_ON (SL:76) |
| Legacy contract | BC-SL-047 (P3 base, review #16, 6 cases) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007 |
| Decisions | OD-113 (theme colors), OD-02 (glyphs) |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.018 — composes with: the mine segment's value rules
- BC-1.04.009 — composes with: the sparkline
- BC-1.03.010 — depends on: last-turn rate

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#row-2` — internal/statusline/row2.go (throughput) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — throughput segment shape

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:772-785) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if mine`, `if rate is not None`, `"" if stale or not SPARK_ON` (SL:780-784)
- **documentation**: comment SL:765-771

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Send + Sync |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. `rstrip()` must use Python whitespace semantics (BC-5.03.002);
here the only possible trailing whitespace is the single space.
