---
artifact_type: semport-target-design
project: hylo-legacy
module: status line (legacy/dgx_statusline.py, 1,245 lines, 742 statements)
source_language: "Python 3 (CPython 3.11.x oracle, OD-104)"
target_language: "Go (go.mod floor go 1.26.0, standard library first)"
semport_phase: "2 — Target Language Design (incremental / scoped: P1 status line only)"
producer: codebase-analyzer (semport-analyze)
date: 2026-11-15
inputs:
  - hylo-legacy-pass-8-deep-synthesis.md
  - hylo-legacy-pass-3-deep-behavioral-contracts.md
  - hylo-legacy-pass-3-deep-behavioral-contracts-r2.md
  - hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - hylo-legacy-pass-4-deep-nfr-r7.md
  - hylo-legacy-pass-5-deep-conventions-r3.md
  - hylo-legacy-pass-5-deep-conventions-r5.md
  - brownfield/porting-decision.md
  - specs/owner-decisions-log-2026-11-14.md
  - specs/research/general-go-port-parity-crossplatform-2026-11-14.md
  - planning/market-intel.md
  - docs/PLAN.md
  - docs/RESUME.md
input_notes: "BC index = P3r4 §7.3 with detail from broad/r1/r2/r3 and amendments r5-r8; thresholds = P4r7 §B.2.1; conventions/pitfalls = P5r3 §B + r4/r5; legacy source legacy/dgx_statusline.py (read-only); docs/STATUSLINE-WIDGETS.md and docs/STATUSLINE-REVIEW-2026-11-13.md consulted"
companion: .factory/semport/hylo-legacy/semport-assessment.md
input-hash: "cf8cd10"
---

# Status line: Python to Go translation plan (semport Phase 2)

**Scope.** One module: `legacy/dgx_statusline.py` (abbreviated **SL**; `SL:n` is a line in that file), minus `--subagent`
(OD-14). Phase 1 (the 6-pass analysis) is not re-run. Every claim cites either a legacy line or a source document section.
Abbreviations follow pass-8 (`P3r4` = pass 3 deepening round 4, and so on). **BC** = behavioral contract (BC-SL-001..103),
**PR-nn** = pitfall register entry (P5r3 §B.6), **T-nnn** = threshold row (P4r7 §B.2.1), **CP-xnn** = crash path
(P3 r1 §B), **IM-nn** = idiom row defined in §1 of this file.

**Settled inputs this plan obeys** (none are reopened): D1-D16 (`docs/PLAN.md` §2, §10); D4-EX-1 (⌂ on Windows), D4-EX-2
(wrong-shape transcript lines skipped), D4-EX-3 (config-error line, OD-102); OD-03 (raw sid in the session-cache name),
OD-05 (HYLO_* plus config only, typed booleans, no DGX_* aliases), OD-14 (no `--subagent`), OD-21/OD-32 (D4-EX-2 edges),
OD-30 (numeric sid: one key), OD-55, OD-56 (total deadlines), OD-57 (all rationales), OD-58 (extended clock shim),
OD-95 + OD-101 (hylo cache dir from P1), OD-103 (one `internal/pyfmt`, four files), OD-104 (CPython 3.11.x, explicit
interpreter), OD-105 (named exclusion list), OD-106 (cost history copied at P5).

---

## 0. Summary

| Item | Value |
|---|---|
| BCs mapped | **103 / 103** (§8). 101 become Go contracts; BC-SL-068 is legacy-only and is replaced by BC-SL-098 (D4-EX-2); BC-SL-097 is not ported (OD-14) |
| Parity class after the owner rulings | BX 96 · D4-EX-2 4 (068, 098, 099, 100) · D4-EX-3 1 (087) · OD-30 known difference 1 (079) · OOS 1 (097) |
| Translation confidence per BC | **HIGH 84 · MEDIUM 18 · LOW 0 · n/a 1** (§8; the reasons are per BC) |
| Translation order | S0 skeleton/CI → S1 `internal/pyfmt` → S2 frame (config subset, guard, stdin, width/trim, cache store, orchestrator) → S3 row-1 widgets → S4 transcript parser → S5 row 2 + metrics client + session cache → S6 cost history → S7 window age; harness H in parallel from S0; S8 goldens and burn-down (§4) |
| Effort | about **62 ideal engineer-days**, range 50-80 (judgment; units and assumptions in the companion assessment §4) |
| Tensions | 10 (§7.1), none resolved here |

---

## 1. Python to Go idiom map (constructs this file actually uses)

Each row names the construct, where the file uses it, the Go mapping, and the BCs and pitfalls it affects. The Go helpers
live in `internal/pyfmt` (OD-103); their file is given in brackets: `[num]`, `[json]`, `[str]`, `[time]`.

### IM-01 JSON decode with Python `json` leniency

- **Python use.** `json.load(sys.stdin)` on text (SL:1202); `json.load(fh)` on cache files in text mode (SL:192-193);
  `json.loads(resp.read())` on bytes (SL:171); `json.loads(line)` on transcript bytes (SL:1061).
- **What differs from Go `encoding/json`.** Python accepts `NaN`/`Infinity`/`-Infinity` tokens. It keeps integers exact (no
  float64 rounding) up to the 4,300-digit limit (PR-10). It keeps lone surrogate escapes (`\ud800`). Duplicate keys are
  last-wins, kept at the first key's position. Nesting of about 1,000 levels raises `RecursionError`, which the callers
  treat as a parse failure. Bytes input detects a UTF-8 BOM and UTF-16/32, while text input rejects a BOM. Invalid UTF-8
  raises (BC-SL-067, BC-SL-076, research P15). Go rejects NaN tokens, decodes numbers to float64, replaces invalid UTF-8
  and lone surrogates with U+FFFD, rejects a BOM, allows 10,000 levels, and its maps lose key order.
- **Go mapping.** A hand-written decoder `pyfmt.Decode(b []byte, mode DecodeMode) (Value, error)` `[json]`.
  `ModeText` follows `json.load` on a strict-UTF-8 text stream: a BOM is an error, invalid UTF-8 is an error. `ModeBytes`
  follows `json.loads(bytes)`: BOM/UTF-16/32 detection, invalid UTF-8 is an error.
  - **Objects are ordered** (`[]Member`) with Python dict semantics: assigning to an existing key keeps its position,
    `Delete` removes it.
  - **Numbers keep their Python type:** int (int64 fast path, promoted to `*big.Int`), float64 or bool.
  - **Strings are WTF-8**, so a lone surrogate survives and counts as one code point (IM-11).
  - **Depth limit** mirrors CPython 3.11's recursion failure point. The exact depth is pinned by a CPython-generated table
    (BC-SL-067: depth 995 accepted, 1,000 rejected).
- **BCs:** 002, 033, 040, 041, 052, 067, 076, 091, 096, 100, 103. **Pitfalls:** PR-09, PR-10, PR-11, PR-19.

### IM-02 dict access, `.get(k) or default`, `isinstance(x, (int, float))`, truthiness

- **Python use.** `d.get("model") or {}` (SL:441), `cost.get(...) or 0` (SL:535), `isinstance(pct, (int, float))`
  (SL:420, 478, 506, 540, 551, 557, 585-598, 602, 622, 628, 1104-1112). `bool` passes `isinstance(int)`; NaN passes too.
  0, 0.0, "", [], {} and None are falsy (CV-12).
- **Go mapping.** These are methods on `pyfmt.Value`: `Get(key) Value` (a missing key gives Null), `Truthy() bool`,
  `IsNumber() bool` (true for bool, int and float, matching `isinstance((int, float))`), and `Float() float64`.
  - **Type confusion that Python turns into an exception** (calling `.get` on a non-dict, `len` of a number) becomes an
    explicit predicate that returns `errDegraded` at the same site (IM-15). Example: `AsDictOrDegrade()` at SL:442
    (CP-S01).
- **BCs:** 006, 007, 011, 013, 019, 024, 035, 057, 058, 060, 072, 085. **Pitfalls:** PR-06, PR-21.

### IM-03 JSON encode for the four cache files (`json.dump` defaults)

- **Python use.** `json.dump(data, fh)` (SL:203) for the session cache (SL:1215), the mix cache (SL:1150-1153), the git
  cache (SL:410-411) and `cost-history.json` (SL:237).
- **Format to reproduce byte for byte.** Ruling (b), P3r2 §0:
  - separators `", "` and `": "`, `ensure_ascii`, and no trailing newline;
  - `NaN`/`Infinity` tokens, and float `repr` (`1794615009.0`, `1e-05`);
  - int versus float preserved (an `api_ms` int stays int, BC-SL-102);
  - insertion order, including order inherited from the file read earlier (`entry = dict(c)` at SL:327, then `fetch_ts, up,
    ts, sample, hist` appended at SL:349; BC-SL-091).
- **Go mapping.** `pyfmt.Dumps(v Value) []byte` `[json]` over the ordered `Value`. The cache writers mutate the `Value`
  they loaded instead of building a fresh struct. **Go structs with `encoding/json` must not be used for caches**: they
  would reorder keys and reformat floats.
- **BCs:** 010, 018, 028, 031, 041, 052, 091, 093, 102, 103. **Pitfalls:** PR-07, PR-08, PR-19.

### IM-04 `json.dumps` length for composition

- **Python use.** `len(json.dumps(it))` for tool_result list items (SL:1138), `len(json.dumps(inner))` (SL:1140),
  `len(json.dumps(blk.get("input") or ""))` (SL:1147).
- **Go mapping.** `pyfmt.DumpsLen(v Value) int` `[json]`. It counts the encoder's output without allocating it, and it
  shares the escaping and float-`repr` code with IM-03 so the two cannot drift. Acceptance oracle: the 63-case table in
  BC-SL-096 plus the tool_result item rules (`{}` 2, `0` 1, `false` 5, `null` 4 in lists, but `null` 0 as a non-list
  inner value; P3r2 §A5).
- **BCs:** 038, 071, 096. **Pitfalls:** PR-07, PR-08, PR-10.

### IM-05 f-strings and format specs; `str()` of non-str

- **Python use.**
  - `{x:.0f}` / `.1f` / `.2f`: 435-437, 479, 522, 599, 616, 625, 635, 700, 741, 761-762, 778-783, 795, 813-819, 857, 870-873
    (research §2b P3).
  - `{n:>2d}` (SL:1172); `{n:02d}` (SL:525, 527, 548, 561, 829, 831).
  - `f"{WHITE}{model_name}{RESET}"` with a non-str value (SL:442, 453; BC-SL-058).
- **What differs.** Python spells `nan`, `inf` and `-inf`; Go spells `NaN` and `+Inf`. `:d` applied to a float raises in
  Python. `str([1, "a"])` is `[1, 'a']` (Python repr), and `str(1e16)` is `1e+16`.
- **Go mapping.** All in `[num]` except `Str`:
  - `pyfmt.F(x float64, prec int) string` wraps `strconv.FormatFloat(x, 'f', prec, 64)`, which matches Python for every
    finite value including `-0` (research P3), and special-cases non-finite values.
  - `pyfmt.D(n int64, width int, zeroPad bool) string`.
  - `pyfmt.Str(v Value) string` `[json]`: Python `str()` of a str is unchanged; anything else goes through `repr`, with
    float `repr` from `pyfmt.Repr`.
- **BCs:** 007, 011, 013, 016, 019, 024-027, 043, 045, 047, 049, 050, 057, 058, 060, 062, 075, 082, 083, 085, 086.
  **Pitfalls:** PR-02, PR-07, PR-16.

### IM-06 `round()` (half-even), `round(x, 4)`, and explicit half-up `int(x + 0.5)`

- **Python use.** `round(n / total * 100)` (SL:1171, BC-SL-012); `round(usd, 4)` (SL:234, BC-SL-028); half-up
  `int(pct / 10 + 0.5)` (SL:426) and `int(min(j, 7) + 0.5)` (SL:675).
- **Go mapping.** All in `[num]`:
  - `pyfmt.Round(x) (Num, error)`: ties to even; NaN gives `ValueError` and ±Inf gives `OverflowError`, both mapped to
    `errDegraded`.
  - `pyfmt.RoundN(x, n) float64`: correctly rounded decimal, via `strconv.ParseFloat(strconv.FormatFloat(x,'f',n,64),64)`
    (research P2); `round(inf, 4)` returns inf.
  - Half-up sites are written as `pyfmt.Int(x + 0.5)`. Never `math.Round`.
- **BCs:** 011, 012, 028, 048, 073, 102. **Pitfall:** PR-01.

### IM-07 `int()`, `math.ceil`, truncation that raises on non-finite values

- **Python use.** `int(r * 255)` (SL:148), `int(pct/10 + 0.5)` (SL:426), `int(ms // 60000)` (SL:546), `int(n)` in
  `_fmt_lines` (SL:853), `math.ceil(kv / 25)` (SL:759), `int(c * fade)` (SL:683).
- **Go mapping.** `pyfmt.Int(x float64) (int64, error)` and `pyfmt.Ceil(x) (int64, error)` `[num]`. NaN gives
  ValueError and Inf gives OverflowError, mapped to `errDegraded` at the sites where Python does not catch the exception
  (CP-S06, CP-S11, CP-S12, CP-S13, CP-N01, CP-N02). `_fmt_lines` catches only `TypeError`/`ValueError` (SL:854-855), so
  NaN gives `"?"` while ±Inf (OverflowError) degrades (BC-SL-063). The helper returns typed errors (`ErrValue`,
  `ErrOverflow`) so each site can reproduce Python's catch list exactly.
- **BCs:** 011, 019, 020, 029, 046, 048, 056, 063, 064, 073, 074. **Pitfall:** PR-05.

### IM-08 `//` and `%` on floats and ints

- **Python use.** Float: `rem // 86400`, `rem % 86400` (SL:525-529), `ms // 60000` (SL:546), `win_ms // 60000`
  (SL:560), `(time.time() - last) // 60` (SL:826). Int: SL:548, 561, 829-831, 859.
- **Go mapping.** `pyfmt.FloorDiv/Mod(a, b float64)` is a port of CPython `float_divmod`, not `math.Floor(a/b)`;
  `FloorDivInt/ModInt` handle ints `[num]`. **Reason:** dividends near 1e8 ms put the `a/b` rounding error near one ulp
  of the quotient (research §2b P7).
- **BCs:** 017, 020, 021, 022, 051, 064, 081, 084. **Pitfall:** PR-03.

### IM-09 `max`/`min` with NaN (argument order matters)

- **Python use.** SL:146, 422, 479, 508, 671, 674-675, 758-759, 1117 (`max(0, prompt - pp)`).
- **Go mapping.** `pyfmt.Max(a, b)` returns `b` only if `b > a`, otherwise `a`; `Min` likewise. They are called with the
  **same argument order** as the source. Never use the builtin `max` or `math.Max`, which propagate NaN (research P8).
- **BCs:** 011, 013, 016, 036, 046, 048, 056, 060, 073, 074. **Pitfall:** PR-04.

### IM-10 Floating-point contraction (FMA)

- **Python use.** colorsys inside `heat` (SL:146-147): `h*6.0 - i`, `v*(1.0 - s*f)`, `v*(1.0 - s*(1.0 - f))`. The ⌂ gate
  `(time.time() - win_start)*1000 - dur` (SL:558-559).
- **Go mapping.** Wrap every product that feeds `+`/`-` in an explicit `float64(...)` conversion (the Go spec forbids
  fusing across one). Port colorsys in CPython's operation order. Tests run on **arm64 only** (macos-15 runner), because
  amd64 at any `GOAMD64` level does not detect the status-line sites (CONV-ABS-77, P5r3 §A.2). Convention: a
  `// pyfmt: no-fuse` comment at each site (research Implications 3).
- **BCs:** 022, 056. **Pitfall:** PR-15. The `--subagent` site (SL:889, 919) is out of scope (OD-14).

### IM-11 String length, slicing, regex substitution, whitespace, paths (code-point semantics)

- **Python use.**
  - `len(_ANSI.sub("", text))` (SL:153).
  - `re.sub(r"[^A-Za-z0-9_-]", "_", sid)[:40]` (SL:1017), substituting per **code point** before truncating.
  - `p.strip()` with Python Unicode whitespace, NBSP included (SL:444-445).
  - `p.rstrip("*")` (SL:487) and `row.rsplit(SEP, 1)` (SL:1196).
  - `bytes.splitlines()` (SL:1059), which splits on `\n`, `\r\n` and `\r` only.
  - `out.strip().split(None, 2)` (SL:284; replaced, see IM-19).
  - `os.path.basename(os.path.normpath(p)) or os.path.normpath(p)` (SL:460). POSIX `normpath("//")` is `//`, while Go's
    `filepath.Clean` gives `/` (BC-SL-059).
  - `os.path.abspath`/`join`/`normpath` in the git walk (SL:373, 375, 383).
  - `len(content)`, `len(inner)`, `len(blk.get("text") or "")` (SL:1122, 1133, 1143, 1145).
- **Go mapping.** In `[str]`:
  - `pyfmt.Len(s)` counts code points, and treats a WTF-8 surrogate as 1.
  - `pyfmt.Truncate(s, n)`, `pyfmt.SubNonWord(s, '_')` (per code point), `pyfmt.Strip`, `pyfmt.RStrip(s, chars)`,
    `pyfmt.RSplit1(s, sep)`, `pyfmt.SplitLinesBytes`.
  - `pyfmt.PosixNormpath`, `pyfmt.NtNormpath` and `pyfmt.Basename`, selected per OS (Windows uses `ntpath`).
  - The ANSI regex stays an RE2-safe `regexp` with explicit `[0-9;]` (research P23).
  - Do **not** use `go-runewidth`: legacy counts code points, not terminal cells (research P12).
- **BCs:** 004, 006, 008, 009, 014, 033, 038, 054, 059, 067, 070. **Pitfalls:** PR-11, PR-12, PR-13, PR-20.

### IM-12 `int()` and `float()` parsing of strings (Python grammar)

- **Python use.** `int(COLUMNS)` (SL:1188); `float(s["value"][1])` on VictoriaMetrics strings (SL:178), which accepts
  `"NaN"`, `"+Inf"`, `"1e400"`, `" 1 "`, `"1_0"` and Unicode digits; `int(n)` and `float(n)` on stdin values in
  `_fmt_lines`/`_fmt_tok_c` (SL:853, 866). The import-time `float`/`int` at SL:74-75 is replaced by IM-16.
- **Go mapping.** `pyfmt.ParseInt(s) (Num, error)`, which enforces the 4,300-digit limit, and
  `pyfmt.ParseFloat(s) (float64, error)` `[num]`. `COLUMNS` keeps the Python grammar because it is a Claude Code protocol
  input, not a hylo setting (P5r3 §B.1 ENV-15). Edge to test: a negative `COLUMNS` longer than 4,300 digits raises in
  Python, giving 0 and therefore row 2 *shown*, whereas a shorter negative value hides row 2 (BC-SL-005/055).
- **BCs:** 005, 019, 024, 040, 055, 062. **Pitfalls:** PR-10, PR-18.

### IM-13 Date and time

- **Python use.** `datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()` (SL:983) with the 3.11 grammar. A naive
  value means **local** time, and fractions beyond microseconds are truncated (BC-SL-069).
  `time.mktime(time.strptime(..., "%a %b %d %H:%M:%S %Y"))` (SL:286) is replaced by IM-19.
- **Go mapping.** In `[time]`:
  - `pyfmt.FromISOFormat(s string, loc *time.Location) (float64, bool)` is a hand-written parser for the 3.11 grammar
    subset, fuzzed against the oracle.
  - Naive values go through `pyfmt.LocalToUnix(loc, wall)`, a port of CPython `_mktime`. That port showed 0 mismatches
    over 10,893 CPython goldens across four zone grids (P5r5 §B.6). Go's `time.Date` differs in gaps (offset < 0) and in
    overlaps (offset ≥ 0) (PR-14).
  - `*time.Location` is injected (`Env.Loc`); `time/tzdata` is embedded.
- **BCs:** 039, 069 (and 080 through the replaced path). **Pitfall:** PR-14.

### IM-14 `time.time()` (nine reads)

- **Python use.** SL:231, 243, 304, 322, 408, 499, 558, 825, 826 (P3r1 §A0; DET-01..08).
- **Go mapping.** `Env.Now func() float64` returns the **Python `time.time()` value**, `float64(t.UnixNano())/1e9`
  (research P20). The orchestrator reads it **once per render** and passes the value down. Under a frozen clock this is
  output-neutral; with a live clock it removes the minute-straddle in the idle widget, where SL:825 and SL:826 read the
  clock separately (P3r1 §A0, DET-08). The binary honors `HYLO_TEST_NOW` as a decimal string that both sides parse (§3).
- **BCs:** 010, 015, 018, 022, 028, 029, 041, 051, 084, 093. **Pitfall:** PR-14 (related, DET-07).

### IM-15 Exceptions to errors: the degraded ladder

- **Python use.** One top-level `except Exception` prints `\e[90mstatusline degraded\e[0m\n` (29 bytes) and exits 0
  (SL:1238-1245; BC-SL-001). The levels below it (CV-08, E1-E5):
  - **Never-raise helpers.** `load_cache` and `save_cache` (SL:190-206), `fetch_sample` (SL:186), `git_branch`
    (SL:394), `claude_window_start` (SL:293).
  - **Narrow catches.** `_fmt_lines` catches `TypeError`/`ValueError` only (SL:854). `fetch_sample` skips a series only
    on `KeyError`/`ValueError`/`IndexError` (SL:179), so a `TypeError` inside the loop escapes to the outer
    `except Exception` and drops the **whole** sample. `json.loads` on a transcript line catches everything (SL:1062).
  - **Unguarded type confusion** that becomes degraded output: 17 stdin paths CP-S01..S17, 7 transcript paths CP-T01..T07,
    2 network paths CP-N01/N02 (P3 r1 §B).
- **Go mapping.**
  - `var errDegraded = errors.New("statusline degraded")`. Each CP site returns an error wrapping it (`%w`, with the CP id
    for diagnostics only). One top-level handler in `statusline.Main` prints `degradedLine` and returns 0.
  - A `recover()` backstop maps any panic to the same line, mirroring `except Exception`. A Go bug that panics would
    still show up in the parity diff, because legacy would not degrade on that input.
  - Never-raise helpers return zero values, not errors.
  - The narrow catch lists are reproduced **per site** with typed helper errors (IM-07), including the `TypeError`
    escape in the VictoriaMetrics loop.
  - The CP-T paths do **not** degrade in Go. They are skipped under D4-EX-2 (BC-SL-098); see S4.
  - Import-time crashes CP-X01/X02 have no Go equivalent: they become D4-EX-3 (IM-16).
- **Side-effect rule.** A crash at step k keeps the writes of steps 1..k-1 (BC-SL-077). The orchestrator therefore runs
  effects and renders in legacy order and stops at the first `errDegraded` (§3.2).
- **BCs:** 001, 040, 057, 063, 064, 068, 072, 073, 074, 077, 088, 093, 098. **Pitfall:** PR-21.

### IM-16 Module-level env parsing becomes `internal/config`

- **Python use.** These run at import: `DGX_SL_VM_URL` with `rstrip("/")` (SL:73), `float(DGX_SL_TTL)` (SL:74),
  `int(DGX_SL_ROWS)` (SL:75), `!= "0"` toggles (SL:76-77), `DGX_SL_TRACE` (SL:89), `expanduser` (SL:78). A bad number
  crashes before the guard: blank output, exit 1 (CP-X01/X02, BC-SL-087). `LOCAL_MODEL_PREFIXES` is read **at render
  time** (SL:444).
- **Go mapping.**
  - The settings are resolved once at startup by `config.Load` (config file, then `HYLO_*`, then defaults). Values are
    typed (booleans `true/false/1/0/yes/no`, OD-05) and validated (`config.Seconds` is finite, > 0 and
    ≤ 9,223,372,036.854775; PR-22).
  - Any invalid value renders `hylo: config error: <key>=<value> (<reason>)`, exits 0, writes details to stderr, and
    performs **no** cache writes. This is **D4-EX-3** (OD-102), and it matches legacy's "nothing written" because legacy
    dies at import.
  - `DGX_*` names are never read (OD-05).
  - `COLUMNS` stays a protocol input with the Python grammar (IM-12).
- **BCs:** 005, 006, 014, 053, 087. **Pitfalls:** PR-18, PR-22.

### IM-17 File I/O and atomic writes

- **Python use.**
  - Cache writes: `os.makedirs(CACHE_DIR)`, `tempfile.mkstemp(dir=CACHE_DIR, prefix=basename + ".")` (mode 0600),
    `json.dump`, `os.replace`, with every exception swallowed (SL:198-206). The temp file leaks if the replace fails
    (BC-SL-078).
  - Cache reads: text mode (SL:192).
  - Transcript: binary `seek(off)`, `read(min(size - off, 524288))`, extended by 524,288-byte chunks **only** while the
    blob has no `\n` (SL:1041-1052); `os.path.isfile` and `os.stat` on `transcript_path` (SL:1010-1015).
  - `.git` reads in text mode (SL:380-386).
- **Go mapping.**
  - `statusline.CacheStore` with `Load(name) pyfmt.Value` and `Save(name, pyfmt.Value)`. The production implementation:
    `os.MkdirAll`, `os.CreateTemp(dir, base+".")`, chmod 0600, write, `os.Rename`, every error swallowed. On Windows, add
    2-3 short retries on a sharing violation (research §4b).
  - Go removes the temp file on failure, which legacy does not; the harness ignores temp names (§5.3; tension T2).
  - Transcript reads are binary, with identical step and completion rules.
- **BCs:** 009, 030, 032, 052, 066, 078. **Pitfall:** PR-20.

### IM-18 `urllib` becomes `net/http`

- **Python use.** `urllib.request.build_opener(ProxyHandler({}))` bypasses proxy environment variables (SL:168), with
  `timeout=1.5` per socket operation (SL:170). The URL is `f"{VM_URL}/api/v1/query?query={quote(QUERY, safe='')}"`
  (SL:165). urllib raises on a non-2xx status (caught, giving None) and follows up to 10 redirects.
- **Go mapping.**
  - Client: `&http.Client{Transport: &http.Transport{Proxy: nil}, Timeout: cfg.Telemetry.Timeout}`, where the timeout is
    a **total** deadline equal to 1.5 s (OD-56; DNS falls inside it, PR-22).
  - Status outside 200-299 gives no sample. The body is read whole and decoded with `pyfmt.Decode(…, ModeBytes)`.
  - The query is escaped like Python `quote(safe='')`, i.e. `%20` for a space and not `+`. This keeps the request
    identical; it is not output-relevant.
  - Under D14 the proxy bypass becomes defense in depth (pass-8 LD-8).
- **BCs:** 040, 053. **Pitfall:** PR-22.

### IM-19 Subprocesses: `ps` and git

- **Python use.** Up to 6 calls of `ps -o ppid=,comm=,lstart= -p <pid>`, each with a 1 s timeout, then
  `strptime`+`mktime` (SL:276-294). On Windows there is no `ps`, so ⌂ never shows. git is **not** a subprocess: the
  branch comes from reading `.git` and `HEAD` (SL:372-396).
- **Go mapping.**
  - `platform.FindAncestor(startPID, "claude", maxDepth)` with native per-OS probes (§2.5): macOS `sysctl kern.proc.pid`
    through `golang.org/x/sys/unix`, Linux `/proc/<pid>/stat` plus `btime`, Windows Toolhelp32 plus `GetProcessTimes`
    (research Q4a).
  - The start time is **truncated to whole seconds** and stored as a float (`1794615009.0`) under the legacy `proc_start`
    key, so `int(win_ms // 60000)` flips on the same refresh (P3r1 §A7).
  - git stays pure file reads.
  - D4-EX-1 applies on Windows (⌂ may show). Behavior differences on macOS and Linux are listed in tension T2.
- **BCs:** 009, 023, 080. **Pitfalls:** PR-14 (removed from this path), PR-22.

### IM-20 `hashlib.sha1` cache key

- **Python use.** `hashlib.sha1(directory.encode("utf-8", "replace")).hexdigest()[:16]` (SL:405). A lone surrogate is
  encoded as `?` before hashing (BC-SL-009/010).
- **Go mapping.** `crypto/sha1` over `pyfmt.EncodeUTF8Replace(s)` `[str]`, plus
  `//nolint:gosec // non-cryptographic cache key, file-name format shared with legacy (T-062)` (research Q6).
- **BC:** 010.

### IM-21 `colorsys.hsv_to_rgb`

- **Python use.** SL:147, inside `heat`.
- **Go mapping.** A private 12-line port in CPython's order (`i = int(h*6.0)`, `f = h*6.0 - i`, …; P3r1 §A1 BC-SL-056)
  with IM-10 conversions. The 10 cell colors and the edge values listed in BC-SL-056 serve as the table.
- **BC:** 056. **Pitfall:** PR-15.

### IM-22 `print` and stdout encoding

- **Python use.** `print("\n".join(rows))` writes once and adds a trailing `\n` (SL:1234). Stdout is strict UTF-8 (owner
  ruling (a), BC-SL-076). A rendered str holding a lone surrogate raises `UnicodeEncodeError` at the print, which degrades
  with the earlier writes kept (CP-S17).
- **Go mapping.** The output is built in a `bytes.Buffer`. Before the single `Write`, a `pyfmt.HasSurrogate` check runs
  over the strings that reach it; if one is found, the result is degraded. LF only (research P25). The degraded line is
  pure ASCII.
- **BCs:** 001, 003, 076. **Pitfall:** PR-17.

### IM-23 `os.path.isfile` / `os.stat` on a non-str `transcript_path`

- **Python use.** SL:1010-1015. A list, dict or float raises `TypeError` (CP-S16, degraded). An int or bool is used as
  a **file descriptor** (BC-SL-088).
- **Go mapping.** list/dict/float return `errDegraded`. int/bool go through `platform.StatFD(n)`: `/dev/fd/n` on Unix,
  "not a regular file" on Windows. Since the harness captures output through pipes (BC-SL-088), both sides return None.
  Non-pipe descriptors are not part of the corpus.
- **BC:** 088. **Pitfall:** PR-21.

---

## 2. Package and file layout (PLAN §6 + OD-103)

PLAN §6 (`docs/PLAN.md` §6) names `cmd/hylo`, `internal/statusline`, `internal/cost` (cost history and backfill),
`internal/config` and `internal/platform`. OD-103 adds `internal/pyfmt`. P1 touches exactly these six packages. Dependency
direction:

```text
cmd/hylo ──> internal/statusline ──> internal/cost ──> internal/pyfmt
                 │      │                                   ^
                 │      └────────> internal/config ─────────┤
                 └──────────────> internal/platform ────────┘
```

`internal/pyfmt` imports only the standard library. `internal/platform` adds `golang.org/x/sys`, the one justified runtime
dependency in P1 (research Q5, porting-decision §4.2).

### 2.1 `cmd/hylo` (subcommand dispatch)

| File | Content |
|---|---|
| `main.go` | `func main() { os.Exit(run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr)) }`; dispatch with stdlib `flag` per subcommand (RESUME step 1) |
| `statusline.go` | `hylo statusline`: builds `statusline.Env` from `config.Load` and `platform`; **ignores unknown arguments** (legacy reads only `--subagent` from `sys.argv[1:]`, SL:1240) and **never returns non-zero**. `--subagent` handling is a spec decision (tension T8) |
| `version.go` | `hylo version` |
| `config.go` | `hylo config validate` (OD-102: exits non-zero on the same errors that produce the D4-EX-3 line) and `hylo config path` (OD-95) |

```go
func run(args []string, stdin io.Reader, stdout, stderr io.Writer) int
func runStatusline(args []string, stdin io.Reader, stdout, stderr io.Writer) int // always 0
```

### 2.2 `internal/statusline` (the port target, split by function family)

| File | Legacy source | BCs |
|---|---|---|
| `statusline.go` | `main` SL:1200-1235; orchestration order (BC-SL-077) | 003, 053, 077 |
| `guard.go` | guard SL:1238-1245; `errDegraded`, `degradedLine`, `recover` | 001 |
| `env.go` | injection seams (§3) | — |
| `input.go` | stdin decode SL:1201-1206 | 002, 076 |
| `width.go` | `visible` SL:151-153, `term_cols` SL:1185-1190, `trim_to_fit` SL:1193-1197 | 004, 005, 054, 055, 090 |
| `theme.go` | SGR palette, `SEP`, pills, glyphs SL:127-137, all from config (D15; OD-02) | — |
| `lane.go` | pill, model, project SL:441-462 | 006, 007, 008, 058, 059 |
| `git.go` | `git_branch`/`git_segment` SL:364-413 | 009, 010 |
| `context.go` | `heat`/`truecolor` SL:140-148, `fmt_ctx` SL:418-437, `mix_labels`/`mix_segment` SL:1157-1183, cache hit SL:477-479 | 011, 012, 013, 056, 057, 060 |
| `limits.go` | `effective_rl` SL:298-312, windows SL:487-532 | 014, 015, 016, 017, 018, 061, 093 |
| `session.go` | lines, timer, API time, ⌂ SL:534-563; `_fmt_lines` SL:849-860 | 019, 020, 021, 022, 063, 064, 081 |
| `tokens.go` | token segment SL:565-600; `_fmt_tok_c` SL:863-873 | 024, 062 |
| `cost.go` | `$`, `$/h`, ⛏ SL:601-636 (⛏ sits inside the `$` block, P3r6 R1-1/BC-SL-027) | 025, 026, 027, 082, 083 |
| `transcript.go` | `_mix_counts` read window, splitlines, dedup, usage, compaction SL:999-1119, 1150-1154 | 030-037, 065, 066, 067, 088 |
| `transcript_mix.go` | composition per block SL:1120-1149 | 038, 071, 072 |
| `transcript_turn.go` | `_iso_ts`, `_finish_turn`, turn machine SL:977-996, 1064-1087 | 039, 069, 094, 095 |
| `transcript_wshape.go` | D4-EX-2 W-predicates (Go-only) | 068 (replaced), 098, 099 |
| `mixcache.go` | mix cache name, `mixv6` reset, `cur` as raw `Value`, OD-32 reader rule SL:1016-1038 | 031, 070, 100, 103 |
| `telemetry.go` | `QUERY` SL:102-123, `fetch_sample` SL:158-187 | 040 |
| `sample.go` | `get_sample` SL:315-359, `_norm_pt` SL:652-656 | 041, 042, 091, 092 |
| `row2.go` | `render_telemetry`, `serving_state`, fields SL:693-835 | 043-047, 049-051, 074, 075, 084, 085, 086 |
| `sparkline.go` | `sparkline` SL:659-690, `TRACE_KEYS`, scale SL:644-649 | 048, 073 |
| `cache.go` | `load_cache`/`save_cache` SL:190-206; file-name rules SL:406, 1017, 1215 | 052, 078 |
| `testdata/` | `pyhooks/sitecustomize.py`, `cases/`, `goldens/`, `parity/exclusions.json`, generators (§5) | 089, 090 + harness |

Exported API sketch:

```go
package statusline

// Main runs one refresh: reads stdin, renders, writes stdout. Always returns 0.
func Main(stdin io.Reader, stdout, stderr io.Writer, env Env) int

// Render is the orchestrator behind Main (BC-SL-077 order). On errDegraded the
// caller prints degradedLine; cache writes made before the error persist.
func Render(stdin []byte, env Env) ([]byte, error)

const degradedLine = "\x1b[90mstatusline degraded\x1b[0m\n" // 29 bytes, BC-SL-001
var errDegraded = errors.New("statusline degraded")

type Env struct {
	Now     func() float64        // Python time.time() value; HYLO_TEST_NOW in the binary
	Loc     *time.Location        // naive transcript timestamps (BC-SL-069)
	Getenv  func(string) string   // COLUMNS only (protocol input, not config)
	Config  *config.Statusline    // resolved once (D15)
	Cache   CacheStore            // paths.cache_dir (OD-101); temp dir in tests
	Metrics MetricsClient         // statusline.telemetry.url; httptest fake in tests
	Proc    ProcStarter           // platform.FindAncestor; fake in tests
	Files   FileSystem            // transcript and .git reads; os-backed by default
	Cwd     func() string         // git fallback when no project dir (SL:373)
}

type CacheStore interface {
	Load(name string) pyfmt.Value      // never fails: unreadable → empty object (SL:190-195)
	Save(name string, v pyfmt.Value)   // never fails: errors swallowed (SL:198-206)
}
type MetricsClient interface {
	Query(ctx context.Context, promql string) ([]byte, error)
}
type ProcStarter interface {
	WindowStart() (start float64, ok bool) // whole seconds, as float64
}
type FileSystem interface {
	Stat(name string) (size int64, regular bool, err error)
	ReadFrom(name string, off int64, max int) ([]byte, error) // transcript window
	ReadFile(name string) ([]byte, error)                     // .git, HEAD
}
```

### 2.3 `internal/cost` (cost history; PLAN §6, OD-36)

PLAN §6 puts "cost history and backfill" in `internal/cost`, and OD-36 makes the backfill's package the owner of the
cost history. P1 places only the **read and record side** here; the backfill arrives in P6. The coloring rules stay in
`internal/statusline/cost.go`.

| File | Legacy source | BCs |
|---|---|---|
| `history.go` | `record_cost` SL:224-237, `cost_thresholds` SL:240-262, constants SL:217-221 | 028, 029, 079, 101, 102 |

```go
package cost

type Thresholds struct{ P75, P95 float64 }

// Record stores this session's exact cost (src "cc"), throttled to one write
// per record_throttle_s (T-022, strict <). The sid stays a raw pyfmt.Value so
// that the OD-30 string-form key rule applies.
func Record(store Store, cfg *config.Cost, now float64, sid pyfmt.Value, lane string, usd float64, apiMs pyfmt.Value)

// ForLane returns the (usd, rate) percentile pairs excluding sid, or nil on a
// cold start (< min_sessions; T-020, inclusive).
func ForLane(store Store, cfg *config.Cost, now float64, lane string, sid pyfmt.Value) (usd, rate *Thresholds)
```

### 2.4 `internal/config` (P1 key subset)

| File | Content |
|---|---|
| `registry.go` | `Key{Name, Type, Default, Unit, Op, Rationale, RationaleCode, Class}`; `Registry() []Key`; `EnvName(key)` = `HYLO_` + upper snake (OD-01); build-time collision test |
| `statusline_keys.go` | the P1 subset (below), one entry per threshold row with its legacy default, comparison operator and rationale (D15; CV-19) |
| `load.go` | `Load(opts) (*Config, error)`: config file, then `HYLO_*`, then defaults; `~` expanded in every path (OD-61); unknown `HYLO_*` warned (OD-01) |
| `types.go` | `Seconds` (PR-22 validation), `Bool` (OD-05 grammar), `Int`, `Float`, `URL`, `Enum`, `List` (comma-encoded in env, OD-74), `Path` |
| `errors.go` | `type Error struct{ Key, Value, Reason string }`; `func (e *Error) StatusLine() string` gives `hylo: config error: <key>=<value> (<reason>)` (OD-102) |

**P1 key subset.** These come from P4r7 §B.2.1 (79 rows: CFG 62, NC 15, EXT 2), and every rationale is resolved by OD-57
(E-0, E-A, E-B..E-G).

- **Telemetry (T-001, 003, 004, 005, 016/017 inside the query):** `statusline.telemetry.{url, ttl_s, fresh_s,
  keep_dead_s, timeout_s, query}`. `url` default `http://192.0.2.10:8428` (SL:73), `ttl_s` 4 (SL:74), `query` byte-identical
  to SL:102-123.
- **Rows and layout (T-002, 014, 116):** `statusline.rows`, `statusline.narrow_cols`.
- **Sparkline (T-006..009, 045, 046):** `statusline.sparkline.{enabled, trace, points, max_age_s, min_gap_s,
  history_cap, scale, colors}`. `trace` is an enum `rate|kv|ttft` (SL:89, 644).
- **Git (T-013):** `statusline.git.{enabled, ttl_s}`.
- **Limits (T-010, 031..035):** `statusline.limits.{keep_s, windows, projection_min_elapsed, projected_bands,
  absolute_bands, countdown_max_factor}`.
- **Context and units (T-027..030, 037, 042):** `statusline.context.{cells, plain_max, red_from}`,
  `statusline.units.{context, lines, tokens}`, `statusline.theme.heat`.
- **Timers and window age (T-025, 026, 038..040):** `statusline.timer.{min_ms, api_min_ms}`,
  `statusline.window_age.{max_depth, ps_timeout_s, min_margin_ms}`. `ps_timeout_s` becomes inert with the native probe
  (risk RK-6).
- **Cost (T-012, 018..024, 043, 044):** `statusline.cost.{basis_min_mtok_month, window_s, min_usd, min_sessions,
  cold_yellow_usd, record_throttle_s, rate_min_api_ms{cc,other}, percentiles, burn_min_api_ms, basis_min_shown_usd}`.
- **Row 2 widgets (T-011, 015, 047..053, 107, 108):** `statusline.idle.{after_s, running_below}`,
  `statusline.ttft.{min_samples, integer_from_s, yellow_s}`, `statusline.queue.yellow`,
  `statusline.kv.{cells, host_yellow_pct, host_shown_pct}`, `statusline.power.{wall_red_w, wall_yellow_w}`.
- **Transcript (T-054..060):** `statusline.transcript.{read_cap_bytes, dedup_memory}`,
  `statusline.turn.{dim_below_out, floor_tps, stale_factor}`, `statusline.tokens.rebuild_excess`,
  `statusline.composition.image_chars`.
- **Glyphs (OD-02):** `statusline.glyphs.*`, one code point and one column each; the sparkline glyph key holds exactly 8
  ordered glyphs.
- **Shared:** `routing.local_model_prefixes`, a comma list (ENV-01). The default is in tension T3.
- **`paths.cache_dir`.** Under OD-101 its default is **not** the legacy literal `~/.cache/dgx-llm` (SL:78). It is
  hylo's OD-95 location built by `internal/platform.CacheDir()`: `$XDG_CACHE_HOME/hylo` or `~/.cache/hylo` on macOS and
  Linux, `%LOCALAPPDATA%\hylo` on Windows. The registry entry records this as the **one explicit owner exception** to D15's
  "defaults equal legacy until cutover", citing OD-101.
- **Named constants (NC, not keys), each with a "why not config" comment:** T-036, 041, 061-064, 106, 109-115, 133. Two
  of them are file-name formats shared with legacy: 40-character sid truncation (T-061) and the sha1 prefix (T-062).
- **Dropped:** T-117 (OD-14).
- **Not in the register: the SGR palette** (SL:127-134), `SEP` (SL:128) and the pill codes (SL:130). D15 lists "colors"
  as configuration, but the register has no rows for these; see tension T9.

```go
package config

type Statusline struct {
	Rows       int
	NarrowCols int
	Telemetry  struct {
		URL                         string
		TTL, Timeout                Seconds
		FreshS, KeepDeadS           float64
		Query                       string
	}
	// … one field per key above
}
func Load(opts LoadOptions) (*Config, error) // *Error for an invalid value
func EnvName(key string) string
```

### 2.5 `internal/platform`

| File | Content |
|---|---|
| `paths.go`, `paths_unix.go`, `paths_windows.go` | `CacheDir()`, `ConfigDir()`, `StateDir()` built explicitly per OD-95/OD-101 (never `os.UserCacheDir`; research §4c) |
| `proc.go` | `type ProcInfo struct{ PID, PPID int; Comm string; Start time.Time }`; `FindAncestor(startPID int, name string, maxDepth int) (float64, bool)` walks from `os.Getppid()` exactly as SL:278-292 (checks the parent first, at most 6 levels per T-025, stops at pid ≤ 1, matches `basename(comm) == "claude"` with `.exe` stripped case-insensitively on Windows) |
| `proc_darwin.go` | `unix.SysctlKinfoProc("kern.proc.pid", pid)`: `Eproc.Ppid`, `P_comm`, `P_starttime` |
| `proc_linux.go` | `/proc/<pid>/stat`, parsed after the last `)`; start = `btime` + ticks/`CLK_TCK` |
| `proc_windows.go` | `CreateToolhelp32Snapshot` + `GetProcessTimes`; PID-reuse guard (the parent was created before the child) |
| `proc_other.go` | `//go:build !darwin && !linux && !windows`: returns not found |
| `fd_unix.go`, `fd_windows.go` | `StatFD(n int) (regular bool)` for IM-23 |

### 2.6 `internal/pyfmt` (one package, four files, OD-103)

| File | Contents | Pitfalls |
|---|---|---|
| `num.go` | `Num` (int64 / `*big.Int` / float64 / bool) and Python arithmetic (`Add`, comparisons, with bool counting as int); `Round`, `RoundN`, `F`, `D`, `Int`, `Ceil`, `FloorDiv`, `Mod`, `FloorDivInt`, `ModInt`, `Max`, `Min`, `MaxSeq`, `Repr`, `ParseInt`, `ParseFloat` | PR-01..06, PR-10, PR-15 (convention), PR-18 |
| `json.go` | `Value`, `Member`, `Kind`; `Decode(b, mode)`; `Dumps`; `DumpsLen`; `Str` (Python `str()`/`repr` of values); ordered-object `Get/Set/Delete` | PR-07, PR-08, PR-09, PR-10, PR-16, PR-19 |
| `str.go` | WTF-8-aware `Len`, `Truncate`, `HasSurrogate`, `EncodeUTF8Replace`; `Strip`, `RStrip`, `SplitN` (`split(None, n)`), `RSplit1`, `SplitLinesBytes`, `SubNonWord`; `PosixNormpath`, `NtNormpath`, `Basename` | PR-11, PR-12, PR-13, PR-20 |
| `time.go` | `TimeFloat` (float ns / 1e9), `FromISOFormat` (3.11 grammar), `LocalToUnix` (CPython `_mktime` port); `Strftime` reserved for P3/P4 (ledger `t`, hook log) | PR-14 |

Each file has a committed **CPython-generated** expectation table. The generator scripts live in
`internal/pyfmt/testdata/gen/` and run under the pinned 3.11 oracle (OD-104). Each file also has `go test -fuzz` targets:
`Decode`, `DumpsLen`, `FromISOFormat`, `ParseFloat` (research Q6).

---

## 3. Purity boundary and determinism seams

### 3.1 The boundary

The core cannot be one pure function, because legacy **reads back its own writes within one refresh**:

- `effective_rl` writes the session cache (SL:307-308);
- `get_sample` re-reads it and writes it again (SL:323, 351/355);
- `claude_window_start` re-reads it (SL:273).

A write that fails on disk must stay invisible to the next read. With a sid containing `/`, legacy's
`get_sample` sees the old file because the replace failed (BC-SL-078). An in-memory overlay would get that wrong. The
design is therefore **pure widgets plus an ordered effect script**:

- **Pure core** (no clock, no I/O, no env). The functions are `renderLane(LaneInput) ([]string, error)`,
  `renderTelemetry(TelemetryInput) ([]string, error)`, `trimToFit(row, cols)`, `mixLabels`, `sparkline`, `heat`, all the
  format helpers, `finishTurn`, `parseTranscriptWindow(state, blob) (state', error)` and `nextSampleState(...)`. Their
  inputs are plain values: the decoded stdin `Value`, `now float64`, the config, the mix result, the rate-limit dict, the
  sample, history, `winStart`, the branch, and the thresholds. Each one is table-testable without a temp directory.
- **Effect script** (`statusline.Render`). It calls the seams in **exactly** legacy's order (BC-SL-077, P3r1 §A8) and
  interleaves the pure renders where legacy can raise, so a degraded run leaves the same cache files:

| # | Step | Legacy | Seam | Can degrade? |
|---|---|---|---|---|
| 0 | config resolved | (import, SL:73-100) | `config.Load` | D4-EX-3 line, **before any write** |
| 1 | stdin decode | SL:1201-1206 | `pyfmt.Decode(ModeText)` | no (invalid gives `{}`) |
| 2 | transcript parse, then mix-cache write | SL:1213, 1150 | `Files`, `Cache` | CP-S14/S16 and the legacy CP-T paths (Go: D4-EX-2 skip, no degrade) |
| 3 | `effective_rl` (session-cache write if stdin carries a non-empty dict) | SL:1216, 307-308 | `Cache`, `Now` | no |
| 4 | `get_sample` when ROWS ≥ 2: fetch, then session-cache write | SL:1217-1218 | `Metrics`, `Cache`, `Now` | no |
| 5 | row-2 render (only under the width rule) | SL:1224-1227 | pure | CP-N01/N02 |
| 6 | window start (may write `proc_start`) | SL:1229, 287-288 | `Proc`, `Cache` | no |
| 7a | lane: badge, model, project; git segment (git-cache write) | SL:441-462, 411 | `Files`, `Cache`, `Cwd` | CP-S01..S04 (S04 at SL:405, before the git write) |
| 7b | thermometer, composition, cache hit, limits, lines, timer, ⌂, tokens | SL:463-600 | pure | CP-S05..S13 |
| 7c | `record_cost` (cost-history write), then `cost_thresholds` | SL:606-607 | `internal/cost` via `Cache` | CP-S15 (at `s.get(sid)`, before the write) |
| 7d | `$`, `$/h`, ⛏ | SL:608-636 | pure | no |
| 8 | trim, surrogate check, single write | SL:1232-1234 | stdout | CP-S17 (after every write) |

### 3.2 Injection seams for the parity harness (RESUME P1 step 3; OD-58, OD-101, OD-104)

| Nondeterminism | Legacy side (harness only, `legacy/` untouched, D10) | Go side | Notes |
|---|---|---|---|
| **Clock** | `testdata/pyhooks/sitecustomize.py` on `PYTHONPATH` freezes `time.time`, `time.strftime`, `time.localtime` and `time.gmtime` from `HYLO_TEST_NOW` (OD-58 mode 1, stepped between refreshes). Run with `-s`, never `-I`/`-E`, which would drop the shim (P5r5 §B.4) | `Env.Now`; the binary honors `HYLO_TEST_NOW` (a decimal string parsed by both sides; research P20) | The status line has no hook-style early stop, so mode 2 is not needed in P1 |
| **Metrics** | `DGX_SL_VM_URL=<httptest URL>`. The proxy bypass at SL:168 means no proxy variables interfere | `HYLO_STATUSLINE_TELEMETRY_URL=<same URL>`; `Transport{Proxy: nil}` | Fake VictoriaMetrics = DTU-3 (pass-8 §2.7). Failure modes: closed listener, 5xx, garbage. Never timeouts (research Q3b) |
| **Process start** | pre-seed `"proc_start": <float>` in `statusline-<sid>.json`; legacy returns it without running `ps` (SL:273-275) | Go reads the same key first (parity), so the binary never probes in seeded cases; unit tests use a fake `ProcStarter` | Unseeded cases on CI agree (no `claude` ancestor on either side; Windows: legacy has no `ps`) |
| **Cache dir** | temp `HOME` **and** `USERPROFILE`, so legacy writes `$HOME/.cache/dgx-llm/` (SL:78) | `HYLO_PATHS_CACHE_DIR=<temp>/hylo-cache` (OD-101); `XDG_CACHE_HOME` and `LOCALAPPDATA` also point into the temp tree | The two sides use different directories under OD-101, so cache comparison is **per file name** (§5.3) |
| **Time zone** | `TZ` per case: UTC + America/Chicago + Europe/London (P5r5 §B.4) | `Env.Loc`. The binary takes `time.Local` from `TZ` on Unix. Go ignores `TZ` on Windows (research P19), so naive-timestamp cases on Windows run as Go table tests with an explicit `Loc` against CPython goldens (P5r3 §B.4 Windows row) | — |
| **Interpreter** | explicit absolute path, a harness setting (OD-104), e.g. `HYLO_PARITY_PYTHON`; never PATH discovery | — | Tier A skips with a message when it is unset locally; CI always sets it to the setup-python output path (tension T4) |
| **Locale / stdio** | `LANG=en_US.UTF-8`, every `PYTHON*` variable unset except `PYTHONPATH`; the shim reconfigures stdin/stdout to `utf-8` strict with `newline="\n"` (ruling (a); research P25 on Windows) | always UTF-8, LF | — |
| **Env from scratch** | DET-43; no `*_proxy`; `COLUMNS` per case | GP-1..GP-6 unset or fixed (`GODEBUG`, `SSL_CERT_*`, proxies, `TMPDIR`, `HOME`) | — |

`HYLO_TEST_NOW` is a **harness hook, not a setting**. It is not a D15 key because it changes no behavior an operator would
configure. It is documented in the config reference under "test hooks" (risk RK-5).

---

## 4. Translation order

The order follows RESUME P1 step 5 (helpers, row 1, parser, row 2 + metrics, cost history, window age) and market-intel
R3 (`pyfmt` before any widget). The harness (H) starts with S0 and grows with each step. Confidence: **HIGH** = mechanical
given pinned oracle tables; **MEDIUM** = a sizeable Python-semantics surface or exact ordering that the tables may not
exhaust; **LOW** = no oracle exists for the real behavior.

| Step | Content | BC set | Table tests and goldens | Confidence (reason) |
|---|---|---|---|---|
| **S0** skeleton + CI | `go.mod` (`go 1.26.0`, `toolchain go1.27.4`), `cmd/hylo` dispatch, `.gitattributes` (`testdata/** -text`), CI on ubuntu-24.04 / macos-15 / windows-2025 + gitleaks, a setup-python 3.11 step from day one (research Q7; OD-104) | — | `gofmt`, `vet`, `test`; dispatch test asserting that `statusline` exits 0 for any argv | HIGH (standard scaffolding) |
| **S1** `internal/pyfmt` | four files (§2.6) | 067, 069, 071, 096 (helper level); helper halves of 011, 012, 019, 020, 028, 062, 064 | CPython-generated tables per function. **BC-SL-096: 63 rows.** BC-SL-067 acceptance set (BOM, `\xff`, `\r`, depth 995/1000, NaN, `1e400`, duplicates, `\ud800`). BC-SL-069 grammar under the TZ grid. PR-14 goldens (10,893 rows). `Round`/`F` boundary rows (`999.5→1000`, `2.675→2.67`, `0.125→0.12`). FMA rows on arm64. Fuzz: `Decode`, `DumpsLen`, `FromISOFormat`, `ParseFloat` | **MEDIUM overall.** `num`/`str`: HIGH (closed-form, oracle-tabled). `time`: HIGH for `LocalToUnix` (0 mismatches in Phase 0), MEDIUM for the breadth of the 3.11 `fromisoformat` grammar. `json`: MEDIUM (WTF-8 strings, depth limit, big ints, NaN tokens, ordered dict semantics) |
| **S2** frame | config subset + D4-EX-3 + `config validate`; guard; stdin; width/trim; `CacheStore`; orchestrator skeleton; `Env` seams | 001, 002, 003, 004, 005, 052, 054, 055, 076, 077 (skeleton), 078, 087, 090 | 29-byte degraded line; stdin modes table (P3r1 §A9); `COLUMNS` table (`" 80 "`, `"٨٠"`, `"1_000"`, `"+72"`, `-5`, a 4,301-digit negative); trim breakpoints BC-SL-090; ROWS × COLUMNS matrix (T-116); **D4-EX-3: one test per key class** (number, boolean, URL, enum) asserting the exact line, exit 0, stderr detail, no cache writes; `hylo config validate` exit code | HIGH. BC-SL-087 is a spec'd deviation, not a port. 077 is finished in S8 |
| **S3** row-1 widgets | lane, model, project, git, thermometer, composition, cache hit, limits + `effective_rl`, lines, timer, ⌂ formatting and gate, tokens, `$`/`$/h`/⛏ formatting | 006-022, 024-027, 056-064, 081-083, 093 | One table per review row (`docs/STATUSLINE-REVIEW-2026-11-13.md` #1-#12; PLAN §8): timer `% 60` (#9.1), half-up cells (#5.2), plain ≤ 50 / bold red ≥ 85 (#5.1), pace bands and 0.9 boundary (BC-SL-061), countdown 1.15 gate, rate-limit sequence and sticky CP-S09 (BC-SL-093), the 10 git layouts (#3, `.git` created at runtime), `normpath` POSIX/NT goldens (BC-SL-059), heat cell colors (BC-SL-056, arm64), every CP-S row as a degraded case | **HIGH.** Exceptions at MEDIUM: 017/022 (float divmod and the FMA gate), 058 (`repr` of nested containers and big ints), 059 (per-OS paths) |
| **S4** transcript parser | read window, splitlines, decode, dedup, usage, rebuild, compaction, composition, turn machine, mix cache, **D4-EX-2** | 030-039, 065-072, 088, 094, 095, 098, 099, 100, 103 (068 replaced) | **BC-SL-094 (20-row turn table)**, **BC-SL-099 (21 D4-EX-2 rows** with exact expected mix caches), BC-SL-066 (600 KB line takes two refreshes), BC-SL-035/036 (5-call rebuild scenario, `rb=2`), BC-SL-037 (compaction), BC-SL-070 (per-code-point sanitizer: `é`×50 → 40 `_`), BC-SL-103 (`t0` null, `out` non-numeric kept verbatim), OD-32 reader rule, BC-SL-088 type table | **MEDIUM.** The largest stateful surface (156-line `_mix_counts`, P1r3 smells). Decoder edges flow straight into counts, and the W-predicates must be exact so that a skipped line leaves no partial mutation (BC-SL-099 T04+ out-only). The pinned tables (094, 099) are HIGH |
| **S5** row 2 + metrics client + session cache | `fetch_sample`, `get_sample` state machine, history points, freshness ladder, health, queue, KV, throughput, sparkline, TTFT, power, idle, mine | 040-051, 053, 073-075, 084-086, 091, 092 | **BC-SL-091 11-step sequence** with exact cache JSON after each step (key order included); BC-SL-092 seeded gap; KV cell table (BC-SL-074); sparkline glyphs and colors (BC-SL-073); NaN/Inf rows (BC-SL-075; latent in production per P3r7); TTFT boundaries (BC-SL-086); idle 300.0/300.5 (BC-SL-084); fetch edge table (non-2xx, non-dict payload, `value` TypeError drops the whole sample, `"a5"` skipped (`ValueError` → `continue`, SL:179), first-wins, `up:<job>`) | **HIGH** for the widgets. MEDIUM for 040 (the catch-list subtleties) and 091 (inherited key order) |
| **S6** cost history | `internal/cost` Record/ForLane; `$`/`$/h` coloring | 028, 029, 079, 101, 102 (+ coloring of 025, 026) | **BC-SL-101: 20 seeded sessions, 12 segment goldens + 5 scenarios**; BC-SL-102 throttle (+59.999 s vs +60.000 s) and exact write format; OD-30 table test pinning the string-form key (BC-SL-079) | HIGH (fully pinned goldens; 079 is a deliberate, ruled difference) |
| **S7** window age | `internal/platform` probes ×3 OSes; `CacheDir` per OS | 023, 080 (022 gate already in S3) | Per-OS probe unit tests (self process and parent; `.exe` strip; depth cap; pid ≤ 1 stop; whole-second truncation); **D4-EX-1** Windows test with a fake `ProcStarter` that shows ⌂; seeded `proc_start` parity cases | **MEDIUM.** Parity is HIGH through seeding. Real-world correctness on Linux (`CLK_TCK`, npm installs whose comm is `node`) and Windows (PID reuse) is LOW-MEDIUM, with no oracle |
| **H** harness | shim, case runner, env translation (§5.2), fake VictoriaMetrics, transcript generator, cache-swap tests, exclusion-list machinery, Tier A/B; Tier C nightly | all (corpus) | §5 | MEDIUM (cross-OS process spawning, Windows Python under the shim) |
| **S8** goldens + burn-down | row goldens, full corpus on 3 OSes, review-rule table sweep, Tier C | 089, 090, 077 (full) | BC-SL-089 goldens A/B/C (198-column row 1, 12 segments), multi-step cache comparison after every step (BC-SL-077), Tier B `*.windows.golden` for root-path cases | MEDIUM (Windows CI and hidden P27-class exception paths, which only Tier C can surface) |

---

## 5. Parity harness design (summary)

### 5.1 Tiers (research Q3c; OD-104)

| Tier | What | Where | Gate |
|---|---|---|---|
| A, live differential | CPython 3.11.x (explicit absolute interpreter path) runs `legacy/dgx_statusline.py` under the shim; Go runs in-process **and** as the built binary for a subset; byte comparison per step | ubuntu-24.04, macos-15 (arm64), windows-2025 | **Yes: the P1 exit criterion** (PLAN §7) |
| B, committed goldens | `-update` writes **Python's** output (never Go's) on Linux; Go must match on every OS; `*.windows.golden` for OS-dependent cases (BC-SL-059 root paths) | all OSes, no Python needed | Yes |
| C, differential fuzz | generator of random valid stdin/transcripts/metrics; both sides; diff | Linux nightly | No (finds P27-class divergences; run clean for an owner-picked number of nights before P1 is declared done, porting-decision §7) |

### 5.2 Fixture classes (synthetic only; public repo, CLAUDE.md hygiene)

- **Case model.** Each case is a directory (research Q3b) containing:
  - `stdin.json.tmpl`, with paths templated into the per-case temp tree;
  - `settings` declared **once** and translated by the harness: legacy gets `DGX_SL_*` and `LOCAL_MODEL_PREFIXES`, Go gets
    `HYLO_*` (OD-05). A setting outside the Go typed domain is legal **only** in a D4-EX-3 case;
  - `metrics.json`, or a mode: `down` / `500` / `garbage`;
  - an optional cache seed;
  - an optional transcript generator spec and `steps` (each step advances the clock and appends transcript lines).
- **stdin.**
  - Normal sessions on both lanes and with an unknown lane.
  - Absent and null objects.
  - The newer optional fields: `output_style.name`, `pr.kind`, `workspace.repo.{host,owner,name}`,
    `prompt_cache.last_miss_cause`/`miss_causes`, `rate_limits.spend_limit` with and without its dollar fields
    (market-intel §6.1).
  - Every CP-S01..S17 trigger, and invalid UTF-8 / BOM / lone surrogates (BC-SL-076).
- **Transcripts** (a committed Go generator; RESUME step 4):
  - split assistant messages that repeat `usage`, a `compact_boundary`, a line over 512 KB;
  - tool_results interleaved inside a message, a cache rebuild, empty thinking blocks, images in tool_results;
  - non-ASCII and astral text, invalid UTF-8, BOM, `\r` separators, NaN tokens, deep nesting;
  - the CP-T shapes, which go to the D4-EX-2 list.
- **Metrics (DTU-3):**
  - healthy; vLLM down; LMCache down (connector present); stale (closed listener); 5xx; garbage JSON;
  - NaN/±Inf values (latent in production per P3r7, still spec'd);
  - fewer than 20 TTFT samples; the idle ☾ and pick ⛏ series; a missing series (no fabricated zeros).
- **Cache seeds:** `proc_start`; legacy `[t, v]` history points; `rl`/`rl_ts`; the BC-SL-101 20-session
  `cost-history.json`; a legacy-written poisoned mix cache (BC-SL-100); the T05~ state (BC-SL-103).
- **Git layouts**, created at test time (a committed `.git` directory is not tracked): directory, worktree pointer file,
  detached HEAD, a stray plain `HEAD`, nested repos, a non-repo (review #3).
- **Cache-swap cases.** Python writes and Go reads, and the reverse, for all four caches (ruling Q-b, research Q3b).

### 5.3 What is compared

- **Per step:** stdout **bytes** and the **exit code**.
- **Per step:** each named cache file, byte for byte. The match is by file name across the two directories: legacy
  `$HOME/.cache/dgx-llm/<name>`, Go `<paths.cache_dir>/<name>` (OD-101). Files named `<name>.<random>` (mkstemp temps)
  are ignored, because legacy leaks them on a failed replace and Go cleans them up (BC-SL-078; tension T2).
- **Never compared:** stderr, and in particular Python tracebacks. Legacy's stderr is invisible to Claude Code (SL:42).
  The D4-EX-3 stderr detail is asserted by its own Go table tests.

### 5.4 Named exclusion list (OD-105)

`internal/statusline/testdata/parity/exclusions.json` (JSON, so the zero-dependency P1 budget holds). One entry per
excluded case: `{id: "D4-EX-1"|"D4-EX-2"|"D4-EX-3", case, expected_output_file, table_test}`. The harness **fails** in
three situations: an excluded case has no matching table test; the Go output of an excluded case differs from its own
expected file; or an entry is a glob ("no blanket exclusions").

| Exclusion | Cases | Dedicated tests |
|---|---|---|
| D4-EX-1 (⌂ on Windows) | Windows cases whose fake probe returns a start | `TestWindowAge_D4EX1_Windows*` |
| D4-EX-2 (wrong-shape transcript lines) | CP-T01..T07 positives, T05~ open at the end, the two-refresh T05~ → U9, the legacy-poisoned cache reader (OD-32) | the 21 BC-SL-099 rows + BC-SL-100/103 rows |
| D4-EX-3 (config-error line) | one invalid value per key class (number, boolean, URL, enum) and each legacy-accepted value outside the Go domain (tension T10) | `TestConfigError_D4EX3_{Number,Boolean,URL,Enum}` + `config validate` |

### 5.5 CI matrix

- **Operating systems:** ubuntu-24.04, macos-15 (arm64, the PR-15 FMA detector) and windows-2025 for every change
  (CLAUDE.md); plus a Go 1.26.x leg on Linux next to the `go.mod` toolchain.
- **Python:** `actions/setup-python` installs CPython 3.11 on all three OSes (OD-104). The resolved patch version is
  recorded in the Tier B golden metadata (risk RK-4).
- **Race detector:** `-race` on Linux and macOS.
- **Tier C:** nightly on Linux, not gating.
- **Push hygiene:** gitleaks with `--log-opts="--all"`.

---

## 6. Target-specific enhancements (output-neutral only)

What Go gives without changing a byte of output:

1. **One static binary per platform** (PLAN §3 goal; `CGO_ENABLED=0`, research Q7). No interpreter and no venv to keep
   aligned. This removes the PATH-dependent interpreter choice that OD-104 records for legacy (an interactive terminal and
   a login shell resolve different interpreters).
2. **No interpreter start-up on each refresh.** Research Q3c measures about 30-60 ms of Python start-up per run. The
   status line runs on every 4 s tick and every assistant message (T-001, T-134; P4r7 P-1), so the refresh is far below
   Claude Code's 300 ms debounce.
3. **No `ps` subprocesses.** When legacy's walk fails it re-runs on every refresh, costing up to 6 × 1 s (T-026; P4r7
   P-1). The native probe is microseconds. The latency gain is output-neutral; the probe's *result* differences are not,
   and are listed in tension T2.
4. **One clock read per render.** Output-neutral under a frozen clock; removes the live minute-straddle at SL:825-826
   (DET-08).
5. **A total network deadline** (OD-56) instead of 1.5 s per socket operation (worst case 3 s or more with dribbling,
   T-005). Corpus outputs are unchanged, because the harness has no slow cases.
6. **Typed config, validated once** (D15, OD-05). Every legacy-accepted value inside the Go domain renders identically.
   Values outside it are D4-EX-3 by ruling, not an enhancement.
7. **Reproducible builds and supply-chain attestations** at release time (research Q7). Not P1-gating.

No other behavior change is planned. The approved differences are D4-EX-1, D4-EX-2 and D4-EX-3 only; the further known
differences found during this design are listed as tensions (§7.1 T2), not adopted.

---

## 7. Tensions and open risks

### 7.1 Tensions (contradictions or frictions with settled decisions or docs; listed, not resolved)

| # | Tension | Evidence | What the owner would choose between |
|---|---|---|---|
| **T1** | **P1 daily-use parity vs the hylo cache dir from P1.** OD-96 makes the P1 success criterion "the owner's own daily use (byte parity on the owner's setup)". OD-101 points hylo at its own cache dir from P1, and OD-106 copies `cost-history.json` only **at cutover (P5)**. During P1 daily use hylo's cost history therefore starts empty. That gives cold-start `$` colors (yellow at a fixed $25, `$/h` uncolored; SL:610-625, BC-SL-101) where legacy shows percentile colors on the same session. After that the two histories diverge, because each records only the sessions it renders (SL:606). Rate-limit smoothing, sparkline history and `proc_start` also restart, but only transiently | OD-96, OD-101, OD-106; SL:217-262, 601-625 | a one-time manual copy at P1 start (the same documented step as OD-106, done earlier); or `$`/`$/h` color excluded from the daily-use criterion until P5; or something else |
| **T2** | **Known byte differences that are not on the named exclusion list.** OD-105 allows exactly D4-EX-1/2/3, "no blanket exclusions". Other ruled or design-forced differences also change bytes on some inputs: (a) **OD-30**, numeric sid: Go writes one string-form key (BC-SL-079/102), whereas legacy writes duplicate keys and self-counts; (b) **OD-76** ("fix") plus the native probe on **macOS/Linux**: the true start in the repeated DST hour (L3-12), ⌂ shown where legacy fails on localized `ps` output, a comm containing spaces, or no `ps` at all (BC-SL-080). D4-EX-1 is scoped to Windows; (c) Go removes mkstemp temps that legacy leaks (BC-SL-078); (d) **OD-56** total deadline (timing only; no corpus case) | OD-105, OD-30, OD-76 (Class 3 FIX list), OD-56; P3r1 §A7; L3-12 | fold (a)-(c) into the existing D4-EX ids, add named entries, or accept them as uncorpused edges with their own table tests |
| **T3** | **`LOCAL_MODEL_PREFIXES` default.** The status line's legacy default is `""` (SL:444): the pill shows `◨ ?`, the lane is None, and `record_cost` is skipped (SL:604-606). The config map gives the shared key `routing.local_model_prefixes` **one** default, `claude-sonnet` (P5r3 §B.1 ENV-01, K-7; pass-8 AP-5), while D15 requires "defaults equal legacy until cutover". An unset-prefix parity case cannot match by default. The launcher always forces the value (`L:38`), so production never sees the empty case | SL:444, 604-606; P5r3 §B.1; PLAN D15 | the key default stays `claude-sonnet` and harness cases always set the prefixes explicitly (the empty list must stay expressible in config to reach BC-SL-006's `◨ ?`); or a status-line-specific default; or something else |
| **T4** | **Explicit interpreter vs the research CI recipe.** OD-104: "the harness never discovers Python from PATH". Research Q7 sets `HYLO_PARITY_PYTHON=python`, which resolves through PATH | OD-104; research Q7 "Steps" | CI must pass the absolute path that setup-python reports; the research recipe is superseded |
| **T5** | **Pass-8 says `-I`; the later rounds say `-s`.** Pass-8 §8.2 item 4 says "Python 3.11.7 oracle with `-I`". `-I` ignores `PYTHONPATH`, so the `sitecustomize` clock shim (OD-58) would not load. P5r5 §B.4 and RESUME step 3 say `-s`, never `-I`/`-E` | pass-8 §8.2; P5r5 §B.4; RESUME step 3 | documentation consistency; this plan follows P5r5/RESUME |
| **T6** | **P1 dispatch scope.** RESUME step 1 lists `hylo statusline` and `hylo version`. OD-102 adds `hylo config validate` (non-zero on the same errors), and OD-95 adds `hylo config path`; PLAN §6 lists `config` (show/validate) | RESUME step 1; OD-95; OD-102 | a P1 scope addition, not a conflict; confirm it lands in P1 |
| **T7** | **Config file in P1.** D15/PLAN §6 resolve settings as file, then `HYLO_*`, then default. Research Q5 schedules the YAML dependency for P4 ("needed in P4, not P1"), and the P1 runtime-dependency budget is zero besides `x/sys`. OD-96 daily use needs at least the real telemetry URL (the default is the RFC 5737 placeholder, SL:73). The legacy launcher still in use through P4 exports only `DGX_*`/`LOCAL_MODEL_PREFIXES`, which Go must not read (OD-05) | PLAN §6, D15; research Q5; OD-05, OD-96 | YAML (`go.yaml.in/yaml/v4`) lands in P1 and the dependency budget changes; or P1 is env-only (`HYLO_*` set in the status-line command string or the shell); or something else |
| **T8** | **`--subagent` vs never-non-zero.** OD-14 says do not port it, and porting-decision §4.1 allows "recognized-but-unported only if the P1 spec says so". The legacy launcher still wires `subagentStatusLine … --subagent` (`L:177`). Go's stdlib `flag` with `ExitOnError` exits 2 on an unknown flag, which gives a blank line and contradicts the never-blank/exit-0 contract (BC-SL-001; market-intel §6.5) | OD-14; SL:1240; L:177 | ignore the flag and render the main line; print nothing and exit 0; or something else. Never exit non-zero |
| **T9** | **D15 color coverage gap.** D15 names "status line thresholds and colors" as configuration. The 79-row register covers the heat HSV (T-030) and the sparkline RGBs (T-046), and OD-02 covers the glyphs, but **no row** covers the SGR palette (`RESET/DIM/BOLD`, `WHITE..GREY`, `MAGENTA`, `BOLDRED`, SL:127-134), the pill codes (SL:130) or `SEP` (SL:128) | PLAN D15; P4r7 §B.2.1; OD-02 | add `statusline.theme.sgr.*` keys with the legacy defaults, or record them as named constants with a "why not config" reason |
| **T10** | **The D4-EX-3 boundary is unspecified per key.** Legacy assigns defined behavior to values that a typed Go config may reject: `DGX_SL_TTL` = `nan` (fetch every refresh), `inf` (never fetch, `◌ DGX ?` forever), `0`/negative (always fetch), `"4_0"` (= 40), Unicode digits; `DGX_SL_ROWS` = `"2_0"` (= 20, forces row 2); an unknown `DGX_SL_TRACE` (silently `rate`, SL:644, 662); any `DGX_SL_VM_URL` string (bad → no sample) (BC-SL-087; P5r3 §B.1). OD-102 makes "malformed" values config errors, but no document lists each key's valid domain. The BC index also still tags BC-SL-087 as BX, and BC-SL-079/097 as pending OD | OD-102; BC-SL-087; P3r4 §7.3 | the registry spec states the domain and operator per key (CV-19), and the BC register re-tags 087 → D4-EX-3, 079 → OD-30 difference, 097 → OOS |

Also noted (a layout choice, not a settled-decision conflict): porting-decision §4.2 omits `internal/cost`, but PLAN §6 and
OD-36 place the cost history there. This plan follows PLAN §6 (§2.3).

### 7.2 Open risks

| # | Risk | Likelihood / impact | Mitigation in this plan |
|---|---|---|---|
| RK-1 | The Python JSON decoder and number model (WTF-8, big ints, NaN tokens, ordered dicts, depth limit) are larger than they look, and every cache byte depends on them | medium / high | S1 first, CPython tables, fuzz, cache-swap tests (IM-01, IM-03) |
| RK-2 | Hidden exception paths (research P27) that the 43-path catalogue missed | medium initially / medium | Tier C nightly; `recover` backstop; per-site catch lists (IM-15) |
| RK-3 | Windows: cache rename sharing violations under concurrent refreshes; `ntpath` goldens; a Python stdio shim under CI | medium / low-medium | retries + swallow (IM-17); `*.windows.golden`; shim reconfigures stdio |
| RK-4 | OD-104 pins 3.11.**x**, production ran 3.11.7; a patch-level difference in `fromisoformat`/`json` edges would shift goldens | low / medium | record the resolved patch in golden metadata; pin `3.11.7` where setup-python offers it |
| RK-5 | `HYLO_TEST_NOW` honored by the release binary could be misused as a setting | low / low | document it as a test hook; consider a stderr warning when it is set outside the harness (spec decision) |
| RK-6 | `statusline.window_age.ps_timeout_s` (T-026) has no effect once the native probe replaces `ps` | certain / low | re-class T-026 N/A in the registry spec, or keep it documented as inert (owner, with T2) |
| RK-7 | Claude Code stdin churn (market-intel R1) changes output without a code change | high / medium | the newer-optional-field fixtures (§5.2); defensive `Value.Get` everywhere |
| RK-8 | FMA regressions introduced by later refactors | medium / low | arm64 gating leg; `// pyfmt: no-fuse` review convention (IM-10) |

---

## 8. BC mapping: all 103

Columns: **Step** (§4), **Go home**, **IM** (§1), **PR** (pitfalls), **Test** (T table, G golden, F fuzz, M multi-step,
X exclusion test), **Parity** (after the owner rulings), **Conf** (translation confidence and, for MEDIUM, the reason).
Package prefixes: `sl/` = `internal/statusline`, `cost/` = `internal/cost`, `cfg/` = `internal/config`, `plat/` =
`internal/platform`, `py/` = `internal/pyfmt`.

| BC | Contract (short) | Step | Go home | IM | PR | Test | Parity | Conf |
|---|---|---|---|---|---|---|---|---|
| 001 | Guard prints the 29-byte degraded line, exit 0 | S2 | sl/guard.go | 15, 22 | 21, 17 | T, G | BX | H |
| 002 | Non-JSON / non-object stdin → `{}` | S2 | sl/input.go | 01 | 09 | T | BX | H |
| 003 | Rows joined by `\n`; row-2 rule | S2 | sl/statusline.go | 22 | — | T | BX | H |
| 004 | Visible width = code points after SGR strip | S2 | sl/width.go | 11 | 11, 13 | T | BX | H |
| 005 | `COLUMNS` Python int grammar, else 0 | S2 | sl/width.go | 12 | 18, 10 | T | BX | H |
| 006 | Lane pill from prefix `startswith` | S3 | sl/lane.go | 11, 16 | 12, 06 | T | BX | H |
| 007 | Model label display_name/id/`?` | S3 | sl/lane.go | 02, 05 | 06, 16 | T | BX | H |
| 008 | Project label `basename(normpath)` | S3 | sl/lane.go | 11 | 20 | T, G | BX | H |
| 009 | Branch walk (`.git` dir/file, HEAD) | S3 | sl/git.go | 17, 11, 19 | 20, 17 | T | BX | H |
| 010 | Branch segment + git cache (TTL 5 s) | S3 | sl/git.go | 20, 03, 14 | 19 | T | BX | H |
| 011 | Thermometer and denominator | S3 | sl/context.go | 06, 05, 09 | 01, 02, 04, 05 | T | BX | H |
| 012 | Composition % (banker's round) | S3 | sl/context.go | 06, 05 | 01 | T | BX | H |
| 013 | Cache-hit segment | S3 | sl/context.go | 09, 05 | 04, 02 | T | BX | H |
| 014 | Limits hidden on reroute-all prefixes | S3 | sl/limits.go | 11, 16 | 12 | T | BX | H |
| 015 | Expired window (`resets_at <= now`) unreported | S3 | sl/limits.go | 14 | — | T | BX | H |
| 016 | Pace / absolute colour bands | S3 | sl/limits.go | 09, 05 | 04, 02 | T | BX | H |
| 017 | Countdown format and 1.15 gate | S3 | sl/limits.go | 08 | 03 | T | BX | M: float `divmod` near unit boundaries |
| 018 | Rate-limit smoothing (1800 s) | S3 | sl/limits.go | 17, 03, 14 | 19 | T, M | BX | H |
| 019 | Lines segment, `_fmt_lines` | S3 | sl/session.go | 07, 12, 05 | 05, 18, 06 | T | BX | H |
| 020 | Timer segment, `_hm` | S3 | sl/session.go | 08, 07 | 03, 05 | T | BX | H |
| 021 | API-time suffix | S3 | sl/session.go | 08, 07 | 03, 05 | T | BX | H |
| 022 | Window-age suffix (⌂) | S3/S7 | sl/session.go | 10, 08, 14 | 15, 03 | T (arm64) | BX | M: FMA gate + float `//` |
| 023 | Window start (`ps` walk → native probe) | S7 | plat/proc_*.go | 19 | 14, 22 | T, seeded | BX (+D4-EX-1 Windows) | M: no oracle for native values; seeded for parity |
| 024 | Token segment, `_fmt_tok_c` | S3 | sl/tokens.go | 05, 02 | 02, 06 | T | BX | H |
| 025 | `$` colours | S3/S6 | sl/cost.go | 05 | 02, 06 | G | BX | H |
| 026 | `$/h` segment | S6 | sl/cost.go | 05 | 02 | G | BX | H |
| 027 | ⛏ (inside the `$` block, r6 R1-1) | S3 | sl/cost.go | 05 | 02 | T | BX | H |
| 028 | `record_cost` write | S6 | cost/history.go | 06, 03 | 01, 07 | T | BX | H |
| 029 | `cost_thresholds` percentiles | S6 | cost/history.go | 07 | 05, 19 | T, G | BX | H |
| 030 | No transcript → None | S4 | sl/transcript.go | 17 | — | T | BX | H |
| 031 | Mix cache name and reset rules | S4 | sl/mixcache.go | 03 | — | T | BX | H |
| 032 | 512 KB read step, long-line completion | S4 | sl/transcript.go | 17 | — | T | BX | H |
| 033 | `bytes.splitlines` + `json.loads` per line | S4 | sl/transcript.go | 11, 01 | 12, 09 | T, F | BX | M: decoder edge set |
| 034 | Usage dedup per message id (256) | S4 | sl/transcript.go | 03 | 19 | T | BX | H |
| 035 | Usage accumulation | S4 | sl/transcript.go | 02 | 06 | T | BX | M: int/float/big-int `Num` arithmetic and its cache repr |
| 036 | Rebuild rule (20,000 excess) | S4 | sl/transcript.go | 09 | 04 | T | BX | H |
| 037 | `compact_boundary` resets composition and `pp` | S4 | sl/transcript.go | — | — | T | BX | H |
| 038 | Composition per block (`json.dumps` lengths) | S4 | sl/transcript_mix.go | 04, 11 | 08, 11 | T, F | BX | M: `DumpsLen` over decoded values |
| 039 | Last-turn rate machine | S4 | sl/transcript_turn.go | 13 | 14 | T | BX | H |
| 040 | `fetch_sample` (query, 1.5 s, first wins) | S5 | sl/telemetry.go | 18, 01, 12, 15 | 09, 18, 19, 22 | T, F | BX | M: per-site catch list (`TypeError` drops the whole sample) |
| 041 | `get_sample` TTL / KEEP_DEAD state machine | S5 | sl/sample.go | 14, 03 | 19, 07 | T, M | BX | H |
| 042 | History point rules (90 s, 2 s) | S5 | sl/sample.go | 03 | 19 | T | BX | H |
| 043 | Freshness ladder + stale suffix | S5 | sl/row2.go | 05 | 02 | T | BX | H |
| 044 | Health dot | S5 | sl/row2.go | — | — | T | BX | H |
| 045 | Queue segment | S5 | sl/row2.go | 05 | 02 | T | BX | H |
| 046 | KV segment | S5 | sl/row2.go | 07, 09 | 04, 05 | T | BX | H |
| 047 | Throughput segments | S5 | sl/row2.go | 05 | 02 | T | BX | H |
| 048 | Sparkline | S5 | sl/sparkline.go | 06, 09, 07 | 04, 05 | T | BX | H |
| 049 | TTFT segment | S5 | sl/row2.go | 05 | 02 | T | BX | H |
| 050 | Power segment | S5 | sl/row2.go | 05 | 02 | T | BX | H |
| 051 | Idle segment | S5 | sl/row2.go | 08, 14 | 03 | T | BX | H |
| 052 | Cache I/O (load/save, raw sid) | S2 | sl/cache.go | 17, 03, 01 | 07, 09, 19, 20 | T, swap | BX (OD-03) | H |
| 053 | VM fetch whenever ROWS ≥ 2 | S5 | sl/statusline.go | 16, 18 | — | T | BX | H |
| 054 | `trim_to_fit` (double reset; single at ♻) | S2 | sl/width.go | 11 | 11 | T | BX | H |
| 055 | Negative `COLUMNS` disables trim, hides row 2 | S2 | sl/width.go | 12 | 18 | T | BX | H |
| 056 | `heat()` HSV colours | S3 | sl/context.go | 21, 10, 07, 09 | 15, 04, 05 | T (arm64) | BX | H |
| 057 | Thermometer quirks (`/0K`, `/1000K`, NaN crash) | S3 | sl/context.go | 05, 15 | 02, 21 | T | BX | H |
| 058 | Model label `str()` of non-str | S3 | sl/lane.go | 05 | 16, 07, 10 | T | BX | M: Python `repr` of nested containers and big ints |
| 059 | POSIX `normpath` keeps `//` | S3 | sl/lane.go | 11 | 20 | T, G (per OS) | BX | M: per-OS `normpath` ports |
| 060 | Cache-hit NaN/inf rendering | S3 | sl/context.go | 05, 09 | 02, 04 | T | BX | H |
| 061 | Pace band boundary at rem = 0.9 × length | S3 | sl/limits.go | — | — | T | BX | H |
| 062 | `_fmt_tok_c` no unit promotion | S3 | sl/tokens.go | 05, 12 | 02, 18 | T | BX | H |
| 063 | `_fmt_lines` OverflowError on inf (CP-S11) | S3 | sl/session.go | 07, 15 | 05, 21 | T | BX | H |
| 064 | `_hm` ValueError on inf (CP-S12/S13) | S3 | sl/session.go | 08, 15 | 03, 21 | T | BX | H |
| 065 | First line of a message supplies its usage | S4 | sl/transcript.go | — | — | T | BX | H |
| 066 | Short + long line takes two refreshes | S4 | sl/transcript.go | 17 | — | T, M | BX | H |
| 067 | `splitlines`/`json.loads(bytes)` acceptance set | S1/S4 | py/json.go, sl/transcript.go | 01, 11 | 09, 12 | T, F | BX | M: BOM / UTF-16 / depth / NaN breadth |
| 068 | Sticky transcript crash (legacy) | S4 | replaced by sl/transcript_wshape.go | 15 | 21 | X | D4-EX-2 | H (not ported; inverse tested) |
| 069 | `_iso_ts` grammar (3.11, naive = local) | S1 | py/time.go | 13 | 14 | T, F | BX | M: breadth of the 3.11 `fromisoformat` grammar |
| 070 | Mix cache sanitizing per code point | S4 | sl/mixcache.go | 11 | 11, 13 | T | BX (OD-03) | H |
| 071 | `json.dumps` length rules | S1 | py/json.go | 04 | 08, 07 | T, F | BX | H |
| 072 | `text`/`thinking` value types | S4 | sl/transcript_mix.go | 02, 15 | 06, 21 | T | BX (crash form → D4-EX-2) | H |
| 073 | Sparkline NaN/+Inf crash (CP-N02) | S5 | sl/sparkline.go | 15, 07 | 04, 05, 21 | T | BX | H |
| 074 | KV NaN crash (CP-N01), cell math | S5 | sl/row2.go | 15, 07 | 04, 05, 21 | T | BX | H |
| 075 | Row-2 NaN/inf rendering; wall-colour mismatch | S5 | sl/row2.go | 05 | 02 | T | BX | H |
| 076 | Strict stdio; invalid UTF-8 → `{}` | S2 | sl/input.go, guard.go | 01, 22 | 17, 09 | T | BX | H |
| 077 | `main()` side-effect order | S2/S8 | sl/statusline.go | 15, 17 | 21 | M | BX | M: exact interleaving of writes and degrade points |
| 078 | Sid with `/` leaks a temp; nothing persists | S2 | sl/cache.go | 17 | 20 | T | BX (OD-03) | M: Go temp cleanup differs (T2c) |
| 079 | Numeric sid: throttle and self-exclusion fail | S6 | cost/history.go | 01 | — | T (string-form key) | OD-30 known difference | H (deliberate) |
| 080 | `ps` output parsing (→ native probe) | S7 | plat/proc_*.go | 19, 13 | 14, 12 | T per OS | BX (D4-EX-1) | M: native probe replaces the parse; edge differences (T2b) |
| 081 | Window-age format | S3 | sl/session.go | 08 | 03 | T | BX | H |
| 082 | `$` and `$/h` number formatting | S3 | sl/cost.go | 05 | 02 | T | BX | H |
| 083 | Pick `eq` threshold 0.005 | S3 | sl/cost.go | 05 | 02 | T | BX | H |
| 084 | Idle strict > 300 and age format | S5 | sl/row2.go | 08 | 03 | T | BX | H |
| 085 | Mine (last-turn) segment | S5 | sl/row2.go | 05, 02 | 02, 06 | T | BX | H |
| 086 | TTFT format boundaries | S5 | sl/row2.go | 05 | 02 | T | BX | H |
| 087 | Import-time env grammar (CP-X01/X02) | S2 | cfg/load.go, errors.go | 16 | 18, 22 | T per key class, X | **D4-EX-3** (was BX) | H (spec'd deviation) |
| 088 | `transcript_path` type semantics (int = fd) | S4 | sl/transcript.go, plat/fd_*.go | 23 | 21 | T | BX | M: fd semantics, pipe capture assumed |
| 089 | Row goldens A/B/C | S8 | sl/testdata/goldens | all | — | G | BX | H |
| 090 | Trim breakpoints | S2/S8 | sl/width.go | 11 | 11 | T | BX | H |
| 091 | `get_sample` pinned sequence, cache key order | S5 | sl/sample.go | 03 | 19 | T, M | BX | M: inherited key order needs the ordered `Value` |
| 092 | `HIST_MIN_GAP` reachability | S5 | sl/sample.go | — | — | T (seeded) | BX | H |
| 093 | `effective_rl` sequence, sticky CP-S09 | S3 | sl/limits.go | 15, 03 | 21 | T, M | BX | H |
| 094 | Turn-machine exhaustive table | S4 | sl/transcript_turn.go | — | — | T (20 rows) | BX | H |
| 095 | Turn identity ignores `seen_ids` | S4 | sl/transcript_turn.go | — | — | T | BX | H |
| 096 | `json.dumps` length oracle (63 cases) | S1 | py/json.go | 04 | 07, 08, 10 | T (63), F | BX | H |
| 097 | `--subagent` entry point | — | not ported | — | 15 (OOS) | dispatch test only (T8) | OOS (OD-14) | n/a |
| 098 | D4-EX-2 Go contract: W-predicates | S4 | sl/transcript_wshape.go | 15 | 21 | T, X | D4-EX-2 | M: predicates must leave no partial mutation |
| 099 | D4-EX-2 table tests (21 rows) | S4 | sl/transcript_wshape_test.go | — | — | T (21), X | D4-EX-2 | H |
| 100 | Legacy persists a poisoned `cur.out` (reader rule) | S4 | sl/mixcache.go | 01 | — | T, X | D4-EX-2 (OD-32) | M: reader rule applies only when `t0` is numeric |
| 101 | Cost colouring goldens (20 sessions) | S6 | cost/history.go + sl/cost.go | — | — | G | BX | H |
| 102 | `record_cost` write contract | S6 | cost/history.go | 03, 06 | 01, 07 | T | BX (OD-30 sub-case) | H |
| 103 | `cur` with `t0` null and non-numeric `out` | S4 | sl/mixcache.go | 01 | — | T | BX (OD-32) | H |

**Tallies.**

- **Rows:** 103 (BC-SL-001..103, none skipped).
- **Confidence:** H 84 · M 18 (017, 022, 023, 033, 035, 038, 040, 058, 059, 067, 069, 077, 078, 080, 088, 091, 098, 100)
  · L 0 · n/a 1 (097).
- **BCs per step:** S1 4 (067, 069, 071, 096); S2 13; S3 33; S4 22 (067's second home; 068 listed, replaced by 098); S5 21; S6 6 (025 shared with S3); S7 2
  (023, 080; 022 shared with S3); S8 1 (089; 077 and 090 shared with S2). Each BC is counted once at its primary step,
  except the shared rows noted here. Sum: 102 primary + 097 (no step, not ported) = 103.

---

## Validation log

Extraction validation (semport Phase 2 review, 2026-11-15). Method: ~80 `SL:nn` line citations sampled across all
sections (plus every MEDIUM-confidence BC row), all 103 BC mappings and parity classes recounted, idiom-map semantics
re-verified against a CPython 3.11.7 oracle and Go 1.26.5 measurements. Convergence after iteration 1 (iterations 2-3
confirmed the corrections and internal consistency; no further changes). Fixed:

1. (Iter 1, IM-02) Citation `SL:1105-1112` for the `isinstance` block began one line late; the guarding
   `isinstance(u, dict)` sits at SL:1104. Changed to `1104-1112`.
2. (Iter 1, IM-11) Citation `SL:390` pointed at `os.path.dirname(d)`; the named `abspath`/`join`/`normpath` uses sit
   at SL:373/375/383. Changed `390` → `375`.
3. (Iter 1, §4 S5) The fetch-edge table claimed `"a5"` parses as 5.0. `float("a5")` raises `ValueError` (oracle
   verified), so the series is skipped via `continue` (SL:179). Wording corrected and the SL citation added.
4. (Iter 1, §8 Tallies) Per-step BC tally recounted from the §8 table under the stated primary-step rule:
   S2 14 → 13, S3 39 → 33, S4 26 → 22 (sum 102 primary + 097 unstepped = 103). No BC row changed. The mirrored
   effort-basis cells in the companion assessment §4 (S3 "39 BCs", S4 "26 BCs") were updated to match.

Verified without change (samples): the 29-byte degraded line (arithmetic re-checked); the nine `time.time()` read
sites; the narrow catch lists (SL:179, 854-855, 1062); the CP-S15 site at `s.get(sid)` (SL:230); T3 (`SL:444` empty
default; launcher `L:38` forces the value); T8 (Go `flag` with `ExitOnError` measured exiting 2 on an unknown flag);
T10 env grammar (`nan`/`inf`/`0`/`"4_0"`/underscore/Unicode digits — oracle verified); `bytes.splitlines` splitting
only on `\n`, `\r\n`, `\r` (not U+2028) while `str.splitlines` splits wider; `fromisoformat` truncation of fractional
seconds beyond microseconds; the 4,300-digit integer limit (4,301-digit negative `COLUMNS` → `ValueError` → 0 → row 2
shown); Go's `encoding/json` nesting limit (measured: 10,000 accepted, 10,001 rejected), invalid-UTF-8 → U+FFFD, BOM
rejection; `filepath.Clean("//")` = `/` vs `posixpath.normpath("//")` = `//`; round/half-even boundaries (999.5 →
1000, 2.675 → 2.67, 0.125 → 0.12); `json.dumps` lengths (`{}` 2, `0` 1, `false` 5, `null` 4; `inner is None` → 0);
MKSTEMP mode 0600 and the leaking-temp path for a sid containing `/`; register-derived table sizes (BC-SL-096 = 63
cases, BC-SL-099 = 21 rows, BC-SL-094 = 20 rows, BC-SL-101 = 20 sessions) and the BC-SL-068 → BC-SL-098 replacement;
"0 tests in legacy"; `tools/backfill_cost_history.py` exists. One register-cited figure (BC-SL-067 depth 995 accepted)
measured 994 in a fresh interpreter — the boundary is calling-context dependent, which is why the design already pins
it with a CPython-generated table; no change.

---

## State Checkpoint

```yaml
semport_phase: 2
module: statusline
status: complete
bcs_mapped: 103
bcs_translated: 101   # 068 replaced by 098 (D4-EX-2); 097 not ported (OD-14)
confidence: {high: 84, medium: 18, low: 0, n_a: 1}
tensions: 10
open_risks: 8
timestamp: 2026-11-15
next: owner review of tensions T1-T10 -> status line spec package (PRD section, BC files with legacy_id, config registry spec, parity-harness spec, internal/pyfmt spec)
```

---

## Owner resolutions (2026-11-15)

Ruled by the owner 2026-11-15; rows in `specs/owner-decisions-log-2026-11-14.md` (OD-107..OD-114). Every tension is closed;
no section above is amended retroactively — the rulings below govern how each tension is resolved going forward.

| # | Resolution |
|---|---|
| T1 | **OD-107** — moot: no live use of `hylo statusline` in real sessions before the instant P5 cutover; the P1 success criterion is byte parity on the owner's real recorded inputs (git-ignored captures/) plus the synthetic CI corpus; the harness replays sequences of stdin snapshots from a captured session |
| T2 | **OD-110** — named exclusion-list entries for every owner-ruled difference (OD-30 single string key; OD-76 + native probe on macOS/Linux; Go temp-file cleanup, cache-file comparison only), each with its own table tests; still no blanket exclusions |
| T3 | **OD-111** — `routing.local_model_prefixes` default stays `claude-sonnet` (one key, one default); parity cases for an unset prefix set an explicit empty value |
| T4 | **OD-108** — CI passes the absolute interpreter path reported by setup-python; the research Q7 recipe (`HYLO_PARITY_PYTHON=python`) is superseded |
| T5 | **OD-109** — the oracle runs with `-s` (never `-I`); the harness constructs the child environment from scratch; a canary test fails the harness if the shim did not load |
| T6 | **OD-107** — confirmed: `hylo config validate` and `hylo config path` ship in P1 (OD-102, OD-95) |
| T7 | **OD-107** — moot: P1 config = HYLO_* env + built-in defaults; the config-file layer and its YAML dependency arrive in P4 (research Q5) |
| T8 | **OD-112** — any unknown flag (incl. a leftover `--subagent`) renders `hylo: unknown flag ...`, exit 0; never blank, never non-zero (same rule as D4-EX-3) |
| T9 | **OD-113** — `statusline.theme.*` config keys for the SGR palette, pill codes and separator (SL:127-134), legacy values as defaults; D15 names colors explicitly |
| T10 | **OD-114** — every config key states its type and range with rationale in the schema (D15); D4-EX-3 error classes enumerated (TTL `nan`/`inf`/negative, `4_0`-style underscores, Unicode digits, unknown TRACE values, non-http(s) metrics URL); TTL `0` stays valid |
