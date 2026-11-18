---
document_type: verification-property
level: L4
version: "2.4"
status: draft
producer: architect
timestamp: 2026-11-20T12:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-00-overview.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.001.md, domain-spec/invariants.md, prd-supplements/nfr-catalog.md, prd-supplements/error-taxonomy.md, owner-decisions-log-2026-11-14.md]
input-hash: "9f62379"
traces_to: prd.md
source_bc: BC-1.01.001
bcs: [BC-1.01.001, BC-1.02.006, BC-1.02.011, BC-1.02.012, BC-1.02.014, BC-1.02.017, BC-1.02.020, BC-1.02.025, BC-1.02.026, BC-1.02.027, BC-1.02.029, BC-1.04.001, BC-1.04.004, BC-1.04.005, BC-1.04.014, BC-1.04.015, BC-1.04.016, BC-1.04.018, BC-1.05.002, BC-1.05.003, BC-1.05.004, BC-1.05.005, BC-1.05.007, BC-1.06.001, BC-1.07.007, BC-1.07.008]
module: internal/statusline (guard), cmd/hylo
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — CP-O01..O09 (OD-156) in catalogue; added the any-stdin/panic fuzz leg with the exactly-29-bytes degraded assert (BC-1.01.001 anchoring); added the --subagent fault legs (BC-1.07.008)", "1.3 2026-11-18T09:05:00Z: ADV-P3 fixes (A2-07) — FaultInjectionTable comment names the CP-A01..A03 subagent fault rows; fuzz leg asserts the promised output-set membership ({render, 29-byte line, subagent JSON lines, zero bytes}) instead of only exit-0/non-blank, with OD-168 placing a subagent config error at zero bytes", "1.4 2026-11-18T14:05:00Z: ADV-P4 fixes — catalogue closed over the pass-3 register: CP-O10/O11 (cost-history borne, BC-1.05.007), CP-A04/A05 (BC-1.07.007) and CP-N03 (metrics-borne degrade, SL:717) added (A2-03); the never-degraded claim limited to the parse path with a coded parseFault condition — subagent renderer faults (CP-A01..A05) are EXPECTED to end in the line (A2-02); frontmatter proof_method/feasibility line unmerged (A2-12); OD-167 turn-drop and OD-166 record-guard legs cross-referenced to VP-029/VP-020", "1.5 2026-11-18T23:30:00Z: pass-4 sync SC-05 — BC-1.01.002 dropped from bcs: and from Partial coverage: that contract deliberately removed VP-001 from its VP Anchors in the pass-4 burst (ADV-P4-B11 + A2-16 sibling sweep; its invalid-stdin-renders-from-{} seam is VP-005's property, whose source BC it is); VP-INDEX catalog/map reconciled in the same burst", "1.6 2026-11-18T23:45:00Z: ADV-P5 fixes (A2-10, A2-11) — the subagent renderer regime of assertPromisedOutputSet now asserts positively: the degraded line and row output never mix (DI-008), and isJSONObject is specified as Python-semantics decode (ARCH-06 ModeBytes: NaN/Infinity tokens) so byte classification cannot false-fail; BC-1.07.007 and BC-1.05.007 added to bcs: and Partial coverage (their CP-A04/A05 and CP-O10/O11 legs are this ladder's — reciprocal BC-body rows are the BC owners' fixes, ADV-P5-A2-11/C15)", "1.7 2026-11-19T00:20:00Z: pass-5 sweep C — the headline catalogue enumeration is closed over CP-A01..A05 (the --subagent renderer faults, BC-1.07.008/.007), which the opening list had left to the second sentence; Source Contract CP-A rows unchanged", "1.8 2026-11-19T12:00:00Z: pass-6 fixes (A2-01, A2-21) — assertPromisedOutputSet returns at the end of the subagent regime (the main-entry check no longer runs on subagent stdout; legal zero bytes and NDJSON rows cannot false-red); the ladder guards an empty FaultInjectionTable (P11); every fenced sketch labelled non-normative (OD-182)", "1.9 2026-11-19T18:00:00Z: pass-7 fix (A2-13) — the renderer regime states where zero tasks fall: zero tasks are a legal ZERO-BYTE output (BC-1.07.004 PC6), the renderer branch's legal set is {degraded line, NDJSON rows, zero bytes on empty task list}, and the sketch returns on len(stdout)==0 before the isNDJSONRows membership check instead of assuming isNDJSONRows(\"\")", "2.0 2026-11-20T08:00:00Z: pass-8 fixes (A2-01, A2-02) — the ruled-consequence sentence corrected: CP-O06..O08 skip the offending line and the refresh RENDERS NORMALLY (OD-156/OD-167, BC-1.03.018) — no whole-refresh degrade; the OD-166 record guard stated precisely (value not recorded, file unchanged; refresh outcome per BC-1.05.004 EC-010/EC-011 — stdin-borne usd and positive-huge api_ms degrade via CP-O10/O11, negative-huge api_ms renders normally); the closed trigger catalogue and the cpt test families gain the Windows-only CP-T09 / cpt09 leg (BC-1.01.001 PC3, error-taxonomy; T08 retired)", "2.1 2026-11-20T12:00:00Z: pass-9 fixes (A2-06, orchestrator call 4) — the closed trigger catalogue, the harness comment and the cpo test families gain CP-O12 / cpo12 (cost-pick equivalence overflow: tin and tout each below the int→float overflow bound but their exact-int sum tot at or above it enters tot * dgx_mtok — SL:626, SL:633 — on the local lane with a valid basis → OverflowError → degraded line, BC-1.02.029); the subagent parse-path oracle narrowed from 'rows or zero bytes' to EXACTLY ZERO stdout bytes (main_subagent absorbs undecodable/non-object stdin to {} → zero rows, SL:928-936; BC-1.07.003, DI-008) — 'rows or zero bytes' blessed a port rendering rows from non-object stdin", "2.2 2026-11-18T17:50:00Z: pass-10 fixes (A2-02, A2-08, B03, C2-05, C2-11) — the never-blank claim scoped to the MAIN entry (the --subagent parse-path faults legally print exactly zero bytes) and the crash register's CP-X01..X04 disposal stated (replaced by D4-EX-3, the cp-x03 exclusion, signals out of scope) (A2-08); the fuzz classifier isJSONObject specified as pyfmt.Decode ModeText semantics with the subagent stdin site's 993 depth budget — legacy reads json.load(sys.stdin) in text mode (SL:930): BOM, UTF-16/32 and depth-994 stdin decode to {} → zero bytes; ModeBytes would admit all three into the renderer regime (A2-02, orchestrator call 10); CP-O10/O11 bearer anchors corrected — stdin-borne conversion sites at the render step (BC-1.05.007, EC-011/EC-012), history-borne raise in cost_thresholds (BC-1.05.005 EC-011, SL:255), replacing the cost-history-borne/EC-009-EC-010 mis-anchor (C2-05); bcs: gains the verified degrade-row owners BC-1.02.006/.011/.012/.014/.017/.029, BC-1.04.001/.004/.005 and BC-1.05.002/.003, named with their EC rows in the Source Contract (B03/C2-11; VP-INDEX map synced by the index owner)", "2.3 2026-11-18T18:40:00Z: pass-10 residual sweep (C2-11 reciprocity) — bcs: gains BC-1.02.025 (the CP-O04 owner, EC-010) and BC-1.05.005 (the history-borne CP-O10/O11 raise in cost_thresholds, EC-011), each degrade vector verified on disk in its BC; the Source Contract partial-coverage sentence names both; VP-INDEX map and recount synced by the index owner in the same burst", "2.4 2026-11-21T09:00:00Z: pass-11 residual — bcs: gains BC-1.04.018 (its VP-table row routes the OD-160 exact-giant-int OverflowError degrade leg, PC-1 qualifier, to this ladder; ADV-P11-C2-02), the Source Contract partial-coverage sentence names the leg; VP-INDEX map and recount synced in the same burst"]
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
degrades), CP-T01..T07 plus the Windows-only CP-T09 (transcript faults; CP-T08 retired,
error-taxonomy), CP-N01..N03 (NaN/inf crash paths; N03 the
metrics-borne degrade — a numeric `__name__` key sorts ahead of every `vllm:` key and
`k.startswith` raises AttributeError, SL:717), CP-O01..O12 (overflow paths, OD-156;
O10/O11 the unconvertible-cost conversion sites — stdin-borne at the render step
(BC-1.05.007, EC-011/EC-012) and history-borne in `cost_thresholds` (BC-1.05.005
EC-011, SL:255); O12 the cost-pick
equivalence overflow — an exact-int `tin`+`tout` sum `tot` (SL:626) at or above the
int→float overflow bound entering `tot * dgx_mtok` (SL:633) on the local lane with a
valid basis → OverflowError → degraded line, BC-1.02.029), CP-A01..A05 (the
`--subagent` renderer faults — A01..A03 the renderer shape faults, BC-1.07.008;
A04/A05 the `_fmt_tokens`/elapsed-clock OverflowErrors, BC-1.07.007), and untyped panics — one
refresh of
`hylo statusline` produces at least one stdout byte and terminates with exit code 0. On
the MAIN entry, no fault class exists that yields blank output or a non-zero statusline
exit (A2-08: the claim is scoped to the main entry — the `--subagent` entry's
parse-path faults legally print exactly zero bytes, below). The taxonomy's
import/exit-time triggers CP-X01..X04 are disposed outside this surface by the crash
register itself: CP-X01/X02 are replaced by D4-EX-3 (BC-2.02.001), CP-X03 is the named
exclusion `cp-x03` (BC-1.01.001 EC-005, OD-136) and CP-X04 (signals) is out of scope.
Degraded
rows emit exactly the 29-byte line `\e[90mstatusline degraded\e[0m\n`. The same ladder
holds for the `--subagent` entry: faults inside the subagent renderer (CP-A01..A05,
BC-1.07.008 — A01..A03 the renderer shape faults, A04/A05 the `_fmt_tokens`/elapsed
clock OverflowErrors, BC-1.07.007) propagate to the guard and end in exactly those 29
bytes, exit 0, with no
partial row output preceding the line; parse-path faults (undecodable or non-object
stdin, subagent config error) never emit the line — they yield EXACTLY ZERO stdout
bytes (A2-06: main_subagent absorbs undecodable/non-object stdin to {} → zero rows,
SL:928-936; BC-1.07.003, DI-008; OD-168 for the config error). Two ruled consequences
have their VP legs elsewhere, and
neither is a whole-refresh degrade: a transcript-borne overflow (CP-O06..O08) skips
the offending line, drops the in-flight turn (OD-167 — leg in VP-029's parse tables)
and the refresh RENDERS NORMALLY — the line's bytes are consumed exactly as a JSON
decode failure and the cache is saved (OD-156, BC-1.03.018) — while an unconvertible
cost value is simply not recorded (OD-166 record guard — leg in VP-020; the file is
unchanged where legacy persisted the raw int), after which the refresh renders or
degrades exactly as BC-1.05.004 rules: the stdin-borne `usd` and a positive-huge
`api_ms` degrade via CP-O10/O11, a negative-huge `api_ms` renders normally with no
$/h segment. Every branch still emits at least one stdout byte and exits 0, so all
of them remain covered by this ladder.

## Source Contract

- **Primary BC:** BC-1.01.001 — Guard prints the 29-byte degraded line and exits 0.
- **Partial coverage:** BC-1.02.020
  (thermometer NaN crash path), BC-1.02.026 (_fmt_lines OverflowError), BC-1.02.027
  (_hm ValueError), BC-1.04.014 (sparkline NaN/+Inf), BC-1.04.015 (KV NaN), BC-1.04.016
  (row-2 NaN rendering), BC-1.06.001 (never-raise cache load/save), BC-1.05.004
  (CP-C09/C10 corrupt-cost-history fault injection — out of parity scope, still
  never-blank/exit-0 per DI-008), BC-1.07.008 (CP-A01..A03 subagent-mode faults reach
  the same guard: 29-byte line, exit 0, no partial rows), BC-1.07.007 (CP-A04/A05 the
  `_fmt_tokens`/elapsed-clock OverflowErrors ride the same ladder), BC-1.05.007
  (CP-O10/O11 the stdin-borne conversion sites at the render step, EC-011/EC-012; the
  history-borne raise at the `cost_thresholds` division is BC-1.05.005 EC-011, SL:255).
  The remaining CP-O/CP-N03 degrade-row owners ride this ladder reciprocally (pass-10
  B03/C2-11, each vector verified in its BC): BC-1.02.006 EC-010 (CP-O01), BC-1.02.011
  EC-010 and BC-1.02.012 EC-012 (CP-O02), BC-1.02.014 EC-013 (CP-O03), BC-1.02.017
  EC-010 (CP-O05), BC-1.02.025 EC-010 (CP-O04 owner), BC-1.02.029 EC-009 (CP-O12
  owner), BC-1.04.001 EC-013 / BC-1.04.004 / BC-1.04.005 EC-007 (CP-N03), BC-1.05.002
  EC-009 (CP-O11 co-owner), BC-1.05.003 EC-011 (CP-O12 co-owner) and BC-1.05.005 EC-011
  (the history-borne CP-O10/O11 raise in `cost_thresholds`). BC-1.04.018 rides the ladder
  likewise (ADV-P11-C2-02): its OD-160 exact-giant-int OverflowError degrade leg (PC-1
  qualifier) is covered by the fault-injection ladder — render output or the 29-byte
  degraded line, never blank, exit 0 (DI-008).
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
  VP-011 hunt). In the RENDERER regime zero tasks are a legal ZERO-BYTE output
  (BC-1.07.004 PC6): the renderer branch's legal set is {29-byte degraded line,
  NDJSON rows, zero bytes when the task list is empty}, so a zero-byte stdout with
  exit 0 passes there too and no membership check assumes
  `isNDJSONRows("")` (A2-13).
- **Honesty (iron law):** testable-only. This is an empirical property over an
  enumerated trigger list, not a formal proof; completeness rests on the taxonomy being
  closed (error-taxonomy.md) and Tier C fuzz hunting for unenumerated paths (VP-011).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Table test | Go test, `go test ./internal/statusline -run TestDegradedLadder` | yes — closed CP-* catalogue | every enumerated fault trigger |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestDegradedLadder_AllTriggers(t *testing.T) {
    if len(FaultInjectionTable) == 0 { // A2-21 (P11): a loop over an empty table
        t.Fatal("FaultInjectionTable is empty — the ladder checks nothing") // checks nothing
    }
    for _, tc := range FaultInjectionTable { // one row per CP-S01..S17, T01..T07 + T09, N01..N03,
        // O01..O12, CP-C09/C10, CP-A01..A05 (subagent renderer faults, BC-1.07.008/.007)
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
        // object reaches the renderer (CP-A fault regime); anything else is parse-borne.
        // A2-02 (pass-10): isJSONObject classifies with pyfmt.Decode ModeText semantics
        // and the subagent stdin site's 993 depth budget (VP-006 :48) — legacy reads
        // json.load(sys.stdin) in TEXT mode (SL:930). NaN/Infinity bare tokens are
        // accepted (both modes, ARCH-06) and reach the renderer, but a UTF-8 BOM,
        // a UTF-16/32 payload (ModeBytes detections, invalid under ModeText) or
        // depth-994 nesting fails the decode → {} → parse path → zero bytes, exactly
        // as legacy; a ModeBytes classifier would wrongly admit all three into the
        // renderer regime (undoing the pass-9 A2-06 tightening for those inputs).
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
            // parse/config path: EXACTLY ZERO bytes (A2-06) — main_subagent absorbs
            // undecodable/non-object stdin to {} → zero rows (SL:928-936, BC-1.07.003),
            // and a subagent config error is zero bytes (OD-168). The former "rows or
            // zero bytes" oracle blessed a port rendering rows from non-object stdin.
            if len(stdout) != 0 {
                t.Fatalf("%s: subagent parse-path stdout is %d bytes, want exactly 0", id, len(stdout))
            }
            if stdout == degradedLine {
                t.Fatalf("%s: degraded line emitted via the parse path", id)
            }
        }
        // renderer-fault regime (!parseFault): DI-008 — the degraded line and row
        // output never mix. Membership is asserted POSITIVELY here (A2-10: a bare
        // return would make the regime vacuous, unfuzzed): the whole stdout is
        // either exactly the 29-byte line (a renderer fault ended the refresh) or
        // NDJSON rows with no degraded line anywhere in them.
        if stdout == degradedLine {
            return
        }
        // A2-13: zero tasks emit ZERO bytes legally (BC-1.07.004 PC6) — a legal
        // renderer outcome; isNDJSONRows("") is deliberately NOT assumed.
        if len(stdout) == 0 {
            return
        }
        if !isNDJSONRows(stdout) || strings.Contains(stdout, degradedLine) {
            t.Fatalf("%s: subagent renderer stdout outside the output set or mixing rows and the degraded line (%d bytes)", id, len(stdout))
        }
        return // A2-01: the subagent regime ends here — the main-entry check below
               // is for the main entry only; legal zero bytes (OD-168 config error,
               // zero tasks, non-object stdin) and NDJSON rows are not isRenderBytes.
    }
    if len(stdout) == 0 || !(stdout == degradedLine || isRenderBytes(stdout)) {
        t.Fatalf("%s: stdout outside the promised output set", id)
    }
}
```

## Named Tests (OD-145 table where applicable)

Fault rows are the cps01..cps17, cpt01..cpt07, cpt09 (the Windows-only MSVC
localtime-domain leg, BC-1.01.001 PC3), cpn01..cpn03, cpo01..cpo12,
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
