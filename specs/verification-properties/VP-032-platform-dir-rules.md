---
document_type: verification-property
level: L4
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-05-platform.md, behavioral-contracts/ss-03/BC-3.01.001.md, behavioral-contracts/ss-02/BC-2.03.002.md, owner-decisions-log-2026-11-14.md]
input-hash: "d4e32e0"
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
modified: []
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
subdirectories; `~` expands in path values (`~user` left as written); and
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
  (XDG_* set/empty/relative/absolute; LOCALAPPDATA set/unset) with fake home dirs;
  the config-path output pinned by golden lines.
- **Honesty:** testable-only; OS legs are pinned independently in the CI matrix (VP-037).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Env matrices | Go test with fake homes | yes — enumerated env shapes | all three dirs x all OSes |
| Golden output | config-path test | yes | fixed labels/order |

## Proof Harness Skeleton

```go
func TestPaths_XDGAndLocalappdataRules(t *testing.T) {
    for _, tc := range PathEnvMatrices {
        if got := platform.CacheDir(); got != tc.Want {
            t.Fatalf("%s: got %q", tc.Name, got)
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
