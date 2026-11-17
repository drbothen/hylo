---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "d937286"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1009-1015)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-088"
parity_class: "byte-exact"
confidence: "M"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.015: transcript_path type semantics (int = fd)

## Description

`transcript_path` is passed to `os.path.isfile` and `os.stat`, which accept strings **and integers** (file
descriptors). The parser's behavior therefore depends on the JSON type: falsy → no transcript; string → a path;
truthy int or `true` → a file descriptor; truthy float, array or object → `TypeError`, a degraded refresh (CP-S16).
The parity corpus captures stdout through pipes, so a descriptor never names a regular file there and both sides
return no-transcript state.

## Preconditions

1. stdin decoded to an object; `transcript_path` read with `get`.
2. Harness: the status line's stdin/stdout/stderr are pipes (BC-6.01.002); non-pipe descriptors are not in the
   corpus.

## Postconditions

1. Falsy (null, `""`, `0`, `0.0`, `false`, `[]`, `{}`) → no-transcript state (BC-1.03.001).
2. Non-empty string → path semantics (BC-1.03.001 onward).
3. Truthy int `n` (or `true` = 1) within the C `int` range [−2³¹, 2³¹−1] → treated as descriptor `n`
   (`platform.StatFD(n)`: `/dev/fd/n` on Unix; "not a regular file" on Windows). If it is not a regular file, or
   the stat fails (`-1`, closed fd) → no-transcript state. If it is a regular file, legacy reads it as the
   transcript and **closes** the descriptor when done (unspecified for the corpus; out of scope).
4. Truthy int outside the C `int` range (e.g. `2147483648`, `-2147483649`, `2^70`) → `OverflowError` in legacy →
   degraded line, exit 0. (Pinned 2026-11-15; not in the legacy contract text — see Edge Cases.)
5. Truthy float (`1.5`), array (`["a"]`) or object (`{"a": 1}`) → `TypeError` → degraded line (29 bytes), exit 0,
   no mix-cache I/O (CP-S16, byte-parity scope).

## Invariants

1. No transcript-path value ever produces non-zero exit or blank output (DI-008).
2. The degraded outcomes happen at step 2 of the effect order (BC-1.01.009): no earlier cache writes exist.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `1` / `true` with stdout a pipe | no-transcript state |
| EC-002 | `-1` | stat fails → no-transcript state |
| EC-003 | `2147483647` (no such fd) | no-transcript state |
| EC-004 | `2147483648` / `2^70` | **degraded** (OverflowError "fd is greater than maximum"); `-2147483649` likewise ("fd is less than minimum"). Newly pinned; the legacy contract (pass-3 r1) lists only list/dict/float as crashing. Platform note: the bound is the C `int` of the build (32-bit on all three CI OSes) |
| EC-005 | `0.0` | falsy → no-transcript state (not TypeError) |
| EC-006 | `1.5` | degraded (TypeError) |
| EC-007 | `{}` / `[]` | falsy → no-transcript state |

## Canonical Test Vectors

Re-pinned 2026-11-15 with the legacy oracle (CPython 3.11, macOS arm64, stdout piped).

| Input (`transcript_path`) | Expected Output | Category |
|-------|----------------|----------|
| `"<path to a regular transcript>"` | normal parse | happy-path |
| `1`, `true`, `-1`, `2147483647`, `0`, `false`, `0.0`, `[]`, `{}`, `null`, `""` | no-transcript state; no mix-cache file | edge-case |
| `1.5` | degraded line `\x1b[90mstatusline degraded\x1b[0m\n`, exit 0 | error |
| `["a"]`, `{"a": 1}` | degraded line, exit 0 | error |
| `2147483648`, `-2147483649` | degraded line, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | The type table above holds on Linux, macOS and Windows (Windows: ints → not a regular file) | table test per OS (CI matrix) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1009-1015) |
| Legacy contract | BC-SL-088 (pass-3 r1, new; CP-S16) |
| Parity class | byte-exact |
| Confidence note | M — fd semantics, pipe capture assumed (design §8, IM-23) |
| Architecture Module | `internal/statusline/transcript.go`; `internal/platform` `fd_*.go` (D5 build tags) |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.001 — composes with: falsy and string paths
- BC-1.01.001 — related to: degraded line
- BC-6.01.002 — depends on: harness captures through pipes

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/transcript.go + internal/platform/fd_*.go (int = fd) (`platform.StatFD` per OS) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md), ARCH-05 (ARCH-05-platform.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029 — per-OS type table

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1009-1015) |
| **Confidence** | medium (descriptor behavior depends on the process's fd table) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **type constraint**: `os.stat` accepts str/bytes/PathLike/int; `genericpath.isfile` catches only `OSError`/`ValueError`
- **inferred**: oracle runs per type

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads only |
| **Global state access** | reads the process fd table |
| **Deterministic** | no — depends on what the descriptor refers to |
| **Thread safety** | unknown |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Classify the value first (pure): falsy / string / int-in-range / int-out-of-range / other; only the string and
int-in-range branches touch `FileSystem` / `platform.StatFD`.
