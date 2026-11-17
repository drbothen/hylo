---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T18:40:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "c2f799c"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1029-1034, 1096-1103, 1153)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-034"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: dedup_memory range >= 1 (OD-162); Python set-key semantics NaN/1/1.0/true (ADV-P2-C03/C07); oracle-verified"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.005: Usage dedup per message id (memory 256)

## Description

Claude Code writes one transcript line per content block of an API message and repeats the message's full
`usage` on every line. The parser counts each message id's usage once: an id already seen is ignored; an unseen
truthy id is recorded and counted; a usage object without an id is always counted. The id memory survives across
refreshes as the last `dedup_memory` (256) ids recorded; within a single refresh it is unbounded.

## Preconditions

1. A decoded line `e` that is an object, is not a `compact_boundary` system line (BC-1.03.008), and passes the
   D4-EX-2 W-predicates (BC-1.03.018).
2. `msg = e.message` if truthy, else `{}`; `u = msg.usage`; `mid = msg.id`.
3. `recent_ids` = cached `ids` list (or `[]` after a reset, BC-1.03.002); `seen` = the set of its elements, kept
   in sync during the refresh.
4. `N = statusline.transcript.dedup_memory` (default 256; T-060, rationale: derived — ids of one message are
   adjacent, so any N ≥ 1 covers refresh boundaries; 256 is margin; SL:1029-1032). **Valid range (OD-162):**
   `>= 1`, derived from legacy semantics — the write stores `recent_ids[-N:]` (SL:1153): `N = 0` yields the Python
   whole-list slice `ids[-0:]` (oracle-verified), defeating the cap; negative N truncates from the wrong end.
   Out-of-range values are number-range config errors (S2 schema, OD-114).

## Postconditions

1. If `u` is an object, `mid` is truthy and `mid ∈ seen`: the line's usage is treated as absent (no counting,
   no rebuild check, `pp` unchanged).
2. Else if `u` is an object and `mid` is truthy: `mid` is added to `seen` and appended to `recent_ids`; the usage
   is counted (BC-1.03.006, BC-1.03.007).
3. Else if `u` is an object (id falsy: missing, null, `""`, `0`, `false`): counted; nothing recorded.
4. If `u` is not an object (missing, null, number, string, array): nothing is counted or recorded (an array
   usage on an opening line is the CP-T03 shape, BC-1.03.018).
5. The cache write stores `"ids": recent_ids[-N:]` (insertion order, oldest first; duplicates cannot occur).
   Membership is Python set semantics over decoded values: hash first, then equality with an identity
   short-circuit. Oracle-verified 2026-11-17 (CPython 3.11.7): (a) every JSON-decoded `NaN` is the **same shared
   object** (`json.loads` returns one constant), so decoded NaN ids dedupe **by identity** despite `NaN != NaN`;
   two distinct NaN objects would not collide (id-based hashing) but the decoder never produces them; (b) the
   scalars `1`, `1.0` and `true` collide (equal, equal hash) — first-recorded wins; (c) strings compare normally.
   Go keys `seen` by the `pyfmt.Value` canonical form reproducing these equivalences.
6. An id that falls out of the stored window (more than N later distinct ids recorded before the refresh boundary)
   is counted again if it reappears in a later refresh.

## Invariants

1. Dedup keys on equality of the decoded id value (string ids in practice; any hashable JSON scalar works the same
   way; an unhashable id is the CP-T07 shape, BC-1.03.018). Python key semantics per postcondition 5: shared-object
   NaN dedupes, and `1`/`1.0`/`true` are one key (both oracle-verified 2026-11-17).
2. Turn tracking does **not** consult `seen` (BC-1.03.017).
3. Composition is counted for every line regardless of dedup (BC-1.03.009).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Same id on the next refresh | ignored (id is in the stored window) |
| EC-002 | Two id-less usage lines | both counted |
| EC-003 | `msg_A`, then 256 other ids in refresh 1, `msg_A` in refresh 2 | counted again (stored window = the 256 others) |
| EC-004 | `msg_A`, then 255 others, `msg_A` next refresh | ignored |
| EC-005 | `msg_A`, 300 others, `msg_A` in the **same** refresh | ignored (in-refresh memory unbounded) |
| EC-006 | Id present but `usage` absent | not recorded; a later line of that id with usage is counted |
| EC-007 | Reset (BC-1.03.002) | memory cleared before parsing |

## Canonical Test Vectors

`A(id, usage, content)` = `{"type": "assistant", "message": {"content": <content>, "id": <id>, "usage": <usage>}}`
serialized with Python `json.dumps` defaults, one per line. `u` = `{"input_tokens": 10,
"cache_creation_input_tokens": 1000, "cache_read_input_tokens": 0, "output_tokens": 300}`. Re-pinned 2026-11-15.

| Input | Expected Output | Category |
|-------|----------------|----------|
| refresh 1: `A("msg_A", u, [{"type":"text","text":"ab"}])`, `A("msg_A", u with output_tokens 900, [{"type":"text","text":"cd"}])` | cache `{"size": 430, "res": 0, "conv": 4, "think": 0, "tin": 1010, "tout": 300, "c_wr": 1000, "c_rd": 0, "mixv6": 1, "c_in": 10, "rb": 0, "pp": 1010, "ids": ["msg_A"], "lr": null, "lu": null, "cur": null}` | happy-path |
| refresh 2: append `A("msg_A", u, "")` | `"size": 615`, all totals unchanged (`tin` 1010, `tout` 300), `"ids": ["msg_A"]` | happy-path |
| two lines `{"type":"assistant","message":{"content":"","usage":{"input_tokens":5}}}` (no id) | `"tin": 10`, `"c_in": 10`, `"pp": 5`, `"ids": []` | edge-case |
| refresh 1: `msg_A` + ids `o000`..`o255` (each `{"input_tokens":1}`); refresh 2: `msg_A` | refresh 1: `tin` 257, stored ids = `o000`..`o255` (256); refresh 2: `tin` 258 | edge-case |
| as above with `o000`..`o254` | refresh 2: `tin` stays 256 | edge-case |
| one refresh: `msg_A`, `o000`..`o299`, `msg_A` | `tin` 301 | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029, VP-031 | Each truthy id contributes usage at most once per stored-window lifetime | Go property test (testing/quick) |
| VP-029, VP-031 | `len(ids) ≤ N` and `ids` has no duplicates after every write | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1029-1034, 1096-1103, 1153) |
| Legacy contract | BC-SL-034 (base; refined pass-3 r1 with BC-SL-065) |
| Threshold | T-060 → `statusline.transcript.dedup_memory` = 256 |
| Parity class | byte-exact |
| Architecture Module | `internal/statusline/transcript.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.011 — composes with: the first line of a message supplies its usage
- BC-1.03.006 — depends on this BC: what "counted" adds
- BC-1.03.017 — related to: turn identity ignores the id memory
- BC-1.03.002 — related to: memory cleared on reset

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript.go (dedup 256) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029, VP-031 — usage counted once per id

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1029-1034, 1096-1103, 1153) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if isinstance(u, dict) and mid and mid in seen_ids: u = None` (SL:1099-1100)
- **documentation**: SL:1029-1032 (review #10.2: per-line summing overcounted ×2.91)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (state carried via the mix cache) |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes (pure over the parse state) |
| **Overall classification** | pure |

#### Refactoring Notes

Hold `recent_ids` as an ordered slice of `pyfmt.Value` plus a set keyed by the value's canonical form; trim to N
only at write time.
