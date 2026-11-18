---
document_type: behavioral-contract
level: L3
version: "1.3.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T18:40:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "19605e7"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_finish_turn, _mix_counts (SL:988-996, 1073-1079, 1150-1153)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-103"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.2.1 2026-11-17: dropped uncited DI-012 (byte-exact, no exclusion entry; ADV-P2-C11)"
  - "1.2.2 2026-11-19T14:00:00Z: pass-6 residual sweep (ADV-P6-A2-07) — Decisions row states both amended OD-32 conditions (numeric cur.t0 AND non-numeric cur.out, BC-1.03.020)"
  - "1.2.3 2026-11-19T23:59:00Z: pass-8 remediation (ADV-P8-C02) — the verbatim round-trip bounded by the mix-save encoder boundary (EC-004 added, oracle end-to-end 2026-11-18: transcript-borne worst case payload doc 993 saves cleanly — the 993 decode edge binds below the save boundary, so no reachable save failure, no temp leak, no per-refresh repeat); PC5 and the VP-029 row state the bound"
  - "1.3.0 2026-11-20T18:00:00Z: pass-9 remediation (orchestrator call 1) — the verbatim round-trip claim narrowed to the measured asymmetry: mix-cache save budget 994 against load budget 991, so a saved document of depth 992..994 fails reload, is treated as absent, and is re-read from offset 0 and rewritten every refresh (PC5, EC-004, VP-029 row; session/git/cost keep equality; depth unit stated once: total nesting of the saved document, top-level object = 1)"
  - "1.3.1 2026-11-21T12:00:00Z: pass-10 remediation (ADV-P10-C08; orchestrator call 11) — PC5 and EC-004 qualified by the pass-10 measurement: constant size and totals hold only while the transcript fits in one 524,288-byte read step; above it the shallow step-1 and deep full-parse states alternate with period 2 (608,960-B transcript measured: size field cycles 524,202 <-> 608,960, on-disk 2,544 <-> 4,520 B, shallow state re-saved byte-identical, file rewritten every refresh, exit 0)"
  - "1.3.2 2026-11-24T12:00:00Z: pass-13 remediation (ADV-P13-C04; orchestrator call 12) — PC5 closing parenthesis rewritten from the measured session-cache leg: session cache saves cleanly at every stdin-reachable depth (decode edge 993; one deeper degrades the parse to an empty dict, exit 0) but reloads only while the saved document nests at most 991 levels, so saved depths 992..993 are treated as absent on the following refresh; measured with the legacy oracle in an isolated temporary HOME and cwd (CPython 3.11.7, DGX_SL_ROWS=1, TZ=UTC, empty cache); the unmeasured equal-budget claim for session is gone, git and cost-history keep the former sentence"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.021: cur with t0 null and non-numeric out kept verbatim

## Description

When the CP-T05 shape occurs while `lu` is still null (no timed user line yet), the W-predicate does not hold, so
both legacy and hylo process the line: they open a turn `{"id": …, "t0": null, "t1": …, "out": "abc"}` and persist
it. This is a normal, crash-free state: `finish` returns early on `t0 == null` before reading `out`. hylo must store
`cur.out` as a raw JSON value, write it back verbatim, and must not apply the OD-32 reader rule to it.

## Preconditions

1. A timed assistant line with a truthy id opens a new turn while `lu` is null, and its `usage.output_tokens` is a
   truthy non-number (or `cur` with `t0` null and non-numeric `out` is loaded from a cache).

## Postconditions

1. `cur = {"id": <id>, "t0": null, "t1": <t>, "out": <raw value>}` is held and written verbatim (`"out": "abc"`,
   `["x"]`, `{"a": 1}`), key order `id, t0, t1, out`.
2. Later lines of the same id move `t1` only; `out` stays the raw value.
3. Closing the turn (newer id, real user prompt, timed system line) calls `finish`, which returns `lr` unchanged
   because `t0` is null; `cur` becomes null; no error.
4. On load, the OD-32 reader rule (BC-1.03.020) does **not** fire because `t0` is not a number.
5. The Go mix-cache type stores `cur` (and `cur.out`) as `pyfmt.Value`, never a typed number. Raw nesting is
   bounded in practice on the SAVE side: the transcript decode edge (993 total document depth, BC-1.03.004
   EC-009) caps any input-borne value below the mix-save encoder boundary (measured end-to-end 2026-11-18:
   transcript-borne worst case — payload document depth 993 — saves cleanly; boundary 994 saves / 995 fails at
   the legacy frame shape, ADV-P8-C02). Depths are the total nesting of the saved document (top-level object =
   1). The round trip is ASYMMETRIC for the mix cache — the measured exception to the equal-budget law
   (BC-5.02.006): a saved cache of document depth 992..994 fails to RELOAD at the 991 load budget; legacy then
   treats the cache as absent ({}), re-reads the transcript from offset 0 and rewrites the cache every refresh
   while the deep payload persists (file rewritten every refresh, no temp leak, exit 0;
   orchestrator-measured pass-9). The pass-9 constant-size phrasing holds only while the transcript fits in one
   524,288-byte read step (pass-10 measurement, ADV-P10-C08): above it, each reload failure resets the offset to
   0 and the parser advances one step per refresh, so the saved cache ALTERNATES between the shallow step-1
   state and the deep full-parse state — measured (CPython 3.11.7, isolated temp HOME/cwd; 608,960-B transcript =
   4,000 152-B filler assistant lines plus a last line whose 990-deep nested `message.id` lands at saved doc
   depth 993; simulated first step cut at byte 524,202): refresh 1 saves the shallow state (on-disk 2,544 B,
   size field 524,202), refresh 2 parses step 2 and saves the deep state (on-disk 4,520 B, size field 608,960),
   refresh 3's reload of the deep cache raises RecursionError, resets and re-saves the shallow state
   byte-identical to refresh 1 (sha-verified), and the two states alternate with period 2, the file rewritten
   every refresh, exit 0, normal render. hylo reproduces the same cycle. (Session-cache budgets, measured
   2026-11-18 with the legacy oracle (CPython 3.11.7, isolated temporary HOME and cwd, DGX_SL_ROWS=1,
   TZ=UTC, empty cache): stdin whose `rate_limits` value carries the whole stdin document to depth 993 —
   the deepest depth the stdin parse accepts (a document one level deeper degrades the stdin parse to an
   empty dict, exit 0) — SAVES the session cache cleanly, and the next refresh FAILS to reload it: the
   cache reloads only while the saved document nests at most 991 levels (a saved depth-991 document
   reloads; saved depths 992..993 do not), so a stdin at the decode edge writes a cache that is treated
   as absent on the following refresh and the plan state is lost, re-failing into the same shape every
   refresh while the deep stdin persists. Git and cost-history caches keep Save budget = Load budget.)

## Invariants

1. `finishTurn` checks `cur == null/empty` and `t0 == null` before reading `out` (legacy order, SL:991-993).
2. Legacy and hylo write identical bytes for this state (byte-exact; no exclusion entry).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Continuation line of the same id, no closer | `t1` updated, `out` still `"abc"` |
| EC-002 | Then a timed system line | `cur` null, `lr` unchanged (null), no crash |
| EC-003 | Applying the original (unamended) OD-32 rule here | would give `"out": 900` after a continuation — **wrong** (diverges from legacy); prohibited |
| EC-004 | Deeply nested `message.id` (timed assistant line without usage; line doc depth 992–993, list- or dict-nested) rides `cur.id` verbatim into the mix-cache payload | end-to-end oracle 2026-11-18 (CPython 3.11.7, isolated temp HOME/cwd): the payload SAVES cleanly — the mcache holds the nested id, exit 0, no RecursionError, no leaked temp. Pass-9 adds the next-refresh leg (orchestrator-measured): the saved depth-992..994 cache FAILS to reload at the 991 load budget, is treated as absent, and is re-read from offset 0 and rewritten every refresh while the deep payload persists (file rewritten every refresh, no temp leak, exit 0 — not a refresh-2 no-op); the constant-size qualifier holds only while the transcript fits in one 524,288-byte read step — above it the shallow step-1 and deep full-parse states alternate with period 2 (ADV-P10-C08; BC-1.03.021 PC5) The mix-save encoder boundary sits above the 993 decode ceiling (frame-shape replica: payload doc 994 saves / 995 fails), so a transcript-borne value cannot trip the save budget (ADV-P8-C02 save side; pass-9 load side, BC-1.03.021 PC5) |

## Canonical Test Vectors

Lines as in BC-1.03.019 (A2', B5, W5) and BC-1.03.020 (A9, S11); TZ=UTC; no cache. Re-pinned 2026-11-15 with the
legacy oracle (hylo must produce identical bytes).

| Input | Expected Output | Category |
|-------|----------------|----------|
| refresh 1: `A2', B5, W5` | `{"size": 669, "res": 0, "conv": 9, "think": 0, "tin": 220, "tout": 15, "c_wr": 200, "c_rd": 0, "mixv6": 1, "c_in": 20, "rb": 0, "pp": 110, "ids": ["msg_A", "msg_B"], "lr": null, "lu": null, "cur": {"id": "msg_A", "t0": null, "t1": 1794650408.0, "out": "abc"}}` | happy-path |
| refresh 2: append `A9` | `{"size": 921, …, "conv": 12, …, "cur": {"id": "msg_A", "t0": null, "t1": 1794650410.0, "out": "abc"}}` | edge-case |
| refresh 3: append `S11` | `{"size": 1005, …, "conv": 12, …, "lr": null, "lu": null, "cur": null}` (no crash) | edge-case |
| BC-1.03.019 row 14 (T05− lu none, with U9) | `"lr": null`, `"cur": null`, byte-exact with legacy | edge-case |

(`…` elides fields equal to refresh 1's.)

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | `cur.out` round-trips verbatim through load/save for any JSON value whose SAVED document nests at most 991 levels (the load budget); saved payload depths 992..994 save but fail to reload — the measured per-refresh rewrite loop (PC5, orchestrator-measured pass-9); depths beyond 994 are unreachable from input because the 993 decode edge binds first (ADV-P8-C02) | Go property test (testing/quick, generator capped at saved-document depth 991) |
| VP-029 | `finishTurn` never errors when `t0` is null | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Source | legacy/dgx_statusline.py:_finish_turn (SL:988-996), _mix_counts (SL:1073-1079, 1150-1153) |
| Legacy contract | BC-SL-103 (pass-3 r4 §1.2; confirmed r5) |
| Parity class | byte-exact (design §8: BX, OD-32) |
| Decisions | OD-32 (amended: the reader rule fires only when `cur.t0` is numeric AND `cur.out` is non-numeric — both conditions, BC-1.03.020); ruling b (exact cache format) |
| Architecture Module | `internal/statusline/mixcache.go`, `transcript_turn.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.020 — related to: the reader rule must not fire here
- BC-1.03.010 — depends on: `finish` order
- BC-1.03.018 — related to: CP-T05 requires `lu` set

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/mixcache.go (t0 null, out verbatim) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — mix cache

## VP Anchors (Recommended)

- VP-029 — raw `cur.out` round-trip

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:988-996, 1073-1079, 1150-1153) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if not cur or cur.get("t0") is None: return lr` (SL:991-992)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed beyond holding `cur` as `pyfmt.Value`.
