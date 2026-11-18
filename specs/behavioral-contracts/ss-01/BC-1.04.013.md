---
document_type: behavioral-contract
level: L3
version: "1.3.3"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "76b3a2d"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:main (SL:1217-1227)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-053"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["2026-11-17 (v1.3) pass-2 remediation ADV-P2-C2-02 (NaN dgx_mtok passthrough)", "2026-11-18 (v1.3.1) pass-3 remediation ADV-P3-C2-13 (request count counts redirect hops)", "2026-11-18 (v1.3.2) pass-4 remediation ADV-P4-C2-16 (bool-is-a-number semantics on dgx_mtok: True kept, False none)", "1.3.3 2026-11-17: pass-4 residual sweep — D4-EX-3 table-test name canonicalized to TestD4EX3_* (ADV-P4-D22)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.013: VM fetch whenever ROWS >= 2

## Description

The metrics sample is obtained (BC-1.04.002, with its fetch and session-cache write)
whenever the configured row count is at least 2, even when row 2 is then hidden because
the terminal is narrow. The sample also feeds two row-1 inputs (owned-hardware cost per
MTok and the monthly-volume basis guard). With rows below 2 no sample is obtained at all.

## Preconditions

1. `rows` = `statusline.rows` (default 2, T-002); `narrow_cols` = `statusline.narrow_cols`
   (default 72, T-014, owner judgment "presentation"); `cols` from BC-1.01.005.
2. Ordering per BC-1.01.009: this step runs after the transcript parse and `effective_rl`,
   before the row-2 render and the window-start probe.

## Postconditions

1. If `rows >= 2`: call `get_sample` exactly once → `(sample, age, up, hist)`.
   - If `sample` is a dict: `dgx_mtok = sample.get("dgx_cost:dgx_usd_per_mtok")`, set to
     none when it is not a number or `<= 0` (bool **is** a number here: `True <= 0` is
     false so `True` is kept raw; only `False` becomes none, ADV-P4-C2-16); NaN is a
     number and `NaN <= 0` is false, so NaN passes through **raw** here (SL:1221; the
     `> 0` re-test lives in the ⛏ basis guard, BC-1.05.003 EC-005).
     `dgx_rate = sample.get("dgx_tokens:rate_mtok_month")` passed **raw** (no type or
     range check here).
   - Row 2 is rendered and appended iff `rows > 2 or cols == 0 or cols >= narrow_cols`;
     it receives `hist` when the sparkline is enabled, else `[]`, and the last-turn value
     `mix[7]` when `mix` has at least 8 elements, else none.
2. If `rows < 2`: no fetch, no session-cache write by `get_sample`, no row 2;
   `dgx_mtok = dgx_rate = none`.
3. `dgx_mtok` and `dgx_rate` are passed to the row-1 renderer (consumed by BC-1.05.003).

## Invariants

1. A hidden row 2 still performs the fetch and the cache write (the ⛏ widget depends on it).
2. `rows > 2` forces row 2 regardless of width (including negative `cols`, which then
   disables trimming per BC-1.01.007).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | rows 2, cols 60 | fetch + cache write; one output row |
| EC-002 | rows 2, cols 0 (unset/non-numeric COLUMNS) | row 2 shown |
| EC-003 | rows 2, cols 71 / 72 | hidden / shown |
| EC-004 | rows 3, cols 60 | row 2 shown (then trimmed by BC-1.01.006) |
| EC-005 | rows 1 | no fetch; cache gains no `fetch_ts` from this step |
| EC-006 | `dgx_cost:dgx_usd_per_mtok` = 0, -1, or a string | `dgx_mtok` none |
| EC-006b | `dgx_cost:dgx_usd_per_mtok` = NaN | `dgx_mtok` stays NaN (raw); ⛏ then renders `⛏n/a` (BC-1.05.003 EC-005) |
| EC-007 | `dgx_tokens:rate_mtok_month` = NaN | passed raw as NaN |
| EC-008 | sample none (dead) | `dgx_mtok = dgx_rate = none`; row 2 = `◌ DGX ?` when shown |
| EC-009 | rows value `2_0` (legacy parsed it as 20 and forced row 2) | not reproduced: approved deviation D4-EX-3 — config error line, no cache writes (BC-2.02.003); OD-105 exclusion entry `D4-EX-3`, dedicated test `TestD4EX3_Number` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| rows 2, cols 80, fake metrics up | 2 output rows; session cache has `fetch_ts`, `up`, `ts`, `sample`, `hist` | happy-path |
| rows 2, cols 60, fake metrics up | 1 output row; session cache identical to the cols-80 case | edge-case |
| rows 1, cols 80, fake metrics up | 1 output row; fake metrics receives 0 requests | edge-case |
| rows 2, cols 80, metrics listener closed | row 2 `\e[31m◌ DGX ?\e[0m`; cache `{"fetch_ts": <now>, "up": false}` on a fresh sid (stdin without `rate_limits`, no window-start found) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Fake-metrics request count = 1 initial GET (plus one request per redirect hop the pinned urllib loop detection accepts, BC-1.04.001 PC1/Invariant 1) iff `rows >= 2` and the TTL has elapsed, independent of `cols` | Go property test (testing/quick) (ROWS × COLUMNS matrix) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:main (SL:1217-1227); ROWS/SPARK_ON (SL:75-76); NARROW_COLS (SL:100) |
| Legacy contract | BC-SL-053 (P3 base) |
| L2 Capability | CAP-010, CAP-009 |
| L2 Domain Invariants | DI-007, DI-008, DI-012 (rows D4-EX-3 deviation) |
| Decisions | OD-114 (rows range), OD-107 (P1 config = HYLO_* env + defaults) |
| Architecture Module | `internal/statusline/statusline.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.002 — depends on: sample acquisition
- BC-1.01.003 — composes with: the width rule for row 2
- BC-1.01.009 — composes with: side-effect order
- BC-1.05.003 — related to: consumes `dgx_mtok`/`dgx_rate`

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#effect-step-script-design-doc-31-normative` — internal/statusline/statusline.go (ROWS >= 2 fetch) (effect script step 4) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — fetch independence from width

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1208-1227) |
| **Confidence** | high (design §8 H; the P3 r4 index lists M) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if rows_env >= 2` (SL:1217); width rule (SL:1224); `dgx_mtok <= 0` (SL:1221)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads + writes (via get_sample), network call |
| **Global state access** | reads config |
| **Deterministic** | yes given seams |
| **Thread safety** | not thread-safe |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Part of the ordered effect script (design §3.1 step 4-5); the row-2 render remains pure.
