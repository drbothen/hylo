---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, architecture/ARCH-04-data-files.md, architecture/ARCH-09-reserved-boundaries.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "2938a6f"
traces_to: prd.md
source_bc: BC-1.04.001
bcs: [BC-1.04.001]
module: internal/statusline (Env read scope)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fixes — source_bc re-anchored off BC-1.06.001 (C05); allowed path set gains the git widget's .git/HEAD ancestor-walk reads (A2-06)"]
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
caches — plus the git widget's reads of `.git` (directory, or worktree/submodule
pointer file) and of the resolved gitdir's `HEAD`, walked up the ancestor chain of the
project dir (legacy SL:369-389); these are part of the allowed set. Enforcement is by
construction (the `Env` seam set) and is verified **non-vacuously**: a
recording-filesystem test asserts that every file path opened during a full render over
the fault table belongs to the allowed statusline path set (transcript, session caches,
mix/git/metrics caches, cost history, git-widget `.git`/`HEAD` reads up the ancestor
walk) and that no opened path matches the D7 ledger language — an assertion that fails
if any code path opens anything else. The REVISIT
flag (OD-125) applies: at P7's ledger redesign, allowing ledger-backed widgets would
amend DI-007 and add a BC7←BC4 dependency; this VP is annotated for that revisit and
would be modified, not silently widened.

## Source Contract

- **Anchor note (C05):** no single BC carries a ledger-scope postcondition — DI-007 is
  a cross-cutting invariant whose enforcers are the SS-01 effect contracts
  (invariants.md names BC-1.01.009 and BC-1.04.001 as examples). The primary anchor is
  therefore **BC-1.04.001** (fetch_sample — the one contract defining a non-file input
  edge beyond stdin/transcript/caches; `Proxy: nil` transport, D14-(b) precedent);
  BC-1.06.001 was a mis-anchor (it owns cache load/save, not read scope — ADV-P2-C05)
  and is removed from this VP. DI-007 (REVISIT P7, OD-125) remains the invariant under
  test.
- **Partial coverage:** BC-1.01.009 (the render write set — the recording test observes
  opens against the same effect contracts).
- **Invariant verified:** DI-007 in force (permanent rule with REVISIT P7, OD-125);
  ARCH-09 boundary rule 3 (Env read scope has no ledger seam).

## Property Class and Verification Method

- **Class:** invariant (an absence property — the strongest form is structural).
- **Method:** static analysis + code review: (a) runtime — a recording-filesystem
  `Env.Files` wrapper records every path opened during a full render over the fault
  table and asserts membership in the allowed statusline path set and zero matches for
  the ledger file name (fails on any extra open — non-vacuous); (b) compile-time —
  the `Env` struct admits no ledger member (reflection check); (c) a CI import/grep
  lint asserting `internal/statusline` and `internal/cost` reference no ledger package
  or file language — to be carried as a hygiene leg in the ARCH-08 / cicd-setup lint
  job (currently gofmt + vet only; see Propagation note); (d) architecture
  conformance at adversarial review.
- **Honesty:** absence verified by construction + audit, not runtime proof; the P1
  structural claim is the cheapest true form of DI-007 enforcement.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Static audit | CI lint (grep/import check) + review | yes — whole-package scope | no ledger reference in render path |

## Proof Harness Skeleton

```go
func TestEnvScope_AllowedPathSet(t *testing.T) {
    for _, tc := range FaultInjectionTable { // full render, all faults
        rec := newRecordingFiles() // wrapper: records every path opened
        env := envWithFiles(rec)
        runStatusline(env, stdin, func() int { return 0 } /*exit hook*/)
        for _, p := range rec.Opened() {
            if !allowedStatuslinePaths(p) { // transcript, caches, cost history, and the
                // git widget's .git / gitdir-HEAD reads up the ancestor walk (SL:369-389)
                t.Fatalf("render opened %q: outside the allowed path set (DI-007)", p)
            }
            if isLedgerLanguage(p) { // D7 ledger file-name language
                t.Fatalf("render opened ledger-looking path %q (DI-007 leak)", p)
            }
        }
    }
}

func TestEnvScope_NoLedgerSeam(t *testing.T) {
    // Reflection over Env's members: none may name a ledger type.
    for m := 0; m < reflect.TypeOf(statusline.Env{}).NumField(); m++ {
        name := reflect.TypeOf(statusline.Env{}).Field(m).Name
        if strings.Contains(strings.ToLower(name), "ledger") {
            t.Fatalf("Env.%s: DI-007 leak", name)
        }
    }
}
// plus a CI lint leg: no ledger package/file reference under internal/statusline or internal/cost
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestEnvScope_AllowedPathSet` +
`TestEnvScope_NoLedgerSeam`; the CI import lint rides a hygiene leg in the ARCH-08 /
cicd-setup lint job (follow-up: that job currently runs gofmt + vet only).

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
