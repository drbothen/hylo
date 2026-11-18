---
document_type: verification-property
level: L4
version: "1.7"
status: draft
producer: architect
timestamp: 2026-11-20T08:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-05/BC-5.04.001.md, behavioral-contracts/ss-05/BC-5.04.002.md, behavioral-contracts/ss-05/BC-5.04.003.md, owner-decisions-log-2026-11-14.md]
input-hash: "f6f6178"
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
modified: ["1.1 2026-11-17: ADV-P2 fixes — golden count stated consistently; tzdata wording corrected; Windows-CRT note added (A2-24)", "1.2 2026-11-18T09:14:00Z: ADV-P3 fix (A2-11) — corpus rule added: naive local-time conversion cases are tagged posix-only and run on the Linux/macOS legs; the Windows Tier A leg skips them by rule, so no unexplained diff can arise", "1.3 2026-11-18T14:25:00Z: ADV-P4 fix (A2-06, OD-171) — the posix-only class skip is REMOVED: hylo resolves the local zone through internal/platform honouring TZ on every OS (named zone, OS-zone fallback); the parity harness pins TZ=UTC for both binaries so the naive local-time cases run on all three legs with no skip and no blanket carve-out; TZ table test added; documented POSIX-TZ-string limitation recorded", "1.4 2026-11-18T23:45:00Z: ADV-P5 fix (A2-06, OD-177) — TZ semantics refined to libc on every OS: TZ unset → OS zone (via os.Unsetenv with original-TZ cleanup — t.Setenv(TZ, empty) is a DIFFERENT case), TZ empty or unparseable → UTC; fallback rows guarded against vacuity on UTC runners with an explicit skip reason", "1.5 2026-11-19T12:00:00Z: pass-6 fixes (A2-04: the OD-177 rows are independent t.Run subtests — a UTC-runner vacuity skip no longer ends the whole test)", "1.6 2026-11-19T16:00:00Z: sync-check adv-p6 closure (SC-28) — the zone-grid harness sketch respelled to the call-2 signature LocalToUnix(fields, loc, msvcDomain bool) (int64, error), returning the pair; sketch-only (OD-182); no property change", "1.7 2026-11-20T08:00:00Z: pass-8 fix (A2-04) — the third LocalToUnix/FromISOFormat caller outcome stated normatively: with msvcDomain set (statusline passes platform.IsWindows(), AD-02) a naive wall time on or before 1970-01-01 or at or after year 3001 returns the distinct ErrLocaltimeDomain sentinel, which the caller degrades on (BC-5.04.001/BC-5.04.002); the zone-grid sketch accepts an expected sentinel (WantErr) instead of failing on any error, and the sentinel rows' oracle is declared as the ruled design (Linux-generated CPython goldens cannot produce the MSVC domain error), flagged for a Windows runner"]
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
four grids (Go `time.Date` differs — that is why the port exists) — and it carries a
THIRD caller outcome beside the value and `ErrValue`: with `msvcDomain` set
(statusline passes `platform.IsWindows()`; pure pyfmt imports no platform package,
AD-02), a naive wall time on or before 1970-01-01 or at or after year 3001 leaves
MSVC `localtime_s`'s domain at one of the conversion probes (`t`, `u1`, `u1 − 86400`,
`u2`) and the function returns the distinct `ErrLocaltimeDomain` sentinel, which the
caller degrades on (BC-5.04.001, BC-5.04.002; ADV-P8-A2-04). `TimeFloat` holds the
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
  is UTC, since "OS zone" and "UTC" are then indistinguishable, ADV-P5-A2-06) — every
  row is an independent `t.Run` subtest, so a vacuity skip suppresses only that row,
  never the OD-177 matrix (A2-04).
  Goldens are TZ-independent input/output rows — with `TZ=UTC` pinned for both binaries
  they run identically on every leg. The `ErrLocaltimeDomain` sentinel rows are NOT
  CPython-golden rows — the committed goldens are generated on Linux, which cannot
  produce the MSVC domain error — so their oracle is the ruled design itself
  (BC-5.04.002's every-probe domain check), authored as Go table rows and flagged for
  a Windows runner; the sketch accepts an expected sentinel instead of failing on any
  error (ADV-P8-A2-04).
- **Honesty:** testable-only; zone-grid breadth is the strongest table-pinning in the
  repo but remains empirical.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Zone-grid goldens | Go test, 10,893 rows per grid x 4 grids | yes — committed grid | gap/overlap/all-zones |
| MSVC-domain sentinel rows | Go test (design-ruled rows, Windows runner) | ruled probe-sequence domain rule (BC-5.04.002) | the `ErrLocaltimeDomain` outcome |
| Grammar tables | Go test | yes | FromISOFormat rows |
| Counter assert | Go test | exact | one TimeFloat read per render |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestLocalToUnix_ZoneGridGoldens(t *testing.T) {
    for _, g := range LoadGolden("testdata/mktime.golden") {
        got, err := pyfmt.LocalToUnix(g.Fields, g.Loc, g.MsvcDomain)
        if g.WantErr != nil { // A2-04: an expected-sentinel row (ErrLocaltimeDomain,
            // the MSVC-domain rule) PASSES on that sentinel — the former blanket
            // `err != nil` Fatalf made such a row unpassable
            if !errors.Is(err, g.WantErr) {
                t.Fatalf("%s %v: got err %v, want sentinel %v", g.Zone, g.Wall, err, g.WantErr)
            }
            continue
        }
        if err != nil || got != g.Unix {
            t.Fatalf("%s %v: got %v want %v", g.Zone, g.Wall, got, g.Unix)
        }
    }
}

func TestPlatform_LocalZoneResolution(t *testing.T) { // OD-171 refined by OD-177 (A2-06)
    // A2-04: every row runs as its own t.Run subtest — a vacuity skip on the
    // OS-zone fallback row (UTC runners) must not end the WHOLE test, or the
    // OD-177 empty/UTC/IANA/unparseable rows never execute on CI.
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
    t.Run("TZ truly unset", func(t *testing.T) {
        _ = os.Unsetenv("TZ") // row 1: TZ truly unset
        if got := platform.ResolveLocalZone(); !zoneMatches(got, osZoneExpectation(t)) {
            t.Fatalf("TZ unset: resolved %v", got)
        }
    })
    for _, tc := range []struct{ tz, want string }{
        {"", "UTC"}, // OD-177: TZ EMPTY → UTC (libc semantics, every OS)
        {"UTC", "UTC"},
        {"Europe/Berlin", "UTC+1 offset via IANA load"}, // sanity: the seam distinguishes zones
        {"@@not~a~zone@@", "UTC"},                       // OD-177: unparseable → UTC
    } {
        t.Run("TZ="+tc.tz, func(t *testing.T) { // A2-04: per-row subtest
            t.Setenv("TZ", tc.tz) // per-case env (t.Setenv restores it on cleanup)
            if got := platform.ResolveLocalZone(); !zoneMatches(got, tc.want) {
                t.Fatalf("TZ=%q: resolved %v", tc.tz, got)
            }
        })
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
