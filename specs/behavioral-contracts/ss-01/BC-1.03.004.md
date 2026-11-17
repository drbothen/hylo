---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T00:30:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "64c1eaa"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1059-1063)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-033"
parity_class: "byte-exact"
confidence: "M"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: VP citation reconciliation — VP-038", "1.2.2 2026-11-17: depth-limit correction 989/990 (SC-01..02) + VP-006 citation (SC-06)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.004: bytes.splitlines + per-line json.loads

## Description

The complete-line window `blob[:cut]` is split exactly like Python `bytes.splitlines()` (on `\n`, `\r\n` and `\r`
only) and each piece is decoded exactly like `json.loads(bytes)`. A piece that fails to decode, for any reason, is
skipped silently and changes no parser state. Decoded pieces go on to the turn machine, usage and composition
steps. The decoder acceptance set is owned by `pyfmt.Decode(ModeBytes)` (BC-5.02.003); this BC fixes how the
transcript parser uses it.

## Preconditions

1. `blob[:cut]` from BC-1.03.003 (bytes; may contain any byte values).
2. `pyfmt.SplitLinesBytes` (BC-5.03.002) and `pyfmt.Decode(..., ModeBytes)` (BC-5.02.003) are available.

## Postconditions

1. Pieces are produced in file order by splitting on `\r\n` (as one separator), `\n`, or `\r`. No other byte or
   code point splits: not `\v` (0x0B), `\f` (0x0C), 0x1C-0x1E, U+0085 (`C2 85`), U+2028, U+2029.
2. Empty pieces (consecutive separators) are passed to the decoder, fail, and are skipped.
3. Each piece is decoded with `json.loads(bytes)` semantics: UTF-8 BOM accepted at the start of the piece;
   UTF-16/32 detection; invalid UTF-8 fails; leading/trailing JSON whitespace (space, tab, CR, LF) allowed;
   `NaN`, `Infinity`, `-Infinity` and overflowing literals (`1e400` → inf) accepted; duplicate keys last-wins in
   first position; lone surrogate escapes kept; integers exact; nesting at CPython 3.11's recursion limit fails
   (depth 989 accepted, 990 rejected at the `_mix_counts` site, measured on the legacy oracle; call-context
   dependent — stdin sits at 993/994; BC-5.02.003, VP-006).
4. A failed decode skips the piece: no change to `res/conv/think`, `tin/tout/c_wr/c_rd/c_in`, `rb`, `pp`, `cur`,
   `lr`, `lu`, ids. Its bytes are still consumed (the offset is already set past `cut`, BC-1.03.003).
5. A successfully decoded piece is processed by the downstream steps in this order: turn machine (BC-1.03.010),
   compaction check (BC-1.03.008), usage (BC-1.03.005/006/007), composition (BC-1.03.009). A decoded value that
   is not an object, or has a wrong-shape field, is handled by the D4-EX-2 W-predicates (BC-1.03.018), not here.

## Invariants

1. The splitter operates on bytes, before any UTF-8 decoding (a `\r` inside a multi-byte sequence cannot occur
   in valid UTF-8; in invalid bytes it still splits).
2. Decode failure is never a degraded refresh (legacy catches every exception at SL:1062).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Two records separated by a bare `\r`, final LF | two pieces, both counted |
| EC-002 | Two records separated by `\x0b` | one piece, invalid JSON → skipped (both records lost) |
| EC-003 | Two records separated by `C2 85` (U+0085) | one piece → skipped |
| EC-004 | Raw U+2028 inside a JSON string | one piece; the string keeps the character (counts 1 code point) |
| EC-005 | UTF-8 BOM before a record | accepted |
| EC-006 | A record containing byte `0xFF` | skipped; neighbors unaffected |
| EC-007 | `NaN` literal anywhere in a record | accepted |
| EC-008 | Torn record (truncated JSON) followed by LF | skipped; offset moves past it permanently |
| EC-009 | Nesting depth limit/limit+1: 989 accepted, 990 skipped | 990 skipped (Go's `encoding/json` limit of 10,000 must not be used) |

## Canonical Test Vectors

Each transcript below is the exact byte string shown (Python bytes notation), parsed once from offset 0; the
expected `conv` and cache `size` were re-pinned 2026-11-15 with the legacy oracle.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `{"message":{"content":"ab"}}\r{"message":{"content":"cde"}}\n` | conv 5, size 59 | happy-path |
| `{"message":{"content":"ab"}}\r\n{"message":{"content":"cde"}}\n` | conv 5, size 60 | happy-path |
| `{"message":{"content":"ab"}}\x0b{"message":{"content":"cde"}}\n` | conv 0, size 59 | edge-case |
| `{"message":{"content":"ab"}}\xc2\x85{"message":{"content":"cde"}}\n` | conv 0, size 60 | edge-case |
| `{"message":{"content":"a` U+2028 (raw, `e2 80 a8`) `b"}}\n` | conv 3, size 32 | edge-case |
| `\xef\xbb\xbf{"message":{"content":"bom"}}\n` | conv 3, size 33 | edge-case |
| `{"message":{"content":"\xff"}}\n{"message":{"content":"ok"}}\n` | conv 2, size 57 | error |
| `\n\n{"message":{"content":"ok"}}\n` | conv 2, size 31 | edge-case |
| `{"message":{"content":"ok"},"x":NaN}\n` | conv 2, size 37 | edge-case |
| `{"message":{"content":"ok"\n` | conv 0, size 27 (written; offset advanced) | error |
| `  {"message":{"content":"ok"}}  \n` | conv 2, size 33 | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-038 | `SplitLinesBytes` equals CPython `bytes.splitlines()` on random byte strings (split points, ends-retained pieces, losslessness) | fuzz (differential vs oracle) |
| VP-006 | Per-call-site JSON depth budget holds at this site's edge: depth 989 accepted, 990 rejected (justified: EC-009's depth edge case is the transcript-site instance of VP-006's per-call-site budget obligation) | fuzz (boundary L/L+1 vs oracle) |
| VP-029 | A skipped piece leaves the parser state bit-identical | Go property test (testing/quick) (state snapshot before/after) |
| VP-029 | Go and legacy agree on random transcripts mixing valid, torn and invalid-UTF-8 records | fuzz (Tier C) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007, DI-008 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1059-1063) |
| Legacy contract | BC-SL-033 (base; refined pass-3 r1 with BC-SL-067 decoder edges) |
| Parity class | byte-exact |
| Confidence note | M — decoder edge set (design §8) |
| Architecture Module | `internal/statusline/transcript.go`; helpers `internal/pyfmt` (OD-103) |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-5.02.003 — depends on: `json.loads(bytes)` acceptance set
- BC-5.03.002 — depends on: `SplitLinesBytes`
- BC-1.03.018 — composes with: decoded-but-wrong-shape lines skipped under D4-EX-2
- BC-1.03.003 — depends on: the complete-line window

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript.go (splitlines + per-line decode) (`pyfmt.Decode(ModeBytes)` (design IM-01)) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-038 — splitlines differential (dedicated differential VP; family table still VP-029)
- VP-006 — per-call-site JSON depth budget (transcript site edge: 989 accepted / 990 rejected)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1059-1063) |
| **Confidence** | high (mechanism); medium (decoder edge breadth) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `except Exception: continue` (SL:1062-1063)
- **type constraint**: `blob` is `bytes`, so `bytes.splitlines` (not `str.splitlines`) applies (SL:1059)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; suitable for differential fuzzing against the oracle.
