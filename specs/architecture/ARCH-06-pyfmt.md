---
document_type: architecture-section
level: L3
section: "pyfmt"
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T02:00:00Z
phase: 1b
inputs: [prd.md, semport/hylo-legacy/statusline-target-design.md, behavioral-contracts/BC-INDEX.md]
traces_to: ARCH-INDEX.md
input-hash: "089b35b"
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
| `num.go` | CPython 3.11 arithmetic on `Num` (int64 / *big.Int / float64 / bool-as-int); `Round` (ties-to-even + decimal re-round, big-int result beyond int64), `RoundN`, `F` ('f' format incl. -0, nan/inf spellings), `D`, `Int`/`Ceil` (exact `Num` results beyond int64, typed NaN/Overflow errors), `FloorDiv`/`Mod` (CPython `float_divmod` port — NOT `math.Floor(a/b)`; `ErrZeroDivision` on zero divisor), `FloorDivInt/ModInt` (integer `//`/`%`, exact for big ints), `Max`/`Min` (first-maximal-wins NaN argument order), `MaxSeq` (typed `ErrValue` on empty), `Repr` (Python repr recipe — see below), `ParseInt`/`ParseFloat` (Python grammar: underscores, Unicode digits, 4,300-digit limit, `1e400`, nan/inf) — BC-5.01.001..006, BC-5.01.003 |
| `Repr` recipe (ADV-P2-D01, normative) | Python `repr(float)` = the shortest round-trip digit string, rendered **fixed** when the decimal exponent satisfies `-4 <= exp < 16`, else in exponent form; Go's shortest `'g'` instead switches to exponent form at `exp >= 6`, so `'g`'s notation decision is never reused — draw the shortest digits from `strconv`/`AppendFloat('g', -1, 64)`, derive `exp = dp - 1` from the digit string, then apply **Python's** fixed/exponent rule; finish with the signed two-digit exponent (`e+09`), the `.0` suffix for integral values, and the `inf`/`nan` spellings. Following `'g'`'s own switching rule yields `1.794615009e+09` where the BC's canonical vector requires `1794615009.0`. — BC-5.01.005 |
| `json.go` | Hand-written decoder/encoder over ordered `Value`/`Member`/`Kind`: `Decode(b, mode, depthBudget)` — the recursion budget is a **per-call-site parameter**, never a mode property and never a package global (BC-5.02.003 invariant 3): named constants pinned by the orchestrator end-to-end measurement of the real legacy program (isolated HOME, 2026-11-17; ADV-P2-A07 CLOSED): `depthStdinLoad = 993` (main → json.load, 6 frames; 993 accepted / 994 rejected, BC-1.01.002), `depthTranscriptLine = 993` (main → _mix_counts → json.loads, 6 frames; also 993/994 — supersedes the earlier frame-local 989/990 probe, which does not transfer across invocation depths), `depthSessionCache = 991` (main → effective_rl → load_cache, 8 frames; 991 accepted / 992 rejected, measured; the get_sample, claude_window_start and mix-cache loaders at the same 8-frame chain depth: 991/992, derived), `depthGitCache = 990` (main → render_lane → git_segment → load_cache, 9 frames; 990 accepted / 991 rejected, measured; the cost-history loaders record_cost and cost_thresholds, called from render_lane, at the same 9-frame depth: 990/991, derived). Governing formula: **limit = 999 − (Python frames from `<module>` down to json's raw_decode)**; full per-site table, measurement recipes and the limit/limit+1 test rule in VP-006. Mode-site pairing: **ModeText serves the stdin and cache loads; ModeBytes serves the transcript line loads** (BC-1.03.004, BC-5.02.003; ADV-P2-A06) — the transcript site's 993 boundary belongs to the ModeBytes site. The pyfmt gen scripts pin the boundaries by re-running the recorded measurement recipes under the pinned oracle — a moved boundary fails regeneration, and the committed tables then pin Go's constants. ModeText = `json.load` text semantics (BOM invalid, invalid-UTF-8 error); ModeBytes = `json.loads(bytes)` (BOM/UTF-16/32 detection, NaN/Infinity tokens, duplicates last-wins keeping position, WTF-8 strings surviving lone surrogates); `Dumps`/`DumpsLen` (json.dump byte defaults, shared escape/float-repr code with DumpsLen so lengths and bytes cannot drift); `Str` (Python str()/repr of values) — BC-5.02.001..006 |
| `str.go` | WTF-8-aware `Len` (surrogate = 1 code point), `Truncate`, `HasSurrogate`, `EncodeUTF8Replace` (lone surrogate -> `?`), `Strip`/`RStrip` (Python whitespace incl. NBSP), `RSplit1`, `SplitLinesBytes` (\n \r\n \r only), `SubNonWord` (per code point before truncation), `PosixNormpath`/`NtNormpath`/`Basename` (per-OS selection, ntpath on Windows) — BC-5.03.001..004 |
| `time.go` | `TimeFloat` (time.Time -> s float, once per render, BC-5.04.003); `FromISOFormat` (3.11 grammar, naive = local, fraction truncation beyond µs, BC-5.04.001); `LocalToUnix` (CPython `_mktime` port: gap/overlap semantics; 0 mismatches over 10,893 CPython goldens across four zone grids; Go `time.Date` differs) with embedded `time/tzdata` — BC-5.04.001..002 |

### Decision: hand-written Python-semantics layer, CPython-generated tables (AD-04)

- **Context:** Go stdlib differs from CPython on JSON leniency (NaN tokens, big ints,
  ordered dicts, WTF-8), float formatting spellings, code-point string ops, and mktime
  gap/overlap — every cache byte and widget byte depends on these.
- **Table-driven expectations:** every file carries a committed CPython-generated
  expectation table; generators live in `internal/pyfmt/testdata/gen/*.py` and run under
  the pinned 3.11 oracle (OD-104). The BC-5.02.002 table (63 cases) is regenerated by
  script, no hand-recorded literals (OD-142). Beyond-int64 durations stay byte-exact via
  `math/big` at exactly two duration-format sites (OD-137).
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
  tables (ARCH-00, ADV-P1-A07); mutation kill rate >= 95% binds here first (tool:
  gremlins, named in ARCH-00; ADR line AD-14 in ARCH-INDEX).
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
func Dumps(v Value) []byte
func DumpsLen(v Value) int
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

## Signature canon (ADV-P2-D08)

The signatures above are the reconciled canon for the pass-2 remediation: `LocalToUnix`
returns `(int64, error)` with `ErrValue` (BC-5.04.002), `TimeFloat` takes `time.Time`
(BC-5.04.003), `MaxSeq(xs []Num) (Num, error)` with typed `ErrValue` (BC-5.01.006 PC-1 —
its Description's `MaxSeq(vals ...Num) Num` sketch is superseded), and `Decode` takes the
per-call-site `depthBudget` (BC-5.02.002/.003). BC rows that still say "the ARCH-06 row
is stale" (BC-5.01.001/.003/.006, BC-5.03.002) are superseded by this section.

## Mapping

Helper-level BCs: BC-5.01.004 (D), BC-5.01.005 (Repr), BC-5.01.006 (MaxSeq),
BC-5.02.005 (Str), BC-5.02.006 (Dumps), BC-5.04.003 (TimeFloat) per OD-141; widget-half
consumption per BC-COMPONENT-MAP.md. `Strftime` is reserved for P3/P4 (ledger `t`,
hook log), not implemented in P1.
