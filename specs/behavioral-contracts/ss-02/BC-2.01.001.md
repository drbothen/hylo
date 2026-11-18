---
document_type: behavioral-contract
level: L3
version: "1.2.3"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
  - domain-spec/invariants.md
input-hash: "d75c50e"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; replaces legacy env reads at legacy/dgx_statusline.py SL:73-77, 89, 444, 902-903)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D07+D37: all-defaults vector gains queue.false/subagent.true; reserved names extended with HYLO_TIMING_GATE and HYLO_PARITY_FUZZSECONDS"
  - "2026-11-18T12:00:00Z ADV-P4 remediation D01+D27: all-defaults vector queue.yellow corrected to true (OD-175); LOCAL_MODEL_PREFIXES second legacy read site SL:902-903 cited and BC-1.07.006 consumer listed"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-2.01.001: P1 resolution: HYLO_* env over built-in defaults; no file layer; DGX_* never read

## Description

In P1 every registry key resolves from exactly two layers: the `HYLO_*` environment variable
named `EnvName(key)` when it is present, otherwise the key's built-in default. No config file
is read in P1, even if one exists (OD-107; the file layer and its YAML dependency arrive in
P4). Legacy names (`DGX_*`, `LOCAL_MODEL_PREFIXES`) are never read (OD-05). Resolution
happens once per process, before any side effect.

## Preconditions

1. The process environment is available (on Windows env names compare case-insensitively,
   per the OS; on macOS/Linux case-sensitively).
2. The key registry (BC-2.01.004) is built; each key has an `EnvName` and a default.

## Postconditions

1. For each key `k` in registry order: if `EnvName(k)` is **present** in the environment
   (including present with an empty value), the effective value is that string parsed and
   validated by `k`'s type and range (BC-2.01.005, BC-2.02.002..005); otherwise the effective
   value is `k`'s built-in default.
2. A present-but-empty variable is "set to empty", never "unset": list keys become the empty
   list (OD-111: the parity cases for an unset prefix set an explicit empty value); number,
   boolean, enum, URL and path keys yield a config error (BC-2.02.001).
3. No config file is opened: not the per-OS default path (BC-2.03.002), not `HYLO_CONFIG`,
   not `--config`. The presence, absence or content of such a file does not change the
   result.
4. No legacy name is read. In particular `DGX_SL_VM_URL`, `DGX_SL_TTL`, `DGX_SL_ROWS`,
   `DGX_SL_SPARK`, `DGX_SL_GIT`, `DGX_SL_TRACE` (legacy SL:73-77, 89) and
   `LOCAL_MODEL_PREFIXES` (legacy reads it twice: render_lane SL:444 for the main lane pill
   and the subagent model segment SL:902-903 for the per-task lane tag, P1 since OD-155)
   have no effect whatever their value, including values that crashed legacy.
5. Resolution runs once, at startup, before stdin decode and before any cache read or write
   (design §3.1 step 0). The resolved `*Config` is immutable for the rest of the run (legacy
   read `LOCAL_MODEL_PREFIXES` at render time; hylo reads it once, which is output-identical
   within one run).
6. A present `HYLO_*` variable that names no registry key and is not a reserved name is
   ignored, with one stderr warning line `hylo: warning: unknown setting <NAME> (ignored)\n`
   (OD-01). Name matching follows OS environment-variable case semantics (ADV-P2-D17
   disposition): on Windows matching is case-insensitive (`os.Environ` keeps the original
   name's case, and Windows env names are case-insensitive), so `hylo_foo` IS recognized
   as an unknown `HYLO_*` setting and warned, with the name shown as given; on POSIX,
   matching is case-sensitive, so a lowercase `hylo_foo` is not a `HYLO_*` variable at all
   and is ignored silently. Reserved names, never warned and never config keys: `HYLO_CONFIG` (config path
   override, BC-2.03.002), `HYLO_TEST_NOW` (harness clock hook, design §3.2; a malformed
   value is ignored with one stderr warning and the real clock is used — BC-6.01.003,
   ADV-P1-D22 spec choice), `HYLO_PARITY_PYTHON` (harness interpreter setting, OD-104),
   `HYLO_TIMING_GATE` (harness timing-gate setting, BC-6.04.002) and
   `HYLO_PARITY_FUZZSECONDS` (harness fuzz-duration setting, BC-6.04.003) — the latter
   two added so inherited harness settings do not draw the unknown-setting warning and
   are collision-checked (ADV-P3-D37 / ADV-P3-A20).
7. If any key fails validation, `Load` returns every failing key (registry order) and the
   caller renders per BC-2.02.001 (statusline) or BC-2.03.001 (validate).

## Invariants

1. Precedence in P1 is env → default; the D15 order file → env → default is completed in P4
   without changing the env layer's semantics.
2. `COLUMNS` is not a configuration input (BC-2.01.005).
3. Resolution has no side effects besides reading the environment and writing warnings to
   stderr.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `DGX_SL_TTL=four` (legacy CP-X01 crash input) and no `HYLO_*` | ttl_s = 4 (default); normal render; no error, no warning |
| EC-002 | `LOCAL_MODEL_PREFIXES=claude-opus` only | `backends[0].model_prefixes` = `[claude-sonnet]` (default, OD-111) |
| EC-003 | A config file exists at the per-OS path with `rows: 1` | ignored in P1; rows = 2 |
| EC-004 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=` (present, empty) | config error `not a number` (not the default) |
| EC-005 | `HYLO_BACKENDS_0_MODEL_PREFIXES=` (present, empty) | empty prefix list; client-view lane unknown (BC-1.02.001 `◨ ?`) |
| EC-006 | `HYLO_FOO=1` | ignored; stderr warning; stdout unaffected |
| EC-007 | `HYLO_TEST_NOW=1700000000.5` | no warning; not a key (harness hook) |
| EC-008 | Windows, `hylo_statusline_rows=1` | honored as `HYLO_STATUSLINE_ROWS` (OS case-insensitivity) |
| EC-009 | Windows, `hylo_foo=1`; POSIX, `hylo_foo=1` | Windows: `hylo: warning: unknown setting hylo_foo (ignored)` (case-insensitive match, ADV-P2-D17); POSIX: no warning (not a `HYLO_*` variable) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| env `{}` | ttl_s 4, rows 2, sparkline.enabled true, sparkline.trace `rate`, git.enabled true, queue.yellow true (OD-175: default true = legacy rule, yellow when queue > 0 or preempt > 0), subagent.enabled true, `backends[0].metrics_url` `http://192.0.2.10:8428`, `backends[0].model_prefixes` `[claude-sonnet]`, `paths.cache_dir` = platform cache dir (OD-101) | happy-path |
| env `{HYLO_STATUSLINE_TELEMETRY_TTL_S: "10"}` | ttl_s 10; others default | happy-path |
| env `{DGX_SL_ROWS: "2.0", DGX_SL_TRACE: "kv"}` | rows 2, trace `rate` (legacy names ignored) | edge-case |
| env `{HYLO_STATUSLINE_ROWS: "x"}` | `Load` error `statusline.rows=x (not an integer)` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-015 | Adding or changing any non-`HYLO_*` variable (except OS-level ones read by `internal/platform` for paths) never changes the resolved config | Go property test (testing/quick) |
| VP-015 | Unset `EnvName(k)` ⇒ effective value == registry default for every k | table test over `Registry()` |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-107 (P1 config = HYLO_* env + built-in defaults; file layer P4), OD-05 (HYLO_* + config only, no DGX_* aliases), OD-01 (unknown HYLO_* warned), D15; legacy names it replaces: legacy/dgx_statusline.py:module tunables (SL:73-77, 89), render_lane (SL:444), subagent model-segment lane tag (SL:902-903, P1 since OD-155) |
| Parity / exclusion | n.a. (no output change for equal effective values; harness sets HYLO_* on the Go side and DGX_* on the legacy side, design §3.2) |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-010 |
| Architecture Module | `internal/config/load.go` (BC-COMPONENT-MAP: internal/config/load.go (env -> defaults) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.01.004 — depends on (registry, EnvName)
- BC-2.01.005 — composes with (value grammars)
- BC-2.01.002 — composes with (backends[0].* keys)
- BC-2.02.001 — composes with (error rendering)
- BC-2.03.002 — related to (config path; file not read in P1)
- BC-3.01.001 — related to (paths.cache_dir default)
- BC-1.07.006 — consumer (subagent model-segment lane tag reads model_prefixes, SL:902-903)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#load` — internal/config/load.go (env -> defaults) (resolution order) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — config subset (design §4 step S2)

## VP Anchors (Recommended)

- VP-015 — legacy names never read

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | safe for concurrent use (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/load.go (env -> defaults) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
