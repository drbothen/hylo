---
document_type: verification-property
level: L4
version: "1.7"
status: draft
producer: architect
timestamp: 2026-11-19T16:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-04-data-files.md, behavioral-contracts/ss-01/BC-1.06.001.md, behavioral-contracts/ss-01/BC-1.06.002.md, behavioral-contracts/ss-06/BC-6.03.003.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "8e9e253"
traces_to: prd.md
source_bc: BC-1.06.001
bcs: [BC-1.06.001, BC-1.06.002, BC-6.03.003, BC-2.01.004]
module: internal/statusline (cache.go), internal/cost
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: dropped BC-1.03.002 from bcs — VP-018 verifies none of its properties (reset predicate, zero-save, 16-key order)", "1.3 2026-11-17: ADV-P2 pass-2 fixes — OD-163: a save removes only its own temp file, no directory-wide sweep (concurrency ruling for ADV-P2-A03/A2-15); load-failure wording aligned with VP-020 (the next save overwrites the file — A2-03); swallow/retry and cleanup-timing wording reconciled with the skeleton (A2-28)", "1.4 2026-11-18T09:23:00Z: ADV-P3 fix (A2-25) — retry scope pinned: the rename-retry arm is Windows-only (sharing violations are the named Windows fs difference); on POSIX a failed rename reports failure immediately, matching legacy", "1.5 2026-11-18T14:28:00Z: ADV-P4 fix (A2-07) — TestCacheStore_OD110_TempCleanup skeleton OS-gated: the success-after-retry leg runs only on windows (runtime.GOOS gate); POSIX legs assert immediate failure reporting, so a correct implementation no longer goes red on the ubuntu/macos CI legs", "1.6 2026-11-19T12:00:00Z: pass-6 fixes (OD-186: single attempt count — one initial attempt + two retries = three attempts (aligned with ARCH-04 and BC-6.03.003); the retry delay is config statusline.cache.rename_retry_delay_ms; the widened temp-file scope (Windows rename-retry persistence) cited)", "1.7 2026-11-19T16:00:00Z: sync-check adv-p6 closure (SC-21) — bcs: gains BC-2.01.004, whose PC-11 registry row cross-references this VP for the rename_retry_delay_ms key semantics; Source Contract names the row; no property change"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-018: Atomic cache writes — no partial files, temp cleanup, failed replace persists nothing

## Property Statement

Every cache save is atomic: write to a `mkstemp`-pattern temp in the cache dir (mode
0600), then `os.replace`. A failed save removes its own temp. A save removes **only
its own temp file** (OD-163): there is no directory-wide sweep, and a temp left behind
by a killed process is not removed by other processes' saves — legacy leaks those
temps identically, and the comparison carve-out for leaked temps is the named
exclusion `temp-file` (cache-file comparison only, per BC-6.03.003 and ARCH-04
temp-file cleanup; OD-163 resolves the cross-window deletion hazard of ADV-P2-A03 by
restoring parity: no Go-side sweep at all). Temp cleanup runs inside `Save`, never on
the load/read path. A save
whose sid contains `/` performs a failed
replace that persists nothing while the in-memory overlay still answers the same
refresh (BC-1.06.002); a failed rename under Windows sharing violations retries
exactly `renameRetryLimit = 2` times — one initial attempt plus two retries, THREE
attempts in all, the single consistent count (OD-186) with ARCH-04 and BC-6.03.003 —
sleeping `statusline.cache.rename_retry_delay_ms` (Int, default 10, range 1..1000,
labeled judgment call, OD-186) between attempts, then reports failure to the caller
by error
return — it is the caller (the render effect) that swallows it, per the DI-008 safe
ladder (limit as named constant; the delay is config (OD-186) — an internal durability
knob of a named fs difference, no parity-visible behavior — legacy
has no retry at all, IM-17/OD-110; the retry arm is Windows-only — sharing
violations are the named Windows fs difference, and on POSIX a failed rename
reports failure immediately, matching legacy; hylo may persist a cache write legacy
would not — the Windows sharing-violation rename-retry outcome rides the widened
`temp-file` exclusion scope, OD-186); and a load never raises — an unreadable or
malformed cache file loads as an empty object, the load itself leaves the file on disk
untouched, and the next successful save overwrites it with regenerated content
(legacy behaviour; the cost-history statement is VP-020's).

## Source Contract

- **Primary BC:** BC-1.06.001 — Cache load/save: never-raise, raw sid in file names.
- **Partial coverage:** BC-1.06.002 (sid with `/`: failed replace persists nothing;
  temp handling), BC-6.03.003 (mkstemp temp names excluded from comparison; Go
  cleanup difference covered), BC-2.01.004 (PC-11 registry row for
  `statusline.cache.rename_retry_delay_ms` cross-references this VP for the OD-186
  key semantics — SC-21 reciprocity).
- **Invariant verified:** DI-008 (cache faults stay on the safe ladder); OD-110
  (temp-file exclusion with its own table test); AP-16 corollary for the session
  caches (unreadable/malformed loads as empty; the next save overwrites the file with
  regenerated content — full cost-history statement in
  VP-020).

## Property Class and Verification Method

- **Class:** safety.
- **Method:** unit/table test with fault injection — failing renames, read-only or
  closed cache dir, sids containing `/`, interrupted saves; asserts no `.tmp` residue,
  no partial files, and unchanged target files.
- **Honesty:** testable-only (filesystem effects); the AP-16-style seam assert is
  "load leaves the file byte-unchanged; only a subsequent successful save rewrites it".

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Fault-injection tables | Go test, temp dirs | yes — enumerated fault sites | failed rename, closed dir, slash-sid, interrupt |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
const renameRetryLimit = 2 // named constant: transient Windows sharing violations
                            // (AV/indexer locks); not config — no parity-visible
                            // behavior, legacy has no retry (IM-17, OD-110).
                            // Value 2 is a LABELED JUDGMENT CALL (P16/D15): unmeasured
                            // — no parity-visible behavior exists to measure; one
                            // retry absorbs a transient lock, two observes the lock
                            // persist (ADV-P5-A2-32). With the initial attempt this
                            // is 3 ATTEMPTS TOTAL — the single consistent count
                            // (OD-186; ARCH-04 and BC-6.03.003 state the same). The
                            // inter-attempt delay is CONFIG:
                            // statusline.cache.rename_retry_delay_ms (Int, default
                            // 10, range 1..1000, OD-186), not a package constant.

func TestCacheStore_OD110_TempCleanup(t *testing.T) {
    dir := tempCacheDir(t)
    if runtime.GOOS == "windows" { // A2-07: the retry arm is Windows-only — a
        // POSIX run must not expect success after failed renames
        store := newFailingRenameStore(dir, failFirst(renameRetryLimit))
        if err := store.Save("statusline-abc.json", val); err != nil {
            t.Fatalf("save within retry budget: %v", err)
        }
        if tmps(dir) != 0 { t.Fatal("temp leaked") }
        if !savedTargetIntact(dir) { t.Fatal("partial file") }
    }

    // Immediate-failure leg (all OSes): past the retry budget the save reports
    // failure by error return — and on POSIX the FIRST failed rename already does.
    fails := renameRetryLimit + 1 // 3 attempts: initial + 2 retries (OD-186 single count)
    if runtime.GOOS != "windows" { fails = 1 } // POSIX: no retry arm, report immediately
    hopeless := newFailingRenameStore(dir, failFirst(fails))
    if err := hopeless.Save("statusline-abc.json", val); err == nil {
        t.Fatal("save past retry budget should report failure, not succeed") // caller swallows (DI-008)
    }
    if tmps(dir) != 0 { t.Fatal("temp leaked on swallowed save") }
}

func TestCacheStore_OwnTempOnly(t *testing.T) { // OD-163: a save removes only its own temp
    dir := tempCacheDir(t)
    plantForeignTemps(dir, "statusline-old.json.tmp123") // simulates a killed process
    store := storeAt(t, dir)
    store.Save("statusline-new.json", val)
    if tmps(dir) != 1 {
        t.Fatal("a Save swept a foreign temp — OD-163 forbids a directory-wide sweep")
    } // the surviving temp is the killed process's; legacy leaks it identically
}

func TestCacheStore_TempFile_CleanupOnFailedReplace(t *testing.T) {
    store := tempCacheDirStore(t)
    before := store.Snapshot()
    store.Save("statusline-a/b.json", val) // slash sid: replace fails
    if store.DiffersFrom(before) { t.Fatal("failed replace persisted something") }
    if tmps(store.Dir()) != 0 { t.Fatal("temp leaked on failed replace") }
}
```

## Named Tests (OD-145 table where applicable)

`TestCacheStore_OD110_TempCleanup`,
`TestCacheStore_OwnTempOnly` (OD-163), and
`TestCacheStore_TempFile_CleanupOnFailedReplace` (settled at stage-3
integration); the `temp-file` exclusion entry is admissibility-checked by
`TestParityExclusions_ClosedSet` (VP-012).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Enumerated fault sites | small |
| Proof complexity | N/A | filesystem-seam observations |
| Tool support | Full | t.TempDir |
| Estimated proof time | Days | Windows retry leg needs the matrix (VP-037) |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
