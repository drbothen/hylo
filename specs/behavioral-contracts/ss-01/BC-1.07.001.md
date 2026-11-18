---
document_type: behavioral-contract
level: L3
version: "1.0.6"
status: draft
producer: product-owner
timestamp: 2026-11-18T08:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md, semport/hylo-legacy/statusline-target-design.md, specs/owner-decisions-log-2026-11-14.md]
input-hash: "a3e067c"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:__main__ dispatch (SL:1240-1241)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.0.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-002 (catalog lists this BC)", "1.0.2 2026-11-18T07:00:00Z: adv-p3 remediation: routing ruling on ADV-P3-A01/D05 sharpened (any index incl. after '--', regardless of other flags); subagent.go placement cited per ARCH-03:133-135 (ADV-P3-C15); argv example clarified (ADV-P3-C22)", "1.0.3 2026-11-18T08:00:00Z: pass-4 remediation: stale anchor labels refreshed — ARCH-03:137-138 for the subagent.go placement and legacy/claude-dgx:177 for the launcher wiring (ADV-P4-C12)", "1.0.4 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C11) — stale ARCH-03 line anchors replaced with the stable fragment #subagent (second drift after ADV-P4-C12; call 19)", "1.0.5 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C12) — frontmatter template conformance: priority P0 added (prd.md S1.07), introduced normalized to the sibling \"0.1\" format", "1.0.6 2026-11-19T19:30:00Z: pass-7 remediation (ADV-P7-C06) — stale BC-4.01.002 cross-references refreshed: its EC-004 no longer carries the superseded \"positional data\" reading (aligned v1.1.3), so EC-003 and Related BCs now state the agreement"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.001: `--subagent` in argv selects the subagent renderer before main

> Byte notation: `\e` = ESC (0x1B). Restored to P1 scope by owner ruling OD-155 (2026-11-17), which
> supersedes OD-14 (a); Claude Code 2.1.326 restored the `subagentStatusLine` setting.

## Description

The status-line binary is single-shot with two entry points. When the exact argument `--subagent`
appears anywhere in `sys.argv[1:]`, the process routes to the subagent panel renderer (`main_subagent`)
and `main()` never runs; otherwise the main render runs. The check is an exact string membership test,
not flag parsing, and it precedes every other mode decision.

## Preconditions

1. The process is invoked once per refresh by the launcher with the subagent stdin contract
   (NDJSON-style single JSON object on stdin; output one JSON line per visible row).
2. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed (`{"columns": N, "tasks": [...]}`; per task
   `id, name, agentType, status, description, label, startTime(ms), model, tokenCount`); to be verified
   by a capture before Phase 3.
3. All other argv elements (if any) are ignored by this contract; unknown-flag handling (OD-112) is
   BC-4.01.002's concern only for argv routed to the main render.

## Postconditions

1. If `--subagent` is an exact element of `argv[1:]`: the subagent renderer produces all stdout, the
   main render (`main()`) never executes, and no session cache is read or written (DI-007 — no ledger,
   transcript or metrics access in this mode).
2. If `--subagent` is absent: the main render runs (BC-1.01.001 path); `--subagent` has no effect on it.
3. Match rule: only the exact element `--subagent` matches; substring, prefixed, or suffixed
   spellings (`--subagent=1`, `-subagent`, `subagent`) are NOT matches, and no element of
   `argv[1:]` is parsed beyond this membership test.
4. Position is irrelevant: `--subagent` matches at any index of `argv[1:]`, including after a
   `--` separator and alongside any other flags — membership in `argv[1:]` is the whole rule
   (adv-p3 owner ruling on ADV-P3-A01/D05: routing is legacy parity, SL:1240).

## Invariants

1. Routing happens before configuration-derived rendering; the mode decision reads argv only.
2. The subagent renderer returns 0 to the `__main__` guard on success; the guard still backs every
   fault (BC-1.07.008).
3. Exactly one of {main render, subagent render} executes per process (DI-008 ladder entry order).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `--subagent` given twice | Single routing decision; behavior identical to one occurrence |
| EC-002 | `--subagent` together with other unknown flags | Still routes to the subagent renderer; unknown flags are not validated in this mode |
| EC-003 | `--subagent` after a `--` separator (`hylo statusline -- --subagent`) | Routes to the subagent renderer: membership in `argv[1:]` holds at any index (ADV-P3-A01/D05 ruling); BC-4.01.002's EC-004 states the same routing (aligned, v1.1.3+ — no superseded reading remains) |
| EC-004 | Launcher wiring | `claude-dgx` launches `hylo statusline --subagent` (legacy/claude-dgx:177 wires the CC `subagentStatusLine` command `--subagent`); the captured CC stdin payload must be verified per ASSUMP-107-1 before Phase 3 |
| EC-005 | Empty argv (no args at all) | Main render (BC-1.01.001) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `argv = ["statusline", "--subagent"]`, stdin `{"tasks":[]}` | exit 0, zero bytes on stdout (renderer ran; main did not) | happy-path |
| `argv = ["statusline"]`, stdin main-contract JSON | main render bytes (BC-1.01.001 row 1), no subagent renderer | happy-path |
| `argv = ["statusline", "--subagent=1"]` | NOT routed in legacy (membership test fails); main render runs; under Go this argv reaches BC-4.01.002's unknown-flag line, exit 0 (OD-112) | edge-case |
| `argv = ["statusline", "--", "--subagent"]`, stdin `{"tasks":[]}` | routed to the subagent renderer (membership at index 2): zero bytes on stdout, exit 0 (ADV-P3-A01/D05 ruling) | edge-case |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`): membership semantics read directly from
SL:1240-1241 (`"--subagent" in sys.argv[1:]`); routing order from SL:1239-1244.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-002 | Dispatcher fuzz (argv vectors incl. the BC-1.07.001 routing rows) asserts exact-member `--subagent` at any index routes to the subagent renderer before flag handling and every non-matching form falls to the main path — realizing the exactly-one-renderer invariant observationally over the fuzzed argv space | fuzz (`go test -fuzz`, NUL-decoded argv) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 (no ledger access in this mode), DI-008 (exit 0 under the guard) |
| Architecture Module | `internal/statusline/subagent.go` (placed by ARCH-03 `#subagent`; hosts BC-1.07.001..008, dispatched per ARCH-01) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py: `__main__` dispatch (SL:1240-1241); launcher `legacy/claude-dgx:177` |
| Legacy contract | BC-SL-097 (P3r2 §A7; P3r4 §7.3; restored to scope OD-155) |
| Decisions | OD-155 (supersedes OD-14 a), adv-p3 routing ruling on ADV-P3-A01/D05 (membership is the whole rule), OD-112 (handoff), D4 (byte parity), tension T8 (design §8) |

## Related BCs (Recommended)

- BC-1.07.003 — composes with (stdin ingestion inside the renderer)
- BC-1.07.004 — composes with (output framing)
- BC-1.07.008 — related to (faults inside the renderer end in the 29-byte line)
- BC-4.01.002 — related to (its EC-004 defers to this routing by agreement: an occurrence after `--` or beside other flags routes here; the "positional data" reading it once held was aligned away in v1.1.3 — ADV-P7-C06)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#subagent` — `subagent.go` hosts the OD-155 agent-panel contracts; second entry point dispatched per ARCH-01

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-002 (dispatcher fuzz: exact-member `--subagent` routing + unknown-flag complement)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1240-1241) |
| **Confidence** | high (direct code read; membership semantics pinned by CPython 3.11.7 run 2026-11-18) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **guard clause**: `if "--subagent" in sys.argv[1:]: sys.exit(main_subagent())` before `sys.exit(main())`
- **assertion**: routing order read from the `__main__` block (SL:1239-1244)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | delegates to renderer (stdout) |
| **Global state access** | reads `sys.argv` |
| **Deterministic** | yes |
| **Thread safety** | n.a. (single-shot process) |
| **Overall classification** | effectful shell (router) |

#### Refactoring Notes

Go: `statusline.Run(argv)` checks `slices.Contains(os.Args[1:], "--subagent")` before `Main()`;
stdlib `flag` must NOT own this decision (ExitOnError would exit 2, contradicting DI-008 — design T8).
