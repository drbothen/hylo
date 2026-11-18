---
document_type: behavioral-contract
level: L3
version: "1.2.8"
status: draft
producer: product-owner
timestamp: 2026-11-21T07:00:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - docs/PLAN.md
input-hash: "f60a5ff"
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
modified:
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T00:30:00Z (1.2.3): ADV-P4 remediation D20 — empty HYLO_PATHS_CACHE_DIR reports the same empty-path error as the status line (no platform-default fallback, OD-165)"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D36: empty override = not present; trailing separator printed as given, OD-165 agreement held at Clean-ed granularity"
  - "2026-11-19T04:45:00Z (1.2.4): ADV-P6 remediation D20 — PC-5 tension resolved: the no-validation claim is scoped to HYLO_* CONFIG-VALUE settings; the two path overrides the command consumes (HYLO_CONFIG, HYLO_PATHS_CACHE_DIR) keep their full path grammar including the empty-path error (PC-3/EC-011 stand)"
  - "2026-11-19T17:45:00Z: ADV-P7 remediation D27 - the --config=<path> equals spelling parses as the separated form; a bare --config is a flag error on the golden usage surface, exit 2 (BC-4.01.001 PC-3 cross-referenced)"
  - "2026-11-19T21:00:00Z (1.2.6): ADV-P8 remediation D01 — the three directory resolvers carry the env seam everywhere in this file: ConfigDir(env EnvVars), CacheDir(env EnvVars), StateDir(env EnvVars), matching BC-3.01.001 and ARCH-05"
  - "2026-11-21T06:00:00Z (1.2.7): ADV-P10 remediation D03 (orchestrator call 3) — the pass-9 A11 absoluteness rule propagated to its sibling: a RELATIVE HYLO_PATHS_CACHE_DIR reports the same config error as the status line's grammar (not an absolute path; cache: (unavailable), stderr detail, exit 1 — new EC-012); absoluteness is filepath.IsAbs semantics computed in internal/platform per OS (Windows: drive + root or UNC); HYLO_CONFIG is reserved for P4 and printed as given, no absoluteness check (PC-3/PC-5 scope note)"
  - "2026-11-21T07:00:00Z (1.2.8): ADV-P11 remediation D07 — PC-3's absoluteness scope note names the registry key as paths.cache_dir (the statusline. prefix spelled at :84 was a mis-anchor; the env name HYLO_PATHS_CACHE_DIR only fits paths.cache_dir)"
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
gives `~/Library/Application Support`). Every line prints the EFFECTIVE path (OD-165,
fixing ADV-P2-D11): the `config:` line applies its `--config <path>` / `HYLO_CONFIG`
override, and the `cache:` line applies the `paths.cache_dir` env override
(`HYLO_PATHS_CACHE_DIR`, BC-3.01.001 PC-3) — the same directory the status line actually
uses — not the platform default `CacheDir(env EnvVars)`. The command neither reads nor creates any
file; in P1 the
file layer does not exist yet (OD-107), so the output is informational. It ships in P1
(OD-107).

## Preconditions

1. Invoked as `hylo config path`, `hylo config path --config <path>` or the EQUALS
   spelling `hylo config path --config=<path>`, which parses exactly as the separated
   form (Go `flag` package convention; pass-7 D27). A BARE `--config` with no value is
   a flag error of the subcommand: usage text on stderr (BC-4.01.001's golden surface),
   exit 2, no stdout.

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
     The per-OS directory comes from `internal/platform.ConfigDir(env EnvVars)` (BC-3.01.001).
   - `cache:` the EFFECTIVE status-line cache directory (OD-165): `paths.cache_dir` after
     `~` expansion when the env override `HYLO_PATHS_CACHE_DIR` is set
     (BC-3.01.001 PC-3), otherwise the platform default (`CacheDir(env EnvVars)`, BC-3.01.001) — on
     Windows `%LOCALAPPDATA%\hylo\cache` (OD-144 subdirectory ruling).
   - `state:` the hylo state DIRECTORY (`StateDir(env EnvVars)`, BC-3.01.001) — on Windows
     `%LOCALAPPDATA%\hylo\state` (OD-144).
3. Override paths (a)/(b) get `~` expansion (OD-61, BC-2.01.005) and are otherwise printed
   as given (not made absolute, not cleaned). Absoluteness scope (ADV-P10-D03,
   orchestrator call 3): only `paths.cache_dir` (`HYLO_PATHS_CACHE_DIR`) must
   be ABSOLUTE — a relative value is a config error, reported exactly as the status
   line's grammar reports it (`not an absolute path`, BC-2.01.005 PC-3; the pass-4
   call-16 empty-path disposition in the same shape): `cache: (unavailable)`, stderr
   `hylo: config path: cannot determine cache directory (not an absolute path)\n`, exit 1.
   Absoluteness is `filepath.IsAbs` semantics computed in `internal/platform` per OS
   (Windows: drive + root or UNC; `\foo` and `C:foo` are relative). `HYLO_CONFIG` is
   reserved for P4 and is printed as given — no absoluteness check applies to it (EC-006
   stands). Overrides are applied wherever they exist:
   `config:` (a)/(b) and `cache:` (`HYLO_PATHS_CACHE_DIR`); the state directory has no
   override in P1 (OD-165). Edge discipline (ADV-P3-D36, amended ADV-P4-D20): an override
   that is set but EMPTY splits by label — `HYLO_CONFIG=` counts as not present (the
   (a)/(b)/(c) fallback proceeds as if the variable were unset, ADV-P1-D25), while
   `HYLO_PATHS_CACHE_DIR=` does NOT fall back to the platform default: it reports the same
   `empty path` error the status line's grammar raises (BC-2.01.005 PC-3, BC-2.01.001 PC-2),
   keeping OD-165's agreement that `config path` and the status line resolve the same
   cache directory. Observable per PC-4: the `cache:` line prints `cache: (unavailable)`,
   stderr carries `hylo: config path: cannot determine cache directory (empty path)\n`,
   and the exit code is 1. A trailing separator in an override is printed exactly
   as given (`/tmp/x/` prints with the slash); this is a PRINT ordering only — OD-165's
   "the status line and `config path` agree on the same directory" holds at
   resolved-directory granularity (Clean-ed), not byte-for-byte on the printed string.
4. If the base needed by a line is unset or empty (`HOME`/`APPDATA`/`LOCALAPPDATA`, or the
   home for a `~` override): that line prints `<label>: (unavailable)`, stderr carries
   `hylo: config path: cannot determine <label> directory (<VAR> unset)\n`, and the exit
   code is 1; the other lines still print their resolved paths. One stderr line prints
   PER unavailable line — if all three lines are unavailable, stderr carries three detail
   lines in label order (config, cache, state) (ADV-P1-D13). `<VAR>` is the unset base of
   that line: `HOME` (macOS/Linux), `APPDATA`/`LOCALAPPDATA` (Windows), and for a `~`
   override on Windows `USERPROFILE` (OD-61).
5. The files are not opened, stat'ed or created; `HYLO_*` CONFIG-VALUE settings are not
   validated — an invalid number, boolean, URL or Text value anywhere in the registry does
   not affect this command (the resolved config is never loaded here). The exceptions are
   the two path overrides this command itself consumes and expands: `HYLO_CONFIG` and
   `HYLO_PATHS_CACHE_DIR`, whose path grammar (including the empty-path error, PC-3/EC-011)
   applies in full (ADV-P6-D20 resolves the PC-3/PC-5 tension); the absoluteness
   requirement applies ONLY to `HYLO_PATHS_CACHE_DIR` — `HYLO_CONFIG` is reserved for P4
   and printed as given, with no absoluteness check (PC-3; ADV-P10-D03c).
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
| EC-008 | Unix, `HOME` and `XDG_CONFIG_HOME` unset | three lines all `(unavailable)`; three stderr lines — `...config directory (HOME unset)`, `...cache directory (HOME unset)`, `...state directory (HOME unset)` in label order; exit 1 |
| EC-009 | `HYLO_STATUSLINE_ROWS=x` set | paths printed normally, exit 0 |
| EC-010 | Windows, `LOCALAPPDATA` unset, `APPDATA` set | `config:` resolves; `cache: (unavailable)` and `state: (unavailable)`; stderr detail twice; exit 1 |
| EC-011 | `HYLO_PATHS_CACHE_DIR=` (present, empty) | `cache: (unavailable)`; stderr `hylo: config path: cannot determine cache directory (empty path)`; exit 1 — same `empty path` error as the status line (ADV-P4-D20) |
| EC-012 | `HYLO_PATHS_CACHE_DIR=rel` (present, relative) | `cache: (unavailable)`; stderr `hylo: config path: cannot determine cache directory (not an absolute path)`; exit 1 — same `not an absolute path` config error as the status line (BC-2.01.005 PC-3; ADV-P10-D03) |

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

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | `os.Args`/`os.Std*`, `os.Exit` |
| **Global state access** | process exit status |
| **Deterministic** | no (process boundary) |
| **Thread safety** | n.a. |
| **Overall classification** | effectful shell |

Owning component `cmd/hylo` (BC-COMPONENT-MAP: cmd/hylo/config.go (path printing, OD-132) - ARCH-01); the ARCH-00 package table classifies the package effectful shell - `os.Args`/`os.Std*`, `os.Exit`, no logic.
