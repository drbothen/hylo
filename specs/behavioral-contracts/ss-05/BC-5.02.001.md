---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T21:45:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "315bc06"
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
  - "patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165), 2026-11-17T21:45:00Z"
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
1147). `pyfmt.DumpsLen(v Value) int` returns exactly `len(json.dumps(v))` for any decoded `Value`, using Python's
defaults (separators `", "`/`": "`, `ensure_ascii`, float `repr`, NaN tokens, insertion order), and the call sites
apply legacy's per-site fallbacks, including "a `null` non-list inner value counts 0". `DumpsLen` shares its
escaping and float-repr code with the cache encoder `Dumps` (IM-03) so the two cannot drift.

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
4. A value that `Decode` accepted never fails here: ints over 4,300 digits are rejected at decode time (PR-10), and
   the encoder's depth budget is the same as the decoder's, so a sub-value of an accepted line is always encodable.

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
| EC-008 | tool_result dict `{"k":"é"}` | 15 |

## Canonical Test Vectors

| Input (Value, shown as JSON source) | Expected `DumpsLen` | Category |
|-------|----------------|----------|
| `{"command":"ls"}` | 17 (`{"command": "ls"}`) | happy-path |
| `{"type":"text","text":"hi"}` | 30 | happy-path |
| `{"a":"é"}` | 15 (`{"a": "é"}`) | edge-case |
| `"😀"` | 14 (`"😀"`, escaped-surrogate notation per BC-5.01.002) | edge-case |
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
