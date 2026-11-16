---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md
  - ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - ../semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-102"
parity_class: "OD-30"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.05.009: record_cost write contract (exact JSON format)

## Description

When `record_cost` writes (BC-1.05.004), hylo produces `cost-history.json` byte for
byte as legacy's `json.dump` would: default Python separators, ASCII escapes, Python
float `repr`, `NaN`/`Infinity` tokens, int/float preserved, inherited key order, no
trailing newline. The format is byte-exact for every string session id. The only
permitted difference is the **OD-30 sub-case** (non-string session id: one
string-form key instead of legacy's duplicates), specified in BC-1.05.006.

## Preconditions

1. `record_cost` passed its guard and throttle (BC-1.05.004).
2. The history value is the ordered `pyfmt.Value` loaded from the file (or `{}`), and
   the writer mutates it in place; Go structs with `encoding/json` are not used
   (design IM-03).
3. Encoding goes through `pyfmt.Dumps` (`internal/pyfmt` `[json]`, OD-103).

## Postconditions

1. Top level: the loaded object with every unknown key preserved in place; if
   `sessions` was absent it is appended as the last top-level key (SL:229).
2. The session entry is exactly, in this key order:
   `{"lane": <"dgx"|"anth">, "usd": <round(usd, 4)>, "api_ms": <api_ms | null>,
   "ts": <now>, "src": "cc"}` (SL:234-236).
3. `usd` = `round(usd, 4)` with CPython semantics (correctly rounded decimal,
   `pyfmt.RoundN`): a float stays a float (`12.345678` → `12.3457`, `1.00001` →
   `1.0`, `1e-5` → `0.0`); an int stays an int (`3` → `3`); `true` → `1` (int); `+inf`
   → `Infinity`.
4. `api_ms` is stored as given when it is a number (int stays int, float stays float,
   `true` stays `true`, NaN → `NaN`, inf → `Infinity`); any non-number → `null`.
5. `ts` is the float clock value in Python `repr` (`1794615009.0`).
6. Serialization: separators `", "` and `": "`; non-ASCII and lone surrogates escaped
   as `\uXXXX` (`ensure_ascii`); no trailing newline; written through the atomic save
   (BC-1.06.001: temp file mode 0600 in `paths.cache_dir`, then rename).
7. **OD-30 sub-case:** for a non-string session id the key is its string form and
   appears once (BC-1.05.006); legacy's duplicate-key output is not reproduced.

## Invariants

1. For string sids, Go-written bytes equal legacy-written bytes for the same loaded
   file, inputs and clock (cache-swap tests, BC-6.02.004).
2. The file name `cost-history.json` and the entry schema are frozen format constants
   (OD-106 copies this file at cutover; CAP-011 / OD-124: the status line owns the
   format).
3. An existing session key keeps its position; other entries are re-emitted unchanged
   (including foreign keys inside them).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | existing file `{"keep": 1}` | `{"keep": 1, "sessions": {…}}` |
| EC-002 | sid `café` | key `"café"` |
| EC-003 | sid holding a lone surrogate (from a JSON `\udce9` escape) | key `"x\udce9"` (escaped, no error) |
| EC-004 | usd `true`, api `1e-05` | `"usd": 1, "api_ms": 1e-05` |
| EC-005 | usd 3 (int), api `true` | `"usd": 3, "api_ms": true` |
| EC-006 | api NaN | `"api_ms": NaN` |
| EC-007 | re-record of key `b` that sits before key `a` | `b` stays first; `a` (even a foreign shape like `{"x": 1}`) re-emitted unchanged |
| EC-008 | non-string sid | OD-30 sub-case → BC-1.05.006 |
| EC-009 | save fails (unwritable dir) | nothing persisted, error swallowed (BC-1.06.001) |

## Canonical Test Vectors

Clock 1794615009.0.

| Input | Expected Output | Category |
|-------|----------------|----------|
| empty history; sid `fmt`, lane anth, usd 12.345678, api 654321.5 | `{"sessions": {"fmt": {"lane": "anth", "usd": 12.3457, "api_ms": 654321.5, "ts": 1794615009.0, "src": "cc"}}}` (no trailing newline) | happy-path |
| `{"keep": 1}`; sid `café` lane dgx usd 3 api `true`; then sid `x\udce9` lane anth usd 1.00001 api NaN | `{"keep": 1, "sessions": {"café": {"lane": "dgx", "usd": 3, "api_ms": true, "ts": 1794615009.0, "src": "cc"}, "x\udce9": {"lane": "anth", "usd": 1.0, "api_ms": NaN, "ts": 1794615009.0, "src": "cc"}}}` | edge-case |
| `{"sessions": {"b": {…backfill…}, "a": {"x": 1}}, "keep": 1}`; sid `b` usd `true` api 1e-05 | `{"sessions": {"b": {"lane": "anth", "usd": 1, "api_ms": 1e-05, "ts": 1794615009.0, "src": "cc"}, "a": {"x": 1}}, "keep": 1}` | edge-case |
| sid `777` (int), two refreshes | Go: one `"777"` key (OD-30, BC-1.05.006) | error (deviation) |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | `pyfmt.Dumps` equals CPython `json.dumps` (defaults) on generated ordered values incl. NaN/inf, ints, surrogates | fuzz (differential vs the oracle) |
| VP-TBD | Python-written file → Go record → bytes equal Python record on the same file (string sids) | manual (cache-swap test) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 |
| L2 Domain Invariants | DI-007 |
| Architecture Module | `internal/cost` history.go; `internal/pyfmt` json.go `Dumps` (filled by architect) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:record_cost (SL:224-237); cost_thresholds read (SL:245-246); save_cache json.dump (SL:203) |
| Legacy contract | BC-SL-102 (P3r3 §4.2; re-confirmed P3r4 §1.1); writer-format ruling (b) P3r2 §0 |
| Decisions | **OD-30** (numeric-sid sub-case: one string-form key), **OD-105/OD-110** (named exclusion entry `OD-30` / case `numeric-session-id`, dedicated test `TestCostHistory_OD30_NumericSidStringKey`, shared with BC-1.05.006), OD-101, OD-103, OD-106, OD-124 |
| Exclusion scope | Only non-string-sid cases are excluded; every string-sid case is compared byte for byte on stdout and `cost-history.json` |

## Related BCs (Recommended)

- BC-1.05.004 — refines (bytes of the write)
- BC-1.05.006 — related to (OD-30 sub-case)
- BC-1.06.001 — depends on (atomic save)
- BC-5.01.001 — depends on (`RoundN`)
- BC-5.02.004 — depends on (ordered Value)
- BC-6.02.004 — verified by (cache-swap coverage)

## Architecture Anchors (Recommended)

- `architecture/[cost].md#history-format` — (filled by architect)

## Story Anchor (Recommended)

S-N.MM — cost history (filled by story-writer)

## VP Anchors (Recommended)

- VP-TBD — Dumps differential equivalence
