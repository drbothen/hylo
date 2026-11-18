---
document_type: verification-property
level: L4
version: "1.5"
status: draft
producer: architect
timestamp: 2026-11-18T23:30:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-00-overview.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.001.md, domain-spec/invariants.md, prd-supplements/nfr-catalog.md, prd-supplements/error-taxonomy.md, owner-decisions-log-2026-11-14.md]
input-hash: "0e9417b"
traces_to: prd.md
source_bc: BC-1.01.001
bcs: [BC-1.01.001, BC-1.02.020, BC-1.02.026, BC-1.02.027, BC-1.04.014, BC-1.04.015, BC-1.04.016, BC-1.05.004, BC-1.06.001, BC-1.07.008]
module: internal/statusline (guard), cmd/hylo
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — CP-O01..O09 (OD-156) in catalogue; added the any-stdin/panic fuzz leg with the exactly-29-bytes degraded assert (BC-1.01.001 anchoring); added the --subagent fault legs (BC-1.07.008)", "1.3 2026-11-18T09:05:00Z: ADV-P3 fixes (A2-07) — FaultInjectionTable comment names the CP-A01..A03 subagent fault rows; fuzz leg asserts the promised output-set membership ({render, 29-byte line, subagent JSON lines, zero bytes}) instead of only exit-0/non-blank, with OD-168 placing a subagent config error at zero bytes", "1.4 2026-11-18T14:05:00Z: ADV-P4 fixes — catalogue closed over the pass-3 register: CP-O10/O11 (cost-history borne, BC-1.05.007), CP-A04/A05 (BC-1.07.007) and CP-N03 (metrics-borne degrade, SL:717) added (A2-03); the never-degraded claim limited to the parse path with a coded parseFault condition — subagent renderer faults (CP-A01..A05) are EXPECTED to end in the degraded line (A2-02); frontmatter proof_method/feasibility line unmerged (A2-12); OD-167 turn-drop and OD-166 record-guard legs cross-referenced to VP-029/VP-020", "1.5 2026-11-18T23:30:00Z: pass-4 sync SC-05 — BC-1.01.002 dropped from bcs: and from Partial coverage: that contract deliberately removed VP-001 from its VP Anchors in the pass-4 burst (ADV-P4-B11 + A2-16 sibling sweep; its invalid-stdin-renders-from-{} seam is VP-005's property, whose source BC it is); VP-INDEX catalog/map reconciled in the same burst"]
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
degrades), CP-T01..T07 (transcript faults), CP-N01..N03 (NaN/inf crash paths; N03 the
metrics-borne degrade — a numeric `__name__` key sorts ahead of every `vllm:` key and
`k.startswith` raises AttributeError, SL:717), CP-O01..O11 (overflow paths, OD-156;
O10/O11 the cost-history-borne conversion sites, BC-1.05.007), and untyped panics — one
refresh of
`hylo statusline` produces at least one stdout byte and terminates with exit code 0. No
fault class exists that yields blank output or a non-zero statusline exit. Degraded
rows emit exactly the 29-byte line `\e[90mstatusline degraded\e[0m\n`. The same ladder
holds for the `--subagent` entry: faults inside the subagent renderer (CP-A01..A05,
BC-1.07.008 — A01..A03 the renderer shape faults, A04/A05 the `_fmt_tokens`/elapsed
clock OverflowErrors, BC-1.07.007) propagate to the guard and end in exactly those 29
bytes, exit 0, with no
partial row output preceding the line; parse-path faults (undecodable or non-object
stdin, subagent config error) never emit the line — they yield rows or zero bytes
(BC-1.07.003, OD-168). Two ruled consequences have their VP legs elsewhere: a
transcript-borne overflow (CP-O06..O08) skips the offending line and drops the
in-flight turn (OD-167 — leg in VP-029's parse tables), and an unconvertible cost
value is not recorded (OD-166 record guard — leg in VP-020); both still degrade the
current refresh and so are covered by this ladder.

## Source Contract

- **Primary BC:** BC-1.01.001 — Guard prints the 29-byte degraded line and exits 0.
- **Partial coverage:** BC-1.02.020
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
  entry/argv shapes asserting exit 0 and the promised output-set membership —
  stdout ∈ {normal render bytes, 29-byte degraded line, subagent JSON lines, zero
  bytes}; a subagent config error is zero bytes (OD-168) and the degraded line never
  appears via the parse path — the any-stdin leg BC-1.01.001
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
    for _, tc := range FaultInjectionTable { // one row per CP-S01..S17, T01..T07, N01..N03,
        // O01..O11, CP-C09/C10, CP-A01..A05 (subagent renderer faults, BC-1.07.008/.007)
        // + panic rows; tc.ParseFault marks parse/config-borne rows (A2-02)
        stdout, _, exit := runStatusline(tc.Env, tc.Args, tc.Stdin, tc.Files) // full argv, verb at [0]
        if exit != 0 { t.Fatalf("%s: exit = %d, want 0", tc.ID, exit) }
        if !tc.Subagent && len(stdout) == 0 { t.Fatalf("%s: blank stdout", tc.ID) }
        if tc.WantDegraded && stdout != degradedLine { // exactly 29 bytes; CP-A rows hit
            // this too — a renderer fault MUST end in the line (BC-1.07.008)
            t.Fatalf("%s: degraded row emitted %d bytes, want the 29-byte line", tc.ID, len(stdout))
        }
        assertPromisedOutputSet(t, tc.ID, tc.Subagent, tc.ParseFault, stdout) // membership, both entries
    }
}

func FuzzDegradedLadder(f *testing.F) { // BC-1.01.001 any-stdin leg; CI-seeded, nightly-extensible
    f.Fuzz(func(t *testing.T, stdin []byte, subagent bool) {
        stdout, _, exit := runStatuslineEntry(stdin, subagent)
        if exit != 0 { t.Fatalf("exit = %d, want 0", exit) }
        if !subagent && len(stdout) == 0 { t.Fatal("blank stdout on main entry") }
        // A2-02: the parse/render distinction is computable at the harness — a JSON
        // object reaches the renderer (CP-A fault regime); anything else is parse-borne
        parseFault := subagent && !isJSONObject(stdin)
        assertPromisedOutputSet(t, "fuzz", subagent, parseFault, stdout) // membership, not just non-blank
    })
}

// assertPromisedOutputSet: stdout ∈ {normal render bytes, 29-byte degraded line,
// subagent JSON rows, zero bytes}. The degraded line is EXPECTED from a subagent
// renderer fault (CP-A01..A05, BC-1.07.008); the never-degraded claim is limited to
// the parse path (A2-02): with parseFault set (undecodable/non-object stdin, or a
// subagent config error — OD-168 zero bytes) the line must not appear.
func assertPromisedOutputSet(t *testing.T, id string, subagent, parseFault bool, stdout string) {
    t.Helper()
    if subagent {
        if parseFault {
            // parse/config path: rows or zero bytes, never the degraded line
            if len(stdout) > 0 && !isNDJSONRows(stdout) {
                t.Fatalf("%s: subagent parse-path stdout outside the output set (%d bytes)", id, len(stdout))
            }
            if stdout == degradedLine {
                t.Fatalf("%s: degraded line emitted via the parse path", id)
            }
        }
        // renderer-fault regime (!parseFault): rows, zero bytes (OD-168 config error)
        // or exactly the degraded line (BC-1.07.008) — all in the promised set
        return
    }
    if len(stdout) == 0 || !(stdout == degradedLine || isRenderBytes(stdout)) {
        t.Fatalf("%s: stdout outside the promised output set", id)
    }
}
```

## Named Tests (OD-145 table where applicable)

Fault rows are the cps01..cps17, cpt01..cpt07, cpn01..cpn03, cpo01..cpo11,
cpa01..cpa05 parity-case
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
