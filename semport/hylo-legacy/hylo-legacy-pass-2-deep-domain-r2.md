# Pass 2 Deepening — Round 2: Domain Model (proxy, exporter, hook, launcher, backfill) — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Read in full this round: `dgx_proxy.py` (764), `dgx_ledger_exporter.py` (414),
  `auto_continue.py` (275), `claude-dgx` (185), `tools/backfill_cost_history.py` (121), `dgx_preflight.py` (41), `dgx-proxy-coordinator.sh` (50),
  `deploy/*.plist`. Re-read for the round-1 audit: `dgx_statusline.py:70-125,160-360,396-470,564-610,862-880,970-1245`.
- Inputs read: every file in this directory, including round 1 (`…-pass-2-deep-domain.md`) and the pass-3 round-1 file
  (`…-pass-3-deep-behavioral-contracts.md`, read only; not edited), plus `.factory/specs/research/domain-hybrid-routing-claude-code-2026-11-14.md` §3.
- Method: static reading. Scratch scripts in `scratchpad/p2r2/` copy expressions only. No legacy module was imported or run, and nothing networked was run.
  Interpreters used: `/opt/homebrew/anaconda3/bin/python3.11` (3.11.7) and `/Library/Developer/CommandLineTools/usr/bin/python3` (3.9.6), always with `-I`.
  Results marked **[scratch-verified]** come from these runs.
- Line numbers are those of the named file. A bare `:N` means the file of that section.
- To avoid duplication, this round adds only what passes 1-3 (broad and deep) do not already state. Where a fact is already in pass 3 (BC-*), it is cited, not repeated.

---

## 0. Audit of round 1 (riskiest claims + 5 hallucination classes) and retractions

| Marker | Round-1 claim | Ground truth | Evidence |
|---|---|---|---|
| Confirmed, refined | **"31 crash paths"** (§5, Delta) | The 31 is a count of **catalogue IDs**, and several IDs bundle several triggers (CP-31, CP-32, CP-34). Pass-3 round 1 counts **40** for the same ground (CP-S/T/N/C/X). The two catalogues **agree** on every trigger; they differ only in granularity: round-1 CP-30..34 (5 IDs) = pass-3 CP-C01..C10, and round-1 CP-13a/b = CP-S14/S15. Round 1 **missed two outside-guard paths**: CP-X03 (the guard's own `print` fails, e.g. EPIPE after a cancelled run → exit 1, `:1244`) and CP-X04 (signals: KeyboardInterrupt traceback / SIGTERM kill). **Use pass-3's numbering as canonical**. Round-1 IDs map 1:1 (table §0.1) | `dgx_statusline.py:1238-1245`; pass-3 §B |
| **CONV-ABS-5** | CP-25: "`output_tokens` non-numeric truthy **on a message's first line** → crash when that turn is finished (`:994`)" | **Retracted as an independent trigger.** On a message's first line the turn machine (`:1069-1079`) runs **before** the usage step (`:1096-1112`). If that line's usage is counted (id not yet seen), `tout += "abc"` raises at `:1112` first (that is CP-22 / CP-T04). The `:994` crash is independently reachable **only when that line's usage is deduplicated**, i.e. a message id seen earlier reappears after another id intervened. This is pass-3 CP-T05's precise condition. Round 1's wording over-extrapolated (class 1) | `dgx_statusline.py:1073-1079,1099-1112,993-994` |
| Confirmed | **7 permanent (sticky) transcript crash paths** (CP-20..26 = CP-T01..T07) | Holds. Every raise in the loop `:1059-1149` happens before `save_cache(mcache, …)` at `:1150`, so the next refresh reloads the old `size` and reparses the same bytes. Refinements: (a) sticky **once the bad line enters the 512 KB read window** (`:1044`). Earlier good lines in the window are not committed either, so the whole window is re-read every refresh. (b) The mix cache is keyed by session id, so the crash also survives a Claude Code restart with `--resume` (same sid, same transcript). (c) It clears only when the transcript shrinks (`size < off` → reset, `:1035`) or the mix cache file is deleted | `:1017-1019,1035,1044,1059-1150` |
| Confirmed, extended | **`NaN`/`Infinity` tokens in caches** | `save_cache` calls `json.dump(data, fh)` with the default `allow_nan=True` (`:203`). VM samples are stored verbatim (`:349`). Extensions: the **mix cache** also persists `NaN`/`Infinity` when a transcript usage value is a JSON `NaN`/`Infinity` literal (`tin += …`, `:1108-1112`; rendering does not crash: `_fmt_tok_c(nan)` → `"nan"`, `:863-873`). **cost-history** can hold `Infinity` when stdin `total_cost_usd` is `Infinity`, because `round(inf,4)` returns inf (pass-3 BC-SL-028). Go's readers and writers for **all four** cache files need the tokens | `:203,349,1108-1112`; `:234` |
| Confirmed, refined | **Cache write order** (6 steps, round 1 §3.6) | Holds: `:1213` mix → `:1216` rl → `:1218` sample → `:1229` proc_start → `:455` git → `:606` cost. Refinements: (a) row 2 is **rendered between steps 3 and 4** (`:1226-1227`), so a CP-N01/N02 crash leaves steps 1-3 only. (b) Steps 2, 3 and 4 each **re-load** `statusline-<sid>.json` and write the whole file again (`:306-308`, `:323,327,351/355`, `:273,287-288`): three separate atomic writes per refresh. (c) Each step is conditional: rl iff stdin `rate_limits` is a non-empty dict; sample iff `ROWS ≥ 2` and the TTL expired; proc_start iff `session_id` is truthy, there is no cached `proc_start`, and the `ps` walk succeeds; git iff `proj_dir` is truthy, `GIT_ON`, and the TTL expired or `branch` is missing; cost iff `usd > 0`, the lane is known, and not throttled | `:298-360,265-295,399-413,224-237,1200-1234` |
| Confirmed, refined | 40 env inputs (round 1 §6.1) | Recount with the shell (`grep os.environ` over `*.py`, `$VAR` over `claude-dgx`, minus 14 launcher-internal shell variables): **42**. The two extra are OS inputs that round 1 omitted while it listed `TMPDIR`: **`HOME`** (every `expanduser`, `claude-dgx:80,114`) and **`PWD`** (`claude-dgx:44`, the **project attribution label**). `PWD` is a domain input (project = basename of the launch dir), not config | `claude-dgx:44,80,114` |
| Superseded | Round 1 §1.3 hint "iTerm/Terminal.app often set `LC_CTYPE=UTF-8`" | Orchestrator evidence plus the source: the launcher sets **no** locale variable (no `LANG`/`LC_*`/`PYTHONUTF8`/`PYTHONIOENCODING` in `claude-dgx`, the coordinator or the plists; grep-verified). So the status line most likely runs **strict**. See §1 | `claude-dgx` (whole file) |
| Refinement | Round 1 §1.1 "literals over 4,300 digits raise `ValueError` → `{}` (Python ≥ 3.11)" | True for ≥ 3.11 only. On **3.9.6** a 5,000-digit literal parses (**[scratch-verified]**). The production interpreter version is a harness parameter (§1.4) | — |
| Refinement | Round 1 §6.1 bool rows (`DGX_STATUSLINE`, `DGX_SANDBOX`, `DGX_SAFE`, `DGX_REMOTE`, `DGX_SKIP_PREFLIGHT`, `DGX_INVISIBLE`, `DGX_PRINT_ARGS`) listed only "bool, default X" | The legacy grammar is a **string comparison**, and it differs per variable: `== "1"` enables for some, `!= "0"` for others. Example: `DGX_STATUSLINE=true` **disables** the status line. Exact table in §6.8 | `claude-dgx:60-182` |

Class audit summary: no phantom entities (class 3/4). One over-extrapolation (CONV-ABS-5). Two metric recounts (crash IDs 31 vs 40: granularity, reconciled; env 40 → 42). No new retractions of pass 0/1 claims.

### 0.1 Crash-ID crosswalk (round 1 → canonical pass-3 IDs)

| Round 1 | Pass 3 | Round 1 | Pass 3 |
|---|---|---|---|
| CP-01 / 02 / 03 / 04 / 05 | CP-S01 / S02 / S03 / S04 / S05 | CP-20 … 26 | CP-T01, T02, T04, T07, T03, T05 (see CONV-ABS-5), T06 |
| CP-06 / 07 / 08 / 09 / 10 | CP-S06 / S07 / S08 / S09 / S10 | CP-30 / 31 / 32 / 33 / 34 | CP-C01 / C02-C06 / C07 / C08 / C09-C10 |
| CP-11 / 12 | CP-S11 / S12+S13 | CP-40 / 41 | CP-N01 / N02 |
| CP-13a / 13b / 14 / 15 | CP-S14 / S15 / S16 / S17 | CP-90 | CP-X01 + X02 (and new X03, X04) |

---

## 1. Gap 1 — Status line process locale: probable **strict**, direct capture still pending

### 1.1 Evidence

| Fact | Source | Status |
|---|---|---|
| Launcher exports no `LANG`, `LC_ALL`, `LC_CTYPE`, `PYTHONUTF8`, `PYTHONIOENCODING` | grep of `claude-dgx`, `dgx-proxy-coordinator.sh`, `deploy/*.plist` | verified (static) |
| The owner's interactive shell has `LANG=en_US.UTF-8`, `LC_CTYPE` → `en_US.UTF-8`, `LC_ALL` unset | orchestrator note | reported, not a capture |
| Under `LANG=en_US.UTF-8` (no `LC_ALL`/`LC_CTYPE`), Python 3.11: `utf8_mode=0`, stdin/stdout `strict` | **[scratch-verified]** `env -i LANG=en_US.UTF-8 python3.11 -I` → `utf8_mode 0 UTF-8 strict strict` | verified |
| Whether Claude Code (Node) passes its own environment to the `statusLine` command unchanged | not in the repo | **UNVERIFIED** |

**Verdict: probable strict; direct capture still pending.**

### 1.2 Harness consequence for each outcome

| Outcome | Harness env for `legacy/dgx_statusline.py` | What Go must reproduce |
|---|---|---|
| **Strict** (probable) | `LANG=en_US.UTF-8`, `LC_ALL` and `LC_CTYPE` **unset**, `PYTHONUTF8` and `PYTHONIOENCODING` **unset**, and the interpreter version of §1.4 | Invalid UTF-8 anywhere in stdin → whole stdin treated as `{}` (row 1 `◨ ?`, `?`). Any lone surrogate in a rendered label (`\ud800`-`\udfff`, including `\udc80`-`\udcff`) → `statusline degraded` (CP-S17). Go's `encoding/json` replaces invalid UTF-8 with U+FFFD and never fails, so Go needs an explicit "invalid UTF-8 → `{}`" pre-check plus surrogate detection on output |
| **surrogateescape** (`LC_CTYPE=UTF-8`, `C.UTF-8`, `LC_ALL=C`, or `PYTHONUTF8=1`) | pin exactly the captured variables | Invalid UTF-8 bytes in stdin are carried through and re-emitted **raw**. JSON escapes `\udc80`-`\udcff` are emitted as raw bytes `0x80`-`0xff`. Other lone surrogates → degraded. Go must work on raw bytes: no `string` round trip through U+FFFD |
| Either | **never `LC_ALL=C`** unless the capture shows exactly that (CONV-ABS-3) | — |

### 1.3 Cheapest capture recipe (owner runs once, later; not run here)

Save as `captures/sl-env-probe.py` (git-ignored directory):

```python
import json, locale, os, sys
out = {
    "env": {k: os.environ.get(k) for k in ("LANG", "LC_ALL", "LC_CTYPE", "LC_MESSAGES", "PYTHONUTF8",
                                           "PYTHONIOENCODING", "PYTHONPATH", "COLUMNS", "TERM", "PATH")},
    "exe": sys.executable, "version": sys.version, "utf8_mode": sys.flags.utf8_mode,
    "stdin": [sys.stdin.encoding, sys.stdin.errors], "stdout": [sys.stdout.encoding, sys.stdout.errors],
    "preferred": locale.getpreferredencoding(False), "fs": sys.getfilesystemencoding(),
}
with open(os.path.expanduser("~/hylo-sl-env-probe.json"), "w") as f:
    json.dump(out, f, indent=1)
print("probe ok")
```

Run it **exactly as production launches the status line**, i.e. through the launcher, so it inherits the same env, from the same terminal app:
`DGX_STATUSLINE=0 claude-dgx --settings '{"statusLine":{"type":"command","command":"python3 /ABS/PATH/captures/sl-env-probe.py"}}'`
(`DGX_STATUSLINE=0` keeps the launcher's own `statusLine` out, `claude-dgx:175`. Whether Claude Code merges two `--settings` flags is itself unverified. If the probe line never appears, temporarily put the probe command in `~/.claude/settings.json` instead.) Read `~/hylo-sl-env-probe.json`, then delete the probe. The file holds `PATH`, which is private: do not commit it.

### 1.4 New co-determinant: interpreter **version** per component (harness parameter)

| Component | Interpreter as launched | Evidence | Version-sensitive semantics |
|---|---|---|---|
| Stop hook | `python3` from Claude Code's `PATH` | `claude-dgx:161` | **Must be ≥ 3.10**: `def kev_pdone(state: str, question: dict \| None = None)` (`auto_continue.py:94`) has no `from __future__ import annotations`. On 3.9.6 this raises `TypeError: unsupported operand type(s) for \|` **at import**, so every Stop would exit 1 (**[scratch-verified]**). The hook runs in production (comments `:233-235`), so production `python3` on that PATH is ≥ 3.10 |
| Status line | same `python3`, same PATH | `claude-dgx:176` | Hence also ≥ 3.10 (inference, not capture). Sensitive: `fromisoformat` grammar (pass-3 BC-SL-069, 3.11 accepts more), the 4,300-digit int limit (≥ 3.11), UTF-8 mode default from 3.15 (PEP 686) |
| Exporter | `/usr/bin/python3` = **3.9.6** (Command Line Tools) | `deploy/io.hylo.ledger-exporter.plist:6`; `--version` **[scratch-verified]** | Under launchd's empty env: `utf8_mode=1`, `open()` = UTF-8 **strict** (**[scratch-verified]** `env -i`). No int-digit limit |
| Proxy | `$HERE/.mitmenv/bin/python` (venv; version and mitmproxy version **not pinned** in the repo) | `claude-dgx:75` | `from __future__ import annotations` (`dgx_proxy.py:26`) |
| Backfill | `python3` (docstring) | backfill `:18` | 3.9 `fromisoformat` rejects 4-digit fractions (`…44.1234+00:00`), 3.11 accepts them (**[scratch-verified]**). Claude Code writes 3-digit ms, so both accept real transcripts |

Harness rule: pin **interpreter version + locale** per component. The §1.3 probe captures both for the status line and the hook (same PATH).

---

## 2. Gap 2 — Can VictoriaMetrics return `"NaN"`/`"+Inf"` for the queried series? (owner capture task)

Static analysis cannot settle it. The derived series (`dgx_kv:host_hit_share`, `dgx_ttft:p95_30m`, `dgx_cost:*`, `dgx_tokens:*`, `dgx_power:*`, `dgx_preempt:*`) come from **recording rules that are not in the repo** (pass 6 gaps), so we cannot tell statically which ones divide or take quantiles. The two inline sub-queries are `sum(rate(…[1m]))` and `sum(increase(…[30m]))` (`dgx_statusline.py:115-122`). Both yield `0`, not NaN, on an idle counter that still exists. Whether VictoriaMetrics drops NaN samples from instant-query responses or returns them is also not determinable here.

**Capture (owner, once, after the DGX soak is scored; not run here).**
- Query: the exact `QUERY` string `dgx_statusline.py:102-123`. Extract it verbatim with `python3 -c 'import ast,sys; …'` or copy it from the file, but do not import the module (import runs the env parsing).
- Request: `GET {VM}/api/v1/query?query=<urlencoded QUERY>` (same as `:165`), e.g. `curl -sG --data-urlencode "query=$Q" http://<vm>:8428/api/v1/query > captures/vm-idle-<date>.json`.
- When: (1) idle box (no DGX-lane traffic for > 30 min, so TTFT has no samples), (2) during light load, (3) with `dgx_ttft:p95_30m` backed by fewer than 20 samples.
- What to look for: any `value[1]` equal to `"NaN"`, `"+Inf"` or `"-Inf"`, and which `__name__` carries it. A `NaN` on `vllm:kv_cache_usage_perc` → CP-N01 reachable. A `NaN` on `dgx_sl:gen_rate1m`, `vllm:kv_cache_usage_perc` or `dgx_ttft:p95_30m` → CP-N02 reachable for that trace. Also record whether such series are **absent** instead (the absent case is already handled: key omitted).
- Hygiene: the response holds hostnames and job labels; keep it in `captures/` and scrub before any fixture use.

---

## 3. Gap 3 — Does `message_delta.usage` carry `input_tokens`? (documented vs needs capture)

| Statement | Status | Source |
|---|---|---|
| `message_delta.usage` counts are cumulative; a delta "may carry only `output_tokens`, or also `input_tokens`, cache counts and `server_tool_use`"; merge present fields, never treat absent as zero | **documented** (Anthropic streaming docs) | research doc §3.1 |
| `message_start` carries the initial usage under `message.usage` | **documented** | research doc §3.1 |
| The tap sets `(in, out)` **only** from an event whose **top-level** `usage` has the key `input_tokens`; no field merge | **code** | `dgx_proxy.py:418-420`; pass-3 BC-PX-017/033, CONTRA-2 |
| Anthropic `message_delta` repeats the cache **write** total (observed 2026-11-12) | in-code comment (live observation) | `dgx_proxy.py:373-376` |
| vLLM's Anthropic endpoint reports `input_tokens = prompt − cached − created` | in-code comment citing vLLM source | `dgx_proxy.py:261-266` |
| Whether real Anthropic and vLLM streams put `input_tokens` in **top-level** `message_delta.usage` | **needs capture** | — |

The docs therefore **permit** streams on which the legacy tap records nothing. So the parity question ("what does legacy do") is settled by code. The production question ("how often is `*_usage` missing") is not.

**Zero-new-capture check (owner, local, private data stays local).** For every tapped Anthropic response the proxy already writes a decision-log line `   anth tap: buf=<n> usage=<tuple|None> ct=<ctype>` (`dgx_proxy.py:239-241`).
1. Count `usage=None` vs all `anth tap:` lines in the routing decision log. Any `usage=None` on a `text/event-stream` reply is a stream with no top-level `input_tokens`.
2. Cross-check in the ledger: `anth_reply` events with `status: 200`, `path: "/v1/messages"` and **no** `in_tok` field (`jq 'select(.event=="anth_reply" and .status==200 and .path=="/v1/messages" and (has("in_tok")|not))'`). For the DGX lane: `dgx_reply` with `status: 200` and no `in_tok`.
Zero hits over a few days settles the production question for both lanes without capturing any stream. Non-zero hits → then capture one stream's event-type and usage-key skeleton only (strip all content).

---

## 4. Target 4 — Proxy-side domain model (P3)

### 4.1 Request body schema consumed (`POST /v1/messages*` on `api.anthropic.com`)

Gate: `host == "api.anthropic.com"` and `path.startswith("/v1/messages")` (`:103`). The body is read with `flow.request.get_text()` (mitmproxy decodes content-encoding and charset) → `json.loads` (`:105-106`).

| Path | Consumed as | Fallback | Mistyped → outcome | Line |
|---|---|---|---|---|
| (body) | JSON | `ValueError`/`TypeError` → note `unparseable /v1/messages body, passing through to anthropic`, no `_attrib` | non-object → silent passthrough, no `_attrib`, no note | `:105-111` |
| `model` | `str`, prefix test `model.startswith(prefixes)` (tuple, case-sensitive) | falsy → `""` → Anthropic lane | **truthy non-str → AttributeError escapes `request`** (P-R1) | `:112,132` |
| `metadata` | dict | non-dict → `{}` | — | `:116` |
| `metadata.user_id` | any JSON (CC: a string holding JSON `{device_id, account_uuid, session_id}`) | — | stored verbatim as `meta_user_id`; parsed later by `_account_hint` (proxy) and `_account_device` (exporter) | `:121` |
| `tools` | list (server-tool test; DGX normalization) | falsy → `[]`; normalization treats a non-list as `[]` | **truthy non-iterable (number/`true`) → TypeError in `uses_server_tool`** (P-R2). A string or dict iterates its chars or keys, so it never matches | `:461,475-477` |
| `tools[].type` | `str(type).startswith(("web_search_","web_fetch_","code_execution_"))` | missing → `""` | — | `:462` |
| `tools[].name` | normalization key (truthy hashable) | falsy → tool not in `by_name` | **unhashable name → TypeError** (P-R3) | `:478` |
| `tools[].input_schema` | presence only | absent → set to `{"type":"object","properties":{}}`, `changed` | — | `:482-485` |
| `messages[]` | iterable of dicts | falsy → `[]` | **truthy non-iterable, or non-dict element → TypeError/AttributeError** (P-R3) | `:486-487` |
| `messages[].content` | list → block filtering; non-list → skipped | — | — | `:487-489` |
| `content[].type` | kept iff in `{text,image,tool_use,tool_result,thinking,redacted_thinking}` or no type / non-dict block | — | — | `:49,492-494` |
| `content[]` `tool_addition` | name = `tool.definition.name` → `tool.name` → `block.name` → `block.tool_name`; definition = `tool.definition` (dict) | no name or empty definition → dropped, nothing added | unhashable name → TypeError (P-R3) | `:497-504` |
| `content[]` `tool_removal` | same name rule; `by_name.pop(name)` | — | unhashable → TypeError (P-R3) | `:505-506` |
| (whole body) | `req_bytes = len(get_text() or "")`: **characters** | — | — | `:123` |

Headers consumed: `X-DGX-Project`, `X-DGX-User`, `X-Claude-Code-Session-Id` (str or None, `:118-120`); `upgrade` (bridge only, `:100`).

### 4.2 Routing decision table, including one new case

| # | Condition (in order) | Lane / effect | Ledger |
|---|---|---|---|
| R0 | host `bridge.claudeusercontent.com` and `upgrade: websocket` | untouched | `bridge_ws_connect` |
| R1 | other host, or path not `/v1/messages*` | untouched | none |
| R2 | body unparseable or not an object | untouched (to Anthropic) | none (reply still logged as `anth_reply` with empty attribution) |
| R3 | `model` does not start with any prefix (empty prefix tuple → nothing matches) | Anthropic, `Accept-Encoding: identity` | `anth_request` lane `anthropic` |
| R4 | prefix match and a server-tool type | Anthropic, identity | `anth_request` lane `anthropic-server-tools` |
| R5 | prefix match, no server tool | **DGX**: path kept, scheme/host/port switched, body re-serialized iff changed | `dgx_request` |

**New: R5 applies to every `/v1/messages*` path, including `POST /v1/messages/count_tokens` with a local-prefix model.** That request goes to the DGX at the **same path** with the model rewritten (`:103,132,146-150,161-163`). Whether the backend serves `/v1/messages/count_tokens` is outside the repo. If it answers ≥ 400, the flow takes the error branch: `dgx_reply` with that status, which feeds `dgx_llm_request_errors_total`, plus a `failed-req-*.json` save (`:283-300`). Every such call also counts in `dgx_llm_requests_total` and `dgx_llm_est_prompt_tokens_total` (exporter `:184-193`). Whether Claude Code sends `count_tokens` for Sonnet models is **UNVERIFIED**. Owner check, local ledger: count `dgx_request` events with `path == "/v1/messages/count_tokens"`. (BC-PX-035/036 cover `batches` and Anthropic-lane `count_tokens` only.)

### 4.3 `normalize_for_dgx`: tool-set entity semantics (**[scratch-verified]**, function copied verbatim)

| Rule | Example result | Line |
|---|---|---|
| The tool list is **rebuilt only when `changed`**. Otherwise `tools` is left byte-identical, including nameless or non-dict entries | unchanged request keeps `[{A}, {nameless}, "junk"]` | `:513-514` |
| When rebuilt: **non-dict and nameless tools are dropped** (`order` holds `None` for nameless tools, and `None` is never in `by_name`) | `[A, nameless, "junk", B1, B2, C(no schema)]` → `[A, B2, C+schema]` | `:478-479,514` |
| **Duplicate names collapse** to the **last** definition, placed at the **first** occurrence's slot | `B1, B2` → `B2` at B1's position | `:478,514` |
| A request **without** `tools` that changes (e.g. a dropped `document` block) gains `"tools": []` | `{"messages":[…document…]}` → content `[(tools updated)]`, `"tools": []` | `:476-477,514` |
| `tool_removal` then `tool_addition` of the same name brings the tool back at its **original** slot with the new definition | `[A,B]`, remove A, add A' → `[A', B]` | `:502-506,514` |
| A dropped non-tool block (`document`, `search_result`, `server_tool_use`, `web_search_tool_result`, `container_upload`, … — anything outside the six-type set) **silently removes that content** from the DGX-lane request. If a message empties, it becomes `[{"type":"text","text":"(tools updated)"}]` (the same placeholder text whatever was dropped). Logged once per type per proxy process (`_logged_unknown` is module-level and is reset on addon reload) | PDF `document` block on Sonnet → model never sees it | `:49,507-512` |

Domain consequence for P3: a Sonnet request that carries a `document` block is not rerouted to Anthropic. It is served locally **without** the document. That is a functional difference from the Anthropic lane, frozen by parity (D4). Recorded as an owner decision (§8).

### 4.4 Response-side schema consumed

| Source | Paths read | Rule | Line |
|---|---|---|---|
| Response headers, host `api.anthropic.com` (any path) | `anthropic-ratelimit-unified-*` | suffix → value, logged on change per session per process | `:176-188` |
| Response headers, any flow | `content-type` | contains `text/event-stream` → `_SSETap` as `response.stream` (any host, both lanes). Else `/v1/messages*`: `application/json` or status ≥ 400 → buffered; otherwise streamed | `:195-208` |
| SSE `data: {…}` events | top-level `usage.input_tokens`/`output_tokens` (sets `usage` only if the `input_tokens` key is present); `usage` and `message.usage` cache fields (maxima); `delta.stop_reason` | pass-3 BC-PX-017/033 | `:412-427` |
| Buffered JSON body (Anthropic lane only, status < 400) | `usage.{input_tokens, output_tokens, cache_*}`, `stop_reason` or `choices[0].finish_reason` | **The DGX lane never parses a buffered body for usage** (BC-PX-020) | `:225-235,439-456` |
| Buffered DGX body | `stop_reason` / `choices[0].finish_reason` | stop reason only, decision log; no ledger usage | `:301-309` |

### 4.5 Flow-attribute entity lifecycle

| Attribute | Set (where, when) | Shape | Mutated | Read by | Absent when |
|---|---|---|---|---|---|
| `_attrib` | `request` `:117`, after the body parses as a dict | `{project, user, session, meta_user_id, model_req, req_bytes, path}` (+ `lane` on R3/R4, `:133,138`) | `lane` added | `responseheaders` (session, `:184`), `response` Anthropic branch (`:216`), `error` fallback (`:318`) | R0-R2; never on DGX-host flows **not** routed by this addon |
| `_t0` | `request` `:128`, with `_attrib` | float (wall clock) | — | Anthropic `duration_s` (`:238`) | same as `_attrib` (then `duration_s ≈ 0.0`) |
| `_dgx` | `request` `:152`, R5 only, **after** `normalize_for_dgx` succeeded | copy of `_attrib` + `model_served` (= the requested model, pre-rewrite) | `response` adds `in_tok`, `out_tok`, `stream_stop_reason` (`:267-271`) | DGX branch (`:256`), `error` (`:318`, preferred over `_attrib`) | R0-R4; R5 when normalization raised (P-R3) |
| `_dgx_t0` | `request` `:153` (= `_t0`) | float | — | DGX `duration_s` (`:273`) | as `_dgx` |
| `_sse_tap` | `responseheaders` `:197`, any SSE response, any host | `_SSETap` (buf ≤ 64,000 B, usage, cache maxima, stop_reason) | fed per chunk | `response` both branches (`:217,257`) | non-SSE responses |
| `_bridge_dur`, `_ws_started` | **never set** | — | — | `:213`, `:529-535` | always (dead; BC-PX-026/027) |

Process-level state: `_router._key_cache` (API key, read once, **retried on every request until a read succeeds**, `:91-95`); `_router._last_rl` (`dict session → sorted-JSON`; **unbounded**, one entry per session id seen, plus a shared `None` key, `:181-187`); `_logged_unknown` (`set`, `:50`). Live reload (`mitmdump -s` re-import) resets all three.

### 4.6 Proxy crash-path catalogue (exceptions that escape a hook to mitmproxy)

What mitmproxy does with an escaped addon exception is **external**: mitmproxy source is not in the repo and its version is unpinned. Expected behavior (LOW, from mitmproxy's design, unverified here): it logs an addon error and **continues the flow with whatever state the hook had already applied**. The "Outcome" column assumes that and is otherwise a static fact about the state at the moment of the raise.

| ID | Hook | Trigger | Raising line | State already applied when it raises | Outcome (if the flow continues) |
|---|---|---|---|---|---|
| P-R1 | request | `model` truthy non-str (number, list, dict, `true`) | `:132` | `_attrib`, `_t0`, `Accept-Encoding: identity` | goes to **Anthropic** unrouted; no `anth_request`; `anth_reply` **without `lane`** (`anth_usage` defaults lane `anthropic`) |
| P-R2 | request | prefix model + `tools` truthy non-iterable | `:461` | same as P-R1 | same as P-R1 (a would-be **DGX** request silently served by Anthropic) |
| P-R3 | request | prefix model, no server tool, and normalization meets: `messages` truthy non-iterable; a non-dict message; an unhashable tool name; an unhashable `tool_addition`/`tool_removal` name | `:478,486,487,502,506` | same as P-R1; the in-memory `req` is partly mutated but **never serialized** (`:150` not reached); `_dgx` unset | same as P-R1: original body to Anthropic, no `dgx_request` |
| **P-R4** | request | API key file missing or unreadable (`open`/`read` OSError in `_key()`) | `:93` via `:164` | `dgx_request` **already written** (`:154`); `X-DGX-Project/User/Session` set (`:156-159`); **scheme/host/port already switched to the DGX** (`:161-163`); body already rewritten if changed (`:150`) | request goes to the **DGX** carrying Claude Code's **original `Authorization`** (OAuth bearer or `x-api-key`) and `anthropic-beta` (`:165` not reached), over the backend's scheme (`http` by default). **Credential exposure to the backend.** Repeats on every DGX-lane request until the file is readable. Ordering is a static fact; continuation is the LOW external assumption |
| P-S1 | response (Anthropic) | buffered JSON `usage.input_tokens`/`output_tokens` not `int()`-able (non-numeric str, list, dict, NaN, ±Inf) | `:243` | — | **neither** `anth_reply` nor `anth_usage` (pass-3 BC-PX-034 (4)) |
| P-S2 | response (Anthropic) | `metadata.user_id` is a JSON-object string whose `account_uuid` is truthy and not sliceable (number, `true`, object) | `:332` via `:250` | `anth_reply` written | `anth_usage` lost (round-1 I6). **[scratch-verified]** int/bool/dict raise TypeError; a **list** slices without error and writes `account: [...]` into the ledger, which poisons the exporter (E-06) |
| P-S3 | response (DGX) | same `account_uuid` trigger | `:332` via `:277` | `dgx_reply` written (`:272`) | `dgx_usage` lost; the status ≥ 400 capture and the success note are skipped |
| — | responseheaders | rate-limit block | `:176-190` | — | fully guarded (`except Exception`) |
| — | `_SSETap.feed` | any `_scan` error | `:404-407` | — | swallowed; the rest of that chunk's block is unparsed (BC-PX-016/033) |
| — | error | — | `:311-323` | — | no escaping path found |

Non-crash note: `ledger(event, **fields)` catches only `OSError` (`:61`). All ledger values are JSON-derived or `str`/`int`/`float`, so `json.dumps` cannot raise. None of the field dicts can contain the keys `t` or `event` (verified against every call site), so no keyword collision is possible.

---

## 5. Target 5 — Exporter domain model (P2)

Metric names, label sets and formats: pass 1 §4.7 (verified by extraction validation). Per-event rules: pass 3 BC-EX-001..017. This section adds the **state entity** (what creates a series and which series are coupled) and the **crash catalogue** with process-level outcomes.

### 5.1 Rebuild state: key creation and series coupling

| State | Key tuple (defaults) | Created by (only) | Series emitted | Coupling / quirk |
|---|---|---|---|---|
| `req_totals` | `(project\|"unknown", user\|"unknown", model_req\|"?", acct, dev)`, with acct/dev from `_account_device(meta_user_id)` | every `dgx_request` | `dgx_llm_requests_total`, one per key | — |
| `est_prompt` | `(project, user, acct)` | `dgx_request` with numeric `req_bytes > 0` (`true` counts as 1 → +0.25) | `dgx_llm_est_prompt_tokens_total` | keys exist only for requests with bytes; `{v:.0f}` half-even on exact ties (**[scratch-verified]** `2.5→2`, `3.5→4`) |
| `tok_in`, `tok_out` | `(project, user, account\|"unknown")`, account from the **proxy's** `_account_hint` | every `dgx_usage` (the key is created even with 0 tokens) | `dgx_llm_tokens_{input,output}_total` | **`tok_in`'s key set drives** the emission of `dgx_llm_tokens_cache_read_total` and `…_input_captured_total` (zeros allowed, `:311-315`) |
| `dgx_cr`, `dgx_in_cap` | same as `tok_in` | `dgx_usage` carrying the key `cache_read_tok` | (via `tok_in` keys) | indexing during exposition inserts zero keys (harmless) |
| `dur_sum`, `dur_count` | `(project, user)` | `dgx_reply` with numeric `duration_s` | `dgx_llm_request_duration_seconds_{sum,count}` | — |
| `errors` | `(project, user)` | `dgx_reply` with `status ≥ 400`, and **every** `dgx_upstream_error` | `dgx_llm_request_errors_total` | session errors do **not** include upstream errors (`:202` vs `:208-210`) |
| `anth_req` | `(project, user, model_req\|"?", account\|"unknown")` | every `anth_request` | `dgx_llm_anthropic_requests_total` | account is always `unknown` (pass 1); label sets never join with the token families below |
| `anth_in` (+ `anth_out`, `anth_ds/dc`, `anth_cr/cw5/cw1/cov`) | `(project, user, model\|"?", account\|"unknown")` | every `anth_usage` | `anth_in`'s key set drives the emission of **all** Anthropic token, duration and cache families (`:327-347`) | `anth_ds/dc` never incremented (always 0); `anth_rqs` computed but never emitted |
| `passthrough` | — | `anth_reply`/`anthropic_reply` with `status == 200` (`200.0` counts too; `"200"` does not) | `dgx_llm_anthropic_passthrough_total` | includes `count_tokens` replies (path prefix) |
| `last_ts`, `last_dgx_ts`, `last_anth_ts` | — | parseable `t` (any event / `dgx_request` / `anth_request`) | gauges (`last_ts` always; the other two only when > 0) | `t` is **local** wall time parsed naive, so the **TZ** of the exporter process is a harness parameter |
| `sess_meta` | `session` | the first DGX-lane event (`dgx_request/reply/usage`) with a truthy session; project/user from that first event; `last` = max parseable `t` | session funnel, trimmed to `SESSION_LIMIT` by `last` desc (stable sort: ties keep first-seen order) | `DGX_SESSION_LIMIT` negative → `[:-n]` on the newest-first list drops the n **oldest** sessions and keeps all others (Python slice, `:238`); `0` → no sessions |
| `sess_stats` | `session` | reqs (`dgx_request`), in/out (`dgx_usage`), errors (`dgx_reply` ≥ 400) | `dgx_llm_session_{requests,tokens_in,tokens_out,errors}` | **never cleared** between rebuilds (entries for sessions that fell out of the top 50 stay in memory; emission is bounded by `sess_meta`) |
| `sess_proj` | `session` | any event with session + project | **none** | dead state |
| `fakestop` | kind | hook log substrings (BC-EX-014) | `dgx_llm_fakestop_events{kind}`, `…_p_done_latest` | `p_done_latest` = **first** `p_done=([0-9.]+)` match of the **last** line that has one. A non-Kev line whose `tail` text contains `p_done=0.9` sets it (**[scratch-verified]**). `"0.3.4"` → `float` ValueError swallowed, keeps the previous value. `p_done=nan` never matches |
| `processed_size` | — | set **after** a successful `rebuild()` (`:286-287`) | — | triggers a rescan when the size differs (also on shrink). `?rebuild=` with an empty value does **not** trigger (`parse_qs` drops blank values); `?rebuild=0` **does** (**[scratch-verified]**) |

Determinism contract for P2: the exposition is a pure function of (ledger bytes, hook-log bytes, process **TZ**, `DGX_SESSION_LIMIT`). Nothing else is read (`:94-266`).

### 5.2 Exporter crash catalogue (no guard around `do_GET` or startup)

Process-level outcome, from the stdlib source (`socketserver.py:316-320,371-382`, Python 3.11; same structure in 3.9). An exception in `do_GET` propagates to `_handle_request_noblock` → `handle_error` prints a traceback to stderr (`/tmp/dgx-ledger-exporter.log` via the plist) → `shutdown_request`. **The scraper gets the connection closed with no HTTP response.** The single-threaded server keeps running.

| ID | Phase | Trigger (ledger / hook log content) | Raising line | Persistence |
|---|---|---|---|---|
| E-01 | rebuild | ledger line is valid JSON but not an object | `:121` AttributeError | **permanent** (append-only ledger) |
| E-02 | rebuild | `t` truthy and not a str (only `ValueError` is caught) | `:125` TypeError (**[scratch-verified]**) | permanent |
| E-03 | rebuild | `session` unhashable (list/dict) with a truthy project or a DGX-lane event | `:137` / `:139` TypeError | permanent |
| E-04 | rebuild | `dgx_usage` `in_tok`/`out_tok`/`cache_read_tok` not `int()`-able | `:152-158` ValueError/TypeError/OverflowError | permanent |
| E-05 | rebuild | `anth_usage` `in_tok`/`out_tok`/`cache_*` not `int()`-able | `:167-176` | permanent |
| E-06 | rebuild | a key component unhashable (`project`, `user`, `model_req`, `model`, `account` is a list/dict), e.g. the list-valued `account` from P-S2 | `:150-152,161-167,186,195,210` TypeError | permanent |
| E-07 | rebuild | `dgx_reply` `status` null or a string | `:200` TypeError (**[scratch-verified]**; BC-EX-004) | permanent |
| E-08 | rebuild | `dgx_request.meta_user_id` JSON whose `account_uuid`/`device_id` is truthy and not sliceable | `:84-85` / `:89-90` TypeError | permanent |
| E-09 | rebuild | ledger or hook log not valid UTF-8 (the file iterator raises outside the inner `try`; open is UTF-8 strict under launchd, §1.4); `PermissionError`/`IsADirectoryError` (only `FileNotFoundError` is caught); `RecursionError` from a deeply nested line | `:116`, `:216`, `:115`, `:118` | permanent. The ledger is ASCII by construction (`json.dumps` `ensure_ascii`, `dgx_proxy.py:60`). The hook log holds raw printable non-ASCII (`repr`, §6.5) written in the hook's locale encoding |
| E-20 | exposition | a label component that is hashable but not a str (int/float, e.g. `model_req: 5`): either `sorted()` meets mixed types first or `esc()` hits a non-str | `:293`, `:294` etc. | permanent: `processed_size` was already updated, so later scrapes skip `rebuild` and re-raise; growth just rebuilds the same poisoned state |
| E-21 | exposition | `session` hashable non-str (int) → `s_id[:8]` | `:382` TypeError | permanent |

**Startup amplification (new):** `__main__` calls `rebuild()` at `:411`, **before** the server binds. Any rebuild-phase trigger (E-01..E-09) kills the process. launchd `KeepAlive` (`plist:10`) restarts it into the same crash, so **`:9210` is never served** (scrapes get connection refused) until the ledger is repaired. In the running process the same trigger makes every scrape fail (no response) but leaves the process up.

Production reachability: every trigger needs a value the proxy never writes for Claude Code's real traffic. `status` and `t` are always int and str; `model_req` reaches the ledger only as a str (a non-str model crashes P-R1 first); sessions come from headers. So E-* are **corruption, hand-edit or cross-version paths**. The P2 parity harness must decide whether to reproduce them (owner decision, §8).

---

## 6. Target 6 — Stop hook and launcher entities (P4)

### 6.1 Hook stdin schema (Claude Code `Stop` hook input) with type/fallback/crash table

| Path | Expected | Consumed at | Fallback | Mistyped → outcome |
|---|---|---|---|---|
| (stdin) | JSON object | `:211` `json.load(sys.stdin)` | empty, invalid JSON, or invalid UTF-8 (strict locale; `UnicodeDecodeError` is a `ValueError`) → `return`: **exit 0, no stdout, no log** | non-object (array, number, string, `null`) → `data.get` AttributeError `:214` → **exit 1** (H-01). Deep nesting → RecursionError (not ValueError) → exit 1 |
| `last_assistant_message` | str | `:214-215` | falsy → `""` | truthy non-str → `.strip()` AttributeError → exit 1 (H-02) |
| `stop_hook_active` | bool | `:226`; logged `:198` | missing → treated as false; logged `None` | **any truthy value allows the stop** (e.g. the string `"false"`) |
| `transcript_path` | str | `:245` → `open(…)` `:68` | falsy → `""` → `FileNotFoundError` (OSError, caught) → no transcript lines; a directory → `IsADirectoryError` (caught) | int/`true` → opened **as a file descriptor** (`true` = fd 1, stdout; the `with` block then closes it). list/dict/float → TypeError, not OSError → exit 1 (H-03) |
| `session_id` | str | logged only (`:198`) | missing → `None` → `session=None` | rendered with `str()` |
| others (`cwd`, `hook_event_name`, `permission_mode`, …) | — | ignored | — | — |

New consequence: an **empty or absent `last_assistant_message` still runs the Kev path**. It is not English-flagged, not `?`, not a colon fake (needs len > 20), and `should_continue("")` is False. But `kev_state` builds the state from the transcript alone, Kev is called (up to 3 times), and a `kev-continue` can be emitted (`:214,236,244-261`).

### 6.2 Kev wire format (optional backend, D11)

| Part | Exact form | Line |
|---|---|---|
| Request | `POST {DGX_KEV_URL}`. Headers: `Content-Type: application/json`, plus `Authorization: Bearer <key>` when a key is truthy (env `DGX_KEV_API_KEY`, else the hard-coded file `~/.config/dgx-llm/kev-api-key`, stripped; an empty file → no header). urllib adds `User-Agent: Python-urllib/3.x`, `Host`, `Content-Length`, `Connection: close` | `:96-110` |
| Body | `json.dumps({"model": KEV_MODEL, "state": state, "questions": {"turn_complete": DONE_QUESTION}})` → ASCII, separators `", "`/`": "`; `DONE_QUESTION = {"type": "noul", "instructions": <fixed text>}` | `:38-61,105-109` |
| Proxying | urllib honors env proxies. The launcher exports `HTTPS_PROXY` only (`claude-dgx:79`), so an `http://` Kev URL goes direct. An `https://` Kev URL would go **through the local mitm proxy**, which passes it untouched (R1) | `:110-113`; `claude-dgx:79` |
| Response | JSON object; `answers.turn_complete.noul` must be `int`/`float` (`true` → 1.0; `NaN` accepted → never "fake", logs `p_done=nan`) | `:114-118` |
| Failure → `(None, None)` | `OSError` (incl. `URLError`/`HTTPError`/timeouts), `ValueError` (bad JSON), `KeyError`, or a non-numeric `noul` | `:119-121` |
| Failure → **crash** | response not a dict, `answers` null or non-dict, `turn_complete` non-dict (AttributeError); `http.client.HTTPException` subclasses (pass-3 BC-HK-019) | `:115-116` |
| Budget | ≤ 3 calls × 2.5 s + transcript read, inside the Stop-hook timeout of 30 s | `:124-138`; `claude-dgx:161` |

### 6.3 New hook crash path H-04: `kev_pdone_median` returns `(p, None)` (**[scratch-verified]**)

`kev_pdone_median` overwrites `t` on **every** attempt (`:130`). If at least one attempt succeeded but the **last** attempt failed, it returns `(median, None)` (`:137-138`). `main` then formats `f"p_done={p_done:.3f} fake={fake} ({secs:.2f}s)"` (`:250`), which raises `TypeError: unsupported format string passed to NoneType.__format__`.
- Reachable sequences (3 tries, no early stop because `t ≤ 1.25 s` or `t` is None): (ok, ok, fail), (ok, fail, fail), (fail, ok, fail). All three crash in scratch.
- Outcome: traceback, **exit 1, no stdout, no log line**. The stop is allowed (pass-3 BC-HK-019 semantics), and the decision is **invisible to the exporter** (no `[kev-…]` line, so no calibration record).
- Realism: **production-reachable**. It needs only one Kev timeout or connection error on the third attempt after a fast success. Pass-3 gap 9 noted the missing early stop but not this crash.
- Also exact: with 2 successes the "median" is the **upper** value (`ps[1]`).

Consolidated hook crash IDs: H-01 non-object stdin; H-02 non-str message; H-03 bad `transcript_path` type; H-04 median `(p, None)`; H-05 transcript content (invalid UTF-8, non-object line, non-dict `message`, non-str truthy `text`; pass-3 BC-HK-019 (3)); H-06 Kev response shape and `HTTPException`; H-07 import-time `float()`/`int()` of `DGX_KEV_*`; **H-08 import on Python < 3.10** (`:94`, §1.4). All give exit 1 with no stdout.

### 6.4 Hook stdout wire format

`json.dumps({"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": <ctx>}})` + `\n`, pure ASCII (pass-3 BC-HK-021). The five `<ctx>` values are fixed texts (`:219-223,237-241,255-260,266-270`). Only two embed variables: `kev-continue` has `p(done)={p_done:.2f}`, and `heuristic-continue` has `\"…{tail[-100:]}\"`. Whether Claude Code honors `additionalContext` on `Stop` (vs the documented `decision:"block"`) remains external (pass 1).

### 6.5 Hook log line as a wire format

```text
line   = ts SP "[" kind "]" SP "kev=" kev SP "session=" pystr SP "stop_hook_active=" pystr SP "tail=" pyrepr LF
ts     = local time.strftime("%Y-%m-%d %H:%M:%S")                         ; auto_continue.py:197
kind   = "non-english" / "colon-fake" / "kev-allow" / "kev-continue" / "heuristic-continue"
kev    = "-"                                              ; non-english, colon-fake (emit default, :204)
       / "p_done=" F3 " fake=" ("True" / "False") " (" F2 "s)"   ; kev-allow => False, kev-continue => True (:250)
       / "unreachable"                                    ; heuristic-continue (:270)
pystr  = Python str(): None -> "None", True/False -> "True"/"False", str verbatim (unescaped)
pyrepr = Python repr() of tail, where tail = msg.strip()[-160:] with "\n" -> " " (:215)
```

`repr` rules, **[scratch-verified]** (3.11):

| Input property | Output |
|---|---|
| default | single quotes: `'plain'` |
| contains `'` and no `"` | double quotes: `"it's"` |
| contains both `'` and `"` | single quotes, `\'` escaped: `'both \' and "'` |
| `\` | `\\` |
| `\t`, `\r` (and `\n`, which cannot occur) | `\t`, `\r` |
| non-printable ≤ U+00FF (C0, DEL, C1, **NBSP U+00A0**) | `\xNN` (`\x1b`, `\xa0`) |
| non-printable BMP (U+200B, lone surrogates) | `\uNNNN` (`​`, `\ud800`) |
| non-printable astral | `\UNNNNNNNN` |
| printable non-ASCII (é, CJK, emoji) | **raw**, encoded in the hook's locale (UTF-8 expected) |

Go hazard: `strconv.Quote` always uses double quotes, and Go's `IsPrint` set differs (e.g. NBSP becomes ` `, not `\xa0`). Go needs a dedicated Python-`repr` encoder driven by Python's `str.isprintable` table (Unicode-version-sensitive). `session` values are not escaped: a newline in a session id would split the line (Claude Code session ids are UUIDs).

Coupling to the exporter: tallies match a substring **anywhere in the line**, checked in a fixed pattern order (kev-continue, kev-allow, kev+opus-continue, colon-fake, heuristic-continue), so the first matching **pattern** wins, not the first position. `non-english` lines are not counted. `tail` is model output, so it can inject both a tally pattern and a `p_done=` value (§5.1).

### 6.6 Launcher `--settings` JSON: exact wire format

Built by string concatenation (`claude-dgx:156-181`); no JSON encoder is involved. Default environment (`DGX_ENGLISH`, `DGX_AUTOCONTINUE` = 1, `DGX_SANDBOX` unset, `DGX_STATUSLINE` unset → 1), `HERE` = the launcher's directory (`${0:A:h}`, `:7`). The exact bytes are one line, no spaces:

```text
{"hooks":{"UserPromptSubmit":[{"hooks":[{"type":"command","command":"echo \"[Reminder: reply and think in English only. No Chinese anywhere, including your reasoning.]\"","timeout":5}]}],"Stop":[{"hooks":[{"type":"command","command":"python3 '<HERE>/auto_continue.py'","timeout":30}]}]},"statusLine":{"type":"command","command":"python3 '<HERE>/dgx_statusline.py'","padding":0,"refreshInterval":4},"subagentStatusLine":{"type":"command","command":"python3 '<HERE>/dgx_statusline.py' --subagent"}}
```

| Variant | Effect on the bytes | Line |
|---|---|---|
| `DGX_ENGLISH=0` | `UserPromptSubmit` element omitted, so `hooks` holds only `Stop` | `:157-159` |
| `DGX_ENGLISH=0` and `DGX_AUTOCONTINUE=0` | no `hooks` key | `:160,164` |
| `DGX_SANDBOX=1` | `,"sandbox":{"enabled":true,"allowUnsandboxedCommands":false}` inserted **after** `hooks`, **before** `statusLine` | `:165-167` |
| `DGX_STATUSLINE` ≠ `1` | both `statusLine` and `subagentStatusLine` omitted | `:175-178` |
| everything omitted | no `--settings` argument at all | `:179-181` |

Hazards (static): `<HERE>` is inserted raw. A `"`, `\` or control character in the path makes the JSON invalid or changes its meaning. A `'` breaks the shell command Claude Code runs. Non-ASCII is fine. `subagentStatusLine` was removed in Claude Code 2.1.323 (per the owner's notes in `CLAUDE.md`); the launcher still emits it.

Argument vector (`:128-185`): `claude --model <opus|sonnet> [--remote-control] [--append-system-prompt <LANGUAGE RULE>] [--dangerously-skip-permissions] [--settings <json>] "$@"`. User arguments come **last**.

### 6.7 Child environment assembled for Claude Code (and inherited by the status line, hook and Kev calls)

| Variable | Value | Line |
|---|---|---|
| `LOCAL_MODEL_PREFIXES` | `claude-sonnet`, **forced** (overrides any user value; only `profile.env`, sourced later, can change it, and then not for the already-running proxy, BC-LN-006) | `:38` |
| `DGX_SERVED_MODEL` | `claude-sonnet-5-5`, forced | `:39` |
| `ANTHROPIC_CUSTOM_HEADERS` | existing value + `\n` + `X-DGX-Project: <basename $PWD>` + `\n` + `X-DGX-User: <DGX_USER or whoami>`, values raw (a newline in a dir name would inject a header line) | `:43-53` |
| `ANTHROPIC_BASE_URL` | **unset** (invisible mode) | `:71,100` |
| `HTTPS_PROXY` | `http://127.0.0.1:<8090..8143>` | `:79` |
| `NODE_EXTRA_CA_CERTS` | `$HOME/.mitmproxy/mitmproxy-ca-cert.pem` | `:80` |
| `API_TIMEOUT_MS` / `CLAUDE_CODE_AUTO_MODE_SERVER` | `1800000` / `0` | `:104,109` |
| `profile.env` contents | exported via `set -a` | `:114-115` |
| `DGX_ENGLISH`, `DGX_AUTOCONTINUE` | `${…:-1}` | `:148` |
| `DGX_KEV_THRESHOLD`, `DGX_KEV_URL`, `DGX_KEV_MODEL` | `0.40`, placeholder URL, `jaredpalmer/kev-4b@v1.0` (defaults) | `:152-155` |
| **not set** | any locale variable, `HTTP_PROXY`, `NO_PROXY`, `PYTHON*` | — |

### 6.8 Env boolean grammar (legacy is string comparison, per variable)

| Variable | "On" iff | Unset / empty | Notable consequences | Line |
|---|---|---|---|---|
| `DGX_INVISIBLE` | `== "1"` | → `1` (on) | any other value selects the **visible** mode, which needs `opus_router.py` (not in `legacy/`), so startup fails, exit 1 | `claude-dgx:62,70,86,99` |
| `DGX_SKIP_PREFLIGHT` | skip iff `== "1"` | → `0` (run preflight) | `true` runs the preflight | `:60` |
| `DGX_MAIN_MODEL` | `== "opus"` → opus | → `sonnet` | any other value → sonnet | `:128-131` |
| `DGX_REMOTE`, `DGX_SANDBOX`, `DGX_PRINT_ARGS` | `== "1"` | off | `true` = off | `:133,165,182` |
| `DGX_SAFE` | `== "1"` keeps permission prompts | off (prompts **skipped**) | `true` = prompts skipped | `:139` |
| `DGX_STATUSLINE` | `== "1"` | → `1` (on) | **`true`/`yes` disable the status line** | `:175` |
| `DGX_ENGLISH` | launcher `!= "0"`, hook `!= "0"` | → `1` (on) | consistent between writer and reader | `:136,148,157,160`; hook `:217` |
| `DGX_AUTOCONTINUE` | launcher `!= "0"`; hook disables iff `== "0"` | → `1` (on) | consistent | `:148,160`; hook `:228` |
| `DGX_SL_SPARK`, `DGX_SL_GIT` | `!= "0"` | on | — | `dgx_statusline.py:76-77` |

Consequence for D15: a `DGX_*` alias cannot go through one generic bool parser without changing legacy behavior for values such as `true`, `yes` or `0`. The per-variable rule has to be kept for the aliases, or the change documented (owner decision §8).

---

## 7. Target 7 — Backfill (`hylo cost backfill`) domain and contract table

All lines are `tools/backfill_cost_history.py`.

| Aspect | Exact rule | Line / evidence |
|---|---|---|
| Inputs | `glob("~/.claude/projects/*/*.jsonl")`: **one directory level**, so subagent transcripts under `<sid>/subagents/` are excluded. `sid = basename[:-6]`. Filter: `getmtime(path) < now − days·86400` → skip (strict; **file mtime**, not transcript time) | `:95-100` |
| Glob order dependence | (1) new `sessions` keys are inserted in **glob order** (filesystem-dependent), which fixes the JSON key order of the output; existing keys keep their position. (2) The same sid in two project dirs → the **last** in glob order wins. The `src=="cc"` check reads the live dict, so it never protects a backfill entry from a later duplicate | `:97-109`; pass 5 |
| Skip rules | existing entry `src == "cc"` → skip (counted `skipped_cc`); `usd < 1.0` (strict) or no timestamped line → skip (`skipped_small`) | `:101-107` |
| Line parse | `open(path, errors="replace")` (locale encoding, replacement on bad bytes) → `json.loads` per line, `ValueError` skipped. A trailing partial line is parsed if it is valid JSON | `:44-48` |
| Timestamp | lines with a falsy `timestamp` are **skipped entirely** (usage included). `ts()` = `fromisoformat(s.replace("Z","+00:00")).timestamp()`; naive → **local** time | `:38-52` |
| Message entity | keyed by `message.id` over the **whole file**, created on the first assistant line with a truthy id and a **dict** `usage`: `{t0: last user ts (any user line, incl. tool_result), t1, u: that line's usage, model: that line's model}`. **First line wins for usage and model**. Later lines update `t1` only, and only if they also carry a dict usage | `:53-62` |
| Family resolution | `next(k for k in ("opus","sonnet","haiku") if k in model)`: dict order, **substring**, case-sensitive. **[scratch-verified]**: `claude-opus-5-5`→opus, `claude-sonnet-5-5`→sonnet, `sonnet-opus-mix`→**opus**, `Claude-Opus`→none, `claude-fable-5-2`→none, `<synthetic>`→none, `glm-…`→none, `""`→none | `:66` |
| Unknown family | the message is skipped for **usd, lane output and span** alike | `:67-68` |
| Price table ($/MTok: in, out, 5m write, 1h write, read) | opus `4, 20, 5, 8, 0.20`; sonnet `2, 10, 2.5, 4, 0.10`; haiku `0.10, 0.50, 0.125, 0.20, 0.005` | `:30-32` |
| vs documented prices (research §3.5) | opus and sonnet: match. **haiku cache read `0.005` vs documented `0.01`**. **Haiku > 100K-prompt tier** (`0.50/2.50/0.625/1.00/0.05`) absent. **Fable/Mythos 5.2** (`8/40/10/16/0.20`) absent, so those sessions are unpriced (skipped). Batch discount, fast mode and server-tool charges are not modeled | research doc §3.4-3.5 |
| Cost formula | `(in·pi + out·po + w5·p5 + w1·p1 + read·pr)/1e6`. `w1 = cache_creation.ephemeral_1h or 0`. `w5 = cache_creation.ephemeral_5m` **or** (`0` if `cache_creation` is a non-empty dict, else `cache_creation_input_tokens or 0`) | `:71-76` |
| `w5` edge cases (**[scratch-verified]**) | no split → total write priced at 5m. `cache_creation: {}` → total at 5m. Split present with 5m=0, 1h=0 but total 100 → **0 priced** (writes vanish). Split `{5m:60, 1h:40}` → 60 + 40. `cache_creation_input_tokens` is **never** used when a split dict exists | `:72-73` |
| Lane | output tokens summed per lane (`any(model.startswith(p) for p in prefixes)` → `dgx`, else `anth`). Lane = `max(out, key=out.get)`; tie or all-zero → `dgx` (**[scratch-verified]**). Prefixes default `claude-sonnet` (the status line's default is empty) | `:63,77,81,89` |
| DGX-lane price meaning | a DGX session is priced at **Anthropic list price** for its model id (`claude-sonnet-5-5` → sonnet rates). This matches the status line's `cost.total_cost_usd`, which is Claude Code's list-price figure. So `usd` is a list-price equivalent on both lanes, never the owned-hardware cost | `:66-76`; statusline `:565-568` |
| Span (`api_ms`) | Σ `t1 − t0` over messages with `t0 is not None` and `0 < span ≤ 4·max(out,1)/15`; `api_ms = span·1000` if ≥ 1,800,000, else `None` (float when set). Round-1 I7 divergences apply | `:78-80` |
| Output record | `sessions[sid] = {"lane", "usd": round(usd,4), "api_ms", "ts": last, "src": "backfill"}`. `ts` = timestamp of the **last timestamped line of any type** | `:108` |
| Output file | unless `--dry-run`: `makedirs`, `mkstemp(prefix="cost-history.")` (mode **0600**), `json.dump(hist, fh)` (default separators, `allow_nan`, no trailing newline), `os.replace`. Other top-level keys are preserved | `:111-116` |
| Stdout | `backfilled N sessions (skipped: S under $1, C already recorded exactly)`, then `wrote <path>` | `:110,117` |
| Corrupt history | parse failure → `{}`, and the write **replaces all history** (round 1 §3.5) | `:90-93` |

Backfill crash catalogue: every exception aborts the run **before** the single write at the end, so on crash nothing is written.

| ID | Trigger | Line |
|---|---|---|
| B-01 | `timestamp` truthy but unparseable (ValueError) or non-str (AttributeError on `.replace`) | `:39,52` |
| B-02 | transcript line is JSON but not an object; `message` truthy and not a dict | `:49,53-54` |
| B-03 | `model` truthy and not a str (`k in 5` TypeError) | `:59,66` |
| B-04 | `cache_creation` truthy and not a dict (`.get` AttributeError, **[scratch-verified]**) | `:71-72` |
| B-05 | token value a non-numeric str/list (`"5" * 2.0` TypeError, **[scratch-verified]**) | `:75-76` |
| B-06 | history top level not an object, `sessions` not a dict, an entry not a dict | `:94,101` |
| B-07 | file vanishes between glob and `getmtime`/`open`; unreadable file | `:98,44` |
| B-08 | `message.id` unhashable with a dict usage | `:58` |

---

## 8. Owner decisions pending (consolidated; not resolved here)

Carried from round 1:
1. CONFIG key naming scheme and the `HYLO_*` derivation rule (round 1 §6).
2. Whether glyphs are config (round 1 §6.2, last row).
3. Windows sid sanitizing (I8).
4. Whether `paths.hook_log` unifies writer and reader during parity (round 1 §6.1 row 16).

New this round:

5. Legacy **env-bool grammar** for `DGX_*` aliases: keep the per-variable string rules (§6.8; `DGX_STATUSLINE=true` disables) or normalize them and document the change.
6. **P-R4 credential exposure**: when the backend key cannot be read, legacy forwards Claude Code's own `Authorization`/`x-api-key` to the backend. Parity (D4) would reproduce it. Fail closed (e.g. 502) as an approved deviation?
7. **P-R1..R3 silent re-lane**: a request-hook exception serves a would-be DGX request from Anthropic (plan usage). Reproduce, or fail visibly?
8. **`document` and other non-six-type blocks dropped** on the DGX lane (§4.3): reproduce (parity), or route such requests to Anthropic later?
9. **`count_tokens` on local-prefix models goes to the DGX** (§4.2): keep, or (in line with D13's narrowing to `POST /v1/messages`) leave `count_tokens` on Anthropic?
10. **Exporter poison-line behavior** (E-01..E-21, startup crash loop): reproduce in the P2 harness, or skip-and-count bad lines as a documented deviation?
11. **Hook H-04** (`(p, None)` crash on a final Kev failure): reproduce (exit 1, no log) or fix during the port?
12. **Backfill price table** vs documented prices (haiku read 0.005 vs 0.01; no Haiku > 100K tier; no Fable/Mythos): keep the legacy table for parity, or update it (it is "used ONLY by this one-off backfill", `:29`)?
13. **Interpreter pinning** for the harness: status line and hook `python3` ≥ 3.10 (exact version via the §1.3 probe); exporter `/usr/bin/python3` 3.9.6. Accept these as the parity oracles?
14. Launcher `subagentStatusLine` emission on Claude Code ≥ 2.1.323 (key removed upstream): carry it into `hylo run` or drop it?

---

## Delta Summary

| Target | New items | Highlights |
|---|---|---|
| Audit | 1 retraction (**CONV-ABS-5**), 4 confirmations with refinements, 1 crosswalk (31 ↔ 40 IDs), 2 recounts | missed CP-X03/X04 acknowledged; sticky-window and `--resume` persistence; NaN in mix and cost caches; env 40 → 42 (`HOME`, `PWD`) |
| T1 locale | 1 verdict + 1 two-outcome harness table + 1 capture recipe + **1 new co-determinant** (interpreter version per component) | hook needs Python ≥ 3.10 (`:94` PEP 604 without the future import; scratch-verified crash on 3.9.6), so production `python3` ≥ 3.10; exporter runs 3.9.6 in UTF-8 mode under launchd |
| T2 VM NaN | 1 owner capture task (exact query, 3 conditions, what to look for) | the derived series come from out-of-repo recording rules, so statically undecidable |
| T3 SSE usage | 1 documented-vs-capture table + **1 zero-capture check** (decision log `usage=None` + ledger `jq`) | settles production frequency without capturing streams |
| T4 proxy | request-schema table (13 rows); routing table with **1 new case** (`count_tokens` to the DGX); tool-set entity (6 scratch-verified rules); response-schema table; flow-attribute lifecycle (6 attributes + 3 process-level); **crash catalogue P-R1..R4, P-S1..S3** | **P-R4**: key-read failure after the host switch → original credentials sent to the backend; P-R1..R3: silent re-lane to Anthropic; nameless tools dropped and duplicates collapsed on rebuild; `document` blocks silently removed |
| T5 exporter | state-entity table (15 rows: creating events, emission coupling, dead state); determinism contract (TZ); **crash catalogue E-01..E-09, E-20, E-21** with phases | **startup crash loop** under KeepAlive; permanent no-response scrapes; `processed_size` ordering makes exposition-phase crashes stick |
| T6 hook + launcher | hook stdin table (6 rows); Kev wire table (7 rows); **new crash H-04** (production-reachable) + consolidated H-01..H-08; log-line grammar + 9-row `repr` table; exact `--settings` bytes + 5 variants + hazards; child-env table (11 rows); env-bool grammar (9 rows) | empty last message still calls Kev; `DGX_STATUSLINE=true` disables; `<HERE>` unescaped in JSON |
| T7 backfill | 18-row contract table + 8 crash paths | price-table discrepancies vs docs; `w5` zero-split edge drops writes; first line wins for usage and model; DGX sessions priced at list; Python-version timestamp grammar |
| Owner decisions | 4 carried + **10 new** | — |

Existing items refined: round-1 §0 (CP-25), §1.1 (int-digit limit by version), §1.3 (locale verdict), §3.6 (write order conditions), §5 (count reconciliation), §6.1 (bool grammar, env count). Pass-3 BC-EX-014 (p_done = first match of the last line), BC-PX-012 (rebuild semantics), BC-HK-010 (median crash), BC-LN-009 (exact bytes). All cited, not edited.

## Remaining Gaps (verbatim-carryable)

1. Owner capture, status line and hook env: run the §1.3 probe (`captures/sl-env-probe.py` via `DGX_STATUSLINE=0 claude-dgx --settings …`) to record locale variables, `utf8_mode`, stdin/stdout error handlers, `sys.executable` and `sys.version` as Claude Code launches the status line. Pin the harness to them. Until then: probable strict, Python ≥ 3.10 (inferred from `auto_continue.py:94`).
2. Owner capture, VictoriaMetrics: one `/api/v1/query` response for the exact `QUERY` (`dgx_statusline.py:102-123`) on an idle box, under light load, and with fewer than 20 TTFT samples, after the DGX soak is scored. Look for `"NaN"`/`"+Inf"`/`"-Inf"` in `value[1]` per `__name__` (decides CP-N01/N02 reachability).
3. Owner local check, SSE usage: count `anth tap: … usage=None` lines in the routing decision log, and `anth_reply`/`dgx_reply` with `status==200`, `path=="/v1/messages"` and no `in_tok` in the ledger. Zero hits settles the production frequency; otherwise capture one stream's event and usage-key skeleton.
4. External mitmproxy semantics (version unpinned): what happens to a flow after an addon exception (decides the P-R1..R4 outcomes, esp. P-R4 credential exposure); `get_text()` on streamed flows; `Headers.get`/`items()` with repeated headers (affects `_attrib` values and `anth_ratelimit` key order). Needs the venv's mitmproxy version and source.
5. Owner local check, `count_tokens`: does Claude Code send `/v1/messages/count_tokens` with Sonnet models (ledger `dgx_request` with that path), and what does the backend answer?
6. Recording rules (out of repo) behind `dgx_kv:*`, `dgx_ttft:*`, `dgx_cost:*`, `dgx_tokens:*`, `dgx_power:*`, `dgx_preempt:*`: which can produce NaN or Inf, and their exact definitions for P6 pluggable telemetry.
7. Coordinator, preflight and trust-CLI entities (`.proxy-state/{port,pid,lock}`, `trust-state.json` wire format, preflight error classes) are not yet modeled at T1-T3 depth. They are lower priority, since D6/D10 replace most of them.
8. Owner decisions §8 items 1-14.

## Novelty Assessment

Novelty: SUBSTANTIVE
Removing this round would change how P2, P3 and P4 are specified:
- New production-reachable crash path **H-04** (hook exits 1 with no log whenever the last Kev attempt fails after a success). It changes the P4 contract and the exporter's calibration data.
- New proxy failure model: **P-R4** (credentials forwarded to the backend when the key file is unreadable, by line order) and **P-R1..R3** (silent re-lane to Anthropic). The broad and deep passes left the `_key()` outcome as an open question.
- New exporter process-level behavior: **startup crash loop** under launchd KeepAlive, and permanent no-response scrapes from one poison line, plus the series-coupling model (`tok_in` and `anth_in` key sets drive whole families).
- New routing case (**`count_tokens` to the DGX**) and tool-set rebuild semantics (nameless tools dropped, duplicates collapsed, `document` blocks removed).
- New harness parameter (**interpreter version per component**). The hook's Python ≥ 3.10 requirement is source-proven, the exporter runs 3.9.6 in UTF-8 mode, and the backfill and status line timestamp grammars are version-dependent.
- Exact wire formats for the launcher `--settings` bytes, the env-bool grammar and the hook log line, which the spec needs for P4.

## Convergence Declaration

Another round is needed. Substantive gaps remain: the external mitmproxy semantics that decide the P-R* outcomes (gap 4), the coordinator/preflight/trust-state entities not yet modeled (gap 7), and three owner captures (gaps 1-3, 5) that decide harness parameters.

## State Checkpoint

```yaml
pass: 2
round: 2
status: complete
files_scanned: 9   # dgx_proxy.py, dgx_ledger_exporter.py, auto_continue.py, claude-dgx, tools/backfill_cost_history.py, dgx_preflight.py, dgx-proxy-coordinator.sh, deploy/*.plist (2) in full; dgx_statusline.py re-read in part for the audit
timestamp: 2026-11-14T06:13:00Z
novelty: SUBSTANTIVE
next: pass 2 round 3 (targets = Remaining Gaps 1-8 verbatim)
```
