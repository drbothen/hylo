---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-00-overview.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.001.md, domain-spec/invariants.md, prd-supplements/nfr-catalog.md, prd-supplements/error-taxonomy.md, owner-decisions-log-2026-11-14.md]
input-hash: "bbb0fcf"
traces_to: prd.md
source_bc: BC-1.01.001
bcs: [BC-1.01.001, BC-1.01.002, BC-1.02.020, BC-1.02.026, BC-1.02.027, BC-1.04.014, BC-1.04.015, BC-1.04.016, BC-1.05.004, BC-1.06.001, BC-1.07.008]
module: internal/statusline (guard), cmd/hylo
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — CP-O01..O09 (OD-156) in catalogue; added the any-stdin/panic fuzz leg with the exactly-29-bytes degraded assert (BC-1.01.001 anchoring); added the --subagent fault legs (BC-1.07.008)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-001: Never-blank, exit-0 rendering under every fault trigger

## Property Statement

For every fault trigger in the closed error taxonomy — CP-S01..S17 (typed widget/parser
degrades), CP-T01..T07 (transcript faults), CP-N01/N02 (NaN/inf crash paths),
CP-O01..O09 (overflow paths, OD-156), and untyped panics — one refresh of
`hylo statusline` produces at least one stdout byte and terminates with exit code 0. No
fault class exists that yields blank output or a non-zero statusline exit. Degraded
rows emit exactly the 29-byte line `\e[90mstatusline degraded\e[0m\n`. The same ladder
holds for the `--subagent` entry: faults inside the subagent renderer (CP-A01..A03,
BC-1.07.008) propagate to the guard and end in exactly those 29 bytes, exit 0, with no
partial row output preceding the line.

## Source Contract

- **Primary BC:** BC-1.01.001 — Guard prints the 29-byte degraded line and exits 0.
- **Partial coverage:** BC-1.01.002 (invalid stdin renders from {}), BC-1.02.020
  (thermometer NaN crash path), BC-1.02.026 (_fmt_lines OverflowError), BC-1.02.027
  (_hm ValueError), BC-1.04.014 (sparkline NaN/+Inf), BC-1.04.015 (KV NaN), BC-1.04.016
  (row-2 NaN rendering), BC-1.06.001 (never-raise cache load/save), BC-1.05.004
  (CP-C09/C10 corrupt-cost-history fault injection — out of parity scope, still
  never-blank/exit-0 per DI-008), BC-1.07.008 (CP-A01..A03 subagent-mode faults reach
  the same guard: 29-byte line, exit 0, no partial rows).
- **Invariant verified:** DI-008 (rendering never fails; degraded ladder ends in
  one-line output, exit 0). NFR-002 (100% of CP-* triggers, fault-injection table).

## Property Class and Verification Method

- **Class:** safety.
- **Method:** unit/table test — exhaustive fault-injection table over the closed
  trigger catalogue, one row per CP-* id plus the CP-C09/C10 corrupt-history shapes
  (BC-1.05.004 EC-008; in coverage for never-blank/exit-0 even though out of parity
  scope), asserting `len(stdout) >= 1 && exit == 0` and, for degraded rows, the exact
  29 bytes; plus a CI-seeded fuzz leg (`FuzzDegradedLadder`) over arbitrary stdin and
  entry/argv shapes asserting exit 0 and stdout ∈ {normal render bytes, 29-byte
  degraded line, subagent JSON lines or zero bytes} — the any-stdin leg BC-1.01.001
  anchors (formerly attributed to Tier C; it is this in-tree fuzz, and Tier C's
  VP-011 hunt).
- **Honesty (iron law):** testable-only. This is an empirical property over an
  enumerated trigger list, not a formal proof; completeness rests on the taxonomy being
  closed (error-taxonomy.md) and Tier C fuzz hunting for unenumerated paths (VP-011).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test | Go test, `go test ./internal/statusline -run TestDegradedLadder` | yes — closed CP-* catalogue | every enumerated fault trigger |

## Proof Harness Skeleton

```go
func TestDegradedLadder_AllTriggers(t *testing.T) {
    for _, tc := range FaultInjectionTable { // one row per CP-S01..S17, T01..T07, N01, N02, O01..O09, CP-C09/C10 + panic rows
        stdout, _, exit := runStatusline(tc.Env, tc.Stdin, tc.Files)
        if exit != 0 { t.Fatalf("%s: exit = %d, want 0", tc.ID, exit) }
        if len(stdout) == 0 { t.Fatalf("%s: blank stdout", tc.ID) }
        if tc.WantDegraded && stdout != degradedLine { // exactly 29 bytes
            t.Fatalf("%s: degraded row emitted %d bytes, want the 29-byte line", tc.ID, len(stdout))
        }
    }
}

func FuzzDegradedLadder(f *testing.F) { // BC-1.01.001 any-stdin leg; CI-seeded, nightly-extensible
    f.Fuzz(func(t *testing.T, stdin []byte, subagent bool) {
        stdout, _, exit := runStatuslineEntry(stdin, subagent)
        if exit != 0 { t.Fatalf("exit = %d, want 0", exit) }
        if !subagent && len(stdout) == 0 { t.Fatal("blank stdout on main entry") }
    })
}
```

## Named Tests (OD-145 table where applicable)

Fault rows are the cps01..cps17, cpt01..cpt07, cpn01, cpn02, cpo01..cpo09 parity-case
families (ARCH-07 case grammar); the degraded line itself is pinned by BC-1.01.001
table tests; the fuzz leg is named `FuzzDegradedLadder` (in-tree, `cmd/hylo` tests).
See also VP-003 for the degraded-write-failure case (`cp-x03`) and VP-005 for the
any-stdin decode-totality fuzz.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Small, closed | one row per taxonomied trigger |
| Proof complexity | N/A | enumeration, not deduction |
| Tool support | Full | plain Go tables |
| Estimated proof time | Hours | table authoring dominates |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
