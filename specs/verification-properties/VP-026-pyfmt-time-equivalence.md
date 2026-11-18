---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T14:25:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-05/BC-5.04.001.md, behavioral-contracts/ss-05/BC-5.04.002.md, behavioral-contracts/ss-05/BC-5.04.003.md, owner-decisions-log-2026-11-14.md]
input-hash: "399d1f4"
traces_to: prd.md
source_bc: BC-5.04.002
bcs: [BC-5.04.001, BC-5.04.002, BC-5.04.003]
module: internal/pyfmt (time.go)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P2 fixes — golden count stated consistently; tzdata wording corrected; Windows-CRT note added (A2-24)", "1.2 2026-11-18T09:14:00Z: ADV-P3 fix (A2-11) — corpus rule added: naive local-time conversion cases are tagged posix-only and run on the Linux/macOS legs; the Windows Tier A leg skips them by rule, so no unexplained diff can arise", "1.3 2026-11-18T14:25:00Z: ADV-P4 fix (A2-06, OD-171) — the posix-only class skip is REMOVED: hylo resolves the local zone through internal/platform honouring TZ on every OS (named zone, OS-zone fallback); the parity harness pins TZ=UTC for both binaries so the naive local-time cases run on all three legs with no skip and no blanket carve-out; TZ table test added; documented POSIX-TZ-string limitation recorded"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-026: pyfmt time semantics equivalent to CPython 3.11 (`_mktime` port, ISO grammar)

## Property Statement

`FromISOFormat` implements the Python 3.11 grammar (naive = local, fraction truncation
beyond µs); `LocalToUnix` is the CPython `_mktime` port with gap/overlap semantics
achieving 0 mismatches over the committed CPython goldens — 10,893 rows per zone grid,
four grids (Go `time.Date` differs — that is why the port exists); `TimeFloat` holds the
Python time.time() value discipline (ns→s float, read once per render). Embedded
`time/tzdata` serves as a fallback zone-data source when the OS zoneinfo is absent —
zone resolution no longer depends on local tzdata files, though the OS zoneinfo wins
when present. Zone resolution (OD-171): hylo resolves the local zone through
`internal/platform`, honouring `TZ` on every OS — load the named zone; fall back to the
OS zone when `TZ` is unset or unparseable — with a table test covering TZ unset / `UTC` /
IANA name / unparseable. The parity harness pins `TZ=UTC` for both binaries, so the
naive local-time wall-clock cases run on ALL THREE Tier A legs with no skip and no
class-wide carve-out (the pass-3 `posix-only` tag is removed; D21/ADV-P4-A2-06).
Documented limitation: POSIX-style TZ strings (e.g. `EST5EDT`) may resolve differently
under the Windows MS CRT than under IANA loading; parity cases use `TZ=UTC` only.

## Source Contract

- **Primary BC:** BC-5.04.002 — LocalToUnix: CPython `_mktime` port, gap/overlap
  semantics, TZ injection, embedded tzdata.
- **Partial coverage:** BC-5.04.001 (FromISOFormat 3.11 grammar), BC-5.04.003
  (TimeFloat once-per-render).
- **Invariant verified:** IM-14 (one clock read per render) jointly with VP-007;
  AD-04 (CPython fidelity for naive-local transcript timestamps, BC-5.04.001).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** oracle tables — 10,893 CPython `_mktime` goldens per zone grid, four
  grids (DST gaps, overlaps, repeated hours), FromISOFormat grammar tables; a once-per-render
  counter for TimeFloat (joint with VP-007's counting seam); the OD-171 TZ-resolution
  table test (unset / `UTC` / IANA name / unparseable) against `internal/platform`.
  Goldens are TZ-independent input/output rows — with `TZ=UTC` pinned for both binaries
  they run identically on every leg.
- **Honesty:** testable-only; zone-grid breadth is the strongest table-pinning in the
  repo but remains empirical.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Zone-grid goldens | Go test, 10,893 rows per grid x 4 grids | yes — committed grid | gap/overlap/all-zones |
| Grammar tables | Go test | yes | FromISOFormat rows |
| Counter assert | Go test | exact | one TimeFloat read per render |

## Proof Harness Skeleton

```go
func TestLocalToUnix_ZoneGridGoldens(t *testing.T) {
    for _, g := range LoadGolden("testdata/mktime.golden") {
        if got := pyfmt.LocalToUnix(g.Loc, g.Wall); got != g.Unix {
            t.Fatalf("%s %v: got %v want %v", g.Zone, g.Wall, got, g.Unix)
        }
    }
}

func TestPlatform_LocalZoneResolution(t *testing.T) { // OD-171 table test (A2-06)
    for _, tc := range []struct{ tz, want string }{
        {"", "os-zone"},        // TZ unset → OS zone
        {"UTC", "UTC"},         // named zone honoured on every OS
        {"Europe/Berlin", "UTC+1 offset via IANA load"},
        {"@@not~a~zone@@", "os-zone"}, // unparseable → OS zone fallback
    } {
        t.Setenv("TZ", tc.tz) // per-case env (t.Setenv restores it on cleanup)
        if got := platform.ResolveLocalZone(); !zoneMatches(got, tc.want) {
            t.Fatalf("TZ=%q: resolved %v", tc.tz, got)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; goldens at `internal/pyfmt/testdata/mktime.golden`
(gen scripts under `testdata/gen/*.py`, pinned 3.11 oracle).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | 10,893 x 4 committed | generated offline |
| Proof complexity | Medium | DST edge enumeration offline |
| Tool support | Full | |
| Estimated proof time | Days | grid generation under the oracle |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
