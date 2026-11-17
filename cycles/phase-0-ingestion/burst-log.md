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

**Parent-commit:** 47e4c3732ffbef8dded4225f0ce75a2a4867dadc

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

**Parent-commit:** 9692c07 (grounding burst 1)

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

## Burst: convergence-deepening COMPLETE — passes 0/1/4/5 converged; canonical Phase 1 input catalogues locked (2026-11-14)

**Parent-commit:** dff1f56 (convergence-deepening passes 2-3)

**Adversary verdict:** convergence-deepening COMPLETE — all six broad-sweep passes converged. Round dispositions verified against the convergence declarations on disk.

- Pass 0 (deep inventory): 3 rounds — SUBSTANTIVE r1-r2, NITPICK r3. **CONVERGED.** Canonical artifact: r3 §2 (`semport/hylo-legacy/hylo-legacy-pass-0-deep-inventory-r3.md`).
- Pass 1 (deep architecture): 3 rounds — SUBSTANTIVE r1-r2, NITPICK r3. **CONVERGED.** Canonical artifact: r3 §B with two Mermaid diagrams (`semport/hylo-legacy/hylo-legacy-pass-1-deep-architecture-r3.md`).
- Pass 4 (deep NFR/thresholds): 7 rounds — SUBSTANTIVE r1-r6, NITPICK r7. **CONVERGED.** The orchestrator overrode r4's self-declared NITPICK: r4 contained retractions and relied on a retracted HTTP/2 fact. Canonical artifact: r7 final catalogue — 147 thresholds; 120 rationales resolved; OD-57 (18 bulk-confirm + 27 owner-rationale in 7 groups); OD-94 fact sheet (`semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md`).
- Pass 5 (deep conventions/env/determinism/pitfalls): 5 rounds — SUBSTANTIVE r1-r4, NITPICK r5. **CONVERGED.** Canonical artifact: r3 consolidated, amended by r4-r5 — 43 explicit + 21 implicit env inputs; 54 determinism rows + 6 Go-side pins; 19 conventions; 22 pitfalls (`semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md`).

Passes 2 (9 rounds) and 3 (8 rounds) converged in the prior burst; see the entry above.

**Counts:** 232 BCs unchanged (137 byte-exact + 44 JSON-equivalent + 10 out of scope + 6 approved deviation + 35 pending owner decision). OD register extended to OD-01..OD-94: 64 issued (62 pending, 2 ruled — OD-24/OD-27); unused or reserved: OD-44, OD-49, OD-62-65, OD-67-73, OD-77-93; next free OD-95. Retraction ledger: CONV-ABS through 94; next free CONV-ABS 95; IDs 101-104 unused.

**Evidence captured:** proxy venv `pyvenv.cfg` include-system-site-packages=false — the proxy and preflight are not affected by the user site, and the parity harness runs shimmed Python cases under -s; mitmproxy 12.3.1 running with no config.yaml; Go 1.26.5 h2 facts recorded for OD-94.

**Codifications:** canonical Phase 1 input sources locked in STATE.md as a pointer table (inventory pass-0 r3 §2; architecture pass-1 r3 §B; domain pass-2 r8 §7 am. r9; BC index pass-3 r4 am. r5-r8, 232 BCs; thresholds/NFR pass-4 r7; conventions pass-5 r3 am. r4-r5). OD register extended to OD-01..OD-94 with the issued/unused-reserved partition. Retraction ledger bounds advanced (CONV-ABS through 94; next free 95; 101-104 unused). Evidence facts recorded (proxy venv isolation, mitmproxy 12.3.1 without config.yaml, Go 1.26.5 h2 facts for OD-94). No policies.yaml change this burst.

**Files touched (Dim-1): 25 unique files** — 18 semport deep-pass files (enumerated set, matches git-status untracked set), plus STATE.md, sidecar-learning.md, 2 log files, and 3 cycle files

- .factory/semport/hylo-legacy/hylo-legacy-pass-0-deep-inventory.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-0-deep-inventory-r2.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-0-deep-inventory-r3.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-1-deep-architecture.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-1-deep-architecture-r2.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-1-deep-architecture-r3.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r2.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r3.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r4.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r5.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r6.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r2.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r4.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r5.md
- .factory/STATE.md
- .factory/sidecar-learning.md
- .factory/logs/dispatcher-internal-2026-11-14.jsonl
- .factory/logs/events-2026-11-14.jsonl
- .factory/cycles/phase-0-ingestion/burst-log.md
- .factory/cycles/phase-0-ingestion/convergence-trajectory.md
- .factory/cycles/phase-0-ingestion/session-checkpoints.md

**Evictions:** Current Phase Steps row 2 (research: 4 reports + RESEARCH-INDEX verification) evicted from the last-5 window — already durably recorded in the grounding entry above and cycle-manifest.md. The passes-2-3 session checkpoint was archived to session-checkpoints.md.

**Dim-2 Attestation:** round counts and final-round NITPICK dispositions cross-checked against the convergence declarations in the final-round files on disk (pass-0 r3: "r1 SUBSTANTIVE, r2 SUBSTANTIVE, r3 NITPICK"; pass-1 r3: same split; pass-4 r7 and pass-5 r5: "findings are nitpicks, not gaps"). OD issued/unused partition verified arithmetically: 64 issued + 30 unused/reserved = 94; next free OD-95.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown analysis/state files and JSONL log churn only).

**Dim-6 Attestation:** N/A — no schema-structured file edited; policies.yaml untouched this burst.

**Dim-7 Attestation:** no repo test suite in scope; convergence verdicts are documented in the respective pass/deep-round files and summarized in convergence-trajectory.md.

**Closes:** convergence-deepening for ALL six passes. Still open: coverage-audit, extraction-validation (final), final-synthesis, input-hash drift check, Phase 0 owner approval gate (present the OD-01..OD-94 decision list).

---

## Burst: final Phase 0 analysis — coverage audit PASS, extraction validation r2 PASS-WITH-FIXES, pass-8 definitive synthesis, owner decision list gate-ready (2026-11-14)

**Parent-commit:** be38c50 (convergence-deepening complete)

**Adversary verdict:** no adversary pass dispatched this burst (deepening rounds already closed on NITPICK). Analysis-verdicts recorded instead: coverage audit (step B.5) **PASS** — `semport/hylo-legacy/hylo-legacy-coverage-audit.md`. Extraction validation r2 (step B.6) **PASS-WITH-FIXES** — `semport/hylo-legacy/hylo-legacy-extraction-validation-r2.md`: 78/232 BCs sampled, 100% confirmed; 26/27 metric groups exact; 1 fix (applied in-burst). Deep synthesis (step C) **DONE** — `semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md` is the definitive synthesis, superseding pass-6; primary reference for create-brief / create-domain-spec / create-prd / semport-analyze. Owner decision list **GATE-READY** — `semport/hylo-legacy/hylo-legacy-owner-decisions.md`.

**Owner decision list:** 64 issued ODs in groups A-F — A 12 (incl. 2 ruled: OD-24, OD-27), B 19, C 13, D 10, E 2, F 8. Recommendations: 23 KEEP (parity), 30 DEVIATE (approved deviations, incl. the 2 rulings), 11 NEW. Answer format in the file header (OD-06 a, or A: all recommended). **Owner flag: OD-14** now recommends (a) do not port --subagent — reversing the earlier Phase-0 toggle recommendation (PLAN §3 lists custom agent-panel rows as a non-goal; Claude Code 2.1.323 removed subagentStatusLine); confirmation requested at the gate.

**Codifications:** pass-0 deep inventory corrected in place (spawn census 10 → 9, with a B.6 note). Lessons recorded in pass-8 §10: 53 total — 13 P0 (L0-01..L0-13), 13 P1, 9 P2, 18 P3. STATE.md canonical-pointer table extended with the synthesis and the owner-decision list as gate inputs. OD register summary advanced to the group form (A 12 / B 19 / C 13 / D 10 / E 2 / F 8 = 64; 23 KEEP / 30 DEVIATE / 11 NEW); no policies.yaml change this burst.

**Files touched (Dim-1): 11 unique files**

- .factory/semport/hylo-legacy/hylo-legacy-coverage-audit.md
- .factory/semport/hylo-legacy/hylo-legacy-extraction-validation-r2.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md
- .factory/semport/hylo-legacy/hylo-legacy-owner-decisions.md
- .factory/semport/hylo-legacy/hylo-legacy-pass-0-deep-inventory-r3.md
- .factory/STATE.md
- .factory/sidecar-learning.md
- .factory/logs/dispatcher-internal-2026-11-14.jsonl
- .factory/logs/events-2026-11-14.jsonl
- .factory/cycles/phase-0-ingestion/burst-log.md
- .factory/cycles/phase-0-ingestion/session-checkpoints.md

**Evictions:** Current Phase Steps row 3 (semport broad sweep passes 0-6 over legacy/) evicted from the last-5 window — durably recorded in the grounding and convergence entries above and in cycle-manifest.md. The convergence-deepening session checkpoint was archived to session-checkpoints.md.

**Dim-2 Attestation:** verdict strings verified against the reports on disk (coverage-audit header; extraction-validation-r2 header; pass-8 confidence blockquote: coverage audit passed with 0 gaps, extraction validation r2 PASS-WITH-FIXES with 78/78 sampled BCs confirmed). OD group counts verified against the owner-decisions summary table: 12+19+13+10+2+8 = 64; KEEP 23 + DEVIATE 30 + NEW 11 = 64; ruled 2 (OD-24, OD-27); next free OD-95. Lesson counts verified in pass-8 §10: L0 13 + L1 13 + L2 9 + L3 18 = 53.

**Dim-5 Attestation:** N/A — no compiled artifacts in this burst (markdown analysis/state files and JSONL log churn only).

**Dim-6 Attestation:** N/A — no schema-structured file edited; policies.yaml untouched this burst.

**Dim-7 Attestation:** no repo test suite in scope; the extraction validator's behavioral verification and the coverage-audit cross-checks are documented in their reports and summarized in the pass-8 confidence block.

**Closes:** Phase 0 analysis — coverage-audit, extraction-validation (final), final-synthesis. Still open: input-hash drift check, fresh-context consistency audit, Phase 0 owner approval gate (present hylo-legacy-owner-decisions.md).

---

<!-- Repeat for each burst. Maintain chronological order. -->

## Extracted from STATE.md on 2026-11-17

### Owner Decisions — rulings recorded 2026-11-14 (as recorded at the 2026-11-17 session-wrap pause)

- **D16 committed on main (3e05cfe):** web UI (React + TypeScript + Vite, go:embed, Node build-time only) plus terminal UI on one local event API; design system in Storybook; guardrails. **D15 committed (a7b5e04).** Policy 12 now reads D1-D16.
- **O1:** CI pins Python 3.11 for the statusline and Stop hook (confirmed 3.11.7 by the env probe); 3.12 for the proxy (venv 3.12.10).
- **O2:** degraded output reproduced byte-for-byte for catalogued crash paths.
- **O3 = D4-EX-1:** Go may show ⌂ on Windows.
- **O5:** the nightly differential fuzz job runs but does not gate P1.
- **Q-a:** harness stdio STRICT, confirmed by the env probe (LANG=en_US.UTF-8, no LC_ALL/PYTHONUTF8, utf8_mode 0, strict stdin/stdout, COLUMNS supplied by Claude Code).
- **Q-b:** foreign-cache crash paths CP-C01..C10 are out of parity scope; the Go writer must produce legacy's exact cache format.
- **Q-c = D4-EX-2:** fix the sticky transcript crash. Skip wrong-shape JSON lines as legacy skips invalid JSON (dgx_statusline.py:1060-1063); excluded from the parity diff; covered by Go table tests (BC-SL-098/099).
- **LAN exposure** of the live legacy proxies/exporter: accepted by the owner until cutover (ruled via OD-24/OD-27). hylo proxy, UI and exporter bind to loopback by default (HY-BIND).
- **OD-01..OD-94 decision list gate-ready** — `semport/hylo-legacy/hylo-legacy-owner-decisions.md`. Groups A-F: A 12 (incl. 2 ruled: OD-24/OD-27), B 19, C 13, D 10, E 2, F 8 = 64 issued; unused or reserved (30): OD-44, OD-49, OD-62-65, OD-67-73, OD-77-93; next free OD-95. Recommendations: 23 KEEP / 30 DEVIATE / 11 NEW. **Owner flag: OD-14** now recommends (a) do not port --subagent, reversing the earlier Phase-0 toggle recommendation (PLAN §3 non-goal; CC 2.1.323 removed subagentStatusLine) — confirm at the gate. D13/D14 remain recorded in the Decisions Log below.
- **DECIDED 2026-11-14 (gate rulings; full log in `specs/owner-decisions-log-2026-11-14.md`):**
  - No DGX_* aliases / no backwards compatibility (OD-05)
  - No shadow week, full cutover (OD-52 moot)
  - --subagent not ported (OD-14)
  - Credential hygiene OD-06/07
  - Upstream TLS OD-41
  - HTTP/1.1 only OD-94
  - Proxy lifecycle OD-66/50/38
  - Config paths OD-95
  - Public doc edits drafted in the main working tree (PLAN, STATUSLINE-WIDGETS, RESUME) → committed on main as c023bc6 (ruling below).
- **Public doc edits committed on main as c023bc6** (PLAN D13/D15/P3/P5/P6/§6/§9, STATUSLINE-WIDGETS health dot, RESUME). Public main is 5 commits ahead of GitHub (f562477, b99082e, a7b5e04, 3e05cfe, c023bc6), not pushed.
- **DECIDED 2026-11-15 (market-intel human gate; rows in `specs/owner-decisions-log-2026-11-14.md`):** rulings OD-96..OD-100, summarized in the market_intel frontmatter block above.

### Phase Progress row detail — "Fix bursts (Phase 0)"

**NONE** — no fix burst required yet; extraction-validation fixes were applied in-burst during the sweep.

### Research (2026-11-14)

Four reports in `specs/research/`, indexed in `specs/research/RESEARCH-INDEX.md` (verified: exactly one row per report):

- `domain-hybrid-routing-claude-code-2026-11-14.md` (domain landscape, config surfaces, Messages API facts, policy risks, OpenAI translation); `general-go-port-parity-crossplatform-2026-11-14.md` (Python->Go byte-parity pitfalls, parity harness, cross-platform, deps, hardening, CI/release).
- `general-go-tls-intercepting-proxy-2026-11-14.md` (stdlib vs goproxy/martian/go-mitmproxy, selective interception + Remote Control, ALPN/SSE/WebSocket, CA semantics, mitmproxy parity behaviors, testing); `peer-tool-lessons-2026-11-14.md` (peer lessons L1-L7; owner decisions OD-1 = D13, OD-2 = D14).
- `domain-statusline-landscape-2026-11-15.md` (2026-11-15, domain): status line peer landscape + freshness delta since 11-14 + P1 risk signals — the market-intel input; row in `specs/research/RESEARCH-INDEX.md`.
