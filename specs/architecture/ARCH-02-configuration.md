---
document_type: architecture-section
level: "L3"
section: "configuration"
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T23:59:00Z
phase: 1b
inputs: [prd.md, prd-supplements/interface-definitions.md, prd-supplements/error-taxonomy.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "f457392"
---

# ARCH-02 — Configuration (`internal/config`)

> Typed, registry-declared `HYLO_*` settings. P1 resolution: built-in defaults ->
> overridden by `HYLO_*` env only (OD-107); the file layer and its YAML dependency are
> reserved for P4 (DI-010 full order file -> env -> default completes then). `DGX_*` is
> never read (OD-05). Classification: **boundary** — pure registry + grammars, one
> env-reading edge (`Load`).

## Key registry (D15, OD-114, BC-2.01.004)

Every key declares `Key{Name, Type, Default, Unit, Op, Rationale, RationaleCode, Class}`
in `registry.go`; the P1 subset lives in `statusline_keys.go` (families per design doc
§2.4: telemetry, rows/layout, sparkline, git, limits, context/units/theme, timers/window
age, cost, row-2 widgets, transcript/turn/composition, glyphs, `paths.cache_dir`,
`backends[0].*`). Golden pin: `internal/config/testdata/legacy_defaults.golden`.
Env name rule (OD-01): `EnvName(key) = HYLO_` + upper snake with every `.`, `[`, `]` run
collapsed to one `_` (`backends[0].metrics_url` -> `HYLO_BACKENDS_0_METRICS_URL`);
build-time collision test; unknown `HYLO_*` warns on stderr and never changes exit
status (BC-2.01.001). Grammar per type in `types.go`: typed bool
`true|false|1|0|yes|no` (OD-05), comma lists (OD-74), `~` expansion in paths (OD-61,
`~user` left as written), `COLUMNS` excluded as protocol input (BC-1.01.005, BC-2.01.005).
Per-OS env/path behavior (P18, ADV-P1-D21) is build-tag confined in `internal/platform`
and consumed by `config`: `platform.HomeDir()` backs `~` expansion (on Windows `~` and
`~\` expand against `USERPROFILE`, BC-2.01.005), `platform.EnvLookup(name)` honors
NT case-insensitivity when matching `HYLO_*` names, and the `paths.*` **defaults are
owned by `internal/platform`** (`CacheDir()`/`StateDir()`/`ConfigDir()`, OD-95/OD-101/OD-144;
ADV-P1-A16) — the registry stores the resolver, not a literal. The cfg→plat edge is
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
  error set closable at six classes (number-range, number-grammar, enum, URL, boolean,
  theme/SGR — OD-114/OD-134/OD-140). The register being closed, a seventh class needs an
  owner decision.
- **Consequences:** every threshold row of P4r7 §B.2.1 becomes a registry entry; two
  documented default exceptions to "defaults equal legacy": `paths.cache_dir` (OD-101)
  and `backends[0].model_prefixes` = `claude-sonnet` (OD-111/OD-123).
- **Verification feasibility:** grammars and ordering are pure — **provable** by
  oracle-pinned class tables (BC-2.02.002..006) plus a registry-order property test
  (first-error selection is order-stable); env reading is testable-only (one thin edge).

## Interfaces

```go
type Config struct{ Statusline Statusline; Cost Cost; Paths Paths; Backends []Backend }
func Load(opts LoadOptions) (*Config, *Error) // P1: env -> defaults; *Error carries Key, Value, Reason, EnvName
func EnvName(key string) string               // OD-01, collision-tested
type Error struct{ Key, Value, Reason, EnvName string }
func (e *Error) StatusLine() string // "hylo: config error: <key>=<value> (<reason>)"
```

Backends: exactly one entry validated until P6 — zero or >1 entries are the backends
config error `exactly one backend entry until P6` (OD-123, BC-2.01.002). Reachability in
P1 (ADV-P1-A21): index 0 is always present through its defaults (PC-1), so the
**zero-entries half is unreachable** — the environment can amend or add entries but never
remove the default one; it is exercised at the validator's unit level only. The
**>1-entries half is reachable and covered**: any `HYLO_BACKENDS_<i>_<FIELD>` with
`<i>` ≠ `0` (any field name) defines an additional entry and trips the error
(PC-4, BC-2.03.001 EC-005); a `_FIELD` that is not a P1 key instead warns as an unknown
setting for every index, `0` included. The status
line's metrics URL and prefixes live at `backends[0].metrics_url` /
`backends[0].model_prefixes`. `statusline.window_age.process_name` default `claude`
(OD-133); `statusline.theme.*` SGR keys validated as SGR parameter lists (OD-113/OD-134).
(OD-133); `statusline.theme.*` SGR keys validated as SGR parameter lists (OD-113/OD-134).
Skeleton obligations for later phases: `LoadOptions.FileLayer` extension point (P4),
`backends[]` cardinality check isolates to one validator function (P6 widens it).

## Mapping

BC-2.01.001..005 -> registry/types/load; BC-2.02.001..006 -> errors.go classes;
BC-2.03.001/.002 -> cmd/hylo consuming these errors (ARCH-01). Criticality HIGH (>= 90%).
