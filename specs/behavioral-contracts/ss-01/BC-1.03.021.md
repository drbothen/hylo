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
extracted_from: "legacy/dgx_statusline.py:_finish_turn, _mix_counts (SL:988-996, 1073-1079, 1150-1153)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-103"
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

# Behavioral Contract BC-1.03.021: cur with t0 null and non-numeric out kept verbatim

## Description

When the CP-T05 shape occurs while `lu` is still null (no timed user line yet), the W-predicate does not hold, so
both legacy and hylo process the line: they open a turn `{"id": …, "t0": null, "t1": …, "out": "abc"}` and persist
it. This is a normal, crash-free state: `finish` returns early on `t0 == null` before reading `out`. hylo must store
`cur.out` as a raw JSON value, write it back verbatim, and must not apply the OD-32 reader rule to it.

## Preconditions

1. A timed assistant line with a truthy id opens a new turn while `lu` is null, and its `usage.output_tokens` is a
   truthy non-number (or `cur` with `t0` null and non-numeric `out` is loaded from a cache).

## Postconditions

1. `cur = {"id": <id>, "t0": null, "t1": <t>, "out": <raw value>}` is held and written verbatim (`"out": "abc"`,
   `["x"]`, `{"a": 1}`), key order `id, t0, t1, out`.
2. Later lines of the same id move `t1` only; `out` stays the raw value.
3. Closing the turn (newer id, real user prompt, timed system line) calls `finish`, which returns `lr` unchanged
   because `t0` is null; `cur` becomes null; no error.
4. On load, the OD-32 reader rule (BC-1.03.020) does **not** fire because `t0` is not a number.
5. The Go mix-cache type stores `cur` (and `cur.out`) as `pyfmt.Value`, never a typed number.

## Invariants

1. `finishTurn` checks `cur == null/empty` and `t0 == null` before reading `out` (legacy order, SL:991-993).
2. Legacy and hylo write identical bytes for this state (byte-exact; no exclusion entry).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Continuation line of the same id, no closer | `t1` updated, `out` still `"abc"` |
| EC-002 | Then a timed system line | `cur` null, `lr` unchanged (null), no crash |
| EC-003 | Applying the original (unamended) OD-32 rule here | would give `"out": 900` after a continuation — **wrong** (diverges from legacy); prohibited |

## Canonical Test Vectors

Lines as in BC-1.03.019 (A2', B5, W5) and BC-1.03.020 (A9, S11); TZ=UTC; no cache. Re-pinned 2026-11-15 with the
legacy oracle (hylo must produce identical bytes).

| Input | Expected Output | Category |
|-------|----------------|----------|
| refresh 1: `A2', B5, W5` | `{"size": 669, "res": 0, "conv": 9, "think": 0, "tin": 220, "tout": 15, "c_wr": 200, "c_rd": 0, "mixv6": 1, "c_in": 20, "rb": 0, "pp": 110, "ids": ["msg_A", "msg_B"], "lr": null, "lu": null, "cur": {"id": "msg_A", "t0": null, "t1": 1794650408.0, "out": "abc"}}` | happy-path |
| refresh 2: append `A9` | `{"size": 921, …, "conv": 12, …, "cur": {"id": "msg_A", "t0": null, "t1": 1794650410.0, "out": "abc"}}` | edge-case |
| refresh 3: append `S11` | `{"size": 1005, …, "conv": 12, …, "lr": null, "lu": null, "cur": null}` (no crash) | edge-case |
| BC-1.03.019 row 14 (T05− lu none, with U9) | `"lr": null`, `"cur": null`, byte-exact with legacy | edge-case |

(`…` elides fields equal to refresh 1's.)

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | `cur.out` round-trips verbatim through load/save for any JSON value | proptest |
| VP-029 | `finishTurn` never errors when `t0` is null | proptest |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Source | legacy/dgx_statusline.py:_finish_turn (SL:988-996), _mix_counts (SL:1073-1079, 1150-1153) |
| Legacy contract | BC-SL-103 (pass-3 r4 §1.2; confirmed r5) |
| Parity class | byte-exact (design §8: BX, OD-32) |
| Decisions | OD-32 (amended: rule only when `t0` is numeric); ruling b (exact cache format) |
| Architecture Module | `internal/statusline/mixcache.go`, `transcript_turn.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.020 — related to: the reader rule must not fire here
- BC-1.03.010 — depends on: `finish` order
- BC-1.03.018 — related to: CP-T05 requires `lu` set

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#mix-cache` — internal/statusline/mixcache.go (t0 null, out verbatim) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — mix cache

## VP Anchors (Recommended)

- VP-029 — raw `cur.out` round-trip

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:988-996, 1073-1079, 1150-1153) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if not cur or cur.get("t0") is None: return lr` (SL:991-992)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed beyond holding `cur` as `pyfmt.Value`.
