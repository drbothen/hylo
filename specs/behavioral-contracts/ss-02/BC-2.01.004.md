---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "d4063b6"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; key defaults trace to legacy/dgx_statusline.py SL:73-137 via the P4r7 B.2.1 threshold register)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-2.01.004: Key registry: every key declares type, range/operator, default and rationale

## Description

`internal/config` exposes one registry, `Registry() []Key`, that is the single source for
every behavior-shaping value in P1 (D15 iron rule). Every entry declares its name, type,
range, the comparison operator legacy uses for it, its default, its unit, and a rationale
with a rationale code (OD-57, OD-114). A build-time test suite rejects any entry that is
incomplete, whose default fails its own validation, or whose env name collides.

## Preconditions

1. The P1 key subset is the one listed in design §2.4 (from the P4r7 §B.2.1 register,
   rationales resolved by OD-57), as amended by OD-113 (theme keys, BC-2.01.003) and OD-123
   (backend keys, BC-2.01.002).

## Postconditions

1. Each `Key` has the fields `Name, Type, Default, Unit, Range, Op, Rationale,
   RationaleCode, Class`:
   - `Name`: dotted lower-snake, matching
     `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*|\[[0-9]+\])*$` (CV-19).
   - `Type`: one of `Seconds, Int, Float, Bool, Enum, URL, List, Path, SGR, Text`.
   - `Range`: the valid domain stated explicitly (e.g. ttl_s: finite, `>= 0`,
     `<= 9223372036.854775`; trace: `rate|kv|ttft`).
   - `Op`: the comparison exactly as legacy writes it (e.g. ttl_s: `fetch_ts > now − ttl`,
     strict; narrow_cols: `cols >= narrow_cols` keeps row 2), or `n.a.` for non-threshold
     keys (URLs, colors, paths).
   - `Rationale`: non-empty prose, the same text that the code comment next to the default
     carries (D15, CLAUDE.md "explain every threshold").
   - `RationaleCode`: one of `M` (measured), `DOC` (written in source or docs), `J` (labeled
     judgment call), `C` (convention or tool default), `Dv`, `Dv†` (derived), `OWNER-<x>`,
     `EXT` (Claude Code constant) — the P4r7 legend.
   - `Class`: `CFG` (config key). Named constants (NC) are not registry entries; each lives in
     code with a "why not config" comment.
2. `EnvName(key)` = `HYLO_` + the key upper-cased with every `.`, `[` and `]` run replaced
   by a single `_` and no trailing `_` (e.g. `statusline.telemetry.ttl_s` →
   `HYLO_STATUSLINE_TELEMETRY_TTL_S`; `backends[0].metrics_url` →
   `HYLO_BACKENDS_0_METRICS_URL`) (OD-01, OD-74).
3. Build-time table tests over `Registry()` fail the build when any of these hold:
   (a) a required field is empty; (b) `RationaleCode` is outside the legend;
   (c) the default does not pass the key's own type + range validation; (d) two keys share an
   `EnvName`, or an `EnvName` equals a reserved name (`HYLO_CONFIG`, `HYLO_TEST_NOW`,
   `HYLO_PARITY_PYTHON`) or `COLUMNS`; (e) a name ending in `_s` is not type `Seconds`, or
   `_ms` not a millisecond integer/float type; (f) a default differs from the legacy value
   recorded in the golden table `internal/config/testdata/legacy_defaults.golden` (key →
   legacy value → SL line), except the two documented exceptions in PC-4.
4. Documented default exceptions to "defaults equal legacy until cutover" (D15), each
   carrying the OD in its rationale: `paths.cache_dir` (platform cache dir, not
   `~/.cache/dgx-llm`; OD-101) and `backends[0].model_prefixes` (`claude-sonnet`, legacy
   status line default `""`; OD-111, OD-123).
5. Registry order is stable and is the order used for config-error reporting
   (BC-2.02.001).

## Invariants

1. Logic reads every behavior-shaping value from the resolved config, never a literal
   (D15); protocol/format constants (API paths, the D7 ledger schema, the 40-char sid
   truncation T-061, the sha1 prefix T-062) are named constants with comments.
2. `HYLO_TEST_NOW` is a harness hook, not a key (design §3.2, RK-5).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | A new key added without `Rationale` | build-time test fails naming the key |
| EC-002 | A key `statusline.foo_s` declared as `Int` | test (e) fails |
| EC-003 | Two keys `a.b_c` and `a_b.c` (both `HYLO_A_B_C`) | collision test fails |
| EC-004 | `statusline.telemetry.ttl_s` default changed to 5 | legacy-default golden test fails (legacy SL:74 is 4) |
| EC-005 | `paths.cache_dir` default ≠ `~/.cache/dgx-llm` | allowed: listed exception citing OD-101 |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `Registry()` entry for `statusline.telemetry.ttl_s` | `Type=Seconds, Default=4, Unit=s, Range="finite, >= 0, <= 9223372036.854775", Op="fetch_ts > now − ttl (strict)", RationaleCode=DOC, Rationale="match refreshInterval (legacy SL:50; T-001)"` | happy-path |
| `EnvName("backends[0].model_prefixes")` | `HYLO_BACKENDS_0_MODEL_PREFIXES` | edge-case |
| registry with an entry whose default `"x"` is type `Int` | build-time test failure | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-015 | `EnvName` is injective over `Registry()` | table test |
| VP-015 | Every default validates under its own type and range | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — D15 (config over code), OD-57 (rationales accepted), OD-114 (type and range per key), OD-01/OD-74 (env naming), CV-19 (operator in comment), P4r7 §B.2.1 register (79 status line rows); defaults trace to legacy/dgx_statusline.py module tunables (SL:73-100) and primitives (SL:127-137) |
| Parity / exclusion | n.a. |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-010 |
| Architecture Module | `internal/config/registry.go`, `statusline_keys.go` (BC-COMPONENT-MAP: internal/config/registry.go (key registry) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.01.001 — consumer (resolution iterates the registry)
- BC-2.01.002, BC-2.01.003 — composes with (backend and theme entries)
- BC-2.02.002..005 — composes with (range/type validation per class)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#registry` — internal/config/registry.go (key registry) (registry schema) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — config registry

## VP Anchors (Recommended)

- VP-015 — EnvName injective; defaults self-validate

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | Send + Sync (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/registry.go (key registry) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
