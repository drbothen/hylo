---
document_type: behavioral-contract
level: L3
version: "1.3.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T13:05:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "75de44d"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_finish_turn, _mix_counts (SL:988-996, 1023, 1073-1079, 1150-1153)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-100"
parity_class: "D4-EX-2"
confidence: "M"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: VP citation reconciliation — VP-012 added", "1.2.2 2026-11-17: pass-4 residual sweep — exclusions.json path canonicalized to internal/parity/testdata/exclusions.json", "1.2.3 2026-11-18T22:00:00Z: pass-4 correction (item 10) — exclusions.json path restored to the OD-148 home internal/statusline/testdata/parity/exclusions.json", "1.3.0 2026-11-20T18:00:00Z: pass-9 remediation (ADV-P9-C10/C11) — VP row: only C1 maps to BC-1.03.019 row 13; C2's native-hylo reference is row 15 plus appended A9/S11 (lr [90.0, false]); EC-005 quotes OD-32 literally (cur.t0 is a number) and credits CONV-ABS-15 for the non-numeric-out half", "1.3.1 2026-11-22T12:00:00Z: pass-11 remediation (ADV-P11-C03) — absent-out pin: a cur object with the out key absent does not fire the OD-32 rule (legacy coerces the missing key to 0, cur.get(out) or 0, SL:993) and never crashes; PC1 requires out present and non-numeric; EC-007 added, EC-005 and the VP predicate row name exclusion id OD-160 like siblings (BC-1.03.002 EC-007..009, BC-1.03.005 PC5)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.020: Legacy-poisoned cur.out reader rule (OD-32)

## Description

**Part of the approved deviation D4-EX-2.** When a CP-T05 opening line is followed by no closer in the same parse
window, legacy saves the open turn with a non-numeric `out` (e.g. `"cur": {"id": "msg_A", "t0": 1794650400.0, "t1":
1794650408.0, "out": "abc"}`) and then crashes at SL:994 on the first later refresh whose lines close that turn,
stickily. hylo can meet such a **legacy-written** mix cache (cache-swap, first run after cutover). The reader rule
(OD-32, amended per CONV-ABS-15): on load, treat `cur` as absent **only** when `cur.t0` is a number and `cur.out` is
not int/float/bool; keep every other `cur` verbatim. A `cur` with the `out` key **absent** does not fire the
rule: legacy coerces the missing key to 0 (`cur.get("out") or 0`, SL:993) and never crashes on it; hylo keeps
such `cur` verbatim (EC-007). hylo then never crashes on it; turn state converges with native
hylo at the next turn event, with a known composition residual.

## Preconditions

1. A mix cache loaded by BC-1.03.002 contains `cur` as an object with `t0` a number — "number" as defined in BC-1.03.018: int, float or bool, so a bool `t0` counts as a number and fires the rule (pinned; arises only with foreign caches) — and `out` present and a JSON
   value that is not int/float/bool (string, array, object; see EC-004 for falsy non-numbers). A `cur` with the
   `out` key absent does not fire the rule (legacy coerces it to 0 at SL:993 — EC-007).
2. Only a legacy-written cache can contain this form: hylo's own parser never writes it (it skips the opening line,
   BC-1.03.018 CP-T05).

## Postconditions

1. Immediately after load (before the reset checks and before parsing), hylo sets `cur = null`; `lr`, `lu` and all
   other cached fields are unchanged.
2. If the refresh then has no new bytes (`size == off`), nothing is written (BC-1.03.002) and stdout is unaffected
   (rendering uses `lr`, not `cur`).
3. Otherwise parsing continues from the cached offset with `cur = null`, and the cache written at the end carries the
   resulting state.
4. **Known residual (accepted):** the composition of the poisoned line (counted by legacy before it saved the cache)
   stays counted; hylo cannot undo it. Turn state (`lr`, `lu`, `cur`, `tout`, `ids`) matches native hylo from the next
   turn event on.
5. **Exclusion:** the cache-swap cases that exercise this rule are listed under the D4-EX-2 entry of the OD-105/OD-110
   named exclusion list (`internal/statusline/testdata/parity/exclusions.json`), each with an expected output file and
   a dedicated table test (`TestMixCache_OD32_*`); legacy degrades on them while hylo renders.

## Invariants

1. The rule never fires for a `cur` whose `t0` is null (BC-1.03.021), nor for a numeric/bool `out`.
2. The rule never alters a cache that hylo itself wrote.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Poisoned cache, then a closer (U9) | legacy: TypeError SL:994, cache unchanged, degraded, sticky; hylo: renders, writes the C1 cache below |
| EC-002 | Poisoned cache, then a continuation line of the same id with no closer | legacy does **not** crash (it only moves `t1`); hylo opens a new turn instead → caches differ (C3 below); excluded under D4-EX-2 |
| EC-003 | `out` is `["x"]` or `{"a": 1}` | same as `"abc"` (legacy crashes at the closer; hylo applies the rule) |
| EC-004 | `out` is `true` or `1.5` (numbers) | rule does not fire; legacy and hylo agree (no crash) |
| EC-005 | `out` null / `""` / `[]` / `{}` (falsy non-numbers) | unreachable from either writer (SL:1079 coerces falsy to 0); a foreign-cache state (CP-C class, ruling b, exclusion id `OD-160` — sibling
convention, BC-1.03.002 EC-007..009 / BC-1.03.005 PC5; out of byte-parity scope). OD-32's literal text ("treat as no open turn when cur.t0 is a number") treats them as absent; the non-numeric-`out` half comes from CONV-ABS-15; hylo follows both |
| EC-006 | `cur.t0` null with `out` `"abc"` | rule does **not** fire (BC-1.03.021) |
| EC-007 | `out` key absent, `t0` a number (foreign cache; neither writer emits a `cur` without `out` — SL:1079 always sets it) | rule does **not** fire: legacy coerces the missing key to 0 (`cur.get("out") or 0`, SL:993) and closes or continues the turn without crashing; hylo keeps `cur` verbatim and agrees (turn state converges from the next turn event); foreign-cache shape (ruling b, exclusion id `OD-160`) |

## Canonical Test Vectors

Seed `P` (legacy-written, from BC-1.03.019 row 15): `{"size": 778, "res": 0, "conv": 20, "think": 0, "tin": 220,
"tout": 15, "c_wr": 200, "c_rd": 0, "mixv6": 1, "c_in": 20, "rb": 0, "pp": 110, "ids": ["msg_A", "msg_B"], "lr":
[5.0, true], "lu": 1794650400.0, "cur": {"id": "msg_A", "t0": 1794650400.0, "t1": 1794650408.0, "out": "abc"}}`,
transcript = row 15's (`U0, A2', B5, W5`, 778 B) plus the appended lines. `A9` = A2' with `"output_tokens": 900` and
timestamp `2026-11-14T10:00:10Z`; `S11` = S20 at `10:00:11Z`. TZ=UTC. Re-pinned 2026-11-15 (legacy oracle; hylo
expectation = legacy run on the seed with `cur` replaced by null).

| Input | Expected Output | Category |
|-------|----------------|----------|
| C1: seed `P`, append `U9` | hylo: `{"size": 887, "res": 0, "conv": 31, "think": 0, "tin": 220, "tout": 15, "c_wr": 200, "c_rd": 0, "mixv6": 1, "c_in": 20, "rb": 0, "pp": 110, "ids": ["msg_A", "msg_B"], "lr": [5.0, true], "lu": 1794650409.0, "cur": null}`; legacy: degraded line, seed bytes unchanged. (Native hylo, row 13: same but `"conv": 28` — the +3 residual is `W5`'s `"Hi."`) | happy-path |
| C2: seed `P`, append `A9`, `S11` | hylo: `{"size": 1114, …, "conv": 23, …, "lr": [90.0, false], "lu": 1794650400.0, "cur": null}`; legacy: degraded | happy-path |
| C3: seed `P`, append `A9` only | hylo: `{"size": 1030, …, "conv": 23, …, "lr": [5.0, true], "lu": 1794650400.0, "cur": {"id": "msg_A", "t0": 1794650400.0, "t1": 1794650410.0, "out": 900}}`; legacy (no crash): same but `"cur": {"id": "msg_A", "t0": 1794650400.0, "t1": 1794650410.0, "out": "abc"}` | edge-case |
| seed `P` with `"out": 1.5`, append `U9` | rule does not fire; hylo = legacy (no crash, `"conv": 31`) | edge-case |
| seed `P`, no new bytes | no write; stdout as legacy for the same `lr` | edge-case |

(`…` elides fields equal to C1's.)

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029, VP-013 | Rule fires iff `cur` is an object, `t0` is a number (int, float or bool), `out` is present and not a number (an absent `out` key does not fire — EC-007) | table test |
| VP-029, VP-013 | After the rule and one turn event, turn state equals native hylo's | table test (C1 vs BC-1.03.019 row 13; C2's native-hylo reference is row 15 plus appended `A9`, `S11`, giving `lr [90.0, false]`) |
| VP-012 | Postcondition 5 closure: the OD-32 cache-swap cases are admitted under the closed D4-EX-2 register, each with an expected output file and a dedicated `TestMixCache_OD32_*` test; no globs | repository test over `exclusions.json` |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Source | legacy/dgx_statusline.py:_finish_turn (SL:988-996), _mix_counts (SL:1023, 1073-1079, 1150-1153) |
| Legacy contract | BC-SL-100 (pass-3 r3 §3.2; confirmed r4 §1.1; rationale retracted CONV-ABS-15, amended rule confirmed r5) |
| Parity class | **D4-EX-2** (OD-32 reader rule) |
| Decisions | OD-32 (amended: `t0` numeric condition), D4-EX-2 (Q-c), OD-105 / OD-110 |
| Exclusion entry | id `D4-EX-2` in `exclusions.json`; dedicated tests `TestMixCache_OD32_*` (C1, C2, C3, numeric-out negative) |
| Confidence note | M — the rule applies only when `t0` is numeric (design §8) |
| Architecture Module | `internal/statusline/mixcache.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.021 — related to: the `t0`-null form kept verbatim
- BC-1.03.018 — depends on: CP-T05 predicate (why hylo never writes this form)
- BC-1.03.019 — related to: row 15 produces the seed
- BC-6.02.004 — related to: cache-swap coverage (Python writes, Go reads)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/mixcache.go (OD-32 reader rule) (reader rule in `mixcache.go`) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — mix cache

## VP Anchors (Recommended)

- VP-029, VP-013 — reader-rule predicate; VP-012 — D4-EX-2 register closure (PC-5)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:988-996, 1023, 1073-1079, 1150-1153) |
| **Confidence** | medium (Go-only rule; legacy mechanism high) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: legacy saves `cur` verbatim (SL:1153) and compares `out <= 0` without a type guard (SL:994)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (applied to the loaded `Value`) |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

`applyOD32(cache Value) Value` called right after `CacheStore.Load`; pure and table-testable.
