---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "372936a"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1041-1058)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-032"
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

# Behavioral Contract BC-1.03.003: 512 KB read step with long-line completion

## Description

Each refresh reads the transcript incrementally from the cached offset: one step of at most `read_cap_bytes`
(524,288) bytes, extended by further steps **only while the blob contains no LF at all** and EOF is not reached.
Only complete lines (up to and including the last LF in the blob) are parsed, and the offset advances past that
LF. A blob with no LF (a torn trailing line) leaves the offset and the cache untouched. The value is a read
**step**, not a cap: a single line of any length is always completed (CONV-ABS-43).

## Preconditions

1. BC-1.03.002 chose the incremental or reset path; `off` (bytes) and `size` (bytes, from the earlier size read)
   are known and `size > off`.
2. `step = statusline.transcript.read_cap_bytes` (default 524,288; T-054, rationale: judgment, the per-refresh
   parse budget; owner-confirmed as a step, design §2.4). Range is defined in the S2 schema (OD-114).

## Postconditions

1. The parser opens the file in binary mode, seeks to `off` and reads `min(size - off, step)` bytes into `blob`.
2. While `blob` contains no `\n` (0x0A) **and** `off + len(blob) < size`: read up to `step` more bytes and append;
   stop early if a read returns 0 bytes. (The loop condition tests the whole accumulated blob, so it stops as soon
   as any LF has been appended.)
3. `cut` = index of the **last** LF in `blob`. If there is none, the parser returns the current values (as
   loaded or reset by BC-1.03.002) **without writing** the mix cache; `off` is unchanged.
4. Otherwise `off' = off + cut + 1`, the lines of `blob[:cut]` are parsed (BC-1.03.004 onward), and the cache is
   written with `"size": off'`.
5. Bytes after the last LF (a partial line, or whole lines beyond the step when the first step already contained
   an LF) are left for later refreshes.
6. An OS error while opening or reading returns the current values without writing.

## Invariants

1. `off` only moves to just past an LF; it never points inside a line.
2. If the first step contains an LF, no extension read happens, even if the step ends mid-line (BC-1.03.012).
3. Size is the value read before the parse; bytes appended after it are not read in this refresh.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | First line is 600,029 bytes (one LF at its end), off 0 | extension reads until the LF; whole line parsed in one refresh; `size` 600,029 |
| EC-002 | Three 199,999-byte lines (599,997 B) | refresh 1: first step (524,288 B) holds 2 LFs → `size` 399,998; refresh 2 → 599,997 |
| EC-003 | Trailing partial line without LF | no write; `off` unchanged; completed on the refresh after its LF lands |
| EC-004 | File grows during the extension loop | extension stops at the earlier `size`; the rest is read next refresh |
| EC-005 | Read error (permission revoked after the stat) | cached values returned, no write |
| EC-006 | A line containing `\r` but no `\n` | treated as "no LF": not cut; `\r` splitting happens only inside `blob[:cut]` (BC-1.03.004) |

## Canonical Test Vectors

`L1` = `{"message": {"content": "aaaaaaaaaa"}}` + LF (39 B). `BIG` = `{"message": {"content": "` + 600,000 × `b`
+ `"}}` + LF (600,029 B). `M` = `{"message": {"content": "` + 199,970 × `c` + `"}}` + LF (199,999 B). Re-pinned
2026-11-15 with the legacy oracle.

| Input | Expected Output | Category |
|-------|----------------|----------|
| transcript = `BIG`, no cache | one refresh: cache `"size": 600029`, `"conv": 600000` | happy-path |
| transcript = `M`×3, two refreshes | refresh 1: `"size": 399998`, `"conv": 399940`; refresh 2: `"size": 599997`, `"conv": 599910` | edge-case |
| refresh 1: `L1`; refresh 2: append `{"message": {"content": "zz"` (no LF); refresh 3: nothing; refresh 4: append `}}` + LF | refreshes 2-3: no write, cache stays `"size": 39`, `"conv": 10`; refresh 4: `"size": 70`, `"conv": 12` | edge-case |
| file unreadable after the stat (fake `FileSystem.ReadFrom` error) | cached values returned, Save not called | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029, VP-031 | After a write, `size` = offset just past an LF, and `size ≤` the stat size | proptest over random line lengths around the step boundary |
| VP-029, VP-031 | Extension reads occur iff the first step contains no LF | proptest with an instrumented `FileSystem` |
| VP-029, VP-031 | Go and legacy offsets agree for random line-length sequences | fuzz (Tier C differential) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007, DI-008 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1041-1058); constant `_READ_CAP` SL:952 |
| Legacy contract | BC-SL-032 (base; refined pass-3 r1: extension only when the first blob has no LF; CONV-ABS-43) |
| Threshold | T-054 → `statusline.transcript.read_cap_bytes` = 524288 (pass-4 r7) |
| Parity class | byte-exact |
| Architecture Module | `internal/statusline/transcript.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.012 — composes with: short line + long line takes two refreshes (consequence of invariant 2)
- BC-1.03.002 — depends on: starting offset and reset
- BC-1.03.004 — composes with: line splitting inside `blob[:cut]`

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#transcript-read-window` — internal/statusline/transcript.go (512 KB step) (`FileSystem.ReadFrom` seam (design §2.2)) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029, VP-031 — offset always just past an LF

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1041-1058; `_READ_CAP` SL:952) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `while b"\n" not in blob and off + len(blob) < size` (SL:1048); `if cut < 0: return …` (SL:1056-1057)
- **documentation**: SL:1045-1047 (review #6.5: a line over the cap used to freeze the parse)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads only |
| **Global state access** | none |
| **Deterministic** | yes, given file contents |
| **Thread safety** | unknown |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Keep the read loop in the shell; hand `blob[:cut]` and `off'` to the pure `parseTranscriptWindow` (design §3.1).
