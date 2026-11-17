---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md]
input-hash: "04f459c"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:get_sample (SL:315-359)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-041"
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

# Behavioral Contract BC-1.04.002: get_sample TTL / KEEP_DEAD state machine

## Description

`get_sample` decides per refresh whether to reuse the cached verdict or fetch, writes the
session cache, and returns `(sample | none, age_s, up, hist)`. Within the TTL the cached
verdict is returned **without** the KEEP_DEAD check (legacy quirk, reproduced); on a
fetch, success resets the age to 0 and failure returns the last-known sample only while
it is younger than KEEP_DEAD.

## Preconditions

1. `now` is the single per-render clock read (`Env.Now`, Python `time.time()` value).
2. `c` = session cache `statusline-<sid>.json` loaded via the never-raise loader
   (BC-1.06.001); an unreadable file is `{}`.
3. `ttl` = `statusline.telemetry.ttl_s` (default 4, T-001, convention: "match refreshInterval");
   `keep_dead` = `statusline.telemetry.keep_dead_s` (default 300, T-004, judgment
   "5 min of last-known telemetry before giving up", OD-57 E-A). Non-finite or negative
   TTL is a config error — approved deviation D4-EX-3 (BC-2.02.002; OD-105 exclusion
   entry `D4-EX-3`, dedicated test `TestConfigError_D4EX3_Number`); TTL 0 is valid
   (always fetch).

## Postconditions

1. **Cached path** — if `c.get("fetch_ts", 0) > now - ttl` (strict): no fetch, no write;
   return `(c.get("sample"), now - c.get("ts", 9999), bool(c.get("up")), c.get("hist", []))`.
   `hist` is returned raw (legacy `[t, v]` list points are not normalized here).
2. **Fetch path** — otherwise call BC-1.04.001 once; `entry` = copy of `c` with key
   `sess_state` deleted if present.
3. **Success** (non-empty sample): build history per BC-1.04.003; append/overwrite keys
   `fetch_ts=now, up=true, ts=now, sample=<sample>, hist=<hist[-32:]>`; save; return
   `(sample, 0.0, true, hist)` (the returned `hist` is the uncapped list).
4. **Failure**: set `entry.fetch_ts=now`, `entry.up=false` (old `ts`, `sample`, `hist`
   kept verbatim); save; `age = now - c.get("ts", 0)`; return
   `(c["sample"], age, false, c.get("hist", []))` if `c.get("sample")` is truthy and
   `age < keep_dead`, else `(none, age, false, [])`.

## Invariants

1. Total except the typed history-point site (a malformed point raises IndexError → errDegraded, BC-1.04.003 EC-009); cache write errors are swallowed.
2. KEEP_DEAD is applied **only** on the fetch path (pinned quirk: inside a TTL window
   after a failed fetch an over-300 s sample renders stale instead of `◌ DGX ?`).
3. A failed fetch never deletes the stored sample.
4. Cache bytes follow BC-1.04.020 (key order, float repr, NaN tokens).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `fetch_ts == now - ttl` | not cached (strict `>`): fetch |
| EC-002 | Failed fetch, age exactly 300 | `(none, 300.0, false, [])` (`< 300` false) |
| EC-003 | Cached path 2 s after EC-002 | `(sample, 302.0, false, hist)` → stale row with `(~302s old)` |
| EC-004 | First-ever failed fetch, empty file | file becomes `{"fetch_ts": 1000.0, "up": false}`; returns `(none, 1000.0, false, [])` (age `now - 0`) |
| EC-005 | Cached path with no `ts` (after EC-004) | age `now - 9999`; sample none → `◌ DGX ?` |
| EC-006 | TTL 0 | every refresh fetches |
| EC-007 | Stored sample holds `NaN` | written as JSON `NaN`, read back by the Go loader (must accept `NaN`/`Infinity` tokens) |
| EC-008 | Foreign/corrupt cache shapes (CP-C01..C10) | out of byte-parity scope (P3 r2 ruling (b)); Go writer never produces them |

## Canonical Test Vectors

TTL 4, frozen clock, fetch outcome injected (full 11-step table with exact JSON: BC-1.04.020).

| Input | Expected Output | Category |
|-------|----------------|----------|
| t=1000, fetch succeeds with S1 = `{running 1, kv 0.5, gen_rate1m 80}` | `(S1, 0.0, true, …)`; cache gains `"fetch_ts": 1000.0, "up": true, "ts": 1000.0, "sample": {…}` | happy-path |
| t=1002 after the above | cached: `(S1, 2.0, true, …)`, file unchanged | edge-case |
| t=1004, fetch fails | `(S1, 4.0, false, …)`; file `"fetch_ts": 1004.0, "up": false`, `ts`/`sample`/`hist` kept | error |
| t=1300 (age 300), fetch fails | `(none, 300.0, false, [])` → row 2 `\e[31m◌ DGX ?\e[0m` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Same `(sample, age, up, hist)` and same cache bytes as legacy for every step of the pinned sequence | manual (multi-step table, BC-1.04.020) |
| VP-030 | Cached path performs zero fetches and zero writes | Go property test (testing/quick) (fake metrics counter) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:get_sample (SL:315-359); TTL/KEEP_DEAD (SL:74, 80) |
| Legacy contract | BC-SL-041 (P3 base quirk; r1 confirmed NaN tokens; r2 §A2) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007, DI-008 |
| Decisions | OD-55 (keep T-003/T-007/T-008/T-009 as keys), OD-57 E-A (T-004), OD-114 (TTL range), OD-101 (cache dir) |
| Architecture Module | `internal/statusline/sample.go` (design §2.2) |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.001 — depends on: the fetch
- BC-1.04.003 — composes with: history point rules on success
- BC-1.04.004 — composes with: renders `(sample, age, up)`
- BC-1.04.020 — refined by: pinned sequence and key order
- BC-1.06.001 — depends on: cache load/save
- BC-2.02.002 — related to: TTL range errors (D4-EX-3)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#effect-step-script-design-doc-31-normative` — internal/statusline/sample.go (TTL/KEEP_DEAD) (session cache state machine) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — state-machine equivalence

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:315-359) |
| **Confidence** | high — re-executed on CPython 3.11.7 (2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if c.get("fetch_ts", 0) > now - TTL` (SL:324); `if c.get("sample") and age < KEEP_DEAD` (SL:357)
- **inferred**: KEEP_DEAD absent on the cached path (no check at SL:325)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads + writes (session cache), network call (via fetch) |
| **Global state access** | reads config |
| **Deterministic** | yes given clock, cache and fetch result |
| **Thread safety** | not thread-safe (file read-modify-write) |
| **Overall classification** | mixed |

#### Refactoring Notes

Extract pure `nextSampleState(c Value, now float64, fetched (Value, bool)) (entry Value,
result SampleResult, write bool)`; the effect script performs the load, fetch and save
in legacy order (design §3.1 step 4).
