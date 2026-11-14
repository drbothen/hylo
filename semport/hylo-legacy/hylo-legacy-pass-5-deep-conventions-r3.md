# Pass 5 deepening, round 3: verification and consolidated pass-5 artifacts (hylo-legacy)

- **Source:** `$HOME/Dev/hylo/legacy/` (read-only). Re-read this round: `dgx_statusline.py:140-150,278-283,553-562,660-690,880-930`,
  `dgx_proxy.py:78-84`, `dgx_preflight.py:15-24`, `tools/backfill_cost_history.py:25-121`, `dgx_ledger_exporter.py:19,25,406,413-414`,
  `claude-dgx:1,13,61,75,158-162,174-178` plus a variable census of the whole file, `dgx-proxy-coordinator.sh:1`, both plists. An `ast.parse` scan
  (text only, nothing imported) covered every legacy `.py` file.
- **Inputs read:** pass-5 broad sweep, deep r1 (all), deep r2 (all). Pass-4 deep r3 was read twice: once at 03:00, then again at 03:02 local after it
  had been updated to adopt the pass-5 r2 key table. Also read: pass-1 deep r3 V1, pass-0 deep r3 row 12, and step-c/_shared-context. Sibling files
  were not edited. `CLAUDE.local.md` was not read.
- **Method:** fresh scripts in `scratchpad/p5r3/`: `dst3_gen.py` + `gomk3/`, `fma3_gen.py` + `gofma3/`, `gofmashape/`, `gosl/`, `gosub/`, `godur3/`,
  `mktime3.py`, `urlport3.py`, `fma_sites.py`, `zsh3/`, `usite/`. Interpreters: CPython 3.11.7 (`/opt/homebrew/anaconda3`), 3.9.6 (`/usr/bin`), plus
  Homebrew 3.12.13 and 3.13.14 for the port grammar only. Go 1.26.5 darwin/arm64 with `GOFLAGS=-mod=mod GOTOOLCHAIN=local`. amd64 and the other
  targets were **cross-compiled and inspected only, never run**. Fusion counts come from the compiler's `-gcflags=-S` listing, because
  `go tool objdump` misdecodes VEX instructions (§A.2). **No socket was opened, no name was resolved, no proxy ran.** The DET-53 and PR-22 network
  claims rest on stdlib source reading only. Nothing from `legacy/` was executed. No process was left running.
- **Numbering:** retraction **CONV-ABS-77** (78-80 unused). Owner items: **none new** (OD-86..OD-89 unused). New IDs: `ENV-I20`, `DET-54`, Go-side
  pin rows `GP-1..GP-6`. Row-source tags: **R1**/**R2**/**R3** = the round that last changed the row.
- **Line cites:** `SL` = `dgx_statusline.py`, `PX` = `dgx_proxy.py`, `HK` = `auto_continue.py`, `EX` = `dgx_ledger_exporter.py`, `BF` =
  `tools/backfill_cost_history.py`, `LN` = `claude-dgx`, `CO` = `dgx-proxy-coordinator.sh`, `PF` = `dgx_preflight.py`. **[exec]** = executed this round.

---

## A. Verification of round 2's results (fresh scripts)

### A.0 Verification table

| # | Round-2 claim | Fresh evidence (round 3) | Verdict |
|---|---|---|---|
| V1 | `time.Date` disagrees with Python on **46 / 3,096** naive times. West-of-UTC zones differ in the spring gap and east-of-UTC zones in the repeated hour | **[exec]** (a) A fresh Go program (`gomk3`) run on round 2's grid file reproduces **46 / 3,096** with the same per-zone split (Chicago 8, St_Johns 8 at −3600; Berlin 8, Sydney 8, Chatham 9 at +3600; Lord_Howe 5 at +1800). (b) A **new sample**: 4,132 naive times, 17 zones, years 2025/2027 plus historical offset changes. Python 3.9.6 and 3.11.7 are byte-identical, and `strptime().timestamp()` equals `fromisoformat().timestamp()` on all rows. `time.Date` mismatches 713. The rate depends on how densely edges are sampled; the pattern does not: **every gap mismatch is in a zone whose pre-transition offset is negative**, and **every overlap mismatch is in a zone at offset ≥ 0**. That includes the zero-offset zones (London, Dublin: +3600) and Casablanca (+1 → 0). | **Confirmed, generalized** (§A.1) |
| V2 | A port of CPython `_mktime` matches **3,096 / 3,096** | **[exec]** A fresh port, written from the 3.11.7 `Lib/datetime.py` `_mktime` source printed this round, gives **0 mismatches on 3,096 (round-2 grid) and 0 on 4,132 (new grid)**. The new grid includes 24 h day skips (Pacific/Apia 2011, Pacific/Kiritimati 1994) and non-DST offset changes (Moscow 2011/2014, Pyongyang 2015/2018, Caracas 2007/2016) | **Confirmed** |
| V3 | Backfill FMA on darwin/arm64: `FMADDD` present; the `float64()` wrap gives 0 differences | **[exec]** New generator (log-uniform tokens, 25,000 sessions, 2,015,604 messages). Naive form: **1 `FMULD` + 4 `FMADDD`**, 99,124 message bit-differences, 280 session bit-differences, max 1.42e-14, **0** `round(usd,4)`/text/`MIN_USD` differences. Guarded form: **5 `FMULD` + 4 `FADDD`, 0 differences of any kind**. linux/arm64 and windows/arm64 also emit 4 `FMADDD` (listing) | **Confirmed** (counts are sample-specific) |
| V4 | `GOAMD64=v1` does not fuse; `GOAMD64=v3` does (4 `VFMADD231SD`) | Compiler listings (`-S`), cross-compiled. v1: no fused instruction in any shape. v3: **fuses only `a*b + c` with both multiply operands in registers** (round 2's by-value struct: 4; `usd += …`: 1). It does **not** fuse when an operand is loaded from memory (pointer/array/map-held prices: 0, because the load folds into `MULSD mem`), and **never fuses subtraction** (the AMD64 rules have only `ADDSD (MULSD …)`, `AMD64.rules:1521`). So colorsys, the ⌂ gate and SL:919 never fuse on any amd64 level | **Narrowed: CONV-ABS-77** (test placement changes, §A.2) |
| V5 | colorsys fused (2 `FMSUBD` + 1 `FNMSUBD`); the ⌂ gate fused across statements; sparkline lines not | **[exec]** Fresh transliterations (`gosl`), arm64 listing: `hsvToRGB` 2 `FMSUBD` + 1 `FNMSUBD`; `windowAge` 1 `FNMSUBD`. The gate fuses **even though `win_ms` is reused for the text**: the compiler emits both an `FNMSUBD` (gate) and a separate `FMULD` (`wm`), so the gate and the text see different values within one render. Not fused: `idx` with `math.Min`, with `if`, or with builtin `min`, and `fade` | **Confirmed + refinement** |
| V6 | PR-15 site list complete | `ast` scan of all legacy `.py` for `x*y ± z` (direct and through one assignment): BF:75, SL:559 (from :558), **SL:919 (from SL:889)**, BF:95. BF:95 `time.time() - a.days*86400` is an int product (exact), so it is not a hazard. **SL:889/919 is new [exec]**: one displayed `MM:SS` difference in 20,000,000 random cases, plus a directed case (`now=1790000000.5009999`, `start=1789999939501`). Naive arm64 Go shows `01:00`; CPython 3.11.7 and 3.9.6 show `01:01`, as does the guarded Go form | **Refuted: new occurrence** (PR-15, DET-54) |
| V7 | PR-22: `http.Client.Timeout ≤ 0` means no timeout | Source, Go 1.26.5: `net/http/client.go:197-201` `if c.Timeout > 0` (otherwise zero deadline); doc `:96` "zero means no timeout". **New:** Go's knobs disagree on negative values. `Transport.ResponseHeaderTimeout` uses `> 0` (`transport.go:2920`). `net.Dialer.Timeout` uses **`!= 0` "including negative, for historical reasons"** (`net/dial.go:252`), so a negative value means an already-expired deadline, an immediate failure. `Transport.TLSHandshakeTimeout` also uses `!= 0` (`transport.go:1727`) | **Confirmed + refinement** |
| V8 | PR-22: float→`Duration` conversion of `inf`/NaN differs between arm64 and amd64 | **[exec]** arm64 run: `+Inf`, `1e10`, `9223372037` → `MaxInt64`; `-Inf` → `MinInt64`; NaN → `0`. Listings: arm64 `FCVTZSD` (saturating, NaN→0); amd64 `CVTTSD2SQ`, which returns the "integer indefinite" value `0x8000000000000000` = `MinInt64` for NaN and out-of-range inputs (reasoning check; not run). Go 1.26 has a staged alternative (`AMD64.rules:172-177`, gated by `-d=converthash`, **off by default**: `base/flag.go:271` "quietly disable"). It would map positive overflow to `MaxInt64` on amd64 but NaN (positive sign) still to `MaxInt64`, not 0. So the semantics are in flux upstream too. Combined with V7: NaN becomes "no dial timeout" on arm64 but "immediate dial failure" on amd64 when it reaches a `Dialer` | **Confirmed** |
| V9 | ENV-I18: zsh reads `$ZDOTDIR/.zshenv` (default `$HOME/.zshenv`) for `#!/bin/zsh` scripts | **[exec]** New scratch script with the same shebang as `LN:1`/`CO:1`. Clean HOME → nothing; `HOME/.zshenv` → `ARGS=(--from-home)` arrives; `ZDOTDIR` wins over HOME; `zsh -f` → nothing. **New detail:** `.zshenv` runs **after** the environment import, so it **overrides** an exported `ARGS`. `.zshrc` is not read (non-interactive). `/etc/zshenv` is absent; `/etc/zprofile` and `/etc/zshrc` exist but are not read by a script | **Confirmed** |
| V10 | ENV-I19: mitmproxy 12.3.1 reads only `MITMPROXY_CASE_SENSITIVE_FILTERS`, `EDITOR`, `PAGER` (+ the `SSLKEYLOGFILE` pair, ENV-I17) | No public copy of mitmproxy exists on this host (anaconda, Homebrew, system site checked), and the venv was not opened. The adoption from pass-1 r3 V1 is internally consistent: V1 searched `os.environ`, and the `SSLKEYLOGFILE` pair is read separately (pass-2 r7) | **Carried as adopted, not re-verified** |
| V11 | DET-20: macOS libc `mktime` switches to the second occurrence at **01:45:19** (Chicago, 2026-11-01) | **[exec]** Same on 3.11.7 and 3.9.6 (macOS 26.5.2), forward and reverse scan order. **Round-2 gap 5 closed:** the crossover is one switch per repeated interval, and its position depends on zone and year: Chicago 2025 01:53:51, New York 2027 01:51:59, Denver 2026 01:53:35, Berlin 02:40:31, London 01:40:31, Sydney 02:36:31, Lord_Howe 01:32:22 (1,800 s interval), Auckland 02:28:14. No result was neither occurrence | **Confirmed, generalized** |
| V12 | DET-53: the exporter does a resolver lookup at start | Source only (3.9.6 printed via `inspect`): `HTTPServer.server_bind` → `socket.getfqdn(host)`; for `"0.0.0.0"` → `gethostname()` then `gethostbyaddr(name)`. `TCPServer.__init__` calls `server_bind()`. `server_name` is never read by the exporter: the only handler override is `log_message` (`EX:406`), and `BaseHTTPRequestHandler` (3.9.6) contains no `server_name`/`getfqdn` | **Confirmed** (source) |
| V13 | URL port grammar: 3.9.6 accepts `+80`, ` 80`, Unicode digits; 3.11.7 rejects them | **[exec]** 17 cases. 3.9.6 also accepts **`80 ` (trailing space)** and **`1_0`** (→ 10), and reports `-1` as "out of range" rather than "could not be cast". Getter source: 3.9.6 `int(port, 10)`; 3.11.7 `port.isdigit() and port.isascii()`. **3.12.13 and 3.13.14 behave like 3.11.7 on all 17 cases.** That brackets the venv's 3.12.10 (3.11.7 < 3.12.10 < 3.12.13), which closes round-2 gap 1 by bracketing, not by running 3.12.10. No production path parses URLs on 3.9.6 (the exporter does not), so the lenient set is not reachable | **Confirmed + refinement** |
| V14 | 43 explicit inputs (27 Python + 22 launcher − 6) | `grep` census: 27 `os.environ` names, 0 `os.getenv`, one dead env write (`HK:153`). Launcher census (comments stripped): 13 never-assigned reads ∪ 19 `${X:-…}` defaults = 21 names, plus `ARGS`. Neither plist has `EnvironmentVariables` | **Confirmed** |
| V15 | (new hunt) implicit inputs complete at 19 | **[exec]** **ENV-I20:** CPython's **user site-packages under `HOME`** runs `.pth` files and `usercustomize.py` at start for every non-venv legacy entry point: 3.9.6 `~/Library/Python/3.9/lib/python/site-packages`, 3.11.7 `~/.local/lib/python3.11/site-packages`. Probe: both printed `PTH RAN` and `USERCUSTOMIZE RAN` before the script body; `-s` or `PYTHONNOUSERSITE=1` suppressed both. Production invocations pass neither flag (`LN:13,161,176-177`; exporter plist `/usr/bin/python3 <file>`). A default venv sets `ENABLE_USER_SITE = False` (3.11.7 `site.py:539`), so mitmdump and the preflight (`.mitmenv`, `LN:61,75`) are inferred unaffected (`pyvenv.cfg` not in the tree) | **New input** |

Verdicts: **9 confirmed** (V2, V3, V8, V9, V10 carried, V11, V12, V14, plus V1's reproduction), **4 refined** (V1 pattern, V5, V7, V13),
**1 narrowed by retraction** (V4, CONV-ABS-77), **2 new** (V6 occurrence, V15 input).

### A.1 Go `time.Date` versus Python for naive local times: the generalized rule

Go's `time.Date` treats the wall time as UTC, looks up the zone offset at that instant, and re-looks it up once if the result falls outside that
offset's period. In Go 1.26.5 the whole correction is skipped when the first offset found is 0. Compared with Python's fold-0 rule (`_mktime`:
earliest solution in an overlap, `max(u1, u2)` in a gap):

| Transition | Zone offset sign at the probe | Go vs Python | Observed (this round's grid) |
|---|---|---|---|
| gap (clock jumps forward) | negative (Americas; Apia/Kiritimati before their day skip) | Go is earlier by the jump: −3600, −1800 (Caracas 2016), **−86,400 (24 h day skip)** | New_York, Denver, Havana (midnight jump), Santiago, Nuuk, Caracas, Apia, Kiritimati |
| gap | ≥ 0 | equal | Berlin, Moscow 2011, Pyongyang 2018, Auckland, Adelaide, Troll spring |
| overlap (clock falls back) | negative | equal | New_York, Denver, Caracas 2007 |
| overlap | **≥ 0, including 0** | Go picks the **second** occurrence: +3600, +1800 (Pyongyang 2015, Lord_Howe), **+7200 (Troll)** | London, Dublin, Casablanca, Moscow 2014, Auckland, Adelaide, Troll, Berlin, Sydney |

Remedy unchanged from round 2: `pytime.LocalToUnix(loc, wall)` = a port of CPython `_mktime`, now verified on 7,228 cases (0 mismatches). Round 2's
grid had 6 transition zones plus 3 controls (America/Sao_Paulo and Asia/Tehran have no DST in 2026, and UTC has none); that is a wording refinement of
its "9 zones", with no numeric change.

### A.2 FMA: test placement corrected (CONV-ABS-77)

| Shape (naive Go) | darwin/linux/windows arm64 | amd64 v1/v2 | amd64 v3/v4 |
|---|---|---|---|
| `Σ a·p` with prices in registers (by value) | 4 `FMADDD` | 0 | **4 `VFMADD231SD`** |
| `Σ a·p` with prices via pointer/array/map (memory operands) | 4 `FMADDD` | 0 | **0** |
| `usd += (a·pi + o·po)/1e6` | 1 `FMADDD` | 0 | 1 |
| colorsys `h*6.0 - i`, `1.0 - s*f`, `1.0 - s*(1.0-f)` | 2 `FMSUBD` + 1 `FNMSUBD` | 0 | **0** (no amd64 subtract rule) |
| ⌂ gate `SL:558-559` | 1 `FNMSUBD` | 0 | **0** |
| subagent clock `SL:889`+`SL:919` | 1 `FNMSUBD` | 0 | **0** |

**CONV-ABS-77.** Retracted: round 2 §D.4's PR-15 test row "T on **darwin/arm64** and `GOAMD64=v3`", and §A.2's implication that v3 CI detects a
missing guard. v3 detects it only for addition shapes with register operands. It never detects the status line sites, and whether it detects the
backfill depends on how the port stores the prices. Corrected placement: **arm64 only** (any OS). GitHub's macOS runners are arm64, so the
CLAUDE.md "CI on all three OSes" rule already includes a detecting target. A tooling note for whoever audits this: `go tool objdump` misdecodes
VEX-encoded amd64 instructions (it printed garbage such as `MOVL $-0x36a8f03b, CX` where the listing shows `VFMADD231SD`). Count fused
instructions from `-gcflags=-S`. `-d=fmahash=n` exists as a compiler debug switch for bisecting, but it is not a remedy.

---

## B. Consolidated pass-5 artifacts for Phase 1

### B.1 Env-var table: 43 explicit inputs → D15 key → `HYLO_*` name

Rules (CV-19): dotted lower-snake keys under a component; every location under `paths.*`; secrets by `*_file`; legacy unit suffixes; a table with an
`.enabled` leaf **only where legacy has a toggle and the feature has settings** (pass-4 r3 §D.2a sweep). `HYLO_` + upper snake of the key (OD-01),
generated from the registry, never parsed back. `DGX_*` aliases keep the legacy parse and predicate (OD-59 (b)). `HYLO_*`/config values are typed
and validated (OD-05, OD-75). Agreement: **pass-4 r3 §D.2a adopted the r2 table, K-1 included**. A mechanical check over 136 keys (pass-4 r3 key
tokens ∪ this table) found **0 `HYLO_*` collisions and 0 real leaf-vs-table conflicts** (`statusline.cost`/`git`/`sparkline` appear as table names
in prose; the map keys `statusline.cost.rate_min_api_ms` and `statusline.queue.yellow` follow K-9).

| ID | Legacy env | Legacy default | Alias-path parse (reproduced) | Bad value in legacy | D15 key | `HYLO_*` name | Src |
|---|---|---|---|---|---|---|---|
| ENV-01 | `LOCAL_MODEL_PREFIXES` | PX `claude-sonnet` (`PX:86`); SL `""` (`:444`, `:902`); BF `claude-sonnet` (`:89`); LN forces it (`:38`) | `split(",")`, Python `strip()`, drop empty; `startswith` | empty → nothing local, pill `◨ ?` | `routing.local_model_prefixes` (one default `claude-sonnet`, K-7) | `HYLO_ROUTING_LOCAL_MODEL_PREFIXES` (comma list) | R1, R2 |
| ENV-02 | `DGX_SERVED_MODEL` | `claude-sonnet-5-5` (`PX:84`; LN `:39`) | raw | empty → no rewrite (`PX:146`) | `backend.served_model` | `HYLO_BACKEND_SERVED_MODEL` | R1 |
| ENV-03 | `DGX_UPSTREAM` | `http://192.0.2.10:8080` (`PX:79`, `PF:18`) | `urlparse` at import (`PX:80-83`, `PF:19-20`): `scheme or "http"`, `hostname or default`, `port or 80`; 3.11/3.12 port grammar = ASCII digits 0..65535 | `https://h` → port 80; schemeless → defaults; bad port → import crash (proxy, trust CLI, preflight) | `backend.url` | `HYLO_BACKEND_URL` | R1, R2, **R3** (grammar, §A.0 V13) |
| ENV-04 | `DGX_KEY_FILE` | `~/.config/dgx-llm/api-key` (`PX:88`) | literal path; content `strip()` | unreadable → P-R4 | `backend.api_key_file` | `HYLO_BACKEND_API_KEY_FILE` | R1 |
| ENV-05 | `DGX_OBS_LEDGER` | `~/dgx-llm-obs.jsonl` (`PX:54`, `EX:22`) | literal | writer swallows `OSError`; exporter E-09 | `paths.ledger` | `HYLO_PATHS_LEDGER` | R1 |
| ENV-06 | `DGX_PROXY_DECISIONS` | `~/dgx-llm-routing-decisions.log` (`PX:53`) | literal | swallowed | `paths.decision_log` | `HYLO_PATHS_DECISION_LOG` | R1 |
| ENV-07 | `DGX_TRUST_STATE` | `~/.dgx/trust-state.json` (`PX:563`) | `Path(env)` | raises | `paths.ca_state` | `HYLO_PATHS_CA_STATE` | R1 |
| ENV-08 | `DGX_PROXY_RESTART_CMD` | unset (`PX:719`) | `shell=True` | any shell text runs | `ca.restart_command` (likely obsolete; if kept, `ca.restart.{command,wait_s,poll_s}`, pass-4 r3 §D.2a) | `HYLO_CA_RESTART_COMMAND` | R1, **R3** (note) |
| ENV-09 | `DGX_SL_VM_URL` | `http://192.0.2.10:8428` (`SL:73`) | `rstrip("/")` | bad URL → no sample | `statusline.telemetry.url` | `HYLO_STATUSLINE_TELEMETRY_URL` | R1 |
| ENV-10 | `DGX_SL_TTL` | `4` (`SL:74`) | Python `float()` | unparsable → CP-X01; `nan`/neg → always refetch; `inf` → never | `statusline.telemetry.ttl_s` | `HYLO_STATUSLINE_TELEMETRY_TTL_S` | R1 |
| ENV-11 | `DGX_SL_ROWS` | `2` (`SL:75`) | Python `int()` | unparsable → CP-X02 | `statusline.rows` | `HYLO_STATUSLINE_ROWS` | R1 |
| ENV-12 | `DGX_SL_SPARK` | on (`SL:76`) | on iff `!= "0"` | — | `statusline.sparkline.enabled` | `HYLO_STATUSLINE_SPARKLINE_ENABLED` | R1 |
| ENV-13 | `DGX_SL_GIT` | on (`SL:77`) | on iff `!= "0"` | — | `statusline.git.enabled` | `HYLO_STATUSLINE_GIT_ENABLED` | R1 |
| ENV-14 | `DGX_SL_TRACE` | `rate` (`SL:89`) | `TRACE_KEYS.get(v, "v")` | unknown → `rate` | `statusline.sparkline.trace` | `HYLO_STATUSLINE_SPARKLINE_TRACE` | R1 |
| ENV-15 | `COLUMNS` | absent → 0 (`SL:1186`) | `int()`, errors → 0 | negative → no trim, no row 2 | — (Claude Code protocol) | — | R1 |
| ENV-16 | `DGX_FAKESTOP_LOG` | `~/.cache/dgx-llm/auto-continue.log` (`EX:23`); writer hard-coded (`HK:195-196`) | literal | missing → no tallies | `paths.hook_log` | `HYLO_PATHS_HOOK_LOG` | R1 |
| ENV-17 | `DGX_SESSION_LIMIT` | `50` (`EX:24`) | Python `int()` | import crash → launchd loop; `-n` drops oldest | `exporter.session_limit` | `HYLO_EXPORTER_SESSION_LIMIT` | R1 |
| ENV-18 | `DGX_LEDGER_EXPORTER_PORT` | `9210` (`EX:25`) | Python `int()` | `0` → ephemeral port, log says `:0`; `<0`/`>65535` → `OverflowError` after the print | `exporter.port` | `HYLO_EXPORTER_PORT` | R1, R2 |
| — | (literal `0.0.0.0`, `EX:414`) | — | — | — | `exporter.bind` (default per OD-24/27) | `HYLO_EXPORTER_BIND` | R2 |
| ENV-19 | `DGX_KEV_URL` | `http://192.0.2.10:8008/v1/systemone` (`HK:31`, `LN:154`) | raw; `Request()` at `HK:110` outside the `try` | empty/no scheme → H-10 (exit 1, no output, no log) | `hook.kev.url` | `HYLO_HOOK_KEV_URL` | R1, R2 |
| ENV-20 | `DGX_KEV_MODEL` | `kev-latest` (`HK:32`); effective = LN-pinned id (`:155`) | raw | — | `hook.kev.model` | `HYLO_HOOK_KEV_MODEL` | R1 |
| ENV-21 | `DGX_KEV_THRESHOLD` | `0.40` (`HK:33`, `LN:152`) | Python `float()` | unparsable → H-07; `nan` → never fake; `inf` → always | `hook.kev.threshold` | `HYLO_HOOK_KEV_THRESHOLD` | R1 |
| ENV-22 | `DGX_KEV_TIMEOUT` | `2.5` (`HK:34`) | Python `float()`; per socket operation | ≤ 0/NaN → Kev never contacted (caught); > 9,223,372,036.854775 s incl. `inf` → H-11 (exit 1) | `hook.kev.timeout_s` (`config.Seconds`, K-8; OD-75 (b)) | `HYLO_HOOK_KEV_TIMEOUT_S` | R1, R2 |
| ENV-23 | `DGX_KEV_MESSAGES` | `14` (`HK:35`) | Python `int()`, unused | unparsable → H-07 | — (accepted, ignored; T-084 DROP) | — | R1 |
| ENV-24 | `DGX_KEV_CHARS` | `6000` (`HK:36`) | Python `int()`; `[-n:]` | `0` = whole state; `-n` drops head | `hook.kev.state_chars` | `HYLO_HOOK_KEV_STATE_CHARS` | R1 |
| ENV-25 | `DGX_KEV_API_KEY` | unset → file (`HK:97-102`) | value wins over the file; empty → file | CR/LF → caught → unreachable | `hook.kev.api_key_file` (K-5) | `HYLO_HOOK_KEV_API_KEY_FILE` (no value var) | R1, R2 |
| ENV-26 | `DGX_ENGLISH` | `1` (`LN:148`) | on iff `!= "0"` | — | `hook.english.enabled` | `HYLO_HOOK_ENGLISH_ENABLED` | R1 |
| ENV-27 | `DGX_AUTOCONTINUE` | `1` (`LN:148`) | hook off iff `== "0"`; LN on iff `!= 0` | — | `hook.autocontinue.enabled` | `HYLO_HOOK_AUTOCONTINUE_ENABLED` | R1 |
| ENV-28 | `DGX_INVISIBLE` | `1` | `== 1` | else → removed visible mode | — (D6) | — | R1 |
| ENV-29 | `ROUTER_PORT` | unset | raw | — | — (D6) | — | R1 |
| ENV-30 | `DGX_USER` | `$(whoami)` (`LN:43`) | raw, unescaped header | newline injects a header | `attribution.user` | `HYLO_ATTRIBUTION_USER` | R1 |
| ENV-31 | `ANTHROPIC_CUSTOM_HEADERS` | appended (`LN:46-53`) | newline-joined | — | — (Claude Code protocol) | — | R1 |
| ENV-32 | `DGX_SKIP_PREFLIGHT` | `0` (`LN:60`) | skip iff `== 1` | `true` runs it | **`run.preflight.enabled`** (inverted; K-1, adopted by pass-4 r3) | `HYLO_RUN_PREFLIGHT_ENABLED` | R2, **R3** (agreed) |
| — | (literal 4 s, `PF:23`) | — | — | — | **`run.preflight.timeout_s`** (pass-4 T-100) | `HYLO_RUN_PREFLIGHT_TIMEOUT_S` | R2, **R3** (agreed) |
| ENV-33 | `DGX_PROFILE` | `$HOME/.config/dgx-llm/profile.env` (`LN:114`) | zsh `source` | arbitrary shell | — (K-2: `hylo run --profile`) | — | R2 |
| ENV-34 | `DGX_MAIN_MODEL` | `sonnet` (`LN:128`) | exactly `opus`, else sonnet | — | `run.main_model` | `HYLO_RUN_MAIN_MODEL` | R1 |
| ENV-35 | `DGX_REMOTE` | `0` | on iff `== 1` | — | `run.remote_control` | `HYLO_RUN_REMOTE_CONTROL` | R1 |
| ENV-36 | `DGX_SAFE` | `0` | prompts kept iff `== 1` (inverted) | — | `run.skip_permissions` | `HYLO_RUN_SKIP_PERMISSIONS` | R1 |
| ENV-37 | `DGX_SANDBOX` | `0` | on iff `== 1` | — | `run.sandbox` | `HYLO_RUN_SANDBOX` | R1 |
| ENV-38 | `DGX_STATUSLINE` | `1` | on iff `== 1` | `true` disables | `run.statusline.enabled` | `HYLO_RUN_STATUSLINE_ENABLED` | R1 |
| ENV-39 | `DGX_PRINT_ARGS` | `0` | `== 1` | — | — (`hylo run --print-args`) | — | R1 |
| ENV-40 | `TMPDIR` | `/tmp` (`LN:23,74`; `CO:32`) | `${TMPDIR:-/tmp}` | — | `paths.proxy_log_dir` (default source, K-6) | `HYLO_PATHS_PROXY_LOG_DIR` | R1, R2 |
| ENV-41 | `HOME` | OS | `expanduser` on defaults only (CV-11) | unset → LN abort (`set -u`) | — (`os.UserHomeDir`) | — | R1 |
| ENV-42 | `PWD` | OS | basename, unescaped (`LN:44`) | newline injection | — (`os.Getwd`) | — | R1 |
| ENV-43 | `ARGS` | unset | zsh scalar prepended to `claude` argv; a `.zshenv` assignment overrides an exported value (§A.0 V9) | accident | — (OD-60 (b)) | — | R1, **R3** |
| — | (none; `PX:289` literal) | `~/dgx-llm-obs/` | — | — | `paths.failed_capture_dir` (K-3, adopted by pass-4 r3) | `HYLO_PATHS_FAILED_CAPTURE_DIR` | R2 |

Totals (unchanged): **43** explicit inputs; **33** map to a key; **10** have none; **3** keys have no legacy env (`exporter.bind`,
`run.preflight.timeout_s`, `paths.failed_capture_dir`). Import-time crashes on a bad value: 9. Per-call crashes: 2 (H-10, H-11).

### B.2 Implicit inputs: 20 IDs (harness parameters, not config)

| ID | Input | Read by | Effect | Pin | Src |
|---|---|---|---|---|---|
| ENV-I1 | `TZ` | every `strftime`/`localtime` (`PX:60,72,632,709`; `HK:197`); naive parses (`SL:983`, `EX:125,145`, `BF:39`); `mktime` (`SL:286`) | local text, naive arithmetic | fixed per case; naive cases use one west and one east-or-zero DST zone (§A.1) | R1, **R3** |
| ENV-I2..I5 | `LANG`, `LC_ALL`, `LC_CTYPE`, `LC_TIME` | stdio/`open()` encoding; child `ps` | strict vs surrogateescape; localized `lstart` | `LANG=en_US.UTF-8`, rest unset | R1 |
| ENV-I6..I9 | whole `PYTHON*` class (`PYTHONUTF8`, `PYTHONIOENCODING`, `PYTHONPATH`, `PYTHONINTMAXSTRDIGITS`, …) | interpreter | codec, digit limit, import path | unset all except the harness `PYTHONPATH`; `PYTHONNOUSERSITE=1` allowed (ENV-I20) | R1, R2 |
| ENV-I10 | `PATH` | `python3`, `ps`, `claude`, `nc`, `whoami`, `curl`, trust-CLI tools, `lsof`/`flock` | which tools run | pinned interpreter per component | R1 |
| ENV-I11 | `USERPROFILE` | `expanduser` on Windows | home | set with `HOME` | R1 |
| ENV-I12..I14 | every `*_proxy` variable (any case; lowercase wins; empty lowercase cancels) | urllib in the Kev call (`HK:113`); SL opts out (`SL:168`) | proxy selection; any non-empty one suppresses ENV-I15 | env from scratch; `no_proxy=*` | R1, R2 |
| ENV-I15 | OS proxy settings (no proxy env set) | urllib `getproxies()` macOS/Windows fallback | Kev request follows system proxy | `no_proxy=*` | R1 |
| ENV-I16 | `REQUEST_METHOD` | urllib CGI guard | ignores `HTTP_PROXY` | unset | R1 |
| ENV-I17 | `SSLKEYLOGFILE`, `MITMPROXY_SSLKEYLOGFILE` | mitmproxy at import | TLS secrets file | unset | R1 |
| ENV-I18 | `ZDOTDIR` → `$ZDOTDIR/.zshenv` (default `$HOME/.zshenv`) | zsh for `LN`, `CO` (`#!/bin/zsh`, no `-f`) | arbitrary shell before line 1; overrides exported vars | `zsh -f`, or temp `HOME` and `ZDOTDIR` | R2, **R3** (re-exec) |
| ENV-I19 | `MITMPROXY_CASE_SENSITIVE_FILTERS`; `EDITOR`, `PAGER` | mitmproxy 12.3.1 | inert in legacy | unset | R2 (adopted) |
| **ENV-I20** | **user site-packages under `HOME`**: `.pth` files and `usercustomize.py` (3.9.6 `~/Library/Python/3.9/lib/python/site-packages`; 3.11.7 `~/.local/lib/python3.11/site-packages`) | CPython `site` at start of SL, HK, BF, trust CLI (3.11.7) and EX (3.9.6). Not the `.mitmenv` venv (PX, PF): a default venv disables the user site | arbitrary code before the script, like ENV-I18 | temp `HOME` (already in every pin set), or `PYTHONNOUSERSITE=1` / `-s`. Both are compatible with the clock shim, which needs `sitecustomize` via `PYTHONPATH`, not the user site | **R3** |
| negative | `PYTHONHASHSEED` | — | no output effect | none | R1 |

### B.3 Determinism and pinning inventory: 54 rows

Go injection points: `statusline.Env{Now, Getenv, Home, Cwd, Stdin, Stdout, Loc}`, one `Clock` per long-running component,
`platform.ProcessStart`, telemetry and Kev clients built from config, `pytime.LocalToUnix(loc, wall)` (CPython `_mktime` port).

| ID | Class | Site | Pin (legacy side) | Go injection point | Src |
|---|---|---|---|---|---|
| DET-01..06 | wall clock | `SL:231` cost record; `:243` thresholds; `:304` rl keep; `:322` TTL/history; `:408` git TTL; `:499` limits | shim mode 1 | `Env.Now` | R1 |
| DET-07 | wall clock + FMA | `SL:558` ⌂ age and 5-min gate | mode 1 + seeded `proc_start` | `Env.Now`, read once per render; gate computed with explicit `float64()` (PR-15) | R1, **R3** |
| DET-08 | two reads | `SL:825-826` idle | mode 1 | one `Now` per render | R1 |
| DET-09 | eager default (two reads) | `PX:128`; `PX:238` `_t0`; `PX:273` `_dgx_t0` (set at `PX:153`) | mask `duration_s` | proxy `Clock`, no read-count matching | R1, R2 |
| DET-10 | wall clock | `PX:296` capture file name | none | proxy `Clock` | R1 |
| DET-11 | dead | `PX:530,535` | none | — | R1 |
| DET-12 | clock + sleep | `PX:723-725` (OOS) | — | — | R1 |
| DET-13 | behavior-affecting reads | `HK:111,118`; early stop `HK:133`; log `HK:197` | mode 1; mode 2 sequences: 2 reads per successful call, 1 per failed call, 1 per log line ([exec] R2) | hook `Clock` at the same two points | R1, R2 |
| DET-14 | wall clock | `BF:95` cutoff vs `getmtime` | mode 1 + `os.utime` | `Clock` + `fs.FS` stat | R1 |
| DET-15..18 | C-level clock (`strftime`) | `PX:60` ledger `t`; `PX:72`; `HK:197`; `PX:632,709` (OOS) | extended shim (patches `strftime`/`localtime`) or mask | `Clock` formatted in `Loc` | R1 |
| DET-19 | naive local → epoch | `SL:983` | fixtures with `Z`; naive case per zone | `pytime.LocalToUnix(Env.Loc, …)` | R1, R2 |
| DET-20 | libc `mktime` | `SL:286` | seeded `proc_start` | `platform.ProcessStart` (true start; OD-76). Crossover is zone- and year-dependent (§A.0 V11) | R1, R2, **R3** |
| DET-21 | naive local → epoch, lenient `strptime` | `EX:125,145` | `TZ` = the ledger writer's zone | `ledger.Rebuild(…, loc)` + Python-lenient parser + `LocalToUnix` | R1, R2 |
| DET-22 | `fromisoformat` by version | `BF:39` | `Z` fixtures; 3.11 grammar | `Loc` | R1 |
| DET-23 | local wall text | all `strftime` sites | fixed `TZ` | `Loc` | R1 |
| DET-24 | monotonic (negative) | none in legacy | — | parity durations from the injected `Clock`, never `time.Since` | R1 |
| DET-25 | network | `SL:165-171` VM GET, proxies off | `httptest` fake via `DGX_SL_VM_URL` | client from config, `Proxy = nil` | R1 |
| DET-26 | network + OS proxy discovery | `HK:110-113` | fake Kev + `no_proxy=*` | Kev client from config; env pinned | R1 |
| DET-27 | network | `PF:23` connect 4 s; DNS outside it (pass-4 r3 A.1 row 10) | closed port / sentinel | dialer with total deadline (Go's covers DNS: `net/dial.go` `dialCtx` before `resolveAddrList`) | R1, **R3** |
| DET-28 | network | upstream via mitmproxy | recorded replies | upstream `RoundTripper` | R1 |
| DET-29 | ports | `LN:21,73,77-78` `nc -z` | accept any port | injected listener | R1 |
| DET-30 | process/ports | `CO:15,23,28` (OOS) | — | — | R1 |
| DET-31 | process tree | `SL:278-286` `ps` walk | seed `proc_start` | `platform.ProcessStart` | R1 |
| DET-32..33 | pids | `PX:518`; `LN:23,74,76,93`; `PX:606` | mask / not compared | — | R1 |
| DET-34 | per-process memory | `PX:50,89-95,181-187` | one process per replay | `Router` fields | R1 |
| DET-35 | cache files | `SL:78,217,405,1017,1215` | temp `HOME`+`USERPROFILE`; compare after every step | `Env.Home` | R1 |
| DET-36..37 | transcript bytes; `.git` walk | `SL:1009-1058`; `SL:373-393` | fixtures created at test time | `Env` | R1 |
| DET-38 | cwd | `SL:373` `abspath` | fixed cwd | `Env.Cwd` | R1 |
| DET-39..42 | filesystem | `PX:93,291`; `EX:66,115,215,282`; `HK:68,100,195-196`; `BF:91,97,98` | temp `HOME`, fixture trees, `os.utime` | config paths; `Rebuild(io.Reader…)`; sorted listing | R1 |
| DET-43 | environment | all of §B.1/B.2 | env built from scratch for **both** the oracle and the Go binary (GP-1..GP-6) | `internal/config` resolved once | R1, **R3** |
| DET-44..46 | locale | stdio (`SL:1201-1204,1234`; `HK:206,211`); text mode files; child `ps` | `LANG=en_US.UTF-8`; exporter under launchd-like empty env | byte-level I/O with explicit checks | R1 |
| DET-47..48 | randomness (temp names; negative) | `SL:201`, `BF:113`, `PX:618` | none | `os.CreateTemp`; never range a map for output | R1 |
| DET-49 | terminal size | `SL:1186` `COLUMNS` | explicit `COLUMNS` | `Env.Getenv` + Python `int()` grammar | R1 |
| DET-50 | interpreter version | SL/HK/BF/trust 3.11.7; PX/PF 3.12.10 venv; EX 3.9.6 | pin per component | per-component oracle rules | R1 |
| DET-51 | ordering | `SL:175-184`; `PX:178-179`; `EX:238,293-380` | fixtures fix order | ordered decode, stable sort | R1 |
| DET-52 | concurrency | debounced status line; multi-writer ledger | serial refreshes | atomic replace; one `Write` per line | R1 |
| DET-53 | resolver lookup at start | `EX:414` → `server_bind` → `getfqdn("0.0.0.0")` | call `Rebuild` with no listener | none (Go does no lookup; output-neutral) | R2, **R3** (source re-read) |
| **DET-54** | wall clock + FMA, `--subagent` path | `SL:889` `now_ms = time.time()*1000`; used at `SL:919` `max(now_ms - start, 0)/1000` → `MM:SS` (`SL:920`) | shim mode 1 (constant) | `Env.Now`; explicit `float64(now*1000)` (PR-15). **OOS unless OD-14 keeps the path** (pass-0 r3 row 12) | **R3** |

Counts: **54** rows (53 + DET-54). Classes: wall clock 15 (DET-01..14, 54), C-level clock 4, time zone 5, monotonic 1 (negative), network 6,
process 4, filesystem 8, environment 1, locale 3, randomness 2, terminal 1, interpreter 1, ordering 1, concurrency 1, resolver 1.

**Go-side pins (new grouping, R3).** These are not legacy inputs, but the parity harness must also build the Go binary's env from scratch:

| ID | Go input | Effect | Pin |
|---|---|---|---|
| GP-1 | `TZ`, `ZONEINFO` (`time/zoneinfo.go:676`) | `time.Local`, zone database | `Loc` injected; `time/tzdata` embedded; both unset |
| GP-2 | `GODEBUG` (and `go.mod` `godebug` lines) | stdlib behavior switches (TLS, HTTP/2, x509, timers) | unset; `godebug` lines reviewed |
| GP-3 | `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`/`REQUEST_METHOD` (`http.ProxyFromEnvironment`) | proxying of hylo's own clients | clients built with explicit `Proxy` |
| GP-4 | `SSL_CERT_FILE`, `SSL_CERT_DIR` (Linux/BSD only, `crypto/x509/root_unix.go`) | trust roots on Linux CI | unset |
| GP-5 | `TMPDIR` / `TMP`, `TEMP` (`os.TempDir`) | temp locations, `paths.proxy_log_dir` default | temp dir per case |
| GP-6 | `HOME` / `USERPROFILE` (`os.UserHomeDir`) | every `paths.*` default | temp dir per case |

### B.4 Per-phase pin sets (consolidated)

| Phase | Clock | Network | Process | Filesystem | Env / locale | Interpreter | Src |
|---|---|---|---|---|---|---|---|
| P1 status line | mode 1, stepped between refreshes | fake VM | seeded `proc_start` | temp `HOME`+`USERPROFILE` (empties ENV-I20), fixtures, fixed cwd | from scratch; `LANG=en_US.UTF-8`; `TZ` = UTC plus one west and one east-or-zero DST zone for naive cases; `COLUMNS` | 3.11.7 | R1, **R3** |
| P2 exporter | none (reads `t` text) | **none** (no listener; DET-53) | — | fixture ledger and hook log | launchd-like empty env + `TZ`, `HOME`, `DGX_*` paths; `TZ` = the ledger's | 3.9.6 | R1, R2 |
| P3 proxy | mode 1 or mask `t`/`duration_s` | recorded upstream | one process per replay | temp `HOME`, key file | `DGX_*`, `LOCAL_MODEL_PREFIXES`, `TZ`; `SSLKEYLOGFILE` unset | 3.12.10 venv (OD-47) | R1 |
| P4 hook | mode 1; mode 2 for early stop | fake Kev + `no_proxy=*` | — | temp `HOME`, transcript | `DGX_KEV_*`, `DGX_ENGLISH`, `DGX_AUTOCONTINUE`, `LANG`, `TZ`; all `PYTHON*` unset except `PYTHONPATH` | 3.11.7 | R1, R2 |
| P4 launcher | — | port occupancy | `$$`, `$!` only in names | temp `HOME` **and** `ZDOTDIR`, or `zsh -f`; `profile.env` fixture | from scratch, no `ARGS` | zsh 5.9 | R1, R2 |
| Go side, all phases | injected `Clock` | `httptest` | fake `ProcessStart` | temp `HOME`/`TMPDIR` | GP-1..GP-6 unset or fixed | Go 1.26.x; FMA guard tests on **arm64** | **R3** |
| Windows CI | — | — | — | — | naive-time cases as Go table tests against CPython-generated goldens (now 7,228 rows across 26 zones) | — | R2, **R3** |

### B.5 Conventions catalogue (19)

| ID | Convention | Evidence | Go equivalent | Src |
|---|---|---|---|---|
| CV-01 | Atomic replace, swallow-all (caches, 0600, leak on failed replace) | `SL:198-206` | `os.CreateTemp` + `Rename`; remove temp on error | R1 |
| CV-02 | Atomic replace, errors propagate (backfill, prefix `cost-history.`) | `BF:111-116` | same helper, error returned | R1 |
| CV-03 | Atomic replace, `indent=2, sort_keys` + `\n` (trust state, OOS) | `PX:616-622` | OOS | R1 |
| CV-04 | Append one complete line per open, umask perms, multi-writer ledger | `PX:56-62,65-74`; `HK:193-201` | `O_APPEND`, one `Write` | R1 |
| CV-05 | Four JSON styles J1-J4 | `PX:60,150,185,620-621`; `SL:203`; `HK:105-109,206`; `BF:115`; `LN:156-181` | `internal/pyjson.Dumps(v, Opts)` | R1 |
| CV-06 | Ledger record shape `{"t", "event", **fields}`, call-site order | `PX:56-62,236-245` | ordered pairs writer | R1 |
| CV-07 | Log line formats (ledger `t`, decision-log `%s` rendering, hook log grammar) | `PX:72`, 11 templates; `HK:197-199` | `pytime.Strftime`, `pyfmt.Str/Repr` | R1 |
| CV-08 | Error ladder E1-E5 (top-level guard; never-raise helpers; narrow catches; unguarded; exceptions as parse results) | `SL:1238-1245` etc. | `errDegraded` + per-site predicates | R1 |
| CV-09 | Env read at import into UPPER_SNAKE constants | `SL:73-100`; `HK:31-36`; `EX:22-25`; `PX:53-54` | `internal/config` once at startup | R1 |
| CV-10 | Env booleans by per-variable string comparison | pass-2 r2 §6.8 | alias predicate table; typed `HYLO_*` (OD-05) | R1 |
| CV-11 | `expanduser` on defaults only | `PX:53-54,88,563`; `EX:22-23` | OD-61 (b) | R1 |
| CV-12 | `x.get(k) or default`; `isinstance(x,(int,float))` accepts `bool`/NaN | `SL:420,540,602,1105-1112` | `pyfmt.Truthy/Num` | R1 |
| CV-13 | Stable digests (sha1), sid sanitizer | `SL:402-405,1017` | `crypto/sha1` with a reason | R1 |
| CV-14 | Python units (code points, `json.dumps` chars) | `SL:1120-1149` | `pystr.Len`, `pyjson.DumpsLen` | R1 |
| CV-15 | Output assembled once, written once | `SL:128,1230-1234` | one `Write` after encodability check | R1 |
| CV-16 | Schema marker key `mixv6` | `SL:1025-1038` | same rule | R1 |
| CV-17 | Process state in module globals; reload resets | `PX:50,89,181-187,521`; `EX:60-61` | struct fields | R1 |
| CV-18 | Naming (UPPER_SNAKE, `_private`, `DGX_`/`DGX_SL_`/`DGX_KEV_`, `dgx_*`/`anth_*` events, `dgx_llm_*` metrics, rationale comments) | passim | CamelCase; D7 freeze; rationale comments | R1 |
| CV-19 | Config key conventions: component namespaces; `paths.*`; `*_file` secrets; unit suffixes; `.enabled` only where legacy has a toggle and the feature has settings; HYLO names generated from the registry; **the source's comparison operator stated in each key's comment, with boundary tests** (pass-4 r3 §D.1 H-5/H-6 note, e.g. `colon_min_chars` is `> 20`) | §B.1; pass-4 r3 §D.1, §D.2a | `internal/config` registry entries (type, default, rationale, operator, alias + predicate) | R2, **R3** (two sub-rules adopted from pass 4) |

### B.6 Python→Go pitfall register (22 entries, corrected remedies)

Test types: **T** table test with CPython-generated expectations (committed generator), **F** differential fuzz, **G** golden/replay.

| ID | Tag | Pitfall | Occurrences | Go remedy | Test | Src |
|---|---|---|---|---|---|---|
| PR-01 | PT-ROUND | `round()` half-even / exact binary | `SL:1171,234`; `BF:108`; `PX:238,273`; `PX:213` (0 production events); half-up `int(x+0.5)` `SL:426,675` | `pyfmt.Round`, `RoundN` | T, F | R1, R2 |
| PR-02 | PT-FMT | `{:.Nf}` and non-finite spellings | SL list (research §2b); `HK:250,256`; `EX:298,333,353,364,370,374,398` | `pyfmt.F` | T, F | R1 |
| PR-03 | PT-FDIV | float `//`/`%` | `SL:525-529,546,560-561,826`; int `SL:548,561,829-831,859`; `HK:138`; `SL:919-920` | `pyfmt.FloorDiv/Mod` | T, F | R1, **R3** (+`SL:920`) |
| PR-04 | PT-NANMM | `max`/`min` argument order with NaN | `SL:146,422,479,508,671,674-675,758-759`; `EX:126-145`; `SL:919` | `pyfmt.Max/MaxSeq` | T | R1 |
| PR-05 | PT-INT | `int()` truncation/raise; `int(True)` | `SL:148,426,546,675,683,759,853`; PX/EX sites; `HK:118` | `pyfmt.Int` | T | R1 |
| PR-06 | PT-BOOL | `bool` is `int`; falsy defaults | passim | `pyfmt.Truthy/Num` | T | R1 |
| PR-07 | PT-FREPR | float `repr` | `json.dumps` floats (`SL:203`; `PX:60,150`; `BF:115`) | `pyfmt.Repr` | T, F | R1 |
| PR-08 | PT-JSONLEN | `json.dumps` length/escaping | `SL:1138,1140,1147`; CV-05 sites | `pyjson.Dumps/DumpsLen` | T, F | R1 |
| PR-09 | PT-JSONIN | `json.loads` leniency | stdin, transcripts, VM, caches, PX, EX, HK, BF | `pyjson.Loads(bytes, mode)` | T, F | R1 |
| PR-10 | PT-INTLIM | 4,300-digit limit (≥ 3.11; not EX on 3.9.6) | 8 SL sites, `PX:106`; EX exempt | per-component limit | T | R1, R2 |
| PR-11 | PT-CP | code-point `len`/slices | SL, HK, PX (ledger-visible `req_bytes`, `error[:300]`, `account[:8]`), EX | `pystr.Len/Slice` | T | R1 |
| PR-12 | PT-SPLIT | `splitlines` sets; Python whitespace; universal newlines | `HK:69,177`; `SL:1059`; `EX:116,216`; `BF:44`; strip sites | `pystr.*` + universal-newline reader | T | R1, R2 |
| PR-13 | PT-RE | Unicode `\b`/`\s`; lookbehind (RE2) | `HK:24-28,177,179-180,184,236`; `SL:137,1017`; `PX:413`; `EX:230` | hand-written splitter; Unicode boundary helper | T, F | R1, R2 |
| PR-14 | PT-TIME | naive local time: Go `time.Date`/`ParseInLocation` picks a different instant than Python in gaps (offset < 0) and overlaps (offset ≥ 0), up to a 24 h day skip; `strptime` leniency (single digits, lowercase `t`) | writers `PX:60,72,632,709`, `HK:197`; readers `EX:125,145`, `SL:983`, `BF:39`, `SL:286` | **`pytime.LocalToUnix` = CPython `_mktime` port (0 / 7,228)**; hand-written lenient parser; `*time.Location` injected; `time/tzdata` | T: committed CPython goldens (both grids) | R1, R2, **R3** (rule generalized) |
| PR-15 | PT-FMA | Go fuses `x*y ± z` (also across statements, also when the product is reused); Python rounds each operation | `BF:75-76` (4 `FMADDD`); colorsys via `SL:146-147` (2 `FMSUBD` + 1 `FNMSUBD`); `SL:558-559` (1 `FNMSUBD`); **`SL:889`+`SL:919` (1 `FNMSUBD`, `--subagent`, OD-14)**. Not hazards: `SL:674-675`, `SL:682`, `BF:95` | **explicit `float64(…)` around every product feeding `+`/`-`**; port colorsys in the same operation order | T on **arm64** (any OS) only; amd64 at any `GOAMD64` level is not a reliable detector (CONV-ABS-77) | R1, R2, **R3** (new occurrence; test placement) |
| PR-16 | PT-STR | `str()`/`repr()` of non-str | `HK:197-199`; `SL:442,453`; EX `esc()` | `pyfmt.Str/Repr` | T | R1 |
| PR-17 | PT-ENC | strict UTF-8 writes; locale stdio | `SL:1234`; `HK:196-199,206`; `PX:71-72`; `EX:399` | byte I/O + explicit checks | T | R1 |
| PR-18 | PT-PARSE | `int()`/`float()` grammar vs `strconv`; `urlparse().port` by version: 3.9.6 accepts `+80`, leading/trailing space, Unicode digits, `_`; 3.11.7/3.12.13/3.13.14 accept ASCII digits only | env `SL:74-75`, `HK:33-36`, `EX:24-25`; coercions; `PX:82`, `PF:20` | `pyfmt.ParseInt/ParseFloat`; port = ASCII digits 0..65535, `0`/empty → 80 (3.11/3.12 oracle) | T | R1, R2, **R3** |
| PR-19 | PT-ORDER | insertion order, first-wins, stable sort | `SL:175-184,338-347,1150-1153`; `PX:60,178,514`; `EX:238,293-380`; `BF:81,97` | ordered pairs; `slices.SortStableFunc` | G | R1 |
| PR-20 | PT-PATH | `posixpath`/`ntpath`; `abspath` (cwd) | `SL:373,383,390,460`; `PX:289,560-572`; `HK:100,195` | `path/filepath`; per-OS goldens | G | R1 |
| PR-21 | PT-EXC | exception-driven output | CP-*, P-*, E-*, H-01..H-11, B-* | `errDegraded` + per-site predicates | T, G | R1, R2 |
| PR-22 | PT-DUR | float seconds → `Duration` is implementation-defined out of range (arm64 saturates, NaN → 0; amd64 → `MinInt64`; an upstream alternative is staged behind `-d=converthash`). Go timeout knobs disagree on ≤ 0: `Client.Timeout`/`ResponseHeaderTimeout` → none; `Dialer.Timeout`/`TLSHandshakeTimeout` negative → immediate expiry. Python: 0/neg/NaN → never connects (caught); > 9,223,372,036.854775 s → crash; timeouts are **per socket operation** with DNS outside them; `subprocess.run(timeout=)` is a total deadline | `HK:34,113`; `SL:168` (1.5 s); `PF:23` (4 s); `SL:280-281` (`ps` 1 s); every `*_timeout_s` key (K-8) | **validate before converting**: `config.Seconds` finite, > 0, ≤ 9,223,372,036.854775; never pass ≤ 0 or an unvalidated conversion to any knob; per OD-75 (b) the `DGX_KEV_TIMEOUT` alias maps ≤ 0/NaN to "Kev disabled, no request" and rejects the overflow range at load; total-deadline semantics with DNS inside (OD-56; Go's `Dialer` applies the deadline before resolving) | T on arm64 and amd64 (cross-compiled test binaries; edge values as table rows) | R2, **R3** (knob semantics; per-op vs total cross-ref from pass-4 r3) |

Tags: 19 original + PT-FREPR, PT-INTLIM, PT-DUR = 22.

---

## C. Reconciliation with sibling deep files

| Sibling | Item | State |
|---|---|---|
| pass-4 r3 §D.2a / §D.3 | **K-1** `run.preflight.enabled` + `run.preflight.timeout_s` | **Resolved.** Pass-4 r3, updated at 03:02 local, adopts it (T-100, H-3) and K-3 `paths.failed_capture_dir`, and reports "None" remaining. HYLO names are identical in both files |
| pass-4 r3 §D.2a | rule-5 refinement: no `.enabled` where legacy has no toggle; `ca.restart.{command,wait_s,poll_s}` if ENV-08 survives | adopted into CV-19 and the ENV-08 row |
| pass-4 r3 Remaining Gap 3 | pass 5 should record per-operation timeouts, unbounded DNS, the `subprocess.run` total deadline, and the strict operators of H-5/H-6 | done: PR-22 (timeout semantics, DNS, `subprocess`), DET-27, CV-19 (operator sub-rule) |
| pass-4 r3 T-083 / P-6 | 2.5 s per socket operation; failure cost from milliseconds up to 2.5 s (CONV-ABS-73) | consistent with ENV-22 and DET-13; no "typical failure" figure is used here |
| pass-1 r3 V1 | mitmproxy reads no proxy variable; ENV-I19 | adopted, not re-verified (§A.0 V10) |
| pass-0 r3 row 12 | `--subagent` OOS pending OD-14 | DET-54 and the PR-15 `SL:889/919` occurrence are tagged OD-14-conditional |
| pass-2 r2 §6.3 (converged at r9) | proposed hook rows H-10, H-11 | still proposals; the pass-8 synthesis should merge them into the hook catalogue |
| pass-3 BC-SL-097 | subagent rows | the DET-54/PR-15 occurrence attaches to BC-SL-097 if OD-14 keeps the path |

**Remaining disagreement: none.** The only open items are owner decisions, listed below.

---

## Delta Summary

| Area | New (R3) | Refined / confirmed |
|---|---|---|
| Verification | 15 checks: 9 confirmed, 4 refined, 1 narrowed, 2 new | 46/3,096 reproduced by fresh code; `_mktime` port 0/7,228; FMA guard 0 diffs on a new 2.0 M-message sample; arm64 Duration conversions executed |
| Retractions | **CONV-ABS-77**: `GOAMD64=v3` as a second FMA detector (v3 fuses only register-operand additions, never subtractions) | — |
| Pitfalls | **PR-15 new occurrence `SL:889/919`** (displayed seconds can be 1 lower in a naive arm64 port; executed); PR-15 test placement → arm64 only | PR-14 rule generalized (zero-offset zones, non-DST changes, 24 h skips); PR-18 grammar (trailing space, `_`; 3.12.13 = 3.11.7); PR-22 knob semantics (`Dialer`/`TLSHandshakeTimeout` `!= 0`), staged `converthash`, per-op vs total cross-ref |
| Env inventory | **ENV-I20** user site-packages (`.pth`, `usercustomize`) under `HOME` (executed) | 43 explicit recounted; ENV-I18 re-executed (+ `.zshenv` overrides exported vars); implicit IDs 19 → 20 |
| Determinism | **DET-54** `SL:889` clock read (OD-14-conditional); Go-side pins GP-1..GP-6 | DET-20 crossover generalized (gap 5 closed); DET-53 source re-read; DET-27 Go DNS-inside-deadline; per-phase pin sets consolidated |
| Conventions | — | CV-19 gains two sub-rules from pass 4 (toggle-only `.enabled`, operator in comment) |
| Consolidation | final env table (43 + 20), DET (54), CV (19), PR (22) with source-round tags | K-1 resolved with pass-4 r3 |
| Owner items | none (OD-86..OD-89 unused) | OD-74, OD-75, OD-76 and OD-58..OD-61 carried; OD-14 now also governs DET-54 |

Existing items refined: 9 (PR-14, PR-18, PR-22, PR-03, DET-20, DET-27, DET-43, ENV-08, CV-19).

## Remaining Gaps (verbatim-carryable)

1. ENV-I19 (mitmproxy 12.3.1 env reads) and the `.mitmenv` `pyvenv.cfg` (user site disabled, inferred for ENV-I20) were not re-verified: no public
   mitmproxy copy exists on this host and the venv was not opened.
2. Python 3.12.10 URL port grammar is bracketed by 3.11.7 and 3.12.13 (identical results), not executed.
3. amd64 behavior (FMA absence, `CVTTSD2SQ` → `MinInt64`) is from compiler listings and the instruction definition; no amd64 binary was run this
   round. Windows was not executed.
4. DET-53 latency and launchd start ordering remain unmeasured (no network by rule).
5. DET-54 and the `SL:889/919` FMA occurrence matter only if OD-14 keeps the `--subagent` path.
6. Owner decisions: OD-74 (key table, now agreed by passes 4 and 5), OD-75, OD-76, OD-58..OD-61, OD-14; carried OD-01, OD-05.

## Novelty Assessment

Novelty: SUBSTANTIVE

By this round's rule, a new input, a new pitfall occurrence or a retraction is substantive. This round has one of each, all executed:
- **ENV-I20**: the Python user site-packages under `HOME` runs `.pth` and `usercustomize` code before every non-venv legacy script. It is a new
  implicit input of the same class as ENV-I18. The harness's temp `HOME` already neutralizes it, so no pin changes, but the inventory was incomplete.
- **PR-15 / DET-54**: `SL:889` reads the clock, and its product feeds `SL:919` across statements. A naive arm64 port fuses it and can show one second
  less than Python (one in 20 M random cases, and a directed case). Round 2 had called the site list complete. The path is OOS unless OD-14 keeps it.
- **CONV-ABS-77**: `GOAMD64=v3` is not a second FMA detector (no subtract rule; memory operands block fusion). The PR-15 test placement changes to
  arm64 only.

Everything else confirms or refines round 2: the DST rule and the `_mktime` port on a new 4,132-case sample, the FMA guard, Duration conversion, the
`http.Client` timeout, `.zshenv`, the libc crossover, DET-53, and the port grammar. All three new findings are narrow, and none changes a Phase 1
design decision beyond one test-placement line.

## Convergence Declaration

Another round needed: the protocol requires one after a SUBSTANTIVE round. It should re-audit ENV-I20, DET-54/`SL:889`, CONV-ABS-77 and the
consolidated tables, and take Remaining Gaps 1-6 verbatim.

## State Checkpoint

```yaml
pass: 5
round: 3
status: complete
files_scanned: 11   # all legacy files (ast scan of every .py; ranges in the header) + CPython 3.9.6/3.11.7 stdlib sources named in §A + Go 1.26.5 stdlib/compiler sources cited
timestamp: 2026-11-14T09:25:00Z
novelty: SUBSTANTIVE
counts: {env_explicit: 43, env_implicit_ids: 20, determinism_rows: 54, go_side_pins: 6, conventions: 19, pitfall_entries: 22, tags: 22}
verification: {checks: 15, confirmed: 9, refined: 4, narrowed: 1, new: 2}
probes: [dst3_gen.py, gomk3, fma3_gen.py, gofma3, gofmashape, gosl, gosub, godur3, mktime3.py, urlport3.py, fma_sites.py, zsh3, usite]
retractions: [CONV-ABS-77]
owner_items: []
unused: {conv_abs: [CONV-ABS-78, CONV-ABS-79, CONV-ABS-80], od: [OD-86, OD-87, OD-88, OD-89]}
sibling_disagreements: []
network: none (no socket bind, no DNS)
next: pass 5 round 4 (audit ENV-I20, DET-54, CONV-ABS-77; Remaining Gaps 1-6 verbatim)
```
