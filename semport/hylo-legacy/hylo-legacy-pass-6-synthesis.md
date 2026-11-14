# Codebase Synthesis: hylo-legacy (broad sweep, passes 0-5)

<!-- validated 2026-11-14: fresh-context cross-check against legacy/ source (static, read-only).
     All eight "owner decision" quirks below verified (one reworded: LOCAL_MODEL_PREFIXES has
     three consumer defaults, two distinct values). No hallucinated identifiers found.
     See hylo-legacy-extraction-validation.md. -->


## Executive Summary

`legacy/` is a 3,181-line, 11-file Python/zsh prototype (`claude-dgx`) with no shared library and no tests. Five
runtime components talk only through files, env vars and HTTP: a zsh launcher builds env and `--settings` for
Claude Code and starts one mitmproxy addon per window; the addon (`dgx_proxy.py`, 764 lines) routes `/v1/messages`
by a case-sensitive model-prefix rule (Sonnet -> local backend, everything else and any server-tool request ->
Anthropic), normalizes DGX-bound bodies, taps SSE for usage, and appends an 11-event-type JSONL ledger; a
Prometheus exporter re-derives counters from the whole ledger; a per-refresh status line (1,245 lines, the P1
target) renders two rows from stdin + an incremental transcript parser + one VictoriaMetrics (MetricsQL) query +
four cache files; a Stop hook polices language and fake stops via an optional Kev oracle with a regex fallback.
The status line is the best-specified part (21 widgets reviewed with recorded cases); the proxy, exporter and
hook have no recorded verification at all.

## Key Findings

1. **Parity is a byte-level problem, not a logic problem.** The statusline logic is small, but its output depends
   on Python-specific semantics: `round()` banker's rounding (`dgx_statusline.py:1171`), Python `json.dumps`
   byte lengths inside the composition counter (`:1138,1140,1147`), code-point `len()` for width and text
   (`:153,1122,1143-1145`). Verified in a scratchpad: Go `math.Round(12.5)=13` vs Python `round(12.5)=12`;
   Go `json.Marshal` emits `1`, `0.00005`, raw `é`, `<` where Python emits `1.0`, `5e-05`, `é`, `<`;
   Go `len("⚡")=3` vs Python 1. (`%.0f`/`%.2f` agreed on the tested ties: both half-even.)
2. **The ledger is underspecified by its own consumers.** Field semantics differ by lane (`in_tok` = uncached
   input on Anthropic, whole prompt on DGX, `dgx_proxy.py:261-268`); `model_served` equals the *requested*
   model (`:144` before `:147`); `req_bytes` counts characters (`:123`); `bridge_ws_close` fires at upgrade with
   `duration_s` always `0.0` (`:213`). D7 freezes these as-is.
3. **Three exporter metrics are silently constant** and D7 freezes them: `dgx_llm_anthropic_requests_total`
   always has `account="unknown"` (`anth_request` has no `account`, exporter `:161-162`);
   `dgx_llm_anthropic_request_duration_seconds_{sum,count}` are always 0 (`anth_usage` has no `duration_s`,
   exporter `:179-182`); `dgx_llm_session_tokens_in/out/errors` lack HELP/TYPE (`:376-387`).
4. **The prefix rule is defined three times with two distinct default values** (proxy `claude-sonnet`, statusline `""`,
   backfill `claude-sonnet`), and the launcher sources `profile.env` *after* starting the proxy
   (`claude-dgx:75` vs `:115`), so a profile change to routing env reaches the status line but not the proxy.
5. **The "every path exits 0" guarantee has holes.** Import-time `float()/int()` of `DGX_SL_TTL`/`DGX_SL_ROWS`
   (`dgx_statusline.py:74-75`) crash before the guard; the same pattern exists in the hook and exporter; the
   trust CLI's `remove`/`rotate` always crash (`dgx_proxy.py:761` passes `None` as args). Telemetry also has a
   KEEP_DEAD bypass on the cached path (`:324-325`).

## Confidence Assessment

| Area | Confidence | Basis |
|---|---|---|
| Architecture | HIGH | every file read in full; interfaces quoted verbatim |
| Domain model / ledger schema | HIGH for field names and order; MEDIUM for runtime shapes (mitmproxy header order, real SSE payloads) | `ledger()` call sites enumerated |
| Behavioral contracts | HIGH-R for status line (review cases); MEDIUM elsewhere (code-read only, zero tests) | 136 BCs |
| NFRs / thresholds | HIGH for values (105, each with file:line); 52 rationales UNKNOWN | Pass 4 |
| Conventions / env / determinism | HIGH | 40 env inputs, determinism sources by file:line |

## Porting risks, ranked (byte-identical output threatened)

| # | Risk | Where | Go pitfall | Mitigation |
|---|---|---|---|---|
| R1 | Python `json.dumps` semantics used as a *measurement* (composition bytes) and as an *output* (ledger lines, hook stdout, DGX body re-serialization) | `dgx_statusline.py:1138,1140,1147`; `dgx_proxy.py:60,150`; `auto_continue.py:206` | `encoding/json`: compact separators, UTF-8 not `\uXXXX` (incl. surrogate pairs for astral chars), HTML escaping, sorted map keys, float formatting, float64 for big ints | write `pyjson` encoder: `", "`/`": "`, ensure_ascii with surrogate pairs, insertion order (ordered decode via `json.Decoder` tokens / `json.Number`), Python float `repr` |
| R2 | Rounding | `round()` at `dgx_statusline.py:1171,234`; `round(…,3)` `dgx_proxy.py:238,273`; backfill `:108` | `math.Round` is half-away-from-zero; `round(x, n)` on binary floats is "correctly rounded decimal" in Python | `math.RoundToEven` for `round(x)`; port CPython's `round(x, n)` algorithm (string-based) for n > 0; keep `%.Nf` (verified equal on ties) |
| R3 | Width, slicing and line splitting | `visible()` `:151-153`; `trim_to_fit` `:1193-1197`; `[:400]`, `[-800:]`, `[-6000:]`, `[-160:]` in hook; `str.splitlines` `auto_continue.py:177` | Go `len`/slicing are bytes; `strings.Split("\n")` vs Python's Unicode line boundaries (` `, `\x85`, `\x0b`, `\x0c`, `\x1c-\x1e`) | rune-based helpers; port `splitlines` boundary set; parity counts code points, not terminal cells |
| R4 | Regex | `auto_continue.py:24-28,177-180,184`; SSE `dgx_proxy.py:413` | RE2 has no lookbehind (verified compile error); `\b`/`\s`/IGNORECASE are ASCII-only in RE2 vs Unicode in Python (verified: `now\b` on `nowé` differs) | hand-written sentence splitter; Unicode-aware word-boundary helper; table tests with non-ASCII |
| R5 | Time and timezone | ledger `t` local naive (`dgx_proxy.py:60`), exporter naive parse (`:125`), `ps lstart` + `mktime` (`dgx_statusline.py:286`), `fromisoformat` naive fallback (`:983`) | Go `time.Parse` defaults to UTC; `time.Local` must be used to match; Python version-dependent `fromisoformat` | explicit `time.ParseInLocation(…, time.Local)`; pin `TZ`, `LC_ALL=C`, Python 3.11 in harness |
| R6 | Python duck typing and exception-driven output | `isinstance(x,(int,float))` accepts `bool` (`:420,540,602`); `int("12")` accepted (`:853`); type errors -> `statusline degraded` (`:1243`) | typed decode rejects or zeroes; Go never "raises" the same way | decode stdin to `any`; emulate Python truthiness/`isinstance`; enumerate which malformed inputs must produce `statusline degraded` |
| R7 | JSON parse leniency | `json.loads` on bytes rejects invalid UTF-8 (line skipped, `:1061-1063`), accepts `NaN`/`Infinity`, exact big ints | Go `encoding/json` replaces invalid UTF-8 with U+FFFD (line counted), rejects NaN | pre-validate UTF-8; custom NaN handling; `json.Number` |
| R8 | Float formatting in cache files shared during shadow/cutover | `save_cache` `json.dump` of floats (`:203`), cost history | Python `1.0` vs Go `1`; both must read each other's files | tolerant readers; Python-compatible writer |
| R9 | `colorsys.hsv_to_rgb` + `int()` truncation | `heat()` `:144-148`, sparkline fade `:682-683` | different float op order changes a truecolor byte | port CPython colorsys verbatim, same op order; table-test all 101 integer percentages |
| R10 | Incremental parse equivalence | 512 KB cap + long-line completion + 256-id memory (`:1032-1058,1153`) | refresh sequence and chunk boundaries must match exactly in the harness | harness replays identical refresh sequences on identical file growth |

## What P1 (`hylo statusline`) needs first

1. Harness determinism (Pass 5 §3): clock shim (`time.time` patched via harness `sitecustomize.py`; Go
   `HYLO_TEST_NOW`), `TZ=UTC`, `LC_ALL=C`, temp `HOME` per case, fake VictoriaMetrics serving canned
   `/api/v1/query` JSON (must accept the MetricsQL query string verbatim), seeded `proc_start` to bypass `ps`.
2. Python-compat primitives package (before any widget): `pyround` (half-even + `round(x,n)`), `pyfmt` (`%.Nf`,
   `{:>2d}`), `pyjson.Dumps` length-exact encoder, `pystr` (code-point len/slice, `splitlines`, `rsplit`),
   ANSI-strip regex, `colorsys`.
3. Widget order per `docs/RESUME.md` step 5, each with the BC-SL table tests from Pass 3 (53 BCs, 30+ HIGH-R).
4. Decide (owner) whether to preserve the KEEP_DEAD cached-path quirk (BC-SL-041) and the import-time crash
   (BC-SL-001) in parity, or whitelist them as known diffs.
5. Synthetic transcript generator covering: split messages with repeated usage, interleaved tool_result lines,
   `compact_boundary`, a > 512 KB line, invalid UTF-8 line, non-ASCII text (escape-length), nested images,
   empty thinking, cache rebuild, timestamps without `Z`.

## Gaps & Risks (to deepen in convergence rounds)

- Real mitmproxy behavior not observable statically: response-header iteration order (affects `anth_ratelimit`
  `headers` key order), what happens when `_key()` raises inside `request`, `get_text()` decoding of
  non-UTF-8 bodies, whether `response` fires for streamed SSE flows on the bridge.
- Real upstream SSE shapes: whether vLLM's/Anthropic's `message_delta` carries `usage.input_tokens` (BC-PX-017 —
  if not, `usage` is never set and no `*_usage` events are written).
- Stop-hook output acceptance by Claude Code for `additionalContext` on Stop (BC-HK-013).
- `ps` output on Linux/Windows; `comm` containing spaces (BC-SL-023).
- The external recording rules (`dgx_*:*` series) and THRESHOLDS §8b / ECONOMICS-BRIEF docs live outside the repo.
- 52 threshold rationales UNKNOWN (Pass 4).

## Inconsistencies found (cross-pass)

| # | Inconsistency | Evidence |
|---|---|---|
| I1 | Docstrings vs code: proxy docstring says passthrough is "untouched", but `Accept-Encoding` is forced on both lanes | `dgx_proxy.py:10` vs `:131` |
| I2 | `_SSETap` docstring says usage comes from `message_start`/`message_delta`; code sets `usage` only from top-level `usage` | `:363-366` vs `:418-420` |
| I3 | Exporter docstring lists 5 metrics; it exports 27 series families | exporter `:4-9` vs `:289-398` |
| I4 | WIDGETS doc says sparkline ≈ 48 s with 12 points; code keeps 90 s / 32 points and plots the last 12 | `STATUSLINE-WIDGETS.md` vs `dgx_statusline.py:82-84,350` (consistent in effect) |
| I5 | Hook docstring says Kev-0.8B; launcher comment says Kev-4B; model defaults differ (`kev-latest` vs pinned id) | `auto_continue.py:125`, `claude-dgx:149,155` |
| I6 | Account hint fallbacks differ between proxy and exporter (JSON non-dict input) | `dgx_proxy.py:326-336` vs exporter `:75-91` |
| I7 | Stale-span rule differs: statusline requires `out > 0`, backfill uses `max(out,1)` | `dgx_statusline.py:994` vs backfill `:78` |
| I8 | Mix cache sanitizes `session_id`, session cache does not | `:1017` vs `:1215` |
| I9 | Exporter tallies `[kev+opus-continue]`, which no current code emits | exporter `:221-222`; `opus_verdict` dead |
| I10 | Coordinator implements "one proxy per user" but is not wired; launcher runs one per window | `dgx-proxy-coordinator.sh` vs `claude-dgx:70-82` |
| I11 | Composition docstring (`:944`) says "≈tokens/4, the same heuristic the ledger exporter uses" — composition uses characters, exporter divides `req_bytes` (characters) by 4; consistent units, misleading wording | `:944` vs exporter `:193` |

## Recommendations for spec crystallization

- Spec the ledger as a frozen wire format (Pass 2 table) including key order, encoding and the quirks above;
  write a golden-line test per event type for P3.
- Spec the exporter output as a golden exposition text including the constant/irregular metrics (D7).
- Treat the Python-compat primitives as their own spec (they are the real P1 risk), with property tests vs a
  Python oracle in the harness.
- Get owner rulings on: the 52 UNKNOWN thresholds (comments required by CLAUDE.md), the KEEP_DEAD quirk,
  import-time crashes, trust CLI bug, `x-api-key` forwarding, exporter `0.0.0.0` bind — list them as
  "post-parity changes" rather than fixing during the port (D4).

## State Checkpoint
```yaml
pass: 6
status: complete
files_scanned: 11
timestamp: 2026-11-14T05:09:24Z
next_pass: convergence-deepening (passes 2 and 3 first)
```
