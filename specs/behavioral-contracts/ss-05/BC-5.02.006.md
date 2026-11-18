---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
input-hash: "b5ce211"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces json.dump cache-file bytes; ruling (b) P3r2 §0)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z ADV-P3 remediation D10+D12: Dumps scoped to include the subagent stdout json.dumps (SL:924, BC-1.07.004); encoder failure on 4300-digit ints = typed ErrValue and legacy no-write"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.02.006: pyfmt.Dumps: json.dump cache-file bytes (separators, ensure_ascii, float repr, order)

## Description

`pyfmt.Dumps(v Value) ([]byte, error)` (json.go, design IM-03) reproduces CPython `json.dump`
defaults byte for byte over an ordered `Value`: separators `", "` and `": "`, ensure_ascii
escaping, `NaN`/`Infinity` tokens, float repr per BC-5.01.005, int-versus-float preserved,
insertion order — for the four cache files (session, mix, git, cost-history) AND the
subagent stdout line (`json.dumps` at SL:924, BC-1.07.004's NDJSON wire; ADV-P3-D10).
Go structs with `encoding/json` are banned for caches: they reorder keys and reformat floats (ruling
(b), P3r2 §0). Helper-level contract per OD-141.

## Preconditions

1. `v` is an ordered `Value` loaded per IM-01 (insertion order from the file read earlier;
   mutations preserve positions).
2. Ordered-`Value` semantics (Set/Delete keep positions; WTF-8 strings) per BC-5.02.004.

## Postconditions

1. Output equals CPython `json.dumps(obj)` defaults for every `Value` the cache writers
   produce: member order = `Value` insertion order; `, ` / `: ` separators; strings
   escaped ensure_ascii (non-ASCII → `\uXXXX` plus the standard two-char escapes);
   `NaN`/`Infinity` tokens; floats via Repr (`1794615009.0`, `1e-05`); the int-versus-float
   distinction preserved (BC-SL-102).
2. Shared primitive with `DumpsLen` (IM-04): both emit/count the same bytes, so the
   composition counter and the cache writer cannot drift.
3. The cache writers assemble/mutate the `Value` and emit via Dumps; no `encoding/json`
   marshal path exists for the four caches (D15: no second encoder).
4. Equal to CPython for the generated cache-value table (realistic cache shapes loaded,
   mutated, emitted) under the pinned oracle (OD-104).
5. **Encoder failure** (ADV-P3-D12): an int past the 4,300-digit encoder limit (accumulated
   token sums can reach it; SL:202-203 raises `ValueError` there) returns typed `ErrValue`
   and the calling cache writer performs the legacy no-write — error swallowed, the
   partial temp file leaks exactly as legacy's does (covered by the temp-file exclusion
   class) and the previous cache file is left untouched. `Dumps` never writes a partial
   destination itself (it returns bytes; the writer owns the file).

## Invariants

1. Insertion order, including order inherited from `entry = dict(c)` (SL:327) and the
   appended `fetch_ts, up, ts, sample, hist` keys (SL:349, BC-SL-091).
2. No trailing newline; the writer does not add one.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `Dumps(decode('{"b":1,"a":2}'))` | `{"b": 1, "a": 2}` (source order) |
| EC-002 | float thresholds survive | `{"a": 1e-05}` for source `{"a":1e-5}` |
| EC-003 | Value holding NaN/±Inf | `{"a": NaN}` / `{"a": Infinity}` tokens |
| EC-004 | int-vs-float preserved: `{"a":1}` vs `{"a":1.0}` | `{"a": 1}` vs `{"a": 1.0}` |
| EC-005 | WTF-8 str member with a lone surrogate | re-escaped `\udXXX` (BC-5.02.003) |
| EC-006 | Nested empty containers | `{"a": {}, "b": []}` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|---|---|---|
| `Dumps(load('{"b":1,"a":2}'))` | bytes `{"b": 1, "a": 2}` | happy-path |
| `Dumps(load('{"a":1.0}'))` | bytes `{"a": 1.0}` | edge-case |
| `Dumps(Value with NaN)` | bytes `{"a": NaN}` | edge-case |
| `Dumps(load('{"a":1e-5}'))` | bytes `{"a": 1e-05}` | edge-case |

Pinned against CPython 3.11 (OD-104 oracle discipline; realistic cache shapes from the
corpus cases).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-024 | Dumps output equals CPython `json.dumps` bytes for every corpus cache shape | CPython oracle table |
| VP-024 | Dumps and DumpsLen agree byte-for-byte on shared shapes | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-03; pitfalls PR-07/PR-08/PR-19; ruling (b) P3r2 §0 |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| L2 Domain Invariants | DI-012 (byte parity machinery) |
| Architecture Module | `internal/pyfmt` json.go (BC-COMPONENT-MAP: internal/pyfmt/json.go (Dumps) — ARCH-06) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.02.004 — composes with (ordered-Value semantics)
- BC-5.01.005 — composes with (Repr)
- BC-1.06.001, BC-1.05.009, BC-1.03.002, BC-1.02.013 — consumers (the four cache writers)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#json` — internal/pyfmt/json.go (Dumps) (json.go helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

S-TBD — pyfmt json helpers

## VP Anchors (Recommended)

- VP-024 — cache-byte equality

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/json.go (Dumps)` (BC-COMPONENT-MAP: py/json.go (Dumps) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
