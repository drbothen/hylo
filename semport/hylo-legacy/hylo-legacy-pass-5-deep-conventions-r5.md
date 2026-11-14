# Pass 5 deepening, round 5: verification round (hylo-legacy)

- **Source:** `$HOME/Dev/hylo/legacy/` (read-only, static). Re-read this round: `claude-dgx:36,80` and `dgx_proxy.py:4,560-561,645,710-715,753`
  (a grep for the CA path, cross-referencing ENV-I21). Nothing from `legacy/` was imported or executed.
- **Authorized read-only reference:** mitmproxy 12.3.1, `m/` = `$PROTOTYPE/.mitmenv/lib/python3.12/site-packages/mitmproxy/`
  (`m/version.py:5` `VERSION = "12.3.1"`). It was read as text only and never imported. **Every command stayed inside `m/`.** No `ls`, grep or read
  touched the parent `site-packages`, `mitmproxy_rs`, `pyvenv.cfg` or any other venv file.
- **Orchestrator evidence, recorded as confirmed (not read by this round):** the prototype venv's `pyvenv.cfg` reads
  `include-system-site-packages = false` (base: a uv-managed CPython 3.12, uv 0.12.23). Consequences in §A.4.
- **Inputs read:** pass-5 deep r4 (all) and r3 (all; §B is the consolidated base), step-c and `_shared-context`. **Pass-4 r6** appeared during this
  round (file time 03:35 local). It was read for its header, numbering and GODEBUG rows (§D). It was not edited. `CLAUDE.local.md` was not read.
- **Method:** fresh scripts in `scratchpad/p5r5/`: `dst5/gen5.py` (new grid; transitions found from libc `localtime` under each `TZ`, the same
  database the oracle uses), `dst5/go/` (`time.Date`, a fresh CPython `_mktime` port, and a rule check), `dst5/noshort/` (Go's `time.Date` offset
  logic reimplemented with and without the zero-offset shortcut), `usite5/run.sh` (user-site probe). Interpreters: CPython 3.11.7
  (`/opt/homebrew/anaconda3`) and 3.9.6 (`/usr/bin`, Xcode framework), run under `env -i`, with `-I` wherever a script read scratch data. Go 1.26.5
  darwin/arm64, `GOFLAGS=-mod=mod GOTOOLCHAIN=local`. **No socket was opened, no name was resolved, no proxy ran, no process was left running, and no
  file was created in the hylo repo.**
- **Numbering:** no retraction (CONV-ABS-97..100 unused). No owner items (OD-106..OD-109 unused). No new IDs. **[exec]** = executed this round.
  Cite prefixes as in r3: `SL` `PX` `HK` `EX` `BF` `LN` `CO` `PF`, plus `m/`.

---

## A. Re-verification of round 4's new items

### A.0 Verification table

| # | Round-4 item | Fresh evidence (round 5) | Verdict |
|---|---|---|---|
| V1 | **CONV-ABS-89**: the exact DST mismatch rule. Gap: Go ≠ Python iff the wall, read as UTC, is before `T` (probe offset = `oᵦ`). Overlap: Go ≠ Python iff the wall, read as UTC, is at or after `T` (probe offset = `oₐ`). Corollaries: all gap walls differ if `oₐ ≤ 0`, none if `oᵦ ≥ 0`; all overlap walls differ if `oₐ ≥ 0`, none if `oᵦ ≤ 0`; straddling transitions split at `T` | **[exec]** New grid: **19 zones, 37 transitions, 1,516 rows**, including Atlantic/Azores 2026, America/Scoresbysund 2023+2024, America/Chicago, Europe/London, and 15 others (Berlin, Dublin, Sydney, Lord_Howe, St_Johns, Chatham, Santiago, Casablanca, Troll, Havana, Tehran 2021, Nuuk 2023, Apia 2011, Kiritimati 1994, Kwajalein 1969). 3.11.7 = 3.9.6 byte for byte. `datetime(...).timestamp()` = `strptime().timestamp()` = `fromisoformat().timestamp()` on every row. Libc transition instants and offsets equal Go's on all 37 transitions. `time.Date` mismatched **339** rows (188 of 435 gap walls, 151 of 281 overlap walls, 0 of 800 ordinary walls). **Rule exceptions: 0** (probe-offset form), **0** (wall-read-as-UTC-vs-`T` form). **Fresh `_mktime` port: 0 mismatches.** Per-zone results in §A.1 | **Confirmed** (plus the first executed straddling overlap, §A.1) |
| V2 | Corollary: Go's zero-offset shortcut (`time.go:1760`) never changes the outcome | **[exec]** `noshort/` reimplements `time.go:1759-1768` with `ZoneBounds`. With the shortcut it equals `time.Date` on 1,516 / 1,516 rows. Removing the shortcut changes **0** results, and the mismatch count stays 339. The grid has 62 transition walls whose probe offset is 0: Azores and Scoresbysund overlaps (probe = `oᵦ` = 0, no mismatch), and London, Dublin, Casablanca and Troll overlaps (probe = `oₐ` = 0, all mismatch) | **Confirmed** (now executed, previously derived) |
| V3 | **ENV-I21**: `HOME` selects mitmproxy's `confdir`. `config.yaml` overrides `--set flow_detail=1` but not `--listen-port`/`-s`. A CA is generated when missing | Source re-read (cites in §A.2). Order in `run()`: `opts.set(*args.setoptions, defer=True)` **`m/tools/main.py:85`**, then `load_paths(confdir/config.yaml, confdir/config.yml)` **`:86-90`**, then `process_options` **`:91`** (definition `:23-39`: `opts.update` of every argparse value that is not `None`, `:36-39`). `load` → `opts.update_defer(**data)` (`m/optmanager.py:548-561`), so the YAML value overwrites the `--set` value whether `flow_detail` is already registered or still deferred (`:337-340`, `:240-242`, `:349-362`). `--listen-port` (`m/tools/cmdline.py:63`) and `-s` (`:54`) are argparse `store` / `append` options with no default (`m/optmanager.py:448-456,467-476`), so given on the command line they are non-`None` and win at `:91`. `--flow-detail` (`cmdline.py:129`) is not passed by legacy, so it stays `None` and does not override the YAML. CA: `CertStore.from_store` creates the store when `mitmproxy-ca.pem` is missing (`m/certs.py:615-618`); `create_store` makes the directory (`:656`), generates a key and CA (`:663`) and writes `-ca.pem`, `-ca.p12`, `-ca-cert.pem`, `-ca-cert.cer`, `-ca-cert.p12` (`:668-700`), with umask `\|0o77` for the key files (`:639-650`). Called from `m/addons/tlsconfig.py:509-517` with `os.path.expanduser(ctx.options.confdir)` | **Confirmed + 3 refinements, 2 cite corrections** (§A.2) |
| V4 | **ENV-I19** list (r4 §B) | **[exec]** (text search) Same patterns as r4 over `m/`, excluding `m/test/` (254 `.py` total, 3 in `test/`, 251 searched). Hits: `m/log.py:73,81`; `m/flowfilter.py:59`; `m/tools/console/master.py:115,117,172-174`; `m/net/tls.py:148`; `m/utils/asyncio_utils.py:46`; `m/utils/debug.py:110,124`. **Exactly r4's set**, with the same path classification: `flowfilter` is imported by `m/addons/dumper.py:16`; `MitmLogHandler` (`m/log.py:70`) is the base of `TermLogHandler` (`m/addons/termlog.py:37`) and `ErrorCheckHandler` (`m/addons/errorcheck.py:49`); the debug handlers are installed at `m/tools/main.py:65` → `m/utils/debug.py:128-131` (non-`nt`); `EDITOR`/`PAGER`/`MITMPROXY_EDITOR` appear only under `m/tools/console/` | **Confirmed** (one wording refinement: `asyncio_utils.py:46` is also gated by `__debug__`, so `PYTHONOPTIMIZE` would disable it; the `PYTHON*` class is already unset by ENV-I6..I9) |
| V5 | **V1 refinements**: `-E` with `PYTHONNOUSERSITE=1` does not stop the user site; load order user `.pth` → `sitecustomize` → `usercustomize` | **[exec]** New probe (`usite5/run.sh`). Scratch `HOME` per interpreter; user site resolved by `site.getusersitepackages()`: 3.11.7 `~/.local/lib/python3.11/site-packages`, 3.9.6 `~/Library/Python/3.9/lib/python/site-packages`. A `.pth`, a `usercustomize.py`, and a `sitecustomize.py` placed in a `PYTHONPATH` "shim" directory. Neither interpreter has a base `sitecustomize`/`usercustomize`. Results, the same on both versions: plain → `USER_PTH SITECUSTOMIZE(shim) USERCUSTOMIZE BODY`; `-s` → `SITECUSTOMIZE(shim) BODY`; `PYTHONNOUSERSITE=1` → `SITECUSTOMIZE(shim) BODY`; **`-E` + `PYTHONNOUSERSITE=1` → `USER_PTH USERCUSTOMIZE BODY`** (user site ran, and the shim did **not** load); `-I` → `BODY`; `-s -E` → `BODY`. Source order: `site.main()` 3.11.7 `site.py:602` `addusersitepackages` (`.pth`), `:609` `execsitecustomize`, `:610-611` `execusercustomize`; 3.9.6 `site.py:607,614,615-616`. `check_enableusersite` returns `False` on `sys.flags.no_user_site` (3.11.7 `:242-243`; 3.9.6 `:224-225`) | **Confirmed + 1 refinement** (§A.3) |
| V6 | ENV-I20 component scope (r4 V2): PX/PF unaffected **only if** `pyvenv.cfg` has `include-system-site-packages = false` | Orchestrator evidence: it does. 3.11.7 `site.py:539` (`ENABLE_USER_SITE = False` in the `venv()` else branch) is the mechanism; the venv base is CPython 3.12, whose `site.py` was not read here, so the mechanism on 3.12 is inferred from 3.9.6/3.11.7 (`site.py:544` / `:539`), which share it | **Confirmed** (closes r4 Remaining Gap 1) |

Verdicts: **6 of 6 confirmed**. V3 and V5 carry refinements. V3 also corrects two line cites. No retraction.

### A.1 DST grid per transition (executed)

`gapM`/`ovlM` = walls that mismatch. "pred" = what the rule predicts. Each row is one transition key (Casablanca's two 2026 `+1 → 0` transitions
are merged).

| Zone, `oᵦ → oₐ` (s) | gap walls / mismatch | overlap walls / mismatch | Rule says | Exceptions |
|---|---|---|---|---|
| Atlantic/Azores −3600 → 0 | 8 / 8 | — | gap, `oₐ ≤ 0`: all | 0 |
| Atlantic/Azores 0 → −3600 | — | 8 / 0 | overlap, `oᵦ ≤ 0`: none | 0 |
| America/Scoresbysund −3600 → 0 (2023) | 8 / 8 | — | all | 0 |
| America/Scoresbysund 0 → −3600 (2023) | — | 8 / 0 | none | 0 |
| America/Scoresbysund −3600 → −7200 (2024) | — | 8 / 0 | none | 0 |
| America/Chicago, St_Johns, Havana, Nuuk 2023, Santiago (spring), Apia (Sept 2011) | 8 / 8 each | — | all | 0 |
| America/Chicago, St_Johns, Santiago (autumn), Apia (Apr 2011) | — | 8 / 0 each | none | 0 |
| Europe/London, Dublin 0 → +3600; Berlin, Sydney, Lord_Howe (5), Chatham, Casablanca, Tehran, Troll (14) gaps | all / 0 | — | gap, `oᵦ ≥ 0`: none | 0 |
| Europe/London, Dublin +3600 → 0; Berlin, Sydney, Lord_Howe (5), Chatham, Tehran overlaps; Casablanca (16), Troll (14) | — | all / all | overlap, `oₐ ≥ 0`: all | 0 |
| Pacific/Apia −36000 → +50400 (Dec 2011, straddling gap) | 148 / 62 | — | walls before `T` only | 0 |
| Pacific/Kiritimati −36000 → +50400 (1994, straddling gap) | 148 / 62 | — | walls before `T` only | 0 |
| **Pacific/Kwajalein +39600 → −43200 (1969, straddling overlap)** | — | **142 / 68** | walls at or after `T` only | 0 |

Totals: 1,516 rows, 339 mismatches, 0 exceptions, `_mktime` port 0 mismatches. **New coverage:** round 4's grid (18 zones) had no straddling
transition at all. Round 3's had straddling gaps but no straddling overlap, so r4 §A.2's "straddling overlaps differ for walls at or after `T`" was
derived until now. Kwajalein 1969 confirms it (68 of 142 repeated walls, exactly the ones at or after `T`).

**Pin-wording refinement (wording only):** r4's corrected pin says "a zone whose **spring** transition ends at offset ≤ 0" and "a zone whose
**autumn** transition ends at offset ≥ 0". Southern-hemisphere zones and negative-DST zones (Casablanca's Ramadan `+1 → 0`, Dublin's tzdata
encoding) make "spring"/"autumn" ambiguous. Restated: **(a) a zone whose clock-forward (gap) transition ends at offset ≤ 0** (any US zone, Azores)
and **(b) a zone whose clock-back (overlap) transition ends at offset ≥ 0** (London, Berlin, Sydney, Casablanca). Executed evidence for both: Chicago
8/8 and London 8/8 above.

### A.2 ENV-I21 refinements (source)

1. **Cite corrections.** r4 cited `m/tools/main.py:84` for `--set` and `:85-89` for `load_paths`. The correct lines are **`:85`** and **`:86-90`**.
   r4 §D.3 described pass-2 r6/r7's `tools/main:86-90` as a one-line offset from r4. In fact **pass-2's cite is the correct one**, and r4's was off by
   one. r4's `m/optmanager.py:346` ("`--set` applied first") should be `:347` (`self.update(**processed)`; `:346` is the comment). No claim changes.
2. **`config.yaml` can also move the CA store.** `confdir` is itself an option (`m/options.py:48-53`). A `confdir:` key in `config.yaml` is applied
   by `update_defer`. `TlsConfig.configure` rebuilds the cert store when `"confdir" in updated` (`m/addons/tlsconfig.py:500-517`), so mitmdump
   would issue leaf certificates from a CA **other than** the one the launcher tells Claude Code to trust: `LN:80`
   `NODE_EXTRA_CA_CERTS="$HOME/.mitmproxy/mitmproxy-ca-cert.pem"` (and the trust CLI's `PX:560-561` `Path.home() / ".mitmproxy"`). The path
   coupling itself is old (r1 ENV-41 lists `LN:80`). What is new is that ENV-I21 is the input that can break it. Production has no `config.yaml`
   (pass-2 r6), so this is a harness and robustness note, not a legacy behavior change.
3. **More files under `confdir`.** `CertStore.load_dhparam` writes `mitmproxy-dhparam.pem` from the constant `DEFAULT_DHPARAM` when missing
   (`m/certs.py:583-587`). It is deterministic, but a pre-seeded fixture `confdir` should include it so the directory does not change during a case.
   `CommandHistory` (a default addon, `m/addons/__init__.py:44`, loaded by `DumpMaster` `m/tools/dump.py:19`) reads `confdir/command_history` if
   present (`m/addons/command_history.py:27-39`). It writes only at ≥ 1,024 entries (`:41-48`) or on console commands. **Inert** for mitmdump
   output.

Not executed: the precedence and CA generation are from source only. Executing them would mean importing mitmproxy, which is outside this round's
authorization.

### A.3 ENV-I20 refinement (executed)

`-E` ignores **every** `PYTHON*` variable, so it drops `PYTHONPATH` as well as `PYTHONNOUSERSITE`. Under `-E` the clock shim (`sitecustomize` via
`PYTHONPATH`) does not load **and** the user site still runs: the worst of both. r4 noted the `PYTHONNOUSERSITE` half and noted that `-I` drops the
shim. The `-E` shim loss was not stated.

**Harness rule, restated from the executed table:** the orchestrator's summary "SL, HK, BF, the trust CLI and EX run under `-s` or `-I`" holds for
**unshimmed** cases. **Shimmed cases must use `-s`** (with `PYTHONPATH` = the shim directory). `-I` and `-E` both lose the shim. A temp `HOME` is an
equivalent alternative (and already part of every pin set). If `-I` is wanted for shimmed cases anyway, the only route is a wrapper script that
installs the shim and then runs the target with `runpy.run_path(..., run_name="__main__")`. That changes `sys.argv[0]`, `__file__` and `sys.path[0]`,
so it would need its own parity check. This is a note, not a recommendation.

### A.4 ENV-I20 scope, now final

| Component | Interpreter | User site runs in production? | Harness |
|---|---|---|---|
| PX (`LN:75`, `CO:31`), PF invisible (`LN:61`) | `.mitmenv` venv, base CPython 3.12 (`include-system-site-packages = false`) | **no** (orchestrator evidence; mechanism `site.py` `venv()`) | no flag needed |
| SL (`LN:176-177`), HK (`LN:161`), trust CLI (`LN:13`) | `python3` → 3.11.7 | **yes** (no `-s`/`-I`) | `-s` (shimmed) or `-s`/`-I` (unshimmed), or temp `HOME` |
| BF | 3.11.7 | yes | same |
| EX (plist `/usr/bin/python3`) | 3.9.6 | yes | same |
| PF visible mode (`LN:62`, dead, D6) | `python3` | yes | not tested (dead mode) |

---

## B. Updates to the consolidated artifacts (r3 §B stays the base; r4 §D and these r5 changes apply on top)

### B.1 Explicit env table

**No change.** 43 explicit inputs; 33 map to a key; 10 have none; 3 keys have no legacy env.

### B.2 Implicit inputs: 21 IDs (r4 + r5 changes only)

| ID | Change | Src |
|---|---|---|
| ENV-I1 `TZ` | pin: "one zone whose **clock-forward (gap)** transition ends at offset ≤ 0, one whose **clock-back (overlap)** transition ends at offset ≥ 0" (r4 CONV-ABS-89 wording, made hemisphere-neutral) | R1, R3, R4, **R5** |
| ENV-I10 `PATH` | + `grep`, `basename`, `sleep`, `mkdir` | R1, R4 |
| ENV-I6..I9 `PYTHON*` | note: `PYTHONOPTIMIZE` would also flip mitmproxy's `__debug__`-gated read (`m/utils/asyncio_utils.py:46`); already unset | R1, R2, **R5** |
| ENV-I19 | on the mitmdump path: `MITMPROXY_CASE_SENSITIVE_FILTERS`, `PYTEST_CURRENT_TEST`, `MITMPROXY_DEBUG_EXIT` (+ the ENV-I17 pair); console-only: `MITMPROXY_EDITOR`, `EDITOR`, `PAGER`. All inert. Re-verified: identical hit set | R2, R4, **R5** |
| ENV-I20 | PX/PF exclusion **confirmed** (venv `include-system-site-packages = false`, orchestrator evidence). Pin: temp `HOME`, or `-s`. Not `-E` (loses the shim **and** keeps the user site). `-I` only for unshimmed cases | R3, R4, **R5** |
| ENV-I21 | cites corrected (`m/tools/main.py:85`, `:86-90`, `:91`); `config.yaml` can also set `confdir`, moving the CA away from the `LN:80` trust path; fixture `confdir` = CA files + `mitmproxy-dhparam.pem`, no `config.yaml`, no `command_history` | R4, **R5** |

Final implicit count: **21 IDs** (ENV-I1..ENV-I21) plus the `PYTHONHASHSEED` negative row.

### B.3 Determinism inventory

**54 rows, unchanged.** Go-side pins GP-1..GP-6, unchanged except one wording refinement. **GP-2**: "`GODEBUG` unset; `go.mod` `godebug` lines **and
`//go:debug` directives** reviewed". The source is pass-4 r6 §B: `http2server`/`http2client` have no version-gated default, `go/src/internal/godebugs/table.go:44,46`,
and a `//go:debug` directive is a process-wide alternative, r6 l.112. PR-14's golden count grows: 4,132 + 3,096 + 2,149 + **1,516** rows (the r5 grid
adds the first straddling overlap).

### B.4 Pin sets

- **P1 status line**: `TZ` = UTC plus a zone whose clock-forward transition ends at ≤ 0 and one whose clock-back transition ends at ≥ 0 (America/Chicago
  + Europe/London). Interpreter flags for shimmed cases: `-s` (or temp `HOME`), never `-E`/`-I`.
- **P3 proxy**: temp `HOME` with a pre-seeded fixture `confdir` (`mitmproxy-ca.pem`, `mitmproxy-ca-cert.pem` and siblings, `mitmproxy-dhparam.pem`; no
  `config.yaml`, no `command_history`). Point `NODE_EXTRA_CA_CERTS` at the same fixture if a client is in the loop. No user-site flag needed (venv).
- P2, P4 hook, P4 launcher, Go side, Windows: unchanged from r3 §B.4 and r4 §D.2.

### B.5 Conventions

**19, unchanged.**

### B.6 Pitfall register

**22 entries, 22 tags, unchanged in number.** PR-14 wording (from r4, re-verified): "differs in a gap when the wall, read as UTC, precedes the transition
(every gap wall if the post-transition offset is ≤ 0), and in an overlap when it is at or after the transition (every repeated wall if the
post-transition offset is ≥ 0); straddling transitions split at the transition instant". Test: committed CPython goldens, now 10,893 rows across four
grids, `_mktime` port 0 mismatches on all of them. PR-15, PR-22: unchanged from r4.

### B.7 Final counts

| Artifact | Count |
|---|---|
| Explicit env inputs | **43** |
| Implicit env inputs | **21 IDs** (ENV-I1..I21) + 1 negative row |
| Determinism rows | **54** (+ 6 Go-side pins GP-1..GP-6) |
| Conventions | **19** |
| Pitfall entries / tags | **22 / 22** |

---

## C. Is anything in pass 5 still open?

**No analytical item is open.** What remains is owner decisions plus things this environment cannot or may not run:

- **Cannot be executed here:** Windows (`USERPROFILE`, `ntpath`, goldens on Windows CI); amd64 (FMA absence and `CVTTSD2SQ` behavior come from
  cross-compiled listings and the instruction definition); Python 3.12.10 (the URL port grammar is bracketed by 3.11.7 and 3.12.13).
- **Not executable under this round's rules (no network, no mitmproxy import):** DET-53 resolver latency and launchd ordering; ENV-I21 precedence and CA
  generation (source-verified, not run).
- **Outside authorization (reading, not execution):** environment reads inside mitmproxy's native extensions (`mitmproxy_rs`, `mitmproxy_macos`) and its
  third-party dependencies (`certifi`, `pyOpenSSL`, `cryptography`, `aioquic`, `tornado`, `ruamel.yaml`). This is the one gap that is neither an owner
  decision nor a platform limit. It does **not** affect harness correctness, because DET-43 builds the oracle's environment from scratch, so any such
  variable is unset. It affects only the completeness of the inventory's list of variable names.
- **Owner-conditional:** DET-54 and the PR-15 `SL:889/919` occurrence (OD-14).
- **Owner decisions carried:** OD-74, OD-75, OD-76, OD-58..OD-61, OD-14, OD-01, OD-05.

---

## D. Sibling reconciliation

| Sibling | Item | State |
|---|---|---|
| pass-2 r6 / r7 | `config.yaml` load at `tools/main:86-90` | **pass-2's cite is correct**; r4's was off by one (§A.2 item 1). No content conflict |
| pass-4 r6 §B (GODEBUG, `omithttp2`) | `http2server`/`http2client` names, no version-gated default; `//go:debug` as a global switch | consistent with GP-2; GP-2 wording now names `//go:debug` (§B.3). Pass-4 r6 numbering (CONV-ABS-93/94, OD-102..105 unused) does not collide with this round (nothing used from 97-100 or OD-106..109) |
| pass-4 r6 header | "Pass-5 deep r4 did not exist when this round ran" | consistent: pass-4 r6 makes no pass-5 claim that this round changes |
| r1 ENV-41 | `LN:80` `NODE_EXTRA_CA_CERTS` under `HOME` | linked to ENV-I21 (§A.2 item 2); no new input |

---

## Delta Summary

| Area | New (R5) | Refined / confirmed |
|---|---|---|
| Verification | 6 checks, 6 confirmed | CONV-ABS-89 rule: 0 exceptions on a new 1,516-row, 19-zone grid; `_mktime` port 0 mismatches; zero-offset shortcut executed (0 outcome changes); ENV-I21 precedence and CA generation re-read; ENV-I19 identical hit set; `-E`/order probe on both versions; venv exclusion confirmed |
| Coverage | first executed **straddling overlap** (Kwajalein 1969, 68/142) | r4 grid had no straddling transition |
| Env inventory | — | ENV-I21 (cite fixes; `confdir` key can move the CA off the `LN:80` trust path; dhparam and `command_history` files); ENV-I20 (`-E` also drops the shim; shimmed cases need `-s`; scope table final); ENV-I1 pin made hemisphere-neutral; ENV-I6..I9 `PYTHONOPTIMIZE` note |
| Determinism | — | GP-2 names `//go:debug` (from pass-4 r6); PR-14 goldens +1,516 |
| Retractions | none (CONV-ABS-97..100 unused) | three line-cite errata in r4 (`m/tools/main.py:84→85`, `:85-89→86-90`, `m/optmanager.py:346→347`), no claim changed |
| Owner items | none (OD-106..OD-109 unused) | — |

New items: 0 inputs, 0 conventions, 0 pitfall occurrences, 0 determinism rows. Existing items refined: 6 (ENV-I1, ENV-I6..I9, ENV-I20, ENV-I21, GP-2,
PR-14 goldens).

## Remaining Gaps (verbatim-carryable)

1. Environment reads in mitmproxy's native extensions (`mitmproxy_rs`, `mitmproxy_macos`) and third-party dependencies (`certifi`, `pyOpenSSL`,
   `cryptography`, `aioquic`, `tornado`, `ruamel.yaml`) were not searched (outside authorization). Harness-neutral under DET-43.
2. Not executable here: Windows, amd64 runs, Python 3.12.10 runs; DET-53 latency and launchd ordering (no network); ENV-I21 precedence and CA
   generation (source only, no mitmproxy import).
3. DET-54 and the `SL:889/919` occurrence matter only if OD-14 keeps the `--subagent` path.
4. Owner decisions carried: OD-74, OD-75, OD-76, OD-58..OD-61, OD-14, OD-01, OD-05.

(r4 Remaining Gap 1, `pyvenv.cfg`, is closed by orchestrator evidence.)

## Novelty Assessment

Novelty: NITPICK — findings are refinements, not gaps.

All six round-4 items survive fresh, independent checks. Five were re-executed or re-read from new scripts: the DST rule (0 exceptions, 1,516 rows,
19 zones), the shortcut (0 changes), ENV-I21 from source, the ENV-I19 hit set, and the user-site switches on both versions. The sixth was closed by
orchestrator evidence. This round found no new input, convention, pitfall occurrence or determinism row, and it retracts nothing. The additions are
three kinds of refinement:
- **Coverage:** the first executed straddling overlap. It confirms a rule row that r4 had derived.
- **Wording and cites:** ENV-I1 made hemisphere-neutral; three r4 line cites corrected, with the claims unchanged; GP-2 names `//go:debug`.
- **Pin detail within existing inputs:** ENV-I20, where `-E` also drops the shim, so shimmed cases need `-s`. ENV-I21, where a `confdir` key can
  move the CA, and the fixture `confdir` contents are now specified.

Removing these findings would not change how the system is specified. The closest call is ENV-I21 item 2, where a `config.yaml` `confdir` key splits
the CA from the `LN:80` trust path. It is a consequence of r4's already-stated "config.yaml can change any option", applied to one option. It is not a
new input. The three cite corrections fix line numbers only; the statements they support are unchanged. If the orchestrator counts cite corrections
as retractions, this verdict would flip, so they are listed explicitly in the Delta Summary.

## Convergence Declaration

Pass 5 has converged — findings are nitpicks, not gaps.

## State Checkpoint

```yaml
pass: 5
round: 5
status: complete
files_scanned: 9   # legacy claude-dgx + dgx_proxy.py (CA-path grep); mitmproxy 12.3.1 tools/main.py, tools/cmdline.py, optmanager.py, options.py, certs.py, addons/{tlsconfig,command_history,__init__,dumper,termlog,errorcheck}.py, tools/dump.py, log.py, flowfilter.py, net/tls.py, utils/{debug,asyncio_utils}.py (+ env grep of 251 files); CPython 3.11.7/3.9.6 site.py and datetime.py; Go 1.26.5 time/time.go
timestamp: 2026-11-14T09:40:14Z
novelty: NITPICK
counts: {env_explicit: 43, env_implicit_ids: 21, determinism_rows: 54, go_side_pins: 6, conventions: 19, pitfall_entries: 22, tags: 22}
verification: {checks: 6, confirmed: 6, refined: 2, retracted: 0, cite_errata: 3}
probes: [dst5/gen5.py, dst5/go, dst5/noshort, usite5/run.sh]
dst_grid: {zones: 19, transitions: 37, rows: 1516, date_mismatch: 339, rule_exceptions: 0, port_mismatch: 0, shortcut_changes: 0}
retractions: []
owner_items: []
unused: {conv_abs: [CONV-ABS-97, CONV-ABS-98, CONV-ABS-99, CONV-ABS-100], od: [OD-106, OD-107, OD-108, OD-109]}
sibling_disagreements: []
network: none (no socket bind, no DNS)
next: none for pass 5 (converged); carry Remaining Gaps 1-4 to the pass-8 synthesis
```
