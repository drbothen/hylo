---
document_type: verification-property
level: L4
version: "1.3"
status: draft
producer: architect
timestamp: 2026-11-22T02:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-05-platform.md, behavioral-contracts/ss-03/BC-3.02.001.md, behavioral-contracts/ss-03/BC-3.02.002.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "115c068"
traces_to: prd.md
source_bc: BC-3.02.002
bcs: [BC-3.02.001, BC-3.02.002]
module: internal/platform (proc_*.go)
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-18T09:19:00Z: ADV-P3 fix (A2-24) — fake-chain seam made explicit: the skeleton probes read the injected pid chain through the production reader seam, never the real OS", "1.3 2026-11-22T02:00:00Z: pass-13 fix (ADV-P13-A2-05) — the depth bound respelled to the registered key statusline.window_age.max_depth (default 6, D15; no hard-coded literal in statement or sketch); new zero-probe leg: max_depth = 0 enters no walk, ZERO ancestor probes, table-covered (the cache-003 empty-bin parity reliance, BC-6.01.002 conditional child key)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-033: Native process probe correctness per OS

## Property Statement

`FindAncestor` obeys the register of named rules identically in unit on every OS leg:
walk from `os.Getppid()` checking the parent first; at most `statusline.window_age.max_depth`
levels — the registered key (D15), default 6, never a hard-coded literal; stop at pid <= 1;
`basename(comm)` match with case-insensitive `.exe` stripping on Windows; start time
truncated to whole seconds returned as float under the legacy `proc_start` key (raw
probe values such as 100.7 truncate to 100.0 — the fake chains carry untruncated raw
values so the truncation rule itself can fail); PID-reuse
guard (parent created before child) on Windows. A configured `max_depth` of 0 enters
no walk at all — ZERO ancestor probes (BC-3.02.001's "at most `max_depth` probe calls"
leg) — the behavior the unseeded `cache-003` parity case relies on when it declares the
empty-bin fake PATH with the conditional `HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0` child
key (BC-6.01.002 key set; VP-014, VP-019, dtu-assessment). Probe-result differences between
macOS/Linux are the ruled OD-76 exclusion entries; the symlinked-binary name case is
measured in the probe test (OD-139 deferral).

## Source Contract

- **Primary BC:** BC-3.02.002 — ps-parse replacement: named per-OS edge differences
  (macOS/Linux).
- **Partial coverage:** BC-3.02.001 (whole-second truncation; `proc_start` key first).
- **Invariant verified:** DI-012 (OD-76 differences are named, never runtime-discovered);
  AD-07 (native probe replaces ps; removes the up-to-6 s latency tail).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test per OS with fake PID chains — depth/stop/name rules, the
  zero-probe `max_depth = 0` leg, the
  PID-reuse guard, truncation; parity flows through seeded `proc_start` cases (probe
  not exercised in parity); the real-syscall legs live in the per-OS CI matrix.
- **Honesty:** testable-only (real syscalls); unit rules table-covered, syscall legs
  observed in CI.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Fake-chain tables | Go test per build tag | yes — depth 0..7 and the configured `max_depth`, incl. `max_depth = 0` ⇒ zero probes; stop, name rules | rule register |
| Seeded parity | proc_start cases (VP-009) | corpus-bounded | end-to-end ⌂ bytes |
| Real-syscall observation | windows-2025 / macos-15 / ubuntu CI legs | process | probe smoke rows |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestFindAncestor_RuleRegister(t *testing.T) {
    for _, tc := range FakePIDChains { // WantStart is the pre-truncated expectation;
        // chains include raw values like 100.7 whose expectation is 100.0, so an
        // implementation that skips truncation fails here. MaxDepth is the case's
        // configured depth — the registered key statusline.window_age.max_depth
        // (default 6), never a hard-coded literal (ADV-P13-A2-05, D15).
        probe := newFakeProbe(tc.Chain) // A2-24 fake-chain seam: the probe reads the
        // injected pid chain via the same reader seam production uses, never the OS
        start, ok := probe.FindAncestor(tc.PID, tc.Name, tc.MaxDepth)
        if ok != tc.WantOK || (ok && start != tc.WantStart) {
            t.Fatalf("%s: ok=%v start=%v want=%v", tc.Name, ok, start, tc.WantStart)
        }
    }
    // ADV-P13-A2-05: the zero-depth leg — max_depth = 0 enters no walk at all,
    // ZERO ancestor probes; the behavior cache-003's empty-bin fake PATH relies
    // on (conditional HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0 child key, BC-6.01.002).
    z := newFakeProbe(knownChain()) // a chain with a matching ancestor in it
    start, ok := z.FindAncestor(rootPid(), knownName(), 0)
    if ok || start != 0 || z.probeCalls() != 0 {
        t.Fatalf("max_depth=0: ok=%v start=%v probeCalls=%d; want false/0/0", ok, start, z.probeCalls())
    }
}
```

## Named Tests (OD-145 table where applicable)

`platform` parity family for seeded cases; in-tree `TestFindAncestor_RuleRegister`
(incl. the zero-depth zero-probe leg, ADV-P13-A2-05);
D4-EX-1 Windows difference is VP-014's fake-probe test.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Rule register + chains | bounded |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | three-OS syscall smoke legs |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
