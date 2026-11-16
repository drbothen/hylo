---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, ../semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "0000000"
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
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.018: D4-EX-2 wrong-shape line W-predicates (skip, no partial mutation)

## Description

**Approved deviation D4-EX-2** (owner ruling Q-c, 2026-11-14). Legacy has seven transcript crash paths CP-T01..T07:
a decoded line with a wrong-shaped field raises mid-parse, the refresh degrades, the mix cache is not saved, and the
crash repeats on every later refresh (sticky; legacy contract BC-SL-068, replaced). hylo instead evaluates a
wrong-shape predicate `W(state, record)` per line **before** processing it and, when it holds, **skips the line with
exactly the effect of a JSON decode failure**: no parser state changes, its bytes are consumed, the cache is saved and
the refresh renders normally. This BC defines the seven predicates precisely so that a skipped line leaves no partial
mutation.

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
   `cur`, `lr`, `lu`, `seen_ids`, `recent_ids`. The offset still advances past the window's last LF.
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

4. **Equivalence oracle:** hylo on transcript T yields the same mix cache and render as legacy on T with the skipped
   lines deleted, except `size`, which equals legacy's plus the deleted lines' bytes (each + 1 for its LF).
5. **Exclusion:** every input that triggers a predicate is listed in the parity harness's named exclusion list
   (OD-105/OD-110), entry id `D4-EX-2`, file `internal/statusline/testdata/parity/exclusions.json`; each entry names
   its expected output file and its dedicated table test (BC-1.03.019). An entry without a test fails the harness; no
   globs.

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

The 21-row table with exact expected caches is BC-1.03.019. Representative rows:

| Input | Expected Output | Category |
|-------|----------------|----------|
| `U0, A2, [1, 2], S20` (T01+) | hylo cache = legacy cache of `U0, A2, S20` with `"size": 451` | error |
| `U0, A2, {}, S20` (T01−) | byte-exact with legacy, `"size": 447` | edge-case |
| T04+ out-only | `"tin": 110` (the `input_tokens: 5` of the skipped line is **not** added) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029, VP-013, VP-012 (frontmatter closure) | For every W-line, parser state after = state before (bit-identical) | proptest with generated W-lines per CP |
| VP-029, VP-013, VP-012 (frontmatter closure) | Delete-the-line equivalence holds on random transcripts with injected W-lines | fuzz (oracle on the transcript with W deleted) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1059-1149), _finish_turn (SL:988-996); raise sites as tabulated |
| Legacy contract | BC-SL-098 (pass-3 r2 §A6; refined r3); replaces BC-SL-068 (sticky crash) |
| Parity class | **D4-EX-2** (approved deviation, owner ruling Q-c 2026-11-14) |
| Exclusion entry | OD-105 / OD-110 named list, id `D4-EX-2`; dedicated tests = BC-1.03.019 (21 rows) + BC-1.03.020 rows |
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

- `architecture/ARCH-03-statusline.md#d4-ex-2` — internal/statusline/transcript_wshape.go (W-predicates) (`transcript_wshape.go`) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — D4-EX-2 wrong-shape skip

## VP Anchors (Recommended)

- VP-029, VP-013, VP-012 — no partial mutation

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
