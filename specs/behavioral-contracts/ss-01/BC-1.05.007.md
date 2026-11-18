---
document_type: behavioral-contract
level: L3
version: "1.3.5"
status: draft
producer: product-owner
timestamp: 2026-11-18T12:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r7.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "1e9a89d"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:601-636)"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-082"
parity_class: "byte-exact"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.3 2026-11-17: pass-2 remediation ADV-P2-C2-11b (reachable NaN rate)"
  - "1.3.1 2026-11-18: pass-3 remediation ADV-P3-C2-01 (CP-O10/CP-O11 overflow crash paths; ruling OD-156; OD-166 record guard cross-ref)"
  - "1.3.2 2026-11-18: pass-5 remediation ADV-P5-C2-19 (H1 enriched with the ⛏ format per bc_h1_is_title_source_of_truth)"
  - "1.3.3 2026-11-18: pass-5 residual sweep (ADV-P5-A2-11/C15 reciprocal) — VP-001 row added to Verification Properties and VP Anchors (the stdin-borne CP-O10/O11 legs ride the never-blank ladder); no behavioral change"
  - "1.3.4 2026-11-18: pass-6 remediation ADV-P6-C2-10 (DI-008 lifted into the L2 invariants row — the CP-O10/O11 legs degrade to the 29-byte line, exit 0)"
  - "1.3.5 2026-11-18: pass-10 remediation ADV-P10-C2-12 sibling sweep (PC2's 3.6e6 ms-per-hour factor carries the unit-constant note, BC-1.05.002 Pre 4)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.05.007: $, $/h and ⛏ number formatting

## Description

The numbers inside the cost segment are formatted exactly as Python's fixed-point
format specs: `$` with `.2f` of the raw `total_cost_usd`, `$/h` with `.1f` of the
computed rate, and `⛏` with `.2f` of `eq`. Rounding is of the exact binary value
(correctly rounded, so ties in decimal look like half-even or half-down), never
`math.Round`, and non-finite values print Python's spelling.

## Preconditions

1. The cost segment exists (BC-1.05.001) and, for `$/h`, the rate gate passed
   (BC-1.05.002); for `⛏`, BC-1.05.003 decided to show a number.
2. Formatting goes through `pyfmt.F(x, prec)` (`internal/pyfmt` `[num]`, OD-103):
   `strconv.FormatFloat(x, 'f', prec, 64)` for finite values, which matches Python
   for every finite double including `-0`, plus Python spellings for non-finite values.

## Postconditions

1. `$` text = `"$" + F(usd, 2)` (SL:616). A bool `true` formats as `1.00`; an int
   formats as its float value.
2. `$/h` text = `" $" + F(r, 1) + "/h"` with `r = usd / (api_ms / 3.6e6)` (SL:623, 625;
   the ms-per-hour factor 3.6e6 is a unit constant — named constant, not config, the
   BC-1.05.002 Pre 4 note; ADV-P10-C2-12 sibling sweep).
3. `⛏` text = `" ⛏" + F(eq, 2)` (SL:635).
4. Non-finite: `+inf` → `inf` (so `$inf`, `$inf/h`, `⛏inf`). NaN never reaches `$`
   (the `usd > 0` guard is false for NaN). A NaN `api_ms` alone fails the
   `>= 300000` gate, but NaN `r` is reachable: `usd` = +Inf with `api_ms` = +Inf
   passes the gate and Inf/Inf = NaN → grey ` $nan/h` (SL:622-625).
5. No thousands separators, no exponent form: `1e16` → `10000000000000000.00`.
6. Catalogued stdin-borne overflow crash paths (ruling **OD-156**, taxonomy **CP-O10/**
   **CP-O11**; Oracle threshold verified on CPython 3.11.7, 2026-11-18: an exact int
   converts/formats iff |n| < 2**1024 - 2**970, and raises OverflowError at
   |n| >= 2**1024 - 2**970 — the int rounded to the halfway point between DBL_MAX and
   2**1024 overflows):
   - **CP-O10** — an exact stdin int `usd` with |usd| >= 2**1024 - 2**970 (309 digits,
      within the JSON 4,300-digit limit) raises OverflowError at the `f"{usd:.2f}"`
      format (SL:616) → the render degrades (BC-1.01.001), exit 0. Per OD-166 such a
      `usd` is not recorded into the cost history (BC-1.05.004), so no later refresh
      is poisoned.
   - **CP-O11** — an exact stdin int `api_ms` that passes the `>= 300000` gate with
      |api_ms| >= 2**1024 - 2**970 raises OverflowError at `usd / (api_ms / 3.6e6)`
      (SL:623) → degraded line. The gate comparison itself is exact (no error).
   The SL:255 threshold crash over a giant recorded entry then only arises from
   **foreign history** (hand-edited or legacy-written; exclusion id **OD-160**,
   BC-1.05.005 EC-011), never from hylo's own writer.

## Invariants

1. Formatting never changes the value used for colouring (colours use raw values,
   BC-1.05.001/002).
2. Go never uses `fmt` `%f` directly on these values (`NaN`/`+Inf` spelling differs,
   design IM-05).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | usd 0.125 | `$0.12` |
| EC-002 | usd 0.995 | `$0.99` |
| EC-003 | usd 1.005 | `$1.00` |
| EC-004 | usd 2.675 | `$2.67` |
| EC-005 | usd 999.995 | `$1000.00` |
| EC-006 | usd `true` | `$1.00` |
| EC-007 | usd +inf | `$inf`; with api 600000 → ` $inf/h` |
| EC-008 | usd 1e16, api 600000 | `$10000000000000000.00`, ` $60000000000000000.0/h` |
| EC-009 | api +inf | `r = 0.0` → ` $0.0/h` |
| EC-010 | usd +inf, api +inf | ` $nan/h`, grey (NaN rate: Inf/Inf at SL:622-625) |
| EC-011 | usd = 2**1024 (309-digit exact stdin int) | OverflowError at `f"{usd:.2f}"` (SL:616) → degraded line (CP-O10, OD-156); boundary: magnitude 2**1024 - 2**970 raises; magnitude 2**1024 - 2**970 - 1 formats (rounds to DBL_MAX) as CPython `format(2**1024 - 2**970 - 1, ".2f")` (ADV-P3-C2-01) |
| EC-012 | usd 1.0, api_ms = 2**1024 (309-digit exact int, passes gate) | OverflowError at `usd / (api_ms / 3.6e6)` (SL:623) → degraded line (CP-O11, OD-156); not recorded (OD-166) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| usd 32.62, api 6,711,428.57 | `$32.62`, ` $17.5/h` (r = 17.497318011387254) | happy-path |
| usd 1.0, api 300,000 | `$1.00`, ` $12.0/h` | edge-case |
| usd 13.99, api 600,000 | `$13.99`, ` $83.9/h` (r = 83.94000000000001) | edge-case |
| usd 1e16, api 600,000, cold start, lane anth | `\e[33m$10000000000000000.00\e[0m\e[90m $60000000000000000.0/h\e[0m` | edge-case |
| usd NaN | no segment | error |
| usd = 2**1024 - 2**970 (boundary, exact int) | degraded line (CP-O10); one unit smaller formats as `format(2**1024 - 2**970 - 1, ".2f")` = the DBL_MAX expansion | edge-case |
| usd 1.0, api_ms = 2**1024 - 2**970 (exact int) | degraded line (CP-O11 at SL:623) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-021 | `pyfmt.F(x, p)` equals CPython `format(x, f".{p}f")` for p ∈ {1, 2} over a generated corpus (boundaries, ties, subnormals, ±0, inf) | fuzz (differential vs the oracle) |
| VP-001 | The promised output set holds under the fault ladder incl. the stdin-borne overflow legs (CP-O10/O11): render output, the 29-byte degraded line, subagent JSON rows or zero bytes — never blank, exit 0 | fault-injection ladder (assertPromisedOutputSet, DI-008) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011, CAP-009 |
| L2 Domain Invariants | DI-008 (the stdin-borne CP-O10/CP-O11 overflow legs degrade to the shared 29-byte non-JSON line, exit 0 — the never-blank ladder; ADV-P6-C2-10) |
| Architecture Module | `internal/pyfmt` num.go `F`; `internal/statusline` cost.go (BC-COMPONENT-MAP: internal/statusline/cost.go ($, $/h formats) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:601-636; formats at SL:616, 625, 635) |
| Legacy contract | BC-SL-082 (P3 deep r1 row 123; `true → $1.00` re-verified P3r7) |
| Decisions | D4, OD-103 (single `internal/pyfmt`), OD-104 (CPython 3.11 oracle) |

## Related BCs (Recommended)

- BC-1.05.001 / BC-1.05.002 / BC-1.05.003 — consumed by
- BC-1.05.008 — verified by (goldens show the number/colour mismatches)
- BC-5.01.001 — depends on (`pyfmt` Round/RoundN/F, nan/inf spellings)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/cost.go ($, $/h formats) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost segment (filled by story-writer)

## VP Anchors (Recommended)

- VP-021 — `F` differential equivalence
- VP-001 — never-blank/exit-0 ladder; the stdin-borne CP-O10/O11 legs of this contract ride it


#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane (SL:601-636; formats at SL:616, 625, 635)) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: format-specifier bytes re-executed against CPython 3.11.7 (2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | only via injected `Env` seams |
| **Global state access** | none (seam-injected) |
| **Deterministic** | yes for widgets, given inputs and fake seams |
| **Thread safety** | single-threaded render loop |
| **Overall classification** | mixed (core-dominant) |

Owning component `internal/statusline` (BC-COMPONENT-MAP: sl/cost.go ($, $/h formats) - ARCH-03); the ARCH-00 package table classifies the package mixed (core-dominant) - pure widgets plus the effect script (AD-03), I/O only via `Env` seams.
