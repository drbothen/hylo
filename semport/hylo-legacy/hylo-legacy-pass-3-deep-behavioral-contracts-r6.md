# Pass 3 deepening, round 6: behavioral contracts (hylo-legacy)

- **Scope:** `legacy/`, unchanged: 11 files, 3,181 lines (recounted with `wc -l`). Re-read **statement by statement** this round (AST
  statement counts from `stmt_count.py`, docstrings included):

  | Region | Functions re-read in full | Statements |
  |---|---|---|
  | A1 status line row 1 | `render_lane` `:440-637` and every widget renderer it calls: `fmt_ctx :418-437`, `git_segment :399-413`, `mix_segment :1177-1183`, `mix_labels :1157-1174`, `_fmt_lines :849-860`, `_fmt_tok_c :863-873`, `record_cost :224-237`, `cost_thresholds :240-262`, `heat :144-148`, `truecolor :140-141`; plus `main :1200-1235` for the inputs it passes | 217 |
  | A1 status line row 2 | `render_telemetry :693-702`, `render_telemetry_fields :725-835`, `serving_state :705-722`, `sparkline :659-690`, `_norm_pt :652-656` | 100 |
  | A2 exporter | `_current_size :64-68`, `esc :71-72`, `_account_device :75-91`, `rebuild :94-266`, `Handler.do_GET :270-404`, `log_message :406-407`, `__main__ :410-414` | 270 |
  | A3 proxy hooks | `ledger :56-62`, `note :65-74`, `DGXRouter.__init__/_key/request/responseheaders/response/error :78-323`, `normalize_for_dgx :467-515` | 211 |
  | A4 Stop hook main flow | `main :209-270`, `emit :204-206`, `_log :193-201`, `kev_state`, `kev_pdone`, `kev_pdone_median`, `should_continue`, `non_english` | 105 |
  | **Total** | | **903** |

  Also read (read-only, for citations only): mitmproxy 12.3.1 `http:30-45,385-445` (header and body decoding), `proxy/layers/http/__init__:494-760`
  (response/error hook exclusivity), and re-read `options:241-246`, `proxy/server:286-310,340-356`, `tools/main:120-135` for Target C.
- **Inputs read:** pass-3 r4 (canonical index, §7) and r5 (diff, BC-EX-027, BC-PX-046); the BC texts of the broad pass-3 file, r1 (§A0-A8, CP-S
  table), r2 (§A1 goldens, §B4 normalization, §C) and r3 (exporter tables) for every BC citing the four regions; pass-2 r2 (§4-§6 entity and crash
  catalogues), r3 (§1.2-1.3 `get_text` and header tables), r4/r5 (as cited); **pass-2 r7** (`…-pass-2-deep-domain-r7.md`, present from 01:24 local;
  read only, not edited).
- **Method:** static reading plus scripts in
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r6/`, run with the oracle
  `/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7); the exporter script also with `/usr/bin/python3 -I` (3.9.6, the exporter's production
  interpreter). Every script execs a **text copy** of a legacy file (the proxy copy stops at line 549, before the trust CLI; the exporter copy runs
  with `__name__ != "__main__"`, so nothing binds) in a fresh namespace, with `HOME`, ledger, hook log and decision log redirected to the scratchpad,
  and asserts the cited source lines have not drifted. Scripts and outputs: `stmt_count.py` → `stmt_count_out.txt`; `sl_pick.py` →
  `sl_pick_out.txt`; `ex_surrogate.py` → `ex_surrogate_out.txt` (both interpreters); `px_note.py` → `px_note_out.txt` (run twice: `LANG=en_US.UTF-8`
  strict, and `LC_ALL=C`, which turns on UTF-8 mode). One Go check (`gosur/main.go`, go1.26.5, `GOCACHE` in the scratchpad) → `gosur_out.txt`.
  No legacy main(), no server, no proxy, nothing networked. `CLAUDE.local.md` was not read. No git commit.
- **Notation:** `\e` is ESC (U+001B). `\udcXX` written in a JSON string is the 6-character JSON escape (ASCII), not a raw code point. A bare `:N`
  means the file named in the section heading. **P2rN**/**P3rN** = pass-2/pass-3 round N.
- **IDs (append-only):** new **BC-PX-047** (carried from P2r7) and **BC-PX-048** (found here). New exporter crash row **E-22**; new proxy crash rows
  **P-R5, P-S5, P-S6, P-E1**. Retraction **CONV-ABS-21** (21-24 reserved for this round; pass-2 r7 starts at 25 and issued none). New owner item
  **OD-45** (pass-2 r7 took OD-41 and OD-42; pass-2 r8 took OD-43; OD-44 is reserved for pass-2 r9).
- **Orchestrator correction applied (2026-11-14, received during this round):** the P3r4 §0 evidence "0 ` HTTP/2.0` lines in the mitmdump logs" was
  wrong (a glob bug); the correct count is **15,131 lines (~7,566 HTTP/2 flows)**, retracted by pass-2 r8 as **CONV-ABS-25** and attributed to child
  tools that trust the CA (gh, git, brew and similar), not to Claude Code, whose own traffic is still HTTP/1.1. Two `/v1/messages` requests from a
  non-Claude-Code h2 client were rerouted to the DGX (new D14 harm). **CONV-ABS-26:** Remote Control does **not** use `bridge.claudeusercontent.com`
  (0 occurrences in 40 logs), so `bridge_ws_connect`/`bridge_ws_close` never fire in production (OD-43); the real channels are a WebSocket on
  `api.anthropic.com/api/frame/sync` and long-lived streaming GETs on `/v1/code/sessions/…` (HY-PASS-1: pass-through flows have no total-duration
  limit). The "0 `error in script` / 0 `nonetype`" counts stand. §5 and §6 below are written with these corrections; no finding of §1-§4 depended on
  either fact.

---

## 1. Target A: line-by-line re-read, statement by statement against the citing BCs

Method per region: every statement was read in order and matched to the BC (or crash-catalogue row, or pass-2 entity row) that states its effect. A
statement "has a stated effect" when a BC's contract text, a pinned golden, or a catalogue row predicts its output, file write, ledger line, exit or
crash. Only statements with **no** such statement are listed as findings.

### 1.1 A1 status line, row 1 (217 statements)

| Statements | Stated by |
|---|---|
| `:441-449` model, id, prefixes, `on_dgx`, pill | BC-SL-006/007/058; CP-S01 (`:442`), CP-S02 (`:446`) |
| `:451-462` workspace, project dir, git, label | BC-SL-008/059, BC-SL-009/010; CP-S03 (`:452`), CP-S04 (`:405`/`:460`) |
| `:463-468`, `fmt_ctx`, `heat`, `truecolor`, `mix_segment`, `mix_labels` | BC-SL-011/057/056, BC-SL-012; CP-S05/S06/S07 |
| `:477-479` cache hit | BC-SL-013/060; CP-S08 |
| `:487-532` limits | BC-SL-014..017, 061; CP-S09; goldens BC-SL-089 |
| `:534-563` lines, timer, API time, ⌂ | BC-SL-019..022, 063, 064, 081; CP-S10..S13; clocks in r1 §A0 |
| `:574-600` tokens | BC-SL-024/062; goldens |
| `:601-625` `$`, `record_cost`, `cost_thresholds`, `$/h` | BC-SL-025/026/028/029/079/082/102; CP-S15; order in BC-SL-077 |
| **`:626-635` ⛏** | **BC-SL-027/083 state the computation, but not that the whole block sits inside `if … usd > 0` (`:602`)** → finding R1-1 |
| `main :1208-1230` inputs to `render_lane` | BC-SL-053, 077, 018 |

**Finding R1-1 (unstated effect, BC-SL-027 wrong as worded).** BC-SL-027 says ⛏ appears on the DGX lane whenever `tin + tout > 0`. In the source,
`:626-635` is nested in the `$` block that starts at `:602` (`if isinstance(usd, (int, float)) and usd > 0:`), and ⛏ is appended to `cseg`, not to
`parts`. So ⛏ (like `$/h`) needs `cost.total_cost_usd` numeric and **> 0**. Pinned (`sl_pick.py`, DGX lane, tin 2.0M, tout 50k, `dgx_mtok` 0.09,
`dgx_rate` 45.0, basis ok):

| `cost.total_cost_usd` | `$` | `$/h` | ⛏ | Last row-1 segment |
|---|---|---|---|---|
| absent | no | no | **no** | the token segment `↑2.0M ↓50k` |
| `0` | no | no | **no** | same |
| NaN | no | no | **no** | same |
| `-1.0` | no | no | **no** | same |
| `0.01` | yes | yes | yes | `\e[90m$0.01\e[0m\e[90m $0.1/h\e[0m\e[90m ⛏0.18\e[0m` |

A Go implementer following BC-SL-027 literally would print `⛏0.18` (or `⛏n/a`) as its own segment in the first four rows. Reachability: needs
transcript tokens > 0 while Claude Code reports no positive cost (for example, if a resumed session restarts the cost counter while the transcript
keeps its totals). Whether that happens is not determinable from authorized sources (LOW). The amendment is §2.1.

Other observations in this region (each already implied by a BC; recorded, no change): `git_segment` is called with the raw `proj_dir`, so
`/x/p` and `/x/p/` use different git caches while showing the same label (BC-SL-010's key definition already says `sha1(dir)` of the raw
string); `$` can be GREY (< $1) while `$/h` is coloured by the rate thresholds, because `:624` does not test `usd` (BC-SL-026 as worded already
predicts this); `cost_thresholds` reads `cost-history.json` on every refresh that has a positive cost, even when the colour cannot use it (no output
effect).

### 1.2 A1 status line, row 2 (100 statements)

Every statement maps to BC-SL-043..051 (and their r1 refinements 073, 074, 075, 084, 085, 086), BC-SL-042 (history keys), BC-SL-089 goldens A-C
(stale path keeps `»`, TTFT, power and idle; drops only the sparkline and greys the box number) and r2's 5-minute fallback golden (`▣12t/s` from
`dgx_tokens:gen_rate5m`, r2 §A2 row 8). The two idle clock reads (`:825`, `:826`) are in r1 §A0. **No unstated effect.**

### 1.3 A2 exporter (270 statements)

| Statements | Stated by |
|---|---|
| `rebuild :94-212` per-event accumulation | BC-EX-004..013, 017, 024; P2r2 §5.1 entity table (incl. `sess_proj` dead, `sess_stats` never cleared, upstream errors not in session errors, `parse_qs` blank values); E-01..E-09 |
| `rebuild :213-236` hook-log tallies | BC-EX-014, 016, 019, 023 |
| `rebuild :237-266` trim and swap | BC-EX-006, P2r2 §5.1 (`SESSION_LIMIT` slicing, stable sort) |
| `do_GET :271-287` routing and trigger | BC-EX-002, 003, 022, **027** |
| `do_GET :288-398` exposition lines | BC-EX-015, 016, 018, 025; pass-1 §4.7 irregular families (TYPE without HELP, `dgx_llm_session_tokens_in/out/errors` untyped); E-20, E-21 |
| **`do_GET :399` `.encode()`** | **no BC or E-row states that this line can raise** → finding R2-1 |
| `:400-407` headers, write, silent log | BC-EX-015, BC-EX-002 (r5 §2.4) |
| `__main__ :410-414` | BC-EX-001, 021 (startup amplification) |

**Finding R2-1 (unstated effect): E-22, a lone surrogate in any label value fails every scrape, permanently.** `json.loads` keeps a JSON escape such
as `\udce9` or `\ud800` as a lone surrogate code point. `esc()` passes it through, `sorted()` and the f-strings accept it, and the body's
`.encode()` (UTF-8, strict, `:399`) raises `UnicodeEncodeError`. The exception escapes `do_GET`; `socketserver` logs a traceback and closes the
connection with no HTTP response (P2r2 §5.2). `processed_size` was already set at `:287`, so the next scrape skips `rebuild` and raises again.
Pinned (`ex_surrogate.py`, identical on 3.11.7 and 3.9.6):

| Ledger line (ASCII, as `dgx_proxy.ledger()` writes it) | Scrape 1 | `processed_size` after scrape 1 | Scrape 2 |
|---|---|---|---|
| `"project": "café"` (valid U+00E9) | 200 | 142 = file size | 200 |
| `"project": "caf\udce9"` | `UnicodeEncodeError: 'utf-8' codec can't encode character '\udce9' in position 122: surrogates not allowed` | 142 = file size | raises again |
| `"project": "x\ud800"` | same error (`'\ud800'`) | 140 | raises again |
| `"session": "\udce9abcdefgh"` (surrogate within the 8-char label) | raises | — | — |

Differences from E-01..E-09: the startup `rebuild()` (`:411`) does **not** raise, so the process binds and stays up (no launchd crash loop);
every scrape fails until the poisoned line leaves the ledger. Same persistence as E-20.

**Why this is not only a corruption path (reachability, partly LOW).** A ledger string gets a lone `\udcXX` when a request **header** carries
bytes that are not valid UTF-8: mitmproxy decodes header values with `utf-8` + `surrogateescape` (mitmproxy 12.3.1 `http:40-41`), and
`json.dumps` (`ensure_ascii`) writes the escape (P2r3 §1.3, which considered only the session id and judged it unreachable for Claude Code's
UUIDs). The **project** header is not a UUID: the launcher builds it as `X-DGX-Project: $(basename "$PWD")` (`claude-dgx:44`). If Claude Code
transmits a non-ASCII directory name (for example `é`) as single Latin-1 bytes rather than UTF-8, the ledger gets `"project": "caf\udce9"` and
the exporter stops answering scrapes. How Claude Code encodes non-ASCII custom header values is **not determinable from authorized sources
(LOW)**; with UTF-8 bytes nothing happens (row 1). Owner check 3 below settles it on the retained ledger in one read-only count.

**Go side (pinned, go1.26.5):** `encoding/json` replaces a lone surrogate escape with U+FFFD (`"caf\udce9"` → bytes `63 61 66 ef bf bd`, no
error). A Go exporter would therefore answer 200 with `project="caf\xEF\xBF\xBD"` where legacy answers nothing. This joins the E-* class whose
parity treatment is **OD-11** (pending); no new OD.

Other observations (NITPICK, no BC change): `print(...)` at `:413` goes to a launchd `StandardOutPath` file with no `PYTHONUNBUFFERED`
(`deploy/io.hylo.ledger-exporter.plist`), so the "serving" line is block-buffered and reaches the log only when the process exits (log text,
not a parity surface; BC-EX-001 flag). `BaseHTTPRequestHandler.send_response` adds `Server:` and `Date:` headers (not part of the JE comparison).

### 1.4 A3 proxy hooks (211 statements)

| Statements | Stated by |
|---|---|
| `request :99-167` | BC-PX-001..012, 030, 032, 035, 042, 043; P-R1..P-R4 (P2r2 §4.4); BC-PX-012 rebuild goldens (P3r2 §B4), `"tools": []` added when absent (P2r2 §4.3) |
| `responseheaders :176-208` | BC-PX-013, 014, 015, 037; P2r3 §1.3 (wire order, folding, `_last_rl` reset on reload) |
| `response :211-309` | BC-PX-017..023, 026, 033, 034, 036, 038, 041; P-S1..P-S4; mirror case (P3r5 §2.4) |
| `error :316-323` | BC-PX-024, 039, 044, 046 |
| `normalize_for_dgx :474-515` | BC-PX-011, 012, 041; P-R3 |
| `ledger :56-62` | BC-PX-028 |
| **`note :65-74`, at the 11 call sites** | BC-PX-029 says "OSError swallowed" and the index marks the **text** OOS. **No BC states that `note()` can raise, or what a raise does to the hook that called it** → finding R3-1 |

**Finding R3-1 (unstated effect): `note()` raises on text it cannot encode, and the calling hook stops there.** `note()` guards the `%` formatting
(`:66-69`) and catches only `OSError` around the write (`:70-74`). The decision log is opened in text mode with the locale encoding, UTF-8 with
**strict** errors in both locale modes (pinned: `LANG=en_US.UTF-8` gives preferred encoding `UTF-8`, `utf8_mode 0`; `LC_ALL=C` gives `utf-8`,
`utf8_mode 1`; `open()` stays strict in both). A message holding a lone surrogate raises `UnicodeEncodeError`, which is a `ValueError`, not an
`OSError`. It leaves `note()`, aborts the hook, and mitmproxy logs an addon error and continues the flow. The 11 call sites by position:

| Call site | Runs before | Effect of a raise | Inputs that can carry a surrogate | Catalogue | Evidence |
|---|---|---|---|---|---|
| `:321` error hook | `ledger("<lane>_upstream_error")` at `:322` | **the `*_upstream_error` event is not written** | `attrib["project"]` (header), `msg` (mitmproxy error text) | **P-E1** | pinned: project `"caf\udce9"` → raise, ledger `[]`; `"café"` → `['dgx_upstream_error']` |
| `:286` DGX ≥ 400 | failed-request capture `:288-299` | `dgx_reply`/`dgx_usage` already written; **no `failed-req-*.json`**, no prune | the error body via `get_text(strict=False)`, which falls back to `surrogateescape` on undecodable bytes (mitmproxy 12.3.1 `http:427-441`) | **P-S5** | pinned: body `"bad \udcff byte"` → raise, ledger `['dgx_reply']`, no capture file; `"plain error"` → capture written |
| `:240` Anthropic tap note | `ledger("anth_reply")` `:245`, `anth_usage` `:247` | **neither event written** | the response `content-type` header | **P-S6** | static (MEDIUM); needs Anthropic to send non-UTF-8 header bytes (judgment: not realistic) |
| `:510` in `normalize_for_dgx` | the rest of normalization, `dgx_request` `:154`, the host switch `:161-164` | request hook aborts: **original body to Anthropic**, no `dgx_request`, no `anth_request` (outcome of P-R3). `_logged_unknown.add(btype)` at `:509` ran **before** the note, so the **next** request with the same block type is routed to the DGX normally until a reload | an unknown block `type` containing a JSON `\udcXX`/`\ud8XX` escape | **P-R5** | pinned: attempt 1 → raise, host `api.anthropic.com`, body not rewritten, ledger `[]`; attempt 2 → ok, host `192.0.2.10`, `['dgx_request']` |
| `:135`, `:140` | `return` (after the `anth_request` line) | none on the ledger | model string from the body | — | static |
| `:167`, `:297`, `:309` | end of the hook / branch | none on the ledger | model, size (int), stop reason from the body | — | static |
| `:108`, `:518` | — | cannot raise (constant text; PID int) | — | — | static |

Only the P-E1 row has a plausible production path, through the same project-header vector as E-22 (§1.3): a Latin-1 project directory would both
**suppress every upstream-error event** for that project (so `dgx_llm_request_errors_total` undercounts) and stop the exporter. P-S5 and P-R5 need
non-UTF-8 backend error bytes or a hand-crafted request (corruption class, like P-R1..R4). The contract, the retraction it implies and the Go rule
are in §2.3.

Other observation (NITPICK, normalized field): when `_t0`/`_dgx_t0` is absent (unrouted or direct-to-backend flows), `duration_s =
round(time.time() - getattr(flow, "_t0", time.time()), 3)` evaluates the left `time.time()` first, so it is `0.0` or `-0.0` (json `-0.0`). The replay
normalizes `duration_s`, and the exporter adds it to a sum (no visible effect). Recorded for the Go reader: accept `-0.0`.

Checked and **not** a finding: whether `response` and `error` can both fire for one flow (which would duplicate the mutated `_dgx` into an error
event). mitmproxy 12.3.1 `proxy/layers/http/__init__:511-512,723-744` sets `server_state = state_done` right after `HttpResponseHook`, and
`handle_protocol_error` fires `HttpErrorHook` only when the server side is not done ("We don't want to trigger both a response hook and an error
hook"); `check_killed(False)` after the response hook does not emit the error hook. So at most one of the two runs.

### 1.5 A4 Stop hook main flow (105 statements)

Every statement maps to BC-HK-001..023 and the H-01..H-08 rows (P2r2 §6): the language check before `stop_hook_active` and before
`DGX_AUTOCONTINUE` (BC-HK-018 order, BC-HK-016/017 order), the colon fake as strip + `endswith(":")` (BC-HK-017), `heuristic` computed before Kev
but used after (BC-HK-012 refined), `kev_state`'s `open("")` and int-as-fd cases (P2r2 §6.1 `transcript_path` row), the median and `(p, None)`
crash (BC-HK-010/022, H-04), `kev-allow` logged without stdout (BC-HK-011), `emit` logs before printing (BC-HK-013/021), the empty-message Kev call
(P2r2 §6), the unused `KEV_MESSAGES` (import-time crash only, P3r5 §2.4). A Kev `noul` that is NaN gives `p_done=nan` in the log, which the
exporter's `[0-9.]+` regex never matches (P2r2 §5.1, `fakestop` row). **No unstated effect.**

### 1.6 Totals

| Region | Statements | Unstated effects | Result |
|---|---|---|---|
| A1 row 1 | 217 | 1 (R1-1, ⛏ gated on `$`) | BC-SL-027 amended |
| A1 row 2 | 100 | 0 | — |
| A2 exporter | 270 | 1 (R2-1, `.encode()` at `:399`) | E-22; BC-EX-021 amended |
| A3 proxy | 211 | 1 mechanism with 4 consequences (R3-1) | new BC-PX-048; P-R5, P-S5, P-S6, P-E1; BC-PX-024/029 amended; CONV-ABS-21 |
| A4 hook | 105 | 0 | — |
| **Total** | **903** | **3** | |

---

## 2. New and amended BCs

### 2.1 BC-SL-027 (amended): ⛏ is a suffix of the `$` segment

**Amended contract.** `⛏` is rendered only inside the cost segment, which exists only when `cost.total_cost_usd` is a number and `> 0` (`:601-602`).
Then, on the DGX lane with `tin + tout > 0` (`:626-627`): basis not ok → `\e[90m ⛏n/a\e[0m`; basis ok → `\e[90m ⛏{eq:.2f}\e[0m` when
`eq >= 0.005`. The text is appended to `cseg` after `$` and the optional `$/h`, so there is never a separator before `⛏`. With no positive cost the
token segment can be the last row-1 segment on the DGX lane even when the basis is valid (§1.1 table). **Go contract:** build `$`, `$/h`, `⛏` as one
segment under one `usd > 0` guard. Table test: the five rows of §1.1. Citation: `:601-602,626-636`. Parity BX (unchanged).

### 2.2 E-22 and BC-EX-021 (amended)

Add to the exporter crash catalogue (P2r2 §5.2):

| ID | Phase | Trigger | Raising line | Persistence |
|---|---|---|---|---|
| **E-22** | exposition | a label value (`project`, `user`, `model_req`/`model`, `account`, `device`, or the first 8 characters of `session`) that is a str containing a lone surrogate (from a JSON `\udcXX`/`\ud8XX` escape, which is what the proxy writes for non-UTF-8 header bytes) | `:399` `UnicodeEncodeError` | permanent while the line is in the ledger; the process stays up (startup `rebuild()` does not render) |

BC-EX-021 ("crash process contract: zero bytes, permanent") gains E-22 as an exposition-phase trigger with the "process stays up" variant. Go
diverges (U+FFFD substitution, pinned); parity treatment follows **OD-11**. If OD-11 is ruled "reproduce", Go must fail the scrape for any label
value that came from a lone-surrogate escape, which requires decoding the ledger with a surrogate-preserving JSON reader; if ruled "approved
deviation" (the recommendation in P2r5), Go's U+FFFD behavior stands and the harness classifies such ledgers as "E-class".

### 2.3 BC-PX-048 (new): `note()` can raise, and the hook that called it stops

**Source:** `dgx_proxy.py:65-74` (guards), call sites `:108,135,140,167,240,286,297,309,321,510,518`; mitmproxy 12.3.1 `http:40-41` (header
decoding), `http:427-441` (`get_text(strict=False)` fallback).

**Contract (legacy).**

1. `note(msg, *args)` swallows `%`-format errors and `OSError` on the write. It does **not** swallow `UnicodeEncodeError`: a formatted message
   holding a lone surrogate raises out of `note()` under both locale modes (pinned).
2. The calling hook stops at that call. Writes made before the call stay; writes after it are lost. Consequences: **P-E1** (no
   `*_upstream_error` line), **P-S5** (no failed-request capture), **P-S6** (no `anth_reply`/`anth_usage`), **P-R5** (request hook aborts inside
   normalization: original body to Anthropic, no request line; `_logged_unknown` makes it a first-occurrence-only failure per proxy generation).
3. Surrogates enter through (a) request or response header values with non-UTF-8 bytes, decoded `utf-8` + `surrogateescape`; (b) response bodies
   decoded with `get_text(strict=False)` that fail UTF-8; (c) JSON `\udcXX`/`\ud8XX` escapes in a request body.
4. `ledger()` is unaffected: `json.dumps` escapes the surrogate as ASCII `\udcXX`, so the ledger line itself is written whenever the hook reaches it.

**Go contract (P3).**

- **Ledger bytes (BX, no OD):** a header value whose bytes are not valid UTF-8 must appear in the ledger as legacy writes it: each undecodable byte
  `0xXY` (≥ 0x80) as the escape `\udcXY`, valid sequences as `ensure_ascii` escapes. Go's `json.Marshal` would instead coerce invalid bytes to U+FFFD
  and write raw UTF-8, so the Go writer needs its own surrogateescape-aware ASCII encoder (it needs an `ensure_ascii` encoder anyway, BC-PX-028).
- **Hook abort (OD-45, new):** *Recommend:* an approved failure-mode deviation. In Go, a decision-log write never aborts routing or ledger
  writes: P-E1, P-S5 and P-S6 events are written, and P-R5 routes on the first occurrence. The replay classifies inputs that trigger P-E1/P-S5/P-S6/P-R5
  as "legacy note-abort" and compares Go against the deviation, not against legacy. *Alternative:* reproduce (order every decision-log write before
  the ledger write it precedes in legacy, and fail the same way). Event names unchanged (D7).

Index row: `BC-PX-048 | note() raises on unencodable text; the calling hook stops (P-E1, P-S5, P-S6, P-R5) | internal/proxy | P3 | OD-45 | OD-11 (E-22 shares the vector), OD-28 | H | r6 | new r6`.

**Amended:** BC-PX-024 (the `error` hook writes its event only if the note at `:321` succeeds; P-E1); BC-PX-029 (OOS stays for the **text**, but the
raise is an in-scope effect, now owned by BC-PX-048).

**CONV-ABS-21 (retraction, P2r3 §1.2 `get_text` table, row "Undecodable text, `strict=False`"):** the claim "response-side notes may contain lone
surrogates. **Harmless, since the decision log is opened in the default locale encoding**" is wrong. The default locale encoding is UTF-8 with strict
errors, so writing a lone surrogate raises, and `note()` does not catch it (pinned, P-S5). Ground truth: BC-PX-048. Related narrowing (not a
retraction): P2r3 §1.3's "Not reachable with Claude Code's UUIDs" holds for the session header, but the project header is the directory basename
(`claude-dgx:44`), so non-UTF-8 header bytes are reachable if Claude Code sends Latin-1 bytes (LOW, owner check 3).

---

## 3. Target B: citation corrections

| # | BC / place | Cited | Source today | Correction |
|---|---|---|---|---|
| COR-1 | **BC-SL-007**, P3r5 §5.1 and §6 | r5 moved the cite to `:440,450` ("`model_name` at `:440`, used at `:450`") | `:440` is `def render_lane(…)`, `:450` is blank; `model_name` is assigned at **`:442`** and used at **`:453`** (`sl_pick.py` asserts both lines) | **Restore the broad sweep's `:442,453`** (and r1's `:441-443,453`, which is also correct). The broad and r1 cites never drifted; r5's sample misread them. Retract r5's index flag "cited lines now :440,450" |
| COR-2 | BC-SL-027 | `:626-635` | `:626-636` plus the enclosing guard `:601-602` | cite `:601-602,626-636` (amendment §2.1) |

Every other citation met in the four regions was checked against the current source and is exact: BC-SL-006, 008, 010-029, 043-053, 056, 077 (all
step lines), 085; CP-S01..S17 lines; r1 §A0 clock lines (`:304`, `:322`, `:408`, `:499`, `:558`, `:231`, `:243`, `:825-826`); BC-EX-001..017,
E-01..E-21 lines, P3r5's `:281-287`; BC-PX-001..031 lines, P3r4's `:316-319`, `:242-245`, `:184-188`, P3r5's decision-line list; BC-HK-001..022
lines; P3r5 §2.3's `:911`, `claude-dgx:15-22,75,85-97,101-104`.

---

## 4. Target C: BC-EX-027 and BC-PX-046 re-checked

### 4.1 BC-EX-027: CONFIRMED, with one refinement

Re-read `:281-287` and `:64-68`; new fixtures in `ex_surrogate.py` (`anth_request` events, a `colon-fake` hook line), identical output on 3.11.7 and
3.9.6:

| Case | Result | Verdict |
|---|---|---|
| A: second line appended after rebuild's EOF, before `:287` | scrape 1 and scrape 2 both `…{model="claude-opus-5",…} 1`; file holds 2 lines | confirmed (contract 2) |
| D: hook log gains a `[colon-fake]` line, ledger unchanged | `colon_caught 0` | confirmed (contract 1) |
| **E (new): ledger replaced by different content of the same byte length** | still `claude-opus-5 1` although the file now says `claude-haik-5` | **refinement:** the trigger is "size ≠ `processed_size`"; a same-size rewrite or rotation is never noticed |
| Recovery: one-byte append | full rescan: `claude-haik-5 2`, `colon_caught 1` | confirmed (contract 3) |
| F: ledger renamed away | last state kept, status 200 | confirmed (contract 3, "freezes") |

BC-EX-027 stands; add contract item 4: "a same-size replacement is indistinguishable from no change". OD-39's recommendation (Go tracks the consumed
offset and watches both files by size **or mtime**) already covers it.

### 4.2 BC-PX-046: CONFIRMED, two rows upgraded by pass-2 r7

Re-read: mitmproxy 12.3.1 `options:241-246` (`tcp_timeout`, int, 600, "Connections will be closed after this period of inactivity"),
`proxy/server:344-354` (`on_timeout` logs `Closing connection due to inactivity` and cancels the handler), `proxy/server:286-310` (a cancelled read
loop still awaits `server_event(ConnectionClosed)`), `tools/main:120-135` (handlers for SIGINT and SIGTERM only); `claude-dgx:75,97,104`. All as
r5 states.

| Row | r5 | Now |
|---|---|---|
| 1 Inactivity cut (600 s) | MEDIUM static, not observed | unchanged (P2r7 §0: not observed in the retained ledger) |
| 2 SIGTERM/SIGINT with flows in flight | MEDIUM ("asyncio.run cancel step not source-read") | **HIGH (static, every link read)**: P2r7 §2 reads the CPython 3.12.10 `asyncio.run` → `Runner.close` → `_cancel_all_tasks` chain; the error-hook task is created after the cancel snapshot and runs before the loop closes. **V-3 is answered statically**; a rig run is optional confirmation. Add the error text **`connection cancelled`** for a flow cancelled while its upstream connect is pending (P2r7 T-5, mitmproxy 12.3.1 `proxy/server:223-227`) |
| 3 SIGHUP / SIGKILL | MEDIUM static | unchanged |

Contract (1) gains a note: the in-flight ceiling is separate from the upstream **connect** wait, which legacy does not bound at all (P2r7 T-4,
OD-42; see BC-PX-047).

---

## 5. Target D: pass-2 r7 folded in

| P2r7 item | Pass-3 effect |
|---|---|
| T-1 upstream verification (certifi only, SAN hostname check, failure texts, lane asymmetry under eager), T-2 TLS 1.2 floor and cipher list, T-4 no connect timeout, T-5 `connection cancelled` | **BC-PX-047 (new, carried)**, below |
| P-1 upstream leg mirrors the client's ALPN, HY-PROTO-1 — **as corrected by P2r8 CONV-ABS-25** | P2r7 derived "h1 on both legs in production" from the wrong 0-line count. Corrected: **Claude Code's** flows are h1 on the client leg (P2r8 attribution), so by mirroring they are h1 upstream too; but **h2 flows do occur in production** (15,131 `HTTP/2.0` lines) from CA-trusting child tools. Effects: **BC-PX-043** — the h1 Host-header contract covers Claude Code; an h2 client's rerouted request carries `:authority` instead, so V-1 must include one h2 case. **BC-PX-044** — consequence 2 is retracted as "observed" (it rested on P3r4 §0's count); it holds for Claude Code only (P2r8 attribution, MEDIUM), and the **HTTP/2 rows** of the error-cause table (P2r4 §1.3) are production-relevant for non-Claude-Code clients. **BC-LN-004 / D14** — the two rerouted h2 `/v1/messages` requests are live evidence of D14 harm (legacy exports `HTTPS_PROXY`/`NODE_EXTRA_CA_CERTS` to the children); D14 already rules the hylo side. OD-17 note: HY-PROTO-1 (mirror the client's version) still holds and now matters on both protocol versions |
| §2 asyncio.run link HIGH | BC-PX-046 row 2 upgraded (§4.2); V-3 answered statically |
| W-1 / F-3 unbounded WebSocket message retention in mitmproxy — **channel corrected by P2r8 CONV-ABS-26** | BC-PX-027 flag only: the addon's WebSocket hooks stay dead; retention is mitmproxy's (`websocket` True applies to any host), so it hits the real Remote Control WebSocket on `api.anthropic.com/api/frame/sync`, not a bridge host; not a ledger or parity surface (HY-WS-1, D16). **BC-PX-001 / BC-PX-026:** contracts unchanged as code behavior, but they **never fire in production** (no `bridge.claudeusercontent.com` traffic; OD-43). The `/api/frame/sync` and `/v1/code/sessions/…` flows fail the `/v1/messages` prefix test (`:103`), so the addon leaves them untouched except `responseheaders`' `anth_ratelimit` capture for any `api.anthropic.com` response (BC-PX-013) and, for SSE responses, the tap (BC-PX-014); HY-PASS-1 governs their duration in hylo |
| T-3 `SSLKEYLOGFILE` / `MITMPROXY_SSLKEYLOGFILE` inherited by the per-window mitmdump | BC-LN-004 flag (the launcher passes its whole environment, `claude-dgx:75`); hylo default HY-TLS-3 |
| Defaults re-confirmed: `body_size_limit` None, `stream_large_bodies` None, `store_streamed_bodies` False, `validate_inbound_headers` True, `connection_strategy` eager, `listen_host` "" | BC-PX-037 confirmed as written; no body-size or keep-alive option changes any BC (no keep-alive option exists; HTTP/1.1 persistence is mitmproxy's default) |
| OD-41 (TLS policy), OD-42 (connect timeout) | adopted as numbered; this round's item is OD-45 |

### 5.1 BC-PX-047 (new; carried from P2r7 §1.3 T-1/T-2, §1.4 T-4/T-5): upstream connection policy

| Facet | Legacy behavior (mitmproxy 12.3.1 defaults, no override) | Ledger / client effect |
|---|---|---|
| Verification | always on: chain against **certifi's bundle only** (OS store, keychains and `SSL_CERT_FILE` ignored) plus hostname check (SAN only) | a TLS-inspection network fails every **Anthropic-lane** request with `Certificate verify failed: <reason>` → `anthropic_upstream_error` **with** attribution; an `https` backend with a private CA fails every routed request → `dgx_upstream_error` |
| Lane asymmetry under eager CONNECT | a failed TLS handshake to `api.anthropic.com` does not kill the tunnel; Anthropic-lane flows on it fail at once, DGX-lane flows open their own backend connection and succeed | per-flow events as above |
| Versions and ciphers | TLS ≥ 1.2, legacy cipher list (incl. 3DES) | unobservable against Anthropic (TLS 1.3) and the plain-HTTP backend |
| Connect timeout | none: refused/unreachable fail at once; a silent host waits for the OS TCP connect timeout | the client waits; the error text then follows BC-PX-044 |
| Connect cancelled (SIGTERM) | `connection cancelled` | `*_upstream_error` with that text |

Go contract (P3): HY-TLS-1 (verification always on), trust anchor per **OD-41**, connect timeout per **OD-42**, texts per **OD-28**, event names
unchanged (D7). Index row: `BC-PX-047 | Upstream TLS verification, lane asymmetry, no connect timeout | internal/proxy | P3 | OD-41 | OD-42, OD-28 | M | r6 | new r6, carried from P2r7`.

---

## 6. Index delta (apply to P3r4 §7.3 as amended by P3r5 §6)

| ID | Change |
|---|---|
| BC-SL-007 | **COR-1:** cite back to `:442,453`; drop r5's flag (Last unchanged, r1) |
| BC-SL-027 | Last → r6; flag "⛏ inside the `$` segment: needs total_cost_usd > 0 (§2.1)"; cite `:601-602,626-636` |
| BC-EX-001 | flag "startup line block-buffered under launchd (log only)" (Last unchanged) |
| BC-EX-021 | Last → r6; flag "E-22 exposition trigger (lone surrogate label; process stays up)" |
| BC-EX-027 | Last → r6; flag "same-size replacement never noticed (contract 4)" |
| BC-PX-024 | Last → r6; flag "event lost if the `:321` note raises (P-E1, BC-PX-048)" |
| BC-PX-001 | flag "never fires in production: Remote Control is not on the bridge host (P2r8 CONV-ABS-26, OD-43)" (Last unchanged) |
| BC-PX-026 | flag "never fires in production (P2r8 CONV-ABS-26, OD-43)" (Last unchanged) |
| BC-PX-027 | flag "mitmproxy retains WS messages of the real Remote Control socket `api.anthropic.com/api/frame/sync` (P2r7 F-3, P2r8); not a ledger surface" (Last unchanged) |
| BC-PX-029 | Last → r6; flag "raise on unencodable text is in scope via BC-PX-048; text stays OOS" |
| BC-PX-043 | Last → r6; flag "h1 Host form covers Claude Code (h1 both legs by mirroring); h2 clients exist in production (P2r8 CONV-ABS-25): V-1 needs an h2 case" |
| BC-PX-044 | Last → r6; Also += OD-41, OD-42; flags "TLS-failure texts and connect behavior in BC-PX-047"; "consequence 2 no longer 'observed' (P3r4 §0 count retracted, CONV-ABS-25): h1 holds for Claude Code only; HTTP/2 rows are production-relevant for other clients" |
| BC-PX-046 | Last → r6; Conf M → H for row 2 (row 1 and row 3 stay M); flag "V-3 answered statically; `connection cancelled`" |
| BC-PX-047 | **new** (§5.1) |
| BC-PX-048 | **new** (§2.3) |
| BC-LN-004 | flag "inherits SSLKEYLOGFILE (P2r7 T-3; HY-TLS-3)"; "D14 harm observed: 2 `/v1/messages` from a non-Claude-Code h2 child rerouted to the DGX (P2r8)" (Last unchanged) |

**Totals after this round: 231 BCs.**

| Component | BCs | BX | JE | OOS | Approved deviation | Pending OD (primary) |
|---|---|---|---|---|---|---|
| Status line (SL) | 103 | 97 | 0 | 0 | 4 | 2 |
| Proxy (PX) | 48 | 37 | 0 | 3 | 1 | 7 (+OD-41, +OD-45) |
| Exporter (EX) | 27 | 0 | 16 | 1 | 0 | 10 |
| Stop hook (HK) | 23 | 3 | 18 | 0 | 0 | 2 |
| Launcher (LN) | 11 | 0 | 8 | 2 | 1 | 0 |
| Coordinator (CO) | 2 | 0 | 0 | 2 | 0 | 0 |
| Preflight (PF) | 2 | 0 | 2 | 0 | 0 | 0 |
| Backfill (BF) | 13 | 0 | 0 | 0 | 0 | 13 |
| Services (SV) | 2 | 0 | 0 | 2 | 0 | 0 |
| **Total** | **231** | **137** | **44** | **10** | **6** | **34** |

By phase: P1 103, P2 29, P3 47, P4 39, unscheduled 13. By last round: B 79, r1 85, r2 24, r3 19, r4 11, r5 3, r6 10.

Crash catalogues: exporter E-* += **E-22** (OD-11); proxy += **P-R5, P-S5, P-S6, P-E1** (OD-45). Status line, hook and backfill catalogues unchanged.

Owner items: **OD-01..OD-43 and OD-45** (44 items; OD-43 is pass-2 r8's bridge item; OD-44 reserved for pass-2 r9). Ruled: OD-24, OD-27. Pending: 42. New this round: **OD-45** (Go behavior when a
decision-log write fails: recommend that it never aborts routing or ledger writes).

RET crosswalk (P3r4 §6, P3r5 §6): add **RET-14 = CONV-ABS-21** (P2r3 §1.2 "undecodable response text in notes is harmless" → `note()` raises and
aborts the hook; BC-PX-048). Numbers 22-24 unused; 25+ belong to pass 2 (P2r8 issued CONV-ABS-25, the HTTP/2 count, and CONV-ABS-26, the bridge host; both are applied in §5-§6
above). P3r4 §0's "0 ` HTTP/2.0` lines" row is superseded by CONV-ABS-25.

---

## Owner checks (after the soak; not attempted)

1. Carried: the Grafana per-session panel with at least 2 recent sessions (BC-EX-025); optionally `promtool check metrics` offline on one saved
   scrape body.
2. Carried: the VictoriaMetrics NaN capture (one `/api/v1/query` response for the exact `QUERY` on an idle box, under light load, and with fewer than
   20 TTFT samples).
3. **New (read-only, local, one command, no networking):** count ledger lines containing the escape `\udc` (lone surrogate from non-UTF-8 header
   bytes), and list whether any `claude-dgx` project directory basename is non-ASCII. Zero lines means E-22 and P-E1 have not occurred; any line
   means the exporter has been failing every scrape since that line and the project's upstream errors are missing (BC-PX-048).

## Delta Summary

- **Target A (line by line):** 903 statements re-read in five regions (row 1 217, row 2 100, exporter 270, proxy 211, hook 105). **Three unstated
  effects**, one per region in A1-row-1, A2 and A3; none in row 2 or the hook:
  - R1-1: ⛏ is nested in the `$` segment, so it needs `total_cost_usd > 0` → **BC-SL-027 amended** (pinned, 5 rows).
  - R2-1: a lone surrogate in a label makes `.encode()` at `:399` raise on every scrape, process up, no response → **E-22**, BC-EX-021 amended
    (pinned on 3.11.7 and 3.9.6; Go substitutes U+FFFD, pinned with go1.26.5; OD-11).
  - R3-1: `note()` raises `UnicodeEncodeError` (not caught) and aborts the calling hook → **BC-PX-048** with **P-E1** (upstream-error event lost),
    **P-S5** (failed-request capture lost), **P-S6** (Anthropic reply events lost, static), **P-R5** (first-occurrence fail-open to Anthropic); pinned
    under both locale modes. **CONV-ABS-21** retracts P2r3's "harmless" claim. New **OD-45**. A shared, partly reachable vector: the project header
    is `basename "$PWD"` (LOW whether Claude Code sends Latin-1 bytes; owner check 3).
- **Target B:** COR-1 restores BC-SL-007's original `:442,453` (r5's `:440,450` was the drift, not the fix); COR-2 widens BC-SL-027's cite. All other
  citations in the four regions are exact.
- **Target C:** BC-EX-027 confirmed with new fixtures on both interpreters, plus contract item 4 (same-size replacement never noticed). BC-PX-046
  confirmed; row 2 upgraded to HIGH via P2r7 §2; `connection cancelled` added.
- **Target D:** P2r7 folded in: **BC-PX-047** (upstream TLS and connect policy, carried); BC-PX-037 re-confirmed. With the orchestrator's correction
  (P2r8 CONV-ABS-25/26): BC-PX-043/044 now say h1 for Claude Code only, with h2 clients present in production; BC-PX-001/026 never fire in
  production; BC-PX-027 and BC-LN-004 flags (real Remote Control socket; observed D14 harm). No P2r7 default changes a body-size, keep-alive or buffering BC.
- **Counts:** new BCs 2 (BC-PX-048 found here; BC-PX-047 carried). Amended or re-dated 8 (BC-SL-027, BC-EX-021, BC-EX-027, BC-PX-024, BC-PX-029,
  BC-PX-043, BC-PX-044, BC-PX-046). Flag-only 6 (BC-SL-007 cite, BC-EX-001, BC-PX-001, BC-PX-026, BC-PX-027, BC-LN-004). Index 231. Crash rows +5. Retraction 1. OD +1.

## Remaining Gaps (verbatim-carryable)

1. Owner checks after the soak (not attempted): the Grafana per-session panel with at least 2 sessions; optionally `promtool check metrics` offline on
   a saved scrape; the VictoriaMetrics NaN capture; **new:** the read-only ledger count of `\udc` escapes and the non-ASCII project-basename check
   (decides whether E-22/P-E1 have happened in production).
2. P3 replay verification items, stub-backend rig only: V-1 (Host header bytes), V-2 (mitmproxy 502 page bytes on connect failure and `server closed
   connection`); V-3 answered statically (rig confirmation optional). **New:** a rig case per BC-PX-048 row (project header with a raw byte 0xE9 on a
   failing backend: expect no `dgx_upstream_error` from legacy) to confirm P-E1 end to end through mitmproxy.
3. Owner decisions: 42 pending (OD-01..OD-23, OD-25, OD-26, OD-28..OD-43, OD-45), including the new OD-45 (OD-44 reserved for pass-2 r9).
4. Not verifiable from authorized sources (LOW): how Claude Code encodes non-ASCII values of `ANTHROPIC_CUSTOM_HEADERS` (UTF-8 vs Latin-1 bytes);
   whether Claude Code can report `total_cost_usd` ≤ 0 while the transcript holds tokens (R1-1 reachability); which duplicate session sample
   VictoriaMetrics keeps (BC-EX-025); whether vLLM streams a byte before the first token (BC-PX-046 row 1).
5. Suggested scope for round 7: re-verify BC-PX-048 / E-22 / BC-SL-027 with new fixtures; apply the same statement-by-statement reading to the
   regions that rounds 5 and 6 have not read statement by statement: the `_mix_counts` loop `dgx_statusline.py:999-1154`, `get_sample`/`fetch_sample`/
   `effective_rl`/`claude_window_start` `:158-362`, `render_subagent_rows`/`main_subagent` `:888-975`, `tools/backfill_cost_history.py` in full, and the
   proxy's `_SSETap`/`cache_fields`/`extract_stop_reason` `:339-456` (r4 proved properties of the tap; this reading checks for unstated effects).

## Novelty Assessment

Novelty: SUBSTANTIVE

Most of the round is confirmation: 903 statements read, two of the five regions clean, every citation in the regions exact except BC-SL-007 (where
the fix is to undo r5's change), BC-EX-027 and BC-PX-046 confirmed, and the pass-2 r7 fold-in, which this pass counts as refinement even though it
adds the carried BC-PX-047.

Three findings fail the orchestrator's test ("an effect not stated by any BC is SUBSTANTIVE"), and each changes what a Go implementer would build:

- **BC-PX-048 (largest):** the decision log is not the inert, out-of-scope side channel the index treats it as. A write failure there removes ledger
  events (P-E1, P-S6), the failed-request capture (P-S5), or routes a Sonnet request to Anthropic (P-R5). It forces a retraction of a pass-2 claim
  (CONV-ABS-21), a Go ledger-escaping rule for non-UTF-8 header bytes, and an owner decision (OD-45).
- **E-22:** a new permanent exporter outage class that, unlike E-01..E-09, keeps the process up, and where Go's JSON decoder silently differs.
- **BC-SL-027:** the BC as worded predicts a ⛏ segment that legacy never prints when there is no positive cost.

The E-22 and P-E1 findings share one possibly reachable input (a non-ASCII project directory sent as Latin-1 header bytes), which is why owner
check 3 was added. Without these findings a Go port could pass every recorded-input diff and still miss them, because no recorded input exercises
them; that is the "citation is not coverage" lesson again.

## Convergence Declaration

Another round needed: three unstated effects were found inside cited regions (BC-SL-027, E-22, BC-PX-048). Round 7 should re-verify them with new
fixtures and run the same statement-by-statement reading over the regions listed in gap 5.

## State Checkpoint

```yaml
pass: 3
round: 6
status: complete
files_scanned: dgx_statusline.py (:140-262, :399-835, :849-873, :1157-1235 statement by statement), dgx_ledger_exporter.py (all, statement by statement), dgx_proxy.py (:56-323, :467-515 statement by statement; :1-549 exec'd as a text copy), auto_continue.py (all, statement by statement), claude-dgx (:15-22, :41-54, :75, :85-104), deploy/io.hylo.ledger-exporter.plist; pass-3 B, r1-r5; pass-2 r2-r5, r7; mitmproxy 12.3.1 http, proxy/layers/http/__init__, options, proxy/server, tools/main (citations only)
statements_reread: {sl_row1: 217, sl_row2: 100, exporter: 270, proxy: 211, hook: 105, total: 903}
unstated_effects: 3 (R1-1 -> BC-SL-027 amended; R2-1 -> E-22 / BC-EX-021; R3-1 -> BC-PX-048 + P-R5/P-S5/P-S6/P-E1)
timestamp: 2026-11-14T07:35:44Z
novelty: SUBSTANTIVE
new_bcs: {PX: 2 (BC-PX-047 carried from P2r7, BC-PX-048 found here)}
amended_bcs: [BC-SL-027, BC-EX-021, BC-EX-027, BC-PX-024, BC-PX-029, BC-PX-043, BC-PX-044, BC-PX-046]
flag_only: [BC-SL-007 (COR-1 cite restored to :442,453), BC-EX-001, BC-PX-001, BC-PX-026, BC-PX-027, BC-LN-004]
crash_rows_added: [E-22, P-R5, P-S5, P-S6, P-E1]
retractions: [CONV-ABS-21 (P2r3 §1.2 'harmless' note claim)]
corrections: [COR-1 BC-SL-007, COR-2 BC-SL-027]
recheck: {BC-EX-027: confirmed + contract 4 (same-size replacement), BC-PX-046: confirmed, row 2 -> HIGH}
bc_index_total: 231
owner_decisions: 44 (OD-01..OD-43, OD-45; 42 pending, 2 ruled; OD-44 reserved for pass-2 r9)
orchestrator_correction_applied: {CONV-ABS-25: HTTP/2 lines 15131 (child tools, not Claude Code) -> BC-PX-043/044, BC-LN-004 flags; CONV-ABS-26: no bridge host -> BC-PX-001/026/027 flags}
new_owner_items: [OD-45]
scratch_evidence: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/p3r6/
next: pass 3 round 7 (carry "Remaining Gaps" verbatim)
```
