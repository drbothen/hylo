# Pass 4 Deepening — Round 3: verification, consolidated threshold and NFR catalogues — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/`, read-only and static. Nothing in `legacy/` was imported, executed or modified. No proxy, nothing
  networked. CLAUDE.local.md was not read.
- Authorized read-only references (same as round 2): mitmproxy 12.3.1 (`m/` = the venv's `site-packages/mitmproxy/`, `version.py:5` `"12.3.1"`);
  `man launchd.plist`, `man ssh_config`; CPython stdlib 3.11 (`py311/`) and 3.9 (`py39/`).
- One scratch script: `anchors.py` prints the cited line of every threshold row (it reads legacy files as text; nothing is imported). Output
  `anchors.out`, 208 lines. Also a text dump of `man launchd.plist`. Both are in
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r3/`.
- Inputs read: pass-4 broad, deep r1, deep r2; pass-1 deep r2 (§A.1, §B.3, OD-66) and **r3** (converged during this round: §B rows C2a, signals,
  script loader, upstream concurrency; §C row 8); pass-5 deep r1 (§A ENV-01..43) and **r2** (§C.1 rules, §C.2 K-1..K-9, §C.3 table). Pass-5 r2
  arrived late in this round; §D.2a aligns the catalogue with it. `docs/STATUSLINE-WIDGETS.md` and `docs/STATUSLINE-REVIEW-2026-11-13.md` (row 9)
  were also read.
- Numbering: retractions **CONV-ABS-73, 74** (75, 76 unused). **No new owner items** (OD-82..OD-85 unused). Sibling files were not edited.
- Orchestrator mid-round item (pass-1 r3 §C row 8): terminal close → SIGHUP. Verified and added as **R-12** (§B.2).

Abbreviations as in rounds 1-2: `SL` status line, `PX` proxy, `EX` exporter, `HK` hook, `PF` preflight, `BF` backfill, `L` launcher, `CO`
coordinator, `pl-tu` tunnel plist. Rationale codes: **M** measured, **DOC** written in source or docs, **J** labeled judgment call, **C**
convention or tool default, **Dv** derived (structural, no sign-off needed), **Dv†** derived by these passes (owner bulk-confirms), **OWNER**
(owner supplies), **N/A** (dead, dropped or an absent limit), **EXT** (a Claude Code constant). The D15 class codes are defined in §C.1.

---

## A. Verification of round 2's claims (fresh evidence)

### A.1 Verification table

| # | Round-2 claim | Fresh evidence (this round) | Verdict |
|---|---|---|---|
| 1 | **CONV-ABS-61**: the T-121 router-port scan is live in invisible mode and exits 1 when 4141..4199 are all busy | `L:17-22` comes before the mode split at `L:70` and is unconditional except for `ROUTER_PORT` (`L:17-18`). The loop increments past 4199 → `exit 1` (`L:21`), so 59 busy ports means 59 `nc` probes and then a failed launch. `PORT` is used only at `L:102` (visible branch). `is_router` (`curl -m 2`, `L:85`) is called only in the `elif` at `L:88`, and the router wait at `L:94` is inside it | **confirmed** |
| 2 | **CONV-ABS-62**: a failed `ps` walk is not cached and reruns on every refresh; the worst case is 6 × 1 s, longer than the 4 s tick | `proc_start` is written only on success (`SL:285-289`); empty output, `pid <= 1` and exceptions all return None without writing (`SL:282-283,291-294`); `SL:1229` calls the walk on every run that has a `session_id`, whether or not `⌂` is shown (`⌂` needs the timer, `SL:540,557`). **Refinement:** a `ps` that hits its 1 s limit raises `TimeoutExpired`, which `SL:293` catches, ending the walk. So 6 s needs six calls that each finish just under 1 s (or five slow calls and then a timeout). The usual failure (no `claude` ancestor) costs a few short `ps` spawns per refresh before `pid <= 1` | **confirmed + refinement** |
| 3 | **CONV-ABS-63**: the Kev timeout is per socket operation; no bound with a dribbling server; no early stop after a failure | py311 `urllib/request.py:1317` / py39 `:1315` pass `timeout` to `HTTPConnection`; `connect()` → `_create_connection((host,port), self.timeout, …)` (py311 `http/client.py:949-953`, py39 `:921-924`); `create_connection` calls `settimeout` then `connect` per address (py311 `socket.py:827-836`, py39 `:822-831`); body reads go through `self.fp.read(amt)` (py311 `http/client.py:638`), with each underlying `recv` bounded separately. A failure returns `(None, None)` (`HK:119-121`), so `t is not None` (`HK:133`) is false after it. 15 s holds only if each phase (connect, response head, body) waits once; with dribbling there is no bound below Claude Code's 30 s kill. **Wording retraction (CONV-ABS-73):** r2's "typical failure ≈ 2.5 s per call" is unsupported. A refused connect fails within milliseconds; 2.5 s is only the unanswered-connect (black-hole) case | **confirmed; one phrase retracted** |
| 4 | **CONV-ABS-64**: T-039's `>=` is observable at `api == 60000` | `SL:540` `dur > 60000` gates the block; `SL:551` `api >= 60000` → `·1m` (`_hm`, `SL:546`). Integer inputs make `api == 60000` with `dur > 60000` reachable | **confirmed** |
| 5 | **R-10** pre-trap orphan window | mitmdump starts at `L:75`; the trap is armed at `L:97`; `exit 1` at `L:78` (readiness failure after 40 × 0.25 s, `L:77`) runs with no trap set. Ctrl-C narrowing: `m/tools/main.py:128-129` installs SIGINT/SIGTERM handlers before `master.run()` (`:140`). **Wording fix:** r2's "visible mode's router failure (`L:95`) does the same" orphans the **router** started at `L:92`, not mitmdump, which visible mode never starts | **confirmed + wording** |
| 6 | **R-11** abort on a busy router range in invisible mode | as row 1 | **confirmed** |
| 7 | Leaf validity 197 days; leaf reuses the CA key | `m/certs.py:41` `CERT_EXPIRY = 199 d`, `:44` `CERT_VALIDITY_OFFSET = −2 d`, `:430-431` → valid from now − 2 d to now + **197 d** (the **span** is still 199 d). `:427` `builder.public_key(cacert.public_key())`; `:493` signs SHA-256 with `privkey`, which the docstring calls the "CA private key" (`:413`); the caller passes `self.default_privatekey` for both the signature and the entry key (`:803-811`). CA: `:340-341`, 3,650 d from now − 2 d; `KEY_SIZE = 2048` (`m/options.py:9`, option at `:226-233`) | **confirmed**. Wording: "valid 199 d, back-dated 2 d (197 d forward)". New: §B.1 T-136 (leaf cache) |
| 8 | launchd throttle = minimum interval between spawns, 10 s | `man launchd.plist` ThrottleInterval: "by default, jobs will not be spawned more than once every 10 seconds" (dump l.316-319); KeepAlive: "Jobs that exit quickly and frequently … will be throttled" (l.194-196). Neither plist sets `ThrottleInterval` (`pl-ex:1-13`, `pl-tu:1-18`). Documented behavior only: launchd was not exercised | **confirmed (documented)** |
| 9 | F-3 lower bound: the cap bites when point spacing < 90/32 = 2.8125 s, including TTL < 2 s | Points need `now − hist[-1].t ≥ 2` (`SL:337`) and a fetch (`SL:324`, `fetch_ts > now − TTL` reuses), and ages must stay < 90 (`SL:336`). With spacing s, the points kept number ⌈90/s⌉, which exceeds 32 iff s < 2.8125. **Clarification:** at the default TTL of 4 s, fetches are ≥ 4 s apart **whatever the trigger rate**. The "bursts" sentence in round 2 applies only to TTL < 2.8125 s. The returned list is uncapped (`SL:352`), but only the saved list is capped (`SL:350`), and the plot uses `[-12:]`, so the cap never changes output | **confirmed + clarification** |
| 10 | DNS outside every timeout | `getaddrinfo` (py311 `socket.py:827`, py39 `:822`) runs before any `settimeout`. Defaults are IP literals (`SL:73`, `HK:31`, `PF:18`), so DNS applies only to a configured host name. **Extension:** the preflight `socket.create_connection((host, port), timeout=4)` (`PF:23`) has the same exposure: unbounded DNS and N × 4 s across N addresses | **confirmed + extension** |
| 11 | Key renames H-1..H-8 | §D.1 | **confirmed**; H-5/H-6 get an operator note |
| 12 | r2 §C.2: "the windows `[1m]`, `[30m]` at `SL:103`" | `SL:102-103` is the start of the `QUERY` literal. The windows are at **`SL:118`** (`[1m]`) and **`SL:121`** (`[30m]`), as the broad pass had them. Also r1 T-113 `SL:135` is a blank line; `SPARK = "▁▂▃▄▅▆▇█"` is at **`SL:136`** | **citation retraction (CONV-ABS-74)** |
| 13 | Remaining gap 2: T-078 "Prometheus exporter ports 9100-9999" | No network this round. Recorded as **C, unverified**: the usual source is the Prometheus project's "default port allocations" wiki page, which allocates exporter ports from 9100 upward. Only the rationale label depends on it; behavior does not | **gap closed as unverified convention** |
| 14 | Remaining gap 3 (pass-5 should record per-operation timeouts, unbounded DNS, `subprocess.run` total deadline) | pass-5 r2 not yet written. Carried | open (sibling) |
| 15 | Remaining gap 4 (table tests for the `SL:674` clamp and the `cols > 0` trim) | P1 test-plan note; no catalogue change | carried as a design note |

**Anchor re-check of the whole catalogue.** `anchors.py` printed the cited line(s) of all 121 source-anchored rows (T-001..T-121). Every value and
operator matches the catalogue. The only wrong anchors are the two in row 12. The operators recorded in §C come from these printed lines.

### A.2 Retractions this round

| Marker | Claim | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-73** | r2 §E P-6: "typical failure ≈ 2.5 s per call (7.5 s total)" | Per-call failure cost ranges from milliseconds (connection refused, fast `EHOSTUNREACH`) to 2.5 s (connect never answered). No "typical" figure is supported. The bounds stand: 15 s without dribbling, unbounded with it | py311 `socket.py:827-836`; `HK:110-121` |
| **CONV-ABS-74** | r2 §C.2 places T-016/T-017's windows at `SL:103`; r1 places T-113's glyph string at `SL:135` | `SL:118`, `SL:121`; `SL:136` | `anchors.out` |

---

## B. New findings

### B.1 Three implicit thresholds missing from the catalogue (mitmproxy 12.3.1 defaults)

| # | Value | Meaning | Source | Effect in legacy | hylo |
|---|---|---|---|---|---|
| **T-136** | **100 leaves**, FIFO | in-memory leaf certificate cache: each minted leaf is stored by `(cn, sans)`, and the oldest is evicted after 100. A cached leaf is **never re-checked for expiry** | `m/certs.py:541` `STORE_CAP = 100`; `:576-580` `expire()`; `:815-816` store and enqueue | not binding: 85 upstream hosts observed across all windows (P2r8 §0), and each window has its own process. A process alive longer than 197 days would serve expired cached leaves (moot per window) | `internal/ca` leaf cache: size is an implementation choice (NC). PLAN §6's long-lived shared proxy **must re-mint before `not_after`**, so attach to **OD-50** (lifecycle). No new OD |
| **T-137** | **5** | concurrent upstream connections per upstream address **per client connection** (`asyncio.Semaphore(5)`) | `m/proxy/server.py:109` (created per `ConnectionHandler`), `:206` `async with self.max_conns[command.connection.address]` | not binding for Claude Code's HTTP/1.1 tunnels (one request at a time per client connection); it could queue a child tool's multiplexed h2 client that fans out to an h1 upstream. Pass-1 r3 lists it (C2a, "Upstream concurrency") | N/A: hylo's Go transport sets its own limits (HY-PROTO-1 keeps h1↔h1). Recorded so the parity harness does not expect queueing |
| **T-138** | **1 s** | addon script live-reload poll (`reload=True`) | `m/addons/script.py:74` `ReloadInterval = 1`, `:150` `asyncio.sleep(ReloadInterval)` | an edit to `dgx_proxy.py` reaches every running window within about 1 s (CLAUDE.local-free fact: pass-1 r3 "Script loader", OD-26) | DROP: hylo is a compiled binary; config reload is a separate design (OD-50 upgrade path) |

Rationale for all three: **C** (tool default). These are the same kind of row as T-122..T-128, so the catalogue was incomplete without them.

### B.2 New reliability NFR R-12: terminal close kills the proxy without draining

- **Evidence.** The launcher trap covers `EXIT INT TERM` only (`L:97`). mitmproxy 12.3.1 has **0** references to `SIGHUP` (package-wide search, this
  round and pass-1 r3 V7). Its only handlers are SIGINT and SIGTERM (`m/tools/main.py:128-129`, Windows fallback `:132-133`), and it ignores SIGPIPE
  (`:137-138`). `utils/debug.py:130-131` (SIGUSR1/2) is a debug aid. CPython installs a handler only for SIGINT at startup, so SIGHUP keeps its
  default action and terminates the process.
- **Behavior.** When a terminal window closes, mitmdump (in the launcher's process group, pass-1 r3 I-23) dies immediately. `master.shutdown` never
  runs, nothing drains, no `error` hook fires, and **no ledger line is written for in-flight flows**. Compare the trap path: SIGTERM →
  `master.shutdown`, which gives in-flight flows `error` lines (pass-1 r3 §B.2 step 8).
- **Confidence.** The handler set is HIGH (source). Delivery of SIGHUP to mitmdump on terminal close is MEDIUM, because it rests on tty/shell hangup
  semantics that no authorized source covers (pass-1 r3 V7).
- **Legacy impact.** Low: Claude Code in that window dies too, so the only loss is ledger completeness for the requests in flight (D7 surface:
  missing `*_reply`/`*_usage`/`*_upstream_error` lines).
- **hylo implication.** PLAN §6's shared proxy must survive any one window closing. OD-66 (a), a detached `hylo proxy` in a new session or process
  group with no controlling terminal, removes the tty SIGHUP path. Stop and drain then follow OD-50 (lifecycle) and OD-38 (drain on shutdown). A
  detached proxy should also give SIGHUP an explicit meaning (ignore it, or reload) rather than inherit "terminate". This is a design default under
  OD-66, not a new OD.
- Cited with R-10 (pre-trap orphan window): both describe how the proxy's life is coupled to its window.

### B.3 Rationale-status corrections

- **T-088** (`t > KEV_TIMEOUT / 2`, `HK:133`): the broad pass's "J: slow endpoint" is weaker than a labeled judgment call. The comment at `HK:134`
  explains *why there is* an early stop, not why the cut-off is half the timeout. Under the round-1 rule ("purpose documented, value not": T-010,
  T-065, T-066 went to OWNER), it needs owner sign-off. Because a qualitative label exists, it joins the **bulk-confirm** list ("half the per-call
  timeout counts as slow; judgment") instead of the owner list.
- **T-040** (`⌂` margin 5 min): the broad pass said "5 min value J-unlabeled". The value is part of the owner's request: review row 9 revisit, "Owner
  request: window-open time `⌂` … shown when ≥ 5 min beyond elapsed"; WIDGETS Timer row. Upgraded to **DOC (owner decision recorded)**, the same
  status as T-020/T-021. It stays off the owner list.

---

## C. Consolidated final threshold catalogue (broad + r1 + r2 + r3)

### C.1 Conventions

- **Class:** **CFG** D15 config key, default = legacy value; **NC** named constant (D15 exception, with the reason in the Key column); **DROP** not
  carried into hylo; **OOS** legacy deployment, not a hylo key; **EXT** Claude Code constant; **NEW-H** hylo key with no legacy value (behavior
  deviation approved elsewhere); **N/A** absent from hylo by construction.
- **Op:** the comparison exactly as the source writes it. Parity (D4) requires it unchanged, and each key's comment states it.
- **Last:** the round that last changed the row: B (broad), R1, R2, R3.
- Key naming follows pass-5 §A and OD-01: `HYLO_` + upper snake case of the key (pending OD-01). Units use the legacy unit (`_s`, `_ms`, `_bytes`,
  `_chars`, `_pct`, `_w`).

### C.2 Status line (`internal/statusline`, P1)

| T | Value (op) | Site | Class | Rat. | Rationale | Key / NC reason | Last |
|---|---|---|---|---|---|---|---|
| 001 | 4 s (reuse while `fetch_ts > now−TTL`) | SL:74,324 | CFG | DOC | "match refreshInterval" (SL:50; WIDGETS Tunables) | `statusline.telemetry.ttl_s` | B |
| 002 | 2 | SL:75 | CFG | C | two-row design | `statusline.rows` | B |
| 003 | 15 s (`age > STALE_OK` → stale) | SL:79,697 | CFG | Dv† | one VM scrape interval (review #16.1); effective only when `ttl_s > 15` (F-1, OD-55) | `statusline.telemetry.fresh_s` | R1 |
| 004 | 300 s (`age < KEEP_DEAD`) | SL:80,357 | CFG | OWNER-A | ladder stated (SL:34-38), value not | `statusline.telemetry.keep_dead_s` | R1 |
| 005 | 1.5 s per socket op | SL:81,170 | CFG | Dv† | ≈ 60 × the measured ~25 ms RTT (SL:81); no-dribble bound 3 s < 4 s tick | `statusline.telemetry.timeout_s` (semantics OD-56) | R2 |
| 006 | 12 points | SL:82,664 | CFG | J | "kept short: long flats read as blobs" | `statusline.sparkline.points` | B |
| 007 | 90 s (`<`) | SL:83,336 | CFG | Dv† | gap pruning (F-4); review #17.2 "~48 s (doc said 90 s)" | `statusline.sparkline.max_age_s` | R2 |
| 008 | 2 s (`>=`) | SL:84,337 | CFG | Dv† | inert at TTL ≥ 2 (F-2) | `statusline.sparkline.min_gap_s` | R1 |
| 009 | 32 | SL:350 | CFG | Dv† | bounds the cache file; inert unless TTL < 2.8125 s (F-3, §A.1 row 9) | `statusline.sparkline.history_cap` | R3 |
| 010 | 1800 s | SL:85 | CFG | OWNER-A | purpose "no blinking", value not | `statusline.limits.keep_s` | R1 |
| 011 | 300 s (`>`) | SL:93,825 | CFG | J | labeled (SL:90-92; review #20.2) | `statusline.idle.after_s` | B |
| 012 | 30.4 MTok/month | SL:98 | CFG | DOC | 1M DGX tokens / 24 h (SL:94-97; review #11.1) | `statusline.cost.basis_min_mtok_month` | B |
| 013 | 5 s | SL:99 | CFG | C | "docs' example pattern" | `statusline.git.ttl_s` | B |
| 014 | 72 cols (`>=` keeps row 2) | SL:100,1224 | CFG | OWNER-B | none | `statusline.narrow_cols` | R1 |
| 015 | 20 | SL:124 | CFG | DOC | below 20 samples p95 = max (SL:124) | `statusline.ttft.min_samples` | B |
| 016 | `[1m]` | SL:118 | CFG | DOC | review #17 A+ (sparkline timescale) | inside `statusline.telemetry.query` (byte-identical default) | R3 |
| 017 | `[30m]` | SL:121 | CFG | DOC | matches `dgx_ttft:p95_30m` (review #18) | inside `statusline.telemetry.query` | R3 |
| 018 | 30 d | SL:218 | CFG | DOC | owner design (review #11 revisit) | `statusline.cost.window_s` | B |
| 019 | $1 (`>=`) | SL:219 | CFG | DOC | DGX p75 $0.13 from probes; "short checks, not work sessions" (SL:213) | `statusline.cost.min_usd` | B |
| 020 | 10 | SL:220 | CFG | DOC | owner decision (review #11 revisit) | `statusline.cost.min_sessions` | B |
| 021 | $25 | SL:221 | CFG | DOC | owner decision (review #11 revisit) | `statusline.cost.cold_yellow_usd` | B |
| 022 | 60 s (`<` skips) | SL:232 | CFG | Dv† | 1 write per 15 refreshes; WIDGETS "repaired by the next minute's write" | `statusline.cost.record_throttle_s` | R1 |
| 023 | 300,000 / 1,800,000 ms | SL:253 | CFG | DOC | "same as the display" / "approximate spans" (SL:214-215) | `statusline.cost.rate_min_api_ms` = `{cc, other}` (H-2) | R2 |
| 024 | p75/p95; index `int(q·(n−1))` | SL:261 | CFG+NC | DOC+C | owner design; "lower" nearest rank, no interpolation | `statusline.cost.percentiles`; index method NC (parity) | R1 |
| 025 | 6 levels | SL:279 | CFG | Dv† | expected depth 2 (SL:269-270) plus margin | `statusline.window_age.max_depth` | R1 |
| 026 | 1 s per `ps` call (total deadline) | SL:281 | CFG | OWNER-G | walk uncached on failure; ≤ 6 s per refresh (CONV-ABS-62) | `statusline.window_age.ps_timeout_s` | R3 |
| 027 | 10 cells, half-up | SL:426 | CFG+NC | DOC | review #5.2 | `statusline.context.cells`; rounding NC | B |
| 028 | 50 (`>`) / 85 (`>=`) | SL:434 | CFG | DOC | review #5.1; SL:430-433 | `statusline.context.plain_max` / `red_from` | B |
| 029 | 1e6 (`>=`) else K | SL:435-436 | CFG | C | SI units | `statusline.units.context` | B |
| 030 | hue 0.22, s 0.85, v 0.80 | SL:146-147 | CFG | OWNER-B | aesthetic | `statusline.theme.heat` | R1 |
| 031 | 5 h / 7 d | SL:501 | CFG | C | Anthropic window definitions | `statusline.limits.windows` | B |
| 032 | `0.10 <= elapsed <= 1.0` | SL:517 | CFG | DOC | "projection is noise" early (review #12 revisit) | `statusline.limits.projection_min_elapsed` | B |
| 033 | `>100` red, `>=80` yellow | SL:519 | CFG | DOC | review #12 revisit | `statusline.limits.projected_bands` | B |
| 034 | `>90` red, `>70` yellow | SL:521 | CFG | DOC | 70 = pace, 90 = throttling imminent (review #12.3) | `statusline.limits.absolute_bands` | B |
| 035 | `rem <= 1.15 × window` | SL:523 | CFG | OWNER-A | none | `statusline.limits.countdown_max_factor` | R1 |
| 036 | 86400 / 3600 / 60 s | SL:524-529 | NC | C | calendar units | NC: a day is a day | B |
| 037 | 10,000 / 1e6 (`>=`) | SL:856-859 | CFG | DOC | keep row 1 narrow (review #8.1) | `statusline.units.lines` | B |
| 038 | `> 60000` ms | SL:540 | CFG | Dv† | `_hm` has minute granularity (SL:546) | `statusline.timer.min_ms` | R1 |
| 039 | `>= 60000` ms | SL:551 | CFG | Dv | as T-038; `>=` is observable at `api == 60000`, keep it (D4) | `statusline.timer.api_min_ms` | R2 |
| 040 | `>= 300000` ms | SL:559 | CFG | DOC | owner request (review row 9 revisit; WIDGETS Timer) | `statusline.window_age.min_margin_ms` | R3 |
| 041 | 1440 min (`>=`) | SL:561,828 | NC | C | calendar | NC | B |
| 042 | 1000 / 1e6 (`>=`) | SL:869-873 | CFG | DOC | approved mockup (review #10 revisit) | `statusline.units.tokens` | B |
| 043 | `>= 300000` ms | SL:622 | CFG | DOC | "below that the ratio is noise" | `statusline.cost.burn_min_api_ms` | B |
| 044 | `>= 0.005` | SL:634 | CFG | DOC | "skip sub-half-cent noise" | `statusline.cost.basis_min_shown_usd` | B |
| 045 | k fixed 1.0; floors v 1.0, f 0.1 | SL:648-649 | CFG | DOC | review #17.1 | `statusline.sparkline.scale` (1e-9 fallback = T-114) | R1 |
| 046 | fade 0.55→1.0; RGB (70,170,190), (220,170,60), (140,235,255) | SL:680-689 | CFG | OWNER-B | aesthetic | `statusline.sparkline.colors` | R1 |
| 047 | `q > 0` or preempt `> 0` | SL:740 | CFG | DOC | review #14 | `statusline.queue.yellow` = `{waiting_gt: 0, preempt_rate_gt: 0}` (H-1) | R2 |
| 048 | `ceil(kv/25)`, 4 cells | SL:759 | CFG+NC | DOC | review #15 | `statusline.kv.cells`; ceiling rule NC | B |
| 049 | `> 5` % | SL:760 | CFG | DOC (M, external) | THRESHOLDS §8b; re-validate under LMCache (review #15.3) | `statusline.kv.host_yellow_pct` | B |
| 050 | `> 0.5` % | SL:763 | CFG | Dv† | the share prints `.0f`, so ≤ 0.5 would print 0% | `statusline.kv.host_shown_pct` | R1 |
| 051 | `>= 10` s | SL:795 | CFG | DOC | buckets 20/40/80 (review #18.2) | `statusline.ttft.integer_from_s` | B |
| 052 | `> 8` s | SL:799 | CFG | DOC (M, external) | THRESHOLDS §8b | `statusline.ttft.yellow_s` | B |
| 053 | `> 1520` / `> 1280` W | SL:812 | CFG | DOC | 95 % / 80 % of the 1,600 W rating | `statusline.power.wall_red_w` / `wall_yellow_w` (keep literals) | B |
| 054 | 524,288 B read **step** | SL:952,1044-1052 | CFG | OWNER-C | a step, not a cap (CONV-ABS-43) | `statusline.transcript.read_cap_bytes` | R1 |
| 055 | 200 tokens | SL:967 | CFG | DOC | owner decision 2026-11-13, replay (SL:955-961) | `statusline.turn.dim_below_out` | B |
| 056 | 20,000 | SL:972 | CFG | M | 9,650 calls / 120 transcripts (SL:968-971) | `statusline.tokens.rebuild_excess` | B |
| 057 | 15 tok/s | SL:973 | CFG | DOC | harness per-agent decode floor (SL:964-965) | `statusline.turn.floor_tps` | B |
| 058 | 4× | SL:974 | CFG | J | "margin for slow prefill" (SL:965) | `statusline.turn.stale_factor` | B |
| 059 | 2,000 chars per image | SL:1137,1149 | CFG | OWNER-C | review #6.3 records the decision, not the derivation | `statusline.composition.image_chars` | R1 |
| 060 | 256 ids | SL:1153 | CFG | Dv† | adjacency comment (SL:1029-1032) | `statusline.transcript.dedup_memory` | R1 |
| 061 | 40 chars | SL:1017 | NC | Dv† | ≥ 36 = a session UUID | NC: cache file-name format shared during shadow (P2r1 §6.3) | R1 |
| 062 | sha1 `[:16]` | SL:405 | NC | C | cache key | NC: file-name format | B |
| 063 | 7 chars | SL:389 | NC | C | git short sha | NC: git format | B |
| 064 | 9999 | SL:325 | NC | Dv† | sentinel (F-5) | NC: explicit "unknown age" in Go | R1 |
| 106 | `len(pts) < 2` → none | SL:666 | NC | Dv | a trend needs two samples | NC: structural | R1 |
| 107 | preempt `> 0` | SL:346 | CFG | DOC | "same rule as the queue (#17.3)" | `statusline.queue.yellow.preempt_rate_gt` (H-1) | R2 |
| 108 | running `< 1` | SL:825 | CFG | DOC | review #20; WIDGETS Idle | `statusline.idle.running_below` | R1 |
| 109 | `round()` half-even; `" <1%"`; width 2 | SL:1171-1172 | NC | DOC | SL:1162,1172 | NC: display format (parity BX) | R1 |
| 110 | `>= 2` parts | SL:595 | NC | DOC | SL:595 comment | NC: structural | R1 |
| 111 | `> 0` zero-suppression group | SL:536-537,586-598,602,627,629,1170,1221 | NC | DOC | WIDGETS Tokens; review #8 | NC: structural | R1 |
| 112 | `(i + 0.5) × 10` | SL:428 | NC | Dv | the cell's midpoint | NC: mathematical | R1 |
| 113 | 8 levels, half-up | SL:136,673-675 | NC | C+Dv | U+2581–U+2588 offer 8 heights | NC rule over the glyph string (OD-02) | R3 |
| 114 | 1e-9 | SL:671 | NC | Dv | division guard | NC | R1 |
| 115 | percent clamps | SL:146,422,479,508,517,674,758 | NC | Dv | percent domain; negatives plot as 0 (SL:674) | NC | R2 |
| 116 | ROWS `>= 2` / `> 2`; COLUMNS 0 = unknown ⇒ wide; trim only if `cols > 0` | SL:1217,1224,1232 | CFG+NC | DOC | WIDGETS Tunables; SL:50 | semantics of `statusline.rows` + `narrow_cols` | R2 |
| 117 | `--subagent` `.2fM`/`.1fk`, `mm:ss` | SL:876-885,919-920 | CFG (if OD-14 keeps it) | OWNER-B | none | `statusline.subagent.units` | R1 |
| 133 | 4,300 digits | CPython 3.11 `default_max_str_digits` (executed r2, synthetic) | NC | C | runtime default | NC parity constant in the transcript decoder | R2 |
| 134 | 300 ms debounce; cancel in-flight | SL:43-44; WIDGETS | EXT | EXT | Claude Code scheduler | — | R1 |
| 135 | 5 s subagent timeout | WIDGETS subagent contract | EXT | EXT | Claude Code | — | R1 |

### C.3 Proxy, CA, ledger (`internal/proxy`, `internal/ledger`, P3; `internal/ca`, P4)

| T | Value (op) | Site | Class | Rat. | Rationale | Key / NC reason | Last |
|---|---|---|---|---|---|---|---|
| 065 | 64,000 B (`>`) | PX:368,408 | CFG | OWNER-C | purpose "runaway line guard", value not | `proxy.sse_tap.max_line_bytes` (OD-35) | R1 |
| 066 | keep 19 + new = ≤ 20 files | PX:291-292 | CFG | OWNER-E | purpose (PX:284-285), count not | `proxy.failed_capture.keep` (location `paths.failed_capture_dir`, pass-5 r2 K-3) | R3 |
| 067 | `< 50,000,000` chars | PX:295 | CFG | OWNER-C | none | `proxy.failed_capture.max_chars` | R1 |
| 068 | `[:600]` | PX:287 | CFG | OWNER-D | none | `proxy.decision_log.error_body_chars` | R1 |
| 069 | `[:300]` | PX:322 | CFG | OWNER-D | D7 field value; 300 through cutover | `ledger.upstream_error.max_chars` | R1 |
| 070 | round 3 dp / 1 dp | PX:213,238,273,536 | NC | C | ledger number format | NC: D7 | B |
| 071 | `[:8]` | PX:332,335 | NC | C | UUID first group | NC: D7 value format | R1 |
| 072 | 80 | PX:83 | NC | C | HTTP default port | NC: URL semantics | B |
| 073 | `>= 400` | PX:205,283 | NC | C | HTTP error class | NC: protocol | B |
| 074 | 3 backups | PX:564 | CFG | OWNER-E | none | `ca.backups_keep` | R1 |
| 075 | 30 s / 0.5 s | PX:723-725 | CFG (DROP with `ca.restart_command`) | OWNER-G | none | `ca.regen_wait_s` / `ca.regen_poll_s` | R1 |
| 076 | `removed < 10` | PX:692 | CFG | Dv† | bounds a loop whose delete is `check=False` | `ca.keychain_delete_max` (darwin) | R1 |
| 122 | 600 s inactivity | m/options.py:240-247; watchdog m/proxy/server.py:117-120,344-354,387; disarmed in hooks m/proxy/mode_servers.py:70 | CFG | C | tool default (fired once in production on an MCP SSE, r8 §1.1) | `proxy.idle_timeout_s` (OD-37) | R2 |
| 123 | TLS ≥ 1.2, max unbounded | m/net/tls.py:69-70 | NC | C | tool default | NC: security floor | R1 |
| 124 | 58 s h2 ping | m/options.py:137-140 | NC | C | tool default | NC, only if hylo speaks h2 upstream | R1 |
| 125 | RSA 2048; CA 3,650 d; leaf 199 d span, back-dated 2 d (197 d forward); leaf reuses the CA key; SHA-256 | m/options.py:9,226-233; m/certs.py:40-44,340-341,427-431,493,803-811 | NC | C | tool default | NC in `hylo ca` with comments | R3 |
| 126 | no connect timeout (OS) | m/proxy/server.py:212 (`asyncio.open_connection`, no `wait_for`) | CFG | N/A | absent limit | `backend.connect_timeout_s` (OD-42) | R1 |
| 127 | unbounded buffered body | PX:195-208; m/addons/proxyserver.py:164-183 | CFG | C | tool default | `proxy.max_buffered_body_bytes` (OD-54) | R1 |
| 128 | unbounded WebSocket retention | m/proxy/layers/websocket.py:186 | NEW-H | C | tool default | D16 bounded buffer (HY-WS-1) | R1 |
| **136** | 100 leaves, FIFO, no expiry re-check | m/certs.py:541,576-580,815-816 | NC | C | tool default | NC in `internal/ca`; re-mint before `not_after` for a long-lived proxy (OD-50) | **R3** |
| **137** | 5 upstream connections per address per client connection | m/proxy/server.py:109,206 | N/A | C | tool default | N/A: Go transport limits (HY-PROTO-1) | **R3** |
| **138** | 1 s script reload poll | m/addons/script.py:74,150 | DROP | C | tool default | — (OD-26; compiled binary) | **R3** |

### C.4 Exporter, hook, launcher, preflight, backfill, services

| T | Value (op) | Site | Class | Rat. | Rationale | Key / NC reason | Last |
|---|---|---|---|---|---|---|---|
| 077 | 50 sessions | EX:24 | CFG | OWNER-E | purpose "most-recent sessions tracked", value not | `exporter.session_limit` | R1 |
| 078 | 9210 | EX:25 | CFG | C (unverified) | Prometheus "default port allocations" wiki (exporters from 9100); the number is arbitrary | `exporter.port` (+ `exporter.bind`, HY-BIND-5) | R3 |
| 079 | bytes / 4.0 | EX:192-193 | CFG | C | "~4 chars per token" (EX:192) | `exporter.est_chars_per_token` | B |
| 080 | `[:8]` | EX:382 | NC | C | UUID group | NC: D7 label value | R1 |
| 081 | `status == 200` | EX:206 | NC | Dv† | success is 200 | NC: D7 metric semantics | R1 |
| 129 | backlog 5 | py39 socketserver.py:441 (py311 :443) | NC | C | library default | NC (failure mode only) | R1 |
| 130 | no socket timeout | py39 socketserver.py:784 (py311 :792) | NEW-H | C | library default | `exporter.read_header_timeout_s` / `idle_timeout_s` (HY-BIND-6, OD-33) | R1 |
| 131 | request line 65,537 B; header line 65,536 B, 100 headers; HTTP/1.0 | py39 http/server.py:402,623; http/client.py:109-110,212-217 | NC | C | library default | NC | R2 |
| 082 | 0.40 (`p < thr` = fake) | HK:33,249; L:150-152 | CFG | M | tuned 2026-11-10 after a 0.487 fake stop (L:150-151) | `hook.kev.threshold` | B |
| 083 | 2.5 s per socket op | HK:34,113 | CFG | OWNER-G | basis Kev-0.8B (HK:125-127); deployed kev-4b unmeasured; bound 15 s no-dribble, unbounded with dribbling | `hook.kev.timeout_s` (OD-56) | R3 |
| 084 | 14 | HK:35 | DROP | N/A | dead (still `int()`-parsed at import) | — | R1 |
| 085 | `[-6000:]` | HK:36,90 | CFG | OWNER-C | none | `hook.kev.state_chars` | R1 |
| 086 | `[:400]`; `[-800:]`; head `[:800]` | HK:83,89,91 | CFG | OWNER-D | purpose (HK:87-88), values not | `hook.kev.line_chars` / `final_tail_chars` | R1 |
| 087 | 3 tries, median | HK:124,129 | CFG | M | ±0.09 single-draw noise (HK:125-127) | `hook.kev.tries` | B |
| 088 | `t > KEV_TIMEOUT / 2` | HK:133 | CFG | Dv† (J weak) | "slow endpoint: stop early" (HK:134) explains the stop, not the half | `hook.kev.early_stop_fraction` | R3 |
| 118 | `len(ps) >= 2`, last call succeeded | HK:133 | CFG | J+Dv | HK:134; a median needs > 1 value | `hook.kev.early_stop_min_scores` | R2 |
| 119 | `ps[len(ps)//2]` (upper median) | HK:137-138 | NC | Dv† | leans toward allowing the stop | NC: median definition (parity) | R1 |
| 089 | `[-160:]` / `[-100:]` | HK:215,268 | CFG | OWNER-D | none | `hook.log.tail_chars` / `hook.autocontinue.quote_chars` (H-5) | R2 |
| 090 | `len > 20` | HK:236 | CFG | OWNER-F | none | `hook.autocontinue.colon_min_chars` (op `>`) | R3 |
| 091 | `len < 200` | HK:179 | CFG | OWNER-F | none | `hook.autocontinue.max_sentence_chars` (op `<`) | R3 |
| 092 | `n >= 12` or (`n >= 4` and ratio `> 0.02`) | HK:190 | CFG | J+OWNER-F | purpose labeled (HK:188), numbers not | `hook.english.cjk_min_count` / `cjk_ratio_min_count` / `cjk_min_ratio` (op `>`) | R3 |
| 093 | 20 s | HK:141 | DROP | N/A | dead | — | R1 |
| 094 | 30 s / 5 s | L:161,158 | CFG | Dv† | 30 s ≥ the 15 s no-dribble Kev bound and is the only hard limit; 5 s for an `echo` | `run.hooks.stop_timeout_s` / `prompt_timeout_s` | R2 |
| 095 | 8090-8143 | L:72-73; CO:10 | DROP | N/A | hylo binds its own listener (OD-19) | — | R1 |
| 096 | 40 × 0.25 s | L:77; CO:35 | DROP | N/A | in-process listener | — | R1 |
| 097 | 1,800,000 ms | L:104 | CFG | DOC | "local … model is slow; allow long responses" | `run.api_timeout_ms` | B |
| 098 | refreshInterval 4 s, padding 0 | L:176 | CFG | OWNER-G | role stated (L:170-171), value not | `run.statusline.refresh_interval_s` / `run.statusline.padding` | R1 |
| 099 | 120 s | CO:11 | DROP | N/A | coordinator unwired | — | R1 |
| 100 | 4 s connect | PF:23 | CFG | OWNER-G | none; DNS outside it, N × 4 s for N addresses | `run.preflight.timeout_s` (`HYLO_RUN_PREFLIGHT_TIMEOUT_S`; toggle `run.preflight.enabled`, pass-5 r2 K-1) | R3 |
| 101 | 30 s × 3 | pl-tu:9-10 | OOS | Dv† | ≈ 90 s dead-peer detection (man ssh_config) | — (BC-SV-002) | R1 |
| 120 | `127.0.0.1:9210:127.0.0.1:9210` | pl-tu:8 | OOS | Dv | mirrors T-078 | — | R1 |
| 121 | 4141-4199 scan (live); `curl -m 2`, 40 × 0.25 s (dead) | L:20-21,85,94 | DROP | N/A | D6 invisible only | — (R-11 parity-era note) | R2 |
| 132 | 10 s minimum spawn interval | man launchd.plist ThrottleInterval; not set in pl-ex/pl-tu | CFG | C | platform default (documented) | `service.restart_throttle_s` (H-4) | R2 |
| 102 | list prices opus/sonnet/haiku | BF:28-32 | CFG | DOC | claude-api reference, cached 2026-11-03 | `prices.<family>` (OD-13) | B |
| 103 | $1 / 30 min | BF:34-35 | CFG | DOC | BF:12-14 docstring | `cost.backfill.min_usd`; minimum API time reads `statusline.cost.rate_min_api_ms.other` (H-2) | R2 |
| 104 | 30 days | BF:86 | CFG | DOC | matches `COST_WINDOW_S` | `cost.backfill.days` | B |
| 105 | `0 < span <= 4·max(o,1)/15` | BF:78 | CFG+NC | DOC | same rule as T-057/T-058 | shares the turn keys; `max(o,1)` and `<=` variant NC (P2r1 §7 I7) | B |

### C.5 Totals

| Measure | Count |
|---|---|
| Thresholds | **138** (broad 105 + r1 30 + r3 3) |
| By class | CFG 96 · NC 28 · DROP 7 · OOS 2 · EXT 2 · NEW-H 2 · N/A 1 |
| By rationale | OWNER **27** · Dv† bulk-confirm **18** · N/A 7 · EXT 2 · resolved DOC/J/M/C/Dv **84** |
| Rationale resolved | **111 of 138** (93 final + 18 awaiting one bulk "yes") |
| Owner must supply | **27** in 7 groups |
| Last changed in R3 | 18 rows (T-009, 016, 017, 026, 040, 066, 078, 083, 088, 090, 091, 092, 100, 113, 125, 136, 137, 138) |

(Rows that split into CFG and NC parts, such as T-024, T-027, T-048, T-105 and T-116, are counted once as CFG.)

### C.6 OD-57: final owner lists

**Bulk confirmation (18 rows, Dv†, one answer: "accept as derived").** T-003, T-005, T-007, T-008, T-009, T-022, T-025, T-038 (covers T-039),
T-050, T-060, T-061, T-064, T-076, T-081, **T-088** (new: "half the per-call timeout counts as slow; judgment"), T-094, T-101, T-119.

**Owner supplies a rationale (27 rows in 7 groups, one line per group).** "Labeled judgment call" is an acceptable answer (policy 16).

| Group | Rows | Suggested wording if no measurement exists |
|---|---|---|
| A. Retention and staleness windows | T-004 300 s, T-010 1800 s, T-035 1.15 × window | "judgment: 5 min of last-known telemetry; 30 min of plan limits between Claude Code reports; 15 % slack before a reset time counts as bogus" |
| B. Layout and aesthetics | T-014 72 cols, T-030 heat HSV, T-046 sparkline colors, T-117 subagent formats (if OD-14 keeps the path) | "judgment (presentation)" |
| C. Byte and size budgets | T-054 512 KiB step, T-059 2,000 chars/image, T-065 64,000 B, T-067 50 M chars, T-085 6,000 chars | "judgment: parse step / image estimate / runaway-line guard / disk guard / Kev context budget" |
| D. Diagnostic text clips | T-068 600, T-069 300, T-086 400/800, T-089 160/100 | "judgment: log readability" |
| E. Retention counts | T-066 20 files, T-074 3 backups, T-077 50 sessions | "judgment: bounded disk / label cardinality" |
| F. Hook heuristic tuning | T-090 > 20, T-091 < 200, T-092 12 / 4 and 2 % | "judgment, tuned on observed fake stops" |
| G. Timeouts and cadence | T-098 4 s refresh (with T-001), T-100 4 s preflight, T-075 30 s / 0.5 s, T-026 1 s per `ps` call (walk uncached on failure, ≤ 6 s per refresh), T-083 2.5 s per socket operation (basis Kev-0.8B; kev-4b unmeasured) | "judgment", or a kev-4b latency figure for T-083 if one exists |

---

## D. Reconciliation with sibling files

### D.1 Key names (pass-4 r2 H-1..H-8 against pass-5 deep r1; pass-5 r2 in §D.2a)

| # | Key(s) | Pass-5 r1 | Check this round | Verdict |
|---|---|---|---|---|
| H-1 | `statusline.queue.yellow` map | no row (not env-backed) | both sites are `> 0` on `dgx_preempt:rate5m` (SL:346, SL:740) | consistent |
| H-2 | `statusline.cost.rate_min_api_ms.{cc,other}`; `cost.backfill.days`, `cost.backfill.min_usd` | no row | `SL:253` else-arm; `BF:35` is the same 1,800,000; `BF:34` = `SL:219` = 1.0 | consistent |
| H-3 | r2: `run.preflight_timeout_s` → **now `run.preflight.timeout_s`** | pass-5 r2 K-1: `run.preflight.enabled` (ENV-32, inverted from `DGX_SKIP_PREFLIGHT`) + `run.preflight.timeout_s` | **adopted** (§D.2a); `HYLO_RUN_PREFLIGHT_TIMEOUT_S` is unchanged | consistent |
| H-4 | `service.restart_throttle_s` | no row | semantics verified (§A.1 row 8) | consistent |
| H-5 | `hook.autocontinue.colon_min_chars`, `max_sentence_chars`, `quote_chars` | ENV-27 `hook.autocontinue.enabled` | checks run after the `DGX_AUTOCONTINUE` gate (HK:228 before :236, :264-268) | consistent; **operator note:** the source uses `> 20` and `< 200`, while `min`/`max` suggest inclusive bounds. Following P2r1 §6.2 (`plain_max` 50 with `>`, `timer.min_ms` with `>`), keep the names and state the operator in the comment, with boundary table tests (20/21, 199/200) |
| H-6 | `hook.english.cjk_min_count` / `cjk_ratio_min_count` / `cjk_min_ratio` | ENV-26 `hook.english.enabled` | HK:190 | consistent; same operator note (`> 0.02`) |
| H-7 | `run.hooks.*`, `run.statusline.refresh_interval_s` / `padding`, `run.api_timeout_ms` | ENV-38 `run.statusline.enabled` | — | consistent |
| H-8 | `statusline.window_age.ps_timeout_s` | no row | §A.1 row 2 | consistent |
| other | `statusline.telemetry.ttl_s`, `statusline.rows`, `hook.kev.{threshold,timeout_s,state_chars}`, `exporter.{session_limit,port,bind}` | ENV-10, -11, -21, -22, -24, -17, -18 | identical names | consistent |
| T-084 | — (DROP) | ENV-23: accepted and ignored, dropped after cutover | same outcome; pass 5 adds the shadow-period alias | consistent |

### D.2 Pass-1 r3 (converged)

- Upstream concurrency `≤ 5 per address` (`proxy/server:109,206`), the 1 s script reload, 600 s watchdog, RSA 2048 / CA 10 y / leaves 199 d,
  "1.5 s per socket operation" and the 43 env inputs all **agree** with this round (T-137, T-138, T-122, T-125, T-005; pass-5 ENV-01..43).
- Pass-1 r3 §C row 8 (SIGHUP gap in pass 4) is **resolved** by R-12.
- Wording only: pass-1 r3 writes "leaves 199 d". That is the span; the forward validity is 197 d (§A.1 row 7). No disagreement.

### D.2a Pass-5 r2 key table (§C.3) — alignment

| Item | Pass-5 r2 | This catalogue | Action |
|---|---|---|---|
| **K-1** | `run.preflight.enabled` + `run.preflight.timeout_s` (rule 5: a feature with settings is a table with an `.enabled` leaf) | r2 had flat `run.preflight` + `run.preflight_timeout_s` | **Adopted** (T-100). Neither key's semantics changes, `HYLO_RUN_PREFLIGHT_TIMEOUT_S` is identical, and `hylo doctor` reads the same keys. No concrete reason against, so **no new owner item**. The owner approves the whole table under pass-5's **OD-74** |
| K-3 | `paths.failed_capture_dir` (default `~/dgx-llm-obs/`, `PX:289`) | r1 noted "needs a path key" | **Adopted** (T-066/T-067 key note) |
| K-8 | one `config.Seconds` type for all `*_timeout_s` keys, total-deadline semantics (OD-56) | T-005, T-083, T-100, T-122, T-126 | consistent |
| K-9 | adopts P4r2 H-2 `statusline.cost.rate_min_api_ms` = `{cc, other}` | T-023, T-103 | consistent |
| K-4, K-5, K-6, K-7, K-2 | `exporter.bind` default per OD-24/27; Kev key file; `TMPDIR` default source; prefixes list; `--profile` | no threshold rows affected (T-078 uses `exporter.bind` by name only) | consistent |
| rule 2 (`paths.*`) | locations under `paths.*` | `hook.log.tail_chars` (T-089) stays in the component; its location is `paths.hook_log` | consistent |

**Rule-5 sweep of the whole catalogue.** Every feature in §C that has a legacy on/off switch *and* its own settings already uses the table +
`.enabled` form: `statusline.git` (T-013), `statusline.sparkline` (T-006..T-009, T-045, T-046), `run.statusline` (T-098), `hook.english`
(T-092), `hook.autocontinue` (T-089-quote, T-090, T-091), and now `run.preflight` (T-100). Features with settings but **no** legacy toggle
(`statusline.telemetry`, `statusline.idle`, `statusline.cost`, `hook.kev`, `proxy.failed_capture`, `run.hooks`) stay tables without
`.enabled`, because rule 5 creates no toggle where legacy has none. One borderline case: `ca.restart_command` acts as an implicit toggle for
T-075's `ca.regen_wait_s` / `ca.regen_poll_s`. Both are expected to be dropped together (pass-5 r2 ENV-08: "likely obsolete"). If they are kept,
the rule-5 form would be `ca.restart.{command, wait_s, poll_s}`. This is noted, not changed.

All other keys in §C match the pass-5 r2 §C.3 names for every env-backed row (ENV-10, -11, -12, -13, -17, -18, -21, -22, -24, -26, -27, -32,
-38), and the pass-4-only keys use the same rules (component namespace, unit suffix).

### D.3 Remaining disagreements

**None.** K-1 is adopted, so pass 4 and pass 5 r2 agree on every key. The only remaining step is the owner's approval of the key table (pass-5
OD-74; OD-01 rule). The H-5/H-6 operator note (§D.1) is a comment convention, not a disagreement.

---

## E. Consolidated final NFR catalogue (for Phase 1)

### E.1 Performance

| NFR | Legacy behavior and numbers | BC / OD / T |
|---|---|---|
| P-1 One status line run fits Claude Code's scheduler | Triggers: assistant messages, `/compact`, mode changes, 4 s tick; 300 ms debounce; a newer trigger cancels the running one. Per run: at most one VM fetch (only once the TTL has passed; TTL = refresh ⇒ every tick fetches), 1.5 s per socket operation, ≤ 3 s without dribbling, DNS unbounded for host names. The fetch also runs when the narrow test hides row 2 (`SL:1217-1224`). Git cached 5 s. `ps` walk: once per session **when it succeeds**, otherwise repeated every refresh, ≤ 6 × 1 s (total deadline per call). Cost-history write ≤ once per minute | BC-SL-010, -023, -040, -041, -053; T-001, T-005, T-013, T-022, T-025, T-026, T-098, T-134; OD-56 |
| P-2 Parse bounds | Transcript read: incremental, ≥ 512 KiB per run, extended to the next newline with **no upper bound** (CONV-ABS-43); dedup memory 256; a `mixv6` marker change forces a full re-parse. VM body read whole. Hook reads the whole transcript on every Stop | BC-SL-032, -068/098, BC-HK-008; T-054, T-060 |
| P-3 Streaming latency | SSE relayed chunk by chunk, tap tail ≤ 64,000 B; `/v1/messages*` JSON or ≥ 400 buffered for the addon; **every other non-SSE response buffered in full, no cap** (CONV-ABS-44); WebSocket messages retained | BC-PX-014, -016, -037, -045; T-065, T-127, T-128; OD-54 |
| P-4 Long routed responses | client timeout 30 min; proxy idle cut 600 s (per client connection, reset by any event, disarmed during hooks); no total cap; pass-through SSE up to 3,600 s and WebSockets 3 h 51 min observed | BC-LN-005, BC-PX-049; T-097, T-122; OD-37; HY-TIMEOUT-1, HY-PASS-1 |
| P-5 Exporter scrape cost | full ledger rescan after growth, single-threaded, HTTP/1.0 one request per connection | BC-EX-003, -022, -026, -027; T-131; OD-39 |
| P-6 Stop-hook latency | Kev 13 ms/pass measured for Kev-0.8B only; ≤ 3 calls; a failed call costs ms (refused) to 2.5 s (unanswered connect) (CONV-ABS-73); strict bound 15 s without dribbling, unbounded with it; early stop only after a slow **successful** call with ≥ 2 scores; Claude Code kills at 30 s. A final failed call after a success crashes the hook (H-04) | BC-HK-010, -022; T-083, T-087, T-088, T-094, T-118; OD-12, OD-56 |
| P-7 (new) mitmproxy internal caps | leaf cache 100 (T-136); 5 upstream connections per address per client connection (T-137); neither binding at observed scale | T-136, T-137; OD-50 |

### E.2 Reliability

| NFR | Legacy behavior | BC / OD / T |
|---|---|---|
| R-1 Status line exits 0 except documented crash paths | guard prints the 29-byte degraded line; exceptions CP-X01/X02 (import-time env parse), CP-X03 (guard's own `print`), CP-X04 (signals) | BC-SL-001, -087; CONV-ABS-41 |
| R-2 Telemetry ladder | green while the latest fetch succeeded (default TTL); yellow from the **first** failed fetch; last-known ≤ 300 s on fetch runs, any age on in-TTL runs; `◌ DGX ?` without a sample | BC-SL-041, -043, -091; T-003, T-004; CONV-ABS-42; OD-55 |
| R-3 No fabricated zeros | missing series omit segments | BC-SL-074 |
| R-4 Cache durability | `mkstemp` + `os.replace`; a lost cost-history update is repaired within a minute (accepted) | BC-SL-052; T-022 |
| R-5 Proxy never breaks traffic on observability failures | appends swallow `OSError`; exceptions OD-45, OD-18, OD-08 | BC-PX-028, -048 |
| R-6 Upstream failures | no retry/backoff, no connect timeout, eager connect | BC-PX-024, -047; T-126; OD-17, OD-42 |
| R-7 Stop hook | no top-level guard; H-01..H-09, H-04 production-reachable | BC-HK-019, -022; OD-12 |
| R-8 Exporter crash loop | a poison line crashes `rebuild()`; launchd spawns **at most once every 10 s** (documented) | BC-EX-021; T-132; OD-11 |
| R-9 Supervision | launchd `KeepAlive` for exporter and tunnel; tunnel dead-peer ≈ 90 s; `ExitOnForwardFailure=yes` (`pl-tu:11`) | BC-SV-001/002 (OOS); T-101, T-132 |
| R-10 Pre-trap orphan window | mitmdump started at `L:75`, trap at `L:97`; readiness failure `exit 1` (`L:78`) orphans it; visible mode's `L:95` orphans the router; Ctrl-C orphans only before `m/tools/main.py:128` | pass-1 r3 §B.2; OD-50, OD-66 |
| R-11 Busy router range aborts invisible launches | 59 `nc` probes then `exit 1` (`L:17-22`) | CONV-ABS-61; OD-19 (hylo drops it) |
| **R-12 (new)** Terminal close kills the proxy without draining | SIGHUP not trapped (`L:97`), no handler in mitmproxy (`m/tools/main.py:128-129` only SIGINT/SIGTERM) → immediate death, no `error` hook, no ledger lines for in-flight flows. hylo: detached shared proxy (OD-66 (a)), drain per OD-38, stop per OD-50; give SIGHUP an explicit meaning | §B.2; pass-1 r3 I-23; OD-38, OD-50, OD-66 |

### E.3 Security

| NFR | Legacy behavior | BC / OD / T |
|---|---|---|
| S-1 Network exposure | proxy on all interfaces, RFC 1918 clients admitted; exporter `0.0.0.0:9210` unauthenticated (both accepted for legacy) | OD-24, OD-27, OD-34; HY-BIND-1..6; BC-EX-001 |
| S-2 Credentials | key file cached per process; unreadable key ⇒ client credentials forwarded (P-R4); only `Authorization` replaced; Kev key as env value; backend plain HTTP | OD-06, OD-07; D16 |
| S-3 Upstream TLS | verification on, certifi only, TLS ≥ 1.2; `SSLKEYLOGFILE` inherited | BC-PX-047; T-123; OD-41; HY-TLS-1/3 |
| S-4 CA | RSA 2048; CA 3,650 d and leaves 199 d, both back-dated 2 d; leaves reuse the CA key pair, SHA-256; cached leaves never re-validated | T-125, T-136 |
| S-5 Data at rest | failed bodies ≤ 50 M chars × ≤ 20 files; ledger unrotated; caches `0600` | BC-PX-021; T-066, T-067 |
| S-6 Command execution | `DGX_PROXY_RESTART_CMD` `shell=True`; trust-CLI subprocesses with no timeout (`PX:568,578,590,606,638,693`) | — |
| S-7 Owner choices | permission prompts skipped, sandbox off by default | BC-LN rows; P2r2 §6.8 |

### E.4 Operability

| NFR | Legacy behavior | BC / OD / T |
|---|---|---|
| O-1 Exporter stall | no socket timeout, one thread, backlog 5, HTTP/1.0; header limits 100 × 65,536 B (431) | BC-EX-026; T-129..T-131; OD-33 |
| O-2 Crash loop | one start about every 10 s, zero bytes, no alert | BC-EX-021; T-132; OD-11 |
| O-3 Silent failures | 600 s idle cut on pass-through leaves no ledger trace; SIGHUP death leaves none (R-12) | BC-PX-024, -049; OD-37, OD-38 |
| O-4 Logs and growth | per-window mitmdump logs never deleted; ledger and hook log never rotated; captures ≤ 20 | T-066 |
| O-5 Health | no exporter or proxy health endpoint; preflight 4 s → `hylo doctor` | BC-PF-001/002; T-100 |
| O-6 Config validation | malformed numeric env crashes at import; per-variable boolean predicates | BC-SL-087; OD-05 |
| O-7 (new) Live reload | an edit to the addon reaches every window within about 1 s | T-138; OD-26 |

### E.5 Portability (D5)

Process ancestry (`ps` + C-locale `strptime`, depth 6, 1 s per call) → `internal/platform` with a Windows fallback (D4-EX-1). Cache names → OD-03.
Supervision: launchd (10 s minimum spawn interval) → `service.restart_throttle_s` with an approximate per-OS mapping. Proxy launch (`zsh`, `nc`,
`lsof`, `flock`) → one in-process listener (OD-19). CA trust (`security`, `openssl`) → `hylo ca` per OS. Interpreter-dependent parsing (3.11
vs 3.9.6, T-133) → O1/OD-15. Time zones → OD-22. Paths → `paths.*`.

### E.6 Missing NFRs (expected, not found)

Ledger rotation; health endpoints; upstream retry/backoff and connect timeout; a body-size cap (T-127); bounded WebSocket retention (T-128); a total
deadline on network calls, with DNS covered (status line, hook, preflight); trust-CLI subprocess timeouts; config validation at load; ledger time
zones; launcher cleanup before the first child starts (R-10); a SIGHUP policy and drain on window close (R-12); leaf re-mint before expiry in a
long-lived proxy (T-136); automated tests.

---

## Delta Summary

- New items added: **3 thresholds** (T-136 leaf cache 100, T-137 upstream concurrency 5, T-138 reload poll 1 s; all mitmproxy defaults missing from
  r1/r2); **1 reliability NFR** (R-12 terminal-close SIGHUP, orchestrator item, verified); new NFR rows P-7 and O-7; missing-NFR entries for SIGHUP
  policy and leaf re-mint.
- Retractions: **CONV-ABS-73** (r2's "typical 2.5 s per failed Kev call"), **CONV-ABS-74** (wrong anchors: r2 `SL:103` for T-016/T-017, r1
  `SL:135` for T-113).
- Verified: CONV-ABS-61, -62, -63, -64; R-10, R-11; 197-day forward leaf validity and CA-key reuse; launchd 10 s minimum spawn interval; F-3 bound;
  DNS outside timeouts (extended to the preflight); H-1..H-8. Every one of the 121 source anchors re-printed and matched.
- Refined: CONV-ABS-62 (a timeout ends the walk; the usual failure is cheap), R-10 wording (visible mode orphans the router), F-3 (no bursts at the
  default TTL), T-125 (199 d span / 197 d forward), T-088 → bulk list, T-040 → DOC (owner request), H-5/H-6 operator notes, T-078 closed as an
  unverified convention.
- Key alignment with pass-5 r2: **K-1 adopted** (`run.preflight.enabled` + `run.preflight.timeout_s`), K-3 `paths.failed_capture_dir` adopted,
  rule-5 sweep found no other flat key to change, 0 remaining key disagreements.
- Consolidated: 138-row threshold catalogue with operator, class, rationale, key and last-changed round; NFR catalogue P-1..P-7, R-1..R-12,
  S-1..S-7, O-1..O-7; OD-57 lists **18 bulk / 27 owner**.
- Owner items: none new (OD-82..OD-85 unused); OD-50 gains T-136; OD-38/OD-50/OD-66 gain R-12.

## Remaining Gaps (verbatim-carryable)

1. Owner answers for OD-57: bulk confirmation of 18 Dv† rows and 27 owner rationales in 7 groups (§C.6). Until then, those defaults carry "UNKNOWN —
   owner to confirm" in code comments.
2. T-078's Prometheus port-allocation source is unverified (no network). It is a rationale label only; confirm it or relabel it "judgment" when the
   `exporter.port` comment is written.
3. Pass 5 (sibling): keys are reconciled (§D.2a). Still to confirm in pass 5's register: unbounded DNS (status line, hook, preflight), the
   `subprocess.run` total deadline, and the strict operators of H-5/H-6. K-8's `config.Seconds` already covers total-deadline semantics.
4. SIGHUP delivery to mitmdump on terminal close stays MEDIUM (tty semantics not covered by authorized sources). The handler set itself is HIGH.
5. P1 test plan: boundary table tests for the `SL:674` clamp, the `cols > 0` trim, and the strict operators of T-090..T-092 (design note).

## Novelty Assessment

Novelty: SUBSTANTIVE

By this round's own rule, a missing threshold, a wrong rationale or a retraction counts as substantive. Three thresholds that shape the legacy proxy
were missing: the leaf cache cap and its missing expiry re-check (which create a hylo requirement for a long-lived proxy under OD-50), the
per-address upstream concurrency cap, and the 1 s reload poll. A reliability NFR was also missing: terminal close kills the proxy with no drain and
no ledger lines (R-12). Two narrow retractions were made (CONV-ABS-73, -74). Everything else this round confirms or consolidates round 2. All of the
round-2 retractions and the R-10/R-11 NFRs survived fresh evidence.

## Convergence Declaration

Another round needed: the three new rows (T-136..T-138) and R-12 need an independent audit. One more check would help: a package-wide sweep of
mitmproxy 12.3.1 for other class-level numeric constants, the kind T-136 and T-137 came from. That would make sure no further tool defaults are
missing.

## State Checkpoint

```yaml
pass: 4
round: 3
status: complete
timestamp: 2026-11-14T09:05:00Z
novelty: SUBSTANTIVE
files_scanned: legacy L:1-180, SL:70-100,160-180,264-296,315-360,536-562,955-974,1210-1245 plus all 121 threshold anchors (anchors.py), HK:25-40,80-93,95-145,170-275, PF:18-26, both plists; mitmproxy 12.3.1 version.py, tools/main.py, certs.py, options.py, proxy/server.py, proxy/mode_servers.py, addons/script.py, package-wide SIGHUP/signal search; py311/py39 urllib/request.py, http/client.py, http/server.py, socket.py, socketserver.py; man launchd.plist, man ssh_config; docs STATUSLINE-REVIEW row 9, STATUSLINE-WIDGETS Timer
thresholds: {total: 138, new_this_round: 3, by_class: {CFG: 96, NC: 28, DROP: 7, OOS: 2, EXT: 2, NEW-H: 2, NA: 1}, rationale: {owner: 27, bulk_confirm: 18, na: 7, ext: 2, resolved_other: 84}, resolved: 111}
verification: {confirmed: 11, confirmed_with_refinement: 6, retracted: 2}
retractions: [CONV-ABS-73, CONV-ABS-74]
conv_abs_unused: [75, 76]
new_owner_items: []
od_unused: [OD-82, OD-83, OD-84, OD-85]
updated_owner_items: [OD-38, OD-50, OD-57, OD-66]
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r3/
next: pass 4 round 4 (audit T-136..T-138 and R-12; package-wide mitmproxy constant sweep)
```
