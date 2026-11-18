---
document_type: behavioral-contract
level: L3
version: "1.3.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "7ba340a"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-003"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified: ["1.3.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-040 P1 (catalog lists this BC)", "1.3.2 2026-11-18T02:00:00Z: pass-3 remediation (ADV-P3-B03/B15/B10): VP anchor names VP-040 P1; PC5 source lines corrected (project label is SL:460-462); ARCH-03 anchor normalized to #statusline-width"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.01.003: Rows join with LF; row 2 shown only when width permits

> Byte notation: `\e` = ESC (0x1B); `\n` = LF.

## Description

The status line output is row 1 (session/lane row) optionally followed by row 2 (backend telemetry strip), joined
by a single LF and terminated by one trailing LF, written once. Row 2 is included only when the configured row
count allows it and the terminal width (COLUMNS) is unknown or wide enough. Each row's segments are joined by the
separator `SEP`.

## Preconditions

1. Configuration resolved: `statusline.rows` (int, default 2, env `HYLO_STATUSLINE_ROWS`) and
   `statusline.narrow_cols` (int, default 72, env `HYLO_STATUSLINE_NARROW_COLS`).
2. `cols` = the parsed COLUMNS value (BC-1.01.005; may be 0, positive or negative).
3. The refresh did not degrade (otherwise BC-1.01.001).

## Postconditions

1. Row 2 is present **iff** `rows >= 2` AND (`rows > 2` OR `cols == 0` OR `cols >= narrow_cols`).
2. stdout = row 1, then (if present) `\n` + row 2, then exactly one trailing `\n`. Row 1 is always first.
3. Each row is `SEP.join(segments)` with `SEP` = `\e[2m · \e[0m` (default `statusline.theme` separator, OD-113).
4. Rows are trimmed (BC-1.01.006) only after the row-2 decision and only when `cols > 0`.
5. No `\r` is emitted by the renderer itself (LF only on every OS). Carve-out: input-derived text is emitted
   verbatim, so it can carry CR or LF bytes to stdout — a stdin `display_name`/`id` (SL:442-443) or project label
   (SL:460-462) containing `"a\rb"` or `"a\nb"` adds those bytes to the row at the single print (SL:1234), and a
   git branch whose HEAD file held a CR is read in text mode with universal newlines and comes back with an LF
   inside (SL:385-386).

## Invariants

1. At most two rows; never an empty stdout. (Verbatim input-derived text may embed LF bytes that display as extra
   lines — PC5 carve-out; the renderer still emits at most two of its own rows.)
2. The row-2 decision does not affect whether the metrics fetch runs: the fetch happens whenever `rows >= 2`, even if
   row 2 is then hidden for width (BC-1.04.013).

Threshold rationale (D15): `rows` default 2 — convention: the two-row design (P4r7 T-002). `narrow_cols` 72 with
operator `>=` keeps row 2 — owner judgment (presentation), catalogue resolution T-014 = OWNER group B
(layout/aesthetics), accepted under OD-57 E-B. `cols == 0` means "width unknown, treat as wide" (P4r7 T-116).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | rows = 1, any COLUMNS | row 1 only |
| EC-002 | rows = 2, COLUMNS unset or `0` | 2 rows |
| EC-003 | rows = 2, COLUMNS = 71 | row 1 only (`71 >= 72` false) |
| EC-004 | rows = 2, COLUMNS = 72 | 2 rows (boundary inclusive) |
| EC-005 | rows = 3, COLUMNS = 10 | 2 rows (rows > 2 forces row 2; both rows then trimmed to 10) |
| EC-006 | rows = 2, negative COLUMNS | row 1 only (BC-1.01.007) |
| EC-007 | rows = 2, COLUMNS = `-0` | parses to 0 -> 2 rows, no trim |

## Canonical Test Vectors

Config: defaults, `HYLO_STATUSLINE_GIT_ENABLED=0`, metrics URL pointing at a closed local port, empty cache dir,
stdin `{}`. R1 = `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97m?\e[0m`; R2 = `\e[31m◌ DGX ?\e[0m` (fetch failed, no
cache; legacy default label text).

| Input (rows, COLUMNS) | Expected Output | Category |
|-------|----------------|----------|
| 2, unset | `R1\nR2\n` (64 bytes) | happy-path |
| 1, unset | `R1\n` (45 bytes) | happy-path |
| 2, `71` | `R1\n` (45 bytes) | edge-case |
| 2, `72` | `R1\nR2\n` (64 bytes) | edge-case |
| 3, `71` | `R1\nR2\n` (64 bytes) | edge-case |
| 2, `-5` | `R1\n` (45 bytes) | edge-case |
| 2, `0` | `R1\nR2\n` (64 bytes) | edge-case |

Full ROWS {1,2,3} x COLUMNS {unset, 0, 71, 72, -5, -0, 10} matrix verified 2026-11-15 on CPython 3.11.7
(design S2 "ROWS x COLUMNS matrix", T-116). Golden-A end-to-end: COLUMNS=71 -> 1 row, 61 columns, 286 bytes;
COLUMNS=72 -> widths [61, 56], 642 bytes (P3r2 §A1; BC-1.01.010).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-040 | P1: output has 1 + [row-2 predicate] renderer rows, each LF-terminated, for all (rows, cols) and inputs whose rendered strings hold no LF/CR (PC5 carve-out) | property-test (testing/quick); VP-027 keeps the fixed breakpoint matrix, VP-040 delivers the quantified leg |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009, CAP-010 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` orchestrator (`statusline.go`) (BC-COMPONENT-MAP: internal/statusline/statusline.go (rows, LF join, width rule) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`main` (SL:1224-1234); `NARROW_COLS` SL:100; `ROWS` SL:75; `SEP` SL:128 |
| Legacy contract | BC-SL-003 (broad sweep HIGH-R; index P3r4 §7.3) |
| Decisions | D4, D15, OD-57 E-B, OD-113 |

## Related BCs (Recommended)

- BC-1.01.005 — depends on (COLUMNS parse)
- BC-1.01.006 — composes with (trim after the row decision)
- BC-1.01.007 — related to (negative COLUMNS hides row 2)
- BC-1.04.013 — related to (fetch runs whenever rows >= 2)
- BC-2.01.004 — depends on (key registry entries for rows / narrow_cols)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-width` — internal/statusline/statusline.go (rows, LF join, width rule) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — status line frame (design step S2)

## VP Anchors (Recommended)

- VP-040 P1 — for-all row-count/LF-termination over (rows, cols) and inputs (VP-027 retains the fixed breakpoint
  matrix; ADV-P3-B03)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1217, 1224-1234) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if (rows_env > 2 or cols == 0 or cols >= NARROW_COLS)` (SL:1224)
- **assertion**: pinned matrix runs 2026-11-15

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | writes stdout (single print) |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | mixed (row assembly pure; print effectful) |

#### Refactoring Notes

The row-2 predicate and join are a pure function of (rows, narrow_cols, cols, row strings); only the final write is
effectful.
