---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "d877571"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces Python str() of values used at legacy/dgx_statusline.py SL:442, 453; BC-SL-058)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z ADV-P3 remediation D34+D10: dict repr key/value separator stated; subagent str() sites SL:896/908/922 added"
  - "1.2.2 2026-11-18: ADV-P4 remediation D14 - isprintable class pinned to the generated Unicode 14.0.0 tables (OD-170, BC-5.01.002 Pre-3)"
  - "2026-11-19T21:00:00Z (1.2.3): ADV-P8 remediation D20 — PC-6 mints the recursion-limit outcome from the pinned measurement (CPython 3.11.7, limit 1000): decode accepts display_name nesting 989, str() reprs only to 988 in the same stack, so Str returns an error there and the caller prints the degraded line (exit 0); n >= 990 is the decode-side {} fallback; fresh repr budget 997"
  - "2026-11-20T12:00:00Z (1.2.4): ADV-P8 residual sweep — PC-6 corrected: the 1.2.3 measurement was taken through a loader that added stack frames and is WRONG. Orchestrator end-to-end measurement through the real entry (`python3 -I -s legacy/dgx_statusline.py`, isolated HOME): n = 987..991 (document depth up to 993) all render normally with the full repr of the list in the model segment, exit 0, no stderr; n = 992 (document depth 994) fails the stdin decode, d = {}, the model segment shows ?. So no Str recursion outcome is reachable from stdin — Str of any stdin-decodable value succeeds at SL:442/453, and Str must not impose a lower nesting limit than the decode allows; the 989 degraded-line canonical vector is withdrawn"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.02.005: pyfmt.Str: Python str() of values (str unchanged, non-str via repr)

## Description

`pyfmt.Str(v Value) string` (json.go, design IM-05) reproduces Python `str()` of a decoded
value: a str is returned unchanged; anything else goes through Python `repr`, with float
repr from `pyfmt.Repr` (BC-5.01.005). Go's `fmt.Sprint` reorders cases and reformats
floats, so every `str()` site routes through this helper. Helper-level contract per OD-141
(consumer site: the model label str() of a non-str value, SL:442, 453).

## Preconditions

1. `v` is a decoded `Value` (str, int, float, bool, None, list, dict).

## Postconditions

1. str → returned unchanged, byte-identical (WTF-8 preserved, IM-11).
2. True/False/None → `True`, `False`, `None`.
3. int/float → Python repr spelling (BC-5.01.005): `str(1794615009.0)` = `1794615009.0`;
   `str(1e16)` = `1e+16`; non-finite: `nan`/`inf`/`-inf`.
4. list/dict → Python repr of the container: `str([1, "a"])` is `[1, 'a']` — single quotes,
   comma+space separators, and each key is followed by `': '` before its value (dict item separator, ADV-P3-D34). Containers nest. **Element string quoting
   (CPython `repr(str)` rules, CPython 3.11 verified with `python3 -I`):** the element is
   wrapped in single quotes unless it contains `'` and not `"`, in which case it is wrapped
   in double quotes (`Str(["it's"])` is `["it's"]`); if it contains both quote characters it
   is wrapped in single quotes with every `'` escaped as `\'`. Inside the quotes: `\` is
   escaped as `\\`; `\n`, `\r`, `\t` use the two-character shorthands; every other
   non-printable code point (anything false under Python `str.isprintable` — the printable
   class is resolved from hylo's own generated tables pinned to Unicode 14.0.0, OD-170 /
   BC-5.01.002 Pre-3, never from Go's `unicode` package — including
   U+0000-U+001F, U+007F-U+009F and lone surrogates) is escaped as `\xhh` (U+00XX),
   `\uhhhh` (U+XXXX) or `\Uhhhhhhhh` (astral) with lowercase hex digits. Printable
   non-ASCII code points (e.g. é, 言) are written as themselves, not escaped.
5. All cases pure and deterministic; equal to CPython `str(value)` for every decoded value
   shape in the generated table (OD-104 oracle discipline).
6. **Recursion budget (pass-8 D20, CORRECTED in the pass-8 residual sweep; measured END
   TO END through the real entry — `python3 -I -s legacy/dgx_statusline.py`, isolated
   HOME, CPython 3.11.7 — with stdin document
   `{"session_id":"s1","model":{"display_name":[<n>-deep list]},"workspace":{"current_dir":"."}}`.)**
   `Str` bounds container-repr recursion exactly as CPython's repr does, but **no `Str`
   recursion outcome is reachable from stdin** at the SL:442/453 sites: the whole-input
   `json.load(sys.stdin)` decode boundary binds first. Measured: display_name nesting
   n = 987..991 (document depth up to 993) renders NORMALLY — the model segment shows the
   full repr of the list, exit 0, no stderr; n = 992 (document depth 994) fails the stdin
   decode and legacy falls back to `d = {}` (defaults), the model segment showing "?".
   There is no n for which stdin delivers a decodable value `Str` cannot repr: **`Str` of
   any stdin-decodable value succeeds at SL:442/453.** The port must therefore not impose
   a lower nesting limit on `Str` than the decode allows (a higher limit is harmless —
   the decode rejects first). The earlier 1.2.3 reading (a decodable 989-deep value whose
   `str()` raises) was an artifact of a measurement loader that added stack frames.
   Canonical vectors: display_name nested 991 → full repr in the model segment, exit 0;
   display_name nested 992 → "?" via the `d = {}` fallback, exit 0.

## Invariants

1. A str input is never re-quoted: `Str("x")` = `x`, never `'x'` (Python distinction of
   `str` vs `repr` for strings).
2. Container rendering reuses the same scalar repr primitive as Repr (no drift).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `Str("x")` | `x` (unchanged) |
| EC-002 | `Str(True)` | `True` |
| EC-003 | `Str(1e16)` | `1e+16` |
| EC-004 | `Str([1, "a"])` | `[1, 'a']` (repr spelling, single quotes) |
| EC-005 | `Str(NaN)` | `nan` |
| EC-006 | `Str({})` | `{}` (empty dict repr) |
| EC-007 | `Str(None)` | `None` |
| EC-008 | `Str(["it's"])` | `["it's"]` (contains `'`, not `"` → double-quoted element) |
| EC-009 | `Str(["both ' and \""])` | `['both \' and "']` (both quotes → single-quoted, `'` escaped) |
| EC-010 | `Str([chr(0)])`, `Str([chr(0x7F)])` | `['\x00']`, `['\x7f']` (non-printables escaped, lowercase hex) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `Str("x")` | `x` | happy-path |
| `Str(True)` | `True` | happy-path |
| `Str([1, "a"])` | `[1, 'a']` | edge-case |
| `Str(NaN)` | `nan` | edge-case |

Expectations generated from CPython 3.11 (OD-104 oracle discipline).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-024 | `Str` equals CPython `str(value)` for every value shape (nested containers included) | CPython oracle table |
| VP-024 | A str input is returned byte-identical (WTF-8) | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-05; consumers: model label str() site SL:442, 453 (BC-1.02.021) plus the subagent str() sites SL:896 (`name` f-string), SL:908 (`model`), SL:922 (`status` suffix) (ADV-P3-D10) |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| L2 Domain Invariants | DI-012 (byte parity machinery) |
| Architecture Module | `internal/pyfmt` json.go (BC-COMPONENT-MAP: internal/pyfmt/json.go (Str) — ARCH-06) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.01.005 — composes with (Repr for scalars)
- BC-1.02.021 — consumer (model label str() of a non-str value, BC-SL-058)
- BC-5.02.006 — related to (Dumps shares the escaping primitive)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#json` — internal/pyfmt/json.go (Str) (json.go helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

S-TBD — pyfmt json helpers

## VP Anchors (Recommended)

- VP-024 — str() equality table

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/json.go (Str)` (BC-COMPONENT-MAP: py/json.go (Str) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
