---
document_type: behavioral-contract
level: L3
version: "1.0.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T07:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md]
input-hash: "14effd8"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_fmt_tokens + token/elapsed branches (SL:909-921, 876-885)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.2.2
modified: ["1.0.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet rows replaced with VP-009 (dense grid) + VP-039 (clock ulp)", "1.0.2 2026-11-18T07:00:00Z: adv-p3 remediation: huge-int overflow paths catalogued as CP-A04 (float(n), SL:878) and CP-A05 (now_ms - start, SL:919) (ADV-P3-C04); threshold/format order wording fixed (ADV-P3-C19); tok suffix and thresholds sourced from statusline.subagent.tokens.* config keys (ADV-P3-C05)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.007: Token segment (_fmt_tokens) and running-only elapsed clock

## Description

Two conditional bits close the row. Tokens: a positive numeric `tokenCount` renders
`<CYAN><_fmt_tokens(tok)> tok<RESET>` with `_fmt_tokens` = `.0f` below 1000, `.1f`k to 999,999, `.2f`M
above (compact tokens approved mockup). The "?" fallback is reached only on TypeError/ValueError
coercions; a huge int (|n| >= 2**1024 - 2**970) raises OverflowError at `float(n)`, which the helper
does not catch, degrading via the guard (CP-A04, BC-1.07.008). Clock: only a `running` row with
numeric `startTime > 0` gets `MM:SS` elapsed (`max(now_ms - start, 0)/1000`, minute-second split) — a
settled row's clock must not keep counting (review #21.2), a huge-int `startTime` overflows the same
way at `now_ms - start` (CP-A05), and the PR-15 FMA pitfall binds the float port (explicit `float64`
per product, operation order preserved; FMA detector test on darwin/arm64 only, CONV-ABS-77).

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 3.
2. Wall clock read once per render (`now_ms = time.time() * 1000`, SL:889 — a PR-15 site).
3. `tokenCount` and `startTime` taken from the eligible task dict.

## Postconditions

1. Token bit: only when `tokenCount` is int/float/bool with value > 0; bytes
   `\e[36m<fmt> tok\e[0m` where fmt = `f"{n:.0f}"` (< 1000), `f"{n/1000:.1f}k"` (< 1e6),
   `f"{n/1e6:.2f}M"` (>= 1e6) after `float(n)`; the threshold compares the float value first, then the
   format rounds (round-half-to-even applied by CPython `format()` to the exact binary double) —
   EC-003.
2. Clock bit: only when `status == "running"` AND `startTime` is int/float/bool AND `startTime > 0`;
   bytes `\e[90m{int(secs//60):02d}:{int(secs%60):02d}\e[0m`, `secs = max(now_ms - start, 0)/1000`.
3. Future startTime (start > now) clamps to `00:00` — the max(..., 0) floor.
4. Settled rows (completed/failed/killed/unknown) show no clock even when `startTime` is set.
5. Non-numeric `tokenCount`/`startTime` (string, null, list, dict) → the bit is silently omitted.
6. Huge-int `tokenCount` (value > 0, |n| >= 2**1024 - 2**970): passes the gate, raises OverflowError
   at `_fmt_tokens`'s `float(n)` (SL:878); the helper catches only TypeError/ValueError, so the fault
   propagates to the guard — the degraded line (CP-A04, BC-1.07.008).
7. Huge-int `startTime` (running, value > 0, |n| >= 2**1024 - 2**970): raises OverflowError at
   `now_ms - start` (SL:919) — the degraded line (CP-A05, BC-1.07.008).

## Invariants

1. `_fmt_tokens` thresholds compare AFTER `float(n)`: 1000 → `1.0k`, 999.5 → `1000`
   (threshold-then-format: 999.5 fails the `>= 1000` test, then the `.0f` format rounds
   half-to-even to `1000`), 999,999 → `1000.0k` (verified).
2. Bool `tokenCount=True` passes the isinstance gate and > 0 test and renders `1 tok`
   (Python bool-as-int quirk, pinned).
3. PR-15 remedy: every float product (notably `time.time() * 1000`) ports with an explicit `float64`
   conversion and Python operation order; Go must not fuse `x*y + z` across statements on arm64.
   Detector test placed on darwin/arm64 CI only (GOAMD64=v3; v1 never fuses — CONV-ABS-77).
4. The clock base `now_ms` is captured once per render, not per row (SL:889).
5. The ` tok` suffix and the 1000/1e6 scale thresholds come from `statusline.subagent.tokens.*`
   config keys (leaf spellings registered by the architect in the BC-2.01.004 registry, per the
   ADV-P3-C05 ruling) with legacy defaults (` tok`, 1000, 1e6); no hard-coded literals in logic (D15).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `tokenCount = 0`, `-5`, `False`, `""`, `"500"`, null | Bit omitted (gate: numeric AND > 0) |
| EC-002 | `tokenCount = True` | Bit renders `1 tok` (bool-is-int quirk) |
| EC-003 | `tokenCount = 999.5` | Renders `1000 tok` (threshold-then-format order) |
| EC-004 | Completed row with `startTime` set | No clock; grey status suffix only |
| EC-005 | `startTime = true` (bool) | Clock computed from epoch-1ms — a huge valid MM:SS; exact bytes time-dependent (not pinned) |
| EC-006 | Very large tokenCount (1e9) | `1000.00M` (>=".2f"M of 1000.0) |
| EC-007 | startTime exactly 0 | No clock (gate is `> 0`) |
| EC-008 | `tokenCount = 2**1024 - 2**970` (huge int) | OverflowError at `float(n)` → exactly the degraded line, exit 0 (CP-A04) |
| EC-009 | `startTime = 2**1024 - 2**970`, running | OverflowError at `now_ms - start` → exactly the degraded line, exit 0 (CP-A05) |

## Canonical Test Vectors

| Input (task fields) | Expected Output | Category |
|---|---|---|
| `tokenCount=12345`, running, `startTime=<now-125000>` | `\e[36m12.3k tok\e[0m \u00b7 \e[90m02:05\e[0m` (within the BC-1.07.004 pinned row) | happy-path |
| `tokenCount=2500000`, completed | `\e[36m2.50M tok\e[0m`, no clock | happy-path |
| `tokenCount=500`, running | `\e[36m500 tok\e[0m` | happy-path |
| `_fmt_tokens` direct: 12345 / 2500000 / 500 / 999.5 / 1000 / 999999 / True / "abc" / None | `12.3k` / `2.50M` / `500` / `1000` / `1.0k` / `1000.0k` / `1` / `?` / `?` | table |
| running, `startTime=<now+60000>` | `\e[90m00:00\e[0m` (floor) | edge-case |
| `tokenCount = 2**1024 - 2**970`, running, `startTime=<now-125000>` | exactly `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 (CP-A04) | error |
| `tokenCount = 2**1024 - 2**970 - 1`, running (largest convertible int) | renders; `float` value is the IEEE-754 maximum; tok bit present, no degrade | edge-case |
| `startTime = 2**1024 - 2**970`, running | exactly `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 (CP-A05) | error |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`): every cell above reproduced, including the
999.5 → `1000` and True → `1` quirks and the `02:05` split at 125 s; the overflow threshold confirmed
empirically — `float(2**1024 - 2**970)` raises OverflowError, `float(2**1024 - 2**970 - 1)` converts
(CP-A04/A05, adv-p3).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-009 | `_fmt_tokens` equals CPython format over a dense grid incl. threshold boundaries (rides the Tier A T-family corpus rows) | manual corpus comparison (Tier A) |
| VP-039 | PR-15: fused vs unfused elapsed-clock floats agree at ulp level on arm64; rendered MM:SS byte-identical across regimes | FMA detector test, darwin/arm64 only (CONV-ABS-77) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (gates never raise), DI-012 (quirks pinned, no silent normalization) |
| Architecture Module | `internal/statusline` (token/clock bits); float ops per `internal/pyfmt` Num conventions |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py: token bit (SL:909-911), clock (SL:913-921), `_fmt_tokens` (SL:876-885; `float(n)` SL:878), now_ms (SL:889), `now_ms - start` (SL:919) |
| Legacy contract | BC-SL-097 (P3r2 §A7; `_fmt_tokens` home r8; CP-A04/A05 enumerated adv-p3); pitfall PR-15 (P5r1 §292, r2 §A.2) |
| Decisions | OD-155; D4; adv-p3: OD-156 + new CP ids (ADV-P3-C04), ADV-P3-C05 token config keys; review 2026-11-13 #21.2 (clock gate), #8.1 analog (compact scales); CONV-ABS-77 (FMA test placement) |

## Related BCs (Recommended)

- BC-1.07.004 — composes with (framing)
- BC-1.07.005 — composes with (suffix interplay: settled rows)
- BC-1.07.008 — related to (CP-A04/A05 overflow sites degrade to the 29-byte line)
- BC-5.01.* — related to (Python number-formatting semantics family)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — segment builder; PR-15 float discipline in the elapsed-clock
  helper

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-009 (T-family `_fmt_tokens` dense grid)
- VP-039 (PR-15 fused/unfused clock ulp agreement)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:909-921, 876-885, 889) |
| **Confidence** | high (dense pinned grid 2026-11-18) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **assertion**: 9-cell `_fmt_tokens` table + clock clamp/bool quirks, all pinned under CPython 3.11.7
- **guard clause**: isinstance+(>0) gates (SL:909, 917-918)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | wall clock (once per render) |
| **Deterministic** | yes modulo wall clock |
| **Thread safety** | safe for concurrent use |
| **Overall classification** | pure (given now_ms) |

#### Refactoring Notes

Go: keep `_fmt_tokens` as a pure `func(n any) string` mirroring float64(everything)-then-branch order;
inject `now_ms` for testability. Apply the PR-15 remedy textually: `nowMs := float64(time.Now().UnixMilli())`
style single-product expression, never a fused multiply-add chain.
