---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "6a5b563"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1041-1058)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-066"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C11) — Pre3 added: len(G) > step (the PC2 extension claim presupposes the first step of refresh 2 ends inside G)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.012: Short + long line completes over two refreshes

## Description

Because long-line completion runs only when the first read step contains **no** LF (BC-1.03.003), a short
complete line followed by a line longer than the step is parsed in two refreshes: refresh 1 advances only past
the short line; refresh 2 starts at the long line, whose first step has no LF, so the extension reads complete it
(together with any lines after it inside the extended blob).

## Preconditions

1. Transcript bytes from `off`: a complete line `S` (with LF) of length < step, then a line `G` whose length plus
   `len(S)` exceeds the step (default 524,288 B), so the first step ends inside `G`.
2. No mix-cache reset applies between the refreshes.
3. `len(G) > step` (ADV-P6-C11): the extension-read claim in PC2 presupposes the first step of refresh 2 ends
   inside `G`, which holds only when `G` alone exceeds the step. With `len(G) ≤ step` the PC1 inequality can still
   hold (via a large `S`), but no extension happens and the outcome differs from the PC2 assertion; the
   two-refresh-shape claims below apply only under this precondition.

## Postconditions

1. Refresh 1: the first step contains `S`'s LF → no extension; `cut` = end of `S`; cache `size` = `off + len(S)`;
   only `S` is counted.
2. Refresh 2: the first step from the new offset lies inside `G` with no LF → extension reads until `G`'s LF (or
   EOF); `G` is parsed; the cache `size` advances past `G` (and past any further complete lines in the blob).
3. Between the refreshes the rendered composition reflects only `S`.

## Invariants

1. No refresh ever splits `G`: it is parsed whole or not at all.
2. The two-refresh latency is legacy behavior and is reproduced, not optimized (D4 parity first).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `G` is last and has no LF yet | refresh 2 reads to EOF, finds no LF, writes nothing (BC-1.03.003 EC-003) |
| EC-002 | Lines after `G` inside the last extension chunk | parsed in refresh 2 up to the last LF in the blob |
| EC-003 | `S` absent (`G` first) | completed in one refresh (BC-1.03.003 EC-001) |

## Canonical Test Vectors

`L1` = `{"message": {"content": "aaaaaaaaaa"}}` + LF (39 B, conv 10). `BIG` = `{"message": {"content": "` +
600,000 × `b` + `"}}` + LF (600,029 B). Transcript = `L1` + `BIG` (600,068 B), written once, no cache, sid
`rs`. Re-pinned 2026-11-15 with the legacy oracle.

| Input | Expected Output | Category |
|-------|----------------|----------|
| refresh 1 | parser returns conv 10; cache `"size": 39`, `"conv": 10` | happy-path |
| refresh 2 (no new bytes appended) | parser returns conv 600010; cache `"size": 600068`, `"conv": 600010` | happy-path |
| same transcript with `L1` removed | one refresh: `"size": 600029`, `"conv": 600000` | edge-case |
| refresh 2 when `BIG`'s trailing LF is missing | no write; cache stays `"size": 39` | error |

Pass-3 r1 pinned the same mechanism with a 600,089 B file (refresh 1 → offset 30, conv 1; refresh 2 → conv
600,002); the vectors above are an independent re-pin.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | For `len(S) < step < len(S)+len(G)`, refresh 1 size = `len(S)`, refresh 2 size = `len(S)+len(G)` | Go property test (testing/quick) over `len(S)`, `len(G)` |
| VP-029 | Multi-step harness case matches legacy per step | M (multi-step parity case) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1041-1058) |
| Legacy contract | BC-SL-066 (pass-3 r1, new; pinned 600,089 B example) |
| Parity class | byte-exact |
| Architecture Module | `internal/statusline/transcript.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.003 — depends on: read step and extension rule
- BC-6.02.002 — related to: multi-step replay drives the two refreshes

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript.go (two-refresh completion) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029 — two-refresh completion

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1041-1058) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: the `b"\n" not in blob` loop condition (SL:1048)
- **inferred**: two-refresh consequence, confirmed by oracle runs

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads only |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | unknown |
| **Overall classification** | effectful shell |

#### Refactoring Notes

No separate code: falls out of BC-1.03.003 when the loop condition is ported literally. Do not "improve" it
by extending to the next LF after a mid-line step end.
