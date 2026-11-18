---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-19T16:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-04-data-files.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.02.004.md, behavioral-contracts/ss-01/BC-1.06.001.md, behavioral-contracts/ss-01/BC-1.05.009.md, behavioral-contracts/ss-01/BC-1.04.020.md, behavioral-contracts/ss-01/BC-1.03.002.md, owner-decisions-log-2026-11-14.md]
input-hash: "9a1ca94"
traces_to: prd.md
source_bc: BC-6.02.004
bcs: [BC-6.02.004, BC-1.06.001, BC-1.05.009, BC-1.04.020, BC-1.03.002, BC-1.02.005, BC-1.02.013, BC-1.02.030, BC-1.01.009]
module: internal/parity (swap), internal/statusline (cache.go)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-18T09:24:00Z: ADV-P3 fix (A2-19) — BC-1.02.005/BC-1.02.013 brought into the body: the session-family swap legs carry the rate-limit cache shape (BC-1.02.005) and the session-state field discipline (BC-1.02.013) through both directions, so frontmatter bcs and Source Contract now agree", "1.3 2026-11-19T16:00:00Z: sync-check adv-p6 closure (SC-21) — bcs: gains BC-1.01.009, whose PC2 names the swap legs' Python-written cost history (VP-019 swap) as the reachability route for the history-borne CP-O10/O11 raise; Source Contract names the row; no property change"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-019: Four-cache swap — Python-writes/Go-reads and reverse are byte-identical

## Property Statement

For all four legacy-compatible cache files (session state, mix cache, git cache, cost
history): a file written by the Python oracle is loaded by Go into the identical
ordered `pyfmt.Value` and vice versa; and a full refresh run by one side against the
other's seeded caches yields byte-identical cache files afterwards. Key order is
inheritance-preserved (BC-1.04.020), int/float distinction survives (api_ms stays int,
BC-1.05.009), and NaN usd bytes match the oracle pin (OD-138). The session-family
swap legs carry the rate-limit cache shape (BC-1.02.005) and the session-state
field discipline (BC-1.02.013) through both directions — the seeded caches exercise
the fields those contracts own, which is what their frontmatter routing claims.

## Source Contract

- **Primary BC:** BC-6.02.004 — Cache-swap coverage: Python-writes/Go-reads and
  reverse, all four caches.
- **Partial coverage:** BC-1.06.001 (load/save never-raise), BC-1.05.009 (record_cost
  exact JSON format), BC-1.04.020 (pinned sequence and cache key order), BC-1.03.002
  (mix cache name/reset rules), BC-1.02.030 (effective_rl writes), BC-1.02.005
  (rate-limit cache shape through the session-family legs), BC-1.02.013
  (session-state field discipline through the session-family legs), BC-1.01.009
  (effect order — its PC2 within-step exception is reachable through the swap legs'
  Python-written cost history, the reachability route its Verification Properties
  note names; SC-21 reciprocity).
- **Invariant verified:** DI-012 (byte-exact interchange is the parity substrate);
  AD-08 (byte-exact writers over ordered Value).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** golden/parity tier — `TestParityCacheSwap_FourCaches` drives the case
  families with `seed/` cache dirs: Python-writes-then-Go-refreshes and
  Go-writes-then-Python-refreshes, all four caches, comparing bytes after each leg.
- **Honesty:** testable-only at the seam (AD-08 feasibility note); the bytes are
  oracle-pinned, so the empirical claim is as strong as the corpus.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Swap differential | `go test ./internal/parity -run TestParityCacheSwap_FourCaches` | yes — 4 caches x 2 directions x seeded cases | all four cache families |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestParityCacheSwap_FourCaches(t *testing.T) {
    for _, fam := range []string{"session", "mix", "git", "cost"} {
        for _, dir := range []string{"py-writes", "go-writes"} {
            out := SwapRefresh(fam, dir)
            if !CacheBytesEqual(fam, out) { t.Fatalf("%s/%s: cache bytes differ", fam, dir) }
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestParityCacheSwap_FourCaches` (ARCH-07); seeds held under `seed/` in legacy
file-name formats (BC-1.06.001 named constants).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | 4 x 2 x seeded cases | bounded |
| Proof complexity | N/A | |
| Tool support | Full | harness per ARCH-07 |
| Estimated proof time | Days | seed curation is the cost |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
