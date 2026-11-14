# Pass 0 Deepening, Round 3: Verification of round 2 and the consolidated inventory for Phase 1 (hylo-legacy)

- **Source:** `$HOME/Dev/hylo/legacy/`, read-only and static. Re-read this round: `dgx-proxy-coordinator.sh` (all), `claude-dgx:1-30,
  55-100,129-185` plus `grep` for `trap`, `ARGS`, `mitmenv`, `whoami` and every variable assignment; `ROLLBACK.md` (`grep` for `checkpoint`,
  `opus_router`, `warlock`, `mitmenv`; l.15-26 in full); `dgx_proxy.py:40-51` plus a `grep -w log` and a `\bctx\b` search; `dgx_ledger_exporter.py:15-27`
  plus `grep threading|state_lock|urlparse|parse_qs`; `dgx_statusline.py:195-206,1012-1020,1208-1220`; `tools/backfill_cost_history.py:108-117`.
  Mechanical re-census of every `os.environ.get`/`os.getenv` name across the 6 `.py` files.
- **Inputs read:** broad pass 0 (all), pass-0 deep r1 (all), r2 (all); pass-2 r7 l.1-20, r6 l.30-45, r5 l.25-35; sibling deep files **pass-1 r1**
  (header, l.71, 94, 113, 216, 324, 327, 348, 472), **pass-4 r1** (header, l.114-115, 124, 188, 201-203, 392, 418), **pass-5 r1** (header,
  §A.1 l.40-50, ENV-40..43 l.95-98, ENV-I1..I17 l.111-121, DET-30/45/50, l.235-236, §E l.306-325). Sibling files were not edited.
- **Method and host evidence:** nothing in legacy ran; no proxy; nothing networked; `CLAUDE.local.md` not read; no git commit. Host facts only from
  `which -a`, `--version`, `ls`, `man lsof`, `git -C … rev-list/ls-files`, a read of the host CPython's `tempfile.py`, and one shell-semantics probe
  that runs no legacy code: `/bin/zsh -f -c '/usr/bin/python3 -I -c "<print SIGINT disposition>" & wait; <same in foreground>'`. Scratch:
  `…/scratchpad/p0r3/host-checks.txt`.
- **Masking:** backend host `<backend>` (the source carries the RFC 5737 default); home paths `~`.
- **Numbering:** **no retraction** this round (CONV-ABS-54..56 unused). **No new owner item** (OD-62..OD-65 unused).

---

## 1. Target A: round 2's own statements, re-verified with fresh evidence

| # | Round-2 statement | Fresh evidence (this round) | Verdict |
|---|---|---|---|
| A1 | **CONV-ABS-53**: the production venv's package versions are recorded in pass-2 r7 (certifi 2026.10.23, pyOpenSSL 26.4.0, cryptography 50.0.2, h11 0.16.0, h2 4.4.1, wsproto 1.3.2; base CPython 3.12.10 via a uv-managed `cpython-3.12`) | pass-2 r7 l.9-11, read verbatim: "Bundled dependency versions from their `dist-info` directories: certifi 2026.10.23, pyOpenSSL 26.4.0, cryptography 50.0.2, h11 0.16.0, h2 4.4.1, wsproto 1.3.2" and "CPython 3.12.10, the venv's base interpreter (`.mitmenv/pyvenv.cfg` `home` → the uv `cpython-3.12` symlink → `cpython-3.12.10`; `include/python3.12/patchlevel.h:26`)". mitmproxy 12.3.1 from `version:5` (r7 l.6). Host: `uv 0.12.23` at `/opt/homebrew/anaconda3/bin/uv` (re-run) | **Confirmed.** Wording fix: round 2 said "the venv was **built with uv**". P2r7 records only that the **base interpreter** is uv-managed; the venv's creator (a `uv =` key in `pyvenv.cfg`) was not recorded. Correct phrasing: "base interpreter uv-managed; venv creator not recorded". OD-47 option (a) is unaffected |
| A2 | Dynamic stdlib import `state_lock = __import__("threading").Lock()` omitted by round 1 | `dgx_ledger_exporter.py:27`; used at `:239` and `:288` (`with state_lock:`) | **Confirmed** |
| A3 | Dead imports `from mitmproxy import ctx` and `logging` (plus round 1's `urlparse`) | `\bctx\b` matches only `dgx_proxy.py:44`. `logging` appears only at `:31` (import) and `:51` (`log = logging.getLogger("dgx_proxy")`); `grep -w log` finds `:51` and three comments (`:14`, `:308`, `:431`), no code use. Exporter `:20` imports `urlparse`; only `parse_qs` is used (`:274`) | **Confirmed** (3 dead imports) |
| A4 | `~/.cache/dgx-llm/statusline-nosession.json` when stdin lacks `session_id`; session-cache `sid` unsanitized, mix-cache `sid` sanitized; mkstemp temporaries left behind on a dump error | `dgx_statusline.py:1214-1215` (`sid = d.get("session_id") or "nosession"`, `f"statusline-{sid}.json"`); mix cache `:1016-1017` (`re.sub(r"[^A-Za-z0-9_-]", "_", sid)[:40]`); `save_cache` `:198-206` swallows every exception without unlinking | **Confirmed, refined.** Temp names are `statusline-<sid>.json.<8 random chars>` (prefix = basename + `"."`, `:201`; CPython `_RandomNameSequence` uses `k=8`, host `tempfile.py:154`), not `<name>.XXXXXX`. Backfill: `cost-history.<8 chars>` (`:113`); it has **no** `try`, so a dump error raises a traceback **and** leaves the temp file |
| A5 | `ROLLBACK.md` states two venv locations; dangling references | `ROLLBACK.md:19` "`dgx-llm/.mitmenv`" vs `:23` `rm -rf ~/hylo/legacy/.mitmenv`; `claude-dgx:36` "Requires dgx-llm/.mitmenv" vs the code's `$HERE/.mitmenv` (`:61`, `:75`). Dangling: `checkpoint-20261109-*` (`:3-4,12-14,41,44-46`), `opus_router.py` (`:11,13,46`), memory file `dgx-warlock-opus-serving.md` (`:30`) | **Confirmed.** Line refinement: `checkpoint` also at `:12` and `:41` |
| A6 | PATH order: Anaconda `python3` 3.11.7 shadows Homebrew 3.15.0 and `/usr/bin` 3.9.6 | `which -a python3` → `/opt/homebrew/anaconda3/bin/python3` (3.11.7), `/opt/homebrew/bin/python3` (3.15.0), `/usr/bin/python3` (3.9.6); PATH has `/opt/homebrew/anaconda3/bin` before `/opt/homebrew/bin` | **Confirmed for the analysis shell's PATH.** Caveat: Claude Code's PATH at hook and status-line run time was not observed (it inherits the launching shell's PATH, so the same order is expected, MEDIUM). The parity harness pins the interpreter by absolute path, so parity is unaffected |
| A7 | Coordinator `lsof` shows `python3.12`, never `mitmdump`, so `state_valid`/`start_new` can never succeed on this host | Coordinator `:15` `lsof -nP -iTCP:"$1" -sTCP:LISTEN 2>/dev/null \| grep -q mitmdump`; `:22`, `:35-36` as stated. Production evidence P2r5 l.30: "9 legacy proxies (`python3.12` mitmdump)". `man lsof` (host): "`+c w` … The lsof default is nine." characters for COMMAND | **Conclusion confirmed; literal refined.** With the default width, the coordinator's `lsof` prints COMMAND `python3.1` (9 chars), not `python3.12`; `python3.12` is the full process name recorded in P2r5. NAME is `*:<port> (LISTEN)`. Neither form contains `mitmdump`, so the grep never matches |
| A8 | Orphan window: mitmdump starts at `claude-dgx:75`, the trap is armed at `:97`; `exit 1` at `:78` leaves it running; Ctrl-C during the 10 s wait also leaves it running (MEDIUM-LOW) | `grep -n trap claude-dgx` → one hit, `:97`. `MITM_PID=$!` `:76`; `exit 1` at `:78` inside the invisible block. **Host probe:** in `zsh -f -c`, a `&` job sees SIGINT = `SIG_IGN`, the foreground child sees `default_int_handler`; the job shares the shell's process group (pgid equal), so a terminal Ctrl-C reaches it. **But** mitmdump replaces the disposition with `loop.add_signal_handler(SIGINT)` and treats SIGINT as `shutdown` (P2r6 l.38, mitmproxy 12.3.1 `tools/main:117-133`) | **`:78` half confirmed (HIGH, source order).** **Ctrl-C half narrowed (MEDIUM):** the premise (inherited `SIG_IGN`, kept by CPython) is now host-verified, but it only protects mitmdump until mitmproxy installs its own handler. A Ctrl-C after that shuts mitmdump down. Whether the handler is installed before or after the listener binds (i.e. how much of the 10 s wait is exposed) is not recorded in any pass file, and mitmproxy source is not on this host. Not a retraction: round 2's claim holds for the pre-handler part of the window |
| A9 | Env-input recount "Python 27, launcher 21, overlap 6 → **42**" (r2 §2.5) | Python re-census: **27** names (same list). Launcher: 21 explicit reads, **plus `ARGS`**, which is never initialized (`grep ARGS` → first occurrence `ARGS+=` at `:129`; also `:133,137,139,180,183,185`), so an exported `ARGS` is imported and prepended to `claude`'s argv | **Superseded by pass-5 ENV-43 (count 43).** Round 2 counted explicit reads correctly but missed the implicit import that pass-5 found and pinned. Adopted below (§2.8); no CONV-ABS, because the correction was already made in pass 5 (its l.321 "count 42 → 43") |

Metrics re-derived this round (unchanged): 11 files, 3,181 lines (per-file 1245/764/414/275/185/121/55/50/41/18/13), 164,151 bytes, 19 commits
touching `legacy/`, 26 on `main`, 11 tracked files.

---

## 2. Target B: consolidated final inventory for Phase 1

**Source tags:** `B` broad pass 0 · `R1`/`R2`/`R3` pass-0 deep rounds · `P5` adopted from pass-5 deep r1 · `P2rN`/`P3rN` cited pass files.
Where a later round corrected an earlier one, the row shows the corrected value and both tags. This section supersedes the inventory tables of
the broad pass 0, r1 and r2 for downstream use.

### 2.1 Codebase metrics

| Metric | Value | Source |
|---|---|---|
| Files / lines / bytes | 11 / 3,181 / 164,151 (Python 2,860 in 6 files, zsh 235 in 2, plist 31 in 2, Markdown 55) | B, R1, R2, R3 |
| Python statements (AST) | 1,809 (status line 742, proxy 500, exporter 316, hook 146, backfill 86, preflight 19) | R1 (P3r8 §1) |
| Commits | 19 touching `legacy/` (18 imported + `220e96c` made in hylo); 26 on `main` | B (validated), R1, R3 |
| Executable bits | `auto_continue.py`, `claude-dgx`, `dgx_ledger_exporter.py`, `dgx-proxy-coordinator.sh` only; every launch names an interpreter | R1, R2 |
| Tests in tree | 0 | B |

### 2.2 Components, entry points and invocation paths → hylo

| # | Component / path | Entry (file:line) | Invoked by | Interpreter | hylo target | Phase / status | Source |
|---|---|---|---|---|---|---|---|
| 1 | Launcher, session mode | `claude-dgx:1-185` | user alias | zsh 5.9 | `hylo run` (+ config profiles) | P4 | B |
| 2 | Launcher `trust` delegation | `claude-dgx:11-14` (`exec python3 … trust`) | user | PATH `python3` | `hylo ca` | OOS (D13) | B, R1 |
| 3 | Launcher dry run | `claude-dgx:182-184` (`DGX_PRINT_ARGS=1`) | user | zsh | `hylo run` dry run / `hylo config` show | P4 (BC-LN-010) | R1 |
| 4 | Launcher visible mode | `claude-dgx:15-22,85-96` | env `DGX_INVISIBLE=0` | zsh + `python3` | none | OOS (D6); broken (`opus_router.py` absent). The 4141-4199 probe at `:17-22` runs in **every** mode unless `ROUTER_PORT` is set | B, R1, R2 |
| 5 | Preflight | `dgx_preflight.py:18-41`, called `claude-dgx:60-68` | launcher unless `DGX_SKIP_PREFLIGHT=1` | **venv** `$HERE/.mitmenv/bin/python` (3.12.10) in invisible mode; `python3` only in visible mode (`:61-62`) | `hylo doctor` | P4 (BC-PF-001/002) | B, R1 (interpreter corrected) |
| 6 | mitmdump host process | `claude-dgx:75` | launcher, one per window | venv 3.12.10, mitmproxy 12.3.1 | `hylo proxy`, one per user | P3. Defaults in effect: R1 §A.2 (10 rows, re-audited R2) | R1 |
| 7 | Proxy addon load | `dgx_proxy.py:518-548` | mitmdump `-s` | venv | `internal/proxy`, `internal/ledger`, `internal/events` | P3 | B |
| 8 | Proxy live reload | mitmproxy script watcher (1 s mtime) | editing `dgx_proxy.py` | venv | none (config reload instead, OD-26) | OOS as a mechanism | R1 (P2r4 §2.1) |
| 9 | Trust CLI | `dgx_proxy.py:759-764` → `_build_parser` `:737`; `install` `:625`, `status` `:648`, `remove` `:676`, `rotate` `:702` | row 2 | PATH `python3`; mitmproxy import optional (`:42-46`) | `hylo ca` | OOS (D13). Side effects: decision-log line `:518`, `DGX_UPSTREAM` parse at import `:521` | B, R1 |
| 10 | Trust `rotate` restart hook | `dgx_proxy.py:719-725` (`shell=True`, 30 s CA poll) | env `DGX_PROXY_RESTART_CMD` | `/bin/sh` | none | OOS (D13) | R1 |
| 11 | Status line | `dgx_statusline.py:1238-1245` → `main()` `:1200` | Claude Code `statusLine`, `refreshInterval` 4 (`claude-dgx:176`) | PATH `python3` (3.11.7 oracle) | `hylo statusline` | P1 | B |
| 12 | Status line `--subagent` | `:1240-1241` → `main_subagent` `:928` → `render_subagent_rows` `:888` | `subagentStatusLine` (`claude-dgx:177`) | same | none | OOS (PLAN §3); parity treatment pending OD-14 | B, R1 |
| 13 | Stop hook | `auto_continue.py:274-275` → `main()` `:209` | Claude Code `Stop`, timeout 30 (`claude-dgx:161`) | PATH `python3`, ≥ 3.10 required (`:94`) | `hylo hook stop` | P4 | B, R1 |
| 14 | UserPromptSubmit hook | `claude-dgx:157-159` (inline `echo`, timeout 5) | Claude Code, every prompt, if `DGX_ENGLISH != 0` | hook shell | `hylo hook prompt` recommended | **OD-46** | R1, R2 |
| 15 | Ledger exporter | `dgx_ledger_exporter.py:410-414` | LaunchAgent (`deploy/io.hylo.ledger-exporter.plist:5-10`) | `/usr/bin/python3` 3.9.6 | `hylo exporter` + per-OS service unit | P2 | B |
| 16 | Exporter forced rebuild | `dgx_ledger_exporter.py:273,285` (`?rebuild=`) | any HTTP client | same | `hylo exporter` (OD-39) | P2 | R1, R2 |
| 17 | Ledger tunnel | `deploy/io.hylo.ledger-tunnel.plist:5-13` | launchd | OpenSSH | docs only | OOS (BC-SV-002) | B |
| 18 | LaunchAgent installation | none (`launchctl` never invoked; 0 hits) | owner by hand | — | per-OS service installer (new, no oracle) | P2/P4 design | R1, R2 |
| 19 | Coordinator | `dgx-proxy-coordinator.sh:40-50` | nobody | zsh + venv mitmdump (`:31`) | built into `hylo proxy`/`hylo run` | OOS (OD-19). **Cannot succeed on this host** (lsof name, §1 A7) | B, R2, R3 |
| 20 | Backfill | `tools/backfill_cost_history.py:120-121` → `main()` `:84` | manual `python3 tools/…` (mode 0644) | PATH `python3` | `hylo cost backfill` | no phase (OD-36) | B, R1 |
| 21 | Dead: Opus arbitration | `auto_continue.py:141-166` | — | — | none | dead | B |
| 22 | Dead: `websocket_start`/`_end` | `dgx_proxy.py:528-536` | — | — | none | dead | B |

hylo surfaces with **no legacy component** (R1): `hylo ui`, `hylo top`, `internal/events`, `web/` (D16; nearest legacy evidence is mitmdump's flow
log, the ledger and the decision log); `hylo config` validation (D15; nearest is `DGX_PRINT_ARGS` and `profile.env`); `hylo ca create` (today
mitmproxy mints the CA in `~/.mitmproxy`).

### 2.3 Interpreters and runtimes

| Component | Launched as (file:line) | Version | Constraint | Source |
|---|---|---|---|---|
| Launcher, coordinator | `#!/bin/zsh` (`claude-dgx:1`, coordinator `:1`) | zsh 5.9 | zsh-only syntax (`${0:A:h}`, `${(j:,:)…}`, `{1..40}`); `&` jobs get SIGINT ignored (host probe, §1 A8) | R1, R3 |
| Proxy addon, mitmdump | `$HERE/.mitmenv/bin/mitmdump` (`claude-dgx:75`; coordinator `:31`) | CPython 3.12.10 (base uv-managed), mitmproxy 12.3.1 | venv **absent from the tree**, no lock file, not gitignored (OD-47) | R1, R2, R3 (P2r7) |
| Preflight | `$HERE/.mitmenv/bin/python` (`claude-dgx:61`) | 3.12.10 | inherits the venv app's macOS Local Network permission (`claude-dgx:56-59`) | R1 |
| Trust CLI | `python3` (`claude-dgx:13`) | 3.11.7 on this host | stdlib + optional mitmproxy | R1 |
| Status line | `python3` (`claude-dgx:176`) | 3.11.7 (owner-ruled oracle) | ≥ 3.11 semantics (`fromisoformat`, 4,300-digit limit) | B, R1 |
| Stop hook | `python3` (`claude-dgx:161`) | 3.11.7 | ≥ 3.10 (PEP 604 at `auto_continue.py:94`) | R1 |
| Exporter | `/usr/bin/python3` (`deploy/io.hylo.ledger-exporter.plist:6`) | 3.9.6 (Command Line Tools) | UTF-8 mode under launchd; argv `~/hylo/legacy/…` not expanded by launchd (`:7`) | B, R1, R2 |
| Backfill | `python3` (docstring `:18`) | 3.11.7 | — | R1 |
| PATH resolution on this host | `which -a python3` | Anaconda 3.11.7 > Homebrew **3.15.0** > `/usr/bin` 3.9.6 | the 3.11.7 oracle depends on PATH order; harness pins `/opt/homebrew/anaconda3/bin/python3 -I` | R2, R3 |

### 2.4 Third-party packages (production venv; none elsewhere)

| Package | Version | Role | Evidence | hylo replacement | Source |
|---|---|---|---|---|---|
| mitmproxy | 12.3.1 | proxy host + addon API (`dgx_proxy.py:43-44`) | P2r7 l.6 (`version:5`) | `crypto/tls`, `net/http`, `httputil` | B, R1 |
| certifi | 2026.10.23 | sole upstream trust anchor | P2r7 l.9 | system roots + per-backend CA (OD-41) | R1 |
| pyOpenSSL | 26.4.0 | mitmproxy TLS | P2r7 l.9 | `crypto/tls` | R2 |
| cryptography | 50.0.2 | CA/leaf minting | P2r7 l.10 | `crypto/x509` (`internal/ca`) | R2 |
| h11 | 0.16.0 | HTTP/1 framing; one error-text source | P2r7 l.10 | `net/http` | R1 (version R2) |
| h2 | 4.4.1 | HTTP/2 upstream leg | P2r7 l.10 | `net/http` (h2) | R2 |
| wsproto | 1.3.2 | WebSocket pass-through | P2r7 l.10 | `net/http` hijack / WS library decision in P3 | R2 |
| (transitive rest) | not recorded | — | — | — | open (OD-47 `pip freeze`) |

Every other legacy program is stdlib-only, including the dynamic `__import__("threading")` (`dgx_ledger_exporter.py:27`). Dead imports: `ctx`
(`dgx_proxy.py:44`), `logging` (`:31`, only feeds the unused `log` `:51`), `urlparse` (`dgx_ledger_exporter.py:20`). Sources: B, R1, R2, R3.

Server-side, outside the tree (PLAN §3 non-goal): VictoriaMetrics recording rules `dgx_kv:*`, `dgx_tokens:*`, `dgx_ttft:*`, `dgx_preempt:*`,
`dgx_power:*`, `dgx_cost:*`; DCGM exporter; vLLM/LMCache scrape jobs; Kev; VM scraping the tunnelled exporter. Source: R1.

### 2.5 OS tools and per-OS replacement (D5)

"Live" = reachable on the invisible-mode production path.

| Tool | Call sites | Live? | Linux | Windows | hylo replacement | Source |
|---|---|---|---|---|---|---|
| `zsh` | `claude-dgx:1`, coordinator `:1` | yes | often absent | absent | Go `hylo run` | B, R1 |
| `nc -z` | `claude-dgx:21,73,77,78,89` | yes (`:21` in every mode) | flavor varies | absent | `net.DialTimeout` / `net.Listen` | B, R1 |
| `sleep` | `claude-dgx:77,94`; coordinator `:35` | yes | yes | absent | `time.Sleep` | R1 |
| `kill`, `trap … EXIT INT TERM` | `claude-dgx:97`; coordinator `:23,36` | yes | builtin | no signals | `os/signal`, `os.Process`; Windows console events / job objects | R1 |
| `whoami` | `claude-dgx:43` (only if `DGX_USER` unset) | yes | yes | `DOMAIN\user` (case may differ from Go) | `os/user.Current()` (OD-48) | B, R1, R2 |
| `basename` | `claude-dgx:44` | yes | yes | absent | `filepath.Base` | B |
| `ps -o ppid=,comm=,lstart=` | `dgx_statusline.py:280` (timeout 1, ≤ 6 ancestors) | yes | procps | absent | `internal/platform` (sysctl / `/proc` / Toolhelp32) | B, R1, R2 |
| `claude` | `claude-dgx:185`; `auto_continue.py:155` (dead) | yes | PATH | `claude.exe` / `.cmd` shim | `exec.LookPath` | B, R1 |
| `python3` (settings commands) | `claude-dgx:161,176,177` | yes | PATH | `py`/`python` | `hylo statusline`, `hylo hook stop` | R1 |
| `echo` (hook command) | `claude-dgx:158` | yes if `DGX_ENGLISH != 0` | builtin | hook-shell dependent | OD-46 | R1 |
| `ssh` | tunnel plist `:6` | home lab | yes | optional feature | docs only | B |
| launchd (no `launchctl` call) | `deploy/*.plist` | yes | systemd `--user` | Task Scheduler | per-OS units | B, R1 |
| `curl`, `grep` | `claude-dgx:85`; coordinator `:15,28` | no | — | — | none (D6) | B, R1 |
| `lsof`, `flock`, `mkdir -p` | coordinator `:12,15,28,43` | no (unwired) | `ss`; util-linux | absent | state file + Go file lock | B, R1 (CONV-ABS-29: Homebrew `flock` 0.4.0 present) |
| `security`, `openssl x509`, `pgrep -f` | `dgx_proxy.py:568,578,590,606,638,693` | trust CLI only | `security` absent | absent | none (D13), `crypto/x509` | B, R1 |
| `/bin/sh -c` | `dgx_proxy.py:722` | trust rotate + env only | `/bin/sh` | `cmd.exe` | none | R1 |
| `git` | **none** (direct `.git` reads, `dgx_statusline.py:364-396`) | — | — | — | Go file reads | R1 |

Spawn census: 10 Python sites, all above; no `os.system`/`Popen`/`exec*`/`spawn*` (R2, unchanged).

### 2.6 Implicit host dependencies (not tools, not packages)

| Dependency | Where | Note | Source |
|---|---|---|---|
| macOS Local Network permission | preflight and proxy (venv app) | reason preflight runs on the venv (`claude-dgx:56-59`, `dgx_preflight.py:5-9`) | R1 |
| **OS proxy settings** (no env proxy set) | hook's Kev `urlopen` (`auto_continue.py:113`): urllib `getproxies()` falls back to macOS SystemConfiguration | Go's `http.ProxyFromEnvironment` does not read OS settings; parity row in P5 ENV-I15. The status line bypasses all proxies (`ProxyHandler({})`) | **P5** (adopted R3) |
| `~/.ssh/config` `dgx` alias and keys | tunnel plist `:12` | outside the tree | R1 |
| Environment inputs | 27 Python + 22 launcher (21 explicit + implicit `ARGS`) − 6 overlap = **43**; plus mitmproxy's `SSLKEYLOGFILE`/`MITMPROXY_SSLKEYLOGFILE` and 17 implicit inputs (P5 ENV-I1..I17) | full table lives in pass-5 §A; `ARGS` → OD-60 | R2 (42), **P5 (43)**, R3 |

### 2.7 Files and directories

| Path (default) | Override | Access | Component (file:line) | Source |
|---|---|---|---|---|
| `~/dgx-llm-obs.jsonl` (ledger) | `DGX_OBS_LEDGER` | append; full read | proxy `:52,56-62`; exporter `:22,115` | B |
| `~/dgx-llm-routing-decisions.log` | `DGX_PROXY_DECISIONS` | append (also every trust-CLI run) | proxy `:53,65-74,518` | B, R1 |
| `~/dgx-llm-obs/failed-req-<ms>.json` | — | write, keep 20 newest | proxy `:288-297` | B |
| `~/.config/dgx-llm/api-key` | `DGX_KEY_FILE` | read, cached | proxy `:88,91-95` | B |
| `~/.config/dgx-llm/kev-api-key` | `DGX_KEV_API_KEY` (value) | read | hook `:97-102` | R1 |
| `~/.config/dgx-llm/profile.env` | `DGX_PROFILE` | `source` (after proxy start) | launcher `:114-115` | B |
| `~/.mitmproxy/` (CA set) | — | mitmproxy creates/reads; Node reads `-ca-cert.pem` (`claude-dgx:80`); trust CLI `:560-561` | mitmproxy, launcher, trust | B, R1 |
| `~/.mitmproxy.bak-<stamp>/` | — | move; keep 3 | trust rotate `:709-717` | R1 |
| `~/.dgx/trust-state.json` (+ `.trust-state.*`) | `DGX_TRUST_STATE` | atomic write, read, unlink | trust `:563,609-622,681,696` | B |
| login keychain | — | add/find/delete cert | trust `:567-572` | R1 |
| `~/.cache/dgx-llm/statusline-<session_id>.json`, `…-nosession.json` | — | read, atomic write; temp `statusline-<sid>.json.<8>`; `sid` unsanitized | status line `:198-206,1214-1215` | B, R2, R3 |
| `~/.cache/dgx-llm/statusline-mix-<sanitized sid[:40]>.json` | — | same | status line `:951,1017` | B |
| `~/.cache/dgx-llm/statusline-git-<sha1[:16]>.json` | — | same | status line `:405-411` | B |
| `~/.cache/dgx-llm/cost-history.json` (temp `cost-history.<8>`) | — | read, atomic write | status line `:217,224-237`; backfill `:33,91,113-116` | B, R3 |
| `~/.cache/dgx-llm/auto-continue.log` | `DGX_FAKESTOP_LOG` (reader only) | append; read | hook `:195-196`; exporter `:23,215` | B, R1 |
| `<project or cwd>/…/.git`, `<gitdir>/HEAD` (walk to `/`) | — | read | status line `:364-396` | R1 |
| `transcript_path`, stdin JSON | — | read | status line, hook | B |
| `~/.claude/projects/*/*.jsonl` | — | glob, read | backfill `:97` | B |
| `$TMPDIR/dgx-mitm.<pid>.<port>.log` | `TMPDIR` | mitmdump stdout+stderr | launcher `:74-75` | B |
| `$TMPDIR/opus-router.<pid>.log` | `TMPDIR` | path set always, written visible-only | launcher `:23,92` | R1 |
| `$TMPDIR/dgx-shared-mitm.<port>.log`; `<legacy>/.proxy-state/{port,pid,lock}` | — | write; mkdir/flock | coordinator `:5,8-9,12,32,37,42` (unwired) | R1 |
| `<legacy>/.mitmenv/` (venv incl. certifi `cacert.pem`) | — | execute, read | launcher `:61,75`; coordinator `:31`. Absent; docs disagree on location (`ROLLBACK.md:19` vs `:23`; `claude-dgx:36` vs `:61`) | R1, R2, R3 |
| `/tmp/dgx-ledger-exporter.log`, `/tmp/dgx-ledger-tunnel.log` | — | launchd stdout/stderr | plists `:11-12`, `:16-17` | B |
| plist argv `~/hylo/legacy/dgx_ledger_exporter.py` | — | literal `~` (not expanded) | exporter plist `:7` | R1, R2 |
| `~/.ssh/config` | — | read by ssh | tunnel plist | R1 |

### 2.8 Network endpoints

| Endpoint | Direction | Protocol | Component (file:line) | Source |
|---|---|---|---|---|
| `*:8090-8143` (first free) | listen | HTTP CONNECT, TLS-intercepting; **all interfaces** (`listen_host ""`) | mitmdump (`claude-dgx:72-75`) | B, R1 |
| `127.0.0.1:8090-8143` | connect (probe) | `nc -z`; readiness 40 × 0.25 s | launcher `:73,77-78` | R1 |
| `127.0.0.1:4141-4199` | connect (probe) | `nc -z`, ≤ 59 probes, exit 1 if all busy; skipped if `ROUTER_PORT` set | launcher `:17-22` | R1, R2 |
| `127.0.0.1:<PORT>/_opus_router/health` | connect | HTTP (visible only) | launcher `:85` | B |
| `${DGX_UPSTREAM:-http://<backend>:8080}` | connect | HTTP by default (`u.scheme or "http"`), `Authorization: Bearer`; port defaults to 80 when absent | proxy `:79-83,161-163` | B, R1, R2 |
| `<backend>:8080` | connect | raw TCP, 4 s | preflight `:23` | B |
| `api.anthropic.com:443` (+ Remote Control `/api/frame/sync` WS, `/v1/code/sessions/…` SSE) | connect | TLS, certifi-verified | proxy pass-through | B, R1 |
| every other host Claude Code or its children contact (85 distinct incl. `api.anthropic.com`) | connect | TLS-intercepted pass-through | proxy | R1 |
| `bridge.claudeusercontent.com` | keyed in code only | — | proxy `:17-19,100-102,211-214`; never contacted (CONV-ABS-26) | R1 |
| `${DGX_SL_VM_URL:-http://<backend>:8428}/api/v1/query` | connect | HTTP GET, 1.5 s, proxies bypassed | status line `:73,165-170` | B |
| `${DGX_KEV_URL:-http://<backend>:8008/v1/systemone}` | connect | HTTP POST, 2.5 s; env **and macOS system** proxies honored | hook `:31,113`; launcher `:154` | B, R1, P5 |
| `0.0.0.0:9210` (`DGX_LEDGER_EXPORTER_PORT`) | listen | HTTP `/metrics` (+ `?rebuild=`), else 404 | exporter `:25,270-273,414` | B, R1 |
| `dgx:22`, remote `127.0.0.1:9210` → local `127.0.0.1:9210` | connect + reverse forward | SSH | tunnel plist `:8,12` | B, R1 |

### 2.9 Runtime dependency edges added since the broad sweep

| Edge | Evidence | Source |
|---|---|---|
| proxy → ledger → exporter → `ssh -R` tunnel → VM → status line, feeding **two** P1 widgets: `☾` (`dgx_llm_last_dgx_request_timestamp_seconds`, `dgx_statusline.py:106,824-825`) and `⛏` (recording rules over exporter token counters, `:107-108,1218-1222`) | P2r3 l.168-169, l.184 | R1 (☾), R2 (⛏) |
| launcher → preflight runs on the venv, not `python3` | `claude-dgx:61-62` | R1 |
| editing `dgx_proxy.py` → every running proxy reloads | P2r4 §2.1 | R1 |
| trust CLI → decision log (false "addon module loaded" marker) | `dgx_proxy.py:518` | R1 |
| launcher → orphaned mitmdump if readiness fails (`:78` before the `:97` trap); Ctrl-C exposure only before mitmdump installs its SIGINT handler | §1 A8 | R2, R3 |

---

## 3. Target C: reconciliation with the sibling deep files

All three sibling deep files exist (pass-1 r1, pass-4 r1, pass-5 r1). None was edited.

| # | Sibling statement | Inventory fact | Status / action for that pass |
|---|---|---|---|
| C1 | Pass-1 l.71 (C8): "`flock` absent on macOS, so it would run unlocked"; l.324: "D5 (no `flock` on macOS …)" | CONV-ABS-29 (Homebrew `flock` 0.4.0 present, supports `flock 9`); the coordinator fails regardless (§1 A7) | **Open** (carried from r2 R1): reword to "not part of base macOS" |
| C2 | Pass-1 l.327: "Configuration (**40** env inputs …)" | **43** (§2.6; pass-5 ENV-43) | **Open**, now 40 → 43 (r2 said 42) |
| C3 | Pass-1 l.472: "OD-44 and OD-46..OD-49 unused" | OD-46, OD-47, OD-48 issued by pass-0 r1; OD-49 unused | **Open** (carried r2 R3) |
| C4 | Pass-1 l.216: "84 further hosts" | 85 distinct incl. `api.anthropic.com` | consistent |
| C5 | Pass-1 l.94: `listen_host ""` all interfaces; l.348 diagram | §2.8 row 1 | consistent |
| C6 | Pass-1 does not draw exporter → tunnel → VM → status line | §2.9 row 1 (two widgets) | **Open** (carried r2 Gap 4) |
| C7 | Pass-4 l.115 **T-121**: "4141-4199; `curl -m 2`; 40 × 0.25 s … **N/A: dead under D6 (invisible mode only)**" | The `curl` probe and the 40 × 0.25 s wait (`:85,94`) are visible-only, but the **4141-4199 `nc` probe loop (`:17-22`) runs in invisible mode too**: up to 59 probes, exit 1 if all busy (R1 C.2, R2 V4) | **Disagreement.** "N/A" is right for hylo rationale (no successor), but "dead" is wrong for legacy behavior. Pass 4 should split T-121: the probe range is live (startup cost and a failure exit), the rest is dead |
| C8 | Pass-4 l.418: "`flock` (absent on stock macOS)" | matches the surviving form of CONV-ABS-29 | consistent; could add the lsof-name failure (§1 A7) |
| C9 | Pass-4 l.114, 188, 201-202, 392 (9210, tunnel, 8090-8143, 40 × 0.25 s, all-interface listen and `0.0.0.0:9210`) | §2.8 | consistent |
| C10 | Pass-4 records no pre-trap orphan window | §2.9 last row | **Gap in pass 4** (carried r2 Gap 3): reliability item, now narrowed per A8 |
| C11 | Pass-5 ENV-43 `ARGS`, count 42 → 43 | verified this round (A9) | **Adopted by pass 0**; supersedes r2 §2.5's 42 |
| C12 | Pass-5 ENV-I15 OS proxy fallback for the hook's Kev call | absent from pass-0 r1 C.2 ("env proxies honored") | **Adopted by pass 0** (§2.6, §2.8 Kev row) |
| C13 | Pass-5 DET-50 interpreter versions (3.11.7 / 3.12.10 + mitmproxy 12.3.1 / 3.9.6); l.236 P3 harness pin | §2.3 | consistent |
| C14 | Pass-5 ENV-I10 `PATH` tool list (`python3`, `ps`, `claude`, `nc`, `whoami`, `curl`, `security`/`openssl`/`pgrep`, `lsof`/`flock`) | §2.5 also lists `basename`, `sleep`, `ssh`, `echo` (hook shell), `/bin/sh` | minor omission in pass 5 (wording); no model change |

Remaining inventory disagreements after this round: **C7** (pass-4 T-121 "dead"), and the three unapplied pass-1 wording corrections **C1-C3**
plus the missing edge **C6**. All other sibling statements agree with the consolidated tables.

---

## Delta Summary

| Target | New items | Refined / confirmed |
|---|---|---|
| A verification | none | A1-A8 confirmed. Refinements: A1 wording ("base interpreter uv-managed", not "venv built with uv"); A4 temp-file names (8 random chars) and backfill leaves its temp file on error; A5 two extra `checkpoint` lines; A6 holds for the analysis shell's PATH; A7 lsof prints `python3.1` at default width (conclusion unchanged); A8 Ctrl-C half narrowed to "before mitmdump installs its SIGINT handler" (premise host-verified). A9: r2's env count 42 superseded by pass-5's 43 |
| B consolidation | one merged inventory (22 components, 9 interpreter rows, 7 recorded packages, 17 OS-tool rows, 4 implicit dependencies, 25 file rows, 13 endpoints, 5 added edges), every row tagged with its source round | adopted from pass 5: `ARGS` (43 env inputs), macOS system-proxy fallback for the Kev call |
| C reconciliation | none | 14 rows: 1 disagreement (pass-4 T-121), 4 open pass-1 items, 1 pass-4 gap (pre-trap window), 2 pass-5 items adopted, 1 minor pass-5 omission, 5 consistent |

Retractions: none (CONV-ABS-54..56 unused). New owner items: none (OD-62..OD-65 unused).

## Remaining Gaps

1. LOW, not verifiable on this host: whether mitmproxy installs its SIGINT handler (`tools/main:117-133`) before or after the listener binds,
   which sets how much of the launcher's 10 s readiness wait leaves a Ctrl-C'd mitmdump orphaned. Needs a read of the venv's mitmproxy source
   (authorized for pass 2 only) or the hylo replacement simply makes it moot (OD-50).
2. LOW: Windows `whoami.exe` case vs Go `NameSamCompatible` (OD-48 note); how Claude Code runs hook and status-line commands on Windows (P4).
3. MEDIUM: Claude Code's PATH at hook and status-line run time was not observed (A6); the harness pin makes it irrelevant for parity.
4. Owner action (OD-47): full `pip freeze` of the production venv (transitive packages) and the venv's creator, after the soak.
5. Sibling passes to apply: pass 1 C1-C3 and C6; pass 4 C7 (split T-121) and C10 (pre-trap window).
6. Owner decisions unchanged by this round; OD-62..OD-65 not issued.

## Novelty Assessment

Novelty: NITPICK — findings are refinements, not gaps.

Every round-2 statement in Target A was confirmed against source or host evidence. Two were narrowed, but neither was retracted: the Ctrl-C half
of the orphan window (A8) and the "built with uv" wording (A1). The lsof literal (A7) and the temp-file names (A4) are wording fixes. The env count
moves from 42 to 43, and the hook's Kev call gains the macOS system-proxy fallback. Both of those are adoptions of findings pass 5 already made
and recorded, not new discoveries by this round. The consolidated tables add no component, dependency or endpoint that some earlier pass file does
not already carry. The one sibling disagreement (pass-4 T-121) is about how pass 4 labels a behavior that pass 0 already recorded. Removing this
round's findings would not change how the system is specced.

## Convergence Declaration

Pass 0 has converged: findings are nitpicks, not gaps. (Rounds: r1 SUBSTANTIVE, r2 SUBSTANTIVE, r3 NITPICK; minimum of 2 deepening rounds met.)

## State Checkpoint

```yaml
pass: 0
round: 3
status: complete
timestamp: 2026-11-14T08:40:11Z
novelty: NITPICK
files_scanned: dgx-proxy-coordinator.sh (all), claude-dgx (1-30, 55-100, 129-185 + greps), ROLLBACK.md (15-26 + greps), dgx_proxy.py (40-51 + greps), dgx_ledger_exporter.py (15-27 + greps), dgx_statusline.py (195-206, 1012-1020, 1208-1220), tools/backfill_cost_history.py (108-117); env-name census over all 6 .py
host_facts: {zsh_bg_sigint: SIG_IGN (probe), bg_job_pgid: same as shell, lsof_command_width_default: 9, python3_path_order: anaconda 3.11.7 > homebrew 3.15.0 > usr/bin 3.9.6, uv: 0.12.23, mitmproxy_source_on_host: absent, legacy/.mitmenv: absent, cpython_mkstemp_random_chars: 8}
retractions: []
new_owner_items: []
conv_abs_used: []
sibling_files: {pass-1-deep: C1-C3, C6 open; pass-4-deep: C7 disagreement, C10 gap; pass-5-deep: ENV-43 and ENV-I15 adopted}
next: none for pass 0 (converged); siblings apply §3 actions
```
