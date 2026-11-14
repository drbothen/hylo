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

## Burst: convergence-deepening — passes 2-3 CONVERGED, 232-BC index, OD-01..OD-45, owner rulings, captures (2026-11-14)

**Parent-commit:** 535b6ae (grounding burst 1)

**Adversary verdict:** deepening rounds for broad-sweep passes 2 and 3 reached convergence.

- Pass 2 (deep domain): 9 rounds — SUBSTANTIVE r1-r8, NITPICK r9. **CONVERGED.** Canonical artifact: r8 §7 combined pointer table, amended by r9 (`semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r8.md`).
- Pass 3 (deep behavioral contracts): 8 rounds — SUBSTANTIVE r1-r7, NITPICK r8. **CONVERGED.** The orchestrator overrode r7's self-declared NITPICK: round r7 surfaced new crash path H-09 and retraction CONV-ABS-22, forcing one more round. Canonical artifact: r4 canonical BC index, amended by r5-r8 (`semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md`).

**Counts:** 232 BCs = 137 byte-exact + 44 JSON-equivalent + 10 out of scope + 6 approved deviation + 35 pending owner decision. Statement partition of 1,809 Python statements: 903 re-read + 422 covered by pinned tables + 133 out of scope + 351 read in r8; 0 uncovered. Retractions: RET crosswalk (pass-3 r4) + CONV-ABS 12-28 (next free 29). Owner decisions OD-01..OD-45 (OD-44 unused): 42 pending, 2 ruled (OD-24/OD-27 — legacy LAN exposure accepted until cutover); next free OD-46.

**Owner rulings recorded:** D16 on main (3e05cfe — web UI React + TypeScript + Vite, go:embed, Node build-time only; terminal UI on one local event API; design system in Storybook; guardrails) and D15 (a7b5e04); policy 12 range amended D1-D15 -> D1-D16 (policies.yaml v1.3). O1 Python pins (3.11 statusline/Stop hook per env probe, 3.12 proxy venv); O2 degraded-output byte-exact reproduction for catalogued crash paths; O3 = D4-EX-1 (fallback glyph on Windows); O5 nightly differential fuzz non-gating for P1; Q-a harness stdio STRICT (env probe: LANG=en_US.UTF-8, no LC_ALL/PYTHONUTF8, utf8_mode 0, strict stdin/stdout, COLUMNS supplied by Claude Code); Q-b foreign-cache crash paths CP-C01..C10 out of parity scope (Go writer must produce legacy's exact cache format); Q-c = D4-EX-2 sticky-transcript fix (skip wrong-shape JSON lines as legacy skips invalid JSON, dgx_statusline.py:1060-1063; excluded from parity diff; Go table tests BC-SL-098/099); LAN exposure accepted (hylo proxy/UI/exporter default to loopback, HY-BIND).

**Captures:** env probe (as above, recorded 2026-11-14); VictoriaMetrics post-soak capture — 19 series, all finite; idle windows produce ABSENT rather than NaN (CP-N01/N02 latent). DGX 24 h soak complete.

**Codifications:** policy 12 (settled_decisions_are_constraints) range amended D1-D15 -> D1-D16 in policies.yaml (v1.3, CHANGELOG row added). Owner rulings O1/O2/O3/O5 and Q-a/Q-b/Q-c and the LAN-exposure acceptance (OD-24/OD-27) recorded in STATE.md Owner Decisions; OD-01..OD-45 list registered with next-free OD-46.

**Files touched (Dim-1): 26 unique files**

- .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r2.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r3.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r4.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r5.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r6.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r7.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r8.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r9.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r3.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r5.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r6.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r7.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md
- .factory/STATE.md
- .factory/policies.yaml
- .factory/sidecar-learning.md
- .factory/logs/dispatcher-internal-2026-11-13.jsonl
- .factory/logs/dispatcher-internal-2026-11-14.jsonl
- .factory/logs/events-2026-11-14.jsonl
- .factory/cycles/phase-0-ingestion/burst-log.md
- .factory/cycles/phase-0-ingestion/convergence-trajectory.md
- .factory/cycles/phase-0-ingestion/session-checkpoints.md

**Evictions:** grounding-burst Current Phase Steps row 1 (pre-0 initialization) evicted from the last-5 window — already durably recorded in the grounding entry above and cycle-manifest.md. Prior session checkpoint archived to session-checkpoints.md.

**Dim-2 Attestation:** counts cross-checked against the canonical artifacts: BC index totals stated in pass-3 r4/r8 (232 = 137+44+10+6+35) and statement partition 1,809 = 903+422+133+351 stated in pass-2 r8 — both sums verified arithmetically at recording time.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown analysis/state files and YAML policy registry only).

**Dim-6 Attestation:** policies.yaml edited strictly within the existing entry schema; only policy 12's description and first verification_step strings and the version/CHANGELOG metadata changed.

**Dim-7 Attestation:** no repo test suite in scope; deepening verdicts are documented in the respective pass/deep-round files and summarized in convergence-trajectory.md.

**Closes:** convergence-deepening for passes 2 and 3. Still open: deepen passes 0, 1, 4, 5 (at least 2 rounds each), coverage-audit, final-synthesis, input-hash drift check, Phase 0 owner approval gate (OD-01..OD-45 presentation).

---

<!-- Repeat for each burst. Maintain chronological order. -->
