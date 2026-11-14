# Pass 4 Deepening — Round 1: NFR catalogue and complete threshold catalogue — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Nothing in `legacy/` was imported, executed or modified; no proxy, nothing networked.
- Method: mechanical census of every numeric literal. Python: `ast.parse` over the 6 `.py` files (scripts copy no legacy code, run with
  `python3.11 -I`); string constants holding numeric defaults found the same way; shell and plists by grep. Scratch evidence:
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r1/` (`nums.py` → `nums.tsv`, 522 rows;
  `strnums.py`; `cmps.py`; `classify.py` → `classify.out`).
- Inputs read: pass-4 broad (`…-pass-4-nfr-catalog.md`, T-001..T-105), extraction validation, pass-2 deep r1 §6 (the CONFIG map base; the
  orchestrator calls it "r2's" map because r2 §0/§6.8 amend it, per r8 §7 "CONFIG map (D15): r1 §6.1-6.3 + r2 §0, §6.8"), r2, r5 §1.4/§2.4/§3.2,
  r6 §1.3, r7 §1 (mitmproxy 12.3.1 option defaults), r8 (§0-§1, §4-§7), r9, pass-3 r2 (BC-SL-091/092), r4 §7 (index), r8 §4 (totals);
  `docs/STATUSLINE-REVIEW-2026-11-13.md`, `docs/STATUSLINE-WIDGETS.md`, `docs/PLAN.md` (D5, D15, D16, §4 line 61), `.factory/policies.yaml` (16, 20).
  CLAUDE.local.md not read.
- Line numbers: `SL` = `dgx_statusline.py`, `PX` = `dgx_proxy.py`, `EX` = `dgx_ledger_exporter.py`, `HK` = `auto_continue.py`,
  `PF` = `dgx_preflight.py`, `BF` = `tools/backfill_cost_history.py`, `L` = `claude-dgx`, `CO` = `dgx-proxy-coordinator.sh`,
  `pl-ex` / `pl-tu` = the two plists.
- Numbering: thresholds continue the broad catalogue (new rows **T-106..T-135**). Retractions **CONV-ABS-41..44** (45, 46 unused). New owner
  items **OD-54..OD-57**. Sibling files (passes 0, 1, 5) not touched.

Rationale codes (policy 16): **M** measured, **Dv** derived, **C** convention, **J** labeled judgment call (labeled in source or docs).
**DOC** = the rationale is written in a code comment or doc (quoted source given). **N/A** = dead or obsolete in hylo, so no rationale needed.
**OWNER** = no rationale found anywhere; goes on the owner list (§B.3). A derived rationale I constructed from the code (not written by the owner)
is marked **Dv†** and goes on the bulk yes/no confirmation list (§B.2).

---

## 0. Audit of the broad pass (5 hallucination classes) and retractions

The broad threshold table was re-checked row by row against the census (§A). All 105 values and line anchors hold (as the extraction validation
found). The problems are in the broad pass's §1 NFR prose, not in the table.

| Marker | Broad pass-4 claim | Ground truth | Evidence |
|---|---|---|---|
| **CONV-ABS-41** | §1 Reliability: "Status line never blank, never non-zero … import-time env parse is the exception, **see BC-SL-001**" | Miscited and incomplete. BC-SL-001 is the guard itself; the import-time crash is **BC-SL-087** (CP-X01/X02). Two more paths end outside the guard: **CP-X03** (the guard's own `print` fails, e.g. EPIPE after Claude Code cancels the run → exit 1) and **CP-X04** (signals). Pass-2 r2 §0 already recorded both; the broad pass-4 row was never updated | `SL:74-75,1238-1245`; P2r2 §0 row 1 |
| **CONV-ABS-42** | §1 Reliability: "Telemetry degradation ladder: fresh -> stale (**≤ 300 s**, age shown) -> dead" (and broad T-003 "STALE_OK green-dot freshness") | Two errors. (a) Stale starts at the **first failed fetch**, not after 15 s: `render_telemetry` goes stale on `not up or age > STALE_OK` (`SL:697`), and after a successful fetch `age < TTL` always, so at the default TTL (4 s) the 15 s bound is **unreachable** (§A.4 F-1). (b) The last-known sample is limited to 300 s only on refreshes that fetch; refreshes inside a TTL window after a failed fetch return the cached sample at **any** age (pass-3 r2 BC-SL-091) | `SL:315-359,693-701`; P3r2 lines 193-197 |
| **CONV-ABS-43** | §1 Performance: "incremental transcript parse **capped at 512 KB/refresh**" | Not a cap. The read is at least 512 KiB, and when the window holds no newline it keeps reading in 512 KiB steps until it finds one or reaches end of file (`SL:1044-1052`). The per-refresh read has **no upper bound** below the file size; lines of 1.36 MB were measured (review #6.5). The broad pass's own reliability row describes the fix, which contradicts the "cap" | `SL:952,1041-1052`; review #6 |
| **CONV-ABS-44** | §1 Performance: "Proxy must not add streaming latency … **only JSON/error bodies buffered**" | Wrong scope. Only `/v1/messages*` JSON or ≥ 400 responses are buffered **by the addon's choice**; every other non-SSE response on every intercepted host is **buffered in full by mitmproxy's default** (`stream` unset, `stream_large_bodies` None, `body_size_limit` None), with no size cap. BC-PX-037 row 4 states this; the NFR row contradicted it | `PX:191-208`; P3r2 §B1 row 4; P3r3 BC-PX-037; r7 §1.2 |

Class audit: no phantom thresholds (classes 3/4); no miscounted enumerations in the table (class 2); metric recount below (class 5) confirms
105 catalogued rows and 52 UNKNOWN rows. Refinements to catalogued rows (not retractions): T-066 keeps **19** old files and then writes one, so
the directory holds ≤ 20, and only 19 when the new body is ≥ 50,000,000 characters (`PX:291-296`); T-086 also has a **head** clip `[:800]` used
when the rendered state is empty (`HK:91`); T-088's early stop also needs **≥ 2** scores and uses the **last** call's latency (`HK:133`, now
T-118); T-045's floors have a third value, `1e-9` for any other key (`SL:671`, now T-114).

---

## A. Complete threshold catalogue

### A.1 Mechanical census of numeric literals

| Source | Sites | Threshold | Format / protocol | Unit conversion | Incidental |
|---|---|---|---|---|---|
| `dgx_statusline.py` (AST) | 303 | 146 | 29 | 36 | 92 |
| `dgx_proxy.py` (AST) | 70 | 17 | 9 | 0 | 44 |
| `dgx_ledger_exporter.py` (AST) | 83 | 9 | 8 | 0 | 66 |
| `auto_continue.py` (AST) | 18 | 16 | 0 | 0 | 2 |
| `dgx_preflight.py` (AST) | 5 | 2 | 2 | 0 | 1 |
| `tools/backfill_cost_history.py` (AST) | 43 | 22 | 1 | 6 | 14 |
| **Python AST total** | **522** | **212** | **49** | **42** | **219** |
| Numeric env defaults in string constants | 10 | 10 | — | — | — |
| Shell + plists (excluding comments and the `0`/`1` env-bool sentinels) | 24 | 24 | — | — | — |

Classification rules (`classify.py`): a site is **threshold** when it belongs to a catalogued or new T-row; **format/protocol** when it fixes a
file, wire or display format (HTTP status, exit code, UUID-prefix truncation, digest lengths, tuple indices of the mix result, JSON indent,
rounding digits of a frozen format); **unit conversion** for 60/3600/86400/1440/1000/1e6/3.6e6/100/255 used as arithmetic; **incidental**
for 0/1 used as start values, indices, increments, defaults and guards with no policy meaning. Zero tests that carry policy (e.g. "any
preemption", "hide zero parts") were found with an AST pass over every comparison against 0/1 (`cmps.py`, 48 comparisons) and moved to threshold
rows (T-047, T-107, T-108, T-111, T-116). After classification **0 sites are unclassified**.

Reconciliation: the 212 AST threshold sites map to 102 T-ids (88 catalogued + 14 new; `HK:133` carries both T-088 and T-118). The 17
catalogued rows the AST cannot reach are all string or shell sites: T-001, T-002, T-016, T-017, T-077, T-078, T-082..T-085 (string constants)
and T-094..T-099, T-101 (shell). **Every catalogued row has a source site, and every threshold site has a row.**

Named-constant classes found (not thresholds; listed for §C): HTTP status codes 200/400/404 (`PX:205,225,283`, `EX:200,202,206,273,400`); URL
default port 80 (`PX:83`, `PF:20`); CLI exit 2 (`PX:764`); UUID first-group truncation to 8 (`PX:332,335`, `EX:84-90,382`); digest lengths
sha1[:16] (`SL:405`), sha256[:16] (`PX:713,730`), 64-hex fingerprint token (`PX:599`); mix-tuple indices 3..9 (`SL:575-578,1225`);
`trust-state.json` indent 2 (`PX:620`); cost-history `round(usd, 4)` (`SL:234`, `BF:108`); ledger duration rounding 3/1 dp (T-070); display
precisions (`.0f/.1f/.2f`, 41 f-string specs in `SL`, `.3f` in `EX` exposition, `.3f/.2f` in the hook log line that the exporter parses with
`p_done=([0-9.]+)`, `HK:250`, `EX:230`); ANSI SGR codes (`SL:127-134`); `ps` walk stop at pid ≤ 1 (`SL:291`, the init process).

### A.2 Prompt-listed items reconciled against the catalogue

| Item named by the orchestrator | Status |
|---|---|
| 512 KB transcript read window | catalogued **T-054** (semantics corrected, CONV-ABS-43) |
| 64,000-byte SSE tap line bound | catalogued **T-065** (OD-35) |
| `API_TIMEOUT_MS` 1,800,000 | catalogued **T-097** |
| cache TTLs | catalogued **T-001** (VM 4 s), **T-013** (git 5 s); write throttle **T-022**; plan-limit retention **T-010** |
| KEEP_DEAD / 300 s / 15 s | catalogued **T-004**, **T-003** (reachability finding §A.4 F-1); the other 300 s values are **T-011**, **T-040**, **T-043** |
| `TTFT_MIN_N` 20, `NARROW_COLS` 72, `RL_KEEP` | catalogued **T-015**, **T-014**, **T-010** |
| mitmproxy `tcp_timeout` 600 s | **missing → T-122** |
| exporter backlog of 5 | **missing → T-129** |
| "and others" | **missing → T-106..T-121, T-123..T-128, T-130..T-135** (below) |

### A.3 New threshold rows (missing from the broad catalogue)

#### A.3.1 Literal thresholds in legacy source

| # | Value | Meaning | file:line | Rationale |
|---|---|---|---|---|
| T-106 | 2 points | sparkline drawn only with ≥ 2 plotted points | `SL:666` | Dv (a trend needs two samples) |
| T-107 | preempt rate > 0 | amber marker stored in the history point at sample time (separate site from the queue rule T-047) | `SL:346` | DOC: "same rule as the queue (#17.3)" (`SL:346`; review #17 "marker > 0") |
| T-108 | running < 1 | idle `☾` also requires no running vLLM request | `SL:825` | DOC: review #20 "gating (> 5 min AND running < 1) correct"; WIDGETS Idle "**and** nothing runs on vLLM" |
| T-109 | `round(n/total*100)`, `" <1%"` when it rounds to 0, width 2 | composition percent format | `SL:1171-1172` | DOC: "present but tiny"; "1-digit values padded so widths don't jitter" (`SL:1162,1172`). **Parity note:** this uses Python `round()` (half-to-even), unlike the thermometer, which review #5.2 moved to half-up |
| T-110 | ≥ 2 non-zero parts | token bracket `[in ✍ ⟳]` shown only with two or more parts | `SL:595` | DOC: "one part alone always equals ↑: no brackets" |
| T-111 | `> 0` tests (group) | zero suppression: `▲▼` hidden at 0/0 (`:536-537`); token parts and `↻0` hidden (`:586-598`); `$` only when `usd > 0` (`:602`); `⛏` only when tokens > 0 and the $/MTok series > 0 (`:627,629,1221`); composition bucket hidden at 0 (`:1170`) | `SL` as listed | DOC: WIDGETS Tokens "Zero parts and ↻0 are hidden"; review #8 "hidden at 0/0" |
| T-112 | `(i + 0.5) * 10` | thermometer cell `i` is colored at its midpoint percentage | `SL:428` | Dv (cell represents its center) |
| T-113 | 8 levels, half-up | sparkline quantization: `len("▁▂▃▄▅▆▇█") - 1` steps, `int(j + 0.5)` | `SL:135,673-675` | C (Unicode block elements U+2581–U+2588 offer 8 heights) + Dv (half-up). If glyphs become config (OD-02) the level count derives from the glyph string length |
| T-114 | 1e-9 | sparkline scale floor for a key without a floor | `SL:671` | Dv (division-by-zero guard; reachable only for an unknown trace key) |
| T-115 | clamps | percent-domain clamps: heat input 0..100 (`:146`), context % (`:422`), `♻` 0..1 (`:479`), plan-limit % (`:508`), KV % (`:758`); projection only for `elapsed ≤ 1.0` (`:517`) | `SL` as listed | Dv (domain of a percentage). Observable: stdin `used_percentage: 104` renders `100%` |
| T-116 | ROWS < 2 / > 2; COLUMNS = 0 | row 2 omitted when `DGX_SL_ROWS < 2` (`:1217`); forced when `> 2` or when the width is unknown (`:1224`) | `SL:1217,1224` | DOC: WIDGETS Tunables "1 = row 1 only; > 2 = force row 2"; header "COLUMNS may be absent/non-numeric" (`SL:50`) |
| T-117 | ≥ 1e6 → `x.xxM`, ≥ 1000 → `x.xk`; `mm:ss` | `--subagent` token and elapsed formats (differ from row 1's `_fmt_tok_c`) | `SL:876-885,919-920` | OWNER (scope depends on OD-14) |
| T-118 | ≥ 2 scores | Kev early stop needs at least two scores in hand | `HK:133` | J: "slow endpoint: stop early, median of what we have" (`HK:134`) + Dv (a median needs > 1 value to differ from a single draw) |
| T-119 | `ps[len(ps) // 2]` | median of the sorted Kev scores: with 2 scores this is the **higher** one, which leans toward allowing the stop | `HK:137-138` | Dv† (formula consequence; owner confirms the lean is acceptable) |
| T-120 | `127.0.0.1:9210:127.0.0.1:9210` | reverse tunnel binds DGX-side loopback 9210 to the exporter port | `pl-tu:8` | Dv (mirrors T-078). OOS: BC-SV-002 "home-lab deployment" |
| T-121 | 4141-4199; `curl -m 2`; 40 × 0.25 s | visible-mode router port range, health probe timeout, start wait | `L:20-21,85,94` | N/A: dead under D6 (invisible mode only) |

#### A.3.2 Implicit defaults in effect (no legacy literal; they shape observed behavior)

| # | Value | Meaning | Source | Rationale | Evidence of effect |
|---|---|---|---|---|---|
| T-122 | **600 s** | mitmproxy `tcp_timeout`: any connection with no bytes in either direction for 600 s is closed (F-2) | mitmproxy 12.3.1 `options:240-246`; launcher sets no option (`L:75`) | C (tool default) | M: 57 closes in 40 logs = 56 idle npm keep-alives at exactly 600 s + **1 in-flight MCP SSE cut**; 0 on Anthropic/DGX lanes (r8 §1.1). OD-37 |
| T-123 | TLS ≥ 1.2, max unbounded | both legs | m/`addons/tlsconfig:157-186` (r7 T-2) | C (tool default) | not observable against `api.anthropic.com` (TLS 1.3) or the plain-HTTP backend |
| T-124 | 58 s | HTTP/2 ping keepalive | m/`options` (r7 §1.5) | C (tool default) | active only for child-tool h2 flows (7,566, CONV-ABS-25); Claude Code is h1 |
| T-125 | RSA 2048; CA 10 years; leaf 199 days | mitmproxy CA and minted leaf certificates | m/`options:7,9`, m/`certs:40-41` (P2r3 §3.1) | C (tool default) | CA trusted via `NODE_EXTRA_CA_CERTS` and the keychain |
| T-126 | none (OS) | upstream connect timeout; a silent backend waits for the OS TCP connect timeout (value not source-read) | m/`proxy/server:206-235` (r7 T-4) | N/A (absence of a limit) | OD-42 |
| T-127 | unbounded | buffered body size: request bodies are read whole for routing; `/v1/messages*` JSON/error responses and **all other non-SSE pass-through responses** are buffered in full | `PX:191-208`; m/`body_size_limit`, `stream_large_bodies` None (r7 §1.2) | C (tool default) | memory and first-byte latency scale with the response (e.g. release downloads from `downloads.claude.ai`, 745 connects, r8 §0). **OD-54** |
| T-128 | unbounded | WebSocket messages kept for the connection's life (F-3) | m/`proxy/layers/websocket:177-187` (r7 W-1, r8 §5 B-3) | C (tool default) | ≤ 1,151 messages per connection observed, bytes unknown (r8 §1.4). hylo default HY-WS-1 (D16 bounded buffer) |
| T-129 | 5 | exporter listen backlog (`request_queue_size`); beyond it connections are refused while the server is stalled | py3.9 `socketserver:441` (P2r6 F-1 (c)) | C (library default) | only matters during an F-1 stall (OD-33) |
| T-130 | none | exporter socket timeout (`StreamRequestHandler.timeout = None`) | py3.9 `socketserver:783-793` (P2r5 §2.4) | C (library default) | F-1: one idle client stalls every scrape (BC-EX-026, OD-33) |
| T-131 | 65,537 B | exporter request-line read limit (`readline(65537)`) | py3.9 `http/server:393-402` | C (library default) | none observed |
| T-132 | 10 s (unverified) | launchd respawn throttle for `KeepAlive` agents; sets the exporter crash-loop cadence | launchd default `ThrottleInterval` (P2r3 E-3: "documented default 10 s; not verified here") | C (platform default) | OD-11 loop is slow, not busy |
| T-133 | 4,300 digits | CPython ≥ 3.11 int-string limit: a transcript line with a longer integer literal raises `ValueError` and is **skipped** by the status line and the hook; the exporter on 3.9.6 parses it | CPython 3.11 (the CVE-2020-10735 mitigation); P2r1 §1.1, P2r2 §0 | C (runtime default) | parity oracle O1 pins 3.11 for status line and hook; OD-15 pins 3.9.6 for the exporter, so the two components disagree on such a line |
| T-134 | 300 ms debounce; in-flight run cancelled by a newer trigger | Claude Code's status line scheduler | `SL:43-44` ("verified against code.claude.com docs, 2026-11-11"); WIDGETS "How it runs" | external constant (Claude Code) | sets the time budget of one status line run (§D P-1). Not configurable by hylo |
| T-135 | 5 s | Claude Code's timeout for a `subagentStatusLine` run | WIDGETS subagent contract (2.1.322) | external constant (Claude Code) | OD-14 scope |

### A.4 Reachability findings (thresholds that are inert at legacy defaults)

| F | Threshold | Finding | Consequence |
|---|---|---|---|
| **F-1 (new)** | T-003 `STALE_OK` 15 s | After a successful fetch, `ts == fetch_ts`, so on the cached path `age = now − ts < TTL`. A failed fetch sets `up = False`, which is stale regardless of age. So "fresh but older than 15 s" needs **TTL > 15 s**. At the default TTL 4 the bound never decides anything (the `ts`-missing default of T-064 is the only other route, and it comes with no sample) | The WIDGETS Health-dot text "Green: VM sample < 15 s old" describes a rule that does not operate at the default: the dot turns yellow on the **first** failed fetch, with `(~Ns old)` where N can be as low as the TTL. OD-55 |
| F-2 (pass-3 BC-SL-092, restated) | T-008 `HIST_MIN_GAP` 2 s | With TTL ≥ 2, history points are at least TTL apart, so the gap never bites | inert at default; guards a TTL < 2 s configuration |
| **F-3 (new)** | T-009 history cap 32 | The age filter (`now − t < 90 s`, `SL:336`) runs first; at TTL 4 it keeps at most 23 points (ages 0..88 s), so `hist[-32:]` never truncates. It bites only for 2 s ≤ TTL < 2.8 s (90/32) | inert at default; bounds the cache file for short TTLs |
| **F-4 (new)** | T-007 `SPARK_MAX_AGE` 90 s | `SPARK_PTS` 12 plots the newest 12 points (~44-48 s at TTL 4, review #17.2: "doc said 90 s"). The 90 s value therefore acts only as **gap pruning**: after a fetch outage or a pause in refreshes longer than 90 s, old points are dropped instead of being joined across the gap | rationale changes from "history length" to "gap pruning" |
| **F-5 (new)** | T-064 default age 9999 | Reached only when the cache has `fetch_ts` but no `ts` (first fetch failed). `now − 9999` is effectively "infinitely old" with real clocks, and the sample is absent, so the output is `◌ DGX ?` whatever the value (except `TTL = inf`, pass-3 BC-SL-087) | a sentinel, not a threshold: Go uses an explicit "unknown age" with the same outcome |
| **F-6 (new)** | T-005 `HTTP_TIMEOUT` 1.5 s, T-083 `KEV_TIMEOUT` 2.5 s | Python `urlopen(timeout=…)` sets a **per-socket-operation** timeout (connect, then each blocking read), not a total deadline. A server that dribbles bytes can hold the status line past 1.5 s and the hook past 2.5 s per call. Go's `http.Client.Timeout` is a total deadline | the D15 key must state its semantics. OD-56 |

---

## B. Rationale resolution for the 52 UNKNOWN rows

### B.1 Resolution table

| T | Value | Resolution | Rationale (source) |
|---|---|---|---|
| T-003 | 15 s | **Dv†** | inert at the default TTL (F-1); the plausible intent is one VM scrape interval, which review #16.1 gives as 15 s. Effective only when `ttl_s > 15` |
| T-004 | 300 s | **OWNER** (group A) | docstring states the ladder (`SL:34-38`), not why 5 min |
| T-005 | 1.5 s | **Dv†** | measured LAN RTT ~25 ms (`SL:81`) and Claude Code's 4 s tick with in-flight cancellation (T-134): 1.5 s is ~60× the RTT and below one tick. Per-operation semantics (F-6) |
| T-007 | 90 s | **Dv†** | gap pruning (F-4); 90 s was the documented history span before `SPARK_PTS` capped it (review #17.2) |
| T-008 | 2 s | **Dv†** | inert at TTL ≥ 2 (F-2); guards oversampling for a short TTL |
| T-009 | 32 | **Dv†** | inert at the default (F-3); bounds the session cache for a short TTL |
| T-010 | 1800 s | **OWNER** (group A) | purpose documented ("no blinking", `SL:85,298-303`); value not |
| T-014 | 72 cols | **OWNER** (group B) | none |
| T-022 | 60 s | **Dv†** | at the 4 s refresh, one write per minute is 1/15 of refreshes; WIDGETS: concurrent sessions' lost updates are "repaired by the next minute's write" |
| T-024 | `int(q·(n−1))` | **C** | the "lower" nearest-rank method (numpy `method="lower"`), no interpolation. Parity requires it exactly; the percentiles 0.75/0.95 are owner design (review #11 revisit) |
| T-025 | 6 levels | **Dv†** | expected chain is status line ← per-refresh shell ← `claude` (docstring `SL:268-271`): depth 2; 6 leaves margin for wrappers |
| T-026 | 1 s | **Dv†** | one `ps` call per level, once per session (cached `proc_start`); 1 s keeps a worst-case walk inside the run budget |
| T-030 | hue 0.22, s 0.85, v 0.80 | **OWNER** (group B, aesthetic) | none |
| T-035 | 1.15 × window | **OWNER** (group A) | none; behavior: a countdown is hidden when `resets_at` lies more than 1.15 windows ahead (implausible data) |
| T-038 | > 60,000 ms | **Dv†** | `_hm` has minute granularity: below 60 s it would print `⏱ 0m` |
| T-039 | ≥ 60,000 ms | **Dv†** | same as T-038 (`·0m` otherwise). The `>` vs `>=` asymmetry is unobservable, since the API part prints only inside a shown timer |
| T-046 | fade 0.55..1.0, RGB triples | **OWNER** (group B, aesthetic) | none |
| T-050 | > 0.5 % | **Dv†** | the share prints with `.0f`; at or below 0.5 it would print `↺host 0%` |
| T-054 | 524,288 B | **OWNER** (group C) | none (semantics corrected by CONV-ABS-43) |
| T-059 | 2,000 chars | **OWNER** (group C) | review #6.3 records the decision ("nested images = 2,000 B"), not the derivation |
| T-060 | 256 ids | **Dv†** | comment: "ids of the same message are adjacent, a short memory of recent ids covers refresh boundaries" (`SL:1029-1032`); any N ≥ 1 covers adjacency, 256 is margin |
| T-061 | 40 chars | **Dv†** | ≥ 36, the length of a session UUID, so real session ids are never truncated. Also a named constant (cache file name format, P2r1 §6.3) |
| T-064 | 9999 | **Dv†** | sentinel (F-5) |
| T-065 | 64,000 B | **OWNER** (group C) | purpose documented ("runaway line guard", `PX:368,408`); value not. OD-35 already proposes it as the configurable default |
| T-066 | 20 files | **OWNER** (group E) | purpose documented (post-mortem of multi-MB 400s, `PX:284-285`); count not |
| T-067 | 50,000,000 chars | **OWNER** (group C) | none (≫ the "multi-MB bodies" of `PX:284`) |
| T-068 | 600 chars | **OWNER** (group D) | none |
| T-069 | 300 chars | **OWNER** (group D) | none. Note: this shapes the ledger `error` field value (D7 surface; parity BX) |
| T-071 | 8 chars | **C** | first group of a UUID (`account_uuid` is a UUID: 8 hex characters). Named constant: D7 ledger value format |
| T-074 | 3 backups | **OWNER** (group E) | none |
| T-075 | 30 s / 0.5 s | **OWNER** (group G) | none; obsolete if `ca.restart_command` is dropped (P2r1 §6.1 row 8) |
| T-076 | 10 | **Dv†** | bound on a loop whose delete call is `check=False`, so a failing delete cannot spin forever |
| T-077 | 50 sessions | **OWNER** (group E) | purpose documented ("most-recent sessions tracked", `EX:24`); value not (Prometheus label cardinality bound) |
| T-078 | 9210 | **C** | Prometheus exporter port range (9100-9999); the number itself is arbitrary. The tunnel mirrors it (T-120) |
| T-080 | 8 chars | **C** | first UUID group (session ids are UUIDs). Named constant: D7 label value |
| T-081 | status == 200 | **Dv†** | a successful Messages API call returns 200, so "other 2xx excluded" changes nothing in practice. D7 metric semantics (named constant) |
| T-083 | 2.5 s | **Dv†** | measured 13 ms per Kev pass (`HK:127`, for Kev-0.8B; the launcher pins kev-4b, latency not recorded) and 3 × 2.5 s = 7.5 s, inside the 30 s Stop timeout (T-094). Per-operation semantics (F-6) |
| T-084 | 14 | **N/A** | dead (`KEV_MESSAGES` never read) |
| T-085 | 6000 chars | **OWNER** (group C) | none |
| T-086 | 400 / 800 | **OWNER** (group D) | purpose documented ("the TAIL carries the verdict signal", `HK:87-88`); values not |
| T-089 | 160 / 100 | **OWNER** (group D) | none |
| T-090 | > 20 chars | **OWNER** (group F) | none |
| T-091 | < 200 chars | **OWNER** (group F) | none |
| T-092 | 12; 4 and > 2 % | **OWNER** (group F) | purpose labeled ("not just a quoted word or two", `HK:188`); numbers not |
| T-093 | 20 s | **N/A** | dead (`opus_verdict` never called) |
| T-094 | 30 s / 5 s | **Dv†** | Stop: ≥ worst-case Kev time 7.5 s plus transcript read; UserPromptSubmit runs an `echo` |
| T-095 | 8090-8143 | **N/A** | per-window port search; hylo binds its own listener (OD-19, BC-LN-004/BC-CO-002 OOS) |
| T-096 | 40 × 0.25 s | **N/A** | waits for a separate mitmdump process; hylo's listener is in process |
| T-098 | 4 s, padding 0 | **OWNER** (group G) | launcher comment states the role ("drives it between messages", `L:170-171`), not why 4 s. One decision with T-001, which is documented as "match refreshInterval" |
| T-099 | 120 s | **N/A** | dead (coordinator unwired, OD-19) |
| T-100 | 4 s | **OWNER** (group G) | none |
| T-101 | 30 s × 3 | **Dv†** | ssh declares the tunnel dead after 3 unanswered probes 30 s apart (~90 s); launchd then restarts it. OOS for hylo (BC-SV-002) |

### B.2 Bulk yes/no confirmation list (derived rationales, Dv†)

One answer ("accept as derived") closes these 20: **T-003, T-005, T-007, T-008, T-009, T-022, T-025, T-026, T-038, T-039, T-050, T-060, T-061,
T-064, T-076, T-081, T-083, T-094, T-101** (old) and **T-119** (new). Each rationale is one line in §B.1 / §A.3; none changes a default.

### B.3 Owner must supply a rationale (25 rows, 7 groups)

A one-line answer per group is enough; the suggested wording is offered so the owner can reply "accept as labeled judgment call".

| Group | Rows | Suggested wording if the owner has no measurement |
|---|---|---|
| **A. Retention / staleness windows** | T-004 KEEP_DEAD 300 s; T-010 RL_KEEP 1800 s; T-035 countdown gate 1.15 × window | "judgment: 5 min of last-known telemetry; 30 min of plan limits between Claude Code reports; 15 % slack on a reset time before it is treated as bogus" |
| **B. Layout and aesthetics** | T-014 NARROW_COLS 72; T-030 heat HSV; T-046 sparkline RGB/fade; T-117 subagent formats (if OD-14 keeps the path) | "judgment (presentation)" |
| **C. Byte and size budgets** | T-054 512 KiB read step; T-059 2,000 chars per image; T-065 64,000 B tap tail (OD-35); T-067 50,000,000-char capture cap; T-085 6,000-char Kev state | "judgment: per-refresh parse budget / image weight estimate / runaway-line guard / disk guard / Kev context budget" |
| **D. Diagnostic text clips** | T-068 600; T-069 300 (ledger `error`); T-086 400/800; T-089 160/100 | "judgment: log readability" |
| **E. Retention counts** | T-066 20 capture files; T-074 3 CA backups; T-077 50 exporter sessions | "judgment: bounded disk / bounded label cardinality" |
| **F. Hook heuristic tuning** | T-090 > 20 chars; T-091 < 200 chars; T-092 CJK 12 / 4 and 2 % | "judgment, tuned on observed fake stops" (or a measurement if one exists) |
| **G. Timeouts and cadence** | T-098 refreshInterval 4 s (with T-001); T-100 preflight 4 s; T-075 CA regeneration 30 s / 0.5 s (or drop with `ca.restart_command`) | "judgment" or "Claude Code example value", if that is where 4 s came from |

Owner item **OD-57** carries §B.2 and §B.3 as one Phase-1 gate decision.

---

## C. D15 config mapping

Columns: key (P2r1 §6 key where one exists; `*` = proposed this round), type, default (= legacy), class. Classes: **CFG** config key;
**NC** named constant (D15 exception, reason given); **DROP** not carried; **EXT** external constant (Claude Code), not configurable by hylo;
**OOS** legacy deployment, not a hylo key; **NEW-H** hylo key without a legacy value.

### C.1 Status line (`internal/statusline`, P1)

| T | Key | Type | Default | Class |
|---|---|---|---|---|
| 001 | `statusline.telemetry.ttl_s` | float | 4 | CFG |
| 002 | `statusline.rows` | int | 2 | CFG |
| 003 | `statusline.telemetry.fresh_s` | float | 15 | CFG (effective only when > `ttl_s`, F-1; OD-55) |
| 004 | `statusline.telemetry.keep_dead_s` | float | 300 | CFG |
| 005 | `statusline.telemetry.timeout_s` | float | 1.5 | CFG (semantics per OD-56) |
| 006 | `statusline.sparkline.points` | int | 12 | CFG |
| 007 | `statusline.sparkline.max_age_s` | float | 90 | CFG |
| 008 | `statusline.sparkline.min_gap_s` | float | 2 | CFG (inert at default, F-2) |
| 009 | `statusline.sparkline.history_cap` | int | 32 | CFG (inert at default, F-3) |
| 010 | `statusline.limits.keep_s` | float | 1800 | CFG |
| 011 | `statusline.idle.after_s` | float | 300 | CFG |
| 012 | `statusline.cost.basis_min_mtok_month` | float | 30.4 | CFG |
| 013 | `statusline.git.ttl_s` | float | 5 | CFG |
| 014 | `statusline.narrow_cols` | int | 72 | CFG |
| 015 | `statusline.ttft.min_samples` | int | 20 | CFG |
| 016, 017 | `statusline.telemetry.query` (embeds `[1m]`, `[30m]`) | string | verbatim `SL:102-123` | CFG (the windows live inside the query string; separate keys would change the byte-identical default) |
| 018-021 | `statusline.cost.window_s` / `min_usd` / `min_sessions` / `cold_yellow_usd` | int/float/int/float | 2,592,000 / 1.0 / 10 / 25.0 | CFG |
| 022 | `statusline.cost.record_throttle_s` | float | 60 | CFG |
| 023 | `statusline.cost.rate_min_api_ms` | map | `{cc: 300000, backfill: 1800000}` | CFG |
| 024 | `statusline.cost.percentiles` | list | [0.75, 0.95] | CFG; the index method ("lower") is **NC** (parity: no interpolation) |
| 025, 026 | `statusline.window_age.max_depth` / `ps_timeout_s` | int/float | 6 / 1 | CFG (`internal/platform`, D4-EX-1 on Windows) |
| 027 | `statusline.context.cells` | int | 10 | CFG; half-up rounding **NC** (review #5.2) |
| 028 | `statusline.context.plain_max` / `red_from` | float | 50 (`>`) / 85 (`>=`) | CFG |
| 029 | `statusline.units.context`* | map | `{M_from: 1e6}` (else `K`) | CFG (consistent with T-037/T-042) |
| 030 | `statusline.theme.heat` | map | `{hue_max: 0.22, s: 0.85, v: 0.80}` | CFG |
| 031-035 | `statusline.limits.windows` / `projection_min_elapsed` / `projected_bands` / `absolute_bands` / `countdown_max_factor` | — | as P2r1 §6.2 | CFG |
| 036, 041 | — | — | 86400/3600/60 s, 1440 min boundaries | **NC**: calendar unit boundaries (a day is a day) |
| 037, 042 | `statusline.units.lines` / `statusline.units.tokens` | map | `{k_from: 10000, M_from: 1e6}` / `{k_from: 1000, M_from: 1e6}` | CFG |
| 038, 039 | `statusline.timer.min_ms` / `api_min_ms` | int | 60000 (`>`) / 60000 (`>=`) | CFG |
| 040 | `statusline.window_age.min_margin_ms` | int | 300000 | CFG |
| 043, 044 | `statusline.cost.burn_min_api_ms` / `basis_min_shown_usd` | int/float | 300000 / 0.005 | CFG |
| 045 | `statusline.sparkline.scale` | map | `k` fixed 1.0; floors `v` 1.0, `f` 0.1 | CFG (`1e-9` fallback T-114 is NC) |
| 046 | `statusline.sparkline.colors` | map | trail (70,170,190), fade 0.55→1.0, preempt (220,170,60), head (140,235,255) | CFG |
| 047, 107 | `statusline.queue.yellow_waiting_gt`* / `yellow_preempt_rate_gt`* | float | 0 / 0 | CFG (one rule serves the queue and the sparkline marker, review #17.3) |
| 048 | `statusline.kv.cells` | int | 4 | CFG; ceiling-quarter rounding **NC** (review #15) |
| 049, 050 | `statusline.kv.host_yellow_pct` / `host_shown_pct` | float | 5 / 0.5 | CFG |
| 051, 052 | `statusline.ttft.integer_from_s` / `yellow_s` | float | 10 / 8 | CFG |
| 053 | `statusline.power.wall_yellow_w` / `wall_red_w` | float | 1280 / 1520 | CFG. Keep the literals: deriving them as 0.80/0.95 × 1600 in floating point is not guaranteed to reproduce `1520` exactly at the `>` boundary |
| 054 | `statusline.transcript.read_cap_bytes` | int | 524288 | CFG (a read **step**, CONV-ABS-43) |
| 055-058 | `statusline.turn.dim_below_out` / `tokens.rebuild_excess` / `turn.floor_tps` / `turn.stale_factor` | int/int/float/float | 200 / 20000 / 15 / 4 | CFG |
| 059, 060 | `statusline.composition.image_chars` / `transcript.dedup_memory` | int | 2000 / 256 | CFG |
| 061-063 | — | — | sid `[:40]`, sha1 `[:16]`, short sha 7 | **NC**: cache file-name format shared with Python during shadow (P2r1 §6.3); git format |
| 064 | — | — | 9999 | **NC** sentinel (F-5) |
| 106, 110-112, 114, 115, 119 | — | — | min 2 points; bracket ≥ 2; zero tests; midpoint color; 1e-9; clamps; (hook median, C.3) | **NC**: structural or mathematical rules; another value would be meaningless |
| 108 | `statusline.idle.running_below`* | int | 1 | CFG |
| 109 | — | — | `round()` half-even, `" <1%"`, width 2 | **NC**: display format (parity BX) |
| 113 | derived from `statusline.theme.glyphs` (OD-02) | — | 8 levels, half-up | NC rule over a configurable glyph string |
| 116 | semantics of `statusline.rows` + `narrow_cols`; "COLUMNS unknown ⇒ wide" | — | — | CFG + NC |
| 117 | `statusline.subagent.units`* | map | `{M_from: 1e6, M_dp: 2, k_from: 1000, k_dp: 1}`; `mm:ss` | CFG if OD-14 keeps the path |
| 133 | — | — | 4,300-digit int limit | **NC** parity constant in the transcript decoder (O1 oracle is CPython 3.11; Go's JSON has no such limit) |
| 134, 135 | — | — | 300 ms debounce; 5 s subagent timeout | **EXT** |

### C.2 Proxy, CA, ledger (`internal/proxy`, `internal/ledger`, P3; `hylo ca`, P4)

| T | Key | Type | Default | Class |
|---|---|---|---|---|
| 065 | `proxy.sse_tap.max_line_bytes` | int | 64000 | CFG (OD-35) |
| 066, 067 | `proxy.failed_capture.keep`* / `max_chars`* | int | 20 / 50,000,000 | CFG (also needs a path key; legacy `~/dgx-llm-obs/` hard-coded, `PX:289`) |
| 068 | `proxy.decision_log.error_body_chars`* | int | 600 | CFG (decision-log text is OOS for parity) |
| 069 | `ledger.upstream_error.max_chars`* | int | 300 | CFG (shapes a D7 field value; default must stay 300 through cutover) |
| 070, 071 | — | — | duration 3/1 dp; account `[:8]` | **NC**: D7 ledger number and value format |
| 072, 073 | — | — | port 80 for `http` without port; status ≥ 400 | **NC**: URL and HTTP protocol semantics |
| 074-076 | `ca.backups_keep`* / `ca.regen_wait_s`*, `ca.regen_poll_s`* / `ca.keychain_delete_max`* | int/float/float/int | 3 / 30 / 0.5 / 10 | CFG (`internal/platform` darwin for 076); 075 dropped if `ca.restart_command` is dropped |
| 122 | `proxy.idle_timeout_s`* | float | 600 | CFG until OD-37 is ruled (HY-TIMEOUT-1 and HY-PASS-1 then split it into routed in-flight and pass-through rules) |
| 123 | — | — | TLS 1.2 minimum | **NC** (r7 T-2: protocol/security constant, no cipher key) |
| 124 | — | — | h2 keepalive | **NC**, only if hylo speaks h2 upstream (HY-PROTO-1 keeps h1↔h1) |
| 125 | — | — | key type/size, CA and leaf validity | **NC** in `hylo ca` (P4) with a comment (r7 §1.5) |
| 126 | `backend.connect_timeout_s` | float or none | none (OS) | CFG (OD-42) |
| 127 | `proxy.max_buffered_body_bytes`* | int or none | none | CFG (OD-54) |
| 128 | D16 bounded buffer | — | — | NEW-H (HY-WS-1; legacy unbounded, deviation approved by D16) |

### C.3 Exporter, hook, launcher, preflight, backfill, services

| T | Key | Type | Default | Class |
|---|---|---|---|---|
| 077, 078 | `exporter.session_limit` / `exporter.port` (+ `exporter.bind` loopback, HY-BIND-5) | int | 50 / 9210 | CFG |
| 079 | `exporter.est_chars_per_token`* | float | 4.0 | CFG (changes metric values, not names; D7 allows) |
| 080, 081 | — | — | session/account/device `[:8]`; passthrough `status == 200`; errors `>= 400` | **NC**: D7 label values and metric semantics |
| 129, 131 | — | — | backlog; request-line cap | **NC** (OS / Go `net/http` defaults; failure-mode only) |
| 130 | `exporter.read_header_timeout_s`* / `idle_timeout_s`* | float | none in legacy | NEW-H (HY-BIND-6, OD-33) |
| 082, 083, 085 | `hook.kev.threshold` / `timeout_s` / `state_chars` | float/float/int | 0.40 / 2.5 / 6000 | CFG |
| 084, 093 | — | — | 14; 20 s | **DROP** (dead) |
| 086 | `hook.kev.line_chars`* / `final_tail_chars`* | int | 400 / 800 | CFG |
| 087, 088, 118 | `hook.kev.tries`* / `early_stop_fraction`* / `early_stop_min_scores`* | int/float/int | 3 / 0.5 / 2 | CFG |
| 119 | — | — | upper median | **NC** (median definition; parity) |
| 089 | `hook.log.tail_chars`* / `hook.heuristic.quote_chars`* | int | 160 / 100 | CFG (the log line is read by the exporter, OD-23/OD-04) |
| 090-092 | `hook.colon_fake.min_chars`* / `hook.heuristic.max_sentence_chars`* / `hook.english.cjk_min_count`*, `cjk_min_count_ratio`*, `cjk_min_ratio`* | int/int/int,int,float | 20 / 200 / 12, 4, 0.02 | CFG |
| 094 | `run.hooks.stop_timeout_s`* / `run.hooks.prompt_timeout_s`* | int | 30 / 5 | CFG |
| 095, 096, 099, 121 | — | — | port ranges, start waits, `STALE_SEC`, visible-mode router | **DROP** (OD-19, D6) |
| 097 | `run.api_timeout_ms`* | int | 1,800,000 | CFG (also the default source for HY-TIMEOUT-1) |
| 098 | `run.statusline.refresh_interval_s`* / `run.statusline.padding`* | int | 4 / 0 | CFG. Coupling rule: TTL equal to the refresh interval makes every tick fetch (strict `>`, pass-3 r2); `hylo doctor` should warn when `statusline.telemetry.ttl_s` ≠ `run.statusline.refresh_interval_s` |
| 100 | `doctor.preflight_timeout_s`* | float | 4 | CFG (BC-PF-001) |
| 101, 120 | — | — | ssh keepalive; tunnel ports | **OOS** (BC-SV-002) |
| 102 | `prices.<family>` | table | legacy table | CFG (OD-13) |
| 103, 104 | `cost.backfill.min_usd`* / `min_api_ms`* / `days`* | float/int/int | 1.0 / 1,800,000 / 30 | CFG (`min_api_ms` = T-023's backfill value: one key) |
| 105 | shares `statusline.turn.floor_tps`, `stale_factor` | — | — | CFG; the `max(o,1)` and `<=` variant is **NC** (parity, P2r1 §7 I7) |
| 132 | `service.restart_delay_s`* | int | 10 | CFG for the per-OS units (`docs/PLAN.md` §4 line 61: launchd / systemd user unit / Windows scheduled task) |

### C.4 hylo keys with no legacy value (policy 16 rationale required when introduced)

`proxy.listen_host` / `proxy.listen_port` (HY-BIND-1/3, OD-19), the admission allow-list (HY-BIND-4), the UI token (D16), HY-BIND-6 read-header
and idle timeouts for every listener, HY-TIMEOUT-1's routed in-flight timeout (default derived from `run.api_timeout_ms`), the HY-BIND-6
WebSocket idle limit (> the observed 20 s ping, r8 §2.2), `backend.tls.ca_file` (OD-41), the D16/HY-WS-1 buffer bound, and the OD-34 proxy
credential if adopted. None has a parity default; each needs its own rationale.

### C.5 Totals

| Class | Rows |
|---|---|
| CFG (config key, default = legacy) | 92 (incl. split rows; 37 keys proposed this round, marked `*`) |
| NC (named constant, reason given) | 27 |
| DROP | 8 (T-084, T-093, T-095, T-096, T-099, T-121, and T-075 if `ca.restart_command` goes; T-117 if OD-14 drops `--subagent`) |
| EXT | 2 (T-134, T-135) |
| OOS | 2 (T-101, T-120) |
| NEW-H with a legacy-side T-row | 2 (T-128, T-130) |

(Rows that split into a CFG part and an NC part, e.g. T-024, T-027, T-048, T-105, T-116, are counted once, under CFG.)

---

## D. NFR catalogue update

### D.1 Performance

| NFR | Legacy behavior and numbers | BC / OD / T |
|---|---|---|
| P-1 One status line run fits inside Claude Code's scheduler | Triggers: each assistant message, `/compact`, mode changes, a 4 s tick; debounced 300 ms; a newer trigger cancels the running one (T-098, T-134). Network work per run: at most one VM query (only when the TTL has passed; TTL = refresh ⇒ every tick fetches), per-operation timeout 1.5 s (F-6). Git lookup cached 5 s. `ps` walk ≤ 6 × 1 s, once per session. Cost-history write ≤ once a minute. The session cache file is re-read and rewritten up to 3 times per run (P2r2 §0) | BC-SL-040, BC-SL-041, BC-SL-010, BC-SL-023, BC-SL-053; T-001, T-005, T-013, T-022, T-025, T-026 |
| P-2 Parse bounds | Transcript: incremental from the cached offset; ≥ 512 KiB per run, extended to the next newline with **no upper bound** (CONV-ABS-43; lines up to 1.36 MB measured); usage dedup memory 256 ids; a format-marker change (`mixv6`) forces one full re-parse. VM response: read whole, no size cap (`SL:171`). Hook: reads the **whole** transcript on every Stop (`HK:68-83`), no cap | BC-SL-032, BC-SL-068/098, BC-HK-008; T-054, T-060 |
| P-3 Proxy adds no streaming latency where it matters | SSE (any host) relayed chunk by chunk through the tap, tail buffer ≤ 64,000 B; `/v1/messages*` JSON or ≥ 400 bodies buffered so the addon can read them; **every other non-SSE response buffered in full by mitmproxy, no cap** (CONV-ABS-44); WebSocket payloads relayed but retained in memory (F-3) | BC-PX-014, BC-PX-016, BC-PX-037, BC-PX-045; T-065, T-127, T-128; **OD-54** |
| P-4 Routed flows: long responses allowed | Client timeout 30 min (`API_TIMEOUT_MS`); proxy idle cut 600 s (lower than the client timeout); no total-duration cap on the proxy; pass-through SSE up to 3,600 s and WebSockets up to 3 h 51 min observed uncut | BC-LN-005, BC-PX-049; T-097, T-122; OD-37; HY-TIMEOUT-1, HY-PASS-1 |
| P-5 Exporter scrape cost | full ledger rescan whenever the size changed: O(ledger) per scrape after growth; single-threaded | BC-EX-003, BC-EX-022, BC-EX-026, BC-EX-027; OD-39 |
| P-6 Stop hook latency | Kev 13 ms per pass measured (Kev-0.8B, `HK:127`); up to 3 passes, early exit after 2 when a call took > 1.25 s; Claude Code kills the hook at 30 s | BC-HK-010, BC-HK-022; T-083, T-087, T-088, T-094, T-118 |

### D.2 Reliability

| NFR | Legacy behavior | BC / OD / T |
|---|---|---|
| R-1 Status line exits 0 on every path, except the documented crash paths | `main()` and `--subagent` run under one guard that prints the 29-byte degraded line and exits 0 (byte-exact, owner ruling O2). Exceptions: CP-X01/X02 import-time env parse (traceback, empty stdout, exit 1), CP-X03 the guard's own `print` fails (EPIPE), CP-X04 signals. Sticky transcript crashes are fixed in Go (D4-EX-2) | BC-SL-001, BC-SL-087, BC-SL-068/098; CP-X01..X04; CONV-ABS-41 |
| R-2 Telemetry degradation ladder | green only while the latest fetch succeeded (at default TTL); yellow with `(~Ns old)` from the **first** failed fetch; last-known kept ≤ 300 s on fetch runs, any age on in-TTL runs; `◌ DGX ?` without a sample; serving-down states from `up` | BC-SL-041, BC-SL-043, BC-SL-091; T-003, T-004; CONV-ABS-42; **OD-55** |
| R-3 No fabricated zeros | missing series omit segments | BC-SL-074 and the KV/TTFT rows (pass-3 index) |
| R-4 Cache durability | atomic `mkstemp` + `os.replace`; concurrent sessions can lose a cost-history update, repaired by the next minute's write (accepted, WIDGETS) | BC-SL-052; T-022 |
| R-5 Proxy never breaks traffic on observability failures | ledger and log appends swallow `OSError`; header capture fully guarded. Exceptions: `note()` raising on unencodable text stops the hook (OD-45); response-hook crashes P-S1..S4 (OD-18); request-hook crashes silently re-lane to Anthropic (OD-08) | BC-PX-028, BC-PX-048; OD-08, OD-18, OD-45 |
| R-6 Upstream failure handling | no retry, no backoff, no connect timeout (OS), eager connect couples the lanes; failures logged by the `error` hook (36 `No route to host` on 2026-11-11, 18 + 24 connect refused) | BC-PX-024, BC-PX-047; OD-17, OD-42; T-126 |
| R-7 Stop hook | no top-level guard: crash → exit 1, no stdout (H-01..H-09); H-04 production-reachable | BC-HK-019, BC-HK-022; OD-12 |
| R-8 Exporter | a poison line crashes `rebuild()`; at startup this loops under `KeepAlive` every ~10 s with zero bytes served; counters reset on restart (accepted, `EX:11-13`) | BC-EX-021; OD-11; T-132 |
| R-9 Supervision | launchd `KeepAlive` for exporter and tunnel; tunnel dead-peer detection ~90 s; hylo: per-OS units | BC-SV-001/002 (OOS); T-101, T-132; `docs/PLAN.md` §4 line 61 |

### D.3 Security

| NFR | Legacy behavior | BC / OD / requirement |
|---|---|---|
| S-1 Network exposure | proxy listens on all interfaces and admits RFC 1918 clients, which then use the backend key; exporter on `0.0.0.0:9210`, unauthenticated, exposing project/user/session labels. Both accepted by the owner for legacy. Production: all 17,156 client connections came from loopback (r8 §0) | OD-24 (R), OD-27 (R), OD-34; HY-BIND-1..6; BC-EX-001 |
| S-2 Credential handling | backend key from a file (`PX:88-95`), cached for the process; **unreadable key ⇒ the client's own `Authorization`/`x-api-key` go to the backend** (P-R4); on the backend lane only `Authorization` is replaced, so `x-api-key` and cookies are forwarded; Kev key accepted as an env **value**; backend traffic is plain HTTP on the LAN by default (bearer key in clear) | OD-06, OD-07; P2r1 §6.1 row 25; D16 redaction |
| S-3 Upstream TLS | verification always on (chain + SAN hostname), trust anchor = certifi snapshot only (OS store and keychain ignored); TLS ≥ 1.2; 7 self-signed rejections observed; `SSLKEYLOGFILE` inherited from the shell would log session keys | BC-PX-047; OD-41; HY-TLS-1, HY-TLS-3; T-123 |
| S-4 CA | RSA 2048, 10-year CA, 199-day leaves; trusted via `NODE_EXTRA_CA_CERTS` and optionally the login keychain (`trustRoot`), which a Go OS-store verifier would also trust for upstream (cutover hygiene) | T-125; P2r7 T-1 point 3 |
| S-5 Data at rest | failed DGX request bodies (≤ 50,000,000 chars, ≤ 20 files) in `~/dgx-llm-obs/`, may hold code or secrets; ledger grows without rotation; cache files are `0600` (`mkstemp`), the ledger uses the default umask | BC-PX-021; T-066, T-067 |
| S-6 Command execution | `DGX_PROXY_RESTART_CMD` run with `shell=True`; trust-CLI subprocesses (`security`, `openssl`, `pgrep`) have **no timeout** | `PX:719-722,567-606` |
| S-7 Owner choices | permission prompts skipped and sandbox off by default | BC-LN (launcher rows); P2r2 §6.8 |

### D.4 Operability

| NFR | Legacy behavior | BC / OD |
|---|---|---|
| O-1 Exporter stall | one idle or slow client blocks every scrape (no socket timeout, one thread, backlog 5); nothing is logged; the status line's `☾ idle` freezes (WIDGETS troubleshooting) | BC-EX-026; OD-33; T-129, T-130 |
| O-2 Exporter crash loop | poison line ⇒ restart every ~10 s forever, zero bytes, no alert | BC-EX-021; OD-11; T-132 |
| O-3 Silent failures | the 600 s idle cut on pass-through flows leaves no ledger trace (r8 §1.1); `error()` filters non-`/v1/messages` paths | BC-PX-024, BC-PX-049; OD-37 |
| O-4 Logs and growth | per-window mitmdump logs never deleted (one line per WebSocket message and ping); ledger and hook log never rotated; failed-request captures capped at 20 | T-066; P2r7 W-1 |
| O-5 Health and diagnostics | no exporter or proxy health endpoint; preflight (4 s TCP connect, three error classes) becomes `hylo doctor` | BC-PF-001, BC-PF-002; T-100 |
| O-6 Config validation | malformed numeric env crashes at import (status line, hook, exporter); booleans are per-variable string tests (`DGX_STATUSLINE=true` disables) | BC-SL-087; OD-05 |

### D.5 Portability (D5)

| Concern | Legacy (macOS only) | hylo handling |
|---|---|---|
| Process ancestry for `⌂` | `ps -o ppid=,comm=,lstart=` + `time.strptime` in the C locale; depth 6, 1 s timeout | `internal/platform` per OS; Windows fallback glyph (D4-EX-1); BC-SL-023, BC-SL-080 |
| Cache file names | raw session id in one name, sanitized in another | OD-03 (Windows-only sanitizing); BC-SL-052, BC-SL-070, BC-SL-078 |
| Supervision | launchd plists (`KeepAlive`, implicit 10 s throttle) | per-OS units with `service.restart_delay_s` (T-132) |
| Proxy launch and ports | zsh, `nc`, `lsof`, `flock` (absent on stock macOS) | one in-process listener (OD-19) |
| CA trust | `security` / keychain, `openssl` CLI, no timeouts | `hylo ca` per OS (P4) |
| Interpreter-dependent parsing | CPython 3.11 int-digit limit and `fromisoformat` grammar (status line, hook) vs 3.9.6 (exporter) | parity oracles O1 / OD-15; T-133 |
| Time zones | naive local timestamps in the ledger and in the exporter's parse | OD-22 |
| Paths | `~`, `$TMPDIR`, `~/.cache/dgx-llm` | `paths.*` keys; `%APPDATA%` (`docs/PLAN.md` line 105) |

### D.6 Missing NFRs (expected, not found), updated

Ledger rotation or size cap; exporter and proxy health endpoints; upstream retry/backoff and a connect timeout; a size cap on buffered bodies
(T-127); bounded WebSocket retention (T-128); a total deadline on network calls (F-6); timeouts on trust-CLI subprocesses; config validation at
load; time zone in ledger timestamps; automated tests.

---

## E. Owner items (new)

| ID | St | Decision | Component | Bites | Recommendation |
|---|---|---|---|---|---|
| **OD-54** | P | **Pass-through buffering and body-size bound.** Legacy buffers every non-SSE response outside `/v1/messages*` in full (mitmproxy default), and every request body, with no size cap (T-127, CONV-ABS-44) | proxy | P3 | Approved deviation (unobservable in byte parity): relay pass-through responses as they arrive; buffer only where the addon must read the body (`/v1/messages*` JSON or ≥ 400, request bodies for routing), with `proxy.max_buffered_body_bytes` (legacy default none through cutover, then a finite value as a labeled judgment call) |
| **OD-55** | P | **Thresholds that are inert at legacy defaults** (T-003 F-1, T-008 F-2, T-009 F-3, and T-007's change to gap pruning F-4), and the WIDGETS Health-dot text "Green: VM sample < 15 s old", which does not describe the default behavior | status line, docs | P1 | Keep all four as config keys (D15) with a "reachable only when …" note; reproduce legacy exactly (D4); correct the WIDGETS sentence to "green while the latest fetch succeeded; yellow from the first failed fetch" (a public-doc edit, owner-gated) |
| **OD-56** | P | **Timeout semantics of D15 `*timeout_s` keys.** Legacy network timeouts are per socket operation (F-6); Go's natural form is a total deadline | config, status line, hook, proxy | P1, P3, P4 | Total deadline, equal to the legacy value, documented on every key; deviation unobservable on recorded inputs (no recorded VM or Kev response dribbles past the limit) |
| **OD-57** | P | **Policy-16 rationale sign-off.** Confirm the 20 derived rationales (§B.2) in one answer and supply the 25 missing ones in 7 groups (§B.3) | all | P1-P4 (each key's comment) | Answer per group; "labeled judgment call" is an acceptable answer under policy 16 |

---

## Delta Summary

- New items added:
  - Thresholds: **30 new rows** (T-106..T-135): 16 literal thresholds in source (status line 12, hook 2, plist 1, dead launcher 1) and 14 implicit
    defaults in effect (mitmproxy 7, Python runtime/library 4, launchd 1, Claude Code external 2).
  - Reachability findings: 4 new (F-1 `STALE_OK` unreachable at the default TTL, F-3 history cap inert, F-4 `SPARK_MAX_AGE` is gap pruning,
    F-5 9999 is a sentinel), 1 timeout-semantics finding (F-6), 1 restated (F-2, pass-3).
  - Census: 522 AST literal sites + 10 string sites + 24 shell/plist sites classified; 0 unclassified; every catalogued row tied to a site.
  - Config map: all 135 rows mapped; 37 keys proposed; 27 named-constant rows with reasons; hylo-only keys listed (§C.4).
  - NFR catalogue: rewritten in 5 categories with BC/OD/T citations (§D), 4 new missing-NFR entries.
  - Owner items: OD-54..OD-57.
- Existing items refined: 52 UNKNOWN rationales → **28 resolved** (19 derived for bulk confirmation, 4 convention, 5 dead/obsolete),
  **24 still UNKNOWN**; plus 1 new row without rationale (T-117) → **25 on the owner list**. Catalogue rows refined: T-045, T-066, T-086, T-088.
  Retractions: **CONV-ABS-41..44** (broad pass-4 §1 prose).
- Threshold totals: catalogued 105 · new 30 · total 135 · rationale resolved this round 28 of 52 (+29 of the 30 new rows carry a rationale) ·
  still UNKNOWN 25 (24 old + T-117).

## Remaining Gaps (verbatim-carryable)

1. Owner answers for OD-57: §B.2 bulk confirmation (20 rows) and §B.3 seven groups (25 rows). Until then those defaults carry "UNKNOWN — owner to
   confirm" in code comments.
2. T-132 launchd `ThrottleInterval` default 10 s is cited from P2r3 E-3 as "documented, not verified": verify against the launchd.plist manual
   (local `man launchd.plist`, read-only) before it becomes `service.restart_delay_s`'s rationale.
3. T-125 leaf validity "199 days" comes from P2r3 §3.1 (m/`certs:41`); re-read that mitmproxy source line once to confirm the figure before it is
   copied into a `hylo ca` constant comment.
4. T-083 rationale uses Kev-0.8B's measured 13 ms/pass; the launcher pins kev-4b (`L:155`). If the owner has a kev-4b latency figure, it replaces
   the measured basis.
5. Pass 5 (sibling) should record two conventions found here: Python `round()` half-even in the composition (T-109) vs half-up elsewhere, and
   per-operation network timeouts (F-6).
6. The external recording rules behind `dgx_preempt:rate5m`, `dgx_ttft:p95_30m`, `dgx_tokens:gen_rate5m` hold thresholds of their own (the
   5-minute preemption window, the 30-minute TTFT window) outside `legacy/`; they are P6 telemetry config (OD-20), not catalogued here.
7. Owner decisions: OD-54..OD-57 (new), in addition to the pending list carried by passes 2 and 3.

## Novelty Assessment

Novelty: SUBSTANTIVE

Removing this round would change how the system is specified. Thirty thresholds were missing from the catalogue, among them the ones that shape
production behavior without appearing as legacy literals: the 600 s inactivity cut (T-122, which fired once in production), unbounded body
buffering on every pass-through response (T-127, OD-54, and a broad-pass NFR claim retracted as CONV-ABS-44), the exporter's backlog and missing
socket timeout (T-129/T-130), and the launchd restart cadence of the crash loop (T-132). The reachability analysis changes the specification of
four status line keys (F-1, F-3, F-4, F-5), and the documented health-dot rule does not match legacy at the default TTL (OD-55). F-6 changes what
every D15 timeout key means (OD-56). Four broad-pass NFR statements were wrong and are retracted (CONV-ABS-41..44).

## Convergence Declaration

Another round needed: the new rows and the four retractions need a round-2 audit against the 5 hallucination classes; Remaining Gaps 2-4 are
source checks that can change a rationale; and §C's 37 proposed keys need a consistency pass against pass 5's naming conventions and OD-01.

## State Checkpoint

```yaml
pass: 4
round: 1
status: complete
timestamp: 2026-11-14T09:30:00Z
novelty: SUBSTANTIVE
files_scanned: all 11 legacy files (AST census of 6 .py; grep of claude-dgx, coordinator, 2 plists; targeted reads SL:1-153,155-480,480-890,940-1245; PX:1-30,76-100,168-215,280-415,555-735; EX:1-30,185-240,262-414; HK:25-275; PF all; BF:1-40,84-100)
census: {ast_sites: 522, threshold: 212, format: 49, unit: 42, incidental: 219, string_numeric_defaults: 10, shell_plist_threshold_sites: 24, unclassified: 0}
thresholds: {catalogued: 105, new: 30, total: 135, unknown_before: 52, resolved: 28, resolved_breakdown: {derived_bulk_confirm: 19, convention: 4, dead_or_obsolete: 5}, still_unknown: 25}
retractions: [CONV-ABS-41, CONV-ABS-42, CONV-ABS-43, CONV-ABS-44]
conv_abs_unused: [45, 46]
new_owner_items: [OD-54, OD-55, OD-56, OD-57]
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p4r1/
next: pass 4 round 2 (audit round 1; Remaining Gaps 2-5)
```
