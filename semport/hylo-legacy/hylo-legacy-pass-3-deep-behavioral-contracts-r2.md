# Pass 3 deepening, round 2: behavioral contracts (hylo-legacy)

- **Scope:** `legacy/` only. Recounted: 11 files, 3,181 lines (`dgx_statusline.py` 1245, `dgx_proxy.py` 764,
  `dgx_ledger_exporter.py` 414, `auto_continue.py` 275; unchanged since round 1).
- **Inputs read:** every file in `.factory/semport/hylo-legacy/`, including round 1 of this pass, pass-2 round 1, and
  pass-2 round 2 (`…-pass-2-deep-domain-r2.md`, written in parallel, read and not edited). I re-read in full:
  `dgx_statusline.py`, `dgx_proxy.py`, `auto_continue.py`, `dgx_ledger_exporter.py`, `claude-dgx`, `dgx_preflight.py`,
  `deploy/*.plist` and `dgx-proxy-coordinator.sh`.
- **Method:** static reading plus pinning scripts in
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r2/`, run with
  `python3.11 -I` (CPython 3.11.7). `loader.py` reads a legacy file's **text** and execs a copy in a fresh namespace.
  Before that it points `HOME`, the ledger, the hook log and the decision log at the scratchpad, and it never imports
  a legacy module in place. Network calls are replaced by fakes (`fetch_sample`, `kev_pdone`). The clock is a frozen
  `time.time` shim. No legacy file was executed in place, modified or networked. Scripts: `golden.py`, `trim.py`,
  `cols.py`, `getsample.py`, `effrl.py`, `turn.py`, `cpt.py`, `dumpslen.py`, `dl2.py`, `proxynorm.py`, `tap.py`,
  `hookkev.py`, `exporter.py`, `dst.py`, `subagent.py`.
- **Notation:** `\e` is ESC (0x1B). Glyphs appear literally. Code points are written `U+XXXX` (not backslash-u) so
  the file stays byte-stable. "Pinned" means a copied expression produced the output shown. Line cites without a file
  refer to `dgx_statusline.py`.
- **IDs (policy 1, append-only):** new BC-SL-089…098, BC-PX-037…042, BC-HK-022…023 and BC-EX-018…023. New crash
  IDs: CP-A01…A03 (status line `--subagent` entry point) and P-S4 (proxy). Proxy, exporter and hook crash IDs reuse
  the pass-2 round-2 series (P-R*, P-S*, E-*, H-*) and are not renumbered. Retractions: CONV-ABS-6 and CONV-ABS-7
  (pass-2 round 2 used CONV-ABS-5).

---

## 0. Owner rulings of 2026-11-14 (applied in this file; no longer pending)

| Ruling | Effect on the contracts |
|---|---|
| **(a) Harness stdio mode: STRICT** (production: `LANG=en_US.UTF-8`, no `PYTHONUTF8`, no C locale). Windows CI compares Go against reference outputs generated on macOS/Linux | BC-SL-076 strict column is **the** parity mode. CONTRA-3 (round 1) is resolved against research Q3a. Invalid UTF-8 on stdin gives `{}` and the `?` defaults. A JSON-escaped lone surrogate in a rendered str gives CP-S17 (degraded). **CONFIRMED by the owner's capture (2026-11-14):** `LANG=en_US.UTF-8`; no `LC_ALL`, `LC_CTYPE`, `PYTHONUTF8` or `PYTHONIOENCODING`; Anaconda `python3` 3.11.7; `utf8_mode=0`; stdin and stdout utf-8/strict; `COLUMNS` set by Claude Code to the terminal width (80 in the probe). **Oracle interpreter for every pinned status line and hook output: CPython 3.11.7** (all pins in this file ran on 3.11.7). Production fixtures carry a present, numeric `COLUMNS`; missing or non-numeric `COLUMNS` remains an edge-case fixture (BC-SL-055) |
| **(b) CP-C01…C10 are OUT of byte-parity scope** (known differences) | Listed in §B as known diffs. **New contract on the Go writer (BC-SL-091/093 pins):** Go writes every cache file in legacy's exact format: keys, key order (including order inherited from earlier writes, §A2), `NaN`/`Infinity` tokens, `", "`/`": "` separators, no trailing newline, and the per-refresh write order (round 1 A8). Legacy then cannot reach a CP-C path during the shadow week |
| **(c) APPROVED DEVIATION D4-EX-2**: no sticky transcript crash | BC-SL-068 and CP-T01…T07 are marked "owner-approved deviation D4-EX-2 (2026-11-14)". The precise Go contract is BC-SL-098 (§A6). These cases are excluded from the Python-vs-Go diff and covered by Go table tests |
| D4-EX-1 (earlier ruling) | ⌂ on Windows (round 1 A7) is named D4-EX-1 |

---

## 1. Audit of round 1 (5 hallucination classes and riskiest claims)

| Item | Verdict | Evidence |
|---|---|---|
| Metrics | Line counts recounted (above). BC counts in round 1: 35 SL, 5 PX, 8 HK new, all present | `find … -exec wc -l` |
| **Crash catalogue counts (40 = 36 guarded + 4 outside)** | **Confirmed for the main entry point.** I re-enumerated every `.get`, arithmetic, format, `int()`/`ceil` and slice reachable from `main()`; nothing was found outside B1–B5. Recount: 17 stdin + 7 transcript + 2 network + 10 foreign-cache = 36 guarded; CP-X01…X04 = 4. **Gap:** round 1 omitted the second entry point `--subagent` (`:1240-1241`, wired by `claude-dgx:176`), which has 3 more guarded crash paths (CP-A01…A03, BC-SL-097). Status line total: **43** | `:1200-1245,888-936` |
| **CP-T predicates** | **Partly over-extrapolated → CONV-ABS-6** (below). The count of 7 stands; five predicates were too broad | `cpt.py` |
| **I1 (Accept-Encoding condition)** | **Confirmed.** Nothing between `:111` and `:131` can raise for a dict body, so the header is set iff host == `api.anthropic.com`, path prefix `/v1/messages`, the body parses, and it is a dict. New nuance: a truthy non-str `model` still gets the header (`:131`), then raises at `:132` (pass-2 P-R1) | `dgx_proxy.py:103-132` |
| **I2 (last qualifying event wins, no merge)** | **Confirmed and pinned** (`tap.py`): `message_start` + `delta(in=10,out=5)` + `delta(out=99)` → `usage=(10, 5)`, `stop=end_turn`. Two nuances: (1) inside the raising event, `usage` and the cache maxima are already applied before `delta.get` raises (`delta: null` event → `usage=(1,2)` kept); (2) an `int()` failure aborts the rest of that **block**, so the result **depends on TCP chunk boundaries** (BC-PX-040) | `dgx_proxy.py:398-427` |
| BC-SL-054 (double reset) | Confirmed with one refinement: the ♻ segment does not end in RESET (`f"{CYAN}♻{RESET} {pct}%"`), so a row trimmed to end at ♻ ends in a **single** `\e[0m`. An untrimmed row whose last segment is ♻ ends in **no** RESET | `:479`; `trim.py` |
| BC-SL-022 example `(112000 s, 26.7e6) → ⌂1d07h` | Confirmed by golden A | `golden.py` |
| Pass-2 r2 H-04 (hook `(p, None)` crash) | **Independently reproduced** (`hookkev.py`). Contract in BC-HK-022 | `auto_continue.py:128-138,250` |

### Retractions

- **CONV-ABS-6** (round 1 §B2 predicates). Round 1 stated CP-T02, T03, T04, T06 and T07 as unconditional on the
  field shape. Pinned exceptions (`cpt.py`):
  - **CP-T02** (`message` truthy non-dict) does **not** crash on an **untimestamped** `system`/`compact_boundary` line.
    The `continue` at `:1095` comes before `:1096`.
  - **CP-T03** (`usage` truthy non-dict) crashes only when the line **opens a new turn**: timestamp parses, `assistant`,
    id truthy, and `cur` is None or `cur.id != id`. On a continuation line of the same id, or with no timestamp, the
    line is processed normally and its usage is not counted (`isinstance(u, dict)` gate, `:1099-1104`).
  - **CP-T04, CP-T06, CP-T07** never fire on a `system`/`compact_boundary` line (usage and content are skipped by
    `continue`). CP-T04 also needs the usage to be **counted**: id falsy, or id not yet in `seen_ids` (an already-seen
    id with a bad token is ignored; pinned).
  - **CP-T05** additionally needs `lu is not None` when the turn opens (`t0 = lu`; `_finish_turn` returns early when
    `t0` is None, `:991`).

  The corrected predicates are the W-predicates of BC-SL-098.
- **CONV-ABS-7** (extraction validation row "Trust `remove`/`rotate` crash at `dgx_proxy.py:761`": "`rotate` touches
  `args.force` unconditionally"). False: `:703` is `if _mitmdump_running() and not args.force:`. Python
  short-circuits, so `args.force` is evaluated **only while a `mitmdump` process is running**. Correct contract:
  `trust rotate` runs normally when no mitmdump is running (it calls `cmd_trust_install(None)`, which reads no args).
  With mitmdump running it raises AttributeError (traceback, exit 1) instead of printing the intended refusal.
  `trust remove` raises at `:687` (`args.yes`) whenever a keychain entry exists, so it never removes anything. The
  broad-sweep BC-PX-031 wording ("remove/rotate crash") is narrowed accordingly.

---

## A. Status line

### A1. Row-1 and row-2 golden composition (BC-SL-089, BC-SL-090; target 1)

**Fixture** (`golden.py`; `NOW = 1794615009.0`, TZ=UTC, `LOCAL_MODEL_PREFIXES=claude-sonnet`, COLUMNS unset). The
fixture was run through the whole of `main()`, with `fetch_sample` faked and the session cache pre-seeded with
`proc_start = NOW-112000` and 6 history points `t = NOW-12 … NOW-2`, `v = 150,170,190,200,204,202`, `k=0.9`, `f=4.2`.

- stdin: `session_id "sess-golden-1"`, `model {id, display_name}`, `workspace.project_dir = <scratch>/home-lab` (a
  `.git/HEAD` of `ref: refs/heads/main`), `context_window {used_percentage 43.4, context_window_size 1000000}`,
  `prompt_cache.hit_ratio 0.94`, `cost {total_lines_added 31, total_lines_removed 4, total_duration_ms 26700000,
  total_api_duration_ms 6711428.57, total_cost_usd 32.62}`. Golden A adds `rate_limits {five_hour {31, NOW+9690},
  seven_day {44, NOW+15510}}`.
- Transcript (6 lines): a user prompt string (21 chars) at NOW-100. Assistant `m1` (thinking 400 chars) at NOW-98, and
  `m1` again (tool_use input `{"command":"ls -la"}`) at NOW-88, both with usage `in 200 / cw 30000 / cr 0 / out 1200`.
  A user tool_result of 3000 chars at NOW-80. `m2` (text 29 chars; usage `100/60000/0/50`) at NOW-70. `m3` (text 1500
  chars; usage `300/900/60100/800`) at NOW-60.
- Sample: running 3, waiting 0, kv 0.92, host share 0.0, gen_rate1m 204.4, gen_rate5m 190, ttft p95 4.2 with
  n30m 57, preempt 0, last DGX request NOW-400, wall 1400 W, tariff 0.24, GPU 1059 W, temp 66, up vllm/lmcache 1,
  usd/MTok 0.09, rate_mtok_month 12.0 (golden C: 45.0).

**Golden A (ANTH lane, limits, cold-start cost colors), row 1** (198 visible columns, 12 segments):

```text
\e[105;30;1m ◨ ANTH \e[0m\e[2m · \e[0m\e[97mOpus 5.5\e[0m\e[2m · \e[0m\e[90m⎇ main\e[0m\e[2m · \e[0m\e[90mhome-lab\e[0m\e[2m · \e[0m\e[38;2;159;204;30m▰\e[38;2;182;204;30m▰\e[38;2;204;202;30m▰\e[38;2;204;179;30m▰\e[90m▱\e[90m▱\e[90m▱\e[90m▱\e[90m▱\e[90m▱\e[0m 43%\e[0m\e[2m/1.0M\e[0m\e[2m · \e[0m\e[36m▤60%\e[0m \e[32m❙32%\e[0m \e[35m◈ 8%\e[0m\e[2m · \e[0m\e[36m♻\e[0m 94%\e[2m · \e[0m\e[90m5h31%\e[0m \e[90m->2h41m\e[0m  \e[90m7d44%\e[0m \e[90m->4h18m\e[0m\e[2m · \e[0m\e[32m▲31\e[0m\e[2m/\e[0m\e[31m▼4\e[0m\e[2m · \e[0m\e[90m⏱ 7h25m\e[0m\e[2m·1h51m\e[0m\e[90m ⌂1d07h\e[0m\e[2m · \e[0m\e[90m↑\e[0m\e[97m152k\e[0m\e[2m[\e[0m\e[97min600\e[0m \e[33m✍91k\e[0m \e[36m⟳60k\e[0m\e[2m]\e[0m\e[90m ↓\e[0m\e[97m2k\e[0m \e[2m\e[33m↻1\e[0m\e[2m · \e[0m\e[33m$32.62\e[0m\e[90m $17.5/h\e[0m
```

Plain: ` ◨ ANTH  · Opus 5.5 · ⎇ main · home-lab · ▰▰▰▰▱▱▱▱▱▱ 43%/1.0M · ▤60% ❙32% ◈ 8% · ♻ 94% · 5h31% ->2h41m  7d44% ->4h18m · ▲31/▼4 · ⏱ 7h25m·1h51m ⌂1d07h · ↑152k[in600 ✍91k ⟳60k] ↓2k ↻1 · $32.62 $17.5/h`

**Row 2 (fresh; identical for A and B)** (81 columns, 7 segments):

```text
\e[32m◉\e[0m\e[2m · \e[0m\e[32mr3·q0\e[0m\e[2m · \e[0m\e[36mKV▰▰▰▰ 92%\e[0m\e[2m · \e[0m\e[90m»\e[0m\e[90m5\e[0m\e[90mt/s\e[0m\e[2m · \e[0m\e[90m▣\e[0m\e[97m204\e[0m\e[90mt/s\e[0m \e[38;2;38;93;104m▆\e[38;2;44;108;121m▇\e[38;2;51;124;138m█\e[38;2;57;139;155m█\e[38;2;63;154;172m█\e[38;2;70;170;190m█\e[38;2;140;235;255m█\e[0m\e[2m · \e[0m\e[90m◔4.2s\e[0m\e[2m · \e[0m\e[97m⚡1059W\e[0m\e[90m·\e[0m\e[33m1400W\e[0m\e[90m 66°\e[0m\e[90m 34¢/h\e[0m
```

**Golden B (DGX lane, ⛏ n/a because rate_mtok_month 12 < 30.4), row 1** (173 columns, 11 segments). Same as A
except: the pill is `\e[106;30;1m ◨ DGX \e[0m`, the model is `\e[97mSonnet 5.5\e[0m`, there is **no limits
segment** (stdin has no `rate_limits`, the cache is empty), and the cost segment ends
`…\e[90m $17.5/h\e[0m\e[90m ⛏n/a\e[0m`.

**Golden C (DGX lane, basis ok, row 2 stale):** the cache holds a sample 40 s old with `fetch_ts = NOW-10`, so the TTL
has expired, the fetch runs and fails. Row 1 is B's row with the cost tail `\e[90m ⛏0.01\e[0m` (174 columns): tokens
152,200 + 2,050 = 154,250 × 0.09 / 1e6 = 0.0139. Row 2 (86 columns, 8 segments):

```text
\e[33m◉\e[0m\e[2m · \e[0m\e[32mr3·q0\e[0m\e[2m · \e[0m\e[36mKV▰▰▰▰ 92%\e[0m\e[2m · \e[0m\e[90m»\e[0m\e[90m5\e[0m\e[90mt/s\e[0m\e[2m · \e[0m\e[90m▣\e[0m\e[90m204\e[0m\e[90mt/s\e[0m\e[2m · \e[0m\e[90m◔4.2s\e[0m\e[2m · \e[0m\e[97m⚡1059W\e[0m\e[90m·\e[0m\e[33m1400W\e[0m\e[90m 66°\e[0m\e[90m 34¢/h\e[0m\e[2m · \e[0m\e[2m(~40s old)\e[0m
```

What the goldens pin (BC-SL-089):

| Item | Value | Line |
|---|---|---|
| Visible width per segment, A row 1 | pill 8 · model 8 · branch 6 · project 8 · thermometer 19 · mix 14 · ♻ 5 · limits 28 · lines 6 · timer 20 · tokens 29 · cost 14 (SEP = 3) | `trim.py` |
| B row 1 | 7 · 10 · 6 · 8 · 19 · 14 · 5 · 6 · 20 · 29 · 19 | — |
| Row 2 fresh | dot 1 · queue 5 · KV 10 · »mine 5 · box+spark 15 · TTFT 5 · power 22 | — |
| Row 2 stale (C) | 1 · 5 · 10 · 5 · **7** (sparkline dropped, box number grey) · 5 · 22 · **10** (`(~40s old)`) | `:698-700,783-785` |
| The pill's leading space | the row starts with a visible space (pill text is ` ◨ ANTH `) | `:447-449` |
| Limits join | two plain spaces between windows, not SEP | `:532` |
| Turn rate `»5` (dim) | m2's turn (`out=50`, t0 = the tool_result line at NOW-80, t1 = NOW-70, span 10 s ≤ 4·50/15) is closed by m3 and **replaces** m1's 100 t/s turn. `dim` because 50 < 200 | `:988-996,1073-1079` |
| ⏱ api `1h51m` | 6,711,428.57 ms → 111 min (the docstring's `1h52m` is illustrative only) | `:546` |
| `$32.62` YELLOW | cold start (no history excluding self) and usd ≥ 25 | `:610-615` |
| Idle hidden | last request NOW-400 > 300, but running = 3 is not < 1 | `:825` |
| Mix | res 3000, conv 21+21+29+1500 = 1571, think 400 → 60.35/31.6/8.05 → `▤60% ❙32% ◈ 8%` | `:1120-1174` |
| Tokens | tin 30,200+60,100+61,300 = 151,600 → `152k`; c_in 600; c_wr 90,900 → `91k`; c_rd 60,100 → `60k`; tout 2,050 → `2k`; rb 1 (m2 excess 60,000 − 29,900 = 30,100 > 20,000) | `:1104-1119` |
| stdout bytes | A 1,179; B 1,120; C 999 (including the final `\n`) | — |

**BC-SL-090 (trim breakpoints, for table tests).** Each pair is (largest COLUMNS that gives this result → visible
width, segments kept). Every row trimmed by at least one segment ends in a double reset, except where the kept last
segment is ♻ (single reset).

| Row | Breakpoints |
|---|---|
| A row 1 (198) | ≥198 → 198/12 · 197 → 181/11 · 180 → 149/10 · 148 → 126/9 · 125 → 117/8 · 116 → 86/7 **(single reset, ends `94%\e[0m`)** · 85 → 78/6 · 77 → 61/5 · 60 → 39/4 · 38 → 28/3 · 27 → 19/2 · 18 and below → 8/1 (the pill alone, even when wider than COLUMNS) |
| B row 1 (173) | 173/11 · 172 → 151/10 · 150 → 119/9 · 118 → 96/8 · 95 → 87/7 (single reset) · 86 → 79/6 · 78 → 62/5 · 61 → 40/4 · 39 → 29/3 · 28 → 20/2 · 19 → 7/1 |
| C row 1 (174) | as B, shifted by 1 at the top (174/11, 173 → 151/10, then identical) |
| Row 2 fresh (81) | 81/7 · 80 → 56/6 · 55 → 48/5 · 47 → 30/4 · 29 → 22/3 · 21 → 9/2 · 8 → 1/1 |
| Row 2 stale (86) | 86/8 · 85 → 73/7 · 72 → 48/6 · 47 → 40/5 · 39 → 30/4 · 29 → 22/3 · 21 → 9/2 · 8 → 1/1 |

**Production-shaped fixture (owner capture: COLUMNS=80)** through `main()` (`cols80.py`, golden A): 2 rows, widths
[78, 56], 701 bytes. Row 1 keeps 6 segments (pill … mix) and ends `…\e[35m◈ 8%\e[0m\e[0m`. Row 2 keeps 6 segments
(dot … TTFT) and ends `…\e[90m◔4.2s\e[0m\e[0m`. The unbounded goldens above (COLUMNS unset) are the edge-case
fixtures. Also end-to-end (`cols.py`, golden A): COLUMNS=100 → 2 rows, widths [86, 81], 809 bytes.
COLUMNS=72 → [61, 56], 642 bytes. **COLUMNS=71 → 1 row** (row 2 is dropped by the `< 72` rule before trimming), 61
columns, 286 bytes. COLUMNS=-5 → 1 row, untrimmed, 198 columns, 743 bytes (round 1 BC-SL-055). Row 2 is trimmed only
when 72 ≤ COLUMNS < its width.

### A2. `get_sample` state machine (BC-SL-091, BC-SL-092; target 2)

Pinned sequence (`getsample.py`, TTL 4, cache file seeded with `hist [[900,50],[990,60],[998.5,70]]` and a retired
`sess_state`). S1 = `{running 1, kv 0.5, gen_rate1m 80}`. Row 2 is shown plain; "cache" is the exact file content
after the step.

| # | t | Fetch? | Result → row 2 | Cache after (exact JSON) |
|---|---|---|---|---|
| 0 | 1000 | yes, S1 | `(S1, 0.0, True, 2 pts)` → `◉ · r1·q0 · KV▰▰▱▱ 50% · ▣80t/s ▇█` | `{"hist": [{"t": 990.0, "v": 60.0}, {"t": 998.5, "v": 70.0}], "fetch_ts": 1000.0, "up": true, "ts": 1000.0, "sample": {"vllm:num_requests_running": 1.0, "vllm:kv_cache_usage_perc": 0.5, "dgx_sl:gen_rate1m": 80.0}}` |
| 1 | 1002 | no (`1000 > 998`) | `(S1, 2.0, True, …)`, same row | unchanged |
| 2 | 1004 | **yes** (`1000 > 1000` is false: the TTL test is strict) and fails | `(S1, 4.0, False, …)` → `… · ▣80t/s · (~4s old)` | `fetch_ts 1004.0`, `up false`; `ts`, `sample`, `hist` kept |
| 3 | 1006 | no | `(S1, 6.0, False)` → `(~6s old)` | unchanged |
| 4 | 1020 | yes, fails | `(S1, 20.0, False)` → `(~20s old)` | `fetch_ts 1020.0` |
| 5 | 1300 | yes, fails, age 300 (`< 300` is false) | `(None, 300.0, False, [])` → `◌ DGX ?` | `fetch_ts 1300.0`; **sample still stored** |
| 6 | 1302 | no (cached path) | **`(S1, 302.0, False)` → `… · (~302s old)`** (KEEP_DEAD not applied on the cached path) | unchanged |
| 7 | 1305 | yes, fails | `◌ DGX ?` | `fetch_ts 1305.0` |
| 8 | 1310 | yes, S2 = `{running 0, gen_rate5m 12.5, ttft 2.0, preempt 0.01}` | `◉ · r0·q0 · ▣12t/s · ◔2.0s` (1 point, no sparkline) | `"hist": [{"t": 1310.0, "f": 2.0, "v": 12.5, "p": 1}]`, the 5-minute fallback places `v` after `f`, then `p` |
| 9 | 1314.5 | yes, S1 | `… ▣80t/s ▂█` | hist `[{…1310…}, {"t": 1314.5, "v": 80.0, "k": 0.5}]` |
| 10 | 1316.5 | no | same | unchanged |

Contract points (BC-SL-091):

- **Step 0: a fetched sample is not plotted** when the newest kept history point is less than 2 s old
  (`1000 − 998.5 = 1.5 < HIST_MIN_GAP`). The sparkline draws only the two old points (`▇█`, values 60 and 70), not 80
  (`:337`).
- Normalization of legacy `[t, v]` points happens **only on a successful fetch** (`:335`). The failure path writes
  them back unchanged (`entry = dict(c)`): pinned `{"hist": [[900.0, 50.0]], "fetch_ts": 1000.0, "up": false}`. The
  cached path returns them raw and `sparkline` normalizes them on read (`:664`).
- After a first-ever failed fetch the file is `{"fetch_ts": 1000.0, "up": false}` (no `ts`). The returned age is
  `now − 0` (`:356`).
- `up:false` marks row 2 stale **immediately**, even with an age below `STALE_OK` (step 2 shows `(~4s old)`). The
  15 s bound applies only while `up` is true (`:697`).
- With refreshes exactly TTL apart (`refreshInterval = 4 = TTL`) every refresh fetches (strict `>`). During an outage
  older than 300 s, `◌ DGX ?` therefore alternates with `(~Ns old)` only on refreshes inside a TTL window (assistant
  messages, mode changes).
- Key order is inherited: `entry = dict(c)` keeps the file's existing order, and new keys are appended in the order
  `fetch_ts, up, ts, sample, hist`. Ruling (b) obliges the Go writer to reproduce this order (step 0 shows `hist`
  first because the seed had it first).
- `DGX_SL_TTL=nan` fetches every refresh. `DGX_SL_TTL=inf` never fetches and never writes; it returns age
  `now − 9999` (`-8999.0` here) and renders `◌ DGX ?` (round 1 BC-SL-087 confirmed).

**BC-SL-092 (HIST_MIN_GAP reachability).** With TTL ≥ 2, a fetch happens only at `now ≥ fetch_ts + TTL`, and history
points are appended only on success at `t = fetch_ts`, so the 2 s gap can **never** bite in steady state (steps 8–9).
It is reachable only with `TTL < 2` (including NaN), a seeded or foreign history point newer than `now − 2` (step 0),
or a backward clock step. A Go table test must cover the seeded case. The steady state needs no gap logic to match
legacy, but the code must keep it.

### A3. `effective_rl` and limits over time (BC-SL-093; target 3)

`effrl.py`, T0 = 1794600000, one window `seven_day {44, T0+15480}` unless noted. Each step runs `effective_rl` and then
`render_lane` (limits segment shown plain).

| t − T0 | stdin `rate_limits` | Shown | Session cache after |
|---|---|---|---|
| 0 | `{seven_day…}` | `7d44% ->4h18m` | `{"rl": {"seven_day": {"used_percentage": 44, "resets_at": 1794615480.0}}, "rl_ts": T0}` |
| 100 | key absent | `7d44% ->4h16m` (countdown recomputed from the cached `resets_at`) | unchanged |
| 200 / 300 / 400 | `{}` / `null` / `"x"` | cached value shown (every falsy or non-dict input counts as absent and is **not** written) | unchanged |
| 1799.999 | absent | shown | — |
| **1800** | absent | **hidden** (`1800 < 1800` is false) | unchanged; the stale `rl` is never deleted |
| 1900 | `{five_hour {90, resets T0+1900}, seven_day {50, …}}` | `7d50% ->3h46m` (5h dropped: `resets_at <= now`) | replaced wholesale, `rl_ts T0+1900` |
| 2000 | absent | `7d50% ->3h44m` | — |
| 15480 | absent | hidden (7d `resets_at == now`; RL_KEEP has also run out) | — |

Sticky CP-S09 (pinned):

| t | stdin | Result | Cache |
|---|---|---|---|
| 0 | `{five_hour: "x"}` | degraded (AttributeError `:503`) | **`{"rl": {"five_hour": "x"}, "rl_ts": T0}` written before the crash** (step 3 of A8 precedes render) |
| 10, 1799 | absent | degraded (cached bad dict) | unchanged |
| 1800 | absent | recovers (hidden) | unchanged |
| 0 then 5 | `{five_hour: [1]}`, then a good dict | degraded, then **recovers at once** (stdin overwrites the cache) | replaced |

More pins: `{five_hour: 0, seven_day: …}` is saved verbatim, and `0` counts as an absent window. `{seven_day: {}}` →
widget hidden, with `{"rl": {"seven_day": {}}, …}` saved. **Reroute-all** (`LOCAL_MODEL_PREFIXES=claude`) still
writes `rl` to the cache but hides the widget. Foreign cache `rl` without `rl_ts` → hidden (`ts` defaults to 0). An
`rl_ts` in the future → shown (there is no lower bound). Harness note: `LOCAL_MODEL_PREFIXES` is read **at render
time** (`:444`, `:902`), not at import time.

### A4. `_mix_counts` turn machine, exhaustive table (BC-SL-094, BC-SL-095; target 4)

`turn.py` and `cpt.py`. `B` is the base time; every assistant line has `out = 300` unless noted. "lr" is the rate
written to the mix cache, as `[rate, dim]`.

| Case | Lines (t in s) | lr | Rule pinned |
|---|---|---|---|
| T1 | U0, A2, A10, B12 | `[30.0, False]`; cur = `{id B, t0 0, t1 12, out 300}` | A runs from the prompt to its **last** line. **B's t0 is also the prompt (0)**: consecutive messages with no user line in between share `t0`, so B's span includes A's time |
| T2 | U0, A2, U5 (tool_result only), A10, S11 | `[30.0, False]`, lu = 5 | a tool_result-only user line updates `lu` but does not close the turn |
| T3 | same with U5 holding `[tool_result, text]` | `[30.0, False]` | **mixed content counts as tool_result** (`any(...)`): no close |
| T4 | U5 = list of text blocks | `[60.0, False]` | closes A (150 t/s); **A's reappearing line at 10 opens a new turn** (t0 = 5) with that line's own `out` (300), not deduplicated; closed by S11 → 300/5 = 60 |
| T5 | U5 with `message: {}` (content missing) | `[60.0, False]` | missing content closes the turn (not a list) |
| T6 | U0, A(untimed)×2, B12, S13 | `[25.0, False]` | untimed lines are invisible to the turn machine (their usage and composition still count) |
| T7 | U0, A2, S3, U(untimed), B30, S31 | `[10.0, False]` | an untimed user prompt does **not** move `lu`; B's t0 stays 0 |
| T8 | S(untimed) between A lines | `[30.0, False]` | an untimed system line does not close |
| T9 | U0, A2, compact_boundary at 10 (timed) | `[150.0, False]` | a timed `compact_boundary` closes the turn **and** resets composition |
| T10 | A2, B10, S11 (no user line) | `None` | t0 None → every turn skipped |
| T11 | refresh 1: U0, A2 · refresh 2: A9 · refresh 3: S10 | None, None, `[33.333333333333336, False]` | `cur` is persisted unfinished: `{"id": "A", "t0": B+0, "t1": B+2, "out": 300}`, then `t1` becomes B+9 on refresh 2 |
| T12 | refresh 1: U0 · refresh 2: A2 · refresh 3: S12 | `[150.0, False]` | `lu` carried across refreshes (cache `lu = B+0`) |
| T14 | U0, A2, B5, A8, S9 | `[37.5, False]` | a reappearing id after another id starts a new turn (t0 = 0, t1 = 8) |
| T15 | U0, A2 (out 10), B5 (out 5), A8 (`output_tokens: "abc"`), U9 | **crash** TypeError `:994` | **CP-T05 is reachable with this 5-line transcript.** Sticky: refresh 2 crashes again and the cache is never written |
| T16 | first line `output_tokens: NaN` | `[nan, False]` | NaN out gives NaN rate (`»nan`); the cache stores the bare `NaN` token |
| T17 | U0, A2 (150), B4 (100), S40 | `[25.0, True]` | the span ends at the message's last line (4), not at the closer (40); both turns dim |
| T18 | U0, A80 (out 300), S81 | `[3.75, False]` | `span == 4·out/15` (80.0) is **accepted** (`>` rejects) |
| T19 | assistant line without `message.id` | `None` | no turn action |
| T20 | `summary`-typed line between A lines | `[33.33…, False]` | other line types are ignored by the turn machine |

BC-SL-095 (turn identity): the turn machine keys only on `cur.id` versus the line's id and **never consults
`seen_ids`**. A message whose lines are split by a closer (user prompt, timed system line) or by another id is
measured as two turns, and each takes `out` from its own opening line.

### A5. `json.dumps` length oracle (BC-SL-096; target 5)

Oracle for tool_use input: `len(json.dumps(json.loads(src) or ""))` (`:1147`), Python defaults (`", "`, `": "`,
`ensure_ascii`, float `repr`, `allow_nan`). `dumpslen.py` and `dl2.py`, 63 cases. Source text is shown as it appears
in the transcript; `U+00E9` etc. means the raw (unescaped) character in the source.

| # | Source | len | # | Source | len |
|---|---|---|---|---|---|
| 1 | `{}` | 2 | 33 | `{"x":1.5e-7}` | 14 (`1.5e-07`) |
| 2 | `[]` | 2 | 34 | `{"x":5e-324}` | 13 |
| 3 | `""` | 2 | 35 | `{"x":1.7976931348623157e308}` | 30 (`e+308`) |
| 4 | `0` | 2 | 36 | `{"x":0.1}` | 10 |
| 5 | `-0.0` | **2** (falsy) | 37 | `{"x":0.30000000000000004}` | 26 |
| 6 | `0.0` | 2 | 38 | `{"x":123456789.123456789}` | 25 (`123456789.12345679`) |
| 7 | `false` | 2 | 39 | `{"x":2.5e-5}` | 14 (`2.5e-05`) |
| 8 | `null` | 2 | 40 | `{"t":"caf` + raw U+00E9 + `"}` | 18 |
| 9 | `{"command":"ls"}` | 17 | 41 | same with the JSON escape for U+00E9 | 18 |
| 10 | `{"command": "ls"}` | 17 | 42 | `{"t":"` + raw U+1F600 + `"}` | 21 (surrogate pair, 12 chars) |
| 11 | `{"a":1,"b":[1,2,{"c":null}]}` | 34 | 43 | same as a JSON surrogate-pair escape | 21 |
| 12 | `{"a":true,"b":false}` | 23 | 44 | JSON escape for lone U+D800 | 15 |
| 13 | `9223372036854775807` | 19 | 45 | `{"t":"a` + escaped U+0000 + `b"}` | 17 |
| 14 | `9223372036854775808` | 19 (exact int, > 2^63−1) | 46 | `{"t":"a\nb\tc"}` | 16 |
| 15 | `18446744073709551616` | 20 | 47 | escaped U+007F U+0080 U+009F | 27 (each 6) |
| 16 | `-123456789012345678901234567890` | 31 | 48 | escaped U+001F | 15 |
| 17 | `{"x":1}` | 8 | 49 | raw U+2028 U+2029 | 21 |
| 18 | `{"x":1.0}` | 10 | 50 | `{"t":"<script>&amp;</script>"}` | 31 (no HTML escaping) |
| 19 | `{"x":1e2}` | 12 (`100.0`) | 51 | `{"t":"\\/\""}` | 14 (`\/` decodes to `/`; `\\` and `\"` re-escape) |
| 20 | `{"x":1.10}` | 10 (`1.1`) | 52 | `{"t":"/"}` | 10 (`/` not escaped) |
| 21 | `{"x":1E400}` | 15 (`Infinity`) | 53 | key with raw U+00E9, nested key with raw U+1F600, value raw U+4E2D | 46 |
| 22 | `{"x":-1e400}` | 16 | 54 | `{"a":{"b":{"c":{"d":[[],{},""]}}}}` | 40 |
| 23 | `{"x":NaN}` | 10 | 55 | `"just a string"` | 15 |
| 24 | `{"x":9999999999999998}` | 23 (int) | 56 | `[1,"a",null]` | 14 |
| 25 | `{"x":9999999999999998.0}` | 25 | 57 | `{"a":1,"a":2}` | 8 (last duplicate wins) |
| 26 | `{"x":1e16}` | 12 (`1e+16`) | 58 | `{"b":1,"a":2}` | 16 (source order kept) |
| 27 | `{"x":10000000000000000.0}` | 12 | 59 | `{"x":1e-4}` | 13 (`0.0001`) |
| 28 | `{"x":1e15}` | 25 (`1000000000000000.0`) | 60 | `{"x":1.0e-4}` | 13 |
| 29 | `{"x":123456789012345680000.0}` | 29 (`1.2345678901234568e+20`) | 61 | `{"x":12345678901234567}` | 24 (int) |
| 30 | `{"x":0.0001}` | 13 | 62 | `{"x":1234567890123456.7}` | 25 (`…456.8`) |
| 31 | `{"x":0.00001}` | 12 (`1e-05`) | 63 | `{"x":-0.0}` | 11 (truthy container) |
| 32 | `{"x":0.000123}` | 15 | | | |

Contract for `pyjson.DumpsLen`: (1) integers keep arbitrary precision (decoding numbers to float64 breaks rows
14–16, 24, 61); (2) floats use Python `repr`: shortest round-trip digits, scientific when the decimal exponent is
< −4 or ≥ 16, exponent with sign and at least 2 digits (`e-05`, `e+16`, `e+308`), and `.0` added to integral values
below 1e16; (3) the strings escape everything ≥ U+007F as `\uXXXX` (astral characters as two surrogates), control
characters as `\n \r \t \b \f` or `\u00XX`, plus `"` and `\`, and nothing else; (4) duplicate keys collapse
last-wins in first-seen position; (5) `Infinity`, `-Infinity` and `NaN` are emitted as tokens.

Tool_result list items have **no** `or ""` fallback (`:1137-1138`): `{}` 2, `[]` 2, `""` 2, `0` 1, `-0.0` 4,
`false` 5, `null` 4, `{"type":"text","text":"hi"}` 30, `"raw"` 5, `{"type":"IMAGE"}` 17 (the image test is
case-sensitive), `{"type":"image"}` 2000. A non-list, non-str inner value (`:1140`): `{}` 2, `0` 1, `false` 5,
`null` **0**, `1.0` 3, `true` 4.

### A6. D4-EX-2: Go contract for the 7 transcript crash paths (BC-SL-098, owner-approved deviation, 2026-11-14)

**General rule.** For each complete line of the parse window (the `bytes.splitlines()` pieces of
`blob[:last "\n"]`, as in legacy), Go computes the legacy decision first:

1. JSON decode fails → **skip** (legacy `:1060-1063`).
2. Otherwise, if the wrong-shape predicate `W(state, record)` holds → **skip, with exactly the same effect as a decode
   failure**.
3. Otherwise → process exactly as legacy.

A skipped line changes **no** parser state: not `res/conv/think`, `tin/tout/c_wr/c_rd/c_in`, `rb`, `pp`, `cur`, `lr`,
`lu`, `seen_ids` or `recent_ids`. Its bytes are still consumed: the offset advances to `last "\n" + 1` of the window,
as for every line. Go then saves the mix cache and renders normally. `W` is evaluated against the state reached so far
in the same parse.

**Equivalence oracle (for Go table tests):** Go on transcript T produces the same mix-cache content and render as
legacy on T with the skipped lines deleted. The one exception is `size`, which in Go equals legacy's plus the bytes of
the deleted lines (newline included). Legacy itself never saves state when it raises, so no legacy "after" state
exists to compare against.

Precise W-predicates, in legacy evaluation order. `ts_ok` = `_iso_ts(e.timestamp)` is not None. `cb` = `e.type ==
"system" and e.subtype == "compact_boundary"`.

| Path | W-predicate (the skipped line is the one that satisfies it) | Legacy mutations before its raise, which Go must NOT apply |
|---|---|---|
| CP-T01 | `e` is not an object | none (`:1069`) |
| CP-T02 | `e.message` truthy and not an object, **and not** (`cb` and not `ts_ok`) | none. With `ts_ok` it raises at `:1072` before the turn machine; without, at `:1097` |
| CP-T03 | `ts_ok`, `e.type == "assistant"`, `message.id` truthy, (`cur` empty or `cur.id != message.id`), and `message.usage` truthy and not an object | `lr = _finish_turn(cur, lr)` (`:1077`) already ran. **Go keeps the previous turn open**: `cur` stays as it was, `lr` unchanged |
| CP-T04 | not `cb`; `message.usage` is an object; (`message.id` falsy, or hashable and not in `seen_ids`); and any of `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens` is truthy and not int/float/bool | possibly the turn machine (close previous, open new `cur`), `seen_ids.add` / `recent_ids.append` (`:1102-1103`), and when only `output_tokens` is bad, `tin/c_in/c_wr/c_rd` and `rb/pp` already incremented (`:1108-1111`). None of this is applied |
| CP-T05 | `ts_ok`, `assistant`, id truthy, the line **opens a new turn** (`cur` empty or `cur.id != id`), **`lu` is not None**, the line's usage is not counted (an object whose id is already in `seen_ids`, or absent), and `(usage or {}).output_tokens` is truthy and not int/float/bool. (If the usage were counted, CP-T04 would apply first.) | Legacy closes the previous turn, opens `cur` with the bad `out`, counts the line's composition, and raises later, when that turn is closed (`:994`), possibly on a later refresh. **Go detects at the opening line and skips it**: the previous turn stays open, and composition and `lu` are unchanged. This is a spec choice that makes the "record carrying the bad value" the skipped line, as the ruling asks. It differs from legacy's lazy crash only when the session ends with that turn still open (legacy then never crashes). Those inputs are excluded from the diff anyway |
| CP-T06 | not `cb`; `message.content` is a list; a dict block has `type == "text"` with `text` truthy and without `len` (number, `true`), or `type == "thinking"` with `thinking` likewise | turn machine, usage counting, ids, and the composition of earlier blocks of the same line. None applied |
| CP-T07 | not `cb`; `message.usage` is an object (even `{}`); `message.id` truthy and unhashable (array/object) | with `ts_ok` and `assistant`: the previous turn closed and `cur = {id: [..], …}` opened (`:1077-1079`). None applied |

Go table tests must cover each row, plus the non-crash look-alikes pinned in `cpt.py`: the T02 untimed
compact_boundary, the T03 continuation line and untimed line, the T04 already-seen id and compact line, the T06
compact line, and T07 with usage absent.

### A7. Subagent entry point (BC-SL-097, new; CP-A01…A03)

`--subagent` (`:1240-1241`) reads stdin `{"tasks": [...]}` and prints one `json.dumps({"id", "content"})` line per
task that is a dict with an `id` (`:888-936`). The output is pure ASCII. `content` joins bits with a raw `" · "` (no
SGR on the separator). No rows → **no output at all** (`:934`), exit 0. Pinned (`subagent.py`, prefixes
`claude-sonnet`):

- running Sonnet task, 12,345 tokens, started 125 s ago → `{"id": "a1", "content": "\e[33m» explore\e[0m · \e[36m◨DGX\e[0m \e[90mclaude-sonnet-5-5\e[0m · \e[36m12.3k tok\e[0m · \e[90m02:05\e[0m"}`
  (as JSON, with every non-ASCII character escaped).
- completed Haiku task labelled with U+00E9 → glyph `✔`, `◨ANTH`, `2.50M tok` (`_fmt_tokens` `.2f`), status text
  `completed`.
- an unknown status → `◍` grey, name `?`, status text shown. Tasks without `id` and non-dict tasks are skipped.
  `tasks` given as an object or a string iterates keys/chars and yields no rows.
- a lone surrogate in a name is escaped by `json.dumps` → **no** CP-S17 analogue.

Guarded crash paths (degraded output is the plain line `\e[90mstatusline degraded\e[0m`, which is **not JSON**):

| CP | Condition | Site |
|---|---|---|
| CP-A01 | `tasks` truthy and not iterable (number, `true`) | `:891` TypeError |
| CP-A02 | a task's `status` is unhashable (list/object) | `:894` (`_SUB_GLYPH.get`) TypeError |
| CP-A03 | a task's `model` is truthy and not a str while `LOCAL_MODEL_PREFIXES` is non-empty | `:906` AttributeError |

Whether `--subagent` is in Go scope is pass-2 r2 owner decision 14 (not re-raised here).

### A8. Crash catalogue status after the rulings

| Class | Count | Disposition |
|---|---|---|
| CP-S01…S17 (stdin), CP-N01…N02 (network) | 19 | **byte-parity scope** (degraded 29 bytes, exit 0) |
| CP-T01…T07 (transcript) | 7 | **owner-approved deviation D4-EX-2**: Go skips the line (BC-SL-098); Go table tests only |
| CP-C01…C10 (foreign cache) | 10 | **known differences, out of byte-parity scope** (ruling b); Go writer format obligation instead |
| CP-X01, X02 (import-time env parse) | 2 | parity scope: empty stdout, exit 1 |
| CP-X03, X04 | 2 | not parity-relevant |
| CP-A01…A03 (`--subagent`) | 3 | pending the scope decision |
| **Total** | **43** | |

---

## B. Proxy (P3)

### B1. Stream-mode decision table and mitmproxy semantics (BC-PX-037, BC-PX-038; target 7)

`responseheaders` (`dgx_proxy.py:191-208`) decides each response's body mode; the code runs in this order:

| Response | `flow.response.stream` | Body in `response()` |
|---|---|---|
| any host, `content-type` contains `text/event-stream` | `_SSETap().feed` (callable) | not retained |
| `/v1/messages*`, `application/json` **or** status ≥ 400 | `False` (buffered) | full body |
| `/v1/messages*`, anything else (e.g. `text/plain`, missing type) | `True` | not retained |
| any other path, non-SSE | untouched (mitmproxy default: buffered; the launcher sets no `stream_large_bodies`, `claude-dgx:76`) | full body |

**Assumed mitmproxy semantics** (no network access; the repo does not pin the `.mitmenv` version). The reasoning
assumes the **sans-IO proxy core of mitmproxy 7.x through 11.x**. **All of this must be verified in P3 against the
venv's actual version.**

1. The http1/h2 layers create the `Response` with `content=None`. On a buffered body, the end of the message sets
   `response.data.content = b"".join(buffer)`. On a streamed body (True or callable) the content stays **None**.
2. `Message.get_text(strict=False)` returns **None** when `raw_content is None`.
3. With a callable stream, each `ResponseData` chunk is replaced by `stream(chunk)`. Some versions also call
   `stream(b"")` at end-of-message and forward a non-empty result. `feed(b"")` is a no-op (it rescans nothing), so
   the output is the same either way.
4. The `response` hook fires after the end of message for streamed flows too.
5. An exception escaping an addon hook is logged ("Addon error") and the flow **continues** with the state applied so
   far (the outcome assumption of pass-2 P-R1…R4).
6. When a connection drops mid-body before the response completes, mitmproxy sets `flow.error` and fires the `error`
   hook **instead of** `response` (it avoids firing both).

**BC-PX-038 (decides round 1 BC-PX-034 path (b)):** for a streamed Anthropic flow whose tap saw no qualifying event,
`json.loads(get_text(strict=False))` gets None under assumption 2. That raises TypeError, caught at `:234`. If some
version returned `""` or the raw SSE text, `json.loads` would raise ValueError, also caught. **The outcome is the same
in every case:** `in_tok` stays None, `anth_reply` has no token fields, and no `anth_usage` is written. Path (b)
yields tokens only for buffered (`application/json`) replies. This part of the conclusion is **version-independent**.

**P-S4 (new proxy crash path, version-dependent):** DGX response with status ≥ 400 **and** an SSE content type (tap
installed, body not retained). `:287` evaluates `flow.response.get_text(strict=False)[:600]`, and under assumption 2
that is `None[:600]` → TypeError escapes `response()`. `dgx_reply` and `dgx_usage` (`:272-282`) are already written;
the error-body note and the `failed-req-*.json` capture (`:288-299`) are lost. Reachability: LOW, because vLLM sends
errors as JSON with status ≥ 400 (buffered) and mid-stream errors as SSE with status 200.

### B2. Interrupted streams (BC-PX-039, assumption-dependent, MEDIUM-LOW)

Under assumption 6, a user interrupt (Esc) during a streamed reply closes the client connection. The `error` hook then
fires and `response` does not. Ledger result: `dgx_request` followed by `dgx_upstream_error {error: str(flow.error),
…attrib}` (`:311-323`), with **no** `dgx_reply` or `dgx_usage` (the tap's partial usage is discarded), plus the
decision note `   DGX UPSTREAM ERROR (project=…): <msg>`. The Anthropic lane writes `anthropic_upstream_error`,
which the exporter ignores. **Exporter consequence:** every interrupted DGX generation adds 1 to
`dgx_llm_request_errors_total{project,user}` (exporter `:208-210`), and its tokens are never counted. P3 must verify
this: the exact error text and whether mitmproxy fires `error` here. It is an owner check on the private ledger, so it
is not done here.

### B3. SSE tap chunk-boundary dependence (BC-PX-040)

Pinned (`tap.py`): bytes `message_start + bad_delta(input_tokens:"abc") + good_delta(11, 12)` delivered as **one**
chunk give `usage=None`, `stop=None` (the exception aborts the rest of the block). Delivered as **two** chunks
(`…bad` | `good`) they give `usage=(11, 12)`, `stop=max_tokens`. Also chunk-dependent: the 64,000-byte tail cap
(`:408-409`). A line longer than 64,000 bytes survives when its pieces arrive in chunks that each leave ≤ 64,000
unterminated bytes in `buf`, and loses its `data: ` head otherwise. For well-formed streams with lines under 64,000
bytes, the tap result **does not depend on chunking**. P3 replay rule: replay captured chunk boundaries, or restrict
the corpus to well-formed streams. A trailing line without `\n` is never scanned (`buf=123` left over, pinned).

### B4. `normalize_for_dgx` re-serialization, byte level (BC-PX-041; target 8)

`proxynorm.py` replicates `:143-150`: normalize, rewrite the model when it differs from `DGX_SERVED_MODEL`, and call
`json.dumps(req)` **only if something changed**.

| Case | In → out | Bytes |
|---|---|---|
| R1 model == served, every tool has `input_schema`, no foreign blocks | **original bytes forwarded unchanged** (compact separators, raw UTF-8 kept) | 158 → 158 |
| R2 model rewrite only | Python separators; `"top_p":1e-1` → `0.1`; `1.0` stays `1.0`; the int `12345678901234567890` is exact; every non-ASCII character escaped (`é` → backslash-u `00e9`, `中` → backslash-u `4e2d`, an emoji → a surrogate pair); `</x>` and `/` unescaped | 213 → 235 |
| R3 duplicate `model` keys + float forms | duplicates collapse (last wins, first position, then the rewrite); `1.10` → `1.1`; `1e2` → `100.0`; `1E400` → **`Infinity`** (invalid JSON for the backend); `-0.0` kept; `5e-324` kept | 104 → 91 |
| R4 model == served, one tool without `input_schema` | re-serialized only because of the schema injection: `{"name": "WebSearch", "input_schema": {"type": "object", "properties": {}}}` | 60 → 118 |

Tool-set rebuild when `changed` (pinned): input tools `[A, B, {nameless}, "junk", A(v2)]` with a `tool_addition` C, a
`tool_removal` B and a `tool_removal` A → output tools `[C]`. Nameless and non-dict tools are **dropped**; duplicate
names collapse to the first position with the last definition. A message emptied by removals becomes
`[{"type": "text", "text": "(tools updated)"}]`. A `tool_addition` without a definition is dropped and adds nothing.
An unknown block type is dropped and noted once per process (`dropping unknown content block type for DGX: <type>
keys=[…]`). A block with no `type` is kept. A non-list `tools` (dict, str, None) is treated as `[]`: with no foreign
blocks it is left untouched in the body; when changed, it is **replaced by a list** (`[{"name": "C"}]`). Crash inputs
(pass-2 P-R3): `messages` as a dict or with a non-dict element → AttributeError. Non-dict blocks inside a list
content are kept, not an error. The body's `Content-Length` after `set_text` is mitmproxy's job (LOW, verify in P3).
The replay oracle compares bytes **after** this function.

### B5. `uses_server_tool` (BC-PX-042)

Pinned: `None`, `[]`, `0`, `false` → False. A dict (iterates its keys), a str (iterates chars), a list of strs, a dict
whose type is None (`str(None)` = `"None"`) or 5, a dict with a matching `name` but no matching `type`, and the
case-variant `Web_search_x` → False. `web_search_*`, `web_fetch_*` and `code_execution_*` types → True. **A truthy
non-iterable (`1`, `true`, `1.5`) → TypeError** (pass-2 P-R2: fails open to Anthropic, no `anth_request`).

---

## C. Stop hook (P4)

### C1. Kev median timing (BC-HK-022; target 9; same as pass-2 H-04)

`kev_pdone_median` (`auto_continue.py:124-138`) overwrites `t` on **every** call. Early stop requires
`len(ps) >= 2 and t is not None and t > KEV_TIMEOUT/2` (1.25 s by default), using the **last** call's elapsed time.
Pinned with a fake `kev_pdone` (`hookkev.py`):

| Sequence (p, elapsed) | Returns | Calls |
|---|---|---|
| (.3,.01) (.5,.01) (.6,.01) | (0.5, 0.01) | 3 |
| (.3,2.0) (.5,1.3) … | (0.5, 1.3), early stop | 2 |
| (.3,.01) (.5,1.25) (.9,.01) | (0.5, 0.01): 1.25 is not > 1.25 | 3 |
| (.2,3.0) (.8,3.0) … | (0.8, 3.0): **upper** value of 2 | 2 |
| (.3,2.0) (.5,.1) (None,None) | **(0.5, None)** | 3 |
| (.3,.1) (None,None) (None,None) | **(0.3, None)** | 3 |
| (None,None) (.3,.1) (.4,.1) | (0.4, 0.1) | 3 |
| (.3,2.0) (None,None) (.4,1.3) | (0.4, 1.3) | 3 |
| 3 × (None,None) | (None, None) | 3 |

`main()` then formats `({secs:.2f}s)` (`:250`). With `secs=None` that raises TypeError: **exit 1, no stdout, no log
line** (pinned: "kev last call fails"). The stop is therefore allowed and invisible to the exporter. The "early stop
after a failed last call" question from round 1's gap 9 is now answered: a failed last call sets `t=None`, so it never
stops early. It also crashes whenever it was the final attempt and an earlier one succeeded.

### C2. Log line ↔ exporter tally coupling (BC-HK-023 and BC-EX-019; target 9)

Pinned log lines (`time.strftime` local; test TZ=UTC):

- `2026-11-14 00:10:09 [kev-allow] kev=p_done=0.800 fake=False (0.01s) session=sess-1 stop_hook_active=False tail='All 14 tests pass. Report written.'`
- `… [kev-continue] kev=p_done=0.200 fake=True (0.01s) session=sess-1 stop_hook_active=False tail="Now I'll run the linter on café"`. The `repr` switches to double quotes when the text contains `'`, and printable non-ASCII stays raw.
- `… [heuristic-continue] kev=unreachable session=sess-1 stop_hook_active=False tail='Tests pass.\tNow I\'ll run "lint" on it\'s café'`. Tab is escaped as `\t`; with both quote kinds present, `repr` keeps single quotes and escapes `'`.
- `… [colon-fake] kev=- session=… tail='Here is the plan for the next step:'`; `session=None` when the session id is absent.
- **No log line** when Kev is unreachable and the heuristic says False, and none on H-04.

Exporter tally consequences, pinned with `exporter.py` on a 4-line log:

1. if/elif substring order on the **whole line**: a `heuristic-continue` line whose tail contains ` [kev-continue]`
   is counted as `kev_caught`, and `heuristic` stays 0.
2. `p_done_latest` = the **first** `p_done=([0-9.]+)` match of the last line that has one. On a `kev=unreachable`
   line that is the user text in `tail`: pinned `dgx_llm_fakestop_p_done_latest 0.990` from a heuristic line's tail.
3. `[non-english]` lines are **never tallied** (no branch). `kev_plus_opus` is always 0 because `opus_verdict`
   (`:141-166`) is never called (dead code).

A Go hook therefore needs a `pyrepr` for log parity, and the Go exporter must keep this substring logic during P2
parity (D7).

---

## D. Exporter (P2): function-level contracts (target 10)

Crash IDs E-01…E-09, E-20 and E-21 and the state-entity model are in pass-2 r2 §5. They are not repeated here. This
section adds the pinned exposition and process contracts.

**BC-EX-018 (exposition golden).** `exporter.py` drives the copied `Handler.do_GET` with a stub socket and a
12-line synthetic ledger: dgx request/reply/usage with `cache_read_tok`; anth request/reply/usage with cache fields;
`anth_ratelimit`; `dgx_upstream_error`; a 502 `dgx_reply` with project `pro"j\x` + newline + `y`; a non-JSON line; an
empty line; an `anth_reply` whose `t` is `bad-time`. Pinned: status 200, `Content-Type: text/plain; version=0.0.4`,
`Content-Length: 5797`. Samples, in emission order:

```text
dgx_llm_requests_total{project="home-lab",user="u",model="claude-sonnet-5-5",account="acct1234",device="dev12345"} 1
dgx_llm_est_prompt_tokens_total{project="home-lab",user="u",account="acct1234"} 1000
dgx_llm_tokens_input_total{project="home-lab",user="u",account="acct1234"} 900
dgx_llm_tokens_output_total{project="home-lab",user="u",account="acct1234"} 120
dgx_llm_tokens_cache_read_total{project="home-lab",user="u",account="acct1234"} 800
dgx_llm_tokens_input_captured_total{project="home-lab",user="u",account="acct1234"} 900
dgx_llm_anthropic_requests_total{project="home-lab",user="u",model="claude-opus-5-5",account="unknown"} 1
dgx_llm_anthropic_tokens_input_total{…,model="claude-opus-5-5",account="acct1234"} 5
dgx_llm_anthropic_tokens_output_total{…} 50
dgx_llm_anthropic_request_duration_seconds_sum{…} 0.000
dgx_llm_anthropic_request_duration_seconds_count{…} 0
dgx_llm_anthropic_tokens_cache_read_total{…} 1000
dgx_llm_anthropic_tokens_cache_write_total{…,ttl="5m"} 0
dgx_llm_anthropic_tokens_cache_write_total{…,ttl="1h"} 300
dgx_llm_anthropic_usage_cache_captured_total{…} 1
dgx_llm_request_duration_seconds_sum{project="home-lab",user="u"} 5.123
dgx_llm_request_duration_seconds_count{project="home-lab",user="u"} 1
dgx_llm_request_errors_total{project="home-lab",user="u"} 1
dgx_llm_request_errors_total{project="pro\"j\\x y",user="u"} 1
dgx_llm_anthropic_passthrough_total 2
dgx_llm_last_request_timestamp_seconds 1794650610
dgx_llm_last_dgx_request_timestamp_seconds 1794650400
dgx_llm_last_anthropic_request_timestamp_seconds 1794650460
dgx_llm_session_requests{session="sess-aaa",project="home-lab",user="u"} 1
dgx_llm_session_tokens_in{…} 900
dgx_llm_session_tokens_out{…} 120
dgx_llm_session_errors{…} 0
dgx_llm_fakestop_events{kind="kev_caught"} 2
dgx_llm_fakestop_events{kind="colon_caught"} 0
dgx_llm_fakestop_events{kind="heuristic"} 0
dgx_llm_fakestop_events{kind="kev_plus_opus"} 0
dgx_llm_fakestop_events{kind="allowed"} 1
dgx_llm_fakestop_p_done_latest 0.990
```

(`…` repeats the preceding row's label set; the full body is reproducible with `exporter.py`.) Pinned rules:
`est_prompt` 4002/4 = 1000.5 → `1000` (half-even). The 1h cache write is clamped to the total
(`min(400, 300)` → 1h 300, 5m 0). Errors count both the 502 reply and the upstream error. `esc` turns `\` into `\\`,
`"` into `\"` and newline into a space. `passthrough` counts the `bad-time` reply (a bad `t` is ignored, the event
still counts). The session label is truncated to 8 chars. HELP/TYPE pairs for input/output tokens are emitted
**together before both families' samples**. `dgx_llm_session_tokens` has HELP/TYPE but no samples, and the samples
`…_tokens_in/_out/_errors` are untyped. The `…_count` families have TYPE without HELP. Time gauges are `.0f` of
**naive local** `strptime` (TZ=UTC here: 10:03:30 → 1794650610).

**BC-EX-020 (DST false idle).** The proxy writes `t` as naive local time (`dgx_proxy.py:60`), and the exporter parses
it naive with `fold=0` (`:125`). Pinned under `TZ=America/Chicago`: the real instants 1793514600 (01:30 CDT) and
1793518200 (01:30 CST) both serialize to `2026-11-01T01:30:00` and both parse to **1793514600.0**, so the second is
3600 s early. During the repeated hour each autumn, `last_dgx_ts` (a max) stays at the end of the first pass. The
status line idle widget (`:824-834`) then shows `☾ idle Nm` during active use, whenever more than 300 s have passed
since the first pass's last request and nothing is running. D7 freezes the ledger format, so Go reproduces this.

**BC-EX-021 (crash process contract; complements pass-2 E-*).** Pinned for E-01, E-02, E-04, E-05 (NaN),
E-06/E-03 (list session), E-07 (status null or string), E-08 (`account_uuid` 5), E-09 (byte 0xFF in the ledger, UTF-8
strict), E-20 (int project; mixed-type sort) and E-21 (int session). In every case the handler raises **before**
`send_response`, so the client receives zero bytes. On a rebuild-phase crash, `processed_size` stays at its previous
value (here -1), so every later scrape retries and fails identically (`scrape2 == scrape1`, pinned). An
exposition-phase crash updates `processed_size` first and is just as permanent. Non-crashes pinned: `status: NaN`
(comparison false), `in_tok: "12"` (→ 12), `in_tok: 1.9` (→ 1).

**BC-EX-022 (routing and rebuild trigger, confirmed by pin).** A path other than `/metrics` → 404 with an empty body
and no `Content-Type`. `?rebuild=1` → rebuild. The size-change rule as in pass-2 r2.

**BC-EX-023 (deploy artifact, LOW).** The scrubbed plist passes `~/hylo/legacy/dgx_ledger_exporter.py` in
`ProgramArguments`. launchd does no tilde expansion, so this copy cannot start as written. It is a scrub artifact; the
real agent's path is private. It runs `/usr/bin/python3` (3.9.6 here), so the exporter's oracle interpreter is 3.9
(pass-2 r2 §1.4).

---

## Delta Summary

- **New BCs:** status line 10 (BC-SL-089 goldens, 090 trim breakpoints, 091 get_sample sequence, 092 HIST_MIN_GAP
  reachability, 093 effective_rl sequence, 094 turn-machine table, 095 turn identity, 096 dumps-length oracle,
  097 `--subagent`, 098 D4-EX-2 Go contract). Proxy 6 (BC-PX-037…042). Hook 2 (BC-HK-022, 023). Exporter 6
  (BC-EX-018…023).
- **New crash paths:** CP-A01…A03 (status line, second entry point) and P-S4 (proxy, version-dependent). The status
  line total is now 43.
- **Refined:** BC-SL-054 (single reset at ♻), 041 (KEEP_DEAD sequence pinned), 068 and CP-T01…T07 (D4-EX-2 plus
  corrected predicates), 076 (strict mode ruled), CP-S09 (cache written before the crash; recovery rules). BC-PX-017
  and 033 (in-event partial effects, chunk dependence), 034 path (b) decided, 005 (I1 confirmed), 031 (CONV-ABS-7).
  BC-EX-014 (first match per line, tag misattribution, non-english untallied, opus dead). BC-HK-010 (timing and
  crash). Total refined: 14.
- **Retractions:** CONV-ABS-6 (CP-T predicates too broad), CONV-ABS-7 (rotate does not always touch `args.force`).
- **Confirmed:** 40-path count for `main()`, I1, I2, pass-2 r2 H-04, P-R4 line order.
- **Owner rulings applied:** (a) strict stdio; (b) CP-C out of scope plus the Go writer format obligation; (c)
  D4-EX-2; D4-EX-1 named.

## Remaining Gaps (verbatim-carryable)

1. Proxy, mitmproxy semantics: verify assumptions 1–6 of §B1 against the `.mitmenv` mitmproxy version (record the
   version). In particular: `get_text(strict=False)` on streamed flows (None vs `""`, decides P-S4); `error` vs
   `response` on a client disconnect mid-stream and the exact `str(flow.error)` text (decides BC-PX-039 and the
   exporter error count); addon-exception continuation (pass-2 P-R1…R4); `Content-Length` after `set_text`.
2. Owner check on the private ledger (not done here): count `dgx_upstream_error` events whose `error` reads like a
   client disconnect, to confirm that interrupted generations inflate `dgx_llm_request_errors_total`.
3. Status line: a Go-side table-test list derived from BC-SL-098. Each W-predicate needs a positive case and its
   look-alike negative, with the expected mix-cache JSON (the "delete the line" oracle). Generate these from legacy
   on the reduced transcripts so `size` is the only adjusted field.
4. Status line: cost-history coloring goldens with ≥ 10 seeded sessions (p75/p95 colors for `$` and `$/h`, including
   the `src: "cc"` 300,000 vs backfill 1,800,000 rate gates and the self-exclusion with numeric sids). Not pinned yet;
   the goldens above use cold start only.
5. Backfill (`tools/backfill_cost_history.py`) function-level BCs with pinned examples (pass-2 r2 §7 has the domain
   table; contracts are not written yet).
6. Exporter: whether VictoriaMetrics' scrape parser accepts the interleaved HELP/TYPE and the untyped
   `dgx_llm_session_tokens_*` samples (it does in production today; a strict Prometheus text parser may not). This
   matters if Go switches to a client library (would change bytes; D7).

## Owner decisions pending (new this round; pass-2 r2 §8 items are not repeated)

1. **CP-T05 detection point** (BC-SL-098): the precise form chosen here skips the **opening** line that carries the
   non-numeric `output_tokens` (when `lu` is set). Confirm this, or instead skip the turn only (keep the line's
   composition and close nothing).
2. **Interrupted generations counted as DGX errors** (BC-PX-039, if verified): reproduce in P2/P3 parity (D7), or
   separate "client cancelled" from errors later?
3. **P-S4** (`None[:600]` on an SSE error reply, if verified): reproduce, or treat it as an approved deviation (Go
   logs the error body capture)?
4. **Exporter DST false idle** (BC-EX-020): accept as a known legacy behavior through cutover (D7), or record an
   offset in a new ledger field after cutover?
5. **Exporter tally misattribution** (BC-EX-019: tags and `p_done=` inside `tail` count): reproduce during P2 parity
   (implied by D7), and fix after cutover?

## Novelty Assessment

Novelty: SUBSTANTIVE

Removing this round would change the spec:

- the owner-approved deviation D4-EX-2 now has an exact, testable Go contract (seven W-predicates plus a
  delete-the-line oracle), and round 1's crash predicates were wrong in five places (CONV-ABS-6);
- a second status line entry point with three crash paths was missing from the catalogue;
- the mitmproxy analysis closes BC-PX-034 path (b) in a version-independent way and surfaces two new behaviors: a
  version-dependent crash (P-S4), and interrupted streams turned into DGX error counts (BC-PX-039);
- the tap's output depends on TCP chunk boundaries for malformed streams (a P3 replay design constraint);
- new exporter contracts: DST false idle in the status line, tally misattribution, and zero-byte permanent scrape
  failure;
- pinned goldens, trim breakpoints, state-machine sequences and a 63-case length oracle give P1 its first end-to-end
  byte fixtures.

## Convergence Declaration

Another round is needed. Substantive gaps remain: the mitmproxy verification set (gap 1), table-test derivation for
D4-EX-2 (gap 3), cost-coloring goldens (gap 4) and backfill contracts (gap 5).

## State Checkpoint
```yaml
pass: 3
round: 2
status: complete
files_scanned: 11
timestamp: 2026-11-14T09:30:00Z
novelty: SUBSTANTIVE
new_bcs: {SL: 10, PX: 6, HK: 2, EX: 6}
refined_bcs: 14
new_crash_paths: {CP-A: 3, P-S4: 1}
status_line_crash_total: 43
retractions: [CONV-ABS-6, CONV-ABS-7]
owner_rulings_applied: [a-strict-stdio, b-foreign-cache-out-of-scope, c-D4-EX-2, D4-EX-1-named]
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r2/
next: pass 3 round 3 (carry "Remaining Gaps" verbatim)
```
