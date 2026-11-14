# General research — Go port: byte-identical parity, cross-platform, toolchain (P1 input)

- **Type:** general (technology) · **Date:** 2026-11-14 (evidence gathered 2026-11-13/14)
- **Feeds:** P1 (`hylo statusline` at parity), later P2 (exporter), P3/P4 (proxy lock, services)
- **Inputs read:** `docs/PLAN.md`, `docs/RESUME.md`, `CLAUDE.md`, `legacy/dgx_statusline.py` (scanned
  in full for formatting constructs), `legacy/dgx_ledger_exporter.py` (output section only)
- **Evidence tags:** **[documented]** = official docs, source, or registry; **[community-observed]** =
  issues, blogs, third-party reports; **[inferred]** = my reasoning from the documented facts.
  Every version number below was checked against proxy.golang.org, go.dev, PyPI, or GitHub releases
  unless marked otherwise.

---

## Executive summary

1. **Go floor is sound.** Latest stable is **go1.27.4**, and **go1.26.11** is still supported (both
   2026-11-10). Go 1.26 stays supported until Go 1.28 ships, expected around February 2027. Set
   `go 1.26.0` in go.mod, build releases with 1.27.x, and run CI on **both** 1.26.x and 1.27.x,
   because in 1.27 `encoding/json` v1 runs on the v2 implementation. [documented]
2. **Byte parity is reachable, but only through a small `internal/pyfmt` package** that reproduces
   Python semantics: banker's `round`, CPython float `//` and `%`, Python `max`/`min` with NaN,
   `nan`/`inf` spelling, Python `repr(float)`, the *length* of `json.dumps` output (ensure_ascii,
   `", "` separators), `bytes.splitlines`, and the `isinstance(x,(int,float))`-accepts-`bool` rule.
   Plain `fmt`/`strconv` already match Python on finite `.Nf` formatting. [documented + inferred]
3. **Arm64 FMA is a real hazard.** The Go compiler may fuse `x*y±z` on arm64, which covers both the
   macOS CI runners and Apple-silicon Macs. `colorsys.hsv_to_rgb` (truecolor bytes, L147) and the
   window-age math (L558–559) contain fusable expressions. Wrap the intermediate products in
   explicit `float64(...)` conversions. [documented]
4. **Python exceptions are part of the output contract.** Any `TypeError` or `ValueError` on
   malformed input makes the whole status line `statusline degraded` (L1243–1244). Example: a
   transcript `text` that is a number (L1143). The Go port must reproduce those paths.
   Differential fuzzing is the way to find them. [inferred from source]
5. **The Python reference runs on Windows CI** if the harness adds a stdlib-only `sitecustomize.py`
   shim with four jobs: freeze `time.time`, force UTF-8 stdin/stdout, force LF newlines, and
   pre-seed `proc_start` in the session cache so the `ps` walk never runs. Recommendation:
   **live differential on all three OSes** (Python and Go on every case) as the gate, plus
   committed Linux-generated goldens. A few OS-specific cases (e.g. project dir `/` →
   `\` on Windows) get per-OS goldens. [documented + inferred]
6. **Pin Python with `actions/setup-python`.** Runner defaults differ: ubuntu-24.04 has 3.12.3,
   macos-15 has 3.15.2, windows-2025 has 3.12.10. Python 3.15 (2026-10-09) made UTF-8 mode the
   default, so set `PYTHONUTF8=1` explicitly to get the same behavior on every version.
   [documented]
7. **Process ancestry needs no cgo and no gopsutil.** Use `golang.org/x/sys`:
   `unix.SysctlKinfoProc` on macOS, `/proc/<pid>/stat` field 22 plus `btime` on Linux, and
   Toolhelp32 + `GetProcessTimes` on Windows. Truncate the start time to whole seconds, because
   `ps lstart` has 1-second resolution and parity depends on it. [documented + inferred]
8. **Dependencies:** no YAML in P1. For P4 config, use `go.yaml.in/yaml/v3` v3.0.6
   (security-only) or v4.0.0 (released 2026-11-04). `gopkg.in/yaml.v3` is archived. For P2,
   **hand-write the Prometheus text format**: the legacy exporter is hand-written with Python
   `str()` value formatting and its own HELP/TYPE ordering, so `client_golang` cannot be
   byte-identical. [documented + inferred]
9. **Hardening picks:** golangci-lint **v2.15.0** (bundles staticcheck v0.8.2 and gosec),
   govulncheck **v1.9.0**, native `go test -fuzz` (one target per invocation), `pgregory.net/rapid`
   v1.3.0 or `testing/quick` for properties. For mutation testing, use **avito-tech/go-mutesting**
   (pinned pseudo-version), scheduled and non-gating. Gremlins has Go 1.26 compatibility doubts
   and an anomalous v0.6.0 tag. [documented + community-observed]
10. **CI and release:** `actions/setup-go@v7` with `go-version-file`; measure Windows cache
    restore and turn caching off there if it is slow. Run the **gitleaks v8.30.1 binary** with
    checksum verification; the action is also license-free for personal repositories.
    **GoReleaser v2.20.2** with `CGO_ENABLED=0`, `-trimpath`, `mod_timestamp`, cosign keyless,
    Syft SBOMs and `actions/attest@v4`. macOS notarization is still an open owner question.
    [documented]

---

## Q1 — Go toolchain status (November 2026)

| Item | Finding | Tag |
|---|---|---|
| Latest stable | `go1.27.4` (2026-11-10). Go 1.27.0 shipped Aug 2026. Point releases: 1.27.1 09-01, .2 10-08, .3 10-19, .4 11-10 | [documented] go.dev/dl JSON, go.dev/doc/devel/release |
| Other supported line | `go1.26.11` (2026-11-10). 1.26.0 shipped 2026-02-10 | [documented] |
| Policy | "Each major Go release is supported until there are two newer major releases." Go 1.25 is out of support since 1.27.0. Go 1.26 loses support when 1.28 ships (≈Feb 2027) | [documented] |
| `testing/synctest` | GA since 1.25. 1.27 adds `synctest.Sleep` and `httptest.NewTestServer` (in-memory network). It virtualizes time **only inside the test process**, so it cannot freeze an exec'd CLI or the Python child | [documented] |
| `os.Root` | Since 1.24; 1.25 added `MkdirAll`, `ReadFile`, `WriteFile`, `Rename` and more. Useful later for cache-dir confinement | [documented] |
| `encoding/json/v2` | 1.26: experiment only (`GOEXPERIMENT=jsonv2`, no compatibility promise). **1.27: available without a flag, and `encoding/json` v1 is now backed by the v2 implementation** ("Marshaling and unmarshaling behavior is preserved, but the exact text of error messages may differ"; opt-out `GOEXPERIMENT=nojsonv2`). The v2 API rejects invalid UTF-8 and duplicate names by default | [documented] go.dev/doc/go1.27 |
| Iterators, `tool` directive | Range-over-func stable since 1.23. `tool` directive in go.mod since 1.24 | [documented] |
| Platform floor | **Go 1.27 requires macOS 13 Ventura+.** No Windows floor change was found in the 1.27 notes | [documented] |
| FMA | No change announced in 1.26/1.27. The spec still allows fusion, and ARM64 SSA rules fuse | [documented] go.dev/ref/spec, ARM64.rules |

**Implications.**
- With a 1.26 floor, do not import `encoding/json/v2`; it is an experiment there.
- Use v1 `encoding/json` with `Decoder.UseNumber`.
- Because 1.27 swaps the v1 engine, the parity suite is the regression net for invalid-UTF-8 and
  duplicate-key behavior on both toolchains. **[inferred]**

**Recommendation.**
- go.mod: `go 1.26.0`, plus a `toolchain go1.27.4` line so local builds and releases are
  reproducible.
- CI matrix axis `go: [1.26.x, 1.27.x]` on Linux (full OS matrix on 1.27.x only, to save minutes).
- Raise the floor to 1.27 when 1.28 ships. That is policy-driven and needs no re-decision.

---

## Q2 — Python → Go semantic pitfalls for byte-identical output

### 2a. Pitfall catalogue with Go equivalents

| # | Python behavior | Naive Go (wrong) | Correct Go equivalent | Tag |
|---|---|---|---|---|
| P1 | `round(x)` → **int**, ties to even | `math.Round` (ties away from zero) | `int64(math.RoundToEven(x))`. NaN raises `ValueError` and inf raises `OverflowError` in Python, so map both to the "degraded" path | [documented] |
| P2 | `round(x, n)` rounds the exact binary value in decimal (`round(2.675,2)=2.67`) | `RoundToEven(x*100)/100` (gives 2.68) | `strconv.ParseFloat(strconv.FormatFloat(x,'f',n,64),64)` | [documented] |
| P3 | `f"{x:.Nf}"`: correctly rounded, half-even on the exact binary value (dtoa mode 3) | — | `strconv.FormatFloat(x,'f',N,64)` / `%.Nf` **match for all finite values, including `-0`** | [documented; implementation-based, not exhaustively proven] |
| P4 | `nan`, `inf`, `-inf` spelling | `NaN`, `+Inf` | `pyfmt.F(x,N)` special-cases non-finite values | [documented] |
| P5 | `{:>2d}`, `{:02d}` on ints | — | `%2d`, `%02d` are identical for ints. Python `:d` on a float **raises** | [documented] |
| P6 | int `//` and `%` floor toward −∞ | Go `/` and `%` truncate | `pyfmt.FloorDivInt`/`ModInt` (adjust when signs differ) | [documented] |
| P7 | float `//` and `%`: fmod-based (`1.0//0.1 == 9.0`); `%` takes the divisor's sign | `math.Floor(a/b)`, `math.Mod` | Port CPython `float_divmod`: `mod=math.Mod(a,b)`; `div=(a-mod)/b`; sign fix; snap with `floor` plus a >0.5 check; zero-sign rules | [documented] CPython floatobject.c |
| P8 | `max(a,b)` keeps the first argument unless `b>a` (so `max(nan,0)=nan`, `max(0,nan)=0`) | builtin `max` / `math.Max` propagate NaN | `pyfmt.Max(a,b){ if b>a {return b}; return a }`, applied in the same argument order | [documented] |
| P9 | `int(x)` truncates; raises on NaN/inf | `int64(NaN)` is implementation-defined | Check finiteness, then truncate; non-finite → degraded | [documented] |
| P10 | `isinstance(True,(int,float))` is **True** (bool subclasses int) | type switch on `float64` only | Numeric guard accepts `bool` as 0/1. `f"{True:.2f}"`="1.00" | [documented] |
| P11 | Truthiness: `x or 0`, `.get(k) or default` (0, 0.0, "", [], {}, None are falsy) | `if v != nil` | `pyfmt.Truthy(v any)` | [documented] |
| P12 | `len(str)` counts **code points** | `len(s)` counts bytes | `utf8.RuneCountInString`. Do **not** use go-runewidth: legacy counts code points, not cells | [documented] |
| P13 | `json.dumps(v)` defaults: `", "`/`": "`, `ensure_ascii=True` (anything outside 0x20–0x7E → `\uXXXX`, astral → surrogate pair = 12 chars, DEL escaped), short escapes `\" \\ \n \r \t \b \f`, insertion order, float `repr`, `NaN`/`Infinity` emitted | `json.Marshal` (compact, HTML-escapes `<>&`, U+2028/9 always escaped, map keys sorted, Go float layout) | `pyfmt.DumpsLen(v)` computes the **length only** (order-independent), using P14 for floats and `json.Number` to keep int vs float | [documented] |
| P14 | `repr(float)`: shortest round-trip digits; exponent form iff decpt ≤ −4 or decpt > 16 (`1e-05`, `0.0001`, `1e+16`, `1000000000000000.0`), always `.0` for integral values | `FormatFloat(f,'g',-1,64)` (switches at 1e+06) | Take digits from `FormatFloat(f,'e',-1,64)` and re-layout with the CPython `'r'` rules | [documented] CPython pystrtod.c |
| P15 | `json.loads`: accepts `NaN`/`Infinity`; arbitrary-precision ints; bytes input auto-detects encoding (UTF-8 BOM → `utf-8-sig`) and decodes with `surrogatepass`; **invalid UTF-8 raises** (line skipped); duplicate keys last-wins; lone `\ud83d` kept | Go rejects NaN/Infinity; float64 for numbers; replaces invalid UTF-8 / lone surrogates with U+FFFD; rejects BOM | `UseNumber`; pre-check `utf8.Valid(line)` and skip like Python. Document remaining divergences (NaN literals, BOM, CESU surrogates) as known edge cases and keep them in the fuzz corpus. Lone surrogate: Python len 1 = Go U+FFFD 1 rune, `DumpsLen` 6 = 6, so equal | [documented] |
| P16 | `bytes.splitlines()` splits on `\n`, `\r\n` **and bare `\r`** | `bytes.Split(b,"\n")` | `pyfmt.SplitLinesBytes` | [documented] |
| P17 | `str.strip()` whitespace includes `\x1c`–`\x1f`; `split(None,n)` likewise | `strings.TrimSpace` / `unicode.IsSpace` lacks `\x1c`–`\x1f` | `strings.TrimFunc(s, pyIsSpace)` | [documented] |
| P18 | `int("…")`/`float("…")` accept surrounding whitespace, `_` separators, Unicode digits, `"nan"`/`"inf"` in any case | `strconv.Atoi`/`ParseFloat` are stricter | `pyfmt.ParseInt`/`ParseFloat` for env vars and `_fmt_*` coercions | [documented] |
| P19 | `datetime.fromisoformat` (3.11+ is permissive; offset-less means **local time**) | `time.Parse(time.RFC3339Nano)` | Parser for the Claude Code subset plus a fuzz diff. Inject the `*time.Location`. Go ignores `TZ` on Windows (uses system zone) [inferred from Go source behavior; not re-verified this session] | [documented]/[inferred] |
| P20 | `time.time()` = `float(ns)/1e9` | — | `float64(t.UnixNano())/1e9` is identical. Pass the frozen instant as a decimal string that both sides parse | [documented] CPython pytime.c |
| P21 | `dict` iterates in insertion order | Go map order is random | Iterate the JSON **array** order where legacy relies on it (VM "first wins", L175–184) | [documented] |
| P22 | `sorted()` is stable; strings compare by code point | — | `slices.SortStableFunc`. UTF-8 byte order equals code-point order (matters for the P2 exporter's `sorted(dict.items())`) | [documented] |
| P23 | Regex: Python `re` has lookarounds and Unicode `\d`; Go RE2 has neither | — | Legacy statusline uses only RE2-safe patterns with explicit `[0-9]` (L137, L1017) | [documented] |
| P24 | FMA: Python rounds every op | Go may fuse `x*y+z` / `z-x*y` on arm64/ppc64/s390x | `float64(x*y) + z` (an explicit conversion prevents fusion; parentheses do not) | [documented] Go spec |
| P25 | `print()` appends `\n`; **Windows text stdout writes `\r\n`**; stdout encoding is the locale's before 3.15 (cp1252 → `UnicodeEncodeError` on `◨`) | — | Go always writes `\n` and UTF-8. Harness shim: `sys.stdout.reconfigure(encoding="utf-8", newline="\n")`. Capture bytes, not text-mode subprocess output | [documented] |
| P26 | `os.path` is `ntpath` on Windows: `normpath("/")` → `\`, `abspath("/x")` → `D:\x` | — | `path/filepath` matches per OS. Expect per-OS output for the root-dir case | [documented] |
| P27 | Any uncaught exception → `statusline degraded` (exit 0). Import-time env parse failure (L73–77) → traceback, exit 1 | Go would panic or return an error differently | One `recover()` at the top that prints the identical degraded line. Mirror each implicit-raise site (see 2b) | [inferred from source] |

### 2b. Where these occur in `legacy/dgx_statusline.py` (line numbers)

| Pitfall | Lines | Notes |
|---|---|---|
| P1 banker's `round` | **1171** `round(n/total*100)` | Drives the composition `%`. Must be `RoundToEven` |
| P2 `round(x,n)` | **234** `round(usd, 4)` | Cache only (cost-history.json); matters for the cache swap test |
| — deliberate half-up | **426** `int(pct/10+0.5)` | Already avoids `round` (review #5.2). Go `int(x+0.5)` is fine for x ≥ 0 |
| P3 `.Nf` | 435–437, 479, 522, 599, 616, 625, 635, 700, 741, 761–762, 778–783, 795, 813–819, 857, 870–873, 882–885 | Safe for finite values |
| P4 nan/inf spelling | 741 (`r`,`q`), 761 (`kv`), 783 (`rate`), 813–819 (`w`,`wall`,`t`,`cents`) | VM values come from `float(s["value"][1])` (L178), which accepts `"NaN"`/`"+Inf"`. Only TTFT is NaN-guarded (L793) |
| P5 width/zero-pad | 525, 527, 548, 561, 829, 831 (`:02d`); 1172 (`:>2d`) | Ints only |
| P6 int `//`,`%` | 548, 561, 829–831, 859 | Operands are non-negative by guards, but use helpers anyway |
| P7 float `//`,`%` | **525–529** (`rem//86400`, `rem%86400`), **546**, **560** (`win_ms//60000`), **826** | Fractional dividends (≈1e8 ms) put the `a/b` rounding error near ulp(q), so `math.Floor(a/b)` can differ. Port CPython [inferred] |
| P8 `max`/`min` | 146, 422, 479, 508, 674–675, 759 | NaN from VM → Python order-dependent result |
| P9 `int()`/`ceil` raise | 148, 426, 675, 683, **759** `math.ceil(kv/25)` | `kv = NaN` → `ValueError` → degraded |
| P10/P11 bool & truthiness | 420, 478, 506, 535, 540, 551, 557, 585–598, 602, 622, 628, 993, 1079, 1105–1112 | `"used_percentage": true` renders as 1% |
| P12 code-point len | **153** `visible()` → **1195** `trim_to_fit`; 1122, 1133, 1143, 1145 | Width trimming and composition byte counts |
| P13/P14 `json.dumps` length | **1138, 1140, 1147** | Feeds the ▤/❙ composition percentages |
| P15 `json.loads` | 171 (VM), 193 (cache), 1202 (stdin, text), **1061** (transcript bytes lines) | 1061 is where invalid UTF-8, NaN and BOM diverge |
| P16 splitlines | **1059** | |
| P17 strip/split | 444–445 (`LOCAL_MODEL_PREFIXES`), 284 (`ps` output), 487 `rstrip("*")`, 1196 `rsplit(SEP,1)` | |
| P18 int/float parse | 73–77, 89 (import time), 853, 866, 878, 1188 | |
| P19 datetime | **983** `fromisoformat(...).timestamp()`; **286** `strptime`+`mktime` (local time, 1-s resolution) | 286 is bypassed in the harness (Q3) |
| P20 clock | 231, 243, 304, 322, 408, 499, 558, 825–826 | Nine separate reads; frozen in tests |
| P21 order | 175–184 | First-wins over the result array |
| P23 regex | 137, 1017 | RE2-safe |
| P24 FMA | **147** `colorsys.hsv_to_rgb` (`v*(1.0 - s*f)`, `v*(1.0 - s*(1.0-f))`); **558–559** `(now-win_start)*1000 - dur` | Truecolor bytes and the ⌂ threshold |
| P25 output | 1234 `print("\n".join(rows))`, 1244 | |
| P26 paths | 373, 383, 390, **460** `basename(normpath(proj_dir)) or normpath(proj_dir)` | |
| P27 implicit raises | e.g. **1143** `len(blk.get("text") or "")` with a numeric `text`; 994 comparisons on str `output_tokens`; 460 non-str `proj_dir` | Each → degraded output |
| Other | 405 `hashlib.sha1` (cache key; gosec G401/G505 → `//nolint` with rationale); 201–204 `mkstemp`+`os.replace` (Python leaks the temp file on failure) | Output-neutral |

Absent from the statusline: `{:,}` grouping, lookaround regexes, `str.split()` on user text,
`sorted` with custom keys. **[documented from source]**

**Recommendation.**
- Create `internal/pyfmt` before any widget: `F`, `Round`, `RoundN`, `FloorDiv`/`Mod` (int and
  float), `Max`/`Min`, `Truthy`, `Num` (with the bool rule), `Repr`, `DumpsLen`,
  `SplitLinesBytes`, `Strip`, `ParseInt`/`ParseFloat`.
- Give each function a table test whose expected values were **generated by running CPython**
  (committed as a fixture with the generator script), plus a fuzz target.
- Model the "degraded" contract as `errDegraded` propagated to one top-level handler.

---

## Q3 — Parity harness design

### 3a. Pinning the four nondeterminism sources without touching `legacy/`

| Source | Python side (harness only) | Go side | Tag |
|---|---|---|---|
| **Clock** | `testhooks/sitecustomize.py` on `PYTHONPATH`: `import time; time.time = lambda: float(os.environ["HYLO_TEST_NOW"])`. Enough here because legacy only calls `time.time()` through the module attribute; `fromisoformat().timestamp()` is clock-independent; `mktime`/`strptime` only run on the `ps` path, which is bypassed (below). **No need for time-machine** (3.6.0, CPython ≥3.11) or freezegun (1.5.5); libfaketime has no Windows support. Do **not** run Python with `-I` or `-S` (they disable the hook) | `statusline.Render(in, Env{Now: func() time.Time})`. The binary honors `HYLO_TEST_NOW` for exec-level tests. synctest does not apply (separate process) | [documented] |
| **Metrics** | `DGX_SL_VM_URL=<httptest URL>` (Python bypasses proxies via `ProxyHandler({})`, L168) | Same URL. `http.Transport{Proxy: nil}` to mirror the proxy bypass | [documented] |
| **Process tree / ⌂** | **Pre-seed `"proc_start": <int>`** in `statusline-<sid>.json`. `claude_window_start` returns the cached value (L273–275) and never runs `ps`, which makes Windows behave like macOS | Go reads the same cache key first (parity). The probe sits behind an interface; per-OS probes get their own unit tests | [inferred from source] |
| **Cache / HOME** | Fresh temp dir per case. Set **both** `HOME` and `USERPROFILE`: Python ≥3.8 `expanduser` ignores `HOME` on Windows | Same. Pass `cmd.Env` per subprocess (not `t.Setenv`) so cases can run in parallel | [documented] |
| **I/O encoding** | Shim: `sys.stdin.reconfigure(encoding="utf-8")`, `sys.stdout.reconfigure(encoding="utf-8", newline="\n")`; env `PYTHONUTF8=1` | Always UTF-8, LF | [documented] |
| **Other env** | `TZ=UTC`, `COLUMNS`, `LOCAL_MODEL_PREFIXES`, `DGX_SL_*`; unset `HTTP(S)_PROXY` | Same | [inferred] |

The shim is about 10 lines of stdlib Python. It lives in `internal/statusline/testdata/pyhooks/`
(Go ignores `testdata/`), so `legacy/` stays untouched (D10).

### 3b. Fixture and case model

- **Case = directory** containing `stdin.json.tmpl`, an optional transcript generator spec,
  `metrics.json` (canned VM response or a `down`/`500`/`garbage` mode), `env`, and an optional
  `steps` list for multi-refresh sequences. Each step advances the clock and appends transcript
  lines; this exercises the incremental parser, the id-memory window, rebuild counting and TTL
  caching. Compare the output at **every step**.
- **Paths are templated at runtime.** `transcript_path` and `workspace.project_dir` point into
  the per-case temp dir. Fake `.git` dirs (HEAD, worktree pointer files) are **created at test
  time**: a committed directory named `.git` inside the repo is not tracked as ordinary files.
  [documented git behavior] Goldens therefore contain no machine paths, only basenames.
- **Synthetic only** (public repo): a committed Go generator emits the review's edge cases.
  These are split assistant messages repeating `usage`, `compact_boundary`, a >512 KB line,
  interleaved tool_results, rebuilds, empty thinking blocks, images in tool results, non-ASCII
  and astral text, invalid UTF-8 lines, and NaN metric values.
- **Fake VM:** `httptest.NewServer` handler that checks the path is `/api/v1/query` and returns
  the canned instant-vector JSON. Avoid timeout-based "slow" cases (the 1.5 s timeout makes them
  flaky in CI); simulate failures with a closed listener, 5xx, or invalid JSON.
- **Cache swap test:** Python writes the caches, Go reads them, and the reverse.
  `cost-history.json` (30 days of seeded history) and the mix cache carry over at cutover, so
  schema parity is part of D7's spirit. [inferred]

### 3c. Golden strategy across OSes

The Python side **does** run on Windows CI under the shim. `os.getppid` works, `ps` is never
reached because of the pre-seed, and `os.replace` uses `MoveFileExW` with
`MOVEFILE_REPLACE_EXISTING`. **[documented + inferred]**

| Tier | What | Where | Gate? |
|---|---|---|---|
| **A — live differential** | For each case, spawn pinned CPython on `legacy/dgx_statusline.py` with the shim, run Go in-process (and via the built binary for a subset), then `bytes.Equal` | ubuntu-24.04, macos-15 (arm64), windows-2025 | **Yes: the P1 exit criterion** |
| **B — committed goldens** | `go test ./internal/statusline -update` writes **Python's** output (never Go's) to `testdata/**/*.golden`, generated on Linux. Go must match on every OS. OS-dependent cases (root `/`, drive letters) use `*.windows.golden` | All OSes; runs without Python | Yes (fast and hermetic) |
| **C — differential fuzz** | Generator produces random valid stdin and transcripts; run both; diff. About 30–60 ms Python start-up per run, so thousands of cases per nightly job (not `go test -fuzz`) | Linux nightly | No (finds P27-class divergences) |

- `.gitattributes`: `testdata/** -text` to stop `core.autocrlf` rewriting golden bytes on Windows
  checkouts. [documented]
- `testscript` (go-internal v1.16.0) is optional for exec-level CLI scripts. Plain Go tests are
  enough for P1. [documented]

**Recommendation.**
- Tier A plus Tier B from day one; Tier C once all widgets are ported.
- Python pinned via `actions/setup-python@v7` to the **same minor version the owner's
  production prototype runs** (open question O1).
- The Tier A test skips with a clear message when `HYLO_PARITY_PYTHON` is unset, so contributors
  without Python can still run `go test`. CI always sets it.

---

## Q4 — Cross-platform specifics

### 4a. Process ancestry (window age ⌂) without cgo

| OS | Mechanism | Caveats | Tag |
|---|---|---|---|
| macOS | `unix.SysctlKinfoProc("kern.proc.pid", pid)` → `Eproc.Ppid`, `Proc.P_comm` (≤16 bytes, NUL-terminated), `Proc.P_starttime` (Timeval, Unix epoch). x/sys calls libSystem through Go's trampolines, so no cgo | Name truncation (`claude` fits) | [documented] |
| Linux | `/proc/<pid>/stat`: parse after the **last `)`**; field 4 ppid, field 2 comm (≤15 bytes), field 22 starttime in ticks. Unix start = `btime` (`/proc/stat`) + ticks/`CLK_TCK` | `CLK_TCK` = 100 is a practical assumption, not a guarantee. `tklauser/go-sysconf` is the cgo-free way to read it | [documented] |
| Windows | `CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS)` + `Process32First/Next` → `ParentProcessID`, `ExeFile`; `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` + `GetProcessTimes` | PID reuse: check that the parent's creation time precedes the child's. Name is `claude.exe` (strip `.exe` case-insensitively) | [documented] |

Libraries:
- `shirou/gopsutil/v4` is **v4.26.10** (2026-10-24), cgo-free on darwin since v4.24.9. Its go.mod
  lists 11 module requirements; overkill for one function.
- `mitchellh/go-ps` v1.0.0 is archived and has no start time.
- `tklauser/ps` v0.0.4 derives Linux start time from the `/proc/<pid>` ctime, not field 22, so it
  is less exact.

**Parity details.**
- Python's value comes from `ps lstart`: local time, **1-second resolution**, through `mktime`.
  Go's native start time has sub-second precision. Truncate it to whole seconds so
  `int(win_ms // 60000)` flips at the same moment. Document this as a parity rule. **[inferred]**
- On Windows the prototype never shows ⌂ (no usable `ps`). Implementing it in Go is a behavior
  addition (see O3).

**Recommendation.** Write the probe on `golang.org/x/sys` only, about 80–150 lines per OS behind
`internal/platform`, with build tags. `x/sys` is the one justified non-stdlib dependency (Go-team
maintained; also needed for locks and services). Walk at most 6 levels, as legacy does (L279).

### 4b. Atomic replace and locking

- **Rename.** Go `os.Rename` on Windows uses `MoveFileExW(MOVEFILE_REPLACE_EXISTING)`, the same
  call as Python `os.replace`. Go documents rename as not atomic on non-Unix systems. It fails
  when another process holds the destination open without `FILE_SHARE_DELETE`. Go's `os.Open`
  does **not** request `FILE_SHARE_DELETE` (issue 32088), and neither does Python's `open`.
  **[documented]**
- **Concurrent refreshes.** Several status-line refreshes running at once on Windows can
  therefore hit sharing violations. Legacy swallows them ("cache loss is cosmetic").
  Recommendation: mirror that (ignore the error, remove the temp file, which Python leaks),
  optionally with 2–3 short retries on `ERROR_SHARING_VIOLATION`/`ERROR_ACCESS_DENIED`.
- **Locking (P3 proxy singleton, not P1).** `gofrs/flock` is **v0.13.2** (2026-11-08):
  `flock(2)` on Unix, `LockFileEx` on Windows. A roughly 60-line `x/sys` wrapper modeled on
  `cmd/go/internal/lockedfile/internal/filelock` (internal, not importable) avoids the dependency.
  Recommendation: own wrapper. Use a **separate, never-deleted lock file** next to the state
  file. **[documented]**

### 4c. Directories

| | `os.UserCacheDir` | `os.UserConfigDir` | Legacy |
|---|---|---|---|
| Linux | `$XDG_CACHE_HOME` or `~/.cache` | `$XDG_CONFIG_HOME` or `~/.config` | `~/.cache/dgx-llm` everywhere (`expanduser`, L78) |
| macOS | `~/Library/Caches` | `~/Library/Application Support` | same |
| Windows | `%LocalAppData%` | `%AppData%` | `%USERPROFILE%\.cache\dgx-llm` |

[documented]

**PLAN conflict.** PLAN §6 says `~/.config/hylo/config.yaml` and, on Windows,
`%APPDATA%\hylo\config.yaml`. On macOS, `os.UserConfigDir` returns `~/Library/Application Support`,
not `~/.config`, so `internal/config` must compute the path explicitly (honor `XDG_CONFIG_HOME`,
else `~/.config`, and `%AppData%` on Windows). **[inferred]**

**Recommendation.**
- P1 keeps the legacy cache path, which is needed for parity and to inherit `cost-history.json`.
- The move to a hylo-owned cache dir is a P6 change with a one-time migration.

### 4d. Per-user background service (P2/P4)

- **macOS:** LaunchAgent plist in `~/Library/LaunchAgents` + `launchctl bootstrap gui/$(id -u)`.
- **Linux:** systemd user unit in `~/.config/systemd/user/` with `WantedBy=default.target` +
  `systemctl --user enable --now`; `loginctl enable-linger` is needed to run while logged out.
- **Windows:** Task Scheduler logon trigger (`schtasks /Create /SC ONLOGON`), which is
  non-admin subject to policy.
- **`kardianos/service` v1.3.0** (2026-07-06) has user-level support on macOS (legacy
  `launchctl load`) and systemd (but its default template uses `WantedBy=multi-user.target`).
  On **Windows it has no user-level/Task Scheduler backend**; it installs an SCM service, which
  needs admin rights. **[documented]**

**Recommendation.** Use hand-written templates per OS (3 small text templates plus exec of the
native tool, with per-OS fallbacks per CLAUDE.md). Do not adopt kardianos/service.

---

## Q5 — Dependencies

### YAML (needed in P4, not P1)

| Module | Latest (registry-verified) | Status | Tag |
|---|---|---|---|
| `gopkg.in/yaml.v3` | v3.0.1 (2022-05-27) | Repo **archived 2025-04-01** | [documented] |
| `go.yaml.in/yaml/v3` | **v3.0.6** (2026-10-13) | YAML-org successor, API frozen, security fixes only. `sigs.k8s.io/yaml` v1.6.0 depends on it | [documented] |
| `go.yaml.in/yaml/v4` | **v4.0.0** (2026-11-04) | Active branch; has built-in decode limits (alias-bomb budget) | [documented] |
| `goccy/go-yaml` | v1.19.2 (2026-01-08) | Independent implementation. An Oct 2026 third-party test reported unbounded alias expansion | [community-observed] |

**Recommendation.** Use `go.yaml.in/yaml/v4` when config lands (P4). By then v4 will have had
months to get point releases; it is where fixes go, and it bounds alias expansion. Fall back to
`go.yaml.in/yaml/v3` v3.0.6 if v4 is still at a bare `.0` with open regressions. In both cases,
decode with unknown-field rejection so config typos fail loudly. **[inferred]**

### Prometheus exposition (P2)

- `prometheus/client_golang` is **v1.25.0** (2026-10-08). It requires Go 1.26 and lists 12 direct
  and 11 indirect module requirements (protobuf, client_model, common, procfs, and others).
  **[documented]**
- `VictoriaMetrics/metrics` v1.45.0 is lighter (3 modules). **[documented]**
- **D7 decides it.** The legacy exporter is hand-written (stdlib `http.server`):
  - its HELP/TYPE lines are grouped idiosyncratically (e.g. both `input`/`output` HELP+TYPE before
    either set of samples, L299–306);
  - label order is fixed and samples are emitted in `sorted()` order of label tuples;
  - values use Python `str()`/`repr` (`{v}`, `{v:.0f}`; L294–306).
  - `client_golang` re-orders families, formats floats its own way and owns escaping, so it cannot
    reproduce these bytes. **[documented from source + inferred]**

**Recommendation.** Hand-write the 0.0.4 text format in `internal/ledger/exporter`:
- reuse `pyfmt.Repr` for values;
- port `esc()` exactly;
- serve `Content-Type: text/plain; version=0.0.4; charset=utf-8`;
- check the output with `promtool check metrics` in CI;
- define parity as byte-equality against the Python exporter on the same synthetic ledger.

### Dependency budget for P1

**Zero** non-stdlib runtime dependencies. `golang.org/x/sys` arrives with the window-age probe
(late P1). Test-only dependencies: optionally `pgregory.net/rapid` v1.3.0.

---

## Q6 — Hardening toolchain (policy mapping)

| Policy slot | Pick | Version (verified) | Status | CI usage |
|---|---|---|---|---|
| cargo-audit → | **govulncheck** | v1.9.0 (2026-10-11) | Go team, active | `go run golang.org/x/vuln/cmd/govulncheck@v1.9.0 ./...` on PRs and weekly. The official action is still "experimental", and its JSON/SARIF modes exit 0 even on findings, so use text mode as the gate |
| clippy → | **golangci-lint v2** (`default: standard` + `gosec`) | v2.15.0 (2026-10-16), bundles staticcheck v0.8.2 | Active | `golangci/golangci-lint-action@v9` pinned to v2.15.0; standalone staticcheck is then redundant |
| SAST | gosec (inside golangci-lint) | v2.30.0 (2026-10-23) | Active | Expect G401/G505 on `sha1` (cache key) → `//nolint:gosec // non-cryptographic cache key, matches legacy L405` |
| SAST (optional) | Semgrep CE / Opengrep | Semgrep 1.185.0; Opengrep 1.33.1 | Semgrep-maintained rules are **not OSI-licensed** since Dec 2024; `opengrep-rules` archived 2025-11-28 | Optional; low marginal value over gosec for this codebase |
| cargo-fuzz → | **`go test -fuzz`** | toolchain | One package and one target per invocation; `go test ./...` replays the seed corpus | Nightly matrix of `-run='^$' -fuzz='^FuzzX$' -fuzztime=60s`. Targets: `pyfmt.*`, transcript line parser, `DumpsLen`, `fromisoformat` subset. Commit crashers to `testdata/fuzz/` |
| Kani → | **property tests** | `pgregory.net/rapid` v1.3.0 (2026-03-30) or `testing/quick` (frozen, stdlib) | rapid has shrinking; some Go 1.27 issues reported [community-observed] | Properties: `DumpsLen(v) == len(python json.dumps(v))` on generated values (oracle corpus), `trim_to_fit` width ≤ cols, the mix percentages |
| cargo-mutants → | **avito-tech/go-mutesting** | pseudo-version `v0.0.0-20261002081621-9ce5f731e321` | Recent; master declares Go 1.27 | Weekly, non-gating, scoped to `internal/pyfmt` and `internal/statusline`; check that the mutant count is > 0 |
| (alternative) | gremlins | proxy `@latest` = **v0.5.1 (2024-05-14)**, although **v0.6.0 appears in the version list**, which suggests it is retracted or invalid. Reports of panics or zero mutants on Go 1.26 | **Inconclusive**; do not adopt now | — |
| vet | `go vet` (also `stdversion` by default in 1.27 `go test`) | toolchain | — | Every PR |

Tool pinning: put dev tools in a **separate `tools/go.mod`** (with `tool` directives) so the main
module's dependency list stays the honest runtime list ("each dependency needs a reason").
**[inferred]**

---

## Q7 — CI and release

### CI (`.github/workflows/ci.yml`)

- **Matrix:**
  - `ubuntu-24.04`, `macos-15` (arm64; this is where FMA bites), `windows-2025`, all on
    `go-version-file: go.mod`;
  - plus a `go: 1.26.x` leg on Linux;
  - pin OS labels, because `ubuntu-latest` moves to 26.04 in Nov 2026;
  - `macos-13`, `windows-2019` and macOS 14 images are retired. **[documented]**
- **setup-go:** `actions/setup-go@v7` (v7.0.0, Jul 2026). It caches modules and build output.
  Since v6 the default key hashes `go.mod`, so set `cache-dependency-path: go.sum`.
  **[documented]**
  - A long-running issue reports Windows cache restores of about 12 minutes. Measure, and use
    `cache: ${{ runner.os != 'Windows' }}` if it shows up. **[community-observed]**
- **Steps:** `gofmt -l .` (fail on output), `go vet ./...`, `go test -race ./...` (race needs cgo
  on some platforms; run `-race` on Linux/macOS only), the parity job
  (`actions/setup-python@v7` with a pinned version, `HYLO_PARITY_PYTHON=python`), golangci-lint,
  govulncheck.
- **gitleaks:**
  - the CLI is MIT; the latest is **v8.30.1** (proxy timestamp 2026-02-21; GitHub release dated
    later in some sources, so this is a minor conflict);
  - `gitleaks/gitleaks-action@v3` needs `GITLEAKS_LICENSE` **only for organization-owned
    repos**; `drbothen/hylo` is a personal account, so none is needed. **[documented]**
  - Recommendation: download the pinned binary, verify `checksums.txt`, run
    `gitleaks git --redact --log-opts="--all" .` with `fetch-depth: 0`. This matches the pre-push
    command in CLAUDE.md, needs no action license logic, and keeps working if the repo moves to
    an organization.

### Release (D12, when there is something to release)

- **GoReleaser v2.20.2** (2026-11-12). Build settings:
  - `env: [CGO_ENABLED=0]`, `flags: [-trimpath]`, `mod_timestamp: "{{ .CommitTimestamp }}"`;
  - `ldflags: -s -w -X main.version={{.Version}} -X main.date={{.CommitDate}}` (CommitDate, not
    Date, for reproducibility);
  - targets darwin/linux/windows × amd64/arm64. **[documented]**
- **Supply chain:**
  - `checksums.txt`;
  - **cosign keyless** `sign-blob` of the checksums (`id-token: write`);
  - **Syft** SBOM per archive (SPDX JSON);
  - **`actions/attest@v4`** on the archives (preferred over the `attest-build-provenance`
    wrapper), giving SLSA v1.0 Build L2. L3 needs an isolated reusable workflow.
  - Users verify with `gh attestation verify`. **[documented]**
- **Reproducibility:** pinned toolchain (go.mod `toolchain`), `-trimpath`, commit timestamps and
  `CGO_ENABLED=0`. Verify by rebuilding a tag twice and comparing hashes. Not guaranteed by the
  flags alone. **[documented]**
- **Not covered by GoReleaser OSS alone:**
  - macOS **notarization**: downloaded unsigned binaries get Gatekeeper quarantine, and signing
    needs an Apple Developer ID;
  - Windows SmartScreen reputation.
  - Both are owner decisions (O4). **[inferred]**

---

## Implications for P1 (ordered, actionable)

1. **Skeleton.** `go.mod` with `go 1.26.0` + `toolchain go1.27.4`; `cmd/hylo` with `flag`
   dispatch; `.gitattributes` (`testdata/** -text`); `tools/go.mod` for dev tools.
2. **CI skeleton** as in Q7. Include the Python setup step from the start (pinned version, O1),
   so Windows problems surface in week one.
3. **`internal/pyfmt` first** (Q2 list). Each function has a table test with
   CPython-generated expected values (committed generator script), plus fuzz targets. Include the
   FMA rule as a code-review checklist item and a lint comment convention (`// pyfmt: no-fuse`).
4. **Harness:**
   - `internal/statusline/testdata/pyhooks/sitecustomize.py` (clock, UTF-8, LF);
   - case runner with a temp HOME/USERPROFILE, httptest VM, runtime-created fake `.git`, the
     `proc_start` pre-seed, and multi-step sequences;
   - Tier A (live) and Tier B (goldens, `-update` writes **Python** output).
5. **Determinism seams in Go:** `Render(stdin []byte, env Env) []byte`, where
   `Env{Now, HTTP, CacheDir, Getenv, ProcStart}`. One clock read is acceptable. The binary
   honors `HYLO_TEST_NOW`.
6. **Port in the RESUME order.** Write each widget's review-rule table test alongside it. Keep the
   `errDegraded` contract (P27).
7. **Transcript parser:**
   - `SplitLinesBytes`, `utf8.Valid` skip, `UseNumber`, `DumpsLen`;
   - the 524,288-byte read cap with line completion;
   - the id window (last 256) and the cache schema **identical** to legacy (`mixv6` keys) for the
     swap test.
8. **Window age last:** the x/sys probes, whole-second truncation, `.exe` stripping, 6-level
   walk, cached in the session file under the legacy key.
9. **Tier C differential fuzz** (nightly) before declaring P1 done. Exit when Tier A and B are
   green on all three OSes, every review rule has a table test, and Tier C has run clean for N
   nights (owner to pick N).

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| FMA fusion changes truecolor bytes or a threshold on arm64 only | Medium | `float64()` conversions at L147/L558-equivalents; macos-15 arm64 in the gating matrix |
| Python version drift changes reference output (3.12 vs 3.15 differ on UTF-8 default; `fromisoformat` is permissive from 3.11) | Medium | Pin setup-python to the owner's production minor version; `PYTHONUTF8=1`; Tier B goldens catch drift |
| Hidden Python exception paths (P27) not mirrored | High initially | Tier C differential fuzz; `errDegraded` design |
| Go 1.27 json-on-v2 engine changes edge decoding (invalid UTF-8, duplicates) relative to 1.26 | Low–medium | Explicit `utf8.Valid` pre-check; CI on 1.26.x and 1.27.x |
| Windows sharing violations on cache rename under concurrent refreshes | Medium (Windows only) | Swallow plus short retry; never delete the destination first |
| Naive (offset-less) timestamps: local-time dependence; Go ignores `TZ` on Windows | Low (CC emits `Z`) | Inject `*time.Location`; keep naive-timestamp cases Linux/macOS-only with `TZ=UTC` |
| Gitleaks/action or runner image changes break CI | Low | Pinned binary + checksum; pinned OS labels |
| Perplexity-sourced dates not re-verified (runner image Python versions, gremlins study, Windows cache issue) | — | Flagged as [community-observed]; re-check when wiring CI |

---

## Open questions for the owner

- **O1.** Which Python minor version runs the production prototype (`python3 --version` on the
  Mac)? The parity job pins that version.
- **O2.** For P27-class malformed inputs (non-string `text`, NaN metrics), should Go reproduce
  `statusline degraded` byte-for-byte (strict D4), or may it render better output and list the
  cases as documented deviations? Recommendation: strict until cutover.
- **O3.** Windows ⌂: the prototype never shows it on Windows because there is no `ps`. Go can.
  Is this an allowed addition during parity? Recommendation: yes; the harness pins it through the
  cache seed, so parity still holds.
- **O4.** Releases: is macOS notarization (Apple Developer ID) in scope for D12, or do we ship
  unsigned binaries plus cosign/attestations and document `xattr -d com.apple.quarantine`?
- **O5.** Exit-criterion length for Tier C (nights of clean differential fuzz): proposal 3.

---

## Sources

Registry and primary (fetched this session):
- go.dev/dl/?mode=json (go1.27.4, go1.26.11); go.dev/doc/devel/release (dates, policy); go.dev/doc/go1.27 (json v2, macOS 13, synctest.Sleep); go.dev/doc/go1.26; go.dev/ref/spec (FMA clause)
- proxy.golang.org `@latest`: go.yaml.in/yaml/v4 v4.0.0 (2026-11-04); go.yaml.in/yaml/v3 v3.0.6 (2026-10-13); shirou/gopsutil/v4 v4.26.10; gofrs/flock v0.13.2; prometheus/client_golang v1.25.0; golang.org/x/vuln v1.9.0; goreleaser/v2 v2.20.2; zricethezav/gitleaks/v8 v8.30.1; honnef.co/go/tools v0.8.2; securego/gosec/v2 v2.30.0; golangci-lint/v2 v2.15.0; go-gremlins/gremlins v0.5.1 (`@v/list` includes v0.6.0); avito-tech/go-mutesting pseudo-version 2026-10-02; pgregory.net/rapid v1.3.0; kardianos/service v1.3.0
- pypi.org/pypi/time-machine/json (3.6.0, requires Python ≥3.11); docs.python.org/3.15/whatsnew/3.15.html (UTF-8 default)
- github.com/gitleaks/gitleaks-action README (v3; license "required for organizations, not required for user accounts"); github.com/actions/setup-go/releases (v7.0.0; v6.3.0 go.mod cache key)

Via Perplexity deep research (cited URLs, not individually re-fetched):
- CPython: Objects/floatobject.c (float_divmod), Python/pystrtod.c and dtoa.c (repr rules), Lib/json/__init__.py (bytes detect_encoding, surrogatepass), Modules/_json.c; docs.python.org json, functions (round), os.path (expanduser), io, cmdline (PYTHONUTF8/PYTHONIOENCODING), site
- pkg.go.dev: encoding/json, strconv, math, builtin, os (UserCacheDir/UserConfigDir/Rename), testing/synctest; github.com/golang/go/issues/32088; go.dev/src/cmd/compile/internal/ssa/_gen/ARM64.rules
- man7 proc_pid_stat(5); x/sys unix/windows docs; github.com/tklauser/ps; github.com/mitchellh/go-ps (archived); github.com/kardianos/service v1.3.0 source
- github.com/yaml/go-yaml; github.com/go-yaml/yaml (archived); github.com/goccy/go-yaml releases; prometheus.io exposition formats; github.com/VictoriaMetrics/metrics
- golangci-lint.run changelog; staticcheck.dev/changes; github.com/securego/gosec releases; semgrep.dev rules license; github.com/opengrep/opengrep-rules; go.dev/doc/security/fuzz; github.com/gomutants/gomutants docs/performance.md (gremlins Go 1.26 study)
- goreleaser.com (builds, sign, sbom, reproducible-builds blog); github.com/actions/attest; docs.github.com artifact attestations / SLSA; github.com/actions/runner-images (image readmes Nov 2026); github.com/actions/setup-go/issues/495; git-scm.com gitattributes; github.com/rogpeppe/go-internal (testscript v1.16.0); time-machine.readthedocs.io; github.com/wolfcw/libfaketime

---

## Research Methods

| Tool | Queries | Purpose |
|---|---|---|
| **Perplexity perplexity_research (PRIMARY)** | 7 | Go toolchain status; YAML and Prometheus libraries; hardening tools; CI/release (setup-go, gitleaks, GoReleaser, runners); Python→Go numeric/JSON/IO semantics; cross-platform process/rename/lock/dirs/services; parity-harness techniques (sitecustomize, time-machine, libfaketime, goldens) |
| Perplexity perplexity_reason | 0 | — |
| Perplexity perplexity_search | 0 | — |
| Perplexity perplexity_ask | 0 | — |
| Context7 | 0 | Not needed: questions were about versions and maintenance status, which were verified directly against proxy.golang.org/PyPI (the authoritative registries), and about semantics, which came from CPython/Go docs and source |
| Tavily (all) | 0 | Cross-validation done with WebFetch against primary registries instead |
| WebFetch | 23 | go.dev (dl JSON, release history, go1.27 notes); 16 proxy.golang.org `@latest`/`@v/list` lookups; PyPI time-machine; Python 3.15 what's new; gitleaks-action README; setup-go releases |
| WebSearch | 0 | — |
| Local reads | 6 | PLAN.md, RESUME.md, legacy/dgx_statusline.py (scanned in full via Grep + Read), legacy/dgx_ledger_exporter.py (output section) |
| Training data | 4 areas | (1) CPython `repr` switch thresholds and `json.dumps` escape set: corroborated by Perplexity-cited source; (2) fusable-expression identification in L147/L558: my reading of the code; (3) Go ignoring `TZ` on Windows: **not re-verified**; (4) git not tracking a nested `.git` directory: standard behavior, not re-verified |

**Total MCP tool calls:** 7 (Perplexity) + 23 WebFetch verifications.
**Training data reliance:** low–medium. Every version and date is registry-verified; semantic
claims rest on Perplexity-cited CPython/Go sources, and the legacy line mapping comes from
reading the file directly. The items in the Training data row are marked [inferred] in the body.
