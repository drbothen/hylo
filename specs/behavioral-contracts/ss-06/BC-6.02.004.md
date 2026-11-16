---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - ../semport/hylo-legacy/statusline-target-design.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
input-hash: "0000000"
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
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.02.004: Cache-swap coverage: Python-writes/Go-reads and reverse, all four caches

## Description

The four status line cache files are a shared on-disk format. Go must read what legacy
wrote, and legacy must read what Go wrote, with no observable difference. The harness
proves this with swap cases. One side runs step `k` and writes the caches; the files are
moved into the other side's cache directory; the other side runs step `k+1`. The
result must be byte-identical to an unswapped run. Byte-exact Go cache writers (ruling
Q-b) make this possible; the one-time `cost-history.json` copy at cutover (OD-106)
makes it necessary.

## Preconditions

1. The four caches and their names (legacy provenance):
   - session cache `statusline-<sid>.json` (SL:1215);
   - mix cache `statusline-mix-<sanitized sid>.json` (SL:951, 1017);
   - git cache `statusline-git-<sha1(dir)[:16]>.json` (SL:405-406);
   - `cost-history.json` (SL:217).
2. A swap case is a multi-step case (BC-6.02.003, at least 2 steps) marked `swap:
   "py->go"` or `swap: "go->py"` at a step boundary `k`. Its inputs exercise all four
   caches: a `session_id`, a transcript, a project directory with a `.git`, a lane that
   triggers `record_cost`, and ROWS ≥ 2 with a canned metrics reply.
3. Tier A (BC-6.03.002) already shows that unswapped Go equals unswapped legacy on the
   same case.

## Postconditions

1. **py→go.** Legacy runs steps `0..k`. The harness then copies every named cache file
   from the legacy cache dir into an empty Go cache dir, byte for byte and under the
   same file name. Go runs steps `k+1..n-1` on those files.
   - At every step `j > k`, Go's stdout, exit code and named cache files must equal the
     pure-legacy run's step `j`.
2. **go→py.** The mirror image: Go runs `0..k`, its named caches are copied into the
   legacy cache dir, and legacy runs `k+1..n-1`.
   - At every step `j > k`, legacy's outputs must equal the pure-Go run's step `j`. By
     Tier A that is also the pure-legacy run.
3. **Coverage.** The corpus contains at least one py→go and one go→py case in which
   each of the four cache files exists at the swap boundary. The harness asserts this
   by listing the copied file names and failing with
   `parity: swap coverage missing <cache>` if any of the four is absent in both
   directions.
4. **Seeded variants.** The swap set also includes these seeds (design §5.2):
   - the BC-SL-101 20-session `cost-history.json`;
   - legacy `[t, v]` history points and `rl`/`rl_ts` in the session cache;
   - a legacy-written poisoned mix cache (BC-SL-100);
   - the T05~ mix state (BC-SL-103).
   Each is read by Go and must produce the oracle's next-step bytes. Rows covered by an
   exclusion entry (BC-6.03.004) are compared against their expected files instead.
5. **Temp files are never swapped.** Only named caches (names ending in `.json`) are
   copied. Files matching the mkstemp temp pattern (BC-6.03.003) are not.

## Invariants

1. A swap changes only which process wrote the cache bytes. Stdin, clock, transcript,
   metrics and settings for steps `j > k` are identical to the unswapped run.
2. Cache files are copied as raw bytes. The harness never decodes and re-encodes them.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Legacy writes a session cache whose key order is inherited (BC-SL-091); Go reads it, then writes it | Go's written bytes equal what legacy would have written at that step, key order included |
| EC-002 | Numeric `session_id` in a swap case touching `cost-history.json` | Covered by the `OD-30` exclusion entry: Go writes one string-form key where legacy writes duplicates. The step is compared against the entry's expected file (BC-6.03.004) |
| EC-003 | Legacy leaks a temp file at the swap boundary (sid containing `/`) | The temp file is not copied; only named caches move |
| EC-004 | Swap case where no `.git` exists | Fails the coverage check unless another swap case covers the git cache in that direction |
| EC-005 | Go-written cache contains NaN tokens (`NaN` literal as legacy's `json.dump` writes) | Legacy reads it via `json.load` (accepts `NaN`); outputs compared normally |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| 3-step case, `swap: "py->go"` at `k=0`, all four caches present after step 0 | Go steps 1-2 byte-equal to pure-legacy steps 1-2 (stdout, exit, four named caches) | happy-path |
| Same case, `swap: "go->py"` at `k=1` | Legacy step 2 byte-equal to pure-Go step 2 | happy-path |
| Seeded BC-SL-101 20-session `cost-history.json`, py→go at `k=0` | Go `$`/`$/h` colors at step 1 equal legacy's (percentile colors, not cold-start) | edge-case |
| Corpus with no go→py case containing `cost-history.json` | FAIL: `parity: swap coverage missing cost-history.json` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-019 | For every swap case, outputs after the swap equal the unswapped run's outputs at every later step | multi-step differential test |
| VP-019 | All four cache files are exercised in both swap directions | coverage assertion in the harness |

## Traceability

| Field | Value |
|-------|-------|
| Source | design §5.2 "Cache-swap cases" (Python writes and Go reads, and the reverse, for all four caches; ruling Q-b, research Q3b); OD-106 (cost-history copied at cutover); OD-03 (raw sid in cache names); OD-30 (numeric sid difference, handled by its exclusion entry); legacy cache names `legacy/dgx_statusline.py` SL:217, 405-406, 951, 1017, 1215 |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009, CAP-011 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/statusline` parity harness swap runner (BC-COMPONENT-MAP: internal/parity/swap.go (four-cache swap) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-1.06.001 — depends on: cache load/save byte format and raw-sid file names
- BC-1.05.009 — depends on: exact `cost-history.json` write format
- BC-6.02.003 — composes with: multi-step case model
- BC-6.03.002 — composes with: per-step comparison by file name
- BC-6.03.004 — related to: OD-30 / D4-EX-2 entries for swapped rows that differ by ruling

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/swap.go (four-cache swap) (cache store and harness swap runner) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- VP-019 — swap equivalence properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/swap.go (four-cache swap) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
