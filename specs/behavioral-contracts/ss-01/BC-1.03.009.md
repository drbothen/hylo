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
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1120-1149)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-038"
parity_class: "byte-exact"
confidence: "M"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: image_chars valid range >= 0 (OD-162; ADV-P2-C03)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.009: Composition per block from json.dumps lengths

## Description

For every processed (non-boundary, non-skipped) line, the parser adds character counts to three composition
buckets: `res` (tool results and images), `conv` (conversation: message text, assistant text, tool_use payloads)
and `think` (thinking). Lengths are Python code-point counts of strings, or of Python `json.dumps` output for
structured values; images count a fixed `image_chars` (2,000). The buckets are byte-proportional estimates that
feed the `▤❙◈` composition widget.

## Preconditions

1. A decoded object line that reached the composition step (after the turn machine, the boundary check and the
   usage step); `msg = e.message or {}`; `content = msg.content`.
2. `IMG = statusline.composition.image_chars` (default 2000; T-059, rationale: judgment/owner-confirmed — review
   #6.3 records the decision "nested images = 2,000", not a derivation). **Valid range (OD-162): `>= 0`**, derived
   from legacy semantics — IMG is a fixed per-image byte estimate summed into `res` (SL:1137, 1149); out-of-range
   values are number-range config errors (S2 schema, OD-114).
3. `DumpsLen` = `len(json.dumps(x))` with Python defaults (BC-5.02.001, 63-case oracle BC-5.02.002); `Len` = code
   points, a lone surrogate counts 1 (BC-5.03.001).

## Postconditions

1. `content` is a string → `conv += Len(content)`; stop.
2. `content` is not a list (object, number, null, missing) → nothing; stop.
3. `content` is a list → for each element in order; non-object elements are ignored; for an object `blk` with
   `bt = blk.type`:
   - `tool_result`: `inner = blk.content`; string → `n = Len(inner)`; list → `n = Σ (IMG if item is an object with
     type == "image" (case-sensitive) else DumpsLen(item))`; null or missing → 0; any other value →
     `DumpsLen(inner)`; then `res += n`.
   - `text` → `conv += len(blk.text or "")`; `thinking` → `think += len(blk.thinking or "")` (value types per
     BC-1.03.014).
   - `tool_use` → `conv += DumpsLen(blk.input or "")` (falsy input → `""` → 2).
   - `image` → `res += IMG`.
   - any other type, or no type → nothing.
4. Counts are added to the current buckets (cached or reset by BC-1.03.002/008) and written to the cache as ints.

## Invariants

1. Composition is counted for every processed line, including lines whose usage was deduplicated.
2. `DumpsLen` is computed on the decoded value (integers exact, float `repr`, `ensure_ascii` escaping, `", "` /
   `": "` separators, no HTML escaping, duplicate keys collapsed last-wins).
3. Tool_result list items have **no** `or ""` fallback (`{}` 2, `0` 1, `false` 5, `null` 4), while a non-list inner
   `null` counts 0.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | String content `"é😀ab"` | conv 4 (code points, not bytes or UTF-16 units) |
| EC-002 | Content is an object | ignored |
| EC-003 | tool_result list `[image, {"type":"text","text":"hi"}, "raw"]` | res 2000 + 30 + 5 = 2035 |
| EC-004 | tool_result object `{"k":"é"}` | res 15 (`é` escaping) |
| EC-005 | tool_result content `0` / `false` | res 1 / 5 |
| EC-006 | tool_result list items `{}`,`[]`,`""`,`0`,`-0.0`,`false`,`null`,`{"type":"IMAGE"}` | res 2+2+2+1+4+5+4+17 = 37 |
| EC-007 | tool_use input `{}` or missing | conv 2 |
| EC-008 | Unknown block type `redacted_thinking`, block without type | nothing |
| EC-009 | Non-object list elements (`"abc"`, `1`, `null`, nested list) | ignored |

## Canonical Test Vectors

Each row: one line `{"type": "assistant", "message": {"content": <content>}}` (or the stated message), parsed
from offset 0; result `res/conv/think`. Re-pinned 2026-11-15 with the legacy oracle.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `[{"type":"text","text":"abc"},{"type":"thinking","thinking":"wxyz"}]` | res 0, conv 3, think 4 | happy-path |
| `[{"type":"tool_use","input":{"command":"ls"}}]` | conv 17 | happy-path |
| `[{"type":"tool_result","content":[{"type":"image","source":{"data":"x…"}},{"type":"text","text":"hi"},"raw"]}]` | res 2035 | happy-path |
| `[{"type":"tool_result","content":{"k":"é"}}]` | res 15 | edge-case |
| `[{"type":"tool_result","content":"héllo"}]` | res 5 | edge-case |
| `[{"type":"tool_result","content":[{},[],"",0,-0.0,false,null,{"type":"IMAGE"}]}]` | res 37 | edge-case |
| `[{"type":"tool_use","input":{"a":"é"}}]` | conv 15 | edge-case |
| `[{"type":"image","source":{}}]` | res 2000 | edge-case |
| `["abc",1,null,[{"type":"text","text":"zz"}]]` | all 0 | edge-case |
| message `{"content": "é😀ab"}` | conv 4 | edge-case |
| message `{"content": {"text": "abc"}}` | all 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | Bucket deltas equal the oracle's for random block lists | fuzz (Tier C differential) |
| VP-029 | `DumpsLen` equals CPython on the 63-case table | table test (BC-5.02.002) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 (KD-003 composition) |
| L2 Domain Invariants | DI-007 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1120-1149) |
| Legacy contract | BC-SL-038 (base; refined pass-3 r1 with BC-SL-071 pinned lengths) |
| Threshold | T-059 → `statusline.composition.image_chars` = 2000 |
| Parity class | byte-exact |
| Confidence note | M — `DumpsLen` over decoded values (design §8) |
| Architecture Module | `internal/statusline/transcript_mix.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.014 — composes with: `text`/`thinking` value types
- BC-5.02.001 / BC-5.02.002 — depends on: `json.dumps` length rules and oracle
- BC-5.03.001 — depends on: code-point `Len`
- BC-1.02.007 — related to: composition percentage rendering

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript_mix.go (dumps lengths) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript composition

## VP Anchors (Recommended)

- VP-029 — composition differential

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1120-1149) |
| **Confidence** | high (rules); medium (`json.dumps` surface) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance` checks SL:1121, 1124, 1127, 1132, 1134
- **documentation**: SL:1135-1136 (nested images), SL:1147, 1149

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; share `DumpsLen` with the cache encoder so escaping and float repr cannot drift (design IM-04).
