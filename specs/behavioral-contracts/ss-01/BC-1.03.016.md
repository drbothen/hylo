---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, ../semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_finish_turn, _mix_counts (SL:988-996, 1064-1087)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-094"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.016: Turn-machine exhaustive table (20 rows)

## Description

The turn machine of BC-1.03.010 is pinned by an exhaustive table of 20 transcript scenarios with exact expected
`lr` (and, where relevant, `cur` / `lu`) values. The Go port must reproduce every row as a table test
(`internal/statusline/transcript_turn_test.go`). Row T15 is a legacy crash; its Go expectation is the D4-EX-2
result.

## Preconditions

1. Time zone UTC; base time `2026-11-14T10:00:00Z` = 1794650400.0; empty mix cache before each row; sid unique per
   row; each line followed by LF; default turn config (200 / 15.0 / 4.0).
2. Line templates (Python `json.dumps` defaults; `t` = seconds after the base, rendered `%Y-%m-%dT%H:%M:%SZ`):
   - `U(t)` = `{"type": "user", "message": {"role": "user", "content": "go"}, "timestamp": "<t>"}`
   - `U(t, TR)` = same with `"content": [{"type": "tool_result", "tool_use_id": "x", "content": "ok"}]`
   - `A<id>(t, out)` = `{"type": "assistant", "message": {"id": "<id>", "content": [{"type": "text", "text":
     "x"}], "usage": {"output_tokens": <out>}}, "timestamp": "<t>"}` (out 300 unless stated)
   - `S(t)` = `{"type": "system", "subtype": "turn_duration", "timestamp": "<t>"}`
   - "untimed" = the same object without the `timestamp` key.

## Postconditions

Each row's final mix cache carries exactly the `lr` (and stated `cur`/`lu`) below. Rows marked "refresh n"
append lines and run one refresh per step.

| Row | Lines (t in s) | Expected | Rule pinned |
|---|---|---|---|
| T1 | U(0), AA(2), AA(10), AB(12) | `lr [30.0, false]`; `cur {"id": "B", "t0": 1794650400.0, "t1": 1794650412.0, "out": 300}` | A runs prompt→last line; B shares t0 0 (no user line between) |
| T2 | U(0), AA(2), U(5,TR), AA(10), S(11) | `lr [30.0, false]`, `lu 1794650405.0` | tool_result-only user line moves `lu`, does not close |
| T3 | as T2 with U(5) content `[tool_result, {"type":"text","text":"t"}]` | `lr [30.0, false]` | mixed content counts as tool_result |
| T4 | as T2 with U(5) content `[{"type":"text","text":"t"}]` | `lr [60.0, false]` | closes A (150 t/s); A's line at 10 reopens (t0 5, own out 300), closed by S11 → 60 |
| T5 | as T2 with U(5) = `{"type": "user", "timestamp": …05Z, "message": {}}` | `lr [60.0, false]` | missing content closes |
| T6 | U(0), AA untimed ×2, AB(12), S(13) | `lr [25.0, false]` | untimed lines invisible to the turn machine |
| T7 | U(0), AA(2), S(3), U untimed, AB(30), S(31) | `lr [10.0, false]` | untimed user line does not move `lu` |
| T8 | U(0), AA(2), S untimed, AA(10), S(11) | `lr [30.0, false]` | untimed system line does not close |
| T9 | U(0), AA(2), timed `compact_boundary` at 10 | `lr [150.0, false]` | timed boundary closes (and resets composition) |
| T10 | AA(2), AB(10), S(11) | `lr null`, `lu null` | t0 null → every turn skipped |
| T11 | refresh 1: U(0), AA(2) · refresh 2: AA(9) · refresh 3: S(10) | `lr` null, null, `[33.333333333333336, false]`; `cur` after r1 `{"id": "A", "t0": 1794650400.0, "t1": 1794650402.0, "out": 300}`, after r2 `t1` 1794650409.0 | `cur` persisted unfinished |
| T12 | refresh 1: U(0) · refresh 2: AA(2) · refresh 3: S(12) | final `lr [150.0, false]` | `lu` carried across refreshes |
| T13 | U(0), AA(2) with **no** `usage` key, S(10) | `lr null` | out 0 → `out ≤ 0` skip (**row added 2026-11-15**, see Edge Cases) |
| T14 | U(0), AA(2), AB(5), AA(8), S(9) | `lr [37.5, false]` | reappearing id after another id opens a new turn (t0 0, t1 8) |
| T15 | U(0), AA(2, 10), AB(5, 5), AA(8, `"abc"`), U(9) | legacy: `TypeError` at SL:994, no cache, sticky; **hylo (D4-EX-2): `lr [5.0, true]`, `cur null`, `lu 1794650409.0`** | CP-T05 reachable from 5 lines |
| T16 | U(0), AA(2, NaN), S(10) | `lr [NaN, false]` (cache token `NaN`) | NaN out → NaN rate |
| T17 | U(0), AA(2, 150), AB(4, 100), S(40) | `lr [25.0, true]` | span ends at the message's last line; both dim |
| T18 | U(0), AA(80, 300), S(81) | `lr [3.75, false]` | `span == 4·out/15` accepted |
| T19 | U(0), assistant at 2 without `message.id`, S(10) | `lr null` | no id → no turn action |
| T20 | U(0), AA(2), `{"type": "summary", "timestamp": …05Z, "summary": "s"}`, AA(9), S(10) | `lr [33.333333333333336, false]` | other line types ignored |

## Invariants

1. Rows are independent (fresh cache each).
2. Every non-T15 row's legacy result equals the Go result byte-for-byte in the whole cache file (byte-exact).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Source table gap | The source table (pass-3 r2 §A4) lists 19 rows (T1-T12, T14-T20; T13 absent) although it is cited as "20 rows". This BC adds **T13** (usage absent → out 0 → skipped). Disposed by OD-143: the row was re-confirmed against the CPython 3.11 oracle on 2026-11-15 (legacy run: `size` 311, `lr` null, `lu` 1794650400.0, `cur` null, `tout` 0 — the pinned golden exactly), so T13 is real legacy behavior and stays; the table is 20 rows |
| EC-002 | T15 under the parity harness | excluded from the Python-vs-Go diff via the D4-EX-2 entry of the OD-105/OD-110 exclusion list; its Go expectation is asserted here and in BC-1.03.019 (T05+) |
| EC-003 | T16 NaN rendering downstream | rendering of a NaN rate is BC-1.04.018's concern |

## Canonical Test Vectors

Full-cache goldens for three rows (re-pinned 2026-11-15, legacy oracle, CPython 3.11, TZ=UTC):

| Input | Expected Output | Category |
|-------|----------------|----------|
| T1 | `{"size": 580, "res": 0, "conv": 5, "think": 0, "tin": 0, "tout": 600, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": 0, "ids": ["A", "B"], "lr": [30.0, false], "lu": 1794650400.0, "cur": {"id": "B", "t0": 1794650400.0, "t1": 1794650412.0, "out": 300}}` | happy-path |
| T13 | `{"size": 311, "res": 0, "conv": 3, "think": 0, "tin": 0, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": null, "ids": [], "lr": null, "lu": 1794650400.0, "cur": null}` (re-produced by the OD-143 oracle run 2026-11-15) | edge-case |
| T16 | `{"size": 344, "res": 0, "conv": 3, "think": 0, "tin": 0, "tout": NaN, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": 0, "ids": ["A"], "lr": [NaN, false], "lu": 1794650400.0, "cur": null}` | edge-case |
| T15 | legacy `TypeError: '<=' not supported between instances of 'str' and 'int'` on both refreshes; hylo as in the table | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | All 20 rows pass as Go table tests | table test (20 rows) |
| VP-TBD | All rows except T15 match legacy byte-for-byte in the parity harness | parity harness (Tier A) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007, DI-012 |
| Source | legacy/dgx_statusline.py:_finish_turn (SL:988-996), _mix_counts (SL:1064-1087) |
| Legacy contract | BC-SL-094 (pass-3 r2 §A4) |
| Parity class | byte-exact (T15 → D4-EX-2) |
| Decisions | D4-EX-2 (Q-c); OD-105/OD-110 exclusion entry `D4-EX-2` for T15; OD-143 (T13 confirmed against the oracle, row kept) |
| Architecture Module | `internal/statusline/transcript_turn.go` (+ `_test.go`) |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.010 — depends on: the rules this table pins
- BC-1.03.017 — related to: T4/T14 (reopened turns)
- BC-1.03.019 — related to: T15 = T05+ shape

## Architecture Anchors (Recommended)

- `architecture/TBD.md#turn-machine`

## Story Anchor (Recommended)

S-TBD — turn machine

## VP Anchors (Recommended)

- VP-TBD — 20-row table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:988-996, 1064-1087) |
| **Confidence** | high (all 20 rows reproduced 2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: oracle runs of each row (pass-3 r2 `turn.py`/`cpt.py`; re-run 2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (table drives the pure parser) |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

Generate the row transcripts with the committed Go fixture generator (design §5.2) from the templates above;
commit the expected caches as goldens.
