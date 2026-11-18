---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md]
input-hash: "ab38ca7"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_telemetry_fields (SL:773-781)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-085"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.2.1 2026-11-18: pass-8 remediation ADV-P8-C2-01 (the marker named as the config key statusline.glyphs.sess_rate with default », OD-189 sibling treatment) + ADV-P8-C2-08 (testing/quick leg routed to the VP-030 quick leg, pass-8 call 12)"
  - "1.2.2 2026-11-18: pass-10 remediation ADV-P10-C2-09 (PC-1 qualifier — an exact-int lr[0] of magnitude >= 2**1024 - 2**970 raises OverflowError at the f{x:.0f} render format → degraded line, tagged OD-160; VP-030 quick-leg generator restricted accordingly; oracle-verified CPython 3.11.7)"
  - "1.2.3 2026-11-18: pass-10 remediation ADV-P10-C2-09 residual (VP-030 row respelled to the narrowed generator — lr[0] generated as bool or float-range number only; the OD-160 exact-giant-int cache shape excluded as a VP-001 degrade site, not a presence/dimming case)"
  - "1.2.4 2026-11-18: pass-11 remediation ADV-P11-C2-02 (sibling lift: L2 row carries DI-008 and DI-012 beside DI-007; VP-012 closure row for OD-160 and VP-001 never-blank row added, with VP Anchors entries) + ADV-P11-C2-08 (format crash site SL:776-777 → SL:778-779 — 776 is the isinstance guard, 777 sets dim) + OD-194 consumer (PC4 names statusline.labels.tps beside its default)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.018: Mine (last-turn) segment

## Description

The `»N t/s` segment shows this session's last completed API call rate from the transcript
(both lanes), bright when the reply was large enough to measure throughput and grey ("dim")
when it was short and latency-dominated. The input shape rules are Python's: a non-empty
list or tuple whose first element is a number. Notation: `\e` is byte 0x1B.

## Preconditions

1. `sess_rate` = transcript value `mix[7]` (BC-1.03.010; the dim flag is set by the
   transcript machine when the reply had fewer than `statusline.turn.dim_below_out` output
   tokens, default 200).

## Postconditions

1. Segment exists iff `sess_rate` is a list or tuple, non-empty, and `sess_rate[0]` is a
   number (bool, int or float; NaN and ±Inf included). Qualifier (foreign mix-cache
   shape, exclusion id **OD-160**, ADV-P10-C2-09): an `lr[0]` that is an exact INT of
   magnitude >= 2**1024 - 2**970 passes that existence check but raises `OverflowError`
   at the `f"{x:.0f}"` render format (SL:778-779 — 776 is the isinstance guard and 777
   sets `dim`; "int too large to convert to float";
   oracle-verified CPython 3.11.7, 2026-11-18) → degraded line. The VP-030 quick leg's
   `mix[7]` generator stays within floats and format-exact ints, never generating the
   OD-160 shape.
2. `dim = len(sess_rate) > 1 and truthy(sess_rate[1])` (Python truthiness: `""`, `0`,
   `False`, `None`, `[]`, `{}` are false; any non-empty string is true).
3. `mine = "\e[90m" + F(sess_rate[0],0) + "\e[0m"` if dim, else
   `"\e[1m\e[97m" + F(sess_rate[0],0) + "\e[0m"`.
4. Segment = `"\e[90m" + glyphs.sess_rate + "\e[0m" + mine + "\e[90m" + labels.tps + "\e[0m"`, placed
   before the box segment, where `glyphs.sess_rate` = `statusline.glyphs.sess_rate`
   (Text, default `»` U+00BB, BC-2.01.004 PC-6; the subagent `running` glyph shares the
   code point via its own family key; the » literals in the vectors are the default
   spelling, ADV-P8-C2-01) and `labels.tps` = `statusline.labels.tps` (Text, default
   `t/s`, SL:783, OD-194 — the same key BC-1.04.008 PC1 names for its SL:781 site).
5. Stale mode does not change this segment (it comes from the transcript, not the metrics
   store).

## Invariants

1. A 1-element list renders bright.
2. Extra elements beyond index 1 are ignored.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `[81.5, true]` | grey `82` (half-even) |
| EC-002 | `[82.5, 1]` | grey `82` |
| EC-003 | `[0.5, false]` / `[1.5, false]` | bright `0` / `2` |
| EC-004 | `[]`, `"x"`, `[null, true]`, none | hidden |
| EC-005 | `[NaN, false]` / `[+Inf, 0]` | bright `nan` / `inf` |
| EC-006 | `[true]` | bright `1` |
| EC-007 | `[113.4, "x"]` / `[113.4, ""]` | grey `113` / bright `113` |
| EC-008 | `[113.4, false, 9]` | bright `113` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `[113.4, false]` | `\e[90m»\e[0m\e[1m\e[97m113\e[0m\e[90mt/s\e[0m` | happy-path |
| `[81.5, true]` | `\e[90m»\e[0m\e[90m82\e[0m\e[90mt/s\e[0m` | edge-case |
| `[5]` | `\e[90m»\e[0m\e[1m\e[97m5\e[0m\e[90mt/s\e[0m` | edge-case |
| `[null, true]` | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Segment presence and dimming equal legacy for generated `mix[7]` values whose `lr[0]` is a bool or a float-range number (VP-030's quick-leg generator; the OD-160 foreign exact-giant-int `lr[0]` cache shape is excluded from the generator — its `.0f` rendering is a degrade site on VP-001's ladder, not a presence/dimming case — PC-1 qualifier, ADV-P10-C2-09) | Go property test (testing/quick) (generated Values; routed to the VP-030 quick leg, pass-8 call 12) |
| VP-012 | The named deviation this contract carries — exclusion id `OD-160` (PC-1 foreign exact-giant-int `lr[0]` mix-cache shape out of parity scope, ADV-P10-C2-09) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-160` entry and its riding table test `TestForeignCacheShape_OD160_Vectors` (this contract has no riding test of its own, same citation class as BC-1.04.002/BC-1.04.003), and the mutation test fails closed if that entry is dropped (ADV-P11-C2-02) | property test (VP-012, go test) |
| VP-001 | The promised output set holds on the OD-160 exact-giant-int OverflowError degrade leg (PC-1 qualifier): render output or the 29-byte degraded line — never blank, exit 0 (DI-008) | fault-injection ladder (assertPromisedOutputSet, DI-008) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:773-781); main (SL:1225) |
| Legacy contract | BC-SL-085 (P3 r1 new) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007, DI-008 (the PC-1 OD-160 OverflowError degrade rides the never-blank ladder: 29-byte line, exit 0), DI-012 (foreign exact-giant-int mix-cache shape OD-160 under the named-deviation rule) |
| Decisions | OD-113 |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.008 — refines: throughput segments
- BC-1.03.010 — depends on: last-turn rate machine
- BC-5.01.001 — depends on: `.0f` half-even

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/row2.go (mine) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — mine segment shapes
- VP-001 — never-blank/exit-0 ladder; the OD-160 exact-giant-int degrade leg rides it (ADV-P11-C2-02)
- VP-012 — OD-160 exclusion closure (citation-only, no riding test of its own)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:773-781) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **type constraint**: `isinstance(sess_rate, (list, tuple)) and sess_rate and isinstance(sess_rate[0], (int, float))` (SL:776)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; operate on `pyfmt.Value` (`IsNumber`, `Truthy`).
