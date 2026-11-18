---
document_type: behavioral-contract
level: L3
version: "1.3.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "6775882"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-055"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.3.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-040 P7"
  - "1.3.2 2026-11-18T04:00:00Z: pass-3 remediation (ADV-P3-B03): VP anchor names VP-040 P7 instead of VP-027"
  - "1.3.3 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) \u2014 pass-3 stamp re-dated ascending (it predated the preceding 1.3.1 reconciliation entry); no behavioral change"
  - "1.3.4 pass-7 remediation (ADV-P7-B01): H1 states the rows == 2 qualifier (negative COLUMNS hides row 2 only when rows == 2; rows >= 3 keeps it untrimmed per PC3/EC-004, SL:1224); no postcondition change; 2026-11-19T07:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.01.007: Negative COLUMNS disables trim and hides row 2 only when rows == 2

> Byte notation: `\e` = ESC (0x1B); `\n` = LF.

## Description

A COLUMNS value that parses (BC-1.01.005) to a negative integer is neither "unknown" (0) nor a usable width. Legacy
treats it as follows: trimming is skipped (`cols > 0` is false) and, when `rows == 2`, row 2 is hidden
(`cols == 0 or cols >= narrow_cols` is false). `rows > 2` still forces row 2. Go reproduces this exactly.

## Preconditions

1. `cols < 0` after the Python-grammar parse (e.g. `-5`, `" -72"`, `-` followed by up to 4,300 digits).
2. Configuration resolved (`statusline.rows`, `statusline.narrow_cols`).

## Postconditions

1. No row is trimmed; rows print at full width.
2. rows = 2 -> row 2 is omitted; stdout is row 1 + `\n`.
3. rows >= 3 -> row 2 is present (untrimmed).
4. rows = 1 -> row 1 only (unchanged rule).
5. The metrics fetch still runs when rows >= 2 (BC-1.04.013), even though row 2 is hidden.

## Invariants

1. `cols < 0` and `cols == 0` differ only in the row-2 decision; both disable trimming.
2. The sign must survive int64 overflow in Go (BC-1.01.005 postcondition 4).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `COLUMNS=-0` | parses to 0, not negative: no trim, row 2 shown |
| EC-002 | `COLUMNS=-` + 4,300 nines | negative: row 2 hidden |
| EC-003 | `COLUMNS=-` + 4,301 nines | exceeds the digit limit -> 0: row 2 **shown** (design IM-12 edge) |
| EC-004 | rows = 3, `COLUMNS=-5` | 2 rows, untrimmed |

## Canonical Test Vectors

Config: defaults, git disabled, metrics URL at a closed local port, empty cache, stdin `{}`.
R1 = `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97m?\e[0m`; R2 = `\e[31m◌ DGX ?\e[0m` (dead-marker word =
`statusline.pill.label_local` default per OD-189 reuse of OD-173).

| Input (rows, COLUMNS) | Expected Output | Category |
|-------|----------------|----------|
| 2, `-5` | `R1\n` (45 bytes) | happy-path |
| 3, `-5` | `R1\nR2\n` (64 bytes) | edge-case |
| 2, `-0` | `R1\nR2\n` (64 bytes) | edge-case |
| 2, `-` + 4,301 x `9` | `R1\nR2\n` (64 bytes) | error |
| Golden A fixture (BC-6.03.001), rows 2, `-5` | 1 row, untrimmed, 198 visible columns, 743 bytes | edge-case |

Rows 1-3 verified 2026-11-15 on CPython 3.11.7; row 4 follows from the verified `term_cols` result (0) and the
verified `COLUMNS` unset/0 behavior; row 5 pinned in P3r2 §A1 (`cols.py`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-040 | P7: for all cols < 0: rows untrimmed and row 2 present iff rows > 2 | property-test (testing/quick); VP-027 keeps the breakpoint matrix |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` width + orchestrator (BC-COMPONENT-MAP: internal/statusline/width.go (negative COLUMNS) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`term_cols` (SL:1188-1190) feeding `main` row-2 rule (SL:1224) and trim gate (SL:1232) |
| Legacy contract | BC-SL-055 (new in P3r1 §A1; index P3r4 §7.3) |
| Decisions | D4; owner ruling (a) production fixtures carry numeric COLUMNS, negative/missing are edge fixtures (P3r2 §0) |

## Related BCs (Recommended)

- BC-1.01.005 — depends on (parse)
- BC-1.01.003 — composes with (row-2 rule)
- BC-1.01.006 — related to (trim gate)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-width` — internal/statusline/width.go (negative COLUMNS) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — status line frame (design step S2)

## VP Anchors (Recommended)

- VP-040 P7 — for-all negative-COLUMNS universality (rows untrimmed, row 2 iff rows > 2; VP-027 retains the
  breakpoint matrix; ADV-P3-B03)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1188-1190, 1224, 1232) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: no explicit negative check; behavior falls out of `cols > 0` and `cols == 0 or cols >= NARROW_COLS`
- **assertion**: pinned runs 2026-11-15

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (decision logic) |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | pure |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. Do not "fix" negative widths before cutover (D4).
