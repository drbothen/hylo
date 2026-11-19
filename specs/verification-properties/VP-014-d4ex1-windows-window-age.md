---
document_type: verification-property
level: L4
version: "1.7"
status: draft
producer: architect
timestamp: 2026-11-22T12:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-05-platform.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-03/BC-3.02.001.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "93539b0"
traces_to: prd.md
source_bc: BC-3.02.001
bcs: [BC-3.02.001, BC-1.02.017]
module: internal/platform (proc), internal/statusline (window age)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-19T18:00:00Z: pass-7 fix (A2-05) — the riding test name is respelled everywhere to the settled TestWindowAge_D4EX1_Windows_AncestorFound (VP-012 v1.13 and BC-6.03.004's delegation), replacing the formerly called-settled TestWindowAge_D4EX1_Windows; the concrete member renders the ⌂ suffix, which requires the fake ProcStarter to return a start (EC-008)", "1.3 2026-11-18T17:50:00Z: pass-10 fix (A2-07) — the ruled ⌂ bytes anchored: pinned by the BC-3.02.001 / BC-1.02.017 canonical vector tables, with the rider's expected output those tables' expected column (the sketch's tc.WantSuffix), no longer an unanchored phrase; the 'macOS/Linux probe behaviour is not touched' clause given legs — macOS/Linux native-probe rendering rides the Tier A corpus parity (VP-009) and the per-OS probe postconditions (VP-033), and VP-012's machinery prevents broadening (property statement and method bullet)", "1.4 2026-11-18T21:00:00Z: pass-11 fix (A2-04) — the bound's legs corrected: the probe is NOT exercised in parity on any OS (parity flows through seeded proc_start cases, VP-033), so the macOS/Linux probe differences ride the closed-set exclusion id OD-76 (OD-110) with its own table tests, not the Tier A corpus parity; the former 'rides the Tier A corpus parity (VP-009)' leg was vacuous (the 1.3 history entry keeps its as-of-pass-10 figures)", "1.5 2026-11-22T04:00:00Z: pass-12 residual (item 5, call 2) — the bound's census restated: every corpus case either seeds `proc_start` or is `cache-003` (unseeded, no probe on either side — empty PATH bin oracle-side, HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0 hylo-side); the former 'parity flows through seeded proc_start cases' phrasing implied no case is unseeded", "1.6 2026-11-22T12:00:00Z: pass-13 fix (A2-04) — bcs: gains BC-1.02.017 (its Inv 3 names this rider test; its canonical vector table is the second pin of the ruled suffix bytes; the reciprocal VP-table row in that contract is its owner's fix); the statement and fake-probe table pin the three walk behaviours BC-3.02.001's vector table routes here jointly with VP-033 — cache-first short-circuit (zero probes), `.0` serialisation, at-most-max_depth probes — so a routed row no longer outruns the verifying statement", "1.7 2026-11-25T12:00:00Z: pass-14 fix (A2-11, cosmetic) — the Proof Harness Skeleton catches up with the three walk behaviours the pass-13 statement and Method bullet already require: the cache-first row asserts ZERO probe calls on the counting fake starter and the whole-second row pins the `.0` serialisation of the stored value, beside the existing at-most-max_depth bound (the sketch previously checked only the upper bound, so a port probing on the cache-first row or dropping the `.0` suffix sketched green); no property or oracle change"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-014: D4-EX-1 — ⌂ window-age difference on Windows is bounded and tested

## Property Statement

The ruled Windows difference (legacy showed no ⌂ on Windows because `ps` is absent; the
native probe shows it) is admitted only through the exclusion id `D4-EX-1` with its
dedicated fake-probe test: with `ProcStarter.WindowStart` faked, the Go port renders the
⌂ suffix with the ruled visibility gate on Windows exactly as the ruled bytes demand —
the ruled bytes are pinned by the canonical vector tables of BC-3.02.001 and
BC-1.02.017, and the rider's expected output is those tables' expected column, surfaced
in the sketch as `tc.WantSuffix` (A2-07: formerly an unanchored phrase). The rider test
is the one BC-1.02.017 Inv 3 names (pass-13 A2-04 reciprocity: `bcs:` gains
BC-1.02.017). BC-3.02.001's vector table additionally routes three walk behaviours
here jointly with VP-033, and the fake-probe table pins each on the ruled path: the
cache-first short-circuit (a numeric cached `proc_start` answers the window age with
zero probe calls on the fake starter), the whole-second `.0` serialisation of the
stored value, and the at-most-`max_depth` probe bound (`statusline.window_age.max_depth`,
BC-3.02.001). macOS/Linux
probe behaviour is outside this exclusion's scope, and that bound has legs: the probe
is NOT exercised in parity on any OS — every corpus case either seeds `proc_start`
(no probe; the seed answers the window start, VP-033) or is `cache-003`, which seeds
no `proc_start` and probes on NEITHER side (pass-12 residual, call 2: the oracle
child's conditional `PATH=<case>/bin` is an EMPTY bin, so legacy's
`subprocess.run(["ps", ...])` raises FileNotFoundError and `claude_window_start`
returns None; the hylo child gets `HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0`, so
`FindAncestor` makes zero probes and returns not-found, BC-3.02.001 — at most
`max_depth` probes; ARCH-07) — so the macOS/Linux probe differences are carried by the closed-set
exclusion id `OD-76` (OD-110: true start in the repeated DST hour; ⌂ where legacy's
localized `ps` fails) with its own table tests, the per-OS probe rules are
table-covered by VP-033, and VP-012's machinery prevents the exclusion set from
broadening (A2-04: the former "rides the Tier A corpus parity (VP-009)" leg was
vacuous — no parity case invokes the native probe, seeded or `cache-003`).

## Source Contract

- **Primary BC:** BC-3.02.001 — Window start via native per-OS ancestor probe;
  whole-second truncation; `proc_start` key first.
- **Invariant verified:** DI-012 (named, tested deviation — OD-105/OD-110); the
  exclusion list cannot broaden (VP-012 closes the machinery).
- **Reciprocity:** BC-1.02.017 Inv 3 names `TestWindowAge_D4EX1_Windows_AncestorFound`
  (pass-13 A2-04); its canonical vector table is the second pin of the ruled suffix
  bytes.

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test with fake probe — `TestWindowAge_D4EX1_Windows_AncestorFound`
  exercises
  the suffix format, the visibility gate, and the whole-second truncation, with the
  fake probe returning ruled values; each row's expected bytes come from the
  BC-3.02.001 / BC-1.02.017 canonical vector tables (the `tc.WantSuffix` column of
  the sketch — not an ad-hoc expectation, A2-07). The routed walk rows carry a probe
  counter on the fake starter: zero probes on the cache-first short-circuit row, at
  most `max_depth` on the walk rows, and the cached-value bytes pinned where the row
  serialises the whole second with a `.0` suffix (pass-13 A2-04).
- **Honesty:** testable-only; the OS-scoped difference itself is a ruling, not a
  derivable fact.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Fake-probe table | Go test, `internal/statusline` + `internal/platform` | yes — ruled value table | ⌂ format x gate x truncation on the ruled OS |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestWindowAge_D4EX1_Windows_AncestorFound(t *testing.T) {
    for _, tc := range WindowAgeTable {
        p := countingProc{Starter: fakeProc(tc.Start)} // pass-13 A2-04: routed rows observe the walk
        out := renderWindowAge(&p, fakeNow(tc.Now), tc.Width)
        if out != tc.WantSuffix { t.Fatalf("%s: %q", tc.Name, out) }
        if tc.CachedStart != "" && p.Probes != 0 { // pass-14 A2-11: cache-first
            t.Fatalf("%s: %d probes on a cached proc_start, want 0", // short-circuit —
                tc.Name, p.Probes) // a numeric cached value answers with ZERO probes
        }
        if p.Probes > windowAgeMaxDepth { // routed row: at-most-max_depth probes (BC-3.02.001)
            t.Fatalf("%s: %d probes > max_depth %d", tc.Name, p.Probes, windowAgeMaxDepth)
        }
        if tc.WantWholeSecond != "" && // pass-14 A2-11: the `.0` pin — the stored
            !strings.Contains(out, tc.WantWholeSecond+".0") { // value serialises as
            t.Fatalf("%s: stored value not `.0`-serialised, got %q", tc.Name, out) // the whole second
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestWindowAge_D4EX1_Windows_AncestorFound` (settled name per VP-012 v1.13 and
BC-3.02.001's delegation; the fake `ProcStarter` returns a start so `⌂` can show,
EC-008); Windows-leg pinned by the
windows-2025 CI assumption set (PRD §9.5).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Small | ruled value table |
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
