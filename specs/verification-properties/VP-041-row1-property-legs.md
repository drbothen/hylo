---
document_type: verification-property
level: L4
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-18T23:45:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.02.001.md, behavioral-contracts/ss-01/BC-1.02.004.md, behavioral-contracts/ss-01/BC-1.02.016.md, behavioral-contracts/ss-01/BC-1.02.018.md, behavioral-contracts/ss-01/BC-1.02.019.md, behavioral-contracts/ss-01/BC-1.02.021.md, behavioral-contracts/ss-01/BC-1.02.022.md, behavioral-contracts/ss-01/BC-1.02.023.md, behavioral-contracts/ss-01/BC-1.02.025.md, behavioral-contracts/ss-01/BC-1.02.027.md, behavioral-contracts/ss-01/BC-1.02.028.md, prd-supplements/test-vectors.md]
input-hash: "9ebb7ae"
traces_to: prd.md
source_bc: BC-1.02.001
bcs: [BC-1.02.001, BC-1.02.004, BC-1.02.016, BC-1.02.018, BC-1.02.019, BC-1.02.021, BC-1.02.022, BC-1.02.023, BC-1.02.025, BC-1.02.027, BC-1.02.028]
module: internal/statusline (row-1 file families)
proof_method: property-test (testing/quick)
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.0 2026-11-18T15:05:00Z: created — ADV-P4 fix (B03, plan item 18): S1.02 for-all property legs split from VP-028, exactly as VP-040 was split from VP-027 in pass 3; VP-028 keeps the bounded golden tables", "1.1 2026-11-18T23:45:00Z: ADV-P5 fixes (A2-04, B08, A2-08) — the four BC-routed legs now exist as properties: P-i BC-1.02.019 dense-grid triple equality over [-10, 110] (arm64 generated table vs CPython oracle), P-j BC-1.02.025 float64 token-format fuzz, P-k BC-1.02.027 _hm fuzz, P-l BC-1.02.028 win_ms fuzz in [300000, 1e12]; P-b and P-g oracles restated as LIVE pinned-CPython calls per generated input (ARCH-07 recipe) — a static pinned table cannot oracle random inputs (A2-08)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-041: Row-1 widget family — for-all property, differential, and lint/syscall legs (S1.02)

## Property Statement

Eight for-all claims — twelve with the pass-5 additions — quantified over generators,
the property rows the S1.02 VP
tables mark "property proof" / "fuzz vs oracle" / "lint" / "fake FileSystem" against
VP-028's bounded golden tables. VP-028 keeps the authored-corner tables; this VP
delivers the quantified legs:

- **P-a (BC-1.02.001):** for all string ids and prefix lists, `on_local ==
  any(strings.HasPrefix(id, p))` whenever both are non-empty, else None.
- **P-b (BC-1.02.016):** for every finite numeric `api`, the shown suffix is present
  iff `api >= 60000`, and spells `\e[2m·` + `_hm(api)` + `\e[0m`.
- **P-c (BC-1.02.018):** brackets appear iff at least two inner parts are > 0.
- **P-d (BC-1.02.019):** the blue channel is 30 for all finite inputs.
- **P-i (BC-1.02.019):** for all float64 `pct` in a dense grid over [-10, 110] the Go
  heat triple (r, g, b) equals the CPython triple (generated table vs oracle, arm64;
  ADV-P5-A2-04/B08).
- **P-j (BC-1.02.025):** for all float64 inputs the Go token-format output equals the
  CPython `_fmt_tok_c` output (fuzz vs oracle; ADV-P5-A2-04/B08).
- **P-k (BC-1.02.027):** `_hm` equals CPython for finite float64 inputs across the
  full range (fuzz vs oracle; ADV-P5-A2-04/B08).
- **P-l (BC-1.02.028):** for finite `win_ms` in [300000, 1e12] the Go text equals the
  CPython text (fuzz vs oracle; ADV-P5-A2-04/B08).
- **P-e (BC-1.02.021):** `pyfmt.Str(v)` equals CPython `str(v)` for generated JSON
  values (nested lists/objects, big ints, floats).
- **P-f (BC-1.02.022):** `PosixNormpath`/`NtNormpath` + `Basename` equal CPython for
  generated path strings, per OS flavour.
- **P-g (BC-1.02.023):** for all float64 `hr` (NaN, ±Inf, ±0 included) the Go segment
  equals the oracle's; no numeric `hr` degrades.
- **P-h (BC-1.02.004):** the branch walk terminates for every start path (strictly
  shorter `d` each iteration until `dirname(d) == d`) and performs no write syscalls
  (fake-FileSystem observation, all three OSes).
- **Lint (BC-1.02.022):** the normpath label is never produced via
  `filepath.Clean` — an ARCH-08 lint-job leg with the VP-022 positive-coverage
  discipline: one planted `filepath.Clean` mutant flagged, real tree zero.

## Source Contract

- **Primary BC:** BC-1.02.001 — Lane pill prefix-match universality row.
- **Partial coverage:** BC-1.02.004, BC-1.02.016, BC-1.02.018, BC-1.02.019,
  BC-1.02.021, BC-1.02.022, BC-1.02.023, BC-1.02.025, BC-1.02.027, BC-1.02.028 (the
  rows those contracts' VP tables route to property/fuzz/lint/syscall proofs).
- **Invariant verified:** NFR-003 byte parity on the whole row-1 surface (joint with
  VP-028's tables and the Tier A corpus, VP-009).

## Property Class and Verification Method

- **Class:** invariant (universality rows).
- **Method:** property test (testing/quick) for P-a, P-b, P-c, P-d, P-g; Tier C
  differential fuzz for the oracle rows P-e, P-f, P-g/P-h oracle halves, budgeted by
  `HYLO_PARITY_FUZZSECONDS` (nightly leg, ARCH-08), same oracle discipline as VP-011;
  fake-FileSystem table for P-h's write-scope observation; a planted-mutant lint leg
  for the `filepath.Clean` rule.
- **Honesty:** testable-only; generator honesty noted per row (P-f's generator
  produces plain generated path strings; flavour choice is fixed per leg, not
  asserted).

## Generators and Oracles

| Row | Generator | Oracle |
|---|---|---|
| P-a | sized string pairs: id and comma-split prefix lists crossing match/mismatch/case boundaries | structural: re-derive `any(HasPrefix)` |
| P-b | float64 api spread around 60000 ± ulp, plus NaN/-0/Inf dispositions | structural presence predicate + live `_hm` oracle call (ARCH-07 recipe; a pinned table cannot cover generated inputs, ADV-P5-A2-08) |
| P-c | part tuples with zeros, positives, and >0 counts 0..5 | structural bracket predicate |
| P-d | finite float64 grid | structural constant-30 observation |
| P-i | dense float64 grid over [-10, 110] | pinned CPython 3.11 heat oracle, per-cell (ARCH-07 recipe) |
| P-j | full float64 range incl. subnormals and overflow neighbours | pinned CPython 3.11 `_fmt_tok_c` oracle, live call per input (ARCH-07 recipe) |
| P-k | finite float64 full range | pinned CPython 3.11 `_hm` oracle, live call per input (ARCH-07 recipe) |
| P-l | finite win_ms in [300000, 1e12] | pinned CPython 3.11 oracle, live call per input (ARCH-07 recipe) |
| P-e | generated JSON values (nesting ≤ 6, big ints, floats, strings) | pinned CPython 3.11 `str()` oracle (ARCH-07 recipe) |
| P-f | generated path strings with `//`, `.`, `..`, trailing slashes | pinned CPython 3.11 `posixpath`/`ntpath` oracle per flavour |
| P-g | full float64 range incl. NaN/±Inf/±0 and hour-scale magnitudes | pinned CPython 3.11 oracle, live call per generated input (ARCH-07 recipe); VP-028's tables pin the bounded corners |
| P-h | synthesized directory layouts of bounded depth on temp dirs | fake-FileSystem syscall log: zero writes |

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Property test | `testing/quick` | sized (quick does not shrink) | P-a, P-b, P-c, P-d, P-g |
| Generated table vs oracle | Go test, arm64 leg | yes — dense grid | P-i |
| Tier C differential fuzz | parity harness | `HYLO_PARITY_FUZZSECONDS` | P-e, P-f, P-g/P-h oracle halves, P-j, P-k, P-l |
| Fake-FileSystem table | Go test, temp dirs + syscall log | yes — bounded depth/width | P-h write scope + termination |
| Planted-mutant lint | ARCH-08 lint job leg | 1 mutant flagged, real tree 0 | `filepath.Clean` absence |

## Proof Harness Skeleton

```go
func TestRow1Prop_All(t *testing.T) {
    // A2-05 lesson applied: a Values filler must ASSIGN each arg
    // (args[i] = reflect.ValueOf(x)); args arrives as zero reflect.Values.
    pillCfg := &quick.Config{MaxCount: 500, Values: func(args []reflect.Value, r *rand.Rand) {
        args[0] = reflect.ValueOf(genID(r))        // string id, non-empty
        args[1] = reflect.ValueOf(genPrefixes(r))  // prefix list, non-empty entries
    }}
    if err := quick.Check(func(id string, prefixes []string) bool {
        return onLocal(id, prefixes) == reDerivePrefixMatch(id, prefixes) // P-a
    }, pillCfg); err != nil {
        t.Fatalf("P-a violated: %v", err)
    }
    hrCfg := &quick.Config{MaxCount: 500, Values: func(args []reflect.Value, r *rand.Rand) {
        args[0] = reflect.ValueOf(genHR(r)) // full float64 range incl. NaN/±Inf/±0
    }}
    if err := quick.Check(func(hr float64) bool {
        seg := renderHourRate(hr)
        // P-g: no numeric hr degrades. A2-08: the oracle is the pinned CPython
        // executable called LIVE per generated input (ARCH-07 recipe) — a static
        // pinned table cannot oracle randomly generated full-range floats.
        return seg == oracleHourRateSegment(hr) && !seg.degraded
    }, hrCfg); err != nil {
        t.Fatalf("P-g violated: %v", err)
    }
}

func TestBranchWalk_ReadOnlyTermination(t *testing.T) { // P-h (BC-1.02.004)
    for _, layout := range SynthLayouts {
        fs := newFakeFS(layout)
        _, ok := walkBranch(fs, layout.Start)
        if !ok || fs.SyscallLog().WriteOps() != 0 { // termination + zero write syscalls
            t.Fatalf("layout %q: ok=%v writes=%d", layout.Name, ok, fs.SyscallLog().WriteOps())
        }
    }
}
// P-e/P-f oracle rows ride TestParityTierC_DiffFuzz under internal/parity
// (HYLO_PARITY_FUZZSECONDS budget, VP-011 oracle discipline), as do the pass-5
// oracle rows P-j (_fmt_tok_c), P-k (_hm) and P-l (win_ms); P-i rides the arm64
// dense-grid generated-table test (BC-1.02.019); the filepath.Clean
// lint leg rides the ARCH-08 lint job with one planted mutant (VP-022 discipline).
```

## Named Tests (OD-145 table where applicable)

`TestRow1Prop_All` and `TestBranchWalk_ReadOnlyTermination` (in-tree quick set);
differential rows ride `TestParityTierC_DiffFuzz` (ARCH-07 OD-145 table); parity
families `row1`/`transcript`/`cost` case grammar.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Infinite (generators), sized | failures print the counterexample directly (quick does not shrink) |
| Proof complexity | Low–medium | structural models are small; oracle rows reuse ARCH-07 |
| Tool support | Full | stdlib testing/quick; fake FS is test scaffolding |
| Estimated proof time | Days | generator authoring dominates |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-18 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
