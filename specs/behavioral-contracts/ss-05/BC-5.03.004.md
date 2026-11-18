---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T11:45:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md, owner-decisions-log-2026-11-14.md]
input-hash: "a7014d0"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces os.path normpath/basename used at legacy/dgx_statusline.py SL:373-390, 460)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-18: ADV-P4 remediation D18 - abspath/join/dirname de-scoped from pyfmt (ARCH-06 agreement); flavor selection pinned to runtime.GOOS incl. Basename", "1.2.2 2026-11-17: pass-4 residual sweep — BC-1.02.003 cross-reference updated to the enriched project-label title (ADV-P4-B17)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.03.004: PosixNormpath/NtNormpath/Basename per-OS selection (ntpath on Windows)

## Description

Legacy's `os.path` is `posixpath` on macOS and Linux and `ntpath` on Windows. `pyfmt.PosixNormpath`,
`pyfmt.NtNormpath` and `pyfmt.Basename` reproduce CPython 3.11's `normpath` and `basename` for each flavor, and the
flavor is selected at build time by `runtime.GOOS` (posix on darwin/linux, nt on windows; Pre-2 — including for
`Basename`, per ARCH-06's ruling, ADV-P4-D18), never by the path's look. Go's `filepath.Clean` differs (it turns `//`
into `/`, BC-SL-059), so it is not used (design IM-11; pitfall PR-20).

## Preconditions

1. `p` is a Value string (code points).
2. The OS flavor is fixed at build time (`runtime.GOOS == "windows"` → nt, else posix).

## Postconditions

1. **PosixNormpath(p):** collapses repeated `/`, removes `.` segments and resolves `..` against preceding segments;
   keeps a leading `..` in relative paths; `""` → `.`; exactly **two** leading slashes are preserved (`//` → `//`,
   `//a//b/` → `//a/b`) while three or more collapse to one (`///` → `/`); `/..` → `/`; a trailing slash is removed.
2. **NtNormpath(p):** treats `/` and `\` as separators and outputs `\`; preserves drive (`C:`) and UNC
   (`\\server\share`) prefixes and the `\\?\` prefix; `C:` stays `C:`, `C:\` stays `C:\`; `//` → `\\`; `""` → `.`.
3. **Basename(p)** returns the text after the last separator of the active flavor (`/` for posix; `/`, `\` and the
   drive colon for nt); `""` when `p` ends with a separator.
4. The project label call site `basename(normpath(p)) or normpath(p)` (SL:460) yields `//` for `//`, `/` for `/..`,
   `proj` for `/work/proj/`, and on Windows `C:\` for `C:\`.

## Invariants

1. `filepath.Clean`, `path.Clean` and `filepath.Base` are never used for these legacy-visible values.
2. Per-OS goldens: the CPython-generated tables for `NtNormpath` are produced by the oracle on the Windows runner
   (`*.windows.golden`, design RK-3); posix tables on Linux/macOS. CPython 3.11.7 implements both via the C
   `_path_normpath` when available.
3. pyfmt serves ONLY the normpath/basename primitives of this contract. `abspath`, `join`
   and `dirname` (git-walk sites SL:373, 375, 383, 390) are **NOT** pyfmt helpers (ARCH-06):
   the git-walk module composes them directly, and their per-flavor behavior (on Windows
   `abspath` resolves through `GetFullPathNameW`; posix/nt `join`/`dirname` flavors) is
   pinned by that module's contract, not here — anchoring gap flagged to the architect
   (ADV-P4-D18).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `PosixNormpath("//")` | `"//"` (Go `filepath.Clean` gives `/`) |
| EC-002 | `PosixNormpath("///")` | `"/"` |
| EC-003 | `PosixNormpath("a/..")`; `PosixNormpath("../x")` | `"."`; `"../x"` |
| EC-004 | `NtNormpath("C:/a/b")` | `"C:\a\b"` |
| EC-005 | `NtNormpath("\\?\C:\x")` | unchanged |
| EC-006 | `NtNormpath("C:")`; basename → `""`; label falls back to `"C:"` | `"C:"` |
| EC-007 | `NtNormpath("a/b\c")` | `"a\b\c"` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| posix label of `/work/proj/` | `proj` | happy-path |
| posix `PosixNormpath("/a/./b/../c")`, label | `/a/c`, `c` | happy-path |
| nt label of `C:\work\proj\` | `proj` | happy-path |
| posix label of `//` | `//` | edge-case |
| nt `NtNormpath("\\server\share\x")`, label | unchanged, `x` | edge-case |
| posix label of `""` | `.` | helper-level edge case (at the legacy call site an empty cwd renders NO label: `if proj_dir:` skips it, SL:454; a fact of the call site, not the helper) |

Verified 2026-11-15 against CPython 3.11.7 `posixpath`/`ntpath` (ntpath rows from the module run on macOS; the
committed Windows goldens are generated on the Windows runner).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-025 | `PosixNormpath` and `NtNormpath` equal the oracle on fuzzed path strings | fuzz + per-OS oracle tables |
| VP-025 | Normpath is idempotent | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/str.go` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/str.go (Posix/Nt Normpath, Basename) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103; design IM-11; pitfall PR-20; D5 (cross-platform). pyfmt-served legacy uses: SL:460 (project label normpath/basename); git-walk sites SL:373, 375, 383, 390 compose `abspath`/`join`/`dirname` OUTSIDE pyfmt (ADV-P4-D18 de-scope; architect to pin the owning contract) |

## Related BCs (Recommended)

- BC-1.02.003 — consumed by (project label `basename(normpath(project_dir | current_dir | cwd))`)
- BC-1.02.022 — consumed by (POSIX normpath keeps `//`)
- BC-1.02.004 — consumed by (branch walk paths)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-str` — internal/pyfmt/str.go (Posix/Nt Normpath, Basename) (path helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt str (design step S1)

## VP Anchors (Recommended)

- VP-025 — normpath equals the oracle per OS

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/str.go (Posix/Nt Normpath, Basename)` (BC-COMPONENT-MAP: py/str.go (Posix/Nt Normpath, Basename) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
