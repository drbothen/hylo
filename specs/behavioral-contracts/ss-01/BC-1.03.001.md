---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, ../semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1009-1015)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-030"
parity_class: "byte-exact"
confidence: "H"
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

# Behavioral Contract BC-1.03.001: No transcript path yields no transcript state

## Description

The transcript parser is the first step of a refresh after stdin decode. When stdin carries no usable
`transcript_path` (falsy, not a regular file, or a path whose size cannot be read), the parser returns
"no transcript state" (legacy `None`) and touches nothing: no mix-cache read, no mix-cache write. Every
transcript-fed widget (composition, token totals, the row-2 last-turn segment) is then absent for this refresh.

## Preconditions

1. stdin has been decoded to a JSON object `d` (BC-1.01.002); `d.transcript_path` is read with object `get`
   semantics (missing key = null).
2. The value is a string, or a falsy value of any JSON type (null, `""`, `0`, `0.0`, `false`, `[]`, `{}`).
   Truthy non-string values are governed by BC-1.03.015.

## Postconditions

1. If `transcript_path` is falsy, the parser returns no-transcript state.
2. If `transcript_path` is a non-empty string that does not name an existing **regular file** (missing path,
   directory, broken symlink, FIFO, device), the parser returns no-transcript state.
3. If the regular-file check passes but reading its size fails with an OS error (race: file removed between the
   check and the stat), the parser returns no-transcript state.
4. In all three cases: no mix cache is loaded, created, modified or deleted, and the session id is not consulted
   (so a non-string `session_id`, which would otherwise degrade under BC-1.03.013, does not degrade here).
5. Downstream rendering receives the no-transcript marker; the renderer's handling of it (composition hidden,
   token totals from stdin only, no last-turn rate) is specified by the consuming widget BCs, not here.

## Invariants

1. The check order is exactly: falsy test, then regular-file test, then size read (SL:1010-1015). No other
   filesystem access precedes or follows on these paths.
2. The status line never fails on these inputs: no degraded line, exit 0 (DI-008).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `transcript_path` key absent | no-transcript state, no cache I/O |
| EC-002 | `transcript_path: ""` / `null` / `0` / `false` / `[]` / `{}` / `0.0` | no-transcript state (all falsy) |
| EC-003 | path names a directory | no-transcript state |
| EC-004 | path does not exist | no-transcript state |
| EC-005 | path is a symlink to a regular file | followed: parsed normally (not this BC) |
| EC-006 | regular file removed between the regular-file check and the size read | no-transcript state (OS error caught) |
| EC-007 | regular file of size 0 with no mix cache | **not** this BC: the file exists, so BC-1.03.002 runs (size == offset 0, cached zeros returned, no write) |
| EC-008 | `session_id` is a number and `transcript_path` is missing | no-transcript state; no degrade, because the sid is only read after the file checks |

## Canonical Test Vectors

Re-pinned 2026-11-15 against `legacy/dgx_statusline.py` under CPython 3.11, stdout captured through a pipe.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `{"session_id": "s1"}` | parser result = no-transcript state; cache dir contains no `statusline-mix-s1.json` afterwards | happy-path |
| `{"transcript_path": "/nonexistent/x.jsonl", "session_id": "s1"}` | no-transcript state; no mix-cache file | error |
| `{"transcript_path": "<temp dir path>", "session_id": "s1"}` (a directory) | no-transcript state; no mix-cache file | edge-case |
| `{"transcript_path": "", "session_id": 123}` | no-transcript state; **no degraded line** (sid never read) | edge-case |
| Pre-existing `statusline-mix-s1.json` with arbitrary bytes, `transcript_path` missing | file bytes unchanged after the refresh | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | For every falsy JSON value of `transcript_path`, the parser performs zero cache-store calls (fake `CacheStore` records no Load/Save) | proptest (table over all JSON falsy values) |
| VP-029 | For a non-regular-file path the parser performs zero cache-store calls and returns no-transcript state | table test with fake `FileSystem` |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 (lane-aware status line) |
| L2 Domain Invariants | DI-007 (inputs = stdin, transcript, metrics, own caches), DI-008 (never fails) |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1009-1015) |
| Legacy contract | BC-SL-030 (pass-3 base table; index in pass-3 r4 §7.3) |
| Parity class | byte-exact (stdout and named cache files compared by the parity harness) |
| Architecture Module | `internal/statusline/transcript.go` (design §2.2; BC-COMPONENT-MAP: internal/statusline/transcript.go (no path -> no state) — ARCH-03) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-1.03.015 — composes with: truthy non-string `transcript_path` types (fd / crash semantics)
- BC-1.03.002 — depends on this BC: mix-cache work starts only after the file checks pass
- BC-1.03.013 — related to: sid sanitizing is never reached on no-transcript paths
- BC-1.01.009 — related to: side-effect order (transcript parse is step 2)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#transcript-parser` — internal/statusline/transcript.go (no path -> no state) (`internal/statusline/transcript.go` per design §2.2) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser (filled by story-writer)

## VP Anchors (Recommended)

- VP-029 — no cache I/O on no-transcript paths

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1009-1015) |
| **Confidence** | high (guard clauses; re-pinned with the oracle) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if not path or not os.path.isfile(path): return None` (SL:1010-1011); `except OSError: return None` (SL:1014-1015)
- **inferred**: no cache access precedes the guard (SL:1016 onward)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads only (stat) |
| **Global state access** | none |
| **Deterministic** | yes, given the filesystem state |
| **Thread safety** | unknown (single-threaded process) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Route the regular-file test and size read through the `FileSystem` seam (`Stat` returns size, regular flag, error)
so the guard is table-testable without a temp directory. The decision itself is pure once `Stat` is injected.
