# Pass 5: Conventions, ENV inventory, Determinism inventory — hylo-legacy

<!-- validated 2026-11-14: fresh-context cross-check against legacy/ source (static, read-only).
     ENV and determinism inventories verified complete (all os.environ / time.* / subprocess /
     network / Path.home reads accounted for). Wording correction: LOCAL_MODEL_PREFIXES has
     three consumer defaults but only two distinct values. See hylo-legacy-extraction-validation.md. -->


## 1. Convention catalog

| Convention | Example | Consistency | Evidence |
|---|---|---|---|
| Module constants UPPER_SNAKE, read from env at import with string defaults | `TTL = float(os.environ.get("DGX_SL_TTL", "4"))` | all Python files | `dgx_statusline.py:73-100`, `auto_continue.py:31-36`, exporter `:22-25` |
| Private helpers `_leading_underscore` | `_mix_counts`, `_fmt_lines`, `_account_hint` | consistent | — |
| Env prefix `DGX_` (+ `DGX_SL_` for the status line, `DGX_KEV_` for Kev) | — | consistent; exception `LOCAL_MODEL_PREFIXES` | Section 2 |
| Rationale comments citing review items `(review 2026-11-13, #N)` next to every changed rule | `# % 60, not % 100 … (#9.1)` | consistent in statusline; sparse elsewhere | `dgx_statusline.py:547` |
| "Never raise" I/O: `try/except Exception: pass/return default` | `load_cache`, `ledger`, `note` | everywhere | Pass 1 §5 |
| Atomic writes via `tempfile.mkstemp` + `os.replace` | — | statusline, trust state, backfill; NOT ledger/logs (append) | `:198-206` |
| Duck typing via `isinstance(x, (int, float))` before arithmetic (note: `bool` passes) | thermometer, cost | consistent in statusline | `:420,540,602` |
| Truthiness defaults `x.get(k) or 0` | usage fields | consistent | `:1105-1112` |
| Color + glyph formatting via f-strings and ANSI constants; segments joined by `SEP` | — | consistent | `:127-136` |
| Cache schema versioning by marker key (`mixv6`) forcing a re-parse | — | single instance | `:1026-1028` |
| Two dialect tolerance (Anthropic and OpenAI) in parsers | `extract_stop_reason` | proxy only | `dgx_proxy.py:430-456` |
| Hook-style addon: module-level functions delegating to a singleton | `_router = DGXRouter()` | proxy | `:521-548` |
| zsh: `${VAR:-default}` env knobs, arrays for argv, `(j:,:)` join for JSON | — | launcher | `claude-dgx:164,180` |

Design patterns: Strategy-ish lane routing (`DGXRouter.request`), Tap/Decorator for SSE (`_SSETap`, pass-through
callable), Cache-aside with TTL (VM sample, git), incremental parser with persisted cursor, rebuild-from-log
(exporter is a pure projection of the ledger), degradation ladder.

Anti-patterns / smells: duplicated rules across files (prefix parsing ×3, account hint ×2, stale span ×2);
dead code (Pass 0); import-time env parsing that can crash; `main()` computes `cols` twice (`:1209,1211`);
stale docstrings (`fetch_sample` claims a tuple return, `:161`; exporter docstring metric list partial, `:4-9`;
`_mix_counts` docstring says 7-tuple, returns 10, `:1002`); misnamed fields (`req_bytes` = chars, `model_served`
= requested model, `bridge_ws_close` at open); long functions (`render_lane` 198 lines, `_mix_counts` 156,
exporter `rebuild` 173).

## 2. ENV VAR inventory (becomes the hylo config file)

| Name | Default | Consumer(s) | Purpose | Evidence |
|---|---|---|---|---|
| `LOCAL_MODEL_PREFIXES` | proxy `claude-sonnet`; statusline **`""`**; backfill `claude-sonnet`; launcher **forces** `claude-sonnet` | proxy, statusline, backfill, launcher | lane rule (comma list, startswith) | `dgx_proxy.py:85-87`, `dgx_statusline.py:444,902`, backfill `:89`, `claude-dgx:38` |
| `DGX_SERVED_MODEL` | `claude-sonnet-5-5` (launcher forces) | proxy | model rewrite target | `dgx_proxy.py:84`, `claude-dgx:39` |
| `DGX_UPSTREAM` | `http://192.0.2.10:8080` | proxy, launcher (preflight arg) | backend URL | `dgx_proxy.py:79`, `claude-dgx:63` |
| `DGX_KEY_FILE` | `~/.config/dgx-llm/api-key` | proxy | backend Bearer key path | `dgx_proxy.py:88` |
| `DGX_OBS_LEDGER` | `~/dgx-llm-obs.jsonl` | proxy, exporter | ledger path | `dgx_proxy.py:54`, exporter `:22` |
| `DGX_PROXY_DECISIONS` | `~/dgx-llm-routing-decisions.log` | proxy | decision log | `dgx_proxy.py:53` |
| `DGX_TRUST_STATE` | `~/.dgx/trust-state.json` | trust CLI | trust state | `:563` |
| `DGX_PROXY_RESTART_CMD` | unset | trust CLI rotate | regenerate CA | `:719` |
| `DGX_SL_VM_URL` | `http://192.0.2.10:8428` | statusline | VictoriaMetrics base | `dgx_statusline.py:73` |
| `DGX_SL_TTL` | `4` | statusline | fetch TTL s | `:74` |
| `DGX_SL_ROWS` | `2` | statusline | rows | `:75` |
| `DGX_SL_SPARK` | `1` (`"0"` disables) | statusline | sparkline | `:76` |
| `DGX_SL_GIT` | `1` (`"0"` disables) | statusline | branch | `:77` |
| `DGX_SL_TRACE` | `rate` | statusline | sparkline signal | `:89` |
| `COLUMNS` | absent -> 0 | statusline | width | `:1186` |
| `DGX_FAKESTOP_LOG` | `~/.cache/dgx-llm/auto-continue.log` | exporter (reader only; hook path is hard-coded) | hook log | exporter `:23`, `auto_continue.py:196` |
| `DGX_SESSION_LIMIT` | `50` | exporter | sessions tracked | exporter `:24` |
| `DGX_LEDGER_EXPORTER_PORT` | `9210` | exporter | listen port | exporter `:25` |
| `DGX_KEV_URL` | hook `http://192.0.2.10:8008/v1/systemone`; launcher same | hook, launcher | Kev endpoint (optional, D11) | `auto_continue.py:31`, `claude-dgx:154` |
| `DGX_KEV_MODEL` | hook `kev-latest`; launcher exports a pinned kev-4b id (different) | hook, launcher | Kev model | `auto_continue.py:32`, `claude-dgx:155` |
| `DGX_KEV_THRESHOLD` | `0.40` | hook, launcher | fake threshold | `auto_continue.py:33`, `claude-dgx:152` |
| `DGX_KEV_TIMEOUT` | `2.5` | hook | Kev timeout | `:34` |
| `DGX_KEV_MESSAGES` | `14` | hook (unused) | — | `:35` |
| `DGX_KEV_CHARS` | `6000` | hook | state size | `:36` |
| `DGX_KEV_API_KEY` | unset -> `~/.config/dgx-llm/kev-api-key` | hook | Kev auth | `:97-102` |
| `DGX_ENGLISH` | `1` | hook, launcher | language policing + system prompt + reminder hook | `auto_continue.py:217`, `claude-dgx:136,148,157` |
| `DGX_AUTOCONTINUE` | `1` | hook, launcher | fake-stop checks | `auto_continue.py:228`, `claude-dgx:148,160` |
| `DGX_INVISIBLE` | `1` | launcher | transport mode (0 = removed visible mode) | `claude-dgx:62,70,86,99` |
| `ROUTER_PORT` | unset | launcher (visible mode) | router port | `claude-dgx:17-18` |
| `DGX_USER` | `whoami` | launcher | `X-DGX-User` | `:43` |
| `ANTHROPIC_CUSTOM_HEADERS` | appended | launcher -> Claude Code | attribution headers | `:46-53` |
| `DGX_SKIP_PREFLIGHT` | `0` | launcher | skip preflight | `:60` |
| `DGX_PROFILE` | `~/.config/dgx-llm/profile.env` | launcher | backend profile (e.g. `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `CLAUDE_CODE_MAX_OUTPUT_TOKENS`) | `:111-115` |
| `DGX_MAIN_MODEL` | `sonnet` | launcher | `--model` | `:128-131` |
| `DGX_REMOTE` | `0` | launcher | `--remote-control` | `:133` |
| `DGX_SAFE` | `0` | launcher | keep permission prompts | `:139` |
| `DGX_SANDBOX` | `0` | launcher | Bash sandbox | `:165` |
| `DGX_STATUSLINE` | `1` | launcher | statusLine settings | `:175` |
| `DGX_PRINT_ARGS` | `0` | launcher | dry run | `:182` |
| `TMPDIR` | `/tmp` | launcher, coordinator | mitmdump logs | `claude-dgx:23,74`, coordinator `:32` |
| Exported by launcher (outputs) | `HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS`, `API_TIMEOUT_MS=1800000`, `CLAUDE_CODE_AUTO_MODE_SERVER=0`, `PYTHONUNBUFFERED=1` (mitmdump), unset `ANTHROPIC_BASE_URL` | Claude Code, mitmdump | — | `claude-dgx:71,75,79-80,100,104,109` |

Config-file implication: 40 inputs collapse into sections `backend` (upstream, served model, key file, prefixes),
`paths` (ledger, decisions, caches, hook log), `statusline` (vm_url, ttl, rows, spark, git, trace), `exporter`
(port, session_limit), `hook` (kev url/model/threshold/timeout/chars/key file, english, autocontinue), `run`
(main model, remote, safe, sandbox, statusline, profile). Note the **three consumer defaults, only two distinct values** for
`LOCAL_MODEL_PREFIXES` — parity must reproduce "statusline sees whatever the launcher exported".

## 3. DETERMINISM INVENTORY (every input the P1–P3 parity harness must pin)

### Status line (`dgx_statusline.py`) — P1 priority
| Source kind | Read | file:line | Pin strategy |
|---|---|---|---|
| Wall clock | `record_cost` now | :231 | shim `time.time` (sitecustomize) + `HYLO_TEST_NOW` |
| Wall clock | `cost_thresholds` now (30-d window) | :243 | same |
| Wall clock | `effective_rl` now (smoothing) | :304 | same |
| Wall clock | `get_sample` now (TTL, ages, hist) | :322 | same |
| Wall clock | `git_segment` TTL | :408 | same |
| Wall clock | limits `now_rl` (expiry, projection, countdown) | :499 | same |
| Wall clock | `⌂` window ms | :558 | same |
| Wall clock | idle age (two separate reads) | :825-826 | same (must be one constant) |
| Process tree | `os.getppid()` + `ps -o ppid=,comm=,lstart=` walk | :278-284 | pre-seed `proc_start` in the session cache, or inject; Go: `internal/platform` |
| Local TZ + locale | `time.mktime(time.strptime(lstart, "%a %b %d %H:%M:%S %Y"))` | :286 | `TZ=UTC`, `LC_ALL=C` |
| Network | VictoriaMetrics GET | :165-171 | fake VM HTTP server via `DGX_SL_VM_URL` |
| Env | all `DGX_SL_*`, `LOCAL_MODEL_PREFIXES`, `COLUMNS`, `HOME` | :73-89,444,1186,78 | fixed env per case |
| Filesystem cache | `~/.cache/dgx-llm/statusline-*.json`, `-mix-*`, `-git-*`, `cost-history.json` | :78,217,406,1017,1215 | fresh temp `HOME` per case; seed files explicitly |
| Filesystem | transcript size/content (`os.stat`, incremental offset) | :1010-1013,1042-1052 | fixture files; replay identical refresh sequences |
| Filesystem | `.git` walk from `project_dir` (`os.path.*`, reads HEAD) | :373-393 | fixture dirs; `DGX_SL_GIT=0` for unrelated cases |
| Filesystem/env | `os.getcwd()` fallback | :373 | unreachable in practice (caller requires non-empty dir) |
| TZ | `_iso_ts` for timestamps lacking an offset | :983 | fixtures use `Z`; also set `TZ=UTC` |
| Randomness | `mkstemp` temp names | :201 | not output-affecting |
| Interpreter version | `datetime.fromisoformat` accepted formats (3.11 vs older) | :983 | pin harness Python (3.11+) |

### Proxy (`dgx_proxy.py`) — P3
| Source kind | Read | file:line | Pin strategy |
|---|---|---|---|
| Wall clock (local, formatted) | ledger `t` | :60 | `TZ` + clock shim |
| Wall clock (local, formatted) | decision-log prefix | :72 | same |
| Wall clock | `_t0`, `duration_s` (anth, dgx) | :128,238,273 | shim with a monotonic fake; or mask `duration_s` in diffs |
| Wall clock | failed-req filename ms | :296 | shim |
| Wall clock | trust state `installed_at`, rotate stamp/deadline | :632,709,723-724 | out of P3 scope |
| Process | `os.getpid()` in load note | :518 | mask in decision-log diff |
| Process state | `_logged_unknown` set, `_last_rl` dict, cached key (per-process memory) | :50,181-187,89 | replay in one process, same order |
| Env | `DGX_*`, `LOCAL_MODEL_PREFIXES` at import | :53-54,79-88 | fixed env |
| Filesystem | key file, `~/dgx-llm-obs/` directory listing (sorted) | :93,291 | temp `HOME` |
| External | `security`, `openssl`, `pgrep` (trust CLI) | :568-606 | out of P3 scope |
| Network | upstream responses (SSE chunk boundaries!) | :398-427 | recorded responses replayed with identical chunking |

### Exporter (`dgx_ledger_exporter.py`) — P2
| Source kind | Read | file:line | Pin strategy |
|---|---|---|---|
| Local TZ | `strptime(t).timestamp()` (naive -> local) | :125,145 | `TZ` fixed (must match the TZ the ledger was written in) |
| Filesystem | ledger, hook log, `os.stat` size | :65-66,115,215,282 | fixture files |
| Env | `DGX_OBS_LEDGER`, `DGX_FAKESTOP_LOG`, `DGX_SESSION_LIMIT`, port | :22-25 | fixed env |
| Ordering | `sorted()` of tuple keys; session sort by `-last` (stable over insertion order) | :238,293-380 | Go: stable sort with identical tie order |

### Stop hook (`auto_continue.py`) — P4
| Source kind | Read | file:line | Pin strategy |
|---|---|---|---|
| Wall clock | Kev elapsed (early-break + log text) | :111,118,133,250 | fake Kev with fixed latency; mask `(N.NNs)` |
| Wall clock (local) | log prefix | :197 | `TZ` + shim |
| Network | Kev POST | :113 | fake Kev server via `DGX_KEV_URL`; or unreachable URL for heuristic path |
| Env | `DGX_KEV_*`, `DGX_ENGLISH`, `DGX_AUTOCONTINUE` | :31-36,217,228 | fixed env |
| Filesystem | Kev key file, transcript, log dir | :100,68,195 | temp `HOME` |
| Subprocess | `claude -p` (dead path) | :154 | none (never called) |

### Launcher, preflight, coordinator, backfill — P4/aux
| Source kind | Read | file:line |
|---|---|---|
| Process/env | `whoami`, `$PWD`, `$$`, `$HOME`, `$TMPDIR`, profile.env | `claude-dgx:43-44,74,80,114` |
| Network/ports | `nc -z` scans, mitmdump readiness | `claude-dgx:21,73,77-78` |
| Network | TCP connect | `dgx_preflight.py:23` |
| Process/fs | `lsof`, `flock`, `kill -0`, state files | coordinator `:15,21-23,42-43` |
| Wall clock | `time.time()` cutoff, `os.path.getmtime` | backfill `:95,98` |
| Filesystem order | `glob.glob` order -> history insertion order | backfill `:97` |
| TZ / version | `fromisoformat` | backfill `:39` |

## State Checkpoint
```yaml
pass: 5
status: complete
files_scanned: 11
timestamp: 2026-11-14T05:09:24Z
next_pass: 6
```
