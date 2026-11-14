# Pass 2 Deepening — Round 9: Domain Model (verification round: independent re-derivation of every r8 production count, ledger cross-check, open-item audit) — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Re-read this round: `dgx_proxy.py:6,86` (the `LOCAL_MODEL_PREFIXES` default).
- Authorized extra sources (read only, **counts and categories only**; IPs, ports, home paths, repository and organization names and all request
  content are masked or omitted):
  - The retained mitmdump logs `$TMPDIR/dgx-mitm.<pid>.<port>.log`: **40 files, 185,336 lines** at read time (r8: 184,943). Several are still
    appended by live proxies (8 files modified after 07:27Z), so every count was re-derived **twice**: on the full current files, and cut off at
    the r8 snapshot (r8's scratch scripts are dated 07:27:20Z to 07:32:15Z; items were time-stamped by back-computing each log line's wall time
    from the file's mtime and its last timestamp).
  - The private ledger `~/dgx-llm-obs.jsonl`: 36,355 lines, 0 unparseable, `t` from 2026-11-09 to 2026-11-14 (local time). Counts only; the one
    model name family reported comes from legacy's public default (`dgx_proxy.py:86`).
  - mitmproxy 12.3.1: not re-opened this round (r8 §5 B-1..B-3 were source checks and are not log-derived).
- Inputs read: pass-2 r8 (complete), r7 (§0-§1, §3), pass-3 r6 (header, §5-§6, delta and checkpoint). Pass-3 r6 **was present**; reconciled in §4,
  nothing edited.
- Method: nothing from legacy ran, no proxy, nothing networked, `CLAUDE.local.md` not read. Fresh scripts written from scratch in
  `scratchpad/p2r9/` (`derive.py`, `derive2.py`, `errmatch.py`), run with `/usr/bin/python3 -I`; r8's scripts were **not** read or reused.
  Each log file is read directly by path from a Python `glob` (no shell variable holding a glob, the failure class behind CONV-ABS-25). Shell
  `grep -c` on `cat $TMPDIR/dgx-mitm.*.log` used only as a cross-check.
- Numbering: CONV-ABS-27 and CONV-ABS-28 issued (§3). **No new owner item** (OD-44 not used).

---

## 1. Target A — r8's production counts, re-derived

"Snapshot" = cut off at the r8 run time (07:27:20Z for the inactivity script, 07:32Z for the HTTP/2 and SSE scripts). "Now" = full files at 07:40Z.

| # | r8 claim | Re-derived (snapshot / now) | Verdict |
|---|---|---|---|
| A1 | 57 inactivity closes (56 `tls`, 1 `alpn=http/1.1`) in 23 logs | **57** at 07:27:20Z / 60 now (59 + 1) in 24 logs. The 3 extra are three closes at 07:27:37Z, 17 s after r8's run, each an idle npm keep-alive after a `304` | **CONFIRMED** (difference = log growth) |
| A1a | All 56 idle ones: upstream `registry.npmjs.org`, gap exactly 600 s, last flow 53 × `304` + 3 × `200`, no error flow after the close | 59/59 on `registry.npmjs.org`; gap 600 s (rounded) in 59/59; last flow 56 × `304` + 3 × `200` now, so 53 × `304` + 3 × `200` at the snapshot; 0 error flows after the close | **CONFIRMED** |
| A1b | 1 in-flight cut: `mcp.atlassian.com`, `200 OK (content missing)` then `<< Client disconnected.`; `Streaming response` line about 2 h 31 min earlier | 1; same host and ALPN; flow printed after the close with `200 OK (content missing)` then `Client disconnected.`; last timestamped activity of that client **9,058 s** (2 h 31 min) before the close | **CONFIRMED** |
| A1c | None of the closes on `api.anthropic.com`, the DGX lane or the WebSocket | 0 of 60 | **CONFIRMED** |
| A2 | 119 server TLS failures: 112 `connection closed` (datadog intake 63, `downloads.claude.ai` 48, browser intake 1), 7 self-signed on a private IP; 0 on `api.anthropic.com`, 0 on the DGX | **119**: 63 (5 logs) + 48 (5 logs) + 1 (1 log) + 7 private IP self-signed (1 log); 0 on `api.anthropic.com`; 0 on the DGX. `Unable to establish TLS connection with server` lines: **119** | **CONFIRMED** (no growth) |
| A2a | Each of the 112 is followed by exactly one `<< connection closed` flow | 63 + 48 + 1 = **112** (flows: `POST …/logs` 63 + 1, `GET …/latest` 48) | **CONFIRMED** |
| A2b | The 112 are "intermittent", "about 1.9 % of connects", clustered "at the same time of day in each of the 5 affected logs (on 2026-11-10, 11-11 and 11-14)" | All 112 fall on **one afternoon, 2026-11-10, 15:13-16:57 local**, seen simultaneously by 5 proxies all started 2026-11-10 12:57-13:44 local (one of them ended at 19:49 the same day). No failure on 11-11 or 11-14; a 15:00 local event on 11-14 had not yet happened when r8 was written | **RETRACTED: CONV-ABS-27** (§3). The ratio itself re-derives (111 / 5,910 connects ≈ 1.9 %, now 5,209 + 746) but describes one ~1 h 44 min upstream episode, not a recurring rate |
| A3 | 75 client trust failures, 16 hosts, 16 logs; pypi 25 (13 logs), raw.githubusercontent 8, api.anthropic.com 8 (1 log, burst within 1 s), private IP 7, … | **75**, **16** hosts, **16** logs; per-host table identical to r8 §3.1 (pypi 25/13 logs, raw 8, api.anthropic.com 8, private IP 7, alpine 5, github.com 4, docs.nvidia 3, docker registry 3, apple 2, api.github 2, docker hub 2, nvcr 2, docker auth 1, githubstatus 1, code.claude.com 1, grafana 1). Alerts: 68 `tlsv1 alert unknown ca`, 7 `bad certificate` (the private-IP host). The api.anthropic.com burst spans **1.5 s**. pypi: 12 logs × 2 + 1 log × 1 (r8 said "two per log") | **CONFIRMED** (two wording nits, no count change) |
| A4 | 7,566 HTTP/2 flows in 25 logs: api.github 4,165, github.com 3,274, brew 51, ghcr 36, pkg-containers 17, pypi 10, others ≤ 4 | **7,566** at 07:32Z / 7,575 now (all 9 extra on `github.com`, at 07:34-07:39Z), **25** logs; host split identical (github.com 3,274 at the snapshot). Methods now: 3,871 POST, 3,704 GET. Cross-check: 15,143 lines contain `HTTP/2.0` now = 7,575 request lines + 7,568 `<< HTTP/2.0 …` response lines (pass-3 r6's "15,131 lines" is the same pair at its read time) | **CONFIRMED** |
| A4a | Exactly 2 h2 `POST /v1/messages` rerouted to the DGX (HTTP/1.1 `200`, 391 and 444 bytes); 0 other h2 flow on `api.anthropic.com` | **2**, both in one log (2026-11-13 05:08:18Z and 06:41:49Z), printed with the rewritten backend URL, answered `HTTP/1.1 200` 391 b and 444 b, each followed by `server disconnect api.anthropic.com` (the CONNECT target). h2 flows on `api.anthropic.com` otherwise: **0** | **CONFIRMED** |
| A5 | WebSocket: 8 connections, 1 log, `api.anthropic.com/api/frame/sync`, 4,202 messages (2,086 → / 2,116 ←), 2,400 pings + 2,400 pongs, ping median 20 s (max 21), per-connection 65…1,151 messages, longest 13,862 s, endings 4 ABNORMAL / 2 `4503 cap_expired` / 2 none | 8 connections (8 × `101 Switching Protocols`), 1 log; **4,202** messages (2,086 / 2,116), all `text`; **2,400 / 2,400**; ping interval median **20.0 s**, min 19.4, max 20.5; per-connection 65, 176, 194, 346, 558, 610, 1,102, 1,151; durations 763-**13,860 s**; endings 4 / 2 / 2. Bridge host lines: **0** | **CONFIRMED** (durations within the ±10 s of the start/end anchoring method; r8's 773 s minimum vs 763 s here is the same tolerance) |
| A6 | 240 streamed GETs on `/v1/code/sessions/…` in 10 logs; 216 with a duration; median 1,442 s, p90 3,565 s, max 3,600 s; 148 ≥ 600 s; endings 128 normal, 80 server EOF, 32 `Client disconnected.` | **240** GETs at 07:32Z / 241 now, 10 logs. Of the 241: **217 streamed** (`200 OK (content missing)`) and **24 buffered** (`200 OK <n>b`, no `Streaming response` line). Endings: 129 normal (105 streamed + 24 buffered), **80** server EOF, **32** `Client disconnected.`. Durations (217 streamed, each matched to the latest `Streaming response` line on the same connection, reset at every flow): min 0, **median 1,384 s**, p90 3,562 s, **max 3,599 s**, **148** ≥ 600 s | **Count CONFIRMED; qualifier and median corrected: CONV-ABS-28** (§3). Every consequence (3,600 s server cap, 148 streams outliving 600 s without an F-2 cut, HY-PASS-1) survives |
| A7 | 36 `[Errno 65] No route to host` DGX flows in one log on 2026-11-11, + 2 in a log spanning 11-10..11; 18 later `[Errno 61]` flows match the ledger's 18 | **36** in one log (started and ended 2026-11-11), all `POST /v1/messages` to the backend; **2** in the 11-10..11 log (dated 2026-11-10). `[Errno 61]`: **18** in a log from 2026-11-12, **plus 24** in two logs of 2026-11-10 (12 + 12) that r8 did not mention. Ledger join in §2.2 | **CONFIRMED**; refinement: 42, not 18, connect-refused flows exist, and the 26 failures of 2026-11-10 have no ledger trace (§2.2) |
| A8 | 17,156 client connections, all loopback; 0 lines naming `bridge.claudeusercontent.com` | 17,203 now, **0** non-loopback; **0** bridge lines | **CONFIRMED** |
| A9 | (orchestrator-supplied) 0 `error in script`, 0 `nonetype`, 1 `Addon error` | 0, 0, 1 (case-insensitive; 1 `Traceback`) | **CONFIRMED** |

**Summary of A:** every r8 count re-derives exactly at the r8 snapshot, and every difference against the current files is explained by lines
appended after r8 ran (time-stamped). Two r8 statements are wrong in their qualifier, not their count: the date/recurrence of the 112 upstream
`connection closed` failures (CONV-ABS-27) and "240 **streamed** GETs" with its median (CONV-ABS-28).

---

## 2. Target B — ledger cross-check

### 2.1 `bridge_ws_*` (closes owner check G-2)

| Event | Count in `~/dgx-llm-obs.jsonl` (2026-11-09 .. 2026-11-14) |
|---|---|
| `bridge_ws_connect` | **0** |
| `bridge_ws_close` | **0** |
| Any line containing `bridge_ws` (raw text count) | **0** |

Event inventory for reference: `anth_request` 7,207, `anth_reply` 7,183, `anth_usage` 6,942, `dgx_request` 4,755, `dgx_reply` 4,696, `dgx_usage`
4,564, `anth_ratelimit` 705, `anthropic_reply` 258, `dgx_upstream_error` 23, `anthropic_upstream_error` 22. The ledger agrees with the logs:
R0 never matched in the whole ledger period, which is longer than the log period (it starts 2026-11-09). **G-2 closed; OD-43's premise holds.**

### 2.2 The 2 rerouted h2 `/v1/messages` requests in the ledger

Both appear, each as a `dgx_request` line at Δt = 0 s from the h2 flow (and a `dgx_reply` at +0/+1 s):

| Field | Value (masked) | Contrast: surrounding Claude Code traffic in the same 4-minute windows |
|---|---|---|
| `model_req` | a `claude-sonnet*` name, i.e. it matches legacy's default `LOCAL_MODEL_PREFIXES` (`dgx_proxy.py:86`); exact string not reported | Claude Code's requests in the window ask for Opus and Haiku models and go to the Anthropic lane |
| `model_served` | set (rewritten for the backend) | — |
| `req_bytes` | **120** in both | 1,177-22,723 |
| `session` | **empty** | present on every surrounding request |
| `meta_user_id` | **empty** | present on every surrounding request |
| `project` | **empty** | present |

**Verdict:** the ledger independently corroborates r8 §3.2. These two requests carry none of the identifiers Claude Code always sends (no
`metadata.user_id`, so no session or project derivation), are tiny (120-byte bodies), ask for a model that matches the local prefix, and were
written to the ledger as **DGX-lane traffic**. Consequence for the domain model: legacy's ledger mixes **non-Claude-Code child traffic into
`dgx_request`/`dgx_reply`** with empty `session`/`project`; the status line and exporter consume these rows (2 of 4,755 in this ledger). Spec impact:
none beyond D14 (ruled); for the parity harness, a fixture with an empty `session` on a `dgx_*` row is a real legacy input, not a malformed one.

### 2.3 DGX failure flows joined to the ledger (A7 refinement)

| Log group (local date) | Flows | `dgx_request` within ±5 s | `dgx_upstream_error` within ±5 s | `dgx_reply` |
|---|---|---|---|---|
| 36 × `No route to host`, 2026-11-11 | 36 | **36** | 0 | 0 |
| 18 × `Connect call failed`, 2026-11-12 | 18 | 18 | **18** | 0 |
| 24 × `Connect call failed` (two logs) + 2 × `No route to host`, 2026-11-10 | 26 | **0** | 0 | 0 |

- The 36 of 2026-11-11 are **exactly** the 36 unpaired requests (r6 §1.4, r7 §0 O-1): request written, then neither a reply nor an error event.
  O-1's mechanism is now joined line to line.
- The 18 of 2026-11-12 are the ledger's 18 connect-refused errors (error texts re-counted: 18 `[Errno 61] Connect call failed` on 2026-11-12).
- The 26 failures of 2026-11-10 left **no ledger line at all**, although the ledger has 282 `dgx_request` lines that day, all paired with a reply.
  Under the frozen legacy copy (2026-11-14), the request hook writes `dgx_request` before forwarding, as the 2026-11-12 group shows. Most likely the
  proxies of 2026-11-10 ran an earlier script revision (judgment; the history is not in the authorized sources). No spec impact: parity targets the
  frozen copy (D4), and pairing (r4 §3.3) is unaffected. Recorded so that no later round treats the 11-10 ledger as complete for failures.

---

## 3. Retractions

| Marker | Prior claim (file) | Ground truth | Evidence | Spec impact |
|---|---|---|---|---|
| **CONV-ABS-27** | P2r8 §4 finding 3: the 112 upstream `connection closed` handshake failures are "intermittent (about 1.9 % of connects …)" and "cluster in a window of roughly 2 hours at the same time of day in each of the 5 affected logs (on 2026-11-10, 11-11 and 11-14)"; P2r8 §6 OD-41 row "112 intermittent … about 1.9 % of their connects" | All 112 are on **2026-11-10, 15:13-16:57 local**, in 5 proxies running concurrently that day. It is **one upstream episode** of about 1 h 44 min on two hosts (telemetry intake and the release check), not a recurring daily pattern. The dates "11-11 and 11-14" were most likely file modification dates, not event dates | §1 A2b (per-failure wall time back-computed from each file's mtime; all five files were created on 2026-11-10, one ended the same evening) | **None.** r8 already concluded "does not change any spec"; OD-41's recommendation is unchanged. OD-41's evidence line should read "112 `connection closed` handshake failures in one ~1 h 44 min episode on 2026-11-10" |
| **CONV-ABS-28** | P2r8 §1.2, §2.1, §7 and checkpoint: "240 **streamed** GETs" / "240 streams" on `/v1/code/sessions/…`; median **1,442 s** | 240 GETs (at the r8 snapshot), of which **216 streamed** and **24 buffered** (ordinary `200` responses with a body). Median of the streamed durations **1,384 s** when each GET is matched to the latest `Streaming response` line on its own connection with the match reset at every flow (a stale match from an earlier flow on the same keep-alive connection inflates it; the inflated method reproduces ≈ 1,441 s here). p90 3,562 s, max 3,599 s and 148 ≥ 600 s are unchanged | §1 A6 | **None.** The class "long-lived pass-through SSE up to the server's 3,600 s cap" and HY-PASS-1 stand. Pointer row "Long-lived pass-through streams" reads "216 streamed GETs (of 240)" |

---

## 4. Reconciliation with pass-3 r6

| Item | Pass-3 r6 | Agreement |
|---|---|---|
| CONV-ABS-25 (h2) | "15,131 lines (~7,566 HTTP/2 flows)" | Agrees: lines containing `HTTP/2.0` are request + response line pairs (15,143 = 7,575 + 7,568 now) |
| CONV-ABS-26 (bridge) | BC-PX-001/026 flagged "never fires in production"; BC-PX-027 flag points at `/api/frame/sync` | Agrees; now also ledger-confirmed (§2.1: 0 `bridge_ws_*`) |
| OD numbering | OD-45 issued; OD-44 reserved for pass-2 r9 | This round issues **no** owner item; OD-44 remains unused (free) |
| CONV-ABS numbering | pass 3 used 21 (22-24 unused); 25+ belong to pass 2 | This round: 27, 28. Next free: **29** |
| HY-PASS-1 | Mentioned in the header; **no BC** exists for it | Downstream note for pass 3 carried (Remaining Gaps 3) |
| BC-LN-004 flag "2 `/v1/messages` from a non-Claude-Code h2 child rerouted to the DGX" | Present | Ledger-corroborated (§2.2); the row could add "written as `dgx_request` with empty `session`/`project`" |

---

## 5. Target C — is anything in the pass-2 domain model still open?

| Item | State after r9 |
|---|---|
| Entities, ledger schema, env inputs, runtime configuration, Remote Control channels, pass-through stream class | Closed. No entity added or removed this round |
| All r8 production counts | Closed: re-derived (§1); two qualifiers corrected (CONV-ABS-27, -28), no consequence changed |
| Owner ledger check G-2 | **Closed**: 0 `bridge_ws_connect`, 0 `bridge_ws_close` (§2.1) |
| D14 rerouting evidence | Closed and ledger-corroborated (§2.2) |
| O-1 (the 36 unpaired requests) | Closed, joined line to line (§2.3) |
| Owner capture: VictoriaMetrics NaN (after the soak) | **Open**, carried, unchanged |
| Not determinable from authorized sources (LOW, no spec impact) | unchanged from r8 §8 (WebSocket message sizes; vLLM first byte; non-streaming Sonnet requests; OS connect timeout; which channel is branded "Remote Control"), plus: the cause of the 2026-11-10 upstream episode, and why 26 failures on 2026-11-10 left no ledger trace |

**Plain answer: nothing in the pass-2 domain model is open except the VictoriaMetrics capture.** Everything else is either closed with evidence
or labeled LOW and not determinable, with no effect on an entity, a schema or a hylo requirement.

---

## 6. Pointer-table delta (apply to r8 §7)

| Row | Add |
|---|---|
| Ledger schema | r9 §2.1 (0 `bridge_ws_*` in the whole ledger, G-2 closed); r9 §2.2 (`dgx_*` rows from non-Claude-Code clients with empty `session`/`project`) |
| Correlation / pairing | r9 §2.3 (36 unpaired = 36 `No route to host` flows, joined; 26 failures of 2026-11-10 with no ledger trace) |
| Error-text table | r9 §2.3 (ledger: 18 × `[Errno 61] Connect call failed` 2026-11-12; logs: 42 in total) |
| Long-lived pass-through streams | r9 CONV-ABS-28 (216 streamed of 240 GETs; median 1,384 s) |
| TLS requirements | r9 CONV-ABS-27 (the 112 upstream failures = one episode on 2026-11-10) |
| Owner-decision list | r9: no change (OD-44 unused) |
| Retractions | r9 CONV-ABS-27, CONV-ABS-28 |

---

## Delta Summary

- New items added: 0 entities, 0 contracts, 0 owner items. Ledger facts added: 3 (0 `bridge_ws_*`; the 2 rerouted h2 requests are `dgx_request`
  rows with a `claude-sonnet*` model and empty `session`/`meta_user_id`/`project`; the line-level join of the 36 / 18 / 26 DGX failure flows).
- Existing items refined: 15 r8 counts confirmed exactly at the r8 snapshot (A1, A1a-c, A2, A2a, A3, A4, A4a, A5, A6 count, A7, A8, A9, plus the
  pass-3 r6 h2 line count); 2 qualifiers retracted with no spec impact (CONV-ABS-27, CONV-ABS-28); 1 omission filled (24 more connect-refused flows
  on 2026-11-10); 3 wording nits (api.anthropic.com burst 1.5 s not 1 s; pypi 12 × 2 + 1 × 1; ping max 20.5 s not 21 s).

## Remaining Gaps

1. Owner capture, VictoriaMetrics (unchanged): one `/api/v1/query` response for the exact `QUERY` (`dgx_statusline.py:102-123`) on an idle box,
   under light load, and with fewer than 20 TTFT samples, after the DGX soak is scored. Look for `"NaN"`/`"+Inf"`/`"-Inf"` in `value[1]` per
   `__name__`.
2. Owner decisions: 42 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-43, OD-45); OD-44 unused. Wording updates for OD-41 (CONV-ABS-27).
3. Downstream note for pass 3 (not a pass-2 gap): a BC for HY-PASS-1 does not exist yet; BC-LN-004 may add the ledger corroboration (§2.2).
4. Not determinable from authorized sources (LOW, no spec impact): as in §5.

## Novelty Assessment

Novelty: NITPICK — findings are refinements, not gaps.

Every r8 count re-derives exactly at the r8 snapshot, and every drift against the current files is time-stamped log growth. Two r8 statements
are retracted (CONV-ABS-27: one 2026-11-10 episode rather than a recurring pattern; CONV-ABS-28: 216 of the 240 GETs were streamed, median
1,384 s), but neither changes an entity, a schema, a requirement or an owner recommendation: r8 already ruled the upstream episode spec-neutral,
and the stream class, the 3,600 s cap and HY-PASS-1 survive unchanged. The ledger checks close G-2 and corroborate existing findings (D14
rerouting, O-1). Removing this round's findings would not change how the system is specified.

## Convergence Declaration

Pass 2 has converged — findings are nitpicks, not gaps. (Rounds after r1: 9; the last open item is the owner's VictoriaMetrics capture, which is
an owner action, not an analysis gap.)

## State Checkpoint

```yaml
pass: 2
round: 9
status: complete
timestamp: 2026-11-14T07:46:00Z
novelty: NITPICK
files_scanned: dgx_proxy.py (6, 86); 40 mitmdump logs (185,336 lines, counts only, snapshot-cut at 07:27:20Z/07:32Z); ~/dgx-llm-obs.jsonl (36,355 lines, counts only); pass-2 r7, r8; pass-3 r6
retractions: [CONV-ABS-27 (112 upstream TLS failures = one 2026-11-10 episode, not recurring), CONV-ABS-28 (240 GETs: 216 streamed + 24 buffered; median 1,384 s)]
conv_abs_next_free: 29
new_owner_items: none (OD-44 unused)
ledger: {bridge_ws_connect: 0, bridge_ws_close: 0, rerouted_h2_as_dgx_request: 2 (model claude-sonnet* family, req_bytes 120, session/meta_user_id/project empty)}
open_items: [VictoriaMetrics owner capture]
```
