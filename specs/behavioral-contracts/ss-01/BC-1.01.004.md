---
document_type: behavioral-contract
level: L3
version: "1.3.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T03:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "1244d41"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-004"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified: ["1.3.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet rows replaced with VP-040 P2/P3"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.01.004: Visible width counts code points after stripping SGR

> Byte notation: `\e` = ESC (0x1B).

## Description

The visible width of a decorated row, used only by the trim rule, is the number of Unicode code points left after
removing every SGR escape run matching the regex `\e\[[0-9;]*m`. It is not terminal-cell width: wide CJK glyphs and
emoji count 1, and a lone surrogate counts 1.

## Preconditions

1. Input is a row string (UTF-8 / WTF-8 in Go; may contain text that arrived from stdin, including ESC bytes).

## Postconditions

1. `visible(s)` = code-point length of `s` with all non-overlapping matches of `\e\[[0-9;]*m` removed (left to
   right, as Python `re.sub`).
2. `\e[m` (empty parameter list) is removed. Sequences whose parameter bytes fall outside `[0-9;]` or whose final
   byte is not `m` (e.g. `\e[?25l`, `\e]...`) are **not** removed and every one of their code points counts.
3. ESC sequences carried inside stdin text (display name, project label) are stripped the same way.

## Invariants

1. `visible` is pure and total (never fails, any input).
2. Go uses `pyfmt.Len` (code points; WTF-8 surrogate = 1) over an RE2-safe `regexp` with the explicit class `[0-9;]`;
   it must not use a terminal-width library such as go-runewidth (design IM-11, research P12).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `\e[97m漢字😀\e[0m` | 3 |
| EC-002 | `\e[1;91mA\e[38;2;1;2;3mB\e[m` | 2 |
| EC-003 | `\e[?25lX` (private-mode CSI, final `l`) | 7 (nothing stripped) |
| EC-004 | lone surrogate U+D800 (from a JSON escape) | 1 |
| EC-005 | empty string | 0 |
| EC-006 | SEP `\e[2m · \e[0m` | 3 |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `\e[106;30;1m ◨ DGX \e[0m\e[2m · \e[0m\e[97mSonnet 5.5\e[0m\e[2m · \e[0m\e[90m⎇ main\e[0m\e[2m · \e[0m\e[90mhome-lab\e[0m` | 40 | happy-path |
| `\e[97m漢字😀\e[0m` | 3 | edge-case |
| `\e[?25lX` | 7 | edge-case |
| `\ud800` (one lone surrogate) | 1 | error |

All verified 2026-11-15 by calling legacy `visible()` under CPython 3.11.7. Golden A row 1 = 198, B = 173, C = 174
(P3r2 §A1).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-040 | P2: `visible(a+b) == visible(a)+visible(b)` whenever neither split point falls inside an SGR run | property-test (testing/quick) |
| VP-040 | P3: Go `visible` equals CPython `len(_ANSI.sub("", s))` on generated strings incl. astral and WTF-8 lone-surrogate byte forms | differential property legs run under the ARCH-07 oracle harness (VP-034 isolation) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | — |
| Architecture Module | `internal/statusline` width (`width.go`) (BC-COMPONENT-MAP: internal/statusline/width.go (visible width, SGR strip) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`visible` (SL:151-153); `_ANSI` regex SL:137 |
| Legacy contract | BC-SL-004 (broad; refined P3r1 §A1; index P3r4 §7.3) |
| Decisions | D4; OD-103 (pyfmt) |

## Related BCs (Recommended)

- BC-1.01.006 — composes with (trim loop uses visible width)
- BC-5.03.001 — depends on (`pyfmt.Len` code-point counting)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-width` — internal/statusline/width.go (visible width, SGR strip) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — status line frame (design step S2)

## VP Anchors (Recommended)

- VP-027 — code-point width parity

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:137, 151-153) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **type constraint**: Python `len` on `str` counts code points
- **assertion**: pinned calls 2026-11-15

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (pure, no shared state) |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed — suitable for property testing.
