---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T11:45:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "720fc73"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; legacy fallback at legacy/dgx_statusline.py SL:89, SL:644, SL:662)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
parity_class: D4-EX-3
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

# Behavioral Contract BC-2.02.004: Enum class: unknown sparkline trace value is a config error

## Description

`statusline.sparkline.trace` is an enum with exactly three values, `rate`, `kv`, `ttft`
(legacy `TRACE_KEYS`, SL:644). Any other value — including the retired `mine`, case
variants and whitespace-padded forms — is a config error. Legacy silently fell back to `rate`
(`TRACE_KEYS.get(TRACE, "v")`, SL:662); hylo renders the config-error line — approved
deviation **D4-EX-3** (enum class).

## Preconditions

1. `HYLO_STATUSLINE_SPARKLINE_TRACE` is present (BC-2.01.001). Absent → default `rate`
   (legacy SL:89).

## Postconditions

1. The value is compared byte-exact, case-sensitive, untrimmed against `rate`, `kv`, `ttft`.
   A match selects that trace (history field `v`, `k`, `f` respectively, SL:644).
2. No match → `statusline.sparkline.trace=<value> (unknown value (rate|kv|ttft))`, rendered
   per BC-2.02.001. The allowed list in the reason is in registry-declared order
   `rate|kv|ttft`.
3. The general enum rule for any future enum key is the same: reason
   `unknown value (<v1>|<v2>|...)` listing the allowed values in registry order.

## Invariants

1. A loaded config always holds one of the three trace values; the renderer's
   `TRACE_KEYS.get(..., "v")` fallback branch is unreachable in hylo (kept only as a
   defensive default equal to `rate`).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `mine` (retired 2026-11-13, SL:642-643) | error |
| EC-002 | `Rate` | error (case-sensitive) |
| EC-003 | ` kv` (leading space) | error; value shown as ` kv` |
| EC-004 | `""` (present, empty) | `statusline.sparkline.trace= (unknown value (rate\|kv\|ttft))` |
| EC-005 | `ttft` | valid |
| EC-006 | trace valid but `HYLO_STATUSLINE_SPARKLINE_ENABLED=0` | valid; trace unused |

## Canonical Test Vectors

`\e` = 0x1B. Error rows: exit 0, no cache writes.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `HYLO_STATUSLINE_SPARKLINE_TRACE=kv` | sparkline plots the `k` history field | happy-path |
| `HYLO_STATUSLINE_SPARKLINE_TRACE=mine` | `\e[90mhylo: config error: statusline.sparkline.trace=mine (unknown value (rate\|kv\|ttft))\e[0m\n` | error |
| `HYLO_STATUSLINE_SPARKLINE_TRACE=RATE` | `\e[90mhylo: config error: statusline.sparkline.trace=RATE (unknown value (rate\|kv\|ttft))\e[0m\n` | edge-case |

(In the table `\|` is a literal `|`.)

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-016, VP-012 (frontmatter closure) | Trace parse accepts exactly the three strings | table test + fuzz |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-114 (T10: unknown TRACE values are config errors), OD-102; legacy behavior replaced: legacy/dgx_statusline.py:module tunables (SL:89 `TRACE = os.environ.get("DGX_SL_TRACE", "rate")`), `TRACE_KEYS` (SL:644), sparkline (SL:662 `TRACE_KEYS.get(TRACE, "v")`) |
| Parity / exclusion | **Approved deviation D4-EX-3 (enum class).** Named exclusion entry id `D4-EX-3`, cases `mine`, `Rate`, ` kv`, `""`, each with its expected output file; dedicated table test `TestD4EX3_Enum` (OD-105, OD-110) |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-008, DI-010 |
| Architecture Module | `internal/config/types.go` (`Enum`) (BC-COMPONENT-MAP: internal/config/errors.go (enum class) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.02.001 — composes with (line format)
- BC-1.04.009 — consumer (sparkline trace selection)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#enum` — internal/config/errors.go (enum class) (enum type) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — D4-EX-3 table tests

## VP Anchors (Recommended)

- VP-016, VP-012 — trace enum exact

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | safe for concurrent use (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/errors.go (enum class) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
