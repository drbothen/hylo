# Pass 5 deepening, round 4: verification round (hylo-legacy)

- **Source:** `$HOME/Dev/hylo/legacy/` (read-only). Re-read this round: `dgx_statusline.py:555-562,880-933,1130-1182,1228-1245`,
  `auto_continue.py:104-166,215-229`, `dgx_ledger_exporter.py:268-280`, `dgx_preflight.py:14-24`, `tools/backfill_cost_history.py:70-78`,
  `claude-dgx:55-80` plus a command census of `claude-dgx` and `dgx-proxy-coordinator.sh`, and an `ast` scan (text only, nothing imported) of
  all six legacy `.py` files.
- **Newly authorized source, read as text only and never imported:** mitmproxy 12.3.1 at
  `$PROTOTYPE/.mitmenv/lib/python3.12/site-packages/mitmproxy/` (`version.py:5` `VERSION = "12.3.1"`). Cites into it
  carry the prefix `m/`.
  **Scope disclosure:** two commands went outside that subdirectory, both read-only. One `ls` listed the names in the parent `site-packages`
  directory (`mitmproxy`, `mitmproxy_macos`, `mitmproxy_rs`, their dist-info folders). One `grep` for `os.environ|getenv` over `../mitmproxy_rs`
  printed nothing. Neither result is used as evidence below. `pyvenv.cfg` and `certifi` were not read.
- **Inputs read:** pass-5 deep r3 (all) and r2 (all; §D/§E/Delta/Gaps in full). Siblings read for cross-reference only, none edited:
  pass-2 r5/r6/r7 and pass-0 r1 for `config.yaml` and `opus_verdict`, and pass-0 r3 row 12. **Pass-4 r5** did not exist when this round
  started. It appeared while this file was being written and was then read (headers, §A-§D summaries, numbering) but not edited (§D.3).
  `CLAUDE.local.md` was not read.
- **Method:** fresh scripts in `scratchpad/p5r4/`: `usite4/` (user-site probe and two throwaway venvs), `gosub4/` (FMA on the subagent clock),
  `goshape4/` (FMA shapes, cross-compiled), `dst4/gen4.py` + `dst4/go/` + `dst4/gorule/` (DST oracle, `time.Date`, fresh `_mktime` port, rule
  test), `attrscan.py`, `fma4.py`. Interpreters: CPython 3.11.7 (`/opt/homebrew/anaconda3`) and 3.9.6 (`/usr/bin`), run with `-I` wherever
  they read scratch data. Go 1.26.5 darwin/arm64, `GOFLAGS=-mod=mod GOTOOLCHAIN=local`. amd64 was **cross-compiled and listed only, never
  run**. **No socket was opened, no name was resolved, no proxy ran, nothing from `legacy/` was executed, no process was left running, and no
  file was created in the hylo repo.**
- **Numbering:** retraction **CONV-ABS-89** (90-92 unused). Owner items: **none** (OD-98..OD-101 unused). New ID: **ENV-I21**. **[exec]** =
  executed this round. Cite prefixes as in r3: `SL` `PX` `HK` `EX` `BF` `LN` `CO` `PF`.

---

## A. Re-verification of round 3's new items (fresh scripts)

### A.0 Verification table

| # | Round-3 item | Fresh evidence (round 4) | Verdict |
|---|---|---|---|
| V1 | **ENV-I20**: user site-packages under `HOME` runs `.pth` and `usercustomize` code for every non-venv legacy script; `-s` / `PYTHONNOUSERSITE=1` stop it | **[exec]** New probe in a scratch `HOME`, with `site.getusersitepackages()` resolved under `env -i`: 3.11.7 → `~/.local/lib/python3.11/site-packages`, 3.9.6 → `~/Library/Python/3.9/lib/python/site-packages`. Results were the same on both versions. plain: `PTH` then `USERCUSTOMIZE` ran before the body. `-s`: neither ran. `PYTHONNOUSERSITE=1`: neither. **`-E` with `PYTHONNOUSERSITE=1`: both ran**, because `-E` ignores the variable. `-I`: neither. `PYTHONUSERBASE` relocates the user site and ignores `HOME` (it ran with `HOME=/nonexistent`). **Order:** user `.pth` runs, then `sitecustomize` (the clock shim), then `usercustomize`, so a `usercustomize` can undo the shim. **Venvs:** a default venv suppressed both (`site.py:535-539`, `ENABLE_USER_SITE = False`). A `--system-site-packages` venv ran both | **Confirmed + 3 refinements** (§A.1) |
| V2 | ENV-I20 component scope: SL, HK, BF and the trust CLI on 3.11.7, EX on 3.9.6; not PX/PF (venv) | Invocations re-read: `LN:13` `exec python3 … trust`, `LN:161` hook, `LN:176-177` status line, exporter plist `/usr/bin/python3`, all with neither `-s` nor `-I`. **Also affected:** the visible-mode preflight `LN:62` (`PF_PY=python3` when `DGX_INVISIBLE != 1`), which is a dead mode (D6). PX (`LN:75`, `CO:31`) and PF (`LN:61`) run from `.mitmenv` and are unaffected **only if** its `pyvenv.cfg` has `include-system-site-packages = false`. The file is outside this round's authorization and was not read, so the exclusion stays inferred | **Confirmed, conditional stated** |
| V3 | **PR-15 / DET-54**: `SL:889` → `SL:919` fused on arm64; directed case shows `01:00` in naive Go vs `01:01` in Python | **[exec]** New Go program. arm64 listing: naive `main.naive` = 1 `FNMSUBD`; guarded `float64(now*1000)` = `FMULD` + `FSUBD`. Directed case `now=1790000000.5009999`, `start=1789999939501`: naive **`01:00`** (60.999999927520754), guarded **`01:01`** (61). CPython 3.11.7 and 3.9.6 both print **`01:01`**. Random sample (new generator, PCG seed 20261114, 30,000,000 cases): 29,765,795 bit differences, **5 displayed differences**. In all 5, Python's elapsed time is an exact multiple of 1,000 ms (the millisecond digits of `now` equal those of `start`) and the fused value lands just below it. Python matched guarded Go on all 5 and on a 100,000-row sample, and matched naive Go on 0 of the 5 | **Confirmed + characterized** |
| V4 | DET-54 scope: only the `--subagent` path; OOS unless OD-14 keeps it | `SL:1240-1241` → `main_subagent` `SL:928` → `render_subagent_rows` `SL:888`. This is the only caller, and `SL:889` is the only clock read on the path. Pass-0 r3 row 12 still says "OOS (PLAN §3); parity treatment pending OD-14" | **Confirmed** |
| V5 | **CONV-ABS-77**: amd64 v3 fuses only register-operand additions; no subtraction rule (`AMD64.rules:1521`) | Source: `AMD64.rules:1521` `(ADDS(S\|D) (MULS(S\|D) x y) z) && buildcfg.GOAMD64 >= 3 && …useFMA(v)` is the **only** detection rule (`:127` lowers explicit `math.FMA`). `ARM64.rules:1771-1782` has add **and** subtract forms. Fresh cross-compiled shapes (`-gcflags=-S`): v1/v2 fused nothing. **v3 and v4 fused** `a*b+c` (1), `c+a*b` (1), and a 4-product sum held by value (3). They fused 0 for: memory operand `a*p.In+c`, a 4-product sum through a pointer, `a*b-c`, `c-a*b`, the subagent shape, and the ⌂-gate shape. arm64 fused every one of these shapes | **Confirmed** |
| V6 | V7 refinement: `Dialer.Timeout` and `TLSHandshakeTimeout` test `!= 0`, so a negative value expires immediately | Source, Go 1.26.5: `net/dial.go:252` `if d.Timeout != 0 { // including negative, for historical reasons`; `net/http/transport.go:1727` `if d := pconn.t.TLSHandshakeTimeout; d != 0 { timer = time.AfterFunc(d, …)`. A negative `AfterFunc` fires at once and races the handshake goroutine; the first value on `errc` wins. Contrast: `ResponseHeaderTimeout` `> 0` (`:2920`), `IdleConnTimeout` `> 0` (`:1160,1195`), `Client.Timeout` `> 0` (`client.go:198`, doc `:96`). Not executed (would need a dial) | **Confirmed** (wording: "immediate expiry, racing the handshake") |
| V7 | Generalized DST rule, 713 / 4,132 on the r3 grid | **[exec]** (a) Python epochs re-derived from round 3's wall times with a new script: 0 of 4,132 differ from the r3 file, and 3.11.7 = 3.9.6 byte for byte. (b) New Go `time.Date` harness: **713 / 4,132**, same per-zone split as r3. (c) Fresh `_mktime` port: **0 / 4,132**. (d) **New grid**: 18 zones, 2,149 rows, 3.11.7 = 3.9.6, `strptime` = `fromisoformat` on every row. `time.Date` mismatched 198 rows, the port mismatched **0**. **But two zones contradict round 3's A.1 row 4:** Atlantic/Azores 2026 and America/Scoresbysund 2023 fall back from offset **0** to −1. The probe offset in the repeated hour is 0, and Go returns the **first** occurrence, equal to Python (12 + 12 rows, 0 mismatches) | **Count confirmed; rule statement partly retracted: CONV-ABS-89** (§A.2) |

Verdicts: **6 confirmed** (V1-V6, with V1, V3 and V6 refined), **1 confirmed in count but narrowed by a retraction** (V7).

### A.1 ENV-I20 refinements (all executed)

1. **`-E` does not neutralize it.** `-E` makes the interpreter ignore `PYTHONNOUSERSITE`. A harness that runs the oracle as
   `python3 -E` with `PYTHONNOUSERSITE=1` still runs user-site code. Reliable switches: temp `HOME` (already in every pin set), `-s`, or `-I`.
   Note that `-I` also drops `PYTHONPATH`, which the clock shim needs, so `-I` cannot be used for shimmed cases.
2. **Order relative to the clock shim:** user `.pth`, then `sitecustomize`, then `usercustomize`. A stray `usercustomize.py` runs **after** the
   shim and could re-patch `time`. The temp-`HOME` pin covers this; the pin text now says why.
3. **The venv exclusion is conditional:** `--system-site-packages` keeps the user site (`site.py:535` keeps `ENABLE_USER_SITE` unless
   `system_site != "true"`). PX/PF stay "inferred unaffected" until `.mitmenv/pyvenv.cfg` is read (Remaining Gap 1).
4. **Negative note:** these interpreter installs also run base `site-packages` `.pth` files that read the environment. Anaconda 3.11.7
   `coloredlogs.pth` reads `COLOREDLOGS_AUTO_INSTALL`, and `distutils-precedence.pth` (Anaconda and the Xcode 3.9.6) reads
   `SETUPTOOLS_USE_DISTUTILS`. These come with the interpreter install (DET-50), not from `HOME`. They do not affect output: the only legacy logger,
   `log` at `PX:51`, is never used (no `log.` call in `PX`), and no legacy file imports `distutils`. The env-from-scratch pin (DET-43) already
   unsets both.

### A.2 DST rule restated exactly (CONV-ABS-89)

Go 1.26.5 `time.Date` (`time/time.go:1734`, tail of the function): `o₁` = the zone offset at the wall time read as UTC. If `o₁ ≠ 0` and
`wall − o₁` falls outside `o₁`'s period, Go looks up the offset again at `wall − o₁`. Python (fold 0) takes the earliest instant in an overlap
and, in a gap, the wall time read with the pre-transition offset. Let the transition be at UTC instant `T`, from offset `oᵦ` to `oₐ`.

| Wall time in | Go differs from Python exactly when | Hence |
|---|---|---|
| gap `[T+oᵦ, T+oₐ)` | the wall, read as UTC, is **before `T`** (Go picks `oₐ`, so it is earlier by `oₐ−oᵦ`) | every gap wall differs if **`oₐ ≤ 0`**; none differ if `oᵦ ≥ 0`; a straddling gap (`oᵦ < 0 < oₐ`, e.g. Apia 2011) differs for walls before `T` only |
| overlap `[T+oₐ, T+oᵦ)` | the wall, read as UTC, is **at or after `T`** (Go picks the second occurrence, later by `oᵦ−oₐ`) | every repeated wall differs if **`oₐ ≥ 0`**; none differ if **`oᵦ ≤ 0`**; straddling overlaps differ for walls at or after `T` |

**[exec]** Tested on the new grid: predicted mismatch = (gap and probe offset = `oᵦ`) or (overlap and probe offset = `oₐ`). **0 exceptions in
2,149 rows**, covering all 18 zones. Go's zero-offset shortcut never changes the outcome. It can trigger only when the probe offset equals the
side Go would pick anyway.

**CONV-ABS-89.** Two items are retracted. (1) Round 3 §A.1 table row 4: "overlap | ≥ 0, **including 0** | Go picks the second occurrence".
(2) The pin wording that follows from it, "one west and one east-or-zero DST zone" (r3 §B.2 ENV-I1, §B.4 P1). Counterexamples (executed):
Atlantic/Azores 2026 (0 → −1) and America/Scoresbysund 2023 (0 → −1). The probe offset there is 0, Go returns the first occurrence, and the
result equals Python. A harness that chose Azores as its "zero" zone would never exercise the overlap defect. Round 3's one-directional
statements remain **true**: every gap mismatch has `oᵦ < 0` and every overlap mismatch has `oₐ ≥ 0`. The remedy is **unchanged**
(`pytime.LocalToUnix` = CPython `_mktime` port, now 0 mismatches on 4,132 + 2,149 fresh rows, plus r3's 7,228).
**Corrected pin wording:** naive-time cases use (a) a zone whose spring transition **ends** at offset ≤ 0 (any US zone; Azores also works) and
(b) a zone whose autumn transition **ends** at offset ≥ 0 (Europe/London, Europe/Berlin, Australia/Sydney). The existing goldens already
include both kinds.

---

## B. V10 / ENV-I19 closed: mitmproxy 12.3.1 environment reads

Method: text search of every `.py` under `m/`, excluding `m/test/`, for `os.environ`, `getenv`, `environ.get`, `environ[`, `putenv`,
`expandvars`, bare `environ` and `MITMPROXY_*`. Then a second search for indirect environment-dependent calls (`expanduser`, `Path.home`,
`tempfile`, `shutil.which`, `webbrowser`, `locale`, `certifi`, `isatty`, `signal.signal`, `os.name`, `sys.platform`). The legacy path is
`mitmdump --set flow_detail=1 --listen-port N -s dgx_proxy.py` (`LN:75`, `CO:31`) → `m/tools/main.py:153-166` `mitmdump` → `run`
(`:45`) with `DumpMaster`.

| Variable | Read at | On the mitmdump path? | Effect | Legacy behavior change? |
|---|---|---|---|---|
| `MITMPROXY_CASE_SENSITIVE_FILTERS` | `m/flowfilter.py:57-61` (import time; `m/addons/dumper.py` imports `flowfilter`) | yes | `"1"` makes filter expressions case-sensitive | none: legacy passes no filter expression |
| `MITMPROXY_SSLKEYLOGFILE`, then `SSLKEYLOGFILE` | `m/net/tls.py:147-149` (import time) | yes | writes TLS secrets to the named file | ENV-I17 (already pinned unset) |
| `PYTEST_CURRENT_TEST` | `m/log.py:73,81` (`MitmLogHandler`, the base of `TermLogHandler` `m/addons/termlog.py:37` and `ErrorCheckHandler` `m/addons/errorcheck.py:49`); `m/utils/asyncio_utils.py:46` | yes | log filter compares the value captured at handler creation with the current one; task names get a suffix | none: the value is fixed per process, so the filter always passes; task names are not output |
| `MITMPROXY_DEBUG_EXIT` | `m/utils/debug.py:110,124` | only after `SIGUSR1`/`SIGUSR2`. The handlers are installed at `m/tools/main.py:65` → `m/utils/debug.py:129-131`, non-Windows | after the debug dump, `sys.exit(1)` | none: legacy sends neither signal |
| `MITMPROXY_EDITOR`, `EDITOR` | `m/tools/console/master.py:115,117` | **no** (console UI only) | editor for flow editing | none |
| `MITMPROXY_EDITOR`, `PAGER`, `EDITOR` | `m/tools/console/master.py:172-174` | **no** | viewer | none |
| indirect: `HOME` (Windows `USERPROFILE`) | `confdir` default `~/.mitmproxy` (`m/options.py:6,49-51`), expanded at `m/optmanager.py:571` (`load_paths`) and `m/addons/tlsconfig.py:509` (CA store) | yes | selects `config.yaml`/`config.yml` and the CA (**ENV-I21**, §D.1) | yes, if a `config.yaml` exists (pass-2 r6: absent in production) |
| negative: `SSL_CERT_FILE`, `SSL_CERT_DIR` | upstream verification loads `certifi.where()` explicitly (`m/net/tls.py:217-220`) when no CA option is set | — | the system trust env is not consulted by mitmproxy's own code | none (`certifi` itself was not read) |

**ENV-I19 corrected.** Round 3 (adopted from pass-1 r3 V1) listed `MITMPROXY_CASE_SENSITIVE_FILTERS`, `EDITOR` and `PAGER`. Three corrections:
`EDITOR` and `PAGER` are **console-only** and are not read by `mitmdump`; `PYTEST_CURRENT_TEST` and `MITMPROXY_DEBUG_EXIT` were missing (both
inert); `MITMPROXY_EDITOR` was missing (console-only). **None of these changes legacy behavior.** The pin "unset" is unchanged; DET-43 already
builds the environment from scratch. Not covered: the `mitmproxy_rs` / `mitmproxy_macos` native extensions and third-party dependencies
(`certifi`, `pyOpenSSL`, `aioquic`, `tornado`). They are outside this round's authorization and stay Remaining Gap 2.

---

## C. Final mechanical scan and diff against the consolidated inventories

### C.1 Scan

`attrscan.py`: `ast.parse` of the six legacy `.py` files. It records every attribute chain rooted at `os`, `sys`, `time`, `datetime`, `locale`,
`socket`, `subprocess`, `urllib`, `random` or `platform`, including names bound by `from <mod> import` and local imports, and keeps the longest
chain at each site. Result: **38 distinct chains** plus 2 from-imported names. `locale`, `random` and `platform` have **zero** accesses.
A second scan (`fma4.py`) lists every `+`/`-` whose operand is a product, directly or through a variable assigned from a product anywhere
earlier in the function. A shell census of `LN` and `CO` lists their external commands.

### C.2 Diff

| Scan hit (sites) | Inventory row | State |
|---|---|---|
| `time.time` ×21: `SL:231,243,304,322,408,499,558,825,826,889`; `PX:128,238,273,296,530,535,723,724`; `HK:111,118`; `BF:95` | DET-01..14, DET-54 | all 21 covered |
| `time.strftime` ×5 (`PX:60,72,632,709`; `HK:197`) | DET-15..18 | covered |
| `time.mktime` + `time.strptime` `SL:286` | DET-20 | covered |
| `time.sleep` `PX:725` | DET-12 (OOS) | covered |
| `datetime.datetime.fromisoformat` `BF:39`, `SL:983`; `.strptime` `EX:125,145` | DET-22, DET-19, DET-21 | covered |
| `os.environ.get` ×31 sites | 27 distinct names (recounted) = §B.1's 27 Python inputs | covered |
| `os.environ` `HK:153` (child env for `claude -p`) | r3 V14 "dead env write" (`opus_verdict` is never called, pass-0 r1 row 21) | covered |
| `os.getcwd`/`os.path.abspath` `SL:373`; `os.getppid` `SL:278`; `os.getpid` `PX:518` | DET-38, DET-31, DET-32 | covered |
| `os.stat` `EX:66,282`, `SL:1013`; `os.path.getmtime` `BF:98`; `os.path.isfile/isdir` `SL:377,379,384,1010` | DET-36, DET-37, DET-39..42, DET-14 | covered |
| `os.path.expanduser` ×11 (`BF:33,97`; `EX:22,23`; `HK:100,195,196`; `PX:53,54,88`; `SL:78`) | CV-11, ENV-41, ENV-I11 | covered |
| `os.makedirs`/`os.fdopen`/`os.replace` (`SL:200-204`, `BF:112-116`, `PX:619-622`, `HK:195`) | CV-01..04 | covered |
| `os.path.join/basename/dirname/normpath` | DET-35, DET-47 (`SL:201`), PR-20 | covered |
| `socket.create_connection` `PF:23`; `socket.timeout` `PF:32` | DET-27; the PF error mapping is a BC (on 3.12 `socket.timeout` is `TimeoutError`, the same catch) | covered |
| `subprocess.run` ×9: `SL:280`; `PX:568-693` (trust CLI, OOS); `PX:722`; `HK:154` (dead) | DET-31, ENV-08, OOS trust rows, dead path | covered |
| `subprocess.TimeoutExpired` `HK:164` | dead path | covered |
| `sys.argv` `PF:18`, `SL:1240`, `PX:760-761` | ENV-03 (PF takes the upstream URL from argv; `LN:63` passes it), DET-54/OD-14, OOS | covered |
| `sys.stdin` `SL:1202`, `HK:211`, `SL:930` | DET-44; `SL:930` is the `--subagent` reader (OD-14) | covered (SL:930 noted) |
| `sys.exit` ×11, `sys.stderr` `PX:763` | E-ladder CV-08 / OOS trust CLI | covered |
| `urllib.parse.quote` `SL:165`; `urllib.request.ProxyHandler`/`build_opener` `SL:168`; `.Request` `HK:110`; `.urlopen` `HK:113`; `urllib.error.URLError` `HK:119` | DET-25, DET-26, ENV-I12..I16 | covered |
| `urlparse` `PF:19`, `PX:80` | ENV-03, PR-18 | covered |
| `parse_qs` `EX:274` (`?rebuild=1` on `/metrics`, `EX:270-274`) | not in pass-5 tables; it is an exporter **request** input documented by passes 0, 1 and 3. P2 parity calls `Rebuild` with no listener (DET-53), so nothing needs pinning | **cross-ref note** (no new row) |
| `EX` imports `urlparse` but never uses it | — | convention nit (unused import) |
| PR-15 scan: `SL:559` (via `win_ms@558`), `SL:919` (via `now_ms@889`), `BF:75` (4 nested adds), `BF:95` (int product) | PR-15 occurrences (colorsys is stdlib, `SL:146-147`) | **identical to r3's list**; no new site |
| `sum()` sites `SL:1137,1164,1166,1181` | — | **negative:** Python 3.12+ `sum()` uses compensated summation for floats, but these sums are of `int`s (`len()` counts) on 3.11.7. Not a hazard |
| Shell commands: `LN` `whoami`, `basename`, `grep`, `nc`, `sleep`, `python3`, `mitmdump`, `claude`, `curl` (`LN:85`, dead visible mode); `CO` `lsof`, `grep`, `flock`, `mkdir`, `sleep`, `mitmdump` | ENV-I10 lists `python3`, `ps`, `claude`, `nc`, `whoami`, `curl`, trust tools, `lsof`/`flock` | **`grep`, `basename`, `sleep`, `mkdir` missing** from the ENV-I10 tool list (POSIX utilities resolved from `PATH`; refinement) |

**Is anything still open after the scan?** No legacy Python attribute access and no product-sum site is missing from the inventories. The
scan's only additions are wording: four POSIX tools in ENV-I10, one cross-reference note for the exporter query, and an unused import. One input
outside the scan's reach is missing from pass 5's tables: mitmproxy's `HOME`-selected `confdir` (ENV-I21, from §B).

---

## D. Changes to the consolidated artifacts (round 3 §B stays the base)

### D.1 Implicit inputs: 20 → 21 IDs

| ID | Input | Read by | Effect | Pin | Src |
|---|---|---|---|---|---|
| **ENV-I21** | **mitmproxy `confdir` under `HOME`**: `$HOME/.mitmproxy/config.yaml`, then `config.yml` (`m/tools/main.py:85-89`, `m/optmanager.py:564-580`); the CA store `mitmproxy-ca*` (`m/addons/tlsconfig.py:509-517`), created when missing (`m/certs.py:617,653-656`) | `mitmdump` for PX (`LN:75`, `CO:31`) | **Precedence (source):** `--set flow_detail=1` is applied first (`m/tools/main.py:84`, `m/optmanager.py:346`). `config.yaml` then overwrites it ("over-writing options already set", `m/optmanager.py:548-561`). Last, `process_options` applies explicit flags (`--listen-port`, `-s`; `m/tools/main.py:23-39`). So a `config.yaml` can change any option, including `flow_detail`, but cannot change the listen port or replace the `-s` script list. Production has no `config.yaml` (pass-2 r6) | temp `HOME` (already in the P3 pin). Consequence: mitmproxy **generates a fresh CA** in the temp `confdir` at the first start of each case. P3 cases should pre-seed a fixture CA there, or run the addon without `mitmdump`; replays never compare certificates | **R4** |
| ENV-I19 (corrected) | on the mitmdump path: `MITMPROXY_CASE_SENSITIVE_FILTERS`, `PYTEST_CURRENT_TEST`, `MITMPROXY_DEBUG_EXIT` (+ the ENV-I17 pair); console-only: `MITMPROXY_EDITOR`, `EDITOR`, `PAGER` | mitmproxy 12.3.1 (§B) | inert in legacy | unset | R2, **R4** (verified) |
| ENV-I20 (refined) | as r3 | as r3 + visible-mode PF `LN:62` (dead); PX/PF exclusion conditional on `pyvenv.cfg` | as r3; `usercustomize` runs **after** the shim | temp `HOME`, or `-s`. Do not rely on `-E` + `PYTHONNOUSERSITE`. `-I` is incompatible with the shim | R3, **R4** |
| ENV-I10 (refined) | `PATH` | + `grep`, `basename`, `sleep`, `mkdir` | — | unchanged | R1, **R4** |
| ENV-I1 (pin reworded) | `TZ` | unchanged | unchanged | naive cases: one zone whose spring transition ends at offset ≤ 0, one whose autumn transition ends at offset ≥ 0 (CONV-ABS-89) | R1, R3, **R4** |

### D.2 Determinism, pins, pitfalls

- **B.4 P1 pin**: "TZ = UTC plus one west and one east-or-zero DST zone" → "UTC, plus a zone whose spring transition ends at ≤ 0 and one whose
  autumn transition ends at ≥ 0 (e.g. America/Chicago + Europe/London)". **B.4 P3 pin**: add "pre-seeded fixture CA in the temp `confdir`;
  no `config.yaml`" (ENV-I21).
- **PR-14** wording: "differs in gaps (offset < 0) and overlaps (offset ≥ 0)" → "differs in a gap when the wall, read as UTC, precedes the
  transition (all gap walls if the post-transition offset is ≤ 0), and in an overlap when it follows the transition (all repeated walls if the
  post-transition offset is ≥ 0)". Remedy and test unchanged. Goldens: 4,132 + 3,096 + 2,149 rows.
- **PR-15**: occurrences unchanged and re-verified. Characterization added: the visible `SL:919` defect occurs when Python's elapsed time is an
  exact multiple of 1,000 ms. A test row for it: `now=1790000000.5009999`, `start=1789999939501`, expect `01:01`.
- **PR-22**: `TLSHandshakeTimeout` negative → "fires at once, racing the handshake".
- DET table: **54 rows, unchanged** (DET-43's from-scratch env already covers ENV-I19/I21 variables; DET-50 covers the base-interpreter `.pth`
  files). CV: **19, unchanged**. PR: **22 entries, 22 tags, unchanged**.

### D.3 Sibling reconciliation

| Sibling | Item | State |
|---|---|---|
| pass-2 r6 §0 / r7 §1 | `config.yaml` absent; `tools/main:86-90` | consistent: this round cites `m/tools/main.py:85-89`, a one-line offset in the same block. The precedence detail (overrides `--set`, not explicit flags) is new to pass 5 and does not contradict pass 2 |
| pass-1 r3 V1 / pass-2 r7 | "mitmdump reads no `MITMPROXY_*` option environment"; ENV-I19 list | **partly corrected**: `MITMPROXY_CASE_SENSITIVE_FILTERS` and `MITMPROXY_DEBUG_EXIT` are `MITMPROXY_*` reads on the mitmdump path, but neither sets an *option*, so pass-2 r7's "option environment" statement stands. `EDITOR`/`PAGER` are console-only |
| pass-0 r3 row 12 | `--subagent` OOS pending OD-14 | DET-54 / PR-15 `SL:889/919` remain OD-14-conditional |
| pass-4 r5 (HTTP/2 re-classification; CONV-ABS-85..87, OD-94) | its subject is HTTP/2 thresholds; its header says pass-5 r3 "has no HTTP/2 statement that this round changes" | **no overlap and no conflict.** Numbering does not collide (pass 4 used CONV-ABS-85..87 and OD-94; this round uses CONV-ABS-89 and no OD). Pass-4 r5 cites `m/tools/main.py` and `m/certs.py` for other purposes and does not touch `config.yaml` precedence or env reads |

---

## Delta Summary

| Area | New (R4) | Refined / confirmed |
|---|---|---|
| Verification | 7 checks: 6 confirmed (3 with refinements), 1 count confirmed with a rule retraction | ENV-I20 executed on both versions with 5 switch modes + 2 venvs; DET-54 directed case + 30 M random (5 displayed); CONV-ABS-77 re-derived from rules and fresh shapes; Dialer/TLS `!= 0` re-read; 713/4,132 reproduced from a re-derived oracle |
| Retractions | **CONV-ABS-89**: r3 A.1 row 4 ("overlap at offset ≥ 0 including 0 → second occurrence") and the pin wording "east-or-zero". Counterexamples Azores 2026, Scoresbysund 2023 (executed) | exact side-of-transition rule, 0 exceptions on 2,149 new rows; `_mktime` port 0 mismatches on 6,281 fresh rows |
| Env inventory | **ENV-I21** mitmproxy `confdir` (`config.yaml` precedence, CA generation under temp `HOME`): known to pass 2, missing from pass-5 tables | ENV-I19 closed by source (2 inert reads added, 2 moved to console-only); ENV-I20 (`-E` caveat, shim order, venv condition, `LN:62`); ENV-I10 (+4 tools); ENV-I1 pin reworded |
| Completeness scan | — | 38 chains + 2 names: every site maps to an existing row; PR-15 site list identical; `sum()` negative; exporter `?rebuild` cross-ref; unused `urlparse` import in EX |
| Owner items | none (OD-98..OD-101 unused) | OD-14 still governs DET-54 |

Existing items refined: 8 (ENV-I1, ENV-I10, ENV-I19, ENV-I20, PR-14, PR-15, PR-22, B.4 P1/P3 pins).

## Remaining Gaps (verbatim-carryable)

1. `.mitmenv/pyvenv.cfg` was not read (outside this round's authorization). PX/PF are unaffected by ENV-I20 only if
   `include-system-site-packages = false`.
2. Environment reads in mitmproxy's native extensions (`mitmproxy_rs`, `mitmproxy_macos`) and third-party dependencies (`certifi`, `pyOpenSSL`,
   `aioquic`, `tornado`, `ruamel.yaml`) were not searched (outside authorization).
3. Carried from r3: Python 3.12.10 URL port grammar bracketed, not run; amd64 and Windows not executed (listings only); DET-53 latency and
   launchd ordering unmeasured (no network by rule). The `config.yaml` precedence is from source, not executed.
4. DET-54 and the `SL:889/919` occurrence matter only if OD-14 keeps the `--subagent` path.
5. Owner decisions carried: OD-74, OD-75, OD-76, OD-58..OD-61, OD-14, OD-01, OD-05.

## Novelty Assessment

Novelty: SUBSTANTIVE

Judged strictly by this round's rule (a retraction or a new input is substantive):
- **CONV-ABS-89** retracts round 3's overlap rule "offset ≥ 0, including 0 → Go picks the second occurrence" and the pin wording built on it.
  Two executed counterexamples (Azores 2026, Scoresbysund 2023, both 0 → −1) give Go = Python. The exact rule has 0 exceptions on a new
  2,149-row grid. The remedy (`_mktime` port) does not change; the test-zone selection guidance does.
- **ENV-I21**: mitmproxy's `HOME`-selected `confdir` (`config.yaml`, CA store) is an implicit input missing from pass 5's consolidated tables.
  Passes 1 and 2 already knew the file existed and that it is absent in production, so this is new to pass 5 only. The new parts are the
  precedence (it overrides `--set flow_detail`, not `--listen-port`/`-s`) and the harness consequence (temp `HOME` makes mitmproxy generate a
  CA per case). If the orchestrator rules that sibling-known inputs do not count, CONV-ABS-89 alone still makes the round SUBSTANTIVE.

Everything else is confirmation or refinement: ENV-I20 (plus `-E`, shim order, venv condition), DET-54 (directed case reproduced, mechanism
characterized), CONV-ABS-77, the `!= 0` timeout knobs, 713/4,132, the ENV-I19 listing (inert, NITPICK by the stated rule), and the mechanical
scan, which found no missing Python input or FMA site.

## Convergence Declaration

Another round needed: this round is SUBSTANTIVE (one retraction, one inventory addition). Round 5 should re-verify CONV-ABS-89 (exact rule) and
ENV-I21 (precedence; CA generation), and take Remaining Gaps 1-5 verbatim.

## State Checkpoint

```yaml
pass: 5
round: 4
status: complete
files_scanned: 11   # all legacy files (ast scans of every .py; shell command census) + mitmproxy 12.3.1 package text (254 .py, test/ excluded from findings) + CPython 3.11.7 site.py + Go 1.26.5 time/net/net/http/ssa rules
timestamp: 2026-11-14T09:45:00Z
novelty: SUBSTANTIVE
counts: {env_explicit: 43, env_implicit_ids: 21, determinism_rows: 54, go_side_pins: 6, conventions: 19, pitfall_entries: 22, tags: 22}
verification: {checks: 7, confirmed: 6, refined: 3, retracted_partially: 1}
probes: [usite4, gosub4, goshape4, dst4/gen4.py, dst4/go, dst4/gorule, attrscan.py, fma4.py]
retractions: [CONV-ABS-89]
owner_items: []
unused: {conv_abs: [CONV-ABS-90, CONV-ABS-91, CONV-ABS-92], od: [OD-98, OD-99, OD-100, OD-101]}
sibling_disagreements: []
network: none (no socket bind, no DNS)
next: pass 5 round 5 (re-verify CONV-ABS-89 and ENV-I21; Remaining Gaps 1-5 verbatim)
```
