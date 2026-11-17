---
document_type: risk-register
level: L3
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-17T16:00:00Z
phase: 1b
inputs: [architecture-feasibility-report.md, prd.md, prd-supplements/nfr-catalog.md, architecture/ARCH-INDEX.md, verification-properties/VP-INDEX.md]
input-hash: "a18a43b"
traces_to: prd.md
---

# Risk Register: hylo P1

> Minted 2026-11-17 per owner ruling OD-152 (consistency audit CA-04, part 2; all-findings
> fix burst per OD-154). One R-NNN row per risk formerly held prose-only in the
> feasibility report's "Risks and Mitigations" table (R-001..R-005, same order), plus the
> two PRD-carried risks closed by spec decision (R-006, R-007; prd.md §10). Impact per the
> de facto mapping in consistency-audit-2026-11-17.md §10.2. Companion of
> prd-supplements/assumptions-register.md (ASM-001..006).

| R ID | Risk | Category | Status | Impact | Mitigation | NFR Link | ARCH / ADR Anchor |
|------|------|----------|--------|--------|------------|----------|-------------------|
| R-001 | Python/Go cache-swap byte divergence across the four caches | Correctness (parity) | open | HIGH | Byte-exact writers over ordered `pyfmt.Value`; Tier B goldens + four-cache swap tier (VP-019); failed-replace semantics pinned by the AD-03 overlay decision | NFR-003 | ARCH-04 / AD-08 (byte-exact writers, atomic write + Windows retry + temp cleanup); swap tier exercised in ARCH-07 |
| R-002 | p95 <= 25 ms render-latency miss on the owner's Mac | Performance | open | MEDIUM | Legacy baseline measured (median 84.5 ms, 2026-11-15); hot-path allocation discipline; per-OS timing report; gate binds only where OD-117 says | NFR-001 | ARCH-08 timing gate (binds only with `HYLO_TIMING_GATE=1`); VP-036 |
| R-003 | Windows-only edge cases marked "not executed" (BC-1.06.001 EC-008, BC-1.06.002 EC-003/EC-005; sitecustomize shim) | Portability | open (disclosed) | MEDIUM | Pinned on the windows-2025 CI leg and the harness canary (ASM-005); disclosed, not hidden | NFR-004 | ARCH-08 3-OS CI matrix (AD-11); VP-037 |
| R-004 | Fake-pass parity: harness weaker than refereed | Verification integrity | open | HIGH | AD-09 fail-closed machinery, canary (BC-6.01.003), exclusion-closure property test (VP-012); HIGH kill-rate tier | n.a. | ARCH-07 / AD-09 |
| R-005 | Purity-annotation drift across BC files | Documentation consistency | closed (remediated) | LOW | Per-BC Purity Classification sections annotated during Pass 3 — 145/145 on disk (re-verified 2026-11-17, CA-07); module-level boundary carried in the ARCH-00 purity table | n.a. | ARCH-00 purity table |
| R-006 | RK-5: HYLO_TEST_NOW stderr warning leaking outside the harness | Operational (determinism) | closed (spec decision) | LOW | Env seam set: HYLO_TEST_NOW is a harness hook, not a setting (AD-10); reserved names are never warned as unknown keys (BC-2.01.001 invariant 6) | n.a. | ARCH-03 / AD-10 |
| R-007 | RK-6: inert key `statusline.window_age.ps_timeout_s` confusing the config surface | Operational (config surface) | closed (owner ruling) | LOW | Key removed from the registry by OD-147 (owner, 2026-11-16); setting it is now an ordinary unknown-key config error | n.a. | ARCH-02 key registry (OD-147) |

## Gate Notes

- HIGH-impact risks: R-001, R-004. Both carry an architecture mitigation (ARCH-04 / AD-08
  and ARCH-07 / AD-09 respectively), matching the audit's 2/2 substance pass
  (consistency-audit-2026-11-17.md §10.3).
- No security-category risks identified (vacuous pass, audit §10.3).
- Open NFR candidates with no matching NFR: none. R-001, R-002 and R-003 link to existing
  NFR-003 / NFR-001 / NFR-004; R-004, R-005, R-006 and R-007 are not NFR candidates —
  their mitigations are verification machinery, documentation, and spec decisions, not
  missing non-functional targets.
- Holdout scenarios are a Phase 2 artifact; HIGH/HIGH holdout coverage is n/a until
  stories exist.
