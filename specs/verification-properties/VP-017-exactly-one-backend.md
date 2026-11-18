---
document_type: verification-property
level: L4
version: "1.6"
status: draft
producer: architect
timestamp: 2026-11-20T12:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-02-configuration.md, behavioral-contracts/ss-02/BC-2.01.002.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "fa66cbd"
traces_to: prd.md
source_bc: BC-2.01.002
bcs: [BC-2.01.002]
module: internal/config (backends validator)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-18T14:48:00Z: ADV-P4 fix (A2-18) — Method no longer claims cardinality 0 is tested through Load: 1 and 2 run through Load, the backends=0 guard is exercised directly at the validator seam (unreachable through Load in P1), joining the Load-driven table at P4", "1.3 2026-11-18T23:45:00Z: ADV-P5 fix (A2-01) — skeleton aligned with the ARCH-02 API: the typed error is taken via ErrorSet.First() (Load returns (*Config, *ErrorSet))", "1.4 2026-11-19T12:00:00Z: pass-6 fixes (A2-09: statement/method/skeleton agree the backends=0 guard is exercised now at the validator seam (Load row joins at P4); the two BC-2.01.002 quick legs (Load ⇒ one entry; metrics_url never ends '/') delivered)", "1.5 2026-11-19T18:00:00Z: pass-7 fix (A2-15) — the leftover A2-09-fix sentence 'validated directly when the P4 file layer makes the case reachable' removed; the now-seam wording (validator unit test with an empty entry slice, joining the Load-driven table at P4) is the single disposition", "1.6 2026-11-20T12:00:00Z: pass-9 fix (A2-20) — the sketch's Load calls take the ARCH-02 three-value signature (*Config, []Warning, *ErrorSet); the former two-value calls contradicted VP-015's skeleton and ARCH-02:91"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-017: Exactly-one-backend cardinality until P6

## Property Statement

The `backends[]` config validator enforces exactly one entry in P1-P5: more than one
entry is a config error carrying the value `backends=<count>` and the reason `exactly
one backend entry until P6` (rendered `hylo: config error: backends=2 (…)`, riding the
D4-EX-3 output path). Zero entries are unreachable in P1 — the built-in defaults always
create index 0 (BC-2.01.002 Invariant 2) — so no P1 test exercises the `backends=0`
guard through `Load`. The status line's metrics URL and model
prefixes are read exclusively at `backends[0].metrics_url` / `backends[0].model_prefixes`
(default `claude-sonnet`), the `backends=0` guard is exercised NOW directly at the
validator seam (a Go unit test calls the validator with an empty entry slice), joining
the `Load`-driven table at P4 when the file layer makes the case reachable, and the
cardinality check is isolated in one validator
function that P6 widens — no other code learns the cardinality rule. Two testing/quick
legs are routed here by BC-2.01.002's VP table (A2-09): successful `Load` ⇒ exactly one
backend entry, over generated environments; and the stored `metrics_url` value never
ends with `/`.

## Source Contract

- **Primary BC:** BC-2.01.002 — backends array: exactly one entry validated until P6;
  backends[0].metrics_url / backends[0].model_prefixes; default prefixes claude-sonnet.
- **Invariant verified:** DI-010 (validated config, named reasons); OD-123 (N backends
  schema from the start, one entry validated); AD-12 (validator-isolated seam for P6).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — cardinality 1 and 2 through `Load`, asserting the
  typed error reason and the D4-EX-3 line; the `backends=0` guard exercised directly
  at the validator seam (empty entry slice; the `Load`-driven row joins at P4); plus
  the two BC-2.01.002 quick legs over generated environments (successful `Load` ⇒
  exactly one entry; stored `metrics_url` never ends with `/`); plus a `backends[0]`
  default-values table (prefixes default, metrics_url plumb-through).
- **Honesty:** testable-only; the rule is a ruling (OD-123), finite case space.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Cardinality table | Go test, `internal/config` | yes — 1/2/N (0 at the validator seam now, `Load` at P4) | error rows + defaults plumb-through + BC-2.01.002 quick legs |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestBackends_ExactlyOneUntilP6(t *testing.T) {
    if _, _, es := config.Load(oneBackendOpts()); es != nil { t.Fatalf("one backend rejected: %v", es.First()) } // A2-20: Load is three-valued (ARCH-02:91)
    if _, _, es := config.Load(twoBackendsOpts()); es == nil ||
        es.First().Reason != "exactly one backend entry until P6" || // Load returns (*Config, []Warning, *ErrorSet),
        es.First().Value != "backends=2" { // ARCH-02: the error comes via nil-safe First()
        t.Fatalf("two backends: got %v", es)
    }
    // backends=0 is unreachable through Load in P1 (defaults create index 0,
    // BC-2.01.002 Inv-2); the guard is exercised NOW at the validator seam and
    // joins the Load-driven table at P4 (A2-09).
    if err := config.ValidateBackends(config.BackendSlice(nil)); err == nil {
        t.Fatal("zero-entry validator call did not fire the exactly-one guard")
    }
    // A2-09: the two testing/quick legs BC-2.01.002's VP table routes here.
    cfg := &quick.Config{MaxCount: 500, Values: genBackendEnvValues}
    if err := quick.Check(func(env map[string]string) bool {
        c, _, es := config.Load(backendEnvOpts(env)) // A2-20: three-value signature
        if es != nil { return true } // invalid envs are the class tables' domain
        return len(c.Backends) == 1 && // Load ⇒ exactly one entry
            !strings.HasSuffix(c.Backends[0].MetricsURL, "/") // stored value never ends with '/'
    }, cfg); err != nil {
        t.Fatalf("BC-2.01.002 quick leg violated: %v", err)
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; in-tree as `TestBackends_ExactlyOneUntilP6`; the
error line itself is pinned by the VP-016 class tables.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Tiny | 0/1/2/N backends |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Hours | |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
