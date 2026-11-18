---
document_type: remediation-plan
phase: 1d
pass: 5
date: 2026-11-18
source: adversarial-reviews/pass-5.md, adversarial-reviews/ADV-P5-INDEX.md
---

# Pass-5 remediation plan (canonical rulings and calls)

Every fix agent in the pass-5 burst reads this file first, and the pass-4 plan's rules section still applies (sibling sweep, python3 -I verification, isolated HOME, hygiene, English, no commits, frontmatter discipline). Values here are binding. Before relying on any call below, agents must not contradict a settled OD; if one seems to, stop and report it instead of applying it (lesson L-PG-13).

## Owner rulings (2026-11-18)

| ID | Ruling | Source |
|---|---|---|
| OD-176 | Convergence keeps the full VSDD standard: every finding of every severity is fixed each pass, and convergence needs three consecutive passes with only cosmetic findings. No severity gate, no scope freeze. | process question after pass 5 |
| OD-177 | Refines OD-171 to libc semantics on every OS: `TZ` unset → OS zone; `TZ` empty or unparseable → UTC. | A2-06, D23 |
| OD-178 | A seventh D4-EX-3 class **Text** covers composite-shape, pill-label, glyph and empty-text errors, with exact reason strings in the vocabulary and its own table test `TestD4EX3_Text`. Canonical D4-EX-3 tests become `TestD4EX3_Boolean`, `_Enum`, `_URL`, `_Number`, `_Text`. | D05, A06 |
| OD-179 | The reroute-all markers become the List key `statusline.lane.reroute_all_prefixes` (default `["claude", "claude-"]`, legacy). Range: every entry non-empty, no control bytes. | B09 |
| OD-180 | A metrics URL with userinfo reproduces legacy: no sample (the dead rung); no exclusion id. | C2-03 |

Next free OD: OD-181.

## Orchestrator calls (binding; each checked against the OD log)

1. **Glyph registry completion (A18, B03, C03, OD-02):** add members with legacy defaults: `statusline.glyphs.lane` (U+25E8, used by the main pill AND the subagent tag), `statusline.glyphs.git` (U+2387), `statusline.glyphs.cell_on` / `cell_off` (U+25B0 / U+25B1), `statusline.glyphs.cost_pick` (U+26CF), `statusline.glyphs.sparkline` (exactly 8 ordered glyphs, OD-02), and any row-2 dot/cell glyphs legacy prints (derive the full list from legacy/dgx_statusline.py; every literal printed glyph must be a member). Each member is 1 code point / 1 column except `sparkline` (8). The subagent lane tag words come from the OD-173 keys `statusline.pill.label_local` / `label_cloud` (BC-1.07.006 joins BC-1.02.001 as a consumer). The subagent token colour and the model/clock colour name their theme keys.
2. **Glyph renames (B04):** `statusline.glyphs.reroute` → `statusline.glyphs.cache_read` (U+27F3, SL:594); `statusline.glyphs.stale` → `statusline.glyphs.cache_rebuild` (U+21BB, SL:598-599). Not shipped, so no alias.
3. **Composite shapes match their defaults (A03, D06, D13, D07, A15):** each composite key's JSON shape is written out per key and must hold its default: `statusline.sparkline.scale` = array of 4 finite numbers `[k_top, v_floor, f_floor, other]`; `statusline.sparkline.colors` = object `{"trail":[r,g,b],"fade":[base,span],"amber":[r,g,b],"head":[r,g,b]}` (CORRECTED after the burst against legacy SL:683 `fade = 0.55 + 0.45 * i / max(len(pts)-2, 1)`: the two numbers are a base and a span, default `[0.55, 0.45]`, not a range); IntMap = object with exactly the keys `cc` and `other`, each a JSON integer (no fraction, no exponent) within int64, no extra keys, duplicate keys rejected; Float pairs name each element (e.g. bands = `[yellow, red]` with the meaning legacy gives them; derive from legacy, and state any ordering constraint legacy implies). Default-only composite keys: an env value equal to the default is accepted; any other value is a number-range config error (OD-162). Shape errors belong to the Text class (OD-178).
4. **`config path` exit codes (A01):** BC-2.03.002 is authoritative: exit 1 when a directory cannot be determined. ARCH-01, interface-definitions and the PRD add exit 1 for `config path`.
5. **Windows oracle env (A02):** BC-6.01.002 and BC-1.01.008 are authoritative (no PYTHON* except PYTHONPATH; strict UTF-8 parity locale; Windows keys TMP/TEMP/SYSTEMROOT plus the TZ=UTC pin). VP-034 and ARCH-07 align to them; the VP asserts the exact allowlisted key set.
6. **CI order and pin (A04, A17):** setup-python runs before the `go generate` staleness step; CI pins Python 3.11.7 exactly (ASM-001). The staleness job runs on ubuntu only, so the Windows Tier B leg needs no Python. release.yml gets the same setup-python + `HYLO_PARITY_PYTHON` as the test job.
7. **Frozen clock (D02):** `HYLO_TEST_NOW` is parsed to a float64 exactly as Python `float()` (within the BC grammar) and that float IS the `time.time()` value everywhere; it is never round-tripped through `time.Time` nanoseconds. `Env.Now` returns float seconds; `TimeFloat` applies only to the real clock.
8. **Windows `localtime` OSError (D01):** reproduce legacy: on Windows, a naive local time whose conversion makes MSVC raise OSError (before 1970-01-01 or from year 3001) degrades the line exactly as legacy does; the rule lives in `internal/platform` with a table test. No exclusion id.
9. **JSON-escaped placeholders (D03):** the harness substitutes placeholders only inside JSON string values and inserts the path JSON-escaped (backslashes and control bytes escaped); captured-snapshot splices follow the same rule. A Windows table test proves a path with `\U` and `\t` round-trips.
10. **Encoder depth per site (D08, D17):** measure (python3 -I, temp dir, never the real HOME) the encode depth boundary at every legacy encode site: `save_cache` via `json.dump` for the session, mix, git and cost-history caches, and the `json.dumps` in `_mix_counts`. Pin each in the owning BC. `Dumps`/`DumpsLen` take a depth budget and return `ErrDepth`; ARCH-06 adds `ErrDepth`. Reconcile the decoder and encoder depth laws so a shallower stack never has the smaller budget.
11. **NaN-aware comparisons (D09):** pyfmt adds `NumLT/NumLE/NumGT/NumGE/NumEQ` with Python semantics (any NaN operand → false, except `!=`); `NumCmp` is defined only for ordered operands. Every cross-kind comparison site uses the relational helpers.
12. **Number-class legacy behaviour (D04):** legacy crashes at import only for grammar failures (`""`, `four`, `0x4`, rows `2.0`); `nan`, `inf`, `-1`, `1e400`, `4_0` and non-ASCII digits parse at SL:74 and legacy renders normally. BC-6.03.004 PC-3 is corrected per value.
13. **OD-167 scope (C01, C02):** the in-flight turn is dropped on every transcript-borne overflow skip (CP-O06, CP-O07 and CP-O08), as OD-167 says. BC-1.03.018 PC2/PC4 get the OD-167 exception in the delete-the-line oracle; vectors gain timestamps so `cur` is observable.
14. **Manual redirect loop (C2-01, C2-02):** the metrics client uses `CheckRedirect` returning `http.ErrUseLastResponse` and drives the hops itself, so it can apply urllib's rules exactly: `location` then `uri`; an empty `Location` redirects to the original URL; normalization `quote(url, encoding="iso-8859-1", safe=string.punctuation)` after `urlunparse`, then `urljoin` (verified in CPython 3.11.7 source); `ftp` and other schemes outside http/https give no sample.
15. **Test names (C2-05, C2-06):** OD-30 = `TestCostHistory_OD30_NumericSidStringKey`; OD-166 = `TestCostHistory_OD166_RecordGuard`. Every BC, VP and index uses these.
16. **Ranges:** `burn_min_api_ms` and the `rate_min_api_ms` values: `> 0` (C2-08). `statusline.sparkline.preempt_marker_above`: Float (it compares a per-second rate), default 0, `>= 0` (C2-11). Caps (A13, NFR-005, judgment calls): `transcript.read_cap_bytes` 1..67108864 (64 MiB), `transcript.dedup_memory` 1..65536, `sparkline.history_cap` 1..1000. `statusline.context.cells` clamping vs rejection (B15): out-of-range is a config error, never a clamp.
17. **Tier C exclusions (A2-09):** Tier C generators exclude ruled-class inputs by construction; each constraint is named after its closed-set id and table-tested; any Tier C divergence is a failure. No runtime classifier.
18. **Test fixture paths (A2-16):** parity tests resolve fixtures from the module root (walk up to `go.mod`, helper named in ARCH-07), never by cwd-relative path.
19. **Line-number anchors into ARCH docs (C11, C2-14):** replace with stable fragment anchors (`#subagent`, `#cost`, `#telemetry`, ...); ARCH-03's anchor rule stays.
