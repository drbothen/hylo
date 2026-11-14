# Pass 2 Deepening — Round 1: Domain Model (P1 status line first) — hylo-legacy

- Source: `$HOME/Dev/hylo/legacy/` (read-only, static). Primary file: `dgx_statusline.py` (1,245 lines, read in full this round).
  Cross-checked: `dgx_proxy.py:320-427`, `dgx_ledger_exporter.py:60-99,184-193,410-414`, `tools/backfill_cost_history.py` (full), `auto_continue.py:31-36,193-201`, `claude-dgx` env knobs.
- Inputs read: every file in this directory (passes 0-6 + extraction validation), `docs/PLAN.md` (D1-D15), `docs/STATUSLINE-WIDGETS.md`, `docs/STATUSLINE-REVIEW-2026-11-13.md`.
- Method: static reading, plus scratch scripts that exercise **Python language semantics only** (no legacy module imported or run), under
  `/opt/homebrew/anaconda3/bin/python3.11` (3.11.7, `-I`), files in the session scratchpad `p2r1/`. Every scratch result quoted below is marked **[scratch-verified]**.
- Line numbers are `dgx_statusline.py` unless another file is named.

---

## 0. Round-1 audit of the broad sweep (5 hallucination classes) and retractions

| Marker | Prior claim (file) | Ground truth | Evidence |
|---|---|---|---|
| CONV-ABS-1 | Pass 4 T-064: "9999 s default age when `ts` missing" | 9999 is a default **timestamp** (unix 9999 = 1970-01-01T02:46:39Z), not an age: `age = now - c.get("ts", 9999)` gives ≈ 1.79e9 s. The case never shows: `ts` can only be missing when no fetch ever worked, and then `sample` is also missing, so the output is `◌ DGX ?` | `:325`, `:349` (only the success path writes `ts`) |
| CONV-ABS-2 | Pass 2 entity "Composition: byte shares"; glossary "byte shares ▤/❙/◈"; WIDGETS "by bytes" / "Images count 2,000 bytes" | The units are **characters**: Python code points for raw strings, characters of Python `json.dumps` output (ASCII-escaped) for structured payloads, and a constant 2000 per image. Nothing is measured in UTF-8 bytes. See I11 (§7) | `:1122,1133,1138,1140,1143,1145,1147,1149` |
| CONV-ABS-3 | Pass 6 harness rule "pin `LC_ALL=C`" | **Unsafe for parity.** `LC_ALL=C` turns on Python's UTF-8 mode, so stdin and stdout use `surrogateescape`. Under `LANG=en_US.UTF-8` (and no `LC_CTYPE`/`LC_ALL`) both are `strict`. Invalid-UTF-8 stdin then **parses** under C but becomes `{}` under en_US.UTF-8. `LC_ALL=C.UTF-8` and macOS `LC_CTYPE=UTF-8` also select surrogateescape. The harness locale has to match production's, and production's locale is UNVERIFIED (§1.3) | [scratch-verified] `p2r1/loc.py`: `LC_ALL=C` → `utf-8 surrogateescape`, parsed `{'x':'a\udcffb'}`, output bytes `a\377b`; `LANG=en_US.UTF-8` → `strict`, `UnicodeDecodeError` → `{}` |
| CONV-ABS-4 | Pass 6 R7 / Pass 3 BC-SL-033: "`json.loads` on bytes rejects invalid UTF-8" | Partly true. `json.loads(bytes)` detects the encoding and decodes with `surrogatepass`. It **accepts** a UTF-8 BOM, UTF-16/32 lines and CESU-encoded surrogates (`ED A0 80` → `'\ud800'`). It rejects other invalid UTF-8 (`\xff` → `UnicodeDecodeError` → line skipped) | [scratch-verified] `sem.py` |
| Refinement | Pass 3 BC-SL-052: "`load_cache` → `{}` on any error" (read as "corrupt caches self-heal") | Only a **parse** failure yields `{}`. Valid JSON with the wrong shape (top level not an object, wrong-typed fields) is returned as-is and crashes later → `statusline degraded` (§5 CP-30..34). A parse-failed `cost-history.json` is **overwritten with a single-session file** on the next `record_cost` (all history lost) | `:190-195,228-237` |
| Refinement | Pass 2 turn state machine | Two missing guards: lines whose `timestamp` does not parse skip the turn machine completely, and `assistant` lines with no truthy `message.id` do nothing in it. Both still count toward usage and composition | `:1069-1087` |
| Confirmed | Env count 40, mix-cache key order, session-cache keys, BC-SL-041 KEEP_DEAD quirk, `sess_state` retirement | Exact. Nuance: `sess_state` is popped **only on the fetch path** (TTL expired). The cached path never rewrites the file | `:324-328` |

No phantom entities were found. Metrics recount: `dgx_statusline.py` = 1,245 lines (`wc -l`); 40 env inputs (recounted from `grep os.environ` + `claude-dgx` knobs).

---

## 1. TARGET 1 — Claude Code status line stdin: field schema the status line consumes

### 1.1 Decoding and top-level

| Step | Rule | Line |
|---|---|---|
| Read | `json.load(sys.stdin)` (text stdin, so decoding depends on locale, §1.3). **Any** exception (empty input, bad JSON, decode error) → `d = {}` | `:1201-1204` |
| Top-level type | not a `dict` → `{}` | `:1205-1206` |
| Accepted JSON extensions | `NaN`, `Infinity`, `-Infinity` literals; exact big ints, but literals over 4,300 digits raise `ValueError` → `{}` (Python ≥ 3.11 int-digit limit) | [scratch-verified] `sem2.py` |
| Mutation | `d["rate_limits"]` is overwritten with the smoothed value before rendering | `:1216` |

### 1.2 Field table (every path read)

Python type rules the table relies on:
- **Truthiness fallbacks** (`x or y`): `0`, `0.0`, `""`, `[]`, `{}`, `false`, `null` all count as missing.
- **Number checks** use `isinstance(x, (int, float))`, and **`bool` passes** (`true` acts as 1).
- **`NaN` passes** the number checks.
- **Non-string labels** are rendered with Python `str()` (`[1, 2]`, `True`, `1.0`).

| Path | Expected (CC) | Accepted as-is | Fallback when missing/falsy | Mistyped → result | Consumer (function:line) |
|---|---|---|---|---|---|
| `session_id` | string (UUID) | any truthy | cache key `"nosession"` (`:1016,1214`); cost history not recorded (`:226`); `⌂` not attempted (`:1229`) | non-string truthy + existing transcript → `re.sub` TypeError → **degraded** (CP-13a). Unhashable (array/object) + `cost.total_cost_usd>0` + known lane → **degraded** (CP-13b). Number → files `statusline-5.json` and cost key `"5"`, so the current session is not excluded from its own thresholds (`"5" != 5`, `:246`) | `_mix_counts:1016-1017`; `main:1214-1215,1229`; `render_lane:605` → `record_cost:224-237`, `cost_thresholds:246` |
| `transcript_path` | string (abs path) | string, or int (treated as an fd: `isfile(True)` stats fd 1) | `None` → no mix: composition, tokens, `»mine` absent | array/object/float → `os.path.isfile` TypeError → **degraded** (CP-14). String with NUL → `False` | `_mix_counts:1009-1015` |
| `model` | object | object | `{}` | truthy non-object → AttributeError → **degraded** (CP-01) | `render_lane:441` |
| `model.display_name` | string | any truthy (`str()`) | → `model.id` → `"?"` | — | `render_lane:442,453` |
| `model.id` | string | any truthy | `""` → pill `◨ ?` | truthy non-string **and** prefixes non-empty → `.startswith` AttributeError → **degraded** (CP-02). With empty prefixes: no crash, pill `?` | `render_lane:443-449` |
| `workspace` | object | object | `{}` | truthy non-object → **degraded** (CP-03) | `render_lane:451` |
| `workspace.project_dir` → `workspace.current_dir` → `cwd` | string | first truthy | `""` → no branch, no project label | non-string truthy → `directory.encode` AttributeError (`:405`, git on) or `normpath` TypeError (`:460`, git off) → **degraded** (CP-04) | `render_lane:452-462`; `git_segment:405`; `git_branch:373` |
| `context_window` | object | object | `{}` | truthy non-object → **degraded** (CP-05) | `render_lane:463` → `fmt_ctx:418` |
| `context_window.used_percentage` | number \| null | int/float/bool | not a number (null before the first call, or a string) → thermometer omitted | `NaN` → `int(nan/10+0.5)` ValueError → **degraded** (CP-06). `±Infinity` clamps to 100 / 0 | `fmt_ctx:419-426` |
| `context_window.context_window_size` | number | any (truthy) | `0` → no denominator | only read when pct is numeric. Truthy string/array/object → `total >= 1e6` TypeError → **degraded** (CP-07). `true` → `/0K` | `fmt_ctx:423,435-436` |
| `prompt_cache` | object | object | `{}` | truthy non-object → **degraded** (CP-08) | `render_lane:477` |
| `prompt_cache.hit_ratio` | number 0..1 | int/float/bool | not a number → `♻` omitted | `NaN` → renders `♻ nan%` (no crash) | `render_lane:477-479` |
| `rate_limits` | object | non-empty object (stored verbatim in the session cache with `rl_ts`) | empty/absent/non-object → cached `rl` if `now - rl_ts < 1800` else `None` → widget hidden | (see children) | `effective_rl:298-312` via `main:1216`; `render_lane:489` |
| `rate_limits.five_hour` / `.seven_day` | object | object | `{}` → window unreported (hidden) | truthy non-object → `.get` AttributeError → **degraded** (CP-09). **Persistent:** the bad object has already been stored in the session cache (`:307-308`), so the crash repeats for up to 1,800 s after stdin stops sending it | `render_lane:501-502` |
| `…used_percentage` | number | int/float/bool | non-number → window unreported | `NaN` → renders `5hnan%`, colour GREY (all comparisons false) | `render_lane:503,508` |
| `…resets_at` | number, unix **seconds** | int/float/bool | non-number → absolute bands, no countdown | `<= now` → window dropped. Milliseconds (13 digits) would give elapsed < 0 → absolute bands, countdown hidden | `render_lane:504-530` |
| `cost` | object | object | `{}` | truthy non-object → **degraded** (CP-10) | `render_lane:534` |
| `cost.total_lines_added` / `_removed` | int | any; `_fmt_lines` does `int(n)` | falsy → `0`; both falsy → hidden | `"12"` → `12`; `"abc"`/array/object/NaN → `"?"`; `±Infinity` → `OverflowError` (not caught) → **degraded** (CP-11). The string `"0"` is truthy, so `▲0/▼0` shows | `render_lane:535-537`; `_fmt_lines:849-860` |
| `cost.total_duration_ms` | number | int/float | not number or ≤ 60000 → no timer (and no `⌂`) | `+Infinity` → `inf//60000 = nan` → `int()` ValueError → **degraded** (CP-12) | `render_lane:539-563` |
| `cost.total_api_duration_ms` | number | int/float | → no `·api`, no `$/h`; cost history `api_ms=None` | `+Infinity` ≥ 60000 → `_hm` ValueError → **degraded** (CP-12). `true` is stored as `api_ms: true` | `render_lane:550-553,603,622-625`; `record_cost:235` |
| `cost.total_cost_usd` | number | int/float/bool > 0 | → no `$` segment, no history write | `true` → `$1.00`, stored `usd: 1` (int) | `render_lane:601-636` |
| env `COLUMNS` | decimal string | Python `int()`: accepts whitespace, `+`, `_` digit separators, non-ASCII Unicode digits | absent or unparsable → 0 (no trimming; row 2 allowed) | negative → no trimming **and** row 2 dropped when `ROWS == 2` (`cols==0 or cols>=72` both false) | `term_cols:1185-1190`; `main:1224,1232` |

Not consumed (verified absent from the code): `version`, `output_style`, `exceeds_200k_tokens`, `context_window.total_input_tokens/total_output_tokens/current_usage` (deliberately, review #10.1), `prompt_cache.cache_write_tokens`, `LINES`. `columns`/`tasks[]` belong to `--subagent` only (out of scope, `:888-936`).

### 1.3 Locale controls stdin and stdout (new finding)

| Locale at status line start | stdin/stdout error handler | Invalid UTF-8 byte in stdin | JSON escape `\udc80`..`\udcff` in a rendered label | Other lone surrogate (`\ud800`) in a rendered label |
|---|---|---|---|---|
| `LANG=en_US.UTF-8` (no LC_ALL/LC_CTYPE) | strict | decode error → `{}` → row 1 `◨ ?`, `?` | `print` UnicodeEncodeError → **degraded** (CP-15) | **degraded** |
| `LC_ALL=C`, `LC_ALL=C.UTF-8`, `LC_CTYPE=UTF-8` (macOS) | surrogateescape | parsed. The byte becomes `\udcXX` and is re-emitted raw on stdout | raw byte `0x80..0xff` emitted | **degraded** |

[scratch-verified] `p2r1/loc.py`, all five locale settings. Claude Code (Node) writes well-formed UTF-8, but `JSON.stringify` emits lone surrogates as `\udXXX` escapes, so the right-hand columns can happen in principle. Production locale: **UNVERIFIED** (depends on the terminal: iTerm/Terminal.app often set `LC_CTYPE=UTF-8`). Owner action: capture `locale` from a status-line run, then pin the harness to the same value.

---

## 2. TARGET 2 — Transcript JSONL: record schema the incremental parser consumes

### 2.1 Framing (bytes → records)

| Rule | Detail | Line |
|---|---|---|
| Window | Read from `off` (cached `size`) up to `min(size - off, 524288)` bytes. `size` comes from `os.stat` at the start of the refresh | `:1013,1042-1044` |
| Long line (> 512 KB) | While the blob has no `\n` **and** `off + len(blob) < size` (stat size), append whole 524,288-byte chunks. The extension can include many later lines, and can read past the stat size if the file grew | `:1048-1052` |
| Commit point | `cut = blob.rfind(b"\n")`. No `\n` → return cached values (offset unchanged, **no save**). Else `off += cut + 1` | `:1055-1058` |
| Splitting | `blob[:cut].splitlines()` on **bytes** splits on `\n`, `\r`, `\r\n` only (not `\x0b`, `\x1c`, `\x85`) | `:1059`; [scratch-verified] |
| Decoding | `json.loads(line)` on bytes; encoding detection + `surrogatepass` (CONV-ABS-4). Any exception → line skipped | `:1060-1063` |
| Non-object record | a line that parses to an array/number/string/bool/null **crashes** at `e.get` → degraded, **persistently** (no save, so the same bytes are re-read every refresh) (CP-20) | `:1069` |

### 2.2 Record schema (fields read; everything else ignored)

```text
Record := object {
  type:      "assistant" | "user" | "system" | <other>           # :1069, :1088
  subtype:   "compact_boundary" (meaningful only with type=system) # :1088
  timestamp: string, ISO-8601 (Z or offset; naive = LOCAL time)  # :1069 -> _iso_ts :977-985
  message?:  object | falsy {                                    # :1071, :1096
    id?:      any truthy hashable (CC: "msg_...")                # :1072, :1098
    usage?:   object {                                           # :1097, :1079
      input_tokens?, cache_creation_input_tokens?,
      cache_read_input_tokens?, output_tokens?: number (falsy -> 0)  # :1105-1107, :1112, :1079
    }
    content?: string | array<Block>                              # :1081, :1120
  }
}
Block := object {
  type: "text"        -> text: string            # :1142-1143
      | "thinking"    -> thinking: string        # :1144-1145
      | "tool_use"    -> input: any              # :1146-1147
      | "tool_result" -> content: string | array<object|any> | other  # :1130-1141
      | "image"                                  # :1148-1149
      | <other: redacted_thinking, document, server_tool_use, ... -> ignored, counts 0>
}
```

Not read by the status line (backfill or hook only): `message.model`, `message.role`, `usage.cache_creation.ephemeral_*`, `uuid`, `parentUuid`, `isSidechain`, `isCompactSummary`, `toolUseResult`.

### 2.3 Per-record processing, in code order (one record)

1. **Turn machine** (only if `_iso_ts(timestamp)` is not None; `_iso_ts` returns None for non-strings and on `ValueError`, e.g. year 0) (`:1069-1087`):
   - `assistant` with truthy `message.id`: same id as `cur` → `cur.t1 = ts`. Otherwise finish `cur` (→ `lr`) and start `cur = {id, t0: lu, t1: ts, out: (usage or {}).output_tokens or 0}`. **`out` comes from the first line of the message.**
   - `user`: if `message.content` is not an array containing a dict with `type=="tool_result"` → finish `cur`, `cur=None`. **Always** `lu = ts`, including tool-result lines, so the next API call's `t0` = the tool-result time.
   - `system` (any subtype): finish `cur`, `cur=None`.
   - other types, and `assistant` without an id: no action.
   - `_finish_turn` (`:988-996`): keep `lr` unless `t0` is set and `0 < out`, `0 < span <= 4.0*out/15.0`. Then `lr = [out/span, out < 200]`.
2. **Compaction** (`type=="system"` and `subtype=="compact_boundary"`, timestamp not required): `res=conv=think=0`, `pp=None`, then `continue`, which skips usage and composition for this line. Totals (`tin,tout,c_in,c_wr,c_rd,rb`) and the id memory are **not** reset (`:1088-1095`).
3. **Usage** (any record type that has `message.usage` as an object) (`:1096-1119`):
   - Dedup: if `message.id` is truthy and already in `seen_ids` → ignored. Otherwise the id is added to `seen_ids` and appended to `recent_ids`. Usage without an id is always counted. An id is marked seen only on a line whose usage is an object.
   - `tin += i+w+r; c_in += i; c_wr += w; c_rd += r; tout += out` (falsy → 0; floats propagate into the cache; strings crash, CP-22).
   - Rebuild: `prompt = i+w+r`; if `pp is not None and w - max(0, prompt - pp) > 20000` → `rb += 1`; then `pp = prompt`.
4. **Composition** (`message.content`, any record type) (`:1120-1149`):
   - `str` → `conv += len(content)` (code points), then `continue`.
   - `list` → per dict block:
     - `tool_result`: str → `len`; list → Σ(`2000` if item is a dict with `type=="image"`, else `len(json.dumps(item))`); other non-null → `len(json.dumps(x))`; null → 0. **→ `res`**
     - `text` → `conv += len(text or "")`.
     - `thinking` → `think += len(thinking or "")`.
     - `tool_use` → `conv += len(json.dumps(input or ""))` (`{}` → `'""'` = 2).
     - `image` → `res += 2000`. A user-pasted image lands in **▤ tool results**, whatever its role.
     - Every other type contributes nothing. `redacted_thinking` is counted **nowhere**.
   - `text`/`thinking` values that are truthy non-strings: arrays/objects count `len()` (items/keys); numbers/`true` → TypeError → **degraded**, persistent (CP-26).

### 2.4 Measurement-unit hazards for Go (byte parity of the percentages)

- `len(str)` = Unicode code points (a decoded `😀` pair = 1; a lone `\ud800` = 1).
- `json.dumps` output length depends on: `ensure_ascii` (BMP non-ASCII = 6 chars, astral = 12 chars), separators `", "`/`": "`, insertion key order as parsed, float repr (`1.0`, `1e-05`, `1e+16`), `NaN`/`Infinity` tokens, big ints exact, and `1E400` re-encoding as `Infinity` [scratch-verified].
- A lone surrogate re-encodes to `"\ud800"` (6 chars). If Go decodes it to U+FFFD and emits `"�"`, that is also 6 chars, so the lengths match by luck.
- `tool_result` content as an **array of text blocks** is measured as JSON (keys included, escaped). As a **string** it is measured raw. Go has to keep the two paths separate.

### 2.5 Dedup and the id memory, exactly

- Load: `recent_ids = list(c["ids"])` unless a reset is pending (`:1033`). `seen_ids = set(recent_ids)`. Within one refresh `seen_ids` grows without bound. Only the last 256 of `recent_ids` are saved (`:1153`).
- Consequence: an id seen again after more than 256 newer ids, across refresh boundaries, is double counted. Within one refresh it never is.
- `ids` stores whatever type `message.id` had (normally str).

---

## 3. TARGET 3 — Cache files as exact wire formats

### 3.1 Shared writer and reader (all four files)

| Aspect | Rule | Line |
|---|---|---|
| Directory | `CACHE_DIR = expanduser("~/.cache/dgx-llm")`, i.e. from `$HOME` (Windows: `%USERPROFILE%`). Created with `makedirs(exist_ok=True)` on every save | `:78,200` |
| Atomic write | `mkstemp(dir=CACHE_DIR, prefix=<basename>+".")` → temp `<basename>.XXXXXXXX` (8 random chars), **mode 0600** → `json.dump` → `os.replace`. All errors swallowed. A failed replace leaks the temp file | `:198-206`; [scratch-verified] name `statusline-x.json.e76h4hgt`, `0o600` |
| Encoding | `json.dump` defaults: separators `", "`/`": "`, `ensure_ascii=True`, `allow_nan=True` (**`NaN`, `Infinity` are written as bare tokens**), insertion key order, float `repr`, no trailing newline | `:203` |
| Reader | `json.load(open(path))` (locale text mode). **Any** exception → `{}`. Valid JSON of the wrong shape is returned as-is (§5) | `:190-195` |
| Concurrency | last writer wins. Every writer re-reads first (merge-by-reload), except the mix cache, which is a full rewrite | — |

### 3.2 `statusline-<sid>.json` (session cache)

Filename: `f"statusline-{sid}.json"` with `sid = session_id or "nosession"`, **raw `str()`**, no sanitizing (`:1214-1215`). A `/` in the sid points into a non-existent subdirectory, so the replace fails silently. Then the file never persists: the VM is fetched on every refresh, there is no rl smoothing, and `ps` is walked every time.

| Key | Type | Written by (line) | When | Read by |
|---|---|---|---|---|
| `rl` | object (stdin `rate_limits` verbatim) | `effective_rl:307` | stdin `rate_limits` is a non-empty object | `effective_rl:311` |
| `rl_ts` | float unix | `effective_rl:307` | with `rl` | `:311-312` (`< 1800`) |
| `fetch_ts` | float unix | `get_sample:349` (success), `:353` (failure) | TTL expired and `ROWS >= 2` | `:324` (`fetch_ts > now - TTL` → reuse) |
| `up` | bool | `:349` (`true`), `:354` (`false`) | same | `:325` |
| `ts` | float unix (last **good** sample) | `:349` only | success | `:325` (age), `:356` |
| `sample` | object `{name: float}` (may contain `NaN`/`Infinity`) | `:349` | success (kept on failure) | `:325,357` |
| `hist` | array of points, ≤ 32 | `:349-350` | success (failure keeps the old array **unnormalized**) | `:325,335,358` |
| `proc_start` | float unix (`time.mktime`, so always `.0`) | `claude_window_start:287-288` | first successful `ps` walk per session | `:274-275` |
| `sess_state` | retired | popped at `:328` | fetch path only | — |
| any other key | preserved | `entry = dict(c)` (`:327`) | — | — |

Point object (sparkline history), key order as built (`:338-347`): `t` (float), `v`, `k`, `f`, then `v` **again in last position** when it came from the 5-minute fallback (order then `t,k,f,v`), then `p: 1` (int) if preemption > 0. Missing series → key omitted. Legacy `[ts, rate]` points are normalized to `{"t","v"}` on the next successful fetch only (`:335,652-656`).
File key order: insertion order across the refresh's three load→save cycles. Example of a first run with stdin rl and a working VM: `rl, rl_ts, fetch_ts, up, ts, sample, hist, proc_start`. Updating existing keys keeps their position.

TTLs / retention: fetch 4 s (`>` strict, `:324`); stale-display bound 300 s (`<`, `:357`, **not applied on the cached path**, BC-SL-041); green bound 15 s (`>` = stale, `:697`); hist age 90 s (`<` kept, `:336`), min gap 2 s (`>=`, `:337`), cap 32 (`:350`); rl 1800 s (`<`, `:312`); `proc_start` never expires. Failed `ps` walks are not cached.

### 3.3 `statusline-mix-<key>.json` (parse state)

Filename key: `re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "nosession")[:40]` (`:1016-1017`). Every sid-less invocation shares `statusline-mix-nosession.json`, even across different transcripts: the parse resumes at the old offset in the other file whenever `size >= off`.

Always a **full rewrite with this exact key order** (`:1150-1153`):

| # | Key | Type | Meaning |
|---|---|---|---|
| 1 | `size` | int | byte offset just past the last parsed `\n` (not the file size) |
| 2-4 | `res`, `conv`, `think` | int | composition counts in characters since the last `compact_boundary` |
| 5-8 | `tin`, `tout`, `c_wr`, `c_rd` | int (float if the transcript had floats) | session totals |
| 9 | `mixv6` | `1` | schema marker (presence is what counts, not the value) |
| 10-11 | `c_in`, `rb` | int | fresh input; rebuild count |
| 12 | `pp` | int \| null | previous call's prompt size (null after compaction or reset) |
| 13 | `ids` | array (≤ 256) | recent message ids |
| 14 | `lr` | null \| `[float, bool]` | last-turn `[rate, dim]` |
| 15 | `lu` | float \| null | last user-line timestamp |
| 16 | `cur` | null \| `{"id", "t0": float\|null, "t1": float, "out": number}` | unfinished message (persisted unfinished) |

Write timing: only when at least one complete new line exists (`cut >= 0`). **Not** written when `size == off`, when no `\n` is found, on read OSError, or when the parse crashes. The write still happens if every new line was unparseable.
Reset (migration): if any of `tin`, `c_wr`, `mixv6` is **absent** while `off > 0`, or `size < off` → all accumulators and the id memory are zeroed and the parse restarts at 0 (`:1025-1038`). Older markers (`mixv2`.. per review #6/#10) are simply dropped by the full rewrite. Edge: a cache without `size` gives `off = 0` and no reset, so the cached accumulators are kept and the file is re-added on top (double count; corruption only).
TTL: none (driven by the offset).

### 3.4 `statusline-git-<hash>.json`

Key: `sha1(directory.encode("utf-8", "replace")).hexdigest()[:16]` of the **raw** project-dir string (not normalized: `/x/p` and `/x/p/` are different files; a lone surrogate hashes as `?`) (`:405`; [scratch-verified] identical digests). Content `{"ts": float, "branch": str}` (branch may be `""`), full rewrite (`:410-411`). Recompute when `now - ts > 5` (strict) or `branch` is absent (`:409`). Disabled entirely when `DGX_SL_GIT == "0"` (`:400`). HEAD content not under `refs/heads/` shows its first 7 chars (`ref: refs/tags/v1` → `ref: re`) [scratch-verified].

### 3.5 `cost-history.json`

```text
{ "sessions": { "<sid>": { "lane": "dgx"|"anth", "usd": number, "api_ms": number|bool|null,
                           "ts": float, "src": "cc"|"backfill" } }, <other top-level keys preserved> }
```

| Writer | Rule | Line |
|---|---|---|
| status line `record_cost` | needs truthy sid, lane in {dgx, anth}, numeric usd. Skip if the existing entry has `src=="cc"` and `now - ts < 60` (strict). Otherwise set `{lane, usd: round(usd,4), api_ms if numeric else None, ts: now, src: "cc"}` (this key order) and save via `save_cache` (temp prefix `cost-history.json.`). `round(5,4)` stays the int `5` → JSON `5` | `:224-237`; [scratch-verified] |
| backfill | same key order, `ts` = the last transcript timestamp, `src: "backfill"`, temp prefix `cost-history.` (different), skips sids whose entry has `src=="cc"` | backfill `:101-116` |
| reader `cost_thresholds` | excludes `k == sid` (stdin value), other lanes, `now - ts > 30 d`, non-numeric or < $1 | `:243-262` |

No pruning: entries older than 30 days stay in the file forever (an unbounded-growth NFR gap). `ts` of a `cc` record is its **last update**, so the 30-day window is measured from the last refresh of that session. Corruption: a parse failure → `{}`, and the next write **replaces the whole history** with one session (also true for backfill, `:90-93`).

### 3.6 Side-effect order of one refresh (matters when a later step crashes)

1. mix cache save (`:1213` → `:1150`)
2. session cache `rl` save (`:1216`, only if stdin rl is non-empty)
3. session cache sample save (`:1218`, only if `ROWS >= 2` and TTL expired)
4. `proc_start` save (`:1229`, first walk only)
5. git cache save (`:455` → `:411`)
6. cost-history save (`:606`)

A crash at step k leaves the saves of steps 1..k-1 on disk. Byte parity of caches **after a degraded refresh** requires the same order. Claude Code cancels in-flight runs when a newer trigger arrives, so a run can also be killed between any two steps. Atomicity is per file only.

---

## 4. TARGET 4 — VictoriaMetrics response consumed and the TelemetrySample entity

### 4.1 Request

`GET {VM_URL}/api/v1/query?query={quote(QUERY, safe='')}`, proxies disabled, timeout 1.5 s, body read whole (no size cap) (`:165-171`).

### 4.2 Response JSON paths actually read (`fetch_sample:172-185`)

| Path | Use | Failure behavior |
|---|---|---|
| `.status` | must equal `"success"` | otherwise → `None` (fetch failure). Top-level non-object → AttributeError → outer `except` → `None` |
| `.data.result` | iterated | missing → KeyError → `None`. An object here iterates its keys → TypeError → `None` |
| `.data.result[i].metric` | object | **missing in any one series → the whole fetch fails** (KeyError outside the inner try) |
| `.data.result[i].metric.__name__` | name (default `""`; empty names skipped) | — |
| `.data.result[i].metric.job` | only when `__name__=="up"` → key `up:<job>` (missing job → `up:`) | — |
| `.data.result[i].value[1]` | `float()` of a string or number (`"NaN"`, `"+Inf"` accepted) | KeyError / ValueError / IndexError → that series skipped. **TypeError** (e.g. `value: null`) → whole fetch fails |

`resultType` is never checked: a `matrix` result has `values`, so every series is skipped and the result is `None`; a `scalar` result → TypeError → `None`. Non-2xx HTTP → `HTTPError` → `None`.

### 4.3 TelemetrySample entity

`map[string]float64`, key = `__name__` or `up:<job>`, **first value per key wins** in VM result order (`:183`), an empty map → `None`. Keys consumed by the status line (the full list is in Pass 1 §4.6). Per-key NaN behavior, a new finding (VM may or may not emit NaN; review #18.4 treats it as hypothetical):

| Key | NaN effect | Line |
|---|---|---|
| `vllm:kv_cache_usage_perc` | `math.ceil(nan)` ValueError → **degraded** on fresh **and** stale paths (CP-40) | `:758-759`; [scratch-verified] |
| sparkline trace value (`v`/`k`/`f` in the last 12 points) | `idx(nan)` → `int(nan)` ValueError → **degraded** (fresh path, sparkline on). Notably `DGX_SL_TRACE=ttft` with the expected no-data TTFT NaN would degrade every fresh refresh (CP-41) | `:673-675` |
| `dgx_ttft:p95_30m` | explicitly hidden | `:793` |
| `dgx_kv:host_hit_share` | comparisons false → `↺host` hidden, KV stays CYAN | `:756-763` |
| running/waiting, power, temp, rates | rendered as text `nan` (`rnan·q0`, `⚡nanW`, `nan¢/h`) | `:741,813-819,783` |
| `dgx_cost:dgx_usd_per_mtok`, `dgx_tokens:rate_mtok_month` | `⛏n/a` | `:1221,628-631` |
| `dgx_llm_last_dgx_request_timestamp_seconds` | idle hidden | `:825` |

Derived entities: **HistoryPoint** (§3.2) and the **health verdict** (`serving_state`, `:705-722`). `sample` is persisted with `NaN` tokens when present, so Go's cache reader and writer must accept and produce `NaN`/`Infinity`.

---

## 5. Crash-path catalogue (the owner requires byte-exact degraded output)

**Degraded output** (every row below except CP-90): stdout is exactly `\x1b[90mstatusline degraded\x1b[0m\n`, exit 0 (`:1243-1245`). No partial output can come first: there is one `print` (`:1234`), and its encode failure happens before any byte is written. Cache saves already made persist (§3.6).

| ID | Trigger | Raising line | Persistent across refreshes? |
|---|---|---|---|
| CP-01..05, 08, 10 | `model` / `model.id` (prefixes set) / `workspace` / project dir / `context_window` / `prompt_cache` / `cost` mistyped (§1.2) | `:442,446,452,405 or 460,419,477,535` | only while stdin keeps it |
| CP-06 | `context_window.used_percentage` = NaN | `:426` | stdin |
| CP-07 | `context_window_size` truthy non-number while pct numeric | `:435` | stdin |
| CP-09 | `rate_limits.<window>` truthy non-object | `:502` | **yes, ≤ 1,800 s** via cached `rl` |
| CP-11 | `cost.total_lines_*` = ±Infinity | `:853` (OverflowError not caught) | stdin |
| CP-12 | `total_duration_ms` = +Inf, or `total_api_duration_ms` = +Inf while duration > 60 s | `:546` | stdin |
| CP-13a / b | non-string truthy `session_id` + existing transcript / unhashable sid + cost > 0 + lane | `:1017` / `:230` | stdin |
| CP-14 | `transcript_path` array/object/float | `:1010` | stdin |
| CP-15 | a rendered label holds a lone surrogate (locale-dependent, §1.3) | `:1234` | stdin |
| CP-20 | transcript line is valid JSON but not an object | `:1069` | **yes, permanent for the session** (offset never advances) |
| CP-21 | `message` truthy non-object | `:1071` / `:1097` | permanent |
| CP-22 | usage token value is a string (or other non-number truthy) | `:1108` | permanent |
| CP-23 | `message.id` unhashable while `usage` is an object | `:1099` | permanent |
| CP-24 | assistant with a new id, timestamp, and `usage` truthy non-object | `:1079` | permanent |
| CP-25 | `output_tokens` non-numeric truthy on a message's first line → crash when that turn is finished | `:994` | permanent |
| CP-26 | block `text`/`thinking` is a number or `true` | `:1143,1145` | permanent |
| CP-30 | session cache is valid JSON but not an object | `:307` or `:311` | until the file is replaced |
| CP-31 | session cache `rl_ts`/`fetch_ts`/`ts` non-numeric; `hist` point is a short list or has a non-numeric `t` (fetch path) | `:312,324,325/356,335-337` | yes |
| CP-32 | mix cache not an object / non-numeric counters / non-iterable `ids` / unhashable ids / truthy non-object `cur` | `:1019,1035,1033,1034,1074` | yes |
| CP-33 | git cache not an object / non-numeric `ts` | `:409` | ≤ until recomputed (never, since it crashes first) |
| CP-34 | cost-history not an object / `sessions` truthy non-object / entry non-object / entry `ts` non-numeric | `:229-232,245-246` | yes |
| CP-40 | sample `vllm:kv_cache_usage_perc` = NaN | `:759` | while cached (≤ TTL) or re-fetched |
| CP-41 | NaN (or +Inf) trace value among the last 12 history points | `:675` | ≤ 90 s (history age) |
| **CP-90** | **import time**: `DGX_SL_TTL` not `float()`-parsable, `DGX_SL_ROWS` not `int()`-parsable (e.g. `"2.0"`) | `:74-75` | **Not degraded:** Python traceback on stderr, **empty stdout, exit 1** (Claude Code shows a blank line) |

Parse rules that are **not** crashes (Go must not "fix" them into crashes): bad timestamps (→ no turn action), invalid UTF-8 lines and >4,300-digit integers (→ line skipped), `display_name` of any type (`str()`), `_fmt_lines` failures (→ `?`), missing VM keys.

---

## 6. TARGET 5 — CONFIG entity (D15): env vars, statusline literals, named constants

Proposed resolution order (PLAN §6, D15): config file → `HYLO_<UPPER_SNAKE_OF_KEY>` → legacy `DGX_*` alias → built-in default = legacy value. Types are hylo types. "Parse" notes record legacy parsing that parity has to reproduce. Rationale codes refer to Pass 4 T-ids. UNKNOWN = owner to confirm.

### 6.1 The 40 legacy env inputs

| # | Legacy env | Proposed key | Type | Default (= legacy) | Consumer (legacy) | Disposition / rationale |
|---|---|---|---|---|---|---|
| 1 | `LOCAL_MODEL_PREFIXES` | `routing.local_model_prefixes` | list[string] | `["claude-sonnet"]` (proxy `dgx_proxy.py:86`, backfill `:89`). Status line default is `[]` (`:444`), and the launcher forces `claude-sonnet` (`claude-dgx:38`) | proxy, statusline `:444`, backfill, launcher | config; one key replaces three defaults. Parity note: the harness must set it explicitly, because an unset value gives the status line `◨ ?`. Parse: comma split, strip, drop empty; case-sensitive `startswith` |
| 2 | `DGX_SERVED_MODEL` | `backend.served_model` | string | `claude-sonnet-5-5` | proxy `:84` | config (owner serving alias) |
| 3 | `DGX_UPSTREAM` | `backend.url` | URL | `http://192.0.2.10:8080` (scrubbed placeholder) | proxy `:79`, launcher `:63` | config. Default is a documentation IP, so recommend required/no default after parity (D15: no hard-coded host) |
| 4 | `DGX_KEY_FILE` | `backend.api_key_file` | path | `~/.config/dgx-llm/api-key` | proxy `:88` | config (secret by file, PLAN §6) |
| 5 | `DGX_OBS_LEDGER` | `paths.ledger` | path | `~/dgx-llm-obs.jsonl` | proxy `:54`, exporter `:22` | config (the path; the format is a D7 constant) |
| 6 | `DGX_PROXY_DECISIONS` | `paths.decision_log` | path | `~/dgx-llm-routing-decisions.log` | proxy `:53` | config |
| 7 | `DGX_TRUST_STATE` | `paths.ca_state` | path | `~/.dgx/trust-state.json` | trust CLI `:563` | config |
| 8 | `DGX_PROXY_RESTART_CMD` | `ca.restart_command` | string | unset | trust rotate `:719` | likely obsolete (mitmproxy-specific); keep only if `hylo ca rotate` needs it |
| 9 | `DGX_SL_VM_URL` | `statusline.telemetry.url` | URL | `http://192.0.2.10:8428` (trailing `/` stripped) | `:73` | config (D15 host) |
| 10 | `DGX_SL_TTL` | `statusline.telemetry.ttl_s` | float | `4` | `:74` | D: match `refreshInterval` (T-001). Parse: Python `float()` accepts `nan`/`inf`/`_`. A bad value **crashes at import** (CP-90) |
| 11 | `DGX_SL_ROWS` | `statusline.rows` | int | `2` | `:75` | C (T-002). Parse: Python `int()`; bad value → CP-90 |
| 12 | `DGX_SL_SPARK` | `statusline.sparkline.enabled` | bool | `true` (anything but `"0"`) | `:76` | config toggle |
| 13 | `DGX_SL_GIT` | `statusline.git.enabled` | bool | `true` (anything but `"0"`) | `:77` | config toggle |
| 14 | `DGX_SL_TRACE` | `statusline.sparkline.trace` | enum `rate\|kv\|ttft` | `rate` (unknown → `rate`) | `:89,662` | config (review #17) |
| 15 | `COLUMNS` | — (**not config**) | — | — | `:1186` | Claude Code runtime input (protocol). Keep reading the env var; reproduce Python `int()` parsing |
| 16 | `DGX_FAKESTOP_LOG` | `paths.hook_log` | path | `~/.cache/dgx-llm/auto-continue.log` | exporter `:23` (reader only). The writer hard-codes the same path (`auto_continue.py:196`) | config; one key for writer and reader (legacy can diverge) |
| 17 | `DGX_SESSION_LIMIT` | `exporter.session_limit` | int | `50` | exporter `:24` | UNKNOWN (T-077) |
| 18 | `DGX_LEDGER_EXPORTER_PORT` | `exporter.port` (+ `exporter.bind` = `0.0.0.0`, hard-coded at `:414`) | int / host | `9210` / `0.0.0.0` | exporter `:25,414` | UNKNOWN (T-078); bind is a security gap (Pass 4) |
| 19 | `DGX_KEV_URL` | `hook.kev.url` | URL | `http://192.0.2.10:8008/v1/systemone` | hook `:31`, launcher `:154` | config (D11 optional) |
| 20 | `DGX_KEV_MODEL` | `hook.kev.model` | string | hook `kev-latest` (`:32`); launcher exports a pinned kev-4b id (`claude-dgx:155`) | hook, launcher | config; two legacy defaults. The effective one is the launcher's |
| 21 | `DGX_KEV_THRESHOLD` | `hook.kev.threshold` | float | `0.40` | hook `:33`, launcher `:152` | D: tuned 2026-11-10 (T-082) |
| 22 | `DGX_KEV_TIMEOUT` | `hook.kev.timeout_s` | float | `2.5` | hook `:34` | UNKNOWN (T-083) |
| 23 | `DGX_KEV_MESSAGES` | — (drop) | int | `14` | hook `:35` (never used) | dead (T-084). Document it as accepted but ignored during parity |
| 24 | `DGX_KEV_CHARS` | `hook.kev.state_chars` | int | `6000` | hook `:36` | UNKNOWN (T-085) |
| 25 | `DGX_KEV_API_KEY` | `hook.kev.api_key_file` | path | `~/.config/dgx-llm/kev-api-key` | hook `:97-102` | legacy env carries the **value**; PLAN §6 says secrets by file → accept the env value only as a deprecated alias |
| 26 | `DGX_ENGLISH` | `hook.english.enabled` | bool | `true` (≠ `"0"`) | hook `:217`, launcher `:136,148,157` | config |
| 27 | `DGX_AUTOCONTINUE` | `hook.autocontinue.enabled` | bool | `true` (≠ `"0"`) | hook `:228`, launcher `:148,160` | config |
| 28 | `DGX_INVISIBLE` | — (drop) | — | `1` | launcher | D6: invisible mode only |
| 29 | `ROUTER_PORT` | — (drop) | — | unset | launcher `:17` | D6 |
| 30 | `DGX_USER` | `attribution.user` | string | OS username (`whoami`) | launcher `:43` | config |
| 31 | `ANTHROPIC_CUSTOM_HEADERS` | — (**not config**) | — | — | launcher `:46-53` | Claude Code protocol env; hylo appends to it |
| 32 | `DGX_SKIP_PREFLIGHT` | `run.preflight` | bool | `true` (legacy skips iff `=1`) | launcher `:60` | config |
| 33 | `DGX_PROFILE` | `profiles.<name>` (hylo profiles) | path → profile | `~/.config/dgx-llm/profile.env` | launcher `:114` | replaced by hylo profiles. Note the BC-LN-006 ordering quirk |
| 34 | `DGX_MAIN_MODEL` | `run.main_model` | string | `sonnet` (`opus` recognized) | launcher `:128` | config |
| 35 | `DGX_REMOTE` | `run.remote_control` | bool | `false` | launcher `:133` | config |
| 36 | `DGX_SAFE` | `run.skip_permissions` | bool | `true` (legacy: `DGX_SAFE=1` disables) | launcher `:139` | config (owner choice) |
| 37 | `DGX_SANDBOX` | `run.sandbox` | bool | `false` | launcher `:165` | config (owner choice 2026-11-05) |
| 38 | `DGX_STATUSLINE` | `run.statusline.enabled` | bool | `true` | launcher `:175` | config |
| 39 | `DGX_PRINT_ARGS` | — (CLI flag `hylo run --print-args`) | — | off | launcher `:182` | an action, not behavior configuration |
| 40 | `TMPDIR` | `paths.proxy_log_dir` (default `$TMPDIR`, else `/tmp`) | path | `${TMPDIR:-/tmp}` | launcher `:23,74` | OS input. The log directory becomes config |

### 6.2 Status line behavior-shaping literals → config keys (defaults = legacy, `dgx_statusline.py`)

| Key | Type | Default | Line | Rationale |
|---|---|---|---|---|
| `paths.cache_dir` | path | `~/.cache/dgx-llm` | `:78` | config (the file **names** are constants, §6.3) |
| `statusline.telemetry.fresh_s` | float | 15 | `:79` | UNKNOWN (T-003) |
| `statusline.telemetry.keep_dead_s` | float | 300 | `:80` | UNKNOWN (T-004) |
| `statusline.telemetry.timeout_s` | float | 1.5 | `:81` | UNKNOWN (T-005) |
| `statusline.telemetry.query` | string | the verbatim MetricsQL of `:102-123` | `:102-123` | config (D15/P6 pluggable telemetry). Parity: byte-identical default |
| `statusline.telemetry.series.<role>` | map role → metric name | 16 names + `dgx_sl:gen_rate1m`, `dgx_sl:ttft_n30m`, `up:vllm`, `up:lmcache`, `vllm:` prefix | `:339-346,716-720,732-824,1220-1223` | config: binds widgets to the query's series |
| `statusline.sparkline.points` | int | 12 | `:82` | J (T-006) |
| `statusline.sparkline.max_age_s` | float | 90 | `:83` | UNKNOWN (T-007) |
| `statusline.sparkline.min_gap_s` | float | 2 | `:84` | UNKNOWN (T-008) |
| `statusline.sparkline.history_cap` | int | 32 | `:350` | UNKNOWN (T-009) |
| `statusline.sparkline.scale` | map | `k` fixed 1.0; floors `v` 1.0, `f` 0.1, else 1e-9 | `:648-649,671` | D (T-045) |
| `statusline.sparkline.colors` | RGB set | trail (70,170,190), fade 0.55→1.0, preempt (220,170,60), head (140,235,255) | `:680-689` | UNKNOWN (T-046) |
| `statusline.limits.keep_s` | float | 1800 | `:85` | UNKNOWN (T-010) |
| `statusline.limits.windows` | list `{label,key,length_s}` | `5h/five_hour/18000`, `7d/seven_day/604800` | `:501` | C (T-031). The labels are plain text on purpose (`:482-483`) |
| `statusline.limits.projection_min_elapsed` | float | 0.10 | `:517` | D (T-032) |
| `statusline.limits.projected_bands` | `{yellow: 80 (>=), red: 100 (>)}` | | `:519` | D (T-033) |
| `statusline.limits.absolute_bands` | `{yellow: 70 (>), red: 90 (>)}` | | `:521` | D (T-034) |
| `statusline.limits.countdown_max_factor` | float | 1.15 | `:523` | UNKNOWN (T-035) |
| `statusline.limits.reroute_all_prefixes` | list | `["claude", "claude-"]` (after `rstrip("*")`) | `:487-488` | config (routing semantics) |
| `statusline.idle.after_s` | float | 300 | `:93` | J (T-011) |
| `statusline.cost.basis_min_mtok_month` | float | 30.4 | `:98` | D (T-012) |
| `statusline.cost.basis_min_shown_usd` | float | 0.005 | `:634` | D (T-044) |
| `statusline.git.ttl_s` | float | 5 | `:99` | C (T-013) |
| `statusline.narrow_cols` | int | 72 | `:100` | UNKNOWN (T-014) |
| `statusline.ttft.min_samples` | int | 20 | `:124` | D (T-015) |
| `statusline.ttft.yellow_s` / `integer_from_s` | float | 8 / 10 | `:795,799` | D (T-052, T-051) |
| `statusline.cost.window_s` | int | 2,592,000 (30 d) | `:218` | D (T-018) |
| `statusline.cost.min_usd` | float | 1.0 | `:219` | D (T-019) |
| `statusline.cost.min_sessions` | int | 10 | `:220` | D (T-020) |
| `statusline.cost.cold_yellow_usd` | float | 25.0 | `:221` | D (T-021) |
| `statusline.cost.record_throttle_s` | float | 60 | `:232` | UNKNOWN (T-022) |
| `statusline.cost.rate_min_api_ms` | `{cc: 300000, backfill: 1800000}` | | `:253` | D (T-023) |
| `statusline.cost.percentiles` | `[0.75, 0.95]`, index `int(q*(n-1))` | | `:261` | D / method UNKNOWN (T-024) |
| `statusline.cost.burn_min_api_ms` | int | 300000 | `:622` | D (T-043) |
| `statusline.window_age.enabled` | bool | `true` | `:1229` | config. Owner: **Go may add `⌂` on Windows** (legacy always yields None there: no `ps`) |
| `statusline.window_age.process_name` | string | `claude` | `:285` | config (a renamed Claude Code binary would break it) |
| `statusline.window_age.max_depth` / `ps_timeout_s` | int / float | 6 / 1 | `:279,281` | UNKNOWN (T-025/T-026) |
| `statusline.window_age.min_margin_ms` | int | 300000 | `:559` | D/J (T-040) |
| `statusline.context.cells` / `plain_max` / `red_from` | int / float / float | 10 / 50 (`>` heat) / 85 (`>=`) | `:426-434` | D (T-027/T-028) |
| `statusline.theme.heat` | `{hue_max: 0.22, s: 0.85, v: 0.80}` | | `:146-147` | UNKNOWN aesthetic (T-030) |
| `statusline.timer.min_ms` / `api_min_ms` | int | 60000 (`>`) / 60000 (`>=`) | `:540,551` | UNKNOWN (T-038/T-039) |
| `statusline.units.lines` | `{k_from: 10000, M_from: 1e6}` | | `:856-859` | D (T-037) |
| `statusline.units.tokens` | `{k_from: 1000, M_from: 1e6}` | | `:869-873` | D (T-042) |
| `statusline.queue.yellow` | rule `q>0 or preempt>0` | | `:740` | D (T-047) |
| `statusline.kv.cells` / `host_yellow_pct` / `host_shown_pct` | 4 / 5 / 0.5 | | `:759-763` | D / D (external doc) / UNKNOWN (T-048..T-050) |
| `statusline.power.wall_yellow_w` / `wall_red_w` | 1280 / 1520 | | `:812` | D (T-053) |
| `statusline.transcript.read_cap_bytes` | int | 524288 | `:952` | UNKNOWN (T-054) |
| `statusline.turn.dim_below_out` | int | 200 | `:967` | D (T-055) |
| `statusline.turn.floor_tps` / `stale_factor` | float | 15 / 4 | `:973-974` | D / J (T-057/T-058) |
| `statusline.tokens.rebuild_excess` | int | 20000 | `:972` | D (T-056) |
| `statusline.composition.image_chars` | int | 2000 | `:1137,1149` | UNKNOWN (T-059) |
| `statusline.transcript.dedup_memory` | int | 256 | `:1153` | UNKNOWN (T-060) |
| `statusline.theme.*` | ANSI SGR strings | `WHITE 97, CYAN 36, GREEN 32, YELLOW 33, RED 31, GREY 90, MAGENTA 35, BOLDRED 1;91, DIM 2, BOLD 1`; pills `106;30;1` / `105;30;1` / `100;37;1` | `:127-134` | D15 lists "colors" as config |
| `statusline.theme.glyphs` | map | `◨ ⎇ ▰ ▱ ▤ ❙ ◈ ♻ ▲ ▼ ⏱ ⌂ ↑ ✍ ⟳ ↓ ↻ ⛏ ◉ ◌ » ▣ ◔ ⚡ ☾ ▁…█` | throughout | judgment: presentation, config-able. Widths stay 1 code point each, so `trim_to_fit` is unaffected |

### 6.3 Keep as named constants (D15 exception), with the reason

| Constant | Value | Line | Why not config |
|---|---|---|---|
| Stdin field paths | §1.2 | — | Claude Code protocol |
| Transcript field names and block types | §2.2 | — | Claude Code file format |
| VM API path + response paths | `/api/v1/query`, `status`, `data.result[].metric/value` | `:165,172-185` | Prometheus HTTP API protocol |
| Cache file **names** and **keys**, `mixv6` marker, `"nosession"`, the sid sanitizer regex and `[:40]`, sha1`[:16]` | §3 | `:951,1016-1017,405,1214-1215` | file format shared by Python and Go during shadow/cutover (D4/D7 spirit) |
| cost-history lane ids `dgx`/`anth`, `src` `cc`/`backfill` | — | `:604,236`; backfill `:108` | file format shared with backfill |
| Degraded text | `GREY + "statusline degraded" + RESET` | `:1244` | owner: byte-exact crash-path contract |
| Segment separator `SEP` | `DIM + " · " + RESET` | `:128` | structural delimiter: `trim_to_fit` splits rows on it (`:1195-1196`) |
| ANSI-strip grammar | `\033\[[0-9;]*m` | `:137` | defines visible width; tied to the SGR form |
| Detached-HEAD length, `ref: refs/heads/`, `gitdir:` | 7 / literals | `:382-389` | git on-disk format |
| Unit conversions | 60000 ms/min, 3600/86400 s, 1440 min/day, 1e6 MTok, 3.6e6 ms/h | throughout | arithmetic, not policy |
| Trace key letters `v/k/f/p` and trace names `rate/kv/ttft` | `:644` | — | history-point format |

---

## 7. TARGET 6 — Cross-pass inconsistencies resolved against the source

| # | Ground truth | Evidence |
|---|---|---|
| **I2** (SSE tap docstring vs code) | **Confirmed, and made precise.** `usage` = `(in, out)` is set **only** from an event whose **top-level** `usage` object contains the key `input_tokens`. The last such event wins. `message_start` keeps usage under `message.usage`, so it never sets `usage`. Cache maxima (`_read/_write/_w1h`) come from **both** top-level and `message.usage` (`:421-424`). Stop reason comes from `delta.stop_reason`. The docstring's "usage from message_start/message_delta" is true only for the cache maxima. Consequence: the `*_usage` ledger events exist only when the upstream's `message_delta` carries `input_tokens`. Indirect evidence that both upstreams do: the cache-split comment says "message_delta repeats the write total" (`:373-376`), and the exporter's token metrics feed the `⛏` basis that the review measured live. Still LOW until a real SSE capture exists. The regex needs `data: ` **with** a space (`:413`) | `dgx_proxy.py:362-427` |
| **I6** (account-hint fallbacks) | Two inputs differ. (a) A string holding valid JSON that is **not an object** (e.g. `"123"`, `"null"`, `"[1]"`): proxy `_account_hint` → raw `[:8]` (`:335`), exporter `_account_device` → `("unknown","unknown")` (no branch). (b) A JSON **object** value (not a string): proxy → `"unknown"` (`:336`), exporter → `account_uuid[:8]` (`:88-90`). Invalid JSON gives `raw[:8]` in both (the exporter's `len>8` split is equivalent). Falsy gives `unknown` in both. Proxy-only crash: a JSON-object string whose `account_uuid` is a truthy non-string → slicing TypeError inside the response hook (`:332`, only ValueError is caught). Effect: for case (a), `dgx_llm_requests_total{account}` (exporter-derived from `dgx_request.meta_user_id`, `:185`) ≠ `dgx_llm_tokens_*{account}` (from proxy-written `dgx_usage.account`, `dgx_proxy.py:277`). D7 freezes both | `dgx_proxy.py:250,277,326-336`; exporter `:75-91,185` |
| **I7** (stale-span rule) | **Confirmed, with more differences.** Status line: valid iff `out > 0` and `0 < span <= 4.0*out/15.0`. Backfill: counted iff `t0 is not None` and `0 < span <= 4*max(o,1)/15`, so `out=0` messages count spans up to 0.2667 s. Further divergences: (1) backfill keys messages by id over the **whole file**, so a reappearing id extends the original `t1`; the status line starts a new turn when another id intervened. (2) Backfill updates `t1` only on assistant lines that have an object `usage`; the status line updates it on any assistant line with that id. (3) Backfill's `ts()` raises on a bad timestamp: the uncaught `ValueError` aborts the whole backfill (`:39,52`), whereas the status line skips the line. (4) Backfill decodes `errors="replace"` and parses a trailing partial line. (5) Lane tie or all-zero → `dgx` (`max` over the dict order `dgx, anth`) | `dgx_statusline.py:988-996,1069-1087`; backfill `:38-81` |
| **I8** (session-id sanitizing) | **Confirmed.** Mix cache: `re.sub(r"[^A-Za-z0-9_-]","_",sid)[:40]`. Session cache: raw `str(sid)`. Both default to `"nosession"`. Cost history: raw `session_id` with **no** default (absent → not recorded). `⌂`: only if `session_id` is truthy. For real UUIDs (36 chars, `[0-9a-f-]`) the names are identical. Differences appear only for exotic sids: collisions in the mix cache, silent persistence failure for sids with `/` in the session cache, and the type crash (CP-13a). Windows note for Go: raw sids with `:`, `\`, `*` etc. are invalid filenames there, so Go will need a sanitizing decision. Legacy never ran on Windows, so this is a D5 design choice, not a parity issue | `:1016-1017,1214-1215,226,605,1229` |
| **I11** (composition "≈tokens/4" wording) | **The units are characters, not bytes, and the /4 is never applied.** Composition sums code points (raw strings) and `json.dumps` characters (structured content), plus 2000 per image (§2.4). The exporter's `est_prompt += req_bytes/4.0` (`:190-193`) uses `req_bytes = len(flow.request.get_text())` (`dgx_proxy.py:123`), also characters of the decoded request body. The shared part is only "characters ≈ 4 × tokens", and in the composition it cancels out (percentages are ratios). The `:944` docstring "Byte-proportional" and the WIDGETS phrase "by bytes" are wrong in wording only. Spec the unit as **characters (Python semantics)** | `:944,1120-1149`; exporter `:190-193`; `dgx_proxy.py:123` |

---

## 8. TARGET 7 — Ubiquitous-language glossary refinements

| Term | Refined meaning (code-grounded) | Evidence |
|---|---|---|
| **Lane** | Three vocabularies. **Proxy lane**, decided per request: `anthropic`, `anthropic-server-tools`, or DGX (implicit: no `lane` key; events prefixed `dgx_`). **Status line lane**, the configured lane of the session's *main* model from stdin `model.id`: `dgx` / `anth` / None (pill `◨ DGX`/`◨ ANTH`/`◨ ?`). It never sees the server-tool override or Haiku background calls. **Backfill lane**: the lane with the most output tokens | `dgx_proxy.py:132-141`; `:446-449,604`; backfill `:77,81` |
| **Window** (overloaded; always qualify it) | **CC window** = the Claude Code OS process (survives `/clear`; `⌂`). **Plan window** = Anthropic 5 h / 7 d quota period. **Context window** = model token capacity (`context_window_size`). **Sparkline window** = the last 12 points ≤ 90 s. **Cost window** = 30 d. **TTFT window** = 30 min. **Read window** = the 512 KB transcript cap | `:265-295,501,423,82-83,218,121,952` |
| **Session** | One Claude Code `session_id`. `/clear` starts a new one (new transcript, new caches, timer reset), but the CC window continues | `:1214`; review #9 |
| **API message / call** | One assistant `message.id`. CC writes **one transcript line per content block** and repeats the full usage on each. The unit of usage counting and of the turn rate | `:1029-1032` |
| **Turn** (last-turn rate) | Only "API message timed from its trigger line": `t0` = the last user line (prompt **or** tool result) before its first line, `t1` = its last line. Not a user→assistant conversational turn | `:1064-1087` |
| **Interleaved tool_result** | A `user` line whose content array holds a `tool_result` block. It updates `lu` but does **not** close the current message | `:1080-1085` |
| **Rebuild (`↻`)** | An API call with `cache_write − max(0, prompt − previous_prompt) > 20000` tokens. Never the first call after a compaction or reset (`pp=None`) | `:1116-1119` |
| **Composition** | Character shares (§2.4) of tool results (incl. all images) ▤, conversation (text, string content, tool-call input) ❙, and thinking text as stored ◈, accumulated since the last `compact_boundary`. Percentages use banker's rounding; `<1%` means present but rounding to 0 | `:1120-1149,1157-1174` |
| **Compaction** | A `system` line with `subtype:"compact_boundary"`. Resets composition and `pp` only, never the totals or the id memory. The transcript file never shrinks | `:1088-1095` |
| **Plan window states** | *reported* (stdin, non-empty) → *remembered* (cached `rl`, `< 1800 s`) → *expired* (`resets_at <= now`, dropped even while remembered) / *unreported* (hidden). *Pace/projection* = used% ÷ elapsed share when elapsed ∈ [0.10, 1.0] | `:298-312,505-521` |
| **Fresh / stale / dead** (telemetry) | *fresh*: `up` and age ≤ 15 s. *stale*: not up or age > 15 s, last-known values shown dimmed with `(~Ns old)`, sparkline hidden. *dead*: no sample (never fetched, or > 300 s on the fetch path) → `◌ DGX ?`. *Serving down* (`vLLM down` / `LMCache down`) is orthogonal and overrides the dot | `:693-730` |
| **Stale** (other uses; always qualify it) | *stale span*: turn span > 4·out/15, skipped. *stale rl*: > 1800 s. *stale git cache*: > 5 s. *stale cost record*: > 30 d, excluded from thresholds, never deleted | `:994,312,409,246` |
| **Degraded** (two distinct meanings) | (1) **`statusline degraded`**: the whole-output fallback for any exception in `main()` (§5). (2) **Degradation ladder**: the per-widget telemetry states fresh→stale→dead. Never call (2) "degraded" in the spec | `:1243-1245`; `:693-702` |
| **Fresh input** | The `in` token class = uncached `input_tokens`. Not related to telemetry "fresh" | `:1109` |
| **Cold start** | Fewer than 10 qualifying (≥ $1, same lane, ≤ 30 d, not this session) cost records for a lane. `$` turns yellow at a fixed $25 and `$/h` stays uncolored | `:240-262,614-615,624` |
| **Reroute-all** | Any routing prefix whose `rstrip("*")` is `claude` or `claude-`. The limits widget is hidden because nothing can burn the plan | `:487-489` |
| **Box vs mine** | **box** `▣` = all-client vLLM generation rate over 1 min (5 min fallback). **mine** `»` = this session's last completed API message rate (transcript, both lanes). Not comparable quantities | `:765-785` |
| **Basis (`⛏`)** | Owned-hardware cash $/MTok from VM (`dgx_cost:dgx_usd_per_mtok`), valid only when the trailing DGX-lane volume is ≥ 30.4 MTok/month. Applied to the session's ↑+↓ tokens, DGX lane only | `:626-635` |
| **Idle** | `☾`: the DGX lane's last request is more than 300 s ago **and** nothing is running on vLLM. Benchmarks bypass the proxy, so they do not reset it | `:822-834` |
| **Reported vs effective rate limits** | stdin `rate_limits` vs `effective_rl()` output (stdin if non-empty, else remembered) | `:1216` |

---

## Delta Summary

New vs the broad sweep (passes 0-6), counted per target:

| Target | New items | Highlights |
|---|---|---|
| T1 stdin | **24 field rows** with type/fallback/crash/consumer (previously 14 rows with field + line only) + **3 new findings** | locale-dependent stdin/stdout decoding (§1.3, strict vs surrogateescape, verified); `COLUMNS` Python-`int()` grammar and negative-value row-2 drop; `str()` rendering of non-string labels |
| T2 transcript | **1 precise schema** + **9 new rules** | per-record processing order; `lu` updated on tool-result lines; images always ▤; `redacted_thinking` counted nowhere; usage/composition counted for any record type; JSON-escaped vs raw measurement split; bytes `splitlines` boundary set; `json.loads(bytes)` BOM/UTF-16/surrogatepass acceptance; 256-id memory double-count condition; long-line extension can read past the stat size |
| T3 caches | **4 exact wire formats** + **8 new facts** | `NaN`/`Infinity` tokens in caches; mode 0600 temp files; point key-order variant (`t,k,f,v`); unbounded cost-history growth; parse-failed cost-history wipes all history on the next write; shared `nosession` mix cache across transcripts; git key is the raw (non-normalized) dir; refresh side-effect order (6 steps) |
| T4 VM | **1 response-path table** + **TelemetrySample NaN matrix (8 keys)** | one series missing `metric` or with `value:null` fails the whole fetch; `resultType` unchecked; KV-NaN and trace-NaN crash paths |
| Crash catalogue | **31 crash paths** (30 degraded, CP-01..41; 1 import-time, CP-90) with trigger, line, persistence | 7 **persistent** transcript paths (offset never advances); CP-09 persists ≤ 1,800 s via the cached `rl`; import-time class is not degraded (empty stdout, exit 1) |
| T5 CONFIG | **40 env rows** mapped + **~55 status line literal keys** + **11 named-constant classes** | 5 env inputs are not config (COLUMNS, ANTHROPIC_CUSTOM_HEADERS, TMPDIR as OS input, PRINT_ARGS as CLI flag) or dropped (INVISIBLE, ROUTER_PORT, KEV_MESSAGES); `paths.hook_log` unifies the hard-coded writer path |
| T6 inconsistencies | **5 resolved** (I2, I6, I7, I8, I11) | I6 has two input classes plus a proxy-only crash; I7 has five extra divergences, incl. the backfill aborting on a bad timestamp |
| T7 glossary | **20 terms refined/added** | "window" ×7 senses, "stale" ×5, "degraded" ×2, lane ×3 vocabularies |
| Audit | **4 retractions** (CONV-ABS-1..4) + 3 refinements | CONV-ABS-3 changes the harness determinism recipe |

Existing items refined: Pass 2 entities Session cache, Mix cache, Composition, Turn, Cost record, Sparkline point; Pass 3 BC-SL-002/033/041/052 (noted here, not edited); Pass 6 R7 and the harness recipe.

## Remaining Gaps / next candidate scope (verbatim-carryable)

1. Production locale of the status line process (the `LANG`/`LC_CTYPE`/`LC_ALL` that Claude Code passes to the status line command) is UNVERIFIED. It decides strict vs surrogateescape stdin/stdout (§1.3) and so the harness locale. Owner capture needed.
2. Whether VictoriaMetrics ever returns `"NaN"`/`"+Inf"` sample values for the queried series (decides whether CP-40/CP-41 are reachable in production). Static analysis cannot settle it. Needs one captured `/api/v1/query` response from an idle box.
3. Real Anthropic and vLLM SSE event shapes: does `message_delta.usage` carry `input_tokens`? (I2 consequence for `*_usage` events; LOW.)
4. Proxy-side domain model at the same depth as T1-T3 for P3: request-body schema consumed (`model`, `tools[].type`, `metadata.user_id`, content blocks for normalization), response JSON/SSE schema, and the flow-attribute entity lifecycle (`_attrib`, `_dgx`, `_t0`, `_dgx_t0`, `_sse_tap`). A crash-path catalogue for the proxy hooks (which exceptions escape to mitmproxy, e.g. the I6 `account_uuid` TypeError).
5. Exporter domain model for P2: the rebuild state entity per metric family (key tuples, types, default labels), and a crash-path catalogue (`status: null` TypeError, non-object ledger lines, `t` parse failures), each tied to its exposition line.
6. Stop-hook and launcher entities for P4: the hook stdin schema with type/fallback/crash table (like T1), the hook log line grammar as a wire format (Python `repr` quoting rules), and the `--settings` JSON assembled by the launcher as an exact wire format.
7. Backfill: a full domain/contract table (pricing family resolution order `opus→sonnet→haiku` by substring, `w5` fallback logic, glob order dependence, crash on a bad timestamp), to spec `hylo cost backfill`.
8. Owner decisions surfaced (do not resolve in analysis): CONFIG key naming scheme and the `HYLO_*` derivation rule; whether glyphs are config (§6.2 last row); Windows sid sanitizing (I8); whether `paths.hook_log` unifies writer and reader during parity.

## Novelty Assessment

Novelty: SUBSTANTIVE
Removing this round would change how the system is specified:
- A complete crash-path catalogue (31 paths; the 7 transcript-driven ones persist for the whole session) now defines the byte-exact degraded contract the owner required. The broad sweep had only the generic "any exception → degraded" rule.
- The locale finding (CONV-ABS-3) invalidates the pass-6 harness recipe.
- `NaN`/`Infinity` tokens and side-effect ordering change the cache wire-format spec that Go's readers and writers must satisfy during shadow/cutover.
- The CONFIG entity is new (D15).
- I6 and I7 resolutions add contract differences the broad sweep did not have.

## Convergence Declaration

Another round needed. Substantive gaps remain: proxy, exporter and hook domain models at field/crash depth (gaps 4-7), and two externally-dependent facts (gaps 1-2) that decide parity-harness design.

## State Checkpoint

```yaml
pass: 2
round: 1
status: complete
files_scanned: 6   # dgx_statusline.py (full), dgx_proxy.py (part), dgx_ledger_exporter.py (part), tools/backfill_cost_history.py (full), auto_continue.py (part), claude-dgx (env knobs)
timestamp: 2026-11-14T05:54:44Z
novelty: SUBSTANTIVE
next: pass 2 round 2 (targets = Remaining Gaps 1-8 verbatim)
```
