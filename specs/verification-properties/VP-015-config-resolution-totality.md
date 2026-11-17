---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-02-configuration.md, behavioral-contracts/ss-02/BC-2.01.001.md, behavioral-contracts/ss-02/BC-2.01.004.md, behavioral-contracts/ss-02/BC-2.01.005.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "29b3f56"
traces_to: prd.md
source_bc: BC-2.01.001
bcs: [BC-2.01.001, BC-2.01.004, BC-2.01.005, BC-2.01.003]
module: internal/config
proof_method: property-test (testing/quick)
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P2 pass-2 fixes — the totality oracle now asserts the DI-010 substance: generated-invalid values must return a typed Error identifying the offending key (no silent fallback to the default); unknown HYLO_* must warn on stderr with unchanged exit status; DGX_*-only environments must yield the exact default config (A2-08)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-015: Config resolution is total over the environment; the registry is closed

## Property Statement

For every possible environment-variable assignment, `config.Load` terminates and
returns either a `*Config` or a single typed `*Error` (Key, Value, Reason, EnvName) —
never a crash, never a silent fallback. "No silent fallback" is asserted, not
narrated: an environment whose generated value is invalid must produce a typed
`*Error` whose Key/EnvName identify the offending variable — a returned `*Config`
carrying the default for that key is a failure. Every key is declared in the closed registry
with type, range/operator, default and rationale (D15/OD-114); `EnvName` derivation is
collision-free at build time; unknown `HYLO_*` variables must warn on stderr and never
change exit status (asserted); environments carrying only `DGX_*` variables must yield
the exact built-in-default config, pinning that `DGX_*` is never read (asserted);
`COLUMNS` is excluded from the registry as a
protocol input.

## Source Contract

- **Primary BC:** BC-2.01.001 — P1 resolution: HYLO_* env over built-in defaults; no
  file layer; DGX_* never read.
- **Partial coverage:** BC-2.01.004 (key registry declarations), BC-2.01.005 (typed
  grammars; COLUMNS excluded), BC-2.01.003 (theme keys validated as SGR lists).
- **Invariant verified:** DI-010's P1 surface (typed, validated, no silent fallback;
  full file→env→default order completes in P4); DI-008 step-0 antecedent.

## Property Class and Verification Method

- **Class:** safety.
- **Method:** property-based test — random environments (valid, invalid, unknown
  variables, pathological values) through `Load` asserting termination + typed-result
  dichotomy; plus a build-time `EnvName` collision test (static analysis over the
  registry); plus the `legacy_defaults.golden` pin.
- **Honesty:** the random-sample property asserts the typed-result dichotomy as its
  own oracle — every generated environment terminates in exactly one of {*Config,
  single typed *Error}, never a crash or silent fallback; no live CPython call exists
  on this surface (equivalence corners are the `legacy_defaults.golden` pin). Totality
  is established empirically (generator breadth) over a pure
  function — provable-grade surface, testable-only artifact; the collision check is the
  closest to an actual proof (finite domain, exhaustively enumerated at build).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Property test | Go test + env generator | no (random), seeded | random environments |
| Build-time enumeration | `go test` (registry collision test) | yes — finite key set | EnvName collision-freedom |

## Proof Harness Skeleton

```go
func TestLoad_TotalOverEnvironment(t *testing.T) {
    for _, env := range RandomEnvironments(500) { // includes unknown HYLO_*, DGX_*, garbage
        c, err := config.Load(env.Opts())
        if c == nil && err == nil { t.Fatal("Load returned neither config nor error") }
        if c != nil && err != nil { t.Fatal("Load returned both") }
        if env.HasInvalidValue() { // DI-010 substance: no silent fallback (A2-08)
            if err == nil {
                t.Fatalf("invalid %s=%s silently accepted (got default-filled config)",
                    env.InvalidKey, env.InvalidValue)
            }
            if err.Key != env.InvalidKey || err.EnvName != env.InvalidEnvName {
                t.Fatalf("typed error does not identify the offending variable: %+v", err)
            }
        }
        if env.OnlyUnknownHYLO() && !env.StderrContainsUnknownSettingWarning() {
            t.Fatal("unknown HYLO_* did not warn on stderr")
        }
        if env.OnlyDGXVars() && !c.Equals(DefaultConfig()) {
            t.Fatal("DGX_* influenced the config — DGX_* must never be read (A2-08)")
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestLoad_TotalOverEnvironment` plus the
registry collision test and `internal/config/testdata/legacy_defaults.golden`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Infinite | sampled; registry finite |
| Proof complexity | Low-medium | pure function over env |
| Tool support | Full | |
| Estimated proof time | Days | grammar generator reuse from vp-016 |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
