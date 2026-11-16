---
document_type: architecture-section
level: L3
section: "statusline"
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, prd-supplements/error-taxonomy.md, semport/hylo-legacy/statusline-target-design.md, behavioral-contracts/BC-INDEX.md]
traces_to: ARCH-INDEX.md
input-hash: "bcf984d"
---

# ARCH-03 — Status line render pipeline (`internal/statusline`)

> The port target. Carries all 93 S1 BCs. Classification: **mixed, core-dominant** —
> pure widget/parser/format functions plus one ordered effect script. CRITICAL tier
> (>= 95% kill rate, OD-135).

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

| # | Step | Seams | Degrade? |
|---|---|---|---|
| 0 | config resolved (D4-EX-3 before any write) | `config.Load` | config-error line |
| 1 | stdin decode (`pyfmt.Decode`, ModeText) | stdin | no — invalid => `{}` (BC-1.01.002/.008) |
| 2 | transcript parse, then mix-cache write | `Files`, `Cache` | D4-EX-2 skip, no degrade |
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
    Load(name string) pyfmt.Value      // never fails: unreadable => empty object
    Save(name string, v pyfmt.Value)   // never fails: errors swallowed
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
cannot occur (IM-14). File families: `guard.go`, `input.go`, `width.go`, `theme.go`,
`lane.go`, `git.go`, `context.go`, `limits.go`, `session.go`, `tokens.go`, `cost.go`,
`transcript*.go`, `mixcache.go`, `telemetry.go`, `sample.go`, `row2.go`, `sparkline.go`,
`cache.go` — one home per S1 subsection (see BC-COMPONENT-MAP.md).

## Mapping

BC-1.01..1.06 subsections -> the file families above (per-row homes in
BC-COMPONENT-MAP.md). Widgets + parser consume `internal/pyfmt` (ARCH-06); metrics
client is the only network edge; caches via ARCH-04.
