---
document_type: behavioral-contract
level: L3
version: "1.3.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "9ae073d"
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
modified: ["1.3 2026-11-17: pass-2 remediation ADV-P2-C2-05 (history_cap range; OD-162)", "1.3.1 2026-11-18: pass-3 remediation ADV-P3-C2-02 (OD-160 exclusion id on EC-009)"]
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
   `history_cap`: Int ≥ 1 — the saved slice generalizes as `hist[-cap:]` for cap ≥ 1,
   but cap 0 is a number-range config error because Python `hist[-0:]` returns the
   whole list (SL:350), not an empty one.

## Postconditions

1. Each stored point is normalized by `_norm_pt`: list `p` → `{"t": p[0], "v": p[1]}`;
   dict unchanged; anything else → `{}`.
2. Points with `now - p.get("t", 0) < 90` are kept (strict; a point aged exactly 90 s is
   dropped).
3. A new point is appended only if the kept list is empty or
   `now - hist[-1]["t"] >= 2`.
4. The new point is built in this key order: `t=now`; then `v` ← `dgx_sl:gen_rate1m`,
   `k` ← `vllm:kv_cache_usage_perc`, `f` ← `dgx_ttft:p95_30m`, each only if the series is
   in the sample; then, if `v` is still absent and `dgx_tokens:gen_rate5m` is present,
   `v` ← that value (so `v` lands after `f`); then `p=1` if
   `sample.get("dgx_preempt:rate5m", 0) > 0` (T-107, same rule as the queue).
5. The cache stores `hist[-32:]`; the caller receives the uncapped list (output-neutral:
   the sparkline reads only the last 12).

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
| EC-008 | Point is a string or number | normalized to `{}`, `t` default 0 → dropped unless `now < 90` |
| EC-009 | Point is `[[0]]`-shaped (list of length 1) | IndexError → degraded (CP-C05, foreign cache; out of byte-parity scope, P3 r2 ruling (b); foreign-cache class carries named exclusion id **OD-160**) |

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
| VP-030, VP-031 | Saved history length ≤ 32 and every saved point satisfies `now - t < 90` or is the new point | Go property test (testing/quick) |
| VP-030, VP-031 | Point key order equals legacy for every subset of the four series | manual (table over 16 subsets) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:get_sample (SL:329-350); _norm_pt (SL:652-656); SPARK_MAX_AGE/HIST_MIN_GAP (SL:83-84) |
| Legacy contract | BC-SL-042 (P3 base) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007 |
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
