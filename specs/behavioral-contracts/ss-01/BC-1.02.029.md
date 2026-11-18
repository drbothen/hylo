---
document_type: behavioral-contract
level: L3
version: "1.7"
status: draft
producer: product-owner
timestamp: 2026-11-17T23:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/ubiquitous-language.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "df5fc95"
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
modified:
  - "1.2 pass-4 remediation (ADV-P4-B21): cost.basis_min_shown_usd renamed to statusline.cost.display_floor_usd per OD-174; misleading-name disclaimers deleted; 2026-11-17T12:00:00Z"
  - "1.4 pass-6 remediation (ADV-P6-B08 + B16): the pick glyph is named as the registry key statusline.glyphs.cost_pick instead of the wildcard statusline.glyphs.* (Config keys row); history label version-prefixed; 2026-11-19T04:00:00Z"
  - "1.5 pass-9 remediation (ADV-P9-B03, orchestrator call 4): the legacy exact-int overflow leg registered as CP-O12 — PC1 qualifies float64 to converting tot values and states the SL:633 OverflowError degrade; EC-009 + a CP-O12 canonical vector minted (oracle-checked 2026-11-18 through the real entry point, isolated HOME and cwd); Related BCs gains the bearer kin BC-1.02.025; crash register now 49 paths (X4 S17 T8 N3 O12 A5); 2026-11-19T16:00:00Z"
  - "1.6 2026-11-20T18:00:00Z: pass-10 remediation (ADV-P10-B03): Verification Properties gains the VP-001 ladder row for the CP-O12 overflow degrade (EC-009) — 29-byte line, exit 0; reciprocal VP-001 bcs: sync is the architect's"
  - "1.7 2026-11-20T18:00:00Z: pass-10 remediation (ADV-P10-B07): Architecture Anchors bullet gains the file-family fragment anchor (sibling convention of BC-1.02.001..015); the Stories placeholder respelled from S-N.MM to the TBD convention; no behavioral change"
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

1. `eq` is computed left to right as `(tot * mtok) / 1e6` in float64 — on `tot` values that convert to float:
   legacy's `tot` is an exact int (BC-1.02.018), and at or beyond the registered int→float conversion threshold
   (error-taxonomy "Conversion threshold": raises only for `|n| >= 2**1024 − 2**970`) the multiply
   `tot * mtok` (SL:633) itself raises uncaught OverflowError and the whole line degrades (CP-O12, EC-009) —
   it does not yield `inf`.
2. If `eq >= statusline.cost.display_floor_usd` (default 0.005, operator `>=`): append `\e[90m ⛏` +
   `F(eq, 2)` + `\e[0m` to the `$` block (half-even `.2f`; `inf` spelled `inf`).
3. Otherwise append nothing.

## Invariants

1. A below-threshold estimate never renders `⛏n/a`.
2. The 0.005 default comes from `statusline.cost.display_floor_usd` (register T-044: "skip sub-half-cent noise"),
   named for what it is: the display floor of the `eq` estimate. The real basis guard is
   `statusline.cost.basis_min_mtok_month`.
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
| EC-009 | `tin`/`tout` each below the int→float conversion threshold but their exact-int sum `tot` (SL:626) at or above it; local lane, valid basis | the multiply `tot * mtok` (SL:633) raises uncaught OverflowError → guard line (OD-156; taxonomy **CP-O12**): exactly the 29-byte degraded line, exit 0, earlier writes kept — **not** `⛏inf` (a float64 port that computes `inf` and renders `⛏inf` is a parity diff) |

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

CP-O12 cost-pick equivalence overflow (pass-9 ADV-P9-B03; oracle-checked 2026-11-18 through the real entry point
`python3 -I -s legacy/dgx_statusline.py` with an isolated HOME and cwd, CPython 3.11.7): the bearer is the
integer-only transcript accumulation (kin of CP-O04, BC-1.02.025 EC-010). Seed: stdin `{"session_id":"r4",
"transcript_path":"<T>","workspace":{"project_dir":"<T>"},"model":{"id":"claude-sonnet-x"},
"cost":{"total_cost_usd":0.5}}` (local lane, prefixes `claude-sonnet`); session cache `statusline-r4.json` seeded
`{"fetch_ts": <now>, "ts": <now>, "up": true, "sample": {"dgx_cost:dgx_usd_per_mtok": 2.0,
"dgx_tokens:rate_mtok_month": 1000000000}}` (valid basis, fresh TTL); transcript one assistant line
`{"type":"assistant","timestamp":"2026-11-18T12:00:00.000Z","message":{"id":"msg_1","usage":
{"input_tokens": 95·10³⁰⁶, "output_tokens": 95·10³⁰⁶}}}` — each total below the conversion threshold (float()
succeeds), `tot = 1.9·10³⁰⁸` at or above it (SL:626). Expected: exactly `\e[90mstatusline degraded\e[0m\n` (29
bytes: `1b 5b 39 30 6d` + `statusline degraded` + `1b 5b 30 6d 0a`), exit 0; the step-2 mix cache and the step-7c
cost-history write persist (measured: `statusline-mix-r4.json` and `cost-history.json` present after the run; the
session cache additionally admitted a machine-dependent trailing `proc_start` key, BC-1.01.001 EC-003-style).
Control (same seed, totals 4·10³⁰⁷ each, `tot = 8·10³⁰⁷` below the threshold): full render, no degrade. Boundary
measured on the same oracle: `float(2**1024 − 2**970 − 1)` converts, `float(2**1024 − 2**970)` raises.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | With a valid basis, `⛏` present iff `(tot*mtok)/1e6 >= 0.005` | generated table vs oracle |
| VP-028 | Below threshold never renders `n/a` | table test |
| VP-028, VP-001 | The CP-O12 overflow degrade (EC-009: exact-int `tot` at or above the int→float bound enters `tot * mtok`, SL:633) stays on the never-blank ladder — exactly the 29-byte degraded line, exit 0 | table test (fault-injection row of VP-001's ladder) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 (owned-hardware cost), CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/cost.go`; BC-COMPONENT-MAP: internal/statusline/cost.go (pick eq 0.005) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:633-635, inside the ⛏ block SL:626-636) |
| Legacy contract | BC-SL-083 (deep pass-3 round 1, new) |
| Config keys | `statusline.cost.display_floor_usd` (T-044, renamed from `cost.basis_min_shown_usd` by OD-174), `statusline.cost.basis_min_mtok_month`, `backends[0].model_prefixes` (OD-123), `statusline.glyphs.cost_pick` (⛏) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.05.003 — composes with (⛏ pick inside the `$` block; basis threshold and `n/a`)
- BC-1.02.001 — depends on (client-view lane)
- BC-1.02.018 — depends on (transcript token totals)
- BC-1.02.025 — related to (same integer-only transcript bearer: CP-O04 at `_fmt_tok_c`, CP-O12 at the SL:633 multiply)
- S1.04 metrics BCs — depends on (`mtok` and `rate` from the sample)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#cost` — internal/statusline/cost.go (pick eq 0.005) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-028 — threshold presence

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
