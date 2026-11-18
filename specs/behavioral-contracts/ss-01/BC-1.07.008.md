---
document_type: behavioral-contract
level: L3
version: "1.1.7"
status: draft
producer: product-owner
timestamp: 2026-11-19T20:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md]
input-hash: "da8081c"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:__main__ guard over main_subagent (SL:1242-1245; sites SL:891, 894, 906, 878, 919)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.1.1 2026-11-18T07:00:00Z: adv-p3 remediation: huge-int overflow paths added to the catalog as CP-A04 (float(n), SL:878) and CP-A05 (now_ms - start, SL:919), five crash paths total (ADV-P3-C04); guard anchor cites the real ARCH-03 Interfaces heading (ADV-P3-C15)", "1.1.2 2026-11-18T08:00:00Z: pass-4 remediation: row-write stdout failure ruled stop-and-exit-0 with no degraded attempt, riding cp-x03 per OD-172 (ADV-P4-C13); stale LOCAL_MODEL_PREFIXES cite corrected to SL:902-903 (ADV-P4-C12)", "1.1.3 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C14/C11/C17) — refactoring note folds CP-A01..A05; stale ARCH-03 line anchor replaced with #statusline-guard; EC table reordered EC-001..009", "1.1.4 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C07) — crash-register count reconciled to 47 (error-taxonomy register: 4+17+7+3+11+5)", "1.1.5 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C12) — frontmatter template conformance: priority P0 added (prd.md S1.07), introduced normalized to the sibling \"0.1\" format", "1.1.6 2026-11-19T19:00:00Z: pass-7 remediation (ADV-P7-C12/C14) — VP-001/VP-003 row respelled to the actual promise (render-time faults end in the 29 degraded bytes; stdin faults absorb to zero bytes per BC-1.07.003; row-write EPIPE stops with no degraded attempt per EC-009/OD-172); EC-003's stray '{}'-less garble respelled to the falsy-values list", "1.1.7 2026-11-19T20:00:00Z: sync-check adv-p7 closure (SC-31) — Legacy-contract cell's pass-6 register count marked as history (47 at ADV-P6-C07; 48 since pass-7 CP-T09)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.008: CP-A01..A05 degrade to the 29-byte line, exit 0

## Description

Five catalogued crash paths are reachable only in `--subagent` mode (CP-A01..A03: P3r1 §A7;
CP-A04..A05: adv-p3, OD-156 + new ids). Like every render fault, they propagate out of
`main_subagent` (which catches only stdin faults) into the `__main__` top-level guard, which prints
the plain 29-byte line `\e[90mstatusline degraded\e[0m\n` — not JSON — and exits 0 (DI-008; the same
rung BC-1.01.001 pins for the main entry; ruled "like O2" in OD-156). Because the renderer prints only
after a complete render, no partial row output precedes the line.

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
   `backends[0].model_prefixes` (OD-123; legacy provenance: env `LOCAL_MODEL_PREFIXES`, SL:902-903)
   is non-empty: AttributeError (`'int' object has no attribute 'startswith'`) at SL:906 → degraded
   line, exit 0. Hylo reads the key through internal/config, never the legacy env (OD-05, ASM-003).
4. CP-A04 — a task's `tokenCount` a huge int (passes the isinstance/(>0) gate; |n| >= 2**1024 -
   2**970): OverflowError (`int too large to convert to float`) at `_fmt_tokens`'s `float(n)` (SL:878);
   the helper's except list covers only TypeError/ValueError → degraded line, exit 0.
5. CP-A05 — a task's `startTime` a huge int (running row, passes the isinstance/(>0) gate):
   OverflowError at `now_ms - start` (SL:919) → degraded line, exit 0.
6. stdout is exactly the 29 degraded bytes + LF (hex `1b 5b 39 30 6d` + `statusline degraded` +
   `1b 5b 30 6d 0a`); no partial rows, no JSON. Exit code 0.
7. Diagnostics to stderr only (never compared for parity, design §5.3).

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
| EC-003 | CP-A01 with falsy tasks (`0`, `""`, `null`, `{}`) | No crash: `or []` yields empty iteration (BC-1.07.003 EC-004) |
| EC-004 | Go panic unmapped to any CP site in subagent mode | `recover()` backstop prints the same 29 bytes, exit 0 (BC-1.01.001 EC-003 rule extended to the second entry point) |
| EC-005 | stdout closed / EPIPE while printing degraded line | OD-136 rule: swallow, exit 0 (named exclusion `cp-x03` extended to this entry point) |
| EC-006 | CP-A04: `{"tasks":[{"id":"a","status":"running","tokenCount":2**1024 - 2**970}]}` | Degraded line, exit 0 (gate passes; `float(n)` overflows) |
| EC-007 | CP-A05: `{"tasks":[{"id":"a","status":"running","startTime":2**1024 - 2**970}]}` | Degraded line, exit 0 (`now_ms - start` overflows) |
| EC-008 | Huge-int just below the threshold (`2**1024 - 2**970 - 1` as `tokenCount`) | Converts to the IEEE-754 maximum; tok bit renders; no degrade |
| EC-009 | stdout closed / EPIPE while printing the ROWS (success path) | `cp-x03` extends to `--subagent` row writes (owner ruling OD-172): stop writing and exit 0 — NO degraded-line attempt. This is a ruled deviation from legacy, where the BrokenPipe reaches the guard and the degraded print fails too (process exits 1); no new exclusion id (rides `cp-x03`) |

## Canonical Test Vectors

| Input (stdin + config) | Expected Output | Category |
|---|---|---|
| `{"tasks":123}`, any config | exactly `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 | error |
| `{"tasks":true}` | same 29 bytes, exit 0 | error |
| `{"tasks":[{"id":"a","status":["x"]}]}` | same 29 bytes, exit 0 | error |
| `{"tasks":[{"id":"a","model":123}]}`, `model_prefixes = [claude-sonnet]` | same 29 bytes, exit 0 | error |
| `{"tasks":[{"id":"a","model":123}]}`, `model_prefixes = []` | grey `123` row, exit 0 (no degrade) | edge-case |
| `{"tasks":[{"id":"a","status":"running","tokenCount":2**1024 - 2**970}]}` | same 29 bytes, exit 0 (CP-A04) | error |
| `{"tasks":[{"id":"a","status":"running","startTime":2**1024 - 2**970}]}` | same 29 bytes, exit 0 (CP-A05) | error |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`): all five CP sites reproduced
(TypeError x2, AttributeError x1, OverflowError x2) by calling `render_subagent_rows` directly; the
overflow threshold confirmed (`2**1024 - 2**970` raises, one less converts); the guard text/colors
are the SL:127-133 defaults (GREY `\e[90m`, RESET `\e[0m`) as pinned in BC-1.01.001.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-001, VP-003 | Every render-time fault (CP-A01..A05 and any unmapped panic) ends in exactly the 29 degraded bytes, exit 0 — stdin faults absorb silently to zero bytes (BC-1.07.003) and a row-write EPIPE stops with exit 0 and NO degraded attempt (EC-009, OD-172); never blank and never non-zero | go test -fuzz (extend VP-001's differential corpus with the `--subagent` stdin argv); VP-003 covers the write-failure leg |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (never blank, exit 0 — the degraded ladder top rung) |
| Architecture Module | `internal/statusline` guard (`guard.go`, design §2.2) shared with BC-1.01.001 |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py: guard (SL:1242-1245); CP sites SL:891, 894, 906, 878, 919 |
| Legacy contract | BC-SL-097 (CP-A01..A03 enumerated P3r1 §A7; CP-A04..A05 adv-p3, OD-156 + new ids; crash register 47 at ADV-P6-C07, 48 since pass-7 CP-T09) |
| Decisions | OD-155 (restores CP-A family to scope), OD-156 ("like O2": catalogued crash paths reproduce the 29-byte line), OD-136 (EPIPE), OD-172 (cp-x03 extends to row writes: stop and exit 0, no degraded attempt — ADV-P4-C13), D4 |

## Related BCs (Recommended)

- BC-1.01.001 — related to (same guard rung, same 29 bytes, main entry point)
- BC-1.07.005 — related to (CP-A02 site is the glyph lookup)
- BC-1.07.006 — related to (CP-A03 site is the model branch)
- BC-1.07.007 — related to (CP-A04/A05 sites are the token float(n) cast and the elapsed-clock base)
- BC-1.07.003 — related to (stdin faults absorb silently, by contrast)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` (Interfaces heading) — `guard.go`, shared with the main entry;
  `recover()` backstop mapped to `degradedLine` per ARCH-03 `#statusline-guard` and BC-COMPONENT-MAP
  (internal/statusline/guard.go — ARCH-03)

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-001, VP-003 — degraded output is exactly 29 bytes, exit 0 (corpus extended with `--subagent` stdin)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1242-1245; sites SL:891, 894, 906, 878, 919) |
| **Confidence** | high (CP sites reproduced under CPython 3.11.7, 2026-11-18) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **assertion**: direct `render_subagent_rows` fault injections (int tasks, list status, int model, huge-int tokenCount and startTime)
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

Go: fold CP-A01..A05 into the existing errDegraded predicate set so the VP-001 fuzz corpus reaches the
second entry point for free; each site gets a wrapped predicate per CV-08 (PR-21 remedy), and the
`--subagent` stdin corpus joins the nightly differential.
