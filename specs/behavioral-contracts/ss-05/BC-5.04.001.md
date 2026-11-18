---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "c3fc33e"
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
(SL:977-985). `pyfmt.FromISOFormat(s, loc) (float64, bool)` reproduces this composition exactly under CPython 3.11
(3.10 rejects most of these forms): the accepted grammar, local-time reading of naive values through
`LocalToUnix` (BC-5.04.002), truncation of fractions beyond microseconds, and the float arithmetic of `timestamp()`.

## Preconditions

1. `s` is the Value at the transcript's `timestamp` field; a non-string Value returns `(0, false)` (None) without
   parsing (SL:979-980).
2. `loc` is the injected `*time.Location` (`Env.Loc`; production `time.Local`, harness `HYLO_TEST_*`-controlled zone).

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
   value → `float64(LocalToUnix(loc, wall seconds)) + float64(µs) / 1e6` (CPython C `datetime_timestamp` arithmetic).
   Leading/trailing whitespace → None. Any failure → `(0, false)`; no other error kind escapes on POSIX (P3r8 R-3:
   only `ValueError` occurs there). On Windows the underlying naive conversion goes through MSVC `localtime_s`,
   which raises `OSError` (not `ValueError`) outside the representable range — the helper maps every failure kind
   to `(0, false)` all the same; the range-end oracle rows are pinned on Linux and macOS only (ADV-P3-D13).
7. **Range ends** (Linux/macOS oracle rows only — on Windows MSVC `localtime_s` raises `OSError`, ADV-P3-D13):
   naive values whose `LocalToUnix` probes leave years 1..9999 → None (TZ-dependent): naive
   `0001-01-01T*` → None in every zone; naive `9999-12-31T23:59:59` → float under UTC but None under UTC+14.

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
