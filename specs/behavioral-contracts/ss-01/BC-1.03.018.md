---
document_type: behavioral-contract
level: L3
version: "1.2.7"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:10Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "5cb6c46"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1059-1149; raise sites SL:994, 1069, 1072, 1079, 1097, 1099, 1108, 1112, 1143, 1145)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-098"
parity_class: "D4-EX-2"
confidence: "M"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: VP citation reconciliation — VP-012 added", "1.2.2 2026-11-17: eighth crash path CP-T08 numeric overflow (ruling OD-156; ADV-P2-C01)", "1.2.3 2026-11-17: CP-T08 renamed to taxonomy ids CP-O06..O08 (OD-156 register)", "1.2.4 2026-11-17: pass-3 remediation (ADV-P3-C03/C06/C07/C10/C11): ten-predicate count, CPython int→double overflow bound 2^1024−2^970, CP-O07 re-anchored to the SL:1117 rebuild check (owner BC-1.03.007), CP-O08 closer-skip plus in-flight turn drop (ruling OD-167)", "1.2.5 2026-11-18T08:00:00Z: pass-4 remediation: general overflow rule stated — any accumulator OverflowError in the SL:1108-1117 window is CP-O06/O07 class; CP-O06 widened to SL:1108-1112, CP-O07 to either direction incl. huge-int pp vs float prompt (ADV-P4-C08)", "1.2.6 2026-11-17: pass-4 residual sweep — exclusions.json path canonicalized; closed set restated as eleven ids incl. OD-166 (OD-169)", "1.2.7 2026-11-18T22:00:00Z: pass-4 correction (item 10) — exclusions.json path restored to the OD-148 home internal/statusline/testdata/parity/exclusions.json"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.018: D4-EX-2 wrong-shape line W-predicates (skip, no partial mutation)

## Description

**Approved deviation D4-EX-2** (owner ruling Q-c, 2026-11-14; extended by rulings OD-156 and OD-167, 2026-11-17/18). Legacy has
ten transcript crash paths, CP-T01..T07 and CP-O06..O08:
a decoded line with a wrong-shaped field raises mid-parse, the refresh degrades, the mix cache is not saved, and the
crash repeats on every later refresh (sticky; legacy contract BC-SL-068, replaced). hylo instead evaluates a
wrong-shape predicate `W(state, record)` per line **before** processing it and, when it holds, **skips the line with
exactly the effect of a JSON decode failure**: no parser state changes, its bytes are consumed, the cache is saved and
the refresh renders normally. This BC defines the ten predicates precisely so that a skipped line leaves no partial
mutation. Predicates CP-T01..T07 come from legacy's wrong-shape raise sites; **CP-O06..O08** (rulings OD-156 and OD-167;
`prd-supplements/error-taxonomy.md`) cover transcript-borne numeric overflow: an exact int with magnitude at or above
CPython's int→double overflow bound 2^1024 − 2^970 meeting a float operand (oracle-verified `OverflowError` "int too
large to convert to float"; magnitudes below the bound convert silently). **General rule (ADV-P4-C08):
any `OverflowError` raised by an accumulator site in the SL:1108-1117 window — `tin` SL:1108, `c_in`
SL:1109, `c_wr` SL:1110, `c_rd` SL:1111, `tout` SL:1112, or the rebuild-check arithmetic SL:1117-1118 —
is CP-O06/O07 class; the per-row "raise site" columns below name the canonical legs, not the full set.**
The lazy CP-O08 site additionally drops the
in-flight turn so that later lines parse normally (ruling OD-167; no sticky state, ARCH-03 `#transcript`).

## Preconditions

1. A piece from the complete-line window decoded successfully (BC-1.03.004); `e` is the decoded value; `state` is
   the parser state reached so far in the same parse.
2. Definitions: `ts_ok` = `FromISOFormat(e.timestamp)` is not null (BC-1.03.010); `cb` = `e.type == "system" and
   e.subtype == "compact_boundary"`; `m` = `e.message` if truthy else `{}`; "number" = int, float or bool
   (`isinstance(x, (int, float))`); "opens a new turn" = `cur` empty/null or `cur.id != m.id`.

## Postconditions

1. Per line, in order: (1) decode fails → skip (legacy); (2) else if any W-predicate below holds → **skip**; (3) else
   process exactly as legacy (BC-1.03.005..010).
2. A skipped line changes **none** of: `res`, `conv`, `think`, `tin`, `tout`, `c_wr`, `c_rd`, `c_in`, `rb`, `pp`,
   `cur`, `lr`, `lu`, `seen_ids`, `recent_ids` — except as ruling OD-167 directs for the lazy CP-O08 site (the closer
   is skipped **and** the in-flight turn is dropped, `cur` → null). The offset still advances past the window's last LF.
3. W-predicates (the skipped line is the one satisfying it), with the legacy mutations Go must **not** apply:

| Path | W-predicate | Legacy raise site | Legacy mutations before the raise (not applied by hylo) |
|---|---|---|---|
| CP-T01 | `e` is not an object | SL:1069 | none |
| CP-T02 | `e.message` truthy and not an object, **and not** (`cb` and not `ts_ok`) | SL:1072 (timed) / SL:1097 (untimed) | none |
| CP-T03 | `ts_ok`, `e.type == "assistant"`, `m.id` truthy, opens a new turn, `m.usage` truthy and not an object | SL:1079 | `lr = finish(cur, lr)` — hylo keeps the previous turn open (`cur`, `lr` unchanged) |
| CP-T04 | not `cb`; `m.usage` is an object; (`m.id` falsy, or hashable and not in `seen_ids`); any of `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens` truthy and not a number | SL:1108 (input fields) / SL:1112 (output only) | turn step, `seen_ids.add`/`recent_ids.append`, and with only `output_tokens` bad: `tin/c_in/c_wr/c_rd` (and `rb`/`pp` are not reached) |
| CP-T05 | `ts_ok`, `assistant`, `m.id` truthy, opens a new turn, **`lu` is not null**, the usage is **not counted** (an object whose id is already in `seen_ids`), and `(m.usage or {}).output_tokens` truthy and not a number | SL:994 (lazily, when the turn later closes, possibly next refresh) | previous turn closed, `cur` opened with the bad `out`, composition counted — hylo skips at the opening line; previous turn stays open, composition and `lu` unchanged |
| CP-T06 | not `cb`; `m.content` is a list; some object block has `type == "text"` with `text` truthy and without a length (number, `true`), or `type == "thinking"` with `thinking` likewise | SL:1143 / SL:1145 | turn step, usage, ids, composition of earlier blocks of the line |
| CP-T07 | not `cb`; `m.usage` is an object (even `{}`); `m.id` truthy and unhashable (array or object) | SL:1099 | with `ts_ok` and `assistant`: previous turn closed and `cur = {id: [..], …}` opened |
| CP-O06 | The line's numbers are all JSON numbers, yet a usage-accumulation step raises `OverflowError`: an exact int with \|value\| ≥ 2^1024 − 2^970 (CPython's int→double overflow bound; JSON admits ints up to 4,300 digits, and magnitudes below the bound — DBL_MAX ≈ 1.7976e308 included — convert silently, oracle-verified 2026-11-17) meets a float operand at **any** accumulation site (general rule, ADV-P4-C08: `tin` SL:1108, `c_in` SL:1109, `c_wr` SL:1110, `c_rd` SL:1111, `tout` SL:1112) | SL:1108-1112 | none (immediate raise during accumulation) |
| CP-O07 | Same overflow condition at the **rebuild-check** step (owner BC-1.03.007): SL:1117-1118 in either direction — a float `pp` carried from an earlier counted line meeting a huge exact int `_w` (the canonical leg; its own SL:1108 accumulation is int-only and overflow-free when `tin` is an int), **or a huge exact int `pp` meeting a float `prompt`** (mirror leg, ADV-P4-C08) | SL:1117-1118 | none (immediate raise; the `pp = prompt` assignment is not reached) |
| CP-O08 | Same overflow condition at the turn-machine steps: SL:994 `stale_factor × out / floor_tps` or SL:996 `out / span` with a huge exact int `out` (lazy: the raise surfaces while processing the **closer** line). **Deviation (ruling OD-167):** hylo skips the closer line **and drops the in-flight turn** (`cur` → null; `lr`, `lu` unchanged), so later lines parse normally — no sticky state (ARCH-03 `#transcript`) | SL:994, 996 | for the lazy `_finish_turn` sites: the closer line's own turn/lu bookkeeping (legacy keeps the bad turn open, so every later closer re-raises inside `finish` and is skipped too: new-id assistant lines, real user prompts and timed system/`compact_boundary` lines stop counting — totals freeze for the rest of the session) |

4. **Equivalence oracle:** hylo on transcript T yields the same mix cache and render as legacy on T with the skipped
   lines deleted, except `size`, which equals legacy's plus the deleted lines' bytes (each + 1 for its LF).
5. **Exclusion:** every input that triggers a predicate is listed in the parity harness's named exclusion list
   (OD-105/OD-110), entry id `D4-EX-2`, file `internal/statusline/testdata/parity/exclusions.json`; each entry names
   its expected output file and its dedicated table test (BC-1.03.019). An entry without a test fails the harness; no
   globs. CP-O06..O08 entries additionally cite ruling `OD-156`.

## Invariants

1. Predicates are evaluated against the state reached so far in the same parse, in legacy evaluation order.
2. Non-crash look-alikes are **not** skipped (they are byte-exact): untimed `cb` with a non-object `message`
   (T02−), continuation line with array usage (T03− continuation), untimed array usage (T03− untimed), already-seen
   id with bad usage (T04− seen id), `cb` with bad usage (T04− cb), `cb` with numeric text (T06− cb), list text
   (T06− list), unhashable id without usage (T07− no usage), and the CP-T05 shape when `lu` is null (T05− lu none).
3. The status line never degrades on any transcript line content in hylo (DI-008); CP-S14/S16 (sid / path types)
   still degrade (byte-parity scope).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | CP-T05 opening line is the last line with no later closer | hylo skips it (cur = previous turn); legacy writes `cur.out` non-numeric (BC-1.03.020) — excluded row T05~ |
| EC-002 | CP-T05 shape with `lu` null | not skipped: legacy and hylo both write `cur` with `t0` null and the raw `out` (BC-1.03.021) |
| EC-003 | CP-T04 with a usage that would be deduplicated | predicate false (id in `seen_ids`) → processed; usage ignored |
| EC-004 | Several W-lines in one window | each skipped independently; state between them evolves normally |
| EC-005 | "Absent usage" with bad `output_tokens` | impossible (absent usage gives out 0); the working CP-T05 condition is "usage object with an already-seen id" (pass-3 r3 refinement) |

## Canonical Test Vectors

The 21-row table with exact expected caches is BC-1.03.019 (legs CP-T01..T07). Dedicated canonical vectors with exact
expected caches for the overflow legs CP-O06..O08 live in their owner BCs: BC-1.03.006 (CP-O06), BC-1.03.007 (CP-O07),
BC-1.03.010 (CP-O08). Representative rows:

| Input | Expected Output | Category |
|-------|----------------|----------|
| `U0, A2, [1, 2], S20` (T01+) | hylo cache = legacy cache of `U0, A2, S20` with `"size": 451` | error |
| `U0, A2, {}, S20` (T01−) | byte-exact with legacy, `"size": 447` | edge-case |
| T04+ out-only | `"tin": 110` (the `input_tokens: 5` of the skipped line is **not** added) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029, VP-013 | For every W-line, parser state after = state before (bit-identical) | Go property test (testing/quick) with generated W-lines per CP |
| VP-029, VP-013 | Delete-the-line equivalence holds on random transcripts with injected W-lines | fuzz (oracle on the transcript with W deleted) |
| VP-012 | Postcondition 5 closure: every predicate-triggering input is a named D4-EX-2 exclusion entry carrying its own expected-output file and dedicated table test; no globs | repository test over `exclusions.json` |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1059-1149), _finish_turn (SL:988-996); raise sites as tabulated |
| Legacy contract | BC-SL-098 (pass-3 r2 §A6; refined r3); replaces BC-SL-068 (sticky crash) |
| Parity class | **D4-EX-2** (approved deviation, owner ruling Q-c 2026-11-14) |
| Exclusion entry | OD-105 / OD-110 named list, id `D4-EX-2`; CP-O06..O08 entries cite ruling `OD-156` (there is no exclusion id `OD-156`; the closed set is now eleven ids incl. `OD-166` (OD-169)); dedicated tests = BC-1.03.019 (21 rows, CP-T legs) + the CP-O06..O08 vector rows in BC-1.03.006, BC-1.03.007, BC-1.03.010 + BC-1.03.020 rows (DI-012) |
| Confidence note | M — predicates must leave no partial mutation (design §8) |
| Architecture Module | `internal/statusline/transcript_wshape.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.019 — composes with: the 21 table tests
- BC-1.03.020 — related to: legacy-poisoned `cur.out` reader rule (OD-32)
- BC-1.03.021 — related to: the non-skipped `lu`-null form
- BC-6.03.004 — depends on: exclusion-list machinery
- BC-1.03.004 — depends on: decode step

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript_wshape.go (W-predicates) (`transcript_wshape.go`) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — D4-EX-2 wrong-shape skip

## VP Anchors (Recommended)

- VP-029, VP-013 — no partial mutation; VP-012 — D4-EX-2 register closure (PC-5)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1059-1149) |
| **Confidence** | medium (Go-only predicates derived from legacy crash sites; all raise sites re-verified 2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: absence of type guards at the raise sites; oracle runs confirm each site

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

Implement `wshape(state, e) (cp string, skip bool)` evaluated before any mutation; record `cp` only for diagnostics
(never in stdout).
