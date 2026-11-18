---
document_type: architecture-section
level: L3
section: "statusline"
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T07:00:00Z
phase: 1b
inputs: [prd.md, prd-supplements/error-taxonomy.md, semport/hylo-legacy/statusline-target-design.md, behavioral-contracts/BC-INDEX.md]
traces_to: ARCH-INDEX.md
input-hash: "de05e56"
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
performs step 0: it calls `config.Load`; on any error it prints the E-CFG-001 line
(first error in registry order, full list to stderr) and returns 0 having written no
caches — `Render` is never entered. `Render`'s precondition is `env.Config != nil`
(non-error `*config.Config`), guaranteed by `Main`; the "no cache writes" guarantee
follows because every cache write sits inside `Render`'s step script.

| # | Step | Seams | Degrade? |
|---|---|---|---|
| 0 | config resolved by `Main` (precondition; D4-EX-3 before any write) | `config.Load` (in `Main`) | config-error line |
| 1 | stdin decode (`pyfmt.Decode`, ModeText) | stdin | no — invalid => `{}` (BC-1.01.002/.008) |
| 2 | transcript parse, then mix-cache write | `Files`, `Cache` | D4-EX-2 skip (wrong-shape lines); CP-S14/S16 degrade sticky (non-string sid at `re.sub` SL:1017; bad `transcript_path` type SL:1010) |
| 3 | effective_rl (session-cache write iff non-empty rl dict) | `Cache`, `Now` | no |
| 4 | get_sample when ROWS >= 2: fetch, then session-cache write | `Metrics`, `Cache`, `Now` | no |
| 5 | row-2 render (width rule) | pure | CP-N01/N02 |
| 6 | window start (may write `proc_start`) | `Proc`, `Cache` | no |
| 7a | lane badge/model/project; git segment (git-cache write) | `Files`, `Cache`, `Cwd` | CP-S01..S04 |
| 7b | thermometer/composition/cache-hit/limits/lines/timer/⌂/tokens | pure | CP-S05..S13 |
| 7c | record_cost (write), then cost_thresholds | `internal/cost` via `Cache` | CP-S15 |
| 7d | $, $/h, ⛏ (pure) | pure | no |
| 8 | trim, surrogate check, single stdout write | stdout | CP-S17 after all writes |

Import-time crash paths CP-X01/X02 are replaced by D4-EX-3 at step 0; CP-X03 (the
degraded-line write failing) is the named exclusion `cp-x03` — Go swallows the write
error and exits 0 (OD-136); CP-X04 (signals) is out of scope.

**Typed crash-path register (normative dispositions live in the owning BCs).** The
script's Degrade? column names the CP families; the full trigger tables are
error-taxonomy.md. Families: CP-S01..S17 (row-1/interaction), CP-T01..T07 (transcript
machine), CP-N01/N02 (row-2 telemetry), **CP-O01..O11** (OD-156 numeric-overflow family:
CP-O01..O05 stdin/metrics-borne at render → E-REN-002, the 29-byte line, exit 0, earlier
writes kept; CP-O06..O08 transcript-borne → the offending line is skipped whole under the
extended D4-EX-2 discipline, no sticky state; CP-O09 moot in hylo; CP-O10/O11
cost-segment stdin-borne overflow — a huge stdin int in `usd`/`api_ms` hitting float
conversion at render, same E-REN-002 disposition, owners BC-1.05.007/.002 — pass-3
C2-01), and **CP-A01..A05** (subagent panel, BC-1.07.008: typed degrades to the 29-byte
line, exit 0; CP-A04/A05 = huge-int `tokenCount`/`startTime` OverflowError paths added
by the pass-3 ruling, owners BC-1.07.007/.008).

## Interfaces (design doc §2.2, reused as the contract)

```go
package statusline

// Main runs one refresh: reads stdin, renders, writes stdout. Always returns 0.
func Main(stdin io.Reader, stdout, stderr io.Writer, env Env) int

// Render is the orchestrator behind Main (BC-1.01.009 order). On errDegraded the
// caller prints degradedLine; cache writes made before the error persist.
func Render(stdin []byte, env Env) ([]byte, error)

const degradedLine = "\x1b[90mstatusline degraded\x1b[0m\n" // 29 bytes, BC-1.01.001
var errDegraded = errors.New("statusline degraded")

type Env struct {
    Now     func() float64        // Python time.time() value; read ONCE per render (IM-14)
    Loc     *time.Location        // naive transcript timestamps (BC-5.04.001)
    Getenv  func(string) string   // COLUMNS only (protocol input, not a setting)
    Config  *config.Config        // resolved once at step 0 (D15)
    Cache   CacheStore            // paths.cache_dir (OD-101); temp dir in tests
    Metrics MetricsClient         // backends[0].metrics_url; httptest fake in tests
    Proc    ProcStarter           // platform.FindAncestor; fake in tests
    Files   FileSystem            // transcript and .git reads; os-backed by default
    Cwd     func() string         // git fallback when no project dir
}

type CacheStore interface {
    Load(name string) pyfmt.Value    // never fails: unreadable => empty object
    Save(name string, v pyfmt.Value) error // reports the write outcome to the caller (ADV-P2-A25, VP-018); Render swallows it — DI-008 never-raise at the orchestrator
}
type MetricsClient interface {
    Query(ctx context.Context, promql string) ([]byte, error) // total deadline, Proxy: nil
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
these.

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
