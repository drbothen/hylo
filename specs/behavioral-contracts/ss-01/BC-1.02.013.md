---
document_type: behavioral-contract
level: L3
version: "1.2.6"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "83527c6"
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
  - "1.2.1 pass-3 remediation (ADV-P3-B09): hand-edited-cache vectors (EC-005, EC-006, and the no-ts / empty-rl vectors) tagged exclusion OD-160; 2026-11-18T02:00:00Z"
  - "1.2.2 pass-4 remediation (ADV-P4-B05/B07): EC-008 and its vector row tagged OD-160; DI-012 cited; 2026-11-18T03:00:00Z"
  - "1.2.3 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-20) — pass-4 stamp re-dated ascending (it predated pass-3's); no behavioral change"
  - "1.2.4 pass-6 remediation (ADV-P6-B01, call 10): for-all used-age row re-anchored from VP-028 to VP-041 (VP-028 keeps the sequence golden leg); 2026-11-19T04:00:00Z"
  - "2026-11-24T01:00:00Z (1.2.5): pass-14 remediation (ADV-P14-B04, call 4): new EC-012 and vector row — a session cache that parses as a JSON non-object (e.g. []) is neither missing nor corrupt; legacy faults at SL:307 (stdin rl present, item assignment TypeError) or SL:311 (absent, .get AttributeError), the CP-C01 register id, OD-160, Go table test (measured CPython 3.11.7, isolated temp HOME/cwd); PC1 qualifies its missing/corrupt fallback accordingly; Verification Properties gains the VP-001 row for EC-010's CP-S09 sticky leg and EC-010 cites it (B02 co-owner symmetry); no behavioral change"
  - "2026-11-26T15:00:00Z (1.2.6): pass-14 residual sweep (OD-160 owner id-range alignment): EC-008 gains the giant rl_ts OverflowError leg CP-C33 (same SL:312 site; scalars stay CP-C02); EC-012's CP-C01 co-ownership recorded in the error-taxonomy row and owner table; no behavioral change"
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

1. If `rl_stdin` is a non-empty object: load the cache object `c` (missing/corrupt → `{}`; a cache that parses as a
   JSON non-object is neither missing nor corrupt — it faults the consult, EC-012/CP-C01),
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
| EC-008 | cached `rl_ts` a string or an exact giant integer **while cached `rl` is an object** (the `isinstance(rl, dict) and` short-circuit at SL:312: with a non-object `rl` and a string `rl_ts` the result is None and there is no crash) | foreign-cache vector (CP-C02 scalar, CP-C33 giant; BC-1.06.001 EC-001): unreachable on Go-authored caches; legacy TypeError → guard line `\e[90mstatusline degraded\e[0m\n` (`\e` = 0x1B), exit 0; Go's foreign-cache behavior carries exclusion id **OD-160** (ruling Q-b); a giant exact-int `rl_ts` (both signs) raises OverflowError at the same `now - ts` subtraction (**CP-C33**, measured pass-14) |
| EC-009 | no `session_id` | shared `statusline-nosession.json` |
| EC-010 | cached window that later crashes rendering (CP-S09) | sticky for up to 1800 s — BC-1.02.030 (VP-001 cps09 fault-injection row; the sticky consequence is stated at BC-1.02.030 PC4) |
| EC-011 | temp-file names during save | covered by the temp-file exclusion, cache comparison only (BC-6.03.003, OD-110) |
| EC-012 | session cache that parses as a JSON non-object (e.g. `[]`) — neither missing nor corrupt (PC1's `{}` fallback does not apply); foreign-cache vector, **CP-C01** (OD-160) | legacy faults the consult before any shape is read: stdin `rl` present — TypeError at the `c["rl"] = ...` item assignment (SL:307); absent — AttributeError at `.get` (SL:311); both measured CPython 3.11.7, isolated temp HOME/cwd (pass-14); unreachable on Go-authored caches; guard line `\e[90mstatusline degraded\e[0m\n`, exit 0; Go's foreign-cache behavior carries exclusion id **OD-160** (ruling Q-b) — Go table test, not byte-parity |

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
| cache `[]` (JSON non-object; foreign-cache vector, **CP-C01** — EC-012), stdin `RL`, `T` | TypeError (item assignment, SL:307) → full run prints the guard line, exit 0 (exclusion **OD-160**, ruling Q-b; measured CPython 3.11.7, isolated temp HOME/cwd) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | Sequence replay (report, silence ×n, report) reproduces oracle stdout and cache bytes at every step | parity harness stdin-sequence (BC-6.02.002) |
| VP-019 | Cache written by Python is read identically by Go and vice versa | cache-swap test (BC-6.02.004) |
| VP-041 | Used value age < keep_s always — for all replay states | property test (for-all leg; VP-028 delivers the oracle legs) |
| VP-001 | The CP-S09 sticky leg (EC-010: a cached malformed window keeps degrading every refresh for up to 1800 s) stays on the never-blank ladder — exactly the 29-byte degraded line, exit 0 | table test (fault-injection row of VP-001's ladder) |

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

- VP-041 — used-age for-all property; VP-028 — smoothing sequence parity (golden leg); VP-019 — four-cache swap (moved from VP-028, pass-1 finding ADV-P1-B11)
- VP-001 — cps09 sticky degrade stays on the never-blank ladder (EC-010; BC-1.02.010 EC-009 is the first-crash owner)

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
