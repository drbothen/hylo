---
document_type: verification-property
level: L4
version: "1.9"
status: draft
producer: architect
timestamp: 2026-11-19T18:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-06/BC-6.01.001.md, behavioral-contracts/ss-06/BC-6.01.002.md, behavioral-contracts/ss-06/BC-6.01.003.md, owner-decisions-log-2026-11-14.md]
input-hash: "26fe0c7"
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
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fix — per-OS child env: Windows TEMP/TMP + PYTHONUTF8/PYTHONIOENCODING pins; no literal temp paths (A2-17)", "1.3 2026-11-18T09:02:00Z: ADV-P3 fixes (A2-04) — Windows child env additionally pins USERPROFILE (and HOMEDRIVE/HOMEPATH) to the parity roots so ntpath.expanduser resolves caches inside the sandbox (CPython 3.8+ ntpath.expanduser reads USERPROFILE, ignores HOME), and preserves SYSTEMROOT (socket initialization); catalog note added: BC-1.01.004 → VP-034 is a stale pairing (A2-13)", "1.4 2026-11-18T23:45:00Z: ADV-P5 fixes (A2-07, A02, D02) — child env asserted as the EXACT BC-6.01.002 allowlisted key set against a seeded forbidden parent; every PYTHON* variable except PYTHONPATH absent (PYTHONUTF8/PYTHONIOENCODING pins removed — stdio encoding comes from the shim UTF-8 reconfigure); TZ pinned to the case zone (UTC in parity, OD-177); Windows SYSTEMROOT looked up case-insensitively; new TestFrozenClock_Float64EndToEnd asserts the frozen instant is a float64 end to end — never round-tripped through time.Time nanoseconds (plan call 7, D02) on an ulp-spanning instant grid", "1.5 2026-11-19T12:00:00Z: pass-6 fixes (A2-06, OD-183: per-OS allowlists so the exact-set assert cannot red a correct windows-2025 run; the OD-183 Windows row PYTHONIOENCODING=utf-8 (stdio only, PYTHONUTF8 still forbidden) with the changes-stdio-only table-test pin)",
 "1.6 2026-11-19T18:00:00Z: pass-7 fixes (D05/A01 call 2, A2-19/OD-190) — the per-OS key sets are copied VERBATIM from BC-6.01.002 PC-1's authoritative consolidation: Windows oracle gains HOME/TMPDIR/LANG (were omitted), HOMEDRIVE/HOMEPATH withdrawn (NOT constructed keys on any OS — the v1.3 expanduser triple), the POSIX and Windows GO-binary allowlists added (XDG_CACHE_HOME, LOCALAPPDATA, HYLO_PATHS_CACHE_DIR, HYLO_BACKENDS_0_MODEL_PREFIXES; no PATH ever), conditional PATH/COLUMNS/setting keys named; OD-190 LF normalization named beside PYTHONIOENCODING=utf-8 (UTF-8 + LF on every OS), not hidden in the shim",
 "1.7 2026-11-19T20:00:00Z: pass-10 residual (ADV-P10-D01 sync) — the copied exact key sets gain the unconditional injected-metrics keys, verbatim from BC-6.01.002 PC-1: DGX_SL_VM_URL (= the injected fake metrics URL) in the POSIX/Windows oracle allowlists and HYLO_BACKENDS_0_METRICS_URL (= the same injected URL, unless the case itself sets backends[0].metrics_url — the case value wins) in the POSIX/Windows Go allowlists, property statement and skeleton alike; '+ the DGX_SL_* keys' respelled '+ the OTHER DGX_SL_* keys'",
 "1.8 2026-11-20T18:00:00Z: pass-11 fix (A2-02, orchestrator call 1) — OD-190 applied literally: the LF conversion lives in the COMPARATOR, not the shim — on the Windows legs the comparator converts the ORACLE's stdout CRLF to LF openly, before the byte comparison; hylo's bytes are never converted (hylo writes LF itself); 'the shim's newline=\\\"\\\\n\\\" reconfigure' wording withdrawn (the shim does no newline reconfigure)", "1.9 2026-11-21T09:00:00Z: pass-11 residual (call 3) — the injected-URL qualifier respelled: when the case itself sets backends[0].metrics_url, the case value is used on BOTH sides (DGX_SL_VM_URL and HYLO_BACKENDS_0_METRICS_URL), admitted only as a placeholder resolving to the fake server (optional path suffix), one value per key; replaces 'the case value wins'"]
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
key sets of BC-6.01.002 PC-1 — AUTHORITATIVE, copied VERBATIM (pass-7 D05, call 2;
conditional keys in parentheses):
the POSIX oracle child carries exactly `HOME`, `USERPROFILE`, `TMPDIR`, `LANG`, `TZ`,
`PYTHONPATH`, `HYLO_TEST_NOW`, `LOCAL_MODEL_PREFIXES`, `DGX_SL_VM_URL` (= the injected
fake metrics URL; ADV-P10-D01) (+ the OTHER `DGX_SL_*` keys the case sets, +
`COLUMNS` when declared, + `PATH` only when the case declares a
subprocess-fake table); the Windows oracle child is that set plus `TMP`, `TEMP`,
`SYSTEMROOT` and `PYTHONIOENCODING=utf-8` (OD-183), same conditionals — so `HOME`,
`USERPROFILE`, `TMPDIR` and `LANG` are present on BOTH OSes, and `HOMEDRIVE`/
`HOMEPATH` are NOT constructed keys on any OS (v1.3's expanduser profile triple is
withdrawn: `ntpath.expanduser` reads USERPROFILE first, and the BC does not allow the
extra keys); the POSIX Go-binary child carries exactly `HOME`, `USERPROFILE`, `TMPDIR`,
`XDG_CACHE_HOME`, `LOCALAPPDATA`, `HYLO_PATHS_CACHE_DIR`, `LANG`, `TZ`,
`HYLO_TEST_NOW`, `HYLO_BACKENDS_0_MODEL_PREFIXES`, `HYLO_BACKENDS_0_METRICS_URL` (=
the injected fake metrics URL, the same URL as the oracle's `DGX_SL_VM_URL`; when
the case itself sets `backends[0].metrics_url`, the case value is used on BOTH sides
(`DGX_SL_VM_URL` and `HYLO_BACKENDS_0_METRICS_URL`), admitted only as a placeholder
resolving to the fake server (optional path suffix), one value per key; ADV-P10-D01;
pass-11 residual call 3)
(+ the `HYLO_*` setting keys the
case sets, + `COLUMNS` when declared; no `PATH` ever — the built binary starts by
absolute path), and the Windows Go child adds `TMP`, `TEMP`, `SYSTEMROOT` — asserted as
exact set equality against a parent env seeded
with every forbidden variable — no `*_proxy` variables, every `PYTHON*` variable
ABSENT except `PYTHONPATH` and — on Windows only (OD-183) — exactly one extra
variable, `PYTHONIOENCODING=utf-8` (stdio encoding only; `PYTHONUTF8` stays
FORBIDDEN; POSIX pins `LANG=en_US.UTF-8` instead), no inherited GP-1..GP-6
variables; `SYSTEMROOT` is preserved and looked up CASE-INSENSITIVELY, because
Windows env keys often spell `SystemRoot`; `TZ` pinned to the case zone — UTC in
parity (OD-177); by OD-190 (as applied by the pass-11 orchestrator call 1) the
Windows legs' LF handling is NAMED beside the
builder variable, never hidden in the shim: hylo writes UTF-8 + LF line endings on
every OS (OD-190 extends OD-183) — the encoding from `PYTHONIOENCODING=utf-8`; on
the Windows legs the COMPARATOR converts the ORACLE's stdout CRLF to LF openly,
BEFORE the byte comparison, and hylo's bytes are NEVER converted (hylo writes LF
itself); the shim does NO newline reconfigure;
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
var oracleAllowlistPosix = []string{ // BC-6.01.002 PC-1, verbatim (pass-7 D05, ADV-P10-D01)
    "HOME", "USERPROFILE", "TMPDIR", "LANG", "TZ", "PYTHONPATH",
    "HYLO_TEST_NOW", "LOCAL_MODEL_PREFIXES",
    "DGX_SL_VM_URL"} // = the injected fake metrics URL (harness-injected,
                     // ADV-P10-D01); + the OTHER DGX_SL_* keys the case sets,
                     // + COLUMNS when declared,
                     // + PATH iff a fake table is declared

var oracleAllowlistWindows = []string{ // BC-6.01.002 PC-1, verbatim: the POSIX set
    // plus TMP/TEMP/SYSTEMROOT and OD-183's single extra variable — HOME, TMPDIR
    // and LANG INCLUDED (D05: they were omitted), HOMEDRIVE/HOMEPATH withdrawn
    // (NOT constructed keys on any OS).
    "HOME", "USERPROFILE", "TMPDIR", "LANG", "TZ", "PYTHONPATH",
    "HYLO_TEST_NOW", "LOCAL_MODEL_PREFIXES",
    "DGX_SL_VM_URL",
    "TEMP", "TMP", "SYSTEMROOT", "PYTHONIOENCODING"} // same conditionals as POSIX

var goAllowlistPosix = []string{ // BC-6.01.002 PC-1, verbatim: the GO-binary child
    "HOME", "USERPROFILE", "TMPDIR", "XDG_CACHE_HOME", "LOCALAPPDATA",
    "HYLO_PATHS_CACHE_DIR", "LANG", "TZ", "HYLO_TEST_NOW",
    "HYLO_BACKENDS_0_MODEL_PREFIXES",
    "HYLO_BACKENDS_0_METRICS_URL"} // = the injected fake metrics URL (the same URL as
                                   // the oracle's DGX_SL_VM_URL unless the case itself
                                   // sets backends[0].metrics_url — the case wins);
                                   // + HYLO_* setting keys the case sets,
                                   // + COLUMNS when declared; no PATH ever

var goAllowlistWindows = []string{ // the POSIX Go set plus the Windows triple
    "HOME", "USERPROFILE", "TMPDIR", "XDG_CACHE_HOME", "LOCALAPPDATA",
    "HYLO_PATHS_CACHE_DIR", "LANG", "TZ", "HYLO_TEST_NOW",
    "HYLO_BACKENDS_0_MODEL_PREFIXES",
    "HYLO_BACKENDS_0_METRICS_URL",
    "TEMP", "TMP", "SYSTEMROOT"} // + HYLO_* conditionals as above

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
    // Both OSes (BC-6.01.002 PC-1: HOME+USERPROFILE on BOTH, always the case-temp
    // value; D05):
    if env["HOME"] != home || env["USERPROFILE"] != home {
        t.Fatal("HOME/USERPROFILE not the fixed parity value")
    }
    if env["TMPDIR"] != tmp { t.Fatal("TMPDIR not the fixed parity value") }
    if env["LANG"] != "en_US.UTF-8" { t.Fatal("locale not pinned (strict UTF-8)") }
    if runtime.GOOS == "windows" {
        if env["TEMP"] != tmp || env["TMP"] != tmp { // CPython on Windows reads TEMP/TMP
            t.Fatal("Windows TEMP/TMP not pinned to the parity root")
        }
        if _, ok := env["HOMEDRIVE"]; ok { // D05: NOT constructed keys on any OS
            t.Fatal("HOMEDRIVE constructed — withdrawn from the allowlist")
        }
        if _, ok := env["HOMEPATH"]; ok {
            t.Fatal("HOMEPATH constructed — withdrawn from the allowlist")
        }
        if envLookupCI(env, "SYSTEMROOT") == "" { // CASE-INSENSITIVE lookup: Windows
            t.Fatal("SYSTEMROOT not preserved in the child env") // keys often spell SystemRoot
        }
        if env["PYTHONIOENCODING"] != "utf-8" { // OD-183: exactly one extra Windows
            t.Fatal("Windows PYTHONIOENCODING not pinned to utf-8") // variable, stdio only
        }
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
