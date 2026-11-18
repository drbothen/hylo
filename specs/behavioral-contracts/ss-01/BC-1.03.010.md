---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:10Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "5cb6c46"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_iso_ts, _finish_turn, _mix_counts (SL:954-996, 1064-1087)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-039"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: EC-009 close-time overflow cross-ref (CP-T08, OD-156; ADV-P2-C01)", "1.2.2 2026-11-17: EC-009 overflow cited by taxonomy id CP-O08 (OD-156 register)", "1.2.3 2026-11-17: pass-3 remediation (ADV-P3-C06/C10/C17/C18): EC-009 redesigned per ruling OD-167 (closer skipped and in-flight turn dropped, no sticky state), finite ranges, CP-O08 canonical vector, DI-012 cited", "1.2.4 2026-11-18T08:00:00Z: pass-4 remediation: CP-O08 vector made self-contained (exact line templates, 100/467/160 B) and byte math re-pinned from the oracle — size 727 = 567 + 160 deleted, conv 3, cur null per OD-167 (was 656/conv 5/131 B; ADV-P4-C09)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.010: Last-turn rate machine

## Description

From timed transcript lines, the parser measures the delivered rate of the most recent completed API message on
**either lane** (local or cloud): output tokens of the message divided by the span from its triggering user line
(`lu`) to its last line. State is `cur` (the open turn `{id, t0, t1, out}`), `lu` (last timed user-line
timestamp) and `lr` (last rate `[rate, dim]`), all persisted in the mix cache. A turn opens on a new assistant
message id, extends on further lines of that id, and closes on a newer id, a real user prompt or any timed system
line. Turns that look stale or empty are skipped and keep the previous `lr`. The result feeds the row-2 last-turn
segment (BC-1.04.018).

## Preconditions

1. A decoded object line `e` (D4-EX-2 skips applied first, BC-1.03.018); `cur`, `lu`, `lr` from the cache (or
   null after reset).
2. `t_line = FromISOFormat(e.timestamp with "Z" replaced by "+00:00")` (BC-5.04.001): a non-string or unparsable
   timestamp gives null; a naive timestamp is local time (`Env.Loc`).
3. Config (D15): `statusline.turn.dim_below_out` = 200 tokens (T-055; documented: owner decision 2026-11-13 from a
   replay of 456 local-lane and 193 cloud-lane messages — shorter replies are latency-dominated, shown dimmed);
   `statusline.turn.floor_tps` = 15.0 (T-057; documented: the harness's per-agent decode floor);
   `statusline.turn.stale_factor` = 4.0 (T-058; judgment: margin for slow prefill). SL:954-974. **Valid ranges
   (OD-162), derived from legacy semantics; out-of-range = number-range config error (S2 schema, OD-114):**
   `dim_below_out >= 0` (a token-count threshold, `out < dim_below_out`, SL:996); `floor_tps > 0 (finite)`
   (divisor of `stale_factor × out / floor_tps`, SL:994 — 0 divides by zero; ADV-P3-C17); `stale_factor > 0
   (finite)` (multiplier forming the stale margin at SL:994; 0 collapses the filter, no legacy-derivable
   meaning).

## Postconditions

1. **Untimed line** (`t_line` null): no turn-state change.
2. **Timed assistant line with truthy `message.id`** (`m = e.message or {}`):
   - if `cur` is non-empty and `cur.id == m.id`: `cur.t1 = t_line` (position of `t1` in `cur` kept);
   - else: `lr = finish(cur, lr)`; `cur = {"id": m.id, "t0": lu, "t1": t_line, "out": (m.usage or {}).output_tokens
     or 0}` (key order `id, t0, t1, out`).
3. **Timed assistant line without a truthy id**: no change.
4. **Timed user line:** if `m.content` is **not** a list containing at least one object block with `type ==
   "tool_result"`, then `lr = finish(cur, lr)` and `cur = null`; in all cases `lu = t_line`.
5. **Timed system line** (any subtype, including `compact_boundary`): `lr = finish(cur, lr)`; `cur = null`.
6. **Other timed types** (e.g. `summary`): no change.
7. **finish(cur, lr):** return `lr` if `cur` is empty/null or `cur.t0` is null. Else `out = cur.out or 0`, `span =
   (cur.t1 or 0) − cur.t0`; return `lr` if `out ≤ 0` or `span ≤ 0` or `span > stale_factor × out / floor_tps`
   (evaluated as `(4.0 × out) / 15.0`, left to right); else return `[out / span, out < dim_below_out]`.
8. An open `cur` at the end of the window is persisted unfinished (`"cur": {...}`) and continues next refresh;
   `lu` is persisted too.
9. Cache form: `"lr": [<float repr>, true|false]` or `null`; NaN rate is written as `NaN` (row T16).

## Invariants

1. The turn step runs before the compaction check and before usage counting for the same line.
2. Turn identity uses `cur.id` only, never the dedup memory (BC-1.03.017).
3. `finish` tests `cur`/`t0` before reading `out`, so a `t0`-null turn with a non-numeric `out` never fails
   (BC-1.03.021).
4. A turn's `t0` is the `lu` at opening time; consecutive messages without a user line in between share `t0`.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `span == 4·out/15` exactly (80 s, out 300) | accepted: [3.75, false] (row T18) |
| EC-002 | No timed user line ever (`lu` null) | every turn skipped, `lr` null (row T10) |
| EC-003 | Tool_result-only or mixed tool_result user line | `lu` moves, turn stays open (rows T2/T3) |
| EC-004 | User line with `message: {}` | closes the turn (content not a list; row T5) |
| EC-005 | Out < 200 | rate shown dimmed: `[r, true]` (row T17) |
| EC-006 | First line `output_tokens` NaN | `[NaN, false]` (row T16) |
| EC-007 | Opening line with non-numeric `out` and `lu` set | legacy CP-T05 (crash at close); hylo skips the opening line (D4-EX-2, BC-1.03.018) |
| EC-008 | Naive timestamp (`2026-11-14T10:00:00`) | interpreted in `Env.Loc` (BC-5.04.001) |
| EC-009 | Closing a turn whose `out` is a huge int (magnitude ≥ 2^1024 − 2^970, ADV-P3-C07) with a float `span`: legacy raises `OverflowError` at SL:994/996 (oracle-verified) | CP-O08: hylo skips the **closer** line **and drops the in-flight turn** (`cur` → null; `lr`, `lu` unchanged), so later lines parse normally — no sticky state (ruling OD-167; ARCH-03 `#transcript`); legacy instead keeps the bad turn open, so every later closer re-raises and totals freeze (BC-1.03.018) |

## Canonical Test Vectors

The exhaustive pinned table is BC-1.03.016 (20 rows). Representative rows (TZ=UTC, base `2026-11-14T10:00:00Z`
= 1794650400.0, every assistant line `out` 300 unless noted):

| Input | Expected Output | Category |
|-------|----------------|----------|
| T1: U0, A2, A10, B12 | `"lr": [30.0, false]`; `"cur": {"id": "B", "t0": 1794650400.0, "t1": 1794650412.0, "out": 300}` | happy-path |
| T18: U0, A80, S81 | `"lr": [3.75, false]` | edge-case |
| T10: A2, B10, S11 | `"lr": null`, `"lu": null` | edge-case |
| T15: U0, A2 (out 10), B5 (out 5), A8 (`output_tokens: "abc"`), U9 | legacy: `TypeError` at SL:994, no cache; hylo (D4-EX-2): `"lr": [5.0, true]`, `"cur": null` | error |
| CP-O08 (ADV-P3-C10, byte math re-pinned ADV-P4-C09; TZ=UTC, base 1794650400.0). Self-contained templates (Python `json.dumps` defaults, each LF-terminated; the BC-1.03.016 PC2 family): U0 = `{"type": "user", "message": {"role": "user", "content": "go"}, "timestamp": "2026-11-14T10:00:00Z"}` (100 B); A2 = the A-template with id `A`, `{"output_tokens": 10^309}`, ts 10:00:02Z (467 B); B10 = the A-template with id `B`, `{"output_tokens": 300}`, ts 10:00:10Z (160 B), where A-template = `{"type": "assistant", "message": {"id": "<id>", "content": [{"type": "text", "text": "x"}], "usage": {"output_tokens": <out>}}, "timestamp": "<ts>"}`. Legacy on U0+A2+B10: `OverflowError` at SL:994 (`4.0 × out`) while processing the closer B10, degraded line, cache not saved (oracle-verified 2026-11-18) | hylo (OD-167: closer B10 skipped, in-flight turn dropped): cache exactly `{"size": 727, "res": 0, "conv": 3, "think": 0, "tin": 0, "tout": 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": 0, "ids": ["A"], "lr": null, "lu": 1794650400.0, "cur": null}` (lr/u.l re-pinned ADV-P4-C09: the legacy U0+A2 golden has `"size"` 567, `conv` 3 — oracle-run 2026-11-18; hylo `"size"` = 567 + 160 deleted bytes = 727 per BC-1.03.018 PC4, `cur` forced to null per OD-167) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | `finish` is pure and equals the CPython oracle for random `(out, t0, t1)` incl. NaN/inf | Go property test (testing/quick) vs oracle table |
| VP-029 | Go and legacy turn state agree on random timed transcripts | fuzz (Tier C) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 (lane-aware status line; client-view lane rate on both lanes) |
| L2 Domain Invariants | DI-007; DI-012 (the D4-EX-2/CP-O08 skip and the OD-167 turn-drop are named, tested deviations) |
| Source | legacy/dgx_statusline.py:_iso_ts (SL:977-985), _finish_turn (SL:988-996), _mix_counts (SL:1064-1087); constants SL:954-974 |
| Legacy contract | BC-SL-039 (base; refined pass-3 r1: out from the first line) |
| Thresholds | T-055 `statusline.turn.dim_below_out` 200; T-057 `statusline.turn.floor_tps` 15.0; T-058 `statusline.turn.stale_factor` 4.0 |
| Parity class | byte-exact |
| Architecture Module | `internal/statusline/transcript_turn.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.016 — composes with: the exhaustive 20-row table
- BC-1.03.017 — composes with: identity ignores the dedup memory
- BC-1.03.011 — related to: `out` from the first line
- BC-1.03.021 — related to: `t0`-null turns with non-numeric `out`
- BC-5.04.001 — depends on: timestamp parsing
- BC-1.04.018 — consumer: row-2 last-turn segment

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript_turn.go (rate machine) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — turn machine

## VP Anchors (Recommended)

- VP-029 — `finish` oracle parity

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:954-996, 1064-1087) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `_finish_turn` early returns (SL:991-995)
- **documentation**: SL:954-966, 1064-1068 (turn definition, thresholds, interleaving)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none (local time zone via injected `Env.Loc`) |
| **Deterministic** | yes, given the time zone |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

Hold `cur` as a `pyfmt.Value` object (raw `out`, BC-1.03.021); `finishTurn(cur Value, lr Value, cfg) Value`.
