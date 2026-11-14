# Pass 5 deepening, round 1: conventions, env-var inventory, determinism inventory, Python→Go pitfall register (hylo-legacy)

- **Source:** `$HOME/Dev/hylo/legacy/` (11 files, 3,181 lines; read-only, static). Re-read for this round: `dgx_statusline.py:60-215,215-300,315-415,416-640,640-700,975-1060,1180-1245`;
  `dgx_proxy.py:26-200,200-435,440-520,606-640,755-764`; `auto_continue.py:60-140,165-275`; `dgx_ledger_exporter.py:60-72,112-240,268-414`;
  `tools/backfill_cost_history.py:20-121`; `claude-dgx` (whole); `dgx-proxy-coordinator.sh`, `dgx_preflight.py`, both plists (whole).
- **Inputs read:** pass-5 broad sweep, extraction validation, pass-2 deep r1 (§1 stdin, §3 caches, §5 crashes, §6 CONFIG), r2 (§0, §1.4, §6.5-6.8), r3 §0.1-0.2
  (owner capture, env recount E-5), r8 §7 (canonical pointer), pass-3 deep r1 (§A0, §B, §C, §F), r2 §A5/B4, r4 §6-7.2, r7 §1.3/§5, pass-6 synthesis,
  `docs/PLAN.md` (layout, D15, P6), research `general-go-port-parity-crossplatform-2026-11-14.md` (Q2 P1-P27, §2b, Q3a, Q4). Sibling pass-0 deep
  (`…-pass-0-deep-inventory.md` §B.1) was read for interpreter versions only; not edited.
- **Method:** static reading plus isolated scripts that copy legacy expressions, never import a legacy module, and touch no network:
  scratchpad `p5r1/` (`envparse.py`, `shim.py`, `hooks/sitecustomize.py` + `probe.py`, `fma_bf.py`, `intdigits.py`, `strp.py`, `args.zsh`), run with
  `/opt/homebrew/anaconda3/bin/python3` (CPython 3.11.7; `-I` except the shim probe, which needs `PYTHONPATH`) and `/bin/zsh -f` 5.9 for one copied
  zsh pattern. FMA was emulated exactly on 3.11.7 with `fractions.Fraction` (`float(Fraction)` is correctly rounded). Results marked **[pinned]**.
- **Numbering:** retractions **CONV-ABS-47..49** (50-52 unused). New owner items **OD-58..OD-61**. IDs used here: `ENV-01..43` (+ `ENV-I1..I17`),
  `DET-01..52`, `CV-01..18`, `PR-01..21`.
- **Line cites:** bare `:N` = the file named in that row or section. `SL` = `dgx_statusline.py`, `PX` = `dgx_proxy.py`, `HK` = `auto_continue.py`,
  `EX` = `dgx_ledger_exporter.py`, `BF` = `tools/backfill_cost_history.py`, `LN` = `claude-dgx`, `CO` = `dgx-proxy-coordinator.sh`, `PF` = `dgx_preflight.py`.

---

## 0. Audit of the broad sweep (5 hallucination classes) and retractions

| Marker | Prior claim | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-47** | Pass-5 broad §3, proxy rows "ledger `t` :60" and "decision-log prefix :72", hook row "log prefix :197": pin strategy "`TZ` + clock shim". The research doc Q3a says the `time.time` sitecustomize shim is enough "because legacy only calls `time.time()` through the module attribute" | **False for every `strftime` site.** Zero-argument `time.strftime(fmt)` (and `time.localtime()`) read the clock in C, not through the patched `time.time`. With `time.time` patched to 1e9, `time.strftime("%Y-%m-%dT%H:%M:%S")` still returned the real wall time. The shim is enough for the **status line only** (it has no `strftime`). It is not enough for the ledger `t` (PX :60), the decision log (PX :72), the hook log (HK :197), or the trust stamps (PX :632, :709) | **[pinned]** `p5r1/shim.py`: `time.time()` → `1000000000.0`, `time.strftime(...)` → `2026-11-14T08:23:57`. Fix in §B.2 (extended shim, **[pinned]** `hooks/sitecustomize.py`) |
| **CONV-ABS-48** | Pass-5 broad §3, hook row "Kev elapsed (early-break + log text) :111,118,133,250 → fake Kev with fixed latency; mask `(N.NNs)`" | **The fake's latency is not visible under a frozen clock.** Elapsed time is `time.time() - t0` (HK :111,:118). With the shim frozen, it is 0.0 whatever the fake Kev's latency, so `t > KEV_TIMEOUT/2` (HK :133) is never true. The early stop cannot be exercised, and the log always shows `(0.00s)`. To test `:133`, the harness needs a sequenced clock (§B.2 mode 2), not a slow fake | HK :111-118, :127-138; **[pinned]** sequence mode of the shim |
| **CONV-ABS-49** | Pass-5 broad §3, status line row "`os.getcwd()` fallback :373: unreachable in practice (caller requires non-empty dir)", so cwd is not an input | The `getcwd()` branch is unreachable, but **cwd is still an input**: `os.path.abspath(directory)` resolves a **relative** `project_dir`/`current_dir`/`cwd` against the process cwd (SL :373). So the git walk start point, and with it the branch shown and the git cache contents, depend on the status line's cwd for relative inputs. The git cache **key** hashes the raw string (SL :405), so it does not. Claude Code sends absolute paths, so the harness only needs a fixed cwd. `DET-38` | SL :364-395, :405, :452-460 |
| Refinement (class 2, total unchanged) | Pass-2 r3 E-5: "the launcher reads 21 external names (`ANTHROPIC_CUSTOM_HEADERS`, 15 `DGX_*`, `HOME`, `PWD`, `ROUTER_PORT`, `TMPDIR`)" | The itemisation lists 20. The launcher reads **16** `DGX_*` names (USER, SKIP_PREFLIGHT, INVISIBLE, UPSTREAM, PROFILE, MAIN_MODEL, REMOTE, ENGLISH, SAFE, AUTOCONTINUE, KEV_THRESHOLD, KEV_URL, KEV_MODEL, SANDBOX, STATUSLINE, PRINT_ARGS). So 21 holds, and 27 + 21 − 6 = 42 holds | shell recount `grep -o '\${\?[A-Z_]…' claude-dgx` (this round) |
| New input | 42 (pass-2 r2/r3) | **43:** add **`ARGS`**. The launcher never initialises the zsh array `ARGS` before `ARGS+=(…)` (LN :129-139, :180). An exported `ARGS` in the caller's environment is imported as a scalar and becomes the **first element of `claude`'s argv** (LN :183, :185). `HOOKS` and `SETTINGS` are initialised (`:156`, `:163`), so they are not affected | **[pinned]** `p5r1/args.zsh`: `env -i ARGS='--resume x' zsh -f args.zsh` → `claude`, `--resume x`, `--model`, `sonnet` |
| Confirmed | 27 distinct `os.environ` names in the Python files; no `os.getenv`; `TERM` and `LINES` are not consumed; `COLUMNS` is supplied by Claude Code (captured `80`) | — | grep this round; pass-2 r3 §0.1 |
| Confirmed | Mode 0600 caches, `NaN`/`Infinity` tokens in caches, cache write order | — | pass-2 r1 §3.1, r2 §0 |

Class audit: no phantom env var, file or function (classes 3 and 4). One itemisation miscount (class 2; total correct). Metric recount: 43 explicit
inputs (§A). No over-extrapolated token list found in the broad sweep's convention table.

---

## A. ENV-VAR INVENTORY (final)

### A.1 Rules used in the table

- **Parse** is the legacy parse that the `DGX_*` alias has to reproduce during parity (D4). Python `float()`/`int()` grammar (**[pinned]** `envparse.py`):
  surrounding whitespace, `+`, `_` digit separators and non-ASCII Unicode digits are accepted (`" 2 "`, `"+3"`, `"1_0"`, `"٢"`). `int("2.0")`, `int("")` and
  `float("")` raise. `float()` accepts `nan`, `inf`, `-inf` in any case, and `"1e400"` becomes `inf`. Strings over 4,300 digits raise in `int()` (3.11).
- **Env-provided paths are taken literally.** Legacy calls `expanduser` only on its **defaults**, never on a value read from the environment (PX :53-54, :88;
  EX :22-23; PX :563 `Path(env)`; LN :114 `${DGX_PROFILE:-…}`). A value such as `~/x.jsonl` that reaches the process unexpanded (plist, `env`, quoted
  shell) names a directory literally called `~`. See OD-61.
- **Key** follows the CONFIG map (pass-2 r1 §6.1, as amended by r2 §6.8). **HYLO name** follows the OD-01 recommended rule: `HYLO_` + the dotted key in
  upper snake case (`.` → `_`). The rule is pending owner approval (OD-01). "—" = no key (OS or protocol input, dropped, or a CLI action).
- **Crash** = what a bad value does in legacy. "Import" = raised at module import, outside every guard.

### A.2 The 43 explicit inputs

| ID | Name | Default (legacy) | Consumer(s) | Parse | Bad-value behavior | D15 key | HYLO name |
|---|---|---|---|---|---|---|---|
| ENV-01 | `LOCAL_MODEL_PREFIXES` | proxy `claude-sonnet` (PX :86); status line `""` (SL :444, and :902 in `--subagent`); backfill `claude-sonnet` (BF :89); launcher **forces** `claude-sonnet` (LN :38) | proxy routing PX :132; pill SL :446-449; reroute-all SL :487-488; backfill lane BF :77 | `split(",")`, Python Unicode `strip()`, empty items dropped; case-sensitive `startswith` (tuple in the proxy) | no crash. Empty list: proxy routes **nothing** local (`startswith(())` is False), pill `◨ ?`, backfill all `anth`. Status line pill crash CP-S02 needs a non-str `model.id`, not a bad env | `routing.local_model_prefixes` | `HYLO_ROUTING_LOCAL_MODEL_PREFIXES` |
| ENV-02 | `DGX_SERVED_MODEL` | `claude-sonnet-5-5` (PX :84); launcher forces it (LN :39) | model rewrite PX :146-147 | raw string | empty → no rewrite (`if self.served and …`, PX :146) | `backend.served_model` | `HYLO_BACKEND_SERVED_MODEL` |
| ENV-03 | `DGX_UPSTREAM` | `http://192.0.2.10:8080` (PX :79; LN :63 as preflight argument; PF :18 own default) | proxy target PX :80-83, :161-163; preflight PF :19-20 | `urlparse` at **import** (`_router = DGXRouter()`, PX :521): `scheme or "http"`, `hostname or "192.0.2.10"`, `port or 80` | **[pinned]** quirks: `https://h` → port **80** (not 443); `192.0.2.10:8080` (no scheme) → default host and port 80, silently; `dgx:8080` → scheme `dgx`, default host; port `0` → 80. `:abc` or `:99999` → `ValueError` **at import**: mitmdump fails to load the addon (startup exit 1, CONV-ABS-12 class), the trust CLI also dies (PX :521 runs before `__main__` :759), and the preflight prints a traceback and exits 1 (LN :63-66 reports "preflight failed") | `backend.url` | `HYLO_BACKEND_URL` |
| ENV-04 | `DGX_KEY_FILE` | `~/.config/dgx-llm/api-key` (PX :88) | `_key()` PX :91-95, used at PX :164 | literal path; content `strip()` (Python whitespace) | unreadable → P-R4 (credential forwarding, pass-2 r2 §4.6), retried per request | `backend.api_key_file` | `HYLO_BACKEND_API_KEY_FILE` |
| ENV-05 | `DGX_OBS_LEDGER` | `~/dgx-llm-obs.jsonl` (PX :54; EX :22) | ledger writer PX :56-62; exporter EX :66, :115, :282 | literal path | writer: `OSError` swallowed (lost events); exporter: `FileNotFoundError` → empty state; other OSErrors → E-09 | `paths.ledger` | `HYLO_PATHS_LEDGER` |
| ENV-06 | `DGX_PROXY_DECISIONS` | `~/dgx-llm-routing-decisions.log` (PX :53) | `note()` PX :65-74 (also from the trust CLI, see DET-32) | literal path | `OSError` swallowed | `paths.decision_log` | `HYLO_PATHS_DECISION_LOG` |
| ENV-07 | `DGX_TRUST_STATE` | `~/.dgx/trust-state.json` (PX :563) | trust CLI PX :609-622 | `Path(env)` literal | write errors raise (not swallowed) | `paths.ca_state` | `HYLO_PATHS_CA_STATE` |
| ENV-08 | `DGX_PROXY_RESTART_CMD` | unset (PX :719) | `trust rotate` PX :721-725 | run with `shell=True` | any shell text runs | `ca.restart_command` (likely obsolete) | `HYLO_CA_RESTART_COMMAND` |
| ENV-09 | `DGX_SL_VM_URL` | `http://192.0.2.10:8428` (SL :73) | `fetch_sample` SL :165 | `.rstrip("/")` (all trailing slashes) | bad URL → `ValueError`, caught (SL :186) → no sample → `◌ DGX ?` (**[pinned]** empty value → `unknown url type`) | `statusline.telemetry.url` | `HYLO_STATUSLINE_TELEMETRY_URL` |
| ENV-10 | `DGX_SL_TTL` | `4` (SL :74) | `get_sample` SL :324 | `float()` at import | unparsable (incl. `""`) → **CP-X01**: empty stdout, traceback, exit 1. **[pinned]** odd values: `nan`, `-inf`, negatives → refetch on every refresh; `inf`, `1e400` → never refetch after the first success; `4_0` → 40 | `statusline.telemetry.ttl_s` | `HYLO_STATUSLINE_TELEMETRY_TTL_S` |
| ENV-11 | `DGX_SL_ROWS` | `2` (SL :75) | `main` SL :1217, :1224 | `int()` at import | `"2.0"`, `""`, `"nan"` → **CP-X02** (exit 1, empty stdout). `≤ 1` → no row 2; `≥ 3` forces row 2 even below 72 columns | `statusline.rows` | `HYLO_STATUSLINE_ROWS` |
| ENV-12 | `DGX_SL_SPARK` | on (SL :76) | SL :1227 | on iff `!= "0"` | none (`false` = on) | `statusline.sparkline.enabled` | `HYLO_STATUSLINE_SPARKLINE_ENABLED` |
| ENV-13 | `DGX_SL_GIT` | on (SL :77) | `git_segment` SL :400 | on iff `!= "0"` | none | `statusline.git.enabled` | `HYLO_STATUSLINE_GIT_ENABLED` |
| ENV-14 | `DGX_SL_TRACE` | `rate` (SL :89) | `sparkline` SL :662 | `TRACE_KEYS.get(TRACE, "v")`, case-sensitive | unknown, `mine` (retired) or `KV` → `rate` | `statusline.sparkline.trace` | `HYLO_STATUSLINE_SPARKLINE_TRACE` |
| ENV-15 | `COLUMNS` | absent → `0` (SL :1186) | `term_cols` SL :1185-1190, called twice (:1209, :1211) | `int()`, `ValueError`/`TypeError` → 0 | negative → no trim **and** row 2 dropped (BC-SL-055); > 4,300 digits → 0. Production: always numeric (captured `80`) | — (Claude Code protocol input) | — |
| ENV-16 | `DGX_FAKESTOP_LOG` | `~/.cache/dgx-llm/auto-continue.log` (EX :23) | exporter reader EX :214-235. **The writer ignores it**: HK :195-196 hard-codes the same path | literal path | `FileNotFoundError` → no tallies | `paths.hook_log` (OD-04) | `HYLO_PATHS_HOOK_LOG` |
| ENV-17 | `DGX_SESSION_LIMIT` | `50` (EX :24) | trim EX :238 | `int()` at import | unparsable → import crash, then launchd `KeepAlive` restart loop; negative `n` → `[:-n]` drops the n oldest sessions; `0` → no session series (pass-2 r2 §5.1) | `exporter.session_limit` | `HYLO_EXPORTER_SESSION_LIMIT` |
| ENV-18 | `DGX_LEDGER_EXPORTER_PORT` | `9210` (EX :25); bind host hard-coded `0.0.0.0` (EX :414) | `HTTPServer` EX :414; startup print EX :413 | `int()` at import | unparsable → import crash (restart loop). **[pinned]** `< 0` or `> 65535` → `OverflowError` at bind, **after** the startup `rebuild()` (EX :411) and the print (EX :413). `0` → an OS-chosen port that nothing scrapes (socket semantics; not executed) | `exporter.port` (+ `exporter.bind`) | `HYLO_EXPORTER_PORT` |
| ENV-19 | `DGX_KEV_URL` | `http://192.0.2.10:8008/v1/systemone` (HK :31; LN :154 exports the same default) | `kev_pdone` HK :110-113 | raw; `urllib.request.Request(KEV_URL, …)` at HK :110, **outside** the `try` (which starts at :112) | **[pinned]** `""` → `ValueError: unknown url type` at :110 → **hook exit 1, no stdout, no log**, on every stop that reaches the Kev path (new hook crash class, see Remaining Gap 2). `host:port/x` (no scheme) passes `Request()` and fails inside the `try` → treated as unreachable → heuristic | `hook.kev.url` | `HYLO_HOOK_KEV_URL` |
| ENV-20 | `DGX_KEV_MODEL` | hook `kev-latest` (HK :32); the launcher exports a pinned kev-4b id (LN :155), which is the effective value | Kev body HK :105-109 | raw | none | `hook.kev.model` | `HYLO_HOOK_KEV_MODEL` |
| ENV-21 | `DGX_KEV_THRESHOLD` | `0.40` (HK :33; LN :152) | `fake = p_done < KEV_THRESHOLD` HK :249 | `float()` at import | unparsable → H-07 (exit 1). **[pinned]** `nan`, `-inf` → never fake (every Kev verdict is `kev-allow`); `inf` → always fake | `hook.kev.threshold` | `HYLO_HOOK_KEV_THRESHOLD` |
| ENV-22 | `DGX_KEV_TIMEOUT` | `2.5` (HK :34) | `urlopen(timeout=…)` HK :113; early stop `t > KEV_TIMEOUT/2` HK :133 | `float()` at import | unparsable → H-07. **[pinned at `socket.settimeout`]** `-1`, `nan` → `ValueError`, caught (HK :119) → every Kev call "unreachable" → heuristic path. `inf`, `1e400` → `OverflowError`, **not** caught → hook exit 1 on every Kev-path stop. `0` → non-blocking connect → expected `OSError` → unreachable (inferred; not executed: no network) | `hook.kev.timeout_s` | `HYLO_HOOK_KEV_TIMEOUT_S` |
| ENV-23 | `DGX_KEV_MESSAGES` | `14` (HK :35) | **none** (dead) | `int()` at import | unparsable → H-07, although the value is never used | — (accepted, ignored; drop after cutover) | — |
| ENV-24 | `DGX_KEV_CHARS` | `6000` (HK :36) | `"\n".join(lines)[-KEV_CHARS:]` HK :90 | `int()` at import | unparsable → H-07. **[pinned]** `0` → `[-0:]` = the **whole** state (no cap); negative `-n` → `[n:]` drops the **first** n code points | `hook.kev.state_chars` | `HYLO_HOOK_KEV_STATE_CHARS` |
| ENV-25 | `DGX_KEV_API_KEY` | unset → file `~/.config/dgx-llm/kev-api-key` (HK :97-102) | `Authorization` header HK :103-104 | the **value** (secret in env); empty → file fallback (`strip()`) | a value with CR/LF → `http.client` `ValueError`, caught → unreachable (stdlib behavior; not executed) | `hook.kev.api_key_file` (the env value only as a deprecated alias, PLAN §6 secrets-by-file) | `HYLO_HOOK_KEV_API_KEY_FILE` |
| ENV-26 | `DGX_ENGLISH` | `1` (LN :148 exports `${…:-1}`) | hook HK :217; launcher LN :136, :157, :160 | on iff `!= "0"` (both sides) | none | `hook.english.enabled` | `HYLO_HOOK_ENGLISH_ENABLED` |
| ENV-27 | `DGX_AUTOCONTINUE` | `1` (LN :148) | hook HK :228 (off iff `== "0"`); launcher LN :160 (`!= 0`) | string compare | none | `hook.autocontinue.enabled` | `HYLO_HOOK_AUTOCONTINUE_ENABLED` |
| ENV-28 | `DGX_INVISIBLE` | `1` | LN :62, :70, :86, :99 | on iff `== 1` | any other value selects the removed visible mode (needs `opus_router.py`, absent) → startup fails | — (D6: invisible only) | — |
| ENV-29 | `ROUTER_PORT` | unset | LN :17-18, passed to the router LN :92 | raw | visible mode only | — (D6) | — |
| ENV-30 | `DGX_USER` | `$(whoami)` (LN :43) | `X-DGX-User` header LN :45-53 → ledger `user` | raw; inserted unescaped | a newline injects a header line | `attribution.user` | `HYLO_ATTRIBUTION_USER` |
| ENV-31 | `ANTHROPIC_CUSTOM_HEADERS` | appended to (LN :46-53) | Claude Code | newline-joined | — | — (Claude Code protocol) | — |
| ENV-32 | `DGX_SKIP_PREFLIGHT` | `0` (LN :60) | preflight gate | skip iff `== 1` | `true` runs the preflight | `run.preflight` (inverted) | `HYLO_RUN_PREFLIGHT` |
| ENV-33 | `DGX_PROFILE` | `$HOME/.config/dgx-llm/profile.env` (LN :114) | `set -a; source` LN :115 | path; file executed as zsh | arbitrary shell; sourced **after** mitmdump started (BC-LN-006) | — (replaced by hylo profiles; the OD-01 rule yields no name) | — |
| ENV-34 | `DGX_MAIN_MODEL` | `sonnet` (LN :128) | `--model` LN :128-131 | `case`: exactly `opus` → opus; anything else → sonnet | — | `run.main_model` | `HYLO_RUN_MAIN_MODEL` |
| ENV-35 | `DGX_REMOTE` | `0` | LN :133 | on iff `== 1` | `true` = off | `run.remote_control` | `HYLO_RUN_REMOTE_CONTROL` |
| ENV-36 | `DGX_SAFE` | `0` | LN :139 | prompts kept iff `== 1` | `true` = prompts skipped | `run.skip_permissions` (inverted) | `HYLO_RUN_SKIP_PERMISSIONS` |
| ENV-37 | `DGX_SANDBOX` | `0` | LN :165-167 | on iff `== 1` | `true` = off | `run.sandbox` | `HYLO_RUN_SANDBOX` |
| ENV-38 | `DGX_STATUSLINE` | `1` | LN :175-178 | on iff `== 1` | **`true`/`yes` disable the status line** (pass-2 r2 §6.8) | `run.statusline.enabled` | `HYLO_RUN_STATUSLINE_ENABLED` |
| ENV-39 | `DGX_PRINT_ARGS` | `0` | LN :182-184 | on iff `== 1` | — | — (CLI flag `hylo run --print-args`) | — |
| ENV-40 | `TMPDIR` | `/tmp` | mitmdump log paths LN :23, :74; CO :32 | `${TMPDIR:-/tmp}` | macOS `TMPDIR` ends in `/`, giving `//` in the path (harmless) | `paths.proxy_log_dir` | `HYLO_PATHS_PROXY_LOG_DIR` |
| ENV-41 | `HOME` | — | LN :80 (`NODE_EXTRA_CA_CERTS`), :114; every Python `expanduser`/`Path.home()` (SL :78; PX :53-54, :88, :289, :560, :563, :572; HK :100, :195-196; EX :22-23; BF :33, :97) | OS | unset under `set -u` (LN :6) aborts the launcher at :80 | — (OS input; Go `os.UserHomeDir`, which reads `USERPROFILE` on Windows) | — |
| ENV-42 | `PWD` | — | `X-DGX-Project: $(basename "$PWD")` LN :44 → ledger `project` | basename, unescaped | newline injection as ENV-30 | — (domain input: Go `os.Getwd` at `hylo run`) | — |
| ENV-43 | **`ARGS`** (new) | unset | `claude` argv LN :129-139, :180, :183, :185 | zsh: imported scalar, then `ARGS+=(…)` appends | an exported `ARGS` is **prepended to `claude`'s arguments** (**[pinned]**) | — (accident; Go builds argv explicitly; OD-60) | — |

Counts: 43 explicit inputs = 27 Python `os.environ` names + 22 launcher-read names (the r3 21 + `ARGS`) − 6 overlaps (`DGX_AUTOCONTINUE`, `DGX_ENGLISH`,
`DGX_KEV_MODEL`, `DGX_KEV_THRESHOLD`, `DGX_KEV_URL`, `DGX_UPSTREAM`). The coordinator adds only `TMPDIR`. Dispositions: **33** map to a config key
and a `HYLO_*` name (two of them inverted booleans, ENV-32 and ENV-36; ENV-25 becomes a file key; ENV-08 is likely obsolete); **10** have no key
(`COLUMNS`, `DGX_KEV_MESSAGES`, `DGX_INVISIBLE`, `ROUTER_PORT`, `ANTHROPIC_CUSTOM_HEADERS`, `DGX_PROFILE`, `DGX_PRINT_ARGS`, `HOME`, `PWD`, `ARGS`). Import-time crash on a bad value: **9** (`DGX_SL_TTL`, `DGX_SL_ROWS`,
`DGX_KEV_THRESHOLD`, `DGX_KEV_TIMEOUT`, `DGX_KEV_MESSAGES`, `DGX_KEV_CHARS`, `DGX_SESSION_LIMIT`, `DGX_LEDGER_EXPORTER_PORT`, `DGX_UPSTREAM` with a
bad port). Per-call crash on a bad value: **2** (`DGX_KEV_URL` empty or schemeless-invalid; `DGX_KEV_TIMEOUT=inf`).

### A.3 Implicit inputs (read by the interpreter, the stdlib or a child tool; harness parameters, not config)

| ID | Name | Read by | Effect | Pin |
|---|---|---|---|---|
| ENV-I1 | `TZ` | every `strftime`/`localtime` (PX :60, :72, :632, :709; HK :197), naive parses (SL :983; EX :125, :145; BF :39), `mktime` (SL :286) | local-time text and naive-time arithmetic | fixed per case (§B) |
| ENV-I2..I5 | `LANG`, `LC_ALL`, `LC_CTYPE`, `LC_TIME` | Python stdio and `open()` default encoding; `ps` output language (child) | strict vs surrogateescape (BC-SL-076); localized `lstart` breaks the `ps` parse | `LANG=en_US.UTF-8`, the others unset (captured, pass-2 r3 §0.1) |
| ENV-I6..I7 | `PYTHONUTF8`, `PYTHONIOENCODING` | interpreter | switch stdio to UTF-8 mode / another codec (CONTRA-3) | unset |
| ENV-I8 | `PYTHONPATH` | interpreter | where the harness `sitecustomize.py` comes from | the harness hook dir only |
| ENV-I9 | `PYTHONINTMAXSTRDIGITS` (new) | interpreter ≥ 3.11 | moves the 4,300-digit limit (PR-10) | unset |
| ENV-I10 | `PATH` | `python3` (LN :13, :161, :176), `ps` (SL :280), `claude` (LN :185), `nc`, `whoami`, `curl`, `security`/`openssl`/`pgrep` (PX :568-606), `lsof`/`flock` (CO) | which interpreter and tools run | pinned interpreter per component (DET-50) |
| ENV-I11 | `USERPROFILE` | Python `expanduser` on Windows | home directory on Windows | set with `HOME` (research Q3a) |
| ENV-I12..I14 | `HTTP_PROXY`/`http_proxy`, `HTTPS_PROXY`/`https_proxy`, `NO_PROXY`/`no_proxy` | urllib in the hook's Kev call (HK :113). The status line opts out (SL :168) | proxy selection for Kev | see ENV-I15 and DET-26 |
| ENV-I15 | (none set) → **OS proxy settings** (new) | urllib `getproxies()` = `getproxies_environment() or getproxies_macosx_sysconf()` on macOS, `… or getproxies_registry()` on Windows (CPython 3.11 `urllib/request.py:2662-2663, 2716-2723`) | with **no** proxy variable in the environment, the hook's Kev request follows the **system** proxy configuration. In production the launcher's `HTTPS_PROXY` (LN :79) makes the env non-empty, so system settings are skipped | `no_proxy=*` in the harness (makes the env non-empty and bypasses every host) |
| ENV-I16 | `REQUEST_METHOD` | urllib ignores `HTTP_PROXY` when it is set (`urllib/request.py:2519`) | CGI guard; irrelevant in production | unset |
| ENV-I17 | `SSLKEYLOGFILE`, `MITMPROXY_SSLKEYLOGFILE` | mitmproxy at import (pass-2 r7 T-3) | TLS secrets written to a file | unset (confirmed unset in production, r8) |
| negative | `PYTHONHASHSEED` | — | **no output effect**: sets are used only for membership (PX :50, :505-507; SL :1034), dict iteration is insertion order, `dict.fromkeys` keeps order (PX :514), and SL :402-405 uses sha1 instead of `hash()` on purpose | none needed |

Launcher outputs (written for children, not read): `LOCAL_MODEL_PREFIXES` (:38), `DGX_SERVED_MODEL` (:39), `ANTHROPIC_CUSTOM_HEADERS` (:47/:51),
`HTTPS_PROXY` (:79), `NODE_EXTRA_CA_CERTS` (:80), `API_TIMEOUT_MS=1800000` (:104), `CLAUDE_CODE_AUTO_MODE_SERVER=0` (:109), `DGX_ENGLISH`,
`DGX_AUTOCONTINUE` (:148), `DGX_KEV_THRESHOLD` (:152), `DGX_KEV_URL` (:154), `DGX_KEV_MODEL` (:155), `PYTHONUNBUFFERED=1` (mitmdump only, :75; CO :31),
`ANTHROPIC_BASE_URL` unset (:71, :100; exported only in the dead visible mode :102), `ROUTER_PORT` (router child only, :92), plus everything in
`profile.env` (`set -a`, :115).

---

## B. DETERMINISM INVENTORY (final; the P1-P4 harness pinning list)

### B.1 Table

Go injection points use the names proposed in research Q3a and PLAN §6: `statusline.Env{Now, Getenv, Home, Cwd, Stdin, Stdout, Loc}`, a telemetry
client built from config, `platform.ProcessStart` (interface), and one `Clock` per long-running component.

| ID | Class | Site (file:line) | Output effect | Pin (legacy side) | Go injection point |
|---|---|---|---|---|---|
| DET-01 | wall clock, `time.time` | SL :231 `record_cost` | throttle + `ts` in cost-history | shim mode 1 (constant) | `Env.Now` |
| DET-02 | same | SL :243 `cost_thresholds` | 30-day window | shim mode 1 | `Env.Now` |
| DET-03 | same | SL :304 `effective_rl` | `rl_ts`, 1,800 s keep | shim mode 1 | `Env.Now` |
| DET-04 | same | SL :322 `get_sample` | TTL, `ts`, `fetch_ts`, history `t`, `(~Ns old)` | shim mode 1; step the value between refreshes | `Env.Now` |
| DET-05 | same | SL :408 `git_segment` | 5 s TTL, `ts` | shim mode 1 | `Env.Now` |
| DET-06 | same | SL :499 limits | expiry, projection, countdown | shim mode 1 | `Env.Now` |
| DET-07 | same | SL :558 window age ⌂ | `⌂` text and 5-min gate | shim mode 1 + seeded `proc_start` | `Env.Now` (read once per render) |
| DET-08 | same, **two reads** | SL :825 and :826 idle | gate and age can straddle a minute with a live clock | shim mode 1 (one value) | one `Now` per render |
| DET-09 | same, **eager default** | PX :128 `_t0`; PX :238 and :273 `round(time.time() - getattr(flow, "_t0", time.time()), 3)` evaluates `time.time()` **twice** (the default is evaluated even when the attribute exists) | ledger `duration_s` | constant clock → `0.0`; P3 replay masks `duration_s` (P3r4 legend). A sequenced clock makes the value depend on the read count (**[pinned]** sequence probe) | proxy `Clock`; Go must not try to match read counts (mask) |
| DET-10 | same | PX :296 `failed-req-<ms>.json` | file name on disk (not compared) | none | proxy `Clock` |
| DET-11 | same (dead) | PX :530, :535 | `ws_closed` never fires (`_ws_started` never set) | none | — |
| DET-12 | same + sleep | PX :723-725 trust rotate deadline, `time.sleep(0.5)` | OOS (`hylo ca`) | — | — |
| DET-13 | same, **behavior-affecting** | HK :111, :118 Kev elapsed → log `(N.NNs)` (HK :250) and early stop `t > KEV_TIMEOUT/2` (HK :133) | log text; number of Kev calls; H-04 reachability | mode 1 → elapsed 0.0, 3 tries always (matches a fast production Kev). Early-stop cases need **mode 2** with the exact read count: 1 read per failed attempt (:111), 2 per successful attempt (:111, :118) (CONV-ABS-48) | hook `Clock` read at the same two points |
| DET-14 | same | BF :95 `--days` cutoff vs `getmtime` | which transcripts are scanned | shim mode 1 + fixture mtimes (`os.utime`) | `Clock` + injected `fs.FS` stat |
| DET-15 | **C-level clock (not shimmed by patching `time.time`)** | PX :60 ledger `t` | every ledger line | **extended shim** (§B.2) or mask `t` (P3r4 legend masks it) | `Clock` formatted in `Loc` |
| DET-16 | same | PX :72 decision-log prefix | decision log (OOS for parity) | extended shim | `Clock` |
| DET-17 | same | HK :197 hook log prefix | hook log line, parsed by the exporter for tallies only | extended shim | hook `Clock` |
| DET-18 | same | PX :632 `installed_at`, PX :709 backup stamp | OOS | — | — |
| DET-19 | time zone | SL :983 `fromisoformat(...).timestamp()`; naive → local | turn-rate spans for naive transcript timestamps | fixtures use `Z` and offsets; add one naive-timestamp case per TZ | `Env.Loc` |
| DET-20 | time zone + libc | SL :286 `mktime(strptime(lstart))` | `proc_start` | bypassed by seeded `proc_start` | `platform.ProcessStart` returns Unix seconds (truncated) |
| DET-21 | time zone | EX :125, :145 `strptime(t, "%Y-%m-%dT%H:%M:%S").timestamp()` | `last_*` gauges, session order | TZ = the TZ the fixture ledger was written in. **[pinned]** lenient: `2026-1-5T3:4:5` parses; `…Z`, fractions and a leading space raise (caught). DST: the repeated 01:30 maps to the **first** occurrence (fold 0); a spring-gap 02:30 maps to 03:30 local | `ledger.Rebuild(…, loc)` with a Python-lenient parser |
| DET-22 | time zone + version | BF :39 `fromisoformat` | span, `ts` | fixtures with `Z`; 3.11 grammar | `Loc` |
| DET-23 | time zone | all DET-15..18 strftime text | local wall time, no offset | fixed TZ | `Loc` |
| DET-24 | monotonic clock | **none** (negative). No `time.monotonic`/`perf_counter` anywhere; every duration is a wall-clock difference (DET-09, DET-13) | NTP steps change durations | — | Go durations must come from the injected `Clock` during parity (not `time.Since`, which uses the monotonic reading) |
| DET-25 | network | SL :165-171 VM GET (proxies disabled :168, 1.5 s timeout) | row 2 | fake VM (`httptest`) via `DGX_SL_VM_URL`; failures by closed listener / 5xx / bad JSON, never by timeout | telemetry client from config, `Transport.Proxy = nil` |
| DET-26 | network + **OS proxy discovery** | HK :110-113 Kev POST; urllib proxy selection (ENV-I12..I15) | Kev verdict, hook decision | fake Kev via `DGX_KEV_URL` **and** `no_proxy=*` (otherwise a clean env on macOS/Windows falls back to system proxy settings) | hook Kev client from config; `http.ProxyFromEnvironment` never consults system settings, so pin the env |
| DET-27 | network | PF :23 TCP connect, 4 s | launcher abort | P4 test: closed port / unroutable sentinel | `platform`/`doctor` dialer |
| DET-28 | network | proxy upstream (mitmproxy) | replies, SSE chunking | recorded replies; boundary-insensitivity oracle (BC-PX-045) | proxy upstream `RoundTripper` |
| DET-29 | network/ports | LN :21, :73, :77-78 `nc -z` scans | chosen port → `HTTPS_PROXY` value and log name | P4: occupy ports deterministically or accept any port | `net.Listen(":0")` or injected listener |
| DET-30 | process/ports | CO :15, :28 `lsof`; :23 `kill -0` | OOS (coordinator never invoked) | — | — |
| DET-31 | process tree | SL :278 `os.getppid()`; :280-286 `ps -o ppid=,comm=,lstart=` walk (≤ 6 levels, 1 s timeout, `PATH`, child locale) | ⌂ | **seed `proc_start` (a number) in `statusline-<sid>.json`** (SL :273-275 returns it before any `ps`) | `platform.ProcessStart` interface; per-OS unit tests; seconds truncation (BC-SL-080) |
| DET-32 | process id | PX :518 `note("addon module loaded (PID %d)")`; it also runs in **trust CLI mode** (module level, before `__main__` :759) | decision-log line | mask | — |
| DET-33 | process ids | LN :23, :74 `$$`; :76, :93 `$!`; PX :606 `pgrep` | log file names; rotate guard | none (not compared) | — |
| DET-34 | per-process memory | PX :50 `_logged_unknown`; :181-187 `_last_rl` (unbounded); :89-95 `_key_cache` | decision-log notes once per process; `anth_ratelimit` only on change | replay one flow sequence in one process, same order | `Router` struct fields |
| DET-35 | cache files | SL :78 dir; `statusline-<sid>.json` (:1215), `-mix-` (:1017), `-git-` (:405), `cost-history.json` (:217) | every row-1/row-2 widget with memory | fresh temp `HOME` (+`USERPROFILE`) per case; seed files explicitly; compare all four after **every** step (BC-SL-077) | `Env.Home` |
| DET-36 | file size + bytes | SL :1009-1058 transcript `stat` size, offset, 512 KB window | composition, tokens, turn rate | fixture transcripts; identical growth and refresh sequence | `Env` file access |
| DET-37 | filesystem walk | SL :373-393 `.git`, `gitdir:`, `HEAD` | branch | fixture dirs created at test time (a committed `.git` is not tracked) | `Env` |
| DET-38 | **cwd** (new) | SL :373 `abspath` of a relative project dir | branch | fixed harness cwd; absolute templated paths | `Env.Cwd` |
| DET-39 | filesystem | PX :93 key file; :291 `sorted(glob("failed-req-*.json"))` prune; ledger/decision appends | P-R4; disk artifacts | temp `HOME` | proxy config paths |
| DET-40 | file content + size | EX :66, :115, :215, :282 | the whole exposition (BC-EX-027 size trigger) | fixture ledger and hook-log bytes; TZ | `Rebuild(ledger, hooklog io.Reader, loc, limit)` |
| DET-41 | filesystem | HK :100 Kev key file, :68 transcript, :195-196 log | Kev auth; state text; log | temp `HOME` | hook config paths |
| DET-42 | filesystem order + mtime | BF :97 `glob` order, :98 `getmtime`, :91 history | session key order in the output file; duplicate-sid winner | fixture tree with one file per directory; `os.utime` | sorted or injected listing (deviation needs a note, OD-36) |
| DET-43 | environment | all of §A | — | fixed env per case, built from scratch (`cmd.Env`), never inherited | `internal/config` resolved once |
| DET-44 | locale, stdio | SL :1201-1204 stdin, :1234 stdout; HK :211 stdin, :206 stdout | `{}` on invalid UTF-8; degraded on lone surrogates (CP-S17); H-09 | `LANG=en_US.UTF-8`; `LC_ALL`, `LC_CTYPE`, `PYTHONUTF8`, `PYTHONIOENCODING` unset (captured; owner ruling) | byte-level stdin with explicit UTF-8 validation; surrogate check before write |
| DET-45 | locale, file text mode | SL :192 caches, :380, :385 git files; HK :68 transcript, :196 log; EX :115, :215 (exporter under launchd = UTF-8 mode on 3.9.6, pass-2 r2 §1.4); BF :44 (`errors="replace"`); PX :59, :71 | decode failures → `{}`/skip/crash per site (E-09, H-05) | same locale; exporter run with an **empty env** like launchd | explicit UTF-8 decoding rules per site |
| DET-46 | locale, child process | SL :280-281 `ps` inherits `LANG`/`LC_TIME`; `text=True` decodes with the locale; Python `strptime` uses C-locale names (Python never sets `LC_TIME`) | localized `ps` → no ⌂, not cached (re-walk every refresh) | seeded `proc_start` | native probe, no text parsing |
| DET-47 | randomness | `mkstemp` names SL :201, BF :113, PX :618 | only a leaked temp file on a failed replace | none | `os.CreateTemp` (name pattern differs; output-neutral) |
| DET-48 | randomness / hashing | **none** (negative): no `random`, `uuid`, `secrets`; `PYTHONHASHSEED` has no output effect (§A.3 "negative" row) | — | — | never `range` over a Go map for output (PR-19) |
| DET-49 | terminal size | SL :1186 `COLUMNS` only; no `get_terminal_size`/ioctl; `LINES`, `TERM` unread | width trim, row-2 gate | `COLUMNS` explicit per case (numeric; production `80`) | `Env.Getenv("COLUMNS")` with Python `int()` grammar |
| DET-50 | interpreter version | status line, hook, backfill, trust CLI: 3.11.7; proxy + preflight: 3.12.10 venv with mitmproxy 12.3.1; exporter: `/usr/bin/python3` 3.9.6 | `fromisoformat` grammar, int-digit limit (≥ 3.11 only), UTF-8 mode defaults | pin per component (sibling pass-0 deep §B.1; OD-47) | Go reproduces the oracle of each component (e.g. no digit limit in the exporter) |
| DET-51 | input ordering | SL :175-184 VM result order (first wins); PX :178-179 header iteration order → `anth_ratelimit` key order; parsed-JSON insertion order everywhere; EX :238, :293-380 stable `sorted()` | output order | fixtures fix the order; recorded headers keep their order | ordered decode; `slices.SortStableFunc` |
| DET-52 | concurrency | Claude Code debounces (300 ms) and cancels in-flight status-line runs; caches are last-writer-wins, atomic per file (SL :198-206); one mitmdump per window appends to one ledger (PX :58-60) | interleaved cache states; interleaved ledger lines | harness runs refreshes serially | per-file atomic replace; one `Write` per ledger line (CV-04) |

**Count: 52 determinism rows.** By class: wall clock 14 (DET-01..14), C-level clock 4 (DET-15..18), time zone 5 (DET-19..23), monotonic 1
(negative), network 6 (DET-25..30), process 4 (DET-31..34), filesystem 8 (DET-35..42), environment 1 (DET-43, §A), locale 3 (DET-44..46),
randomness 2 (one negative), terminal 1, interpreter 1, ordering 1, concurrency 1. New versus the broad sweep: DET-09 (eager default), DET-13
(behavior-affecting read count), DET-15..18 (shim gap), DET-21 (strptime leniency and DST), DET-24, DET-26 (OS proxy fallback), DET-38 (cwd),
DET-46 (child locale), DET-48, DET-49, DET-50 (`PYTHONINTMAXSTRDIGITS` and the per-component versions), DET-52.

### B.2 The clock shim, corrected (harness only; lives under `internal/*/testdata/pyhooks/`, never in `legacy/`)

**[pinned]** `p5r1/hooks/sitecustomize.py` with `PYTHONPATH=hooks` (Python must run **without** `-I`/`-S`, which disable `sitecustomize`):

```python
import os, time as _t
_seq = [float(x) for x in os.environ.get("HYLO_TEST_CLOCK_SEQ", "").split(",") if x]
_now = os.environ.get("HYLO_TEST_NOW")
if _now is not None or _seq:
    _lt, _gt, _sf = _t.localtime, _t.gmtime, _t.strftime
    def _time():
        if _seq:
            return _seq.pop(0) if len(_seq) > 1 else _seq[0]   # last value sticks
        return float(_now)
    _t.time = _time
    _t.localtime = lambda secs=None: _lt(_time() if secs is None else secs)
    _t.gmtime = lambda secs=None: _gt(_time() if secs is None else secs)
    _t.strftime = lambda fmt, tup=None: _sf(fmt, _t.localtime() if tup is None else tup)
```

- **Mode 1 (constant, `HYLO_TEST_NOW`)**: froze `time.time()` **and** `time.strftime(...)` (`1000000000.0`, `2001-09-09T01:46:40` under `TZ=UTC`).
  Use for P1, P2 and P3, and for P4 hook cases without early stop.
- **Mode 2 (sequence, `HYLO_TEST_CLOCK_SEQ`)**: each read takes the next value. The probe showed that a zero-argument `strftime` **consumes a
  value** too, so the sequence has to be written for the exact read order of the code path. Use only for the Kev early-stop cases (DET-13), where
  the read order is short and fixed.
- Not patched, and not needed: `time.mktime`/`time.strptime` (pure functions of their argument), `datetime` (legacy uses only `fromisoformat` and
  `strptime`, never `now()`).
- Go side: one `Clock` interface per component. Status line: read once per render (approved output-neutral deviation from DET-08). Hook: read at
  the same two points as HK :111/:118, so mode-2 cases reproduce. Proxy: durations masked, no read-count matching.

### B.3 Per-phase pin sets

| Phase | Clock | Network | Process | Filesystem | Env/locale | Interpreter |
|---|---|---|---|---|---|---|
| P1 status line | mode 1, stepped between refreshes | fake VM | seeded `proc_start` | temp `HOME`+`USERPROFILE`, fixture transcript and `.git`, fixed cwd | §A rows for SL; `LANG=en_US.UTF-8`; `TZ` fixed (UTC plus one DST zone for naive cases); `COLUMNS` | 3.11.7 |
| P2 exporter | none (reads `t` text) | none | — | fixture ledger and hook log | empty env except `TZ`, `HOME`, `DGX_*` paths (launchd-like); `TZ` = ledger's | 3.9.6 |
| P3 proxy | mode 1 or mask `t`/`duration_s` (P3r4) | recorded upstream | one process per replay | temp `HOME`, key file | `DGX_*`, `LOCAL_MODEL_PREFIXES`, `TZ`; `SSLKEYLOGFILE` unset | 3.12.10 + mitmproxy 12.3.1 (OD-47) |
| P4 hook | mode 1; mode 2 for early stop | fake Kev + `no_proxy=*` | — | temp `HOME`, transcript | `DGX_KEV_*`, `DGX_ENGLISH`, `DGX_AUTOCONTINUE`, `LANG`, `TZ` | 3.11.7 |
| P4 launcher | — | port occupancy | `$$`, `$!` unmasked only in names | temp `HOME`, `profile.env` fixture | env built from scratch (no `ARGS`) | zsh 5.9 |

---

## C. CODING CONVENTIONS relevant to the port

| ID | Convention (legacy) | Evidence | Go equivalent | Ties |
|---|---|---|---|---|
| CV-01 | **Atomic replace, swallow-all (status line caches).** `makedirs(CACHE_DIR, exist_ok=True)` on every save; `mkstemp(dir=CACHE_DIR, prefix=basename+".")` → file mode **0600**; `json.dump`; `os.replace`; no `fsync`; any exception → `pass`; a failed replace **leaks** the temp file. Because `os.replace` keeps the temp file's mode, every cache file ends up 0600 whatever the umask | SL :198-206 | `os.MkdirAll`; `os.CreateTemp(dir, base+".*")` (0600); write; `Close`; `os.Rename`; on error remove the temp (output-neutral deviation: no leak). On Windows, ignore sharing violations as legacy does (research Q4b) | BC-SL-052, BC-SL-070, BC-SL-077 (order), PR-08 |
| CV-02 | **Atomic replace, errors propagate (backfill).** Same shape, but prefix `cost-history.` (not `cost-history.json.`) and no `try`: a failure aborts with a traceback | BF :111-116 | same helper with `returnErr=true` | BC-BF-012, OD-36 |
| CV-03 | **Atomic replace, different JSON style (trust state).** Hidden prefix `.trust-state.`; `json.dump(indent=2, sort_keys=True)` plus a trailing `\n`; parent dirs created; errors propagate | PX :616-622 | OOS (replaced by `hylo ca`); noted so nobody copies CV-01 here | BC-PX-031 |
| CV-04 | **Append, one write per record, mode from umask.** Ledger, decision log and hook log open the file in `"a"` mode **per record** and write one complete line. Ledger and decision log catch `OSError` only; the hook log catches `OSError` only, so `UnicodeEncodeError` escapes (H-09). Files are created with the umask (typically 0644), **not** 0600 like the caches. Several mitmdump processes append to one ledger concurrently and rely on `O_APPEND` plus one write per line | PX :56-62, :65-74; HK :193-201 | `os.OpenFile(O_APPEND\|O_CREATE\|O_WRONLY, 0o666)`, build the full line, one `Write`. Ledger perms per umask for parity (tightening is a post-cutover decision) | BC-PX-006, BC-PX-048, H-09, DET-52 |
| CV-05 | **JSON output styles (four).** **J1** `json.dumps`/`json.dump` defaults: separators `", "` and `": "`, `ensure_ascii=True`, `allow_nan=True`, insertion order, float `repr`, no trailing newline: ledger lines (+`\n`, PX :60), status line caches (SL :203), cost history (SL :203 via `save_cache`; BF :115), DGX body rewrite (PX :150), Kev request body (HK :105-109, `.encode()`), hook stdout (`print` adds `\n`, HK :206). **J2** `sort_keys=True`, default separators: the `_last_rl` change key (PX :185), internal only. **J3** `indent=2, sort_keys=True` + `\n` (PX :620-621; item separator `,`, key separator `": "`). **J4** hand-built by string concatenation, no escaping: launcher `--settings` (LN :156-181) | as cited | `internal/pyjson.Dumps(v, Opts{SortKeys, Indent})` over an ordered value tree; J4 via the same encoder (deviation: the launcher's unescaped `<HERE>` hazard disappears; output equal for ordinary paths) | BC-PX-041, BC-HK-021, BC-LN-009, PR-07, PR-08 |
| CV-06 | **Ledger record shape.** `{"t": local strftime, "event": name, **fields}`; field order = keyword order at the call site; `ev = dict(attrib); ev.update(…)` keeps existing keys in place and appends new ones (PX :236-245) | PX :56-62, call sites | ordered struct-to-pairs writer per event type; `t` from `Clock` in `Loc` | D7, ledger schema (P2r4 §3.2), DET-15 |
| CV-07 | **Log line formats.** Ledger `t` `%Y-%m-%dT%H:%M:%S` (local, no offset). Decision log `%Y-%m-%d %H:%M:%S ` + `msg % args`; `%s` renders Python `str()` (tuples `(12, 34)`, `None`, lists with `repr` items `['type', 'tool']`); formatting errors are swallowed and the raw template is written; 11 templates (PX :108, :135, :140, :167, :240, :286, :297, :309, :321, :510, :518). Hook log: `%Y-%m-%d %H:%M:%S [kind] kev=… session=<str()> stop_hook_active=<str()> tail=<repr()>` (HK :197-199; grammar in pass-2 r2 §6.5) | as cited | `pytime.Strftime(loc)`; `pyfmt.Str` and `pyfmt.Repr`. Decision-log text is OOS for parity (P3r4 legend); the hook log is parsed by the exporter, so its `[kind]` tokens and `p_done=` must stay | BC-HK-021, BC-HK-023, BC-EX-014/019, PR-16 |
| CV-08 | **Error-handling ladder.** E1 one top-level `except Exception` → a fixed degraded line, exit 0 (SL :1238-1245); import-time env parsing sits **outside** it (CP-X01/X02). E2 "never raise" helpers: `except Exception: return {}`/`None`/`pass` (SL :186, :190-195, :198-206, :293, :394; PX :176-190, :404-407). E3 narrow catches that let other classes escape: `except OSError` (PX :61, :73; HK :84, :200), `except ValueError` (HK :72, :212; EX :119, :133, :147), `except (ValueError, TypeError)` (PX :107, :234, :307; SL :1189), `except (OSError, URLError, ValueError, KeyError)` (HK :119). E4 no guard at all: hook `main`, exporter `do_GET` and startup, backfill `main`. E5 exceptions as parse results (`_fmt_lines` → `?` SL :849-860; `_iso_ts` → `None` SL :977-985) | as cited | E1: one `recover` + `errDegraded` at the top of `hylo statusline`, config parsed **before** it. E3/E4: per-site predicates that reproduce which inputs escape (the crash catalogues), not a blanket recover | PT-EXC, CP-*, P-*, E-*, H-*, B-* |
| CV-09 | **Env read at import into UPPER_SNAKE module constants, with string defaults** (`float()`/`int()` there) | SL :73-100; HK :31-36; EX :22-25; PX :53-54 | `internal/config` resolves once at startup: config file → `HYLO_*` → `DGX_*` alias → default (D15) | §A, CP-X01/X02, H-07 |
| CV-10 | **Env booleans by per-variable string comparison** (`!= "0"` for some, `== "1"` for others) | pass-2 r2 §6.8 | alias table with the legacy predicate per `DGX_*` name; typed booleans for `HYLO_*` (OD-05) | ENV-12/13/26/27/32/35-39 |
| CV-11 | **Paths: `expanduser` on defaults only**; env values literal | §A.1 | OD-61 | ENV-04..07, -16, -33 |
| CV-12 | **Python value idioms**: `x.get(k) or default` (falsy = missing), `isinstance(x, (int, float))` (accepts `bool`, accepts NaN) | SL :420, :540, :602, :1105-1112 and passim | `pyfmt.Truthy`, `pyfmt.Num` over a decoded `any` tree | PR-06, BC-SL-018/035/036 |
| CV-13 | **Stable digests, never `hash()`** for persisted names (`sha1(dir.encode("utf-8","replace")).hexdigest()[:16]`); mix-cache sid sanitizer `re.sub(r"[^A-Za-z0-9_-]", "_", sid)[:40]` | SL :402-405, :1017 | `crypto/sha1` (gosec G401/G505 suppressed with a reason); sanitizer applied per rune | BC-SL-070, OD-03 |
| CV-14 | **Measurement units are Python's**: code points, `json.dumps` characters, 2,000 per image (never bytes) | SL :1120-1149 | `pystr.Len`, `pyjson.DumpsLen` | CONV-ABS-2, PR-08, PR-11 |
| CV-15 | **Output assembled once, written once.** Segments joined by `SEP`, rows by `\n`, one `print` (so an encode failure writes nothing) | SL :128, :1230-1234 | `strings.Builder`, one `os.Stdout.Write`; check encodability first | BC-SL-003, CP-S17 |
| CV-16 | **Schema versioning by a marker key** (`mixv6`): its absence forces a full re-parse | SL :1025-1038 | same marker and same reset rule | BC-SL-065 |
| CV-17 | **Process state in module globals** (proxy `_logged_unknown`, `_router` attributes; exporter globals with `state_lock`); a mitmdump live reload resets them | PX :50, :89, :181-187, :521; EX :60-61 | fields on a `Router`/`Exporter` struct; no reload in Go | DET-34 |
| CV-18 | **Naming.** UPPER_SNAKE constants; `_private` helpers; env prefixes `DGX_`, `DGX_SL_`, `DGX_KEV_` (exception `LOCAL_MODEL_PREFIXES`); ledger events `dgx_*`/`anth_*`/`bridge_ws_*`; metrics `dgx_llm_*`; rationale comments citing review items (`(review 2026-11-13, #N)`) | passim | Go: CamelCase identifiers; dotted snake config keys; `HYLO_*` env (OD-01); ledger event and metric names frozen (D7); every threshold keeps its rationale comment (CLAUDE.md rule) | D7, D15 |

**Count: 18 conventions.** New versus the broad sweep: CV-02/03 (three atomic-write variants, not one), CV-04 (umask perms, concurrency), CV-05
(four JSON styles), CV-06, CV-07 (decision-log `%s` rendering and template list), CV-08 (the full ladder), CV-11, CV-13, CV-15.

---

## D. PYTHON→GO PITFALL REGISTER (consolidated)

Tags from pass-3 r1 §C are kept. Two tags are added: **PT-FREPR** (float `repr`, previously folded into PT-JSONLEN/PT-STR) and **PT-INTLIM**
(the 3.11 integer-digit limit). Universal-newline text iteration is a new sub-case of PT-SPLIT. Test types: **T** = table test with expected values
generated by CPython (committed generator), **F** = differential fuzz against CPython, **G** = golden/replay through the parity harness.

| ID | Tag | Pitfall | Occurrences (file:line) | Reach | Go remedy | Test |
|---|---|---|---|---|---|---|
| PR-01 | PT-ROUND | `round(x)` ties to even and returns int; `round(x, n)` rounds the exact binary value | SL :1171 composition %; SL :234 and BF :108 `round(usd, 4)`; PX :238, :273 `round(dt, 3)` (ledger `duration_s`); PX :213 `round(…, 1)` (bridge, never fires). Deliberate half-up `int(x + 0.5)`: SL :426, :675 (identical in Go) | production | `pyfmt.Round` (`math.RoundToEven`; NaN → `ValueError` path, ±inf → `OverflowError` path), `pyfmt.RoundN` (CPython algorithm via `strconv`, research P2) | T (ties 0.5, 2.5, 2.675, 0.125), F |
| PR-02 | PT-FMT | `{:.Nf}` correctly rounded half-even on the binary value; `nan`/`inf`/`-inf` spelling; `-0` | SL :435-437, :479, :522, :599, :612, :616, :625, :635, :700, :741, :761-762, :778-783, :795, :813-819, :857, :870-873, :882-885 (research §2b list); HK :250 (`.3f`, `.2f`), :256 (`.2f`); EX :298 (`.0f`), :333, :353 (`.3f`), :364, :370, :374 (`.0f`), :398 (`.3f`) | production (finite); NaN latent (VM capture all finite, P3r7 §5) | `pyfmt.F(x, n)`: `strconv.FormatFloat(x,'f',n,64)` plus Python spellings for non-finite values | T, F |
| PR-03 | PT-FDIV | float `//` and `%` are fmod-based, `%` takes the divisor's sign; `inf // x` is NaN | SL :525-529, :546, :560-561, :826 (float); int `//`/`%`: SL :548, :561, :829-831, :859; HK :138 | production; divergence theoretical for these divisors (CONTRA-1) | `pyfmt.FloorDiv`/`Mod` (port of CPython `float_divmod`); int helpers | T (boundaries), F (2M samples) |
| PR-04 | PT-NANMM | `max`/`min` keep the first argument unless the second compares greater; `max(list)` likewise | SL :146, :422, :479, :508, :671 (`max(max(vals), floor)`), :674-675, :758-759; EX :126, :130, :132, :145 (finite by construction); PX :384-396 (ints) | latent (no NaN from VM in production) | `pyfmt.Max(a,b)`, `pyfmt.MaxSeq` in the same argument order | T (NaN in each position) |
| PR-05 | PT-INT | `int()` truncates and raises on NaN/inf; `math.ceil(nan)` raises; `int(True)` = 1; `int("12")` parses | SL :148, :426, :546, :675, :683, :759, :853 (`OverflowError` not caught, CP-S11); PX :243, :250-253, :277-282, :352-357, :392-396, :418; EX :152-176 (E-04/E-05); HK :118 (`float(p)` accepts `bool`) | production for ints; crash paths on bad input | `pyfmt.Int` (finiteness check, Python string grammar, bool → 0/1) | T |
| PR-06 | PT-BOOL | `bool` is an `int`; truthiness defaults (`or 0`, `or ""`, `or {}`) | SL :420, :478, :506, :535, :540, :551, :557, :585-598, :602, :622, :628, :993, :1079, :1105-1112; PX :112, :118-127, :243; EX :150-210; HK :214, :226; BF :70-76 | production | `pyfmt.Truthy`, `pyfmt.Num` | T |
| PR-07 | **PT-FREPR** (new tag) | float `repr`: shortest round-trip digits, exponent iff < 1e-4 or ≥ 1e16, `.0` on integral values, `e-05`/`e+16` | `json.dumps` floats: SL :203 (cache `t`, `ts`, `fetch_ts`, samples, `lr`, `lu`, `t0`, `t1`, `usd`), PX :60 (`duration_s`), PX :150 (DGX body floats, e.g. `top_p`), BF :115 (`usd`, `api_ms`, `ts`); `str()` of a non-str label (SL :442, :453); `%s` in decision-log notes (OOS) | production | `pyfmt.Repr` (digits from `FormatFloat(f,'e',-1,64)`, re-laid out with CPython `'r'` rules, research P14) | T (P3r2 A5 rows 18-32, 59-63), F |
| PR-08 | PT-JSONLEN | `json.dumps` length and escaping (separators, `ensure_ascii` with surrogate pairs, NaN tokens, insertion order, duplicate keys last-wins-first-position, no HTML escaping) | measurement: SL :1138, :1140, :1147; outputs: CV-05 J1-J3 sites | production | `internal/pyjson.Dumps`/`DumpsLen` over an ordered tree with `json.Number` | T (63-row oracle, P3r2 A5), F |
| PR-09 | PT-JSONIN | `json.loads` leniency: NaN/Infinity literals, big ints, duplicate keys, bytes input (BOM/UTF-16/32/CESU accepted, invalid UTF-8 rejected), text input under strict locale, depth → `RecursionError` | SL :1202 (stdin), :1061 (transcript bytes), :171 (VM), :193 (caches); PX :106, :226, :306, :332, :414; EX :81, :118; HK :71, :114, :211; BF :46, :91 | production for the common subset; edges latent | `pyjson.Loads(bytes, mode)` (mode = bytes or text) with Python's acceptance set | T, F |
| PR-10 | **PT-INTLIM** (new tag) | CPython ≥ 3.11 rejects int literals and `int()` strings over 4,300 digits (`ValueError`); `json.dumps` of such an int also raises; `float()` and float literals are unaffected (`inf`) | **[pinned]** SL :1202-1204 stdin → `{}`; SL :1061-1063 transcript line → skipped; SL :171/:186 VM → no sample; SL :193 cache → `{}`; SL :1188 `COLUMNS` → 0; SL :75 `DGX_SL_ROWS` → CP-X02; SL :853 `_fmt_lines` → `?`; PX :106 (3.12.10: limit applies) → "unparseable" pass-through; **EX on 3.9.6: no limit** (big ints parse and count) | edge only | enforce the limit in `pyjson`/`pyfmt.ParseInt` per component oracle (off for the exporter); `PYTHONINTMAXSTRDIGITS` unset in the harness | T (4,300 vs 4,301 digits per component) |
| PR-11 | PT-CP | `len`/slicing count code points (a lone surrogate counts 1) | SL :153 (`visible`), :1195-1196 (`trim_to_fit`), :1122, :1133, :1143, :1145 (composition), :1017 `[:40]`, :389 `[:7]`; HK :83 `[:400]`, :89 `[-800:]`, :90 `[-KEV_CHARS:]`, :91 `[:800]`, :180 `len(last) < 200`, :190 `len(msg)`, :215 `[-160:]`, :236 `len(...) > 20`, :266 `tail[-100:]`; PX :123 `req_bytes` (a **ledger field**, BX), :322 `msg[:300]` (ledger), :332/:335 `[:8]` (ledger `account`), :287 `[:600]` (OOS), :295; EX :84-90 `[:8]`, :87 `len > 8`, :382 `s_id[:8]` | production | `internal/pystr.Len`/`Slice` over runes (U+FFFD for a lone surrogate also counts 1) | T (astral, combining, lone surrogate) |
| PR-12 | PT-SPLIT (+ universal newlines) | `str.splitlines` boundary set (`\n \r \r\n \v \f \x1c-\x1e \x85    `); `bytes.splitlines` (`\n \r \r\n`); Python `strip`/`split(None)` whitespace (incl. NBSP, `\x1c-\x1f`); **text-mode `for line in f` translates `\r` and `\r\n` to `\n` (universal newlines)** | `str.splitlines` HK :177; `bytes.splitlines` SL :1059; strip/split: SL :284, :381-386, :444-445, :902, HK :82-83, :89, :100, :170, :215, :230, :236, PX :86, :94, BF :89; `rsplit` SL :1196; `rstrip("*")` SL :487; **universal-newline iteration (new): HK :69, EX :116, EX :216, BF :44** (a bare `\r` splits a record in Python, not in a `\n`-only Go scanner) | production for strip/split; universal-newline edge only (JSON forbids raw CR inside strings; reachable through `str()`-rendered session ids in the hook log, CV-07) | `pystr.Strip`, `SplitNone`, `SplitLines`, `SplitLinesBytes`, and a universal-newline line reader for text-mode files | T |
| PR-13 | PT-RE | Python `\b`, `\s`, IGNORECASE are Unicode; lookbehind unsupported in RE2; `$` also matches before a final `\n` | HK :24-28 (ANNOUNCE `\b`), :177 (lookbehind split: **RE2 compile error**), :179-180 (`\b`), :184 (CJK class, same semantics), :236 (`:\s*$` = `endswith(":")` after strip); SL :137, :1017; PX :413 (bytes); EX :230 | production (hook English/continue logic) | hand-written sentence splitter; Unicode word-boundary helper; RE2 only for the safe patterns | T (`nowé`, `ſ`, NBSP), F |
| PR-14 | PT-TIME | local time with no zone (write and read), DST ambiguity, `fromisoformat` grammar by version, `strptime` leniency | writers PX :60, :72, :632, :709; HK :197; readers EX :125, :145 (**[pinned]** single-digit fields accepted; DST fold 0), SL :983, BF :39 (3.9 vs 3.11), SL :286 (`mktime`) | production (every ledger line) | `internal/pytime`: `Strftime(loc)`, `ParseNaive(loc)` with Python leniency, `FromISOFormat` subset; `*time.Location` injected, never implicit `time.Local`; Windows ignores `TZ` (research P19) | T (UTC + America/Chicago edges), F |
| PR-15 | PT-FMA | Go may fuse `x*y + z` (also across statements, Go spec); Python rounds every operation | SL :146-147 via `colorsys.hsv_to_rgb` (`h*6.0 - i`, `1.0 - s*f`, `1.0 - s*(1.0-f)`); SL :558-559 `(now - win_start)*1000 - dur`; **BF :75-76 sum of five products (new)**: **[pinned]** emulated fused vs unfused gave ulp differences in about 10 % of messages (200,751 of ~2M) and **0 of 20,000** sessions changed after `round(usd, 4)` | colorsys/⌂: 0 byte differences observed (P3r1); backfill: ulp-level only | wrap every product in `float64(…)`; port colorsys with the same operation order | T (pct 0..100 step 0.01; backfill fuzz) on arm64 CI |
| PR-16 | PT-STR | `str()`/`repr()` of non-str values; `repr` quote choice and `isprintable` table | HK :197-199 (`str()` of `session_id`/`stop_hook_active`, `repr(tail)`; H-09); SL :442, :453 (labels); PX `%s` notes (OOS); EX `esc()` needs str (E-20) | production (hook log) | `pyfmt.Str`, `pyfmt.Repr` (Python `str.isprintable`, Unicode-version-sensitive) | T |
| PR-17 | PT-ENC | strict UTF-8 text writes raise on lone surrogates; stdio mode depends on locale | SL :1234 (CP-S17), stdin SL :1201-1204; HK :196-199 (H-09), :206; PX :71-72 (BC-PX-048); EX :399 `.encode()` (E-22); text-mode reads DET-45 | latent (0 lone-surrogate escapes in the production ledger, P3r7) | operate on bytes; explicit "would Python's strict codec fail here" checks at each write site | T |
| PR-18 | PT-PARSE | `int()`/`float()` grammar (whitespace, `_`, Unicode digits, `nan`/`inf`); `urlparse(...).port` raises on bad ports | env: SL :74-75, HK :33-36, EX :24-25 (§A); SL :1188, :853, :866, :878, :178; PX :243 and the other `int(...)` sites; EX :232; PX :82 and PF :20 (`.port`) | production (env, coercions) | `pyfmt.ParseInt`/`ParseFloat`; a `urlparse`-compatible port rule for `DGX_UPSTREAM` | T |
| PR-19 | PT-ORDER | dict insertion order, first-wins, stable sort, dict-order tie-breaks | SL :175-184 (VM first wins), :338-347 (history point key order), :1150-1153 (mix cache key order); PX :60 + call sites (ledger fields), :178 (headers), :514 (`dict.fromkeys`); EX :238, :293-380 (stable sorts); BF :81 (`max(out, key=out.get)` tie → `dgx`), :97 (glob order) | production | ordered pairs, never `range` over a map for output; `slices.SortStableFunc` | G |
| PR-20 | PT-PATH | `posixpath` vs `ntpath`; `normpath`, `basename`, `abspath` (cwd) | SL :373, :383, :390, :460; PX :289, :560-572; HK :100, :195 | per OS | `path/filepath` per OS; per-OS goldens for root and drive cases | G |
| PR-21 | PT-EXC | exception-driven output | CP-S01..S17, CP-T01..T07, CP-N01..N02, CP-C01..C10, CP-X01..X04, CP-A01..A03; P-R1..R5, P-S1..S6; E-01..E-09, E-20..E-22; H-01..H-09; B-01..B-08; plus the new env-value crashes in §A (ENV-03, -19, -22) | mixed | `errDegraded` + per-site predicates (CV-08) | T (D4-EX-2 tables), G |

**Count: 21 register entries, 19 tags + 2 new (PT-FREPR, PT-INTLIM).** New occurrences this round: PR-10 (all pinned sites and the per-component
split), PR-12 (four universal-newline sites), PR-14 (exporter `strptime` leniency and DST behavior), PR-15 (backfill cost formula), PR-18 (`urlparse`
port), PR-11 (ledger-visible `req_bytes`, `error[:300]`, `account[:8]` called out as BX).

---

## E. Owner decisions (new: OD-58..OD-61)

| ID | Decision | Options | Recommendation |
|---|---|---|---|
| **OD-58** | **Harness clock design** (CONV-ABS-47/48). The research doc's `time.time` shim does not freeze `strftime`, and a frozen clock hides the Kev early stop | (a) research shim + mask every `strftime`-derived field; (b) the extended shim of §B.2: mode 1 for P1-P3, mode 2 for the hook early-stop cases | **(b).** It freezes the ledger `t` and hook log prefix, so fewer fields need masking, and it is the only way to test HK :133. Go reads one injected `Clock` and matches read counts only in the hook |
| **OD-59** | **Env-value parse quirks for `DGX_*` aliases** (§A): `https` upstream on port 80, schemeless values silently ignored, `DGX_KEV_CHARS=0` meaning "no cap", negative slices, `DGX_KEV_TIMEOUT=inf` and an empty `DGX_KEV_URL` crashing the hook, `nan`/`inf` TTLs and thresholds | (a) reproduce for `DGX_*` and `HYLO_*`; (b) reproduce for `DGX_*` aliases only, validate `HYLO_*` at config load (typed, range-checked, clear error); (c) validate both | **(b).** Parity cases keep legacy behavior on the alias path; the new names fail fast with a message. A valid production value behaves the same on both paths |
| **OD-60** | **`ARGS` leaking into the `claude` argv** (ENV-43) | (a) reproduce; (b) do not reproduce and record it as an approved deviation | **(b).** It is a zsh accident with no intended behavior; `hylo run` builds argv explicitly |
| **OD-61** | **`~` in env-provided paths** (CV-11): legacy expands only defaults | (a) literal for every source; (b) literal for `DGX_*` aliases during parity, leading `~` expanded for config-file and `HYLO_*` values; (c) expand everywhere | **(b).** Matches legacy where parity is measured and removes a footgun for new users (the committed plist already shows a `~` that launchd does not expand, BC-SV-001) |

---

## Delta Summary

| Target | New | Refined / confirmed |
|---|---|---|
| A env inventory | **ENV-43 `ARGS`** (count 42 → 43); 17 implicit inputs listed with pins, incl. **OS proxy fallback** (ENV-I15), `PYTHONINTMAXSTRDIGITS`, `REQUEST_METHOD`; **value-parse quirks pinned** for `DGX_UPSTREAM` (https → port 80, schemeless ignored, bad port = import crash in proxy, trust CLI and preflight), `DGX_KEV_URL` (empty → hook crash at HK :110, outside the `try`), `DGX_KEV_TIMEOUT` (`inf` → uncaught `OverflowError`; `-1`/`nan` → unreachable), `DGX_KEV_CHARS` (`0` = no cap, negative drops the head), `DGX_SL_TTL` (`nan`/`inf`), `DGX_KEV_THRESHOLD` (`nan`/`inf`), exporter port range | 43 rows with default, consumers, parse, crash, key and `HYLO_*` name; r3 itemisation fixed (16 `DGX_*` in the launcher); env-path literalness (CV-11) |
| B determinism | **C-level clock reads are not frozen by the research shim** (CONV-ABS-47), with a pinned corrected shim; **Kev early stop untestable under a frozen clock** (CONV-ABS-48); **cwd** input (CONV-ABS-49); eager-default double read (DET-09); OS proxy discovery (DET-26); child-process locale (DET-46); exporter `strptime` leniency + DST fold (DET-21); concurrency (DET-52); negatives (monotonic, hashing, terminal size) | 52 rows with Go injection points; per-phase pin sets (§B.3) |
| C conventions | three atomic-write variants; append writers with umask perms and multi-process ledger; four JSON styles; ledger record shape; decision-log `%s` rendering and the 11 templates; the five-level error ladder; env-path literalness | 18 conventions, each tied to BCs/pitfalls and a Go equivalent |
| D pitfalls | 2 new tags (PT-FREPR, PT-INTLIM); new occurrences: backfill FMA (pinned, ulp-level), universal-newline iteration (4 sites), int-digit limit across 8 sites with the 3.9.6 exporter exception, `urlparse` port, ledger-visible code-point slices | 21 entries with remedy and test type |
| Owner items | OD-58..OD-61 | — |
| Retractions | CONV-ABS-47, -48, -49 | — |

Existing items refined: pass-5 broad §2 (40 → 43 with parse/crash columns), §3 (55 rows → 52 consolidated rows with corrected pins), §1 (13 → 18
conventions); pass-2 r3 E-5 itemisation; research Q3a shim (CONV-ABS-47).

## Remaining Gaps (verbatim-carryable)

1. Go-side pins not run this round (no Go probe was executed): `time.Date`/`ParseInLocation` results for the America/Chicago ambiguous 01:30 and the
   spring-gap 02:30 versus Python's fold-0 values (`1793514600.0`, `1772958600.0`, pinned in `p5r1/strp.py`); and whether the Go compiler actually
   fuses the backfill expression `BF :75-76` on arm64 (the register entry is based on emulation).
2. New hook crash rows to add to the hook catalogue (pass-2 r2 §6.3, after H-09): an empty or otherwise `Request()`-invalid `DGX_KEV_URL` raises at
   HK :110 outside the `try`; `DGX_KEV_TIMEOUT=inf` raises `OverflowError` inside `urlopen`, which HK :119 does not catch. Only `Request()` and
   `socket.settimeout` were pinned; the full `urlopen` path was not executed (no network). `DGX_KEV_TIMEOUT=0` (non-blocking connect) is inferred.
3. Exporter `DGX_LEDGER_EXPORTER_PORT=0` (ephemeral bind) is inferred from socket semantics; not executed.
4. mitmproxy 12.3.1 environment reads other than `SSLKEYLOGFILE`/`MITMPROXY_SSLKEYLOGFILE` (any `MITMPROXY_*` option overrides) were not enumerated:
   the venv is not in the tree (OD-47).
5. Windows harness time-zone pinning: Python and Go both depend on the system zone there (`TZ` is ignored by Go on Windows, research P19); the
   naive-time cases (DET-19..23) need a Windows-specific rule (UTC system zone on CI, or skip with a reason).
6. Owner decisions OD-58..OD-61 (§E), plus the carried OD-01 (`HYLO_*` derivation rule, assumed in §A) and OD-05 (boolean grammar).

## Novelty Assessment

Novelty: SUBSTANTIVE

Removing this round would change how the harness and the config layer are specified:
- A missing env input (`ARGS`) and a missing implicit input class (OS proxy discovery for the Kev call when no proxy variable is set).
- Three retractions of recorded harness pins: the research shim does not freeze `strftime` (ledger `t`, hook log), a frozen clock cannot exercise
  the Kev early stop, and cwd is an input.
- New determinism sources (eager double clock reads, child-process locale, exporter `strptime` leniency and DST fold, concurrency).
- New pitfall occurrences (backfill FMA, universal-newline iteration, int-digit limit with a per-component split) and new env-value crash and quirk
  rows that the alias parser has to reproduce or deliberately reject (OD-59).

## Convergence Declaration

Another round needed: this round retracted three recorded pins and added an env input, an implicit-input class and new crash rows. Round 2 should
re-verify CONV-ABS-47..49 and the new env-value rows from scratch, run the Go-side pins of Remaining Gap 1 if a Go probe is authorized, and audit
this round against the five hallucination classes.

## State Checkpoint

```yaml
pass: 5
round: 1
status: complete
files_scanned: 11   # all legacy files; Python files re-read in the ranges listed in the header
timestamp: 2026-11-14T08:40:00Z
novelty: SUBSTANTIVE
counts: {env_explicit: 43, env_implicit: 17, determinism_rows: 52, conventions: 18, pitfall_entries: 21, new_tags: 2}
retractions: [CONV-ABS-47, CONV-ABS-48, CONV-ABS-49]
owner_items: [OD-58, OD-59, OD-60, OD-61]
next: pass 5 round 2 (targets = Remaining Gaps 1-6 verbatim)
```
