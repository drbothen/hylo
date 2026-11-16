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
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1059-1153)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-099"
parity_class: "D4-EX-2"
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

# Behavioral Contract BC-1.03.019: D4-EX-2 table tests (21 rows, exact expected caches)

## Description

The dedicated table tests for the **approved deviation D4-EX-2** (owner ruling Q-c). 21 rows cover each W-predicate
of BC-1.03.018 positively (legacy raises; hylo skips) and each non-crash look-alike negatively (legacy and hylo
agree byte-for-byte). Every expected mix cache is exact. Positive expectations were derived by the delete-the-line
oracle: legacy run on the transcript without the W-line, `size` increased by the W-line's bytes + 1.

## Preconditions

1. TZ=UTC; sid `d4ex2`; empty mix cache before each row; one refresh; every line followed by LF.
2. Base lines (byte-exact):

```text
U0  {"type": "user", "timestamp": "2026-11-14T10:00:00Z", "message": {"role": "user", "content": "hello there"}}
A2  {"type": "assistant", "message": {"id": "msg_A", "content": [{"type": "text", "text": "Hi."}], "usage": {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 0, "output_tokens": 30}}, "timestamp": "2026-11-14T10:00:02Z"}
S20 {"type": "system", "subtype": "turn_duration", "timestamp": "2026-11-14T10:00:20Z"}
A2' = A2 with "output_tokens": 10
B5  = A2 with "msg_A" -> "msg_B", "output_tokens": 5, timestamp "2026-11-14T10:00:05Z"
U9  = U0 with timestamp "2026-11-14T10:00:09Z"
W5  {"type": "assistant", "message": {"id": "msg_A", "content": [{"type": "text", "text": "Hi."}], "usage": {"output_tokens": "abc"}}, "timestamp": "2026-11-14T10:00:08Z"}
```

3. Unless stated otherwise a row's transcript is `U0, A2, W, S20`.
4. `BASE(n)` denotes the cache `{"size": n, "res": 0, "conv": 14, "think": 0, "tin": 110, "tout": 30, "c_wr": 100,
   "c_rd": 0, "mixv6": 1, "c_in": 10, "rb": 0, "pp": 110, "ids": ["msg_A"], "lr": [15.0, true], "lu":
   1794650400.0, "cur": null}` (Python `json.dump` bytes, no trailing newline).

## Postconditions

| # | Row | W line (byte-exact) | Legacy full run | Expected hylo mix cache |
|---|---|---|---|---|
| 1 | T01+ | `[1, 2]` | AttributeError SL:1069 | `BASE(451)` |
| 2 | T01− | `{}` | OK | `BASE(447)` (= legacy) |
| 3 | T02+ timed | `{"type": "user", "timestamp": "2026-11-14T10:00:05Z", "message": "oops"}` | AttributeError SL:1072 | `BASE(517)` |
| 4 | T02+ untimed | `{"type": "assistant", "message": "oops"}` | AttributeError SL:1097 | `BASE(485)` |
| 5 | T02− untimed cb | `{"type": "system", "subtype": "compact_boundary", "message": "oops"}` | OK | `BASE(513)` with `"conv": 0`, `"pp": null` |
| 6 | T03+ | `{"type": "assistant", "timestamp": "2026-11-14T10:00:05Z", "message": {"id": "msg_B", "usage": [1], "content": []}}` | AttributeError SL:1079 | `BASE(560)` |
| 7 | T03− continuation | row 6 with `"id": "msg_A"` | OK | `BASE(560)` with `"lr": [6.0, true]` |
| 8 | T03− untimed | `{"type": "assistant", "message": {"id": "msg_B", "usage": [1], "content": []}}` | OK | `BASE(523)` |
| 9 | T04+ in | `{"type": "assistant", "message": {"id": "msg_B", "content": [{"type": "text", "text": "Hi."}], "usage": {"input_tokens": "5"}}, "timestamp": "2026-11-14T10:00:05Z"}` | TypeError SL:1108 | `BASE(609)` |
| 10 | T04+ out-only | row 9 with `"usage": {"input_tokens": 5, "output_tokens": "x"}` | TypeError SL:1112 | `BASE(629)` (legacy's pre-raise `tin`/`c_in` increments not applied) |
| 11 | T04− seen id | row 9 with `"id": "msg_A"` | OK | `BASE(609)` with `"conv": 17`, `"lr": [6.0, true]` |
| 12 | T04− cb | `{"type": "system", "subtype": "compact_boundary", "timestamp": "2026-11-14T10:00:05Z", "message": {"id": "msg_B", "usage": {"input_tokens": "5"}}}` | OK | `BASE(591)` with `"conv": 0`, `"pp": null` |
| 13 | T05+ | transcript `U0, A2', B5, W5, U9` | TypeError SL:994 (on U9) | `{"size": 887, "res": 0, "conv": 28, "think": 0, "tin": 220, "tout": 15, "c_wr": 200, "c_rd": 0, "mixv6": 1, "c_in": 20, "rb": 0, "pp": 110, "ids": ["msg_A", "msg_B"], "lr": [5.0, true], "lu": 1794650409.0, "cur": null}` |
| 14 | T05− lu none | transcript `A2', B5, W5, U9` | OK | `{"size": 778, "res": 0, "conv": 20, "think": 0, "tin": 220, "tout": 15, "c_wr": 200, "c_rd": 0, "mixv6": 1, "c_in": 20, "rb": 0, "pp": 110, "ids": ["msg_A", "msg_B"], "lr": null, "lu": 1794650409.0, "cur": null}` (= legacy) |
| 15 | T05~ open at end | transcript `U0, A2', B5, W5` | OK, but writes `"cur": {"id": "msg_A", "t0": 1794650400.0, "t1": 1794650408.0, "out": "abc"}` with `"conv": 20` | `{"size": 778, "res": 0, "conv": 17, "think": 0, "tin": 220, "tout": 15, "c_wr": 200, "c_rd": 0, "mixv6": 1, "c_in": 20, "rb": 0, "pp": 110, "ids": ["msg_A", "msg_B"], "lr": [5.0, true], "lu": 1794650400.0, "cur": {"id": "msg_B", "t0": 1794650400.0, "t1": 1794650405.0, "out": 5}}` — **excluded from the diff** (legacy itself does not crash here) |
| 16 | T06+ text | `{"type": "assistant", "message": {"id": "msg_B", "content": [{"type": "text", "text": 5}], "usage": {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 0, "output_tokens": 30}}, "timestamp": "2026-11-14T10:00:05Z"}` | TypeError SL:1143 | `BASE(691)` |
| 17 | T06+ thinking | `{"type": "assistant", "timestamp": "2026-11-14T10:00:05Z", "message": {"id": "msg_B", "content": [{"type": "thinking", "thinking": true}]}}` | TypeError SL:1145 | `BASE(584)` |
| 18 | T06− cb | `{"type": "system", "subtype": "compact_boundary", "timestamp": "2026-11-14T10:00:05Z", "message": {"content": [{"type": "text", "text": 5}]}}` | OK | `BASE(586)` with `"conv": 0`, `"pp": null` |
| 19 | T06− list | row 16 with `"text": [1, 2, 3]` | OK | `{"size": 699, "res": 0, "conv": 17, "think": 0, "tin": 220, "tout": 60, "c_wr": 200, "c_rd": 0, "mixv6": 1, "c_in": 20, "rb": 0, "pp": 110, "ids": ["msg_A", "msg_B"], "lr": [6.0, true], "lu": 1794650400.0, "cur": null}` |
| 20 | T07+ | `{"type": "assistant", "timestamp": "2026-11-14T10:00:05Z", "message": {"id": ["x"], "usage": {}, "content": []}}` | TypeError SL:1099 | `BASE(557)` |
| 21 | T07− no usage | row 20 without `"usage": {}, ` | OK | `BASE(544)` |

Additional two-refresh case (part of the D4-EX-2 exclusion, not one of the 21): refresh 1 = row 15's transcript,
refresh 2 appends `U9` → legacy raises TypeError SL:994 and keeps the poisoned cache (degraded, sticky); hylo writes
row 13's cache bytes exactly.

## Invariants

1. For positive rows 1, 3, 4, 6, 9, 10, 16, 17, 20 the expected cache equals `BASE` except `size`: the clearest check
   that no partial mutation was applied.
2. Negative rows (2, 5, 7, 8, 11, 12, 14, 18, 19, 21) are byte-exact with legacy and stay in the parity diff.
3. In legacy, positive rows leave **no** mix cache (legacy saves nothing when it raises).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Row 15 (T05~) | hylo cache differs from legacy's; listed in the exclusion file with its own expected output |
| EC-002 | Rows run with TZ ≠ UTC | timestamps carry `Z`, so values are unchanged; the harness still runs them under UTC |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| row 2 (T01−) | `BASE(447)` | happy-path |
| row 13 (T05+) | the row-13 cache above | error |
| row 10 (T04+ out-only) | `BASE(629)` | error |
| row 15 (T05~) | the row-15 hylo cache above | edge-case |

All 21 rows and the two-refresh case were re-run 2026-11-15 against `legacy/dgx_statusline.py` (CPython 3.11) and
reproduce pass-3 r3 §3.1 exactly.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | All 21 rows pass as Go table tests with exact cache bytes | table test (21 rows) |
| VP-TBD | Each positive row and row 15 has an `exclusions.json` entry naming this test | harness self-check (BC-6.03.004) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1059-1153), _finish_turn (SL:988-996) |
| Legacy contract | BC-SL-099 (pass-3 r3 §3.1) |
| Parity class | **D4-EX-2** (approved deviation, owner ruling Q-c) |
| Exclusion entry | OD-105 / OD-110 named list, id `D4-EX-2`, one entry per positive row + row 15 + the two-refresh case; table test `internal/statusline/transcript_wshape_test.go` |
| Architecture Module | `internal/statusline/transcript_wshape_test.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.018 — depends on: the predicates under test
- BC-1.03.020 — related to: row 15's legacy-written cache read back by hylo
- BC-6.03.004 — depends on: exclusion-list machinery

## Architecture Anchors (Recommended)

- `architecture/TBD.md#d4-ex-2`

## Story Anchor (Recommended)

S-TBD — D4-EX-2 wrong-shape skip

## VP Anchors (Recommended)

- VP-TBD — 21-row table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:988-996, 1059-1153) |
| **Confidence** | high (all rows reproduced) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: legacy oracle runs on full and W-deleted transcripts

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (test data) |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

Commit the 21 transcripts and expected caches as synthetic fixtures (`testdata/`); they contain no personal data.
