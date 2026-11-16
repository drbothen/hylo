---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, ../semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, ../semport/hylo-legacy/statusline-target-design.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-024"
parity_class: byte-exact
confidence: H
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

# Behavioral Contract BC-1.02.018: Token segment formats via _fmt_tok_c

> Byte notation used below: `\e` = ESC (0x1B). All other characters are literal UTF-8.

## Description

Row 1 shows the session's token totals as `↑total[in ✍ ⟳] ↓out ↻n`: all prompt tokens sent, the non-overlapping
price classes in brackets (only when two or more are non-zero), output tokens, and cache rebuilds. The values come
only from the transcript accumulation (S1.03), never from stdin. Every count is formatted by `_fmt_tok_c`
(BC-1.02.025); the rebuild count uses `.0f`.

## Preconditions

1. `mix` is the transcript accumulation tuple produced by S1.03 (or `None`).
2. When `len(mix) >= 7`: `tin = mix[3]`, `tout = mix[4]`, `c_wr = mix[5]`, `c_rd = mix[6]`; otherwise all are `None`.
3. When `len(mix) >= 10`: `c_in = mix[8]`, `rb = mix[9]`; otherwise both are `None`.
4. Default theme (OD-113): GREY `\e[90m`, WHITE `\e[97m`, YELLOW `\e[33m`, CYAN `\e[36m`, DIM `\e[2m`, RESET `\e[0m`.

## Postconditions

1. The segment is shown iff (`tin` is numeric or `tout` is numeric) and (`(tin or 0) > 0` or `(tout or 0) > 0`),
   with Python truthiness (`None`/0 → 0) and numeric = int or float.
2. When shown, the segment bytes are, in order:
   1. `\e[90m↑\e[0m\e[97m` + `_fmt_tok_c(tin or 0)` + `\e[0m`;
   2. inner parts, each only when its value is numeric and `> 0`, in this order:
      `\e[97min` + `_fmt_tok_c(c_in)` + `\e[0m`, `\e[33m✍` + `_fmt_tok_c(c_wr)` + `\e[0m`,
      `\e[36m⟳` + `_fmt_tok_c(c_rd)` + `\e[0m`;
   3. if there are **two or more** inner parts: `\e[2m[\e[0m` + parts joined by one space + `\e[2m]\e[0m`
      (a single part equals `↑` and is omitted entirely);
   4. `\e[90m ↓\e[0m\e[97m` + `_fmt_tok_c(tout or 0)` + `\e[0m`;
   5. if `rb` is numeric and `> 0`: ` \e[2m\e[33m↻` + `format(rb, ".0f")` (half-even) + `\e[0m`.
3. When not shown, no segment is appended.

## Invariants

1. The segment never reads stdin token fields (`context_window.total_*` are the last response, not the session;
   review 2026-11-13 #10.1).
2. Glyphs `↑ ✍ ⟳ ↓ ↻` and the `in` label are legacy defaults of `statusline.glyphs.*`; colours are
   `statusline.theme.*` (OD-113).
3. Compact units follow `statusline.units.tokens` (T-042: 1000 / 1e6, `>=`; approved mockup, review #10 revisit).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | All totals 0 | segment hidden |
| EC-002 | `tin = 0`, `tout = 50` | shown: `↑0 ↓50` |
| EC-003 | `tin` = NaN, `tout = 0` | hidden (`NaN > 0` false) |
| EC-004 | `tin` = NaN, `tout = 10` | shown with `↑nan` |
| EC-005 | Exactly one non-zero inner part | no brackets, no part |
| EC-006 | `tout` = `None` with `tin > 0` | `↓0` |
| EC-007 | `rb = 1.5` | `↻2` (half-even `.0f`) |
| EC-008 | `mix` of length 7 (no `c_in`, no `rb`) | only `✍`/`⟳` can be inner parts; no `↻` |
| EC-009 | `tin` a non-numeric truthy value with numeric `tout` | legacy raises TypeError at SL:586 → degraded line; whether S1.03 can deliver such a value is governed by the S1.03 contracts (D4-EX-2 skips wrong-shape lines) |

## Canonical Test Vectors

Input is `mix` (indices 3,4,5,6,8,9 = tin, tout, c_wr, c_rd, c_in, rb); output is the exact token segment.

| Input | Expected Output | Category |
|-------|----------------|----------|
| tin 970000, tout 4200, c_wr 20000, c_rd 900000, c_in 50000, rb 2 | `\e[90m↑\e[0m\e[97m970k\e[0m\e[2m[\e[0m\e[97min50k\e[0m \e[33m✍20k\e[0m \e[36m⟳900k\e[0m\e[2m]\e[0m\e[90m ↓\e[0m\e[97m4k\e[0m \e[2m\e[33m↻2\e[0m` | happy-path |
| tin 5000, tout 100, c_wr 0, c_rd 4000, c_in 1000, rb 0 | `\e[90m↑\e[0m\e[97m5k\e[0m\e[2m[\e[0m\e[97min1k\e[0m \e[36m⟳4k\e[0m\e[2m]\e[0m\e[90m ↓\e[0m\e[97m100\e[0m` | happy-path |
| tin 1200, tout 300, c_wr 0, c_rd 0, c_in 1200, rb 0 | `\e[90m↑\e[0m\e[97m1k\e[0m\e[90m ↓\e[0m\e[97m300\e[0m` | edge-case (one part, no brackets) |
| length-7 mix: tin 1200, tout 300, c_wr 10, c_rd 20 | `\e[90m↑\e[0m\e[97m1k\e[0m\e[2m[\e[0m\e[33m✍10\e[0m \e[36m⟳20\e[0m\e[2m]\e[0m\e[90m ↓\e[0m\e[97m300\e[0m` | edge-case |
| tin 2500, tout 999500, c_rd 2500, rb 1.5 | `\e[90m↑\e[0m\e[97m2k\e[0m\e[90m ↓\e[0m\e[97m1000k\e[0m \e[2m\e[33m↻2\e[0m` | edge-case (no promotion, half-even) |
| tin NaN, tout 10 | `\e[90m↑\e[0m\e[97mnan\e[0m\e[90m ↓\e[0m\e[97m10\e[0m` | edge-case |
| tin 0, tout 0 | segment absent | edge-case |
| tin `"x"`, tout 5 | whole stdout = `\e[90mstatusline degraded\e[0m\n` (legacy oracle) | error |

Pinned 2026-11-15 with the legacy `render_lane` under CPython 3.11 (oracle, OD-104).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | Brackets appear iff at least two inner parts are > 0 | proptest vs oracle |
| VP-TBD | Segment shown iff the visibility predicate of Postcondition 1 holds | table test |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 (transcript, not ledger), DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/tokens.go`; filled by architect) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:565-600) and legacy/dgx_statusline.py:_fmt_tok_c (SL:863-873) |
| Legacy contract | BC-SL-024 (pass-3 r1; refined deep pass-3 round 1) |
| Config keys | `statusline.units.tokens` (T-042), `statusline.glyphs.*`, `statusline.theme.*` (OD-113) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.025 — depends on (`_fmt_tok_c`, no unit promotion)
- S1.03 transcript BCs — depends on (source of `mix`)
- BC-1.02.029 — related to (`tot = tin + tout` feeds the ⛏ estimate)

## Architecture Anchors (Recommended)

- `architecture/[section-name].md#[anchor]` — filled by architect

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-TBD — bracket rule

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane SL:574-600; `_fmt_tok_c` SL:863-873) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `have_t` and `> 0` checks (SL:585-586), per-part `isinstance` checks (SL:589-598)
- **documentation**: SL:579-584 layout comment (owner-approved, review #10 revisit)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | unknown (single-threaded render) |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. Python truthiness (`tin or 0`) must be reproduced exactly (design IM-02); NaN is truthy.
