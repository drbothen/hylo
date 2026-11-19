---
document_type: behavioral-contract
level: L3
version: "1.3.5"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:10Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "05d958d"
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
modified:
  - "1.2.1 2026-11-17: CP-T08 overflow skip (OD-156) + 4,300-digit save failure (ADV-P2-C01/C02); oracle re-verified"
  - "1.2.2 2026-11-17: overflow crash path cited by taxonomy id CP-O06 (OD-156 register)"
  - "1.2.3 2026-11-17: pass-3 remediation (ADV-P3-C07/C08/C09/C10/C18/C22): overflow bound 2^1024−2^970, D4-EX-2 rides the closed id set (OD-156 cited, not an id), CP-O09 not moot (int-only totals), CP-O06 canonical vector, DI-012 cited, duplicate PC 5 renumbered"
  - "1.2.4 2026-11-18T08:00:00Z: pass-4 remediation: PC3 generalized to the ADV-P4-C08 rule (any accumulation site); reviewer two-line vector added (ints-cancel x, then float c_wr meeting at SL:1110; hylo size 852 = 744 + 108, oracle-run 2026-11-18)"
  - "1.2.5 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C01/C02/C04) — PC3 and EC-010 name the OD-167 in-flight-turn drop; timestamped CP-O06 turn-drop vector added: the drop is observable in `lr` (hylo null) against the plain-deletion oracle (lr [50.0, true], oracle-run 2026-11-18)"
  - "1.2.6 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C06) — VP table and VP Anchors gain the owned CP-O06 D4-EX-2 legs (VP-013 register, VP-012 closure)"
  - "1.2.7 2026-11-19T20:15:00Z: pass-7 remediation (ADV-P7-C08) — the CP-O06 turn-drop leg now cites where the A-template is defined (BC-1.03.016 PC2; self-contained copy in BC-1.03.010 CP-O08) instead of relying on an out-of-file template"
  - "1.3.0 2026-11-20T18:00:00Z: pass-9 remediation (ADV-P9-C03; orchestrator call 4) — PC5 gains the BC-1.03.018 Inv-3 cross-reference: counted exact-int totals degrade the later render (CP-O04, CP-O09, CP-O12); parse-time skips never fire for int+int sums"
  - "1.3.1 2026-11-22T12:00:00Z: pass-11 remediation (ADV-P11-C02) — DI-012 traceability row: the CP-O09 no-write is reproduced legacy behavior (PC5; error-taxonomy CP-O09 row), not a named deviation; the only CP-O09 divergence, the leaked partial temp file, rides the temp-file exclusion/OD-163 (BC-1.06.001 EC-010), not D4-EX-2"
  - "1.3.2 2026-11-24T12:00:00Z: pass-13 remediation (ADV-P13-C07) - the CP-O09 trigger now has the required canonical vector (error-taxonomy: edge case + canonical vector per owning BC): CTV gains the save-failure cycle row with exact cache-dir and stdout expectations (no target, leaked 55-B partial temp, 29-byte grey degraded line, hex-pinned; refresh-2 second temp) and the at-limit boundary bracket, measured end-to-end with the legacy oracle in an isolated temp HOME/cwd"
  - "1.3.3 2026-11-24T13:30:00Z: pass-13 sync closure - the save-failure-cycle setup gains the BC-3.02.001 Inv-4 proc_start seed via the BC-1.03.005 parse-leg reference (session cache statusline-probe.json seeded with the leading proc_start key, 900.0); expected output gains the measured session-cache outcome (byte-unchanged from the seed across both refreshes, consult short-circuit SL:273-275); stdout, leak count, leak bytes and the boundary bracket re-verified against the legacy oracle with the seed present (CPython 3.11.7, isolated temp HOME/cwd, -I); no outcome field changed"
  - "1.3.4 2026-11-26T12:30:00Z: pass-14 remediation (ADV-P14-C03) — EC-009 wording: the crossing requires the two 4,300-digit operands to sum to 10^4300 (e.g. 5·10^4299 each; two 10^4299 operands sum to a 4,300-digit total at the limit that writes, the BC-1.03.005 parse-leg CTV); no behavioral change"
  - "1.3.5 2026-11-26T15:00:00Z: pass-14 residual sweep (OD-160 owner id-range alignment): EC-011 minted — a cached non-numeric accumulator meeting a new counted line raises TypeError at the respective += (CP-C54; giant-plus-int exact); no behavioral change"
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
   values are added as-is. **Exception (overflow, CP-O06):** when an int operand with magnitude at or above
   2^1024 − 2^970 meets a float operand, Python raises `OverflowError` ("int too large to convert to float";
   oracle-verified 2026-11-17 for `+`, `−`, `×`, `÷`) instead of producing a float — DBL_MAX ≈ 1.7976e308 itself
   and every smaller magnitude converts silently, so a bare \|int\| > DBL_MAX predicate skips lines legacy processes
   (ADV-P3-C07; JSON admits ints up to 4,300 digits) — e.g. `input_tokens: 1.5` accumulated onto a 310-digit
   `cache_creation_input_tokens` (SL:1108), a float `tin` plus a huge int, or — any accumulation site qualifies
   (ADV-P4-C08 general rule) — a 310-digit `cache_creation_input_tokens` meeting a later float
   `cache_creation_input_tokens: 1.5` at the `c_wr` site SL:1110. Legacy degrades (crash path CP-O06,
   BC-1.03.018); hylo **skips the line and drops the in-flight turn** (owner rulings OD-156/Q-c: the CP-O entries ride the extended `D4-EX-2`
   id and cite OD-156; the closed exclusion-id set has no `OD-156` id — ADV-P3-C08), covered by dedicated Go
   table tests. The drop rides OD-167 and applies at every accumulation site (ADV-P5-C01).
4. The cache stores each total in Python `json.dump` form: ints as decimal digits of any length **up to the CPython
   int↔str conversion limit (`sys.get_int_max_str_digits()` = 4,300; oracle-verified 2026-11-17)**, floats as `repr`
   (`1.5`, `2.0`, `1e+16`), `NaN`/`Infinity` as bare tokens.
5. **Digit-limit save failure (EC-009, CP-O09):** when any serialized accumulator exceeds 4,300 decimal digits (e.g. two
   counted 4,300-digit `input_tokens` summing to 4,301 digits, oracle-verified), CPython `json.dump` raises
   `ValueError` mid-write (after partial content has reached the stream); `save_cache` swallows it, so the mix cache
   is **not written** and keeps its previous bytes, and the failure repeats every refresh while the totals stay
   above the limit. **Not moot in hylo (ADV-P3-C09):** the CP-O06..O08 skip rule requires an int to meet a float,
   but two exact ints add without ever touching a float, so nothing is skipped; hylo counts both lines exactly
   (EC-002) and reproduces the **no-write** observable and the re-failing parse on every later refresh; the
   temp-file disposition is ruled by OD-163 (BC-1.06.001 EC-010). Cross-reference (BC-1.03.018 Inv 3): a counted
   exact-int total above the render-side conversion bounds degrades the later render at the aggregate sites
   (CP-O04, CP-O09, now CP-O12) — the CP-O06..O08 parse-time skip never fires for int+int sums, so nothing at
   parse time prevents the stored total from poisoning the render.
6. A `compact_boundary` line does not change these totals (BC-1.03.008).

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
| EC-009 | Accumulator crosses 4,301 decimal digits (two counted 4,300-digit `input_tokens` whose sum reaches 10^4300 — e.g. 5·10^4299 each; two 10^4299 operands sum to a 4,300-digit total at the limit that writes, the BC-1.03.005 parse-leg CTV; int-only — no float operand, so no CP-O06..O08 skip: not moot) | `json.dump` raises `ValueError` mid-write (CPython int↔str limit 4,300, oracle-verified with 19 bytes already streamed); no cache write, previous cache bytes retained (postcondition 5; temp disposition per OD-163); hylo reproduces the no-write |
| EC-010 | Huge int (e.g. 310-digit `cache_creation_input_tokens`) meets a float operand (`input_tokens: 1.5`, or a float `tin`) | Python raises `OverflowError` at SL:1108 (oracle-verified; bound 2^1024 − 2^970, ADV-P3-C07); legacy degrades (CP-O06, sticky); hylo skips the line and drops the in-flight turn (OD-167), totals unchanged |\n| EC-011 | Cached accumulator `tin`/`tout`/`c_in`/`c_wr`/`c_rd`/`rb` a non-numeric non-giant (string, null, list, dict) meeting a new counted transcript line (foreign cache, **OD-160**) | legacy TypeError at the respective `+=` (SL:1108-1112, SL:1118) → typed 29-byte degrade, exit 0, nothing saved that refresh; giant-plus-int stays exact (a giant meeting a transcript-borne float is CP-O06's bearer, EC-010); foreign cached values: CP-C54, OD-160, Go table tests (measured pass-14) |

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
| CP-O09 save-failure cycle (PC5/EC-009; ADV-P13-C07): transcript = two lines x, y, each {"type": "assistant", "message": {"content": "", "id": "x or y", "usage": {"input_tokens": 5*10^4299}}} + LF (each operand 4,300 digits; sum 10^4300 = 4,301 digits; 8,780 B total); same setup as the BC-1.03.005 parse leg, including its statusline-probe.json = {"proc_start": 900.0} seed (the corpus admission rule, BC-3.02.001 Inv 4) | measured end-to-end 2026-11-18 (isolated temp HOME/cwd, interpreter -I, seed present): refresh 1: exit 0, stdout exactly the 29-byte grey degraded line (hex as the BC-1.03.005 parse leg), cache dir has NO statusline-mix-probe.json and exactly one leaked temp named statusline-mix-probe.json. + 8 random chars, 55 B, bytes exactly {"size": 8780, "res": 0, "conv": 0, "think": 0, "tin":  (json.dump died converting the 4,301-digit tin); refresh 2: stdout identical, still no target, a second leaked temp (legacy leaks; hylo removes its own temp per OD-163 - a cache-listing-only difference, OD-110 class); the session cache stays byte-unchanged from the seed across both refreshes (the seeded numeric proc_start returns at the consult short-circuit, SL:273-275 — no probe, no rewrite); boundary bracket: the operands of the BC-1.03.005 parse leg (sum 4,300 digits, at the limit) DO write the cache with the exact sum | error |
| CP-O06 (lines `x` then `y`, distinct ids): `x` = `{"input_tokens": 5}`; `y` = `{"input_tokens": 1.5, "cache_creation_input_tokens": 10^309}` (310 digits, ≥ 2^1024 − 2^970). Legacy: `OverflowError` at SL:1108, degraded line, cache not saved (oracle-verified 2026-11-18) | hylo (OD-156): `y` skipped, `x` counted — cache exactly `{"size": 527, "res": 0, "conv": 0, "think": 0, "tin": 5, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 5, "rb": 0, "pp": 5, "ids": ["x"], "lr": null, "lu": null, "cur": null}` (base bytes pinned from legacy on the `x`-only transcript, `"size"` 91 + 436 deleted bytes per BC-1.03.018 PC4) | error |
| CP-O06 general-rule leg (lines `x` then `y`, distinct ids; ADV-P4-C08): `x` = `{"input_tokens": -10^309, "cache_creation_input_tokens": 10^309}` (ints cancel: `tin` 0, `pp` 0); `y` = `{"cache_creation_input_tokens": 1.5}`. Legacy: `x` counts; `y` raises `OverflowError` at the `c_wr` site SL:1110 (`10^309 + 1.5`), degraded line, cache not saved (oracle-verified 2026-11-18) | hylo (OD-156): `y` skipped, `x` counted — cache exactly `{"size": 852, "res": 0, "conv": 0, "think": 0, "tin": 0, "tout": 0, "c_wr": 10^309, "c_rd": 0, "mixv6": 1, "c_in": -10^309, "rb": 0, "pp": 0, "ids": ["x"], "lr": null, "lu": null, "cur": null}` (10^309 = the 310-digit integer; base bytes pinned from legacy on the `x`-only transcript, `"size"` 744 + 108 deleted bytes per BC-1.03.018 PC4) | error |
| CP-O06 turn-drop leg (timestamped; lines `U_a, A_x, A_y, U_b`, distinct ids, TZ=UTC; ADV-P5-C01/C02): `U_a` = the U-template `{'type': 'user', 'message': {'role': 'user', 'content': 'go'}, 'timestamp': '2026-11-14T10:00:00Z'}` (92 B); `A_x` = the A-template (defined in BC-1.03.016 PC2; self-contained copy in BC-1.03.010's CP-O08 row) with id `x`, usage `{'input_tokens': 5, 'output_tokens': 100}`, ts 10:00:02Z (163 B); `A_y` poisoned as in the canonical leg above (ts 10:00:04Z, 486 B); `U_b` = U-template ts 10:00:06Z (92 B). Legacy on the full window: `OverflowError` at SL:1108 (`1.5 + 10^309`), degraded, no save (oracle-run 2026-11-18). Plain-deletion oracle (PC4(a)): legacy on `U_a, A_x, U_b` = `{'size': 347, ..., 'lr': [50.0, true], 'lu': 1794650406.0, 'cur': null}` (oracle-run). | hylo (OD-167): `A_y` skipped and the open turn discarded — cache exactly `{'size': 833, 'res': 0, 'conv': 5, 'think': 0, 'tin': 5, 'tout': 100, 'c_wr': 0, 'c_rd': 0, 'mixv6': 1, 'c_in': 5, 'rb': 0, 'pp': 5, 'ids': ['x'], 'lr': null, 'lu': 1794650406.0, 'cur': null}` (compact `json.dumps` separators, each line LF-terminated; `'size'` 833 = 347 + 486 deleted bytes; `'lr'` null is the ruled drop observable — the plain-deletion oracle would rate the dropped turn 50.0 tok/s) | error |

(`…` elides keys equal to the first row's values; key order is always the 16-key sequence of BC-1.03.002.)

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | `pyfmt` Num addition equals CPython for int/big-int/float/bool operand pairs | Go property test (testing/quick) vs oracle table |
| VP-029 | Cache repr of totals equals CPython `json.dumps` | fuzz (differential) |
| VP-013 | The CP-O06 vector leg this contract owns is a D4-EX-2 wrong-shape leg: the overflow skip leaves no partial mutation and (OD-167) drops the in-flight turn (register VP-013; ADV-P6-C06) | Go property/table test over the owned vector |
| VP-012 | The CP-O06 exclusion entry this contract owns rides the D4-EX-2 closure check (BC-1.03.018 PC5 names this contract's vector rows among the dedicated tests) | repository test over `exclusions.json` |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009, CAP-011 (token totals feed cost/tokens widgets) |
| L2 Domain Invariants | DI-007; DI-012 (the OD-156/D4-EX-2 skip is a named, tested deviation; the CP-O09 no-write is **reproduced** legacy behavior — PC5 and the error-taxonomy CP-O09 row — and the only CP-O09 divergence, the leaked partial temp file, rides the temp-file exclusion/OD-163 (BC-1.06.001 EC-010), not D4-EX-2) |
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
- VP-013 — the owned CP-O06 D4-EX-2 leg (no partial mutation, OD-167 drop)
- VP-012 — closure cover for the owned D4-EX-2 exclusion entry

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
