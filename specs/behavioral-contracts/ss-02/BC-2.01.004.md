---
document_type: behavioral-contract
level: L3
version: "1.3.0"
status: draft
producer: product-owner
timestamp: 2026-11-19T01:30:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "50dde61"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; key defaults trace to legacy/dgx_statusline.py SL:73-137 via the P4r7 B.2.1 threshold register)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.2.1 2026-11-18T01:42:00Z ADV-P3 remediation D37: build-time reserved EnvName list extended with HYLO_TIMING_GATE and HYLO_PARITY_FUZZSECONDS"
  - "1.2.2 2026-11-18: ADV-P4 remediation A04/A05/D19 + OD-173/174/175 — composite registry types with strict-JSON env grammar; glyph families enumerated member-wise (1 code point / 1 column, OD-02); statusline.labels.input Text key; pill-label and display_floor_usd keys; queue.yellow OD-175 ratification"
  - "1.2.3 2026-11-18: pass-4 sync-check SC-09 — registry text extended with statusline.subagent.tokens.suffix (C05), statusline.sparkline.preempt_marker_above (C2-13) and the dotted key statusline.subagent.glyphs.unknown (C07), type/default/range per interface-definitions.md; no behavioral change"
  - "2026-11-19T00:35:00Z (1.2.4) ADV-P5 remediation B03/C03/A18/D14/D15 + calls 1-2, 16 + OD-179 — glyph family completed with the derived row-2 members (lane, git, cell_on/off, cost_pick, telemetry_dot, degraded, ttft, watts, idle, box_rate, sess_rate, host) and the 8-glyph sparkline ramp; reroute→cache_read and stale→cache_rebuild renamed (no alias); statusline.lane.reroute_all_prefixes registered (OD-179); PC-3(e) millisecond-type wording fixed (IntMap members); OD-170 display-width function defined (D15, ARCH-06 coordination); preempt_marker_above type aligned to pass-5 call 16 (Float, per-second rate)"
  - "2026-11-19T01:30:00Z (1.2.5) pass-5 residual sweep A — glyph-registry consumer cites corrected to the verified renderers and unified with interface-definitions.md (telemetry_dot BC-1.04.005, colour coupled to BC-1.04.004; degraded BC-1.04.004; box_rate BC-1.04.008; sess_rate BC-1.04.018, value from BC-1.03.010; cache_hit adds BC-1.02.008; cell_on/off add BC-1.04.015; ttft adds BC-1.04.019; idle adds BC-1.04.017; cost_pick adds BC-1.05.003); member names, defaults and code points unchanged"
  - "2026-11-19T02:00:00Z (1.2.6): sync-check adv-p5 closure (SC-16) — the four call-16 range keys registered in PC-10 (statusline.transcript.read_cap_bytes, statusline.transcript.dedup_memory, statusline.sparkline.history_cap, statusline.cost.burn_min_api_ms) and the Preconditions-1 amendment sentence extended through call 16, type/default/range per interface-definitions.md; no behavioral change"
  - "2026-11-19T04:15:00Z (1.3.0): ADV-P6 remediation D02+D03+D23+OD-186 — glyph column rule restated per OD-184: every statusline.glyphs.*/subagent.glyphs.* member is exactly 1 code point measured in legacy's render width, sparkline = exactly 8 ordered code points; the EAW validation width no longer applies to glyph members (it keeps the pill-label 1..16 bound), so the W-class watts default ⚡ (U+26A1) is in range; PC-9 scope note with the 中文-measures-4 grounding; reroute-all anchor corrected to SL:487-488 (markers tuple; SL:489 is the rl reset); PC-11 mints statusline.cache.rename_retry_delay_ms (Int, default 10, range 1..1000, J; consumer BC-6.03.003)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-2.01.004: Key registry: every key declares type, range/operator, default and rationale

## Description

`internal/config` exposes one registry, `Registry() []Key`, that is the single source for
every behavior-shaping value in P1 (D15 iron rule). Every entry declares its name, type,
range, the comparison operator legacy uses for it, its default, its unit, and a rationale
with a rationale code (OD-57, OD-114). A build-time test suite rejects any entry that is
incomplete, whose default fails its own validation, or whose env name collides.

## Preconditions

1. The P1 key subset is the one listed in design §2.4 (from the P4r7 §B.2.1 register,
   rationales resolved by OD-57), as amended by OD-113 (theme keys, BC-2.01.003), OD-123
   (backend keys, BC-2.01.002), and the pass-4 owner rulings OD-173 (lane-pill label Text
   keys `statusline.pill.label_local`/`label_cloud`/`label_unknown`, defaults `DGX`/`ANTH`/`?`),
   OD-174 (`statusline.cost.display_floor_usd`, renamed from `cost.basis_min_shown_usd`),
   and OD-175 (`statusline.queue.yellow` ratified as a P1 `Bool` key, default `true`); the
   pass-4 orchestrator design calls add `statusline.subagent.tokens.suffix` (call 3),
   `statusline.subagent.glyphs.unknown` (call 4) and
   `statusline.sparkline.preempt_marker_above` (call 5) — see PC-6 and PC-8; the pass-5
   orchestrator design call 16 further amended the ranges of four existing keys, registered
   with type/default/range in PC-10.

## Postconditions

1. Each `Key` has the fields `Name, Type, Default, Unit, Range, Op, Rationale,
   RationaleCode, Class`:
   - `Name`: dotted lower-snake, matching
     `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*|\[[0-9]+\])*$` (CV-19).
   - `Type`: one of `Seconds, Int, Float, Bool, Enum, URL, List, Path, SGR, Text`; the
     composite numeric types `FloatPair` (Float pair), `FloatTriple` (Float triple),
     `IntMap` (Int map), `RGBTriplesFloat` (RGB triples + Float) and `NumberList` (any list
     of numbers) are additional registry types whose env grammar is strict JSON of the
     declared shape (BC-2.01.005 PC-5, ADV-P4-D19).
   - `Range`: the valid domain stated explicitly (e.g. ttl_s: finite, `>= 0`,
     `<= 9223372036.854775`; trace: `rate|kv|ttft`).
   - `Op`: the comparison exactly as legacy writes it (e.g. ttl_s: `fetch_ts > now − ttl`,
     strict; narrow_cols: `cols >= narrow_cols` keeps row 2), or `n.a.` for non-threshold
     keys (URLs, colors, paths).
   - `Rationale`: non-empty prose, the same text that the code comment next to the default
     carries (D15, CLAUDE.md "explain every threshold").
   - `RationaleCode`: one of `M` (measured), `DOC` (written in source or docs), `J` (labeled
     judgment call), `C` (convention or tool default), `Dv`, `Dv†` (derived), `OWNER-<x>`,
     `EXT` (Claude Code constant) — the P4r7 legend.
   - `Class`: `CFG` (config key). Named constants (NC) are not registry entries; each lives in
     code with a "why not config" comment.
2. `EnvName(key)` = `HYLO_` + the key upper-cased with every `.`, `[` and `]` run replaced
   by a single `_` and no trailing `_` (e.g. `statusline.telemetry.ttl_s` →
   `HYLO_STATUSLINE_TELEMETRY_TTL_S`; `backends[0].metrics_url` →
   `HYLO_BACKENDS_0_METRICS_URL`) (OD-01, OD-74).
3. Build-time table tests over `Registry()` fail the build when any of these hold:
   (a) a required field is empty; (b) `RationaleCode` is outside the legend;
   (c) the default does not pass the key's own type + range validation; (d) two keys share an
   `EnvName`, or an `EnvName` equals a reserved name (`HYLO_CONFIG`, `HYLO_TEST_NOW`,
   `HYLO_PARITY_PYTHON`, `HYLO_TIMING_GATE`, `HYLO_PARITY_FUZZSECONDS`; the last two added
   per ADV-P3-D37/ADV-P3-A20) or `COLUMNS`; (e) a name ending in `_s` is not type `Seconds`, or
   `_ms` is not a millisecond-valued type — `Int`, `Float`, or a composite numeric type
   whose members are milliseconds (`IntMap`, e.g. `statusline.cost.rate_min_api_ms`;
   ADV-P5-D14); (f) a default differs from the legacy value
   recorded in the golden table `internal/config/testdata/legacy_defaults.golden` (key →
   legacy value → SL line), except the two documented exceptions in PC-4.
4. Documented default exceptions to "defaults equal legacy until cutover" (D15), each
   carrying the OD in its rationale: `paths.cache_dir` (platform cache dir, not
   `~/.cache/dgx-llm`; OD-101) and `backends[0].model_prefixes` (`claude-sonnet`, legacy
   status line default `""`; OD-111, OD-123).
5. Registry order is stable and is the order used for config-error reporting
   (BC-2.02.001).
6. **Glyph registry enumeration (ADV-P4-A05, orchestrator design call 2; column rule
   OD-184):** the
   `statusline.glyphs.*` family comprises exactly these members, each a `Text` key whose
   value is measured in legacy's render width — **code points**, the count legacy's layout
   uses. Every member is exactly **1 code point**, except `statusline.glyphs.sparkline` =
   exactly **8 ordered code points** (env name via PC-2's `EnvName`):

   | Key | Default | Consumer |
   |-----|---------|----------|
   | `statusline.glyphs.tools` | `▤` (U+25A4) | BC-1.02.007 |
   | `statusline.glyphs.conversation` | `❙` (U+2759) | BC-1.02.007 |
   | `statusline.glyphs.thinking` | `◈` (U+25C8) | BC-1.02.007 |
   | `statusline.glyphs.lines_up` | `▲` (U+25B2) | BC-1.02.014 |
   | `statusline.glyphs.lines_down` | `▼` (U+25BC) | BC-1.02.014 |
   | `statusline.glyphs.timer` | `⏱` (U+23F1) | BC-1.02.015, BC-1.02.028 |
   | `statusline.glyphs.window_age` | `⌂` (U+2302) | BC-1.02.017, BC-1.02.028 |
   | `statusline.glyphs.tokens_up` | `↑` (U+2191) | BC-1.02.018 |
   | `statusline.glyphs.write` | `✍` (U+270D) | BC-1.02.018 |
   | `statusline.glyphs.cache_read` | `⟳` (U+27F3; SL:594 — renamed from `reroute`, ADV-P5-B04/call 2: the glyph means cache reads; not shipped, so no alias) | BC-1.02.018 |
   | `statusline.glyphs.tokens_down` | `↓` (U+2193) | BC-1.02.018 |
   | `statusline.glyphs.cache_rebuild` | `↻` (U+21BB; SL:598-599 — renamed from `stale`, ADV-P5-B04/call 2: the glyph means cache rebuilds; not shipped, so no alias) | BC-1.02.018 |
   | `statusline.glyphs.cache_hit` | `♻` (U+267B; SL:479) | BC-1.02.008, BC-1.02.023 |
   | `statusline.glyphs.lane` | `◨` (U+25E8; the main pill marker AND the subagent-tag marker, SL:447-449/SL:902-903) | BC-1.02.001, BC-1.07.006 |
   | `statusline.glyphs.git` | `⎇` (U+2387; SL:413) | BC-1.02.005 |
   | `statusline.glyphs.cell_on` | `▰` (U+25B0; filled cell) | BC-1.02.006, BC-1.04.007, BC-1.04.015 |
   | `statusline.glyphs.cell_off` | `▱` (U+25B1; empty cell) | BC-1.02.006, BC-1.04.007, BC-1.04.015 |
   | `statusline.glyphs.cost_pick` | `⛏` (U+26CF; KD-002) | BC-1.02.029, BC-1.05.003 |
   | `statusline.glyphs.telemetry_dot` | `◉` (U+25C9; row-2 telemetry dot, SL:730) | BC-1.04.005 (dot colour coupled to BC-1.04.004) |
   | `statusline.glyphs.degraded` | `◌` (U+25CC; row-2 red `◌ DGX ?` marker, SL:696) | BC-1.04.004 |
   | `statusline.glyphs.ttft` | `◔` (U+25D4; row-2 TTFT marker, SL:797-799) | BC-1.04.010, BC-1.04.019 |
   | `statusline.glyphs.watts` | `⚡` (U+26A1; row-2 power marker, SL:808-813; 1 code point — East-Asian Width W, which under OD-184 does NOT violate the member rule: glyph columns are counted in code points, not terminal columns, ADV-P6-D02) | BC-1.04.011 |
   | `statusline.glyphs.idle` | `☾` (U+263E; row-2 idle marker, SL:834) | BC-1.04.012, BC-1.04.017 |
   | `statusline.glyphs.box_rate` | `▣` (U+25A3; row-2 box-rate marker, SL:770/783) | BC-1.04.008 |
   | `statusline.glyphs.sess_rate` | `»` (U+00BB; row-2 session-rate marker, SL:781 — the subagent `running` glyph shares the code point via its own family key) | BC-1.04.018 (value from BC-1.03.010) |
   | `statusline.glyphs.host` | `↺` (U+21BA; row-2 host-share marker, SL:752/762) | BC-1.04.007 |
   | `statusline.glyphs.sparkline` | `▁▂▃▄▅▆▇█` — exactly the 8 ordered glyphs U+2581..U+2588 (legacy `SPARK`, SL:136; the one member whose value is NOT 1 code point: it is the 8-code-point ramp, indexed left-to-right by bar height; OD-184 carve-out) | BC-1.04.009 |

   The `statusline.subagent.glyphs.*` family comprises `running` (`»`, U+00BB),
   `completed` (`✔`, U+2714), `failed` (`✘`, U+2718), `killed` (`◍`, U+25CD) and —
   added by the pass-4 C07 disposition as its own key (not derived from `glyphs.killed`,
   though sharing its default) — `statusline.subagent.glyphs.unknown` (`Text`, default
   `◍` U+25CD; exactly 1 code point (OD-184), non-empty, no control bytes;
   rendered in `statusline.theme.grey`; SL:894; env
   `HYLO_STATUSLINE_SUBAGENT_GLYPHS_UNKNOWN`). The two-character input label is NOT a
   glyph: it is the `Text` key `statusline.labels.input` (default `in`, env
   `HYLO_STATUSLINE_LABELS_INPUT`). A glyph member whose value is not exactly 1 code
   point (sparkline: exactly 8 ordered code points) fails the build-time tests of PC-3.
   The East-Asian-Width validation width (PC-9, OD-170 tables) is NOT applied to glyph
   members (OD-184): it is consulted only for ranges that state a display width — the
   pill-label 1..16 bound (OD-173) — so the W-class `watts` default ⚡ is in range.
7. **Label and floor keys (OD-173/OD-174):** the lane-pill words are the `Text` keys
   `statusline.pill.label_local` (default `DGX`), `statusline.pill.label_cloud` (default
   `ANTH`) and `statusline.pill.label_unknown` (default `?`), range: non-empty, no control
   bytes, display width 1..16 (BC-2.01.005 PC-6). The cost-basis display floor is
   `statusline.cost.display_floor_usd` (Float, 0.005) — the rename of
   `cost.basis_min_shown_usd` per OD-174; the D7 citation is dropped with the rename.
8. **Subagent token suffix and sparkline preempt-marker keys (pass-4 C05 and C2-13,
   orchestrator design calls 3 and 5):** the registry carries
   `statusline.subagent.tokens.suffix` (Text, default ` tok` — U+0020 + `tok`; range:
   non-empty, no control bytes, mirroring BC-2.01.003 PC-3; env
   `HYLO_STATUSLINE_SUBAGENT_TOKENS_SUFFIX`) and
   `statusline.sparkline.preempt_marker_above` (Float per pass-5 call 16/C2-11 — it
   compares the per-second `dgx_preempt:rate5m` rate, so an Int could not express the
   historical > 0.01/s rule; default `0`; range `>= 0`; the
   history `p` marker shows when preempt > the value; independent of
   `statusline.queue.yellow`; env `HYLO_STATUSLINE_SPARKLINE_PREEMPT_MARKER_ABOVE`).
   The `k_from`/`m_from` values are display thresholds only — the divisors 1e3/1e6 are
   format constants that define the K/M units, not config (why-not-config comment
   required at the call site).

9. **Pass-5 additions (ADV-P5-B03/C03/A18/D14/D15, orchestrator calls 1-2, OD-179):**
   - **Reroute-all key (OD-179):** the reroute-all markers become the List key
     `statusline.lane.reroute_all_prefixes` (default `["claude", "claude-"]`, markers
     tuple legacy SL:487-488; SL:489 is the `rl = {}` reset the markers feed,
     ADV-P6-D23), range: every entry non-empty and control-free; it is never a hard-coded
     literal in logic. Consumer: BC-1.02.011 (reroute-all hiding, with BC-1.02.009's
     provenance).
   - **Derived members:** the PC-6 table above is the complete enumeration of the
     behavior-shaping glyph roles legacy prints; every literal printed glyph is a
     member. Punctuation and format characters (`·`, `°`, `¢`, `->`) are format
     constants, not glyphs (why-not-config comments at the call sites).
   - **Display width (D15, OD-170):** the display width of a string is the sum over its
     code points of the OD-170 width function on hylo's own Unicode 14.0.0 tables:
     width 2 for East-Asian Width Wide/Fullwidth code points; width 0 for combining
     marks (Mn, Me) and Cf format code points; width 1 otherwise (Ambiguous counts 1 —
     the legacy target-terminal behavior; judgment call OD-02 width discipline);
     U+0000-U+001F and U+007F are control bytes with no width (range violations, not
     widths). The OD-170 generated-table set grows the East-Asian-Width table
     (coordination: ARCH-06 adds the width class to its OD-170 table list).
     Punctuation-or-format characters are not widths; the width function is total over
     valid UTF-8 input. Scope (OD-184): this validation width is consulted ONLY for the
     registry ranges that state a display width — the pill-label 1..16 bound (OD-173)
     and the general Text ranges of BC-2.01.005 PC-6 — never for glyph-family
     validation, which counts code points (PC-6). Grounding: under this function
     `中文` measures 4 (both code points EAW W), and the watts default ⚡ measures 2
     while remaining a valid 1-code-point glyph (ADV-P6-D02, ADV-P6-D17).
   - **PC-3(d) reserved-name list unchanged** (`HYLO_PARITY_FUZZSECONDS` et al.); the
     D30 citation target BC-6.04.003 now names the setting and its 0/unset semantics.

10. **Call-16 range registrations (pass-5 A13/C2-08, orchestrator design call 16;
   sync-check SC-16):** the registry carries the four keys whose ranges call 16 changed,
   with type/default/range identical to interface-definitions.md:
   - `statusline.transcript.read_cap_bytes` — `Int (bytes)`, default `524288`, range
     `1..67108864` (upper bound 64 MiB, labeled judgment call: caps per-refresh read
     buffering far beyond any real transcript step; RationaleCode `J`, T-054); consumer
     BC-1.03.003; env `HYLO_STATUSLINE_TRANSCRIPT_READ_CAP_BYTES`.
   - `statusline.transcript.dedup_memory` — `Int`, default `256`, range `1..65536` (upper
     bound labeled judgment call; RationaleCode `Dv`, T-060); consumer BC-1.03.005; env
     `HYLO_STATUSLINE_TRANSCRIPT_DEDUP_MEMORY`.
   - `statusline.sparkline.history_cap` — `Int`, default `32`, range `1..1000` (upper
     bound labeled judgment call, same render-budget rationale as `kv.cells`;
     RationaleCode `Dv`, T-009); consumers BC-1.04.003/.009; env
     `HYLO_STATUSLINE_SPARKLINE_HISTORY_CAP`.
   - `statusline.cost.burn_min_api_ms` — `Int`, default `300000`, range `> 0` (ratio
     gate; ZeroDivisionError guard rationale as for `cost.rate_min_api_ms`, pass-5
     C2-08/call 16; RationaleCode `Dv`, T-043); consumer BC-1.05.002; env
     `HYLO_STATUSLINE_COST_BURN_MIN_API_MS`.

11. **Windows rename-retry delay (OD-186, ADV-P6 remediation):** the registry carries
   `statusline.cache.rename_retry_delay_ms` — `Int (ms)`, default `10`, range `1..1000`
   (labeled judgment call: long enough to let a concurrent Windows reader close its
   handle, far below any perceptible refresh latency; RationaleCode `J`). Millisecond
   delay between rename-retry attempts in the cache Save path after a sharing violation
   (attempt count stated once — three attempts total, initial attempt + two retries — in
   BC-6.03.003, ARCH-04 and VP-018); consumer BC-6.03.003; env
   `HYLO_STATUSLINE_CACHE_RENAME_RETRY_DELAY_MS`.

## Invariants

1. Logic reads every behavior-shaping value from the resolved config, never a literal
   (D15); protocol/format constants (API paths, the D7 ledger schema, the 40-char sid
   truncation T-061, the sha1 prefix T-062) are named constants with comments.
2. `HYLO_TEST_NOW` is a harness hook, not a key (design §3.2, RK-5).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | A new key added without `Rationale` | build-time test fails naming the key |
| EC-002 | A key `statusline.foo_s` declared as `Int` | test (e) fails |
| EC-003 | Two keys `a.b_c` and `a_b.c` (both `HYLO_A_B_C`) | collision test fails |
| EC-004 | `statusline.telemetry.ttl_s` default changed to 5 | legacy-default golden test fails (legacy SL:74 is 4) |
| EC-005 | `paths.cache_dir` default ≠ `~/.cache/dgx-llm` | allowed: listed exception citing OD-101 |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `Registry()` entry for `statusline.telemetry.ttl_s` | `Type=Seconds, Default=4, Unit=s, Range="finite, >= 0, <= 9223372036.854775", Op="fetch_ts > now − ttl (strict)", RationaleCode=DOC, Rationale="match refreshInterval (legacy SL:50; T-001)"` | happy-path |
| `EnvName("backends[0].model_prefixes")` | `HYLO_BACKENDS_0_MODEL_PREFIXES` | edge-case |
| registry with an entry whose default `"x"` is type `Int` | build-time test failure | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-015 | `EnvName` is injective over `Registry()` | table test |
| VP-015 | Every default validates under its own type and range | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — D15 (config over code), OD-57 (rationales accepted), OD-114 (type and range per key), OD-01/OD-74 (env naming), CV-19 (operator in comment), P4r7 §B.2.1 register (79 status line rows); defaults trace to legacy/dgx_statusline.py module tunables (SL:73-100) and primitives (SL:127-137) |
| Parity / exclusion | n.a. |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-010 |
| Architecture Module | `internal/config/registry.go`, `statusline_keys.go` (BC-COMPONENT-MAP: internal/config/registry.go (key registry) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.01.001 — consumer (resolution iterates the registry)
- BC-2.01.002, BC-2.01.003 — composes with (backend and theme entries)
- BC-2.02.002..005 — composes with (range/type validation per class)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#registry` — internal/config/registry.go (key registry) (registry schema) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — config registry

## VP Anchors (Recommended)

- VP-015 — EnvName injective; defaults self-validate

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | safe for concurrent use (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/registry.go (key registry) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
