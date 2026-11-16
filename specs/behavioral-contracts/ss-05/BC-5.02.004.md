---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/statusline-target-design.md, ../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md, owner-decisions-log-2026-11-14.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces Python dict/str semantics behind every cache and transcript value in legacy/dgx_statusline.py)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
confidence: "—"
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

# Behavioral Contract BC-5.02.004: Ordered object Value: insertion order, last-wins keeps position, Delete; WTF-8 strings

## Description

`pyfmt.Value` is the in-memory model of every decoded JSON document (stdin, caches, metrics replies, transcript
lines). Its objects behave like Python dicts (ordered by first insertion; re-assigning a key keeps its position;
deleting and re-adding moves the key to the end) and its strings are sequences of code points that may include
lone surrogates. Cache bytes depend on this order (IM-03), and length measures depend on this string model (IM-11).

## Preconditions

1. Values are built by `Decode` (BC-5.02.003) or by cache writers mutating a loaded Value (design IM-03: writers
   mutate what they loaded instead of building a fresh struct).

## Postconditions

1. **Kinds:** Null, Bool, Int (int64 fast path, promoted to exact big integer), Float (float64 incl. NaN/±Inf), String,
   Array, Object. Int and Float stay distinct (`1` vs `1.0` serialize differently).
2. **Object order:** members iterate in first-insertion order. `Set(k, v)` on an existing key replaces the value in
   place; on a new key appends at the end. `Delete(k)` removes the member; a later `Set(k, …)` appends at the end.
   Decoding duplicate keys is a sequence of `Set`s: last value, first position.
3. **Lookup:** `Get(k)` on a missing key returns Null (Python `.get(k)` → None); on a non-object receiver it is not
   called (callers use the explicit predicates that return `errDegraded`, design IM-02).
4. **Keys** compare by exact code-point sequence, surrogates included (an escaped surrogate pair key, which combines
   into one astral code point, differs from a raw-byte surrogate pair key, which stays two code points).
5. **Strings** hold code points U+0000-U+10FFFF including lone surrogates U+D800-U+DFFF, stored in a WTF-8-style byte
   encoding where every surrogate code point is kept **as written** (two adjacent surrogates from raw bytes are **not**
   merged into one character, unlike strict WTF-8). `Len` counts one per code point (BC-5.03.001).
6. **Copy:** `Clone()` (Python `dict(c)`) preserves order; mutating the clone does not affect the original.

## Invariants

1. No Go map iteration is ever used to produce output (PR-19); object members are a slice.
2. Encoding a Value with `Dumps` writes members in this order (IM-03), so `load → Set → save` reproduces legacy cache
   bytes, including order inherited from the file read earlier (`entry = dict(c)`, SL:327; BC-1.04.020).
3. A string with lone surrogates survives `Decode → Dumps` unchanged (`"\ud800"` → `"\ud800"`).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Decode `{"a":1,"b":2,"a":3}` | members `a: 3, b: 2` |
| EC-002 | On that object: `Set("b", 5)`, `Delete("a")`, `Set("a", 9)` | `Dumps` → `{"b": 5, "a": 9}` |
| EC-003 | Decode raw bytes `"\xed\xa0\xbd\xed\xb8\x80"` | string of 2 code points (U+D83D, U+DE00); `Len` 2; `Dumps` → `"😀"` (14 chars) |
| EC-004 | Decode JSON escapes `"😀"` | 1 code point U+1F600; `Len` 1 |
| EC-005 | Decode `"\ude00\ud83d"` (reversed escapes) | 2 code points, not combined |
| EC-006 | `Get("missing")` | Null |
| EC-007 | Cache `{"proc_start": "x", "a": 1}` then `Set("proc_start", 1794615009.0)` | `{"proc_start": 1794615009.0, "a": 1}` (BC-3.02.001) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `Decode({"b":1,"a":2})` then `Dumps` | `{"b": 1, "a": 2}` | happy-path |
| `Decode({"x":1})`, `Set("y", 2.0)`, `Dumps` | `{"x": 1, "y": 2.0}` | happy-path |
| EC-002 sequence | `{"b": 5, "a": 9}` | edge-case |
| EC-003 raw surrogate pair | `Len` 2, `HasSurrogate` true | edge-case |
| `Get` on a missing key | Null | error |

Rows verified 2026-11-15 against CPython 3.11.7 (`json.loads`, dict assignment/deletion, `json.dumps`, `len`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | For random op sequences (Set/Delete), member order equals a Python dict driven by the same ops | proptest vs oracle replay |
| VP-TBD | `Dumps(Decode(b))` equals `json.dumps(json.loads(b))` byte for byte | fuzz + oracle |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/json.go` `Value`, `Member`, `Kind`, `Get/Set/Delete` (design §2.6) (filled by architect) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103; design IM-01 (ordered objects, WTF-8 strings), IM-03 (insertion order in caches); pitfalls PR-11, PR-19. Legacy semantics it reproduces: dict copy SL:327, cache writes SL:203 via `save_cache` |

## Related BCs (Recommended)

- BC-5.02.003 — composes with (Decode builds Values)
- BC-5.02.001 — consumed by (DumpsLen walks Values in order)
- BC-5.03.001 — related to (`Len` over these strings)
- BC-1.04.020, BC-1.06.001 — consumed by (cache key order)

## Architecture Anchors (Recommended)

- `architecture/TBD.md#pyfmt-json` — Value model (filled by architect)

## Story Anchor (Recommended)

TBD — pyfmt json (design step S1)

## VP Anchors (Recommended)

- VP-TBD — dict-order equivalence
