# Pass 2 Deepening — Round 5: Domain Model (LAN-exposure model, catalogue/schema re-verification, final owner-decision list) — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Re-read this round: `dgx_proxy.py:1-560` (whole routing addon),
  `dgx_ledger_exporter.py` (whole file), `claude-dgx:70-80,97`, `dgx_statusline.py:217-253,274-358,405,952-1056,1148-1153`,
  `dgx_preflight.py:15-30`, `dgx-proxy-coordinator.sh:20-40`, `auto_continue.py:124-134,246`.
- Authorized extra sources (read only, never imported or executed): **mitmproxy 12.3.1** `addons/block`, `addons/proxyserver:376-396`,
  `options:90-100`, `proxy/layers/http/__init__:225-262`. The venv's base interpreter **CPython 3.12.10** stdlib `ipaddress.py` (to pin
  mitmproxy's admission rule). **Python 3.9 stdlib** (CommandLineTools framework, the `/usr/bin/python3` family the exporter runs on, r2/OD-15)
  `socketserver.py`, `http/server.py`. **dgx-llm `deploy/recording.yml`** (cited by repo-relative name).
- Inputs read: every file in this directory, especially pass-2 r1-r4 and **pass-3 round 3** (`…-pass-3-deep-behavioral-contracts-r3.md`, which
  now exists: read, reconciled in §0.3, not edited). `docs/PLAN.md` D13-D16.
- Method: static reading only. Nothing from legacy ran, no proxy, nothing networked. `CLAUDE.local.md` was not read. Scratch dir
  `scratchpad/p2r5/` created and left empty (no execution needed).
- Addresses in examples are RFC 5737 (`192.0.2.x`). A bare `:N` means `dgx_proxy.py` unless the section says otherwise; `EX:N` =
  `dgx_ledger_exporter.py`, `SL:N` = `dgx_statusline.py`.
- Retraction numbers: the highest used so far is 12 (pass 2 used 1-6 and 12; pass 3 used 6, 7, 8). This round uses **CONV-ABS-13** and **-14**.
  Pass 3's 9-11 stay free.

---

## 0. Evidence recorded, owner ruling, reconciliation

### 0.1 Orchestrator evidence (local, read-only, 2026-11-14) and the r4 gaps it closes

| r4 gap | Evidence | Verdict |
|---|---|---|
| **2** client protocol | 38 mitmdump logs in `$TMPDIR`: **0** lines containing ` HTTP/2.0` | **Closed. Claude Code talks HTTP/1.1 to the proxy.** The r4 §1.3 **HTTP/1.1 row** is the production row: a DGX connect failure gets a 502 and the client connection closes, so the cached `connection.error` is never served twice. **The HTTP/2 sticky-failure mode is not live in production.** The 18 connect-refused `dgx_upstream_error` events are 18 separate connect attempts, not cached repeats. This independently corroborates pass-3 r3 BC-PX-044 consequence 2, which inferred HTTP/1.1 from the `Client disconnected.` wording (`_http1:142` vs `_http2:266-268`). The h2-to-h1 per-flow connection accumulation (r4 §1.3) is also not live. HIGH (log evidence + source) |
| **3** import-failure pass-through | same logs: **0** `error in script`, **0** `nonetype` | **Closed as "not observed".** The plain pass-through state (failed reload, r4 §2.1 D-2) has not happened in the retained logs. It stays **possible** (source-confirmed for reloads; the 1 observed `NameError` shows that mid-edit reloads reach running proxies). OD-26 stays as a hylo design rule, not a parity item |
| **4** `peer closed` attribution | not attempted (orchestrator instruction) | **Closed as LOW impact, unknown.** Also, r4's test for it was unsound (CONV-ABS-14): empty attribution would not have identified the side |
| **5** host firewall | `lsof`: **9** legacy proxies (`python3.12` mitmdump) listening on `*:8090` … `*:8098` (all interfaces, IPv4 + IPv6); the exporter (Python) on `*:9210`. macOS application firewall **disabled**, stealth mode off | **Closed. OD-24 and OD-27 are CONFIRMED LIVE in production.** The precise exposure model is in §1 |
| r3/r4 "Sonnet on Anthropic unpriced" (rule side carried) | `deploy/recording.yml` read this round | **Verified, wording sharpened** (§2.3 C-9) |

### 0.2 Owner ruling (2026-11-14, relayed by the coordinator) on OD-24 / OD-27

> The owner accepts the LAN exposure of the **live legacy** proxies and exporter until cutover ("not a risk I'm worried about right now").

Recorded as: **OD-24 and OD-27, legacy side: live risk accepted by owner; no change to legacy.** For hylo the requirement stands as a
**default, not a pending decision**: the proxy and the UI API bind to loopback by default, and a non-loopback bind is opt-in configuration (D15)
that triggers a warning (§1.4). Both items move down the risk ranking (§3.3).

### 0.3 Reconciliation with pass-3 round 3 (read, not edited)

| Topic | Pass-3 r3 | This pass | Status |
|---|---|---|---|
| Client protocol | inferred HTTP/1.1 from the `Client disconnected.` text | now log-confirmed (0 ` HTTP/2.0` lines) | **agree**, upgraded to observed |
| Error-cause table (BC-PX-044) vs r4 §1.3 | 4 causes plus the "client closes after completion" row, exact texts | same texts, same source lines | **agree**. Pass-3 adds that a client cancel also closes the upstream connection (`__init__:736-738`), which pass 2 had not recorded. Accepted |
| `anthropic_upstream_error` count | 21 | r4: 21 | **agree** (r3's 20 was an older snapshot) |
| `anthropic_upstream_error` meaning | "current name" for the Anthropic lane | **refined**: written for **any non-DGX host** whose path starts with `/v1/messages` (CONV-ABS-14) | pass 3 should note this in its next round |
| CONV-ABS numbering | P3 CONV-ABS-8 = "legacy never crashes" retraction (CP-T05) | crosswalk below | **agree** |
| Owner items | 10 (5 carried, 5 new: #6-#10) | r4 had only the carried ones (pass-3 r3 did not exist then) | **#6-#10 added as OD-28..OD-32** (§3) |
| P-S4 exceptions (empty SSE body; `~/.mitmproxy/config.yaml`) | new | the same config file could also override `listen_host`, `block_private` or `proxyauth`. The orchestrator's `lsof` shows the all-interface bind is in effect; whether `proxyauth` is set is part of pass-3 r3 gap 1 | **agree**, scope widened (§1.1) |

CONV-ABS crosswalk (extends r4 §0.3):

| Number | Pass 2 | Pass 3 |
|---|---|---|
| 1-5 | r1/r2 (see r4 §0.3) | — |
| 6 | r3: `rotate` crash scope | r2: CP-T predicates too broad |
| 7 | — | r2: `rotate` / `args.force` (alias of P2-6) |
| 8 | — | r3: CP-T05 "legacy never crashes" |
| 12 | r4: no plain-proxy state at launch | — |
| **13** | **r5: exporter state miscount** | — |
| **14** | **r5: the empty-attribution test for `*_upstream_error`** | — |

---

## 1. Target A — the LAN-exposure model (OD-24 / OD-27), precisely

### 1.1 Admission: who can connect

| Fact | Source |
|---|---|
| Bind: `listen_host` defaults to `""` = every interface, IPv4 and IPv6. The launcher sets only `--listen-port`. Observed live on `*:8090-8098` | mitmproxy 12.3.1 `options:94-99`; `claude-dgx:75`; orchestrator `lsof` |
| Admission runs at `client_connected`. **Loopback is always admitted.** `block_private=False`: private sources admitted. `block_global=True`: sources with `is_global` refused | mitmproxy 12.3.1 `addons/block:8-48` |
| `is_private` (CPython 3.12.10) covers **10/8, 172.16/12, 192.168/16, 169.254/16** (IPv4 link-local), **fc00::/7** (ULA), **fe80::/10** (IPv6 link-local), and the documentation ranges. All of these are **admitted** | `ipaddress.py:1580-1595,2340-2354` |
| **100.64.0.0/10** (CGNAT, also used by overlay VPNs such as Tailscale) is **neither private nor global**, so **admitted** | `ipaddress.py:1361-1375,1556-1566` |
| An IPv6 **global** source (2000::/3) is refused **even from the same LAN segment**. IPv4-mapped IPv6 is judged by its IPv4 address | `addons/block:30-33,44-48` |
| No proxy authentication is passed by the launcher. A user-level `~/.mitmproxy/config.yaml` could add one; that file is outside the repo (pass-3 r3 gap 1). The orchestrator's statement "unauthenticated" is consistent with the launcher, not separately verified | `claude-dgx:75` |
| The exporter binds `("0.0.0.0", PORT)` with `HTTPServer`, which is `AF_INET`: **IPv4 only, no source filter of any kind** (no `block_global` equivalent) | `EX:414`; Python 3.9 `socketserver.py:437` |
| Exposure window: a proxy port is open only while a `claude-dgx` window runs (9 at capture time; range 8090-8143, `claude-dgx:72-73`). The exporter is **always** listening (launchd `KeepAlive` + `RunAtLoad`, r4 §0.1) | as cited |

### 1.2 What a LAN client can do

| # | Capability and mechanism | Source |
|---|---|---|
| L1 | **Run inference on the owner's backend using the owner's key, with no TLS and no CA trust.** A plain-HTTP, absolute-form request through the proxy, `POST http://api.anthropic.com/v1/messages` with a body whose `model` starts with a local prefix (default `claude-sonnet`) and declares no server tool, takes route R5. The proxy switches scheme/host/port to the backend and sets `Authorization: Bearer <owner key>`. The backend's reply, streamed, goes back to the sender. Over CONNECT + TLS it works too: the sender only has to skip verification of the forged leaf, which is signed by the owner's mitmproxy CA | regular mode takes the host from the absolute-form request line, then sets origin form (`proxy/layers/http/__init__:225-261`). Routing `:103,132-141,161-164` |
| L2 | **Write attributed lines into the owner's ledger and metrics.** `X-DGX-Project`, `X-DGX-User` and `X-Claude-Code-Session-Id` are whatever the sender sends. They land in `dgx_request`/`anth_request` and following events, in the exporter's labels, and (DGX lane) in the `X-DGX-*` headers the backend logs | `:117-127,156-159`; `EX:136-203` |
| L3 | **Break the owner's metrics persistently with one request.** A DGX-lane body with `metadata.user_id` = the string `{"account_uuid": 1}` writes a `dgx_request` line whose `meta_user_id` crashes the exporter's `_account_device` (`(1 or "unknown")[:8]` → TypeError, E-08). After that line is in the ledger, **every scrape fails**: `do_GET` calls `rebuild()` because the size changed, `rebuild` raises before `processed_size` is updated, so the next scrape rebuilds and fails again. A restart puts it in the launchd crash loop (OD-11). The append-only ledger keeps the line forever. A list-valued `account_uuid` does the same through E-06. Claude Code itself never sends these shapes; only a crafted sender does | `EX:75-91,184-186,280-287`; r2 E-06/E-08; `EX:411` |
| L4 | **Load the backend**, slowing the owner's sessions. The owner's DGX telemetry and the exporter's `last_dgx_request` series show the sender's activity as the owner's | routing as L1 |
| L5 | **Use the Mac as a general forward proxy** to any `host:port` the Mac can reach, egressing from the owner's address. **This includes the Mac's loopback-only services:** the only destination mitmproxy refuses is its **own** listen port (self-connect guard). All TLS is intercepted with the owner's CA (the sender skips verification) | mitmproxy 12.3.1 `addons/proxyserver:376-396`; no destination filter in `addons/block` |
| L6 | **Write to the owner's disk**: unbounded ledger and decision-log growth; failed-request captures by sending bodies the backend rejects with status ≥ 400 (newest 20 kept, each under 50,000,000 characters, so on the order of 1 GB at most). Ledger growth also raises the exporter's full-rescan cost on every scrape | `:56-62,65-74,283-297`; `EX:280-287` |
| L7 | **Exporter (`*:9210`):** read every label (project, user, model, 8-character account/device/session prefixes, token and timing totals); force full rebuilds with `?rebuild=1`; **stall it indefinitely with one idle TCP connection** (new failure mode F-1, §2.4) | `EX:270-287,414` |

### 1.3 What a LAN client cannot do

| # | Not possible, and why | Source |
|---|---|---|
| N1 | **Read the backend key's value through the proxy.** The key exists only as a request header on the proxy-to-backend leg. Nothing echoes it: the reply comes from the backend, the failed-request capture stores the **body only**, and the decision log never prints headers. *Caveat (separate, already pass-4):* the default backend transport is **plain HTTP**, so any host that can observe the Mac-to-backend path sees the key on every DGX-lane request, whatever the bind | `:164,286-297`; pass 4 security gap (`dgx_proxy.py:79,164`) |
| N2 | **Use the owner's Anthropic account.** The proxy never adds Anthropic credentials. Anthropic-lane requests go out with whatever the sender supplied (OAuth lives in Claude Code, not in the proxy) | `:132-141` (no header writes on these branches except `Accept-Encoding`, `:131`) |
| N3 | See the owner's own flows, ledger, transcripts or caches through the proxy or exporter (no read API; the ledger is not served; the exporter serves aggregates only) | `:98-323`; `EX:270-404` |
| N4 | Connect from a public IPv4 or a global IPv6 source | `addons/block:44-48` (proxy only; the exporter has no such filter, but behind NAT with the firewall off it is still reachable only from routable LAN or VPN peers) |
| N5 | Change the status line directly. It reads stdin and VictoriaMetrics; LAN senders affect it only through exporter series (L2-L4, L7) and backend load | r3 §4.1; `SL:824` |

**Severity.** OD-24 (proxy): **HIGH** in the abstract. Unauthenticated use of the owner's backend credential (L1), a one-request persistent
outage of the metrics pipeline (L3), and a pivot to loopback-only services (L5). OD-27 (exporter): **MEDIUM**. Label disclosure, rebuild
amplification, indefinite stall (L7). **Both are accepted by the owner for legacy until cutover** (§0.2), so neither is in the top risk set (§3.3).

### 1.4 hylo's required behavior (D13, D15, D16) — a default, not a pending decision

| ID | Requirement | Basis | Table tests |
|---|---|---|---|
| HY-BIND-1 | `hylo proxy` binds `127.0.0.1` by default (the address `HTTPS_PROXY` points at; legacy also probes and exports `127.0.0.1`, `claude-dgx:73,79`). The port follows the P4 listener design (OD-19) | owner ruling 2026-11-14; D13 does not set a bind, so this fills that gap | default config → listener address is loopback; a connection from `192.0.2.20` gets no service |
| HY-BIND-2 | The D16 event API and `hylo ui` bind loopback with the per-launch access token (already in D16) | D16 guardrails | as above, plus token required |
| HY-BIND-3 | A non-loopback bind is **opt-in configuration** (e.g. `proxy.listen_host`, `ui.listen_host`; D15 key names per OD-01). When it is set, hylo prints a **warning** at startup on stderr, emits a config/warning event on the D16 feed, and `hylo doctor` reports it. The warning names the consequence: "any host that can reach this address can use your backend credentials" | D15; owner ruling | `listen_host: 0.0.0.0` → warning text present on stderr and on the event feed; loopback → no warning |
| HY-BIND-4 | Defense in depth: the client-admission check is separate from the bind. Even with a wider bind, non-loopback peers are refused unless an explicit allow-list (config) admits them. This replaces mitmproxy's `block_global`/`block_private` pair with one explicit rule | L1-L6; mitmproxy's rule admits RFC 1918, link-local, ULA and 100.64/10 by default | peer `192.0.2.20` refused by default; admitted only when listed |
| HY-BIND-5 | **Exporter (P2)**: bind loopback by default under the same opt-in-plus-warning rule. The deployed scrape path is `ssh -R` loopback-to-loopback (`deploy/io.hylo.ledger-tunnel.plist:7`), so loopback loses nothing. The owner ruling names the proxy and the UI API; extending it to the exporter is carried from r4's OD-27 recommendation and is marked **for owner confirmation** in OD-27 | r4 §2.2; OD-27 | default → `127.0.0.1:9210`; exposition bytes unchanged (bind is not part of D7) |
| HY-BIND-6 | Every hylo HTTP listener (proxy, UI API, exporter) sets read-header and idle timeouts and serves connections concurrently, so one idle client cannot stall it (F-1, OD-33) | §2.4 | an idle connection held open does not delay a concurrent `/metrics` scrape |

Loopback is not authentication: on a multi-user host any local account can still use a loopback proxy (L1, L5). Whether hylo adds a per-launch
proxy credential is a new pending decision (OD-34). It is not implied by the ruling.

---

## 2. Target B — re-verification of r4's catalogue and ledger schema

### 2.1 Spot-check (33 rows checked against source)

| # | r4 row / claim | Verdict | Source |
|---|---|---|---|
| 1 | Ledger writer contract: `open(…, "a")`, one `json.dumps(...) + "\n"`, `OSError` swallowed, `t` = local `%Y-%m-%dT%H:%M:%S` at write time | ✓ | `:56-62` |
| 2 | #1 `dgx_request` field order `project, user, session, meta_user_id, model_req, req_bytes, path, model_served` | ✓ (`model_served` = raw `req.get("model")`, equal to `model_req` on this lane, since R5 needs a truthy string) | `:117-127,143-154` |
| 3 | #1 `req_bytes` = characters of the **original** body (taken before normalization) | ✓ | `:123,145-150` |
| 4 | #2 `dgx_reply` = `status, duration_s`, then `_dgx`, then `in_tok, out_tok` iff tap usage, `stream_stop_reason` iff tap stop | ✓ | `:259-274` |
| 5 | #2 `_dgx` absent → only `status, duration_s ≈ 0.0` | ✓ | `:256,273` |
| 6 | #2 `in_tok` = whole prompt (uncached + cache read + cache write) | ✓ | `:267-268` |
| 7 | #3 `dgx_usage` fields and the conditional `cache_read_tok` | ✓ | `:275-282` |
| 8 | #4 `dgx_upstream_error` = `error[:300]` + `_dgx` (or `_attrib`) minus `error` | ✓ | `:316-323` |
| 9 | #5 `anth_request` = `_attrib` + trailing `lane` (`anthropic` / `anthropic-server-tools`) | ✓ | `:132-141` |
| 10 | #6 `anth_reply` = `_attrib`, `status, duration_s`, token fields iff `in_tok is not None`, then the cache dict | ✓ order. **Variant missing** → C-1 | `:236-245` |
| 11 | #7 `anth_usage` field order (`lane` default `anthropic`, …, `model` = `model_req`) | ✓ | `:247-253` |
| 12 | #7 `cache_write_5m_tok` build defect | ✓ that it exists and that the derivation is right; **window and mechanism refined** → C-2 | `EX:172-178`; tap comment `:373-376` |
| 13 | #8 `anthropic_upstream_error` trigger "request host ≠ DGX host" | ✓ literally. **Meaning refined** → CONV-ABS-14 | `:316,319` |
| 14 | #9 `anth_ratelimit` = `session, headers`, logged on change per session per process, reset by reload | ✓. Refinement C-4 | `:176-190` |
| 15 | #10 `bridge_ws_connect` = `host`, only on a websocket upgrade | ✓ | `:100-102` |
| 16 | #11 `bridge_ws_close` "at the 101 upgrade response" | **incomplete** → C-3 | `:211-214` |
| 17 | #12 `ws_closed` dead (`_ws_started` never set) | ✓ | `:528-536` |
| 18 | #13 `anthropic_reply` aliased to `anth_reply` in the exporter | ✓ | `EX:204-207` |
| 19 | Exporter `anth_req` key `(project, user, model_req, account)` and account always `unknown` | ✓ (`anth_request` has no `account` field) | `EX:160-163` |
| 20 | Exporter `est_prompt` = `req_bytes/4` iff numeric > 0 | ✓ (a `bool` `true` also passes, 0.25 tokens; synthetic only) | `EX:190-193` |
| 21 | Exporter `dgx_upstream_error` → `errors` only, not session errors, no session creation | ✓ | `EX:138,208-210` |
| 22 | Exporter `dgx_reply` status ≥ 400 → errors; non-numeric status crashes (E-07) | ✓ | `EX:200-203` |
| 23 | Exporter "15 keyed accumulators" | **miscount** → CONV-ABS-13 | `EX:28-61` |
| 24 | Exposition "27 metric families" | **ambiguous** → C-5 | `EX:289-398` |
| 25 | Exporter bind `0.0.0.0:9210`, `/metrics` only, `text/plain; version=0.0.4` | ✓ (port from `DGX_LEDGER_EXPORTER_PORT`; host not configurable; IPv4 only) | `EX:25,272-273,401,414` |
| 26 | Fake-stop tally order kev-continue, kev-allow, kev+opus, colon, heuristic; `p_done_latest` = last line's first match | ✓ | `EX:217-234` |
| 27 | Exporter rebuild before bind | ✓ | `EX:410-414` |
| 28 | Composite near-key `(session, path, model_req, req_bytes)` + `reply.t − duration_s ≈ request.t` | ✓. **Extends to the Anthropic lane** → C-6 | `:236-238,256,272-274,318-323` |
| 29 | SSE tap: `KEEP = 64_000`, usage only from a top-level `usage` with `input_tokens`, cache maxima from both levels, stop from `delta` | ✓ | `:368,412-427` |
| 30 | Failed-request capture: body only, newest 20, < 50,000,000 chars, lost on P-S4 | ✓ (pruning to 19 runs **before** the size test, so an oversized body still prunes; directory is `Path.home()`, not configurable) | `:283-299` |
| 31 | Proxy listener port range 8090-8143, probe on `127.0.0.1` | ✓ | `claude-dgx:72-79` |
| 32 | Mix cache 16 keys incl. `mixv6`, `ids` last 256; transcript window 512 KB (`_READ_CAP = 524288`); git cache key `sha1(dir)[:16]`; session-cache keys `rl, rl_ts, fetch_ts, up, ts, sample, hist, proc_start` | ✓ | `SL:1150-1153,952,405,274-358` |
| 33 | Preflight 4 s TCP connect, port default 80; coordinator `.proxy-state`; Kev median of up to 3 with early stop | ✓ | `dgx_preflight.py:18-23`; `dgx-proxy-coordinator.sh:20-38`; `auto_continue.py:124-134` |

Result: 26 rows confirmed as written, 2 retractions, 5 refinements. No phantom entity, no wrong field order, no wrong emitter line.

### 2.2 Retractions

| Marker | Prior claim (file) | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-13** | r4 §3.1 "Rebuild state: **15** keyed accumulators" (hallucination class 2, miscount) | The exporter holds **19 keyed `defaultdict` accumulators** (`req_totals, est_prompt, dur_sum, dur_count, errors, tok_in, tok_out, anth_req, anth_in, anth_out, anth_ds, anth_dc, anth_rqs, anth_cr, anth_cw5, anth_cw1, anth_cache_cov, dgx_cr, dgx_in_cap`), **3 dict states** (`sess_meta`, `sess_stats`, `fakestop`) and **5 scalars** (`passthrough, last_ts, last_dgx_ts, last_anth_ts, processed_size`): 27 module-level state objects. Never emitted: `anth_rqs` (accumulated, no exposition line; known since r2). Emitted but always 0: `anth_ds/anth_dc`. The rebuild-local `sess_proj` is dead | `EX:28-61,183,254,289-398` |
| **CONV-ABS-14** | r4 §1.3 error-string table: "an event with **empty attribution would mean the client side** (the `request` hook never ran)"; r4 Remaining Gap 4 built on it | **Empty attribution does not identify the side.** `error()` writes `<lane>_upstream_error` for **any** flow whose path starts with `/v1/messages`, with `lane = "anthropic"` for **every non-DGX host** (`:316,319`). Attribution is empty when (a) the request hook never ran, (b) it ran but returned before `_attrib` was set: unparseable body (`:105-109`), non-object JSON (`:110-111`), or a host other than `api.anthropic.com` (`:103`). So **`anthropic_upstream_error` means "a non-DGX host", not "Anthropic"**: through the proxy (any local process or, in legacy, a LAN client, L5) a failing `/v1/messages*` request to any third-party host is logged as an Anthropic error. Claude Code itself sends `/v1/messages` only to `api.anthropic.com`, so the 21 production events are very likely Anthropic; the name is still wrong in general. Gap 4 is closed as LOW/unknown regardless (§0.1) | `:98-111,311-323` |

### 2.3 Corrections and refinements (r4 is not edited; these supersede the cited rows)

| ID | r4 location | Correction | Evidence |
|---|---|---|---|
| **C-1** | §3.2 row 6 `anth_reply` | `anth_reply` carries the **same** `cache` dict as `anth_usage` (`cache = dict(tap.cache)` then `ev.update(…, **cache)`), so lines from the defective builds have the wrong `cache_write_5m_tok` **on `anth_reply` too**. No legacy consumer reads cache fields from `anth_reply`. The r4 reader rule "derive 5m cache writes" now names **both** events | `:221-224,242-245` |
| **C-2** | §3.2 row 7 defect wording "proxy builds of 2026-11-12" | Window: builds **deployed with the change at 13:31:52 on 2026-11-12, until its fix** (exporter comment; the defective code is not in the repo). Mechanism (tap comment): `message_delta` repeats the write total without a TTL split; the old code applied the "no split → 5m" default per field and merged by maximum, so **5m = total** while **1h stayed correct** (live example: 5m = 949 and 1h = 949 for 949 written). Therefore `5m = write − min(1h, write)` is **exact** for those lines, not an approximation. MEDIUM (from comments, defective code absent) | `EX:172-178`; `:373-376` |
| **C-3** | §3.2 row 11 `bridge_ws_close` | Fires on **every** `response` for host `bridge.claudeusercontent.com`, whatever the path or upgrade. `bridge_ws_connect` fires only for upgrades. So `bridge_ws_close` counts **bridge HTTP responses** (the 101 included), not WebSocket closes, and the two events do not pair. Unconsumed except for `last_ts` | `:100-102,211-214` |
| **C-4** | §3.2 row 9 `anth_ratelimit` | Runs for **every** `api.anthropic.com` response, not only `/v1/messages*`. Flows without `_attrib` (other paths, R2) log `session: null`, and all of them share one change-detection slot (`_last_rl[None]`) | `:177-188` |
| **C-5** | §3.1 Exposition "27 metric families" | The code declares **28 metric names**. 27 can carry samples: `dgx_llm_session_tokens` has HELP/TYPE but no samples. 3 are conditional: `last_dgx` iff > 0, `last_anthropic` iff > 0, `p_done_latest` iff not None. A reference parser sees 47 families because of detached metadata (pass-3 r3 BC-EX-025) | `EX:289-398` |
| **C-6** | §3.3 correlation | The composite near-key also works on the **Anthropic lane**: `anth_reply` and `anthropic_upstream_error` copy `_attrib` (with `req_bytes`, `path`, `session`, `model_req`), and `duration_s` is measured from the same `_t0`. **Replies without a request exist**: R2 flows (no `_attrib`, no `anth_request`) and P-R1..R3 flows (`_attrib` set at `:117`, the raise comes before the `anth_request` write at `:134`). Reader rule added: **never assume a reply has a request** (in addition to r4's "never assume a request has a reply") | `:117-141,236-245,318` |
| **C-7** | §2.2 / §3.1 proxy listener "LAN clients accepted" | Precise admission (§1.1): RFC 1918, IPv4/IPv6 link-local, ULA and **100.64/10** admitted; **IPv6 global sources refused even from the LAN**. "Reachability depends on the host firewall" is **resolved**: the firewall is disabled, so reachability is confirmed | §1.1 |
| **C-8** | §2.2 "matches the exporter's `0.0.0.0:9210` exposure" | The exporter is **IPv4 only** (`AF_INET`) and has **no source filter**, so its admission is wider than the proxy's for IPv4 (public IPv4 sources would be served if routable) | `EX:414`; `socketserver.py:437` |
| **C-9** | §0.2 / OD-13 "Sonnet on Anthropic unpriced" | **Rule side verified.** The Anthropic spend rules match **exact model labels only**: `model="claude-opus-5-5"` and `model="claude-haiku-5-5"` (`recording.yml:100-113`); total spend sums those two (`:121-123`). **Every** other model on the Anthropic lane, Sonnet included and also any dated or variant id of Opus/Haiku, is absent from spend and counted by `dgx_cost:anth_unpriced_requests_24h` (`model!~"claude-(opus\|haiku)-5-5"`, `:151-156`). The `dgx_price:sonnet_*` constants (`:222-224`) feed only the DGX displaced-cost basis (`:259-261`). Correct wording: "**unpriced** by exact-label matching: absent from the spend sums and counted as unpriced requests" | `deploy/recording.yml` as cited |
| **C-10** | §1.3 "which row applies is UNVERIFIED" | Resolved: the HTTP/1.1 row (§0.1). OD-17's rationale drops the h2 sticky mode as a live behavior; the deviation itself is unchanged | §0.1 |

### 2.4 New failure mode F-1: one idle connection stalls the exporter indefinitely

| Fact | Source |
|---|---|
| The exporter serves with `HTTPServer(...).serve_forever()`: the synchronous `TCPServer`, **not** `ThreadingHTTPServer`. One request at a time | `EX:414`; Python 3.9 `http/server.py:132,144`; `socketserver.py:215-237,390` |
| `StreamRequestHandler.timeout = None`, so no socket timeout is set | `socketserver.py:783-793` |
| `handle_one_request` blocks on `self.rfile.readline(65537)` for the request line | `http/server.py:393-402` |
| **Consequence:** a client that opens a TCP connection to `:9210` and sends nothing (or a partial request line) **blocks every later scrape** until it closes. No error is logged. VictoriaMetrics' scrape over the tunnel times out, and every exporter series stops updating, including `dgx_llm_last_dgx_request_timestamp_seconds`, the one the status line's idle indicator uses (`SL:824`) | combination of the above |
| Triggers: any LAN host (L7, legacy only), any local process, or a browser's speculative preconnect when someone opens `/metrics` in a browser (plausible, unverified). Port scanners that connect and close right away do **not** trigger it (`readline` returns empty) | judgment, labeled |
| Not in any prior pass (r2 §5.2 covers exceptions in `do_GET`, which close the connection and continue; the pass-4 NFR catalogue lists the rescan cost only) | search of all pass files |

Parity: this is a failure mode, not exposition bytes, so D7 is untouched. hylo requirement HY-BIND-6; owner item OD-33.

### 2.5 Candidate explanation for the 36 unpaired DGX requests (hypothesis, not verified)

The launcher kills mitmdump on `EXIT INT TERM` (`claude-dgx:97`), and closing a terminal window signals the process group. A flow still in
flight when its proxy dies writes neither `dgx_reply` nor `dgx_upstream_error`. That matches "request with no reply and no error", unlike
every hook-level path catalogued so far. P-S1..S4 all run after `dgx_reply` or only on the Anthropic branch. Whether mitmproxy's shutdown fires
`error` for open flows was **not checked**. MEDIUM-LOW, static. It does not change the schema. It gives the P3 replay a likely classification
("orphaned by proxy exit") for requests whose session ends at the same time.

---

## 3. Target C — final owner-decision list

### 3.1 Audit of r4's 27

- **Duplicates:** none among OD-01..OD-27. OD-06 (unreadable key → client credentials to the backend) and OD-07 (client credentials always
  forwarded on the DGX lane) are distinct triggers with one shared fix. They stay separate because OD-06 also involves fail-closed behavior.
- **Misattribution:** OD-07's "consistent with D16's guardrail" stretches D16. D16's "never stored or forwarded" governs the UI and event feed,
  not the proxy's upstream requests. Recommendation reworded below. OD-17's rationale cited the h2 sticky mode as live; now known not live (C-10).
  OD-13's "Sonnet on Anthropic unpriced" now carries the exact-label wording (C-9).
- **Missing:** pass-3 r3's new items **#6-#10** (r4 could not see them) → OD-28..OD-32. New this round: OD-33 (F-1), OD-34 (loopback is not
  authentication). Pass-3 r3 #1-#5 were already merged: #1 → OD-21, #2 → OD-16, #3 → OD-18, #4 → OD-22, #5 → OD-23.
- **Ruled:** OD-24 and OD-27, legacy side (§0.2).

### 3.2 Final list (OD-01..OD-34)

Status: **P** = pending owner decision; **R** = ruled. Phase codes per `docs/PLAN.md`.

| ID | St | Decision | Component | Bites | Origin | Recommendation (one line) |
|---|---|---|---|---|---|---|
| OD-01 | P | CONFIG key naming and the `HYLO_*` derivation rule | config | P1 | P2r1 #1 | Derive mechanically: `HYLO_` + upper-snake of the dotted key. |
| OD-02 | P | Status line glyphs as config | status line | P1 | P2r1 #2 | `statusline.glyphs.*` with legacy defaults. |
| OD-03 | P | Windows sanitizing of session ids in cache file names | status line | P1 | P2r1 #3 | Sanitize on Windows only. |
| OD-04 | P | One `paths.hook_log` key for hook (writer) and exporter (reader) | hook, exporter | P2, P4 | P2r1 #4 | One key, legacy default path. |
| OD-05 | P | Env-bool grammar for `DGX_*` aliases | config, launcher | P1, P4, P6 | P2r2 #5 | Legacy per-variable rules for `DGX_*`; typed booleans for `HYLO_*`. |
| OD-06 | P | P-R4: unreadable backend key → client credentials sent to the backend | proxy | P3 | P2r2 #6, P2r3 E-1 | Approved deviation: fail closed (local 502 + error event). |
| OD-07 | P | Client `x-api-key`/`Authorization`/cookies forwarded on every DGX-lane request | proxy | P3 | pass 4, P2r3 #7 | Approved deviation: strip client credentials before adding the backend key (the same credential hygiene D16 applies to the UI). |
| OD-08 | P | P-R1..R3 silently re-lane a would-be DGX request to Anthropic | proxy | P3 | P2r2 #7 | Reproduce in replay; hylo also emits a routing-error event. |
| OD-09 | P | Non-six-type blocks (e.g. `document`) dropped on the DGX lane | proxy | P3, P6 | P2r2 #8 | Parity now; post-cutover config rule routes such requests to Anthropic. |
| OD-10 | P | `count_tokens` for local models goes to the backend vs D13 wording | proxy | P3 | P2r2 #9 | Keep behavior; amend D13 to name `/v1/messages/count_tokens`. |
| OD-11 | P | Exporter poison-line crash loop under KeepAlive (production config confirmed; remotely triggerable in legacy, L3) | exporter | P2 | P2r2 #10 | Approved deviation: skip and count bad lines. |
| OD-12 | P | Hook H-04 crash | hook | P4 | P2r2 #11 | Fix; document as deviation. |
| OD-13 | P | Price tables (Haiku read 0.005; no Haiku > 100K tier; no Fable/Mythos; **exact-label pricing leaves Sonnet-on-Anthropic and every variant id unpriced**) | backfill, P6 cost | P6 | P2r2 #12, P2r3, r5 C-9 | Prices in config keyed by model pattern; legacy values for parity. |
| OD-14 | P | `subagentStatusLine` emission and `--subagent` in Go scope | launcher, status line | P1, P4 | P2r2 #14, P3r2 | Toggle, default on for parity. |
| OD-15 | P | Exporter parity oracle `/usr/bin/python3` 3.9.6, empty env | exporter | P2 | P2r2 #13 | Pin it for P2 goldens. |
| OD-16 | P | Client cancels counted as DGX errors (4 of 23) | proxy, exporter | P2, P3 | P2r3 #16, P3r2 #2 | Reproduce through cutover; later a `reason` field. |
| OD-17 | P | Upstream connection management out of parity scope (eager CONNECT couples lanes; no retry on stale keep-alive; h2 sticky cache exists in source but is **not live**, HTTP/1.1 observed) | proxy | P3 | P2r3 #17, P2r4 §1, r5 C-10 | Approved failure-mode deviation: lazy connects, reconnect or backoff, never couple lanes. |
| OD-18 | P | Response-hook crash paths P-S1..P-S4 | proxy | P3 | P2r3 #18, P3r2 #3, P3r3 #3 | Reproduce P-S1..S3 ledger effects; P-S4 approved deviation. |
| OD-19 | P | Launcher port race; unwired coordinator | launcher | P4 | P2r3 #19 | Out of parity scope; hylo binds its own listener. |
| OD-20 | P | P6 telemetry backend contract; evaluator unknown | status line, P6 | P6 | P2r3 #20 | Accept r3 §2.3 as the requirement; evaluator as a doc note. |
| OD-21 | P | CP-T05 detection point in D4-EX-2 | status line | P1 | P3r2 #1, P3r3 #1 | Opening-line skip (it also prevents BC-SL-100's poisoned cache). |
| OD-22 | P | Exporter DST false idle | exporter, status line | P2, P7 | P3r2 #4, P3r3 #4 | Accept through cutover; offset or epoch in P7. |
| OD-23 | P | Exporter tally misattribution | exporter | P2, P7 | P3r2 #5, P3r3 #5 | Reproduce in P2; structured hook log in P7. |
| OD-24 | **R** | Proxy listens on all interfaces and admits LAN clients, which then use the backend key (§1) | proxy | — (legacy) / P3 (hylo) | P2r4 §2.2, r5 §1 | **Legacy: live risk accepted by owner 2026-11-14; no change to legacy.** hylo default: HY-BIND-1/3/4. |
| OD-25 | P | No correlation key in the ledger | proxy, ledger | P3, P7 | P2r4 §3.3, r5 C-6 | Composite near-key on both lanes in P3 replay; `flow_id` + UTC offset in P7. |
| OD-26 | P | Config reload semantics (legacy can degrade to pass-through; not observed in logs) | proxy, config | P3, P6 | P2r4 §2.1, r5 §0.1 | Keep last good config, emit error event, never pass through. |
| OD-27 | **R** (exporter default: confirm) | Exporter binds `0.0.0.0:9210`, IPv4, unauthenticated, no source filter | exporter | — (legacy) / P2 (hylo) | pass 4, P2r4 §2.2, r5 §1 | **Legacy: live risk accepted by owner 2026-11-14; no change to legacy.** hylo default loopback (HY-BIND-5). The ruling named proxy + UI API; owner to confirm the exporter is included. |
| OD-28 | P | Upstream-error **text** in the Go proxy (mitmproxy/OS strings) | proxy | P3 | P3r3 #6 | Emit mitmproxy's fixed strings for the deterministic causes; declare `error` text out of byte parity (no metric reads it). |
| OD-29 | P | Exporter writer: hand-written byte-identical vs client library | exporter | P2 | P3r3 #7 | Hand-written during parity. |
| OD-30 | P | Numeric-sid duplicate keys in `cost-history.json` vs the exact-format ruling | status line | P1 | P3r3 #8 | Known difference (non-production shape); Go writes one key per sid. |
| OD-31 | P | Backfill NaN usd and history-shape behavior | backfill | P6 | P3r3 #9 | Keep for the one-off tool; any `hylo cost backfill` skips non-finite usd. |
| OD-32 | P | Go reader of a legacy-written poisoned mix cache (`cur.out` non-numeric) | status line | P1 (shadow week) | P3r3 #10 | Treat as no open turn (`cur = null`); paired with OD-21. |
| OD-33 | P | **Exporter stalls on one idle connection** (single-threaded, no socket timeout) (F-1) | exporter | P2 | r5 §2.4 | Approved failure-mode deviation: concurrent server with read-header and idle timeouts (HY-BIND-6); exposition bytes unchanged. |
| OD-34 | P | **Loopback is not authentication**: other local accounts or processes can use a loopback proxy and the backend key (L1, L5 on a multi-user host) | proxy, run | P3, P4 | r5 §1.4 | Judgment call: optional per-launch proxy credential (D16-style token) off by default for parity; verify Claude Code honors credentials in `HTTPS_PROXY` before adopting. |

**Final count: 34 items (OD-01..OD-34): 32 pending, 2 ruled (OD-24, OD-27 legacy side; OD-27's hylo exporter default awaits a one-word
confirmation).** Merges: pass-3 r3 #1 → OD-21, #2 → OD-16, #3 → OD-18, #4 → OD-22, #5 → OD-23 (as in r4); #6-#10 added unmerged as OD-28..OD-32
(OD-32 cross-referenced to OD-21, not merged: one is a parser rule, the other a reader rule for legacy-written state).

### 3.3 Risk ranking (revised)

Top 8: **OD-06** (client credentials to the backend), **OD-07** (client auth headers forwarded), **OD-11** (exporter crash loop, production
config), **OD-16** (cancels inflate the error metric), **OD-17** (lane coupling via eager CONNECT), **OD-25** (no correlation key: P3 replay
design), **OD-10** (`count_tokens` vs D13), **OD-33** (exporter stall). OD-24 and OD-27 leave the top set: accepted by the owner for legacy, and
their hylo side is a recorded default (HY-BIND-1..6), not an open risk.

---

## 4. Target D — anything else open in the pass-2 domain model

- **Entity model:** stable. This round added no domain entity. F-1 is a failure mode of an existing entity (exporter process lifecycle). The
  §1 exposure model refines the existing "Proxy listener" entity. The catalogue rows to update are: *Proxy listener* (C-7, HY-BIND),
  *Process lifecycle* (F-1), *Rebuild state* (CONV-ABS-13), *Exposition* (C-5).
- **Schema:** corrected in place by C-1..C-4, C-6 and CONV-ABS-14. Nothing else in the 13-event schema failed re-verification.
- **Still open, owner-side only:** the VictoriaMetrics capture (carried); `~/.mitmproxy/config.yaml` contents (pass-3 r3 gap 1, now also
  relevant to `proxyauth`/`listen_host`); confirmation of OD-27's exporter default; 32 pending decisions.
- **Pass-3 hand-offs** (to its next round, not edited here): `anthropic_upstream_error` covers any non-DGX host (CONV-ABS-14); the exporter
  stall (F-1) as a BC; the near-key on the Anthropic lane (C-6).

---

## Delta Summary

| Target | New | Refined / confirmed |
|---|---|---|
| A evidence and exposure | 4 gap closures (protocol h1, pass-through not observed, peer-closed LOW, firewall off); owner ruling recorded; **LAN capability model L1-L7 / N1-N5** with sources, including three paths no prior round had: **plain-HTTP absolute-form use of the key without TLS or CA** (L1), **one-request persistent metrics outage** (L3, E-08 made remote), **pivot to the Mac's loopback services** (L5); precise admission set (100.64/10 admitted, IPv6 global refused); hylo requirements HY-BIND-1..6 | OD-24/OD-27 confirmed live, severity assigned, then ruled |
| B re-verification | 33 rows checked; **F-1 exporter idle-connection stall** (new failure mode); orphaned-by-proxy-exit hypothesis for unpaired requests | 26 confirmed; CONV-ABS-13 (state miscount), CONV-ABS-14 (empty-attribution test; `anthropic_upstream_error` = any non-DGX host); C-1..C-10 |
| C decisions | OD-28..OD-34 (5 from pass-3 r3, 2 new) | 0 duplicates; 2 rewordings (OD-07, OD-17); OD-13 exact-label wording; 2 ruled |
| D open items | none in the entity model | pass-3 hand-offs listed |

Existing items refined: 12 (C-1..C-10, OD-07, OD-17).

## Remaining Gaps (verbatim-carryable)

1. Owner capture, VictoriaMetrics (unchanged): one `/api/v1/query` response for the exact `QUERY` (`dgx_statusline.py:102-123`) on an idle box,
   under light load, and with fewer than 20 TTFT samples, after the DGX soak is scored. Look for `"NaN"`/`"+Inf"`/`"-Inf"` in `value[1]` per
   `__name__`.
2. Owner one-word confirmation: does the OD-27 ruling's hylo default (loopback with opt-in and warning) cover the **exporter** as well as the proxy
   and UI API (HY-BIND-5)?
3. Owner check (LOW, shared with pass-3 r3 gap 1): whether `~/.mitmproxy/config.yaml` exists and sets `proxyauth`, `listen_host`,
   `block_private`, `store_streamed_bodies`, `connection_strategy` or body-size options. Absent → §1 and P-S4 hold as written.
4. Not checked, LOW: whether mitmproxy 12.3.1's shutdown path fires the `error` hook for in-flight flows (decides whether §2.5's
   orphaned-by-exit hypothesis can explain unpaired requests). Static read of `master`/`proxy/server` shutdown, no execution.
5. Owner decisions: 32 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-34).

## Novelty Assessment

Novelty: SUBSTANTIVE

Most of this round is confirmation and consolidation (26 of 33 rows confirmed, the decision list completed from pass-3 r3, the owner ruling
recorded). On their own those would be NITPICK. Under this round's stated rule (a new failure mode or a schema error is SUBSTANTIVE), three
findings qualify, and each changes a spec:
- **F-1, exporter stall on one idle connection** (single-threaded `HTTPServer`, `timeout = None`). No prior pass recorded it. It adds a hylo P2
  requirement (HY-BIND-6) and owner item OD-33.
- **CONV-ABS-14, schema semantics:** `anthropic_upstream_error` is written for any non-DGX host, and empty attribution does not identify the
  failing side. This corrects the meaning of a ledger event, which any P3 replay or D16 history reader depends on.
- **The LAN capability model** adds three exposure paths absent from r4: key use **without TLS or CA trust** (plain-HTTP absolute form), a
  **one-request persistent metrics outage** (E-08 made remotely triggerable), and a **pivot to loopback-only services**. For legacy these are
  covered by the owner's acceptance. For hylo they justify HY-BIND-4 (an admission check separate from the bind) and OD-34 (loopback is not
  authentication).
The schema corrections C-1..C-6 (the `anth_reply` defect variant, the defect mechanism, the `bridge_ws_close` trigger, replies without requests)
are refinements. The entity model itself did not change.

## Convergence Declaration

Another round needed — the substantive items above surfaced this round (F-1, CONV-ABS-14, the L1/L3/L5 exposure paths). The domain entity set
was stable for the second consecutive round. What remains is owner-side (gaps 1-3, 5) plus one static mitmproxy shutdown read (gap 4).

## State Checkpoint

```yaml
pass: 2
round: 5
status: complete
files_scanned: dgx_proxy.py (1-560), dgx_ledger_exporter.py (full), claude-dgx (70-80, 97), dgx_statusline.py (parts), dgx_preflight.py, dgx-proxy-coordinator.sh, auto_continue.py (parts) + mitmproxy 12.3.1 (addons/block, addons/proxyserver, options, proxy/layers/http/__init__) + CPython 3.12.10 ipaddress + Python 3.9 socketserver/http.server + dgx-llm deploy/recording.yml
timestamp: 2026-11-14T06:55:01Z
novelty: SUBSTANTIVE
retractions: [CONV-ABS-13, CONV-ABS-14]
corrections: [C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10]
new_failure_modes: [F-1 exporter idle-connection stall]
owner_decisions: 34 (OD-01..OD-34; 32 pending, 2 ruled: OD-24, OD-27 legacy side)
owner_ruling_recorded: 2026-11-14 OD-24/OD-27 legacy LAN exposure accepted; hylo loopback default kept (HY-BIND-1..6)
pass3_r3_reconciled: yes (read, not edited)
next: pass 2 round 6 (targets = Remaining Gaps 1-5 verbatim)
```
