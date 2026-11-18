---
document_type: behavioral-contract
level: L3
version: "1.2.5"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "9c2a9e3"
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
modified: ["1.2.2 2026-11-18: ADV-P3 remediation D07 — P1 Bool set completed with queue.yellow and subagent.enabled", "2026-11-18T22:00:00Z (1.2.3) ADV-P4 remediation D19+D26 — composite strict-JSON env grammar (PC-5) and OD-173 label-Text validation (PC-6) added; queue.yellow priority citation corrected to OD-175", "2026-11-19T00:40:00Z (1.2.4) ADV-P5 remediation D05+D06+D07+D12+D13 — PC-5 shapes written per key and matched to defaults (colors object spelling supersedes the positional triple-array; IntMap exact-keys/JSON-integer/int64/duplicate rules; scale is a 4-number array); PC-6 Text reasons minted for glyph and general Text keys; PC-7 default-only rule (byte-equal accepted, else out of range, OD-162); FloatPair example corrected to the registered [0.5,0.9] range (D12)", "2026-11-19T02:00:00Z (1.2.5) ADV-P5 remediation A03 correction — sparkline.colors fade elements renamed [lo, hi] → [base, span] and law restated as base + span·i/max(n-2, 1) per legacy SL:683 (a base and a span, not a range)"]
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
   `statusline.git.enabled` (legacy `DGX_SL_GIT`, SL:77),
   `statusline.queue.yellow` (P1 per OD-175, ADV-P3-D07) and
   `statusline.subagent.enabled` (OD-155; default true). Legacy treated every value except
   `"0"` as on; values legacy accepted that are outside this grammar are D4-EX-3 boolean-class
   cases (BC-2.02.001, test `TestD4EX3_Boolean`).
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
   (OD-61), including `HYLO_CONFIG` (BC-2.03.002) — except that an empty `HYLO_CONFIG` is
   treated as unset and falls through to the per-OS default rather than raising the
   empty-path error (resolution semantics of BC-2.03.002 PC-2b/EC-007, ADV-P1-D25).
4. **COLUMNS:** no registry key reads or shadows `COLUMNS`; `HYLO_COLUMNS` is not a key
   (an unknown-setting warning if set). The renderer reads `COLUMNS` per BC-1.01.005.
5. **Composite numeric types (ADV-P4-D19, orchestrator design call 1; shapes written
   out per key and matched to their defaults, ADV-P5-D06/D07/D13 / owner call 3):** a
   key whose registry type is composite — `FloatPair` (Float pair), `FloatTriple`
   (Float triple), `IntMap` (Int map), `RGBTriplesFloat` (RGB triples + Float) or
   `NumberList` (any list of numbers) — takes its env value as **strict JSON** of the
   declared shape. A value that is not valid JSON of the declared shape yields
   `<key>=<value> (expected JSON <shape>)`, where `<shape>` spells the key's declared
   shape (per-key, from the registry):
   - `array of 2 numbers` (FloatPair). Elements are named per key:
     `statusline.cost.percentiles` = `[p75, p95]`, ASCENDING (`p75 <= p95` ratified,
     pass-3 C2-07); `statusline.limits.projected_bands` = `[yellow, red]` (yellow when
     `proj >= yellow`, red when `proj > red`; legacy default `[80, 100]`, SL:519);
     `statusline.limits.absolute_bands` = `[yellow, red]` (yellow when `pct > yellow`,
     red when `pct > red`; legacy default `[70, 90]`, SL:521). No ordering constraint is
     ratified for the bands pairs — legacy's chained red-first comparison is
     comparison-total for any finite pair.
   - `array of 3 numbers` (FloatTriple; `statusline.theme.heat`, default-only).
   - `array of 4 numbers` (`statusline.sparkline.scale` = `[k_top, v_floor, f_floor,
     other]`; legacy default `[1.0, 1.0, 0.1, 1e-9]` from `_SPARK_FIXED`/`_SPARK_FLOOR`
     SL:648-649 and the 1e-9 fallback SL:671; each member finite `> 0`).
   - `object {trail,fade,amber,head}` (RGBTriplesFloat;
     `statusline.sparkline.colors`: trail/amber/head each an array of 3 integers, fade
     an array of 2 numbers `[base, span]`, the trail fade factor
     `base + span·i/max(n-2, 1)` (pass-5 A03 corrected against legacy SL:683
     `fade = 0.55 + 0.45 * i / max(len(pts) - 2, 1)`: the two numbers are a base and a
     span, not a range); legacy default trail `[70,170,190]`, fade `[0.55,0.45]`,
     amber `[220,170,60]`, head `[140,235,255]`, SL:682-690). This object spelling
     supersedes the former positional `array of 3 arrays of 3 numbers plus 1 number`
     (ADV-P5-D06).
   - `object {cc,other} of integers` (IntMap, e.g.
     `HYLO_STATUSLINE_COST_RATE_MIN_API_MS='{"cc":1,"other":2}'`): the object has
     exactly the keys `cc` and `other` — a missing key or an extra key is a shape
     error; each value is a JSON integer (no fraction, no exponent — `1.0` and `1e3`
     are shape errors), within int64 (past int64 is a shape error); duplicate keys in
     the JSON text are rejected (shape error) (ADV-P5-D13).
   - `array of numbers` (NumberList).
   Strict JSON only (no `NaN`/`Infinity` tokens, no trailing data). Range checks
   (registry `Range`) apply **after** the shape check, member-wise. Shape errors belong
   to the Text class (OD-178).
6. **Text keys (OD-173, ADV-P4-B16; runtime reasons minted ADV-P5-D05/OD-178):**
   - The lane-pill label keys `statusline.pill.label_local`, `label_cloud` and
     `label_unknown` (display width 1..16, judgment call keeping the pill short): a
     violating value yields
     `<key>=<value> (expected non-empty control-free text of display width 1..16)`.
   - The glyph-family keys (`statusline.glyphs.*`, `statusline.subagent.glyphs.*`):
     a value that is not non-empty control-free text of exactly 1 code point and 1
     display column (OD-170 width function, BC-2.01.004 PC-9) yields
     `<key>=<value> (expected exactly 1 code point and 1 display column)`.
   - Every other `Text` key with the non-empty/no-control-bytes range
     (`statusline.subagent.tokens.suffix`, `statusline.window_age.process_name`,
     `statusline.labels.input`, ...): a violating value yields
     `<key>=<value> (expected non-empty control-free text)`.
   All three reason strings ride the Text class (OD-178) on the E-CFG-001 surface.

7. **Default-only keys (ADV-P5-D07 / owner call 3, OD-162):** for a key the registry
   marks default-only — the composite `statusline.theme.heat` and the `Text`/`List`
   keys `statusline.units.context`, `statusline.units.lines`, `statusline.units.tokens`
   and `statusline.limits.windows` — an env value byte-equal to the default's env
   spelling is accepted; any other value runs the key's own grammar first (a parse or
   shape failure is that type's error), and a value that parses but differs from the
   default is a config error on the E-CFG-001 surface riding the number-range class,
   reason `out of range` (OD-162: the key's valid range is its default value only;
   the number-range class is the OD-162-designated class even for Text/List
   default-only keys). It is definite: `HYLO_STATUSLINE_THEME_HEAT` at any non-default
   value is a config error, never a warning and never silence. (The former PC-5 claim
   that default-only keys "never read their env name" is superseded; the former
   listing of `statusline.units.context` as composite is corrected — it is `Text`.)

## Invariants

1. Parsing is pure: same string → same typed value or the same error.
2. Error strings come from the BC-2.02.001 reason vocabulary (including the Text-class
   strings of PC 6 and the composite shape string of PC 5).

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
| EC-010 | `HYLO_STATUSLINE_THEME_HEAT='0.22/0.85/0.80'` (default spelling) | accepted, no error (PC 7) |
| EC-011 | `HYLO_STATUSLINE_THEME_HEAT='0.5/0.5/0.5'` | `\e[90mhylo: config error: statusline.theme.heat=0.5/0.5/0.5 (out of range)\e[0m\n` (PC 7, OD-162) |
| EC-012 | `HYLO_STATUSLINE_COST_RATE_MIN_API_MS='{"cc":1.0,"other":2}'` | shape error: `expected JSON object {cc,other} of integers` (`1.0` has a fraction, PC 5) |
| EC-013 | `HYLO_STATUSLINE_GLYPHS_TIMER='ab'` | `\e[90mhylo: config error: statusline.glyphs.timer=ab (expected exactly 1 code point and 1 display column)\e[0m\n` (PC 6, OD-178) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `HYLO_STATUSLINE_SPARKLINE_ENABLED=0` | sparkline disabled | happy-path |
| `HYLO_BACKENDS_0_MODEL_PREFIXES=" claude-sonnet ,claude-haiku "` | `["claude-sonnet","claude-haiku"]` | edge-case |
| `HYLO_STATUSLINE_GIT_ENABLED=2` (legacy: on) | statusline stdout `\e[90mhylo: config error: statusline.git.enabled=2 (not a boolean (true\|false\|1\|0\|yes\|no))\e[0m\n` (`\e` = 0x1B), exit 0 | error |
| `HYLO_STATUSLINE_COST_PERCENTILES=[0.5,0.9]` | percentiles (0.5, 0.9) — strict-JSON FloatPair grammar (ADV-P4-D19) | happy-path |
| `HYLO_STATUSLINE_COST_PERCENTILES=0.5,0.9` | `\e[90mhylo: config error: statusline.cost.percentiles=0.5,0.9 (expected JSON array of 2 numbers)\e[0m\n`, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-015 | Bool parse accepts exactly six strings | table test (exhaustive over the six plus a fuzz corpus) |
| VP-015 | List parse equals Python `[p.strip() for p in s.split(",") if p.strip()]` on the CPython-generated table | table test against oracle goldens |
| VP-016 | Bool and path-grammar error reasons ride the closed six-class register on the E-CFG-001 surface (PC-1 error strings; invariant 2) | table test (class register) |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-05 (typed booleans), OD-74 (comma-list encoding in env), OD-61 (expand `~` in every path), OD-59 (typed + validated); replaces legacy/dgx_statusline.py:module tunables (SL:76-77 `!= "0"`, SL:78 `expanduser`), render_lane (SL:444-445), term_cols (SL:1185-1190, kept as protocol input) |
| Parity / exclusion | boolean values legacy accepted outside the grammar → D4-EX-3 (boolean class), exclusion entry `D4-EX-3`, test `TestD4EX3_Boolean` (OD-102, OD-105) |
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

- VP-015 — bool grammar exact; VP-016 — error reasons on the six-class register

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | safe for concurrent use (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/types.go (value grammars) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
