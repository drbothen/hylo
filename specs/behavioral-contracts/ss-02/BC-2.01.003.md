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
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "51f00c6"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; defaults taken from legacy/dgx_statusline.py SL:127-134)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
parity_class: "n.a."
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

# Behavioral Contract BC-2.01.003: statusline.theme.* keys for SGR palette, pill codes and separator, legacy defaults

> Notation: `\e` is the byte 0x1B (ESC). Byte strings are exact.

## Description

The SGR palette, the three lane-pill codes and the separator that legacy hard-codes
(SL:127-134) become `statusline.theme.*` config keys (OD-113; D15 names colors explicitly).
Each SGR key holds an SGR parameter list; the renderer emits `\e[` + value + `m`. With all
defaults the emitted bytes are identical to legacy's literals, so the keys change no output
during parity.

## Preconditions

1. Resolution per BC-2.01.001.

## Postconditions

1. The registry contains these keys with these defaults (env name = `EnvName(key)`):

   | Key | Default value | Rendered default bytes | Legacy source |
   |-----|---------------|------------------------|---------------|
   | `statusline.theme.reset` | `0` | `\e[0m` | SL:127 `RESET` |
   | `statusline.theme.dim` | `2` | `\e[2m` | SL:127 `DIM` |
   | `statusline.theme.bold` | `1` | `\e[1m` | SL:127 `BOLD` |
   | `statusline.theme.white` | `97` | `\e[97m` | SL:131-132 `WHITE` |
   | `statusline.theme.cyan` | `36` | `\e[36m` | SL:131-132 `CYAN` |
   | `statusline.theme.green` | `32` | `\e[32m` | SL:131-132 `GREEN` |
   | `statusline.theme.yellow` | `33` | `\e[33m` | SL:131-132 `YELLOW` |
   | `statusline.theme.red` | `31` | `\e[31m` | SL:131-132 `RED` |
   | `statusline.theme.grey` | `90` | `\e[90m` | SL:131-132 `GREY` |
   | `statusline.theme.magenta` | `35` | `\e[35m` | SL:133 `MAGENTA` |
   | `statusline.theme.boldred` | `1;91` | `\e[1;91m` | SL:134 `BOLDRED` |
   | `statusline.theme.pill_local` | `106;30;1` | `\e[106;30;1m` | SL:130 `PILL_DGX` (local lane) |
   | `statusline.theme.pill_cloud` | `105;30;1` | `\e[105;30;1m` | SL:130 `PILL_ANTH` (cloud lane) |
   | `statusline.theme.pill_unknown` | `100;37;1` | `\e[100;37;1m` | SL:130 `PILL_NONE` (lane unknown) |
   | `statusline.theme.separator` | ` · ` (space, U+00B7, space) | `\e[2m · \e[0m` (composed `dim + separator + reset`) | SL:128 `SEP` |

2. An SGR key's value must match `^[0-9]{1,3}(;[0-9]{1,3})*$`; otherwise `Load` returns
   `<key>=<value> (not an SGR parameter list)` (rendered per BC-2.02.001). The empty string
   is invalid (legacy has no empty SGR; `\e[m` differs from `\e[0m` by bytes). Per OD-134,
   this is the theme class: a named config-error class extending OD-114's register (which
   fixed four classes and left theme open, PRD OQ-6), with the reason string above in the
   error-taxonomy Reason Vocabulary.
3. `statusline.theme.separator` is free text, but any byte 0x00-0x1F or 0x7F yields
   `<key>=<value> (control character)` (it would break the one-line output). The separator
   is always composed as `dim + separator + reset` using the configured `dim` and `reset`.
4. Widgets read these values from config only; no SGR literal for these roles remains in
   widget logic (D15).
5. Out of scope for this BC: the heat HSV (`statusline.theme.heat`, T-030), sparkline RGBs
   (`statusline.sparkline.colors`, T-046), glyphs (`statusline.glyphs.*`, OD-02), and the
   built-in grey pair of the degraded / config-error / unknown-flag lines, which stays a named
   constant (BC-2.02.001 invariant 2).

## Invariants

1. All defaults ⇒ every rendered byte equals legacy (parity unaffected; covered by the S1
   goldens).
2. Theme values never contain ESC or `m`: the key holds parameters only; the renderer adds
   the `\e[` prefix and `m` suffix.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `HYLO_STATUSLINE_THEME_GREY=38;5;244` | valid; GREY renders `\e[38;5;244m` |
| EC-002 | `HYLO_STATUSLINE_THEME_RED=$'\e[31m'` | error `not an SGR parameter list` (value escaped `\x1b[31m` in the line) |
| EC-003 | `HYLO_STATUSLINE_THEME_RED=` | error `not an SGR parameter list` |
| EC-004 | `HYLO_STATUSLINE_THEME_SEPARATOR=" / "` | valid; separator renders `\e[2m / \e[0m` |
| EC-005 | `HYLO_STATUSLINE_THEME_BOLD=1000` | error (four digits) |
| EC-006 | `HYLO_STATUSLINE_THEME_SEPARATOR=$'\t'` | error `control character` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| env `{}` | `Theme.Separator()` = `\e[2m · \e[0m` (bytes `1b 5b 32 6d 20 c2 b7 20 1b 5b 30 6d`); `Theme.PillLocal()` = `\e[106;30;1m` | happy-path |
| env `{HYLO_STATUSLINE_THEME_PILL_LOCAL: "46;30;1"}` | local-lane pill renders `\e[46;30;1m` | edge-case |
| env `{HYLO_STATUSLINE_THEME_CYAN: "cyan"}` | statusline stdout `\e[90mhylo: config error: statusline.theme.cyan=cyan (not an SGR parameter list)\e[0m\n`, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-015, VP-016 (theme/SGR class) | Default theme bytes equal the legacy literals SL:127-134 (golden table) | table test |
| VP-015, VP-016 (theme/SGR class) | Any accepted SGR value renders without ESC inside the parameter span | proptest |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-113 (theme keys, legacy defaults), D15 (colors are config), tension T9; OD-134 (theme validation is the named "not an SGR parameter list" config-error class, amending OD-114's class register); defaults from legacy/dgx_statusline.py:module primitives (SL:127-134) |
| Parity / exclusion | n.a. (defaults are byte-identical) |
| L2 Capability | CAP-015 (supports CAP-009) |
| L2 Domain Invariants | DI-010 |
| Architecture Module | `internal/config/statusline_keys.go`, `internal/statusline/theme.go` (BC-COMPONENT-MAP: internal/config/statusline_keys.go (theme keys, SGR class) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.01.004 — depends on (registry entries with rationale "legacy literal SL:127-134, OD-113")
- BC-2.02.001 — composes with (error rendering; built-in grey pair not themed)
- BC-1.02.001 — consumer (lane pills)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#theme` — internal/config/statusline_keys.go (theme keys, SGR class) (theme keys) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — theme keys

## VP Anchors (Recommended)

- VP-015, VP-016 — default theme bytes equal legacy

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | Send + Sync (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/statusline_keys.go (theme keys, SGR class) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
