---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T14:58:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.03.001.md, behavioral-contracts/ss-01/BC-1.03.003.md, behavioral-contracts/ss-01/BC-1.03.005.md, behavioral-contracts/ss-01/BC-1.03.007.md, behavioral-contracts/ss-01/BC-1.03.016.md, prd-supplements/test-vectors.md, prd-supplements/nfr-catalog.md]
input-hash: "0cb9a48"
traces_to: prd.md
source_bc: BC-1.03.016
bcs: [BC-1.03.001, BC-1.03.002, BC-1.03.003, BC-1.03.004, BC-1.03.005, BC-1.03.006, BC-1.03.007, BC-1.03.008, BC-1.03.009, BC-1.03.010, BC-1.03.011, BC-1.03.012, BC-1.03.013, BC-1.03.014, BC-1.03.015, BC-1.03.016, BC-1.03.017, BC-1.03.018, BC-1.03.019, BC-1.03.020, BC-1.03.021]
module: internal/statusline (transcript*.go, mixcache.go, session.go)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-18T09:16:00Z: ADV-P3 fix (A2-18) — int-transcript_path property recast per OD-161/BC-1.03.015 PC3: truthy int means no transcript, no descriptor I/O (the fd-semantics wording predates the ruling)", "1.3 2026-11-18T14:58:00Z: ADV-P4 fixes — OD-167 leg added: a transcript line whose numbers overflow float64 conversion is skipped whole AND drops the in-flight turn (cur → null), overlapping the D4-EX-2 skip discipline (A2-03); skeleton comparison made compile-plausible: parser state holds slices, so reflect.DeepEqual replaces struct equality; runStatusline call shape unified (A2-22)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-029: Transcript parsing family — turn machine and read-step totals

## Property Statement

The transcript parser matches the oracle-pinned tables for: no-path state, mix-cache
name/reset rules (mixv6), 512 KB read steps with long-line completion over two
refreshes, bytes.splitlines + per-line json.loads consumption, usage dedup (memory
256), usage accumulation across int/float/big-int, the 20,000-excess rebuild rule,
compact_boundary resets, composition per block from json.dumps lengths, the last-turn
rate machine, first-line usage, sanitized mix-cache sid, text/thinking block types,
int-`transcript_path` means no transcript — hylo performs no descriptor I/O (OD-161,
BC-1.03.015 PC3), the exhaustive 20-row turn machine (T13
oracle-confirmed, OD-143), turn identity ignoring seen_ids, cur with t0-null/non-numeric
out verbatim; the reset write-scope property (after the reset step `size == off`, the
step performs zero `Save` calls — fake-`CacheStore` table, BC-1.03.002 row 2); the
OD-167 overflow-skip leg — a transcript line whose numbers overflow float64 conversion
(CP-O06..O08) is skipped whole AND drops the in-flight turn (`cur` → null), the ruled
sharpening of the D4-EX-2 skip discipline; plus the
D4-EX-2 wrong-shape rows (VP-013).

## Source Contract

- **Primary BC:** BC-1.03.016 — Turn-machine exhaustive table (20 rows).
- **Partial coverage:** BC-1.03.001..021 (all twenty-one S1.03 contracts; the D4-EX-2
  trio primarily in VP-013).
- **Invariant verified:** NFR-005 caps (256 dedup [SL:1153 `ids[-256:]`], 512 KB steps
  [`_READ_CAP`], 32-point histories [SL:350 `hist[-32:]`] — joint with VP-031);
  OD-143 (T13 confirmed by oracle, row kept); OD-32 (poisoned cur.out reader rule).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — the 20-row turn-machine table, read-step matrices
  (short+long completion), dedup/accumulation corners, rebuild-rule boundary rows;
  consumed end-to-end by corpus parity.
- **Honesty:** testable-only; state-machine exhaustiveness is table-bounded.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Turn table | Go test, 20 canonical rows | yes | full state machine |
| Read-step matrices | Go test | yes | completion across refreshes |
| Corpus parity | VP-009 | corpus-bounded | end-to-end bytes |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestTurnMachine_ExhaustiveTable(t *testing.T) {
    for _, r := range TurnTable20 {
        st := advance(newState(r.Seed), r.Events)
        // A2-22: parser state holds slices — struct equality does not compile;
        // deep equality is the observable.
        if !reflect.DeepEqual(st, r.Want) { t.Fatalf("row %s: %+v", r.ID, st) }
    }
}

func TestOverflowSkip_DropsInFlightTurn(t *testing.T) { // OD-167 leg (A2-03)
    st := newState(seedWithOpenTurn(curOutBig)) // in-flight turn open, cur set
    st.ApplyLine(overflowLine("cache_creation_input_tokens", strings.Repeat("9", 310))) // 310+-digit exact int
    if !st.CurIsNull() { // the ruled consequence: the in-flight turn is dropped
        t.Fatal("overflow skip kept the in-flight turn (OD-167)")
    }
    if st.CommittedMutated(seedWithOpenTurn(curOutBig)) {
        t.Fatal("overflow skip partially mutated committed state")
    }
}

func TestReset_WriteScope(t *testing.T) {
    st := newStore(t, seedMixCache(off)) // off > 0 forces the reset step
    st.Refresh(transcriptL1)
    if st.Size() != st.Offset() { t.Fatal("size != off after reset") }
    if st.SaveCalls() != 0 { t.Fatal("reset step performed a Save (write scope exceeded)") }
}
```

## Named Tests (OD-145 table where applicable)

`transcript` parity family; in-tree `TestTurnMachine_ExhaustiveTable`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | 20 rows + step matrices | canonical |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Weeks | table volume; largest S1 family |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
