---
document_type: behavioral-contract
level: L3
version: "1.0.7"
status: draft
producer: product-owner
timestamp: 2026-11-18T08:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/statusline-target-design.md, specs/owner-decisions-log-2026-11-14.md]
input-hash: "7ad8a24"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "new contract (OD-155 config off switch; no legacy counterpart)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "new (OD-155)"
parity_class: "byte-exact"
confidence: H
priority: P0
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.0.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-005 (off leg) + VP-009 (on-leg parity rows)"
  - "1.0.2 2026-11-18T07:00:00Z: adv-p3 remediation: OD-168 config-error behavior in this mode pinned (zero bytes stdout, diagnostic stderr — ADV-P3-D18); invalid-boolean vector given concrete bytes (ADV-P3-C20)"
  - "1.0.3 2026-11-18T08:00:00Z: pass-4 remediation: invalid-boolean vector re-pinned to grammar-invalid `on` with the canonical reason string and from-ENVNAME suffix (ADV-P4-C01; `yes` resolves true per BC-2.01.005)"
  - "1.0.4 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C16) — parity_class brought into the closed vocabulary: byte-exact, scoped per the BC-INDEX parity-class note to the ENABLED half (default true = legacy rows); the disabled OD-155 off-switch half is new behavior contracted here, not a parity class (the ruled off-switch and OD-168 behavior stay named in the body)"
  - "1.0.5 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C12) — frontmatter template conformance: priority P0 added (prd.md S1.07), introduced normalized to the sibling \"0.1\" format"
  - "1.0.6 2026-11-20T12:00:00Z: pass-8 residual sweep (task 9) — ASSUMP-107-1 capture timing respelled per OD-192: 'before Phase 3' -> 'before Phase 2 writes the S1.07 stories'; body wording only"
  - "1.0.7 2026-11-20T18:00:00Z: pass-9 remediation (ADV-P9-C02/C05) — frontmatter modified list repaired to block style (lost closing quote restored); enabled=false recast as ruled new behavior (OD-155), not a DI-012 named deviation, in Description, VP-005 row and Traceability — agrees with VP-005"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.002: `statusline.subagent.enabled` off switch (default true = legacy)

## Description

Owner ruling OD-155 restores the agent-panel rows with a config off switch. The boolean config key
`statusline.subagent.enabled` defaults to `true`, which reproduces legacy bytes exactly. Setting it
to `false` is ruled new behavior (OD-155), not a DI-012 parity exclusion — DI-012's exclusion set is
closed and lists no id for it (VP-005). When `false` it suppresses the entire subagent
render: Claude Code receives zero JSON lines and renders its own default row bodies (the CC contract
treats omitted rows as "keep the default body").

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 2 writes the S1.07 stories (OD-192).
   (With the switch off, compatibility does not matter — nothing is emitted.)
2. Configuration resolved per BC-2.01.001; the key participates in the typed-boolean grammar
   (BC-2.02.00x classes) like every other `statusline.*` boolean.

## Postconditions

1. Default (`enabled = true`, absent key, or any spelling resolving true): output is byte-identical to
   legacy `main_subagent` for the same stdin/env (BC-1.07.003..008).
2. `enabled = false`: stdout receives zero bytes, exit code 0, regardless of stdin content; stdin is
   not required to be valid JSON in this path (the renderer is not entered).
3. The key affects only the subagent entry point (BC-1.07.001 routing); the main render is unaffected.
4. With the switch off, no cache write, no env read other than config resolution, and no ledger access
   occurs (DI-007).
5. Config-resolution error while routed to the subagent entry (any invalid value, e.g. an invalid
   boolean spelling): stdout receives ZERO bytes and the `hylo: config error: <key>=<value> (<reason>)`
   diagnostic goes to stderr (OD-168); the grey config-error line of BC-2.02.001 is NOT printed in this
   mode because it is not NDJSON and would corrupt the agent-panel row stream. Exit code 0 carries over
   from the D4-EX-3 contract (OD-168 rules the byte routing, not the exit path).

## Invariants

1. `true` (explicit or defaulted) is behaviorally indistinguishable from pre-toggle legacy — the switch
   is purely subtractive.
2. The default lives in the `internal/config` schema with its rationale (D15: config over code); no
   hard-coded toggle in logic.
3. Boolean grammar errors are config errors (BC-2.02.001 class, D4-EX-3), not silent disables (DI-012:
   an unparseable value must not masquerade as `false`); in this mode the diagnostic is rerouted to
   stderr with zero stdout bytes (OD-168).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Key absent | Defaults to `true` (= legacy; backward compatibility with recorded parity fixtures) |
| EC-002 | `enabled = false` with well-formed tasks on stdin | Zero bytes, exit 0; CC shows its default row bodies |
| EC-003 | `enabled = false` with malformed stdin | Still zero bytes, exit 0 (config check precedes any stdin parse) |
| EC-004 | Invalid boolean spelling (e.g. `on`) | Config error (D4-EX-3 boolean class, BC-2.02.001 format; reason vocabulary entry `not a boolean (true\|false\|1\|0\|yes\|no)` byte-exact): stdout receives zero bytes; the `hylo: config error: <key>=<value> (<reason>) [from <ENVNAME>]` diagnostic goes to stderr; exit 0 — NOT a fallback to true or false (OD-168). Grammar-valid spellings (`yes`, `1`, `true`, …) resolve true and are NOT errors (BC-2.01.005: `true`, `1`, `yes` → true) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| defaults, stdin `{"tasks":[{"id":"a1","name":"explore","status":"running","model":"claude-sonnet-5-5","tokenCount":12345,"startTime":<now-125000>}]}` | BC-1.07.004 pinned row bytes, exit 0 | happy-path |
| `statusline.subagent.enabled = false`, same stdin | zero bytes, exit 0 | edge-case |
| `statusline.subagent.enabled = "yes"`, same stdin | renders rows: `yes` is a grammar-valid true spelling (BC-2.01.005: `true`, `1`, `yes` → true) — BC-1.07.004 pinned row bytes, exit 0 (NOT a config error) | happy-path |
| env `HYLO_STATUSLINE_SUBAGENT_ENABLED=on`, same stdin | zero bytes on stdout; stderr `hylo: config error: statusline.subagent.enabled=on (not a boolean (true\|false\|1\|0\|yes\|no)) [from HYLO_STATUSLINE_SUBAGENT_ENABLED]`; exit 0 (OD-168 byte routing; reason string byte-exact per BC-2.02.001's vocabulary, `from` suffix per BC-2.02.001 PC6) | error |

Verified 2026-11-18 against CPython 3.11.7 for the legacy (enabled) half of each vector; the disabled
half has no legacy counterpart and is pinned by this contract alone (OD-155).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-005 | enabled=false: for every stdin byte string the render is zero JSON lines, exit 0 (ruled new behavior, not a DI-012 parity exclusion; default true = legacy) | fuzz over stdin corpus |
| VP-009 | enabled=true: stepwise stdout/exit/cache parity vs the CPython oracle over the committed subagent corpus family rows | manual corpus comparison (Tier A) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 (no ledger access); DI-012 cited for the pinned-quirk vocabulary only — the off switch is ruled new behavior (OD-155), not a DI-012 parity exclusion (VP-005) |
| Architecture Module | `internal/config` (key + default + rationale), `internal/statusline` (early-out branch) |
| Stories | TBD (filled by story-writer) |
| Source | new contract; OD-155 row in `specs/owner-decisions-log-2026-11-14.md` |
| Legacy contract | none (OD-155 addition; legacy had no toggle) |
| Decisions | OD-155 (supersedes OD-14 a), D15 (config over code), DI-012; adv-p3: OD-168 config-error byte routing (ADV-P3-D18) |

## Related BCs (Recommended)

- BC-1.07.001 — composes with (checked at routing, before stdin work)
- BC-1.07.004 — related to (disabled output differs from the empty-tasks output only in stdin tolerance, EC-003)
- BC-2.01.001 — related to (key + default + rationale in the schema)
- BC-2.02.001 — related to (D4-EX-3 diagnostic format; in this mode rerouted to stderr per OD-168)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — switch consumed at entry; config key owned by ARCH-02 schema

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-005 (enabled=false zero-lines totality)
- VP-009 (enabled=true corpus parity rows)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | new contract (OD-155); legacy counterpart is the unguarded `main_subagent` (SL:928-936) |
| **Confidence** | high for the enabled half (oracle-pinned); disabled half ruled, not extracted |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **owner ruling**: OD-155 "(a) reopen OD-14 (a): port `--subagent` / subagentStatusLine agent-panel
  rows in P1 now, before Phase 2 stories, with a config off switch"

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (pure config predicate + early-out) |
| **Global state access** | reads resolved config |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (read-only config) |
| **Overall classification** | pure |

#### Refactoring Notes

Go: `cfg.Statusline.Subagent.Enabled` (default true); the early-out returns before constructing the
subagent `Env`, so a disabled run costs one config load. Record the default's rationale next to the
schema entry (D15).
