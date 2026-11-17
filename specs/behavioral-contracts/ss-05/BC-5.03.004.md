---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md, owner-decisions-log-2026-11-14.md]
input-hash: "013d953"
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
modified: []
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
caller selects the flavor by the running OS, never by the path's look. Go's `filepath.Clean` differs (it turns `//`
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
3. Uses served: SL:460 (project label), SL:373, 375, 383 (`abspath`/`join`/`normpath` in the git walk), SL:390
   (`dirname`, walk step).

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
| posix label of `""` | `.` | error (empty cwd still renders a label) |

Verified 2026-11-15 against CPython 3.11.7 `posixpath`/`ntpath` (ntpath rows from the module run on macOS; the
committed Windows goldens are generated on the Windows runner).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-025 | `PosixNormpath` and `NtNormpath` equal the oracle on fuzzed path strings | fuzz + per-OS oracle tables |
| VP-025 | Normpath is idempotent | proptest |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/str.go` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/str.go (Posix/Nt Normpath, Basename) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103; design IM-11; pitfall PR-20; D5 (cross-platform). Legacy uses served: SL:373, 375, 383, 390, 460 |

## Related BCs (Recommended)

- BC-1.02.003 — consumed by (project label `basename(normpath(cwd))`)
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
| **Thread safety** | Send + Sync (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/str.go (Posix/Nt Normpath, Basename)` (BC-COMPONENT-MAP: py/str.go (Posix/Nt Normpath, Basename) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
