---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T11:45:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md]
input-hash: "f2c1725"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "BC-SL-067"
parity_class: byte-exact
confidence: M
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

# Behavioral Contract BC-5.02.003: json.loads(bytes) acceptance set: BOM/UTF-16/32, invalid UTF-8, depth, NaN, duplicates

## Description

Each transcript line is decoded with `json.loads(line)` on **bytes** (SL:1061); any exception skips the line
(SL:1062-1063). Which lines count therefore depends on exactly which byte strings CPython 3.11 accepts.
`pyfmt.Decode(b, ModeBytes)` must accept and reject the same set, with the same resulting values. Go's
`encoding/json` differs on BOMs, UTF-16/32, invalid UTF-8, lone surrogates, NaN tokens, big ints, duplicate keys and
nesting depth, so it is not used (design IM-01; pitfall PR-09).

## Preconditions

1. `b` is one line produced by `SplitLinesBytes` (BC-5.03.002) from the complete-lines blob (SL:1055-1059); it never
   contains `\n` or `\r`.
2. The caller treats any returned error as "skip this line" (SL:1062-1063) and never degrades on it.

## Postconditions

1. **Encoding detection** (Python `json.detect_encoding`): BOM `00 00 FE FF` / `FF FE 00 00` → UTF-32; BOM `FE FF` /
   `FF FE` → UTF-16; BOM `EF BB BF` → UTF-8 with the BOM removed; else by the zero-byte pattern of the first 4 bytes
   (`00 00 ..` UTF-32-BE, `00 xx ..` UTF-16-BE, `xx 00 00 00` UTF-32-LE, `xx 00 ..` UTF-16-LE; for a 2-byte input
   `00 xx` UTF-16-BE, `xx 00` UTF-16-LE); otherwise UTF-8. Decoding uses the `surrogatepass` error handler.
2. **Invalid encoding** (e.g. `\xff` in UTF-8) → error (UnicodeDecodeError) → line skipped.
3. **Surrogates:** an encoded surrogate (`ED A0 80`) decodes to a lone surrogate code point (accepted, not
   replaced); JSON escapes `\ud800` are kept lone; an escaped high+low pair combines into one astral code point; a
   low+high escaped pair or a raw-byte surrogate pair stays two code points.
4. **JSON grammar** (CPython scanner, strict): whitespace only ` \t\n\r`; any top-level value; trailing non-space
   data → error; raw control characters U+0000-U+001F inside strings → error; a BOM remaining after decoding
   (e.g. a double UTF-8 BOM) → error; empty or all-whitespace → error.
5. **Numbers:** `-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][-+]?[0-9]+)?` with ASCII digits; without fraction/exponent → exact
   int (int64 or big), rejected with an error over 4,300 digits (PR-10); otherwise float64, correctly rounded, `1e400`
   → `+Inf`, `-0.0` → negative zero. Tokens `NaN`, `Infinity`, `-Infinity` (case-sensitive) → float NaN/±Inf; `nan`
   → error.
6. **Objects:** duplicate keys keep the **last** value at the **first** key's position (BC-5.02.004).
7. **Depth:** nesting beyond the CPython recursion budget at the legacy call site → error (RecursionError) → skipped.
   The boundary is a single limit `L`: depth `L` is accepted and depth `L + 1` is rejected — there is no gap. Go uses
   a named constant equal to `L`, with a "why not config" comment; Go's own 10,000-level limit must not apply. At
   this call site (`_mix_counts`, SL:1061) the pinned boundary is **L = 989 accepted / 990 rejected** for wrapped
   array nesting, measured 2026-11-17 with the recorded recipe (below) under the pinned oracle CPython 3.11.7,
   `python3 -I`, default recursion limit 1000, one line per fresh process. The stdin text-mode call site pins its
   own budget (993 accepted / 994 rejected, BC-1.01.002); the two differ because the recursion budget depends on
   the Python-frame depth of the call site. `Decode` therefore takes the recursion budget as a per-call-site
   parameter — it is never a package global.
   **Measurement recipe (how L was pinned):** run `python3 -I` with the legacy module imported
   (`importlib`, `legacy/dgx_statusline.py`), `mod.CACHE_DIR` redirected to an empty temp dir, and call
   `mod._mix_counts(d)` through one module-level runner frame so the frame depth at `json.loads` equals
   production (`module → main → _mix_counts → json.loads`). The transcript file holds the single line
   `{"type":"assistant","message":{"id":"m1","content":[{"type":"tool_use","input":` + `"["·d + "]"·d` + `}]}}`
   with a trailing `\n`; acceptance is observable as `conv = 2·d` (a rejected line leaves `conv = 0`). Bisect d;
   the largest accepted d is `L` (reproduced: 989 accepted, 990 rejected, four consecutive runs).

## Invariants

1. `Decode` never replaces data with U+FFFD and never panics; it returns `(Value, nil)` or an error.
2. The depth constant is a parity constant (named, with a "why not config" comment: it reproduces a CPython
   implementation limit at one call site).
3. `ModeText` (stdin and cache files, `json.load` on a text stream) is a different mode: there a BOM and invalid
   UTF-8 are errors; it is not this contract (BC-1.01.002, BC-1.01.008, BC-1.06.001).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `EF BB BF` + `{"message":{"content":"bom"}}` | accepted; counted (conv 3 at the composition site) |
| EC-002 | `{"a":1}` encoded UTF-16 with BOM; UTF-16-BE without BOM; UTF-32-LE | all accepted → `{"a": 1}` |
| EC-003 | `{"a":"\xff"}` | error → skipped |
| EC-004 | `"\xed\xa0\x80"` (encoded lone surrogate) | accepted → one lone surrogate |
| EC-005 | `{"x":1e400}` | accepted → `+Inf` |
| EC-006 | `{"a":1,"b":2,"a":3}` | accepted → ordered `a: 3, b: 2` |
| EC-007 | `"a\x01b"` (raw control char) | error |
| EC-008 | 4,301-digit integer literal | error (ValueError) → skipped |
| EC-009 | `{"a":1} x` | error (extra data) |
| EC-010 | Wrapped array nesting at depth 989 / 990 (`L` / `L + 1`) | accepted / error (RecursionError → skipped) |

## Canonical Test Vectors

| Input bytes | Expected Output | Category |
|-------|----------------|----------|
| `{"x":NaN}` | object `x: NaN` | happy-path |
| `{"x":Infinity,"y":-Infinity}` | `x: +Inf, y: -Inf` | happy-path |
| `123456789012345678901234567890` | exact big int | edge-case |
| `{"t":"\ud800"}` (JSON escape) | string of one lone surrogate | edge-case |
| `EF BB BF EF BB BF 7B 7D` (double BOM) | error | edge-case |
| `\xff`; empty; `   `; `nan` | error each | error |

All rows verified 2026-11-15 against CPython 3.11.7 `json.loads(bytes)`.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-024, VP-006 | `Decode(b, ModeBytes)` succeeds iff oracle `json.loads(b)` succeeds, with equal values (type-preserving) | fuzz (`Decode` target) + oracle table |
| VP-024, VP-006 | `Decode` never panics on arbitrary bytes | fuzz |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (a bad line never degrades), DI-012 |
| Architecture Module | `internal/pyfmt/json.go` `Decode` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/json.go (loads bytes acceptance) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1059-1063: `for line in blob[:cut].splitlines(): try: e = json.loads(line) except Exception: continue`) |
| Legacy contract | BC-SL-067 (new in P3r1 with BC-SL-033 refinement; index P3r4 §7.3) |
| Decisions | OD-103; design IM-01; pitfalls PR-09, PR-10, PR-11, PR-19; validation-log note (depth boundary is call-context dependent: 989/990 at this site vs 993/994 at the stdin site, design "Validation log") |

## Related BCs (Recommended)

- BC-1.03.004 — consumed by (`bytes.splitlines` + per-line `json.loads`)
- BC-5.02.004 — composes with (the decoded Value model)
- BC-5.03.002 — depends on (`SplitLinesBytes`)
- BC-1.03.018 — related to (D4-EX-2 handles wrong-shape lines that decode fine)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-json` — internal/pyfmt/json.go (loads bytes acceptance) (Python-compatible decoder) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt json (design step S1)

## VP Anchors (Recommended)

- VP-024, VP-006 — acceptance set equals the oracle

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1059-1063) |
| **Confidence** | medium (breadth of BOM/UTF-16/depth/NaN surface; design §8 conf M) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `except Exception: continue` (SL:1062-1063)
- **assertion**: pinned runs (P3r1; re-run 2026-11-15 incl. UTF-16/32, CESU, double BOM)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | pure |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed -- pure decoder, fuzzable against the oracle.
