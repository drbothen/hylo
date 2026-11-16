---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs:
  - prd.md
  - behavioral-contracts/BC-ALLOCATION.md
  - domain-spec/capabilities.md
  - ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - ../semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-078"
parity_class: "temp-file"
confidence: "M"
lifecycle_status: active
introduced: v0.1.0
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.06.002: Sid with / : failed replace persists nothing; temp handling

## Description

A `session_id` containing a path separator points the session cache into a
subdirectory of the cache dir that does not exist. The temp file is still created in
the cache dir, the rename fails, the error is swallowed, and nothing persists: every
refresh behaves like a first refresh. That observable behavior is byte-exact.
**Approved deviation (temp-file, OD-110):** legacy leaks the temp file; hylo removes
it. This changes only the cache directory's listing, never stdout, so it is excluded
from the cache-file comparison only.

## Preconditions

1. `session_id` is a string containing `/` (on Windows also `\`), e.g. `../x` or
   `a/b`, so the session-cache path is `<cache dir>/statusline-../x.json` or
   `<cache dir>/statusline-a/b.json` (BC-1.06.001 naming).
2. The intermediate directory (`statusline-..`, `statusline-a`) does not exist in the
   cache dir.

## Postconditions

1. Every save to that path (rate-limit smoothing SL:307-308, sample SL:351/355, window
   start SL:287-288) creates a temp named `basename(target) + "." + <random>` in the
   cache dir (`x.json.<random>`, `b.json.<random>` — the prefix is the last path
   component, not `statusline-…`), then the rename fails (no such directory) and the
   error is swallowed (SL:198-206).
2. Every load of that path returns `{}` (SL:190-195), so within and across refreshes:
   the metrics TTL is never honored (a fetch every refresh, when rows ≥ 2), the
   process-age window probe runs every refresh, rate-limit smoothing is lost, and the
   sparkline never accumulates. No crash; stdout is as for a first refresh.
3. **Legacy:** the temp file is leaked (one per failed save per refresh).
   **hylo:** the temp file is removed after the failed rename (design IM-17). This is
   the only difference.
4. Path strings go to the OS unmodified (BC-1.06.001 postcondition 3). `a/../b` must
   fail like legacy on macOS/Linux (the OS needs `statusline-a` to exist), not be
   lexically cleaned to `b.json` in the cache dir.

## Invariants

1. stdout and every named cache file are byte-identical to legacy on these inputs
   (the other caches — mix, git, cost history — are unaffected by the session path).
2. The temp-file difference is excluded **only** from the cache-directory comparison,
   by name pattern `<name>.<random>`; stdout is never excluded for it.
3. No blanket exclusion: the entry names this case (OD-105).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | sid `a/b` and directory `statusline-a` **exists** in the cache dir | rename succeeds; data persists at `statusline-a/b.json`; later loads see it (legacy and Go alike) |
| EC-002 | sid `a/../b`, macOS/Linux | rename fails (no `statusline-a`), nothing persists; Go must not write `b.json` |
| EC-003 | sid `a/../b`, Windows | the OS normalizes `..` lexically, so the target resolves to `b.json` in the cache dir and the save succeeds (Go and legacy both defer to the OS). Expected from Win32 path rules; **not executed** — to be pinned on the windows-2025 CI leg |
| EC-004 | Go temp removal itself fails | swallowed; a leaked temp remains (still ignored by the comparison) |
| EC-005 | sid `../x`, Windows | the trailing-dot component `statusline-..` does not exist → fails, nothing persists. **Not executed** — to be pinned on the windows-2025 CI leg |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| sid `../x`, one save `{"k": 1}` | legacy: cache dir lists `x.json.<random>`, load → `{}`; Go: cache dir has no `x.json.*`, load → `{}` | happy-path |
| sid `a/b` with `statusline-a/` pre-created, save `{"k": 2}` | `statusline-a/b.json` holds `{"k": 2}`; load → `{"k": 2}` | edge-case |
| sid `a/../b` (macOS/Linux) | no `b.json` in the cache dir; load → `{}` | edge-case |
| two refreshes with sid `../x`, rows 2, healthy metrics | both refreshes fetch metrics and render identical "first refresh" stdout to legacy | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-018, VP-012 (frontmatter closure) | After any failed save, no file matching `<base>.*` created by that save remains (Go) | manual (table test with a temp cache dir) |
| VP-018, VP-012 (frontmatter closure) | stdout over an N-refresh sequence with a `/` sid equals legacy | manual (parity harness case) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 |
| Architecture Module | `internal/statusline` cache.go `CacheStore.Save` (BC-COMPONENT-MAP: internal/statusline/cache.go (failed replace, temp handling) — ARCH-04) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:save_cache (SL:198-206), load_cache (SL:190-195); session-cache path in main (SL:1215) |
| Legacy contract | BC-SL-078 (P3 deep r1 row 157) |
| Decisions | **OD-110** (Go cleaning up temp files legacy leaks: named exclusion, cache-file comparison only, stdout unaffected), **OD-105** (named exclusion list, no blanket exclusions), OD-03 (raw sid kept), OD-101 |
| Exclusion entry | `internal/statusline/testdata/parity/exclusions.json`: `{id: "temp-file", case: "session-id-with-slash", expected_output_file: <Go-expected cache-dir listing>, table_test: "TestCacheStore_OD110_TempCleanup"}` — id from the closed set defined in BC-6.03.004; a distinct case and table test from BC-6.03.003's temp-cleanup entry; the harness comparison ignores `<name>.<random>` temps (design §5.3, BC-6.03.003) |
| Dedicated table test | `TestCacheStore_OD110_TempCleanup` (rows: `../x`, `a/b` missing dir, `a/b` existing dir, `a/../b` per OS, removal failure) |

## Related BCs (Recommended)

- BC-1.06.001 — refines (save failure path)
- BC-6.03.003 — verified by (temp names excluded from comparison)
- BC-6.03.004 — depends on (exclusion-list machinery)
- BC-1.04.002 — related to (TTL never honored → fetch every refresh)

## Architecture Anchors (Recommended)

- `architecture/ARCH-04-data-files.md#cache-store` — internal/statusline/cache.go (failed replace, temp handling) (BC-COMPONENT-MAP: ARCH-04 (ARCH-04-data-files.md))

## Story Anchor (Recommended)

S-N.MM — cache store (filled by story-writer)

## VP Anchors (Recommended)

> Names provisional — architect (OD-145): harness flag names, the timing method, proposed
> test names and seed paths in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

- VP-018, VP-012 — temp cleanup

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | only via injected `Env` seams |
| **Global state access** | none (seam-injected) |
| **Deterministic** | yes for widgets, given inputs and fake seams |
| **Thread safety** | single-threaded render loop |
| **Overall classification** | mixed (core-dominant) |

Owning component `internal/statusline` (BC-COMPONENT-MAP: sl/cache.go (failed replace, temp handling) - ARCH-04); the ARCH-00 package table classifies the package mixed (core-dominant) - pure widgets plus the effect script (AD-03), I/O only via `Env` seams.
