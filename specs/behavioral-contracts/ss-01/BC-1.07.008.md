---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T02:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md]
input-hash: "443be16"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:__main__ guard over main_subagent (SL:1242-1245; sites SL:891, 894, 906)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.2.2
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.008: CP-A01..A03 degrade to the 29-byte line, exit 0

## Description

Three catalogued crash paths are reachable only in `--subagent` mode (P3r1 §A7). Like every render
fault, they propagate out of `main_subagent` (which catches only stdin faults) into the `__main__`
top-level guard, which prints the plain 29-byte line `\e[90mstatusline degraded\e[0m\n` — not JSON —
and exits 0 (DI-008; the same rung BC-1.01.001 pins for the main entry; ruled "like O2" in OD-156).
Because the renderer prints only after a complete render, no partial row output precedes the line.

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 3.
2. Switch on (BC-1.07.002); renderer entered (BC-1.07.001); stdin parsed or absorbed (BC-1.07.003).

## Postconditions

1. CP-A01 — `tasks` truthy and not iterable (number, `true`): TypeError at the `for task in
   d.get("tasks") or []` site (SL:891) → degraded line, exit 0.
2. CP-A02 — a task's `status` unhashable (list/object): TypeError at `_SUB_GLYPH.get(status, ...)`
   (SL:894) → degraded line, exit 0.
3. CP-A03 — a task's `model` truthy and not a str while the configured prefix list
   `backends[0].model_prefixes` (OD-123; legacy provenance: env `LOCAL_MODEL_PREFIXES`, SL:903-905)
   is non-empty: AttributeError (`'int' object has no attribute 'startswith'`) at SL:906 → degraded
   line, exit 0. Hylo reads the key through internal/config, never the legacy env (OD-05, ASM-003).
4. stdout is exactly the 29 degraded bytes + LF (hex `1b 5b 39 30 6d` + `statusline degraded` +
   `1b 5b 30 6d 0a`); no partial rows, no JSON. Exit code 0.
5. Diagnostics to stderr only (never compared for parity, design §5.3).

## Invariants

1. The degraded output is the shared guard constant, byte-identical to BC-1.01.001's — one ladder, one
   rung text (DI-008).
2. The line is NOT valid JSON; CC consumes it as a row-body miss and keeps default bodies (parity-
   observed legacy outcome).
3. Single write per refresh: rows or degraded line, never both (no partial output, print-after-render).
4. Stdin absorption (BC-1.07.003) happens inside the renderer and never reaches this rung; only
   render-time faults do.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Fault on the 3rd task of 5 | Degraded line only; tasks 1-2 bytes never reach stdout (buffer-then-print) |
| EC-002 | CP-A03 with prefixes empty | No crash: grey `123` segment renders (truthy non-str model only faults when the pill branch calls startswith) |
| EC-003 | CP-A01 with falsy tasks (`0`, `""`, `null`, `{}`-less) | No crash: `or []` yields empty iteration (BC-1.07.003 EC-004) |
| EC-004 | Go panic unmapped to any CP site in subagent mode | `recover()` backstop prints the same 29 bytes, exit 0 (BC-1.01.001 EC-003 rule extended to the second entry point) |
| EC-005 | stdout closed / EPIPE while printing degraded line | OD-136 rule: swallow, exit 0 (named exclusion `cp-x03` extended to this entry point) |

## Canonical Test Vectors

| Input (stdin + config) | Expected Output | Category |
|---|---|---|
| `{"tasks":123}`, any config | exactly `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 | error |
| `{"tasks":true}` | same 29 bytes, exit 0 | error |
| `{"tasks":[{"id":"a","status":["x"]}]}` | same 29 bytes, exit 0 | error |
| `{"tasks":[{"id":"a","model":123}]}`, `model_prefixes = [claude-sonnet]` | same 29 bytes, exit 0 | error |
| `{"tasks":[{"id":"a","model":123}]}`, `model_prefixes = []` | grey `123` row, exit 0 (no degrade) | edge-case |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`): all three CP sites reproduced
(TypeError ×2, AttributeError ×1) by calling `render_subagent_rows` directly; the guard text/colors
are the SL:127-133 defaults (GREY `\e[90m`, RESET `\e[0m`) as pinned in BC-1.01.001.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-001, VP-003 | Every fault routed to the subagent renderer ends in exactly the 29 degraded bytes, exit 0, never blank and never non-zero | go test -fuzz (extend VP-001's differential corpus with the `--subagent` stdin argv); VP-003 covers the write-failure leg |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (never blank, exit 0 — the degraded ladder top rung) |
| Architecture Module | `internal/statusline` guard (`guard.go`, design §2.2) shared with BC-1.01.001 |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py: guard (SL:1242-1245); CP sites SL:891, 894, 906 |
| Legacy contract | BC-SL-097 (CP-A01..A03 enumerated P3r1 §A7; count fixed at 43 total) |
| Decisions | OD-155 (restores CP-A family to scope), OD-156 ("like O2": catalogued crash paths reproduce the 29-byte line), OD-136 (EPIPE), D4 |

## Related BCs (Recommended)

- BC-1.01.001 — related to (same guard rung, same 29 bytes, main entry point)
- BC-1.07.005 — related to (CP-A02 site is the glyph lookup)
- BC-1.07.006 — related to (CP-A03 site is the model branch)
- BC-1.07.003 — related to (stdin faults absorb silently, by contrast)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-guard` — guard shared with the main entry
  (BC-COMPONENT-MAP: internal/statusline/guard.go — ARCH-03)

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-001, VP-003 — degraded output is exactly 29 bytes, exit 0 (corpus extended with `--subagent` stdin)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1242-1245; sites SL:891, 894, 906) |
| **Confidence** | high (CP sites reproduced under CPython 3.11.7, 2026-11-18) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **assertion**: direct `render_subagent_rows` fault injections (int tasks, list status, int model)
- **guard clause**: `except Exception:` around `sys.exit(main_subagent())` (SL:1243-1245)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | writes stdout |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | n.a. (single-shot process) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Go: fold CP-A01..A03 into the existing errDegraded predicate set so the VP-001 fuzz corpus reaches the
second entry point for free; each site gets a wrapped predicate per CV-08 (PR-21 remedy), and the
`--subagent` stdin corpus joins the nightly differential.
