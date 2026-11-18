---
document_type: prd-supplement-error-taxonomy
level: L3
version: "1.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:38:15Z
phase: 1a
stage: "3 of 3 (integration)"
inputs: [prd.md]
input-hash: "c2ae96e"
traces_to: prd.md
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
| CFG | Configuration | D4-EX-3 invalid `HYLO_*` values (six classes) |
| CLI | Command-line | unknown flags, usage errors |
| VAL | Validation | `config validate` reporting |
| NET | Metrics transport | metrics store unreachable/500/garbage |
| FS  | Filesystem | cache load/save faults, failed replaces |
| HAR | Harness integrity | canary, exclusion machinery, corpus hygiene (harness process only) |

## Error Catalog

| Error Code | Category | Severity | Exit Code | Observable / Message Format |
|-----------|----------|----------|-----------|----------------------------|
| E-REN-001 | REN | broken | 0 | `\e[90mstatusline degraded\e[0m\n` (29 bytes) — BC-1.01.001. Failure of the degraded-line write itself (legacy CP-X03, stdout closed) is the named exclusion `cp-x03` (OD-136): Go swallows the write error and still exits 0, per DI-008 |
| E-REN-002 | REN | broken | 0 | same line, via typed CP-* degrades (overflow/NaN/type confusion): CP-S01..S17, CP-N01/N02, the OD-156 Surface 1 overflow family CP-O01..O05 and CP-O10/O11, and the Surface 3 subagent family CP-A01..A05 (the Surface 2 transcript family CP-O06..O09 resolves to the D4-EX-2 skip discipline, not a line degrade) — BC-1.02.026/.027, BC-1.02.020, BC-1.04.014/.015, BC-1.03.015, BC-1.05.007, BC-1.07.007/.008 |
| E-CFG-001 | CFG | degraded | 0 | `\e[90mhylo: config error: <key>=<value> (<reason>)\e[0m\n`; stderr detail `[from <ENVNAME>]` — BC-2.02.001 |
| E-CLI-001 | CLI | degraded | 0 | `\e[90mhylo: unknown flag <flag>\e[0m\n` — BC-4.01.002 |
| E-CLI-002 | CLI | broken | 2 | golden usage text on stderr — BC-4.01.001 |
| E-VAL-001 | VAL | broken | 1 | plain reason lines (no SGR), one per error — BC-2.03.001 |
| E-NET-001 | NET | degraded | 0 | freshness ladder down to the stale suffix — BC-1.04.001/.004 |
| E-FS-001 | FS | degraded | 0 | never-raise caches; failed replace persists nothing — BC-1.06.001/.002 |
| E-HAR-001 | HAR | broken | non-zero | harness FAIL naming the reason (canary, missing table test, glob, id outside closed set) — BC-6.01.003, BC-6.03.004 |

## D4-EX-3 config-error line (E-CFG-001) in detail

Format (BC-2.02.001, OD-102): `\e[90m` + `hylo: config error: ` + `<key>` + `=` +
`<value>` + ` (` + `<reason>` + `)` + `\e[0m` + `\n`. Exactly one line on stdout — the
first error in stable registry order; the full list goes to stderr; a config-error run
writes no caches. `<key>` is the dotted config name (not the env var); `<value>` is
escaped with control bytes and invalid UTF-8 as `\xNN`. In `--subagent` mode a config
error emits **zero bytes on stdout**; the reason lines go to stderr (OD-168).

Classes and owner rulings: number-range (BC-2.02.002; OD-114 keeps TTL 0 valid, contra
IM-16; every registry key declares a range and an out-of-range value is a number-range
config error — OD-162; int64-overflow and Duration-ceiling values are number-range cases —
OD-164), number-grammar (BC-2.02.003), enum (BC-2.02.004), URL (BC-2.02.005), boolean
(BC-2.02.006; OD-140 — dedicated class contract; grammar pinned in BC-2.01.005), theme/SGR
(BC-2.01.003 — reason string `not an SGR parameter list`, named class per OD-134, resolving
PRD OQ-6). The class register is closed at six (OD-114 four + OD-134 + OD-140); a seventh
class needs an owner decision. Unknown-flag precedence: E-CLI-001 is checked before
E-CFG-001.

## Reason Vocabulary (exact strings, BC-2.02.001)

| Reason | Class | Raised by |
|--------|-------|-----------|
| `underscore in numeral` | number-grammar | BC-2.02.003 |
| `non-ASCII digit` | number-grammar | BC-2.02.003 |
| `not a number` / `not an integer` | number-grammar | BC-2.02.003 |
| `not finite` / `negative` / `must be > 0` / `out of range` | number-range | BC-2.02.002/.003 |
| `not a boolean (true\|false\|1\|0\|yes\|no)` | boolean | BC-2.01.005 |
| `unknown value (<v1>\|<v2>\|...)` | enum | BC-2.02.004 |
| `scheme must be http or https` / `not a URL` / `missing host` | URL | BC-2.02.005 |
| `control character` | URL (BC-2.02.005) / theme (BC-2.01.003) | BC-2.02.005, BC-2.01.003 |
| `not an SGR parameter list` | theme | BC-2.01.003 |
| `empty path` / `home directory unknown` | path (BC-2.01.005 grammar; no dedicated class contract) | BC-2.01.005 |
| `exactly one backend entry until P6` | backends (BC-2.01.002 cardinality rule; no dedicated class contract) | BC-2.01.002 |

Reconciliation with the closed register: the six closed classes (OD-114 four + OD-134 +
OD-140) are the classes with dedicated class contracts and D4-EX-3 table tests. The
vocabulary above also contains reasons raised under the same E-CFG-001 surface by other
contracts: the path-grammar reasons (`empty path`, `home directory unknown`) come from
BC-2.01.005 and the backends-cardinality reason from BC-2.01.002 — each maps to its raising
contract, not to a seventh class; `control character` maps to the URL class when raised by
BC-2.02.005 and to the theme class when raised by BC-2.01.003. The class register stays
closed at six.

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
| CP-O10 | cost segment (SL:616) | BC-1.05.007 | huge exact int `usd` from the cost history enters `f"{usd:.2f}"` (int-to-float conversion) |
| CP-O11 | API-time suffix (SL:623) | BC-1.05.007 | huge exact int `api_ms` from the cost history enters `api_ms / 3.6e6` |

CP-O10/O11 bearer: the cost-history cache (record_cost persisted the huge exact int
earlier, SL:234-237), so every later refresh on that lane whose entry passes the API-time
gate raises at the same sites (ADV-P3-C2-01). **OD-166 (owner, 2026-11-18):** a cost value
(`usd` or `api_ms`) that cannot convert to float is **not recorded** in the cost history —
hylo's `record_cost` skips it where legacy persisted the raw int; the current refresh
still degrades per OD-156 (E-REN-002). The cache-byte divergence cites OD-166 and rides
the extended D4-EX-2 discipline; the closed ten-id exclusion set is unchanged.

**Surface 1 exception (OD-156, extending OD-137):** ints beyond int64 at the `_fmt_lines`
site are carried exactly via `math/big`, staying byte-exact where CPython itself renders
(`int(1e300)` is exact, SL:853/857 — no degrade); the int64-typed `pyfmt.Int` sketch in
BC-1.02.026 PC2 is superseded by this ruling — `Int` is exact beyond int64, matching
ARCH-06 / BC-5.01.003.

**Surface 2 — transcript-borne overflow: the offending line is skipped and the in-flight
turn is dropped (D4-EX-2 extension; sharpened by OD-167).** Hylo's W-predicate family
gains a numeric-overflow predicate: a transcript line whose numbers overflow float64
conversion is skipped whole (no partial mutation of parser state) and the in-flight turn
is dropped (OD-167), matching the D4-EX-2 skip discipline. Big integers beyond int64
accumulate exactly — there is **no** int64 accumulation-overflow skip (BC-1.03.006
EC-002). Legacy instead degrades sticky (nothing saved that refresh); the resulting
cache-byte divergence rides the extended D4-EX-2 entry. This resolves ADV-P2-C01
([owner-question]): the degrade is kept for parity by naming it, not by inventing
behavior.

| Trigger id | Site (legacy SL) | Owning BC(s) | Trigger |
|-----------|------------------|--------------|---------|
| CP-O06 | usage accumulation (SL:1108) | BC-1.03.006 | `_i + _w`, or a cached float `tin`, meets a 310+-digit `cache_creation_input_tokens` |
| CP-O07 | rebuild-excess check (SL:1117, `_w - max(0, prompt - pp) > REBUILD_EXCESS`) | BC-1.03.007 | `prompt - pp` with a float `pp` and a huge exact int (ADV-P3-C03: this is the rebuild predicate, not the turn machine) |
| CP-O08 | turn machine (SL:994/996) | BC-1.03.010, BC-1.03.016 | `TURN_STALE * out` or `out / span` with a huge exact int `out` |

**Surface 2 consequence — reachable in hylo (ADV-P3-C09; not moot):** two 4,300-digit
ints add without ever meeting a float, so no CP-O06..O08 skip fires and the accumulated
totals can still breach CPython's 4,300-digit int-to-string limit at the save.

| Trigger id | Site (legacy SL) | Owning BC(s) | Trigger |
|-----------|------------------|--------------|---------|
| CP-O09 | mix-cache save (SL:203-205) | BC-1.03.005, BC-1.03.006 | totals above CPython's 4,300-digit int-to-string limit fail `json.dump`; legacy swallows, writes nothing, leaves a partial temp — hylo reproduces the no-write, and the cache-byte divergence rides the extended D4-EX-2 entry |

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
emits zero bytes on stdout with the reason lines on stderr. The closed ten-id exclusion
set (D4-EX-1/2/3, OD-30, OD-76, `temp-file`, `cp-x03`, OD-159, OD-160, OD-161) is
unchanged by OD-156 and the pass-3 rulings — the transcript extension rides the existing
D4-EX-2 id.

## Crash-path register coverage

Every CP-S/CP-T/CP-N/CP-O/CP-A trigger resolves to E-REN-001 or E-REN-002 or a stated
widget fallback (Surface 2 transcript triggers resolve to the D4-EX-2 skip discipline);
the per-trigger disposition lives in the owning BC (CP-S01..S17 in BC-1.02.x /
BC-1.01.x, CP-T01..T07 in BC-1.03.x, CP-N01/N02 in BC-1.04.x, CP-O01..O11 per the OD-156
register above, CP-A01..A05 per the Surface 3 register). The import/exit-time triggers
CP-X01/X02 are replaced by D4-EX-3 (BC-2.02.001) and CP-X03 is the named exclusion
`cp-x03` (BC-1.01.001 EC-005, OD-136); CP-X04 (signals) is out of scope. A trigger whose
disposition is neither of those is a spec gap and fails the consistency check.
