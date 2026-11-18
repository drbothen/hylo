---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-18T09:22:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-05-platform.md, behavioral-contracts/ss-03/BC-3.01.001.md, behavioral-contracts/ss-02/BC-2.03.002.md, owner-decisions-log-2026-11-14.md]
input-hash: "0f6e715"
traces_to: prd.md
source_bc: BC-3.01.001
bcs: [BC-3.01.001, BC-2.03.002]
module: internal/platform (paths)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P2 fix — skeleton applies each row's env/home seam and asserts Config/State dirs (A2-12)", "1.2 2026-11-18T09:22:00Z: ADV-P3 fix (A2-25) — Windows resolution pinned: config = %APPDATA%\\hylo, cache/state = %LOCALAPPDATA%\\hylo\\{cache,state} per BC-3.01.001; LOCALAPPDATA/APPDATA empty ⇒ the EC-004 unavailable error, reported by hylo config path", "1.3 2026-11-20T18:00:00Z: pass-11 fix (A2-05) — statement extended to BC-3.01.001 v1.3.1's additions: a relative base (Unix HOME=rel; Windows LOCALAPPDATA=rel / APPDATA=rel) is treated as UNSET falling to the 'cannot be determined' error (EC-013, base-directory kind discipline), and EC-004's Unix half (home cannot be determined, no XDG override) is named; env matrix gains Unix-HOME unset/set/relative and Windows relative-base rows"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-032: Per-OS directory resolution rules (OD-95/OD-101/OD-144)

## Property Statement

Directory resolution is explicit per OS — never `os.UserCacheDir`: macOS/Linux build
`$XDG_CACHE_HOME/hylo` else `~/.cache/hylo` (and Config/State analogues honoring
XDG_CONFIG_HOME/XDG_STATE_HOME); relative or empty `XDG_*` values are ignored (fall
through to the default); Windows uses `%LOCALAPPDATA%\hylo\cache` and `...\hylo\state`
subdirectories, with the config dir at `%APPDATA%\hylo` (OD-144); when `LOCALAPPDATA`
or `APPDATA` is empty on Windows the resolver returns the unavailable error
(EC-004) and `hylo config path` reports it; a RELATIVE base — Unix `HOME=rel`, or
Windows `LOCALAPPDATA=rel` / `APPDATA=rel` — is treated as UNSET and falls to the
next source, ending in the same "cannot be determined" error (EC-013, base-directory
kind discipline), the path never joined into a cwd-relative directory; on Unix an
unset/undeterminable home with no XDG override is the same unavailable error
(EC-004's Unix half); `~` expands in path values (`~user` left as written); and
`hylo config path` prints config/cache/state in fixed order with fixed labels from
this resolution.

## Source Contract

- **Primary BC:** BC-3.01.001 — Per-OS cache/config/state dirs; hylo cache dir from P1
  (XDG/hylo, LOCALAPPDATA).
- **Partial coverage:** BC-2.03.002 (config path prints the three paths, OD-132).
- **Invariant verified:** OD-95 (built explicitly in internal/platform), OD-101 (real
  hylo location from P1), OD-144 (relative/empty XDG ignored; Windows subdirs);
  DI-010's "no silent fallback" analogue for paths.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test per OS leg — environment matrices
  (XDG_* set/empty/relative/absolute; Unix HOME unset/set/relative; Windows
  LOCALAPPDATA/APPDATA empty/unset/relative/absolute) with fake home dirs;
  the config-path output pinned by golden lines.
- **Honesty:** testable-only; OS legs are pinned independently in the CI matrix (VP-037).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Env matrices | Go test with fake homes | yes — enumerated env shapes | all three dirs x all OSes |
| Golden output | config-path test | yes | fixed labels/order |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestPaths_XDGAndLocalappdataRules(t *testing.T) {
    for _, tc := range PathEnvMatrices {
        // Each row carries its own env/home seam; the resolver reads ONLY that seam
        // (no process-global getenv), so rows cannot bleed into each other.
        env := seamWithHome(tc.Env, tc.Home) // injected env + fake home, per row
        wantCache, wantConfig, wantState := tc.WantCache, tc.WantConfig, tc.WantState
        if got := platform.CacheDir(env); got != wantCache {
            t.Fatalf("%s: cache got %q want %q", tc.Name, got, wantCache)
        }
        if got := platform.ConfigDir(env); got != wantConfig {
            t.Fatalf("%s: config got %q want %q", tc.Name, got, wantConfig)
        }
        if got := platform.StateDir(env); got != wantState {
            t.Fatalf("%s: state got %q want %q", tc.Name, got, wantState)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree `TestPaths_XDGAndLocalappdataRules` per OS
build tag; `platform` parity family covers seeded dir outputs.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Enumerated env shapes | small |
| Proof complexity | N/A | |
| Tool support | Full | fake homes, build tags |
| Estimated proof time | Days | three-OS bookkeeping |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
