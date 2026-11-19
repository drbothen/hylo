---
document_type: behavioral-contract
level: L3
version: "1.2.3"
status: draft
producer: product-owner
timestamp: 2026-11-19T17:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md, owner-decisions-log-2026-11-14.md]
input-hash: "9e29fea"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces Python len()/slicing and the strict UTF-8 print check of legacy/dgx_statusline.py)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.2.1 2026-11-19T17:00:00Z: ADV-P7 remediation D21 — Inv 1's go-runewidth/East-Asian-width ban restricted to the RENDER PATH; the OD-170 EA-width table function is registry range-validation only (pill-label 1..16 bound, OD-173/OD-184), consulted at config-load time, never while rendering"
  - "2026-11-25T00:00:00Z (1.2.2): ADV-P14 remediation D01 (orchestrator call 5) — Inv 1's validation-only ban scope extends to the nine width-bounded statusline.labels.* members (OD-194) beside the pill-label bound"
  - "2026-11-25T00:00:00Z (1.2.3): pass-14 sync closure (orchestrator call 5) — Inv 1's live parenthetical spells the pill-label 1..16 display-width bound as covering the three `pill.label_*` keys (OD-173/OD-184, pass-7 D21) and extends the OD-170 width-check scope to the nine width-bounded statusline.labels.* members (old, rate, queue, kv, host, tps, max, idle, na; OD-194), matching BC-2.01.004/BC-2.01.005 PC-6; no behavioral change"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.03.001: Len/Truncate/HasSurrogate: code points, surrogate = 1, not terminal cells

## Description

Legacy measures and cuts strings with Python `len()` and slicing, which count **code points** (a lone surrogate
counts 1; a combining mark counts 1; a CJK or emoji character counts 1), never terminal cells and never bytes.
`pyfmt.Len`, `pyfmt.Truncate` and `pyfmt.HasSurrogate` reproduce this over the Value string model (BC-5.02.004);
`HasSurrogate` is the check that stands in for Python's strict UTF-8 print failure (design IM-11, IM-22).

## Preconditions

1. `s` is a Value string (code points, lone surrogates allowed, BC-5.02.004) or a Go string built by the renderer.
2. `Truncate(s, n)` takes `n >= 0`.

## Postconditions

1. `Len(s)` = number of code points; each surrogate code point (U+D800-U+DFFF) counts exactly 1.
2. `Truncate(s, n)` = the first `min(n, Len(s))` code points (Python `s[:n]`); never splits a code point's encoding;
   `Truncate(s, n)` with `n >= Len(s)` returns `s` unchanged.
3. `HasSurrogate(s)` is true iff `s` contains at least one surrogate code point.
4. All three are pure.

## Invariants

1. `go-runewidth` or any East-Asian-width logic is never used IN THE RENDER PATH (legacy
   counts code points there, research P12). The ban does NOT cover the registry's
   range-validation side: the OD-170 East-Asian-Width table function exists solely for
   registry range VALIDATION (the pill-label 1..16 display-width bound on the three
   `pill.label_*` keys, OD-173/OD-184, pass-7 D21, and the nine width-bounded
   `statusline.labels.*` members — old, rate, queue, kv, host, tps, max, idle, na —
   OD-194, per BC-2.01.004/BC-2.01.005 PC-6), consulted only at config-load time, never
   while rendering.
2. `len()` of a Go string (bytes) and `utf8.RuneCountInString` over WTF-8 surrogates (which counts 3 invalid bytes
   as 3 runes) are never used for these measures.
3. Uses served (IM-11, PR-11): `visible()` width after SGR strip (SL:153), composition `len(content)`/`len(inner)`/
   `len(text)`/`len(thinking)` (SL:1122, 1133, 1143, 1145), the 40-code-point sid cut (SL:1017) and the 7-char
   branch cut (SL:389). Before the single stdout write the renderer calls `HasSurrogate` on every string that reaches
   output; true → degraded (CP-S17, BC-1.01.008).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `Len("😀")` | 1 |
| EC-002 | `Len(lone U+D800)` | 1 |
| EC-003 | `Len("e\u0301")` (e + combining acute U+0301, escape notation; the precomposed é would be 1) | 2 |
| EC-004 | `Len("中")` | 1 (not 2 cells) |
| EC-005 | Raw-byte surrogate pair (two code points, BC-5.02.004 EC-003) | `Len` 2; `HasSurrogate` true |
| EC-006 | `Truncate("😀x", 1)` | `"😀"` |
| EC-007 | `Truncate(s, 0)` | `""` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `Len("abc")`; `Len("café")` | 3; 4 | happy-path |
| `Truncate("a" × 45, 40)` | `"a" × 40` | happy-path |
| `Len("\ud800x")` (escape-decoded) | 2 | edge-case |
| `HasSurrogate("ok")`; `HasSurrogate("\ud800")` | false; true | edge-case |
| `HasSurrogate` true on a rendered label | renderer returns degraded (29-byte line) | error |

Verified 2026-11-15 against CPython 3.11.7 (`len`, slicing, strict UTF-8 `print` raising `UnicodeEncodeError`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-025 | `Len(Truncate(s, n)) == min(n, Len(s))` | Go property test (testing/quick) |
| VP-025 | `Len` equals the oracle `len()` on fuzzed decoded strings | fuzz + oracle |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (surrogate → degraded, never a crash), DI-012 |
| Architecture Module | `internal/pyfmt/str.go` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/str.go (Len/Truncate/HasSurrogate) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103; design IM-11, IM-22; pitfalls PR-11, PR-17. Legacy uses served: SL:153, 389, 1017, 1122, 1133, 1143, 1145, 1234 |

## Related BCs (Recommended)

- BC-1.01.004 — consumed by (visible width counts code points)
- BC-1.01.008 — consumed by (strict UTF-8 output; surrogate degrades)
- BC-1.03.009, BC-1.03.014 — consumed by (composition lengths)
- BC-5.02.004 — depends on (string model)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-str` — internal/pyfmt/str.go (Len/Truncate/HasSurrogate) (code-point string helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt str (design step S1)

## VP Anchors (Recommended)

- VP-025 — truncate/length consistency

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/str.go (Len/Truncate/HasSurrogate)` (BC-COMPONENT-MAP: py/str.go (Len/Truncate/HasSurrogate) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
