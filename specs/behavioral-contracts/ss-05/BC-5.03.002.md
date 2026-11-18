---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T03:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md, owner-decisions-log-2026-11-14.md]
input-hash: "bebcc79"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces str.strip/rstrip/rsplit and bytes.splitlines used in legacy/dgx_statusline.py)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T03:00:00Z VP citation reconciliation: SplitLinesBytes row re-homed from VP-025 to VP-038 (pass-2 mint; VP-038 partial-coverage note)"
  - '2026-11-18T23:50:00Z (1.2.3) ADV-P5 D26 — EC-002 notation: NEL spelled as the \u0085 code-point escape, disambiguated from the BC-5.01.002 raw-byte \xNN convention'
  - "1.2.4 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-15) — 1.2.3 entry requoted single-quoted (the raw-byte escape spellings are not YAML double-quoted-scalar escapes); no behavioral change"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.03.002: Strip/RStrip/RSplit1/SplitLinesBytes: Python whitespace; \n \r\n \r only

## Description

Four Python string operations whose boundary sets differ from Go's: `str.strip()` (Unicode whitespace per
`str.isspace`), `str.rstrip(chars)`, `str.rsplit(sep, 1)` and `bytes.splitlines()` (only `\n`, `\r\n`, `\r`, unlike
`str.splitlines`). `pyfmt.Strip`, `RStrip`, `RSplit1` and `SplitLinesBytes` reproduce them exactly (design IM-11;
pitfall PR-12). Signature note (ADV-P1-D06, resolved ADV-P2-D08): this contract pins `RSplit1` to Python
`rsplit(sep, 1)` semantics — it returns the 1- or 2-element list `[head, tail]` / `[s]`; the ARCH-06
signature row (`RSplit1(s, sep string) []string`) is reconciled.

## Preconditions

1. `Strip`, `RStrip`, `RSplit1` take Value/Go strings (code points); `SplitLinesBytes` takes raw bytes.
2. `RSplit1(s, sep)` takes a non-empty `sep` (legacy passes `SEP`, SL:1196).

## Postconditions

1. **Strip(s)** removes leading and trailing code points for which Python `str.isspace()` is true — exactly these 29:
   U+0009-U+000D, U+001C-U+001F, U+0020, U+0085, U+00A0, U+1680, U+2000-U+200A, U+2028, U+2029, U+202F, U+205F,
   U+3000. U+200B (zero-width space) and U+FEFF are **not** stripped. (This set differs from the `int()`/`float()`
   whitespace set, which excludes U+001C-U+001F, BC-5.01.002.)
2. **RStrip(s, chars)** removes trailing code points that are members of `chars` (a set, not a suffix):
   `RStrip("claude-sonnet**", "*")` = `claude-sonnet`, `RStrip("***", "*")` = `""`, `RStrip("a*b*", "*")` = `a*b`.
3. **RSplit1(s, sep)** returns `[head, tail]` split at the **last** occurrence of `sep`, or `[s]` when `sep` does not
   occur (`RSplit1("", "|")` = `[""]`).
4. **SplitLinesBytes(b)** splits at `\r\n`, `\n` or `\r` only (a `\r\n` pair is one boundary); a trailing terminator
   does not produce a final empty element; `b""` → `[]`. Bytes `\v`, `\f`, `\x1c`-`\x1e`, `\xc2\x85` (NEL in UTF-8)
   and U+2028/U+2029 encodings are **not** boundaries.

## Invariants

1. `strings.TrimSpace` (Go's `unicode.IsSpace` set includes U+0085/U+00A0 but its exact set must not be relied on),
   `bufio.Scanner` lines and `strings.Split(s, "\n")` are never used in place of these helpers.
2. Uses served: `p.strip()` on model prefixes (SL:444-445), `p.rstrip("*")` (SL:487), `row.rsplit(SEP, 1)` in
   `trim_to_fit` (SL:1196), `blob[:cut].splitlines()` (SL:1059).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `Strip("\u00a0 x \u200b")` | `"x \u200b"` (NBSP stripped; ZWSP kept, so the trailing space before it stays) |
| EC-002 | `Strip("\x1c\x1fx\u0085")` (U+0085 NEL written as the `\u0085` code-point escape — a raw `\x85` byte is invalid UTF-8 and not a str here, per the BC-5.01.002 `\xNN` raw-byte notation) | `"x"` |
| EC-003 | `Strip(" \u3000x\u2028")` (leading plain space + U+3000 IDEOGRAPHIC SPACE; trailing U+2028 LINE SEPARATOR, escape notation) | `"x"` (U+3000 and U+2028 are in Python str.strip()'s space set) |
| EC-004 | `SplitLinesBytes(b"\n")` | `[b""]` |
| EC-005 | `SplitLinesBytes(b"a\r\rb")` | `[b"a", b"", b"b"]` |
| EC-006 | `SplitLinesBytes(b"\r\n\r")` | `[b"", b""]` |
| EC-007 | `RSplit1("abc", " · ")` | `["abc"]` |

In vector cells the escapes `\uXXXX` (e.g. `\u200b` = ZERO WIDTH SPACE, `\u00a0` = NBSP) denote that code point, written visibly so the byte content of the vector is unambiguous; no cell contains a literal invisible character.

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `SplitLinesBytes(b"ab\rcde\r\n\n\x0bf\x0cg\x1ch\xc2\x85i")` | `[b"ab", b"cde", b"", b"\x0bf\x0cg\x1ch\xc2\x85i"]` | happy-path |
| `RSplit1("a · b · c", " · ")` | `["a · b", "c"]` | happy-path |
| `RStrip("claude-sonnet**", "*")` | `"claude-sonnet"` | happy-path |
| `SplitLinesBytes(b"a\n")`; `SplitLinesBytes(b"")` | `[b"a"]`; `[]` | edge-case |
| `Strip("\u200b")` | `"\u200b"` (nothing removed) | error (non-whitespace look-alike) |

Verified 2026-11-15 against CPython 3.11.7 (`str.isspace` enumeration over all code points; `strip`, `rstrip`,
`rsplit`, `bytes.splitlines`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-025 | `Strip` equals oracle `str.strip()` for strings built from the 29 whitespace code points plus look-alikes | Go property test (testing/quick) + oracle table |
| VP-038 | `SplitLinesBytes` split points equal CPython 3.11 `bytes.splitlines()` (keepends=False) on `\n`/`\r\n`/`\r`; pieces carry no terminators; pinned by committed oracle corner tables + random self-consistency | oracle corner tables (OD-142) + Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/str.go` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/str.go (whitespace/splitlines) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103; design IM-11; pitfall PR-12. Legacy uses served: SL:444-445, 487, 1059, 1196 |

## Related BCs (Recommended)

- BC-1.02.001, BC-1.02.009 — consumed by (prefix strip, reroute-all `rstrip("*")`)
- BC-1.01.006 — consumed by (`trim_to_fit` `rsplit`)
- BC-1.03.004 — consumed by (`bytes.splitlines`)
- BC-5.01.002 — contrasts with (numeric-parse whitespace set)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-str` — internal/pyfmt/str.go (whitespace/splitlines) (whitespace and split helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt str (design step S1)

## VP Anchors (Recommended)

- VP-025 — strip set equals `str.isspace`

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/str.go (whitespace/splitlines)` (BC-COMPONENT-MAP: py/str.go (whitespace/splitlines) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
