---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T21:30:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - ../semport/hylo-legacy/statusline-target-design.md
  - ../semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces Python max(list) used at legacy/dgx_statusline.py SL:671)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: new
parity_class: "n.a."
confidence: "—"
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

# Behavioral Contract BC-5.01.006: pyfmt.MaxSeq: Python max() over a sequence with first-maximal-wins NaN order

## Description

`pyfmt.MaxSeq(vals ...Num) Num` (num.go) reproduces Python `max(list)` for the seed-list
sites (SL:671 `max(max(vals), floor)`, feeding the sparkline cell ceiling; pitfall PR-04):
it keeps the earlier element unless the later one compares greater, which is observable
exactly when a NaN is present. Helper-level contract per OD-141. The pairwise `Max`/`Min`
are pinned in BC-5.01.003; this contract covers the sequence form.

## Preconditions

1. `vals` is the sequence in file order (SL:671: the per-cell kept values).
2. Elements are `Num`s (int64 / `*big.Int` / float64 / bool-as-int, design §2.6 num.go).

## Postconditions

1. Empty sequence → typed `ErrValue` (Python `ValueError: max() arg is an empty sequence`),
   mapped to `errDegraded` at the consuming site (design IM-15).
2. Otherwise the result is `vals[0]`, replaced by `vals[i]` only when `vals[i] > current`
   (Python's first-maximal-wins order). Consequence for NaN: an earlier NaN can only be
   displaced by a later element that compares greater — a NaN never compares greater, so a
   NaN at position 0 wins over any later NaN and over later finites until a finite
   `b > a` displacement occurs exactly as Python decides it (pinned table).
3. Same comparison semantics as `pyfmt.Max` applied left-fold, but always in Python's
   argument order (never the builtin `max`/`math.Max`, design IM-09).

## Invariants

1. Pure; no NaN-normalization: NaN propagates per Python's order, never filtered.
2. The left-fold with `Max` yields the same result — one shared comparison primitive, no
   drift (PR-04 test obligation shared with BC-5.01.003).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `MaxSeq()` empty | `ErrValue` → `errDegraded` at the site |
| EC-002 | `MaxSeq(nan, 1, 2)` | `nan` (position 0; `1 > nan` false forever) |
| EC-003 | `MaxSeq(1, nan, 2)` | `nan` (displaced 1; `2 > nan` false) |
| EC-004 | `MaxSeq(1, 2, nan)` | `nan` (NaN last compares-not-greater, stays; result is NaN) |
| EC-005 | `MaxSeq(2, 1, 3)` | `3` |
| EC-006 | `MaxSeq(true, 1)` | `1` (bool counts as int; tie keeps the first) |
| EC-007 | `MaxSeq(nan, nan)` | first `nan` (identity of the winner is positional) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `MaxSeq(1, 2, 3)` | `3` | happy-path |
| `MaxSeq(nan, 1, 2)` | `nan` | edge-case |
| `MaxSeq(1, nan, 2)` | `nan` | edge-case |
| `MaxSeq()` | typed `ErrValue` | error |

Expectations generated from CPython 3.11 `max()` semantics (OD-104 oracle discipline;
pitfall PR-04 test grid).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-023 | MaxSeq equals CPython `max(list)` for the PR-04 grid (NaN in every position, int/float/bool mixes) | CPython oracle table |
| VP-023 | MaxSeq fold equals chained Max for every permutation | proptest |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-09, pitfall PR-04; consumer SL:671 (sparkline ceiling via BC-1.04.009) |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| L2 Domain Invariants | DI-012 (byte parity machinery) |
| Architecture Module | `internal/pyfmt` num.go (BC-COMPONENT-MAP: internal/pyfmt/num.go (MaxSeq) — ARCH-06) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.01.003 — composes with (Max/Min pairwise primitive)
- BC-1.04.009 — consumer (sparkline cell ceiling)
- BC-1.04.014 — related to (NaN crash paths downstream)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#num` — internal/pyfmt/num.go (MaxSeq) (num.go helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

S-TBD — pyfmt num helpers

## VP Anchors (Recommended)

- VP-023 — PR-04 grid equality

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | Send + Sync (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/num.go (MaxSeq)` (BC-COMPONENT-MAP: py/num.go (MaxSeq) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
