---
document_type: verification-property
level: L4
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-18T23:45:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-05/BC-5.04.001.md, behavioral-contracts/ss-05/BC-5.04.002.md, behavioral-contracts/ss-05/BC-5.04.003.md, owner-decisions-log-2026-11-14.md]
input-hash: "efe94ae"
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
modified: ["1.1 2026-11-17: ADV-P2 fixes — golden count stated consistently; tzdata wording corrected; Windows-CRT note added (A2-24)", "1.2 2026-11-18T09:14:00Z: ADV-P3 fix (A2-11) — corpus rule added: naive local-time conversion cases are tagged posix-only and run on the Linux/macOS legs; the Windows Tier A leg skips them by rule, so no unexplained diff can arise", "1.3 2026-11-18T14:25:00Z: ADV-P4 fix (A2-06, OD-171) — the posix-only class skip is REMOVED: hylo resolves the local zone through internal/platform honouring TZ on every OS (named zone, OS-zone fallback); the parity harness pins TZ=UTC for both binaries so the naive local-time cases run on all three legs with no skip and no blanket carve-out; TZ table test added; documented POSIX-TZ-string limitation recorded", "1.4 2026-11-18T23:45:00Z: ADV-P5 fix (A2-06, OD-177) — TZ semantics refined to libc on every OS: TZ unset → OS zone (via os.Unsetenv with original-TZ cleanup — t.Setenv(TZ, empty) is a DIFFERENT case), TZ empty or unparseable → UTC; fallback rows guarded against vacuity on UTC runners with an explicit skip reason"]
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
when present. Zone resolution (OD-171 as refined by OD-177 — libc semantics on every OS): hylo
resolves the local zone through
`internal/platform`, honouring `TZ` on every OS — load the named zone; `TZ` unset
falls back to the OS zone; `TZ` EMPTY or unparseable falls back to UTC (POSIX and Go
both read an empty `TZ` as UTC, so the empty case is NOT the unset case) — with a
table test covering TZ unset / empty / `UTC` / IANA name / unparseable. The parity harness pins `TZ=UTC` for both binaries, so the
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
  counter for TimeFloat (joint with VP-007's counting seam); the OD-171/OD-177 TZ-resolution
  table test (unset / empty / `UTC` / IANA name / unparseable) against
  `internal/platform` — the unset case via `os.Unsetenv` with original-TZ cleanup
  (`t.Setenv("TZ", "")` sets an EMPTY TZ, a different case), and the fallback rows
  guarded against vacuity on UTC runners (skip with reason when the ambient OS zone
  is UTC, since "OS zone" and "UTC" are then indistinguishable, ADV-P5-A2-06).
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

func TestPlatform_LocalZoneResolution(t *testing.T) { // OD-171 refined by OD-177 (A2-06)
    // The unset case needs a REAL unset: t.Setenv("TZ", "") sets an EMPTY TZ, which
    // libc reads as UTC — a different row. Restore the ambient TZ on cleanup.
    orig, had := os.LookupEnv("TZ")
    t.Cleanup(func() {
        if had {
            _ = os.Setenv("TZ", orig)
        } else {
            _ = os.Unsetenv("TZ")
        }
    })
    _ = os.Unsetenv("TZ") // row 1: TZ truly unset
    if got := platform.ResolveLocalZone(); !zoneMatches(got, osZoneExpectation(t)) {
        t.Fatalf("TZ unset: resolved %v", got)
    }
    for _, tc := range []struct{ tz, want string }{
        {"", "UTC"}, // OD-177: TZ EMPTY → UTC (libc semantics, every OS)
        {"UTC", "UTC"},
        {"Europe/Berlin", "UTC+1 offset via IANA load"}, // sanity: the seam distinguishes zones
        {"@@not~a~zone@@", "UTC"},                       // OD-177: unparseable → UTC
    } {
        t.Setenv("TZ", tc.tz) // per-case env (t.Setenv restores it on cleanup)
        if got := platform.ResolveLocalZone(); !zoneMatches(got, tc.want) {
            t.Fatalf("TZ=%q: resolved %v", tc.tz, got)
        }
    }
}

// osZoneExpectation: the OS-zone fallback row is meaningful only where the ambient
// OS zone differs from UTC; on UTC runners "os-zone" and "UTC" cannot be told apart,
// so the row SKIPS with that reason instead of passing vacuously (ADV-P5-A2-06).
func osZoneExpectation(t *testing.T) string { // re-derives the OS zone at a fixed probe instant
    t.Helper()
    if zoneIsUTCAtProbeInstant() {
        t.Skip("fallback row vacuous: ambient OS zone is UTC on this runner")
    }
    return ambientOSZone() // libc-reported zone, probe instant fixed
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
