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
- .factory/cycles/phase-1-spec-crystallization/burst-log.md
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

## Burst: ADV pass-2 remediation — rulings OD-155..165 applied, --subagent BCs, VP-039/040, sync check SC-01..09 fixed (2026-11-17)

**Scope.** Remediation of ADV pass 2 (116 findings: 17 HIGH / 58 MEDIUM / 35 LOW / 6 COSMETIC; reports `adversarial-reviews/pass-2.md` + `ADV-P2-INDEX.md`). Executed by the business-analyst, product-owner (7 sub-bursts, including 8 new behavioral contracts BC-1.07.001..008 for `--subagent` per OD-155) and architect (6 sub-bursts, including the VP-INDEX rebuild). Fixed across domain-spec, product-brief, prd.md, prd-supplements, behavioral contracts, architecture, verification properties (VP-039 and VP-040 minted; VP-INDEX rebuilt), and the cicd / dtu / gene-transfusion / feasibility documents. Rulings OD-155..OD-165 applied throughout; new owner rulings OD-160..OD-165 recorded (owner chose the recommended option each time); the closed exclusion set now holds 10 ids (D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161).

**JSON depth limits, measured end to end.** The orchestrator re-measured the limits on the real legacy program with an isolated HOME (three sites measured directly, the rest derived): limit = 999 − Python frames to `raw_decode`; stdin and transcript 993/994, session/mix cache 991/992, git cache and cost history 990/991. This superseded conflicting wrapper-probe figures (989/990) reported during remediation.

**Counts.** Contract count 145 → 153 (8 new `--subagent` BCs); VP count 38 → 40 (VP-039, VP-040).

**Sync check (step 4b).** `sync-check-adv-p2-2026-11-18.md`: initial verdict FAIL with 9 findings SC-01..09; all nine were fixed in the working tree after the check. Orchestrator re-verification: VP `bcs` fields ↔ BC citations consistent (3 prose-only mentions), no live 989 depth value anywhere in the corpus, no stray characters, no Rust vocabulary.

**Dim-2 Attestation:** artifact counts verified on disk this burst: 153 BC files under `specs/behavioral-contracts/ss-01..ss-06`; 40 VP files (+ rebuilt VP-INDEX); 10 ARCH sections (+ ARCH-INDEX); ASM/R registers under `specs/prd-supplements/`.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown state/bookkeeping files only).

**Dim-6 Attestation:** N/A — no schema-structured file edited; policies.yaml untouched this burst.

**Dim-7 Attestation:** N/A — no repo test suite in scope (markdown state/bookkeeping files only).

**Next:** ADV pass 3 (fresh-context perimeters; >=3 clean passes to convergence).

## Burst: ADV pass-3 remediation — rulings OD-166..168 applied, BC-5.01.007, ARCH-03 anchors, VP-INDEX rebuilt, sync check PASS (2026-11-18)

**Parent-commit:** 9122069 (factory(phase-1d): adversarial pass 3 (150 findings, regression analysed))

**Adversary verdict:** pass 3 recorded 2026-11-18: NOT_CONVERGED, 150 findings (36H/61M/48L/5C), Δ +34 REGRESSION vs pass 2, root-caused (pass-2 remediation added new scope without pre-validation), novelty MEDIUM; this burst remediates all 150 findings; next: ADV pass 4.

**Codifications:** owner rulings OD-166..OD-168 recorded 2026-11-18 (owner chose the recommended option each time; next free OD-169 — log: `specs/owner-decisions-log-2026-11-14.md`); four [process-gap] lessons codified L-PG-09..12 in `cycles/phase-1-spec-crystallization/lessons.md` (each with a D-448(b) Closes cite) and recorded as Drift Items in STATE.md (target before Phase 2).

**Scope.** Remediation of ADV pass 3 (150 findings: 36 HIGH / 61 MEDIUM / 48 LOW / 5 COSMETIC; reports `adversarial-reviews/pass-3.md` + `ADV-P3-INDEX.md`). Executed by the business-analyst, product-owner (7 sub-bursts, including the new BC-5.01.007 mixed int/float Num semantics) and architect (4 sub-bursts, including the VP-INDEX rebuild). Fixed across domain-spec, product-brief, prd.md, prd-supplements, behavioral contracts, architecture (12 stable ARCH-03 anchors, the `--subagent` entry point, the harness argv field), verification properties (VP-INDEX rebuilt) and the cicd / dtu / gene-transfusion / feasibility documents. Owner rulings OD-166..OD-168 recorded (owner chose the recommended option each time); new crash ids minted by the orchestrator: CP-O10, CP-O11 (cost segment), CP-A04, CP-A05 (subagent tokens/clock). One business-analyst agent broke down with garbled output and zero tool calls — nothing was written; the sub-burst was re-dispatched and verified on disk.

**Counts.** Contract count 153 → 154 (BC-5.01.007; S5 = 20); VP count 40 (VP-INDEX rebuilt: 40 VPs, 154 BCs, no one-sided links).

**Sync check (step 4b).** `sync-check-adv-p3-2026-11-18.md`: verdict PASS with 4 warnings; all four were fixed in the working tree after the check. Orchestrator re-verification (python scripts): 154 BC titles consistent across BC files, BC-INDEX and PRD; VP↔BC links consistent (3 prose-only mentions); no live 989 depth value; no CP-T08; non-English text only as CJK test data in the width/Unicode vectors.

**Dim-2 Attestation:** artifact counts verified on disk this burst: 154 BC files under `specs/behavioral-contracts/ss-01..ss-06`; 40 VP files (+ rebuilt VP-INDEX); 10 ARCH sections (+ ARCH-INDEX); ASM/R registers under `specs/prd-supplements/`.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown state/bookkeeping files only).

**Dim-6 Attestation:** N/A — no schema-structured file edited; policies.yaml untouched this burst.

**Dim-7 Attestation:** N/A — no repo test suite in scope (markdown state/bookkeeping files only).

**Files touched (Dim-1): 148 unique files**

- .factory/cycles/phase-1-spec-crystallization/burst-log.md
- .factory/cycles/phase-1-spec-crystallization/lessons.md
- .factory/cycles/phase-1-spec-crystallization/sync-check-adv-p3-2026-11-18.md
- .factory/sidecar-learning.md
- .factory/specs/architecture-feasibility-report.md
- .factory/specs/architecture/ARCH-00-overview.md
- .factory/specs/architecture/ARCH-01-binary-cli.md
- .factory/specs/architecture/ARCH-03-statusline.md
- .factory/specs/architecture/ARCH-04-data-files.md
- .factory/specs/architecture/ARCH-05-platform.md
- .factory/specs/architecture/ARCH-06-pyfmt.md
- .factory/specs/architecture/ARCH-07-parity-harness.md
- .factory/specs/architecture/ARCH-08-build-ci-release.md
- .factory/specs/architecture/ARCH-INDEX.md
- .factory/specs/architecture/BC-COMPONENT-MAP.md
- .factory/specs/behavioral-contracts/BC-ALLOCATION.md
- .factory/specs/behavioral-contracts/BC-INDEX.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.008.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.009.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.013.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.014.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.017.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.019.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.022.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.024.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.025.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.026.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.027.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.030.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.010.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.015.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.018.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.013.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.015.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.008.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.06.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.008.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.001.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.004.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.005.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.02.001.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.02.006.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.03.001.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.03.002.md
- .factory/specs/behavioral-contracts/ss-03/BC-3.01.001.md
- .factory/specs/behavioral-contracts/ss-04/BC-4.01.002.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.001.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.003.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.004.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.006.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.007.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.001.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.002.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.003.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.004.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.005.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.006.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.04.001.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.04.002.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.04.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.01.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.01.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.004.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.004.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.04.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.04.003.md
- .factory/specs/cicd-setup.md
- .factory/specs/domain-spec/bounded-contexts.md
- .factory/specs/domain-spec/capabilities.md
- .factory/specs/domain-spec/invariants.md
- .factory/specs/domain-spec/owner-validation-list.md
- .factory/specs/domain-spec/state-machines.md
- .factory/specs/domain-spec/ubiquitous-language.md
- .factory/specs/dtu-assessment.md
- .factory/specs/gene-transfusion-assessment.md
- .factory/specs/owner-decisions-log-2026-11-14.md
- .factory/specs/prd-supplements/assumptions-register.md
- .factory/specs/prd-supplements/error-taxonomy.md
- .factory/specs/prd-supplements/interface-definitions.md
- .factory/specs/prd-supplements/module-criticality.md
- .factory/specs/prd-supplements/nfr-catalog.md
- .factory/specs/prd-supplements/risk-register.md
- .factory/specs/prd-supplements/test-vectors.md
- .factory/specs/prd.md
- .factory/specs/product-brief.md
- .factory/specs/verification-properties/VP-001-never-blank-exit0.md
- .factory/specs/verification-properties/VP-002-unknown-flag-one-line.md
- .factory/specs/verification-properties/VP-005-stdin-decode-totality.md
- .factory/specs/verification-properties/VP-006-json-depth-budgets.md
- .factory/specs/verification-properties/VP-009-tier-a-live-parity.md
- .factory/specs/verification-properties/VP-010-tier-b-committed-goldens.md
- .factory/specs/verification-properties/VP-012-exclusion-set-closure.md
- .factory/specs/verification-properties/VP-015-config-resolution-totality.md
- .factory/specs/verification-properties/VP-018-atomic-cache-writes.md
- .factory/specs/verification-properties/VP-019-four-cache-swap-parity.md
- .factory/specs/verification-properties/VP-021-cost-colour-goldens.md
- .factory/specs/verification-properties/VP-022-ledger-read-scope-absence.md
- .factory/specs/verification-properties/VP-023-pyfmt-num-equivalence.md
- .factory/specs/verification-properties/VP-024-pyfmt-json-equivalence.md
- .factory/specs/verification-properties/VP-026-pyfmt-time-equivalence.md
- .factory/specs/verification-properties/VP-028-row1-widget-tables.md
- .factory/specs/verification-properties/VP-029-transcript-parse-tables.md
- .factory/specs/verification-properties/VP-030-telemetry-row2-tables.md
- .factory/specs/verification-properties/VP-032-platform-dir-rules.md
- .factory/specs/verification-properties/VP-033-process-probe-correctness.md
- .factory/specs/verification-properties/VP-034-oracle-isolation.md
- .factory/specs/verification-properties/VP-035-corpus-hygiene.md
- .factory/specs/verification-properties/VP-036-render-latency-p95.md
- .factory/specs/verification-properties/VP-037-three-os-ci-matrix.md
- .factory/specs/verification-properties/VP-039-elapsed-clock-ulp-agreement.md
- .factory/specs/verification-properties/VP-040-frame-width-property-legs.md
- .factory/specs/verification-properties/VP-INDEX.md
- .factory/STATE.md

**Closes:** all 150 pass-3 findings remediated across perimeters A/A2/B/C/C2/D (reports `adversarial-reviews/pass-3.md` + `ADV-P3-INDEX.md`), sync check adv-p3 (verdict PASS, 4 warnings fixed), rulings OD-166..OD-168 recorded, lessons L-PG-09..12 codified. Still open: ADV pass 4 (>=3 clean passes to convergence); CR-04 dependent-artifact hash staleness (check-input-drift, pre-gate).

**Next:** ADV pass 4 (fresh-context perimeters; >=3 clean passes to convergence).

## Burst: ADV pass-4 recording + remediation — rulings OD-169..175 applied, VP-041 minted, crash register 47 paths, sync check PASS-WITH-FINDINGS (2026-11-17)

**Parent-commit:** 9c5dda3 (factory(phase-1d): pass-3 remediation, BC-5.01.007, rulings OD-166..168)

**Adversary verdict:** pass 4 recorded 2026-11-17: NOT_CONVERGED, 133 findings (39H/57M/32L/5C), Δ −17 vs pass 3 (150) but HIGH 36 → 39; many findings sibling-propagation — fixed facts re-flagged at sibling sites, not relapses; HIGH concentrated on the interface-definitions/registry closure (ADV-P4-A04/A05) and partial-fix propagation (ADV-P4-A2-03). Novelty pass-level MEDIUM-HIGH (A HIGH, A2 HIGH, B/C/C2/D MEDIUM). Reports `adversarial-reviews/pass-4.md` + `ADV-P4-INDEX.md` (133 rows cross-checked: A 19, A2 26, B 22, C 15, C2 17, D 34). This burst remediates all 133 findings; next: ADV pass 5.

**Codifications:** owner rulings OD-169..OD-175 recorded 2026-11-17 (owner chose the recommended option each time; next free OD-176 — log: `specs/owner-decisions-log-2026-11-14.md`). Highlights: OD-169 cost-history divergence gets its own closed-set exclusion id `OD-166` (closed set now 11 ids); OD-170 hylo carries its own Unicode 14.0 tables generated from CPython 3.11.7; OD-171 local zone resolved through internal/platform honouring TZ on every OS (VP-026 posix-only tag removed); OD-173 lane-pill words become config keys; OD-174 `cost.basis_min_shown_usd` renamed `statusline.cost.display_floor_usd`; OD-175 `statusline.queue.yellow` ratified as a P1 Bool key. Four [process-gap] lessons codified L-PG-13..16 in `cycles/phase-1-spec-crystallization/lessons.md` and recorded as Drift Items in STATE.md: L-PG-13 remediation-plan design calls checked against settled ODs before dispatch (plan call 10 first contradicted OD-148 — corrected post-burst); L-PG-14 hook scratch files untracked and gitignored (regression-state.json was tracked on the public branch with an absolute home path); L-PG-15 every claimed fix verified on disk (BC-1.07.002 vector row unwritten, VP-011 count recomputed wrongly — both caught by the residual sweeps); L-PG-16 injected instructions in a tool result recorded and the owner notified (pass-4 subagent sighting: credential/SSH/Wi-Fi collection instructions ignored, source unidentified).

**Scope.** Remediation of ADV pass 4 (133 findings; source `adversarial-reviews/pass-4.md`, canonical rulings and minted ids in `pass-4-remediation-plan.md`). Executed as 8 parallel fix agents + 2 residual sweeps + the OD-148 layout correction (plan call 10 as first drafted moved the parity corpus root to internal/parity/testdata/cases/, contradicting the settled OD-148 fixture layout — corrected post-burst: corpus root internal/statusline/testdata/parity/cases/, generic runner in ./internal/parity) + 2 sync-fix agents. Fixed across domain-spec, product-brief, prd.md, prd-supplements, behavioral contracts, architecture, verification properties and the cicd / dtu / gene-transfusion / feasibility documents. New crash id CP-N03; crash register now 47 paths including the foreign-cache CP-C family under OD-160. Residual sweeps verified claimed fixes on disk (L-PG-15). One subagent reported injected instructions in a shell tool result; it ignored them and the sighting was escalated to the owner (L-PG-16).

**Counts.** Contract count unchanged at 154 (S5 = 20); VP count 40 → 41 (VP-041 minted, row-1 property legs); crash register 47 paths.

**Sync check (post-burst).** `sync-check-adv-p4-2026-11-17.md`: verdict PASS-WITH-FINDINGS; all 8 findings (SC-05..SC-12) closed before this commit. 157 dirty files vs 9c5dda3 scanned; 239 spec .md files across 7 trees.

**Housekeeping.** `regression-state.json` (hook scratch that had captured an absolute home path) removed from tracking and added to `.factory/.gitignore`.

**Dim-2 Attestation:** artifact counts verified on disk this burst: 154 BC files under `specs/behavioral-contracts/ss-01..ss-06`; 41 VP files (+ VP-INDEX) under `specs/verification-properties/`; 10 ARCH sections (+ ARCH-INDEX) under `specs/architecture/`.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown state/bookkeeping files only).

**Dim-6 Attestation:** N/A — no schema-structured file edited; policies.yaml untouched this burst.

**Dim-7 Attestation:** N/A — no repo test suite in scope (markdown state/bookkeeping files only).

**Files touched (Dim-1): 163 unique paths** (regression-state.json removed from tracking; linkscan.tmp scratch left unstaged)

- .factory/.gitignore
- .factory/cycles/phase-1-spec-crystallization/adversarial-reviews/ADV-P4-INDEX.md
- .factory/cycles/phase-1-spec-crystallization/adversarial-reviews/pass-4.md
- .factory/cycles/phase-1-spec-crystallization/burst-log.md
- .factory/cycles/phase-1-spec-crystallization/convergence-trajectory.md
- .factory/cycles/phase-1-spec-crystallization/cycle-manifest.md
- .factory/cycles/phase-1-spec-crystallization/lessons.md
- .factory/cycles/phase-1-spec-crystallization/pass-4-remediation-plan.md
- .factory/cycles/phase-1-spec-crystallization/sync-check-adv-p4-2026-11-17.md
- .factory/regression-state.json
- .factory/sidecar-learning.md
- .factory/specs/architecture-feasibility-report.md
- .factory/specs/architecture/ARCH-00-overview.md
- .factory/specs/architecture/ARCH-01-binary-cli.md
- .factory/specs/architecture/ARCH-02-configuration.md
- .factory/specs/architecture/ARCH-03-statusline.md
- .factory/specs/architecture/ARCH-05-platform.md
- .factory/specs/architecture/ARCH-06-pyfmt.md
- .factory/specs/architecture/ARCH-07-parity-harness.md
- .factory/specs/architecture/ARCH-08-build-ci-release.md
- .factory/specs/architecture/ARCH-INDEX.md
- .factory/specs/architecture/BC-COMPONENT-MAP.md
- .factory/specs/behavioral-contracts/BC-ALLOCATION.md
- .factory/specs/behavioral-contracts/BC-INDEX.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.008.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.01.009.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.011.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.012.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.013.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.014.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.016.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.017.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.018.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.019.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.020.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.021.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.022.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.023.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.025.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.027.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.028.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.029.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.02.030.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.010.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.014.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.015.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.018.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.03.020.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.009.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.013.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.020.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.04.021.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.05.009.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.06.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.001.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.002.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.003.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.004.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.005.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.006.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.007.md
- .factory/specs/behavioral-contracts/ss-01/BC-1.07.008.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.001.md
- .factory/specs/behavioral-contracts/ss-02/BC-2.01.002.md
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
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.002.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.01.007.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.001.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.005.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.02.006.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.03.004.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.04.001.md
- .factory/specs/behavioral-contracts/ss-05/BC-5.04.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.01.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.01.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.01.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.02.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.003.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.03.004.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.04.001.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.04.002.md
- .factory/specs/behavioral-contracts/ss-06/BC-6.04.003.md
- .factory/specs/cicd-setup.md
- .factory/specs/domain-spec/bounded-contexts.md
- .factory/specs/domain-spec/capabilities.md
- .factory/specs/domain-spec/invariants.md
- .factory/specs/domain-spec/owner-validation-list.md
- .factory/specs/domain-spec/state-machines.md
- .factory/specs/domain-spec/ubiquitous-language.md
- .factory/specs/dtu-assessment.md
- .factory/specs/gene-transfusion-assessment.md
- .factory/specs/owner-decisions-log-2026-11-14.md
- .factory/specs/prd-supplements/assumptions-register.md
- .factory/specs/prd-supplements/error-taxonomy.md
- .factory/specs/prd-supplements/interface-definitions.md
- .factory/specs/prd-supplements/module-criticality.md
- .factory/specs/prd-supplements/nfr-catalog.md
- .factory/specs/prd-supplements/risk-register.md
- .factory/specs/prd-supplements/test-vectors.md
- .factory/specs/prd.md
- .factory/specs/product-brief.md
- .factory/specs/verification-properties/VP-001-never-blank-exit0.md
- .factory/specs/verification-properties/VP-002-unknown-flag-one-line.md
- .factory/specs/verification-properties/VP-003-cpx03-write-failure-exit0.md
- .factory/specs/verification-properties/VP-005-stdin-decode-totality.md
- .factory/specs/verification-properties/VP-006-json-depth-budgets.md
- .factory/specs/verification-properties/VP-007-render-determinism-seams.md
- .factory/specs/verification-properties/VP-009-tier-a-live-parity.md
- .factory/specs/verification-properties/VP-011-tier-c-differential-fuzz.md
- .factory/specs/verification-properties/VP-012-exclusion-set-closure.md
- .factory/specs/verification-properties/VP-013-d4ex2-wrong-shape-tables.md
- .factory/specs/verification-properties/VP-016-config-error-classes-line.md
- .factory/specs/verification-properties/VP-017-exactly-one-backend.md
- .factory/specs/verification-properties/VP-018-atomic-cache-writes.md
- .factory/specs/verification-properties/VP-020-cost-history-integrity.md
- .factory/specs/verification-properties/VP-021-cost-colour-goldens.md
- .factory/specs/verification-properties/VP-022-ledger-read-scope-absence.md
- .factory/specs/verification-properties/VP-023-pyfmt-num-equivalence.md
- .factory/specs/verification-properties/VP-026-pyfmt-time-equivalence.md
- .factory/specs/verification-properties/VP-028-row1-widget-tables.md
- .factory/specs/verification-properties/VP-029-transcript-parse-tables.md
- .factory/specs/verification-properties/VP-030-telemetry-row2-tables.md
- .factory/specs/verification-properties/VP-036-render-latency-p95.md
- .factory/specs/verification-properties/VP-039-elapsed-clock-ulp-agreement.md
- .factory/specs/verification-properties/VP-040-frame-width-property-legs.md
- .factory/specs/verification-properties/VP-041-row1-property-legs.md
- .factory/specs/verification-properties/VP-INDEX.md
- .factory/STATE.md

**Closes:** all 133 pass-4 findings remediated across perimeters A/A2/B/C/C2/D (reports `adversarial-reviews/pass-4.md` + `ADV-P4-INDEX.md`), sync check adv-p4 (verdict PASS-WITH-FINDINGS, SC-05..SC-12 closed), rulings OD-169..OD-175 recorded, lessons L-PG-13..16 codified. Still open: ADV pass 5 (>=3 clean passes to convergence); CR-04 dependent-artifact hash staleness (check-input-drift, pre-gate).

**Next:** ADV pass 5 (fresh-context perimeters; >=3 clean passes to convergence).

## Burst: ADV pass-5 recording + remediation — rulings OD-176..180 applied, seventh D4-EX-3 class Text, sync check PASS-WITH-FINDINGS (2026-11-18)

**Parent-commit:** f920d7f (factory(phase-1d): adversarial pass 4 + remediation, rulings OD-169..175, VP-041)

**Adversary verdict:** pass 5 recorded 2026-11-18: NOT_CONVERGED, 148 findings (24H/75M/43L/6C), Δ +15 vs pass 4 (133) while HIGH fell 39 → 24 — severity mass moved to MEDIUM (75); the first pass of the series where the total rose but HIGH fell sharply. Pass-level novelty MEDIUM. Reports `adversarial-reviews/pass-5.md` + `ADV-P5-INDEX.md` (148 rows; perimeters A 25, A2 36, B 16, C 17, C2 21, D 33). This burst also remediates all 148 findings; next: ADV pass 6.

**Codifications:** owner rulings OD-176..OD-180 recorded 2026-11-18 (owner chose the recommended option each time; next free OD-181 — log: `specs/owner-decisions-log-2026-11-14.md`). Highlights: OD-176 convergence keeps the full VSDD standard — every finding of every severity is fixed each pass and convergence needs three consecutive passes with only cosmetic findings; no severity gate, no scope freeze. OD-177 refines OD-171 to libc semantics on every OS (`TZ` unset → OS zone; `TZ` empty or unparseable → UTC). OD-178 mints a seventh D4-EX-3 class **Text** (composite-shape, pill-label, glyph and empty-text errors) with exact reason strings in the vocabulary and its own table test `TestD4EX3_Text` — canonical D4-EX-3 tests are now TestD4EX3_Boolean, _Enum, _URL, _Number, _Text. OD-179 ratifies the reroute-all markers as the List key `statusline.lane.reroute_all_prefixes` (default `["claude", "claude-"]`, legacy; every entry non-empty, no control bytes). OD-180: a metrics URL with userinfo reproduces legacy — no sample (the dead rung); no exclusion id. Three [process-gap] lessons codified L-PG-17..19 in `cycles/phase-1-spec-crystallization/lessons.md` and recorded as Drift Items in STATE.md: L-PG-17 agent briefs must name the oracle interpreter path (an agent ran the legacy oracle with /usr/bin/python3, macOS Python 3.9.6, not CPython 3.11.7; the re-run on 3.11.7 was identical); L-PG-18 one measurement per fact, one agent, end to end (two agents pinned conflicting encoder depth limits); L-PG-19 canonical lists are minted centrally before parallel dispatch (parallel agents minted divergent glyph registries).

**Scope.** Remediation of ADV pass 5 (148 findings; source `adversarial-reviews/pass-5.md`, canonical rulings and minted ids in `pass-5-remediation-plan.md`), executed across domain-spec, product-brief, prd.md, prd-supplements, behavioral contracts, architecture, verification properties and the cicd / dtu / gene-transfusion / feasibility documents.

**Counts.** Contract count unchanged at 154 (S5 = 20); VP count unchanged at 41; closed exclusion set unchanged at 11 ids; D4-EX-3 classes 6 → 7 (Text) with 5 canonical table tests.

**Sync check (post-burst).** `sync-check-adv-p5-2026-11-18.md`: verdict PASS-WITH-FINDINGS; all 8 findings (SC-13..SC-20) closed before this commit. 146 dirty files vs f920d7f scanned; 239 spec .md files across 7 trees.

**Dim-2 Attestation:** artifact counts verified on disk this burst: 154 BC files under `specs/behavioral-contracts/ss-01..ss-06`; 41 VP files (+ VP-INDEX) under `specs/verification-properties/`; 11 ARCH-*.md files under `specs/architecture/`.

**Next:** ADV pass 6 (fresh-context perimeters; >=3 clean passes to convergence); CR-04 dependent-artifact hash staleness (check-input-drift, pre-gate) remains open.

## Burst: ADV pass-6 recording + remediation — rulings OD-181..187 applied, closed exclusion set 12 ids, sync check PASS-WITH-FINDINGS (2026-11-18)

**Recording.** ADV pass 6 run 2026-11-18 over the full P1 spec package as the same six fresh-context perimeters (A/A2/B/C/C2/D), final messages extracted verbatim (`adversarial-reviews/pass-6.md`, indexed in `adversarial-reviews/ADV-P6-INDEX.md`, 124 rows cross-checked against the report). Totals: 124 findings — 27 HIGH / 52 MEDIUM / 38 LOW / 7 COSMETIC; Δ −24 vs pass 5 (148 → 124), the largest total drop of the series, though HIGH ticked up 24 → 27. Per-perimeter counts: A 19, A2 30, B 16, C 17, C2 15, D 27. Pass-level novelty MEDIUM. Row tags: 7 [owner-question], 2 [process-gap]. Verdict NOT_CONVERGED (per OD-176: three consecutive cosmetic-only passes required).

**Remediation.** Fixes executed per `pass-6-remediation-plan.md` (calls 1-16) across domain-spec, prd.md, prd-supplements, behavioral contracts, architecture, verification properties and the cicd/dtu/feasibility documents. Every agent's changes verified on disk by diff and a non-English scan regardless of the agent report (codified L-PG-20); one wrongly rejected pass-5 finding (ADV-P5-D16) overturned and applied (ADV-P6-D07; codified L-PG-21).

**Codifications.** Owner rulings OD-181..OD-187 recorded 2026-11-18 (owner chose the recommended option each time; next free OD-188 — log: `specs/owner-decisions-log-2026-11-14.md`). Highlights: OD-181 mints a new closed-set exclusion id "metrics transport beyond plain http" (non-http(s) redirect targets: no sample; TLS trust-store differences: OS trust store; parity cases use plain http only) — the closed exclusion set is now 12 ids (D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161, OD-166, OD-181). OD-182: VP Go blocks are non-normative illustrations labelled "Illustrative sketch (non-normative, not compiled; OD-182)"; normative VP content = property statement, oracle, method, inputs, pass/fail rule; sketch-only defects are cosmetic, a property only clear from its sketch is a HIGH defect against the statement. OD-183: OD-159 extends to stdio — hylo reads and writes UTF-8 on every OS; the Windows oracle gets exactly one extra variable `PYTHONIOENCODING=utf-8` (PYTHONUTF8 stays forbidden). OD-184: every `statusline.glyphs.*` / `statusline.subagent.glyphs.*` member is exactly 1 code point except `statusline.glyphs.sparkline` = exactly 8 ordered code points; the East-Asian-Width validation width applies only to the pill-label 1..16 bound. OD-185: OD-104 stands — CI installs Python 3.11.x, the exact-3.11.7 pin is withdrawn; the harness self-checks measured constants (depth boundaries, `unicodedata.unidata_version`) against the resolved oracle at start, failing closed on mismatch, and golden metadata records the resolved patch. OD-186: the temp-file exclusion is widened by ruling to cover the Windows sharing-violation rename-retry outcome; the retry delay becomes config key `statusline.cache.rename_retry_delay_ms` (Int, default 10, range 1..1000); the attempt count is stated once — three attempts in total (initial + 2 retries). OD-187: the VP-036 >512 KB timing-fixture exemption is conditional — it applies only when the fixture misses the 25 ms target and its use is reported. Three [process-gap] lessons codified L-PG-20..22 in `cycles/phase-1-spec-crystallization/lessons.md` and recorded as Drift Items in STATE.md: L-PG-20 every agent's changes are verified on disk by diff and a non-English scan regardless of its report (garbled or non-English reports; one agent made zero edits reporting nothing usable); L-PG-21 fix-agent rejections are verified on disk like fixes (a pass-5 agent wrongly rejected ADV-P5-D16, overturned by ADV-P6-D07); L-PG-22 VP Go sketches are non-normative per OD-182 (untypechecked sketches churned every pass).

**Counts.** Contract count unchanged at 154 (S5 = 20); VP count unchanged at 41; closed exclusion set 11 → 12 ids (OD-181); D4-EX-3 classes unchanged at 7 with 5 canonical table tests.

**Sync check (post-burst).** `sync-check-adv-p6-2026-11-18.md`: verdict PASS-WITH-FINDINGS; all 8 findings (SC-21..SC-28 — 3 Major / 4 Minor / 1 Cosmetic) closed before this commit (spot-verified on disk: VP-019/VP-012 `bcs:` reciprocity, ARCH-06 3-arg `FromISOFormat`, VP-009 TWELVE-id enumeration). 156 dirty files vs c26526e scanned; 239 spec .md files across 7 trees; interpreter `/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7, PyYAML 6.0.2).

**Dim-2 Attestation:** artifact counts verified on disk this burst: 154 BC files under `specs/behavioral-contracts/ss-01..ss-06`; 41 VP files (+ VP-INDEX) under `specs/verification-properties/`.

**Next:** ADV pass 7 (fresh-context perimeters; >=3 clean passes to convergence); CR-04 dependent-artifact hash staleness (check-input-drift, pre-gate) remains open.

## Burst: ADV pass-7 recording + remediation — rulings OD-188..192 applied, crash register 48 paths, sync check PASS-WITH-FINDINGS (2026-11-18)

**Recording.** ADV pass 7 run 2026-11-18 over the full P1 spec package as the same six fresh-context perimeters (A/A2/B/C/C2/D), final messages extracted verbatim (`adversarial-reviews/pass-7.md`, indexed in `adversarial-reviews/ADV-P7-INDEX.md`, 114 rows). Totals: 114 findings — 14 HIGH / 47 MEDIUM / 49 LOW / 4 COSMETIC; Δ −10 vs pass 6 (124 → 114), HIGH 27 → 14; perimeter A2 filed zero HIGH for the first time. Per-perimeter counts: A 22, A2 22, B 15, C 14, C2 14, D 27. Pass-level novelty MEDIUM. Row tags: 8 [owner-question], 0 [process-gap]. Verdict NOT_CONVERGED (per OD-176: three consecutive cosmetic-only passes required — 0 so far). Orchestrator spot-verified ADV-P7-A03, A2-08, B01, C02, C2-02 and D01 on disk and against CPython 3.11.7; all held.

**Remediation.** Fixes executed per `pass-7-remediation-plan.md` (calls 1-15) across domain-spec, prd.md, prd-supplements, behavioral contracts, architecture, verification properties and the assessment/cicd documents. Two pass-7 process lessons codified from the burst itself (L-PG-23/24): one fix agent broke down mid-burst after correct edits — the orchestrator diffed its assigned file set on disk and re-dispatched the remainder to a fresh agent; parallel agents were found to have edited files outside their assigned sets — briefs henceforth forbid out-of-set edits and the orchestrator checks `git diff --name-only` against each set.

**Codifications.** Owner rulings OD-188..OD-192 recorded 2026-11-18 (owner chose the recommended option each time; next free OD-193 — log: `specs/owner-decisions-log-2026-11-14.md`). Highlights: OD-188 the Windows rename retry count becomes config key `statusline.cache.rename_retry_limit` (Int, default 2, range 0..10; total attempts = 1 + limit) beside `statusline.cache.rename_retry_delay_ms`. OD-189 the dead-backend marker word reuses `statusline.pill.label_local` (OD-173); new Text keys `statusline.labels.vllm_down` (`vLLM down`), `statusline.labels.lmcache_down` (`LMCache down`), `statusline.subagent.name_fallback` (`?`). OD-190 extends OD-183: hylo writes LF line endings on every OS (UTF-8 + LF); the Windows oracle's LF normalization is named beside `PYTHONIOENCODING=utf-8`, not hidden in the shim. OD-191 the OD-187 >512 KB timing fixture stays exempt from the 25 ms p95 target but the gate fails if its p95 exceeds 100 ms (4x the target). OD-192 ASM-007 (Claude Code 2.1.326 subagentStatusLine payload) must be validated by an owner capture into git-ignored `captures/` before Phase 2 writes the S1.07 stories; the rest of Phase 2 is not blocked (recorded as a Drift Item in STATE.md). Four [process-gap] lessons codified L-PG-23..26 in `cycles/phase-1-spec-crystallization/lessons.md` and recorded as Drift Items in STATE.md: L-PG-23 diff each fix agent's file set on disk and re-dispatch the remainder; L-PG-24 parallel fix agents stay inside their assigned set (out-of-set hits listed, not edited); L-PG-25 validator/sync-check reports use repo-relative paths only (pass-6 residue); L-PG-26 verify the source's citations before ordering an exact copy (pass-7 call 10 copied the OD-159 rider citing BC-1.03.001 PC-3 instead of BC-1.02.004).

**Counts.** Contract count unchanged at 154 (S5 = 20); VP count unchanged at 41; crash register 47 → 48 paths (CP-T09 minted, CP-T08 retired; T family 8); VP↔BC `bcs:` directed edges re-machine-checked at 261 (SC-29 closure); closed exclusion set unchanged at 12 ids; D4-EX-3 classes unchanged at 7 with 5 canonical table tests.

**Sync check (post-burst).** `sync-check-adv-p7-2026-11-18.md`: verdict PASS-WITH-FINDINGS; all 114 pass-7 findings verified CLOSED on disk, 0 OPEN; three new findings SC-29 (VP-INDEX edge-count prose), SC-30 (VP-011 crash-path recount) and SC-31 (cosmetic wording in BC-1.07.008/ARCH-07) all closed in the same burst — SC-29/SC-30 closures are the VP-INDEX v1.17 and VP-011 1.7 history entries; SC-31 count wording rides the next edit of each file. 102 dirty spec files vs HEAD scanned; 244 spec .md files across 7 trees; interpreter `/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7).

**Next:** ADV pass 8 (fresh-context perimeters; OD-176 needs three consecutive cosmetic-only passes to converge — 0 so far); CR-04 dependent-artifact hash staleness (check-input-drift, pre-gate) remains open.
## Burst: ADV pass-8 recording + remediation — ruling OD-193 applied, VP↔BC edges 269, sync check 87 closed / 1 rejected / 0 open (2026-11-18)

**Recording.** ADV pass 8 run 2026-11-18 over the full P1 spec package as the same six fresh-context perimeters (A/A2/B/C/C2/D), final messages extracted verbatim (`adversarial-reviews/pass-8.md`, indexed in `adversarial-reviews/ADV-P8-INDEX.md`, 88 rows). Totals: 88 findings — 12 HIGH / 36 MEDIUM / 33 LOW / 7 COSMETIC; Δ −26 vs pass 7 (114 → 88), the second-largest total drop of the series, HIGH 14 → 12. Per-perimeter counts: A 13, A2 19, B 11, C 6, C2 15, D 24. Pass-level novelty MEDIUM. Row tags: 2 [owner-question], 3 [process-gap]. Verdict NOT_CONVERGED (per OD-176: three consecutive cosmetic-only passes required — 0 so far). Orchestrator spot-verified ADV-P8-A01, A02, A05, A2-01, A2-05, B01, C2-03 and C2-13 on disk and against CPython 3.11.7; all held.

**Remediation.** Fixes executed per `pass-8-remediation-plan.md` (8 fix agents + 2 residual sweeps) across domain-spec, prd.md, prd-supplements, behavioral contracts, architecture, verification properties and the assessment/cicd documents. Residual high-risk strands from earlier passes persisted into pass 8 in mutated form — ADV-P8-B01 is a HIGH regression introduced by the pass-7 B06 respelling fix (key renamed without re-checking meaning at each use site), and ADV-P8-D20 replaced a wrong recursion-boundary measurement (989 claimed through a harness loader; end to end none is reachable) — both codified below.

**Codifications.** Owner ruling OD-193 recorded 2026-11-18 (owner chose the recommended option; next free OD-194 — log: `specs/owner-decisions-log-2026-11-14.md`). Highlight: OD-158 stands unchanged — the P1 >=95% line-coverage gate covers S1 (`internal/statusline`, `internal/cost`) and S5 (`internal/pyfmt`) only; `internal/parity` (S6) coverage is reported, not gated; pass-7 call 12's addition of `internal/parity` to the gate is withdrawn (ADV-P8-A04). Five [process-gap] lessons codified L-PG-27..31 in `cycles/phase-1-spec-crystallization/lessons.md` and recorded as Drift Items in STATE.md: L-PG-27 a respelling fix must re-check what the renamed thing means at every use site (pass-7 B06 key rename → HIGH regression ADV-P8-B01); L-PG-28 depth/recursion facts are measured only through the real entry point (python3 -I -s legacy/dgx_statusline.py, isolated HOME), and the orchestrator re-runs any measurement that mints a new outcome (pass-8 D20); L-PG-29 sync-check briefs must require resolving every rider/anchor citation on disk, not just comparing copies (pass-7 OD-160 riders, caught by ADV-P8-A2-05); L-PG-30 orchestrator calls touching gates or scope are checked against the OD log before issue (pass-7 call 12 vs OD-158, resolved by OD-193; repeat of L-PG-13); L-PG-31 the validate-cross-site-correspondence hook mis-parses flow-style `modified:` lists whose entries contain ", " — agents converted 48 files to block style; recorded as tooling drift for the plugin owner.

**Counts.** Contract count unchanged at 154 (S5 = 20); VP count unchanged at 41; VP↔BC `bcs:` directed edges re-machine-checked at 269; crash register unchanged at 48 paths; closed exclusion set unchanged at 12 ids; D4-EX-3 classes unchanged at 7 with 5 canonical table tests.

**Sync check (post-burst).** `sync-check-adv-p8-2026-11-18.md`: 87 pass-7→pass-8 register findings verified CLOSED on disk, 1 REJECTED (C02 — measured unreachable end to end), 0 OPEN; SC-32 (cosmetic) disposed as no-change — the disputed history entry is accurate provenance and VP-012's 1.19 entry records the correction. 112 dirty spec files vs `HEAD` (+1392/−681) scanned; 244 spec `.md` files across 7 trees; interpreter `/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7).

**Dim-2 Attestation:** artifact counts verified on disk this burst: 154 BC files under `specs/behavioral-contracts/ss-01..ss-06`; 41 VP files (+ VP-INDEX) under `specs/verification-properties/`.

**Next:** ADV pass 9 (fresh-context perimeters; OD-176 needs three consecutive cosmetic-only passes to converge — 0 so far); CR-04 dependent-artifact hash staleness (check-input-drift, pre-gate) remains open.
