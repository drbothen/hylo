---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-17T22:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-04-data-files.md, behavioral-contracts/ss-01/BC-1.06.001.md, behavioral-contracts/ss-01/BC-1.06.002.md, behavioral-contracts/ss-06/BC-6.03.003.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "d8caaec"
traces_to: prd.md
source_bc: BC-1.06.001
bcs: [BC-1.06.001, BC-1.06.002, BC-6.03.003]
module: internal/statusline (cache.go), internal/cost
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: dropped BC-1.03.002 from bcs — VP-018 verifies none of its properties (reset predicate, zero-save, 16-key order)"]
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
0600), then `os.replace`. A failed save removes its temp, and a temp left behind by a
killed process is removed opportunistically at the next `Save`, never at render time
(the ruled difference from leaking legacy, named exclusion `temp-file`, carved out only
from the cache-file comparison per BC-6.03.003 and ARCH-04 temp-file cleanup); a save
whose sid contains `/` performs a failed
replace that persists nothing while the in-memory overlay still answers the same
refresh (BC-1.06.002); a failed rename under Windows sharing violations retries
exactly `renameRetryLimit = 2` times before swallowing (named constant, not config:
internal durability knob of a named fs difference, no parity-visible behavior — legacy
has no retry at all, IM-17/OD-110); and a load never raises — an unreadable or
malformed cache file
loads as an empty object without corrupting or deleting the file on disk.

## Source Contract

- **Primary BC:** BC-1.06.001 — Cache load/save: never-raise, raw sid in file names.
- **Partial coverage:** BC-1.06.002 (sid with `/`: failed replace persists nothing;
  temp handling), BC-6.03.003 (mkstemp temp names excluded from comparison; Go
  cleanup difference covered).
- **Invariant verified:** DI-008 (cache faults stay on the safe ladder); OD-110
  (temp-file exclusion with its own table test); AP-16 corollary for the session
  caches (parse failure never destroys the file — full cost-history statement in
  VP-020).

## Property Class and Verification Method

- **Class:** safety.
- **Method:** unit/table test with fault injection — failing renames, read-only or
  closed cache dir, sids containing `/`, interrupted saves; asserts no `.tmp` residue,
  no partial files, and unchanged target files.
- **Honesty:** testable-only (filesystem effects); the AP-16-style "never overwrite
  unreadable" invariant is asserted at the seam.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Fault-injection tables | Go test, temp dirs | yes — enumerated fault sites | failed rename, closed dir, slash-sid, interrupt |

## Proof Harness Skeleton

```go
const renameRetryLimit = 2 // named constant: transient Windows sharing violations
                            // (AV/indexer locks); not config — no parity-visible
                            // behavior, legacy has no retry (IM-17, OD-110)

func TestCacheStore_OD110_TempCleanup(t *testing.T) {
    dir := tempCacheDir(t)
    store := newFailingRenameStore(dir, failFirst(renameRetryLimit))
    if err := store.Save("statusline-abc.json", val); err != nil {
        t.Fatalf("save within retry budget: %v", err)
    }
    if tmps(dir) != 0 { t.Fatal("temp leaked") }
    if !savedTargetIntact(dir) { t.Fatal("partial file") }

    hopeless := newFailingRenameStore(dir, failFirst(renameRetryLimit+1))
    if err := hopeless.Save("statusline-abc.json", val); err == nil {
        t.Fatal("save past retry budget should swallow, not succeed")
    }
    if tmps(dir) != 0 { t.Fatal("temp leaked on swallowed save") }
}

func TestCacheStore_StaleTempCleanupAtNextSave(t *testing.T) {
    dir := tempCacheDir(t)
    plantStaleTemps(dir, "statusline-old.json.tmp123") // simulates a killed process
    store := storeAt(t, dir)
    store.Save("statusline-new.json", val) // one save, any sid
    if tmps(dir) != 0 { t.Fatal("stale temp survived a Save (ARCH-04 cleanup)") }
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

`TestCacheStore_OD110_TempCleanup` and
`TestCacheStore_TempFile_CleanupOnFailedReplace` (both settled at stage-3
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
