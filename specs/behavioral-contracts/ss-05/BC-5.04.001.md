---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "65d04ee"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "BC-SL-069"
parity_class: byte-exact
confidence: M
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z ADV-P3 remediation D13: POSIX-only ValueError claim qualified (Windows MSVC localtime_s raises OSError); range-end oracle rows restricted to Linux/macOS"
  - "2026-11-18T22:00:00Z (1.2.2) 2026-11-18: ADV-P4 remediation D21 - Env.Loc routed through internal/platform.LocalZone (OD-171); phantom HYLO_TEST_* zone citation replaced by TZ=UTC harness pin"
  - "2026-11-18T23:55:00Z (1.2.3) ADV-P5 remediation D01 — Windows MSVC localtime_s OSError (naive wall time on/before 1970-01-01 or from year 3001) now reproduces legacy: it propagates and DEGRADES the line (SL:984 catches ValueError only); rule in internal/platform with a table test; no exclusion id"
  - "2026-11-19T04:00:00Z (1.2.4) ADV-P6 remediation D06 + D10 / orchestrator call 2 — signatures carry the third outcome in pure pyfmt: FromISOFormat(s, loc, msvcDomain bool) (float64, error) with sentinels ErrValue (None) and ErrLocaltimeDomain (caller degrades); LocalToUnix(fields, loc, msvcDomain bool) (int64, error); statusline injects msvcDomain = platform.IsWindows(), no platform import (AD-02); Pre-2 TZ reading aligned to OD-177 (empty or unparseable TZ → UTC; unset → OS-zone fallback)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.04.001: FromISOFormat: 3.11 grammar, naive = local, fraction truncation beyond µs

## Description

Transcript timestamps feed the last-turn rate machine through `_iso_ts(s)` =
`datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()`, with `ValueError` → None and non-str → None
(SL:977-985). `pyfmt.FromISOFormat(s, loc, msvcDomain bool) (float64, error)` reproduces this composition exactly
under CPython 3.11
(3.10 rejects most of these forms): the accepted grammar, local-time reading of naive values through
`LocalToUnix` (BC-5.04.002), truncation of fractions beyond microseconds, and the float arithmetic of `timestamp()`.
Its `error` result carries the three caller outcomes (ADV-P6-D06, orchestrator call 2): nil = a value,
`ErrValue` = None (parse failure, non-str, whitespace), `ErrLocaltimeDomain` = the Windows MSVC
domain failure, which the CALLER degrades on — `LocalToUnix(fields, loc, msvcDomain bool) (int64, error)`
returns that distinct sentinel when `msvcDomain` is set and the instant lies outside MSVC's
[1970-01-01, year 3001) domain. The flag is injected — statusline passes
`msvcDomain = platform.IsWindows()` — so the rule stays in pure pyfmt with no platform
import (AD-02).

## Preconditions

1. `s` is the Value at the transcript's `timestamp` field; a non-string Value returns `(0, false)` (None) without
   parsing (SL:979-980).
2. `loc` is the injected `*time.Location` (`Env.Loc`), derived exclusively through
   `internal/platform.LocalZone` (BC-3.01.001 PC-6, OD-171): `TZ` is honored on every OS
   (named zone → that zone; empty or unparseable `TZ` → UTC, OD-177; unset `TZ` →
   OS-zone fallback), in production and in the parity harness alike — the
   harness pins `TZ=UTC` for both binaries; no `HYLO_TEST_*` zone variable exists or is
   reserved (ADV-P4-D21).

## Postconditions

1. **Z replacement:** every `Z` in `s` is replaced by `+00:00` before parsing (so `…ZZ` becomes two offsets → None).
2. **Date forms:** `YYYY-MM-DD`, `YYYYMMDD`, `YYYY-Www`, `YYYYWww`, `YYYY-Www-D`, `YYYYWwwD` (ISO week dates).
   Ordinal dates (`2026-317`) and single-digit fields (`2026-1-13`) → None. Invalid calendar dates (`2026-02-29`) → None.
3. **Separator:** any single character between date and time (`T`, `t`, space, `X`, even an emoji) is accepted.
4. **Time forms:** `HH`, `HH:MM`, `HH:MM:SS`, `HHMM`, `HHMMSS`, each with an optional fraction after `.` or `,` of any
   length (including empty: `…:04.Z` is accepted). Digits beyond the 6th are **truncated**, not rounded
   (`.123456789` → 123456 µs). Hour 24 → None; single-digit seconds (`20:18:4`) → None.
5. **Offset:** `+HH`, `+HHMM`, `+HH:MM`, `+HH:MM:SS[.ffffff]` (and `-`); `-00:00` accepted; an offset of 24 h or more
   → None.
6. **Result:** aware value → `(total microseconds since the epoch) / 1e6` as one correctly rounded division; naive
   value → `float64(LocalToUnix(fields, loc, msvcDomain)) + float64(µs) / 1e6` (CPython C `datetime_timestamp`
   arithmetic).
   Leading/trailing whitespace → None. POSIX (`msvcDomain = false`): any failure is `ValueError` →
   `(0, ErrValue)` (P3r8 R-3). **Windows
   (ADV-P5-D01, owner call 8; signatures ADV-P6-D06 / orchestrator call 2):** with
   `msvcDomain = platform.IsWindows()` the naive conversion goes through MSVC `localtime_s`, whose range
   starts at
   1970-01-01 and ends in year 3001; outside it MSVC raises `OSError` (CPython's fold-0 `u1-86400` probe hits
   it for any naive wall time on or before 1970-01-01 or at or after year 3001). Legacy's `_iso_ts` catches
   `ValueError` only (SL:984), so the `OSError` propagates out of `_mix_counts` (SL:1069) to the top-level
   guard and the whole line **degrades** — hylo reproduces this exactly: `LocalToUnix` returns the
   distinct `ErrLocaltimeDomain` sentinel in pure pyfmt (no platform import; statusline injects the
   flag and degrades on that sentinel, with a table test over the
   before-1970 / in-range / from-3001 legs); it is not `ErrValue`, and no closed-set
   exclusion id covers it. The range-end oracle rows remain pinned on Linux and macOS only (ADV-P3-D13).
7. **Range ends** (Linux/macOS oracle rows only — on Windows MSVC `localtime_s` raises `OSError` and the line degrades, PC 6 / ADV-P5-D01):
   naive values whose `LocalToUnix` probes leave years 1..9999 → `ErrValue` (TZ-dependent): naive
   `0001-01-01T*` → `ErrValue` in every zone; naive `9999-12-31T23:59:59` → float under UTC but `ErrValue` under UTC+14.

## Invariants

1. Go `time.Parse(time.RFC3339…)` and `time.ParseInLocation` are never used (grammar and DST resolution differ,
   PR-14); the parser is hand-written and fuzzed against the oracle (design IM-13, §2.6).
2. The result is `float64`; the renderer formats it as Python does where it reaches output (BC-1.03.010).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `2026-11-13T20:18:04ZZ` | None |
| EC-002 | `2026-11-13T24:00:00` | None |
| EC-003 | ` 2026-11-13T20:18:04Z` (leading space) | None |
| EC-004 | `2026-11-13T20:18:04.1234567890Z` | `1794601084.123456` |
| EC-005 | `2026-11-13T20:18:04,5Z` | `1794601084.5` |
| EC-006 | `2026-11-13T20:18:04+05:30:15.5` | `1794581268.5` |
| EC-007 | naive `0001-01-01T23:59:59` (UTC) / `0001-01-02T00:00:00` (UTC) | None / `-62135510400.0` |
| EC-008 | naive `9999-12-31T23:59:59` under `Pacific/Kiritimati` | None |
| EC-009 | naive `2026-03-08T02:30:00` (Chicago gap) | `1772958600.0` (= 03:30 CDT, BC-5.04.002) |
| EC-010 | `5` (number) / `null` | None |

## Canonical Test Vectors

| Input (`TZ`) | Expected Output | Category |
|-------|----------------|----------|
| `2026-11-13T20:18:04.123Z` (any) | `1794601084.123` | happy-path |
| `2026-11-13 20:18:04Z`; `20261113T201804Z`; `2026-11-13t20:18:04Z` (any) | `1794601084.0` each | happy-path |
| `2026-W46-5T20:18Z` (any) | `1794601080.0` | edge-case |
| `2026-11-13` (UTC / America/Chicago / Pacific/Kiritimati) | `1794528000.0` / `1794549600.0` / `1794477600.0` | edge-case |
| naive `2026-11-13T20:18:04` (UTC / America/Chicago) | `1794601084.0` / `1794622684.0` | edge-case |
| naive `9999-12-31T23:59:59` (UTC / America/Chicago) | `253402300799.0` / `253402322399.0` | edge-case |
| `2026-317`; `2026-11-13T20:18:04+24:00`; `2026-02-29T00:00:00Z` | None each | error |

All rows verified 2026-11-15 against CPython 3.11.7 running the `_iso_ts` expression under `TZ=UTC`,
`America/Chicago` and `Pacific/Kiritimati`.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-026 | `FromISOFormat` equals the oracle `_iso_ts` on fuzzed strings under the committed TZ grid | fuzz (`FromISOFormat` target) + oracle |
| VP-026 | Aware inputs are independent of `loc` | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/time.go` `FromISOFormat` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/time.go (FromISOFormat) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:_iso_ts (SL:977-985; parse at SL:983) |
| Legacy contract | BC-SL-069 (new in P3r1; amended P3r8 R-3 "TZ-dependent None near the range ends; no exception other than ValueError"; index P3r4 §7.3) |
| Decisions | OD-103, OD-104 (3.11 oracle; 3.10 grammar would differ); design IM-13; pitfall PR-14 |

## Related BCs (Recommended)

- BC-5.04.002 — depends on (naive values through `LocalToUnix`)
- BC-1.03.010, BC-1.03.016 — consumed by (last-turn rate machine)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-time` — internal/pyfmt/time.go (FromISOFormat) (ISO timestamp parsing) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt time (design step S1)

## VP Anchors (Recommended)

- VP-026 — `FromISOFormat` equals the oracle

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:977-985) |
| **Confidence** | medium (breadth of the 3.11 `fromisoformat` grammar; design §8 conf M) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if not isinstance(s, str): return None` (SL:979-980); `except ValueError: return None` (SL:984-985)
- **assertion**: pinned runs (P3r1, P3r8 R-3; re-run 2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (zone data via injected `loc`) |
| **Global state access** | none once `loc` is injected |
| **Deterministic** | yes for a fixed `loc` and tzdata |
| **Thread safety** | pure |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed -- pure with an injected location.
