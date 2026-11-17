# Burst log — phase-1-spec-crystallization (active cycle)

Burst narratives for this cycle, in chronological order.

## Burst: resume housekeeping — status in_progress, cycle directory created retroactively, STATE.md compacted (2026-11-17)

**Parent-commit:** 479a14d (factory(pause): Phase 1 — CI/CD done, next consistency audit (session wrap))

**Adversary verdict:** no adversary pass dispatched this burst (housekeeping only; the phase-1d adversarial spec review has not started — Phase 0 passes converged 0:3 1:3 2:9 3:8 4:7 5:5, round record in `cycles/phase-0-ingestion/convergence-trajectory.md`).

**Codifications:** check-state-health warnings resolved — `status: draft` → `in_progress`; `current_cycle` moved phase-0-ingestion → phase-1-spec-crystallization with this directory created retroactively; STATE.md compacted (221 lines → target <200, ~150). The Project Metadata "Last Updated" narrative for the phase-1 sessions 2026-11-15..17 is preserved below, per the move-never-delete rule, and pointed to from STATE.md.

**Files touched (Dim-1): 9 unique files**

- .factory/STATE.md
- .factory/cycles/phase-1-spec-crystallization/cycle-manifest.md
- .factory/cycles/phase-1-spec-crystallization/burst-log.md
- .factory/cycles/phase-1-spec-crystallization/session-checkpoints.md
- .factory/cycles/phase-1-spec-crystallization/lessons.md
- .factory/cycles/phase-1-spec-crystallization/convergence-trajectory.md
- .factory/cycles/phase-0-ingestion/convergence-trajectory.md
- .factory/cycles/phase-0-ingestion/burst-log.md
- .factory/sidecar-learning.md (hook-appended session-end markers, committed with the burst)

**Dim-2 Attestation:** artifact counts verified on disk this burst: 145 BC files under `specs/behavioral-contracts/ss-01..ss-06`; 37 VP files (+ VP-INDEX) under `specs/verification-properties/`; 10 ARCH sections (+ ARCH-INDEX) under `specs/architecture/`. Owner-ruling ranges cited from the log (`specs/owner-decisions-log-2026-11-14.md`), next free OD-152.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown state/bookkeeping files only).

**Dim-6 Attestation:** N/A — no schema-structured file edited; policies.yaml untouched this burst.

**Dim-7 Attestation:** N/A — no repo test suite in scope (markdown state/bookkeeping files only).

**Closes:** the three check-state-health warnings actionable by housekeeping (status: draft, missing Phase 1 cycle directory, STATE.md 200+ lines). Still open: CLAUDE_AUTOCOMPACT_PCT_OVERRIDE advisory (handled separately from this burst), phase-1-consistency-audit NEXT.

---

### Session record 2026-11-15..17 (extracted from STATE.md Project Metadata "Last Updated" on 2026-11-17)

2026-11-16 — phase-1-cicd-setup DONE: PR #1 (ci/phase-1-setup @ d88e5ea) merged with admin override (squash) by owner instruction; squash commit rewritten with the GitHub no-reply identity; main force-pushed 570a0fc -> fd031da (same tree and parent; owner ran the push); branch protection live per OD-150 (lint, test x3, gitleaks full history; strict; enforce_admins false; force-push/deletion blocked); OD-151 recorded. Prior burst — parallel Phase 1 steps DONE: architect-feasibility-review (`specs/architecture-feasibility-report.md`, verdict 'PRD CHANGES REQUIRED: none' — prd-revision closed as a no-op); phase-1-dtu-assessment (`specs/dtu-assessment.md`, DTU_REQUIRED false — seam fakes, no Docker clones); phase-1-gene-transfusion-assessment (`specs/gene-transfusion-assessment.md` — statusline + cost gene-transfusion, pyfmt/config/platform hybrid, cmd/hylo + parity fresh). Follow-ups done: purity classification added to the 55 BCs that lacked it (145/145); ARCH-INDEX VP-022 bucket corrected to ARCH-04/09. PHASE-1-CICD-SETUP DONE 2026-11-16: PR #1 (ci/phase-1-setup, workflows @ d88e5ea) merged with admin override (squash) by owner instruction (OD-151); GitHub's squash commit carried the owner's personal email as author — rewritten with the GitHub no-reply identity, main force-pushed 570a0fc -> fd031da (same tree and parent; owner ran the push); branch protection live per OD-150 (lint, test ubuntu-24.04, test macos-15, test windows-2025, gitleaks full history; strict; enforce_admins false; force-push/deletion blocked); CI green on 3 OSes. Three [process-gap] lessons recorded (Drift Items, target before Phase 3). Then: phase-1-consistency-audit. Prior burst — backup-create-architecture DONE: `specs/architecture/` ARCH-00..09 (10 sections, 13 ADRs) + ARCH-INDEX + BC-COMPONENT-MAP; 37 VPs in `specs/verification-properties/` covering 145/145 BCs; BC anchor back-fill; owner rulings OD-146..OD-149. Earlier bursts: backup-create-prd DONE (145 BCs under `behavioral-contracts/ss-01..ss-06`: S1 93, S2 13, S3 3, S4 3, S5 19, S6 14; 101 legacy-mapped + 44 new; BC-INDEX + 5 supplements; rulings OD-132..OD-145); create-domain-spec DONE (`specs/domain-spec/`, product-level L2 per OD-115); create-brief DONE (`specs/product-brief.md`, OD-115..117); semport-translation DONE (design + assessment PASSED; OD-107..114); trajectory-tail →0→0→0→0

---

## Burst: consistency-audit fix burst — CA-01..CA-12 fixed, ASM/R registers minted, OD-152..154 recorded (2026-11-17)

**Parent-commit:** 4004444 (factory(state): resume housekeeping — status in_progress, phase-1 cycle dir, compact STATE.md)

**Adversary verdict:** no adversary pass dispatched this burst (remediation of the consistency-audit findings CA-01..CA-12; the phase-1d adversarial spec review has not started — Phase 0 passes converged 0:3 1:3 2:9 3:8 4:7 5:5, round record in `cycles/phase-0-ingestion/convergence-trajectory.md`).

**Audit outcome:** phase-1-consistency-audit DONE — report `cycles/phase-1-spec-crystallization/consistency-audit-2026-11-17.md`; verdict PASS-WITH-FINDINGS, 0 CRITICAL / 0 HIGH / 4 MEDIUM / 8 LOW (CA-01..CA-12); all 12 findings fixed this burst per OD-154.

**Codifications:** owner rulings OD-152..OD-154 recorded 2026-11-17, ruled "adopt" — OD-152 (CA-04): mint an ASM/R register pair instead of waiving the gate criteria (`specs/prd-supplements/assumptions-register.md` ASM-001..006; `specs/prd-supplements/risk-register.md` R-001..007); OD-153 (CA-03): the 14 S6 parity-harness BCs keep capability CAP-009 with a stated rationale (verification machinery proving CAP-009 byte parity; governed by DI-012); no new L2 capability added; OD-154: fix all remaining consistency-audit findings in one burst before phase-1-gate. Next free OD-155.

**Input-hash recomputation (placeholder "0000000" files only; no blanket --scan --update):** 147 placeholder files identified (145 BC files + the two new registers). Updated 2/147: `specs/prd-supplements/assumptions-register.md` (669ab0f) and `specs/prd-supplements/risk-register.md` (a18a43b), both --check clean. The 145 BC files report MISSING inputs — left as-is. Cause (uniform): their frontmatter `inputs:` reference siblings in traversal form (`../semport/hylo-legacy/...`, `../../semport/...`, `../domain-spec/...`, `../owner-decisions-log-2026-11-14.md`, `../../docs/PLAN.md`, `../../../docs/RESUME.md`, `../../CLAUDE.md`), and compute-input-hash deliberately rejects '..' path components (CWE-22 guard; "legitimate factory inputs never use '..' components") before any resolution attempt, so no hash can be computed for any of them. Affected: all 145 BC files under `specs/behavioral-contracts/ss-01..ss-06` (ss-01: 93, ss-02: 13, ss-03: 3, ss-04: 3, ss-05: 19, ss-06: 14). A future spec-steward burst may normalize those inputs to search-base form (e.g. `semport/hylo-legacy/...`, `owner-decisions-log-2026-11-14.md`) to make them resolvable; content untouched this burst (state-manager mandate).

**Eviction note (keep-last-5):** step row 16 (create-prd DONE, rulings OD-132..145, input-hash re-stamp note) evicted from STATE.md Current Phase Steps on appending row 21; content preserved below in the extracted session record ("backup-create-prd DONE ...") per the move-never-delete rule.

**Files touched (Dim-1): 27 unique files**

- .factory/STATE.md
- .factory/sidecar-learning.md
- .factory/specs/owner-decisions-log-2026-11-14.md
- .factory/specs/prd-supplements/assumptions-register.md (new, OD-152)
- .factory/specs/prd-supplements/risk-register.md (new, OD-152)
- .factory/cycles/phase-1-spec-crystallization/consistency-audit-2026-11-17.md (new, audit report)
- .factory/cycles/phase-1-spec-crystallization/burst-log.md
- .factory/specs/architecture-feasibility-report.md
- .factory/specs/architecture/ARCH-INDEX.md
- .factory/specs/behavioral-contracts/BC-ALLOCATION.md
- .factory/specs/behavioral-contracts/ss-04/BC-4.01.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.01.001.md .. BC-6.01.003.md (3)
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.001.md .. BC-6.02.004.md (4)
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.001.md .. BC-6.03.004.md (4)
- .factory/specs/behavioral-contracts/ss-06/BC-6.04.001.md .. BC-6.04.003.md (3)
- .factory/specs/prd-supplements/module-criticality.md
- .factory/specs/prd.md
- .factory/specs/verification-properties/VP-INDEX.md

**Dim-2 Attestation:** artifact counts verified on disk this burst: 145 BC files under `specs/behavioral-contracts/ss-01..ss-06` (placeholder-hash census 147 = 145 BC + 2 registers); 37 VP files (+ VP-INDEX); 10 ARCH sections (+ ARCH-INDEX); 2 new registers under `specs/prd-supplements/`. Owner-ruling ranges cited from the log (`specs/owner-decisions-log-2026-11-14.md`), next free OD-155.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown state/bookkeeping files only).

**Dim-6 Attestation:** N/A — no schema-structured file edited; policies.yaml untouched this burst.

**Dim-7 Attestation:** N/A — no repo test suite in scope (markdown state/bookkeeping files only).

**Closes:** all 12 consistency-audit findings CA-01..CA-12 (OD-154). Still open: fresh re-check of changed files, then phase-1-gate; the 145-BC input-hash normalization (spec-steward, optional follow-up); CLAUDE_AUTOCOMPACT_PCT_OVERRIDE advisory.

---

## Burst: BC input-hash normalization (CA-09 closed), re-check PASS, CR-01..03 fixed, phase-1-gate PASSED (2026-11-17)

**Parent-commit:** 6b67d35 (factory(phase-1): consistency audit + fixes CA-01..12, ASM/R registers, OD-152..154)

**Adversary verdict:** no adversary pass dispatched this burst (consistency re-check + gate bookkeeping; the phase-1d adversarial spec review is NEXT — Phase 0 passes converged 0:3 1:3 2:9 3:8 4:7 5:5, round record in `cycles/phase-0-ingestion/convergence-trajectory.md`).

**Codifications:** no new owner rulings this burst (OD-152..154 remain the latest; next free OD-155 — log: `specs/owner-decisions-log-2026-11-14.md`).

**Re-check outcome:** fresh re-check of the changed files PASS — report `cycles/phase-1-spec-crystallization/consistency-recheck-2026-11-17.md`. CA-01..CA-12 resolved; CR-01 fixed (`specs/prd.md`), CR-02 fixed (`specs/prd-supplements/assumptions-register.md`), CR-03 fixed (`specs/architecture/ARCH-INDEX.md`); CR-04 = 69 dependent artifacts hash-stale — deferred to the check-input-drift step before the owner gate; dependent-artifact hashes deliberately NOT updated this burst (do-not-update directive).

**Gate outcome:** phase-1-gate PASSED 2026-11-17 (orchestrator evaluation): all criteria met. P1-scoped capabilities CAP-009/010/011/015 covered by BCs; the other 14 capabilities deferred to P2-P6 per OD-115/OD-131; module criticality at `specs/prd-supplements/module-criticality.md` (path note, not a failure); design-system and heuristic-evaluation criteria N/A (OD-100, feature_type = cli); ASM-001..006 + R-001..007 registers present; branch protection verified via GitHub API (5 required checks, strict). Next step: phase-1d-adversarial-spec-review.

**Input-hash normalization (CA-09 closed):** all 145 BC files under `specs/behavioral-contracts/ss-01..ss-06` (ss-01: 93, ss-02: 13, ss-03: 3, ss-04: 3, ss-05: 19, ss-06: 14): frontmatter `inputs:` normalized from '..'-traversal form to repo-relative search-base form (resolvable by compute-input-hash; no '..' components per its CWE-22 guard) and the MISSING placeholders replaced with real input-hashes. BC content untouched (state-manager mandate: input-path frontmatter only).

**Eviction note (keep-last-5):** step rows 17 (create-architecture DONE) and 18 (parallel Phase 1 steps DONE) evicted from STATE.md Current Phase Steps on appending rows 22-23; both preserved in the extracted session record above ("backup-create-architecture DONE ...", "parallel Phase 1 steps DONE ...") per the move-never-delete rule.

**Files touched (Dim-1): 152 unique files**

- .factory/STATE.md
- .factory/sidecar-learning.md
- .factory/specs/prd.md (CR-01 fix)
- .factory/specs/prd-supplements/assumptions-register.md (CR-02 fix)
- .factory/specs/architecture/ARCH-INDEX.md (CR-03 fix)
- .factory/cycles/phase-1-spec-crystallization/consistency-recheck-2026-11-17.md (new, re-check report)
- .factory/cycles/phase-1-spec-crystallization/burst-log.md (this entry)
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.008.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.009.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.010.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.008.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.009.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.010.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.011.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.012.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.013.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.014.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.015.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.016.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.017.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.018.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.019.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.020.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.021.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.022.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.023.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.024.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.025.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.026.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.027.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.028.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.029.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.030.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.008.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.009.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.010.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.011.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.012.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.013.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.014.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.015.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.016.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.017.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.018.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.019.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.020.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.021.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.008.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.009.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.010.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.011.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.012.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.013.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.014.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.015.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.016.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.017.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.018.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.019.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.020.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.021.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.008.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.009.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.06.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.06.002.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.001.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.002.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.003.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.004.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.005.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.02.001.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.02.002.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.02.003.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.02.004.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.02.005.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.02.006.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.03.001.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.03.002.md
- .factory/specs/behavioral-contracts/ss-03/BC-3.01.001.md
- .factory/specs/behavioral-contracts/ss-03/BC-3.02.001.md
- .factory/specs/behavioral-contracts/ss-03/BC-3.02.002.md
- .factory/specs/behavioral-contracts/ss-04/BC-4.01.001.md
- .factory/specs/behavioral-contracts/ss-04/BC-4.01.002.md
- .factory/specs/behavioral-contracts/ss-04/BC-4.01.003.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.001.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.002.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.003.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.004.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.005.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.006.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.001.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.002.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.003.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.004.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.005.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.006.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.03.001.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.03.002.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.03.003.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.03.004.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.04.001.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.04.002.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.04.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.01.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.01.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.01.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.004.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.004.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.04.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.04.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.04.003.md

**Dim-2 Attestation:** artifact counts verified on disk this burst: 145 BC files under `specs/behavioral-contracts/ss-01..ss-06`; 37 VP files (+ VP-INDEX); 10 ARCH sections (+ ARCH-INDEX); registers ASM-001..006 + R-001..007 present under `specs/prd-supplements/`.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown state/bookkeeping files only).

**Dim-6 Attestation:** N/A — no schema-structured file edited; policies.yaml untouched this burst.

**Dim-7 Attestation:** N/A — no repo test suite in scope (markdown state/bookkeeping files only).

**Closes:** CA-09 (input-hash placeholders), CR-01..CR-03, the re-check step, and phase-1-gate (PASSED 2026-11-17). Still open: phase-1d-adversarial-spec-review NEXT; CR-04 dependent-artifact hash staleness (check-input-drift, pre-owner-gate); CLAUDE_AUTOCOMPACT_PCT_OVERRIDE advisory.

## Burst: ADV pass-1 remediation — ~115/129 findings fixed, VP-038 minted, sync check SC-01..07 fixed (2026-11-17)

**Scope.** Remediation of ADV pass 1 (129 findings: 21 HIGH / 63 MEDIUM / 40 LOW / 5 COSMETIC; reports `adversarial-reviews/pass-1.md` + `ADV-P1-INDEX.md`). Executed by business-analyst and product-owner (4 parallel sub-bursts + 4 follow-ups) and architect (2 parallel sub-bursts + 3 follow-ups). ~115 of 129 findings fixed across domain-spec, prd.md, product-brief.md, prd-supplements, behavioral contracts ss-01..ss-06 (+ BC-INDEX, BC-ALLOCATION), architecture, verification properties, and the cicd-setup / dtu / gene-transfusion / feasibility documents. Four findings held as owner questions (below); verdict remains NOT_CONVERGED until pass 2.

**Oracle re-run.** ~45 Python-result vector cells re-run on CPython 3.11.7; 8 were wrong and were corrected. Transcript JSON depth limits re-measured: 989/990.

**Held as owner questions (not yet ruled; next free OD remains OD-155).** (1) OverflowError exception-class treatment — C01, B05, B06. (2) ±Inf handling vs OD-130 — A2-01 and the OD-130 claim in VP-030. (3) Coverage-vs-mutation 95% gate — A08. (4) Windows file encoding — B08, C06.

**Sync check (step 4b).** `sync-check-adv-p1-2026-11-17.md` ran against baseline 6fa2b38 (~180 changed files): initial verdict FAIL with 7 findings SC-01..07; all seven were fixed in the working tree after the check. Orchestrator re-verification: no stale depth wording anywhere in the corpus; VP<->BC citations bijective, 38 VPs x 145 BCs (VP-038 minted this burst).

**Dim-2 Attestation:** artifact counts per the orchestrator re-verification this burst: 145 BC files under `specs/behavioral-contracts/ss-01..ss-06`; 38 VP files (+ VP-INDEX); 10 ARCH sections (+ ARCH-INDEX); ASM/R registers under `specs/prd-supplements/`.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown state/bookkeeping files only).

**Dim-6 Attestation:** N/A — no schema-structured file edited; policies.yaml untouched this burst.

**Dim-7 Attestation:** N/A — no repo test suite in scope (markdown state/bookkeeping files only).

**Next:** ADV pass 2 (fresh-context perimeters; >=3 clean passes to convergence). Four owner questions above remain open pending rulings.
