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
  - ../../../docs/PLAN.md
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; no legacy counterpart)"
subsystem: "SS-02"
capability: "CAP-015"
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

# Behavioral Contract BC-2.03.002: hylo config path prints the config, cache and state paths (OD-132)

## Description

`hylo config path` prints all three per-user paths hylo uses on this OS — the config file,
the cache directory and the state directory — one per line in that fixed order with fixed
labels, built explicitly per OD-95 and OD-132 (never `os.UserConfigDir`, which on macOS
gives `~/Library/Application Support`). An explicit `--config <path>` or `HYLO_CONFIG`
overrides the config line only. The command neither reads nor creates any file; in P1 the
file layer does not exist yet (OD-107), so the output is informational. It ships in P1
(OD-107).

## Preconditions

1. Invoked as `hylo config path` or `hylo config path --config <path>`.

## Postconditions

1. stdout is exactly three LF-terminated lines, in this fixed order with these fixed
   labels (OD-132): `config: <path>\n`, `cache: <path>\n`, `state: <path>\n`; exit 0;
   nothing on stderr on success.
2. Per-line resolution:
   - `config:` the resolved config FILE path. Order: (a) `--config <path>`; else
     (b) `HYLO_CONFIG` when present and non-empty; else (c) the per-OS default:
     macOS and Linux `$XDG_CONFIG_HOME/hylo/config.yaml` when `XDG_CONFIG_HOME` is set,
     non-empty and absolute (a relative value is ignored, per the XDG spec and OD-144),
     otherwise `$HOME/.config/hylo/config.yaml`; Windows `%APPDATA%\hylo\config.yaml`.
     The per-OS directory comes from `internal/platform.ConfigDir()` (BC-3.01.001).
   - `cache:` the hylo cache DIRECTORY (`CacheDir()`, BC-3.01.001) — on Windows
     `%LOCALAPPDATA%\hylo\cache` (OD-144 subdirectory ruling).
   - `state:` the hylo state DIRECTORY (`StateDir()`, BC-3.01.001) — on Windows
     `%LOCALAPPDATA%\hylo\state` (OD-144).
3. Override paths (a)/(b) get `~` expansion (OD-61, BC-2.01.005) and are otherwise printed
   as given (not made absolute, not cleaned). Overrides apply to the `config:` line only.
4. If the base needed by a line is unset or empty (`HOME`/`APPDATA`/`LOCALAPPDATA`, or the
   home for a `~` override): that line prints `<label>: (unavailable)`, stderr carries
   `hylo: config path: cannot determine <label> directory (<VAR> unset)\n`, and the exit
   code is 1; the other lines still print their resolved paths.
5. The files are not opened, stat'ed or created; `HYLO_*` settings are not validated (a
   config error does not affect this command).
6. Any other argument or flag: usage on stderr (BC-4.01.001 golden), exit 2.

## Invariants

1. Output is a pure function of argv and the environment variables named above.
2. The default paths match PLAN §6 ("Config") and OD-95; the three-line contract (order,
   labels) is OD-132.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Linux, `XDG_CONFIG_HOME=/x`, `HOME=/home/user` | `config: /x/hylo/config.yaml`; `cache: /home/user/.cache/hylo`; `state: /home/user/.local/state/hylo` |
| EC-002 | Linux, `XDG_CONFIG_HOME=rel` | `config: /home/user/.config/hylo/config.yaml` (relative XDG ignored, OD-144) |
| EC-003 | macOS, no XDG | `config: $HOME/.config/hylo/config.yaml` (not `~/Library/...`) |
| EC-004 | Windows, `APPDATA=C:\Users\user\AppData\Roaming`, `LOCALAPPDATA=C:\Users\user\AppData\Local` | `config: C:\Users\user\AppData\Roaming\hylo\config.yaml`; `cache: C:\Users\user\AppData\Local\hylo\cache`; `state: C:\Users\user\AppData\Local\hylo\state` (OD-144) |
| EC-005 | `HYLO_CONFIG=~/alt.yaml`, `HOME=/home/user` | `config: /home/user/alt.yaml` |
| EC-006 | `--config ./c.yaml` and `HYLO_CONFIG=/y.yaml` | `config: ./c.yaml` (flag wins) |
| EC-007 | `HYLO_CONFIG=` (empty) | ignored; per-OS default |
| EC-008 | Unix, `HOME` and `XDG_CONFIG_HOME` unset | three lines all `(unavailable)`; stderr `hylo: config path: cannot determine config directory (HOME unset)`, exit 1 |
| EC-009 | `HYLO_STATUSLINE_ROWS=x` set | paths printed normally, exit 0 |
| EC-010 | Windows, `LOCALAPPDATA` unset, `APPDATA` set | `config:` resolves; `cache: (unavailable)` and `state: (unavailable)`; stderr detail twice; exit 1 |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Linux, env `{HOME: "/home/user"}` | stdout `config: /home/user/.config/hylo/config.yaml\ncache: /home/user/.cache/hylo\nstate: /home/user/.local/state/hylo\n`, exit 0 | happy-path |
| env `{HOME: "/home/user", HYLO_CONFIG: "/etc/hylo.yaml"}` | `config: /etc/hylo.yaml` line; cache/state lines unchanged; exit 0 | edge-case |
| Windows, env without `APPDATA` | `config: (unavailable)`; stderr `hylo: config path: cannot determine config directory (APPDATA unset)\n`; exit 1 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-004, VP-032 | Per-OS default table holds on each CI OS (ubuntu, macos, windows) | table test with injected env |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-95 (explicit per-OS paths, XDG honored, `%APPDATA%` on Windows, `HYLO_CONFIG` / `--config` override, `hylo config path` prints paths), OD-132 (prints all three paths: config, cache, state, fixed order and labels), OD-107 (ships in P1; file not read until P4), OD-61; PLAN §6 "Config" |
| Parity / exclusion | n.a. |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-010 |
| Architecture Module | `cmd/hylo/config.go`, `internal/platform/paths*.go` (BC-COMPONENT-MAP: cmd/hylo/config.go (path printing, OD-132) — ARCH-01) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-3.01.001 — depends on (per-OS config dir)
- BC-2.01.005 — depends on (`~` expansion)
- BC-4.01.001 — depends on (dispatch)

## Architecture Anchors (Recommended)

- `architecture/ARCH-01-binary-cli.md#config` — cmd/hylo/config.go (path printing, OD-132) (config subcommands) (BC-COMPONENT-MAP: ARCH-01 (ARCH-01-binary-cli.md))

## Story Anchor (Recommended)

S-TBD — config subcommands

## VP Anchors (Recommended)

- VP-004, VP-032 — per-OS path table
