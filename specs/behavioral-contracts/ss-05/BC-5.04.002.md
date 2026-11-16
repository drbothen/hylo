---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/statusline-target-design.md, ../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r2.md, ../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md, ../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r4.md, ../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r5.md, owner-decisions-log-2026-11-14.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; ports CPython datetime._mktime behind naive .timestamp() at legacy/dgx_statusline.py SL:983)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
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

# Behavioral Contract BC-5.04.002: LocalToUnix: CPython _mktime port, gap/overlap semantics, TZ injection, embedded tzdata

## Description

`pyfmt.LocalToUnix(loc, wall) (int64, error)` converts a naive local wall time to Unix seconds exactly as CPython
3.11's `datetime._mktime` (fold = 0) does, including which instant it picks in a DST gap or a repeated hour. Go's
`time.Date` picks differently (in gaps when the wall read as UTC precedes the transition, in overlaps when it is at
or after it; CONV-ABS-89), so it is never used for naive values (design IM-13; pitfall PR-14).

## Preconditions

1. `wall` = (year, month, day, hour, minute, second) with year 1..9999 (microseconds are added by the caller,
   BC-5.04.001).
2. `loc` is an injected `*time.Location`; `local(u)` means the wall-clock breakdown of `time.Unix(u, 0).In(loc)`.

## Postconditions

1. Let `t` = seconds from 1970-01-01T00:00:00 to `wall`, both read as UTC, and `local(u)` = seconds from the epoch to
   the wall-clock breakdown of instant `u` in `loc`, read as UTC. The algorithm is CPython `_mktime`, fold = 0:
   - `a = local(t) - t`; `u1 = t - a`; `t1 = local(u1)`.
   - If `t1 == t`: `u2 = u1 - 86400`; `b = local(u2) - u2`; if `a == b` return `u1`. Otherwise `b = t1 - u1`.
   - `u2 = t - b`; `t2 = local(u2)`; if `t2 == t` return `u2`; if `t1 == t` return `u1`.
   - Otherwise `t` is in a gap: return `max(u1, u2)`.
2. **Repeated hour (overlap):** returns the **first** occurrence (earlier instant).
3. **Gap:** returns the instant as if the pre-transition offset still applied (the later candidate), e.g. Chicago
   `02:30` on the spring-forward day → `03:30` CDT.
4. **Range:** if any `local(u)` breakdown (including the `u1 - 86400` probe) falls outside years 1..9999, the
   function returns `ErrValue` (CPython "year N is out of range" `ValueError`), which `_iso_ts` maps to None.
5. Pure for a fixed `loc` and zone database.

## Invariants

1. `time.Date(..., loc)` and `time.ParseInLocation` are never used for naive wall times.
2. The location is always injected (`Env.Loc`), never read implicitly from `time.Local` inside the helper; Windows
   ignores `TZ`, so the harness injects the zone explicitly (research P19).
3. `time/tzdata` is embedded so a zone always loads; `time.LoadLocation` still prefers the system database, so the
   oracle (system tzdata) and Go read the same data on a given runner. Goldens are restricted to transitions that are
   identical across tzdata releases in use (labeled assumption; a tzdata mismatch shows up as a golden failure, never
   as a silent pass).
4. Committed CPython goldens: 10,893 rows across four zone grids (P5r5 §B.6), on which the port showed 0 mismatches in
   Phase 0; they include 24 h day skips (Pacific/Apia 2011, Pacific/Kiritimati 1994), non-DST offset changes and
   zero-offset fall-backs (Atlantic/Azores 2026, America/Scoresbysund 2023).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Chicago `2026-11-01 01:30:00` (repeated hour) | `1793514600` (first, CDT); fold-1 would be `1793518200` |
| EC-002 | Chicago `2026-11-01 01:59:59` | `1793516399` (first). macOS libc `mktime` returns `1793519999` here — that libc value appears only on the removed `ps` path (BC-3.02.002 D1), never in this helper |
| EC-003 | Chicago `2026-03-08 02:00:00` (gap) | `1772956800` (= 03:00 CDT); Go `time.Date` gives `1772953200` |
| EC-004 | Berlin `2026-10-25 02:30:00` (repeated hour, east of UTC) | `1792888200` (first, CEST); Go `time.Date` picks the second |
| EC-005 | Berlin `2026-03-29 02:30:00` (gap) | `1774747800` (= 03:30 CEST) |
| EC-006 | Lord_Howe `2026-04-05 01:45:00` (30-minute overlap) | `1775313900` (first) |
| EC-007 | UTC `0001-01-01 23:59:59` | `ErrValue` (the −24 h probe reaches year 0) |
| EC-008 | Kiritimati (UTC+14) `9999-12-31 23:59:59` | `ErrValue` (`local(t)` reaches year 10000) |

## Canonical Test Vectors

| Input (`loc`, wall) | Expected Output | Category |
|-------|----------------|----------|
| America/Chicago, `2026-11-13 18:10:09` | `1794615009` | happy-path |
| UTC, `2026-11-13 18:10:09` | `1794593409` | happy-path |
| Europe/Berlin, `2026-07-01 12:00:00` | `1782900000` | happy-path |
| America/Chicago, `2026-11-01 01:30:00` | `1793514600` | edge-case |
| America/Chicago, `2026-03-08 02:30:00` | `1772958600` | edge-case |
| UTC, `0001-01-02 00:00:00` | `-62135510400` | edge-case |
| UTC, `0001-01-01 00:00:00` | `ErrValue` | error |

All rows verified 2026-11-15 against CPython 3.11.7 (`datetime(...).timestamp()` for naive values, fold 0 and 1,
under the named `TZ`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | `LocalToUnix` equals the committed CPython goldens (10,893 rows, 0 mismatches) | table test |
| VP-TBD | Outside transitions, `LocalToUnix(loc, w) == time.Date(w, loc).Unix()` | proptest |
| VP-TBD | For overlap walls the result is the smaller of the two candidate instants | proptest over the grid |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/time.go` `LocalToUnix` (design §2.6) (filled by architect) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103; design IM-13 and PR-14; P5r2 §A.1 (Go vs Python DST table), P5r3 V2, P5r4 V7 (CONV-ABS-89 rule), P5r5 V1 and §B.6 (10,893 goldens, 0 mismatches). Legacy semantics reproduced: naive `.timestamp()` at SL:983 |

## Related BCs (Recommended)

- BC-5.04.001 — consumed by (naive ISO timestamps)
- BC-3.02.002 — contrasts with (the libc `mktime` path that the native probe removes)

## Architecture Anchors (Recommended)

- `architecture/TBD.md#pyfmt-time` — local-time conversion (filled by architect)

## Story Anchor (Recommended)

TBD — pyfmt time (design step S1)

## VP Anchors (Recommended)

- VP-TBD — `_mktime` port equals CPython goldens
