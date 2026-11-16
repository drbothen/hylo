---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/ubiquitous-language.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, ../semport/hylo-legacy/statusline-target-design.md, ../semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-083"
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

# Behavioral Contract BC-1.02.029: Pick eq threshold 0.005

> Byte notation used below: `\e` = ESC (0x1B). All other characters are literal UTF-8.

## Description

On the local lane (client-view lane = backend), the `$` block appends the owned-hardware cost estimate
`⛏<usd>` for the session's tokens at the backend's blended cost per million tokens. When the basis is valid, the
estimate `eq = tot × mtok / 1e6` is shown only when `eq >= 0.005` (sub-half-cent noise is skipped), formatted with
two decimals. Below the threshold the `⛏` part is omitted entirely; it is **not** `⛏n/a` (that is the invalid-basis
case, BC-1.05.003).

## Preconditions

1. The `$` block is rendered: `cost.total_cost_usd` numeric and `> 0`.
2. Client-view lane is local: `model.id` starts with one of `backends[0].model_prefixes` (default `claude-sonnet`,
   OD-111/OD-123; BC-1.02.001).
3. `tot = (tin or 0) + (tout or 0) > 0` (transcript totals, BC-1.02.018).
4. The basis is valid (BC-1.05.003): `rate` (backend monthly token rate) numeric and
   `>= statusline.cost.basis_min_mtok_month` (default 30.4), and `mtok` (backend blended USD per million tokens from
   the metrics sample) numeric and `> 0`.
5. Default theme (OD-113): GREY `\e[90m`, RESET `\e[0m`.

## Postconditions

1. `eq` is computed left to right as `(tot * mtok) / 1e6` in float64.
2. If `eq >= statusline.cost.basis_min_shown_usd` (default 0.005, operator `>=`): append `\e[90m ⛏` +
   `F(eq, 2)` + `\e[0m` to the `$` block (half-even `.2f`; `inf` spelled `inf`).
3. Otherwise append nothing.

## Invariants

1. A below-threshold estimate never renders `⛏n/a`.
2. The 0.005 default comes from `statusline.cost.basis_min_shown_usd` (register T-044: "skip sub-half-cent noise").
3. Cloud-lane and unknown-lane sessions never show `⛏`.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | tot 1000, mtok 5.0 → eq exactly 0.005 | shown ` ⛏0.01` (`>=`; `.2f` of 0.005 rounds to 0.01) |
| EC-002 | tot 999, mtok 5.0 → eq 0.004995 | omitted (not `n/a`) |
| EC-003 | tot 1, mtok 5000.0 → eq 0.005 | shown ` ⛏0.01` |
| EC-004 | tot 1, mtok 4999.0 → eq 0.004999 | omitted |
| EC-005 | mtok = `+inf` | ` ⛏inf` |
| EC-006 | mtok NaN or `None`, or rate below 30.4 | basis invalid → ` ⛏n/a` (BC-1.05.003, not this contract) |
| EC-007 | tot = 0 | no `⛏` part at all |
| EC-008 | cloud-lane model | no `⛏` part |

## Canonical Test Vectors

stdin `{"model": {"id": "claude-sonnet-x"}, "cost": {"total_cost_usd": 0.5}}`, `backends[0].model_prefixes =
claude-sonnet`, rate = 1e9, transcript totals (tin, tout); output is the exact `$` block (`$0.50` is GREY because it
is below the $1 minimum, BC-1.05.001).

| Input (tin + tout, mtok) | Expected Output | Category |
|-------|----------------|----------|
| 2,000,000, 0.09 | `\e[90m$0.50\e[0m\e[90m ⛏0.18\e[0m` | happy-path |
| 600 + 400, 7.5 | `\e[90m$0.50\e[0m\e[90m ⛏0.01\e[0m` | happy-path |
| 1000, 5.0 | `\e[90m$0.50\e[0m\e[90m ⛏0.01\e[0m` | edge-case (exact threshold) |
| 999, 5.0 | `\e[90m$0.50\e[0m` | edge-case (omitted) |
| 1, 4999.0 | `\e[90m$0.50\e[0m` | edge-case |
| 1000, +inf | `\e[90m$0.50\e[0m\e[90m ⛏inf\e[0m` | edge-case |
| 1000, NaN | `\e[90m$0.50\e[0m\e[90m ⛏n/a\e[0m` (basis invalid; owned by BC-1.05.003) | error |

Pinned 2026-11-15 with the legacy `render_lane` under CPython 3.11 (oracle, OD-104) using the legacy prefix variable
(`LOCAL_MODEL_PREFIXES=claude-sonnet`, quoted as provenance only).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | With a valid basis, `⛏` present iff `(tot*mtok)/1e6 >= 0.005` | generated table vs oracle |
| VP-TBD | Below threshold never renders `n/a` | table test |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 (owned-hardware cost), CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/cost.go`; filled by architect) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:633-635, inside the ⛏ block SL:626-636) |
| Legacy contract | BC-SL-083 (deep pass-3 round 1, new) |
| Config keys | `statusline.cost.basis_min_shown_usd` (T-044), `statusline.cost.basis_min_mtok_month`, `backends[0].model_prefixes` (OD-123), `statusline.glyphs.*` |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.05.003 — composes with (⛏ pick inside the `$` block; basis threshold and `n/a`)
- BC-1.02.001 — depends on (client-view lane)
- BC-1.02.018 — depends on (transcript token totals)
- S1.04 metrics BCs — depends on (`mtok` and `rate` from the sample)

## Architecture Anchors (Recommended)

- `architecture/[section-name].md#[anchor]` — filled by architect

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-TBD — threshold presence

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane, SL:626-636) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if eq >= 0.005` (SL:634)
- **documentation**: SL:634 comment "skip sub-half-cent noise"

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config only |
| **Deterministic** | yes |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. Keep the multiplication order `(tot * mtok) / 1e6`.
