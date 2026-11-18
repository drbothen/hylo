---
document_type: behavioral-contract
level: L3
version: "1.4.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md]
input-hash: "b8b756c"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-056"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.2 pass-3 remediation (ADV-P3-B07): Inv 3 justification reworded to OD-162's actual test (non-default behavior cannot be defined); 2026-11-18T02:00:00Z"
  - "1.3 pass-4 remediation (ADV-P4-B03): for-all grid-equality and blue-channel legs re-anchored to VP-041 (B01: this BC's default-only Inv 3 stands; the contradicting registry row is the architect's fix); 2026-11-18T03:00:00Z"
  - "1.4.1 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) — pass-4 stamp re-dated ascending (it predated pass-3's); no behavioral change"
  - "1.4.2 pass-7 remediation (ADV-P7-B12): history labels version-prefixed; no behavioral change; 2026-11-19T07:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.019: heat() HSV cell colours

> Byte notation used below: `\e` = ESC (0x1B). All other characters are literal UTF-8.

## Description

`heat(pct)` maps a percentage to a green → amber → red 24-bit colour used for the thermometer cells and the
thermometer number above 50% (BC-1.02.006). It clamps `pct` to 0..100, maps it to an HSV hue between 0.22 (green)
and 0 (red) at fixed saturation and value, converts with CPython's `colorsys.hsv_to_rgb` operation order, and
truncates each channel with `int(c * 255)`. The SGR form is `\e[38;2;R;G;Bm` (`truecolor`).

## Preconditions

1. `pct` is a Python int or float (bool counts as int).
2. Config `statusline.theme.heat` holds the legacy defaults: hue span 0.22, saturation 0.85, value 0.80 (T-030).

## Postconditions

1. `h = (1.0 - Min(Max(pct, 0.0), 100.0) / 100.0) * 0.22`, with `Max`/`Min` in the source argument order
   (`pyfmt.Max(a, b)` returns `b` only if `b > a`; design IM-09).
2. `(r, g, b) = hsv_to_rgb(h, 0.85, 0.80)` computed in CPython's order: `i = int(h*6.0)`, `f = (h*6.0) - i`,
   `p = v*(1.0-s)`, `q = v*(1.0-s*f)`, `t = v*(1.0-s*(1.0-f))`, `i % 6` selecting `(v,t,p)` for 0 and `(q,v,p)` for 1
   (h ≤ 0.22 keeps `i` in {0, 1}). Every product feeding `+`/`-` is wrapped in an explicit `float64(...)` so Go cannot
   fuse it (design IM-10, PR-15; `// pyfmt: no-fuse`).
3. Result = `(int(r*255), int(g*255), int(b*255))` (truncation toward zero, `pyfmt.Int`).
4. `truecolor(rgb)` = `\e[38;2;` + R + `;` + G + `;` + B + `m` (decimal, no padding).

## Invariants

1. Blue is always 30 for finite inputs (p = 0.80 × 0.15 = 0.12, 0.12 × 255 truncated).
2. Monotone hue: higher `pct` never gives a greener colour.
3. Default values come from `statusline.theme.heat` (T-030, owner group B: aesthetic judgment call). Valid range
   (Policy 20, OD-162): no non-default semantics is derivable from legacy for this key — the triple (hue span 0.22,
   saturation 0.85, value 0.80, SL:145-146) is baked and the sector guarantee in Postcondition 2 (`i` in {0, 1},
   i.e. h ≤ 0.22 < 1/3 for all pct) is stated only for the default triple — so per OD-162's test the valid range of
   `statusline.theme.heat` is the default triple only; any other value is a number-range config error
   (BC-2.02.003). Range for architect registration: theme.heat = {(0.22, 0.85, 0.80)}.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `pct > 100`, `+Infinity` | clamped: `(204,30,30)` |
| EC-002 | `pct < 0`, `-Infinity` | clamped: `(148,204,30)` |
| EC-003 | `pct = true` | treated as 1: `(150,204,30)` |
| EC-004 | `pct` = NaN | `Max(nan, 0.0)` keeps NaN; the ValueError ("cannot convert float NaN to integer") is raised inside `colorsys.hsv_to_rgb` at `i = int(h*6.0)` — before any channel multiplication, same outcome. Verified 2026-11-17 on CPython 3.11.7. Unreachable from `fmt_ctx`, because SL:426 raises first (CP-S06, BC-1.02.020) |
| EC-005 | FMA-capable target (arm64) | results identical to CPython; the table runs on the macos-15 arm64 runner, the only CI leg where fusion is detectable |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| cell centres `(i+0.5)*10`, i = 0..9 | `(159,204,30)` `(182,204,30)` `(204,202,30)` `(204,179,30)` `(204,156,30)` `(204,133,30)` `(204,110,30)` `(204,87,30)` `(204,64,30)` `(204,42,30)` | happy-path |
| `heat(5)` as SGR | `\e[38;2;159;204;30m` | happy-path |
| `heat(0)` | `(148,204,30)` | edge-case |
| `heat(50.4)` | `(204,144,30)` | edge-case |
| `heat(51)` | `(204,142,30)` | edge-case |
| `heat(84.5)` | `(204,66,30)` | edge-case |
| `heat(100)`, `heat(150)`, `heat(+inf)` | `(204,30,30)` | edge-case |
| `heat(-5)`, `heat(-inf)` | `(148,204,30)` | edge-case |
| `heat(true)` | `(150,204,30)` | edge-case |
| `heat(NaN)` | ValueError (Go: typed `ErrValue`; never reached from the thermometer) | error |

Pinned 2026-11-15 by calling the legacy `heat` under CPython 3.11 (oracle, OD-104); matches deep pass-3 round 1.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-041 | For all float64 `pct` in a dense grid over [-10, 110] the Go triple equals the CPython triple | generated table vs oracle (arm64; VP-028 retains the bounded golden vector table above) |
| VP-041 | Blue channel is 30 for all finite inputs | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/context.go`; BC-COMPONENT-MAP: internal/statusline/context.go (heat HSV; arm64) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:heat (SL:144-148) and legacy/dgx_statusline.py:truecolor (SL:140-141) |
| Legacy contract | BC-SL-056 (deep pass-3 round 1, new) |
| Config keys | `statusline.theme.heat` (T-030) |
| Parity | byte-exact (no exclusion entry) |

## Related BCs (Recommended)

- BC-1.02.006 — composes with (thermometer cells and number colour)
- BC-1.02.020 — related to (NaN crash happens before `heat`)
- BC-5.01.003 — depends on (`pyfmt.Max/Min/Int`)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/context.go (heat HSV; arm64) (FMA no-fuse convention) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-041 — grid equality vs CPython (for-all/differential); VP-028 — the pinned golden vector table above

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:140-148) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **type constraint**: CPython `colorsys.hsv_to_rgb` (standard library operation order)
- **documentation**: SL:145-146 comments (hue 0 red .. 0.22 green)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config only |
| **Deterministic** | yes |
| **Thread safety** | yes (pure) |
| **Overall classification** | pure |

#### Refactoring Notes

A private 12-line port of `colorsys.hsv_to_rgb` (design IM-21); no library HSV conversion.
