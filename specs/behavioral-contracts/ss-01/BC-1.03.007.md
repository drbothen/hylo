---
document_type: behavioral-contract
level: L3
version: "1.2.8"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:10Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "75de44d"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1113-1119, 1094; REBUILD_EXCESS SL:968-972)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-036"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: rebuild_excess valid range >= 0 (OD-162; ADV-P2-C03)", "1.2.2 2026-11-17: pass-3 remediation (ADV-P3-C03/C10/C16): corrected negative-X rationale, CP-O07 rebuild-check overflow edge case and canonical vector (owner of the SL:1117 site)", "1.2.3 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C01/C02/C10) — EC-007 names the OD-167 in-flight-turn drop; timestamped CP-O07 turn-drop vector added (`lr` observable: hylo null vs plain-deletion [50.0, true], oracle-run 2026-11-18); DI-012 lifted to the traceability row (sibling convention, ADV-P5-C10)", "1.2.4 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C06) — VP table and VP Anchors gain the owned CP-O07 D4-EX-2 legs (VP-013 register, VP-012 closure)", "1.2.5 2026-11-19T20:15:00Z: pass-7 remediation (ADV-P7-C07) — the CP-O07 turn-drop leg seed made self-consistent: it is the CP-O07 seed with ids ['x'] in place of [] (the variant that the A_x dedup and the expected ids require), not the 'same seed cache'", "1.2.6 2026-11-21T12:00:00Z: pass-10 remediation (ADV-P10-C01; orchestrator call 13) — the CP-O07 canonical vector is the transcript-reachable mirror sequence (huge exact int `pp` vs float `prompt`; D4-EX-2; legacy oracle-run 2026-11-18): three timed lines input_tokens 10^309, -10^309, 1.5 leave `tin` 0 (exact int) so SL:1108 passes and SL:1117 raises converting `pp`; the hand-edited int-`tin`/float-`pp` seed legs are foreign-cache states re-registered under OD-160 (Go table tests, not byte-parity)", "1.2.7 2026-11-22T12:00:00Z: pass-11 remediation (ADV-P11-C01; orchestrator call 11) — the CP-O07 canonical mirror cache pins lu null (legacy assigns lu only on a user line, SL:1085; the vector has none); the three timestamps stated (2026-11-14T10:00:00Z a, 10:00:02Z b, 10:00:04Z c; 20-char Z stamps, per-line 426/427/119 B, 972 total with LF); row-107 code span closed; every field of the expected cache re-walked against SL:1037-1153", "1.2.8 2026-11-26T15:00:00Z: pass-14 residual sweep (OD-160 owner id-range alignment): EC-008 minted — a cached non-numeric pp meeting a new counted line raises TypeError at prompt - pp (CP-C55; the float-pp overflow leg stays CP-O07); no behavioral change"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.007: Rebuild rule at 20,000 excess input tokens

## Description

A counted API call is a cache **rebuild** when its cache write exceeds its context growth by more than
`rebuild_excess` (20,000) tokens: it re-wrote context that was already cached. The parser counts rebuilds in `rb`
and carries the previous call's prompt size in `pp`. The first counted call after a reset or a compaction boundary
is never a rebuild because `pp` is null.

## Preconditions

1. A counted usage object (BC-1.03.005) with `_i`, `_w`, `_r` as in BC-1.03.006.
2. `pp` = cached previous prompt size or null; `rb` = cached rebuild count (0 after reset).
3. `X = statusline.transcript.rebuild_excess` (default 20000; T-056, rationale: **measured** — validated on 9,650
   calls in 120 transcripts: normal calls max 4,145 excess (99.9 % under 577), smallest rebuild 61,901; 20K sits
   about 5× above the worst normal call and 3× below the smallest rebuild; SL:968-971). **Valid range (OD-162):
   `>= 0`**, derived from legacy semantics — `X` is a token-excess comparison threshold against
   `_w − max(0, prompt − pp)` (SL:1117): the excess is negative whenever context growth exceeds the write, so a
   negative `X` would count ordinary growing calls (excess between `X` and 0) as rebuilds (ADV-P3-C16);
   out-of-range values are number-range config errors (S2 schema, OD-114).

## Postconditions

1. `prompt = _i + _w + _r`.
2. If `pp` is not null and `_w - max(0, prompt - pp) > X` (strict), then `rb += 1`.
3. `pp = prompt` (always, for every counted usage, after the test).
4. Lines whose usage is not counted (dedup, BC-1.03.005) leave `rb` and `pp` unchanged.
5. A `compact_boundary` line sets `pp = null` (BC-1.03.008); a reset sets `pp = null`, `rb = 0` (BC-1.03.002).
6. `rb` and `pp` are written to the cache (`"rb"` int, `"pp"` int/float/null).

## Invariants

1. Context shrinkage counts as zero growth (`max(0, …)`), so after a shrink the whole write counts as excess.
2. The comparison is strict: an excess of exactly X is not a rebuild.
3. `max` argument order follows legacy (`max(0, prompt - pp)`); with NaN operands Python returns the first
   argument, 0 (BC-5.01.003).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | First counted call (pp null) with a 50,000 write | not a rebuild; `pp` = its prompt |
| EC-002 | Excess exactly 20,000 | not a rebuild |
| EC-003 | Excess 20,001 | rebuild |
| EC-004 | Prompt shrank (growth clamped to 0), write 20,001 | rebuild |
| EC-005 | Duplicate-id line with a large write | ignored (not counted) |
| EC-006 | After `compact_boundary`, a 50,000 write | not a rebuild (`pp` null) |
| EC-007 | Overflow at the rebuild check (CP-O07, ADV-P3-C03; this BC owns the SL:1117 site). Two legs meet CPython's int→double bound \|value\| ≥ 2^1024 − 2^970 in `_w − max(0, prompt − pp)`: (a) **mirror leg, transcript-reachable** — a huge exact int `pp` meets a float `prompt` (ADV-P4-C08); the state is authored by the three-line transcript of the canonical vector below, no hand-edited cache; (b) a parse state carrying an int `tin` with a float `pp` meets a huge exact int `_w` — a legal stored form (postcondition 6), but no legacy or hylo writer pairs an int `tin` with a float `pp` (a legacy-written cache couples float `pp` with float `tin`), so (b)'s seed is a hand-edited foreign-cache state | Python raises `OverflowError` at SL:1117 (both legs oracle-verified 2026-11-18); legacy degrades sticky; hylo skips the line and drops the in-flight turn (D4-EX-2 extension, rulings OD-156 + OD-167), `rb` and `pp` unchanged (BC-1.03.018). Registration split (ADV-P10-C01, orchestrator call 13): (a) rides D4-EX-2; (b) rides OD-160 (Go table test, not byte-parity) |\n| EC-008 | Cached `pp` a non-numeric non-giant (string, list, dict; null is the fresh state and skips the predicate) meeting a new counted line (foreign cache, **OD-160**) | legacy TypeError at `prompt - pp` (SL:1117) → typed 29-byte degrade, exit 0; the float-`pp` overflow leg stays CP-O07 (EC-007); foreign cached values: CP-C55, OD-160, Go table tests (measured pass-14) |

## Canonical Test Vectors

Lines `{"type": "assistant", "message": {"content": "", "id": "m<i>", "usage": <u_i>}}`. Five calls, no cache:
u0 = `{"input_tokens": 1000, "cache_read_input_tokens": 100000}`, u1 = `{"cache_creation_input_tokens": 90000,
"cache_read_input_tokens": 11500}` (growth 500 → excess 89,500 → rebuild), u2 = `{"cache_creation_input_tokens":
20000, "cache_read_input_tokens": 101500}` (excess 0), u3 = `{"cache_creation_input_tokens": 40001,
"cache_read_input_tokens": 121500}` (excess 0), u4 = `{"cache_creation_input_tokens": 20001}` (shrink, excess
20,001 → rebuild). Re-pinned 2026-11-15 with the legacy oracle.

| Input | Expected Output | Category |
|-------|----------------|----------|
| u0..u4 in one refresh | `{"size": 678, "res": 0, "conv": 0, "think": 0, "tin": 505502, "tout": 0, "c_wr": 170002, "c_rd": 334500, "mixv6": 1, "c_in": 1000, "rb": 2, "pp": 20001, "ids": ["m0", "m1", "m2", "m3", "m4"], "lr": null, "lu": null, "cur": null}` | happy-path |
| then refresh 2 appends `{"type": "system", "subtype": "compact_boundary"}` and m9 with `{"cache_creation_input_tokens": 50000}` | `{"size": 839, …, "tin": 555502, …, "c_wr": 220002, "c_rd": 334500, …, "rb": 2, "pp": 50000, "ids": ["m0", "m1", "m2", "m3", "m4", "m9"], …}` | edge-case |
| a: `{"cache_read_input_tokens": 100000}`; b: `{"cache_creation_input_tokens": 20000, "cache_read_input_tokens": 80000}` | `"rb": 0`, `"pp": 100000` (excess exactly 20,000) | edge-case |
| same with b write 20001, read 79999 | `"rb": 1`, `"pp": 100000` | edge-case |

Pass-3 r1 pinned an equivalent 5-call scenario (`rb` 2, tin 501,502); the vectors above are an independent re-pin.

CP-O07 canonical vector (transcript-reachable mirror leg; ADV-P10-C01; orchestrator call 13; legacy oracle-run 2026-11-18): no seed cache — the parser state is authored by the transcript itself. Three timed assistant lines (TZ=UTC, compact json.dumps, LF-terminated, contents "", ids a/b/c; timestamps 2026-11-14T10:00:00Z (a), 2026-11-14T10:00:02Z (b), 2026-11-14T10:00:04Z (c) — 20-character Z stamps, epochs 1794650400/402/404; per-line 426/427/119 B, 972 total with LF; no user line, so `lu` stays null — legacy assigns `lu` only on a user line, SL:1085, and the OD-167 drop leaves it unchanged): usage 1 = `{"input_tokens": 10^309}`, usage 2 = `{"input_tokens": -10^309}` (the int-only window: oracle-verified saved state after line 2 — `tin` 0 (exact int), `c_in` 0, `pp` −10^309 (exact int), `rb` 0, `ids` ["a","b"], `lr` null, `cur` open for "b" with t0 null), usage 3 = `{"input_tokens": 1.5}` (float; 972 bytes total with LF).

CP-O07 foreign-seed vector (ADV-P3-C10; legacy legs oracle-verified 2026-11-18) — **FOREIGN-CACHE STATE (OD-160, ADV-P10-C01)**: the hand-edited seed pairs an int `tin` with a float `pp`, which no legacy or hylo writer produces; Go table test, not byte-parity. Seed cache exactly `{"size": 0, "res": 0, "conv": 0,
"think": 0, "tin": 0, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": 5.0, "ids": [], "lr": null,
"lu": null, "cur": null}`; transcript is the single line `{"type": "assistant", "message": {"content": "", "id": "y",
"usage": {"cache_creation_input_tokens": 10^309}}}` (415 bytes with LF).

| Input | Expected Output | Category |
|-------|----------------|----------|
| the three lines above, no cache | legacy: `OverflowError` at SL:1117 ("int too large to convert to float", traceback-pinned 2026-11-18), degraded line — exit 0, stdout exactly the 29 bytes `1b5b39306d` + `statusline degraded` + `1b5b306d0a` (LF included), no mix cache ever authored (cache dir stays ABSENT); the identical degrade repeats on every refresh (sticky by replay; oracle-run 3 refreshes); hylo (D4-EX-2 + OD-167): line 3 skipped whole, in-flight turn "b" dropped — cache exactly `{"size": 972, "res": 0, "conv": 0, "think": 0, "tin": 0, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": -10^309, "ids": ["a", "b"], "lr": null, "lu": null, "cur": null}` (`lu` null: no user line in the window; the pinned 1794650402.0 was line b's own timestamp, ADV-P11-C01) | error |
| seed + the line above | legacy: `OverflowError` at SL:1117, degraded line, exit 0, cache keeps its seed bytes; hylo (D4-EX-2): cache exactly `{"size": 415, "res": 0, "conv": 0, "think": 0, "tin": 0, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": 5.0, "ids": [], "lr": null, "lu": null, "cur": null}` | error |
| CP-O07 turn-drop leg (timestamped; ADV-P5-C01/C02): seed cache = the CP-O07 seed above with `ids` `["x"]` in place of `[]` (float `pp` 5.0 and int `tin` unchanged — the `["x"]` variant is what A_x's dedup and the expected `'ids': ['x']` below require; ADV-P7-C07) plus four timed lines (TZ=UTC, compact `json.dumps`, LF-terminated): `U_a` ts 10:00:00Z (92 B), `A_x` id `x` usage `{'input_tokens': 5, 'output_tokens': 100}` ts 10:00:02Z (163 B — mid `x` is in the seed's `ids`, so the usage is **deduplicated**: `pp` stays 5.0 while the turn machine still opens the turn), `A_y` id `y` usage `{'cache_creation_input_tokens': 10^309}` ts 10:00:04Z (467 B — SL:1108 is int-only and overflow-free; the rebuild check `prompt − pp` = `10^309 − 5.0` raises), `U_b` ts 10:00:06Z (92 B). | Legacy on the full window: `OverflowError` at SL:1117, degraded, seed bytes kept (oracle-run 2026-11-18). Plain-deletion oracle: legacy on `U_a, A_x, U_b` + seed = `{'size': 347, ..., 'lr': [50.0, true], 'lu': 1794650406.0, 'cur': null}` (oracle-run). hylo (OD-167): `A_y` skipped and the open turn discarded — cache exactly `{'size': 814, 'res': 0, 'conv': 5, 'think': 0, 'tin': 0, 'tout': 0, 'c_wr': 0, 'c_rd': 0, 'mixv6': 1, 'c_in': 0, 'rb': 0, 'pp': 5.0, 'ids': ['x'], 'lr': null, 'lu': 1794650406.0, 'cur': null}` (`'size'` 814 = 347 + 467 deleted bytes; `'lr'` null is the ruled drop observable; `'pp'` stays the float 5.0) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | `rb` increments iff `pp ≠ null ∧ _w − max(0, prompt − pp) > X` | Go property test (testing/quick) |
| VP-029 | `pp` after a counted call equals that call's prompt | Go property test (testing/quick) |
| VP-013 | The CP-O07 vector legs this contract owns realize the D4-EX-2 skip with no partial mutation and (OD-167) the in-flight-turn drop; the canonical leg is the transcript-reachable mirror vector, the hand-edited-seed legs ride OD-160 as Go table tests (register VP-013; ADV-P6-C06, ADV-P10-C01) | Go property/table test over the owned vectors |
| VP-012 | The CP-O07 exclusion entry this contract owns rides the D4-EX-2 closure check (BC-1.03.018 PC5 names this contract's vector rows among the dedicated tests); the foreign-seed legs ride the OD-160 closure as Go table tests (ADV-P10-C01) | repository test over `exclusions.json` |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007; DI-012 (the CP-O07 D4-EX-2 skip and the OD-167 turn-drop are named, tested deviations); the hand-edited int-`tin`/float-`pp` seed legs are OD-160 foreign-cache vectors (ADV-P10-C01) |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1113-1119, 1094); constant SL:968-972 |
| Legacy contract | BC-SL-036 (base; pinned pass-3 r1) |
| Threshold | T-056 → `statusline.transcript.rebuild_excess` = 20000 (measured) |
| Parity class | byte-exact |
| Architecture Module | `internal/statusline/transcript.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.006 — depends on: `_i/_w/_r`
- BC-1.03.008 — composes with: compaction clears `pp`
- BC-1.03.005 — depends on: only counted usage participates

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript.go (rebuild 20,000) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029 — rebuild predicate
- VP-013 — the owned CP-O07 D4-EX-2 leg (no partial mutation, OD-167 drop; canonical = the transcript-reachable mirror vector, ADV-P10-C01)
- VP-012 — closure cover for the owned D4-EX-2 exclusion entry

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1113-1119; `REBUILD_EXCESS` SL:968-972) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if pp is not None and _w - max(0, prompt - pp) > REBUILD_EXCESS` (SL:1117)
- **documentation**: measured rationale SL:968-971

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none (reads the config value) |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; `X` comes from `config.Statusline` (D15).
