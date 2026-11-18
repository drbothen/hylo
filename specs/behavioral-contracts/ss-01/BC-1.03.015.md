---
document_type: behavioral-contract
level: L3
version: "1.2.3"
status: draft
producer: product-owner
timestamp: 2026-11-18T10:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "44590c6"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1009-1015)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-088"
parity_class: "OD-161"
confidence: "M"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: int transcript_path → no-transcript, no foreign-descriptor I/O (ruling OD-161; ADV-P2-C06)", "1.2.2 2026-11-17: pass-3 remediation (ADV-P3-C12/C18): H1 retitled to hylo's behavior, StatFD/fd anchors dropped, parity_class OD-161, int branches disambiguated, DI-012 cited"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.015: transcript_path type semantics (truthy int → no transcript, no descriptor I/O)

## Description

`transcript_path` is passed to `os.path.isfile` and `os.stat`, which accept strings **and integers** (file
descriptors). The parser's behavior therefore depends on the JSON type: falsy → no transcript; string → a path;
truthy int or `true` → **no-transcript state** (ruling OD-161); truthy float, array or object → `TypeError`, a
degraded refresh (CP-S16). Legacy reads and closes a descriptor naming a regular file; hylo never touches a
descriptor it did not open.

## Preconditions

1. stdin decoded to an object; `transcript_path` read with `get`.
2. Harness: the status line's stdin/stdout/stderr are pipes (BC-6.01.002); non-pipe descriptors are not in the
   corpus.

## Postconditions

1. Falsy (null, `""`, `0`, `0.0`, `false`, `[]`, `{}`) → no-transcript state (BC-1.03.001).
2. Non-empty string → path semantics (BC-1.03.001 onward).
3. Truthy int `n` (or `true` = 1) → **no-transcript state**, for every int magnitude (owner ruling OD-161,
   2026-11-17: hylo never reads or closes a descriptor it did not open; exclusion id `OD-161`). Legacy contrast:
   `os.path.isfile(int)` stats the descriptor (oracle-verified) and a regular-file hit makes legacy read and close
   the descriptor it did not open — a foreign-descriptor hazard hylo deliberately does not reproduce; the deviation
   is confined to the transcript feed and covered by the `OD-161` exclusion entry.
4. **Legacy contrast only** (no hylo counterpart): a truthy int outside the C `int` range (e.g. `2147483648`,
   `-2147483649`, `2^70`) → `OverflowError` in legacy → degraded line, exit 0. hylo performs no descriptor I/O for
   any int, so it takes the no-transcript state here too (postcondition 3); the cache/output divergence rides the
   `OD-161` exclusion. (Legacy leg pinned 2026-11-15; see Edge Cases.)
5. Truthy float (`1.5`), array (`["a"]`) or object (`{"a": 1}`) → `TypeError` → degraded line (29 bytes), exit 0,
   no mix-cache I/O (CP-S16, byte-parity scope).

## Invariants

1. No transcript-path value ever produces non-zero exit or blank output (DI-008).
2. The degraded outcomes happen at step 2 of the effect order (BC-1.01.009): no earlier cache writes exist.
3. Hylo never reads or closes a file descriptor it did not open (ruling OD-161); the int-valued `transcript_path`
   branch performs no descriptor I/O at all.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `1` / `true` with stdout a pipe | no-transcript state |
| EC-002 | `-1` | legacy stats the fd (fails) → no-transcript state; hylo: no descriptor I/O, no-transcript state |
| EC-003 | `2147483647` (no such fd) | legacy stats (miss) → no-transcript state; hylo: no descriptor I/O, no-transcript state |
| EC-004 | `2147483648` / `2^70` | **legacy: degraded** (OverflowError "fd is greater than maximum"); hylo: no-transcript state — the OD-161 divergence (no descriptor I/O). `-2147483649` likewise ("fd is less than minimum"). Newly pinned; the legacy contract (pass-3 r1) lists only list/dict/float as crashing. Platform note: the bound is the C `int` of the build (32-bit on all three CI OSes) |
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
| `2147483648`, `-2147483649` | legacy: degraded line, exit 0; hylo: no-transcript state, no mix-cache file (OD-161 divergence) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | The type table above holds on Linux, macOS and Windows (the int branch is OS-independent no-I/O under OD-161) | table test per OS (CI matrix) |
| VP-012 | The named deviation this contract carries — exclusion id `OD-161` (truthy int `transcript_path` → no-transcript state, no descriptor I/O) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-161` entry and its riding table test `TestTranscriptPath_OD161_IntMeansNoTranscript`, and the mutation test fails closed if that entry is dropped | property test (VP-012 `TestParityExclusions_ClosedSet` / `TestParityExclusions_MutationFailClosed`, go test) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008; DI-012 (the int branch's no-I/O divergence rides the named, tested `OD-161` exclusion) |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1009-1015) |
| Legacy contract | BC-SL-088 (pass-3 r1, new; CP-S16) |
| Parity class | **OD-161** (int branch diverges by ruling; string/falsy/float-array-object legs byte-exact) |
| Confidence note | M — type dispatch; the int branch is ruled by OD-161 (pipe capture assumed, design §8, IM-23) |
| Architecture Module | `internal/statusline/transcript.go` (type dispatch; no descriptor I/O) |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.001 — composes with: falsy and string paths
- BC-1.01.001 — related to: degraded line
- BC-6.01.002 — depends on: harness captures through pipes

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#transcript` — internal/statusline/transcript.go (type dispatch; no descriptor I/O, OD-161) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029 — per-OS type table
- VP-012 — exclusion-closure cover for the named deviation `OD-161`

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1009-1015) |
| **Confidence** | medium (legacy descriptor legs oracle-pinned; hylo int branch ruled by OD-161) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **type constraint**: `os.stat` accepts str/bytes/PathLike/int; `genericpath.isfile` catches only `OSError`/`ValueError`
- **inferred**: oracle runs per type

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | hylo: none in the classified branch (string branch via the `FileSystem` seam); legacy stat/read/close described above |
| **Global state access** | hylo: none; legacy consults the process fd table |
| **Deterministic** | hylo: yes (type dispatch); legacy: no — depends on what the descriptor refers to |
| **Thread safety** | single-threaded render loop |
| **Overall classification** | pure (hylo classification branch; legacy contrast is effectful) |

#### Refactoring Notes

Classify the value first (pure): falsy / string / int / int-out-of-range / other; only the string branch touches
`FileSystem` (the int branch performs no descriptor I/O, OD-161).
