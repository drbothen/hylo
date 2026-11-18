---
document_type: verification-property
level: L4
version: "1.7"
status: draft
producer: architect
timestamp: 2026-11-18T21:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-04-data-files.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.05.004.md, behavioral-contracts/ss-01/BC-1.05.006.md, behavioral-contracts/ss-01/BC-1.05.009.md, owner-decisions-log-2026-11-14.md]
input-hash: "232daeb"
traces_to: prd.md
source_bc: BC-1.05.004
bcs: [BC-1.05.004, BC-1.05.006, BC-1.05.009]
module: internal/cost
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fixes — honest title (A2-03); wrong-type shapes out of parity scope, exclusion id OD-160; numeric-sid self-exclusion holds (C2-06)", "1.3 2026-11-18T14:50:00Z: ADV-P4 fix (A2-03/OD-169) — OD-166 record-guard leg added: record_cost SKIPS a cost value whose usd or api_ms cannot convert to float (legacy persisted the raw int); the current refresh still degrades; the resulting cache-byte divergence cites exclusion id OD-166 with its own table test TestCostHistory_OD166_RecordGuard and its own VP-012 closure row — no 'rides D4-EX-2' wording", "1.4 2026-11-18T23:45:00Z: ADV-P5 fix (A2-26) — the OD-166 leg is exercised through the RENDERED refresh over both guard fields (usd and api_ms): the P1 cost.Record signature takes no api_ms and a library call renders nothing, so file-unchanged and the E-REN-002 degrade are observed in the rendered bytes", "1.5 2026-11-19T12:00:00Z: pass-6 fixes (C2-04, A2-02: the OD-166 guard legs put the unconvertible exact int on STDIN (BC-1.05.004 EC-010/011) over a valid history; outcomes are field-specific (usd degrades per EC-010, api_ms renders normally per EC-011); a seeded-history huge value is the OD-160/CP-O10/O11 class)", "1.6 2026-11-20T08:00:00Z: pass-8 fixes (C2-06, C2-07) — the record-guard refresh outcome stated field- AND sign-specific per BC-1.05.004 PC1: usd degrades (CP-O10 at the .2f site SL:616, before the $/h math SL:622), POSITIVE huge api_ms passes the gate and degrades via CP-O11, NEGATIVE huge api_ms fails the gate and renders normally (EC-011); sketch gains the positive-api_ms row; the BC-1.05.004/006 testing/quick rows gained a matching property leg (TestCostRecord_QuickProperties: at-most-one-write under a fake clock; no duplicate keys), Method/Proof Method/Named Tests updated", "1.7 2026-11-18T21:00:00Z: pass-11 fix (C2-07) — the field-/sign-specific refresh-outcome citations moved from BC-1.05.004 PC1 to PC4 in the statement and the sketch comment: pass-9 (ADV-P9-C2-03) relocated the OD-166 convertibility skip out of the PC1 guard to the write step (PC4), and PC1 now explicitly says the skip is not part of the guard; the 1.6 history entry keeps its as-of-pass-8 figures"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-020: Cost-history parse failure — legacy reload; next record regenerates the file

## Property Statement

An unreadable or truncated `cost-history.json` is handled exactly as legacy handles it
(`load_cache`, SL:190-197: any open/parse failure returns `{}`): the load yields an
empty in-memory history, and the next throttle-through `record_cost` saves the whole
(now one-session) history, overwriting the corrupt file — with the exact legacy JSON
format (separators, ensure_ascii, int/float distinction, OD-138's oracle-pinned NaN usd
bytes) regenerated from the loaded state. The title is deliberately honest: the corrupt
history **is** wiped by the next successful record, exactly as the oracle wipes it —
the claim is "no loss wider than legacy's" (at most the unreadable bytes are lost),
not "no wipe". Anti-pattern AP-16 (a cache parse failure wipes *all* history on the
next write) is disposed by matching legacy's reload-from-scratch semantics, with no
silent format drift. Valid-JSON wrong-type shapes are a different class and outside
this VP's parity scope: legacy raises on them (CP-C09/C10 crash paths, BC-1.05.004
EC-008 — degraded, no write); they are foreign-cache forms carrying exclusion id
**OD-160** (ruling Q-b). The throttle is strict `<`; numeric sids write one
string-form key (OD-30) under which the throttle applies and self-exclusion **holds**
(BC-1.05.006 PC2/PC3). Record guard (OD-166): a cost value on the refresh's **stdin**
usage block — field `usd` or `api_ms` (BC-1.05.004 EC-010/EC-011) — that cannot
convert to float (magnitude >= 2**1024 - 2**970 as an exact int) is **not recorded** —
the file is unchanged, where legacy persisted the raw int. The refresh outcome is
field- AND sign-specific (BC-1.05.004 PC4): an unconvertible `usd` degrades the
current refresh (EC-010 — the `.2f` format site SL:616 raises CP-O10/BC-1.05.007,
E-REN-002, before the $/h math at SL:622); a huge `api_ms` passes or fails the
`>= burn_min_api_ms` gate BY SIGN — a POSITIVE huge `api_ms` passes the gate and
degrades the current refresh via CP-O11 (BC-1.05.007), while a NEGATIVE huge
`api_ms` fails it (`-(2**1024) >= burn_min_api_ms` is false) and renders normally
with no $/h segment (EC-011, BC-1.05.002 PC4).
A huge value SEEDED INTO the history file is a different input path: it is the
OD-160 foreign-history class exercising the CP-O10/O11 conversion sites
(BC-1.05.005/BC-1.05.007, VP-001's fault ladder), where the step-7c `record_cost`
write precedes `cost_thresholds` and may legitimately rewrite the file. The
stdin-borne divergence cites exclusion
id **OD-166** with its own table test (`TestCostHistory_OD166_RecordGuard`) and its
own VP-012 closure row — it does not ride D4-EX-2 and is not an OD-156 case.

## Source Contract

- **Primary BC:** BC-1.05.004 — record_cost throttled write.
- **Partial coverage:** BC-1.05.006 (numeric sid: throttle and self-exclusion, single
  string-form key), BC-1.05.009 (record_cost exact JSON format).
- **Invariant verified:** OD-124 (status line owns the format; guests honor it), OD-138
  (NaN usd pinned from the oracle), AP-16 disposition (pass-8 anti-pattern register,
  porting-decision §8.2 item 5).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — poisoned-file fault injection: malformed/truncated
  JSON, wrong permissions, plus load-succeeds rows (NaN-bearing history); assert the
  load yields an empty history and the next record regenerates the exact legacy-format
  file from scratch (the corrupt bytes are replaced, as the oracle replaces them);
  format rows compare exact bytes against oracle-pinned expectations. Valid-JSON
  wrong-type shapes are excluded from the table (OD-160, see above). Plus two Go
  property tests (testing/quick) owning the rows BC-1.05.004/BC-1.05.006 route here
  (ADV-P8-C2-07): under a fake clock + fake store, two refreshes less than
  `record_throttle_s` apart with a `cc` entry produce at most one write
  (BC-1.05.004); and no Go-written cost history contains a duplicate key
  (BC-1.05.006).
- **Honesty:** testable-only (filesystem seam); byte format is oracle-pinned.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Poisoned-file tables | Go test, temp dirs | yes — enumerated malformation classes | legacy-reload semantics + write-format rows |
| Byte pins | oracle-pinned expectations | yes | record_cost JSON format incl. NaN usd |
| Throttle/keys property | Go property test (testing/quick), fake clock + fake store | generated refresh sequences | at-most-one-write (BC-1.05.004); no duplicate keys (BC-1.05.006) |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestCostHistory_ParseFailure_LegacyReloadSemantics(t *testing.T) {
    dir := tempCacheDir(t)
    writeFile(dir, "cost-history.json", garbage) // unreadable/truncated — load => {}
    hist := cost.Load(dir)
    if !hist.Empty() { t.Fatal("poisoned load not empty") }
    cost.Record(hist, session, usd) // throttle-through record
    got := readFile(dir, "cost-history.json")
    if !parsesAsJSON(got) { t.Fatal("corrupt file not regenerated (legacy reloads from scratch, SL:190-197)") }
    if got != legacyOneSessionBytes(session, usd) {
        t.Fatal("regenerated bytes drift from the legacy format (AP-16)")
    }
    // valid-JSON wrong-type shapes are NOT in this table: legacy raises on them
    // (CP-C09/C10, BC-1.05.004 EC-008) — foreign-cache forms, exclusion id OD-160.
}

func TestCostHistory_OD166_RecordGuard(t *testing.T) { // OD-166/OD-169 record guard
    // C2-04 (with A2-02): the guard checks the value on STDIN (BC-1.05.004
    // EC-010/011) — NOT a value seeded into the history file. A seeded huge history
    // value is the OD-160/CP-O10/O11 class, where the 7c write legitimately happens
    // first; asserting "file unchanged" there would fail a correct implementation.
    // The guard covers usd OR api_ms, so both legs are exercised THROUGH THE
    // RENDERED REFRESH over a VALID seeded history.
    for _, tc := range []struct {
        name    string
        stdin   string // usage block bytes carrying the unconvertible exact int
        wantOut string // EC-010: degraded line; EC-011: renders normally
    }{
        {"huge stdin usd", usageBlockUSD(exactIntAboveFloat64Max), degradedLine}, // EC-010: degrades (CP-O10 at the .2f site SL:616, before the $/h math SL:622)
        {"huge positive stdin api_ms", usageBlockAPIMS(exactPosIntAboveFloat64Max), degradedLine}, // BC-1.05.004 PC4 (C2-06): passes the gate, degrades via CP-O11
        {"huge negative stdin api_ms", usageBlockAPIMS(exactNegIntAboveFloat64Max), normalRender}, // EC-011: fails the gate, renders normally, no $/h segment
    } {
        dir := tempCacheDir(t)
        seedValidHistory(dir) // the history itself is valid — the fault is on stdin
        out := renderRefresh(dir, tc.stdin)
        if !fileUnchanged(dir, "cost-history.json") {
            t.Fatalf("%s: unconvertible stdin cost recorded — guard skipped nothing", tc.name)
        }
        if out != tc.wantOut { // field- and sign-specific (C2-06): usd and positive
            // huge api_ms degrade; negative huge api_ms renders normally
            t.Fatalf("%s: refresh outcome %q, want %q", tc.name, out, tc.wantOut)
        }
    }
}

func TestCostRecord_QuickProperties(t *testing.T) { // ADV-P8-C2-07: the testing/quick
    // rows BC-1.05.004 (throttle) and BC-1.05.006 (duplicate keys) route here.
    err := quick.Check(func(intervalLessThrottle bool, sids []PyValue) bool {
        store := newFakeStore()
        clock := newFakeClock()
        recordAt(store, clock, sid("t"), usd(2.0), intervalLessThrottle) // first record
        clock.Advance(lessThan(recordThrottleMS()))                      // second record sooner
        writes := store.WriteCount("cost-history.json")                  // than the throttle
        if writes > 1 { return false } // BC-1.05.004: at most one write within the throttle
        return noDuplicateKeys(store.Contents("cost-history.json")) // BC-1.05.006
    }, nil)
    if err != nil { t.Fatalf("cost-record quick properties violated: %v", err) }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as
`TestCostHistory_ParseFailure_LegacyReloadSemantics`,
`TestCostHistory_OD166_RecordGuard` (OD-166 record guard), and
`TestCostRecord_QuickProperties` (the testing/quick rows from BC-1.05.004/006,
ADV-P8-C2-07); format rows additionally pinned by the `swap` cost family (VP-019).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Enumerated malformations | small |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | OD-30 single-key rows included |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
