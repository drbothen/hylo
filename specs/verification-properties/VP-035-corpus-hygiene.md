---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-18T09:10:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, architecture/ARCH-08-build-ci-release.md, behavioral-contracts/ss-06/BC-6.02.001.md, prd-supplements/nfr-catalog.md]
input-hash: "89fd12d"
traces_to: prd.md
source_bc: BC-6.02.001
bcs: [BC-6.02.001, BC-6.04.001]
module: internal/parity (corpus), CI hygiene legs
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-18T09:10:00Z: ADV-P3 fixes (A2-06) — provenance test asserts a non-zero computed fixture count and logs “N fixtures validated” (POL-11)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-035: Corpus hygiene — synthetic committed fixtures only, secret-scan clean

## Property Statement

Every committed fixture under `internal/statusline/testdata/` is synthetic; the
owner's real inputs exist only as git-ignored copies under `captures/` (OD-107) and are
never committed; `gitleaks detect --source . --log-opts="--all"` plus the category
pattern scan are clean on every push and CI leg. `TestCorpusHygiene` enforces the
committed-corpus provenance in-tree.

## Source Contract

- **Primary BC:** BC-6.02.001 — Committed corpus synthetic-only; owner real inputs
  replayed from git-ignored captures/.
- **Partial coverage:** BC-6.04.001 (gitleaks leg on every change).
- **Invariant verified:** NFR-006 / policy 21 (public-repo hygiene: synthetic paths
  only — examples use /home/user shapes, never machine-specific details).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test + CI gate — `TestCorpusHygiene` asserts fixture
  provenance markers and rejects committed captures; the CI hygiene leg runs gitleaks
  with the category scan (push-gate, not a proof).
- **Honesty:** in-tree part is table-tested; overall cleanliness is a push-gate
  assertion, honestly weaker than a proof (ARCH-08 feasibility note).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Provenance test | `TestCorpusHygiene` | yes — testdata tree | synthetic markers, no committed captures |
| Secret scan | gitleaks + category pattern scan | process gate | every push and CI leg |

## Proof Harness Skeleton

```go
func TestCorpusHygiene(t *testing.T) {
    n := 0
    for _, fx := range CommittedFixtures() {
        if !fx.ProvenanceSynthetic() { t.Fatalf("%s: not marked synthetic", fx.Path) }
        n++
    }
    if n == 0 { // POL-11 (A2-06): a mis-pathed fixture load must not pass green
        t.Fatal("zero committed fixtures found — mis-pathed load passes nothing")
    }
    t.Logf("%d committed fixtures validated", n)
    if committedCapturesExist() { t.Fatal("captures/ content committed") }
}
```

## Named Tests (OD-145 table where applicable)

`TestCorpusHygiene` (settled, NFR-006); CI hygiene leg per ARCH-08 workflow.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Whole testdata tree | static |
| Proof complexity | N/A | gate + test |
| Tool support | Full | gitleaks |
| Estimated proof time | Hours | |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
