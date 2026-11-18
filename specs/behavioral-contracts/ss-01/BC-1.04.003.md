---
document_type: behavioral-contract
level: L3
version: "1.3.10"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "ff74134"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:get_sample (SL:329-350)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-042"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.3 2026-11-17: pass-2 remediation ADV-P2-C2-05 (history_cap range; OD-162)"
  - "1.3.1 2026-11-18: pass-3 remediation ADV-P3-C2-02 (OD-160 exclusion id on EC-009)"
  - "1.3.2 2026-11-18: pass-4 remediation ADV-P4-C2-13/14/15 (preempt_marker_above config key + queue.yellow independence; output-neutrality qualified by points <= history_cap; EC-008 KeyError degrade outcome)"
  - "1.3.3 2026-11-18: pass-5 remediation ADV-P5-C2-09 (EC-008 KeyError scoped to hist[-1] + OD-160 tag) and ADV-P5-C2-17 (DI-012 + VP-012 closure citations) and design call 16 (history_cap range 1..1000; preempt_marker_above Float >= 0)"
  - "1.3.10 2026-11-18: pass-13 residual (orchestrator residual sweep, CP-C register alignment): EC-008 cites crash id CP-C17 and EC-010 cites CP-C16, minted by error-taxonomy 1.20 for this contract's foreign cached-sample legs; no behavioral change"
  - "1.3.4 2026-11-18: pass-8 remediation ADV-P8-C2-05 (DI-008 lifted into the L2 row — the EC-008/EC-009 degrades ride the never-blank ladder) + ADV-P8-C2-08 (row-1 testing/quick leg routed to the VP-030 quick leg, VP-031 de-cited; pass-8 call 12)"
  - "1.3.5 2026-11-18: pass-9 remediation ADV-P9-C2-09 (PC2/PC3 name the registered keys statusline.sparkline.max_age_s and statusline.sparkline.min_gap_s beside their default literals)"
  - "1.3.6 2026-11-18: pass-9 residual sweep (call 9, ADV-P9-A2-04 disk sync) — the VP-030 quick-leg row names the registered keys (statusline.sparkline.history_cap, statusline.sparkline.max_age_s) instead of the 32/90 literals, states the pruning invariant on the success path only, and adds the failure-path verbatim re-save (SL:327, SL:353-355; Inv 2), matching VP-030's statement"
  - "1.3.7 2026-11-18: pass-10 remediation ADV-P10-C2-02 (EC-010 added — a dict point whose t is a huge exact JSON integer, magnitude >= 2**1024 - 2**970, raises OverflowError at the SL:336 age filter → errDegraded; OD-160 class; oracle-verified CPython 3.11.7)"
  - "1.3.8 2026-11-18: pass-11 remediation ADV-P11-C2-01 (the VP-031 row names the four varied series v/k/f/p by their series names and pins the gen_rate5m fallback position — v inserted AFTER k and f — so the 16-subset table can no longer be misread as varying the insertion order)"
  - "1.3.9 2026-11-18: pass-12 remediation ADV-P12-C2-04 (the VP-031 row's proof method tracks VP-031 v1.6: the key-order table is 24 rows — 16 primary-v plus 8 fallback-v series subsets, primary and fallback v mutually exclusive)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.003: History point rules (90 s cap, 2 s gap)

## Description

On a successful fetch the sparkline history is normalized, pruned to points younger than
90 s, and extended by at most one new point holding every plottable signal present in the
sample. A missing series omits its key (never a fabricated 0). The saved history is capped
at the last 32 points.

## Preconditions

1. The fetch succeeded (BC-1.04.002 postcondition 3) at clock `now`.
2. `c.hist` is the stored history (any mix of dict points and legacy `[t, v]` lists).
3. Config: `statusline.sparkline.max_age_s` 90 (T-007, derived: gap pruning, F-4),
   `statusline.sparkline.min_gap_s` 2 (T-008, derived: guards a TTL < 2 s), 
   `statusline.sparkline.history_cap` 32 (T-009, derived: bounds the cache for short TTLs;
   rationale accepted OD-57 E-0, kept as keys per OD-55). OD-162 range for
   `history_cap`: Int 1..1000 — the upper bound 1000 is a labeled judgment call
   (A13/NFR-005: bounds the session-cache memory and the `hist[-cap:]` copy cost far
   beyond any TTL the status line admits; pass-5 call 16); the saved slice generalizes
   as `hist[-cap:]` for cap ≥ 1, but cap 0 is a number-range config error because
   Python `hist[-0:]` returns the whole list (SL:350), not an empty one.
   `statusline.sparkline.preempt_marker_above`
   Float 0, range `>= 0` (T-107; ADV-P4-C2-13 — see PC4; Float, not Int, because it
   compares the per-second rate `dgx_preempt:rate5m` whose historical rule was
   `> 0.01/s` (SL:737-738), which no non-zero Int can express — pass-5 call 16,
   ADV-P5-C2-11).

## Postconditions

1. Each stored point is normalized by `_norm_pt`: list `p` → `{"t": p[0], "v": p[1]}`;
   dict unchanged; anything else → `{}`.
2. Points with `now - p.get("t", 0) < statusline.sparkline.max_age_s` (default 90) are
   kept (strict; a point aged exactly `max_age_s` is dropped).
3. A new point is appended only if the kept list is empty or
   `now - hist[-1]["t"] >= statusline.sparkline.min_gap_s` (default 2).
4. The new point is built in this key order: `t=now`; then `v` ← `dgx_sl:gen_rate1m`,
   `k` ← `vllm:kv_cache_usage_perc`, `f` ← `dgx_ttft:p95_30m`, each only if the series is
   in the sample; then, if `v` is still absent and `dgx_tokens:gen_rate5m` is present,
   `v` ← that value (so `v` lands after `f`); then `p=1` if
   `sample.get("dgx_preempt:rate5m", 0) > statusline.sparkline.preempt_marker_above`
   (T-107; config key `statusline.sparkline.preempt_marker_above`, Float, default 0,
   range `>= 0`: the `p` marker shows when preempt > value, default 0 reproducing
   legacy's hard-coded `> 0` — P20; Float, not Int, because the compared series
   `dgx_preempt:rate5m` is a per-second rate whose historical rule was `> 0.01/s`
   (SL:737-738), which no non-zero Int can express — pass-5 call 16, ADV-P5-C2-11. The
   marker is independent of the `statusline.queue.yellow`
   Bool (OD-175): `queue.yellow=false` suppresses the queue segment's yellow colour but
   the `p` marker still plots, ADV-P4-C2-13).
5. The cache stores `hist[-cap:]` (cap = `statusline.sparkline.history_cap`, 32); the
   caller receives the uncapped list. This is output-neutral only while
   `statusline.sparkline.points <= history_cap` (12 <= 32 by default): both lists share
   their last `points` entries. Under an allowed config with `points > history_cap`
   (e.g. points 100, cap 32 — both in range), a history longer than the cap renders
   differently on the fetch path (uncapped list) than on the next cached path (capped
   32-entry list), ADV-P4-C2-14.

## Invariants

1. A point never carries a key whose series was absent from the sample.
2. Normalization happens only on the success path (failure and cached paths keep stored
   points verbatim, BC-1.04.020).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Stored point exactly 90 s old (`t`=910, now=1000) | dropped; `t`=910.5 kept |
| EC-002 | Newest kept point 1.5 s old | no new point (sample not plotted) |
| EC-003 | Newest kept point exactly 2 s old | new point appended |
| EC-004 | Sample has none of v/k/f/gen_rate5m, preempt 0 | point `{"t": 1000.0}` appended |
| EC-005 | Only `gen_rate5m` 12.5, ttft 2.0, preempt 0.01 | `{"t": 1310.0, "f": 2.0, "v": 12.5, "p": 1}` |
| EC-006 | Preempt `NaN` | no `p` (`nan > 0` false) |
| EC-007 | 40 points within 90 s, then one appended | 41 returned, 32 saved |
| EC-008 | Point is a string or number | normalized to `{}`, `t` default 0 → dropped unless `now < 90`; a `{}` point raises KeyError at the gap check ONLY when it is the newest kept point — `hist[-1]` is `{}` makes `hist[-1]["t"]` raise (SL:337) → degraded line (ADV-P4-C2-15); a kept `{}` followed by a newer kept point (e.g. `[{}, {"t": now-1}]`) prunes without raising (ADV-P5-C2-09); crash id **CP-C17**. String/number points are foreign-cache shapes (hylo's and legacy's writers always write dicts): out of byte-parity scope, P3 r2 ruling (b), foreign-cache class carries exclusion id **OD-160**, as EC-009 |
| EC-009 | Point is `[[0]]`-shaped (list of length 1) | IndexError → degraded (CP-C05, foreign cache; out of byte-parity scope, P3 r2 ruling (b); foreign-cache class carries named exclusion id **OD-160**) |
| EC-010 | Dict point whose `"t"` is a huge exact JSON integer (magnitude >= 2**1024 - 2**970, i.e. a 309..4300-digit literal; both signs) | the SL:336 age-filter subtraction `now - t` raises OverflowError ("int too large to convert to float"; oracle-verified CPython 3.11.7, 2026-11-18; `_norm_pt` passes the dict through unchanged, so the intact int reaches the filter) → out of `get_sample` → errDegraded (BC-1.04.002 Inv 1); smaller magnitudes convert and 4301+ digits fail the parse earlier in the never-raise loader (BC-1.06.001); foreign-cache shape, exclusion id **OD-160**, crash id **CP-C16** (ADV-P10-C2-02) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| now 1000, stored `[{"t":998.0,"v":5.0}]`, sample `{gen_rate1m 9.0}` | saved `"hist": [{"t": 998.0, "v": 5.0}, {"t": 1000.0, "v": 9.0}]` | happy-path |
| now 1000, stored `[{"t":999.0,"v":5.0}]`, same sample | saved `"hist": [{"t": 999.0, "v": 5.0}]` (gap 1 s < 2) | edge-case |
| now 1000, stored `[{"t":910.0,"v":1.0},{"t":910.5,"v":2.0}]` | saved `[{"t": 910.5, "v": 2.0}, {"t": 1000.0, "v": 9.0}]` | edge-case |
| stored `[[900.0,50.0],[990.0,60.0],[998.5,70.0]]`, now 1000, S1 | saved `[{"t": 990.0, "v": 60.0}, {"t": 998.5, "v": 70.0}]` (900 pruned, 1000 not appended) | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | On the success path, saved history length ≤ `statusline.sparkline.history_cap` with every saved point satisfying `now - t < statusline.sparkline.max_age_s` or being the new point; the fetch-failure path re-saves the stored history verbatim, unpruned (SL:327, SL:353-355; Inv 2) | Go property test (testing/quick) (routed to the VP-030 quick leg, pass-8 call 12; VP-031 de-cited from this row) |
| VP-030, VP-031 | Point key order equals legacy for every subset of the four varied series — `v` (`dgx_sl:gen_rate1m`), `k` (`vllm:kv_cache_usage_perc`), `f` (`dgx_ttft:p95_30m`) and the preempt marker `p` (`dgx_preempt:rate5m`) — including the fallback cases: when `dgx_sl:gen_rate1m` is absent and `dgx_tokens:gen_rate5m` is present, the fallback fills `v` AFTER `k` and `f` (PC4; SL:344-345), so a subset table built from varying v/k/f/p exercises that order | manual (table over the 24 VP-031 v1.6 rows — 16 primary-`v` plus 8 fallback-`v` series subsets, primary and fallback `v` mutually exclusive; ADV-P12-C2-04) |
| VP-012 | The named deviation this contract carries — exclusion id `OD-160` (EC-008/EC-009 foreign-cache crash shapes out of parity scope) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-160` entry and its riding table test `TestForeignCacheShape_OD160_Vectors`, and the mutation test fails closed if that entry is dropped (ADV-P5-C2-17) | property test (VP-012, go test) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:get_sample (SL:329-350); _norm_pt (SL:652-656); SPARK_MAX_AGE/HIST_MIN_GAP (SL:83-84) |
| Legacy contract | BC-SL-042 (P3 base) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007, DI-008 (the EC-008/EC-009 KeyError/IndexError degrades ride the never-blank ladder: 29-byte line, exit 0; ADV-P8-C2-05), DI-012 (foreign-cache shapes OD-160 under the named-deviation rule) |
| Decisions | OD-55, OD-57 E-0 (T-007/T-008/T-009) |
| Architecture Module | `internal/statusline/sample.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.002 — composes with: called on the success path
- BC-1.04.009 — composes with: the sparkline consumes these points
- BC-1.04.021 — refined by: 2 s gap reachability (seeded)
- BC-1.04.020 — related to: exact cache bytes

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#effect-step-script-design-doc-31-normative` — internal/statusline/sample.go (history points) (history storage) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030, VP-031 — history bound and key order

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:329-350, 652-656) |
| **Confidence** | high — re-executed on CPython 3.11.7 (2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `now - p.get("t", 0) < SPARK_MAX_AGE` (SL:336); `now - hist[-1]["t"] >= HIST_MIN_GAP` (SL:337)
- **documentation**: comment SL:330-334 (no fabricated 0)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Safe for concurrent use (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed — suitable for property testing. Points must be ordered
`pyfmt.Value` objects (BC-5.02.004), not Go structs, to keep key order.
