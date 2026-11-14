# Pass 4 Deepening — Round 2: audit of round 1, carried gaps, census re-run — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/`, read-only and static. Nothing in `legacy/` was imported, executed or modified. No proxy, nothing
  networked. CLAUDE.local.md was not read.
- Authorized read-only references: mitmproxy 12.3.1 (`m/` = `.mitmenv/lib/python3.12/site-packages/mitmproxy/`, `version.py:5` = `"12.3.1"`);
  `man launchd.plist`, `man ssh_config`; CPython stdlib 3.9 (`py39/` = CommandLineTools `Python3.framework/Versions/3.9/lib/python3.9`, the
  `/usr/bin/python3` 3.9.6 that runs the exporter) and 3.11 (`py311/` = `/opt/homebrew/anaconda3/lib/python3.11`).
- One runtime probe, on **synthetic input only**: `python3.11 -I` and `/usr/bin/python3 -I` parsing a JSON integer of 4,300/4,301/5,000 digits
  (T-133).
- Inputs read: pass-4 broad, pass-4 deep r1, pass-5 deep r1 (§A env inventory, CV-18 naming), pass-0 deep r3 (§2 rows 210 and 229), pass-1 deep r2
  (§B.3, OD-66, CONV-ABS-57), pass-2 deep r1 §6.1-6.3 (CONFIG map) and r2 §6.8; `docs/STATUSLINE-WIDGETS.md`, `docs/STATUSLINE-REVIEW-2026-11-13.md`,
  `docs/PLAN.md` (D15, §6 lines 97 and 105).
- Scratch (fresh scripts, round 1's scripts not reused): `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r2/`
  (`census.py` → `census.tsv`; `classify2.py`; `strcensus.py`; `p2keys.txt`).
- Abbreviations as in round 1: `SL` status line, `PX` proxy, `EX` exporter, `HK` hook, `PF` preflight, `BF` backfill, `L` launcher, `CO`
  coordinator, `pl-ex`/`pl-tu` plists.
- Numbering: retractions **CONV-ABS-61..64** (all four used). **No new owner items**: OD-70..OD-73 are unused. Every decision this round raised
  fits an existing item (OD-50, OD-56, OD-57, OD-66). Sibling files were not edited.

---

## 0. Audit of round 1 against the 5 hallucination classes

| Class | Result |
|---|---|
| 1 Over-extrapolated lists | T-111 site list re-checked line by line: correct (`SL:536,586-598,602,627,629,1170,1221`). T-115's clamp list is **incomplete, not inflated**: it misses `SL:674` `max(v, 0.0)` (negative sparkline values plot as 0). Refinement only |
| 2 Miscounted enumerations | 30 new rows; 28 resolved (19 Dv† + 4 C + 5 N/A); 24 + 1 OWNER; 7 groups of 3/4/5/4/3/3/3 = 25. All recounted and **correct** |
| 3 Fabricated names | none. Every quoted doc phrase was found verbatim (table B.2) |
| 4 Same-basename conflation | none |
| 5 Metrics | census re-derived by a fresh script (§C): **522 / 10 / 24 confirmed** |

Four round-1 claims fail the audit on substance and are retracted:

| Marker | Round-1 claim | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-61** | T-121 "visible-mode router port range 4141-4199 … N/A: dead under D6 (invisible mode only)", in §A.3.1, §C.3 DROP and §C.5 | **Live in invisible mode.** The `nc -z` scan at `L:17-22` comes before the invisible/visible split at `L:70` and is unconditional. Only `ROUTER_PORT` skips it (`L:17-18`). If 4141..4199 are all busy, the launcher prints "no free router port" and **exits 1 even in invisible mode**. Its result (`PORT`) is unused in invisible mode, because `ANTHROPIC_BASE_URL=…:$PORT` is set only in the visible branch (`L:99-102`). The `curl -m 2` probe (`L:85`) and the router start wait (`L:94`) are visible-only (`L:86-87`), so those two stay dead. The pass-0 orchestrator flagged the same point; it was found independently here | `L:15-22,70,85-96,99-102` |
| **CONV-ABS-62** | T-026 Dv† "one `ps` call per level, **once per session** (cached `proc_start`); 1 s keeps a worst-case walk inside the run budget". P-1 also says "`ps` walk ≤ 6 × 1 s, once per session" | Only a **successful** walk is cached (`SL:286-288`). A walk that finds no `claude` ancestor (renamed binary, pid ≤ 1, localized `ps`, empty output, timeout, or Windows with no `ps`) returns None without writing, and **runs again on every refresh** (`SL:1229` calls it whenever `session_id` is present). Passes 2, 3 and 5 already say so (P2r1 l.197 "Failed `ps` walks are not cached"; BC-SL-023; DET-46). Worst case per refresh is 6 × 1 s = **6 s, longer than the 4 s tick** (T-098), so "inside the run budget" is false. The rationale survives only as "1 s bounds each `ps` call". It moves to the owner list (group G) | `SL:264-294,1229`; P2r1 §1 l.197 |
| **CONV-ABS-63** | T-083 Dv† "3 × 2.5 s = **7.5 s**, inside the 30 s Stop timeout"; T-094 Dv† "Stop: ≥ worst-case Kev time 7.5 s plus transcript read" | Contradicts round 1's own F-6. `urlopen(timeout=2.5)` bounds **each socket operation**: connect (`socket.create_connection` → `sock.settimeout` + `connect`) and then each blocking `recv`. So one call can take connect ≤ 2.5 s **plus** a response wait ≤ 2.5 s **plus** more per dribbled read. The early stop cannot cut a failing series short: a failed call returns `(None, None)` (`HK:120-121`), and `t is not None` (`HK:133`) is false after a failure. Corrected bounds: typical failure ≈ 2.5 s per call (7.5 s total); strict bound without dribbling 3 × (2.5 + 2.5) = **15 s**; **unbounded** with a dribbling server, where Claude Code's 30 s kill is the only hard limit. The 30 s value still holds (15 < 30); the stated bound did not | `HK:110-121,128-138`; py311 `urllib/request.py:1317`, `http/client.py:952-953`, `socket.py:827-836`; py39 `urllib/request.py:1315`, `http/client.py:923-924`, `socket.py:822-831` |
| **CONV-ABS-64** | T-039 Dv† "The `>` vs `>=` asymmetry is **unobservable**, since the API part prints only inside a shown timer" | Observable. With `dur > 60000` (timer shown) and `api == 60000` exactly, `>=` prints `·1m` and `>` would print nothing. Integer milliseconds make that input possible, though rare. The parity consequence: keep `>=` exactly (D4), as P2r1 §6.2 already does. The derived part ("below 60 s `_hm` prints `0m`") stands | `SL:539-553` |

Refinements to round 1 (not retractions):

- **F-3** (T-009 history cap 32): "bites only for 2 s ≤ TTL < 2.8 s" has the wrong lower bound. Point spacing is ≥ max(TTL, `HIST_MIN_GAP` 2 s,
  gap between triggers), so the cap bites whenever that spacing is below 90/32 = 2.81 s. That **includes TTL < 2 s**: at the 2 s gap, up to 45
  points fit in 90 s. It also needs triggers more often than every 2.8 s. Idle refreshes come every 4 s (T-098), so the cap can bite only during
  bursts triggered by assistant messages. It is still inert at the defaults.
- **T-007** rationale wording: review #17.2 says only "~48 s (doc said 90 s)". Round 1's "before `SPARK_PTS` capped it" is not in the source;
  drop it. The F-4 conclusion (90 s acts as gap pruning) is unchanged.
- **T-005** rationale: under per-operation semantics, the no-dribble bound is connect + first read = 2 × 1.5 = 3 s, still below the 4 s tick.
  With CONV-ABS-62's uncached `ps` walk on top, one run can exceed the tick. Keep "Dv†" for "1.5 s ≈ 60 × the 25 ms RTT"; the tick claim gets the 3 s
  bound.
- **T-118 / P-6**: the early stop uses the **last** call's latency, and only when that call **succeeded** (failed calls return `t = None`). It can
  fire after 2 scores only when a successful call took > 1.25 s.
- **T-023** map arm: `SL:253` is `300000 if src == "cc" else 1800000`. The 30-minute arm applies to **every non-`cc` source**, including entries
  with no `src`, not just `"backfill"`. Name the arm `other` (see §D H-2).

---

## A. Round 1's remaining gaps (carried verbatim) — resolution

| # | Round-1 gap | Resolution |
|---|---|---|
| 1 | Owner answers for OD-57 (§B.2 20 rows, §B.3 25 rows) | Still owner-gated. Lists updated by this round: §B.2 shrinks to **17** (T-026, T-039 change; T-083 moves to OWNER), §B.3 grows to **27** (T-026, T-083 added). See §B.3 |
| 2 | T-132 launchd `ThrottleInterval` 10 s "documented, not verified" | **Confirmed** from `man launchd.plist`: "by default, jobs will not be spawned more than once every 10 seconds" (ThrottleInterval entry); KeepAlive entry: "Jobs that exit quickly and frequently when configured to be kept alive will be throttled". Neither plist sets `ThrottleInterval` (`pl-ex:1-13`, `pl-tu:1-18`). **Semantic refinement:** this is a **minimum interval between spawns**, not a delay after exit. A process that crashes at t = 0.2 s respawns about 10 s after its previous spawn. systemd's `RestartSec` is a delay after exit, which is a different meaning. Key renamed (§D H-4). Status: **C, verified** |
| 3 | T-125 leaf validity "199 days" from P2r3 | **Confirmed**: `m/certs.py:41` `CERT_EXPIRY = datetime.timedelta(days=199)`; `:40` `CA_EXPIRY = timedelta(days=10 * 365)`; `m/options.py:9` `KEY_SIZE = 2048` (option `key_size` at `:226-232`; round 1's "`options:7,9`" citation should read `options:9,226-232`). **New detail:** `:44` `CERT_VALIDITY_OFFSET = timedelta(days=-2)`, applied at `:340-341` (CA) and `:430-431` (leaf). Both certificates are back-dated **2 days**: a leaf is valid from now − 2 d to now + **197 d**; the CA runs 3,650 days (not 10 calendar years) from now − 2 d. **New detail:** the leaf carries the **CA's own public key** (`:427` `builder.public_key(cacert.public_key())`) and is signed with SHA-256 by the CA key (`:493`). mitmproxy mints no per-host key pair. `hylo ca` (P4) records all of these as named constants with comments; reusing the CA key is unobservable to clients and is an implementation choice for P4 |
| 4 | kev-4b latency figure | **None exists in the repo.** Searched `legacy/`, `docs/` and every tracked file outside `.factory/semport` and `.git` for Kev latency figures. The only measurement is Kev-0.8B: "~40ms total at 13ms/pass" (`HK:125-127`), and `HK:234-235` also names "the 0.8B judge". The launcher pins `jaredpalmer/kev-4b@v1.0` (`L:149,153,155`); the hook's own default is `kev-latest` (`HK:32`). Recorded as an **owner rationale gap**: T-083 moves from §B.2 (Dv†) to §B.3 group G. Combined with CONV-ABS-63, the measured basis covers neither the deployed model nor the per-operation semantics |
| 5 | Pass 5 should record `round()` half-even (T-109) and per-operation timeouts (F-6) | Checked pass-5 deep r1: **PR-01** records `round(x)` half-even at `SL:1171` and the deliberate half-up `int(x + 0.5)` at `SL:426,675`. ENV-22 records `socket.settimeout` pinning for `DGX_KEV_TIMEOUT` but not the per-operation-vs-total distinction. Carried as a cross-pass note (Remaining Gap 3); not edited here |
| 6 | External recording rules (`dgx_preempt:rate5m`, `dgx_ttft:p95_30m`, `dgx_tokens:gen_rate5m`) | Outside `legacy/`; still P6 telemetry config (OD-20). Unchanged |
| 7 | OD-54..OD-57 owner decisions | Pending; OD-56 gains the CONV-ABS-63 bounds (§E) |

---

## B. Audit of round 1's new claims (fresh evidence)

### B.1 The 30 new thresholds T-106..T-135

| T | Round-1 value / site | Fresh evidence | Verdict |
|---|---|---|---|
| 106 | 2 points, `SL:666` | `if len(pts) < 2: return ""` | confirmed |
| 107 | preempt > 0, `SL:346` | `sample.get("dgx_preempt:rate5m", 0) > 0`, comment "same rule as the queue (#17.3)" | confirmed |
| 108 | running < 1, `SL:825` | literal `1`, `Compare:Lt` on `vllm:num_requests_running` | confirmed |
| 109 | `round()`, `" <1%"`, width 2, `SL:1171-1172` | `round(n / total * 100)`; `f"{pct:>2d}%" if pct > 0 else " <1%"` | confirmed |
| 110 | ≥ 2 parts, `SL:595` | `if len(inner) >= 2:` | confirmed |
| 111 | `> 0` group | all 10 sites re-read | confirmed |
| 112 | `(i + 0.5) * 10`, `SL:428` | literal | confirmed |
| 113 | 8 levels, half-up, `SL:135,673-675` | `int(min(j, len(SPARK) - 1) + 0.5)` at `:675` | confirmed |
| 114 | 1e-9, `SL:671` | literal | confirmed |
| 115 | clamps | 6 sites confirmed; **add `SL:674`** `max(v, 0.0)` | confirmed + 1 site |
| 116 | ROWS < 2 / > 2; COLUMNS = 0, `SL:1217,1224` | confirmed; refinement: `SL:1232` `if cols > 0` trims only at a known width (same "unknown ⇒ wide" rule). Note: the VM fetch at `:1218` runs whenever `rows ≥ 2`, **even when** the narrow test then drops row 2, because row 1's `⛏` needs `dgx_mtok` (`:1219-1222`) | confirmed + refinement |
| 117 | `--subagent` formats, `SL:876-885,919-920` | `:881-884` (`.2fM` / `.1fk`), `:919-920` `mm:ss` | confirmed |
| 118 | ≥ 2 scores, `HK:133` | confirmed; needs a successful last call (§0) | confirmed + refinement |
| 119 | upper median, `HK:137-138` | `ps.sort(); return ps[len(ps) // 2], t`; higher p_done means `fake = p_done < KEV_THRESHOLD` is less likely (`HK:249`), so the lean toward allowing the stop is confirmed | confirmed |
| 120 | `127.0.0.1:9210:127.0.0.1:9210`, `pl-tu:8` | literal | confirmed |
| 121 | 4141-4199; `curl -m 2`; 40 × 0.25 s, N/A dead | scan **live** (CONV-ABS-61); `-m 2` and the router wait dead | **retracted in part** |
| 122 | 600 s `tcp_timeout`, `m/options:240-246` | `m/options.py:240-247` (default `600` at `:243`). Mechanics, newly read: one `TimeoutWatchdog` per **client connection** (`m/proxy/server.py:117-120`); **every** proxy event (client or server data, hook completion) resets it (`server_event` → `register_activity`, `:387`); it is **disarmed while an addon hook runs** (`m/proxy/mode_servers.py:69-70` `with self.timeout_watchdog.disarm()`), and re-armed with fresh activity after (`server.py:79-88`). On expiry it cancels the client handler, logged "Closing connection due to inactivity" (`:344-354`) | confirmed + mechanics |
| 123 | TLS ≥ 1.2, max unbounded | `m/net/tls.py:69-70` `DEFAULT_MIN_VERSION = TLS1_2`, `DEFAULT_MAX_VERSION = UNBOUNDED`; options at `m/addons/tlsconfig.py:157-186` | confirmed |
| 124 | 58 s h2 ping | `m/options.py:137-140` | confirmed |
| 125 | RSA 2048; CA 10 y; leaf 199 d | confirmed (§A row 3); back-dated 2 d; leaf reuses the CA key | confirmed + 2 details |
| 126 | no upstream connect timeout | `m/proxy/server.py` `asyncio.open_connection(` (in `:200-240`) with no `wait_for`/timeout wrapper | confirmed |
| 127 | unbounded buffered body | `m/addons/proxyserver.py:164-183` `stream_large_bodies` None, `body_size_limit` None; `PX:195-208` sets `stream` only for SSE and `/v1/messages*` | confirmed |
| 128 | unbounded WebSocket retention | `m/proxy/layers/websocket.py:186` `self.flow.websocket.messages.append(message)` | confirmed |
| 129 | backlog 5 | py39 `socketserver.py:441`, py311 `:443` `request_queue_size = 5`; `EX:414` plain `HTTPServer` | confirmed |
| 130 | no socket timeout | py39 `socketserver.py:784` `timeout = None`, `:790-793` `settimeout` only if set (py311 `:792,798-801`) | confirmed |
| 131 | 65,537-byte request line | py39 `http/server.py:402` (py311 `:404`). **Extension** (same mechanism, failure-mode only): headers are parsed by `http.client.parse_headers` (`http/server.py:344`), which caps a header line at 65,536 bytes (`http/client.py:109`, → 431 at `server.py:346-349`) and the header count at 100 (`:110`, `:216-217`). The exporter also speaks **HTTP/1.0** by default (`server.py:623` `protocol_version = "HTTP/1.0"`): one request per connection, closed after the response | confirmed + extension |
| 132 | 10 s launchd throttle, "unverified" | **verified** (§A row 2); minimum spawn interval | confirmed |
| 133 | 4,300 digits | probe: 3.11 `default_max_str_digits = 4300`, 4,300 digits parse, 4,301 raise `ValueError`; `/usr/bin/python3` 3.9.6 has no limit and parses 5,000 | confirmed (executed) |
| 134 | 300 ms debounce, cancellation | `SL:43-44`; WIDGETS l.17-18 | confirmed |
| 135 | 5 s subagent timeout | WIDGETS "Agent-panel subagent rows", contract paragraph ("5 s timeout") | confirmed |

Result: **28 confirmed, 1 retracted in part (T-121), 1 confirmed with a semantic fix (T-132)**, plus 8 refinements (T-115, T-116, T-118, T-122,
T-125 ×2, T-131, T-132).

### B.2 The 28 resolved rationales — does the cited source say it?

| T | Round-1 basis | Check | Verdict |
|---|---|---|---|
| 003 | review #16.1 15 s scrape | review row 16: "reaches VM via the 15 s scrape" | holds (Dv†) |
| 005 | `SL:81` "~25 ms" + tick | `SL:81` verbatim; tick bound restated (§0) | holds, reworded |
| 007 | review #17.2 | "~48 s (doc said 90 s)"; "before SPARK_PTS capped it" not in source | holds, wording fixed |
| 008 | F-2 | `SL:324,337`: after a fetch, `now − hist[-1].t ≥ TTL ≥ 2` | holds |
| 009 | F-3 | bound corrected (§0) | holds, bound fixed |
| 022 | WIDGETS repair sentence | WIDGETS l.28-29 "the next minute's write repairs" | holds |
| 024 | numpy "lower" | `SL:261` `v[int(0.75 * (len(v) - 1))]` = floor index | holds (C) |
| 025 | docstring `SL:268-271` | `SL:269-270` "walk up from our parent (a per-refresh shell)" | holds |
| 026 | once per session | false on the failure path | **retracted, CONV-ABS-62 → OWNER** |
| 038 | `_hm` minute granularity | `SL:546` `int(ms // 60000)` | holds |
| 039 | asymmetry unobservable | observable at `api == 60000` | **retracted clause, CONV-ABS-64**; derived part holds |
| 050 | `.0f` share | `SL:762` `{host_share:.0f}` | holds |
| 060 | `SL:1029-1032` | verbatim "a short memory of recent ids covers refresh boundaries" | holds |
| 061 | ≥ 36-char UUID | `SL:1017` `[:40]` after sanitizing | holds |
| 064 | sentinel | `SL:325`; F-5 re-derived | holds |
| 071 | UUID first group | `PX:332,335` `[:8]` | holds (C) |
| 076 | `check=False` loop bound | `PX:691-695` `while removed < 10 and _keychain_fingerprint(…)`, `check=False` | holds |
| 078 | Prometheus port range 9100-9999 | convention claim from outside the repo; **not verifiable offline** (no network this round) | holds as C, marked unverified |
| 080 | session UUID `[:8]` | `EX:84-90,382` | holds (C) |
| 081 | 200 = success | `EX:206` `status == 200` on `anth_reply`/`anthropic_reply` | holds |
| 083 | 13 ms/pass, 7.5 s | basis is Kev-0.8B; bound wrong | **retracted, CONV-ABS-63 → OWNER** |
| 084 | dead | `KEV_MESSAGES` assigned at `HK:35`, never read. Note: still `int()`-parsed at import, so a bad value crashes the hook (pass-5 ENV-23) | holds (N/A) |
| 093 | dead | `opus_verdict` defined at `HK:141`, never called | holds (N/A) |
| 094 | ≥ 7.5 s | rationale restated: 30 s ≥ the 15 s no-dribble bound; the only hard bound | holds, **basis replaced** (CONV-ABS-63) |
| 095 | hylo binds its own listener | `L:72-73` live in legacy, N/A for hylo (OD-19) | holds |
| 096 | in-process listener | `L:77` live in legacy, N/A for hylo | holds |
| 099 | coordinator unwired | no reference to `dgx-proxy-coordinator.sh` outside itself | holds |
| 101 | 3 × 30 s ≈ 90 s | `man ssh_config` ServerAliveCountMax: disconnect when the count is reached | holds |

Tally: **24 hold** (3 reworded), **3 retracted in whole or in part** (T-026, T-039 clause, T-083), **1 basis replaced** (T-094).

### B.3 Updated rationale lists for OD-57

- **§B.2 bulk confirmation (Dv†), now 17:** T-003, T-005 (3 s bound), T-007 (wording), T-008, T-009 (bound), T-022, T-025, T-038, T-050, T-060,
  T-061, T-064, T-076, T-081, T-094 (15 s basis), T-101, T-119. Round 1's 20, minus T-026 and T-083 (to OWNER) and minus T-039. T-039 leaves the
  list because what remains of it is a parity rule (keep `>=` exactly, D4), not a rationale to confirm.
- **§B.3 owner list, now 27 rows in 7 groups:** round 1's 25, plus **T-026** (group G: "1 s per `ps` call; the walk is uncached on failure, ≤ 6 s per
  refresh") and **T-083** (group G: "2.5 s per socket operation; measured basis is Kev-0.8B, deployed model kev-4b, no figure recorded").

### B.4 The "inert at default" findings

| F | Re-derivation | Verdict |
|---|---|---|
| F-1 `STALE_OK` | Cached path `SL:324-325`: `fetch_ts > now − TTL`, `age = now − ts`; success writes `ts = fetch_ts = now` (`:348`), so cached age < TTL; a failed fetch sets `up = False` (`:353`) → stale at `:697` whatever the age. A failing fetch happens only when `now − fetch_ts ≥ TTL`, so the first stale age shown is ≥ TTL | **confirmed**. WIDGETS l.67 "Green: VM sample < 15 s old" does not describe default behavior (OD-55 stands) |
| F-2 `HIST_MIN_GAP` | as B.2 T-008 | confirmed |
| F-3 cap 32 | bound corrected (§0) | confirmed, bound fixed |
| F-4 `SPARK_MAX_AGE` | `:336` age filter runs only on a successful fetch; `:664` plots `hist[-SPARK_PTS:]`; WIDGETS l.71 "Last ≤ 12 samples ≥ 2 s apart — about 48 s at the 4 s fetch" | confirmed |
| F-5 9999 | `:325` reached with `fetch_ts` and no `ts` (first fetch failed); sample absent → `◌ DGX ?` | confirmed |

### B.5 Per-socket-operation timeout semantics (F-6), 3.9 and 3.11

Same code path in both versions, so the semantics are identical:

1. `urlopen(…, timeout=T)` / `opener.open(url, timeout=T)` → `AbstractHTTPHandler.do_open` → `http_class(host, timeout=req.timeout)`
   (py311 `urllib/request.py:1317`; py39 `:1315`).
2. `HTTPConnection.connect` → `socket.create_connection((host, port), self.timeout, …)` (py311 `http/client.py:949-953`; py39 `:921-924`).
3. `create_connection` loops over **every** `getaddrinfo` result and calls `sock.settimeout(timeout)` then `sock.connect(sa)` for each (py311
   `socket.py:827-836`; py39 `:822-831`). So: (a) **`getaddrinfo` itself is not bounded** by T; (b) a host name with N addresses can spend N × T
   connecting. The legacy defaults are IP literals (`SL:73`, `HK:31`), so neither applies at the defaults; both apply to a configured host name.
4. The timeout stays on the socket, so every later `recv` (status line, headers, each body chunk via `_safe_read`/`_read_chunked`) is bounded
   **separately** by T.

Conclusion: F-6 **confirmed**. CONV-ABS-63 applies the consequence to T-083/T-094. The preflight `socket.create_connection(…, timeout=4)`
(`PF:23`) bounds connect only, which is the whole operation there. The `ps` call's `subprocess.run(timeout=1)` (`SL:281`) is a **total**
deadline per call.

### B.6 CONV-ABS-41..44 re-check

| Marker | Fresh evidence | Verdict |
|---|---|---|
| 41 | `SL:74-75` `float(os.environ.get("DGX_SL_TTL","4"))`, `int(…ROWS…)` at import, before the `:1238-1245` guard; the guard's own `print` can raise (EPIPE) inside the `except` | confirmed |
| 42 | B.4 F-1; `SL:356-358` applies `KEEP_DEAD` only on the fetch path; the cached path returns `c.get("sample")` at any age (`:325`) | confirmed |
| 43 | `SL:1044-1052`: first read `min(size − off, _READ_CAP)`, then `while b"\n" not in blob and off + len(blob) < size: blob += fh.read(_READ_CAP)` | confirmed |
| 44 | `PX:195-208` sets `stream` for SSE (any host) and for `/v1/messages*` only; everything else falls to mitmproxy's defaults (`m/addons/proxyserver.py:164-183`, both None) → fully buffered, uncapped | confirmed |

---

## C. Census re-run (independent script)

### C.1 Python AST

`census.py` counts every `ast.Constant` whose type is exactly `int`/`float`/`complex` (`bool` excluded). A negated literal (`-32`) counts once.

| File | Sites (round 2) | Round 1 |
|---|---|---|
| `dgx_statusline.py` | 303 | 303 |
| `dgx_proxy.py` | 70 | 70 |
| `dgx_ledger_exporter.py` | 83 | 83 |
| `auto_continue.py` | 18 | 18 |
| `dgx_preflight.py` | 5 | 5 |
| `tools/backfill_cost_history.py` | 43 | 43 |
| **Total** | **522** | **522** |

Classification by a fresh rule set (`classify2.py`) with **no default class**: a site that no rule matches is reported as UNCLASSIFIED. Result:
**T 220 · format 27 · unit 52 · incidental 223 · unclassified 0**. Round 1 had 212 / 49 / 42 / 219. The class totals differ and the tie to rows does
not:

- The two rule sets put the boundary in different places. Round 2 counts a literal as T whenever a catalogued row owns it, including the
  named-constant rows T-062/T-063 (digest and short-SHA lengths), T-070..T-073 (ledger rounding, port 80, HTTP ≥ 400) and T-080/T-081. Round 1
  counted some of those as format. Round 2 also counts `ms // 60000` (`SL:546,560`) as a unit conversion.
- Both rule sets reach **exactly the same 102 T-ids** from AST sites: 88 catalogued + T-106..T-119. Round 2's list matches round 1's
  reconciliation. The 17 catalogued rows the AST cannot reach are the same string and shell rows.
- During classification, the only literals not in round 1's T-rows turned out to be format or incidental: tuple layout (`SL:575-578,1163,1167,
  1181,1225`), JSON indent (`PX:620`), `split(None, 2)` (`SL:284`), the `"p": 1` marker (`SL:347`), exit codes, and the `mixv6: 1` marker
  (`SL:1151`). **No missing threshold** was found.

### C.2 Numeric values in string constants

`strcensus.py` found 19 string constants that parse as numbers, plus 2 bracketed PromQL durations:

- **10 threshold values** (confirms round 1): 8 numeric env defaults (`SL:74` "4" T-001, `SL:75` "2" T-002, `EX:24` "50" T-077, `EX:25` "9210"
  T-078, `HK:33` "0.40" T-082, `HK:34` "2.5" T-083, `HK:35` "14" T-084, `HK:36` "6000" T-085) and the windows `[1m]`, `[30m]` at `SL:103`
  (T-016, T-017).
- 11 sentinels, no threshold meaning: the `"0"`/`"1"` boolean defaults and comparisons (`SL:76,77`; `HK:153,156,217,228`) and `COLUMNS` default
  `"0"` (`SL:1186`, the "unknown width" sentinel used by T-116).

### C.3 Shell and plists (comments and `0`/`1` env-bool sentinels excluded)

| File | Sites |
|---|---|
| `claude-dgx` | 15: `:20` 4141, `:21` 4199, `:72` 8090, `:73` 8143, `:77` 40 and 0.25, `:85` `-m 2`, `:94` 40 and 0.25, `:104` 1800000, `:152` 0.40, `:158` timeout 5, `:161` timeout 30, `:176` padding 0 and refreshInterval 4 |
| `dgx-proxy-coordinator.sh` | 5: `:10` 8090 and 8143, `:11` 120, `:35` 40 and 0.25 |
| `io.hylo.ledger-tunnel.plist` | 4: `:8` 9210 (remote) and 9210 (local), `:9` 30, `:10` 3 |
| `io.hylo.ledger-exporter.plist` | 0 |
| **Total** | **24** (23 if the tunnel's two 9210 ports count as one site) |

Each one maps to a row (T-082, T-094..T-099, T-101, T-120, T-121). **0 unclassified.**

**Census result: 522 Python literals + 10 string values + 24 shell/plist sites, 0 unclassified. Confirmed.**

---

## D. Key-name harmonization (pass-5 deep r1, OD-01, P2r1 §6)

Rules applied, all already in force:
- Dotted snake-case keys, with a unit suffix that names the legacy unit (`_s`, `_ms`, `_bytes`, `_chars`, `_pct`, `_w`). `_ms` stays wherever
  the value is compared with Claude Code millisecond fields (P2r1 §6.2 precedent: `timer.min_ms`, `cost.rate_min_api_ms`).
- `HYLO_` + the key in upper snake case (OD-01 recommended rule, as pass-5 §A.1 applies it).
- The subsystem prefixes used by pass 5: `hook.kev.*`, `hook.english.*`, `hook.autocontinue.*`, `run.*` (settings the launcher writes into Claude
  Code), `paths.*`.

| # | Round-1 proposal | Conflict | Harmonized key (HYLO name) |
|---|---|---|---|
| H-1 | `statusline.queue.yellow_waiting_gt`* / `yellow_preempt_rate_gt`* | P2r1 §6.2 already defines `statusline.queue.yellow` as one rule | `statusline.queue.yellow` = map `{waiting_gt: 0, preempt_rate_gt: 0}`; the sparkline marker (T-107) reads `statusline.queue.yellow.preempt_rate_gt` (one rule, review #17.3) |
| H-2 | `cost.backfill.min_api_ms`* duplicating T-023's arm; T-023 map `{cc, backfill}` | two keys for one value; the arm covers every non-`cc` source (`SL:253`) | **one key**: `statusline.cost.rate_min_api_ms` = `{cc: 300000, other: 1800000}`; the backfill (`BF:35,80`) reads `.other`. `cost.backfill.days` (`HYLO_COST_BACKFILL_DAYS`) and `cost.backfill.min_usd` stay (PLAN §6 l.97 has a `cost backfill` command); `min_usd` defaults to `statusline.cost.min_usd` (both 1.0, same "skip sub-$1 sessions" intent, `SL:219`, `BF:34`) |
| H-3 | `doctor.preflight_timeout_s`* | pass 5 maps `DGX_SKIP_PREFLIGHT` to `run.preflight` (ENV-32); legacy preflight is a launcher step (`L:60-68`) | `run.preflight_timeout_s` (`HYLO_RUN_PREFLIGHT_TIMEOUT_S`); `hylo doctor` reads the same key |
| H-4 | `service.restart_delay_s`* | launchd's value is a minimum interval between spawns, not a delay (§A row 2) | `service.restart_throttle_s` (`HYLO_SERVICE_RESTART_THROTTLE_S`), documented as "minimum seconds between starts"; per-OS mapping (launchd `ThrottleInterval`; systemd `RestartSec` plus `StartLimit*`; Windows task restart interval) noted as approximate |
| H-5 | `hook.colon_fake.min_chars`*, `hook.heuristic.max_sentence_chars`*, `hook.heuristic.quote_chars`* | pass 5 groups these paths under `hook.autocontinue.enabled` (ENV-27); the colon and heuristic checks run only when `DGX_AUTOCONTINUE` ≠ 0 (`HK:228-240`) | `hook.autocontinue.colon_min_chars`, `hook.autocontinue.max_sentence_chars`, `hook.autocontinue.quote_chars` |
| H-6 | `hook.english.cjk_min_count`*, `cjk_min_count_ratio`*, `cjk_min_ratio`* | `cjk_min_count_ratio` is opaque | `hook.english.cjk_min_count` (12), `hook.english.cjk_ratio_min_count` (4), `hook.english.cjk_min_ratio` (0.02) |
| H-7 | `run.hooks.stop_timeout_s`* / `prompt_timeout_s`*, `run.statusline.refresh_interval_s`* / `padding`*, `run.api_timeout_ms`* | consistent with pass 5's `run.statusline.enabled` | unchanged |
| H-8 | `statusline.window_age.ps_timeout_s` | none | unchanged; the comment states "per call; walk uncached on failure" (CONV-ABS-62) |

Env-input count: pass 5 now lists **43** explicit inputs (ENV-01..ENV-43, adding `ARGS`). Round 1 cited the CONFIG map's "40 legacy env inputs"
(P2r1 §6.1) only as a heading. Pass-4 key mapping follows pass-5 §A.2, and no pass-4 threshold depends on `ARGS`.

---

## E. NFR catalogue changes

| ID | Change | Evidence |
|---|---|---|
| P-1 (amended) | "`ps` walk ≤ 6 × 1 s, once per session" → "**once per session when it succeeds; repeated on every refresh when no `claude` ancestor is found**, ≤ 6 × 1 s per refresh". VM fetch: per-operation 1.5 s, ≤ 3 s without dribbling. The fetch runs even when the narrow test hides row 2 (`SL:1217-1224`) | CONV-ABS-62; §B.5 |
| P-6 (amended) | Stop-hook Kev time: typical failure ≈ 2.5 s per call; strict no-dribble bound 15 s; unbounded with dribbling (Claude Code kills at 30 s). Early stop only after a slow **successful** call. The measured basis is Kev-0.8B; the deployed kev-4b is unmeasured | CONV-ABS-63; §A row 4 |
| R-8 / O-2 (amended) | Exporter crash loop: launchd spawns **at most once every 10 s** (verified), so a poison line yields one start about every 10 s | `man launchd.plist`; T-132 |
| **R-10 (new)** | **Launcher pre-trap orphan window.** mitmdump starts in the background at `L:75`; the cleanup trap is armed only at `L:97`. If the readiness wait fails (`L:77-78`, 40 × 0.25 s = 10 s), the launcher exits 1 and **leaves that mitmdump running, orphaned**. Visible mode's router failure (`L:95`) does the same. A Ctrl-C in the window orphans it **only before mitmdump installs its own SIGINT handler**; after that, mitmdump receives the SIGINT itself and shuts down (pass-1 r2 §B.3, CONV-ABS-57). hylo: moot for a per-window proxy run in-process; for PLAN §6's shared, long-lived proxy, lifecycle and detach are decided by **OD-50** and **OD-66** | `L:75-78,94-97`; pass-0 r3 §2 rows 210, 229 (C10); pass-1 r2 §B.3 |
| **R-11 (new)** | **Launcher abort on a busy router range in invisible mode.** The 4141-4199 `nc -z` scan runs before the mode split; 59 busy ports make every launch fail, although invisible mode never uses the port. Up to 59 `nc` probes per launch. hylo drops the scan (D6); a parity-era note only | CONV-ABS-61; `L:17-22` |
| S-4 (amended) | CA: RSA 2048, CA valid 3,650 d and leaf 199 d, **both back-dated 2 d**; leaf certificates **reuse the CA key pair**, signed SHA-256 | `m/certs.py:40-44,340-341,427-431,493` |
| O-1 (amended) | Exporter: HTTP/1.0, one request per connection; header limits 100 × 65,536 B (→ 431); still no socket timeout, backlog 5 | §B.1 T-129..T-131 |
| D.6 missing NFRs (added) | DNS resolution is not covered by any timeout (status line, hook) for host-name configurations; launcher cleanup not armed before the first child starts (R-10) | §B.5; R-10 |

### E.1 Updates to existing owner items (no new OD)

- **OD-56** (timeout semantics): add the measured consequences. Legacy per-operation bounds are status line ≤ 3 s and Kev ≤ 15 s per hook run
  without dribbling, unbounded with it; DNS is unbounded. With a Go total deadline equal to the legacy value, the bounds become 1.5 s and 3 × 2.5
  = 7.5 s. Recommendation unchanged (total deadline), now with numbers.
- **OD-57**: lists updated per §B.3 (17 bulk, 27 owner).
- **OD-50 / OD-66**: R-10 is the legacy evidence that a launcher-owned proxy can outlive its launcher. Attach it to both.
- T-121's live scan needs no decision: hylo drops it under D6/OD-19.

---

## Delta Summary

- New items added: NFR rows **R-10** (pre-trap orphan window) and **R-11** (launch abort on a busy router range); 1 new missing-NFR entry (DNS not
  covered by timeouts). New source details: mitmproxy watchdog mechanics (per connection, disarmed during hooks), back-dated certificates, leaf
  reuses the CA key, exporter HTTP/1.0 and header limits, `getaddrinfo` and multi-address connect outside the timeout.
- Retractions: **CONV-ABS-61** (T-121 not dead), **CONV-ABS-62** (T-026/P-1 `ps` walk not once per session; 6 s > tick), **CONV-ABS-63** (Kev 7.5 s
  is not a bound; 15 s / unbounded), **CONV-ABS-64** (T-039 asymmetry is observable).
- Verified: T-132 (launchd 10 s, as a minimum spawn interval), T-125 (199 d leaf, plus details), T-133 (executed on synthetic input), F-6 in 3.9
  and 3.11, 28 of 30 new rows confirmed outright, CONV-ABS-41..44 confirmed.
- Existing items refined: 8 threshold refinements (T-115 +1 site, T-116, T-118, T-122, T-125, T-131, T-132, T-023 arm), 3 rationale rewordings
  (T-005, T-007, T-009/F-3 bound), T-094 basis replaced; OD-57 lists 20/25 → 17/27; 8 key-name harmonizations (H-1..H-8).
- Census: re-derived independently, **522 + 10 + 24, 0 unclassified**, the same 102 AST-reachable T-ids; class split differs only at rule
  boundaries (§C.1).
- Owner items: none new (OD-70..OD-73 unused); OD-50, OD-56, OD-57, OD-66 updated.

## Remaining Gaps (verbatim-carryable)

1. Owner answers for OD-57 (lists in §B.3): bulk confirmation (17 Dv† rows) and the owner list (27 rows in 7 groups, now including T-026 and T-083 in group
   G). Until then those defaults carry "UNKNOWN — owner to confirm" in code comments.
2. T-078's "Prometheus exporter port range 9100-9999" convention could not be verified offline. Check it against the Prometheus default-port
   allocation list (a networked lookup) before it becomes the `exporter.port` comment, or relabel it "judgment".
3. Pass 5 (sibling): its PR/ENV register should state the per-operation-vs-total-deadline distinction (§B.5, ENV-22 and `DGX_SL_VM_URL`), the
   unbounded `getaddrinfo`, and that `subprocess.run(timeout=…)` is a total deadline. Cross-pass note only.
4. Whether the T-115 clamp at `SL:674` (negative sparkline values plot as 0) and the T-116 `cols > 0` trim rule need their own table tests in P1
   (CLAUDE.md "every widget rule … gets a table test"). Design note for the P1 test plan, not a catalogue gap.

## Novelty Assessment

Novelty: SUBSTANTIVE

Four round-1 statements are retracted (CONV-ABS-61..64). Each changes how a key or an NFR is specified. T-121 moves from "dead" to live launcher
behavior with an exit path. T-026's rationale and NFR P-1 were wrong about caching, and the worst case exceeds the 4 s tick. The Kev worst-case
bound behind T-083/T-094 was off by a factor of 2 without dribbling and was not a bound at all with it, which changes OD-56's numbers. T-039's
boundary is observable. A reliability NFR present in passes 0 and 1 was missing here (R-10, the pre-trap orphan window). The census and the key
harmonization, by themselves, are confirmations and nitpicks.

## Convergence Declaration

Another round needed: the four retractions and R-10/R-11 need a round-3 audit. Remaining Gaps 2-4 are open, though none is expected to change a
value.

## State Checkpoint

```yaml
pass: 4
round: 2
status: complete
timestamp: 2026-11-14T11:30:00Z
novelty: SUBSTANTIVE
files_scanned: all 11 legacy files (fresh AST census of 6 .py; shell/plist re-read; targeted reads SL:40-46,155-180,245-262,264-360,536-562,655-705,752-764,1026-1060,1196-1245; PX:186-212,686-697,718-728; HK:100-140,145-160,210-245; L:15-25,60-100,145-160; pl-ex, pl-tu); mitmproxy 12.3.1 options.py, certs.py, net/tls.py, addons/tlsconfig.py, addons/proxyserver.py, proxy/server.py, proxy/mode_servers.py, proxy/layers/websocket.py; py39/py311 socket.py, socketserver.py, http/server.py, http/client.py, urllib/request.py; man launchd.plist, man ssh_config
census: {ast_sites: 522, per_file: {SL: 303, PX: 70, EX: 83, HK: 18, PF: 5, BF: 43}, r2_split: {threshold: 220, format: 27, unit: 52, incidental: 223}, r1_split: {threshold: 212, format: 49, unit: 42, incidental: 219}, ast_t_ids: 102, string_threshold_values: 10, shell_plist_sites: 24, unclassified: 0}
audit: {new_rows_confirmed: 28, new_rows_retracted_in_part: 1, new_rows_semantic_fix: 1, rationales_hold: 24, rationales_retracted: 3, rationales_basis_replaced: 1}
retractions: [CONV-ABS-61, CONV-ABS-62, CONV-ABS-63, CONV-ABS-64]
new_owner_items: []
od_unused: [OD-70, OD-71, OD-72, OD-73]
updated_owner_items: [OD-50, OD-56, OD-57, OD-66]
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r2/
next: pass 4 round 3 (audit CONV-ABS-61..64, R-10, R-11; Remaining Gaps 2-4)
```
