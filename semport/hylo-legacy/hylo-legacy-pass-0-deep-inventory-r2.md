# Pass 0 Deepening, Round 2: Inventory audit and mechanical sweep (hylo-legacy)

- **Source:** `$HOME/Dev/hylo/legacy/`, read-only and static. Re-read in full this round: `claude-dgx`, `dgx-proxy-coordinator.sh`,
  `dgx_preflight.py`, both `deploy/*.plist`, `ROLLBACK.md`, `tools/backfill_cost_history.py` (1-40, 84-121). Re-read in part: `dgx_proxy.py:1-105,
  280-300,510-764`; `dgx_statusline.py:58-125,158-240,268-300,360-415,925-950,1198-1245`; `auto_continue.py:13-36,94-166,193-200`;
  `dgx_ledger_exporter.py:13-30,205-220,266-290,365-372,400-414`. Mechanical greps over all 6 `.py` files: every `import`/`from`/`__import__`;
  every `subprocess`/`os.system`/`exec*`/`Popen`/`shell=True`; every `open(`/`urlopen`/`socket.`/`HTTPServer`/`mkstemp`/`os.replace`/`shutil.`/
  `unlink`/`mkdir`/`glob`/`expanduser`; every `os.environ`; every `http(s)://` literal. Shell: every `$VAR`/`${VAR}` and every external command in
  `claude-dgx` and the coordinator.
- **Inputs read:** round 1 (`…-pass-0-deep-inventory.md`, all of it), the broad pass 0, pass-2 r7 header and §1 counts, pass-2 r8 §0/§5/§7 headings
  and l.299, pass-2 r5 l.30 and l.73-75, pass-2 r3 l.160-186 and l.249, pass-2 r2 l.25 and r4 l.221 (env count), pass-3 r1 BC-LN/BC-CO rows,
  extraction validation l.17/l.67/l.71. Sibling files: **pass-1 deep r1 present** (read §A.2, §B.8, §C, Remaining Gaps); pass-4 and pass-5 deep
  files **absent** at 08:34Z.
- **Method and host evidence:** nothing in legacy ran; no proxy; nothing networked; `CLAUDE.local.md` not read; no git commit. Host facts only from
  `command -v`, `--version`, `ls`, `git -C … rev-list/ls-files/check-ignore`, `man launchd.plist`, and a read of the Go 1.26.5 standard-library
  source on this host (`os/user/lookup_windows.go`). Scratch: `…/scratchpad/p0r2/`.
- **Masking:** backend host `<backend>`; home paths `~`.
- **Numbering:** this round issues **CONV-ABS-53** only (54-56 unused). **No new owner item** (OD-62..OD-65 unused).

---

## 1. Hallucination audit of round 1 (Remaining Gap 1 and the orchestrator's named claims)

### 1.1 The named claims, re-verified with fresh evidence

| # | Round-1 claim | Fresh evidence (this round) | Verdict |
|---|---|---|---|
| V1 | Six new entry points / invocation paths | (a) UserPromptSubmit `echo` hook: `claude-dgx:157-159` verbatim. (b) Live reload: no legacy line (mitmproxy-side, cited to P2r4 §2.1 / CONV-ABS-12); re-confirmed by pass-1 deep §A.3 row "Script loader". (c) `DGX_PROXY_RESTART_CMD` → `subprocess.run(restart_cmd, shell=True, check=False)` `dgx_proxy.py:719-722`, 30 s CA poll `:723-725`. (d) `?rebuild=`: `params.get("rebuild") or grew` `dgx_ledger_exporter.py:273,285`. (e) No installer: `grep launchctl` over `legacy/` → 0 hits; `launchctl` exists on host (`/bin/launchctl`). (f) mitmdump host process: `claude-dgx:75` verbatim | **all 6 confirmed** |
| V2 | Preflight runs on the venv, CPython 3.12.10 | `claude-dgx:61` `PF_PY="$HERE/.mitmenv/bin/python"`, `:62` falls back to `python3` only when `DGX_INVISIBLE != 1`. The **3.12.10** value is not a host fact obtainable here (`legacy/.mitmenv` is absent, `ls` → "No such file"); its source is pass-2 r7 l.11 (`.mitmenv/pyvenv.cfg` `home` → uv `cpython-3.12` → `cpython-3.12.10`, `patchlevel.h:26`) | **confirmed** (interpreter path from source; version by reference to P2r7, which read the production venv) |
| V3 | Venv unpinned; `.gitignore` covers neither `legacy/.mitmenv/` nor `legacy/.proxy-state/` | `find` over the repo (excluding `.git`, `.factory`) for `requirements*`, `pyproject.toml`, `uv.lock`, `Pipfile*`, `setup.py`, `.python-version` → **0**. `git check-ignore -v legacy/.mitmenv/x legacy/.proxy-state/port legacy/__pycache__/a.pyc` → only the `.pyc` matches (`.gitignore:17 __pycache__/`) | **confirmed** |
| V4 | 4141-4199 `nc -z` probe runs in invisible mode too; ≤ 59 probes; exit 1 if all busy | `claude-dgx:17-22` sits outside any `DGX_INVISIBLE` test; ports 4141..4199 inclusive = 59; `(( PORT > 4199 )) && … exit 1` `:21`. **Refinement:** skipped entirely when `ROUTER_PORT` is set (`:17-18`); never reached by `claude-dgx trust` (exec at `:13`); runs **before** preflight (`:60`), so it also runs with `DGX_SKIP_PREFLIGHT=1` | **confirmed, refined** |
| V5 | Exporter plist's `~/hylo/legacy/dgx_ledger_exporter.py` is not expanded by launchd | `deploy/io.hylo.ledger-exporter.plist:7`. `man launchd.plist` (host): `ProgramArguments` "maps to the second argument of execvp(3)"; the only expansion mechanism is `EnableGlobbing` ("use the glob(3) mechanism"), and the plist has no such key; the man page never mentions `~`. Python receives the literal `~/…` and does not expand `argv[1]` | **confirmed** (static; launchd was not exercised) |
| V6 | Hidden tunnel dependency of the idle widget | Statusline queries `dgx_llm_last_dgx_request_timestamp_seconds` (`dgx_statusline.py:106`) and renders `☾` from it (`:824-825`); only the exporter emits it (`dgx_ledger_exporter.py:367-370`); VM reaches the exporter only through `ssh -R 127.0.0.1:9210:127.0.0.1:9210` (`deploy/io.hylo.ledger-tunnel.plist:8`). **Refinement (under-reported):** `⛏` depends on the same chain. `dgx_tokens:rate_mtok_month` and `dgx_cost:dgx_usd_per_mtok` (queried `:107-108`, read `:1218-1222`) are recording rules over the exporter's `dgx_llm_tokens_{input,output}_total` (pass-2 r3 l.168-169, l.184). So **two** P1 widgets (`☾`, `⛏`) depend on exporter → tunnel → VM. Round 1's citation "r3 l.185" is l.184 | **confirmed, scope widened to 2 widgets** |
| V7 | CONV-ABS-29: Homebrew `flock` present | `command -v flock` → `/opt/homebrew/bin/flock`; `ls -la` → `../Cellar/flock/0.4.0/bin/flock` (dated Jul 22); `flock -h` usage line 1 `flock [-sxun][-w #][-E #] fd#` (so `flock 9` at coordinator `:43` is supported) | **confirmed** (CONV-ABS-29 stands) |
| V8 | Windows `whoami` / Go `Username` give `DOMAIN\user` (OD-48) | Go 1.26.5 source on host: `user.Current()` on Windows → `current()` → `windows.GetUserName(syscall.NameSamCompatible)` → `Username: username` (`lookup_windows.go:282,295`); the SID path also builds `domain + "\" + username` (`:229,237`). Windows `whoami.exe` output was **not** verifiable on this host (LOW): it is commonly lower-cased, so whoami and Go may differ in **case** as well as from macOS/Linux | **confirmed for Go; whoami form LOW**. OD-48 recommendation (a) unaffected; add "case may differ from `whoami`" to its note |

### 1.2 The five hallucination classes across the rest of round 1

| Class | Round-1 item checked | Result |
|---|---|---|
| 1 Over-extrapolated lists | A.2's 10 mitmdump option rows against pass-2 r7 §1 (93 = 3 set + 90 default, l.63-68), r4 l.138 (`listen_host ""`), r6 l.77 (`tcp_timeout` 600), r7 l.140-146 (`websocket`, `flow_detail` 1), r8 l.299 ("message sizes not determinable" supports "logged without sizes") | all 10 grounded. `confdir` default `~/.mitmproxy` is grounded by `claude-dgx:80` and P2r6 l.27 rather than an option-table line (MEDIUM) |
| 1 | B.3 "24 tool rows" and every call-site line | 24 rows counted. Every call site re-grepped: `nc` `:21,73,77,78,89`; `sleep` `:77,94` + coordinator `:35`; `kill` `:97` + `:23,36`; `curl`/`grep` `:85`; `lsof`/`grep` coordinator `:15,28`; `mkdir` `:12`; `flock` `:43`; `ps` `dgx_statusline.py:280`; `security` `dgx_proxy.py:568,590,638,693`; `openssl` `:578`; `pgrep` `:606`; `/bin/sh` `:722`; `claude` `claude-dgx:185`, `auto_continue.py:154-156`; `ssh` tunnel plist `:6`. Omitted, harmless: zsh builtins `printf` (`claude-dgx:183`), `source`/`set -a` (`:115`), `exec` (`:13`, coordinator `:42`) |
| 2 Miscounted enumerations | C.1 "9 file rows absent from pass 0 and pass 1" | 7 rows carry the **New** tag; the other 2 named in the Delta (plist `~` artifact, `~/.ssh/config`) are untagged but are absent from the broad pass 0 and pass-1 §4.8 (checked by grep). Count 9 holds; tagging is a wording fix |
| 2 | Python import census "stdlib only" lines | **Omission:** `dgx_ledger_exporter.py:27` `state_lock = __import__("threading").Lock()` (a dynamic stdlib import, not in round 1's `:15-20,124,144,229`). Dead imports: round 1 had `urlparse` (exporter `:20`); **also dead:** `from mitmproxy import ctx` (`dgx_proxy.py:44`, no other `ctx` token) and `logging` (`:31`), whose only use is `log = logging.getLogger("dgx_proxy")` (`:51`), with `log` never referenced again |
| 3 Fabricated names | "mitmdump host process", "live reload", "LaunchAgent installation" | descriptive labels, not claimed as source names. No fabricated identifiers found |
| 4 Same-basename conflation | `claude-dgx` (launcher file) vs `claude` (binary); `io.hylo.*` labels vs the owner's installed agents | kept distinct in round 1. Note: the plist **labels** are scrubbed; pass-2 r4 l.26 says the installed agents "match" in `KeepAlive`/`RunAtLoad`/interpreter only |
| 5 Metrics | 11 files / 3,181 lines / 164,151 bytes / 19 legacy commits / 26 repo commits / 4 executable files | recounted: `find legacy -type f -exec wc -l` → 3,181 (per-file identical); `cat … \| wc -c` → 164,151; `git rev-list --count main -- legacy` → 19, `main` → 26; `git ls-files legacy` → 11; `find -perm -u+x` → `auto_continue.py`, `claude-dgx`, `dgx_ledger_exporter.py`, `dgx-proxy-coordinator.sh`. Entry anchors: `main()` `dgx_statusline.py:1200`, `main_subagent` `:928`, `render_subagent_rows` `:888`, `__main__` `:1238`; hook `:209/:274`; exporter `:410`; proxy `:759`; backfill `:84/:120` — all exact |

### 1.3 Retraction

| Marker | Prior claim | Ground truth | Evidence | Spec impact |
|---|---|---|---|---|
| **CONV-ABS-53** | Round 1 §B.2 row "h11 … **not recorded**" and Remaining Gap 4 "**Not recorded anywhere in authorized sources:** the h11 version and the full package list of the production venv" | Pass-2 r7 read the production venv's `dist-info` directories and recorded **certifi 2026.10.23, pyOpenSSL 26.4.0, cryptography 50.0.2, h11 0.16.0, h2 4.4.1, wsproto 1.3.2**, plus the base interpreter's provenance: `.mitmenv/pyvenv.cfg` `home` → a **uv-managed** `cpython-3.12` → `cpython-3.12.10` | pass-2 r7 l.9-11 | OD-47's pin list is largely known already: the P3 harness can pin these 6 + mitmproxy 12.3.1 + CPython 3.12.10 now; only a complete `pip freeze` (transitive packages beyond these) remains an owner action. The venv was built with **uv** (host has `uv 0.12.23` at `/opt/homebrew/anaconda3/bin/uv`), which is the natural tool for OD-47 option (a) |

---

## 2. Mechanical sweep diff against round 1 (Target B)

### 2.1 Top-level files (all 11)

| File | In round 1? | New this round |
|---|---|---|
| `claude-dgx`, `dgx_proxy.py`, `dgx_statusline.py`, `auto_continue.py`, `dgx_ledger_exporter.py`, `dgx_preflight.py`, `dgx-proxy-coordinator.sh`, `tools/backfill_cost_history.py`, both `deploy/*.plist` | yes | — |
| `ROLLBACK.md` | yes (text-only tool mentions) | **Dangling references:** `checkpoint-20261109-*` directories (`:3-4,13-14,44-46`), `opus_router.py` (`:11,13,46`) and the memory file `dgx-warlock-opus-serving.md` (`:30`) are not in the tree, so the document is not actionable inside hylo. **Venv location stated two ways:** `:19` "`dgx-llm/.mitmenv`" vs `:23` `~/hylo/legacy/.mitmenv`; `claude-dgx:36` also says "`dgx-llm/.mitmenv`" while the code uses `$HERE/.mitmenv` (`:61,75`). Input for OD-47 (where the harness venv lives) |
| hidden files in `legacy/` | — | none (`ls -la`) |

### 2.2 Process-spawn call sites

Python: 10 sites (`auto_continue.py:154`; `dgx_proxy.py:568,578,590,606,638,693,722`; `dgx_statusline.py:280`), **all** in round 1's B.3. No
`os.system`, `os.exec*`, `os.popen`, `Popen` or `os.spawn*` anywhere. `ps` has `timeout=1` and walks at most 6 ancestors (`dgx_statusline.py:279-281`).
Shell: every external command is in B.3 (see §1.2). **Diff: 0 missing spawn sites.**

### 2.3 Opened paths

Every `open`/`mkstemp`/`replace`/`unlink`/`glob`/`shutil` site maps to a round-1 C.1 row. Refinements only:

| Path | Evidence | Note |
|---|---|---|
| `~/.cache/dgx-llm/statusline-nosession.json` | `dgx_statusline.py:1214-1215` (`sid = d.get("session_id") or "nosession"`) | a fixed-name variant of the session cache when stdin lacks `session_id`; the session-cache `sid` is **not** sanitized (the mix cache is, `:1017`) |
| mkstemp temporaries `<name>.XXXXXX` in `~/.cache/dgx-llm/` and `cost-history.XXXXXX` | `dgx_statusline.py:201`; backfill `:113` | left behind if `json.dump` raises after `mkstemp` (the status-line `except: pass`, `:205-206`, does not unlink) |
| `/usr/bin/python3` reads the literal `~/hylo/legacy/…` | V5 | see §1.1 |

**Diff: 0 new path classes.**

### 2.4 Sockets and URLs

Connect sites: preflight `socket.create_connection` `:23`; status line `opener.open` `:170` (proxy-bypassing); hook `urlopen` `:113`; the proxy's
upstream via mitmproxy after `flow.request.scheme/host/port` are swapped (`dgx_proxy.py:161-163`). Listen: exporter `HTTPServer(("0.0.0.0", PORT))`
`:414`; mitmdump. URL literals: `192.0.2.10:8080/8008/8428`, `127.0.0.1:$PORT`/`$MITM_PORT`, docs links `code.claude.com` (`claude-dgx:107,124`,
comments), preflight text `127.0.0.1:8080/health` (`:38`, text). **Diff: 0 new endpoints.** One refinement: the DGX-lane scheme is
`u.scheme or "http"` (`dgx_proxy.py:81`), so "plain HTTP" in round 1 C.2 is the **default**, not a fixed property (an `https` upstream is OD-41's case).

### 2.5 Environment inputs (not tabulated by round 1)

Recount: Python reads **27** distinct names (`os.environ.get`), the launcher **21** (`ANTHROPIC_CUSTOM_HEADERS`, `DGX_AUTOCONTINUE`, `DGX_ENGLISH`,
`DGX_INVISIBLE`, `DGX_KEV_MODEL`, `DGX_KEV_THRESHOLD`, `DGX_KEV_URL`, `DGX_MAIN_MODEL`, `DGX_PRINT_ARGS`, `DGX_PROFILE`, `DGX_REMOTE`, `DGX_SAFE`,
`DGX_SANDBOX`, `DGX_SKIP_PREFLIGHT`, `DGX_STATUSLINE`, `DGX_UPSTREAM`, `DGX_USER`, `HOME`, `PWD`, `ROUTER_PORT`, `TMPDIR`), overlap **6** → **42**.
This matches pass-2 r2 l.25 / r4 l.221 (42). The coordinator reads no environment input beyond `TMPDIR`. mitmproxy itself additionally reads
`SSLKEYLOGFILE`/`MITMPROXY_SSLKEYLOGFILE` (round 1 A.2 row). Note: `$(whoami)` at `claude-dgx:43` runs only when `DGX_USER` is unset (lazy `:-`).

### 2.6 Host interpreter resolution (refinement of B.1)

`which -a python3` → `/opt/homebrew/anaconda3/bin/python3` (3.11.7), `/opt/homebrew/bin/python3` (**3.15.0**), `/usr/bin/python3` (3.9.6). The
status-line and hook oracle "python3 3.11.7" is Anaconda's only because Anaconda precedes Homebrew on this PATH; without it, the same launcher
command would run **3.15.0**. The pass-3 harness already pins `/opt/homebrew/anaconda3/bin/python3 -I` (P3r4 l.10), so parity is unaffected; the
inventory records the fragility. `openssl` resolves to Anaconda OpenSSL 3.0.13, then Homebrew, then `/usr/bin/openssl` = LibreSSL 3.3.6 (round 1
correct). `curl` also resolves to Anaconda's (visible mode only).

---

## 3. Gap closures and cross-pass notes

### 3.1 Round-1 Remaining Gap 3 (lsof COMMAND for the venv mitmdump): closed

Pass-2 r5 l.30 recorded the orchestrator's `lsof`: the 9 legacy proxies appear as **`python3.12`**, not `mitmdump`. The coordinator's
`proxy_alive_on_port` greps the whole `lsof` line for `mitmdump` (`dgx-proxy-coordinator.sh:15`); no field (COMMAND, NAME `*:<port> (LISTEN)`)
contains it. Static consequence: `state_valid` is always false (`:22`), and `start_new` always starts a mitmdump, waits 10 s for a match that never
comes, kills it and returns 1 "mitmdump failed to bind" (`:35-36`). **On this host the coordinator cannot succeed, with or without `flock`.**
BC-CO-001/002 describe the code correctly; they are unreachable in practice. Spec impact: none (OOS, OD-19); hylo's PID/state-file check replaces
name matching. Two dead coordinator details: `STALE_SEC=120` (`:11`) is never read; the comment at `:45` ("kill leftovers…") has no code.

### 3.2 Pre-trap window in the launcher (cross-pass note for passes 3 and 4; not an inventory item)

mitmdump starts at `claude-dgx:75`; the `trap … EXIT INT TERM` that kills it is armed only at `:97`. The `exit 1` at `:78` (not listening after
40 × 0.25 s) therefore leaves a still-starting mitmdump running. Static, MEDIUM-LOW: in a non-interactive shell, `&` jobs start with SIGINT ignored,
so Ctrl-C during the 10 s wait also leaves it running. No pass records this window (grep for "orphan", "before the trap", `:97` ordering). hylo:
belongs with OD-50 (shared-proxy lifecycle), no new OD.

### 3.3 Comment drift (nitpick)

`dgx_ledger_exporter.py:276-277` says the status line's idle meter uses `dgx_llm_last_request_timestamp_seconds`; the status line actually queries
`dgx_llm_last_dgx_request_timestamp_seconds` (`dgx_statusline.py:106,824`). `fetch_sample`'s docstring promises per-session series (`:161-163`) that
`QUERY` (`:102-123`) does not request. `claude-dgx:5` still says the launcher "starts the opus router on 127.0.0.1:4141".

---

## 4. Reconciliation with sibling deep files (Target C)

Pass-4 and pass-5 deep files: **absent** (checked 08:34Z). Pass-1 deep r1:

| # | Pass-1 deep statement | Inventory fact | Action for pass 1 |
|---|---|---|---|
| R1 | §A.2 C8: "`flock` absent on macOS, so it would run unlocked"; §C row C8: "D5 (no `flock` on macOS …)" | CONV-ABS-29: base macOS lacks `flock`, but this host has Homebrew `flock` 0.4.0 on PATH, which supports `flock 9`. And per §3.1 the coordinator fails anyway (lsof name match) | reword to "not part of base macOS"; cite CONV-ABS-29 and §3.1 |
| R2 | §C "Configuration (40 env inputs …)" | 42 (§2.5; pass-2 r2 l.25 and r4 l.221 already corrected 40 → 42) | update to 42 |
| R3 | Remaining Gap 4: "OD-44 and **OD-46..OD-49 unused**" | pass-0 r1 issued **OD-46, OD-47, OD-48** (OD-49 unused) | correct the unused list |
| R4 | §B.4 "84 further hosts observed" | round 1 C.2 "85 distinct upstream hosts" | consistent (85 = `api.anthropic.com` + 84) |
| R5 | §A.2 C5 exporter `0.0.0.0:9210` IPv4; C2a mitmproxy 12.3.1; C6b UserPromptSubmit; C7 one-shot per launch; C10 tunnel args | identical to round 1 A.1/C.2 | consistent |
| R6 | §A.2 "VictoriaMetrics → exporter through the tunnel" | consistent; pass 1 does not draw the exporter → status line edge for `☾`/`⛏` (§1.1 V6) | round-1 Remaining Gap 5 still applies |

---

## Delta Summary

| Target | New items | Refined / confirmed |
|---|---|---|
| A audit | **1 retraction (CONV-ABS-53)**: the production venv's package list is recorded (P2r7), not unrecorded; **5 dependencies new to the pass-0 inventory**: pyOpenSSL 26.4.0, cryptography 50.0.2, h2 4.4.1, wsproto 1.3.2, h11 0.16.0 (version), plus the uv-managed CPython 3.12.10 base | V1-V8 all confirmed with fresh evidence; V4 refined (`ROUTER_PORT` skip, before preflight); V6 widened from 1 to 2 widgets (`☾`, `⛏`); V8 Go confirmed from stdlib source, whoami case LOW; 5-class audit: 1 import omission (`__import__("threading")`), 2 extra dead imports (`ctx`, `logging`), tag wording in C.1; all metrics re-derived |
| B sweep | 0 new files, 0 new spawn sites, 0 new endpoints, 0 new path classes | ROLLBACK dangling refs and two venv locations; `statusline-nosession.json`; mkstemp leftovers; DGX scheme is a default; 42 env inputs; PATH shadowing (Homebrew python3 3.15.0) |
| Gap closure | Gap 3 closed: coordinator can never succeed on this host (lsof shows `python3.12`) | pre-trap orphan window flagged for passes 3/4 |
| C reconcile | — | 3 pass-1 corrections (flock wording, 40 → 42, OD-46..48 used); 3 consistent rows |

## Remaining Gaps

1. LOW, not verifiable on this host: Windows `whoami.exe` output case vs Go's `NameSamCompatible` form (OD-48 note); how Claude Code runs hook and
   status-line command strings on Windows (carried from round 1 Gap 2, check in P4).
2. Owner action (OD-47): a complete `pip freeze` of the production venv for transitive packages beyond the 7 recorded (mitmproxy + 6), after the soak.
3. Pass 3/4 to evaluate: the launcher's pre-trap window (§3.2), static and unrecorded.
4. Pass 1 to apply R1-R3 (§4) and draw the exporter → tunnel → VM → status line edge for both `☾` and `⛏`.
5. Pass-4 and pass-5 deep files did not exist at write time; reconcile in the next round.
6. Owner decisions unchanged by this round: OD-01..OD-23, OD-25, OD-26, OD-28..OD-43, OD-45..OD-48 (pass 0) and OD-50..OD-53 (pass 1) pending;
   OD-24, OD-27 ruled; OD-44, OD-49 unused; OD-62..OD-65 not issued.

## Novelty Assessment

Novelty: SUBSTANTIVE

By the round's stated rule, a retraction or a new dependency is SUBSTANTIVE. This round makes one retraction (CONV-ABS-53: round 1 called the
venv package list unrecorded, but pass-2 r7 recorded it). It also adds five pinned mitmproxy dependencies and the uv-built base interpreter to the
pass-0 inventory. That changes OD-47 from "pin unknown, owner must freeze" to "pin mostly known, harness can pin now". These items come from an
earlier pass file, not from new source reading. The mechanical source sweep found **no** new file, spawn site, endpoint or path class. Every
other finding is a confirmation or a refinement. If the CONV-ABS-53 group were removed, this round would be NITPICK.

## Convergence Declaration

Another round needed: CONV-ABS-53 and the new dependency rows must be audited in round 3, and the pass-4 and pass-5 sibling files must be
reconciled once they exist. The source sweep itself found nothing new, so round 3 is expected to be short. This is not a prediction of NITPICK.

## State Checkpoint

```yaml
pass: 0
round: 2
status: complete
timestamp: 2026-11-14T08:34:01Z
novelty: SUBSTANTIVE
files_scanned: claude-dgx (all), dgx-proxy-coordinator.sh (all), dgx_preflight.py (all), deploy/*.plist (all), ROLLBACK.md (all), tools/backfill_cost_history.py (1-40, 84-121), dgx_proxy.py (1-105, 280-300, 510-764), dgx_statusline.py (58-125, 158-240, 268-300, 360-415, 925-950, 1198-1245), auto_continue.py (13-36, 94-166, 193-200), dgx_ledger_exporter.py (13-30, 205-220, 266-290, 365-372, 400-414); mechanical greps (imports, spawns, paths, sockets, env, URLs) over all 6 .py + 2 zsh files
host_facts: {python3: anaconda 3.11.7, homebrew_python3: 3.15.0, usr_bin_python3: 3.9.6, zsh: 5.9, flock: homebrew 0.4.0 (fd# form), openssl: anaconda 3.0.13 > homebrew > LibreSSL 3.3.6, uv: 0.12.23, go: 1.26.5, launchctl: present never invoked, mitmdump: not on PATH, legacy/.mitmenv: absent}
retractions: [CONV-ABS-53 (venv package list "not recorded")]
new_owner_items: []
conv_abs_used: [53]
sibling_files: {pass-1-deep: reconciled (R1-R3 corrections), pass-4-deep: absent, pass-5-deep: absent}
next: pass 0 round 3 (audit CONV-ABS-53 group; reconcile pass-4/5 deep when present)
```
