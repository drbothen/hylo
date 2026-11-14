---
document_type: burst-log
level: ops
version: "1.0"
status: in-progress
producer: state-manager
timestamp: 2026-11-14T05:34:00Z
cycle: "phase-0-ingestion"
inputs: [STATE.md]
input-hash: "[live-state]"
traces_to: STATE.md
---

# Burst Log — phase-0-ingestion

## Burst: Grounding burst 1 — research, legacy broad sweep + validation, D13-D15, policy 20 (2026-11-14)

**Parent-commit:** 5007a346d58d5cf1309e2f3cc634f40e820e0e49

**Adversary verdict:** N/A — grounding burst, no adversary pass dispatched. Extraction validation verdict recorded instead: PASS-WITH-FIXES (exhaustive; 0 hallucinations). Adversary passes begin at convergence-deepening.

**Files touched (Dim-1): 20 unique files**

- .factory/specs/research/RESEARCH-INDEX.md
- .factory/specs/research/domain-hybrid-routing-claude-code-2026-11-14.md
- .factory/specs/research/general-go-port-parity-crossplatform-2026-11-14.md
- .factory/specs/research/general-go-tls-intercepting-proxy-2026-11-14.md
- .factory/specs/research/peer-tool-lessons-2026-11-14.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-0-inventory.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-1-architecture.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-2-domain-model.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-4-nfr-catalog.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-5-conventions.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-6-synthesis.md
- .factory/semport/hylo-legacy/hylo-legacy-extraction-validation.md
- .factory/policies.yaml
- .factory/STATE.md
- .factory/cycles/phase-0-ingestion/cycle-manifest.md
- .factory/cycles/phase-0-ingestion/burst-log.md
- .factory/sidecar-learning.md
- .factory/logs/dispatcher-internal-2026-11-13.jsonl
- .factory/logs/events-2026-11-13.jsonl

**Codifications:** Policy 20 (config_over_code, D15 iron rule) added to policies.yaml; policy 12 (settled_decisions_are_constraints) range amended D1-D12 -> D1-D15. Owner decisions D13 (intercept all Claude Code traffic) and D14 (no proxy env leak to child processes) recorded as settled (docs/PLAN.md on main, b99082e); D15 adopted (public commit pending owner approval).

**Dim-2 Attestation:** Literal shell gate executed. `grep -c '^| 2026-11-14 |' RESEARCH-INDEX.md` -> 4 index rows, matching the 4 report files on disk exactly (one row per report; no duplicates, none missing).

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown research reports, YAML policy registry, markdown state files only).

**Dim-6 Attestation:** policies.yaml edited strictly within the existing entry schema (id/name/description/adopted/severity/enforced_by/scope/lint_hook/verification_steps); policy 20 copied the structure of policies 12-19 and metadata/changelog were updated per the file's own convention.

**Dim-7 Attestation:** No repo test suite in scope for this burst. validate-extraction suite over the semport sweep reported PASS-WITH-FIXES (exhaustive; 0 hallucinations) — recorded in semport/hylo-legacy/hylo-legacy-extraction-validation.md.

**Closes:** none — Phase 0 grounding burst; formal finding closure begins at convergence-deepening. Open owner questions consolidated in STATE.md (status line/parity, proxy, legacy quirks, policy risk).

---

<!-- Repeat for each burst. Maintain chronological order. -->
