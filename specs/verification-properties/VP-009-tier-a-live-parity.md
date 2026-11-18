---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T09:08:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.02.002.md, behavioral-contracts/ss-06/BC-6.02.003.md, behavioral-contracts/ss-06/BC-6.03.002.md, prd-supplements/nfr-catalog.md, owner-decisions-log-2026-11-14.md]
input-hash: "bdc53a7"
traces_to: prd.md
source_bc: BC-6.03.002
bcs: [BC-6.03.002, BC-6.02.002, BC-6.02.003, BC-1.01.009, BC-1.07.002, BC-1.07.007]
module: internal/parity
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — exclusion ids respelled to the BC form and closed set extended to ten ids (A2-02); subagent corpus family added (BC-1.07.002 enabled=true parity rows, BC-1.07.007 _fmt_tokens dense grid)", "1.3 2026-11-18T09:08:00Z: ADV-P3 fixes — corpus leg asserts a non-zero computed case count and logs “N cases validated” (POL-11, A2-06); “93 contracts” count claim re-anchored honestly (A2-20)"]
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
(D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161)
carving out ruled differences. Zero
unexplained diffs is the D4 exit criterion (OD-117 target 1). The corpus carries the
`--subagent` family: enabled=true rows replay the legacy subagent renderer stepwise
(BC-1.07.002), and the `_fmt_tokens` dense-grid table rides the T-family rows
(BC-1.07.007).

## Source Contract

- **Primary BC:** BC-6.03.002 — Comparison = stdout bytes + exit code per step; named
  caches byte-for-byte by file name; stderr never compared.
- **Partial coverage:** BC-6.02.002 (stdin-sequence replay, clock stepped per refresh),
  BC-6.02.003 (case model), and collectively the byte-exact-class SS-01 contracts the
  VP-INDEX coverage table routes to this tier (68 BCs carry `parity_class: byte-exact`
  by file grep; each is exercised by its corpus family, not by this VP file alone).
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
    n := 0
    for _, cs := range LoadCases("internal/statusline/testdata/parity/cases") {
        pyOut := RunOracle(cs)                       // CPython 3.11.x, clock shim, -s
        goOut := RunGoPort(cs)                       // in-process + built binary subset
        CompareStepwise(t, cs, pyOut, goOut)         // stdout bytes + exit per step
        CompareNamedCaches(t, cs, pyOut.Caches, goOut.Caches) // byte-for-byte, minus exclusions
        n++
    }
    if n == 0 { // POL-11 (A2-06): an empty/mis-pathed corpus must not pass green
        t.Fatal("zero parity cases loaded — mis-pathed corpus passes nothing")
    }
    t.Logf("%d parity cases validated", n)
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
