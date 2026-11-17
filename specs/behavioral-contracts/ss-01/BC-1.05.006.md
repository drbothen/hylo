---
document_type: behavioral-contract
level: L3
version: "1.3"
status: draft
producer: product-owner
timestamp: 2026-11-17T15:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "24b0715"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:record_cost (SL:224-237)"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-079"
parity_class: "OD-30"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified: ["1.3 2026-11-17: pass-2 remediation ADV-P2-C2-01/14 (H1 now describes Go postconditions)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.05.006: Numeric sid keyed by string form — throttle and self-exclusion hold

## Description

**Approved deviation (OD-30, named exclusion per OD-105/OD-110).** When stdin's
`session_id` is a JSON number (or `true`), legacy stores it under a non-string dict
key that JSON turns into a string on disk, so on later refreshes its throttle lookup
misses, the file gains a duplicate key, and the session counts in its own
percentiles. hylo instead keys the session by the **string form** of the sid
everywhere in the cost history: one key per sid, throttle applies, self-exclusion
works. Claude Code always sends string session ids, so this shape is non-production.

## Preconditions

1. `session_id` is truthy and hashable but not a string: an int (e.g. `777`), a float
   (e.g. `1.5`) or `true`. (Falsy values never record, BC-1.05.004; unhashable values
   degrade, CP-S15.)
2. The cost segment exists and the lane is known, so `record_cost` and
   `cost_thresholds` run.
3. `transcript_path` is absent or not a file, so `_mix_counts` returns before its
   `re.sub` sid sanitize (early return SL:1010-1011; `re.sub` SL:1017). With a transcript present, legacy's numeric-sid
   refresh raises TypeError in `re.sub` and degrades (CP-S14, BC-1.03.013 EC-007) while
   the string sid renders normally, so the equality claims below are restricted to the
   no-transcript case.

## Postconditions

1. **String-form key (Go).** The sid key is the string JSON would emit for that value
   as an object key: a string unchanged; an int as decimal digits (`777` → `"777"`); a
   float as Python `repr` (`1.5` → `"1.5"`, `1e16` → `"1e+16"`; non-finite floats are
   pinned to `repr` spelling `nan`/`inf`/`-inf`, although JSON key emission would spell
   them `NaN`/`Infinity` — the `repr` rule wins); `true` → `"true"`.
   It is computed with `internal/pyfmt` (OD-103).
2. **Record (Go).** `record_cost` looks up, throttles and writes under that one string
   key, so the file never holds two equal keys and the throttle applies as for a
   string sid (BC-1.05.004).
3. **Thresholds (Go).** `cost_thresholds` excludes the entry whose key equals the
   string form, so the session never counts in its own percentiles.
4. **Legacy behavior (reference, not reproduced).** Refresh 1 writes the int key,
   serialized `"777"`, and self-exclusion fails (`"777" == 777` is false, SL:246), so the
   own entry counts. Refresh 2 loads `"777"`; `s.get(777)` misses (SL:230), the
   throttle never applies, and `json.dump` writes **two** `"777"` keys; `json.load` keeps
   the last, so the file stays at two duplicates on every later refresh.
5. Hence — when no transcript exists (Precondition 3) — Go output equals legacy's
   output for the **string** sid `"777"` on the same inputs (stdout and
   `cost-history.json`). With a transcript present legacy degrades on the numeric sid
   (CP-S14), so no equality is claimed there.

## Invariants

1. Exactly one cost-history key per session id in any Go-written file.
2. The session-cache **file name** is unaffected by this rule and stays byte-exact
   (`statusline-777.json`, BC-1.06.001).
3. The deviation is visible only for non-string sids; string sids are byte-exact.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | sid `777`, refresh 2 within 60 s | Go: throttled, no write, one `"777"` key; legacy: two `"777"` keys |
| EC-002 | sid `true` | key `"true"` (legacy also serializes `"true"`, then misses on reload) |
| EC-003 | sid `1.5` | key `"1.5"` |
| EC-004 | history already holds legacy duplicate `"777"` keys (legacy-written file) | Go's reader keeps the last occurrence (Python `json.load` semantics, `internal/pyfmt`), then writes one key |
| EC-005 | sid `"777"` (string) | not a deviation; byte-exact |

## Canonical Test Vectors

Seed: nine backfill entries `o0…o8`, lane anth, usd 10.0…18.0, api 3,600,000, ts =
now − 3600; now = 1794615009.0; model `claude-opus-5-5` (cloud lane); usd 30.0, api
3,600,000.

| Input | Expected Output | Category |
|-------|----------------|----------|
| sid `"777"` (string), refresh 1 | `\e[33m$30.00\e[0m\e[90m $30.0/h\e[0m` (9 others → cold start); one `"777"` key | happy-path |
| sid `777` (int), refresh 1 — Go | `\e[33m$30.00\e[0m\e[90m $30.0/h\e[0m`; one `"777"` key (legacy: `\e[31m$30.00\e[0m\e[31m $30.0/h\e[0m`, self counted → pair (16.0, 18.0)) | edge-case (deviation) |
| sid `777`, refresh 2 at now + 1 — Go | same stdout; file unchanged (throttled); legacy: two `"777"` keys, tail `…"777": {"lane": "anth", "usd": 30.0, "api_ms": 3600000, "ts": 1794615009.0, "src": "cc"}, "777": {"lane": "anth", "usd": 30.0, "api_ms": 3600000, "ts": 1794615010.0, "src": "cc"}}}` | edge-case (deviation) |
| sid `["x"]` | CP-S15 degrade (not this BC) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-020 | For any non-string hashable sid with no transcript present, Go output equals legacy output for `str_form(sid)` as a string sid (with a transcript legacy degrades on the numeric sid, CP-S14) | manual (paired oracle runs) |
| VP-020 | No Go-written cost history contains a duplicate key | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 |
| L2 Domain Invariants | DI-007, DI-012 (OD-30 named deviation) |
| Architecture Module | `internal/cost` history.go (`Record`/`ForLane` take the sid as a raw `pyfmt.Value`, design §2.3; BC-COMPONENT-MAP: internal/cost/history.go (numeric sid, OD-30) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:record_cost (SL:224-237, lookup SL:230); cost_thresholds (SL:240-262, compare SL:246) |
| Legacy contract | BC-SL-079 (P3 deep r1; refined P3r3 §4.2; re-confirmed P3r4 §1.1 with sid 777) |
| Decisions | **OD-30** (known difference: Go writes one key per sid; table test pins the string-form key), **OD-105** (named exclusion list), **OD-110** (every owner-ruled byte difference gets a named entry with its own table tests), OD-103 |
| Exclusion entry | `internal/statusline/testdata/parity/exclusions.json`: `{id: "OD-30", case: "numeric-session-id", expected_output_file: <Go-expected stdout + cost-history.json>, table_test: "TestCostHistory_OD30_NumericSidStringKey"}` — no glob; covers stdout and the cost-history cache-file comparison for numeric-sid cases only |
| Dedicated table test | `TestCostHistory_OD30_NumericSidStringKey` (rows: int, float, `true`, two-refresh throttle, legacy-duplicate reader) |

## Related BCs (Recommended)

- BC-1.05.004 — refines (record path for non-string sids)
- BC-1.05.005 — refines (self-exclusion for non-string sids)
- BC-1.05.009 — related to (OD-30 sub-case of the write format)
- BC-1.06.001 — related to (session-cache file name stays raw)
- BC-5.02.004 — depends on (ordered Value, last-wins duplicate keys)
- BC-6.03.004 — depends on (exclusion-list machinery)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#effect-step-script-design-doc-31-normative` — internal/cost/history.go (numeric sid, OD-30) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost history (filled by story-writer)

## VP Anchors (Recommended)

- VP-020 — string-form equivalence


#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (record_cost (SL:224-237, lookup SL:230); cost_thresholds (SL:246)) |
| **Confidence** | high — frontmatter confidence H; OD-30 pairing re-confirmed P3r4 §1.1 with sid 777 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: OD-30 pairing runs (numeric sid vs string form) executed on CPython 3.11.7 (2026-11-15); dict-key identity semantics are the subtle surface

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | writes via the injected `Store` seam |
| **Global state access** | none |
| **Deterministic** | yes (given samples and a store fake) |
| **Thread safety** | Safe for concurrent use (store injected) |
| **Overall classification** | boundary |

Owning component `internal/cost` (BC-COMPONENT-MAP: cost/history.go (numeric sid, OD-30) - ARCH-03); the ARCH-00 package table classifies the package boundary - pure percentile math; writes go through the injected `Store` seam.
