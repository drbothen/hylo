---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "2c519fb"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-090"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.01.010: Trim breakpoint matrix across widths

> Byte notation: `\e` = ESC (0x1B).

## Description

Applied to the pinned golden rows (A, B, C row 1; row 2 fresh and stale), the trim rule (BC-1.01.006) produces a
fixed staircase of (visible width, segments kept) as COLUMNS decreases. This contract pins that staircase as a table
test so every segment boundary, the ♻ single-reset step and the "first segment never dropped" floor are exercised
on realistic rows.

## Preconditions

1. The golden fixture of BC-6.03.001 (P3r2 §A1: frozen `NOW = 1794615009.0`, TZ=UTC, prefixes `claude-sonnet`,
   seeded session cache, synthetic 6-line transcript, faked metrics sample) renders the untrimmed rows below.
2. `trim_to_fit(row, cols)` is called with `cols > 0` on each row independently.

## Postconditions

1. Notation `upper -> width/segments`: every COLUMNS value from `width` up to and including `upper` keeps that many
   segments and yields that visible width; `upper` is the largest COLUMNS giving the result.

   | Row (untrimmed width) | Staircase |
   |---|---|
   | A row 1 (198) | >=198 -> 198/12 · 197 -> 181/11 · 180 -> 149/10 · 148 -> 126/9 · 125 -> 117/8 · 116 -> 86/7 (single reset, ends `94%\e[0m`) · 85 -> 78/6 · 77 -> 61/5 · 60 -> 39/4 · 38 -> 28/3 · 27 -> 19/2 · 18 and below -> 8/1 |
   | B row 1 (173) | >=173 -> 173/11 · 172 -> 151/10 · 150 -> 119/9 · 118 -> 96/8 · 95 -> 87/7 (single reset) · 86 -> 79/6 · 78 -> 62/5 · 61 -> 40/4 · 39 -> 29/3 · 28 -> 20/2 · 19 and below -> 7/1 |
   | C row 1 (174) | >=174 -> 174/11 · 173 -> 151/10 · then identical to B |
   | Row 2 fresh (81) | >=81 -> 81/7 · 80 -> 56/6 · 55 -> 48/5 · 47 -> 30/4 · 29 -> 22/3 · 21 -> 9/2 · 8 and below -> 1/1 |
   | Row 2 stale (86) | >=86 -> 86/8 · 85 -> 73/7 · 72 -> 48/6 · 47 -> 40/5 · 39 -> 30/4 · 29 -> 22/3 · 21 -> 9/2 · 8 and below -> 1/1 |

2. Every row trimmed by at least one segment ends in `\e[0m\e[0m`, except when the kept last segment is ♻ (single
   `\e[0m`). The untrimmed rows end exactly as their goldens.
3. The 1-segment floor is kept even when wider than COLUMNS (A: 8 visible columns at COLUMNS 5).
4. End-to-end through the whole refresh with golden A (row-2 rule of BC-1.01.003 applies first):
   COLUMNS=80 -> 2 rows, widths [78, 56], 701 bytes, row 1 ends `…\e[35m◈ 8%\e[0m\e[0m`, row 2 ends
   `…\e[90m◔4.2s\e[0m\e[0m`; COLUMNS=100 -> [86, 81], 809 bytes; COLUMNS=72 -> [61, 56], 642 bytes;
   COLUMNS=71 -> 1 row, 61 columns, 286 bytes; COLUMNS=-5 -> 1 row untrimmed, 198 columns, 743 bytes.

## Invariants

1. The staircase widths are the cumulative sums of per-segment visible widths plus 3 per SEP. Segment widths (P3r2
   §A1): A row 1 = 8·8·6·8·19·14·5·28·6·20·29·14; B = 7·10·6·8·19·14·5·6·20·29·19; C = B with cost 20;
   row 2 fresh = 1·5·10·5·15·5·22; row 2 stale = 1·5·10·5·7·5·22·10.
2. Row 2 is trimmed only when `narrow_cols <= COLUMNS < its width`.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | COLUMNS exactly equal to a staircase width (A, 117) | keeps 8 segments, width 117 (fits, `>` is strict) |
| EC-002 | COLUMNS one below (A, 116) | drops to 7 segments, width 86, single reset (♻) |
| EC-003 | COLUMNS 1 on any row | first segment only + `\e[0m` |
| EC-004 | Production width COLUMNS=80 | see postcondition 4 |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| golden A row 1, COLUMNS 198 | untrimmed golden A row 1 (198 columns) | happy-path |
| golden A row 1, COLUMNS 116 | 7 segments, width 86, ends `\e[36m♻\e[0m 94%\e[0m` | edge-case |
| golden A row 1, COLUMNS 18 | `\e[105;30;1m ◨ ANTH \e[0m\e[0m` (width 8) | edge-case |
| golden A full refresh, COLUMNS 80 | 2 rows, widths [78, 56], 701 bytes | happy-path |
| golden A full refresh, COLUMNS 71 | 1 row, 61 columns, 286 bytes | edge-case |
| golden A full refresh, COLUMNS -5 | 1 row, 198 columns, 743 bytes | error |

Golden bytes are not duplicated here: the pinned reference is the Python-written Tier B golden set of BC-6.03.001
(source text P3r2 §A1). Staircase values pinned in P3r2 (`trim.py`, `cols.py`, `cols80.py`); this round re-derived
every staircase width from the segment widths (all match) but did not re-run the golden fixture.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-027 | For every COLUMNS in 1..max+1, Go trim of each golden row equals the pinned staircase entry | table test (exhaustive over the range) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009, CAP-010 |
| L2 Domain Invariants | — |
| Architecture Module | `internal/statusline` width (`width.go`) (BC-COMPONENT-MAP: internal/statusline/width.go (trim breakpoint matrix) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`trim_to_fit` (SL:1193-1197); `main` trim and row-2 gates SL:1224, 1232-1233 |
| Legacy contract | BC-SL-090 (new P3r2 §A1; index P3r4 §7.3) |
| Decisions | D4; owner capture COLUMNS=80 as production width (P3r2 §0 (a)) |

## Related BCs (Recommended)

- BC-1.01.006 — depends on (trim rule)
- BC-6.03.001 — depends on (golden rows A/B/C)
- BC-1.01.003 — composes with (row-2 gate before trim)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-width` — internal/statusline/width.go (trim breakpoint matrix) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — frame (design step S2) and goldens/burn-down (step S8)

## VP Anchors (Recommended)

- VP-027 — staircase table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1193-1197, 1224, 1232-1233) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **assertion**: pinned golden runs (P3r2 §A1)
- **inferred**: staircase = cumulative segment widths (re-derived this round)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (trim is pure; the fixture needs the full refresh) |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | pure |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed.
