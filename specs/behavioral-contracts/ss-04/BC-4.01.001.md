---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - ../owner-decisions-log-2026-11-14.md
  - ../../semport/hylo-legacy/statusline-target-design.md
  - ../../../docs/RESUME.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; legacy entry point legacy/dgx_statusline.py SL:1238-1245 is the statusline-only analogue)"
subsystem: "SS-04"
capability: "CAP-009"
legacy_id: new
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

# Behavioral Contract BC-4.01.001: Dispatch statusline / version / config; statusline exits 0 for any argv

## Description

`cmd/hylo` dispatches on the first argument to one of the P1 subcommands: `statusline`,
`version`, `config validate`, `config path` (RESUME step 1; OD-95, OD-102, OD-107). The
`statusline` path returns exit status 0 for every argv, every environment and every stdin,
including panics (recovered to the degraded line), matching the legacy guard (SL:1238-1245,
"never blank, never nonzero"). Other subcommands use conventional exit codes.

## Preconditions

1. `main` calls `run(os.Args[1:], stdin, stdout, stderr)` and exits with its return value
   (design §2.1).

## Postconditions

1. `args[0] == "statusline"` → `runStatusline(args[1:], ...)`, which **always returns 0**.
   Within it: unknown flags → BC-4.01.002; config errors → BC-2.02.001; any render fault →
   the degraded line (BC-1.01.001); any panic is recovered and mapped to the degraded line.
   Positional (non-flag) arguments are ignored (legacy reads nothing from argv except
   `--subagent`, SL:1240).
2. `args[0] == "version"` → BC-4.01.003.
3. `args[0] == "config"` and `args[1] == "validate"` → BC-2.03.001; `args[1] == "path"` →
   BC-2.03.002.
4. `args` empty, or `args[0]` not one of the above (including `config` alone or
   `config <other>`): usage text on stderr, exit 2. Usage bytes are pinned by the golden
   `cmd/hylo/testdata/usage.golden`, which lists the four P1 command forms.
5. `args[0]` is `help`, `-h` or `--help` → the same usage text on stdout, exit 0.
6. Dispatch reads no config and touches no file before the subcommand runs; only the
   statusline path reads stdin.

## Invariants

1. `runStatusline` never returns non-zero and never leaves stdout empty (DI-008).
2. Go stdlib `flag.ExitOnError` (exit 2, blank output) is never used on the statusline path
   (OD-112).
3. No command name, binary name or output contains "Claude" as a product name (CLAUDE.md
   trademark rule); "for Claude Code" only in descriptive help text if at all.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `hylo statusline extra positional` | normal render; exit 0 |
| EC-002 | `hylo statusline` with stdin closed / empty | renders from `{}` (BC-1.01.002); exit 0 |
| EC-003 | `hylo statusline` where a widget panics (fault injection) | degraded line `\e[90mstatusline degraded\e[0m\n` (`\e` = 0x1B); exit 0 |
| EC-004 | `hylo` (no args) | usage on stderr; exit 2 |
| EC-005 | `hylo status` (typo) | usage on stderr; exit 2 |
| EC-006 | `hylo config` | usage on stderr; exit 2 |
| EC-007 | `hylo --help` | usage on stdout; exit 0 |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| argv `statusline`, stdin `{}`, env `{}` | S1 render bytes (golden); exit 0 | happy-path |
| argv `statusline foo bar` | same bytes as argv `statusline`; exit 0 | edge-case |
| argv `frobnicate` | stdout empty; stderr = `usage.golden`; exit 2 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-004 | For all argv with `args[0]=="statusline"`, all env, all stdin: exit 0 and stdout ends with `\n` and is non-empty | fuzz (`go test -fuzz`) |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — design §2.1 (`cmd/hylo` dispatch, `runStatusline` always 0), RESUME P1 step 1 (`hylo statusline`, `hylo version`), OD-102 / OD-95 / OD-107 (config validate / path in P1), tension T6; legacy analogue: legacy/dgx_statusline.py:`__main__` guard (SL:1238-1245) |
| Parity / exclusion | n.a. (dispatch adds no status line bytes; the statusline path's output is governed by S1 BCs) |
| L2 Capability | CAP-009, CAP-015 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `cmd/hylo/main.go`, `statusline.go` (BC-COMPONENT-MAP: cmd/hylo/main.go + statusline.go (dispatch) — ARCH-01) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-4.01.002 — composes with (unknown flags on statusline)
- BC-4.01.003 — composes with (version)
- BC-2.03.001, BC-2.03.002 — composes with (config subcommands)
- BC-1.01.001 — depends on (degraded line)

## Architecture Anchors (Recommended)

- `architecture/ARCH-01-binary-cli.md#dispatch` — cmd/hylo/main.go + statusline.go (dispatch) (subcommand dispatch) (BC-COMPONENT-MAP: ARCH-01 (ARCH-01-binary-cli.md))

## Story Anchor (Recommended)

S-TBD — skeleton + dispatch (RESUME P1 step 1)

## VP Anchors (Recommended)

- VP-004 — statusline always exits 0

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | `os.Args`/`os.Std*`, `os.Exit` |
| **Global state access** | process exit status |
| **Deterministic** | no (process boundary) |
| **Thread safety** | n.a. |
| **Overall classification** | effectful shell |

Owning component `cmd/hylo` (BC-COMPONENT-MAP: cmd/hylo/main.go + statusline.go (dispatch) - ARCH-01); the ARCH-00 package table classifies the package effectful shell - `os.Args`/`os.Std*`, `os.Exit`, no logic.
