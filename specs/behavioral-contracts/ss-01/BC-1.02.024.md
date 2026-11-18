---
document_type: behavioral-contract
level: L3
version: "1.1.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/ubiquitous-language.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r5.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "2177115"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-061"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.1 pass-3 remediation (ADV-P3-B06): VP-028 grid centered on the rem = 0.9 x length boundary (544320 s for 7 d), not 0.10 x length; 2026-11-18T02:00:00Z"
  - "1.1.2 pass-7 remediation (ADV-P7-B12): history labels version-prefixed; no behavioral change; 2026-11-19T07:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.024: Pace band boundary at rem = 0.9 × length

> Byte notation used below: `\e` = ESC (0x1B). All other characters are literal UTF-8.

## Description

A plan window's colour uses projected use (`pct / elapsed`) only when `0.10 <= elapsed <= 1.0`, where
`elapsed = 1.0 - rem/length`; otherwise the absolute bands apply (BC-1.02.011). At exactly `rem = 0.9 × length`
the IEEE-754 result is `1.0 - 0.9 = 0.09999999999999998`, which is below 0.10, so the **absolute** bands apply. The
port must evaluate the same expression in the same order, so it lands on the same side of the boundary.

## Preconditions

1. A plan window (`five_hour`, length 18000 s; `seven_day`, length 604800 s) is reported, unexpired, with numeric
   clamped `pct` and numeric `resets_at` (BC-1.02.010/011).
2. `now` = the single per-render clock value (design IM-14); `rem = resets_at - now`.
3. Config defaults: `statusline.limits.projection_min_elapsed` 0.10 (T-032), `statusline.limits.projected_bands`
   red `> 100`, yellow `>= 80` (T-033), `statusline.limits.absolute_bands` red `> 90`, yellow `> 70` (T-034),
   `statusline.limits.windows` 5 h / 7 d (T-031).

## Postconditions

1. `elapsed` is computed as `1.0 - (rem / length)` in float64, exactly this expression (no algebraic rewrite such as
   `(length - rem) / length`, which yields exactly 0.1 at the boundary and would flip the band).
2. If `0.10 <= elapsed <= 1.0`: colour = RED `\e[31m` if `pct/elapsed > 100`, YELLOW `\e[33m` if `>= 80`, else GREY
   `\e[90m`.
3. Otherwise: colour = RED if `pct > 90`, YELLOW if `pct > 70`, else GREY.
4. At `rem = 0.9 × length` (exactly representable here: 544320 s for 7 d, 16200 s for 5 h) the absolute rule applies.

## Invariants

1. The comparison operators are exactly `0.10 <= elapsed <= 1.0`, `> 100`, `>= 80`, `> 90`, `> 70`.
2. The countdown text and its 1.15 gate are unaffected by which band rule applied (BC-1.02.012).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | 7 d, pct 75, rem = 544320 (elapsed 0.09999999999999998) | absolute → YELLOW |
| EC-002 | 7 d, pct 75, rem = 544319 (one second more elapsed; elapsed 0.10000165…) | projected 749.99 → RED |
| EC-003 | 7 d, pct 75, rem = 544321 | absolute → YELLOW |
| EC-004 | 7 d, pct 65 at the boundary | absolute → GREY |
| EC-005 | 7 d, pct 95 at the boundary | absolute → RED |
| EC-006 | 5 h, pct 8, rem = 16200 | absolute → GREY |

## Canonical Test Vectors

now = 1794600000.0; stdin `{"rate_limits": {KEY: {"used_percentage": P, "resets_at": now + REM}}}`; output is the
exact limits segment.

| Input (KEY, P, REM) | Expected Output | Category |
|-------|----------------|----------|
| seven_day, 75, 544319 | `\e[31m7d75%\e[0m \e[31m->6d07h\e[0m` | happy-path (pace bands) |
| seven_day, 75, 544320 | `\e[33m7d75%\e[0m \e[33m->6d07h\e[0m` | edge-case (boundary → absolute) |
| seven_day, 75, 544321 | `\e[33m7d75%\e[0m \e[33m->6d07h\e[0m` | edge-case |
| seven_day, 65, 544320 | `\e[90m7d65%\e[0m \e[90m->6d07h\e[0m` | edge-case |
| seven_day, 95, 544320 | `\e[31m7d95%\e[0m \e[31m->6d07h\e[0m` | edge-case |
| five_hour, 8, 16200 | `\e[90m5h8%\e[0m \e[90m->4h30m\e[0m` | edge-case |
| elapsed via `(length-rem)/length` at REM 544320, P 75 | must NOT be used: it yields 0.1 → projected 750 → RED, which differs from legacy YELLOW | error (forbidden rewrite) |

Pinned 2026-11-15 with the legacy `render_lane` under CPython 3.11 (oracle, OD-104); the boundary value
`1.0 - 0.9 = 0.09999999999999998 < 0.10` is also pinned in deep pass-3 round 5.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | For REM in a ±5 s grid around the `rem = 0.9 × length` boundary (544320 s for 7 d; 16200 s for 5 h) and P in 0..100, Go colour equals oracle colour | generated table vs oracle |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/limits.go`; BC-COMPONENT-MAP: internal/statusline/limits.go (0.9 pace boundary) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:515-521, inside limits block SL:487-532) |
| Legacy contract | BC-SL-061 (deep pass-3 round 1, new; confirmed round 5) |
| Config keys | `statusline.limits.{projection_min_elapsed, projected_bands, absolute_bands, windows}` (T-031..T-034) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.011 — refines (pace and absolute colour bands)
- BC-1.02.012 — composes with (countdown)
- BC-1.02.010 — depends on (expired windows unreported)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/limits.go (0.9 pace boundary) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-028 — boundary grid equality

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane, SL:515-521) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `elapsed is not None and 0.10 <= elapsed <= 1.0` (SL:517)
- **documentation**: SL:490-498 comment (owner redesign 2026-11-14; projection is noise in the first 10%)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config only |
| **Deterministic** | yes given `now` |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure (clock as input) |

#### Refactoring Notes

No refactoring needed; keep the expression literal and add a comment naming this contract at the site.
