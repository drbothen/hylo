---
document_type: assumption-register
level: L3
version: "1.2.0"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:38:15Z
phase: 1a
inputs: [prd.md]
input-hash: "c2ae96e"
traces_to: prd.md
---

# Assumptions Register: hylo P1

> Minted 2026-11-17 per owner ruling OD-152 (consistency audit CA-04). One ASM-NNN row
> per operating assumption formerly held in prd.md §9 prose; Status, Validation Method
> and Impact populated per the de facto mapping in consistency-audit-2026-11-17.md §10.1.
> The companion R-NNN risk register is minted in `prd-supplements/risk-register.md` (R-001..R-008).

| ASM ID | Assumption | Status | Validation Method | Impact | Traced To |
|--------|-----------|--------|-------------------|--------|-----------|
| ASM-001 | CPython 3.11.7 with a strict UTF-8 locale is the parity oracle (OD-104); all nine stage-2 writer groups re-ran their expected outputs against it on 2026-11-15. Pin scope (ADV-P3-A19): 3.11.7 governs the local oracle facts and vector pins; CI installs 3.11.x (setup-python resolves the latest patch, OD-104/ARCH-08). Edge cases reasoned out rather than run are not in vector tables. | validated | Writer-group oracle re-runs (2026-11-15): expected outputs regenerated from the pinned interpreter and pinned in vector tables. | HIGH | All vector-table BCs; ASM-001 gate in consistency-audit-2026-11-17.md §10.1 |
| ASM-002 | Claude Code 2.1.325 was the tested statusLine surface at mint time; the installed client is now 2.1.326 (BC-1.07.001), and the `subagentStatusLine` payload compatibility for it is tracked separately as ASM-007 (ASSUMP-107-1), not re-asserted here. The main stdin field list is unchanged since 2026-11-14 and the newer optional fields are tolerated absent (market-intel §5/§6.1). | validated | Market-intel §5/§6.1 surface survey; field-list diff against 2026-11-14 captures. | HIGH | BC-1.01.002 |
| ASM-002 | Claude Code 2.1.325 is the tested statusLine surface; the stdin field list is unchanged since 2026-11-14 and the newer optional fields are tolerated absent (market-intel §5/§6.1). | validated | Market-intel §5/§6.1 surface survey; field-list diff against 2026-11-14 captures. | HIGH | BC-1.01.002 |
| ASM-003 | The harness translates legacy `DGX_SL_*`/`LOCAL_MODEL_PREFIXES` to typed `HYLO_*` per case (OD-05); stdout parity is unaffected by the typed-bool grammar difference. | validated | Per-case translation table review against OD-05; typed-bool grammar pinned in BC-1.02.005 EC-011. | MEDIUM | BC-1.02.005 |
| ASM-004 | The p95 <= 25 ms render-latency target binds on the owner's Mac (darwin/arm64) only; CI legs report timings without gating (OD-117). | validated | Timing methodology review (BC-6.04.002); OD-117 ruling scope check; VP-036 measurement plan. | MEDIUM | BC-6.04.002, NFR-001, VP-036 |
| ASM-005 | Windows edge cases (BC-1.06.001 EC-008, BC-1.06.002 EC-003/EC-005) and the sitecustomize shim on CPython 3.11 (observed on 3.9.6) are marked "not executed" and pinned on the windows-2025 CI leg / harness canary. | open (disclosed) | Deferred to the windows-2025 CI leg and harness canary; re-check at first three-OS CI run (VP-037). | HIGH | BC-1.06.001/.002, BC-6.01.003, VP-037 |
| ASM-006 | OD-56 replaces the per-socket timeout with a total fetch deadline; output-identical on the corpus. | validated | Corpus replay equivalence check against the OD-56 ruling (BC-1.04.001). | MEDIUM | BC-1.04.001 |
| ASM-007 | The `--subagent` / custom agent-panel surface is portable in P1 behind a config off switch (OD-155, superseding OD-14); compatibility with the Claude Code 2.1.326 `subagentStatusLine` stdin payload (vs the 2.1.322 contract legacy parsed) is assumed (ASSUMP-107-1, BC-1.07.001/.002 PC-2). | open (disclosed) | Compatibility to be verified by a capture before Phase 3 (ASSUMP-107-1); argv surface and agent-panel row behavior per owner ruling OD-155 (2026-11-17). | MEDIUM | BC-1.07.001..008, BC-4.01.002 |

## Gate Notes

- HIGH-impact ASMs: ASM-001, ASM-002, ASM-005. The unvalidated ASMs are ASM-005 and
  ASM-007; their validation vehicles (windows-2025 CI leg / harness canary; a stdin
  capture before Phase 3) are disclosed, matching the audit's "deferred to Phase 3 by
  disclosure" disposition.
- Story-level `assumption_validations` traces are a Phase 2 artifact (no stories exist).
