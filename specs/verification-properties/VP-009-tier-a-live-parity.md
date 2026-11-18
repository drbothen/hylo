---
document_type: verification-property
level: L4
version: "1.11"
status: draft
producer: architect
timestamp: 2026-11-18T21:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.02.002.md, behavioral-contracts/ss-06/BC-6.02.003.md, behavioral-contracts/ss-06/BC-6.03.002.md, prd-supplements/nfr-catalog.md, owner-decisions-log-2026-11-14.md]
input-hash: "926fd96"
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
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — exclusion ids respelled to the BC form and closed set extended to ten ids (A2-02); subagent corpus family added (BC-1.07.002 enabled=true parity rows, BC-1.07.007 _fmt_tokens dense grid)", "1.3 2026-11-18T09:08:00Z: ADV-P3 fixes — corpus leg asserts a non-zero computed case count and logs “N cases validated” (POL-11, A2-06); “93 contracts” count claim re-anchored honestly (A2-20)", "1.4 2026-11-18: ADV-P4 pass-4 fix (D10) — harness skeleton loads cases from the canonical corpus root internal/parity/testdata/cases", "1.5 2026-11-18T22:00:00Z: pass-4 correction (item 10) — harness skeleton loads cases from the OD-148 corpus root internal/statusline/testdata/parity/cases (fixtures stay with the subject package)", "1.6 2026-11-18T23:30:00Z: pass-4 sync SC-06 — closed-set enumeration gains OD-166 (cost-history unconvertible-field scope, OD-169), completing the eleven-id set to match VP-012 and the other enumeration sites", "1.7 2026-11-18T23:45:00Z: ADV-P5 fixes (A2-14, A2-16) — the byte-exact census corrected to a reproducible count and method: 73 BC frontmatters (68 in SS-01, 5 in SS-05/SS-06) by grep -rl over specs/, dated 2026-11-18; parity cases resolve from the MODULE ROOT via the ARCH-07 helper (walk up to go.mod), never cwd-relative — go test cwd is the package dir and a cwd-relative load finds zero cases, turned false-red by the POL-11 guard", "1.8 2026-11-19T12:00:00Z: pass-6 fixes (A2-23: skeleton replays git-ignored captures/ when present under the same closed-set rule, not only the committed corpus)", "1.9 2026-11-19T16:00:00Z: sync-check adv-p6 closure (SC-23) — the property statement's closed-set parenthetical extends to the TWELVE-id set with OD-181 (metrics transport beyond plain http), matching VP-012, error-taxonomy, prd DI-012, ARCH-00 and invariants.md; no property or method change",
  "1.10 2026-11-19T18:00:00Z: pass-7 fixes (A2-12, A2-19/OD-190) — the sketch's captures leg resolves from the module root (walk up to go.mod) like the corpus leg, never cwd-relative, and runs the same CompareNamedCaches referee half as the corpus leg; the property statement names the owner-ruled Windows-oracle stdio normalization (OD-190, extending OD-183: UTF-8 + LF on every OS) beside the closed set",
  "1.11 2026-11-18T21:00:00Z: pass-11 fixes (A2-02/OD-190 call 1, A2-09) — the normalization clause applied literally: the COMPARATOR converts the ORACLE's stdout CRLF to LF openly, before the stepwise byte comparison; hylo's bytes are never converted; the clock shim does no newline reconfigure (the former 'rather than hidden in the shim' wording was ambiguous in the shim's direction); Source Contract names and justifies BC-1.01.009, which bcs: carries and whose VP-table row ('per-step cache bytes match legacy across the corpus') is this VP's Tier A leg"]
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
(D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161,
OD-166, OD-181) carving out ruled differences — plus the owner-ruled Windows-oracle
stdio normalization (OD-190, extending OD-183: hylo reads and writes UTF-8 + LF line
endings on every OS): on the Windows legs the COMPARATOR converts the ORACLE's stdout
CRLF to LF openly, before the stepwise byte comparison — hylo's bytes are never
converted (hylo writes LF itself, so where legacy's Windows text-mode `print()` would
emit CRLF, SL:1234, the referee folds the oracle side only) — and the clock shim does
no newline reconfigure; the conversion is a named comparator step, not a shim behavior.
Zero
unexplained diffs is the D4 exit criterion (OD-117 target 1). The corpus carries the
`--subagent` family: enabled=true rows replay the legacy subagent renderer stepwise
(BC-1.07.002), and the `_fmt_tokens` dense-grid table rides the T-family rows
(BC-1.07.007).

## Source Contract

- **Primary BC:** BC-6.03.002 — Comparison = stdout bytes + exit code per step; named
  caches byte-for-byte by file name; stderr never compared.
- **Partial coverage:** BC-6.02.002 (stdin-sequence replay, clock stepped per refresh),
  BC-6.02.003 (case model), BC-1.01.009 (side-effect order: the stepwise referee
  observes each write's disk state between the per-step stdout/exit comparisons, so a
  write misplaced from legacy's position k is visible as a mid-sequence cache diff —
  the BC's VP-table row "per-step cache bytes match legacy across the corpus" is this
  VP's Tier A leg; A2-09), and collectively the byte-exact-class SS-01 contracts the
  VP-INDEX coverage table routes to this tier (73 BCs carry `parity_class: byte-exact`
  in frontmatter — 68 in SS-01, 5 in SS-05/SS-06 — by `grep -rl "parity_class:
  byte-exact"` over specs/, 2026-11-18, ADV-P5-A2-14; each is exercised by its corpus
  family, not by this VP file alone).
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

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestParityTierA_Corpus(t *testing.T) {
    n := 0
    // A2-16 (plan call 18): fixtures resolve from the MODULE ROOT (walk up to
    // go.mod — the helper ARCH-07 names), never cwd-relative: go test sets cwd
    // to the package dir, and a cwd-relative load finds zero cases, which the
    // POL-11 guard then reports as a false red.
    for _, cs := range LoadCases(ModuleRoot("internal/statusline/testdata/parity/cases")) {
        pyOut := RunOracle(cs)                       // CPython 3.11.x, clock shim, -s
        goOut := RunGoPort(cs)                       // in-process + built binary subset
        CompareStepwise(t, cs, pyOut, goOut)         // stdout bytes + exit per step
        CompareNamedCaches(t, cs, pyOut.Caches, goOut.Caches) // byte-for-byte, minus exclusions
        n++
    }
    // A2-23: the statement covers replay of git-ignored captures/ too (the brief's
    // success criterion) — replay them when present, validated by the same
    // closed-set rule via captures/exclusions.json (plan call 12; CI never runs them).
    // A2-12: captures resolve from the MODULE ROOT (walk up to go.mod) exactly like
    // the corpus leg — LoadCases("captures") is cwd-relative, go test sets cwd to
    // the package dir, so a cwd-relative load finds zero captures and the corpus
    // count keeps n > 0, hiding the defect.
    for _, cs := range LoadCases(ModuleRoot("captures")) {
        pyOut := RunOracle(cs)
        goOut := RunGoPort(cs)
        CompareStepwise(t, cs, pyOut, goOut)
        CompareNamedCaches(t, cs, pyOut.Caches, goOut.Caches) // A2-12: the same referee
        n++                                                   // half as the corpus leg
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
