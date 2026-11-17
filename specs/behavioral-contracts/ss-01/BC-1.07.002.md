---
document_type: behavioral-contract
level: L3
version: "1.0.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T03:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/statusline-target-design.md, specs/owner-decisions-log-2026-11-14.md]
input-hash: "c28cb1e"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "new contract (OD-155 config off switch; no legacy counterpart)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "new (OD-155)"
parity_class: OD-155 off switch
confidence: H
lifecycle_status: active
introduced: v0.2.2
modified: ["1.0.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-005 (off leg) + VP-009 (on-leg parity rows)"]
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
`statusline.subagent.enabled` defaults to `true`, which reproduces legacy bytes exactly
(DI-012-compliant named deviation when `false`). Setting it to `false` suppresses the entire subagent
render: Claude Code receives zero JSON lines and renders its own default row bodies (the CC contract
treats omitted rows as "keep the default body").

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 3.
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

## Invariants

1. `true` (explicit or defaulted) is behaviorally indistinguishable from pre-toggle legacy — the switch
   is purely subtractive.
2. The default lives in the `internal/config` schema with its rationale (D15: config over code); no
   hard-coded toggle in logic.
3. Boolean grammar errors are config errors (D4-EX-3 line, BC-2.02.001), not silent disables (DI-012:
   every deviation is named and tested; an unparseable value must not masquerade as `false`).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Key absent | Defaults to `true` (= legacy; backward compatibility with recorded parity fixtures) |
| EC-002 | `enabled = false` with well-formed tasks on stdin | Zero bytes, exit 0; CC shows its default row bodies |
| EC-003 | `enabled = false` with malformed stdin | Still zero bytes, exit 0 (config check precedes any stdin parse) |
| EC-004 | Invalid boolean spelling | D4-EX-3 config-error line per BC-2.02.001, exit 0 — NOT a fallback to true or false |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| defaults, stdin `{"tasks":[{"id":"a1","name":"explore","status":"running","model":"claude-sonnet-5-5","tokenCount":12345,"startTime":<now-125000>}]}`
 | BC-1.07.004 pinned row bytes, exit 0 | happy-path |
| `statusline.subagent.enabled = false`, same stdin | zero bytes, exit 0 | edge-case |
| `statusline.subagent.enabled = "yes"` (grammar-valid Python-ish truthy is NOT accepted unless the boolean grammar says so) | per BC-2.02.00x boolean grammar; never a silent disable | error |

Verified 2026-11-18 against CPython 3.11.7 for the legacy (enabled) half of each vector; the disabled
half has no legacy counterpart and is pinned by this contract alone (OD-155).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-005 | enabled=false: for every stdin byte string the render is zero JSON lines, exit 0 (DI-012 named deviation, default true = legacy) | fuzz over stdin corpus |
| VP-009 | enabled=true: stepwise stdout/exit/cache parity vs the CPython oracle over the committed subagent corpus family rows | manual corpus comparison (Tier A) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 (named deviation: the off switch itself), DI-007 (no ledger access) |
| Architecture Module | `internal/config` (key + default + rationale), `internal/statusline` (early-out branch) |
| Stories | TBD (filled by story-writer) |
| Source | new contract; OD-155 row in `specs/owner-decisions-log-2026-11-14.md` |
| Legacy contract | none (OD-155 addition; legacy had no toggle) |
| Decisions | OD-155 (supersedes OD-14 a), D15 (config over code), DI-012 |

## Related BCs (Recommended)

- BC-1.07.001 — composes with (checked at routing, before stdin work)
- BC-1.07.004 — related to (disabled output differs from the empty-tasks output only in stdin tolerance, EC-003)
- BC-2.01.001 — related to (key + default + rationale in the schema)

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
