# Pass 4: NFR Catalog — hylo-legacy

## 1. NFRs by category

### Performance
| NFR | Implementation | Evidence |
|---|---|---|
| Status line must finish well inside Claude Code's refresh cadence (4 s tick, 300 ms debounce, in-flight cancel) | one VM round trip per TTL (4 s) with disk cache; 1.5 s HTTP timeout; incremental transcript parse capped at 512 KB/refresh; git lookups cached 5 s; `ps` walk once per session | `dgx_statusline.py:74,81,99,952,273-275` |
| Proxy must not add streaming latency | `response.stream` pass-through tap returns each chunk unchanged; only JSON/error bodies buffered; WebSocket payloads never touched | `dgx_proxy.py:191-208,398-410,16-20` |
| Stop hook must never hang Claude Code's stop path | Kev timeout 2.5 s, ≤ 3 tries with early exit; registered timeout 30 s | `auto_continue.py:34,124-138`, `claude-dgx:161` |
| Exporter scrape cost | full ledger rescan only when the file size changed ("ledger is small, a few MB") | `dgx_ledger_exporter.py:11,275-287` |
| Known costly paths | hook reads the entire transcript each Stop (`auto_continue.py:68`); exporter rescans the whole ledger on every growth (O(file) per scrape) | — |

### Reliability / degradation
| NFR | Implementation | Evidence |
|---|---|---|
| Status line never blank, never non-zero | top-level catch -> `statusline degraded`; all I/O helpers swallow errors (import-time env parse is the exception, see BC-SL-001) | `dgx_statusline.py:1238-1245` |
| Telemetry degradation ladder | fresh -> stale (≤ 300 s, age shown) -> dead `◌ DGX ?`; serving-down states | `dgx_statusline.py:693-730` |
| No fabricated zeros | missing series omit keys/segments (KV hidden, sparkline keys omitted, NaN TTFT hidden) | `:331-332,757,793` |
| Atomic cache writes | mkstemp + os.replace | `:198-206` |
| Ledger/log writes never break traffic | try/except OSError around appends; header capture fully guarded | `dgx_proxy.py:56-74,176-190` |
| Upstream failure visibility | `error` hook + launch preflight | `dgx_proxy.py:311-323`, `claude-dgx:60-68` |
| Long-line parser freeze fixed | finish a line longer than the cap | `dgx_statusline.py:1045-1052` |
| Service supervision | launchd KeepAlive for exporter and tunnel; ssh keepalives | `deploy/*.plist` |
| Missing / accepted | no retry/backoff on VM or upstream; exporter counters reset on restart (accepted, exporter `:12-13`); concurrent cost-history writes can lose an update (accepted, WIDGETS) | — |

### Security
| NFR | Implementation / gap | Evidence |
|---|---|---|
| Secrets by file, not inline | DGX key `~/.config/dgx-llm/api-key`, Kev key file or env | `dgx_proxy.py:88-95`, `auto_continue.py:97-102` |
| CA trust scoped to Node | `NODE_EXTRA_CA_CERTS`; keychain trust optional via the trust CLI | `claude-dgx:80`, `dgx_proxy.py:625-645` |
| **Gap**: backend traffic is plain HTTP on the LAN carrying a Bearer key | `DGX_UPSTREAM=http://…` default | `dgx_proxy.py:79,164` |
| **Gap**: only `Authorization` is replaced on the DGX lane | `x-api-key` (API-key accounts) and other Anthropic headers would be forwarded to the backend | `dgx_proxy.py:161-166` |
| **Gap**: exporter binds `0.0.0.0:9210`, unauthenticated | project/user/session labels exposed to the LAN | `dgx_ledger_exporter.py:414` |
| **Gap**: statusline session cache path uses raw `session_id` | no sanitizing (mix cache does sanitize) | `dgx_statusline.py:1215` |
| **Gap**: full failed request bodies written to disk | may contain secrets/code; `~/dgx-llm-obs/` | `dgx_proxy.py:288-299` |
| Permissions bypass and sandbox off by default | owner choice (`--dangerously-skip-permissions`) | `claude-dgx:117-139,165-167` |
| Restart hook runs a shell string | `DGX_PROXY_RESTART_CMD` with `shell=True` | `dgx_proxy.py:719-722` |

### Observability
Ledger (11 event types), decision log, hook log, failed-request captures, Prometheus exporter (Pass 1 §4.7);
`flow_detail=1` mitmdump log per window. No tracing, no structured logs beyond the ledger, no health endpoint
on the exporter, no metrics for the proxy itself (process count, errors) except via ledger events.

### Scalability
One mitmdump per window (8 observed) — PLAN.md §6 moves to one per user. Exporter keeps 50 recent sessions.
Ledger grows unbounded (no rotation in code).

### Portability (D5 gap list)
macOS-only today: `ps -o lstart` + `time.strptime` C-locale format, `security`/keychain, `nc`, `lsof`, `flock`
(not stock macOS), launchd plists, zsh launcher, `$TMPDIR`. Paths assume POSIX `~`.

## 2. THRESHOLD CATALOG

Rationale codes: **D** documented in review/WIDGETS/comment (quoted source); **J** labeled judgment call;
**C** convention; **UNKNOWN — owner to confirm** (policy 16). Line numbers are legacy file:line.

### Status line (`dgx_statusline.py`)
| # | Value | Meaning | file:line | Rationale |
|---|---|---|---|---|
| T-001 | 4 s | `DGX_SL_TTL` VM fetch/cache TTL | :74 | D: "match refreshInterval" (:50, WIDGETS Tunables) |
| T-002 | 2 | `DGX_SL_ROWS` default | :75 | C (two-row design) |
| T-003 | 15 s | `STALE_OK` green-dot freshness | :79 | UNKNOWN — owner to confirm (plausibly the 15 s VM scrape interval cited in review #16.1) |
| T-004 | 300 s | `KEEP_DEAD` last-known retention | :80 | UNKNOWN — owner to confirm |
| T-005 | 1.5 s | `HTTP_TIMEOUT` VM query | :81 | UNKNOWN — owner to confirm (comment gives measured RTT ~25 ms, not why 1.5 s) |
| T-006 | 12 pts | `SPARK_PTS` | :82 | J: "kept short: long flats read as blobs" |
| T-007 | 90 s | `SPARK_MAX_AGE` history age | :83 | UNKNOWN — owner to confirm |
| T-008 | 2 s | `HIST_MIN_GAP` | :84 | UNKNOWN — owner to confirm |
| T-009 | 32 pts | history cap saved | :350 | UNKNOWN — owner to confirm |
| T-010 | 1800 s | `RL_KEEP` plan-limit smoothing | :85 | UNKNOWN — owner to confirm (purpose "no blinking" given, 30 min value not) |
| T-011 | 300 s | `IDLE_AFTER` | :90-93 | J: labeled judgment call (review #20.2) |
| T-012 | 30.4 MTok/month | `MIN_BASIS_MTOK_MONTH` ⛏ floor | :94-98 | D: 1M DGX tokens/24 h (review #11.1) |
| T-013 | 5 s | `GIT_TTL` | :99 | C: "docs' example pattern" |
| T-014 | 72 cols | `NARROW_COLS` drop row 2 | :100 | UNKNOWN — owner to confirm |
| T-015 | 20 | `TTFT_MIN_N` | :124 | D: below 20 samples p95 = max (1/20 = 5%) |
| T-016 | [1m] | inline box-rate window | :118 | D: review #17 A+ (sparkline timescale) |
| T-017 | [30m] | TTFT count window | :121 | D: matches `dgx_ttft:p95_30m` (review #18) |
| T-018 | 30 d | `COST_WINDOW_S` | :218 | D: owner design (review #11 revisit) |
| T-019 | $1 | `COST_MIN_USD` | :219 | D: DGX p75 was $0.13 from probes (review #11 revisit) |
| T-020 | 10 | `COST_MIN_N` cold start | :220 | D (owner decision, review #11 revisit); numeric derivation not stated |
| T-021 | $25 | `COST_FALLBACK_YELLOW` | :221 | D (owner decision, review #11 revisit); derivation not stated |
| T-022 | 60 s | `record_cost` throttle | :232 | UNKNOWN — owner to confirm |
| T-023 | 300,000 ms / 1,800,000 ms | min API time for $/h in history (cc / backfill) | :253 | D: same as display / approximate spans (:214-215) |
| T-024 | p75 / p95, index `int(q*(n-1))` | dynamic color percentiles | :261 | D: owner design; index method UNKNOWN — owner to confirm (no interpolation) |
| T-025 | 6 levels | `ps` ancestor walk depth | :279 | UNKNOWN — owner to confirm |
| T-026 | 1 s | `ps` timeout | :281 | UNKNOWN — owner to confirm |
| T-027 | 10 cells, half-up | thermometer resolution | :426 | D: review #5.2 |
| T-028 | 50% / 85% | thermometer plain / bold red | :430-434 | D: 85% leaves ~117K before ~967K auto-compact (review #5.1) |
| T-029 | 1e6 / 1000 | context denominator M/K | :435-436 | C |
| T-030 | hue 0.22, s 0.85, v 0.80 | heat gradient | :146-147 | UNKNOWN — owner to confirm (aesthetic) |
| T-031 | 5 h / 7 d | plan window lengths | :501 | C (Anthropic window definitions) |
| T-032 | 10% elapsed | projection vs absolute bands | :517 | D: "projection is noise" early (review #12 revisit) |
| T-033 | >100 red, ≥80 yellow | projected-use colors | :519 | D: review #12 revisit |
| T-034 | >90 red, >70 yellow | absolute bands | :521 | D: 70 = pace, 90 = throttling imminent (review #12.3) |
| T-035 | 1.15 × window | countdown visibility | :523 | UNKNOWN — owner to confirm |
| T-036 | 86400 / 3600 s | countdown units | :524-529 | C |
| T-037 | 10,000 / 1,000,000 | lines exact/k/M | :856-859 | D: keep row 1 narrow (review #8.1) |
| T-038 | > 60,000 ms | timer shown | :540 | UNKNOWN — owner to confirm (WIDGETS states "after 1 min", not why) |
| T-039 | ≥ 60,000 ms | API time shown | :551 | UNKNOWN — owner to confirm |
| T-040 | ≥ 300,000 ms | `⌂` margin over elapsed | :559 | D: avoid repeating elapsed (:554-556); 5 min value J-unlabeled |
| T-041 | 1440 min | `⌂`/idle day format | :561,828 | C |
| T-042 | 1e6 / 1000 | token compact units | :869-873 | D: approved mockup (review #10 revisit) |
| T-043 | 300,000 ms | `$/h` minimum API time | :622 | D: "below that the ratio is noise" |
| T-044 | 0.005 | `⛏` minimum shown | :634 | D: "skip sub-half-cent noise" |
| T-045 | k fixed 1.0; floors v 1.0, f 0.1 | sparkline scale | :648-649 | D: review #17.1 |
| T-046 | fade 0.55..1.0; RGB (70,170,190), (220,170,60), (140,235,255) | sparkline colors | :680-689 | UNKNOWN — owner to confirm (aesthetic) |
| T-047 | q > 0 or preempt > 0 | queue yellow | :740 | D: review #14 |
| T-048 | ceil quarters, 4 cells | KV bar | :759 | D: review #15 |
| T-049 | > 5% | host-share yellow | :760 | D: THRESHOLDS §8b measured (external doc; re-validate under LMCache, review #15.3) |
| T-050 | > 0.5% | host share displayed | :763 | UNKNOWN — owner to confirm |
| T-051 | ≥ 10 s | TTFT integer format | :795 | D: buckets 20/40/80/… (review #18.2) |
| T-052 | > 8 s | TTFT yellow | :799 | D: THRESHOLDS §8b (external doc) |
| T-053 | > 1520 W / > 1280 W | wall power red/yellow | :812 | D: 95% / 80% of 1,600 W rating |
| T-054 | 524,288 B | `_READ_CAP` per refresh | :952 | UNKNOWN — owner to confirm |
| T-055 | 200 tokens | `TURN_DIM_OUT` | :967 | D: replay, latency-dominated (review #16 follow-up) |
| T-056 | 20,000 tokens | `REBUILD_EXCESS` | :968-972 | D: measured (normal max 4,145; smallest rebuild 61,901) |
| T-057 | 15 tok/s | `TURN_FLOOR_TPS` | :973 | D: harness per-agent decode floor |
| T-058 | 4× | `TURN_STALE` | :974 | J: margin for slow prefill (:962-966) |
| T-059 | 2,000 B | image byte estimate | :1137,1149 | UNKNOWN — owner to confirm |
| T-060 | 256 ids | dedup id memory | :1153 | UNKNOWN — owner to confirm |
| T-061 | 40 chars | mix cache sid truncation | :1017 | UNKNOWN — owner to confirm |
| T-062 | 16 hex | git cache key length | :405 | C |
| T-063 | 7 chars | detached HEAD short sha | :389 | C (git short sha) |
| T-064 | 9999 s | default age when `ts` missing | :325 | UNKNOWN — owner to confirm |

### Proxy (`dgx_proxy.py`)
| # | Value | Meaning | file:line | Rationale |
|---|---|---|---|---|
| T-065 | 64,000 B | SSE tap tail cap | :368,408 | UNKNOWN — owner to confirm ("runaway line guard") |
| T-066 | 20 files | failed-request captures kept | :291-292 | UNKNOWN — owner to confirm |
| T-067 | 50,000,000 chars | max captured body | :295 | UNKNOWN — owner to confirm |
| T-068 | 600 chars | error body in decision log | :287 | UNKNOWN — owner to confirm |
| T-069 | 300 chars | upstream error message | :322 | UNKNOWN — owner to confirm |
| T-070 | 3 dp / 1 dp | duration rounding (replies / ws) | :238,273,213,536 | C |
| T-071 | 8 chars | account hint length | :332,335 | UNKNOWN — owner to confirm |
| T-072 | 80 | default upstream port | :83 | C (HTTP) |
| T-073 | 400 | error status cut | :205,283 | C (HTTP) |
| T-074 | 3 | CA backups kept | :564 | UNKNOWN — owner to confirm |
| T-075 | 30 s / 0.5 s | CA regeneration wait / poll | :723-725 | UNKNOWN — owner to confirm |
| T-076 | 10 | keychain delete loop max | :692 | UNKNOWN — owner to confirm |

### Exporter (`dgx_ledger_exporter.py`)
| # | Value | Meaning | file:line | Rationale |
|---|---|---|---|---|
| T-077 | 50 | `DGX_SESSION_LIMIT` | :24 | UNKNOWN — owner to confirm |
| T-078 | 9210 | port | :25 | UNKNOWN — owner to confirm |
| T-079 | bytes/4 | prompt-token estimate | :192-193 | C: "~4 chars per token" heuristic |
| T-080 | 8 chars | session label length | :382 | UNKNOWN — owner to confirm |
| T-081 | 200 | passthrough counted only for status 200 | :206 | UNKNOWN — owner to confirm (2xx other than 200 excluded) |

### Stop hook (`auto_continue.py`) and launcher
| # | Value | Meaning | file:line | Rationale |
|---|---|---|---|---|
| T-082 | 0.40 | Kev threshold | auto_continue.py:33; claude-dgx:150-152 | D: tuned 2026-11-10 after a 0.487 fake stop |
| T-083 | 2.5 s | Kev timeout | auto_continue.py:34 | UNKNOWN — owner to confirm (purpose "never hang" given) |
| T-084 | 14 | `KEV_MESSAGES` (unused) | :35 | UNKNOWN — owner to confirm (dead) |
| T-085 | 6000 chars | Kev state size | :36,90 | UNKNOWN — owner to confirm |
| T-086 | 400 / 800 chars | per-line clip / final-message tail | :83,89,91 | D (purpose: tail carries signal, :87-88); values UNKNOWN — owner to confirm |
| T-087 | 3 tries, median | Kev scoring | :124-138 | D: ±0.09 single-draw noise |
| T-088 | KEV_TIMEOUT/2 | early-stop latency | :133 | J: "slow endpoint" |
| T-089 | 160 / 100 chars | log tail / heuristic quote | :215,268 | UNKNOWN — owner to confirm |
| T-090 | > 20 chars | colon-fake minimum length | :236 | UNKNOWN — owner to confirm |
| T-091 | < 200 chars | heuristic sentence length | :179 | UNKNOWN — owner to confirm |
| T-092 | ≥ 12, or ≥ 4 and > 2% | non-English CJK test | :190 | J: "not just a quoted word or two"; values UNKNOWN — owner to confirm |
| T-093 | 20 s | `opus_verdict` timeout (dead) | :141 | UNKNOWN — owner to confirm (dead code) |
| T-094 | 30 s / 5 s | Stop / UserPromptSubmit hook timeouts | claude-dgx:161,158 | UNKNOWN — owner to confirm |
| T-095 | 8090-8143 | proxy port range | claude-dgx:72-73; coordinator:10 | UNKNOWN — owner to confirm |
| T-096 | 40 × 0.25 s | proxy start wait | claude-dgx:77; coordinator:35 | UNKNOWN — owner to confirm |
| T-097 | 1,800,000 ms | `API_TIMEOUT_MS` | claude-dgx:104 | D: "local model is slow; allow long responses" |
| T-098 | 4 s, padding 0 | statusLine refreshInterval | claude-dgx:176 | UNKNOWN — owner to confirm |
| T-099 | 120 s | `STALE_SEC` (unused) | coordinator:11 | UNKNOWN — owner to confirm (dead) |
| T-100 | 4 s | preflight connect timeout | dgx_preflight.py:23 | UNKNOWN — owner to confirm |
| T-101 | 30 s × 3 | ssh ServerAlive | ledger-tunnel.plist:9-10 | UNKNOWN — owner to confirm |

### Backfill (`tools/backfill_cost_history.py`)
| # | Value | Meaning | file:line | Rationale |
|---|---|---|---|---|
| T-102 | price table opus/sonnet/haiku | list $/MTok | :28-32 | D: claude-api reference cached 2026-11-03 |
| T-103 | $1 / 30 min | min usd / min backfilled API time | :34-35 | D: docstring :12-14 |
| T-104 | 30 days | `--days` | :86 | D: matches COST_WINDOW_S |
| T-105 | `4*max(o,1)/15` | stale span | :78 | D: same rule as T-057/T-058 (variant: `max(o,1)`, `<=`) |

**Totals: 105 thresholds; 52 rows carry "UNKNOWN — owner to confirm"** (fully or for the numeric value;
counted from the tables above: status line 23 of 64, proxy 9 of 12, exporter 4 of 5, hook/launcher/preflight/plist
16 of 20, backfill 0 of 4). Several "D" items rely on documents outside
this repo (THRESHOLDS §8b, ECONOMICS-BRIEF) — the Go port's comments should cite them by name, not link them.

## 3. Missing NFRs (expected, not found)
Ledger rotation/size cap; exporter auth or loopback bind; proxy health endpoint; upstream retries/circuit
breaker; timezone in ledger timestamps; config validation (malformed env crashes at import); any automated tests.

## State Checkpoint
```yaml
pass: 4
status: complete
files_scanned: 11
timestamp: 2026-11-14T05:09:24Z
next_pass: 5
```
