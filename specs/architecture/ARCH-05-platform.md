---
document_type: architecture-section
level: L3
section: "platform"
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T23:59:00Z
phase: 1b
inputs: [prd.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "ea79506"
---

# ARCH-05 — Platform (`internal/platform`)

> All OS-specific code, build-tag confined (D5, NFR-004). Classification:
> **infrastructure** — syscalls and Win32; no parity logic; every function returns data
> consumed by pure code. HIGH tier (>= 90%).

## Files (design doc §2.5)

| File | Content |
|---|---|
| `paths.go` + `paths_unix.go` / `paths_windows.go` | `CacheDir()`, `ConfigDir()`, `StateDir()` built explicitly per OD-95/OD-101/OD-144 (never `os.UserCacheDir`); relative/empty `XDG_*` ignored (OD-144); Windows `%LOCALAPPDATA%\hylo\cache` / `...\hylo\state` |
| `proc.go` | `FindAncestor(startPID int, name string, maxDepth int) (float64, bool)`; walk from `os.Getppid()` checking the parent first, at most `maxDepth` levels, stop at pid <= 1, `basename(comm)` match with `.exe` stripped case-insensitively on Windows. The caller passes `statusline.window_age.max_depth` (default 6, legacy T-025, SL:279; BC-3.02.001) — the depth is registry config (D15), not a magic number (ADV-P1-A18) |
| `proc_darwin.go` | `unix.SysctlKinfoProc("kern.proc.pid", pid)`: `Eproc.Ppid`, `P_comm`, `P_starttime` |
| `proc_linux.go` | `/proc/<pid>/stat` after the last `)`; start = `btime` + ticks/`procUserHZ`, with `procUserHZ = 100` a named constant, not config: Linux procfs emits times in USER_HZ, a fixed kernel-ABI unit (= 100, independent of CONFIG_HZ) that equals the glibc `sysconf(_SC_CLK_TCK)`/`CLK_TCK` value on every supported kernel — Go's stdlib has no sysconf, and the constant reproduces that ABI rather than a tunable (ADV-P1-A18) |
| `proc_windows.go` | `CreateToolhelp32Snapshot` + `GetProcessTimes`; PID-reuse guard (parent created before child) |
| `proc_other.go` | `//go:build !darwin && !linux && !windows`: not found |
| `fd_unix.go`, `fd_windows.go` | `StatFD(n int) (regular bool)` for the int-`transcript_path` = fd semantics (BC-1.03.015) |

### Decision: native per-OS ancestor probe replaces the ps subprocess (AD-07)

- **Context:** legacy shells up to 6 × `ps -o ppid=,comm=,lstart= -p <pid>` at 1 s
  timeouts; on failure it re-probes every refresh; no `ps` on Windows (⌂ never showed).
  OD-76 ("fix") plus the native probe yield true start times in the repeated-DST hour
  and ⌂ on Windows (D4-EX-1 scopes the Windows difference).
- **Options considered:** (1) keep ps with a parser; (2) native probes via
  `golang.org/x/sys/unix` / Win32.
- **Option 2.** Microsecond-cost native probes; start time truncated to whole seconds
  and stored as a float under the legacy `proc_start` key so `int(win_ms // 60000)` flips
  on the same refresh (design doc IM-19).
- **Rationale:** removes the worst latency tail (up to 6 s) from the render path without
  changing corpus outputs (seeded `proc_start` cases never probe; unseeded CI cases agree
  — no `claude` ancestor on either side).
- **Consequences:** the former inert key `statusline.window_age.ps_timeout_s` is
  removed by OD-147 (owner, 2026-11-16); setting it is thereafter an unknown `HYLO_*`
  setting — one stderr warning, then ignored, with no output or exit-status change
  (BC-2.01.001 PC-6, VP-015; there is no unknown-key config-error class; ADV-P1-A03);
  macOS/Linux probe-result differences are the ruled OD-76
  exclusion entries; the symlinked-binary name case is measured in the probe test
  (deferred, OQ-3).
- **Verification feasibility:** probe units are **testable-only** (real syscalls) —
  per-OS tables for depth/stop/name rules with fake PIDs; parity flows through **seeded
  `proc_start` cases** (probe not exercised in parity, exercising instead table tests
  plus the D4-EX-1 Windows fake-probe test `TestWindowAge_D4EX1_Windows`).
- **x/sys usage:** `golang.org/x/sys/unix` only (`SysctlKinfoProc`); `golang.org/x/sys/windows`
  for Toolhelp32/GetProcessTimes — the sole runtime dependency budget in P1 (AD-02).

## Mapping

BC-3.01.001 -> paths; BC-3.02.001/.002 -> proc; fd helpers serve BC-1.03.015. All
per-OS edge differences are named in BC-3.02.002's register, not discovered at runtime.
