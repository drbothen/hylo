---
document_type: architecture-section
level: L3
section: "pyfmt"
version: "1.12"
status: draft
producer: architect
timestamp: 2026-11-19T07:00:00Z
phase: 1b
inputs: [prd.md, semport/hylo-legacy/statusline-target-design.md, behavioral-contracts/BC-INDEX.md]
traces_to: ARCH-INDEX.md
input-hash: "2665978"

---

# ARCH-06 — Python-compatible formatting (`internal/pyfmt`)

> The parity foundation under every widget (OD-103: ONE package, four files).
> Classification: **pure core** — the only package with no effect edge at all; stdlib
> imports only; `math/big` for beyond-int64 durations (OD-137). CRITICAL tier
> (line coverage >= 95% P1; mutation kill rate >= 95% is the Phase 6 target, OD-135/OD-158).
> encoding/json and strconv are banned on protocol inputs; inside `F`/`Repr`, strconv is
> trusted only for finite values (BC-5.01.002 invariant 1, NFR-003).

## Four files (OD-103) and what each reproduces

| File | Reproduces (BCs) |
|---|---|
| `num.go` | CPython 3.11 arithmetic on `Num` (int64 / *big.Int / float64 / bool-as-int); `Round` (ties-to-even + decimal re-round, big-int result beyond int64), `RoundN`, `F` ('f' format incl. -0, nan/inf spellings), `D`, `Int`/`Ceil` (exact `Num` results beyond int64, typed NaN/Overflow errors), `FloorDiv`/`Mod` (CPython `float_divmod` port — NOT `math.Floor(a/b)`; `ErrZeroDivision` on zero divisor), `FloorDivInt/ModInt` (integer `//`/`%`, exact for big ints), `Max`/`Min` (first-maximal-wins NaN argument order), `MaxSeq` (typed `ErrValue` on empty), `Repr` (Python repr recipe — see below), `ParseInt`/`ParseFloat` (Python grammar: underscores, Unicode digits, 4,300-digit limit, `1e400`, nan/inf), `NumToF`/`TrueDiv`/`NumCmp` (CPython mixed int/float semantics: `NumToF` float(int) conversion with typed `ErrOverflow` at `\|n\| >= 2**1024 - 2**970`, `TrueDiv` int/int exact rational quotient rounded once to float64 (operands not pre-truncated) with `ErrZeroDivision`, `NumCmp` exact cross-kind comparison — which also pins Max/Min exact tie-breaks) — BC-5.01.001..007, BC-5.01.003 |
| `Repr` recipe (ADV-P2-D01, normative) | Python `repr(float)` = the shortest round-trip digit string, rendered **fixed** when the decimal exponent satisfies `-4 <= exp < 16`, else in exponent form; Go's shortest `'g'` instead switches to exponent form at `exp >= 6`, so `'g`'s notation decision is never reused — draw the shortest digits from `strconv`/`AppendFloat('g', -1, 64)` (the same shortest digit string the BC-5.01.005 recipe draws from the `'e'` form; `'g'` is a DIGIT SOURCE here, not a notation authority — the notation decision is always re-applied from Python's rule, which is how the two wordings reconcile), derive `exp = dp - 1` from the digit string, then apply **Python's** fixed/exponent rule; finish with the signed two-digit exponent (`e+09`), the `.0` suffix for integral values, and the `inf`/`nan` spellings. Following `'g'`'s own switching rule yields `1.794615009e+09` where the BC's canonical vector requires `1794615009.0`. — BC-5.01.005 |
| `json.go` | Hand-written decoder/encoder over ordered `Value`/`Member`/`Kind`: `Decode(b, mode, depthBudget)` — the recursion budget is a **per-call-site parameter**, never a mode property and never a package global (BC-5.02.003 invariant 3): named constants pinned by the orchestrator end-to-end measurement of the real legacy program (isolated HOME, 2026-11-17; ADV-P2-A07 CLOSED): `depthStdinLoad = 993` (main → json.load, 6 frames; 993 accepted / 994 rejected, BC-1.01.002), `depthTranscriptLine = 993` (main → _mix_counts → json.loads, 6 frames; also 993/994 — supersedes the earlier frame-local 989/990 probe, which does not transfer across invocation depths), `depthSessionCache = 991` (main → effective_rl → load_cache, 8 frames; 991 accepted / 992 rejected, measured; the get_sample, claude_window_start and mix-cache loaders at the same 8-frame chain depth: 991/992, derived), `depthGitCache = 990` (main → render_lane → git_segment → load_cache, 9 frames; 990 accepted / 991 rejected, measured; the cost-history loaders record_cost and cost_thresholds, called from render_lane, at the same 9-frame depth: 990/991, derived), `depthMetricsReply = 992` (main → get_sample → fetch_sample → json.loads(resp.read()), 7 frames; 992 accepted / 993 rejected, MEASURED end to end against a localhost HTTP reply, pass-5 ADV-P5-A2-05; BC-5.02.004 names metrics replies pyfmt.Value decodes). Governing formula: **limit = 999 − (Python frames from `<module>` down to json's raw_decode)**; full per-site table, measurement recipes and the limit/limit+1 test rule in VP-006. Mode-site pairing (three sites, not two): **ModeText serves the stdin and cache loads; ModeBytes serves the transcript line loads AND the metrics reply** (BC-1.03.004, BC-5.02.003, BC-5.02.004; ADV-P2-A06; metrics reply added pass-6 A07, call 5 — legacy decodes the fetch with `json.loads(resp.read())` on bytes, SL:171, so BOM/UTF-16/32 detection applies; 992 accepted / 993 rejected, `depthMetricsReply` above, VP-006; the owning BC-5.02.003 one-line precondition gains the multi-line-body case, pass-6 C2-06) — the transcript site's 993 boundary belongs to the ModeBytes site. The pyfmt gen scripts pin the boundaries by re-running the recorded measurement recipes under the pinned oracle — a moved boundary fails regeneration, and the committed tables then pin Go's constants. ModeText = `json.load` text semantics (BOM invalid, invalid-UTF-8 error, **NaN/Infinity tokens** — Python's json module accepts the spellings in BOTH modes; pass-5 A23 — the cache writer emits NaN tokens that are read back via ModeText, [AD-08 cache-writer decision](ARCH-04-data-files.md#decision-go-is-byte-exact-cache-writer-and-reader-across-pythongo-swaps-ad-08)); ModeBytes = `json.loads(bytes)` (BOM/UTF-16/32 detection, NaN/Infinity tokens, duplicates last-wins keeping position, WTF-8 strings surviving lone surrogates); `Dumps`/`DumpsLen` (json.dump byte defaults, shared escape/float-repr code with DumpsLen so lengths and bytes cannot drift); `Str` (Python str()/repr of values) — BC-5.02.001..006 |
| `str.go` | WTF-8-aware `Len` (surrogate = 1 code point), `Truncate`, `HasSurrogate`, `EncodeUTF8Replace` (lone surrogate -> `?`), `Strip`/`RStrip` (Python whitespace incl. NBSP), `RSplit1`, `SplitLinesBytes` (\n \r\n \r only), `SubNonWord` (per code point before truncation), `PosixNormpath`/`NtNormpath`/`Basename` (per-OS selection, ntpath on Windows). Scope note (pass-3 D14, sharpened pass-4 D18): pyfmt contracts ONLY normpath (both flavors) and basename — `abspath`/`join`/`dirname` are NOT pyfmt functions, because Windows `abspath` needs cwd via GetFullPathNameW (an effect); any caller needing abs-path resolution performs it in `internal/statusline` against the dedicated `Env.Abs` seam (ARCH-03; pass-6 A18 — the bare `Cwd func() string` cannot express drive-relative `C:rel` resolution, which BC-1.02.004 EC-012 needs), never inside pure pyfmt. BC-5.03.004 Inv 3's citation of `abspath`/`join`/`dirname` (SL:373-390) as "served by pyfmt" is SUPERSEDED by this scope rule (the underlying SL:373-390 behavior is served by `internal/statusline`); the flavor rule is uniform: `Basename` — and every per-OS flavor selection pyfmt makes — is a pure function of the build target (`runtime.GOOS`, compile-time constant per build; both flavors always compiled and table-pinned on every OS), never a caller choice. The posix/nt `join`/`dirname`/`abspath` flavor pinning is OWNED HERE (architect — resolving the pass-4 D18 / BC-5.03.004 obligation ping-pong, pass-6 A18): per-flavor rules are owned by BC-5.03.004 with `abspath` per-flavor behavior pinned by BC-1.02.004 PC-1/EC-012 — BC-5.03.001..004 |
| `time.go` | `TimeFloat` (time.Time -> s float, once per render, BC-5.04.003); `FromISOFormat` (3.11 grammar, naive = local, fraction truncation beyond µs; ERROR RESULT distinguishing None (`ErrValue`) from the Windows degrade (`ErrLocaltimeDomain`), pass-6 A05, call 2, BC-5.04.001); `LocalToUnix` (CPython `_mktime` port: gap/overlap semantics; 0 mismatches over 10,893 CPython goldens across four zone grids; Go `time.Date` differs; typed `ErrLocaltimeDomain` when `msvcDomain` and the instant is outside MSVC's `localtime_s` domain — on or before 1970-01-01 or from year ≥ 3001 (corrected pass-7 D06, owner call 8: the domain check covers EVERY MSVC `localtime_s` call in CPython's conversion, the probes `t`, `u1`, `u1 − 86400` and `u2`, so every wall time on 1970-01-01 degrades, not only instants before midnight) — pass-6 A05, call 2) with embedded `time/tzdata` — BC-5.04.001..002 |

### Encoder depth law — one law, both directions (pass-5 D08/D17, call 10; measured sweep C)

One convention throughout: **total JSON nesting depth** of the encoded or decoded
document/value (containers counted from the root — the decode convention). Measured
this burst with `python3 -I` (CPython 3.11.7, recursion limit 1000, isolated temp
HOME and cwd; slope and absolutes verified three ways), every JSON recursion
boundary obeys

> **acceptance = K_entry − s**, where **s = the number of Python frames on the stack
> when json is invoked (invoking frame inclusive, `<module>` = 1)** and the slope is
> exactly **1 slot per Python frame**;

- **Decode** (`json.load`/`json.loads`): the pinned decoder law stands unchanged —
  **999 − F** with F counted from `<module>` through `raw_decode`'s chain including
  json's internal decode frames: stdin/subagent 993 @6, transcript 993 @6, metrics
  reply 992 @7 (measured, ADV-P5-A2-05), session/mix/window-start/get_sample loaders
  991 @8, git/cost-history 990 @9 (VP-006).
- **Encode via `json.dump`**: **K = 995** — boundary = **995 − s**.
- **Encode via `json.dumps`**: **K = 994** — boundary = **994 − s**; at equal stack
  `json.dump` accepts exactly ONE level more than `json.dumps` (generator-chain vs
  C-encoder internals; verified 993 vs 992 on the same replica chain).

Measurement grounding (method and method-cross-checks, 2026-11-18): (a) end to end on
the real `legacy/dgx_statusline.py` with isolated temp HOME+cwd — the session-cache
save via `effective_rl` (SL:308) flips between stdin `rate_limits` value depth 990
(saves: encoded document nests 991) and 991 (skips: document 992); (b) faithful
frame-chain replicas (`<module>→main→effective_rl→save_cache→json.dump` and
`<module>→main→_mix_counts→json.dumps` with and without the genexp frame) give 991 /
991 / 990 — matching (a) exactly; (c) a slope probe over five stacked frames
confirming the 1-slot-per-frame slope for `json.dump`, `json.dumps` and `json.loads`
alike. Per-site encoder constants:

| Encode site | Legacy chain | s | Entry | Budget (total nesting) |
|---|---|---|---|---|
| `save_cache` session — `effective_rl` SL:308; `get_sample` SL:351/355; `claude_window_start` SL:288 | `<module>→main→caller→save_cache` | 4 | `json.dump` | **991** — measured end to end (flip at stdin value 990/991) |
| `save_cache` mix — `_mix_counts` SL:1150 | `<module>→main→_mix_counts→save_cache` | 4 | `json.dump` | **991** — payload flat; unreachable from input |
| `save_cache` git — `git_segment` SL:411 (via `render_lane`) | `<module>→main→render_lane→git_segment→save_cache` | 5 | `json.dump` | **990** — payload flat; unreachable from input |
| `save_cache` cost-history — `record_cost` SL:237 (via `render_lane`) | same 5-frame depth | 5 | `json.dump` | **990** — payload flat; unreachable from input |
| `_mix_counts` serializers, inner-value and tool_use input (SL:1140/1147) | `<module>→main→_mix_counts` | 3 | `json.dumps` | **991** — value nesting; input capped at 989 by the line decode → unreachable |
| `_mix_counts` serializer, tool_result list genexp (SL:1138) | `<module>→main→_mix_counts→genexp` | 4 | `json.dumps` | **990** — item capped at 988 → unreachable |

Superseded by this table: the pass-5 D08-era budgets (session/mix 989, record_cost/git
988, composition 990/989 — the `993 − W` convention under-modeled the invoke-frame
slot) and the derived mix figure 993 with its "one frame shallower" rationale
(superseded). Reconciliation (D17 as measured): a DEEPER stack never has the larger
budget and a SHALLOWER stack never has the smaller one (budget strictly decreasing in
s within every entry, both entries), and every cache's **Save budget EQUALS its Load
budget** (session/mix 991/991, git/cost 990/990) — `Decode(Save(x))` never rejects
what `Save` produced. The real exposure is the stdin side: a `rate_limits` value
nested 991..992 decodes at the stdin site (bound 993) yet breaches the session Save
budget 991 — legacy skips the session-cache write there (SL:307-308), which is ruled
in-band behavior (BC-5.02.006), not an exclusion.

### Decision: hand-written Python-semantics layer, CPython-generated tables (AD-04)

- **Context:** Go stdlib differs from CPython on JSON leniency (NaN tokens, big ints,
  ordered dicts, WTF-8), float formatting spellings, code-point string ops, and mktime
  gap/overlap — every cache byte and widget byte depends on these.
- **Table-driven expectations:** every file carries a committed CPython-generated
  expectation table; generators live in `internal/pyfmt/testdata/gen/*.py` and run under
  the pinned 3.11 oracle (OD-104). The BC-5.02.002 table (63 cases) is regenerated by
  script, no hand-recorded literals (OD-142). Beyond-int64 exactness via `math/big`
  (OD-137, extended by OD-156 — pass-3 A15): the duration-format sites — the window-age
  duration path (BC-1.02.028) and the `_fmt_lines` lines/thresholds path (BC-1.02.014,
  added by OD-156; the int64 sketch is superseded) — and the exact `Int`/`Ceil`/`Round`
  results beyond int64 (BC-5.01.003/.001, typed NaN/Overflow errors).
- **Options considered:** (1) adapt Go stdlib at each call site — semantics scatter;
  (2) vendored third-party parity lib — dependency budget plus unverifiable provenance;
  (3) one hand-written package with oracle tables and fuzz targets.
- **Option 3.**
- **Rationale:** closed, single-home semantics; every helper has one oracle-pinned table
  and, where breadth demands it, a fuzz target: `Decode`, `DumpsLen`, `FromISOFormat`,
  `ParseFloat` (design doc §2.6).
- **Consequences:** `strconv.FormatFloat` inside `F`/`Repr` is trusted only for finite
  values; tests run the FMA-sensitive sites on arm64 (IM-10/PR-15) with a
  `// pyfmt: no-fuse` convention at each site.
- **Verification feasibility: the strongest provable-grade surface in the repo** — closed
  functions over values; oracle tables + `go test -fuzz` targets + property generators
  (`github.com/flyingmutant/rapid`, test-only; `testing/quick` suffices for trivial
  chains) asserting metamorphic oracles plus spot-pins against the committed CPython
  tables (ARCH-00, ADV-P1-A07); mutation kill rate >= 95% is the Phase 6 target
  (OD-158) — pyfmt is simply reported first as the densest pure surface, not a P1
  gate (tool: gremlins, named in ARCH-00; ADR line AD-14 in ARCH-INDEX; pass-3 A25).
- **Per-OS behavior (P18, ADV-P1-D21, explicitly justified):** the only GOOS-dependent
  logic in `pyfmt` is `Basename` choosing ntpath on Windows. The Windows `localtime`
  failure domain rides a caller-injected `msvcDomain bool` parameter (`LocalToUnix`,
  above) — statusline passes `platform.IsWindows()` — so pyfmt still imports no
  platform package and compiles portable logic only (pass-6 A05, call 2). It is deliberately NOT
  routed through `internal/platform`: `pyfmt` is the repo's lowest sink and importing
  infrastructure from it would invert AD-02's dependency direction. The selection is a
  pure function of the build target; both flavors are always compiled and always
  table-pinned on every OS, so no build tag or platform call is needed. Flavor files
  carry no GOOS-recognized filename suffix for the same reason (call 11 naming rule,
  pass-7 A10 — ARCH-05).

## Interfaces (signatures per design doc §2.6)

```go
package pyfmt

type Num struct{ /* int64 | *big.Int | float64 | bool */ }

func Round(x float64) (Num, error)      // BC-5.01.001: ties-to-even; ErrValue / ErrOverflow; result is a Num int (int64 or exact big int)
func RoundN(x float64, n int) float64
func F(x float64, prec int) string
func D(n int64, width int, zeroPad bool) string
func Int(x float64) (Num, error)        // BC-5.01.003 EC-006: exact beyond int64 (Int(1e300)); ErrValue / ErrOverflow
func Ceil(x float64) (Num, error)       // exact beyond int64; ErrValue / ErrOverflow
func FloorDiv(a, b float64) (float64, error) // CPython float_divmod port; ErrZeroDivision when b == 0
func Mod(a, b float64) (float64, error)      // float_divmod remainder;       ErrZeroDivision when b == 0
func FloorDivInt(a, b Num) (Num, error) // integer //: quotient toward −∞, exact for big ints; ErrZeroDivision on zero divisor
func ModInt(a, b Num) (Num, error)      // integer %: remainder takes the divisor's sign; ErrZeroDivision on zero divisor
func Max(a, b Num) Num                  // first-maximal-wins NaN argument order
func Min(a, b Num) Num
func MaxSeq(xs []Num) (Num, error)      // BC-5.01.006 PC-1: typed ErrValue on empty input
func NumToF(x Num) (float64, error)     // BC-5.01.007: float(int); ErrOverflow at |n| >= 2**1024 − 2**970 (unordered operands never compare — see NumCmp)
func TrueDiv(a, b Num) (float64, error) // BC-5.01.007: true division; exact int/int quotient rounded once; ErrZeroDivision
func NumCmp(a, b Num) (int, error)      // BC-5.01.007: exact cross-kind comparison (never rounds the int to float64); defined only for ORDERED operands — cross-kind comparison sites use the NaN-aware relational helpers NumLT/NumLE/NumGT/NumGE/NumEQ (Python semantics: any NaN operand → false, except !=) (pass-5 D09, call 11)
func NumLT(a, b Num) bool // BC-5.01.007 PC-3b (pass-7 D22): NaN-aware relationals; any NaN operand → false
func NumLE(a, b Num) bool // ≤ likewise: any NaN operand → false
func NumGT(a, b Num) bool // > likewise: any NaN operand → false
func NumGE(a, b Num) bool // ≥ likewise: any NaN operand → false
func NumEQ(a, b Num) bool // ==: any NaN operand → false (Python ==)
func NumNE(a, b Num) bool // !=: any NaN operand → true (Python !=)
func Repr(x float64) string // Python repr: shortest round-trip digits; fixed notation iff -4 <= exp < 16, else exponent (ADV-P2-D01 — never 'g''s exp>=6 rule); ".0" integral suffix; inf/nan spellings (BC-5.01.005)
func ParseInt(s string) (Num, error)
func ParseFloat(s string) (float64, error)

type Value struct{ /* Kind + ordered members / WTF-8 string / Num / bool */ }
type DecodeMode uint8
const (ModeText DecodeMode = iota; ModeBytes)

// depthBudget is per CALL SITE, not per mode. Named constants from the orchestrator
// end-to-end measurement (isolated HOME, 2026-11-17; ADV-P2-A07 closed): stdin 993
// (6 frames), transcript line 993 (6 frames), session cache 991 (8 frames), git cache
// 990 (9 frames) — limit = 999 − Python frames from <module> down to json.raw_decode;
// derived peer loaders share the chain depth (full table: VP-006). Boundaries are
// pinned via the recorded measurement recipes (gen scripts) — do not invent a value.
func Decode(b []byte, mode DecodeMode, depthBudget int) (Value, error)
// ErrDepth: typed encoder depth breach (pass-5 D08/D17, call 10) — Dumps/DumpsLen
// return it when nesting exceeds the site's budget; Decode rejects at budget+1.
var ErrDepth = errors.New("pyfmt: JSON nesting exceeds the call-site depth budget")
func Dumps(v Value, depthBudget int) ([]byte, error) // (ADV-P4-D07; budget added pass-5 D08/call 10) encoder failures are typed: the 4,300-digit int-to-string limit -> ErrValue (BC-5.02.006 PC-5; pass-6 D25); a depth breach -> ErrDepth (pass-5 D08)
func DumpsLen(v Value, depthBudget int) (int, error) // shared escape/float-repr code with Dumps so lengths and bytes cannot drift (BC-5.02.001); same depthBudget and typed dispositions as Dumps (pass-5 D08/call 10; pass-6 D25)
func Str(v Value) string

func Len(s string) int
func Truncate(s string, n int) string
func HasSurrogate(s string) bool
func EncodeUTF8Replace(s string) string
func Strip(s string) string
func RStrip(s, chars string) string
func RSplit1(s, sep string) []string // Python rsplit(sep, 1): 1- or 2-element list [head, tail] / [s] (BC-5.03.002)
func SplitLinesBytes(b []byte) [][]byte
func SubNonWord(s, repl string) string
func ValidationWidth(s string) int // VALIDATION width, config grammar only — never the render path (BC-2.01.004 PC-9; pass-7 D22): sum over the value's code points of the OD-170 EA-width function on hylo's Unicode 14.0.0 tables — Wide/Fullwidth 2, Mn/Me/Cf 0, else 1, Ambiguous 1; control bytes are range violations, not widths (see "Two width functions" above)
func PosixNormpath(p string) string
func NtNormpath(p string) string
func Basename(p string) string        // runtime.GOOS selects ntpath on Windows; both flavors always compiled and table-pinned (see P18 note)

func TimeFloat(t time.Time) float64
func FromISOFormat(s string, loc *time.Location, msvcDomain bool) (float64, error) // BC-5.04.001; ErrValue = unparsable (legacy None); ErrLocaltimeDomain = Windows MSVC domain failure (degrade) — msvcDomain threads through to LocalToUnix (pass-6 A05, call 2; arity synced to BC-5.04.001 by sync-check adv-p6 SC-22)
func LocalToUnix(fields Naive, loc *time.Location, msvcDomain bool) (int64, error) // BC-5.04.002: Unix seconds from parsed naive fields; ErrValue (value error); DISTINCT ErrLocaltimeDomain when msvcDomain and any MSVC localtime_s probe in the conversion (t, u1, u1 − 86400, u2 — pass-7 D06, owner call 8) falls outside the domain (on or before 1970-01-01, or from year ≥ 3001) — the caller (statusline) passes msvcDomain = platform.IsWindows(); pure pyfmt imports no platform package (pass-6 A05, call 2)
```

### Unicode tables (OD-170, pass-4)

hylo carries its own Unicode 14.0 tables for every character class pyfmt consults
(decimal digit Nd for `ParseInt`/`ParseFloat`, printable and whitespace for
`Strip`/`RStrip`, the word-character class for `SubNonWord`, **the East-Asian-Width
class for the config-validation width** — Wide/Fullwidth = 2, Mn/Me/Cf = 0, else 1,
Ambiguous = 1, per BC-2.01.004 PC-9 — and any other class a gen
script exercises), generated from CPython 3.11.7 `unicodedata` by a committed generator
script run under `go generate`; pyfmt never consults Go's `unicode` package for these
classes (Go's bundled tables are newer and diverge on post-14.0 assignments — e.g. Kawi
digits U+11F50-59). A version constant (`14.0.0`) and a test pin the tables to the
oracle; CI fails the `go generate` staleness check if the generated file is stale
(ARCH-08). P6 may move to a current Unicode.

**Two width functions (pass-5 D15 as reconciled by sweep C).** hylo carries TWO
character-width functions with disjoint uses — do not merge them:

1. **Render width** — layout parity, render pipeline only. Legacy `visible()` =
   `len(_ANSI.sub("", text))` (SL:152-153 verbatim): ANSI/SGR runs stripped to zero,
   then Python `len()` per code point. pyfmt serves it as `Len` (WTF-8 code-point
   count, surrogate = 1) composed with the SGR-strip primitive. There is NO
   East-Asian-width consultation in the render width — BC-5.03.001's pin that EA
   logic is never consulted holds for the render path. Used by `trim_to_fit` and
   every row-layout decision (BC-1.01.005).
2. **Validation width** — config grammar only, never the render path. The display
   width of a glyph/label value is the sum over its code points of the OD-170 width
   function on hylo's own Unicode 14.0.0 tables: East-Asian Width
   Wide/Fullwidth = 2, combining marks and formats (Mn, Me, Cf) = 0, otherwise 1
   (Ambiguous counts 1; control bytes are range violations, not widths). Used ONLY
   by config validation: the glyph rule (OD-184, superseding the OD-02 "exactly 1
   code point and 1 column" wording that pitted the U+26A1 default against its own
   range) — every `statusline.glyphs.*` / `statusline.subagent.glyphs.*` member is
   exactly 1 code point, except `statusline.glyphs.sparkline` = exactly 8 ordered
   code points, MEASURED IN LEGACY'S RENDER WIDTH (code points, the count legacy's
   layout uses); the East-Asian-Width validation width (columns) applies ONLY to the
   pill-label bound "display width 1..16" (OD-173), per BC-2.01.004 PC-9
   (which names the ARCH-06 coordination).

Grounding (validation width): a glyph such as `▤` is 1 code point / 1 column and
passes; a label such as `中文` measures 4 under the validation width (two
East-Asian-Wide code points x 2 — corrected pass-6 D17; it passes the 1..16 bound);
U+0301 (combining acute) adds 0. Grounding (render width): the same `中文` also
measures 2
(code points), but U+0301 adds 1 — the two functions intentionally differ on
combining marks.

## Signature canon (ADV-P2-D08)

The signatures above are the reconciled canon for the pass-2 remediation: `LocalToUnix`
takes `(fields, loc, msvcDomain bool)` and returns `(int64, error)` with `ErrValue` plus
the distinct Windows `ErrLocaltimeDomain` disposition, and `FromISOFormat` returns
`(float64, error)` so the caller can tell None from degrade (pass-6 A05, call 2 —
superseding the pass-2 `(loc, wall time.Time) -> (int64, error)` and
`(float64, bool)` forms; BC-5.04.002), `TimeFloat` takes `time.Time`
(BC-5.04.003), `MaxSeq(xs []Num) (Num, error)` with typed `ErrValue` (BC-5.01.006 PC-1 —
its Description's `MaxSeq(vals ...Num) Num` sketch is superseded), and `Decode` takes the
per-call-site `depthBudget` (BC-5.02.002/.003). Pass-4 D07 reconciles the encoder
signatures: `Dumps(v, depthBudget) ([]byte, error)` and
`DumpsLen(v, depthBudget) (int, error)` — the 4,300-digit
encoder failure is typed (BC-5.02.006 PC-2, BC-5.02.001) and the depth budget is
per-site in both directions (pass-5 D08/call 10: encoder breach -> `ErrDepth`, the
new typed error in this section; budget table and the one depth law above), per
BC-5.02.001 Inv 4 as corrected by pass-5 D17 (superseding the pass-2
`Dumps(v) []byte` / `DumpsLen(v) int` sketches AND the "limit − 8" module-scope
wording). BC rows that still say "the ARCH-06 row
is stale" (BC-5.01.001/.003/.006, BC-5.03.002) are superseded by this section.
Pass-7 D22 adds the BC-5.01.007 PC-3b NaN-aware relational helpers
(`NumLT`/`NumLE`/`NumGT`/`NumGE`/`NumEQ`/`NumNE`) and the config-grammar
validation-width function (`ValidationWidth`) to the canon.

## Fragment anchors (pass-4 A01; stable targets for BC-body fragment links)

BC bodies link fragments like `architecture/ARCH-06-pyfmt.md#pyfmt-num`; the seven
anchors below are the complete, closed set for this section — new BC fragment links
must target one of these.

<a id="pyfmt-num"></a>
<a id="num"></a>
<a id="pyfmt-json"></a>
<a id="json"></a>
<a id="pyfmt-str"></a>
<a id="pyfmt-time"></a>
<a id="time"></a>

| Anchor | Target |
|---|---|
| `#pyfmt-num` | the `num.go` file row (module overview: CPython 3.11 arithmetic on `Num`, BC-5.01.001..003) |
| `#num` | the `num.go` helper signatures and semantics in the Interfaces block (`D`, `Repr`, `MaxSeq`, `NumToF`/`TrueDiv`/`NumCmp`; BC-5.01.004..007) |
| `#pyfmt-json` | the `json.go` file row (module overview: ordered `Value`/`Member`/`Kind`, depth constants, BC-5.02.001..004) |
| `#json` | the `json.go` function signatures in the Interfaces block (`Decode`/`Dumps`/`Str`; BC-5.02.005/.006) |
| `#pyfmt-str` | the `str.go` file row (WTF-8 string ops, normpath/basename scope; BC-5.03.001..004) |
| `#pyfmt-time` | the `time.go` file row (`FromISOFormat`, `LocalToUnix`; BC-5.04.001..002) |
| `#time` | the `time.go` function signatures in the Interfaces block (`TimeFloat`; BC-5.04.003) |

## Mapping

Helper-level BCs: BC-5.01.004 (D), BC-5.01.005 (Repr), BC-5.01.006 (MaxSeq),
BC-5.01.007 (NumToF/TrueDiv/NumCmp, ADV-P3-D08),
BC-5.02.005 (Str), BC-5.02.006 (Dumps), BC-5.04.003 (TimeFloat) per OD-141; widget-half
consumption per BC-COMPONENT-MAP.md. `Strftime` is reserved for P3/P4 (ledger `t`,
hook log), not implemented in P1.
