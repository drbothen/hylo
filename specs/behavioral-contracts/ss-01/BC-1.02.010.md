---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "5ecc7b2"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:499-514)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-015
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["1.2 pass-6 remediation (ADV-P6-B01, call 10): for-all window-shown row re-anchored from VP-028 to VP-041 (VP-028 keeps the sequence golden leg); 2026-11-19T04:00:00Z"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.010: Expired rate-limit window is unreported

## Description

Each plan window (5h, 7d) is reported only while its data is current. A window whose
numeric `resets_at` is at or before now is treated exactly like a window the client never
sent: it is hidden. This applies equally to fresh stdin values and to values replayed from
the 30-minute smoothing cache. When no window remains reported, the whole limits widget is
omitted.

Notation: `\e` is the byte 0x1B; `T = 1800000000.0` is the injected clock.

## Preconditions

1. Reroute-all is false (BC-1.02.009); `rl` = the smoothed `d.rate_limits` (BC-1.02.013)
   if truthy, else `{}`.
2. `now` = the render's clock read.
3. Windows, in order: (`5h`, key `five_hour`, length 18000 s), (`7d`, key `seven_day`,
   length 604800 s) — `statusline.limits.windows`.

## Postconditions

1. For each window: `w = rl[key]` if truthy, else `{}`; `pct = w.used_percentage`;
   `reset = w.resets_at`.
2. If `reset` is a number (Python `int`/`float`, booleans included) and `reset <= now` →
   `pct = None` (unreported).
3. A window is **reported** iff `pct` is then a number; its stored pct is
   `Min(Max(pct, 0.0), 100.0)` and its stored reset is `reset` if numeric, else None.
4. If no window is reported → no limits segment at all.
5. Otherwise only reported windows render (BC-1.02.011, BC-1.02.012); unreported ones
   contribute nothing (no placeholder, no extra separator).

## Invariants

1. A window is never shown with a reset time in the past.
2. Expiry is evaluated at render time, so a cached window disappears at its reset even
   while the smoothing cache is still fresh (review #12.1).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `resets_at == now` | unreported (`<=`) |
| EC-002 | `resets_at = now + 0.5` | reported; countdown `->0m` |
| EC-003 | 5h expired, 7d live | only 7d shown, no leading separator |
| EC-004 | only window expired | widget omitted |
| EC-005 | `resets_at` non-numeric (`"2026"`) | not an expiry: window reported, no countdown, absolute bands |
| EC-006 | `resets_at` `true` | number 1 ≤ now → unreported |
| EC-007 | `used_percentage` string / missing | unreported |
| EC-008 | window value `[]` or `0` | falsy → `{}` → unreported |
| EC-009 | window value truthy non-object (e.g. `"x"`, `[1]`) | CP-S09 AttributeError → guard line; sticky through the cache — BC-1.02.030 |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15; prefixes `claude-sonnet`.

| Input (`rate_limits`) | Expected limits segment | Category |
|-------|----------------|----------|
| `{"seven_day":{"used_percentage":44,"resets_at":T+60}}` | `\e[90m7d44%\e[0m \e[90m->1m\e[0m` | happy-path |
| `{"seven_day":{"used_percentage":44,"resets_at":T-1}}` | none | happy-path |
| `{"seven_day":{"used_percentage":44,"resets_at":T}}` | none | edge-case |
| `{"seven_day":{"used_percentage":44,"resets_at":T+0.5}}` | `\e[90m7d44%\e[0m \e[90m->0m\e[0m` | edge-case |
| `{"five_hour":{"used_percentage":31,"resets_at":T},"seven_day":{"used_percentage":44,"resets_at":T+15480}}` | `\e[90m7d44%\e[0m \e[90m->4h18m\e[0m` | edge-case |
| `{"five_hour":{"used_percentage":31,"resets_at":T-5}}` | none | edge-case |
| `{"seven_day":{"used_percentage":44,"resets_at":"2026"}}` | `\e[90m7d44%\e[0m` | edge-case |
| `{"seven_day":{"used_percentage":44,"resets_at":true}}` | none | edge-case |
| `{"seven_day":[]}` | none | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-041 | For numeric reset, window shown ⇒ `reset > now` — for all renders | property test (for-all leg; VP-028 delivers the oracle legs) |
| VP-028 | Smoothed window disappears at its reset during a stdin-sequence replay (cache fresh, reset passed) | parity harness sequence (BC-6.02.002) — golden leg |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane (SL:499-514; expiry SL:505-507) |
| Legacy contract | BC-SL-015 |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | owner 2026-11-14 redesign (review #12 revisit: unreported windows hidden), recorded in SL:490-498 |
| Config keys | `statusline.limits.windows` (5 h / 7 d; convention: Anthropic window definitions, T-031) |
| Architecture Module | `internal/statusline/limits.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.013 — depends on (smoothed input)
- BC-1.02.011 — composes with (rendering of reported windows)
- BC-1.02.012 — composes with (countdown)
- BC-1.02.030 — related to (CP-S09 sticky crash)
- BC-1.02.009 — depends on (reroute-all gate)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#limits` — internal/statusline/limits.go (expired window unreported) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — plan-window widget story

## VP Anchors (Recommended)

- VP-041 — no-past-reset for-all property (VP-028 retains the sequence golden leg)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`render_lane`, SL:499-514) |
| **Confidence** | high (pass-3 HIGH-R #12.1) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(reset, (int, float)) and reset <= now_rl` (SL:506)
- **documentation**: comment SL:505

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads clock (injected) |
| **Deterministic** | yes under the injected clock |
| **Thread safety** | n.a. |
| **Overall classification** | pure (given `now`) |

#### Refactoring Notes

Pass `now` in (design IM-14); no other change.
