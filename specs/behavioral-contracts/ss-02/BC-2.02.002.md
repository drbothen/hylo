---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-19T17:30:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "ad596a8"
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
modified:
  - "1.2.1 2026-11-18: ADV-P4 remediation A03 — per-key exception: statusline.git.ttl_s admits any finite value, negative = never fresh (legacy SL:409); TestD4EX3_Name rename (D22)"
  - "1.2.2 2026-11-18T22:00:00Z: pass-4 correction (item 10) — exclusions.json path restored to the OD-148 home internal/statusline/testdata/parity/exclusions.json"
  - "2026-11-19T00:50:00Z (1.2.3) ADV-P5 remediation D11 (A14 sibling) — git.ttl_s bounded by the mirrored Duration floor -9223372036.854775 (values below yield out of range), Inv 1 restated to the symmetric span, VP property row corrected to the per-key exception, EC-011 added"
  - "2026-11-19T17:30:00Z (1.2.4): ADV-P7 remediation D11 — H1 admits the git.ttl_s negative exception (postcondition PC-2 already did); BC-INDEX and PRD title columns synced"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-2.02.002: Number-range class: non-finite/negative durations are config errors, except the git.ttl_s negative exception; TTL 0 stays valid

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
2. Value < 0 → `<key>=<value> (negative)`. **Per-key exception (ADV-P4-A03, bounded per
   ADV-P5-D11):** `statusline.git.ttl_s` admits any finite value in
   `[-9223372036.854775, 9223372036.854775]` — negatives included (registry range
   "finite, bounded by the Duration conversion"): legacy's gate `now - ts > GIT_TTL`
   (SL:409, tunable SL:99) admits them
   unvalidated, and a negative TTL makes the gate true for every cached sample, i.e. the
   git cache is **never fresh** (re-read `.git/HEAD` on every render) — legacy-identical
   observable behavior, so no D4-EX-3 entry arises. For this key check 2 is skipped and
   check 3's ceiling is mirrored by the floor: a value below `-9223372036.854775`
   (e.g. `-1e300`) yields `<key>=<value> (out of range)`, so Inv 1's "conversion
   well-defined" holds for the exception too. `-0`, `-0.0` and underflow to -0.0 (e.g.
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

1. A loaded `Seconds` value is always finite and within
   `[-9223372036.854775, 9223372036.854775]`, so a float→Duration conversion is
   well-defined on every architecture (PR-22: arm64 saturates, amd64 yields MinInt64 for
   NaN/out-of-range); it is `>= 0` for every key except `statusline.git.ttl_s`, whose
   per-key exception admits negative values down to the mirrored Duration floor (PC-2,
   ADV-P4-A03; the floor added by ADV-P5-D11).
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
| EC-010 | `HYLO_STATUSLINE_GIT_TTL_S=-5` | valid for `statusline.git.ttl_s` (per-key exception); git cache never fresh — legacy-identical (ADV-P4-A03) |
| EC-011 | `HYLO_STATUSLINE_GIT_TTL_S=-1e300` | `out of range` (below the mirrored Duration floor; the conversion stays well-defined, ADV-P5-D11) |

## Canonical Test Vectors

`\e` = 0x1B. All rows: exit 0, no cache writes (BC-2.02.001).

| Input | Expected Output | Category |
|-------|----------------|----------|
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=0` | normal render; metrics fetched on this run | happy-path |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=nan` | `\e[90mhylo: config error: statusline.telemetry.ttl_s=nan (not finite)\e[0m\n` | error |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=inf` | `\e[90mhylo: config error: statusline.telemetry.ttl_s=inf (not finite)\e[0m\n` | error |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=-1` | `\e[90mhylo: config error: statusline.telemetry.ttl_s=-1 (negative)\e[0m\n` | error |
| `HYLO_STATUSLINE_TELEMETRY_TTL_S=-0.0` | normal render (0) | edge-case |
| `HYLO_STATUSLINE_GIT_TTL_S=-5` | normal render; git cache never fresh (per-key exception, ADV-P4-A03) | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-016, VP-012 (frontmatter closure) | Every accepted Seconds value v satisfies `!IsNaN(v) && !IsInf(v,0) && v <= 9223372036.854775`, and `v >= 0` for every key except `statusline.git.ttl_s`, for which `v >= -9223372036.854775` (ADV-P5-D11) | Go property test (testing/quick) / fuzz on the parser |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-114 (T10: TTL `nan`/`inf`/negative are config errors; TTL `0` stays valid), OD-102; legacy behavior replaced: legacy/dgx_statusline.py:module tunables (SL:74 `TTL = float(...)`) and get_sample (SL:324 `fetch_ts > now - TTL`); per-key negative exception for `statusline.git.ttl_s` per the git freshness gate (SL:409, tunable SL:99; ADV-P4-A03); legacy contract notes BC-SL-087 (pass-3 r1, r2 §A5) |
| Parity / exclusion | **Approved deviation D4-EX-3 (number class).** Named exclusion entry id `D4-EX-3` in `internal/statusline/testdata/parity/exclusions.json`, one case per value (`nan`, `inf`, `-inf`, `-1`), each with its expected output file; dedicated table test `TestD4EX3_Number` (OD-105, OD-110) |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-008, DI-010 |
| Architecture Module | `internal/config/types.go` (`Seconds`) (BC-COMPONENT-MAP: internal/config/errors.go (number-range class) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.02.003 — depends on (grammar runs first)
- BC-2.02.001 — composes with (line format)
- BC-2.01.004 — depends on (per-key Range)
- BC-1.04.020 — related to (get_sample TTL semantics)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#seconds` — internal/config/errors.go (number-range class) (Seconds type) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — D4-EX-3 table tests

## VP Anchors (Recommended)

- VP-016, VP-012 — loaded Seconds always finite and in range

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | safe for concurrent use (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/errors.go (number-range class) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
