---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - ../owner-decisions-log-2026-11-14.md
  - ../../semport/hylo-legacy/statusline-target-design.md
  - ../../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - ../../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; legacy float()/int() parse at legacy/dgx_statusline.py SL:74-75)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
parity_class: D4-EX-3
confidence: "—"
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

# Behavioral Contract BC-2.02.003: Number-grammar class: underscore and Unicode-digit numerals are config errors

## Description

Numeric config values are parsed with the Python `float()` / `int()` grammar (`pyfmt`,
OD-103) **narrowed** by OD-114: a numeral containing `_` or any non-ASCII decimal digit is a
config error, as is anything the Python grammar itself rejects. Legacy accepted `"4_0"` (=40),
`"٤"` (=4) and `"2_0"` (=20) silently, and crashed at import on `""`, `"four"`, `"0x4"`,
`"2.0"` (for ints); hylo renders the config-error line for all of them — approved deviation
**D4-EX-3** (number class).

## Preconditions

1. A registry key of type `Seconds`, `Float` or `Int` whose `EnvName` is present.

## Postconditions

Checks run in this order; the first failing one produces the error (rendered per
BC-2.02.001):

1. The value contains `_` (U+005F) anywhere → `<key>=<value> (underscore in numeral)`.
2. The value contains a code point of Unicode category Nd other than ASCII `0`-`9` (e.g.
   U+0664 `٤`, U+FF14 `４`) → `<key>=<value> (non-ASCII digit)`.
3. `Seconds`/`Float`: `pyfmt.ParseFloat` (Python 3.11 `float()` grammar, BC-5.01.002) fails
   → `<key>=<value> (not a number)`. Accepted forms keep Python semantics: surrounding
   whitespace, leading `+`/`-`, exponent (`1e1`), `nan`/`inf`/`infinity` spellings (then
   rejected by range, BC-2.02.002).
4. `Int`: `pyfmt.ParseInt` (Python `int(x)` base-10 grammar) fails →
   `<key>=<value> (not an integer)` (e.g. `2.0`, `1e1`, `nan`, `""`, `0x2`). A result
   outside int64 → `<key>=<value> (out of range)`.
5. Otherwise the parsed number goes to the range check (BC-2.02.002 for `Seconds`; the key's
   registry range for `Int`/`Float`). `statusline.rows` (legacy `DGX_SL_ROWS`, SL:75) has
   range "any int64" in P1, preserving legacy semantics for negative and large values
   (`rows >= 2` / `> 2`, SL:1217, SL:1224).

## Invariants

1. Any value legacy parsed successfully and that contains neither `_` nor a non-ASCII digit
   yields the same number in hylo (parity for in-domain values).
2. Grammar errors precede range errors.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=4_0` (legacy: 40) | `underscore in numeral` |
| EC-002 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=٤` (legacy: 4) | `non-ASCII digit` (value shown verbatim as `٤`) |
| EC-003 | `HYLO_STATUSLINE_ROWS=2_0` (legacy: 20) | `underscore in numeral` |
| EC-004 | `HYLO_STATUSLINE_ROWS=٢` | `non-ASCII digit` |
| EC-005 | `HYLO_STATUSLINE_ROWS=2.0` (legacy CP-X02 crash) | `not an integer` |
| EC-006 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=0x4` (legacy CP-X01 crash) | `not a number` |
| EC-007 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=٤_0` | `underscore in numeral` (check 1 first) |
| EC-008 | `HYLO_STATUSLINE_ROWS=" +2 "` | valid, 2 |
| EC-009 | `HYLO_STATUSLINE_ROWS=-1` | valid (one row; legacy-identical) |
| EC-010 | `HYLO_STATUSLINE_ROWS=99999999999999999999` | `out of range` |

## Canonical Test Vectors

`\e` = 0x1B. Error rows: exit 0, no cache writes.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=1e1` | ttl 10; normal render | happy-path |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=4_0` | `\e[90mhylo: config error: statusline.telemetry.ttl_s=4_0 (underscore in numeral)\e[0m\n` | error |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=٤` | `\e[90mhylo: config error: statusline.telemetry.ttl_s=٤ (non-ASCII digit)\e[0m\n` (value bytes `d9 a4`) | error |
| `HYLO_STATUSLINE_ROWS=2.0` | `\e[90mhylo: config error: statusline.rows=2.0 (not an integer)\e[0m\n` | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-016, VP-012 (frontmatter closure) | For ASCII-only, underscore-free strings, hylo's parse result equals CPython 3.11 `float()`/`int()` (oracle table) | table test vs CPython goldens + fuzz |
| VP-016, VP-012 (frontmatter closure) | No string containing `_` or a non-ASCII Nd digit is accepted | proptest |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-114 (T10: `4_0`-style underscores and Unicode digits are config errors), OD-102, OD-103 (pyfmt grammar), PR-18; legacy behavior replaced: legacy/dgx_statusline.py:module tunables (SL:74 `float(DGX_SL_TTL)`, SL:75 `int(DGX_SL_ROWS)`); legacy contract notes BC-SL-087, CP-X01/CP-X02 (pass-3 r1) |
| Parity / exclusion | **Approved deviation D4-EX-3 (number class).** Named exclusion entry id `D4-EX-3`, one case per value (`4_0`, `٤`, `2_0`, `٢`, and the legacy crash inputs `""`, `four`, `0x4`, `2.0`), each with its expected output file; dedicated table test `TestConfigError_D4EX3_Number` (OD-105, OD-110) |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-008, DI-010 |
| Architecture Module | `internal/config/types.go`; `internal/pyfmt/num.go` (BC-COMPONENT-MAP: internal/config/errors.go (number-grammar class) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.01.002 — depends on (Python grammar parse)
- BC-2.02.002 — composes with (range check follows)
- BC-2.02.001 — composes with (line format)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#numbers` — internal/config/errors.go (number-grammar class) (numeric types) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — D4-EX-3 table tests

## VP Anchors (Recommended)

- VP-016, VP-012 — in-domain values parse as CPython

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | Send + Sync (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/errors.go (number-grammar class) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
