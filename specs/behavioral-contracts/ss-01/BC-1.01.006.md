---
document_type: behavioral-contract
level: L3
version: "1.3.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "05fa0e0"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-054"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.3.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet rows replaced with VP-040 P5/P6"
  - "1.3.2 2026-11-18T04:00:00Z: pass-3 remediation (ADV-P3-B03): VP anchor names VP-040 P5/P6 instead of VP-027"
  - "1.3.3 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) \u2014 pass-3 stamp re-dated ascending (it predated the preceding 1.3.1 reconciliation entry); no behavioral change"
  - "1.3.4 pass-11 remediation (ADV-P11-B05): Inv 1 widened \u2014 the prefix-of-segments reading is defeated not only by stdin text containing SEP but by a configured separator whose bytes occur inside built-in segment markup (theme.separator=/ makes SEP equal the lines segment's dim slash, SL:537; [/] collide with the tokens segment's dim brackets, SL:596), which is also where VP-040 P5's generator assumption fails; no behavioral change; 2026-11-21T12:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.01.006: trim_to_fit double-resets; single reset on the recycle row

> Byte notation: `\e` = ESC (0x1B). "Recycle row" = a row whose kept last segment is the cache-hit segment
> `\e[36m♻\e[0m NN%` (BC-1.02 cache-hit widget), which does not end in a reset.

## Description

When `cols > 0`, each row is trimmed by repeatedly dropping its last `SEP`-delimited segment and appending one
`RESET`, until its visible width (BC-1.01.004) fits or no `SEP` remains. Because most segments already end in
`\e[0m`, a trimmed row usually ends in a double reset `\e[0m\e[0m`; a row trimmed back to the ♻ segment ends in a
single `\e[0m`. A row with no `SEP` is returned unchanged even if it is too wide.

## Preconditions

1. `cols > 0` (trim is skipped entirely for `cols <= 0`, BC-1.01.007 / BC-1.01.005).
2. `row` is a fully rendered row (`SEP.join(segments)`), `SEP` = `\e[2m · \e[0m`, `RESET` = `\e[0m` (theme defaults,
   OD-113).

## Postconditions

1. Loop: while `visible(row) > cols` AND `SEP` occurs in `row`: `row = row.rsplit(SEP, 1)[0] + RESET`.
2. Each iteration appends exactly one `RESET` and removes everything from the last `SEP` occurrence onward
   (including any `RESET`s appended by previous iterations, which sit after that `SEP`). Net effect: the result is
   the kept prefix of segments followed by exactly one appended `RESET`.
3. A kept last segment ending in `\e[0m` -> row ends `\e[0m\e[0m`; the ♻ segment (`\e[36m♻\e[0m 94%`) -> row ends
   `94%\e[0m`.
4. An untrimmed row (already fits) is returned byte-identical; an untrimmed row whose last segment is ♻ ends with
   **no** reset.
5. When only the first segment remains it is kept even if wider than `cols` (e.g. the pill alone).

## Invariants

1. The function is pure; the output is always a prefix of the input's segments plus at most one `RESET` — provided no
   segment text contains the exact `SEP` byte string. Two sources defeat the proviso: (a) stdin text (model display
   name, project label; BC-1.01.004 PC3) can contain `SEP` verbatim; (b) the configured separator itself —
   `statusline.theme.separator` is free text (no control bytes) — can make a **built-in** segment's own markup
   contain `SEP`: a configured `/` makes `SEP` = `\e[2m/\e[0m`, the dim slash the lines segment embeds between its
   counts (SL:537), and a configured `[` or `]` collides with the tokens segment's dim brackets (SL:596). In either
   case `rsplit` cuts inside a segment, the "prefix of segments" reading no longer holds, and the VP-040 P5
   generator's no-SEP assumption fails for such rows (the trimming behavior itself is pinned by Postcondition 1
   either way; legacy SL:1196).
2. The `rsplit` is on the exact `SEP` byte string (code-point semantics, `pyfmt.RSplit1`); a `·` that is not part of
   `SEP` is not a split point.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Row fits (`visible <= cols`) | unchanged |
| EC-002 | Row has no SEP and is wider than cols (`"x"*50`, cols 10) | unchanged (50 x's) |
| EC-003 | Trim stops on the ♻ segment | single trailing `\e[0m` |
| EC-004 | cols smaller than the first segment | first segment + `\e[0m`, wider than cols |

## Canonical Test Vectors

Row X (visible 40) = `\e[106;30;1m ◨ DGX \e[0m` SEP `\e[97mSonnet 5.5\e[0m` SEP `\e[90m⎇ main\e[0m` SEP `\e[90mhome-lab\e[0m`.

| Input | Expected Output | Category |
|-------|----------------|----------|
| X, cols 40 | X unchanged (width 40) | happy-path |
| X, cols 30 | `\e[106;30;1m ◨ DGX \e[0m\e[2m · \e[0m\e[97mSonnet 5.5\e[0m\e[2m · \e[0m\e[90m⎇ main\e[0m\e[0m` (width 29) | happy-path |
| X, cols 25 | `\e[106;30;1m ◨ DGX \e[0m\e[2m · \e[0m\e[97mSonnet 5.5\e[0m\e[0m` (width 20) | edge-case |
| X, cols 18 or 5 | `\e[106;30;1m ◨ DGX \e[0m\e[0m` (width 7) | edge-case |
| `\e[106;30;1m ◨ DGX \e[0m` SEP `\e[36m♻\e[0m 94%` SEP `\e[90mxxxxxxxxxx\e[0m`, cols 15 | `\e[106;30;1m ◨ DGX \e[0m\e[2m · \e[0m\e[36m♻\e[0m 94%\e[0m` (width 15, single reset) | edge-case |
| `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`, cols 10 | unchanged | error |
| stdin `{}`, ROWS 1, COLUMNS 5 (end-to-end) | stdout `\e[100;37;1m ◨ ? \e[0m\e[0m\n` | edge-case |

All verified 2026-11-15 under CPython 3.11.7 (direct `trim_to_fit` calls and one end-to-end run).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-040 | P5: output = (max-prefix of segments joined by SEP) + (RESET iff at least one segment dropped), for generated rows whose segment text excludes the exact SEP bytes | property-test (testing/quick; generator excludes SEP-containing segment text) |
| VP-040 | P6: after trim, `visible(out) <= cols` or out contains no SEP | property-test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | — |
| Architecture Module | `internal/statusline` width (`width.go`) (BC-COMPONENT-MAP: internal/statusline/width.go (trim_to_fit double reset) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`trim_to_fit` (SL:1193-1197); applied in `main` SL:1232-1233; ♻ segment shape SL:479 |
| Legacy contract | BC-SL-054 (new in P3r1 §A1; refined P3r2 §1 single reset at ♻; index P3r4 §7.3) |
| Decisions | D4; OD-113 (SEP/RESET from theme keys) |

## Related BCs (Recommended)

- BC-1.01.004 — depends on (visible width)
- BC-1.01.010 — composes with (breakpoint matrix over goldens)
- BC-1.01.003 — composes with (trim after row decision)
- BC-5.03.002 — depends on (`pyfmt.RSplit1`)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-width` — internal/statusline/width.go (trim_to_fit double reset) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — status line frame (design step S2)

## VP Anchors (Recommended)

- VP-040 P5/P6 — trim structure (max-prefix + conditional RESET) and boundedness (ADV-P3-B03; VP-027 retains
  the breakpoint matrix)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1193-1197) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `while visible(row) > cols and SEP in row`
- **assertion**: pinned calls 2026-11-15; P3r1/P3r2 `trim.py`

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads SEP/RESET (config) |
| **Deterministic** | yes |
| **Thread safety** | pure |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; pass SEP/RESET in from the resolved theme.
