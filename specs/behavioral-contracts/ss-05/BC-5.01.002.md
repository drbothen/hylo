---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T11:45:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md, owner-decisions-log-2026-11-14.md]
input-hash: "a7014d0"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces CPython int()/float() of str used at legacy/dgx_statusline.py SL:1188, 178, 853, 866)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-18: ADV-P4 remediation D14+D31 — character classes (Nd, whitespace, printable) pinned to hylo's generated Unicode 14.0.0 tables from CPython 3.11.7 unicodedata under go generate, oracle version constant + CI staleness test (OD-170); \\x85 vs U+0085 escape ambiguity resolved in EC-003 and the notation note"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.01.002: ParseInt/ParseFloat Python grammar: underscores, Unicode digits, signs, 4,300-digit limit, nan/inf/1e400

## Description

`pyfmt.ParseInt(s) (Num, error)` and `pyfmt.ParseFloat(s) (float64, error)` accept exactly the strings that CPython
3.11 `int(s)` and `float(s)` accept, with the same values. The status line parses protocol inputs with them:
`COLUMNS` (SL:1188), metrics-store sample strings (SL:178) and stdin values coerced in `_fmt_lines`/`_fmt_tok_c`
(SL:853, 866). Hylo's own settings do **not** use this grammar: they are typed config values, and underscore or
Unicode-digit numerals there are config errors (D4-EX-3, BC-2.02.003).

## Preconditions

1. `s` is a Go string holding the Python str (may contain any Unicode, including WTF-8 surrogates).
2. Base 10 only (legacy never passes a base).
3. **Character-class oracle (OD-170, ADV-P4-D14):** every Unicode class this contract
   consults — decimal digit (Nd), whitespace, printable, and any other class pyfmt
   consults — is resolved from hylo's own generated tables pinned to **Unicode 14.0.0**,
   generated from CPython 3.11.7 `unicodedata` by a committed generator script run under
   `go generate`. pyfmt never consults Go's `unicode` package for these classes (Go
   releases carry newer tables — e.g. the Kawi digits U+11F50..59 are Nd in Go but not in
   14.0). A version constant (`14.0.0`) and a generated-table test pin the tables to the
   oracle; CI fails when the generated file is stale. P6 may move to a current Unicode.

## Postconditions

1. **Whitespace.** Leading and trailing characters are skipped if they are ASCII ` \t\n\v\f\r` or **non-ASCII**
   Unicode whitespace (`U+0085`, `U+00A0`, `U+1680`, `U+2000`-`U+200A`, `U+2028`, `U+2029`, `U+202F`, `U+205F`,
   `U+3000`), membership per the OD-170 pinned tables (Pre-3). `U+001C`-`U+001F` are **not** skipped (they are `str.isspace()` but rejected by `int()`/`float()`), and
   `U+200B` is not whitespace.
2. **Digits.** Any Unicode decimal digit (category Nd per the OD-170 pinned tables, Pre-3, e.g. `٣`, `１２`) counts as its ASCII value. Code points assigned after Unicode 14.0 (e.g. Kawi digits U+11F50..59) are NOT digits to pyfmt, matching CPython 3.11.7's `int()` (ADV-P4-D14).
3. **ParseInt grammar.** `[+-]? digit (_? digit)*`: at most one sign, single underscores only between digits, no
   prefix (`0x10` rejected), no `.`/exponent (`4.0` rejected), leading zeros allowed (`007` → 7). Result is exact:
   int64 when it fits, else big integer; the sign and magnitude survive any accepted length — at the `COLUMNS` call
   site (SL:1188) an overflowing negative stays negative, so row 2 stays hidden (BC-1.01.005 PC-4; clamping to
   `math.MinInt64` is output-equivalent there), and only the over-4,300-digit `ErrValue` path maps to 0 (EC-006).
4. **4,300-digit limit (PR-10).** ParseInt fails with `ErrValue` when the number of digits (sign, underscores and
   whitespace excluded; leading zeros included) exceeds 4,300. Exactly 4,300 digits is accepted.
5. **ParseFloat grammar.** Python float syntax: `[+-]?` then a decimal with optional fraction and exponent
   (`.5`, `5.`, `1E-3`, `1.5e+3`), single underscores only between digits in every digit group (`1_0.5`,
   `0_0.0_1`, `1e1_0` accepted; `_1.0`, `1_.5`, `1._5`, `1_e3`, `1__0` rejected), or the case-insensitive words
   `nan`, `inf`, `infinity` with an optional sign. No 4,300 limit. Overflow gives `±Inf` (`1e400` → `+Inf`,
   `1.7976931348623159e308` → `+Inf`), underflow gives `0.0`/`-0.0`; `-0.0` keeps its sign; `-nan` → NaN.
   Hex floats (`0x1p3`) rejected. Correctly rounded (round-half-even on the exact decimal).
6. Any rejection returns typed `ErrValue` (Python `ValueError`); the caller applies its own catch list.

## Invariants

1. `strconv.Atoi`/`ParseInt`/`ParseFloat` are never applied directly to these inputs (they reject `_`, Unicode digits
   and Unicode whitespace, and spell specials differently).
2. Committed CPython-generated table plus a `go test -fuzz` target for `ParseFloat` (design §2.6).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `ParseInt("1_000")` / `"1__0"` / `"_1"` / `"1_"` | `1000` / err / err / err |
| EC-002 | `ParseInt("-_1")`, `"+ 1"`, `"--1"`, `"+-1"`, `"1 2"` | all err |
| EC-003 | `ParseInt(" 12 ")`, `" -5 "`, `"\u0085" + "5"` | `12`, `-5`, `5` |
| EC-004 | `ParseInt("\x1c5\x1f")`, `"5\u200b"` | err, err |
| EC-005 | `ParseInt` of 4,300 `1`s; of `"1_"` + 4,299 `1`s; of `"+"` + 4,300 `1`s | accepted (4,300 digits each) |
| EC-006 | `ParseInt` of 4,301 `1`s; of `"0"` × 4,301; of `"-"` + 4,301 `1`s | `ErrValue`. Consequence at SL:1188: a 4,301-digit negative `COLUMNS` → 0 → row 2 shown, whereas a shorter negative value hides row 2 (BC-1.01.005/007) |

| EC-007 | `ParseInt("")`, `"  "` | err |
| EC-008 | `ParseFloat("4.9e-325")` | `0.0` |

In vector cells the escapes `\uXXXX` (e.g. `\u200b` = ZERO WIDTH SPACE, `\u00a0` = NBSP) denote that code point, written visibly so the byte content of the vector is unambiguous; no cell contains a literal invisible character. A `\xNN` escape denotes the single raw byte 0xNN in Go literal notation \u2014 it is a code point only when NN is ASCII, and a standalone `\x85` would be an INVALID UTF-8 byte, not U+0085; this table therefore writes U+0085 as `\u0085` (ADV-P4-D31).

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `ParseInt("42")`; `" 42 "`; `"+7"`; `"-0"`; `"٣"`; `"１２"` | `42`; `42`; `7`; `0`; `3`; `12` | happy-path |
| `ParseFloat("1.5")`; `" 1.5 "`; `"  1.5 "`; `"١.٥"`; `"１.５"`; `"١e٢"` | `1.5`; `1.5`; `1.5`; `1.5`; `1.5`; `100.0` | happy-path |
| `ParseFloat("NaN")`; `"nAn"`; `"+Inf"`; `"iNfInItY"`; `"-Infinity"`; `"1e400"`; `"-1e400"`; `"  -0.0 "` | NaN; NaN; +Inf; +Inf; -Inf; +Inf; -Inf; `-0.0` | edge-case |
| `ParseFloat("1_0.5")`; `"0_0.0_1"`; `"1e1_0"` | `10.5`; `0.01`; `1e10` | edge-case |
| `ParseFloat("1__0")`; `"_1.0"`; `"1e"`; `"0x1p3"`; `""`; `"in f"`; `"\x1c5"` | all `ErrValue` | error |
| `ParseInt("0x10")`; `"4.0"`; 4,301 digits | all `ErrValue` | error |

All values verified 2026-11-15 against CPython 3.11.7 (`int`, `float`, default `PYTHONINTMAXSTRDIGITS`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-023 | `ParseFloat` accepts/rejects and values match the CPython oracle on fuzzed strings | fuzz (`go test -fuzz`) + oracle table |
| VP-023 | `ParseInt(s)` succeeds iff the oracle `int(s)` succeeds, with equal value | fuzz + oracle table |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/num.go` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/num.go (ParseInt/ParseFloat) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103; design IM-12; pitfalls PR-10, PR-18. Legacy call sites served: SL:1188 (`int(COLUMNS)`), SL:178 (`float(s["value"][1])`), SL:853 (`int(n)`), SL:866 (`float(n)`); the import-time env parses SL:74-75 are replaced by `internal/config` (IM-16), not by this helper |

## Related BCs (Recommended)

- BC-1.01.005, BC-1.01.007 — consumed by (`COLUMNS` grammar)
- BC-1.04.001 — consumed by (metrics-store value strings)
- BC-1.02.014, BC-1.02.018 — consumed by (`_fmt_lines`, `_fmt_tok_c`)
- BC-2.02.003 — contrasts with (the same numerals are config errors in hylo settings)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-num` — internal/pyfmt/num.go (ParseInt/ParseFloat) (Python numeric parsing) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt num (design step S1)

## VP Anchors (Recommended)

- VP-023 — parse acceptance equals the oracle

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/num.go (ParseInt/ParseFloat)` (BC-COMPONENT-MAP: py/num.go (ParseInt/ParseFloat) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
