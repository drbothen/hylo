# Pass 5 deepening, round 2: conventions, env-var inventory, determinism inventory, pitfall register (hylo-legacy)

- **Source:** `$HOME/Dev/hylo/legacy/` (11 files, 3,181 lines, recounted with `wc -l`; read-only). Re-read this round: `auto_continue.py` (all 275),
  `claude-dgx` (all 185), `dgx_proxy.py:50-130,153,205-216,238,273,296,515-545,555-566,618,632,709`, `dgx_ledger_exporter.py:1-70,110-160,212-236,395-414`,
  `dgx_statusline.py:140-150,165-171,201,217,231,243,268-300,304,322,362-410,420-428,450-462,499,525-561,660-690,825-831,853,859,975-990,1017,1186-1188,1215`,
  `tools/backfill_cost_history.py:30-121`, `dgx_preflight.py` (all), both plists, `dgx-proxy-coordinator.sh:1-3`. CPython stdlib read via `inspect`:
  3.9.6 `http/server.py` `HTTPServer.server_bind`, `socket.getfqdn`; 3.11.7 `urllib/request.py` `getproxies_environment`, `getproxies`.
- **Inputs read:** pass-5 broad sweep, pass-5 deep r1 (all), pass-4 deep r1 §C (D15 map) and **r2** §D (key harmonization, appeared during this round),
  pass-0 deep r3 §2.5-2.6 and C11-C14, pass-1 deep r2 §B (Kev proxy path) and **r3** V1/V10/V19, pass-2 r1 §6.1-6.3 (CONFIG map), r2 §6.3/§6.8, r7 §1.4,
  r9 (G-2), `docs/PLAN.md` l.42, 56, 105-108, 130, D14-D16. Siblings were read only, never edited. `CLAUDE.local.md` was not read.
- **Method:** isolated scripts in `scratchpad/p5r2/` that copy legacy expressions, plus one **copy** of `auto_continue.py` run with `HOME` redirected to
  a scratch directory against a loopback stub (`127.0.0.1`, ephemeral port, `no_proxy=*`). Interpreters: `/opt/homebrew/anaconda3/bin/python3` 3.11.7
  and `/usr/bin/python3` 3.9.6, `/bin/zsh` 5.9. Go: `go1.26.5 darwin/arm64`, `GOFLAGS=-mod=mod GOTOOLCHAIN=local`; amd64 builds cross-compiled
  (GOAMD64=v1 run under Rosetta; v3 assembly only, it cannot run on this host). Nothing from `legacy/` was executed in place. No proxy ran. Nothing
  left the host. One disclosure: the exporter port-0 probe (bind host changed to `127.0.0.1`) triggers the stdlib's `socket.getfqdn("127.0.0.1")`,
  that is, a reverse lookup through the local system resolver.
- **Numbering:** retractions **none** (CONV-ABS-65..68 unused). New owner items **OD-74..OD-76** (OD-77 unused). New IDs: `ENV-I18..I19`, `DET-53`,
  `CV-19`, `PR-22`, tag `PT-DUR`. Proposed hook-catalogue rows `H-10`, `H-11` (pass 2 owns that catalogue).
- **Line cites:** `SL` = `dgx_statusline.py`, `PX` = `dgx_proxy.py`, `HK` = `auto_continue.py`, `EX` = `dgx_ledger_exporter.py`, `BF` =
  `tools/backfill_cost_history.py`, `LN` = `claude-dgx`, `CO` = `dgx-proxy-coordinator.sh`, `PF` = `dgx_preflight.py`. Results marked **[exec]** were
  executed this round.

---

## 0. Audit of round 1 against the 5 hallucination classes

| Class | Checked | Result |
|---|---|---|
| 1 Over-extrapolated token lists | env-bool predicates (ENV-12/13/26/27/32/35-39) re-read against `LN:60-182`, `SL:76-77`, `HK:217,228`; JSON styles J1-J4 | none found |
| 2 Miscounted enumerations | 27 Python names (grep + regex count = **27**); 22 launcher-read names (token census of `claude-dgx`, comments stripped: 16 `DGX_*` + `ANTHROPIC_CUSTOM_HEADERS`, `ARGS`, `HOME`, `PWD`, `ROUTER_PORT`, `TMPDIR`); 6 overlaps; coordinator adds only `TMPDIR`. 33 keyed + 10 unkeyed = 43. 17 implicit **IDs** = 21 env names + the OS proxy source | all counts **confirmed** |
| 3 Fabricated names | every function/variable cited in the sampled rows exists | none. Two wording slips (DET-09, PR-01) refined in §B |
| 4 Same-basename conflation | `dgx_proxy.py` addon vs trust CLI (same file, two entry points) kept apart | none |
| 5 Inflated metrics | LOC 3,181 recounted; FMA counts re-derived with real Go (§A.2) | **confirmed** exactly |

No round-1 claim is false. **No retraction.** Several claims were incomplete; §B lists each with the fresh evidence.

---

## A. Round 1's Remaining Gaps 1-6, settled

### A.1 Gap 1a: Go DST handling of naive local times versus Python **[exec]**

Python side (`dst_py.py`, copies of `EX:125,145` `strptime(...).timestamp()`, `SL:983` `fromisoformat(...).timestamp()`, `SL:286`
`mktime(strptime(lstart))`), America/Chicago, identical on 3.9.6 and 3.11.7:

| Wall time | `strptime`/`fromisoformat` | macOS `mktime` (SL:286) | Go `time.Date` / `ParseInLocation` |
|---|---|---|---|
| 2026-11-01 01:30:00 (repeated hour) | 1793514600 (first, CDT) | 1793514600 | 1793514600 (match) |
| 2026-11-01 01:59:59 (repeated hour) | 1793516399 (first) | **1793519999 (second, CST)** | 1793516399 (match) |
| 2026-03-08 02:00:00 (gap) | 1772956800 (= 03:00 CDT) | 1772956800 | **1772953200 (= 01:00 CST), −3600** |
| 2026-03-08 02:30:00 (gap) | 1772958600 (= 03:30 CDT) | 1772958600 | **1772955000 (= 01:30 CST), −3600** |

Grid test (`dst_grid_py.py` → `gomktime/main.go`): 3,096 naive times around 2026 transitions in 9 zones (America/Chicago, Europe/Berlin,
Australia/Sydney, Australia/Lord_Howe, America/St_Johns, Pacific/Chatham, America/Sao_Paulo, Asia/Tehran, UTC); Python 3.9.6 and 3.11.7 outputs
byte-identical.

| Go implementation | Mismatches vs Python | Where |
|---|---|---|
| `time.Date(..., loc)` (same as `ParseInLocation`) | **46 / 3,096** | **west-of-UTC zones: the spring gap** (Chicago 8, St_Johns 8, all −3600); **east-of-UTC zones: the repeated hour** picks the second occurrence (Berlin 8, Sydney 8, Chatham 9 at +3600; Lord_Howe 5 at +1800) |
| Port of CPython `datetime._mktime` (fold = 0), local time read through `time.Unix(u,0).In(loc)` | **0 / 3,096** | — |

Consequences:
- **Remedy change (PR-14, DET-19, DET-21):** `pytime.ParseNaive(loc)` must implement CPython's `_mktime` search (offset probe, fold-0 "earlier"
  candidate within 24 h, `max(u1, u2)` in a gap), not call `time.Date`/`ParseInLocation`. Go's own doc says the ambiguous choice "is not guaranteed";
  its actual choice depends on the sign of the zone offset. For the owner's US zone the repeated hour already matches, so recorded US ledgers would
  not have caught this. A European user's ledger contains the repeated hour twice a year and would diverge by 3,600 s in `last_*` gauges.
- **Leniency delta [exec]:** Python `strptime` with `%Y-%m-%dT%H:%M:%S` accepts single-digit fields **and a lowercase `t`** (`2026-11-14t08:05:09`,
  regex is case-insensitive). Go layout `2006-1-2T15:4:5` accepts single digits but rejects `t`. Both reject `Z`, fractions, leading/trailing space,
  `24:00:00`, `2026-02-29`. A hand-written parser is required (the ledger writer always emits `T`, so this is edge-only).
- **New legacy quirk, DET-20 (SL:286) [exec]:** macOS libc `mktime` with `tm_isdst = -1` (what `time.strptime` returns) resolves the repeated hour
  **inconsistently**: first occurrence through 01:45:18, second occurrence from **01:45:19** (America/Chicago 2026-11-01; same on 3.9.6 and 3.11.7;
  not call-order dependent). The ⌂ window age is therefore wrong by 3,600 s when Claude Code was started in the last ~15 minutes of the repeated hour.
  It follows neither Python's fold rule nor Go's. hylo's native `platform.ProcessStart` returns the true start, so the harness (which seeds
  `proc_start`) never sees it. Recorded as a deviation candidate, OD-76.

### A.2 Gap 1b: does Go on darwin/arm64 fuse the backfill cost expression? **[exec]**

Inputs: round 1's generator and seed (20,000 sessions, 2,047,586 messages), written as binary by Python with CPython's per-message and per-session
results; `gofma/main.go` recomputes them and compares bits.

| Go form of `BF:75-76` | arm64 instructions | Message bit diffs | Session-sum bit diffs | `round(usd, 4)` diffs | JSON text diffs | `usd < MIN_USD` flips |
|---|---|---|---|---|---|---|
| naive `(float64(a)*pi + float64(o)*po + … + float64(r)*pr) / 1e6` | 1 `FMULD` + **4 `FMADDD`** | **200,751** | **1,439** | 0 | 0 | 0 |
| guarded `float64(float64(a)*pi) + float64(float64(o)*po) + …` | 5 `FMULD` + 4 `FADDD` | **0** | **0** | 0 | 0 | 0 |
| explicit `math.FMA` chain (round 1's emulation order) | 4 `FMADDD` | 200,751 | 1,439 | 0 | 0 | 0 |

- Round 1's emulation predicted the compiler's fusion order exactly (identical counts). Max absolute session difference 2.84e-14.
- **Fix confirmed:** wrap each product in an explicit `float64(…)` (Go spec: an explicit conversion rounds and prevents fusion).
- Other float sites, naive Go transliterations (`gofma2/main.go`), arm64: **fused** = colorsys core (2 `FMSUBD` + 1 `FNMSUBD`; `SL:146-147` via
  `colorsys.hsv_to_rgb`) and the ⌂ gate `SL:558-559` (`FNMSUBD`, fused **across two statements**); **not fused** = `SL:674-675` sparkline index (the
  `min` clamp separates product and add, with `math.Min` or with an `if`) and `SL:682` fade (`0.45*i/den`, a quotient). PR-15's site list is complete.
- **Target dependence (new):** amd64 `GOAMD64=v1` (Go's default) does **not** fuse the naive form; `GOAMD64=v3` does (4 `VFMADD231SD`). Linux and
  Windows CI on default amd64 would not catch a missing guard; darwin/arm64 CI does.

### A.3 Gap 2: hook crash paths for `DGX_KEV_URL` and `DGX_KEV_TIMEOUT`, end to end **[exec]**

Harness `kev_e2e.py`: a copy of the hook, `HOME` = fresh scratch dir, loopback stub Kev answering `noul = 0.9`, stdin message
`"Now let me run the tests"` (reaches the Kev path; heuristic = continue). 3.11.7.

| Case | Exit | Stub hits | Stdout | Log line | Raised at |
|---|---|---|---|---|---|
| baseline | 0 | 3 | empty | `[kev-allow] … p_done=0.900 fake=False (0.00s)` | — |
| `DGX_KEV_URL=""` | **1** | 0 | empty | **none** | `ValueError: unknown url type: ''` at copy line 110 (`HK:110`) |
| `DGX_KEV_URL=kev.invalid/v1/systemone` (no `scheme:` token) | **1** | 0 | empty | none | `ValueError` at `HK:110` |
| `DGX_KEV_URL=127.0.0.1:<port>/v1/systemone` | 0 | 0 | continue JSON | `[heuristic-continue] kev=unreachable` | `URLError` inside the `try` (caught) |
| `DGX_KEV_TIMEOUT=inf` / `1e400` | **1** | 0 | empty | none | `OverflowError: timestamp out of range for platform time_t` at `HK:113` (innermost `socket.py:833 create_connection`) |
| `DGX_KEV_TIMEOUT=1e10` | **1** | 0 | empty | none | same `OverflowError` |
| `DGX_KEV_TIMEOUT=9223372036` | 0 | 3 | empty | kev-allow | — |
| `DGX_KEV_TIMEOUT=9223372037` | **1** | 0 | empty | none | same `OverflowError` |
| `DGX_KEV_TIMEOUT=-1` / `nan` | 0 | 0 | continue JSON | heuristic-continue, `kev=unreachable` | `ValueError` from `settimeout`, caught (`HK:119`) |
| `DGX_KEV_TIMEOUT=0` | 0 | 0 | continue JSON | heuristic-continue, `kev=unreachable` | non-blocking connect fails, caught (**executed**; round 1 had inferred it) |
| `DGX_KEV_TIMEOUT=""` | 1 | 0 | empty | none | import, `HK:34` (H-07) |
| `DGX_KEV_API_KEY="abc\r\nX-Evil: 1"` | 0 | 0 | continue JSON | heuristic-continue | `http.client` header `ValueError`, caught (stdlib inference of round 1 now executed) |

- **Refinement of ENV-22:** the crash threshold is `settimeout`'s limit, measured at **9,223,372,036.854775 s** (2^63 ns) on both interpreters, not
  only `inf`. Any larger value crashes the hook on every Kev-path stop.
- Proposed hook-catalogue rows (pass-2 r2 §6.3 numbering, after H-09): **H-10** `Request()`-invalid `DGX_KEV_URL` (empty, or no `scheme:` token
  before the first `/`) raises at `HK:110`, outside the `try`. **H-11** `DGX_KEV_TIMEOUT` > 9,223,372,036.854775 (incl. `inf`) raises
  `OverflowError` inside `urlopen` (`HK:113`), not in `HK:119`'s tuple. Both: exit 1, empty stdout, **no log line**, on the first Kev call.
- **Go side [exec], changes the remedy** (`godur/`, `gohttpto/`): a naive port `time.Duration(f * 1e9)` gives, for `inf` and `1e10`,
  `MaxInt64` on arm64 but **`MinInt64` on amd64**, and for `nan` **0** on arm64 but `MinInt64` on amd64 (out-of-range float→int conversion is
  implementation-defined in the Go spec). `http.Client{Timeout: d}` treats **every `d ≤ 0` as "no timeout"**: against a 300 ms stub, `0`, `-1s` and
  `MinInt64` all waited and succeeded. So legacy "0 / negative / NaN ⇒ Kev never contacted" becomes "Kev with no deadline" in a naive port (the hook
  could hang until Claude Code's 30 s hook timeout), and the result differs between macOS/arm64 and Linux/Windows/amd64. New pitfall PR-22; owner item OD-75.
- Clock reads along these paths, measured with a counting shim (`hooks_count/`): **7** for three successful Kev calls (2 per call + 1 log
  `strftime`), **4** for three failed calls (1 per call + 1 log). No stdlib code in the `urlopen` path reads `time.time()`. Early stop exercised
  end to end with the corrected shim in mode 2: `HYLO_TEST_CLOCK_SEQ=0,2,10,12,100` → **2** stub hits, log `(2.00s)`; `0,1,10,11,20,21,100` → 3
  hits, `(1.00s)`. This confirms CONV-ABS-48 and OD-58 (b).

### A.4 Gap 3: exporter `DGX_LEDGER_EXPORTER_PORT=0` **[exec]**

Copy of `EX:25` and `EX:411-414` on 3.9.6 (bind host changed to `127.0.0.1`):

| Value | Startup print (`EX:413`) | Bind result |
|---|---|---|
| `0`, `00`, `+0` | `serving :0` | an ephemeral port (53033, 53036, 53038 in three runs): the log names port 0, so the port cannot be found from the log, and no scrape config can target it |
| `-1`, `65536` | `serving :-1` / `:65536` | `OverflowError: bind(): port must be 0-65535.` after the print (round 1 confirmed) |
| `" 9210 "`, `9_210` | `serving :9210` | 9210 (Python `int()` grammar) |

**New finding, DET-53:** `HTTPServer.server_bind` (3.9.6 `http/server.py`) calls `socket.getfqdn(host)`; for the legacy host `"0.0.0.0"` that is
`gethostname()` followed by `gethostbyaddr(hostname)`, i.e. a **resolver lookup at every exporter start**. It is output-neutral (`server_name` is
not used in `/metrics` responses) but can delay startup when the resolver is slow (for example at boot under launchd). Source-derived; latency not
measured (no network allowed). Go's `net/http` does no such lookup: an output-neutral deviation. Also: `HTTPServer.allow_reuse_address = 1`
(`SO_REUSEADDR`). Go sets `SO_REUSEADDR` on Unix listeners too.

### A.5 Gap 4: mitmproxy 12.3.1 environment reads (closed by cross-reference)

Pass-1 r3 V1 (package-wide search of mitmproxy 12.3.1) and pass-2 r7 §1.4: the only environment reads are `SSLKEYLOGFILE`/`MITMPROXY_SSLKEYLOGFILE`
(m/`net/tls:147-149`), `MITMPROXY_CASE_SENSITIVE_FILTERS`, and console-only `EDITOR`/`PAGER`. No `MITMPROXY_*` option overrides, no proxy
variables. Added as **ENV-I19** (inert in legacy: no filter expressions are configured; `mitmdump` never opens an editor or pager). This venv was
not opened by this round; the result is adopted, not re-verified.

### A.6 Gap 5: Windows time-zone pinning (narrowed, not closed)

The Go side no longer depends on the OS zone once `ParseNaive` takes an injected `*time.Location` (A.1). Two Go-side facts for the harness design
(from the `time` package docs; not executed on Windows): `time.LoadLocation` on Windows has no system zoneinfo, so the binary must import
`time/tzdata` (or set `ZONEINFO`); and `ZONEINFO` is an implicit Go input. Recommendation: Windows CI runs the naive-time cases as **Go table tests
against CPython-generated goldens** (committed generator, run on macOS/Linux); the live Python oracle is not run on Windows for DET-19..23.

### A.7 Gap 6: owner decisions

OD-58..OD-61 stay pending with their round-1 recommendations. OD-59 gains the A.3 evidence (see OD-75). OD-01 and OD-05 are carried; OD-74 below
asks the owner to approve the harmonized key table built on OD-01.

---

## B. Round-2 audit of round 1's new claims (fresh evidence)

| # | Round-1 claim | Fresh evidence (this round) | Verdict |
|---|---|---|---|
| B1 | ENV-43 `ARGS` leak | `args_r2.zsh` (copy of `LN:6,128-133,182-185` with `printf` only): `env -i ARGS='--resume x' zsh -f` → `claude`, `--resume x`, `--model`, `sonnet`; with `DGX_REMOTE=1` and a user arg: `claude -p --model sonnet --remote-control hello`. The scalar stays **one** argument (no word split). All other launcher variables are assigned before use (token census) | **Confirmed** |
| B1+ | (new) | Run as an executable (shebang `#!/bin/zsh`, no `-f`), zsh sources **`$ZDOTDIR/.zshenv`** (default `$HOME/.zshenv`) first: a scratch `.zshenv` containing `ARGS=(--from-zshenv)` produced `claude --from-zshenv --model sonnet`; with `ZDOTDIR` set, that directory's `.zshenv` wins. `/etc/zshenv` does not exist on this macOS. `dgx-proxy-coordinator.sh` has the same shebang | **New implicit input ENV-I18** |
| B2 | 43 explicit + 17 implicit | §0 class-2 recount. Implicit list refined: urllib's environment scan takes **every** variable whose lower-cased name ends in `_proxy` (3.11.7 `getproxies_environment`, printed via `inspect`): `ALL_PROXY=socks5://…` alone makes `getproxies()` return `{'all': …}`, which **suppresses the macOS system-proxy fallback**, while `ProxyHandler` gets no `http_open` (so the Kev call goes direct). A lowercase empty value cancels the uppercase one. With a clean env this host's system settings return `{}` | **Confirmed**; ENV-I12..I15 refined (any `*_proxy`) |
| B3 | 9 import-time crashes | Each `float()`/`int()` re-read at `SL:74-75`, `HK:33-36`, `EX:24-25`; `DGX_UPSTREAM` via `_router = DGXRouter()` at `PX:521` (after the `note` at `PX:518`, so the decision log still gets "addon module loaded"). Executed: `DGX_KEV_TIMEOUT=""` → import crash at `HK:34`. `urlparse` port cases **[exec]**: `:abc`, `:99999` raise on 3.9.6 and 3.11.7; **`:+80`, `: 80`, non-ASCII digits raise on 3.11.7 but parse on 3.9.6** (port grammar is version-dependent). `PX`/`PF` run on the 3.12.10 venv (strict, inferred from 3.11.7) and the trust CLI on 3.11.7 | **Confirmed**; PR-18 refined |
| B4 | 2 per-call crashes | §A.3 executed end to end | **Confirmed**, `DGX_KEV_TIMEOUT` threshold widened to > 9,223,372,036.854775 s |
| B5 | CONV-ABS-47 (research shim does not freeze `strftime`) | Copies of `PX:60`, `PX:72`, `HK:197`, `PX:632`-style under `HYLO_TEST_NOW=1e9`, `TZ=UTC`: research shim (patches `time.time` only) → `time.time()` = `1000000000.0` but all four stamps show the real wall clock (`2026-11-14T08:47:45`); corrected shim → `2001-09-09T01:46:40` everywhere, on 3.11.7 and 3.9.6. With `-I` the shim is ignored (stated in round 1) | **Confirmed** |
| B6 | CONV-ABS-48 (frozen clock hides the Kev early stop) | §A.3 clock-read counts and early-stop runs | **Confirmed**, now exercised end to end |
| B7 | CONV-ABS-49 (cwd is an input for relative project dirs) | `SL:373` `os.path.abspath(directory or os.getcwd())`; `SL:405` key hashes the raw string; `SL:452-453` passes the stdin string unchanged | **Confirmed** |
| B8 | 52 determinism rows (sample 25) | Line text verified for DET-01 (`SL:231`), 02 (`:243`), 03 (`:304`), 04 (`:322`), 05 (`:408`), 06 (`:499`), 07 (`:558`), 08 (`:825-826`), 09 (`PX:128,238,273`), 10 (`PX:296`), 11 (`PX:529-536`), 13 (`HK:111,118,133`), 14 (`BF:95`), 15 (`PX:60`), 16 (`PX:72`), 17 (`HK:197`), 18 (`PX:632,709`), 19 (`SL:983`), 20 (`SL:286`), 21 (`EX:125,145`), 22 (`BF:39`), 24 (no `monotonic`/`perf_counter`: grep 0), 25 (`SL:165-171`), 31 (`SL:278-286`), 32 (`PX:518`), 35 (`SL:217,405,1017,1215`), 42 (`BF:91,97,98`), 47 (`SL:201`, `BF:113`, `PX:618`), 48 (no `random`/`uuid`/`secrets`: grep 0), 49 (`SL:1186`) | **Confirmed**, two refinements: DET-09's second site reads **`_dgx_t0`** (`PX:273`; set at `PX:153` to `_t0`), not `_t0`; DET-20 gains the libc quirk (§A.1) |
| B9 | 21 pitfall rows (sample 13) | PR-01 (`SL:426,675,1171,234`, `BF:108`, `PX:213`), PR-02 (`HK:250,256`; `EX:298,333,353,364,370,374,398`), PR-03 (`SL:525-529,546,548,560-561,826,829-831,859`), PR-04 (`SL:146,671`), PR-05 (`SL:853`), PR-10 (**[exec]** `COLUMNS` of 4,301 digits → 0 on 3.11.7, a huge int on 3.9.6; 4,301-digit JSON int → `ValueError` on 3.11.7, parsed on 3.9.6), PR-11 (all `HK` cites), PR-12 (`HK:69,177`, `EX:116,216`, `BF:44`), PR-13 (`HK:24-28,177,179-180,184,236`), PR-15 (§A.2), PR-16 (`HK:197-199`), PR-18 (B3), PR-19 (`BF:81` dict order `dgx` first) | **Confirmed**. Wording: PR-01's `PX:213` `bridge_ws_close` is code-live but **0 events in the production ledger** (pass-2 r9 G-2), not "never fires" |
| B10 | `PYTHONHASHSEED` negative; implicit `PYTHON*` set | Hook copy run **without** `-I` under `PYTHONWARNINGS=error` + `PYTHONDONTWRITEBYTECODE=1`: identical results for baseline, unreachable and `timeout=0` | **Confirmed** for the hook; class note added: the harness unsets **every** `PYTHON*` except its own `PYTHONPATH` |
| B11 | `opus_verdict` env write | `HK:153` `dict(os.environ, DGX_AUTOCONTINUE="0")` is in `opus_verdict` (`HK:141-166`), which nothing calls | a dead env **write**, no row needed (already dead in pass 0/3) |

Verdict summary: **14 claims confirmed, 0 retracted, 6 refined** (ENV-22 threshold, ENV-I12..I15 `*_proxy` set, PR-18 version split, DET-09
wording, DET-20 libc quirk, PR-01 wording), **3 new inputs/sources** (ENV-I18 `.zshenv`/`ZDOTDIR`, ENV-I19 mitmproxy reads, DET-53 resolver lookup).

### B.1 Go-side parse grammar deltas (PR-18 detail) **[exec]**

`strconv.ParseFloat` / `strconv.Atoi` vs Python `float()` / `int()` (`goparse/`, `python3 -I`):

| Input | Python `float` | Go `ParseFloat` | Python `int` | Go `Atoi` |
|---|---|---|---|---|
| `" 2"`, `"2 "` | 2.0 | error | 2 | error |
| `"٢"` (Arabic-Indic 2) | 2.0 | error | 2 | error |
| `"4_0"` | 40.0 | 40 | 40 | **error** |
| `"0x1p3"` | **error** | **8** | error | error |
| `"+nan"` | nan | **error** | error | error |
| `"1e400"` | inf | error **with** `+Inf` | — | — |
| `"1__0"`, `"_1"`, `"1_"` | error | error | error | error |
| `"-iNF"`, `"infinity"`, `"1e1_0"`, `".5"`, `"5."` | accepted | accepted (same values) | — | — |

`pyfmt.ParseFloat`/`ParseInt` (round-1 remedy) are required; `strconv` is not a drop-in, in either direction.

---

## C. Key-name harmonization with pass 4 (OD-01 scheme)

### C.1 Rules applied

1. Dotted lower-snake keys; first segment = component (`routing`, `backend`, `paths`, `statusline`, `hook`, `exporter`, `run`, `attribution`, `ca`,
   `proxy`, `ledger`, `cost`, `service`, `prices`).
2. **Every filesystem location lives under `paths.*`**; behavior settings stay in the component (`paths.hook_log` + `hook.log.tail_chars`).
3. Secrets by file: `*_file` keys (PLAN l.105-106). An env var that carries a secret **value** is a deprecated alias only.
4. Unit suffix names the legacy unit (`_s`, `_ms`, `_bytes`, `_chars`, `_pct`, `_w`), as in pass-4 r2 §D.
5. **Toggles:** a feature that has its own settings is a table with an `.enabled` leaf (`statusline.git.enabled` + `statusline.git.ttl_s`,
   `run.statusline.enabled` + `run.statusline.refresh_interval_s`); a plain flag with no settings stays a bare leaf (`run.sandbox`, `run.remote_control`).
6. OD-01: `HYLO_` + the dotted key in upper snake case. Because leaf names contain `_`, the env name is **generated from the schema's key registry and
   looked up**, never parsed back into a key. A mechanical check over all 134 keys parsed from P2r1 §6.1-6.2, P5r1 §A.2 and P4r1 §C found **0 HYLO name
   collisions and 0 leaf-vs-table conflicts**.
7. `DGX_*` aliases keep the legacy parse and predicate (OD-59 (b)); `HYLO_*` values are typed and validated (OD-05 for booleans).

### C.2 Disagreements found and resolved

| # | Sources | Disagreement | Resolution |
|---|---|---|---|
| K-1 | P2r1/P5r1 `run.preflight` (bool); P4r1 `doctor.preflight_timeout_s`; P4r2 H-3 `run.preflight` + `run.preflight_timeout_s` | namespace (`doctor` vs `run`) settled by P4r2; shape differs from rule 5 (the preflight now has a setting) | **`run.preflight.enabled`** (`HYLO_RUN_PREFLIGHT_ENABLED`, `DGX_SKIP_PREFLIGHT=1` → false) and **`run.preflight.timeout_s`** (`HYLO_RUN_PREFLIGHT_TIMEOUT_S`, 4). The timeout's HYLO name is identical to P4r2's; only the toggle's name changes. `hylo doctor` reads the same keys. Carried to pass 4 as a one-line change; OD-74 |
| K-2 | P2r1 §6.1 `DGX_PROFILE` → `profiles.<name>`; P5r1 "—" | a profile file is **selected**, not a value | no D15 key and no alias (the legacy value is a zsh file to `source`, not translatable). Successor: config-file `profiles.<name>` sections selected by `hylo run --profile <name>`. Whether an env selector `HYLO_PROFILE` exists is a meta-setting outside the key registry (OD-74 (c)) |
| K-3 | P4r1 T-066/067 "also needs a path key" (unnamed) | missing name | **`paths.failed_capture_dir`** (`HYLO_PATHS_FAILED_CAPTURE_DIR`, default `~/dgx-llm-obs/`, `PX:289`); no `DGX_*` alias exists |
| K-4 | P2r1 `exporter.bind` default `0.0.0.0` (legacy); P4r1/r2 loopback (HY-BIND-5) | default, not name | name agreed (`HYLO_EXPORTER_BIND`, no alias). Default governed by OD-24/OD-27 rulings (LAN exposure accepted until cutover); not reopened here |
| K-5 | `DGX_KEV_API_KEY` (value) vs `hook.kev.api_key_file` | value vs file | file key only (`HYLO_HOOK_KEV_API_KEY_FILE`); `DGX_KEV_API_KEY` stays a deprecated value alias that wins over the file (legacy order `HK:97-102`); no `HYLO_` value variable |
| K-6 | `TMPDIR` → `paths.proxy_log_dir` | is `TMPDIR` an alias? | no: it is the **default source** (`os.TempDir()` reads `TMPDIR` on Unix, `TMP`/`TEMP` on Windows). `HYLO_PATHS_PROXY_LOG_DIR` overrides |
| K-7 | `LOCAL_MODEL_PREFIXES` (unprefixed legacy name, three different defaults) | list type in an env var | `routing.local_model_prefixes`, `HYLO_ROUTING_LOCAL_MODEL_PREFIXES` = comma-separated, Python-`strip()`ped, empty items dropped (legacy encoding). One default (`claude-sonnet`) replaces the status line's `""` (P2r1 parity note: the harness sets it explicitly) |
| K-8 | timeout keys (`hook.kev.timeout_s`, `statusline.telemetry.timeout_s`, `run.preflight.timeout_s`, `backend.connect_timeout_s`, `proxy.idle_timeout_s`) | value domain | one `config.Seconds` type: finite, > 0, ≤ 9,223,372,036.854775 s, total-deadline semantics (OD-56). Alias-path special values per OD-75 |
| K-9 | P4r2 H-2 `statusline.cost.rate_min_api_ms = {cc, other}`; P4r1 `cost.backfill.min_api_ms` | non-env | adopt P4r2 H-2 (one key). Maps have no scalar env form: per-leaf override `HYLO_STATUSLINE_COST_RATE_MIN_API_MS_OTHER` only if OD-74 (b) allows map leaves |

### C.3 The table: env var → D15 key → HYLO name

"Agree" lists the passes that already use the key: P2 = pass-2 r1 §6.1, P5 = pass-5 r1 §A.2, P4 = pass-4 r1 §C / r2 §D.

| ID | Legacy env | Alias-path parse (legacy, reproduced) | D15 key | HYLO name | Agree |
|---|---|---|---|---|---|
| ENV-01 | `LOCAL_MODEL_PREFIXES` | `split(",")`, `strip()`, drop empty | `routing.local_model_prefixes` | `HYLO_ROUTING_LOCAL_MODEL_PREFIXES` | P2 P5 |
| ENV-02 | `DGX_SERVED_MODEL` | raw; empty = no rewrite | `backend.served_model` | `HYLO_BACKEND_SERVED_MODEL` | P2 P5 |
| ENV-03 | `DGX_UPSTREAM` | `urlparse` (scheme/host/port defaults, port 0 → 80, bad port = import crash) | `backend.url` | `HYLO_BACKEND_URL` | P2 P5 |
| ENV-04 | `DGX_KEY_FILE` | literal path | `backend.api_key_file` | `HYLO_BACKEND_API_KEY_FILE` | P2 P5 |
| ENV-05 | `DGX_OBS_LEDGER` | literal path | `paths.ledger` | `HYLO_PATHS_LEDGER` | P2 P5 |
| ENV-06 | `DGX_PROXY_DECISIONS` | literal path | `paths.decision_log` | `HYLO_PATHS_DECISION_LOG` | P2 P5 |
| ENV-07 | `DGX_TRUST_STATE` | `Path(env)` | `paths.ca_state` | `HYLO_PATHS_CA_STATE` | P2 P5 |
| ENV-08 | `DGX_PROXY_RESTART_CMD` | `shell=True` | `ca.restart_command` (likely obsolete; P4 drops T-075 with it) | `HYLO_CA_RESTART_COMMAND` | P2 P5 P4 |
| ENV-09 | `DGX_SL_VM_URL` | `rstrip("/")` | `statusline.telemetry.url` | `HYLO_STATUSLINE_TELEMETRY_URL` | P2 P5 |
| ENV-10 | `DGX_SL_TTL` | Python `float()` | `statusline.telemetry.ttl_s` | `HYLO_STATUSLINE_TELEMETRY_TTL_S` | P2 P5 P4 (T-001) |
| ENV-11 | `DGX_SL_ROWS` | Python `int()` | `statusline.rows` | `HYLO_STATUSLINE_ROWS` | P2 P5 P4 (T-002) |
| ENV-12 | `DGX_SL_SPARK` | on iff `!= "0"` | `statusline.sparkline.enabled` | `HYLO_STATUSLINE_SPARKLINE_ENABLED` | P2 P5 |
| ENV-13 | `DGX_SL_GIT` | on iff `!= "0"` | `statusline.git.enabled` | `HYLO_STATUSLINE_GIT_ENABLED` | P2 P5 |
| ENV-14 | `DGX_SL_TRACE` | `TRACE_KEYS.get(v, "v")` | `statusline.sparkline.trace` | `HYLO_STATUSLINE_SPARKLINE_TRACE` | P2 P5 |
| ENV-16 | `DGX_FAKESTOP_LOG` | literal path (reader only; writer hard-coded `HK:195-196`) | `paths.hook_log` | `HYLO_PATHS_HOOK_LOG` | P2 P5 |
| ENV-17 | `DGX_SESSION_LIMIT` | Python `int()` | `exporter.session_limit` | `HYLO_EXPORTER_SESSION_LIMIT` | P2 P5 P4 (T-077) |
| ENV-18 | `DGX_LEDGER_EXPORTER_PORT` | Python `int()`; range checked at bind | `exporter.port` | `HYLO_EXPORTER_PORT` | P2 P5 P4 (T-078) |
| — | (none; `EX:414` literal) | — | `exporter.bind` | `HYLO_EXPORTER_BIND` | P2 P5 P4 (K-4) |
| ENV-19 | `DGX_KEV_URL` | raw; `Request()` at `HK:110` (H-10) | `hook.kev.url` | `HYLO_HOOK_KEV_URL` | P2 P5 |
| ENV-20 | `DGX_KEV_MODEL` | raw; effective default = launcher's pinned id | `hook.kev.model` | `HYLO_HOOK_KEV_MODEL` | P2 P5 |
| ENV-21 | `DGX_KEV_THRESHOLD` | Python `float()` | `hook.kev.threshold` | `HYLO_HOOK_KEV_THRESHOLD` | P2 P5 P4 (T-082) |
| ENV-22 | `DGX_KEV_TIMEOUT` | Python `float()`; ≤ 0 / NaN ⇒ Kev unreachable; > 9.22e9 ⇒ crash (H-11) | `hook.kev.timeout_s` | `HYLO_HOOK_KEV_TIMEOUT_S` | P2 P5 P4 (T-083) |
| ENV-24 | `DGX_KEV_CHARS` | Python `int()`; `0` = no cap; `-n` drops head | `hook.kev.state_chars` | `HYLO_HOOK_KEV_STATE_CHARS` | P2 P5 P4 (T-085) |
| ENV-25 | `DGX_KEV_API_KEY` | value; empty → file | `hook.kev.api_key_file` (K-5) | `HYLO_HOOK_KEV_API_KEY_FILE` | P2 P5 |
| ENV-26 | `DGX_ENGLISH` | on iff `!= "0"` | `hook.english.enabled` | `HYLO_HOOK_ENGLISH_ENABLED` | P2 P5 P4 (H-6 siblings) |
| ENV-27 | `DGX_AUTOCONTINUE` | hook off iff `== "0"`; launcher on iff `!= 0` | `hook.autocontinue.enabled` | `HYLO_HOOK_AUTOCONTINUE_ENABLED` | P2 P5 P4 (H-5 siblings) |
| ENV-30 | `DGX_USER` | raw, unescaped header | `attribution.user` | `HYLO_ATTRIBUTION_USER` | P2 P5 |
| ENV-32 | `DGX_SKIP_PREFLIGHT` | skip iff `== "1"` (inverted) | **`run.preflight.enabled`** (K-1) | `HYLO_RUN_PREFLIGHT_ENABLED` | **changed** from P2/P5 `run.preflight` |
| — | (none; `PF:23` literal 4) | — | **`run.preflight.timeout_s`** (K-1) | `HYLO_RUN_PREFLIGHT_TIMEOUT_S` | P4r2 name; key path changed from `run.preflight_timeout_s` |
| ENV-34 | `DGX_MAIN_MODEL` | `opus` exact, else sonnet | `run.main_model` | `HYLO_RUN_MAIN_MODEL` | P2 P5 |
| ENV-35 | `DGX_REMOTE` | on iff `== "1"` | `run.remote_control` | `HYLO_RUN_REMOTE_CONTROL` | P2 P5 |
| ENV-36 | `DGX_SAFE` | prompts iff `== "1"` (inverted) | `run.skip_permissions` | `HYLO_RUN_SKIP_PERMISSIONS` | P2 P5 |
| ENV-37 | `DGX_SANDBOX` | on iff `== "1"` | `run.sandbox` | `HYLO_RUN_SANDBOX` | P2 P5 |
| ENV-38 | `DGX_STATUSLINE` | on iff `== "1"` | `run.statusline.enabled` | `HYLO_RUN_STATUSLINE_ENABLED` | P2 P5 P4 (H-7) |
| ENV-40 | `TMPDIR` | `${TMPDIR:-/tmp}` | `paths.proxy_log_dir` (default source, K-6) | `HYLO_PATHS_PROXY_LOG_DIR` | P2 P5 |
| ENV-15 | `COLUMNS` | Python `int()`, errors → 0 | — (Claude Code protocol input) | — | P2 P5 |
| ENV-23 | `DGX_KEV_MESSAGES` | Python `int()` at import, unused | — (accepted and ignored during parity) | — | P2 P5 P4 (T-084 DROP) |
| ENV-28 | `DGX_INVISIBLE` | `== 1` | — (D6) | — | P2 P5 |
| ENV-29 | `ROUTER_PORT` | raw | — (D6) | — | P2 P5 P4 (T-121) |
| ENV-31 | `ANTHROPIC_CUSTOM_HEADERS` | appended | — (Claude Code protocol) | — | P2 P5 |
| ENV-33 | `DGX_PROFILE` | zsh `source` | — (K-2: `--profile`) | — | **resolved** (P2 had `profiles.<name>`) |
| ENV-39 | `DGX_PRINT_ARGS` | `== 1` | — (`hylo run --print-args`) | — | P2 P5 |
| ENV-41 | `HOME` | OS | — (`os.UserHomeDir`) | — | P2 P5 |
| ENV-42 | `PWD` | basename | — (`os.Getwd`) | — | P2 P5 |
| ENV-43 | `ARGS` | zsh scalar prepended to argv | — (OD-60) | — | P5 |

Totals: 33 env inputs map to a key (unchanged); 2 more keys have no legacy env (`exporter.bind`, `run.preflight.timeout_s`) plus K-3's
`paths.failed_capture_dir`; 10 env inputs have no key. Open disagreement after this round: **K-1 only** (pass 4 r2 writes `run.preflight` /
`run.preflight_timeout_s`; this round proposes `run.preflight.enabled` / `run.preflight.timeout_s`; same HYLO name for the timeout).

---

## D. Additions to the inventories

### D.1 Env inventory (§A of round 1)

| ID | Input | Read by | Effect | Pin |
|---|---|---|---|---|
| **ENV-I18** (new) | `ZDOTDIR` and the startup file it selects: `$ZDOTDIR/.zshenv`, default `$HOME/.zshenv` (`/etc/zshenv` absent on this macOS) | zsh when running `claude-dgx` and `dgx-proxy-coordinator.sh` (shebang `#!/bin/zsh`, no `-f`, `LN:1`, `CO:1`) | arbitrary shell before line 1: can set `ARGS`, any `DGX_*`, `PATH`, options. **[exec]** `ARGS=(--from-zshenv)` in a scratch `.zshenv` reached `claude`'s argv | P4 launcher cases run with `zsh -f`, or with `HOME` and `ZDOTDIR` both pointing at an empty temp dir (round 1's pin set only `HOME`) |
| **ENV-I19** (new, adopted) | `MITMPROXY_CASE_SENSITIVE_FILTERS`; console-only `EDITOR`, `PAGER` | mitmproxy 12.3.1 (pass-1 r3 V1) | inert in legacy (no filter expressions; `mitmdump`) | unset |
| ENV-I12..I15 (refined) | **every** env var whose lower-cased name ends in `_proxy`, including `ALL_PROXY`, `FTP_PROXY`; lowercase wins; an empty lowercase value cancels the uppercase one | urllib `getproxies_environment` (3.11.7) | any non-empty one suppresses the macOS/Windows system-proxy fallback (ENV-I15) even if it is not `HTTP(S)_PROXY` | the harness env is built from scratch; `no_proxy=*` pin unchanged |
| ENV-I6..I9 (refined) | the whole `PYTHON*` class (round 1 listed 4) | interpreter (production runs `python3 '<file>'` without `-I`/`-E`) | `PYTHONWARNINGS=error` tested inert for the hook | unset all except the harness `PYTHONPATH` |

Counts: explicit inputs **43** (unchanged); implicit IDs **17 → 19**.

### D.2 Determinism inventory (§B of round 1)

| ID | Class | Site | Output effect | Pin (legacy) | Go injection point |
|---|---|---|---|---|---|
| **DET-53** (new) | network (resolver) at startup | `EX:414` `HTTPServer(("0.0.0.0", PORT), …)` → `server_bind` → `socket.getfqdn("0.0.0.0")` → `gethostname()` + `gethostbyaddr()` (3.9.6 stdlib) | none in `/metrics`; startup delay when the resolver is slow | P2 parity calls the rebuild/exposition path with no listener (as round 1's `Rebuild(…)` design already does) | none: Go `net/http` does no lookup (output-neutral deviation) |
| DET-09 (refined) | eager default | `PX:238` `getattr(flow, "_t0", time.time())`; `PX:273` `getattr(flow, "_dgx_t0", time.time())` (`_dgx_t0` set at `PX:153`) | unchanged | unchanged | unchanged |
| DET-13 (refined) | clock reads, measured | `HK:111,118,197` | 2 reads per successful Kev call, 1 per failed call, 1 per log line; no stdlib reads in between (**[exec]**) | mode 2 sequences written to these counts | unchanged |
| DET-18/23 (refined) | naive local time → epoch | `EX:125,145`, `SL:983` | Go `time.Date` differs from Python in the gap (west) and the repeated hour (east) | unchanged | `pytime.LocalToUnix(loc, wall)` = CPython `_mktime` port; `loc` injected; `time/tzdata` embedded |
| DET-20 (refined) | libc `mktime` | `SL:286` | repeated-hour choice switches at 01:45:19 (Chicago) | seeded `proc_start` (unchanged) | native probe (true value; OD-76) |

Count: **52 → 53** rows.

### D.3 Conventions (§C of round 1)

| ID | Convention | Evidence | Go equivalent |
|---|---|---|---|
| **CV-19** (new) | **Config key conventions** (the harmonized form of CV-09/10/18): component namespaces; `paths.*` for every location; `*_file` for secrets; unit suffixes; table + `.enabled` for features with settings, bare leaf for plain flags; HYLO names generated from the key registry (C.1) | §C; P2r1 §6; P4r1 §C; P4r2 §D | `internal/config` registry: one entry per key (type, default, rationale, legacy alias + predicate); env names derived, never parsed |

Count: **18 → 19**.

### D.4 Pitfall register (§D of round 1)

| ID | Tag | Pitfall | Occurrences | Reach | Go remedy | Test |
|---|---|---|---|---|---|---|
| PR-14 (remedy changed) | PT-TIME | Go `time.Date`/`ParseInLocation` resolve ambiguous and nonexistent local times differently from Python's fold-0 rule, depending on the zone's offset sign; Python `strptime` accepts lowercase `t` | `EX:125,145`; `SL:983` | production for east-of-UTC users (repeated hour every autumn); spring gap only for ledgers read in another zone | `pytime.LocalToUnix`: CPython `_mktime` port (0/3,096 mismatches) + hand-written lenient parser | T: the 9-zone grid as committed goldens |
| PR-15 (confirmed with Go) | PT-FMA | naive Go fuses; guard verified | `BF:75-76` (4 `FMADDD`), colorsys (3), `SL:558-559` (1, across statements) | ulp-level; 0 visible diffs on the sample | explicit `float64()` per product | T on **darwin/arm64** and `GOAMD64=v3` (v1 never fuses) |
| PR-18 (refined) | PT-PARSE | `urlparse().port` grammar differs by version (3.9.6 accepts `+80`, ` 80`, Unicode digits; 3.11.7 rejects); `strconv` deltas (B.1) | `PX:82`, `PF:20`; env parses | env only | `pyfmt` parsers; port: ASCII digits 0..65535, `0` → 80 (3.11/3.12 oracle) | T |
| **PR-22** (new) | **PT-DUR** (new tag) | float seconds → `time.Duration`: out-of-range and NaN conversions are implementation-defined (arm64: `inf` → `MaxInt64`, NaN → 0; amd64: both → `MinInt64`); `http.Client.Timeout ≤ 0` means **no timeout**, whereas Python's 0 / negative / NaN mean "never connects" and > 9,223,372,036.854775 s raises | `HK:34,113` (env); every hylo `*_timeout_s` key (K-8) | env and config edge values; changes semantics, not just digits | `config.Seconds` validated before conversion; alias path maps ≤ 0/NaN to "Kev disabled, no request" and the overflow range per OD-75 | T on arm64 **and** amd64 |

Count: **21 → 22** entries; tags 19 + 3 new (PT-FREPR, PT-INTLIM, **PT-DUR**).

---

## E. Owner decisions (new: OD-74..OD-76)

| ID | Decision | Options | Recommendation |
|---|---|---|---|
| **OD-74** | **Approve the harmonized key table (§C.3)** built on OD-01 | (a) approve as is: `run.preflight.enabled` / `run.preflight.timeout_s` (rule 5), `paths.failed_capture_dir`, `DGX_PROFILE` → `--profile`; (b) also allow per-leaf env overrides for map keys (`HYLO_<MAP>_<LEAF>`) and comma lists for list keys; (c) also reserve `HYLO_PROFILE` as a meta-variable outside the registry | **(a) + list encoding from (b)**, no map-leaf env overrides yet (no legacy env sets a map); decide `HYLO_PROFILE` with the P4 `hylo run` design. If the owner prefers pass-4 r2's flat `run.preflight` + `run.preflight_timeout_s`, only one key path changes |
| **OD-75** | **Out-of-domain timeout values** (A.3, PR-22). Legacy `DGX_KEV_TIMEOUT`: 0 / negative / NaN ⇒ Kev never contacted, heuristic decides; > 9,223,372,036.854775 s (incl. `inf`) ⇒ hook exit 1, no output. A naive Go port inverts the first case (no deadline) and differs by CPU architecture | (a) reproduce both on the `DGX_*` path, reject on `HYLO_*`/config; (b) reproduce "disabled" on the alias path, but reject the overflow range at config load with a clear error on every path (no crash reproduction); (c) reject all at config load | **(b).** "0 disables Kev" is a plausible user intent worth keeping on the alias path; reproducing a crash adds a test with no user value. `HYLO_HOOK_KEV_TIMEOUT_S` must be finite and > 0. Refines OD-59 |
| **OD-76** | **Legacy ⌂ in the repeated DST hour** (A.1): legacy uses macOS libc `mktime`, which picks the wrong occurrence from 01:45:19 to 01:59:59 local on fall-back day, so ⌂ is off by 3,600 s for windows started then | (a) approve as a deviation: hylo reports the true start (native probe); (b) emulate libc's choice | **(a).** Not reachable in the harness (seeded `proc_start`), and the legacy value is wrong |

---

## Delta Summary

| Area | New this round | Refined / confirmed |
|---|---|---|
| Go execution | naive-time grid: `time.Date` 46/3,096 mismatches, CPython-`_mktime` port 0/3,096 (**remedy change**); FMA on darwin/arm64 confirmed with real Go (200,751 / 1,439 / 0), guard verified (0), amd64 v1 vs v3; `Duration` conversion arch-dependent and `http.Client.Timeout ≤ 0` = no timeout (**remedy change**); `strconv` grammar deltas | round 1's emulation exact |
| Hook crash paths | end-to-end runs (11 + 3 cases); threshold 9,223,372,036.854775 s; `timeout=0` and CR/LF key now executed; H-10/H-11 rows proposed; clock-read counts measured; early stop exercised | ENV-19/22 confirmed |
| Exporter | port 0 executed (print says `:0`); **DET-53** resolver lookup at startup | ENV-18 confirmed |
| Env inventory | **ENV-I18** `.zshenv`/`ZDOTDIR` (pinned), **ENV-I19** mitmproxy reads (gap 4 closed by cross-reference) | `*_proxy` wildcard; `PYTHON*` class; urlparse version split; counts 43/17 confirmed → 43/19 |
| Determinism | DET-53; DET-20 libc quirk; DET-09 wording; DET-13 measured | 25 rows re-verified |
| Conventions | CV-19 config key conventions | — |
| Pitfalls | PR-22 / PT-DUR; PR-14 remedy changed | PR-15 confirmed, PR-18 refined, 13 rows re-verified |
| Key harmonization | one table, 9 disagreements resolved, 1 open with pass 4 (K-1) | 0 HYLO collisions over 134 keys |
| Owner items | OD-74, OD-75, OD-76 | OD-58..61 carried; OD-59 refined by OD-75 |
| Retractions | none (CONV-ABS-65..68 unused) | — |

Existing items refined: 6 (ENV-22, ENV-I12..I15, PR-18, DET-09, DET-20, PR-01) plus remedies of PR-14 and PR-15 test placement.

## Remaining Gaps (verbatim-carryable)

1. Python 3.12.10 (proxy and preflight venv) `urlparse` port strictness is inferred from 3.11.7; not executed (venv not opened this round).
2. DET-53 resolver-lookup latency at exporter start is source-derived; not measured (no network). Whether launchd starts the exporter before the
   resolver is ready was not checked.
3. Windows: the naive-time oracle cannot run there; the recommendation (Go goldens generated by CPython on macOS/Linux, `time/tzdata` embedded,
   `ZONEINFO` treated as a Go-side implicit input) is not executed on Windows.
4. K-1 key shape (`run.preflight.enabled` vs pass-4 r2's `run.preflight`) needs pass 4 to adopt it or the owner to pick (OD-74).
5. The ⌂ libc crossover (01:45:19) was measured for America/Chicago 2026 only; other zones and macOS versions not sampled (OD-76 does not depend on it).
6. Owner decisions OD-58..OD-61, OD-74..OD-76; carried OD-01, OD-05.

## Novelty Assessment

Novelty: SUBSTANTIVE

Removing this round would change the spec in four places:
- **Two Go-side results change remedies:** naive local time must be converted with a port of CPython's `_mktime`, because Go's `time.Date` disagrees
  with Python in 46 of 3,096 transition cases (gap for western zones, repeated hour for eastern zones); and timeout values must be validated before
  `Duration` conversion, because Go's `http.Client` treats ≤ 0 as "no timeout" (legacy: Kev disabled) and out-of-range conversions differ between
  arm64 and amd64 (new pitfall PR-22, OD-75).
- **Two missing inputs:** the launcher's `.zshenv`/`ZDOTDIR` (pinned: it can inject `ARGS` or any `DGX_*`), and the exporter's startup resolver
  lookup (DET-53).
- A new legacy determinism quirk (libc `mktime` in the repeated hour, OD-76) and a wider crash range for `DGX_KEV_TIMEOUT` (H-11).
- The key table now resolves every pass-2/4/5 naming disagreement but one (K-1).

## Convergence Declaration

Another round needed: this round changed two Go remedies and added two inputs. Round 3 should take Remaining Gaps 1-6 verbatim, re-audit this
round's new rows (ENV-I18, DET-53, PR-22, CV-19, the §C.3 table), and confirm K-1 against pass 4's latest round.

## State Checkpoint

```yaml
pass: 5
round: 2
status: complete
files_scanned: 11   # all legacy files; ranges in the header; plus CPython 3.9.6/3.11.7 stdlib functions named in the header
timestamp: 2026-11-14T09:05:00Z
novelty: SUBSTANTIVE
counts: {env_explicit: 43, env_implicit_ids: 19, determinism_rows: 53, conventions: 19, pitfall_entries: 22, new_tags_total: 3}
verification: {confirmed: 14, refined: 6, retracted: 0, new_inputs_or_sources: 3}
go_probes: [godst, gomktime, gofma, gofma2, godur, gohttpto, goparse]
retractions: []
owner_items: [OD-74, OD-75, OD-76]
unused: {conv_abs: [CONV-ABS-65, CONV-ABS-66, CONV-ABS-67, CONV-ABS-68], od: [OD-77]}
next: pass 5 round 3 (targets = Remaining Gaps 1-6 verbatim)
```
