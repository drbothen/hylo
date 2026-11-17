---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r7.md]
input-hash: "58646e3"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-073"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.014: Sparkline NaN/+Inf crash path (CP-N02)

## Description

A non-finite value that reaches the sparkline's half-up index makes legacy raise
(`int(nan)`), which the top-level guard turns into the degraded line. The Go port
reproduces this byte for byte: the same inputs produce the 29-byte degraded line with the
same earlier cache writes kept. Latent in production (the metrics store returns absent
series, not NaN; capture 2026-11-14), but kept per the owner ruling on catalogued crash
paths. Notation: `\e` is byte 0x1B.

## Preconditions

1. The sparkline is actually invoked: row 2 is rendered (BC-1.04.013), the row is fresh
   (not stale), the sparkline is enabled, the box rate is present (BC-1.04.008), and at
   least 2 of the last 12 history points carry the trace key.
2. Among those plotted points: any NaN (any trace), or +Inf for the `v` or `f` trace.

## Postconditions

1. The render returns `errDegraded` at the sparkline site (CP-N02); stdout is exactly the
   degraded line `\e[90mstatusline degraded\e[0m\n` (29 bytes, BC-1.01.001); exit 0.
2. Writes made before the row-2 render persist (mix cache, rate-limit write, session-cache
   write from `get_sample`); writes after it do not happen (`proc_start`, git cache,
   cost-history), per BC-1.01.009.

## Invariants

1. +Inf on the `k` trace is safe (fixed top 1.0: `min(inf, 7)` = 7 → `█`).
2. -Inf on any trace is safe (clamped to 0 → `▁`).
3. A finite value with a +Inf peak on `v`/`f` crashes (`inf / inf` = NaN at the +Inf point).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `v` [1, NaN] fresh | degraded |
| EC-002 | `v` [1, +Inf] fresh | degraded |
| EC-003 | `k` [0.5, +Inf] (`kv` trace) | `\e[38;2;38;93;104m▅\e[38;2;140;235;255m█\e[0m` |
| EC-004 | `v` [-Inf, 2] (as [-5, 2]) | `▁█`, no crash |
| EC-005 | Same NaN history but row stale | no sparkline call → no crash |
| EC-006 | NaN point older than the last 12 | not plotted → no crash |
| EC-007 | Sparkline disabled | main passes `[]` → no crash |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| fresh, `gen_rate1m` 80, hist `v` [60, 70] | normal row 2 (no crash) | happy-path |
| `kv` trace, `k` [0.5, +Inf] | `\e[38;2;38;93;104m▅\e[38;2;140;235;255m█\e[0m` | edge-case |
| fresh, rate trace, hist `v` [1.0, NaN] (NaN stored as JSON `NaN` in the session cache) | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030, VP-001 | Go degrades iff legacy raises at SL:675, for every trace × value class (finite, NaN, +Inf, -Inf) | manual (table) |
| VP-030, VP-001 | Cache files after a degraded run equal legacy's byte for byte | manual (multi-step) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:sparkline (SL:659-690; raise at SL:673-675); guard (SL:1238-1245) |
| Legacy contract | BC-SL-073 (P3 r1 new; r7 flag "latent in production") |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008 |
| Decisions | owner ruling on catalogued crash paths (handled defensively, byte for byte; P3 r7 §5) |
| Architecture Module | `internal/statusline/sparkline.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.009 — refines: sparkline
- BC-1.01.001 — depends on: degraded line
- BC-1.01.009 — depends on: writes kept before a degrade
- BC-5.01.003 — depends on: typed `Int` errors (ErrValue)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#degraded-ladder` — internal/statusline/sparkline.go (CP-N02) (errDegraded sites) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030, VP-001 — CP-N02 equivalence

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:671-675) |
| **Confidence** | high — re-executed on CPython 3.11.7 (`ValueError: cannot convert float NaN to integer` for both NaN and +Inf) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: no guard around `int(...)` at SL:675; top-level `except Exception` (SL:1243)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | reads config |
| **Deterministic** | yes |
| **Thread safety** | Send + Sync |
| **Overall classification** | pure (returns an error) |

#### Refactoring Notes

`sparkline` returns `(string, error)`; `pyfmt.Int` returns `ErrValue` for NaN. The
error wraps `errDegraded` with the CP id for diagnostics only.
