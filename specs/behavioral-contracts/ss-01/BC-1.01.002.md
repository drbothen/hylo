---
document_type: behavioral-contract
level: L3
version: "1.2.5"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "a99539e"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-002"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "consolidated pass-2 follow-up: transcript site re-measured end to end at 993/994 — equality with stdin, not 989/990 divergence, 2026-11-17T21:21:12Z"
  - "pass-3 remediation (ADV-P3-B14/B16/B10): 4,300-digit int-literal edge case added; VP table cites VP-005/VP-006 (not VP-001); ARCH-03 anchor normalized to the stable #statusline-guard fragment; 2026-11-18T02:00:00Z"
  - "pass-4 remediation (ADV-P4-B11 + ADV-P4-A2-16 sibling): VP-001 removed from VP Anchors; EC-006 states the L+1 observable explicitly (default line, not the degraded line); 2026-11-18T03:00:00Z"
  - "1.2.5 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) — pass-4 stamp re-dated ascending (it predated pass-3's); no behavioral change"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.01.002: Non-JSON or non-object stdin decodes to an empty object

> Byte notation: `\e` = ESC (0x1B); `\n` = LF.

## Description

The status line decodes stdin once with Python `json.load` text-mode semantics. If decoding fails for any reason,
or the decoded top-level value is not a JSON object, the refresh proceeds with an empty object `{}` and renders the
`?` defaults instead of failing. Type confusion *inside* a valid object is not covered here: it degrades through
the guard (BC-1.01.001).

## Preconditions

1. Configuration resolved without error.
2. stdin holds arbitrary bytes (possibly empty) as delivered by Claude Code.

## Postconditions

1. If stdin parses (strict UTF-8, BC-1.01.008) as a JSON **object**, the decoded ordered object is the render input.
2. Otherwise the render input is `{}`. This covers: empty stdin; whitespace only; malformed JSON; trailing garbage
   after a value; a UTF-8 BOM before `{`; invalid UTF-8 (BC-1.01.008); nesting deeper than the CPython 3.11 limit
   at this call site; an integer literal whose `int`/`str` conversion exceeds CPython 3.11's 4,300-digit limit
   (json raises `ValueError`, caught at SL:1203-1204 — see EC-009); and a valid top-level array, string, number,
   `true`/`false` or `null`.
3. With `{}` the refresh renders the defaults (pill `◨ ?`, model `?`) and exits 0; it never degrades because of the
   decode result alone.
4. Python `json` leniencies are kept when the object parses: `NaN`/`Infinity`/`-Infinity` tokens accepted; duplicate
   keys are last-wins at the first key's position; integers stay exact; leading/trailing whitespace (incl. newlines)
   around the value is accepted (`pyfmt.Decode(ModeText)`, design IM-01, BC-5.02.004).

## Invariants

1. Decoding never raises past this step; the only outcomes are "object" or `{}`.
2. Side effects of the rest of the refresh still run on `{}` (e.g. with ROWS >= 2 the session cache
   `statusline-nosession.json` is written by the metrics step, BC-1.01.009).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Empty stdin (0 bytes) | `{}` |
| EC-002 | `[1,2]`, `"s"`, `42`, `true`, `null` | `{}` |
| EC-003 | UTF-8 BOM `EF BB BF` before `{...}` | `{}` (text-mode `json.load` rejects a BOM) |
| EC-004 | `{"model":{"display_name":"X"}} trailing` | `{}` (extra data) |
| EC-005 | Object whose member `"z"` holds 992 nested arrays (total depth 993) | accepted, renders `X` |
| EC-006 | Same with 993 nested arrays (total depth 994) | `{}` (CPython RecursionError at this call site); renders the 45-byte default line — the L+1 observable is the default line, **not** the degraded line |
| EC-007 | `{"model":{"display_name":"X","display_name":"Y"},"v":NaN}` | parses; model label `Y` |
| EC-008 | `{"model":"x"}` (valid object, wrong inner type) | not this BC: degrades via BC-1.01.001 (CP-S01) |
| EC-009 | an integer literal of 4,301 digits (over CPython 3.11's `sys.int_max_str_digits` = 4300; oracle-verified 2026-11-18: `json.loads` raises `ValueError` "Exceeds the limit (4300 digits)") | `ValueError` caught at SL:1203-1204 → `{}` → the 45-byte default line |

Note on EC-005/006: the stdin depth limit pinned here (993 accepted / 994 rejected) equals the transcript
`json.loads` limit (993 accepted / 994 rejected, BC-5.02.003) — both call sites sit at the same Python
frame depth. The Go decoder must take the depth limit per call site, and each site's value must be measured
end to end, not inferred from the other.
Measured invocation (OD-104/OD-109 oracle, CPython 3.11.7, default recursion limit 1000): a fresh `python3 -I`
process running a module-level `main()` that calls `json.load(sys.stdin)`, stdin piped from a file; depth = top-level
`[` nesting. Re-probed 2026-11-17: 993 accepted, 994 RecursionError. The Tier C harness must invoke the oracle in
this same shape — feed stdin to a fresh process, do not import the module — or the budget can shift by a Python
frame.

## Canonical Test Vectors

Config: defaults with `HYLO_STATUSLINE_ROWS=1`, `HYLO_STATUSLINE_GIT_ENABLED=0`, COLUMNS unset, empty cache dir.
Expected default line (45 bytes): `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97m?\e[0m\n`.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `  \n{"model":{"display_name":"X"}}\n\n` | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97mX\e[0m\n` | happy-path |
| empty stdin | the 45-byte default line, exit 0 | edge-case |
| `[1,2]` | the 45-byte default line, exit 0 | edge-case |
| `EF BB BF` + `{"model":{"id":"x"}}` | the 45-byte default line | edge-case |
| object with 993 nested arrays (EC-006) | the 45-byte default line | edge-case |
| `{"model":{"display_name":"X"}} trailing` | the 45-byte default line | error |
| `{"model":{"display_name":"X"},"n":` + 4,301-digit decimal literal + `}` | the 45-byte default line (EC-009; integers up to 4,300 digits stay exact per PC4) | edge-case |

All rows verified 2026-11-15 on CPython 3.11.7 (`LANG=en_US.UTF-8`, `DGX_SL_ROWS=1`, `DGX_SL_GIT=0`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-005, VP-006 | For all byte strings, decode returns an object or `{}`, never an error to the caller | fuzz |
| VP-005, VP-006 | Go decode result equals CPython `json.load` (text, strict UTF-8) acceptance on the generated corpus | Tier C differential fuzz |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` input decode (`input.go`, design §2.2) (BC-COMPONENT-MAP: internal/statusline/input.go (stdin decode, {} fallback) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`main` (SL:1201-1206) |
| Legacy contract | BC-SL-002 (broad sweep; refined P3r1 §A9; index P3r4 §7.3) |
| Decisions | D4; owner ruling (a) strict stdio (P3r2 §0); OD-104 (CPython 3.11 oracle) |

## Related BCs (Recommended)

- BC-1.01.008 — composes with (invalid UTF-8 is one decode failure class)
- BC-1.01.001 — related to (inner type confusion degrades instead)
- BC-5.02.004 — depends on (ordered object Value)
- BC-5.02.003 — related to (bytes-mode acceptance set for transcripts; different depth limit)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-guard` — internal/statusline/input.go (stdin decode, {} fallback; effect-script step 1) (stdin decode) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — status line frame (design step S2)

## VP Anchors (Recommended)

- VP-005, VP-006 — decode is total (object or `{}`)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1201-1206) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `try: d = json.load(sys.stdin) except Exception: d = {}`; `if not isinstance(d, dict): d = {}`
- **assertion**: pinned runs 2026-11-15 (depth boundary measured this round)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads stdin |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | mixed (read is effectful; decode is pure) |

#### Refactoring Notes

Read stdin fully in the shell, then call the pure `pyfmt.Decode(b, ModeText)` with the stdin depth limit; map any
error or non-object to an empty ordered object.
