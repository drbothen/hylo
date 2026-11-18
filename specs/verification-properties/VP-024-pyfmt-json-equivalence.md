---
document_type: verification-property
level: L4
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-19T22:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-05/BC-5.02.001.md, behavioral-contracts/ss-05/BC-5.02.002.md, behavioral-contracts/ss-05/BC-5.02.004.md, behavioral-contracts/ss-05/BC-5.02.005.md, behavioral-contracts/ss-05/BC-5.02.006.md, owner-decisions-log-2026-11-14.md]
input-hash: "2e5067d"
traces_to: prd.md
source_bc: BC-5.02.001
bcs: [BC-5.02.001, BC-5.02.002, BC-5.02.003, BC-5.02.004, BC-5.02.005, BC-5.02.006, BC-1.05.009]
module: internal/pyfmt (json.go)
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-18T09:13:00Z: ADV-P3 fixes (A2-08) — both fuzz skeletons call the 3-arg Decode(b, mode, per-site budget); the single-variable multi-value assignment (again := pyfmt.Decode(...)) fixed to the two-value form; pyfmtDefaultBudget free constant removed in favour of the call-site budget rule of VP-006", "1.3 2026-11-19T12:00:00Z: pass-6 fixes (A2-05: skeleton uses the (v, budget) → (result, error) DumpsLen/Dumps shapes per BC-5.02.001/BC-5.02.006 (D28); the BC-routed fuzz + oracle leg rides the Tier C harness (VP-011 discipline))", "1.4 2026-11-19T22:00:00Z: pass-8 fix (ADV-P8-C2-07, orchestrator call 12) — this VP is the OWNING HOME of the pyfmt.Dumps differential-fuzz leg BC-1.05.009's Verification Properties table routes here; bcs: gains BC-1.05.009; the leg is stated normatively in the Property Statement (Dumps == CPython json.dumps on generated ordered values incl. NaN/inf, ints, surrogates, live pinned-CPython oracle per input, Tier C harness)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-024: pyfmt JSON byte semantics equivalent to CPython 3.11

## Property Statement

Hand-written decoder/encoder over the ordered `Value` agrees with CPython 3.11:
`Dumps`/`DumpsLen` share one escape/float-repr code path so byte length and bytes
cannot drift; the 63-case dump-length oracle table is script-regenerated (OD-142, row
53 = 38 bytes), `json.dumps` length rules (escaping, float repr, inner-null 0) hold;
`Decode` implements the ModeText/ModeBytes acceptance sets (BOM/UTF-16/32 detection,
invalid UTF-8, NaN/Infinity tokens, duplicates last-wins keeping position, WTF-8
strings surviving lone surrogates); `Str` reproduces Python str() of values
(repr-based for non-str). On the cost-history write path (BC-1.05.009), `Dumps` equals
CPython `json.dumps` (defaults) on GENERATED ordered values — including NaN/inf, ints
as JSON spellings, and surrogate pairs — exercised as a Tier C differential-fuzz leg
(live pinned-CPython oracle per input, `HYLO_PARITY_FUZZSECONDS` budget), the owning
home of the fuzz leg BC-1.05.009's Verification Properties table routes here
(ADV-P8-C2-07).

## Source Contract

- **Primary BC:** BC-5.02.001 — json.dumps length rules (escaping, float repr,
  inner-null 0).
- **Partial coverage:** BC-5.02.002 (63-case length oracle, OD-142), BC-5.02.003
  (acceptance set — depth budgets in VP-006), BC-5.02.004 (ordered Value: insertion
  order, last-wins keeps position, Delete), BC-5.02.005 (Str), BC-5.02.006 (Dumps),
  BC-1.05.009 (the cost-history writer's `pyfmt.Dumps` bytes equal CPython
  `json.dumps` on generated ordered values — the differential-fuzz leg, ADV-P8-C2-07).
- **Invariant verified:** NFR-003 (banned stdlib codecs on protocol inputs, IM-01);
  AD-04 (CPython fidelity of every cache/widget byte).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** property-based + oracle tables — 63-case script-regenerated table;
  round-trip property `spelling(Decode(Dumps(v))) == spelling(v)` over generated
  ordered Values, compared as byte spellings (NaN-aware: NaN never equals itself, so
  equality is on `Dumps` output bytes, not on `Value` identity); fuzz
  targets `DumpsLen`/`Decode` (length == bytes invariant is fuzzed directly:
  `DumpsLen(v, budget) == len(Dumps(v, budget))`). Random-sample oracle: the committed
  CPython
  3.11-generated tables pin equivalence; generated samples assert self-consistency
  (round-trip spelling stability, length==bytes) in-tree — the unit set never calls a
  live interpreter (VP-038 discipline). The "fuzz + oracle" legs BC-5.02.001 and
  BC-5.02.004 route here (A2-05), and BC-1.05.009's "fuzz (differential vs the oracle)"
  row routes here as the owning home (ADV-P8-C2-07): all ride the Tier C differential
  harness — generated
  Values compared against the live pinned-CPython `dumps` per input under the
  `HYLO_PARITY_FUZZSECONDS` budget (VP-011 oracle discipline, ARCH-07 recipe).
- **Honesty:** testable-only; the shared-code-path argument is a structural argument
  (one implementation), strengthened but not replaced by fuzzing.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Oracle table | Go test, 63 cases, script-regenerated | yes | dump lengths/bytes |
| Round-trip property | Go test + generator | no (random), seeded | ordered Values |
| Length==bytes fuzz | `go test -fuzz DumpsLen` | budget-bounded | the cannot-drift invariant |
| Tier C differential | parity harness, live CPython per input | `HYLO_PARITY_FUZZSECONDS` | BC-5.02.001/BC-5.02.004 fuzz + oracle legs (A2-05); BC-1.05.009 Dumps-differential leg (ADV-P8-C2-07) |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func FuzzDumpsLenAgreesWithDumps(f *testing.F) {
    f.Fuzz(func(t *testing.T, b []byte) { // primitives only: fuzz bytes, decode
        // jsonSiteBudget = the json call-site budget per VP-006's per-call-site rule;
        // defined at the call site, never a package-level free constant (A2-08).
        v, err := pyfmt.Decode(b, pyfmt.ModeBytes, jsonSiteBudget)
        if err != nil { return } // undecodable bytes: length invariant vacuous
        n, err := pyfmt.DumpsLen(v, jsonSiteBudget) // A2-05: (v, budget) → (int, error) per BC-5.02.001/BC-5.02.006 (D28)
        if err != nil { t.Fatal("DumpsLen errored on decodable input") }
        out, err := pyfmt.Dumps(v, jsonSiteBudget) // A2-05: (v, budget) → ([]byte, error)
        if err != nil { t.Fatal("Dumps errored on decodable input") }
        if n != len(out) {
            t.Fatal("DumpsLen/Dumps drift")
        }
    })
}

func FuzzJSONRoundTrip(f *testing.F) {
    f.Fuzz(func(t *testing.T, b []byte) {
        v, err := pyfmt.Decode(b, pyfmt.ModeBytes, jsonSiteBudget)
        if err != nil { return }
        dumped, err := pyfmt.Dumps(v, jsonSiteBudget) // A2-05: two-result, budget-taking shape
        if err != nil { t.Fatal("Dumps output must re-decode") }
        d, err := pyfmt.Decode(dumped, pyfmt.ModeBytes, jsonSiteBudget) // 3-arg, two-value
        if err != nil { t.Fatal("Dumps output must re-decode") }
        redumped, _ := pyfmt.Dumps(d, jsonSiteBudget)
        // NaN-aware equality: compare byte spellings, never v == v on NaN
        if !bytes.Equal(redumped, dumped) {
            t.Fatal("round-trip drift")
        }
    })
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table; tables at `internal/pyfmt/testdata/*.golden` (gen
scripts under `testdata/gen/*.py`, pinned 3.11 oracle per OD-104/OD-142).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Large; corner-pinned + sampled | |
| Proof complexity | Medium | round-trip + shared path |
| Tool support | Full | |
| Estimated proof time | Weeks | generator for WTF-8/ordered Values |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
