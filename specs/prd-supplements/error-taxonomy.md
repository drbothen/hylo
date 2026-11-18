---
document_type: prd-supplement-error-taxonomy
level: L3
version: "1.14"
status: draft
producer: product-owner
timestamp: 2026-11-19T06:00:00Z
phase: 1a
stage: "3 of 3 (integration)"
inputs: [prd.md]
input-hash: "982366b"
traces_to: prd.md
modified:
  - "1.6 2026-11-18: pass-4 sync-check SC-10 — foreign-cache crash family CP-C01..C10 registered under the named exclusion OD-160, outside the 47-path crash register; no behavioral change"
  - "1.7 2026-11-18: pass-5 remediation — seventh D4-EX-3 class Text (OD-178) with exact reason strings; CP-O06/O07 site widening per BC-1.03.018 (ADV-P4-C08); CP-O10/O11 bearer sites split stdin/history; CP-O09 divergence claim corrected (temp-file, not D4-EX-2; ADV-P5-A21); CP-N03 insertion-order wording (ADV-P5-C2-21)"
  - "1.8 2026-11-18: pass-5 residual sweep — glyph Text reason string matched byte for byte to the class contract vocabulary (expected exactly 1 code point and 1 display column); no behavioral change"
  - "1.9 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-19/SC-20) — history re-spun oldest-first so the version field matches the last entry; no behavioral change"
  - "1.10 2026-11-19T06:00:00Z: pass-6 remediation — closed exclusion set extended to twelve ids (OD-181 metrics transport beyond plain http); `control character` reason extended to the Text class for non-theme free-text keys and List entries; new List-entry violation reason string; TestD4EX3_Text is a Go table test only, not a parity exclusion entry (beside the Theme note); E-REN-002 gains the CP-N03 carrier cites; CP-O10 history-bearer trigger narrowed to the SL:255 division only; no behavioral change (ADV-P6-A14/D14/C2-13; OD-181)"
  - "1.11 2026-11-19T12:00:00Z: pass-7 remediation — glyph reason strings corrected to the OD-184 code-point counts (`expected exactly 1 code point`; sparkline `expected exactly 8 code points`) with the numeric-range reason precedence defined by type (A13/A16/D03, orchestrator call 6); descending `cost.percentiles` pair gets its own ascending-pair reason; CP-T09 minted (Windows MSVC localtime domain OSError on a naive transcript timestamp; CP-T08 retired), register 47 → 48 paths, T family 7 → 8 (call 8/B03); E-REN-002 carrier list completed (CP-N03 owner set BC-1.04.001/.004/.005, A14; CP-O01..O05 and CP-S owners, B11); E-NET-001 gains the KEEP_DEAD dead rung (C2-13); no behavioral change"
  - "1.12 2026-11-19T22:00:00Z: pass-8 remediation — `ascending pair violated (p75 <= p95)` restated as an INTRA-key member-pair check on the one composite key `statusline.cost.percentiles`: the D4-EX-3 line names the whole key with its full JSON env value, no per-member spelling (A11); the only-cross-key sentence rescoped to one cross-KEY case (subagent.tokens) plus one intra-key composite case (A11); no behavioral change"
  - "1.13 2026-11-20T12:00:00Z: pass-8 residual sweep — the `control character` Text example no longer cites a `statusline.lane.reroute_all_prefixes` entry (a control byte there yields the OD-179 List-entry reason of BC-2.01.004 PC-9, not this reason); examples are now `statusline.subagent.joiner` or a `backends[0].model_prefixes` item; CP-O08 site cell records that SL:996 is unreachable at CP-O08 magnitudes (BC-1.03.010 EC-009)"
  - "1.14 2026-11-20T18:00:00Z: pass-9 remediation — CP-O12 minted (cost-pick equivalence: exact-int sum of two sub-bound tokens overflows at tot * dgx_mtok, SL:626/633; Surface 1 render-time degrade like CP-O04; owner BC-1.02.029, co-owner BC-1.05.003), register 48 → 49 paths (O family 11 → 12), E-REN-002 family list and carrier set completed (call 4/B03); Text-class reason `invalid UTF-8` mirrored byte for byte from BC-2.02.001 (D08); E-NET-001 dead rung states it follows `statusline.theme.red` and `statusline.glyphs.degraded` (A14); no behavioral change"
---

# Error Taxonomy: hylo P1 statusline

> PRD supplement — extracted from PRD Section 5.
> Referenced by: implementer, test-writer.
> Principle (DI-008): the user-visible render never fails and never exits non-zero.
> Errors are observable as (a) the degraded ladder or (b) one-line grey notices; non-zero
> exits exist only in validate/usage contexts and inside the parity harness.

## Error Categories

| Category Code | Category | Description |
|--------------|----------|-------------|
| REN | Rendering degrade | guard recovery or typed crash-path degrade; the 29-byte line |
| CFG | Configuration | D4-EX-3 invalid `HYLO_*` values (seven classes) |
| CLI | Command-line | unknown flags, usage errors |
| VAL | Validation | `config validate` reporting |
| NET | Metrics transport | metrics store unreachable/500/garbage |
| FS  | Filesystem | cache load/save faults, failed replaces |
| HAR | Harness integrity | canary, exclusion machinery, corpus hygiene (harness process only) |

## Error Catalog

| Error Code | Category | Severity | Exit Code | Observable / Message Format |
|-----------|----------|----------|-----------|----------------------------|
| E-REN-001 | REN | broken | 0 | `\e[90mstatusline degraded\e[0m\n` (29 bytes) — BC-1.01.001. Failure of the degraded-line write itself (legacy CP-X03, stdout closed) is the named exclusion `cp-x03` (OD-136): Go swallows the write error and still exits 0, per DI-008 |
| E-REN-002 | REN | broken | 0 | same line, via typed CP-* degrades (overflow/NaN/type confusion): CP-S01..S17, CP-N01/N02/N03, the OD-156 Surface 1 overflow family CP-O01..O05, CP-O10/O11 and the cost-pick sum CP-O12, the Surface 3 subagent family CP-A01..A05, and the Windows localtime-domain transcript degrade CP-T09 (pass-7 call 8/B03; CP-O12 minted pass-9 call 4/B03; the Surface 2 transcript family CP-O06..O08 resolves to the D4-EX-2 skip discipline; CP-O09 reproduces the legacy no-write save, not a skip — BC-1.03.006 PC5; none of them a line degrade) — BC-1.01.008, BC-1.02.001, BC-1.02.006, BC-1.02.011, BC-1.02.012, BC-1.02.014, BC-1.02.017, BC-1.02.020, BC-1.02.025, BC-1.02.026/.027, BC-1.02.029 (CP-O12 owner; pass-9 call 4), BC-1.02.030, BC-1.03.015, BC-1.04.001, BC-1.04.004, BC-1.04.005 (CP-N03 carriers; pass-7 A14), BC-1.05.003 (CP-O12 co-owner), BC-1.05.007, BC-1.07.007/.008, BC-5.04.001 (CP-T09) |
| E-CFG-001 | CFG | degraded | 0 | `\e[90mhylo: config error: <key>=<value> (<reason>)\e[0m\n`; stderr detail `[from <ENVNAME>]` — BC-2.02.001 |
| E-CLI-001 | CLI | degraded | 0 | `\e[90mhylo: unknown flag <flag>\e[0m\n` — BC-4.01.002 |
| E-CLI-002 | CLI | broken | 2 | golden usage text on stderr — BC-4.01.001 |
| E-VAL-001 | VAL | broken | 1 | plain reason lines (no SGR), one per error — BC-2.03.001 |
| E-NET-001 | NET | degraded | 0 | freshness ladder down to the stale suffix; past KEEP_DEAD the dead rung `\e[31m◌ <label_local> ?\e[0m` (the red parameter is the `statusline.theme.red` value — default `31`, byte-equal to legacy — and the glyph is `statusline.glyphs.degraded`, default U+25CC: the rung follows the config keys, unlike the theme-independent grey of E-REN-001, because it renders only in a successfully configured render; BC-1.04.004 PC3, pass-9 A14; marker word from `statusline.pill.label_local`, OD-189) — BC-1.04.001/.004, BC-1.04.002 (PC4 dead rung; BC-1.04.020 step 5; pass-7 C2-13) |
| E-FS-001 | FS | degraded | 0 | never-raise caches; failed replace persists nothing — BC-1.06.001/.002 |
| E-HAR-001 | HAR | broken | non-zero | harness FAIL naming the reason (canary, missing table test, glob, id outside closed set) — BC-6.01.003, BC-6.03.004 |

## D4-EX-3 config-error line (E-CFG-001) in detail

Format (BC-2.02.001, OD-102): `\e[90m` + `hylo: config error: ` + `<key>` + `=` +
`<value>` + ` (` + `<reason>` + `)` + `\e[0m` + `\n`. Exactly one line on stdout — the
first error in stable registry order; the full list goes to stderr; a config-error run
writes no caches. `<key>` is the dotted config name (not the env var); `<value>` is
escaped with control bytes and invalid UTF-8 as `\xNN`. In `--subagent` mode a config
error emits **zero bytes on stdout**; all reason lines (the full list) go to stderr (OD-168; pass-4 A22).

Classes and owner rulings: number-range (BC-2.02.002; OD-114 keeps TTL 0 valid, contra
IM-16; every registry key declares a range and an out-of-range value is a number-range
config error — OD-162; int64-overflow and Duration-ceiling values are number-range cases —
OD-164), number-grammar (BC-2.02.003), enum (BC-2.02.004), URL (BC-2.02.005), boolean
(BC-2.02.006; OD-140 — dedicated class contract; grammar pinned in BC-2.01.005), theme/SGR
(BC-2.01.003 — reason string `not an SGR parameter list`, named class per OD-134, resolving
PRD OQ-6), and **Text** (BC-2.01.005 — composite-shape, pill-label, glyph and empty-text
errors; named seventh class by **OD-178**, pass-5 A06/D05). The class register is closed
at seven (OD-114 four + OD-134 + OD-140 + OD-178). Unknown-flag precedence: E-CLI-001 is
checked before E-CFG-001.

## Reason Vocabulary (exact strings, BC-2.02.001)

| Reason | Class | Raised by |
|--------|-------|-----------|
| `underscore in numeral` | number-grammar | BC-2.02.003 |
| `non-ASCII digit` | number-grammar | BC-2.02.003 |
| `not a number` / `not an integer` | number-grammar | BC-2.02.003 |
| `not finite` / `negative` / `must be > 0` / `out of range` | number-range | BC-2.02.002/.003 |
| `ascending pair violated (k_from <= m_from)` | number-range (cross-key pair check, fired at `m_from`'s validation; pass-6 A19) | BC-2.01.004 pair rule |
| `ascending pair violated (p75 <= p95)` | number-range (INTRA-key member-pair check on the ONE composite key `statusline.cost.percentiles` — both pair members are members of the key's single JSON value, unlike the cross-KEY `subagent.tokens` pair; it fires at that key's validation, after both members pass their single-member range checks, `p95` second under the same fire-at-second rule as the `m_from` check; pass-7 A13/D02, call 6 — cost.percentiles' OWN reason, the k_from string is not reused; when it fails, the D4-EX-3 line names the WHOLE key `statusline.cost.percentiles` with its full JSON env value — a member has no separate env spelling, pass-8 A11) | BC-2.01.004 pair rule (widget owner BC-1.05.005) |
| `expected exactly 1 code point` | Text (glyph family and `statusline.subagent.glyphs.*` runtime values; the enforced rule is the OD-184 code-point count measured in legacy's render width — there is NO display-column check under OD-184; pass-7 A16/call 6) | BC-2.01.005, BC-2.01.004 |
| `expected exactly 8 code points` | Text (sole member `statusline.glyphs.sparkline`, the U+2581..U+2588 ramp; OD-02/OD-184; pass-7 A16/call 6) | BC-2.01.005, BC-2.01.004 |
| `not a boolean (true\|false\|1\|0\|yes\|no)` | boolean | BC-2.01.005 |
| `unknown value (<v1>\|<v2>\|...)` | enum | BC-2.02.004 |
| `scheme must be http or https` / `not a URL` / `missing host` | URL | BC-2.02.005 |
| `control character` | URL (BC-2.02.005) / theme (BC-2.01.003) / Text (OD-178: control bytes in non-theme free-text keys and List entries — e.g. `statusline.subagent.joiner` or a `backends[0].model_prefixes` item; a control byte in a `statusline.lane.reroute_all_prefixes` entry instead yields the OD-179 List-entry reason of BC-2.01.004 PC-9; pass-6 A14) | BC-2.02.005, BC-2.01.003, BC-2.01.005 |
| `invalid UTF-8` | Text (a Text, glyph, label or separator value that is not valid UTF-8; on Windows a WTF-8 value with a lone surrogate; minted in BC-2.02.001 pass-9 D08 and mirrored here byte for byte — agent 8's BC-2.02.001 amendment had not landed on disk when this mirror was written, so the mirror is the minting source of record for the string) | BC-2.02.001, BC-2.01.005 |
| `expected non-empty control-free text in every entry` | Text (List-entry violations, e.g. `statusline.lane.reroute_all_prefixes` empty or control-byte entry; OD-179 range + OD-178 class; pass-6 A14) | BC-2.01.004 |
| `not an SGR parameter list` | theme | BC-2.01.003 |
| `expected JSON <shape>` (`<shape>` = e.g. `array of 2 numbers`, `object {cc,other} of integers`) | Text (composite shape; OD-178) | BC-2.01.005 |
| `expected non-empty control-free text of display width 1..16` | Text (pill labels; OD-178) | BC-2.01.005 |
| `expected non-empty control-free text` | Text (generic non-empty Text keys: `window_age.process_name`, `subagent.tokens.suffix`, `labels.input`, ...; OD-178) | BC-2.01.005 |
| `empty path` / `home directory unknown` | path (BC-2.01.005 grammar; no dedicated class contract) | BC-2.01.005 |
| `exactly one backend entry until P6` | backends (BC-2.01.002 cardinality rule; no dedicated class contract) | BC-2.01.002 |

Numeric-range reason precedence by type (pass-7 D03/call 6; the four strings above are the
entire number-range vocabulary — no new string exists): the BC-2.02.002 check order is the
precedence, and the first applicable string wins. **Seconds keys** (BC-2.02.002 checks 1-3):
NaN/±Inf → `not finite`; value < 0 → `negative` (except the `git.ttl_s` exception, which
skips the check); value beyond the Duration ceiling or the `git.ttl_s` mirrored floor →
`out of range`. **Float keys** (BC-2.02.003 PC-5 registry-range check; the BC-2.02.002 order is the
precedence): non-finite parse →
`not finite`; value < 0 against a range whose floor is 0 or higher (`>= 0` or `> 0`) →
`negative`; breach of any other registered bound (below a positive minimum, above a
maximum) → `out of range`; value == 0 against a `> 0` range → `must be > 0`
(the last two swap only in which bound the value misses — a negative never reaches the
`must be > 0` check).
**Int keys** (BC-2.02.003 PC-5): the number-grammar class already rejects non-integer
parses (`not a number` / `not an integer`), so an Int never fires `not finite`; a value
below a registered `>= 0` floor → `negative`; every other registered-bound breach
(inclusive-exclusive bounds, e.g. `kv.cells = 0` against `1..100`) → `out of range`.
**Composite keys** (members checked member by member in declared order; the first failing
member produces the line): each member fires its own type's string — a non-finite member →
`not finite`, a member outside its per-member bound → `out of range` (or `must be > 0` for
an exclusive-positive member bound, e.g. a `scale` member at 0); the pair checks above are
the only ascending-pair number-range cases — one cross-KEY (`subagent.tokens.k_from <=
m_from`, two registry keys) and one INTRA-key composite (`cost.percentiles` member
`p75 <= p95`, both members of one key's JSON value; pass-8 A11).

Reconciliation with the closed register: the seven closed classes (OD-114 four + OD-134 +
OD-140 + Text by OD-178) are the classes with dedicated class contracts and D4-EX-3
table tests. The canonical D4-EX-3 table tests are `TestD4EX3_Boolean`, `TestD4EX3_Enum`,
`TestD4EX3_URL`, `TestD4EX3_Number` (range and grammar classes merged into one test;
pass-4 D22) and `TestD4EX3_Text` (OD-178); there is no Theme member (theme settings are
rejected by the corpus validator; pass-4 D22). Symmetrically, there is no `TestD4EX3_Text`
parity exclusion entry: Text-family keys (glyphs, labels, suffix, composites) likewise have
no legacy analog, so `TestD4EX3_Text` is a Go table test only, not a parity corpus case
(pass-6 call 1). The theme class keeps its dedicated class
contract BC-2.01.003. The vocabulary above also contains reasons raised under the same
E-CFG-001 surface by other contracts: the path-grammar reasons (`empty path`,
`home directory unknown`) come from BC-2.01.005 and the backends-cardinality reason from
BC-2.01.002 — each maps to its raising contract, not to an eighth class;
`control character` maps to the URL class when raised by BC-2.02.005 and to the theme
class when raised by BC-2.01.003, and to the Text class when raised for a non-theme
free-text key or a List entry (BC-2.01.005; pass-6 A14). The class register stays closed at seven.

## Severity Definitions

| Severity | Meaning | Exit Code Impact |
|----------|---------|-----------------|
| broken | Cannot render the requested output | zero exit with the degraded line (statusline), or non-zero in validate/usage/harness contexts |
| degraded | Partial result with stated fallback | zero exit |
| cosmetic | stderr-only detail | zero exit (stderr is never compared by the harness) |

## OD-156 numeric-overflow register (pass-2 remediation, 2026-11-17)

Owner ruling OD-156 splits numeric overflow by source. **Minted trigger ids CP-O01..CP-O11**
(CP-* style, new oVerflow family; CP-O10/O11 added by the pass-3 remediation, 2026-11-18)
and subagent ids CP-A01..A05 (CP-A04/A05 added by the pass-3 remediation) are listed here
for the BC agents: each owning BC must carry its trigger as an edge case + canonical vector.

**Surface 1 — stdin/metrics/cache-borne overflow at render: catalogued crash paths →
E-REN-002, the 29-byte degraded line, exit 0, earlier side-effect writes kept.** Legacy
analog: an exact JSON int above float64 max (~1.8e308; JSON permits 4,300 digits) meets a
float and CPython raises uncaught `OverflowError: int too large to convert to float`,
degrading the whole render (ADV-P2-B01/C01 evidence).

| Trigger id | Site (legacy SL) | Owning BC(s) | Trigger |
|-----------|------------------|--------------|---------|
| CP-O01 | context denominator (SL:435) | BC-1.02.006, BC-1.02.020 | huge exact int (`context_window_size`) enters `total/1e6` |
| CP-O02 | limits/countdown (SL:515) | BC-1.02.011, BC-1.02.012 | huge `resets_at` enters `reset − now` |
| CP-O03 | lines segment (SL:857) | BC-1.02.014 | huge int enters `n / 1e6` in `_fmt_lines` |
| CP-O04 | token segment (SL:866) | BC-1.02.025 | huge int enters `float(n)` in `_fmt_tok_c` |
| CP-O05 | window-age suffix (SL:558-559) | BC-1.02.017 | huge `total_duration_ms` enters `win_ms − dur` |
| CP-O10 | cost segment (SL:616, stdin bearer) / `cost_thresholds` (SL:255, history bearer) | BC-1.05.007, BC-1.05.005 (EC-011, history bearer) | huge exact int `usd` — stdin-borne it enters `f"{usd:.2f}"` at the render site (SL:616); history-borne it raises at the `usd / (api / 3.6e6)` division in `cost_thresholds` (SL:255) only — the percentile math never raises (int-to-float comparisons and `sorted` cannot overflow; pass-6 C2-13) — NOT at SL:616 (pass-5 C2-10) |
| CP-O11 | $/h burn-rate division (SL:622-623, stdin bearer) / `cost_thresholds` (SL:255, history bearer) | BC-1.05.007, BC-1.05.005 (EC-011, history bearer), BC-1.05.002 (EC-009, co-owner) | huge exact int `api_ms` — stdin-borne it enters `api_ms / 3.6e6` (SL:622-623); history-borne it raises at the `api / 3.6e6` division in `cost_thresholds` (SL:255) — including a huge positive recorded `api_ms` with a small `usd` (pass-5 C2-10) |
| CP-O12 | cost-pick equivalence (SL:626, SL:633) | BC-1.02.029 (owner), BC-1.05.003 (co-owner, the `⛏` value) | `tin` and `tout` each below the int→float overflow bound but their exact-int sum `tot` (SL:626) at or above it enters `tot * dgx_mtok` (SL:633) on the local lane with a valid basis → OverflowError → degraded line (render-time degrade, like CP-O04; pass-9 B03/call 4) |

CP-O10/O11 bearers (pass-4 B14/C2-10 anchor correction): SL:616 and SL:622-623 read the
stdin `cost` fields; the cost-history-borne raise happens in `cost_thresholds` at SL:255
(the history division; BC-1.05.005 EC-011), after record_cost persisted the huge exact int
earlier (SL:234-237) — not at SL:616/623. The `_hm` API-time-suffix helper (BC-1.02.016)
uses integer arithmetic only and cannot overflow. **OD-166 (owner, 2026-11-18) as ruled by
OD-169:** a cost value
(`usd` or `api_ms`) that cannot convert to float is **not recorded** in the cost history —
hylo's `record_cost` skips it where legacy persisted the raw int; the current refresh
still degrades per OD-156 (E-REN-002). The resulting cache-byte divergence is the
closed-set exclusion id `OD-166` (pass-4 ruling OD-169), scoped to cost-history bytes
written after such a refresh and nothing else; it has its own table test and a VP-012
closure row, and no longer rides the extended D4-EX-2 discipline.

**Surface 1 exception (OD-156, extending OD-137):** ints beyond int64 at the `_fmt_lines`
site are carried exactly via `math/big`, staying byte-exact where CPython itself renders
(`int(1e300)` is exact, SL:853/857 — no degrade); `pyfmt.Int` is exact beyond int64
matching ARCH-06 / BC-5.01.003, in agreement with BC-1.02.026 PC2 (pass-4 B19 — the
former "superseded int64 sketch" cross-reference, in both directions, is stale).

**Surface 2 — transcript-borne overflow: the offending line is skipped and the in-flight
turn is dropped (D4-EX-2 extension; sharpened by OD-167).** Hylo's W-predicate family
gains a numeric-overflow predicate: a transcript line whose numbers overflow float64
conversion is skipped whole (no partial mutation of parser state) and the in-flight turn
is dropped (OD-167), matching the D4-EX-2 skip discipline. Big integers beyond int64
accumulate exactly — there is **no** int64 accumulation-overflow skip (BC-1.03.006
EC-002). Legacy instead degrades sticky (nothing saved that refresh); the resulting
cache-byte divergence rides the extended D4-EX-2 entry — a claim scoped to the CP-O06..O08
skip family only: at the save-time CP-O09 site both sides write nothing and there is no
divergence (see its row; pass-5 A21). This resolves ADV-P2-C01
([owner-question]): the degrade is kept for parity by naming it, not by inventing
behavior.

| Trigger id | Site (legacy SL) | Owning BC(s) | Trigger |
|-----------|------------------|--------------|---------|
| CP-O06 | usage accumulation (SL:1108-1112, widened per BC-1.03.018; ADV-P4-C08) | BC-1.03.006 | `_i + _w`, a cached float `tin`, or the `c_*`/`tout` updates at SL:1109-1112 meet a 310+-digit `cache_creation_input_tokens` |
| CP-O07 | rebuild-excess check (SL:1117, `_w - max(0, prompt - pp) > REBUILD_EXCESS`) | BC-1.03.007 | `prompt - pp` with a huge exact int and a float operand on either side: a float `pp` meeting a huge int `prompt`, or the mirror case — a huge-int `pp` meeting a float `prompt` (ADV-P3-C03: this is the rebuild predicate, not the turn machine; mirror case added ADV-P4-C08) |
| CP-O08 | turn machine (SL:994/996; SL:996 unreachable at CP-O08 magnitudes; BC-1.03.010 EC-009) | BC-1.03.010, BC-1.03.016 | `TURN_STALE * out` or `out / span` with a huge exact int `out` |

**Surface 2 consequence — reachable in hylo (ADV-P3-C09; not moot):** two 4,300-digit
ints add without ever meeting a float, so no CP-O06..O08 skip fires and the accumulated
totals can still breach CPython's 4,300-digit int-to-string limit at the save.

| Trigger id | Site (legacy SL) | Owning BC(s) | Trigger |
|-----------|------------------|--------------|---------|
| CP-O09 | mix-cache save (SL:203-205) | BC-1.03.005, BC-1.03.006 | totals above CPython's 4,300-digit int-to-string limit fail `json.dump`; legacy swallows, writes nothing, leaves a partial temp — hylo reproduces the no-write. Both sides write nothing, so there is NO cache-byte divergence here; the observable difference is the leaked partial temp, covered by the `temp-file` exclusion (BC-6.03.003), not by D4-EX-2 (pass-5 A21) |

**Conversion threshold (verified on the pinned oracle, ADV-P3-C07):** CPython int→float
rounds to nearest and raises `OverflowError` only for `|n| >= 2**1024 - 2**970`;
`DBL_MAX + 1` as an exact int converts silently to `DBL_MAX`. Overflow predicates spelled
`|n| > DBL_MAX` over-skip and would skip lines legacy processes — test `DBL_MAX + 1`
against a float operand in the owning BCs' vectors.

**Surface 3 — subagent-panel crash paths (argv `--subagent` renderer): catalogued crash paths →
E-REN-002, the 29-byte degraded line, exit 0 (OD-156 ruling "like O2").** Legacy analog: a wrong-shape
task field raises uncaught TypeError/AttributeError inside the subagent renderer (BC-SL-097, P3r1 §A7),
and a huge exact int raises uncaught OverflowError at the two conversions below (ADV-P3-C04).

| Trigger id | Site (legacy SL) | Owning BC(s) | Trigger |
|-----------|------------------|--------------|---------|
| CP-A01 | subagent renderer (SL:1242-1245) | BC-1.07.008 | `tasks` truthy and not iterable (number, `true`) — TypeError at the `for task in tasks` step |
| CP-A02 | subagent renderer (SL:1242-1245) | BC-1.07.008 | a task's `status` unhashable (list/object) — TypeError at `_SUB_GLYPH.get(status, ...)` |
| CP-A03 | subagent renderer (SL:1242-1245) | BC-1.07.008, BC-1.07.006 | a task's `model` truthy and not a str while the configured prefix list is consulted — AttributeError at `startswith` |
| CP-A04 | subagent token segment `_fmt_tokens` (SL:878) | BC-1.07.007 | a huge exact int `tokenCount` passes the `isinstance`/`> 0` gate and raises OverflowError at `float(n)`; the helper catches only TypeError/ValueError, so the render degrades |
| CP-A05 | subagent elapsed clock (SL:919) | BC-1.07.007 | a huge exact int `startTime` raises OverflowError at `now_ms - start` |

Notes: OD-163 rules that a save removes only its own temp file (owns the CP-O09 partial
temp); OD-160 (`foreign-cache shapes`, ruling Q-b) is the exclusion id for foreign-form
cached values, OD-161 for an integer `transcript_path` (no transcript, never touch
foreign descriptors). The pass-3 rulings sharpen the register: **OD-166** - a cost value
(`usd` or `api_ms`) that cannot convert to float is not recorded in the cost history (the
refresh still degrades per OD-156); **OD-167** - a transcript-borne overflow skips the
line AND drops the in-flight turn; **OD-168** - a config error in `--subagent` mode
emits zero bytes on stdout with the reason lines on stderr. The closed exclusion set counts
twelve ids (D4-EX-1/2/3, OD-30, OD-76, `temp-file`, `cp-x03`, OD-159, OD-160, OD-161,
OD-166, OD-181): OD-169 added `OD-166` as a closed-set id of its own, scoped to cost-history bytes
written after a refresh whose `usd` or `api_ms` could not convert to float and nothing
else (own table test; VP-012 closure row), so the divergence no longer rides the
extended D4-EX-2 id — the transcript extension still does. The pass-6 ruling OD-181
(2026-11-18) added `OD-181` "metrics transport beyond plain http", scoped to non-http(s)
redirect targets (hylo: no sample) and https TLS trust-store differences (hylo: OS trust
store); parity metrics cases use plain http only, and Go table tests pin hylo's behaviour.

## Foreign-cache crash family CP-C01..C10 (named exclusion OD-160)

The foreign-cache family was minted by owner ruling **OD-160** (ruling Q-b,
owner-decisions-log-2026-11-14.md:144): foreign-form cached values are out of byte-parity
scope under the named exclusion id **OD-160**; vectors relying on hand-edited/foreign
caches are Go table tests, **not byte-parity** (on caches Go authored itself these shapes
are unreachable — the Go writer emits legacy's exact format). The family is catalogued
below in the same register shape as the other surfaces. **It lies outside the 49-path
crash register**, which counts the X/S/T/N/O/A families only (CP-X01..X04, CP-S01..S17,
CP-T01..T07 + T09, CP-N01..N03, CP-O01..O12, CP-A01..A05 = 4 + 17 + 8 + 3 + 12 + 5 = 49;
the T family counts 8 live ids — **CP-T08 is a RETIRED id** (withdrawn; the id is never
reused, per append-only numbering — pass-7 call 8/B03); the
C register is a separate, ninth register. **CP-C06 and CP-C07 are reserved**: minted by
the OD-160 closed-set label "CP-C01..C10" but not cited by any live BC or VP.

| Trigger id | Site (legacy SL) | Owning BC(s) | Trigger |
|-----------|------------------|--------------|---------|
| CP-C01 | session-cache load / `effective_rl` consult (SL:273-275, 307-312) | BC-1.01.009, BC-3.02.001 | session cache holds a JSON non-object (e.g. `[]`): the consult yields None or faults outside the load's try |
| CP-C02 | `effective_rl` short-circuit (SL:312) | BC-1.02.013, BC-1.01.009 | cached `rl_ts` a string while cached `rl` is an object — TypeError at the `isinstance(rl, dict) and` short-circuit |
| CP-C03 | metrics sample, rows >= 2 (SL:1217-1218) | BC-1.01.009 | wrong-shape metrics fetch result restored from the session cache |
| CP-C04 | metrics sample, rows >= 2 (SL:1217-1218) | BC-1.01.009 | wrong-shape `up` flag (`up: false` bearer) restored from the session cache |
| CP-C05 | sparkline history shaping (BC-1.04.003 EC-009) | BC-1.04.003 | a history Point is `[[0]]`-shaped (list of length 1) — IndexError |
| CP-C06 | — | reserved | not cited by any live BC/VP; reserved within the foreign-cache family (OD-160) |
| CP-C07 | — | reserved | not cited by any live BC/VP; reserved within the foreign-cache family (OD-160) |
| CP-C08 | badge/model/project, git segment (SL:441-462, 411) | BC-1.02.005, BC-1.01.009 | git cache foreign forms: cached `ts` a string (`"x"`) — TypeError; top-level JSON array (`[1,2]`) — AttributeError |
| CP-C09 | `record_cost` / cost-threshold step (SL:606-607) | BC-1.05.004, BC-1.05.005, BC-1.01.009 | corrupt cost history: top level not an object, or `sessions`/an entry not an object |
| CP-C10 | `record_cost` / cost-threshold step (SL:606-607) | BC-1.05.004, BC-1.05.005, BC-1.01.009 | cost-history entry `ts` non-numeric; within-step order exception: the record_cost write lands first, then the fault (BC-1.01.009) |

Family-level citations: BC-1.06.001 EC-001 (the cache loader) and BC-1.04.002 EC-008
(retention path) cite CP-C01..C10 as a class; VP-001 and VP-020 exercise CP-C09/C10 by
fault injection (out of parity scope; never-blank/exit-0 per DI-008).

## Crash-path register coverage

Every CP-S/CP-T/CP-N/CP-O/CP-A trigger resolves to E-REN-001 or E-REN-002 or a stated
widget fallback (Surface 2 transcript triggers resolve to the D4-EX-2 skip discipline for
CP-O06..O08 and to the legacy no-write save for CP-O09 — BC-1.03.006 PC5 — the save-time
difference being the `temp-file` exclusion, not a cache-byte divergence; pass-5 A21);
the per-trigger disposition lives in the owning BC (CP-S01..S17 in BC-1.02.x /
BC-1.01.x, CP-T01..T07 in BC-1.03.x, CP-T09 — the Windows MSVC localtime domain OSError
on a naive transcript timestamp (CP-T08 retired; every MSVC probe t, u1, u1 − 86400, u2
is domain-checked, so a naive wall time on or before 1970-01-01 and from year 3001
degrades the whole line) — in BC-5.04.001/ARCH-06, listed by BC-1.01.009 step 2 and
BC-1.01.001 PC3 (pass-7 call 8/B03), CP-N01/N02 in BC-1.04.x, CP-N03 — the metrics-borne
degrade: a numeric `__name__` key precedes every `vllm:` key in dict insertion order and
`k.startswith` raises AttributeError, SL:717 — in BC-1.04.x per the pass-4 design call 17,
CP-O01..O12 per the OD-156
register above, CP-A01..A05 per the Surface 3 register). The import/exit-time triggers
CP-X01/X02 are replaced by D4-EX-3 (BC-2.02.001) and CP-X03 is the named exclusion
`cp-x03` (BC-1.01.001 EC-005, OD-136); CP-X04 (signals) is out of scope. The
foreign-cache family CP-C01..C10 (register above) is governed by its named exclusion
OD-160 — the Python-side observable stays the standard degrade/guard ladder and the
Go-side obligation is Go table tests, never byte-parity — so its disposition is the
exclusion itself, not a register gap. A trigger whose
disposition is neither of those is a spec gap and fails the consistency check.
