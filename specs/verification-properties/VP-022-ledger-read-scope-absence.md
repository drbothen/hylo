---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, architecture/ARCH-04-data-files.md, architecture/ARCH-09-reserved-boundaries.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "2e59f37"
traces_to: prd.md
source_bc: BC-1.06.001
bcs: [BC-1.06.001, BC-1.04.001]
module: internal/statusline (Env read scope)
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

# VP-022: The status line never reads the ledger (DI-007) — architectural absence, REVISIT P7

## Property Statement

The status line's read scope contains no ledger access whatsoever: the `Env` seam set
has no ledger member, no statusline/cost package code opens `paths.ledger`, and its
live per-request inputs are only stdin, the transcript, the metrics store, and its own
caches. DI-007 is thus enforced structurally in P1 — not by discipline. The REVISIT
flag (OD-125) applies: at P7's ledger redesign, allowing ledger-backed widgets would
amend DI-007 and add a BC7←BC4 dependency; this VP is annotated for that revisit and
would be modified, not silently widened.

## Source Contract

- **Primary BC:** BC-1.06.001 — Cache load/save: never-raise, raw sid in file names
  (session caches are the only persisted state the render path touches).
- **Partial coverage:** BC-1.04.001 (fetch_sample — the metrics client is the only
  network edge; `Proxy: nil` transport, D14-(b) precedent).
- **Invariant verified:** DI-007 in force (permanent rule with REVISIT P7, OD-125);
  ARCH-09 boundary rule 3 (Env read scope has no ledger seam).

## Property Class and Verification Method

- **Class:** invariant (an absence property — the strongest form is structural).
- **Method:** static analysis + code review: (a) compile-time — the `Env` struct
  literal admits no ledger member; a package-import audit asserts
  `internal/statusline` and `internal/cost` do not reference `paths.ledger` or any
  ledger package; (b) a grep-based CI lint asserting no ledger file open in the render
  path; (c) architecture conformance at adversarial review.
- **Honesty:** absence verified by construction + audit, not runtime proof; the P1
  structural claim is the cheapest true form of DI-007 enforcement.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Static audit | CI lint (grep/import check) + review | yes — whole-package scope | no ledger reference in render path |

## Proof Harness Skeleton

```go
func TestEnvScope_NoLedgerSeam(t *testing.T) {
    // Reflection over Env's members: none may name a ledger type.
    for m := 0; m < reflect.TypeOf(statusline.Env{}).NumField(); m++ {
        name := reflect.TypeOf(statusline.Env{}).Field(m).Name
        if strings.Contains(strings.ToLower(name), "ledger") {
            t.Fatalf("Env.%s: DI-007 leak", name)
        }
    }
}
// plus a CI grep: no `paths.ledger` reference under internal/statusline or internal/cost
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestEnvScope_NoLedgerSeam` + the CI
import lint (ARCH-08 hygiene legs carry it).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Whole-package source | static |
| Proof complexity | Low | structural absence |
| Tool support | Full | reflect + grep lint |
| Estimated proof time | Hours | |
| Revisit | P7 (OD-125) | ledger redesign may amend DI-007; this VP is the revisit anchor |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
