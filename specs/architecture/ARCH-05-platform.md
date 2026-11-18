---
document_type: architecture-section
level: L3
section: "platform"
version: "1.10"
status: draft
producer: architect
timestamp: 2026-11-18T18:00:00Z
phase: 1b
inputs: [prd.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "380f3f1"

---

# ARCH-05 — Platform (`internal/platform`)

> All OS-specific code, build-tag confined (D5, NFR-004). Classification:
> **infrastructure** — syscalls and Win32; no parity logic; every function returns data
> consumed by pure code. HIGH tier (>= 90% kill rate — the Phase 6 mutation target, not a
> P1 gate; OD-158).

## Files (design doc §2.5)

| File | Content |
|---|---|
| `paths.go` + `paths_unix.go` / `paths_windows.go` | `CacheDir(env EnvVars) (string, error)`, `ConfigDir(env EnvVars) (string, error)`, `StateDir(env EnvVars) (string, error)` built explicitly per OD-95/OD-101/OD-144 (never `os.UserCacheDir`); error return per pass-8 D01, orchestrator call 7 — BC-3.01.001 EC-004 requires the error when a directory cannot be determined and `config path` exits 1 on it; at status-line startup the same error is NOT a config error — `Main` wires the load-empty / save-no-op store and the render proceeds (ARCH-03 step 0, ADV-P11-A08); relative/empty `XDG_*` ignored (OD-144); Windows `%LOCALAPPDATA%\hylo\cache` / `...\hylo\state` |
| `proc.go` | `FindAncestor(startPID int, name string, maxDepth int) (float64, bool)`; walk from `os.Getppid()` checking the parent first, at most `maxDepth` levels, stop at pid <= 1, `basename(comm)` match with `.exe` stripped case-insensitively on Windows. The caller passes `statusline.window_age.max_depth` (default 6, legacy T-025, SL:279; BC-3.02.001) — the depth is registry config (D15), not a magic number (ADV-P1-A18) |
| `proc_darwin.go` | `unix.SysctlKinfoProc("kern.proc.pid", pid)`: `Eproc.Ppid`, `P_comm`, `P_starttime` |
| `proc_linux.go` | `/proc/<pid>/stat` after the last `)`; start = `btime` + ticks/`procUserHZ`, with `procUserHZ = 100` a named constant, not config: Linux procfs emits times in USER_HZ, a fixed kernel-ABI unit (= 100, independent of CONFIG_HZ) that equals the glibc `sysconf(_SC_CLK_TCK)`/`CLK_TCK` value on every supported kernel — Go's stdlib has no sysconf, and the constant reproduces that ABI rather than a tunable (ADV-P1-A18) |
| `proc_windows.go` | `CreateToolhelp32Snapshot` + `GetProcessTimes`; PID-reuse guard (parent created before child). Walk rule (pass-5 D22): when the guard REJECTS a candidate parent, the walk TERMINATES — treated as not found; it never continues upward with the rejected impostor's PPID, which could climb an unrelated process chain and match a stranger's `claude` (logic hazard flagged pass-5 D22). Termination rule table-tested with fake PIDs |
| `envfold_posix.go` / `envfold_nt.go` (naming rule, orchestrator call 11 pass-7 A10: the PURE, always-compiled matcher flavors carry NO GOOS-recognized suffix — `_posix`/`_nt` are flavor names, not build constraints, so both flavors compile on every OS; only real syscall wrappers use `_windows.go`/`_unix.go` with explicit build tags) | The `HYLO_*` matcher flavors behind the `platform.EnvVars` interface (declared in this section, single home — ADV-P9-A12): plain exact matching on POSIX, case-insensitive NT-name matching on Windows; injected into `config.Load` at the seam (ADV-P2-A02, ADV-P4-A20). Seam rule (pass-5 D25): the case-insensitive matcher is implemented BEHIND the `platform.EnvVars` interface (single home in this section, ADV-P9-A12) — `config` consumes only the interface, never a bare Go map (maps are case-sensitive; a matcher inside `internal/config` would be untestable on POSIX and unexercisable on Windows CI). The matcher is a PURE function over a name→value listing, compile-time GOOS-selected with BOTH flavors always compiled and table-pinned on every OS (the Basename rule, ARCH-06) — so the Windows case-insensitivity table runs on POSIX CI legs, and no new seam is minted: the existing EnvVars interface IS the seam. Purity seam (pass-7 A03, orchestrator call 4): the process environment is enumerated exactly ONCE — by the `EnvVars` constructor `main` wires (ARCH-01); no platform resolver (`CacheDir`/`ConfigDir`/`StateDir`/`HomeDir`/`LocalZone`) reads the real process environment; each receives `env EnvVars` |
| `homedir.go` (+ per-OS flavor) | `HomeDir(env EnvVars)` backs `~`/`~\` expansion (OD-61, BC-2.01.005): `$HOME` on unix, `USERPROFILE` on Windows — read from the injected env, never `os.UserHomeDir` (the BC-3.01.001 home source goes through `EnvVars`; pass-7 A03/D12); consumed by `internal/config`, never resolved ad hoc in grammars (ADV-P4-A20) |
| `abspath.go` (+ `abspath_windows.go` Win32 wrapper) | `Abs(cwd, p string) (string, error)` — per-flavor absolute-path resolution; result type stated once here (ADV-P9-A03): the resolved absolute path, or the error `os.path.abspath` raises at the legacy site (e.g. an embedded NUL on Windows). POSIX flavor reproduces `os.path.abspath` with `cwd` injected as the process-cwd seam; the Windows wrapper resolves drive-relative `C:rel` through `GetFullPathNameW` (BC-1.02.004 PC-1 / EC-012 — the bare `Cwd func() string` cannot express it, pass-6 A18). Consumed by `internal/statusline`'s git walk (`platform.Abs(env.Cwd(), directory)`, BC-1.02.004 PC-1); per-flavor rules owned by BC-1.02.004 (PC-1, EC-012; ADV-P8-D22) |
| `zone.go` | `LocalZone(env EnvVars) (*time.Location, error)` (OD-171, refined by OD-177; env-injected signature and error return per orchestrator call 4, pass-7 A03): resolves the local zone on EVERY OS with libc semantics (OD-177), reading `TZ` ONLY through the injected `EnvVars` seam: `TZ` unset → the OS zone; `TZ` set but EMPTY or unparseable → UTC. `time.Local` is not used on Windows (it ignores `TZ`), so this is the single zone seam for `Env.Loc` (ARCH-03), the parity harness's child environments, and `Env.Loc` derivation being routed through `internal/platform` (ADV-P4-D21). Table test: TZ unset / `UTC` / IANA name / set-but-empty / unparseable. Documented limitation: POSIX-style TZ strings (e.g. `EST5EDT`) may differ between Go's tzdata loader and the MSVC CRT; the parity harness pins `TZ=UTC` for both binaries, so parity cases never hit the limitation (OD-171). Startup wiring of the error result: non-nil ONLY on the TZ-unset path when OS resolution fails (BC-3.01.001 PC-6); `Main` wires `Env.Loc = time.UTC` on it and the render proceeds (ARCH-03 step 0, ADV-P11-A08) |
| `localtime_domain.go` (pure, always-compiled — no GOOS suffix, call 11 naming rule pass-7 A10; the Windows-disposition table runs on POSIX CI legs) | Windows naive-conversion failure domain (pass-5 D01, call 8; domain statement corrected pass-7 D06, owner call 8): EVERY MSVC `localtime_s` call in CPython's local-to-UTC conversion — the probes `t`, `u1`, `u1 − 86400` and `u2` — is checked against the domain, so a naive wall time ON or before 1970-01-01 (the fold-0 `u1 − 86400` probe is negative for every wall time on 1970-01-01, not only midnight) or from year 3001 makes `localtime_s` raise OSError and degrades the line exactly as legacy does (the OSError propagates out of `_mix_counts` SL:1069 to the top-level guard, printing the degraded line). REHOMED pass-6 A05 (orchestrator call 2): the failure rule itself lives in PURE pyfmt (`LocalToUnix(fields, loc, msvcDomain)` returning `ErrLocaltimeDomain`, ARCH-06) with NO pyfmt→platform import — this section no longer hosts the conversion; it contributes the injected flag `IsWindows()` (compile-time `GOOS` constant) that `internal/statusline` passes as `msvcDomain`, and the epoch-negative / year-3001 probes here table-test pyfmt's `ErrLocaltimeDomain` disposition through that flag. The POSIX flavor converts the whole time_t domain with no failure domain. Disposition rides the owning BC-5.04.001 legs (pass-5 D01); NO exclusion id — ruled in-band behavior, not a divergence |
| `proc_other.go` | `//go:build !darwin && !linux && !windows`: not found |

### Canonical `EnvVars` declaration (single home — ADV-P9-A12)

```go
// Declared in internal/platform; consumed by cmd/hylo and internal/statusline
// (they reference platform.EnvVars, they do not re-declare it — ADV-P9-A12).
type EnvVars interface {
    Lookup(name string) (value string, ok bool) // ok=false => unset; ok=true + "" => set-but-empty
    Names() []string                            // full environ listing (os.Environ()-backed in main)
}
```

Path-value encoding for syscalls (pass-6 orchestrator call 16, ADV-P6-B05): every `str` path value hylo passes to
the OS on Windows is encoded WTF-8 → UTF-16 by `internal/platform` itself, keeping lone surrogates as single 16-bit
units — never Go's native U+FFFD substitution — so a path whose name contains a lone surrogate stats the same
directory CPython's wide-string call does (POSIX keeps the `surrogateescape` byte mapping, BC-1.02.004
EC-013/EC-014). Table-tested on Windows CI.

No descriptor helpers exist: OD-161 (pass-3 A06, superseding the "int `transcript_path`
= fd semantics" reading) rules that an integer `transcript_path` means NO transcript
with no descriptor I/O at all — the integer branch is a pure type switch in
`internal/statusline` (`sl/transcript.go`), so `StatFD`/`fd_*.go` were removed from
this section and BC-1.03.015 remapped (BC-COMPONENT-MAP).

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
  plus the D4-EX-1 Windows fake-probe test `TestWindowAge_D4EX1_Windows_AncestorFound` (settled name, VP-012 v1.13; pass-7 A2-05)).
- **x/sys usage:** `golang.org/x/sys/unix` only (`SysctlKinfoProc`); `golang.org/x/sys/windows`
  for Toolhelp32/GetProcessTimes — the sole runtime dependency budget in P1 (AD-02).

### Decision: zone resolution through `internal/platform` (OD-171, pass-4)

- **Context:** Go's `time.Local` ignores `TZ` on Windows, while CPython's MSVC runtime
  honors it; a naive local-time case would diverge on a non-UTC Windows host.
- **Decision:** hylo resolves its local zone ONLY through `platform.LocalZone(env EnvVars) (*time.Location, error)`, which
  honors `TZ` with libc semantics on every OS (OD-177): `TZ` unset → the OS zone;
  `TZ` set but empty or unparseable → UTC. The parity harness pins `TZ=UTC` for both
  binaries; the Windows
  leg runs the naive local-time cases with no skip (VP-026's `posix-only` tag is
  removed). Table test: TZ unset / `UTC` / IANA name / set-but-empty / unparseable. Documented
  limitation: POSIX-style TZ strings (e.g. `EST5EDT`) may differ from the MSVC runtime
  on Windows; parity cases use `TZ=UTC` only.
- **Consequence:** `Env.Loc` (ARCH-03) and the harness child environments derive their
  zone exclusively from this seam.

## Fragment anchors (pass-4 A01; stable targets for BC-body fragment links)

BC bodies link fragments like `architecture/ARCH-05-platform.md#platform-paths`; the
two anchors below are the complete, closed set for this section — new BC fragment links
must target one of these.

<a id="platform-paths"></a>
<a id="platform-proc"></a>

| Anchor | Target |
|---|---|
| `#platform-paths` | the `paths.go` + per-OS flavor rows in the Files table (per-OS dirs, OD-95/OD-101/OD-144) |
| `#platform-proc` | the `proc.go` + `proc_darwin/linux/windows/other.go` rows in the Files table (native ancestor probe) |

## Mapping

BC-3.01.001 -> paths; BC-3.02.001/.002 -> proc. Integer-`transcript_path` handling
needs no platform code (OD-161; see the note under Files). All
per-OS edge differences are named in BC-3.02.002's register, not discovered at runtime.
