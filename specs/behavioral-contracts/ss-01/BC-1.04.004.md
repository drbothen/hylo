---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md]
input-hash: "e4f8db5"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_telemetry (SL:693-702)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-043"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: ["2026-11-18 (v1.2.1) pass-4 remediation ADV-P4-C2-12 (metrics-borne SL:717 degrade named CP-N03 on invariant 3)", "2026-11-18 (v1.2.2) pass-7 remediation ADV-P7-C2-07 (dead-marker word sourced to statusline.pill.label_local per OD-189, glyph named glyphs.degraded) + ADV-P7-C2-14 BC side (CP-N03 canonical vector row added; the sole-key AttributeError raise type oracle-verified)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.004: Freshness ladder + stale suffix

## Description

`render_telemetry` picks the row-2 rung from `(sample, age, up)`: no sample → the dead
marker alone; failed latest fetch or an age beyond the freshness bound → the fields in
stale mode plus a dimmed `(~Ns old)` suffix; otherwise the fields in fresh mode. Notation:
`\e` is byte 0x1B; segments are joined by the separator `\e[2m · \e[0m` (BC-1.01.003).

## Preconditions

1. `(sample, age, up, hist)` come from BC-1.04.002.
2. `fresh_s` = `statusline.telemetry.fresh_s`, default 15 (T-003, derived: one metrics
   scrape interval; inert at the default TTL 4 and effective only when `ttl_s > 15`;
   OD-55, OD-57 E-0).
3. Colors come from `statusline.theme.*`; the dead-marker glyph ◌ is
   `statusline.glyphs.degraded` (U+25CC, SL:696) and the dead-marker WORD is
   `statusline.pill.label_local` (Text, default `DGX` — OD-189 extends OD-173's key
   reuse to the dead-backend marker, closing the P20 gap), so PC1's dead segment is
   `"\e[31m" + glyphs.degraded + " " + pill.label_local + " ?" + "\e[0m"` with every
   default byte-equal to legacy (OD-113, OD-02, OD-189).

## Postconditions

1. If `sample` is falsy (none or empty): segments = `["\e[31m◌ DGX ?\e[0m"]`.
2. Else if `not up` or `age > fresh_s`: segments = fields rendered with `stale=true`
   (BC-1.04.005..012), then, only if `age > 0`, one more segment
   `"\e[2m(~" + F(age, 0) + "s old)\e[0m"` where `F(x,0)` is Python `f"{x:.0f}"`
   (round-half-even on the binary value, BC-5.01.001).
3. Else: segments = fields rendered with `stale=false`.

## Invariants

1. `up=false` marks the row stale **immediately**, whatever the age (the 15 s bound
   applies only while `up` is true).
2. The dead rung never shows stale fields or a suffix.
3. Rendering never fails for a dict sample except via the named crash paths
   (BC-1.04.014, BC-1.04.015) plus the non-string-key site of BC-1.04.001 EC-013: a
   numeric sample key ahead of every `vllm:` key degrades in `serving_state` (SL:717;
   metrics-borne degrade, crash id **CP-N03**);
   after the session-cache write it returns as string `"5"` and no longer degrades.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `up=true`, age 15.0 | fresh (`> 15` false) |
| EC-002 | `up=true`, age 15.5 | stale, suffix `(~16s old)` |
| EC-003 | age 16.5 | `(~16s old)` (half-even) |
| EC-004 | `up=false`, age 0.0 | stale, **no** suffix (`age > 0` false) |
| EC-005 | `up=false`, age 299.9 | `(~300s old)` |
| EC-006 | `up=false`, age 302.0 (cached path, BC-1.04.002 EC-003) | `(~302s old)` |
| EC-007 | sample `{}` (foreign cache) | dead rung |
| EC-008 | age negative (clock step) with `up=false` | stale, no suffix |

## Canonical Test Vectors

Sample `{"up:vllm": 1.0}` unless noted; output = list of segments.

| Input | Expected Output | Category |
|-------|----------------|----------|
| age 2.0, up true | `["\e[32m◉\e[0m"]` | happy-path |
| age 4.0, up false | `["\e[33m◉\e[0m", "\e[2m(~4s old)\e[0m"]` | edge-case |
| age 15.5, up true | `["\e[33m◉\e[0m", "\e[2m(~16s old)\e[0m"]` | edge-case |
| sample none | `["\e[31m◌ DGX ?\e[0m"]` | error |
| `{5: 1.0}` (sole, numeric key), age 2.0, up true | degraded line (errDegraded, BC-1.01.001): `serving_state` raises AttributeError at SL:717 (`'int' object has no attribute 'startswith'`, oracle-verified CPython 3.11.7, 2026-11-18) — metrics-borne crash id **CP-N03**, sole-key case of BC-1.04.001 EC-013; a leading `"vllm:x"` key short-circuits `any()` and renders normally (BC-1.04.005 EC-007) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Rung selection is a total function of `(truthy(sample), up, age > fresh_s, age > 0)` matching legacy | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry (SL:693-702); STALE_OK (SL:79) |
| Legacy contract | BC-SL-043 (P3 base; r1 refined half-even suffix) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | OD-55 (health-dot doc fix: "green while the latest fetch succeeded; yellow from the first failed fetch"), OD-57 E-0, OD-113 |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.002 — depends on: supplies `(sample, age, up)`
- BC-1.04.005 — composes with: the dot color follows `stale`
- BC-5.01.001 — depends on: `.0f` formatting

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/row2.go (freshness ladder) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — ladder totality

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:693-702) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if not sample`, `if not up or age > STALE_OK`, `if age > 0` (SL:695-700)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed — suitable for table and property tests.
