---
document_type: behavioral-contract
level: L3
version: "1.2.3"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, owner-decisions-log-2026-11-14.md, semport/hylo-legacy/statusline-target-design.md, research/general-go-port-parity-crossplatform-2026-11-14.md]
input-hash: "fd7637c"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; replaces legacy CACHE_DIR at legacy/dgx_statusline.py SL:78)"
subsystem: "SS-03"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z ADV-P3 remediation D17: default exceptions aligned with BC-2.01.004 PC-4 (two exceptions, OD-101 + OD-111)"
  - "1.2.2 2026-11-18: ADV-P4 remediation D21/D30 — platform LocalZone contract added (OD-171: TZ honoured on every OS, OS-zone fallback, TZ=UTC parity pins); purity table rescoped to the paths functions (pure over injected env)"
  - "2026-11-19T01:05:00Z (1.2.3) ADV-P5 remediation D23+D24 — PC-6 refined to OD-177 libc semantics on every OS: TZ unset → OS zone; TZ empty or unparseable → UTC (was OS zone); leading-colon TZ form pinned; canonical table legs gain empty; H1/Description now name the LocalZone responsibility (P7)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-3.01.001: Per-OS cache/config/state dirs (XDG/hylo, LOCALAPPDATA); LocalZone TZ resolution (OS zone, UTC on empty/unparseable)

## Description

`internal/platform` computes hylo's three per-user directories (cache, config, state) explicitly per OS, never through
`os.UserCacheDir`/`os.UserConfigDir` (which return `~/Library/...` on macOS). It also resolves the local zone (`LocalZone`, PC 6). From P1 on, the status line keeps its
status-line caches in hylo's own cache directory (OD-101), not in the legacy `~/.cache/dgx-llm` (SL:78). The functions
only compute paths; creating a directory is the cache store's job (BC-1.06.001).

## Preconditions

1. The process environment is readable. Inputs: `HOME` (macOS, Linux), `XDG_CACHE_HOME`, `XDG_CONFIG_HOME`,
   `XDG_STATE_HOME` (macOS, Linux), `LOCALAPPDATA`, `APPDATA` (Windows), and the config key `paths.cache_dir`
   (env `HYLO_PATHS_CACHE_DIR` in P1, OD-107).
2. The home directory comes from `os.UserHomeDir` (`HOME` on Unix, `USERPROFILE` on Windows).

## Postconditions

1. **macOS and Linux** (identical rules; macOS does not use `~/Library`):
   - `CacheDir()` = `$XDG_CACHE_HOME/hylo` if `XDG_CACHE_HOME` is set, non-empty and absolute; else `$HOME/.cache/hylo`.
   - `ConfigDir()` = `$XDG_CONFIG_HOME/hylo` under the same rule; else `$HOME/.config/hylo`.
   - `StateDir()` = `$XDG_STATE_HOME/hylo` under the same rule; else `$HOME/.local/state/hylo`.
2. **Windows:**
   - `CacheDir()` = `%LOCALAPPDATA%\hylo\cache`; `StateDir()` = `%LOCALAPPDATA%\hylo\state`
     (separate subdirectories, OD-144; amending the PLAN §6 "cache and state under
     `%LOCALAPPDATA%\hylo`" shared-dir reading); `ConfigDir()` = `%APPDATA%\hylo`.
   - `XDG_*` variables are ignored on Windows.
3. **Status-line cache directory** used by the cache store = the value of `paths.cache_dir` when set (after `~`
   expansion, OD-61), otherwise `CacheDir()`. The legacy literal `~/.cache/dgx-llm` is never used as a default and
   never read (OD-101, OD-05).
4. Paths are returned joined with the OS separator (`/` on Unix, `\` on Windows), with no trailing separator.
5. No directory is created and no file is touched by these functions.
6. **Local zone resolution (OD-171 as refined by OD-177, ADV-P4-D21):** `internal/platform`
   also provides
   `LocalZone(env) (*time.Location, error)`, the only way hylo derives its local zone
   (`Env.Loc` is populated from it; BC-5.04.001, BC-6.01.002, BC-6.02.003 route through
   it). On every OS it applies LIBC semantics (OD-177, ADV-P5-D23): (a) `TZ` set to a
   non-empty IANA name present in the zone database → that zone (`LoadLocation(name)`;
   one leading `:` is stripped before the lookup — libc file-reference form, a judgment
   call for `TZ=:Area/City`, non-parity-critical); (b) `TZ` set but EMPTY, or set and
   unparseable/unknown → **UTC** (libc verdict on every OS; this refines OD-171's
   earlier OS-zone fallback for these two cases); (c) `TZ` unset → the OS local zone.
   It never calls `time.Local` directly for the decision (Go's `time.Local`
   ignores `TZ` on Windows); the (c) fallback itself may resolve through the runtime's
   local-time machinery. Documented limitation (OD-171): POSIX-style TZ strings (e.g.
   `EST5EDT`) may differ between Go's zone loader and the MSVC runtime on Windows; parity
   cases therefore pin `TZ=UTC` only (parity harness, BC-6.01.002). Canonical table legs:
   `TZ` unset / `UTC` / IANA name / empty / unparseable.

## Invariants

1. The default of `paths.cache_dir` is one of the TWO explicit owner exceptions to D15's "defaults equal
   `legacy/` until cutover" (OD-101); its registry rationale cites OD-101. The other is
   `backends[0].model_prefixes` (`claude-sonnet`, OD-111, BC-2.01.004 PC-4). Every other P1 default equals
   legacy (ADV-P3-D17 alignment).
2. The last path component is always the literal `hylo` (product name; a format constant, not config).
3. The result depends only on the environment passed in (the function takes an env lookup, so tests inject it).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `XDG_CACHE_HOME=""` (set but empty) | Treated as unset: `$HOME/.cache/hylo` |
| EC-002 | `XDG_CACHE_HOME=rel/dir` (relative) | Ignored per the XDG Base Directory spec ("relative paths are invalid and should be ignored"): `$HOME/.cache/hylo`. Owner-ruled OD-144 (adopting the XDG-spec convention; empty values likewise ignored, EC-001) |
| EC-003 | `XDG_CACHE_HOME=/x/` (trailing slash) | `/x/hylo` (cleaned, no doubled separator) |
| EC-004 | Home directory cannot be determined and no XDG override applies (Unix), or `LOCALAPPDATA`/`APPDATA` empty (Windows) | The function returns an error ("unavailable"). The status line still renders: the never-raise cache helpers treat an unavailable dir as load-empty / save-no-op (BC-1.06.001). `hylo config path` reports the error (BC-2.03.002). Legacy instead used the literal relative path `~/.cache/dgx-llm` when `HOME` was unset; not a parity case |
| EC-005 | `HYLO_PATHS_CACHE_DIR=~/c` | `$HOME/c` (OD-61 `~` expansion); `CacheDir()` is not consulted |
| EC-006 | Windows with `XDG_CACHE_HOME` set | Ignored; `%LOCALAPPDATA%\hylo\cache` |
| EC-007 | Parity harness run (OD-101, design §3.2) | The harness sets `HYLO_PATHS_CACHE_DIR=<temp>/hylo-cache` and points `XDG_CACHE_HOME` and `LOCALAPPDATA` into the temp tree; caches are compared by file name across the two directories (design §5.3), so the directory difference is not a parity diff and needs no exclusion entry |
| EC-008 | `TZ=Europe/Paris` (valid IANA name) | `LocalZone` returns that zone, on all three OSes (OD-171) |
| EC-009 | `TZ=Not/AZone` (unparseable/unknown) | UTC (libc semantics, OD-177); no error surfaced to the renderer |
| EC-011 | `TZ=` (set but empty) | UTC (libc semantics, OD-177; Go `LoadLocation("")` agrees) |
| EC-012 | `TZ=:Europe/Paris` (leading colon) | the colon is stripped, Paris loads (libc file-reference form; judgment call, PC 6) |
| EC-010 | windows-2025 leg, naive local-time parity cases | executed with no skip — the harness pins `TZ=UTC` for both binaries, so the cases are OS-neutral (OD-171; VP-026's `posix-only` tag removed) |

## Canonical Test Vectors

Synthetic environments only (no real home paths).

| Input | Expected Output | Category |
|-------|----------------|----------|
| linux, `HOME=/t/h`, no XDG vars | cache `/t/h/.cache/hylo`, config `/t/h/.config/hylo`, state `/t/h/.local/state/hylo` | happy-path |
| darwin, `HOME=/t/h`, no XDG vars | same three paths as linux (not `~/Library/Caches`) | happy-path |
| linux, `HOME=/t/h`, `XDG_CACHE_HOME=/t/xc`, `XDG_STATE_HOME=/t/xs` | cache `/t/xc/hylo`, config `/t/h/.config/hylo`, state `/t/xs/hylo` | happy-path |
| windows, `LOCALAPPDATA=X:\local`, `APPDATA=X:\roaming` | cache `X:\local\hylo\cache`, state `X:\local\hylo\state`, config `X:\roaming\hylo` (OD-144 subdirectories) | happy-path |
| linux, `HOME=/t/h`, `XDG_CACHE_HOME=rel` | cache `/t/h/.cache/hylo` | edge-case |
| linux, `HOME=/t/h`, `HYLO_PATHS_CACHE_DIR=/t/c` | status-line cache dir `/t/c`; `CacheDir()` still `/t/h/.cache/hylo` | edge-case |
| windows, `LOCALAPPDATA` unset | `CacheDir()` returns an error | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-032 | For every env map, the result ends in the component `hylo` and contains no `dgx-llm` component | Go property test (testing/quick) |
| VP-032 | The functions perform no filesystem writes | manual (code review) + unit test on a read-only temp root |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 (render-path support), CAP-015 (path keys) |
| L2 Domain Invariants | DI-008 (an unavailable dir never fails the render) |
| Architecture Module | `internal/platform` `paths.go`, `paths_unix.go`, `paths_windows.go` (design §2.5) (BC-COMPONENT-MAP: internal/platform/paths*.go (per-OS dirs, OD-144) — ARCH-05) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. Decisions OD-95 (paths, XDG, APPDATA/LOCALAPPDATA), OD-101 (hylo cache dir from P1, explicit D15 exception), OD-144 (relative/empty `XDG_*` ignored; Windows cache/state as separate `%LOCALAPPDATA%` subdirectories), OD-61 (`~` expansion), OD-107 (P1 config = `HYLO_*` env + defaults), OD-05 (no `DGX_*`); PLAN §6 "Config"; legacy contrast SL:78 (`CACHE_DIR = os.path.expanduser("~/.cache/dgx-llm")`) |

## Related BCs (Recommended)

- BC-1.06.001 — composes with (the cache store creates and uses this directory)
- BC-2.03.002 — related to (`hylo config path` prints these paths)
- BC-2.01.001 — depends on (`HYLO_PATHS_CACHE_DIR` resolution)
- BC-6.03.002 — related to (caches compared by file name across directories)

## Architecture Anchors (Recommended)

- `architecture/ARCH-05-platform.md#platform-paths` — internal/platform/paths*.go (per-OS dirs, OD-144) (per-OS directory resolution) (BC-COMPONENT-MAP: ARCH-05 (ARCH-05-platform.md))

## Story Anchor (Recommended)

TBD — platform paths (design step S7)

## VP Anchors (Recommended)

- VP-032 — no `dgx-llm` path is ever produced

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none — pure computation over the injected env lookup (PC-5: no directory created, no file touched); the enclosing `internal/platform` package is infrastructure (process and OS probes live in its other files) |
| **Global state access** | none (env lookup is a parameter, Inv 3) |
| **Deterministic** | yes (given the injected environment; ADV-P4-D30) |
| **Thread safety** | safe (stateless functions); build-tag confined per OS |
| **Overall classification** | pure core (package: infrastructure) |

Owning component `internal/platform` (BC-COMPONENT-MAP: plat/paths*.go (per-OS dirs, OD-144) - ARCH-05); the ARCH-00 package table classifies the package infrastructure - syscalls, `/proc`, `sysctl`, Win32, build-tag confined.
