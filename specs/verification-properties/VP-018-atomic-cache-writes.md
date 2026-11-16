---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-04-data-files.md, behavioral-contracts/ss-01/BC-1.06.001.md, behavioral-contracts/ss-01/BC-1.06.002.md, behavioral-contracts/ss-06/BC-6.03.003.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "78016eb"
traces_to: prd.md
source_bc: BC-1.06.001
bcs: [BC-1.03.002, BC-1.06.001, BC-1.06.002, BC-6.03.003]
module: internal/statusline (cache.go), internal/cost
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: []
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
0600), then `os.replace`. A failed or interrupted save removes its temp (the ruled
difference from leaking legacy, named exclusion `temp-file`, carved out only from the
cache-file comparison per BC-6.03.003); a save whose sid contains `/` performs a failed
replace that persists nothing while the in-memory overlay still answers the same
refresh (BC-1.06.002); a failed rename under Windows sharing violations retries 2-3
times before giving up; and a load never raises — an unreadable or malformed cache file
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
func TestCacheStore_OD110_TempCleanup(t *testing.T) {
    dir := tempCacheDir(t)
    store := newFailingRenameStore(dir, failFirst(1))
    store.Save("statusline-abc.json", val)
    if tmps(dir) != 0 { t.Fatal("temp leaked") }
    if !savedTargetIntact(dir) { t.Fatal("partial file") }
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
