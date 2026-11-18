---
document_type: architecture-section
level: "L3"
section: "configuration"
version: "1.6"
status: draft
producer: architect
timestamp: 2026-11-20T22:00:00Z
phase: 1b
inputs: [prd.md, prd-supplements/interface-definitions.md, prd-supplements/error-taxonomy.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "1142d58"

---

# ARCH-02 — Configuration (`internal/config`)

> Typed, registry-declared `HYLO_*` settings. P1 resolution: built-in defaults ->
> overridden by `HYLO_*` env only (OD-107); the file layer and its YAML dependency are
> reserved for P4 (DI-010 full order file -> env -> default completes then). `DGX_*` is
> never read (OD-05). Classification: **boundary** — pure registry + grammars, one
> env-reading edge (`Load`).

## Key registry (D15, OD-114, BC-2.01.004)

Every key declares `Key{Name, Type, Default, Range, Unit, Op, Rationale, RationaleCode, Class}`
in `registry.go`; the P1 subset lives in `statusline_keys.go` (families per design doc
§2.4: telemetry, rows/layout, sparkline, git, limits, context/units/theme, timers/window
age, cost, row-2 widgets, transcript/turn/composition, glyphs, `paths.cache_dir`,
`backends[0].*`, and `statusline.subagent.enabled` (Bool, default true = legacy, OD-155,
BC-1.07.002)). Golden pin: `internal/config/testdata/legacy_defaults.golden`.
Env name rule (OD-01): `EnvName(key) = HYLO_` + upper snake with every `.`, `[`, `]` run
collapsed to one `_` (`backends[0].metrics_url` -> `HYLO_BACKENDS_0_METRICS_URL`);
build-time collision test; unknown `HYLO_*` warns on stderr and never changes exit
status (BC-2.01.001). Grammar per type in `types.go`: typed bool
`true|false|1|0|yes|no` (OD-05), comma lists (OD-74), `~` expansion in paths (OD-61,
`~user` left as written), `COLUMNS` excluded as protocol input (BC-1.01.005, BC-2.01.005).
Per-OS env/path behavior (P18, ADV-P1-D21) is build-tag confined in `internal/platform`
and consumed by `config`: `platform.HomeDir(env EnvVars)` backs `~` expansion (on Windows `~` and
`~\` expand against `USERPROFILE`, BC-2.01.005). Environment access is the injected
`EnvVars` seam of ARCH-01 (AD-10) — `Lookup(name) (string, bool)` plus `Names()`; the
Windows NT case-insensitive `HYLO_*` name matching is a `platform`-provided
**implementation of that same interface**, injected into `config.Load` at the seam —
never a call around it (ADV-P2-A02), so tests fake env behavior on every OS. The
`paths.*` **defaults are
owned by `internal/platform`** (`CacheDir(env EnvVars) (string, error)` / `StateDir(env EnvVars) (string, error)` /
`ConfigDir(env EnvVars) (string, error)`, OD-95/OD-101/OD-144;
ADV-P1-A16; env-injected signatures with error returns per pass-8 D01, orchestrator call 7 —
BC-3.01.001 EC-004 requires the error when a directory cannot be determined, and
`config path` exits 1 on it) — the registry stores the resolver, not a literal. The cfg→plat edge is
drawn in ARCH-00's dependency graph; pyfmt and platform remain the two sinks.

- **Context:** legacy parsed `DGX_*` ad hoc at import; a malformed number crashed before
  the guard (blank, exit 1 — CP-X01/X02).
- **Options considered:** (1) per-key ad hoc parsing; (2) one closed registry with
  declared domains and stable registry-order errors.
- **Decision:** option 2 (AD-06). A run with any invalid value renders the D4-EX-3 line
  `\e[90mhylo: config error: <key>=<value> (<reason>)\e[0m\n`, exit 0, first error in
  **registry order** on stdout, full list + `[from <ENVNAME>]` on stderr, and **no cache
  writes** (BC-2.02.001; OD-102).
- **Rationale:** closed registry makes the valid domain of every key enumerable and the
  error set closable at SEVEN classes (number-range, number-grammar, enum, URL, boolean,
  theme/SGR, text — OD-114/OD-134/OD-140; the seventh Text class closed by OD-178,
  pass-6 A01). The register being closed, an eighth class needs an owner decision.
- **Consequences:** every threshold row of P4r7 §B.2.1 becomes a registry entry; two
  documented default exceptions to "defaults equal legacy": `paths.cache_dir` (OD-101)
  and `backends[0].model_prefixes` = `claude-sonnet` (OD-111/OD-123). Per OD-162 every
  key carries a `Range`; an out-of-range value is a **number-range config error**
  (BC-2.02.002/.003), and where the owning BC defines no non-default behavior the
  range is the default value only (e.g. `statusline.units.context` — the fixed
  1e6/1000 M/K divisors are format constants, so no non-default labels exist, and
  `statusline.theme.heat`, BC-1.02.019 — pass-4 A12: the `statusline.context.*`
  percentage keys are NOT default-only; BC-1.02.006 PC3-PC5 defines non-default
  behavior). int64-overflow
  and Duration-ceiling values are number-range cases riding D4-EX-3 (OD-164).
- **Verification feasibility:** grammars and ordering are pure — **provable** by
  oracle-pinned class tables (BC-2.02.002..006) plus a registry-order property test
  (first-error selection is order-stable); env reading is testable-only (one thin edge).

## Interfaces

```go
type Config struct{ Statusline Statusline; Cost Cost; Paths Paths; Backends []Backend }
// Load returns the FULL ordered error list in stable registry order (ADV-P2-A01):
// the stdout line renders Errors.First(), the full list goes to stderr
// (BC-2.02.001), and `config validate` prints one plain line per error (E-VAL-001,
// BC-2.03.001) — a single *Error cannot carry either. Warnings (unknown HYLO_*
// settings) come back ordered ahead of the errors; the CALLER (Main, `config
// validate`) prints them BEFORE any load error on stderr, exit status untouched —
// "warning first, then load error" (BC-2.01.001 PC-6/Inv-3; pass-6 A08, call 9).
// LoadOptions is Load's sole injection seam (AD-10): EnvVars carries the
// environment implementation — platform.EnvVars, `Lookup(name) (string, bool)`
// plus `Names()` (ARCH-01); the Windows NT case-insensitive `HYLO_*` matcher is
// a platform IMPLEMENTATION of that same interface, injected here, never a call
// around it (ADV-P2-A02) — so tests fake env behavior on every OS through this
// one field. FileLayer is the reserved P4 extension point (DI-010 full order
// file -> env -> default; OD-107); nil in P1.
type LoadOptions struct {
    EnvVars   platform.EnvVars  // the injected environment seam (AD-10, ARCH-01)
    FileLayer *FileLayerOptions // nil in P1; P4 file layer (OD-107, DI-010)
}
func Load(opts LoadOptions) (*Config, []Warning, *ErrorSet) // P1: env -> defaults
func EnvName(key string) string                  // OD-01, collision-tested
type Warning struct{ Key, EnvName string } // unknown-setting warning (BC-2.01.001 PC-6)
type Error struct{ Key, Value, Reason, EnvName string }
type ErrorSet struct{ Errors []Error } // registry-ordered
func (es *ErrorSet) First() *Error     // highest-precedence error, first in registry order (nil-safe)
func (e *Error) StatusLine() string    // "hylo: config error: <key>=<value> (<reason>)"
```

Backends: exactly one entry validated until P6 — zero or >1 entries are the backends
config error `exactly one backend entry until P6` (OD-123, BC-2.01.002). Reachability in
P1 (ADV-P1-A21): index 0 is always present through its defaults (PC-1), so the
**zero-entries half is unreachable** — the environment can amend or add entries but never
remove the default one; it is exercised at the validator's unit level only. The
**>1-entries half is reachable and covered**: a `HYLO_BACKENDS_<i>_<FIELD>` with
`<i>` ≠ `0` and a known P1 backend field defines an additional entry and trips the
cardinality error (PC-4, BC-2.03.001 EC-005); a `_FIELD` that is not a P1 key never
parses a value but STILL establishes the index's presence for the cardinality count —
the two effects are independent and both apply (BC-2.01.002 PC-4, ADV-P2-D10
disposition): for `HYLO_BACKENDS_1_NAME=x` the outcome is the unknown-setting warning
for `NAME` FOLLOWED BY the fatal load error `backends=2 (exactly one backend entry
until P6)` with `[from HYLO_BACKENDS_1_NAME]` — warning first, then the load error,
whose position in the error list follows registry field order. The status
line's metrics URL and prefixes live at `backends[0].metrics_url` /
`backends[0].model_prefixes`. `statusline.window_age.process_name` default `claude`
(OD-133); `statusline.theme.*` SGR keys validated as SGR parameter lists (OD-113/OD-134).
Skeleton obligations for later phases: `LoadOptions.FileLayer` extension point (P4),
`backends[]` cardinality check isolates to one validator function (P6 widens it).

## Fragment anchors (pass-4 A01; stable targets for BC-body fragment links)

BC bodies link fragments like `architecture/ARCH-02-configuration.md#registry`; the
twelve anchors below are the complete, closed set for this section — new BC fragment
links must target one of these.

<a id="registry"></a>
<a id="types"></a>
<a id="load"></a>
<a id="backends"></a>
<a id="errors"></a>
<a id="seconds"></a>
<a id="numbers"></a>
<a id="enum"></a>
<a id="url"></a>
<a id="classes"></a>
<a id="theme"></a>
<a id="text"></a>

| Anchor | Target |
|---|---|
| `#registry` | the "Key registry" section (D15, OD-114, BC-2.01.004) |
| `#types` | the per-type grammars in `types.go` (typed bool, comma lists, `~` expansion, `COLUMNS` exclusion) in the Key registry section |
| `#load` | `Load` in the Interfaces block (full ordered error list, ADV-P2-A01) |
| `#backends` | the "Backends" paragraph (exactly-one-entry cardinality, OD-123) |
| `#errors` | the D4-EX-3 config-error line decision (first error in registry order on stdout, full list + `[from <ENVNAME>]` on stderr, no cache writes) |
| `#seconds` | the Seconds grammar class (BC-2.02.002) inside the closed seven-class register |
| `#numbers` | the number-grammar/number-range classes (BC-2.02.002/.003) |
| `#enum` | the enum class (BC-2.02.004) |
| `#url` | the URL class (BC-2.02.005) |
| `#classes` | the boolean class and the closed seven-class register as a whole (BC-2.02.006; theme/SGR validation per OD-113/OD-134) |
| `#theme` | `statusline.theme.*` SGR key validation (OD-113/OD-134) in the Backends paragraph |
| `#text` | the Text class (BC-2.01.005, OD-178) — composite-shape, pill-label, glyph and empty-text errors from registry-declared keys, exact reason strings in the taxonomy vocabulary. Text keys have no legacy analog, so `TestD4EX3_Text` is a Go table test only, not a parity exclusion entry (pass-6 A01, call 1) |

## Mapping

BC-2.01.001..005 -> registry/types/load; BC-2.02.001..006 -> errors.go classes;
BC-2.03.001/.002 -> cmd/hylo consuming these errors (ARCH-01). Criticality HIGH (>= 90%
kill rate — the Phase 6 mutation target, not a P1 gate; OD-158).
