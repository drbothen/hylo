---
document_type: bc-component-map
level: L3
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-17T22:30:00Z
phase: 1b
inputs: [prd.md, behavioral-contracts/BC-INDEX.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "e197094"
traces_to: ../prd.md

---

# BC-COMPONENT-MAP: hylo P1 (154/154)

> One row per behavioral contract: component home (package/file) + governing ARCH
> section. Homes follow the design doc §8 mapping under the new BC ids; titles here are
> abbreviated — the BC file H1 (BC-INDEX.md) is the title source of truth. `sl/` =
> `internal/statusline`, `py/` = `internal/pyfmt`, `cfg/` = `internal/config`,
> `plat/` = `internal/platform`, `cost/` = `internal/cost`, `par/` = `internal/parity`,
> `cmd/` = `cmd/hylo`.

## S1 — Status Line (101)

### S1.01 Input/output contract

| BC | Component | ARCH |
|---|---|---|
| BC-1.01.001 | sl/guard.go (29-byte degraded line, recover backstop) | ARCH-03 |
| BC-1.01.002 | sl/input.go (stdin decode, {} fallback) | ARCH-03 |
| BC-1.01.003 | sl/statusline.go (rows, LF join, width rule) | ARCH-03 |
| BC-1.01.004 | sl/width.go (visible width, SGR strip) | ARCH-03 |
| BC-1.01.005 | sl/width.go (COLUMNS grammar via py.ParseInt) | ARCH-03 |
| BC-1.01.006 | sl/width.go (trim_to_fit double reset) | ARCH-03 |
| BC-1.01.007 | sl/width.go (negative COLUMNS) | ARCH-03 |
| BC-1.01.008 | sl/input.go (strict UTF-8 stdio) | ARCH-03 |
| BC-1.01.009 | sl/statusline.go (side-effect order) | ARCH-03 |
| BC-1.01.010 | sl/width.go (trim breakpoint matrix) | ARCH-03 |

### S1.02 Row-1 widgets

| BC | Component | ARCH |
|---|---|---|
| BC-1.02.001 | sl/lane.go (prefix startswith pill) | ARCH-03 |
| BC-1.02.002 | sl/lane.go (model label chain) | ARCH-03 |
| BC-1.02.003 | sl/lane.go (project basename) | ARCH-03 |
| BC-1.02.004 | sl/git.go (.git/HEAD walk; py sha1 key) | ARCH-03 |
| BC-1.02.005 | sl/git.go (5 s TTL git cache) | ARCH-03 |
| BC-1.02.006 | sl/context.go (thermometer, denominator) | ARCH-03 |
| BC-1.02.007 | sl/context.go (half-even percentage) | ARCH-03 |
| BC-1.02.008 | sl/context.go (cache-hit segment) | ARCH-03 |
| BC-1.02.009 | sl/limits.go (reroute-all hides limits) | ARCH-03 |
| BC-1.02.010 | sl/limits.go (expired window unreported) | ARCH-03 |
| BC-1.02.011 | sl/limits.go (pace/absolute bands) | ARCH-03 |
| BC-1.02.012 | sl/limits.go (countdown, 1.15 gate) | ARCH-03 |
| BC-1.02.013 | sl/limits.go (smoothing 1800 s + session cache) | ARCH-03 |
| BC-1.02.014 | sl/session.go (_fmt_lines) | ARCH-03 |
| BC-1.02.015 | sl/session.go (_hm) | ARCH-03 |
| BC-1.02.016 | sl/session.go (API-time suffix) | ARCH-03 |
| BC-1.02.017 | sl/session.go (⌂ gate) | ARCH-03 |
| BC-1.02.018 | sl/tokens.go (_fmt_tok_c) | ARCH-03 |
| BC-1.02.019 | sl/context.go (heat HSV; arm64) | ARCH-03 |
| BC-1.02.020 | sl/context.go (thermometer quirks) | ARCH-03 |
| BC-1.02.021 | sl/lane.go (str() of non-str) | ARCH-03 |
| BC-1.02.022 | sl/lane.go (POSIX normpath //) | ARCH-03 |
| BC-1.02.023 | sl/context.go (cache-hit NaN/inf) | ARCH-03 |
| BC-1.02.024 | sl/limits.go (0.9 pace boundary) | ARCH-03 |
| BC-1.02.025 | sl/tokens.go (no unit promotion) | ARCH-03 |
| BC-1.02.026 | sl/session.go (CP-S11 degrade) | ARCH-03 |
| BC-1.02.027 | sl/session.go (CP-S12/S13 degrade) | ARCH-03 |
| BC-1.02.028 | sl/session.go (window-age duration; big via OD-137) | ARCH-03 |
| BC-1.02.029 | sl/cost.go (pick eq 0.005) | ARCH-03 |
| BC-1.02.030 | sl/limits.go (effective_rl, sticky CP-S09) | ARCH-03 |

### S1.03 Transcript parsing

| BC | Component | ARCH |
|---|---|---|
| BC-1.03.001 | sl/transcript.go (no path -> no state) | ARCH-03 |
| BC-1.03.002 | sl/mixcache.go (name, mixv6 reset) | ARCH-03 |
| BC-1.03.003 | sl/transcript.go (512 KB step) | ARCH-03 |
| BC-1.03.004 | sl/transcript.go (splitlines + per-line decode) | ARCH-03 |
| BC-1.03.005 | sl/transcript.go (dedup 256) | ARCH-03 |
| BC-1.03.006 | sl/transcript.go (usage accumulation; py.Num) | ARCH-03 |
| BC-1.03.007 | sl/transcript.go (rebuild 20,000) | ARCH-03 |
| BC-1.03.008 | sl/transcript.go (compact_boundary reset) | ARCH-03 |
| BC-1.03.009 | sl/transcript_mix.go (dumps lengths) | ARCH-03 |
| BC-1.03.010 | sl/transcript_turn.go (rate machine) | ARCH-03 |
| BC-1.03.011 | sl/transcript.go (first-line usage) | ARCH-03 |
| BC-1.03.012 | sl/transcript.go (two-refresh completion) | ARCH-03 |
| BC-1.03.013 | sl/mixcache.go (sid sanitize) | ARCH-03 |
| BC-1.03.014 | sl/transcript_mix.go (block value types) | ARCH-03 |
| BC-1.03.015 | sl/transcript.go (int = no transcript, OD-161; no descriptor I/O) | ARCH-03 |
| BC-1.03.016 | sl/transcript_turn.go (20-row table) | ARCH-03 |
| BC-1.03.017 | sl/transcript_turn.go (turn identity) | ARCH-03 |
| BC-1.03.018 | sl/transcript_wshape.go (W-predicates) | ARCH-03 |
| BC-1.03.019 | sl/transcript_wshape_test.go (21 rows) | ARCH-03 |
| BC-1.03.020 | sl/mixcache.go (OD-32 reader rule) | ARCH-03 |
| BC-1.03.021 | sl/mixcache.go (t0 null, out verbatim) | ARCH-03 |

### S1.04 Row-2 telemetry

| BC | Component | ARCH |
|---|---|---|
| BC-1.04.001 | sl/telemetry.go (query, total deadline, first-wins) | ARCH-03 |
| BC-1.04.002 | sl/sample.go (TTL/KEEP_DEAD) | ARCH-03 |
| BC-1.04.003 | sl/sample.go (history points) | ARCH-03 |
| BC-1.04.004 | sl/row2.go (freshness ladder) | ARCH-03 |
| BC-1.04.005 | sl/row2.go (health dot) | ARCH-03 |
| BC-1.04.006 | sl/row2.go (queue) | ARCH-03 |
| BC-1.04.007 | sl/row2.go (KV) | ARCH-03 |
| BC-1.04.008 | sl/row2.go (throughput) | ARCH-03 |
| BC-1.04.009 | sl/sparkline.go (glyphs/scale/colors) | ARCH-03 |
| BC-1.04.010 | sl/row2.go (TTFT) | ARCH-03 |
| BC-1.04.011 | sl/row2.go (power) | ARCH-03 |
| BC-1.04.012 | sl/row2.go (idle) | ARCH-03 |
| BC-1.04.013 | sl/statusline.go (ROWS >= 2 fetch) | ARCH-03 |
| BC-1.04.014 | sl/sparkline.go (CP-N02) | ARCH-03 |
| BC-1.04.015 | sl/row2.go (CP-N01, cell math) | ARCH-03 |
| BC-1.04.016 | sl/row2.go (NaN/inf, wall mismatch) | ARCH-03 |
| BC-1.04.017 | sl/row2.go (idle > 300, age format) | ARCH-03 |
| BC-1.04.018 | sl/row2.go (mine) | ARCH-03 |
| BC-1.04.019 | sl/row2.go (TTFT boundaries) | ARCH-03 |
| BC-1.04.020 | sl/sample.go (11-step pinned seq) | ARCH-03 |
| BC-1.04.021 | sl/sample.go (HIST_MIN_GAP) | ARCH-03 |

### S1.05 Cost history + colors

| BC | Component | ARCH |
|---|---|---|
| BC-1.05.001 | sl/cost.go ($ percentile colors) | ARCH-03 |
| BC-1.05.002 | sl/cost.go ($/h thresholds) | ARCH-03 |
| BC-1.05.003 | sl/cost.go (⛏ in $ block) | ARCH-03 |
| BC-1.05.004 | cost/history.go (throttled write) | ARCH-03 |
| BC-1.05.005 | cost/history.go (p75/p95; NaN usd OD-138) | ARCH-03 |
| BC-1.05.006 | cost/history.go (numeric sid, OD-30) | ARCH-03 |
| BC-1.05.007 | sl/cost.go ($, $/h formats) | ARCH-03 |
| BC-1.05.008 | sl/cost.go + cost/history.go (goldens) | ARCH-03 |
| BC-1.05.009 | cost/history.go (exact write format) | ARCH-03 |

### S1.06 Session caches

| BC | Component | ARCH |
|---|---|---|
| BC-1.06.001 | sl/cache.go (never-raise, raw sid) | ARCH-04 |
| BC-1.06.002 | sl/cache.go (failed replace, temp handling) | ARCH-04 |

### S1.07 Subagent panel (OD-155)

| BC | Component | ARCH |
|---|---|---|
| BC-1.07.001 | cmd/hylo + sl/subagent.go (`--subagent` argv routing per ARCH-01 `runStatuslineSubagent`; panel body) | ARCH-03, ARCH-01 |
| BC-1.07.002 | sl/subagent.go (enabled off switch, default true) | ARCH-03 |
| BC-1.07.003 | sl/subagent.go (total stdin: unparseable ⇒ zero rows) | ARCH-03 |
| BC-1.07.004 | sl/subagent.go (one line per eligible task) | ARCH-03 |
| BC-1.07.005 | sl/subagent.go (status glyph, name fallback, settled suffix) | ARCH-03 |
| BC-1.07.006 | sl/subagent.go (model-prefix lane tag) | ARCH-03 |
| BC-1.07.007 | sl/subagent.go (_fmt_tokens, running-only elapsed) | ARCH-03 |
| BC-1.07.008 | sl/subagent.go (CP-A01..A05 degrade, 29-byte line) | ARCH-03 |

## S2 — Configuration (13)

| BC | Component | ARCH |
|---|---|---|
| BC-2.01.001 | cfg/load.go (env -> defaults) | ARCH-02 |
| BC-2.01.002 | cfg/statusline_keys.go (backends[0] validator) | ARCH-02 |
| BC-2.01.003 | cfg/statusline_keys.go (theme keys, SGR class) | ARCH-02 |
| BC-2.01.004 | cfg/registry.go (key registry) | ARCH-02 |
| BC-2.01.005 | cfg/types.go (value grammars) | ARCH-02 |
| BC-2.02.001 | cfg/errors.go (D4-EX-3 line) | ARCH-02 |
| BC-2.02.002 | cfg/errors.go (number-range class) | ARCH-02 |
| BC-2.02.003 | cfg/errors.go (number-grammar class) | ARCH-02 |
| BC-2.02.004 | cfg/errors.go (enum class) | ARCH-02 |
| BC-2.02.005 | cfg/errors.go (URL class) | ARCH-02 |
| BC-2.02.006 | cfg/errors.go (boolean class) | ARCH-02 |
| BC-2.03.001 | cmd/hylo/config.go (validate exit 1) | ARCH-01 |
| BC-2.03.002 | cmd/hylo/config.go (path printing, OD-132) | ARCH-01 |

## S3 — Platform (3)

| BC | Component | ARCH |
|---|---|---|
| BC-3.01.001 | plat/paths*.go (per-OS dirs, OD-144) | ARCH-05 |
| BC-3.02.001 | plat/proc.go + proc_*.go (ancestor probe) | ARCH-05 |
| BC-3.02.002 | plat/proc_*.go (named per-OS edges) | ARCH-05 |

## S4 — CLI (3)

| BC | Component | ARCH |
|---|---|---|
| BC-4.01.001 | cmd/hylo/main.go + statusline.go (dispatch) | ARCH-01 |
| BC-4.01.002 | cmd/hylo/statusline.go (unknown-flag scan) | ARCH-01 |
| BC-4.01.003 | cmd/hylo/version.go | ARCH-01 |

## S5 — Pyfmt (20)

| BC | Component | ARCH |
|---|---|---|
| BC-5.01.001 | py/num.go (Round/RoundN/F) | ARCH-06 |
| BC-5.01.002 | py/num.go (ParseInt/ParseFloat) | ARCH-06 |
| BC-5.01.003 | py/num.go (divmod/mod, Int/Ceil, Max/Min) | ARCH-06 |
| BC-5.01.004 | py/num.go (D) | ARCH-06 |
| BC-5.01.005 | py/num.go (Repr) | ARCH-06 |
| BC-5.01.006 | py/num.go (MaxSeq) | ARCH-06 |
| BC-5.01.007 | py/num.go (NumToF/TrueDiv/NumCmp) | ARCH-06 |
| BC-5.02.001 | py/json.go (dumps length rules) | ARCH-06 |
| BC-5.02.002 | py/json.go (63-case oracle) | ARCH-06 |
| BC-5.02.003 | py/json.go (loads bytes acceptance) | ARCH-06 |
| BC-5.02.004 | py/json.go (ordered Value) | ARCH-06 |
| BC-5.02.005 | py/json.go (Str) | ARCH-06 |
| BC-5.02.006 | py/json.go (Dumps) | ARCH-06 |
| BC-5.03.001 | py/str.go (Len/Truncate/HasSurrogate) | ARCH-06 |
| BC-5.03.002 | py/str.go (whitespace/splitlines) | ARCH-06 |
| BC-5.03.003 | py/str.go (SubNonWord, EncodeUTF8Replace) | ARCH-06 |
| BC-5.03.004 | py/str.go (Posix/Nt Normpath, Basename) | ARCH-06 |
| BC-5.04.001 | py/time.go (FromISOFormat) | ARCH-06 |
| BC-5.04.002 | py/time.go (LocalToUnix _mktime port) | ARCH-06 |
| BC-5.04.003 | py/time.go (TimeFloat) | ARCH-06 |

## S6 — Parity harness (14)

| BC | Component | ARCH |
|---|---|---|
| BC-6.01.001 | par/oracle.go (explicit interpreter, -s) | ARCH-07 |
| BC-6.01.002 | par/env.go (child env from scratch) | ARCH-07 |
| BC-6.01.003 | par/shim_canary.go + sl/testdata/pyhooks/sitecustomize.py | ARCH-07 |
| BC-6.02.001 | par/corpus.go (synthetic corpus; captures/) | ARCH-07 |
| BC-6.02.002 | par/replay.go (stdin-sequence, stepped clock) | ARCH-07 |
| BC-6.02.003 | par/case.go (case model) | ARCH-07 |
| BC-6.02.004 | par/swap.go (four-cache swap) | ARCH-07 |
| BC-6.03.001 | sl/testdata/goldens (Tier B, Python-written) | ARCH-07 |
| BC-6.03.002 | par/compare.go (bytes+exit+caches) | ARCH-07 |
| BC-6.03.003 | par/compare.go (temp carve-out) | ARCH-07 |
| BC-6.03.004 | par/exclusions.go (closed set, no globs) | ARCH-07 |
| BC-6.04.001 | CI matrix (ARCH-08 workflow) + par/ci.go | ARCH-07, ARCH-08 |
| BC-6.04.002 | par/timing.go (p95 report, HYLO_TIMING_GATE) | ARCH-07 |
| BC-6.04.003 | par/fuzzdiff.go (nightly Tier C) | ARCH-07 |

## Coverage

101 + 13 + 3 + 3 + 20 + 14 = **154/154**. Every row names exactly one primary component
home and at least one ARCH section. Multi-home rows (pass-4 A18: the earlier "two-row
exception" note wrongly implied BC-6.04.001 was the only one): BC-6.04.001 (par +
ARCH-08 workflow), BC-1.07.001 (cmd/hylo + sl/subagent.go; ARCH-03 + ARCH-01), and
BC-1.05.008 (sl/cost.go + cost/history.go). BC-1.03.015 collapsed to sl-only when OD-161
removed the fd helpers (pass-3 A06). No BC unmapped; no component without a BC set
except theme.go (serves BC-2.01.003 via cfg) and env.go seams (serve BC-1.01.009).
