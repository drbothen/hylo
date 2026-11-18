---
document_type: behavioral-contract
level: L3
version: "1.3.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r7.md]
input-hash: "024779e"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:sparkline (SL:659-690)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-073"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.3 2026-11-18: pass-11 remediation ADV-P11-C2-04 (cached-path sparkline crash sites EC-008..EC-010 added — dict/number/null hist TypeError at the SL:664 slice, short-list-point IndexError at SL:655 via SL:664, plotted giant exact int OverflowError at SL:674, non-numeric plotted value TypeError at SL:671/674, OD-160 class; DI-012 lifted into the L2 row; timestamp raised above the new modified entry)"
  - "1.3.1 2026-11-18: pass-12 remediation ADV-P12-C2-01 (EC-010 giant-int bound signed positive — value >= 2**1024 - 2**970; a negative giant renders the lowest glyph per BC-1.04.009 EC-012, oracle-verified) + ADV-P12-C2-02 (VP-012 exclusion-closure row) + ADV-P12-C2-05 (Pre 1/EC-006/EC-008 plotted window generalized to statusline.sparkline.points, default 12)"
  - "1.3.2 2026-11-18: pass-13 residual (orchestrator residual sweep, CP-C register alignment): EC-008 cites CP-C20 and EC-010 cites CP-C21/CP-C22/CP-C23 beside the legacy sites, minted by error-taxonomy 1.20; no behavioral change"
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
   least 2 of the last `statusline.sparkline.points` history points (default 12) carry
   the trace key.
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
| EC-006 | NaN point older than the last `statusline.sparkline.points` points (default 12) | not plotted → no crash |
| EC-007 | Sparkline disabled | main passes `[]` → no crash |
| EC-008 | Cached path, stored `hist` a JSON dict, number or null (foreign cache, exclusion id **OD-160**) | `hist[-N:]` (`N` = `statusline.sparkline.points`, default 12) raises TypeError (a dict slice is unhashable in CPython 3.11; SL:664; CP-C20) → errDegraded, same top-level-guard disposition as PC1 (not the CP-N02 `int()` site itself) |
| EC-009 | Cached path, a stored point a list shorter than 2 elements | IndexError inside `_norm_pt` (SL:655 via SL:664) → errDegraded (same class; on the cached path the sparkline's own normalization at SL:664 is the first — BC-1.04.002 PC1 returns `hist` raw) |
| EC-010 | A plotted point's value a giant exact int (value >= 2**1024 - 2**970, positive only — a NEGATIVE giant does not raise: `max(v, 0.0)` returns the float `0.0` and the cell draws the lowest glyph, BC-1.04.009 EC-012, ADV-P12-C2-01) or a non-numeric scalar (foreign cache, **OD-160**) | OverflowError (SL:674, CP-C22) / TypeError (SL:671, CP-C21; SL:674, CP-C23) → errDegraded (same class) |

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
| VP-012 | The named deviation this contract carries — exclusion id `OD-160` (EC-008..EC-010 cached-path foreign-hist crash shapes) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-160` entry and its riding table test `TestForeignCacheShape_OD160_Vectors` (this contract has no riding test of its own, same citation class as BC-1.04.002/BC-1.04.003/BC-1.04.018), and the mutation test fails closed if that entry is dropped (ADV-P12-C2-02) | property test (VP-012, go test) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:sparkline (SL:659-690; raise at SL:673-675); guard (SL:1238-1245) |
| Legacy contract | BC-SL-073 (P3 r1 new; r7 flag "latent in production") |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-008, DI-012 (cached-path foreign-hist crash shapes EC-008..EC-010 under the OD-160 named-deviation rule) |
| Decisions | owner ruling on catalogued crash paths (handled defensively, byte for byte; P3 r7 §5) |
| Architecture Module | `internal/statusline/sparkline.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.009 — refines: sparkline
- BC-1.01.001 — depends on: degraded line
- BC-1.01.009 — depends on: writes kept before a degrade
- BC-5.01.003 — depends on: typed `Int` errors (ErrValue)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/sparkline.go (CP-N02) (errDegraded sites) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030, VP-001 — CP-N02 equivalence
- VP-012 — OD-160 exclusion-closure citation (EC-008..EC-010; ADV-P12-C2-02)

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
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure (returns an error) |

#### Refactoring Notes

`sparkline` returns `(string, error)`; `pyfmt.Int` returns `ErrValue` for NaN. The
error wraps `errDegraded` with the CP id for diagnostics only.
