---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T10:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
  - semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "718be36"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:record_cost (SL:224-237)"
subsystem: "SS-01"
capability: "CAP-011"
legacy_id: "BC-SL-028"
parity_class: "byte-exact"
confidence: "H"
lifecycle_status: active
introduced: v0.1.0
modified: ["1.2.1 2026-11-17: VP citation reconciliation — VP-001 added", "1.2.2 2026-11-17: pass-2 remediation ADV-P2-C2-07 (T-022 rationale signed off)", "1.2.3 2026-11-18: pass-3 remediation ADV-P3-C2-01 (OD-166 record guard) + ADV-P3-C2-02 (OD-160 exclusion id on EC-008)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.05.004: record_cost throttled write

## Description

Every refresh that renders a cost segment stores this session's exact Claude Code cost
in the cost history (`cost-history.json` in `paths.cache_dir`), tagged `src: "cc"`, at
most once per session per minute. It runs before the percentile read, so a new entry
is visible to other sessions' thresholds in the same instant but never to its own
(self-exclusion, BC-1.05.005). The exact bytes written are BC-1.05.009.

## Preconditions

1. Called only inside the cost block (`total_cost_usd` numeric and `> 0`), with
   `sid = stdin session_id` as given (raw value, **not** the `nosession` fallback),
   `lane` = the client-view lane (`dgx` | `anth` | None), `usd` = `total_cost_usd`,
   `api_ms` = `total_api_duration_ms` (SL:603-606).
2. Config: `statusline.cost.record_throttle_s` = 60 (T-022, strict `<`).
3. `now` is the render's clock reading (one clock read per render in Go, design §6.4;
   legacy reads `time.time()` per call, identical under the frozen-clock harness).

## Postconditions

1. **Guard (no read, no write):** if `sid` is falsy (absent, null, `""`, `0`, `false`),
   or `lane` is not exactly `"dgx"` or `"anth"`, or `usd` is not a number (bool counts as
   a number), return without touching the file (SL:226-227). Per ruling **OD-166**, the
   guard also rejects a numeric `usd` (and the paired `api_ms`) whose float conversion
   would overflow — an exact stdin int with magnitude >= 2**1024 - 2**970 — so an
   unconvertible value is **not recorded** (exclusion id `OD-166`; legacy did record the
   giant int via `round(usd, 4)` + `json.dump`, SL:234-237, poisoning later refreshes at
   SL:255 — a foreign-history class path, BC-1.05.005 EC-011). The current refresh still
   renders/degrades as ruled (BC-1.05.007 CP-O10/CP-O11).
2. Otherwise load the history (BC-1.06.001 load: any error → `{}`), take
   `sessions = h.setdefault("sessions", {})` and `e = sessions.get(sid) or {}`
   (SL:228-230).
3. **Throttle:** if `e.src == "cc"` and `now - e.get("ts", 0) < record_throttle_s`,
   return without writing (SL:232-233).
4. Otherwise set `sessions[sid] = {"lane": lane, "usd": round(usd, 4), "api_ms": api_ms
   if numeric else null, "ts": now, "src": "cc"}` and save the whole history atomically
   (BC-1.06.001 save) (SL:234-237). An existing key keeps its position; a new key is
   appended last; every other key and entry is preserved unchanged.
5. An entry with any other `src` (e.g. `"backfill"`) is overwritten on the first
   refresh (never throttled).

## Invariants

1. At most one write of `cost-history.json` per refresh, and none while throttled.
2. The write precedes `cost_thresholds` (SL:606-607; design §3.1 step 7c).
3. Save errors are swallowed (cache loss is cosmetic); a concurrent session may lose an
   update, repaired within a minute (R-4, accepted).
4. No write at all on a D4-EX-3 config error (design §3.1 step 0).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | existing `cc` entry at `ts`, refresh at `ts + 59.999` | no write (file unchanged) |
| EC-002 | refresh at `ts + 60.000` | written (strict `<`) |
| EC-003 | lane None (no prefixes or empty model id) | no read, no write |
| EC-004 | `session_id` absent / `""` | no write (the `nosession` fallback is never used here) |
| EC-005 | `session_id` unhashable (non-empty list/object) | legacy `sessions.get(sid)` raises TypeError (CP-S15, SL:230) after the load, before any write → degraded line (BC-1.01.001); Go degrades at the same step |
| EC-006 | numeric `session_id` | OD-30 known difference, see BC-1.05.006 |
| EC-007 | entry `ts` missing | default 0 → throttle not applied → written |
| EC-008 | corrupt history shapes (top level not an object; `sessions` or an entry not an object; entry `ts` non-numeric) | CP-C09/CP-C10 foreign-cache crash paths: out of parity scope (P3r2 ruling b); the foreign-cache class carries named exclusion id **OD-160** (DI-012 named-deviation rule); the Go writer only ever writes legacy's exact format |
| EC-009 | `api_ms` = `"x"` | stored as `null` |
| EC-010 | `usd` = 2**1024 (309-digit exact stdin int; numeric guard passes) | not recorded (OD-166 guard: magnitude >= 2**1024 - 2**970 cannot convert to float); file unchanged; the current refresh degrades via CP-O10 (BC-1.05.007); legacy did record it (ADV-P3-C2-01) |

## Canonical Test Vectors

Clock `now = 1794615009.0`, empty history unless noted.

| Input | Expected Output | Category |
|-------|----------------|----------|
| sid `t`, lane anth, usd 2.0, api 1000 | file `{"sessions": {"t": {"lane": "anth", "usd": 2.0, "api_ms": 1000, "ts": 1794615009.0, "src": "cc"}}}` | happy-path |
| then sid `t`, usd 4.0 at now + 59.999 | file unchanged (usd 2.0) | edge-case |
| then sid `t`, usd 4.0 at now + 60.000 | `{"sessions": {"t": {"lane": "anth", "usd": 4.0, "api_ms": 1000, "ts": 1794615069.0, "src": "cc"}}}` | edge-case |
| sid `""`, or lane `zzz`, or usd `"3"` | no file written / file unchanged | error |
| sid `t`, lane anth, usd = 2**1024 (exact int), api 1000 | file unchanged (OD-166 record guard) | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-020 | Two refreshes less than record_throttle_s apart with a `cc` entry produce at most one write | Go property test (testing/quick) (fake clock + fake store) |
| VP-020 | All non-target keys survive a write byte-identically | manual (cache-swap test, design §5.2) |
| VP-001 | Corrupt cost history (CP-C09/C10, EC-008) still yields ≥1 stdout byte and exit 0 — out of parity scope, never-blank per DI-008 | fault-injection table (exhaustive CP-*) |
| VP-012 | The named deviation this contract carries — exclusion id `OD-160` (EC-008 foreign-cache crash shapes out of parity scope) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-160` entry and its riding table test `TestForeignCacheShape_OD160_Vectors`, and the mutation test fails closed if that entry is dropped | property test (VP-012 `TestParityExclusions_ClosedSet` / `TestParityExclusions_MutationFailClosed`, go test) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-011 (cost history; format is status-line-owned, OD-124) |
| L2 Domain Invariants | DI-007 |
| Architecture Module | `internal/cost` history.go `Record` (design §2.3; BC-COMPONENT-MAP: internal/cost/history.go (throttled write) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:record_cost (SL:224-237); call site render_lane (SL:603-606) |
| Legacy contract | BC-SL-028 (P3r1 row 57; refined P3 deep r1) |
| Thresholds | T-022 (60 s throttle; derived, accepted in the OD-57 E-0 bulk row — it bounds cache-loss repair to under a minute, R-4 rationale, pass-4-deep-nfr-r7 §C) |
| Decisions | D4, D7-style format freeze for the cost history (OD-106 copies it at cutover), D15, OD-101 (cache dir), OD-124 |

## Related BCs (Recommended)

- BC-1.05.005 — composes with (runs immediately after)
- BC-1.05.006 — related to (numeric sid known difference)
- BC-1.05.009 — refined by (exact JSON bytes)
- BC-1.06.001 — depends on (load/save)
- BC-1.01.009 — related to (side-effect order)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#effect-step-script-design-doc-31-normative` — internal/cost/history.go (throttled write) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — cost history (filled by story-writer)

## VP Anchors (Recommended)

- VP-020 — throttle; VP-001 — never-blank/exit-0 under CP-C09/C10 corrupt history
- VP-012 — exclusion-closure cover for the named deviation `OD-160`


#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (record_cost (SL:224-237)) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: one-write-per-minute throttle `now - e.get("ts", 0) < 60` (SL:232)
- **documentation**: throttle rationale comment (review #11, SL:224)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | writes via the injected `Store` seam |
| **Global state access** | none |
| **Deterministic** | yes (given samples and a store fake) |
| **Thread safety** | Safe for concurrent use (store injected) |
| **Overall classification** | boundary |

Owning component `internal/cost` (BC-COMPONENT-MAP: cost/history.go (throttled write) - ARCH-03); the ARCH-00 package table classifies the package boundary - pure percentile math; writes go through the injected `Store` seam.
