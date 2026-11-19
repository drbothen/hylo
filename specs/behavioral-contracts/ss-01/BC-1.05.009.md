---
document_type: behavioral-contract
level: L3
version: "1.4.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T18:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "27cb4d8"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:record_cost (SL:224-237)"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-102"
parity_class: "OD-30, OD-166"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified:
  - "2026-11-18 (v1.3.1) pass-4 remediation ADV-P4-C2-05 (Description and exclusion scope list both permitted differences: OD-30 sub-case and OD-166 record skip; EC-010; parity_class)"
  - "2026-11-18 (v1.3.2) pass-5 remediation ADV-P5-C2-06 (Decisions-row riding-test name aligned to the canonical TestCostHistory_OD166_RecordGuard)"
  - "2026-11-18 (v1.3.3) pass-8 remediation ADV-P8-C2-07 (Dumps-differential fuzz row rerouted to VP-024, the pyfmt JSON-equivalence VP whose bcs gains BC-1.05.009, per pass-8 call 12; cache-swap row keeps VP-020/VP-019)"
  - "2026-11-18 (v1.3.4) pass-9 remediation ADV-P9-C2-04 (VP-012 closure rows for OD-30 and OD-166 in the VP table + VP Anchors line) and cross-references updated to BC-1.05.004 PC4 (OD-166 skip moved to the write step, ADV-P9-C2-03)"
  - "2026-11-21T12:15:00Z (v1.4.0) pass-13 sync closure — Owning component line and Purity Classification I/O cell respelled to the ARCH-03 declared cost API (§Interfaces, 'package internal/cost — DECLARED API'): internal/cost is pure core with no I/O; internal/statusline loads and saves the cost-history file through its CacheStore (sync-check adv-p13 finding 1, call-7 residual); no behavioral change"
  - "2026-11-21T13:00:00Z (v1.4.1) pass-14 remediation ADV-P14-C2-04 (the declared symbol RecordCost respelled in the Owning-component line) + ADV-P14-C2-05 (Purity Classification respelled: pure core, no store fake, no injected seam; no behavioral change)"
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
trailing newline. The format is byte-exact for every string session id. Exactly two
differences are permitted, and only these (ADV-P4-C2-05): the **OD-30 sub-case**
(non-string session id: one string-form key instead of legacy's duplicates, specified
in BC-1.05.006) and the **OD-166 record skip** (BC-1.05.004 PC4: a refresh whose
numeric `usd` or `api_ms` cannot convert to float writes **no entry** where legacy
persisted the raw int — an absent-entry byte divergence, sign-agnostic and
gate-independent; decided at the write step, after load and lookup, ADV-P9-C2-03).

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
| EC-002 | sid `café` | key `"caf\u00e9"` — `ensure_ascii` escapes the non-ASCII key on disk (legacy `json.dump` default, SL:203) |
| EC-003 | sid holding a lone surrogate (from a JSON `\udce9` escape) | key `"x\udce9"` (escaped, no error) |
| EC-004 | usd `true`, api `1e-05` | `"usd": 1, "api_ms": 1e-05` |
| EC-005 | usd 3 (int), api `true` | `"usd": 3, "api_ms": true` |
| EC-006 | api NaN | `"api_ms": NaN` |
| EC-007 | re-record of key `b` that sits before key `a` | `b` stays first; `a` (even a foreign shape like `{"x": 1}`) re-emitted unchanged |
| EC-008 | non-string sid | OD-30 sub-case → BC-1.05.006 |
| EC-009 | save fails (unwritable dir) | nothing persisted, error swallowed (BC-1.06.001) |
| EC-010 | unconvertible `usd`/`api_ms` (OD-166, BC-1.05.004 PC4) | no entry written at all — the skip is decided before this contract applies; this contract governs only the bytes of writes that happen |

## Canonical Test Vectors

Clock 1794615009.0.

| Input | Expected Output | Category |
|-------|----------------|----------|
| empty history; sid `fmt`, lane anth, usd 12.345678, api 654321.5 | `{"sessions": {"fmt": {"lane": "anth", "usd": 12.3457, "api_ms": 654321.5, "ts": 1794615009.0, "src": "cc"}}}` (no trailing newline) | happy-path |
| `{"keep": 1}`; sid `café` lane dgx usd 3 api `true`; then sid `x\udce9` lane anth usd 1.00001 api NaN | `{"keep": 1, "sessions": {"caf\u00e9": {"lane": "dgx", "usd": 3, "api_ms": true, "ts": 1794615009.0, "src": "cc"}, "x\udce9": {"lane": "anth", "usd": 1.0, "api_ms": NaN, "ts": 1794615009.0, "src": "cc"}}}` | edge-case |
| `{"sessions": {"b": {…backfill…}, "a": {"x": 1}}, "keep": 1}`; sid `b` usd `true` api 1e-05 | `{"sessions": {"b": {"lane": "anth", "usd": 1, "api_ms": 1e-05, "ts": 1794615009.0, "src": "cc"}, "a": {"x": 1}}, "keep": 1}` | edge-case |
| sid `777` (int), two refreshes | Go: one `"777"` key (OD-30, BC-1.05.006) | error (deviation) |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-024 | `pyfmt.Dumps` equals CPython `json.dumps` (defaults) on generated ordered values incl. NaN/inf, ints, surrogates | fuzz (differential vs the oracle) (routed to VP-024, the pyfmt JSON-equivalence differential — pass-8 call 12; VP-020/VP-019 had no fuzz leg) |
| VP-020, VP-019 | Python-written file → Go record → bytes equal Python record on the same file (string sids) | manual (cache-swap test) |
| VP-012 | The named deviation this contract carries — exclusion id `OD-30` (non-string sid: one string-form key, BC-1.05.006) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-30` entry and its riding table test `TestCostHistory_OD30_NumericSidStringKey`, and the mutation test fails closed if that entry is dropped | property test (VP-012 `TestParityExclusions_ClosedSet` / `TestParityExclusions_MutationFailClosed`, go test) |
| VP-012 | The named deviation this contract carries — exclusion id `OD-166` (a refresh whose numeric `usd` or `api_ms` cannot convert to float writes no entry where legacy wrote one; the absent entry is the excluded divergence) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-166` entry and its riding table test `TestCostHistory_OD166_RecordGuard`, and the mutation test fails closed if that entry is dropped | property test (VP-012, go test; OD-169) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 |
| L2 Domain Invariants | DI-007, DI-012 (OD-30 sub-case deviation; OD-166 record skip) |
| Architecture Module | `internal/cost` history.go; `internal/pyfmt` json.go `Dumps` (BC-COMPONENT-MAP: internal/cost/history.go (exact write format) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:record_cost (SL:224-237); cost_thresholds read (SL:245-246); save_cache json.dump (SL:203) |
| Legacy contract | BC-SL-102 (P3r3 §4.2; re-confirmed P3r4 §1.1); writer-format ruling (b) P3r2 §0 |
| Decisions | **OD-30** (numeric-sid sub-case: one string-form key), **OD-105/OD-110** (named exclusion entry `OD-30` / case `numeric-session-id`, dedicated test `TestCostHistory_OD30_NumericSidStringKey`, shared with BC-1.05.006), OD-101, OD-103, OD-106, OD-124, **OD-166/OD-169** (record skip: unconvertible `usd`/`api_ms`, exclusion entry `OD-166`, dedicated table test `TestCostHistory_OD166_RecordGuard`) |
| Exclusion scope | Only non-string-sid cases (OD-30) and entries a refresh skips under the OD-166 record guard (BC-1.05.004 PC4) are excluded; every other string-sid case is compared byte for byte on stdout and `cost-history.json` — the absent OD-166 entry itself is the excluded divergence |

## Related BCs (Recommended)

- BC-1.05.004 — refines (bytes of the write)
- BC-1.05.006 — related to (OD-30 sub-case)
- BC-1.06.001 — depends on (atomic save)
- BC-5.01.001 — depends on (`RoundN`)
- BC-5.02.004 — depends on (ordered Value)
- BC-6.02.004 — verified by (cache-swap coverage)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#effect-step-script-design-doc-31-normative` — internal/cost/history.go (exact write format) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost history (filled by story-writer)

## VP Anchors (Recommended)

- VP-024 — Dumps differential fuzz (pass-8 call 12); VP-020, VP-019 — cache-swap parity (row 2)
- VP-012 — exclusion-closure cover for the named deviations `OD-30` and `OD-166`


#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (record_cost (SL:224-237); save_cache json.dump (SL:203)) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: isinstance filters on usd/api_ms (SL:226, 235)
- **documentation**: key order and entry schema frozen (D7/AP-16)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none in hylo — the legacy function writes the history file; per ARCH-03's declared cost API (§Interfaces, 'package internal/cost — DECLARED API') the in-place mutation of the loaded ordered value and its `pyfmt.Dumps` encoding are pure, and `internal/statusline` loads and saves the file through its `CacheStore` |
| **Global state access** | none |
| **Deterministic** | yes (given the loaded history, session entry and `now` passed in) |
| **Thread safety** | Safe for concurrent use (pure) |
| **Overall classification** | pure core |

Owning component `internal/cost` (BC-COMPONENT-MAP: cost/history.go (exact write format) - ARCH-03); per ARCH-03's declared cost API ('package internal/cost — DECLARED API' in the §Interfaces section, ADV-P13-A02 / orchestrator call 7), the package is pure core with no I/O — `RecordCost` mutates the loaded ordered value in place and `pyfmt.Dumps` emits the bytes, and `internal/statusline` loads and saves the cost-history file through its `CacheStore`.
