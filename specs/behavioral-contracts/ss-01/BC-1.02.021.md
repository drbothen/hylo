---
document_type: behavioral-contract
level: L3
version: "1.5"
status: draft
producer: product-owner
timestamp: 2026-11-17T23:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "a99539e"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-058"
parity_class: byte-exact
confidence: M
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.3 pass-4 remediation (ADV-P4-B03): Str-vs-str fuzz leg re-anchored to VP-041; 2026-11-17T12:00:00Z"
  - "1.5 pass-6 remediation (ADV-P6-B16): history label version-prefixed; no behavioral change; 2026-11-19T04:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.021: Model label str() of a non-str value

> Byte notation used below: `\e` = ESC (0x1B). All other characters are literal UTF-8.

## Description

The model label is `model.display_name or model.id or "?"` (BC-1.02.002), wrapped in WHITE. When the selected value
is truthy but not a string, legacy renders it with Python `str()`, which for numbers, booleans, lists and objects is
Python's `repr` spelling (`1e+16`, `True`, `[1, 'a']`, `{'k': 1.0}`), not JSON. The port reproduces that spelling
through `pyfmt.Str`.

## Preconditions

1. stdin `model` is an object (or absent → `{}`).
2. `v = display_name or id or "?"` under Python truthiness: `None`, `false`, `0`, `0.0`, `-0.0`, `""`, `[]`, `{}`
   fall through to the next candidate.
3. Default theme (OD-113): WHITE `\e[97m`, RESET `\e[0m`.

## Postconditions

1. The label segment is `\e[97m` + `Str(v)` + `\e[0m`.
2. `Str(v)`: a string is unchanged; any other value is Python `repr`:
   - int: exact decimal of the arbitrary-precision integer (no float conversion);
   - float: Python float `repr` (shortest round-trip; exponent form `1e+16`, `1e-05`, `1.5e+300`; `nan`, `inf`; `3.0`);
   - bool: `True` / `False` (only `True` can be selected, `False` is falsy);
   - `null` cannot be selected (falsy);
   - list: `[` + items' `repr` joined by `, ` + `]`; strings inside use Python quoting (single quotes unless the
     string contains `'` and no `"`), with non-printable code points escaped (`'\ud800'`);
   - object: `{` + `repr(key): repr(value)` joined by `, ` + `}` in insertion order.

## Invariants

1. A top-level string containing a lone surrogate is printed as is and fails strict UTF-8 output (CP-S17,
   BC-1.01.008); inside a list or object the surrogate is escaped by `repr` and does not crash.
2. Large integers are never rounded (`12345678901234567890`, `18446744073709551616` stay exact).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `display_name = 1e16` | `1e+16` |
| EC-002 | `display_name = true` | `True` |
| EC-003 | `display_name = [1, "a"]` | `[1, 'a']` |
| EC-004 | `display_name = {"k": 1.0}` | `{'k': 1.0}` |
| EC-005 | `display_name = ["it's"]` | `["it's"]` (double quotes chosen by repr) |
| EC-006 | `display_name = {"a": null, "b": true}` | `{'a': None, 'b': True}` |
| EC-007 | `display_name` = 0, `""`, `false`, `[]`, `-0.0`, `null` | falls through to `id` |
| EC-008 | `display_name = ["\ud800"]` (lone surrogate in a list) | `['\ud800']` (escaped, no crash) |
| EC-009 | `display_name` = `"\ud800"` (top-level lone surrogate) | degraded at output (CP-S17, BC-1.01.008) |
| EC-010 | `display_name` absent, `id = 42` | label `42` **only when the model-prefix list resolves empty** (legacy `LOCAL_MODEL_PREFIXES` unset / hylo `backends[0].model_prefixes` empty, OD-123). Under the default prefix `claude-sonnet` (OD-123), `model_id.startswith(p)` at SL:446 raises AttributeError (`'int' object has no attribute 'startswith'`, verified 2026-11-17) and the refresh degrades (BC-1.01.001) |

## Canonical Test Vectors

stdin `{"model": {"display_name": X, "id": "claude-x"}}`; output is the label segment (second row-1 segment).

| Input X | Expected Output | Category |
|-------|----------------|----------|
| `"Opus 5.5"` | `\e[97mOpus 5.5\e[0m` | happy-path |
| `1e16` | `\e[97m1e+16\e[0m` | edge-case |
| `true` | `\e[97mTrue\e[0m` | edge-case |
| `[1, "a"]` | `\e[97m[1, 'a']\e[0m` | edge-case |
| `{"k": 1.0}` | `\e[97m{'k': 1.0}\e[0m` | edge-case |
| `12345678901234567890` | `\e[97m12345678901234567890\e[0m` | edge-case |
| `NaN` | `\e[97mnan\e[0m` | edge-case |
| `Infinity` | `\e[97minf\e[0m` | edge-case |
| `3.0` | `\e[97m3.0\e[0m` | edge-case |
| `1e-5` | `\e[97m1e-05\e[0m` | edge-case |
| `["it's"]` | `\e[97m["it's"]\e[0m` | edge-case |
| `0` | `\e[97mclaude-x\e[0m` | edge-case (falls through) |
| `"\ud800"` | whole stdout = `\e[90mstatusline degraded\e[0m\n` | error (CP-S17) |

Pinned 2026-11-15 with the legacy `render_lane` under CPython 3.11 (oracle, OD-104), except the CP-S17 row, which is
the deep pass-3 round 1 finding (crash at print, BC-1.01.008).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-041 | `pyfmt.Str(v)` equals CPython `str(v)` for generated JSON values (nested lists/objects, big ints, floats) | fuzz vs oracle (VP-028 retains the bounded golden tables) |
| VP-028 | Falsy values select the next candidate | table test |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/lane.go`; `pyfmt.Str` in `internal/pyfmt` json file; BC-COMPONENT-MAP: internal/statusline/lane.go (str() of non-str) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:442 selection, SL:453 rendering) |
| Legacy contract | BC-SL-058 (deep pass-3 round 1, new) |
| Config keys | `statusline.theme.*` (OD-113) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.002 — refines (fallback chain)
- BC-1.01.008 — related to (strict UTF-8 output, CP-S17)
- BC-5.02.004 — depends on (ordered object Value, WTF-8 strings)
- BC-5.01.001 — depends on (float spelling)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/lane.go (str() of non-str) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-041 — `Str` equals CPython `str` (fuzz); VP-028 — golden label bytes

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane, SL:441-443, 453) |
| **Confidence** | medium (Python `repr` of nested containers and big ints) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: f-string `str()` conversion; no type check on `display_name`

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

The decoded stdin must keep big integers exact and object insertion order (design IM-01) for `Str` to match.
