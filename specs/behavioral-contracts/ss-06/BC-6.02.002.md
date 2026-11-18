---
document_type: behavioral-contract
level: L3
version: "1.2.3"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "87101f4"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (new contract, no legacy source)"
subsystem: "SS-06"
capability: "CAP-009"
legacy_id: "new"
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.2.3 2026-11-18: ADV-P4 remediation D25 - captured stdin moved to a byte-exact sibling file stdin.bin (never a JSON member); mode: main/subagent marker added"
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D24: captured stdin snapshots spliced byte-level (no re-serialization); parse-required captures are build errors"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.02.002: stdin-sequence replay of captured sessions: ordered snapshots, clock advanced per step

## Description

A captured session is replayed as an ordered sequence of status line refreshes, not as
single frames (OD-107). Each step supplies that refresh's stdin snapshot, the frozen
instant at which it was captured, and the transcript as it stood at that moment. The
oracle and Go run step by step, in order, against their own persistent cache
directories. Cache state therefore carries across steps exactly as it does in a real
session: TTLs, rate-limit smoothing, mix-cache offsets and cost history. Both sides
are compared after every step (BC-6.03.002).

## Preconditions

1. A captured session is a directory under `captures/` (git-ignored, BC-6.02.001)
   holding `session.json`, an ordered array of steps. Each step has:
   - `now`: required decimal epoch seconds;
   - `stdin.bin`: a SIBLING FILE holding that refresh's stdin snapshot byte-exact
     (advocate design call 15, ADV-P4-D25) — the snapshot is NEVER a JSON member of
     `session.json`. Because the step's stdin lives outside the JSON document, any captured
     bytes are representable, including NaN/`Infinity` tokens, big-int literals, duplicate
     keys or an invalid/non-object snapshot: the harness splices the file's bytes directly
     and never parses them; a JSON-object-shaped snapshot as Claude Code sent it is the
     normal case;
   - `mode`: optional, `main` (default) or `subagent` — the marker for a subagent-mode
     capture, giving that step the handler-relative argv `["--subagent"]` (design call 9);
   - `metrics`: REQUIRED per step — the metrics source for that step's refresh, in the
     BC-6.02.003 model (`"canned"` serving the case's `metrics.json`, or `"down"`,
     `"500"`, `"garbage"`). There is no default: a step without `metrics` is a harness
     build error, so neither side can silently hit an unroutable URL and reintroduce the
     1.5 s timeout flakiness BC-6.02.003 bans (ADV-P1-D18);
   - `transcript_bytes`: optional integer, the transcript length at capture time;
   - `columns`: optional, the `COLUMNS` value seen at capture time.
   The directory may also hold `transcript.jsonl` (a copy of the session transcript)
   and the case settings (BC-6.02.003).
2. Paths inside each `stdin.bin` snapshot (`transcript_path`, `workspace.project_dir`,
   `cwd`) are rewritten by the harness to the per-case temp tree before use. The
   project directory is materialized with the same basename as the captured one.
   **Byte fidelity of the rewritten snapshot (ADV-P3-D24):** the harness performs a
   surgical, byte-level splice — only the path substring occurrences inside the captured
   bytes are replaced (lengths adjusted); `stdin.bin` is NOT parsed and
   re-serialized. Big-int literals, `NaN`/`Infinity` tokens, duplicate keys, key order
   and the original escaping are thereby preserved verbatim, satisfying the OD-107
   byte-parity-on-real-inputs criterion. If a capture ever requires more than a
   substring splice (paths split by JSON escapes), the case is a harness build error,
   not a silent rewrite.

## Postconditions

1. **Order.** Steps run strictly in array order, `k = 0..n-1`. For each `k` the
   harness:
   a. truncates the working transcript copy to `transcript_bytes[k]` when given (the
      prefix of `transcript.jsonl`), otherwise exposes the full copy;
   b. sets `HYLO_TEST_NOW = now[k]` for both sides (BC-6.01.003);
   c. runs the oracle with `stdin[k]` (paths rewritten), then Go with the identical
      bytes;
   d. compares stdout bytes, exit code and named caches (BC-6.03.002) before step
      `k+1`.
2. **Persistent per-side state.** Each side keeps its own cache directory for the
   whole sequence. The harness never resets, copies or edits a cache between steps;
   only the side itself writes it. Cache-swap tests are separate (BC-6.02.004).
3. **Clock advances per step.** The clock moves only from `now[k]` to `now[k+1]`.
   - `now` must be non-decreasing. If `now[k+1] < now[k]`, the harness fails with
     `parity: captured session <name> step <k+1>: now decreases`.
   - Equal consecutive instants are allowed (two refreshes inside one debounce
     window).
4. **First divergence reported.** On the first mismatch the harness reports the
   session name, step index, which artifact differed (stdout / exit code /
   `<cache name>`), and a byte-offset diff. Later steps of that session still run and
   report, because a divergence often heals or cascades and both are informative.
5. **Transcript growth is monotonic.** The EFFECTIVE transcript length — the step's
   `transcript_bytes` when given, otherwise the full `transcript.jsonl` length for a
   step that omits it (a "full copy" step, ADV-P2-D14) — must be non-decreasing across
   steps. A decrease of the effective length, or a given value larger than the file,
   fails the harness with the step index. A real transcript only grows; a shrink would
   exercise a reset path the capture never saw.

## Invariants

1. Both sides see byte-identical stdin, transcript prefix, clock and env at every
   step.
2. Replay never consults the real wall clock or the developer's real cache directory.
3. The replay code path is the same multi-step runner used by synthetic `steps` cases
   (BC-6.02.003).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Step without `now` | Harness FAIL naming the step. No default instant is guessed |
| EC-002 | Two consecutive steps with the same `now` | Both run. The git TTL (5 s) and metrics TTL see zero elapsed time, as in a real debounced burst |
| EC-003 | `transcript_bytes` splits a line mid-way (snapshot taken during an append) | Allowed. Both sides see the same partial last line. Long-line completion behavior is then compared, which is the realistic case |
| EC-004 | Snapshot has no `transcript_path` | Step runs. Both sides take the no-transcript path |
| EC-005 | Snapshot `session_id` changes mid-sequence (`/clear`) | Step runs. New session cache names appear on both sides and are compared by file name |
| EC-006 | Captured `columns` differs per step (terminal resized) | `COLUMNS` set per step for both sides |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Synthetic 3-step session (committed analogue): `now` = 1794615009, 1794615011, 1794615020; transcript grows 0 → 1,200 → 2,400 bytes | 3 comparisons. The step-1 metrics fetch is skipped by TTL on both sides; cache files compared after each step | happy-path |
| Steps with `now` 1794615009, 1794615009 | Both steps run; no error | edge-case |
| Steps with `now` 1794615020, 1794615009 | FAIL: `parity: captured session <name> step 1: now decreases` | error |
| `transcript_bytes` 2,400 then 1,200 | FAIL naming step index (transcript shrink) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-009 | The runner executes steps in order and compares after each step before running the next | table test with an instrumented fake side |
| VP-009 | Non-monotonic `now` or `transcript_bytes` is always rejected before any side runs that step | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-107 ("the harness replays sequences of stdin snapshots from a captured session, not only single frames"; P1 success criterion on the owner's real recorded inputs); design §5.2 (`steps`: each step advances the clock and appends transcript lines) and §5.3 (compare per step); OD-58 (clock stepped between refreshes) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/parity` parity harness multi-step runner (BC-COMPONENT-MAP: internal/parity/replay.go (stdin-sequence, stepped clock) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.02.001 — depends on: captured sessions live only in git-ignored `captures/`
- BC-6.02.003 — composes with: same step runner and settings translation
- BC-6.01.003 — depends on: per-step `HYLO_TEST_NOW`
- BC-6.03.002 — composes with: what is compared after each step

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/replay.go (stdin-sequence, stepped clock) (parity harness step runner) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- VP-009 — ordered replay properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/replay.go (stdin-sequence, stepped clock) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
