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
  - domain-spec/ubiquitous-language.md
  - semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md
  - semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "79177eb"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-052"
parity_class: "byte-exact"
confidence: "H"
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

# Behavioral Contract BC-1.06.001: Cache load/save: never-raise, raw sid in file names

## Description

All four status-line caches (session, mix, git, cost history) are read and written
through one load/save pair that never raises: a load that fails for any reason yields
an empty object, and a save writes a temp file in the cache directory and atomically
renames it over the target, swallowing every error. The session cache's file name
embeds stdin's `session_id` raw, unsanitized (OD-03), unlike the mix cache.

## Preconditions

1. Cache directory = `paths.cache_dir`; default per OD-101: `$XDG_CACHE_HOME/hylo` or
   `~/.cache/hylo` on macOS/Linux, `%LOCALAPPDATA%\hylo` on Windows, built by
   `internal/platform` (the one explicit owner exception to "defaults equal legacy";
   legacy used its own fixed directory, SL:78).
2. Session-cache path = cache dir + separator + `"statusline-" + S + ".json"`, where
   `S = session_id` if truthy, else `"nosession"`, rendered with Python `str()`
   semantics (`pyfmt.Str`) (SL:1214-1215).
3. Config error (D4-EX-3) → no load/save runs at all (design §3.1 step 0).

## Postconditions

1. **Load** (SL:190-195): read the file as UTF-8 text and parse it with Python
   `json.load` semantics (`internal/pyfmt`): `NaN`/`Infinity` accepted, duplicate keys
   last-wins, trailing whitespace allowed. Return the parsed value **whatever its JSON
   type** (a top-level array is returned as an array). On any failure — missing file,
   permission error, empty file, invalid JSON, a UTF-8 BOM, invalid UTF-8, trailing
   garbage — return `{}`.
2. **Save** (SL:198-206): create the cache directory if missing (`os.makedirs(...,
   exist_ok=True)`); create a temp file **in the cache directory** (not the target's
   directory) named `basename(target) + "." + <random>`, mode 0600; write
   `json.dump(data)` bytes (BC-1.05.009 format rules); rename the temp over the target
   (`os.replace`). Any exception at any step is swallowed; the render continues.
3. The target path string is handed to the OS unmodified — Go must not lexically
   clean it (`filepath.Join`/`Clean` would turn `statusline-a/../b.json` into
   `b.json`); it concatenates directory, separator and name.
4. Session-cache names: `abc` → `statusline-abc.json`; `777` → `statusline-777.json`;
   `true` → `statusline-True.json`; `1.5` → `statusline-1.5.json`; absent/`null`/`""`
   → `statusline-nosession.json`.

## Invariants

1. Load and save never raise into the render (cache loss is cosmetic; the next refresh
   rewrites, SL:206).
2. Readers never see a torn file: the target is replaced atomically by rename.
3. A write that fails on disk stays invisible to the next read in the same refresh
   (no in-memory overlay, design §3.1).
4. Only the session cache uses the raw sid; the mix cache sanitizes it (BC-1.03.013).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | file contains `[1]` | load returns `[1]`; caller-level crash paths for wrong shapes are CP-C01..C10, out of parity scope (P3r2 ruling b) |
| EC-002 | file `{"a": NaN}` | `{"a": NaN}` |
| EC-003 | file `{"a":1,"a":2}` | `{"a": 2}` |
| EC-004 | file starts with a UTF-8 BOM | `{}` |
| EC-005 | file `{"a":1} x` | `{}` |
| EC-006 | cache dir path is a regular file | save fails silently; nothing persisted |
| EC-007 | sid contains `/` | BC-1.06.002 |
| EC-008 | Windows, sid with a character invalid in file names (`:` `*` `?` `"` `<` `>` `\|`) | save fails silently, nothing persists (same class as BC-1.06.002); expected from Win32 file-name rules, **not executed** (pin on the windows-2025 CI leg); kept as-is per OD-03 ("revisit only if Windows complains; real ids are UUIDs") |
| EC-009 | Windows sharing violation on rename | 2-3 short retries, then swallow (design IM-17) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| save `{"z": 1, "a": [1.0, inf]}` to `t.json` | file bytes `{"z": 1, "a": [1.0, Infinity]}`, mode 0600, no temp left | happy-path |
| load of a missing file | `{}` | edge-case |
| stdin `session_id: 777` | session cache `statusline-777.json` | edge-case |
| load of bytes `{"a":\xff}` | `{}` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-018, VP-001, VP-022 (primary), VP-019 (frontmatter closure) | Load returns `{}` for every input the CPython oracle rejects, and the oracle's value otherwise | fuzz (differential) |
| VP-018, VP-001, VP-022 (primary), VP-019 (frontmatter closure) | Save never panics or returns an error to the caller under injected FS faults | proptest (fault-injecting store) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 (status-line caches) |
| L2 Domain Invariants | DI-007 (the status line's own caches are an allowed input) |
| Architecture Module | `internal/statusline` cache.go `CacheStore` Load/Save (design IM-17; BC-COMPONENT-MAP: internal/statusline/cache.go (never-raise, raw sid) — ARCH-04) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:load_cache (SL:190-195), save_cache (SL:198-206); main session-cache path (SL:1214-1215) |
| Legacy contract | BC-SL-052 (P3r1 row 91; refined P3 deep r1 row 157) |
| Decisions | D4, D5 (cross-platform), **OD-03** (raw sid kept), **OD-101** (hylo cache dir from P1), OD-103, OD-110 (temp cleanup is a named, cache-comparison-only exclusion, see BC-1.06.002) |

## Related BCs (Recommended)

- BC-1.06.002 — related to (sid with `/`, temp handling)
- BC-1.05.009 — consumed by (cost-history bytes)
- BC-1.03.013 — related to (mix cache sanitizes the sid)
- BC-6.03.003 — related to (temp names excluded from comparison)
- BC-5.02.003 / BC-5.02.004 — depends on (JSON decode, ordered Value)

## Architecture Anchors (Recommended)

- `architecture/ARCH-04-data-files.md#cache-store` — internal/statusline/cache.go (never-raise, raw sid) (BC-COMPONENT-MAP: ARCH-04 (ARCH-04-data-files.md))

## Story Anchor (Recommended)

S-N.MM — cache store (filled by story-writer)

## VP Anchors (Recommended)

- VP-018, VP-001, VP-022, VP-019 — never-raise load/save

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | only via injected `Env` seams |
| **Global state access** | none (seam-injected) |
| **Deterministic** | yes for widgets, given inputs and fake seams |
| **Thread safety** | single-threaded render loop |
| **Overall classification** | mixed (core-dominant) |

Owning component `internal/statusline` (BC-COMPONENT-MAP: sl/cache.go (never-raise, raw sid) - ARCH-04); the ARCH-00 package table classifies the package mixed (core-dominant) - pure widgets plus the effect script (AD-03), I/O only via `Env` seams.
