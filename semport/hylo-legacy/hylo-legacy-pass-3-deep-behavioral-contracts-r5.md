# Pass 3 deepening, round 5: behavioral contracts (hylo-legacy)

- **Scope:** `legacy/`, unchanged: 11 files, 3,181 lines (recounted with `wc -l`). Re-read this round: all of `dgx_proxy.py` and `auto_continue.py`;
  `dgx_statusline.py:56-420,438-456,496-532,638-1245`; `dgx_ledger_exporter.py:1-150,196-300,396-414`; `tools/backfill_cost_history.py:36-82`;
  `claude-dgx:11-36,70-97,156-185`; `dgx-proxy-coordinator.sh:38-50`. mitmproxy 12.3.1 `options:241-246`, `proxy/server:50,290-308,344-354`,
  `tools/main:126-133` (read-only, only to check pass-2 r6's citations).
- **Inputs read:** pass-3 r4 (canonical index, OD mapping, RET crosswalk) and r3; pass-2 r5; **pass-2 r6** (`…-pass-2-deep-domain-r6.md`, present
  from 01:10 local; read only, not edited); the broad pass-3 file and r1/r2 BC rows (for cited lines); `docs/PLAN.md` §7 and §10.
- **Orchestrator messages applied (2026-11-14):** (1) OD numbers. OD-35 (tap lines over 64,000 B) and OD-36 (backfill unscheduled) keep pass-3 r4's
  numbers. Pass-2 r6's OD-35/OD-36 become **OD-37** (mitmproxy `tcp_timeout` 600 s, HY-TIMEOUT-1) and **OD-38** (in-flight flows at proxy exit). New
  pass-3 retractions would have to start above CONV-ABS-20. (2) Ledger evidence for V-3: all 36 unpaired `dgx_request` events are dated
  2026-11-11. The 4 DGX `Client disconnected.` errors came 0, 342, 0 and 181 s after the session's latest request (§4).
- **Method:** static reading plus scripts in
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r5/`, run with the oracle
  `/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7). The exporter pin was also run with `/usr/bin/python3 -I` (3.9, the exporter's production
  interpreter, BC-EX-023). Every script execs a **text copy** of a legacy file in a fresh namespace, with `HOME`, the ledger and the hook log
  redirected to the scratchpad, and asserts that the source lines it depends on have not drifted. Scripts: `ast_walk.py` (→ `ast_out.txt`),
  `cover.py` (→ `cover_out.txt`), `tally.py`, `od32_r5.py` (→ `od32_r5_out.txt`), `ex_race.py` (→ `ex_race_out.txt`), `sample.py`, `rows_pin.py`.
  No main() and no server ran. Nothing networked, nothing proxy-related. `CLAUDE.local.md` was not read. No git commit.
- **Notation:** `\e` is ESC (U+001B). A bare `:N` means the file named in the section heading. **P2rN**/**P3rN** = pass-2/pass-3 round N.
- **IDs (append-only):** new **BC-EX-027** and **BC-PX-046**. New owner items **OD-39** and **OD-40** (provisional, the next numbers after OD-38;
  the orchestrator reconciles). **No retraction this round**, so no CONV-ABS number is used (the next free one is 21).

---

## 1. Target A: round 4's SUBSTANTIVE item, re-verified from scratch

`od32_r5.py` is a new script with new fixtures, not round 4's `od32.py`. It writes transcripts line by line, runs the copied `_mix_counts` once per
"window" (one refresh), and reads the mix cache. Fixtures use a user line U0, message A (out 10), message B (out 5), and the poisoned line **W** = a
second line of A with `output_tokens: "abc"`. A's id is already in `seen_ids`, so W's usage is not counted (CP-T05 rather than CP-T04), and W opens a
new turn because `cur.id` is B. The lu-None form omits U0. **K** = legacy across both windows. **R orig** = P2r5's OD-32 applied to the cache after
window 1 (non-numeric `out` → `cur = null`). **R amend** = round 4's amended rule (only when `cur.t0` is a number). **N** = native D4-EX-2 Go:
legacy run with W deleted when the CP-T05 W-predicate holds (it requires `lu` set, BC-SL-098), and with W kept otherwise.

| Case (window 2 lines) | K legacy | R orig | R amend | N native Go |
|---|---|---|---|---|
| C1 lu set; closer (system) | window 2 raises `TypeError at :994`; cache stays at window 1, `cur.out = "abc"` | `cur null`, `lr [10.0, true]`, conv 5 | same as R orig | `cur null`, `lr [10.0, true]`, **conv 4** |
| C2 lu set; A again (out 900), closer | `TypeError at :994` | `lr [180.0, false]`, conv 6 | same | `lr [180.0, false]`, **conv 5** |
| C3 lu set; new id C (out 300), no closer | `TypeError at :994` | `cur = C (t0 lu, out 300)`, tout 315, conv 6 | same | same turn state, **conv 5** |
| **C4 lu None; A again (out 900), no closer** | ok; `cur {"id":"A","t0":null,"t1":…805.0,"out":"abc"}` | **`"out": 900`** | `"out": "abc"` | `"out": "abc"` (W not skipped) |
| C5 lu None; A again, closer | ok; `cur null` (`_finish_turn` returns at `t0 is None`, `:991`) | equal | equal | equal |

Window-1 states pinned: lu set → `{"id": "A", "t0": 1794646800.0, "t1": 1794646803.0, "out": "abc"}`; lu None →
`{"id": "A", "t0": null, "t1": 1794646803.0, "out": "abc"}`.

**Verdicts on the three spec changes:**

| Round-4 change | Verdict | Basis |
|---|---|---|
| 1. Go's mix-cache `cur.out` is a raw JSON value | **CONFIRMED** | C4: native Go (N) holds `"out": "abc"` and must write it back verbatim (ruling b). A number-typed field cannot hold it |
| 2. Go's `finishTurn` tests `cur == nil` / `t0 == null` before it reads `out` | **CONFIRMED** | C5: legacy and N close a `t0`-null turn whose `out` is `"abc"` with no crash. `:991` returns before `:993-994` touch `out` |
| 3. OD-32 amended: `cur = null` only when `cur.t0` is a number and `cur.out` is not int/float/bool | **CONFIRMED** | C4: the original rule diverges from legacy and N (`900` vs `"abc"`). The amended rule matches both. C1-C3: the amended rule gives N's turn state (`lr`, `lu`, `cur`, `tout`, `ids`) from the next turn event on. The known residual is reproduced: **conv is +1** (W's one-character text, counted before legacy saved the cache) |

CONV-ABS-15 and BC-SL-103 stand as written. No change to BC-SL-100/103.

---

## 2. Target B: mechanical completeness diff (the convergence test)

### 2.1 Method

- **Python (6 files):** `ast_walk.py` lists every `FunctionDef` (methods and nested functions included), every call that writes to
  stdout/stderr/a file/the ledger/the decision log, exits, or starts a process (`print`, `ledger`, `note`, `emit`, `_log`, `open(…, "w"/"a")`,
  `json.dump`, `os.replace`, `mkstemp`, `fdopen`, `mkdir`/`makedirs`, `unlink`, `write_text`, `wfile.write`, `send_*`/`end_headers`, `sys.exit`,
  `subprocess.run`), and every `ExceptHandler`. False positives removed: 8 `str.replace` calls (`esc` ×3 at exporter `:72`, statusline `:983`,
  backfill `:39`, hook `:215`, proxy `:583,:599`). Added by hand, because the name filter missed them: `shutil.move` (proxy `:712`), `shutil.rmtree`
  (`:717`), and the `input()` prompt to stdout (`:688`).
- **Coverage, step 1 (mechanical):** `cover.py` collects every line range cited on any line that names a BC, in all pass-3 files (broad, r1-r4). It
  maps the range to the file implied by the BC prefix, unless a filename is written. An item counts as cited if its line (or, for a function, its
  span) falls inside a range.
- **Coverage, step 2 (reading):** every uncited item was read and assigned to a BC or ruled out of scope. Code that is cited but sits in regions
  re-read this round was also checked for behavior that the citing BC does not state. That reading found BC-EX-027 inside a **cited** region
  (`:280-287`, cited by BC-EX-003). So mechanical citation does not prove semantic coverage.
- **Shell (2 files):** a structured grep (`echo|printf|exit|>>|> |exec|kill|trap|source|export|unset` plus control flow) over `claude-dgx` and
  `dgx-proxy-coordinator.sh`, grouped into output, exit and process branches.

### 2.2 Totals

| File | Functions | Write/effect sites | Exception handlers | Items | Cited (step 1) | Assigned on reading (step 2) | New BC needed |
|---|---|---|---|---|---|---|---|
| `dgx_statusline.py` | 36 | 12 | 17 | 65 | 62 | 3 (`truecolor` → BC-SL-056; `_fmt_tokens` + its handler → BC-SL-097) | 0 |
| `dgx_proxy.py` | 35 | 75 | 14 | 124 | 75 | 49 (trust CLI → BC-PX-031; module hook delegators `:524-548` → BC-PX-030; import guard `:45` → BC-PX-031) | 0 |
| `dgx_ledger_exporter.py` | 6 | 8 | 9 | 23 | 20 | 1 (`log_message` → BC-EX-002, refined §2.4) | **2** (`_current_size` and its handler → BC-EX-027) |
| `auto_continue.py` | 9 | 11 | 7 | 27 | 27 | 0 | 0 |
| `dgx_preflight.py` | 0 | 5 | 1 | 6 | 6 | 0 | 0 |
| `tools/backfill_cost_history.py` | 3 | 7 | 2 | 12 | 12 | 0 | 0 |
| **Python total** | **89** | **118** | **50** | **257** | **202** | **53** | **2** |
| `claude-dgx` | 1 (`is_router`) | 14 branches | — | 15 | — | 10 → BC-LN-001/003/004/006/010/011 | 0; **5 out of scope (D6)** |
| `dgx-proxy-coordinator.sh` | 3 | 8 branches | — | 11 | — | 11 → BC-CO-001/002 (OOS, unwired) | 0 |
| **All** | **93** | **140** | **50** | **283** | — | — | **2 items + 1 cited-region gap → BC-EX-027** |

(`tally.py` output: 89 functions, 118 write/effect sites, 50 handlers. Raw AST write list 123, minus 8 `str.replace` false positives, plus 3
hand-added sites = 118. Per-file write counts: status line 13−1, proxy 74−2+3, exporter 11−3, hook 12−1, preflight 5, backfill 8−1.)

Plists (`deploy/*.plist`) → BC-SV-001/002. `ROLLBACK.md` is documentation (OOS).

### 2.3 Every item not cited in step 1, with its disposition

| Item(s) | Lines | Disposition |
|---|---|---|
| Trust CLI: `_login_keychain`, `_file_fingerprint` (+ handler `:584`), `_keychain_fingerprint`, `_mitmdump_running`, `_read_state` (+ handler `:612`), `_write_state`, `cmd_trust_remove`, `_build_parser`, and their 36 effect sites (prints, `sys.exit`, `security`/`openssl`/`pgrep`/restart subprocesses, state-file write/unlink, `shutil.move`/`rmtree`, the `input()` prompt, the bare-invocation usage line and exit 2 at `:763-764`) | `dgx_proxy.py:567-764` | **BC-PX-031**, out of parity scope (replaced by `hylo ca`, D13; RET-06 narrowing). The broad row cites only the install/status/rotate entry points. Its text covers the whole CLI. No new BC |
| Module hooks `request`, `responseheaders`, `response`, `error` | `dgx_proxy.py:524-548` | Delegation to `_router` (`:521`). **BC-PX-030** (module-level config and router instance). No behavior of their own |
| `except ImportError: pass` | `dgx_proxy.py:45` | Lets the CLI run without mitmproxy. **BC-PX-031**. In the addon path mitmproxy is always importable |
| `truecolor` | `dgx_statusline.py:140-141` | SGR helper for `heat()` colours. **BC-SL-056** |
| `_fmt_tokens` + `(TypeError, ValueError)` → `"?"` | `dgx_statusline.py:876-885` | Called only by `render_subagent_rows` (`:911`). **BC-SL-097** (`--subagent`, OD-14) |
| `Handler.log_message` (no-op) | `dgx_ledger_exporter.py:406-407` | **BC-EX-002**, refined §2.4 |
| `_current_size` + `except OSError: return 0` | `dgx_ledger_exporter.py:64-68` | **Uncovered behavior** → new **BC-EX-027** (§3.1) |
| `claude-dgx` router port probe, `no free router port in 4141-4199` → exit 1 | `claude-dgx:15-22` | **Out of scope (D6).** It belongs to the visible mode's machinery but runs in invisible mode too (P2r6 §4.2 "launcher oddity"). Its only effect on an invisible launch is an exit 1 when all 59 ports 4141-4199 are listening (judgment: not a realistic state). hylo has no router (D6) |
| `is_router`; visible-mode router start, its log `${TMPDIR}/opus-router.$$.log`, and two stderr+exit branches | `claude-dgx:85-96,101-102` | **Out of scope (D6)**, as the broad pass-3 scope note says (`claude-dgx:85-96,102`). `opus_router.py` is absent from `legacy/`, so this path fails at startup |

**Diff result:** 283 items. Python: 202 cited, 53 assigned to existing BCs on reading, **2 uncovered** (one function and its handler, plus the
cited-region gap at `:280-287`: together, BC-EX-027). Shell: 21 covered by BC-LN/BC-CO, 5 explicitly out of scope (D6). No uncovered item in the
status line, proxy, hook, preflight or backfill.

### 2.4 Refinements found during the reading (no new BC)

- **BC-EX-002:** `log_message` is a no-op (`:406-407`). `BaseHTTPRequestHandler` routes both access lines and `log_error` (used by `send_error`,
  for example the 501 for non-GET methods and the 400 for a malformed request line) through it. So the exporter writes **nothing to stderr per
  request**. Only `socketserver`'s `handle_error` tracebacks (BC-EX-021 crashes) reach the launchd log. This is not an exposition-parity surface.
- **BC-HK-013 / BC-HK-019:** import-time `float()`/`int()` of `DGX_KEV_THRESHOLD`, `DGX_KEV_TIMEOUT`, `DGX_KEV_MESSAGES`, `DGX_KEV_CHARS`
  (`auto_continue.py:33-36`) raise before `main()`. That is BC-HK-019's "no top-level guard: exit 1, no stdout" (P2r2 H-catalogue). Same for the
  exporter's `DGX_SESSION_LIMIT`/`DGX_LEDGER_EXPORTER_PORT` (`:24-25`): a startup crash, which falls under BC-EX-021's startup crash loop
  (P2r2 T5). `opus_verdict` (`:141-166`) is never called (BC-HK-013, dead).
- **BC-PX-020 / BC-PX-024 (P2r6 mirror case, absorbed):** a flow addressed directly to the backend host (absolute-form request through the
  proxy) skips the `api.anthropic.com` gate. On success, `response()` still writes `dgx_reply` (`:254-274`) with empty attribution (`_dgx` unset, so
  `attrib = {}`). On failure, `error()` writes `dgx_upstream_error` with empty attribution. Neither event name identifies the lane by itself.

---

## 3. New BCs

### 3.1 BC-EX-027 (new): the rebuild trigger watches only the ledger size, so the exposition can lag the files

**Source:** `dgx_ledger_exporter.py:281-287`, `:64-68`, `:114-120`, `:214-236`.

```python
try:
    grew = os.stat(LEDGER).st_size != processed_size     # :282
except OSError:
    grew = False
if params.get("rebuild") or grew:
    rebuild()                                              # reads ledger to EOF, then the hook log
    processed_size = _current_size()                       # :287, a SECOND stat, after the read
```

**Contract (legacy):**

1. A scrape rebuilds iff `?rebuild` has a non-blank value or the ledger size differs from `processed_size`. A change to the **hook log**
   (`auto-continue.log`) alone never triggers a rebuild.
2. `processed_size` is taken by a second `stat` **after** `rebuild()` has read the ledger. Bytes appended between rebuild's EOF and that stat are
   recorded as processed but were never parsed. A line that was half-written when rebuild read it fails `json.loads`, is skipped (`:117-120`), and
   its completed size is then recorded as processed.
3. Either way the exposition **omits those events until the ledger next changes size**. The next change triggers a full rescan that recovers
   everything (rebuild is not incremental). A ledger that disappears after start (`stat` OSError) freezes the last state: `grew = False`, no reset.

**Pinned** (`ex_race.py`, identical output on 3.11.7 and 3.9; the hook between `rebuild()` and `:287` is injected by wrapping the copied
`rebuild`):

| Case | Scrape 1 | Scrape 2 (no file change) | File state | Recovery |
|---|---|---|---|---|
| A: a second `dgx_request` appended after rebuild's EOF, before `:287` | `dgx_llm_requests_total{…} 1` | **1** | 2 `dgx_request` lines; `processed_size 302` = file size 302 | next ledger append → **2** |
| B: second line half-written at read time, completed before `:287` | 1 | **1** | same | same |
| D: hook log gains a `[kev-allow] … p_done=0.800` line, ledger unchanged | `allowed 0`, no `p_done_latest` | **`allowed 0`** | — | after one ledger append: `allowed 1`, `dgx_llm_fakestop_p_done_latest 0.800` |

**Production relevance (judgment, labelled):** the Stop hook writes its log line at the **end** of a turn, after that turn's last ledger line. So
the newest fake-stop tally (and `p_done_latest`) usually appears only on the next ledger write, which is the next API call or rate-limit change.
During active use the lag is seconds. After the last turn of a session it lasts until the next activity. Window 2 needs an append inside the
microseconds-to-milliseconds gap between rebuild's EOF and the stat. Rare, but it lasts until the next write. Counters are monotonic, so
VictoriaMetrics sees the increment late, not lost.

**Go contract (P2):** the P2 exit criterion compares expositions on recorded inputs (JE). A harness that writes the files and then scrapes once
cannot see any of this. A harness that replays a **sequence** of scrapes interleaved with hook-log writes would see Go differ if Go watched both
files. Owner item **OD-39 (new):** *Recommend:* an approved failure-mode deviation. Go records the byte offset it actually consumed (up to the last
complete `\n`), not a second `stat`, and rebuilds when **either** file changes (size or mtime). Single-scrape expositions are unchanged. The parity
harness scrapes only after quiescence and lists this BC as the reason. Alternative: reproduce exactly (watch the ledger size only, second stat).

Index row: `BC-EX-027 | Rebuild trigger: ledger size only; post-read stat; hook-log-only changes and in-gap appends lag | internal/ledger | P2 | OD-39 | OD-29 | H | r5 | new r5`.

### 3.2 BC-PX-046 (new; carries pass-2 r6 §1 into the BC catalogue): flows ended outside the response path

**Source:** `dgx_proxy.py:311-323` (the `error` hook); `claude-dgx:75,97,104`; mitmproxy 12.3.1 `options:241-246` (`tcp_timeout`, default 600),
`proxy/server:344-354` (`on_timeout` cancels the client handler: "Closing connection due to inactivity"), `proxy/server:290-308` (a cancelled
connection still emits `ConnectionClosed`), `tools/main:126-133` (handlers for SIGINT and SIGTERM only). I re-read these lines this round. The
remaining steps of the chain are P2r6 §1.2-1.3 (MEDIUM, static).

| Cause | What legacy writes | Client sees | Status |
|---|---|---|---|
| **Inactivity cut:** the tunnel carries no bytes either way for 600 s (`tcp_timeout`; neither the launcher nor a `config.yaml` sets it) | `error` hook → `dgx_upstream_error` or `anthropic_upstream_error`, `error: "Client disconnected."` (indistinguishable from a user cancel) | connection closed | MEDIUM static. **Not observed in production:** the 4 DGX `Client disconnected.` events came 0, 342, 0 and 181 s after the session's latest request (orchestrator, 2026-11-14) |
| **SIGTERM / SIGINT** (the launcher's `kill` from its `EXIT INT TERM` trap) with flows in flight | `error` hook runs for each in-flight `/v1/messages*` flow → `*_upstream_error` (cancel texts) | — (client exiting) | MEDIUM static (P2r6 §1.2; the CPython `asyncio.run` cancel step was not source-read) |
| **SIGHUP** (window/pane closed, not trapped, no mitmdump handler) or SIGKILL | nothing: the request has no terminal event | — | MEDIUM static |

**Contracts for Go (P3):** (1) The proxy's in-flight ceiling must be at least the client's API timeout (`API_TIMEOUT_MS=1800000`, `claude-dgx:104`),
configurable (D15). Idle-between-requests timeouts stay separate (HY-TIMEOUT-1, **OD-37**). (2) Exit semantics: handle SIGHUP like SIGTERM (Windows:
console close via `internal/platform`), drain for a bounded deadline, then write one error event per remaining flow (**OD-38**). Event names stay
unchanged (D7). Texts follow OD-28. (3) Reader rule, unchanged: never assume a request has a terminal event (OD-25).

Index row: `BC-PX-046 | Flows ended outside response(): 600 s inactivity cut, SIGTERM, SIGHUP/SIGKILL | internal/proxy | P3 | OD-37 | OD-38, OD-16, OD-28 | M | r5 | new r5, carried from P2r6 §1`.

---

## 4. Target D: pass-2 r6 folded in

| P2r6 item | Pass-3 effect |
|---|---|
| §1.1-1.2 shutdown path (SIGTERM → `error` hook; SIGHUP/SIGKILL → orphan) | **V-3 re-scoped.** The orchestrator's ledger evidence settles the 36 unpaired DGX requests: all are dated **2026-11-11** (per-day request vs reply+error: 11-10 282/282, 11-11 4265/4229, 11-12 85/85, 11-13 108/108, 11-14 15/15). That fits P2r6 O-1: they predate the `error` hook, which was added after that day's incident (`:312-315` docstring). Shutdown is not the explanation. V-3 no longer decides the replay's "orphaned by proxy exit" class. It remains a rig check that SIGTERM fires the `error` hook (verifies BC-PX-046 row 2 and informs OD-38). Replay rule: classify ledgers from before the hook existed as "pre-error-hook era" and exclude their missing terminal events from pairing diffs |
| §1.3 F-2 inactivity cut | **BC-PX-046** row 1; OD-37. BC-PX-044's cause table gains the inactivity and shutdown rows (same `Client disconnected.` text) |
| §2 CONV-ABS-14 mirror case | BC-PX-020/024 refined (§2.4) |
| §2 F-1 refinements (partial headers stall too; HTTP/1.0 rules out keep-alive; backlog 5; `state_lock` vestigial) | BC-EX-026 detail; no parity change (OD-33) |
| §4 mechanical entity diff: 0 new entities, events, env inputs | Agrees with this round's diff: no new ledger event, no new env input. BC-EX-027 is a behavior inside a known entity (exporter process lifecycle) |
| OD renumbering (orchestrator) | OD-35/OD-36 keep pass-3 r4's meanings. P2r6's two items are **OD-37/OD-38**. This file uses that numbering |

---

## 5. Target C: index re-check

### 5.1 Twenty random rows (seed **20261114**, `random.sample` over the 227 rows of P3r4 §7.3, CPython 3.11.7)

| Row | Component / package | Parity | Cited lines checked | Verdict |
|---|---|---|---|---|
| BC-BF-002 | backfill, `cmd/hylo (cost backfill)` | OD-36 | `:77,81`: `max(out, key=out.get)` over `{"dgx", "anth"}` in that order. Pinned: 0/0 → `dgx`, 5/5 → `dgx` | correct |
| BC-BF-005 | backfill | OD-36 | `:110-117`: summary print, then `makedirs`/`mkstemp`/`fdopen`/`json.dump`/`os.replace` (AST) | correct |
| BC-BF-006 | backfill | OD-36 | `:38-52`: falsy `timestamp` → `continue` before `last`; `ts()` uses `fromisoformat(s.replace("Z", "+00:00"))` | correct |
| BC-EX-003 | exporter, `internal/ledger` | JE | `:280-287` | correct but **incomplete** → BC-EX-027 (this round) |
| BC-HK-016 | hook | JE | `:169-181` (re-read in full) | correct |
| BC-HK-022 | hook | OD-12 | `:128-138` returns `(p, t)` with `t` from the last attempt; `:250` `f"{secs:.2f}"` with `None` → TypeError (H-04) | correct |
| BC-LN-004 | launcher | D14 | `:70-81`; D14 (PLAN §10) is exactly "`HTTPS_PROXY`/`NODE_EXTRA_CA_CERTS` … not to the commands it spawns", which legacy does export to the whole environment | correct |
| BC-PX-005 | proxy | BX + D13 (non-POST) | `:131,166`; prefix test is method-agnostic (`:103`); D13 rewrites only `POST /v1/messages` | correct |
| BC-PX-008 | proxy | BX | `:143-150` | correct |
| BC-PX-010 | proxy | OD-07 (+OD-06) | `:161-167`; client credentials are not stripped (OD-07); `_key()` raises after the host switch (P-R4, OD-06) | correct |
| BC-PX-021 | proxy | BX + OD-18 | `:283-300`: `[:600]`, `old[:-19]`, `< 50_000_000`, `return` | correct |
| BC-PX-025 | proxy | BX | `:326-336` | correct |
| BC-PX-027 | proxy | BX | `:528-536`: `_ws_started` is never set, so `ws_closed` is never written | correct |
| BC-PX-039 | proxy | OD-16 | `:311-323` | correct |
| BC-SL-007 | status line | BX | `:440,450` (now `model_name` at `:440`, used at `:450`); the broad row's `:442,453` and r1's `:441-443,453` are **off by 1-3 lines** | content correct; line cite drift (NITPICK) |
| BC-SL-017 | status line | BX | `:523-530`; pinned 1.15·7d shown, 1.16·7d hidden | correct |
| BC-SL-034 | status line | BX | `:1033-1034,1096-1103,1153` | correct |
| BC-SL-040 | status line | BX | `:158-187` | correct |
| BC-SL-061 | status line | BX | `:517-519`; pinned `1.0 - 0.9 = 0.09999999999999998 < 0.10` | correct |
| BC-SL-062 | status line | BX | `:863-873`; pinned `999.5→1000`, `2500→2k`, `999500→1000k`, `1049999→1.0M`, `1050000→1.1M`, `None→?`, `True→1` | correct |

Result: 20 of 20 correct on component, Go package, phase and parity status. One is incomplete (BC-EX-003, fixed by BC-EX-027) and one has a line-cite
drift of 1-3 lines (BC-SL-007). No row is wrong.

### 5.2 The "decision-log text out of scope" call (BC-PX-003 note, BC-PX-022, BC-PX-029)

Exact wording relied on, `docs/PLAN.md` §7, P3 row, exit criterion: **"Recorded-request replay: identical routing decisions, rewritten bodies and
ledger lines vs the Python addon; then a shadow week: one real window on hylo, the rest on Python, ledger diff clean"**. Also §10 D7 keeps "the ledger
format and metric names" unchanged. Neither names the decision log.

**Confirmed, with one caveat.** The criterion lists three comparands, and the decision-log file is not one of them by name. But the legacy file **is
named** "routing decisions" (`DECISION_LOG` default `~/dgx-llm-routing-decisions.log`, env `DGX_PROXY_DECISIONS`, `:53`). So "identical routing
decisions" can be read as "the same decision-log lines". The lines split into two kinds:

- **Decision lines**, one per routed request: `-> anthropic (%s)` (`:135`), `-> anthropic (%s declares a server tool)` (`:140`), `-> DGX (%s)` (`:167`),
  and `unparseable /v1/messages body, passing through to anthropic` (`:108`). Each states only the lane choice, which the replay already compares
  through the ledger's `lane` / event name and the outgoing request (host, rewritten body).
- **Diagnostic lines:** tap summary (`:240`), DGX error body and saved request (`:286,297`), DGX reply stop reason (`:309`), upstream error (`:321`),
  unknown block type (`:510`), module loaded (`:518`).

Reading used here: "routing decisions" means the per-request lane decision, which is compared as data. The log **text** stays OOS. Owner item
**OD-40 (new):** confirm that reading. *Recommend:* yes. Optionally, the replay also checks the decision lines **semantically** (one `-> <lane>
(<model>)` per routed request, with the same lane and model). That is cheap and removes the ambiguity. No parity status in the index changes unless
the owner rules otherwise.

---

## 6. Index delta (apply to P3r4 §7.3; all other rows unchanged)

| ID | Change |
|---|---|
| BC-EX-002 | Last → r5; flag "log_message no-op: nothing on stderr per request" |
| BC-EX-003 | Last → r5; flag "contract completed by BC-EX-027" |
| BC-EX-027 | **new** (§3.1) |
| BC-PX-020 | Last → r5; flag "direct-to-backend flows: dgx_reply with empty attribution (P2r6 mirror)" |
| BC-PX-024 | Last → r5; flag "dgx_upstream_error can also carry empty attribution (P2r6 mirror)" |
| BC-PX-044 | Last → r5; Also += OD-37; flag "cause table += inactivity cut and shutdown rows (BC-PX-046)" |
| BC-PX-046 | **new** (§3.2) |
| BC-SL-007 | flag "cited lines now :440,450" (cite drift only; Last unchanged) |

**Totals after this round: 229 BCs.**

| Component | BCs | BX | JE | OOS | Approved deviation | Pending OD (primary) |
|---|---|---|---|---|---|---|
| Status line (SL) | 103 | 97 | 0 | 0 | 4 | 2 |
| Proxy (PX) | 46 | 37 | 0 | 3 | 1 | 5 (+OD-37) |
| Exporter (EX) | 27 | 0 | 16 | 1 | 0 | 10 (+OD-39) |
| Stop hook (HK) | 23 | 3 | 18 | 0 | 0 | 2 |
| Launcher (LN) | 11 | 0 | 8 | 2 | 1 | 0 |
| Coordinator (CO) | 2 | 0 | 0 | 2 | 0 | 0 |
| Preflight (PF) | 2 | 0 | 2 | 0 | 0 | 0 |
| Backfill (BF) | 13 | 0 | 0 | 0 | 0 | 13 |
| Services (SV) | 2 | 0 | 0 | 2 | 0 | 0 |
| **Total** | **229** | **137** | **44** | **10** | **6** | **32** |

By phase: P1 103, P2 29, P3 45, P4 39, unscheduled 13. By last round: B 80, r1 86, r2 25, r3 20, r4 11, r5 7.

Owner items: OD-01..OD-40. Ruled: OD-24, OD-27. Pending: 38. New this round: OD-39 (exporter trigger), OD-40 (meaning of "routing decisions"). The
renumbered P2r6 items are OD-37 and OD-38.

RET crosswalk (P3r4 §6): unchanged by this round. Add **RET-13 = P2-CONV-ABS-20** (P2r6: trap-SIGTERM does not orphan in-flight flows). Numbers 16-19
were never used. 21 and up are free.

---

## Owner checks carried forward (after the soak; not attempted)

1. Grafana per-session panel with at least 2 recent sessions (VictoriaMetrics ingesting the non-contiguous `dgx_llm_session_*` fragments,
   BC-EX-025). Optionally `promtool check metrics` offline on one saved scrape body.
2. VictoriaMetrics NaN capture: one `/api/v1/query` response for the exact `QUERY` on an idle box, under light load, and with fewer than 20 TTFT
   samples (CP-N01/N02 reachability).

## Delta Summary

- **Target A (re-verification):** all three of round 4's spec changes **confirmed** with new fixtures. Raw-JSON `cur.out` (C4: native Go holds
  `"abc"`); `finishTurn` tests `t0` first (C5: no crash); the amended OD-32 condition (C4: the original rule gives 900, the amended rule and native Go
  give `"abc"`; C1-C3: turn state converges, conv residual +1). CONV-ABS-15 and BC-SL-103 stand. **No retraction.**
- **Target B (mechanical diff):** 283 items (Python 89 functions, 118 write/effect sites, 50 handlers = 257; shell 26). Python: 202 cited, 53
  assigned to existing BCs on reading, **2 uncovered** (`_current_size` and its handler), plus one gap in a cited region (`:281-287`). Together these
  give **BC-EX-027**. Shell: 21 covered, 5 out of scope (D6 visible mode, including the router port probe that also runs in invisible mode).
- **Target C (index):** seed 20261114, 20 of 20 rows correct on component, package, phase and parity status. BC-EX-003 is incomplete (now completed)
  and BC-SL-007's cite drifts 1-3 lines. The OOS call on decision-log text is confirmed against the exact P3 wording, with an ambiguity flagged
  (the log is *named* "routing decisions") → OD-40.
- **Target D (pass-2 r6):** BC-PX-046 (inactivity cut, SIGTERM, SIGHUP/SIGKILL); V-3 re-scoped (the 36 orphans are all from 2026-11-11, before the
  error hook; shutdown is not the cause); BC-PX-020/024 mirror-case refinement; BC-EX-026 detail; OD-37/OD-38 numbering adopted.
- **New BCs (2):** BC-EX-027 (found by this pass), BC-PX-046 (carried from P2r6). **Refined (5):** BC-EX-002, BC-EX-003, BC-PX-020, BC-PX-024,
  BC-PX-044. **Index:** 229.
- **New owner items:** OD-39, OD-40.

## Remaining Gaps (verbatim-carryable)

1. Owner checks after the soak (carried, not attempted): the Grafana per-session panel with at least 2 sessions; optionally `promtool check metrics`
   offline on a saved scrape; the VictoriaMetrics NaN capture.
2. P3 replay verification items, each needing a stub-backend rig, not the live proxies: V-1 (Host header bytes), V-2 (mitmproxy 502 page bytes on
   connect failure and `server closed connection`), V-3 re-scoped (SIGTERM mid-stream fires the `error` hook; inform OD-38). Optional: a 600 s
   silent-backend run to confirm BC-PX-046 row 1 directly.
3. Owner decisions: 38 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-40), including the new OD-39 (exporter trigger) and OD-40 (meaning of
   "routing decisions").
4. Not verifiable from authorized sources (LOW): which of two conflicting duplicate session samples VictoriaMetrics keeps (BC-EX-025); whether vLLM
   streams any byte before the first token (decides whether BC-PX-046 row 1 can hit streamed DGX requests).
5. Suggested scope for round 6: re-verify BC-EX-027 with new fixtures, and run the same "cited region, missing contract" reading over the remaining
   cited regions not re-read this round: `dgx_statusline.py:420-437,456-495,533-637` (row-1 renderers) and `dgx_ledger_exporter.py:150-195,300-396`
   (accumulation and exposition body). This round re-read every other region of the six Python files.

## Novelty Assessment

Novelty: SUBSTANTIVE

Most of this round is confirmation. Round 4's item re-verified with no retraction. The diff assigned 255 of 257 Python items and all 26 shell items
to existing BCs or to explicit out-of-scope rulings. The 20-row index sample is clean, and the pass-2 r6 fold-in carries a pass-2 discovery
(BC-PX-046), which this pass counts as a refinement, as round 4 did for BC-EX-026.

One finding fails the convergence test as the orchestrator stated it ("any uncovered behavior-bearing code is SUBSTANTIVE"). **BC-EX-027:** the
exporter's rebuild trigger watches only the ledger size and takes `processed_size` from a second `stat` after the read. Two pinned consequences follow:
a hook-log-only change never refreshes the fake-stop tallies, and an append in the gap is never parsed until the ledger next changes. No prior pass of
either kind states this (searched: "race", `_current_size`, "processed_size", hook-log trigger). It changes the Go exporter's spec, because Go must
choose and document a trigger, and the P2 harness must scrape only after quiescence. That adds OD-39. It is narrow: one function plus the three
lines around it, and only scrape timing is affected, not single-scrape exposition bytes. It also shows that "cited by a BC" is not "covered", which
is why gap 5 proposes the same reading for the regions not re-read.

## Convergence Declaration

Another round needed: BC-EX-027 is an uncovered behavior found by this round's diff. The next round should re-verify it and finish the
cited-region reading listed in gap 5.

## State Checkpoint

```yaml
pass: 3
round: 5
status: complete
files_scanned: all 6 legacy .py files AST-walked (257 items) and mostly re-read; claude-dgx and dgx-proxy-coordinator.sh grep-structured (26 items); pass-3 B, r1-r4; pass-2 r5, r6; docs/PLAN.md §7, §10; mitmproxy 12.3.1 options, proxy/server, tools/main (citations only)
timestamp: 2026-11-14T07:18:16Z
novelty: SUBSTANTIVE
new_bcs: {EX: 1 (BC-EX-027), PX: 1 (BC-PX-046, carried from P2r6)}
refined_bcs: 5
retractions: []
diff: {items: 283, python: 257, shell: 26, cited: 202, assigned_on_reading: 53, shell_covered: 21, shell_oos_D6: 5, uncovered: 2 + 1 cited-region gap -> BC-EX-027}
index_sample: {seed: 20261114, rows: 20, correct: 20, incomplete: 1 (BC-EX-003), cite_drift: 1 (BC-SL-007)}
bc_index_total: 229
owner_decisions: 40 (OD-01..OD-40; 38 pending, 2 ruled)
new_owner_items: [OD-39, OD-40]
od_renumbering_applied: {P2r6 OD-35: OD-37, P2r6 OD-36: OD-38}
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r5/
next: pass 3 round 6 (carry "Remaining Gaps" verbatim)
```
