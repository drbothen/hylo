---
document_type: behavioral-contract
level: L3
version: "1.2.7"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md]
input-hash: "bec9327"
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
modified:
  - "2026-11-17T21:21:12Z consolidated pass-2 follow-up: transcript-site depth boundary re-measured end to end at 993/994 (989/990 recipe not reproducible end to end)"
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-17T21:58:00Z patch bump + sync-check SC-08: Decode call snippets pinned to the 3-arg signature with the transcript budget"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D01+D11: boundary restated as TOTAL nesting depth (formula L = 999 minus F frames, F = 6); recipe re-derived, largest accepted d = 992 = L-1 (total 993); third stdin site main_subagent SL:930 pinned 993/994, over-limit = zero bytes stdout"
  - "2026-11-18T23:30:00Z (1.2.5) ADV-P5 remediation D17 — PC-7 reconciliation sentence: encoder budgets measured per site under the unified law 993 − W (BC-5.02.006 PC-6), strictly below the decoder acceptance at every shared context"
  - "2026-11-19T02:00:00Z (1.2.6) pass-5 remediation sweep — PC-7 encoder reconciliation restated to the re-measured sweep-C law (995 − s json.dump / 994 − s json.dumps, s = frames at the encode call inclusive; per-site budgets session/mix 991, record_cost/git 990, composition 991/990; Save budget equals Load budget; exposure = stdin rate_limits value depth 991..992, session-save document flip 991 saved / 992 skipped), matching BC-5.02.006 PC-6 and ARCH-06"
  - "2026-11-19T14:00:00Z (1.2.7) pass-6 residual sweep (call 5) — PC-1 rider: the one-line rule governs the stdin/transcript/cache line-splitting sites; the metrics reply body is decoded whole (ModeBytes, may be multi-line) at 992 accepted / 993 rejected (BC-1.04.001 PC3, VP-006)"
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
`pyfmt.Decode(b, ModeBytes, 993)` must accept and reject the same set, with the same resulting values. Go's
`encoding/json` differs on BOMs, UTF-16/32, invalid UTF-8, lone surrogates, NaN tokens, big ints, duplicate keys and
nesting depth, so it is not used (design IM-01; pitfall PR-09).

## Preconditions

1. `b` is one line produced by `SplitLinesBytes` (BC-5.03.002) from the complete-lines blob (SL:1055-1059); it never
   contains `\n` or `\r`. This one-line rule governs the line-splitting sites — the stdin decode (BC-1.01.002), the
   transcript lines (this contract) and the cache loaders (ARCH-04) — where the input is split into lines first. The
   metrics reply is the one whole-input exception: BC-1.04.001 PC3 decodes the complete reply body,
   `json.loads(resp.read())` on bytes (ModeBytes detection; the acceptance mechanics of this contract apply
   unchanged), and the body may be multi-line, at the fetch site's measured boundary **992 accepted / 993
   rejected** (F = 7 frames; VP-006 per-site table).
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
   The boundary is a single limit `L`: total nesting depth `L` is accepted and total depth `L + 1` is rejected — there is
   no gap. **Total nesting depth counts the outermost container as depth 1** (ADV-P3-D01 disposition: every statement of
   this boundary is in total-depth terms). The formula is `L = 999 − F`, where `F` is the number of Python frames on the
   interpreter stack between the program entry and `json.scanner`'s recursive parse call at that site (`F = 6` for each of
   the three stdin-adjacent call sites below). Go uses a named constant equal to `L`, with a "why not config" comment;
   Go's own 10,000-level limit must not apply. At this call site (`_mix_counts`, SL:1061) the pinned boundary is
   **L = 993 accepted / 994 rejected** for total nesting depth, measured 2026-11-18 end to end with the recorded recipe
   (below) under CPython 3.11.7, default recursion limit 1000. The stdin text-mode call site (BC-1.01.002) and the
   `main_subagent` stdin call site (`json.load(sys.stdin)`, SL:930; ADV-P3-D11) measure the same **993 accepted / 994
   rejected** — all three sites sit at `F = 6` Python frames (`<module>→main→…→json.load/loads→decode→raw_decode`).
   `Decode` therefore takes the recursion budget as a per-call-site parameter — it is never a package global — and each
   call site's value must be measured end to end, not inferred from another site.
   **Measurement recipe (how L was pinned):** run the REAL legacy program end to end — `HOME` and cwd pointed
   at fresh temp directories so `legacy/dgx_statusline.py` never touches the real cache — with the transcript
   file holding the single line
   `{"type":"assistant","message":{"id":"m1","usage":{"input_tokens":7}},"x":` + `"["·d + "]"·d` + `}`
   plus a trailing `\n`. The `d` nested arrays sit inside the outer object, so the line's **total nesting depth is
   d + 1**. Acceptance is observable in the mix cache: the largest accepted d leaves `tin = 7` (counted); a larger d is
   skipped (`tin = 0`). Bisect d; the largest accepted d is `L − 1` — **reproduced 2026-11-18: d = 992 accepted
   (total depth 993), d = 993 rejected (total depth 994)**. End-to-end invocation is required: the budget is per call
   site, and importing `_mix_counts` through a runner frame instead of the program's own `main` shifts the measured
   boundary. For the `main_subagent` site the same boundary is observed on stdout: stdin nested to total depth 993
   under `"tasks":[…]` renders a row (90 bytes); total depth 994 yields **zero bytes** (the swallowed `json.load`
   exception leaves `d = {}`, which renders no rows). **Encoder reconciliation (ADV-P5-D17, law as re-measured pass-5 sweep C; BC-5.02.006 PC-6, ARCH-06):** the
   encoder also spends one slot per level and one per Python frame, but its acceptance is `K_entry − s`:
   `995 − s` for `json.dump` (cache writes) and `994 − s` for `json.dumps` (C encoder), with `s` = Python
   frames at the encode call, invoking frame inclusive (`<module>` = 1). Pinned per-site budgets (measured
   end to end with `python3 -I`, CPython 3.11.7, isolated temp HOME+cwd): session/mix saves 991,
   record_cost/git 990, composition 991/990; the session-save end-to-end flip is a stdin document nesting
   991 saved / 992 skipped (stdin `rate_limits` value 990 — encoded document 991 — is the deepest that
   still saves). At equal chain depth every cache's Save budget EQUALS its Load budget (session/mix
   991/991, git/cost 990/990), so `Decode(Save(x))` never rejects what `Save` produced; a deeper stack
   never has the larger budget and a shallower stack never has the smaller one. The real exposure is the
   stdin side: a `rate_limits` nested to total value depth 991..992 decodes here (decoder bound 993) yet
   breaches the session Save budget 991, so a value that decodes can still fail to re-encode. `Decode`
   keeps its per-call-site `L`; the encoder's per-site `budget` travels with `Dumps`/`DumpsLen`.

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
| EC-010 | Total nesting depth 993 / 994 (`L` / `L + 1`) per the PC-7 recipe (recipe `d` = 992 / 993) | accepted / error (RecursionError → skipped) |

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
| VP-024, VP-006 | `Decode(b, ModeBytes, 993)` succeeds iff oracle `json.loads(b)` succeeds, with equal values (type-preserving) | fuzz (`Decode` target) + oracle table |
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
| Decisions | OD-103; design IM-01; pitfalls PR-09, PR-10, PR-11, PR-19; validation-log note (budgets are per call site and each site's value must be measured end to end; both current sites measure 993/994, design "Validation log") |

## Related BCs (Recommended)

- BC-1.03.004 — consumed by (`bytes.splitlines` + per-line `json.loads`)
- BC-1.07.003 — related to (the `main_subagent` stdin site: same boundary, over-limit → zero bytes stdout, ADV-P3-D11)
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
