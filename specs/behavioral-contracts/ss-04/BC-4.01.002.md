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
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; legacy --subagent dispatch at legacy/dgx_statusline.py SL:1240-1241 is not ported, OD-14)"
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

# Behavioral Contract BC-4.01.002: Unknown flag renders one-line error, exit 0, never blank (incl. leftover --subagent)

> Notation: `\e` is the byte 0x1B (ESC); `\n` is 0x0A. Byte strings are exact.

## Description

`hylo statusline` defines no flags in P1. Any flag-shaped argument — including a leftover
`--subagent` from a legacy `subagentStatusLine` wiring (OD-14: not ported) — makes it print
exactly one grey line `hylo: unknown flag <flag>` and exit 0, never a blank line and never a
non-zero status (OD-112, same rule as D4-EX-3).

## Preconditions

1. Invoked as `hylo statusline <args...>`.
2. A **flag** is an argument that starts with `-`, is not exactly `-`, and appears before a
   `--` terminator. `--` itself ends flag scanning; later arguments are positional.

## Postconditions

1. If at least one flag is present, stdout is exactly
   `\e[90m` + `hylo: unknown flag ` + `<flag>` + `\e[0m` + `\n` for the **first** flag in
   argv order, where `<flag>` is the whole argument as given (including any `=value`),
   escaped by the BC-2.02.001 `<value>` rule (control bytes and invalid UTF-8 → `\xNN`).
2. Exit status is 0.
3. stderr receives `hylo: unknown flag <flag> (hylo statusline takes no flags)\n` for each
   flag in argv order.
4. The check runs before configuration resolution: an unknown flag takes precedence over a
   config error (BC-2.02.001 is not printed). No stdin read is required, no cache file is
   read or written, no network request or subprocess runs.
5. Positional arguments alone (no flag) do not trigger this BC; the normal render runs
   (BC-4.01.001).

## Invariants

1. Never blank, never non-zero (DI-008).
2. The grey pair is the built-in literal (`\e[90m`/`\e[0m`), independent of
   `statusline.theme.*`, like the config-error line.
3. `--subagent` has no special handling: it is an unknown flag like any other (the
   agent-panel row is out of scope, OD-14; BC-SL-097 not ported).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `hylo statusline --subagent` | `\e[90mhylo: unknown flag --subagent\e[0m\n`, exit 0 |
| EC-002 | `hylo statusline -h` | `\e[90mhylo: unknown flag -h\e[0m\n`, exit 0 |
| EC-003 | `hylo statusline --config=x.yaml` | `\e[90mhylo: unknown flag --config=x.yaml\e[0m\n`, exit 0 (no config flag on statusline in P1) |
| EC-004 | `hylo statusline -- --subagent` | normal render (after `--`), exit 0 |
| EC-005 | `hylo statusline -` | normal render (`-` is positional), exit 0 |
| EC-006 | `hylo statusline foo --a --b` | line names `--a`; stderr lists `--a` and `--b` |
| EC-007 | `--subagent` plus `HYLO_STATUSLINE_TELEMETRY_TTL_S=nan` | unknown-flag line (precedence), exit 0 |
| EC-008 | flag containing a newline `$'--a\nb'` | `\e[90mhylo: unknown flag --a\x0ab\e[0m\n` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| argv `statusline`, stdin `{}` | normal S1 render; exit 0 | happy-path |
| argv `statusline --subagent`, any stdin/env | stdout `\e[90mhylo: unknown flag --subagent\e[0m\n` (bytes `1b 5b 39 30 6d` + `hylo: unknown flag --subagent` + `1b 5b 30 6d 0a`); exit 0; cache dir unchanged | error |
| argv `statusline -- -x` | normal render; exit 0 | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-002 | For any argv containing a flag before `--`: stdout is one line beginning `\e[90mhylo: unknown flag `, exit 0 | fuzz |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-112 (T8: unknown flag incl. leftover `--subagent` → `hylo: unknown flag ...`, exit 0), OD-14 (`--subagent` not ported), DI-008; legacy reference: legacy/dgx_statusline.py:`__main__` (SL:1240-1241 `--subagent` dispatch; SL:1243-1245 never-nonzero guard) |
| Parity / exclusion | n.a.: no parity case passes flags (the harness invokes `hylo statusline` without flags; legacy `--subagent` mode is out of scope, BC-SL-097 OOS). Covered by its own Go table test `TestStatusline_UnknownFlag` |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `cmd/hylo/statusline.go` (BC-COMPONENT-MAP: cmd/hylo/statusline.go (unknown-flag scan) — ARCH-01) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-4.01.001 — depends on (dispatch)
- BC-2.02.001 — related to (same one-line/exit-0 rule; escaping rule reused; this BC takes precedence)
- BC-1.01.001 — related to (degraded line)

## Architecture Anchors (Recommended)

- `architecture/ARCH-01-binary-cli.md#statusline-args` — cmd/hylo/statusline.go (unknown-flag scan) (statusline argument handling) (BC-COMPONENT-MAP: ARCH-01 (ARCH-01-binary-cli.md))

## Story Anchor (Recommended)

S-TBD — skeleton + dispatch

## VP Anchors (Recommended)

- VP-002 — unknown flag never blank
