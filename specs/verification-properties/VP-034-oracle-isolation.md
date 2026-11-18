---
document_type: verification-property
level: L4
version: "1.5"
status: draft
producer: architect
timestamp: 2026-11-19T12:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.01.001.md, behavioral-contracts/ss-06/BC-6.01.002.md, behavioral-contracts/ss-06/BC-6.01.003.md, owner-decisions-log-2026-11-14.md]
input-hash: "ec43647"
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
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fix — per-OS child env: Windows TEMP/TMP + PYTHONUTF8/PYTHONIOENCODING pins; no literal temp paths (A2-17)", "1.3 2026-11-18T09:02:00Z: ADV-P3 fixes (A2-04) — Windows child env additionally pins USERPROFILE (and HOMEDRIVE/HOMEPATH) to the parity roots so ntpath.expanduser resolves caches inside the sandbox (CPython 3.8+ ntpath.expanduser reads USERPROFILE, ignores HOME), and preserves SYSTEMROOT (socket initialization); catalog note added: BC-1.01.004 → VP-034 is a stale pairing (A2-13)", "1.4 2026-11-18T23:45:00Z: ADV-P5 fixes (A2-07, A02, D02) — child env asserted as the EXACT BC-6.01.002 allowlisted key set against a seeded forbidden parent; every PYTHON* variable except PYTHONPATH absent (PYTHONUTF8/PYTHONIOENCODING pins removed — stdio encoding comes from the shim UTF-8 reconfigure); TZ pinned to the case zone (UTC in parity, OD-177); Windows SYSTEMROOT looked up case-insensitively; new TestFrozenClock_Float64EndToEnd asserts the frozen instant is a float64 end to end — never round-tripped through time.Time nanoseconds (plan call 7, D02) on an ulp-spanning instant grid", "1.5 2026-11-19T12:00:00Z: pass-6 fixes (A2-06, OD-183: per-OS allowlists so the exact-set assert cannot red a correct windows-2025 run; the OD-183 Windows row PYTHONIOENCODING=utf-8 (stdio only, PYTHONUTF8 still forbidden) with the changes-stdio-only table-test pin)"]
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
OD-109); the child environment is constructed from scratch as the EXACT allowlisted
key set of BC-6.01.002 — asserted as exact set equality against a parent env seeded
with every forbidden variable — no `*_proxy` variables, every `PYTHON*` variable
ABSENT except `PYTHONPATH` and — on Windows only (OD-183) — exactly one extra
variable, `PYTHONIOENCODING=utf-8` (stdio encoding only; `PYTHONUTF8` stays
FORBIDDEN; POSIX pins `LANG=en_US.UTF-8` instead), no inherited GP-1..GP-6
variables, and per-OS temp/locale pins: on POSIX, fixed
HOME/USERPROFILE, TMPDIR and `LANG=en_US.UTF-8` (strict UTF-8 parity locale); on
Windows, `TEMP` and `TMP` (which
CPython reads instead of TMPDIR) pinned to the parity roots, `USERPROFILE` (and
`HOMEDRIVE`/`HOMEPATH`) pinned to the parity profile roots so
`ntpath.expanduser` — which since CPython 3.8 reads USERPROFILE and ignores HOME —
resolves caches inside the sandbox, `SYSTEMROOT` preserved (Windows socket
initialization needs it; looked up CASE-INSENSITIVELY, because Windows env keys
often spell `SystemRoot`); `TZ` pinned to the case zone — UTC in parity (OD-177);
a table test pins that `PYTHONIOENCODING=utf-8` changes stdio encoding ONLY
(files stay OD-159 strict UTF-8 reads), per the BC-6.01.002/BC-1.01.008 wording; and the
canary test fails the harness if the shim did not load (BC-6.01.003), so a silently
disabled clock shim cannot produce false-pass parity.

Catalog note (A2-13): VP-034 carries no BC-1.01.004 anchor — oracle isolation does
not verify visible width (that surface is VP-027/VP-040's). A rebuilt VP-INDEX must
not restore a BC-1.01.004 → VP-034 pairing.

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
| Frozen-clock round trip | Go test, `math.Float64bits` grid | yes — captured decimals | D02: `HYLO_TEST_NOW` float64 never round-tripped through `time.Time` |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
var oracleAllowlistPosix = []string{ // BC-6.01.002 canonical vector, Linux oracle env
    "HOME", "USERPROFILE", "TMPDIR", "LANG", "TZ", "PYTHONPATH",
    "HYLO_TEST_NOW", "LOCAL_MODEL_PREFIXES"} // + COLUMNS when declared, + case settings

var oracleAllowlistWindows = []string{ // A2-06: the Windows child env this VP itself
    // mandates (TEMP/TMP/HOMEDRIVE/HOMEPATH/SYSTEMROOT, no TMPDIR/LANG) can never
    // equal the POSIX set — a correct implementation went red on windows-2025.
    // OD-183 adds exactly one extra variable, PYTHONIOENCODING=utf-8.
    "TEMP", "TMP", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "SYSTEMROOT", "TZ",
    "PYTHONPATH", "PYTHONIOENCODING",
    "HYLO_TEST_NOW", "LOCAL_MODEL_PREFIXES"} // + COLUMNS when declared, + case settings

func TestOracleEnv_FromScratch(t *testing.T) {
    // A2-07: the sweep is not enough — the allowlist is asserted as an EXACT set
    // against a parent env containing every forbidden variable (BC-6.01.002
    // assertion 5). Proxy sentinels, PYTHONUTF8, DGX_SL_TTL, HYLO_X, HOME=/real…
    parent := seededForbiddenParentEnv()
    home, tmp := t.TempDir(), t.TempDir() // parity roots from the test, never literals
    env := oracleChildEnv(parent, nowSetting, home, tmp)
    want := oracleAllowlistPosix // A2-06: PER-OS allowlist selection
    if runtime.GOOS == "windows" {
        want = oracleAllowlistWindows
    }
    if !setsEqual(keys(env), withDeclared(want, testCaseKeys())) {
        t.Fatalf("child env is not the exact allowlisted key set: %v", keys(env))
    }
    for k := range env { // forbidden-class sweep on the constructed list
        lk := strings.ToLower(k)
        if strings.HasSuffix(lk, "_proxy") || (strings.HasPrefix(lk, "python") &&
            lk != "pythonpath" && !(lk == "pythonioencoding" && runtime.GOOS == "windows")) { // OD-183
            t.Fatalf("forbidden variable leaked into child env: %s", k)
        }
    }
    if env["TZ"] != "UTC" { // OD-177 parity pin: both sides see the case zone
        t.Fatal("TZ not pinned to the case zone (UTC in parity)")
    }
    if runtime.GOOS == "windows" {
        if env["TEMP"] != tmp || env["TMP"] != tmp { // CPython on Windows reads TEMP/TMP
            t.Fatal("Windows TEMP/TMP not pinned to the parity root")
        }
        vol := filepath.VolumeName(home) // A2-04: pin the profile triple so
        homePath := strings.TrimPrefix(home, vol) // ntpath.expanduser stays in the sandbox
        if env["USERPROFILE"] != home || env["HOMEDRIVE"] != vol || env["HOMEPATH"] != homePath {
            t.Fatal("Windows profile pins (USERPROFILE/HOMEDRIVE/HOMEPATH) not the parity values")
        }
        if envLookupCI(env, "SYSTEMROOT") == "" { // CASE-INSENSITIVE lookup: Windows
            t.Fatal("SYSTEMROOT not preserved in the child env") // keys often spell SystemRoot
        }
        if env["PYTHONIOENCODING"] != "utf-8" { // OD-183: exactly one extra Windows
            t.Fatal("Windows PYTHONIOENCODING not pinned to utf-8") // variable, stdio only
        }
    } else {
        if env["HOME"] != home || env["USERPROFILE"] != home {
            t.Fatal("HOME/USERPROFILE not the fixed parity value")
        }
        if env["TMPDIR"] != tmp { t.Fatal("TMPDIR not the fixed parity value") }
        if env["LANG"] != "en_US.UTF-8" { t.Fatal("locale not pinned (strict UTF-8)") }
    }
    if !argsInclude(runnerArgs, "-s") || argsInclude(runnerArgs, "-I") || argsInclude(runnerArgs, "-E") {
        t.Fatal("wrong interpreter flags (-s required; -I and -E banned, OD-109)")
    }
}

func TestFrozenClock_Float64EndToEnd(t *testing.T) { // D02 round trip (plan call 7)
    // The frozen instant is a float64 END TO END: parsed exactly as Python float()
    // (within the BC-6.01.003 grammar) and NEVER round-tripped through time.Time
    // nanoseconds — float64 spacing at ~1.79e18 ns is 256 ns, so a nanosecond round
    // trip perturbs fractional instants; Env.Now returns float seconds and TimeFloat
    // applies only to the real clock. The former canary value .5 hides the defect;
    // the grid below is ulp-spanning on purpose.
    for _, now := range frozenNowGrid() { // captured decimals: .5, .25, .123456789, ulp spans
        if bits := math.Float64bits(envNowForTest(now)); bits != math.Float64bits(pythonFloat64(now)) {
            t.Fatalf("frozen instant %v perturbed by a time.Time round trip", now)
        }
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
