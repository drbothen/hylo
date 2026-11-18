---
document_type: verification-property
level: L4
version: "1.7"
status: draft
producer: architect
timestamp: 2026-11-19T12:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, behavioral-contracts/ss-01/BC-1.01.003.md, behavioral-contracts/ss-01/BC-1.01.004.md, behavioral-contracts/ss-01/BC-1.01.005.md, behavioral-contracts/ss-01/BC-1.01.006.md, behavioral-contracts/ss-01/BC-1.01.007.md]
input-hash: "98815f4"
traces_to: prd.md
source_bc: BC-1.01.004
bcs: [BC-1.01.003, BC-1.01.004, BC-1.01.005, BC-1.01.006, BC-1.01.007]
module: internal/statusline (width.go, guard frame, term_cols)
proof_method: property-test (testing/quick)
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-18T09:03:00Z: ADV-P3 fixes (A2-05) — both quick.Check return errors are checked (the harness could never fail); *quick.Config with a Values filler supplies the LF/CR-free and SEP-free generators (a nil config would use default generators); “quick shrink” claims removed — testing/quick does not shrink", "1.2 2026-11-18T14:22:00Z: ADV-P4 fix (A2-05) — both Values fillers rewritten to the assigning form args[i] = reflect.ValueOf(x) and segCfg now sets BOTH arguments (text string, cols int); Elem().Set on the zero reflect.Values would panic", "1.3 2026-11-18T23:45:00Z: ADV-P5 fix (A2-34) — P7 split into its own quick.Check: negated-int64 cols from its own generator (the shared anchorCols config could not serve it) and the rows > 2 constraint expressed by construction; the shared segCfg now serves P1/P5/P6 only", "1.4 2026-11-19T12:00:00Z: pass-6 fixes (A2-15: P7 varies the statusline.rows setting (covering rows == 2) with cols < 0, instead of guarding on segment count)", "1.5 2026-11-20T12:00:00Z: pass-8 residual sweep (task 5) — P7 restated per BC-1.01.007 PC2 (incl. negative narrow_cols): row 2 is OMITTED iff rows == 2 and cols < narrow_cols; the former 'present iff rows > 2' phrasing dropped the narrow_cols condition", "1.6 2026-11-20T15:00:00Z: pass-9 fixes (ADV-P9-A2-01/B01, orchestrator call 2) — P7 restated to the canonical TOTAL predicate from legacy SL:1217/SL:1224: row 2 is rendered iff rows ≥ 2 and (rows > 2 or cols == 0 or cols ≥ narrow_cols); the pass-8 omission form was false for rows ≤ 1 (row 2 is never rendered there, so three of the generator's eight settings violated it); omission form and skeleton corrected, and the P7 generator now varies narrow_cols so both halves of the comparison are exercisable", "1.7 2026-11-20T18:00:00Z: pass-11 fixes (A2-11, B03) — P5's 'max-prefix' fit criterion stated per legacy SL:1193-1196 (longest prefix with visible width <= cols; once no SEP remains the row emits as-is and may still exceed cols — P6 is the observable postcondition); P7's generator gains pinned big-int TABLE legs for beyond-int64 NEGATIVE cols (COLUMNS = −10^30 exact, sign-preserved) crossed with narrow_cols = MinInt64 and rows == 2 — the clamp-fails counter-case from BC-1.01.005 PC4, never exercised by the int64-only quick spread"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-040: Frame, width, and trim — for-all property and Tier C differential legs (BC-1.01.003..007)

## Property Statement

Seven for-all claims, quantified over generators — the property rows BC-1.01.003..007
mark "no VP yet" against VP-027's fixed breakpoint matrix. VP-027 keeps the matrix;
this VP delivers the quantified legs:

- **P1 (BC-1.01.003):** for all (rows, cols) and inputs whose rendered strings hold
  no LF/CR (PC5 carve-out), stdout has exactly 1 + [row-2 predicate] renderer rows,
  each LF-terminated.
- **P2 (BC-1.01.004):** `visible(a+b) == visible(a)+visible(b)` whenever neither split
  point falls inside an SGR run.
- **P3 (BC-1.01.004):** Go `visible` equals CPython `len(_ANSI.sub("", s))` on
  generated strings, including astral code points and WTF-8 lone-surrogate byte forms.
- **P4 (BC-1.01.005):** Go `term_cols` equals CPython `int()`-or-0 on generated
  strings: Unicode digits, underscores, signs, whitespace, invalid-UTF-8 byte sequences.
- **P5 (BC-1.01.006):** output = (max-prefix of segments joined by SEP) + (RESET iff
  at least one segment dropped), for generated rows whose segment text excludes the
  exact SEP bytes — the fit criterion stated per legacy SL:1193-1196 (A2-11): the
  prefix kept is the LONGEST whose joined visible width is <= cols, and once no SEP
  remains the row is emitted as-is (which may still exceed cols; the first segment
  alone is the floor only in the sense that rsplit stops there — trim_to_fit never
  splits inside a segment), so P6's `visible(out) <= cols or no SEP` is the
  observable postcondition, not a width guarantee.
- **P6 (BC-1.01.006):** after trim, `visible(out) <= cols` or out contains no SEP.
- **P7 (BC-1.01.007):** for all `statusline.rows` settings and all cols < 0: rows
  untrimmed, and row 2 is rendered iff `rows ≥ 2` and (`rows > 2` or `cols == 0` or
  `cols ≥ narrow_cols`) (legacy SL:1217, SL:1224; BC-1.01.007 PC2–PC4, incl. negative
  narrow_cols) — equivalently, row 2 is omitted iff rows ≤ 1, or (rows == 2 and
  `cols ≠ 0` and `cols < narrow_cols`). Within the cols < 0 domain the `cols == 0`
  disjunct is vacuous, but the predicate is stated as the BC's canonical total
  form, not a domain-restricted rewrite (the pass-8 restricted rewrite is what
  regressed: it required row 2 to be present at rows ≤ 1, where legacy never
  renders it).

## Source Contract

- **Primary BC:** BC-1.01.004 (additivity + CPython-visible differential rows).
- **Partial coverage:** BC-1.01.003 (row/LF structure), BC-1.01.005 (term_cols
  grammar differential), BC-1.01.006 (trim structure + boundedness), BC-1.01.007
  (negative-COLUMNS universality).
- **Invariant verified:** NFR-005 joint (caps are legacy-fixed named constants where
  applicable); oracle isolation per VP-034 (differential legs run under the ARCH-07
  harness: `-s`, frozen clock shim, constructed child env).

## Property Class and Verification Method

- **Class:** invariant (universality rows).
- **Method:** property test (testing/quick) for the structural rows P1, P2, P5, P6,
  P7; Tier C differential fuzz for the oracle rows P3, P4, budgeted by
  `HYLO_PARITY_FUZZSECONDS` (nightly leg, ARCH-08), same oracle discipline as VP-011.
- **Honesty:** testable-only; generator honesty noted per row (P5's generator filters
  SEP-containing segment text rather than asserting on it).

## Generators and Oracles

| Row | Generator | Oracle |
|---|---|---|
| P1 | sized list of segment texts with LF/CR filtered out, cols anchored at the breakpoint matrix ±1 | structural count + termination check |
| P2 | sized code-point strings split at non-SGR indices | algebraic, evaluated directly |
| P3 | SGR-bearing strings: CSI sequences from the oracle-palette alphabet interleaved with astral and lone-surrogate WTF-8 bytes | pinned CPython 3.11 oracle (ARCH-07 recipe) |
| P4 | Python int grammar corners crossed with random decimal/underscore/sign/whitespace permutations and invalid-UTF-8 bytes | pinned CPython 3.11 oracle (ARCH-07 recipe) |
| P5 | segment lists with SEP-free text (filter), crossing drop counts | structural model re-derivation |
| P6 | trim inputs from P5's generator at cols inside/outside the matrix | structural inequality check |
| P7 | `statusline.rows` settings {-1,0,1,2,3,4,5,10} × cols drawn from negated int64 spread × `narrow_cols` drawn from an int64 spread (negatives included, so both halves of the `cols ≥ narrow_cols` comparison are exercisable); PLUS pinned big-int TABLE legs outside the quick generator's int64 reach (quick carries int64 only): beyond-int64 NEGATIVE cols as exact big ints — e.g. COLUMNS = −10^30, per BC-1.01.005 PC4 sign-preservation — crossed with `narrow_cols` = MinInt64 (the "any Int" range admits it) and rows == 2, exercising the clamp-fails counter-case: Python evaluates −10^30 >= −2^63 as False (row 2 hidden) while a clamped MinInt64 comparison would be True (row 2 shown) | structural predicate check of the full rule: rows ≤ 1 never renders row 2; at rows == 2 row 2 hides iff `cols ≠ 0` and `cols < narrow_cols`; rows ≥ 3 always renders it; the big-int legs compare in exact big-int space (BC-1.01.005 PC4: compare big or carry the sign bit, never clamp) |

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Property test | `testing/quick` | sized (quick does not shrink) | P1, P2, P5, P6, P7 |
| Big-int table legs | Go table test (exact big.Int comparisons) | yes — pinned legs | P7 beyond-int64 negative cols (B03; BC-1.01.005 PC4) |
| Tier C differential fuzz | parity harness | `HYLO_PARITY_FUZZSECONDS` | P3, P4 |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestFrameProp_All(t *testing.T) {
    // A2-05: custom generators via Values (a nil config would use defaults);
    // testing/quick does not shrink — failures print the counterexample as-is.
    // A Values filler must ASSIGN each arg (args[i] = reflect.ValueOf(x)):
    // args arrives as zero reflect.Values — Elem()/Set would panic.
    segCfg := &quick.Config{MaxCount: 500, Values: func(args []reflect.Value, r *rand.Rand) {
        args[0] = reflect.ValueOf(genSEPFreeText(r)) // LF/CR-free, SEP-free segments
        args[1] = reflect.ValueOf(anchorCols(r))     // 2-arg property: cols is set too (A2-05)
    }}
    if err := quick.Check(func(text string, cols int) bool {
        segs := splitSegments(text) // SEP-free by construction
        out := renderFrame(segs, cols)
        return framePropMatches(out, segs, cols) // P1/P5/P6 model
    }, segCfg); err != nil {
        t.Fatalf("P1/P5/P6 violated: %v", err)
    }
    // P7 has its own regime (A2-34): the negated-int64 cols spread and the
    // statusline.rows SETTING vary here — A2-15: rows is the BC-1.01.007 setting,
    // not the segment count; the rows==2 half of the iff (row 2 hidden) is tested.
    // B03/pass-11: the quick int generator carries int64 only, so beyond-int64
    // NEGATIVE cols ride pinned big-int TABLE legs — COLUMNS = -10^30 (exact,
    // sign-preserved) with narrow_cols = MinInt64 and rows == 2 must HIDE row 2
    // (Python: -10**30 >= -2**63 is False); a clamped MinInt64 comparison would
    // show it. Compare in big-int space or carry the sign bit (BC-1.01.005 PC4).
    p7Cfg := &quick.Config{MaxCount: 500, Values: func(args []reflect.Value, r *rand.Rand) {
        args[0] = reflect.ValueOf(rowsSettingSpread(r)) // A2-15: statusline.rows ∈ {-1, 0, 1, 2, 3, 4, 5, 10}, covering rows == 2 and rows > 2
        args[1] = reflect.ValueOf(negInt64ColSpread(r)) // negated int64 spread
        args[2] = reflect.ValueOf(int64Spread(r))       // narrow_cols setting, negatives included (pass-9 call 2)
        args[3] = reflect.ValueOf(genSEPFreeText(r))    // enough segments to compose any row count
    }}
    if err := quick.Check(func(rowsSetting, cols, narrowCols int, text string) bool {
        segs := splitSegments(text)
        out := renderFrameWithRows(rowsSetting, segs, cols)
        // P7 model (pass-9 call 2, legacy SL:1217/SL:1224): untrimmed at cols < 0,
        // and row 2 rendered IFF rows >= 2 AND (rows > 2 OR cols == 0 OR
        // cols >= narrowCols) — omitted at rows <= 1, and at rows == 2 exactly
        // when cols != 0 and cols < narrowCols (A2-15, ADV-P9-A2-01/B01).
        return framePropMatchesP7(out, rowsSetting, cols, narrowCols, segs)
    }, p7Cfg); err != nil {
        t.Fatalf("P7 violated: %v", err)
    }
    pairCfg := &quick.Config{MaxCount: 500, Values: func(args []reflect.Value, r *rand.Rand) {
        args[0] = reflect.ValueOf(genSGRBearing(r)) // P2: SGR runs + astral + WTF-8
        args[1] = reflect.ValueOf(genSGRBearing(r))
    }}
    if err := quick.Check(func(a, b string) bool {
        return visible(a+b) == visible(a)+visible(b) // P2, split guards
    }, pairCfg); err != nil {
        t.Fatalf("P2 violated: %v", err)
    }
}
// P3/P4: TestParityTierC_DiffFuzz rows under internal/parity (oracle-bound).
```

## Named Tests (OD-145 table where applicable)

`TestFrameProp_All` (in-tree quick set); differential rows ride
`TestParityTierC_DiffFuzz` (ARCH-07 OD-145 table); parity family `frame` case grammar.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Infinite (generators), sized | failures print the counterexample directly (quick does not shrink) |
| Proof complexity | Low–medium | structural models are small; oracle rows reuse ARCH-07 |
| Tool support | Full | stdlib testing/quick; no new dependency |
| Estimated proof time | Days | generator authoring + model re-derivation |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-17 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
