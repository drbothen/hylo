---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-17T20:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.01.001.md, behavioral-contracts/ss-06/BC-6.01.002.md, behavioral-contracts/ss-06/BC-6.01.003.md, owner-decisions-log-2026-11-14.md]
input-hash: "04658a4"
traces_to: prd.md
source_bc: BC-6.01.001
bcs: [BC-6.01.001, BC-6.01.002, BC-6.01.003]
module: internal/parity (runner, pyhooks shim)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fix — per-OS child env: Windows TEMP/TMP + PYTHONUTF8/PYTHONIOENCODING pins; no literal temp paths (A2-17)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-034: Oracle isolation — explicit interpreter, from-scratch child env, canary

## Property Statement

The parity oracle runs under explicit isolation: the interpreter is the absolute
CPython 3.11.x path from `HYLO_PARITY_PYTHON`, never PATH discovery (OD-104, OD-108);
invocation uses `-s`, never `-I`/`-E` (`-I` would drop the sitecustomize clock shim,
OD-109); the child environment is constructed from scratch — no `*_proxy` variables,
no inherited GP-1..GP-6 variables, and per-OS temp/locale pins: on POSIX, fixed
HOME/USERPROFILE, TMPDIR and `LANG=en_US.UTF-8`; on Windows, `TEMP` and `TMP` (which
CPython reads instead of TMPDIR) pinned to the parity roots, and `PYTHONUTF8=1` plus
`PYTHONIOENCODING=utf-8` so oracle pipe/stdout bytes are UTF-8 regardless of the
locale code page; and the
canary test fails the harness if the shim did not load (BC-6.01.003), so a silently
disabled clock shim cannot produce false-pass parity.

## Source Contract

- **Primary BC:** BC-6.01.001 — Oracle runs via explicit absolute CPython 3.11.x path,
  never PATH; invoked with -s, never -I/-E.
- **Partial coverage:** BC-6.01.002 (child env from scratch), BC-6.01.003 (clock shim
  freeze from HYLO_TEST_NOW, stepped per refresh; canary).
- **Invariant verified:** DI-012's substrate (the referee's determinism is a
  precondition for every parity claim); RK-4/RK-5 dispositions.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test + canary — env-construction assertions on the spawned
  child (variable allowlist, per-OS temp/locale table), `-s` flag pin,
  interpreter-setting failure rows (unset
  variable fails loudly), canary `TestParityCanary_ShimLoaded` gating every harness run.
- **Honesty:** testable-only; isolation is observed on the child process, plus the
  canary's active probe of the shim.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Env assertions | Go test on the runner | yes — allowlist pin | child env shape |
| Canary | `TestParityCanary_ShimLoaded` | exact | shim presence per harness run |

## Proof Harness Skeleton

```go
func TestOracleEnv_FromScratch(t *testing.T) {
    home, tmp := t.TempDir(), t.TempDir() // parity roots from the test, never literals
    env := oracleChildEnv(nowSetting, home, tmp)
    for k := range env { // real proxy-var sweep: HTTP_PROXY, HTTPS_PROXY, ALL_PROXY,
        if strings.HasSuffix(strings.ToLower(k), "_proxy") { // NO_PROXY, lower-case forms
            t.Fatalf("proxy variable leaked into child env: %s", k)
        }
    }
    if runtime.GOOS == "windows" {
        if env["TEMP"] != tmp || env["TMP"] != tmp { // CPython on Windows reads TEMP/TMP
            t.Fatal("Windows TEMP/TMP not pinned to the parity root")
        }
        if env["PYTHONUTF8"] != "1" || env["PYTHONIOENCODING"] != "utf-8" {
            t.Fatal("Windows pipe encoding not pinned to UTF-8 (locale code page) ")
        }
    } else {
        if env["HOME"] != home || env["USERPROFILE"] != home {
            t.Fatal("HOME/USERPROFILE not the fixed parity value")
        }
        if env["TMPDIR"] != tmp { t.Fatal("TMPDIR not the fixed parity value") }
        if env["LANG"] != "en_US.UTF-8" { t.Fatal("locale not pinned") }
    }
    if !argsInclude(runnerArgs, "-s") || argsInclude(runnerArgs, "-I") || argsInclude(runnerArgs, "-E") {
        t.Fatal("wrong interpreter flags (-s required; -I and -E banned, OD-109)")
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestParityCanary_ShimLoaded` (settled, ARCH-07); env/flag assertions in
`TestOracleEnv_FromScratch`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Allowlist shape | small |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | env-diff tooling on the child |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
