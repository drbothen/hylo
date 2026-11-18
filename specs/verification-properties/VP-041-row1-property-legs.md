---
document_type: verification-property
level: L4
version: "1.5"
status: draft
producer: architect
timestamp: 2026-11-19T18:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.02.001.md, behavioral-contracts/ss-01/BC-1.02.004.md, behavioral-contracts/ss-01/BC-1.02.016.md, behavioral-contracts/ss-01/BC-1.02.018.md, behavioral-contracts/ss-01/BC-1.02.019.md, behavioral-contracts/ss-01/BC-1.02.021.md, behavioral-contracts/ss-01/BC-1.02.022.md, behavioral-contracts/ss-01/BC-1.02.023.md, behavioral-contracts/ss-01/BC-1.02.025.md, behavioral-contracts/ss-01/BC-1.02.027.md, behavioral-contracts/ss-01/BC-1.02.028.md, prd-supplements/test-vectors.md]
input-hash: "c25da45"
traces_to: prd.md
source_bc: BC-1.02.001
bcs: [BC-1.02.001, BC-1.02.004, BC-1.02.016, BC-1.02.018, BC-1.02.019, BC-1.02.021, BC-1.02.022, BC-1.02.023, BC-1.02.025, BC-1.02.027, BC-1.02.028, BC-1.02.002, BC-1.02.003, BC-1.02.006, BC-1.02.007, BC-1.02.009, BC-1.02.010, BC-1.02.013, BC-1.02.015]
module: internal/statusline (row-1 file families)
proof_method: property-test (testing/quick)
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.0 2026-11-18T15:05:00Z: created — ADV-P4 fix (B03, plan item 18): S1.02 for-all property legs split from VP-028, exactly as VP-040 was split from VP-027 in pass 3; VP-028 keeps the bounded golden tables", "1.1 2026-11-18T23:45:00Z: ADV-P5 fixes (A2-04, B08, A2-08) — the four BC-routed legs now exist as properties: P-i BC-1.02.019 dense-grid triple equality over [-10, 110] (arm64 generated table vs CPython oracle), P-j BC-1.02.025 float64 token-format fuzz, P-k BC-1.02.027 _hm fuzz, P-l BC-1.02.028 win_ms fuzz in [300000, 1e12]; P-b and P-g oracles restated as LIVE pinned-CPython calls per generated input (ARCH-07 recipe) — a static pinned table cannot oracle random inputs (A2-08)", "1.2 2026-11-19T12:00:00Z: pass-6 fixes (B01/call 10, A2-16: eight properties P-m..P-t added for the ADV-P6-B01 BCs (bcs: and the generator table extended); P-g's live-oracle half moves to the Tier C harness (VP-038 discipline); P-h has no oracle half)", "1.3 2026-11-19T18:00:00Z: pass-7 fix (A2-11) — P-b's live `_hm` oracle half moves to the Tier C harness with P-g's (pass-6 A2-16 left it behind): the Generators table row no longer claims a live in-tree oracle call, the Method quick-set lists the structural halves only, and the Tier C Proof Method row gains P-b", "1.4 2026-11-20T12:00:00Z: pass-8 residual sweep (task 5) — P-o width formula corrected to 10 + 1 + len(number text) + 1 + len(denominator text) (the middle 1 is the %; BC-1.02.006 PC7/VP row)", "1.5 2026-11-20T15:00:00Z: pass-9 fixes (ADV-P9-A2-13, ADV-P9-A2-14, ADV-P9-B06; orchestrator call 3) — P-b gains its missing precondition (the API suffix exists only inside the timer segment, which renders only when dur > 60000, SL:540/SL:551-553; the generator draws dur > 60000); P-t restricted to absent-or-finite timers in NON-DEGRADING renders (CP-S12/S13/O05 carved out: predicate holds, render degrades, no segment); the Method bullet now names the P-i generated-table leg, which previously appeared only in the Proof Method table"]
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

Eight for-all claims — twenty with the pass-6 additions — quantified over generators,
the property rows the S1.02 VP
tables mark "property proof" / "fuzz vs oracle" / "lint" / "fake FileSystem" against
VP-028's bounded golden tables. VP-028 keeps the authored-corner tables; this VP
delivers the quantified legs:

- **P-a (BC-1.02.001):** for all string ids and prefix lists, `on_local ==
  any(strings.HasPrefix(id, p))` whenever both are non-empty, else None.
- **P-b (BC-1.02.016):** inside the timer segment — which renders only when
  `dur > 60000` (gate SL:540; suffix SL:551-553) — for every finite numeric `api`,
  the shown `·<api>` suffix is present iff `api >= 60000`, and spells
  `\e[2m·` + `_hm(api)` + `\e[0m`; the generator draws `dur > 60000` (a generator
  varying `dur` below the gate false-fails — pass-9 ADV-P9-A2-13).
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
- **P-m (BC-1.02.002, ADV-P6-B01):** for all generated (display_name, id) string
  pairs including empties, the label is the first non-empty of (display_name, id, "?").
- **P-n (BC-1.02.003, ADV-P6-B01):** for all non-empty generated strings, the label is
  `pyfmt.Basename(pyfmt.Normpath(s))`, or the normpath when empty, per host OS — the
  differential half (equals the CPython posixpath/ntpath golden per generated input)
  rides the Tier C harness, VP-011 discipline.
- **P-o (BC-1.02.006, ADV-P6-B01):** for all finite `pct` in [0,100],
  `filled == min(floor(pct/10 + 0.5), 10)`, and the visible width of the segment is
  `10 + 1 + len(number text) + 1 + len(denominator text)` (the middle `1` is the `%`;
  BC-1.02.006 PC7 / VP row).
- **P-p (BC-1.02.007, ADV-P6-B01):** for all non-negative int triples with positive
  sum, each shown percentage equals `pyfmt.Round(n/total*100)` (the Round equivalence
  itself is oracle-pinned by the committed tables).
- **P-q (BC-1.02.009, ADV-P6-B01):** when `reroute_all` matches, row 1 contains no
  limits segment, for any generated stdin.
- **P-r (BC-1.02.010, ADV-P6-B01):** for a numeric reset, the window segment is shown
  only if `reset > now` (shown ⇒ reset > now), over generated (reset, now) pairs.
- **P-s (BC-1.02.013, ADV-P6-B01):** a cached `used` value is displayed only when its
  age < `keep_s`, for generated (now, cached_at, keep_s) triples.
- **P-t (BC-1.02.015, ADV-P6-B01):** for generated ABSENT or FINITE numeric timers in
  non-degrading renders, the timer segment is present iff the number is set and
  > 60000. Degrading renders are carved out (pass-9 ADV-P9-B06, call 3): dur =
  +Infinity (CP-S12), api = +Infinity (CP-S13), and dur ≥ OV with a numeric win_start
  (CP-O05) each satisfy the predicate but degrade the render, so no segment prints.
- **P-e (BC-1.02.021):** `pyfmt.Str(v)` equals CPython `str(v)` for generated JSON
  values (nested lists/objects, big ints, floats).
- **P-f (BC-1.02.022):** `PosixNormpath`/`NtNormpath` + `Basename` equal CPython for
  generated path strings, per OS flavour.
- **P-g (BC-1.02.023):** for all float64 `hr` (NaN, ±Inf, ±0 included) the Go segment
  is present, well-formed and non-degrading (structural half, in-tree); the
  equals-the-oracle differential half rides the Tier C harness per generated input
  (A2-16 — a unit test never spawns the oracle, VP-038 discipline); no numeric `hr`
  degrades.
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
  rows those contracts' VP tables route to property/fuzz/lint/syscall proofs);
  BC-1.02.002, BC-1.02.003, BC-1.02.006, BC-1.02.007, BC-1.02.009, BC-1.02.010,
  BC-1.02.013, BC-1.02.015 (ADV-P6-B01: the "for all … / property test" rows those
  contracts route to VP-028, which VP-028 delegates here — P-m..P-t).
- **Invariant verified:** NFR-003 byte parity on the whole row-1 surface (joint with
  VP-028's tables and the Tier A corpus, VP-009).

## Property Class and Verification Method

- **Class:** invariant (universality rows).
- **Method:** property test (testing/quick) for the structural rows P-a, P-c,
  P-d and the STRUCTURAL HALVES of P-b and P-g (in-tree: the structural half only —
  no live interpreter call, per
  VP-038's oracle discipline, A2-16); a generated-table-vs-oracle leg for P-i (the
  dense heat triple over [-10, 110], arm64); Tier C differential fuzz for the oracle rows
  P-e, P-f, P-g, P-j, P-k, P-l, P-n AND P-b's differential half, budgeted by
  `HYLO_PARITY_FUZZSECONDS` (nightly leg, ARCH-08), same oracle discipline as VP-011;
  fake-FileSystem table for P-h's write-scope observation (P-h has no oracle half);
  a planted-mutant lint leg
  for the `filepath.Clean` rule.
- **Honesty:** testable-only; generator honesty noted per row (P-f's generator
  produces plain generated path strings; flavour choice is fixed per leg, not
  asserted).

## Generators and Oracles

| Row | Generator | Oracle |
|---|---|---|
| P-a | sized string pairs: id and comma-split prefix lists crossing match/mismatch/case boundaries | structural: re-derive `any(HasPrefix)` |
| P-b | float64 api spread around 60000 ± ulp, plus NaN/-0/Inf dispositions | structural presence predicate in-tree; differential half = pinned CPython 3.11 `_hm` oracle, live call per generated input UNDER THE TIER C HARNESS only (A2-11, same discipline as P-g; a pinned table cannot cover generated inputs, ADV-P5-A2-08) |
| P-c | part tuples with zeros, positives, and >0 counts 0..5 | structural bracket predicate |
| P-d | finite float64 grid | structural constant-30 observation |
| P-i | dense float64 grid over [-10, 110] | pinned CPython 3.11 heat oracle, per-cell (ARCH-07 recipe) |
| P-j | full float64 range incl. subnormals and overflow neighbours | pinned CPython 3.11 `_fmt_tok_c` oracle, live call per input (ARCH-07 recipe) |
| P-k | finite float64 full range | pinned CPython 3.11 `_hm` oracle, live call per input (ARCH-07 recipe) |
| P-l | finite win_ms in [300000, 1e12] | pinned CPython 3.11 oracle, live call per input (ARCH-07 recipe) |
| P-e | generated JSON values (nesting ≤ 6, big ints, floats, strings) | pinned CPython 3.11 `str()` oracle (ARCH-07 recipe) |
| P-f | generated path strings with `//`, `.`, `..`, trailing slashes | pinned CPython 3.11 `posixpath`/`ntpath` oracle per flavour |
| P-g | full float64 range incl. NaN/±Inf/±0 and hour-scale magnitudes | in-tree structural half (presence + no-degrade model); differential half = pinned CPython 3.11 oracle, live call per generated input UNDER THE TIER C HARNESS only (A2-16; VP-038: the oracle is not callable from unit tests); VP-028's tables pin the bounded corners |
| P-h | synthesized directory layouts of bounded depth on temp dirs | fake-FileSystem syscall log: zero writes (no oracle half, A2-16) |
| P-m | (display_name, id) string pairs incl. both empty, id-only, name-only | structural: re-derive first-non-empty |
| P-n | generated path strings, empty and non-empty | structural Basename∘Normpath identity in-tree; CPython posixpath/ntpath golden per input under the Tier C harness |
| P-o | finite pct in [0,100] around each k·10 boundary ± ulp | structural: re-derive floor(pct/10+0.5) clamp and the width sum |
| P-p | non-negative int triples incl. zero parts and max-int parts | structural: re-derive via pyfmt.Round (oracle-pinned by the committed tables) |
| P-q | generated stdin objects with reroute_all prefix sets on/off | structural: limits-segment absence predicate |
| P-r | (reset, now) pairs spanning reset < now, == now, > now | structural: shown ⇒ reset > now |
| P-s | (now, cached_at, keep_s) triples around the keep_s edge | structural: age < keep_s display predicate |
| P-t | absent or finite numeric timers around 60000 ± ulp; renders constrained to non-degrading dispositions (CP-S12/S13/O05 renders carved out, pass-9 call 3) | structural: presence iff number && > 60000, over absent/finite dur in non-degrading renders |

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Property test | `testing/quick` | sized (quick does not shrink) | P-a, P-b, P-c, P-d, P-g (structural half), P-m..P-t |
| Generated table vs oracle | Go test, arm64 leg | yes — dense grid | P-i |
| Tier C differential fuzz | parity harness | `HYLO_PARITY_FUZZSECONDS` | P-e, P-f, P-g, P-n, P-j, P-k, P-l, P-b (oracle halves under the harness, A2-16/A2-11) |
| Fake-FileSystem table | Go test, temp dirs + syscall log | yes — bounded depth/width | P-h write scope + termination |
| Planted-mutant lint | ARCH-08 lint job leg | 1 mutant flagged, real tree 0 | `filepath.Clean` absence |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
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
        // P-g structural half (in-tree, A2-16): presence + no-degrade + well-formed
        // model. A2-08/A2-16: the equals-oracle differential half is NOT callable
        // from a unit test (VP-038 discipline) — it rides the Tier C harness, where
        // the pinned CPython executable is called LIVE per generated input
        // (ARCH-07 recipe) — a static pinned table cannot oracle random floats.
        return segmentWellFormed(seg) && !seg.degraded
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
