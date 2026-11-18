---
document_type: verification-property
level: L4
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-18T21:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-05-platform.md, architecture/ARCH-07-parity-harness.md, behavioral-contracts/ss-03/BC-3.02.001.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "4f6b4b0"
traces_to: prd.md
source_bc: BC-3.02.001
bcs: [BC-3.02.001]
module: internal/platform (proc), internal/statusline (window age)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-19T18:00:00Z: pass-7 fix (A2-05) — the riding test name is respelled everywhere to the settled TestWindowAge_D4EX1_Windows_AncestorFound (VP-012 v1.13 and BC-6.03.004's delegation), replacing the formerly called-settled TestWindowAge_D4EX1_Windows; the concrete member renders the ⌂ suffix, which requires the fake ProcStarter to return a start (EC-008)", "1.3 2026-11-18T17:50:00Z: pass-10 fix (A2-07) — the ruled ⌂ bytes anchored: pinned by the BC-3.02.001 / BC-1.02.017 canonical vector tables, with the rider's expected output those tables' expected column (the sketch's tc.WantSuffix), no longer an unanchored phrase; the 'macOS/Linux probe behaviour is not touched' clause given legs — macOS/Linux native-probe rendering rides the Tier A corpus parity (VP-009) and the per-OS probe postconditions (VP-033), and VP-012's machinery prevents broadening (property statement and method bullet)", "1.4 2026-11-18T21:00:00Z: pass-11 fix (A2-04) — the bound's legs corrected: the probe is NOT exercised in parity on any OS (parity flows through seeded proc_start cases, VP-033), so the macOS/Linux probe differences ride the closed-set exclusion id OD-76 (OD-110) with its own table tests, not the Tier A corpus parity; the former 'rides the Tier A corpus parity (VP-009)' leg was vacuous (the 1.3 history entry keeps its as-of-pass-10 figures)"]
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
in the sketch as `tc.WantSuffix` (A2-07: formerly an unanchored phrase). macOS/Linux
probe behaviour is outside this exclusion's scope, and that bound has legs: the probe
is NOT exercised in parity on any OS — parity flows through seeded `proc_start` cases
(VP-033) — so the macOS/Linux probe differences are carried by the closed-set
exclusion id `OD-76` (OD-110: true start in the repeated DST hour; ⌂ where legacy's
localized `ps` fails) with its own table tests, the per-OS probe rules are
table-covered by VP-033, and VP-012's machinery prevents the exclusion set from
broadening (A2-04: the former "rides the Tier A corpus parity (VP-009)" leg was
vacuous — the seeded cases never invoke the native probe).

## Source Contract

- **Primary BC:** BC-3.02.001 — Window start via native per-OS ancestor probe;
  whole-second truncation; `proc_start` key first.
- **Invariant verified:** DI-012 (named, tested deviation — OD-105/OD-110); the
  exclusion list cannot broaden (VP-012 closes the machinery).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test with fake probe — `TestWindowAge_D4EX1_Windows_AncestorFound`
  exercises
  the suffix format, the visibility gate, and the whole-second truncation, with the
  fake probe returning ruled values; each row's expected bytes come from the
  BC-3.02.001 / BC-1.02.017 canonical vector tables (the `tc.WantSuffix` column of
  the sketch — not an ad-hoc expectation, A2-07).
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
        out := renderWindowAge(fakeProc(tc.Start), fakeNow(tc.Now), tc.Width)
        if out != tc.WantSuffix { t.Fatalf("%s: %q", tc.Name, out) }
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
