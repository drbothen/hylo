---
document_type: verification-property
level: L4
version: "1.6"
status: draft
producer: architect
timestamp: 2026-11-19T18:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.04.002.md, behavioral-contracts/ss-01/BC-1.04.004.md, behavioral-contracts/ss-01/BC-1.04.009.md, behavioral-contracts/ss-01/BC-1.04.014.md, behavioral-contracts/ss-01/BC-1.04.020.md, prd-supplements/test-vectors.md]
input-hash: "c530f76"
traces_to: prd.md
source_bc: BC-1.04.002
bcs: [BC-1.04.001, BC-1.04.002, BC-1.04.003, BC-1.04.004, BC-1.04.005, BC-1.04.006, BC-1.04.007, BC-1.04.008, BC-1.04.009, BC-1.04.010, BC-1.04.011, BC-1.04.012, BC-1.04.013, BC-1.04.014, BC-1.04.015, BC-1.04.016, BC-1.04.017, BC-1.04.018, BC-1.04.019, BC-1.04.020, BC-1.04.021]
module: internal/statusline (sample.go, row2.go, sparkline.go, telemetry.go)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fix — OD-130 not verified in P1; P1 asserts legacy ±Inf behavior per BC-1.04.014 (OD-157, A2-01)", "1.3 2026-11-18T09:17:00Z: ADV-P3 fix (C2-08) — the legs the BC VP-tables route here now exist in this document: testing/quick for-all leg (BC-1.04.002/004/006/007/009/013/017/021 invariants) and Tier C differential-fuzz rows (BC-1.04.001 fetch/redirect sampling, BC-1.04.009 sparkline scale), with skeleton", "1.4 2026-11-18T14:20:00Z: ADV-P4 fix (A2-05) — quick.Values filler rewritten to the assigning form args[0] = reflect.ValueOf(genRow2State(r))", "1.5 2026-11-19T12:00:00Z: pass-6 fixes (A2-12, OD-181: quick-leg oracle respelled as harness re-derivation; TestMetricsClient_OD181_TransportTable transport rows (OD-181 rider per VP-012))", "1.6 2026-11-19T18:00:00Z: pass-7 fix (ADV-P7-C2-05) — the transport table's wire fake is a raw net.Listener (or hijacked connection), not httptest: httptest canonicalises header order into a map and writeSubset trims values, so it can neither replay urllib's order nor send a trailing-space Location value"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-030: Row-2 telemetry family — TTL machine, freshness ladder, NaN crash paths

## Property Statement

Row-2 telemetry matches the oracle-pinned tables: fetch_sample (query, 1.5 s timeout,
first-wins), get_sample TTL / KEEP_DEAD state machine and pinned 11-step sequence with
cache key order, history point rules (90 s cap, 2 s gap) with `_norm_pt`, freshness
ladder + stale suffix, health dot (green-while-success rule), queue/KV/throughput/
sparkline/TTFT/power/idle segments incl. format boundaries, mine segment, VM fetch
whenever ROWS >= 2, and the NaN/+Inf crash paths (CP-N01/N02) with wall-colour
mismatch quirk.

## Source Contract

- **Primary BC:** BC-1.04.002 — get_sample TTL / KEEP_DEAD state machine.
- **Partial coverage:** BC-1.04.001..021 (all twenty-one S1.04 contracts; NaN crash
  paths also ride VP-001).
- **Invariant verified:** NFR-005 (32-point metric histories — joint with VP-031).
  ±Inf disposition (OD-157): P1 verifies the **legacy** behavior of BC-1.04.014 —
  +Inf on the `v`/`f` traces degrades (CP-N02), -Inf on any trace clamps to `▁`, and
  +Inf on the `k` trace is safe — and NOT OD-130 (±Inf treated as unknown), which takes
  effect only after cutover (P6) and has no verification claim in P1.


## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — the 11-step get_sample sequence table, TTL/KEEP_DEAD
  transition matrices, freshness-ladder rows, sparkline glyph/color/scale tables, NaN/inf
  fault rows; PLUS the legs the BC VP-tables route here (C2-08): testing/quick
  for-all legs for the row-2 invariants marked "property proof" in
  BC-1.04.002/004/006/007/009/013/017/021 (TTL/freshness monotonicity, redirect
  visited-cap sampling behaviour, cells caps, sparkline scale bounds, TTFT
  rounding bands, idle-age ordering, power-format invariants — the quick-leg oracle
  INDEPENDENTLY RE-DERIVES each BC rule in the harness; a canonical table cannot
  oracle randomly generated states, the VP-041 A2-08 lesson), and Tier C
  differential-fuzz rows for the
  surfaces marked "fuzz" in BC-1.04.001 (fetch/redirect sampling) and BC-1.04.009
  (sparkline scale), budgeted by `HYLO_PARITY_FUZZSECONDS`, same oracle discipline
  as VP-011. The metrics-client transport table (`TestMetricsClient_OD181_TransportTable`,
  OD-181 rider per VP-012) pins hylo's plain-http client behaviour here: urllib's
  exact header set/order, the empty-`Location` urljoin rule, the visited-cap worst
  case, and the OD-181 non-http/https table rows (no sample / OS trust store). The
  wire fake for the transport table is a RAW `net.Listener` (or a hijacked
  connection) writing hand-crafted HTTP/1.1 bytes — NOT `httptest`: `httptest`
  canonicalises incoming headers into a map, so urllib's header ORDER is
  unobservable, and its `Header.writeSubset` trims values with
  `textproto.TrimString`, so it can neither replay urllib's order nor send a
  `Location: /x␠` trailing-space value (ADV-P7-C2-05).
- **Honesty:** testable-only; the 1.5 s timeout and first-wins semantics are
  fake-server integration rows.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Sequence table | Go test, 11 canonical steps | yes | get_sample pinned sequence |
| Segment tables | Go test | yes | all row-2 segments x freshness states |
| Fault rows | Go test (httptest fake for the status/body fault rows; RAW `net.Listener` for the transport table, ADV-P7-C2-05) | yes | down/500/garbage/±Inf metrics |
| Property legs | `testing/quick`, *quick.Config with Values | sized | BC-1.04.002/004/006/007/009/013/017/021 for-all rows |
| Differential fuzz | parity harness, `HYLO_PARITY_FUZZSECONDS` | budget-bounded | BC-1.04.001, BC-1.04.009 |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestGetSample_Pinned11StepSequence(t *testing.T) {
    for _, s := range SampleSequence11 {
        got := advanceSample(newFakeMetrics(), s.Steps...)
        if got != s.Want { t.Fatalf("step %d: %+v", s.ID, got) }
    }
}

func TestRow2Props_QuickLeg(t *testing.T) { // C2-08: for-all rows routed here by the BCs
    cfg := &quick.Config{MaxCount: 500, Values: func(args []reflect.Value, r *rand.Rand) {
        // A2-05: assign the arg; args arrives as zero reflect.Values, so
        // Elem().Set would panic (invalid/not-addressable).
        args[0] = reflect.ValueOf(genRow2State(r)) // generated TTL/freshness/sparkline states
    }}
    if err := quick.Check(func(st row2State) bool {
        // A2-08: the predicates are STRUCTURAL re-derivations of the BC-1.04.x rules
        // (TTL monotonicity, ladder ordering, scale bounds) — the BC's canonical table
        // pins only bounded corners and cannot oracle randomly generated states.
        return row2InvariantsHold(st)
    }, cfg); err != nil {
        t.Fatalf("row-2 invariant violated: %v", err)
    }
}
// BC-1.04.001 / BC-1.04.009 fuzz rows ride TestParityTierC_DiffFuzz under
// internal/parity (HYLO_PARITY_FUZZSECONDS budget, VP-011 oracle discipline).
```

## Named Tests (OD-145 table where applicable)

`row2` parity family (ARCH-07 case-id grammar) + the metrics-mode rows
(down/500/garbage) of the ARCH-07 case model; in-tree
`TestGetSample_Pinned11StepSequence`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Sequence + segment tables | bounded |
| Proof complexity | N/A | |
| Tool support | Full | httptest fake + raw `net.Listener` (transport table, ADV-P7-C2-05) |
| Estimated proof time | Weeks | segment volume |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
