---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.02.002.md, behavioral-contracts/ss-06/BC-6.02.003.md, behavioral-contracts/ss-06/BC-6.03.002.md, prd-supplements/nfr-catalog.md, owner-decisions-log-2026-11-14.md]
input-hash: "3fbb08d"
traces_to: prd.md
source_bc: BC-6.03.002
bcs: [BC-6.03.002, BC-6.02.002, BC-6.02.003, BC-1.01.009]
module: internal/parity
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-009: Tier A live differential parity — zero unexplained diffs over corpus and captures

## Property Statement

Over the committed synthetic corpus and the owner's recorded stdin-sequence replays
(git-ignored `captures/`), a live run of `legacy/` under the CPython 3.11.x oracle and
the Go port produce identical results per refresh step: stdout bytes, exit code, and
named caches byte-for-byte by file name — with only the closed named exclusion set
(D4-EX-1/2/3, od30, od76, temp-file, cp-x03) carving out ruled differences. Zero
unexplained diffs is the D4 exit criterion (OD-117 target 1).

## Source Contract

- **Primary BC:** BC-6.03.002 — Comparison = stdout bytes + exit code per step; named
  caches byte-for-byte by file name; stderr never compared.
- **Partial coverage:** BC-6.02.002 (stdin-sequence replay, clock stepped per refresh),
  BC-6.02.003 (case model), and collectively every byte-exact-class S1 contract
  (93 contracts, see the VP-INDEX coverage table).
- **Invariant verified:** DI-012 (changes only via named tested deviations); NFR-003.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** golden/parity tier — `TestParityTierA_Corpus` over the case dirs; the
  referee (comparison + exclusion machinery) is itself proved closed by VP-012.
- **Honesty:** testable-only. Corpus breadth bounds the claim; Tier C fuzz (VP-011)
  extends it randomly; neither is a deductive proof.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Differential test | `go test ./internal/parity -run TestParityTierA_Corpus` | yes — committed corpus + captures | all case families incl. cps/cpt/cpn fault rows |

## Proof Harness Skeleton

```go
func TestParityTierA_Corpus(t *testing.T) {
    for _, cs := range LoadCases("internal/statusline/testdata/parity/cases") {
        pyOut := RunOracle(cs)                       // CPython 3.11.x, clock shim, -s
        goOut := RunGoPort(cs)                       // in-process + built binary subset
        CompareStepwise(t, cs, pyOut, goOut)         // stdout bytes + exit per step
        CompareNamedCaches(t, cs, pyOut.Caches, goOut.Caches) // byte-for-byte, minus exclusions
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestParityTierA_Corpus`; interpreter `HYLO_PARITY_PYTHON` (OD-104/108); captures
replayed only from `captures/` (OD-107).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Large, committed | corpus grows only via review |
| Proof complexity | N/A | differential execution |
| Tool support | Full | harness per ARCH-07 |
| Estimated proof time | Weeks (harness build) | corpus authoring dominates |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
