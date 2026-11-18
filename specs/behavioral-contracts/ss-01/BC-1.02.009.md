---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "038ee14"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:444-445, 487-489)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-014
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.2 pass-5 remediation (ADV-P5-B09 disposition, OD-179): the reroute-all markers become the List key statusline.lane.reroute_all_prefixes (default [\"claude\", \"claude-\"], legacy; entries non-empty, no control bytes); PC1, Config keys, Owner decisions and Refactoring Notes aligned; 2026-11-18T05:42:56Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.009: Limits segment hidden on reroute-all prefixes

## Description

When the configured model prefixes reroute every Claude model to the backend — any prefix
that, after removing trailing `*` characters, equals `claude` or `claude-` — no request can
consume the subscription plan, so the plan-window (limits) widget is suppressed entirely,
whatever `rate_limits` stdin or the smoothing cache carries.

## Preconditions

1. `prefixes` is the parsed list of BC-1.02.001 Precondition 4 (split on `,`, Python
   whitespace stripped, empties dropped) from `backends[0].model_prefixes`.
2. `d.rate_limits` has already been replaced by the smoothed value (BC-1.02.013).

## Postconditions

1. `reroute_all = any(RStrip(p, "*") in reroute_all_prefixes for p in prefixes)` where
   `reroute_all_prefixes` is the configured List key `statusline.lane.reroute_all_prefixes` (OD-179; default
   `["claude", "claude-"]`, equal to the legacy literals; range: every entry non-empty, no control bytes)
   (only `*` is stripped, only from the right; comparison is exact and case-sensitive).
2. If `reroute_all` → the limits input is the empty mapping: no limits segment is
   emitted (BC-1.02.010/011/012 never produce output).
3. Otherwise the limits input is `d.rate_limits` if truthy, else `{}`, and rendering
   continues per BC-1.02.010..012.
4. Nothing else in row 1 changes: the pill still follows BC-1.02.001 (so `claude*` gives
   the ANTH pill while limits are hidden — legacy inconsistency kept for parity).

## Invariants

1. Suppression is decided from configuration only, never from stdin.
2. The smoothing side effect (BC-1.02.013 cache write) still happens in `main` before
   rendering; reroute-all affects display only.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | prefix `claude` | hidden |
| EC-002 | `claude*`, `claude-*`, `claude-**` | hidden |
| EC-003 | `claude-s`, `claude-sonnet` | shown |
| EC-004 | `Claude` (case) | shown |
| EC-005 | mixed list `claude-sonnet,claude` | hidden (any) |
| EC-006 | `"  claude  "` | whitespace stripped by list parsing → hidden |
| EC-007 | empty prefix list | shown (no prefix qualifies) |
| EC-008 | `*claude` / `claude*x` | shown (only trailing `*` removed) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15, `T = 1800000000.0`, stdin
`{"model":{"id":"claude-opus-5"},"rate_limits":{"seven_day":{"used_percentage":44,"resets_at":T+15480}}}`.
`S` = `\e[90m7d44%\e[0m \e[90m->4h18m\e[0m` (`\e` = 0x1B).

| Input (prefix value) | Expected limits segment | Category |
|-------|----------------|----------|
| `claude-sonnet` | `S` | happy-path |
| `claude` | none | happy-path |
| `claude*` | none | edge-case |
| `claude-*` | none | edge-case |
| `claude-**` | none | edge-case |
| `claude-s` | `S` | edge-case |
| `Claude` | `S` | edge-case |
| `claude-sonnet,claude` | none | edge-case |
| `""` (explicit empty) | `S` | edge-case |
| `"  claude  "` | none | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | `reroute_all(prefixes)` equals the oracle for all prefixes built from `{claude, claude-, Claude, claude-s, *, space, NBSP}` up to length 3 | exhaustive table test |
| VP-028 | When `reroute_all`, row 1 contains no limits segment for any stdin | property test |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane (SL:444-445 prefix list; SL:487-489 reroute_all) |
| Legacy contract | BC-SL-014 |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-111 / OD-123 (prefix key under `backends[0]`, default `claude-sonnet`), OD-179 (reroute-all markers are the List key `statusline.lane.reroute_all_prefixes`) |
| Config keys | `backends[0].model_prefixes`, `statusline.lane.reroute_all_prefixes` (OD-179; List of Text, default `["claude", "claude-"]`, legacy; every entry non-empty, no control bytes) |
| Architecture Module | `internal/statusline/limits.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.001 — related to (same prefix list, different match rule)
- BC-1.02.010 / BC-1.02.011 / BC-1.02.012 — composes with (gated widget)
- BC-1.02.013 — related to (smoothing still runs)
- BC-2.01.002 — depends on (prefix key)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#limits` — internal/statusline/limits.go (reroute-all hides limits) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — plan-window widget story

## VP Anchors (Recommended)

- VP-028 — reroute-all predicate

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`render_lane`, SL:487-489; comment SL:481-486) |
| **Confidence** | high (design §8 H; pass-3 broad row MEDIUM, raised by r1 vectors) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `rl = {} if reroute_all else ...` (SL:489)
- **documentation**: comment SL:484-486

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | n.a. |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. The reroute-all markers are resolved config: the List key
`statusline.lane.reroute_all_prefixes` (OD-179, default `["claude", "claude-"]`, legacy); the render takes the
parsed list from `internal/config` (D15), falling back to nothing hard-coded.
