---
document_type: behavioral-contract
level: L3
version: "1.1.5"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "06d6b68"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; --subagent is a valid P1 flag dispatched per BC-1.07.*, OD-155; legacy reference: the --subagent dispatch at legacy/dgx_statusline.py SL:1240-1241)"
subsystem: "SS-04"
capability: "CAP-009"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.1.2 2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "1.1.3 2026-11-18T01:42:00Z ADV-P3 remediation D05+D28: EC-004 exempts --subagent anywhere in argv[1:] incl. after -- (OD-155, SL:1240); stderr suffix amended"
  - "1.1.4 2026-11-18: ADV-P4 remediation D05 - parity argv row corrected: case argv admits only [] and [\"--subagent\"] in P1 (design call 9); subagent mode performs no flag validation (PC-4 qualifier); pass-4 sync-check SC-07 — repaired the unescaped double quotes that broke YAML parsing; no behavioral change"
  - "2026-11-19T21:00:00Z (1.1.5): ADV-P8 remediation D23 — VP-002 row states the --subagent routing carve-out the VP file already had (exact-argument --subagent routes before flag handling)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-4.01.002: Unknown flag renders one-line error, exit 0, never blank

> Notation: `\e` is the byte 0x1B (ESC); `\n` is 0x0A. Byte strings are exact.

## Description

`hylo statusline` defines no other flags in P1 (`--subagent` is a VALID flag in P1, OD-155:
it dispatches the subagent status line mode, BC-1.07.*). Any other flag-shaped argument (any argument other than `--subagent` and the `--`
terminator) makes
it print
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
3. stderr receives `hylo: unknown flag <flag> (--subagent is the only P1 flag)\n` for each
   flag in argv order (suffix amended per ADV-P3-D28; the former "takes no flags" text is
   false since OD-155).
4. The check runs before configuration resolution: an unknown flag takes precedence over a
   config error (BC-2.02.001 is not printed). MAIN MODE ONLY — the subagent mode performs
   no flag validation at all (BC-2.02.001 PC-8, ADV-P4-D04). No stdin read is required, no
   cache file is
   read or written, no network request or subprocess runs.
5. Positional arguments alone (no flag) do not trigger this BC; the normal render runs
   (BC-4.01.001).

## Invariants

1. Never blank, never non-zero (DI-008).
2. The grey pair is the built-in literal (`\e[90m`/`\e[0m`), independent of
   `statusline.theme.*`, like the config-error line.
3. `--subagent` is a valid flag in P1 (OD-155): it dispatches the subagent status line mode
   (BC-1.07.*) and never reaches the unknown-flag path of this BC. Every flag other than
   `--subagent` (and the `--` terminator) is unknown and handled here.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `hylo statusline --subagent` | NOT this BC: `--subagent` is valid in P1 (OD-155), dispatched per BC-1.07.* |
| EC-002 | `hylo statusline -h` | `\e[90mhylo: unknown flag -h\e[0m\n`, exit 0 |
| EC-003 | `hylo statusline --config=x.yaml` | `\e[90mhylo: unknown flag --config=x.yaml\e[0m\n`, exit 0 (no config flag on statusline in P1) |
| EC-004 | `hylo statusline -- --subagent` | NOT a normal render: `--subagent` ANYWHERE in argv[1:] routes to the subagent mode before any flag handling, including after `--` (OD-155; legacy SL:1240 `"--subagent" in sys.argv[1:]`; ADV-P3-D05, aligning with BC-1.07.001 PC-4) |
| EC-005 | `hylo statusline -` | normal render (`-` is positional), exit 0 |
| EC-006 | `hylo statusline foo --a --b` | line names `--a`; stderr lists `--a` and `--b` |
| EC-007 | `-h` plus `HYLO_STATUSLINE_TELEMETRY_TTL_S=nan` | unknown-flag line (precedence over the config error), exit 0 |
| EC-008 | flag containing a newline `$'--a\nb'` | `\e[90mhylo: unknown flag --a\x0ab\e[0m\n` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| argv `statusline`, stdin `{}` | normal S1 render; exit 0 | happy-path |
| argv `statusline --leftover`, any stdin/env | stdout `\e[90mhylo: unknown flag --leftover\e[0m\n` (bytes `1b 5b 39 30 6d` + `hylo: unknown flag --leftover` + `1b 5b 30 6d 0a`); exit 0; cache dir unchanged | error |
| argv `statusline -- -x` | normal render; exit 0 | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-002 | For any argv containing a flag before `--` (MAIN-mode statusline only: the exact argument `--subagent` routes to the subagent renderer before flag handling, so subagent-mode argv is carved out of this row): stdout is one line beginning `\e[90mhylo: unknown flag `, exit 0 | fuzz |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-112 (T8: unknown flag → `hylo: unknown flag ...`, exit 0), OD-155 (owner ruling 2026-11-17: `--subagent` IS a valid P1 flag, dispatched per BC-1.07.*), DI-008; legacy reference: legacy/dgx_statusline.py:`__main__` (SL:1240-1241 `--subagent` dispatch; SL:1243-1245 never-nonzero guard); parity argv correction ADV-P4-D05 (design call 9) |
| Parity / exclusion | n.a.: a parity case's handler-relative `argv` (after the `statusline` verb, BC-6.01.001 PC-5) admits only `[]` and `["--subagent"]` in P1 (orchestrator design call 9, ADV-P4-D05/D09), so no parity case passes a flag — the oracle receives `[python, -s, script]` plus the same list; every other argv shape (unknown flags, `--`, positionals) is covered by this BC's Go table tests, never parity. Covered by its own Go table test `TestStatusline_UnknownFlag` |
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

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | `os.Args`/`os.Std*`, `os.Exit` |
| **Global state access** | process exit status |
| **Deterministic** | no (process boundary) |
| **Thread safety** | n.a. |
| **Overall classification** | effectful shell |

Owning component `cmd/hylo` (BC-COMPONENT-MAP: cmd/hylo/statusline.go (unknown-flag scan) - ARCH-01); the ARCH-00 package table classifies the package effectful shell - `os.Args`/`os.Std*`, `os.Exit`, no logic.
