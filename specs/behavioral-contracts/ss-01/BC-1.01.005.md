---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "7d75fbc"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-005"
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

# Behavioral Contract BC-1.01.005: COLUMNS parses with the Python int grammar, else 0

## Description

The terminal width `cols` is read from the `COLUMNS` environment variable that Claude Code sets, and parsed with
CPython 3.11 `int(str)` grammar. Absent or unparseable values give 0 ("width unknown"). `COLUMNS` is a Claude Code
protocol input, not a hylo setting: it has no `HYLO_*` key and is not validated as config (design IM-12; BC-2.01.005).

## Preconditions

1. `COLUMNS` may be absent, empty, or any string.

## Postconditions

1. Absent -> 0.
2. Otherwise `cols = int(COLUMNS)` under the Python grammar: optional surrounding Unicode whitespace; optional `+`/`-`;
   decimal digits from any Unicode `Nd` script (incl. fullwidth and Arabic-Indic); single `_` between digits allowed;
   at most 4,300 digits.
3. Any value outside that grammar gives 0: empty string, `80.0`, `0x50`, `1__0`, `_1`, more than 4,300 digits.
4. The value is an arbitrary-precision integer in Python; Go may use `pyfmt.ParseInt` (int64 fast path, big
   promotion). A positive value too large for int64 must behave as "no trim, row 2 shown" (identical output to a
   huge Python int, P3r1 §A1). A negative value beyond int64 range (up to 4,300 digits) must stay **negative**
   (row 2 hidden, BC-1.01.007); mapping int64 overflow to 0 would show row 2 and diverge, so the Go parser must
   keep the sign (clamping to `math.MinInt64` is output-equivalent).

## Invariants

1. Parsing never fails the refresh.
2. The result feeds exactly two decisions: row-2 visibility (BC-1.01.003) and trimming when `cols > 0`
   (BC-1.01.006). Negative results are BC-1.01.007.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `" 80 "` | 80 |
| EC-002 | `"٨٠"` (Arabic-Indic) | 80 |
| EC-003 | `"１２"` (fullwidth) | 12 |
| EC-004 | `"1_000"` | 1000 |
| EC-005 | `"+72"` | 72 |
| EC-006 | `"80.0"`, `"0x50"`, `""`, `"1__0"`, `"_1"` | 0 |
| EC-007 | `"-0"` | 0 |
| EC-008 | 30 nines | exact big int (no trim, row 2 shown) |
| EC-009 | `"-"` + 4,301 nines | 0 (digit limit) -> no trim, row 2 **shown** (contrast BC-1.01.007) |
| EC-010 | absent | 0 |

## Canonical Test Vectors

| Input (COLUMNS) | Expected Output (cols) | Category |
|-------|----------------|----------|
| `80` | 80 | happy-path |
| `" 80 "` | 80 | edge-case |
| `"٨٠"` | 80 | edge-case |
| `"1_000"` | 1000 | edge-case |
| `"+72"` | 72 | edge-case |
| `"80.0"` | 0 | error |
| `"0x50"` | 0 | error |
| `"-"` + 4,301 x `9` | 0 | error |

All verified 2026-11-15 by calling legacy `term_cols()` under CPython 3.11.7.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-027 | Go `term_cols` equals CPython `int()`-or-0 on generated strings (Unicode digits, underscores, signs, whitespace) | Tier C differential fuzz / table |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | — |
| Architecture Module | `internal/statusline` width (`width.go`) (BC-COMPONENT-MAP: internal/statusline/width.go (COLUMNS grammar via py.ParseInt) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`term_cols` (SL:1185-1190); read twice in `main` SL:1209, 1211 (same value) |
| Legacy contract | BC-SL-005 (broad; refined P3r1 §A1; index P3r4 §7.3) |
| Decisions | D4; OD-103; OD-05 (COLUMNS is not a HYLO_* key) |

## Related BCs (Recommended)

- BC-1.01.007 — related to (negative values)
- BC-1.01.003 — composes with (row-2 rule)
- BC-5.01.002 — depends on (`pyfmt.ParseInt` grammar)
- BC-2.01.005 — related to (COLUMNS excluded from config grammars)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-width` — internal/statusline/width.go (COLUMNS grammar via py.ParseInt) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — status line frame (design step S2)

## VP Anchors (Recommended)

- VP-027 — COLUMNS grammar parity

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1185-1190) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `except (ValueError, TypeError): return 0`
- **assertion**: pinned calls 2026-11-15

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads env |
| **Global state access** | reads environment |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | mixed (env read; parse pure) |

#### Refactoring Notes

Read COLUMNS through `Env.Getenv` (design §2.2) and pass the string to the pure parser.
