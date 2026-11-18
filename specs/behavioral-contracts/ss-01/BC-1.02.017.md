---
document_type: behavioral-contract
level: L3
version: "1.3.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/ubiquitous-language.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "7e9aa61"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-022"
parity_class: byte-exact
confidence: M
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.2 pass-3 remediation (ADV-P3-B17): EC-010 states the numeric precondition — the SL:559 OverflowError fires only when win_start is numeric; otherwise the huge exact timer text renders with no degrade; 2026-11-18T02:00:00Z"
  - "1.3 pass-4 remediation (ADV-P4-B05/B04/B07): Inv 3 self-contradiction removed (rendering carries no exclusion; acquisition and foreign-cache shapes do — OD-160); EC-004..006 and the -Infinity vector tagged OD-160 (hand-edited-cache shapes); EC-010 names CP-O05 with the exact threshold; canonical OV overflow vector added; DI-012 cited; 2026-11-18T03:00:00Z"
  - "1.3.1 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) — pass-4 stamp re-dated ascending (it predated pass-3's); no behavioral change"
  - "1.3.2 pass-6 remediation (ADV-P6-B08): the house glyph is named as the registry key statusline.glyphs.window_age instead of the wildcard statusline.glyphs.* (Config keys row); 2026-11-19T04:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.017: Window-age suffix (⌂) with its visibility gate

> Byte notation used below: `\e` = ESC (0x1B). All other characters are literal UTF-8.

## Description

Inside a shown timer segment, the process-age window (`⌂`, the age of the client process behind the status line,
which survives `/clear`) is appended when it exceeds the session's elapsed time by at least 5 minutes, that is after a
`/clear` or a resume. This contract is the gate and the placement; the duration text is BC-1.02.028, and how the
start time is acquired (native per-OS probe) is BC-3.02.001/002.

## Preconditions

1. The timer segment is shown (`cost.total_duration_ms` numeric and `> 60000`; BC-1.02.015); `dur` is that value.
2. `win_start` is the client process start time delivered by the window-start acquisition (BC-3.02.001), or
   `None` when stdin has no truthy `session_id` or the probe found nothing.
3. `now` is the single per-render clock value `Env.Now()` (design IM-14), the Python `time.time()` value
   `float64(t.UnixNano())/1e9`. The parity harness freezes it via `HYLO_TEST_NOW`.

## Postconditions

1. If `win_start` is a number (int or float, including a JSON-cached `true` = 1), compute
   `win_ms = (now - win_start) * 1000` and evaluate `win_ms - dur >= statusline.window_age.min_margin_ms`
   (default 300000, operator `>=`) with **no fused multiply-add**: the product is wrapped in an explicit
   `float64(...)` conversion and the site carries `// pyfmt: no-fuse` (design IM-10, pitfall PR-15).
2. When the gate passes, the bytes `\e[90m ⌂` + `wtxt` + `\e[0m` are appended to the timer segment after the API-time
   suffix (BC-1.02.016), where `wtxt` is the window-age text of BC-1.02.028.
3. When `win_start` is not numeric, or the gate fails (including NaN operands), nothing is appended.

## Invariants

1. The `⌂` suffix only appears inside a shown timer segment; a hidden timer hides it.
2. Order inside the timer segment is fixed: `⏱ <elapsed>`, then `·<api>`, then ` ⌂<age>`.
3. Rendering given a `win_start` value is byte-exact on every OS. The approved deviations for this widget live in
   acquisition, not here: **D4-EX-1** (on Windows legacy has no `ps`, so it never shows `⌂`, while Go's native probe can
   return a start) is excluded from the parity diff through the OD-105 exclusion-list entry `D4-EX-1` with dedicated
   tests `TestWindowAge_D4EX1_Windows*`; the macOS/Linux native-probe differences (true start in the repeated DST hour,
   `⌂` where legacy's localized `ps` fails) are the OD-76 entry named by OD-110, with their own table tests
   (BC-3.02.002). The rendering rules of this contract itself carry no exclusion; the foreign-cache shapes
   (EC-004..EC-007's hand-edited `proc_start`; ruling Q-b) carry exclusion id **OD-160**: vectors that rely on a
   hand-edited cache are Go table tests, not byte-parity obligations.
4. The 300000 default comes from `statusline.window_age.min_margin_ms` (register T-040: owner request, review row 9
   revisit, "otherwise it would repeat the elapsed figure").

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `win_ms - dur` exactly 300000 (now − start = 27000 s, dur = 26,700,000) | shown (`>=`) |
| EC-002 | now − start = 26999.9 s, dur = 26,700,000 | hidden |
| EC-003 | `win_start` in the future | `win_ms` negative → hidden |
| EC-004 | `win_start` = NaN (hand-edited-cache shape, **OD-160**: Go's encoder never emits NaN) | hidden (comparison false) |
| EC-005 | `win_start` = `+Infinity` (hand-edited-cache shape, **OD-160**) | `win_ms = -inf` → hidden |
| EC-006 | `win_start` = `-Infinity` (hand-edited-cache shape, **OD-160**) | `win_ms = +inf` passes the gate; `int(inf // 60000)` raises ValueError at SL:560 → 29-byte degraded line (BC-1.02.028 EC, BC-1.01.001) |
| EC-007 | `win_start` = `true` (only reachable through a hand-edited cache `proc_start`) | treated as epoch second 1; at now = 1794600000 renders `⌂20770d19h` |
| EC-008 | stdin has no `session_id` | acquisition is skipped (SL:1229), `win_start = None` → no suffix |
| EC-009 | FMA contraction of `(now - win_start)*1000 - dur` | forbidden; tests for this site run on arm64 (macos-15 runner), where fusion is detectable (design IM-10) |
| EC-010 | `dur` (`cost.total_duration_ms`) a JSON integer at or beyond the int→float conversion threshold \|n\| ≥ 2**1024 − 2**970 (oracle-verified 2026-11-17), e.g. 10³⁰⁹, **with `win_start` numeric** (the SL:559 subtraction is reached) | `win_ms - dur` raises OverflowError at SL:559 (mixed float/int arithmetic converts the int; taxonomy **CP-O05**). With a *non-numeric* `win_start` the gate block is skipped and legacy renders the exact huge `_hm(10**309)` timer text (integer arithmetic only) with no degrade — PC1's "timer shown" plus numeric `win_start` is what reaches the crash site |

## Canonical Test Vectors

now = 1794600000.0; stdin `{"cost": {...}}`; `win_start = now - (now−start)`; shown is the exact timer segment.

| Input | Expected Output | Category |
|-------|----------------|----------|
| now−start 112000 s, dur 26,700,000 | `\e[90m⏱ 7h25m\e[0m\e[90m ⌂1d07h\e[0m` | happy-path |
| now−start 27000 s, dur 26,700,000, api 60000 | `\e[90m⏱ 7h25m\e[0m\e[2m·1m\e[0m\e[90m ⌂7h30m\e[0m` | happy-path (order) |
| now−start 27000 s, dur 26,700,000 | `\e[90m⏱ 7h25m\e[0m\e[90m ⌂7h30m\e[0m` | edge-case (boundary, shown) |
| now−start 26999.9 s, dur 26,700,000 | `\e[90m⏱ 7h25m\e[0m` | edge-case (hidden) |
| win_start = now + 1000, dur 120000 | `\e[90m⏱ 2m\e[0m` | edge-case |
| win_start = NaN, dur 120000 | `\e[90m⏱ 2m\e[0m` | edge-case |
| win_start = -Infinity, dur 60001 | whole stdout = `\e[90mstatusline degraded\e[0m\n` (hand-edited-cache shape, **OD-160**) | error |
| dur = OV (`2**1024 − 2**970` = 179769313486231580793728971405303415079934132710037826936173778980444968292764750946649017977587207096330286416692887910946555547851940402630657488671505820681908902000708383676273854845817711531764475730270069855571366959622842914819860834936475292719074168444365510704342711559699508093042880177904174497792, the smallest positive integer that fails float conversion), win_start numeric | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 (`win_ms - dur` OverflowError at SL:559; CP-O05, EC-010) | error |

Pinned 2026-11-15 with the legacy `render_lane` under CPython 3.11 (oracle, OD-104); the 112000 s vector is also
confirmed by golden A (deep pass-3 round 2).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | Suffix present iff `win_start` numeric, timer shown and `(now-win_start)*1000 - dur >= 300000` evaluated without FMA | table test on arm64 + 300k sampled boundary cases vs oracle |
| VP-028 | Suffix position is after the API-time suffix | table test |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Architecture Module | `internal/statusline` (design §8 home `sl/session.go`; BC-COMPONENT-MAP: internal/statusline/session.go (⌂ gate) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:render_lane (SL:554-563; gate SL:557-559, append SL:562) |
| Legacy contract | BC-SL-022 (pass-3 r1; refined deep pass-3 round 1) |
| Config keys | `statusline.window_age.min_margin_ms` (T-040), `statusline.glyphs.window_age` (`⌂`), `statusline.theme.*` (OD-113) |
| Parity | byte-exact for rendering; acquisition deviations D4-EX-1 / OD-76 owned by BC-3.02.001/002 |

## Related BCs (Recommended)

- BC-1.02.028 — composes with (window-age text)
- BC-1.02.016 — composes with (precedes this suffix)
- BC-1.02.015 — depends on (timer shown)
- BC-3.02.001 — depends on (window start acquisition, D4-EX-1)
- BC-3.02.002 — related to (OD-76 edge differences)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/session.go (⌂ gate) (row-1 session widgets; FMA no-fuse convention) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-028 — gate without FMA

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (render_lane, SL:554-563) |
| **Confidence** | medium (FMA gate and float floor division; 0 diffs in 300k sampled boundary cases, guard kept) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(win_start, (int, float))` (SL:557), `win_ms - dur >= 300000` (SL:559)
- **documentation**: SL:554-556 comment (process age, survives `/clear`, 5 min margin)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (clock injected) |
| **Global state access** | none |
| **Deterministic** | yes given `Env.Now` |
| **Thread safety** | unknown (single-threaded render) |
| **Overall classification** | pure (clock as input) |

#### Refactoring Notes

Legacy reads `time.time()` again at SL:558; Go reads the clock once per render (IM-14), output-neutral under a
frozen clock.
