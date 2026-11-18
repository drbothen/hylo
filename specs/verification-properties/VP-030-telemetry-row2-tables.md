---
document_type: verification-property
level: L4
version: "1.10"
status: draft
producer: architect
timestamp: 2026-11-21T12:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.04.002.md, behavioral-contracts/ss-01/BC-1.04.004.md, behavioral-contracts/ss-01/BC-1.04.009.md, behavioral-contracts/ss-01/BC-1.04.014.md, behavioral-contracts/ss-01/BC-1.04.020.md, prd-supplements/test-vectors.md]
input-hash: "7dc5b3f"
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
modified:
  - "1.1 2026-11-17: ADV-P1 pass-1 fixes"
  - "1.2 2026-11-17: ADV-P2 fix — OD-130 not verified in P1; P1 asserts legacy ±Inf behavior per BC-1.04.014 (OD-157, A2-01)"
  - "1.3 2026-11-18T09:17:00Z: ADV-P3 fix (C2-08) — the legs the BC VP-tables route here now exist in this document: testing/quick for-all leg (BC-1.04.002/004/006/007/009/013/017/021 invariants) and Tier C differential-fuzz rows (BC-1.04.001 fetch/redirect sampling, BC-1.04.009 sparkline scale), with skeleton"
  - "1.4 2026-11-18T14:20:00Z: ADV-P4 fix (A2-05) — quick.Values filler rewritten to the assigning form args[0] = reflect.ValueOf(genRow2State(r))"
  - "1.5 2026-11-19T12:00:00Z: pass-6 fixes (A2-12, OD-181: quick-leg oracle respelled as harness re-derivation; TestMetricsClient_OD181_TransportTable transport rows (OD-181 rider per VP-012))"
  - "1.6 2026-11-19T18:00:00Z: pass-7 fix (ADV-P7-C2-05) — the transport table's wire fake is a raw net.Listener (or hijacked connection), not httptest: httptest canonicalises header order into a map and writeSubset trims values, so it can neither replay urllib's order nor send a trailing-space Location value"
  - "1.7 2026-11-19T22:00:00Z: pass-8 fixes (ADV-P8-C2-08: the testing/quick for-all legs now cover the five BCs the pass-8 recount added - BC-1.04.003/008/015/018/019 predicates stated normatively in the Property Statement; ADV-P8-C2-09: the transport table respelled from 'pins hylo's plain-http client behaviour' to the minimal HTTP/1.1 client over plain http AND https-through-crypto/tls per BC-1.04.001 PC1, only the parity CORPUS being plain http, OD-181; ADV-P8-A2-19: Named Tests gains TestMetricsClient_OD181_TransportTable)"
  - "1.8 2026-11-20T12:30:00Z: pass-8 residual (C2-05 seam): Proof Method and Feasibility tables respelled — every metrics fake in this document is a RAW net.Listener fake, the status/body fault rows included; not httptest, whose server canonicalises headers into a map and trims values"
  - "1.9 2026-11-20T15:00:00Z: pass-9 fixes (ADV-P9-A2-04, orchestrator call 3; ADV-P9-A2-05) — the BC-1.04.003 history for-all restated: caps named by their registered keys (statusline.sparkline.history_cap, statusline.sparkline.max_age_s), and the pruning invariant holds on the SUCCESS path only — the fetch-failure path re-saves the stored history verbatim, unpruned (SL:327, SL:353-355; BC-1.04.003 Inv 2); VP-031 de-cited from the quick leg (the BC de-cited it in pass 8; the joint-routing residue corrected) | frontmatter: the line-29 invalid escape (a backslash before a plain apostrophe) repaired to the bare apostrophe (YAML repair, orchestrator call 5); no history entry lost"
  - "1.10 2026-11-21T12:00:00Z: pass-10 fix (ADV-P10-C2-09, generator side; the BC-1.04.018 PC side is the BC-row owner's) — the BC-1.04.018 quick-leg generator narrowed: sess_rate[0] is generated as bool or float-range number only; the exact-giant-int cache shape that overflows CPython's int→float conversion at the .0f format (measured OverflowError at 10**400) is a foreign mix-cache state (OD-160) riding VP-001's degrade ladder, excluded from this presence/dimming leg | input-hash refreshed to 7dc5b3f (hook-flagged drift)"

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
mismatch quirk. The testing/quick for-all legs cover every row-2 invariant whose BC
VP-table routes a "Go property test (testing/quick)" row here — BC-1.04.002/003/
004/006/007/008/009/013/015/017/018/019/021 — including, for the five added on the
pass-8 recount (ADV-P8-C2-08): saved history length <= `statusline.sparkline.history_cap`
with every saved point
satisfying `now - t < statusline.sparkline.max_age_s` or being the new point — on the
SUCCESS path only; the fetch-failure path re-saves the stored history verbatim,
unpruned (SL:327, SL:353-355; BC-1.04.003 Inv 2) (BC-1.04.003 quick leg; VP-031
de-cited from this row, pass-9 ADV-P9-A2-05); the box segment never ending in a space (BC-1.04.008); degrade-iff-NaN
for the KV gauge (BC-1.04.015, finite/±Inf rows table-equal legacy); segment
presence and dimming equal to legacy for every JSON value shape of `mix[7]`
whose `sess_rate[0]` is a bool or a float-range number — the generator excludes
the foreign exact-giant-int cache shape whose rendering overflows CPython at
`f"{x:.0f}"` (measured: 10**400 raises OverflowError, 10**308 formats), a degrade
site on VP-001's ladder (OD-160), not a presence/dimming case (BC-1.04.018,
ADV-P10-C2-09); and TTFT text equal to CPython for random doubles in [0, 10^4] and
all tie points k+0.05 (BC-1.04.019).

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
  BC-1.04.002/003/004/006/007/008/009/013/015/017/018/019/021 (TTL/freshness
  monotonicity, history cap and point-age order on the success path — the failure
  path re-saves verbatim, BC-1.04.003 Inv 2 —, redirect
  visited-cap sampling behaviour, cells caps, box-segment trailing space, NaN-iff
  degrade, mix[7] shape presence/dimming, sparkline scale bounds, TTFT
  rounding bands and ties, idle-age ordering, power-format invariants — the quick-leg oracle
  INDEPENDENTLY RE-DERIVES each BC rule in the harness; a canonical table cannot
  oracle randomly generated states, the VP-041 A2-08 lesson), and Tier C
  differential-fuzz rows for the
  surfaces marked "fuzz" in BC-1.04.001 (fetch/redirect sampling) and BC-1.04.009
  (sparkline scale), budgeted by `HYLO_PARITY_FUZZSECONDS`, same oracle discipline
  as VP-011. The metrics-client transport table (`TestMetricsClient_OD181_TransportTable`,
  OD-181 rider per VP-012) pins hylo's minimal HTTP/1.1 client behaviour here — plain
  http AND https upgraded through `crypto/tls` per BC-1.04.001 PC1 (only the parity
  CORPUS is plain http, OD-181, ADV-P8-C2-09): urllib's
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
| Fault rows | Go test (RAW `net.Listener` fake for every metrics fake — the status/body fault rows included, not only the transport table; not httptest, whose server canonicalises headers into a map and trims values, ADV-P7-C2-05) | yes | down/500/garbage/±Inf metrics |
| Property legs | `testing/quick`, *quick.Config with Values | sized | BC-1.04.002/003/004/006/007/008/009/013/015/017/018/019/021 for-all rows (ADV-P8-C2-08) |
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
`TestGetSample_Pinned11StepSequence` and
`TestMetricsClient_OD181_TransportTable` (defined here per VP-012's rider register,
ADV-P8-A2-19).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Sequence + segment tables | bounded |
| Proof complexity | N/A | |
| Tool support | Full | RAW `net.Listener` fake for every metrics fake (transport table and status/body fault rows alike, ADV-P7-C2-05) — not httptest |
| Estimated proof time | Weeks | segment volume |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
