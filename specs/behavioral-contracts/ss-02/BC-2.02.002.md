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
  - ../owner-decisions-log-2026-11-14.md
  - ../../semport/hylo-legacy/statusline-target-design.md
  - ../../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - ../../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; legacy-accepted TTL values at legacy/dgx_statusline.py SL:74, SL:324)"
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

# Behavioral Contract BC-2.02.002: Number-range class: non-finite/negative durations are config errors; TTL 0 stays valid

## Description

After a duration value parses (grammar: BC-2.02.003), its numeric range is checked: NaN,
+Inf and -Inf are config errors, negative values are config errors, values above the Go
`time.Duration` ceiling are config errors, and `0` stays valid for
`statusline.telemetry.ttl_s` (OD-114: "always fetch"). Legacy gave these values defined
behavior (`nan` fetch every refresh, `inf` never fetch, negative always fetch); hylo renders
the config-error line instead — approved deviation **D4-EX-3** (number class).

## Preconditions

1. A registry key of type `Seconds` (name ends `_s`) whose `EnvName` is present and whose
   value passed the number grammar (Python `float()` grammar minus underscores and non-ASCII
   digits, BC-2.02.003).

## Postconditions

Checks run in this order; the first failing one produces the error, rendered per
BC-2.02.001:

1. Value is NaN, +Inf or -Inf (spelled `nan`, `inf`, `infinity`, any case and sign Python
   accepts, or a literal that overflows to infinity such as `1e400`) →
   `<key>=<value> (not finite)`.
2. Value < 0 → `<key>=<value> (negative)`. `-0`, `-0.0` and underflow to -0.0 (e.g.
   `-1e-400`) are **not** negative (−0.0 < 0 is false) and are treated as 0.
3. Value > 9223372036.854775 (the largest seconds value a `time.Duration` holds; PR-22) →
   `<key>=<value> (out of range)`.
4. Value == 0 and the key's registry range is `> 0` → `<key>=<value> (must be > 0)`.
   `statusline.telemetry.ttl_s` has range `>= 0` (OD-114), so `0` is valid and keeps the
   legacy meaning: `fetch_ts > now − 0` is false for any non-future `fetch_ts`, i.e. fetch
   on every refresh (SL:324). Other `Seconds` keys default to range `> 0` (design IM-16)
   unless their registry entry states `>= 0` with a rationale.
5. Otherwise the value is accepted as a float64 seconds value; no rounding is applied at
   load time.

## Invariants

1. A loaded `Seconds` value is always finite, `>= 0` and `<= 9223372036.854775`, so a
   float→Duration conversion is well-defined on every architecture (PR-22: arm64 saturates,
   amd64 yields MinInt64 for NaN/out-of-range).
2. Of the P1 `Seconds` keys only `statusline.telemetry.ttl_s` was settable in legacy (via
   `DGX_SL_TTL`), so it is the only key whose range errors are parity deviations; for the
   other keys the range is a hylo-only validation with no legacy counterpart.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=0` | valid; fetch every refresh (legacy-identical) |
| EC-002 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=-0` | valid; treated as 0 |
| EC-003 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=-inf` | `not finite` (check 1 precedes check 2) |
| EC-004 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=1e400` | `not finite` |
| EC-005 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=9223372036.854775` | valid |
| EC-006 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=9223372037` | `out of range` |
| EC-007 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=" 4 "` | valid, 4 (Python grammar keeps surrounding whitespace legal; not an OD-114 error) |
| EC-008 | `HYLO_STATUSLINE_TELEMETRY_TIMEOUT_S=0` | `must be > 0` (range `> 0`) |
| EC-009 | `HYLO_STATUSLINE_TELEMETRY_TTL_S=1e1` | valid, 10 |

## Canonical Test Vectors

`\e` = 0x1B. All rows: exit 0, no cache writes (BC-2.02.001).

| Input | Expected Output | Category |
|-------|----------------|----------|
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=0` | normal render; metrics fetched on this run | happy-path |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=nan` | `\e[90mhylo: config error: statusline.telemetry.ttl_s=nan (not finite)\e[0m\n` | error |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=inf` | `\e[90mhylo: config error: statusline.telemetry.ttl_s=inf (not finite)\e[0m\n` | error |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=-1` | `\e[90mhylo: config error: statusline.telemetry.ttl_s=-1 (negative)\e[0m\n` | error |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=-0.0` | normal render (0) | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | Every accepted Seconds value v satisfies `!IsNaN(v) && !IsInf(v,0) && v >= 0 && v <= 9223372036.854775` | proptest / fuzz on the parser |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-114 (T10: TTL `nan`/`inf`/negative are config errors; TTL `0` stays valid), OD-102; legacy behavior replaced: legacy/dgx_statusline.py:module tunables (SL:74 `TTL = float(...)`) and get_sample (SL:324 `fetch_ts > now - TTL`); legacy contract notes BC-SL-087 (pass-3 r1, r2 §A5) |
| Parity / exclusion | **Approved deviation D4-EX-3 (number class).** Named exclusion entry id `D4-EX-3` in `internal/statusline/testdata/parity/exclusions.json`, one case per value (`nan`, `inf`, `-inf`, `-1`), each with its expected output file; dedicated table test `TestConfigError_D4EX3_Number` (OD-105, OD-110) |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-008, DI-010 |
| Architecture Module | `internal/config/types.go` (`Seconds`) (filled by architect) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.02.003 — depends on (grammar runs first)
- BC-2.02.001 — composes with (line format)
- BC-2.01.004 — depends on (per-key Range)
- BC-1.04.020 — related to (get_sample TTL semantics)

## Architecture Anchors (Recommended)

- `architecture/SS-02-configuration.md#seconds` — Seconds type (TBD)

## Story Anchor (Recommended)

S-TBD — D4-EX-3 table tests

## VP Anchors (Recommended)

- VP-TBD — loaded Seconds always finite and in range
