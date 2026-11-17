---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T21:21:12Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "c2f799c"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1104-1112)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-035"
parity_class: "byte-exact"
confidence: "M"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: CP-T08 overflow skip (OD-156) + 4,300-digit save failure (ADV-P2-C01/C02); oracle re-verified", "1.2.2 2026-11-17: overflow crash path cited by taxonomy id CP-O06 (OD-156 register)", "1.2.2 2026-11-17: overflow crash path cited by taxonomy id CP-O06 (OD-156 register), 2026-11-17T21:21:41Z"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.006: Usage accumulation across int/float/big-int

## Description

For every counted usage object (BC-1.03.005), the parser adds its token fields to the session totals with Python
numeric semantics: each field defaults to 0 when missing or falsy, and the sums keep the Python type of the
operands (int stays an exact arbitrary-precision int, any float makes the sum a float, `true` counts as 1). The
totals are cumulative for the session and are **not** reset at compaction.

## Preconditions

1. `u` is a counted usage object (BC-1.03.005) whose four fields `input_tokens`, `cache_creation_input_tokens`,
   `cache_read_input_tokens`, `output_tokens` are each falsy or an int/float/bool. (A truthy non-number field is
   the CP-T04 shape and the line is skipped, BC-1.03.018.)
2. Accumulators `tin`, `c_in`, `c_wr`, `c_rd`, `tout` hold the cached values (int, float or big int; 0 after reset).

## Postconditions

1. `_i = u.input_tokens or 0`, `_w = u.cache_creation_input_tokens or 0`, `_r = u.cache_read_input_tokens or 0`
   (falsy: missing, null, `0`, `0.0`, `false`, `""`, `[]`, `{}` → integer 0).
2. `tin += _i + _w + _r` (left-to-right Python addition: `(_i + _w) + _r`, then added to `tin`); `c_in += _i`;
   `c_wr += _w`; `c_rd += _r`; `tout += u.output_tokens or 0`.
3. Type rules (Python `Num` arithmetic, design IM-02): int + int = exact int (no overflow, no float64 rounding);
   anything + float = float (IEEE 754 double); `true` = 1, `false` = 0 (falsy → int 0); NaN propagates; negative
   values are added as-is. **Exception (overflow, CP-O06):** when an int operand whose magnitude exceeds the
   float64 maximum (DBL_MAX ≈ 1.7976e308; JSON admits ints up to 4,300 digits) meets a float operand, Python
   raises `OverflowError` ("int too large to convert to float"; oracle-verified 2026-11-17 for `+`, `−`, `×`, `÷`)
   instead of producing a float — e.g. `input_tokens: 1.5` accumulated onto a 310-digit `cache_creation_input_tokens`
   (SL:1108), or a float `tin` plus a huge int. Legacy degrades (crash path CP-O06, BC-1.03.018); hylo **skips the
   line** (owner ruling OD-156, extending D4-EX-2 like ruling Q-c; exclusion id `OD-156`), covered by dedicated Go
   table tests.
4. The cache stores each total in Python `json.dump` form: ints as decimal digits of any length **up to the CPython
   int↔str conversion limit (`sys.get_int_max_str_digits()` = 4,300; oracle-verified 2026-11-17)**, floats as `repr`
   (`1.5`, `2.0`, `1e+16`), `NaN`/`Infinity` as bare tokens.
5. **Digit-limit save failure (EC-009):** when any serialized accumulator exceeds 4,300 decimal digits (e.g. two
   counted 4,300-digit `input_tokens` summing to 4,301 digits, oracle-verified), CPython `json.dump` raises
   `ValueError` mid-write (after partial content has reached the stream); `save_cache` swallows it, so the mix cache
   is **not written** and keeps its previous bytes, and the failure repeats every refresh while the totals stay
   above the limit. hylo reproduces the **no-write** observable; the temp-file disposition is ruled by OD-163
   (BC-1.06.001 EC-010).
5. A `compact_boundary` line does not change these totals (BC-1.03.008).

## Invariants

1. `tin = c_in + c_wr + c_rd` holds whenever all values are ints (float rounding may break exact equality).
2. Totals are monotone non-decreasing only if the transcript has no negative token values (not enforced).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `input_tokens: 1.5` | `tin` 1.5, `c_in` 1.5 (float) |
| EC-002 | `input_tokens: 12345678901234567890` (> 2^63) | stored exactly as `12345678901234567890` |
| EC-003 | `input_tokens: true, output_tokens: true` | `tin` 1, `tout` 1 (int) |
| EC-004 | `input_tokens: null` / `""` | adds int 0 |
| EC-005 | `input_tokens: NaN` | `tin`, `c_in` become `NaN` and stay NaN |
| EC-006 | `input_tokens: -5` | `tin` -5 |
| EC-007 | `output_tokens: 2.0` | `tout` 2.0 (float persists in the cache) |
| EC-008 | `input_tokens: "5"` (truthy string) | CP-T04: line skipped under D4-EX-2 (BC-1.03.018), not accumulated |
| EC-009 | Accumulator crosses 4,301 decimal digits (two counted 4,300-digit `input_tokens`) | `json.dump` raises `ValueError` mid-write (CPython int↔str limit 4,300, oracle-verified); no cache write, previous cache bytes retained (postcondition 5; temp disposition per OD-163) |
| EC-010 | Huge int (e.g. 310-digit `cache_creation_input_tokens`) meets a float operand (`input_tokens: 1.5`, or a float `tin`) | Python raises `OverflowError` at SL:1108 (oracle-verified); legacy degrades (CP-O06, sticky); hylo skips the line per OD-156, totals unchanged |

## Canonical Test Vectors

Each row: one line `{"type": "assistant", "message": {"content": "", "id": "x", "usage": <usage>}}`, no cache.
Expected bytes are the complete cache files, re-pinned 2026-11-15 with the legacy oracle.

| Input | Expected Output | Category |
|-------|----------------|----------|
| usage `{"input_tokens": 1.5}` | `{"size": 93, "res": 0, "conv": 0, "think": 0, "tin": 1.5, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 1.5, "rb": 0, "pp": 1.5, "ids": ["x"], "lr": null, "lu": null, "cur": null}` | happy-path |
| usage `{"input_tokens": 12345678901234567890}` | `{"size": 110, …, "tin": 12345678901234567890, …, "c_in": 12345678901234567890, "rb": 0, "pp": 12345678901234567890, …}` | edge-case |
| usage `{"input_tokens": true, "output_tokens": true}` | `{"size": 117, …, "tin": 1, "tout": 1, …, "c_in": 1, "rb": 0, "pp": 1, …}` | edge-case |
| usage `{"input_tokens": NaN}` | `{"size": 93, …, "tin": NaN, …, "c_in": NaN, "rb": 0, "pp": NaN, …}` | edge-case |
| usage `{"output_tokens": 2.0}` | `{"size": 94, …, "tin": 0, "tout": 2.0, …, "c_in": 0, "rb": 0, "pp": 0, …}` | edge-case |
| usage `{"input_tokens": null}` | `{"size": 94, …, "tin": 0, …, "pp": 0, …}` | error |

(`…` elides keys equal to the first row's values; key order is always the 16-key sequence of BC-1.03.002.)

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | `pyfmt` Num addition equals CPython for int/big-int/float/bool operand pairs | Go property test (testing/quick) vs oracle table |
| VP-029 | Cache repr of totals equals CPython `json.dumps` | fuzz (differential) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009, CAP-011 (token totals feed cost/tokens widgets) |
| L2 Domain Invariants | DI-007 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1104-1112) |
| Legacy contract | BC-SL-035 (base; pinned pass-3 r1: float usage accepted) |
| Parity class | byte-exact |
| Confidence note | M — int/float/big-int `Num` arithmetic and its cache repr (design §8) |
| Architecture Module | `internal/statusline/transcript.go`; `internal/pyfmt` num/json |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.005 — depends on: which usage objects are counted
- BC-1.03.007 — composes with: rebuild check uses the same `_i/_w/_r`
- BC-5.01.001 — depends on: float repr / Num semantics
- BC-1.03.018 — related to: CP-T04 skip for truthy non-number fields

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript.go (usage accumulation; py.Num) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029 — Num addition parity

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1104-1112) |
| **Confidence** | high (mechanism); medium (numeric type surface) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if isinstance(u, dict)` (SL:1104)
- **inferred**: Python dynamic numeric typing determines the stored representation

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

Use `pyfmt.Num` (int64 fast path promoted to `*big.Int`, float64, bool-as-int) for every accumulator; never
`float64` totals.
