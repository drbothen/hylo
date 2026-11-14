# Pass 3 deepening, round 4: behavioral contracts (hylo-legacy)

- **Scope:** `legacy/` (unchanged: 11 files, 3,181 lines). Re-read this round: `dgx_proxy.py:96-118,174-190,209-248,311-323,336-428`,
  `dgx_statusline.py:217-262,986-1040,1064-1112,1150-1154`, `dgx_ledger_exporter.py:135-148,236-240,355-404`. No mitmproxy module was needed.
- **Inputs read:** every file in `.factory/semport/hylo-legacy/`: pass-3 broad, r1, r2, r3; pass-2 broad, r1-r4; and **pass-2 r5**
  (`…-pass-2-deep-domain-r5.md`, which appeared at 00:58 local while this round ran). It was read and not edited, and its numbering is followed
  (OD-01..OD-34, CONV-ABS-13/14). Also `docs/PLAN.md` §2, §6, §7, §10.
- **Method:** static reading plus pinning scripts in
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r4/`, run with the oracle
  `/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7). `loader.py` (new, independent of round 3's) execs a **copy** of a legacy file's text in a
  fresh namespace with `HOME`, the ledger, the hook log and the decision log redirected to the scratchpad. `tap_prop.py` execs a text copy of
  `dgx_proxy.py:339-427` only (`cache_fields` + `_SSETap`) and asserts that the line numbers have not drifted. Scripts: `f_sl.py`, `f_ex.py`, `od32.py`,
  `tap_prop.py` (output `tap_prop_out.txt`), `index.py` (generates the §7 table and its totals). Nothing legacy ran in place. Nothing networked or
  proxy-related ran. `CLAUDE.local.md` was not read.
- **Notation:** `\e` is ESC (0x1B). Code points are written `U+XXXX`. "Pinned" means a copied expression produced the output shown. A bare `:N` means the
  file named in the section heading. Abbreviations: **P2rN**/**P3rN** = pass-2/pass-3 round N; **B** = broad sweep.
- **IDs (append-only):** new BC-SL-103, BC-PX-045, BC-EX-026 (the last carries pass-2 r5's F-1 into the BC catalogue). Retraction **CONV-ABS-15**. The
  highest number in use before this round was 14 (P2r5), and 9-11 were never used (left unused here, so that no number is reused). New owner items **OD-35, OD-36**, continuing P2r5's final list.

---

## 0. Evidence recorded and rulings applied

| Item | Evidence (orchestrator, local, read-only, 2026-11-14) | Effect on pass-3 contracts |
|---|---|---|
| r3 gap 1 `~/.mitmproxy/config.yaml` | **absent**; the directory holds only the CA files (`mitmproxy-ca.pem`, `-ca-cert.pem/.cer/.p12`, `-ca.p12`, dhparam) | mitmproxy 12.3.1 runs on its **defaults**. **P-S4 CONFIRMED** (the `store_streamed_bodies` exception cannot apply). **BC-PX-037 table CONFIRMED** as written (no `stream_large_bodies`, `body_size_limit`, `connection_strategy` or `validate_inbound_headers` override). No `proxyauth` or `listen_host` override either (consistent with P2r5 §1.1) |
| r3 gap 3 `anthropic_upstream_error` count | **21 as of 2026-11-14**; the 21st event was written at 00:23:42 local time, after the first count | 20 (P2r3) and 21 (P3r3, P2r4) were both right at their times. Counts are now quoted "as of": **`anthropic_upstream_error` = 21 and `dgx_upstream_error` = 23, as of 2026-11-14 ~00:24 local** (orchestrator snapshot). The ledger is live and append-only |
| mitmdump logs | 38 retained logs: **0** ` HTTP/2.0` lines, **0** `error in script` lines | BC-PX-044 consequence 2 (Claude Code talks HTTP/1.1 to the proxy) is **observed**, not just inferred (also P2r5 §0.1). The error-cause table applies in its HTTP/1 form only |
| OD-24 live | 9 legacy proxies on `*:8090-8098`, exporter on `*:9210`, macOS firewall disabled | Recorded. OD-24/OD-27 legacy side were ruled by the owner (P2r5 §0.2) and are not pending |

Owner rulings applied (not pending): strict stdio and the 3.11.7 oracle; degraded output byte for byte for catalogued crash paths; CP-C01..C10 out of
parity scope (the Go writer writes legacy's exact cache format); D4-EX-1; D4-EX-2; D13-D16; OD-24/OD-27 legacy side.

---

## 1. Target F: protocol re-check of round 3's riskiest claims

All re-checks used new transcripts, seeds and ledgers, not round 3's fixtures (`f_sl.py`, `f_ex.py`).

### 1.1 Verdicts

| Claim (round 3) | Verdict | Evidence |
|---|---|---|
| **BC-SL-100** legacy persists a poisoned `cur.out`; the next closer crashes at `:994`; sticky | **CONFIRMED** for `"abc"`, `["x"]` and `{"a": 1}`. Refresh 1 writes `"cur": {"id": "m1", "t0": 1794654000.0, "t1": 1794654009.0, "out": "abc"}`. A continuation line of the same id updates `t1` (1794654010.0) **without** crashing. The first closer (a timed system line) raises `TypeError at :994` and leaves the cache byte-identical. The next refresh raises again. **Refinement:** the trigger is "**no closer** follows the opening line in the same parse window", not "the opening line is the last line". Continuation lines of the same id may follow it, because they only move `t1` (`:1074-1075`). **Correction:** see §1.2 (CONV-ABS-15) for the reader-rule rationale | `dgx_statusline.py:988-996,1073-1079,1150-1153` |
| **BC-SL-101** two colour/value mismatches | **CONFIRMED** with an independent seed (10 `cc` sessions, rates `[5, 8, 11, 14, 17, 19, 20, 23, 26, 40]` at 1 h each, thresholds pinned `((20.0, 26.0), (20.0, 26.0))`). usd 19.99 at 1 h → `\e[97m$19.99\e[0m\e[90m $20.0/h\e[0m` (rate 19.99 < p75 20, so grey, while `.1f` shows 20.0). usd 25.99 → `\e[33m$25.99\e[0m\e[33m $26.0/h\e[0m` (25.99 < p95 26, so yellow, displayed 26.0). Also 25.96 → yellow `$26.0/h`. 20.0 → yellow, 26.0 → red (`>=`) | `:257-262,601-625` |
| **BC-EX-025** non-contiguous session families; duplicate series | **CONFIRMED**, with one refinement. Ledger with three sessions sharing the 8-character prefix `abcdef12`: the session block yields **12 family runs** (contiguous would be 4), because `:380-387` emits `requests, tokens_in, tokens_out, errors` per session. Two sessions with the same prefix, project and user give **duplicate series**. **Refinement:** the duplicates carry **different values** (`tokens_in` 11 and 10 for the same label set), so a scrape holds conflicting samples, not identical repeats. A third session with the same prefix but another project is a distinct series. Which sample VictoriaMetrics keeps is not verified (LOW). The birthday bound of about 3·10⁻⁷ for 50 random UUIDs (32-bit prefix) is an upper bound, since project and user must also match | `dgx_ledger_exporter.py:380-387` |
| **BC-SL-102** duplicate `"123"` keys | **CONFIRMED** with sid 777. Refresh 1: one `"777"`. Refresh 2: **two** `"777"` keys (the loaded string key plus the new int key; `s.get(777)` misses the string key, so the throttle never applies). Refresh 3: still two (`json.load` keeps the last, usd 5.0, then the int key is added again). Tail pinned: `…"usd": 4.0, …, "ts": 1794615010.0, "src": "cc"}, "777": {"lane": "anth", "usd": 5.0, "api_ms": 3600000, "ts": 1794615011.0, "src": "cc"}}}`. Self-exclusion failing (`"777" == 777` is false, `:246`) is source-certain. This seed's percentiles happen not to move, so round 3's pinned `(17.0, 19.0)` vs `(16.0, 18.0)` stands as the numeric example | `:224-237,245-246` |

### 1.2 Retraction CONV-ABS-15 and the new BC-SL-103

**CONV-ABS-15** (P3r3 §3.2, BC-SL-100, last bullet: "treat such a `cur` as absent (`cur = null`, `lr` unchanged), **which is what Go would hold had it
parsed the same lines under D4-EX-2**"; adopted by P2r5 as OD-32 "treat a non-numeric `cur.out` as no open turn"). Pinned with `od32.py`, which
compares three states after the same later lines. **R** is the OD-32 rule applied to the legacy-written cache. **K** is the cache kept verbatim. **N** is
native D4-EX-2 Go, i.e. legacy on the transcript with the W-line deleted (`size` excluded):

| Case | Native Go right after the poisoned window | R vs N after the later lines | Verdict on the claim |
|---|---|---|---|
| `lu` set; then a closer | `cur = {"id": "B", …, "out": 7}`: the **previous turn stays open** (BC-SL-099 row T05~) | `lr`, `lu`, `cur`, `tout`, `ids` equal. **`conv` differs** (+1: legacy counted W's composition before persisting, and the reader cannot undo it) | **Inexact.** Go would not hold `cur = null`. The rule converges on turn state at the next turn event, with a residual in composition |
| `lu` set; continuation of A (out 900), then closer | as above | `lr = [90.0, False]` on both; `conv` differs | same |
| `lu` set; a new id C, no closer | as above | `cur` = C's turn on both; `conv` differs | same |
| **`lu` None**; continuation of A (out 900), no closer | the W-predicate for CP-T05 requires `lu is not None` (BC-SL-098), so **native Go does not skip W**: native Go = **K** = legacy, `cur = {"id": "A", "t0": null, "t1": …10, "out": "abc"}` | **R gives `"out": 900`**, while native Go and legacy keep `"out": "abc"` | **False.** Applying the rule here makes Go's mix cache diverge from legacy's on a state that both write. This breaks the exact-cache-format obligation (ruling b) |
| `lu` None; continuation, then closer | K = legacy: no crash (`_finish_turn` returns at `t0 is None`, `:991`), `cur` null | equal | harmless either way |

**BC-SL-103 (new):** a `cur` whose `t0` is null and whose `out` is a non-numeric JSON value (string, array, object) is a **normal, crash-free state** that
**both legacy and D4-EX-2 Go write** (pinned: `{'id': 'm1', 't0': None, 't1': 1794654009.0, 'out': 'abc'}`). `_finish_turn` tests `t0` first
(`:991`), so the value of `out` is never compared. Contracts for Go (P1):

1. The Go mix-cache type stores **`cur.out` as a raw JSON value** (any type), not a number. Go's own D4-EX-2 parser produces the string form, and
   ruling (b) requires Go to write it back verbatim.
2. Go's `finishTurn` checks `cur == nil || t0 == null` **before** it reads `out`, in legacy's order.
3. **OD-32 amended:** treat `cur` as absent only when **`cur.t0` is a number and `cur.out` is not int/float/bool** (the legacy-written CP-T05 form,
   reachable only from a legacy-written cache). Keep every other `cur` verbatim. Known residual: W's composition (`res/conv/think`) stays counted.
   Turn state matches native Go from the next turn event on.

BC-SL-100 keeps its behavioral content (confirmed above). Only its reader-rule rationale is retracted and replaced by item 3.

---

## 2. Target A: P3 harness design input for the SSE tap (closes r3 gap 4)

### 2.1 Decision: prove boundary insensitivity (option 2). Do not capture real boundaries (option 1)

| Option | Feasible? | Safe now? | Useful for a Go port? | Verdict |
|---|---|---|---|---|
| 1. Capture real `feed` boundaries (HTTP chunk + TCP read) into the replay corpus | Only with an instrumented addon in the live proxies. Editing `dgx_proxy.py` live-reloads every running proxy (P2r4 §2.1), and the boundaries come from `reader.read(65535)` (mitmproxy 12.3.1 `proxy/server:285`) plus chunked framing | **No.** The soak forbids touching the live proxies, and a failed reload drops a proxy into plain pass-through (OD-26) | **No.** Go's `net/http` reader produces different boundaries, so recorded boundaries test only legacy against itself | **Rejected** |
| 2. Show that the corpus is boundary-insensitive and property-test it | Yes: one theorem from the tap's source, one mechanical per-stream check, one property test | Yes: offline, on recorded bytes | Yes: it defines a chunking-free oracle that a Go tap can match | **Adopted** (BC-PX-045) |

### 2.2 BC-PX-045 (new): boundary insensitivity of the tap, and the per-line replay oracle

**Structural facts** (`dgx_proxy.py:398-427`):

- (a) `feed` splits at the **last** `\n` of the buffer, so every block passed to `_scan` is a concatenation of complete lines joined by `\n`
  (`:401-403`).
- (b) `rb"data: ({.*})"` cannot cross `\n`, and the greedy `.*` runs to the last `}` of the line, so each line yields **at most one match**. A block's
  matches are therefore exactly its lines' matches, in order (`:413`).
- (c) Whether a line raises inside `_scan` depends **only on that line**. The raising operations are `int()` on usage or cache values, `.get` on a
  non-dict `delta` (including `null`), and a non-`ValueError` from `json.loads` such as `RecursionError`. None of them reads tap state. `max()`
  compares ints and cannot raise.
- (d) A raising line keeps the effects applied before the raise (for example `usage` set, then `delta: null` raises). The exception aborts the
  **rest of its block** (`:404-407`).
- (e) The 64,000-byte guard (`:408-409`) truncates only the unterminated tail. That tail is a prefix of the current line, so a line of **at most
  64,000 bytes, excluding its `\n`** (a `\r` counts), is never truncated.
- (f) An unterminated final line is never scanned, and the end-of-message `feed(b"")` scans nothing (P3r3 §2.1 assumption 3). Neither depends on
  chunking.

**Theorem.** If every complete line of a stream is at most 64,000 bytes and no complete line raises when scanned alone, then **every** chunking (empty
chunks, 1-byte chunks, splits inside UTF-8 sequences, with or without the end-of-message call) leaves the tap in the same final state
`(usage, cache, stop_reason)`. That state equals the **per-line oracle**: the legacy tap fed `line + b"\n"` once per complete line, then the tail,
then `b""`. Proof: by (a), (b) and (e) the matches seen are the same sequence under any chunking; by (c) no line raises, so nothing is skipped; by
(f) the tail contributes nothing.

**Property test** (pinned, `tap_prop.py 300`: 300 random chunkings per stream, plus 1-byte chunks and "each `\n` starts the next chunk"):

| Stream | Max line (B) | Outcomes different from the per-line oracle | Per-line oracle |
|---|---|---|---|
| Anthropic-shaped, 40 text deltas with multibyte text, pings, cache split | 279 | **0** | `((12, 321), {read 3000, write 949, 5m 0, 1h 949}, 'end_turn')` |
| same, no cache fields / CRLF line endings / unterminated final `data:` line / `message_delta` without `input_tokens` | ≤ 280 | **0** each | as expected; the out-only case gives `usage None` (BC-PX-033) |
| vLLM-shaped, two `message_delta`s with `input_tokens` | 145 | **0** | `((500, 77), {read 400, …}, 'max_tokens')` |
| a 63,999-byte text-delta line, then a usage event | 63,999 | **0** | `((1, 2), {}, 'end_turn')` |
| a **64,000-byte** usage line | 64,000 | **0** | `((7, 8), {}, None)` |
| a **64,001-byte** usage line | 64,001 | **2** (random chunking and the `\n` split both give `(None, {}, None)`) | `((7, 8), {}, None)` |
| `delta: null` event, then a good event | 110 | **1** (one-shot gives `((1, 2), {}, None)`) | `((3, 4), {}, 'end_turn')` |
| `input_tokens: "abc"`, then a good event | 114 | **1** (one-shot gives `(None, {}, None)`) | `((11, 12), {}, 'max_tokens')` |
| raising line that is the **last** line with any effect | 279 | **0** | as expected |

The 64,000/64,001 pair pins the exact bound. The last row shows that a raising line is harmless when no effect follows it.

**Harness contract (P3):**

1. **Oracle.** The replay runs the legacy tap with **per-line feeding** for every recorded SSE body. Go's tap must produce the same `usage`, cache
   fields and `stop_reason`, and therefore the same `*_reply`/`*_usage` ledger lines. This applies to every stream, including the raising class: the
   per-line result is one of legacy's reachable outcomes (a network that delivers one line per read), so matching it is parity, not a deviation.
2. **Classification.** For each recorded stream the harness also computes the one-shot result and the per-line "does this line raise" check (with the
   copied `_scan`). A stream is **boundary-insensitive** iff every complete line is ≤ 64,000 bytes and no complete line raises, or the only raising
   lines have no effect-carrying line after them. Insensitive streams are full parity fixtures. Sensitive streams are kept, labelled
   "chunk-sensitive", and compared against the per-line oracle only.
3. **Property test.** Every corpus stream is re-chunked at random boundaries (≥ 300 trials, plus 1-byte and newline-split chunkings). For insensitive
   streams every result must equal the per-line oracle. This guards the classifier and any Go refactor of the tap.
4. **Reference model for Go.** `tap_prop.py`'s `ref()` is an independent per-line model: at most one match per line; `ValueError` from `json.loads`
   skips the line; any other exception aborts only that line; effects apply in legacy's order (usage, top-level cache, `message.usage` cache,
   `delta.stop_reason`). It **equals the legacy per-line run on all 12 streams**, the raising ones included. It is the executable spec for the Go tap.
5. **Expected corpus class.** The shapes known from the code and from Anthropic's documented event set carry dict `delta`s and integer usage, and
   no line comes near 64,000 bytes. The recorded corpus is therefore expected to be fully insensitive. The classifier verifies this per stream; it is
   not assumed.

**Outside the class (OD-35, new):** the Go tap's behavior for lines longer than 64,000 bytes. Legacy's result for such a line depends on chunking
(row 64,001). Matching the per-line oracle would require Go to buffer unbounded lines. *Recommendation:* Go scans complete lines up to a configurable
cap (D15, default 64,000) and does not scan longer lines. This is an approved deviation on a class the classifier will report if it ever appears.
The raising class needs no owner decision (contract item 1).

Refined by this BC: **BC-PX-040** (the bound is exactly ≤ 64,000 bytes excluding `\n`; its P3 replay rule is superseded by the contract above) and
**BC-PX-016** (detail).

---

## 3. Target E: P3 replay verification items (recorded, not attempted)

| ID | Item | Source-level expectation | How the P3 replay settles it |
|---|---|---|---|
| **V-1** | Host header sent to the backend after the lane switch (BC-PX-043) | `Host: <host>[:<port>]`, port omitted iff it is the scheme default; default upstream `Host: 192.0.2.10:8080`; `DGX_UPSTREAM=http://h` gives `Host: h`. Request line in origin form (client used CONNECT + TLS over HTTP/1.1) | Run the legacy addon in mitmdump against a stub backend on loopback and record the raw request head. Compare with Go's |
| **V-2** | mitmproxy's 502 response bytes on a backend connect failure (BC-PX-044 row 1) and on `server closed connection` (row 3), including status line, headers (`Connection: close`, content type, length) and HTML body; the eager-CONNECT 502 naming `connection_strategy` (P2r4 D-1) | HTTP/1.1: the 502 is sent and the client connection closes (P2r4 §1.3, HTTP/1 row; production is HTTP/1.1) | Same stub, backend port closed. Record the client-side bytes. Whether Go reproduces them is OD-17 / OD-28 |
| **V-3** | Whether mitmproxy's shutdown fires `error` for in-flight flows (P2r5 §2.5 hypothesis for the 36 unpaired DGX requests) | unknown | Kill mitmdump mid-stream in the replay rig and check the ledger. It decides the replay's "orphaned by proxy exit" classification (OD-25) |

---

## 4. Pass-2 r5 hand-offs absorbed (refinements; the source re-read this round agrees)

| P2r5 item | Pass-3 BC refined | Refinement (source) |
|---|---|---|
| **CONV-ABS-14**: `anthropic_upstream_error` covers any non-DGX host | **BC-PX-024**, **BC-PX-044**, **BC-EX-024** | `error()` fires for **any** flow whose path starts with `/v1/messages`, whatever the host. `lane = "dgx" if host == dgx_host else "anthropic"` (`dgx_proxy.py:316-319`). Read "`anthropic_upstream_error`" as "non-DGX host". Attribution is empty when `_attrib` was never set: request hook not run, unparseable or non-object body, or a host other than `api.anthropic.com` (`:103-111`). BC-PX-044's table holds for routed flows; its scope is all `/v1/messages*` flows |
| C-1: `anth_reply` carries the cache dict | **BC-PX-019** | `ev.update(in_tok=…, out_tok=…, stop_reason=…, **cache)` on `anth_reply` (`:242-245`), so the cache fields (and the 2026-11-12 `cache_write_5m_tok` defect) are on `anth_reply` as well as `anth_usage` |
| C-3: `bridge_ws_close` on every bridge response | **BC-PX-026** | `response` writes `bridge_ws_close` for **every** response from `bridge.claudeusercontent.com` (`:211-214`). `bridge_ws_connect` only for upgrades (`:100-102`). The two do not pair |
| C-4: `anth_ratelimit` scope | **BC-PX-013** | Runs for every `api.anthropic.com` response, any path (`:177`). Flows without `_attrib` share the change-detection slot `_last_rl[None]` and log `session: null` (`:184-188`) |
| F-1: exporter idle-connection stall | **BC-EX-026 (new BC, P2r5's finding)** | Synchronous `HTTPServer`, no socket timeout. One client that connects and sends nothing blocks every later scrape until it closes, with no error logged. Parity: a failure mode, not exposition bytes. OD-33 (approved failure-mode deviation recommended) |
| C-6: near-key on both lanes | (no BC change) | P3 replay pairing input. Reader rule: never assume a reply has a request (OD-25) |

---

## 5. Target C: round 3's 10 pending items mapped onto the OD list

P2r5 already finalized OD-01..OD-34 and mapped all ten items. This round follows that numbering and adds two items.

| P3r3 item | Maps to | Relation | Note |
|---|---|---|---|
| #1 CP-T05 detection point | **OD-21** | duplicate | — |
| #2 interrupted generations counted as DGX errors | **OD-16** | duplicate | now production-observed (4 of 23 as of 2026-11-14) |
| #3 P-S4 | **OD-18** (P-S4 part) | duplicate | P-S4 confirmed for the production config (§0) |
| #4 exporter DST false idle | **OD-22** | duplicate | — |
| #5 exporter tally misattribution | **OD-23** | duplicate | — |
| #6 upstream-error text in the Go proxy | **OD-28** | added by P2r5 | scope widened by CONV-ABS-14 (non-DGX host) |
| #7 exporter writer: hand-written vs library | **OD-29** | added by P2r5 | BC-EX-025's conflicting duplicate samples strengthen "hand-written" |
| #8 numeric-sid duplicate keys | **OD-30** | added by P2r5 | re-confirmed (§1.1) |
| #9 backfill NaN and history shape | **OD-31** | added by P2r5 | — |
| #10 Go reader of a poisoned mix cache | **OD-32** | added by P2r5; **recommendation amended here** | add the condition "`cur.t0` is a number" (§1.2 item 3); without it the rule breaks parity on the `t0`-null state that Go itself writes |
| (new) SSE tap lines > 64,000 bytes | **OD-35** | new | *Recommend:* configurable cap (default 64,000); longer lines not scanned; approved deviation on a class the classifier reports (§2.2) |
| (new) `hylo cost backfill` has no phase in `docs/PLAN.md` §7 | **OD-36** | new | PLAN §4 maps the tool to `hylo cost backfill`, but no phase P1-P7 names it, and §6 names no package for it. P2r5 tags its items P6. *Recommend:* schedule it in P6 with the cost basis, under the package that owns `cost-history.json` (`internal/statusline`, or a shared `internal/cost`), and keep `legacy/tools/backfill_cost_history.py` runnable until then |

Final count: **36 items (OD-01..OD-36)**, 34 pending and 2 ruled (OD-24, OD-27 legacy side). OD-36 also explains why the index (§7) shows the
backfill rows as "unsched.".

---

## 6. Target D: CONV-ABS crosswalk across both passes (one retraction list for Phase 1)

Cite as `P2-CONV-ABS-N` / `P3-CONV-ABS-N` wherever the number alone is ambiguous (only 6 is).

| Phase-1 ID | Number(s) | Pass, round | Retracted claim → ground truth | Phase-1 consequence |
|---|---|---|---|---|
| RET-01 | CONV-ABS-1 | P2r1 | "9999 s default age" → 9999 is a default **timestamp** (age ≈ 1.79e9 s) | none on output (unreachable) |
| RET-02 | CONV-ABS-2 | P2r1 | composition "byte shares" → **characters** (code points; `json.dumps` characters; 2,000 per image) | P1 composition math |
| RET-03 | CONV-ABS-3 | P2r1 | harness `LC_ALL=C` → **unsafe**; strict UTF-8 locale (owner ruling) | P1 harness env |
| RET-04 | CONV-ABS-4 | P2r1 | `json.loads(bytes)` rejects invalid UTF-8 → accepts BOM, UTF-16/32 and CESU surrogates | P1 transcript decoder |
| RET-05 | CONV-ABS-5 | P2r2 | CP-25 as an independent trigger → not independent (the turn machine runs before the usage step) | crash-catalogue count |
| RET-06 | **P2-CONV-ABS-6** = **P3-CONV-ABS-7** (alias, one retraction) | P2r3 / P3r2 | trust `rotate` always crashes / touches `args.force` unconditionally → only while a mitmdump runs (`:703` short-circuit); `remove` crashes whenever a keychain entry exists | BC-PX-031 narrowed (OOS: replaced by `hylo ca`) |
| RET-07 | **P3-CONV-ABS-6** | P3r2 | CP-T02/T03/T04/T06/T07 unconditional on field shape → the W-predicates of BC-SL-098 | D4-EX-2 table tests (BC-SL-099) |
| RET-08 | CONV-ABS-8 | P3r3 | "legacy never crashes" when the CP-T05 turn stays open → legacy persists the poisoned `cur` and crashes on the first later closer | BC-SL-100 |
| — | CONV-ABS-9..11 | — | **never used** (reserved for P3r3, which used only 8) | — |
| RET-09 | CONV-ABS-12 | P2r4 | plain pass-through reachable at launch → mitmdump **exits 1** at startup (`ErrorCheck`); pass-through only after a reload | launcher/proxy failure model, OD-26 |
| RET-10 | CONV-ABS-13 | P2r5 | exporter "15 keyed accumulators" → 19 `defaultdict`s + 3 dict states + 5 scalars | P2 state model |
| RET-11 | CONV-ABS-14 | P2r5 | empty attribution identifies the client side → it does not; `anthropic_upstream_error` = any non-DGX host | BC-PX-024/044, BC-EX-024 wording |
| RET-12 | **CONV-ABS-15** | **P3r4** | OD-32's `cur = null` reader rule is "what Go would hold" → inexact for the `lu`-set form, and wrong for the `t0`-null form that Go itself writes | BC-SL-100/103, OD-32 amended |

Totals: numbers 1-15 issued; **12 in use** (1-8, 12-15; 9-11 never used); **13 meanings** (6 has one per pass); **12 distinct retractions**
(RET-01..RET-12): 9 from pass 2 (1-5, P2-6, 12-14) and 3 from pass 3 (P3-6, 8, 15). P3-7 is an alias of P2-6 and counts once.

---

## 7. Target B: canonical BC index for Phase 1

### 7.1 Legend

- **Go package:** per `docs/PLAN.md` §6. `cmd/hylo (run)` = the `hylo run` subcommand (it uses `internal/config` and `internal/platform`).
  `internal/platform (doctor)` = `hylo doctor`. `cmd/hylo (cost backfill)` = proposed; §6 names no package (OD-36).
- **Ph:** P1 status line, P2 exporter, P3 proxy, P4 run/hook/doctor/ca/ui (`docs/PLAN.md` §7); "unsched." = no phase assigned (OD-36).
- **Parity** (primary status for macOS/Linux parity):
  - **BX** = byte-exact (stdout, cache files, rewritten bodies, ledger lines; the replay normalizes only `t` and `duration_s`).
  - **JE** = JSON/value-equivalent: same parsed content, same metric names, labels and values, same hook decision and JSON (P2/P4 exit criteria).
  - **OOS** = out of parity scope.
  - **D4-EX-2 / D13 / D14** = owner-approved deviation.
  - **OD-NN** = parity treatment pending that owner decision.
- **Also:** secondary tags (Windows-only deviations, post-cutover items, sub-cases governed by another OD).
- **Conf:** H = pinned or source plus production; H-R = review-verified (the broad sweep's HIGH-R); M = read in code; L = inferred or external.
- **Last:** the round that last changed the BC (B = broad sweep). **Flags:** supersession or provenance notes.
- **OOS on decision-log text** (BC-PX-022/029, PX-003 note text) is inferred from the P3 exit criterion (routing decisions, rewritten bodies, ledger
  lines). No consumer reads the decision log. The owner may override.
- **Superseded / retracted:** no BC is fully retracted. Superseded in detail: BC-BF-001..005 (by BC-BF-006..013, r3); BC-PX-040's replay rule (by
  BC-PX-045, r4); BC-PX-014/015 (detail in BC-PX-037); BC-PX-016 (detail in BC-PX-045); BC-EX-015 (detail in BC-EX-018/025). Narrowed: BC-PX-031
  (RET-06). Legacy-only behavior that Go replaces: BC-SL-068 (Go contract BC-SL-098, D4-EX-2). Rationale retracted: BC-SL-100 (RET-12). Crash-catalogue
  predicates retracted: CP-T (RET-07).

### 7.2 Totals

| Component | BCs | BX | JE | OOS | Approved deviation | Pending OD (primary) |
|---|---|---|---|---|---|---|
| Status line (SL) | 103 | 97 | 0 | 0 | 4 (D4-EX-2) | 2 (OD-14, OD-30) |
| Proxy (PX) | 45 | 37 | 0 | 3 | 1 (D13) | 4 (OD-07, OD-16, OD-26, OD-28) |
| Exporter (EX) | 26 | 0 | 16 | 1 | 0 | 9 (OD-11 ×2, OD-22, OD-23 ×2, OD-29 ×3, OD-33) |
| Stop hook (HK) | 23 | 3 | 18 | 0 | 0 | 2 (OD-12) |
| Launcher (LN) | 11 | 0 | 8 | 2 | 1 (D14) | 0 |
| Coordinator (CO) | 2 | 0 | 0 | 2 | 0 | 0 |
| Preflight (PF) | 2 | 0 | 2 | 0 | 0 | 0 |
| Backfill (BF) | 13 | 0 | 0 | 0 | 0 | 13 (OD-36) |
| Services (SV) | 2 | 0 | 0 | 2 | 0 | 0 |
| **Total** | **227** | **137** | **44** | **10** | **6** | **30** |

- By phase: P1 103, P2 28 (26 EX + 2 SV), P3 44, P4 39 (23 HK + 11 LN + 2 CO + 2 PF + BC-PX-031), unscheduled 13.
- By last round: B 82, r1 87, r2 25, r3 20, r4 13.
- Secondary tags: D4-EX-1 ×2 (BC-SL-023/080), OD-03 ×3, OD-19 ×3, OD-04/05/13/15/16/31/32 ×2 each, and OD-06/08/09/10/14/17/18/22/23/24/27/28/30/33/35
  and D13 ×1 each.
- New this round: 3 (BC-SL-103, BC-PX-045, BC-EX-026). Refined this round: 10 (BC-SL-100; BC-PX-013, 019, 024, 026, 037, 040, 044; BC-EX-024, 025).

### 7.3 Index

| ID | Title | Go package | Ph | Parity | Also | Conf | Last | Flags |
|---|---|---|---|---|---|---|---|---|
| BC-SL-001 | Guard: any exception in main() prints the 29-byte degraded line, exit 0 | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-002 | Non-JSON / non-object stdin treated as {} | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-003 | Rows joined by \n; row 2 iff ROWS>=2 and width rule | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-004 | Trim: visible width = code points after SGR strip | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-005 | COLUMNS parse (Python int grammar), else 0 | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-006 | Lane pill from LOCAL_MODEL_PREFIXES startswith | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-007 | Model label display_name or id or ? | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-008 | Project label basename(normpath(dir)) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-009 | Branch lookup walk (.git dir/file, HEAD) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-010 | Branch segment and git cache (TTL 5 s) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-011 | Context thermometer and denominator | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-012 | Composition percentages (banker's round) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-013 | Cache-hit segment | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-014 | Limits hidden on reroute-all prefixes | `internal/statusline` | P1 | BX |  | M | B |  |
| BC-SL-015 | Expired window (resets_at <= now) unreported | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-016 | Window pace/absolute colour bands | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-017 | Window countdown format and 1.15 gate | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-018 | Rate-limit smoothing (RL_KEEP 1800 s) | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-019 | Lines segment and _fmt_lines | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-020 | Timer segment and _hm | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-021 | API-time suffix | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-022 | Window-age suffix (house glyph) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-023 | Window start via ps ancestor walk | `internal/platform` | P1 | BX | D4-EX-1 (Windows) | H-R/L | r1 |  |
| BC-SL-024 | Token segment and _fmt_tok_c | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-025 | Dollar segment colours | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-026 | $/h segment | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-027 | Pick (displaced cost) segment | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-028 | record_cost write | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-029 | cost_thresholds percentiles | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-030 | No transcript -> parser returns None | `internal/statusline` | P1 | BX |  | M | B |  |
| BC-SL-031 | Mix cache name and reset rules | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-032 | 512 KB read window and long-line completion | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-033 | bytes.splitlines + json.loads per line | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-034 | Usage dedup per message id (256 ids) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-035 | Usage accumulation | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-036 | Rebuild rule (20,000 excess) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-037 | compact_boundary resets composition and pp | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-038 | Composition per block (json.dumps lengths) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-039 | Last-turn rate machine | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-040 | fetch_sample (VM query, 1.5 s) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-041 | get_sample TTL/KEEP_DEAD state machine | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-042 | History point rules (90 s, 2 s gap) | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-043 | Row-2 freshness ladder and stale suffix | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-044 | Health dot | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-045 | Queue segment | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-046 | KV segment | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-047 | Throughput segments | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-048 | Sparkline | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-049 | TTFT segment | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-050 | Power segment | `internal/statusline` | P1 | BX |  | H-R | B |  |
| BC-SL-051 | Idle segment | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-052 | Cache I/O (load/save, raw sid in name) | `internal/statusline` | P1 | BX | OD-03 (Windows) | H | r1 |  |
| BC-SL-053 | VM fetch runs whenever ROWS>=2 | `internal/statusline` | P1 | BX |  | M | B |  |
| BC-SL-054 | trim_to_fit (double reset; single at cache-hit) | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-055 | Negative COLUMNS disables trim and hides row 2 | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-056 | heat() HSV colours | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-057 | Thermometer quirks (/0K, /1000K, NaN crash) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-058 | Model label str() of non-str | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-059 | posix normpath // label | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-060 | Cache-hit NaN/inf rendering | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-061 | Pace band boundary at rem = 0.9 length | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-062 | _fmt_tok_c no unit promotion (1000k) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-063 | _fmt_lines OverflowError on inf (CP-S11) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-064 | _hm ValueError on inf (CP-S12/S13) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-065 | First line of a message supplies its usage | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-066 | Short line + long line takes two refreshes | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-067 | splitlines/json.loads(bytes) acceptance set | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-068 | Sticky transcript crash (legacy) | `internal/statusline` | P1 | D4-EX-2 |  | H | r2 | Go contract in BC-SL-098 |
| BC-SL-069 | _iso_ts grammar (3.11 fromisoformat, local naive) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-070 | Mix cache sanitizing per code point | `internal/statusline` | P1 | BX | OD-03 (Windows) | H | r1 |  |
| BC-SL-071 | json.dumps length rules for composition | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-072 | text/thinking value types (len of list; crash on number) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-073 | Sparkline NaN/+Inf crash (CP-N02) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-074 | KV NaN crash (CP-N01) and cell math | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-075 | Row-2 NaN/inf rendering; wall colour mismatch | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-076 | Strict stdio (ruled); invalid UTF-8 -> {} | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-077 | main() side-effect order | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-078 | Sid with / leaks temp file; nothing persists | `internal/statusline` | P1 | BX | OD-03 (Windows) | H | r1 |  |
| BC-SL-079 | Numeric sid: throttle and self-exclusion fail | `internal/statusline` | P1 | OD-30 |  | H | r3 |  |
| BC-SL-080 | ps output parsing (C locale, spaces in comm) | `internal/platform` | P1 | BX | D4-EX-1 (Windows) | H | r1 |  |
| BC-SL-081 | Window-age format | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-082 | $ and $/h number formatting | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-083 | Pick eq threshold 0.005 | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-084 | Idle strict > 300 and age format | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-085 | Mine (last-turn) segment | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-086 | TTFT format boundaries | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-087 | Import-time env grammar (CP-X01/X02) | `internal/config` | P1 | BX |  | H | r1 |  |
| BC-SL-088 | transcript_path type semantics (int = fd) | `internal/statusline` | P1 | BX |  | H | r1 |  |
| BC-SL-089 | Row goldens A/B/C | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-090 | Trim breakpoints | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-091 | get_sample pinned sequence, cache key order | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-092 | HIST_MIN_GAP reachability | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-093 | effective_rl sequence and sticky CP-S09 | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-094 | Turn-machine exhaustive table | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-095 | Turn identity ignores seen_ids | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-096 | json.dumps length oracle (63 cases) | `internal/statusline` | P1 | BX |  | H | r2 |  |
| BC-SL-097 | --subagent entry point (CP-A01..A03) | `internal/statusline` | P1 | OD-14 |  | H | r2 |  |
| BC-SL-098 | D4-EX-2 Go contract: W-predicates, delete-the-line oracle | `internal/statusline` | P1 | D4-EX-2 |  | H | r3 |  |
| BC-SL-099 | D4-EX-2 table tests (21 rows) | `internal/statusline` | P1 | D4-EX-2 |  | H | r3 |  |
| BC-SL-100 | Legacy persists a poisoned cur.out (lu set) | `internal/statusline` | P1 | D4-EX-2 | OD-32 | H | r4 | rationale retracted (RET-12) |
| BC-SL-101 | Cost colouring goldens (20 seeded sessions) | `internal/statusline` | P1 | BX |  | H | r3 | r4: re-confirmed |
| BC-SL-102 | record_cost write contract | `internal/statusline` | P1 | BX | OD-30 | H | r3 | r4: re-confirmed |
| BC-SL-103 | cur with t0 null and non-numeric out: written by legacy and Go, harmless | `internal/statusline` | P1 | BX | OD-32 | H | r4 | new r4 |
| BC-PX-001 | Bridge WebSocket upgrade -> bridge_ws_connect | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-002 | Non-api.anthropic.com or non-/v1/messages* untouched | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-003 | Unparseable body -> note, passthrough | `internal/proxy` | P3 | BX | OOS (note text) | M | B |  |
| BC-PX-004 | Attribution stash (headers, metadata, req_bytes chars) | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-005 | Accept-Encoding: identity on both lanes | `internal/proxy` | P3 | BX | D13 (non-POST paths) | H | r1 |  |
| BC-PX-006 | Non-prefix model -> Anthropic lane, anth_request | `internal/proxy` | P3 | BX |  | H-R | B |  |
| BC-PX-007 | Server-tool model -> anthropic-server-tools | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-008 | DGX rewrite: model_served, normalize, re-serialize iff changed | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-009 | DGX headers X-DGX-*, dgx_request | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-010 | Upstream switch, Bearer key, anthropic-beta removed | `internal/proxy` | P3 | OD-07 | OD-06 | M | B |  |
| BC-PX-011 | Inject empty input_schema | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-012 | Block filter and tool-set rebuild | `internal/proxy` | P3 | BX | OD-09 (post-cutover) | M | B |  |
| BC-PX-013 | anth_ratelimit on change per session | `internal/proxy` | P3 | BX |  | H-R | r4 |  |
| BC-PX-014 | SSE response -> tap installed (any host) | `internal/proxy` | P3 | BX |  | M | B | detail in BC-PX-037 |
| BC-PX-015 | Buffer JSON/>=400, else stream | `internal/proxy` | P3 | BX |  | M | B | detail in BC-PX-037 |
| BC-PX-016 | Tap feed: complete lines, 64,000-byte tail | `internal/proxy` | P3 | BX |  | M | B | detail in BC-PX-045 |
| BC-PX-017 | Tap _scan: usage only from top-level usage.input_tokens | `internal/proxy` | P3 | BX |  | H | r2 |  |
| BC-PX-018 | cache_fields and tap maxima | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-019 | Anthropic response: anth_reply (+cache fields), anth_usage | `internal/proxy` | P3 | BX |  | M | r4 |  |
| BC-PX-020 | DGX response: dgx_reply, dgx_usage (tap only) | `internal/proxy` | P3 | BX |  | M | r1 |  |
| BC-PX-021 | DGX >=400: error-body note and failed-req capture | `internal/proxy` | P3 | BX | OD-18 (P-S4) | M | B |  |
| BC-PX-022 | DGX success decision note | `internal/proxy` | P3 | OOS |  | M | B | inferred from PLAN 7 P3 criterion |
| BC-PX-023 | extract_stop_reason and alias map | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-024 | error hook -> <lane>_upstream_error (lane = non-DGX host) | `internal/proxy` | P3 | BX | OD-16, OD-28 | H | r4 |  |
| BC-PX-025 | _account_hint | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-026 | bridge_ws_close on every bridge response | `internal/proxy` | P3 | BX |  | M | r4 |  |
| BC-PX-027 | websocket hooks never log (dead) | `internal/proxy` | P3 | BX |  | M | B |  |
| BC-PX-028 | ledger() writer (json.dumps defaults, OSError swallowed) | `internal/ledger` | P3 | BX |  | M | B |  |
| BC-PX-029 | note() decision log | `internal/proxy` | P3 | OOS |  | M | B | inferred from PLAN 7 P3 criterion |
| BC-PX-030 | Config read at import; reload re-imports | `internal/config` | P3 | OD-26 |  | M | B |  |
| BC-PX-031 | Trust CLI (remove/rotate narrowed) | `internal/ca` | P4 | OOS |  | M | r2 | replaced by hylo ca (D13); RET-06 |
| BC-PX-032 | Accept-Encoding precondition set (I1) | `internal/proxy` | P3 | BX |  | H | r1 |  |
| BC-PX-033 | No field merge: last qualifying event wins (I2) | `internal/proxy` | P3 | BX |  | H | r2 |  |
| BC-PX-034 | When *_usage events are written (truth table) | `internal/proxy` | P3 | BX |  | H | r3 |  |
| BC-PX-035 | Method-agnostic prefix: /v1/messages/batches | `internal/proxy` | P3 | D13 | OD-10 | M | r1 |  |
| BC-PX-036 | count_tokens never writes anth_usage | `internal/proxy` | P3 | BX |  | M | r1 |  |
| BC-PX-037 | Stream decision table (12.3.1 defaults) | `internal/proxy` | P3 | BX |  | H | r4 | config.yaml absent: confirmed |
| BC-PX-038 | Streamed body unreadable -> path (b) yields nothing | `internal/proxy` | P3 | BX |  | H | r3 |  |
| BC-PX-039 | Interrupted stream -> error hook, no reply | `internal/proxy` | P3 | OD-16 |  | H | r3 |  |
| BC-PX-040 | Tap result depends on chunk boundaries (raising lines, >64,000 B) | `internal/proxy` | P3 | BX |  | H | r4 | harness rule superseded by BC-PX-045 |
| BC-PX-041 | normalize_for_dgx re-serialization bytes | `internal/proxy` | P3 | BX |  | H | r3 |  |
| BC-PX-042 | uses_server_tool type semantics | `internal/proxy` | P3 | BX | OD-08 | H | r3 |  |
| BC-PX-043 | Host header after switch to the backend | `internal/proxy` | P3 | BX |  | H | r3 | P3 verification item V-1 |
| BC-PX-044 | Error-cause table, texts, client-visible results | `internal/proxy` | P3 | OD-28 | OD-16, OD-17 | H | r4 | 502 bytes: V-2 |
| BC-PX-045 | Tap boundary-insensitivity and per-line replay oracle | `internal/proxy` | P3 | BX | OD-35 | H | r4 | new r4 |
| BC-EX-001 | Start: rebuild, bind 0.0.0.0:PORT, serve forever | `internal/ledger` | P2 | JE | OD-27, OD-33 | M | B |  |
| BC-EX-002 | Non-/metrics -> 404 | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-003 | Rebuild on ?rebuild or size change | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-004 | Full rescan; status null aborts the scrape | `internal/ledger` | P2 | OD-11 |  | M | B |  |
| BC-EX-005 | t parsed naive local; last_* timestamps | `internal/ledger` | P2 | JE | OD-22 | M | B |  |
| BC-EX-006 | Session funnel, 50 newest | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-007 | dgx_usage accumulation | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-008 | anth_request account always unknown | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-009 | anth_usage accumulation; duration never present | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-010 | dgx_request accumulation, est_prompt | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-011 | dgx_reply duration and >=400 errors | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-012 | anth_reply/anthropic_reply passthrough | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-013 | dgx_upstream_error counted; anthropic_ ignored | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-014 | Hook-log tallies by substring | `internal/ledger` | P2 | OD-23 |  | M | r2 |  |
| BC-EX-015 | Exposition order and escaping | `internal/ledger` | P2 | OD-29 |  | M | B | detail in BC-EX-018/025 |
| BC-EX-016 | Conditional timestamp and p_done lines | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-017 | _account_device | `internal/ledger` | P2 | JE |  | M | B |  |
| BC-EX-018 | Exposition golden (synthetic ledger) | `internal/ledger` | P2 | OD-29 |  | H | r3 |  |
| BC-EX-019 | Tally misattribution (tags in tail) | `internal/ledger` | P2 | OD-23 |  | H | r2 |  |
| BC-EX-020 | DST false idle | `internal/ledger` | P2 | OD-22 |  | H | r2 |  |
| BC-EX-021 | Crash process contract: zero bytes, permanent | `internal/ledger` | P2 | OD-11 |  | H | r2 |  |
| BC-EX-022 | Routing and rebuild trigger | `internal/ledger` | P2 | JE |  | H | r2 |  |
| BC-EX-023 | Deploy artifact (~ not expanded), 3.9 oracle | `internal/platform` | P2 | OOS | OD-15 | L | r2 |  |
| BC-EX-024 | Event-name treatment per consumer | `internal/ledger` | P2 | JE |  | H | r4 |  |
| BC-EX-025 | Non-contiguous families; duplicate series with distinct values | `internal/ledger` | P2 | OD-29 |  | H | r4 |  |
| BC-EX-026 | One idle connection stalls every scrape (F-1) | `internal/ledger` | P2 | OD-33 |  | H | r4 | new r4, carried from P2r5 |
| BC-HK-001 | Invalid stdin -> allow; non-object -> exit 1 | `internal/hook` | P4 | JE |  | M | B |  |
| BC-HK-002 | tail = last 160 code points | `internal/hook` | P4 | JE |  | M | B |  |
| BC-HK-003 | Non-English check first | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-004 | stop_hook_active -> allow | `internal/hook` | P4 | JE |  | M | B |  |
| BC-HK-005 | DGX_AUTOCONTINUE=0 -> allow | `internal/hook` | P4 | JE | OD-05 | M | B |  |
| BC-HK-006 | Ends with ? -> allow | `internal/hook` | P4 | JE |  | M | B |  |
| BC-HK-007 | Colon fake | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-008 | kev_state rendering | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-009 | Kev POST | `internal/hook` | P4 | JE |  | L | B |  |
| BC-HK-010 | Kev median (up to 3 calls) | `internal/hook` | P4 | OD-12 |  | H | r2 |  |
| BC-HK-011 | Kev verdict p<0.40 | `internal/hook` | P4 | JE |  | M | B |  |
| BC-HK-012 | Regex fallback should_continue | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-013 | emit: stdout JSON + log line | `internal/hook` | P4 | BX | OD-04 | H | r1 |  |
| BC-HK-014 | ANNOUNCE match, Unicode \b divergences | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-015 | Sentence split (no RE2 lookbehind) | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-016 | should_continue exhaustive cases | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-017 | Colon fake = strip + endswith(':') | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-018 | non_english ranges and ratio | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-019 | No top-level guard: crash -> exit 1, no stdout | `internal/hook` | P4 | JE |  | M | r1 |  |
| BC-HK-020 | kev_state block rendering details | `internal/hook` | P4 | JE |  | H | r1 |  |
| BC-HK-021 | emit bytes; log uses Python repr | `internal/hook` | P4 | BX | OD-04 | H | r1 |  |
| BC-HK-022 | Median timing; (p, None) crash (H-04) | `internal/hook` | P4 | OD-12 |  | H | r2 |  |
| BC-HK-023 | Log line <-> exporter tally coupling | `internal/hook` | P4 | BX | OD-23 | H | r2 |  |
| BC-LN-001 | trust subcommand -> dgx_proxy.py trust | `cmd/hylo (run)` | P4 | OOS |  | M | B | replaced by hylo ca |
| BC-LN-002 | Exports prefixes/served model; custom headers | `cmd/hylo (run)` | P4 | JE |  | M | B |  |
| BC-LN-003 | Preflight unless DGX_SKIP_PREFLIGHT=1 | `cmd/hylo (run)` | P4 | JE |  | M | B |  |
| BC-LN-004 | Per-window mitmdump, HTTPS_PROXY/NODE_EXTRA_CA_CERTS exported | `cmd/hylo (run)` | P4 | D14 | OD-19, OD-24 | M | B |  |
| BC-LN-005 | API_TIMEOUT_MS, AUTO_MODE_SERVER exports | `cmd/hylo (run)` | P4 | JE |  | M | B |  |
| BC-LN-006 | Profile sourced after proxy start | `cmd/hylo (run)` | P4 | OOS |  | M | B | one proxy per user (PLAN 6) |
| BC-LN-007 | claude argv | `cmd/hylo (run)` | P4 | JE |  | M | B |  |
| BC-LN-008 | Hook env exports and defaults | `cmd/hylo (run)` | P4 | JE | OD-05 | M | B |  |
| BC-LN-009 | --settings JSON | `cmd/hylo (run)` | P4 | JE | OD-14 | M | B |  |
| BC-LN-010 | DGX_PRINT_ARGS dry run | `cmd/hylo (run)` | P4 | JE |  | M | B |  |
| BC-LN-011 | Child claude; trap kills mitmdump | `cmd/hylo (run)` | P4 | JE |  | M | B |  |
| BC-CO-001 | Coordinator reuse under flock (unwired) | `internal/proxy` | P4 | OOS | OD-19 | L | B |  |
| BC-CO-002 | Coordinator port pick (unwired) | `internal/proxy` | P4 | OOS | OD-19 | L | B |  |
| BC-PF-001 | Preflight TCP connect, 4 s | `internal/platform (doctor)` | P4 | JE |  | M | B |  |
| BC-PF-002 | Preflight error classes | `internal/platform (doctor)` | P4 | JE |  | M | B |  |
| BC-BF-001 | Per-transcript message pricing | `cmd/hylo (cost backfill)` | unsched. | OD-36 | OD-13 | M | B | superseded in detail by BC-BF-006..008 |
| BC-BF-002 | Lane = max output tokens, tie -> dgx | `cmd/hylo (cost backfill)` | unsched. | OD-36 |  | M | B | superseded in detail by BC-BF-009 |
| BC-BF-003 | api_ms spans >= 30 min | `cmd/hylo (cost backfill)` | unsched. | OD-36 |  | M | B | superseded in detail by BC-BF-010 |
| BC-BF-004 | Session selection and write | `cmd/hylo (cost backfill)` | unsched. | OD-36 |  | M | B | superseded in detail by BC-BF-011 |
| BC-BF-005 | Summary and atomic write | `cmd/hylo (cost backfill)` | unsched. | OD-36 |  | M | B | superseded in detail by BC-BF-012 |
| BC-BF-006 | Line filter and clock | `cmd/hylo (cost backfill)` | unsched. | OD-36 |  | H | r3 |  |
| BC-BF-007 | Message entity (first usage wins) | `cmd/hylo (cost backfill)` | unsched. | OD-36 |  | H | r3 |  |
| BC-BF-008 | Pricing (family by substring, cache split) | `cmd/hylo (cost backfill)` | unsched. | OD-36 | OD-13 | H | r3 |  |
| BC-BF-009 | Lane, set-but-empty prefixes | `cmd/hylo (cost backfill)` | unsched. | OD-36 |  | H | r3 |  |
| BC-BF-010 | Model time | `cmd/hylo (cost backfill)` | unsched. | OD-36 |  | H | r3 |  |
| BC-BF-011 | Session selection | `cmd/hylo (cost backfill)` | unsched. | OD-36 |  | H | r3 |  |
| BC-BF-012 | History I/O, NaN written | `cmd/hylo (cost backfill)` | unsched. | OD-36 | OD-31 | H | r3 |  |
| BC-BF-013 | Abort contract | `cmd/hylo (cost backfill)` | unsched. | OD-36 | OD-31 | H | r3 |  |
| BC-SV-001 | Exporter LaunchAgent (scrubbed path) | `internal/platform` | P2 | OOS | OD-15 | L | B | scrub artifact |
| BC-SV-002 | ssh -R ledger tunnel agent | `internal/platform` | P2 | OOS |  | M | B | home-lab deployment |

Crash catalogues stay indexed by their own IDs (status line CP-S/T/N/C/X/A = 43; proxy P-R1..R4, P-S1..S4; exporter E-*; hook H-01..H-08; backfill
B-01..B-08). Their dispositions: CP-S/N and CP-X01/X02 BX (ruled); CP-T D4-EX-2; CP-C OOS (ruled); CP-X03/X04 not parity-relevant; CP-A OD-14; P-S4
OD-18; E-* OD-11; H-04 OD-12; B-* OD-31/OD-36.

---

## Owner checks carried forward (after the soak; not attempted)

1. Grafana per-session panel with ≥ 2 recent sessions, to confirm that VictoriaMetrics ingests the non-contiguous `dgx_llm_session_*` fragments
   (BC-EX-025). Optionally `promtool check metrics` offline on one saved scrape body.
2. VictoriaMetrics NaN capture: one `/api/v1/query` response for the exact `QUERY` on an idle box, under light load, and with fewer than 20 TTFT
   samples (CP-N01/N02 reachability; P2r4 gap 1).
3. One-word confirmation of OD-27's hylo exporter default (P2r5).

## Delta Summary

- **New BCs (3):** BC-SL-103 (`t0`-null non-numeric `cur.out`: a crash-free state written by legacy and by Go; Go type and order constraints),
  BC-PX-045 (tap boundary-insensitivity theorem, property test and per-line replay oracle; closes r3 gap 4), BC-EX-026 (exporter idle-connection
  stall, carried from P2r5 F-1).
- **Refined (10):** BC-SL-100 (trigger is "no closer in the same window"); BC-PX-040 (exact bound ≤ 64,000 bytes excluding `\n`; replay rule
  superseded), BC-PX-037 and P-S4 (confirmed: no `config.yaml`), BC-PX-024/044 and BC-EX-024 (non-DGX-host scope, CONV-ABS-14), BC-PX-019 (cache
  fields on `anth_reply`), BC-PX-026 (every bridge response), BC-PX-013 (all api.anthropic.com paths, shared null slot), BC-EX-025 (duplicate series
  carry distinct values).
- **Confirmed (re-pinned independently):** BC-SL-100 mechanism, BC-SL-101's two mismatches, BC-EX-025 fragmentation and duplicates, BC-SL-102
  duplicate keys.
- **Retraction:** CONV-ABS-15 (BC-SL-100's reader-rule rationale; OD-32 amended with a `t0`-is-numeric condition).
- **Mappings:** round 3's 10 items → OD-21, 16, 18, 22, 23, 28, 29, 30, 31, 32 (P2r5 numbering). New OD-35 (tap lines > 64,000 B) and OD-36 (backfill
  unscheduled).
- **Index:** 227 BCs. By component: SL 103, PX 45, EX 26, HK 23, LN 11, CO 2, PF 2, BF 13, SV 2. By parity: BX 137, JE 44, OOS 10, approved deviation
  6, pending OD 30.
- **Crosswalk:** CONV-ABS 1-15 issued, 12 numbers in use (9-11 never used), 13 meanings, 12 distinct retractions as RET-01..RET-12 (P2-6 = P3-7
  aliased).
- **Verification items:** V-1 Host header, V-2 502 bytes, V-3 shutdown and in-flight flows.

## Remaining Gaps (verbatim-carryable)

1. Owner checks after the soak (carried, not attempted): the Grafana per-session panel with ≥ 2 sessions (VictoriaMetrics ingesting fragments);
   optionally `promtool check metrics` offline on a saved scrape; the VictoriaMetrics NaN capture.
2. P3 replay verification items V-1 (Host header bytes), V-2 (mitmproxy 502 page bytes on connect failure and `server closed connection`), V-3
   (does mitmproxy shutdown fire `error` for in-flight flows). Each needs a stub-backend rig, not the live proxies.
3. Owner decisions: 34 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-36), including the amended OD-32 and the new OD-35/OD-36.
4. Not verifiable from authorized sources (LOW): which of two conflicting duplicate session samples VictoriaMetrics keeps (BC-EX-025).

## Novelty Assessment

Novelty: SUBSTANTIVE

Most of this round is NITPICK by the stated rule: the 227-row index, the CONV-ABS crosswalk, the OD mapping, four confirmations, the pass-2 hand-offs,
and the tap decision. The tap work is a proof plus a harness contract for behavior already known since r2, so it is a refinement. One finding is an
**error in an existing BC** and changes the Go spec:

- **CONV-ABS-15 / BC-SL-103:** BC-SL-100's reader rule was justified as "what Go would hold". That is inexact for the `lu`-set form (native Go keeps
  the previous turn open, and W's composition stays counted). It is **wrong** for the `t0`-null form: D4-EX-2 does not skip that line, so **Go itself
  writes a non-numeric `cur.out`**. Applying OD-32 as worded would make Go's cache diverge from legacy's (pinned: `"out": 900` vs `"abc"`). Two spec
  changes follow. The Go mix-cache `cur.out` must be a raw JSON value, and `finishTurn` must test `t0` before `out`. OD-32 gains a "`t0` is a number"
  condition. Without this finding, a Go implementer would type `cur.out` as a number, which cannot represent a state the Go parser itself produces.

The finding is narrow and limited to non-production transcript shapes (a non-numeric `output_tokens` on an already-seen id). It is still a correction
to a contract and to an owner recommendation, not a refinement of wording.

## Convergence Declaration

Another round needed: one substantive item (CONV-ABS-15, BC-SL-103) changed a BC and an owner recommendation this round. Everything else was index,
crosswalk, mapping and confirmation work. Open items are owner checks, verification items V-1..V-3 that need a stub rig, and owner decisions.

## State Checkpoint

```yaml
pass: 3
round: 4
status: complete
files_scanned: 3 legacy files in part (dgx_proxy.py, dgx_statusline.py, dgx_ledger_exporter.py); all pass files incl. P2r5
timestamp: 2026-11-14T07:04:03Z
novelty: SUBSTANTIVE
new_bcs: {SL: 1, PX: 1, EX: 1}
refined_bcs: 10
retractions: [CONV-ABS-15]
bc_index_total: 227
bc_index_by_parity: {BX: 137, JE: 44, OOS: 10, approved_deviation: 6, pending_OD: 30}
owner_decisions: 36 (OD-01..OD-36; 34 pending, 2 ruled)
new_owner_items: [OD-35, OD-36]
od32: amended (t0-is-numeric condition)
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r4/
next: pass 3 round 5 (carry "Remaining Gaps" verbatim)
```
