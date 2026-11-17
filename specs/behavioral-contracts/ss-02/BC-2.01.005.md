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
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "bc396c7"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; replaces legacy toggles SL:76-77, list split SL:444-445, expanduser SL:78)"
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

# Behavioral Contract BC-2.01.005: HYLO_* value grammars: typed bool, comma lists, ~ path expansion; COLUMNS excluded as protocol input

## Description

Defines how a `HYLO_*` string becomes a typed value for the non-numeric shared types:
booleans accept only `true/false/1/0/yes/no` (OD-05), lists are comma-encoded (OD-74), and
path values expand a leading `~` (OD-61). `COLUMNS` is a Claude Code protocol input read by
the renderer with the Python `int()` grammar (BC-1.01.005), never a config key (ENV-15).
Number grammars are BC-2.02.003; URL is BC-2.02.005; enum is BC-2.02.004.

## Preconditions

1. A registry key of type `Bool`, `List` or `Path` whose `EnvName` is present
   (BC-2.01.001).

## Postconditions

1. **Bool:** the value, compared byte-exact and case-sensitive with no trimming, maps
   `true`, `1`, `yes` → true and `false`, `0`, `no` → false. Any other value (including
   `""`, `TRUE`, `on`, ` 1`) yields `<key>=<value> (not a boolean (true|false|1|0|yes|no))`.
   P1 bool keys: `statusline.sparkline.enabled` (legacy `DGX_SL_SPARK`, SL:76),
   `statusline.git.enabled` (legacy `DGX_SL_GIT`, SL:77). Legacy treated every value except
   `"0"` as on; values legacy accepted that are outside this grammar are D4-EX-3 boolean-class
   cases (BC-2.02.001, test `TestConfigError_D4EX3_Boolean`).
2. **List:** the value is split on `,`; each item is stripped with Python `str.strip()`
   semantics (`pyfmt.Strip`, OD-103); empty items are dropped; order and duplicates are kept.
   `""` → empty list (valid). This reproduces legacy SL:444-445 for
   `backends[0].model_prefixes`. Items are not otherwise validated in P1.
3. **Path:** a value equal to `~`, or starting with `~/` (or `~\` on Windows), has that `~`
   replaced by the user home directory (`HOME` on macOS/Linux, `USERPROFILE` on Windows);
   `~user` forms are left literal; other values are used as given. `""` yields
   `<key>= (empty path)`; a needed but unknown home yields
   `<key>=<value> (home directory unknown)`. P1 path key: `paths.cache_dir` (OD-101 default
   from `internal/platform`, BC-3.01.001). The same rule applies to every path value
   (OD-61), including `HYLO_CONFIG` (BC-2.03.002).
4. **COLUMNS:** no registry key reads or shadows `COLUMNS`; `HYLO_COLUMNS` is not a key
   (an unknown-setting warning if set). The renderer reads `COLUMNS` per BC-1.01.005.

## Invariants

1. Parsing is pure: same string → same typed value or the same error.
2. Error strings come from the BC-2.02.001 reason vocabulary.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `HYLO_STATUSLINE_GIT_ENABLED=yes` | true |
| EC-002 | `HYLO_STATUSLINE_GIT_ENABLED=Yes` | error `not a boolean (...)` |
| EC-003 | `HYLO_STATUSLINE_SPARKLINE_ENABLED=` | error `not a boolean (...)` |
| EC-004 | `HYLO_BACKENDS_0_MODEL_PREFIXES=",,"` | `[]` |
| EC-005 | `HYLO_BACKENDS_0_MODEL_PREFIXES="a,a"` | `["a","a"]` |
| EC-006 | `HYLO_PATHS_CACHE_DIR=~/c` with `HOME=/home/user` | `/home/user/c` |
| EC-007 | `HYLO_PATHS_CACHE_DIR=~other/c` | `~other/c` (literal) |
| EC-008 | `HYLO_PATHS_CACHE_DIR=~/c`, `HOME` unset (Unix) | error `home directory unknown` |
| EC-009 | `COLUMNS=" 80 "` | not a config input; renderer gives 80 (BC-1.01.005) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `HYLO_STATUSLINE_SPARKLINE_ENABLED=0` | sparkline disabled | happy-path |
| `HYLO_BACKENDS_0_MODEL_PREFIXES=" claude-sonnet ,claude-haiku "` | `["claude-sonnet","claude-haiku"]` | edge-case |
| `HYLO_STATUSLINE_GIT_ENABLED=2` (legacy: on) | statusline stdout `\e[90mhylo: config error: statusline.git.enabled=2 (not a boolean (true\|false\|1\|0\|yes\|no))\e[0m\n` (`\e` = 0x1B), exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-015 | Bool parse accepts exactly six strings | table test (exhaustive over the six plus a fuzz corpus) |
| VP-015 | List parse equals Python `[p.strip() for p in s.split(",") if p.strip()]` on the CPython-generated table | table test against oracle goldens |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-05 (typed booleans), OD-74 (comma-list encoding in env), OD-61 (expand `~` in every path), OD-59 (typed + validated); replaces legacy/dgx_statusline.py:module tunables (SL:76-77 `!= "0"`, SL:78 `expanduser`), render_lane (SL:444-445), term_cols (SL:1185-1190, kept as protocol input) |
| Parity / exclusion | boolean values legacy accepted outside the grammar → D4-EX-3 (boolean class), exclusion entry `D4-EX-3`, test `TestConfigError_D4EX3_Boolean` (OD-102, OD-105) |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-010 |
| Architecture Module | `internal/config/types.go` (BC-COMPONENT-MAP: internal/config/types.go (value grammars) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.01.001 — consumer
- BC-2.02.001 — composes with (error rendering)
- BC-1.01.005 — related to (COLUMNS grammar)
- BC-5.03.002 — depends on (pyfmt Strip, Python whitespace semantics)
- BC-3.01.001 — related to (cache dir default)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#types` — internal/config/types.go (value grammars) (typed value grammars) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — config subset

## VP Anchors (Recommended)

- VP-015 — bool grammar exact

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | Send + Sync (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/types.go (value grammars) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
