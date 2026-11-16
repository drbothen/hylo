---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, ../semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, ../semport/hylo-legacy/statusline-target-design.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_lane (SL:451-462)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-008
parity_class: byte-exact
confidence: H
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

# Behavioral Contract BC-1.02.003: Project label is basename(normpath(cwd))

## Description

Row 1 shows the project label: the last path component of the session's project
directory, taken from `workspace.project_dir`, else `workspace.current_dir`, else `cwd`,
after Python `normpath` (so a trailing slash is ignored and the root shows `/`). The label
is grey and is omitted when no directory is known.

Notation: `\e` is the byte 0x1B.

## Preconditions

1. stdin decoded to an object `d` (BC-1.01.002).
2. `ws = d.workspace` if truthy else `{}`; a truthy non-object `workspace` is out of
   contract (EC-006).
3. `proj_dir` = first truthy of (`ws.project_dir`, `ws.current_dir`, `d.cwd`), else `""`.

## Postconditions

1. If `proj_dir` is falsy: no branch segment and no project label are emitted.
2. If `proj_dir` is truthy (a string):
   - the branch segment (BC-1.02.005) is computed first from the **raw** `proj_dir` and,
     when non-empty, appended before the label;
   - `pname = basename(normpath(proj_dir))`, or `normpath(proj_dir)` when that basename
     is empty; `normpath`/`basename` are the host OS's Python path module (posixpath on
     macOS/Linux, ntpath on Windows), ported in `pyfmt` (BC-5.03.004);
   - the label segment is exactly `\e[90m` + `pname` + `\e[0m` (GREY/RESET from
     `statusline.theme.*`, OD-113).
3. Segment order in row 1: pill, model label, [branch], [project label], then the context
   widgets.

## Invariants

1. The label is derived without filesystem access (pure string operation); only the
   branch lookup touches the filesystem.
2. `pname` is never empty when `proj_dir` is non-empty.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | trailing slash `/x/p/` | label `p` (normpath drops it) |
| EC-002 | root `/` | basename empty → label `/` |
| EC-003 | `..` segments `/a/../b` | label `b` (lexical normpath, no symlink resolution) |
| EC-004 | relative `.` / `rel/dir` | label `.` / `dir` (no abspath for the label) |
| EC-005 | `project_dir` `""` with `current_dir` `/w/c` | label `c` (empty string falls through) |
| EC-006 | truthy non-string dir (e.g. `5`, `["a"]`) or truthy non-object `workspace` | legacy raises (AttributeError/TypeError) → guard line `\e[90mstatusline degraded\e[0m\n`, exit 0 (BC-1.01.001) |
| EC-007 | `"//"` and Windows path forms | POSIX keeps `//`; ntpath variants — contract BC-1.02.022 |
| EC-008 | `/x/p` vs `/x/p/` | same label, but different git cache keys (BC-1.02.005), by design of legacy |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7, macOS posixpath) on 2026-11-15; git
disabled so only the label varies.

| Input | Expected label segment | Category |
|-------|----------------|----------|
| `{"workspace":{"project_dir":"/x/p"}}` | `\e[90mp\e[0m` | happy-path |
| `{"workspace":{"project_dir":"/x/p/"}}` | `\e[90mp\e[0m` | edge-case |
| `{"workspace":{"project_dir":"/"}}` | `\e[90m/\e[0m` | edge-case |
| `{"workspace":{"current_dir":"/a/../b"}}` | `\e[90mb\e[0m` | edge-case |
| `{"workspace":{"project_dir":"","current_dir":"/w/c"}}` | `\e[90mc\e[0m` | edge-case |
| `{"cwd":"/q/r"}` | `\e[90mr\e[0m` | edge-case |
| `{"cwd":"."}` | `\e[90m.\e[0m` | edge-case |
| `{"workspace":{}}` | no label (row 1 = pill, model, ...) | edge-case |
| `{"workspace":{"project_dir":5}}` | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 | error |
| `{"workspace":"abc"}` | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | For all non-empty strings, label = `pyfmt.Basename(pyfmt.Normpath(s))` or the normpath when empty, per host OS | property test against CPython goldens (BC-5.03.004) |
| VP-028 | Label bytes equal the oracle on Tier A cases, per OS | parity harness |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:render_lane (SL:451-452, 454, 458-462) |
| Legacy contract | BC-SL-008 |
| Parity class | byte-exact (no exclusion-list entry) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-113 (theme keys), D5 (cross-platform: per-OS path module) |
| Config keys | `statusline.theme.*` (grey, reset) |
| Architecture Module | `internal/statusline/lane.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.005 — composes with (branch segment precedes the label, keyed on the raw dir)
- BC-1.02.022 — composes with (`//` and ntpath quirks)
- BC-5.03.004 — depends on (Normpath/Basename per OS)
- BC-6.03.001 — related to (OS-specific golden variants)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#lane` — internal/statusline/lane.go (project basename) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row-1 lane segments story

## VP Anchors (Recommended)

- VP-028 — label derivation property

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`render_lane`, SL:451-462) |
| **Confidence** | high (pass-3 HIGH-R, 7 cases) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if proj_dir:` (SL:454), `if pname:` (SL:461)
- **documentation**: comment SL:458-459 (review 2026-11-13 #4.1)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none for the label (the branch lookup is separate) |
| **Global state access** | none |
| **Deterministic** | yes (per OS) |
| **Thread safety** | n.a. |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed. Never use Go `filepath.Clean` directly: it differs from posixpath on
`//` (BC-1.02.022); use the `pyfmt` port.
