---
document_type: verification-property
level: L4
version: "1.6"
status: draft
producer: architect
timestamp: 2026-11-19T22:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.03.003.md, behavioral-contracts/ss-01/BC-1.03.005.md, behavioral-contracts/ss-01/BC-1.04.003.md, prd-supplements/nfr-catalog.md]
input-hash: "020303d"
traces_to: prd.md
source_bc: BC-1.03.005
bcs: [BC-1.03.003, BC-1.03.005, BC-1.04.003]
module: internal/statusline (store caps)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified:
  - "1.1 2026-11-17: ADV-P1 pass-1 fixes"
  - "1.2 2026-11-17: ADV-P2 fix — legacy has exactly FOUR caps: SPARK_MAX_AGE = 90 s age cap added (A2-14)"
  - "1.3 2026-11-19T18:00:00Z: pass-7 fix (A2-06) — the 512 KB read step and the 32-point history cap are registered CONFIG keys per BC-2.01.004 PC-10 (statusline.transcript.read_cap_bytes, Int(bytes), default 524288; statusline.sparkline.history_cap, Int, default 32, range 1..1000), not the module constant _READ_CAP and not an unnamed cap; 'legacy-identical' is stated as: the DEFAULT values equal legacy's constants, and at non-default values hylo applies legacy's eviction discipline (FIFO/oldest-first slice or prune) at the configured magnitude"
  - "1.4 2026-11-19T22:00:00Z: pass-8 fix (ADV-P8-C2-08, orchestrator call 12) - the testing/quick for-all leg BC-1.04.003's VP-table routes here jointly with VP-030 now exists in this document, stated normatively: for every generated history state, saved length <= 32 and every saved point satisfies now - t < 90 or is the new point; Method bullet, Proof Method table and skeleton updated"
  - "1.5 2026-11-20T15:00:00Z: pass-9 fixes (ADV-P9-A2-05, orchestrator call 3; ADV-P9-A2-04 side) — the pass-8 joint-routing claim corrected: the BC-1.04.003 testing/quick row is VP-030's ALONE (the BC de-cited VP-031 in pass 8); what BC-1.04.003 routes HERE is the 16-subset point key-order table (VP-030, VP-031), which this document now delivers; the duplicated cap/age for-all removed from this document (VP-030 states it, success-path-qualified); frontmatter converted to a block list and the 1.3 entry's lost closing quote repaired (YAML repair, orchestrator call 5); no history entry lost"
  - "1.6 2026-11-20T18:00:00Z: pass-11 fix (C2-01, orchestrator call 12) — the gen_rate5m fallback `v` is inserted AFTER `k` and `f` (SL:344-345), correcting the statement's buried parenthetical and the SL:333-343 citation (builder SL:338-347); the point key-order table now includes the 8 fallback-v subsets (24 rows total, primary and fallback `v` mutually exclusive) in statement, Method bullet, Proof Method table and skeleton"
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-031: Bounded per-refresh state — legacy-identical caps

## Property Statement

Per-refresh state is capped exactly as legacy capped it, and legacy has exactly four
caps (NFR-005, P13 — no cap may be invented): the 256-id usage dedup (registry key
`statusline.transcript.dedup_memory`, default 256, T-060; legacy `ids[-256:]`,
mix-cache writer, SL:1153), the 32-point metric histories (config key
`statusline.sparkline.history_cap`, Int, default 32, range 1..1000, BC-2.01.004
PC-10; legacy `hist[-32:]`, SL:350), the 512 KB transcript read step (config key
`statusline.transcript.read_cap_bytes`, Int(bytes), default 524288,
BC-2.01.004 PC-10; legacy `_READ_CAP = 524288`, SL:952), and the 90 s history age cap
(config key `statusline.sparkline.max_age_s`, 90,
T-007; legacy `SPARK_MAX_AGE = 90.0`, SL:83) — the fourth cap is age-based, pruning
history points older than 90 s (BC-1.04.003). The "memory-256 mix cache" is that same
256-id dedup list seen from the
mix-cache writer — one cap, not two. There is no turn-identity-line window in legacy
and none in hylo. "Legacy-identical" is stated per value (A2-06): the DEFAULT
configuration reproduces legacy's constants exactly (parity, D4), and at NON-default
values hylo applies legacy's eviction discipline (the same FIFO/oldest-first slice
or prune, per the owning BC) at the configured magnitude — configurable magnitude,
identical mechanism. Each cap value is a registry key with rationale
(D15), and exceeding a cap evicts per legacy's discipline (FIFO/oldest-first as the
owning BC rules). BC-1.04.003's VP-table also routes a MANUAL table here jointly with
VP-030 (pass-9 ADV-P9-A2-05): point key order equals legacy for every subset of the
four plottable series (v, k, f, p), with v split by SOURCE — primary `v`
(`dgx_sl:gen_rate1m` in the sample, inserted by the series loop) versus fallback `v`
(`dgx_tokens:gen_rate5m`, inserted AFTER `k` and `f`, SL:344-345). Legacy inserts
`t` first (unix now), then the loop's `v`, `k`, `f` each when its PRIMARY series is
in the sample, then — after the loop, so after `k` and `f` — the fallback `v` when
`v` is still absent and `dgx_tokens:gen_rate5m` is in the sample, then `p` = 1 when
preemptions are active (SL:338-347); the fallback can never precede `k` or `f`, and
primary and fallback `v` are mutually exclusive. hylo's writer inserts in the same
order, and `json.dumps` preserves insertion order.

Point key order, v primary (dgx_sl:gen_rate1m in sample; loop order) — 16 subsets:

| v | k | f | p | Saved point key order |
|---|---|---|---|---|
| – | – | – | – | t |
| v | – | – | – | t, v |
| – | k | – | – | t, k |
| – | – | f | – | t, f |
| – | – | – | p | t, p |
| v | k | – | – | t, v, k |
| v | – | f | – | t, v, f |
| v | – | – | p | t, v, p |
| – | k | f | – | t, k, f |
| – | k | – | p | t, k, p |
| – | – | f | p | t, f, p |
| v | k | f | – | t, v, k, f |
| v | k | – | p | t, v, k, p |
| v | – | f | p | t, v, f, p |
| – | k | f | p | t, k, f, p |
| v | k | f | p | t, v, k, f, p |

Point key order, v via the gen_rate5m fallback (loop `v` absent; fallback `v` AFTER
`k` and `f`, SL:344-345) — 8 subsets:

| k | f | p | Saved point key order |
|---|---|---|---|
| – | – | – | t, v |
| k | – | – | t, k, v |
| – | f | – | t, f, v |
| – | – | p | t, v, p |
| k | f | – | t, k, f, v |
| k | – | p | t, k, v, p |
| – | f | p | t, f, v, p |
| k | f | p | t, k, f, v, p |

## Source Contract

- **Primary BC:** BC-1.03.005 — Usage dedup per message id (memory 256).
- **Partial coverage:** BC-1.03.003 (512 KB read steps), BC-1.04.003 (90 s cap, 2 s
  gap — 32-point histories).
- **Invariant verified:** NFR-005 (table-verified caps identical to legacy).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — cap±1 boundary rows per cap; eviction-order rows;
  PLUS the point key-order table BC-1.04.003's VP-table routes here jointly with
  VP-030 (manual table over the 16 primary-v + 8 fallback-v series subsets; pass-9
  ADV-P9-A2-05 — the pass-8 quick-leg routing claim corrected: the testing/quick row
  is VP-030's alone; pass-11 C2-01 adds the fallback rows, fallback `v` after `k`
  and `f` per SL:344-345).
- **Honesty:** testable-only; boundary tables, plus a static check that cap constants
  match the registry/constant register (no silent retuning).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Cap boundary tables | Go test | yes — cap±1 per cap (age cap: age ± ε) | all four caps + eviction rows |
| Constant pin | registry golden | yes | cap provenance (D15) |
| Point key-order table | Go table test over the 16 primary + 8 fallback series subsets | yes — 24 rows | BC-1.04.003 manual row (VP-030, VP-031; pass-9 ADV-P9-A2-05; pass-11 C2-01 fallback rows) |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestCaps_LegacyIdentical(t *testing.T) { // defaults equal legacy (A2-06)
    if transcriptDedupMemory() != 256 { t.Fatal("dedup cap drifted (SL:1153 ids[-256:])") }
    if metricHistoryPoints() != 32 { t.Fatal("history cap drifted (SL:350 hist[-32:])") }
    if readCapBytes() != 512*1024 { t.Fatal("read cap drifted (SL:952 _READ_CAP 524288)") }
    if sparkMaxAgeS() != 90.0 { t.Fatal("history age cap drifted (SPARK_MAX_AGE 90.0, SL:83)") }
    // The cap SOURCES are the registered config keys (BC-2.01.004 PC-10):
    // statusline.transcript.read_cap_bytes, statusline.sparkline.history_cap —
    // not package constants; the boundary rows below run at default AND at
    // non-default values, asserting the SAME eviction discipline at any magnitude.
    // no turn-identity window constant exists; a static registry check asserts
    // the registry set is exactly these four caps (NFR-005).
}

func TestPointKeyOrder_SeriesSubsets(t *testing.T) { // pass-9 ADV-P9-A2-05: BC-1.04.003 manual row
    for _, s := range SeriesSubsets24 { // 16 primary-v subsets of {v, k, f, p} + 8 fallback-v subsets (pass-11 C2-01: fallback v AFTER k and f, SL:344-345)
        pt := buildPoint(now, s) // sample carrying exactly s's series (fallback rules per BC-1.04.003)
        got := keyOrder(pt)      // insertion order of the saved dict
        if !reflect.DeepEqual(got, legacyKeyOrder(s)) {
            t.Fatalf("subset %v: key order %+v", s, got)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestCaps_LegacyIdentical` + boundary
matrices per cap.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Four caps (point/byte caps ±1; age cap ±ε) | tiny |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Hours | |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
