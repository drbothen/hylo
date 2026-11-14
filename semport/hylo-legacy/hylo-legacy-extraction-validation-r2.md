# Extraction Validation R2 (step B.6): hylo-legacy — canonical consolidations

- **Validator:** fresh-context checker, no prior round assumptions; nothing in the artifacts taken as true until confirmed in source.
- **Source:** `$HOME/Dev/hylo/legacy/` — READ-ONLY. Nothing from `legacy/` was run or imported; no proxy; nothing networked;
  `CLAUDE.local.md` not read; no git commit. Recounts by `find`, `wc -l`, `stat`, `grep -c/-o`, `sort -u`, `git log/rev-list/ls-files`, and
  `python3 -I` AST scripts in `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/b6/`
  (`stmt_count.py`, `numlit.py`). mitmproxy 12.3.1 anchors spot-checked read-only in the production venv's `site-packages/mitmproxy/`.
- **Validated:** pass-0 r3 §2; pass-1 r3 §B (both Mermaid diagrams); pass-2 r8 §7 amended by r9 (base rows read in r4 §3.1-3.3 with r5/r6 amendments);
  pass-3 r4 §7 amended by r5-r8; pass-4 r7; pass-5 r3 amended by r4/r5; `hylo-legacy-coverage-audit.md`.
- **Earlier broad-sweep validation** (`hylo-legacy-extraction-validation.md`) untouched, per brief.

## Phase 1 — Behavioral verification

### 1.1 Behavioral contracts (sample 78 of 232 = 33.6%; minimum 58)

Stratified across every component, weighted toward P1 byte-exact statusline BCs and the approved deviations. Every sample read at its cited site.

| Component (BCs sampled) | Sample | Result |
|---|---|---|
| Status line (34) | 001, 002, 003, 004, 005, 006, 007, 008, 010, 011, 012, 014, 015, 016, 017, 018, 023, 027, 028, 031, 034, 036, 040, 043, 051, 052, 061, 068, 080, 084, 087, 098, 099, 103 | 34 CONFIRMED |
| Proxy (13) | 001, 002, 005, 006, 010, 013, 021, 024, 027, 037, 046, 047, 048 | 13 CONFIRMED |
| Exporter (8) | 001, 002, 003, 006, 008, 013, 026, 027 | 8 CONFIRMED |
| Stop hook (9) | 001, 002, 004, 007, 010, 011, 013, 018, 022 | 9 CONFIRMED |
| Launcher (6) | 001, 003, 004, 007, 010, 011 | 6 CONFIRMED |
| Preflight (2) | 001, 002 | 2 CONFIRMED |
| Coordinator (1) | 001 (lsof/grep-mitmdump mechanism, `CO:15,18-24`) | 1 CONFIRMED |
| Backfill (3) | 003, 008, 011 | 3 CONFIRMED |
| Services (2) | 001, 002 (plist argv literal `~`; `ssh -N -R` + keepalive options) | 2 CONFIRMED |
| **Total** | **78 unique, 0 inaccurate, 0 hallucinated** | **78 CONFIRMED** |

Notes on load-bearing samples: BC-SL-003 (`rows >= 2` + width rule, `SL:1217,1224,1234`), BC-SL-005 (Python `int()` grammar incl.
negative-disables-trim, `SL:1185-1190`), BC-SL-015 (expired-window hide, `SL:506`), BC-SL-043 (degradation ladder, `SL:693-702`),
BC-SL-052 (raw sid in cache name, `SL:1214-1215`; sanitized mix sid `SL:1017`), BC-SL-061 (`>= 10` / `> 8` TTFT boundaries, `SL:794-799`),
BC-SL-068/098/099 (persisted `cur` in mix cache `SL:1150-1153`; legacy predicate confirmed, Go contracts marked D4-EX-2 in the artifacts),
BC-PX-048 (`note()` catches only `OSError` at `dgx_proxy.py:73`, so an unencodable write raises — mechanism confirmed), BC-EX-027
(`_current_size`/`processed_size` at `dgx_ledger_exporter.py:64-68,280-287` — exactly the uncovered behavior r5 claims), BC-HK-010/022
(median-of-3 with early stop `HK:124-138`), BC-SV-002 (`ServerAliveInterval=30`, `CountMax=3`, `ExitOnForwardFailure=yes`, tunnel plist `:9-11`).

Approved-deviation rows verified: D4-EX-1 (BC-SL-023/080, `ps -o ppid=,comm=,lstart=`, `timeout=1`, 6 ancestors, `SL:278-295`), D4-EX-2
(BC-SL-068/098/099), D13 (BC-PX-035, path-agnostic `/v1/messages*` prefix, `dgx_proxy.py:103,215,254,316`), D14 (BC-LN-004,
`HTTPS_PROXY`/`NODE_EXTRA_CA_CERTS` exported to the launcher env `claude-dgx:79-80`).

### 1.2 Ledger schema (pass-2 r4 §3.2 amended by r5-r9)

All 13 schema rows sampled (the brief's 15 exceeds the 13 rows that exist; coverage is complete), plus the writer contract.

| Row | Field/behavior claim | Result |
|---|---|---|
| Writer | `open(a)`, one `write()`, `OSError` swallowed, naive local `t` at write time (`PX:56-62`) | CONFIRMED |
| 1 `dgx_request` | `_attrib` field order, `model_served`, `path` query-stripped (`:117-127,144,154`) | CONFIRMED |
| 2 `dgx_reply` | `status, duration_s` 3 dp + `_dgx` fields, `in_tok` = whole prompt iff tap (`:267-274`) | CONFIRMED |
| 3 `dgx_usage` | `account` 8-char hint, `cache_read_tok` iff present (`:276-282,326-336`) | CONFIRMED |
| 4 `dgx_upstream_error` | `error[:300]`, attribution minus `error` key (`:322-323`) | CONFIRMED |
| 5 `anth_request` | lane values `anthropic` / `anthropic-server-tools` (`:133,138`) | CONFIRMED |
| 6 `anth_reply` | consumer counts `status == 200` only; alias `anthropic_reply` (`EX:206`) | CONFIRMED |
| 7 `anth_usage` | no `duration_s` in writer; exporter derives 5m = write − min(1h, write) (`PX:247-253`; `EX:175-178`) | CONFIRMED |
| 8 `anthropic_upstream_error` | not read by the exporter (absent from `rebuild()`) | CONFIRMED |
| 9 `anth_ratelimit` | changed-per-session guard, api.anthropic.com only (`:176-188`) | CONFIRMED |
| 10 `bridge_ws_connect` | upgrade-gated, `host` field (`:100-101`) | CONFIRMED |
| 11 `bridge_ws_close` | `_bridge_dur` never set → `duration_s` always 0.0 (`:213`) | CONFIRMED |
| 12 `ws_closed` | guard on an attribute never set → never emitted (`:528-536`) | CONFIRMED (dead, as claimed) |
| 13 `anthropic_reply` | historical alias, still read (`EX:206` comment) | CONFIRMED |

Consumer fields (`req_totals` incl. device from `meta_user_id`, `est_prompt` bytes/4 iff positive, session funnel, `last_*` timestamps) all
match `dgx_ledger_exporter.py:129-210,238-266`.

### 1.3 Entities (10 sampled)

Ledger event, Session cache (`rl, rl_ts, fetch_ts, up, ts, sample, hist, proc_start`), Mix cache (`mixv6` marker, offset, `ids[-256:]`),
Git cache (`sha1[:16]`, TTL 5), Cost history (`sessions{}, lane/usd/api_ms/ts/src`, "cc" never overwritten), Decision log + failed-req dir
(`old[:-19]` keep-20, 50 MB cap), Trust state (atomic `mkstemp`+`os.replace`, `.trust-state.` prefix, `BACKUPS_TO_KEEP=3`), Preflight probe
(4 s, port-or-80, four error classes), Exporter metric family state (19 defaultdicts + dicts + scalars as amended by P2r5 C-5),
Stop-hook stdin record (`last_assistant_message`, `stop_hook_active`, `transcript_path`, `session_id`). **10/10 CONFIRMED.**

### 1.4 Threshold rows (15+ of 147; value and file:line)

T-001 (`4 s`, SL:74,324), T-003 (15.0, SL:79,697), T-005 (1.5 s, SL:81,170), T-008 (2.0 `>=`, SL:84,337), T-011 (300 `>`, SL:93,825),
T-023 (300,000/1,800,000 ms, SL:253), T-028 (50/85, SL:434), T-033/034 (projected vs absolute bands, SL:519,521), T-038/039 (`> 60000` vs
`>= 60000`, SL:540,551 — the operator distinction is real), T-047 (`q > 0` or preempt `> 0`, SL:740), T-053 (1520/1280 W, SL:812),
T-056 (20,000, SL:972), T-090/091/092 (HK:236,179,190), T-097 (1,800,000 ms, L:104), T-100 (4 s, PF:23), T-105 (`0 < span <= 4·max(o,1)/15`,
BF:78), T-066 (keep 19+1=20, PX:291-292). **All CONFIRMED, operators included.**

### 1.5 Env-var rows (10 of 43 + 21 implicit)

ENV-01 (multi-component defaults PX:86/SL:444,902/BF:89/LN:38), ENV-02 (PX:84), ENV-03 (`scheme or "http"`, `port or 80`, PX:79-83),
ENV-09 (`rstrip("/")`, SL:73), ENV-10 (Python `float()`, SL:74), ENV-17 (`-n` drops the oldest of the newest-first list, EX:24,238),
ENV-18 (bind-time `OverflowError` after the print, EX:25,413-414), ENV-22 (per-socket-operation, HK:34,113), ENV-32 (skip iff `== 1`, LN:60),
ENV-43 (`ARGS` never initialized, first hit LN:129). Implicit: TZ (I1), LANG/LOCTYPE (I2..I5), PATH (I10), `*_proxy` (I12..I14), OS-proxy
fallback (I15), ZDOTDIR/.zshenv (I18), user site-packages (I20, r3), mitmproxy confdir (I21, r4). **All CONFIRMED.**

### 1.6 Determinism rows (10 of 54) and pitfalls (10 of 22)

DET-01..06 sites (SL:231,243,304,322,408,499 — all six exact), DET-08 (two `time.time()` reads, SL:825-826), DET-13 (HK:111,118,133,197),
DET-19/20/22 (naive parses, SL:983 / SL:286 / BF:39), DET-25 (VM GET `ProxyHandler({})`, SL:165-171), DET-31 (ps walk, SL:278-295),
DET-49 (COLUMNS, SL:1186), DET-53 (`HTTPServer` → `getfqdn`, EX:414). Pitfalls: PR-01 (half-even + half-up sites), PR-03 (`//`/`%` sites),
PR-04 (NaN min/max argument order), PR-05 (`int()`), PR-11 (code-point slices `[:300]`/`[:8]`), PR-13 (Unicode `\b`, lookbehind, CJK class),
PR-14 (naive-local writers/readers lists), PR-15 (FMA sites incl. the correct "not a hazard" classification of BF:95 — integer product, exact),
PR-18 (port grammar PX:82/PF:20), PR-20 (posixpath sites). **All CONFIRMED.**

### 1.7 Interface rows (10 of 26, pass-1 r3 §B.4)

I-1 (argv/env phases incl. `API_TIMEOUT_MS=1800000`, `CLAUDE_CODE_AUTO_MODE_SERVER=0`, `--settings` conditionality, `ARGS` leak), I-2
(**19 leaf paths / 8 objects** — independently enumerated and matched exactly; `ProxyHandler({})` bypass), I-9 (13 event names), I-12
(VictoriaMetrics **query verbatim verified against `dgx_statusline.py:102-123`; 18 metric names / 19 result keys** both recount exactly),
I-13 (Kev, ≤ 3 calls, `answers.turn_complete.noul`), I-14 (preflight, port default 80), I-16 (**28 names, 25 TYPE, 22 HELP, 27 with samples**
— recount exact), I-17 (tunnel plist options), I-22 (`ps` walk + direct `.git` reads), I-25 (43 explicit + 17→21 implicit + `profile.env`).
**All CONFIRMED.**

### 1.8 Legacy Mermaid diagram (pass-1 r3 §B.6) — every edge checked

All 32 edges/arrows verified against source: launcher→mitmdump spawn `:75` + trap `:97`; caller-env+P0 `:38-53`; preflight on venv with no
proxy env yet (`:61-63` before `:79`); P3-P5 env + argv (`:79-109,128-181`); children-inherit (`HTTPS_PROXY`/`NODE_EXTRA_CA_CERTS`);
statusLine refresh 4 s gated `DGX_STATUSLINE` (`:175-177`); Stop gated `DGX_ENGLISH or DGX_AUTOCONTINUE` (`:160-161`); UserPromptSubmit gated
`DGX_ENGLISH` (`:157-158`); addon load via `-s` (`:75`); 1 s reload (mitmproxy-side); caches; ledger/decision-log/flow-log writers
(`:56-74`, `L:74-75`); hook log (`HK:193-201`); exporter reads ledger + hook log (`EX:22-23,115,215`); launchd agents (plists `RunAtLoad`
+`KeepAlive`); tunnel `ssh -R` (`pl-tu:8`); CONNECT h1 (children h1/h2); LAN admission (private/loopback) + `0.0.0.0` exporter; eager upstream
connect; pass-through classes (SSE tapped / non-SSE buffered / 84 other hosts); lazy Bearer to backend; preflight TCP 4 s; Kev POST direct;
VM `GET /api/v1/query` with `ProxyHandler({})`; VM scrapes the tunnel; VM ⇒ status line idle+pick series (`SL:824,107-108,1220-1223`).
Thick-arrow telemetry chain LG/HL ⇒ EX ⇒ T ⇒ VM ⇒ SL1 matches pass-1 §B.2 step 5. **All edges CONFIRMED.** (The hylo-target diagram §B.7 is
design intent; its legacy-facing claims — P1 statusline, D7 ledger bytes, legacy-format caches, OD-36 backfill — are consistent with the
validated artifacts.)

## Phase 2 — Metric verification

| Claim | Claimed | Recounted | Delta | Command / method |
|---|---|---|---|---|
| Files / lines / bytes | 11 / 3,181 / 164,151 | 11 / 3,181 / 164,151 | 0 | `find \| wc -l`; `wc -l`; `stat -f %z` sum |
| Per-file lines 1245/764/414/275/185/121/55/50/41/18/13 | same | same | 0 | `wc -l` |
| Python 2,860 (6); zsh 235 (2); plist 31 (2); MD 55 | same | same | 0 | `wc -l` groups |
| Python AST statements 1,809 (742/500/316/146/86/19) | 1,809 | 1,809 exact | 0 | `python3 -I` `ast.walk` `ast.stmt` count |
| Numeric literals 522 (SL 303, PX 70, EX 83, HK 18, PF 5, BF 43) | 522 | 522, per-file exact | 0 | `python3 -I` `Constant` int/float/complex census |
| Commits touching legacy / on main / tracked | 19 / 26 / 11 | 19 / 26 / 11 | 0 | `git log -- legacy`; `rev-list --count main`; `ls-files` |
| Executable bits (4 files) | 4 named | 4, same names | 0 | `ls -la` |
| Tests in tree | 0 | 0 | 0 | `find -name '*test*'` + file list |
| Exporter metric names 28 declared / 25 TYPE / 22 HELP / 27 with samples | 28/25/22/27 | 28 (25+3 undeclared session names) / 25 / 22 / 27 | 0 | `grep -c '# HELP'`, `'# TYPE'`; sample f-string census |
| Ledger event names 13 (12 emitted + 1 historical); 11 call sites | 13/12+1/11 | 13 names (12 with writer code incl. dead-guard `ws_closed`, 1 historical alias); 11 `ledger("` sites | 0 | `grep -n 'ledger("'` + f-string expansion at `:322` |
| BCs: r4 index 227; union r4-r8 232 | 227 / 232 | 227 / 232 | 0 | `grep -oE 'BC-[A-Z]{2}-[0-9]{3}' \| sort -u` |
| BC per component SL 103, PX 49, EX 27, HK 23, LN 11, PF 2, CO 2, BF 13, SV 2 | same | same (sum 232) | 0 | per-prefix `sort -u` |
| r4 §7.2: BX 137 (SL 97, PX 37, HK 3); phases P1 103/P2 28/P3 44/P4 39/unsched 13; last-round B 82/r1 87/r2 25/r3 20/r4 13 | same | same | 0 | awk over the index table |
| Thresholds 147 = 79+31+37; unique contiguous T-001..T-147 | 147 | 147, unique, contiguous | 0 | awk row counts + `sort -nu` |
| Threshold classes CFG 96 / NC 37 / DROP 7 / OOS 2 / EXT 2 / NEW-H 2 / N-A 1 | same | same (NC-solo 37 = 42−5 CFG+NC; DROP-solo 7 = 8−1 shared T-075) | 0 | awk class column |
| Threshold rationale OWNER 27 / Dv† 18 / N-A 8 / EXT 2 | same | same | 0 | awk rationale column |
| Threshold last-changed B 45 / R1 56 / R2 16 / R3 14 / R4 3 / R5 8 / R6 5 / R7 0 | same | same | 0 | §B.2.5 lists vs Last column spot-checks |
| OD-94 sensitivity (a) NC 28/N-A 10; (b) CFG 97/NC 36 | same | same (9 = 1+8 rows; ±1 shifts) | 0 | arithmetic recheck |
| Explicit env inputs 43 (27 Python + 22 launcher − 6 overlap) | 43 | 27 exact; launcher 21 explicit (`${...}` 19 + `$HOME` + `$PWD`) + implicit `ARGS`; overlap exactly 6 | 0 | `grep -ohE 'os.environ.get...'`; launcher expansion census |
| Implicit inputs 21 (I-21 added r4) | 20 (r3) → 21 (r4) | 21 IDs I1..I21 | 0 | table walk |
| Determinism rows 54; conventions 19; pitfalls 22 | 54 / 19 / 22 | 54 (contiguous DET-01..54); 19 (CV-01..19); 22 (PR-01..22, 19+3 tags) | 0 | table walks |
| pass-5 B.1 totals: 33 keyed / 10 unkeyed / 3 no-env keys / 9 import-crash / 2 per-call | same | same (dash recount = 10: ENV-15,23,28,29,31,33,39,41,42,43) | 0 | row-by-row |
| mitmproxy version anchor `version:5` = 12.3.1 | 12.3.1 | exact, `version.py:5` | 0 | grep in venv reference |
| mitmproxy option anchors (listen_host `options:94-99`, ignore/allow `:81-93`, http2 `:131-135`, ping 58 `:137-146`, tcp_timeout) | as cited | byte-exact | 0 | `sed -n` of `options.py` |
| Coverage audit BC-id per-prefix table (103/49/27/23/13/11/2/2/2) | same | same | 0 | `sort -u` recount |
| **Spawn census "10 Python sites"** | 10 | **9** (`subprocess.run` occurrences; r2's own itemization lists 9) | **−1** | `grep -c 'subprocess.run'` |
| Production counts (ledger tallies 4755/4696/…, 57 inactivity closes, 75 child handshakes, 7,566 child h2 flows, 112 TLS failures, 36 unpaired, Remote-Control 8/240/11,224, 9,650 calls/120 transcripts, 456/193 medians, 7,228 DST goldens, 1,516-row grid/339, 713/4,132, 44 files at audit time, matrix 141 rows) | — | not recomputable (production evidence) | n/a | retained logs/ledgers, outside `legacy/` |

## Refinement iterations

- **Iteration 1:** full sampling + recount as above. One factual error found (spawn census 10 → 9).
- **Iteration 2:** fix applied and re-verified; propagated nowhere else (grep: single occurrence in latest-round files). Distributions
  (§7.2, §B.2.4, §B.2.5, B.1 totals) re-derived under the artifacts' own counting conventions — all consistent.
- **Iteration 3:** cross-reference sweep: every BC id cited in pass-1 r3 §B.5 resolves in the canonical 232; amendment chains (r5→r8 additions
  BC-EX-027, BC-PX-046..049; pass-2 r9 §6 delta rows; pass-5 r4/r5 implicit-input additions) close; no orphaned references; the pass-0 C7
  (T-121) and pass-1 C1-C3/C6 disputes are recorded as closed by the later rounds that absorbed them.

## Fixes applied (latest round file of the affected pass, minimal edits)

| File | Fix |
|---|---|
| `hylo-legacy-pass-0-deep-inventory-r3.md` §2.5 | "Spawn census: 10 Python sites" → **9**, with a "validated 2026-11-14 (B.6)" note recording the grep evidence and that pass-0 r2 §2.2's prose "Python: 10 sites" conflicts with its own 9-item list (r2 left untouched as a historical round; downstream reads r3 §2) |

## Hallucinated items

None found. Every sampled function, event, metric, threshold and file:line anchor exists in `legacy/` (mitmproxy-internal `m/` anchors
spot-verified against the venv reference).

## Unverifiable items

Production-log-derived counts (listed above) and runtime-only behaviors (Claude Code stdin contract details, launchd behavior, VM server
responses) — marked as such in the artifacts themselves, correctly.

## Confidence assessment

- Behavioral accuracy of the sample: 100% (78/78 BCs, 13/13 schema rows, 10/10 entities, 35+ thresholds, 10+10+10 env/det/pitfall rows,
  10/10 interfaces, 32/32 diagram edges).
- Metric accuracy after one fix: 26 of 27 recount groups exact; 1 corrected (delta −1 on a non-headline census).
- Overall extraction accuracy: ~99%.
- **Recommendation: TRUST** (the single fix is incorporated; no re-analysis needed).

Result: PASS-WITH-FIXES
