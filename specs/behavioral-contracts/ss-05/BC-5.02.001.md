---
document_type: behavioral-contract
level: L3
version: "1.2.5"
status: draft
producer: product-owner
timestamp: 2026-11-19T00:20:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "3ee40d0"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "BC-SL-071"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z (1.2.2) ADV-P3 remediation D09+D12: expected bytes written as escape notation (wire forms shown); DumpsLen gains (int, error) with ErrValue on encoder-failure ints past 4300 digits; anchor fix (notation per PC-4, not BC-5.01.002)"
  - "2026-11-18T22:00:00Z (1.2.3) ADV-P4 remediation D17 — Inv 4 recursion economy measured: decoder and encoder consume one slot per nesting level (max depth = limit − 8 at module scope, limits 700/1000/1300), encoder boundary strictly lower at every call site"
  - "2026-11-18T23:30:00Z (1.2.4) ADV-P5 remediation D28+D08/D17 — Description signature corrected to DumpsLen(v Value, budget int) (int, error) (D28); Inv 4 recursion law restated per site (max total nesting = 993 − W at the encode call, W = Python frames; SL:1140/1147 budget 990, SL:1138 genexp budget 989); ErrDepth past the site budget"
  - "2026-11-19T00:20:00Z (1.2.5) pass-5 sweep C end-to-end re-measurement — Inv 4 depth values: law 994 − s (json.dumps) / 995 − s (json.dump), s = Python frames at the encode call inclusive; composition budgets SL:1140/1147 = 991 (s=3), SL:1138 genexp = 990 (s=4); no input-borne transcript Value can both decode and fail measurement (line-decode cap under the wrapper), correcting the decode-and-still-fail consequence"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.02.001: json.dumps length rules (escaping, float repr, inner-null 0)

## Description

The composition widget measures transcript blocks in characters of Python's `json.dumps` output (SL:1138, 1140,
1147). `pyfmt.DumpsLen(v Value, budget int) (int, error)` returns exactly `len(json.dumps(v))` for any decoded
`Value`, using Python's
defaults (separators `", "`/`": "`, `ensure_ascii`, float `repr`, NaN tokens, insertion order), and the call sites
apply legacy's per-site fallbacks, including "a `null` non-list inner value counts 0". `DumpsLen` shares its
escaping and float-repr code with the cache encoder `Dumps` (IM-03) so the two cannot drift. `budget` is the
per-site recursion budget (BC-5.02.006 PC-6); exceeding it returns `ErrDepth`.

## Preconditions

1. `v` is a `pyfmt.Value` produced by `Decode` (BC-5.02.003) or a sub-value of one: null, bool, int (int64 or big),
   float64 (incl. NaN/±Inf), string (code points incl. lone surrogates, BC-5.02.004), array, ordered object.
2. The three call sites (all in `_mix_counts`):
   - SL:1137-1138 tool_result list item `it`: 2000 if `it` is an object whose `type` == `"image"`, else
     `len(json.dumps(it))` (no fallback);
   - SL:1140 tool_result inner value that is neither str nor list: `len(json.dumps(inner)) if inner is not None
     else 0`;
   - SL:1147 tool_use input: `len(json.dumps(blk.get("input") or ""))` (falsy → `""`).

## Postconditions

1. `DumpsLen(v)` equals the number of characters of `json.dumps(v)`; the output is pure ASCII, so characters =
   bytes.
2. **Scalars:** `null` 4, `true` 4, `false` 5; ints in decimal with a `-` sign, exact for any size (`9223372036854775808`
   is 19); `NaN` 3, `Infinity` 8, `-Infinity` 9.
3. **Float repr (PR-07):** shortest round-trip digits; scientific notation when the decimal exponent `e` (value =
   d.ddd × 10^e) is `< -4` or `>= 16`, written `<digits>e<sign><at least 2 digits>` (`1e-05`, `1e+16`, `1.5e-07`,
   `e+308`); otherwise fixed notation with `.0` appended to integral values (`100.0`, `1000000000000000.0`, `0.0001`,
   `-0.0`).
4. **Strings:** `"` + escaped content + `"`. `"` → `\"`, `\` → `\\`, `\n \r \t \b \f` → two characters each; other
   code points below U+0020 → `\u00XX` (6); U+007F and above → `\uXXXX` with lowercase hex (6); astral code points →
   a surrogate pair (12); a lone surrogate → `\udXXX` (6); `/` is **not** escaped; no HTML escaping (`<`, `>`, `&` are 1).
5. **Containers:** `[]`/`{}` empty → 2; arrays `[` + items joined by `", "` + `]`; objects `{` + `"key": value` pairs
   joined by `", "` + `}`, in the object's insertion order (duplicate keys already collapsed last-wins at their first
   position by `Decode`).
6. **Call-site rules:** list items `{}` 2, `[]` 2, `""` 2, `0` 1, `-0.0` 4, `false` 5, `null` 4, `"raw"` 5,
   `{"type":"IMAGE"}` 17 (the image test is case-sensitive), `{"type":"image"}` counts 2000 (not measured).
   Non-list, non-str inner: `{}` 2, `0` 1, `false` 5, `true` 4, `1.0` 3, **`null` 0**. tool_use input: any falsy
   value (`{}`, `[]`, `""`, `0`, `-0.0`, `0.0`, `false`, `null`) → `json.dumps("")` → **2**.

## Invariants

1. `DumpsLen(v) == len(Dumps(v))` for every `v` (shared code; test-enforced).
2. No allocation of the full output is required (counting encoder), but the count must equal the bytes `Dumps` would
   write.
3. Go `encoding/json` is never used for measurement (it escapes HTML, writes `1e+16` differently, rejects NaN and
   reorders map keys).
4. Encoder failure is possible on **accumulated** values (unlike freshly decoded ones): ints past the 4,300-digit
   decode limit can arise from summed totals in a cache. `DumpsLen`'s signature gains the error return
   (`DumpsLen(v Value, budget int) (int, error)`): it returns typed `ErrValue` exactly where CPython's `json.dumps` raises
   `ValueError` on such ints (signature amended, ADV-P3-D12). At the composition sites the legacy equivalent
   propagates to the top-level handler → the whole line degrades; in the cache writer the same encoder failure
   reproduces legacy's no-write (swallowed error, partial temp file, BC-5.02.006). Recursion economy
   (measured per site, ADV-P4-D17 as corrected by ADV-P5-D08/D17, re-measured end to end pass-5 sweep C):
   CPython's encoder spends ONE slot per container nesting level and one per Python frame at every legacy
   encode site — measured law: maximum encodable total object nesting = `994 − s` for `json.dumps` (`s` =
   Python frames on the stack at the encode call, invoking frame inclusive, `<module>` = 1), `995 − s` for
   `json.dump`, slope 1 slot/frame verified over five stacked frames (`python3 -I`, CPython 3.11.7,
   isolated temp dir/HOME, 2026-11-18). Composition sites: SL:1140 and SL:1147 sit at `s = 3` (budget
   **991**), the SL:1138 genexp adds a frame (`s = 4`, budget **990**). At each site `DumpsLen` takes
   `budget` and returns `ErrDepth` past it; a depth failure at a composition site propagates like the
   `ValueError` leg (whole line degrades). The composition budget (991) is strictly below the stdin
   decoder's acceptance constant (993, BC-5.02.003 PC-7), but the transcript-line decoder caps every
   input-borne Value below it: the tool_use input (SL:1147) decodes at most to value depth 989 (line bound
   993 minus the 4-container wrapper) and a tool_result item (SL:1138) to 988 — both under budget, so no
   input-borne Value both decodes and fails measurement (supersedes the earlier "can decode and still fail"
   consequence); the ErrDepth leg is exercised at the helper level (VP-024 fuzz), and legacy's observable
   line-degrade via composition depth does not occur. A shallower stack never has the smaller budget
   (budget strictly monotone decreasing in frame depth on both sides).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | tool_use input `-0.0` vs `{"x":-0.0}` | 2 (falsy → `""`) vs 11 (truthy container) |
| EC-002 | String containing U+2028 / U+2029 (LINE SEPARATOR / PARAGRAPH SEPARATOR, in escapes `\u2028` / `\u2029`) | each escape is 6 characters (escaped as ≥ U+007F) |
| EC-003 | `{"t":"\\\/\""}` source (`\\`, `\/`, `\"` escapes) | 14: `\/` decodes to `/` (written as 1 char); `\\` and `\"` re-escape to 2 each |
| EC-004 | Raw U+1F600 vs JSON surrogate-pair escape for it | both 21 in `{"t":…}` (one astral char → 12) |
| EC-005 | Two raw CESU-encoded surrogate bytes (kept as two lone surrogates by `Decode`) | 12 (two `\udXXX` escapes) — same count as the combined character |
| EC-006 | Float `123456789.123456789` | repr `123456789.12345679` (shortest round-trip) |
| EC-007 | tool_result list with an image dict, a text dict and a string | `2000 + 30 + 5 = 2035` |
| EC-008 | tool_result dict `{"k":"\u00e9"}` | 15 (wire `{"k": "\u00e9"}`) |

## Canonical Test Vectors

| Input (Value, shown as JSON source) | Expected `DumpsLen` | Category |
|-------|----------------|----------|
| `{"command":"ls"}` | 17 (`{"command": "ls"}`) | happy-path |
| `{"type":"text","text":"hi"}` | 30 | happy-path |
| `{"a":"\u00e9"}` | 15 (wire `{"a": "\u00e9"}`) | edge-case |
| `"\ud83d\ude00"` (string of one astral char) | 14 (wire `"\ud83d\ude00"`, the escaped surrogate pair; escape notation per BC-5.02.001 PC-4) | edge-case |
| `{"x":1.0}`; `{"x":1e+16}`; `{"x":1e-05}`; `{"x":-0.0}` | 10; 12; 12; 11 | edge-case |
| `{"x":12345678901234567890}` | 27 (exact big int) | edge-case |
| `{"x":Infinity}`; `{"x":NaN}` | 15; 10 | edge-case |
| `{"t":"<&>"}`; `{"t":"\u007f"}` | 12; 15 | edge-case |
| tool_result inner `null` (SL:1140) | 0 | edge-case |
| tool_use input `{}` / `null` / `0` (SL:1147) | 2 | error (falsy fallback) |

Rows verified 2026-11-15 against CPython 3.11.7 (`len(json.dumps(...))`); the full 63-case table is BC-5.02.002.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-024 | `DumpsLen(v) == len(Dumps(v))` for random Values | Go property test (testing/quick) |
| VP-024 | `DumpsLen(Decode(b))` equals the oracle `len(json.dumps(json.loads(b)))` on fuzzed inputs | fuzz (`DumpsLen` target) + oracle |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/json.go` (design §2.6); call sites in `internal/statusline` transcript composition (BC-COMPONENT-MAP: internal/pyfmt/json.go (dumps length rules) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1120-1149; measurement at SL:1137-1138, 1140, 1147) |
| Legacy contract | BC-SL-071 (new in P3r1 with BC-SL-038 refinement; oracle P3r2 §A5; index P3r4 §7.3) |
| Decisions | OD-103 (one `internal/pyfmt`); design IM-03, IM-04; pitfalls PR-07, PR-08, PR-10 |

## Related BCs (Recommended)

- BC-5.02.002 — verified by (63-case oracle)
- BC-1.03.009 — consumed by (composition per block from `json.dumps` lengths)
- BC-1.03.014 — related to (text/thinking value types use `Len`, not `DumpsLen`)
- BC-5.02.003, BC-5.02.004 — depends on (decoded Value model)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-json` — internal/pyfmt/json.go (dumps length rules) (JSON encode/measure) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt json (design step S1)

## VP Anchors (Recommended)

- VP-024 — `DumpsLen == len(Dumps)`

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1120-1149) |
| **Confidence** | high (pinned lengths re-run 2026-11-15; design §8 conf H) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if inner is not None else 0` (SL:1140); `or ""` (SL:1147); image test (SL:1137)
- **assertion**: pinned runs (P3r1, P3r2 §A5; re-run 2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | pure; safe |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed -- suitable for property testing and fuzzing against the oracle.
