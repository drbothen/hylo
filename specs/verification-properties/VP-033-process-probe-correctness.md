---
document_type: verification-property
level: L4
version: "1.2"
status: draft
producer: architect
timestamp: 2026-11-18T09:19:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-05-platform.md, behavioral-contracts/ss-03/BC-3.02.001.md, behavioral-contracts/ss-03/BC-3.02.002.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "e7d5ba8"
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
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-18T09:19:00Z: ADV-P3 fix (A2-24) — fake-chain seam made explicit: the skeleton probes read the injected pid chain through the production reader seam, never the real OS"]
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
walk from `os.Getppid()` checking the parent first; at most 6 levels; stop at pid <= 1;
`basename(comm)` match with case-insensitive `.exe` stripping on Windows; start time
truncated to whole seconds returned as float under the legacy `proc_start` key (raw
probe values such as 100.7 truncate to 100.0 — the fake chains carry untruncated raw
values so the truncation rule itself can fail); PID-reuse
guard (parent created before child) on Windows. Probe-result differences between
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
  PID-reuse guard, truncation; parity flows through seeded `proc_start` cases (probe
  not exercised in parity); the real-syscall legs live in the per-OS CI matrix.
- **Honesty:** testable-only (real syscalls); unit rules table-covered, syscall legs
  observed in CI.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Fake-chain tables | Go test per build tag | yes — depth 0..7, stop, name rules | rule register |
| Seeded parity | proc_start cases (VP-009) | corpus-bounded | end-to-end ⌂ bytes |
| Real-syscall observation | windows-2025 / macos-15 / ubuntu CI legs | process | probe smoke rows |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestFindAncestor_RuleRegister(t *testing.T) {
    for _, tc := range FakePIDChains { // WantStart is the pre-truncated expectation;
        // chains include raw values like 100.7 whose expectation is 100.0, so an
        // implementation that skips truncation fails here.
        probe := newFakeProbe(tc.Chain) // A2-24 fake-chain seam: the probe reads the
        // injected pid chain via the same reader seam production uses, never the OS
        start, ok := probe.FindAncestor(tc.PID, tc.Name, 6)
        if ok != tc.WantOK || (ok && start != tc.WantStart) {
            t.Fatalf("%s: ok=%v start=%v want=%v", tc.Name, ok, start, tc.WantStart)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

`platform` parity family for seeded cases; in-tree `TestFindAncestor_RuleRegister`;
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
