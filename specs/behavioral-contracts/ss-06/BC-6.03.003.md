---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T11:45:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - owner-decisions-log-2026-11-14.md
input-hash: "427aa34"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (new contract; governs the comparison of the legacy behavior at legacy/dgx_statusline.py SL:198-206)"
subsystem: "SS-06"
capability: "CAP-009"
legacy_id: "new"
parity_class: temp-file
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

# Behavioral Contract BC-6.03.003: mkstemp temp names excluded from comparison; Go temp-cleanup difference covered

## Description

**This contract governs an approved deviation.** Its parity class is `temp-file`
(OD-110). When the atomic replace fails, legacy `save_cache` leaks its `mkstemp` temp
file in the cache directory. Go removes the temp file on that failure. The harness
handles the difference in two parts:

- Temp-pattern file names are removed from the named-cache comparison set, so stdout
  and named caches are still compared byte for byte.
- The cleanup difference itself is covered by a named exclusion-list entry, id
  `temp-file`, with its own expected file and a dedicated table test
  `TestCacheStore_TempFile_CleanupOnFailedReplace`.

It is never a blanket exclusion.

## Preconditions

1. Legacy writes caches with
   `tempfile.mkstemp(dir=CACHE_DIR, prefix=os.path.basename(path) + ".")` and then
   `os.replace(tmp, path)`. Any exception is swallowed with no cleanup (SL:198-206).
   The temp name is `<basename(target)>.` followed by 8 characters from
   `[a-z0-9_]` (CPython `tempfile._RandomNameSequence`).
2. A replace fails in practice when the raw sid contains `/`, e.g. `../x`. The target
   `statusline-../x.json` points into a nonexistent subdirectory, `mkstemp` succeeds in
   `CACHE_DIR`, and `os.replace` fails. Legacy leaves `x.json.<8 chars>` behind
   (BC-SL-078, OD-03). Each failed session-cache write leaks one temp. A refresh can
   leak up to two, from `effective_rl` (SL:308) and `get_sample` (SL:350 or 355).
3. Go writes through `os.CreateTemp(cacheDir, base+".*")` plus `os.Rename`. On error
   it removes the temp (design IM-17; convention CV-01 "remove temp on error").

## Postconditions

1. **Temp-name filter.** Before the named-cache comparison of BC-6.03.002, the
   harness removes from each side's file list every regular file whose name matches
   `^.+\.json\.[a-z0-9_]{8}$` — the anatomy of a leaked legacy temp
   `<target>.json.<8 mkstemp chars>` (Python `tempfile` suffix alphabet
   `[a-z0-9_]{8}`, CPython 3.11 verified with `python3 -I`). A named cache
   `statusline-<sid>.json` can never match: legacy's sid sanitizer
   (`re.sub(r"[^A-Za-z0-9_-]", "_", sid)[:40]`, SL:1015-1016) removes dots from the
   sid, so a named cache contains exactly one `.` and cannot have the `.json.`
   double-dot anatomy — not even for a fuzzed or synthetic sid (fail-closed for
   named caches, ADV-P1-D16). Removed names are listed in the step report as
   `temp (ignored): <name>`.
2. **stdout unaffected.** The filter never touches stdout or exit-code comparison.
   For the sid-with-`/` case, stdout and exit code are compared to the oracle exactly
   as for any other case, and must match. Nothing persists on either side, so both
   sides fetch on every refresh and both lose rate-limit smoothing.
3. **Named exclusion entry.** `internal/statusline/testdata/parity/exclusions.json`
   contains exactly one entry with id `temp-file` per case that triggers a failed
   replace, for example
   `{"id": "temp-file", "case": "cache/sid-slash-temp", "expected_output_file":
   "cache/sid-slash-temp/expected.go-cache-listing.txt", "table_test":
   "TestCacheStore_TempFile_CleanupOnFailedReplace"}`. Its scope is the cache-file
   comparison only (OD-110). The expected file pins Go's cache-directory listing
   after each step, with no temp file present.
4. **Dedicated table test** `TestCacheStore_TempFile_CleanupOnFailedReplace`, a Go unit
   test on the cache store with a real temp dir. For each row it asserts:
   - a write to a target whose parent directory does not exist returns without panic;
   - the target is absent;
   - the cache dir contains no file matching the temp pattern;
   - an existing unrelated cache file is unchanged.
   Rows: sid `../x`, sid `a/b`, and on Windows sid `a\b`.
5. **Legacy leak observed, not required of Go.** The harness case asserts that the
   oracle's cache dir contains ≥ 1 temp-pattern file after the step. This proves the
   case exercises the difference. Go's cache dir must contain 0.

## Invariants

1. The temp filter applies only to names matching the pattern. It never hides a
   missing or extra named cache.
2. The `temp-file` entry has no glob and names one case (BC-6.03.004). There is one
   entry per triggering case.
3. Go never leaves a temp file behind on any write error path.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | sid `../x`, ROWS 2, stdin carries non-empty `rate_limits`, metrics canned | Legacy leaks two temps (`x.json.<8>` ×2); Go leaks none. stdout equal; named caches equal (the only named caches are git and mix, plus cost history if recorded) |
| EC-002 | A sid containing `.json.` such as `a.json.b` | Session cache `statusline-a.json.b.json` ends in `.json` and is compared normally |
| EC-003 | Go's `os.CreateTemp` random part is decimal digits | Also matched by the pattern; it would be ignored if ever present, but the table test requires that none remain |
| EC-004 | Windows: rename fails on a sharing violation under concurrent refreshes (RK-3) | Not a corpus case. Go retries, then swallows and cleans up; covered by Go unit tests only |
| EC-005 | A temp-pattern file appears in a case with no `temp-file` entry | Ignored by the filter for comparison. If the file is on the Go side, the store invariant is violated, and the harness fails the case with `go left temp <name>` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Normal case, no failed replace | No temp names on either side; filter removes nothing | happy-path |
| `cache/sid-slash-temp`: sid `../x`, one step | Oracle dir contains `x.json.<8 chars>`; Go dir contains none; stdout and exit equal; the Go listing matches the expected file; `TestCacheStore_TempFile_CleanupOnFailedReplace` passes | edge-case |
| Go store modified to skip cleanup | `TestCacheStore_TempFile_CleanupOnFailedReplace` FAIL; harness FAIL `go left temp x.json.<n>` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-012, VP-018 | The temp-name filter removes exactly the names matching the pattern, never a `.json` named cache | table test on the filter |
| VP-012, VP-018 | After any failed Go cache write, no temp file remains in the cache dir | `TestCacheStore_TempFile_CleanupOnFailedReplace` + fuzz over sids |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-110 (Go cleaning up temp files legacy leaks: named exclusion entry, excluded only from the cache-file comparison since stdout is unaffected; own table tests); OD-105 (named exclusion list, no blanket exclusions); design §5.3 (files named `<name>.<random>` are ignored), §7.1 T2(c); legacy behavior `legacy/dgx_statusline.py:save_cache` (SL:198-206), write sites `effective_rl` (SL:308), `get_sample` (SL:350, 355); BC-SL-078 |
| Approved deviation | `temp-file` (OD-110) — exclusion entry id `temp-file`; dedicated table test `TestCacheStore_TempFile_CleanupOnFailedReplace` |
| Parity class | temp-file |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/statusline/cache.go`; parity harness comparator (BC-COMPONENT-MAP: internal/parity/compare.go (temp carve-out) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-1.06.002 — composes with: the cache-store behavior on a failed replace (BC-SL-078, temp-file class)
- BC-6.03.002 — composes with: named-cache comparison that consumes the filtered name set
- BC-6.03.004 — depends on: exclusion-list machinery validating the `temp-file` entry

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/compare.go (temp carve-out) (cache store write path and harness comparator) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

> Names provisional — architect (OD-145): harness flag names, the timing method, proposed
> test names and seed paths in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

- VP-012, VP-018 — temp filter and cleanup properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/compare.go (temp carve-out) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
