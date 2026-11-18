---
document_type: architecture-section
level: L3
section: "statusline"
version: "1.7"
status: draft
producer: architect
timestamp: 2026-11-19T04:00:00Z
phase: 1b
inputs: [prd.md, prd-supplements/error-taxonomy.md, semport/hylo-legacy/statusline-target-design.md, behavioral-contracts/BC-INDEX.md]
traces_to: ARCH-INDEX.md
input-hash: "0258ea6"

---

# ARCH-03 — Status line render pipeline (`internal/statusline`)

> The port target. Carries all S1 BCs (BC-1.01..1.07, including the OD-155 subagent
> panel, BC-1.07.001..008). Classification: **mixed, core-dominant** —
> pure widget/parser/format functions plus one ordered effect script. CRITICAL tier
> (line coverage >= 95% for P1; mutation kill rate >= 95% is the Phase 6 target,
> OD-135/OD-158).

### Decision: pure widgets plus an ordered effect script (AD-03)

- **Context:** legacy reads back its own writes within one refresh (effective_rl writes
  the session cache; get_sample re-reads and rewrites it; window start re-reads it), so
  the whole refresh cannot be one pure function — an in-memory overlay would get the
  failed-replace persistence semantics wrong (BC-1.06.002: a failed replace persists
  nothing and the next read must see that).
- **Options considered:** (1) one pure render + a final commit block — wrong persistence
  semantics on failed replaces; (2) pure widgets + one orchestrator executing legacy's
  effect order through injected seams.
- **Decision:** option 2 (design doc §3). The orchestrator `Render` executes the step
  script below, calling seams in exactly legacy's order (BC-1.01.009): a crash at step
  k keeps the writes of steps 1..k-1.
- **Rationale:** identical cache states after both happy and degraded runs are a parity
  requirement; only order-preserving effects achieve it.
- **Consequences:** every nondeterminism source is an `Env` interface; the pure renders
  are table-testable without a temp dir; the seams double as harness hooks (ARCH-07).
- **Verification feasibility:** pure renders — **provable-grade** oracle-pinned tables,
  mutation target >= 95%; the effect order — **testable-only**, order-asserting recording
  fakes plus parity steps (ARCH-07). A widget that needs I/O gets redesigned, not patched
  (iron law).

## Effect-step script (design doc §3.1, normative)

**Ownership of step 0 (ADV-P2-A08):** config resolution is NOT inside `Render`. `Main`
performs step 0: it calls `config.Load` through the injected `EnvVars` seam it is given
(AD-10 amended; ARCH-01), then constructs over the Load-resolved configuration every
seam that reads config at build time (pass-5 A11 — `Query`/`WindowStart` take no
config argument, so pre-built arrivals are impossible):
the `CacheStore` over `paths.cache_dir`, the `MetricsClient` over
`backends[0].metrics_url` and `telemetry.timeout_s`, and the `ProcStarter` over
`window_age.process_name` and `window_age.max_depth`; on any error it prints the E-CFG-001 line
(first error in registry order, full list to stderr) and returns 0 having written no
caches — `Render` is never entered. `Render`'s precondition is `env.Config != nil &&
env.Cache != nil`
(non-error `*config.Config`), guaranteed by `Main`; the "no cache writes" guarantee
follows because every cache write sits inside `Render`'s step script.

| # | Step | Seams | Degrade? |
|---|---|---|---|
| 0 | config resolved by `Main` (precondition; D4-EX-3 before any write) | `config.Load` (in `Main`) | config-error line |
| 1 | stdin decode (`pyfmt.Decode`, ModeText) | stdin | no — invalid => `{}` (BC-1.01.002/.008) |
| 2 | transcript parse, then mix-cache write | `Files`, `Cache` | D4-EX-2 skip (wrong-shape lines); CP-O06..O08 overflow lines skipped whole, in-flight turn dropped (OD-167); CP-S14/S16 degrade sticky (non-string sid at `re.sub` SL:1017; bad `transcript_path` type SL:1010); Windows: a naive timestamp on/before 1970-01-01 or from year ≥ 3001 makes MSVC `localtime_s` raise OSError out of `_iso_ts` (which catches only ValueError) and DEGRADES the whole line (BC-5.04.001 v1.2.3, owner call 8; pass-6 C01 — Windows test vectors derived from the pre-call-8 BCs assert the wrong outcome) |
| 3 | effective_rl (session-cache write iff non-empty rl dict) | `Cache`, `Now` | no |
| 4 | get_sample when ROWS >= 2: fetch, then session-cache write | `Metrics`, `Cache`, `Now` | no |
| 5 | row-2 render (width rule) | pure | CP-N01/N02/N03 |
| 6 | window start (may write `proc_start`) | `Proc`, `Cache` | no |
| 7a | lane badge/model/project; git segment (git-cache write) | `Files`, `Cache`, `Cwd` | CP-S01..S04 |
| 7b | thermometer/composition/cache-hit/limits/lines/timer/⌂/tokens | pure | CP-S05..S13 |
| 7c | record_cost (write), then cost_thresholds | `internal/cost` via `Cache` | CP-S15; unconvertible `usd`/`api_ms` is not recorded (OD-166) — Go skips the record where legacy persisted the raw int, the ruled write-divergence exclusion `OD-166`; history-borne CP-O10/O11 raise HERE in `cost_thresholds` (SL:255; site correction per pass-4 B14, propagated pass-5 A09), owner BC-1.05.005 EC-011 — the bearer (the cost-history cache persisted the value earlier) is unchanged |
| 7d | $, $/h, ⛏ (pure) | pure | CP-O10/O11 (E-REN-002) — disposition only; the history-borne raise sits in step 7c, so the SL:616/623 render sites are unreachable for history-borne values (pass-4 B14) |
| 8 | trim, surrogate check, single stdout write | stdout | CP-S17 after all writes |

Import-time crash paths CP-X01/X02 are replaced by D4-EX-3 at step 0; CP-X03 (the
degraded-line write failing) is the named exclusion `cp-x03` — Go swallows the write
error and exits 0 (OD-136; per OD-172 the same discipline extends to `--subagent` row
writes: a stdout write failure while printing rows stops writing and exits 0, with no
degraded-line attempt); CP-X04 (signals) is out of scope.

**Typed crash-path register (normative dispositions live in the owning BCs).** The
script's Degrade? column names the CP families; the full trigger tables are
error-taxonomy.md. Families: CP-S01..S17 (row-1/interaction), CP-T01..T07 (transcript
machine), CP-N01..N03 (row-2 telemetry; pass-4 C2-12), **CP-O01..O11** (OD-156 numeric-overflow family:
CP-O01..O05 stdin/metrics-borne at render → E-REN-002, the 29-byte line, exit 0, earlier
writes kept; CP-O06..O08 transcript-borne → the offending line is skipped whole under the
extended D4-EX-2 discipline, no sticky state, and the in-flight turn is dropped
(OD-167); CP-O09 reachable in hylo — two 4,300-digit ints accumulate without meeting a
float and breach CPython's int-to-string limit at the save (ADV-P3-C09; not moot,
disposition per the owning BC); CP-O10/O11
cost-segment overflow — a huge exact int in `usd`/`api_ms` overflowing int→float
conversion in the `cost_thresholds` division at SL:255 (`usd / (api / 3.6e6)`;
OverflowError at \|n\| >= 2**1024−2**970 — an int-to-string reading is WRONG: an int
over ~4,300 digits cannot even load, and the int-to-string breach at the save is
CP-O09's site, not this one; pass-6 A06) (step 7c; the SL:616/623 render sites are unreachable for
history-borne values because `cost_thresholds` raises first — pass-4 B14 site
correction, propagated pass-5 A09), same E-REN-002 disposition, owner BC-1.05.005
EC-011, bearer the cost-history cache), and **CP-A01..A05** (subagent panel, BC-1.07.008: typed degrades to the 29-byte
line, exit 0; CP-A04/A05 = huge-int `tokenCount`/`startTime` OverflowError paths added
by the pass-3 ruling, owners BC-1.07.007/.008), and **CP-N03** (pass-4 C2-12: the
metrics-borne degrade — a numeric `__name__` key sorting ahead of every `vllm:` key so
`k.startswith` raises AttributeError, SL:717; owner BC-1.04.005 EC-007 / BC-1.04.004
(pass-5 A24 correction — the degrade sits in `serving_state`), E-REN-002 disposition).

## Interfaces (design doc §2.2, reused as the contract)

```go
package statusline

// Main runs one refresh and always returns 0. Wiring order (ADV-P4-A06; pass-5 A11):
// step 0 resolves config THROUGH the injected EnvVars seam (AD-10 amended — never a bare
// func(string) string); only then does Main construct, over the Load-resolved
// configuration: the CacheStore (resolved paths.cache_dir), the MetricsClient
// (backends[0].metrics_url + telemetry.timeout_s), and the ProcStarter
// (window_age.process_name + window_age.max_depth). Env.Cache/Metrics/Proc are empty
// before step 0 and filled by Main — the seams do not presuppose the dir/url/pid.
func Main(stdin io.Reader, stdout, stderr io.Writer, env *Env) int

// Render is the orchestrator behind Main (BC-1.01.009 order). On errDegraded the
// caller prints degradedLine; cache writes made before the error persist.
// Preconditions: env.Config != nil && env.Cache != nil, guaranteed by Main.
func Render(stdin []byte, env Env) ([]byte, error)

// Panel is the subagent entry point's body (BC-1.07.001..008), called by
// runStatuslineSubagent after that entry point resolves config itself (OD-168).
// Renders the NDJSON panel rows to stdout; the elapsed-clock widget reads Now
// (BC-1.07.007). Same degrade discipline as Main (typed CP-A01..A05 sites + the
// recover() backstop), and OD-172 row-write discipline: a stdout write failure
// while printing rows stops writing and exits 0.
func Panel(stdin io.Reader, stdout, stderr io.Writer, env *Env) int

const degradedLine = "\x1b[90mstatusline degraded\x1b[0m\n" // 29 bytes, BC-1.01.001
var errDegraded = errors.New("statusline degraded")

type Env struct {
    Now     func() float64        // Python time.time() value; read ONCE per render (IM-14); the panel reads it too (BC-1.07.007). Frozen clock (pass-5 D02/call 7): HYLO_TEST_NOW is parsed to a float64 exactly as Python float() (within the BC grammar) and THAT float IS the time.time() value everywhere — never round-tripped through time.Time nanoseconds (float64 spacing at 1.79e18 ns exceeds the seconds-value ulp; cache bytes would drift); TimeFloat applies only to the real clock (ARCH-06 time.go)
    Loc     *time.Location        // naive transcript timestamps (BC-5.04.001)
    EnvVar  EnvVars               // AD-10 seam (ARCH-01: Lookup + Names); backs the COLUMNS lookup (BC-1.01.005) and the unknown-HYLO_* sweep (BC-2.01.001 PC-6). The former bare Getenv func(string) string is superseded (ADV-P4-A06)
    Config  *config.Config        // filled by Main at step 0 (D15); Render precondition
    Cache   CacheStore            // constructed by Main after step 0 over the resolved dir (OD-101); temp dir in tests
    Metrics MetricsClient         // constructed by Main after step 0 from backends[0].metrics_url + telemetry.timeout_s (pass-5 A11); httptest fake in tests
    Proc    ProcStarter           // constructed by Main after step 0 from window_age.process_name + window_age.max_depth (pass-5 A11); fake in tests
    Files   FileSystem            // transcript and .git reads; os-backed by default
    Cwd     func() string         // git fallback when no project dir
    Abs     func(p string) (string, error) // per-flavor absolute-path resolution served by internal/statusline (GetFullPathNameW on Windows), backing BC-1.02.004 EC-012 drive-relative "C:rel" resolution — a bare Cwd func() string cannot express it (pass-6 A18); never inside pure pyfmt (ARCH-06 scope note)
}

type EnvVars interface {
    Lookup(name string) (value string, ok bool) // ok=false => unset; ok=true + "" => set-but-empty
    Names() []string                            // full environ listing; backs the unknown-HYLO_* sweep
}

type CacheStore interface {
    // Depth budgets are PER FILE, not per interface (pass-5 A10): Load decodes and
    // Save encodes with the file's constant from the ARCH-06 depth law, in total
    // JSON nesting depth (the decode convention). Measured END-TO-END on real
    // legacy this burst (pass-5 sweep C: isolated temp HOME+cwd, never the real
    // HOME; python3 -I, CPython 3.11.7):
    //
    //     file          Load(decode)  Save(encode)   reachable from input?
    //     session       991           991            YES — Save re-encodes the stdin-borne rl
    //     mix           991           991            no — flat legacy-computed payload
    //     git           990           990            no — flat legacy-computed payload
    //     cost-history  990           990            no — flat legacy-computed payload
    //
    // One law, both directions (ARCH-06): the encoder boundary is 995 − s for
    // json.dump and 994 − s for json.dumps (s = Python frames at the invoke,
    // invoking frame inclusive), slope exactly 1 slot per frame — a DEEPER stack
    // never has the larger budget, and every cache's Save budget EQUALS its Load
    // budget, so Decode(Save(x)) never rejects what Save produced. The real
    // exposure is the stdin side: a rate_limits value nested 991..992 decodes
    // (stdin bound 993) yet breaches the session Save budget 991 — legacy skips
    // the write (SL:307-308), ruled in-band behavior (BC-5.02.006). Mix, git and
    // cost-history Save constants are unreachable from input (flat payloads) but
    // are still named per-file constants (D15), pinned by the same law; the
    // owning-BC gen recipes re-measure and a moved boundary fails table
    // regeneration (measurement recipes: VP-006).
    Load(name string) pyfmt.Value    // never fails: unreadable => empty object
    Save(name string, v pyfmt.Value) error // reports the write outcome to the caller (ADV-P2-A25, VP-018); Render swallows it — DI-008 never-raise at the orchestrator
}
type MetricsClient interface {
    // MINIMAL HTTP/1.1 CLIENT OVER net.Conn, plain http only (pass-6 C2-02/C2-05,
    // call 4; OD-181 limits parity to http): Go's net/http trims header values
    // (textproto) and url.Parse rejects "%" without two hex digits, while urllib
    // keeps both — so net/http cannot reproduce urllib's targets byte-exactly.
    // The client sends exactly urllib's request headers (method GET, `Host`,
    // `User-Agent: Python-urllib/3.11`, `Accept-Encoding: identity`,
    // `Connection: close`, in urllib's order; verify against the CPython 3.11.7
    // source) and parses status line and headers as http.client does (compat32:
    // header values keep inner and trailing spaces, only CR/LF stripped).
    // MANUAL REDIRECT LOOP: hylo drives the hops itself, so urllib's rules apply
    // exactly: follow `location` then `uri` headers; a present-but-EMPTY Location
    // resolves by urljoin(<URL of the request that received this 3xx>, "") — from
    // the second hop on that is the CURRENT hop's URL, not the first request's
    // (pass-6 C2-02, call 4; supersedes the "redirects to the original URL" rule).
    // An empty fragment is dropped by urlunsplit, so /x# and /x are one loop key.
    // After urlunparse, normalize quote(url, encoding="iso-8859-1",
    // safe=string.punctuation), then urljoin (verified in CPython 3.11.7 source).
    // Hop rules are urllib's visited-set/max_repeats/max_redirections limits — 37 is
    // the worst-case chain length, NOT a hop budget (pass-6 C2-03, call 4;
    // BC-1.04.001). Schemes outside http/https give NO sample — the ruled closed-set
    // exclusion OD-181, "metrics transport beyond plain http" (non-http(s) redirect
    // targets included; parity cases use plain http only).
    // UserInfo (pass-5 C2-03 ruling OD-180): a metrics URL with userinfo reproduces
    // legacy — NO sample (urllib puts u:p@host into HTTPConnection's host, DNS fails,
    // the dead rung); no exclusion id.
    // Total deadline, Proxy: nil. Raw bytes in, no transparent decompression (urllib
    // sends Accept-Encoding: identity and parses the body raw; an auto-gzip response
    // legacy never asked for would give Go a sample where legacy gets none, a
    // spurious VP-030 divergence — the net.Conn design has no auto-gzip by
    // construction, superseding the DisableCompression transport note).
    // Reply decode: pyfmt.Decode(b, ModeBytes, depthMetricsReply = 992) (pass-6 A07,
    // call 5 — legacy fetch_sample calls json.loads(resp.read()) on bytes, SL:171,
    // so BOM/UTF-16/32 detection applies; BC-5.02.004).
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

A `recover()` backstop in `Main` maps any panic to `degradedLine` (mirrors
`except Exception`); typed CP-* sites return `errDegraded` wrappers with per-site catch
lists reproduced exactly (IM-15). One clock read per render; a live-clock minute-straddle
cannot occur (IM-14). File families: `guard.go`, `input.go`, `statusline.go`,
`width.go`, `theme.go`,
`lane.go`, `git.go`, `context.go`, `limits.go`, `session.go`, `tokens.go`, `cost.go`,
`transcript*.go`, `mixcache.go`, `telemetry.go`, `sample.go`, `row2.go`, `sparkline.go`,
`cache.go`, `subagent.go` — one home per S1 subsection (see BC-COMPONENT-MAP.md;
`subagent.go` hosts the OD-155 agent-panel contracts BC-1.07.001..008, dispatched per
ARCH-01; `statusline.go` hosts
the frame-level contracts BC-1.01.003/.009 and BC-1.04.013, ADV-P1-A20).

## Fragment anchors (pass-3 B10/C15; stable targets for BC-body fragment links)

BC bodies link fragments like `architecture/ARCH-03-statusline.md#lane`; the twelve
anchors below are the complete, closed set — new BC fragment links must target one of
these. Practice note (pass-5 C2-14, call 19): BC bodies additionally link the
auto-generated heading slugs of this section (`#effect-step-script-…`,
`#interfaces-design-doc-22-…`); those resolve and are recognized targets. The ONLY
banned form is the bare line-number pointer (`ARCH-03:NNN`) — never an anchor, always
drifts; line-number pointers in BC bodies are replaced by fragment anchors on sight.

<a id="lane"></a>
<a id="git"></a>
<a id="context"></a>
<a id="limits"></a>
<a id="session"></a>
<a id="statusline-width"></a>
<a id="statusline-guard"></a>
<a id="transcript"></a>
<a id="telemetry"></a>
<a id="cost"></a>
<a id="caches"></a>
<a id="subagent"></a>

| Anchor | Target |
|---|---|
| `#lane`, `#git`, `#context`, `#limits`, `#session`, `#statusline-width` | row-1 widget file families (`lane.go`, `git.go`, `context.go`, `limits.go`, `session.go`, `width.go`) in the Interfaces paragraph |
| `#transcript`, `#telemetry`, `#cost`, `#caches`, `#subagent` | `transcript*.go`/`mixcache.go`, `telemetry.go`/`row2.go`/`sample.go`, `cost.go` + `internal/cost`, `cache.go` (ARCH-04), `subagent.go` |
| `#statusline-guard` | the 29-byte degraded-line guard (`guard.go`, BC-1.01.001) |

## Mapping

BC-1.01..1.06 subsections -> the file families above (per-row homes in
BC-COMPONENT-MAP.md). Widgets + parser consume `internal/pyfmt` (ARCH-06); metrics
client is the only network edge; caches via ARCH-04.
