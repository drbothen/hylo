---
document_type: architecture-section
level: L3
section: "pyfmt"
version: "1.6"
status: draft
producer: architect
timestamp: 2026-11-17T22:30:00Z
phase: 1b
inputs: [prd.md, semport/hylo-legacy/statusline-target-design.md, behavioral-contracts/BC-INDEX.md]
traces_to: ARCH-INDEX.md
input-hash: "9664a5d"

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
| `num.go` | CPython 3.11 arithmetic on `Num` (int64 / *big.Int / float64 / bool-as-int); `Round` (ties-to-even + decimal re-round, big-int result beyond int64), `RoundN`, `F` ('f' format incl. -0, nan/inf spellings), `D`, `Int`/`Ceil` (exact `Num` results beyond int64, typed NaN/Overflow errors), `FloorDiv`/`Mod` (CPython `float_divmod` port — NOT `math.Floor(a/b)`; `ErrZeroDivision` on zero divisor), `FloorDivInt/ModInt` (integer `//`/`%`, exact for big ints), `Max`/`Min` (first-maximal-wins NaN argument order), `MaxSeq` (typed `ErrValue` on empty), `Repr` (Python repr recipe — see below), `ParseInt`/`ParseFloat` (Python grammar: underscores, Unicode digits, 4,300-digit limit, `1e400`, nan/inf), `NumToF`/`TrueDiv`/`NumCmp` (CPython mixed int/float semantics: `NumToF` float(int)
conversion with typed `ErrOverflow` at `|n| >= 2**1024 - 2**970`, `TrueDiv` int/int exact rational quotient
rounded once to float64 (operands not pre-truncated) with `ErrZeroDivision`, `NumCmp` exact cross-kind
comparison — which also pins Max/Min exact tie-breaks) — BC-5.01.001..007, BC-5.01.003 |
| `Repr` recipe (ADV-P2-D01, normative) | Python `repr(float)` = the shortest round-trip digit string, rendered **fixed** when the decimal exponent satisfies `-4 <= exp < 16`, else in exponent form; Go's shortest `'g'` instead switches to exponent form at `exp >= 6`, so `'g`'s notation decision is never reused — draw the shortest digits from `strconv`/`AppendFloat('g', -1, 64)` (the same shortest digit string the BC-5.01.005 recipe draws from the `'e'` form; `'g'` is a DIGIT SOURCE here, not a notation authority — the notation decision is always re-applied from Python's rule, which is how the two wordings reconcile), derive `exp = dp - 1` from the digit string, then apply **Python's** fixed/exponent rule; finish with the signed two-digit exponent (`e+09`), the `.0` suffix for integral values, and the `inf`/`nan` spellings. Following `'g'`'s own switching rule yields `1.794615009e+09` where the BC's canonical vector requires `1794615009.0`. — BC-5.01.005 |
| `json.go` | Hand-written decoder/encoder over ordered `Value`/`Member`/`Kind`: `Decode(b, mode, depthBudget)` — the recursion budget is a **per-call-site parameter**, never a mode property and never a package global (BC-5.02.003 invariant 3): named constants pinned by the orchestrator end-to-end measurement of the real legacy program (isolated HOME, 2026-11-17; ADV-P2-A07 CLOSED): `depthStdinLoad = 993` (main → json.load, 6 frames; 993 accepted / 994 rejected, BC-1.01.002), `depthTranscriptLine = 993` (main → _mix_counts → json.loads, 6 frames; also 993/994 — supersedes the earlier frame-local 989/990 probe, which does not transfer across invocation depths), `depthSessionCache = 991` (main → effective_rl → load_cache, 8 frames; 991 accepted / 992 rejected, measured; the get_sample, claude_window_start and mix-cache loaders at the same 8-frame chain depth: 991/992, derived), `depthGitCache = 990` (main → render_lane → git_segment → load_cache, 9 frames; 990 accepted / 991 rejected, measured; the cost-history loaders record_cost and cost_thresholds, called from render_lane, at the same 9-frame depth: 990/991, derived). Governing formula: **limit = 999 − (Python frames from `<module>` down to json's raw_decode)**; full per-site table, measurement recipes and the limit/limit+1 test rule in VP-006. Mode-site pairing: **ModeText serves the stdin and cache loads; ModeBytes serves the transcript line loads** (BC-1.03.004, BC-5.02.003; ADV-P2-A06) — the transcript site's 993 boundary belongs to the ModeBytes site. The pyfmt gen scripts pin the boundaries by re-running the recorded measurement recipes under the pinned oracle — a moved boundary fails regeneration, and the committed tables then pin Go's constants. ModeText = `json.load` text semantics (BOM invalid, invalid-UTF-8 error); ModeBytes = `json.loads(bytes)` (BOM/UTF-16/32 detection, NaN/Infinity tokens, duplicates last-wins keeping position, WTF-8 strings surviving lone surrogates); `Dumps`/`DumpsLen` (json.dump byte defaults, shared escape/float-repr code with DumpsLen so lengths and bytes cannot drift); `Str` (Python str()/repr of values) — BC-5.02.001..006 |
| `str.go` | WTF-8-aware `Len` (surrogate = 1 code point), `Truncate`, `HasSurrogate`, `EncodeUTF8Replace` (lone surrogate -> `?`), `Strip`/`RStrip` (Python whitespace incl. NBSP), `RSplit1`, `SplitLinesBytes` (\n \r\n \r only), `SubNonWord` (per code point before truncation), `PosixNormpath`/`NtNormpath`/`Basename` (per-OS selection, ntpath on Windows). Scope note (pass-3 D14, sharpened pass-4 D18): pyfmt contracts ONLY normpath (both flavors) and basename — `abspath`/`join`/`dirname` are NOT pyfmt functions, because Windows `abspath` needs cwd via GetFullPathNameW (an effect); any caller needing abs-path resolution performs it in `internal/statusline` against the `Cwd`/`Files` seams (ARCH-03), never inside pure pyfmt. BC-5.03.004 Inv 3's citation of `abspath`/`join`/`dirname` (SL:373-390) as "served by pyfmt" is SUPERSEDED by this scope rule (the underlying SL:373-390 behavior is served by `internal/statusline`); the flavor rule is uniform: `Basename` — and every per-OS flavor selection pyfmt makes — is a pure function of the build target (`runtime.GOOS`, compile-time constant per build; both flavors always compiled and table-pinned on every OS), never a caller choice. BC-5.03.004's posix/nt `join`/`dirname`/`abspath` flavor pinning is a product-owner obligation tracked for the next BC pass (pass-4 D18) | BC-5.03.001..004 |
| `time.go` | `TimeFloat` (time.Time -> s float, once per render, BC-5.04.003); `FromISOFormat` (3.11 grammar, naive = local, fraction truncation beyond µs, BC-5.04.001); `LocalToUnix` (CPython `_mktime` port: gap/overlap semantics; 0 mismatches over 10,893 CPython goldens across four zone grids; Go `time.Date` differs) with embedded `time/tzdata` — BC-5.04.001..002 |

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
  logic in `pyfmt` is `Basename` choosing ntpath on Windows. It is deliberately NOT
  routed through `internal/platform`: `pyfmt` is the repo's lowest sink and importing
  infrastructure from it would invert AD-02's dependency direction. The selection is a
  pure function of the build target; both flavors are always compiled and always
  table-pinned on every OS, so no build tag or platform call is needed.

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
func NumToF(x Num) (float64, error)     // BC-5.01.007: float(int); ErrOverflow at |n| >= 2**1024 − 2**970
func TrueDiv(a, b Num) (float64, error) // BC-5.01.007: true division; exact int/int quotient rounded once; ErrZeroDivision
func NumCmp(a, b Num) (int, error)      // BC-5.01.007: exact cross-kind comparison (never rounds the int to float64)
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
func Dumps(v Value) ([]byte, error)    // (ADV-P4-D07) encoder failure is typed: the 4,300-digit int-to-string limit (BC-5.02.001/.006)
func DumpsLen(v Value) (int, error)    // shared escape/float-repr code with Dumps so lengths and bytes cannot drift (BC-5.02.001)
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
func PosixNormpath(p string) string
func NtNormpath(p string) string
func Basename(p string) string        // runtime.GOOS selects ntpath on Windows; both flavors always compiled and table-pinned (see P18 note)

func TimeFloat(t time.Time) float64
func FromISOFormat(s string, loc *time.Location) (float64, bool)
func LocalToUnix(loc *time.Location, wall time.Time) (int64, error) // BC-5.04.002: Unix seconds; ErrValue (not a bool)
```

### Unicode tables (OD-170, pass-4)

hylo carries its own Unicode 14.0 tables for every character class pyfmt consults
(decimal digit Nd for `ParseInt`/`ParseFloat`, printable and whitespace for
`Strip`/`RStrip`, the word-character class for `SubNonWord`, and any other class a gen
script exercises), generated from CPython 3.11.7 `unicodedata` by a committed generator
script run under `go generate`; pyfmt never consults Go's `unicode` package for these
classes (Go's bundled tables are newer and diverge on post-14.0 assignments — e.g. Kawi
digits U+11F50-59). A version constant (`14.0.0`) and a test pin the tables to the
oracle; CI fails the `go generate` staleness check if the generated file is stale
(ARCH-08). P6 may move to a current Unicode.

## Signature canon (ADV-P2-D08)

The signatures above are the reconciled canon for the pass-2 remediation: `LocalToUnix`
returns `(int64, error)` with `ErrValue` (BC-5.04.002), `TimeFloat` takes `time.Time`
(BC-5.04.003), `MaxSeq(xs []Num) (Num, error)` with typed `ErrValue` (BC-5.01.006 PC-1 —
its Description's `MaxSeq(vals ...Num) Num` sketch is superseded), and `Decode` takes the
per-call-site `depthBudget` (BC-5.02.002/.003). Pass-4 D07 reconciles the encoder
signatures: `Dumps(v) ([]byte, error)` and `DumpsLen(v) (int, error)` — the 4,300-digit
encoder failure is typed, per BC-5.02.006 PC-2 and BC-5.02.001 (superseding the
pass-2 `Dumps(v) []byte` / `DumpsLen(v) int` sketches). BC rows that still say "the ARCH-06 row
is stale" (BC-5.01.001/.003/.006, BC-5.03.002) are superseded by this section.

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
