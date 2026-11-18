---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "874a4f0"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:effective_rl (SL:298-312)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-018
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "pass-3 remediation (ADV-P3-B09): hand-edited-cache vectors (EC-005, EC-006, and the no-ts / empty-rl vectors) tagged exclusion OD-160; 2026-11-18T02:00:00Z"
  - "pass-4 remediation (ADV-P4-B05/B07): EC-008 and its vector row tagged OD-160; DI-012 cited; 2026-11-17T12:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.013: Rate-limit smoothing over 1800 s

## Description

The client sends `rate_limits` only on subscription accounts and not on every refresh. To
stop the plan-window widget from blinking, a non-empty `rate_limits` object on stdin is
stored in the session cache with the current time and used; when stdin has none, the
cached value is used while it is younger than 1800 s, and otherwise nothing is shown. The
result replaces `d.rate_limits` before row 1 is rendered.

Notation: `T = 1800000000.0` is the injected clock.

## Preconditions

1. `sid = d.session_id` if truthy, else `nosession`; `cache_path` =
   `<cache dir>/statusline-<sid>.json` (raw sid, BC-1.06.001; cache dir per OD-101,
   BC-3.01.001).
2. `rl_stdin = d.rate_limits` (any JSON value or absent).
3. `statusline.limits.keep_s` = 1800 s (operator `<`).
4. Runs in `main` after the mix parse and before row 2 / row 1 rendering (side-effect
   order, BC-1.01.009), regardless of reroute-all and row count.

## Postconditions

1. If `rl_stdin` is a non-empty object: load the cache object `c` (missing/corrupt → `{}`),
   set `c["rl"] = rl_stdin` and `c["rl_ts"] = now` (existing keys keep their position;
   new keys are appended; BC-5.02.004), save atomically (failures ignored), and return
   `rl_stdin`.
2. Otherwise: load `c`; `rl = c.rl`; `ts = c.rl_ts` (default `0`); return `rl` if `rl` is
   an object and `now - ts < 1800`, else None. Nothing is written.
3. `d.rate_limits` := the returned value for all later rendering.
4. Written cache bytes follow Python `json.dump` defaults, e.g.
   `{"rl": {"seven_day": {"used_percentage": 44, "resets_at": 1800015480}}, "rl_ts": 1800000000.0}`
   for a previously empty cache (BC-5.02.001).

## Invariants

1. A stored value is never older than 1800 s when used.
2. Only non-empty objects are ever stored; `{}`, arrays, scalars and null on stdin count
   as absent.
3. Other keys of the shared session cache (e.g. `proc_start`, sample data) are preserved
   byte-for-byte in order.
4. Rationale (D15, T-010): owner judgment, OD-57 E-A — "30 min of plan limits between
   Claude Code reports"; may later be upgraded to measured from `anth_ratelimit` gaps.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | stdin `rate_limits: {}` | absent → cache path |
| EC-002 | stdin `rate_limits: [1]` | absent; not stored |
| EC-003 | cache age 1799.999 s | cached value used |
| EC-004 | cache age exactly 1800 s | None (strict `<`) |
| EC-005 | cache has `rl` but no `rl_ts` (foreign-cache shape, **OD-160**: Go stores only non-empty rl dicts with `rl_ts`, SL:305-308) | ts 0 → stale → None |
| EC-006 | cached `rl` is `{}` (foreign-cache shape, **OD-160**: `effective_rl` stores only non-empty dicts) | returned (object); renders nothing |
| EC-007 | cached `rl_ts` in the future | negative age → used |
| EC-008 | cached `rl_ts` a string **while cached `rl` is an object** (the `isinstance(rl, dict) and` short-circuit at SL:312: with a non-object `rl` and a string `rl_ts` the result is None and there is no crash) | foreign-cache vector (CP-C02, BC-1.06.001 EC-001): unreachable on Go-authored caches; legacy TypeError → guard line `\e[90mstatusline degraded\e[0m\n` (`\e` = 0x1B), exit 0; Go's foreign-cache behavior carries exclusion id **OD-160** (ruling Q-b) |
| EC-009 | no `session_id` | shared `statusline-nosession.json` |
| EC-010 | cached window that later crashes rendering (CP-S09) | sticky for up to 1800 s — BC-1.02.030 |
| EC-011 | temp-file names during save | covered by the temp-file exclusion, cache comparison only (BC-6.03.003, OD-110) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15 by calling `effective_rl`
with a frozen clock. `RL` = `{"seven_day":{"used_percentage":44,"resets_at":1800015480}}`.

| Input (cache before, stdin, now) | Expected Output | Category |
|-------|----------------|----------|
| no cache, `RL`, `T` | returns `RL`; cache bytes `{"rl": {"seven_day": {"used_percentage": 44, "resets_at": 1800015480}}, "rl_ts": 1800000000.0}` | happy-path |
| that cache, stdin absent, `T+1799.999` | returns `RL`; no write | happy-path |
| that cache, stdin `{}`, `T+1799.999` | returns `RL` | edge-case |
| that cache, stdin absent, `T+1800` | None | edge-case |
| no cache, stdin absent | None | edge-case |
| no cache, stdin `[1]` | None; no write | edge-case |
| cache `{"rl": {"a": 1}}` (no ts; foreign-cache shape, **OD-160**) | None | edge-case |
| cache `{"rl": {}, "rl_ts": T}` (foreign-cache shape, **OD-160**) | `{}` | edge-case |
| cache `{"proc_start": 1.5, "rl": {"old": 1}, "rl_ts": 1.0, "zz": 2}`, stdin `{"seven_day": {"used_percentage": 44}}`, `T` | cache bytes `{"proc_start": 1.5, "rl": {"seven_day": {"used_percentage": 44}}, "rl_ts": 1800000000.0, "zz": 2}` | edge-case |
| cache `{"rl": {"a": 1}, "rl_ts": "x"}`, stdin absent | TypeError → full run prints the guard line, exit 0 (foreign-cache vector, CP-C02 — EC-008; exclusion **OD-160**, ruling Q-b) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | Sequence replay (report, silence ×n, report) reproduces oracle stdout and cache bytes at every step | parity harness stdin-sequence (BC-6.02.002) |
| VP-019 | Cache written by Python is read identically by Go and vice versa | cache-swap test (BC-6.02.004) |
| VP-028 | Used value age < keep_s always | property test |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:effective_rl (SL:298-312); RL_KEEP SL:85; call site main SL:1214-1216 |
| Legacy contract | BC-SL-018 |
| Parity class | byte-exact for Go-authored caches; hand-edited-cache vectors carry exclusion **OD-160** (foreign-cache shapes, ruling Q-b); temp-file handling belongs to BC-6.03.003 |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 (no ledger read: smoothing uses only stdin + own cache), DI-008, DI-012 |
| Owner decisions | OD-57 E-A (1800 s rationale), OD-101 (cache dir), OD-110 (temp-file entry) |
| Config keys | `statusline.limits.keep_s` (1800 s), `paths.cache_dir` |
| Architecture Module | `internal/statusline/limits.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.010 — composes with (expiry applies to smoothed values)
- BC-1.02.009 — related to (display gate; smoothing still runs)
- BC-1.02.030 — composes with (sticky CP-S09 sequence)
- BC-1.06.001 — depends on (cache load/save, raw sid names)
- BC-1.01.009 — related to (side-effect order)
- BC-5.02.001 / BC-5.02.004 — depends on (json bytes, ordered objects)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#limits` — internal/statusline/limits.go (smoothing 1800 s + session cache) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — plan-window widget story

## VP Anchors (Recommended)

- VP-028 — smoothing sequence parity; VP-019 — four-cache swap (moved from VP-028, pass-1 finding ADV-P1-B11)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`effective_rl`, SL:298-312) |
| **Confidence** | high (pass-3 HIGH-R; re-run 2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(rl_stdin, dict) and rl_stdin` (SL:305); `isinstance(rl, dict) and now - ts < RL_KEEP` (SL:312)
- **documentation**: docstring SL:299-303

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads + writes (session cache) |
| **Global state access** | reads clock (injected) |
| **Deterministic** | yes under injected clock and cache dir |
| **Thread safety** | n.a. (atomic rename) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Split into a pure `(cache, stdin, now, keep) -> (value, newCache?)` and an I/O shell.
