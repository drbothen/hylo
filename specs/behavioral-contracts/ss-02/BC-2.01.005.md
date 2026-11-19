---
document_type: behavioral-contract
level: L3
version: "1.4.6"
status: draft
producer: product-owner
timestamp: 2026-11-21T06:00:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "b80b867"
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
modified:
  - "2026-11-18T00:00:00Z (1.2.2): ADV-P3 remediation D07 — P1 Bool set completed with queue.yellow and subagent.enabled"
  - "2026-11-18T22:00:00Z (1.2.3): ADV-P4 remediation D19+D26 — composite strict-JSON env grammar (PC-5) and OD-173 label-Text validation (PC-6) added; queue.yellow priority citation corrected to OD-175"
  - "2026-11-19T00:40:00Z (1.2.4): ADV-P5 remediation D05+D06+D07+D12+D13 — PC-5 shapes written per key and matched to defaults (colors object spelling supersedes the positional triple-array; IntMap exact-keys/JSON-integer/int64/duplicate rules; scale is a 4-number array); PC-6 Text reasons minted for glyph and general Text keys; PC-7 default-only rule (byte-equal accepted, else out of range, OD-162); FloatPair example corrected to the registered [0.5,0.9] range (D12)"
  - "2026-11-19T02:00:00Z (1.2.5): ADV-P5 remediation A03 correction — sparkline.colors fade elements renamed [lo, hi] to [base, span] and law restated as base + span-times-i/max(n-2, 1) per legacy SL:683 (a base and a span, not a range)"
  - "2026-11-19T04:20:00Z (1.3.0): ADV-P6 remediation D01+D04+OD-184 — PC-7 default-only spellings minted per orchestrator call 8 (theme.heat env spelling is the strict-JSON array [0.22,0.85,0.80]; comparison on the PARSED value, not bytes; limits.windows 5h,7d; units.lines k; units.tokens M); EC-010/EC-011 realigned (0.5/0.5/0.5 is now the shape error it always was under PC-5); glyph PC-6 wording states the OD-184 code-point enforcement behind the fixed reason string; VP-016 row and VP anchor say seven classes"
  - "2026-11-19T17:30:00Z (1.3.1): ADV-P7 remediation D01+D02+D09 (orchestrator call 5) — PC-7 env names canonized under EnvName (HYLO_STATUSLINE_LIMITS_WINDOWS, HYLO_STATUSLINE_UNITS_LINES=k, HYLO_STATUSLINE_UNITS_TOKENS=M, HYLO_STATUSLINE_UNITS_CONTEXT=K) with registry Defaults single-valued (= the accepted spelling), legacy derivations and a stated reason why the letters differ; PC-6 glyph reasons corrected per OD-184 to expected exactly 1 code point / expected exactly 8 code points (sparkline); PC-5 scale attributed to NumberList with a registry-declared fixed length of 4"
  - "2026-11-19T21:00:00Z (1.4.0): ADV-P8 remediation D04+D05+D07+D15 — H1/Description/Pre-1 broadened to cover PC-5/PC-6/PC-7 (P7); PC-2 item wording corrected: List items get the PC-6 control-free check (a control byte in an item is the Text-class `control character` error, OD-178/pass-6 A14) with key-specific entry ranges superseding; PC-5 type enumeration completed with FloatQuad (the 1.3.1 changelog's 'NumberList' wording for scale is superseded — the registry type is FloatQuad, fixed length 4) and an overflowing JSON member classified: a literal such as `1e400` parses to ±Inf, passes the strict-JSON shape check and fails the member-wise range check with `not finite` (BC-2.02.001 precedence check 1); PC-6 gains the control-character rule and now mints five reason strings"
  - "2026-11-20T18:30:00Z (1.4.1): ADV-P9 remediation A11+D18+D08+D07 (orchestrator calls 13+15+14+14) — PC-3: paths.cache_dir MUST resolve absolute (relative value = config error `not an absolute path`, path-grammar family, OD-144 rationale) and a set-but-empty HOME/USERPROFILE is home-unknown (BC-2.03.002 PC-4 consistent); PC-6 mints the Text-class `invalid UTF-8` pre-check (six reason strings); PC-7 states the Text-class-checks-first order for default-only Text/List keys with exact bytes"
  - "2026-11-21T06:00:00Z (1.4.2): ADV-P10 remediation D08 — three legacy citations corrected against legacy/dgx_statusline.py: fade formula SL:683 → SL:682 (SL:683 is the RGB scaling), _fmt_lines whole-thousands `184k` SL:860 → SL:859 (SL:860 is `return str(n)`), token millions `88.0M` SL:871 → SL:870 (the .1f}M spelling; SL:871 is the k branch)"
  - "2026-11-21T07:00:00Z (1.4.3): ADV-P11 remediation D12 (orchestrator call 16) — PC-6's control-byte rule states the ANY-TEXT verdict: a control byte in an any-text key value (e.g. statusline.telemetry.query) yields the same Text-class reason 'control character' (its only bounds are the control-byte bound and valid UTF-8; the empty string stays in range); sibling A09/D08 respell — PC-5 band defaults to strict-JSON env spellings [80,100] and [70,90]"
  - "2026-11-22T00:00:00Z (1.4.4): ADV-P12 remediation D06 (orchestrator call 9) + D07 (call 10) + D12 — PC-2 List: strip-then-validate order STATED (Python str.strip() FIRST, then control-byte/emptiness checks on the stripped item; legacy-identical; applies to limits.windows and reroute-all entries too); PC-3: the ~-expansion home source is platform.HomeDir(env) — a relative HOME (macOS/Linux) or relative USERPROFILE (Windows) is treated as UNSET (BC-3.01.001 PC-2 kind discipline), yielding 'home directory unknown' (with a relative home, ~/c reports home-unknown, never 'not an absolute path'); PC-3 absoluteness gains the per-OS filepath.IsAbs rule (Windows: \\foo and C:foo are relative), propagated from BC-3.01.001 PC-3 / BC-2.03.002 PC-3"
  - "2026-11-23T00:00:00Z (1.4.5): ADV-P13 remediation D09 — PC-6 pins the List-item invalid-byte verdict legacy performs: POSIX env values arrive surrogateescape-decoded (byte b = code point U+DC00+b; measured on CPython 3.11.7: raw 0xFF = U+DCFF, Cs, kept by strip), so a List item with invalid POSIX bytes is strip-mapped and ACCEPTED — no invalid-UTF-8 verdict exists for List items and no new reason string enters the BC-2.02.001 vocabulary; 0xFF vector added"
  - "2026-11-25T00:00:00Z (1.4.6): ADV-P14 remediation D01+D07 (orchestrator calls 5, 11) — PC-6 extends the display-width 1..16 bound and its reason string to the nine width-bounded statusline.labels.* members (OD-194); the List-item passage pins the U+DC00+b mapping as stored in the BC-5.02.004 WTF-8 form with prefix matching over those bytes"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-2.01.005: HYLO_* value grammars: Bool, List, Path, strict-JSON composites, Text, and default-only keys; COLUMNS excluded as protocol input

## Description

Defines how a `HYLO_*` string becomes a typed value for the non-numeric shared types —
the plain grammars (`Bool` PC 1, `List` PC 2, `Path` PC 3), the composite strict-JSON
types (PC 5), `Text` (PC 6) and the default-only keys (PC 7):
booleans accept only `true/false/1/0/yes/no` (OD-05), lists are comma-encoded (OD-74), and
path values expand a leading `~` (OD-61). `COLUMNS` is a Claude Code protocol input read by
the renderer with the Python `int()` grammar (BC-1.01.005), never a config key (ENV-15).
Number grammars are BC-2.02.003; URL is BC-2.02.005; enum is BC-2.02.004.

## Preconditions

1. A registry key whose type is `Bool`, `List` or `Path` (PC 1-3), a composite numeric
   type (PC 5), or `Text` (PC 6), or that the registry marks default-only (PC 7), and
   whose `EnvName` is present (BC-2.01.001).

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
   semantics (`pyfmt.Strip`, OD-103) FIRST, then validated on the STRIPPED item (control
   bytes, emptiness — check order stated pass-12 call 9: strip-then-validate,
   legacy-identical; a value ending in a tab is accepted because the tab is stripped,
   while check-first would raise `control character`). Empty items are dropped; order
   and duplicates are kept.
   `""` → empty list (valid). This reproduces legacy SL:444-445 for
   `backends[0].model_prefixes`. Stripped items are otherwise validated only by the PC-6
   control-free check (pass-8 D04: a control byte in an item is the Text-class
   `control character` error, OD-178/pass-6 A14); where the registry declares a
   key-specific entry range — `statusline.lane.reroute_all_prefixes` (BC-2.01.004 PC-9,
   reason `expected non-empty control-free text in every entry`) — that range supersedes
   for the key's entries. No other item validation in P1. The same strip-then-validate
   order applies to `statusline.limits.windows` and to reroute-all entries.
3. **Path:** a value equal to `~`, or starting with `~/` (or `~\` on Windows), has that `~`
   replaced by the user home directory (`HOME` on macOS/Linux, `USERPROFILE` on Windows);
   `~user` forms are left literal; other values are used as given. Absoluteness
   (ADV-P9-A11, orchestrator call 13): the P1 path key `paths.cache_dir` MUST resolve
   absolute — a RELATIVE value (after `~` expansion) is a config error with the exact
   reason `not an absolute path` (path-grammar reason family: no dedicated class, riding
   E-CFG-001 per the Reason-Vocabulary note in BC-2.02.006; a relative value would
   resolve against Claude Code's per-project cwd and split caches and cost history, the
   same reason relative `XDG_*` values are rejected, OD-144; the registry row is
   interface-definitions `paths.cache_dir`). Absoluteness is `filepath.IsAbs` semantics
   computed in `internal/platform` per OS (Windows: drive + root or UNC; `\foo` and
   `C:foo` are relative) — the same per-OS rule BC-3.01.001 PC-3 and BC-2.03.002 PC-3
   state (propagated pass-12 D12). The home source for `~` expansion is
   `platform.HomeDir(env)` (the BC-3.01.001 PC-2 seam): a RELATIVE `HOME` (macOS/Linux)
   or relative `USERPROFILE` (Windows) is treated as UNSET — the same kind discipline as
   the base directories (BC-3.01.001 PC-2, pass-12 call 10) — yielding
   `<key>=<value> (home directory unknown)`; with a relative home,
   `HYLO_PATHS_CACHE_DIR=~/c` reports `home directory unknown`, never
   `not an absolute path`. A set-but-empty `HOME`/`USERPROFILE` during
   `~` expansion is treated as unavailable — it yields
   `<key>=<value> (home directory unknown)`, consistent with BC-2.03.002 PC-4
   (ADV-P9-D18). `""` yields
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
   (Float triple), `FloatQuad` (Float quadruple — sole member `statusline.sparkline.scale`,
   declared shape `array of 4 numbers`), `IntMap` (Int map), `RGBTriplesFloat`
   (RGB triples + Float) or `NumberList` (any list of numbers) — takes its env value as
   **strict JSON** of the declared shape. A value that is not valid JSON of the declared
   shape yields
   `<key>=<value> (expected JSON <shape>)`, where `<shape>` spells the key's declared
   shape (per-key, from the registry):
   - `array of 2 numbers` (FloatPair). Elements are named per key:
     `statusline.cost.percentiles` = `[p75, p95]`, ASCENDING (`p75 <= p95` ratified,
     pass-3 C2-07); `statusline.limits.projected_bands` = `[yellow, red]` (yellow when
     `proj >= yellow`, red when `proj > red`; legacy default `[80,100]` in the strict-JSON
     env spelling, SL:519);
     `statusline.limits.absolute_bands` = `[yellow, red]` (yellow when `pct > yellow`,
     red when `pct > red`; legacy default `[70,90]`, SL:521). No ordering constraint is
     ratified for the bands pairs — legacy's chained red-first comparison is
     comparison-total for any finite pair.
   - `array of 3 numbers` (FloatTriple; `statusline.theme.heat`, default-only).
   - `array of 4 numbers` — registry type `FloatQuad` (`statusline.sparkline.scale` =
     `[k_top, v_floor, f_floor, other]`; a JSON array of 3 numbers misses the declared
     shape and is a shape error with the same bytes, pass-7 D09); legacy default
     `[1.0, 1.0, 0.1, 1e-9]` from `_SPARK_FIXED`/`_SPARK_FLOOR`
     SL:648-649 and the 1e-9 fallback SL:671; each member finite `> 0`.
   - `object {trail,fade,amber,head}` (RGBTriplesFloat;
     `statusline.sparkline.colors`: trail/amber/head each an array of 3 integers, fade
     an array of 2 numbers `[base, span]`, the trail fade factor
     `base + span·i/max(n-2, 1)` (pass-5 A03 corrected against legacy SL:682
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
   to the Text class (OD-178). An OVERFLOWING member (pass-8 D15): a JSON number literal
   too large for float64 (e.g. `1e400`, which Python's JSON parser maps to +Inf) is not an
   `Infinity` token, so it PASSES the shape check and fails the member-wise range check
   with the number-range reason `not finite` (BC-2.02.001's numeric-range precedence,
   check 1) — the only way a composite reaches `not finite`.
6. **Text keys (OD-173, ADV-P4-B16; runtime reasons minted ADV-P5-D05/OD-178):**
   - The lane-pill label keys `statusline.pill.label_local`, `label_cloud` and
     `label_unknown` (display width 1..16, judgment call keeping the pill short): a
     violating value yields
     `<key>=<value> (expected non-empty control-free text of display width 1..16)`.
     The same bound and the same reason string cover the nine width-bounded
     `statusline.labels.*` members (OD-194, BC-2.01.004 PC-13): a value outside
     1..16 columns yields `expected non-empty control-free text of display width
     1..16` (pass-14 D01).
   - The glyph-family keys (`statusline.glyphs.*`, `statusline.subagent.glyphs.*`):
     a value that is not non-empty control-free text of exactly 1 code point yields
     `<key>=<value> (expected exactly 1 code point)`; the sparkline member yields
     `<key>=<value> (expected exactly 8 code points)`. The reason strings are fixed
     vocabulary (OD-184, pass-7 D02: the former "... and 1 display column" suffix is
     withdrawn — columns are counted in legacy's render width, i.e. code points, not
     terminal columns); the ENFORCED rule is the OD-184 code-point count (8 for the
     sparkline ramp) — the OD-170 validation width is not consulted for glyph members
     (BC-2.01.004 PC-6/PC-9, ADV-P6-D02/D03).
   - Every other `Text` key with the non-empty/no-control-bytes range
     (`statusline.subagent.tokens.suffix`, `statusline.window_age.process_name`,
     `statusline.labels.input`, ...): a violating value yields
     `<key>=<value> (expected non-empty control-free text)`.
   - **Control bytes (OD-178; pass-6 A14, normative here per pass-8 D04):** a control
     byte (0x00-0x1F, 0x7F) anywhere in a non-theme free-text key value, in an
     ANY-TEXT key value (e.g. `statusline.telemetry.query` — its only registered bounds
     are the control-byte bound and valid UTF-8, so the empty string is in range
     (BC-2.01.001 PC-2) and a control byte is the violation), or in a `List`
     item — e.g. `statusline.subagent.joiner` or a `backends[0].model_prefixes` item —
     yields the Text-class reason `control character` (pass-11 D12: the any-text verdict
     is stated; previously only the free-text case was). Precedence: where the registry
     declares a key-specific entry range (`statusline.lane.reroute_all_prefixes`,
     BC-2.01.004 PC-9), that range's own reason
     (`expected non-empty control-free text in every entry`) supersedes for the key's
     entries.
   - **Invalid UTF-8 (pass-9 D08 / orchestrator call 14):** a Text, glyph, label or
     separator value whose bytes are not valid UTF-8 yields the Text-class reason
     `invalid UTF-8` (BC-2.02.001
     vocabulary, mirrored byte for byte in error-taxonomy), checked BEFORE the
     non-empty/control-byte bounds above so no width or code-point count is taken on
     invalid input. On Windows a lone surrogate cannot occur on the env path:
     `platform.EnvVars` reads the UTF-16 environment through Go's standard decoding,
     substituting U+FFFD for an unpaired surrogate (BC-2.01.001 PC-6, pass-12 call 8),
     so this reason is reachable from POSIX byte values only.
   - **List items with invalid POSIX bytes (pass-13 D09).** The `invalid UTF-8` check
     above covers Text, glyph, label and separator values only. A LIST item whose
     bytes are not valid UTF-8 has a DIFFERENT, pinned verdict: acceptance. Legacy
     decodes POSIX environment values with the filesystem encoding plus
     surrogateescape, so an invalid byte b (0x80..0xFF) arrives as the single code
     point U+DC00+b — measured on the oracle interpreter (CPython 3.11.7, `python3
     -I`): the raw byte 0xFF in a POSIX env value decodes to `U+DCFF`, category `Cs`,
     not whitespace, kept whole by `str.strip()`. The byte-to-code-point rule for a
     List item is therefore surrogateescape: Go maps each invalid byte to U+DC00+b
     before `pyfmt.Strip` and the control-free check; U+DC80..U+DCFF are neither
     control bytes (Cs, not Cc) nor whitespace, so the item passes
     strip-then-validate and the key is ACCEPTED. No new reason exists: invalid
     bytes in a List item yield NO Text-class verdict, and the BC-2.02.001 reason
     vocabulary is unchanged. The decoded-item decision itself (prefix matching for
     `backends[0].model_prefixes`) runs bytewise over Go strings holding the mapped
     code points STORED in the BC-5.02.004 WTF-8 form (a lone surrogate kept as
     written, three bytes), decision-equivalent to legacy's mapped-string comparison
     because model names on both sides arrive through the same stdin JSON decode
     (BC-5.02.003) (pass-14 D07). Pin: with
     `HYLO_BACKENDS_0_MODEL_PREFIXES` carrying the raw byte 0xFF on POSIX, the item
     is stripped (no-op), passes the control-free check, and the value is accepted
     with no config error.
   All six reason strings of this PC ride the Text class (OD-178) on the E-CFG-001
   surface.

7. **Default-only keys (ADV-P5-D07 / owner call 3, OD-162; spellings ADV-P6-D01 /
   orchestrator call 8, pass 6):** for a key the registry
   marks default-only — the composite `statusline.theme.heat` and the `Text`/`List`
   keys `statusline.units.context`, `statusline.units.lines`, `statusline.units.tokens`
   and `statusline.limits.windows` — the env value is first parsed under the key's OWN
   grammar (a parse or shape failure is that type's error: strict-JSON shape errors for
   the composite, the List/Text grammar otherwise), and the PARSED value is compared to
   the default: equal → accepted; different → a config error on the E-CFG-001 surface
   riding the number-range class, reason `out of range` (OD-162: the key's valid range
   is its default value only; the number-range class is the OD-162-designated class even
   for Text/List default-only keys). CHECK ORDER for the Text/List default-only keys
   (ADV-P9-D07, orchestrator call 14): the Text-class checks run FIRST — for the `units.*`
   Text keys the empty value (reason `expected non-empty control-free text`) and the
   control byte (reason `control character`); for the `limits.windows` List key the entry
   control byte (`control character`; the empty string is the empty list per PC 2) — and
   only then the default comparison (number-range class, `out of range`). Exact bytes:
   `HYLO_STATUSLINE_UNITS_LINES=` → `(expected non-empty control-free text)`;
   `HYLO_STATUSLINE_UNITS_LINES=$'k\tx'` → `(control character)`;
   `HYLO_STATUSLINE_UNITS_LINES=j` → `(out of range)`;
   `HYLO_STATUSLINE_LIMITS_WINDOWS=$'5h,\x07d'` → `(control character)`;
   `HYLO_STATUSLINE_LIMITS_WINDOWS=` → empty list, not the default → `(out of range)`.
   The default's env spelling — the exact string that
   parses to the default — for each default-only key, with the registry `Default` a
   SINGLE value equal to that spelling (pass-7 D01, orchestrator call 5):
   `HYLO_STATUSLINE_THEME_HEAT` = `[0.22,0.85,0.80]` (strict-JSON FloatTriple; the
   slash spelling `0.22/0.85/0.80` is NOT the grammar and is a shape error);
   `HYLO_STATUSLINE_LIMITS_WINDOWS` = `5h,7d` (comma list; registry Default `5h,7d`);
   `HYLO_STATUSLINE_UNITS_LINES` = `k` (registry Default `k` — legacy `_fmt_lines`
   spells whole thousands lowercase `184k`, SL:859);
   `HYLO_STATUSLINE_UNITS_TOKENS` = `M` (registry Default `M` — the token segment's
   millions denamination `88.0M`, SL:870/882, the binding spelling of pass-6 call 8
   reaffirmed by pass-7 call 5);
   `HYLO_STATUSLINE_UNITS_CONTEXT` = `K` (registry Default `K` — legacy `fmt_ctx`
   spells the sub-million denominator uppercase `/967K`, SL:436-437). WHY THE LETTERS
   DIFFER (judgment call, pass-7 call 5): the three selectors each store the letter
   legacy's own formatter spells for the denamination its governing review names —
   lowercase `k` for the lines base (`184k`), uppercase `K` for the context
   denominator (SI convention trailing a slash-bound total), and the millions `M` for
   the token segment whose approved-mockup headline is the top denamination (`500,
   970k, 88.0M`, SL:864); the widgets never read them (fixed divisors are format
   constants), so the only tested fact is parse-equality with the single default. It
   is definite: `HYLO_STATUSLINE_THEME_HEAT`
   at any parsed-non-default
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
| EC-010 | `HYLO_STATUSLINE_THEME_HEAT='[0.22,0.85,0.80]'` (the default's env spelling, strict JSON) | accepted, no error (PC 7, call 8) |
| EC-011 | `HYLO_STATUSLINE_THEME_HEAT='0.5/0.5/0.5'` | `\e[90mhylo: config error: statusline.theme.heat=0.5/0.5/0.5 (expected JSON array of 3 numbers)\e[0m\n` — a SHAPE error riding the Text class, caught before the default comparison (PC 5, PC 7, ADV-P6-D01) |
| EC-012 | `HYLO_STATUSLINE_COST_RATE_MIN_API_MS='{"cc":1.0,"other":2}'` | shape error: `expected JSON object {cc,other} of integers` (`1.0` has a fraction, PC 5) |
| EC-013 | `HYLO_STATUSLINE_GLYPHS_TIMER='ab'` | `\e[90mhylo: config error: statusline.glyphs.timer=ab (expected exactly 1 code point)\e[0m\n` (PC 6, OD-178, pass-7 D02 wording) |

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
| VP-016 | Bool and path-grammar error reasons ride the closed SEVEN-class register on the E-CFG-001 surface (PC-1 error strings; invariant 2; OD-178) | table test (class register) |

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

- VP-015 — bool grammar exact; VP-016 — error reasons on the seven-class register

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | safe for concurrent use (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/types.go (value grammars) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
