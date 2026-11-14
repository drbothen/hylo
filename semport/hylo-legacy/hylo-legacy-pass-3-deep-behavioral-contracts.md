# Pass 3 deepening, round 1: behavioral contracts (hylo-legacy)

- **Scope:** `legacy/` only (11 files, 3,181 lines, recounted with `find … -exec wc -l`). Priority is the status line
  (`legacy/dgx_statusline.py`), because P1 ports it byte for byte. After that: the proxy items I1 and I2 and the
  consequence of BC-PX-017, then the Stop hook's regex fallback.
- **Inputs read:** every file in `.factory/semport/hylo-legacy/` (passes 0–6 and the extraction validation),
  `docs/PLAN.md` (D1–D15), `docs/STATUSLINE-WIDGETS.md`, `docs/STATUSLINE-REVIEW-2026-11-13.md`, and
  `.factory/specs/research/general-go-port-parity-crossplatform-2026-11-14.md` (pitfalls P1–P27). I also read
  `legacy/dgx_statusline.py`, `legacy/dgx_proxy.py` and `legacy/auto_continue.py` in full.
- **Method:** static reading, plus isolated pinning scripts in the session scratchpad
  (`/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/pin/`,
  run with `python3.11 -I`, CPython 3.11.7). They copy legacy functions or expressions and never import a legacy
  module. The transcript parser was copied verbatim (`dgx_statusline.py:190-206,951-1154` into `mixcopy.py`). It
  ran against synthetic transcripts and wrote caches only into the scratchpad. Go RE2 compile checks ran with
  go1.26.5 (`scratchpad/re2/main.go`). The FMA probe used `math.fma` from Python 3.13. Nothing in `legacy/` was
  executed, modified or networked.
- **Notation:** `\e` = ESC (0x1B). Glyphs appear literally. "pinned" means the output shown was produced by running
  the copied expression. Line cites without a file are `dgx_statusline.py`.
- **IDs:** the existing BC IDs are kept (policy 1, append-only). New BCs continue each series: BC-SL-054…088,
  BC-PX-032…036, BC-HK-014…021. Crash paths have their own series, CP-*.

---

## 0. Audit of the broad sweep against the 5 known hallucination classes

| Class | Finding | Action |
|---|---|---|
| Over-extrapolated token lists | None. Glyph sets, label sets and the CJK ranges were checked against the source bytes. The CJK class is exactly U+3040–30FF, U+3400–4DBF, U+4E00–9FFF, U+AC00–D7AF, U+F900–FAFF (`auto_continue.py:184`, decoded from the file) | — |
| Miscounted enumerations | None. 53 SL / 31 PX / 13 HK BCs recounted | — |
| Fabricated named patterns | None | — |
| Same-basename conflation | None | — |
| Inflated/deflated metrics | Line counts re-derived: 1245 / 764 / 275 / 3181 total. All match | — |

**Refinements to broad-sweep BCs** (not retractions; each is pinned below):

- BC-SL-004: "appending RESET after each cut" really means each trimmed row ends with exactly one extra RESET, so
  the row closes with a double reset `…\e[0m\e[0m` (pinned).
- BC-SL-011: the "no /0K denominator" v2 fix in the docstring (`:55-56`) is only partial. A total of 0 < t ≤ 500
  renders `/0K`, and 999,500 ≤ t < 1,000,000 renders `/1000K` (pinned).
- BC-SL-032: long-line completion runs only when the first 512 KB blob contains no newline at all. A long line
  that follows a short line takes two refreshes (pinned).
- BC-SL-034/039: dedup keeps the **first** line's usage for a message id. Both the session totals and the turn's
  `out` therefore come from the first transcript line of each message (pinned).

**Contradictions with the research input (flagged, not adopted):**

- **CONTRA-1** (research `general-go-port…` P7 / §2b) says "`math.Floor(a/b)` can differ" for `rem//86400`,
  `ms//60000` and similar. Pinned: zero divergences in about 600k boundary candidates (one or two ulps below
  k·b for k < 200,000) and 2M realistic `(now-start)*1000` samples, for the divisors 60000, 86400, 3600 and 60.
  For these exact-integer divisors the hazard is **theoretical**. Porting CPython `float_divmod` is still
  cheap insurance.
- **CONTRA-2** (research `domain-hybrid-routing…` line 148) says the prototype's SSE tap "merge[s] the fields
  that are present … exactly what the prototype's SSE usage tap must keep doing". The source does **not** merge.
  It replaces `(in, out)` from the last event whose top-level `usage` has an `input_tokens` key, and it ignores
  output-only deltas (`dgx_proxy.py:418-420`). See BC-PX-033.
- **CONTRA-3** (research Q3a, harness shim) recommends `PYTHONUTF8=1`. That **changes legacy behavior** on
  invalid-UTF-8 stdin: strict mode gives `{}` and the "?" defaults, while UTF-8 mode passes the raw bytes through
  (pinned, BC-SL-076). The harness must pin the production locale mode, not UTF-8 mode, unless the owner rules
  otherwise.

---

## A. Status line: function-level contracts

### A0. Inputs each function reads (what a test must pin)

| Function | Clock (`time.time`) | Env | Network | Process tree | Cache files | Filesystem / other |
|---|---|---|---|---|---|---|
| module import | — | `DGX_SL_VM_URL :73`, `DGX_SL_TTL :74`, `DGX_SL_ROWS :75`, `DGX_SL_SPARK :76`, `DGX_SL_GIT :77`, `DGX_SL_TRACE :89`, `HOME` (`expanduser :78`) | — | — | — | — |
| `main` `:1200-1235` | via callees | `COLUMNS :1186` (read twice, `:1209,1211`) | via `get_sample` | via `claude_window_start` | all four | stdin bytes, **stdio locale mode** (BC-SL-076) |
| `_mix_counts` `:999-1154` | — | `TZ` (naive timestamps, `:983`) | — | — | `statusline-mix-<sanitized sid>.json` | transcript file (size, bytes) |
| `effective_rl` `:298-312` | `:304` | — | — | — | `statusline-<sid>.json` (`rl`, `rl_ts`) | — |
| `get_sample` `:315-359` | `:322` | `TTL` | VM `/api/v1/query` (timeout 1.5 s, proxy bypass `:168`) | — | `statusline-<sid>.json` (`fetch_ts, up, ts, sample, hist`) | — |
| `claude_window_start` `:265-295` | — (`mktime` uses `TZ`) | locale of `ps` output (`LC_TIME`) | — | `getppid` + up to 6 `ps` calls | `proc_start` | `ps` binary (absent on Windows) |
| `git_segment`/`git_branch` `:364-413` | `:408` | `DGX_SL_GIT` | — | — | `statusline-git-<sha1[:16]>.json` | `.git`, `HEAD`, cwd fallback `:373` |
| `render_lane` limits `:499` | `:499` | `LOCAL_MODEL_PREFIXES :444` | — | — | — | — |
| `render_lane` window age `:558` | `:558` | — | — | — | — | — |
| `record_cost`/`cost_thresholds` `:224-262` | `:231`, `:243` | — | — | — | `cost-history.json` | — |
| idle `:824-834` | `:825` **and** `:826` (two reads) | — | — | — | — | — |
| `sparkline` `:659-690` | — | `DGX_SL_TRACE`, `DGX_SL_SPARK` | — | — | `hist` | — |

Harness rule: freeze **all nine** clock reads to one value. Idle reads the clock twice. With a live clock the
condition (`:825`) and the displayed age (`:826`) can straddle a minute boundary, which a frozen clock hides. Go
should read the clock once per render (an output-neutral deviation under a frozen clock).

### A1. Primitives

| ID | Contract | Pinned examples / edges | Evidence | Pitfalls |
|---|---|---|---|---|
| BC-SL-056 (new) | `heat(pct)`: `h = (1.0 - min(max(pct,0.0),100.0)/100.0) * 0.22`, then `colorsys.hsv_to_rgb(h, 0.85, 0.80)` and `int(c*255)` per channel. CPython's colorsys order is `i=int(h*6.0)`, `f=(h*6.0)-i`, `p=v*(1.0-s)`, `q=v*(1.0-s*f)`, `t=v*(1.0-s*(1.0-f))`, `i%6` selects `(v,t,p)` or `(q,v,p)` (h ≤ 0.22, so i ∈ {0,1}) | Cell colors `(i+0.5)*10` for i=0..9: (159,204,30) (182,204,30) (204,202,30) (204,179,30) (204,156,30) (204,133,30) (204,110,30) (204,87,30) (204,64,30) (204,42,30). heat(0)=(148,204,30), heat(50.4)=(204,144,30), heat(51)=(204,142,30), heat(84.5)=(204,66,30), heat(100)=heat(150)=heat(inf)=(204,30,30), heat(-5)=(148,204,30). heat(NaN): `max(nan,0.0)` keeps nan, then `int(nan*255)` → ValueError. It is unreachable from fmt_ctx, because `:426` raises first | `:144-148` | PT-NANMM, PT-INT, PT-FMA |
| FMA evidence | Fused versus unfused colorsys (`f=fma(h,6,-i)`, `q=v*fma(-s,f,1)`, `t=v*fma(-s,1-f,1)`) gave **0 byte differences** over pct 0.00…100.00 in 0.01 steps and over the 10 cell values (pinned with py3.13 `math.fma`) | Keep explicit `float64()` conversions anyway. The hazard is unobserved, not disproven | — | PT-FMA |
| BC-SL-054 (new) | `trim_to_fit(row, cols)`: while `visible(row) > cols` and SEP is in the row, `row = row.rsplit(SEP,1)[0] + RESET`. The result ends in exactly one appended RESET (double reset after a RESET-terminated segment). A row with no SEP is returned unchanged even when too wide | 4-segment row, visible width 40. cols=30 → `…\e[90m⎇ main\e[0m\e[0m` (width 29). cols=25 → width 20. cols=18 or 5 → `\e[106;30;1m ◨ DGX \e[0m\e[0m` (width 7, wider than 5, left as is) | `:1193-1197` | PT-CP |
| BC-SL-004 (refined) | `visible()` counts **code points** after removing `\033\[[0-9;]*m`. Lone surrogates count 1. Wide CJK and emoji count 1. ESC sequences arriving in stdin text (e.g. a display name) are stripped too | — | `:137,151-153` | PT-CP, PT-RE (RE2-safe) |
| BC-SL-005 (refined) + BC-SL-055 (new) | `term_cols()` = `int(COLUMNS)`, otherwise 0. Python `int()` grammar: whitespace, `+`, `_` separators and Unicode digits are accepted; `"80.0"`, `"0x50"` and `""` give 0. **New:** negative COLUMNS (e.g. `-5`) disables trimming (`cols > 0` is false) **and hides row 2** when ROWS == 2 (`cols == 0 or cols >= 72` is false). ROWS > 2 still forces row 2 | Pinned: `" 80 "`→80, `"٨٠"`→80, `"1_000"`→1000, `"+72"`→72, 30 nines → exact big int (Go `Atoi` overflows to an error → 0; the output is identical, since both mean "no trim, row 2 shown"). Strings over 4,300 digits → ValueError → 0 | `:1185-1190,1224,1232` | PT-PARSE |

### A2. Formatting helpers

| ID | Contract | Pinned examples | Evidence | Pitfalls |
|---|---|---|---|---|
| BC-SL-019 (refined) + BC-SL-063 (new) | `_fmt_lines(n)`: `int(n)` (truncates floats, parses numeric strings with whitespace); TypeError or ValueError → `"?"`; ≥ 1,000,000 → `f"{n/1e6:.1f}M"`; ≥ 10,000 → `f"{n//1000}k"`; otherwise `str(n)`. **New:** ±Infinity raises **OverflowError, which is not caught** → crash (CP-S11) | 0→`0`, -5→`-5`, 9999→`9999`, 10000→`10k`, 12345.9→`12k`, 999999→`999k`, 1e6→`1.0M`, 1,050,000→`1.1M`, 1,250,000→`1.2M` (half-even on an exact tie), 1,350,000→`1.4M`, -20000→`-20000`, `"12"`→`12`, `" 42 "`→`42`, `"1e3"`→`?`, `"abc"`→`?`, `True`→`1`, `[1]`→`?`, NaN→`?` | `:849-860` | PT-INT, PT-FMT, PT-BOOL, PT-PARSE |
| BC-SL-024 (refined) + BC-SL-062 (new) | `_fmt_tok_c(n)`: `float(n)`; error → `"?"`; ≥ 1e6 → `.1f`+`M`; ≥ 1000 → `.0f`+`k`; otherwise `.0f`. **New:** a half-even rounding result is **not promoted** to the next unit | 999.4→`999`, **999.5→`1000`**, 1000→`1k`, 1500→`2k`, **2500→`2k`**, 3500→`4k`, 999,499→`999k`, **999,500→`1000k`**, 999,999→`1000k`, 1,049,999→`1.0M`, 1,050,000→`1.1M`, 1,250,000→`1.2M`, NaN→`nan`, inf→`infM`, `"1e3"`→`1k`, None→`?`, True→`1`, -5→`-5` | `:863-873` | PT-FMT (half-even, nan/inf spelling), PT-PARSE |
| BC-SL-020 (refined) + BC-SL-064 (new) | `_hm(ms)`: `mins=int(ms//60000)`, then `h{m:02d}m` when mins ≥ 60, otherwise `{m}m`. **New:** `ms=+inf` gives `inf//60000 = nan`, and `int(nan)` raises ValueError (CP-S12, CP-S13) | 60001→`1m`, 119999→`1m`, 120000→`2m`, 3,599,999→`59m`, 3,600,000→`1h00m`, 4,500,000→`1h15m`, 6,000,000→`1h40m`, 7,500,000→`2h05m`, 90,000,000→`25h00m`, 26,700,000.0→`7h25m`, nextafter(120000,0)→`1m` | `:545-548` | PT-FDIV (CONTRA-1), PT-INT |
| Countdown (BC-SL-017 refined) | `rem ≥ 86400` → `{int(rem//86400)}d{int((rem%86400)//3600):02d}h`; `≥ 3600` → `{h}h{mm:02d}m`; otherwise `{int(rem//60)}m`. `0 < rem < 60` renders `->0m` | 15480→`4h18m`, 518400→`6d00h`, 544320 (0.9×7d)→`6d07h`, 59→`0m`, 0.5→`0m`, 3600→`1h00m`, 86400→`1d00h`, 1.15×7d=695520→`8d01h` | `:523-530` | PT-FDIV |
| Idle age (BC-SL-051 refined) + BC-SL-084 (new) | `idle_min=int((now-last)//60)`, formatted `d..h` / `h..m` / `m`. The gate is strict: `now-last > 300` | Δ=300.0 → hidden; Δ=300.5 → `☾ idle 5m` (shows 5m, not 6m); 360 → `6m`; 66000 → `18h20m`; 274000 → `3d04h`; running=1 → hidden; running=0.5 → shown (`< 1`); `last`=NaN → hidden (`nan > 0` is false); running NaN → hidden (`nan < 1` is false) | `:824-834` | PT-FDIV, PT-NANMM, PT-BOOL |

### A3. Row-1 widgets

| ID | Contract (function level) | Pinned examples / edges | Evidence | Pitfalls | D15 literals |
|---|---|---|---|---|---|
| BC-SL-006 (refined) | Pill. `prefixes` = `LOCAL_MODEL_PREFIXES.split(",")`, each `.strip()` with **Python Unicode whitespace** (NBSP stripped), empties dropped. The pill uses `startswith` against the raw prefix (so `claude*` never matches), while `reroute_all` uses `rstrip("*")` | `" claude-sonnet ,\u00a0claude-opus\u00a0,, "` → `['claude-sonnet','claude-opus']`. reroute_all: `claude`, `claude*`, `claude-*`, `claude-**` → True; `claude-s`, `Claude` → False | `:444-449,487-488` | PT-SPLIT (strip), PT-BOOL | prefix default `""` (`:444`); pill SGRs `:130` |
| BC-SL-007 (refined) + BC-SL-058 (new) | The model label is `f"{WHITE}{model_name}{RESET}"`, where `model_name = display_name or id or "?"`. **New:** a truthy non-str value renders through Python `str()` | `1e16`→`1e+16`, `True`→`True`, `[1,"a"]`→`[1, 'a']`, `{"k":1.0}`→`{'k': 1.0}`, 12345678901234567890 stays exact, NaN→`nan`. A lone surrogate inside a str crashes at print (CP-S17); inside a list/dict it is escaped by repr (no crash) | `:441-443,453` | PT-STR, PT-ENC | — |
| BC-SL-008 (refined) + BC-SL-059 (new) | Project label = `basename(normpath(d)) or normpath(d)`. **New:** POSIX `normpath` keeps exactly two leading slashes, so `"//"` renders `//` (Go `filepath.Clean("//")` = `/` → **divergence**). `"///"`→`/`, `"."`→`.`, `"/a/../b"`→`b`. On Windows (ntpath), `"/"`→`\` and `"//"`→`\\`. An embedded NUL is kept in the label | pinned (posix and nt) | `:458-462` | PT-PATH | — |
| BC-SL-009/010 (confirmed) | Branch lookup is fully guarded (`try/except Exception` → `""`). HEAD is read in **text mode with the locale encoding**, so invalid UTF-8 in HEAD → UnicodeDecodeError → caught → no branch. The cache key is `sha1(dir.encode("utf-8","replace"))[:16]`; `/x/p` → `5a3006e969bd95e3`. A lone surrogate is replaced by `?` before hashing (`/x/\udcff` → `a77db2f8cb13007e`) | — | `:372-396,405` | PT-ENC, PT-PATH | `GIT_TTL=5.0 :99` |
| BC-SL-011 (refined) + BC-SL-057 (new) | Thermometer. `filled=min(int(pct/10+0.5),10)` (half-up). Number color is BOLDRED at ≥ 85, `heat(pct)` above 50, otherwise `""` (RESET is still appended). Denominator: total ≥ 1e6 → `/{t/1e6:.1f}M`; total > 0 → `/{t/1000:.0f}K` (half-even). **New quirks:** 0 < total ≤ 500 → `/0K`; 999,500 ≤ total < 1e6 → `/1000K`; total=True → `/0K`; total=NaN → no denominator (NaN is truthy but fails both comparisons); pct=True → 1%; pct=+inf → 100% with 10 cells; **pct=NaN → crash** (CP-S06); a non-numeric truthy total → crash (CP-S07) | 45%/1.0M → 5 cells + ` 45%\e[0m\e[2m/1.0M\e[0m` (visible 19). 55%/200000 → 6 cells + ` \e[38;2;204;133;30m55%\e[0m\e[2m/200K\e[0m`. 44.9 → 4 cells, text `45%`. 0/999999 → `/1000K`. 50.4/500 → `\e[38;2;204;144;30m50%`, `/0K`. 84.5/501 → `84%` (half-even), heat color, `/1K`. 85/1048576 → `\e[1;91m85%`, `/1.0M`. -3/1500 → `0%`, `/2K` | `:418-437` | PT-INT, PT-FMT, PT-NANMM, PT-BOOL, PT-FMA (heat) | 85, 50 (`:434`), 10 cells, 1e6/1000 |
| BC-SL-012 (refined) | Composition `mix_labels`: `pct=round(n/total*100)` (banker's rounding); body `f"{pct:>2d}%"` when pct > 0, otherwise `" <1%"`. Percentages can sum to 99, 100 or 101 | (1,1,0)→`\e[36m▤50%\e[0m \e[32m❙50%\e[0m`. (1,1,1)→33/33/33 (sum 99). (125,250,625)→`▤12%` `❙25%` `◈62%` (12.5→12, 62.5→62). (1,199,0)→`▤ <1%` `❙100%`. (5,1990,5)→` <1%`,`100%`,` <1%`. (2,2,1)→40/40/20. (7,0,993)→`▤ 1%` `◈99%`. (30,68,2)→`▤30% ❙68% ◈ 2%` | `:1157-1174` | PT-ROUND, PT-FMT | glyph/colour map `:1167` |
| BC-SL-013 (refined) + BC-SL-060 (new) | Cache hit `f"{min(max(hr,0.0),1.0)*100:.0f}%"`. **New:** NaN → `♻ nan%` (no crash); +inf → `100%`; True → `100%` | — | `:477-479` | PT-NANMM, PT-FMT, PT-BOOL | — |
| BC-SL-016 (refined) + BC-SL-061 (new) | Limits. `elapsed = 1.0 - rem/length`; pace bands apply only when `0.10 <= elapsed <= 1.0`. **New boundary:** `rem = 0.9*length` exactly gives elapsed `0.09999999999999998` < 0.10, so the **absolute** bands apply. Pinned: 7d 75% at rem=0.9·7d → YELLOW (absolute >70); 1 s earlier → RED (proj 750). Proj exactly 80 → YELLOW, exactly 100 → YELLOW (`> 100` for red). pct NaN → `7dnan%` in GREY, countdown kept. resets_at NaN → no countdown, absolute bands. pct True → `7d1%`. 44.5 → `44%`, 45.5 → `46%`. A window value of `[]` or `0` counts as absent. **A window value that is truthy and not a dict crashes** (CP-S09) | `both` → `\e[90m5h31%\e[0m \e[90m->2h41m\e[0m␣␣\e[90m7d44%\e[0m \e[90m->4h18m\e[0m` (two spaces between windows) | `:499-532` | PT-FDIV, PT-FMT, PT-NANMM | 0.10, 80, 100, 70, 90, 1.15, labels `5h`/`7d`, lengths 18000/604800 |
| BC-SL-017 (refined) | Countdown shown only when `0 < rem <= length*1.15`. rem = 1.15·7d → `->8d01h`; 1.16·7d → none | — | `:523` | PT-FDIV | 1.15 |
| BC-SL-019 (refined) | Lines segment shown when `la or lr` is truthy. NaN is truthy, so `▲?/▼0` | — | `:534-537` | PT-BOOL | 10,000 / 1e6 |
| BC-SL-020/021 (refined) | Timer shown when `dur > 60000` (NaN hidden; +inf → crash CP-S12). API part when `api >= 60000` (+inf → crash CP-S13) | — | `:539-553` | PT-INT | 60000 |
| BC-SL-022 (refined) + BC-SL-081 (new) | Window age. `win_ms=(time.time()-win_start)*1000`; shown when `win_ms - dur >= 300000`; `wm=int(win_ms//60000)`; wm ≥ 1440 → `{wm//1440}d{(wm%1440)//60:02d}h`, otherwise `_hm(win_ms)` | (now−start, dur): (112000 s, 26.7e6) → `⌂1d07h`; (26999.9 s, 26.7e6) → hidden; (27000 s, 26.7e6) → `⌂7h30m`; (7200, 60001) → `2h00m`; (277200, 60001) → `3d05h`; (86399, 60001) → `23h59m`; (86400, 60001) → `1d00h` | `:557-562` | PT-FDIV, PT-FMA (`:558-559`; 0 diffs in 300k sampled boundary cases, keep the guard) | 300000, 1440 |
| BC-SL-024 (refined) | Tokens use the transcript totals. Values can be floats (float usage) or NaN; `(tin or 0) > 0` is false for NaN. Rebuilds render `f"{rb:.0f}"` | — | `:574-600` | PT-BOOL, PT-FMT | — |
| BC-SL-025/026 (refined) + BC-SL-082 (new) | `$` uses `f"${usd:.2f}"`, which rounds the exact binary value half-even; `$/h` uses `r=usd/(api/3.6e6)` with `.1f` | 0.125→`$0.12`, 0.995→`$0.99`, 1.005→`$1.00`, 2.675→`$2.67`, 999.995→`$1000.00`, True→`$1.00`; (32.62, 6,711,428.57) → `r=17.497318011387254` → ` $17.5/h`; (1.0, 300000) → ` $12.0/h`; usd=+inf → `$inf`, `$inf/h` (recorded as Infinity in cost-history). NaN → hidden (`nan > 0` is false) | `:601-625` | PT-FMT, PT-BOOL | 1.0, 25.0, 300000, 3.6e6 |
| BC-SL-027 (refined) + BC-SL-083 (new) | ⛏ `eq = tot*dgx_mtok/1e6`, shown when `eq >= 0.005`, formatted `.2f`. dgx_mtok NaN or rate NaN → `⛏n/a` | (1000, 5.0) → eq 0.005 → ` ⛏0.01`; (999, 5.0) → 0.004995 → hidden (segment omitted, **not** `n/a`); (2,000,000, 0.09) → `⛏0.18`; mtok=inf → `⛏inf` | `:626-635,1220-1223` | PT-FMT, PT-NANMM | 30.4, 0.005 |

### A4. Transcript parser (`_mix_counts`)

| ID | Contract | Pinned evidence | Evidence | Pitfalls |
|---|---|---|---|---|
| BC-SL-088 (new) | `transcript_path` type semantics: falsy → None. str → normal path. **list, dict or float → TypeError from `os.path.isfile`, i.e. crash** (CP-S16; `genericpath.isfile` catches only OSError/ValueError). **int or bool → treated as a file descriptor** (`os.stat(1)` = stdout); if that fd is a regular file (harness capturing stdout to a file), the parser reads and then *closes* it. The harness must capture through pipes | pinned TypeError for `['a']`, `1.5`, `{'a':1}` | `:1009-1015` | PT-EXC |
| BC-SL-070 (new) | Mix cache name `statusline-mix-%s.json % re.sub(r"[^A-Za-z0-9_-]","_",sid)[:40]`. The substitution is **per code point** and happens before truncation to 40 **code points**. A non-str truthy sid with an existing transcript → crash (CP-S14). The sid defaults to `"nosession"` (shared between id-less sessions) | `a.b/c d`→`a_b_c_d`; `é`×50 → 40 `_` (a Go per-byte substitution would give 2 per `é` before truncation, so mixed strings diverge); `../../etc` → `______etc` | `:1016-1017` | PT-CP, PT-RE (RE2-safe pattern, per-rune semantics required) |
| BC-SL-031 (confirmed) | Reset conditions are evaluated before `size == off`; `need_reset` also clears the id memory | pinned "file shrank → full reset (id memory cleared)" → only post-shrink usage counted | `:1025-1040` | — |
| BC-SL-032 (refined) + BC-SL-066 (new) | Read `min(size-off, 524288)` bytes. **Only if that blob has no `\n` at all** are more 524,288-byte chunks appended until a `\n` appears or EOF. Parse up to the last `\n`. Consequence: a short line followed by a 600 KB line advances past the short line only on refresh 1, and completes the long line (and any line after it) on refresh 2 | pinned: file 600,089 B; refresh 1 → offset 30, conv=1; refresh 2 → conv=600,002 | `:1041-1058` | — |
| BC-SL-033 (refined) + BC-SL-067 (new) | Lines come from `bytes.splitlines()`, which splits on **only** `\n`, `\r\n` and `\r` (not `\v`, `\f`, `\x1c-\x1e`, `\x85` or U+2028, which `str.splitlines` would split on). Empty segments fail `json.loads` and are skipped. `json.loads(bytes)` behavior: **UTF-8 BOM accepted** (utf-8-sig detection); invalid UTF-8 → UnicodeDecodeError → line skipped; `NaN`, `Infinity` and `1e400` (→ inf) accepted; duplicate keys last wins; a lone `\ud800` escape is kept; nesting ≥ ~1000 levels → RecursionError → caught → line skipped (Go's `encoding/json` limit is 10,000, so it would count the line) | pinned: `b'\xef\xbb\xbf{"message":{"content":"bom"}}'` counted (conv 3); `\xff` line skipped; `ab\rcde\r\n\n` → two lines (conv 5); depth 995 ok, depth 1000 RecursionError | `:1059-1063` | PT-SPLIT, PT-JSONIN |
| BC-SL-034 (refined) + BC-SL-065 (new) | Dedup. A usage dict with a truthy id already in `seen_ids` is ignored; otherwise the id is recorded and the usage counted. **The first transcript line of a message supplies its usage.** Later lines of the same id (even with larger `output_tokens`) are ignored. Id-less usage is always counted. Ids persist as the last 256 of `recent_ids`; within one refresh the list is unbounded. An id repeated after more than 256 other distinct ids is counted again | pinned: split message with usage repeated → counted once (tin 1010, tout 300); same id on the next refresh → ignored; two id-less usages → both counted | `:1033-1034,1096-1103,1153` | PT-ORDER |
| BC-SL-035/036 (confirmed, pinned) | Accumulation and rebuild rule | pinned with 5 calls: write 90,000 vs growth 500 → rebuild; write 20,000 vs growth 20,000 → excess 0; write 40,001 vs growth 40,001 → 0; prompt shrank (growth clamped to 0) with write 20,001 → rebuild. **rb=2**, tin 501,502, c_wr 270,002, c_rd 231,500. After `compact_boundary`, a 50,000 write is not a rebuild (`pp=None`) | `:1104-1119` | PT-BOOL (float usage accepted: `input_tokens:1.5` → tin 1.5) |
| BC-SL-037 (confirmed) | `compact_boundary` resets res/conv/think and `pp`; usage totals are kept | pinned scenario C: (0,7,0) after the boundary, tin keeps growing | `:1088-1095` | — |
| BC-SL-038 (refined) + BC-SL-071 (new) | Composition byte rules with **Python `json.dumps` defaults** (separators `", "`/`": "`, `ensure_ascii`, float repr, NaN/Infinity literals). Pinned lengths: `{}`/`[]`/`""`/None/0 used as tool_use input → `json.dumps(x or "")` = `""` → **2**; `{"command":"ls"}`→17; `{"a":"é"}`→15 (`\u00e9`); `"😀"`→14 (surrogate pair); `{"x":1.0}`→10; `{"x":1e+16}`→12; `{"x":1e-05}`→12; `{"x":12345678901234567890}`→27; `{"x":-0.0}`→11; `{"x":Infinity}`→15; `{"x":NaN}`→10; `{"t":"a\u2028b"}`→17; `{"t":"<&>"}`→12 (no HTML escaping); `{"t":"\u007f"}`→15 (DEL escaped); `{"type":"text","text":"hi"}`→30. A tool_result list `[image, {"type":"text","text":"hi"}, "raw"]` → 2000+30+5 = **2035**; a tool_result dict `{"k":"é"}` → 15; tool_result str → `len` in code points | pinned (`tx1.py`, `mixdrive2.py`) | `:1120-1149` | PT-JSONLEN, PT-CP |
| BC-SL-072 (new) | Value types inside blocks. `text`/`thinking` that is a list or dict counts its **item count** (`len`), e.g. `[1,2,3]` → 3. Falsy values (0, "", None, []) count 0. **A truthy number or `true` → TypeError → crash** (CP-T06). Message-level `content` that is a str → `len`; a dict → ignored | pinned | `:1121-1125,1143-1145` | PT-EXC, PT-BOOL |
| BC-SL-039 (refined) | The turn rate takes `out` from the **first** line of the message id (BC-SL-065). If the first line carries a streaming placeholder (`output_tokens:1`), the span test `span <= 4*out/15` fails and the turn is skipped; the previous `lr` stays | pinned: first line out=1, last line out=900, span 10 s → `lr=None` | `:1073-1079,988-996` | — |
| BC-SL-069 (new) | `_iso_ts` = `datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()`; ValueError → None; non-str → None. **Python 3.11 grammar** (3.10 rejects most of these): `…T20:18:04.123Z`, `… 20:18:04Z` (space), `20261113T201804Z` (basic), `2026-W46-5T20:18Z` (week date) and `2026-11-13` (date only, local midnight) are accepted. **Fractions beyond microseconds are truncated** (`.123456789Z` → `.123456`). Naive values are **local time** (TZ=UTC 1794601084.0 vs America/Chicago 1794622684.0). `ZZ` → None; `24:00:00` → None; naive `0001-01-01T00:00:00` → None (raises ValueError, caught); `9999-12-31T23:59:59` naive → 253402300799.0 (UTC) | pinned under TZ=UTC and America/Chicago | `:977-985` | PT-TIME |
| BC-SL-068 (new) | Every unguarded type confusion in the parser crashes **before** `save_cache`, so the offset never advances and the **same line re-raises on every refresh**. The status line stays degraded for the rest of the transcript's life (sticky). Because `_mix_counts` runs first in `main` (`:1213`), the crash also prevents the session-cache, git-cache, `proc_start` and cost-history writes of that refresh | pinned: non-object line → AttributeError on two consecutive runs | `:1059-1153,1213` | PT-EXC (see CP-T*) |

### A5. Row 2, metrics client and cache

| ID | Contract | Pinned / edges | Evidence | Pitfalls | D15 literals |
|---|---|---|---|---|---|
| BC-SL-040 (refined) | `fetch_sample` swallows every exception (`except Exception`), so **no network input can crash at fetch time**. But `float(s["value"][1])` accepts `"NaN"`, `"+Inf"`, `"-Inf"`, `"1e400"` and Unicode digits, and those values reach the renderers and the sparkline history | — | `:158-187` | PT-PARSE, PT-ORDER (first wins over the result array) | VM URL, `QUERY :102-123`, 1.5 s |
| BC-SL-074 (new) | KV: `n=min(math.ceil(kv/25),4)`. **`vllm:kv_cache_usage_perc = NaN` → `max(nan,0.0)` keeps NaN → `math.ceil(nan)` ValueError → crash** (CP-N01), on both the fresh and the stale path | 0.0→`KV▱▱▱▱ 0%`; 0.0001→1 cell, `0%`; 0.25→1 cell `25%`; 0.2500001→2 cells `25%`; 0.29→2 cells `29%` (28.999999999999996); 0.51→3; 0.75→3; 0.76→4; 1.2→4 `100%`; ±inf → 4 / 0 cells. host 0.005 → hidden (`> 0.5` is false); 0.00501 → ` ↺host 1%`; 0.05 → CYAN with ` ↺host 5%`; 0.0500001 → YELLOW `↺host 5%`; host NaN → hidden, CYAN | `:754-763` | PT-NANMM, PT-INT (ceil), PT-FMT | 25, 4, 5, 0.5 |
| BC-SL-073 (new) | Sparkline: `top = 1.0` for `k`, otherwise `max(max(vals), floor)`; `idx(v)=int(min(max(v,0.0)/top*7, 7)+0.5)`. **Any NaN among the plotted points (any trace), or +Inf for the `v`/`f` traces, → ValueError → crash** (CP-N02). +Inf is safe for `k` (fixed top); -Inf is safe (clamped to 0). The fade is computed per channel as `int(c*fade)` | n=12 trail colors: (38,93,104) (41,101,113) (44,108,121) (47,116,130) (51,124,138) (54,131,147) (57,139,155) (60,147,164) (63,154,172) (66,162,181) (70,170,190), head `\e[38;2;140;235;255m`. vals [100,100.3,101,99,200,0,0.5,50] → `▅▅▅▄█▁▁▃`; idle [0.2,0.6] (floor 1) → `▂▅`; preempt `p` → `\e[38;2;220;170;60m` trail / `\e[33m` head; < 2 points → `""`; legacy `[t,v]` list points accepted; `[[0]]` → IndexError (CP-C05). idx at top=7: 0.49→0, 0.5→1, 2.5→3 (half-up via +0.5) | `:644-690` | PT-NANMM, PT-INT, PT-FMT | 12 pts, floors 1.0/0.1, fade 0.55/0.45, RGBs |
| BC-SL-075 (new) | NaN and Inf rendering in the other row-2 fields (no crash): queue `rnan·qnan` in GREEN (`nan > 0` is false); `r=2.6,q=0.5` → YELLOW `r3·q0` (q > 0 although it displays 0); TTFT +inf → YELLOW `◔infs`; -1.0 → `◔-1.0s`; n NaN → not "max" (`nan < 20` is false); power NaN → `⚡nanW·nanW nan° nan¢/h`. **Color/number mismatch:** wall 1520.4 → RED `1520W` (`> 1520` is true, `.0f` rounds down) | queue / TTFT / power pinned; `207.1/346.25/36/0.12` → `⚡207W·346W 36° 4¢/h`; `1059/1400/66/0.24` → YELLOW `1400W`, `34¢/h` | `:732-741,792-820` | PT-FMT, PT-NANMM | 1520, 1280, 8 s, 20 |
| BC-SL-086 (new) | TTFT format boundaries: `.0f` when ≥ 10, otherwise `.1f` | 9.95→`◔9.9s` (binary below the tie), 9.96→`◔10.0s` (the `.1f` branch rounds up to "10.0"), 10→`◔10s`, 2.25→`2.2s`, 2.35→`2.4s`, 8.0 → GREY, 8.04 → YELLOW `8.0s` (color tests t > 8, not the rounded value), 0.059 with n=6 → `◔max 0.1s`, 116 with n=5 → `◔max 116s`, n=19.999 → max | `:792-799` | PT-FMT | 10, 8, 20 |
| BC-SL-085 (new) | `»mine`: needs list/tuple, non-empty, numeric `[0]`. `dim = len>1 and bool([1])`; 1-element lists render bright | [113.4,False]→`\e[90m»\e[0m\e[1m\e[97m113\e[0m\e[90mt/s\e[0m`; [81.5,True]→`\e[90m82\e[0m` (half-even); [82.5,1]→`82`; [5]→bright `5`; [] / "x" / [None,True] → hidden; [nan,False] → `nan` | `:776-781` | PT-FMT, PT-BOOL | 200 |
| BC-SL-043 (refined) | Stale suffix `f"(~{age:.0f}s old)"`, half-even | 15.5→`(~16s old)`, 16.5→`(~16s old)`, 299.9→`(~300s old)` | `:697-701` | PT-FMT | 15, 300 |
| BC-SL-087 (new) | Import-time env grammar. `TTL=float(...)` accepts `" 4 "`, `"4_0"`→40, `"nan"`, `"inf"`, `"1e1"`, `"٤"`; **`""`, `"four"`, `"0x4"` → crash outside the guard** (CP-X01). `ROWS=int(...)` accepts `" 2 "`, `"2_0"`, `"٢"`; **`""`, `"2.0"`, `"nan"`, `"1e1"` → crash** (CP-X02). Semantics: `TTL=nan` → `fetch_ts > now-nan` is false → fetch every refresh; `TTL=inf` → `fetch_ts > -inf` is true even with no cache (default 0) → **never fetches**, renders `◌ DGX ?` forever on an empty cache; `TTL=-inf` → always fetch | pinned | `:74-75,324` | PT-PARSE | `DGX_SL_TTL=4`, `DGX_SL_ROWS=2` |
| BC-SL-041 (confirmed) | KEEP_DEAD cached-path quirk as in the broad sweep. Also: a NaN in a stored `sample` (JSON `NaN`) is written by `json.dump` and read back by `json.load`, so **Go cache readers must accept the `NaN`/`Infinity` tokens** during cache-swap and shadow (R8) | — | `:203,324-359` | PT-JSONIN, PT-JSONLEN | TTL, 300, 32 pts, 90 s, 2 s |
| BC-SL-052 (refined) + BC-SL-078 (new) | Session cache path `os.path.join(CACHE_DIR, f"statusline-{sid}.json")` with a raw sid. **New:** a sid containing `/` (e.g. `../x`) points into a nonexistent subdirectory. `mkstemp` succeeds in CACHE_DIR but `os.replace` fails, the OSError is swallowed and the temp file is **leaked**. Nothing persists: the TTL is never honored (fetch every refresh), the `ps` walk runs every refresh, rate-limit smoothing is lost and the sparkline never accumulates. No crash | — | `:198-206,1215` | PT-PATH | — |

### A6. Cost history

| ID | Contract | Pinned / edges | Evidence | Pitfalls |
|---|---|---|---|---|
| BC-SL-028 (refined) | `record_cost` writes `round(usd, 4)` (CPython correctly-rounded decimal): 1.23455→1.2346, 2.00005→2.0, 0.00015→0.0001, 13.78125→13.7812, 1e-5→0.0; `round(inf,4)`→inf (no raise; plain `round(inf)` raises OverflowError). An unhashable sid (list/dict) → `s.get(sid)` TypeError → crash (CP-S15) | pinned | `:224-237` | PT-ROUND (n-digit form) |
| BC-SL-079 (new) | A numeric sid (e.g. 123) is stored under int key 123 but JSON round-trips it to `"123"`. On the next refresh `s.get(123)` misses, so the per-minute throttle never applies (a write every refresh), and `cost_thresholds` (`k == sid`) does **not** exclude the session's own entry. Output quirk, no crash | pinned JSON round-trip `{123:1}` → `{'123': 1}` | `:230,246` | PT-ORDER/PT-STR |
| BC-SL-029 (refined) | Percentile index `int(0.75*(n-1))`, `int(0.95*(n-1))`. Pinned: the float index equals the exact integer `floor(75(n-1)/100)`, `floor(95(n-1)/100)` for every n in 10..400, so a Go integer formula is safe in that range. n=10 → (6,8); 11 → (7,9); 20 → (14,18); 21 → (15,19); 41 → (30,38); 81 → (60,76). `sorted()` over values that may include `Infinity` (inf usd) | pinned | `:257-261` | PT-INT |

### A7. Window age (⌂) process probe

| ID | Contract | Pinned / edges | Evidence | Pitfalls |
|---|---|---|---|---|
| BC-SL-023 (refined) + BC-SL-080 (new) | `out.strip().split(None, 2)`: ppid, comm, rest. A match needs `basename(comm) == "claude"` and a non-empty rest; then `time.mktime(time.strptime(rest[0].strip(), "%a %b %d %H:%M:%S %Y"))`. A space in the format matches 1+ whitespace, so the space-padded day `Nov  6` parses. Python's LC_TIME stays "C" (Python never calls `setlocale(LC_TIME)`), so **localized `ps` output** (`Do Nov 13 …`) raises ValueError → caught → None, which is **not cached**, so the walk re-runs on every refresh. **comm containing spaces** (e.g. `…/Application Support/claude`) shifts the tokens; no match, walk continues. A process with no lstart gives empty `rest`; no match. **DST-ambiguous local times** depend on `mktime` (macOS libc gave 1793514600.0 for `Sun Nov  1 01:30:00 2026` America/Chicago). A failure anywhere → None; there are no crash paths (`except Exception :293`). The non-dict cache check at `:273-275` sits **outside** that try, but `effective_rl` crashes first (CP-C01) | pinned: `812 claude Thu Nov 13 18:10:09 2026` → 1794615009.0 (Chicago); `/Users/x/.local/bin/claude Thu Nov  6 …` → 1794010209.0 | `:265-295` | PT-TIME, PT-SPLIT (Python whitespace) |
| Platform reach (legacy) | macOS: works (owner-verified). Linux procps supports `-o lstart`; it works only if the ancestor's comm is `claude` (an npm `#!/usr/bin/env node` install shows `node`, so no ⌂; LOW, install-dependent). **Windows: no `ps`, FileNotFoundError is caught, so ⌂ is never shown** | — | `:277-294` | — |
| **Approved additive deviation (owner)** | The Go port **may show ⌂ on Windows** (and wherever a native probe finds `claude`/`claude.exe`). Legacy cannot. Parity cases on Windows must pre-seed `proc_start` (both sides then render identically) or be marked additive. The Go native probe must **truncate the start time to whole seconds** (ps lstart resolution), so `int(win_ms//60000)` flips on the same refresh as legacy | — | PLAN D5; research Q4a | — |

### A8. `main()` orchestration and side-effect order (BC-SL-077, new)

Execution order, with the writes each step makes **before** any later crash:

1. stdin parse (`:1201-1206`).
2. `_mix_counts` (`:1213`) writes the mix cache at its very end (`:1150`).
3. `effective_rl` (`:1216`) writes the session cache when stdin carries a non-empty dict.
4. When ROWS ≥ 2: `get_sample` (`:1218`) writes the session cache (fetch result or `up:False`).
5. Row 2 render (`:1226-1227`), only under the width rule. It can crash (CP-N01/N02).
6. `claude_window_start` (`:1229`) may write `proc_start`.
7. `render_lane` (`:1230`): git cache write (`:411`), then widgets in order (thermometer → composition → ♻ → limits → lines → timer/⌂ → tokens → cost: `record_cost` write `:606`, then `cost_thresholds`).
8. trim, then print.

A multi-step parity harness must compare cache files after every step, not only stdout. A crash at step k leaves the
writes of steps 1…k−1 in place. Example: a row-2 crash (CP-N01) happens *before* `proc_start` and the cost record
are written. A thermometer crash (CP-S06) happens *after* the git cache write and *before* the cost record.

### A9. stdin and stdout encoding (BC-SL-076, new; BC-SL-002 refined)

- stdin is parsed with `json.load(sys.stdin)` (text). Pinned per mode:

  | stdin content | `LC_ALL=en_US.UTF-8` (strict) | `LC_ALL=C` or `PYTHONUTF8=1` (surrogateescape) |
  |---|---|---|
  | invalid UTF-8 byte inside a string (`A\xffB`) | UnicodeDecodeError, caught → `{}`, renders the `?` defaults | decoded to `A\udcffB` (3 code points), **printed back as the raw byte 0xFF** |
  | UTF-8 BOM before `{` | JSONDecodeError → `{}` | same |
  | JSON escape `\ud800` (lone high surrogate) in a rendered string | **print raises UnicodeEncodeError → degraded** (CP-S17) | same (surrogateescape covers only U+DC80–DCFF) |
  | JSON escape `\udcff` in a rendered string | crash → degraded | printed as raw byte 0xFF |
  | nesting ≥ ~1000 | RecursionError (an Exception), caught → `{}` | same |
  | top-level non-object | `{}` | same |

- **Harness consequence:** pin the locale mode that production uses (the status line inherits Claude Code's env;
  PYTHONUTF8 is not set by the launcher). The default proposal is strict UTF-8 locale without UTF-8 mode, and Go
  treats invalid-UTF-8 stdin as a parse failure. This conflicts with research Q3a (CONTRA-3), so it needs owner
  confirmation.
- stdout: `print("\n".join(rows))` adds a trailing `\n`. On Windows text mode Python writes `\r\n` (research P25).
  The degraded line is pure ASCII plus ESC and can never fail to encode.

---

## B. Crash-path catalogue (owner decision: Go reproduces the degraded output byte for byte)

**Degraded output (guarded paths):** stdout is exactly these 29 bytes:
`1B 5B 39 30 6D` `statusline degraded` `1B 5B 30 6D` `0A`, i.e. `\e[90mstatusline degraded\e[0m\n`.
Exit code 0 and stderr empty (pinned with a guard replica). Nothing else is printed, because the only other
`print` is the last statement and a failing `print` encodes the whole string before writing anything. Side effects
from earlier steps persist (A8). Guard: `:1238-1245` (`except Exception`, so RecursionError and MemoryError are
caught; KeyboardInterrupt and SystemExit are not).

"Sticky" means the crash repeats on later refreshes without new input.

### B1. stdin-sourced (guarded → degraded, exit 0)

| CP | Condition | Raise site | Exception | Sticky |
|---|---|---|---|---|
| CP-S01 | `model` truthy and not a dict (non-empty str/list, nonzero number, `true`) | `:442` | AttributeError | no |
| CP-S02 | `model.id` truthy and not a str **and** `LOCAL_MODEL_PREFIXES` non-empty | `:446` | AttributeError | no |
| CP-S03 | `workspace` truthy and not a dict | `:452` | AttributeError | no |
| CP-S04 | first truthy of `project_dir`/`current_dir`/`cwd` is not a str | `:405` (GIT on) / `:460` (`DGX_SL_GIT=0`) | AttributeError / TypeError | no |
| CP-S05 | `context_window` truthy and not a dict | `:419` | AttributeError | no |
| CP-S06 | `context_window.used_percentage` = NaN | `:426` | ValueError | no |
| CP-S07 | numeric `used_percentage` and `context_window_size` truthy non-numeric (str/list/dict) | `:435` | TypeError | no |
| CP-S08 | `prompt_cache` truthy and not a dict | `:477` | AttributeError | no |
| CP-S09 | `rate_limits.five_hour` or `.seven_day` truthy and not a dict (str, non-empty list, nonzero number, `true`), when not rerouting all | `:503` | AttributeError | **yes, ≤ 1800 s**: the bad dict is cached by `effective_rl` (`:307`) and re-served while stdin omits `rate_limits` |
| CP-S10 | `cost` truthy and not a dict | `:535` | AttributeError | no |
| CP-S11 | `total_lines_added` or `total_lines_removed` = ±Infinity (JSON `Infinity`/`-Infinity`, or an overflowing literal such as `1e400`) | `:853` | OverflowError (not caught by `_fmt_lines`) | no |
| CP-S12 | `total_duration_ms` = +Infinity | `:546` (`inf//60000`=nan) | ValueError | no |
| CP-S13 | `total_api_duration_ms` = +Infinity and `total_duration_ms > 60000` | `:546` via `:553` | ValueError | no |
| CP-S14 | `session_id` truthy and not a str, **and** `transcript_path` is an existing file | `:1017` | TypeError | no |
| CP-S15 | `session_id` unhashable (non-empty list/dict), `total_cost_usd > 0` and the lane is known (prefixes set, id set). Only reachable when CP-S14 is not (no transcript) | `:230` | TypeError | no |
| CP-S16 | `transcript_path` is a list, dict or float | `:1010` | TypeError | no |
| CP-S17 | A **str** that reaches the output contains a lone surrogate (`\ud800`–`\udbff`, `\udc00`–`\udc7f`, in any mode; `\udc80`–`\udcff` only in strict mode): model display name or id, project label | `:1234` | UnicodeEncodeError | no |

### B2. transcript-sourced (guarded → degraded, exit 0, **all sticky**: the offset never advances, BC-SL-068)

| CP | Condition (on an unparsed complete line) | Raise site | Exception |
|---|---|---|---|
| CP-T01 | line is valid JSON but not an object (`[…]`, number, string, `true`, `null`) | `:1069` | AttributeError |
| CP-T02 | `message` truthy and not a dict | `:1072` (when the timestamp parses) / `:1097` | AttributeError |
| CP-T03 | timestamp parses, `type=="assistant"`, `message.id` truthy, `message.usage` truthy and not a dict | `:1079` | AttributeError |
| CP-T04 | a counted usage (first-seen id, or no id) whose `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` or `output_tokens` is truthy and not a number (str, list, dict); `true` is fine | `:1108` / `:1112` | TypeError |
| CP-T05 | `output_tokens` truthy non-numeric on the first line of a **new turn whose id was already counted** (so CP-T04 does not fire), then that turn is finished by a newer id, a system line or a user prompt | `:994` | TypeError |
| CP-T06 | content block `text` or `thinking` is a nonzero number or `true` | `:1143` / `:1145` | TypeError |
| CP-T07 | `message.id` unhashable (list/dict) with a dict `usage` | `:1099` | TypeError |

### B3. network-sourced, VictoriaMetrics (guarded → degraded, exit 0)

| CP | Condition | Raise site | Exception | Sticky |
|---|---|---|---|---|
| CP-N01 | `vllm:kv_cache_usage_perc` value `"NaN"` and row 2 rendered (fresh or stale) | `:759` | ValueError | per fetch. During a VM outage the bad stale sample is re-served for ≤ 300 s (KEEP_DEAD); within TTL the cached sample is reused |
| CP-N02 | Fresh path, sparkline on, and among the last 12 history points that carry the trace key at least one is NaN (any trace) or +Inf (`v`, `f` traces). Realistic case: `DGX_SL_TRACE=ttft` on a quiet box, since `dgx_ttft:p95_30m` NaN is guarded for display (`:793`) but stored in `hist["f"]` (`:339-343`) | `:675` | ValueError | **yes**, until the bad point leaves the last-12 window (≥ 12 newer points ≥ 2 s apart, ≈ 24–48 s) or ages past 90 s |

Not crash paths (checked): NaN or Inf in queue, TTFT, power, idle, health, `dgx_mtok` and `dgx_rate`; any fetch
error, which is swallowed (`:186`).

### B4. foreign-cache class (guarded → degraded, exit 0; reachable only from a cache file not written by legacy, e.g. hand edits, the Go port during shadow, cache-swap tests)

All are sticky until the file is fixed or overwritten.

| CP | File / key | Condition | Raise site |
|---|---|---|---|
| CP-C01 | `statusline-<sid>.json` top level | not an object | `:307` (TypeError, stdin carries rate_limits) or `:311` (AttributeError) |
| CP-C02 | same, `rl_ts` | non-numeric while `rl` is a dict and stdin lacks rate_limits | `:312` |
| CP-C03 | same, `fetch_ts` | non-numeric or `null` (ROWS ≥ 2) | `:324` |
| CP-C04 | same, `ts` | non-numeric within TTL | `:325` |
| CP-C05 | same, `hist` | an element that is a list with < 2 items (`:655`); a dict with non-numeric `t` (`:336`); `hist` itself a number (`:335`). The sparkline also crashes on a dict-valued `hist` (`:664`) | IndexError / TypeError |
| CP-C06 | same, `sample` | truthy non-dict (`:716`), or a value of wrong type that reaches a format (e.g. `vllm:num_requests_running: "3"` → `:741` "Unknown format code 'f'") | AttributeError / ValueError |
| CP-C07 | `statusline-mix-*.json` | top level not an object (`:1019`); `size` non-numeric (`:1035`); `ids` non-iterable or holding unhashables (`:1033-1034`); accumulators non-numeric (first `+=`); `cur` truthy non-dict (`:1074`/`:991`); `pp` non-numeric (`:1117`); `lu` non-numeric (`:993` at finish) | various |
| CP-C08 | `statusline-git-*.json` | top level not an object, or `ts` non-numeric | `:409` |
| CP-C09 | `cost-history.json` top level | not an object | `:229` (`setdefault`) / `:245` |
| CP-C10 | `cost-history.json` `sessions` / entries | `sessions` truthy non-dict (`:230`/`:245`); entry non-dict (`:232`/`:246`); entry `ts` `null` or non-numeric (`:232`/`:246`) | AttributeError / TypeError |

### B5. Outside the guard

| CP | Condition | Site | Result | Parity-relevant |
|---|---|---|---|---|
| CP-X01 | `DGX_SL_TTL` not `float()`-parseable, **including the empty string** (`DGX_SL_TTL=`) | `:74` (import) | stdout **empty** (0 bytes), traceback on stderr ending `ValueError: could not convert string to float: ''`, **exit 1**. Claude Code shows a blank status line | **yes** (pinned) |
| CP-X02 | `DGX_SL_ROWS` not `int()`-parseable (`""`, `"2.0"`, `"nan"`, `"1e1"`, …) | `:75` (import) | same, `ValueError: invalid literal for int() with base 10: '2.0'`, exit 1 | **yes** (pinned) |
| CP-X03 | the guard's own `print` fails (stdout closed, EPIPE after Claude Code cancelled the run) | `:1244` | exception during handling, exit 1, no stdout | no (the consumer is gone) |
| CP-X04 | BaseException: SIGINT → KeyboardInterrupt (traceback, exit 1); SIGTERM from a cancelled run → killed by the signal (no handler) | anywhere | no stdout | no |

**Counts:** 40 catalogued paths. 36 are guarded (17 stdin, 7 transcript, 2 network, 10 foreign-cache) and 4 sit
outside the guard (2 parity-relevant). The Go port needs one top-level `recover`/`errDegraded` handler emitting the
29 bytes, and **must not** wrap the import-time env parse in it. CP-X01/X02 produce empty stdout with exit 1.

---

## C. Python-semantics pitfall tags per status line BC

Tags: PT-ROUND banker's/n-digit `round` · PT-FMT `%.Nf` half-even on binary values plus `nan`/`inf` spelling ·
PT-FDIV float `//` and `%` · PT-NANMM `max`/`min` keep the first argument with NaN · PT-INT `int()`/`ceil` truncate
and raise on NaN/inf · PT-BOOL bool is int, plus truthiness · PT-JSONLEN `json.dumps` lengths and escaping ·
PT-JSONIN `json.loads` leniency (NaN/Infinity/BOM/invalid UTF-8/depth/duplicate keys) · PT-CP code-point
`len`/slice · PT-SPLIT `splitlines`/`strip`/`split(None)` whitespace sets · PT-RE regex semantics · PT-TIME local
time and `fromisoformat` · PT-FMA fused multiply-add · PT-STR `str()`/repr of non-str · PT-PATH posixpath/ntpath ·
PT-ENC stdio encoding and surrogates · PT-PARSE `int()`/`float()` grammar · PT-ORDER insertion order, first wins,
key type round-trips · PT-EXC exception-driven output.

| BC | Tags |
|---|---|
| 001 | PT-EXC (catalogue B) |
| 002, 076 | PT-JSONIN, PT-ENC |
| 003 | PT-ENC (`\r\n` on Windows text stdout) |
| 004, 054 | PT-CP, PT-RE (RE2-compatible) |
| 005, 055, 087 | PT-PARSE |
| 006 | PT-SPLIT (Unicode strip), PT-BOOL |
| 007, 058 | PT-STR, PT-ENC |
| 008, 059 | PT-PATH |
| 009, 010 | PT-ENC (HEAD text decode), PT-PATH |
| 011, 056, 057 | PT-INT, PT-FMT, PT-NANMM, PT-BOOL, PT-FMA |
| 012 | PT-ROUND, PT-FMT |
| 013, 060 | PT-NANMM, PT-FMT, PT-BOOL |
| 014 | PT-SPLIT (`rstrip("*")`) |
| 015, 016, 017, 061 | PT-FDIV, PT-FMT, PT-NANMM, PT-EXC (CP-S09) |
| 018 | PT-BOOL (`{}` counts as absent) |
| 019, 063 | PT-INT, PT-PARSE, PT-EXC (CP-S11) |
| 020, 021, 064 | PT-FDIV, PT-INT, PT-EXC (CP-S12/S13) |
| 022, 081 | PT-FDIV, PT-FMA, PT-TIME |
| 023, 080 | PT-TIME, PT-SPLIT |
| 024, 062 | PT-FMT, PT-BOOL, PT-PARSE |
| 025, 026, 082 | PT-FMT, PT-BOOL |
| 027, 083 | PT-FMT, PT-NANMM |
| 028, 079 | PT-ROUND (n-digit), PT-JSONLEN (cache floats), PT-ORDER (int key → str) |
| 029 | PT-INT, PT-ORDER (stable sort) |
| 030, 088 | PT-EXC |
| 031 | — |
| 032, 066 | — (byte offsets; Go must count bytes, not runes) |
| 033, 067 | PT-SPLIT (bytes), PT-JSONIN |
| 034, 065 | PT-ORDER |
| 035, 036 | PT-BOOL |
| 037 | — |
| 038, 071, 072 | PT-JSONLEN, PT-CP, PT-EXC |
| 039 | PT-TIME |
| 069 | PT-TIME |
| 040 | PT-PARSE, PT-ORDER |
| 041 | PT-JSONIN, PT-JSONLEN |
| 042 | — |
| 043 | PT-FMT |
| 044 | — |
| 045 | PT-FMT, PT-NANMM |
| 046, 074 | PT-NANMM, PT-INT, PT-FMT |
| 047, 085 | PT-FMT, PT-BOOL |
| 048, 073 | PT-NANMM, PT-INT, PT-FMT |
| 049, 086 | PT-FMT |
| 050, 075 | PT-FMT, PT-NANMM |
| 051, 084 | PT-FDIV, PT-NANMM, PT-BOOL |
| 052, 078 | PT-PATH |
| 053 | — |
| 068 | PT-EXC |
| 070 | PT-CP, PT-RE |
| 077 | — (ordering) |

---

## D. D15 literal dependencies (config-over-code; defaults must equal these during parity)

| BC(s) | Literals (name = value @ line) |
|---|---|
| 003, 055 | `NARROW_COLS=72 :100`; `DGX_SL_ROWS=2 :75` |
| 006, 014 | `LOCAL_MODEL_PREFIXES` default `"" :444` (proxy default `claude-sonnet`, `dgx_proxy.py:86`); reroute set `{"claude","claude-"} :487` |
| 010 | `GIT_TTL=5.0 :99`; `DGX_SL_GIT :77` |
| 011, 056, 057 | 85 / 50 `:434`; 10 cells; HSV 0.22 / 0.85 / 0.80 `:146-147`; 1e6 / 1000 `:435-436` |
| 016, 017, 061 | 0.10, 80, 100, 70, 90, 1.15, lengths 5×3600 / 7×86400 `:501-523` |
| 018 | `RL_KEEP=1800.0 :85` |
| 019, 063 | 1,000,000 / 10,000 `:856-858` |
| 020–022, 081 | 60000 `:540,551`; 300000 `:559`; 1440 `:561` |
| 024, 062 | 1e6 / 1000 `:869-871` |
| 025, 026, 028, 029, 082 | `COST_WINDOW_S=30*86400`, `COST_MIN_USD=1.0`, `COST_MIN_N=10`, `COST_FALLBACK_YELLOW=25.0 :217-221`; throttle 60 `:232`; rate gates 300000 / 1800000 `:253`; p75/p95 `:261`; `round(…,4) :234`; $/h gate 300000 `:622` |
| 027, 083 | `MIN_BASIS_MTOK_MONTH=30.4 :98`; 0.005 `:634` |
| 032, 066 | `_READ_CAP=524288 :952` |
| 034, 065 | 256 ids `:1153` |
| 036 | `REBUILD_EXCESS=20000 :972` |
| 038, 071 | 2000 per image `:1137,1149` |
| 039 | `TURN_DIM_OUT=200`, `TURN_FLOOR_TPS=15.0`, `TURN_STALE=4.0 :967-974` |
| 040, 041, 042 | `VM_URL :73`, `QUERY :102-123`, `HTTP_TIMEOUT=1.5 :81`, `TTL=4 :74`, `KEEP_DEAD=300 :80`, `SPARK_MAX_AGE=90 :83`, `HIST_MIN_GAP=2 :84`, 32 pts `:350` |
| 043 | `STALE_OK=15.0 :79` |
| 046, 074 | 25 / 4 cells, 5 % host, 0.5 % display `:759-763` |
| 048, 073 | `SPARK_PTS=12 :82`; `TRACE` default `rate :89`; floors `{v:1.0, f:0.1} :649`; fixed `{k:1.0} :648`; fade 0.55 / 0.45; RGB (70,170,190) / (220,170,60) / (140,235,255) `:680-689` |
| 049, 086 | `TTFT_MIN_N=20 :124`; 10 s / 8 s `:795-799` |
| 050, 075 | 1520 / 1280 `:812` |
| 051, 084 | `IDLE_AFTER=300.0 :93` |
| 023, 080 | 6 ancestors `:279`; `ps` timeout 1 s `:281` |
| all | colors/SGRs `:127-134`; `SEP :128`; glyphs. These are format constants (D15 exception): named constants with a "why not config" comment |

D13/D14 (intercept all hosts; no proxy env in children) are P3/P4 deviations and change nothing here. Note for P1:
the status line bypasses `HTTP(S)_PROXY` itself (`:168`), so D14 makes that bypass redundant but harmless. Keep it
for parity.

---

## E. Proxy: I1, I2 and the consequence of BC-PX-017

### I1 resolved: `Accept-Encoding: identity` on passthrough

| ID | Contract | Evidence | Conf |
|---|---|---|---|
| BC-PX-005 (refined) + BC-PX-032 (new) | `Accept-Encoding` is set to `identity` at `:131` **only** when all of these hold: host `api.anthropic.com`; path starts with `/v1/messages` (`:103`); `get_text()` decodes and parses as JSON (`:105-109`); the JSON is a dict (`:110-111`). It is set **before** the lane decision, so the Anthropic lane (`anthropic`), the server-tool lane (`anthropic-server-tools`) and the DGX lane all get it. The DGX lane sets it again at `:166` (redundant). **Untouched:** unparseable or non-dict bodies, all other paths and hosts, and the bridge websocket. The request body is never changed on passthrough; only this header is. So the module docstring's "untouched" (`:10`) is wrong for this one header, and the in-code comment (`:129-130`) states the intent (plain-text SSE for the tap). Effect: Anthropic replies on these flows arrive uncompressed. The P3 replay must expect the rewritten header on Anthropic-lane `/v1/messages` requests. How mitmproxy `Headers.__setitem__` treats multiple pre-existing `Accept-Encoding` fields is LOW (runtime) | `dgx_proxy.py:10,103-111,129-131,166` | HIGH (code) / LOW (mitmproxy header-collapsing detail) |
| BC-PX-035 (new) | Path matching is a **method-agnostic prefix** (`startswith("/v1/messages")`). So `POST /v1/messages/batches` (body `{"requests":[…]}`, no top-level `model`) parses → `model=""` → Anthropic lane: `anth_request` with `model_req:""`, `path:"/v1/messages/batches"`, plus the Accept-Encoding rewrite. `GET /v1/messages/batches/{id}` has an empty body → `json.loads("")` ValueError → decision note `unparseable /v1/messages body…` → passthrough with the header untouched. D13 narrows the Go rewrite scope to `POST /v1/messages`. That is a P3 deviation, noted here and not re-specified | `:103-111,112,126,132-136` | MEDIUM |

### I2 resolved: SSE tap usage source

| ID | Contract | Evidence | Conf |
|---|---|---|---|
| BC-PX-017 (refined) + BC-PX-033 (new) | `_scan` runs `re.finditer(rb"data: ({.*})", block)` (unanchored; `.` excludes `\n`; greedy to the last `}` on the line; RE2-compatible). For each match that parses as a JSON dict: (1) **`self.usage` is replaced by `(int(in or 0), int(out or 0))` iff the top-level `usage` is a dict containing the key `input_tokens`** (the value may be null, giving 0). (2) Cache maxima are absorbed from the top-level `usage` **and** from `message.usage`. (3) `delta.stop_reason`, when truthy, replaces `stop_reason`. **Not done:** `message_start` (usage under `message`) never sets `usage`; an output-only `message_delta` (`usage:{output_tokens}`) is **ignored**, so `out_tok` = `output_tokens` of the **last event that also carried `input_tokens`**, even when a later output-only delta reports more. No field-wise merge happens (**CONTRA-2**). The docstring (`:363-366`, "extracts usage{} from message_start / message_delta") is therefore wrong for `message_start`; that part of I2 is resolved against the code. Exceptions: a non-dict truthy `delta` (string/list) → AttributeError, and `delta: null` → `None.get` AttributeError. Either aborts the rest of that block (`:404-407`), keeping the effects of earlier matches in the block. A trailing partial line at end of stream is never scanned. The 64,000-byte tail cap (`:408-409`) drops a runaway line's head, so its `data: ` prefix is lost and it never matches | `:362-427` | HIGH (code) |
| External dependency (unchanged LOW) | Whether real upstreams send a top-level `usage.input_tokens`: Anthropic's documented `message_delta` "may carry only output_tokens, or also input_tokens" (domain research line 148). The in-code comment (`:373-376`, "seen live 2026-11-12") confirms that `message_delta` carries cache counters but says nothing about `input_tokens`. vLLM's dialect is cited from its serving code (`:262-263`), not from the repo | — | LOW |

### BC-PX-017 consequence made explicit (BC-PX-034, new): when `*_usage` events are written

`anth_usage` is written (`:246-253`) iff the response is for host `api.anthropic.com` with path prefix `/v1/messages`
and `in_tok is not None`. `in_tok` comes from:

| # | Source | Precondition | `in_tok` value |
|---|---|---|---|
| a | SSE tap (`:221-224`) | a tap exists (response content type contains `text/event-stream`, `:196-198`) **and** `tap.usage` is truthy. A tuple is truthy even when it is `(0,0)`, so any qualifying event counts | the **last** qualifying event's `input_tokens` (int) |
| b | JSON body (`:225-235`) | (a) did not apply **and** status < 400 **and** the body parses as a JSON dict with a dict `usage`. In the tapped-but-no-qualifying-event case, the body of a streamed flow is unreadable (`json.loads` on an empty or None body raises ValueError/TypeError, caught) | `usage.get("input_tokens")`, which may be `None` (no event) or `0` (event written with 0) |

- Consequences: (1) **A streamed Anthropic reply whose events never carry a top-level `usage.input_tokens` writes
  `anth_reply` without token fields and no `anth_usage`.** Its tokens are invisible to the exporter. (2)
  `/v1/messages/count_tokens` (JSON `{"input_tokens":N}`, no `usage`) never writes `anth_usage` (BC-PX-036, new;
  `:124` comment "free, no usage{}"). (3) An SSE response with status ≥ 400 still takes path (a) if the tap saw
  usage. (4) A non-numeric `input_tokens` in a JSON body (e.g. `"abc"`) makes `int()` at `:243` raise **inside the
  hook**. `ev.update` runs before `ledger("anth_reply")`, so **neither event** is written (mitmproxy logs the addon
  error; LOW).
- `dgx_usage` is written (`:275-282`) iff the flow's host equals the DGX host, the path has the `/v1/messages` prefix,
  and `tap is not None and tap.usage` (**source (a) only, no body fallback**). Then `in_tok = usage[0] +
  cache_read_tok + cache_write_tok` (whole prompt). Non-streaming DGX JSON replies never write `dgx_usage`
  (BC-PX-020 quirk confirmed). `dgx_reply` is always written, and carries `in_tok`/`out_tok` only under the same
  condition.
- Exporter impact (P2 parity): `dgx_llm_anthropic_tokens_*` and the DGX token counters count only flows meeting
  these conditions. Any replay corpus must include an SSE stream with **no** top-level `input_tokens` (expected: no
  `*_usage` line) and one with two `message_delta`s (expected: `out_tok` from the last delta that carries
  `input_tokens`).

---

## F. Stop hook (`auto_continue.py`): regex fallback and English policing

### F1. RE2 compile status of every legacy pattern (go1.26.5, pinned)

| Pattern | Site | Go `regexp` | Notes |
|---|---|---|---|
| `ANNOUNCE` `^(now\|next\|…\|continuing)\b` + IGNORECASE | `auto_continue.py:24-28` | compiles as `(?i)^(…)\b` | `\b` is **ASCII** in RE2, Unicode in Python (divergences below) |
| `(?<=[.!])\s+` (sentence split) | `:177` | **COMPILE ERROR** (`invalid named capture`) | needs a hand-written splitter (BC-HK-015) |
| `\b(now\|next\|first)\b` + IGNORECASE | `:179` | compiles | ASCII `\b` |
| `\b(done\|complete\|finished\|ready for you)\b` + IGNORECASE | `:180` | compiles | ASCII `\b` |
| CJK class `[぀-ヿ㐀-䶿一-鿿가-힯豈-﫿]` | `:184` | compiles | identical semantics (code-point ranges) |
| `:\s*$` | `:236` | compiles | `\s` is ASCII `[\t\n\f\r ]` in RE2 (not `\v`). Moot, see BC-HK-017 |
| statusline `\033\[[0-9;]*m`, `[^A-Za-z0-9_-]` | `dgx_statusline.py:137,1017` | compile | the second must be applied per rune (BC-SL-070) |
| proxy `data: ({.*})` (bytes) | `dgx_proxy.py:413` | compiles as `data: (\{.*\})` | same semantics on bytes |
| exporter `p_done=([0-9.]+)` | exporter | compiles | — |

**Exactly one pattern cannot compile in RE2: the lookbehind split at `auto_continue.py:177`.**

### F2. Function-level BCs

| ID | Contract | Pinned examples | Evidence | Pitfalls |
|---|---|---|---|---|
| BC-HK-014 (new) | `ANNOUNCE.match(last)`: anchored at the start; alternatives tried in order; `\b` = Python Unicode word boundary; IGNORECASE uses Unicode simple folding (`ſ`→`s`). **Python vs Go divergences (pinned on both sides):** `nowé we go` Py False / Go True; `runningé` Py False / Go True. Agree: `Now we run` T, `ſtarting the build` T (both fold ſ), `next_step` F, `now—then` T, `first2` F, `I'll do it` T, `LET ME check` T. Curly `I’ll` (U+2019) matches no alternative on either side | — | `:24-28` | PT-RE |
| BC-HK-015 (new) | Sentence split: `re.split(r"(?<=[.!])\s+", line)` splits at every maximal run of **Python Unicode whitespace** (`str.isspace`: includes NBSP U+00A0, U+2003, `\x1c-\x1f`, `\x85`) that **immediately follows** `.` or `!`. `last` = the final piece. Go spec: scan the runes; where rune i is `.` or `!` and rune i+1 starts a whitespace run, cut and drop the run | `"a.  b! c d.\u00a0e"` → `['a.','b!','c d.','e']`; `"Fixed.\u00a0Now running tests"` → `['Fixed.','Now running tests']` | `:177` | PT-RE, PT-SPLIT |
| BC-HK-016 (new) | `should_continue(msg)`: `text=msg.strip()` (Python whitespace); empty → False; ends with `?` → False; ends with `:`, `…` or `...` → True; `last = split(text.splitlines()[-1].strip())[-1]` using **`str.splitlines`** (boundaries `\n \r \r\n \v \f \x1c \x1d \x1e \x85 \u2028 \u2029`). Return `(A and not last.endswith((".","!"))) or C`, where A = ANNOUNCE matches and C = A and `\b(now\|next\|first)\b` and `len(last) < 200` (code points) and not `\b(done\|complete\|finished\|ready for you)\b` (both IGNORECASE) | `""`→F; `Shall I proceed?`→F; `Here is the plan:`→T; `Working on it…`→T; `Done...`→T; `Tests pass. Now I'll run the linter`→T; same with `.`→T (C); `All good! Next we deploy.`→T; `Next: done with step one.`→F (done); `Running the suite now.`→T; `Let me check the ledger format`→T; `I will finish it.\nNow writing the file`→T; `The build is complete. Now ready for you to review.`→F; `First, the setup. Then we test.`→F; `nowhere to go`→F; `Proceeding with step 2 of 3.`→F; `Fixed.\u00a0Now running tests`→T; `Now `+200×`x`+`.`→F (len ≥ 200, ends `.`); `Line one.\u2028Now writing`→T (U+2028 is a line boundary); `a.  b. Now c.`→T | `:169-181` | PT-RE, PT-SPLIT, PT-CP |
| BC-HK-017 (new; refines BC-HK-007) | Colon fake: `re.search(r":\s*$", msg.strip())` on an already-stripped string is **exactly equivalent to `stripped.endswith(":")`** (strip removed every Python-whitespace char, so `\s*` matches empty and `$` is the end). Go must implement it as Python-strip plus `HasSuffix(":")`. A literal RE2 port on unstripped text would differ (`abc:\u00a0`, `abc:\v`, `abc: \u2003` are True in Python and False in RE2; pinned). The length gate `len(msg.strip()) > 20` counts code points. Order: after the `?` check, before Kev | — | `:236-242` | PT-RE, PT-SPLIT, PT-CP |
| BC-HK-018 (new; refines BC-HK-003) | `non_english(msg)`: `n` = number of code points in U+3040–30FF, U+3400–4DBF, U+4E00–9FFF, U+AC00–D7AF, U+F900–FAFF. True iff `n >= 12` or (`n >= 4` and `n/max(1,len(msg)) > 0.02`), with `len` over the **raw** (unstripped) message in code points. Not counted: halfwidth katakana (U+FF61–FF9F), fullwidth Latin, Hangul Jamo (U+1100–11FF), CJK punctuation (U+3000–303F), Extension B+ (astral). Runs before `stop_hook_active` (unless `DGX_ENGLISH=0`) | `你好`→F (n=2); 16 hanzi → T; `abc 中文字 `+200 x → F (n=3); n=4, len 109 → T (0.0367); n=4, len 309 → F (0.0129); `ｶﾀｶﾅ`→F (n=0); `カタカナです`→T; `한국어문장입니다`→T | `:184-190,217-224` | PT-CP |
| BC-HK-020 (new; refines BC-HK-008) | `kev_state` block rendering: a text block gives `b.get("text","")`; any other dict block gives `f"[{type}: {name or ''}]".strip("]")`, which strips **all** leading and trailing `]`. Pinned: `{"type":"tool_use","name":"Bash"}` → `[tool_use: Bash`; `{"type":"tool_result"}` → `[tool_result: ` (**kept**: the `endswith(": ]")` filter can never match after strip); a text block with no `text` → `""` (dropped); `{"type":"image","name":"]x]"}` → `[image: ]x`. Lines are `f"{role}: {content.strip()[:400]}"`; the final line `assistant (final, ending): …` + `last_msg.strip()[-800:]`; the whole state is `[-6000:]` code points (`DGX_KEV_CHARS`). The transcript file is opened in **text mode with the locale encoding** | — | `:64-91` | PT-CP, PT-SPLIT |
| BC-HK-021 (new; refines BC-HK-013) | `emit` stdout = `json.dumps({"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": ctx}})` + `\n`. Python separators and **ensure_ascii**, so the bytes are pure ASCII. Pinned heuristic sample: `{"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": "continue. You ended your turn right after announcing the next step (\"\u2026Now I'll run the linter on caf\u00e9\u2026\") without doing it."}}`. The log line uses Python `repr(tail)` (quote choice: `"it's"`, `'say "hi"'`, `'both \' and "'`; non-printables `\x07`, `\u2028` escaped; printable non-ASCII kept). The exporter parses this log (BC-EX-014), so a Go hook needs a `pyrepr` for log parity | pinned (`hk.py`) | `:193-206` | PT-JSONLEN, PT-STR |
| BC-HK-019 (new) | **The hook has no top-level guard.** Any uncaught exception gives a traceback on stderr, **exit 1** and no stdout; Claude Code treats that as a non-blocking hook error, so the stop proceeds (effectively "allow"; external behavior LOW). Crash paths: (1) stdin JSON not an object (`:214`); RecursionError on deep stdin (not a ValueError, so not caught at `:212`). (2) `last_assistant_message` truthy and not a str (`:215`). (3) On the Kev path only (not non-English, not `stop_hook_active`, autocontinue on, not `?`, not a colon fake): the transcript contains **invalid UTF-8**, so the line iterator raises UnicodeDecodeError, which is a ValueError outside the inner try and is not OSError (`:69` vs `:84`); a transcript line that is JSON but not an object (`:74`); `message` truthy and not a dict (`:75`); a text block whose `text` is truthy and not a str (`:81`, `p.endswith`). (4) A Kev response that is a JSON non-dict, or `answers.turn_complete` that is not a dict (`:115-116`, AttributeError not in the except list); `http.client.HTTPException` subclasses such as `BadStatusLine`/`IncompleteRead` (not OSError; LOW). (5) Import-time `float(DGX_KEV_THRESHOLD/TIMEOUT)`, `int(DGX_KEV_MESSAGES/CHARS)` on bad values (`:33-36`) | — | `:33-36,64-121,209-215` | PT-EXC, PT-ENC, PT-PARSE |
| BC-HK-012 (refined) | The regex fallback runs only when Kev returns no score (`:263-270`); its message embeds `tail[-100:]` (code points). `heuristic` is computed **before** the Kev call (`:244`) but used only after | — | `:244-270` | PT-CP |

---

## Delta Summary

- **New items added:**
  - Status line: 35 new BCs (BC-SL-054 … BC-SL-088).
  - Status line: 33 broad-sweep BCs refined, with pinned examples or corrected edges: 001, 002, 004, 005, 006, 007,
    008, 009/010, 011, 012, 013, 016, 017, 019, 020, 021, 022, 023, 024, 025, 026, 027, 028, 029, 032, 033, 034, 038,
    039, 040, 041, 043, 052. Confirmed with pinned runs: 031, 035, 036, 037.
  - Crash-path catalogue: **40 paths** (CP-S01…S17, CP-T01…T07, CP-N01…N02, CP-C01…C10, CP-X01…X04). 36 are guarded
    (degraded 29 bytes, exit 0) and 4 are outside the guard (2 parity-relevant: empty stdout, exit 1).
  - Proxy: 5 new (BC-PX-032 … 036) and 4 refined (005, 017, 019 via the BC-PX-034 truth table, 020). I1 and I2 are
    resolved against the code.
  - Stop hook: 8 new (BC-HK-014 … 021) and 5 refined (003, 007, 008, 012, 013). RE2 compile table: 1 of 6 hook
    patterns fails (the lookbehind at `:177`). Python/Go `\b` divergences are pinned.
  - Contradictions with research inputs: 3 (CONTRA-1 float floor-div hazard is theoretical for these divisors;
    CONTRA-2 the tap does not merge; CONTRA-3 `PYTHONUTF8=1` changes stdin behavior).
  - A0 input-pinning matrix and A8 side-effect order (new artifacts for the P1 harness).
- **Existing items refined:** 33 SL + 4 PX + 5 HK = 42. No retractions; no CONV-ABS markers were needed.
- **Remaining gaps:** listed below.

## Remaining Gaps / next candidate scope (verbatim-carryable)

1. Status line, row-1 assembly golden: compose 3 complete row-1 and row-2 strings end to end (all widgets present,
   ANTH lane with limits, DGX lane with ⛏ n/a) from a copied `render_lane`/`render_telemetry_fields`, to pin
   separator placement and the exact visible width per segment for `trim_to_fit` table tests.
2. Status line, `get_sample` state machine at function level with pinned multi-step sequences (fresh → failed →
   cached-within-TTL → stale > 15 s → > 300 s), including the KEEP_DEAD cached-path quirk and the `hist`
   normalization of legacy list points. Pin the exact cache JSON after each step (cache-swap fixtures).
3. Status line, `effective_rl` + limits interplay over time: stdin present/absent/`{}` sequences across RL_KEEP,
   with expired windows, and the sticky CP-S09 path. Pin the outputs and cache contents.
4. Status line, `_mix_counts` turn machine exhaustive table: lines without timestamps, user lines that are
   tool_result only vs mixed content, `cur` persisted across refresh boundaries (unfinished turn at parse end),
   `lu` carried across refreshes, and CP-T05 reachability with a concrete transcript.
5. Status line, `json.dumps` length oracle coverage: ints beyond 2^63, floats near the repr switch points (1e16,
   1e-4/1e-5), astral and control characters inside nested tool_use inputs. Pin a 50-case length table for
   `pyjson.DumpsLen`.
6. Owner decisions needed: (a) harness stdio mode (strict UTF-8 locale vs `PYTHONUTF8=1`; CONTRA-3 / BC-SL-076);
   (b) whether foreign-cache crash paths CP-C01…C10 are in the byte-parity scope or documented as known diffs;
   (c) whether the Go reader keeps the sticky transcript crash (BC-SL-068) through parity, as D4 implies.
7. Proxy: `responseheaders` stream-mode decision table vs mitmproxy semantics (`stream=True` vs callable vs
   `False`) and what `get_text(strict=False)` returns for streamed flows (decides path (b) of BC-PX-034 in the
   tapped-but-no-usage case). This needs a mitmproxy-source reading; the version is not pinned in the repo.
8. Proxy: `normalize_for_dgx` byte-level effect of `json.dumps(req)` re-serialization (key order, ensure_ascii,
   float repr) as pinned examples for the P3 replay, plus `uses_server_tool` with a non-list `tools`.
9. Stop hook: Kev path timing semantics (`kev_pdone_median` early stop uses the *last* call's elapsed, even when
   that call failed and returned `(None, None)`, so `t` is None and there is no early stop). Pin with a fake
   `kev_pdone` sequence. Also log-line format parity (`time.strftime` local, `repr(tail)`) for the exporter's
   substring tallies.
10. Exporter (P2): function-level BCs and its own crash catalogue (no guard around the request handler; e.g.
    `status: null` TypeError, BC-EX-004), with pinned exposition text for a synthetic ledger.

## Novelty Assessment

Novelty: SUBSTANTIVE

Removing this round would change how the system is specified. It adds:

- a 40-entry crash-path catalogue, of which the broad sweep listed none, including the sticky paths;
- 35 new status line contracts. Several are new observable behaviors that a byte-identical port would otherwise
  get wrong: `/0K` and `/1000K`, `1000k` without promotion, `//` project label, `rem=0.9·len` band flip,
  first-line usage dedup, two-refresh long lines, BOM-accepted transcript lines, the NaN-driven crashes in KV and
  the sparkline, and row-2 hidden at negative COLUMNS;
- a code-resolved answer to I1 and I2 that contradicts the research doc's description of the tap;
- an exact RE2 compile verdict for the hook.

## Convergence Declaration

Another round is needed. Substantive gaps remain: row assembly goldens, the multi-step state machines for
`get_sample`/`effective_rl`/turn machine, json.dumps length oracle coverage, and the mitmproxy streamed-body
semantics. See the list above.

## State Checkpoint
```yaml
pass: 3
round: 1
status: complete
files_scanned: 11
timestamp: 2026-11-14T08:30:00Z
novelty: SUBSTANTIVE
new_bcs: {SL: 35, PX: 5, HK: 8}
refined_bcs: {SL: 33, PX: 4, HK: 5}
crash_paths: {total: 40, guarded: 36, outside_guard: 4, parity_relevant_outside: 2}
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/pin/
next: pass 3 round 2 (carry "Remaining Gaps" verbatim)
```
